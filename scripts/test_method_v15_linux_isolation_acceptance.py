#!/usr/bin/env python3
"""Adversarial tests for descriptor-pinned Method v1.5 Linux isolation."""

from __future__ import annotations

import hashlib
import importlib.util
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


backend = load("method_v15_triplet_isolation_backend_acceptance_tests", ROOT / "scripts" / "method_v15_triplet_isolation_backend.py")
acceptance = load("method_v15_linux_isolation_acceptance_tests", ROOT / "scripts" / "method_v15_linux_isolation_acceptance.py")


class LinuxIsolationAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "common.json"
        self.source.write_bytes(b'{"fixture":"target-free"}\n')
        self.forbidden = self.root / "wall-analysis.json"
        self.forbidden.write_bytes(b'{"forbidden":true}\n')
        self.private_base = self.root / "private"
        self.private_base.mkdir(mode=0o700)
        cpu = min(os.sched_getaffinity(0))
        self.request = backend.IsolationRequest(
            tree_id="CATALOGUE-0",
            arm="CATALOGUE",
            argv=("/fixed/fixture",),
            cpu=cpu,
            allowed_roots=(backend.RootSpec(
                role="COMMON_TARGET_BUNDLE",
                source=self.source,
                sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(),
            ),),
            forbidden_roots=(("WALL_ANALYSIS", self.forbidden),),
            private_base=self.private_base,
        )

    def plan(self) -> dict:
        return backend.build_plan(self.request)

    def test_symlink_swap_after_pin_cannot_redirect_descriptor(self) -> None:
        plan = self.plan()
        pinned = acceptance.pin_plan_sources(plan)
        self.addCleanup(lambda: [item.close() for item in pinned])
        original_digest = pinned[0].sha256
        displaced = self.root / "displaced.json"
        self.source.rename(displaced)
        attacker = self.root / "attacker.json"
        attacker.write_bytes(b'{"attacker":true}\n')
        self.source.symlink_to(attacker)
        self.assertEqual(acceptance.pinned_digest(pinned[0].fd), original_digest)
        self.assertNotEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), original_digest)

    def test_symlink_source_is_rejected_by_openat2_without_fallback(self) -> None:
        link = self.root / "linked.json"
        link.symlink_to(self.source)
        plan = self.plan()
        plan["allowed_roots"][0]["source_path"] = str(link)
        with self.assertRaises((OSError, acceptance.IsolationAcceptanceError)):
            acceptance.pin_plan_sources(plan)

    def test_hardlink_and_device_sources_are_rejected(self) -> None:
        plan = self.plan()
        hardlink = self.root / "hardlink.json"
        os.link(self.source, hardlink)
        with self.assertRaisesRegex(acceptance.IsolationAcceptanceError, "hardlinked"):
            acceptance.pin_plan_sources(plan)
        if Path("/dev/null").exists():
            device_plan = dict(plan)
            device_plan["allowed_roots"] = [dict(plan["allowed_roots"][0])]
            device_plan["allowed_roots"][0]["source_path"] = "/dev/null"
            device_plan["allowed_roots"][0]["source_sha256"] = "0" * 64
            with self.assertRaisesRegex(acceptance.IsolationAcceptanceError, "device"):
                acceptance.pin_plan_sources(device_plan)

    def test_openat2_rejects_magic_or_parent_components(self) -> None:
        directory = os.open(self.root, os.O_PATH | os.O_DIRECTORY)
        self.addCleanup(os.close, directory)
        with self.assertRaises(acceptance.IsolationAcceptanceError):
            acceptance.openat2_beneath(directory, "../common.json", os.O_PATH)
        with self.assertRaises(acceptance.IsolationAcceptanceError):
            acceptance.openat2_beneath(directory, ".", os.O_PATH)

    def test_parent_secrets_are_not_part_of_the_worker_environment(self) -> None:
        os.environ["GITHUB_TOKEN"] = "must-not-cross"
        self.addCleanup(os.environ.pop, "GITHUB_TOKEN", None)
        result = acceptance.kernel_acceptance(self.plan())
        self.assertFalse(result["activation_permitted"])
        self.assertFalse(result["target_specific_fields_present"])
        if not result["kernel_acceptance_passed"]:
            self.skipTest("host fails closed: " + ";".join(result["remaining_blocks"]))
        self.assertTrue(result["checks"]["fixed_secret_free_environment"])

    def test_real_fixture_exercises_complete_namespace_mount_network_and_kill_closure(self) -> None:
        result = acceptance.kernel_acceptance(self.plan())
        self.assertEqual(result["status"], "PRE_P1_TARGET_FREE_KERNEL_ACCEPTANCE_NOT_OPERATIONAL")
        self.assertFalse(result["activation_permitted"])
        if not result["kernel_acceptance_passed"]:
            self.skipTest("host fails closed: " + ";".join(result["remaining_blocks"]))
        checks = result["checks"]
        for namespace in acceptance.NS_NAMES:
            self.assertTrue(checks[f"namespace_{namespace}"])
        for name in (
            "pid_one", "single_cpu", "fixed_secret_free_environment", "host_root_absent",
            "forbidden_roots_absent", "private_paths_distinct", "allowed_roots_read_only",
            "allowed_mount_set_exact", "network_denied", "whole_process_tree_kill_path",
        ):
            self.assertTrue(checks[name], name)

    def test_noncontract_plan_is_rejected_without_launch(self) -> None:
        plan = self.plan()
        plan["wall_cap_seconds"] = 59
        result = acceptance.kernel_acceptance(plan)
        self.assertFalse(result["kernel_acceptance_passed"])
        self.assertIn("PLAN_IS_NOT_THE_SEALED_PRE_P1_60_SECOND_CONTRACT", result["remaining_blocks"])


if __name__ == "__main__":
    unittest.main()
