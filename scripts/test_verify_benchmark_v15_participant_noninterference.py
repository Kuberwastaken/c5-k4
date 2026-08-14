#!/usr/bin/env python3
"""Positive and adversarial tests for the controlled-harness boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


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

    def test_committed_artifacts_are_valid_but_inert(self) -> None:
        result = module.verify(self.ledger, self.receipt)
        self.assertTrue(result["valid"])
        self.assertFalse(result["activation_permitted"])

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


if __name__ == "__main__":
    unittest.main()
