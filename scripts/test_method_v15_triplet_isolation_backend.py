#!/usr/bin/env python3
"""Acceptance tests for the non-activated Method v1.5 isolation backend."""

from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "method_v15_triplet_isolation_backend.py"
SPEC = importlib.util.spec_from_file_location("method_v15_triplet_isolation_backend", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
backend = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = backend
SPEC.loader.exec_module(backend)


class TripletIsolationBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.common = self.inputs / "common.json"
        self.contract = self.inputs / "contract.json"
        self.forbidden = self.inputs / "wall-analysis.json"
        self.common.write_bytes(b'{"common":true}\n')
        self.contract.write_bytes(b'{"contract":"catalogue"}\n')
        self.forbidden.write_bytes(b'{"wall":true}\n')
        self.request = backend.IsolationRequest(
            tree_id="CATALOGUE-0",
            arm="CATALOGUE",
            argv=("/usr/bin/python3", "-c", "print('non-target-fixture')"),
            cpu=0,
            allowed_roots=(
                self.spec("COMMON_TARGET_BUNDLE", self.common),
                self.spec("CATALOGUE_CONTRACT", self.contract),
            ),
            forbidden_roots=(("WALL_ANALYSIS", self.forbidden),),
            private_base=self.root / "private",
        )

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def spec(self, role: str, path: Path) -> backend.RootSpec:
        return backend.RootSpec(role=role, source=path, sha256=self.digest(path))

    def test_plan_freezes_namespace_mount_network_budget_and_environment_contract(self) -> None:
        plan = backend.build_plan(self.request)
        backend.validate_plan(plan)
        self.assertEqual(plan["wall_cap_seconds"], 60)
        self.assertEqual(plan["cpu_affinity"], 0)
        self.assertEqual(plan["network"], {
            "policy": "DENY", "new_namespace": True,
            "interfaces_brought_up": [], "dns_files_mounted": [],
        })
        self.assertEqual(set(plan["namespaces"]), {
            "user", "mount", "network", "pid", "ipc", "uts", "map_root_user", "kill_child",
        })
        self.assertTrue(all(plan["namespaces"][name] for name in ("user", "mount", "network", "pid", "ipc", "uts")))
        self.assertEqual(plan["namespaces"]["kill_child"], "KILL")
        self.assertFalse(plan["root_filesystem"]["host_root_visible"])
        self.assertEqual(
            {row["root_role"] for row in plan["allowed_roots"]},
            {"COMMON_TARGET_BUNDLE", "CATALOGUE_CONTRACT"},
        )
        self.assertTrue(all(not row["writable"] for row in plan["allowed_roots"]))
        self.assertEqual(plan["forbidden_root_roles"], ["WALL_ANALYSIS"])
        self.assertEqual(set(plan["environment"]), backend.FIXED_ENV_KEYS)
        self.assertFalse(set(plan["environment"]) & backend.SECRET_NAMES)
        self.assertFalse(plan["implementation"]["target_launch_wired"])
        self.assertFalse(plan["implementation"]["fd_pinned_mounts"])
        self.assertFalse(plan["implementation"]["production_claim_permitted"])

    def test_injected_executor_accepts_only_the_complete_enforcement_closure(self) -> None:
        observed: list[dict] = []

        def fake(plan: dict) -> backend.AcceptanceObservation:
            observed.append(plan)
            return backend.AcceptanceObservation({name: True for name in backend.ALL_CHECKS})

        plan = backend.build_plan(self.request)
        record = backend.exercise_with_injected_executor(plan, fake)
        self.assertEqual(len(observed), 1)
        self.assertTrue(record["accepted"])
        self.assertEqual(record["plan_sha256"], plan["plan_sha256"])
        self.assertEqual(record["status"], "PRE_P1_FAKE_EXECUTOR_ACCEPTANCE_ONLY_NOT_OPERATIONAL")
        backend.validate_schema(
            record, "benchmark-triplet-isolation-acceptance-v1.5.schema.json", "acceptance"
        )

    def test_any_failed_enforcement_check_is_not_accepted(self) -> None:
        checks = {name: True for name in backend.ALL_CHECKS}
        checks["forbidden_roots_absent"] = False
        record = backend.exercise_with_injected_executor(
            backend.build_plan(self.request),
            lambda _: backend.AcceptanceObservation(checks),
        )
        self.assertFalse(record["accepted"])

    def test_injected_executor_cannot_omit_or_invent_checks(self) -> None:
        incomplete = {name: True for name in backend.ALL_CHECKS[:-1]}
        with self.assertRaisesRegex(backend.IsolationError, "exact acceptance closure"):
            backend.exercise_with_injected_executor(
                backend.build_plan(self.request),
                lambda _: backend.AcceptanceObservation(incomplete),
            )
        invented = {name: True for name in backend.ALL_CHECKS}
        invented["target_result_was_good"] = True
        with self.assertRaisesRegex(backend.IsolationError, "exact acceptance closure"):
            backend.exercise_with_injected_executor(
                backend.build_plan(self.request),
                lambda _: backend.AcceptanceObservation(invented),
            )

    def test_plan_tampering_and_secret_environment_injection_are_rejected(self) -> None:
        plan = backend.build_plan(self.request)
        plan["cpu_affinity"] = 1
        with self.assertRaisesRegex(backend.IsolationError, "self-digest"):
            backend.validate_plan(plan)
        plan = backend.build_plan(self.request)
        plan["environment"]["GITHUB_TOKEN"] = "secret"
        plan["plan_sha256"] = backend.object_digest(plan, "plan_sha256")
        with self.assertRaisesRegex(backend.IsolationError, "secret-free closure"):
            backend.validate_plan(plan)
        plan = backend.build_plan(self.request)
        plan["private_paths"]["cache"] = plan["private_paths"]["home"] + "/nested-cache"
        plan["plan_sha256"] = backend.object_digest(plan, "plan_sha256")
        with self.assertRaisesRegex(backend.IsolationError, "working paths overlap"):
            backend.validate_plan(plan)

    def test_symlink_source_escape_is_rejected(self) -> None:
        link = self.inputs / "linked.json"
        link.symlink_to(self.common)
        request = copy.copy(self.request)
        request = backend.IsolationRequest(
            **{**request.__dict__, "allowed_roots": (backend.RootSpec("COMMON_TARGET_BUNDLE", link, self.digest(self.common)),)}
        )
        with self.assertRaisesRegex(backend.IsolationError, "symlink|non-canonical"):
            backend.build_plan(request)

    def test_hardlinked_source_escape_is_rejected(self) -> None:
        original = self.inputs / "hard-original.json"
        linked = self.inputs / "hard-linked.json"
        original.write_bytes(b"hardlink\n")
        os.link(original, linked)
        request = backend.IsolationRequest(
            **{**self.request.__dict__, "allowed_roots": (self.spec("COMMON_TARGET_BUNDLE", original),)}
        )
        with self.assertRaisesRegex(backend.IsolationError, "hardlinked"):
            backend.build_plan(request)

    def test_device_and_fifo_source_escapes_are_rejected(self) -> None:
        if Path("/dev/null").exists():
            device = backend.RootSpec("COMMON_TARGET_BUNDLE", Path("/dev/null"), "0" * 64)
            request = backend.IsolationRequest(
                **{**self.request.__dict__, "allowed_roots": (device,)}
            )
            with self.assertRaisesRegex(backend.IsolationError, "device node"):
                backend.build_plan(request)
        fifo = self.inputs / "escape.fifo"
        os.mkfifo(fifo)
        request = backend.IsolationRequest(
            **{**self.request.__dict__, "allowed_roots": (backend.RootSpec("COMMON_TARGET_BUNDLE", fifo, "0" * 64),)}
        )
        with self.assertRaisesRegex(backend.IsolationError, "FIFO"):
            backend.build_plan(request)

    def test_allowed_forbidden_and_private_source_overlap_are_rejected(self) -> None:
        request = backend.IsolationRequest(
            **{**self.request.__dict__, "forbidden_roots": (("WALL_ANALYSIS", self.inputs),)}
        )
        with self.assertRaisesRegex(backend.IsolationError, "allowed and forbidden"):
            backend.build_plan(request)
        request = backend.IsolationRequest(
            **{**self.request.__dict__, "private_base": self.inputs}
        )
        with self.assertRaisesRegex(backend.IsolationError, "private destination overlaps"):
            backend.build_plan(request)

    def test_target_free_readiness_is_always_false_with_fully_positive_fake_probe(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "", "")
        value = backend.readiness(
            resolver=lambda name: f"/usr/bin/{name}",
            runner=lambda *args, **kwargs: completed,
        )
        self.assertEqual(value["required_tools"], {name: True for name in backend.TOOLS})
        self.assertEqual(value["kernel_probes"], {
            "user_mount_network_pid_namespaces": True,
            "private_tmpfs_mount": True,
        })
        self.assertFalse(value["operational_ready"])
        self.assertFalse(value["activation_permitted"])
        self.assertFalse(value["launcher_wired"])
        self.assertFalse(value["target_specific_fields_present"])

    def test_missing_tool_skips_probes_and_remains_nonoperational(self) -> None:
        calls: list[object] = []

        def runner(*args, **kwargs):
            calls.append(args)
            raise AssertionError("probe must not run")

        value = backend.readiness(
            resolver=lambda name: None if name == "unshare" else f"/usr/bin/{name}",
            runner=runner,
        )
        self.assertEqual(calls, [])
        self.assertFalse(value["kernel_probes"]["user_mount_network_pid_namespaces"])
        self.assertFalse(value["kernel_probes"]["private_tmpfs_mount"])
        self.assertFalse(value["operational_ready"])

    @unittest.skipUnless(shutil.which("unshare"), "Linux unshare is unavailable")
    def test_real_target_free_namespace_and_tmpfs_smoke_when_kernel_permits(self) -> None:
        value = backend.readiness()
        self.assertFalse(value["operational_ready"])
        if not value["kernel_probes"]["user_mount_network_pid_namespaces"]:
            self.skipTest("kernel policy denies unprivileged namespace smoke")
        self.assertTrue(value["kernel_probes"]["user_mount_network_pid_namespaces"])
        self.assertTrue(value["kernel_probes"]["private_tmpfs_mount"])

    def test_cli_writes_only_target_free_nonoperational_readiness(self) -> None:
        destination = self.root / "readiness.json"
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(backend.main(["--readiness-output", str(destination)]), 0)
        value = json.loads(destination.read_text(encoding="utf-8"))
        self.assertFalse(value["operational_ready"])
        self.assertFalse(value["target_specific_fields_present"])
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(backend.main(["--readiness-output", str(destination)]), 2)
            self.assertEqual(backend.main([]), 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
