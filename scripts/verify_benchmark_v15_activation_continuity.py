#!/usr/bin/env python3
"""Verify one identity/evidence chain from P1 unit to noninterference receipt.

This module is deliberately read-only and target blind.  It does not install a
unit, call AWS, start a listener, freeze P1, or create/sign a receipt.  Its main
purpose is to prevent a live activation from combining a participant ledger,
deployment, unit, key, WORM acceptance, and destructive-gap acceptance that
refer to different service identities or filesystem boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping
from urllib.parse import urlsplit

from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
PROTOCOL = ROOT / "results" / "benchmark" / "v1.5-protocol"
SHA = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = frozenset({
    "target", "target_id", "target_identity", "cluster", "cluster_id",
    "conjecture", "statement", "statement_text", "semantic_text", "outcome",
})
CANONICAL_AUDIENCE_PREFIX = "c5k4-method-v1.5"
CANONICAL_CHECKPOINT_PATH = "/v1/checkpoint"


class ContinuityError(ValueError):
    """Operational artifacts do not form one exact activation identity."""


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContinuityError(f"cannot load frozen verifier {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


noninterference = _load_module(
    "c5k4_v15_activation_noninterference",
    ROOT / "scripts" / "verify_benchmark_v15_participant_noninterference.py",
)
infrastructure = _load_module(
    "c5k4_v15_activation_infrastructure",
    ROOT / "scripts" / "verify_benchmark_v15_immutable_infrastructure.py",
)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContinuityError(f"cannot load JSON object {path}") from exc
    if not isinstance(value, dict):
        raise ContinuityError(f"{path}: expected one JSON object")
    return value


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def digest_object(value: Mapping[str, Any], digest_key: str) -> str:
    return hashlib.sha256(canonical_bytes({key: item for key, item in value.items() if key != digest_key})).hexdigest()


def validate(value: dict[str, Any], schema_name: str, label: str) -> None:
    schema = load_object(SCHEMAS / schema_name)
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "$"
        raise ContinuityError(f"{label} schema failure at {location}: {errors[0].message}")


def reject_target_material(value: object) -> None:
    if isinstance(value, dict):
        overlap = FORBIDDEN_KEYS.intersection(key.casefold().replace("-", "_") for key in value)
        if overlap:
            raise ContinuityError(f"target-bearing field entered activation continuity: {sorted(overlap)[0]}")
        for child in value.values():
            reject_target_material(child)
    elif isinstance(value, list):
        for child in value:
            reject_target_material(child)


def _unit_directives(content: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "[")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        rows.setdefault(key, []).append(value)
    return rows


def _one(directives: dict[str, list[str]], key: str) -> str:
    values = directives.get(key, [])
    if len(values) != 1:
        raise ContinuityError(f"generated unit does not have exactly one {key}")
    return values[0]


def check_identity_continuity(
    ledger: Mapping[str, Any],
    deployment: Mapping[str, Any],
    activation: Mapping[str, Any],
    unit: Mapping[str, Any],
) -> None:
    """Require every contract to describe the same participant boundary."""

    directives = _unit_directives(str(unit["unit"]["content"]))
    service = ledger["service_identity"]["name"]
    if deployment["identity"]["user"] != service or deployment["identity"]["group"] != service:
        raise ContinuityError("participant ledger and deployment service identity differ")
    if _one(directives, "User") != service or _one(directives, "Group") != service:
        raise ContinuityError("participant ledger and generated unit service identity differ")

    ledger_p1 = ledger["resources"]["p1_checkout"]["path"]
    if deployment["paths"]["p1_checkout"]["path"] != ledger_p1:
        raise ContinuityError("participant ledger and deployment P1 paths differ")
    if activation["p1"]["tree_path"] != ledger_p1:
        raise ContinuityError("participant ledger and activation P1 paths differ")
    if unit["p1_tree_sha256"] != activation["p1"]["tree_sha256"]:
        raise ContinuityError("generated unit does not bind the activation P1 tree")

    private_roots = ledger["resources"]["private_roots"]
    deployment_private_roots = {
        deployment["paths"]["private_state"]["path"],
        deployment["paths"]["private_cache"]["path"],
    }
    if set(private_roots) != deployment_private_roots:
        raise ContinuityError("participant ledger and deployment private roots differ")
    if deployment["paths"]["private_state"]["path"] not in private_roots:
        raise ContinuityError("deployment private state is outside the participant ledger")
    if _one(directives, "WorkingDirectory") not in private_roots:
        raise ContinuityError("generated unit working directory is outside the participant ledger")
    read_write = set(_one(directives, "ReadWritePaths").split())
    if deployment["paths"]["private_state"]["path"] not in read_write or deployment["paths"]["runtime"]["path"] not in read_write:
        raise ContinuityError("generated unit writable paths omit the deployment boundary")
    for writable in read_write:
        if writable not in private_roots and writable != deployment["paths"]["runtime"]["path"]:
            raise ContinuityError("generated unit has a writable path outside the participant ledger/deployment boundary")

    sockets = ledger["resources"]["control_sockets"]
    if not sockets or any(str(Path(path).parent) != deployment["paths"]["runtime"]["path"] for path in sockets):
        raise ContinuityError("participant control socket is outside the deployment runtime boundary")
    credentials = ledger["resources"]["credential_roots"]
    if credentials != [deployment["paths"]["credential_root"]["path"]]:
        raise ContinuityError("participant credential root is outside the deployment configuration boundary")


def check_request_interface_continuity(
    invocation: Mapping[str, Any],
    service_contract: Mapping[str, Any],
    activation: Mapping[str, Any],
    unit: Mapping[str, Any],
    *,
    require_operational: bool,
    workflow_bytes: bytes | None = None,
) -> dict[str, bool]:
    """Bind the workflow request URL/audience to the daemon and unit.

    Null PRE-P1 endpoint/prefix fields are reported as not ready.  They are not
    treated as contradictory values.  A future operational closure requires
    all four surfaces to be non-null and exact.
    """

    invocation_harness = invocation["controlled_harness"]
    service_transport = service_contract["transport"]
    service_oidc = service_contract["oidc"]
    activation_prefix = activation["oidc"].get("audience_prefix")
    prefixes = [
        invocation_harness.get("oidc_audience_prefix"),
        service_oidc.get("audience_prefix"),
        activation_prefix,
    ]
    observed_prefixes = [value for value in prefixes if value is not None]
    if any(value != CANONICAL_AUDIENCE_PREFIX for value in observed_prefixes):
        raise ContinuityError("OIDC audience prefix differs across activation surfaces")
    if require_operational and len(observed_prefixes) != len(prefixes):
        raise ContinuityError("OIDC audience prefix is still PRE-P1 null")

    endpoints = [
        invocation_harness.get("https_endpoint"),
        service_transport.get("https_endpoint"),
        activation["listener"]["https_endpoint"],
        unit["network_policy"]["listener"]["https_endpoint"],
    ]
    observed_endpoints = [value for value in endpoints if value is not None]
    for endpoint in observed_endpoints:
        parsed = urlsplit(endpoint)
        if parsed.scheme != "https" or parsed.path != CANONICAL_CHECKPOINT_PATH or parsed.query or parsed.fragment:
            raise ContinuityError("HTTPS checkpoint endpoint path differs across activation surfaces")
    if len(set(observed_endpoints)) > 1:
        raise ContinuityError("HTTPS checkpoint endpoints are not byte-identical")
    if require_operational and len(observed_endpoints) != len(endpoints):
        raise ContinuityError("HTTPS checkpoint endpoint is still PRE-P1 null")

    oidc = activation["oidc"]
    for key, service_key in (
        ("issuer", "issuer"), ("repository", "repository"), ("ref", "ref"),
        ("workflow_ref", "workflow_ref"), ("event_name", "event_name"),
        ("run_attempt", "run_attempt"),
    ):
        service_value = service_oidc.get(service_key)
        if service_value is not None and str(service_value) != str(oidc[key]):
            raise ContinuityError(f"OIDC {key} differs between service and activation")
        if require_operational and service_value is None:
            raise ContinuityError(f"OIDC {key} is still PRE-P1 null")
    if invocation_harness["request_signature_binding"] != "OIDC_AUDIENCE_SUFFIX_IS_SHA256_OF_CANONICAL_REQUEST_BYTES":
        raise ContinuityError("invocation request-to-audience binding differs")
    workflow_path = invocation.get("frozen", {}).get("workflow_path")
    workflow_ref = activation["oidc"]["workflow_ref"]
    expected_ref_suffix = f"/{workflow_path}@refs/heads/main" if isinstance(workflow_path, str) else None
    if expected_ref_suffix is None or not workflow_ref.endswith(expected_ref_suffix):
        raise ContinuityError("activation OIDC workflow ref differs from invocation workflow")
    if workflow_bytes is not None:
        try:
            workflow_text = workflow_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContinuityError("checkpoint workflow is not UTF-8") from exc
        for required in (
            'audience_prefix=$(jq -er \'.controlled_harness.oidc_audience_prefix\'',
            'audience="${audience_prefix}:${request_sha}"',
            'harness_url=$(jq -er \'.controlled_harness.https_endpoint\'',
        ):
            if required not in workflow_text:
                raise ContinuityError("workflow does not derive endpoint/audience from the invocation contract")
        frozen_sha = invocation.get("frozen", {}).get("workflow_sha256")
        if frozen_sha is not None and frozen_sha != hashlib.sha256(workflow_bytes).hexdigest():
            raise ContinuityError("workflow bytes differ from invocation digest")
        if require_operational and frozen_sha is None:
            raise ContinuityError("workflow digest is still PRE-P1 null")
    elif require_operational:
        raise ContinuityError("operational workflow bytes were not supplied")
    if unit["bound_acceptances"].get("oidc_config_sha256") != hashlib.sha256(canonical_bytes(activation["oidc"])).hexdigest():
        raise ContinuityError("generated unit does not bind the activation OIDC configuration")
    return {
        "audience_operationally_bound": len(observed_prefixes) == len(prefixes),
        "endpoint_operationally_bound": len(observed_endpoints) == len(endpoints),
        "workflow_operationally_bound": workflow_bytes is not None and invocation.get("frozen", {}).get("workflow_sha256") is not None,
    }


def verify_operational_closure(
    ledger: dict[str, Any],
    deployment: dict[str, Any],
    activation: dict[str, Any],
    unit: dict[str, Any],
    receipt: dict[str, Any],
    verification_key: bytes,
    expected_source_boundary_sha256: str,
    expected_service_epoch_binding_sha256: str,
    invocation: dict[str, Any],
    service_contract: dict[str, Any],
    workflow_bytes: bytes,
) -> dict[str, Any]:
    """Verify a future signed receipt against the exact unit input closure."""

    artifacts = (ledger, deployment, activation, unit, receipt, invocation, service_contract)
    for artifact in artifacts:
        reject_target_material(artifact)
    validate(ledger, "benchmark-participant-ledger-v1.5.schema.json", "participant ledger")
    validate(deployment, "benchmark-controlled-harness-deployment-contract-v1.5.schema.json", "deployment")
    validate(activation, "benchmark-operational-controlled-harness-activation-v1.5.schema.json", "activation inputs")
    validate(unit, "benchmark-operational-controlled-harness-unit-v1.5.schema.json", "generated unit")
    validate(receipt, "benchmark-operational-noninterference-receipt-v1.5.schema.json", "noninterference receipt")
    validate(service_contract, "benchmark-controlled-harness-service-contract-v1.5.schema.json", "service contract")
    if invocation.get("schema") != "c5k4-method-v1.5-checkpoint-invocation-contract-1.0":
        raise ContinuityError("checkpoint invocation contract schema differs")

    if ledger["ledger_sha256"] != noninterference.canonical_digest(ledger, "ledger_sha256"):
        raise ContinuityError("participant ledger self-digest mismatch")
    for value, key, label in (
        (activation, "activation_inputs_sha256", "activation inputs"),
        (unit, "bundle_sha256", "generated unit"),
        (activation["noninterference_key_commitment"], "commitment_sha256", "key commitment"),
        (activation["worm_acceptance"], "acceptance_sha256", "WORM acceptance"),
        (activation["destructive_gap_acceptance"], "acceptance_sha256", "destructive-gap acceptance"),
    ):
        if value[key] != digest_object(value, key):
            raise ContinuityError(f"{label} self-digest mismatch")

    check_identity_continuity(ledger, deployment, activation, unit)
    interface = check_request_interface_continuity(
        invocation, service_contract, activation, unit,
        require_operational=True, workflow_bytes=workflow_bytes,
    )
    if unit["activation_inputs_sha256"] != activation["activation_inputs_sha256"]:
        raise ContinuityError("generated unit is bound to different activation inputs")
    if unit["service_binary_sha256"] != activation["service"]["binary_sha256"]:
        raise ContinuityError("generated unit is bound to a different service binary")
    bindings = unit["bound_acceptances"]
    expected = {
        "noninterference_key_commitment_sha256": activation["noninterference_key_commitment"]["commitment_sha256"],
        "worm_acceptance_sha256": activation["worm_acceptance"]["acceptance_sha256"],
        "destructive_gap_acceptance_sha256": activation["destructive_gap_acceptance"]["acceptance_sha256"],
        "daemon_contract_sha256": activation["service"]["daemon_contract_sha256"],
    }
    for key, digest in expected.items():
        if bindings[key] != digest:
            raise ContinuityError(f"generated unit {key} mismatch")

    key_commitment = activation["noninterference_key_commitment"]
    if receipt["signing_key_id"] != key_commitment["signing_key_id"]:
        raise ContinuityError("receipt signing key ID differs from activation commitment")
    if receipt["verification_key_sha256"] != key_commitment["verification_key_sha256"]:
        raise ContinuityError("receipt verification key differs from activation commitment")
    if receipt["service_epoch_binding_sha256"] != expected_service_epoch_binding_sha256:
        raise ContinuityError("receipt is bound to another service epoch")
    try:
        verified = noninterference.verify_operational(
            ledger, expected_source_boundary_sha256, receipt, verification_key
        )
    except Exception as exc:
        raise ContinuityError("signed operational noninterference receipt rejected") from exc
    return {
        "valid": True,
        "status": "FUTURE_OPERATIONAL_ACTIVATION_CONTINUITY_VERIFIED",
        "activation_inputs_sha256": activation["activation_inputs_sha256"],
        "unit_bundle_sha256": unit["bundle_sha256"],
        "participant_ledger_sha256": ledger["ledger_sha256"],
        "noninterference_receipt_sha256": verified["noninterference_receipt_sha256"],
        "worm_acceptance_sha256": expected["worm_acceptance_sha256"],
        "destructive_gap_acceptance_sha256": expected["destructive_gap_acceptance_sha256"],
        "service_epoch_binding_sha256": expected_service_epoch_binding_sha256,
        "target_specific": False,
        "request_interface": interface,
    }


def verify_committed_pre_p1_continuity() -> None:
    """Static gate: committed contracts must align before live provisioning."""

    plan = infrastructure.load_object(infrastructure.PLAN)
    template = infrastructure.load_object(infrastructure.TEMPLATE)
    infrastructure.verify_plan(plan, infrastructure.TEMPLATE, template)
    infrastructure.verify_cloudformation(template)
    infrastructure.verify_target_blind(template, plan)

    ledger = load_object(PROTOCOL / "participant-ledger.json")
    deployment = load_object(PROTOCOL / "controlled-harness-deployment-contract.json")
    validate(ledger, "benchmark-participant-ledger-v1.5.schema.json", "participant ledger")
    validate(deployment, "benchmark-controlled-harness-deployment-contract-v1.5.schema.json", "deployment")
    # Use the frozen activation-schema constants and the deterministic generator
    # surface.  No operational input or target-bearing artifact exists PRE-P1.
    activation_schema = load_object(SCHEMAS / "benchmark-operational-controlled-harness-activation-v1.5.schema.json")
    unit_schema = load_object(SCHEMAS / "benchmark-operational-controlled-harness-unit-v1.5.schema.json")
    Draft7Validator.check_schema(activation_schema)
    Draft7Validator.check_schema(unit_schema)
    actual_audience_prefix = activation_schema["properties"]["oidc"]["properties"]["audience_prefix"].get("const")
    if actual_audience_prefix != CANONICAL_AUDIENCE_PREFIX:
        raise ContinuityError("operational activation schema freezes a different OIDC audience prefix")
    expected_endpoint_pattern = r"^https://[a-z0-9][a-z0-9.-]{0,252}:443/v1/checkpoint$"
    activation_endpoint_pattern = activation_schema["properties"]["listener"]["properties"]["https_endpoint"]["pattern"]
    unit_endpoint_pattern = unit_schema["properties"]["network_policy"]["properties"]["listener"]["properties"]["https_endpoint"]["pattern"]
    if activation_endpoint_pattern != expected_endpoint_pattern or unit_endpoint_pattern != expected_endpoint_pattern:
        raise ContinuityError("operational schemas freeze a different HTTPS checkpoint path")
    activation_shape = {"p1": {"tree_path": activation_schema["properties"]["p1"]["properties"]["tree_path"]["const"], "tree_sha256": "0" * 64}}
    unit_shape = {
        "p1_tree_sha256": "0" * 64,
        "unit": {"content": "\n".join([
            "[Service]", "User=c5k4-benchmark-v15", "Group=c5k4-benchmark-v15",
            "WorkingDirectory=/var/lib/c5k4-benchmark-v15",
            "ReadWritePaths=/var/lib/c5k4-benchmark-v15 /var/cache/c5k4-benchmark-v15 /run/c5k4-benchmark-v15",
        ])},
    }
    check_identity_continuity(ledger, deployment, activation_shape, unit_shape)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--audit-committed-pre-p1", action="store_true")
    try:
        args = parser.parse_args(argv)
        if not args.audit_committed_pre_p1:
            return 2
        verify_committed_pre_p1_continuity()
    except (ContinuityError, OSError, json.JSONDecodeError, infrastructure.InfrastructurePlanError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
