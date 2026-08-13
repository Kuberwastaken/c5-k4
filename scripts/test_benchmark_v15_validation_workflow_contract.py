#!/usr/bin/env python3
"""Static security contract for the non-scheduled Method v1.5 validator."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1].resolve()
WORKFLOW = ROOT / ".github/workflows/method-v15-validation.yml"


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


class ValidationWorkflowContractTests(unittest.TestCase):
    def test_validation_triggers_are_non_scheduled(self) -> None:
        text = workflow_text()
        header = text.split("permissions:", 1)[0]
        for required in ("  push:\n", "  pull_request:\n", "  workflow_dispatch:\n"):
            self.assertIn(required, header)
        for forbidden in ("  schedule:\n", "  repository_dispatch:\n", "  workflow_call:\n"):
            self.assertNotIn(forbidden, header)

    def test_permissions_and_checkout_are_read_only(self) -> None:
        text = workflow_text()
        permission_block = text.split("permissions:", 1)[1].split("concurrency:", 1)[0]
        self.assertEqual(permission_block.strip(), "contents: read")
        self.assertIn("persist-credentials: false", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn("lfs: true", text)
        self.assertNotIn("contents: write", text)

    def test_all_v15_python_and_json_contracts_are_discovered(self) -> None:
        text = workflow_text()
        for required in (
            "-name '*v15*.py'",
            "-name 'test_*v15*.py'",
            "Path('schemas').glob('*v1.5*.json')",
            "Path('results/benchmark').glob('v1.5*/**/*.json')",
            "Draft7Validator.check_schema(value)",
        ):
            self.assertIn(required, text)

    def test_environment_and_dependencies_are_pinned(self) -> None:
        text = workflow_text()
        for required in (
            "python-version: '3.12.9'",
            "PYTHONDONTWRITEBYTECODE: '1'",
            "PYTHONHASHSEED: '0'",
            "TZ: UTC",
            "cryptography==44.0.1",
            "jsonschema==3.2.0",
        ):
            self.assertIn(required, text)
        uses = re.findall(r"(?m)^\s+uses:\s+([^#\s]+)(?:\s+#.*)?$", text)
        self.assertTrue(uses)
        for action in uses:
            self.assertRegex(action, r"^[^@]+@[0-9a-f]{40}$")

    def test_validator_cannot_activate_or_run_checkpointing_or_lean(self) -> None:
        text = workflow_text().casefold()
        for forbidden in (
            "method-v15-checkpoint.py",
            "run_benchmark_v15_checkpoint.py",
            "frozen_p1_executable",
            "git push",
            " lake ",
            "elan",
            "lean/",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
