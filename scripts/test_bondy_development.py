#!/usr/bin/env python3
"""Target-free tests for the frozen Bondy constructor and execution lock."""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import networkx as nx

import prospective_bondy_construct as construct
import prospective_bondy_search as search
import prospective_bondy_verify as verify

ROOT = Path(__file__).resolve().parents[1]


class SourceAndGrammarTests(unittest.TestCase):
    def test_s44_source_control_is_exact_minus_one(self) -> None:
        row = construct.source_control()
        self.assertEqual((row["k"], row["t"], row["delta_h"], row["delta_g"]), (4, 4, 3, 7))
        self.assertEqual(row["threshold"], {"numerator": 36, "denominator": 5, "ceiling": 8})
        self.assertEqual(row["scaled_degree_residual"], -1)

    def test_catalogue_is_loopless_two_factor_with_five_components(self) -> None:
        for quotient in range(len(construct.QUOTIENT_CATALOGUE)):
            for permutation in range(len(construct.PORT_PERMUTATIONS)):
                factor = construct.cross_factor(quotient, permutation)
                self.assertEqual(sorted(dict(factor.degree()).values()), [2] * 20)
                self.assertEqual(nx.number_connected_components(factor), 5)
                self.assertTrue(all(u // 4 != v // 4 for u, v in factor.edges()))

    def test_constructor_replays_only_declared_balanced_changes(self) -> None:
        graph, metadata = construct.construct_row((0, 1, 2, 0, 1), 2, 1)
        verdict, gate = construct.constructor_gate(graph, metadata)
        self.assertIn(verdict, {"APPLICABLE", "KNOWN_PROOF_DOMAIN"})
        self.assertEqual(sorted(dict(graph.degree()).values()), [4] * 20)
        self.assertEqual(len(metadata["deleted_edges"]), 10)
        self.assertEqual(len(metadata["added_edges"]), 20)
        self.assertEqual(gate.get("reason"), None)

    def test_noop_and_naive_neutral_factor_are_rejected_before_target(self) -> None:
        graph, metadata = construct.construct_row((0, 0, 0, 0, 0), 0, 0)
        neutral = dict(metadata)
        # Declaring no deletions exposes an integrity failure rather than a row.
        neutral["deleted_edges"] = []
        verdict, gate = construct.constructor_gate(graph, neutral)
        self.assertEqual((verdict, gate["reason"]), ("GATE_FAIL", "undeclared_edge_change"))
        four_cycle_factor = nx.cycle_graph(20)
        neutral["deleted_edges"] = metadata["deleted_edges"]
        neutral["added_edges"] = construct.edge_list(four_cycle_factor)
        altered = construct.source_seed()
        altered.remove_edges_from(metadata["deleted_edges"])
        altered.add_edges_from(neutral["added_edges"])
        verdict, gate = construct.constructor_gate(altered, neutral)
        self.assertNotEqual(verdict, "APPLICABLE")

    def test_claw_free_domain_check_is_exact(self) -> None:
        complete = nx.complete_graph(24)
        self.assertIsNone(construct.induced_claw(complete))
        graph, metadata = construct.construct_row((0, 1, 2, 0, 1), 2, 1)
        verdict, gate = construct.constructor_gate(graph, metadata)
        if verdict == "APPLICABLE":
            witness = gate["induced_claw"]
            center, leaves = witness[0], witness[1:]
            joined = construct.join_separator(graph)
            self.assertTrue(all(joined.has_edge(center, leaf) for leaf in leaves))
            self.assertTrue(all(not joined.has_edge(a, b) for a, b in __import__("itertools").combinations(leaves, 2)))

    def test_connectivity_deletion_audit_covers_every_set_below_four(self) -> None:
        audit = construct.universal_join_connectivity_audit()
        self.assertEqual(audit["sets_checked"], 2325)
        self.assertEqual(audit["sets_checked"], audit["expected_sets"])

    def test_constructor_prefix_is_deterministic_and_deduplicated(self) -> None:
        first = list(construct.generate(24))
        second = list(construct.generate(24))
        self.assertEqual(first, second)
        accepted = [row for row in first if row["constructor_verdict"] == "APPLICABLE"]
        labelled = [row["gate"]["labelled_sha256"] for row in accepted]
        graph6 = [row["gate"]["graph6"] for row in accepted]
        self.assertEqual(len(labelled), len(set(labelled)))
        self.assertEqual(len(graph6), len(set(graph6)))


class TargetIsolationTests(unittest.TestCase):
    def test_constructor_source_contains_no_target_evaluator(self) -> None:
        source = (ROOT / "scripts/prospective_bondy_construct.py").read_text()
        tree = ast.parse(source)
        function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        forbidden = {"target_evaluate", "maximize_q4", "circumference", "path_cover", "pcov4"}
        self.assertTrue(function_names.isdisjoint(forbidden))

    def test_constructor_tests_do_not_call_proposed_candidate_target(self) -> None:
        with mock.patch.object(search, "target_evaluate", side_effect=AssertionError("target called")), mock.patch.object(
            search, "EndpointPathCoverDP", side_effect=AssertionError("path-cover target called")
        ):
            rows = list(construct.generate(12))
            self.assertEqual(len(rows), 12)

    def test_execution_lock_fails_before_attestation_or_target(self) -> None:
        args = types.SimpleNamespace(
            enable_target=True,
            campaign_commit="0" * 40,
            activation_token="BONDY_TARGET_DISABLED",
        )
        with self.assertRaisesRegex(RuntimeError, "TARGET_EXECUTION_DISABLED"):
            search.unlock(args)

    def test_ledger_cannot_append_after_seal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = search.DurableLedger(Path(directory) / "ledger.jsonl")
            ledger.append({"kind": "fixture"})
            ledger.seal()
            with self.assertRaisesRegex(RuntimeError, "after durable"):
                ledger.append({"kind": "forbidden"})

    def test_atomic_replace_failure_does_not_publish_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "candidate.json"
            with mock.patch.object(os, "replace", side_effect=OSError("synthetic rename failure")):
                with self.assertRaisesRegex(OSError, "synthetic rename"):
                    search.atomic_json(destination, {"status": "CANDIDATE_FOUND"})
            self.assertFalse(destination.exists())

    def test_cpp_replay_rejects_malformed_and_trailing_tokens_before_dp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "replay"
            subprocess.run(
                ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                 str(ROOT / "scripts/prospective_bondy_replay.cpp"), "-o", str(binary)],
                check=True,
                timeout=30,
            )
            for payload in ("0 1\nnot-an-edge\n", "0 1 trailing-token\n"):
                edge_file = Path(directory) / "malformed.edges"
                table_file = Path(directory) / "must-not-exist.bin"
                edge_file.write_text(payload, encoding="ascii")
                completed = subprocess.run(
                    [str(binary), str(edge_file), str(table_file)],
                    text=True,
                    capture_output=True,
                    timeout=5,
                )
                self.assertEqual(completed.returncode, 3)
                self.assertIn('"status":"GATE_FAIL"', completed.stdout)
                self.assertIn("malformed edge line", completed.stdout)
                self.assertFalse(table_file.exists())

    def test_nonzero_independent_replay_is_gate_failure_not_timeout(self) -> None:
        fake = mock.Mock()
        fake.pid = 123456
        fake.returncode = 2
        fake.communicate.return_value = ('{"status":"REJECT_UPPER_BOUND","removed_mask":1}\n', None)
        fake.poll.return_value = 2
        with mock.patch.object(subprocess, "Popen", return_value=fake):
            with self.assertRaisesRegex(RuntimeError, "nonzero logical/internal exit"):
                search.independent_upper_replay(Path("/bin/true"), [], "0" * 64, 1.0)

    def test_synthetic_upper_rejection_counter_witness_replays(self) -> None:
        graph = nx.path_graph(20)
        kept = list(range(1, 20))
        result = {
            "candidate": False,
            "classification": "Q4_UPPER_BOUND_REJECTED",
            "upper_deletion_sets_completed": 2,
            "upper_rejection": {
                "X": [0],
                "removed_mask": 1,
                "kept_mask": (1 << 20) - 2,
                "pc_H_minus_X": 1,
                "cover_H_minus_X": [kept],
            },
        }
        self.assertEqual(verify.validate_upper_rejection(graph, result), {"removed": 1, "paths": 1})

    def test_full_ledger_rejects_unrecognized_fake_target_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = search.DurableLedger(Path(directory) / "ledger.jsonl")
            ledger.append({"kind": "source_control", "record": construct.source_control()})
            applicable = 0
            for row in construct.generate(construct.ROW_LIMIT):
                ledger.append({k: v for k, v in row.items() if k not in ("edges_h", "roles")})
                if row["constructor_verdict"] == "APPLICABLE":
                    applicable += 1
                    ledger.append({
                        "kind": "target_evaluation",
                        "row_index": row["row_index"],
                        "result": {
                            "candidate": False,
                            "classification": "UNRECOGNIZED_FAKE_RESULT",
                            "algorithm": "python_endpoint_path_cover_dp_v1",
                            "dp_digests": {"pc_table_sha256": "0" * 64, "endpoint_table_sha256": "0" * 64},
                            "upper_deletion_sets_completed": 1351,
                            "evaluation_seconds_millis": 0,
                        },
                    })
            ledger.seal()
            records, head = verify.verify_ledger(ledger.path)
            self.assertEqual(sum(verify.semantic_payload(record).get("kind") == "constructor_row" for record in records), 96)
            artifact = {
                "status": "DOMAIN_EXHAUSTED",
                "applicable": applicable,
                "evaluated": applicable,
                "ledger_head": head,
            }
            with self.assertRaisesRegex(RuntimeError, "missing or unknown target evaluation classification"):
                verify.verify_ledger_semantics(records, artifact)

    def test_complete_joined_edge_list_round_trips_without_target_evaluation(self) -> None:
        peripheral, _ = construct.construct_row((0, 1, 2, 0, 1), 2, 1)
        joined = construct.join_separator(peripheral)
        edges_g = construct.edge_list(joined)
        self.assertEqual(len(edges_g), 126)
        self.assertEqual(construct.edge_list(construct.graph_from_edges(24, edges_g)), edges_g)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-free", action="store_true", required=True)
    parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
