#!/usr/bin/env python3
"""Non-activated Linux isolation contract for Method v1.5 triplet trees.

This module validates and seals plans, exercises them only through an injected
acceptance executor, and performs target-free host probes.  It deliberately has
no target execution entry point.  In particular, the future production backend
still needs descriptor-pinned ``open_tree``/``move_mount`` source handling to
close the validation-to-bind-mount race before P1 activation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from typing import Any, Callable, Mapping, Sequence

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ZERO_SHA256 = "0" * 64
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
TOOLS = ("unshare", "mount", "umount", "chroot", "taskset")
SECRET_NAMES = frozenset({
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "GITHUB_TOKEN", "GH_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY", "SSH_AUTH_SOCK", "DOCKER_HOST",
})
FIXED_ENV_KEYS = frozenset({
    "PATH", "HOME", "TMPDIR", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "LANG",
    "LC_ALL", "TZ", "PYTHONHASHSEED", "PYTHONNOUSERSITE", "PYTHONDONTWRITEBYTECODE",
    "C5K4_BENCHMARK_VERSION", "C5K4_ARM", "C5K4_TREE_ID", "C5K4_NETWORK_POLICY",
    "C5K4_OUTPUT_DIR",
})
ALL_CHECKS = (
    "user_namespace", "mount_namespace", "network_namespace", "pid_namespace",
    "ipc_namespace", "uts_namespace", "host_root_absent", "allowed_roots_read_only_exact",
    "forbidden_roots_absent", "private_paths_disjoint", "single_cpu_affinity",
    "process_tree_killed_at_wall_cap", "fixed_environment_only", "secrets_absent",
    "symlink_escape_blocked", "hardlink_escape_blocked", "device_escape_blocked",
)


class IsolationError(ValueError):
    """A plan, filesystem root, or acceptance observation fails closed."""


class SilentArgumentParser(argparse.ArgumentParser):
    """Keep malformed diagnostic invocations out of public CI streams."""

    def error(self, message: str) -> None:
        raise IsolationError(f"argument contract rejected: {message}")


@dataclass(frozen=True)
class RootSpec:
    role: str
    source: Path
    sha256: str


@dataclass(frozen=True)
class IsolationRequest:
    tree_id: str
    arm: str
    argv: tuple[str, ...]
    cpu: int
    allowed_roots: tuple[RootSpec, ...]
    forbidden_roots: tuple[tuple[str, Path], ...]
    private_base: Path


@dataclass(frozen=True)
class AcceptanceObservation:
    checks: Mapping[str, bool]


InjectedExecutor = Callable[[dict[str, Any]], AcceptanceObservation]
CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def object_digest(value: dict[str, Any], digest_key: str) -> str:
    unsigned = {key: item for key, item in value.items() if key != digest_key}
    return hashlib.sha256(canonical_bytes(unsigned)).hexdigest()


def _schema(name: str) -> dict[str, Any]:
    try:
        value = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IsolationError(f"cannot load schema {name}: {exc}") from exc
    if not isinstance(value, dict):
        raise IsolationError(f"schema {name} is not an object")
    return value


def validate_schema(value: object, name: str, label: str) -> None:
    validator = jsonschema.Draft7Validator(_schema(name))
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(item) for item in error.absolute_path) or "$"
        raise IsolationError(f"{label} schema failure at {location}: {error.message}")


def _contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _canonical_absolute(path: Path, label: str, *, must_exist: bool) -> Path:
    if not path.is_absolute():
        raise IsolationError(f"{label} must be absolute")
    if any(part in {".", ".."} for part in path.parts):
        raise IsolationError(f"{label} must be lexically normalized")
    if must_exist:
        try:
            resolved = path.resolve(strict=True)
        except OSError as exc:
            raise IsolationError(f"{label} does not resolve: {exc}") from exc
        if resolved != path:
            raise IsolationError(f"{label} contains a symlink or non-canonical component")
        return resolved
    # A private destination may not exist, but every existing ancestor must be
    # canonical and non-symlinked.
    cursor = path
    suffix: list[str] = []
    while not cursor.exists():
        if cursor.parent == cursor:
            raise IsolationError(f"{label} has no existing ancestor")
        suffix.append(cursor.name)
        cursor = cursor.parent
    resolved_parent = cursor.resolve(strict=True)
    if resolved_parent != cursor:
        raise IsolationError(f"{label} has a symlinked ancestor")
    rebuilt = resolved_parent.joinpath(*reversed(suffix))
    if rebuilt != path:
        raise IsolationError(f"{label} is not canonical")
    return path


def _walk_root(path: Path) -> list[Path]:
    rows = [path]
    if path.is_dir():
        for directory, directories, files in os.walk(path, followlinks=False):
            base = Path(directory)
            rows.extend(base / name for name in directories)
            rows.extend(base / name for name in files)
    return rows


def validate_source_root(path: Path, label: str) -> Path:
    root = _canonical_absolute(path, label, must_exist=True)
    for child in _walk_root(root):
        try:
            metadata = child.lstat()
        except OSError as exc:
            raise IsolationError(f"{label} cannot be inspected atomically enough: {exc}") from exc
        mode = metadata.st_mode
        if stat.S_ISLNK(mode):
            raise IsolationError(f"{label} contains a symlink escape: {child}")
        if stat.S_ISREG(mode):
            if metadata.st_nlink != 1:
                raise IsolationError(f"{label} contains a hardlinked regular file: {child}")
        elif stat.S_ISDIR(mode):
            continue
        elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
            raise IsolationError(f"{label} contains a device node: {child}")
        elif stat.S_ISFIFO(mode):
            raise IsolationError(f"{label} contains a FIFO: {child}")
        elif stat.S_ISSOCK(mode):
            raise IsolationError(f"{label} contains a socket: {child}")
        else:
            raise IsolationError(f"{label} contains an unsupported filesystem object: {child}")
    return root


def content_sha256(path: Path) -> str:
    """Hash file bytes or a canonical tree manifest without following links."""

    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    rows: list[dict[str, Any]] = []
    for child in sorted(_walk_root(path), key=lambda item: item.relative_to(path).as_posix()):
        relative = child.relative_to(path).as_posix() or "."
        metadata = child.lstat()
        if stat.S_ISDIR(metadata.st_mode):
            rows.append({"path": relative, "kind": "directory", "mode": stat.S_IMODE(metadata.st_mode)})
        elif stat.S_ISREG(metadata.st_mode):
            rows.append({
                "path": relative,
                "kind": "file",
                "mode": stat.S_IMODE(metadata.st_mode),
                "bytes": metadata.st_size,
                "sha256": hashlib.sha256(child.read_bytes()).hexdigest(),
            })
        else:  # validate_source_root should make this unreachable
            raise IsolationError(f"unsupported object entered digest tree: {child}")
    return hashlib.sha256(canonical_bytes(rows)).hexdigest()


def _validate_request(request: IsolationRequest) -> tuple[list[RootSpec], dict[str, Path]]:
    if request.arm not in ARMS or request.tree_id.split("-", 1)[0] != request.arm:
        raise IsolationError("tree id and arm disagree")
    if not (0 <= request.cpu < 1_000_000):
        raise IsolationError("CPU affinity must name exactly one nonnegative CPU")
    if not request.argv or any(
        not isinstance(arg, str) or not arg or any(mark in arg for mark in ("\x00", "\n", "\r"))
        for arg in request.argv
    ):
        raise IsolationError("argv is empty or contains an unsafe value")
    if len({root.role for root in request.allowed_roots}) != len(request.allowed_roots):
        raise IsolationError("allowed root roles are not unique")
    forbidden = dict(request.forbidden_roots)
    if len(forbidden) != len(request.forbidden_roots):
        raise IsolationError("forbidden root roles are not unique")
    if set(forbidden) & {root.role for root in request.allowed_roots}:
        raise IsolationError("a root role is both allowed and forbidden")
    allowed: list[RootSpec] = []
    for root in request.allowed_roots:
        source = validate_source_root(root.source, f"allowed root {root.role}")
        if content_sha256(source) != root.sha256:
            raise IsolationError(f"allowed root {root.role} digest mismatch")
        allowed.append(RootSpec(root.role, source, root.sha256))
    sources = [root.source for root in allowed]
    if len(sources) != len(set(sources)):
        raise IsolationError("two allowed root roles alias one source")
    for index, left in enumerate(sources):
        for right in sources[index + 1:]:
            if _contains(left, right) or _contains(right, left):
                raise IsolationError("allowed source roots overlap")
    forbidden_paths: dict[str, Path] = {}
    for role, path in forbidden.items():
        candidate = _canonical_absolute(path, f"forbidden root {role}", must_exist=False)
        forbidden_paths[role] = candidate
        for source in sources:
            if _contains(source, candidate) or _contains(candidate, source):
                raise IsolationError("allowed and forbidden source roots overlap")
    _canonical_absolute(request.private_base, "private base", must_exist=False)
    for source in sources:
        if _contains(source, request.private_base) or _contains(request.private_base, source):
            raise IsolationError("private destination overlaps an allowed source")
    return allowed, forbidden_paths


def build_plan(request: IsolationRequest) -> dict[str, Any]:
    allowed, forbidden = _validate_request(request)
    sandbox = request.private_base / request.tree_id
    private = {
        "sandbox_root": str(sandbox / "root"),
        "output": str(sandbox / "private" / "output"),
        "tmp": str(sandbox / "private" / "tmp"),
        "home": str(sandbox / "private" / "home"),
        "cache": str(sandbox / "private" / "cache"),
    }
    if len(private.values()) != len(set(private.values())):
        raise IsolationError("private paths are not disjoint")
    environment = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/home/agent",
        "TMPDIR": "/tmp",
        "XDG_CACHE_HOME": "/cache",
        "XDG_CONFIG_HOME": "/home/agent/.config",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "C5K4_BENCHMARK_VERSION": "1.5",
        "C5K4_ARM": request.arm,
        "C5K4_TREE_ID": request.tree_id,
        "C5K4_NETWORK_POLICY": "DENY",
        "C5K4_OUTPUT_DIR": "/output",
    }
    if set(environment) != FIXED_ENV_KEYS or set(environment) & SECRET_NAMES:
        raise IsolationError("fixed environment closure is invalid")
    plan = {
        "schema": "c5k4-method-v1.5-triplet-isolation-plan-1.0",
        "artifact_kind": "PRIVATE_TREE_ISOLATION_PLAN",
        "protocol_version": "1.5",
        "status": "PRE_P1_TEST_ONLY_NOT_OPERATIONAL",
        "tree_id": request.tree_id,
        "arm": request.arm,
        "argv": list(request.argv),
        "cpu_affinity": request.cpu,
        "wall_cap_seconds": 60,
        "namespaces": {
            "user": True, "mount": True, "network": True, "pid": True,
            "ipc": True, "uts": True, "map_root_user": True, "kill_child": "KILL",
        },
        "network": {
            "policy": "DENY", "new_namespace": True,
            "interfaces_brought_up": [], "dns_files_mounted": [],
        },
        "root_filesystem": {
            "kind": "PRIVATE_TMPFS_CHROOT", "host_root_visible": False,
            "runtime_roots": ["/usr", "/bin", "/lib", "/lib64"],
            "proc_policy": "PRIVATE_PID_NAMESPACE_PROCFS",
        },
        "allowed_roots": [
            {
                "root_role": root.role,
                "source_path": str(root.source),
                "source_sha256": root.sha256,
                "sandbox_path": f"/inputs/{root.role}",
                "mount": "BIND_REMOUNT_READ_ONLY_NODEV_NOSUID",
                "writable": False,
            }
            for root in allowed
        ],
        "forbidden_root_roles": sorted(forbidden),
        "private_paths": private,
        "environment": environment,
        "escape_policy": {
            "symlinks_permitted": False,
            "hardlinked_regular_files_permitted": False,
            "device_nodes_permitted": False,
            "fifos_permitted": False,
            "sockets_permitted": False,
            "source_destination_overlap_permitted": False,
            "allowed_forbidden_overlap_permitted": False,
        },
        "implementation": {
            "backend": "LINUX_UNSHARE_PRIVATE_ROOT_CONTRACT",
            "target_launch_wired": False,
            "fd_pinned_mounts": False,
            "production_claim_permitted": False,
        },
        "plan_sha256": ZERO_SHA256,
    }
    plan["plan_sha256"] = object_digest(plan, "plan_sha256")
    validate_plan(plan)
    return plan


def validate_plan(plan: dict[str, Any]) -> None:
    validate_schema(plan, "benchmark-triplet-isolation-plan-v1.5.schema.json", "isolation plan")
    if plan["plan_sha256"] != object_digest(plan, "plan_sha256"):
        raise IsolationError("isolation plan self-digest mismatch")
    if set(plan["environment"]) != FIXED_ENV_KEYS or set(plan["environment"]) & SECRET_NAMES:
        raise IsolationError("isolation plan environment is not the exact secret-free closure")
    roles = [root["root_role"] for root in plan["allowed_roots"]]
    paths = [root["source_path"] for root in plan["allowed_roots"]]
    destinations = [root["sandbox_path"] for root in plan["allowed_roots"]]
    if len(roles) != len(set(roles)) or len(paths) != len(set(paths)) or len(destinations) != len(set(destinations)):
        raise IsolationError("isolation plan root closure aliases a role or path")
    if set(roles) & set(plan["forbidden_root_roles"]):
        raise IsolationError("isolation plan exposes a forbidden root")
    private = [Path(value) for value in plan["private_paths"].values()]
    if len(private) != len(set(private)):
        raise IsolationError("isolation plan private paths are not disjoint")
    working = [Path(plan["private_paths"][name]) for name in ("output", "tmp", "home", "cache")]
    for index, left in enumerate(working):
        for right in working[index + 1:]:
            if _contains(left, right) or _contains(right, left):
                raise IsolationError("isolation plan private working paths overlap")
    sources = [Path(root["source_path"]) for root in plan["allowed_roots"]]
    for source in sources:
        for destination in private:
            if _contains(source, destination) or _contains(destination, source):
                raise IsolationError("isolation plan source and private paths overlap")


def exercise_with_injected_executor(plan: dict[str, Any], executor: InjectedExecutor) -> dict[str, Any]:
    """Evaluate enforcement metadata only; never interpret target output."""

    validate_plan(plan)
    observation = executor(json.loads(json.dumps(plan)))
    if not isinstance(observation, AcceptanceObservation):
        raise IsolationError("injected executor returned the wrong observation type")
    if set(observation.checks) != set(ALL_CHECKS) or any(
        not isinstance(value, bool) for value in observation.checks.values()
    ):
        raise IsolationError("injected executor did not attest the exact acceptance closure")
    record = {
        "schema": "c5k4-method-v1.5-triplet-isolation-acceptance-1.0",
        "artifact_kind": "INJECTED_ISOLATION_ACCEPTANCE_RECORD",
        "protocol_version": "1.5",
        "status": "PRE_P1_FAKE_EXECUTOR_ACCEPTANCE_ONLY_NOT_OPERATIONAL",
        "plan_sha256": plan["plan_sha256"],
        "accepted": all(observation.checks.values()),
        "checks": dict(observation.checks),
        "acceptance_sha256": ZERO_SHA256,
    }
    record["acceptance_sha256"] = object_digest(record, "acceptance_sha256")
    validate_schema(
        record, "benchmark-triplet-isolation-acceptance-v1.5.schema.json", "acceptance record"
    )
    return record


def _run_probe(argv: Sequence[str], runner: CommandRunner) -> bool:
    try:
        result = runner(
            list(argv), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=10, env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def readiness(
    *,
    resolver: Callable[[str], str | None] = shutil.which,
    runner: CommandRunner = subprocess.run,
) -> dict[str, Any]:
    tools = {name: resolver(name) is not None for name in TOOLS}
    namespace_probe = False
    mount_probe = False
    if all(tools.values()):
        unshare = resolver("unshare") or "unshare"
        shell = resolver("sh") or "/bin/sh"
        common = [
            unshare, "--user", "--map-root-user", "--mount", "--net", "--pid",
            "--ipc", "--uts", "--fork", "--kill-child=KILL",
        ]
        namespace_probe = _run_probe([*common, shell, "-eu", "-c", "test -r /proc/self/ns/user"], runner)
        mount_probe = _run_probe([
            *common, shell, "-eu", "-c",
            "d=$(mktemp -d); mount -t tmpfs -o nosuid,nodev,size=1m none \"$d\"; "
            "touch \"$d/probe\"; umount \"$d\"; rmdir \"$d\"",
        ], runner)
    value = {
        "schema": "c5k4-method-v1.5-triplet-isolation-readiness-1.0",
        "artifact_kind": "TARGET_FREE_ISOLATION_READINESS",
        "protocol_version": "1.5",
        "status": "PRE_P1_ISOLATION_BACKEND_NOT_OPERATIONAL",
        "target_specific_fields_present": False,
        "operational_ready": False,
        "activation_permitted": False,
        "launcher_wired": False,
        "required_tools": tools,
        "kernel_probes": {
            "user_mount_network_pid_namespaces": namespace_probe,
            "private_tmpfs_mount": mount_probe,
        },
        "remaining_blocks": [
            "NOT_WIRED_TO_TRIPLET_LAUNCHER",
            "NO_FD_PINNED_OPEN_TREE_MOVE_MOUNT_IMPLEMENTATION",
            "NO_PRODUCTION_ACCEPTANCE_ATTESTATION",
            "NO_P1_ACTIVATION",
        ],
        "readiness_sha256": ZERO_SHA256,
    }
    value["readiness_sha256"] = object_digest(value, "readiness_sha256")
    validate_schema(
        value, "benchmark-triplet-isolation-readiness-v1.5.schema.json", "isolation readiness"
    )
    return value


def _exclusive_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:  # pragma: no cover - kernel/filesystem failure
                raise OSError("short readiness write")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main(argv: list[str] | None = None) -> int:
    parser = SilentArgumentParser(description=__doc__)
    parser.add_argument("--readiness-output", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        _exclusive_write(args.readiness_output, canonical_bytes(readiness()))
    except (IsolationError, OSError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
