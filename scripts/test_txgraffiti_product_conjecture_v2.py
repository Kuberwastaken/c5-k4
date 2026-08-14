#!/usr/bin/env python3
"""Constructor and certificate-shape tests; no frozen target pair is evaluated."""

import json
from pathlib import Path
import tempfile
import time
import unittest

import networkx as nx

import search_txgraffiti_product_conjecture_v2 as worker
import verify_txgraffiti_product_v2_certificate as independent


class V2ContractTests(unittest.TestCase):
    def test_product_constructors_remain_distinct(self) -> None:
        k2, k3 = nx.complete_graph(2), nx.complete_graph(3)
        self.assertTrue(nx.is_isomorphic(worker.cartesian_product(k2, k2), nx.cycle_graph(4)))
        self.assertTrue(nx.is_isomorphic(
            worker.direct_product(k2, k2),
            nx.disjoint_union(nx.path_graph(2), nx.path_graph(2)),
        ))
        self.assertTrue(nx.is_isomorphic(worker.cartesian_product(k2, k3), nx.circular_ladder_graph(3)))
        self.assertTrue(nx.is_isomorphic(worker.direct_product(k2, k3), nx.cycle_graph(6)))
        self.assertEqual(
            worker.identity(worker.cartesian_product(k2, k3)),
            independent.graph_identity(independent.cartesian_product(k2, k3)),
        )
        self.assertEqual(
            worker.identity(worker.direct_product(k2, k3)),
            independent.graph_identity(independent.direct_product(k2, k3)),
        )

    def test_fixed_size_receipts_are_honest(self) -> None:
        path = nx.path_graph(3)
        witness = worker.fixed_size_decision(path, 1, False, time.monotonic() + 10)
        absent = worker.fixed_size_decision(path, 1, True, time.monotonic() + 10)
        self.assertEqual(witness["status"], "WITNESS")
        self.assertEqual(witness["witness"], [1])
        self.assertLess(witness["subsets_examined"], witness["total_subsets"])
        self.assertEqual(absent["status"], "ABSENT")
        self.assertTrue(absent["complete"])
        self.assertEqual(absent["subsets_examined"], absent["total_subsets"])

    def test_cartesian_descent_reaches_tiny_exact_value(self) -> None:
        rows = []
        value = worker.descend_cartesian_upper_bound(
            nx.cycle_graph(4), time.monotonic() + 10, rows.append
        )
        self.assertEqual(value["upper_bound"], 2)
        self.assertTrue(value["exact"])
        self.assertEqual(value["lower_bound"], 2)

    def test_direct_value_is_never_admitted_after_timeout(self) -> None:
        original = worker.fixed_size_decision
        worker.fixed_size_decision = lambda *args, **kwargs: {
            "status": "TIMEOUT", "size": args[1], "total": False,
            "subsets_examined": 0, "total_subsets": 1,
            "witness": None, "complete": False,
        }
        try:
            value = worker.exact_direct_domination(nx.path_graph(3), time.monotonic() + 10, lambda row: None)
        finally:
            worker.fixed_size_decision = original
        self.assertFalse(value["exact"])
        self.assertIsNone(value["value"])

    def test_frozen_domain_sizes_and_determinism(self) -> None:
        self.assertEqual(len(list(worker.catalogue_pairs())), 69)
        self.assertEqual(len(list(worker.wall_pairs())), 32)
        first = list(worker.generic_pairs(count=4))
        second = list(worker.generic_pairs(count=4))
        self.assertEqual(
            [(name, worker.identity(left), worker.identity(right)) for name, left, right in first],
            [(name, worker.identity(left), worker.identity(right)) for name, left, right in second],
        )

    def test_hard_caps_and_vocabulary(self) -> None:
        self.assertEqual(worker.SUBPROBLEM_SECONDS, 4.0)
        self.assertEqual(worker.INTERNAL_STOP_SECONDS, 54.0)
        self.assertEqual(worker.ARMS, ("CATALOGUE", "GENERIC", "WALL_NAVIGATION"))
        self.assertIn("DEADLINE_PREFIX", worker.TERMINAL_REASONS)
        with self.assertRaises(worker.SearchError):
            worker.fixed_size_decision(nx.path_graph(3), 1, False, time.monotonic() + 10, 4.01)

    def test_incremental_chain_replays(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = worker.Ledger(Path(directory) / "ledger.jsonl")
            ledger.append({"kind": "subproblem", "status": "ABSENT"})
            ledger.append({"kind": "pair", "status": "EXACT"})
            rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
            self.assertEqual(rows[1]["previous_row_sha256"], rows[0]["row_sha256"])
            for row in rows:
                digest = row.pop("row_sha256")
                self.assertEqual(digest, worker.hashlib.sha256(worker.canonical_json(row)).hexdigest())

    def test_independent_identity_rejects_mutation(self) -> None:
        record = worker.identity(nx.path_graph(3))
        graph = independent.graph_from_identity(record, connected=True)
        self.assertTrue(nx.is_isomorphic(graph, nx.path_graph(3)))
        mutated = dict(record); mutated["m"] += 1
        with self.assertRaises(independent.CertificateError):
            independent.graph_from_identity(mutated, connected=True)


if __name__ == "__main__":
    unittest.main()
