#!/usr/bin/env python3
"""Assemble and validate non-circular Method v1.2 P0A/P0T artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import jsonschema


ROOT = Path(__file__).parents[1].resolve()
SCHEMA = ROOT / "schemas/benchmark-v1.2-p0.schema.json"
SCHEMA_VERSION = "c5k4-method-v1.2-p0-1.0"
CONFIG_VERSION = "c5k4-method-v1.2-p0-components-1.0"
REQUIRED_COMPONENTS = (
    "protocol_document",
    "five_strata_classifier",
    "grouping_rule",
    "provenance_policy",
    "source_discovery_contract",
    "source_path_policy",
    "source_discovery_boundary",
    "upstream_ref_rule",
    "quotas",
    "registry_contact_input_schema",
    "registry_contact_output_schema",
    "protocol_manifest_schema",
    "benchmark_schema",
    "benchmark_linter",
    "registry_builder",
    "selector",
    "budget_rule",
    # P0 freezes how the three comparison arms are instantiated. Exact
    # target-specific contracts and grids remain post-C1/pre-execution.
    "arm_design_rule",
    "baseline_library",
    "development_prior",
    # Selection probabilities are frozen from registry metadata at C1.  Their
    # rule and five stratum priors are distinct from the post-C1 intervention
    # forecast rule and must therefore be independently content-addressed.
    "selection_forecast_rule",
    "selection_stratum_priors",
    "intervention_forecast_rule",
    "transformation_library",
    "scoring_rule",
    "stopping_rule",
    "target_data_audit_rule",
)
PROTOTYPE_SEGMENT = "v1.2-prototype"
JSON_CONTRACTS = {
    "five_strata_classifier": (
        "c5k4-five-strata-classifier-1.2",
        {"schema_version", "scope", "upstream", "permitted_inputs", "forbidden_inputs", "domain_signals", "finite_signal", "graph_scalar_signal", "declaration_rule", "cluster_rule", "output_policy"},
    ),
    "grouping_rule": (
        "c5k4-question-cluster-grouping-rule-1.2",
        {"schema_version", "unit", "input_scope", "statement_semantics_permitted", "rules_in_precedence_order", "ambiguity_policy", "manual_grouping_after_p0"},
    ),
    "provenance_policy": (
        "c5k4-provenance-policy-1.2",
        {"schema_version", "artifact_status", "unit_classes", "precedence", "semantic_roles", "unknown_roles", "machine_roles", "machine_source_kinds", "bounded_content_schemas", "machine_exemption_required_fields", "machine_exemption_required_true", "immutable_locator_prefixes", "identity_policy", "invariants"},
    ),
    "source_path_policy": (
        "c5k4-source-path-purpose-policy-1.2",
        {"schema_version", "description", "default", "required_session_mirror_ids", "required_release_snapshot_ids", "rules"},
    ),
    "source_discovery_boundary": (
        "c5k4-source-discovery-boundary-1.2",
        {"schema_version", "research_root", "required_semantic_source_classes", "semantic_scan_unit_policy", "dirty_research_worktree_policy", "source_drift_policy", "missing_source_policy", "unknown_path_policy", "discovery_reads_target_semantics", "post_s0_pre_c1_semantic_access", "post_c0_pre_c1_semantic_access"},
    ),
    "upstream_ref_rule": (
        "c5k4-upstream-ref-rule-1.2",
        {"schema_version", "repository", "subtree", "remote_ref", "resolution_event", "resolution_command", "required_object_format", "required_matches", "tree_rule", "retry_or_repin"},
    ),
    "quotas": (
        "c5k4-benchmark-quotas-1.2",
        {"schema_version", "sampling_unit", "selected_n", "quotas", "no_backfill"},
    ),
    "budget_rule": (
        "c5k4-benchmark-budget-rule-1.2",
        {"schema_version", "shared_analysis", "each_discovery_arm", "arms", "independent_verification", "no_adaptation", "no_cross_arm_sharing_before_all_terminate", "early_stop_after_crossing", "network_policy"},
    ),
    "arm_design_rule": (
        "c5k4-arm-design-rule-1.2",
        {"schema_version", "freeze_phase", "common_rules", "seed_rule", "arms", "protocol_invalid_conditions"},
    ),
    "baseline_library": (
        "c5k4-baseline-library-1.2",
        {"schema_version", "freeze_phase", "catalogue", "generic_operation_grammars", "canonical_schedule", "forbidden"},
    ),
    "development_prior": (
        "c5k4-development-prior-1.2",
        {"schema_version", "scope", "evidence_cutoff", "probability_increment", "exact_arithmetic", "outcome_order", "probabilities"},
    ),
    "selection_forecast_rule": (
        "c5k4-selection-forecast-rule-1.2",
        {"schema_version", "freeze_phase", "allowed_inputs", "forbidden_inputs", "rule", "probability_increment", "strictly_between_zero_and_one", "exact_sum", "all_selected_required"},
    ),
    "selection_stratum_priors": (
        "c5k4-selection-stratum-priors-1.2",
        {"schema_version", "evidence_cutoff", "probability_increment", "derivation", "priors"},
    ),
    "intervention_forecast_rule": (
        "c5k4-intervention-forecast-rule-1.2",
        {"schema_version", "freeze_phase", "probability_increment", "strictly_between_zero_and_one", "exact_sum", "manual_probability_adjustment", "all_selected_required", "profile_precedence", "profile_conditions", "profiles"},
    ),
    "transformation_library": (
        "c5k4-transformation-library-1.2",
        {"schema_version", "selection_rule", "forbidden_adaptation", "entries"},
    ),
    "scoring_rule": (
        "c5k4-scoring-rule-1.2",
        {"schema_version", "selected_n", "aggregate_denominator", "outcomes", "brier", "terminal_precedence", "theorem_yield", "arm_metrics", "support_thresholds", "reporting"},
    ),
    "stopping_rule": (
        "c5k4-stopping-rule-1.2",
        {"schema_version", "required_terminal_clusters", "early_stop_after_crossing", "new_solver_family_target_or_bound", "selected_cluster_replacement", "no_backfill", "no_quota_relaxation", "pre_c0_shortage", "zero_complete_requirement", "cross_requirements", "terminal_precedence", "protocol_invalid_precedence_note"},
    ),
    "target_data_audit_rule": (
        "c5k4-target-data-audit-rule-1.2",
        {"schema_version", "required_per_selected_cluster", "phase0_terminal_reasons", "semantic_review_starts_after", "selected_denominator", "selected_cluster_replacement", "audit_evidence_content_addressed"},
    ),
}
JSON_SCHEMA_ROLES = {
    "registry_contact_input_schema", "registry_contact_output_schema",
    "protocol_manifest_schema", "benchmark_schema",
}
FORBIDDEN_DATA_KEYS = {
    "clusters", "eligible_rows", "final_eligible_rows", "selected_rows",
    "selected_clusters", "statement", "statement_text", "declarations",
    "candidate", "candidates", "residual", "proof_route",
}
SCHEMA_CONTAINER_KEYS = {"properties", "definitions", "$defs", "patternProperties"}


class P0Error(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def repo_path(recorded: str) -> Path:
    pure = PurePosixPath(recorded)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise P0Error(f"artifact path must be a normalized repository-relative path: {recorded!r}")
    path = (ROOT / Path(*pure.parts)).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise P0Error(f"artifact escapes repository: {recorded!r}") from exc
    return path


def file_digest(value: Any, *, role: str, permit_prototype: bool = False) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise P0Error(f"{role} must contain exactly path and sha256")
    path_text, expected = value["path"], value["sha256"]
    if not isinstance(path_text, str) or not isinstance(expected, str):
        raise P0Error(f"{role} path and sha256 must be strings")
    path = repo_path(path_text)
    if not path.is_file():
        raise P0Error(f"{role} artifact does not exist: {path_text}")
    actual = sha256_file(path)
    if expected != actual:
        raise P0Error(f"{role} SHA-256 mismatch: expected {expected}, found {actual}")
    if not permit_prototype and PROTOTYPE_SEGMENT in PurePosixPath(path_text).parts:
        raise P0Error(f"authoritative component {role} points into PRE_P0 prototype area")
    return {"path": path_text, "sha256": actual}


def _nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def scan_for_target_data(value: Any, *, role: str, trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        inside_schema_definition = any(part in SCHEMA_CONTAINER_KEYS for part in trail)
        for key, child in value.items():
            child_trail = (*trail, str(key))
            if str(key).casefold() in FORBIDDEN_DATA_KEYS and _nonempty(child) and not inside_schema_definition:
                raise P0Error(f"{role} contains nonempty forbidden target-data field {'.'.join(child_trail)}")
            scan_for_target_data(child, role=role, trail=child_trail)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_for_target_data(child, role=role, trail=(*trail, str(index)))


def audit_json_component(role: str, path: Path) -> None:
    if path.suffix.casefold() != ".json":
        if role in JSON_CONTRACTS or role in JSON_SCHEMA_ROLES:
            raise P0Error(f"{role} must be a JSON component")
        return
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P0Error(f"{role} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise P0Error(f"{role} JSON component must be an object")
    if role in JSON_CONTRACTS:
        version, allowed_keys = JSON_CONTRACTS[role]
        if value.get("schema_version") != version:
            raise P0Error(f"{role} schema_version must be {version!r}")
        if set(value) != allowed_keys:
            raise P0Error(
                f"{role} top-level keys differ: missing={sorted(allowed_keys-set(value))}, "
                f"extra={sorted(set(value)-allowed_keys)}"
            )
    elif role in JSON_SCHEMA_ROLES:
        if "$schema" not in value or value.get("type") not in {"object", None}:
            raise P0Error(f"{role} is not a recognizable JSON Schema object")
        try:
            jsonschema.Draft7Validator.check_schema(value)
        except jsonschema.SchemaError as exc:
            raise P0Error(f"{role} is not a valid Draft-07-compatible schema: {exc.message}") from exc
    scan_for_target_data(value, role=role)


def generate_audit_receipt(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("schema_version") != CONFIG_VERSION or config.get("authority") != "AUTHORITATIVE_P0":
        raise P0Error("audit generation requires an AUTHORITATIVE_P0 component config")
    components = config.get("components")
    if not isinstance(components, dict) or set(components) != set(REQUIRED_COMPONENTS):
        observed = set(components) if isinstance(components, dict) else set()
        required = set(REQUIRED_COMPONENTS)
        raise P0Error(f"component roles differ: missing={sorted(required-observed)}, extra={sorted(observed-required)}")
    rows = []
    for role in REQUIRED_COMPONENTS:
        ref = file_digest(components[role], role=role)
        audit_json_component(role, repo_path(ref["path"]))
        rows.append({
            "role": role,
            "path": ref["path"],
            "sha256": ref["sha256"],
            "classification": "PROTOCOL_ONLY_NO_TARGET_DATA",
        })
    return {
        "schema_version": "c5k4-method-v1.2-target-data-audit-receipt-1.0",
        "audit_rule_sha256": components["target_data_audit_rule"]["sha256"],
        "components": rows,
        "final_eligible_rows_detected": 0,
        "selected_clusters_detected": 0,
        "statement_text_detected": 0,
        "semantic_target_analysis_detected": 0,
    }


def explicit_ref(path_text: str, *, role: str, permit_prototype: bool = False) -> dict[str, str]:
    path = repo_path(path_text)
    if not path.is_file():
        raise P0Error(f"{role} artifact does not exist: {path_text}")
    if not permit_prototype and PROTOTYPE_SEGMENT in PurePosixPath(path_text).parts:
        raise P0Error(f"authoritative component {role} points into PRE_P0 prototype area")
    return {"path": path_text, "sha256": sha256_file(path)}


def materialize_config(
    component_assignments: list[str], producer_assignments: list[str], prototypes: list[str]
) -> dict[str, Any]:
    components: dict[str, dict[str, str]] = {}
    for assignment in component_assignments:
        if "=" not in assignment:
            raise P0Error(f"component assignment must be ROLE=PATH: {assignment!r}")
        role, path_text = assignment.split("=", 1)
        if role not in REQUIRED_COMPONENTS:
            raise P0Error(f"unknown component role: {role!r}")
        if role in components:
            raise P0Error(f"duplicate component role: {role}")
        components[role] = explicit_ref(path_text, role=role)
    observed, required = set(components), set(REQUIRED_COMPONENTS)
    if observed != required:
        raise P0Error(f"component roles differ: missing={sorted(required-observed)}, extra={sorted(observed-required)}")

    producers = []
    producer_ids: set[str] = set()
    for assignment in producer_assignments:
        fields = assignment.split(",")
        if len(fields) != 5:
            raise P0Error("producer assignment must be ID,EXECUTABLE,CONTRACT,INPUT_SCHEMA,OUTPUT_SCHEMA")
        producer_id, executable, contract, input_schema, output_schema = fields
        if not producer_id or producer_id in producer_ids:
            raise P0Error(f"empty or duplicate producer ID: {producer_id!r}")
        producer_ids.add(producer_id)
        producers.append({
            "producer_id": producer_id,
            "executable": explicit_ref(executable, role=f"producer {producer_id} executable"),
            "invocation_contract": explicit_ref(contract, role=f"producer {producer_id} contract"),
            "input_schema": explicit_ref(input_schema, role=f"producer {producer_id} input schema"),
            "output_schema": explicit_ref(output_schema, role=f"producer {producer_id} output schema"),
        })
    if not producers:
        raise P0Error("at least one explicit producer assignment is required")
    prototype_rows = []
    for path_text in prototypes:
        ref = explicit_ref(path_text, role="prototype", permit_prototype=True)
        prototype_rows.append({
            **ref, "authority": "PRE_P0_NOT_FREEZE", "excluded_from_formal_build": True
        })
    return {
        "schema_version": CONFIG_VERSION,
        "authority": "AUTHORITATIVE_P0",
        "components": components,
        "allowlisted_registry_producers": producers,
        "prototype_artifacts": prototype_rows,
        "target_data_audit_receipt": None,
    }


def _schema_validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in errors
        )
        raise P0Error(f"P0 schema validation failed: {detail}")


def iter_refs(p0a: dict[str, Any]) -> Iterable[tuple[str, dict[str, str]]]:
    for role, ref in p0a["components"].items():
        yield f"components.{role}", ref
    for index, producer in enumerate(p0a["allowlisted_registry_producers"]):
        for field in ("executable", "invocation_contract", "input_schema", "output_schema"):
            yield f"allowlisted_registry_producers.{index}.{field}", producer[field]
    for index, prototype in enumerate(p0a["prototype_artifacts"]):
        yield f"prototype_artifacts.{index}", prototype
    yield "target_data_audit_receipt", p0a["target_data_audit_receipt"]


def validate_audit_receipt(receipt_ref: dict[str, str], components: dict[str, Any]) -> None:
    ref = file_digest(receipt_ref, role="target_data_audit_receipt")
    try:
        receipt = json.loads(repo_path(ref["path"]).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise P0Error(f"target data audit receipt is not valid UTF-8 JSON: {exc}") from exc
    expected_keys = {
        "schema_version", "audit_rule_sha256", "components", "final_eligible_rows_detected",
        "selected_clusters_detected", "statement_text_detected", "semantic_target_analysis_detected",
    }
    if not isinstance(receipt, dict) or set(receipt) != expected_keys:
        raise P0Error("target data audit receipt has invalid shape")
    if receipt["schema_version"] != "c5k4-method-v1.2-target-data-audit-receipt-1.0":
        raise P0Error("unsupported target data audit receipt schema")
    audit_sha = components["target_data_audit_rule"]["sha256"]
    if receipt["audit_rule_sha256"] != audit_sha:
        raise P0Error("target data audit receipt does not bind the frozen audit rule")
    expected_rows = [
        {
            "role": role,
            "path": components[role]["path"],
            "sha256": components[role]["sha256"],
            "classification": "PROTOCOL_ONLY_NO_TARGET_DATA",
        }
        for role in REQUIRED_COMPONENTS
    ]
    if receipt["components"] != expected_rows:
        raise P0Error("target data audit receipt does not exactly cover frozen components")
    for role in REQUIRED_COMPONENTS:
        audit_json_component(role, repo_path(components[role]["path"]))
    for field in (
        "final_eligible_rows_detected", "selected_clusters_detected",
        "statement_text_detected", "semantic_target_analysis_detected",
    ):
        if receipt[field] != 0:
            raise P0Error(f"target data audit failed: {field}={receipt[field]!r}")


def validate_p0a(p0a: dict[str, Any]) -> None:
    _schema_validate(p0a)
    if p0a.get("artifact_kind") != "P0A":
        raise P0Error("expected a P0A artifact")
    observed = set(p0a["components"])
    required = set(REQUIRED_COMPONENTS)
    if observed != required:
        raise P0Error(f"component roles differ: missing={sorted(required-observed)}, extra={sorted(observed-required)}")
    producer_ids = [row["producer_id"] for row in p0a["allowlisted_registry_producers"]]
    if len(producer_ids) != len(set(producer_ids)):
        raise P0Error("producer_id values must be unique")
    for location, ref in iter_refs(p0a):
        prototype = location.startswith("prototype_artifacts.")
        expected_keys = {"path", "sha256", "authority", "excluded_from_formal_build"} if prototype else (
            {"path", "sha256", "content_class"} if location.startswith("components.") else {"path", "sha256"}
        )
        if set(ref) != expected_keys:
            raise P0Error(f"unexpected fields in {location}")
        plain = {"path": ref["path"], "sha256": ref["sha256"]}
        file_digest(plain, role=location, permit_prototype=prototype)
    validate_audit_receipt(p0a["target_data_audit_receipt"], p0a["components"])
    if any((p0a["final_eligible_rows"], p0a["selected_clusters"], p0a["target_semantics"])):
        raise P0Error("P0A contains forbidden final rows, selection, or target semantics")


def assemble_p0a(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != CONFIG_VERSION:
        raise P0Error(f"unsupported component config schema: {config.get('schema_version')!r}")
    if config.get("authority") != "AUTHORITATIVE_P0":
        raise P0Error("component config is PRE_P0_NOT_FREEZE and cannot assemble authoritative P0A")
    components = config.get("components")
    if not isinstance(components, dict):
        raise P0Error("components must be an object")
    observed, required = set(components), set(REQUIRED_COMPONENTS)
    if observed != required:
        raise P0Error(f"component roles differ: missing={sorted(required-observed)}, extra={sorted(observed-required)}")
    frozen_components = {}
    for role in REQUIRED_COMPONENTS:
        ref = file_digest(components[role], role=role)
        frozen_components[role] = {**ref, "content_class": "PROTOCOL_ONLY_NO_TARGET_DATA"}

    producers = []
    for index, producer in enumerate(config.get("allowlisted_registry_producers", [])):
        if not isinstance(producer, dict) or set(producer) != {
            "producer_id", "executable", "invocation_contract", "input_schema", "output_schema"
        }:
            raise P0Error(f"allowlisted_registry_producers[{index}] has invalid shape")
        frozen = {"producer_id": producer["producer_id"]}
        for field in ("executable", "invocation_contract", "input_schema", "output_schema"):
            frozen[field] = file_digest(producer[field], role=f"producer {index} {field}")
        producers.append(frozen)
    if not producers:
        raise P0Error("at least one allowlisted registry producer is required")

    prototypes = []
    for index, prototype in enumerate(config.get("prototype_artifacts", [])):
        if not isinstance(prototype, dict):
            raise P0Error(f"prototype_artifacts[{index}] must be an object")
        plain = {"path": prototype.get("path"), "sha256": prototype.get("sha256")}
        ref = file_digest(plain, role=f"prototype {index}", permit_prototype=True)
        prototypes.append({
            **ref,
            "authority": "PRE_P0_NOT_FREEZE",
            "excluded_from_formal_build": True,
        })

    receipt = file_digest(
        config.get("target_data_audit_receipt"), role="target_data_audit_receipt"
    )
    validate_audit_receipt(receipt, frozen_components)

    p0a = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "P0A",
        "authority": "AUTHORITATIVE_P0",
        "protocol_version": "1.2",
        "components": frozen_components,
        "allowlisted_registry_producers": producers,
        "prototype_artifacts": prototypes,
        "target_data_audit_receipt": receipt,
        "registry_build": {
            "allowed_build_count": 1,
            "requires_p0t": True,
            "entropy_permitted": False,
            "upstream_resolution_component": "upstream_ref_rule",
        },
        "prohibitions": {
            "final_eligible_pool": True,
            "selection": True,
            "target_ranking": True,
            "statement_text": True,
            "semantic_target_analysis": True,
        },
        "final_eligible_rows": [],
        "selected_clusters": [],
        "target_semantics": [],
    }
    validate_p0a(p0a)
    return p0a


def _parse_timestamp(value: str) -> None:
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise P0Error(f"invalid UTC publication timestamp: {value!r}") from exc
    if not value.endswith("Z") or parsed.utcoffset().total_seconds() != 0:
        raise P0Error("publication timestamp must be UTC and end in Z")


def commit_file(commit: str, path: str) -> bytes:
    try:
        resolved = git("rev-parse", commit).decode().strip()
    except subprocess.CalledProcessError as exc:
        raise P0Error(f"P0A commit is not present locally: {commit}") from exc
    if resolved.lower() != commit.lower():
        raise P0Error("P0A commit must be an exact object ID, not a ref or abbreviation")
    try:
        return git("show", f"{commit}:{path}")
    except subprocess.CalledProcessError as exc:
        raise P0Error(f"P0A path {path!r} is absent from commit {commit}") from exc


def assemble_p0t(p0a_path: Path, p0a_commit: str, published: str, p0t_path: str) -> dict[str, Any]:
    p0a = json.loads(p0a_path.read_text(encoding="utf-8"))
    validate_p0a(p0a)
    relative = p0a_path.resolve().relative_to(ROOT).as_posix()
    raw = p0a_path.read_bytes()
    if commit_file(p0a_commit, relative) != raw:
        raise P0Error("committed P0A bytes differ from the attested P0A file")
    _parse_timestamp(published)
    p0t = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "P0T",
        "protocol_version": "1.2",
        "p0a": {"path": relative, "sha256": sha256_bytes(raw)},
        "p0a_commit": p0a_commit.lower(),
        "p0a_published_at_utc": published,
        "attestation_policy": {
            "p0a_ancestor_required": True,
            "p0a_bytes_immutable": True,
            "allowed_p0t_changed_paths": [p0t_path],
        },
    }
    _schema_validate(p0t)
    return p0t


def validate_p0t(p0t: dict[str, Any], *, p0t_commit: str | None = None, artifact_path: Path | None = None) -> None:
    _schema_validate(p0t)
    if p0t.get("artifact_kind") != "P0T":
        raise P0Error("expected a P0T artifact")
    _parse_timestamp(p0t["p0a_published_at_utc"])
    p0a_ref = p0t["p0a"]
    repo_path(p0a_ref["path"])
    allowed_paths = p0t["attestation_policy"]["allowed_p0t_changed_paths"]
    for allowed_path in allowed_paths:
        repo_path(allowed_path)
    p0a_raw = commit_file(p0t["p0a_commit"], p0a_ref["path"])
    if sha256_bytes(p0a_raw) != p0a_ref["sha256"]:
        raise P0Error("P0T digest does not authenticate committed P0A bytes")
    p0a = json.loads(p0a_raw)
    validate_p0a(p0a)
    if p0t_commit is None:
        return
    resolved = git("rev-parse", p0t_commit).decode().strip()
    if resolved.lower() != p0t_commit.lower():
        raise P0Error("P0T commit must be an exact object ID")
    parent = git("rev-parse", f"{p0t_commit}^").decode().strip()
    if parent != p0t["p0a_commit"]:
        raise P0Error("P0T commit must have the exact P0A commit as its sole first parent")
    parents = git("show", "-s", "--format=%P", p0t_commit).decode().split()
    if len(parents) != 1:
        raise P0Error("P0T must be a non-merge attestation commit")
    changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", p0t_commit).decode().splitlines()
    allowed = allowed_paths
    if changed != allowed:
        raise P0Error(f"P0T changed paths {changed}, expected exactly {allowed}")
    if artifact_path is not None:
        relative = artifact_path.resolve().relative_to(ROOT).as_posix()
        if relative != allowed[0] or commit_file(p0t_commit, relative) != artifact_path.read_bytes():
            raise P0Error("committed P0T bytes/path differ from validated attestation")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_a = sub.add_parser("assemble-p0a")
    build_a.add_argument("--components", type=Path, required=True)
    build_a.add_argument("--output", type=Path, required=True)
    build_t = sub.add_parser("assemble-p0t")
    build_t.add_argument("--p0a", type=Path, required=True)
    build_t.add_argument("--p0a-commit", required=True)
    build_t.add_argument("--published-at-utc", required=True)
    build_t.add_argument("--p0t-path", required=True)
    build_t.add_argument("--output", type=Path, required=True)
    audit = sub.add_parser("audit-receipt")
    audit.add_argument("--components", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument(
        "--update-components",
        action="store_true",
        help="content-address the new receipt into the explicit component config",
    )
    materialize = sub.add_parser("materialize-config")
    materialize.add_argument("--component", action="append", default=[], metavar="ROLE=PATH")
    materialize.add_argument(
        "--producer", action="append", default=[],
        metavar="ID,EXECUTABLE,CONTRACT,INPUT_SCHEMA,OUTPUT_SCHEMA",
    )
    materialize.add_argument("--prototype", action="append", default=[])
    materialize.add_argument("--output", type=Path, required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--artifact", type=Path, required=True)
    validate.add_argument("--p0t-commit")
    args = parser.parse_args()
    try:
        if args.command == "assemble-p0a":
            write_json(args.output, assemble_p0a(args.components.resolve()))
        elif args.command == "assemble-p0t":
            value = assemble_p0t(args.p0a.resolve(), args.p0a_commit, args.published_at_utc, args.p0t_path)
            if args.output.resolve().relative_to(ROOT).as_posix() != args.p0t_path:
                raise P0Error("--output must equal the repository-relative --p0t-path")
            write_json(args.output, value)
        elif args.command == "audit-receipt":
            config = json.loads(args.components.read_text(encoding="utf-8"))
            receipt = generate_audit_receipt(config)
            write_json(args.output, receipt)
            if args.update_components:
                config["target_data_audit_receipt"] = {
                    "path": args.output.resolve().relative_to(ROOT).as_posix(),
                    "sha256": sha256_file(args.output),
                }
                write_json(args.components, config)
        elif args.command == "materialize-config":
            write_json(
                args.output,
                materialize_config(args.component, args.producer, args.prototype),
            )
        else:
            value = json.loads(args.artifact.read_text(encoding="utf-8"))
            if value.get("artifact_kind") == "P0A":
                if args.p0t_commit:
                    raise P0Error("--p0t-commit is valid only for P0T")
                validate_p0a(value)
            elif value.get("artifact_kind") == "P0T":
                validate_p0t(value, p0t_commit=args.p0t_commit, artifact_path=args.artifact)
            else:
                raise P0Error("artifact_kind must be P0A or P0T")
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError, P0Error, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
