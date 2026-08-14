#!/usr/bin/env python3
"""Target-free Linux isolation acceptance for Method v1.5.

This is deliberately not a benchmark launcher.  It accepts only an already
sealed PRE-P1 isolation plan and runs a fixed, non-semantic fixture.  Source
roots are opened with ``openat2(RESOLVE_BENEATH|NO_SYMLINKS|NO_XDEV)`` and
mounted from descriptor-pinned, detached ``open_tree`` clones.  No source path
is resolved again between validation and attachment.

The module is Linux/x86-64 specific for now.  Unsupported syscalls, namespace
policy, or mount permissions produce a negative readiness result; there is no
fallback to path-based bind mounts.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "scripts" / "method_v15_triplet_isolation_backend.py"
NS_NAMES = ("user", "mnt", "net", "pid", "ipc", "uts")
SECRET_NAMES = {
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "GITHUB_TOKEN", "GH_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY", "SSH_AUTH_SOCK", "DOCKER_HOST",
}

# x86-64 Linux syscall ABI.  We explicitly reject other architectures.
SYS_OPEN_TREE = 428
SYS_MOVE_MOUNT = 429
SYS_OPENAT2 = 437
SYS_MOUNT_SETATTR = 442
AT_EMPTY_PATH = 0x1000
AT_RECURSIVE = 0x8000
OPEN_TREE_CLONE = 1
MOVE_MOUNT_F_EMPTY_PATH = 0x4
RESOLVE_NO_XDEV = 0x01
RESOLVE_NO_MAGICLINKS = 0x02
RESOLVE_NO_SYMLINKS = 0x04
RESOLVE_BENEATH = 0x08
MOUNT_ATTR_RDONLY = 0x1
MOUNT_ATTR_NOSUID = 0x2
MOUNT_ATTR_NODEV = 0x4
MS_NOSUID = 0x2
MS_NODEV = 0x4
MS_NOEXEC = 0x8

libc = ctypes.CDLL(None, use_errno=True)


class IsolationAcceptanceError(RuntimeError):
    """The host or fixture failed closed."""


class OpenHow(ctypes.Structure):
    _fields_ = [("flags", ctypes.c_uint64), ("mode", ctypes.c_uint64), ("resolve", ctypes.c_uint64)]


class MountAttr(ctypes.Structure):
    _fields_ = [
        ("attr_set", ctypes.c_uint64), ("attr_clr", ctypes.c_uint64),
        ("propagation", ctypes.c_uint64), ("userns_fd", ctypes.c_uint64),
    ]


def _syscall(number: int, *args: object) -> int:
    result = int(libc.syscall(number, *args))
    if result < 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))
    return result


def _c(value: str) -> ctypes.c_char_p:
    return ctypes.c_char_p(os.fsencode(value))


def openat2_beneath(directory_fd: int, name: str, flags: int, *, permit_mount_boundary: bool = False) -> int:
    """Open one relative component without links, magic links, or mount hops."""

    if not name or name in {".", ".."} or "/" in name or "\x00" in name:
        raise IsolationAcceptanceError("openat2 component is not a single safe name")
    how = OpenHow(
        flags=flags | os.O_CLOEXEC | os.O_NOFOLLOW,
        mode=0,
        resolve=(RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS |
                 (0 if permit_mount_boundary else RESOLVE_NO_XDEV)),
    )
    return _syscall(SYS_OPENAT2, directory_fd, _c(name), ctypes.byref(how), ctypes.sizeof(how))


def open_absolute_pinned(path: Path) -> int:
    """Resolve an absolute source entirely through descriptor-relative openat2."""

    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise IsolationAcceptanceError("source path must be normalized and absolute")
    fd = os.open("/", os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        parts = path.parts[1:]
        if not parts:
            raise IsolationAcceptanceError("host root may not be an allowed source")
        for index, part in enumerate(parts):
            # The project may itself live on a dedicated mount.  Crossing a
            # mount boundary while walking *to* the requested root is safe;
            # the resulting inode is pinned.  Traversal *inside* that root is
            # subsequently RESOLVE_NO_XDEV and rejects nested mount escapes.
            next_fd = openat2_beneath(
                fd, part, os.O_PATH | (os.O_DIRECTORY if index < len(parts) - 1 else 0),
                permit_mount_boundary=True,
            )
            os.close(fd)
            fd = next_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def _read_fd(fd: int) -> bytes:
    reader = os.open(f"/proc/self/fd/{fd}", os.O_RDONLY | os.O_CLOEXEC)
    try:
        chunks: list[bytes] = []
        while True:
            chunk = os.read(reader, 1024 * 1024)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(reader)


def _scan_directory(fd: int, relative: str = ".") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metadata = os.fstat(fd)
    rows.append({"path": relative, "kind": "directory", "mode": stat.S_IMODE(metadata.st_mode)})
    for name in sorted(os.listdir(fd)):
        child = openat2_beneath(fd, name, os.O_PATH)
        try:
            item = os.fstat(child)
            child_relative = name if relative == "." else f"{relative}/{name}"
            if stat.S_ISDIR(item.st_mode):
                rows.extend(_scan_directory(child, child_relative))
            elif stat.S_ISREG(item.st_mode):
                if item.st_nlink != 1:
                    raise IsolationAcceptanceError("allowed source contains a hardlinked regular file")
                raw = _read_fd(child)
                rows.append({
                    "path": child_relative, "kind": "file", "mode": stat.S_IMODE(item.st_mode),
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                })
            elif stat.S_ISLNK(item.st_mode):
                raise IsolationAcceptanceError("allowed source contains a symlink")
            elif stat.S_ISCHR(item.st_mode) or stat.S_ISBLK(item.st_mode):
                raise IsolationAcceptanceError("allowed source contains a device")
            else:
                raise IsolationAcceptanceError("allowed source contains a special filesystem object")
        finally:
            os.close(child)
    return rows


def pinned_digest(fd: int) -> str:
    metadata = os.fstat(fd)
    if stat.S_ISREG(metadata.st_mode):
        if metadata.st_nlink != 1:
            raise IsolationAcceptanceError("allowed source is a hardlinked regular file")
        return hashlib.sha256(_read_fd(fd)).hexdigest()
    if stat.S_ISDIR(metadata.st_mode):
        rows = _scan_directory(fd)
        raw = (json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        return hashlib.sha256(raw).hexdigest()
    if stat.S_ISCHR(metadata.st_mode) or stat.S_ISBLK(metadata.st_mode):
        raise IsolationAcceptanceError("allowed source is a device")
    raise IsolationAcceptanceError("allowed source is not a regular file or directory")


@dataclass
class PinnedSource:
    role: str
    fd: int
    sha256: str

    def close(self) -> None:
        os.close(self.fd)


def pin_plan_sources(plan: Mapping[str, Any]) -> list[PinnedSource]:
    """Pin and re-hash every source.  Paths are never used by the worker."""

    pinned: list[PinnedSource] = []
    identities: set[tuple[int, int]] = set()
    try:
        for row in plan["allowed_roots"]:
            fd = open_absolute_pinned(Path(row["source_path"]))
            item = PinnedSource(str(row["root_role"]), fd, str(row["source_sha256"]))
            digest = pinned_digest(fd)
            if digest != item.sha256:
                item.close()
                raise IsolationAcceptanceError(f"descriptor-pinned digest mismatch for {item.role}")
            metadata = os.fstat(fd)
            identity = (metadata.st_dev, metadata.st_ino)
            if identity in identities:
                item.close()
                raise IsolationAcceptanceError("allowed source descriptors alias one inode")
            identities.add(identity)
            pinned.append(item)
        return pinned
    except BaseException:
        for item in pinned:
            item.close()
        raise


def clone_read_only_mount(source_fd: int, destination_parent_fd: int, destination_name: str) -> None:
    """Attach a descriptor-pinned source and make it recursively read-only.

    ``open_tree(CLONE)`` cannot clone an ordinary non-mount inode on current
    kernels.  A bind whose source and destination are both procfs descriptor
    references has the same race-free property: both names dereference
    already-open inodes and never revisit an attacker-controlled path.  We
    then apply mount_setattr to the descriptor-pinned destination mount.
    """

    destination_fd = openat2_beneath(destination_parent_fd, destination_name, os.O_PATH)
    source_mount_fd = -1
    try:
        # Turn the pinned source inode into a detached mount.  The temporary
        # source is a descriptor reference, not its original path; therefore
        # a post-validation rename/symlink swap cannot affect this operation.
        source_mount_fd = os.open("/tmp", os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
        scratch_name = f".c5k4-source-{os.getpid()}-{source_fd}"
        source_metadata = os.fstat(source_fd)
        scratch = Path("/tmp", scratch_name)
        if stat.S_ISDIR(source_metadata.st_mode):
            scratch.mkdir(mode=0o700)
        else:
            scratch.touch(mode=0o600)
        scratch_fd = openat2_beneath(source_mount_fd, scratch_name, os.O_PATH)
        result = libc.mount(
            _c(f"/proc/self/fd/{source_fd}"), _c(f"/proc/self/fd/{scratch_fd}"),
            None, 4096, None,  # MS_BIND
        )
        if result != 0:
            code = ctypes.get_errno()
            raise OSError(code, os.strerror(code))
        tree_fd = _syscall(SYS_OPEN_TREE, source_mount_fd, _c(scratch_name), OPEN_TREE_CLONE | os.O_CLOEXEC)
        os.close(scratch_fd)
        scratch_fd = -1
        libc.umount2(_c(str(scratch)), 2)  # MNT_DETACH; clone remains detached
        scratch.rmdir() if stat.S_ISDIR(source_metadata.st_mode) else scratch.unlink()
        attributes = MountAttr(MOUNT_ATTR_RDONLY | MOUNT_ATTR_NOSUID | MOUNT_ATTR_NODEV, 0, 0, 0)
        _syscall(
            SYS_MOUNT_SETATTR, tree_fd, _c(""), AT_EMPTY_PATH | AT_RECURSIVE,
            ctypes.byref(attributes), ctypes.sizeof(attributes),
        )
        _syscall(
            SYS_MOVE_MOUNT, tree_fd, _c(""), destination_parent_fd, _c(destination_name),
            MOVE_MOUNT_F_EMPTY_PATH,
        )
        os.close(tree_fd)
    finally:
        if source_mount_fd >= 0:
            os.close(source_mount_fd)
        os.close(destination_fd)


def _mount(source: str, target: str, filesystem: str, flags: int, data: str = "") -> None:
    result = libc.mount(_c(source), _c(target), _c(filesystem), flags, _c(data))
    if result != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), target)


def _namespace_ids() -> dict[str, int]:
    return {name: os.stat(f"/proc/self/ns/{name}").st_ino for name in NS_NAMES}


def _fixed_environment(plan: Mapping[str, Any]) -> None:
    os.environ.clear()
    os.environ.update({str(key): str(value) for key, value in plan["environment"].items()})


def _worker(envelope_fd: int, result_fd: int) -> int:
    """Fixed target-free fixture, entered only under unshare."""

    envelope = json.loads(_read_fd(envelope_fd))
    plan = envelope["plan"]
    rows = plan["allowed_roots"]
    # Pin and re-hash inside the user/mount namespace.  This is the descriptor
    # set actually mounted.  A swap before this point either fails openat2 or
    # must reproduce the sealed bytes; a swap afterwards cannot redirect FDs.
    pinned = pin_plan_sources(plan)
    source_fds = [item.fd for item in pinned]
    _fixed_environment(plan)

    # The private tree parent is mode 0700 and freshly created.  The source
    # side of every input mount is nevertheless descriptor-pinned.
    private = Path(plan["private_paths"]["sandbox_root"]).parent
    os.mkdir(private, 0o700)
    root = private / "root"
    os.mkdir(root, 0o700)
    _mount("tmpfs", str(root), "tmpfs", MS_NODEV | MS_NOSUID, "size=256m,mode=0755")
    for relative in ("inputs", "output", "tmp", "home", "home/agent", "cache", "proc"):
        (root / relative).mkdir(exist_ok=True)
    inputs_fd = os.open(root / "inputs", os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for row, source_fd in zip(rows, source_fds):
            name = str(row["root_role"])
            metadata = os.fstat(source_fd)
            destination = root / "inputs" / name
            if stat.S_ISDIR(metadata.st_mode):
                destination.mkdir()
            else:
                destination.touch(mode=0o400)
            clone_read_only_mount(source_fd, inputs_fd, name)
    finally:
        os.close(inputs_fd)
    for relative in ("output", "tmp", "home/agent", "cache"):
        _mount("tmpfs", str(root / relative), "tmpfs", MS_NODEV | MS_NOSUID, "size=16m,mode=0700")
    _mount("proc", str(root / "proc"), "proc", MS_NODEV | MS_NOSUID | MS_NOEXEC)

    os.chroot(root)
    os.chdir("/")
    checks: dict[str, bool] = {}
    current_namespaces = _namespace_ids()
    for name in NS_NAMES:
        checks[f"namespace_{name}"] = current_namespaces[name] != envelope["parent_namespaces"][name]
    checks["pid_one"] = os.getpid() == 1
    checks["single_cpu"] = len(os.sched_getaffinity(0)) == 1 and next(iter(os.sched_getaffinity(0))) == plan["cpu_affinity"]
    checks["fixed_secret_free_environment"] = (
        os.environ == plan["environment"] and not (set(os.environ) & SECRET_NAMES)
    )
    checks["host_root_absent"] = not Path("/etc/passwd").exists() and not Path("/Users").exists()
    checks["forbidden_roots_absent"] = all(
        not Path("/inputs", role).exists() for role in plan["forbidden_root_roles"]
    )
    checks["private_paths_distinct"] = len({
        os.stat(path).st_dev for path in ("/output", "/tmp", "/home/agent", "/cache")
    }) == 4

    readonly = True
    for row in rows:
        destination = Path("/inputs", row["root_role"])
        try:
            if destination.is_dir():
                (destination / ".write-probe").write_text("forbidden", encoding="utf-8")
            else:
                with destination.open("ab") as stream:
                    stream.write(b"forbidden")
            readonly = False
        except OSError as exc:
            readonly = readonly and exc.errno in {errno.EROFS, errno.EACCES, errno.EPERM}
    checks["allowed_roots_read_only"] = readonly
    mount_points = []
    for line in Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines():
        fields = line.split()
        mount_points.append(fields[4])
    expected_inputs = {f"/inputs/{row['root_role']}" for row in rows}
    checks["allowed_mount_set_exact"] = expected_inputs <= set(mount_points) and not any(
        point.startswith("/inputs/") and point not in expected_inputs for point in mount_points
    )

    network_denied = False
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.2)
    try:
        probe.connect(("1.1.1.1", 53))
    except OSError:
        network_denied = True
    finally:
        probe.close()
    checks["network_denied"] = network_denied

    raw = (json.dumps({"checks": checks}, sort_keys=True, separators=(",", ":")) + "\n").encode()
    os.write(result_fd, raw)
    for item in pinned:
        item.close()
    return 0 if all(checks.values()) else 3


def _memfd(raw: bytes, name: str) -> int:
    fd = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    os.write(fd, raw)
    os.lseek(fd, 0, os.SEEK_SET)
    return fd


def kernel_acceptance(plan: dict[str, Any]) -> dict[str, Any]:
    """Run the fixed fixture.  Always reports activation as forbidden."""

    if os.uname().machine != "x86_64" or sys.platform != "linux":
        return _negative("UNSUPPORTED_LINUX_SYSCALL_ABI")
    if plan.get("status") != "PRE_P1_TEST_ONLY_NOT_OPERATIONAL" or plan.get("wall_cap_seconds") != 60:
        return _negative("PLAN_IS_NOT_THE_SEALED_PRE_P1_60_SECOND_CONTRACT")
    pinned: list[PinnedSource] = []
    envelope_fd = -1
    read_fd = write_fd = -1
    process: subprocess.Popen[bytes] | None = None
    try:
        pinned = pin_plan_sources(plan)  # preliminary host-side fail-fast audit
        envelope = {"plan": plan, "parent_namespaces": _namespace_ids()}
        envelope_fd = _memfd((json.dumps(envelope, sort_keys=True) + "\n").encode(), "c5k4-isolation-envelope")
        read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
        cpu = int(plan["cpu_affinity"])
        if cpu not in os.sched_getaffinity(0):
            return _negative("REQUESTED_CPU_IS_OUTSIDE_HOST_AFFINITY")
        command = [
            "/usr/bin/taskset", "--cpu-list", str(cpu),
            "/usr/bin/unshare", "--user", "--map-root-user", "--mount", "--net",
            "--pid", "--ipc", "--uts", "--fork", "--kill-child=KILL",
            sys.executable, str(Path(__file__).resolve()), "--worker",
            str(envelope_fd), str(write_fd),
        ]
        pass_fds = (envelope_fd, write_fd)
        process = subprocess.Popen(
            command, pass_fds=pass_fds, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
            start_new_session=True,
        )
        os.close(write_fd)
        write_fd = -1
        try:
            process.wait(timeout=60.0)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            return _negative("FIXTURE_EXCEEDED_60_SECOND_WHOLE_TREE_CAP")
        raw = b""
        while True:
            chunk = os.read(read_fd, 65536)
            if not chunk:
                break
            raw += chunk
        if process.returncode != 0:
            debug = process.stderr.read().decode(errors="replace") if process.stderr else ""
            if process.stderr:
                process.stderr.close()
            return _negative(f"ISOLATION_FIXTURE_EXIT_{process.returncode}:{debug}")
        if process.stderr:
            process.stderr.close()
        observation = json.loads(raw)
        checks = observation.get("checks", {})
        checks["whole_process_tree_kill_path"] = whole_tree_kill_probe(cpu)
        accepted = bool(checks) and all(value is True for value in checks.values())
        return {
            "status": "PRE_P1_TARGET_FREE_KERNEL_ACCEPTANCE_NOT_OPERATIONAL",
            "kernel_acceptance_passed": accepted,
            "activation_permitted": False,
            "target_specific_fields_present": False,
            "checks": checks,
            "remaining_blocks": ["NOT_WIRED_TO_TRIPLET_LAUNCHER", "NO_P1_ACTIVATION"],
        }
    except (OSError, ValueError, KeyError, TypeError, IsolationAcceptanceError) as exc:
        return _negative(f"FAIL_CLOSED:{type(exc).__name__}:{exc}")
    finally:
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        for fd in (read_fd, write_fd, envelope_fd):
            if fd >= 0:
                try:
                    os.close(fd)
                except OSError:
                    pass
        for item in pinned:
            item.close()


def _negative(reason: str) -> dict[str, Any]:
    return {
        "status": "PRE_P1_TARGET_FREE_KERNEL_ACCEPTANCE_NOT_OPERATIONAL",
        "kernel_acceptance_passed": False,
        "activation_permitted": False,
        "target_specific_fields_present": False,
        "checks": {},
        "remaining_blocks": [reason, "NOT_WIRED_TO_TRIPLET_LAUNCHER", "NO_P1_ACTIVATION"],
    }


def _descendants(pid: int) -> set[int]:
    """Return a best-effort snapshot of Linux descendants via procfs."""

    found: set[int] = set()
    pending = [pid]
    while pending:
        parent = pending.pop()
        path = Path(f"/proc/{parent}/task/{parent}/children")
        try:
            children = [int(value) for value in path.read_text(encoding="ascii").split()]
        except (OSError, ValueError):
            continue
        for child in children:
            if child not in found:
                found.add(child)
                pending.append(child)
    return found


def whole_tree_kill_probe(cpu: int) -> bool:
    """Exercise the same process-group kill path without waiting sixty seconds.

    The production timeout remains exactly 60 seconds.  This accelerated probe
    exists solely to prove that a PID-namespace init and its stubborn child do
    not survive termination of the supervising process group.
    """

    command = [
        "/usr/bin/taskset", "--cpu-list", str(cpu),
        "/usr/bin/unshare", "--user", "--map-root-user", "--mount", "--net",
        "--pid", "--ipc", "--uts", "--fork", "--kill-child=KILL",
        sys.executable, str(Path(__file__).resolve()), "--hang-worker",
    ]
    try:
        process = subprocess.Popen(
            command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
            start_new_session=True,
        )
        observed: set[int] = set()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if process.poll() is not None:
                return False
            observed |= _descendants(process.pid)
            if len(observed) >= 2:
                break
            time.sleep(0.02)
        if len(observed) < 2:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=2)
            return False
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=2)
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and any(Path(f"/proc/{pid}").exists() for pid in observed):
            time.sleep(0.02)
        return not any(Path(f"/proc/{pid}").exists() for pid in observed)
    except (OSError, subprocess.SubprocessError):
        try:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=2)
        except (NameError, OSError, subprocess.SubprocessError):
            pass
        return False


def _main(argv: list[str]) -> int:
    if len(argv) >= 4 and argv[1] == "--worker":
        return _worker(int(argv[2]), int(argv[3]))
    if len(argv) == 2 and argv[1] == "--hang-worker":
        child = os.fork()
        if child == 0:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            while True:
                signal.pause()
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        while True:
            signal.pause()
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
