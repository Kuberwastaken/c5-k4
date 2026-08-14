#!/usr/bin/env python3
"""Authenticate Method v1.5 classifier execution before registry row access.

This verifier is target blind.  It authenticates a published P1 role-resolution
proof, the actual Python modules loaded by the future-cohort runtime, and a
previous target-free classifier readiness receipt.  It reruns synthetic
closure validation before returning.  Callers must invoke it before calling
``future.build`` or any function that reads a U1/U2 registry row.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v15_future_cohort as future  # noqa: E402
import validate_benchmark_v15_classifier_closure as closure  # noqa: E402


BINDING_SCHEMA = ROOT / "schemas/benchmark-classifier-runtime-binding-v1.5.schema.json"
ROLE_SCHEMA = ROOT / "schemas/benchmark-p1-role-resolution-v1.5.schema.json"
EXPECTED_COMPONENTS = {
    "five_strata_classifier": ("INHERITED_V1_4", "five_strata_classifier"),
    "syntax_pool_builder": ("INHERITED_V1_4", "syntax_pool_builder"),
    "classifier_closure_contract": ("NATIVE_V1_5", "classifier_closure_contract"),
    "classifier_closure_validator": ("NATIVE_V1_5", "classifier_closure_validator"),
    "classifier_closure_readiness_schema": ("NATIVE_V1_5", "classifier_closure_readiness_schema"),
    "classifier_runtime_binding_schema": ("NATIVE_V1_5", "classifier_runtime_binding_schema"),
    "classifier_runtime_verifier": ("NATIVE_V1_5", "classifier_runtime_verifier"),
}


class RuntimeBindingError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw: bytes, where: str) -> dict[str, Any]:
    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, child in rows:
            if key in result:
                raise RuntimeBindingError(f"{where} has duplicate key {key!r}")
            result[key] = child
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeBindingError(f"{where} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeBindingError(f"{where} must be one JSON object")
    return value


def _schema(path: Path) -> dict[str, Any]:
    return strict_json(path.read_bytes(), path.name)


def schema_validate(value: dict[str, Any], schema: dict[str, Any], where: str) -> None:
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise RuntimeBindingError(f"{where} schema failed: " + "; ".join(error.message for error in errors))


def normalized_component_path(value: Any) -> str:
    if not isinstance(value, str):
        raise RuntimeBindingError("component path is not a string")
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or path.as_posix() != value:
        raise RuntimeBindingError("component path is not normalized repo-relative")
    return value


def load_ref(ref: dict[str, Any], where: str, *, repo_relative: bool = False) -> tuple[Path, bytes]:
    path_text = ref.get("path")
    expected = ref.get("sha256")
    if not isinstance(path_text, str) or not isinstance(expected, str):
        raise RuntimeBindingError(f"{where} has no exact path/digest")
    if repo_relative:
        path = ROOT / normalized_component_path(path_text)
        try:
            path.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeBindingError(f"{where} resolves outside the protocol repository") from exc
    else:
        path = Path(path_text)
        if not path.is_absolute():
            path = ROOT / path
    try:
        if not path.is_file() or path.is_symlink():
            raise RuntimeBindingError(f"{where} is absent, non-regular, or symlinked")
        raw = path.read_bytes()
    except OSError as exc:
        raise RuntimeBindingError(f"cannot read {where}") from exc
    if sha256(raw) != expected:
        raise RuntimeBindingError(f"{where} byte digest mismatch")
    return path.resolve(), raw


def _role_index(resolution: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    supplied = resolution.get("resolution_sha256")
    unsigned = dict(resolution)
    unsigned.pop("resolution_sha256", None)
    if supplied != sha256(canonical_json(unsigned)):
        raise RuntimeBindingError("P1 role-resolution self-digest mismatch")
    rows = resolution.get("resolved_roles")
    if not isinstance(rows, list):
        raise RuntimeBindingError("P1 role resolution has no rows")
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeBindingError("P1 role row is malformed")
        key = (row.get("closure"), row.get("role"))
        if key in index:
            raise RuntimeBindingError("duplicate P1 role resolution")
        index[key] = row
    return index


def verify(binding_path: Path) -> dict[str, Any]:
    binding = strict_json(binding_path.read_bytes(), "classifier runtime binding")
    schema_validate(binding, _schema(BINDING_SCHEMA), "classifier runtime binding")
    if binding["target_data_access_permitted"] is not False or binding["future_registry_invocation_started"] is not False:
        raise RuntimeBindingError("classifier binding was not invoked before registry access")

    _, resolution_raw = load_ref(binding["p1_role_resolution"], "P1 role resolution")
    resolution = strict_json(resolution_raw, "P1 role resolution")
    schema_validate(resolution, _schema(ROLE_SCHEMA), "P1 role resolution")
    roles = _role_index(resolution)
    component_paths: dict[str, Path] = {}
    for name, expected_role in EXPECTED_COMPONENTS.items():
        bound = binding["components"][name]
        if (bound["closure"], bound["role"]) != expected_role:
            raise RuntimeBindingError(f"{name} binds the wrong closure/role")
        resolved = roles.get(expected_role)
        if resolved is None:
            raise RuntimeBindingError(f"P1 role resolution omits {expected_role}")
        if bound["path"] != resolved.get("path") or bound["sha256"] != resolved.get("sha256"):
            raise RuntimeBindingError(f"{name} differs from authenticated P1 role")
        path, _ = load_ref(bound, name, repo_relative=True)
        component_paths[name] = path

    consumed_classifier_path, consumed_classifier_raw = load_ref(
        binding["consumed_classifier"], "classifier consumed by future registry"
    )
    frozen_classifier_raw = component_paths["five_strata_classifier"].read_bytes()
    if (
        sha256(consumed_classifier_raw) != binding["components"]["five_strata_classifier"]["sha256"]
        or consumed_classifier_raw != frozen_classifier_raw
    ):
        raise RuntimeBindingError("classifier consumed by future registry is not the P1-authenticated classifier")

    actual_builder = Path(future.syntax.__file__).resolve()
    if actual_builder.suffix == ".pyc":
        actual_builder = actual_builder.with_suffix(".py")
    if actual_builder != component_paths["syntax_pool_builder"] or sha256(actual_builder.read_bytes()) != binding["components"]["syntax_pool_builder"]["sha256"]:
        raise RuntimeBindingError("executing future-cohort syntax_pool_builder bytes are not P1-authenticated")
    actual_validator = Path(closure.__file__).resolve()
    if actual_validator.suffix == ".pyc":
        actual_validator = actual_validator.with_suffix(".py")
    if actual_validator != component_paths["classifier_closure_validator"] or sha256(actual_validator.read_bytes()) != binding["components"]["classifier_closure_validator"]["sha256"]:
        raise RuntimeBindingError("executing classifier closure validator bytes are not P1-authenticated")
    actual_verifier = Path(__file__).resolve()
    if actual_verifier != component_paths["classifier_runtime_verifier"] or sha256(actual_verifier.read_bytes()) != binding["components"]["classifier_runtime_verifier"]["sha256"]:
        raise RuntimeBindingError("executing classifier runtime verifier bytes are not P1-authenticated")
    if BINDING_SCHEMA.resolve() != component_paths["classifier_runtime_binding_schema"] or sha256(BINDING_SCHEMA.read_bytes()) != binding["components"]["classifier_runtime_binding_schema"]["sha256"]:
        raise RuntimeBindingError("classifier runtime binding schema bytes are not P1-authenticated")

    _, readiness_raw = load_ref(binding["classifier_readiness_receipt"], "classifier readiness receipt")
    readiness = strict_json(readiness_raw, "classifier readiness receipt")
    readiness_schema = strict_json(component_paths["classifier_closure_readiness_schema"].read_bytes(), "classifier readiness schema")
    schema_validate(readiness, readiness_schema, "classifier readiness receipt")
    unsigned = dict(readiness)
    unsigned.pop("receipt_sha256", None)
    if readiness.get("receipt_sha256") != sha256(closure.canonical_json(unsigned)):
        raise RuntimeBindingError("classifier readiness receipt self-digest mismatch")

    # This target-free rerun is the final operation before the caller may read
    # a real registry row.  Exact receipt equality binds all executable bytes.
    try:
        replay = closure.validate(
            component_paths["classifier_closure_contract"],
            consumed_classifier_path,
            component_paths["syntax_pool_builder"],
        )
    except closure.ClassifierClosureError as exc:
        raise RuntimeBindingError("target-blind classifier closure replay failed") from exc
    if replay != readiness:
        raise RuntimeBindingError("classifier readiness receipt does not replay exactly")
    result = {
        "schema": "c5k4-method-v1.5-classifier-runtime-verification-1.0",
        "status": "CLASSIFIER_RUNTIME_AUTHENTICATED_BEFORE_REGISTRY",
        "target_data_read": False,
        "future_registry_invocation_started": False,
        "p1_role_resolution_sha256": resolution["resolution_sha256"],
        "classifier_readiness_receipt_sha256": readiness["receipt_sha256"],
        "classifier_sha256": binding["components"]["five_strata_classifier"]["sha256"],
        "executing_pool_builder_sha256": binding["components"]["syntax_pool_builder"]["sha256"],
        "executing_closure_validator_sha256": binding["components"]["classifier_closure_validator"]["sha256"],
    }
    result["verification_sha256"] = sha256(canonical_json(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify(args.binding.resolve())
    except (OSError, RuntimeBindingError) as exc:
        print(f"CLASSIFIER_RUNTIME_REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
