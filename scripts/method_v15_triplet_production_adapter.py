#!/usr/bin/env python3
"""Non-activated production-executor adapter for the v1.5 triplet.

The adapter turns the sealed 24-tree schedule into exact Linux isolation plans
and accepts a triplet only when every plan has a fresh, same-boot attestation
from the descriptor-pinned executor.  It has no public command-line launch
path and never interprets target content or fixture output.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any, Callable, Mapping, Protocol

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ZERO = "0" * 64
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
FIXTURE_ARGV = ("/fixture/c5k4-target-free-isolation-probe-v1",)
MAX_CAPTURE_BYTES = 65_536


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


launcher = _load("c5k4_v15_adapter_triplet", SCRIPTS / "run_benchmark_v15_triplet.py")
isolation = _load("c5k4_v15_adapter_isolation", SCRIPTS / "method_v15_triplet_isolation_backend.py")
linux_acceptance = _load("c5k4_v15_adapter_linux_acceptance", SCRIPTS / "method_v15_linux_isolation_acceptance.py")


class AdapterError(ValueError):
    """The sealed production-adapter contract fails closed."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_object(value: Mapping[str, Any], digest_key: str) -> str:
    return hashlib.sha256(canonical_bytes({key: item for key, item in value.items() if key != digest_key})).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_record(raw: bytes) -> dict[str, Any]:
    return {"byte_count": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def host_fingerprint() -> str:
    """Hash stable same-boot evidence without publishing its raw identifiers."""

    try:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
        machine = Path("/etc/machine-id").read_text(encoding="ascii").strip()
    except OSError as exc:
        raise AdapterError(f"same-host identity is unavailable: {exc}") from exc
    if not boot or not machine:
        raise AdapterError("same-host identity is empty")
    material = canonical_bytes({
        "boot_id": boot,
        "machine_id": machine,
        "kernel": platform.release(),
        "machine": platform.machine(),
    })
    return hashlib.sha256(material).hexdigest()


def implementation_digests() -> dict[str, str]:
    return {
        "plan_backend_sha256": file_sha256(SCRIPTS / "method_v15_triplet_isolation_backend.py"),
        "linux_executor_sha256": file_sha256(SCRIPTS / "method_v15_linux_isolation_acceptance.py"),
        "adapter_sha256": file_sha256(Path(__file__).resolve()),
        # The fixed probe is the worker embedded in the executor; binding the
        # executable digest therefore binds the actual bytes run in the chroot.
        "fixture_executable_sha256": file_sha256(SCRIPTS / "method_v15_linux_isolation_acceptance.py"),
    }


@dataclass(frozen=True)
class SealedTreePlan:
    tree_id: str
    arm: str
    plan: dict[str, Any]


class ProductionExecutor(Protocol):
    def attest(self, sealed: SealedTreePlan, session_nonce_sha256: str) -> dict[str, Any]: ...


def _result_path_by_role(envelope: dict[str, Any]) -> dict[str, Path]:
    return {
        row["root_role"]: Path(row["path"])
        for row in envelope["target_execution"]["digest_roots"]
        if row["access"] == "PRIVATE_RESULT_OUTPUT"
    }


def build_sealed_tree_plans(
    envelope_path: Path,
    matrix_path: Path,
    private_base: Path,
    *,
    cpus: list[int] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], list[SealedTreePlan]]:
    """Map the authenticated envelope to all 24 exact-capability plans."""

    envelope, matrix, authenticated = launcher.authenticate_envelope(envelope_path, matrix_path)
    available = sorted(set(cpus if cpus is not None else os.sched_getaffinity(0)))
    if not available or any(cpu not in os.sched_getaffinity(0) for cpu in available):
        raise AdapterError("declared production CPU set is empty or unavailable")
    private_base = private_base.resolve()
    if not private_base.is_dir():
        raise AdapterError("private isolation base must pre-exist")
    results = _result_path_by_role(envelope)
    order = launcher.sealed_arm_order(envelope["envelope_sha256"])
    schedule = launcher.balanced_schedule(order)
    trees: list[SealedTreePlan] = []
    for ordinal, (arm, tree_index) in enumerate(schedule):
        capability = matrix["capabilities"][arm]
        allowed_roles = tuple(capability["allowed_root_roles"])
        forbidden_roles = tuple(capability["forbidden_root_roles"])
        allowed = tuple(
            isolation.RootSpec(role, Path(authenticated[role].path), authenticated[role].sha256)
            for role in allowed_roles
        )
        forbidden: list[tuple[str, Path]] = []
        for role in forbidden_roles:
            if role in authenticated:
                forbidden.append((role, Path(authenticated[role].path)))
            elif role in results:
                forbidden.append((role, results[role].resolve()))
            else:
                raise AdapterError(f"{arm} forbidden capability role has no sealed path: {role}")
        tree_id = f"{arm}-{tree_index}"
        request = isolation.IsolationRequest(
            tree_id=tree_id,
            arm=arm,
            argv=FIXTURE_ARGV,
            cpu=available[ordinal % len(available)],
            allowed_roots=allowed,
            forbidden_roots=tuple(forbidden),
            private_base=private_base,
        )
        plan = isolation.build_plan(request)
        if tuple(row["root_role"] for row in plan["allowed_roots"]) != allowed_roles:
            raise AdapterError(f"{tree_id} allowed capability order changed")
        if set(plan["forbidden_root_roles"]) != set(forbidden_roles):
            raise AdapterError(f"{tree_id} forbidden capability closure changed")
        if plan["wall_cap_seconds"] != 60 or plan["argv"] != list(FIXTURE_ARGV):
            raise AdapterError(f"{tree_id} fixture or time contract changed")
        trees.append(SealedTreePlan(tree_id, arm, plan))
    if len(trees) != 24 or len({tree.tree_id for tree in trees}) != 24:
        raise AdapterError("sealed schedule is not exactly 24 distinct trees")
    return envelope, matrix, trees


class LinuxProductionAcceptanceExecutor:
    """Strict adapter over the real descriptor-pinned kernel acceptance."""

    def __init__(self, run: Callable[[dict[str, Any]], dict[str, Any]] | None = None):
        self._run = run or linux_acceptance.kernel_acceptance

    def attest(self, sealed: SealedTreePlan, session_nonce_sha256: str) -> dict[str, Any]:
        if len(session_nonce_sha256) != 64 or any(c not in "0123456789abcdef" for c in session_nonce_sha256):
            raise AdapterError("session nonce must be one lowercase SHA-256")
        observed = self._run(json.loads(json.dumps(sealed.plan)))
        accepted = observed.get("kernel_acceptance_passed") is True
        checks = observed.get("checks") if isinstance(observed.get("checks"), dict) else {}
        # The current fixed kernel probe intentionally emits no semantic bytes.
        stdout = b""
        stderr = b"" if accepted else canonical_bytes({"failure_classes": observed.get("remaining_blocks", [])})
        stderr = stderr[:MAX_CAPTURE_BYTES]
        record = {
            "schema": "c5k4-method-v1.5-production-isolation-attestation-1.0",
            "artifact_kind": "TARGET_FREE_SAME_HOST_ISOLATION_ATTESTATION",
            "protocol_version": "1.5",
            "status": "PRE_P1_PRODUCTION_ADAPTER_ACCEPTANCE_NOT_OPERATIONAL",
            "tree_id": sealed.tree_id,
            "arm": sealed.arm,
            "plan_sha256": sealed.plan["plan_sha256"],
            "session_nonce_sha256": session_nonce_sha256,
            "host_fingerprint_sha256": host_fingerprint(),
            "implementation": implementation_digests(),
            "kernel_acceptance_passed": accepted,
            "checks": checks,
            "capture": {
                "exit_code": 0 if accepted else None,
                "timed_out": "FIXTURE_EXCEEDED_60_SECOND_WHOLE_TREE_CAP" in observed.get("remaining_blocks", []),
                "wall_cap_seconds": 60,
                "stdout": bytes_record(stdout),
                "stderr": bytes_record(stderr),
                "capture_limit_bytes_per_stream": MAX_CAPTURE_BYTES,
                "semantic_parsing_performed": False,
            },
            "activation_permitted": False,
            "attestation_sha256": ZERO,
        }
        record["attestation_sha256"] = digest_object(record, "attestation_sha256")
        validate_attestation(record)
        return record


def _schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def validate_attestation(value: dict[str, Any]) -> None:
    errors = sorted(
        jsonschema.Draft7Validator(_schema("benchmark-production-isolation-attestation-v1.5.schema.json")).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise AdapterError(f"attestation schema rejected: {errors[0].message}")
    if value["attestation_sha256"] != digest_object(value, "attestation_sha256"):
        raise AdapterError("attestation self-digest mismatch")


def certify_complete_triplet(
    trees: list[SealedTreePlan],
    attestations: list[dict[str, Any]],
    session_nonce_sha256: str,
) -> dict[str, Any]:
    """Reject partial, replayed, foreign-host, or mismatched acceptance sets."""

    expected = {tree.tree_id: tree for tree in trees}
    if len(trees) != 24 or len(expected) != 24:
        raise AdapterError("triplet plan closure is not 24 distinct trees")
    if len(attestations) != 24:
        raise AdapterError("all 24 acceptance attestations are required")
    if len({row.get("tree_id") for row in attestations}) != 24:
        raise AdapterError("attestation set contains a replay or duplicate tree")
    current_host = host_fingerprint()
    current_impl = implementation_digests()
    digests: list[str] = []
    for row in attestations:
        validate_attestation(row)
        tree = expected.get(row["tree_id"])
        if tree is None or row["arm"] != tree.arm:
            raise AdapterError("attestation names an unexpected tree or arm")
        if row["plan_sha256"] != tree.plan["plan_sha256"]:
            raise AdapterError(f"{tree.tree_id} attests a different plan")
        if row["session_nonce_sha256"] != session_nonce_sha256:
            raise AdapterError(f"{tree.tree_id} attestation is replayed from another session")
        if row["host_fingerprint_sha256"] != current_host:
            raise AdapterError(f"{tree.tree_id} attestation came from another host or boot")
        if row["implementation"] != current_impl:
            raise AdapterError(f"{tree.tree_id} implementation digest mismatch")
        if row["kernel_acceptance_passed"] is not True or row["activation_permitted"] is not False:
            raise AdapterError(f"{tree.tree_id} did not pass kernel acceptance")
        if row["capture"]["wall_cap_seconds"] != 60 or row["capture"]["semantic_parsing_performed"]:
            raise AdapterError(f"{tree.tree_id} capture contract mismatch")
        digests.append(row["attestation_sha256"])
    if set(expected) != {row["tree_id"] for row in attestations}:
        raise AdapterError("attestation set does not equal the sealed 24-tree schedule")
    certificate = {
        "schema": "c5k4-method-v1.5-production-triplet-acceptance-certificate-1.0",
        "artifact_kind": "TARGET_FREE_COMPLETE_TRIPLET_ACCEPTANCE_CERTIFICATE",
        "protocol_version": "1.5",
        "status": "PRE_P1_COMPLETE_ACCEPTANCE_NOT_ACTIVATED",
        "session_nonce_sha256": session_nonce_sha256,
        "host_fingerprint_sha256": current_host,
        "implementation": current_impl,
        "tree_count": 24,
        "accepted_tree_ids": sorted(expected),
        "attestation_set_sha256": hashlib.sha256(canonical_bytes(sorted(digests))).hexdigest(),
        "production_triplet_launch_permitted": False,
        "activation_permitted": False,
        "remaining_blocks": ["TRIPLET_CLI_REMAINS_INERT", "NO_P1_ACTIVATION"],
        "certificate_sha256": ZERO,
    }
    certificate["certificate_sha256"] = digest_object(certificate, "certificate_sha256")
    errors = list(jsonschema.Draft7Validator(
        _schema("benchmark-production-triplet-acceptance-certificate-v1.5.schema.json")
    ).iter_errors(certificate))
    if errors:
        raise AdapterError(f"certificate schema rejected: {errors[0].message}")
    return certificate


def attest_all(
    trees: list[SealedTreePlan], executor: ProductionExecutor, session_nonce_sha256: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Attest every plan, then cross the complete barrier; no early launch exists."""

    attestations = [executor.attest(tree, session_nonce_sha256) for tree in trees]
    return attestations, certify_complete_triplet(trees, attestations, session_nonce_sha256)


def main() -> int:
    """The public adapter is intentionally inert before P1."""

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
