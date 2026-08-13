#!/usr/bin/env python3
"""PRE-P1 controlled-delivery broker prototype for one dedicated VPS harness.

This is deliberately not a daemon and does not claim capture of stock Codex,
Claude, a companion Mac, or any production delivery path.  It proves the local
transition mechanics needed by source-boundary 1.1: durable custody precedes
START, and only START may precede DELIVER or ABORT.  Production storage, key
acceptance, and service acceptance remain unset.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Callable, Sequence
import uuid

import jsonschema
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


ROOT = Path(__file__).resolve().parents[1]
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()
MAX_HEARTBEAT_SECONDS = 240
STATUS = "PRE_P1_NOT_OPERATIONAL"
STATE_SCHEMA = "c5k4-method-v1.5-delivery-broker-state-1.0"
RECEIPT_SCHEMA = "c5k4-method-v1.5-delivery-broker-receipt-1.0"


class BrokerError(RuntimeError):
    """A fail-closed broker contract violation."""


class SimulatedCrash(RuntimeError):
    """Test-only crash at a named durability boundary."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def utc(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise BrokerError(f"invalid UTC timestamp: {value!r}") from exc


def schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def validate(value: object, name: str) -> None:
    try:
        jsonschema.Draft7Validator(schema(name), format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.ValidationError as exc:
        raise BrokerError(f"{name} validation failed: {exc.message}") from exc


def _without(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in keys}


def _fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write(path: Path, raw: bytes, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            try:
                os.link(temporary, path)
            except FileExistsError as exc:
                raise BrokerError(f"immutable destination already exists: {path.name}") from exc
            temporary.unlink()
        else:
            os.replace(temporary, path)
        _fsync_dir(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


class LocalImmutableStore:
    """Content-addressed test store; intentionally not a production backend."""

    def __init__(self, root: Path, available: Callable[[], bool] | None = None):
        self.root = root
        self.available = available or (lambda: True)

    def _check(self) -> None:
        if not self.available():
            raise BrokerError("content store unavailable")

    def path(self, object_sha256: str) -> Path:
        return self.root / "objects" / object_sha256[:2] / object_sha256

    def put(self, raw: bytes) -> str:
        self._check()
        object_sha256 = sha256(raw)
        destination = self.path(object_sha256)
        if destination.exists():
            if destination.read_bytes() != raw:
                raise BrokerError("content-address collision or tamper")
            return object_sha256
        atomic_write(destination, raw, exclusive=True)
        if destination.read_bytes() != raw:
            raise BrokerError("durable content verification failed")
        return object_sha256

    def get(self, object_sha256: str) -> bytes:
        self._check()
        try:
            raw = self.path(object_sha256).read_bytes()
        except FileNotFoundError as exc:
            raise BrokerError("content-addressed blob missing") from exc
        if sha256(raw) != object_sha256:
            raise BrokerError("content-addressed blob tampered")
        return raw


class DeliveryBroker:
    """Single-process reference state machine with crash-recoverable receipts."""

    def __init__(
        self,
        root: Path,
        config: dict[str, Any],
        private_key: Ed25519PrivateKey,
        *,
        store_available: Callable[[], bool] | None = None,
    ):
        validate(config, "benchmark-delivery-broker-config-v1.5.schema.json")
        self.root = root
        self.config = config
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.store = LocalImmutableStore(root / "store", store_available)
        self.receipts = root / "receipts"
        self.state_path = root / "state.json"
        self.lock_path = root / "LOCKED_INVALID"
        self.root.mkdir(parents=True, exist_ok=True)
        self.receipts.mkdir(parents=True, exist_ok=True)
        self._recover()

    @property
    def public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def _default_state(self) -> dict[str, Any]:
        row: dict[str, Any] = {
            "schema": STATE_SCHEMA, "status": STATUS, "sequence_number": -1,
            "last_receipt_sha256": None, "last_heartbeat_utc": None,
            "active_transaction": None,
        }
        row["state_sha256"] = digest(row)
        return row

    def _state_digest(self, row: dict[str, Any]) -> str:
        return digest(_without(row, "state_sha256"))

    def _write_state(self, row: dict[str, Any]) -> None:
        row["state_sha256"] = self._state_digest(row)
        validate(row, "benchmark-delivery-broker-state-v1.5.schema.json")
        atomic_write(self.state_path, canonical_json(row))
        self.state = row

    def _receipt_files(self) -> list[Path]:
        return sorted(self.receipts.glob("[0-9]" * 20 + ".json"))

    def _verify_receipt(self, row: dict[str, Any], expected_sequence: int, previous: str | None) -> None:
        validate(row, "benchmark-delivery-broker-receipt-v1.5.schema.json")
        if row["sequence_number"] != expected_sequence or row["previous_receipt_sha256"] != previous:
            raise BrokerError("receipt sequence rollback, gap, or fork")
        actual = digest(_without(row, "receipt_sha256", "signature"))
        if actual != row["receipt_sha256"]:
            raise BrokerError("receipt hash mismatch")
        try:
            self.public_key.verify(base64.b64decode(row["signature"], validate=True), bytes.fromhex(actual))
        except Exception as exc:
            raise BrokerError("receipt signature mismatch") from exc

    def _apply(self, state: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
        active = state["active_transaction"]
        event = row["event_kind"]
        txid = row["transaction_id"]
        if event == "HEARTBEAT":
            if txid is not None or row["payload_sha256"] != EMPTY_SHA256 or row["payload_byte_count"] != 0:
                raise BrokerError("malformed heartbeat")
            state["last_heartbeat_utc"] = row["observed_at_utc"]
        elif event == "PREPARE":
            if active is not None:
                raise BrokerError("parallel delivery transaction forbidden")
            active = {"transaction_id": txid, "phase": "PREPARED", "payload_sha256": row["payload_sha256"], "payload_byte_count": row["payload_byte_count"], "delivery_channel": row["delivery_channel"]}
            state["active_transaction"] = active
        elif event == "START":
            if active is None or active["phase"] != "PREPARED" or active["transaction_id"] != txid:
                raise BrokerError("START without matching PREPARE")
            if any(row[key] != active[key] for key in ("payload_sha256", "payload_byte_count", "delivery_channel")):
                raise BrokerError("START metadata differs from PREPARE")
            active["phase"] = "STARTED"
        elif event in {"DELIVER", "ABORT"}:
            if active is None or active["phase"] != "STARTED" or active["transaction_id"] != txid:
                raise BrokerError(f"{event} without matching START")
            if any(row[key] != active[key] for key in ("payload_sha256", "payload_byte_count", "delivery_channel")):
                raise BrokerError(f"{event} metadata differs from PREPARE")
            state["active_transaction"] = None
        elif event == "LOCK_INVALID":
            state["status"] = "LOCKED_INVALID"
        state["sequence_number"] = row["sequence_number"]
        state["last_receipt_sha256"] = row["receipt_sha256"]
        return state

    def _recover(self) -> None:
        if self.lock_path.exists():
            state = self._default_state()
            state["status"] = "LOCKED_INVALID"
            self._write_state(state)
            return
        state = self._default_state()
        previous = None
        try:
            files = self._receipt_files()
            for expected, path in enumerate(files):
                if path.name != f"{expected:020d}.json":
                    raise BrokerError("receipt filename sequence gap")
                row = json.loads(path.read_text(encoding="utf-8"))
                self._verify_receipt(row, expected, previous)
                self.store.get(sha256(canonical_json(row)))
                state = self._apply(state, row)
                previous = row["receipt_sha256"]
            if self.state_path.exists():
                persisted = json.loads(self.state_path.read_text(encoding="utf-8"))
                validate(persisted, "benchmark-delivery-broker-state-v1.5.schema.json")
                if persisted["state_sha256"] != self._state_digest(persisted):
                    raise BrokerError("state hash mismatch")
                if persisted["sequence_number"] > state["sequence_number"]:
                    raise BrokerError("state references a missing receipt")
            self._write_state(state)
            if state["active_transaction"] is not None:
                self.store.get(state["active_transaction"]["payload_sha256"])
                if state["active_transaction"]["phase"] == "STARTED":
                    raise BrokerError("restart found an indeterminate STARTED delivery")
        except Exception as exc:
            self._lock(f"recovery:{type(exc).__name__}")
            raise BrokerError("broker recovery failed and is now LOCKED_INVALID") from exc

    def _lock(self, reason: str) -> None:
        if not self.lock_path.exists():
            atomic_write(self.lock_path, canonical_json({"status": "LOCKED_INVALID", "reason_sha256": sha256(reason.encode())}), exclusive=True)
        state = getattr(self, "state", self._default_state())
        state["status"] = "LOCKED_INVALID"
        self._write_state(state)

    def _store_put(self, raw: bytes) -> str:
        try:
            return self.store.put(raw)
        except Exception as exc:
            self._lock(f"store-write:{type(exc).__name__}")
            raise BrokerError("content store write failed; broker locked") from exc

    def _store_get(self, object_sha256: str) -> bytes:
        try:
            return self.store.get(object_sha256)
        except Exception as exc:
            self._lock(f"store-read:{type(exc).__name__}")
            raise BrokerError("content store verification failed; broker locked") from exc

    def _guard(self, observed_at_utc: str, *, permit_initial_heartbeat: bool = False) -> None:
        if self.lock_path.exists() or self.state["status"] == "LOCKED_INVALID":
            raise BrokerError("broker is LOCKED_INVALID")
        now = utc(observed_at_utc)
        last = self.state["last_heartbeat_utc"]
        if last is None:
            if permit_initial_heartbeat:
                return
            self._lock("delivery before initial heartbeat")
            raise BrokerError("initial heartbeat required")
        gap = int((now - utc(last)).total_seconds())
        if gap < 0 or gap > self.config["heartbeat_interval_seconds"]:
            self._lock("stale or nonmonotonic heartbeat")
            raise BrokerError("heartbeat stale; broker locked")

    def _append(self, event: str, observed_at_utc: str, tx: dict[str, Any] | None = None, *, crash: str | None = None) -> dict[str, Any]:
        sequence = self.state["sequence_number"] + 1
        tx = tx or {"transaction_id": None, "payload_sha256": EMPTY_SHA256, "payload_byte_count": 0, "delivery_channel": "broker:control"}
        row: dict[str, Any] = {
            "schema": RECEIPT_SCHEMA, "status": STATUS, "protocol_version": "1.5",
            "host_id": self.config["host_id"], "signing_key_id": self.config["signing_key_id"],
            "signature_algorithm": "Ed25519", "sequence_number": sequence,
            "previous_receipt_sha256": self.state["last_receipt_sha256"], "event_kind": event,
            "transaction_id": tx["transaction_id"], "payload_sha256": tx["payload_sha256"],
            "payload_byte_count": tx["payload_byte_count"], "delivery_channel": tx["delivery_channel"],
            "observed_at_utc": observed_at_utc,
        }
        row["receipt_sha256"] = digest(row)
        row["signature"] = base64.b64encode(self.private_key.sign(bytes.fromhex(row["receipt_sha256"]))).decode()
        validate(row, "benchmark-delivery-broker-receipt-v1.5.schema.json")
        raw = canonical_json(row)
        self._store_put(raw)
        atomic_write(self.receipts / f"{sequence:020d}.json", raw, exclusive=True)
        if crash == "AFTER_RECEIPT":
            raise SimulatedCrash(event)
        next_state = self._apply(json.loads(json.dumps(self.state)), row)
        self._write_state(next_state)
        return row

    def heartbeat(self, observed_at_utc: str) -> dict[str, Any]:
        self._guard(observed_at_utc, permit_initial_heartbeat=True)
        return self._append("HEARTBEAT", observed_at_utc)

    def prepare(self, payload: bytes, delivery_channel: str, observed_at_utc: str, *, crash: str | None = None) -> str:
        self._guard(observed_at_utc)
        if self.state["active_transaction"] is not None:
            self._lock("overlapping prepare")
            raise BrokerError("parallel delivery transaction forbidden")
        payload_sha = self._store_put(payload)
        if crash == "AFTER_BLOB":
            raise SimulatedCrash("PREPARE")
        tx = {"transaction_id": uuid.uuid4().hex, "payload_sha256": payload_sha, "payload_byte_count": len(payload), "delivery_channel": delivery_channel}
        self._append("PREPARE", observed_at_utc, tx, crash=crash)
        return tx["transaction_id"]

    def start(self, transaction_id: str, observed_at_utc: str, *, crash: str | None = None) -> None:
        self._guard(observed_at_utc)
        active = self.state["active_transaction"]
        if active is None or active["phase"] != "PREPARED" or active["transaction_id"] != transaction_id:
            self._lock("unwrapped start")
            raise BrokerError("START requires the current PREPARE")
        self._store_get(active["payload_sha256"])
        self._append("START", observed_at_utc, active, crash=crash)

    def finish(self, transaction_id: str, event: str, observed_at_utc: str, *, crash: str | None = None) -> bytes:
        self._guard(observed_at_utc)
        if event not in {"DELIVER", "ABORT"}:
            self._lock("invalid terminal event")
            raise BrokerError("terminal event must be DELIVER or ABORT")
        active = self.state["active_transaction"]
        if active is None or active["phase"] != "STARTED" or active["transaction_id"] != transaction_id:
            self._lock("unwrapped delivery")
            raise BrokerError(f"{event} requires the current START")
        payload = self._store_get(active["payload_sha256"])
        self._append(event, observed_at_utc, active, crash=crash)
        return payload

    def deliver_to(self, transaction_id: str, sink: Callable[[bytes], None], observed_at_utc: str) -> None:
        active = self.state["active_transaction"]
        if active is None or active["phase"] != "STARTED":
            self.finish(transaction_id, "DELIVER", observed_at_utc)
            return
        payload = self._store_get(active["payload_sha256"])
        try:
            sink(payload)
        except Exception:
            self.finish(transaction_id, "ABORT", observed_at_utc)
            raise
        self.finish(transaction_id, "DELIVER", observed_at_utc)

    def run_subprocess(self, command: Sequence[str], stdin: bytes, observed_at_utc: str) -> subprocess.CompletedProcess[bytes]:
        """Capture stdin before child delivery and stdout before caller delivery."""
        stdin_tx = self.prepare(stdin, "subprocess:stdin", observed_at_utc)
        self.start(stdin_tx, observed_at_utc)
        try:
            completed = subprocess.run(command, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        except Exception:
            self.finish(stdin_tx, "ABORT", observed_at_utc)
            raise
        self.finish(stdin_tx, "DELIVER", observed_at_utc)
        stdout_tx = self.prepare(completed.stdout, "subprocess:stdout", observed_at_utc)
        self.start(stdout_tx, observed_at_utc)
        captured_stdout = self.finish(stdout_tx, "DELIVER", observed_at_utc)
        stderr_tx = self.prepare(completed.stderr, "subprocess:stderr", observed_at_utc)
        self.start(stderr_tx, observed_at_utc)
        captured_stderr = self.finish(stderr_tx, "DELIVER", observed_at_utc)
        return subprocess.CompletedProcess(completed.args, completed.returncode, captured_stdout, captured_stderr)

    def readiness(self, observed_at_utc: str) -> dict[str, Any]:
        last = self.state["last_heartbeat_utc"]
        fresh = last is not None and 0 <= int((utc(observed_at_utc) - utc(last)).total_seconds()) <= self.config["heartbeat_interval_seconds"]
        reasons = ["PRODUCTION_STORE_UNSET", "HOST_KEY_NOT_ACCEPTED", "DEDICATED_SERVICE_NOT_ACCEPTED", "ACCEPTANCE_SUITE_NOT_FROZEN"]
        if not fresh:
            reasons.append("HEARTBEAT_STALE")
        if self.lock_path.exists():
            reasons.append("LOCKED_INVALID")
        row: dict[str, Any] = {
            "schema": "c5k4-method-v1.5-delivery-broker-readiness-1.0", "status": STATUS,
            "scope": "DEDICATED_AI_VPS_HARNESS_ONLY", "config_sha256": digest(self.config),
            "public_key_sha256": sha256(self.public_key_bytes), "state_sha256": self.state["state_sha256"],
            "receipt_chain_tip_sha256": self.state["last_receipt_sha256"], "heartbeat_fresh": fresh,
            "locked_invalid": self.lock_path.exists(), "production_store_configured": False,
            "service_accepted": False, "operational": False, "reasons": reasons,
        }
        row["readiness_sha256"] = digest(row)
        validate(row, "benchmark-delivery-broker-readiness-v1.5.schema.json")
        return row


def test_config(root: Path, key_id: str = "test-key") -> dict[str, Any]:
    """Construct the only supported PRE-P1 local-test configuration."""
    return {
        "schema": "c5k4-method-v1.5-delivery-broker-config-1.0", "status": STATUS,
        "protocol_version": "1.5", "host_id": "ai-vps-controlled-harness",
        "signing_key_id": key_id, "heartbeat_interval_seconds": MAX_HEARTBEAT_SECONDS,
        "store": {"test_backend": "LOCAL_FILESYSTEM_CONTENT_ADDRESSED_TEST_STORE", "test_root": str(root / "store"), "production_backend": None, "production_locator": None, "retention_acceptance": False},
        "service_acceptance": {"dedicated_service_installed": False, "host_key_accepted": False, "acceptance_suite_passed": False},
    }
