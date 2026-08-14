#!/usr/bin/env python3
"""Focused tests for the Method v1.5 live-search scientific runtime."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest

import networkx as nx


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RUNTIME = load("c5k4_test_v15_live_runtime", HERE / "method_v15_live_search_runtime.py")
LINTER = load("c5k4_test_v15_live_linter", HERE / "lint_method_v15_live_search_output.py")
LABELG = Path(
    "/Users/kuber.mehta/Projects/breakthroughmaxxing/07-marlin/"
    "total-coloring-n12-d6-m25-minimal/nauty2_8_9/labelg"
)


@unittest.skipUnless(LABELG.is_file(), "nauty labelg fixture is unavailable")
class ScientificRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_exact_canonicalization_deduplicates_relabelings_and_flushes_each_row(self) -> None:
        output = self.root / "tree.jsonl"
        ledger = RUNTIME.ScientificJsonl(output, "GENERIC", 3)
        recorder = RUNTIME.GraphSearchRecorder(ledger, RUNTIME.LabelgCanonicalizer(LABELG))
        graph = nx.house_graph()
        relabeled = nx.relabel_nodes(graph, {index: (index * 3 + 1) % 5 for index in graph})

        def evaluate(value):
            return {"objective": -1, "crossing": True, "n": len(value)}

        first = recorder.evaluate(graph, lambda _: True, evaluate)
        second = recorder.evaluate(relabeled, lambda _: True, evaluate)
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        # The candidate row is already durable before a summary is written.
        durable_prefix = output.read_bytes()
        self.assertTrue(durable_prefix.endswith(b"\n"))
        self.assertEqual(len(durable_prefix.splitlines()), 2)
        self.assertEqual(LINTER.lint_jsonl(output, allow_timeout_prefix=True, labelg=LABELG), [])

        ledger.finish()
        self.assertEqual(LINTER.lint_jsonl(output, labelg=LABELG), [])
        rows = [json.loads(line) for line in output.read_text().splitlines()]
        self.assertEqual(rows[-1]["counters"], {
            "proposed": 2,
            "canonical_unique": 1,
            "hypothesis_survivor": 1,
            "exact_evaluated": 1,
            "objective_scored": 1,
        })
        self.assertEqual(first["canonical_sha256"], recorder.canonicalizer.canonicalize(relabeled).sha256)

    def test_five_counters_distinguish_duplicate_filter_and_unscored_evaluation(self) -> None:
        output = self.root / "counters.jsonl"
        ledger = RUNTIME.ScientificJsonl(output, "CATALOGUE", 0)
        recorder = RUNTIME.GraphSearchRecorder(ledger, RUNTIME.LabelgCanonicalizer(LABELG))
        self.assertIsNone(recorder.evaluate(nx.path_graph(4), lambda _: False, lambda _: {}))
        row = recorder.evaluate(
            nx.cycle_graph(5), lambda _: True,
            lambda _: {"objective": None, "crossing": None, "reason": "not scored"},
        )
        self.assertIsNotNone(row)
        self.assertEqual(row["counters"], {
            "proposed": 2,
            "canonical_unique": 2,
            "hypothesis_survivor": 1,
            "exact_evaluated": 1,
            "objective_scored": 0,
        })
        ledger.finish()
        self.assertEqual(LINTER.lint_jsonl(output, labelg=LABELG), [])

    def test_linter_rejects_corrupt_chain_and_success_without_summary(self) -> None:
        output = self.root / "bad.jsonl"
        ledger = RUNTIME.ScientificJsonl(output, "WALL_NAVIGATION", 7)
        self.assertTrue(any(
            row.code == "TERMINAL_SUMMARY" for row in LINTER.lint_jsonl(output, labelg=LABELG)
        ))
        row = json.loads(output.read_text().splitlines()[0])
        row["counters"]["proposed"] = 4
        output.write_text(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        codes = {
            finding.code for finding in LINTER.lint_jsonl(
                output, allow_timeout_prefix=True, labelg=LABELG
            )
        }
        self.assertIn("ROW_DIGEST", codes)

    def test_hard_cap_kills_a_term_ignoring_process(self) -> None:
        command = [
            sys.executable,
            "-c",
            "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)",
        ]
        started = time.monotonic()
        result = RUNTIME.run_arm_process(
            command,
            arm="GENERIC",
            tree_index=0,
            output=self.root / "unused.jsonl",
            labelg=LABELG,
            cap_seconds=0.05,
        )
        self.assertTrue(result.timed_out)
        self.assertLess(time.monotonic() - started, 2.0)
        self.assertNotEqual(result.returncode, 0)

    def test_arm_wrapper_rejects_stale_output(self) -> None:
        output = self.root / "stale.jsonl"
        output.write_text("stale\n")
        with self.assertRaisesRegex(RUNTIME.LiveSearchRuntimeError, "must not pre-exist"):
            RUNTIME.run_arm_process(
                [sys.executable, "-c", "pass"],
                arm="CATALOGUE",
                tree_index=0,
                output=output,
                labelg=LABELG,
                cap_seconds=0.1,
            )


class CanonicalizerFailureTests(unittest.TestCase):
    def test_nonisomorphic_labelg_output_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            fake = root / "labelg"
            fake.write_text("#!/bin/sh\necho 'Dhc'\n")  # C5, regardless of input
            fake.chmod(0o755)
            canonicalizer = RUNTIME.LabelgCanonicalizer(fake)
            with self.assertRaisesRegex(RUNTIME.LiveSearchRuntimeError, "not isomorphic"):
                canonicalizer.canonicalize(nx.path_graph(4))

    def test_empty_output_is_not_a_valid_zero_exit_scientific_result(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            findings = LINTER.lint_jsonl(Path(raw) / "missing.jsonl")
            self.assertEqual(findings[0].code, "OUTPUT_MISSING")


if __name__ == "__main__":
    unittest.main()
