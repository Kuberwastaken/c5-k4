#!/usr/bin/env python3
"""Adversarial tests for the inert Method v1.5 checkpoint runner boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("run_benchmark_v15_checkpoint.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v15_runner", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)
H = "a" * 64


class RunnerBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="v15-runner-")
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, value: object) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def ref(self, path: Path) -> dict[str, str]:
        return {"path": str(path.resolve()), "sha256": R.sha256_file(path)}

    def proof(self) -> dict:
        return {"proof_sha256": "9" * 64}

    def private_input(self) -> tuple[dict, list[Path]]:
        files = [self.write(f"private-{i}.json", {"private": i}) for i in range(5)]
        isolated = self.root / "isolated"
        isolated.mkdir()
        value = {
            "schema": R.PRIVATE_INPUT_SCHEMA,
            "status": "PRIVATE_CUSTODY_READY",
            "runner_contract": {
                "mode": "CAPTURE",
                "runner_path": "scripts/run_benchmark_v15_checkpoint.py",
                "invocation_contract_path": "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json",
                "private_input_argument": "--private-input",
            },
            "checkpoint": {
                "scheduled_for_utc": "2026-08-14T00:17:00Z",
                "public_chain_proof_sha256": "9" * 64,
            },
            "custody": {
                "coverage_certificate": self.ref(files[0]),
                "public_sealed_binding": self.ref(files[1]),
                "source_boundary_status": "FROZEN_P1_EXECUTABLE",
            },
            "registry": {
                "private_registry": self.ref(files[2]),
                "provenance_content_pack": self.ref(files[3]),
                "provenance_ledgers": [self.ref(files[4])],
            },
            "replay": {
                "isolated_repository": str(isolated.resolve()),
                "fresh_reacquisition_completed": True,
                "network_acquisition_by_runner": False,
            },
        }
        return value, files

    def test_current_pre_p1_contract_is_silent_and_writes_nothing(self) -> None:
        output = self.root / "publication"
        code = R.main([
            "--contract", str(R.ROOT / "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json"),
            "--u1-receipt", str(self.root / "absent-u1.json"),
            "--scheduled-for-utc", "2026-08-14T00:17:00Z",
            "--event-name", "schedule", "--run-attempt", "1",
            "--public-chain-proof", str(self.root / "absent-proof.json"),
            "--public-repository", str(R.ROOT), "--output", str(output),
        ])
        self.assertEqual(code, 2)
        self.assertFalse(output.exists())

    def test_parser_rejects_missing_or_unknown_argument_without_system_exit(self) -> None:
        self.assertEqual(R.main([]), 2)
        self.assertEqual(R.main(["--unknown"]), 2)

    def test_publication_allowlist_rejects_extra_file(self) -> None:
        values = {name: {"schema": "c5k4-method-v1.5-fixture"} for name in R.PUBLIC_FILES}
        values["private.json"] = {"records": []}
        with self.assertRaisesRegex(R.RunnerError, "allowlist"):
            R.publish(self.root / "out", values)
        self.assertFalse((self.root / "out").exists())

    def test_publication_rejects_identity_field_atomically(self) -> None:
        values = {name: {"schema": "c5k4-method-v1.5-fixture"} for name in R.PUBLIC_FILES}
        values["receipt.json"]["cluster_id"] = "secret"
        with self.assertRaisesRegex(R.RunnerError, "forbidden"):
            R.publish(self.root / "out", values)
        self.assertFalse((self.root / "out").exists())

    def test_terminal_certificate_and_manifest_are_strict_and_target_blind(self) -> None:
        certificate = R._terminal_certificate("2026-08-14T00:17:00Z", self.proof())
        receipt = {
            "schema": "c5k4-method-v1.5-chronology-receipt-1.0",
            "status": "INVALID_CHRONOLOGY_CAPTURE",
        }
        manifest = R._publication_manifest(
            "2026-08-14T00:17:00Z", "TERMINAL_CHRONOLOGY_GAP", certificate, receipt
        )
        self.assertEqual(certificate["certificate_sha256"], R.content_digest(certificate, "certificate_sha256"))
        self.assertEqual(manifest["manifest_sha256"], R.content_digest(manifest, "manifest_sha256"))
        for value in (certificate, receipt, manifest):
            R.assert_no_public_secrets(value)

    def test_manifest_schema_rejects_extra_property(self) -> None:
        certificate = R._terminal_certificate("2026-08-14T00:17:00Z", self.proof())
        receipt = {"schema": "c5k4-method-v1.5-chronology-receipt-1.0"}
        manifest = R._publication_manifest("2026-08-14T00:17:00Z", "TERMINAL_CHRONOLOGY_GAP", certificate, receipt)
        manifest["target_identity"] = "leak"
        with self.assertRaises(R.RunnerError):
            R.validate_schema(manifest, "benchmark-checkpoint-publication-manifest-v1.5.schema.json", "manifest")

    def test_private_manifest_rejects_wrong_tick_before_private_file_reads(self) -> None:
        value, _ = self.private_input()
        path = self.write("private-input.json", value)
        with self.assertRaisesRegex(R.RunnerError, "another checkpoint"):
            R.validate_private_input(path, "2026-08-15T00:17:00Z", self.proof())

    def test_private_manifest_rejects_another_runner_contract(self) -> None:
        value, _ = self.private_input()
        value["runner_contract"]["runner_path"] = "scripts/another_runner.py"
        path = self.write("wrong-runner-input.json", value)
        with self.assertRaisesRegex(R.RunnerError, "frozen schema"):
            R.validate_private_input(path, "2026-08-14T00:17:00Z", self.proof())

    def test_private_manifest_rejects_tampered_content_address(self) -> None:
        value, files = self.private_input()
        path = self.write("private-input.json", value)
        files[2].write_text("tampered\n", encoding="utf-8")
        with self.assertRaisesRegex(R.RunnerError, "digest mismatch"):
            R.validate_private_input(path, "2026-08-14T00:17:00Z", self.proof())

    def test_capture_never_writes_when_adapter_is_not_frozen(self) -> None:
        output = self.root / "out"
        args = Namespace(
            contract=self.root / "contract", u1_receipt=self.root / "u1",
            scheduled_for_utc="2026-08-14T00:17:00Z", event_name="schedule",
            run_attempt=1, public_chain_proof=self.root / "proof",
            public_repository=self.root, private_input=self.root / "private",
            terminal_chronology_gap=False, output=output,
        )
        with mock.patch.object(R, "validate_contract"), \
             mock.patch.object(R, "validate_source_readiness"), \
             mock.patch.object(R, "authenticate_p1_and_components"), \
             mock.patch.object(R, "validate_chain", return_value=self.proof()), \
             mock.patch.object(R, "validate_private_input"):
            with self.assertRaisesRegex(R.RunnerError, "adapter is not frozen"):
                R.run(args)
        self.assertFalse(output.exists())

    def test_terminal_mode_forbids_private_input_before_receipt(self) -> None:
        args = Namespace(
            contract=self.root / "contract", u1_receipt=self.root / "u1",
            scheduled_for_utc="2026-08-14T00:17:00Z", event_name="schedule",
            run_attempt=1, public_chain_proof=self.root / "proof",
            public_repository=self.root, private_input=self.root / "private",
            terminal_chronology_gap=True, output=self.root / "out",
        )
        with mock.patch.object(R, "validate_contract"), \
             mock.patch.object(R, "validate_source_readiness"), \
             mock.patch.object(R, "authenticate_p1_and_components"), \
             mock.patch.object(R, "validate_chain", return_value=self.proof()):
            with self.assertRaisesRegex(R.RunnerError, "must not receive private"):
                R.run(args)

    def test_output_directory_must_be_empty(self) -> None:
        output = self.root / "out"
        output.mkdir()
        (output / "old").write_text("x", encoding="utf-8")
        values = {name: {"schema": "c5k4-method-v1.5-fixture"} for name in R.PUBLIC_FILES}
        with self.assertRaisesRegex(R.RunnerError, "not empty"):
            R.publish(output, values)
        self.assertTrue((output / "old").exists())


if __name__ == "__main__":
    unittest.main()
