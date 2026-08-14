#!/usr/bin/env python3
"""Fail-closed exact-C Docker boundary for candidate-readiness verifiers.

The verifier, its schema, and its evidence object are the only non-runtime
files exposed to the container.  A container is created and its effective
configuration is audited before it is started.  Mutable image tags, implicit
pulls, unauthenticated daemon state, extra mounts, inherited image environment,
and weaker fallback execution are rejected.
"""

from __future__ import annotations

import hashlib
import base64
import json
import os
import re
import stat
import subprocess
import uuid
from pathlib import Path
from typing import Any

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


DOCKER = "/usr/bin/docker"
ROOT = Path(__file__).resolve().parent.parent
CONTRACT_RELATIVE = Path("results/benchmark/v1.5-protocol/candidate-base-isolated-evidence-runner-contract.json")
SCHEMA_RELATIVE = Path("schemas/benchmark-candidate-base-isolated-evidence-runner-v1.5.schema.json")
RUNNER_RELATIVE = Path("scripts/run_benchmark_v15_isolated_evidence.py")
TEST_RELATIVE = Path("scripts/test_run_benchmark_v15_isolated_evidence.py")
CONTRACT_PATH = ROOT / CONTRACT_RELATIVE
SCHEMA_PATH = ROOT / SCHEMA_RELATIVE
EXPECTED_ENV = {
    "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C", "PATH": "/usr/local/bin:/usr/bin:/bin",
    "PYTHONHASHSEED": "0", "PYTHONNOUSERSITE": "1", "TMPDIR": "/tmp", "TZ": "UTC",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
OID = re.compile(r"^[0-9a-f]{40}$")


class IsolatedEvidenceRunnerError(OSError):
    pass


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _domain_digest(domain: str, value: Any) -> str:
    return _sha(domain.encode() + b"\0" + _canonical(value))


def _json(raw: bytes, label: str) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise IsolatedEvidenceRunnerError(f"{label} contains duplicate JSON keys")
            value[key] = item
        return value
    try:
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=no_duplicates, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise IsolatedEvidenceRunnerError(f"{label} is not strict UTF-8 JSON") from exc
    return value


def _run(args: list[str], *, timeout: int = 10) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            args, check=False, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd="/", env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise IsolatedEvidenceRunnerError("isolated evidence Docker boundary failed closed") from exc
    return result


def _checked(args: list[str], label: str, *, timeout: int = 10) -> bytes:
    result = _run(args, timeout=timeout)
    if result.returncode != 0:
        raise IsolatedEvidenceRunnerError(f"{label} failed closed")
    return result.stdout


def _exact_c_component_bytes(candidate: str) -> tuple[bytes, bytes]:
    """Prove the running backend, contract, schema, and test are exact C bytes."""
    if not OID.fullmatch(candidate):
        raise IsolatedEvidenceRunnerError("isolated runner candidate commit is invalid")
    env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "GIT_NO_REPLACE_OBJECTS": "1"}
    local = {
        RUNNER_RELATIVE: Path(__file__).read_bytes(), CONTRACT_RELATIVE: CONTRACT_PATH.read_bytes(),
        SCHEMA_RELATIVE: SCHEMA_PATH.read_bytes(), TEST_RELATIVE: (ROOT / TEST_RELATIVE).read_bytes(),
    }
    exact: dict[Path, bytes] = {}
    for relative in local:
        try:
            result = subprocess.run(
                ["/usr/bin/git", "-C", str(ROOT), "show", f"{candidate}:{relative.as_posix()}"],
                check=False, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd="/", env=env, timeout=10,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise IsolatedEvidenceRunnerError("exact-C runner component lookup failed") from exc
        if result.returncode != 0 or result.stdout != local[relative]:
            raise IsolatedEvidenceRunnerError(f"running isolated-runner component differs from exact C: {relative}")
        exact[relative] = result.stdout
    return exact[SCHEMA_RELATIVE], exact[CONTRACT_RELATIVE]


def _load_contract(schema_raw: bytes | None = None, contract_raw: bytes | None = None) -> dict[str, Any]:
    schema = _json(SCHEMA_PATH.read_bytes() if schema_raw is None else schema_raw, "isolated-runner schema")
    contract = _json(CONTRACT_PATH.read_bytes() if contract_raw is None else contract_raw, "isolated-runner contract")
    try:
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(contract)
    except jsonschema.ValidationError as exc:
        raise IsolatedEvidenceRunnerError("isolated-runner contract does not validate") from exc
    if not contract["operational"]:
        raise IsolatedEvidenceRunnerError("isolated evidence runner is not operationally attested at exact C")
    return contract


def _version(value: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        raise IsolatedEvidenceRunnerError("runtime version is not a semantic version")
    return tuple(int(part) for part in match.groups())


def _live_daemon_projection(contract: dict[str, Any]) -> None:
    version = json.loads(_checked([DOCKER, "version", "--format", "{{json .}}"], "docker version"))
    info = json.loads(_checked([DOCKER, "info", "--format", "{{json .}}"], "docker info"))
    server = version.get("Server") or {}
    if _version(str(server.get("ApiVersion", "0.0.0"))) < _version(contract["backend"]["api_minimum"] + ".0"):
        raise IsolatedEvidenceRunnerError("Docker server API is below the frozen minimum")
    runc_versions = [
        row.get("Version") for row in server.get("Components", [])
        if row.get("Name") == contract["backend"]["runtime"]
    ]
    if len(runc_versions) != 1 or _version(str(runc_versions[0])) < _version(contract["backend"]["runtime_minimum"]):
        raise IsolatedEvidenceRunnerError("Docker runtime differs from the frozen minimum")
    projection = {
        "host_id": contract["daemon"]["host_id"],
        "engine_version": server.get("Version"),
        "engine_id": info.get("ID"),
        "security_options": sorted(info.get("SecurityOptions") or []),
        "cgroup_version": str(info.get("CgroupVersion")),
        "cgroup_driver": info.get("CgroupDriver"),
        "default_runtime": info.get("DefaultRuntime"),
        "user_namespace_mode": "daemon-userns-remap" if "name=userns" in (info.get("SecurityOptions") or []) else "absent",
    }
    expected = {key: contract["daemon"][key] for key in projection}
    if projection != expected:
        raise IsolatedEvidenceRunnerError("live Docker daemon differs from exact-C attestation")
    digest = _domain_digest("c5k4-method-v1.5-isolated-runner-daemon-info-1.0", projection)
    if digest != contract["daemon"]["info_projection_sha256"]:
        raise IsolatedEvidenceRunnerError("live Docker daemon projection digest mismatch")
    attestation = contract["daemon"]["attestation"]
    try:
        key = base64.b64decode(attestation["verification_key_base64"], validate=True)
        signature = base64.b64decode(attestation["signature"], validate=True)
        if len(key) != 32 or _sha(key) != attestation["verification_key_sha256"]:
            raise IsolatedEvidenceRunnerError("daemon-attestation key differs from exact-C commitment")
        message = b"c5k4-method-v1.5-isolated-runner-daemon-attestation-1.0\0" + _canonical(projection)
        Ed25519PublicKey.from_public_bytes(key).verify(signature, message)
    except (ValueError, InvalidSignature) as exc:
        raise IsolatedEvidenceRunnerError("daemon attestation signature is invalid") from exc


def _audit_image(contract: dict[str, Any]) -> None:
    image = contract["runtime_image"]
    raw = _checked([DOCKER, "image", "inspect", image["reference"]], "runtime-image inspection")
    rows = json.loads(raw)
    if not isinstance(rows, list) or len(rows) != 1:
        raise IsolatedEvidenceRunnerError("runtime-image inspection is not singular")
    row = rows[0]
    config = row.get("Config") or {}
    expected_repo_digest = image["repository_digest"]
    digest_suffix = "@" + expected_repo_digest.rsplit("@", 1)[1]
    def normalized_repo(value: str) -> str:
        for prefix in ("docker.io/library/", "index.docker.io/library/", "registry-1.docker.io/library/"):
            if value.startswith(prefix):
                return value[len(prefix):]
        return value
    repo_digests = {normalized_repo(value) for value in (row.get("RepoDigests") or []) if value.endswith(digest_suffix)}
    if (
        row.get("Id") != image["image_id"]
        or normalized_repo(expected_repo_digest) not in repo_digests
        or row.get("Os") != "linux" or row.get("Architecture") != "amd64"
        or config.get("User") not in (image["config_user"], "")
        or (config.get("Env") or []) != image["config_env"]
        or config.get("Entrypoint") != image["config_entrypoint"]
        or config.get("Cmd") != image["config_cmd"]
        or config.get("WorkingDir") not in (image["config_working_dir"], "")
        or config.get("Volumes") not in (None, {})
        or config.get("OnBuild") not in (None, [])
    ):
        raise IsolatedEvidenceRunnerError("runtime image differs from exact-C immutable image contract")


def _validated_inputs(root: Path, command: list[str], env: dict[str, str], timeout: int) -> Path:
    """Validate the complete, exact command grammar and three-file closure."""
    unresolved_root = Path(root)
    unresolved_inputs = unresolved_root / "inputs"
    if unresolved_root.is_symlink() or unresolved_inputs.is_symlink():
        raise IsolatedEvidenceRunnerError("input closure root is not a direct non-symlink directory")
    root = unresolved_root.resolve(strict=True)
    inputs = unresolved_inputs.resolve(strict=True)
    if inputs.parent != root or not inputs.is_dir():
        raise IsolatedEvidenceRunnerError("input closure root is not a direct non-symlink directory")
    if env != EXPECTED_ENV or timeout != 30:
        raise IsolatedEvidenceRunnerError("verifier environment or timeout differs from frozen contract")
    if len(command) != 19 or command[:4] != ["/usr/local/bin/python3", "-I", "-S", "/inputs/verifier.py"]:
        raise IsolatedEvidenceRunnerError("verifier command shape differs from frozen protocol")
    fixed = {
        4: "--candidate-readiness-verify", 5: "--artifact", 6: "/inputs/artifact.json",
        7: "--schema", 8: "/inputs/artifact.schema.json", 9: "--expected-status",
        11: "--candidate", 13: "--authority-root", 15: "--service-epoch", 17: "--challenge-nonce",
    }
    if any(command[index] != value for index, value in fixed.items()):
        raise IsolatedEvidenceRunnerError("verifier command flag grammar differs from frozen protocol")
    if not command[10] or not OID.fullmatch(command[12]) or not OID.fullmatch(command[14]):
        raise IsolatedEvidenceRunnerError("verifier command status or commit binding is invalid")
    if not SHA256.fullmatch(command[16]) or not SHA256.fullmatch(command[18]):
        raise IsolatedEvidenceRunnerError("verifier command epoch or nonce binding is invalid")
    expected = {"artifact.json", "artifact.schema.json", "verifier.py"}
    if {entry.name for entry in inputs.iterdir()} != expected:
        raise IsolatedEvidenceRunnerError("isolated verifier input closure has missing or extra paths")
    for name in expected:
        path = inputs / name
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or path.is_symlink() or info.st_nlink != 1:
            raise IsolatedEvidenceRunnerError("isolated verifier inputs must be singly-linked regular files")
        path.chmod(0o444)
    return inputs


def _audit_container(row: dict[str, Any], contract: dict[str, Any], volume_name: str, command: list[str], env: dict[str, str]) -> None:
    host = row.get("HostConfig") or {}; config = row.get("Config") or {}
    mounts = row.get("Mounts") or []
    required_security = {"no-new-privileges=true", "seccomp=builtin"}
    ulimits = {item["Name"]: (item["Soft"], item["Hard"]) for item in host.get("Ulimits") or []}
    env_map: dict[str, str] = {}
    for item in config.get("Env") or []:
        key, separator, value = item.partition("=")
        if not separator or key in env_map:
            raise IsolatedEvidenceRunnerError("container environment is ambiguous")
        env_map[key] = value
    if (
        row.get("Image") != contract["runtime_image"]["image_id"]
        or config.get("Image") != contract["runtime_image"]["reference"]
        or config.get("User") != "65534:65534"
        or config.get("Hostname") != "c5k4-evidence"
        or config.get("Entrypoint") != ["/usr/bin/env"]
        or config.get("Cmd") != ["-i", *[f"{key}={env[key]}" for key in sorted(env)], *command]
        or (config.get("Env") or []) != contract["runtime_image"]["config_env"]
        or config.get("WorkingDir") != "/"
        or host.get("NetworkMode") != "none" or not host.get("ReadonlyRootfs")
        or set(host.get("CapDrop") or []) != {"ALL"} or set(host.get("SecurityOpt") or []) != required_security
        or host.get("CgroupnsMode") != "private" or host.get("IpcMode") != "private"
        or host.get("PidMode") not in ("", None) or host.get("UTSMode") not in ("", None)
        or host.get("PidsLimit") != 32 or host.get("Memory") != 536870912
        or host.get("MemorySwap") != 536870912 or host.get("NanoCpus") != 1000000000
        or ulimits != {"nofile": (64, 64), "fsize": (1048576, 1048576)}
        or host.get("Tmpfs") != {"/tmp": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"}
        or host.get("LogConfig") != {"Type": "local", "Config": {"max-file": "1", "max-size": "16k"}}
        or len(mounts) != 1 or mounts[0].get("Type") != "volume" or mounts[0].get("Name") != volume_name
        or mounts[0].get("Destination") != "/inputs" or mounts[0].get("RW") is not False
    ):
        raise IsolatedEvidenceRunnerError("effective container isolation differs from exact-C contract")


def docker_isolated_evidence_runner(
    root: Path, command: list[str], env: dict[str, str], timeout: int,
) -> subprocess.CompletedProcess[bytes]:
    """Execute the exact verifier closure or fail before unisolated execution."""
    inputs = _validated_inputs(root, command, env, timeout)
    schema_raw, contract_raw = _exact_c_component_bytes(command[12])
    contract = _load_contract(schema_raw, contract_raw)
    _live_daemon_projection(contract)
    _audit_image(contract)
    suffix = uuid.uuid4().hex
    volume = f"c5k4-v15-evidence-{suffix}"
    container = f"c5k4-v15-evidence-{suffix}"
    volume_created = False; container_created = False
    try:
        _checked([
            DOCKER, "volume", "create", "--driver", "local", "--opt", "type=none",
            "--opt", f"device={inputs}", "--opt", "o=bind,ro,nosuid,nodev,noexec", volume,
        ], "isolated input-volume creation")
        volume_created = True
        volume_row = json.loads(_checked([DOCKER, "volume", "inspect", volume], "isolated input-volume inspection"))[0]
        if volume_row.get("Driver") != "local" or volume_row.get("Options") != {
            "type": "none", "device": str(inputs), "o": "bind,ro,nosuid,nodev,noexec",
        }:
            raise IsolatedEvidenceRunnerError("effective input volume differs from exact closure mount")
        limits = contract["resource_limits"]
        create = [
            DOCKER, "create", "--name", container, "--pull", "never", "--network", "none",
            "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true",
            "--security-opt", "seccomp=builtin", "--cgroupns", "private", "--ipc", "private",
            "--user", "65534:65534", "--workdir", "/", "--hostname", "c5k4-evidence",
            "--pids-limit", str(limits["pids"]), "--memory", str(limits["memory_bytes"]),
            "--memory-swap", str(limits["memory_swap_bytes"]), "--cpus", "1",
            "--ulimit", "nofile=64:64", "--ulimit", "fsize=1048576:1048576",
            "--log-driver", "local", "--log-opt", "max-size=16k", "--log-opt", "max-file=1",
            "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=16777216,mode=1777", "--no-healthcheck",
            "--mount", f"type=volume,source={volume},target=/inputs,readonly,volume-nocopy",
        ]
        process_command = ["-i", *[f"{key}={env[key]}" for key in sorted(env)], *command]
        create.extend(["--entrypoint", "/usr/bin/env", contract["runtime_image"]["reference"], *process_command])
        created_id = _checked(create, "isolated verifier container creation").decode().strip()
        if not re.fullmatch(r"[0-9a-f]{64}", created_id):
            raise IsolatedEvidenceRunnerError("Docker returned a non-canonical container ID")
        container_created = True
        inspected = json.loads(_checked([DOCKER, "container", "inspect", created_id], "isolated verifier container inspection"))
        if not isinstance(inspected, list) or len(inspected) != 1:
            raise IsolatedEvidenceRunnerError("container inspection is not singular")
        _audit_container(inspected[0], contract, volume, command, env)
        _checked([DOCKER, "start", created_id], "isolated verifier start")
        waited = _checked([DOCKER, "wait", created_id], "isolated verifier wait", timeout=timeout)
        try:
            returncode = int(waited.decode("ascii").strip())
        except (UnicodeDecodeError, ValueError) as exc:
            raise IsolatedEvidenceRunnerError("isolated verifier exit status is invalid") from exc
        logs = _run([DOCKER, "logs", created_id], timeout=10)
        if logs.returncode != 0 or len(logs.stdout) > limits["max_output_bytes"] or len(logs.stderr) > limits["max_output_bytes"]:
            raise IsolatedEvidenceRunnerError("isolated verifier output retrieval failed closed")
        result = subprocess.CompletedProcess(command, returncode, logs.stdout, logs.stderr)
        expected = {
            "status": "CANDIDATE_READINESS_EVIDENCE_VERIFIED",
            "artifact_sha256": _sha((inputs / "artifact.json").read_bytes()),
            "verifier_sha256": _sha((inputs / "verifier.py").read_bytes()),
        }
        if result.returncode == 0 and result.stdout != _canonical(expected):
            return subprocess.CompletedProcess(result.args, 125, result.stdout, b"authenticated output mismatch")
        return result
    finally:
        if container_created:
            _checked([DOCKER, "rm", "--force", "--volumes", container], "isolated container cleanup")
        if volume_created:
            _checked([DOCKER, "volume", "rm", "--force", volume], "isolated input-volume cleanup")


if __name__ == "__main__":
    raise SystemExit("This fixed backend is an imported protocol component, not a standalone command.")
