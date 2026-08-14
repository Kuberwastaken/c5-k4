#!/usr/bin/env python3
"""Constructor-only tests; no C13 target above the frozen boundary is scored."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import prepare_graffiti3_conjecture13_gate as gate
import search_graffiti3_conjecture13 as search
import verify_graffiti3_conjecture13_candidate as verifier


class ArithmeticFixtures(unittest.TestCase):
    def test_segmented_phi(self) -> None:
        self.assertEqual(gate.segmented_phi(1, 10), [1, 1, 2, 2, 4, 2, 6, 4, 6, 4])

    def test_calibration_controls(self) -> None:
        for n in (341, 561):
            row = gate.control_profile(n)
            self.assertEqual(row["modular_residue"], 1)
            self.assertFalse(row["premise"])

    def test_independent_primality(self) -> None:
        self.assertTrue(verifier.prime64(2**61 - 1))
        self.assertFalse(verifier.prime64(341))

    def test_korselt_fixture(self) -> None:
        factors = search.factor_with_primes(561, gate.primes_through(30))
        self.assertEqual(factors, {3: 1, 11: 1, 17: 1})
        self.assertTrue(search.is_carmichael(561, factors))


class FrozenConstruction(unittest.TestCase):
    def test_generic_shards_are_disjoint_and_above_boundary(self) -> None:
        manifest = gate.load_manifest(gate.DEFAULT_MANIFEST, verify_artifacts=False)
        blocks = [search.generic_block(manifest, shard) for shard in range(search.SHARDS)]
        self.assertTrue(all(start > search.BOUNDARY for start, _ in blocks))
        self.assertTrue(all(end < manifest["generic"]["upper_exclusive"] for _, end in blocks))
        self.assertEqual(len(blocks), len(set(blocks)))
        for left, right in zip(blocks, blocks[1:]):
            self.assertLess(left[1], right[0])

    def test_partition_is_complete_without_overlap(self) -> None:
        values = list(range(101))
        pieces = [list(search.partition(values, shard)) for shard in range(search.SHARDS)]
        self.assertEqual([item for piece in pieces for item in piece], values)

    def test_generic_receipt_is_exact_and_tamper_evident(self) -> None:
        receipt = search.scan_generic_block(2, 100)
        search.validate_generic_block(receipt, 2, 100)
        receipt["evaluated"] -= 1
        with self.assertRaises(search.SearchError):
            search.validate_generic_block(receipt, 2, 100)

    def test_ledger_is_incremental_hash_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            ledger = search.Ledger(path, "CATALOGUE", 0, "a" * 40)
            ledger.emit("fixture", {"n": 341})
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(rows[1]["previous_row_sha256"], rows[0]["row_sha256"])
            for row in rows:
                claimed = row.pop("row_sha256")
                self.assertEqual(claimed, hashlib.sha256(gate.canonical_json(row)).hexdigest())


class GateAttestation(unittest.TestCase):
    @staticmethod
    def write(path: Path, data: bytes) -> str:
        path.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def fixture(self, root: Path) -> tuple[Path, Path]:
        pdf = root / "source.pdf"
        a1 = root / "b001567.txt"
        a2 = root / "b002997.txt"
        pdf_hash = self.write(pdf, b"fixture primary source\n")
        a1_hash = self.write(a1, b"1 341\n2 561\n")
        a2_hash = self.write(a2, b"1 561\n")
        manifest = {
            "schema": gate.MANIFEST_SCHEMA,
            "source": {"pdf_sha256": pdf_hash},
            "oeis": {
                "A001567": {"sha256": a1_hash, "rows": 2, "last_index": 2, "last_value": 561},
                "A002997": {"sha256": a2_hash, "rows": 1, "last_index": 1, "last_value": 561},
            },
            "gate": {"min_n": 2, "max_n": 20, "chunk_size": 7,
                     "child_cap_seconds": 4, "controls": [341, 561]},
            "artifacts": [],
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        bundle = root / "bundle"
        gate.prepare_bundle(manifest_path, pdf, a1, a2, bundle, "a" * 40)
        return manifest_path, bundle

    def test_complete_bundle_replays(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest, bundle = self.fixture(Path(directory))
            attestation = gate.verify_bundle(manifest, bundle, "a" * 40)
            self.assertEqual(attestation["coverage"]["evaluated"], 19)

    def test_missing_and_tampered_chunks_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest, bundle = self.fixture(Path(directory))
            chunk = sorted((bundle / "chunks").iterdir())[0]
            original = chunk.read_bytes()
            chunk.unlink()
            with self.assertRaises(gate.GateError):
                gate.verify_bundle(manifest, bundle, "a" * 40)
            chunk.write_bytes(original + b" ")
            with self.assertRaises(gate.GateError):
                gate.verify_bundle(manifest, bundle, "a" * 40)

    def test_gate_rejects_a_stale_campaign_commit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest, bundle = self.fixture(Path(directory))
            with self.assertRaises(gate.GateError):
                gate.verify_bundle(manifest, bundle, "b" * 40)

    def test_candidate_replay_rejects_calibration_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, bundle = self.fixture(root)
            certificate = root / "candidate.json"
            certificate.write_text(json.dumps({
                "schema": verifier.SCHEMA,
                "campaign_commit": "a" * 40,
                "manifest_sha256": gate.sha256_file(manifest),
                "construction": {"kind": "A001567"},
                "evaluation": {"n": 341, "arm": "CATALOGUE"},
            }), encoding="utf-8")
            with self.assertRaises(verifier.ReplayError):
                verifier.replay(certificate, manifest, bundle)


class WorkflowContract(unittest.TestCase):
    def test_caps_and_no_public_permissions(self) -> None:
        workflow = (gate.REPO_ROOT / ".github/workflows/graffiti3-conjecture13-development.yml").read_text()
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("timeout --signal=TERM --kill-after=5s 60s", workflow)
        self.assertIn("set +e", workflow)
        self.assertIn("Verify immutable preparation checkout", workflow)
        self.assertIn("Verify immutable worker checkout", workflow)
        self.assertIn("terminal_validation_exit_code", workflow)
        self.assertIn("certificate/terminal mismatch", workflow)
        self.assertIn("timeout=float(gate[\"child_cap_seconds\"])",
                      (gate.REPO_ROOT / "scripts/prepare_graffiti3_conjecture13_gate.py").read_text())
        self.assertIn("INTERNAL_SECONDS = 54.0",
                      (gate.REPO_ROOT / "scripts/search_graffiti3_conjecture13.py").read_text())


if __name__ == "__main__":
    unittest.main()
