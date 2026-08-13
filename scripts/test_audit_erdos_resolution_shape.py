#!/usr/bin/env python3
"""Regression tests for the Erdős declaration-shape audit."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("audit_erdos_resolution_shape.py")
SPEC = importlib.util.spec_from_file_location("erdos_shape_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def entry(number: int, informal: str, formal: str = "unformalized") -> dict:
    return {
        "number": number,
        "informal_status": {"state": informal},
        "formal_status": {"state": formal},
        "formalized": {"state": "yes"},
    }


class ShapeAuditTests(unittest.TestCase):
    def scan_one(self, number: int, source: str, status: dict):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            root = repo / "FormalConjectures" / "ErdosProblems"
            root.mkdir(parents=True)
            (root / f"{number}.lean").write_text(source, encoding="utf-8")
            rows = AUDIT.scan(repo, {str(number): status})
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_edge_coloring_without_simple_graph_is_not_omitted(self):
        row = self.scan_one(
            617,
            "@[category research open]\n"
            "theorem erdos_617 {V : Type} (coloring : Sym2 V → Fin 10) :\n"
            "    ∃ S : Finset V, S.card = 11 := by sorry\n",
            entry(617, "falsifiable"),
        )
        self.assertEqual(row.resolution_lane, "REVIEW_FINITE_NEGATION")
        self.assertTrue(row.existential_head)

    def test_eventual_quantifier_is_proof_or_family_only(self):
        row = self.scan_one(
            600,
            "@[category research open]\n"
            "theorem erdos_600 : ∀ᶠ n : ℕ in Filter.atTop, n > 0 := by sorry\n",
            entry(600, "open"),
        )
        self.assertTrue(row.eventual_or_limit)
        self.assertEqual(
            row.resolution_lane, "PROOF_OR_EXPLICIT_INFINITE_FAMILY"
        )

    def test_formal_solution_forces_status_sync_lane(self):
        row = self.scan_one(
            146,
            "@[category research open]\n"
            "theorem erdos_146 : True := by trivial\n",
            entry(146, "open", formal="Lean"),
        )
        self.assertEqual(row.resolution_lane, "STATUS_OR_PROOF_SYNC")


if __name__ == "__main__":
    unittest.main()
