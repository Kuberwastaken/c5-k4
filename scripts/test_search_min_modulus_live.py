#!/usr/bin/env python3
"""Constructor-only and synthetic-control tests for the minimum-modulus worker."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import search_min_modulus_live as target


class MinimumModulusHelperTests(unittest.TestCase):
    def test_manifest_and_contract_pin(self) -> None:
        manifest = target.load_and_verify_manifest(target.DEFAULT_MANIFEST)
        self.assertEqual(manifest["upstream"]["commit"], target.UPSTREAM_COMMIT)
        self.assertEqual(manifest["evidence_split"], "DEVELOPMENT")
        self.assertFalse(manifest["candidate_policy"]["public_action"])

    def test_min_modulus_initial_values(self) -> None:
        self.assertEqual([target.min_modulus(n) for n in range(2, 7)], [2, 6, 12, 28, 60])

    def test_weak_composition_count(self) -> None:
        for total, parts in ((0, 1), (2, 2), (3, 3), (5, 4)):
            rows = list(target.weak_compositions(total, parts))
            self.assertEqual(len(rows), math.comb(total + parts - 1, parts - 1))
            self.assertEqual(len(set(rows)), len(rows))
            self.assertTrue(all(sum(row) == total for row in rows))

    def test_exact_dp_matches_independent_replay_on_controls(self) -> None:
        for n, modulus, residues in (
            (2, 2, (0, 1)),
            (3, 6, (0, 1, 3)),
            (3, 6, (0, 1, 2)),
            (4, 9, (0, 1, 3, 7)),
        ):
            profile = target.exact_collision_profile(n, modulus, residues)
            replay = target.replay_collision_count(n, modulus, residues)
            self.assertEqual(profile["collision_count"], replay)

    def test_database_gate_reproduces_positive_and_negative_controls(self) -> None:
        receipt = target.database_sanity_gate()
        rows = {row["name"]: row for row in receipt["controls"]}
        self.assertEqual(rows["boundary_n2_valid"]["collision_count"], 0)
        self.assertEqual(rows["boundary_n3_valid"]["collision_count"], 0)
        self.assertGreater(rows["documented_collision"]["collision_count"], 0)
        self.assertTrue(receipt["modulus_one_size_two_rejected"])

    def test_affine_canonicalization_is_exactly_invariant(self) -> None:
        n, modulus = 4, 13
        base = (0, 1, 4, 9)
        translated = tuple((value + 7) % modulus for value in base)
        scaled = tuple((5 * value) % modulus for value in translated)
        expected = target.canonical_residue_set(n, modulus, base)
        self.assertEqual(target.canonical_residue_set(n, modulus, translated), expected)
        self.assertEqual(target.canonical_residue_set(n, modulus, scaled), expected)
        self.assertEqual(
            target.identity_sha256(n, modulus, scaled),
            target.identity_sha256(n, modulus, base),
        )

    def test_stable_catalogue_partition(self) -> None:
        identity = target.identity_sha256(4, 11, (0, 1, 3, 7))
        shard = int(identity, 16) % target.SHARDS_PER_ARM
        self.assertGreaterEqual(shard, 0)
        self.assertLess(shard, target.SHARDS_PER_ARM)
        self.assertEqual(shard, int(target.identity_sha256(4, 11, (2, 3, 5, 9)), 16) % 8)

    def test_terminal_reason_is_durable_and_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            ledger = target.DurableLedger(root / "ledger.jsonl", "GENERIC", 3)
            ledger.emit("database_sanity_gate", {"synthetic": True})
            receipt = target.write_terminal(
                root / "terminal.json",
                ledger,
                "PROPOSAL_LIMIT",
                {"proposal_index": 10},
                False,
            )
            rows = [json.loads(line) for line in (root / "ledger.jsonl").read_text().splitlines()]
            previous = target.ZERO_SHA256
            for sequence, row in enumerate(rows):
                self.assertEqual(row["sequence"], sequence)
                self.assertEqual(row["previous_row_sha256"], previous)
                claimed = row.pop("row_sha256")
                self.assertEqual(claimed, hashlib.sha256(target.canonical_json(row)).hexdigest())
                previous = claimed
            self.assertEqual(receipt["final_row_sha256"], previous)
            self.assertEqual(receipt["terminal_reason"], "PROPOSAL_LIMIT")

    def test_wall_constructor_emits_only_finite_size_n_sets(self) -> None:
        n = 5
        modulus = target.min_modulus(n)
        root = tuple((1 << exponent) - 1 for exponent in range(n))
        children = list(target.wall_children(n, modulus, root))
        self.assertTrue(children)
        for child_modulus, residues, operation in children:
            self.assertGreaterEqual(child_modulus, n)
            self.assertEqual(len(residues), n)
            self.assertEqual(len(set(residues)), n)
            self.assertTrue(operation)

    def test_workflow_is_manual_read_only_and_matrix_sharded(self) -> None:
        workflow = target.REPO_ROOT / ".github" / "workflows" / "min-modulus-live.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("arm: [CATALOGUE, GENERIC, WALL_NAVIGATION]", text)
        self.assertIn("shard: [0, 1, 2, 3, 4, 5, 6, 7]", text)
        self.assertIn("--kill-after=5s 60s", text)
        self.assertNotIn("release", text.lower())


if __name__ == "__main__":
    unittest.main()
