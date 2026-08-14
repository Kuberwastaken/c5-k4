#!/usr/bin/env python3
"""Unit and contract tests for the frozen Graffiti³ Conjecture 2 worker."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import networkx as nx

import search_graffiti3_conjecture2 as search


class ArithmeticTests(unittest.TestCase):
    def test_dyadic_sqrt_bounds_are_outward(self) -> None:
        lower, upper = search.sqrt_dyadic_bounds(2, bits=12)
        self.assertLessEqual(lower * lower, 2)
        self.assertGreaterEqual(upper * upper, 2)
        self.assertLess(upper - lower, Fraction(1, 1 << 12) + Fraction(1, 1 << 20))

    def test_perfect_square_has_exact_bound(self) -> None:
        self.assertEqual(search.sqrt_dyadic_bounds(81), (Fraction(9), Fraction(9)))

    def test_d2_is_closed_ball_and_includes_self(self) -> None:
        self.assertEqual(search.d2_values(nx.path_graph(4)), {0: 3, 1: 4, 2: 4, 3: 3})

    def test_star_is_exact_equality_with_leaf_witness(self) -> None:
        graph = nx.star_graph(5)
        witness = (1, 2, 3, 4, 5)
        search.validate_witness(graph, witness)
        form = search.rga2_radical_normal_form(graph)
        self.assertTrue(search.is_exact_integer(form, len(witness)))
        lower, upper, _ = search.rga2_bounds(graph)
        self.assertEqual((lower, upper), (Fraction(5), Fraction(5)))


class ConstructorTests(unittest.TestCase):
    def test_frozen_file_hashes_match_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((
            root / "results/expansion/live-search-2026-08-14/graffiti3-conjecture2-manifest.json"
        ).read_text())
        for relative, expected in manifest["frozen_files"].items():
            self.assertEqual(hashlib.sha256((root / relative).read_bytes()).hexdigest(), expected)

    def test_exact_isomorphism_deduplicator_rejects_relabelling(self) -> None:
        dedup = search.IsomorphismDeduplicator()
        graph = nx.path_graph(7)
        relabelled = nx.relabel_nodes(graph, {v: (3 * v + 1) % 7 for v in graph})
        self.assertTrue(dedup.add_if_new(graph))
        self.assertFalse(dedup.add_if_new(relabelled))

    def test_wall_constructors_are_applicable_and_witnesses_replay(self) -> None:
        rows = list(search.wall_graphs())
        self.assertGreater(len(rows), 100)
        for _, graph, witness in rows:
            self.assertGreaterEqual(graph.number_of_nodes(), 2)
            self.assertTrue(nx.is_connected(graph))
            if witness is not None:
                search.validate_witness(graph, witness)

    def test_generic_constructor_is_deterministic(self) -> None:
        first = [(name, search.graph6(graph)) for name, graph, _ in search.generic_graphs(count=8)]
        second = [(name, search.graph6(graph)) for name, graph, _ in search.generic_graphs(count=8)]
        self.assertEqual(first, second)

    def test_terminal_never_conflates_prefix_with_exhaustion(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for reason, exhausted in (("DOMAIN_EXHAUSTED", True), ("DEADLINE_PREFIX", False)):
                path = root / f"{reason}.json"
                search.write_terminal(path, "CATALOGUE", reason, 3, 2, 2)
                self.assertIs(json.loads(path.read_text())["domain_exhausted"], exhausted)


if __name__ == "__main__":
    unittest.main()
