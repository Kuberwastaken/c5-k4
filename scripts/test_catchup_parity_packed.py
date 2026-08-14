#!/usr/bin/env python3
"""Target-free tests for the parity-packed Catch-Up exact-search arm."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import verify_catchup_parity_packed as verifier


class ParityPackedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.solver = Path(cls.temporary.name) / "catchup-parity-packed-test"
        source = Path(__file__).with_name("prospective_catchup_parity_packed.cpp")
        subprocess.run(
            ["g++", "-std=c++20", "-O3", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(cls.solver)],
            check=True,
            timeout=60,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def solver_rows(self, n: int) -> list[dict]:
        process = subprocess.run(
            [str(self.solver), "--small", str(n)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        return [json.loads(line) for line in process.stdout.splitlines()]

    def test_absolute_score_reference_matches_every_small_order(self) -> None:
        for n in range(1, 13):
            result = next(row for row in self.solver_rows(n) if row["event"] == "result")
            self.assertEqual(result["value"], verifier.independent_absolute_value(n))
            self.assertEqual(result["memo_bytes"], (1 << n) * 4)

    def test_even_triangular_source_controls_are_draws(self) -> None:
        for n in (3, 4, 7, 8, 11, 12):
            result = next(row for row in self.solver_rows(n) if row["event"] == "result")
            self.assertEqual(result["value"], 0)

    def test_target_is_mechanically_disabled(self) -> None:
        fake = "0" * 40
        process = subprocess.run(
            [str(self.solver), "--n24-target", "--campaign-commit", fake, "--certificate", "/tmp/forbidden"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("mechanically disabled", process.stderr)

    def test_ledger_rejects_wrong_n23_counts(self) -> None:
        commit = "1" * 40
        rows = [
            {
                "event": "run_start", "n": 23, "schema": "catchup-parity-packed-v1",
                "upstream_commit": verifier.UPSTREAM_COMMIT, "upstream_tree": verifier.UPSTREAM_TREE,
                "source_blob": verifier.SOURCE_BLOB, "source_sha256": verifier.SOURCE_SHA256,
                "campaign_commit": commit, "move_order": "ascending_set_bits",
                "mode": "n23_performance_gate", "deadline_seconds": 38.0,
                "state": "remaining_mask,current_deficit,remaining_sum",
                "memo": "uint32_per_mask_two_bits_per_parity_slot",
            },
            {
                "event": "result", "n": 23, "mode": "n23_performance_gate",
                "value": 0, "value_name": "draw", "memo_states": 1,
                "memo_bytes": (1 << 23) * 4, "calls": 1, "seconds": 1.0,
                "matches_frozen_gate": True, "certificate_emitted": False,
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "N=23"):
                verifier.verify_ledger(path, 23, commit, None)

    def test_ledger_rejects_unknown_event_and_early_timeout(self) -> None:
        commit = "3" * 40
        start = {
            "event": "run_start", "n": 24, "schema": "catchup-parity-packed-v1",
            "upstream_commit": verifier.UPSTREAM_COMMIT, "upstream_tree": verifier.UPSTREAM_TREE,
            "source_blob": verifier.SOURCE_BLOB, "source_sha256": verifier.SOURCE_SHA256,
            "campaign_commit": commit, "mode": "n24_target", "deadline_seconds": 54.0,
            "move_order": "ascending_set_bits", "state": "remaining_mask,current_deficit,remaining_sum",
            "memo": "uint32_per_mask_two_bits_per_parity_slot",
        }
        timeout_row = {
            "event": "controlled_timeout", "n": 24, "mode": "n24_target",
            "memo_states": 0, "memo_bytes": (1 << 24) * 4, "calls": 1, "seconds": 1.0,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in [start, {"event": "mystery"}, timeout_row]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown event"):
                verifier.verify_ledger(path, 24, commit, None)
            path.write_text("".join(json.dumps(row) + "\n" for row in [start, timeout_row]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "precedes"):
                verifier.verify_ledger(path, 24, commit, None)

    def test_strategy_checker_accepts_minimal_synthetic_win(self) -> None:
        # N=1 is outside target execution but is a compact checker fixture.
        commit = "2" * 40
        rows = [
            {"event": "certificate_start", "schema": "catchup-parity-packed-v1-strategy-dag", "n": 1, "campaign_commit": commit, "root_value": 1},
            {"event": "node", "mask": 0, "deficit": 1, "remaining_sum": 0, "value": -1, "edges": []},
            {"event": "root", "value": 1, "edges": [{"move": 1, "swapped": True, "child_mask": 0, "child_deficit": 1, "child_sum": 0, "child_value": -1, "move_value": 1}]},
            {"event": "certificate_end", "nodes": 1},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dag.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            verifier.verify_strategy_dag(path, 1, commit, 1)

    def test_solver_strategy_writer_replays_win_and_loss(self) -> None:
        commit = "0" * 40
        with tempfile.TemporaryDirectory() as directory:
            for n, expected in ((1, 1), (9, -1)):
                path = Path(directory) / f"n{n}.jsonl"
                process = subprocess.run(
                    [str(self.solver), "--small-certificate", str(n), "--certificate", str(path)],
                    check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
                )
                result = next(json.loads(line) for line in process.stdout.splitlines() if json.loads(line).get("event") == "result")
                self.assertEqual(result["value"], expected)
                self.assertTrue(result["certificate_emitted"])
                verifier.verify_strategy_dag(path, n, commit, expected)

    def test_strategy_checker_rejects_noncanonical_or_incomplete_dag(self) -> None:
        commit = "4" * 40
        rows = [
            {"event": "certificate_start", "schema": "catchup-parity-packed-v1-strategy-dag", "n": 2, "campaign_commit": commit, "root_value": -1},
            {"event": "node", "mask": 2, "deficit": 1, "remaining_sum": 2, "value": -1, "edges": []},
            {"event": "root", "value": -1, "edges": [{"move": 1, "swapped": True, "child_mask": 2, "child_deficit": 1, "child_sum": 2, "child_value": -1, "move_value": 1}]},
            {"event": "certificate_end", "nodes": 1},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dag.jsonl"
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            with self.assertRaises(ValueError):
                verifier.verify_strategy_dag(path, 2, commit, -1)


if __name__ == "__main__":
    unittest.main()
