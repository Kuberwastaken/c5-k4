#!/usr/bin/env python3
"""Inert, fail-closed production boundary for Method v1.5 checkpoints.

This runner never acquires network evidence.  CAPTURE mode accepts only a
separately produced, content-addressed private input manifest.  Until P1,
source custody, and the capture adapter are frozen operationally it emits no
files and no diagnostics.  TERMINAL_CHRONOLOGY_GAP can eventually emit the
three bounded public files without reading private inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft7Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark_v15_aggregate_certificate as aggregate  # noqa: E402
import build_benchmark_v15_chronology as chronology  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA = "c5k4-method-v1.5-checkpoint-invocation-contract-1.0"
MANIFEST_SCHEMA = "c5k4-method-v1.5-checkpoint-publication-manifest-1.0"
PRIVATE_INPUT_SCHEMA = "c5k4-method-v1.5-checkpoint-runner-private-input-1.0"
GAP_SCHEMA = "c5k4-method-v1.5-terminal-chronology-gap-certificate-1.0"
PUBLIC_FILES = ("publication-manifest.json", "quota-certificate.json", "receipt.json")
FORBIDDEN_KEYS = {
    "cluster_id", "declarations", "records", "statement", "statement_text",
    "target_identity", "target_identities", "candidate_identities", "outcomes",
    "ranking", "rankings", "logs", "stdout", "stderr",
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
OID_RE = re.compile(r"^[0-9a-f]{40}$")


class RunnerError(ValueError):
    """A public-boundary condition failed; intentionally safe to suppress."""


class SilentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise RunnerError(message)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def content_digest(value: dict[str, Any], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return hashlib.sha256(canonical_json(unsigned)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RunnerError(f"invalid {label}") from exc
    if not isinstance(value, dict):
        raise RunnerError(f"invalid {label}")
    return value


def load_schema(name: str) -> dict[str, Any]:
    return load_json(ROOT / "schemas" / name, "schema")


def validate_schema(value: dict[str, Any], name: str, label: str) -> None:
    try:
        Draft7Validator(load_schema(name), format_checker=FormatChecker()).validate(value)
    except Exception as exc:
        raise RunnerError(f"{label} fails its frozen schema") from exc


def repo_file(recorded: Any, label: str) -> Path:
    if not isinstance(recorded, str):
        raise RunnerError(f"invalid {label} path")
    pure = PurePosixPath(recorded)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.as_posix() != recorded:
        raise RunnerError(f"invalid {label} path")
    path = (ROOT / Path(*pure.parts)).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise RunnerError(f"invalid {label} path") from exc
    if not path.is_file():
        raise RunnerError(f"missing {label}")
    return path


def exact_file(ref: dict[str, Any], label: str, *, private: bool = False) -> Path:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise RunnerError(f"invalid {label} binding")
    path_value, expected = ref["path"], ref["sha256"]
    if not isinstance(expected, str) or SHA_RE.fullmatch(expected) is None:
        raise RunnerError(f"invalid {label} digest")
    if private:
        if not isinstance(path_value, str) or not Path(path_value).is_absolute():
            raise RunnerError(f"invalid {label} path")
        path = Path(path_value).resolve()
        if not path.is_file():
            raise RunnerError(f"missing {label}")
    else:
        path = repo_file(path_value, label)
    if sha256_file(path) != expected:
        raise RunnerError(f"{label} digest mismatch")
    return path


def assert_no_public_secrets(value: Any) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_KEYS.intersection(key.casefold() for key in value):
            raise RunnerError("public artifact contains a forbidden field")
        for child in value.values():
            assert_no_public_secrets(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_public_secrets(child)


def validate_contract(path: Path, event_name: str, run_attempt: int) -> dict[str, Any]:
    contract = load_json(path, "invocation contract")
    if contract.get("schema") != CONTRACT_SCHEMA:
        raise RunnerError("unsupported invocation contract")
    if contract.get("status") != "FROZEN_P1_EXECUTABLE":
        raise RunnerError("checkpoint runner is not activated by P1")
    if event_name != "schedule" or run_attempt != 1:
        raise RunnerError("only the original scheduled run is admissible")
    runner = contract.get("runner", {})
    if runner.get("path") != "scripts/run_benchmark_v15_checkpoint.py":
        raise RunnerError("unexpected frozen runner path")
    invocation = runner.get("invocation_contract", {})
    if invocation.get("capture_required_argument") != "--private-input" or invocation.get("capture_without_private_input_permitted") is not False:
        raise RunnerError("CAPTURE private-input interface differs from the runner")
    if invocation.get("terminal_gap_required_argument") != "--terminal-chronology-gap" or invocation.get("terminal_gap_with_private_input_permitted") is not False:
        raise RunnerError("terminal-gap private-input interface differs from the runner")
    private_input = runner.get("private_input", {})
    if private_input.get("schema_path") != "schemas/benchmark-checkpoint-runner-private-input-v1.5.schema.json":
        raise RunnerError("unexpected private-input schema path")
    expected_private_schema = private_input.get("schema_sha256")
    actual_private_schema = sha256_file(ROOT / private_input["schema_path"])
    if not isinstance(expected_private_schema, str) or expected_private_schema != actual_private_schema:
        raise RunnerError("private-input schema bytes are not P1-frozen")
    expected_runner = runner.get("sha256")
    if not isinstance(expected_runner, str) or expected_runner != sha256_file(Path(__file__).resolve()):
        raise RunnerError("runner bytes are not the P1-frozen bytes")
    workflow = contract.get("frozen", {})
    workflow_path = repo_file(workflow.get("workflow_path"), "workflow")
    if workflow.get("workflow_sha256") != sha256_file(workflow_path):
        raise RunnerError("workflow bytes are not P1-frozen")
    publication = contract.get("publication", {})
    if publication.get("files") != list(PUBLIC_FILES) or publication.get("logs_permitted") is not False:
        raise RunnerError("publication boundary differs from the runner boundary")
    if set(publication.get("forbidden_fields", ())) - FORBIDDEN_KEYS:
        raise RunnerError("runner does not enforce every contract-forbidden field")
    return contract


def validate_source_readiness() -> None:
    boundary = load_json(ROOT / "results/benchmark/v1.5-protocol/source-boundary.json", "source boundary")
    policy = load_json(ROOT / "results/benchmark/v1.5-protocol/source-path-purpose-policy.json", "source path policy")
    if boundary.get("status") != "FROZEN_P1_EXECUTABLE" or policy.get("status") != "FROZEN_P1_EXECUTABLE":
        raise RunnerError("source custody is not operationally frozen")
    readiness = boundary.get("operational_readiness", {})
    if readiness.get("executable") is not True or readiness.get("fail_closed") is not True:
        raise RunnerError("source custody readiness is incomplete")


def authenticate_p1_and_components(u1_path: Path, contract_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        u1 = chronology.validate_u1(u1_path)
    except chronology.ChronologyError as exc:
        raise RunnerError("U1 authentication failed") from exc
    p1t_ref = u1.get("p1", {}).get("p1t_artifact")
    p1t_path = exact_file(p1t_ref, "P1T")
    p1t = load_json(p1t_path, "P1T")
    p1a_path = repo_file(p1t.get("p1a", {}).get("path"), "P1A")
    try:
        p1a, _p1t, _binding = aggregate.authenticate_p1(
            p1a_path, p1t_path, u1["p1"]["p1t_commit"]
        )
        components, runtime = aggregate.load_components(
            ROOT / "results/benchmark/v1.5-protocol/checkpoint-component-manifest.json", p1a
        )
    except aggregate.CertificateError as exc:
        raise RunnerError("P1 component closure authentication failed") from exc
    frozen_contract = components.get("registry", {}).get("invocation_contract", {})
    if frozen_contract != {
        "path": contract_path.resolve().relative_to(ROOT).as_posix(),
        "sha256": sha256_file(contract_path.resolve()),
    }:
        raise RunnerError("invocation contract is not selected by authenticated P1")
    return components, runtime


def validate_chain(
    proof_path: Path, repository: Path, u1_path: Path, scheduled_for: str,
) -> dict[str, Any]:
    u1 = chronology.validate_u1(u1_path)
    try:
        proof = chronology.validate_public_chain_proof(
            proof_path, repository.resolve(), chronology.public_chain.PUBLICATION_REF,
            u1["p1"]["p1t_commit"],
        )
        chronology.checkpoint_position(u1, proof, scheduled_for)
    except chronology.ChronologyError as exc:
        raise RunnerError("public checkpoint chain authentication failed") from exc
    return proof


def validate_private_input(path: Path, scheduled_for: str, proof: dict[str, Any]) -> dict[str, Any]:
    value = load_json(path, "private input manifest")
    validate_schema(value, "benchmark-checkpoint-runner-private-input-v1.5.schema.json", "private input manifest")
    checkpoint = value["checkpoint"]
    if checkpoint["scheduled_for_utc"] != scheduled_for or checkpoint["public_chain_proof_sha256"] != proof["proof_sha256"]:
        raise RunnerError("private input is bound to another checkpoint")
    for key in ("coverage_certificate", "public_sealed_binding"):
        exact_file(value["custody"][key], key, private=True)
    for key in ("private_registry", "provenance_content_pack"):
        exact_file(value["registry"][key], key, private=True)
    for index, ref in enumerate(value["registry"]["provenance_ledgers"]):
        exact_file(ref, f"provenance ledger {index}", private=True)
    isolated = Path(value["replay"]["isolated_repository"]).resolve()
    if not isolated.is_dir():
        raise RunnerError("isolated replay repository is absent")
    # The current custody certificates deliberately have PRE-P1-only status.
    # Operational status constants and their validators must be frozen before
    # this runner can consume their contents.
    coverage = load_json(Path(value["custody"]["coverage_certificate"]["path"]), "custody coverage")
    binding = load_json(Path(value["custody"]["public_sealed_binding"]["path"]), "custody binding")
    if coverage.get("status") != "FROZEN_P1_CUSTODY_COVERAGE_VALID" or binding.get("status") != "FROZEN_P1_PUBLIC_BINDING_VALID":
        raise RunnerError("private custody evidence is not operationally frozen")
    return value


def _terminal_certificate(scheduled_for: str, proof: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema": GAP_SCHEMA,
        "artifact_kind": "TERMINAL_CHRONOLOGY_GAP_CERTIFICATE",
        "protocol_version": "1.5",
        "scheduled_for_utc": scheduled_for,
        "status": "INVALID_CHRONOLOGY_CAPTURE",
        "public_chain_proof_sha256": proof["proof_sha256"],
        "capture_attempted": False,
        "private_inputs_read": False,
    }
    value["certificate_sha256"] = content_digest(value, "certificate_sha256")
    validate_schema(value, "benchmark-terminal-chronology-gap-certificate-v1.5.schema.json", "gap certificate")
    return value


def _publication_manifest(scheduled_for: str, mode: str, certificate: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema": MANIFEST_SCHEMA,
        "artifact_kind": "CHECKPOINT_PUBLICATION_MANIFEST",
        "protocol_version": "1.5",
        "scheduled_for_utc": scheduled_for,
        "mode": mode,
        "public_files": list(PUBLIC_FILES),
        "artifacts": {
            "quota-certificate.json": {"sha256": hashlib.sha256(canonical_json(certificate)).hexdigest(), "schema": certificate["schema"]},
            "receipt.json": {"sha256": hashlib.sha256(canonical_json(receipt)).hexdigest(), "schema": receipt["schema"]},
        },
        "publication_boundary": {
            "identities_present": False, "statement_text_present": False,
            "outcomes_present": False, "ranking_present": False,
            "entropy_present": False, "logs_present": False,
        },
    }
    value["manifest_sha256"] = content_digest(value, "manifest_sha256")
    validate_schema(value, "benchmark-checkpoint-publication-manifest-v1.5.schema.json", "publication manifest")
    return value


def publish(output: Path, values: dict[str, dict[str, Any]]) -> None:
    if set(values) != set(PUBLIC_FILES):
        raise RunnerError("publication allowlist mismatch")
    if output.exists() and any(output.iterdir()):
        raise RunnerError("publication output is not empty")
    parent = output.parent.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".method-v15-publication-", dir=parent))
    try:
        for name in PUBLIC_FILES:
            assert_no_public_secrets(values[name])
            (temporary / name).write_bytes(
                json.dumps(values[name], ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n"
            )
        if sorted(path.name for path in temporary.iterdir()) != sorted(PUBLIC_FILES):
            raise RunnerError("publication staging allowlist mismatch")
        if output.exists():
            output.rmdir()
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def run(args: argparse.Namespace) -> None:
    contract_path = args.contract.resolve()
    validate_contract(contract_path, args.event_name, args.run_attempt)
    validate_source_readiness()
    authenticate_p1_and_components(args.u1_receipt.resolve(), contract_path)
    proof = validate_chain(
        args.public_chain_proof.resolve(), args.public_repository.resolve(),
        args.u1_receipt.resolve(), args.scheduled_for_utc,
    )
    if args.terminal_chronology_gap:
        if args.private_input is not None:
            raise RunnerError("terminal gap mode must not receive private inputs")
        try:
            receipt = chronology.record_missed_checkpoint(
                args.u1_receipt.resolve(), args.public_chain_proof.resolve(),
                args.public_repository.resolve(), chronology.public_chain.PUBLICATION_REF,
                args.scheduled_for_utc,
            )
        except chronology.ChronologyError as exc:
            raise RunnerError("terminal chronology-gap receipt rejected") from exc
        certificate = _terminal_certificate(args.scheduled_for_utc, proof)
        manifest = _publication_manifest(args.scheduled_for_utc, "TERMINAL_CHRONOLOGY_GAP", certificate, receipt)
        publish(args.output.resolve(), {
            "publication-manifest.json": manifest,
            "quota-certificate.json": certificate,
            "receipt.json": receipt,
        })
        return
    if args.private_input is None:
        raise RunnerError("CAPTURE mode requires the frozen private input manifest")
    validate_private_input(args.private_input.resolve(), args.scheduled_for_utc, proof)
    raise RunnerError("CAPTURE execution adapter is not frozen; refusing to synthesize source completeness")


def parser() -> argparse.ArgumentParser:
    value = SilentParser(add_help=False)
    value.add_argument("--contract", type=Path, required=True)
    value.add_argument("--u1-receipt", type=Path, required=True)
    value.add_argument("--scheduled-for-utc", required=True)
    value.add_argument("--event-name", required=True)
    value.add_argument("--run-attempt", type=int, required=True)
    value.add_argument("--public-chain-proof", type=Path, required=True)
    value.add_argument("--public-repository", type=Path, required=True)
    value.add_argument("--private-input", type=Path)
    value.add_argument("--terminal-chronology-gap", action="store_true")
    value.add_argument("--output", type=Path, required=True)
    return value


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        run(args)
    except (RunnerError, OSError, ValueError, KeyError, TypeError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
