#!/usr/bin/env python3
"""Constructor/control-only tests for the frozen Graffiti3 energy C3 campaign.

These tests deliberately never call evaluate_graph on an eligible order >= 8
graph.  Target evaluation begins only from a committed exact-head workflow.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import json
import tempfile
from pathlib import Path
import unittest

import networkx as nx

import search_graffiti3_energy_c3 as search
import verify_graffiti3_energy_c3 as verify


def k2_integrity_fixture() -> dict[str, object]:
    """Build a certificate-integrity fixture without evaluating an eligible target."""
    graph = nx.path_graph(2)
    rounded = 2
    literal_lower, literal_upper, literal_terms = search.reciprocal_sum_bounds(
        graph, include_center=True
    )
    open_lower, open_upper, open_terms = search.reciprocal_sum_bounds(
        graph, include_center=False
    )
    return {
        "schema": verify.CANDIDATE_SCHEMA,
        "doi": search.DOI,
        "reading": "LITERAL_CLOSED_D2",
        "graph6": search.graph6(graph),
        "edges": search.edge_list(graph),
        "order": 2,
        "size": 1,
        "premises": search.premise_record(graph),
        "diameter_paths": search.diameter_paths(graph),
        "d2_closed": [[v, x] for v, x in sorted(search.d2_values(graph, include_center=True).items())],
        "d2_center_excluding": [
            [v, x] for v, x in sorted(search.d2_values(graph, include_center=False).items())
        ],
        "spectral": search.rational_eigenvalue_intervals(graph),
        "rounded_energy": rounded,
        "rounding": {
            "shelf_lower": search.frac_pair(Fraction(3, 2)),
            "shelf_upper": search.frac_pair(Fraction(5, 2)),
            "half_up": rounded,
            "ties_to_even": rounded,
            "tie_boundary_excluded": True,
        },
        "literal_rhs_lower": search.frac_pair(literal_lower),
        "literal_rhs_upper": search.frac_pair(literal_upper),
        "literal_terms": literal_terms,
        "center_excluding_rhs_lower": search.frac_pair(open_lower),
        "center_excluding_rhs_upper": search.frac_pair(open_upper),
        "center_excluding_terms": open_terms,
        "strict_certificate": f"{literal_lower} > {rounded}",
    }


class ConstructorTests(unittest.TestCase):
    def test_book_chain_shape_and_premises(self) -> None:
        graph = search.book_chain(3, 4)
        self.assertEqual(graph.number_of_nodes(), 11)
        self.assertEqual(graph.number_of_edges(), 3 + 2 * 7)
        self.assertTrue(nx.is_connected(graph))
        self.assertTrue(nx.check_planarity(graph)[0])
        self.assertEqual(nx.diameter(graph), 3)

    def test_apollonian_is_deterministic_and_planar(self) -> None:
        import random
        first = search.apollonian_graph(12, random.Random(20260814))
        second = search.apollonian_graph(12, random.Random(20260814))
        self.assertEqual(search.graph6(first), search.graph6(second))
        self.assertTrue(nx.check_planarity(first)[0])

    def test_three_arm_constructor_prefixes(self) -> None:
        for arm in search.ARMS:
            iterator = iter(search.arm_graphs(arm))
            rows = [next(iterator) for _ in range(3)]
            self.assertEqual(len(rows), 3)
            self.assertTrue(all(isinstance(name, str) and len(graph) >= 2 for name, graph in rows))

    def test_two_degree_readings_are_distinct(self) -> None:
        graph = nx.path_graph(3)
        self.assertEqual(search.d2_values(graph, include_center=True), {0: 3, 1: 3, 2: 3})
        self.assertEqual(search.d2_values(graph, include_center=False), {0: 2, 1: 2, 2: 2})

    def test_radical_bounds_are_outward(self) -> None:
        lower, upper = search.sqrt_dyadic_bounds(13, bits=20)
        self.assertLessEqual(lower * lower, 13)
        self.assertGreaterEqual(upper * upper, 13)
        self.assertLess(upper - lower, Fraction(1, 1 << 19))

    def test_ledger_chain_is_replayable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            ledger = search.ChainedLedger(path)
            first_hash = ledger.append({"kind": "fixture", "value": 1})
            second_hash = ledger.append({"kind": "fixture", "value": 2})
            ledger.close()
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(rows[0]["record_hash"], first_hash)
            self.assertEqual(rows[1]["previous_hash"], first_hash)
            self.assertEqual(rows[1]["record_hash"], second_hash)


class CertificateIntegrityTests(unittest.TestCase):
    def test_k2_control_fixture_replays_all_asserted_fields(self) -> None:
        verify.verify_candidate_integrity(k2_integrity_fixture())

    def test_graph6_mutation_is_rejected(self) -> None:
        certificate = k2_integrity_fixture()
        certificate["graph6"] = "A?"
        with self.assertRaisesRegex(ValueError, "graph6 checksum mismatch"):
            verify.verify_candidate_integrity(certificate)

    def test_missing_diameter_pair_is_rejected(self) -> None:
        certificate = k2_integrity_fixture()
        certificate["diameter_paths"].pop("0:1")
        with self.assertRaisesRegex(ValueError, "diameter path coverage mismatch"):
            verify.verify_candidate_integrity(certificate)

    def test_spectral_and_radical_mutations_are_rejected(self) -> None:
        mutations = {
            "root interval": lambda c: c["spectral"]["root_intervals"][0].update(
                {"left": [0, 1]}
            ),
            "energy interval": lambda c: c["spectral"].update({"energy_upper": [99, 1]}),
            "literal lower": lambda c: c.update({"literal_rhs_lower": [0, 1]}),
            "literal upper": lambda c: c.update({"literal_rhs_upper": [99, 1]}),
            "literal term": lambda c: c["literal_terms"][0].update({"lower": [0, 1]}),
            "open lower": lambda c: c.update({"center_excluding_rhs_lower": [0, 1]}),
            "open upper": lambda c: c.update({"center_excluding_rhs_upper": [99, 1]}),
            "open term": lambda c: c["center_excluding_terms"][0].update({"upper": [99, 1]}),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                certificate = copy.deepcopy(k2_integrity_fixture())
                mutate(certificate)
                with self.assertRaisesRegex(ValueError, "stored .* mismatch"):
                    verify.verify_candidate_integrity(certificate)

    def test_candidate_bytes_are_bound_to_ledger_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.json"
            ledger_path = root / "ledger.jsonl"
            terminal = root / "terminal.json"
            payload = k2_integrity_fixture()
            search.write_fsync_json(candidate, payload)
            ledger = search.ChainedLedger(ledger_path)
            ledger.append({
                "kind": "evaluation",
                "verdict": "CANDIDATE_ONLY",
                "certificate_sha256": hashlib.sha256(search.canonical_bytes(payload)).hexdigest(),
            })
            ledger.close()
            terminal.write_text(json.dumps({
                "reason": "CANDIDATE_FOUND",
                "candidate_path": "candidate.json",
            }))
            verify.verify_candidate_binding(ledger_path, terminal, candidate)
            payload["graph6"] = "A?"
            search.write_fsync_json(candidate, payload)
            with self.assertRaisesRegex(ValueError, "candidate bytes do not match"):
                verify.verify_candidate_binding(ledger_path, terminal, candidate)

    def test_k2_control_cannot_pass_the_literal_crossing_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.json"
            search.write_fsync_json(candidate, k2_integrity_fixture())
            with self.assertRaisesRegex(ValueError, "strict crossing not certified"):
                verify.verify_candidate(candidate)


if __name__ == "__main__":
    unittest.main()
