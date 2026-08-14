#!/usr/bin/env python3
"""Positive and adversarial tests for the controlled-harness boundary."""

from __future__ import annotations

import base64
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_benchmark_v15_participant_noninterference.py"
SPEC = importlib.util.spec_from_file_location("verify_participant_noninterference", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)
PROTOCOL = ROOT / "results" / "benchmark" / "v1.5-protocol"


class ParticipantNoninterferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = module.load_object(PROTOCOL / "participant-ledger.json")
        cls.receipt = module.load_object(PROTOCOL / "noninterference-receipt.json")

    @staticmethod
    def rehash(ledger: dict, receipt: dict) -> None:
        ledger["ledger_sha256"] = module.canonical_digest(ledger, "ledger_sha256")
        receipt["participant_ledger_sha256"] = ledger["ledger_sha256"]
        receipt["receipt_sha256"] = module.canonical_digest(receipt, "receipt_sha256")

    def mutate(self) -> tuple[dict, dict]:
        return copy.deepcopy(self.ledger), copy.deepcopy(self.receipt)

    def operational_fixture(self) -> tuple[dict, bytes]:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        receipt = {
            "schema": "c5k4-method-v1.5-operational-noninterference-receipt-1.0",
            "status": "FROZEN_P1_NONINTERFERENCE_LIVE_ACCEPTED",
            "protocol_version": "1.5",
            "host_id": "ai-vps-controlled-harness",
            "participant_ledger_sha256": self.ledger["ledger_sha256"],
            "source_boundary_sha256": "b" * 64,
            "signing_key_id": "future-target-blind-key-1",
            "service_epoch_binding_sha256": "c" * 64,
            "verification_key_sha256": module.hashlib.sha256(public_key).hexdigest(),
            "signature_algorithm": "Ed25519",
            "unjournaled_delivery_detected": False,
            "proofs": {
                "dedicated_nonlogin_identity": True,
                "root_owned_read_only_p1_checkout": True,
                "private_root_permissions": True,
                "private_socket_permissions": True,
                "credential_isolation": True,
                "network_default_deny": True,
                "allowed_endpoint_enforcement": True,
                "excluded_process_denial": True,
                "unbroken_ingress_custody": True,
                "destructive_gap_acceptance": True,
            },
            "blockers": [],
            "scope_complete": True,
            "operational_ready": True,
            "activation_permitted": True,
            "claims": {"p1_frozen": True, "operational_capture": True, "production_ready": True, "target_specific": False},
        }
        receipt["receipt_sha256"] = module.operational_receipt_digest(receipt)
        receipt["signature"] = base64.b64encode(
            private_key.sign(bytes.fromhex(receipt["receipt_sha256"]))
        ).decode()
        return receipt, public_key

    def test_committed_artifacts_are_valid_but_inert(self) -> None:
        result = module.verify(self.ledger, self.receipt)
        self.assertTrue(result["valid"])
        self.assertFalse(result["activation_permitted"])
        self.assertIsNone(self.receipt["source_boundary_sha256"])
        self.assertIsNone(self.receipt["signing_key_id"])
        self.assertIsNone(self.receipt["service_epoch_binding_sha256"])
        self.assertFalse(self.receipt["unjournaled_delivery_detected"])

    def test_no_human_or_model_participant_exists(self) -> None:
        serialized = json.dumps(self.ledger)
        self.assertEqual(self.ledger["model_endpoints"], [])
        for forbidden in ("HUMAN", "CODEX_MODEL", "CLAUDE_MODEL"):
            self.assertNotIn(forbidden, self.ledger["participants"])

    def test_model_or_human_insertion_fails_even_after_rehash(self) -> None:
        for endpoint in ("stock-codex", "claude", "human:kuber"):
            ledger, receipt = self.mutate()
            ledger["model_endpoints"] = [endpoint]
            self.rehash(ledger, receipt)
            with self.assertRaises(module.BoundaryError):
                module.verify(ledger, receipt)

    def test_participant_substitution_and_channel_injection_fail(self) -> None:
        ledger, receipt = self.mutate()
        ledger["participants"][-1] = "STOCK_CODEX"
        self.rehash(ledger, receipt)
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)
        ledger, receipt = self.mutate()
        ledger["channels"].append({"channel_id": "LOCAL_RELAY", "payload_class": "CONTROL", "captured_before_delivery": True})
        self.rehash(ledger, receipt)
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_unregistered_ingress_cannot_be_downgraded_to_unknown(self) -> None:
        ledger, receipt = self.mutate()
        ledger["failure_policy"]["missing_ingress_proof"] = "UNKNOWN"
        self.rehash(ledger, receipt)
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_proved_external_noninterference_is_not_an_evidence_unit(self) -> None:
        self.assertEqual(self.ledger["failure_policy"]["proved_external_noninterference"], "NO_EVIDENCE_UNIT")
        ledger, receipt = self.mutate()
        ledger["failure_policy"]["proved_external_noninterference"] = "IMMUTABLE_SOURCE_CUSTODY"
        self.rehash(ledger, receipt)
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_target_identity_result_and_semantics_fields_fail(self) -> None:
        for key in ("target_id", "statement_text", "result", "ranking"):
            ledger, receipt = self.mutate()
            ledger[key] = "forbidden"
            self.rehash(ledger, receipt)
            with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_proof_or_activation_claim_fails(self) -> None:
        ledger, receipt = self.mutate()
        receipt["proofs"]["network_default_deny"] = True
        self.rehash(ledger, receipt)
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_premature_binding_and_unjournaled_delivery_fail(self) -> None:
        for key, value in (
            ("source_boundary_sha256", "a" * 64),
            ("signing_key_id", "pre-p1-key"),
            ("service_epoch_binding_sha256", "b" * 64),
            ("unjournaled_delivery_detected", True),
        ):
            ledger, receipt = self.mutate()
            receipt[key] = value
            self.rehash(ledger, receipt)
            with self.assertRaises(module.BoundaryError):
                module.verify(ledger, receipt)
        ledger, receipt = self.mutate()
        receipt["activation_permitted"] = True
        self.rehash(ledger, receipt)
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_digest_tampering_and_cross_ledger_replay_fail(self) -> None:
        ledger, receipt = self.mutate()
        ledger["host_id"] = "different-host"
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)
        ledger, receipt = self.mutate()
        receipt["participant_ledger_sha256"] = "f" * 64
        receipt["receipt_sha256"] = module.canonical_digest(receipt, "receipt_sha256")
        with self.assertRaises(module.BoundaryError): module.verify(ledger, receipt)

    def test_cli_is_silent_and_fail_closed(self) -> None:
        completed = subprocess.run([sys.executable, str(MODULE_PATH)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary) / "bad.json"
            bad.write_text("{}\n", encoding="utf-8")
            completed = subprocess.run([sys.executable, str(MODULE_PATH), "--ledger", str(bad)], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.stderr, "")

    def test_future_operational_schema_is_valid_but_has_no_committed_artifact(self) -> None:
        schema = module.load_object(
            ROOT / "schemas" / "benchmark-operational-noninterference-receipt-v1.5.schema.json"
        )
        Draft7Validator.check_schema(schema)
        self.assertFalse((PROTOCOL / "operational-noninterference-receipt.json").exists())

    def test_generated_future_operational_receipt_requires_authentic_signature(self) -> None:
        receipt, public_key = self.operational_fixture()
        result = module.verify_operational(self.ledger, "b" * 64, receipt, public_key)
        self.assertTrue(result["activation_permitted"])
        tampered = copy.deepcopy(receipt)
        tampered["service_epoch_binding_sha256"] = "d" * 64
        with self.assertRaises(module.BoundaryError):
            module.verify_operational(self.ledger, "b" * 64, tampered, public_key)
        wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
        with self.assertRaises(module.BoundaryError):
            module.verify_operational(self.ledger, "b" * 64, receipt, wrong_key)

    def test_future_operational_receipt_fails_closed_on_every_readiness_relaxation(self) -> None:
        receipt, public_key = self.operational_fixture()
        for field in receipt["proofs"]:
            mutated = copy.deepcopy(receipt)
            mutated["proofs"][field] = False
            with self.assertRaises(module.BoundaryError):
                module.verify_operational(self.ledger, "b" * 64, mutated, public_key)
        for field, value in (
            ("blockers", ["NOT_READY"]),
            ("scope_complete", False),
            ("operational_ready", False),
            ("activation_permitted", False),
            ("unjournaled_delivery_detected", True),
        ):
            mutated = copy.deepcopy(receipt)
            mutated[field] = value
            with self.assertRaises(module.BoundaryError):
                module.verify_operational(self.ledger, "b" * 64, mutated, public_key)


if __name__ == "__main__":
    unittest.main()
