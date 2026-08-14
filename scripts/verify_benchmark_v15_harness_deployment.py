#!/usr/bin/env python3
"""Fail-closed PRE-P1 acceptance for a dedicated AL2023 harness scaffold.

This verifier performs read-only host inspection.  It cannot provision a user,
install a unit, create an activation marker, freeze P1, or authorize service
activation.  The committed contract intentionally accepts only an inert host.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Any, Callable

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "results" / "benchmark" / "v1.5-protocol"
SCHEMA = ROOT / "schemas" / "benchmark-controlled-harness-deployment-contract-v1.5.schema.json"


class DeploymentError(ValueError):
    """The host is not exactly the inert, target-blind deployment scaffold."""


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DeploymentError(f"{path}: expected one JSON object")
    return value


def parse_kv(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"')
    return result


def rooted(root: Path, absolute: str) -> Path:
    if not absolute.startswith("/") or ".." in Path(absolute).parts:
        raise DeploymentError("contract path is not a normalized absolute path")
    return root / absolute.removeprefix("/")


class HostInspector:
    def __init__(
        self,
        root: Path = Path("/"),
        runner: Callable[[list[str]], subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self.root = root.resolve()
        self._runner = runner or self._run

    @staticmethod
    def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(argv, text=True, capture_output=True, check=False, timeout=5)

    def path(self, absolute: str) -> Path:
        return rooted(self.root, absolute)

    def exists(self, absolute: str) -> bool:
        return os.path.lexists(self.path(absolute))

    def stat(self, absolute: str) -> os.stat_result:
        return os.lstat(self.path(absolute))

    def read(self, absolute: str) -> str:
        return self.path(absolute).read_text(encoding="utf-8")

    def command(self, argv: list[str]) -> subprocess.CompletedProcess[str]:
        if self.root != Path("/"):
            raise DeploymentError("fixture root requires an injected command runner")
        return self._runner(argv)


def exact_mode(info: os.stat_result, expected: int, label: str) -> None:
    if stat.S_IMODE(info.st_mode) != expected:
        raise DeploymentError(f"{label} mode is not {expected:04o}")
    if stat.S_ISLNK(info.st_mode):
        raise DeploymentError(f"{label} may not be a symlink")


def parse_identity(inspector: HostInspector, name: str) -> tuple[int, int, str, str]:
    passwd_rows = [line.split(":") for line in inspector.read("/etc/passwd").splitlines()]
    rows = [row for row in passwd_rows if len(row) == 7 and row[0] == name]
    if len(rows) != 1:
        raise DeploymentError("dedicated service identity is absent or ambiguous")
    row = rows[0]
    group_rows = [line.split(":") for line in inspector.read("/etc/group").splitlines()]
    groups = [group for group in group_rows if len(group) >= 3 and group[0] == name]
    if len(groups) != 1:
        raise DeploymentError("dedicated service group is absent or ambiguous")
    uid, gid, group_gid = int(row[2]), int(row[3]), int(groups[0][2])
    if gid != group_gid:
        raise DeploymentError("dedicated service primary group mismatch")
    return uid, gid, row[5], row[6]


def verify_repo_assets(contract: dict[str, Any]) -> None:
    for relative in contract["assets"].values():
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise DeploymentError(f"deployment asset missing or symlinked: {relative}")

    unit = (ROOT / contract["assets"]["systemd_unit"]).read_text(encoding="utf-8")
    required = (
        "ConditionPathExists=/etc/c5k4-benchmark-v15/ACTIVATED",
        "RefuseManualStart=yes", "User=c5k4-benchmark-v15", "Group=c5k4-benchmark-v15",
        "ExecStart=/bin/false",
        "ProtectSystem=strict", "ReadOnlyPaths=/opt/c5k4-benchmark-v15/p1 /etc/c5k4-benchmark-v15",
        "ReadWritePaths=/var/lib/c5k4-benchmark-v15 /var/cache/c5k4-benchmark-v15 /run/c5k4-benchmark-v15",
        "IPAddressDeny=any", "NoNewPrivileges=yes", "RestrictNamespaces=no",
    )
    if any(item not in unit for item in required):
        raise DeploymentError("systemd unit does not retain the PRE-P1 hardening closure")
    if "[Install]" in "\n".join(line for line in unit.splitlines() if not line.lstrip().startswith("#")):
        raise DeploymentError("PRE-P1 unit may not be enableable")
    if any(token in unit for token in ("ListenStream=", "ListenDatagram=", "EnvironmentFile=-")):
        raise DeploymentError("PRE-P1 unit contains an optional listener or environment ingress")

    network = load_object(ROOT / contract["assets"]["network_policy"])
    if network != {
        "schema": "c5k4-method-v1.5-pre-p1-network-policy-1.0",
        "status": "PRE_P1_DEFAULT_DENY_NO_ENDPOINTS", "default_deny": True,
        "dns_allowed": False, "allowed_endpoints": [], "listener_endpoints": [],
        "activation_permitted": False,
    }:
        raise DeploymentError("PRE-P1 network policy is not exact default-deny/no-endpoint")

    gap = load_object(ROOT / contract["assets"]["destructive_gap_plan"])
    expected_tests = ["DESTRUCTIVE_WRITE", "TRUNCATION", "SERVICE_RESTART", "OFFLINE_GAP", "SEQUENCE_CONFLICT", "UNEXPECTED_INGRESS"]
    if gap.get("tests") != expected_tests or gap.get("executed") or gap.get("passed") or gap.get("activation_permitted"):
        raise DeploymentError("destructive gap plan is incomplete or prematurely accepted")
    if not all(gap.get(key) is True for key in ("requires_fresh_disposable_host", "requires_live_immutable_store", "requires_operational_signing_key")):
        raise DeploymentError("destructive gap plan omits an operational prerequisite")


def verify_host(contract: dict[str, Any], inspector: HostInspector) -> dict[str, Any]:
    os_release = parse_kv(inspector.read("/etc/os-release"))
    if (os_release.get("ID"), os_release.get("VERSION_ID")) != ("amzn", "2023"):
        raise DeploymentError("host is not Amazon Linux 2023")
    enforce = inspector.command(["getenforce"])
    if enforce.returncode != 0 or enforce.stdout.strip() != "Enforcing":
        raise DeploymentError("SELinux is not enforcing")

    identity = contract["identity"]
    uid, gid, home, shell = parse_identity(inspector, identity["user"])
    if uid == 0 or uid >= 1000 or home != identity["home"] or shell != identity["login_shell"]:
        raise DeploymentError("service identity is not a dedicated nonlogin system identity")

    path_specs = contract["paths"]
    p1_parent = inspector.stat("/opt/c5k4-benchmark-v15")
    if not stat.S_ISDIR(p1_parent.st_mode) or (p1_parent.st_uid, p1_parent.st_gid) != (0, 0):
        raise DeploymentError("P1 checkout parent is not a root-owned directory")
    exact_mode(p1_parent, 0o755, "P1 checkout parent")
    for key, expected_type in (("private_state", stat.S_ISDIR), ("private_cache", stat.S_ISDIR), ("runtime", stat.S_ISDIR), ("configuration", stat.S_ISDIR), ("credential_root", stat.S_ISDIR)):
        spec = path_specs[key]
        info = inspector.stat(spec["path"])
        if not expected_type(info.st_mode):
            raise DeploymentError(f"{key} is not a directory")
        expected_uid = 0 if spec["owner"] == "root" else uid
        expected_gid = 0 if spec["group"] == "root" else gid
        if (info.st_uid, info.st_gid) != (expected_uid, expected_gid):
            raise DeploymentError(f"{key} ownership mismatch")
        exact_mode(info, int(spec["mode"], 8), key)

    installed = {
        "/etc/systemd/system/c5k4-benchmark-v15.service": contract["assets"]["systemd_unit"],
        "/usr/lib/sysusers.d/c5k4-benchmark-v15.conf": contract["assets"]["sysusers"],
        "/usr/lib/tmpfiles.d/c5k4-benchmark-v15.conf": contract["assets"]["tmpfiles"],
        "/etc/c5k4-benchmark-v15/network-policy.json": contract["assets"]["network_policy"],
        "/etc/c5k4-benchmark-v15/destructive-gap-plan.json": contract["assets"]["destructive_gap_plan"],
    }
    for destination, source in installed.items():
        info = inspector.stat(destination)
        if not stat.S_ISREG(info.st_mode) or (info.st_uid, info.st_gid) != (0, 0):
            raise DeploymentError(f"installed asset is not a root-owned regular file: {destination}")
        exact_mode(info, 0o444, destination)
        if inspector.read(destination).encode() != (ROOT / source).read_bytes():
            raise DeploymentError(f"installed asset differs from frozen repository bytes: {destination}")

    if inspector.exists(path_specs["p1_checkout"]["path"]):
        raise DeploymentError("P1 checkout exists before a P1 tree digest is frozen")
    if inspector.exists(path_specs["activation_marker"]):
        raise DeploymentError("activation marker exists in PRE-P1 state")
    if inspector.exists(path_specs["listener_socket"]):
        raise DeploymentError("controlled-harness listener socket exists in PRE-P1 state")

    active = inspector.command(["systemctl", "is-active", "c5k4-benchmark-v15.service"])
    if active.stdout.strip() != "inactive" or active.returncode == 0:
        raise DeploymentError("controlled harness is active before P1")
    enabled = inspector.command(["systemctl", "is-enabled", "c5k4-benchmark-v15.service"])
    if enabled.stdout.strip() not in ("disabled", "static"):
        raise DeploymentError("controlled harness is enabled before P1")
    internet_sockets = inspector.command(["ss", "-H", "-lntup"])
    unix_sockets = inspector.command(["ss", "-H", "-lxnp"])
    if internet_sockets.returncode != 0 or unix_sockets.returncode != 0:
        raise DeploymentError("cannot prove listener absence")
    listeners = internet_sockets.stdout + unix_sockets.stdout
    if "c5k4-benchmark-v15" in listeners or "/run/c5k4-benchmark-v15/control.sock" in listeners:
        raise DeploymentError("controlled-harness listener exists before P1")

    return {
        "valid": True,
        "status": contract["status"],
        "service_identity_verified": True,
        "filesystem_boundary_verified": True,
        "network_default_deny_declared": True,
        "destructive_gap_plan_ready_but_unexecuted": True,
        "p1_checkout_present": False,
        "listener_present": False,
        "operational_ready": False,
        "activation_permitted": False,
    }


def verify(contract: dict[str, Any], inspector: HostInspector) -> dict[str, Any]:
    schema = load_object(SCHEMA)
    errors = sorted(Draft7Validator(schema).iter_errors(contract), key=lambda item: list(item.path))
    if errors:
        raise DeploymentError(f"deployment contract schema failure: {errors[0].message}")
    verify_repo_assets(contract)
    return verify_host(contract, inspector)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=PROTOCOL / "controlled-harness-deployment-contract.json")
    parser.add_argument("--root", type=Path, default=Path("/"))
    args = parser.parse_args(argv)
    try:
        verify(load_object(args.contract), HostInspector(args.root))
    except (DeploymentError, OSError, json.JSONDecodeError, subprocess.SubprocessError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
