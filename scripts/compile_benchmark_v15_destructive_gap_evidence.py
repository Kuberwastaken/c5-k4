#!/usr/bin/env python3
"""Verify signed target-blind gap evidence and compile one bounded acceptance.

This pure compiler performs no gap test, target access, service control, or
external call.  Operational acceptance is possible only for six authentic
LIVE_CONTROLLED_HARNESS records under the P1-committed Ed25519 key.  Signed
fixture records compile only to an explicitly nonoperational receipt.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA = ROOT / "schemas/benchmark-destructive-gap-evidence-bundle-v1.5.schema.json"
OUTPUT_SCHEMA = ROOT / "schemas/benchmark-operational-destructive-gap-acceptance-v1.5.schema.json"
TESTS = ("DESTRUCTIVE_WRITE", "TRUNCATION", "SERVICE_RESTART", "OFFLINE_GAP", "SEQUENCE_CONFLICT", "UNEXPECTED_INGRESS")
FORBIDDEN_KEYS = frozenset({"candidate", "candidate_id", "cluster", "cluster_id", "conjecture", "declaration", "statement", "statement_text", "target", "target_id", "theorem", "semantic_text", "score", "ranking"})
ZERO = "0" * 64


class GapEvidenceError(ValueError):
    """Signed destructive-gap evidence is absent, invalid, or incomplete."""


class SilentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise GapEvidenceError(f"argument contract rejected: {message}")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest_object(value: Mapping[str, Any], *excluded: str) -> str:
    body = {key: item for key, item in value.items() if key not in set(excluded)}
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GapEvidenceError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GapEvidenceError(f"{path}: expected one JSON object")
    return value


def validate_schema(value: object, path: Path, label: str) -> None:
    schema = load_object(path)
    errors = sorted(Draft7Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        location = ".".join(str(item) for item in errors[0].absolute_path) or "$"
        raise GapEvidenceError(f"{label} schema failure at {location}: {errors[0].message}")


def reject_target_fields(value: object, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower().replace("-", "_") in FORBIDDEN_KEYS:
                raise GapEvidenceError(f"target-bearing field forbidden: {'/'.join(path + (key,))}")
            reject_target_fields(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_target_fields(child, path + (str(index),))


def verify_key(verification_key: bytes, commitment: dict[str, Any]) -> Ed25519PublicKey:
    if len(verification_key) != 32:
        raise GapEvidenceError("verification key is not exactly 32 raw Ed25519 bytes")
    if hashlib.sha256(verification_key).hexdigest() != commitment["verification_key_sha256"]:
        raise GapEvidenceError("verification key does not match the P1 commitment")
    if commitment["commitment_sha256"] != digest_object(commitment, "commitment_sha256"):
        raise GapEvidenceError("P1 key commitment self-digest mismatch")
    try:
        return Ed25519PublicKey.from_public_bytes(verification_key)
    except ValueError as exc:
        raise GapEvidenceError("verification key is malformed") from exc


def verify_row(
    row: dict[str, Any], key: Ed25519PublicKey, *, plan_sha256: str,
    epoch_sha256: str, signing_key_id: str, verification_key_sha256: str,
) -> None:
    if row["committed_plan_sha256"] != plan_sha256:
        raise GapEvidenceError(f"{row['test']} does not bind the committed gap plan")
    if row["service_epoch_binding_sha256"] != epoch_sha256:
        raise GapEvidenceError(f"{row['test']} does not bind the service epoch")
    if row["signing_key_id"] != signing_key_id or row["verification_key_sha256"] != verification_key_sha256:
        raise GapEvidenceError(f"{row['test']} does not bind the committed signing key")
    actual = digest_object(row, "evidence_sha256", "signature")
    if row["evidence_sha256"] != actual:
        raise GapEvidenceError(f"{row['test']} evidence self-digest mismatch")
    try:
        signature = base64.b64decode(row["signature"], validate=True)
        key.verify(signature, bytes.fromhex(actual))
    except (ValueError, InvalidSignature) as exc:
        raise GapEvidenceError(f"{row['test']} signature mismatch") from exc


def compile_evidence(bundle: dict[str, Any], verification_key: bytes) -> dict[str, Any]:
    validate_schema(bundle, INPUT_SCHEMA, "gap evidence bundle")
    reject_target_fields(bundle)
    if bundle["bundle_sha256"] != digest_object(bundle, "bundle_sha256"):
        raise GapEvidenceError("gap evidence bundle self-digest mismatch")
    commitment = bundle["key_commitment"]
    key = verify_key(verification_key, commitment)
    expected_context = "LIVE_CONTROLLED_HARNESS" if bundle["status"] == "LIVE_CONTROLLED_HARNESS_EVIDENCE" else "FIXTURE_NONOPERATIONAL"
    for row in bundle["evidence"]:
        if row["execution_context"] != expected_context:
            raise GapEvidenceError("bundle status and evidence execution context disagree")
        verify_row(
            row, key, plan_sha256=bundle["committed_plan_sha256"],
            epoch_sha256=bundle["service_epoch_binding_sha256"],
            signing_key_id=commitment["signing_key_id"],
            verification_key_sha256=commitment["verification_key_sha256"],
        )
    if len({row["evidence_sha256"] for row in bundle["evidence"]}) != len(TESTS):
        raise GapEvidenceError("evidence record replay detected")
    if len({row["request_sha256"] for row in bundle["evidence"]}) != len(TESTS):
        raise GapEvidenceError("gap request replay detected")
    if len({row["result_sha256"] for row in bundle["evidence"]}) != len(TESTS):
        raise GapEvidenceError("gap result replay detected")

    all_passed = all(row["passed"] for row in bundle["evidence"])
    live = expected_context == "LIVE_CONTROLLED_HARNESS"
    if live and not all_passed:
        raise GapEvidenceError("live destructive-gap closure contains a failed test")
    output = {
        "schema": "c5k4-method-v1.5-operational-destructive-gap-acceptance-1.0",
        "status": "OPERATIONAL_DESTRUCTIVE_GAP_ACCEPTANCE_PASSED" if live else "FIXTURE_DESTRUCTIVE_GAP_EVIDENCE_VERIFIED_NONOPERATIONAL",
        "committed_plan_sha256": bundle["committed_plan_sha256"],
        "service_epoch_binding_sha256": bundle["service_epoch_binding_sha256"],
        "signing_key_id": commitment["signing_key_id"],
        "verification_key_sha256": commitment["verification_key_sha256"],
        "evidence_bundle_sha256": bundle["bundle_sha256"],
        "tests": list(TESTS),
        "evidence_sha256": {row["test"]: row["evidence_sha256"] for row in bundle["evidence"]},
        "all_passed": all_passed,
        "operational": live,
        "activation_permitted": live,
        "acceptance_sha256": ZERO,
    }
    output["acceptance_sha256"] = digest_object(output, "acceptance_sha256")
    validate_schema(output, OUTPUT_SCHEMA, "gap acceptance")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = SilentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--verification-key", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        output = compile_evidence(load_object(args.evidence), args.verification_key.read_bytes())
        print(canonical_bytes(output).decode() + "\n", end="")
    except (GapEvidenceError, OSError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
