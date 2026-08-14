#!/usr/bin/env python3
"""PRE-P1 bridge from the delivery broker to version-pinned S3 custody.

The S3 Object Lock object version is authoritative.  Local content bytes are
only a cache and are never used to satisfy ``get`` or recovery when S3 is
unavailable.  PrivateObjectRef records remain private local state.

This module is an integration acceptance harness, not activation.  The broker
configuration accepted here remains the committed local/test-only schema and
cannot be reused unchanged for activation.  This module does not construct a
boto3 client, accept a live bucket/key/service ceremony, or make the broker
operational.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import method_v15_delivery_broker as broker
import method_v15_s3_object_lock_store as s3store


class RemoteAdapterError(broker.BrokerError):
    """The remote-authoritative custody bridge failed closed."""


class SimulatedPowerLoss(BaseException):
    """Test-only process loss; deliberately bypasses exception recovery."""


class RemoteAuthoritativeCAS:
    """Adapt PrivateObjectRef storage to the broker's digest-keyed interface."""

    REF_SCHEMA = "c5k4-method-v1.5-private-s3-object-reference-1.0"
    REF_STATUS = "PRE_P1_PRIVATE_REMOTE_REFERENCE_NOT_OPERATIONAL"
    REF_SCHEMA_FILE = "benchmark-private-s3-object-reference-v1.5.schema.json"

    def __init__(
        self,
        root: Path,
        remote: s3store.S3ObjectLockStore,
        *,
        fault: Callable[[str, str], None] | None = None,
    ) -> None:
        self.root = root
        self.remote = remote
        self.fault = fault or (lambda _boundary, _digest: None)
        self.references = root / "private-object-refs"
        self.cache = root / "cache"

    def _reference_path(self, object_sha256: str) -> Path:
        return self.references / object_sha256[:2] / f"{object_sha256}.json"

    def _cache_path(self, object_sha256: str) -> Path:
        return self.cache / object_sha256[:2] / object_sha256

    @staticmethod
    def _row(reference: s3store.PrivateObjectRef) -> dict[str, Any]:
        return {
            "schema": RemoteAuthoritativeCAS.REF_SCHEMA,
            "status": RemoteAuthoritativeCAS.REF_STATUS,
            "bucket": reference.bucket,
            "key": reference.key,
            "version_id": reference.version_id,
            "sha256": reference.sha256,
            "byte_count": reference.byte_count,
            "retain_until_utc": reference.retain_until_utc,
        }

    @staticmethod
    def _parse(row: object, expected_sha256: str) -> s3store.PrivateObjectRef:
        try:
            broker.validate(row, RemoteAuthoritativeCAS.REF_SCHEMA_FILE)
        except Exception as exc:
            raise RemoteAdapterError("private object reference schema mismatch") from exc
        assert isinstance(row, dict)
        if row["sha256"] != expected_sha256:
            raise RemoteAdapterError("private object reference digest mismatch")
        return s3store.PrivateObjectRef(
            bucket=row["bucket"], key=row["key"], version_id=row["version_id"],
            sha256=row["sha256"], byte_count=row["byte_count"],
            retain_until_utc=row["retain_until_utc"],
        )

    def _persist_reference(self, reference: s3store.PrivateObjectRef) -> None:
        path = self._reference_path(reference.sha256)
        row = self._row(reference)
        broker.validate(row, self.REF_SCHEMA_FILE)
        raw = broker.canonical_json(row)
        if path.exists():
            try:
                current = self._parse(json.loads(path.read_text(encoding="utf-8")), reference.sha256)
            except Exception as exc:
                raise RemoteAdapterError("persisted private object reference is invalid") from exc
            if current != reference:
                raise RemoteAdapterError("immutable private object reference changed version")
            return
        broker.atomic_write(path, raw, exclusive=True)

    def _load_reference(self, object_sha256: str) -> s3store.PrivateObjectRef:
        try:
            row = json.loads(self._reference_path(object_sha256).read_text(encoding="utf-8"))
        except Exception as exc:
            raise RemoteAdapterError("private remote object reference missing or unreadable") from exc
        return self._parse(row, object_sha256)

    def put(self, raw: bytes) -> str:
        """Commit remotely, pin exact version locally, then optionally cache."""
        try:
            reference = self.remote.put(raw)
        except Exception as exc:
            raise RemoteAdapterError("remote immutable put or verification failed") from exc
        expected = broker.sha256(raw)
        if reference.sha256 != expected or reference.byte_count != len(raw):
            raise RemoteAdapterError("remote adapter returned a mismatched private reference")
        self.fault("AFTER_REMOTE_PUT", expected)
        self._persist_reference(reference)
        self.fault("AFTER_REFERENCE", expected)
        # Cache creation occurs only after the authoritative object and exact
        # version reference are durable.  Reads never fall back to this cache.
        broker.atomic_write(self._cache_path(expected), raw)
        return expected

    def get(self, object_sha256: str) -> bytes:
        """Read and reverify the exact remote version; never trust local cache."""
        reference = self._load_reference(object_sha256)
        try:
            raw = self.remote.get(reference)
        except Exception as exc:
            raise RemoteAdapterError("remote exact-version read or verification failed") from exc
        if broker.sha256(raw) != object_sha256 or len(raw) != reference.byte_count:
            raise RemoteAdapterError("remote exact-version bytes mismatch")
        broker.atomic_write(self._cache_path(object_sha256), raw)
        return raw


class S3BackedDeliveryBroker(broker.DeliveryBroker):
    """DeliveryBroker whose only custody authority is S3 Object Lock."""

    def __init__(
        self,
        root: Path,
        config: dict[str, Any],
        private_key: Ed25519PrivateKey,
        remote: s3store.S3ObjectLockStore,
        *,
        fault: Callable[[str, str], None] | None = None,
    ) -> None:
        broker.validate(config, "benchmark-delivery-broker-config-v1.5.schema.json")
        self.root = root
        self.config = config
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.store = RemoteAuthoritativeCAS(root / "remote-custody", remote, fault=fault)
        self.receipts = root / "receipts"
        self.state_path = root / "state.json"
        self.lock_path = root / "LOCKED_INVALID"
        self.root.mkdir(parents=True, exist_ok=True)
        self.receipts.mkdir(parents=True, exist_ok=True)
        self._recover()
        self._verify_remote_payload_inventory()

    def _verify_remote_payload_inventory(self) -> None:
        """Reverify every nonempty journal-referenced payload on each restart."""
        try:
            seen: set[str] = set()
            for path in self._receipt_files():
                row = json.loads(path.read_text(encoding="utf-8"))
                payload_sha256 = row["payload_sha256"]
                if row["payload_byte_count"] and payload_sha256 not in seen:
                    self.store.get(payload_sha256)
                    seen.add(payload_sha256)
        except Exception as exc:
            self._lock(f"remote-payload-inventory:{type(exc).__name__}")
            raise RemoteAdapterError("remote payload inventory failed; broker locked") from exc


def build_pre_p1_integration(
    root: Path,
    broker_config: dict[str, Any],
    private_key: Ed25519PrivateKey,
    remote: s3store.S3ObjectLockStore,
    *,
    acceptance_test: bool,
    live_store_acceptance: dict[str, Any] | None = None,
) -> S3BackedDeliveryBroker:
    """Build only the test integration; its broker config is not activatable."""
    if not acceptance_test:
        if live_store_acceptance is None:
            raise RemoteAdapterError("live accepted immutable-store configuration is absent")
        raise RemoteAdapterError("PRE-P1 integration cannot claim operational activation")
    if live_store_acceptance is not None:
        raise RemoteAdapterError("acceptance-test mode cannot consume a live acceptance claim")
    return S3BackedDeliveryBroker(root, broker_config, private_key, remote)
