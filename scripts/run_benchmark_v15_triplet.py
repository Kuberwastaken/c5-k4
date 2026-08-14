#!/usr/bin/env python3
"""Fail-closed PRE-P1 skeleton for one Method v1.5 three-arm launch.

The command-line interface never launches a target.  The sole executable path
is :func:`execute_with_test_kernel`, which exists for adversarial contract tests
and emits only a combined, explicitly non-operational record after every one of
the 24 injected test calls has terminated.  This module does not claim to
implement mount namespaces, production network denial, or a live Git claim.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Callable

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
RESULT_ROLES = frozenset(("CATALOGUE_RESULT", "GENERIC_RESULT", "WALL_NAVIGATION_RESULT"))
ZERO_SHA256 = "0" * 64
CLAIM_NAME = "triplet-claim.json"
COMBINED_NAME = "triplet-combined-record.json"


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover - broken Python installation
        raise RuntimeError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


envelope_validator = _load_module(
    "c5k4_v15_execution_envelope_validator",
    SCRIPTS / "validate_benchmark_v15_execution_envelope.py",
)
v14_runner = _load_module("c5k4_v14_runner_primitives", SCRIPTS / "run_benchmark_v14_job.py")


class TripletError(ValueError):
    """The triplet cannot be claimed or executed under the frozen contract."""


class TripletRejected(TripletError):
    """All test trees terminated, but a kernel attestation violated the contract."""

    def __init__(self, message: str, record: dict[str, Any]):
        super().__init__(message)
        self.record = record


class SilentArgumentParser(argparse.ArgumentParser):
    """Turn malformed public CLI input into a silent fail-closed result."""

    def error(self, message: str) -> None:
        raise TripletError(f"argument contract rejected: {message}")


@dataclass(frozen=True)
class AuthenticatedRoot:
    role: str
    path: str
    sha256: str


@dataclass(frozen=True)
class TreeInvocation:
    """Capability-minimal input passed to an injected test kernel."""

    tree_id: str
    arm: str
    tree_index: int
    launch_ordinal: int
    cpu: int
    wall_cap_seconds: int
    declared_writable_root: str
    private_test_buffer_root: str
    environment: tuple[tuple[str, str], ...]
    allowed_roots: tuple[AuthenticatedRoot, ...]
    network_policy: str = "DENY"
    network_enforcement: str = "INJECTED_TEST_KERNEL_CONTRACT_ONLY"


@dataclass(frozen=True)
class KernelCompletion:
    """Opaque streams plus non-scientific enforcement metadata from a test kernel."""

    returncode: int
    stdout: bytes
    stderr: bytes
    artifact: bytes
    accessed_root_roles: tuple[str, ...]
    network_denied: bool


TestKernel = Callable[[TreeInvocation], KernelCompletion]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def object_digest(value: dict[str, Any], digest_key: str) -> str:
    return hashlib.sha256(canonical_bytes({key: item for key, item in value.items() if key != digest_key})).hexdigest()


def bytes_digest(raw: bytes) -> dict[str, Any]:
    return {"byte_count": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TripletError(f"cannot load {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise TripletError(f"{label} must be an object")
    return value


def validate_schema(value: object, name: str, label: str) -> None:
    schema = load_json(ROOT / "schemas" / name, f"{label} schema")
    validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        raise TripletError(f"{label} schema failure at {location}: {error.message}")


def _resolve_input(campaign: Path, recorded: str, role: str) -> Path:
    pure = PurePosixPath(recorded)
    if ".." in pure.parts or "." in pure.parts:
        raise TripletError(f"{role} input path is not normalized")
    if pure.is_absolute():
        resolved = Path(recorded).resolve()
    else:
        resolved = campaign.joinpath(*pure.parts).resolve()
        try:
            resolved.relative_to(campaign)
        except ValueError as exc:
            raise TripletError(f"{role} input escapes the campaign checkout") from exc
    if not resolved.is_file():
        raise TripletError(f"{role} authenticated input is not one regular file")
    return resolved


def authenticate_envelope(
    envelope_path: Path, matrix_path: Path
) -> tuple[dict[str, Any], dict[str, Any], dict[str, AuthenticatedRoot]]:
    """Validate the complete envelope and hash every read-only root.

    No state directory is created and no one-shot claim is attempted until this
    function returns successfully.
    """

    matrix = load_json(matrix_path, "capability matrix")
    envelope = load_json(envelope_path, "execution envelope")
    try:
        envelope_validator.validate_envelope(envelope, matrix)
    except envelope_validator.EnvelopeError as exc:
        raise TripletError(f"execution envelope rejected: {exc}") from exc
    if envelope["status"] != "POST_C1_RUN_FREEZE_DRAFT_NOT_EXECUTABLE":
        raise TripletError("triplet execution requires a complete post-C1 draft envelope")
    target = envelope["target_execution"]
    campaign = Path(target["campaign_checkout"]).resolve()
    if not campaign.is_dir():
        raise TripletError("campaign checkout is not an existing directory")
    authenticated: dict[str, AuthenticatedRoot] = {}
    for root in target["digest_roots"]:
        role = root["root_role"]
        if root["access"] == "PRIVATE_RESULT_OUTPUT":
            continue
        resolved = _resolve_input(campaign, root["path"], role)
        actual = hashlib.sha256(resolved.read_bytes()).hexdigest()
        if actual != root["sha256"]:
            raise TripletError(f"{role} authenticated input digest mismatch")
        authenticated[role] = AuthenticatedRoot(role=role, path=str(resolved), sha256=actual)
    expected = set(matrix["root_roles"]) - RESULT_ROLES
    if set(authenticated) != expected:
        raise TripletError("authenticated input closure is incomplete")
    return envelope, matrix, authenticated


def sealed_arm_order(envelope_sha256: str) -> tuple[str, str, str]:
    entropy = hashlib.sha256(f"{envelope_sha256}:balanced-arm-order-v1".encode()).digest()
    permutations = tuple(itertools.permutations(ARMS))
    return permutations[int.from_bytes(entropy, "big") % len(permutations)]


def balanced_schedule(order: tuple[str, str, str]) -> tuple[tuple[str, int], ...]:
    """Interleave arms in rotated rounds; each arm receives exactly eight slots."""

    rows: list[tuple[str, int]] = []
    for tree_index in range(8):
        rotation = tree_index % len(order)
        round_order = order[rotation:] + order[:rotation]
        rows.extend((arm, tree_index) for arm in round_order)
    return tuple(rows)


def schedule_digest(schedule: tuple[tuple[str, int], ...]) -> str:
    return hashlib.sha256(canonical_bytes([[arm, index] for arm, index in schedule])).hexdigest()


def _fsync_parent(path: Path) -> None:
    descriptor = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def exclusive_write(path: Path, raw: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        remaining = memoryview(raw)
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:  # pragma: no cover - kernel/filesystem failure
                raise OSError("short write")
            remaining = remaining[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_parent(path)


def claim_once(
    state_dir: Path,
    envelope: dict[str, Any],
    order: tuple[str, str, str],
    schedule: tuple[tuple[str, int], ...],
    now: Callable[[], str],
) -> tuple[Path, dict[str, Any]]:
    state_dir.mkdir(parents=True, exist_ok=True)
    claim_path = state_dir / CLAIM_NAME
    source = envelope["target_execution"]["one_shot_claim"]
    claim = {
        "schema": "c5k4-method-v1.5-triplet-claim-1.0",
        "artifact_kind": "TEST_ONLY_THREE_ARM_EXECUTION_CLAIM",
        "protocol_version": "1.5",
        "status": "PRE_P1_TEST_ONLY_NOT_OPERATIONAL",
        "claim_state": "CLAIMED_ONCE",
        "envelope_sha256": envelope["envelope_sha256"],
        "claim_nonce_sha256": source["claim_nonce_sha256"],
        "claim_ref": source["claim_ref"],
        "claimed_at_utc": now(),
        "sealed_arm_order": list(order),
        "arm_order_derivation": "SHA256(envelope_sha256 || ':balanced-arm-order-v1') MOD 6",
        "balanced_schedule_sha256": schedule_digest(schedule),
        "prior_claims_permitted": False,
        "atomic_create": "O_CREAT|O_EXCL+FSYNC_FILE+FSYNC_PARENT",
        "claim_sha256": ZERO_SHA256,
    }
    claim["claim_sha256"] = object_digest(claim, "claim_sha256")
    validate_schema(claim, "benchmark-triplet-claim-v1.5.schema.json", "triplet claim")
    try:
        exclusive_write(claim_path, canonical_bytes(claim))
    except FileExistsError as exc:
        raise TripletError("one-shot triplet claim already exists; retry is forbidden") from exc
    return claim_path, claim


def _environment(
    private_root: Path, tree_id: str, benchmark_id: str, cluster_id: str, arm: str
) -> tuple[tuple[str, str], ...]:
    env = v14_runner.sanitized_environment(
        private_root, tree_id, benchmark_id, cluster_id, "DISCOVERY_ARM", arm
    )
    env.update({
        "C5K4_BENCHMARK_VERSION": "1.5",
        "C5K4_NETWORK_POLICY": "DENY",
        "C5K4_NETWORK_ENFORCEMENT": "INJECTED_TEST_KERNEL_CONTRACT_ONLY",
        "C5K4_PRE_P1_TEST_ONLY": "1",
    })
    return tuple(sorted(env.items()))


def _opaque_completion(tree_id: str, value: KernelCompletion | None) -> dict[str, Any]:
    if value is None:
        empty = bytes_digest(b"")
        return {
            "tree_id": tree_id,
            "status": "KERNEL_ERROR",
            "returncode": None,
            "network_denied": None,
            "accessed_root_roles": [],
            "stdout": empty,
            "stderr": empty,
            "artifact": empty,
        }
    return {
        "tree_id": tree_id,
        "status": "TERMINATED",
        "returncode": value.returncode,
        "network_denied": value.network_denied,
        "accessed_root_roles": sorted(value.accessed_root_roles),
        "stdout": bytes_digest(value.stdout),
        "stderr": bytes_digest(value.stderr),
        "artifact": bytes_digest(value.artifact),
    }


def execute_with_test_kernel(
    envelope_path: Path,
    matrix_path: Path,
    state_dir: Path,
    *,
    test_kernel: TestKernel,
    cpus: list[int] | None = None,
    now: Callable[[], str] = utc_now,
) -> dict[str, Any]:
    """Exercise the sealed contract without enabling a production launcher."""

    # Authentication is intentionally complete before state_dir is touched.
    envelope, matrix, authenticated = authenticate_envelope(envelope_path, matrix_path)
    order = sealed_arm_order(envelope["envelope_sha256"])
    schedule = balanced_schedule(order)
    claim_path, claim = claim_once(state_dir, envelope, order, schedule, now)
    started = now()
    target = envelope["target_execution"]
    available_cpus = cpus if cpus is not None else sorted(os.sched_getaffinity(0))
    if not available_cpus:
        raise TripletError("test kernel has no declared CPU slot")

    invocations: list[TreeInvocation] = []
    for ordinal, (arm, tree_index) in enumerate(schedule):
        policy = matrix["capabilities"][arm]
        allowed = tuple(authenticated[role] for role in policy["allowed_root_roles"])
        if set(root.role for root in allowed) != set(policy["allowed_root_roles"]):
            raise TripletError(f"{arm} capability closure is incomplete")
        if set(root.role for root in allowed) & set(policy["forbidden_root_roles"]):
            raise TripletError(f"{arm} capability closure escapes the frozen matrix")
        tree_id = f"{arm}-{tree_index}"
        private_root = state_dir / "private-test-buffers" / arm.lower() / str(tree_index)
        invocations.append(TreeInvocation(
            tree_id=tree_id,
            arm=arm,
            tree_index=tree_index,
            launch_ordinal=ordinal,
            cpu=-1,
            wall_cap_seconds=60,
            declared_writable_root=target["arms"][arm]["writable_root"],
            private_test_buffer_root=str(private_root),
            environment=_environment(private_root, tree_id, target["benchmark_id"], target["cluster_id"], arm),
            allowed_roots=allowed,
        ))

    def worker(invocation: TreeInvocation, cpu: int) -> dict[str, Any]:
        bound = replace(invocation, cpu=cpu)
        try:
            completion: KernelCompletion | None = test_kernel(bound)
            error_class: str | None = None
        except Exception as exc:  # all siblings must still terminate
            completion = None
            error_class = type(exc).__name__
        return {"invocation": bound, "completion": completion, "error_class": error_class}

    # This v1.4 primitive submits the entire frozen set before observing any
    # result and deliberately has no crossing predicate or cancellation path.
    raw_results, infrastructure_errors = v14_runner.run_all_processes(
        invocations, available_cpus, worker
    )
    violations: list[str] = []
    if infrastructure_errors:
        violations.append("LOW_LEVEL_RUNNER_INFRASTRUCTURE_ERROR")
    if len(raw_results) != 24:
        violations.append("INCOMPLETE_TRIPLET")

    by_tree = {row["invocation"].tree_id: row for row in raw_results}
    arm_records: dict[str, Any] = {}
    for arm in ARMS:
        completions: list[dict[str, Any]] = []
        allowed_roles = set(matrix["capabilities"][arm]["allowed_root_roles"])
        for tree_index in range(8):
            tree_id = f"{arm}-{tree_index}"
            row = by_tree.get(tree_id)
            value = None if row is None else row["completion"]
            if row is None or row["error_class"] is not None:
                violations.append(f"{tree_id}:KERNEL_ERROR")
            elif not isinstance(value, KernelCompletion):
                violations.append(f"{tree_id}:INVALID_KERNEL_COMPLETION")
                value = None
            else:
                if not value.network_denied:
                    violations.append(f"{tree_id}:NETWORK_DENIAL_NOT_ATTESTED")
                accessed = set(value.accessed_root_roles)
                if not accessed <= allowed_roles:
                    violations.append(f"{tree_id}:CAPABILITY_ESCAPE")
                if len(accessed) != len(value.accessed_root_roles):
                    violations.append(f"{tree_id}:DUPLICATE_ACCESSED_ROLE")
                if not all(isinstance(item, bytes) for item in (value.stdout, value.stderr, value.artifact)):
                    violations.append(f"{tree_id}:NON_BYTES_OPAQUE_OUTPUT")
                    value = None
            completions.append(_opaque_completion(tree_id, value))
        arm_records[arm] = {
            "declared_writable_root": target["arms"][arm]["writable_root"],
            "tree_count": 8,
            "completions": completions,
        }

    record = {
        "schema": "c5k4-method-v1.5-triplet-combined-record-1.0",
        "artifact_kind": "TEST_ONLY_THREE_ARM_COMBINED_RECORD",
        "protocol_version": "1.5",
        "status": (
            "PRE_P1_TEST_ONLY_TRIPLET_REJECTED_NOT_OPERATIONAL"
            if violations else "PRE_P1_TEST_ONLY_TRIPLET_TERMINATED_NOT_OPERATIONAL"
        ),
        "envelope_sha256": envelope["envelope_sha256"],
        "claim": {"path": CLAIM_NAME, "sha256": claim["claim_sha256"]},
        "sealed_arm_order": list(order),
        "balanced_schedule_sha256": schedule_digest(schedule),
        "started_at_utc": started,
        "finished_at_utc": now(),
        "execution_guarantees": {
            "envelope_authenticated_before_claim": True,
            "all_24_trees_submitted_before_observation": True,
            "scientific_result_parsing_performed": False,
            "result_driven_control_adaptation_performed": False,
            "network_policy": "DENY",
            "network_enforcement": "INJECTED_TEST_KERNEL_ATTESTATION_ONLY",
            "filesystem_separation": "DISTINCT_TEST_BUFFER_AND_ENVIRONMENT_PER_TREE",
            "mount_namespace_implementation": "NOT_IMPLEMENTED_BY_THIS_PRE_P1_SKELETON",
            "intermediate_stream_delivery_permitted": False,
            "intermediate_artifact_delivery_permitted": False,
            "public_output": "COMBINED_RECORD_ONLY_AFTER_ALL_24_TERMINATE",
        },
        "arms": arm_records,
        "violations": sorted(set(violations)),
        "combined_record_sha256": ZERO_SHA256,
    }
    record["combined_record_sha256"] = object_digest(record, "combined_record_sha256")
    validate_schema(
        record, "benchmark-triplet-combined-record-v1.5.schema.json", "combined triplet record"
    )
    combined_path = state_dir / COMBINED_NAME
    try:
        exclusive_write(combined_path, canonical_bytes(record))
    except FileExistsError as exc:
        raise TripletError("combined triplet record already exists; retry is forbidden") from exc
    if violations:
        raise TripletRejected("test-only triplet rejected after the complete barrier", record)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = SilentArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        # Validation is useful at the CLI boundary, but every currently allowed
        # schema status is explicitly non-executable.  No claim is written.
        matrix = load_json(args.matrix, "capability matrix")
        envelope = load_json(args.envelope, "execution envelope")
        envelope_validator.validate_envelope(envelope, matrix)
        raise TripletError(
            f"{envelope['status']}: production triplet launching is not implemented; "
            "the injected test-kernel entry point is library-only"
        )
    except (TripletError, envelope_validator.EnvelopeError):
        # The public CI/log boundary is deliberately content-free.  Callers
        # needing diagnostics use the library functions in private custody.
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
