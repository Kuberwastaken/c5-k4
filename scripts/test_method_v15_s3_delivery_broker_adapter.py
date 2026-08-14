#!/usr/bin/env python3
"""Adversarial integration tests for remote-authoritative broker custody."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import method_v15_delivery_broker as broker
import method_v15_s3_delivery_broker_adapter as integration
import method_v15_s3_object_lock_store as s3store
from test_method_v15_s3_object_lock_store import FakeS3, NOW, config as s3_config


T0 = "2026-08-13T12:00:00Z"
T1 = "2026-08-13T12:01:00Z"
T2 = "2026-08-13T12:02:00Z"


class Fixture:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.client = FakeS3()
        self.remote = s3store.S3ObjectLockStore(self.client, s3_config(), clock=lambda: NOW)
        self.key = Ed25519PrivateKey.generate()
        self.config = broker.test_config(self.root)

    def open(self, **kwargs: object) -> integration.S3BackedDeliveryBroker:
        return integration.S3BackedDeliveryBroker(self.root, self.config, self.key, self.remote, **kwargs)

    def primed(self) -> integration.S3BackedDeliveryBroker:
        value = self.open()
        value.heartbeat(T0)
        return value

    def close(self) -> None:
        self.temp.cleanup()


class S3DeliveryBrokerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.f = Fixture()

    def tearDown(self) -> None:
        self.f.close()

    def test_payload_and_each_receipt_are_remote_before_local_journal(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"semantic payload", "wrapper:stdout", T1)
        value.start(txid, T1)
        value.finish(txid, "DELIVER", T2)
        local_receipts = value._receipt_files()
        self.assertEqual(len(local_receipts), 4)
        for path in local_receipts:
            raw = path.read_bytes()
            object_sha = broker.sha256(raw)
            reference = value.store._load_reference(object_sha)
            self.assertEqual(value.store.remote.get(reference), raw)
        payload_ref = value.store._load_reference(broker.sha256(b"semantic payload"))
        self.assertEqual(value.store.remote.get(payload_ref), b"semantic payload")

    def test_remote_receipt_failure_prevents_local_prepare_and_sticky_locks(self) -> None:
        value = self.f.primed()

        def fail_after_payload(boundary: str, object_sha: str) -> None:
            if boundary == "AFTER_REFERENCE" and object_sha == broker.sha256(b"payload"):
                self.f.client.outage = "all"

        value.store.fault = fail_after_payload
        with self.assertRaisesRegex(broker.BrokerError, "store write failed"):
            value.prepare(b"payload", "wrapper:stdout", T1)
        rows = [json.loads(path.read_text()) for path in value._receipt_files()]
        self.assertEqual([row["event_kind"] for row in rows], ["HEARTBEAT"])
        self.assertTrue(value.lock_path.exists())

    def test_power_loss_after_remote_put_leaves_no_local_delivery_and_retries(self) -> None:
        value = self.f.primed()
        fired = False

        def crash(boundary: str, object_sha: str) -> None:
            nonlocal fired
            if not fired and boundary == "AFTER_REMOTE_PUT" and object_sha == broker.sha256(b"payload"):
                fired = True
                raise integration.SimulatedPowerLoss()

        value.store.fault = crash
        with self.assertRaises(integration.SimulatedPowerLoss):
            value.prepare(b"payload", "wrapper:stdout", T1)
        self.assertEqual([json.loads(path.read_text())["event_kind"] for path in value._receipt_files()], ["HEARTBEAT"])
        self.assertFalse(value.store._reference_path(broker.sha256(b"payload")).exists())
        restarted = self.f.open()
        txid = restarted.prepare(b"payload", "wrapper:stdout", T1)
        self.assertEqual(restarted.state["active_transaction"]["transaction_id"], txid)

    def test_power_loss_after_private_ref_still_precedes_local_journal(self) -> None:
        value = self.f.primed()

        def crash(boundary: str, object_sha: str) -> None:
            if boundary == "AFTER_REFERENCE" and object_sha == broker.sha256(b"payload"):
                raise integration.SimulatedPowerLoss()

        value.store.fault = crash
        with self.assertRaises(integration.SimulatedPowerLoss):
            value.prepare(b"payload", "wrapper:stdout", T1)
        self.assertTrue(value.store._reference_path(broker.sha256(b"payload")).exists())
        self.assertEqual([json.loads(path.read_text())["event_kind"] for path in value._receipt_files()], ["HEARTBEAT"])

    def test_power_loss_after_remote_prepare_receipt_cannot_publish_local_prepare(self) -> None:
        value = self.f.primed()
        payload_sha = broker.sha256(b"payload")
        payload_seen = False

        def crash(boundary: str, object_sha: str) -> None:
            nonlocal payload_seen
            if boundary != "AFTER_REMOTE_PUT":
                return
            if object_sha == payload_sha:
                payload_seen = True
            elif payload_seen:
                raise integration.SimulatedPowerLoss()

        value.store.fault = crash
        with self.assertRaises(integration.SimulatedPowerLoss):
            value.prepare(b"payload", "wrapper:stdout", T1)
        rows = [json.loads(path.read_text()) for path in value._receipt_files()]
        self.assertEqual([row["event_kind"] for row in rows], ["HEARTBEAT"])
        self.assertIsNone(value.state["active_transaction"])

    def test_remote_outage_during_read_locks_even_with_valid_local_cache(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"payload", "wrapper:stdout", T1)
        self.assertEqual(value.store._cache_path(broker.sha256(b"payload")).read_bytes(), b"payload")
        self.f.client.outage = "all"
        with self.assertRaisesRegex(broker.BrokerError, "broker locked"):
            value.start(txid, T2)
        self.assertTrue(value.lock_path.exists())

    def test_remote_tamper_locks_and_cache_cannot_mask_it(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"payload", "wrapper:stdout", T1)
        reference = value.store._load_reference(broker.sha256(b"payload"))
        self.f.client.objects[reference.key]["Body"] = b"tamper!"
        self.f.client.objects[reference.key]["Metadata"] = {"sha256": reference.sha256}
        with self.assertRaisesRegex(broker.BrokerError, "broker locked"):
            value.start(txid, T2)
        self.assertTrue(value.lock_path.exists())

    def test_remote_version_mismatch_locks(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"payload", "wrapper:stdout", T1)
        self.f.client.head_version_override = "different-version"
        with self.assertRaisesRegex(broker.BrokerError, "broker locked"):
            value.start(txid, T2)

    def test_corrupt_local_cache_is_repaired_only_after_remote_verification(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"payload", "wrapper:stdout", T1)
        cache = value.store._cache_path(broker.sha256(b"payload"))
        cache.write_bytes(b"local attacker bytes")
        value.start(txid, T2)
        self.assertEqual(cache.read_bytes(), b"payload")

    def test_restart_reverifies_completed_payloads_not_only_receipts(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"payload", "wrapper:stdout", T1)
        value.start(txid, T1)
        value.finish(txid, "DELIVER", T2)
        reference = value.store._load_reference(broker.sha256(b"payload"))
        self.f.client.objects[reference.key]["Body"] = b"tamper!"
        self.f.client.objects[reference.key]["Metadata"] = {"sha256": reference.sha256}
        with self.assertRaisesRegex(integration.RemoteAdapterError, "payload inventory failed"):
            self.f.open()
        self.assertTrue(value.lock_path.exists())

    def test_private_reference_version_tamper_fails_closed(self) -> None:
        value = self.f.primed()
        txid = value.prepare(b"payload", "wrapper:stdout", T1)
        path = value.store._reference_path(broker.sha256(b"payload"))
        row = json.loads(path.read_text())
        row["version_id"] = "forged-version"
        broker.atomic_write(path, broker.canonical_json(row))
        with self.assertRaisesRegex(broker.BrokerError, "broker locked"):
            value.start(txid, T2)

    def test_private_reference_schema_rejects_extra_status_version_and_digest(self) -> None:
        mutations = (
            lambda row: row.update(extra="forbidden"),
            lambda row: row.update(status="OPERATIONAL"),
            lambda row: row.update(version_id=""),
            lambda row: row.update(sha256="not-a-digest"),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                f = Fixture()
                try:
                    value = f.primed()
                    txid = value.prepare(b"payload", "wrapper:stdout", T1)
                    path = value.store._reference_path(broker.sha256(b"payload"))
                    row = json.loads(path.read_text())
                    mutate(row)
                    broker.atomic_write(path, broker.canonical_json(row))
                    with self.assertRaisesRegex(broker.BrokerError, "broker locked"):
                        value.start(txid, T2)
                finally:
                    f.close()

    def test_production_builder_refuses_absent_or_claimed_live_acceptance(self) -> None:
        with self.assertRaisesRegex(integration.RemoteAdapterError, "live accepted.*absent"):
            integration.build_pre_p1_integration(
                self.f.root, self.f.config, self.f.key, self.f.remote,
                acceptance_test=False,
            )
        with self.assertRaisesRegex(integration.RemoteAdapterError, "cannot claim operational"):
            integration.build_pre_p1_integration(
                self.f.root, self.f.config, self.f.key, self.f.remote,
                acceptance_test=False, live_store_acceptance={"claimed": True},
            )
        self.assertFalse((self.f.root / "state.json").exists())
        self.assertFalse((self.f.root / "remote-custody").exists())

    def test_acceptance_mode_rejects_live_claim_and_remains_nonoperational(self) -> None:
        with self.assertRaisesRegex(integration.RemoteAdapterError, "cannot consume"):
            integration.build_pre_p1_integration(
                self.f.root, self.f.config, self.f.key, self.f.remote,
                acceptance_test=True, live_store_acceptance={"claimed": True},
            )
        value = integration.build_pre_p1_integration(
            self.f.root, self.f.config, self.f.key, self.f.remote,
            acceptance_test=True,
        )
        self.assertEqual(value.readiness(T0)["status"], "PRE_P1_NOT_OPERATIONAL")
        self.assertFalse(value.readiness(T0)["operational"])


if __name__ == "__main__":
    unittest.main()
