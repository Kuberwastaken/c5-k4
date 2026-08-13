#!/usr/bin/env python3
"""Regression tests for the syntax-only Method v1.3 prototype builder."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v13_pool as pool  # noqa: E402


CLASSIFIER = (
    ROOT / "results" / "benchmark" / "v1.3-prototype" / "five-strata-classifier.json"
)
AUTHORITATIVE_CLASSIFIER = (
    ROOT / "results" / "benchmark" / "v1.3-protocol" / "five-strata-classifier.json"
)


class PoolV13Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = json.loads(CLASSIFIER.read_text(encoding="utf-8"))

    def metadata(self, path: str, declaration: str, module_prefix: str = ""):
        match = pool.DECLARATION.search(declaration)
        assert match is not None
        return pool.syntax_metadata(
            path, declaration, match.end(), self.rules, module_prefix + declaration
        )

    def test_ordered_binder_hypothesis_does_not_force_scalar(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem structural (G : SimpleGraph (Fin 4)) (h : G.edgeSet.ncard ≤ 6) : G.Connected",
        )
        self.assertFalse(metadata["outer_ordered_relation_conclusion"])
        self.assertEqual(pool.classify(metadata)[0], "GRAPH_STRUCTURAL_PROPERTY")

    def test_outer_conclusion_relation_forces_scalar(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem scalar (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6",
        )
        self.assertTrue(metadata["outer_ordered_relation_conclusion"])
        self.assertEqual(pool.classify(metadata)[0], "GRAPH_SCALAR_INEQUALITY")

    def test_top_level_implication_uses_consequent_relation(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem scalar (G : SimpleGraph (Fin 4)) : G.Connected → G.edgeSet.ncard ≤ 6",
        )
        self.assertTrue(metadata["outer_ordered_relation_conclusion"])

    def test_parenthesized_outer_relation_is_scalar(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem scalar (G : SimpleGraph (Fin 4)) : (G.edgeSet.ncard ≤ 6)",
        )
        self.assertTrue(metadata["outer_ordered_relation_conclusion"])
        self.assertEqual(pool.classify(metadata)[0], "GRAPH_SCALAR_INEQUALITY")

    def test_nested_ordered_term_is_not_outer_relation(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem structural (G : SimpleGraph (Fin 4)) : SomePredicate (G.edgeSet.ncard ≤ 6)",
        )
        self.assertFalse(metadata["outer_ordered_relation_conclusion"])

    def test_module_wide_simplegraph_signal_classifies_declaration(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/ErdosProblems/Fixture.lean",
            "theorem indirect (n : Fin 4) : True",
            "import Mathlib.Combinatorics.SimpleGraph.Basic\n",
        )
        self.assertTrue(metadata["graph_module"])
        self.assertEqual(pool.classify(metadata)[0], "GRAPH_STRUCTURAL_PROPERTY")

    def test_module_wide_process_signal_and_fourth_path(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Arxiv/CurlingNumberConjecture.lean",
            "theorem process (n : Nat) : True",
        )
        self.assertTrue(metadata["automata_game_process_path"])
        self.assertEqual(pool.classify(metadata)[0], "AUTOMATA_GAME_PROCESS")

    def test_bounded_output_has_no_statement_or_selection(self) -> None:
        metadata = self.metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem secret (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6",
        )
        upstream = {"commit": pool.PINNED_COMMIT, "tree": pool.PINNED_TREE}
        declaration = {
            "declaration_id": "FormalConjectures/Fixture/X.lean::secret",
            "path": "FormalConjectures/Fixture/X.lean",
            "name": "secret",
            "kind": "theorem",
            "category_line": 1,
            "module_blob_sha256": "1" * 64,
            "statement_header_sha256": "2" * 64,
            "syntax_metadata": metadata,
            "machine_stratum": "GRAPH_SCALAR_INEQUALITY",
            "classification_basis": "FINITE_GRAPH_WITH_OUTER_ORDERED_CONCLUSION",
        }
        inventory = pool.build_inventory(upstream, [declaration], CLASSIFIER)
        built = pool.build_pool(inventory, "3" * 64, CLASSIFIER)
        encoded = pool.pretty_json(built).casefold()
        self.assertNotIn("edgeset", encoded)
        self.assertNotIn("random_rank", encoded)
        self.assertNotIn("selected_cluster", encoded)
        self.assertFalse(built["selection_fields_present"])

    def test_classifier_and_executable_have_same_exact_pin(self) -> None:
        self.assertEqual(self.rules["upstream"]["commit"], pool.PINNED_COMMIT)
        self.assertEqual(self.rules["upstream"]["tree"], pool.PINNED_TREE)

    def test_authoritative_classifier_has_executable_rules_matching_prototype(self) -> None:
        authoritative = json.loads(AUTHORITATIVE_CLASSIFIER.read_text(encoding="utf-8"))
        self.assertEqual(authoritative["schema_version"], "c5k4-five-strata-classifier-1.3")
        for key in ("domain_signals", "graph_scalar_signal", "finite_signal", "cluster_rule", "output_policy"):
            self.assertEqual(authoritative[key], self.rules[key])
        self.assertEqual(
            authoritative["classification_algorithm"]["multiple_domain_signals"],
            "MULTIPLE_DOMAIN_SIGNALS",
        )
        self.assertEqual(
            [row["basis"] for row in authoritative["classification_algorithm"]["branches"]],
            [
                "GRAPH_WITHOUT_FINITE_SIGNAL",
                "FINITE_GRAPH_WITH_OUTER_ORDERED_CONCLUSION",
                "FINITE_GRAPH_WITHOUT_OUTER_ORDERED_CONCLUSION",
                "ALGEBRA_AND_FINITE_SIGNALS",
                "ALGEBRA_WITHOUT_FINITE_SIGNAL",
                "AUTOMATA_GAME_PROCESS_SYNTAX_SIGNAL",
                "EXPLICIT_FINITE_SIGNAL",
                "UNCLASSIFIED_WITHOUT_FINITE_SIGNAL",
            ],
        )

    def test_authoritative_regexes_execute_with_builder_semantics(self) -> None:
        authoritative = json.loads(AUTHORITATIVE_CLASSIFIER.read_text(encoding="utf-8"))
        match = pool.DECLARATION.search(
            "theorem scalar (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6"
        )
        assert match is not None
        metadata = pool.syntax_metadata(
            "FormalConjectures/Fixture/X.lean",
            "theorem scalar (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6",
            match.end(),
            authoritative,
            "",
        )
        self.assertEqual(pool.classify(metadata), (
            "GRAPH_SCALAR_INEQUALITY",
            "FINITE_GRAPH_WITH_OUTER_ORDERED_CONCLUSION",
        ))


if __name__ == "__main__":
    unittest.main()
