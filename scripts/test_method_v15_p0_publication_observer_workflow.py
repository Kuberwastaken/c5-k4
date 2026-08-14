#!/usr/bin/env python3
"""Closed-shape contract test for the read-only P0/A0 publication observer."""

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/method-v15-p0-publication-observer.yml"
CHECKOUT = "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803"
SETUP = "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"


class ObserverWorkflowTests(unittest.TestCase):
    def test_observer_is_pinned_read_only_first_attempt_and_exact_path(self) -> None:
        value = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        self.assertEqual(set(value), {"name", "on", "permissions", "jobs"})
        self.assertEqual(value["permissions"], {"contents": "read"})
        trigger = value["on"]["push"]
        self.assertEqual(trigger["branches"], ["method-v1.5-p0"])
        self.assertEqual(trigger["paths"], [
            "results/benchmark/v1.5-p0-a0/P0A.json",
            "results/benchmark/v1.5-p0-a0/P0T.json",
            "results/benchmark/v1.5-p0-a0/A0.json",
        ])
        self.assertEqual(set(value["jobs"]), {"verify-exact-publication"})
        job = value["jobs"]["verify-exact-publication"]
        self.assertEqual(job["runs-on"], "ubuntu-24.04")
        self.assertEqual(job["steps"][0], {"uses": CHECKOUT, "with": {"fetch-depth": "4", "persist-credentials": "false"}})
        self.assertEqual(job["steps"][1], {"uses": SETUP, "with": {"python-version": "3.12.9"}})
        install = job["steps"][2]["run"]
        for pin in ("cryptography==44.0.1", "jsonschema==3.2.0"):
            self.assertIn(pin, install)
        run = job["steps"][3]["run"]
        for required in (
            'test "$GITHUB_RUN_ATTEMPT" = "1"', 'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"',
            'test "${#changed[@]}" = "1"', '--stage "$stage" --commit "$GITHUB_SHA"',
        ):
            self.assertIn(required, run)
        self.assertNotIn("permissions: write", WORKFLOW.read_text())


if __name__ == "__main__":
    unittest.main()
