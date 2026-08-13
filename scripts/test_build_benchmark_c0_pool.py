#!/usr/bin/env python3
"""Regression tests for the semantics-blind C0 pool builder."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_c0_pool as pool


ROOT = Path(__file__).parents[1]
CLASSIFIER = ROOT / "results" / "benchmark" / "c0" / "five-strata-classifier.json"


class PoolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = json.loads(CLASSIFIER.read_text(encoding="utf-8"))

    def test_five_strata_and_ambiguous_module(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            files = {
                "FormalConjectures/G/Scalar.lean":
                    "@[category research open]\ntheorem gs (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6 := by sorry\n",
                "FormalConjectures/G/Structural.lean":
                    "@[category research open]\ntheorem gp (G : SimpleGraph (Fin 4)) : G.Connected := by sorry\n",
                "FormalConjectures/Other/EquationalTheories_X.lean":
                    "@[category research open]\ntheorem ae (G : Type) [Fintype G] [Magma G] : True := by sorry\n",
                "FormalConjectures/Paper/CatchUpFixture.lean":
                    "@[category research open]\ntheorem agp (state : Fin 4) : True := by sorry\n",
                "FormalConjectures/OEIS/Fixture.lean":
                    "@[category research open]\ntheorem fc (n : Fin 4) : True := by sorry\n",
                "FormalConjectures/G/Mixed.lean":
                    "@[category research open]\ntheorem m1 (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6 := by sorry\n"
                    "@[category research open]\ntheorem m2 (G : SimpleGraph (Fin 4)) : G.Connected := by sorry\n",
            }
            for name, text in files.items():
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "FormalConjectures"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=t@example.com", "commit", "-qm", "fixture"],
                check=True,
            )
            upstream, declarations = pool.extract(repo, "HEAD", self.rules)
            inventory = pool.build_inventory(upstream, declarations, CLASSIFIER)
            built = pool.build_pool(inventory, "0" * 64, CLASSIFIER)
            observed = {row["machine_stratum"] for row in built["clusters"]}
            self.assertEqual(
                observed,
                {
                    "GRAPH_SCALAR_INEQUALITY",
                    "GRAPH_STRUCTURAL_PROPERTY",
                    "FINITE_ALGEBRA_EQUATIONAL",
                    "AUTOMATA_GAME_PROCESS",
                    "FINITE_COMBINATORIAL",
                    None,
                },
            )
            mixed = next(row for row in built["clusters"] if row["path"].endswith("Mixed.lean"))
            self.assertEqual(mixed["classification_status"], "AMBIGUOUS_EXCLUDE")
            self.assertFalse(mixed["eligible"])
            self.assertEqual(mixed["eligibility_scope"], "PRE_CONTAMINATION")

    def test_artifact_emits_no_statement_text_or_selection(self) -> None:
        metadata = pool.syntax_metadata(
            "FormalConjectures/G/X.lean",
            "theorem secret (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6",
            self.rules,
        )
        self.assertEqual(pool.classify(metadata)[0], "GRAPH_SCALAR_INEQUALITY")
        encoded = pool.pretty_json(metadata)
        self.assertNotIn("secret", encoded)
        self.assertNotIn("selected", encoded.casefold())

    def test_unclassified_and_infinite_domains_fail_closed(self) -> None:
        unknown = pool.syntax_metadata(
            "FormalConjectures/NumberTheory/X.lean",
            "theorem x (r : Real) : True",
            self.rules,
        )
        self.assertEqual(pool.classify(unknown), (None, "UNCLASSIFIED_WITHOUT_FINITE_SIGNAL"))
        infinite_algebra = pool.syntax_metadata(
            "FormalConjectures/Algebra/X.lean",
            "theorem x (G : Type) [Group G] : True",
            self.rules,
        )
        self.assertEqual(pool.classify(infinite_algebra), (None, "ALGEBRA_WITHOUT_FINITE_SIGNAL"))
        infinite_graph = pool.syntax_metadata(
            "FormalConjectures/Graph/X.lean",
            "theorem x (G : SimpleGraph V) : G.Connected",
            self.rules,
        )
        self.assertEqual(pool.classify(infinite_graph), (None, "GRAPH_WITHOUT_FINITE_SIGNAL"))
        section_finite_graph = pool.syntax_metadata(
            "FormalConjectures/Graph/X.lean",
            "theorem x (G : SimpleGraph V) : G.Connected",
            self.rules,
            "variable [Fintype V]",
        )
        self.assertEqual(pool.classify(section_finite_graph)[0], "GRAPH_STRUCTURAL_PROPERTY")


if __name__ == "__main__":
    unittest.main()
