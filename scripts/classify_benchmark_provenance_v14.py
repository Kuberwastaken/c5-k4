#!/usr/bin/env python3
"""Fail-closed Method v1.4 provenance and identity-decision prototype.

The classifier uses structural provenance only.  It does not inspect target
statements or infer mathematical meaning.  Every input unit receives exactly
one of SEMANTIC_SOURCE, MACHINE_REGISTRY_CONTACT, or UNKNOWN.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


SEMANTIC_SOURCE = "SEMANTIC_SOURCE"
MACHINE_REGISTRY_CONTACT = "MACHINE_REGISTRY_CONTACT"
UNKNOWN = "UNKNOWN"
CLASSES = {SEMANTIC_SOURCE, MACHINE_REGISTRY_CONTACT, UNKNOWN}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unit_identity_sha256(unit: dict[str, Any]) -> str:
    return sha256(canonical_json({
        "source_id": unit.get("source_id"),
        "locator": unit.get("locator"),
        "role": unit.get("role"),
        "content_sha256": unit.get("content_sha256"),
    }))


def load_policy(path: Path) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("unit_classes") != [SEMANTIC_SOURCE, MACHINE_REGISTRY_CONTACT, UNKNOWN]:
        raise ValueError("policy must define the three Method v1.4 unit classes")
    return policy


def _result(unit: dict[str, Any], provenance_class: str, reason: str) -> dict[str, Any]:
    assert provenance_class in CLASSES
    return {
        "source_id": unit.get("source_id"),
        "source_kind": unit.get("source_kind"),
        "locator": unit.get("locator"),
        "role": unit.get("role"),
        "content_sha256": unit.get("content_sha256"),
        "content_schema": unit.get("content_schema"),
        "unit_identity_sha256": unit_identity_sha256(unit),
        "provenance_class": provenance_class,
        "classification_reason": reason,
    }


def _valid_core(unit: dict[str, Any]) -> bool:
    strings = ("source_id", "source_kind", "locator", "role", "content_sha256")
    return (
        all(isinstance(unit.get(key), str) and unit[key] for key in strings)
        and len(unit["content_sha256"]) == 64
        and all(char in "0123456789abcdef" for char in unit["content_sha256"])
    )


def _locator_allowed(role: str, locator: str, policy: dict[str, Any]) -> bool:
    prefixes = policy["immutable_locator_prefixes"].get(role, [])
    return any(locator.startswith(prefix) for prefix in prefixes)


def _matching_exemption(
    unit: dict[str, Any], exemption: dict[str, Any] | None, policy: dict[str, Any]
) -> bool:
    if not isinstance(exemption, dict):
        return False
    required = policy["machine_exemption_required_fields"]
    if any(field not in exemption for field in required):
        return False
    if any(exemption.get(field) is not True for field in policy["machine_exemption_required_true"]):
        return False
    for field in ("source_id", "source_kind", "locator", "role", "content_sha256", "content_schema"):
        if exemption.get(field) != unit.get(field):
            return False
    expected_identity = unit_identity_sha256(unit)
    return exemption.get("unit_identity_sha256") == expected_identity


def classify_unit(
    unit: dict[str, Any],
    verified_exemption: dict[str, Any] | None,
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Classify one indivisible scan unit without inspecting target semantics."""

    if not isinstance(unit, dict) or not _valid_core(unit):
        return _result(unit if isinstance(unit, dict) else {}, UNKNOWN, "MALFORMED_UNIT_RECORD")
    if unit.get("mixed") is True or unit.get("malformed") is True:
        return _result(unit, UNKNOWN, "MIXED_OR_MALFORMED_UNIT")

    role = unit["role"]
    if role in policy["semantic_roles"]:
        return _result(unit, SEMANTIC_SOURCE, "SEMANTIC_ROLE")

    if role in policy["unknown_roles"]:
        return _result(unit, UNKNOWN, "METADATA_OR_UNVERIFIED_ROLE")

    if role not in policy["machine_roles"]:
        return _result(unit, UNKNOWN, "UNRECOGNIZED_ROLE")
    if unit["source_kind"] not in policy["machine_source_kinds"].get(role, []):
        return _result(unit, UNKNOWN, "ROLE_INCOMPATIBLE_SOURCE_KIND")
    schema = unit.get("content_schema")
    if schema not in policy["bounded_content_schemas"]:
        return _result(unit, UNKNOWN, "UNBOUNDED_CONTENT_SCHEMA")
    if not _locator_allowed(role, unit["locator"], policy):
        return _result(unit, UNKNOWN, "MUTABLE_OR_ROLE_INCOMPATIBLE_LOCATOR")
    if not _matching_exemption(unit, verified_exemption, policy):
        return _result(unit, UNKNOWN, "MISSING_OR_MISMATCHED_PROVENANCE_EXEMPTION")
    return _result(unit, MACHINE_REGISTRY_CONTACT, "VERIFIED_BOUNDED_GENERATED_OUTPUT")


def exemption_index(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index records by full unit identity, rejecting ambiguous duplicate proofs."""

    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        identity = record.get("unit_identity_sha256")
        if not isinstance(identity, str) or len(identity) != 64:
            continue
        if identity in indexed and indexed[identity] != record:
            raise ValueError(f"conflicting provenance exemptions for {identity}")
        indexed[identity] = record
    return indexed


def classify_units(
    units: Iterable[dict[str, Any]],
    exemptions: Iterable[dict[str, Any]],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    indexed = exemption_index(exemptions)
    return [classify_unit(unit, indexed.get(unit_identity_sha256(unit)), policy) for unit in units]


def alias_can_identify(alias: dict[str, Any], policy: dict[str, Any]) -> bool:
    """Return whether a syntactic alias hit is sufficiently anchored to count."""

    if not isinstance(alias, dict) or alias.get("matched") is not True:
        return False
    kind = alias.get("alias_kind")
    if kind in {"FULL_PATH", "MODULE_PATH", "DECLARATION_ID"}:
        return True
    required = policy["identity_policy"]["namespace_anchor_required_alias_kinds"]
    if kind in required:
        anchor = alias.get("namespace_anchor")
        return isinstance(anchor, str) and bool(anchor.strip())
    return False


def identity_decision(
    provenance_class: str,
    aliases: Iterable[dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Apply the exclusion rule after provenance and alias matching are frozen."""

    if provenance_class not in CLASSES:
        raise ValueError("invalid provenance class")
    identifying = [alias for alias in aliases if alias_can_identify(alias, policy)]
    hit = bool(identifying)
    excludes = hit and provenance_class in policy["identity_policy"]["excluding_unit_classes"]
    return {
        "identity_hit": hit,
        "identifying_alias_sha256s": sorted(
            sha256(canonical_json(alias)) for alias in identifying
        ),
        "excludes_cluster": excludes,
        "reason": (
            "IDENTITY_IN_SEMANTIC_OR_UNKNOWN_UNIT"
            if excludes
            else "IDENTITY_CONFINED_TO_MACHINE_REGISTRY_CONTACT"
            if hit
            else "NO_ANCHORED_IDENTITY_HIT"
        ),
    }
