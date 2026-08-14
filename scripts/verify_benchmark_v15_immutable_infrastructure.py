#!/usr/bin/env python3
"""Static, target-blind PRE-P1 acceptance for the immutable AWS plan.

The verifier parses only committed JSON.  It imports no AWS SDK, reads no
environment credentials, performs no network operation, and cannot create or
modify a CloudFormation stack.  Success certifies an inert plan, never a live
store or permission to activate the benchmark.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "infra" / "benchmark-v1.5" / "immutable-store" / "plan.json"
TEMPLATE = ROOT / "infra" / "benchmark-v1.5" / "immutable-store" / "cloudformation.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class InfrastructurePlanError(ValueError):
    """The inert infrastructure plan fails the static safety closure."""


def _pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise InfrastructurePlanError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise InfrastructurePlanError(f"{path}: expected one JSON object")
    return value


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_keys(value: Mapping[str, Any], expected: Iterable[str], label: str) -> None:
    if set(value) != set(expected):
        raise InfrastructurePlanError(f"{label} fields are not exact")


def statements(policy: Mapping[str, Any], label: str) -> dict[str, dict[str, Any]]:
    if policy.get("Version") != "2012-10-17" or not isinstance(policy.get("Statement"), list):
        raise InfrastructurePlanError(f"{label} is not an exact IAM policy document")
    result: dict[str, dict[str, Any]] = {}
    for row in policy["Statement"]:
        if not isinstance(row, dict) or not isinstance(row.get("Sid"), str) or row["Sid"] in result:
            raise InfrastructurePlanError(f"{label} statement identifiers are absent or ambiguous")
        result[row["Sid"]] = row
    return result


def actions(row: Mapping[str, Any]) -> set[str]:
    value = row.get("Action")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    raise InfrastructurePlanError("policy action set is malformed")


def verify_policy_forms(
    rows: Mapping[str, Mapping[str, Any]], *, allowed_not_resource: set[str] | None = None
) -> None:
    allowed = allowed_not_resource or set()
    for sid, row in rows.items():
        if "NotAction" in row:
            raise InfrastructurePlanError("NotAction is forbidden in every policy")
        if "NotResource" in row and sid not in allowed:
            raise InfrastructurePlanError("NotResource is forbidden outside the exact prefix deny")
        if row.get("Effect") == "Allow" and "NotResource" in row:
            raise InfrastructurePlanError("Allow with NotResource is forbidden")


def _walk(value: object) -> Iterable[tuple[str | None, object]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield None, child
            yield from _walk(child)


def verify_target_blind(template: Mapping[str, Any], plan: Mapping[str, Any]) -> None:
    forbidden_fields = {
        "target", "target_id", "target_identity", "selected_target", "cluster_id",
        "conjecture", "conjecture_id", "statement_text", "record_id", "record_url",
        "repository_target", "registry_record",
    }
    for key, _ in _walk({"template": template, "plan": plan}):
        if key is not None and key.lower() in forbidden_fields:
            raise InfrastructurePlanError("plan contains a target-identity field")
    if plan.get("target_identity_fields") != [] or plan.get("cloudformation_outputs") != []:
        raise InfrastructurePlanError("plan exposes an output or target identity")
    if "Outputs" in template:
        raise InfrastructurePlanError("CloudFormation outputs are forbidden")
    for name in template.get("Parameters", {}):
        if any(token in name.lower() for token in ("target", "cluster", "conjecture", "record")):
            raise InfrastructurePlanError("CloudFormation parameter can carry a target identity")


def verify_plan(plan: Mapping[str, Any], template_path: Path, template: Mapping[str, Any]) -> None:
    exact_keys(plan, (
        "schema", "status", "activation_permitted", "aws_api_calls_permitted",
        "deployment_executed", "template", "template_sha256", "commitments",
        "resource_logical_ids", "cloudformation_outputs", "target_identity_fields",
        "acceptance", "remaining_external_prerequisites",
    ), "plan")
    if plan["schema"] != "c5k4-method-v1.5-immutable-infrastructure-plan-1.0":
        raise InfrastructurePlanError("plan schema identifier differs")
    if plan["status"] != "PRE_P1_INFRASTRUCTURE_PLAN_NOT_DEPLOYED":
        raise InfrastructurePlanError("plan is not PRE-P1 and inert")
    for key in ("activation_permitted", "aws_api_calls_permitted", "deployment_executed"):
        if plan[key] is not False:
            raise InfrastructurePlanError(f"{key} must remain false")
    if plan["template"] != "infra/benchmark-v1.5/immutable-store/cloudformation.json":
        raise InfrastructurePlanError("template path is not exact")
    if plan["template_sha256"] != file_digest(template_path):
        raise InfrastructurePlanError("template bytes differ from committed digest")
    commitments = plan["commitments"]
    exact_keys(commitments, ("kms_key_policy_sha256", "bucket_policy_sha256", "writer_policy_sha256"), "commitments")
    if any(not isinstance(value, str) or not SHA256.fullmatch(value) for value in commitments.values()):
        raise InfrastructurePlanError("policy commitment is not a SHA-256 digest")
    resources = template.get("Resources", {})
    expected_ids = ["CustodyBucket", "CustodyBucketPolicy", "CustodyKey", "CustodyWriterPolicy", "CustodyWriterRole"]
    if plan["resource_logical_ids"] != expected_ids or sorted(resources) != expected_ids:
        raise InfrastructurePlanError("resource closure is not exact")
    acceptance = plan["acceptance"]
    exact_keys(acceptance, (
        "cloudformation_native", "generated_physical_names", "kms_key_retained",
        "object_lock_compliance", "bucket_retained", "versioning_enabled",
        "public_access_blocked", "destructive_mutation_denied", "single_writer_role",
        "exact_sse_kms_required", "target_blind", "operationally_accepted",
    ), "acceptance")
    if any(acceptance[key] is not True for key in acceptance if key != "operationally_accepted"):
        raise InfrastructurePlanError("static acceptance flags are incomplete")
    if acceptance["operationally_accepted"] is not False:
        raise InfrastructurePlanError("an inert plan cannot claim operational acceptance")
    if plan["remaining_external_prerequisites"] != [
        "ACCOUNT_SCOPED_PERMISSIONS_BOUNDARY_EXISTS",
        "FRESH_PRIVATE_AWS_ACCOUNT_OR_EQUIVALENT_BOUNDARY",
        "LIVE_STACK_ACCEPTANCE_NOT_RUN",
        "BROKER_CREDENTIAL_DELIVERY_NOT_CONFIGURED",
        "DESTRUCTIVE_GAP_TESTS_NOT_RUN",
        "P1_NOT_FROZEN",
    ]:
        raise InfrastructurePlanError("external prerequisites are not exact")
    if commitments["kms_key_policy_sha256"] != digest(resources["CustodyKey"]["Properties"]["KeyPolicy"]):
        raise InfrastructurePlanError("KMS key policy differs from exact commitment")
    if commitments["bucket_policy_sha256"] != digest(resources["CustodyBucketPolicy"]["Properties"]["PolicyDocument"]):
        raise InfrastructurePlanError("bucket policy differs from exact commitment")
    if commitments["writer_policy_sha256"] != digest(resources["CustodyWriterPolicy"]["Properties"]["PolicyDocument"]):
        raise InfrastructurePlanError("writer policy differs from exact commitment")


def verify_cloudformation(template: Mapping[str, Any]) -> None:
    exact_keys(template, ("AWSTemplateFormatVersion", "Description", "Parameters", "Resources"), "template")
    if template["AWSTemplateFormatVersion"] != "2010-09-09":
        raise InfrastructurePlanError("CloudFormation version is not pinned")
    if not isinstance(template["Description"], str) or "inert until separately deployed and accepted" not in template["Description"]:
        raise InfrastructurePlanError("template does not declare inert status")
    for key, child in _walk(template):
        if key in {"Transform", "Fn::ImportValue"}:
            raise InfrastructurePlanError("macros and cross-stack imports are forbidden")
        if key == "Type" and isinstance(child, str) and (child.startswith("Custom::") or child == "AWS::CloudFormation::Stack"):
            raise InfrastructurePlanError("custom and nested resources are forbidden")

    parameters = template["Parameters"]
    exact_keys(parameters, ("HarnessPrincipalArn", "HarnessExternalId", "PrivatePrefix", "RetentionYears"), "parameters")
    if parameters["HarnessPrincipalArn"].get("NoEcho") is not True or parameters["HarnessExternalId"].get("NoEcho") is not True:
        raise InfrastructurePlanError("harness trust parameters are not NoEcho")
    if parameters["HarnessExternalId"].get("MinLength", 0) < 32:
        raise InfrastructurePlanError("external ID is too short")
    prefix = parameters["PrivatePrefix"]
    if prefix != {"Type": "String", "Default": "private/c5k4/v1.5", "AllowedPattern": "^private/c5k4/v1\\.5$"}:
        raise InfrastructurePlanError("private prefix is not exact")
    retention = parameters["RetentionYears"]
    if retention != {"Type": "Number", "Default": 3, "MinValue": 3, "MaxValue": 10}:
        raise InfrastructurePlanError("retention bounds are not exact")

    resources = template["Resources"]
    expected_types = {
        "CustodyBucket": "AWS::S3::Bucket",
        "CustodyBucketPolicy": "AWS::S3::BucketPolicy",
        "CustodyKey": "AWS::KMS::Key",
        "CustodyWriterPolicy": "AWS::IAM::Policy",
        "CustodyWriterRole": "AWS::IAM::Role",
    }
    if {name: row.get("Type") for name, row in resources.items()} != expected_types:
        raise InfrastructurePlanError("resource types are not exact and native")
    for name, row in resources.items():
        if row.get("DeletionPolicy") != "Retain" or row.get("UpdateReplacePolicy") != "Retain":
            raise InfrastructurePlanError(f"{name} is not retained across deletion/replacement")
        props = row.get("Properties")
        if not isinstance(props, dict):
            raise InfrastructurePlanError(f"{name} properties are malformed")
        if any(field in props for field in ("BucketName", "RoleName", "KeyId", "AliasName")):
            raise InfrastructurePlanError("physical resource names must remain generated")

    verify_role(resources["CustodyWriterRole"]["Properties"])
    verify_key(resources["CustodyKey"]["Properties"])
    verify_bucket(resources["CustodyBucket"]["Properties"])
    verify_bucket_policy(resources["CustodyBucketPolicy"]["Properties"])
    verify_writer_policy(resources["CustodyWriterPolicy"]["Properties"])


def verify_role(role: Mapping[str, Any]) -> None:
    exact_keys(role, ("AssumeRolePolicyDocument", "MaxSessionDuration", "Path", "PermissionsBoundary", "Tags"), "writer role")
    if role["MaxSessionDuration"] != 3600 or role["Path"] != "/c5k4/v1.5/":
        raise InfrastructurePlanError("writer role duration or path is not exact")
    if role["PermissionsBoundary"] != {"Fn::Sub": "arn:${AWS::Partition}:iam::${AWS::AccountId}:policy/c5k4-v1-5-custody-writer-boundary"}:
        raise InfrastructurePlanError("writer role lacks the exact account boundary")
    if role["Tags"] != [
        {"Key": "c5k4:protocol", "Value": "v1.5"},
        {"Key": "c5k4:activation", "Value": "PRE-P1"},
    ]:
        raise InfrastructurePlanError("writer role tags are not exact PRE-P1 tags")
    trust = statements(role["AssumeRolePolicyDocument"], "writer trust")
    verify_policy_forms(trust)
    if set(trust) != {"OnlyControlledHarness"}:
        raise InfrastructurePlanError("writer trust has another principal path")
    row = trust["OnlyControlledHarness"]
    if row != {
        "Sid": "OnlyControlledHarness", "Effect": "Allow",
        "Principal": {"AWS": {"Ref": "HarnessPrincipalArn"}}, "Action": "sts:AssumeRole",
        "Condition": {"StringEquals": {"sts:ExternalId": {"Ref": "HarnessExternalId"}}},
    }:
        raise InfrastructurePlanError("writer trust is not exact")


def verify_key(key: Mapping[str, Any]) -> None:
    exact_keys(key, ("BypassPolicyLockoutSafetyCheck", "Description", "EnableKeyRotation", "KeySpec", "KeyUsage", "MultiRegion", "KeyPolicy", "Tags"), "KMS key")
    if key["BypassPolicyLockoutSafetyCheck"] is not True:
        raise InfrastructurePlanError("immutable KMS policy requires explicit lockout-safety bypass")
    if (key["EnableKeyRotation"], key["KeySpec"], key["KeyUsage"], key["MultiRegion"]) != (True, "SYMMETRIC_DEFAULT", "ENCRYPT_DECRYPT", False):
        raise InfrastructurePlanError("KMS key cryptographic closure differs")
    if key["Tags"] != [
        {"TagKey": "c5k4:protocol", "TagValue": "v1.5"},
        {"TagKey": "c5k4:activation", "TagValue": "PRE-P1"},
    ]:
        raise InfrastructurePlanError("KMS key tags are not exact PRE-P1 tags")
    rows = statements(key["KeyPolicy"], "KMS key policy")
    verify_policy_forms(rows)
    if set(rows) != {"DenyKeyDestruction", "AccountReadOnlyAdministration", "SingleWriterCryptography"}:
        raise InfrastructurePlanError("KMS key policy statements are not exact")
    deny = rows["DenyKeyDestruction"]
    if deny.get("Effect") != "Deny" or deny.get("Principal") != "*" or deny.get("Resource") != "*" or actions(deny) != {"kms:DisableKey", "kms:ScheduleKeyDeletion"} or "Condition" in deny:
        raise InfrastructurePlanError("KMS destruction is not unconditionally denied")
    admin = rows["AccountReadOnlyAdministration"]
    allowed_admin = {"kms:DescribeKey", "kms:EnableKeyRotation", "kms:GetKeyPolicy", "kms:GetKeyRotationStatus", "kms:ListResourceTags", "kms:TagResource", "kms:UntagResource"}
    if admin.get("Effect") != "Allow" or actions(admin) != allowed_admin or admin.get("Principal") != {"AWS": {"Fn::Sub": "arn:${AWS::Partition}:iam::${AWS::AccountId}:root"}}:
        raise InfrastructurePlanError("KMS account administration is broader than exact non-destructive actions")
    writer = rows["SingleWriterCryptography"]
    crypt = {"kms:Decrypt", "kms:DescribeKey", "kms:Encrypt", "kms:GenerateDataKey"}
    if writer.get("Effect") != "Allow" or actions(writer) != crypt or writer.get("Principal") != {"AWS": {"Fn::GetAtt": ["CustodyWriterRole", "Arn"]}} or writer.get("Condition") != {"StringEquals": {"kms:ViaService": {"Fn::Sub": "s3.${AWS::Region}.${AWS::URLSuffix}"}}}:
        raise InfrastructurePlanError("KMS cryptographic use is not confined to the single writer via S3")


def verify_bucket(bucket: Mapping[str, Any]) -> None:
    exact_keys(bucket, ("BucketEncryption", "ObjectLockEnabled", "ObjectLockConfiguration", "OwnershipControls", "PublicAccessBlockConfiguration", "VersioningConfiguration", "Tags"), "bucket")
    if bucket["ObjectLockEnabled"] is not True or bucket["ObjectLockConfiguration"] != {"ObjectLockEnabled": "Enabled", "Rule": {"DefaultRetention": {"Mode": "COMPLIANCE", "Years": {"Ref": "RetentionYears"}}}}:
        raise InfrastructurePlanError("Object Lock COMPLIANCE retention is not exact")
    if bucket["VersioningConfiguration"] != {"Status": "Enabled"}:
        raise InfrastructurePlanError("bucket versioning is not enabled")
    if bucket["OwnershipControls"] != {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}:
        raise InfrastructurePlanError("bucket ownership is not enforced")
    if bucket["PublicAccessBlockConfiguration"] != {"BlockPublicAcls": True, "BlockPublicPolicy": True, "IgnorePublicAcls": True, "RestrictPublicBuckets": True}:
        raise InfrastructurePlanError("public access block is incomplete")
    expected_encryption = {"ServerSideEncryptionConfiguration": [{"BucketKeyEnabled": True, "ServerSideEncryptionByDefault": {"KMSMasterKeyID": {"Fn::GetAtt": ["CustodyKey", "Arn"]}, "SSEAlgorithm": "aws:kms"}}]}
    if bucket["BucketEncryption"] != expected_encryption:
        raise InfrastructurePlanError("bucket encryption is not the exact custody KMS key")
    if bucket["Tags"] != [
        {"Key": "c5k4:protocol", "Value": "v1.5"},
        {"Key": "c5k4:activation", "Value": "PRE-P1"},
    ]:
        raise InfrastructurePlanError("bucket tags are not exact PRE-P1 tags")


def verify_bucket_policy(props: Mapping[str, Any]) -> None:
    exact_keys(props, ("Bucket", "PolicyDocument"), "bucket policy resource")
    if props["Bucket"] != {"Ref": "CustodyBucket"}:
        raise InfrastructurePlanError("bucket policy is bound elsewhere")
    rows = statements(props["PolicyDocument"], "bucket policy")
    verify_policy_forms(rows, allowed_not_resource={"DenyWritesOutsidePrivatePrefix"})
    required = {"DenyInsecureTransport", "DenyDestructiveMutation", "DenyWritesOutsidePrivatePrefix", "DenyWritesOutsideSingleWriter", "DenyWrongEncryptionAlgorithm", "DenyWrongEncryptionKey", "DenyNonComplianceWrites"}
    if set(rows) != required:
        raise InfrastructurePlanError("bucket policy statement closure is not exact")
    destructive = rows["DenyDestructiveMutation"]
    destructive_actions = {"s3:DeleteBucket", "s3:DeleteObject", "s3:DeleteObjectVersion", "s3:PutBucketVersioning", "s3:PutEncryptionConfiguration", "s3:PutObjectLockConfiguration"}
    if destructive.get("Effect") != "Deny" or destructive.get("Principal") != "*" or actions(destructive) != destructive_actions or "Condition" in destructive:
        raise InfrastructurePlanError("destructive S3 mutation is not unconditionally denied")
    outside = rows["DenyWritesOutsidePrivatePrefix"]
    if outside != {
        "Sid": "DenyWritesOutsidePrivatePrefix", "Effect": "Deny", "Principal": "*",
        "Action": ["s3:PutObject", "s3:PutObjectRetention"],
        "NotResource": {"Fn::Sub": "${CustodyBucket.Arn}/${PrivatePrefix}/*"},
    }:
        raise InfrastructurePlanError("writes outside the private prefix are not universally denied")
    writer = rows["DenyWritesOutsideSingleWriter"]
    if writer.get("Effect") != "Deny" or writer.get("Principal") != "*" or actions(writer) != {"s3:PutObject", "s3:PutObjectRetention"} or writer.get("Condition") != {"StringNotEquals": {"aws:PrincipalArn": {"Fn::GetAtt": ["CustodyWriterRole", "Arn"]}}}:
        raise InfrastructurePlanError("bucket writes are not confined to the single writer")
    if rows["DenyInsecureTransport"].get("Condition") != {"Bool": {"aws:SecureTransport": "false"}}:
        raise InfrastructurePlanError("insecure transport is not denied")
    if rows["DenyWrongEncryptionAlgorithm"].get("Condition") != {"StringNotEquals": {"s3:x-amz-server-side-encryption": "aws:kms"}}:
        raise InfrastructurePlanError("non-KMS writes are not denied")
    if rows["DenyWrongEncryptionKey"].get("Condition") != {"ArnNotEquals": {"s3:x-amz-server-side-encryption-aws-kms-key-id": {"Fn::GetAtt": ["CustodyKey", "Arn"]}}}:
        raise InfrastructurePlanError("wrong KMS-key writes are not denied")
    if rows["DenyNonComplianceWrites"].get("Condition") != {"StringNotEquals": {"s3:x-amz-object-lock-mode": "COMPLIANCE"}}:
        raise InfrastructurePlanError("non-COMPLIANCE writes are not denied")
    for row in rows.values():
        if row.get("Effect") != "Deny" or row.get("Principal") != "*":
            raise InfrastructurePlanError("bucket policy may contain only universal denies")


def verify_writer_policy(props: Mapping[str, Any]) -> None:
    exact_keys(props, ("PolicyName", "Roles", "PolicyDocument"), "writer policy resource")
    if props["PolicyName"] != "c5k4-v1-5-private-custody-single-writer" or props["Roles"] != [{"Ref": "CustodyWriterRole"}]:
        raise InfrastructurePlanError("writer policy can attach to more than one role")
    rows = statements(props["PolicyDocument"], "writer policy")
    verify_policy_forms(rows)
    if set(rows) != {"InspectExactBucketGuards", "ListPrivateVersions", "WriteAndVerifyImmutableVersions", "UseExactCustodyKeyViaS3"}:
        raise InfrastructurePlanError("writer permissions are not exact")
    allowed = {
        "s3:GetBucketEncryption", "s3:GetBucketLocation", "s3:GetBucketObjectLockConfiguration",
        "s3:GetBucketPolicy", "s3:GetBucketPolicyStatus", "s3:GetBucketPublicAccessBlock",
        "s3:GetBucketVersioning", "s3:ListBucket", "s3:ListBucketVersions",
        "s3:GetObject", "s3:GetObjectRetention", "s3:GetObjectVersion", "s3:PutObject",
        "s3:PutObjectRetention", "kms:Decrypt", "kms:DescribeKey", "kms:Encrypt", "kms:GenerateDataKey",
    }
    observed: set[str] = set()
    for row in rows.values():
        if row.get("Effect") != "Allow" or "Principal" in row:
            raise InfrastructurePlanError("writer policy contains a non-allow or principal")
        observed |= actions(row)
    if observed != allowed or any("Delete" in action or action.endswith(":*") for action in observed):
        raise InfrastructurePlanError("writer permissions exceed the least-privilege action closure")
    inspect = rows["InspectExactBucketGuards"]
    inspect_actions = {
        "s3:GetBucketEncryption", "s3:GetBucketLocation", "s3:GetBucketObjectLockConfiguration",
        "s3:GetBucketPolicy", "s3:GetBucketPolicyStatus", "s3:GetBucketPublicAccessBlock",
        "s3:GetBucketVersioning",
    }
    bucket_arn = {"Fn::GetAtt": ["CustodyBucket", "Arn"]}
    if actions(inspect) != inspect_actions or inspect.get("Resource") != bucket_arn or "Condition" in inspect:
        raise InfrastructurePlanError("bucket guard inspection permissions are not exact")
    listing = rows["ListPrivateVersions"]
    if actions(listing) != {"s3:ListBucket", "s3:ListBucketVersions"} or listing.get("Resource") != bucket_arn or listing.get("Condition") != {"StringLike": {"s3:prefix": [{"Fn::Sub": "${PrivatePrefix}/*"}]}}:
        raise InfrastructurePlanError("bucket listing escapes the private prefix")
    if rows["UseExactCustodyKeyViaS3"].get("Resource") != {"Fn::GetAtt": ["CustodyKey", "Arn"]}:
        raise InfrastructurePlanError("writer can use another KMS key")
    if rows["UseExactCustodyKeyViaS3"].get("Condition") != {"StringEquals": {"kms:ViaService": {"Fn::Sub": "s3.${AWS::Region}.${AWS::URLSuffix}"}}}:
        raise InfrastructurePlanError("writer KMS access is not confined to S3")
    if rows["WriteAndVerifyImmutableVersions"].get("Resource") != {"Fn::Sub": "${CustodyBucket.Arn}/${PrivatePrefix}/*"}:
        raise InfrastructurePlanError("writer object permissions escape the private prefix")


def verify(plan: Mapping[str, Any], template: Mapping[str, Any], template_path: Path = TEMPLATE) -> dict[str, Any]:
    verify_target_blind(template, plan)
    verify_cloudformation(template)
    verify_plan(plan, template_path, template)
    return {
        "valid": True,
        "status": "PRE_P1_INFRASTRUCTURE_PLAN_NOT_DEPLOYED",
        "target_blind": True,
        "aws_api_calls_made": 0,
        "deployment_executed": False,
        "operationally_accepted": False,
        "activation_permitted": False,
        "template_sha256": plan["template_sha256"],
        "commitments": plan["commitments"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--emit-summary", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = verify(load_object(args.plan), load_object(args.template), args.template)
    except (InfrastructurePlanError, OSError, json.JSONDecodeError, KeyError, TypeError):
        return 2
    if args.emit_summary:
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
