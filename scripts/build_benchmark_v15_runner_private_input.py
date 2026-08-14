#!/usr/bin/env python3
"""Assemble one Method v1.5 runner input from accepted private WORM objects.

This executable is intentionally inert before P1.  It accepts no local
artifact paths: every source artifact is a version-pinned, content-addressed
private-store reference.  The public runner-input manifest is created only
after custody verification, two isolated registry executions, and atomic
private staging have all succeeded.

The command prints nothing on success or failure.  Private diagnostics must
not cross the scheduled workflow's public log boundary.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Callable

from jsonschema import Draft7Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark_v15_aggregate_certificate as aggregate  # noqa: E402
import build_benchmark_v15_future_cohort as future  # noqa: E402
import build_benchmark_v15_identity_hits as identity_hits  # noqa: E402
import build_benchmark_v15_vendor_bases as vendor  # noqa: E402
import method_v15_s3_object_lock_store as s3_store  # noqa: E402
import resolve_benchmark_v15_p1_roles as p1_roles  # noqa: E402
import verify_benchmark_v15_classifier_runtime as classifier_runtime  # noqa: E402
import verify_benchmark_v15_private_custody as custody  # noqa: E402
import verify_benchmark_v15_participant_noninterference as noninterference_verifier  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
REQUEST_SCHEMA = "benchmark-runner-private-input-assembly-v1.5.schema.json"
LOCATOR_SCHEMA = "benchmark-private-artifact-locator-v1.5.schema.json"
CUSTODY_SCHEMA = "benchmark-operational-private-custody-evidence-v1.5.schema.json"
NONINTERFERENCE_SCHEMA = "benchmark-operational-noninterference-receipt-v1.5.schema.json"
NONINTERFERENCE_KEY_COMMITMENT_SCHEMA = "benchmark-operational-noninterference-key-commitment-v1.5.schema.json"
P1R_ACTIVATION_SCHEMA = "benchmark-public-p1r-activation-receipt-v1.5.schema.json"
P1R_VALIDATOR = ROOT / "scripts/validate_benchmark_v15_candidate_base.py"
OUTPUT_SCHEMA = "benchmark-checkpoint-runner-private-input-v1.5.schema.json"
UPSTREAM = "https://github.com/google-deepmind/formal-conjectures.git"
UPSTREAM_REF = "refs/heads/main"
STATUS = "FROZEN_P1_PRIVATE_INPUT_ASSEMBLY_READY"
SOURCE_BOUNDARY = ROOT / "results/benchmark/v1.5-protocol/source-boundary.json"
SOURCE_POLICY = ROOT / "results/benchmark/v1.5-protocol/source-path-purpose-policy.json"
INVOCATION_CONTRACT = ROOT / "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json"
ASSEMBLER_ROLE = "runner_private_input_assembler"
STAGED_NAMES = {
    "custody_coverage_certificate": "custody-coverage-certificate.json",
    "public_custody_sealed_binding": "public-custody-sealed-binding.json",
    "primary_private_registry": "private-registry.json",
    "provenance_content_pack": "provenance-content-pack.json",
}
P1_SCOPE_ROLES = {
    "participant_ledger": ("participant_ledger", "participant_ledger_artifact_sha256"),
    "source_boundary": ("source_boundary", "source_boundary_sha256"),
    "noninterference_receipt": ("noninterference_receipt", "noninterference_receipt_sha256"),
    "noninterference_receipt_schema": ("operational_noninterference_receipt_schema", "noninterference_receipt_schema_sha256"),
    "noninterference_verifier": ("participant_noninterference_verifier", "noninterference_verifier_sha256"),
    "operational_noninterference_key_commitment": ("operational_noninterference_key_commitment", "operational_noninterference_key_commitment_sha256"),
    "operational_noninterference_key_commitment_schema": ("operational_noninterference_key_commitment_schema", "operational_noninterference_key_commitment_schema_sha256"),
    "classifier_readiness_receipt": ("classifier_readiness_receipt", "classifier_readiness_receipt_sha256"),
}
P1_RUNTIME_ROLES = {
    "classifier_runtime_binding_schema": (
        ROOT / "schemas/benchmark-classifier-runtime-binding-v1.5.schema.json",
        "classifier_runtime_binding_schema_sha256",
    ),
    "classifier_runtime_verifier": (
        Path(classifier_runtime.__file__).resolve(),
        "classifier_runtime_verifier_sha256",
    ),
}


class AssemblyError(RuntimeError):
    """A private assembly invariant failed; callers must suppress its text."""


class SilentParser(argparse.ArgumentParser):
    """Argument parser whose failures cannot expose command-line paths."""

    def error(self, message: str) -> None:
        raise AssemblyError(message)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _load_schema(name: str) -> dict[str, Any]:
    value = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssemblyError("invalid frozen schema")
    return value


def _validate(value: object, schema_name: str) -> None:
    try:
        Draft7Validator(
            _load_schema(schema_name), format_checker=FormatChecker()
        ).validate(value)
    except Exception as exc:
        raise AssemblyError("strict schema validation failed") from exc


def _json(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssemblyError("private artifact is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise AssemblyError("private artifact is not one JSON object")
    return value


def _utc(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except (TypeError, ValueError) as exc:
        raise AssemblyError("invalid UTC timestamp") from exc
    return parsed


def _self_digest(value: dict[str, Any], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return sha256(canonical_json(unsigned))


def _domain_digest(domain: str, value: dict[str, Any]) -> str:
    return sha256(domain.encode("ascii") + b"\0" + canonical_json(value))


def require_repo_activation(request: dict[str, Any]) -> dict[str, Any]:
    """Resolve exact executing components through published P1T/P1A roles.

    P1T supplies component identity only.  The separate full P1R receipt is
    replayed after WORM fetch and is the sole activation authority.
    """
    scope = request["p1_scope"]
    try:
        resolution = p1_roles.resolve_published_roles(
            ROOT, scope["p1t_commit"], scope["p1t_path"]
        )
        boundary = _json(SOURCE_BOUNDARY.read_bytes())
        policy = _json(SOURCE_POLICY.read_bytes())
        invocation = _json(INVOCATION_CONTRACT.read_bytes())
    except Exception as exc:
        raise AssemblyError("repository component-role evidence is unavailable") from exc
    if (
        resolution.get("status") != "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE"
        or resolution.get("operational") is not True
        or resolution.get("resolution_sha256") != scope["role_resolution_sha256"]
        or resolution.get("p1", {}).get("p1t_commit") != scope["p1t_commit"]
        or resolution.get("p1", {}).get("p1t_path") != scope["p1t_path"]
    ):
        raise AssemblyError("published P1 role resolution differs from request scope")
    roles = {
        row.get("role"): row
        for row in resolution.get("resolved_roles", [])
        if isinstance(row, dict) and row.get("closure") == "NATIVE_V1_5"
    }
    required = {
        ASSEMBLER_ROLE: (Path(__file__).resolve(), scope["assembler_sha256"]),
        "source_boundary": (SOURCE_BOUNDARY, scope["source_boundary_sha256"]),
        "source_path_policy": (SOURCE_POLICY, scope["source_policy_sha256"]),
        "checkpoint_invocation_contract": (
            INVOCATION_CONTRACT, scope["invocation_contract_sha256"]
        ),
    }
    for role, (path, expected) in required.items():
        row = roles.get(role)
        if (
            not isinstance(row, dict)
            or row.get("path") != path.relative_to(ROOT).as_posix()
            or row.get("sha256") != expected
            or sha256_file(path) != expected
        ):
            raise AssemblyError(f"resolved {role} bytes do not match P1 components")
    if scope["assembler_sha256"] != request["runner_contract"]["assembly_executable_sha256"]:
        raise AssemblyError("request assembler digest differs from activated P1 role")
    readiness = boundary.get("operational_readiness")
    if (
        boundary.get("status") != "FROZEN_P1_EXECUTABLE"
        or boundary.get("executable") is not True
        or not isinstance(readiness, dict)
        or readiness.get("fail_closed") is not True
        or readiness.get("executable") is not True
        or policy.get("status") != "FROZEN_P1_EXECUTABLE"
        or invocation.get("status") != "FROZEN_P1_EXECUTABLE"
    ):
        raise AssemblyError("repository source/runner boundary is not activated")
    return resolution


def validate_request(value: dict[str, Any]) -> None:
    """Validate activation, executable, acceptance and retention bindings."""
    _validate(value, REQUEST_SCHEMA)
    if value.get("status") != STATUS:
        raise AssemblyError("private assembler is not activated")
    runner = value["runner_contract"]
    if runner["assembly_executable_sha256"] != sha256_file(Path(__file__).resolve()):
        raise AssemblyError("assembler bytes are not the accepted bytes")
    acceptance = value["store_acceptance"]
    expected_acceptance = _self_digest(acceptance, "acceptance_sha256")
    if acceptance["acceptance_sha256"] != expected_acceptance:
        raise AssemblyError("store acceptance self-digest mismatch")
    if _utc(acceptance["retention_through_utc"]) < _utc(
        value["checkpoint"]["required_custody_through_utc"]
    ):
        raise AssemblyError("accepted retention does not cover the custody interval")


def _validate_p1_scope(request: dict[str, Any], raw: dict[str, bytes | list[bytes]]) -> dict[str, Any]:
    """Authenticate caller scope against exact native bytes resolved by P1A."""
    scope = request["p1_scope"]
    if scope["required_host_id"] != "ai-vps-controlled-harness":
        raise AssemblyError("runner custody is not scoped to the controlled harness")
    try:
        resolution = p1_roles.resolve_published_roles(
            ROOT, scope["p1t_commit"], scope["p1t_path"]
        )
    except Exception as exc:
        raise AssemblyError("P1 scope closure is unavailable") from exc
    resolution_raw = raw["p1_role_resolution"]
    assert isinstance(resolution_raw, bytes)
    if (
        canonical_json(resolution) != resolution_raw
        or resolution.get("resolution_sha256") != scope["role_resolution_sha256"]
        or resolution.get("status") != "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE"
        or resolution.get("operational") is not True
    ):
        raise AssemblyError("stored and live P1 role resolutions differ")
    components = {
        row["role"]: row for row in resolution.get("resolved_roles", [])
        if row.get("closure") == "NATIVE_V1_5"
    }
    for artifact, (role, scope_key) in P1_SCOPE_ROLES.items():
        row = components.get(role)
        value = raw[artifact]
        assert isinstance(value, bytes)
        expected = scope[scope_key]
        if not isinstance(row, dict) or row.get("sha256") != expected or sha256(value) != expected:
            raise AssemblyError(f"{artifact} does not resolve through exact P1 native bytes")
    for role, (path, scope_key) in P1_RUNTIME_ROLES.items():
        row = components.get(role)
        expected = scope[scope_key]
        if (
            not isinstance(row, dict)
            or row.get("sha256") != expected
            or row.get("path") != path.relative_to(ROOT).as_posix()
            or sha256_file(path) != expected
        ):
            raise AssemblyError(f"{role} does not resolve through executing P1 native bytes")
    participant = _json(raw["participant_ledger"])  # type: ignore[arg-type]
    boundary = _json(raw["source_boundary"])  # type: ignore[arg-type]
    receipt = _json(raw["noninterference_receipt"])  # type: ignore[arg-type]
    receipt_schema_raw = raw["noninterference_receipt_schema"]
    verifier_raw = raw["noninterference_verifier"]
    verification_key = raw["noninterference_verification_key"]
    key_commitment = _json(raw["operational_noninterference_key_commitment"])  # type: ignore[arg-type]
    key_commitment_schema_raw = raw["operational_noninterference_key_commitment_schema"]
    assert isinstance(receipt_schema_raw, bytes)
    assert isinstance(verifier_raw, bytes)
    assert isinstance(verification_key, bytes)
    assert isinstance(key_commitment_schema_raw, bytes)
    if len(verification_key) != 32:
        raise AssemblyError("noninterference verification key is not raw Ed25519")
    if (
        receipt_schema_raw != (ROOT / "schemas" / NONINTERFERENCE_SCHEMA).read_bytes()
        or verifier_raw != Path(noninterference_verifier.__file__).resolve().read_bytes()
        or key_commitment_schema_raw != (ROOT / "schemas" / NONINTERFERENCE_KEY_COMMITMENT_SCHEMA).read_bytes()
    ):
        raise AssemblyError("noninterference schema/verifier differs from P1 native bytes")
    _validate(key_commitment, NONINTERFERENCE_KEY_COMMITMENT_SCHEMA)
    if (
        key_commitment["commitment_sha256"] != _self_digest(key_commitment, "commitment_sha256")
        or key_commitment["verification_key_sha256"] != sha256(verification_key)
        or key_commitment["signing_key_id"] != receipt.get("signing_key_id")
        or key_commitment["host_id"] != receipt.get("host_id")
        or key_commitment["verification_key_sha256"] != receipt.get("verification_key_sha256")
    ):
        raise AssemblyError("operational key commitment does not bind receipt and WORM key")
    try:
        noninterference_verifier.verify_operational(
            participant,
            scope["source_boundary_sha256"],
            receipt,
            verification_key,
        )
    except Exception as exc:
        raise AssemblyError("operational noninterference receipt verification failed") from exc
    if (
        participant.get("host_id") != "ai-vps-controlled-harness"
        or participant.get("ledger_sha256") != scope["participant_ledger_sha256"]
        or receipt.get("host_id") != "ai-vps-controlled-harness"
        or receipt.get("participant_ledger_sha256") != scope["participant_ledger_sha256"]
        or receipt.get("source_boundary_sha256") != scope["source_boundary_sha256"]
        or sha256(receipt_schema_raw) != scope["noninterference_receipt_schema_sha256"]
        or sha256(verifier_raw) != scope["noninterference_verifier_sha256"]
        or sha256(key_commitment_schema_raw) != scope["operational_noninterference_key_commitment_schema_sha256"]
        or receipt.get("scope_complete") is not True
        or receipt.get("unjournaled_delivery_detected") is not False
        or boundary.get("status") != "FROZEN_P1_EXECUTABLE"
    ):
        raise AssemblyError("authenticated P1 scope/noninterference receipt is not operational")
    return receipt


def _validate_p1r_activation(
    request: dict[str, Any], raw: dict[str, bytes | list[bytes]]
) -> dict[str, Any]:
    """Replay the full public P1R receipt against U1 and the chain proof.

    P1T remains the component-role closure only.  The nine-field public P1R
    receipt is the activation authority, and its complete canonical bytes are
    content-addressed by the private request before any target-bearing input is
    parsed.
    """
    receipt_raw = raw["p1r_activation_receipt"]
    u1_raw = raw["u1_receipt"]
    proof_raw = raw["public_chain_proof"]
    assert isinstance(receipt_raw, bytes)
    assert isinstance(u1_raw, bytes)
    assert isinstance(proof_raw, bytes)
    receipt = _json(receipt_raw)
    _validate(receipt, P1R_ACTIVATION_SCHEMA)
    if canonical_json(receipt) != receipt_raw:
        raise AssemblyError("P1R activation receipt is not canonical JSON")
    unsigned = dict(receipt)
    recorded_receipt_sha256 = unsigned.pop("receipt_sha256", None)
    if recorded_receipt_sha256 != _domain_digest(receipt["schema"], unsigned):
        raise AssemblyError("P1R activation receipt self-digest is invalid")
    scope = request["p1_scope"]
    if (
        sha256(receipt_raw) != scope["p1r_activation_receipt_sha256"]
        or receipt["p1r_commit"] != scope["p1r_commit"]
        or receipt["activation_boundary"] != "PUBLIC_AUTHENTICATED_P1R"
        or receipt["validator"] != {
            "path": P1R_VALIDATOR.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(P1R_VALIDATOR),
        }
    ):
        raise AssemblyError("full P1R activation receipt differs from request scope")
    u1 = _json(u1_raw)
    proof = _json(proof_raw)
    if (
        u1.get("p1", {}).get("p1r_commit") != scope["p1r_commit"]
        or u1.get("p1", {}).get("activation_receipt") != receipt
        or u1.get("p1", {}).get("p1r_activation_sha256")
        != scope["p1r_activation_receipt_sha256"]
        or proof.get("p1r_commit") != scope["p1r_commit"]
        or proof.get("p1r_activation") != receipt
        or proof.get("p1r_activation_sha256")
        != scope["p1r_activation_receipt_sha256"]
    ):
        raise AssemblyError("U1/public-chain proof does not bind the exact P1R receipt")
    return receipt


def fetch_artifacts(
    request: dict[str, Any], fetch: Callable[[dict[str, Any]], bytes]
) -> dict[str, bytes | list[bytes]]:
    """Fetch every exact WORM version and reverify its private locator."""
    acceptance_sha = request["store_acceptance"]["acceptance_sha256"]

    def one(locator: dict[str, Any]) -> bytes:
        _validate(locator, LOCATOR_SCHEMA)
        if locator["store_acceptance_sha256"] != acceptance_sha:
            raise AssemblyError("private locator belongs to another accepted store")
        if _utc(locator["retain_until_utc"]) < _utc(
            request["checkpoint"]["required_custody_through_utc"]
        ):
            raise AssemblyError("private object retention ends too early")
        try:
            raw = fetch(locator)
        except Exception as exc:
            raise AssemblyError("private object fetch failed") from exc
        if not isinstance(raw, bytes):
            raise AssemblyError("private object fetch did not return bytes")
        if len(raw) != locator["byte_count"] or sha256(raw) != locator["sha256"]:
            raise AssemblyError("private object bytes differ from locator")
        return raw

    result: dict[str, bytes | list[bytes]] = {}
    for name, locator in request["artifacts"].items():
        if name == "provenance_ledgers":
            result[name] = [one(item) for item in locator]
        else:
            result[name] = one(locator)
    return result


def _validate_custody(
    request: dict[str, Any], raw: dict[str, bytes | list[bytes]]
) -> None:
    noninterference = _validate_p1_scope(request, raw)
    coverage = _json(raw["custody_coverage_certificate"])  # type: ignore[arg-type]
    binding = _json(raw["public_custody_sealed_binding"])  # type: ignore[arg-type]
    _validate(coverage, CUSTODY_SCHEMA)
    _validate(binding, CUSTODY_SCHEMA)
    if coverage["status"] != "FROZEN_P1_CUSTODY_COVERAGE_VALID":
        raise AssemblyError("custody coverage is not operationally accepted")
    if binding["status"] != "FROZEN_P1_PUBLIC_BINDING_VALID":
        raise AssemblyError("custody seal is not operationally accepted")
    if coverage["certificate_sha256"] != custody.certificate_digest(coverage):
        raise AssemblyError("custody coverage digest mismatch")
    if binding["binding_sha256"] != custody.binding_digest(binding):
        raise AssemblyError("custody binding digest mismatch")
    checkpoint = request["checkpoint"]
    chains = coverage["host_chains"]
    chain_hosts = [row["host_id"] for row in chains]
    if (
        chain_hosts != coverage["required_hosts"]
        or len(set(chain_hosts)) != len(chain_hosts)
    ):
        raise AssemblyError("custody host chains do not exactly cover required hosts")
    required_from = _utc(coverage["required_from_utc"])
    required_through = _utc(coverage["required_through_utc"])
    for chain in chains:
        if (
            _utc(chain["first_observed_at_utc"]) > required_from
            or _utc(chain["last_observed_at_utc"]) < required_through
            or chain["last_batch_sequence"] - chain["first_batch_sequence"] + 1
            != chain["batch_count"]
            or chain["last_record_sequence"] - chain["first_record_sequence"] + 1
            != chain["record_count"]
            or chain["maximum_observed_gap_seconds"]
            > coverage["maximum_heartbeat_interval_seconds"]
        ):
            raise AssemblyError("custody host-chain coverage does not replay")
    if (
        coverage["required_from_utc"] != checkpoint["required_custody_from_utc"]
        or coverage["required_through_utc"] != checkpoint["required_custody_through_utc"]
        or binding["required_from_utc"] != coverage["required_from_utc"]
        or binding["required_through_utc"] != coverage["required_through_utc"]
        or binding["required_host_count"] != len(coverage["required_hosts"])
        or binding["private_coverage_certificate_sha256"]
        != coverage["certificate_sha256"]
    ):
        raise AssemblyError("custody interval or seal binding mismatch")
    scope = request["p1_scope"]
    expected_scope = {
        "participant_ledger_sha256": scope["participant_ledger_sha256"],
        "source_boundary_sha256": scope["source_boundary_sha256"],
        "noninterference_receipt_sha256": scope["noninterference_receipt_sha256"],
        "store_acceptance_sha256": request["store_acceptance"]["acceptance_sha256"],
        "service_epoch_binding_sha256": noninterference["service_epoch_binding_sha256"],
    }
    if any(coverage.get(key) != value or binding.get(key) != value for key, value in expected_scope.items()):
        raise AssemblyError("custody evidence scope differs from P1/noninterference bindings")
    host = chains[0]
    if (
        coverage["required_hosts"] != ["ai-vps-controlled-harness"]
        or host["host_id"] != "ai-vps-controlled-harness"
        or host["signing_key_id"] != noninterference["signing_key_id"]
    ):
        raise AssemblyError("custody host/key differs from frozen noninterference scope")
    sealed = raw["sealed_private_custody_bundle"]
    assert isinstance(sealed, bytes)
    if (
        binding["sealed_private_bundle_sha256"] != sha256(sealed)
        or binding["sealed_private_bundle_byte_count"] != len(sealed)
    ):
        raise AssemblyError("sealed custody bundle does not match its public binding")


def _validate_acquisitions(
    primary: dict[str, Any], replay: dict[str, Any], capture: dict[str, Any]
) -> tuple[Path, Path]:
    try:
        vendor.validate_receipt(primary)
        vendor.validate_receipt(replay)
    except Exception as exc:
        raise AssemblyError("isolated acquisition receipt failed live replay") from exc
    if (
        primary["remote"] != UPSTREAM
        or replay["remote"] != UPSTREAM
        or primary["remote_ref"] != UPSTREAM_REF
        or replay["remote_ref"] != UPSTREAM_REF
    ):
        raise AssemblyError("acquisition source is not canonical upstream main")
    primary_path = Path(primary["repository_path"]).resolve()
    replay_path = Path(replay["repository_path"]).resolve()
    if primary_path == replay_path or primary["receipt_sha256"] == replay["receipt_sha256"]:
        raise AssemblyError("registry replay did not use a distinct acquisition")
    left, right = primary["audit"], replay["audit"]
    upstream = capture.get("upstream")
    if (
        not isinstance(upstream, dict)
        or left.get("commit") != right.get("commit")
        or left.get("root_tree") != right.get("root_tree")
        or left.get("commit") != upstream.get("commit")
        or left.get("root_tree") != upstream.get("root_tree")
    ):
        raise AssemblyError("two acquisitions do not authenticate the captured U2")
    return primary_path, replay_path


def _registry_inputs(raw: dict[str, bytes | list[bytes]]) -> dict[str, str]:
    names = (
        "u1_receipt", "checkpoint_capture", "v14_exclusion", "grouping_rule",
        "classifier", "provenance_content_pack", "public_chain_proof",
        "p1r_activation_receipt",
    )
    values = {
        ("u2_receipt" if name == "checkpoint_capture" else name) + "_sha256":
        sha256(raw[name])  # type: ignore[arg-type]
        for name in names
    }
    ledgers = raw["provenance_ledgers"]
    assert isinstance(ledgers, list)
    values.update({f"provenance_ledger_{index}_sha256": sha256(value)
                   for index, value in enumerate(ledgers)})
    return values


def verify_private_replay(
    request: dict[str, Any], raw: dict[str, bytes | list[bytes]], work: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Re-execute the frozen registry against two distinct isolated stores."""
    _validate_p1r_activation(request, raw)
    _verify_classifier_runtime(raw, work)
    u1 = _json(raw["u1_receipt"])  # type: ignore[arg-type]
    capture = _json(raw["checkpoint_capture"])  # type: ignore[arg-type]
    v14 = _json(raw["v14_exclusion"])  # type: ignore[arg-type]
    grouping = _json(raw["grouping_rule"])  # type: ignore[arg-type]
    classifier = _json(raw["classifier"])  # type: ignore[arg-type]
    proof = _json(raw["public_chain_proof"])  # type: ignore[arg-type]
    pack = _json(raw["provenance_content_pack"])  # type: ignore[arg-type]
    ledgers_raw = raw["provenance_ledgers"]
    assert isinstance(ledgers_raw, list)
    ledgers = [_json(value) for value in ledgers_raw]
    supplied = _json(raw["primary_private_registry"])  # type: ignore[arg-type]
    supplied_replay = _json(raw["replayed_private_registry"])  # type: ignore[arg-type]
    primary_receipt = _json(raw["primary_acquisition_receipt"])  # type: ignore[arg-type]
    replay_receipt = _json(raw["replay_acquisition_receipt"])  # type: ignore[arg-type]

    for ledger in ledgers:
        _validate(ledger, "benchmark-provenance-ledger-v1.5.schema.json")
    _validate(pack, "benchmark-private-provenance-content-pack-v1.5.schema.json")
    _validate(supplied, "benchmark-future-registry-output-v1.5.schema.json")
    _validate(supplied_replay, "benchmark-future-registry-output-v1.5.schema.json")
    _validate(proof, "benchmark-public-checkpoint-chain-proof-v1.5.schema.json")
    if (
        proof.get("proof_sha256") != request["checkpoint"]["public_chain_proof_sha256"]
        or capture.get("scheduled_for_utc") != request["checkpoint"]["scheduled_for_utc"]
        or capture.get("artifact_kind") != "CHECKPOINT_CAPTURE"
        or capture.get("status") != "AWAITING_MACHINE_QUOTA_CERTIFICATE"
        or capture.get("basis", {}).get("public_chain_proof", {}).get("proof_sha256")
        != proof.get("proof_sha256")
    ):
        raise AssemblyError("checkpoint capture, chain proof, and request differ")
    primary_repo, replay_repo = _validate_acquisitions(
        primary_receipt, replay_receipt, capture
    )
    try:
        contents = identity_hits.load_content_pack(pack)
    except Exception as exc:
        raise AssemblyError("private content pack failed verification") from exc
    classifier_path = work / "classifier.json"
    classifier_path.write_bytes(raw["classifier"])  # type: ignore[arg-type]
    inputs = _registry_inputs(raw)

    def execute(repository: Path) -> dict[str, Any]:
        try:
            return future.build(
                u1, capture, v14, grouping, classifier, classifier_path,
                input_digests=inputs, repository=repository,
                provenance_ledgers=ledgers, provenance_contents=contents,
                public_chain_proof=proof,
            )
        except Exception as exc:
            raise AssemblyError("isolated private-registry execution failed") from exc

    first = execute(primary_repo)
    second = execute(replay_repo)
    first_raw, second_raw = future.pretty_json(first), future.pretty_json(second)
    if (
        first_raw != second_raw
        or first_raw != raw["primary_private_registry"]
        or second_raw != raw["replayed_private_registry"]
    ):
        raise AssemblyError("private registry did not replay byte-identically")
    if supplied.get("registry_sha256") != future.registry_digest(supplied):
        raise AssemblyError("private registry self-digest mismatch")
    return ledgers, pack


def _verify_classifier_runtime(
    raw: dict[str, bytes | list[bytes]], work: Path
) -> dict[str, Any]:
    """Authenticate classifier/runtime closure before any target-row parse."""
    try:
        resolution_raw = raw["p1_role_resolution"]
        readiness_raw = raw["classifier_readiness_receipt"]
        classifier_raw = raw["classifier"]
        assert isinstance(resolution_raw, bytes)
        assert isinstance(readiness_raw, bytes)
        assert isinstance(classifier_raw, bytes)

        resolution = classifier_runtime.strict_json(
            resolution_raw, "P1 role resolution"
        )
        roles = {
            (row.get("closure"), row.get("role")): row
            for row in resolution.get("resolved_roles", [])
            if isinstance(row, dict)
        }
        components: dict[str, dict[str, str]] = {}
        for name, (closure_name, role_name) in classifier_runtime.EXPECTED_COMPONENTS.items():
            row = roles.get((closure_name, role_name))
            if not isinstance(row, dict):
                raise AssemblyError("classifier runtime role is absent")
            components[name] = {
                "closure": closure_name,
                "role": role_name,
                "path": row["path"],
                "sha256": row["sha256"],
            }

        resolution_path = work / "p1-role-resolution.json"
        readiness_path = work / "classifier-readiness.json"
        classifier_path = work / "classifier.json"
        resolution_path.write_bytes(resolution_raw)
        readiness_path.write_bytes(readiness_raw)
        classifier_path.write_bytes(classifier_raw)
        binding = {
            "schema": "c5k4-method-v1.5-classifier-runtime-binding-1.0",
            "status": "FROZEN_P1_PRE_REGISTRY_CLASSIFIER_BINDING",
            "target_data_access_permitted": False,
            "future_registry_invocation_started": False,
            "p1_role_resolution": {
                "path": str(resolution_path.resolve()),
                "sha256": sha256(resolution_raw),
            },
            "classifier_readiness_receipt": {
                "path": str(readiness_path.resolve()),
                "sha256": sha256(readiness_raw),
            },
            "consumed_classifier": {
                "path": str(classifier_path.resolve()),
                "sha256": sha256(classifier_raw),
            },
            "components": components,
        }
        binding_path = work / "classifier-runtime-binding.json"
        binding_path.write_bytes(canonical_json(binding))
        result = classifier_runtime.verify(binding_path)
        if (
            result.get("status")
            != "CLASSIFIER_RUNTIME_AUTHENTICATED_BEFORE_REGISTRY"
            or result.get("target_data_read") is not False
            or result.get("future_registry_invocation_started") is not False
        ):
            raise AssemblyError("classifier runtime verifier returned unsafe status")
        return result
    except Exception as exc:
        if isinstance(exc, AssemblyError):
            raise
        raise AssemblyError(
            "classifier runtime gate failed before registry access"
        ) from exc


def _fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_new_file(path: Path, raw: bytes) -> None:
    """Publish a previously absent file atomically without overwrite."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError as exc:
            raise AssemblyError("private runner-input output already exists") from exc
        _fsync_dir(path.parent)
    finally:
        temporary_path.unlink(missing_ok=True)


def _stage_private(
    stage: Path, raw: dict[str, bytes | list[bytes]]
) -> tuple[dict[str, Path], list[Path]]:
    if os.path.lexists(stage):
        raise AssemblyError("private staging destination must be previously absent")
    stage.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{stage.name}.", dir=stage.parent))
    paths: dict[str, Path] = {}
    ledger_paths: list[Path] = []
    try:
        for key, name in STAGED_NAMES.items():
            value = raw[key]
            assert isinstance(value, bytes)
            path = temporary / name
            path.write_bytes(value)
            path.chmod(0o600)
            paths[key] = path
        ledgers = raw["provenance_ledgers"]
        assert isinstance(ledgers, list)
        for index, value in enumerate(ledgers):
            path = temporary / f"provenance-ledger-{index:04d}.json"
            path.write_bytes(value)
            path.chmod(0o600)
            ledger_paths.append(path)
        for path in temporary.iterdir():
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
        _fsync_dir(temporary)
        os.rename(temporary, stage)
        _fsync_dir(stage.parent)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise
    translated = {key: stage / path.name for key, path in paths.items()}
    translated_ledgers = [stage / path.name for path in ledger_paths]
    return translated, translated_ledgers


def assemble(
    request: dict[str, Any], fetch: Callable[[dict[str, Any]], bytes],
    stage: Path, output: Path, *,
    activation_guard: Callable[[dict[str, Any]], Any] = require_repo_activation,
) -> None:
    """Create the existing runner-input manifest last, or create nothing public."""
    validate_request(request)
    activation_guard(request)
    if output.exists() or os.path.lexists(stage):
        raise AssemblyError("assembly destinations must be previously absent")
    raw = fetch_artifacts(request, fetch)
    _validate_custody(request, raw)
    with tempfile.TemporaryDirectory(prefix="method-v15-private-replay-") as work:
        verify_private_replay(request, raw, Path(work))
    staged, ledger_paths = _stage_private(stage.resolve(), raw)
    replay_receipt = _json(raw["replay_acquisition_receipt"])  # type: ignore[arg-type]
    manifest = {
        "schema": "c5k4-method-v1.5-checkpoint-runner-private-input-1.0",
        "status": "PRIVATE_CUSTODY_READY",
        "runner_contract": {
            "mode": "CAPTURE",
            "runner_path": "scripts/run_benchmark_v15_checkpoint.py",
            "invocation_contract_path": "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json",
            "private_input_argument": "--private-input",
        },
        "checkpoint": {
            "scheduled_for_utc": request["checkpoint"]["scheduled_for_utc"],
            "public_chain_proof_sha256": request["checkpoint"]["public_chain_proof_sha256"],
        },
        "custody": {
            "coverage_certificate": {
                "path": str(staged["custody_coverage_certificate"]),
                "sha256": sha256_file(staged["custody_coverage_certificate"]),
            },
            "public_sealed_binding": {
                "path": str(staged["public_custody_sealed_binding"]),
                "sha256": sha256_file(staged["public_custody_sealed_binding"]),
            },
            "participant_ledger_sha256": request["p1_scope"]["participant_ledger_sha256"],
            "source_boundary_sha256": request["p1_scope"]["source_boundary_sha256"],
            "noninterference_receipt_sha256": request["p1_scope"]["noninterference_receipt_sha256"],
            "host_id": "ai-vps-controlled-harness",
            "signing_key_id": _json(raw["noninterference_receipt"])["signing_key_id"],  # type: ignore[arg-type]
            "service_epoch_binding_sha256": _json(raw["noninterference_receipt"])["service_epoch_binding_sha256"],  # type: ignore[arg-type]
            "store_acceptance_sha256": request["store_acceptance"]["acceptance_sha256"],
        },
        "registry": {
            "private_registry": {
                "path": str(staged["primary_private_registry"]),
                "sha256": sha256_file(staged["primary_private_registry"]),
            },
            "provenance_content_pack": {
                "path": str(staged["provenance_content_pack"]),
                "sha256": sha256_file(staged["provenance_content_pack"]),
            },
            "provenance_ledgers": [
                {"path": str(path), "sha256": sha256_file(path)}
                for path in ledger_paths
            ],
        },
        "replay": {
            "isolated_repository": str(Path(replay_receipt["repository_path"]).resolve()),
            "fresh_reacquisition_completed": True,
            "network_acquisition_by_runner": False,
        },
    }
    _validate(manifest, OUTPUT_SCHEMA)
    _atomic_new_file(output.resolve(),
                     json.dumps(manifest, sort_keys=True, indent=2).encode() + b"\n")


def _s3_fetcher(config: dict[str, Any]) -> Callable[[dict[str, Any]], bytes]:
    try:
        import boto3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise AssemblyError("private store client is unavailable") from exc
    store = s3_store.S3ObjectLockStore(
        boto3.client("s3", region_name=config["region"]), config
    )

    def fetch(locator: dict[str, Any]) -> bytes:
        reference = s3_store.PrivateObjectRef(
            bucket=locator["bucket"], key=locator["key"],
            version_id=locator["version_id"], sha256=locator["sha256"],
            byte_count=locator["byte_count"],
            retain_until_utc=locator["retain_until_utc"],
        )
        return store.get(reference)

    return fetch


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = SilentParser(add_help=False)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--store-config", type=Path, required=True)
    parser.add_argument("--private-stage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        request = _json(args.request.read_bytes())
        validate_request(request)
        # Public request scope is the only caller input read before the
        # repo-authenticated gate.  No config, client, private fetch or output
        # path is touched until exact published P1 roles authenticate it.
        require_repo_activation(request)
        config_raw = args.store_config.read_bytes()
        config = _json(config_raw)
        validate_request(request)
        if sha256(config_raw) != request["store_acceptance"]["config_sha256"]:
            raise AssemblyError("store configuration differs from accepted bytes")
        assemble(
            request, _s3_fetcher(config), args.private_stage.resolve(),
            args.output.resolve(), activation_guard=lambda _request: None,
        )
    except Exception:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
