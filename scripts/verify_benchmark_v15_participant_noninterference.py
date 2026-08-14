#!/usr/bin/env python3
"""Verify the inert, target-blind Method v1.5 participant boundary artifacts."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "results" / "benchmark" / "v1.5-protocol"
SCHEMAS = ROOT / "schemas"
FORBIDDEN_KEYS = {
    "candidate", "candidate_id", "cluster", "cluster_id", "conjecture",
    "declaration", "statement", "statement_text", "target", "target_id",
    "theorem", "result", "outcome", "ranking", "score",
}


class BoundaryError(ValueError):
    """The participant/noninterference boundary is not exactly the frozen contract."""


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BoundaryError(f"{path}: expected one JSON object")
    return value


def canonical_digest(value: dict[str, Any], digest_field: str) -> str:
    body = copy.deepcopy(value)
    body.pop(digest_field, None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_schema(value: dict[str, Any], schema_name: str) -> None:
    schema = load_object(SCHEMAS / schema_name)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = "/".join(str(item) for item in error.path) or "<root>"
        raise BoundaryError(f"schema failure at {location}: {error.message}")


def reject_target_material(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise BoundaryError(f"target/result-bearing field forbidden: {'/'.join(path + (key,))}")
            reject_target_material(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_target_material(child, path + (str(index),))


def verify_scope_contract(ledger: dict[str, Any]) -> None:
    """Require a phase-invariant scope; runtime facts belong in signed evidence."""
    validate_schema(ledger, "benchmark-participant-ledger-v1.5.schema.json")
    contract = ledger["contract"]
    if (
        contract["phase_invariant"] is not True
        or contract["runtime_state_asserted"] is not False
        or contract["operational_evidence_authority"]
        != "SIGNED_DEPLOYMENT_AND_NONINTERFERENCE_EVIDENCE"
    ):
        raise BoundaryError("participant ledger is not a phase-invariant scope contract")


def verify(ledger: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    verify_scope_contract(ledger)
    validate_schema(receipt, "benchmark-noninterference-receipt-v1.5.schema.json")
    reject_target_material(ledger)
    reject_target_material(receipt)

    ledger_digest = canonical_digest(ledger, "ledger_sha256")
    if ledger["ledger_sha256"] != ledger_digest:
        raise BoundaryError("participant ledger self-digest mismatch")
    if receipt["participant_ledger_sha256"] != ledger_digest:
        raise BoundaryError("noninterference receipt does not bind participant ledger")
    receipt_digest = canonical_digest(receipt, "receipt_sha256")
    if receipt["receipt_sha256"] != receipt_digest:
        raise BoundaryError("noninterference receipt self-digest mismatch")

    if ledger["model_endpoints"]:
        raise BoundaryError("pre-C1 controlled harness cannot contain a model endpoint")
    for field in ("source_boundary_sha256", "signing_key_id", "service_epoch_binding_sha256"):
        if receipt[field] is not None:
            raise BoundaryError(f"PRE-P1 receipt cannot claim frozen {field}")
    if receipt["unjournaled_delivery_detected"]:
        raise BoundaryError("unjournaled delivery invalidates the controlled harness")
    if receipt["scope_complete"] or receipt["operational_ready"] or receipt["activation_permitted"]:
        raise BoundaryError("PRE-P1 receipt cannot authorize activation")
    if any(receipt["proofs"].values()):
        raise BoundaryError("inert receipt cannot claim an operational proof")
    return {
        "valid": True,
        "status": "PRE_P1_NONINTERFERENCE_NOT_OPERATIONAL",
        "activation_permitted": False,
        "participant_ledger_sha256": ledger_digest,
        "noninterference_receipt_sha256": receipt_digest,
    }


def operational_receipt_digest(receipt: dict[str, Any]) -> str:
    unsigned = copy.deepcopy(receipt)
    unsigned.pop("receipt_sha256", None)
    unsigned.pop("signature", None)
    encoded = json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def verify_operational(
    ledger: dict[str, Any],
    expected_source_boundary_sha256: str,
    receipt: dict[str, Any],
    verification_key: bytes,
) -> dict[str, Any]:
    """Verify a future operational receipt; no such artifact exists pre-P1."""
    verify_scope_contract(ledger)
    validate_schema(receipt, "benchmark-operational-noninterference-receipt-v1.5.schema.json")
    reject_target_material(ledger)
    reject_target_material(receipt)
    ledger_digest = canonical_digest(ledger, "ledger_sha256")
    if ledger["ledger_sha256"] != ledger_digest:
        raise BoundaryError("participant ledger self-digest mismatch")
    if receipt["participant_ledger_sha256"] != ledger_digest:
        raise BoundaryError("operational receipt participant-ledger binding mismatch")
    if receipt["source_boundary_sha256"] != expected_source_boundary_sha256:
        raise BoundaryError("operational receipt source-boundary binding mismatch")
    if hashlib.sha256(verification_key).hexdigest() != receipt["verification_key_sha256"]:
        raise BoundaryError("operational receipt verification-key binding mismatch")
    actual = operational_receipt_digest(receipt)
    if receipt["receipt_sha256"] != actual:
        raise BoundaryError("operational receipt self-digest mismatch")
    try:
        signature = base64.b64decode(receipt["signature"], validate=True)
        Ed25519PublicKey.from_public_bytes(verification_key).verify(signature, bytes.fromhex(actual))
    except (ValueError, InvalidSignature) as exc:
        raise BoundaryError("operational receipt signature mismatch") from exc
    return {
        "valid": True,
        "status": receipt["status"],
        "activation_permitted": True,
        "participant_ledger_sha256": ledger_digest,
        "source_boundary_sha256": expected_source_boundary_sha256,
        "noninterference_receipt_sha256": actual,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=PROTOCOL / "participant-ledger.json")
    parser.add_argument("--receipt", type=Path, default=PROTOCOL / "noninterference-receipt.json")
    args = parser.parse_args(argv)
    try:
        verify(load_object(args.ledger), load_object(args.receipt))
    except (BoundaryError, OSError, json.JSONDecodeError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
