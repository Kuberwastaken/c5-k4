#!/usr/bin/env python3
"""Adversarial tests for the target-blind destructive-gap evidence compiler."""

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
SCRIPT = ROOT / "scripts/compile_benchmark_v15_destructive_gap_evidence.py"
SPEC = importlib.util.spec_from_file_location("compile_v15_gap_evidence", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class DestructiveGapEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.key = Ed25519PrivateKey.generate()
        self.public = self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.plan = "1" * 64
        self.epoch = "2" * 64

    def commitment(self) -> dict:
        value = {
            "schema": "c5k4-method-v1.5-operational-noninterference-key-commitment-1.0",
            "status": "FROZEN_P1_NONINTERFERENCE_KEY_COMMITTED", "protocol_version": "1.5",
            "host_id": "ai-vps-controlled-harness", "signing_key_id": "p1-gap-key",
            "signature_algorithm": "Ed25519", "verification_key_sha256": __import__("hashlib").sha256(self.public).hexdigest(),
            "operational": True, "activation_permitted": True, "target_specific": False,
            "commitment_sha256": module.ZERO,
        }
        value["commitment_sha256"] = module.digest_object(value, "commitment_sha256")
        return value

    def bundle(self, *, live: bool = True, passed: bool = True) -> dict:
        commitment = self.commitment()
        rows = []
        for index, test in enumerate(module.TESTS):
            row = {
                "schema": "c5k4-method-v1.5-destructive-gap-evidence-1.0",
                "execution_context": "LIVE_CONTROLLED_HARNESS" if live else "FIXTURE_NONOPERATIONAL",
                "test": test,
                "request_sha256": format(index + 3, "x") * 64,
                "result_sha256": format(index + 9, "x") * 64,
                "pre_state_sha256": format(index + 1, "x") * 64,
                "post_state_sha256": format(index + 2, "x") * 64,
                "committed_plan_sha256": self.plan,
                "service_epoch_binding_sha256": self.epoch,
                "signing_key_id": commitment["signing_key_id"],
                "verification_key_sha256": commitment["verification_key_sha256"],
                "signature_algorithm": "Ed25519", "observed_at_utc": f"2026-08-14T00:00:{index:02d}Z",
                "passed": passed, "evidence_sha256": module.ZERO, "signature": "",
            }
            row["evidence_sha256"] = module.digest_object(row, "evidence_sha256", "signature")
            row["signature"] = base64.b64encode(self.key.sign(bytes.fromhex(row["evidence_sha256"]))).decode()
            rows.append(row)
        bundle = {
            "schema": "c5k4-method-v1.5-destructive-gap-evidence-bundle-1.0",
            "status": "LIVE_CONTROLLED_HARNESS_EVIDENCE" if live else "FIXTURE_EVIDENCE_NONOPERATIONAL",
            "protocol_version": "1.5", "host_id": "ai-vps-controlled-harness",
            "committed_plan_sha256": self.plan, "service_epoch_binding_sha256": self.epoch,
            "key_commitment": commitment, "evidence": rows, "target_specific": False,
            "bundle_sha256": module.ZERO,
        }
        self.reseal_bundle(bundle)
        return bundle

    def resign_row(self, row: dict) -> None:
        row["evidence_sha256"] = module.digest_object(row, "evidence_sha256", "signature")
        row["signature"] = base64.b64encode(self.key.sign(bytes.fromhex(row["evidence_sha256"]))).decode()

    def reseal_bundle(self, bundle: dict) -> None:
        bundle["bundle_sha256"] = module.digest_object(bundle, "bundle_sha256")

    def test_authentic_live_six_test_closure_compiles_operational(self) -> None:
        evidence = self.bundle()
        output = module.compile_evidence(evidence, self.public)
        self.assertEqual(output["status"], "OPERATIONAL_DESTRUCTIVE_GAP_ACCEPTANCE_PASSED")
        self.assertEqual(output["tests"], list(module.TESTS))
        self.assertEqual(output["committed_plan_sha256"], self.plan)
        self.assertEqual(output["service_epoch_binding_sha256"], self.epoch)
        self.assertEqual(output["signing_key_id"], evidence["key_commitment"]["signing_key_id"])
        self.assertEqual(output["verification_key_sha256"], evidence["key_commitment"]["verification_key_sha256"])
        self.assertEqual(output["evidence_bundle_sha256"], evidence["bundle_sha256"])
        self.assertTrue(output["all_passed"]); self.assertTrue(output["operational"]); self.assertTrue(output["activation_permitted"])
        self.assertEqual(output["acceptance_sha256"], module.digest_object(output, "acceptance_sha256"))

    def test_signed_fixture_can_never_emit_operational_acceptance(self) -> None:
        output = module.compile_evidence(self.bundle(live=False), self.public)
        self.assertEqual(output["status"], "FIXTURE_DESTRUCTIVE_GAP_EVIDENCE_VERIFIED_NONOPERATIONAL")
        self.assertTrue(output["all_passed"])
        self.assertFalse(output["operational"]); self.assertFalse(output["activation_permitted"])

    def test_schemas_are_valid_and_compiled_provenance_is_required(self) -> None:
        for path in (module.INPUT_SCHEMA, module.OUTPUT_SCHEMA):
            Draft7Validator.check_schema(module.load_object(path))
        output_schema = module.load_object(module.OUTPUT_SCHEMA)
        output = module.compile_evidence(self.bundle(), self.public)
        Draft7Validator(output_schema).validate(output)
        for field in ("committed_plan_sha256", "service_epoch_binding_sha256", "signing_key_id", "verification_key_sha256", "evidence_bundle_sha256"):
            missing = copy.deepcopy(output); missing.pop(field)
            self.assertTrue(list(Draft7Validator(output_schema).iter_errors(missing)), field)

    def test_compiled_provenance_is_covered_by_acceptance_digest(self) -> None:
        output = module.compile_evidence(self.bundle(), self.public)
        for field in ("committed_plan_sha256", "service_epoch_binding_sha256", "verification_key_sha256", "evidence_bundle_sha256"):
            tampered = copy.deepcopy(output); tampered[field] = "f" * 64
            self.assertNotEqual(tampered["acceptance_sha256"], module.digest_object(tampered, "acceptance_sha256"))
        tampered = copy.deepcopy(output); tampered["signing_key_id"] = "different-key"
        self.assertNotEqual(tampered["acceptance_sha256"], module.digest_object(tampered, "acceptance_sha256"))

    def test_missing_duplicate_or_reordered_test_fails(self) -> None:
        for mutate in (
            lambda rows: rows.pop(),
            lambda rows: rows.__setitem__(1, copy.deepcopy(rows[0])),
            lambda rows: rows.reverse(),
        ):
            value = self.bundle(); mutate(value["evidence"]); self.reseal_bundle(value)
            with self.assertRaisesRegex(module.GapEvidenceError, "schema failure"):
                module.compile_evidence(value, self.public)

    def test_plan_epoch_and_key_bindings_fail_closed(self) -> None:
        for field, message in (("committed_plan_sha256", "committed gap plan"), ("service_epoch_binding_sha256", "service epoch"), ("signing_key_id", "committed signing key")):
            value = self.bundle(); row = value["evidence"][0]
            row[field] = "f" * 64 if field.endswith("sha256") else "other-key"
            self.resign_row(row); self.reseal_bundle(value)
            with self.assertRaisesRegex(module.GapEvidenceError, message):
                module.compile_evidence(value, self.public)

    def test_request_result_pre_post_are_signed(self) -> None:
        for field in ("request_sha256", "result_sha256", "pre_state_sha256", "post_state_sha256"):
            value = self.bundle(); value["evidence"][0][field] = "f" * 64; self.reseal_bundle(value)
            with self.assertRaisesRegex(module.GapEvidenceError, "self-digest mismatch"):
                module.compile_evidence(value, self.public)

    def test_signature_tamper_wrong_key_and_commitment_tamper_fail(self) -> None:
        value = self.bundle(); value["evidence"][0]["signature"] = "A" * 86 + "=="; self.reseal_bundle(value)
        with self.assertRaisesRegex(module.GapEvidenceError, "signature mismatch"):
            module.compile_evidence(value, self.public)
        wrong = Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with self.assertRaisesRegex(module.GapEvidenceError, "does not match"):
            module.compile_evidence(self.bundle(), wrong)
        value = self.bundle(); value["key_commitment"]["signing_key_id"] = "changed"; self.reseal_bundle(value)
        with self.assertRaisesRegex(module.GapEvidenceError, "commitment self-digest"):
            module.compile_evidence(value, self.public)

    def test_live_failure_cannot_compile_but_fixture_failure_stays_nonoperational(self) -> None:
        with self.assertRaisesRegex(module.GapEvidenceError, "failed test"):
            module.compile_evidence(self.bundle(passed=False), self.public)
        output = module.compile_evidence(self.bundle(live=False, passed=False), self.public)
        self.assertFalse(output["all_passed"]); self.assertFalse(output["operational"])

    def test_replayed_request_or_result_fails(self) -> None:
        for field, message in (("request_sha256", "request replay"), ("result_sha256", "result replay")):
            value = self.bundle(); value["evidence"][1][field] = value["evidence"][0][field]
            self.resign_row(value["evidence"][1]); self.reseal_bundle(value)
            with self.assertRaisesRegex(module.GapEvidenceError, message):
                module.compile_evidence(value, self.public)

    def test_target_fields_are_rejected(self) -> None:
        value = self.bundle(); value["evidence"][0]["target_id"] = "forbidden"; self.reseal_bundle(value)
        with self.assertRaisesRegex(module.GapEvidenceError, "schema failure"):
            module.compile_evidence(value, self.public)

    def test_cli_is_stdout_only_deterministic_and_silent_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); evidence = root / "evidence.json"; key = root / "key.raw"
            evidence.write_text(json.dumps(self.bundle()), encoding="utf-8"); key.write_bytes(self.public)
            command = [sys.executable, str(SCRIPT), "--evidence", str(evidence), "--verification-key", str(key)]
            first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0); self.assertEqual(first.stderr, ""); self.assertEqual(first.stdout, second.stdout)
            evidence.write_text("{}", encoding="utf-8")
            failed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(failed.returncode, 2); self.assertEqual(failed.stdout, ""); self.assertEqual(failed.stderr, "")


if __name__ == "__main__":
    unittest.main()
