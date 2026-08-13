#!/usr/bin/env python3
"""Adversarial tests for the isolated PRE-P1 controlled-delivery broker."""

from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import method_v15_delivery_broker as broker


T0 = "2026-08-13T12:00:00Z"
T1 = "2026-08-13T12:01:00Z"
T2 = "2026-08-13T12:02:00Z"
T3 = "2026-08-13T12:03:00Z"
T5 = "2026-08-13T12:05:00Z"


class Fixture:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.key = Ed25519PrivateKey.generate()
        self.available = True
        self.config = broker.test_config(self.root)

    def open(self) -> broker.DeliveryBroker:
        return broker.DeliveryBroker(self.root, copy.deepcopy(self.config), self.key, store_available=lambda: self.available)

    def close(self) -> None:
        self.temp.cleanup()


class DeliveryBrokerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.f = Fixture()

    def tearDown(self) -> None:
        self.f.close()

    def primed(self) -> broker.DeliveryBroker:
        instance = self.f.open()
        instance.heartbeat(T0)
        return instance

    def test_prepare_start_deliver_is_signed_monotonic_and_durable(self) -> None:
        instance = self.primed()
        txid = instance.prepare(b"secret target bytes", "wrapper:stdout", T1)
        instance.start(txid, T1)
        self.assertEqual(instance.finish(txid, "DELIVER", T2), b"secret target bytes")
        reopened = self.f.open()
        self.assertEqual(reopened.state["sequence_number"], 3)
        self.assertIsNone(reopened.state["active_transaction"])
        rows = [json.loads(path.read_text()) for path in reopened._receipt_files()]
        self.assertEqual([row["event_kind"] for row in rows], ["HEARTBEAT", "PREPARE", "START", "DELIVER"])
        self.assertEqual(rows[-1]["previous_receipt_sha256"], rows[-2]["receipt_sha256"])

    def test_crash_after_blob_leaves_no_started_delivery(self) -> None:
        instance = self.primed()
        with self.assertRaises(broker.SimulatedCrash):
            instance.prepare(b"orphan is safe", "wrapper:stdout", T1, crash="AFTER_BLOB")
        reopened = self.f.open()
        self.assertIsNone(reopened.state["active_transaction"])
        self.assertEqual(reopened.state["sequence_number"], 0)

    def test_crash_after_prepare_receipt_recovers_prepared_state(self) -> None:
        instance = self.primed()
        with self.assertRaises(broker.SimulatedCrash):
            instance.prepare(b"captured", "wrapper:stdout", T1, crash="AFTER_RECEIPT")
        reopened = self.f.open()
        self.assertEqual(reopened.state["active_transaction"]["phase"], "PREPARED")

    def test_crash_after_start_receipt_locks_indeterminate_delivery(self) -> None:
        instance = self.primed()
        txid = instance.prepare(b"captured", "wrapper:stdout", T1)
        with self.assertRaises(broker.SimulatedCrash):
            instance.start(txid, T2, crash="AFTER_RECEIPT")
        with self.assertRaisesRegex(broker.BrokerError, "LOCKED_INVALID"):
            self.f.open()
        self.assertTrue(instance.lock_path.exists())

    def test_crash_after_deliver_receipt_recovers_finalized_state(self) -> None:
        instance = self.primed()
        txid = instance.prepare(b"captured", "wrapper:stdout", T1)
        instance.start(txid, T1)
        with self.assertRaises(broker.SimulatedCrash):
            instance.finish(txid, "DELIVER", T2, crash="AFTER_RECEIPT")
        reopened = self.f.open()
        self.assertIsNone(reopened.state["active_transaction"])
        self.assertEqual(reopened.state["sequence_number"], 3)

    def test_state_rollback_is_repaired_from_receipt_chain(self) -> None:
        instance = self.primed()
        old_state = instance.state_path.read_bytes()
        instance.prepare(b"captured", "wrapper:stdout", T1)
        broker.atomic_write(instance.state_path, old_state)
        reopened = self.f.open()
        self.assertEqual(reopened.state["sequence_number"], 1)
        self.assertEqual(reopened.state["active_transaction"]["phase"], "PREPARED")

    def test_receipt_fork_or_tamper_sticky_locks(self) -> None:
        instance = self.primed()
        txid = instance.prepare(b"captured", "wrapper:stdout", T1)
        receipt = instance.receipts / "00000000000000000001.json"
        row = json.loads(receipt.read_text())
        row["transaction_id"] = "0" * 32
        broker.atomic_write(receipt, broker.canonical_json(row))
        with self.assertRaisesRegex(broker.BrokerError, "LOCKED_INVALID"):
            self.f.open()
        self.assertTrue(instance.lock_path.exists())
        with self.assertRaisesRegex(broker.BrokerError, "LOCKED_INVALID"):
            instance.start(txid, T2)

    def test_missing_trailing_receipt_detected_from_durable_state(self) -> None:
        instance = self.primed()
        instance.prepare(b"captured", "wrapper:stdout", T1)
        (instance.receipts / "00000000000000000001.json").unlink()
        with self.assertRaisesRegex(broker.BrokerError, "LOCKED_INVALID"):
            self.f.open()

    def test_blob_deletion_and_tamper_lock(self) -> None:
        for mutation in ("delete", "tamper"):
            with self.subTest(mutation=mutation):
                f = Fixture()
                try:
                    instance = f.open()
                    instance.heartbeat(T0)
                    txid = instance.prepare(b"captured", "wrapper:stdout", T1)
                    object_path = instance.store.path(broker.sha256(b"captured"))
                    if mutation == "delete":
                        object_path.unlink()
                    else:
                        object_path.write_bytes(b"changed")
                    with self.assertRaisesRegex(broker.BrokerError, "broker locked"):
                        instance.start(txid, T2)
                    self.assertTrue(instance.lock_path.exists())
                finally:
                    f.close()

    def test_store_outage_locks_before_prepare_receipt(self) -> None:
        instance = self.primed()
        self.f.available = False
        with self.assertRaisesRegex(broker.BrokerError, "store write failed"):
            instance.prepare(b"never delivered", "wrapper:stdout", T1)
        self.assertTrue(instance.lock_path.exists())

    def test_stale_heartbeat_locks_at_241_seconds(self) -> None:
        instance = self.primed()
        with self.assertRaisesRegex(broker.BrokerError, "heartbeat stale"):
            instance.prepare(b"never delivered", "wrapper:stdout", "2026-08-13T12:04:01Z")
        self.assertTrue(instance.lock_path.exists())

    def test_unwrapped_delivery_locks(self) -> None:
        instance = self.primed()
        with self.assertRaisesRegex(broker.BrokerError, "requires the current START"):
            instance.finish("0" * 32, "DELIVER", T1)
        self.assertTrue(instance.lock_path.exists())

    def test_sink_failure_aborts(self) -> None:
        instance = self.primed()
        txid = instance.prepare(b"captured", "wrapper:stdout", T1)
        instance.start(txid, T1)
        with self.assertRaisesRegex(RuntimeError, "sink failed"):
            instance.deliver_to(txid, lambda _: (_ for _ in ()).throw(RuntimeError("sink failed")), T2)
        self.assertIsNone(instance.state["active_transaction"])
        last = json.loads(instance._receipt_files()[-1].read_text())
        self.assertEqual(last["event_kind"], "ABORT")

    def test_subprocess_stdin_stdout_stderr_are_all_wrapped(self) -> None:
        instance = self.primed()
        result = instance.run_subprocess([sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read()[::-1]); sys.stderr.buffer.write(b'warning')"], b"abc", T1)
        self.assertEqual(result.stdout, b"cba")
        self.assertEqual(result.stderr, b"warning")
        rows = [json.loads(path.read_text()) for path in instance._receipt_files()]
        self.assertEqual([row["event_kind"] for row in rows], ["HEARTBEAT", "PREPARE", "START", "DELIVER", "PREPARE", "START", "DELIVER", "PREPARE", "START", "DELIVER"])
        prepares = [row for row in rows if row["event_kind"] == "PREPARE"]
        self.assertEqual([row["delivery_channel"] for row in prepares], ["subprocess:stdin", "subprocess:stdout", "subprocess:stderr"])
        self.assertEqual(instance.store.get(prepares[-1]["payload_sha256"]), b"warning")

    def test_readiness_is_target_blind_and_permanently_pre_p1(self) -> None:
        instance = self.primed()
        txid = instance.prepare(b"TOP SECRET CONJECTURE 999", "wrapper:stdout", T1)
        instance.start(txid, T1)
        instance.finish(txid, "DELIVER", T2)
        readiness = instance.readiness(T3)
        raw = broker.canonical_json(readiness)
        self.assertNotIn(b"TOP SECRET", raw)
        self.assertNotIn(b"payload", raw)
        self.assertEqual(readiness["status"], "PRE_P1_NOT_OPERATIONAL")
        self.assertFalse(readiness["operational"])
        self.assertEqual(set(readiness["reasons"]), {"PRODUCTION_STORE_UNSET", "HOST_KEY_NOT_ACCEPTED", "DEDICATED_SERVICE_NOT_ACCEPTED", "ACCEPTANCE_SUITE_NOT_FROZEN"})

    def test_readiness_reports_stale_and_locked_without_private_metadata(self) -> None:
        instance = self.primed()
        instance._lock("private failure detail")
        readiness = instance.readiness(T5)
        self.assertIn("HEARTBEAT_STALE", readiness["reasons"])
        self.assertIn("LOCKED_INVALID", readiness["reasons"])
        raw = broker.canonical_json(readiness)
        for forbidden in (b"private failure detail", b"delivery_channel", b"transaction_id", b"signature"):
            self.assertNotIn(forbidden, raw)

    def test_config_cannot_claim_production_or_acceptance(self) -> None:
        for mutate in (
            lambda value: value["store"].update(production_locator="s3://claimed"),
            lambda value: value["service_acceptance"].update(dedicated_service_installed=True),
            lambda value: value.update(status="OPERATIONAL"),
        ):
            config = copy.deepcopy(self.f.config)
            mutate(config)
            with self.assertRaises(broker.BrokerError):
                broker.DeliveryBroker(self.f.root, config, self.f.key)


if __name__ == "__main__":
    unittest.main()
