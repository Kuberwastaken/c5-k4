#!/usr/bin/env python3
"""Build the repository-only Method v1.5 P0A -> P0T -> A0 draft chain.

This program is deliberately incapable of producing an authoritative A0.  The
NitroTPM-sealed harness key and independent signatures are external authority
and must be added by the separately controlled manual activation ceremony.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from datetime import datetime

import jsonschema


ROOT = Path(__file__).resolve().parent.parent
P0A_PATH = "results/benchmark/v1.5-p0-a0/P0A.json"
P0T_PATH = "results/benchmark/v1.5-p0-a0/P0T.json"
A0_PATH = "results/benchmark/v1.5-p0-a0/A0.json"
P0A_SCHEMA = "schemas/benchmark-p0a-v1.5.schema.json"
P0T_SCHEMA = "schemas/benchmark-p0t-v1.5.schema.json"
A0_SCHEMA = "schemas/benchmark-a0-v1.5.schema.json"
RECEIPT_SCHEMA = "schemas/benchmark-p0-publication-receipt-v1.5.schema.json"
OID = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "candidate", "candidate_id", "candidate_identity", "candidate_identities",
    "statement", "statement_text", "target", "target_id", "target_identity",
    "target_rankings", "target_semantics", "entropy", "selection",
}
TARGET_DATA_KEYS = {
    "clusters", "eligible_rows", "final_eligible_rows", "selected_rows", "selected_clusters",
    "candidate_identities", "statement", "statement_text", "declarations", "candidates",
    "target_rankings", "target_semantics", "residual", "proof_route", "outcomes",
    "target_identity", "target_identities",
}
SCHEMA_CONTAINER_KEYS = {"properties", "definitions", "$defs", "patternProperties"}
REQUIRED_COMPONENTS = {
    ".github/workflows/method-v15-p0-publication-observer.yml",
    "schemas/benchmark-a0-v1.5.schema.json", "schemas/benchmark-p0a-v1.5.schema.json",
    "schemas/benchmark-p0t-v1.5.schema.json", "schemas/benchmark-p0-publication-receipt-v1.5.schema.json",
    "scripts/build_benchmark_v15_p0_a0.py", "scripts/verify_benchmark_v15_p0_a0_publication.py",
    "results/benchmark/v1.5-p0-a0/OFFLINE_PUBLICATION_WORKFLOW.md",
    "scripts/test_build_verify_benchmark_v15_p0_a0.py",
    "scripts/test_method_v15_p0_publication_observer_workflow.py",
    "scripts/verify_benchmark_v15_attestable_ami_acceptance.py",
    "schemas/benchmark-attestable-ami-plan-v1.5.schema.json",
    "schemas/benchmark-attestable-ami-receipt-v1.5.schema.json",
    "schemas/benchmark-attestable-ami-authority-binding-v1.5.schema.json",
    "infra/benchmark-v1.5/attestable-ami/plan.json",
}
AMI_POLICY_COMPONENTS = (
    "scripts/verify_benchmark_v15_attestable_ami_acceptance.py",
    "schemas/benchmark-attestable-ami-plan-v1.5.schema.json",
    "schemas/benchmark-attestable-ami-receipt-v1.5.schema.json",
    "schemas/benchmark-attestable-ami-authority-binding-v1.5.schema.json",
    "infra/benchmark-v1.5/attestable-ami/plan.json",
)


class ChainError(ValueError):
    pass


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise ChainError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChainError(f"cannot read strict JSON {path}") from exc
    if not isinstance(value, dict):
        raise ChainError(f"{path} must contain one JSON object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def domain_digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + canonical_bytes(value)).hexdigest()


def self_digest(domain: str, value: dict[str, Any], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return domain_digest(domain, unsigned)


def _git(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(repo), *args],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"},
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise ChainError("sanitized Git query failed") from exc


def exact_commit(repo: Path, commit: str) -> str:
    if OID.fullmatch(commit) is None:
        raise ChainError("commit must be an exact lowercase SHA-1 object ID")
    resolved = _git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise ChainError("commit did not resolve to itself")
    return commit


def commit_bytes(repo: Path, commit: str, path: str) -> bytes:
    if path.startswith("/") or ".." in Path(path).parts or "\x00" in path:
        raise ChainError("repository path is not normalized")
    return _git(repo, "show", f"{commit}:{path}")


def blob_binding(repo: Path, commit: str, path: str) -> dict[str, str]:
    raw = commit_bytes(repo, commit, path)
    oid = _git(repo, "rev-parse", f"{commit}:{path}").decode().strip()
    if OID.fullmatch(oid) is None:
        raise ChainError(f"{path} did not resolve to an exact blob")
    return {"path": path, "blob_oid": oid, "sha256": hashlib.sha256(raw).hexdigest()}


def validate_schema(value: dict[str, Any], schema_path: str) -> None:
    schema = load_json(ROOT / schema_path)
    receipt = load_json(ROOT / RECEIPT_SCHEMA)
    resolver = jsonschema.RefResolver.from_schema(
        schema, store={receipt["$id"]: receipt, Path(RECEIPT_SCHEMA).name: receipt}
    )
    try:
        jsonschema.Draft7Validator(schema, resolver=resolver, format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.ValidationError as exc:
        raise ChainError(f"schema validation failed at {list(exc.absolute_path)}: {exc.message}") from exc


def assert_target_blind(value: Any, location: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ChainError(f"target-bearing key forbidden at {location}.{key}")
            assert_target_blind(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_target_blind(child, f"{location}[{index}]")


def audit_json_component(value: Any, path: str, trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        inside_schema = any(part in SCHEMA_CONTAINER_KEYS for part in trail)
        for key, child in value.items():
            folded = str(key).casefold()
            nonempty = child is not None and child is not False and child not in ("", [], {})
            if folded in TARGET_DATA_KEYS and nonempty and not inside_schema:
                raise ChainError(f"{path} contains populated target-data field {'.'.join((*trail, str(key)))}")
            audit_json_component(child, path, (*trail, str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            audit_json_component(child, path, (*trail, str(index)))


def validate_authority_policy(policy: dict[str, Any]) -> None:
    if set(policy) != {"required_independent_signature_count", "independent_authorities", "authority_roster_sha256", "attestable_ami_authority_binding_policy_sha256", "harness_key_policy"}:
        raise ChainError("authority policy has an open or incomplete shape")
    count = policy["required_independent_signature_count"]
    authorities = policy["independent_authorities"]
    if not isinstance(count, int) or count < 2 or not isinstance(authorities, list) or len(authorities) < count:
        raise ChainError("at least two frozen independent authorities are required")
    ids: set[str] = set()
    hashes: set[str] = set()
    for authority in authorities:
        if not isinstance(authority, dict) or set(authority) != {"authority_id", "verification_key_sha256", "key_origin"}:
            raise ChainError("independent authority has an open or incomplete shape")
        if authority["key_origin"] != "EXTERNAL_PUBLIC_KEY_HASH_FROZEN_BEFORE_P0A":
            raise ChainError("authority keys must originate outside the builder")
        if not isinstance(authority["authority_id"], str) or not authority["authority_id"]:
            raise ChainError("authority_id must be nonempty")
        if HEX64.fullmatch(str(authority["verification_key_sha256"])) is None:
            raise ChainError("authority verification-key hash is invalid")
        if authority["authority_id"] in ids or authority["verification_key_sha256"] in hashes:
            raise ChainError("independent authority identities and keys must be distinct")
        ids.add(authority["authority_id"]); hashes.add(authority["verification_key_sha256"])
    if policy["harness_key_policy"] != {
        "algorithm": "Ed25519", "storage": "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY",
        "verification_key_hash_known_at_p0a": False, "raw_private_key_egress_permitted": False,
    }:
        raise ChainError("harness key policy is not the frozen NitroTPM policy")
    roster = {"required_independent_signature_count": count, "independent_authorities": authorities}
    if policy["authority_roster_sha256"] != domain_digest("c5k4-method-v1.5-a0-authority-roster-1.0", roster):
        raise ChainError("authority roster canonical digest mismatch")
    if HEX64.fullmatch(str(policy["attestable_ami_authority_binding_policy_sha256"])) is None:
        raise ChainError("attestable AMI authority-binding policy commitment is absent")


def validate_receipt(repo: Path, receipt: dict[str, Any], kind: str, commit: str, path: str, raw: bytes) -> None:
    validate_schema(receipt, RECEIPT_SCHEMA)
    if receipt["subject"] != {
        "artifact_kind": kind, "path": path, "commit": commit,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }:
        raise ChainError("Actions receipt does not bind the exact published subject")
    projection = receipt["actions_run"]
    if projection["head_sha"] != commit:
        raise ChainError("Actions receipt head SHA differs from the subject commit")
    if projection["workflow_commit"] != commit:
        raise ChainError("Actions receipt workflow commit differs from the subject commit")
    workflow_raw = commit_bytes(repo, commit, projection["workflow_path"])
    if projection["workflow_blob_sha256"] != hashlib.sha256(workflow_raw).hexdigest():
        raise ChainError("Actions receipt workflow digest differs from exact commit bytes")
    projection_unsigned = dict(projection); projection_unsigned.pop("api_projection_sha256", None); projection_unsigned.pop("captured_ref_sha256", None)
    if projection["api_projection_sha256"] != domain_digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", projection_unsigned):
        raise ChainError("Actions bounded API projection digest mismatch")
    try:
        created = datetime.fromisoformat(projection["created_at_utc"].replace("Z", "+00:00"))
        started = datetime.fromisoformat(projection["run_started_at_utc"].replace("Z", "+00:00"))
        completed = datetime.fromisoformat(projection["updated_at_utc"].replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ChainError("Actions receipt server time is invalid") from exc
    if not created <= started <= completed:
        raise ChainError("Actions receipt chronology must satisfy create <= start <= completion")
    expected = self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", receipt, "receipt_sha256")
    if receipt["receipt_sha256"] != expected:
        raise ChainError("Actions receipt canonical digest mismatch")


def build_p0a(repo: Path, base_commit: str, manifest: dict[str, Any], authority_policy: dict[str, Any]) -> dict[str, Any]:
    exact_commit(repo, base_commit)
    assert_target_blind(manifest); assert_target_blind(authority_policy)
    validate_authority_policy(authority_policy)
    if set(manifest) != {"component_paths"} or not isinstance(manifest["component_paths"], list) or not manifest["component_paths"]:
        raise ChainError("component manifest must contain one nonempty component_paths list")
    paths = manifest["component_paths"]
    if paths != sorted(set(paths)) or any(not isinstance(path, str) for path in paths):
        raise ChainError("component paths must be unique and lexicographically sorted")
    if set(paths) != REQUIRED_COMPONENTS:
        raise ChainError("component manifest must equal the exact frozen P0/A0 and AMI policy closure")
    components = []
    json_audited = 0
    for path in paths:
        binding = blob_binding(repo, base_commit, path)
        if Path(path).suffix.casefold() == ".json":
            component_value = strict_json_bytes(commit_bytes(repo, base_commit, path), path)
            audit_json_component(component_value, path); json_audited += 1
        components.append(binding)
    by_path = {row["path"]: row for row in components}
    ami_policy_components = [by_path[path] for path in AMI_POLICY_COMPONENTS]
    ami_policy_digest = domain_digest("c5k4-method-v1.5-attestable-ami-authority-binding-policy-template-1.0", ami_policy_components)
    if authority_policy["attestable_ami_authority_binding_policy_sha256"] != ami_policy_digest:
        raise ChainError("attestable AMI authority-binding policy digest does not match exact frozen components")
    value: dict[str, Any] = {
        "schema": "c5k4-method-v1.5-p0a-1.0", "artifact_kind": "P0A",
        "status": "AUTHORITATIVE_TARGET_BLIND_PROTOCOL_FREEZE_NO_OPERATIONAL_AUTHORITY",
        "protocol_version": "1.5", "target_specific": False,
        "protocol_base_commit": base_commit, "components": components,
        "components_sha256": domain_digest("c5k4-method-v1.5-p0a-components-1.0", components),
        "target_data_audit": {
            "algorithm": "STRUCTURAL_JSON_KEY_AUDIT_V1_5", "json_component_count": json_audited,
            "populated_target_data_fields_detected": 0,
            "free_text_or_python_semantic_audit_claimed": False,
        },
        "authority_policy": authority_policy,
        "chronology_policy": {
            "p0a_commit_changes_only_p0a": True, "p0t_must_be_sole_parent_child": True,
            "a0_must_be_sole_parent_child_of_p0t": True, "post_hoc_component_substitution_permitted": False,
        },
        "activation_policy": {
            "operational_authority": False, "a0_draft_is_activation": False,
            "external_nitrotpm_harness_key_hash_required": True,
            "independent_authority_signatures_required": authority_policy["required_independent_signature_count"],
            "repository_builder_may_mint_authoritative_a0": False,
        },
        "p0a_sha256": "0" * 64,
    }
    value["p0a_sha256"] = self_digest("c5k4-method-v1.5-p0a-1.0", value, "p0a_sha256")
    validate_schema(value, P0A_SCHEMA)
    return value


def strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChainError(f"JSON component is not strict UTF-8 JSON: {label}") from exc
    if not isinstance(value, dict):
        raise ChainError(f"JSON component must be an object: {label}")
    return value


def _replay_observation(repo: Path, receipt: dict[str, Any], kind: str, commit: str) -> None:
    spec = importlib.util.spec_from_file_location("p0_publication_verifier", ROOT / "scripts/verify_benchmark_v15_p0_a0_publication.py")
    if spec is None or spec.loader is None:
        raise ChainError("independent Actions replay verifier is unavailable")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.replay_actions_observation(repo, receipt, kind=kind, commit=commit)


def build_p0t(repo: Path, p0a_commit: str, receipt: dict[str, Any], *, observation_verifier: Any = _replay_observation) -> dict[str, Any]:
    exact_commit(repo, p0a_commit)
    raw = commit_bytes(repo, p0a_commit, P0A_PATH)
    p0a = json.loads(raw, object_pairs_hook=_pairs)
    validate_schema(p0a, P0A_SCHEMA)
    validate_receipt(repo, receipt, "P0A", p0a_commit, P0A_PATH, raw)
    observation_verifier(repo, receipt, "P0A", p0a_commit)
    value: dict[str, Any] = {
        "schema": "c5k4-method-v1.5-p0t-1.0", "artifact_kind": "P0T",
        "status": "P0A_PUBLICATION_ATTESTED_NO_OPERATIONAL_AUTHORITY", "protocol_version": "1.5",
        "target_specific": False,
        "p0a": {"path": P0A_PATH, "commit": p0a_commit, "sha256": hashlib.sha256(raw).hexdigest(), "canonical_sha256": p0a["p0a_sha256"]},
        "p0a_publication_receipt": receipt,
        "topology_policy": {"parent_must_be_exact_p0a": True, "allowed_changed_paths": [P0T_PATH]},
        "activation_authority": False, "p0t_sha256": "0" * 64,
    }
    value["p0t_sha256"] = self_digest("c5k4-method-v1.5-p0t-1.0", value, "p0t_sha256")
    validate_schema(value, P0T_SCHEMA)
    return value


def build_a0_draft(repo: Path, p0t_commit: str, receipt: dict[str, Any], *, observation_verifier: Any = _replay_observation) -> dict[str, Any]:
    exact_commit(repo, p0t_commit)
    raw = commit_bytes(repo, p0t_commit, P0T_PATH)
    p0t = json.loads(raw, object_pairs_hook=_pairs)
    validate_schema(p0t, P0T_SCHEMA)
    p0a_raw = commit_bytes(repo, p0t["p0a"]["commit"], P0A_PATH)
    p0a = strict_json_bytes(p0a_raw, "P0A")
    component_index = {row["path"]: row for row in p0a["components"]}
    ami_components = [component_index[path] for path in AMI_POLICY_COMPONENTS]
    validate_receipt(repo, receipt, "P0T", p0t_commit, P0T_PATH, raw)
    observation_verifier(repo, receipt, "P0T", p0t_commit)
    p0a_run = p0t["p0a_publication_receipt"]["actions_run"]
    p0t_run = receipt["actions_run"]
    p0a_completed = datetime.fromisoformat(p0a_run["updated_at_utc"].replace("Z", "+00:00"))
    p0t_created = datetime.fromisoformat(p0t_run["created_at_utc"].replace("Z", "+00:00"))
    if p0a_run["run_id"] == p0t_run["run_id"] or not p0a_completed < p0t_created:
        raise ChainError("P0A and P0T require distinct sequential pushes and Actions runs")
    value: dict[str, Any] = {
        "schema": "c5k4-method-v1.5-a0-1.0", "artifact_kind": "A0",
        "status": "NONAUTHORITATIVE_DRAFT_AWAITING_EXTERNAL_NITROTPM_KEY_AND_SIGNATURES",
        "protocol_version": "1.5", "target_specific": False,
        "p0t": {"path": P0T_PATH, "commit": p0t_commit, "sha256": hashlib.sha256(raw).hexdigest(), "canonical_sha256": p0t["p0t_sha256"]},
        "p0t_publication_receipt": receipt,
        "a0_authorized_at_utc": None,
        "ami_authority_binding_contract": {
            "policy_template_sha256": p0a["authority_policy"]["attestable_ami_authority_binding_policy_sha256"],
            "components": ami_components,
            "future_live_binding_sha256": None,
        },
        "external_harness_authority": None, "independent_authority_signatures": [],
        "activation_policy": {
            "activation_authority": False, "fail_closed": True,
            "nitrotpm_sealed_verification_key_hash_present": False,
            "required_independent_signatures_present": False,
            "external_activation_ceremony_required": True,
            "repository_builder_can_activate": False,
            "local_preview_only": True, "publication_permitted": False,
        },
        "topology_policy": {"parent_must_be_exact_p0t": True, "allowed_changed_paths": [A0_PATH]},
        "a0_payload_sha256": "0" * 64, "a0_sha256": "0" * 64,
    }
    payload = {k: v for k, v in value.items() if k not in {"a0_payload_sha256", "a0_sha256", "independent_authority_signatures"}}
    value["a0_payload_sha256"] = domain_digest("c5k4-method-v1.5-a0-activation-payload-1.0", payload)
    value["a0_sha256"] = self_digest("c5k4-method-v1.5-a0-1.0", value, "a0_sha256")
    validate_schema(value, A0_SCHEMA)
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)
    p0a = sub.add_parser("p0a"); p0a.add_argument("--base-commit", required=True); p0a.add_argument("--components", type=Path, required=True); p0a.add_argument("--authority-policy", type=Path, required=True); p0a.add_argument("--output", type=Path, required=True)
    p0t = sub.add_parser("p0t"); p0t.add_argument("--p0a-commit", required=True); p0t.add_argument("--actions-receipt", type=Path, required=True); p0t.add_argument("--output", type=Path, required=True)
    a0 = sub.add_parser("a0-draft"); a0.add_argument("--p0t-commit", required=True); a0.add_argument("--actions-receipt", type=Path, required=True); a0.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "p0a":
            value = build_p0a(args.repo, args.base_commit, load_json(args.components), load_json(args.authority_policy))
        elif args.command == "p0t":
            value = build_p0t(args.repo, args.p0a_commit, load_json(args.actions_receipt))
        else:
            value = build_a0_draft(args.repo, args.p0t_commit, load_json(args.actions_receipt))
        write_json(args.output, value)
    except (ChainError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
