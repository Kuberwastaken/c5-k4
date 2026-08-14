#!/usr/bin/env python3
"""Compile Method v1.5 C0A and provide canonical C0 structure helpers.

C0A is deliberately non-authoritative.  It is assembled only after replaying
the complete pass-pool source gate and embeds that canonical object verbatim.
C0T public authority is intentionally delegated to the strict repository-only
adapter in ``verify_benchmark_v15_c0_publication.py``.  The compatibility
functions here are exercised by unit tests but the CLI cannot mint or accept a
C0T without that adapter's run-listing, public-ref, source-replay, and exact
commit gates.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from jsonschema import Draft7Validator, FormatChecker, RefResolver

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark_v15_pass_pool as pass_pool  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/benchmark-v1.5-c0.schema.json"
OBSERVATION_SCHEMA_PATH = ROOT / "schemas/benchmark-c0-publication-observation-v1.5.schema.json"
SCHEMA = "c5k4-method-v1.5-c0-1.0"
OBSERVATION_SCHEMA = "c5k4-method-v1.5-c0a-publication-observation-1.0"
REPOSITORY = "https://github.com/Kuberwastaken/c5-k4"
REPOSITORY_SLUG = "Kuberwastaken/c5-k4"
PUBLICATION_REF = "refs/heads/method-v1.5-c0"
PUBLICATION_BRANCH = "method-v1.5-c0"
LEGACY_CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
LEGACY_GENESIS = 1595431050
LEGACY_PERIOD_SECONDS = 30
OID_RE = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_KEYS = {
    "entropy", "randomness_value", "selected", "selected_clusters", "selection",
    "ranking", "target_ranking", "statement", "statement_text", "semantics",
    "target_semantics", "outcome", "outcomes", "proof_route", "residual",
}
ApiFetch = Callable[[str], bytes]
ActivationVerifier = Callable[[dict[str, Any]], dict[str, Any]]
P1R_PATH = "results/benchmark/v1.5-protocol/P1R.json"
C0A_PATH = "results/benchmark/v1.5-protocol/C0A.json"
C0T_PATH = "results/benchmark/v1.5-protocol/C0T.json"


class C0Error(ValueError):
    """The target-blind C0 publication contract is not satisfied."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def artifact_digest(value: dict[str, Any]) -> str:
    unsigned = copy.deepcopy(value)
    unsigned.pop("artifact_sha256", None)
    return sha256_bytes(canonical_json(unsigned))


def observation_digest(value: dict[str, Any]) -> str:
    unsigned = copy.deepcopy(value)
    unsigned.pop("receipt_sha256", None)
    return sha256_bytes(OBSERVATION_SCHEMA.encode("ascii") + b"\0" + canonical_json(unsigned))


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise C0Error(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise C0Error(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise C0Error(f"{label} must be one JSON object")
    return value


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return strict_json(path.read_bytes(), label)
    except OSError as exc:
        raise C0Error(f"cannot read {label}") from exc


def schema_validate(value: dict[str, Any]) -> None:
    schema = load_json(SCHEMA_PATH, "C0 schema")
    observation_schema = load_json(OBSERVATION_SCHEMA_PATH, "C0 observation schema")
    resolver = RefResolver.from_schema(schema, store={observation_schema["$id"]: observation_schema})
    errors = sorted(
        Draft7Validator(schema, resolver=resolver, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in errors
        )
        raise C0Error(f"C0 schema validation failed: {rendered}")


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise C0Error(f"{label} must be a whole-second RFC3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise C0Error(f"{label} is invalid") from exc
    if parsed.microsecond:
        raise C0Error(f"{label} must use whole seconds")
    return parsed


def close_time(round_number: int) -> str:
    if type(round_number) is not int or round_number < 1:
        raise C0Error("legacy drand round must be a positive integer")
    timestamp = LEGACY_GENESIS + (round_number - 1) * LEGACY_PERIOD_SECONDS
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_path(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise C0Error(f"{label} must be a repository-relative path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or pure.as_posix() != value:
        raise C0Error(f"{label} must be a normalized repository-relative path")
    return value


def repository_file(value: str, label: str) -> Path:
    normalized = normalize_path(value, label)
    resolved = (ROOT / normalized).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise C0Error(f"{label} escapes the repository through a symlink") from exc
    return resolved


def git(*args: str) -> bytes:
    env = {
        "PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
    }
    try:
        return subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never", *args],
            cwd=ROOT, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=env,
        ).stdout
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.decode(errors="replace").strip()
        raise C0Error(f"git {' '.join(args)} failed: {message}") from exc


def exact_commit(commit: str) -> None:
    if not isinstance(commit, str) or not OID_RE.fullmatch(commit):
        raise C0Error("commit must be an exact 40-lowercase-hex object ID")
    if git("rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
        raise C0Error("commit does not resolve to its exact object ID")


def commit_file(commit: str, path: str) -> bytes:
    exact_commit(commit)
    normalize_path(path, "committed path")
    return git("show", f"{commit}:{path}")


def changed_paths(commit: str) -> list[str]:
    rows = [
        row for row in git(
            "diff-tree", "--no-commit-id", "--name-status", "-r", "--root", commit,
        ).decode().splitlines() if row
    ]
    entries = [row.split("\t", 1) for row in rows]
    if any(len(entry) != 2 or entry[0] != "A" for entry in entries):
        raise C0Error("C0 publication commit contains a non-additive path change")
    return [entry[1] for entry in entries]


def parents(commit: str) -> list[str]:
    exact_commit(commit)
    return git("show", "-s", "--format=%P", commit).decode().split()


def _scan_forbidden(value: Any, *, inside_pool: bool = False, path: tuple[str, ...] = ()) -> None:
    # The canonical pass-pool has its own stricter schema and uses fixed false
    # boundary keys such as entropy_present.  It is checked separately.
    if inside_pool:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = key.lower()
            if lowered in FORBIDDEN_KEYS:
                raise C0Error(f"forbidden C0 field {'.'.join(path + (key,))}")
            _scan_forbidden(item, inside_pool=(path == () and key == "pass_pool"), path=path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden(item, inside_pool=False, path=path + (str(index),))


def _boundary() -> dict[str, bool]:
    return {
        "target_blind": True, "entropy_present": False, "selection_present": False,
        "ranking_present": False, "statement_text_present": False,
        "target_semantics_present": False, "outcomes_present": False,
    }


def _randomness(round_number: int) -> dict[str, Any]:
    return {
        "source": "League of Entropy drand", "chain_hash": LEGACY_CHAIN_HASH,
        "round": round_number, "round_closes_at_utc": close_time(round_number),
        "value": None, "entropy_used": False, "selection_performed": False,
    }


def validate_c0a(value: dict[str, Any]) -> None:
    schema_validate(value)
    if value.get("artifact_kind") != "C0A":
        raise C0Error("expected C0A")
    if value.get("artifact_sha256") != artifact_digest(value):
        raise C0Error("C0A self-digest is invalid")
    _scan_forbidden(value)
    embedded = value["pass_pool"]
    try:
        pass_pool.validate_pool(embedded)
    except pass_pool.PassPoolError as exc:
        raise C0Error(f"embedded pass pool is invalid: {exc}") from exc
    binding = value["pass_pool_binding"]
    canonical_digest = sha256_bytes(canonical_json(embedded))
    if (
        binding["canonical_object_sha256"] != canonical_digest
        or binding["pool_sha256"] != embedded["pool_sha256"]
        or value["publication_topology"]["terminal_u2_commit"]
        != embedded["public_chain"]["pass_publication_commit"]
    ):
        raise C0Error("C0A pass-pool binding does not replay")
    randomness = value["randomness_contract"]
    if randomness["round_closes_at_utc"] != close_time(randomness["round"]):
        raise C0Error("C0A drand close does not derive from the frozen chain")
    if value["publication_topology"]["c0a_path"] == value["publication_topology"]["c0t_path"]:
        raise C0Error("C0A and C0T must use distinct add-only paths")


def assemble_c0a(
    pass_pool_path: Path, *, source_paths: dict[str, Path], public_repository: Path,
    future_drand_round: int, c0a_path: str, c0t_path: str, workflow_path: str,
    activation_verifier: ActivationVerifier | None = None,
) -> dict[str, Any]:
    """Re-run the complete source gate and embed the exact canonical pool."""
    normalize_path(c0a_path, "C0A path")
    normalize_path(c0t_path, "C0T path")
    normalize_path(workflow_path, "workflow path")
    supplied = load_json(pass_pool_path, "pass pool")
    try:
        expected = pass_pool.build_pool(
            source_paths["private_registry"], source_paths["aggregate_certificate"],
            source_paths["replay_attestation"], source_paths["pass_receipt"],
            source_paths["prior_public_chain_proof"], source_paths["pass_public_chain_proof"],
            source_paths["p1a"], source_paths["p1t"], public_repository,
        )
    except (KeyError, pass_pool.PassPoolError) as exc:
        raise C0Error(f"pass-pool source reauthentication failed: {exc}") from exc
    raw = pass_pool_path.read_bytes()
    if raw != canonical_json(supplied) or canonical_json(expected) != raw:
        raise C0Error("supplied pass-pool bytes are not the reauthenticated canonical object")
    p1_activation = _require_p1_activation(expected, activation_verifier)
    workflow_raw = repository_file(workflow_path, "workflow path").read_bytes()
    pool_binding = {
        "input_file_sha256": sha256_bytes(raw),
        "canonical_object_sha256": sha256_bytes(canonical_json(expected)),
        "pool_sha256": expected["pool_sha256"],
        "embedded_exact_canonical_object": True,
        "source_reauthentication_performed": True,
    }
    c0a = {
        "schema": SCHEMA, "artifact_kind": "C0A", "protocol_version": "1.5",
        "status": "AWAITING_C0_PUBLICATION_ATTESTATION",
        "authority": "NO_LIVE_C0_AUTHORITY_CLAIMED",
        "p1_activation": p1_activation,
        "pass_pool": copy.deepcopy(expected), "pass_pool_binding": pool_binding,
        "randomness_contract": _randomness(future_drand_round),
        "publication_topology": {
            "repository": REPOSITORY, "ref": PUBLICATION_REF,
            "terminal_u2_commit": expected["public_chain"]["pass_publication_commit"],
            "c0a_path": c0a_path, "c0t_path": c0t_path,
            "c0a_change": "ADD_EXACTLY_ONE_C0A_PATH", "c0t_change": "ADD_EXACTLY_ONE_C0T_PATH",
            "merge_commits_permitted": False,
        },
        "workflow_binding": {"path": workflow_path, "sha256": sha256_bytes(workflow_raw)},
        "publication_boundary": _boundary(),
    }
    c0a["artifact_sha256"] = artifact_digest(c0a)
    validate_c0a(c0a)
    return c0a


def validate_c0a_commit(c0a: dict[str, Any], c0a_commit: str, artifact_path: Path) -> None:
    validate_c0a(c0a)
    path = artifact_path.resolve().relative_to(ROOT).as_posix()
    if path != c0a["publication_topology"]["c0a_path"]:
        raise C0Error("C0A file path differs from its frozen topology")
    terminal = c0a["publication_topology"]["terminal_u2_commit"]
    if parents(c0a_commit) != [terminal]:
        raise C0Error("C0A must be a direct nonmerge child of terminal first-pass U2")
    if changed_paths(c0a_commit) != [path]:
        raise C0Error("C0A commit must add exactly its one frozen path")
    if commit_file(c0a_commit, path) != artifact_path.read_bytes():
        raise C0Error("committed C0A bytes differ from the supplied artifact")


def authenticate_run(
    raw: bytes, *, run_id: int, c0a: dict[str, Any], c0a_commit: str,
) -> dict[str, Any]:
    raise C0Error(
        "weak single-run authentication is forbidden; use "
        "scripts/verify_benchmark_v15_c0_publication.py"
    )


def assemble_c0t(
    c0a_path: Path, c0a_commit: str, run_id: int, *, api_fetch: ApiFetch | None = None,
    activation_verifier: ActivationVerifier | None = None,
) -> dict[str, Any]:
    raise C0Error(
        "C0T compilation requires the strict repository/run-list/rules/ancestry adapter: "
        "scripts/verify_benchmark_v15_c0_publication.py compile-c0t"
    )


def _require_p1_activation(
    pool: dict[str, Any], verifier: ActivationVerifier | None,
) -> dict[str, Any]:
    """Call the future public P1 activation verifier or fail closed.

    The verifier interface is intentionally not represented by a boolean or a
    caller-authored JSON field. Until the separately public and replayable
    exact P1R verifier is installed,
    neither the CLI nor a bare P1A/P1T binding can mint/accept C0T.
    """
    if verifier is None or not callable(verifier):
        raise C0Error(
            "separately public replayable P1 activation verifier is required; "
            "bare P1A/P1T and caller booleans are not authority"
        )
    try:
        result = verifier(pool)
    except C0Error:
        raise
    except Exception as exc:
        raise C0Error(f"P1 public activation verification failed: {exc}") from exc
    keys = {"p1r", "p1r_commit", "activation_boundary"}
    if not isinstance(result, dict) or set(result) != keys:
        raise C0Error("P1 activation verifier did not return the exact frozen binding")
    p1r = result.get("p1r")
    if (
        not isinstance(p1r, dict) or set(p1r) != {"path", "sha256"}
        or p1r.get("path") != P1R_PATH
        or not pass_pool.SHA256_RE.fullmatch(str(p1r.get("sha256", "")))
        or not OID_RE.fullmatch(str(result.get("p1r_commit", "")))
        or result.get("activation_boundary") != "PUBLIC_AUTHENTICATED_P1R"
    ):
        raise C0Error("P1 activation verifier did not authenticate exact public P1R")
    return copy.deepcopy(result)


def validate_c0t(
    value: dict[str, Any], *, observed_run_raw: bytes | None = None,
    api_fetch: ApiFetch | None = None, c0t_commit: str | None = None,
    artifact_path: Path | None = None,
    activation_verifier: ActivationVerifier | None = None,
) -> None:
    raise C0Error(
        "commit-optional C0T validation is forbidden; use "
        "scripts/verify_benchmark_v15_c0_publication.py verify-c0t --commit <exact-oid>"
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise C0Error("C0 output already exists; overwrite is forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


def _source_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--pass-pool", type=Path, required=True)
    parser.add_argument("--private-registry", type=Path, required=True)
    parser.add_argument("--aggregate-certificate", type=Path, required=True)
    parser.add_argument("--replay-attestation", type=Path, required=True)
    parser.add_argument("--pass-receipt", type=Path, required=True)
    parser.add_argument("--prior-public-chain-proof", type=Path, required=True)
    parser.add_argument("--pass-public-chain-proof", type=Path, required=True)
    parser.add_argument("--p1a", type=Path, required=True)
    parser.add_argument("--p1t", type=Path, required=True)
    parser.add_argument("--public-repository", type=Path, required=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build_a = commands.add_parser("build-c0a")
    _source_args(build_a)
    build_a.add_argument("--future-drand-round", type=int, required=True)
    build_a.add_argument("--c0a-path", required=True)
    build_a.add_argument("--c0t-path", required=True)
    build_a.add_argument("--workflow-path", required=True)
    build_a.add_argument("--output", type=Path, required=True)
    build_t = commands.add_parser("build-c0t")
    build_t.add_argument("--c0a", type=Path, required=True)
    build_t.add_argument("--c0a-commit", required=True)
    build_t.add_argument("--github-actions-run-id", type=int, required=True)
    build_t.add_argument("--output", type=Path, required=True)
    check_a = commands.add_parser("validate-c0a")
    check_a.add_argument("--c0a", type=Path, required=True)
    check_t = commands.add_parser("validate-c0t")
    check_t.add_argument("--c0t", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build-c0a":
            source_paths = {
                name: getattr(args, name).resolve() for name in (
                    "private_registry", "aggregate_certificate", "replay_attestation",
                    "pass_receipt", "prior_public_chain_proof", "pass_public_chain_proof", "p1a", "p1t",
                )
            }
            value = assemble_c0a(
                args.pass_pool.resolve(), source_paths=source_paths,
                public_repository=args.public_repository.resolve(),
                future_drand_round=args.future_drand_round, c0a_path=args.c0a_path,
                c0t_path=args.c0t_path, workflow_path=args.workflow_path,
            )
            write_json(args.output.resolve(), value)
        elif args.command == "build-c0t":
            raise C0Error(
                "C0T authority requires scripts/verify_benchmark_v15_c0_publication.py compile-c0t"
            )
        elif args.command == "validate-c0a":
            validate_c0a(load_json(args.c0a.resolve(), "C0A"))
        else:
            raise C0Error(
                "C0T authority requires scripts/verify_benchmark_v15_c0_publication.py verify-c0t"
            )
    except (OSError, C0Error) as exc:
        print(f"INVALID_C0: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
