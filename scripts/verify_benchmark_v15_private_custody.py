#!/usr/bin/env python3
"""Verify PRE-P1 private custody chains without inspecting target semantics.

This is a protocol-contract verifier, not a capture daemon.  It accepts only
closed metadata schemas, verifies Ed25519 signatures and hash/sequence chains,
checks content-addressed payload bytes, and emits a target-blind private
coverage certificate plus a public sealed binding.  It does not provision
keys, repositories, retention, capture, or sealing infrastructure.
"""

from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import jsonschema
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


ROOT = Path(__file__).resolve().parents[1]
MAX_SEQUENCE = 9223372036854775807
BATCH_SCHEMA = "c5k4-method-v1.5-private-custody-batch-1.0"
COVERAGE_SCHEMA = "c5k4-method-v1.5-private-custody-coverage-certificate-1.0"
BINDING_SCHEMA = "c5k4-method-v1.5-public-custody-sealed-binding-1.0"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
PRIVATE_ONLY_KEYS = {
    "host_id", "signing_key_id", "signature", "boot_id", "records",
    "payload_sha256", "payload_byte_count", "delivery_channel",
    "observed_at_utc", "receipt_sha256", "previous_receipt_sha256",
}


class CustodyError(ValueError):
    """Fail-closed custody contract violation."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise CustodyError(f"invalid UTC timestamp: {value!r}") from exc
    return parsed


def load_schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def validate_schema(value: object, name: str) -> None:
    try:
        jsonschema.Draft7Validator(load_schema(name), format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.ValidationError as exc:
        raise CustodyError(f"{name} validation failed: {exc.message}") from exc


def _without(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in keys}


def record_digest(record: dict[str, Any]) -> str:
    return digest(_without(record, "receipt_sha256"))


def batch_digest(batch: dict[str, Any]) -> str:
    return digest(_without(batch, "batch_sha256", "signature"))


def certificate_digest(certificate: dict[str, Any]) -> str:
    return digest(_without(certificate, "certificate_sha256"))


def binding_digest(binding: dict[str, Any]) -> str:
    return digest(_without(binding, "binding_sha256"))


def _verify_signature(batch: dict[str, Any], public_key: bytes) -> None:
    try:
        signature = base64.b64decode(batch["signature"], validate=True)
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature, bytes.fromhex(batch["batch_sha256"])
        )
    except Exception as exc:
        raise CustodyError("batch signature does not verify") from exc


def _verify_host_chain(
    host_id: str,
    batches: list[dict[str, Any]],
    public_key: bytes,
    blobs: dict[str, bytes],
    required_from: datetime,
    required_through: datetime,
) -> dict[str, Any]:
    if not batches:
        raise CustodyError(f"host {host_id} has no custody batches")
    ordered = sorted(batches, key=lambda row: row.get("batch_sequence", -1))
    previous_batch: str | None = None
    previous_receipt: str | None = None
    previous_record_sequence: int | None = None
    previous_time: datetime | None = None
    previous_boot: str | None = None
    maximum_gap = 0
    restart_count = 0
    total_records = 0

    for batch_index, batch in enumerate(ordered):
        validate_schema(batch, "benchmark-private-custody-batch-v1.5.schema.json")
        if batch["host_id"] != host_id:
            raise CustodyError("batch is filed under the wrong host")
        if batch["batch_sequence"] != batch_index:
            raise CustodyError("missing, duplicate, or overflowed batch sequence")
        if batch["previous_batch_sha256"] != previous_batch:
            raise CustodyError("batch chain splice or rewrite detected")
        actual_batch = batch_digest(batch)
        if batch["batch_sha256"] != actual_batch:
            raise CustodyError("batch hash mismatch")
        _verify_signature(batch, public_key)
        records = batch["records"]
        if batch["first_record_sequence"] != records[0]["sequence_number"] or batch["last_record_sequence"] != records[-1]["sequence_number"]:
            raise CustodyError("batch record range disagrees with records")
        if batch["captured_from_utc"] != records[0]["observed_at_utc"] or batch["captured_through_utc"] != records[-1]["observed_at_utc"]:
            raise CustodyError("batch time range disagrees with records")

        for record in records:
            sequence = record["sequence_number"]
            expected = 0 if previous_record_sequence is None else previous_record_sequence + 1
            if previous_record_sequence == MAX_SEQUENCE:
                raise CustodyError("record sequence overflow")
            if sequence != expected:
                raise CustodyError("missing, duplicate, or rewritten record sequence")
            if record["previous_receipt_sha256"] != previous_receipt:
                raise CustodyError("record chain splice or rewrite detected")
            if record["receipt_sha256"] != record_digest(record):
                raise CustodyError("receipt hash mismatch")
            if record["boot_id"] != batch["boot_id"]:
                raise CustodyError("record boot identity disagrees with batch")
            if previous_boot is not None and record["boot_id"] != previous_boot:
                if record["event_kind"] != "RESTART":
                    raise CustodyError("boot changed without an explicit restart record")
                restart_count += 1
            elif record["event_kind"] == "RESTART":
                raise CustodyError("restart record does not change boot identity")

            observed = parse_time(record["observed_at_utc"])
            if previous_time is not None:
                gap = int((observed - previous_time).total_seconds())
                if gap < 0 or gap > 300:
                    raise CustodyError("missing heartbeat or nonmonotonic observation time")
                maximum_gap = max(maximum_gap, gap)
            payload_hash = record["payload_sha256"]
            payload_count = record["payload_byte_count"]
            if record["event_kind"] in {"HEARTBEAT", "RESTART"}:
                if payload_hash != EMPTY_SHA256 or payload_count != 0:
                    raise CustodyError("heartbeat/restart must bind the empty payload")
            else:
                raw = blobs.get(payload_hash)
                if raw is None or hashlib.sha256(raw).hexdigest() != payload_hash or len(raw) != payload_count:
                    raise CustodyError("content-addressed payload blob mismatch or missing blob")

            previous_record_sequence = sequence
            previous_receipt = record["receipt_sha256"]
            previous_time = observed
            previous_boot = record["boot_id"]
            total_records += 1
        previous_batch = actual_batch

    first_time = parse_time(ordered[0]["records"][0]["observed_at_utc"])
    last_time = parse_time(ordered[-1]["records"][-1]["observed_at_utc"])
    if first_time > required_from or last_time < required_through:
        raise CustodyError(f"host {host_id} does not cover the required interval")
    return {
        "host_id": host_id,
        "signing_key_id": ordered[-1]["signing_key_id"],
        "first_batch_sequence": ordered[0]["batch_sequence"],
        "last_batch_sequence": ordered[-1]["batch_sequence"],
        "first_record_sequence": ordered[0]["first_record_sequence"],
        "last_record_sequence": ordered[-1]["last_record_sequence"],
        "first_observed_at_utc": ordered[0]["captured_from_utc"],
        "last_observed_at_utc": ordered[-1]["captured_through_utc"],
        "batch_count": len(ordered),
        "record_count": total_records,
        "last_batch_sha256": previous_batch,
        "last_receipt_sha256": previous_receipt,
        "maximum_observed_gap_seconds": maximum_gap,
        "restart_count": restart_count,
        "chain_complete": True,
    }


def verify_coverage(
    batches: Iterable[dict[str, Any]],
    public_keys: dict[tuple[str, str], bytes],
    blobs: dict[str, bytes],
    required_hosts: list[str],
    required_from_utc: str,
    required_through_utc: str,
) -> dict[str, Any]:
    """Verify all required host chains and return a private certificate."""
    if len(set(required_hosts)) != len(required_hosts) or not required_hosts:
        raise CustodyError("required hosts must be a nonempty unique list")
    required_from = parse_time(required_from_utc)
    required_through = parse_time(required_through_utc)
    if required_from >= required_through:
        raise CustodyError("required custody interval must be nonempty")
    grouped: dict[str, list[dict[str, Any]]] = {host: [] for host in required_hosts}
    for batch in batches:
        if not isinstance(batch, dict) or batch.get("host_id") not in grouped:
            raise CustodyError("unexpected host in custody input")
        grouped[batch["host_id"]].append(batch)
    chains = []
    for host in required_hosts:
        host_batches = grouped[host]
        if not host_batches:
            raise CustodyError(f"required host {host} is absent")
        key_ids = {row.get("signing_key_id") for row in host_batches}
        if len(key_ids) != 1:
            raise CustodyError("signing-key rotation is not specified by the PRE-P1 contract")
        key = public_keys.get((host, next(iter(key_ids))))
        if key is None:
            raise CustodyError("missing pinned host public key")
        chains.append(_verify_host_chain(host, host_batches, key, blobs, required_from, required_through))
    certificate: dict[str, Any] = {
        "schema": COVERAGE_SCHEMA,
        "status": "PRE_P1_VERIFIED_CONTRACT_NOT_OPERATIONAL",
        "protocol_version": "1.5",
        "verification_mode": "TARGET_BLIND_METADATA_ONLY",
        "required_from_utc": required_from_utc,
        "required_through_utc": required_through_utc,
        "maximum_heartbeat_interval_seconds": 300,
        "required_hosts": required_hosts,
        "host_chains": chains,
        "complete": True,
        "gaps": [],
    }
    certificate["certificate_sha256"] = certificate_digest(certificate)
    validate_schema(certificate, "benchmark-private-custody-coverage-certificate-v1.5.schema.json")
    return certificate


def public_sealed_binding(certificate: dict[str, Any], sealed_private_bundle: bytes) -> dict[str, Any]:
    """Bind opaque private bytes without publishing host, record, or payload metadata."""
    validate_schema(certificate, "benchmark-private-custody-coverage-certificate-v1.5.schema.json")
    if certificate_digest(certificate) != certificate["certificate_sha256"]:
        raise CustodyError("coverage certificate hash mismatch")
    binding: dict[str, Any] = {
        "schema": BINDING_SCHEMA,
        "status": "PRE_P1_PUBLIC_BINDING_NOT_OPERATIONAL",
        "protocol_version": "1.5",
        "disclosure": "TARGET_BLIND_HASHES_AND_COVERAGE_ONLY",
        "seal_algorithm": "PRE_P1_OPAQUE_AUTHENTICATED_ENVELOPE",
        "sealed_private_bundle_sha256": hashlib.sha256(sealed_private_bundle).hexdigest(),
        "sealed_private_bundle_byte_count": len(sealed_private_bundle),
        "private_coverage_certificate_sha256": certificate["certificate_sha256"],
        "required_host_count": len(certificate["required_hosts"]),
        "required_from_utc": certificate["required_from_utc"],
        "required_through_utc": certificate["required_through_utc"],
    }
    binding["binding_sha256"] = binding_digest(binding)
    validate_public_binding(binding)
    return binding


def validate_public_binding(binding: dict[str, Any]) -> None:
    validate_schema(binding, "benchmark-public-custody-sealed-binding-v1.5.schema.json")
    if binding_digest(binding) != binding["binding_sha256"]:
        raise CustodyError("public binding hash mismatch")
    stack: list[object] = [binding]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            forbidden = PRIVATE_ONLY_KEYS.intersection(value)
            if forbidden:
                raise CustodyError(f"forbidden private fields in public binding: {sorted(forbidden)}")
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-public-binding", type=Path)
    args = parser.parse_args()
    if args.validate_public_binding is None:
        parser.error("PRE-P1 contract verifier exposes only --validate-public-binding on the CLI; no daemon or operational custody command exists")
    validate_public_binding(json.loads(args.validate_public_binding.read_text(encoding="utf-8")))
    print("PRE_P1_PUBLIC_BINDING_VALID_NOT_OPERATIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
