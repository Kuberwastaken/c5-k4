#!/usr/bin/env python3
"""Focused tests for the frozen Method v1.1 GitHub job runner."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import test_lint_benchmark_v11 as benchmark_fixture


SCRIPT = Path(__file__).with_name("run_benchmark_v11_job.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v11_runner", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BenchmarkRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = benchmark_fixture.BenchmarkLintTests(methodName="test_valid_c1_manifest_passes")
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.manifest = self.fixture.manifest()
        self.fixture.attach_arms(self.manifest)
        self.cluster = self.manifest["clusters"][0]

    def contract(self, mode: str, arm: str | None, count: int, cpu_budget: int) -> dict:
        if arm is None:
            seed = None
            grid = {}
            transformation = "frozen-verification" if mode == "INDEPENDENT_VERIFICATION" else "frozen-shared"
        else:
            frozen = self.cluster["arms"][arm]
            seed = frozen["seed"]
            grid = copy.deepcopy(frozen["parameter_grid"])
            transformation = frozen["transformation_id"]
        return {
            "$schema": "schemas/benchmark-run-contract-v1.schema.json",
            "schema_version": "c5k4-benchmark-run-contract-1",
            "benchmark_id": self.manifest["benchmark_id"],
            "cluster_id": self.cluster["cluster_id"],
            "job_mode": mode,
            "arm": arm,
            "process_count": count,
            "process_wall_cap_seconds": 60,
            "cpu_budget_seconds": cpu_budget,
            "seed": seed,
            "parameter_grid": grid,
            "transformation_id": transformation,
            "no_adaptation": True,
            "network_policy": "DENY",
            "processes": [
                {
                    "process_id": f"p{index}",
                    "argv": ["/usr/bin/python3", "-c", "print('bounded')"],
                    "working_directory": ".",
                    "parameter_assignment": {"index": index},
                }
                for index in range(count)
            ],
        }

    def install_contract(self, contract: dict, field: str | None = None, arm: str | None = None) -> Path:
        path = self.fixture.root / f"contract-{contract['job_mode']}-{arm or 'none'}.json"
        path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        reference = {"path": path.name, "sha256": digest(path)}
        if arm is not None:
            self.cluster["arms"][arm]["contract"] = reference
        else:
            assert field is not None
            self.cluster[field] = reference
        return path

    def write_manifest(self) -> Path:
        self.fixture.write(self.manifest)
        return self.fixture.manifest_path

    def args(self, output: Path, mode: str, arm: str = "NONE", dry_run: bool = True) -> argparse.Namespace:
        return argparse.Namespace(
            manifest=self.write_manifest(),
            cluster_id=self.cluster["cluster_id"],
            mode=mode,
            arm=arm,
            output=output,
            dry_run=dry_run,
            require_git_ancestry=False,
        )

    def test_discovery_dry_run_resolves_frozen_contract(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "CATALOGUE", 8, 480)
        self.install_contract(contract, arm="CATALOGUE")
        output = self.fixture.root / "dry-run"
        self.assertEqual(RUNNER.execute(self.args(output, "DISCOVERY_ARM", "CATALOGUE")), 0)
        metadata = json.loads((output / "run-metadata.json").read_text(encoding="utf-8"))
        self.assertTrue(metadata["dry_run"])
        self.assertEqual(metadata["process_count"], 8)
        self.assertEqual(metadata["cpu_budget_seconds"], 480)

    def test_discovery_rejects_grid_adaptation(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "GENERIC", 8, 480)
        contract["parameter_grid"] = {"changed_after_freeze": [99]}
        self.install_contract(contract, arm="GENERIC")
        with self.assertRaisesRegex(RUNNER.ContractError, "parameter_grid"):
            RUNNER.execute(self.args(self.fixture.root / "reject-grid", "DISCOVERY_ARM", "GENERIC"))

    def test_discovery_rejects_less_than_eight_processes(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "WALL_NAVIGATION", 7, 420)
        self.install_contract(contract, arm="WALL_NAVIGATION")
        with self.assertRaisesRegex(RUNNER.ContractError, "exactly 8"):
            RUNNER.execute(self.args(self.fixture.root / "reject-count", "DISCOVERY_ARM", "WALL_NAVIGATION"))

    def test_shared_analysis_honors_ten_process_ceiling(self) -> None:
        contract = self.contract("SHARED_ANALYSIS", None, 10, 600)
        self.install_contract(contract, field="shared_analysis_contract")
        output = self.fixture.root / "shared-dry-run"
        self.assertEqual(RUNNER.execute(self.args(output, "SHARED_ANALYSIS")), 0)

    def test_verification_runs_two_network_isolated_processes(self) -> None:
        contract = self.contract("INDEPENDENT_VERIFICATION", None, 2, 120)
        self.install_contract(contract, field="independent_verification_contract")
        for arm in self.cluster["arms"].values():
            arm["status"] = "TERMINATED"
        self.manifest["phase"] = "EVALUATING"
        self.manifest["chronology"]["evaluation_started_at_utc"] = "2026-08-14T06:00:00Z"
        self.cluster["evaluation_started_at_utc"] = "2026-08-14T06:00:00Z"
        output = self.fixture.root / "verification-run"
        self.assertEqual(RUNNER.execute(self.args(output, "INDEPENDENT_VERIFICATION", dry_run=False)), 0)
        summary = json.loads((output / "run-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["completed_process_count"], 2)
        self.assertEqual(summary["nonzero_processes"], [])
        self.assertTrue((output / "processes" / "p0" / "stdout.log").is_file())


if __name__ == "__main__":
    unittest.main()
