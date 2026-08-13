#!/usr/bin/env python3
"""Focused tests for the Method v1.2 isolated equal-budget runner."""

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


SCRIPT = Path(__file__).with_name("run_benchmark_v12_job.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v12_runner", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BenchmarkV12RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest_path = self.root / "benchmark.json"
        self.cluster = {
            "cluster_id": "opaque-cluster-01",
            "runnable": True,
            "evaluation_started_at_utc": None,
            "shared_analysis_contract": None,
            "independent_verification_contract": None,
            "arms": {
                arm: {
                    "status": "PENDING",
                    "seed": f"seed-{arm.lower()}",
                    "parameter_grid": {"fixed": [1, 2]},
                    "transformation_id": f"frozen-{arm.lower()}",
                    "no_adaptation": True,
                    "contract": {"path": "not-installed", "sha256": "0" * 64},
                }
                for arm in RUNNER.ARMS
            },
        }
        self.manifest = {
            "schema_version": "c5k4-benchmark-1.2",
            "benchmark_id": "method-v1.2-test",
            "phase": "C1_SELECTED",
            "chronology": {"c1_attestation_commit": "a" * 40},
            "budgets": {
                "discovery_arm": {
                    "process_tree_count": 8,
                    "process_wall_cap_seconds": 60,
                    "cpu_budget_seconds": 480,
                },
                "shared_analysis": {
                    "process_tree_count": 10,
                    "process_wall_cap_seconds": 60,
                    "cpu_budget_seconds": 600,
                },
                "independent_verification": {
                    "process_tree_count": 2,
                    "process_wall_cap_seconds": 60,
                    "cpu_budget_seconds": 120,
                },
            },
            "clusters": [self.cluster],
        }

    def contract(self, mode: str, arm: str | None, count: int, cpu_budget: int) -> dict:
        if arm is None:
            seed = None
            grid = {}
            transformation = (
                "frozen-verification" if mode == "INDEPENDENT_VERIFICATION" else "frozen-shared"
            )
        else:
            frozen = self.cluster["arms"][arm]
            seed = frozen["seed"]
            grid = copy.deepcopy(frozen["parameter_grid"])
            transformation = frozen["transformation_id"]
        return {
            "$schema": "schemas/benchmark-run-contract-v1.2.schema.json",
            "schema_version": "c5k4-benchmark-run-contract-1.2",
            "benchmark_version": "c5k4-benchmark-1.2",
            "benchmark_id": self.manifest["benchmark_id"],
            "cluster_id": self.cluster["cluster_id"],
            "job_mode": mode,
            "arm": arm,
            "process_tree_count": count,
            "process_tree_wall_cap_seconds": 60,
            "cpu_budget_seconds": cpu_budget,
            "seed": seed,
            "parameter_grid": grid,
            "transformation_id": transformation,
            "no_adaptation": True,
            "continue_after_crossing": True,
            "cross_arm_result_inputs": [],
            "results_embargo": "UNTIL_ALL_DISCOVERY_ARMS_TERMINATE",
            "network_policy": "DENY",
            "process_tree_isolation": "ONE_CPU_PROCESS_GROUP_NETWORK_NAMESPACE",
            "ledger_policy": {
                "format": "JSONL_HASH_CHAIN_V1",
                "append_only": True,
                "hash_algorithm": "SHA256",
                "genesis_previous_sha256": "0" * 64,
                "sequence_origin": 0,
            },
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

    def install_contract(self, contract: dict, arm: str | None = None) -> Path:
        path = self.root / f"contract-{contract['job_mode']}-{arm or 'none'}.json"
        path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        reference = {"path": str(path), "sha256": digest(path)}
        if arm is not None:
            self.cluster["arms"][arm]["contract"] = reference
        elif contract["job_mode"] == "SHARED_ANALYSIS":
            self.cluster["shared_analysis_contract"] = reference
        else:
            self.cluster["independent_verification_contract"] = reference
        return path

    def write_manifest(self) -> Path:
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8")
        return self.manifest_path

    def args(self, output: Path, mode: str, arm: str = "NONE") -> argparse.Namespace:
        return argparse.Namespace(
            manifest=self.write_manifest(),
            cluster_id=self.cluster["cluster_id"],
            mode=mode,
            arm=arm,
            output=output,
            dry_run=True,
            require_git_ancestry=False,
        )

    @staticmethod
    def clean_linter(_: Path) -> list:
        return []

    def test_discovery_dry_run_freezes_exact_equal_budget(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "CATALOGUE", 8, 480)
        self.install_contract(contract, arm="CATALOGUE")
        output = self.root / "dry-run"
        self.assertEqual(
            RUNNER.execute(
                self.args(output, "DISCOVERY_ARM", "CATALOGUE"), self.clean_linter
            ),
            0,
        )
        metadata = json.loads((output / "run-metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["process_tree_count"], 8)
        self.assertEqual(metadata["cpu_budget_seconds"], 480)
        self.assertTrue(metadata["continue_after_crossing"])
        self.assertEqual(metadata["cross_arm_result_inputs"], [])
        self.assertEqual(len(RUNNER.verify_ledger(output / "runtime-ledger.jsonl")), 2)

    def test_discovery_rejects_any_nonpending_sibling_arm(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "GENERIC", 8, 480)
        self.install_contract(contract, arm="GENERIC")
        self.cluster["arms"]["CATALOGUE"]["status"] = "TERMINATED"
        with self.assertRaisesRegex(RUNNER.ContractError, "all-PENDING barrier"):
            RUNNER.execute(
                self.args(self.root / "reject-shared-result", "DISCOVERY_ARM", "GENERIC"),
                self.clean_linter,
            )

    def test_schema_rejects_seventh_discovery_tree(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "WALL_NAVIGATION", 7, 420)
        self.install_contract(contract, arm="WALL_NAVIGATION")
        with self.assertRaisesRegex(RUNNER.ContractError, "contract schema failure"):
            RUNNER.execute(
                self.args(self.root / "reject-count", "DISCOVERY_ARM", "WALL_NAVIGATION"),
                self.clean_linter,
            )

    def test_rejects_cross_arm_input_or_crossing_stop(self) -> None:
        contract = self.contract("DISCOVERY_ARM", "CATALOGUE", 8, 480)
        contract["cross_arm_result_inputs"] = ["another-arm/result.json"]
        contract["continue_after_crossing"] = False
        self.install_contract(contract, arm="CATALOGUE")
        with self.assertRaisesRegex(RUNNER.ContractError, "contract schema failure"):
            RUNNER.execute(
                self.args(self.root / "reject-information", "DISCOVERY_ARM", "CATALOGUE"),
                self.clean_linter,
            )

    def test_shared_analysis_rejects_underdeclared_cpu_budget(self) -> None:
        contract = self.contract("SHARED_ANALYSIS", None, 10, 540)
        self.install_contract(contract)
        with self.assertRaisesRegex(RUNNER.ContractError, "upper bound exceeds"):
            RUNNER.execute(
                self.args(self.root / "reject-shared-budget", "SHARED_ANALYSIS"),
                self.clean_linter,
            )

    def test_shared_analysis_accepts_at_most_six_hundred_cpu_seconds(self) -> None:
        contract = self.contract("SHARED_ANALYSIS", None, 10, 600)
        self.install_contract(contract)
        self.assertEqual(
            RUNNER.execute(
                self.args(self.root / "shared", "SHARED_ANALYSIS"), self.clean_linter
            ),
            0,
        )

    def test_verification_is_exactly_two_trees_after_all_arms(self) -> None:
        contract = self.contract("INDEPENDENT_VERIFICATION", None, 2, 120)
        self.install_contract(contract)
        for frozen in self.cluster["arms"].values():
            frozen["status"] = "TERMINATED"
        self.cluster["evaluation_started_at_utc"] = "2026-08-14T06:00:00Z"
        self.manifest["phase"] = "EVALUATING"
        self.assertEqual(
            RUNNER.execute(
                self.args(self.root / "verification", "INDEPENDENT_VERIFICATION"),
                self.clean_linter,
            ),
            0,
        )

    def test_complete_process_set_runs_after_crossing_result(self) -> None:
        processes = [{"process_id": f"p{index}"} for index in range(8)]
        called: list[str] = []

        def worker(process: dict, _: int) -> dict:
            called.append(process["process_id"])
            return {"process_id": process["process_id"], "outcome": "CROSS"}

        results, errors = RUNNER.run_all_processes(processes, list(range(8)), worker)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 8)
        self.assertCountEqual(called, [f"p{index}" for index in range(8)])

    def test_append_only_ledger_detects_tampering(self) -> None:
        ledger = self.root / "runtime.jsonl"
        RUNNER.append_ledger(ledger, "ONE", {"value": 1})
        before = ledger.read_bytes()
        RUNNER.append_ledger(ledger, "TWO", {"value": 2})
        after = ledger.read_bytes()
        self.assertTrue(after.startswith(before))
        rows = RUNNER.verify_ledger(ledger)
        self.assertEqual(len(rows), 2)
        tampered = after.replace(b'"value":1', b'"value":9', 1)
        ledger.write_bytes(tampered)
        with self.assertRaisesRegex(RUNNER.ContractError, "invalid digest"):
            RUNNER.verify_ledger(ledger)

    def test_process_environment_is_a_secret_free_fixed_allowlist(self) -> None:
        environment = RUNNER.sanitized_environment(
            self.root / "isolated", "p0", "benchmark", "cluster", "DISCOVERY_ARM", "GENERIC"
        )
        self.assertNotIn("GITHUB_TOKEN", environment)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", environment)
        self.assertEqual(environment["C5K4_ARM"], "GENERIC")
        self.assertEqual(environment["C5K4_BENCHMARK_VERSION"], "1.2")


if __name__ == "__main__":
    unittest.main()
