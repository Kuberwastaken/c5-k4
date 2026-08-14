#!/usr/bin/env python3
"""Constructor/contract tests only: these do not enumerate a campaign arm."""

import json
from pathlib import Path
import tempfile
import unittest

import networkx as nx

import search_txgraffiti_product_conjecture as worker
import verify_txgraffiti_product_certificate as independent


class ContractTests(unittest.TestCase):
    def test_products_are_not_conflated(self) -> None:
        k2 = nx.complete_graph(2)
        self.assertTrue(nx.is_isomorphic(worker.cartesian_product(k2, k2), nx.cycle_graph(4)))
        self.assertTrue(nx.is_isomorphic(worker.direct_product(k2, k2), nx.disjoint_union(nx.path_graph(2), nx.path_graph(2))))

    def test_domination_definitions_are_not_conflated(self) -> None:
        path = nx.path_graph(3)
        self.assertTrue(worker.dominates(path, (1,)))
        self.assertFalse(worker.totally_dominates(path, (1,)))
        self.assertTrue(worker.totally_dominates(path, (0, 1)))

    def test_fixed_arms_and_moves(self) -> None:
        self.assertEqual(worker.ARMS, ("CATALOGUE", "GENERIC", "WALL_NAVIGATION"))
        self.assertEqual([name for name, _ in worker.fixed_moves(nx.path_graph(3))], ["leaf", "false-twin", "true-twin", "subdivision", "parity-path-2"])
        first = list(worker.generic_pairs(count=4))
        second = list(worker.generic_pairs(count=4))
        self.assertEqual([(n, worker.identity(g), worker.identity(h)) for n, g, h in first], [(n, worker.identity(g), worker.identity(h)) for n, g, h in second])

    def test_hash_chain_and_fsync_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = worker.Ledger(Path(directory) / "ledger.jsonl")
            ledger.append({"kind": "unit", "value": 1}); ledger.append({"kind": "unit", "value": 2})
            rows = [json.loads(line) for line in ledger.path.read_text().splitlines()]
            self.assertEqual(rows[1]["previous_row_sha256"], rows[0]["row_sha256"])
            for row in rows:
                digest = row.pop("row_sha256")
                self.assertEqual(digest, worker.hashlib.sha256(worker.canonical_json(row)).hexdigest())

    def test_deadlines_and_terminal_vocabulary(self) -> None:
        self.assertEqual(worker.INTERNAL_STOP_SECONDS, 54.0)
        self.assertIn("DB_SOURCE_GATE_FAILED", worker.TERMINAL_REASONS)
        self.assertIn("DEADLINE_PREFIX", worker.TERMINAL_REASONS)
        self.assertIn("CERTIFICATE_FAILED", worker.TERMINAL_REASONS)

    def test_early_witness_records_actual_subset_count(self) -> None:
        proof = worker.absence_proof(worker.nx.path_graph(3), 1, float("inf"))
        self.assertEqual(proof["total_subsets"], 3)
        self.assertEqual(proof["subsets_examined"], 2)
        self.assertEqual(proof["dominating_set_found"], [1])
        self.assertFalse(proof["complete"])

    def test_independent_identity_mutations_are_rejected(self) -> None:
        record = worker.identity(worker.nx.path_graph(3))
        graph = independent.graph_from_identity(record, require_connected=True)
        self.assertTrue(worker.nx.is_isomorphic(graph, worker.nx.path_graph(3)))
        for key, replacement in (
            ("m", record["m"] + 1),
            ("labelled_identity_sha256", "0" * 64),
            ("labelled_graph6", "invalid"),
        ):
            mutated = dict(record)
            mutated[key] = replacement
            with self.assertRaises(independent.CertificateError):
                independent.graph_from_identity(mutated, require_connected=True)

    def test_independent_absence_record_mutations_are_rejected(self) -> None:
        valid = {
            "size": 1,
            "subsets_examined": 3,
            "total_subsets": 3,
            "dominating_set_found": None,
            "complete": True,
        }
        independent.validate_absence_record(valid, size=1, order=3)
        for key, replacement in (
            ("subsets_examined", 2),
            ("total_subsets", 4),
            ("dominating_set_found", [1]),
            ("complete", False),
        ):
            mutated = dict(valid)
            mutated[key] = replacement
            with self.assertRaises(independent.CertificateError):
                independent.validate_absence_record(mutated, size=1, order=3)


if __name__ == "__main__":
    unittest.main()
