#!/usr/bin/env python3
"""Constructor-only tests; target indices n >= 5 are intentionally untouched."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import search_tan_arctan_sum_live as target


class TanArctanFrozenHarnessTests(unittest.TestCase):
    def test_manifest_source_and_development_pins(self) -> None:
        manifest = target.load_and_verify_manifest(target.DEFAULT_MANIFEST)
        self.assertEqual(manifest["upstream"]["commit"], target.UPSTREAM_COMMIT)
        self.assertEqual(manifest["upstream"]["blob"], target.UPSTREAM_BLOB)
        self.assertEqual(manifest["evidence_split"], "DEVELOPMENT")
        self.assertFalse(manifest["candidate_policy"]["public_action"])

    def test_recurrence_and_balanced_product_only_on_non_target_controls(self) -> None:
        gate = target.database_sanity_gate()
        self.assertEqual(gate["target_values_evaluated"], 0)
        self.assertEqual(gate["documented_integer_indices"], [1, 2, 3, 4])
        self.assertEqual(gate["controls"][-1], {"n": 4, "a": -10, "b": -40, "omega": 1700})

    def test_integrality_is_exact_reduced_denominator_one(self) -> None:
        self.assertTrue(target.is_integer_value(-10, -40))
        self.assertEqual(target.reduced_denominator(-10, -40), 1)
        self.assertFalse(target.is_integer_value(6, 15))
        self.assertEqual(target.reduced_denominator(6, 15), 2)
        self.assertFalse(target.is_integer_value(0, 9))

    def test_wall_predicate_uses_integer_cross_multiplication(self) -> None:
        self.assertTrue(target.is_exceptional_wall(4, -10, -40))
        self.assertFalse(target.is_exceptional_wall(4, 10, 20))
        self.assertTrue(target.is_exceptional_wall(4, 0, 1))

    def test_frozen_domains_are_structural_only(self) -> None:
        self.assertEqual(target.PAPER_EXCEPTIONAL_CATALOGUE[0], 15)
        self.assertEqual(target.PAPER_EXCEPTIONAL_CATALOGUE[-1], 44088)
        self.assertEqual(len(target.PAPER_EXCEPTIONAL_CATALOGUE), 12)
        self.assertGreater(target.SEARCH_START, 60000)
        selected = [n for n in range(target.SEARCH_START, target.SEARCH_START + 1000) if target.generic_selected(n)]
        self.assertTrue(selected)
        self.assertEqual(selected, [n for n in range(target.SEARCH_START, target.SEARCH_START + 1000) if target.generic_selected(n)])

    def test_incremental_hash_chain_and_terminal_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            ledger = target.DurableLedger(root / "ledger.jsonl", "GENERIC")
            ledger.emit("database_sanity_gate", {"synthetic": True, "target_values_evaluated": 0})
            receipt = target.write_terminal(root / "terminal.json", ledger, "PROPOSAL_LIMIT", {"next_n": 7})
            rows = [json.loads(line) for line in (root / "ledger.jsonl").read_text().splitlines()]
            previous = target.ZERO_SHA256
            for sequence, row in enumerate(rows):
                self.assertEqual(row["sequence"], sequence)
                self.assertEqual(row["previous_row_sha256"], previous)
                claimed = row.pop("row_sha256")
                self.assertEqual(claimed, hashlib.sha256(target.canonical_json(row)).hexdigest())
                previous = claimed
            self.assertEqual(receipt["final_row_sha256"], previous)

    def test_workflow_is_manual_read_only_and_hard_capped(self) -> None:
        workflow = target.REPO_ROOT / ".github" / "workflows" / "tan-arctan-sum-development.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("arm: [CATALOGUE, GENERIC, WALL_NAVIGATION]", text)
        self.assertIn("--kill-after=5s 60s", text)
        self.assertIn("campaign_commit", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)


if __name__ == "__main__":
    unittest.main()
