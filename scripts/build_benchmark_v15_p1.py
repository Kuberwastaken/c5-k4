#!/usr/bin/env python3
"""Assemble and validate the non-circular Method v1.5 P1A/P1T freeze.

P1A binds every native v1.5 executable-protocol component and derives the
unchanged scientific components directly from a fully validated Method v1.4
P0A.  P1T is a separate, one-path commit attesting the already committed P1A.
This module never reads target statements and performs no network operation.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import jsonschema


ROOT = Path(__file__).parents[1].resolve()
SCHEMA = ROOT / "schemas/benchmark-p1-v1.5.schema.json"
P1R_SCHEMA = ROOT / "schemas/benchmark-p1r-v1.5.schema.json"
READINESS_PACKAGE_SCHEMA_PATH = ROOT / "schemas/benchmark-candidate-base-readiness-package-v1.5.schema.json"
SCHEMA_VERSION = "c5k4-method-v1.5-p1-1.0"
CONFIG_VERSION = "c5k4-method-v1.5-p1-components-1.0"
NATIVE_CONTENT_CLASS = "V1_5_PROTOCOL_ONLY_NO_TARGET_DATA"
INHERITED_CONTENT_CLASS = "INHERITED_V1_4_EXACT"
SOURCE_CONTENT_CLASS = "PROTOCOL_ONLY_NO_TARGET_DATA"

# This is deliberately a closed map.  P1 cannot be assembled while a
# production component is absent, and an unreviewed extra cannot silently join
# the freeze.  Tests are not executable protocol components except for the
# checkpoint workflow contract test, which is itself the offline validator for
# that security boundary.
NATIVE_COMPONENTS = (
    "protocol_document",
    "p1_builder",
    "p1_schema",
    "chronology_rule",
    "chronology_builder",
    "future_cohort_rule",
    "future_cohort_builder",
    "provenance_ontology",
    "provenance_classifier",
    "git_provenance_partitioner",
    "source_boundary",
    "participant_ledger",
    "participant_ledger_schema",
    "noninterference_receipt",
    "noninterference_receipt_schema",
    "operational_noninterference_receipt_schema",
    "noninterference_key_commitment",
    "noninterference_key_commitment_schema",
    "operational_noninterference_key_commitment_schema",
    "participant_noninterference_verifier",
    "participant_noninterference_contract_test",
    "source_path_policy",
    "source_boundary_contract_test",
    "source_snapshot_builder",
    "source_snapshot_schema",
    "provenance_ledger_schema",
    "vendor_base_builder",
    "vendor_base_schema",
    "generated_registry_verifier",
    "generation_proof_schema",
    "future_registry_input_schema",
    "future_registry_output_schema",
    "identity_hits_builder",
    "private_identity_hits_schema",
    "provenance_content_pack_schema",
    "checkpoint_component_manifest",
    "checkpoint_component_manifest_schema",
    "checkpoint_runner",
    "checkpoint_runner_contract_test",
    "checkpoint_publication_manifest_schema",
    "checkpoint_runner_private_input_schema",
    "terminal_chronology_gap_certificate_schema",
    "public_checkpoint_chain_verifier",
    "public_checkpoint_chain_proof_schema",
    "private_custody_verifier",
    "private_custody_verifier_contract_test",
    "private_custody_batch_schema",
    "private_custody_coverage_certificate_schema",
    "public_custody_sealed_binding_schema",
    "delivery_broker",
    "delivery_broker_contract_test",
    "controlled_delivery_service_boundary",
    "controlled_delivery_service_acceptance_tests",
    "delivery_broker_config_schema",
    "delivery_broker_state_schema",
    "delivery_broker_receipt_schema",
    "delivery_broker_readiness_schema",
    "s3_object_lock_store",
    "s3_object_lock_store_contract_test",
    "s3_object_lock_store_config_schema",
    "s3_object_lock_store_readiness_schema",
    "s3_delivery_broker_adapter",
    "s3_delivery_broker_adapter_contract_test",
    "private_s3_object_reference_schema",
    "arm_capability_matrix",
    "arm_capability_matrix_schema",
    "arm_execution_envelope_schema",
    "arm_execution_envelope_validator",
    "arm_execution_envelope_contract_test",
    "runner_private_input_assembler",
    "runner_private_input_assembler_contract_test",
    "runner_private_input_assembly_schema",
    "private_artifact_locator_schema",
    "operational_private_custody_evidence_schema",
    "broker_custody_compiler",
    "broker_custody_compiler_contract_test",
    "private_worm_object_inventory_schema",
    "private_broker_service_epoch_schema",
    "private_custody_compiler_output_schema",
    "arm_triplet_launcher",
    "arm_triplet_launcher_contract_test",
    "arm_triplet_claim_schema",
    "arm_triplet_combined_record_schema",
    "triplet_isolation_backend",
    "triplet_isolation_backend_contract_test",
    "triplet_isolation_plan_schema",
    "triplet_isolation_acceptance_schema",
    "triplet_isolation_readiness_schema",
    "checkpoint_capture_orchestrator",
    "checkpoint_capture_orchestrator_contract_test",
    "checkpoint_capture_plan_schema",
    "checkpoint_capture_readiness_schema",
    "p1_role_resolver",
    "p1_role_resolver_contract_test",
    "p1_role_resolution_schema",
    "p1_role_resolution_readiness_schema",
    "linux_isolation_acceptance",
    "linux_isolation_acceptance_contract_test",
    "controlled_harness_service_contract",
    "controlled_harness_service_contract_schema",
    "target_blind_checkpoint_request_schema",
    "controlled_harness_response_schema",
    "controlled_harness_service",
    "controlled_harness_service_contract_test",
    "triplet_production_adapter",
    "triplet_production_adapter_contract_test",
    "production_isolation_attestation_schema",
    "production_triplet_acceptance_certificate_schema",
    "five_strata_classifier_contract",
    "five_strata_classifier_contract_schema",
    "five_strata_classifier_readiness_schema",
    "classifier_readiness_receipt",
    "five_strata_classifier_closure_validator",
    "five_strata_classifier_closure_contract_test",
    "immutable_infrastructure_plan",
    "immutable_infrastructure_cloudformation",
    "immutable_infrastructure_verifier",
    "immutable_infrastructure_contract_test",
    "immutable_live_acceptance_evidence_schema",
    "immutable_live_acceptance_verifier",
    "immutable_live_acceptance_contract_test",
    "operational_controlled_harness_activation_schema",
    "operational_controlled_harness_unit_schema",
    "operational_harness_unit_generator",
    "operational_harness_unit_generator_contract_test",
    "controlled_harness_deployment_contract",
    "controlled_harness_deployment_contract_schema",
    "controlled_harness_deployment_verifier",
    "controlled_harness_deployment_contract_test",
    "controlled_harness_systemd_unit",
    "controlled_harness_sysusers_asset",
    "controlled_harness_tmpfiles_asset",
    "controlled_harness_network_policy",
    "controlled_harness_destructive_gap_plan",
    "controlled_harness_activation_continuity_verifier",
    "controlled_harness_activation_continuity_contract_test",
    "controlled_harness_https_daemon_contract",
    "controlled_harness_https_daemon_contract_schema",
    "controlled_harness_https_daemon",
    "controlled_harness_https_daemon_contract_test",
    "classifier_runtime_binding_schema",
    "classifier_runtime_verifier",
    "scheduled_aggregate_certificate_builder",
    "scheduled_aggregate_certificate_schema",
    "scheduled_replay_attestation_schema",
    "scheduled_checkpoint_workflow",
    "checkpoint_invocation_contract",
    "checkpoint_workflow_contract_test",
    "candidate_base_validator",
    "candidate_base_validator_contract_test",
    "public_readiness_authority_root_schema",
    "candidate_base_operational_evidence_schema",
    "candidate_base_independent_recompile_schema",
    "candidate_base_readiness_package_schema",
    "candidate_base_validation_input_schema",
    "candidate_base_validation_output_schema",
    "p1r_schema",
    "public_p1r_activation_receipt_schema",
    "isolated_evidence_runner",
    "isolated_evidence_runner_schema",
    "isolated_evidence_runner_contract",
    "isolated_evidence_runner_test",
    "candidate_base_readiness_spec",
    "candidate_base_readiness_spec_schema",
    "candidate_base_readiness_spec_contract_test",
    "candidate_base_validator_independent_audit",
    "candidate_base_validator_independent_audit_schema",
    "candidate_base_validator_independent_audit_contract_test",
    "operational_authority_gap",
    "operational_authority_gap_schema",
    "operational_authority_gap_contract_test",
    "pass_pool_builder",
    "pass_pool_schema",
    "pass_pool_builder_contract_test",
    "c0_publication_contract",
    "c0_publication_contract_schema",
    "c0_publication_contract_test",
    "c0_v15_builder",
    "c0_v15_schema",
    "c0_v15_builder_contract_test",
    "infrastructure_activation_workflow",
    "infrastructure_activation_workflow_contract_test",
    "candidate_base_security_schema_contract_test",
    "public_p1r_verifier",
    "public_p1r_verifier_contract_test",
    "p1t_publication_observer_workflow",
    "p1t_publication_observer_workflow_contract_test",
    "p1t_publication_observer_validator",
    "p1t_publication_observer_validator_contract_test",
    "p1r_publication_observer_workflow",
    "p1r_publication_observer_workflow_contract_test",
    "p1r_publication_observer_validator",
    "p1r_publication_observer_validator_contract_test",
    "c0_observer_workflow",
    "c0_observer_workflow_contract_test",
    "c0_publication_verifier",
    "c0_publication_verifier_contract_test",
    "c0_publication_observation_schema",
    "c0_pass_pool_replay_input_schema",
)

# Security-critical C0 roles are path-frozen as well as digest-frozen.  This
# prevents a caller from satisfying the closed role names with an alternate
# verifier, schema, workflow, or test at P1 assembly time.
EXACT_NATIVE_PATHS = {
    "c0_v15_builder": "scripts/build_benchmark_v15_c0.py",
    "c0_v15_schema": "schemas/benchmark-v1.5-c0.schema.json",
    "c0_v15_builder_contract_test": "scripts/test_build_benchmark_v15_c0.py",
    "c0_observer_workflow": ".github/workflows/method-v15-c0a-publication-observer.yml",
    "c0_observer_workflow_contract_test": "scripts/test_verify_benchmark_v15_c0_publication.py",
    "c0_publication_verifier": "scripts/verify_benchmark_v15_c0_publication.py",
    "c0_publication_verifier_contract_test": "scripts/test_verify_benchmark_v15_c0_publication.py",
    "c0_publication_observation_schema": "schemas/benchmark-c0-publication-observation-v1.5.schema.json",
    "c0_pass_pool_replay_input_schema": "schemas/benchmark-c0-pass-pool-replay-input-v1.5.schema.json",
}

# The assembler selects these records from the authenticated P0A.  A caller
# cannot supply, replace, or hand-copy their digests.  These are the scientific
# arm, budget, forecast, scoring, stopping, selection, execution, and entropy
# components that v1.5 states are unchanged.
INHERITED_V1_4_ROLES = (
    "arm_design_rule",
    "budget_rule",
    "baseline_library",
    "transformation_library",
    "development_prior",
    "selection_forecast_rule",
    "selection_stratum_priors",
    "intervention_forecast_rule",
    "scoring_rule",
    "stopping_rule",
    "target_data_audit_rule",
    "five_strata_classifier",
    "grouping_rule",
    "syntax_pool_builder",
    "quotas",
    "selector",
    "c0_builder",
    "scorer",
    "benchmark_linter",
    "benchmark_schema",
    "frozen_job_runner",
    "run_contract_schema",
    "drand_fetcher",
    "drand_package_manifest",
    "drand_package_lock",
)

FORBIDDEN_DATA_KEYS = {
    "clusters", "eligible_rows", "final_eligible_rows", "selected_rows",
    "selected_clusters", "candidate_identities", "statement", "statement_text",
    "declarations", "candidates", "target_rankings", "target_semantics",
    "residual", "proof_route", "outcomes", "target_identity", "target_identities",
}
SCHEMA_CONTAINER_KEYS = {"properties", "definitions", "$defs", "patternProperties"}
STRUCTURAL_STATEMENT_ROLES = {"immutable_infrastructure_cloudformation"}
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
HEX_GIT_OID = re.compile(r"[0-9a-f]{40}")
READINESS_PACKAGE_SCHEMA = "c5k4-method-v1.5-candidate-base-readiness-package-1.0"
READINESS_PACKAGE_DOMAIN = "c5k4-method-v1.5-candidate-base-readiness-package-1.0"
P1R_PATH = "results/benchmark/v1.5-protocol/P1R.json"


class P1Error(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def domain_digest(domain: str, value: Any) -> str:
    return sha256_bytes(domain.encode("ascii") + b"\x00" + canonical_json(value))


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise P1Error(f"duplicate JSON key in candidate readiness binding: {key!r}")
        result[key] = value
    return result


def validate_candidate_readiness_package(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise P1Error("candidate readiness package must be an object")
    try:
        schema = json.loads(READINESS_PACKAGE_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P1Error(f"candidate readiness package schema is unavailable: {exc}") from exc
    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        detail = "; ".join(f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in errors)
        raise P1Error(f"candidate readiness package schema validation failed: {detail}")
    unsigned = dict(value)
    recorded = unsigned.pop("package_sha256")
    if recorded != domain_digest(READINESS_PACKAGE_DOMAIN, unsigned):
        raise P1Error("candidate readiness package self-digest mismatch")
    return value


def load_candidate_readiness_package(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P1Error(f"candidate readiness package is not strict UTF-8 JSON: {exc}") from exc
    return validate_candidate_readiness_package(value)


def embed_candidate_readiness_package(value: dict[str, Any]) -> dict[str, Any]:
    canonical = canonical_json(value)
    return {
        "schema": "c5k4-method-v1.5-p1-embedded-readiness-package-1.0",
        "status": "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R",
        "encoding": "BASE64_CANONICAL_JSON_UTF8",
        "canonical_package_base64": base64.b64encode(canonical).decode("ascii"),
        "package_sha256": sha256_bytes(canonical),
        "assembler_verification_scope": "STRUCTURAL_CANONICAL_PACKAGE_ONLY_CRYPTO_UNVERIFIED_AWAITING_PUBLIC_P1R",
        "activation_authority": False,
    }


def validate_embedded_candidate_readiness(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"schema", "status", "encoding", "canonical_package_base64", "package_sha256", "assembler_verification_scope", "activation_authority"}:
        raise P1Error("embedded candidate readiness package has invalid closed shape")
    if (
        value["schema"] != "c5k4-method-v1.5-p1-embedded-readiness-package-1.0"
        or value["status"] != "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R"
        or value["encoding"] != "BASE64_CANONICAL_JSON_UTF8"
        or value["assembler_verification_scope"] != "STRUCTURAL_CANONICAL_PACKAGE_ONLY_CRYPTO_UNVERIFIED_AWAITING_PUBLIC_P1R"
        or value["activation_authority"] is not False
    ):
        raise P1Error("embedded candidate readiness package has invalid authority")
    try:
        raw = base64.b64decode(value["canonical_package_base64"], validate=True)
    except ValueError as exc:
        raise P1Error("embedded candidate readiness package is not canonical base64") from exc
    if sha256_bytes(raw) != value["package_sha256"]:
        raise P1Error("embedded candidate readiness package byte digest mismatch")
    package = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_pairs)
    validate_candidate_readiness_package(package)
    if raw != canonical_json(package):
        raise P1Error("embedded candidate readiness package bytes are not canonical JSON")
    return package


def repo_path(recorded: str) -> Path:
    if not isinstance(recorded, str):
        raise P1Error("artifact path must be a string")
    pure = PurePosixPath(recorded)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.as_posix() != recorded:
        raise P1Error(f"artifact path must be normalized and repository-relative: {recorded!r}")
    resolved = (ROOT / Path(*pure.parts)).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise P1Error(f"artifact path escapes repository: {recorded!r}") from exc
    return resolved


def repo_relative(path: Path, *, role: str) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise P1Error(f"{role} must be inside the repository") from exc


def file_digest(value: Any, *, role: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise P1Error(f"{role} must contain exactly path and sha256")
    expected_path = EXACT_NATIVE_PATHS.get(role)
    if expected_path is not None and value.get("path") != expected_path:
        raise P1Error(f"{role} must use exact tracked path {expected_path!r}")
    path = repo_path(value["path"])
    expected = value["sha256"]
    if not isinstance(expected, str) or HEX_SHA256.fullmatch(expected) is None:
        raise P1Error(f"{role} SHA-256 must be exact lowercase hexadecimal")
    if not path.is_file():
        raise P1Error(f"{role} artifact does not exist: {value['path']}")
    actual = sha256_file(path)
    if actual != expected:
        raise P1Error(f"{role} SHA-256 mismatch: expected {expected}, found {actual}")
    return {"path": value["path"], "sha256": actual}


def _nonempty(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, (str, list, tuple, dict, set)):
        return bool(value)
    return True


def scan_for_target_data(
    value: Any,
    *,
    role: str,
    trail: tuple[str, ...] = (),
    allow_structural_statement: bool = False,
) -> None:
    """Reject populated target-data containers, except JSON-Schema definitions."""
    if isinstance(value, dict):
        inside_schema = any(part in SCHEMA_CONTAINER_KEYS for part in trail)
        for key, child in value.items():
            next_trail = (*trail, str(key))
            folded_key = str(key).casefold()
            structural_statement = allow_structural_statement and folded_key == "statement"
            if folded_key in FORBIDDEN_DATA_KEYS and _nonempty(child) and not inside_schema and not structural_statement:
                raise P1Error(f"{role} contains nonempty forbidden target-data field {'.'.join(next_trail)}")
            scan_for_target_data(
                child,
                role=role,
                trail=next_trail,
                allow_structural_statement=allow_structural_statement,
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_for_target_data(
                child,
                role=role,
                trail=(*trail, str(index)),
                allow_structural_statement=allow_structural_statement,
            )


def audit_native_component(role: str, ref: dict[str, str]) -> None:
    path = repo_path(ref["path"])
    if path.suffix.casefold() != ".json":
        return
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P1Error(f"{role} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise P1Error(f"{role} JSON component must be an object")
    if role.endswith("_schema") or role == "p1_schema":
        try:
            jsonschema.Draft7Validator.check_schema(value)
        except jsonschema.SchemaError as exc:
            raise P1Error(f"{role} is not a valid Draft-07-compatible schema: {exc.message}") from exc
    scan_for_target_data(
        value,
        role=role,
        allow_structural_statement=role in STRUCTURAL_STATEMENT_ROLES,
    )


def _load_v14_module() -> Any:
    script = ROOT / "scripts/build_benchmark_v14_p0.py"
    spec = importlib.util.spec_from_file_location("benchmark_v14_p0_for_v15", script)
    if spec is None or spec.loader is None:
        raise P1Error("cannot load the v1.4 P0 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _p0t_binding(source_p0a: dict[str, str]) -> tuple[dict[str, str], str]:
    p0t_path = ROOT / "results/benchmark/v1.4-p0/P0T.json"
    p0t_ref = {"path": p0t_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(p0t_path)}
    try:
        p0t = json.loads(p0t_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P1Error(f"v1.4 P0T is invalid: {exc}") from exc
    if (
        p0t.get("artifact_kind") != "P0T"
        or p0t.get("protocol_version") != "1.4"
        or p0t.get("p0a") != source_p0a
        or not isinstance(p0t.get("p0a_commit"), str)
        or re.fullmatch(r"[0-9a-f]{40,64}", p0t["p0a_commit"]) is None
    ):
        raise P1Error("v1.4 P0T does not authenticate the selected P0A")
    if commit_file(p0t["p0a_commit"], source_p0a["path"]) != repo_path(source_p0a["path"]).read_bytes():
        raise P1Error("working v1.4 P0A differs from its attested commit bytes")
    return p0t_ref, p0t["p0a_commit"]


def derive_v14_closure(source_ref: dict[str, str]) -> tuple[dict[str, str], dict[str, str], str, dict[str, Any]]:
    source = file_digest(source_ref, role="v1.4 source P0A")
    p0t_ref, source_commit = _p0t_binding(source)
    try:
        p0a = json.loads(repo_path(source["path"]).read_text(encoding="utf-8"))
        # Validate the closed P0A structure.  Component bytes are authenticated
        # below from the exact attested P0A commit, not from a later worktree in
        # which operational files may legitimately have evolved.
        v14 = _load_v14_module()
        v14._schema_validate(p0a)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P1Error(f"v1.4 source P0A is invalid JSON: {exc}") from exc
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise P1Error(f"v1.4 source P0A does not validate: {exc}") from exc
    if p0a.get("schema_version") != "c5k4-method-v1.4-p0-1.0" or p0a.get("artifact_kind") != "P0A":
        raise P1Error("inheritance source must be an authoritative Method v1.4 P0A")
    if any(p0a.get(field) for field in ("final_eligible_rows", "selected_clusters", "target_semantics")):
        raise P1Error("v1.4 inheritance source contains forbidden target data")
    # Close over every reference in the P0A at its attested commit.  This is
    # intentionally stronger than checking only the roles reused by v1.5.
    for location, record in v14.iter_refs(p0a):
        if not isinstance(record, dict):
            raise P1Error(f"v1.4 reference {location} has an invalid shape")
        path, expected = record.get("path"), record.get("sha256")
        if not isinstance(path, str) or not isinstance(expected, str) or HEX_SHA256.fullmatch(expected) is None:
            raise P1Error(f"v1.4 reference {location} has an invalid binding")
        repo_path(path)
        actual = sha256_bytes(commit_file(source_commit, path))
        if actual != expected:
            raise P1Error(
                f"v1.4 reference {location} commit-byte digest mismatch: expected {expected}, found {actual}"
            )
    receipt_ref = p0a.get("target_data_audit_receipt", {})
    receipt = json.loads(commit_file(source_commit, receipt_ref["path"]))
    expected_rows = [
        {
            "role": role,
            "path": p0a["components"][role]["path"],
            "sha256": p0a["components"][role]["sha256"],
            "classification": SOURCE_CONTENT_CLASS,
        }
        for role in v14.REQUIRED_COMPONENTS
    ]
    if (
        receipt.get("audit_rule_sha256") != p0a["components"]["target_data_audit_rule"]["sha256"]
        or receipt.get("components") != expected_rows
        or any(receipt.get(field) != 0 for field in (
            "final_eligible_rows_detected", "selected_clusters_detected",
            "statement_text_detected", "semantic_target_analysis_detected",
        ))
    ):
        raise P1Error("v1.4 target-data audit receipt is not the exact zero-detection closure")
    components = p0a.get("components", {})
    missing = set(INHERITED_V1_4_ROLES) - set(components)
    if missing:
        raise P1Error(f"v1.4 inheritance source lacks required roles: {sorted(missing)}")
    closure: dict[str, Any] = {}
    for role in INHERITED_V1_4_ROLES:
        source_component = components[role]
        if source_component.get("content_class") != SOURCE_CONTENT_CLASS:
            raise P1Error(f"v1.4 role {role} has an unexpected content class")
        path = source_component.get("path")
        expected_sha = source_component.get("sha256")
        if not isinstance(path, str) or not isinstance(expected_sha, str):
            raise P1Error(f"v1.4 role {role} has an invalid digest binding")
        repo_path(path)
        raw = commit_file(source_commit, path)
        actual_sha = sha256_bytes(raw)
        if actual_sha != expected_sha:
            raise P1Error(
                f"inherited v1.4 {role} commit-byte digest mismatch: expected {expected_sha}, found {actual_sha}"
            )
        ref = {"path": path, "sha256": actual_sha}
        closure[role] = {
            **ref,
            "source_commit": source_commit,
            "content_class": INHERITED_CONTENT_CLASS,
            "source_content_class": SOURCE_CONTENT_CLASS,
        }
    return source, p0t_ref, source_commit, closure


def audit_binding(native: dict[str, Any], inherited: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for role in NATIVE_COMPONENTS:
        rows.append({"scope": "V1_5_NATIVE", "role": role, **native[role]})
    for role in INHERITED_V1_4_ROLES:
        rows.append({"scope": "V1_4_INHERITED", "role": role, **inherited[role]})
    return {
        "algorithm": "STRICT_ROLE_MAP_DIGEST_AND_STRUCTURAL_TARGET_DATA_AUDIT_V1_5",
        "native_component_count": len(NATIVE_COMPONENTS),
        "inherited_component_count": len(INHERITED_V1_4_ROLES),
        "audited_bindings_sha256": sha256_bytes(canonical_json(rows)),
        "candidate_identities_detected": 0,
        "statement_text_detected": 0,
        "target_rankings_detected": 0,
        "target_semantic_analysis_detected": 0,
    }


def _schema_validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in errors
        )
        raise P1Error(f"P1 schema validation failed: {detail}")


def assemble_p1a(config_path: Path, readiness_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) != {"schema_version", "authority", "components", "v1_4_p0a"}:
        raise P1Error("P1 component config has an invalid shape")
    if config.get("schema_version") != CONFIG_VERSION or config.get("authority") != "AUTHORITATIVE_P1":
        raise P1Error("component config is not an authoritative Method v1.5 P1 config")
    components = config.get("components")
    if not isinstance(components, dict) or set(components) != set(NATIVE_COMPONENTS):
        observed = set(components) if isinstance(components, dict) else set()
        required = set(NATIVE_COMPONENTS)
        raise P1Error(f"native component roles differ: missing={sorted(required-observed)}, extra={sorted(observed-required)}")
    native: dict[str, Any] = {}
    for role in NATIVE_COMPONENTS:
        ref = file_digest(components[role], role=role)
        audit_native_component(role, ref)
        native[role] = {**ref, "content_class": NATIVE_CONTENT_CLASS}
    source_p0a, source_p0t, source_commit, inherited = derive_v14_closure(config["v1_4_p0a"])
    candidate_readiness = embed_candidate_readiness_package(load_candidate_readiness_package(readiness_path))
    p1a = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "P1A",
        "authority": "AUTHORITATIVE_P1",
        "protocol_version": "1.5",
        "components": native,
        "inherited_v1_4": {
            "source_p0a": source_p0a,
            "source_p0t": source_p0t,
            "source_p0a_commit": source_commit,
            "source_protocol_version": "1.4",
            "selected_roles": list(INHERITED_V1_4_ROLES),
            "components": inherited,
            "closure_policy": {
                "source_p0a_must_validate": True,
                "roles_selected_by_assembler": True,
                "manual_digest_copy_forbidden": True,
                "all_selected_files_revalidated": True,
            },
        },
        "candidate_base_readiness": candidate_readiness,
        "target_data_audit": audit_binding(native, inherited),
        "chronology_capture": {
            "allowed_u1_capture_count": 1,
            "requires_public_p1r_receipt": True,
            "p1t_alone_activation_permitted": False,
            "entropy_permitted": False,
            "selection_permitted": False,
        },
        "prohibitions": {
            "candidate_identities": True,
            "statement_text": True,
            "target_ranking": True,
            "target_semantic_analysis": True,
            "entropy": True,
            "selection": True,
        },
        "candidate_identities": [],
        "statement_text": [],
        "target_rankings": [],
        "target_semantics": [],
    }
    validate_p1a(p1a)
    return p1a


def validate_p1a(p1a: dict[str, Any]) -> None:
    _schema_validate(p1a)
    if p1a.get("artifact_kind") != "P1A":
        raise P1Error("expected P1A")
    native = p1a["components"]
    if set(native) != set(NATIVE_COMPONENTS):
        raise P1Error("P1A native component map is not the frozen closed role map")
    for role in NATIVE_COMPONENTS:
        row = native[role]
        if row.get("content_class") != NATIVE_CONTENT_CLASS:
            raise P1Error(f"native role {role} has the wrong content class")
        ref = file_digest({"path": row["path"], "sha256": row["sha256"]}, role=role)
        audit_native_component(role, ref)
    inheritance = p1a["inherited_v1_4"]
    validate_embedded_candidate_readiness(p1a["candidate_base_readiness"])
    if inheritance["selected_roles"] != list(INHERITED_V1_4_ROLES):
        raise P1Error("P1A inherited role order or closure differs from the frozen selection")
    source, p0t, source_commit, expected = derive_v14_closure(inheritance["source_p0a"])
    if (
        source != inheritance["source_p0a"]
        or p0t != inheritance["source_p0t"]
        or source_commit != inheritance["source_p0a_commit"]
        or inheritance["components"] != expected
    ):
        raise P1Error("P1A inheritance was not derived exactly from the validated v1.4 P0A")
    if p1a["target_data_audit"] != audit_binding(native, expected):
        raise P1Error("P1A target-data audit does not authenticate the exact component closure")
    if any(p1a[field] for field in ("candidate_identities", "statement_text", "target_rankings", "target_semantics")):
        raise P1Error("P1A contains forbidden target data")


def git(*args: str) -> bytes:
    return subprocess.run(
        ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(ROOT), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C"},
    ).stdout


def commit_file(commit: str, path: str) -> bytes:
    if not isinstance(commit, str) or HEX_GIT_OID.fullmatch(commit) is None:
        raise P1Error("commit must be an exact lowercase object ID")
    try:
        resolved = git("rev-parse", commit).decode().strip()
        if resolved != commit:
            raise P1Error("commit resolved through a ref or abbreviation")
        return git("show", f"{commit}:{path}")
    except subprocess.CalledProcessError as exc:
        raise P1Error(f"committed path {path!r} is unavailable at {commit}") from exc


def parse_timestamp(value: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise P1Error("publication timestamp must be UTC and end in Z")
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise P1Error(f"invalid publication timestamp: {value!r}") from exc
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise P1Error("publication timestamp must be UTC")


def assemble_p1t(p1a_path: Path, p1a_commit: str, published: str, p1t_path: str) -> dict[str, Any]:
    p1a = json.loads(p1a_path.read_text(encoding="utf-8"))
    validate_p1a(p1a)
    relative = repo_relative(p1a_path, role="P1A artifact")
    raw = p1a_path.read_bytes()
    if commit_file(p1a_commit, relative) != raw:
        raise P1Error("committed P1A bytes differ from the attested P1A file")
    parse_timestamp(published)
    repo_path(p1t_path)
    p1t = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "P1T",
        "protocol_version": "1.5",
        "p1a": {"path": relative, "sha256": sha256_bytes(raw)},
        "p1a_commit": p1a_commit,
        "p1a_published_at_utc": published,
        "attestation_policy": {
            "p1a_ancestor_required": True,
            "p1a_bytes_immutable": True,
            "allowed_p1t_changed_paths": [p1t_path],
        },
    }
    _schema_validate(p1t)
    return p1t


def validate_p1t(p1t: dict[str, Any], *, p1t_commit: str | None = None, artifact_path: Path | None = None) -> None:
    _schema_validate(p1t)
    if p1t.get("artifact_kind") != "P1T":
        raise P1Error("expected P1T")
    parse_timestamp(p1t["p1a_published_at_utc"])
    allowed = p1t["attestation_policy"]["allowed_p1t_changed_paths"]
    if len(allowed) != 1:
        raise P1Error("P1T must allow exactly one changed path")
    repo_path(allowed[0])
    p1a_raw = commit_file(p1t["p1a_commit"], p1t["p1a"]["path"])
    if sha256_bytes(p1a_raw) != p1t["p1a"]["sha256"]:
        raise P1Error("P1T digest does not authenticate committed P1A bytes")
    validate_p1a(json.loads(p1a_raw))
    if p1t_commit is None:
        return
    resolved = git("rev-parse", p1t_commit).decode().strip()
    if resolved != p1t_commit:
        raise P1Error("P1T commit must be an exact object ID")
    parents = git("show", "-s", "--format=%P", p1t_commit).decode().split()
    if parents != [p1t["p1a_commit"]]:
        raise P1Error("P1T must be a non-merge commit whose sole parent is exact P1A")
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", p1t_commit).decode().splitlines()
    if changed != allowed:
        raise P1Error(f"P1T changed paths {changed}, expected exactly {allowed}")
    if artifact_path is not None:
        relative = repo_relative(artifact_path, role="P1T artifact")
        if relative != allowed[0] or commit_file(p1t_commit, relative) != artifact_path.read_bytes():
            raise P1Error("committed P1T bytes/path differ from validated attestation")


def _p1r_schema_validate(value: dict[str, Any]) -> None:
    schema = json.loads(P1R_SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in errors)
        raise P1Error(f"P1R schema validation failed: {detail}")


def assemble_p1r(p1t_path: Path, p1t_commit: str, observation_path: Path) -> dict[str, Any]:
    p1t = json.loads(p1t_path.read_text(encoding="utf-8"), object_pairs_hook=_strict_pairs)
    validate_p1t(p1t)
    relative = repo_relative(p1t_path, role="P1T artifact")
    if relative != "results/benchmark/v1.5-protocol/P1T.json":
        raise P1Error("P1R requires the canonical P1T path")
    raw = p1t_path.read_bytes()
    if commit_file(p1t_commit, relative) != raw:
        raise P1Error("committed P1T bytes differ from P1R observation source")
    try:
        observation = json.loads(observation_path.read_text(encoding="utf-8"), object_pairs_hook=_strict_pairs)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P1Error(f"P1R public observation is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(observation, dict) or observation.get("p1t", {}).get("commit") != p1t_commit:
        raise P1Error("P1R observation does not bind exact P1T commit")
    p1r = {
        "schema_version": "c5k4-method-v1.5-p1r-1.0",
        "artifact_kind": "P1R",
        "status": "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY",
        "protocol_version": "1.5",
        "p1t": {"path": relative, "sha256": sha256_bytes(raw)},
        "p1t_commit": p1t_commit,
        "observation": observation,
        "activation_policy": {
            "structural_draft_only": True,
            "p1r_is_activation_boundary": False,
            "p1t_alone_is_activation_boundary": False,
            "full_exact_c_replay_required": True,
            "p1r_parent_must_be_exact_p1t": True,
            "allowed_p1r_changed_paths": [P1R_PATH],
            "public_p1r_ref_required": True,
        },
    }
    _p1r_schema_validate(p1r)
    return p1r


def validate_p1r(p1r: dict[str, Any], *, p1r_commit: str | None = None, artifact_path: Path | None = None) -> None:
    _p1r_schema_validate(p1r)
    p1t_raw = commit_file(p1r["p1t_commit"], p1r["p1t"]["path"])
    if sha256_bytes(p1t_raw) != p1r["p1t"]["sha256"]:
        raise P1Error("P1R does not authenticate exact committed P1T bytes")
    validate_p1t(json.loads(p1t_raw), p1t_commit=p1r["p1t_commit"])
    if p1r["observation"]["p1t"]["commit"] != p1r["p1t_commit"]:
        raise P1Error("P1R public observation differs from exact P1T")
    if p1r_commit is None:
        return
    resolved = git("rev-parse", p1r_commit).decode().strip()
    if resolved != p1r_commit:
        raise P1Error("P1R commit must be an exact object ID")
    parents = git("show", "-s", "--format=%P", p1r_commit).decode().split()
    if parents != [p1r["p1t_commit"]]:
        raise P1Error("P1R must be a non-merge commit whose sole parent is exact P1T")
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", p1r_commit).decode().splitlines()
    if changed != [P1R_PATH]:
        raise P1Error(f"P1R changed paths {changed}, expected exactly {[P1R_PATH]}")
    if artifact_path is not None:
        relative = repo_relative(artifact_path, role="P1R artifact")
        if relative != P1R_PATH or commit_file(p1r_commit, relative) != artifact_path.read_bytes():
            raise P1Error("committed P1R bytes/path differ from validated observation receipt")


def explicit_ref(path_text: str, *, role: str) -> dict[str, str]:
    path = repo_path(path_text)
    if not path.is_file():
        raise P1Error(f"{role} artifact does not exist: {path_text}")
    return {"path": path_text, "sha256": sha256_file(path)}


def materialize_config(assignments: Iterable[str], v1_4_p0a: str) -> dict[str, Any]:
    components: dict[str, Any] = {}
    for assignment in assignments:
        if "=" not in assignment:
            raise P1Error(f"component assignment must be ROLE=PATH: {assignment!r}")
        role, path_text = assignment.split("=", 1)
        if role not in NATIVE_COMPONENTS or role in components:
            raise P1Error(f"unknown or duplicate native component role: {role!r}")
        components[role] = explicit_ref(path_text, role=role)
    if set(components) != set(NATIVE_COMPONENTS):
        raise P1Error(f"component assignments must exactly cover {list(NATIVE_COMPONENTS)}")
    return {
        "schema_version": CONFIG_VERSION,
        "authority": "AUTHORITATIVE_P1",
        "components": components,
        "v1_4_p0a": explicit_ref(v1_4_p0a, role="v1.4 P0A"),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    config = sub.add_parser("materialize-config")
    config.add_argument("--component", action="append", default=[], metavar="ROLE=PATH")
    config.add_argument("--v1-4-p0a", required=True)
    config.add_argument("--output", type=Path, required=True)
    p1a = sub.add_parser("assemble-p1a")
    p1a.add_argument("--components", type=Path, required=True)
    p1a.add_argument("--candidate-readiness", type=Path, required=True)
    p1a.add_argument("--output", type=Path, required=True)
    p1t = sub.add_parser("assemble-p1t")
    p1t.add_argument("--p1a", type=Path, required=True)
    p1t.add_argument("--p1a-commit", required=True)
    p1t.add_argument("--published-at-utc", required=True)
    p1t.add_argument("--p1t-path", required=True)
    p1t.add_argument("--output", type=Path, required=True)
    p1r = sub.add_parser("assemble-p1r")
    p1r.add_argument("--p1t", type=Path, required=True)
    p1r.add_argument("--p1t-commit", required=True)
    p1r.add_argument("--observation", type=Path, required=True)
    p1r.add_argument("--output", type=Path, required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--artifact", type=Path, required=True)
    validate.add_argument("--p1t-commit")
    validate.add_argument("--p1r-commit")
    args = parser.parse_args()
    try:
        if args.command == "materialize-config":
            write_json(args.output, materialize_config(args.component, args.v1_4_p0a))
        elif args.command == "assemble-p1a":
            write_json(args.output, assemble_p1a(args.components.resolve(), args.candidate_readiness.resolve()))
        elif args.command == "assemble-p1t":
            if args.output.resolve().relative_to(ROOT).as_posix() != args.p1t_path:
                raise P1Error("--output must equal repository-relative --p1t-path")
            write_json(args.output, assemble_p1t(args.p1a.resolve(), args.p1a_commit, args.published_at_utc, args.p1t_path))
        elif args.command == "assemble-p1r":
            if args.output.resolve().relative_to(ROOT).as_posix() != P1R_PATH:
                raise P1Error(f"--output must equal {P1R_PATH}")
            write_json(args.output, assemble_p1r(args.p1t.resolve(), args.p1t_commit, args.observation.resolve()))
        else:
            value = json.loads(args.artifact.read_text(encoding="utf-8"))
            if value.get("artifact_kind") == "P1A":
                if args.p1t_commit or args.p1r_commit:
                    raise P1Error("commit validation options are invalid for P1A")
                validate_p1a(value)
            elif value.get("artifact_kind") == "P1T":
                if args.p1r_commit:
                    raise P1Error("--p1r-commit is valid only for P1R")
                validate_p1t(value, p1t_commit=args.p1t_commit, artifact_path=args.artifact)
            elif value.get("artifact_kind") == "P1R":
                if args.p1t_commit:
                    raise P1Error("--p1t-commit is valid only for P1T")
                validate_p1r(value, p1r_commit=args.p1r_commit, artifact_path=args.artifact)
            else:
                raise P1Error("artifact_kind must be P1A, P1T, or P1R")
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError, P1Error, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
