#!/usr/bin/env python3
"""Adversarial tests for raw-transcript bootstrap prerequisite acceptance."""

from __future__ import annotations

import base64
import copy
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
from xml.sax.saxutils import escape

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/verify_benchmark_v15_aws_github_bootstrap_acceptance.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_raw_acceptance", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(module)

CHAIN_SPEC = importlib.util.spec_from_file_location("p0_chain_helpers_for_bootstrap", ROOT / "scripts/test_build_verify_benchmark_v15_p0_a0.py")
assert CHAIN_SPEC and CHAIN_SPEC.loader
chain_helpers = importlib.util.module_from_spec(CHAIN_SPEC); CHAIN_SPEC.loader.exec_module(chain_helpers)

ACCOUNT = "123456789012"
SERVER_DATE = datetime(2026, 8, 14, 3, 0, 0, tzinfo=timezone.utc)
SIGNED_AT = "2026-08-14T03:01:00Z"


def raw_json(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def headers(provider: str, request_id: str, observed_date: datetime = SERVER_DATE) -> bytes:
    request_header = "x-github-request-id" if provider == "GITHUB" else "x-amzn-requestid"
    content_type = "application/json; charset=utf-8" if provider == "GITHUB" else "text/xml"
    return f"date: {format_datetime(observed_date, usegmt=True)}\r\n{request_header}: {request_id}\r\ncontent-type: {content_type}\r\n".encode()


def exchange(receipt_id: str, provider: str, service: str, operation: str, method: str, url: str, request_body: bytes, response_body: bytes, index: int, observed_date: datetime = SERVER_DATE) -> dict:
    request_headers = (b"accept: application/vnd.github+json\r\nuser-agent: c5k4-method-v1.5-bootstrap-observer\r\nx-github-api-version: 2022-11-28\r\n" if provider == "GITHUB" else b"content-type: application/x-www-form-urlencoded; charset=utf-8\r\n")
    return {
        "id": receipt_id,
        "request": {"provider": provider, "service": service, "operation": operation, "method": method, "url": url, "headers_base64": module.b64(request_headers), "body_base64": module.b64(request_body)},
        "response": {"status": 200, "headers_base64": module.b64(headers(provider, f"ABCD:1234:5678:9ABC:{index:04X}" if provider == "GITHUB" else f"00000000-0000-4000-8000-{index:012d}", observed_date)), "body_base64": module.b64(response_body)},
    }


def github_exchange(receipt_id: str, url: str, body: dict, index: int) -> dict:
    return exchange(receipt_id, "GITHUB", "REST", receipt_id, "GET", url, b"", raw_json(body), index)


def aws_body(service: str, operation: str, params: dict[str, str]) -> bytes:
    version = "2011-06-15" if service == "STS" else "2010-05-15" if service == "CLOUDFORMATION" else "2010-05-08"
    return urllib.parse.urlencode({"Action": operation, "Version": version, **params}).encode()


def aws_exchange(receipt_id: str, service: str, operation: str, params: dict[str, str], xml: str, index: int, observed_date: datetime = SERVER_DATE) -> dict:
    url = "https://sts.amazonaws.com/" if service == "STS" else f"https://cloudformation.{module.REGION}.amazonaws.com/" if service == "CLOUDFORMATION" else "https://iam.amazonaws.com/"
    closing = f"</{operation}Response>"
    request_id = f"00000000-0000-4000-8000-{index:012d}"
    if not xml.endswith(closing): raise AssertionError("fixture AWS response root differs")
    opening = f"<{operation}Response>"
    xml = xml.replace(opening, f'<{operation}Response xmlns="{module.AWS_XML_NAMESPACES[service]}">', 1)
    xml = xml[:-len(closing)] + f"<ResponseMetadata><RequestId>{request_id}</RequestId></ResponseMetadata>" + closing
    return exchange(receipt_id, "AWS", service, operation, "POST", url, aws_body(service, operation, params), xml.encode(), index, observed_date)


def policy_text(value: dict) -> str:
    return escape(urllib.parse.quote(raw_json(value).decode(), safe=""))


def role_xml(name: str, arn: str, path: str, duration: int, trust: dict, boundary: str | None = None) -> str:
    boundary_xml = f"<PermissionsBoundary><PermissionsBoundaryArn>{boundary}</PermissionsBoundaryArn></PermissionsBoundary>" if boundary else ""
    return f"<GetRoleResponse><GetRoleResult><Role><Path>{path}</Path><RoleName>{name}</RoleName><Arn>{arn}</Arn><MaxSessionDuration>{duration}</MaxSessionDuration><AssumeRolePolicyDocument>{policy_text(trust)}</AssumeRolePolicyDocument>{boundary_xml}</Role></GetRoleResult></GetRoleResponse>"


def list_inline_xml(policy_name: str) -> str:
    return f"<ListRolePoliciesResponse><ListRolePoliciesResult><PolicyNames><member>{policy_name}</member></PolicyNames><IsTruncated>false</IsTruncated></ListRolePoliciesResult></ListRolePoliciesResponse>"


def inline_xml(role_name: str, policy_name: str, policy: dict) -> str:
    return f"<GetRolePolicyResponse><GetRolePolicyResult><RoleName>{role_name}</RoleName><PolicyName>{policy_name}</PolicyName><PolicyDocument>{policy_text(policy)}</PolicyDocument></GetRolePolicyResult></GetRolePolicyResponse>"


def attached_xml() -> str:
    return "<ListAttachedRolePoliciesResponse><ListAttachedRolePoliciesResult><AttachedPolicies></AttachedPolicies><IsTruncated>false</IsTruncated></ListAttachedRolePoliciesResult></ListAttachedRolePoliciesResponse>"


def authority() -> tuple[dict, list[Ed25519PrivateKey], tempfile.TemporaryDirectory, Path]:
    keys = [Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()]
    rows = []; file_rows = []
    for index, key in enumerate(keys, 1):
        public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        rows.append({"authority_id": f"independent-{index}", "verification_key_sha256": module.sha256(public), "key_origin": "EXTERNAL_PUBLIC_KEY_HASH_FROZEN_BEFORE_P0A"})
        file_rows.append({"authority_id": f"independent-{index}", "public_key_base64": module.b64(public)})
    p0a = {"authority_policy": {"required_independent_signature_count": 2, "independent_authorities": rows}}
    temp = tempfile.TemporaryDirectory(); path = Path(temp.name) / "keys.json"
    path.write_text(json.dumps({"schema": "c5k4-method-v1.5-offline-a0-authority-keys-1.0", "keys": file_rows}))
    return p0a, keys, temp, path


def reseal(value: dict, p0a: dict, keys: list[Ed25519PrivateKey]) -> None:
    payload = module.payload_sha256(value); signatures = []
    for authority_row, key in zip(p0a["authority_policy"]["independent_authorities"], keys):
        signatures.append({
            "authority_id": authority_row["authority_id"], "verification_key_sha256": authority_row["verification_key_sha256"],
            "algorithm": "Ed25519", "signed_payload_sha256": payload,
            "signature_base64": module.b64(key.sign(module.signature_message(payload))), "signed_at_utc": SIGNED_AT,
        })
    value["authentication"] = {"payload_sha256": payload, "signatures": signatures}


def fixture(candidate_commit: str = "9" * 40) -> tuple[dict, dict, dict, dict, list[Ed25519PrivateKey], tempfile.TemporaryDirectory, Path]:
    contract = json.loads((ROOT / module.CONTRACT_PATH).read_text())
    store_template = json.loads((ROOT / module.STORE_TEMPLATE_PATH).read_text())
    p0a, keys, temporary, keys_path = authority()
    identity = {
        "schema": "c5k4-method-v1.5-validated-a0-identity-1.0", "commit": "a" * 40, "root_tree": "b" * 40,
        "artifact": {"path": "results/benchmark/v1.5-p0-a0/A0.json", "sha256": "c" * 64, "canonical_sha256": "d" * 64},
        "authority_roster_sha256": "e" * 64, "ami_authority_binding_policy_template_sha256": "f" * 64,
        "external_harness_verification_key_sha256": "1" * 64, "nitrotpm_key_generation_attestation_sha256": "2" * 64,
        "nitrotpm_key_policy": "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY", "a0_authorized_at_utc": "2026-08-14T01:03:30Z",
        "a0_publication_observed_at_utc": "2026-08-14T01:05:00Z", "a0_publication_run_id": 43,
        "github_server_replay": {"api_version": "2022-11-28", **{kind: {"run_id": index, "head_sha": "a" * 40, "created_at_utc": "2026-08-14T01:00:00Z", "run_started_at_utc": "2026-08-14T01:00:10Z", "updated_at_utc": "2026-08-14T01:01:00Z", "captured_run_object_sha256": "3" * 64, "captured_listing_sha256": "4" * 64, "captured_ref_sha256": "5" * 64, "api_projection_sha256": "6" * 64} for index, kind in enumerate(("p0a", "p0t", "a0"), 41)}},
        "status": "EXTERNALLY_AUTHORIZED_A0", "activation_authority": True,
    }
    account = ACCOUNT; provider_arn = f"arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com"
    store_arn = f"arn:aws:iam::{account}:role{module.DEPLOYER_PATH}{module.STORE_ROLE}"
    host_arn = f"arn:aws:iam::{account}:role{module.DEPLOYER_PATH}{module.HOST_ROLE}"
    harness_arn = f"arn:aws:iam::{account}:role{module.DEPLOYER_PATH}{module.HARNESS_ROLE}"
    custody_name = "c5k4-v15-store-CustodyWriterRole-ABC123"
    custody_arn = f"arn:aws:iam::{account}:role{module.CUSTODY_PATH}{custody_name}"
    boundary_arn = f"arn:aws:iam::{account}:policy/{module.BOUNDARY_NAME}"
    values = {
        "BENCHMARK_V15_AWS_REGION": module.REGION, "BENCHMARK_V15_TEMPLATE_SHA256": module.STORE_TEMPLATE_SHA256,
        "BENCHMARK_V15_STACK_NAME": "c5k4-v15-immutable-store", "BENCHMARK_V15_AWS_ROLE_ARN": store_arn,
        "BENCHMARK_V15_HARNESS_PRINCIPAL_ARN": harness_arn, "BENCHMARK_V15_HOST_STACK_NAME": "c5k4-v15-controlled-host",
        "BENCHMARK_V15_HOST_TEMPLATE_SHA256": module.HOST_TEMPLATE_SHA256, "BENCHMARK_V15_HOST_AMI_ID": "ami-0123456789abcdef0",
        "BENCHMARK_V15_HOST_AMI_MEASUREMENTS_SHA256": "6" * 64, "BENCHMARK_V15_HOST_AWS_ROLE_ARN": host_arn,
    }
    external_id = module.sha256(f"{candidate_commit}:{module.STORE_TEMPLATE_SHA256}:{values['BENCHMARK_V15_STACK_NAME']}:{harness_arn}".encode())
    github_base = "https://api.github.com/repos/Kuberwastaken/c5-k4"
    transcript = [
        github_exchange("github_repository", github_base, {"id": 1331829034, "name": "c5-k4", "full_name": "Kuberwastaken/c5-k4", "default_branch": "main", "owner": {"login": "Kuberwastaken", "id": 97027230}}, 1),
        github_exchange("github_oidc_subject", github_base + "/actions/oidc/customization/sub", {"use_default": False, "use_immutable_subject": True, "include_claim_keys": ["repo", "context"]}, 2),
        github_exchange("github_environment", github_base + f"/environments/{module.ENVIRONMENT}", {"name": module.ENVIRONMENT, "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}, "protection_rules": [{"type": "required_reviewers", "prevent_self_review": True, "reviewers": [{"type": "User", "reviewer": {"id": 42, "login": "independent-reviewer"}}]}, {"type": "branch_policy"}]}, 3),
        github_exchange("github_environment_branches", github_base + f"/environments/{module.ENVIRONMENT}/deployment-branch-policies", {"total_count": 1, "branch_policies": [{"id": 501, "node_id": "BRANCH_POLICY_501", "name": "main", "type": "branch"}]}, 4),
        github_exchange("github_repository_variables", github_base + "/actions/variables?per_page=100", {"total_count": 10, "variables": [{"name": name, "value": values[name], "created_at": "2026-08-14T02:00:00Z", "updated_at": "2026-08-14T02:30:00Z"} for name in module.VARIABLE_NAMES]}, 5),
        github_exchange("github_environment_variables", github_base + f"/environments/{module.ENVIRONMENT}/variables?per_page=100", {"total_count": 0, "variables": []}, 6),
        github_exchange("github_repository_secrets", github_base + "/actions/secrets?per_page=100", {"total_count": 0, "secrets": []}, 7),
        github_exchange("github_environment_secrets", github_base + f"/environments/{module.ENVIRONMENT}/secrets?per_page=100", {"total_count": 0, "secrets": []}, 8),
    ]
    index = 9
    transcript.append(aws_exchange("aws_caller_identity", "STS", "GetCallerIdentity", {}, f"<GetCallerIdentityResponse><GetCallerIdentityResult><UserId>AROATEST:observer</UserId><Account>{account}</Account><Arn>arn:aws:sts::{account}:assumed-role/bootstrap-observer/session</Arn></GetCallerIdentityResult></GetCallerIdentityResponse>", index)); index += 1
    transcript.append(aws_exchange("aws_oidc_provider", "IAM", "GetOpenIDConnectProvider", {"OpenIDConnectProviderArn": provider_arn}, "<GetOpenIDConnectProviderResponse><GetOpenIDConnectProviderResult><Url>token.actions.githubusercontent.com</Url><ClientIDList><member>sts.amazonaws.com</member></ClientIDList><ThumbprintList><member>" + "1" * 40 + "</member></ThumbprintList></GetOpenIDConnectProviderResult></GetOpenIDConnectProviderResponse>", index)); index += 1
    store_policy = module.expected_deployer_policy("store_deployer", account, values, contract)
    host_policy = module.expected_deployer_policy("host_deployer", account, values, contract)
    harness_policy = {"Version": "2012-10-17", "Statement": [module.policy_statement("OnlyExactCustodyWriter", ["sts:AssumeRole"], custody_arn, {"StringEquals": {"sts:ExternalId": external_id}})]}
    substitutions = {
        "AWS::Partition": "aws", "AWS::AccountId": account, "AWS::Region": module.REGION, "AWS::URLSuffix": "amazonaws.com",
        "HarnessPrincipalArn": harness_arn, "HarnessExternalId": external_id, "PrivatePrefix": "private/c5k4/v1.5", "RetentionYears": 3,
        "CustodyBucket": "fixture-custody-bucket", "CustodyBucket.Arn": "arn:aws:s3:::fixture-custody-bucket",
        "CustodyKey": "11111111-2222-3333-4444-555555555555", "CustodyKey.Arn": f"arn:aws:kms:{module.REGION}:{account}:key/11111111-2222-3333-4444-555555555555",
        "CustodyWriterRole": custody_name, "CustodyWriterRole.Arn": custody_arn,
    }
    custody_policy = module.render_template(store_template["Resources"]["CustodyWriterPolicy"]["Properties"]["PolicyDocument"], substitutions)
    role_specs = {
        "store_deployer": (module.STORE_ROLE, store_arn, module.DEPLOYER_PATH, 1800, module.oidc_trust(account), None, module.STORE_POLICY, store_policy),
        "host_deployer": (module.HOST_ROLE, host_arn, module.DEPLOYER_PATH, 1800, module.oidc_trust(account), None, module.HOST_POLICY, host_policy),
        "harness": (module.HARNESS_ROLE, harness_arn, module.DEPLOYER_PATH, 3600, module.ec2_trust(), None, module.HARNESS_POLICY, harness_policy),
        "custody_writer": (custody_name, custody_arn, module.CUSTODY_PATH, 3600, module.custody_trust(harness_arn, external_id), boundary_arn, module.CUSTODY_POLICY, custody_policy),
    }
    for label, (name, arn, path, duration, trust_doc, boundary, policy_name, policy_doc) in role_specs.items():
        transcript.append(aws_exchange(f"aws_{label}_role", "IAM", "GetRole", {"RoleName": name}, role_xml(name, arn, path, duration, trust_doc, boundary), index)); index += 1
        transcript.append(aws_exchange(f"aws_{label}_inline_names", "IAM", "ListRolePolicies", {"RoleName": name}, list_inline_xml(policy_name), index)); index += 1
        transcript.append(aws_exchange(f"aws_{label}_inline_policy", "IAM", "GetRolePolicy", {"RoleName": name, "PolicyName": policy_name}, inline_xml(name, policy_name, policy_doc), index)); index += 1
        transcript.append(aws_exchange(f"aws_{label}_attached", "IAM", "ListAttachedRolePolicies", {"RoleName": name}, attached_xml(), index)); index += 1
    profile_xml = f"<GetInstanceProfileResponse><GetInstanceProfileResult><InstanceProfile><Path>{module.DEPLOYER_PATH}</Path><InstanceProfileName>{module.HARNESS_ROLE}</InstanceProfileName><Arn>arn:aws:iam::{account}:instance-profile{module.DEPLOYER_PATH}{module.HARNESS_ROLE}</Arn><Roles><member><RoleName>{module.HARNESS_ROLE}</RoleName></member></Roles></InstanceProfile></GetInstanceProfileResult></GetInstanceProfileResponse>"
    transcript.append(aws_exchange("aws_harness_profile", "IAM", "GetInstanceProfile", {"InstanceProfileName": module.HARNESS_ROLE}, profile_xml, index)); index += 1
    boundary_xml = f"<GetPolicyResponse><GetPolicyResult><Policy><PolicyName>{module.BOUNDARY_NAME}</PolicyName><Arn>{boundary_arn}</Arn><Path>/</Path><DefaultVersionId>v3</DefaultVersionId></Policy></GetPolicyResult></GetPolicyResponse>"
    transcript.append(aws_exchange("aws_boundary_metadata", "IAM", "GetPolicy", {"PolicyArn": boundary_arn}, boundary_xml, index)); index += 1
    boundary_doc = module.expected_boundary(account)
    boundary_version_xml = f"<GetPolicyVersionResponse><GetPolicyVersionResult><PolicyVersion><Document>{policy_text(boundary_doc)}</Document><VersionId>v3</VersionId><IsDefaultVersion>true</IsDefaultVersion></PolicyVersion></GetPolicyVersionResult></GetPolicyVersionResponse>"
    transcript.append(aws_exchange("aws_boundary_version", "IAM", "GetPolicyVersion", {"PolicyArn": boundary_arn, "VersionId": "v3"}, boundary_version_xml, index)); index += 1
    deployment_parameters = {"aws_region": module.REGION, "harness_external_id": external_id, "harness_external_id_policy": "SHA256(candidate_commit:template_sha256:stack_name:harness_principal_arn)", "harness_principal_arn": harness_arn, "private_prefix": "private/c5k4/v1.5", "retention_years": 3, "stack_name": values["BENCHMARK_V15_STACK_NAME"]}
    parameters_sha256 = module.sha256(deployment_parameters)
    change_set_name = f"c5k4-v15-{parameters_sha256[:16]}-987654"
    stack_id = f"arn:aws:cloudformation:{module.REGION}:{account}:stack/{values['BENCHMARK_V15_STACK_NAME']}/aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    change_set_id = f"arn:aws:cloudformation:{module.REGION}:{account}:changeSet/{change_set_name}/11111111-2222-3333-4444-555555555555"
    changes = "".join(f"<member><ResourceChange><Action>Add</Action><LogicalResourceId>{logical}</LogicalResourceId><ResourceType>{kind}</ResourceType></ResourceChange><Type>Resource</Type></member>" for logical, kind in (("CustodyBucket", "AWS::S3::Bucket"), ("CustodyBucketPolicy", "AWS::S3::BucketPolicy"), ("CustodyKey", "AWS::KMS::Key"), ("CustodyWriterPolicy", "AWS::IAM::Policy"), ("CustodyWriterRole", "AWS::IAM::Role")))
    change_set_xml = f"<DescribeChangeSetResponse><DescribeChangeSetResult><ChangeSetName>{change_set_name}</ChangeSetName><ChangeSetId>{change_set_id}</ChangeSetId><StackName>{values['BENCHMARK_V15_STACK_NAME']}</StackName><StackId>{stack_id}</StackId><Description>candidate={candidate_commit} template={module.STORE_TEMPLATE_SHA256} parameters={parameters_sha256}</Description><CreationTime>2026-08-14T02:58:00Z</CreationTime><ChangeSetType>CREATE</ChangeSetType><Status>CREATE_COMPLETE</Status><ExecutionStatus>AVAILABLE</ExecutionStatus><Capabilities><member>CAPABILITY_IAM</member></Capabilities><Changes>{changes}</Changes></DescribeChangeSetResult></DescribeChangeSetResponse>"
    transcript.append(aws_exchange("aws_store_change_set_pre_execution", "CLOUDFORMATION", "DescribeChangeSet", {"StackName": values["BENCHMARK_V15_STACK_NAME"], "ChangeSetName": change_set_name}, change_set_xml, index, SERVER_DATE - timedelta(minutes=1))); index += 1
    stack_xml = f"<DescribeStacksResponse><DescribeStacksResult><Stacks><member><StackName>{values['BENCHMARK_V15_STACK_NAME']}</StackName><StackId>{stack_id}</StackId><ChangeSetId>{change_set_id}</ChangeSetId><StackStatus>CREATE_COMPLETE</StackStatus><Parameters><member><ParameterKey>HarnessPrincipalArn</ParameterKey><ParameterValue>{harness_arn}</ParameterValue></member><member><ParameterKey>HarnessExternalId</ParameterKey><ParameterValue>****</ParameterValue></member><member><ParameterKey>PrivatePrefix</ParameterKey><ParameterValue>private/c5k4/v1.5</ParameterValue></member><member><ParameterKey>RetentionYears</ParameterKey><ParameterValue>3</ParameterValue></member></Parameters></member></Stacks></DescribeStacksResult></DescribeStacksResponse>"
    transcript.append(aws_exchange("aws_store_stack", "CLOUDFORMATION", "DescribeStacks", {"StackName": values["BENCHMARK_V15_STACK_NAME"]}, stack_xml, index)); index += 1
    resources = [("CustodyBucket", "fixture-custody-bucket", "AWS::S3::Bucket"), ("CustodyBucketPolicy", "fixture-custody-bucket", "AWS::S3::BucketPolicy"), ("CustodyKey", "11111111-2222-3333-4444-555555555555", "AWS::KMS::Key"), ("CustodyWriterPolicy", module.CUSTODY_POLICY, "AWS::IAM::Policy"), ("CustodyWriterRole", custody_name, "AWS::IAM::Role")]
    members = "".join(f"<member><LogicalResourceId>{logical}</LogicalResourceId><PhysicalResourceId>{physical}</PhysicalResourceId><ResourceType>{kind}</ResourceType><ResourceStatus>CREATE_COMPLETE</ResourceStatus></member>" for logical, physical, kind in resources)
    resources_xml = f"<DescribeStackResourcesResponse><DescribeStackResourcesResult><StackResources>{members}</StackResources></DescribeStackResourcesResult></DescribeStackResourcesResponse>"
    transcript.append(aws_exchange("aws_store_stack_resources", "CLOUDFORMATION", "DescribeStackResources", {"StackName": values["BENCHMARK_V15_STACK_NAME"]}, resources_xml, index))
    assert [row["id"] for row in transcript] == module.EXPECTED_IDS
    value = {
        "schema": "c5k4-method-v1.5-aws-github-bootstrap-acceptance-2.0", "status": "AUTHENTICATED_LIVE_BOOTSTRAP_PREREQUISITE_SATISFIED",
        "protocol_version": "1.5", "target_specific": False,
        "scope": {"raw_server_responses_only": True, "signed_summaries_permitted": False, "operator_assertion_is_evidence": False, "external_mutation_authorized_by_artifact": False, "long_lived_credentials_present": False, "bootstrap_prerequisite_satisfied": True, "ami_acceptance_separate_and_required": True, "controlled_host_apply_permitted_by_this_artifact_alone": False},
        "frozen_bindings": {
            "bootstrap_contract_commit": module.CONTRACT_COMMIT, "bootstrap_contract_file_sha256": module.CONTRACT_FILE_SHA256,
            "bootstrap_contract_canonical_sha256": module.CONTRACT_CANONICAL_SHA256, "controlled_host_preflight_commit": module.PREFLIGHT_COMMIT,
            "controlled_host_plan_file_sha256": module.HOST_PLAN_FILE_SHA256, "immutable_store_template_sha256": module.STORE_TEMPLATE_SHA256,
            "controlled_host_template_sha256": module.HOST_TEMPLATE_SHA256, "acceptance_schema_sha256": "1" * 64, "acceptance_verifier_sha256": "2" * 64,
            "infrastructure_activation_workflow_sha256": module.ACTIVATION_WORKFLOW_SHA256,
            "p0_verifier_sha256": "3" * 64, "p0_schema_sha256": {path: "4" * 64 for path in module.P0_SCHEMA_PATHS},
        },
        "a0_identity": identity,
        "p0_publication_replay": {"a0_publication_receipt": {}, "raw_api_responses": [{"url": f"https://api.github.com/replay/{i}", "body_base64": module.b64(b"{}") } for i in range(7)]},
        "transcript": transcript, "authentication": {"payload_sha256": "0" * 64, "signatures": []},
    }
    reseal(value, p0a, keys)
    return value, identity, p0a, contract, store_template, keys, temporary, keys_path


class RawBootstrapAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / module.SCHEMA_REPO_PATH).read_text())

    def setUp(self) -> None:
        self.value, self.identity, self.p0a, self.contract, self.template, self.keys, self.temporary, self.keys_path = fixture()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def verify(self, value=None):
        return module.verify_payload(copy.deepcopy(self.value if value is None else value), copy.deepcopy(self.schema), copy.deepcopy(self.contract), copy.deepcopy(self.template), copy.deepcopy(self.identity), copy.deepcopy(self.p0a), self.keys_path)

    def mutate_body(self, value: dict, receipt_id: str, transform) -> None:
        row = next(row for row in value["transcript"] if row["id"] == receipt_id)
        raw = base64.b64decode(row["response"]["body_base64"])
        row["response"]["body_base64"] = module.b64(transform(raw))
        reseal(value, self.p0a, self.keys)

    def test_exact_raw_transcript_satisfies_only_bootstrap_prerequisite(self) -> None:
        result = self.verify()
        self.assertTrue(result["bootstrap_prerequisite_satisfied"])
        self.assertTrue(result["ami_acceptance_separate_and_required"])
        self.assertFalse(result["controlled_host_apply_permitted"])
        self.assertEqual(result["raw_exchange_count"], 32)
        self.assertEqual(set(result["computed_policy_sha256"]), {
            "store_deployer", "host_deployer", "harness", "custody_writer", "custody_writer_boundary",
            "store_deployer_trust", "host_deployer_trust", "harness_trust", "custody_writer_trust",
        })

    def test_nonauthoritative_plan_is_strict_self_digested_and_blocked(self) -> None:
        plan_path = ROOT / "results/benchmark/v1.5-protocol/aws-github-bootstrap-acceptance-plan.json"
        schema_path = ROOT / "schemas/benchmark-aws-github-bootstrap-acceptance-plan-v1.5.schema.json"
        plan = json.loads(plan_path.read_text()); schema = json.loads(schema_path.read_text())
        Draft7Validator(schema).validate(plan)
        self.assertEqual(plan["plan_sha256"], module.domain_digest("c5k4-method-v1.5-aws-github-bootstrap-acceptance-plan-2.0", module.without(plan, "plan_sha256")))
        self.assertFalse(plan["gate"]["bootstrap_prerequisite_satisfied"])
        self.assertFalse(plan["gate"]["controlled_host_apply_permitted"])

    def test_raw_response_forgery_fails_even_when_resigned(self) -> None:
        value = copy.deepcopy(self.value)
        self.mutate_body(value, "github_repository", lambda raw: raw.replace(b"1331829034", b"1331829035"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value)
        row = next(row for row in value["transcript"] if row["id"] == "aws_oidc_provider")
        row["response"]["headers_base64"] = module.b64(headers("AWS", "AWS-REQUEST-FORGED").replace(b"date:", b"x-date:")); reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_arbitrary_github_or_aws_api_is_rejected(self) -> None:
        value = copy.deepcopy(self.value); row = value["transcript"][0]; row["request"]["url"] += "/hooks"; row["request"]["operation"] = "list_hooks"; reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); row = next(row for row in value["transcript"] if row["id"] == "aws_store_deployer_role"); row["request"]["operation"] = "DeleteRole"; row["request"]["body_base64"] = module.b64(aws_body("IAM", "DeleteRole", {"RoleName": module.STORE_ROLE})); reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_exact_immutable_oidc_environment_variables_and_secrets_are_decoded_from_raw(self) -> None:
        mutations = [
            ("github_oidc_subject", lambda raw: raw.replace(b"true", b"false", 1)),
            ("github_environment_branches", lambda raw: raw.replace(b'"main"', b'"*"')),
            ("github_environment", lambda raw: raw.replace(b'"prevent_self_review":true', b'"prevent_self_review":false')),
            ("github_repository_secrets", lambda raw: raw.replace(b'"total_count":0', b'"total_count":1')),
            ("github_environment_secrets", lambda raw: raw.replace(b'"total_count":0', b'"total_count":1')),
            ("github_repository_variables", lambda raw: raw.replace(module.STORE_TEMPLATE_SHA256.encode(), ("9" * 64).encode())),
        ]
        for receipt_id, transform in mutations:
            value = copy.deepcopy(self.value); self.mutate_body(value, receipt_id, transform)
            with self.subTest(receipt_id=receipt_id), self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_role_path_policy_resource_and_custody_substitution_exploits_fail(self) -> None:
        value = copy.deepcopy(self.value); self.mutate_body(value, "aws_harness_role", lambda raw: raw.replace(module.DEPLOYER_PATH.encode(), b"/"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); self.mutate_body(value, "aws_host_deployer_inline_policy", lambda raw: raw.replace(b"iam%3APassRole", b"iam%3A%2A"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); self.mutate_body(value, "aws_custody_writer_role", lambda raw: raw.replace(b"CustodyWriterRole-ABC123", b"CustodyWriterRole-EVIL999"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_missing_duplicate_or_stale_server_receipt_fails(self) -> None:
        value = copy.deepcopy(self.value); value["transcript"].pop(); reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); value["transcript"][1]["response"]["headers_base64"] = value["transcript"][0]["response"]["headers_base64"]; reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); row = value["transcript"][-1]; stale = headers("AWS", "ffffffff-ffff-4fff-8fff-ffffffffffff", SERVER_DATE + timedelta(minutes=6)); row["response"]["headers_base64"] = module.b64(stale); reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_resigned_header_namespace_and_pagination_downgrades_fail(self) -> None:
        value = copy.deepcopy(self.value)
        row = value["transcript"][0]
        row["request"]["headers_base64"] = module.b64(b"accept: application/vnd.github+json\r\nuser-agent: c5k4-method-v1.5-bootstrap-observer\r\nx-github-api-version: 2022-11-28-downgrade\r\n")
        reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        row = value["transcript"][3]
        raw = base64.b64decode(row["response"]["headers_base64"])
        row["response"]["headers_base64"] = module.b64(raw + b'link: <https://api.github.com/next>; rel="next"\r\n')
        reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_stack_resources", lambda raw: raw.replace(b"</DescribeStackResourcesResult>", b"<NextToken>hidden</NextToken></DescribeStackResourcesResult>"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_caller_identity", lambda raw: raw.replace(module.AWS_XML_NAMESPACES["STS"].encode(), b"https://sts.amazonaws.com/doc/2010-01-01/"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_caller_identity", lambda raw: raw.replace(b"<Account>", b'<Account xmlns="urn:evil">'))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_resigned_masked_external_id_formula_and_change_set_substitutions_fail(self) -> None:
        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_stack", lambda raw: raw.replace(b"****", b"7" * 64))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_change_set_pre_execution", lambda raw: raw.replace(("9" * 40).encode(), ("8" * 40).encode()))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_change_set_pre_execution", lambda raw: re.sub(br"parameters=[0-9a-f]{64}", b"parameters=" + b"0" * 64, raw))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_change_set_pre_execution", lambda raw: raw.replace(b"<ExecutionStatus>AVAILABLE</ExecutionStatus>", b"<ExecutionStatus>EXECUTE_COMPLETE</ExecutionStatus>"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_change_set_pre_execution", lambda raw: raw.replace(b"</Description>", b"</Description><ClientToken>synthetic-echo</ClientToken>"))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_resigned_stack_arn_and_exact_change_structure_substitutions_fail(self) -> None:
        value = copy.deepcopy(self.value)
        for receipt_id in ("aws_store_change_set_pre_execution", "aws_store_stack"):
            self.mutate_body(value, receipt_id, lambda raw: re.sub(br"arn:aws:cloudformation:ap-south-1:123456789012:stack/c5k4-v15-immutable-store/[0-9a-f-]+", b"not-an-arn", raw))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_change_set_pre_execution", lambda raw: raw.replace(b"<Action>Add</Action>", b"<Action>Remove</Action><Action>Add</Action>", 1))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

        value = copy.deepcopy(self.value)
        self.mutate_body(value, "aws_store_change_set_pre_execution", lambda raw: raw.replace(b"<Changes>", b"<Changes><Bogus>same-namespace</Bogus>", 1))
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_verify_committed_succeeds_offline_with_explicit_p0_publication_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            subprocess.run(["git", "clone", "-q", "--shared", str(ROOT), str(repo)], check=True)
            helper = chain_helpers.ChainTests("runTest")
            helper.tmp = None; helper.repo = repo
            helper.git("config", "user.name", "Bootstrap E2E"); helper.git("config", "user.email", "bootstrap@example.invalid")

            # The P0 freeze and bootstrap validator must both preexist the chain.
            base_paths = set(chain_helpers.BUILD.REQUIRED_COMPONENTS) | {module.SCHEMA_REPO_PATH, module.VERIFIER_REPO_PATH, module.ACTIVATION_WORKFLOW_PATH}
            for path in base_paths:
                source = ROOT / path; destination = repo / path
                destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, destination)
            helper.git("add", *sorted(base_paths)); helper.git("commit", "-qm", "exact protocol base")
            helper.base = helper.git("rev-parse", "HEAD")
            helper.private_keys = [Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()]
            helper.authorities = []
            for index, key in enumerate(helper.private_keys, 1):
                public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
                helper.authorities.append({"authority_id": f"independent-{index}", "verification_key_sha256": module.sha256(public), "key_origin": "EXTERNAL_PUBLIC_KEY_HASH_FROZEN_BEFORE_P0A"})
            roster = {"required_independent_signature_count": 2, "independent_authorities": helper.authorities}
            helper.policy = {
                **roster,
                "authority_roster_sha256": chain_helpers.BUILD.domain_digest("c5k4-method-v1.5-a0-authority-roster-1.0", roster),
                "attestable_ami_authority_binding_policy_sha256": chain_helpers.BUILD.domain_digest(
                    "c5k4-method-v1.5-attestable-ami-authority-binding-policy-template-1.0",
                    [chain_helpers.BUILD.blob_binding(repo, helper.base, path) for path in chain_helpers.BUILD.AMI_POLICY_COMPONENTS],
                ),
                "harness_key_policy": {"algorithm": "Ed25519", "storage": "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY", "verification_key_hash_known_at_p0a": False, "raw_private_key_egress_permitted": False},
            }
            helper.component_paths = sorted(chain_helpers.BUILD.REQUIRED_COMPONENTS)
            helper.p0a = chain_helpers.BUILD.build_p0a(repo, helper.base, {"component_paths": helper.component_paths}, helper.policy)
            helper.write(chain_helpers.BUILD.P0A_PATH, helper.p0a); helper.commit_only(chain_helpers.BUILD.P0A_PATH, "P0A"); helper.p0a_commit = helper.git("rev-parse", "HEAD")
            p0a_fetch = helper.api_fetch("P0A", helper.p0a_commit, 41)
            helper.p0a_receipt = chain_helpers.VERIFY.compile_actions_observation(repo, kind="P0A", commit=helper.p0a_commit, run_id=41, fetch=p0a_fetch)
            helper.p0t = chain_helpers.BUILD.build_p0t(repo, helper.p0a_commit, helper.p0a_receipt, observation_verifier=lambda r, a, k, c: chain_helpers.VERIFY.replay_actions_observation(r, a, kind=k, commit=c, fetch=p0a_fetch))
            helper.write(chain_helpers.BUILD.P0T_PATH, helper.p0t); helper.commit_only(chain_helpers.BUILD.P0T_PATH, "P0T"); helper.p0t_commit = helper.git("rev-parse", "HEAD")
            p0t_fetch = helper.api_fetch("P0T", helper.p0t_commit, 42)
            helper.p0t_receipt = chain_helpers.VERIFY.compile_actions_observation(repo, kind="P0T", commit=helper.p0t_commit, run_id=42, fetch=p0t_fetch)
            authoritative, keys_path = helper.authoritative_a0()
            a0_commit = helper.commit_a0(authoritative)
            a0_fetch = helper.api_fetch("A0", a0_commit, 43)
            a0_receipt = chain_helpers.VERIFY.compile_actions_observation(repo, kind="A0", commit=a0_commit, run_id=43, fetch=a0_fetch)
            combined = helper.combined_fetch(p0a_fetch, p0t_fetch, a0_fetch)
            urls = []
            for run_id, commit in ((41, helper.p0a_commit), (42, helper.p0t_commit), (43, a0_commit)):
                urls.extend(chain_helpers.VERIFY._api_urls(run_id, commit))
            replay_responses = {url: combined(url) for url in urls}
            for run_id, commit in ((41, helper.p0a_commit), (42, helper.p0t_commit), (43, a0_commit)):
                ref_url = chain_helpers.VERIFY._api_urls(run_id, commit)[2]
                replay_responses[ref_url] = raw_json({"ref": "refs/heads/method-v1.5-p0", "object": {"type": "commit", "sha": a0_commit}})
            replay_fetch = lambda url: replay_responses[url]
            identity = chain_helpers.VERIFY.validated_a0_identity(repo, a0_commit, authority_keys=keys_path, publication_receipt=a0_receipt, fetch=replay_fetch)

            value, _, _, _, _, _, fixture_temp, _ = fixture(helper.base)
            try:
                value["a0_identity"] = identity
                value["p0_publication_replay"] = {"a0_publication_receipt": a0_receipt, "raw_api_responses": [{"url": url, "body_base64": module.b64(replay_fetch(url))} for url in dict.fromkeys(urls)]}
                value["frozen_bindings"].update({
                    "acceptance_schema_sha256": module.sha256((repo / module.SCHEMA_REPO_PATH).read_bytes()),
                    "acceptance_verifier_sha256": module.sha256((repo / module.VERIFIER_REPO_PATH).read_bytes()),
                    "infrastructure_activation_workflow_sha256": module.sha256((repo / module.ACTIVATION_WORKFLOW_PATH).read_bytes()),
                    "p0_verifier_sha256": module.sha256((repo / module.P0_VERIFIER_PATH).read_bytes()),
                    "p0_schema_sha256": {path: module.sha256((repo / path).read_bytes()) for path in module.P0_SCHEMA_PATHS},
                })
                reseal(value, helper.p0a, helper.private_keys)
                helper.write(module.ACCEPTANCE_PATH, value); helper.commit_only(module.ACCEPTANCE_PATH, "bootstrap acceptance")
                acceptance_commit = helper.git("rev-parse", "HEAD")
                result = module.verify_committed(repo, acceptance_commit, keys_path)
                self.assertEqual(result["a0_commit"], a0_commit)
                self.assertEqual(result["raw_exchange_count"], 32)

                # A separately re-signed forged replay body is still rejected by
                # the pinned P0 validator, without falling back to the network.
                helper.git("checkout", "-qb", "replay-forgery", a0_commit)
                forged = copy.deepcopy(value)
                replay_body = base64.b64decode(forged["p0_publication_replay"]["raw_api_responses"][0]["body_base64"])
                forged["p0_publication_replay"]["raw_api_responses"][0]["body_base64"] = module.b64(replay_body.replace(b'"id": 41', b'"id": 99'))
                reseal(forged, helper.p0a, helper.private_keys)
                helper.write(module.ACCEPTANCE_PATH, forged); helper.commit_only(module.ACCEPTANCE_PATH, "forged replay")
                with self.assertRaises(ValueError):
                    module.verify_committed(repo, helper.git("rev-parse", "HEAD"), keys_path)

                helper.git("checkout", "-qb", "p0-pin-forgery", a0_commit)
                forged = copy.deepcopy(value); forged["frozen_bindings"]["p0_verifier_sha256"] = "0" * 64
                reseal(forged, helper.p0a, helper.private_keys)
                helper.write(module.ACCEPTANCE_PATH, forged); helper.commit_only(module.ACCEPTANCE_PATH, "forged P0 pin")
                with self.assertRaisesRegex(module.BootstrapAcceptanceError, "frozen binding"):
                    module.verify_committed(repo, helper.git("rev-parse", "HEAD"), keys_path)

                helper.git("checkout", "-qb", "workflow-pin-forgery", a0_commit)
                forged = copy.deepcopy(value); forged["frozen_bindings"]["infrastructure_activation_workflow_sha256"] = "0" * 64
                reseal(forged, helper.p0a, helper.private_keys)
                helper.write(module.ACCEPTANCE_PATH, forged); helper.commit_only(module.ACCEPTANCE_PATH, "forged workflow pin")
                with self.assertRaisesRegex(module.BootstrapAcceptanceError, "frozen binding"):
                    module.verify_committed(repo, helper.git("rev-parse", "HEAD"), keys_path)
            finally:
                fixture_temp.cleanup()

    def test_a0_identity_and_threshold_signatures_cannot_be_substituted(self) -> None:
        value = copy.deepcopy(self.value); value["a0_identity"]["commit"] = "9" * 40; reseal(value, self.p0a, self.keys)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); value["authentication"]["signatures"] = value["authentication"]["signatures"][:1]
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)
        value = copy.deepcopy(self.value); value["authentication"]["signatures"][0]["signature_base64"] = module.b64(b"x" * 64)
        with self.assertRaises(module.BootstrapAcceptanceError): self.verify(value)

    def test_acceptance_publication_must_be_exact_one_parent_one_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory); subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True); subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            path = repo / module.ACCEPTANCE_PATH; path.parent.mkdir(parents=True); path.write_text("{}\n")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            path.write_text('{"changed":true}\n'); (repo / "escape.txt").write_text("escape\n")
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "bad acceptance"], check=True)
            commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            with self.assertRaises(module.BootstrapAcceptanceError): module.verify_committed(repo, commit, self.keys_path)

    def test_cli_has_no_uncommitted_or_caller_selected_root_mode(self) -> None:
        result = subprocess.run([sys.executable, str(MODULE_PATH)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        source = MODULE_PATH.read_text()
        self.assertNotIn("--p0a", source); self.assertNotIn("--a0", source)
        self.assertIn("p0.validated_a0_identity", source)


if __name__ == "__main__": unittest.main()
