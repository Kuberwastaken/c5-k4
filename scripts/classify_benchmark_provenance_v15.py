#!/usr/bin/env python3
"""Fail-closed Method v1.5 evidence-unit provenance classifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

import build_benchmark_v15_vendor_bases as vendor


SEMANTIC_EXPOSURE = "SEMANTIC_EXPOSURE"
MACHINE_REGISTRY_CONTACT = "MACHINE_REGISTRY_CONTACT"
IMMUTABLE_SOURCE_CUSTODY = "IMMUTABLE_SOURCE_CUSTODY"
UNKNOWN = "UNKNOWN"
CLASSES = {SEMANTIC_EXPOSURE, MACHINE_REGISTRY_CONTACT, IMMUTABLE_SOURCE_CUSTODY, UNKNOWN}
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
GIT_BLOB_LOCATOR = re.compile(r"git-blob:([0-9a-f]{40}|[0-9a-f]{64}):(.+)")

SEMANTIC_ROLES = {
    "user-turn", "assistant-turn", "human-message", "model-message",
    "repo-prose", "repo-script", "repo-code", "repo-comment", "commit-message",
    "user-commit-message", "user-path-delta", "worktree-overlay",
    "codex-tool-output", "claude-tool-output", "agent-tool-output",
    "custom-tool-output", "interactive-tool-output", "target-specific-compute",
}
MACHINE_ROLE = "machine-generated-git-blob"
CUSTODY_ROLES = {"vendor-base-blob", "vendor-base-tree", "vendor-base-commit"}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unit_identity_sha256(unit: dict[str, Any]) -> str:
    return sha256(canonical_json({
        "source_id": unit.get("source_id"),
        "source_kind": unit.get("source_kind"),
        "locator": unit.get("locator"),
        "role": unit.get("role"),
        "content_sha256": unit.get("content_sha256"),
        "content_schema": unit.get("content_schema"),
    }))


def load_ontology(path: Path) -> dict[str, Any]:
    ontology = json.loads(path.read_text(encoding="utf-8"))
    if set(ontology.get("classes", {})) != CLASSES:
        raise ValueError("ontology must define exactly the four Method v1.5 classes")
    if ontology.get("classification", {}).get("manual_hash_exemptions") is not False:
        raise ValueError("ontology must prohibit manual hash exemptions")
    return ontology


def _valid_core(unit: object) -> bool:
    if not isinstance(unit, dict):
        return False
    strings = ("source_id", "source_kind", "locator", "role", "content_sha256")
    return all(isinstance(unit.get(key), str) and unit[key] for key in strings) and bool(
        HEX_SHA256.fullmatch(unit["content_sha256"])
    )


def _result(unit: object, provenance_class: str, reason: str) -> dict[str, Any]:
    row = unit if isinstance(unit, dict) else {}
    return {
        "source_id": row.get("source_id"), "source_kind": row.get("source_kind"),
        "locator": row.get("locator"), "role": row.get("role"),
        "content_sha256": row.get("content_sha256"), "content_schema": row.get("content_schema"),
        "unit_identity_sha256": unit_identity_sha256(row),
        "provenance_class": provenance_class, "classification_reason": reason,
    }


def _proof_is_locator_bound(unit: dict[str, Any], proof: object) -> bool:
    if not isinstance(proof, dict):
        return False
    exact = ("source_id", "source_kind", "locator", "role", "content_sha256", "content_schema")
    if any(proof.get(key) != unit.get(key) for key in exact):
        return False
    return proof.get("unit_identity_sha256") == unit_identity_sha256(unit)


def _valid_machine_proof(unit: dict[str, Any], proof: object) -> bool:
    if not _proof_is_locator_bound(unit, proof):
        return False
    assert isinstance(proof, dict)
    required_true = (
        "historical_inputs_predate_output", "bounded_safe_surface_verified",
        "deterministic_exact_replay_verified", "locator_specific_proof",
    )
    return (
        proof.get("schema_version") == "c5k4-generated-identity-verification-1.5"
        and proof.get("verification_status") == "VERIFIED"
        and all(proof.get(key) is True for key in required_true)
        and proof.get("global_content_hash_allowlist") is False
        and proof.get("interactive_delivery") is False
    )


def _valid_custody_proof(unit: dict[str, Any], proof: object) -> bool:
    if not isinstance(proof, dict):
        return False
    binding = proof.get("locator_binding")
    receipt = proof.get("vendor_receipt")
    verification = proof.get("verification")
    if not _proof_is_locator_bound(unit, binding):
        return False
    if (
        proof.get("schema") != "c5k4-method-v1.5-git-custody-locator-proof-1.0"
        or proof.get("status") != "VERIFIED_IMMUTABLE_SOURCE_CUSTODY"
        or proof.get("proof_sha256") != sha256(canonical_json({key: value for key, value in proof.items() if key != "proof_sha256"}))
        or not isinstance(receipt, dict)
        or not isinstance(verification, dict)
        or not all(verification.get(key) is True for key in (
            "vendor_receipt_live_replay", "base_commit_and_tree_match",
            "path_and_blob_match", "blob_content_sha256_match",
            "no_semantic_rendering_evidenced",
        ))
    ):
        return False
    try:
        vendor.validate_receipt(receipt)
    except (ValueError, OSError):
        return False
    match = GIT_BLOB_LOCATOR.fullmatch(unit["locator"])
    if match is None:
        return False
    blob, path = match.groups()
    audit = receipt.get("audit", {})
    if (
        binding.get("locator_specific") is not True
        or binding.get("git_blob") != blob
        or binding.get("path") != path
        or binding.get("vendor_base_commit") != audit.get("commit")
        or binding.get("vendor_base_tree") != audit.get("root_tree")
        or binding.get("acquisition_receipt_sha256") != receipt.get("receipt_sha256")
    ):
        return False
    try:
        raw = vendor.git(Path(receipt["repository_path"]), "ls-tree", "-z", audit["commit"], "--", path).stdout
        records = [record for record in raw.split(b"\0") if record]
        if len(records) != 1:
            return False
        metadata, path_raw = records[0].split(b"\t", 1)
        _mode, kind, tree_blob = metadata.decode("ascii").split(" ")
        if kind != "blob" or tree_blob != blob or path_raw.decode("utf-8", "surrogateescape") != path:
            return False
        content = vendor.git(Path(receipt["repository_path"]), "cat-file", "blob", blob).stdout
    except (KeyError, OSError, UnicodeError, ValueError, subprocess.CalledProcessError):
        return False
    return sha256(content) == unit["content_sha256"]


def classify_unit(
    unit: dict[str, Any], verified_proof: dict[str, Any] | None,
    ontology: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assign exactly one class without target-dependent reclassification."""

    del ontology  # Ontology bytes are frozen/bound externally; rules are executable here.
    if not _valid_core(unit):
        return _result(unit, UNKNOWN, "MALFORMED_UNIT_RECORD")
    if unit.get("mixed") is True or unit.get("malformed") is True:
        return _result(unit, UNKNOWN, "MIXED_OR_MALFORMED_UNIT")
    role = unit["role"]
    if role in SEMANTIC_ROLES:
        reason = "INTERACTIVE_OR_TOOL_OUTPUT_IS_SEMANTIC" if "tool-output" in role else "SEMANTIC_DELIVERY_ROLE"
        return _result(unit, SEMANTIC_EXPOSURE, reason)
    if role == MACHINE_ROLE:
        if unit["source_kind"] != "git" or not GIT_BLOB_LOCATOR.fullmatch(unit["locator"]):
            return _result(unit, UNKNOWN, "MACHINE_ROLE_WITHOUT_IMMUTABLE_GIT_BLOB_LOCATOR")
        if not _valid_machine_proof(unit, verified_proof):
            return _result(unit, UNKNOWN, "MISSING_OR_MISMATCHED_LOCATOR_SPECIFIC_REPLAY_PROOF")
        return _result(unit, MACHINE_REGISTRY_CONTACT, "VERIFIED_HISTORICAL_EXACT_REPLAY")
    if role in CUSTODY_ROLES:
        if unit["source_kind"] not in {"git_vendor", "git", "git_provenance_partition"}:
            return _result(unit, UNKNOWN, "CUSTODY_ROLE_WITH_INCOMPATIBLE_SOURCE")
        if role == "vendor-base-blob" and not GIT_BLOB_LOCATOR.fullmatch(unit["locator"]):
            return _result(unit, UNKNOWN, "CUSTODY_BLOB_WITHOUT_IMMUTABLE_LOCATOR")
        if not _valid_custody_proof(unit, verified_proof):
            return _result(unit, UNKNOWN, "MISSING_OR_MISMATCHED_CUSTODY_PROOF")
        return _result(unit, IMMUTABLE_SOURCE_CUSTODY, "VERIFIED_IMMUTABLE_VENDOR_CUSTODY")
    return _result(unit, UNKNOWN, "UNRECOGNIZED_OR_UNVERIFIED_ROLE")


def proof_index(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        identity = record.get("unit_identity_sha256")
        if not isinstance(identity, str) and isinstance(record.get("locator_binding"), dict):
            identity = record["locator_binding"].get("unit_identity_sha256")
        if not isinstance(identity, str) or not HEX_SHA256.fullmatch(identity):
            continue
        if identity in indexed and indexed[identity] != record:
            raise ValueError(f"conflicting provenance proofs for {identity}")
        indexed[identity] = record
    return indexed


def classify_units(
    units: Iterable[dict[str, Any]], proofs: Iterable[dict[str, Any]],
    ontology: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    indexed = proof_index(proofs)
    return [classify_unit(unit, indexed.get(unit_identity_sha256(unit)), ontology) for unit in units]


def cluster_excluded(classifications: Iterable[dict[str, Any]]) -> bool:
    return any(row.get("provenance_class") in {SEMANTIC_EXPOSURE, UNKNOWN} for row in classifications)
