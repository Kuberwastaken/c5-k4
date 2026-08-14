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
    campaign_commit = "a" * 40

    def complete_gate_rows(self) -> list[dict[str, int]]:
        return [
            {
                "order": order,
                "id": identifier,
                "residual_w": 0 if (order, identifier) in {(8, 3), (8, 4)} else 1,
            }
            for order, identifier in target.database_gate_coordinates()
        ]

    def valid_gate_document(self) -> dict[str, object]:
        return target.build_database_gate_preparation(
            self.complete_gate_rows(), self.campaign_commit, target.DEFAULT_MANIFEST,
        )

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

    def test_gap_profile_source_uses_function_local_variables(self) -> None:
        source = target.gap_profile_source("SmallGroup(256,1)", "fixture")
        self.assertIn("C5K4Profile:=function()", source)
        self.assertIn("local G,D,Z;", source)
        self.assertIn("  G:=SmallGroup(256,1);;", source)
        self.assertFalse(any(line.startswith("G:=") for line in source.splitlines()))

    def test_profile_marker_failure_preserves_gap_output_tail(self) -> None:
        with self.assertRaisesRegex(target.SearchError, "Variable.*read only"):
            target.unique_marker("Variable: 'G' is read only\n", "@@PROFILE@@")

    def test_gap_table_source_and_parser_fixture(self) -> None:
        source = target.gap_table_source("SmallGroup(2,1)", "C2")
        self.assertIn("C5K4Table:=function()", source)
        self.assertIn("local G,els,n,i,j;", source)
        self.assertFalse(any(line.startswith("G:=") for line in source.splitlines()))
        stdout = "@@TABLE_BEGIN@@\tC2\t2\n0,1\n1,0\n@@TABLE_END@@\n"
        self.assertEqual(target.parse_gap_table(stdout, "C2", 2), [[0, 1], [1, 0]])

    def test_database_gate_chunks_cover_snapshot_exactly(self) -> None:
        chunks = [
            target.database_gate_chunk_coordinates(chunk)
            for chunk in range(target.DATABASE_GATE_CHUNKS)
        ]
        self.assertEqual(sum(map(len, chunks)), target.EXPECTED_DATABASE_GATE_COUNT)
        self.assertEqual(tuple(value for chunk in chunks for value in chunk),
                         target.database_gate_coordinates())

    def test_database_gate_chunk_parser_fixture(self) -> None:
        expected = ((8, 3), (8, 4))
        stdout = (
            "@@GATE_ROW@@\t8\t3\t0\t@@END@@\n"
            "@@GATE_ROW@@\t8\t4\t0\t@@END@@\n"
            "@@GATE_CHUNK@@\t7\t2\t@@END@@\n"
        )
        rows = target.parse_database_gate_chunk(stdout, 7, expected)
        self.assertEqual([row["residual_w"] for row in rows], [0, 0])

    def test_database_gate_chunk_source_uses_local_gap_variables(self) -> None:
        expected = target.database_gate_chunk_coordinates(0)
        source = target.gap_database_gate_chunk_source(0, expected)
        self.assertIn("C5K4GateChunk:=function(coordinates)", source)
        self.assertIn("local coordinate,n,identifier,G,D,Z,w;", source)
        self.assertIn(f"@@GATE_CHUNK@@\\t0\\t{len(expected)}", source)

    def test_database_gate_preparation_accepts_complete_bound_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "gate.json"
            target.write_json_fsync(path, self.valid_gate_document())
            receipt = target.verify_database_gate_preparation(
                path, self.campaign_commit, target.DEFAULT_MANIFEST,
            )
            self.assertEqual(receipt["checked"], target.EXPECTED_DATABASE_GATE_COUNT)
            self.assertEqual(receipt["chunk_count"], target.DATABASE_GATE_CHUNKS)

    def test_database_gate_preparation_rejects_missing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(target.SearchError):
                target.verify_database_gate_preparation(
                    Path(raw) / "missing.json", self.campaign_commit,
                    target.DEFAULT_MANIFEST,
                )

    def test_database_gate_preparation_rejects_partial_even_if_resigned(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "partial.json"
            document = self.valid_gate_document()
            document["rows"] = document["rows"][:-1]  # type: ignore[index]
            unsigned = dict(document)
            unsigned.pop("preparation_sha256")
            document["preparation_sha256"] = hashlib.sha256(
                target.canonical_json(unsigned)
            ).hexdigest()
            target.write_json_fsync(path, document)
            with self.assertRaises(target.SearchError):
                target.verify_database_gate_preparation(
                    path, self.campaign_commit, target.DEFAULT_MANIFEST,
                )

    def test_database_gate_preparation_rejects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "tampered.json"
            document = self.valid_gate_document()
            document["rows"][0]["residual_w"] = -1  # type: ignore[index]
            target.write_json_fsync(path, document)
            with self.assertRaises(target.SearchError):
                target.verify_database_gate_preparation(
                    path, self.campaign_commit, target.DEFAULT_MANIFEST,
                )

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
        self.assertIn("prepare-database-gate", text)
        self.assertIn("actions/download-artifact@", text)
        self.assertIn("timeout --signal=TERM --kill-after=5s 60s", text)
        self.assertIn("set +e", text)
        self.assertIn("verifier_exit_code", text)
        self.assertIn("terminal_validation_exit_code", text)
        self.assertIn("certificate/terminal mismatch", text)
        self.assertIn("timeout --signal=TERM --kill-after=5s 60s", text)
        self.assertIn("Verify immutable preparation checkout", text)
        self.assertIn("Verify immutable worker checkout", text)
        self.assertNotIn("release", text.lower())


if __name__ == "__main__":
    unittest.main()
