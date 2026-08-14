#!/usr/bin/env python3
"""Adversarial tests for the PRE-P1 broker-to-custody compiler."""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import compile_benchmark_v15_broker_custody as compiler
import method_v15_delivery_broker as broker


TIMES = [f"2026-08-13T12:{minute:02d}:00Z" for minute in range(10)]
RETAIN = "2028-08-16T00:00:00Z"


def store_config() -> dict:
    return {
        "schema": "c5k4-method-v1.5-s3-object-lock-store-config-1.0",
        "status": "PRE_P1_STORE_ADAPTER_NOT_OPERATIONAL",
        "backend": "AWS_S3_OBJECT_LOCK",
        "bucket": "c5k4-private-custody",
        "expected_bucket_owner": "123456789012",
        "region": "ap-south-1",
        "key_prefix": "private/c5k4/v1.5",
        "kms_key_arn": "arn:aws:kms:ap-south-1:123456789012:key/12345678-1234-1234-1234-123456789abc",
        "bucket_policy_sha256": "1" * 64,
        "benchmark_horizon_utc": "2027-08-15T00:00:00Z",
        "retention_through_utc": RETAIN,
        "required_object_lock_mode": "COMPLIANCE",
        "put_if_absent": True,
        "private_only": True,
    }


class Fixture:
    def __init__(self, *, terminal: str = "DELIVER", close: bool = True, start: bool = True) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.key = Ed25519PrivateKey.generate()
        self.config = broker.test_config(self.root, "broker-test-key")
        self.config["host_id"] = "ai-vps-controlled-harness"
        self.store_config = store_config()
        self.secret = b"TOP SECRET target: conjecture 999"
        self.abandoned = b"PRIVATE partial response"
        self.instance = broker.DeliveryBroker(self.root / "broker", self.config, self.key)
        self.instance.heartbeat(TIMES[0])
        first = self.instance.prepare(self.secret, "model:response", TIMES[1])
        if start:
            self.instance.start(first, TIMES[1])
        if close:
            if not start:
                raise ValueError("a closed fixture must start its transaction")
            self.instance.finish(first, terminal, TIMES[2])
            second = self.instance.prepare(self.abandoned, "tool:stderr", TIMES[2])
            self.instance.start(second, TIMES[2])
            self.instance.finish(second, "ABORT", TIMES[3])
            self.instance.heartbeat(TIMES[4])
        self.objects: dict[tuple[str, str, str], bytes] = {}
        self.inventory = self._inventory(self._receipt_rows())

    @property
    def public_key(self) -> bytes:
        return self.key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

    def _receipt_rows(self) -> list[dict]:
        return [json.loads(path.read_text(encoding="utf-8")) for path in self.instance._receipt_files()]

    def _ref(self, raw: bytes, role: str, sequence: int | None, suffix: str) -> dict:
        object_sha = hashlib.sha256(raw).hexdigest()
        key = f"private/c5k4/v1.5/objects/{object_sha[:2]}/{object_sha}"
        version = f"version-{suffix}"
        ref = {
            "role": role,
            "broker_sequence_number": sequence,
            "bucket": self.store_config["bucket"],
            "key": key,
            "version_id": version,
            "sha256": object_sha,
            "byte_count": len(raw),
            "retain_until_utc": RETAIN,
            "object_lock_mode": "COMPLIANCE",
        }
        self.objects[(ref["bucket"], key, version)] = raw
        return ref

    def _inventory(self, rows: list[dict]) -> dict:
        self.objects = {}
        refs = [
            self._ref(compiler.canonical_json(row), "BROKER_RECEIPT", index, f"receipt-{index}")
            for index, row in enumerate(rows)
        ]
        payloads: dict[str, bytes] = {}
        for row in rows:
            if row["event_kind"] == "PREPARE":
                raw = self.instance.store.get(row["payload_sha256"])
                payloads[row["payload_sha256"]] = raw
        refs.extend(
            self._ref(raw, "DELIVERY_PAYLOAD", None, f"payload-{index}")
            for index, raw in enumerate(payloads.values())
        )
        epoch = {
            "schema": "c5k4-method-v1.5-private-broker-service-epoch-1.0",
            "status": compiler.STATUS,
            "protocol_version": "1.5",
            "visibility": "PRIVATE_TARGET_BEARING",
            "host_id": self.config["host_id"],
            "signing_key_id": self.config["signing_key_id"],
            "signature_algorithm": "Ed25519",
            "service_epoch_id": "a" * 32,
            "broker_config_sha256": compiler.digest(self.config),
            "broker_verification_key_sha256": compiler.sha256(self.public_key),
            "first_broker_sequence": 0,
            "last_broker_sequence": len(rows) - 1,
            "broker_receipt_count": len(rows),
            "first_broker_receipt_sha256": rows[0]["receipt_sha256"],
            "last_broker_receipt_sha256": rows[-1]["receipt_sha256"],
            "opened_at_utc": rows[0]["observed_at_utc"],
            "sealed_at_utc": rows[-1]["observed_at_utc"],
        }
        epoch["binding_sha256"] = compiler.digest(compiler._without(epoch, "binding_sha256", "signature"))
        epoch["signature"] = base64.b64encode(
            self.key.sign(bytes.fromhex(epoch["binding_sha256"]))
        ).decode()
        refs.append(self._ref(compiler.canonical_json(epoch), "SERVICE_EPOCH_BINDING", None, "service-epoch"))
        return compiler.build_private_inventory(self.store_config, refs)

    def read(self, ref: dict) -> bytes:
        return self.objects[(ref["bucket"], ref["key"], ref["version_id"])]

    def compile(self, *, inventory: dict | None = None, state: dict | None = None, key: bytes | None = None) -> dict:
        selected_inventory = inventory or self.inventory
        return compiler.compile_private_custody(
            broker_config=deepcopy(self.config),
            broker_state=deepcopy(state or self.instance.state),
            store_config=deepcopy(self.store_config),
            inventory=deepcopy(selected_inventory),
            broker_verification_key=key or self.public_key,
            custody_signing_key=self.key,
            required_from_utc=TIMES[0],
            required_through_utc=TIMES[4] if self.instance.state["last_heartbeat_utc"] == TIMES[4] else TIMES[1],
            scope_bindings={
                "participant_ledger_sha256": "1" * 64,
                "source_boundary_sha256": "2" * 64,
                "noninterference_receipt_sha256": "3" * 64,
                "store_acceptance_sha256": "4" * 64,
                "service_epoch_binding_sha256": self._service_epoch_binding_sha256(selected_inventory),
            },
            read_object=self.read,
        )

    def _service_epoch_binding_sha256(self, inventory: dict | None = None) -> str:
        ref = next(row for row in (inventory or self.inventory)["objects"] if row["role"] == "SERVICE_EPOCH_BINDING")
        return json.loads(self.read(ref))["binding_sha256"]

    def rewritten_inventory(self, mutation) -> dict:
        rows = self._receipt_rows()
        mutation(rows)
        previous = None
        for sequence, row in enumerate(rows):
            row["sequence_number"] = sequence
            row["previous_receipt_sha256"] = previous
            row["receipt_sha256"] = compiler.digest(compiler._without(row, "receipt_sha256", "signature"))
            row["signature"] = base64.b64encode(
                self.key.sign(bytes.fromhex(row["receipt_sha256"]))
            ).decode()
            previous = row["receipt_sha256"]
        return self._inventory(rows)

    def close(self) -> None:
        self.temp.cleanup()


class CustodyCompilerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = Fixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_complete_deliver_and_abort_chain_compiles_without_raw_bytes(self) -> None:
        output = self.fixture.compile()
        records = output["custody_batches"][0]["records"]
        self.assertEqual(
            [row["event_kind"] for row in records],
            ["HEARTBEAT", "DELIVERY", "ABANDONED_PARTIAL", "HEARTBEAT"],
        )
        self.assertEqual([row["sequence_number"] for row in records], list(range(4)))
        self.assertEqual(
            [row["broker_event_kind"] for row in output["record_bindings"]],
            ["HEARTBEAT", "DELIVER", "ABORT", "HEARTBEAT"],
        )
        encoded = compiler.canonical_json(output)
        self.assertNotIn(self.fixture.secret, encoded)
        self.assertNotIn(self.fixture.abandoned, encoded)
        self.assertNotIn(b'"public', encoded.lower())
        self.assertEqual(output["status"], compiler.STATUS)
        self.assertEqual(output["coverage_certificate"]["status"], "PRE_P1_VERIFIED_CONTRACT_NOT_OPERATIONAL")
        self.assertTrue(output["coverage_certificate"]["complete"])
        compiler.verify_compiler_output(output, self.fixture.public_key)
        tampered = deepcopy(output)
        tampered["object_inventory_sha256"] = "0" * 64
        with self.assertRaisesRegex(compiler.CompilerError, "hash mismatch"):
            compiler.verify_compiler_output(tampered, self.fixture.public_key)

    def test_prepare_only_and_started_restart_fail_closed(self) -> None:
        prepared = Fixture(close=False, start=False)
        try:
            with self.assertRaisesRegex(compiler.CompilerError, "remains PREPARED"):
                prepared.compile()
            prepared.instance.start(prepared.instance.state["active_transaction"]["transaction_id"], TIMES[2])
            prepared.inventory = prepared._inventory(prepared._receipt_rows())
            with self.assertRaisesRegex(compiler.CompilerError, "remains STARTED"):
                prepared.compile()
            locked = deepcopy(prepared.instance.state)
            locked["status"] = "LOCKED_INVALID"
            locked["state_sha256"] = compiler.digest(compiler._without(locked, "state_sha256"))
            with self.assertRaisesRegex(compiler.CompilerError, "LOCKED_INVALID"):
                prepared.compile(state=locked)
        finally:
            prepared.close()

    def test_signed_epoch_splice_and_duplicate_epoch_fail_closed(self) -> None:
        spliced = deepcopy(self.fixture.inventory)
        epoch_ref = next(row for row in spliced["objects"] if row["role"] == "SERVICE_EPOCH_BINDING")
        locator = (epoch_ref["bucket"], epoch_ref["key"], epoch_ref["version_id"])
        epoch = json.loads(self.fixture.objects[locator])
        epoch["last_broker_sequence"] -= 1
        epoch["broker_receipt_count"] -= 1
        epoch["last_broker_receipt_sha256"] = self.fixture._receipt_rows()[-2]["receipt_sha256"]
        epoch["sealed_at_utc"] = self.fixture._receipt_rows()[-2]["observed_at_utc"]
        epoch["binding_sha256"] = compiler.digest(compiler._without(epoch, "binding_sha256", "signature"))
        epoch["signature"] = base64.b64encode(
            self.fixture.key.sign(bytes.fromhex(epoch["binding_sha256"]))
        ).decode()
        raw = compiler.canonical_json(epoch)
        epoch_ref["sha256"] = hashlib.sha256(raw).hexdigest()
        epoch_ref["byte_count"] = len(raw)
        epoch_ref["key"] = f"private/c5k4/v1.5/objects/{epoch_ref['sha256'][:2]}/{epoch_ref['sha256']}"
        epoch_ref["version_id"] += "-spliced"
        self.fixture.objects[(epoch_ref["bucket"], epoch_ref["key"], epoch_ref["version_id"])] = raw
        spliced["inventory_sha256"] = compiler.inventory_digest(spliced)
        with self.assertRaisesRegex(compiler.CompilerError, "does not seal exact broker"):
            self.fixture.compile(inventory=spliced)

        duplicate = deepcopy(self.fixture.inventory)
        second = deepcopy(next(row for row in duplicate["objects"] if row["role"] == "SERVICE_EPOCH_BINDING"))
        second["version_id"] += "-second"
        raw = self.fixture.objects[locator]
        self.fixture.objects[(second["bucket"], second["key"], second["version_id"])] = raw
        duplicate["objects"].append(second)
        duplicate["inventory_sha256"] = compiler.inventory_digest(duplicate)
        with self.assertRaisesRegex(compiler.CompilerError, "duplicate or replayed|exactly one"):
            self.fixture.compile(inventory=duplicate)

    def test_transition_order_is_replayed_not_inferred(self) -> None:
        cases = (
            (lambda rows: rows.__setitem__(1, {**rows[1], "event_kind": "START"}), "lacks its matching"),
            (lambda rows: rows.__setitem__(2, {**rows[2], "event_kind": "DELIVER"}), "occurs without START"),
            (lambda rows: rows.__setitem__(3, {**rows[3], "event_kind": "START"}), "duplicate or out-of-order START"),
            (lambda rows: rows[3].update(transaction_id="f" * 32), "matching active transaction"),
        )
        for mutation, message in cases:
            with self.subTest(message=message):
                inventory = self.fixture.rewritten_inventory(mutation)
                with self.assertRaisesRegex(compiler.CompilerError, message):
                    self.fixture.compile(inventory=inventory)

    def test_completed_transaction_replay_and_heartbeat_gap_fail(self) -> None:
        first_txid = self.fixture._receipt_rows()[1]["transaction_id"]
        replay = self.fixture.rewritten_inventory(
            lambda rows: rows[4].update(transaction_id=first_txid)
        )
        with self.assertRaisesRegex(compiler.CompilerError, "replayed PREPARE"):
            self.fixture.compile(inventory=replay)

        def move_after_gap(rows: list[dict]) -> None:
            for index, value in enumerate(("12:04:01", "12:04:02", "12:04:03", "12:04:04"), 4):
                rows[index]["observed_at_utc"] = f"2026-08-13T{value}Z"

        gap = self.fixture.rewritten_inventory(move_after_gap)
        with self.assertRaisesRegex(compiler.CompilerError, "outside heartbeat coverage"):
            self.fixture.compile(inventory=gap)

    def test_unknown_and_lock_receipts_are_rejected(self) -> None:
        unknown = self.fixture.rewritten_inventory(lambda rows: rows[1].update(event_kind="UNKNOWN"))
        with self.assertRaisesRegex(compiler.CompilerError, "receipt.*validation"):
            self.fixture.compile(inventory=unknown)
        locked = self.fixture.rewritten_inventory(lambda rows: rows[1].update(
            event_kind="LOCK_INVALID", transaction_id=None,
            payload_sha256=broker.EMPTY_SHA256, payload_byte_count=0,
            delivery_channel="broker:control",
        ))
        with self.assertRaisesRegex(compiler.CompilerError, "LOCK_INVALID"):
            self.fixture.compile(inventory=locked)

    def test_receipt_gap_duplicate_replay_and_signature_tamper_fail(self) -> None:
        gap = deepcopy(self.fixture.inventory)
        gap["objects"] = [
            row for row in gap["objects"]
            if not (row["role"] == "BROKER_RECEIPT" and row["broker_sequence_number"] == 1)
        ]
        gap["inventory_sha256"] = compiler.inventory_digest(gap)
        with self.assertRaisesRegex(compiler.CompilerError, "sequence gap"):
            self.fixture.compile(inventory=gap)

        duplicate = deepcopy(self.fixture.inventory)
        duplicate["objects"].append(deepcopy(duplicate["objects"][0]))
        duplicate["inventory_sha256"] = compiler.inventory_digest(duplicate)
        with self.assertRaisesRegex(compiler.CompilerError, "duplicate or replayed"):
            self.fixture.compile(inventory=duplicate)

        rows = self.fixture._receipt_rows()
        rows[1]["signature"] = ("A" if rows[1]["signature"][0] != "A" else "B") + rows[1]["signature"][1:]
        tampered = self.fixture._inventory(rows)
        with self.assertRaisesRegex(compiler.CompilerError, "signature mismatch"):
            self.fixture.compile(inventory=tampered)

    def test_worm_payload_receipt_and_locator_tamper_fail(self) -> None:
        payload = next(row for row in self.fixture.inventory["objects"] if row["role"] == "DELIVERY_PAYLOAD")
        locator = (payload["bucket"], payload["key"], payload["version_id"])
        original = self.fixture.objects[locator]
        self.fixture.objects[locator] = b"tampered"
        with self.assertRaisesRegex(compiler.CompilerError, "digest or byte count"):
            self.fixture.compile()
        self.fixture.objects[locator] = original

        receipt = next(row for row in self.fixture.inventory["objects"] if row["role"] == "BROKER_RECEIPT")
        bad_locator = deepcopy(self.fixture.inventory)
        bad_locator["objects"][0]["version_id"] = "unrecognized-version"
        bad_locator["inventory_sha256"] = compiler.inventory_digest(bad_locator)
        with self.assertRaisesRegex(compiler.CompilerError, "WORM object read failed"):
            self.fixture.compile(inventory=bad_locator)

        early = deepcopy(self.fixture.inventory)
        early["objects"][0]["retain_until_utc"] = "2026-08-13T12:03:59Z"
        early["inventory_sha256"] = compiler.inventory_digest(early)
        with self.assertRaisesRegex(compiler.CompilerError, "retention ends"):
            self.fixture.compile(inventory=early)
        self.assertIsNotNone(receipt)

    def test_key_host_config_state_and_inventory_bindings_are_exact(self) -> None:
        wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        with self.assertRaisesRegex(compiler.CompilerError, "signer is not"):
            self.fixture.compile(key=wrong_key)

        config_bound = deepcopy(self.fixture.inventory)
        config_bound["store_config_sha256"] = "0" * 64
        config_bound["inventory_sha256"] = compiler.inventory_digest(config_bound)
        with self.assertRaisesRegex(compiler.CompilerError, "another store config"):
            self.fixture.compile(inventory=config_bound)

        wrong_state = deepcopy(self.fixture.instance.state)
        wrong_state["last_heartbeat_utc"] = TIMES[3]
        wrong_state["state_sha256"] = compiler.digest(compiler._without(wrong_state, "state_sha256"))
        with self.assertRaisesRegex(compiler.CompilerError, "does not exactly replay"):
            self.fixture.compile(state=wrong_state)

        host_rows = self.fixture._receipt_rows()
        host_rows[0]["host_id"] = "other-host"
        host_rows[0]["receipt_sha256"] = compiler.digest(compiler._without(host_rows[0], "receipt_sha256", "signature"))
        host_rows[0]["signature"] = base64.b64encode(self.fixture.key.sign(bytes.fromhex(host_rows[0]["receipt_sha256"]))).decode()
        host_inventory = self.fixture._inventory(host_rows)
        with self.assertRaisesRegex(compiler.CompilerError, "host/key differs|receipt.*validation"):
            self.fixture.compile(inventory=host_inventory)

    def test_unused_payload_reference_and_noncanonical_receipt_fail(self) -> None:
        extra = deepcopy(self.fixture.inventory)
        raw = b"never referenced target"
        extra["objects"].append(self.fixture._ref(raw, "DELIVERY_PAYLOAD", None, "extra"))
        extra["inventory_sha256"] = compiler.inventory_digest(extra)
        with self.assertRaisesRegex(compiler.CompilerError, "unused or duplicate payload"):
            self.fixture.compile(inventory=extra)

        receipt_ref = next(row for row in self.fixture.inventory["objects"] if row["role"] == "BROKER_RECEIPT")
        old_locator = (receipt_ref["bucket"], receipt_ref["key"], receipt_ref["version_id"])
        noncanonical = json.dumps(json.loads(self.fixture.objects[old_locator]), indent=2).encode()
        changed = deepcopy(self.fixture.inventory)
        changed_ref = next(row for row in changed["objects"] if row["role"] == "BROKER_RECEIPT" and row["broker_sequence_number"] == 0)
        changed_ref["sha256"] = hashlib.sha256(noncanonical).hexdigest()
        changed_ref["byte_count"] = len(noncanonical)
        changed_ref["key"] = f"private/c5k4/v1.5/objects/{changed_ref['sha256'][:2]}/{changed_ref['sha256']}"
        changed_ref["version_id"] += "-noncanonical"
        self.fixture.objects[(changed_ref["bucket"], changed_ref["key"], changed_ref["version_id"])] = noncanonical
        changed["inventory_sha256"] = compiler.inventory_digest(changed)
        with self.assertRaisesRegex(compiler.CompilerError, "not canonical JSON"):
            self.fixture.compile(inventory=changed)


if __name__ == "__main__":
    unittest.main()
