#!/usr/bin/env python3
"""Adversarial tests for the PRE-P1 Method v1.5 triplet launcher."""

from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_benchmark_v15_triplet.py"
SPEC = importlib.util.spec_from_file_location("run_benchmark_v15_triplet", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)

MATRIX_PATH = ROOT / "results/benchmark/v1.5-protocol/arm-capability-matrix.json"
ZERO = "0" * 64
ONE = "1" * 64
COMMIT_A = "a" * 40
COMMIT_B = "b" * 40


def seal(value: dict, key: str) -> dict:
    value[key] = launcher.envelope_validator.content_digest(value, key)
    return value


def fixed_rules() -> dict:
    return {
        "arms": list(launcher.ARMS),
        "all_three_pending_barrier": True,
        "validate_complete_triplet_before_claim": True,
        "equal_discovery_budget": {
            "process_trees_per_arm": 8,
            "wall_seconds_per_tree": 60,
            "cpu_seconds_per_arm_max": 480,
        },
        "baseline_contract_precommit_before_wall_analysis": True,
        "no_adaptation": True,
        "cross_arm_result_inputs": [],
        "continue_after_crossing": True,
        "result_reveal": "ONLY_AFTER_ALL_THREE_ARMS_TERMINATE",
        "intermediate_result_delivery_permitted": False,
        "one_shot_claim_required": True,
        "claim_update_rule": "APPEND_ONLY_ATOMIC_NORMAL_FAST_FORWARD",
        "network_policy": "DENY",
        "filesystem_isolation": "SEPARATE_READ_ONLY_INPUT_AND_PRIVATE_WRITABLE_MOUNT_NAMESPACES",
        "shared_writable_root_permitted": False,
        "target_process_launching_implemented": False,
    }


class TripletLauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.campaign = self.root / "campaign"
        self.campaign.mkdir()
        self.state = self.root / "state"
        self.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        self.envelope_path = self.root / "envelope.json"
        self.matrix_path = self.root / "matrix.json"
        self.matrix_path.write_text(json.dumps(self.matrix) + "\n", encoding="utf-8")
        self.envelope = self.make_envelope()
        self.write_envelope()

    def make_envelope(self) -> dict:
        output_paths = {
            "CATALOGUE_RESULT": str(self.root / "declared-results" / "catalogue"),
            "GENERIC_RESULT": str(self.root / "declared-results" / "generic"),
            "WALL_NAVIGATION_RESULT": str(self.root / "declared-results" / "wall"),
        }
        roots = []
        for index, role in enumerate(self.matrix["root_roles"]):
            if role in output_paths:
                roots.append({
                    "root_role": role,
                    "path": output_paths[role],
                    "sha256": None,
                    "access": "PRIVATE_RESULT_OUTPUT",
                })
                continue
            relative = f"inputs/{index:02d}-{role.lower()}.json"
            path = self.campaign / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"frozen-{role}\n".encode())
            roots.append({
                "root_role": role,
                "path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "access": "READ_ONLY_INPUT",
            })
        by_role = {root["root_role"]: root for root in roots}

        def reference(role: str) -> dict:
            root = by_role[role]
            return {"path": root["path"], "sha256": root["sha256"]}

        arms = {}
        for arm, contract_role, result_role in (
            ("CATALOGUE", "CATALOGUE_CONTRACT", "CATALOGUE_RESULT"),
            ("GENERIC", "GENERIC_CONTRACT", "GENERIC_RESULT"),
            ("WALL_NAVIGATION", "WALL_CONTRACT", "WALL_NAVIGATION_RESULT"),
        ):
            arms[arm] = {
                "status": "PENDING",
                "contract": reference(contract_role),
                "seed": f"seed-{arm.lower()}",
                "parameter_grid": {"frozen": [0, 1]},
                "transformation_id": f"frozen-{arm.lower()}",
                "process_tree_count": 8,
                "process_tree_wall_cap_seconds": 60,
                "cpu_budget_seconds": 480,
                "no_adaptation": True,
                "continue_after_crossing": True,
                "cross_arm_result_inputs": [],
                "allowed_digest_root_roles": list(self.matrix["capabilities"][arm]["allowed_root_roles"]),
                "forbidden_digest_root_roles": list(self.matrix["capabilities"][arm]["forbidden_root_roles"]),
                "writable_root": output_paths[result_role],
            }
        return seal({
            "schema": "c5k4-method-v1.5-execution-envelope-1.0",
            "artifact_kind": "THREE_ARM_EXECUTION_ENVELOPE",
            "protocol_version": "1.5",
            "status": "POST_C1_RUN_FREEZE_DRAFT_NOT_EXECUTABLE",
            "target_specific_fields_present": True,
            "capability_matrix": {
                "path": "results/benchmark/v1.5-protocol/arm-capability-matrix.json",
                "sha256": self.matrix["matrix_sha256"],
            },
            "fixed_rules": fixed_rules(),
            "target_execution": {
                "benchmark_id": "method-v1.5-test",
                "cluster_id": "future-cluster-test",
                "campaign_checkout": str(self.campaign),
                "c1_attestation_commit": COMMIT_A,
                "run_freeze_commit": COMMIT_B,
                "digest_roots": roots,
                "baseline_contract_precommit": {
                    "commit": COMMIT_A,
                    "recorded_at_utc": "2027-01-01T00:00:00Z",
                    "CATALOGUE": copy.deepcopy(arms["CATALOGUE"]["contract"]),
                    "GENERIC": copy.deepcopy(arms["GENERIC"]["contract"]),
                },
                "wall_analysis_first_delivered_at_utc": "2027-01-01T00:00:01Z",
                "arms": arms,
                "one_shot_claim": {
                    "state": "UNCLAIMED",
                    "claim_ref": "refs/heads/method-v1.5-execution-claims",
                    "claim_nonce_sha256": ONE,
                    "prior_claims_permitted": False,
                    "update_rule": "APPEND_ONLY_ATOMIC_NORMAL_FAST_FORWARD",
                },
                "reveal": {
                    "condition": "ALL_THREE_ARMS_TERMINATED",
                    "intermediate_logs_permitted": False,
                    "intermediate_artifacts_permitted": False,
                    "combined_record_only": True,
                },
            },
            "envelope_sha256": ZERO,
        }, "envelope_sha256")

    def write_envelope(self) -> None:
        self.envelope_path.write_text(json.dumps(self.envelope) + "\n", encoding="utf-8")

    @staticmethod
    def clock() -> str:
        return "2027-01-01T00:00:02Z"

    def good_kernel(self, seen: list[launcher.TreeInvocation] | None = None):
        def kernel(invocation: launcher.TreeInvocation) -> launcher.KernelCompletion:
            if seen is not None:
                seen.append(invocation)
            self.assertFalse((self.state / launcher.COMBINED_NAME).exists())
            return launcher.KernelCompletion(
                returncode=0,
                stdout=f"stdout-{invocation.tree_id}".encode(),
                stderr=b"",
                artifact=f"opaque-{invocation.tree_id}".encode(),
                accessed_root_roles=tuple(root.role for root in invocation.allowed_roots),
                network_denied=True,
            )
        return kernel

    def execute(self, kernel=None) -> dict:
        return launcher.execute_with_test_kernel(
            self.envelope_path,
            self.matrix_path,
            self.state,
            test_kernel=kernel or self.good_kernel(),
            cpus=[0, 1],
            now=self.clock,
        )

    def test_complete_triplet_is_balanced_isolated_and_revealed_once(self) -> None:
        seen: list[launcher.TreeInvocation] = []
        record = self.execute(self.good_kernel(seen))
        self.assertEqual(len(seen), 24)
        self.assertEqual({inv.arm for inv in seen}, set(launcher.ARMS))
        self.assertEqual(
            {arm: sum(inv.arm == arm for inv in seen) for arm in launcher.ARMS},
            {arm: 8 for arm in launcher.ARMS},
        )
        self.assertEqual(len({inv.private_test_buffer_root for inv in seen}), 24)
        self.assertEqual(len({inv.environment for inv in seen}), 24)
        for invocation in seen:
            environment = dict(invocation.environment)
            allowed = {root.role for root in invocation.allowed_roots}
            self.assertEqual(invocation.network_policy, "DENY")
            self.assertEqual(environment["C5K4_NETWORK_POLICY"], "DENY")
            self.assertEqual(
                allowed,
                set(self.matrix["capabilities"][invocation.arm]["allowed_root_roles"]),
            )
            self.assertFalse(allowed & launcher.RESULT_ROLES)
            self.assertNotIn("GITHUB_TOKEN", environment)
        self.assertEqual(record["status"], "PRE_P1_TEST_ONLY_TRIPLET_TERMINATED_NOT_OPERATIONAL")
        self.assertEqual(record["violations"], [])
        self.assertTrue((self.state / launcher.CLAIM_NAME).is_file())
        self.assertTrue((self.state / launcher.COMBINED_NAME).is_file())
        launcher.validate_schema(
            record, "benchmark-triplet-combined-record-v1.5.schema.json", "combined"
        )

    def test_all_24_are_submitted_before_any_result_can_drive_control(self) -> None:
        barrier = threading.Barrier(24)
        entered: list[str] = []
        lock = threading.Lock()

        def kernel(invocation: launcher.TreeInvocation) -> launcher.KernelCompletion:
            with lock:
                entered.append(invocation.tree_id)
            barrier.wait(timeout=5)
            return launcher.KernelCompletion(
                returncode=0, stdout=b"CROSS", stderr=b"", artifact=b"candidate",
                accessed_root_roles=(), network_denied=True,
            )

        record = self.execute(kernel)
        self.assertEqual(len(entered), 24)
        self.assertEqual(
            record["execution_guarantees"]["result_driven_control_adaptation_performed"], False
        )
        self.assertEqual(
            sum(len(record["arms"][arm]["completions"]) for arm in launcher.ARMS), 24
        )

    def test_sealed_order_and_rotated_schedule_are_deterministic_and_balanced(self) -> None:
        order = launcher.sealed_arm_order(self.envelope["envelope_sha256"])
        schedule = launcher.balanced_schedule(order)
        self.assertEqual(order, launcher.sealed_arm_order(self.envelope["envelope_sha256"]))
        self.assertEqual(len(schedule), 24)
        for position in range(3):
            counts = {
                arm: sum(schedule[index][0] == arm for index in range(position, 24, 3))
                for arm in launcher.ARMS
            }
            self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)

    def test_retry_and_prior_claim_are_rejected_before_second_kernel_call(self) -> None:
        seen: list[launcher.TreeInvocation] = []
        self.execute(self.good_kernel(seen))
        with self.assertRaisesRegex(launcher.TripletError, "retry is forbidden"):
            self.execute(self.good_kernel(seen))
        self.assertEqual(len(seen), 24)

    def test_partial_envelope_is_rejected_before_claim(self) -> None:
        del self.envelope["target_execution"]["arms"]["GENERIC"]
        seal(self.envelope, "envelope_sha256")
        self.write_envelope()
        with self.assertRaisesRegex(launcher.TripletError, "execution envelope rejected"):
            self.execute()
        self.assertFalse(self.state.exists())

    def test_tampered_input_is_rejected_before_claim(self) -> None:
        root = next(
            item for item in self.envelope["target_execution"]["digest_roots"]
            if item["access"] == "READ_ONLY_INPUT"
        )
        (self.campaign / root["path"]).write_bytes(b"tampered\n")
        with self.assertRaisesRegex(launcher.TripletError, "digest mismatch"):
            self.execute()
        self.assertFalse(self.state.exists())

    def test_envelope_capability_escape_is_rejected_before_claim(self) -> None:
        arm = self.envelope["target_execution"]["arms"]["CATALOGUE"]
        arm["allowed_digest_root_roles"].append("WALL_ANALYSIS")
        arm["forbidden_digest_root_roles"].remove("WALL_ANALYSIS")
        seal(self.envelope, "envelope_sha256")
        self.write_envelope()
        with self.assertRaisesRegex(launcher.TripletError, "allowed digest-root closure"):
            self.execute()
        self.assertFalse(self.state.exists())

    def test_kernel_capability_escape_is_rejected_only_after_full_barrier(self) -> None:
        called: list[str] = []

        def kernel(invocation: launcher.TreeInvocation) -> launcher.KernelCompletion:
            called.append(invocation.tree_id)
            return launcher.KernelCompletion(
                returncode=0, stdout=b"", stderr=b"", artifact=b"opaque",
                accessed_root_roles=("WALL_ANALYSIS",), network_denied=True,
            )

        with self.assertRaises(launcher.TripletRejected) as caught:
            self.execute(kernel)
        self.assertEqual(len(called), 24)
        self.assertTrue((self.state / launcher.COMBINED_NAME).is_file())
        self.assertEqual(
            caught.exception.record["status"],
            "PRE_P1_TEST_ONLY_TRIPLET_REJECTED_NOT_OPERATIONAL",
        )
        self.assertTrue(any("CAPABILITY_ESCAPE" in row for row in caught.exception.record["violations"]))

    def test_network_attestation_failure_does_not_cancel_siblings(self) -> None:
        called: list[str] = []

        def kernel(invocation: launcher.TreeInvocation) -> launcher.KernelCompletion:
            called.append(invocation.tree_id)
            return launcher.KernelCompletion(
                returncode=0, stdout=b"", stderr=b"", artifact=b"",
                accessed_root_roles=(), network_denied=invocation.tree_index != 0,
            )

        with self.assertRaises(launcher.TripletRejected) as caught:
            self.execute(kernel)
        self.assertEqual(len(called), 24)
        self.assertEqual(
            sum("NETWORK_DENIAL_NOT_ATTESTED" in item for item in caught.exception.record["violations"]),
            3,
        )

    def test_cli_is_inert_and_cannot_claim(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = launcher.main([
                "--matrix", str(self.matrix_path),
                "--envelope", str(self.envelope_path),
                "--state-dir", str(self.state),
            ])
        self.assertEqual(rc, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertFalse(self.state.exists())

    def test_malformed_cli_is_also_silent(self) -> None:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = launcher.main([])
        self.assertEqual(rc, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
