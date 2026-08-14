#!/usr/bin/env python3
"""Verify private AWS evidence and compile the two existing WORM interfaces.

This module is deliberately an offline consumer.  It has no AWS SDK import and
never invokes AWS CLI.  A future private acquisition step must supply the exact
responses described by the evidence schema.  Injected fixtures can exercise
verification, but cannot be emitted as operational acceptance by the CLI.
"""

from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import verify_benchmark_v15_immutable_infrastructure as infra
import resolve_benchmark_v15_p1_roles as p1_roles


ROOT = Path(__file__).resolve().parents[1]
SLICE = ROOT / "infra" / "benchmark-v1.5" / "immutable-store"
EVIDENCE_SCHEMA = SLICE / "live-acceptance-evidence.schema.json"
STORE_CONFIG_SCHEMA = ROOT / "schemas" / "benchmark-s3-object-lock-store-config-v1.5.schema.json"
PLAN = SLICE / "plan.json"
TEMPLATE = SLICE / "cloudformation.json"
TARGET_FIELDS = {"target", "target_id", "target_identity", "cluster_id", "conjecture", "conjecture_id", "statement_text", "record_id"}
SIGNATURE_DOMAIN = b"c5k4-method-v1.5-immutable-live-evidence-1.1\0"


class LiveAcceptanceError(ValueError):
    """Live evidence or its deterministic acceptance mapping is invalid."""


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def self_digest(value: Mapping[str, Any], field: str) -> str:
    return digest({key: child for key, child in value.items() if key != field})


def receipt_payload_sha256(value: Mapping[str, Any]) -> str:
    unsigned = copy.deepcopy(dict(value))
    unsigned.pop("receipt_sha256", None)
    authentication = unsigned.get("receipt_authentication")
    if not isinstance(authentication, dict):
        raise LiveAcceptanceError("receipt authentication is absent")
    authentication.pop("signed_payload_sha256", None)
    authentication.pop("signature_base64", None)
    return digest(unsigned)


def receipt_signing_payload(receipt_sha256: str) -> bytes:
    try:
        raw = bytes.fromhex(receipt_sha256)
    except ValueError as exc:
        raise LiveAcceptanceError("receipt digest is malformed") from exc
    if len(raw) != 32:
        raise LiveAcceptanceError("receipt digest is malformed")
    return SIGNATURE_DOMAIN + raw


def verify_receipt_signature(value: Mapping[str, Any], verification_key: bytes) -> None:
    if not isinstance(verification_key, bytes) or len(verification_key) != 32:
        raise LiveAcceptanceError("receipt verification key must be raw Ed25519 bytes")
    authentication = value["receipt_authentication"]
    expected = receipt_payload_sha256(value)
    if value["receipt_sha256"] != expected or authentication["signed_payload_sha256"] != expected:
        raise LiveAcceptanceError("authenticated receipt payload digest mismatch")
    if authentication["verification_key_sha256"] != hashlib.sha256(verification_key).hexdigest():
        raise LiveAcceptanceError("receipt is bound to another verification key")
    try:
        signature = base64.b64decode(authentication["signature_base64"], validate=True)
        if len(signature) != 64:
            raise ValueError("wrong signature length")
        Ed25519PublicKey.from_public_bytes(verification_key).verify(
            signature, receipt_signing_payload(expected)
        )
    except (InvalidSignature, ValueError) as exc:
        raise LiveAcceptanceError("receipt Ed25519 signature is invalid") from exc


def parse_utc(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise LiveAcceptanceError("invalid UTC timestamp") from exc


def add_years(value: datetime, years: int) -> datetime:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years)


def validate_schema(value: object, path: Path, label: str) -> None:
    schema = infra.load_object(path)
    try:
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.ValidationError as exc:
        raise LiveAcceptanceError(f"{label} schema failure: {exc.message}") from exc


def reject_target_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in TARGET_FIELDS:
                raise LiveAcceptanceError("live evidence contains a target-identity field")
            reject_target_fields(child)
    elif isinstance(value, list):
        for child in value:
            reject_target_fields(child)


def role_name(role_arn: str) -> str:
    marker = ":role/c5k4/v1.5/"
    if marker not in role_arn:
        raise LiveAcceptanceError("writer role ARN does not retain the exact path")
    return role_arn.split(marker, 1)[1]


def substitutions(evidence: Mapping[str, Any]) -> dict[str, object]:
    ids = evidence["resource_identities"]
    account = evidence["account_id"]
    prefix = "private/c5k4/v1.5"
    return {
        "AWS::Partition": "aws", "AWS::AccountId": account,
        "AWS::Region": "ap-south-1", "AWS::URLSuffix": "amazonaws.com",
        "HarnessPrincipalArn": evidence["iam"]["trusted_harness_principal_arn"],
        "HarnessExternalId": evidence["iam"]["trusted_harness_external_id"],
        "PrivatePrefix": prefix, "RetentionYears": evidence["s3"]["retention_years"],
        "CustodyBucket": ids["bucket"], "CustodyKey": ids["kms_key_id"],
        "CustodyWriterRole": role_name(ids["writer_role_arn"]),
        "CustodyBucket.Arn": f"arn:aws:s3:::{ids['bucket']}",
        "CustodyKey.Arn": ids["kms_key_arn"], "CustodyWriterRole.Arn": ids["writer_role_arn"],
    }


def render(value: object, values: Mapping[str, object]) -> object:
    if isinstance(value, list):
        return [render(child, values) for child in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {"Ref"}:
        name = value["Ref"]
        if name not in values:
            raise LiveAcceptanceError(f"unresolved Ref in committed template: {name}")
        return values[name]
    if set(value) == {"Fn::GetAtt"}:
        parts = value["Fn::GetAtt"]
        if not isinstance(parts, list) or len(parts) != 2 or parts[1] != "Arn":
            raise LiveAcceptanceError("unsupported GetAtt in committed template")
        name = f"{parts[0]}.Arn"
        if name not in values:
            raise LiveAcceptanceError(f"unresolved GetAtt in committed template: {name}")
        return values[name]
    if set(value) == {"Fn::Sub"}:
        text = value["Fn::Sub"]
        if not isinstance(text, str):
            raise LiveAcceptanceError("unsupported Fn::Sub form")
        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            if name not in values:
                raise LiveAcceptanceError(f"unresolved Fn::Sub in committed template: {name}")
            return str(values[name])
        return re.sub(r"\$\{([^}]+)\}", replace, text)
    return {key: render(child, values) for key, child in value.items()}


def expected_boundary(account: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowExactImmutableCustodyOperations", "Effect": "Allow", "Resource": "*",
                "Action": sorted({
                    "s3:GetBucketEncryption", "s3:GetBucketLocation", "s3:GetBucketObjectLockConfiguration",
                    "s3:GetBucketPolicy", "s3:GetBucketPolicyStatus", "s3:GetBucketPublicAccessBlock",
                    "s3:GetBucketVersioning", "s3:ListBucket", "s3:ListBucketVersions", "s3:GetObject",
                    "s3:GetObjectRetention", "s3:GetObjectVersion", "s3:PutObject", "s3:PutObjectRetention",
                    "kms:Decrypt", "kms:DescribeKey", "kms:Encrypt", "kms:GenerateDataKey",
                }),
            },
            {
                "Sid": "DenyDestructiveCustodyOperations", "Effect": "Deny", "Principal": "*", "Resource": "*",
                "Action": [
                    "kms:DisableKey", "kms:ScheduleKeyDeletion", "s3:DeleteBucket", "s3:DeleteObject",
                    "s3:DeleteObjectVersion", "s3:PutBucketVersioning", "s3:PutEncryptionConfiguration",
                    "s3:PutObjectLockConfiguration",
                ],
            },
        ],
    }


def verify_stack(evidence: Mapping[str, Any], template: Mapping[str, Any]) -> None:
    stack = evidence["stack"]
    account = evidence["account_id"]
    if f":{account}:stack/" not in stack["stack_id"]:
        raise LiveAcceptanceError("stack ARN account differs")
    if stack["deployed_template"] != template:
        raise LiveAcceptanceError("deployed stack template differs from committed template")
    ids = evidence["resource_identities"]
    expected = {
        "CustodyBucket": (ids["bucket"], "AWS::S3::Bucket"),
        "CustodyBucketPolicy": (ids["bucket"], "AWS::S3::BucketPolicy"),
        "CustodyKey": (ids["kms_key_id"], "AWS::KMS::Key"),
        "CustodyWriterPolicy": (ids["writer_policy_name"], "AWS::IAM::Policy"),
        "CustodyWriterRole": (role_name(ids["writer_role_arn"]), "AWS::IAM::Role"),
    }
    observed: dict[str, tuple[str, str]] = {}
    for row in stack["resources"]:
        if row["logical_id"] in observed:
            raise LiveAcceptanceError("duplicate stack resource identity")
        if row["status"] not in {"CREATE_COMPLETE", "UPDATE_COMPLETE"} or row["drift_status"] != "IN_SYNC":
            raise LiveAcceptanceError("stack resource is incomplete or drifted")
        observed[row["logical_id"]] = (row["physical_id"], row["type"])
    if observed != expected:
        raise LiveAcceptanceError("deployed resource identities differ from exact stack closure")


def verify_s3(evidence: Mapping[str, Any], template: Mapping[str, Any], store: Mapping[str, Any]) -> None:
    s3 = evidence["s3"]
    ids = evidence["resource_identities"]
    values = substitutions(evidence)
    if s3["versioning"] != {"Status": "Enabled"}:
        raise LiveAcceptanceError("live bucket versioning is not enabled")
    retention = {"ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Years": s3["retention_years"]}}}}
    if s3["object_lock"] != retention or not isinstance(s3["retention_years"], int) or not 3 <= s3["retention_years"] <= 10:
        raise LiveAcceptanceError("live Object Lock COMPLIANCE retention differs")
    encryption = {"ServerSideEncryptionConfiguration": [{"BucketKeyEnabled": True, "ApplyServerSideEncryptionByDefault": {"KMSMasterKeyID": ids["kms_key_arn"], "SSEAlgorithm": "aws:kms"}}]}
    if s3["encryption"] != encryption:
        raise LiveAcceptanceError("live bucket encryption differs from exact KMS key")
    blocks = {"PublicAccessBlockConfiguration": {"BlockPublicAcls": True, "BlockPublicPolicy": True, "IgnorePublicAcls": True, "RestrictPublicBuckets": True}}
    if s3["public_access_block"] != blocks or s3["policy_status"] != {"PolicyStatus": {"IsPublic": False}}:
        raise LiveAcceptanceError("live bucket is not provably private")
    expected_policy = render(template["Resources"]["CustodyBucketPolicy"]["Properties"]["PolicyDocument"], values)
    if s3["policy_document"] != expected_policy or store["bucket_policy_sha256"] != digest(expected_policy):
        raise LiveAcceptanceError("live bucket policy differs from committed rendered policy")
    if s3["tags"] != [{"Key": "c5k4:protocol", "Value": "v1.5"}, {"Key": "c5k4:activation", "Value": "PRE-P1"}]:
        raise LiveAcceptanceError("live bucket tags differ")
    canary = s3["probe_canary"]
    if canary["exists"] is not True or canary["delete_marker_present"] is not False:
        raise LiveAcceptanceError("retained acceptance canary is absent or delete-marked")
    if parse_utc(canary["retain_until_utc"]) < parse_utc(store["retention_through_utc"]):
        raise LiveAcceptanceError("acceptance canary retention does not cover store horizon")
    acquired = parse_utc(evidence["acquired_at_utc"])
    if add_years(acquired, s3["retention_years"]) < parse_utc(store["retention_through_utc"]):
        raise LiveAcceptanceError("live default retention does not cover store horizon")


def verify_kms(evidence: Mapping[str, Any], template: Mapping[str, Any]) -> None:
    kms = evidence["kms"]
    ids = evidence["resource_identities"]
    expected_metadata = {
        "AWSAccountId": evidence["account_id"], "Arn": ids["kms_key_arn"], "KeyId": ids["kms_key_id"],
        "Enabled": True, "KeyState": "Enabled", "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT", "MultiRegion": False, "Origin": "AWS_KMS",
    }
    if kms["metadata"] != expected_metadata or kms["rotation_enabled"] is not True:
        raise LiveAcceptanceError("live KMS key identity/state/rotation differs")
    expected_policy = render(template["Resources"]["CustodyKey"]["Properties"]["KeyPolicy"], substitutions(evidence))
    if kms["policy_document"] != expected_policy:
        raise LiveAcceptanceError("live KMS policy differs from committed rendered policy")
    if kms["tags"] != [{"TagKey": "c5k4:protocol", "TagValue": "v1.5"}, {"TagKey": "c5k4:activation", "TagValue": "PRE-P1"}]:
        raise LiveAcceptanceError("live KMS tags differ")


def verify_iam(evidence: Mapping[str, Any], template: Mapping[str, Any]) -> None:
    iam = evidence["iam"]
    ids = evidence["resource_identities"]
    account = evidence["account_id"]
    boundary_arn = f"arn:aws:iam::{account}:policy/c5k4-v1-5-custody-writer-boundary"
    expected_role = {
        "Arn": ids["writer_role_arn"], "RoleName": role_name(ids["writer_role_arn"]),
        "Path": "/c5k4/v1.5/", "MaxSessionDuration": 3600,
        "PermissionsBoundary": {"PermissionsBoundaryArn": boundary_arn, "PermissionsBoundaryType": "Policy"},
        "Tags": [{"Key": "c5k4:protocol", "Value": "v1.5"}, {"Key": "c5k4:activation", "Value": "PRE-P1"}],
    }
    if iam["role"] != expected_role:
        raise LiveAcceptanceError("live writer role identity/boundary/tags differ")
    values = substitutions(evidence)
    expected_trust = render(template["Resources"]["CustodyWriterRole"]["Properties"]["AssumeRolePolicyDocument"], values)
    expected_inline = render(template["Resources"]["CustodyWriterPolicy"]["Properties"]["PolicyDocument"], values)
    if iam["trust_policy_document"] != expected_trust:
        raise LiveAcceptanceError("live writer trust differs")
    if iam["inline_policy_document"] != expected_inline:
        raise LiveAcceptanceError("live writer inline policy differs")
    if iam["boundary_policy_document"] != expected_boundary(account):
        raise LiveAcceptanceError("live permissions boundary differs from exact maximum")
    if iam["inline_policy_names"] != [ids["writer_policy_name"]] or iam["attached_policy_arns"] != []:
        raise LiveAcceptanceError("writer role has additional policy paths")


def probe_state(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "c5k4-method-v1.5-immutable-store-probe-state-1.0",
        "stack_sha256": digest(evidence["stack"]),
        "s3_sha256": digest(evidence["s3"]),
        "kms_sha256": digest(evidence["kms"]),
        "iam_sha256": digest(evidence["iam"]),
    }


def expected_probe_requests(evidence: Mapping[str, Any]) -> dict[str, tuple[str, str, dict[str, Any]]]:
    ids = evidence["resource_identities"]
    canary = evidence["s3"]["probe_canary"]
    bucket = ids["bucket"]
    return {
        "DELETE_OBJECT": ("CUSTODY_WRITER", "s3:DeleteObject", {"Bucket": bucket, "Key": canary["key"]}),
        "DELETE_OBJECT_VERSION": ("CUSTODY_WRITER", "s3:DeleteObject", {"Bucket": bucket, "Key": canary["key"], "VersionId": canary["version_id"]}),
        "SUSPEND_VERSIONING": ("CUSTODY_WRITER", "s3:PutBucketVersioning", {"Bucket": bucket, "VersioningConfiguration": {"Status": "Suspended"}}),
        "CHANGE_OBJECT_LOCK": ("CUSTODY_WRITER", "s3:PutObjectLockConfiguration", {"Bucket": bucket, "ObjectLockConfiguration": {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "GOVERNANCE", "Years": 1}}}}),
        "CHANGE_ENCRYPTION": ("CUSTODY_WRITER", "s3:PutBucketEncryption", {"Bucket": bucket, "ServerSideEncryptionConfiguration": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}),
        "DISABLE_KMS_KEY": ("CUSTODY_WRITER", "kms:DisableKey", {"KeyId": ids["kms_key_arn"]}),
        "SCHEDULE_KMS_KEY_DELETION": ("CUSTODY_WRITER", "kms:ScheduleKeyDeletion", {"KeyId": ids["kms_key_arn"], "PendingWindowInDays": 7}),
        "PUT_OUTSIDE_PREFIX": ("CUSTODY_WRITER", "s3:PutObject", {"Bucket": bucket, "Key": "acceptance/outside-private-prefix-canary", "BodySHA256": canary["sha256"]}),
        "PUT_AS_NONWRITER": ("NON_WRITER_ACCOUNT_PRINCIPAL", "s3:PutObject", {"Bucket": bucket, "Key": "private/c5k4/v1.5/acceptance/nonwriter-canary", "BodySHA256": canary["sha256"]}),
    }


def verify_probes(evidence: Mapping[str, Any]) -> None:
    expected = expected_probe_requests(evidence)
    expected_state = probe_state(evidence)
    observed: set[str] = set()
    request_ids: set[str] = set()
    for row in evidence["destructive_probes"]:
        operation = row["operation"]
        if operation in observed or operation not in expected:
            raise LiveAcceptanceError("duplicate or unknown destructive probe")
        observed.add(operation)
        caller, api, parameters = expected[operation]
        request = row["request"]
        if request != {"service": api.split(":", 1)[0].upper(), "api": api, "caller": caller, "parameters": parameters} or row["caller"] != caller:
            raise LiveAcceptanceError("destructive probe raw request differs from exact operation")
        if row["request_sha256"] != digest(request):
            raise LiveAcceptanceError("destructive probe request digest mismatch")
        result = row["result"]
        code = "AccessDeniedException" if api.startswith("kms:") else "AccessDenied"
        if set(result) != {"Error", "ResponseMetadata"}:
            raise LiveAcceptanceError("destructive probe raw result shape differs")
        error = result["Error"]
        metadata = result["ResponseMetadata"]
        if set(error) != {"Code", "Message"} or error["Code"] != code or not isinstance(error["Message"], str) or not 1 <= len(error["Message"]) <= 4096:
            raise LiveAcceptanceError("destructive probe did not return exact access denial")
        expected_status = 400 if api.startswith("kms:") else 403
        if set(metadata) != {"HTTPStatusCode", "RequestId"} or metadata["HTTPStatusCode"] != expected_status or not re.fullmatch(r"[A-Za-z0-9-]{16,128}", str(metadata["RequestId"])):
            raise LiveAcceptanceError("destructive probe response metadata differs")
        if metadata["RequestId"] in request_ids:
            raise LiveAcceptanceError("destructive probes reuse an AWS request ID")
        request_ids.add(metadata["RequestId"])
        if row["result_sha256"] != digest(result):
            raise LiveAcceptanceError("destructive probe result digest mismatch")
        for phase in ("pre", "post"):
            if row[f"{phase}_state"] != expected_state or row[f"{phase}_state_sha256"] != digest(row[f"{phase}_state"]):
                raise LiveAcceptanceError("destructive probe state transcript differs")
        if row["pre_state_sha256"] != row["post_state_sha256"]:
            raise LiveAcceptanceError("destructive mutation changed authenticated state")
    if observed != set(expected):
        raise LiveAcceptanceError("destructive probe closure is incomplete")


def verify_store_config(evidence: Mapping[str, Any], raw: bytes) -> dict[str, Any]:
    try:
        store = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LiveAcceptanceError("store config is not JSON") from exc
    validate_schema(store, STORE_CONFIG_SCHEMA, "store config")
    if hashlib.sha256(raw).hexdigest() != evidence["bindings"]["store_config_sha256"]:
        raise LiveAcceptanceError("store config bytes differ from evidence binding")
    ids = evidence["resource_identities"]
    if store["bucket"] != ids["bucket"] or store["expected_bucket_owner"] != evidence["account_id"] or store["region"] != evidence["region"] or store["key_prefix"] != "private/c5k4/v1.5" or store["kms_key_arn"] != ids["kms_key_arn"]:
        raise LiveAcceptanceError("store config differs from deployed identities")
    return store


def verify(evidence: Mapping[str, Any], store_config_raw: bytes, verification_key: bytes) -> dict[str, Any]:
    validate_schema(evidence, EVIDENCE_SCHEMA, "live evidence")
    reject_target_fields(evidence)
    verify_receipt_signature(evidence, verification_key)
    plan = infra.load_object(PLAN)
    template = infra.load_object(TEMPLATE)
    infra.verify(plan, template)
    expected_bindings = {
        "template_sha256": plan["template_sha256"],
        **plan["commitments"],
        "store_config_sha256": evidence["bindings"]["store_config_sha256"],
    }
    if evidence["bindings"] != expected_bindings:
        raise LiveAcceptanceError("live evidence differs from committed infrastructure commitments")
    store = verify_store_config(evidence, store_config_raw)
    verify_stack(evidence, template)
    verify_s3(evidence, template, store)
    verify_kms(evidence, template)
    verify_iam(evidence, template)
    verify_probes(evidence)
    return {
        "verified": True, "source": evidence["source"],
        "signature_authenticated": True,
        "signing_key_id": evidence["receipt_authentication"]["signing_key_id"],
        "verification_key_sha256": evidence["receipt_authentication"]["verification_key_sha256"],
        "template_sha256": plan["template_sha256"],
        "store_config_sha256": evidence["bindings"]["store_config_sha256"],
        "evidence_receipt_sha256": evidence["receipt_sha256"],
        "retention_through_utc": store["retention_through_utc"],
    }


def _require_live_proof(proof: Mapping[str, Any]) -> None:
    if proof.get("verified") is not True or proof.get("signature_authenticated") is not True:
        raise LiveAcceptanceError("acceptance compiler requires signature-authenticated evidence")
    if proof.get("source") != "AWS_MIXED_READ_PROBE_CAPTURE":
        raise LiveAcceptanceError("injected fixture cannot produce operational acceptance")


def _activation_acceptance(proof: Mapping[str, Any]) -> dict[str, Any]:
    worm = {
        "schema": "c5k4-method-v1.5-operational-worm-acceptance-1.0",
        "status": "OPERATIONAL_WORM_ACCEPTANCE_PASSED",
        "store_config_sha256": proof["store_config_sha256"], "object_lock_mode": "COMPLIANCE",
        "versioning_enabled": True, "retention_verified": True, "destructive_write_rejected": True,
        "operational": True, "activation_permitted": True,
    }
    worm["acceptance_sha256"] = digest(worm)
    return worm


def compile_activation_worm_acceptance(proof: Mapping[str, Any]) -> dict[str, Any]:
    """Compile PRE-P1 activation readiness from a real signed live receipt."""
    _require_live_proof(proof)
    return _activation_acceptance(proof)


def _runner_acceptance(proof: Mapping[str, Any]) -> dict[str, Any]:
    runner = {
        "schema": "c5k4-method-v1.5-worm-store-acceptance-1.0",
        "status": "FROZEN_P1_WORM_STORE_ACCEPTED", "operational": True,
        "backend": "AWS_S3_OBJECT_LOCK", "config_sha256": proof["store_config_sha256"],
        "acceptance_receipt_sha256": proof["evidence_receipt_sha256"],
        "retention_through_utc": proof["retention_through_utc"], "private_only": True,
    }
    runner["acceptance_sha256"] = digest(runner)
    return runner


def authorize_p1_resolution(
    resolution: Mapping[str, Any], verification_key: bytes,
    reader: Any = None,
) -> dict[str, Any]:
    """Prove the exact live verifier/schema/key commitment selected by P1."""
    if resolution.get("status") != "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE" or resolution.get("operational") is not True:
        raise LiveAcceptanceError("P1 role resolution is not authenticated and operational")
    rows = {
        (row.get("closure"), row.get("role")): row
        for row in resolution.get("resolved_roles", []) if isinstance(row, dict)
    }
    required = {
        "immutable_live_acceptance_verifier",
        "immutable_live_acceptance_evidence_schema",
        "noninterference_key_commitment",
        "operational_noninterference_key_commitment_schema",
    }
    if any(("NATIVE_V1_5", role) not in rows for role in required):
        raise LiveAcceptanceError("P1 omits an immutable-acceptance authority role")
    read = reader or (lambda path: (ROOT / path).read_bytes())
    def role_bytes(role: str) -> bytes:
        row = rows[("NATIVE_V1_5", role)]
        raw = read(row["path"])
        if not isinstance(raw, bytes) or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise LiveAcceptanceError(f"P1 role bytes differ for {role}")
        return raw
    verifier_row = rows[("NATIVE_V1_5", "immutable_live_acceptance_verifier")]
    schema_row = rows[("NATIVE_V1_5", "immutable_live_acceptance_evidence_schema")]
    if verifier_row["path"] != Path(__file__).resolve().relative_to(ROOT).as_posix() or role_bytes("immutable_live_acceptance_verifier") != Path(__file__).resolve().read_bytes():
        raise LiveAcceptanceError("executing acceptance verifier differs from P1")
    if schema_row["path"] != EVIDENCE_SCHEMA.relative_to(ROOT).as_posix() or role_bytes("immutable_live_acceptance_evidence_schema") != EVIDENCE_SCHEMA.read_bytes():
        raise LiveAcceptanceError("executing acceptance schema differs from P1")
    commitment_raw = role_bytes("noninterference_key_commitment")
    commitment_schema_raw = role_bytes("operational_noninterference_key_commitment_schema")
    try:
        commitment = json.loads(commitment_raw)
        commitment_schema = json.loads(commitment_schema_raw)
        jsonschema.Draft7Validator(commitment_schema).validate(commitment)
    except (UnicodeDecodeError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        raise LiveAcceptanceError("P1 key commitment is not exact operational JSON") from exc
    if commitment["commitment_sha256"] != digest({key: value for key, value in commitment.items() if key != "commitment_sha256"}):
        raise LiveAcceptanceError("P1 key commitment self-digest mismatch")
    if not isinstance(verification_key, bytes) or len(verification_key) != 32 or commitment["verification_key_sha256"] != hashlib.sha256(verification_key).hexdigest():
        raise LiveAcceptanceError("P1 key commitment selects another Ed25519 key")
    return {
        "p1t_commit": resolution["p1"]["p1t_commit"],
        "resolution_sha256": resolution["resolution_sha256"],
        "signing_key_id": commitment["signing_key_id"],
        "verification_key_sha256": commitment["verification_key_sha256"],
    }


def compile_runner_store_acceptance(
    proof: Mapping[str, Any], verification_key: bytes, p1t_commit: str, p1t_path: str,
) -> dict[str, Any]:
    """Compile FROZEN_P1 runner acceptance only through published P1 roles."""
    _require_live_proof(proof)
    try:
        resolution = p1_roles.resolve_published_roles(ROOT, p1t_commit, p1t_path)
    except Exception as exc:
        raise LiveAcceptanceError("published P1 role resolution failed") from exc
    authority = authorize_p1_resolution(resolution, verification_key)
    if authority["signing_key_id"] != proof["signing_key_id"] or authority["verification_key_sha256"] != proof["verification_key_sha256"]:
        raise LiveAcceptanceError("P1 key commitment differs from signed evidence")
    return _runner_acceptance(proof)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--store-config", type=Path, required=True)
    parser.add_argument("--verification-key", type=Path, required=True)
    outputs = parser.add_mutually_exclusive_group()
    outputs.add_argument("--emit-activation-acceptance", action="store_true")
    outputs.add_argument("--emit-runner-acceptance", action="store_true")
    parser.add_argument("--p1t-commit")
    parser.add_argument("--p1t-path")
    args = parser.parse_args(argv)
    try:
        verification_key = args.verification_key.read_bytes()
        proof = verify(infra.load_object(args.evidence), args.store_config.read_bytes(), verification_key)
        output = None
        if args.emit_activation_acceptance:
            output = compile_activation_worm_acceptance(proof)
        elif args.emit_runner_acceptance:
            if not args.p1t_commit or not args.p1t_path:
                raise LiveAcceptanceError("runner acceptance requires exact P1T inputs")
            output = compile_runner_store_acceptance(proof, verification_key, args.p1t_commit, args.p1t_path)
        if output is not None:
            print(json.dumps(output, sort_keys=True, separators=(",", ":")))
    except (LiveAcceptanceError, infra.InfrastructurePlanError, OSError, json.JSONDecodeError, KeyError, TypeError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
