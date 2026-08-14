#!/usr/bin/env python3
"""Fail-closed PRE-P1 validator for the Method v1.5 arm envelope.

This validates only the target-free capability policy and the shape/invariants
of a future post-C1 run freeze.  It does not authenticate Git ancestry, claim
an execution nonce, launch a target process, or reveal arm results.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
RESULT_ROLES = ("CATALOGUE_RESULT", "GENERIC_RESULT", "WALL_NAVIGATION_RESULT")
CONTRACT_ROLES = {
    "CATALOGUE": "CATALOGUE_CONTRACT",
    "GENERIC": "GENERIC_CONTRACT",
    "WALL_NAVIGATION": "WALL_CONTRACT",
}
RESULT_ROLE_FOR_ARM = {
    "CATALOGUE": "CATALOGUE_RESULT",
    "GENERIC": "GENERIC_RESULT",
    "WALL_NAVIGATION": "WALL_NAVIGATION_RESULT",
}
TARGET_BEARING_KEYS = {
    "cluster_id", "statement", "statement_text", "declarations", "target_identity",
    "target_semantics", "outcome", "outcomes", "residual", "proof_route", "candidate",
    "candidates", "parameter_grid", "transformation_id", "seed",
}


class EnvelopeError(ValueError):
    """The capability matrix or execution envelope fails closed."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def content_digest(value: dict[str, Any], digest_key: str) -> str:
    return hashlib.sha256(canonical_json({key: item for key, item in value.items() if key != digest_key})).hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EnvelopeError(f"cannot load {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise EnvelopeError(f"{label} must be an object")
    return value


def validate_schema(value: object, schema_name: str, label: str) -> None:
    schema = load_json(ROOT / "schemas" / schema_name, f"{label} schema")
    validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        raise EnvelopeError(f"{label} schema failure at {location}: {error.message}")


def parse_time(value: str, label: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise EnvelopeError(f"{label} is not an exact UTC timestamp") from exc
    return parsed


def _target_key_hits(value: object, location: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key in TARGET_BEARING_KEYS:
                hits.append(child_location)
            hits.extend(_target_key_hits(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(_target_key_hits(child, f"{location}[{index}]"))
    return hits


def validate_matrix(matrix: dict[str, Any]) -> None:
    validate_schema(matrix, "benchmark-arm-capability-matrix-v1.5.schema.json", "capability matrix")
    if matrix["matrix_sha256"] != content_digest(matrix, "matrix_sha256"):
        raise EnvelopeError("capability matrix self-digest mismatch")
    hits = _target_key_hits(matrix)
    if hits:
        raise EnvelopeError(f"PRE-P1 capability matrix contains target-specific fields: {hits}")
    roles = matrix["root_roles"]
    if len(roles) != len(set(roles)):
        raise EnvelopeError("capability matrix root roles are not unique")
    role_set = set(roles)
    if tuple(matrix["all_result_root_roles"]) != RESULT_ROLES:
        raise EnvelopeError("capability matrix result-role order differs from the frozen order")
    for arm in ARMS:
        policy = matrix["capabilities"][arm]
        allowed = policy["allowed_root_roles"]
        forbidden = policy["forbidden_root_roles"]
        if len(allowed) != len(set(allowed)) or len(forbidden) != len(set(forbidden)):
            raise EnvelopeError(f"{arm} capability roles are not unique")
        if set(allowed) & set(forbidden):
            raise EnvelopeError(f"{arm} has a root that is both allowed and forbidden")
        if set(allowed) | set(forbidden) != role_set:
            raise EnvelopeError(f"{arm} capability partition is not exhaustive")
        if set(RESULT_ROLES) - set(forbidden):
            raise EnvelopeError(f"{arm} permits a discovery result as an input")
    wall_only = {
        "WALL_ANALYSIS", "WALL_EFFECT_FORECAST", "WALL_TRANSFORMATION_AND_GRID",
        "WALL_CONTRACT", "WALL_SEED",
    }
    for arm in ("CATALOGUE", "GENERIC"):
        if wall_only & set(matrix["capabilities"][arm]["allowed_root_roles"]):
            raise EnvelopeError(f"{arm} receives wall-analysis capabilities")


def _lexical(path: str, label: str, *, absolute: bool) -> PurePosixPath:
    value = PurePosixPath(path)
    if absolute != value.is_absolute() or ".." in value.parts or "." in value.parts:
        kind = "absolute" if absolute else "repository-relative or private locator"
        raise EnvelopeError(f"{label} must be a normalized {kind} path")
    return value


def _contains(parent: PurePosixPath, child: PurePosixPath) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_target_execution(envelope: dict[str, Any], matrix: dict[str, Any]) -> None:
    target = envelope["target_execution"]
    if not isinstance(target, dict):
        raise EnvelopeError("post-C1 envelope lacks target execution data")
    roots = target["digest_roots"]
    by_role: dict[str, dict[str, Any]] = {}
    seen_paths: set[str] = set()
    for index, root in enumerate(roots):
        role = root["root_role"]
        if role in by_role:
            raise EnvelopeError(f"duplicate digest root role: {role}")
        if root["path"] in seen_paths:
            raise EnvelopeError("two digest roles alias the same path")
        _lexical(root["path"], f"digest_roots[{index}].path", absolute=root["path"].startswith("/"))
        by_role[role] = root
        seen_paths.add(root["path"])
    if set(by_role) != set(matrix["root_roles"]):
        raise EnvelopeError("execution digest roots differ from the capability-matrix closure")
    for role, root in by_role.items():
        expected_access = "PRIVATE_RESULT_OUTPUT" if role in RESULT_ROLES else "READ_ONLY_INPUT"
        if root["access"] != expected_access:
            raise EnvelopeError(f"{role} has the wrong access class")
        if role in RESULT_ROLES and root["sha256"] is not None:
            raise EnvelopeError(f"pre-execution result root {role} already has a digest")

    arms = target["arms"]
    if set(arms) != set(ARMS) or any(arms[arm]["status"] != "PENDING" for arm in ARMS):
        raise EnvelopeError("all-three-arm PENDING barrier is not intact")
    writable: dict[str, PurePosixPath] = {}
    checkout = _lexical(target["campaign_checkout"], "campaign_checkout", absolute=True)
    for arm in ARMS:
        actual = arms[arm]
        policy = matrix["capabilities"][arm]
        if actual["allowed_digest_root_roles"] != policy["allowed_root_roles"]:
            raise EnvelopeError(f"{arm} allowed digest-root closure differs from the frozen matrix")
        if actual["forbidden_digest_root_roles"] != policy["forbidden_root_roles"]:
            raise EnvelopeError(f"{arm} forbidden digest-root closure differs from the frozen matrix")
        if any(role in RESULT_ROLES for role in actual["allowed_digest_root_roles"]):
            raise EnvelopeError(f"{arm} consumes a discovery result")
        contract_root = by_role[CONTRACT_ROLES[arm]]
        if actual["contract"] != {"path": contract_root["path"], "sha256": contract_root["sha256"]}:
            raise EnvelopeError(f"{arm} contract does not match its digest root")
        writable[arm] = _lexical(actual["writable_root"], f"{arm}.writable_root", absolute=True)
        own_result = by_role[RESULT_ROLE_FOR_ARM[arm]]
        if own_result["path"] != actual["writable_root"]:
            raise EnvelopeError(f"{arm} writable root differs from its private result root")
        if _contains(checkout, writable[arm]) or _contains(writable[arm], checkout):
            raise EnvelopeError(f"{arm} writable root overlaps the campaign checkout")
        for root in roots:
            if root["path"].startswith("/"):
                if root["root_role"] == RESULT_ROLE_FOR_ARM[arm]:
                    continue
                digest_path = _lexical(root["path"], f"{root['root_role']}.path", absolute=True)
                if _contains(digest_path, writable[arm]) or _contains(writable[arm], digest_path):
                    raise EnvelopeError(f"{arm} writable root overlaps digest root {root['root_role']}")
    for index, left in enumerate(ARMS):
        for right in ARMS[index + 1:]:
            if _contains(writable[left], writable[right]) or _contains(writable[right], writable[left]):
                raise EnvelopeError(f"writable roots overlap: {left} and {right}")

    precommit = target["baseline_contract_precommit"]
    for arm in ("CATALOGUE", "GENERIC"):
        if precommit[arm] != arms[arm]["contract"]:
            raise EnvelopeError(f"{arm} contract changed after its baseline precommit")
    if parse_time(precommit["recorded_at_utc"], "baseline precommit time") >= parse_time(
        target["wall_analysis_first_delivered_at_utc"], "wall-analysis delivery time"
    ):
        raise EnvelopeError("baseline contract precommit does not precede wall-analysis delivery")

    claim = target["one_shot_claim"]
    if claim != {
        "state": "UNCLAIMED",
        "claim_ref": claim["claim_ref"],
        "claim_nonce_sha256": claim["claim_nonce_sha256"],
        "prior_claims_permitted": False,
        "update_rule": "APPEND_ONLY_ATOMIC_NORMAL_FAST_FORWARD",
    }:
        raise EnvelopeError("one-shot execution claim is not fail-closed")
    reveal = target["reveal"]
    if reveal != {
        "condition": "ALL_THREE_ARMS_TERMINATED",
        "intermediate_logs_permitted": False,
        "intermediate_artifacts_permitted": False,
        "combined_record_only": True,
    }:
        raise EnvelopeError("result reveal is not embargoed until the complete triplet terminates")


def validate_envelope(envelope: dict[str, Any], matrix: dict[str, Any]) -> None:
    validate_matrix(matrix)
    validate_schema(envelope, "benchmark-execution-envelope-v1.5.schema.json", "execution envelope")
    if envelope["envelope_sha256"] != content_digest(envelope, "envelope_sha256"):
        raise EnvelopeError("execution envelope self-digest mismatch")
    matrix_ref = envelope["capability_matrix"]
    if matrix_ref != {
        "path": "results/benchmark/v1.5-protocol/arm-capability-matrix.json",
        "sha256": matrix["matrix_sha256"],
    }:
        raise EnvelopeError("execution envelope does not bind the exact capability matrix")
    if envelope["status"] == "PRE_P1_SCAFFOLD_NOT_EXECUTABLE":
        if envelope["target_specific_fields_present"] is not False or envelope["target_execution"] is not None:
            raise EnvelopeError("PRE-P1 scaffold contains target-specific execution data")
        hits = _target_key_hits(envelope)
        if hits:
            raise EnvelopeError(f"PRE-P1 envelope contains target-specific fields: {hits}")
        return
    _validate_target_execution(envelope, matrix)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--envelope", type=Path, required=True)
    args = parser.parse_args()
    try:
        validate_envelope(load_json(args.envelope, "execution envelope"), load_json(args.matrix, "capability matrix"))
    except EnvelopeError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
