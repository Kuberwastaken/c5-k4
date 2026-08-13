#!/usr/bin/env python3
"""Focused tests for Method v1.5 future-cohort membership and closure."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from jsonschema import Draft7Validator


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v15_future_cohort as future  # noqa: E402


CLASSIFIER_PATH = ROOT / "results/benchmark/v1.4-protocol/five-strata-classifier.json"
GROUPING_PATH = ROOT / "results/benchmark/v1.4-protocol/grouping-rule.json"


class FutureCohortTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "formal.git"
        subprocess.run(["/usr/bin/git", "init", "--quiet", "-b", "main", str(self.repo)], check=True)
        self.git_run("config", "user.name", "Future cohort fixture")
        self.git_run("config", "user.email", "future@example.invalid")
        self.classifier = json.loads(CLASSIFIER_PATH.read_text())
        self.grouping = json.loads(GROUPING_PATH.read_text())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git_run(self, *args: str) -> str:
        return subprocess.run(
            ["/usr/bin/git", "-C", str(self.repo), *args], check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode().strip()

    def write(self, path: str, declaration: str | None) -> None:
        target = self.repo / path
        if declaration is None:
            target.unlink()
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(declaration, encoding="utf-8")

    def commit(self, message: str) -> str:
        self.git_run("add", "-A")
        self.git_run("commit", "--quiet", "-m", message)
        return self.git_run("rev-parse", "HEAD")

    def receipt(self, commit: str) -> dict:
        return {
            "schema_version": "fixture-receipt",
            "repository_path": str(self.repo),
            "commit": commit,
            "root_tree": self.git_run("rev-parse", f"{commit}^{{tree}}"),
            "checkpoint_ordinal": 1,
            "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "basis": {"previous_checkpoint": None},
        }

    def v14(self, rows: list[dict] | None = None) -> dict:
        return {"schema_version": "c5k4-question-cluster-pool-1.4", "clusters": rows or []}

    def ledger(self, units: list[dict] | None = None, *, fail_closed: bool = False) -> dict:
        rows = units or []
        counts = {key: 0 for key in (
            "SEMANTIC_EXPOSURE", "MACHINE_REGISTRY_CONTACT", "IMMUTABLE_SOURCE_CUSTODY", "UNKNOWN",
        )}
        for row in rows:
            counts[row["provenance_class"]] += 1
        ledger = {
            "status": "CLASSIFIED_FAIL_CLOSED" if fail_closed else "CLASSIFIED_COMPLETE",
            "source_complete": True, "fail_closed": fail_closed,
            "units": rows, "counts": counts,
        }
        ledger["ledger_sha256"] = future.identity_hits.content_address(ledger, "ledger_sha256")
        return ledger

    def build(self, u1: str, u2: str, excluded: list[dict] | None = None) -> dict:
        return future.build(
            self.receipt(u1), self.receipt(u2), self.v14(excluded), self.grouping,
            self.classifier, CLASSIFIER_PATH, input_digests={"fixture_sha256": "0" * 64},
            provenance_ledgers=[self.ledger()],
        )

    def test_new_post_u1_open_cluster_is_included_without_semantic_fields(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("U1")
        self.write(
            "FormalConjectures/GraphFresh.lean",
            "@[category research open]\n"
            "theorem graph_fresh (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6 := by sorry\n",
        )
        u2 = self.commit("new graph question")
        output = self.build(u1, u2)
        self.assertEqual(output["counts"]["included"], 1)
        row = output["records"][0]
        self.assertEqual(row["membership_status"], "INCLUDE")
        self.assertEqual(row["first_introduction_commit"], u2)
        encoded = json.dumps(output).casefold()
        for forbidden in ("statement_text", "outcome", "random_rank", "entropy_value"):
            self.assertNotIn(f'"{forbidden}":', encoded)

    def test_rename_after_u1_is_not_a_new_question(self) -> None:
        self.write(
            "FormalConjectures/GraphOld.lean",
            "@[category research open]\ntheorem old_graph (G : SimpleGraph (Fin 4)) : True := by sorry\n",
        )
        u1 = self.commit("U1 with old path")
        self.git_run("mv", "FormalConjectures/GraphOld.lean", "FormalConjectures/GraphRenamed.lean")
        u2 = self.commit("rename only")
        row = self.build(u1, u2)["records"][0]
        self.assertEqual(row["membership_status"], "EXCLUDE")
        self.assertIn("INTRODUCTION_REACHABLE_BEFORE_U1", row["exclusion_reasons"])

    def test_readd_and_reopen_are_excluded_by_reachable_history(self) -> None:
        self.write(
            "FormalConjectures/FiniteReturn.lean",
            "@[category research open]\ntheorem finite_return (n : Fin 4) : True := by sorry\n",
        )
        self.commit("original open question")
        self.write("FormalConjectures/FiniteReturn.lean", None)
        u1 = self.commit("absent at U1")
        self.write(
            "FormalConjectures/FiniteReturn.lean",
            "@[category research open]\ntheorem finite_return (n : Fin 4) : True := by sorry\n",
        )
        u2 = self.commit("readd")
        row = self.build(u1, u2)["records"][0]
        self.assertEqual(row["membership_status"], "EXCLUDE")
        self.assertIn("PATH_REACHABLE_BEFORE_U1", row["exclusion_reasons"])

    def test_reformalization_with_old_declaration_name_is_excluded(self) -> None:
        self.write(
            "FormalConjectures/FiniteOld.lean",
            "@[category research open]\ntheorem persistent_name (n : Fin 4) : True := by sorry\n",
        )
        self.commit("old formalization")
        self.write("FormalConjectures/FiniteOld.lean", None)
        u1 = self.commit("old formalization removed before U1")
        self.write(
            "FormalConjectures/FiniteNew.lean",
            "@[category research open]\ntheorem persistent_name (n : Fin 5) : True := by sorry\n",
        )
        u2 = self.commit("reformalize")
        row = self.build(u1, u2)["records"][0]
        self.assertEqual(row["membership_status"], "EXCLUDE")
        self.assertIn("DECLARATION_NAME_REACHABLE_BEFORE_U1", row["exclusion_reasons"])

    def test_rename_and_rewrite_with_new_name_fails_closed(self) -> None:
        self.write(
            "FormalConjectures/GraphOld.lean",
            "@[category research open]\ntheorem old_name (G : SimpleGraph (Fin 4)) : True := by sorry\n",
        )
        u1 = self.commit("U1 old identity")
        self.write("FormalConjectures/GraphOld.lean", None)
        self.write(
            "FormalConjectures/GraphNew.lean",
            "@[category research open]\ntheorem new_name (H : SimpleGraph (Fin 4)) : (True ∧ True) := by sorry\n",
        )
        u2 = self.commit("rename and rewrite")
        row = self.build(u1, u2)["records"][0]
        self.assertEqual(row["membership_status"], "EXCLUDE")
        self.assertIn("COINTRODUCED_WITH_FORMAL_DELETION_OR_RENAME", row["exclusion_reasons"])

    def test_unchanged_tip_is_valid_zero_delta_quota_fail(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("unchanged")
        output = self.build(u1, u1)
        self.assertEqual(output["counts"]["delta_records"], 0)
        self.assertEqual(output["quota_certificate"]["status"], "FAIL")
        self.assertEqual(output["quota_certificate"]["candidate_count"], 0)
        self.assertEqual(output["registry_sha256"], future.registry_digest(output))
        mutated = json.loads(json.dumps(output))
        mutated["counts"]["u1_open_clusters"] += 1
        self.assertNotEqual(output["registry_sha256"], future.registry_digest(mutated))

    def test_chronology_nested_receipt_crosses_registry_and_strict_schema(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("U1")
        self.write(
            "FormalConjectures/GraphFresh.lean",
            "@[category research open]\ntheorem graph_fresh_schema (G : SimpleGraph (Fin 4)) : G.edgeSet.ncard ≤ 6 := by sorry\n",
        )
        u2 = self.commit("U2")
        nested_u1 = {"upstream": {"commit": u1, "root_tree": self.git_run("rev-parse", f"{u1}^{{tree}}")}}
        nested_u2 = {
            "checkpoint_ordinal": 1,
            "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "basis": {"previous_checkpoint": None},
            "capture": {"commit": u2, "root_tree": self.git_run("rev-parse", f"{u2}^{{tree}}")},
        }
        excluded = [{
            "cluster_id": f"old-{i}", "path": f"old/{i}",
            "identity_sha256": f"{i:064x}", "module_blob_sha256": f"{i + 728:064x}",
            "declarations": [{"name": f"old_{i}", "statement_header_sha256": f"{i + 1456:064x}"}],
        } for i in range(728)]
        output = future.build(
            nested_u1, nested_u2, self.v14(excluded), self.grouping, self.classifier,
            CLASSIFIER_PATH, input_digests={"fixture_sha256": "0" * 64}, repository=self.repo,
            provenance_ledgers=[self.ledger()],
        )
        schema = json.loads((ROOT / "schemas/benchmark-future-registry-output-v1.5.schema.json").read_text())
        errors = list(Draft7Validator(schema).iter_errors(output))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_provenance_join_excludes_semantic_and_unknown_identity_hits(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("U1")
        path = "FormalConjectures/GraphExposed.lean"
        self.write(
            path,
            "@[category research open]\ntheorem exposed_name (G : SimpleGraph (Fin 4)) : True := by sorry\n",
        )
        u2 = self.commit("new exposed target")
        unit = {
            "unit_id": "semantic-unit-1",
            "locator": "session:tool-output:1", "content_sha256": hashlib.sha256(path.encode()).hexdigest(),
            "provenance_class": "SEMANTIC_EXPOSURE",
        }
        output = future.build(
            self.receipt(u1), self.receipt(u2), self.v14(), self.grouping,
            self.classifier, CLASSIFIER_PATH, input_digests={"provenance_ledger_sha256": "1" * 64},
            provenance_ledgers=[self.ledger([unit])],
            provenance_contents={unit["content_sha256"]: path.encode()},
        )
        self.assertEqual(output["records"][0]["membership_status"], "EXCLUDE")
        self.assertIn("SEMANTIC_EXPOSURE", output["records"][0]["exclusion_reasons"])
        with self.assertRaisesRegex(future.FutureCohortError, "failed closed"):
            future.build(
                self.receipt(u1), self.receipt(u2), self.v14(), self.grouping,
                self.classifier, CLASSIFIER_PATH, input_digests={"provenance_ledger_sha256": "3" * 64},
                provenance_ledgers=[self.ledger([unit])], provenance_contents={},
            )
        unit["provenance_class"] = "UNKNOWN"
        output = future.build(
            self.receipt(u1), self.receipt(u2), self.v14(), self.grouping,
            self.classifier, CLASSIFIER_PATH, input_digests={"provenance_ledger_sha256": "2" * 64},
            provenance_ledgers=[self.ledger([unit])],
            provenance_contents={unit["content_sha256"]: path.encode()},
        )
        self.assertIn("UNKNOWN_EXPOSURE", output["records"][0]["exclusion_reasons"])

    def test_v14_identity_trace_is_permanently_excluded(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("U1")
        self.write(
            "FormalConjectures/FiniteNew.lean",
            "@[category research open]\ntheorem excluded_name (n : Fin 4) : True := by sorry\n",
        )
        u2 = self.commit("new but in permanent closure")
        probe = self.build(u1, u2)["records"][0]
        excluded = [{
            "cluster_id": "historic-unrelated", "path": "old/path",
            "identity_sha256": "1" * 64, "module_blob_sha256": "2" * 64,
            "declarations": [{
                "name": "excluded_name",
                "statement_header_sha256": "3" * 64,
            }],
        }]
        row = self.build(u1, u2, excluded)["records"][0]
        self.assertEqual(probe["membership_status"], "INCLUDE")
        self.assertIn("V14_EXCLUSION_DECLARATION_NAME", row["exclusion_reasons"])

    def test_ambiguous_classifier_result_fails_closed(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("U1")
        self.write(
            "FormalConjectures/GraphMixed.lean",
            "@[category research open]\ntheorem graph_row (G : SimpleGraph (Fin 4)) : True := by sorry\n"
            "@[category research open]\ntheorem process_row (A : Automaton) : True := by sorry\n",
        )
        u2 = self.commit("ambiguous module")
        row = self.build(u1, u2)["records"][0]
        self.assertEqual(row["membership_status"], "EXCLUDE")
        self.assertIn("AMBIGUOUS_OR_UNCLASSIFIED", row["exclusion_reasons"])

    def test_checkpoint_chain_stops_at_first_passing_checkpoint(self) -> None:
        self.write("FormalConjectures/Base.lean", "def base : True := True.intro\n")
        u1 = self.commit("U1")
        self.write(
            "FormalConjectures/FiniteOne.lean",
            "@[category research open]\ntheorem finite_one (n : Fin 4) : True := by sorry\n",
        )
        u2a = self.commit("checkpoint one")
        self.write(
            "FormalConjectures/FiniteTwo.lean",
            "@[category research open]\ntheorem finite_two (n : Fin 5) : True := by sorry\n",
        )
        u2b = self.commit("checkpoint two")
        quotas = dict(future.QUOTAS)
        try:
            future.QUOTAS.clear()
            future.QUOTAS.update({key: 0 for key in future.STRATA})
            future.QUOTAS["FINITE_COMBINATORIAL"] = 2
            chain, selected = future.checkpoint_chain(
                self.receipt(u1), [
                    {"checkpoint_ordinal": 1, "checkpoint_label": "missed", "capture_status": "MISSED", "terminal_horizon": False},
                    {"checkpoint_ordinal": 2, "checkpoint_label": "first", "capture_status": "CAPTURED", "terminal_horizon": False, "receipt": self.receipt(u2a)},
                    {"checkpoint_ordinal": 3, "checkpoint_label": "second", "capture_status": "CAPTURED", "terminal_horizon": False, "receipt": self.receipt(u2b)},
                ], self.v14(), self.grouping, self.classifier, CLASSIFIER_PATH,
                input_digests={"fixture_sha256": "0" * 64},
                provenance_ledgers=[self.ledger()],
            )
        finally:
            future.QUOTAS.clear()
            future.QUOTAS.update(quotas)
        self.assertEqual(chain["first_passing_ordinal"], 3)
        self.assertEqual(chain["checkpoint_certificates"][0]["status"], "UNEVALUATED_MISSED")
        self.assertEqual(selected["upstream"]["u2_commit"], u2b)


if __name__ == "__main__":
    unittest.main()
