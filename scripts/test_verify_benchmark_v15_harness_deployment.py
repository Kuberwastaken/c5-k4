#!/usr/bin/env python3
"""Adversarial tests for the inert dedicated-host deployment acceptance."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_benchmark_v15_harness_deployment.py"
SPEC = importlib.util.spec_from_file_location("verify_harness_deployment", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)
CONTRACT_PATH = ROOT / "results" / "benchmark" / "v1.5-protocol" / "controlled-harness-deployment-contract.json"


class FakeInspector(module.HostInspector):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.ownership: dict[str, tuple[int, int]] = {}
        self.responses = {
            ("getenforce",): subprocess.CompletedProcess([], 0, "Enforcing\n", ""),
            ("systemctl", "is-active", "c5k4-harness.service"): subprocess.CompletedProcess([], 3, "inactive\n", ""),
            ("systemctl", "is-enabled", "c5k4-harness.service"): subprocess.CompletedProcess([], 0, "static\n", ""),
            ("ss", "-H", "-lntup"): subprocess.CompletedProcess([], 0, "", ""),
        }

    def stat(self, absolute: str) -> os.stat_result:
        info = super().stat(absolute)
        uid, gid = self.ownership.get(absolute, (info.st_uid, info.st_gid))
        values = list(info)
        values[4], values[5] = uid, gid
        return os.stat_result(values)

    def command(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            return self.responses[tuple(argv)]
        except KeyError as exc:
            raise module.DeploymentError(f"unexpected fixture command: {argv}") from exc


class HarnessDeploymentTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.contract = module.load_object(CONTRACT_PATH)
        self.inspector = FakeInspector(self.root)

        def directory(path: str, mode: int, uid: int, gid: int) -> None:
            target = module.rooted(self.root, path)
            target.mkdir(parents=True, exist_ok=True)
            target.chmod(mode)
            self.inspector.ownership[path] = (uid, gid)

        directory("/etc", 0o755, 0, 0)
        directory("/etc/systemd/system", 0o755, 0, 0)
        directory("/usr/lib/sysusers.d", 0o755, 0, 0)
        directory("/usr/lib/tmpfiles.d", 0o755, 0, 0)
        directory("/etc/c5k4-harness", 0o755, 0, 0)
        directory("/opt/c5k4", 0o755, 0, 0)
        directory("/var/lib/c5k4-harness", 0o700, 988, 988)
        directory("/run/c5k4-harness", 0o700, 988, 988)
        (self.root / "etc/os-release").write_text('ID="amzn"\nVERSION_ID="2023"\n', encoding="utf-8")
        (self.root / "etc/passwd").write_text(
            "root:x:0:0:root:/root:/bin/bash\n"
            "c5k4-harness:x:988:988:C5-K4 harness:/var/lib/c5k4-harness:/sbin/nologin\n",
            encoding="utf-8",
        )
        (self.root / "etc/group").write_text("root:x:0:\nc5k4-harness:x:988:\n", encoding="utf-8")

        installed = {
            "/etc/systemd/system/c5k4-harness.service": "systemd_unit",
            "/usr/lib/sysusers.d/c5k4-harness.conf": "sysusers",
            "/usr/lib/tmpfiles.d/c5k4-harness.conf": "tmpfiles",
            "/etc/c5k4-harness/network-policy.json": "network_policy",
            "/etc/c5k4-harness/destructive-gap-plan.json": "destructive_gap_plan",
        }
        for destination, key in installed.items():
            target = module.rooted(self.root, destination)
            shutil.copyfile(ROOT / self.contract["assets"][key], target)
            target.chmod(0o444)
            self.inspector.ownership[destination] = (0, 0)

    def verify(self) -> dict:
        return module.verify(self.contract, self.inspector)

    def test_exact_scaffold_is_valid_but_inert(self) -> None:
        result = self.verify()
        self.assertTrue(result["valid"])
        self.assertTrue(result["service_identity_verified"])
        self.assertTrue(result["network_default_deny_declared"])
        self.assertTrue(result["destructive_gap_plan_ready_but_unexecuted"])
        self.assertFalse(result["p1_checkout_present"])
        self.assertFalse(result["listener_present"])
        self.assertFalse(result["operational_ready"])
        self.assertFalse(result["activation_permitted"])

    def test_contract_and_schema_are_draft7_valid(self) -> None:
        schema = module.load_object(module.SCHEMA)
        Draft7Validator.check_schema(schema)
        Draft7Validator(schema).validate(self.contract)

    def test_wrong_platform_or_permissive_selinux_fails(self) -> None:
        (self.root / "etc/os-release").write_text('ID="ubuntu"\nVERSION_ID="24.04"\n', encoding="utf-8")
        with self.assertRaisesRegex(module.DeploymentError, "Amazon Linux 2023"):
            self.verify()
        (self.root / "etc/os-release").write_text('ID="amzn"\nVERSION_ID="2023"\n', encoding="utf-8")
        self.inspector.responses[("getenforce",)] = subprocess.CompletedProcess([], 0, "Permissive\n", "")
        with self.assertRaisesRegex(module.DeploymentError, "SELinux"):
            self.verify()

    def test_login_root_or_regular_uid_identity_fails(self) -> None:
        for uid, shell in ((0, "/sbin/nologin"), (1000, "/sbin/nologin"), (988, "/bin/bash")):
            (self.root / "etc/passwd").write_text(
                f"c5k4-harness:x:{uid}:988:harness:/var/lib/c5k4-harness:{shell}\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(module.DeploymentError, "nonlogin system identity"):
                self.verify()

    def test_identity_group_ambiguity_or_mismatch_fails(self) -> None:
        (self.root / "etc/group").write_text("c5k4-harness:x:987:\n", encoding="utf-8")
        with self.assertRaisesRegex(module.DeploymentError, "group mismatch"):
            self.verify()
        (self.root / "etc/group").write_text("c5k4-harness:x:988:\nc5k4-harness:x:988:\n", encoding="utf-8")
        with self.assertRaisesRegex(module.DeploymentError, "absent or ambiguous"):
            self.verify()

    def test_private_path_mode_and_ownership_relaxations_fail(self) -> None:
        path = self.root / "var/lib/c5k4-harness"
        path.chmod(0o750)
        with self.assertRaisesRegex(module.DeploymentError, "mode"):
            self.verify()
        path.chmod(0o700)
        self.inspector.ownership["/var/lib/c5k4-harness"] = (0, 0)
        with self.assertRaisesRegex(module.DeploymentError, "ownership"):
            self.verify()

    def test_p1_parent_must_remain_root_owned_and_nonwritable(self) -> None:
        path = self.root / "opt/c5k4"
        path.chmod(0o775)
        with self.assertRaisesRegex(module.DeploymentError, "mode"):
            self.verify()
        path.chmod(0o755)
        self.inspector.ownership["/opt/c5k4"] = (988, 988)
        with self.assertRaisesRegex(module.DeploymentError, "root-owned"):
            self.verify()

    def test_installed_asset_mode_ownership_or_bytes_tampering_fails(self) -> None:
        path = self.root / "etc/systemd/system/c5k4-harness.service"
        path.chmod(0o644)
        with self.assertRaisesRegex(module.DeploymentError, "mode"):
            self.verify()
        path.chmod(0o444)
        self.inspector.ownership["/etc/systemd/system/c5k4-harness.service"] = (988, 988)
        with self.assertRaisesRegex(module.DeploymentError, "root-owned"):
            self.verify()
        self.inspector.ownership["/etc/systemd/system/c5k4-harness.service"] = (0, 0)
        path.chmod(0o644); path.write_text("tampered\n", encoding="utf-8"); path.chmod(0o444)
        with self.assertRaisesRegex(module.DeploymentError, "differs"):
            self.verify()

    def test_symlinked_installed_asset_fails(self) -> None:
        path = self.root / "etc/c5k4-harness/network-policy.json"
        path.unlink()
        path.symlink_to(ROOT / self.contract["assets"]["network_policy"])
        with self.assertRaises(module.DeploymentError):
            self.verify()

    def test_premature_checkout_activation_or_socket_fails(self) -> None:
        cases = (
            ("/opt/c5k4/p1", "P1 checkout"),
            ("/etc/c5k4-harness/ACTIVATED", "activation marker"),
            ("/run/c5k4-harness/harness.sock", "listener socket"),
        )
        for absolute, message in cases:
            target = module.rooted(self.root, absolute)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.mkdir() if absolute.endswith("/p1") else target.touch()
            with self.assertRaisesRegex(module.DeploymentError, message):
                self.verify()
            target.rmdir() if target.is_dir() else target.unlink()

    def test_active_or_enabled_service_fails(self) -> None:
        self.inspector.responses[("systemctl", "is-active", "c5k4-harness.service")] = subprocess.CompletedProcess([], 0, "active\n", "")
        with self.assertRaisesRegex(module.DeploymentError, "active"):
            self.verify()
        self.inspector.responses[("systemctl", "is-active", "c5k4-harness.service")] = subprocess.CompletedProcess([], 3, "inactive\n", "")
        self.inspector.responses[("systemctl", "is-enabled", "c5k4-harness.service")] = subprocess.CompletedProcess([], 0, "enabled\n", "")
        with self.assertRaisesRegex(module.DeploymentError, "enabled"):
            self.verify()

    def test_listener_or_unprovable_listener_absence_fails(self) -> None:
        self.inspector.responses[("ss", "-H", "-lntup")] = subprocess.CompletedProcess([], 0, 'users:(("c5k4-harness",pid=8,fd=3))\n', "")
        with self.assertRaisesRegex(module.DeploymentError, "listener exists"):
            self.verify()
        self.inspector.responses[("ss", "-H", "-lntup")] = subprocess.CompletedProcess([], 127, "", "missing")
        with self.assertRaisesRegex(module.DeploymentError, "cannot prove"):
            self.verify()

    def test_activation_claim_or_gap_acceptance_cannot_enter_contract(self) -> None:
        for key in ("operational_ready", "activation_permitted"):
            mutated = copy.deepcopy(self.contract)
            mutated[key] = True
            with self.assertRaisesRegex(module.DeploymentError, "schema failure"):
                module.verify(mutated, self.inspector)

    def test_assets_are_target_blind_and_gap_plan_is_unexecuted(self) -> None:
        serialized = json.dumps(self.contract, sort_keys=True)
        for forbidden in ("target_id", "cluster_id", "conjecture", "statement_text"):
            self.assertNotIn(forbidden, serialized)
        gap = module.load_object(ROOT / self.contract["assets"]["destructive_gap_plan"])
        self.assertFalse(gap["executed"])
        self.assertFalse(gap["passed"])
        self.assertFalse(gap["activation_permitted"])

    def test_cli_on_nondedicated_current_host_fails_closed_and_silent(self) -> None:
        completed = subprocess.run([sys.executable, str(MODULE_PATH)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
