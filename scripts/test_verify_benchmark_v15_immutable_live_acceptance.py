#!/usr/bin/env python3
"""Adversarial fixture tests for authenticated immutable-store acceptance v1.1."""

from __future__ import annotations

import base64
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_benchmark_v15_immutable_live_acceptance.py"
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("verify_immutable_live_acceptance", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


ACCOUNT = "123456789012"
KEY_ID = "12345678-1234-1234-1234-123456789abc"
BUCKET = "c5k4-custody-generated-012345"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT}:role/c5k4/v1.5/custody-generated-role"
KEY_ARN = f"arn:aws:kms:ap-south-1:{ACCOUNT}:key/{KEY_ID}"
HARNESS_ARN = f"arn:aws:iam::{ACCOUNT}:role/controlled-harness"
EXTERNAL_ID = "fixture_external_id_0123456789abcdef"


def sign(evidence: dict, private_key: Ed25519PrivateKey) -> None:
    receipt = module.receipt_payload_sha256(evidence)
    evidence["receipt_sha256"] = receipt
    evidence["receipt_authentication"]["signed_payload_sha256"] = receipt
    evidence["receipt_authentication"]["signature_base64"] = base64.b64encode(
        private_key.sign(module.receipt_signing_payload(receipt))
    ).decode()


def fixture() -> tuple[dict, bytes, Ed25519PrivateKey, bytes]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    template = module.infra.load_object(module.TEMPLATE)
    plan = module.infra.load_object(module.PLAN)
    evidence = {
        "schema": "c5k4-method-v1.5-immutable-store-live-evidence-1.1",
        "status": "LIVE_ACCEPTANCE_EVIDENCE_CAPTURE", "visibility": "PRIVATE_ACCEPTANCE_EVIDENCE",
        "source": "INJECTED_TEST_FIXTURE", "acquired_at_utc": "2026-08-14T02:00:00Z",
        "account_id": ACCOUNT, "region": "ap-south-1", "receipt_sha256": "0" * 64,
        "receipt_authentication": {
            "schema": "c5k4-method-v1.5-immutable-store-evidence-signature-1.0",
            "signing_key_id": "fixture-key", "signature_algorithm": "Ed25519",
            "verification_key_sha256": module.hashlib.sha256(public_key).hexdigest(),
            "signed_payload_sha256": "0" * 64, "signature_base64": base64.b64encode(b"\0" * 64).decode(),
        },
        "bindings": {"template_sha256": plan["template_sha256"], **plan["commitments"], "store_config_sha256": "0" * 64},
        "resource_identities": {"bucket": BUCKET, "kms_key_id": KEY_ID, "kms_key_arn": KEY_ARN, "writer_role_arn": ROLE_ARN, "writer_policy_name": "c5k4-v1-5-private-custody-single-writer"},
        "iam": {"trusted_harness_principal_arn": HARNESS_ARN, "trusted_harness_external_id": EXTERNAL_ID, "role": {}, "trust_policy_document": {}, "boundary_policy_document": {}, "inline_policy_document": {}, "inline_policy_names": ["c5k4-v1-5-private-custody-single-writer"], "attached_policy_arns": []},
        "s3": {
            "retention_years": 3,
            "probe_canary": {"key": "private/c5k4/v1.5/acceptance/immutable-store-canary", "version_id": "fixture-version-id", "sha256": module.digest("fixture-canary"), "retain_until_utc": "2029-08-14T02:00:00Z", "exists": True, "delete_marker_present": False},
        },
        "kms": {}, "stack": {}, "destructive_probes": [], "target_specific": False,
    }
    values = module.substitutions(evidence)
    rendered_bucket_policy = module.render(template["Resources"]["CustodyBucketPolicy"]["Properties"]["PolicyDocument"], values)
    config = {"schema": "c5k4-method-v1.5-s3-object-lock-store-config-1.0", "status": "PRE_P1_STORE_ADAPTER_NOT_OPERATIONAL", "backend": "AWS_S3_OBJECT_LOCK", "bucket": BUCKET, "expected_bucket_owner": ACCOUNT, "region": "ap-south-1", "key_prefix": "private/c5k4/v1.5", "kms_key_arn": KEY_ARN, "bucket_policy_sha256": module.digest(rendered_bucket_policy), "benchmark_horizon_utc": "2027-08-15T00:00:00Z", "retention_through_utc": "2028-08-16T00:00:00Z", "required_object_lock_mode": "COMPLIANCE", "put_if_absent": True, "private_only": True}
    config_raw = (json.dumps(config, sort_keys=True, separators=(",", ":")) + "\n").encode()
    evidence["bindings"]["store_config_sha256"] = module.hashlib.sha256(config_raw).hexdigest()
    evidence["stack"] = {"stack_id": f"arn:aws:cloudformation:ap-south-1:{ACCOUNT}:stack/c5k4-custody/12345678-1234-1234-1234-123456789abc", "status": "CREATE_COMPLETE", "termination_protection": True, "drift_status": "IN_SYNC", "deployed_template": template, "state_capture_phase": "AFTER_DESTRUCTIVE_PROBES", "resources": [
        {"logical_id": "CustodyBucket", "physical_id": BUCKET, "type": "AWS::S3::Bucket", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
        {"logical_id": "CustodyBucketPolicy", "physical_id": BUCKET, "type": "AWS::S3::BucketPolicy", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
        {"logical_id": "CustodyKey", "physical_id": KEY_ID, "type": "AWS::KMS::Key", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
        {"logical_id": "CustodyWriterPolicy", "physical_id": "c5k4-v1-5-private-custody-single-writer", "type": "AWS::IAM::Policy", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"},
        {"logical_id": "CustodyWriterRole", "physical_id": "custody-generated-role", "type": "AWS::IAM::Role", "status": "CREATE_COMPLETE", "drift_status": "IN_SYNC"}]}
    evidence["s3"].update({"versioning": {"Status": "Enabled"}, "object_lock": {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Years": 3}}}}, "encryption": {"ServerSideEncryptionConfiguration": [{"BucketKeyEnabled": True, "ApplyServerSideEncryptionByDefault": {"KMSMasterKeyID": KEY_ARN, "SSEAlgorithm": "aws:kms"}}]}, "public_access_block": {"PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "BlockPublicPolicy": True, "IgnorePublicAcls": True, "RestrictPublicBuckets": True}}, "policy_status": {"PolicyStatus": {"IsPublic": False}}, "policy_document": rendered_bucket_policy, "tags": [{"Key": "c5k4:protocol", "Value": "v1.5"}, {"Key": "c5k4:activation", "Value": "PRE-P1"}]})
    evidence["kms"] = {"metadata": {"AWSAccountId": ACCOUNT, "Arn": KEY_ARN, "KeyId": KEY_ID, "Enabled": True, "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT", "KeySpec": "SYMMETRIC_DEFAULT", "MultiRegion": False, "Origin": "AWS_KMS"}, "rotation_enabled": True, "policy_document": module.render(template["Resources"]["CustodyKey"]["Properties"]["KeyPolicy"], values), "tags": [{"TagKey": "c5k4:protocol", "TagValue": "v1.5"}, {"TagKey": "c5k4:activation", "TagValue": "PRE-P1"}]}
    evidence["iam"].update({"role": {"Arn": ROLE_ARN, "RoleName": "custody-generated-role", "Path": "/c5k4/v1.5/", "MaxSessionDuration": 3600, "PermissionsBoundary": {"PermissionsBoundaryArn": f"arn:aws:iam::{ACCOUNT}:policy/c5k4-v1-5-custody-writer-boundary", "PermissionsBoundaryType": "Policy"}, "Tags": [{"Key": "c5k4:protocol", "Value": "v1.5"}, {"Key": "c5k4:activation", "Value": "PRE-P1"}]}, "trust_policy_document": module.render(template["Resources"]["CustodyWriterRole"]["Properties"]["AssumeRolePolicyDocument"], values), "boundary_policy_document": module.expected_boundary(ACCOUNT), "inline_policy_document": module.render(template["Resources"]["CustodyWriterPolicy"]["Properties"]["PolicyDocument"], values)})
    state = module.probe_state(evidence)
    for index, (operation, (caller, api, parameters)) in enumerate(module.expected_probe_requests(evidence).items()):
        request = {"service": api.split(":", 1)[0].upper(), "api": api, "caller": caller, "parameters": parameters}
        result = {"Error": {"Code": "AccessDeniedException" if api.startswith("kms:") else "AccessDenied", "Message": "explicit deny by frozen policy"}, "ResponseMetadata": {"HTTPStatusCode": 400 if api.startswith("kms:") else 403, "RequestId": f"REQUESTIDENTIFIER{index:016d}"}}
        evidence["destructive_probes"].append({"operation": operation, "caller": caller, "request": request, "request_sha256": module.digest(request), "result": result, "result_sha256": module.digest(result), "pre_state": copy.deepcopy(state), "pre_state_sha256": module.digest(state), "post_state": copy.deepcopy(state), "post_state_sha256": module.digest(state)})
    sign(evidence, private_key)
    return evidence, config_raw, private_key, public_key


class ImmutableLiveAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence, self.config_raw, self.private_key, self.public_key = fixture()

    def verify(self, evidence=None, raw=None, key=None):
        return module.verify(evidence or self.evidence, raw or self.config_raw, key or self.public_key)

    def reseal(self, value: dict) -> None:
        sign(value, self.private_key)

    def test_exact_signed_fixture_verifies_but_cannot_compile_operationally(self) -> None:
        proof = self.verify()
        self.assertTrue(proof["signature_authenticated"])
        self.assertEqual(proof["source"], "INJECTED_TEST_FIXTURE")
        with self.assertRaisesRegex(module.LiveAcceptanceError, "fixture"):
            module.compile_activation_worm_acceptance(proof)
        with self.assertRaisesRegex(module.LiveAcceptanceError, "fixture"):
            module.compile_runner_store_acceptance(proof, self.public_key, "a" * 40, "p1.json")

    def test_v11_source_and_signature_contract_are_explicit(self) -> None:
        self.assertEqual(self.evidence["schema"], "c5k4-method-v1.5-immutable-store-live-evidence-1.1")
        schema = module.infra.load_object(module.EVIDENCE_SCHEMA)
        self.assertEqual(schema["properties"]["source"]["enum"], ["AWS_MIXED_READ_PROBE_CAPTURE", "INJECTED_TEST_FIXTURE"])
        self.assertNotIn("AWS_CLI_READONLY_CAPTURE", json.dumps(schema))

    def test_signature_key_payload_or_algorithm_tampering_fails(self) -> None:
        other = Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        with self.assertRaisesRegex(module.LiveAcceptanceError, "another verification key"):
            self.verify(key=other)
        value = copy.deepcopy(self.evidence); value["receipt_authentication"]["signature_base64"] = base64.b64encode(b"x" * 64).decode()
        with self.assertRaisesRegex(module.LiveAcceptanceError, "signature"):
            self.verify(evidence=value)
        value = copy.deepcopy(self.evidence); value["receipt_authentication"]["signature_algorithm"] = "RSA"
        with self.assertRaises(module.LiveAcceptanceError): self.verify(evidence=value)

    def test_each_raw_request_result_and_digest_is_authenticated(self) -> None:
        for field in ("request", "request_sha256", "result", "result_sha256"):
            value = copy.deepcopy(self.evidence)
            if isinstance(value["destructive_probes"][0][field], dict): value["destructive_probes"][0][field]["tampered"] = True
            else: value["destructive_probes"][0][field] = "0" * 64
            self.reseal(value)
            with self.subTest(field=field):
                with self.assertRaises(module.LiveAcceptanceError): self.verify(evidence=value)

    def test_pre_post_state_content_and_digests_are_recomputed(self) -> None:
        for field in ("pre_state", "pre_state_sha256", "post_state", "post_state_sha256"):
            value = copy.deepcopy(self.evidence)
            if isinstance(value["destructive_probes"][0][field], dict): value["destructive_probes"][0][field]["s3_sha256"] = "0" * 64
            else: value["destructive_probes"][0][field] = "0" * 64
            self.reseal(value)
            with self.subTest(field=field):
                with self.assertRaises(module.LiveAcceptanceError): self.verify(evidence=value)

    def test_denial_code_http_request_id_and_probe_closure_fail_closed(self) -> None:
        mutations = []
        value = copy.deepcopy(self.evidence); value["destructive_probes"][0]["result"]["Error"]["Code"] = "Success"; value["destructive_probes"][0]["result_sha256"] = module.digest(value["destructive_probes"][0]["result"]); mutations.append(value)
        value = copy.deepcopy(self.evidence); value["destructive_probes"][0]["result"]["ResponseMetadata"]["HTTPStatusCode"] = 200; value["destructive_probes"][0]["result_sha256"] = module.digest(value["destructive_probes"][0]["result"]); mutations.append(value)
        value = copy.deepcopy(self.evidence); value["destructive_probes"].pop(); mutations.append(value)
        for value in mutations:
            self.reseal(value)
            with self.assertRaises(module.LiveAcceptanceError): self.verify(evidence=value)

    def test_store_stack_s3_kms_iam_and_target_tampering_still_fail(self) -> None:
        cases = []
        for section, key, changed in (("stack", "termination_protection", False), ("s3", "versioning", {"Status": "Suspended"}), ("kms", "rotation_enabled", False), ("iam", "attached_policy_arns", ["admin"])):
            value = copy.deepcopy(self.evidence); value[section][key] = changed; cases.append(value)
        value = copy.deepcopy(self.evidence); value["s3"]["target_id"] = "forbidden"; cases.append(value)
        for value in cases:
            self.reseal(value)
            with self.assertRaises(module.LiveAcceptanceError): self.verify(evidence=value)

    def test_p1_authority_requires_exact_four_roles_and_operational_key(self) -> None:
        commitment = {"schema": "c5k4-method-v1.5-operational-noninterference-key-commitment-1.0", "status": "FROZEN_P1_NONINTERFERENCE_KEY_COMMITTED", "protocol_version": "1.5", "host_id": "ai-vps-controlled-harness", "signing_key_id": "fixture-key", "signature_algorithm": "Ed25519", "verification_key_sha256": module.hashlib.sha256(self.public_key).hexdigest(), "operational": True, "activation_permitted": True, "target_specific": False}
        commitment["commitment_sha256"] = module.digest(commitment)
        schema_path = ROOT / "schemas/benchmark-operational-noninterference-key-commitment-v1.5.schema.json"
        blobs = {"key.json": json.dumps(commitment).encode(), "key-schema.json": schema_path.read_bytes(), "verifier.py": MODULE_PATH.read_bytes(), "evidence-schema.json": module.EVIDENCE_SCHEMA.read_bytes()}
        roles = []
        mapping = {"immutable_live_acceptance_verifier": "verifier.py", "immutable_live_acceptance_evidence_schema": "evidence-schema.json", "noninterference_key_commitment": "key.json", "operational_noninterference_key_commitment_schema": "key-schema.json"}
        for role, path in mapping.items(): roles.append({"closure": "NATIVE_V1_5", "role": role, "path": path, "sha256": module.hashlib.sha256(blobs[path]).hexdigest()})
        resolution = {"status": "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE", "operational": True, "p1": {"p1t_commit": "a" * 40}, "resolution_sha256": "b" * 64, "resolved_roles": roles}
        # Exact production paths are additionally required for executable/schema roles.
        roles[0]["path"] = MODULE_PATH.relative_to(ROOT).as_posix(); blobs[roles[0]["path"]] = MODULE_PATH.read_bytes()
        roles[1]["path"] = module.EVIDENCE_SCHEMA.relative_to(ROOT).as_posix(); blobs[roles[1]["path"]] = module.EVIDENCE_SCHEMA.read_bytes()
        authority = module.authorize_p1_resolution(resolution, self.public_key, reader=lambda path: blobs[path])
        self.assertEqual(authority["signing_key_id"], "fixture-key")
        bad = copy.deepcopy(resolution); bad["resolved_roles"] = bad["resolved_roles"][:-1]
        with self.assertRaisesRegex(module.LiveAcceptanceError, "omits"): module.authorize_p1_resolution(bad, self.public_key, reader=lambda path: blobs[path])

    def test_runner_public_compiler_invokes_nonoverridable_p1_resolver(self) -> None:
        proof = self.verify(); proof = {**proof, "source": "AWS_MIXED_READ_PROBE_CAPTURE"}
        with mock.patch.object(module.p1_roles, "resolve_published_roles", side_effect=RuntimeError("no P1")) as resolver:
            with self.assertRaisesRegex(module.LiveAcceptanceError, "P1 role resolution"):
                module.compile_runner_store_acceptance(proof, self.public_key, "a" * 40, "p1.json")
        resolver.assert_called_once_with(module.ROOT, "a" * 40, "p1.json")

    def test_existing_output_shapes_remain_exact_under_pure_mapping(self) -> None:
        proof = self.verify()
        activation = module._activation_acceptance(proof); runner = module._runner_acceptance(proof)
        activation_schema = module.infra.load_object(ROOT / "schemas/benchmark-operational-controlled-harness-activation-v1.5.schema.json")
        runner_schema = module.infra.load_object(ROOT / "schemas/benchmark-runner-private-input-assembly-v1.5.schema.json")
        jsonschema.Draft7Validator(activation_schema["definitions"]["wormAcceptance"], resolver=jsonschema.RefResolver.from_schema(activation_schema)).validate(activation)
        jsonschema.Draft7Validator(runner_schema["properties"]["store_acceptance"], resolver=jsonschema.RefResolver.from_schema(runner_schema)).validate(runner)

    def test_cli_verifies_fixture_silently_and_refuses_both_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); evidence = root / "evidence.json"; config = root / "config.json"; key = root / "key.raw"
            evidence.write_text(json.dumps(self.evidence)); config.write_bytes(self.config_raw); key.write_bytes(self.public_key)
            argv = [sys.executable, str(MODULE_PATH), "--evidence", str(evidence), "--store-config", str(config), "--verification-key", str(key)]
            completed = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
            self.assertEqual((completed.returncode, completed.stdout, completed.stderr), (0, "", ""))
            for flag in ("--emit-activation-acceptance", "--emit-runner-acceptance"):
                result = subprocess.run(argv + [flag], cwd=ROOT, text=True, capture_output=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (2, "", ""))


if __name__ == "__main__":
    unittest.main()
