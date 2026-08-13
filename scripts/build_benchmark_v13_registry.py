#!/usr/bin/env python3
"""Perform the sole production Method v1.3 registry build.

This command is intentionally one shot.  It accepts only a post-P0T/S0,
content-addressed build request, resolves the frozen upstream ref once, and
writes bounded identity metadata to a previously absent output directory.  It
does not print target identities or statement text and it never uses entropy.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Iterator

import jsonschema

import build_benchmark_contamination_v13 as contamination
import build_benchmark_v13_p0 as p0
import build_benchmark_v13_pool as syntax
import build_benchmark_v13_source_snapshot as source_snapshot
import select_benchmark_v13 as selector


ROOT = Path(__file__).parents[1].resolve()
INPUT_SCHEMA = ROOT / "schemas/benchmark-registry-input-v1.3.schema.json"
OUTPUT_SCHEMA = ROOT / "schemas/benchmark-registry-output-v1.3.schema.json"
INPUT_SCHEMA_VERSION = "c5k4-registry-build-input-1.3"
OUTPUT_SCHEMA_VERSION = "c5k4-registry-build-output-1.3"
PREFLIGHT_SCHEMA_VERSION = "c5k4-registry-preflight-input-1.3"
RECEIPT_SCHEMA_VERSION = "c5k4-resolver-receipt-1.3"
STRATA = tuple(selector.STRATA)
QUOTAS = dict(selector.QUOTAS)
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
OUTPUT_FILES = {
    "open_inventory": "open-inventory.json",
    "question_cluster_pool": "question-cluster-pool.json",
    "provenance_inventory": "provenance-inventory.json",
    "contamination_inventory": "contamination-inventory.json",
    "eligible_pool": "eligible-cluster-pool.json",
    "quota_feasibility": "quota-feasibility.json",
}
OUTPUT_SCHEMAS = {
    "open_inventory": "c5k4-open-inventory-1.3",
    "question_cluster_pool": "c5k4-question-cluster-pool-1.3",
    "provenance_inventory": "c5k4-provenance-inventory-1.3",
    "contamination_inventory": "c5k4-contamination-inventory-1.3",
    "eligible_pool": "c5k4-eligible-cluster-pool-1.3",
    "quota_feasibility": "c5k4-quota-feasibility-1.3",
}


class RegistryBuildError(ValueError):
    """A fail-closed production registry contract violation."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def pretty_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_digest(value: dict[str, Any], digest_key: str | None = None) -> str:
    if digest_key is not None:
        value = {key: item for key, item in value.items() if key != digest_key}
    return sha256(canonical_json(value))


SELF_DIGEST_BY_SCHEMA = {
    "c5k4-source-snapshot-S0-1.3": "snapshot_sha256",
    "c5k4-semantic-sources-config-1.3": "sources_config_sha256",
    "c5k4-contamination-inventory-1.3": "inventory_sha256",
    "c5k4-eligible-cluster-pool-1.3": "eligible_pool_sha256",
    "c5k4-quota-feasibility-1.3": "certificate_sha256",
    "c5k4-registry-exemption-rule-1.3": "inventory_sha256",
    OUTPUT_SCHEMA_VERSION: "output_sha256",
}


def artifact_object_digest(value: dict[str, Any]) -> str:
    """Apply the frozen canonical rule to an artifact with a self digest."""

    digest_key = SELF_DIGEST_BY_SCHEMA.get(value.get("schema_version"))
    return object_digest(value, digest_key if digest_key in value else None)


def timestamp(value: Any, where: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise RegistryBuildError(f"{where} must be RFC3339 UTC")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise RegistryBuildError(f"{where} is not RFC3339 UTC") from exc


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_object(path: Path, where: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegistryBuildError(f"cannot read {where}: {exc}") from exc
    if not isinstance(value, dict):
        raise RegistryBuildError(f"{where} must be one JSON object")
    return value, raw


def validate_schema(value: dict[str, Any], schema_path: Path, where: str) -> None:
    schema, _ = load_object(schema_path, f"{where} schema")
    errors = sorted(
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in errors
        )
        raise RegistryBuildError(f"{where} schema validation failed: {detail}")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise RegistryBuildError(f"artifact is outside the protocol repository: {path}") from exc


def content_ref(request: dict[str, Any], name: str) -> tuple[Path, dict[str, Any], bytes]:
    """Load and authenticate one exact request input descriptor."""

    refs = request.get("inputs")
    if not isinstance(refs, dict) or not isinstance(refs.get(name), dict):
        raise RegistryBuildError(f"request.inputs.{name} is required")
    ref = refs[name]
    path_text = ref.get("path")
    expected = ref.get("file_sha256")
    if not isinstance(path_text, str) or not path_text or not isinstance(expected, str):
        raise RegistryBuildError(f"request.inputs.{name} needs path and SHA-256")
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path
    value, raw = load_object(path.resolve(), name)
    if sha256(raw) != expected:
        raise RegistryBuildError(f"request.inputs.{name} file digest mismatch")
    canonical = ref.get("canonical_sha256")
    if canonical is not None and canonical != artifact_object_digest(value):
        raise RegistryBuildError(f"request.inputs.{name} canonical digest mismatch")
    if value.get("schema_version") != ref.get("schema_version"):
        raise RegistryBuildError(f"request.inputs.{name} schema version mismatch")
    if "prototype" in str(ref.get("schema_version", "")).casefold():
        raise RegistryBuildError(f"request.inputs.{name} is a prototype input")
    return path.resolve(), value, raw


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def preflight(request_path: Path, receipt_dir: Path) -> dict[str, dict[str, Any]]:
    """Make exactly the two frozen network calls and preserve raw responses."""

    request, _ = load_object(request_path.resolve(), "registry preflight request")
    if set(request) != {
        "schema_version", "p0t_commit", "public_remote_url",
        "upstream_resolution_command", "resolved_at_utc",
    } or request.get("schema_version") != PREFLIGHT_SCHEMA_VERSION:
        raise RegistryBuildError("preflight request has an unsupported or unbounded shape")
    if not HEX40.fullmatch(str(request.get("p0t_commit", ""))):
        raise RegistryBuildError("preflight p0t_commit must be an exact lowercase SHA-1")
    timestamp(request.get("resolved_at_utc"), "preflight resolution time")
    remote = request.get("public_remote_url")
    if not isinstance(remote, str) or not remote:
        raise RegistryBuildError("preflight public remote must be nonempty")
    upstream_command = [
        "git", "ls-remote", "https://github.com/google-deepmind/formal-conjectures.git",
        "refs/heads/main",
    ]
    if request.get("upstream_resolution_command") != upstream_command:
        raise RegistryBuildError("preflight upstream command differs from frozen command")
    if receipt_dir.exists() or not receipt_dir.parent.is_dir():
        raise RegistryBuildError("receipt directory must be absent with an existing parent")

    # Deliberately two calls, written without a retry loop.
    public_raw = subprocess.run(
        ["git", "ls-remote", remote], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.decode("ascii", "strict")
    upstream_raw = subprocess.run(
        upstream_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.decode("ascii", "strict")
    advertised = request["p0t_commit"] in {
        row.split()[0] for row in public_raw.splitlines() if row.split()
    }
    if not advertised:
        raise RegistryBuildError("preflight public remote does not advertise P0T")
    upstream_rows = [row.split() for row in upstream_raw.splitlines() if row.split()]
    if len(upstream_rows) != 1 or len(upstream_rows[0]) != 2 or upstream_rows[0][1] != "refs/heads/main" or not HEX40.fullmatch(upstream_rows[0][0]):
        raise RegistryBuildError("preflight upstream response is not one exact main ref")
    receipts = {
        "public_p0t": {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "authority": "FROZEN_PRODUCTION_INPUT",
            "kind": "PUBLIC_P0T_ADVERTISEMENT",
            "resolved_at_utc": request["resolved_at_utc"],
            "command": ["git", "ls-remote", remote],
            "remote_url": remote,
            "p0t_commit": request["p0t_commit"],
            "advertised": True,
            "stdout": public_raw,
            "stdout_sha256": sha256(public_raw.encode()),
        },
        "upstream_main": {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "authority": "FROZEN_PRODUCTION_INPUT",
            "kind": "UPSTREAM_MAIN_RESOLUTION",
            "resolved_at_utc": request["resolved_at_utc"],
            "command": upstream_command,
            "stdout": upstream_raw,
            "stdout_sha256": sha256(upstream_raw.encode()),
        },
    }
    temporary = Path(tempfile.mkdtemp(prefix=f".{receipt_dir.name}.tmp-", dir=receipt_dir.parent))
    try:
        for name, value in receipts.items():
            (temporary / f"{name.replace('_', '-')}.json").write_bytes(pretty_json(value))
        os.rename(temporary, receipt_dir)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return receipts


def validate_protocol_bindings(
    request: dict[str, Any], formal_repo: Path
) -> dict[str, tuple[Path, dict[str, Any], bytes]]:
    if request.get("schema_version") != INPUT_SCHEMA_VERSION:
        raise RegistryBuildError("unsupported registry build request schema")
    if request.get("authority") != "PRODUCTION_AFTER_P0T_S0":
        raise RegistryBuildError("registry build request is not production-authoritative")
    if request.get("build_ordinal") != 1 or request.get("allowed_build_count") != 1:
        raise RegistryBuildError("production registry build must be ordinal one of one")
    controls = request.get("controls", {})
    if controls.get("entropy_used") is not False or controls.get("selected_clusters") != []:
        raise RegistryBuildError("pre-C0 production build cannot use entropy or select targets")
    if controls.get("create_exclusive_output_directory") is not True:
        raise RegistryBuildError("production output must be created exclusively")
    producer = request["producer"]
    producer_files = {
        "executable_sha256": Path(__file__).resolve(),
        "invocation_contract_sha256": ROOT / "results/benchmark/v1.3-protocol/registry-build-invocation.json",
        "input_schema_sha256": INPUT_SCHEMA,
        "output_schema_sha256": OUTPUT_SCHEMA,
    }
    for field, path in producer_files.items():
        if producer.get(field) != sha256(path.read_bytes()):
            raise RegistryBuildError(f"producer {field} does not match frozen bytes")

    # Load only protocol/source envelopes before receipt replay.  Registry
    # identity artifacts remain unread until the frozen resolution is valid.
    required = ("p0a", "p0t", "s0", "sources_config")
    loaded = {name: content_ref(request, name) for name in required}
    p0a_path, p0a, _ = loaded["p0a"]
    p0t_path, p0t, _ = loaded["p0t"]
    p0.validate_p0a(p0a)
    chronology = request["chronology"]
    p0t_commit = chronology["p0_attestation_commit"]
    if not isinstance(p0t_commit, str) or not HEX40.fullmatch(p0t_commit):
        raise RegistryBuildError("p0t_commit must be an exact lowercase SHA-1")
    p0.validate_p0t(p0t, p0t_commit=p0t_commit, artifact_path=p0t_path)
    if p0t.get("p0a_commit") != chronology["p0_artifact_commit"]:
        raise RegistryBuildError("request P0A commit differs from P0T")
    if p0t.get("p0a", {}).get("sha256") != sha256(loaded["p0a"][2]):
        raise RegistryBuildError("P0T does not bind the supplied P0A bytes")

    s0 = loaded["s0"][1]
    sources = loaded["sources_config"][1]
    if s0.get("schema_version") != source_snapshot.SNAPSHOT_SCHEMA or s0.get("complete") is not True:
        raise RegistryBuildError("S0 is absent, non-production, or incomplete")
    if sources.get("schema_version") != source_snapshot.CONFIG_SCHEMA or sources.get("prototype_only") is not False:
        raise RegistryBuildError("semantic source config is not production-authoritative")
    if s0.get("sources_config_file_sha256") != sha256(loaded["sources_config"][2]):
        raise RegistryBuildError("S0 does not bind supplied semantic source config bytes")
    if s0.get("sources_config_sha256") != sources.get("sources_config_sha256"):
        raise RegistryBuildError("S0 source config content address mismatch")
    if s0.get("p0a_commit") != chronology["p0_artifact_commit"] or s0.get("p0t_commit") != p0t_commit:
        raise RegistryBuildError("S0 is not bound to supplied P0A/P0T")
    published = timestamp(s0.get("p0a_published_at_utc"), "S0 P0 publication")
    acquired = timestamp(s0.get("acquired_at_utc"), "S0 acquisition")
    if chronology["s0_snapshot_id"] != "S0" or chronology["s0_snapshot_sha256"] != s0.get("snapshot_sha256"):
        raise RegistryBuildError("request chronology does not bind exact S0")
    if chronology["p0_published_at_utc"] != s0.get("p0a_published_at_utc") or chronology["s0_acquired_at_utc"] != s0.get("acquired_at_utc"):
        raise RegistryBuildError("request chronology differs from P0/S0 artifacts")
    checked = acquired
    if not published < acquired <= checked:
        raise RegistryBuildError("chronology must satisfy public P0T < S0 <= gate")
    source_snapshot.verify_config_sources(sources)

    components = p0a.get("components", {})
    frozen_producer = next(
        (row for row in p0a.get("allowlisted_registry_producers", []) if row.get("producer_id") == producer["producer_id"]),
        None,
    )
    if frozen_producer is None:
        raise RegistryBuildError("registry producer is not allowlisted by P0A")
    for field in ("executable", "invocation_contract", "input_schema", "output_schema"):
        if frozen_producer[field]["sha256"] != producer[f"{field}_sha256"]:
            raise RegistryBuildError(f"P0A producer {field} digest mismatch")
    upstream_rule = components.get("upstream_ref_rule")
    if not isinstance(upstream_rule, dict):
        raise RegistryBuildError("P0A lacks upstream ref rule")
    rule_path = ROOT / upstream_rule["path"]
    rule, rule_raw = load_object(rule_path, "upstream ref rule")
    if sha256(rule_raw) != upstream_rule["sha256"]:
        raise RegistryBuildError("upstream ref rule differs from frozen P0 component")
    expected_rule = loaded.get("upstream_ref_rule")
    if expected_rule is not None and expected_rule[2] != rule_raw:
        raise RegistryBuildError("request upstream rule differs from P0")
    if rule.get("retry_or_repin") is not False or rule.get("required_matches") != 1:
        raise RegistryBuildError("upstream rule must forbid retry/repin and require one match")
    if rule.get("remote_ref") != "refs/heads/main":
        raise RegistryBuildError("production upstream ref must be refs/heads/main")

    receipts = request.get("resolver_receipts")
    if not isinstance(receipts, dict):
        raise RegistryBuildError("offline build requires frozen resolver receipts")
    public_receipt_path, public_receipt, _ = content_ref(
        {"inputs": {"public_p0t": receipts.get("public_p0t")}}, "public_p0t"
    )
    upstream_receipt_path, upstream_receipt, _ = content_ref(
        {"inputs": {"upstream_main": receipts.get("upstream_main")}}, "upstream_main"
    )
    del public_receipt_path, upstream_receipt_path
    if public_receipt.get("kind") != "PUBLIC_P0T_ADVERTISEMENT" or public_receipt.get("p0t_commit") != p0t_commit or public_receipt.get("advertised") is not True:
        raise RegistryBuildError("public P0T resolver receipt does not authenticate P0T")
    if public_receipt.get("stdout_sha256") != sha256(public_receipt.get("stdout", "").encode()) or p0t_commit not in {row.split()[0] for row in public_receipt.get("stdout", "").splitlines() if row.split()}:
        raise RegistryBuildError("public P0T receipt raw response does not replay")
    if public_receipt.get("remote_url") != loaded["sources_config"][1].get("protocol", {}).get("public_remote_url"):
        raise RegistryBuildError("public P0T resolver receipt remote differs from S0")
    if upstream_receipt.get("kind") != "UPSTREAM_MAIN_RESOLUTION" or upstream_receipt.get("command") != rule["resolution_command"]:
        raise RegistryBuildError("upstream resolver receipt differs from frozen command")
    if upstream_receipt.get("stdout_sha256") != sha256(upstream_receipt.get("stdout", "").encode()):
        raise RegistryBuildError("upstream receipt raw response digest does not replay")
    public_resolved = timestamp(public_receipt.get("resolved_at_utc"), "public receipt time")
    upstream_resolved = timestamp(upstream_receipt.get("resolved_at_utc"), "upstream receipt time")
    invoked = timestamp(request.get("registry_build_invoked_at_utc"), "registry invocation time")
    if public_resolved != upstream_resolved or not acquired <= public_resolved <= invoked:
        raise RegistryBuildError("receipt chronology must satisfy S0 <= resolution <= invocation")

    for name in (
        "five_strata_classifier", "grouping_rule", "provenance_policy",
        "source_discovery_boundary", "quotas", "registry_exemptions",
    ):
        loaded[name] = content_ref(request, name)
    bindings = {
        "five_strata_classifier": "five_strata_classifier",
        "grouping_rule": "grouping_rule",
        "provenance_policy": "provenance_policy",
        "source_discovery_boundary": "source_discovery_boundary",
        "quotas": "quotas",
    }
    for input_name, component_name in bindings.items():
        component = components.get(component_name)
        if not isinstance(component, dict) or component.get("sha256") != sha256(loaded[input_name][2]):
            raise RegistryBuildError(f"{input_name} differs from frozen P0 component")
    if loaded["quotas"][1].get("quotas") != QUOTAS:
        raise RegistryBuildError("quota artifact differs from fixed 3/3/2/2/2 design")
    exemption_component = components.get("registry_exemption_rule")
    if not isinstance(exemption_component, dict):
        raise RegistryBuildError("P0A lacks the registry exemption rule")
    if sha256(loaded["registry_exemptions"][2]) != exemption_component["sha256"]:
        raise RegistryBuildError("registry exemption rule differs from frozen P0 component")
    validate_exemption_ledger(
        loaded["registry_exemptions"][1], loaded["provenance_policy"][1],
    )

    # Consume the sole content-addressed resolution; offline build never calls
    # the network, retries, or repins.
    resolved_rows = upstream_receipt.get("stdout", "").splitlines()
    matches = [row.split() for row in resolved_rows if row.split()]
    if len(matches) != 1 or len(matches[0]) != 2 or matches[0][1] != rule["remote_ref"]:
        raise RegistryBuildError("upstream resolution did not return exactly one required ref")
    resolved_commit = matches[0][0]
    if not HEX40.fullmatch(resolved_commit):
        raise RegistryBuildError("upstream ref did not resolve to a lowercase SHA-1 commit")
    requested_upstream = request.get("upstream")
    if not isinstance(requested_upstream, dict) or requested_upstream.get("commit") != resolved_commit:
        raise RegistryBuildError("request upstream commit differs from sole resolution")
    local_commit = git(formal_repo, "rev-parse", f"{resolved_commit}^{{commit}}").decode().strip()
    local_tree = git(formal_repo, "rev-parse", f"{resolved_commit}^{{tree}}").decode().strip()
    if local_commit != resolved_commit or requested_upstream.get("tree") != local_tree:
        raise RegistryBuildError("local checkout does not contain the exact resolved commit/tree")
    if requested_upstream.get("repository") != "https://github.com/google-deepmind/formal-conjectures.git" or requested_upstream.get("subtree") != "FormalConjectures":
        raise RegistryBuildError("request upstream identity is not the frozen registry/subtree")
    loaded["_upstream_rule"] = (rule_path, rule, rule_raw)
    return loaded


def normalize_sources(s0: dict[str, Any]) -> dict[str, Any]:
    """Adapt S0 source records to the semantics-blind replay library API."""

    rows: list[dict[str, Any]] = []
    for source in s0["sources"]:
        kind = source["kind"]
        base = {**source, "id": source["source_id"]}
        if kind == "git_history":
            rows.append({**base, "kind": "git", "tips": [row["object_id"] for row in source["tips"]]})
        elif kind == "git_user_delta":
            rows.append({
                **base,
                "kind": "git_delta",
                "tips": sorted({source["head_commit"], *[row["object_id"] for row in source["tips"]]}),
                "excluded_commits": sorted(row["object_id"] for row in source["upstream_base_refs"]),
                "_scan_overlay": True,
            })
        elif kind == "tree":
            rows.append({**base, "kind": "tree"})
        elif kind == "git_sessions":
            for mirror in source["session_mirrors"]:
                rows.append({
                    **base,
                    "id": source["source_id"] + ":" + mirror["id"],
                    "kind": "git_sessions",
                    "ref": source["immutable_commit"],
                    "subdir": mirror["ai_chats_subdir"],
                    "format": mirror["format"],
                })
        elif kind == "release_metadata_snapshot":
            rows.append({**base, "kind": "release_snapshot"})
        else:
            raise RegistryBuildError(f"unsupported frozen S0 source kind: {kind!r}")
    return {
        "schema_version": contamination.CONFIG_SCHEMA,
        "artifact_status": contamination.ARTIFACT_STATUS,
        "sources": rows,
    }


def validate_exemption_ledger(
    ledger: dict[str, Any], policy: dict[str, Any]
) -> None:
    """Validate the P0-frozen unit-exact exemption ledger without global hashes."""

    if ledger.get("schema_version") != "c5k4-registry-exemption-rule-1.3":
        raise RegistryBuildError("registry exemption ledger is not the production schema")
    if ledger.get("artifact_status") != "AUTHORITATIVE_P0_PROTOCOL" or ledger.get("complete") is not True:
        raise RegistryBuildError("registry exemption ledger is not complete P0 authority")
    if ledger.get("policy", {}).get("global_content_hash_allowlist") is not False:
        raise RegistryBuildError("global content-hash exemptions are forbidden")
    units = ledger.get("units")
    if not isinstance(units, list):
        raise RegistryBuildError("registry exemption units must be an array")
    identities: set[str] = set()
    required = set(policy["machine_exemption_required_fields"])
    required_true = set(policy["machine_exemption_required_true"])
    for index, row in enumerate(units):
        if not isinstance(row, dict) or not required.issubset(row):
            raise RegistryBuildError(f"registry exemption unit {index} lacks required fields")
        if any(row.get(field) is not True for field in required_true):
            raise RegistryBuildError(f"registry exemption unit {index} lacks verification proof")
        if row.get("role") not in policy["machine_roles"]:
            raise RegistryBuildError(f"registry exemption unit {index} is not a machine role")
        if row.get("source_kind") not in policy["machine_source_kinds"].get(row["role"], []):
            raise RegistryBuildError(f"registry exemption unit {index} role/source mismatch")
        if row.get("content_schema") not in policy["bounded_content_schemas"]:
            raise RegistryBuildError(f"registry exemption unit {index} lacks bounded schema")
        identity = contamination.provenance.unit_identity_sha256(row)
        if row.get("unit_identity_sha256") != identity or identity in identities:
            raise RegistryBuildError(f"registry exemption unit {index} identity is invalid or duplicate")
        identities.add(identity)
    if ledger.get("registry_only_unit_identity_sha256") != sorted(identities):
        raise RegistryBuildError("registry-only unit identity index does not replay")
    if ledger.get("inventory_sha256") != object_digest(ledger, "inventory_sha256"):
        raise RegistryBuildError("registry exemption ledger self digest does not replay")


@contextmanager
def production_replay_context(
    frozen_policy: dict[str, Any], captured: dict[str, dict[str, Any]]
) -> Iterator[None]:
    """Inject frozen policy and S0 delta-overlay support without a second scan."""

    original_load = contamination.provenance.load_policy
    original_classify = contamination.provenance.classify_unit
    original_iter = contamination.iter_source

    def load_frozen(_path: Path) -> dict[str, Any]:
        return frozen_policy

    def classify_and_capture(unit: dict[str, Any], exemption: Any, policy: dict[str, Any]):
        result = original_classify(unit, exemption, policy)
        identity = result["unit_identity_sha256"]
        stored = {
            "result": result,
            "mixed": bool(unit.get("mixed")),
            "exemption": exemption,
        }
        if identity in captured and captured[identity] != stored:
            raise RegistryBuildError(f"conflicting scan-unit provenance for {identity}")
        captured[identity] = stored
        return result

    def iter_with_overlay(source: dict[str, Any], registry_units: dict):
        yield from original_iter(source, registry_units)
        if source.get("_scan_overlay"):
            yield from contamination.iter_worktree_overlay(Path(source["path"]), source)

    contamination.provenance.load_policy = load_frozen
    contamination.provenance.classify_unit = classify_and_capture
    contamination.iter_source = iter_with_overlay
    try:
        yield
    finally:
        contamination.provenance.load_policy = original_load
        contamination.provenance.classify_unit = original_classify
        contamination.iter_source = original_iter


def production_artifacts(
    request: dict[str, Any], loaded: dict[str, tuple[Path, dict[str, Any], bytes]],
    formal_repo: Path,
) -> dict[str, dict[str, Any]]:
    request_upstream = request["upstream"]
    upstream = {
        "repository": "google-deepmind/formal-conjectures",
        "commit": request_upstream["commit"],
        "tree": request_upstream["tree"],
    }
    rules_path, rules, rules_raw = loaded["five_strata_classifier"]
    old_commit, old_tree = syntax.PINNED_COMMIT, syntax.PINNED_TREE
    syntax.PINNED_COMMIT, syntax.PINNED_TREE = upstream["commit"], upstream["tree"]
    try:
        extracted_upstream, declarations = syntax.extract(formal_repo, rules, enforce_pin=True)
    finally:
        syntax.PINNED_COMMIT, syntax.PINNED_TREE = old_commit, old_tree
    if extracted_upstream != {"commit": upstream["commit"], "tree": upstream["tree"]}:
        raise RegistryBuildError("syntax extraction drifted from resolved upstream")

    proto_inventory = syntax.build_inventory(extracted_upstream, declarations, rules_path)
    proto_pool = syntax.build_pool(proto_inventory, object_digest(proto_inventory), rules_path)
    open_inventory = {
        **proto_inventory,
        "schema_version": OUTPUT_SCHEMAS["open_inventory"],
        "artifact_status": "PRODUCTION_REGISTRY_BUILD",
    }
    open_inventory["upstream"] = {**upstream, "declaration_root": "FormalConjectures"}
    open_inventory["extraction_policy"] = {
        **open_inventory["extraction_policy"],
        "classifier_path": repo_relative(rules_path),
        "classifier_sha256": sha256(rules_raw),
    }
    question_pool = {
        **proto_pool,
        "schema_version": OUTPUT_SCHEMAS["question_cluster_pool"],
        "artifact_status": "PRODUCTION_REGISTRY_BUILD",
        "upstream": {key: upstream[key] for key in ("repository", "commit", "tree")},
        "open_inventory_sha256": object_digest(open_inventory),
        "classifier": {"path": repo_relative(rules_path), "sha256": sha256(rules_raw)},
    }

    # The replay library consumes its own bounded prototype interface, but all
    # persisted artifacts below are production-only versions.
    proto_pool["upstream"] = question_pool["upstream"]
    captured: dict[str, dict[str, Any]] = {}
    with production_replay_context(loaded["provenance_policy"][1], captured):
        proto_contamination, proto_eligible, _ = contamination.build(
            proto_pool,
            normalize_sources(loaded["s0"][1]),
            loaded["registry_exemptions"][1],
        )
    if proto_contamination.get("complete") is not True:
        raise RegistryBuildError("uncapped semantic-source replay was incomplete")
    exemption_units = loaded["registry_exemptions"][1]["units"]
    exemption_ids = {row["unit_identity_sha256"] for row in exemption_units}
    missing = exemption_ids - set(captured)
    if missing:
        raise RegistryBuildError(
            f"{len(missing)} exemption units are absent from the exact S0 scan"
        )
    for identity in exemption_ids:
        item = captured[identity]
        if item["result"]["provenance_class"] != "MACHINE_REGISTRY_CONTACT":
            raise RegistryBuildError(
                f"P0 exemption {identity} did not replay as unit-exact machine contact"
            )

    hit_counts: Counter[str] = Counter()
    for cluster in proto_contamination["clusters"]:
        for evidence in cluster["evidence"]:
            identity = evidence.get("unit_identity_sha256")
            if isinstance(identity, str):
                hit_counts[identity] += 1
    provenance_rows = []
    for identity, item in sorted(captured.items()):
        result, exemption = item["result"], item["exemption"]
        machine = result["provenance_class"] == "MACHINE_REGISTRY_CONTACT"
        provenance_rows.append({
            "unit_id": identity,
            "class": result["provenance_class"],
            "identity_evidence_count": hit_counts[identity],
            "mixed": item["mixed"],
            "producer_id": exemption.get("producer_id") if machine and isinstance(exemption, dict) else None,
            "input_sha256": exemption.get("input_sha256") if machine and isinstance(exemption, dict) else None,
            "output_sha256": exemption.get("output_sha256") if machine and isinstance(exemption, dict) else None,
            "schema_valid": bool(machine and isinstance(exemption, dict) and exemption.get("bounded_schema_verified") is True),
        })
    provenance_inventory = {
        "schema_version": OUTPUT_SCHEMAS["provenance_inventory"],
        "artifact_status": "PRODUCTION_REGISTRY_BUILD",
        "policy_sha256": sha256(loaded["provenance_policy"][2]),
        "s0_sha256": sha256(loaded["s0"][2]),
        "complete": True,
        "record_count": len(provenance_rows),
        "records": provenance_rows,
    }
    contamination_inventory = {
        **proto_contamination,
        "schema_version": OUTPUT_SCHEMAS["contamination_inventory"],
        "artifact_status": "PRODUCTION_REGISTRY_BUILD",
        "pool_sha256": object_digest(question_pool),
        "config_sha256": sha256(loaded["sources_config"][2]),
        "registry_exemptions_sha256": sha256(loaded["registry_exemptions"][2]),
    }
    contamination_inventory["inventory_sha256"] = artifact_object_digest(contamination_inventory)

    evidence_by_id = {row["cluster_id"]: row for row in proto_contamination["clusters"]}
    eligible_rows = []
    for row in question_pool["clusters"]:
        evidence = evidence_by_id[row["cluster_id"]]
        semantic = evidence["evidence_by_provenance_class"]["SEMANTIC_SOURCE"] > 0
        unknown = evidence["evidence_by_provenance_class"]["UNKNOWN"] > 0
        unambiguous = row.get("machine_stratum") in STRATA
        grouping_complete = row.get("classification_status") != "AMBIGUOUS_EXCLUDE"
        eligible = unambiguous and grouping_complete and not semantic and not unknown
        eligible_rows.append({
            **row,
            "machine_classification_unambiguous": unambiguous,
            "identity_grouping_complete": grouping_complete,
            "semantic_exposure": semantic,
            "unknown_exposure": unknown,
            "registry_contact_evidence_count": evidence["evidence_by_provenance_class"]["MACHINE_REGISTRY_CONTACT"],
            "eligible": eligible,
            "eligibility_scope": "PRODUCTION_CONTAMINATION_INTERSECTION",
        })

    frozen_hashes = {
        "open_inventory_sha256": None,
        "classifier_sha256": sha256(rules_raw),
        "provenance_policy_sha256": sha256(loaded["provenance_policy"][2]),
        "provenance_inventory_sha256": None,
        "contamination_inventory_sha256": None,
        "source_snapshots_sha256": sha256(loaded["s0"][2]),
    }
    # File hashes depend on pretty encoding, so finalize upstream artifacts
    # before binding them into the eligible pool.
    frozen_hashes["open_inventory_sha256"] = sha256(pretty_json(open_inventory))
    frozen_hashes["provenance_inventory_sha256"] = sha256(pretty_json(provenance_inventory))
    frozen_hashes["contamination_inventory_sha256"] = sha256(pretty_json(contamination_inventory))
    eligible_pool = {
        "schema_version": OUTPUT_SCHEMAS["eligible_pool"],
        "artifact_status": "CONTAMINATION_APPLIED",
        "upstream": {key: upstream[key] for key in ("repository", "commit", "tree")},
        "digests": frozen_hashes,
        "entropy_used": False,
        "selected_clusters": [],
        "clusters": eligible_rows,
    }

    counts = Counter(row["stratum"] for row in eligible_rows if row["eligible"])
    strata = [
        {
            "stratum": stratum,
            "quota": QUOTAS[stratum],
            "eligible_count": counts[stratum],
            "deficit": max(0, QUOTAS[stratum] - counts[stratum]),
            "surplus": max(0, counts[stratum] - QUOTAS[stratum]),
        }
        for stratum in STRATA
    ]
    status = "PASS" if all(row["deficit"] == 0 for row in strata) else "FAIL"
    chronology = {
        "p0_artifact_commit": request["chronology"]["p0_artifact_commit"],
        "p0_attestation_commit": request["chronology"]["p0_attestation_commit"],
        "p0_published_at_utc": loaded["s0"][1]["p0a_published_at_utc"],
        "s0_acquired_at_utc": loaded["s0"][1]["acquired_at_utc"],
        "feasibility_checked_at_utc": request["chronology"]["s0_acquired_at_utc"],
    }
    eligibility_bytes = pretty_json(eligible_pool)
    feasibility = {
        "schema_version": OUTPUT_SCHEMAS["quota_feasibility"],
        "phase": "PRE_C0_FEASIBILITY",
        "status": status,
        "upstream": eligible_pool["upstream"],
        "chronology": chronology,
        "entropy_used": False,
        "selected_clusters": [],
        "digests": {
            "eligible_pool_file_sha256": sha256(eligibility_bytes),
            "eligible_pool_canonical_sha256": object_digest(eligible_pool),
            **frozen_hashes,
        },
        "quotas": QUOTAS,
        "strata": strata,
    }
    feasibility["certificate_sha256"] = object_digest(feasibility, "certificate_sha256")

    artifacts = {
        "open_inventory": open_inventory,
        "question_cluster_pool": question_pool,
        "provenance_inventory": provenance_inventory,
        "contamination_inventory": contamination_inventory,
        "eligible_pool": eligible_pool,
        "quota_feasibility": feasibility,
    }
    replay_rows(artifacts, loaded)
    return artifacts


def replay_rows(
    artifacts: dict[str, dict[str, Any]],
    loaded: dict[str, tuple[Path, dict[str, Any], bytes]],
) -> None:
    """Replay every eligibility row and the exact five-row quota gate."""

    pool = artifacts["eligible_pool"]
    selector.validate_pool(pool)
    rows = selector.validate_pool(pool)
    for index, row in enumerate(rows):
        expected = (
            row.get("machine_classification_unambiguous") is True
            and row.get("identity_grouping_complete") is True
            and row.get("semantic_exposure") is False
            and row.get("unknown_exposure") is False
        )
        if row.get("eligible") is not expected:
            raise RegistryBuildError(
                f"eligible pool row {index} does not replay the frozen intersection"
            )
        count = row.get("registry_contact_evidence_count")
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise RegistryBuildError(
                f"eligible pool row {index} has invalid registry-contact count"
            )
    feasibility = artifacts["quota_feasibility"]
    if feasibility["status"] == "PASS":
        artifact_bytes = {
            "open_inventory": pretty_json(artifacts["open_inventory"]),
            "classifier": loaded["five_strata_classifier"][2],
            "provenance_policy": loaded["provenance_policy"][2],
            "provenance_inventory": pretty_json(artifacts["provenance_inventory"]),
            "contamination_inventory": pretty_json(artifacts["contamination_inventory"]),
            "source_snapshots": loaded["s0"][2],
        }
        selector.replay_feasibility(
            pool, pretty_json(pool), rows, feasibility, artifact_bytes
        )
    else:
        expected = [
            {
                "stratum": stratum,
                "quota": QUOTAS[stratum],
                "eligible_count": sum(row["eligible"] and row["stratum"] == stratum for row in rows),
                "deficit": max(0, QUOTAS[stratum] - sum(row["eligible"] and row["stratum"] == stratum for row in rows)),
                "surplus": max(0, sum(row["eligible"] and row["stratum"] == stratum for row in rows) - QUOTAS[stratum]),
            }
            for stratum in STRATA
        ]
        if feasibility["strata"] != expected or not any(row["deficit"] for row in expected):
            raise RegistryBuildError("FAIL feasibility certificate does not replay from rows")
        if feasibility["certificate_sha256"] != object_digest(feasibility, "certificate_sha256"):
            raise RegistryBuildError("FAIL feasibility certificate digest does not replay")


def artifact_descriptor(artifact_id: str, value: dict[str, Any]) -> dict[str, Any]:
    rows = value.get("clusters", value.get("records", value.get("strata", [])))
    return {
        "artifact_id": artifact_id,
        "path": OUTPUT_FILES[artifact_id],
        "file_sha256": sha256(pretty_json(value)),
        "canonical_sha256": artifact_object_digest(value),
        "schema_version": value["schema_version"],
        "row_count": len(rows) if isinstance(rows, list) else 0,
    }


def execute(request_path: Path, formal_repo: Path, output_dir: Path) -> dict[str, Any]:
    request, request_raw = load_object(request_path.resolve(), "registry build request")
    validate_schema(request, INPUT_SCHEMA, "registry build request")
    if output_dir.exists():
        raise RegistryBuildError("output directory already exists; retry/second build is forbidden")
    loaded = validate_protocol_bindings(request, formal_repo.resolve())
    artifacts = production_artifacts(request, loaded, formal_repo.resolve())
    descriptors = [
        artifact_descriptor(artifact_id, artifacts[artifact_id])
        for artifact_id in OUTPUT_FILES
    ]
    feasibility = artifacts["quota_feasibility"]
    eligible_pool = artifacts["eligible_pool"]
    completed_at = utc_now()
    if timestamp(completed_at, "observed completion") < timestamp(
        request["registry_build_invoked_at_utc"], "registry invocation time"
    ):
        raise RegistryBuildError("observed completion precedes registry invocation")
    output = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "authority": "PRODUCTION_REGISTRY_BUILD",
        "protocol_version": "1.3",
        "build_ordinal": 1,
        "input_file_sha256": sha256(request_raw),
        "input_canonical_sha256": object_digest(request),
        "upstream": request["upstream"],
        "chronology": {
            **request["chronology"],
            "registry_build_completed_at_utc": completed_at,
        },
        "producer": {key: request["producer"][key] for key in (
            "producer_id", "executable_sha256", "invocation_contract_sha256",
            "input_schema_sha256", "output_schema_sha256",
        )},
        "controls": {
            "prototype_inputs_used": False,
            "candidate_semantics_inspected": False,
            "entropy_used": False,
            "selected_clusters": [],
            "selection_or_ranking_performed": False,
            "output_directory_created_exclusively": True,
            "preexisting_output_replaced": False,
        },
        "artifacts": descriptors,
        "feasibility_replay": {
            "row_source_artifact_id": "eligible_pool",
            "row_source_canonical_sha256": object_digest(eligible_pool),
            "eligibility_rule": "MACHINE_CLASSIFIED_AND_IDENTITY_COMPLETE_AND_NO_SEMANTIC_OR_UNKNOWN_EXPOSURE",
            "all_rows_replayed": True,
            "total_row_count": len(eligible_pool["clusters"]),
            "eligible_row_count": sum(row["eligible"] for row in eligible_pool["clusters"]),
            "quotas": QUOTAS,
            "strata": feasibility["strata"],
            "status": feasibility["status"],
            "terminal_result": None if feasibility["status"] == "PASS" else "NO_ELIGIBLE_BENCHMARK_PRE_C0",
            "entropy_used": False,
            "selected_clusters": [],
        },
    }
    output["output_sha256"] = object_digest(output, "output_sha256")
    validate_schema(output, OUTPUT_SCHEMA, "registry build output")
    if not output_dir.parent.is_dir():
        raise RegistryBuildError("output directory parent must already exist")
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent))
    try:
        for artifact_id, filename in OUTPUT_FILES.items():
            (temporary / filename).write_bytes(pretty_json(artifacts[artifact_id]))
        (temporary / "registry-build-output.json").write_bytes(pretty_json(output))
        os.rename(temporary, output_dir)
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("preflight")
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--receipt-dir", type=Path, required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--input", type=Path, required=True)
    build.add_argument("--formal-repo", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "preflight":
        receipts = preflight(args.input, args.receipt_dir)
        print(json.dumps({"receipt_count": len(receipts), "network_call_count": 2}, sort_keys=True))
        return 0
    output = execute(args.input, args.formal_repo, args.output_dir)
    print(json.dumps({
        "authority": output["authority"],
        "upstream_commit": output["upstream"]["commit"],
        "artifact_count": len(output["artifacts"]),
        "feasibility_status": output["feasibility_replay"]["status"],
        "entropy_used": False,
        "selected_cluster_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RegistryBuildError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
