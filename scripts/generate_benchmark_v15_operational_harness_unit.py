#!/usr/bin/env python3
"""Generate, but never install or activate, the future v1.5 harness unit.

The generator consumes one complete target-blind activation bundle, verifies
the actual P1 tree, service binary, TLS files, signed-key commitment, immutable
store acceptance, destructive-gap acceptance, and exact egress allowlist, then
emits a deterministic JSON bundle on stdout.  It has no installation, systemd,
AWS, GitHub, P1-freeze, listener, or target-execution operation.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Any, Mapping
from urllib.parse import urlsplit

from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA = ROOT / "schemas/benchmark-operational-controlled-harness-activation-v1.5.schema.json"
OUTPUT_SCHEMA = ROOT / "schemas/benchmark-operational-controlled-harness-unit-v1.5.schema.json"
ZERO = "0" * 64
NAMESPACES = ("user", "mount", "network", "pid", "ipc", "uts", "cgroup")
SYSTEMD_NAMESPACES = "user mnt net pid ipc uts cgroup"
FORBIDDEN_KEYS = frozenset({"target_id", "cluster_id", "conjecture", "statement", "statement_text", "semantic_text"})


class UnitContractError(ValueError):
    """The future operational unit cannot be generated fail-closed."""


class SilentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise UnitContractError(f"argument contract rejected: {message}")


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_object(value: Mapping[str, Any], digest_key: str) -> str:
    return hashlib.sha256(canonical_bytes({key: item for key, item in value.items() if key != digest_key})).hexdigest()


def file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise UnitContractError(f"cannot read required immutable input {path}: {exc}") from exc


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UnitContractError(f"cannot load JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise UnitContractError(f"{path}: expected one JSON object")
    return value


def validate_schema(value: object, path: Path, label: str) -> None:
    schema = load_object(path)
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        location = ".".join(str(item) for item in errors[0].absolute_path) or "$"
        raise UnitContractError(f"{label} schema failure at {location}: {errors[0].message}")


def reject_target_semantics(value: object) -> None:
    if isinstance(value, dict):
        overlap = FORBIDDEN_KEYS & set(value)
        if overlap:
            raise UnitContractError(f"target-specific field entered activation inputs: {sorted(overlap)[0]}")
        for item in value.values():
            reject_target_semantics(item)
    elif isinstance(value, list):
        for item in value:
            reject_target_semantics(item)


def rooted(filesystem_root: Path, absolute: str) -> Path:
    path = Path(absolute)
    if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise UnitContractError("an activation path is not normalized and absolute")
    try:
        root = filesystem_root.resolve(strict=True)
    except OSError as exc:
        raise UnitContractError("filesystem root is absent or unresolved") from exc
    if root != filesystem_root.absolute():
        raise UnitContractError("filesystem root itself may not be a symlink")
    candidate = root
    for part in path.parts[1:]:
        candidate = candidate / part
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            raise UnitContractError(f"required immutable path component is absent: {absolute}")
        except OSError as exc:
            raise UnitContractError(f"cannot inspect immutable path component: {absolute}") from exc
        if stat.S_ISLNK(info.st_mode):
            raise UnitContractError(f"immutable path has a symlinked parent or leaf: {absolute}")
    return candidate


def exact_regular_file(filesystem_root: Path, absolute: str, expected_sha256: str, *, executable: bool = False, private: bool = False, root_owned: bool = False) -> Path:
    path = rooted(filesystem_root, absolute)
    try:
        info = path.lstat()
    except OSError as exc:
        raise UnitContractError(f"required input is absent: {absolute}") from exc
    if not stat.S_ISREG(info.st_mode) or path.is_symlink():
        raise UnitContractError(f"required input is not a regular non-symlink file: {absolute}")
    mode = stat.S_IMODE(info.st_mode)
    if root_owned and (info.st_uid, info.st_gid) != (0, 0):
        raise UnitContractError(f"production immutable input is not root-owned: {absolute}")
    if root_owned:
        root = filesystem_root.resolve(strict=True)
        cursor = root
        for part in Path(absolute).parts[1:-1]:
            cursor = cursor / part
            parent = cursor.lstat()
            if not stat.S_ISDIR(parent.st_mode) or (parent.st_uid, parent.st_gid) != (0, 0) or stat.S_IMODE(parent.st_mode) & 0o022:
                raise UnitContractError(f"production immutable input has a mutable or non-root parent: {absolute}")
    if executable and not (mode & stat.S_IXUSR):
        raise UnitContractError(f"service binary is not owner-executable: {absolute}")
    if mode & 0o022:
        raise UnitContractError(f"required input is group/world writable: {absolute}")
    if private and mode & 0o077:
        raise UnitContractError(f"private TLS key permissions exceed 0600: {absolute}")
    if file_sha256(path) != expected_sha256:
        raise UnitContractError(f"required input digest mismatch: {absolute}")
    return path


def tree_sha256(path: Path, *, root_owned: bool = False) -> str:
    try:
        root_info = path.lstat()
    except OSError as exc:
        raise UnitContractError("P1 tree is absent") from exc
    if not stat.S_ISDIR(root_info.st_mode) or path.is_symlink() or stat.S_IMODE(root_info.st_mode) & 0o022:
        raise UnitContractError("P1 tree root is not a nonwritable real directory")
    if root_owned and (root_info.st_uid, root_info.st_gid) != (0, 0):
        raise UnitContractError("production P1 tree root is not root-owned")
    rows: list[dict[str, Any]] = []
    for directory, directories, files in os.walk(path, followlinks=False):
        base = Path(directory)
        directories.sort(); files.sort()
        for name in [*directories, *files]:
            child = base / name
            relative = child.relative_to(path).as_posix()
            info = child.lstat()
            mode = stat.S_IMODE(info.st_mode)
            if root_owned and (info.st_uid, info.st_gid) != (0, 0):
                raise UnitContractError(f"production P1 entry is not root-owned: {relative}")
            if stat.S_ISLNK(info.st_mode):
                raise UnitContractError(f"P1 tree contains a symlink: {relative}")
            if mode & 0o022:
                raise UnitContractError(f"P1 tree contains a group/world-writable entry: {relative}")
            if stat.S_ISDIR(info.st_mode):
                rows.append({"path": relative, "kind": "directory", "mode": mode})
            elif stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1:
                    raise UnitContractError(f"P1 tree contains a hardlinked file: {relative}")
                rows.append({"path": relative, "kind": "file", "mode": mode, "bytes": info.st_size, "sha256": file_sha256(child)})
            else:
                raise UnitContractError(f"P1 tree contains an unsupported filesystem object: {relative}")
    return hashlib.sha256(canonical_bytes(rows)).hexdigest()


def validate_self_digest(value: dict[str, Any], key: str, label: str) -> None:
    if value[key] != digest_object(value, key):
        raise UnitContractError(f"{label} self-digest mismatch")


def validate_network(value: dict[str, Any], listener_address: str) -> tuple[list[str], set[tuple[str, str]]]:
    listener = ipaddress.ip_address(listener_address)
    if listener.is_unspecified or listener.is_multicast:
        raise UnitContractError("listener address is unspecified or multicast")
    all_cidrs: list[str] = []
    resolutions: set[tuple[str, str]] = set()
    for endpoint in value["allowed_endpoints"]:
        for raw in endpoint["pinned_cidrs"]:
            try:
                network = ipaddress.ip_network(raw, strict=True)
            except ValueError as exc:
                raise UnitContractError(f"invalid pinned endpoint CIDR: {raw}") from exc
            if network.is_unspecified or network.is_multicast or network.is_loopback or not network.is_global:
                raise UnitContractError(f"pinned endpoint CIDR is not global unicast: {raw}")
            minimum = 24 if network.version == 4 else 64
            if network.prefixlen != network.max_prefixlen:
                raise UnitContractError(f"pinned endpoint resolution is not one exact host: {raw}")
            if network.prefixlen < minimum:  # defensive if another address family is introduced
                raise UnitContractError(f"pinned endpoint CIDR is too broad: {raw}")
            all_cidrs.append(network.with_prefixlen)
            resolutions.add((str(network.network_address), endpoint["hostname"]))
    if len(all_cidrs) != len(set(all_cidrs)):
        raise UnitContractError("two allowlisted endpoints share a pinned CIDR")
    return all_cidrs, resolutions


def validate_resolution_artifact(path: Path, expected: set[tuple[str, str]]) -> None:
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as exc:
        raise UnitContractError("cannot read pinned endpoint resolution artifact") from exc
    observed: list[tuple[str, str]] = []
    for line in lines:
        if not line or line != line.strip() or "#" in line:
            raise UnitContractError("pinned resolution artifact contains blank, padded, or commented input")
        fields = line.split()
        if len(fields) != 2:
            raise UnitContractError("pinned resolution artifact row is not exactly address hostname")
        try:
            address = ipaddress.ip_address(fields[0])
        except ValueError as exc:
            raise UnitContractError("pinned resolution artifact contains an invalid address") from exc
        observed.append((str(address), fields[1]))
    if len(observed) != len(set(observed)) or set(observed) != expected:
        raise UnitContractError("pinned resolution artifact does not exactly bind the endpoint allowlist")


def openssl(argv: list[str], *, stdin: bytes | None = None) -> bytes:
    try:
        result = subprocess.run(
            ["openssl", *argv], input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=10, env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise UnitContractError("OpenSSL identity verification is unavailable") from exc
    if result.returncode != 0 or not result.stdout:
        raise UnitContractError("OpenSSL rejected the TLS certificate or private key")
    return result.stdout


def derive_tls_spki(certificate: Path, private_key: Path, listener_endpoint: str) -> str:
    certificate_public_pem = openssl(["x509", "-in", str(certificate), "-pubkey", "-noout"])
    certificate_public_der = openssl(["pkey", "-pubin", "-outform", "DER"], stdin=certificate_public_pem)
    private_public_der = openssl(["pkey", "-in", str(private_key), "-pubout", "-outform", "DER"])
    if certificate_public_der != private_public_der:
        raise UnitContractError("TLS private key does not match the certificate")
    hostname = urlsplit(listener_endpoint).hostname
    if not hostname:
        raise UnitContractError("listener endpoint has no TLS hostname")
    openssl(["x509", "-in", str(certificate), "-checkhost", hostname, "-noout"])
    return "sha256//" + base64.b64encode(hashlib.sha256(certificate_public_der).digest()).decode("ascii")


def render_unit(value: dict[str, Any], cidrs: list[str]) -> str:
    listener = value["listener"]
    service = value["service"]
    binding = value["activation_inputs_sha256"]
    listener_ip = ipaddress.ip_address(listener["bind_address"])
    allow_lines = [f"IPAddressAllow={listener_ip}/{listener_ip.max_prefixlen}", *(f"IPAddressAllow={cidr}" for cidr in cidrs)]
    return "\n".join([
        "[Unit]",
        "Description=C5-K4 Method v1.5 controlled harness (P1-bound future unit)",
        "After=network-online.target",
        "Wants=network-online.target",
        f"ConditionPathExists={service['activation_binding_path']}",
        "",
        "[Service]",
        "Type=exec",
        "User=c5k4-benchmark-v15",
        "Group=c5k4-benchmark-v15",
        f"ExecStart={service['binary_path']} --activation-binding={service['activation_binding_path']} --expected-binding-sha256={binding} --daemon-contract={service['daemon_contract_path']} --control-socket={service['control_socket_path']} --tls-certificate={value['tls']['certificate_path']} --tls-private-key=%d/tls-private-key",
        f"LoadCredential=tls-private-key:{value['tls']['private_key_path']}",
        "WorkingDirectory=/var/lib/c5k4-benchmark-v15",
        "UMask=0077",
        "NoNewPrivileges=yes",
        "PrivateDevices=yes",
        "PrivateTmp=yes",
        "ProtectClock=yes",
        "ProtectControlGroups=no",
        "ProtectHome=yes",
        "ProtectHostname=yes",
        "ProtectKernelLogs=yes",
        "ProtectKernelModules=yes",
        "ProtectKernelTunables=yes",
        "ProtectSystem=strict",
        "ReadOnlyPaths=/opt/c5k4-benchmark-v15/p1 /etc/c5k4-benchmark-v15",
        f"BindReadOnlyPaths={value['network']['resolution_artifact_path']}:/etc/hosts",
        "ReadWritePaths=/var/lib/c5k4-benchmark-v15 /var/cache/c5k4-benchmark-v15 /run/c5k4-benchmark-v15",
        "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6",
        f"RestrictNamespaces={SYSTEMD_NAMESPACES}",
        "RestrictRealtime=yes",
        "RestrictSUIDSGID=yes",
        "LockPersonality=yes",
        "MemoryDenyWriteExecute=yes",
        "SystemCallArchitectures=native",
        "IPAddressDeny=any",
        *allow_lines,
        "Restart=no",
        "",
        "# No [Install] section: generation does not enable or activate this unit.",
        "",
    ])


def generate(value: dict[str, Any], filesystem_root: Path = Path("/")) -> dict[str, Any]:
    validate_schema(value, INPUT_SCHEMA, "activation inputs")
    reject_target_semantics(value)
    validate_self_digest(value, "activation_inputs_sha256", "activation inputs")
    validate_self_digest(value["noninterference_key_commitment"], "commitment_sha256", "noninterference key commitment")
    validate_self_digest(value["worm_acceptance"], "acceptance_sha256", "WORM acceptance")
    validate_self_digest(value["destructive_gap_acceptance"], "acceptance_sha256", "destructive-gap acceptance")

    try:
        production_root = filesystem_root.resolve(strict=True) == Path("/") and filesystem_root.absolute() == Path("/")
    except OSError as exc:
        raise UnitContractError("filesystem root is unavailable") from exc
    p1_path = rooted(filesystem_root, value["p1"]["tree_path"])
    if production_root:
        cursor = Path("/")
        for part in Path(value["p1"]["tree_path"]).parts[1:-1]:
            cursor = cursor / part
            parent = cursor.lstat()
            if not stat.S_ISDIR(parent.st_mode) or (parent.st_uid, parent.st_gid) != (0, 0) or stat.S_IMODE(parent.st_mode) & 0o022:
                raise UnitContractError("production P1 tree has a mutable or non-root parent")
    if tree_sha256(p1_path, root_owned=production_root) != value["p1"]["tree_sha256"]:
        raise UnitContractError("P1 tree digest mismatch")
    exact_regular_file(filesystem_root, value["service"]["binary_path"], value["service"]["binary_sha256"], executable=True, root_owned=production_root)
    exact_regular_file(filesystem_root, value["service"]["daemon_contract_path"], value["service"]["daemon_contract_sha256"], root_owned=production_root)
    certificate = exact_regular_file(filesystem_root, value["tls"]["certificate_path"], value["tls"]["certificate_sha256"], root_owned=production_root)
    private_key = exact_regular_file(filesystem_root, value["tls"]["private_key_path"], value["tls"]["private_key_sha256"], private=True, root_owned=production_root)
    tls_spki_sha256 = derive_tls_spki(certificate, private_key, value["listener"]["https_endpoint"])
    cidrs, expected_resolutions = validate_network(value["network"], value["listener"]["bind_address"])
    resolution = exact_regular_file(filesystem_root, value["network"]["resolution_artifact_path"], value["network"]["resolution_artifact_sha256"], root_owned=production_root)
    validate_resolution_artifact(resolution, expected_resolutions)

    network_policy = {
        "default_deny": True,
        "unlisted_egress_forbidden": True,
        "dns_policy": value["network"]["dns_policy"],
        "resolution_artifact_path": value["network"]["resolution_artifact_path"],
        "resolution_artifact_sha256": value["network"]["resolution_artifact_sha256"],
        "allowed_endpoints": value["network"]["allowed_endpoints"],
        "listener": value["listener"],
        "sha256": ZERO,
    }
    network_policy["sha256"] = digest_object(network_policy, "sha256")
    unit = render_unit(value, cidrs)
    bundle = {
        "schema": "c5k4-method-v1.5-operational-controlled-harness-unit-bundle-1.0",
        "status": "FUTURE_OPERATIONAL_UNIT_GENERATED_NOT_INSTALLED" if production_root else "FIXTURE_UNIT_GENERATED_NONOPERATIONAL",
        "protocol_version": "1.5",
        "host_id": value["host_id"],
        "activation_inputs_sha256": value["activation_inputs_sha256"],
        "p1_tree_sha256": value["p1"]["tree_sha256"],
        "service_binary_sha256": value["service"]["binary_sha256"],
        "validation_environment": {
            "filesystem_scope": "PRODUCTION_ROOT" if production_root else "FIXTURE_ROOT",
            "production_root_ownership_proven": production_root,
            "pinned_resolution_artifact_verified": True,
            "runnable_candidate": production_root,
        },
        "unit": {"name": "c5k4-benchmark-v15.service", "content": unit, "sha256": hashlib.sha256(unit.encode()).hexdigest()},
        "tls_material": {
            "certificate_source": value["tls"]["certificate_path"],
            "certificate_sha256": value["tls"]["certificate_sha256"],
            "private_key_source": value["tls"]["private_key_path"],
            "private_key_sha256": value["tls"]["private_key_sha256"],
            "private_key_runtime_credential": "%d/tls-private-key",
            "credential_loader": "systemd LoadCredential",
            "source_permissions_widened": False,
        },
        "network_policy": network_policy,
        "bound_acceptances": {
            "noninterference_key_commitment_sha256": value["noninterference_key_commitment"]["commitment_sha256"],
            "worm_acceptance_sha256": value["worm_acceptance"]["acceptance_sha256"],
            "destructive_gap_acceptance_sha256": value["destructive_gap_acceptance"]["acceptance_sha256"],
            "daemon_contract_sha256": value["service"]["daemon_contract_sha256"],
            "tls_spki_sha256": tls_spki_sha256,
            "oidc_config_sha256": hashlib.sha256(canonical_bytes(value["oidc"])).hexdigest(),
        },
        "namespace_capabilities": list(NAMESPACES),
        "target_specific": False,
        "installed": False,
        "active": False,
        "activation_permitted": False,
        "bundle_sha256": ZERO,
    }
    bundle["bundle_sha256"] = digest_object(bundle, "bundle_sha256")
    validate_schema(bundle, OUTPUT_SCHEMA, "unit bundle")
    return bundle


def main(argv: list[str] | None = None) -> int:
    parser = SilentParser(description=__doc__)
    parser.add_argument("--activation-inputs", type=Path, required=True)
    parser.add_argument("--filesystem-root", type=Path, default=Path("/"))
    try:
        args = parser.parse_args(argv)
        bundle = generate(load_object(args.activation_inputs), args.filesystem_root)
        print(canonical_bytes(bundle).decode(), end="")
    except (UnitContractError, OSError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
