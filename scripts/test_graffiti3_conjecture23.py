#!/usr/bin/env python3
"""Constructor-only tests; no development target is evaluated."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import search_graffiti3_conjecture23 as target
import verify_graffiti3_conjecture23_certificate as verifier


class Graffiti3Conjecture23FreezeTests(unittest.TestCase):
    def test_manifest_freeze(self) -> None:
        manifest = target.load_and_verify_manifest(target.DEFAULT_MANIFEST)
        self.assertEqual(manifest["evidence_split"], "DEVELOPMENT")
        self.assertEqual(manifest["source"]["conjecture"], 23)
        self.assertEqual(manifest["catalogue"]["order"], 256)
        self.assertFalse(manifest["candidate_policy"]["public_action"])

    def test_literal_integer_residual(self) -> None:
        self.assertEqual(target.residual_w(8, 2, 2, 5), 0)  # D8/Q8 equality fixture
        self.assertEqual(target.residual_w(2, 1, 2, 2), 2)  # C2 safe fixture

    def test_profile_parser_recovers_extraspecial_controls(self) -> None:
        for identity in ("D8", "Q8"):
            row = target.parse_profile(
                f"@@PROFILE@@\t{identity}\t8\t2\t4\t2\t5\ttrue\t@@END@@\n",
                identity, "sanity fixture", "fixture",
            )
            self.assertEqual(row.residual_w, 0)
            self.assertTrue(row.is_p_group)

    def test_database_gate_fixture(self) -> None:
        receipt = target.parse_database_gate("@@GATE@@\t2732\t0\t17\t0\t0\t@@END@@\n")
        self.assertEqual(receipt["checked"], target.EXPECTED_DATABASE_GATE_COUNT)
        self.assertEqual(receipt["negatives"], 0)

    def test_database_gate_rejects_partial_snapshot(self) -> None:
        with self.assertRaises(target.SearchError):
            target.parse_database_gate("@@GATE@@\t2328\t0\t17\t0\t0\t@@END@@\n")

    def test_catalogue_partition_is_complete_and_disjoint(self) -> None:
        domains = [target.partition_interval(target.CATALOGUE_COUNT, target.SHARDS, shard) for shard in range(target.SHARDS)]
        flattened = [value for domain in domains for value in domain]
        self.assertEqual(flattened, list(range(1, target.CATALOGUE_COUNT + 1)))

    def test_generic_ids_are_deterministic_and_in_range(self) -> None:
        first = [target.deterministic_generic_id(7, cursor) for cursor in range(20)]
        second = [target.deterministic_generic_id(7, cursor) for cursor in range(20)]
        self.assertEqual(first, second)
        self.assertTrue(all(1 <= value <= target.GENERIC_COUNT for value in first))

    def test_wall_domain_constructor_only(self) -> None:
        rows = target.wall_assignments()
        self.assertEqual(len(rows), (3 ** 3 - 3) + (3 ** 4 - 3))
        self.assertTrue(all(target.binary_rank(outputs, 2) == 2 for _, outputs in rows))
        assigned = sum((list(target.wall_shard_rows(shard)) for shard in range(target.SHARDS)), [])
        self.assertEqual(sorted(assigned), sorted(rows))

    def test_cocycle_basis_identity_fixture(self) -> None:
        # Constructor algebra only, below the frozen d=6/d=8 target domain.
        d, outputs = 2, (1,)
        for i in range(d):
            for j in range(d):
                for k in range(d):
                    x, y, z = 1 << i, 1 << j, 1 << k
                    lhs = target.cocycle_value(d, outputs, x, y) ^ target.cocycle_value(d, outputs, x ^ y, z)
                    rhs = target.cocycle_value(d, outputs, y, z) ^ target.cocycle_value(d, outputs, x, y ^ z)
                    self.assertEqual(lhs, rhs)

    def test_hash_chain_and_terminal_fsync_shape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            ledger = target.DurableLedger(root / "ledger.jsonl", "GENERIC", 4, "a" * 40)
            ledger.emit("fixture", {"value": 7})
            receipt = target.write_terminal(root / "terminal.json", ledger, "PROPOSAL_LIMIT")
            previous = target.ZERO_SHA256
            for sequence, line in enumerate((root / "ledger.jsonl").read_text().splitlines()):
                row = json.loads(line)
                self.assertEqual(row["sequence"], sequence)
                self.assertEqual(row["previous_row_sha256"], previous)
                claimed = row.pop("row_sha256")
                self.assertEqual(claimed, hashlib.sha256(target.canonical_json(row)).hexdigest())
                previous = claimed
            self.assertEqual(receipt["final_row_sha256"], previous)

    def test_independent_verifier_rejects_safe_fixture(self) -> None:
        document = {
            "schema": verifier.CERTIFICATE_SCHEMA,
            "profile": {
                "order": 2, "derived_order": 1, "abelianization_order": 2,
                "center_order": 2, "conjugacy_classes": 2, "residual_w": 1,
                "wall_descriptor": None,
            },
            "multiplication_table": [[0, 1], [1, 0]],
        }
        with self.assertRaises(verifier.VerificationError):
            verifier.verify_document(document)

    def test_workflow_is_manual_read_only_pinned_and_capped(self) -> None:
        workflow = target.REPO_ROOT / ".github" / "workflows" / "graffiti3-conjecture23-development.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("gap=4.12.1-2build2", text)
        self.assertIn("gap-smallgrp=1.5.3-1", text)
        self.assertIn("timeout --signal=TERM --kill-after=5s 60s", text)
        self.assertNotIn("release", text.lower())


if __name__ == "__main__":
    unittest.main()
