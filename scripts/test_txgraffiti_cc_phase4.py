#!/usr/bin/env python3
"""Constructor-only and unit tests for TxGraffiti C-C phase four."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import networkx as nx

import search_txgraffiti_cc_phase2 as phase2
import search_txgraffiti_cc_phase3 as phase3
import search_txgraffiti_cc_phase4 as worker
import txgraffiti_cc_phase4_domain as domain
from aggregate_txgraffiti_cc_phase4 import classify


class Phase4DomainTests(unittest.TestCase):
    def test_frozen_constructor_has_exactly_5320_unique_states(self) -> None:
        records = domain.construction_records()
        self.assertEqual(len(records), 5320)
        self.assertEqual(len({row["state_key_sha256"] for row in records}), 5320)
        counts = {encoded: 0 for encoded in phase3.BASE_GRAPH6}
        for row in records:
            counts[str(row["base_graph6"])] += 1
        self.assertEqual([counts[encoded] for encoded in phase3.BASE_GRAPH6], [278, 697, 2658, 768, 919])

    def test_representative_rebuilds_certified_order_twenty_cubic_graph(self) -> None:
        graph = domain.graph_from_record(domain.construction_records()[0])
        self.assertEqual((graph.number_of_nodes(), graph.number_of_edges()), (20, 30))
        self.assertTrue(nx.is_connected(graph))
        self.assertEqual(set(dict(graph.degree()).values()), {3})
        self.assertEqual(phase2.verify_structural_mu_certificate(graph), 6)

    def test_partition_arm_tree_mapping_is_bijective(self) -> None:
        identities = [worker.arm_tree_for_partition(index) for index in range(24)]
        self.assertEqual(len(set(identities)), 24)
        self.assertEqual(identities[0], ("CATALOGUE", 0))
        self.assertEqual(identities[8], ("GENERIC", 0))
        self.assertEqual(identities[23], ("WALL_NAVIGATION", 7))

    def test_selector_removes_only_prior_identity(self) -> None:
        digests = [f"{value:064x}" for value in range(1, 200) if value % 24 == 7][:3]
        rows = [{
            "schema": domain.IDENTITY_SCHEMA,
            "canonical_graph6": "Dhc",
            "canonical_sha256": digest,
            "partition": 7,
            "construction_multiplicity": 1,
            "representative_state": {},
        } for digest in digests]
        retained = domain.unscored_partition_rows(rows, {digests[1]}, 7)
        self.assertEqual([row["canonical_sha256"] for row in retained], [digests[0], digests[2]])

    def test_scored_ledger_reader_ignores_objective_values(self) -> None:
        digest = "a" * 64
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "prior.jsonl"
            rows = [
                {"kind": "checkpoint", "label": "started"},
                {"kind": "evaluated_candidate", "canonical_sha256": digest, "objective": -999},
                {"kind": "summary", "status": "COMPLETED"},
            ]
            path.write_bytes(b"".join(domain.canonical_json(row) for row in rows))
            scored, sources = domain.scored_identities([path])
        self.assertEqual(scored, {digest})
        self.assertEqual(sources[0]["evaluated_rows"], 1)

    def test_terminal_receipt_distinguishes_exhaustion_and_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for reason, exhausted in (("DOMAIN_EXHAUSTED", True), ("DEADLINE_PREFIX", False)):
                path = root / f"{reason}.json"
                worker.write_terminal(
                    path,
                    partition=0,
                    reason=reason,
                    total=10,
                    evaluated=4,
                    next_index=4,
                )
                value = json.loads(path.read_text())
                self.assertEqual(value["terminal_reason"], reason)
                self.assertIs(value["domain_exhausted"], exhausted)

    def test_aggregate_status_never_infers_exhaustion_from_normal_exit(self) -> None:
        self.assertEqual(classify(["DOMAIN_EXHAUSTED"] * 24, 0, []), "DOMAIN_EXHAUSTED_ZERO")
        self.assertEqual(
            classify(["DOMAIN_EXHAUSTED"] * 23 + ["DEADLINE_PREFIX"], 0, []),
            "BOUNDED_PREFIX_ZERO",
        )
        self.assertEqual(classify(["CROSSING_VERIFIED"], 1, []), "VERIFIED_CROSSING")
        self.assertEqual(classify(["DOMAIN_EXHAUSTED"] * 24, 0, ["bad"]), "INVALID_RUN")


if __name__ == "__main__":
    unittest.main()
