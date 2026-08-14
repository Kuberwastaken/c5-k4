#!/usr/bin/env python3
"""Contract and adversarial tests for the inert v1.5 private-input assembler."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft7Validator, ValidationError

import build_benchmark_v15_runner_private_input as A


ZERO = "0" * 64
ONE = "1" * 64
TWO = "2" * 64
THREE = "3" * 64
FOUR = "4" * 64
FIVE = "5" * 64
HOST = "ai-vps-controlled-harness"
SCOPE = {
    "participant_ledger_sha256": ONE,
    "source_boundary_sha256": TWO,
    "noninterference_receipt_sha256": THREE,
    "service_epoch_binding_sha256": FIVE,
}
P1_SCOPE_EXTRA = {
    "participant_ledger_artifact_sha256": "6" * 64,
    "noninterference_receipt_schema_sha256": "7" * 64,
    "noninterference_verifier_sha256": "8" * 64,
    "operational_noninterference_key_commitment_sha256": "9" * 64,
    "operational_noninterference_key_commitment_schema_sha256": "a" * 64,
}


def accepted_store() -> dict:
    value = {
        "schema": "c5k4-method-v1.5-worm-store-acceptance-1.0",
        "status": "FROZEN_P1_WORM_STORE_ACCEPTED",
        "operational": True,
        "backend": "AWS_S3_OBJECT_LOCK",
        "config_sha256": ZERO,
        "acceptance_receipt_sha256": ONE,
        "retention_through_utc": "2028-08-15T00:00:00Z",
        "private_only": True,
    }
    value["acceptance_sha256"] = A._self_digest(value, "acceptance_sha256")
    return value


def locator(acceptance: dict, raw: bytes = b"{}\n", key: str = "private/objects/a") -> dict:
    return {
        "schema": "c5k4-method-v1.5-private-artifact-locator-1.0",
        "status": "FROZEN_P1_WORM_OBJECT_VERIFIED",
        "backend": "AWS_S3_OBJECT_LOCK",
        "bucket": "private-benchmark-bucket",
        "key": key,
        "version_id": "version-1",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_count": len(raw),
        "retain_until_utc": "2028-08-15T00:00:00Z",
        "store_acceptance_sha256": acceptance["acceptance_sha256"],
        "private_only": True,
    }


def request() -> dict:
    acceptance = accepted_store()
    base = locator(acceptance)
    names = (
        "u1_receipt", "checkpoint_capture", "v14_exclusion", "grouping_rule",
        "classifier", "public_chain_proof", "provenance_content_pack",
        "custody_coverage_certificate", "public_custody_sealed_binding",
        "sealed_private_custody_bundle", "primary_acquisition_receipt",
        "p1_role_resolution", "participant_ledger", "source_boundary",
        "noninterference_receipt", "noninterference_receipt_schema",
        "noninterference_verifier", "noninterference_verification_key",
        "operational_noninterference_key_commitment",
        "operational_noninterference_key_commitment_schema",
        "service_epoch_binding",
        "replay_acquisition_receipt", "primary_private_registry",
        "replayed_private_registry",
    )
    artifacts = {
        name: {**base, "key": f"private/objects/{name}"} for name in names
    }
    artifacts["provenance_ledgers"] = [
        {**base, "key": "private/objects/ledger-0"}
    ]
    return {
        "schema": "c5k4-method-v1.5-runner-private-input-assembly-1.0",
        "status": "FROZEN_P1_PRIVATE_INPUT_ASSEMBLY_READY",
        "publication_permitted": False,
        "runner_contract": {
            "runner_path": "scripts/run_benchmark_v15_checkpoint.py",
            "invocation_contract_path": "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json",
            "private_input_schema_path": "schemas/benchmark-checkpoint-runner-private-input-v1.5.schema.json",
            "assembly_executable_sha256": A.sha256_file(Path(A.__file__)),
        },
        "checkpoint": {
            "scheduled_for_utc": "2026-08-15T00:17:00Z",
            "public_chain_proof_sha256": TWO,
            "required_custody_from_utc": "2026-08-14T00:00:00Z",
            "required_custody_through_utc": "2026-08-15T00:30:00Z",
        },
        "p1_scope": {
            "p1t_commit": "a" * 40,
            "p1t_path": "results/benchmark/v1.5-protocol/p1t.json",
            "role_resolution_sha256": FOUR,
            **{key: SCOPE[key] for key in (
                "participant_ledger_sha256", "source_boundary_sha256",
                "noninterference_receipt_sha256",
            )},
            **P1_SCOPE_EXTRA,
            "required_host_id": HOST,
        },
        "store_acceptance": acceptance,
        "artifacts": artifacts,
    }


def operational_coverage() -> dict:
    host = {
        "host_id": HOST, "signing_key_id": "key-1",
        "first_batch_sequence": 0, "last_batch_sequence": 1,
        "first_record_sequence": 0, "last_record_sequence": 4,
        "first_observed_at_utc": "2026-08-14T00:00:00Z",
        "last_observed_at_utc": "2026-08-15T00:30:00Z",
        "batch_count": 2, "record_count": 5,
        "last_batch_sha256": ZERO, "last_receipt_sha256": ONE,
        "maximum_observed_gap_seconds": 300, "restart_count": 0,
        "chain_complete": True,
    }
    value = {
        "schema": "c5k4-method-v1.5-private-custody-coverage-certificate-1.0",
        "status": "FROZEN_P1_CUSTODY_COVERAGE_VALID",
        "protocol_version": "1.5",
        "verification_mode": "TARGET_BLIND_METADATA_ONLY",
        "required_from_utc": "2026-08-14T00:00:00Z",
        "required_through_utc": "2026-08-15T00:30:00Z",
        "maximum_heartbeat_interval_seconds": 300,
        **SCOPE,
        "store_acceptance_sha256": accepted_store()["acceptance_sha256"],
        "required_hosts": [HOST], "host_chains": [host],
        "complete": True, "gaps": [],
    }
    value["certificate_sha256"] = A.custody.certificate_digest(value)
    return value


def operational_binding(coverage: dict, sealed: bytes = b"sealed") -> dict:
    value = {
        "schema": "c5k4-method-v1.5-public-custody-sealed-binding-1.0",
        "status": "FROZEN_P1_PUBLIC_BINDING_VALID",
        "protocol_version": "1.5",
        "disclosure": "TARGET_BLIND_HASHES_AND_COVERAGE_ONLY",
        "seal_algorithm": "FROZEN_P1_OPAQUE_AUTHENTICATED_ENVELOPE_V1",
        "sealed_private_bundle_sha256": hashlib.sha256(sealed).hexdigest(),
        "sealed_private_bundle_byte_count": len(sealed),
        "private_coverage_certificate_sha256": coverage["certificate_sha256"],
        **{key: coverage[key] for key in (
            "participant_ledger_sha256", "source_boundary_sha256",
            "noninterference_receipt_sha256", "store_acceptance_sha256",
            "service_epoch_binding_sha256",
        )},
        "required_host_count": 1,
        "required_from_utc": coverage["required_from_utc"],
        "required_through_utc": coverage["required_through_utc"],
    }
    value["binding_sha256"] = A.custody.binding_digest(value)
    return value


class PrivateAssemblerContractTests(unittest.TestCase):
    def schema(self, name: str) -> dict:
        return json.loads((A.ROOT / "schemas" / name).read_text(encoding="utf-8"))

    def validate(self, value: object, name: str) -> None:
        Draft7Validator(self.schema(name)).validate(value)

    def test_new_schemas_are_valid_draft7(self) -> None:
        for name in (A.LOCATOR_SCHEMA, A.REQUEST_SCHEMA, A.CUSTODY_SCHEMA, A.NONINTERFERENCE_SCHEMA):
            Draft7Validator.check_schema(self.schema(name))

    def test_request_requires_worm_operational_receipt_verifier_and_raw_key(self) -> None:
        value = request()
        self.validate(value, A.REQUEST_SCHEMA)
        for artifact in (
            "noninterference_receipt_schema", "noninterference_verifier",
            "noninterference_verification_key", "operational_noninterference_key_commitment",
            "operational_noninterference_key_commitment_schema",
        ):
            mutated = copy.deepcopy(value)
            del mutated["artifacts"][artifact]
            with self.assertRaises(ValidationError):
                self.validate(mutated, A.REQUEST_SCHEMA)

    def test_scope_gate_cryptographically_verifies_operational_receipt(self) -> None:
        value = request()
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        participant = json.loads(
            (A.ROOT / "results/benchmark/v1.5-protocol/participant-ledger.json").read_text()
        )
        boundary_raw = b'{"status":"FROZEN_P1_EXECUTABLE"}\n'
        receipt = {
            "schema": "c5k4-method-v1.5-operational-noninterference-receipt-1.0",
            "status": "FROZEN_P1_NONINTERFERENCE_LIVE_ACCEPTED",
            "protocol_version": "1.5", "host_id": HOST,
            "participant_ledger_sha256": participant["ledger_sha256"],
            "source_boundary_sha256": A.sha256(boundary_raw),
            "signing_key_id": "key-1", "service_epoch_binding_sha256": FIVE,
            "verification_key_sha256": A.sha256(public_key),
            "signature_algorithm": "Ed25519", "unjournaled_delivery_detected": False,
            "proofs": {key: True for key in (
                "dedicated_nonlogin_identity", "root_owned_read_only_p1_checkout",
                "private_root_permissions", "private_socket_permissions",
                "credential_isolation", "network_default_deny",
                "allowed_endpoint_enforcement", "excluded_process_denial",
                "unbroken_ingress_custody", "destructive_gap_acceptance",
            )},
            "blockers": [], "scope_complete": True, "operational_ready": True,
            "activation_permitted": True,
            "claims": {"p1_frozen": True, "operational_capture": True, "production_ready": True, "target_specific": False},
        }
        receipt["receipt_sha256"] = A.noninterference_verifier.operational_receipt_digest(receipt)
        import base64
        receipt["signature"] = base64.b64encode(
            private_key.sign(bytes.fromhex(receipt["receipt_sha256"]))
        ).decode()
        commitment = {
            "schema": "c5k4-method-v1.5-operational-noninterference-key-commitment-1.0",
            "status": "FROZEN_P1_NONINTERFERENCE_KEY_COMMITTED",
            "protocol_version": "1.5", "host_id": HOST,
            "signing_key_id": receipt["signing_key_id"],
            "signature_algorithm": "Ed25519",
            "verification_key_sha256": A.sha256(public_key),
            "operational": True, "activation_permitted": True, "target_specific": False,
        }
        commitment["commitment_sha256"] = A._self_digest(commitment, "commitment_sha256")
        raw = {
            "participant_ledger": A.canonical_json(participant),
            "source_boundary": boundary_raw,
            "noninterference_receipt": A.canonical_json(receipt),
            "noninterference_receipt_schema": (A.ROOT / "schemas" / A.NONINTERFERENCE_SCHEMA).read_bytes(),
            "noninterference_verifier": Path(A.noninterference_verifier.__file__).read_bytes(),
            "noninterference_verification_key": public_key,
            "operational_noninterference_key_commitment": A.canonical_json(commitment),
            "operational_noninterference_key_commitment_schema": (A.ROOT / "schemas" / A.NONINTERFERENCE_KEY_COMMITMENT_SCHEMA).read_bytes(),
            "p1_role_resolution": b"placeholder",
        }
        value["p1_scope"].update({
            "participant_ledger_sha256": participant["ledger_sha256"],
            "participant_ledger_artifact_sha256": A.sha256(raw["participant_ledger"]),
            "source_boundary_sha256": A.sha256(boundary_raw),
            "noninterference_receipt_sha256": A.sha256(raw["noninterference_receipt"]),
            "noninterference_receipt_schema_sha256": A.sha256(raw["noninterference_receipt_schema"]),
            "noninterference_verifier_sha256": A.sha256(raw["noninterference_verifier"]),
            "operational_noninterference_key_commitment_sha256": A.sha256(raw["operational_noninterference_key_commitment"]),
            "operational_noninterference_key_commitment_schema_sha256": A.sha256(raw["operational_noninterference_key_commitment_schema"]),
        })
        roles = []
        for artifact, (role, scope_key) in A.P1_SCOPE_ROLES.items():
            roles.append({"role": role, "closure": "NATIVE_V1_5", "sha256": value["p1_scope"][scope_key]})
        resolution = {"status": "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE", "operational": True, "resolved_roles": roles}
        resolution["resolution_sha256"] = "r" * 64
        value["p1_scope"]["role_resolution_sha256"] = "r" * 64
        raw["p1_role_resolution"] = A.canonical_json(resolution)
        with mock.patch.object(A.p1_roles, "resolve_published_roles", return_value=resolution):
            self.assertEqual(A._validate_p1_scope(value, raw)["receipt_sha256"], receipt["receipt_sha256"])
            original_key = raw["noninterference_verification_key"]
            raw["noninterference_verification_key"] = b"x" * 32
            with self.assertRaises(A.AssemblyError): A._validate_p1_scope(value, raw)
            raw["noninterference_verification_key"] = original_key
            forged = copy.deepcopy(receipt); forged["signature"] = "A" * 86 + "=="
            raw["noninterference_receipt"] = A.canonical_json(forged)
            value["p1_scope"]["noninterference_receipt_sha256"] = A.sha256(raw["noninterference_receipt"])
            for row in resolution["resolved_roles"]:
                if row["role"] == "noninterference_receipt": row["sha256"] = value["p1_scope"]["noninterference_receipt_sha256"]
            with self.assertRaises(A.AssemblyError): A._validate_p1_scope(value, raw)
        for field in P1_SCOPE_EXTRA:
            mutated = copy.deepcopy(value)
            del mutated["p1_scope"][field]
            with self.assertRaises(ValidationError):
                self.validate(mutated, A.REQUEST_SCHEMA)

    def test_forged_operational_cli_is_silent_and_inert(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            request_path = root / "forged-request.json"
            config_path = root / "forged-config.json"
            request_path.write_text(json.dumps(request()), encoding="utf-8")
            config_path.write_text("{}", encoding="utf-8")
            stage, output = root / "stage", root / "private-input.json"
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(A, "_s3_fetcher") as fetcher, \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = A.main([
                    "--request", str(request_path), "--store-config", str(config_path),
                    "--private-stage", str(stage), "--output", str(output),
                ])
            self.assertEqual(code, 2)
            self.assertEqual(out.getvalue(), "")
            self.assertEqual(err.getvalue(), "")
            fetcher.assert_not_called()
            self.assertFalse(stage.exists())
            self.assertFalse(output.exists())

    def test_malformed_cli_is_also_silent(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = A.main(["--not-an-interface"])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "")

    def test_internal_assemble_gates_before_fetch_or_write(self) -> None:
        called = 0

        def fetch(_locator: dict) -> bytes:
            nonlocal called
            called += 1
            return b"{}\n"

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(A.AssemblyError):
                A.assemble(request(), fetch, root / "stage", root / "out")
            self.assertEqual(called, 0)
            self.assertFalse((root / "stage").exists())
            self.assertFalse((root / "out").exists())

    def test_locator_is_closed_and_has_no_local_path(self) -> None:
        value = locator(accepted_store())
        self.validate(value, A.LOCATOR_SCHEMA)
        value["path"] = "/private/file"
        with self.assertRaises(ValidationError):
            self.validate(value, A.LOCATOR_SCHEMA)

    def test_request_rejects_pre_p1_acceptance_status(self) -> None:
        value = request()
        value["store_acceptance"]["status"] = "PRE_P1_STORE_ADAPTER_NOT_OPERATIONAL"
        with self.assertRaises(A.AssemblyError):
            A.validate_request(value)

    def test_fetch_rechecks_locator_bytes_and_acceptance(self) -> None:
        value = request()
        with self.assertRaises(A.AssemblyError):
            A.fetch_artifacts(value, lambda _locator: b"wrong")
        value["artifacts"]["u1_receipt"]["store_acceptance_sha256"] = ZERO
        with self.assertRaises(A.AssemblyError):
            A.fetch_artifacts(value, lambda _locator: b"{}\n")

    def test_operational_custody_shapes_are_closed(self) -> None:
        coverage = operational_coverage()
        binding = operational_binding(coverage)
        self.validate(coverage, A.CUSTODY_SCHEMA)
        self.validate(binding, A.CUSTODY_SCHEMA)

        extra = copy.deepcopy(coverage)
        extra["host_chains"][0]["unbounded_private_metadata"] = "forbidden"
        with self.assertRaises(ValidationError):
            self.validate(extra, A.CUSTODY_SCHEMA)

        malformed = copy.deepcopy(coverage)
        malformed["host_chains"][0]["maximum_observed_gap_seconds"] = 301
        with self.assertRaises(ValidationError):
            self.validate(malformed, A.CUSTODY_SCHEMA)

        heartbeat = copy.deepcopy(coverage)
        heartbeat["maximum_heartbeat_interval_seconds"] = 299
        with self.assertRaises(ValidationError):
            self.validate(heartbeat, A.CUSTODY_SCHEMA)

        algorithm = copy.deepcopy(binding)
        algorithm["seal_algorithm"] = "some-nonempty-string"
        with self.assertRaises(ValidationError):
            self.validate(algorithm, A.CUSTODY_SCHEMA)

    def test_custody_cross_bindings_and_sealed_bytes_are_verified(self) -> None:
        coverage = operational_coverage()
        sealed = b"sealed"
        binding = operational_binding(coverage, sealed)
        raw = {
            "custody_coverage_certificate": canonical(coverage),
            "public_custody_sealed_binding": canonical(binding),
            "sealed_private_custody_bundle": sealed,
        }
        receipt = {**SCOPE, "host_id": HOST, "signing_key_id": "key-1"}
        with mock.patch.object(A, "_validate_p1_scope", return_value=receipt):
            A._validate_custody(request(), raw)
        raw["sealed_private_custody_bundle"] = b"changed"
        with mock.patch.object(A, "_validate_p1_scope", return_value=receipt), \
                self.assertRaises(A.AssemblyError):
            A._validate_custody(request(), raw)

        duplicate = operational_coverage()
        duplicate["required_hosts"] = [HOST, "other-vps"]
        duplicate["host_chains"].append(copy.deepcopy(duplicate["host_chains"][0]))
        duplicate["host_chains"][1]["host_id"] = HOST
        duplicate["certificate_sha256"] = A.custody.certificate_digest(duplicate)
        duplicate_binding = operational_binding(duplicate, sealed)
        bad = {
            "custody_coverage_certificate": canonical(duplicate),
            "public_custody_sealed_binding": canonical(duplicate_binding),
            "sealed_private_custody_bundle": sealed,
        }
        with mock.patch.object(A, "_validate_p1_scope", return_value=receipt), \
                self.assertRaises(A.AssemblyError):
            A._validate_custody(request(), bad)

    def test_acquisitions_must_be_distinct_and_match_capture(self) -> None:
        primary = {
            "repository_path": "/private/primary.git", "receipt_sha256": ZERO,
            "remote": A.UPSTREAM, "remote_ref": A.UPSTREAM_REF,
            "audit": {"commit": "a" * 40, "root_tree": "b" * 40},
        }
        replay = copy.deepcopy(primary)
        capture = {"upstream": {"commit": "a" * 40, "root_tree": "b" * 40}}
        with mock.patch.object(A.vendor, "validate_receipt"):
            with self.assertRaises(A.AssemblyError):
                A._validate_acquisitions(primary, replay, capture)
            replay["repository_path"] = "/private/replay.git"
            replay["receipt_sha256"] = ONE
            left, right = A._validate_acquisitions(primary, replay, capture)
        self.assertNotEqual(left, right)

    def test_private_registry_is_executed_on_both_acquisitions(self) -> None:
        result = {"registry_sha256": ""}
        result["registry_sha256"] = A.future.registry_digest(result)
        registry_raw = A.future.pretty_json(result)
        capture = {
            "artifact_kind": "CHECKPOINT_CAPTURE",
            "status": "AWAITING_MACHINE_QUOTA_CERTIFICATE",
            "scheduled_for_utc": "2026-08-15T00:17:00Z",
            "basis": {"public_chain_proof": {"proof_sha256": TWO}},
        }
        proof = {"proof_sha256": TWO}
        raw = {
            "u1_receipt": b"{}", "checkpoint_capture": canonical(capture),
            "v14_exclusion": b"{}", "grouping_rule": b"{}",
            "classifier": b"{}", "public_chain_proof": canonical(proof),
            "provenance_content_pack": b"{}", "provenance_ledgers": [b"{}"],
            "primary_private_registry": registry_raw,
            "replayed_private_registry": registry_raw,
            "primary_acquisition_receipt": b"{}",
            "replay_acquisition_receipt": b"{}",
        }
        repos = (Path("/private/primary.git"), Path("/private/replay.git"))
        with tempfile.TemporaryDirectory() as temporary, \
                mock.patch.object(A, "_validate"), \
                mock.patch.object(A, "_validate_acquisitions", return_value=repos), \
                mock.patch.object(A.identity_hits, "load_content_pack", return_value={}), \
                mock.patch.object(A.future, "build", side_effect=[result, result]) as build:
            A.verify_private_replay(request(), raw, Path(temporary))
        self.assertEqual(build.call_count, 2)
        self.assertEqual(build.call_args_list[0].kwargs["repository"], repos[0])
        self.assertEqual(build.call_args_list[1].kwargs["repository"], repos[1])


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"


if __name__ == "__main__":
    unittest.main()
