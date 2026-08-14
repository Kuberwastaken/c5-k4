#!/usr/bin/env python3
"""Security-contract tests for public A0, typed evidence, recompiles, and P1R."""

from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
H = "a" * 64
OID = "b" * 40
T0 = "2026-08-14T00:00:00Z"
T1 = "2026-08-14T01:00:00Z"
DOMAINS = (
    ("PARTICIPANT_SCOPE_AND_NONINTERFERENCE", "CANDIDATE_C_PARTICIPANT_NONINTERFERENCE_ACCEPTED"),
    ("CONTROLLED_HARNESS_DEPLOYMENT_AND_RUNTIME", "CANDIDATE_C_CONTROLLED_HARNESS_ACCEPTED"),
    ("IMMUTABLE_WORM_STORE", "CANDIDATE_C_IMMUTABLE_WORM_ACCEPTED"),
    ("DESTRUCTIVE_GAP_ACCEPTANCE", "CANDIDATE_C_DESTRUCTIVE_GAP_ACCEPTED"),
    ("BROKER_CUSTODY_AND_CAPTURE_REPLAY", "CANDIDATE_C_BROKER_CUSTODY_CAPTURE_REPLAY_ACCEPTED"),
    ("CLASSIFIER_CLOSURE", "CANDIDATE_C_CLASSIFIER_CLOSURE_ACCEPTED"),
    ("EXPERIMENTER_NONINTERVENTION", "CANDIDATE_C_EXPERIMENTER_NONINTERVENTION_ACCEPTED"),
)


def schema(name: str) -> dict:
    value = json.loads((ROOT / "schemas" / name).read_text())
    Draft7Validator.check_schema(value)
    return value


def validate(name: str, value: dict) -> None:
    Draft7Validator(schema(name)).validate(value)


def embedded(value: dict) -> dict:
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    import hashlib
    return {"encoding": "BASE64_CANONICAL_JSON_UTF8", "canonical_json_base64": base64.b64encode(raw).decode(), "sha256": hashlib.sha256(raw).hexdigest()}


def authority() -> dict:
    issuer_rows = [
        {"signer_class": "OPERATIONAL_EVIDENCE_ISSUER", "domain": domain, "signer_id": f"issuer-{index}", "verification_key_sha256": f"{index + 1:x}" * 64}
        for index, (domain, _) in enumerate(DOMAINS)
    ]
    return {
        "schema": "c5k4-method-v1.5-public-readiness-authority-root-1.0",
        "status": "PUBLIC_PRE_C_READINESS_AUTHORITIES_FROZEN", "protocol_version": "1.5",
        "authority_epoch_id": "epoch-1", "created_at_utc": T0, "target_specific": False,
        "controlled_harness": {"signer_class": "CONTROLLED_HARNESS_READINESS_KEY", "signer_id": "harness", "verification_key_sha256": "8" * 64},
        "experimenters": [{"signer_class": "FROZEN_EXPERIMENTER_IDENTITY", "signer_id": "experimenter", "verification_key_sha256": "9" * 64}],
        "evidence_issuers": issuer_rows,
        "independent_recompilers": [
            {"signer_class": "INDEPENDENT_RECOMPILER", "signer_id": "recompiler-a", "verification_key_sha256": "a" * 64},
            {"signer_class": "INDEPENDENT_RECOMPILER", "signer_id": "recompiler-b", "verification_key_sha256": "b" * 64},
        ],
        "nonintervention_contract_sha256": "c" * 64, "challenge_namespace_sha256": "d" * 64,
        "authority_root_sha256": "e" * 64,
    }


def evidence() -> dict:
    rows = []
    for index, (domain, status) in enumerate(DOMAINS):
        rows.append({
            "domain": domain, "accepted_status": status,
            "artifact": {"scheme": "S3_OBJECT_LOCK_VERSION", "bucket_arn": "arn:aws:s3:::c5k4-test", "object_key": f"evidence/{index}.json", "version_id": f"version-{index}", "object_sha256": f"{index + 1:x}" * 64, "size_bytes": 100, "retention_until_utc": T1},
            "artifact_schema": {"path": f"schemas/domain-{index}.json", "sha256": H},
            "frozen_verifier": {"path": f"scripts/domain-{index}.py", "sha256": H}, "verifier_protocol": "C5K4_CANDIDATE_READINESS_VERIFY_V1",
            "self_digest_field": "receipt_sha256", "self_digest_domain": f"c5k4-method-v1.5-domain-{index}",
            "self_digest_excluded_fields": ["signature"],
            "candidate_commit": OID, "authority_root_commit": "c" * 40, "service_epoch_binding_sha256": H,
            "challenge_nonce": f"{index + 1:x}" * 64, "observed_at_utc": T0, "valid_through_utc": T1,
            "issuer": {"signer_id": f"issuer-{index}", "verification_key_sha256": f"{index + 1:x}" * 64},
            "acceptance_sha256": H, "signature": base64.b64encode(b"\0" * 64).decode(),
        })
    return {
        "schema": "c5k4-method-v1.5-candidate-base-operational-evidence-1.0",
        "status": "CANDIDATE_BASE_TYPED_OPERATIONAL_EVIDENCE_ACCEPTED", "protocol_version": "1.5",
        "candidate": {"commit": OID, "root_tree": "d" * 40},
        "authority_root": {"commit": "c" * 40, "root_tree": "e" * 40, "path": "results/authority.json", "sha256": H},
        "service_epoch_binding_sha256": H, "compiled_at_utc": T0, "valid_through_utc": T1,
        "evidence": rows, "bundle_sha256": H,
    }


def recompile(signer: str = "recompiler-a") -> dict:
    return {
        "schema": "c5k4-method-v1.5-candidate-base-independent-recompile-1.0",
        "status": "INDEPENDENT_EXACT_C_RECOMPILE_PASSED", "protocol_version": "1.5",
        "payload_sha256": H, "closure_aggregate_sha256": H, "operational_evidence_bundle_sha256": H,
        "authority_root_commit": "c" * 40, "authority_root_sha256": H, "compiler_closure_sha256": H,
        "validator_sha256": H, "execution_id": f"execution-{signer}", "execution_host_id": f"host-{signer}",
        "completed_at_utc": T0,
        "signer": {"signer_class": "INDEPENDENT_RECOMPILER", "signer_id": signer, "verification_key_sha256": H},
        "attestation_sha256": H, "signature": base64.b64encode(b"\0" * 64).decode(),
    }


def package() -> dict:
    file_ref = {"path": "scripts/validator.py", "sha256": H}
    sig = base64.b64encode(b"\0" * 64).decode()
    return {
        "schema": "c5k4-method-v1.5-candidate-base-readiness-package-1.0",
        "status": "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R", "protocol_version": "1.5",
        "candidate": {"commit": OID, "root_tree": "d" * 40},
        "authority_root": {"commit": "c" * 40, "root_tree": "e" * 40, "path": "results/authority.json", "sha256": H},
        "closures": {"native": {"row_count": 1, "sha256": H}, "inherited": {"row_count": 1, "sha256": H}, "full_source": {"row_count": 1, "sha256": H}, "aggregate_sha256": H},
        "operational_evidence": embedded(evidence()),
        "compiler": {key: copy.deepcopy(file_ref) for key in ("validator", "input_schema", "output_schema", "authority_root_schema", "operational_evidence_schema", "independent_recompile_schema", "readiness_package_schema", "p1r_schema", "activation_receipt_schema", "isolated_evidence_runner", "isolated_evidence_runner_schema", "isolated_evidence_runner_contract", "isolated_evidence_runner_test")},
        "structural_json_key_audit": {"algorithm": "STRUCTURAL_JSON_KEY_AUDIT_V1_5", "scope": ["V1_5_NATIVE_JSON_BLOBS", "V1_4_SELECTED_INHERITED_JSON_BLOBS", "V1_4_FULL_P0A_REFERENCED_JSON_BLOBS"], "json_blob_count": 1, "candidate_identities_keys_detected": 0, "statement_text_keys_detected": 0, "target_rankings_keys_detected": 0, "target_semantic_analysis_keys_detected": 0, "does_not_claim_free_text_or_python_semantic_audit": True},
        "payload_sha256": H,
        "authority_signatures": [
            {"signer_class": "CONTROLLED_HARNESS_READINESS_KEY", "signer_id": "harness", "verification_key_sha256": H, "algorithm": "Ed25519", "signature": sig},
            {"signer_class": "FROZEN_EXPERIMENTER_IDENTITY", "signer_id": "experimenter", "verification_key_sha256": H, "algorithm": "Ed25519", "signature": sig},
        ],
        "independent_recompiles": [embedded(recompile("recompiler-a")), embedded(recompile("recompiler-b"))],
        "package_sha256": H,
    }


def p1r() -> dict:
    binding = lambda ref, commit: {"ref": ref, "commit": commit}
    return {
        "schema_version": "c5k4-method-v1.5-p1r-1.0", "artifact_kind": "P1R",
        "status": "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY", "protocol_version": "1.5",
        "p1t": {"path": "results/benchmark/v1.5-protocol/P1T.json", "sha256": H}, "p1t_commit": OID,
        "observation": {
            "public_remote_url": "https://github.com/Kuberwastaken/c5-k4",
            "authority_root": binding("refs/tags/a0", "c" * 40), "v1_4_p0t": binding("refs/tags/p0t", "d" * 40),
            "candidate_c": binding("refs/tags/c", "e" * 40), "p1t": binding("refs/tags/p1t", OID),
            "observed_at_utc": T0, "ls_remote_stdout_sha256": H,
            "observer": {
                "workflow_repository": "Kuberwastaken/c5-k4",
                "workflow_path": ".github/workflows/method-v15-p1t-publication-observer.yml",
                "workflow_ref": ".github/workflows/method-v15-p1t-publication-observer.yml@refs/heads/main",
                "workflow_blob_sha256": H, "run_id": 1, "run_attempt": 1,
                "actions_run_projection_sha256": H,
            },
        },
        "activation_policy": {"structural_draft_only": True, "p1r_is_activation_boundary": False, "p1t_alone_is_activation_boundary": False, "full_exact_c_replay_required": True, "p1r_parent_must_be_exact_p1t": True, "allowed_p1r_changed_paths": ["results/benchmark/v1.5-protocol/P1R.json"], "public_p1r_ref_required": True},
    }


def activation_receipt() -> dict:
    return {
        "schema": "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
        "p1r": {"path": "results/benchmark/v1.5-protocol/P1R.json", "sha256": H},
        "p1r_commit": OID, "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
        "public_observation": {
            "workflow_repository": "Kuberwastaken/c5-k4",
            "workflow_path": ".github/workflows/method-v15-p1r-publication-observer.yml",
            "workflow_blob_sha256": H,
            "workflow_ref": ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r",
            "run_id": 1, "run_attempt": 1, "server_observed_at_utc": T0,
            "actions_run_projection_sha256": H,
        },
        "validation_inputs_sha256": H, "validation_diagnostic_sha256": H,
        "validator": {"path": "scripts/validate_benchmark_v15_candidate_base.py", "sha256": H},
        "receipt_sha256": H,
    }


class CandidateBaseSecuritySchemaTests(unittest.TestCase):
    def test_all_redesigned_artifacts_validate(self) -> None:
        for name, value in (
            ("benchmark-public-readiness-authority-root-v1.5.schema.json", authority()),
            ("benchmark-candidate-base-operational-evidence-v1.5.schema.json", evidence()),
            ("benchmark-candidate-base-independent-recompile-v1.5.schema.json", recompile()),
            ("benchmark-candidate-base-readiness-package-v1.5.schema.json", package()),
            ("benchmark-p1r-v1.5.schema.json", p1r()),
            ("benchmark-public-p1r-activation-receipt-v1.5.schema.json", activation_receipt()),
        ):
            validate(name, value)

    def test_authority_requires_every_class_and_two_recompilers(self) -> None:
        for mutation in (
            lambda value: value.__setitem__("experimenters", []),
            lambda value: value.__setitem__("evidence_issuers", value["evidence_issuers"][:-1]),
            lambda value: value.__setitem__("independent_recompilers", value["independent_recompilers"][:1]),
        ):
            value = authority(); mutation(value)
            with self.assertRaises(Exception):
                validate("benchmark-public-readiness-authority-root-v1.5.schema.json", value)

    def test_evidence_rejects_opaque_rows_wrong_status_and_placeholders(self) -> None:
        value = evidence(); value["evidence"][0] = {"domain": DOMAINS[0][0], "accepted": True, "sha256": H}
        with self.assertRaises(Exception):
            validate("benchmark-candidate-base-operational-evidence-v1.5.schema.json", value)
        value = evidence(); value["evidence"][0]["accepted_status"] = DOMAINS[1][1]
        with self.assertRaises(Exception):
            validate("benchmark-candidate-base-operational-evidence-v1.5.schema.json", value)

    def test_package_schema_rejects_single_recompile(self) -> None:
        value = package(); value["independent_recompiles"] = value["independent_recompiles"][:1]
        with self.assertRaises(Exception):
            validate("benchmark-candidate-base-readiness-package-v1.5.schema.json", value)

    def test_p1r_is_structural_draft_not_activation_boundary(self) -> None:
        value = p1r(); value["activation_policy"]["p1r_is_activation_boundary"] = True
        with self.assertRaises(Exception):
            validate("benchmark-p1r-v1.5.schema.json", value)
        value = p1r(); value["activation_policy"]["p1t_alone_is_activation_boundary"] = True
        with self.assertRaises(Exception):
            validate("benchmark-p1r-v1.5.schema.json", value)

    def test_activation_receipt_rejects_broad_ref_rerun_and_missing_content_binding(self) -> None:
        for mutate in (
            lambda value: value["public_observation"].__setitem__("workflow_ref", ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/main"),
            lambda value: value["public_observation"].__setitem__("run_attempt", 2),
            lambda value: value.pop("validation_diagnostic_sha256"),
        ):
            value = activation_receipt(); mutate(value)
            with self.assertRaises(Exception):
                validate("benchmark-public-p1r-activation-receipt-v1.5.schema.json", value)


if __name__ == "__main__":
    unittest.main()
