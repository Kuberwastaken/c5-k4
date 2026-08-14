#!/usr/bin/env python3
"""Static contract checks for the phase-four GitHub Actions workflow."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/txgraffiti-cc-phase4.yml"
MANIFEST = ROOT / "results/expansion/live-search-2026-08-14/txgraffiti-cc-phase4-manifest.json"


class Phase4WorkflowTests(unittest.TestCase):
    def test_manual_read_only_exact_commit_workflow(self) -> None:
        value = yaml.load(WORKFLOW.read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(value["permissions"], {"contents": "read"})
        self.assertIn("workflow_dispatch", value["on"])
        self.assertEqual(
            set(value["jobs"]), {"prepare-domain", "evaluate-partition", "aggregate"}
        )
        matrix = value["jobs"]["evaluate-partition"]["strategy"]["matrix"]["partition"]
        self.assertEqual([int(item) for item in matrix], list(range(24)))
        self.assertEqual(value["jobs"]["evaluate-partition"]["strategy"]["max-parallel"], "8")

    def test_hard_caps_and_immutable_artifacts_are_explicit(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn("--wall-seconds 60", text)
        self.assertIn("INTERNAL_STOP_SECONDS = 54.0", (ROOT / "scripts/search_txgraffiti_cc_phase4.py").read_text())
        self.assertIn("SOLVER_CAP_SECONDS = 4.0", (ROOT / "scripts/search_txgraffiti_cc_phase4.py").read_text())
        self.assertIn("persist-credentials: false", text)
        self.assertIn("github.run_id", text)
        self.assertIn("github.run_attempt", text)
        self.assertNotIn("contents: write", text)

    def test_nauty_binary_is_portable_and_smoked_at_each_trust_boundary(self) -> None:
        text = WORKFLOW.read_text()
        self.assertIn(
            "./configure --enable-generic --disable-popcnt --disable-clz",
            text,
        )
        self.assertNotIn("\n          ./configure\n", text)
        self.assertEqual(text.count("printf 'Dhc\\n'"), 3)
        self.assertEqual(text.count(")\" = DqK"), 3)

        manifest = json.loads(MANIFEST.read_text())
        chronology = manifest["campaign_chronology"]
        self.assertEqual(chronology["invalid_run_id"], 31788725249)
        self.assertEqual(chronology["invalid_run_status"], "INVALID_RUN")
        self.assertIs(chronology["mathematical_inference_allowed"], False)
        self.assertIs(manifest["post_failure_infrastructure_replay"], True)

    def test_domain_is_built_once_and_workers_consume_worklists(self) -> None:
        text = WORKFLOW.read_text()
        self.assertEqual(text.count("txgraffiti_cc_phase4_domain.py build"), 1)
        self.assertIn("work-partition-${partition_label}.jsonl", text)
        self.assertIn("aggregate_txgraffiti_cc_phase4.py", text)
        self.assertIn("if: always()", text)

    def test_frozen_file_hashes_match_manifest(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        for relative, expected in manifest["frozen_files"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)


if __name__ == "__main__":
    unittest.main()
