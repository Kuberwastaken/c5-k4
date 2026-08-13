#!/usr/bin/env python3
"""Focused tests for Method v1.5 generated identity artifact verification."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import verify_generated_registry_artifacts_v15 as verifier


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class Fixture:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.com")
        (self.repo / "scripts").mkdir()
        (self.repo / "inputs").mkdir()
        self.producer = self.repo / "scripts" / "produce.py"
        self.producer.write_text(
            "import json\nfrom pathlib import Path\n"
            "row=json.loads(Path('inputs/source.json').read_text())\n"
            "print(json.dumps(row, sort_keys=True, indent=2))\n",
            encoding="utf-8",
        )
        self.input = self.repo / "inputs" / "source.json"
        self.value = {
            "schema_version": "c5k4-open-inventory-1.5",
            "artifact_kind": "open_inventory",
            "declarations": [{"declaration_id": "FormalConjectures.Future.One", "status": "OPEN"}],
        }
        self.input.write_text(json.dumps(self.value), encoding="utf-8")
        self.contract = self.repo / "contract.json"
        self.contract_value = {
            "schema_version": verifier.CONTRACT_SCHEMA,
            "producer_path": "scripts/produce.py",
            "argv": ["{PYTHON}", "scripts/produce.py"],
            "input_paths": ["inputs/source.json"],
            "output_mode": "stdout",
            "artifact_kind": "open_inventory",
            "output_schema_version": "c5k4-open-inventory-1.5",
            "safe_surface": verifier.SAFE_SURFACE,
            "network": "FORBIDDEN",
            "interactive_delivery": False,
            "timeout_seconds": 10,
        }
        self.contract.write_text(json.dumps(self.contract_value, sort_keys=True) + "\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "freeze producer contract and input")
        self.basis = git(self.repo, "rev-parse", "HEAD")
        raw = (json.dumps(self.value, sort_keys=True, indent=2) + "\n").encode()
        output = self.repo / "results" / "open-inventory.json"
        output.parent.mkdir()
        output.write_bytes(raw)
        git(self.repo, "add", "results/open-inventory.json")
        git(self.repo, "commit", "-qm", "commit generated output")
        self.output_commit = git(self.repo, "rev-parse", "HEAD")
        self.raw = raw

    def manifest(self) -> dict:
        return {
            "schema_version": verifier.MANIFEST_SCHEMA,
            "repository": str(self.repo),
            "basis_commit": self.basis,
            "output_commit": self.output_commit,
            "producer": {"path": "scripts/produce.py", "sha256": verifier.sha256(self.producer.read_bytes())},
            "contract": {"path": "contract.json", "sha256": verifier.sha256(self.contract.read_bytes())},
            "inputs": [{"path": "inputs/source.json", "sha256": verifier.sha256(self.input.read_bytes())}],
            "output": {
                "path": "results/open-inventory.json", "artifact_kind": "open_inventory",
                "schema_version": "c5k4-open-inventory-1.5",
                "content_sha256": verifier.sha256(self.raw), "byte_count": len(self.raw),
                "source_id": "repo:c5-k4",
            },
        }


class VerificationTests(unittest.TestCase):
    def test_exact_historical_replay_emits_locator_specific_proof(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            proof = verifier.verify(fixture.manifest())
            self.assertEqual(proof["verification_status"], "VERIFIED")
            self.assertTrue(proof["deterministic_exact_replay_verified"])
            self.assertTrue(proof["historical_inputs_predate_output"])
            self.assertTrue(proof["locator"].endswith(":results/open-inventory.json"))
            self.assertFalse(proof["global_content_hash_allowlist"])

    def test_producer_contract_and_inputs_must_predate_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            manifest = fixture.manifest()
            manifest["basis_commit"] = fixture.output_commit
            with self.assertRaisesRegex(verifier.VerificationError, "sole first parent"):
                verifier.verify(manifest)

    def test_exact_replay_rejects_committed_bytes_not_generated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            manifest = fixture.manifest()
            output = fixture.repo / "results" / "open-inventory.json"
            changed = {**fixture.value, "complete": True}
            raw = (json.dumps(changed, sort_keys=True, indent=2) + "\n").encode()
            output.write_bytes(raw)
            git(fixture.repo, "add", str(output.relative_to(fixture.repo)))
            git(fixture.repo, "commit", "-qm", "non-replayable output")
            manifest["basis_commit"] = fixture.output_commit
            manifest["output_commit"] = git(fixture.repo, "rev-parse", "HEAD")
            manifest["output"]["content_sha256"] = verifier.sha256(raw)
            manifest["output"]["byte_count"] = len(raw)
            with self.assertRaisesRegex(verifier.VerificationError, "exact replay"):
                verifier.verify(manifest)

    def test_safe_surface_rejects_statement_or_prose(self) -> None:
        bad = {
            "schema_version": "c5k4-open-inventory-1.5", "artifact_kind": "open_inventory",
            "declarations": [{"declaration_id": "X", "statement": "Every graph is ..."}],
        }
        with self.assertRaisesRegex(verifier.VerificationError, "outside the identity-only"):
            verifier.validate_identity_artifact(
                json.dumps(bad).encode(), "open_inventory", "c5k4-open-inventory-1.5"
            )

    def test_same_hash_at_unregistered_locator_has_no_proof(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            proof = verifier.verify(fixture.manifest())
            copied = dict(proof)
            copied["locator"] = proof["locator"].replace("open-inventory", "discussion")
            self.assertNotEqual(
                copied["unit_identity_sha256"],
                verifier.unit_identity_sha256(
                    copied["source_id"], copied["source_kind"], copied["locator"], copied["role"],
                    copied["content_sha256"], copied["content_schema"],
                ),
            )

    def test_contract_cannot_expand_safe_surface_or_use_interactive_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            manifest = fixture.manifest()
            # A changed contract is not historical evidence and fails before replay.
            fixture.contract_value["interactive_delivery"] = True
            fixture.contract.write_text(json.dumps(fixture.contract_value, sort_keys=True) + "\n")
            manifest["contract"]["sha256"] = verifier.sha256(fixture.contract.read_bytes())
            with self.assertRaisesRegex(verifier.VerificationError, "historical bytes"):
                verifier.verify(manifest)


if __name__ == "__main__":
    unittest.main()
