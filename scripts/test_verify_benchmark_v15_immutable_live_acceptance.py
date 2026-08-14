#!/usr/bin/env python3
"""Adversarial fixture tests for offline immutable-store live acceptance."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_benchmark_v15_immutable_live_acceptance.py"
SPEC = importlib.util.spec_from_file_location("verify_immutable_live_acceptance", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(ROOT / "scripts"))
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


ACCOUNT = "123456789012"
KEY_ID = "12345678-1234-1234-1234-123456789abc"
BUCKET = "c5k4-custody-generated-012345"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/c5k4/v1.5/custody-generated-role"
KEY_ARN = f"arn:aws:kms:ap-south-1:{ACCOUNT}:key/{KEY_ID}"
HARNESS_ARN = f"arn:aws:iam::{ACCOUNT}:role/controlled-harness"
EXTERNAL_ID = "fixture_external_id_0123456789abcdef"


def fixture() -> tuple[dict, bytes]:
    template = module.infra.load_object(module.TEMPLATE)
    plan = module.infra.load_object(module.PLAN)
    evidence = {
        "schema": "c5k4-method-v1.5-immutable-store-live-evidence-1.0",
        "status": "LIVE_ACCEPTANCE_EVIDENCE_CAPTURE", "visibility": "PRIVATE_ACCEPTANCE_EVIDENCE",
        "source": "INJECTED_TEST_FIXTURE", "acquired_at_utc": "2026-08-14T02:00:00Z",
        "account_id": ACCOUNT, "region": "ap-south-1", "receipt_sha256": "0" * 64,
        "bindings": {"template_sha256": plan["template_sha256"], **plan["commitments"], "store_config_sha256": "0" * 64},
        "resource_identities": {
            "bucket": BUCKET, "kms_key_id": KEY_ID, "kms_key_arn": KEY_ARN,
            "writer_role_arn": ROLE_ARN, "writer_policy_name": "c5k4-v1-5-private-custody-single-writer",
        },
        "iam": {
            "trusted_harness_principal_arn": HARNESS_ARN, "trusted_harness_external_id": EXTERNAL_ID,
            "role": {}, "trust_policy_document": {}, "boundary_policy_document": {},
            "inline_policy_document": {}, "inline_policy_names": ["c5k4-v1-5-private-custody-single-writer"],
            "attached_policy_arns": [],
        },
        "s3": {"retention_years": 3}, "kms": {}, "stack": {}, "destructive_probes": [],
        "target_specific": False,
    }
    values = module.substitutions(evidence)
    rendered_bucket_policy = module.render(template["Resources"]["CustodyBucketPolicy"]["Properties"]["PolicyDocument"], values)
    config = {
        "schema": "c5k4-method-v1.5-s3-object-lock-store-config-1.0",
        "status": "PRE_P1_STORE_ADAPTER_NOT_OPERATIONAL", "backend": "AWS_S3_OBJECT_LOCK",
        "bucket": BUCKET, "expected_bucket_owner": ACCOUNT, "region": "ap-south-1",
        "key_prefix": "private/c5k4/v1.5", "kms_key_arn": KEY_ARN,
        "bucket_policy_sha256": module.digest(rendered_bucket_policy),
        "benchmark_horizon_utc": "2027-08-15T00:00:00Z", "retention_through_utc": "2028-08-16T00:00:00Z",
        "required_object_lock_mode": "COMPLIANCE", "put_if_absent": True, "private_only": True,
    }
    config_raw = (json.dumps(config, sort_keys=True, separators=(",", ":")) + "\n").encode()
    evidence["bindings"]["store_config_sha256"] = module.hashlib.sha256(config_raw).hexdigest()
    evidence["stack"] = {
        "stack_id": f"arn:aws:cloudformation:ap-south-1:{ACCOUNT}:stack/c5k4-custody/12345678-1234-1234-1234-123456789abc",
        "status": "CREATE_COMPLETE", "termination_protection": True, "drift_status": "IN_SYNC",
        "deployed_template": template, "state_capture_phase": "AFTER_DESTRUCTIVE_PROBES",
        "resources": [
            {"logical_id": "CustodyBucket", "physical_id": BUCKET, "type": "AWS::S3::Bucket", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
            {"logical_id": "CustodyBucketPolicy", "physical_id": BUCKET, "type": "AWS::S3::BucketPolicy", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
            {"logical_id": "CustodyKey", "physical_id": KEY_ID, "type": "AWS::KMS::Key", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
            {"logical_id": "CustodyWriterPolicy", "physical_id": "c5k4-v1-5-private-custody-single-writer", "type": "AWS::IAM::Policy", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
            {"logical_id": "CustodyWriterRole", "physical_id": "custody-generated-role", "type": "AWS::IAM::Role", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
        ],
    }
    evidence["s3"].update({
        "versioning": {"Status": "Enabled"},
        "object_lock": {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Years": 3}}}},
        "encryption": {"ServerSideEncryptionConfiguration": [{"BucketKeyEnabled": True, "ApplyServerSideEncryptionByDefault": {"KMSMasterKeyID": KEY_ARN, "SSEAlgorithm": "aws:kms"}}]},
        "public_access_block": {"PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "BlockPublicPolicy": True, "IgnorePublicAcls": True, "RestrictPublicBuckets": True}},
        "policy_status": {"PolicyStatus": {"IsPublic": False}}, "policy_document": rendered_bucket_policy,
        "tags": [{"Key": "c5k4:protocol", "Value": "v1.5"}, {"Key": "c5k4:activation", "Value": "PRE-P1"}],
    })
    evidence["kms"] = {
        "metadata": {"AWSAccountId": ACCOUNT, "Arn": KEY_ARN, "KeyId": KEY_ID, "Enabled": True, "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT", "MultiRegion": False, "Origin": "AWS_KMS"},
        "rotation_enabled": True,
        "policy_document": module.render(template["Resources"]["CustodyKey"]["Properties"]["KeyPolicy"], values),
        "tags": [{"TagKey": "c5k4:protocol", "TagValue": "v1.5"}, {"TagKey": "c5k4:activation", "TagValue": "PRE-P1"}],
    }
    evidence["iam"].update({
        "role": {"Arn": ROLE_ARN, "RoleName": "custody-generated-role", "Path": "/c5k4/v1.5/", "MaxSessionDuration": 3600, "PermissionsBoundary": {"PermissionsBoundaryArn": f"arn:aws:iam::{ACCOUNT}:policy/c5k4-v1-5-custody-writer-boundary", "PermissionsBoundaryType": "Policy"}, "Tags": [{"Key": "c5k4:protocol", "Value": "v1.5"}, {"Key": "c5k4:activation", "Value": "PRE-P1"}]},
        "trust_policy_document": module.render(template["Resources"]["CustodyWriterRole"]["Properties"]["AssumeRolePolicyDocument"], values),
        "boundary_policy_document": module.expected_boundary(ACCOUNT),
        "inline_policy_document": module.render(template["Resources"]["CustodyWriterPolicy"]["Properties"]["PolicyDocument"], values),
    })
    operations = [
        ("DELETE_OBJECT", "CUSTODY_WRITER", "AccessDenied"), ("DELETE_OBJECT_VERSION", "CUSTODY_WRITER", "AccessDenied"),
        ("SUSPEND_VERSIONING", "CUSTODY_WRITER", "AccessDenied"), ("CHANGE_OBJECT_LOCK", "CUSTODY_WRITER", "AccessDenied"),
        ("CHANGE_ENCRYPTION", "CUSTODY_WRITER", "AccessDenied"), ("DISABLE_KMS_KEY", "CUSTODY_WRITER", "AccessDeniedException"),
        ("SCHEDULE_KMS_KEY_DELETION", "CUSTODY_WRITER", "AccessDeniedException"), ("PUT_OUTSIDE_PREFIX", "CUSTODY_WRITER", "AccessDenied"),
        ("PUT_AS_NONWRITER", "NON_WRITER_ACCOUNT_PRINCIPAL", "AccessDenied"),
    ]
    evidence["destructive_probes"] = [
        {"operation": op, "caller": caller, "error_code": code, "http_status": 403, "explicit_deny": True, "state_unchanged": True, "aws_request_id": f"REQUESTIDENTIFIER{i:016d}"}
        for i, (op, caller, code) in enumerate(operations)
    ]
    evidence["receipt_sha256"] = module.self_digest(evidence, "receipt_sha256")
    return evidence, config_raw


class ImmutableLiveAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence, self.config_raw = fixture()

    def verify(self, evidence=None, raw=None):
        return module.verify(evidence or self.evidence, raw or self.config_raw)

    @staticmethod
    def reseal(value: dict) -> None:
        value["receipt_sha256"] = module.self_digest(value, "receipt_sha256")

    def test_exact_injected_fixture_verifies_without_becoming_operational(self) -> None:
        proof = self.verify()
        self.assertTrue(proof["verified"])
        self.assertEqual(proof["source"], "INJECTED_TEST_FIXTURE")
        with self.assertRaisesRegex(module.LiveAcceptanceError, "fixture"):
            module.compile_acceptance_bundle(proof)

    def test_compiler_maps_one_receipt_to_both_existing_interfaces(self) -> None:
        proof = self.verify()
        bundle = module.compile_acceptance_bundle(proof, allow_test_fixture=True)
        module.verify_acceptance_bundle(bundle, proof)
        activation = module.infra.load_object(ROOT / "schemas/benchmark-operational-controlled-harness-activation-v1.5.schema.json")
        runner = module.infra.load_object(ROOT / "schemas/benchmark-runner-private-input-assembly-v1.5.schema.json")
        jsonschema.Draft7Validator(
            activation["definitions"]["wormAcceptance"],
            resolver=jsonschema.RefResolver.from_schema(activation),
        ).validate(bundle["activation_worm_acceptance"])
        jsonschema.Draft7Validator(
            runner["properties"]["store_acceptance"],
            resolver=jsonschema.RefResolver.from_schema(runner),
        ).validate(bundle["runner_store_acceptance"])
        self.assertEqual(bundle["store_config_sha256"], bundle["activation_worm_acceptance"]["store_config_sha256"])
        self.assertEqual(bundle["store_config_sha256"], bundle["runner_store_acceptance"]["config_sha256"])
        self.assertEqual(bundle["evidence_receipt_sha256"], bundle["runner_store_acceptance"]["acceptance_receipt_sha256"])

    def test_commitment_receipt_or_config_byte_tampering_fails(self) -> None:
        evidence = copy.deepcopy(self.evidence); evidence["bindings"]["template_sha256"] = "0" * 64; self.reseal(evidence)
        with self.assertRaises(module.LiveAcceptanceError): self.verify(evidence=evidence)
        evidence = copy.deepcopy(self.evidence); evidence["receipt_sha256"] = "0" * 64
        with self.assertRaisesRegex(module.LiveAcceptanceError, "self-digest"): self.verify(evidence=evidence)
        with self.assertRaisesRegex(module.LiveAcceptanceError, "config bytes"): self.verify(raw=self.config_raw + b" ")

    def test_stack_template_identity_retention_and_drift_tampering_fails(self) -> None:
        mutations = []
        value = copy.deepcopy(self.evidence); value["stack"]["termination_protection"] = False; mutations.append(value)
        value = copy.deepcopy(self.evidence); value["stack"]["deployed_template"]["Resources"]["CustodyBucket"]["DeletionPolicy"] = "Delete"; mutations.append(value)
        value = copy.deepcopy(self.evidence); value["stack"]["resources"][0]["physical_id"] = "other-bucket"; mutations.append(value)
        value = copy.deepcopy(self.evidence); value["stack"]["resources"][0]["drift_status"] = "MODIFIED"; mutations.append(value)
        for value in mutations:
            self.reseal(value)
            with self.subTest():
                with self.assertRaises((module.LiveAcceptanceError, jsonschema.ValidationError)): self.verify(evidence=value)

    def test_s3_lock_versioning_encryption_public_policy_and_retention_fail_closed(self) -> None:
        paths = (
            ("versioning", {"Status": "Suspended"}), ("object_lock", {}), ("encryption", {}),
            ("public_access_block", {}), ("policy_status", {"PolicyStatus": {"IsPublic": True}}),
            ("policy_document", {}), ("retention_years", 2),
        )
        for key, value in paths:
            evidence = copy.deepcopy(self.evidence); evidence["s3"][key] = value; self.reseal(evidence)
            with self.subTest(key=key):
                with self.assertRaises((module.LiveAcceptanceError, jsonschema.ValidationError)): self.verify(evidence=evidence)

    def test_kms_identity_rotation_policy_and_tags_fail_closed(self) -> None:
        for key, value in (("metadata", {}), ("rotation_enabled", False), ("policy_document", {}), ("tags", [])):
            evidence = copy.deepcopy(self.evidence); evidence["kms"][key] = value; self.reseal(evidence)
            with self.subTest(key=key):
                with self.assertRaises((module.LiveAcceptanceError, jsonschema.ValidationError)): self.verify(evidence=evidence)

    def test_role_trust_boundary_inline_policy_and_extra_paths_fail_closed(self) -> None:
        cases = (("trust_policy_document", {}), ("boundary_policy_document", {}), ("inline_policy_document", {}), ("attached_policy_arns", ["arn:aws:iam::aws:policy/AdministratorAccess"]))
        for key, value in cases:
            evidence = copy.deepcopy(self.evidence); evidence["iam"][key] = value; self.reseal(evidence)
            with self.subTest(key=key):
                with self.assertRaises((module.LiveAcceptanceError, jsonschema.ValidationError)): self.verify(evidence=evidence)

    def test_every_destructive_probe_is_required_unique_and_state_preserving(self) -> None:
        mutations = []
        value = copy.deepcopy(self.evidence); value["destructive_probes"].pop(); mutations.append(value)
        value = copy.deepcopy(self.evidence); value["destructive_probes"][0]["state_unchanged"] = False; mutations.append(value)
        value = copy.deepcopy(self.evidence); value["destructive_probes"][1]["aws_request_id"] = value["destructive_probes"][0]["aws_request_id"]; mutations.append(value)
        value = copy.deepcopy(self.evidence); value["destructive_probes"][0]["error_code"] = "AccessDeniedException"; mutations.append(value)
        for value in mutations:
            self.reseal(value)
            with self.subTest():
                with self.assertRaises((module.LiveAcceptanceError, jsonschema.ValidationError)): self.verify(evidence=value)

    def test_target_fields_are_rejected_even_when_nested(self) -> None:
        evidence = copy.deepcopy(self.evidence); evidence["s3"]["target_id"] = "hidden"; self.reseal(evidence)
        with self.assertRaises((module.LiveAcceptanceError, jsonschema.ValidationError)): self.verify(evidence=evidence)

    def test_acceptance_bundle_tampering_fails(self) -> None:
        proof = self.verify(); bundle = module.compile_acceptance_bundle(proof, allow_test_fixture=True)
        bundle["activation_worm_acceptance"]["retention_verified"] = False
        with self.assertRaises(module.LiveAcceptanceError): module.verify_acceptance_bundle(bundle, proof)

    def test_cli_verifies_fixture_silently_but_refuses_operational_emit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            evidence_path = Path(temporary) / "evidence.json"; config_path = Path(temporary) / "config.json"
            evidence_path.write_text(json.dumps(self.evidence), encoding="utf-8"); config_path.write_bytes(self.config_raw)
            argv = [sys.executable, str(MODULE_PATH), "--evidence", str(evidence_path), "--store-config", str(config_path)]
            completed = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual((completed.returncode, completed.stdout, completed.stderr), (0, "", ""))
            emitted = subprocess.run(argv + ["--emit-acceptance-bundle"], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual((emitted.returncode, emitted.stdout, emitted.stderr), (2, "", ""))


if __name__ == "__main__":
    unittest.main()
