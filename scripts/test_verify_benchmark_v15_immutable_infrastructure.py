#!/usr/bin/env python3
"""Adversarial static tests for the inert immutable-infrastructure plan."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "verify_benchmark_v15_immutable_infrastructure.py"
SPEC = importlib.util.spec_from_file_location("verify_immutable_infrastructure", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class ImmutableInfrastructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = module.load_object(module.PLAN)
        self.template = module.load_object(module.TEMPLATE)

    def verify(self, plan=None, template=None):
        return module.verify(plan or self.plan, template or self.template)

    def statement(self, template, resource: str, policy: str, sid: str):
        rows = template["Resources"][resource]["Properties"][policy]["Statement"]
        return next(row for row in rows if row["Sid"] == sid)

    def test_exact_plan_is_valid_but_inert(self) -> None:
        result = self.verify()
        self.assertTrue(result["valid"])
        self.assertTrue(result["target_blind"])
        self.assertEqual(result["aws_api_calls_made"], 0)
        self.assertFalse(result["deployment_executed"])
        self.assertFalse(result["operationally_accepted"])
        self.assertFalse(result["activation_permitted"])

    def test_activation_deployment_or_api_permission_claim_fails(self) -> None:
        for key in ("activation_permitted", "deployment_executed", "aws_api_calls_permitted"):
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan); plan[key] = True
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(plan=plan)
        plan = copy.deepcopy(self.plan); plan["acceptance"]["operationally_accepted"] = True
        with self.assertRaises(module.InfrastructurePlanError):
            self.verify(plan=plan)

    def test_target_identity_fields_outputs_or_parameters_fail(self) -> None:
        cases = []
        plan = copy.deepcopy(self.plan); plan["target_identity_fields"] = ["target_id"]
        cases.append((plan, self.template))
        template = copy.deepcopy(self.template); template["Outputs"] = {"Bucket": {"Value": {"Ref": "CustodyBucket"}}}
        cases.append((self.plan, template))
        template = copy.deepcopy(self.template); template["Parameters"]["ConjectureId"] = {"Type": "String"}
        cases.append((self.plan, template))
        for plan, template in cases:
            with self.subTest():
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(plan=plan, template=template)

    def test_template_digest_and_all_policy_commitments_are_exact(self) -> None:
        for key in ("template_sha256",):
            plan = copy.deepcopy(self.plan); plan[key] = "0" * 64
            with self.assertRaises(module.InfrastructurePlanError):
                self.verify(plan=plan)
        for key in self.plan["commitments"]:
            with self.subTest(key=key):
                plan = copy.deepcopy(self.plan); plan["commitments"][key] = "0" * 64
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(plan=plan)

    def test_duplicate_json_keys_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"status":"PRE_P1","status":"ACTIVE"}', encoding="utf-8")
            with self.assertRaisesRegex(module.InfrastructurePlanError, "duplicate"):
                module.load_object(path)

    def test_non_native_custom_nested_or_imported_resource_fails(self) -> None:
        mutations = []
        template = copy.deepcopy(self.template); template["Resources"]["Extra"] = {"Type": "Custom::Provision", "Properties": {}}
        mutations.append(template)
        template = copy.deepcopy(self.template); template["Resources"]["Extra"] = {"Type": "AWS::CloudFormation::Stack", "Properties": {}}
        mutations.append(template)
        template = copy.deepcopy(self.template); template["Resources"]["CustodyBucket"]["Properties"]["Tag"] = {"Fn::ImportValue": "foreign"}
        mutations.append(template)
        for template in mutations:
            with self.subTest():
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_physical_bucket_role_or_alias_names_fail(self) -> None:
        for resource, key, value in (
            ("CustodyBucket", "BucketName", "predictable"),
            ("CustodyWriterRole", "RoleName", "predictable"),
            ("CustodyKey", "AliasName", "alias/predictable"),
        ):
            with self.subTest(resource=resource):
                template = copy.deepcopy(self.template)
                template["Resources"][resource]["Properties"][key] = value
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_every_resource_must_be_retained(self) -> None:
        for resource in self.template["Resources"]:
            for policy in ("DeletionPolicy", "UpdateReplacePolicy"):
                with self.subTest(resource=resource, policy=policy):
                    template = copy.deepcopy(self.template)
                    template["Resources"][resource][policy] = "Delete"
                    with self.assertRaisesRegex(module.InfrastructurePlanError, "retained"):
                        self.verify(template=template)

    def test_object_lock_must_be_compliance_with_three_year_floor(self) -> None:
        template = copy.deepcopy(self.template)
        template["Resources"]["CustodyBucket"]["Properties"]["ObjectLockConfiguration"]["Rule"]["DefaultRetention"]["Mode"] = "GOVERNANCE"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "COMPLIANCE"):
            self.verify(template=template)
        template = copy.deepcopy(self.template); template["Parameters"]["RetentionYears"]["MinValue"] = 1
        with self.assertRaisesRegex(module.InfrastructurePlanError, "retention"):
            self.verify(template=template)

    def test_versioning_ownership_and_all_public_blocks_are_required(self) -> None:
        template = copy.deepcopy(self.template); template["Resources"]["CustodyBucket"]["Properties"]["VersioningConfiguration"]["Status"] = "Suspended"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "versioning"):
            self.verify(template=template)
        template = copy.deepcopy(self.template); template["Resources"]["CustodyBucket"]["Properties"]["OwnershipControls"]["Rules"][0]["ObjectOwnership"] = "ObjectWriter"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "ownership"):
            self.verify(template=template)
        for key in ("BlockPublicAcls", "BlockPublicPolicy", "IgnorePublicAcls", "RestrictPublicBuckets"):
            template = copy.deepcopy(self.template); template["Resources"]["CustodyBucket"]["Properties"]["PublicAccessBlockConfiguration"][key] = False
            with self.assertRaisesRegex(module.InfrastructurePlanError, "public"):
                self.verify(template=template)

    def test_bucket_encryption_must_use_only_exact_kms_key(self) -> None:
        encryption = self.template["Resources"]["CustodyBucket"]["Properties"]["BucketEncryption"]
        for path, value in (("SSEAlgorithm", "AES256"), ("KMSMasterKeyID", "foreign-key"), ("BucketKeyEnabled", False)):
            with self.subTest(path=path):
                template = copy.deepcopy(self.template)
                row = template["Resources"]["CustodyBucket"]["Properties"]["BucketEncryption"]["ServerSideEncryptionConfiguration"][0]
                if path == "BucketKeyEnabled": row[path] = value
                else: row["ServerSideEncryptionByDefault"][path] = value
                with self.assertRaisesRegex(module.InfrastructurePlanError, "encryption"):
                    self.verify(template=template)
        self.assertIsNotNone(encryption)

    def test_kms_destruction_deny_cannot_be_removed_conditioned_or_narrowed(self) -> None:
        for mutation in ("remove", "condition", "principal", "action"):
            template = copy.deepcopy(self.template)
            row = self.statement(template, "CustodyKey", "KeyPolicy", "DenyKeyDestruction")
            if mutation == "remove":
                template["Resources"]["CustodyKey"]["Properties"]["KeyPolicy"]["Statement"].remove(row)
            elif mutation == "condition": row["Condition"] = {"Bool": {"aws:MultiFactorAuthPresent": "false"}}
            elif mutation == "principal": row["Principal"] = {"AWS": "account-root"}
            else: row["Action"] = ["kms:ScheduleKeyDeletion"]
            with self.subTest(mutation=mutation):
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_kms_lockout_safety_bypass_is_explicit_and_exact(self) -> None:
        for value in (False, None, "true"):
            template = copy.deepcopy(self.template)
            if value is None:
                del template["Resources"]["CustodyKey"]["Properties"]["BypassPolicyLockoutSafetyCheck"]
            else:
                template["Resources"]["CustodyKey"]["Properties"]["BypassPolicyLockoutSafetyCheck"] = value
            with self.subTest(value=value):
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_kms_administration_cannot_gain_policy_or_deletion_power(self) -> None:
        for action in ("kms:PutKeyPolicy", "kms:ScheduleKeyDeletion", "kms:*", "kms:CreateGrant"):
            template = copy.deepcopy(self.template)
            row = self.statement(template, "CustodyKey", "KeyPolicy", "AccountReadOnlyAdministration")
            row["Action"].append(action)
            with self.subTest(action=action):
                with self.assertRaisesRegex(module.InfrastructurePlanError, "broader"):
                    self.verify(template=template)

    def test_kms_crypto_principal_key_use_and_via_service_are_exact(self) -> None:
        for field, value in (
            ("Principal", "*"),
            ("Action", ["kms:*"]),
            ("Condition", {}),
        ):
            template = copy.deepcopy(self.template)
            self.statement(template, "CustodyKey", "KeyPolicy", "SingleWriterCryptography")[field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(module.InfrastructurePlanError, "single writer"):
                    self.verify(template=template)

    def test_bucket_deletion_deny_is_unconditional_and_complete(self) -> None:
        for mutation in ("condition", "missing-delete", "narrow-principal"):
            template = copy.deepcopy(self.template)
            row = self.statement(template, "CustodyBucketPolicy", "PolicyDocument", "DenyDestructiveMutation")
            if mutation == "condition": row["Condition"] = {"Bool": {"aws:MultiFactorAuthPresent": "false"}}
            elif mutation == "missing-delete": row["Action"].remove("s3:DeleteObjectVersion")
            else: row["Principal"] = {"AWS": "account-root"}
            with self.subTest(mutation=mutation):
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_write_enforcement_requires_single_writer_kms_and_compliance(self) -> None:
        cases = (
            ("DenyWritesOutsideSingleWriter", "Condition", {}),
            ("DenyWrongEncryptionAlgorithm", "Condition", {}),
            ("DenyWrongEncryptionKey", "Condition", {}),
            ("DenyNonComplianceWrites", "Condition", {}),
        )
        for sid, field, value in cases:
            template = copy.deepcopy(self.template)
            self.statement(template, "CustodyBucketPolicy", "PolicyDocument", sid)[field] = value
            with self.subTest(sid=sid):
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_writes_outside_private_prefix_are_universally_denied(self) -> None:
        cases = (
            ("Effect", "Allow"),
            ("Principal", {"AWS": "account-root"}),
            ("Action", ["s3:PutObject"]),
            ("NotResource", "*"),
            ("Resource", {"Fn::Sub": "${CustodyBucket.Arn}/${PrivatePrefix}/*"}),
        )
        for field, value in cases:
            template = copy.deepcopy(self.template)
            row = self.statement(template, "CustodyBucketPolicy", "PolicyDocument", "DenyWritesOutsidePrivatePrefix")
            if field == "Resource":
                del row["NotResource"]
            row[field] = value
            with self.subTest(field=field):
                with self.assertRaises(module.InfrastructurePlanError):
                    self.verify(template=template)

    def test_role_key_and_bucket_tags_are_exact(self) -> None:
        cases = (
            ("CustodyWriterRole", "Tags", "Value"),
            ("CustodyKey", "Tags", "TagValue"),
            ("CustodyBucket", "Tags", "Value"),
        )
        for resource, field, value_key in cases:
            for mutation in ("change", "extra", "missing"):
                template = copy.deepcopy(self.template)
                tags = template["Resources"][resource]["Properties"][field]
                if mutation == "change": tags[1][value_key] = "ACTIVE"
                elif mutation == "extra": tags.append(copy.deepcopy(tags[0]))
                else: tags.pop()
                with self.subTest(resource=resource, mutation=mutation):
                    with self.assertRaisesRegex(module.InfrastructurePlanError, "tags"):
                        self.verify(template=template)

    def test_notaction_and_nonintentional_notresource_are_forbidden(self) -> None:
        policy_paths = (
            ("CustodyWriterRole", "AssumeRolePolicyDocument"),
            ("CustodyKey", "KeyPolicy"),
            ("CustodyBucketPolicy", "PolicyDocument"),
            ("CustodyWriterPolicy", "PolicyDocument"),
        )
        for resource, policy_name in policy_paths:
            template = copy.deepcopy(self.template)
            rows = template["Resources"][resource]["Properties"][policy_name]["Statement"]
            rows[0]["NotAction"] = ["service:Forbidden"]
            with self.subTest(resource=resource, form="NotAction"):
                with self.assertRaisesRegex(module.InfrastructurePlanError, "NotAction"):
                    self.verify(template=template)
        template = copy.deepcopy(self.template)
        row = self.statement(template, "CustodyWriterPolicy", "PolicyDocument", "WriteAndVerifyImmutableVersions")
        del row["Resource"]
        row["NotResource"] = "arn:aws:s3:::excluded/*"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "NotResource"):
            self.verify(template=template)

    def test_role_trust_is_one_principal_with_external_id_and_boundary(self) -> None:
        template = copy.deepcopy(self.template)
        template["Resources"]["CustodyWriterRole"]["Properties"]["AssumeRolePolicyDocument"]["Statement"][0]["Principal"] = "*"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "trust"):
            self.verify(template=template)
        template = copy.deepcopy(self.template)
        del template["Resources"]["CustodyWriterRole"]["Properties"]["AssumeRolePolicyDocument"]["Statement"][0]["Condition"]
        with self.assertRaisesRegex(module.InfrastructurePlanError, "trust"):
            self.verify(template=template)
        template = copy.deepcopy(self.template)
        template["Resources"]["CustodyWriterRole"]["Properties"]["PermissionsBoundary"] = "foreign"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "boundary"):
            self.verify(template=template)

    def test_writer_policy_cannot_attach_elsewhere_or_gain_delete_wildcard(self) -> None:
        template = copy.deepcopy(self.template)
        template["Resources"]["CustodyWriterPolicy"]["Properties"]["Roles"].append("AnotherRole")
        with self.assertRaisesRegex(module.InfrastructurePlanError, "more than one"):
            self.verify(template=template)
        for action in ("s3:DeleteObject", "s3:*", "kms:ScheduleKeyDeletion"):
            template = copy.deepcopy(self.template)
            self.statement(template, "CustodyWriterPolicy", "PolicyDocument", "WriteAndVerifyImmutableVersions")["Action"].append(action)
            with self.subTest(action=action):
                with self.assertRaisesRegex(module.InfrastructurePlanError, "least-privilege"):
                    self.verify(template=template)

    def test_writer_object_prefix_and_kms_resource_are_exact(self) -> None:
        template = copy.deepcopy(self.template)
        self.statement(template, "CustodyWriterPolicy", "PolicyDocument", "WriteAndVerifyImmutableVersions")["Resource"] = "*"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "prefix"):
            self.verify(template=template)
        template = copy.deepcopy(self.template)
        self.statement(template, "CustodyWriterPolicy", "PolicyDocument", "UseExactCustodyKeyViaS3")["Resource"] = "*"
        with self.assertRaisesRegex(module.InfrastructurePlanError, "another KMS"):
            self.verify(template=template)
        template = copy.deepcopy(self.template)
        self.statement(template, "CustodyWriterPolicy", "PolicyDocument", "ListPrivateVersions")["Condition"] = {}
        with self.assertRaisesRegex(module.InfrastructurePlanError, "listing"):
            self.verify(template=template)

    def test_cli_is_silent_by_default_and_summary_has_no_identities(self) -> None:
        completed = subprocess.run([sys.executable, str(MODULE_PATH)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")
        emitted = subprocess.run([sys.executable, str(MODULE_PATH), "--emit-summary"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(emitted.returncode, 0)
        summary = json.loads(emitted.stdout)
        serialized = json.dumps(summary, sort_keys=True).lower()
        for forbidden in ("bucket_name", "arn:aws", "target_id", "conjecture", "cluster_id"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
