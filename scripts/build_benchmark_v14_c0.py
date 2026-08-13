#!/usr/bin/env python3
"""Assemble and validate Method v1.4 C0A/C0T without fetching entropy."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

import build_benchmark_v14_source_snapshot as source_snapshot


ROOT = Path(__file__).parents[1].resolve()
SCHEMA = ROOT / "schemas/benchmark-v1.4-c0.schema.json"
SCHEMA_VERSION = "c5k4-method-v1.4-c0-1.0"
CONFIG_VERSION = "c5k4-method-v1.4-c0-inputs-1.0"
LEGACY_CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
LEGACY_GENESIS = 1595431050
LEGACY_PERIOD_SECONDS = 30


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


P0 = _load_module("benchmark_v14_p0_for_c0", ROOT / "scripts/build_benchmark_v14_p0.py")
SELECTOR = _load_module("benchmark_v14_selector_for_c0", ROOT / "scripts/select_benchmark_v14.py")
SOURCE = _load_module("benchmark_v14_source_for_c0", ROOT / "scripts/build_benchmark_v14_source_snapshot.py")


class C0Error(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_time(value: Any, where: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise C0Error(f"{where} must be a whole-second RFC3339 UTC timestamp")
    try:
        result = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise C0Error(f"{where} is invalid") from exc
    if result.microsecond:
        raise C0Error(f"{where} must use whole seconds")
    return result


def close_time(round_number: int) -> str:
    if type(round_number) is not int or round_number < 1:
        raise C0Error("legacy drand round must be a positive integer")
    timestamp = LEGACY_GENESIS + (round_number - 1) * LEGACY_PERIOD_SECONDS
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_path(recorded: str) -> Path:
    pure = PurePosixPath(recorded)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise C0Error(f"path must be normalized and repository-relative: {recorded!r}")
    resolved = (ROOT / Path(*pure.parts)).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise C0Error(f"path escapes repository: {recorded!r}") from exc
    return resolved


def reference(value: Any, where: str) -> tuple[dict[str, str], bytes]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise C0Error(f"{where} must contain exactly path and sha256")
    if not isinstance(value["path"], str) or not isinstance(value["sha256"], str):
        raise C0Error(f"{where} fields must be strings")
    path = repo_path(value["path"])
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise C0Error(f"cannot read {where}: {exc}") from exc
    actual = sha256(raw)
    if value["sha256"] != actual:
        raise C0Error(f"{where} SHA-256 mismatch")
    return {"path": value["path"], "sha256": actual}, raw


def object_digest(value: dict[str, Any], key: str) -> str:
    return sha256(canonical_json({name: item for name, item in value.items() if name != key}))


def schema_validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value), key=lambda e: list(e.absolute_path))
    if errors:
        raise C0Error("C0 schema validation failed: " + "; ".join(
            f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in errors
        ))


def git(*args: str) -> bytes:
    source_snapshot.assert_offline_git_repository(ROOT)
    return source_snapshot.git(ROOT, *args)


def commit_file(commit: str, path: str) -> bytes:
    try:
        resolved = git("rev-parse", commit).decode().strip()
    except subprocess.CalledProcessError as exc:
        raise C0Error(f"commit is not present locally: {commit}") from exc
    if resolved != commit:
        raise C0Error("commit must be an exact object ID")
    try:
        return git("show", f"{commit}:{path}")
    except subprocess.CalledProcessError as exc:
        raise C0Error(f"path {path!r} is absent from commit {commit}") from exc


def validate_sources_snapshot(snapshot: dict[str, Any], p0t: dict[str, Any]) -> None:
    if snapshot.get("schema_version") != SOURCE.SNAPSHOT_SCHEMA or snapshot.get("snapshot_id") != "S0":
        raise C0Error("S0 has the wrong schema or snapshot identity")
    if snapshot.get("complete") is not True or snapshot.get("candidate_semantics_inspected") is not False:
        raise C0Error("S0 is incomplete or records candidate-semantic inspection")
    if snapshot.get("snapshot_sha256") != object_digest(snapshot, "snapshot_sha256"):
        raise C0Error("S0 self-digest does not replay")
    p0t_commit = snapshot.get("p0_attestation_commit")
    if not isinstance(p0t_commit, str) or len(p0t_commit) != 40:
        raise C0Error("S0 does not record an exact P0T commit")
    expected = {
        "p0_artifact_commit": p0t["p0a_commit"],
        "p0_published_at_utc": p0t["p0a_published_at_utc"],
    }
    for key, value in expected.items():
        if value is None or snapshot.get(key) != value:
            raise C0Error(f"S0 {key} does not match P0T")


def validate_inputs(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bytes]]:
    if config.get("schema_version") != CONFIG_VERSION:
        raise C0Error("unsupported C0 input config")
    required = {"p0a", "p0t", "s0", "eligible_pool", "quota_feasibility", "selector_artifacts", "protocol_components", "future_drand_round"}
    if set(config) != required | {"schema_version"}:
        raise C0Error("C0 input config has missing or unknown fields")
    refs: dict[str, Any] = {}
    raws: dict[str, bytes] = {}
    for name in ("p0a", "p0t", "s0", "eligible_pool", "quota_feasibility"):
        refs[name], raws[name] = reference(config[name], name)
    selector_refs = config["selector_artifacts"]
    if not isinstance(selector_refs, dict) or set(selector_refs) != set(SELECTOR.ARTIFACT_KEYS):
        raise C0Error("selector_artifacts must contain exactly the six selector inputs")
    refs["selector_artifacts"] = {}
    for name in SELECTOR.ARTIFACT_KEYS:
        refs["selector_artifacts"][name], raws[name] = reference(selector_refs[name], f"selector_artifacts.{name}")
    protocol = config["protocol_components"]
    if not isinstance(protocol, dict) or set(protocol) != set(P0.REQUIRED_COMPONENTS):
        raise C0Error("protocol_components must contain every P0-frozen component")
    refs["protocol_components"] = {}
    for name in P0.REQUIRED_COMPONENTS:
        refs["protocol_components"][name], raws[f"protocol:{name}"] = reference(protocol[name], f"protocol_components.{name}")

    values = {}
    for name in ("p0a", "p0t", "s0", "eligible_pool", "quota_feasibility"):
        try:
            values[name] = json.loads(raws[name])
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise C0Error(f"{name} is not valid UTF-8 JSON: {exc}") from exc
    P0.validate_p0a(values["p0a"])
    if values["p0t"]["p0a"] != refs["p0a"]:
        raise C0Error("P0T does not authenticate supplied P0A")
    if set(values["p0a"]["components"]) != set(P0.REQUIRED_COMPONENTS):
        raise C0Error("P0A components are incomplete")
    for name in P0.REQUIRED_COMPONENTS:
        p0_ref = values["p0a"]["components"][name]
        if {"path": p0_ref["path"], "sha256": p0_ref["sha256"]} != refs["protocol_components"][name]:
            raise C0Error(f"protocol component {name} differs from P0A")
    validate_sources_snapshot(values["s0"], values["p0t"])
    # P0T intentionally cannot name its own object ID. S0 records the already
    # public attestation commit, allowing C0 to replay its exact ancestry and
    # committed bytes without introducing a circular field into P0T.
    P0.validate_p0t(
        values["p0t"],
        p0t_commit=values["s0"]["p0_attestation_commit"],
        artifact_path=repo_path(refs["p0t"]["path"]),
    )

    pool = values["eligible_pool"]
    clusters = SELECTOR.validate_pool(pool)
    feasibility = values["quota_feasibility"]
    try:
        SELECTOR.replay_feasibility(
            pool, raws["eligible_pool"], clusters, feasibility,
            {name: raws[name] for name in SELECTOR.ARTIFACT_KEYS},
        )
    except ValueError as exc:
        raise C0Error(f"passing feasibility replay failed: {exc}") from exc
    if feasibility["chronology"]["p0_artifact_commit"] != values["p0t"]["p0a_commit"]:
        raise C0Error("feasibility chronology does not match P0A")
    if feasibility["chronology"]["p0_attestation_commit"] != values["s0"]["p0_attestation_commit"]:
        raise C0Error("feasibility chronology does not match P0T")
    if feasibility["chronology"]["s0_acquired_at_utc"] != values["s0"]["acquired_at_utc"]:
        raise C0Error("feasibility chronology does not match S0")
    if parse_time(values["p0t"]["p0a_published_at_utc"], "P0 publication") >= parse_time(values["s0"]["acquired_at_utc"], "S0 acquisition"):
        raise C0Error("P0T publication must precede S0")
    if feasibility.get("entropy_used") is not False or feasibility.get("selected_clusters") != []:
        raise C0Error("feasibility artifact consumed entropy or selected clusters")
    refs["future_drand_round"] = config["future_drand_round"]
    return {"refs": refs, "values": values, "raws": raws}, refs


def assemble_c0a(config_path: Path) -> dict[str, Any]:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise C0Error(str(exc)) from exc
    state, _ = validate_inputs(config)
    refs, values = state["refs"], state["values"]
    feasibility = values["quota_feasibility"]
    round_number = config["future_drand_round"]
    c0a = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "C0A",
        "protocol_version": "1.4",
        "phase": "C0_ARTIFACT",
        "p0a": refs["p0a"], "p0t": refs["p0t"], "s0": refs["s0"],
        "bindings": {
            "eligible_pool": refs["eligible_pool"],
            "quota_feasibility": refs["quota_feasibility"],
            "selector_artifacts": refs["selector_artifacts"],
            "protocol_components": refs["protocol_components"],
            "selection_algorithm": {
                "name": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES",
                "schema_version": SELECTOR.SCHEMA_VERSION,
                "domain_hex": SELECTOR.DOMAIN.hex(),
                "selector_sha256": refs["protocol_components"]["selector"]["sha256"],
            },
        },
        "upstream": values["eligible_pool"]["upstream"],
        "pool_file_sha256": refs["eligible_pool"]["sha256"],
        "quota_feasibility_sha256": feasibility["certificate_sha256"],
        "randomness": {
            "source": "League of Entropy drand", "chain_hash": LEGACY_CHAIN_HASH,
            "round": round_number, "round_closes_at_utc": close_time(round_number),
            "value": None,
        },
        "chronology": {
            "p0_artifact_commit": feasibility["chronology"]["p0_artifact_commit"],
            "p0_attestation_commit": feasibility["chronology"]["p0_attestation_commit"],
            "p0_published_at_utc": feasibility["chronology"]["p0_published_at_utc"],
            "s0_acquired_at_utc": feasibility["chronology"]["s0_acquired_at_utc"],
            "feasibility_checked_at_utc": feasibility["chronology"]["feasibility_checked_at_utc"],
            "c0_artifact_commit": None, "c0_attestation_commit": None,
            "c0_published_at_utc": None,
        },
        "published_at_utc": None,
        "entropy_used": False, "selected_clusters": [], "target_ranking": [],
    }
    validate_c0a(c0a)
    return c0a


def validate_c0a(value: dict[str, Any], *, authenticate_bindings: bool = True) -> None:
    schema_validate(value)
    if value.get("artifact_kind") != "C0A":
        raise C0Error("expected C0A")
    if value["randomness"]["round_closes_at_utc"] != close_time(value["randomness"]["round"]):
        raise C0Error("drand close does not derive from legacy genesis/period/round")
    if value["randomness"]["value"] is not None or value["entropy_used"] is not False or value["selected_clusters"] or value["target_ranking"]:
        raise C0Error("C0A contains forbidden entropy, value, selection, or ranking")
    if not authenticate_bindings:
        return
    reconstructed = {
        "schema_version": CONFIG_VERSION,
        "p0a": value["p0a"], "p0t": value["p0t"], "s0": value["s0"],
        "eligible_pool": value["bindings"]["eligible_pool"],
        "quota_feasibility": value["bindings"]["quota_feasibility"],
        "selector_artifacts": value["bindings"]["selector_artifacts"],
        "protocol_components": value["bindings"]["protocol_components"],
        "future_drand_round": value["randomness"]["round"],
    }
    state, _ = validate_inputs(reconstructed)
    values = state["values"]
    feasibility = values["quota_feasibility"]
    expected_chronology = {
        "p0_artifact_commit": feasibility["chronology"]["p0_artifact_commit"],
        "p0_attestation_commit": feasibility["chronology"]["p0_attestation_commit"],
        "p0_published_at_utc": feasibility["chronology"]["p0_published_at_utc"],
        "s0_acquired_at_utc": feasibility["chronology"]["s0_acquired_at_utc"],
        "feasibility_checked_at_utc": feasibility["chronology"]["feasibility_checked_at_utc"],
        "c0_artifact_commit": None, "c0_attestation_commit": None,
        "c0_published_at_utc": None,
    }
    if value["chronology"] != expected_chronology:
        raise C0Error("C0A chronology differs from its authenticated inputs")
    if value["upstream"] != values["eligible_pool"]["upstream"]:
        raise C0Error("C0A upstream differs from authenticated pool")
    if value["pool_file_sha256"] != value["bindings"]["eligible_pool"]["sha256"]:
        raise C0Error("C0A pool digest differs from authenticated binding")
    if value["quota_feasibility_sha256"] != feasibility["certificate_sha256"]:
        raise C0Error("C0A feasibility digest differs from authenticated certificate")
    expected_algorithm = {
        "name": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES",
        "schema_version": SELECTOR.SCHEMA_VERSION,
        "domain_hex": SELECTOR.DOMAIN.hex(),
        "selector_sha256": value["bindings"]["protocol_components"]["selector"]["sha256"],
    }
    if value["bindings"]["selection_algorithm"] != expected_algorithm:
        raise C0Error("C0A selection algorithm binding differs from executable selector")


def assemble_c0t(c0a_path: Path, c0a_commit: str, observed_at: str, c0t_path: str) -> dict[str, Any]:
    c0a = json.loads(c0a_path.read_text(encoding="utf-8"))
    validate_c0a(c0a)
    relative = c0a_path.resolve().relative_to(ROOT).as_posix()
    raw = c0a_path.read_bytes()
    if commit_file(c0a_commit, relative) != raw:
        raise C0Error("committed C0A bytes differ from supplied artifact")
    parse_time(observed_at, "GitHub-observed C0A publication time")
    if parse_time(c0a["chronology"]["p0_published_at_utc"], "P0 publication") >= parse_time(c0a["chronology"]["s0_acquired_at_utc"], "S0 acquisition"):
        raise C0Error("P0T publication must precede S0")
    observed = parse_time(observed_at, "C0A publication")
    if parse_time(c0a["chronology"]["s0_acquired_at_utc"], "S0 acquisition") >= observed:
        raise C0Error("S0 must precede observed C0A publication")
    if observed >= parse_time(c0a["randomness"]["round_closes_at_utc"], "round close"):
        raise C0Error("observed C0A publication must precede the frozen round close")
    c0t = {
        "schema_version": SELECTOR.C0_SCHEMA_VERSION,
        "artifact_kind": "C0T", "protocol_version": "1.4", "phase": "C0_FROZEN",
        "c0a": {"path": relative, "sha256": sha256(raw)},
        "pool_file_sha256": c0a["pool_file_sha256"],
        "quota_feasibility_sha256": c0a["quota_feasibility_sha256"],
        "bindings_sha256": sha256(canonical_json(c0a["bindings"])),
        "randomness": c0a["randomness"],
        "chronology": {
            "p0_artifact_commit": c0a["chronology"]["p0_artifact_commit"],
            "p0_attestation_commit": c0a["chronology"]["p0_attestation_commit"],
            "p0_published_at_utc": c0a["chronology"]["p0_published_at_utc"],
            "s0_acquired_at_utc": c0a["chronology"]["s0_acquired_at_utc"],
            "c0_artifact_commit": c0a_commit, "c0_attestation_commit": None,
            "c0_published_at_utc": observed_at,
        },
        "published_at_utc": observed_at,
        "publication_observation": {
            "source": "GITHUB_COMMIT_API_OBSERVATION",
            "repository": "https://github.com/Kuberwastaken/c5-k4",
            "observed_commit": c0a_commit, "observed_at_utc": observed_at,
        },
        "entropy_used": False, "selected_clusters": [], "target_ranking": [],
        "attestation_policy": {
            "direct_parent_required": True, "nonmerge_required": True,
            "c0a_bytes_immutable": True, "allowed_c0t_changed_paths": [c0t_path],
        },
    }
    validate_c0t(c0t)
    return c0t


def validate_c0t(value: dict[str, Any], *, c0t_commit: str | None = None, artifact_path: Path | None = None) -> None:
    schema_validate(value)
    if value.get("artifact_kind") != "C0T":
        raise C0Error("expected C0T")
    c0a_raw = commit_file(value["chronology"]["c0_artifact_commit"], value["c0a"]["path"])
    if sha256(c0a_raw) != value["c0a"]["sha256"]:
        raise C0Error("C0T does not authenticate committed C0A bytes")
    c0a = json.loads(c0a_raw)
    validate_c0a(c0a)
    if value["pool_file_sha256"] != c0a["pool_file_sha256"] or value["quota_feasibility_sha256"] != c0a["quota_feasibility_sha256"] or value["bindings_sha256"] != sha256(canonical_json(c0a["bindings"])):
        raise C0Error("C0T scientific bindings differ from C0A")
    if value["randomness"] != c0a["randomness"] or value["randomness"]["value"] is not None:
        raise C0Error("C0T changed or unlocked the frozen randomness contract")
    p0 = parse_time(value["chronology"]["p0_published_at_utc"], "P0 publication")
    s0 = parse_time(value["chronology"]["s0_acquired_at_utc"], "S0 acquisition")
    c0 = parse_time(value["chronology"]["c0_published_at_utc"], "observed C0A publication")
    close = parse_time(value["randomness"]["round_closes_at_utc"], "round close")
    if not p0 < s0 < c0 < close:
        raise C0Error("chronology must satisfy P0T < S0 < observed C0A publication < round close")
    if value["publication_observation"]["observed_commit"] != value["chronology"]["c0_artifact_commit"] or value["publication_observation"]["observed_at_utc"] != value["chronology"]["c0_published_at_utc"]:
        raise C0Error("GitHub publication observation does not bind C0A")
    if value["entropy_used"] is not False or value["selected_clusters"] or value["target_ranking"]:
        raise C0Error("C0T contains entropy, selection, or ranking")
    if c0t_commit is None:
        return
    resolved = git("rev-parse", c0t_commit).decode().strip()
    if resolved != c0t_commit:
        raise C0Error("C0T commit must be exact")
    parents = git("show", "-s", "--format=%P", c0t_commit).decode().split()
    if parents != [value["chronology"]["c0_artifact_commit"]]:
        raise C0Error("C0T must be a direct, nonmerge child of C0A")
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", c0t_commit).decode().splitlines()
    if changed != value["attestation_policy"]["allowed_c0t_changed_paths"]:
        raise C0Error("C0T changed paths outside its one attestation path")
    if artifact_path is not None:
        relative = artifact_path.resolve().relative_to(ROOT).as_posix()
        if relative != changed[0] or commit_file(c0t_commit, relative) != artifact_path.read_bytes():
            raise C0Error("committed C0T bytes/path differ from validated artifact")


def validation_receipt(value: dict[str, Any], c0t_commit: str, artifact_path: Path) -> dict[str, Any]:
    """Content-address the live Git and publication checks for offline consumers."""
    validate_c0t(value, c0t_commit=c0t_commit, artifact_path=artifact_path)
    relative = artifact_path.resolve().relative_to(ROOT).as_posix()
    receipt = {
        "schema_version": "c5k4-c0-validation-receipt-1.4",
        "c0t": {"path": relative, "file_sha256": sha256(artifact_path.read_bytes())},
        "c0_artifact_commit": value["chronology"]["c0_artifact_commit"],
        "c0_attestation_commit": c0t_commit,
        "direct_nonmerge_parent_verified": True,
        "changed_paths": [relative],
        "committed_bytes_verified": True,
        "publication_observation": value["publication_observation"],
        "c0_published_at_utc": value["chronology"]["c0_published_at_utc"],
        "future_round_close_at_utc": value["randomness"]["round_closes_at_utc"],
        "receipt_sha256": "0" * 64,
    }
    receipt["receipt_sha256"] = sha256(canonical_json({k: v for k, v in receipt.items() if k != "receipt_sha256"}))
    return receipt


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("assemble-c0a")
    a.add_argument("--config", type=Path, required=True); a.add_argument("--output", type=Path, required=True)
    t = sub.add_parser("assemble-c0t")
    t.add_argument("--c0a", type=Path, required=True); t.add_argument("--c0a-commit", required=True)
    t.add_argument("--observed-at", required=True)
    t.add_argument("--output", type=Path, required=True)
    v = sub.add_parser("validate-c0t")
    v.add_argument("--artifact", type=Path, required=True); v.add_argument("--commit")
    v.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "assemble-c0a": value = assemble_c0a(args.config)
        elif args.command == "assemble-c0t": value = assemble_c0t(args.c0a, args.c0a_commit, args.observed_at, args.output.resolve().relative_to(ROOT).as_posix())
        else:
            value = json.loads(args.artifact.read_text()); validate_c0t(value, c0t_commit=args.commit, artifact_path=args.artifact if args.commit else None)
            if args.receipt:
                if not args.commit: raise C0Error("--receipt requires --commit")
                write_json(args.receipt, validation_receipt(value, args.commit, args.artifact))
            return 0
        write_json(args.output, value)
    except (C0Error, OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
