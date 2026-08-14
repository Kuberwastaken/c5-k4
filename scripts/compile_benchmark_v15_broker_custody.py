#!/usr/bin/env python3
"""Compile signed broker/WORM evidence into private custody verifier artifacts.

This PRE-P1 compiler is deliberately a library, not an activation command.  It
reopens every version-pinned receipt and payload through an injected immutable
store reader, verifies the broker chain and finite-state transitions, and emits
only private metadata.  Target bytes are used transiently for CAS verification
and are never returned or serialized by this module.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Iterable

import jsonschema
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

import method_v15_delivery_broker as broker
import verify_benchmark_v15_private_custody as custody


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_SCHEMA = "c5k4-method-v1.5-private-worm-object-inventory-1.0"
OUTPUT_SCHEMA = "c5k4-method-v1.5-private-custody-compiler-output-1.0"
STATUS = "PRE_P1_PRIVATE_CUSTODY_NOT_OPERATIONAL"
MAX_OBJECTS = 200001


class CompilerError(ValueError):
    """A fail-closed broker-to-custody compilation failure."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _without(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in keys}


def _time(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise CompilerError(f"{label} is not a UTC timestamp")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise CompilerError(f"{label} is not a UTC timestamp") from exc


def _schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _validate(value: object, name: str) -> None:
    try:
        jsonschema.Draft7Validator(
            _schema(name), format_checker=jsonschema.FormatChecker()
        ).validate(value)
    except jsonschema.ValidationError as exc:
        raise CompilerError(f"{name} validation failed: {exc.message}") from exc


def _validate_output(value: object) -> None:
    output_schema = _schema("benchmark-private-custody-compiler-output-v1.5.schema.json")
    store = {}
    for name in (
        "benchmark-private-custody-batch-v1.5.schema.json",
        "benchmark-private-custody-coverage-certificate-v1.5.schema.json",
    ):
        dependency = _schema(name)
        store[dependency["$id"]] = dependency
        store[name] = dependency
    resolver = jsonschema.RefResolver.from_schema(output_schema, store=store)
    try:
        jsonschema.Draft7Validator(
            output_schema, resolver=resolver, format_checker=jsonschema.FormatChecker()
        ).validate(value)
    except jsonschema.ValidationError as exc:
        raise CompilerError(f"compiler output validation failed: {exc.message}") from exc


def inventory_digest(inventory: dict[str, Any]) -> str:
    return digest(_without(inventory, "inventory_sha256"))


def output_digest(output: dict[str, Any]) -> str:
    return digest(_without(output, "compiler_output_sha256", "signature"))


def verify_compiler_output(output: dict[str, Any], broker_verification_key: bytes) -> None:
    """Verify the private compiler envelope that binds WORM inventory to custody."""
    _validate_output(output)
    if output_digest(output) != output["compiler_output_sha256"]:
        raise CompilerError("compiler output hash mismatch")
    if output["broker_binding"]["broker_verification_key_sha256"] != sha256(broker_verification_key):
        raise CompilerError("compiler output is bound to another broker key")
    try:
        Ed25519PublicKey.from_public_bytes(broker_verification_key).verify(
            base64.b64decode(output["signature"], validate=True),
            bytes.fromhex(output["compiler_output_sha256"]),
        )
    except Exception as exc:
        raise CompilerError("compiler output signature mismatch") from exc


def build_private_inventory(
    store_config: dict[str, Any],
    objects: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Build a closed private inventory; this does not attest that objects exist."""
    _validate(store_config, "benchmark-s3-object-lock-store-config-v1.5.schema.json")
    rows = list(objects)
    inventory: dict[str, Any] = {
        "schema": INVENTORY_SCHEMA,
        "status": STATUS,
        "protocol_version": "1.5",
        "visibility": "PRIVATE_TARGET_BEARING",
        "backend": "AWS_S3_OBJECT_LOCK_VERSION_PINNED",
        "store_config_sha256": digest(store_config),
        "bucket": store_config["bucket"],
        "required_object_lock_mode": "COMPLIANCE",
        "private_only": True,
        "retain_through_utc": store_config["retention_through_utc"],
        "objects": rows,
    }
    inventory["inventory_sha256"] = inventory_digest(inventory)
    _validate(inventory, "benchmark-private-worm-object-inventory-v1.5.schema.json")
    return inventory


def _verify_inventory(
    inventory: dict[str, Any],
    store_config: dict[str, Any],
    required_through_utc: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    _validate(store_config, "benchmark-s3-object-lock-store-config-v1.5.schema.json")
    _validate(inventory, "benchmark-private-worm-object-inventory-v1.5.schema.json")
    if inventory_digest(inventory) != inventory["inventory_sha256"]:
        raise CompilerError("private WORM inventory hash mismatch")
    if inventory["store_config_sha256"] != digest(store_config):
        raise CompilerError("private WORM inventory is bound to another store config")
    if inventory["bucket"] != store_config["bucket"]:
        raise CompilerError("private WORM inventory bucket differs from store config")
    required_through = _time(required_through_utc, "required_through_utc")
    if _time(store_config["retention_through_utc"], "store retention") < required_through:
        raise CompilerError("store retention ends before required custody coverage")

    receipt_refs: list[dict[str, Any]] = []
    payload_refs: dict[str, dict[str, Any]] = {}
    epoch_refs: list[dict[str, Any]] = []
    object_digests: set[str] = set()
    locators: set[tuple[str, str, str]] = set()
    for ref in inventory["objects"]:
        if ref["bucket"] != store_config["bucket"]:
            raise CompilerError("object reference escapes the configured bucket")
        expected_key = f"{store_config['key_prefix'].rstrip('/')}/objects/{ref['sha256'][:2]}/{ref['sha256']}"
        if ref["key"] != expected_key:
            raise CompilerError("object reference is not the configured content-addressed key")
        if _time(ref["retain_until_utc"], "object retention") < required_through:
            raise CompilerError("WORM object retention ends before required custody coverage")
        locator = (ref["bucket"], ref["key"], ref["version_id"])
        if locator in locators or ref["sha256"] in object_digests:
            raise CompilerError("duplicate or replayed WORM object reference")
        locators.add(locator)
        object_digests.add(ref["sha256"])
        if ref["role"] == "BROKER_RECEIPT":
            receipt_refs.append(ref)
        elif ref["role"] == "DELIVERY_PAYLOAD":
            payload_refs[ref["sha256"]] = ref
        else:
            epoch_refs.append(ref)
    receipt_refs.sort(key=lambda row: row["broker_sequence_number"])
    if not receipt_refs:
        raise CompilerError("WORM inventory contains no broker receipts")
    if [row["broker_sequence_number"] for row in receipt_refs] != list(range(len(receipt_refs))):
        raise CompilerError("broker receipt references contain a sequence gap or duplicate")
    if len(epoch_refs) != 1:
        raise CompilerError("exactly one WORM service-epoch binding is required")
    return receipt_refs, payload_refs, epoch_refs[0]


def _read_ref(ref: dict[str, Any], read_object: Callable[[dict[str, Any]], bytes]) -> bytes:
    try:
        raw = read_object(dict(ref))
    except Exception as exc:
        raise CompilerError("version-pinned WORM object read failed") from exc
    if not isinstance(raw, bytes):
        raise CompilerError("WORM reader returned non-bytes content")
    if sha256(raw) != ref["sha256"] or len(raw) != ref["byte_count"]:
        raise CompilerError("version-pinned WORM object digest or byte count mismatch")
    return raw


def _verify_broker_receipt(
    row: dict[str, Any],
    sequence: int,
    previous: str | None,
    config: dict[str, Any],
    verification_key: Ed25519PublicKey,
) -> None:
    _validate(row, "benchmark-delivery-broker-receipt-v1.5.schema.json")
    if row["sequence_number"] != sequence or row["previous_receipt_sha256"] != previous:
        raise CompilerError("broker receipt chain has a gap, fork, replay, or duplicate")
    if row["host_id"] != config["host_id"] or row["signing_key_id"] != config["signing_key_id"]:
        raise CompilerError("broker receipt host/key differs from pinned config")
    actual = digest(_without(row, "receipt_sha256", "signature"))
    if actual != row["receipt_sha256"]:
        raise CompilerError("broker receipt hash mismatch")
    try:
        signature = base64.b64decode(row["signature"], validate=True)
        verification_key.verify(signature, bytes.fromhex(actual))
    except Exception as exc:
        raise CompilerError("broker receipt signature mismatch") from exc


def compile_private_custody(
    *,
    broker_config: dict[str, Any],
    broker_state: dict[str, Any],
    store_config: dict[str, Any],
    inventory: dict[str, Any],
    broker_verification_key: bytes,
    custody_signing_key: Ed25519PrivateKey,
    required_from_utc: str,
    required_through_utc: str,
    read_object: Callable[[dict[str, Any]], bytes],
) -> dict[str, Any]:
    """Compile one complete broker chain into one private custody batch/certificate."""
    _validate(broker_config, "benchmark-delivery-broker-config-v1.5.schema.json")
    _validate(broker_state, "benchmark-delivery-broker-state-v1.5.schema.json")
    if broker_state["state_sha256"] != digest(_without(broker_state, "state_sha256")):
        raise CompilerError("broker state hash mismatch")
    if broker_state["status"] == "LOCKED_INVALID":
        raise CompilerError("LOCKED_INVALID broker state cannot be compiled")
    if not isinstance(broker_verification_key, bytes) or len(broker_verification_key) != 32:
        raise CompilerError("broker Ed25519 verification key must be exactly 32 bytes")
    try:
        verification_key = Ed25519PublicKey.from_public_bytes(broker_verification_key)
    except Exception as exc:
        raise CompilerError("broker Ed25519 verification key is malformed") from exc
    signing_public = custody_signing_key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    if signing_public != broker_verification_key:
        raise CompilerError("custody signer is not the pinned broker Ed25519 key")
    required_from = _time(required_from_utc, "required_from_utc")
    required_through = _time(required_through_utc, "required_through_utc")
    if required_from >= required_through:
        raise CompilerError("required custody interval must be nonempty")
    receipt_refs, payload_refs, epoch_ref = _verify_inventory(inventory, store_config, required_through_utc)

    receipts: list[dict[str, Any]] = []
    previous: str | None = None
    previous_time: datetime | None = None
    for sequence, ref in enumerate(receipt_refs):
        raw = _read_ref(ref, read_object)
        try:
            row = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise CompilerError("broker receipt WORM object is not canonical UTF-8 JSON") from exc
        if canonical_json(row) != raw:
            raise CompilerError("broker receipt WORM object is not canonical JSON")
        _verify_broker_receipt(row, sequence, previous, broker_config, verification_key)
        if ref["sha256"] != sha256(canonical_json(row)):
            raise CompilerError("broker receipt reference does not bind the canonical receipt")
        observed = _time(row["observed_at_utc"], "broker observation")
        if previous_time is not None and observed < previous_time:
            raise CompilerError("broker observation time is nonmonotonic")
        receipts.append(row)
        previous = row["receipt_sha256"]
        previous_time = observed

    if receipts[0]["event_kind"] != "HEARTBEAT":
        raise CompilerError("broker chain must begin with an accepted heartbeat")

    epoch_raw = _read_ref(epoch_ref, read_object)
    try:
        epoch = json.loads(epoch_raw.decode("utf-8"))
    except Exception as exc:
        raise CompilerError("service-epoch WORM object is not canonical UTF-8 JSON") from exc
    if canonical_json(epoch) != epoch_raw:
        raise CompilerError("service-epoch WORM object is not canonical JSON")
    _validate(epoch, "benchmark-private-broker-service-epoch-v1.5.schema.json")
    actual_epoch = digest(_without(epoch, "binding_sha256", "signature"))
    if epoch["binding_sha256"] != actual_epoch:
        raise CompilerError("service-epoch binding hash mismatch")
    try:
        verification_key.verify(
            base64.b64decode(epoch["signature"], validate=True), bytes.fromhex(actual_epoch)
        )
    except Exception as exc:
        raise CompilerError("service-epoch binding signature mismatch") from exc
    exact_epoch = {
        "host_id": broker_config["host_id"],
        "signing_key_id": broker_config["signing_key_id"],
        "broker_config_sha256": digest(broker_config),
        "broker_verification_key_sha256": sha256(broker_verification_key),
        "first_broker_sequence": 0,
        "last_broker_sequence": len(receipts) - 1,
        "broker_receipt_count": len(receipts),
        "first_broker_receipt_sha256": receipts[0]["receipt_sha256"],
        "last_broker_receipt_sha256": receipts[-1]["receipt_sha256"],
        "opened_at_utc": receipts[0]["observed_at_utc"],
        "sealed_at_utc": receipts[-1]["observed_at_utc"],
    }
    for key, expected in exact_epoch.items():
        if epoch[key] != expected:
            raise CompilerError(f"service-epoch binding does not seal exact broker {key}")
    boot_id = epoch["service_epoch_id"]

    active: dict[str, Any] | None = None
    used_transactions: set[str] = set()
    used_payload_refs: set[str] = set()
    blobs: dict[str, bytes] = {}
    custody_records: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    previous_custody: str | None = None
    last_heartbeat: str | None = None

    def append_record(source: dict[str, Any], event_kind: str) -> None:
        nonlocal previous_custody
        record = {
            "sequence_number": len(custody_records),
            "previous_receipt_sha256": previous_custody,
            "event_kind": event_kind,
            "payload_sha256": source["payload_sha256"],
            "payload_byte_count": source["payload_byte_count"],
            "delivery_channel": source["delivery_channel"],
            "observed_at_utc": source["observed_at_utc"],
            "boot_id": boot_id,
        }
        record["receipt_sha256"] = custody.record_digest(record)
        custody_records.append(record)
        bindings.append({
            "custody_record_sequence": record["sequence_number"],
            "custody_event_kind": event_kind,
            "custody_receipt_sha256": record["receipt_sha256"],
            "broker_sequence_number": source["sequence_number"],
            "broker_event_kind": source["event_kind"],
            "broker_receipt_sha256": source["receipt_sha256"],
        })
        previous_custody = record["receipt_sha256"]

    for row in receipts:
        event = row["event_kind"]
        txid = row["transaction_id"]
        if event == "LOCK_INVALID":
            raise CompilerError("LOCK_INVALID broker receipt cannot be compiled")
        if event == "HEARTBEAT":
            if txid is not None or row["payload_sha256"] != broker.EMPTY_SHA256 or row["payload_byte_count"] != 0 or row["delivery_channel"] != "broker:control":
                raise CompilerError("malformed broker heartbeat")
            if last_heartbeat is not None:
                gap = int((_time(row["observed_at_utc"], "heartbeat") - _time(last_heartbeat, "heartbeat")).total_seconds())
                if gap < 0 or gap > broker_config["heartbeat_interval_seconds"]:
                    raise CompilerError("broker heartbeat coverage gap")
            last_heartbeat = row["observed_at_utc"]
            append_record(row, "HEARTBEAT")
            continue
        if last_heartbeat is None:
            raise CompilerError("broker delivery event precedes initial heartbeat")
        since_heartbeat = int((_time(row["observed_at_utc"], "event") - _time(last_heartbeat, "heartbeat")).total_seconds())
        if since_heartbeat < 0 or since_heartbeat > broker_config["heartbeat_interval_seconds"]:
            raise CompilerError("broker event lies outside heartbeat coverage")
        if event == "PREPARE":
            if active is not None or txid is None or txid in used_transactions:
                raise CompilerError("overlapping or replayed PREPARE")
            payload_ref = payload_refs.get(row["payload_sha256"])
            if payload_ref is None:
                raise CompilerError("PREPARE payload lacks a version-pinned WORM reference")
            raw = _read_ref(payload_ref, read_object)
            if len(raw) != row["payload_byte_count"]:
                raise CompilerError("PREPARE payload metadata differs from WORM object")
            blobs[row["payload_sha256"]] = raw
            used_payload_refs.add(row["payload_sha256"])
            active = {
                "transaction_id": txid,
                "phase": "PREPARED",
                "payload_sha256": row["payload_sha256"],
                "payload_byte_count": row["payload_byte_count"],
                "delivery_channel": row["delivery_channel"],
            }
            used_transactions.add(txid)
            continue
        if active is None or active["transaction_id"] != txid:
            raise CompilerError(f"{event} lacks its matching active transaction")
        if any(row[key] != active[key] for key in ("payload_sha256", "payload_byte_count", "delivery_channel")):
            raise CompilerError(f"{event} metadata differs from PREPARE")
        if event == "START":
            if active["phase"] != "PREPARED":
                raise CompilerError("duplicate or out-of-order START")
            active["phase"] = "STARTED"
        elif event in {"DELIVER", "ABORT"}:
            if active["phase"] != "STARTED":
                raise CompilerError(f"{event} occurs without START")
            append_record(row, "DELIVERY" if event == "DELIVER" else "ABANDONED_PARTIAL")
            active = None
        else:
            raise CompilerError("unknown broker transition")

    if active is not None:
        phase = active["phase"]
        raise CompilerError(f"incomplete broker transaction remains {phase}")
    if set(payload_refs) != used_payload_refs:
        raise CompilerError("private WORM inventory contains unused or duplicate payload objects")
    if not custody_records:
        raise CompilerError("broker chain produced no custody records")

    expected_state: dict[str, Any] = {
        "schema": broker.STATE_SCHEMA,
        "status": broker.STATUS,
        "sequence_number": len(receipts) - 1,
        "last_receipt_sha256": receipts[-1]["receipt_sha256"],
        "last_heartbeat_utc": last_heartbeat,
        "active_transaction": None,
    }
    expected_state["state_sha256"] = digest(expected_state)
    if broker_state != expected_state:
        raise CompilerError("broker durable state does not exactly replay from WORM receipts")

    batch: dict[str, Any] = {
        "schema": custody.BATCH_SCHEMA,
        "status": STATUS,
        "protocol_version": "1.5",
        "host_id": broker_config["host_id"],
        "signing_key_id": broker_config["signing_key_id"],
        "signature_algorithm": "Ed25519",
        "batch_sequence": 0,
        "previous_batch_sha256": None,
        "boot_id": boot_id,
        "captured_from_utc": custody_records[0]["observed_at_utc"],
        "captured_through_utc": custody_records[-1]["observed_at_utc"],
        "maximum_heartbeat_interval_seconds": 300,
        "first_record_sequence": 0,
        "last_record_sequence": len(custody_records) - 1,
        "records": custody_records,
    }
    batch["batch_sha256"] = custody.batch_digest(batch)
    batch["signature"] = base64.b64encode(
        custody_signing_key.sign(bytes.fromhex(batch["batch_sha256"]))
    ).decode()
    _validate(batch, "benchmark-private-custody-batch-v1.5.schema.json")

    certificate = custody.verify_coverage(
        [batch],
        {(broker_config["host_id"], broker_config["signing_key_id"]): broker_verification_key},
        blobs,
        [broker_config["host_id"]],
        required_from_utc,
        required_through_utc,
    )
    output: dict[str, Any] = {
        "schema": OUTPUT_SCHEMA,
        "status": STATUS,
        "protocol_version": "1.5",
        "visibility": "PRIVATE_TARGET_BEARING",
        "broker_binding": {
            "host_id": broker_config["host_id"],
            "signing_key_id": broker_config["signing_key_id"],
            "signature_algorithm": "Ed25519",
            "broker_config_sha256": digest(broker_config),
            "broker_verification_key_sha256": sha256(broker_verification_key),
            "broker_state_sha256": broker_state["state_sha256"],
            "boot_id": boot_id,
            "first_broker_sequence": 0,
            "last_broker_sequence": len(receipts) - 1,
            "broker_receipt_count": len(receipts),
            "broker_chain_tip_sha256": receipts[-1]["receipt_sha256"],
        },
        "object_inventory_sha256": inventory["inventory_sha256"],
        "record_bindings": bindings,
        "custody_batches": [batch],
        "coverage_certificate": certificate,
        "signature_algorithm": "Ed25519",
    }
    output["compiler_output_sha256"] = output_digest(output)
    output["signature"] = base64.b64encode(
        custody_signing_key.sign(bytes.fromhex(output["compiler_output_sha256"]))
    ).decode()
    verify_compiler_output(output, broker_verification_key)
    return output


if __name__ == "__main__":
    raise SystemExit(
        "PRE-P1 library only: production custody compilation requires an injected "
        "accepted version-pinned WORM reader and cannot be activated from this CLI"
    )
