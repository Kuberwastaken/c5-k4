#!/usr/bin/env python3
"""Adversarial tests for the inert v1.5 production triplet adapter."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


adapter = load("method_v15_triplet_production_adapter_tests", ROOT / "scripts" / "method_v15_triplet_production_adapter.py")
fixture_tests = load("run_benchmark_v15_triplet_fixture_for_adapter", ROOT / "scripts" / "test_run_benchmark_v15_triplet.py")
NONCE = hashlib.sha256(b"fresh-production-adapter-session").hexdigest()
OTHER_NONCE = hashlib.sha256(b"replayed-session").hexdigest()


class ProductionTripletAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        # Reuse the established envelope constructor rather than maintaining a
        # subtly different target-specific fixture in this adapter suite.
        self.fixture = fixture_tests.TripletLauncherTests("test_cli_is_inert_and_cannot_claim")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.private = self.fixture.root / "production-isolation"
        self.private.mkdir(mode=0o700)
        cpus = sorted(os.sched_getaffinity(0))[:2]
        self.envelope, self.matrix, self.trees = adapter.build_sealed_tree_plans(
            self.fixture.envelope_path, self.fixture.matrix_path, self.private, cpus=cpus
        )

    @staticmethod
    def passing_observation(_: dict) -> dict:
        return {
            "status": "PRE_P1_TARGET_FREE_KERNEL_ACCEPTANCE_NOT_OPERATIONAL",
            "kernel_acceptance_passed": True,
            "activation_permitted": False,
            "target_specific_fields_present": False,
            "checks": {"fixed_target_free_fixture": True, "network_denied": True},
            "remaining_blocks": ["NOT_WIRED_TO_TRIPLET_LAUNCHER", "NO_P1_ACTIVATION"],
        }

    def attestations(self) -> list[dict]:
        executor = adapter.LinuxProductionAcceptanceExecutor(self.passing_observation)
        return [executor.attest(tree, NONCE) for tree in self.trees]

    def reseal(self, value: dict) -> None:
        value["attestation_sha256"] = adapter.digest_object(value, "attestation_sha256")

    def kernel_preflight(self) -> tuple[bool, str]:
        readiness = adapter.isolation.readiness()
        probes = readiness["kernel_probes"]
        supported = (
            all(readiness["required_tools"].values())
            and probes["user_mount_network_pid_namespaces"]
            and probes["private_tmpfs_mount"]
        )
        return supported, json.dumps(
            {"required_tools": readiness["required_tools"], "kernel_probes": probes},
            sort_keys=True,
        )

    def fresh_trees(self, name: str) -> list[adapter.SealedTreePlan]:
        private = self.fixture.root / name
        private.mkdir(mode=0o700)
        _, _, trees = adapter.build_sealed_tree_plans(
            self.fixture.envelope_path,
            self.fixture.matrix_path,
            private,
            cpus=sorted(os.sched_getaffinity(0))[:2],
        )
        return trees

    def test_maps_complete_schedule_to_exact_capabilities_and_equal_limits(self) -> None:
        self.assertEqual(len(self.trees), 24)
        self.assertEqual(len({tree.tree_id for tree in self.trees}), 24)
        self.assertEqual(
            {arm: sum(tree.arm == arm for tree in self.trees) for arm in adapter.ARMS},
            {arm: 8 for arm in adapter.ARMS},
        )
        for tree in self.trees:
            capability = self.matrix["capabilities"][tree.arm]
            self.assertEqual(
                [root["root_role"] for root in tree.plan["allowed_roots"]],
                capability["allowed_root_roles"],
            )
            self.assertEqual(set(tree.plan["forbidden_root_roles"]), set(capability["forbidden_root_roles"]))
            self.assertEqual(tree.plan["wall_cap_seconds"], 60)
            self.assertEqual(tree.plan["argv"], list(adapter.FIXTURE_ARGV))
            self.assertFalse(tree.plan["implementation"]["target_launch_wired"])

    def test_all_24_same_host_acceptances_cross_only_the_inert_barrier(self) -> None:
        attestations = self.attestations()
        certificate = adapter.certify_complete_triplet(self.trees, attestations, NONCE)
        self.assertEqual(certificate["tree_count"], 24)
        self.assertEqual(len(certificate["accepted_tree_ids"]), 24)
        self.assertFalse(certificate["production_triplet_launch_permitted"])
        self.assertFalse(certificate["activation_permitted"])
        self.assertEqual(certificate["remaining_blocks"], ["TRIPLET_CLI_REMAINS_INERT", "NO_P1_ACTIVATION"])

    def test_partial_or_duplicate_acceptance_is_rejected(self) -> None:
        attestations = self.attestations()
        with self.assertRaisesRegex(adapter.AdapterError, "all 24"):
            adapter.certify_complete_triplet(self.trees, attestations[:-1], NONCE)
        duplicate = attestations[:-1] + [copy.deepcopy(attestations[0])]
        with self.assertRaisesRegex(adapter.AdapterError, "replay or duplicate"):
            adapter.certify_complete_triplet(self.trees, duplicate, NONCE)

    def test_plan_arm_host_and_implementation_mismatches_are_rejected(self) -> None:
        different_arm = next(arm for arm in adapter.ARMS if arm != self.trees[0].arm)
        mutations = (
            ("plan_sha256", "0" * 64, "different plan"),
            ("arm", different_arm, "unexpected tree or arm"),
            ("host_fingerprint_sha256", "1" * 64, "another host"),
        )
        for key, value, message in mutations:
            with self.subTest(key=key):
                rows = self.attestations()
                rows[0][key] = value
                self.reseal(rows[0])
                with self.assertRaisesRegex(adapter.AdapterError, message):
                    adapter.certify_complete_triplet(self.trees, rows, NONCE)
        rows = self.attestations()
        rows[0]["implementation"]["linux_executor_sha256"] = "2" * 64
        self.reseal(rows[0])
        with self.assertRaisesRegex(adapter.AdapterError, "implementation digest"):
            adapter.certify_complete_triplet(self.trees, rows, NONCE)

    def test_session_replay_and_failed_kernel_acceptance_are_rejected(self) -> None:
        rows = self.attestations()
        rows[0]["session_nonce_sha256"] = OTHER_NONCE
        self.reseal(rows[0])
        with self.assertRaisesRegex(adapter.AdapterError, "replayed"):
            adapter.certify_complete_triplet(self.trees, rows, NONCE)
        failed = adapter.LinuxProductionAcceptanceExecutor(lambda _: {
            "kernel_acceptance_passed": False,
            "checks": {},
            "remaining_blocks": ["NETWORK_ESCAPE"],
        }).attest(self.trees[0], NONCE)
        rows = self.attestations()
        rows[0] = failed
        with self.assertRaisesRegex(adapter.AdapterError, "did not pass"):
            adapter.certify_complete_triplet(self.trees, rows, NONCE)

    def test_injected_unsupported_host_fails_closed_and_cannot_certify(self) -> None:
        failed = adapter.LinuxProductionAcceptanceExecutor(lambda _: {
            "status": "PRE_P1_TARGET_FREE_KERNEL_ACCEPTANCE_NOT_OPERATIONAL",
            "kernel_acceptance_passed": False,
            "activation_permitted": False,
            "target_specific_fields_present": False,
            "checks": {},
            "remaining_blocks": ["HOST_NAMESPACE_POLICY_DENIED"],
        }).attest(self.trees[0], NONCE)
        self.assertFalse(failed["kernel_acceptance_passed"])
        self.assertFalse(failed["activation_permitted"])
        rows = self.attestations()
        rows[0] = failed
        with self.assertRaisesRegex(adapter.AdapterError, "did not pass kernel acceptance"):
            adapter.certify_complete_triplet(self.trees, rows, NONCE)

    def test_real_non_target_fixture_is_bounded_and_still_not_activated(self) -> None:
        row = adapter.LinuxProductionAcceptanceExecutor().attest(self.trees[0], NONCE)
        self.assertFalse(row["activation_permitted"])
        self.assertEqual(row["capture"]["wall_cap_seconds"], 60)
        self.assertLessEqual(row["capture"]["stdout"]["byte_count"], adapter.MAX_CAPTURE_BYTES)
        self.assertLessEqual(row["capture"]["stderr"]["byte_count"], adapter.MAX_CAPTURE_BYTES)
        self.assertFalse(row["capture"]["semantic_parsing_performed"])
        supported, reason = self.kernel_preflight()
        if not supported:
            self.assertFalse(row["kernel_acceptance_passed"])
            self.skipTest("host correctly fails closed: " + reason)
        self.assertTrue(row["kernel_acceptance_passed"])

    def test_real_complete_24_tree_acceptance_still_cannot_launch(self) -> None:
        supported, reason = self.kernel_preflight()
        probe = adapter.LinuxProductionAcceptanceExecutor().attest(self.trees[0], NONCE)
        self.assertFalse(probe["activation_permitted"])
        if not supported:
            self.assertFalse(probe["kernel_acceptance_passed"])
            self.skipTest("host correctly fails closed: " + reason)
        # The supported-host probe must itself pass.  A fresh root avoids
        # treating a repeated fixture directory as a host capability result.
        self.assertTrue(probe["kernel_acceptance_passed"])
        trees = self.fresh_trees("production-isolation-full-24")
        rows, certificate = adapter.attest_all(
            trees, adapter.LinuxProductionAcceptanceExecutor(), NONCE
        )
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(row["kernel_acceptance_passed"] for row in rows))
        self.assertEqual(certificate["tree_count"], 24)
        self.assertFalse(certificate["production_triplet_launch_permitted"])
        self.assertFalse(certificate["activation_permitted"])

    def test_old_predictable_scratch_collisions_are_ignored_and_untouched(self) -> None:
        old = Path("/tmp", f".c5k4-source-{os.getpid()}-3")
        old.write_bytes(b"attacker-owned-sentinel")
        self.addCleanup(old.unlink, missing_ok=True)
        row = adapter.LinuxProductionAcceptanceExecutor().attest(self.trees[0], NONCE)
        self.assertFalse(row["activation_permitted"])
        self.assertEqual(old.read_bytes(), b"attacker-owned-sentinel")
        supported, reason = self.kernel_preflight()
        if not supported:
            self.assertFalse(row["kernel_acceptance_passed"])
            self.skipTest("host correctly fails closed: " + reason)
        self.assertTrue(row["kernel_acceptance_passed"])

    def test_public_adapter_entrypoint_is_inert(self) -> None:
        self.assertEqual(adapter.main(), 2)


if __name__ == "__main__":
    unittest.main()
