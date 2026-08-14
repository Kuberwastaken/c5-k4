#!/usr/bin/env python3
"""Verify a committed raw-wire Method v1.5 AWS/GitHub bootstrap receipt.

No network call or mutation is performed.  The only accepted entry point is an
exact one-path acceptance commit whose sole parent is a fully validated,
externally authorized P0A -> P0T -> A0 chain.
"""

from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any, Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_PATH = "results/benchmark/v1.5-bootstrap-acceptance/acceptance.json"
SCHEMA_REPO_PATH = "schemas/benchmark-aws-github-bootstrap-acceptance-v1.5.schema.json"
VERIFIER_REPO_PATH = "scripts/verify_benchmark_v15_aws_github_bootstrap_acceptance.py"
CONTRACT_PATH = "results/benchmark/v1.5-protocol/aws-github-bootstrap-contract.json"
HOST_PLAN_PATH = "results/benchmark/v1.5-protocol/controlled-host-provisioning-plan.json"
STORE_TEMPLATE_PATH = "infra/benchmark-v1.5/immutable-store/cloudformation.json"
HOST_TEMPLATE_PATH = "infra/benchmark-v1.5/controlled-host/cloudformation.json"
ACTIVATION_WORKFLOW_PATH = ".github/workflows/method-v15-infrastructure-activation.yml"
ACTIVATION_WORKFLOW_SHA256 = "b0f1656e6f2dbcb3884f0000cce171bc77afd775df531128b157a3f42cff4ea1"

CONTRACT_COMMIT = "b8eacd7fdbfecafa7f215a4f19fba950fb3d4e81"
PREFLIGHT_COMMIT = "4b6f23c79a4bee891cc74de98faf412d95f12e08"
CONTRACT_FILE_SHA256 = "aa7dae771b48c131b2b98db0a773daeadedfdf8441e89d2a57b74d590983de38"
CONTRACT_CANONICAL_SHA256 = "af54cd80ba257cad9d990238e513284276c8b67ca44aefb5fe18116c3fef1352"
HOST_PLAN_FILE_SHA256 = "966f48ad4228f98c384a14a2096236fac717ca28d87d9a1c8c91cce75de4df7d"
STORE_TEMPLATE_SHA256 = "08486d446a67f627ce88a859c6c70518d1ef5ccb40aca7ccbb8bf03715614d89"
HOST_TEMPLATE_SHA256 = "0af41e32554089c8fc48b30d84b442b6f6b3cca576b38014d1542dcd62e950f1"

SUBJECT = "repo:Kuberwastaken@97027230/c5-k4@1331829034:environment:benchmark-v15-production"
ENVIRONMENT = "benchmark-v15-production"
REGION = "ap-south-1"
DEPLOYER_PATH = "/c5k4/v1.5/bootstrap/"
CUSTODY_PATH = "/c5k4/v1.5/"
STORE_ROLE = "c5k4-v15-immutable-store-deployer"
HOST_ROLE = "c5k4-v15-controlled-host-deployer"
HARNESS_ROLE = "c5k4-v15-controlled-harness"
BOUNDARY_NAME = "c5k4-v1-5-custody-writer-boundary"
STORE_POLICY = "c5k4-v15-immutable-store-deployer"
HOST_POLICY = "c5k4-v15-controlled-host-deployer"
HARNESS_POLICY = "c5k4-v15-controlled-harness-custody-hop"
CUSTODY_POLICY = "c5k4-v1-5-private-custody-single-writer"
PAYLOAD_DOMAIN = "c5k4-method-v1.5-aws-github-bootstrap-acceptance-payload-2.0"
SIGNATURE_DOMAIN = "c5k4-method-v1.5-aws-github-bootstrap-acceptance-signature-2.0"

VARIABLE_NAMES = [
    "BENCHMARK_V15_AWS_REGION", "BENCHMARK_V15_TEMPLATE_SHA256", "BENCHMARK_V15_STACK_NAME",
    "BENCHMARK_V15_AWS_ROLE_ARN", "BENCHMARK_V15_HARNESS_PRINCIPAL_ARN",
    "BENCHMARK_V15_HOST_STACK_NAME", "BENCHMARK_V15_HOST_TEMPLATE_SHA256",
    "BENCHMARK_V15_HOST_AMI_ID", "BENCHMARK_V15_HOST_AMI_MEASUREMENTS_SHA256",
    "BENCHMARK_V15_HOST_AWS_ROLE_ARN",
]
GITHUB_IDS = [
    "github_repository", "github_oidc_subject", "github_environment", "github_environment_branches",
    "github_repository_variables", "github_environment_variables", "github_repository_secrets",
    "github_environment_secrets",
]
ROLE_LABELS = ("store_deployer", "host_deployer", "harness", "custody_writer")
AWS_IDS = ["aws_caller_identity", "aws_oidc_provider"] + [
    f"aws_{label}_{suffix}" for label in ROLE_LABELS
    for suffix in ("role", "inline_names", "inline_policy", "attached")
] + [
    "aws_harness_profile", "aws_boundary_metadata", "aws_boundary_version",
    "aws_store_change_set_pre_execution", "aws_store_stack", "aws_store_stack_resources",
]
EXPECTED_IDS = GITHUB_IDS + AWS_IDS
FORBIDDEN_KEYS = {"candidate_id", "cluster_id", "statement_text", "target_id", "target_rankings", "conjecture_id"}


P0_VERIFIER_PATH = "scripts/verify_benchmark_v15_p0_a0_publication.py"
P0_SCHEMA_PATHS = (
    "schemas/benchmark-p0a-v1.5.schema.json",
    "schemas/benchmark-p0t-v1.5.schema.json",
    "schemas/benchmark-a0-v1.5.schema.json",
    "schemas/benchmark-p0-publication-receipt-v1.5.schema.json",
)
P0_PIN_PATHS = (P0_VERIFIER_PATH, *P0_SCHEMA_PATHS)
OID = re.compile(r"^[0-9a-f]{40}$")
GITHUB_API_VERSION = "2022-11-28"
GITHUB_REQUEST_HEADERS = {
    "accept": "application/vnd.github+json",
    "user-agent": "c5k4-method-v1.5-bootstrap-observer",
    "x-github-api-version": GITHUB_API_VERSION,
}
AWS_REQUEST_HEADERS = {"content-type": "application/x-www-form-urlencoded; charset=utf-8"}
AWS_XML_NAMESPACES = {
    "IAM": "https://iam.amazonaws.com/doc/2010-05-08/",
    "STS": "https://sts.amazonaws.com/doc/2011-06-15/",
    "CLOUDFORMATION": "http://cloudformation.amazonaws.com/doc/2010-05-15/",
}


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


class BootstrapAcceptanceError(ValueError):
    pass


def git(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(repo), *args],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"},
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise BootstrapAcceptanceError("sanitized Git query failed") from exc


def commit_raw(repo: Path, commit: str, path: str) -> bytes:
    return git(repo, "show", f"{commit}:{path}")


def topology(repo: Path, commit: str, path: str) -> str:
    if OID.fullmatch(commit) is None or git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
        raise BootstrapAcceptanceError("acceptance commit is not an exact lowercase SHA-1 object ID")
    parents = git(repo, "show", "-s", "--format=%P", commit).decode().split()
    if len(parents) != 1:
        raise BootstrapAcceptanceError("acceptance publication must have exactly one parent")
    changed = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()
    if changed != [path]:
        raise BootstrapAcceptanceError(f"acceptance publication must change exactly {path}")
    return parents[0]


def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise BootstrapAcceptanceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapAcceptanceError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise BootstrapAcceptanceError(f"{label} must be one JSON object")
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: bytes | Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def domain_digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\0" + canonical(value)).hexdigest()


def without(value: dict[str, Any], *keys: str) -> dict[str, Any]:
    result = copy.deepcopy(value)
    for key in keys: result.pop(key, None)
    return result


def payload_sha256(value: dict[str, Any]) -> str:
    return domain_digest(PAYLOAD_DOMAIN, without(value, "authentication"))


def signature_message(payload_sha: str) -> bytes:
    return SIGNATURE_DOMAIN.encode("ascii") + b"\0" + bytes.fromhex(payload_sha)


def b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def decode_b64(value: Any, label: str, maximum: int = 2_000_000) -> bytes:
    try:
        raw = base64.b64decode(value, validate=True)
    except (TypeError, ValueError) as exc:
        raise BootstrapAcceptanceError(f"{label} is not canonical base64") from exc
    if len(raw) > maximum:
        raise BootstrapAcceptanceError(f"{label} exceeds size limit")
    return raw


def parse_headers(raw: bytes, label: str) -> dict[str, str]:
    if b"\n" in raw.replace(b"\r\n", b"") or (raw and not raw.endswith(b"\r\n")):
        raise BootstrapAcceptanceError(f"{label} headers are not exact CRLF lines")
    result: dict[str, str] = {}
    for line in raw.split(b"\r\n"):
        if not line: continue
        try:
            name, value = line.decode("ascii").split(":", 1)
        except (UnicodeDecodeError, ValueError) as exc:
            raise BootstrapAcceptanceError(f"{label} header line is invalid") from exc
        key = name.strip().casefold()
        if not re.fullmatch(r"[a-z0-9-]+", key) or key in result:
            raise BootstrapAcceptanceError(f"{label} header is duplicate or malformed")
        result[key] = value.strip()
    return result


def response_date(headers: dict[str, str], provider: str) -> datetime:
    required = "x-github-request-id" if provider == "GITHUB" else "x-amzn-requestid"
    if required not in headers or "date" not in headers:
        raise BootstrapAcceptanceError(f"{provider} response lacks server Date/request ID")
    if provider == "GITHUB":
        if re.fullmatch(r"[0-9A-F]{4,8}(?::[0-9A-F]{4,16}){4}", headers[required]) is None:
            raise BootstrapAcceptanceError("GitHub request ID syntax differs")
    elif re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", headers[required]) is None:
        raise BootstrapAcceptanceError("AWS request ID syntax differs")
    if re.fullmatch(r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), [0-9]{2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT", headers["date"]) is None:
        raise BootstrapAcceptanceError(f"{provider} server Date is not IMF-fixdate")
    try:
        result = parsedate_to_datetime(headers["date"])
    except (TypeError, ValueError) as exc:
        raise BootstrapAcceptanceError(f"{provider} server Date is invalid") from exc
    if result.tzinfo is None:
        raise BootstrapAcceptanceError(f"{provider} server Date lacks timezone")
    result = result.astimezone(timezone.utc)
    if result.strftime("%a, %d %b %Y %H:%M:%S GMT") != headers["date"]:
        raise BootstrapAcceptanceError(f"{provider} server Date is not canonical IMF-fixdate")
    return result


def iso_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise BootstrapAcceptanceError(f"{label} is not a UTC timestamp")
    try: return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc: raise BootstrapAcceptanceError(f"{label} is invalid") from exc


def decode_exchange(row: dict[str, Any]) -> tuple[bytes, bytes, dict[str, str], dict[str, str], datetime]:
    request, response = row["request"], row["response"]
    request_headers = parse_headers(decode_b64(request["headers_base64"], f"{row['id']} request headers", 64_000), row["id"])
    response_headers = parse_headers(decode_b64(response["headers_base64"], f"{row['id']} response headers", 64_000), row["id"])
    if any(key in request_headers for key in ("authorization", "cookie", "x-amz-security-token")):
        raise BootstrapAcceptanceError("credential-bearing request header was published")
    request_body = decode_b64(request["body_base64"], f"{row['id']} request body")
    response_body = decode_b64(response["body_base64"], f"{row['id']} response body")
    return request_body, response_body, request_headers, response_headers, response_date(response_headers, request["provider"])


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items(): yield key; yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value: yield from _walk_keys(child)


def xml_root(raw: bytes, label: str, service: str) -> ET.Element:
    try: root = ET.fromstring(raw)
    except ET.ParseError as exc: raise BootstrapAcceptanceError(f"{label} is not AWS XML") from exc
    expected_namespace = AWS_XML_NAMESPACES[service]
    prefix = "{" + expected_namespace + "}"
    if any(not isinstance(node.tag, str) or not node.tag.startswith(prefix) for node in root.iter()):
        raise BootstrapAcceptanceError(f"{label} AWS XML namespace closure differs")
    return root


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def xml_texts(root: ET.Element, name: str) -> list[str]:
    return [(node.text or "") for node in root.iter() if local(node.tag) == name]


def xml_one(root: ET.Element, name: str) -> str:
    values = xml_texts(root, name)
    if len(values) != 1: raise BootstrapAcceptanceError(f"AWS response requires exactly one {name}")
    return values[0]


def xml_members(root: ET.Element, container_name: str) -> list[str]:
    containers = [node for node in root.iter() if local(node.tag) == container_name]
    if len(containers) != 1: raise BootstrapAcceptanceError(f"AWS response requires exactly one {container_name}")
    return [(node.text or "") for node in containers[0] if local(node.tag) == "member"]


def aws_policy(root: ET.Element, field: str = "PolicyDocument") -> dict[str, Any]:
    return strict_json(urllib.parse.unquote(xml_one(root, field)).encode(), "AWS policy document")


def aws_request(raw: bytes, operation: str, service: str) -> dict[str, str]:
    try: parsed = urllib.parse.parse_qs(raw.decode("ascii"), keep_blank_values=True, strict_parsing=True)
    except (UnicodeDecodeError, ValueError) as exc: raise BootstrapAcceptanceError("AWS query request is malformed") from exc
    if any(len(values) != 1 for values in parsed.values()): raise BootstrapAcceptanceError("AWS query request has duplicate parameters")
    flat = {key: values[0] for key, values in parsed.items()}
    version = "2011-06-15" if service == "STS" else "2010-05-15" if service == "CLOUDFORMATION" else "2010-05-08"
    if flat.get("Action") != operation or flat.get("Version") != version:
        raise BootstrapAcceptanceError("AWS request action/version differs")
    return flat


def policy_statement(sid: str, actions: list[str], resource: Any, condition: dict | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"Sid": sid, "Effect": "Allow", "Action": actions, "Resource": resource}
    if condition is not None: result["Condition"] = condition
    return result


def expected_deployer_policy(label: str, account: str, values: dict[str, str], contract: dict[str, Any]) -> dict[str, Any]:
    if label == "store_deployer":
        privilege = contract["principals"]["immutable_store_deployer"]["least_privilege"]
        stack = f"arn:aws:cloudformation:{REGION}:{account}:stack/{values['BENCHMARK_V15_STACK_NAME']}/*"
        inspect = ["cloudformation:GetTemplateSummary", "cloudformation:ValidateTemplate"]
        stack_actions = [action for action in privilege["cloudformation_actions"] if action not in inspect]
        statements = [
            policy_statement("InspectImmutableStoreTemplate", inspect, "*"),
            policy_statement("ExactImmutableStoreStack", stack_actions, stack),
            policy_statement("ExactImmutableStoreIam", privilege["iam_actions"], f"arn:aws:iam::{account}:role/c5k4/v1.5/*"),
            policy_statement("ExactImmutableStoreKms", privilege["kms_actions"], "*"),
            policy_statement("ExactImmutableStoreS3", privilege["s3_actions"], "arn:aws:s3:::*"),
        ]
    else:
        privilege = contract["principals"]["controlled_host_deployer"]["least_privilege"]
        stack = f"arn:aws:cloudformation:{REGION}:{account}:stack/{values['BENCHMARK_V15_HOST_STACK_NAME']}/*"
        iam_read = [action for action in privilege["iam_actions"] if action != "iam:PassRole"]
        inspect = ["cloudformation:GetTemplateSummary", "cloudformation:ValidateTemplate"]
        stack_actions = [action for action in privilege["cloudformation_actions"] if action not in inspect]
        statements = [
            policy_statement("InspectControlledHostTemplate", inspect, "*"),
            policy_statement("ExactControlledHostStack", stack_actions, stack),
            policy_statement("ExactControlledHostEc2", privilege["ec2_actions"], "*", {"StringEquals": {"ec2:Region": REGION}}),
            policy_statement("InspectExactHarness", iam_read, [values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"], f"arn:aws:iam::{account}:instance-profile{DEPLOYER_PATH}{HARNESS_ROLE}"]),
            policy_statement("PassExactHarnessToEc2", ["iam:PassRole"], values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"], {"StringEquals": {"iam:PassedToService": "ec2.amazonaws.com"}}),
        ]
    return {"Version": "2012-10-17", "Statement": statements}


def oidc_trust(account: str) -> dict[str, Any]:
    return {"Version": "2012-10-17", "Statement": [{
        "Sid": "ExactImmutableGitHubEnvironment", "Effect": "Allow",
        "Principal": {"Federated": f"arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com"},
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": {"StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com", "token.actions.githubusercontent.com:sub": SUBJECT}},
    }]}


def ec2_trust() -> dict[str, Any]:
    return {"Version": "2012-10-17", "Statement": [{"Sid": "ExactEc2Harness", "Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}


def custody_trust(harness_arn: str, external_id: str) -> dict[str, Any]:
    return {"Version": "2012-10-17", "Statement": [{"Sid": "OnlyControlledHarness", "Effect": "Allow", "Principal": {"AWS": harness_arn}, "Action": "sts:AssumeRole", "Condition": {"StringEquals": {"sts:ExternalId": external_id}}}]}


def render_template(value: Any, substitutions: dict[str, Any]) -> Any:
    if isinstance(value, list): return [render_template(child, substitutions) for child in value]
    if not isinstance(value, dict): return value
    if set(value) == {"Ref"}:
        if value["Ref"] not in substitutions: raise BootstrapAcceptanceError("unresolved template Ref")
        return substitutions[value["Ref"]]
    if set(value) == {"Fn::GetAtt"}:
        parts = value["Fn::GetAtt"]; key = f"{parts[0]}.{parts[1]}" if isinstance(parts, list) and len(parts) == 2 else ""
        if key not in substitutions: raise BootstrapAcceptanceError("unresolved template GetAtt")
        return substitutions[key]
    if set(value) == {"Fn::Sub"}:
        text = value["Fn::Sub"]
        if not isinstance(text, str): raise BootstrapAcceptanceError("unsupported template Sub")
        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in substitutions: raise BootstrapAcceptanceError("unresolved template Sub variable")
            return str(substitutions[key])
        return re.sub(r"\$\{([^}]+)\}", replace, text)
    return {key: render_template(child, substitutions) for key, child in value.items()}


def expected_boundary(account: str) -> dict[str, Any]:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {"Sid": "AllowExactImmutableCustodyOperations", "Effect": "Allow", "Resource": "*", "Action": sorted({
                "s3:GetBucketEncryption", "s3:GetBucketLocation", "s3:GetBucketObjectLockConfiguration", "s3:GetBucketPolicy",
                "s3:GetBucketPolicyStatus", "s3:GetBucketPublicAccessBlock", "s3:GetBucketVersioning", "s3:ListBucket",
                "s3:ListBucketVersions", "s3:GetObject", "s3:GetObjectRetention", "s3:GetObjectVersion", "s3:PutObject",
                "s3:PutObjectRetention", "kms:Decrypt", "kms:DescribeKey", "kms:Encrypt", "kms:GenerateDataKey",
            })},
            {"Sid": "DenyDestructiveCustodyOperations", "Effect": "Deny", "Principal": "*", "Resource": "*", "Action": [
                "kms:DisableKey", "kms:ScheduleKeyDeletion", "s3:DeleteBucket", "s3:DeleteObject", "s3:DeleteObjectVersion",
                "s3:PutBucketVersioning", "s3:PutEncryptionConfiguration", "s3:PutObjectLockConfiguration",
            ]},
        ],
    }


def role_from_xml(root: ET.Element) -> dict[str, Any]:
    boundary = xml_texts(root, "PermissionsBoundaryArn")
    return {
        "name": xml_one(root, "RoleName"), "arn": xml_one(root, "Arn"), "path": xml_one(root, "Path"),
        "max_session": int(xml_one(root, "MaxSessionDuration")),
        "trust": strict_json(urllib.parse.unquote(xml_one(root, "AssumeRolePolicyDocument")).encode(), "AWS role trust"),
        "boundary": boundary[0] if len(boundary) == 1 else None if not boundary else "INVALID",
    }


def parse_github(receipts: dict[str, tuple[dict[str, Any], bytes]], contract: dict[str, Any]) -> tuple[dict[str, str], list[datetime]]:
    base = "https://api.github.com/repos/Kuberwastaken/c5-k4"
    urls = {
        "github_repository": base,
        "github_oidc_subject": base + "/actions/oidc/customization/sub",
        "github_environment": base + f"/environments/{ENVIRONMENT}",
        "github_environment_branches": base + f"/environments/{ENVIRONMENT}/deployment-branch-policies",
        "github_repository_variables": base + "/actions/variables?per_page=100",
        "github_environment_variables": base + f"/environments/{ENVIRONMENT}/variables?per_page=100",
        "github_repository_secrets": base + "/actions/secrets?per_page=100",
        "github_environment_secrets": base + f"/environments/{ENVIRONMENT}/secrets?per_page=100",
    }
    decoded: dict[str, dict[str, Any]] = {}; times: list[datetime] = []
    for receipt_id in GITHUB_IDS:
        row, body = receipts[receipt_id]
        request = row["request"]
        if request != {"provider": "GITHUB", "service": "REST", "operation": receipt_id, "method": "GET", "url": urls[receipt_id], "headers_base64": request["headers_base64"], "body_base64": ""}:
            raise BootstrapAcceptanceError(f"arbitrary or malformed GitHub API request: {receipt_id}")
        if row["_request_headers"] != GITHUB_REQUEST_HEADERS:
            raise BootstrapAcceptanceError(f"GitHub stable request headers differ: {receipt_id}")
        if "link" in row["_response_headers"] and re.search(r'rel\s*=\s*"next"', row["_response_headers"]["link"], re.IGNORECASE):
            raise BootstrapAcceptanceError(f"GitHub pagination is not closed: {receipt_id}")
        decoded[receipt_id] = strict_json(body, receipt_id); times.append(receipts[receipt_id][0]["_date"])
    repository = decoded["github_repository"]
    owner = repository.get("owner")
    if repository.get("id") != 1331829034 or repository.get("name") != "c5-k4" or repository.get("full_name") != "Kuberwastaken/c5-k4" or repository.get("default_branch") != "main" or not isinstance(owner, dict) or owner.get("login") != "Kuberwastaken" or owner.get("id") != 97027230:
        raise BootstrapAcceptanceError("GitHub raw repository identity differs")
    oidc = decoded["github_oidc_subject"]
    if oidc != {"use_default": False, "use_immutable_subject": True, "include_claim_keys": ["repo", "context"]}:
        raise BootstrapAcceptanceError("GitHub immutable repo/context OIDC response differs")
    if contract["repository_identity"]["immutable_oidc_subject"] != SUBJECT:
        raise BootstrapAcceptanceError("frozen contract immutable subject differs")
    environment = decoded["github_environment"]
    if environment.get("name") != ENVIRONMENT or environment.get("deployment_branch_policy") != {"protected_branches": False, "custom_branch_policies": True}:
        raise BootstrapAcceptanceError("GitHub environment is not custom-branch protected")
    rules = environment.get("protection_rules")
    if not isinstance(rules, list): raise BootstrapAcceptanceError("GitHub environment protection rules absent")
    required = [row for row in rules if isinstance(row, dict) and row.get("type") == "required_reviewers"]
    if len(required) != 1 or required[0].get("prevent_self_review") is not True:
        raise BootstrapAcceptanceError("GitHub prevent-self-review rule absent")
    reviewers = required[0].get("reviewers")
    if not isinstance(reviewers, list) or not reviewers: raise BootstrapAcceptanceError("GitHub independent reviewer absent")
    reviewer_ids: set[tuple[str, int]] = set()
    for row in reviewers:
        reviewer = row.get("reviewer") if isinstance(row, dict) else None
        identity = (row.get("type"), reviewer.get("id")) if isinstance(reviewer, dict) else (None, None)
        if identity[0] not in {"User", "Team"} or not isinstance(identity[1], int) or not isinstance(reviewer.get("login"), str) or not reviewer["login"] or identity in reviewer_ids:
            raise BootstrapAcceptanceError("GitHub reviewer identity is malformed or duplicate")
        reviewer_ids.add(identity)
    branches = decoded["github_environment_branches"]
    branch_rows = branches.get("branch_policies")
    if branches.get("total_count") != 1 or not isinstance(branch_rows, list) or len(branch_rows) != 1:
        raise BootstrapAcceptanceError("GitHub environment branch closure is not exact main-only")
    branch = branch_rows[0]
    if not isinstance(branch, dict) or set(branch) != {"id", "node_id", "name", "type"} or not isinstance(branch["id"], int) or not isinstance(branch["node_id"], str) or branch["name"] != "main" or branch["type"] != "branch":
        raise BootstrapAcceptanceError("GitHub environment branch closure is not exact main-only")
    variables = decoded["github_repository_variables"]
    rows = variables.get("variables")
    if variables.get("total_count") != 10 or not isinstance(rows, list) or len(rows) != 10:
        raise BootstrapAcceptanceError("GitHub repository variable count differs")
    values: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"name", "value", "created_at", "updated_at"} or row["name"] in values:
            raise BootstrapAcceptanceError("GitHub raw variable row is open, malformed, or duplicate")
        values[row["name"]] = row["value"]
        if not iso_time(row["created_at"], "GitHub variable creation") <= iso_time(row["updated_at"], "GitHub variable update") <= receipts["github_repository_variables"][0]["_date"]:
            raise BootstrapAcceptanceError("GitHub variable chronology exceeds raw server Date")
    if sorted(values) != sorted(VARIABLE_NAMES): raise BootstrapAcceptanceError("GitHub exact variable names differ")
    for empty_id, key in (("github_environment_variables", "variables"), ("github_repository_secrets", "secrets"), ("github_environment_secrets", "secrets")):
        value = decoded[empty_id]
        if value != {"total_count": 0, key: []}: raise BootstrapAcceptanceError(f"{empty_id} is not exact empty closure")
    if values["BENCHMARK_V15_AWS_REGION"] != REGION or values["BENCHMARK_V15_TEMPLATE_SHA256"] != STORE_TEMPLATE_SHA256 or values["BENCHMARK_V15_HOST_TEMPLATE_SHA256"] != HOST_TEMPLATE_SHA256:
        raise BootstrapAcceptanceError("GitHub region/template variables differ")
    if not re.fullmatch(r"[A-Za-z][-A-Za-z0-9]{0,127}", values["BENCHMARK_V15_STACK_NAME"]) or not re.fullmatch(r"[A-Za-z][-A-Za-z0-9]{0,127}", values["BENCHMARK_V15_HOST_STACK_NAME"]) or values["BENCHMARK_V15_STACK_NAME"] == values["BENCHMARK_V15_HOST_STACK_NAME"]:
        raise BootstrapAcceptanceError("GitHub stack-name variables differ")
    if not re.fullmatch(r"ami-[0-9a-f]{8,17}", values["BENCHMARK_V15_HOST_AMI_ID"]) or not re.fullmatch(r"[0-9a-f]{64}", values["BENCHMARK_V15_HOST_AMI_MEASUREMENTS_SHA256"]):
        raise BootstrapAcceptanceError("GitHub AMI variable grammar differs")
    return values, times


def parse_aws(receipts: dict[str, tuple[dict[str, Any], bytes]], contract: dict[str, Any], values: dict[str, str], store_template: dict[str, Any]) -> tuple[list[datetime], dict[str, str], str, str]:
    times = [receipts[row][0]["_date"] for row in AWS_IDS]
    roots = {receipt_id: xml_root(receipts[receipt_id][1], receipt_id, receipts[receipt_id][0]["request"]["service"]) for receipt_id in AWS_IDS}
    for receipt_id, root in roots.items():
        if receipts[receipt_id][0]["_request_headers"] != AWS_REQUEST_HEADERS:
            raise BootstrapAcceptanceError(f"AWS stable request headers differ: {receipt_id}")
        if xml_texts(root, "NextToken") or xml_texts(root, "Marker"):
            raise BootstrapAcceptanceError(f"AWS pagination is not closed: {receipt_id}")
        if xml_one(root, "RequestId") != receipts[receipt_id][0]["_request_id"]:
            raise BootstrapAcceptanceError(f"AWS body/header request ID reconciliation differs: {receipt_id}")
    caller = roots["aws_caller_identity"]
    account = xml_one(caller, "Account"); caller_arn = xml_one(caller, "Arn")
    if not re.fullmatch(r"[0-9]{12}", account) or f"::{account}:" not in caller_arn: raise BootstrapAcceptanceError("AWS caller identity differs")
    provider_arn = f"arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com"
    provider = roots["aws_oidc_provider"]
    if xml_one(provider, "Url") != "token.actions.githubusercontent.com" or xml_members(provider, "ClientIDList") != ["sts.amazonaws.com"]:
        raise BootstrapAcceptanceError("AWS OIDC provider URL/audience differs")
    thumbprints = xml_members(provider, "ThumbprintList")
    if not thumbprints or len(thumbprints) != len(set(thumbprints)) or any(re.fullmatch(r"[0-9a-f]{40}", item) is None for item in thumbprints):
        raise BootstrapAcceptanceError("AWS OIDC provider thumbprint closure differs")

    if contract["principals"]["immutable_store_deployer"]["custody_writer_creation"]["external_id_policy"] != "SHA256(candidate_commit:template_sha256:stack_name:harness_principal_arn)":
        raise BootstrapAcceptanceError("frozen external-ID formula differs")
    change_set = roots["aws_store_change_set_pre_execution"]
    if xml_texts(change_set, "ClientToken"):
        raise BootstrapAcceptanceError("DescribeChangeSet contains undocumented synthetic ClientToken authority")
    if xml_one(change_set, "ChangeSetType") != "CREATE" or xml_one(change_set, "Status") != "CREATE_COMPLETE" or xml_one(change_set, "ExecutionStatus") != "AVAILABLE":
        raise BootstrapAcceptanceError("pre-execution immutable-store change-set state differs")
    description = re.fullmatch(r"candidate=([0-9a-f]{40}) template=([0-9a-f]{64}) parameters=([0-9a-f]{64})", xml_one(change_set, "Description"))
    if description is None or description.group(2) != STORE_TEMPLATE_SHA256:
        raise BootstrapAcceptanceError("immutable-store change-set candidate/template binding differs")
    candidate_commit = description.group(1)
    external_id = hashlib.sha256(
        f"{candidate_commit}:{STORE_TEMPLATE_SHA256}:{values['BENCHMARK_V15_STACK_NAME']}:{values['BENCHMARK_V15_HARNESS_PRINCIPAL_ARN']}".encode("ascii")
    ).hexdigest()
    deployment_parameters = {
        "aws_region": REGION, "harness_external_id": external_id,
        "harness_external_id_policy": "SHA256(candidate_commit:template_sha256:stack_name:harness_principal_arn)",
        "harness_principal_arn": values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"],
        "private_prefix": "private/c5k4/v1.5", "retention_years": 3,
        "stack_name": values["BENCHMARK_V15_STACK_NAME"],
    }
    parameters_sha256 = sha256(deployment_parameters)
    if description.group(3) != parameters_sha256:
        raise BootstrapAcceptanceError("pre-execution change-set deployment-parameter digest differs")
    change_set_name = xml_one(change_set, "ChangeSetName")
    if re.fullmatch(rf"c5k4-v15-{parameters_sha256[:16]}-[1-9][0-9]*", change_set_name) is None:
        raise BootstrapAcceptanceError("pre-execution change-set name differs")
    change_set_id = xml_one(change_set, "ChangeSetId")
    stack_id = xml_one(change_set, "StackId")
    uuid = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    expected_stack_arn = rf"arn:aws:cloudformation:{REGION}:{account}:stack/{re.escape(values['BENCHMARK_V15_STACK_NAME'])}/{uuid}"
    if re.fullmatch(expected_stack_arn, stack_id) is None:
        raise BootstrapAcceptanceError("pre-execution stack ID is not the exact frozen CloudFormation stack ARN")
    if xml_one(change_set, "StackName") != values["BENCHMARK_V15_STACK_NAME"] or re.fullmatch(rf"arn:aws:cloudformation:{REGION}:{account}:changeSet/{re.escape(change_set_name)}/{uuid}", change_set_id) is None:
        raise BootstrapAcceptanceError("pre-execution change-set identity differs")
    if xml_members(change_set, "Capabilities") != ["CAPABILITY_IAM"]:
        raise BootstrapAcceptanceError("pre-execution change-set capabilities differ")
    try: creation_time = datetime.fromisoformat(xml_one(change_set, "CreationTime").replace("Z", "+00:00"))
    except ValueError as exc: raise BootstrapAcceptanceError("pre-execution change-set creation time differs") from exc
    if creation_time.tzinfo is None or creation_time.astimezone(timezone.utc) > receipts["aws_store_change_set_pre_execution"][0]["_date"]:
        raise BootstrapAcceptanceError("pre-execution change-set creation time exceeds capture")
    change_containers = [node for node in change_set.iter() if local(node.tag) == "Changes"]
    if len(change_containers) != 1:
        raise BootstrapAcceptanceError("pre-execution change-set resource closure differs")
    planned: dict[str, str] = {}
    change_members = list(change_containers[0])
    if len(change_members) != 5 or any(local(node.tag) != "member" for node in change_members):
        raise BootstrapAcceptanceError("pre-execution Changes must contain exactly five member elements")
    for member in change_members:
        resource_changes = [node for node in member if local(node.tag) == "ResourceChange"]
        type_nodes = [node for node in member if local(node.tag) == "Type"]
        if len(resource_changes) != 1 or len(type_nodes) != 1 or (type_nodes[0].text or "") != "Resource" or len(member) != 2:
            raise BootstrapAcceptanceError("pre-execution resource change shape differs")
        field_rows = [(local(child.tag), child.text or "") for child in resource_changes[0]]
        allowed = {"Action", "LogicalResourceId", "ResourceType", "Replacement"}
        if any(name not in allowed for name, _ in field_rows) or len({name for name, _ in field_rows}) != len(field_rows):
            raise BootstrapAcceptanceError("pre-execution ResourceChange has duplicate or unrecognized fields")
        fields = dict(field_rows)
        if fields.get("Action") != "Add" or set(fields) not in ({"Action", "LogicalResourceId", "ResourceType"}, {"Action", "LogicalResourceId", "ResourceType", "Replacement"}) or fields.get("Replacement", "") != "":
            raise BootstrapAcceptanceError("pre-execution resource change is not exact Add")
        if fields["LogicalResourceId"] in planned: raise BootstrapAcceptanceError("duplicate pre-execution resource change")
        planned[fields["LogicalResourceId"]] = fields["ResourceType"]

    stack = roots["aws_store_stack"]
    if xml_one(stack, "StackName") != values["BENCHMARK_V15_STACK_NAME"] or xml_one(stack, "StackId") != stack_id or xml_one(stack, "ChangeSetId") != change_set_id or xml_one(stack, "StackStatus") != "CREATE_COMPLETE":
        raise BootstrapAcceptanceError("post-execution immutable-store stack/change-set linkage is absent or incomplete")
    if not receipts["aws_store_change_set_pre_execution"][0]["_date"] < receipts["aws_store_stack"][0]["_date"]:
        raise BootstrapAcceptanceError("pre-execution change-set capture does not precede post-execution stack evidence")
    if xml_texts(stack, "OutputKey") or xml_texts(stack, "OutputValue"):
        raise BootstrapAcceptanceError("immutable-store stack unexpectedly exports a value")
    parameters = {}
    for member in [node for node in stack.iter() if local(node.tag) == "member"]:
        children = {local(child.tag): child.text or "" for child in member}
        if set(children) == {"ParameterKey", "ParameterValue"}: parameters[children["ParameterKey"]] = children["ParameterValue"]
    if set(parameters) != {"HarnessPrincipalArn", "HarnessExternalId", "PrivatePrefix", "RetentionYears"} or parameters["HarnessPrincipalArn"] != values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"] or parameters["HarnessExternalId"] != "****" or parameters["PrivatePrefix"] != "private/c5k4/v1.5" or parameters["RetentionYears"] != "3":
        raise BootstrapAcceptanceError("immutable-store stack parameter reconciliation differs")
    resources: dict[str, tuple[str, str, str]] = {}
    for member in [node for node in roots["aws_store_stack_resources"].iter() if local(node.tag) == "member"]:
        children = {local(child.tag): child.text or "" for child in member}
        if {"LogicalResourceId", "PhysicalResourceId", "ResourceType", "ResourceStatus"} <= set(children):
            logical = children["LogicalResourceId"]
            if logical in resources: raise BootstrapAcceptanceError("duplicate CloudFormation stack resource")
            resources[logical] = (children["PhysicalResourceId"], children["ResourceType"], children["ResourceStatus"])
    expected_types = {"CustodyBucket": "AWS::S3::Bucket", "CustodyBucketPolicy": "AWS::S3::BucketPolicy", "CustodyKey": "AWS::KMS::Key", "CustodyWriterPolicy": "AWS::IAM::Policy", "CustodyWriterRole": "AWS::IAM::Role"}
    if planned != expected_types: raise BootstrapAcceptanceError("pre-execution resource change closure differs")
    if set(resources) != set(expected_types) or any(resources[name][1:] != (kind, "CREATE_COMPLETE") for name, kind in expected_types.items()):
        raise BootstrapAcceptanceError("immutable-store stack resource closure differs")
    custody_name = resources["CustodyWriterRole"][0]
    if not re.fullmatch(r"[A-Za-z0-9+=,.@_-]{1,64}", custody_name): raise BootstrapAcceptanceError("custody writer physical role name differs")

    expected_roles = {
        "store_deployer": (STORE_ROLE, DEPLOYER_PATH, 1800, values["BENCHMARK_V15_AWS_ROLE_ARN"], oidc_trust(account), STORE_POLICY),
        "host_deployer": (HOST_ROLE, DEPLOYER_PATH, 1800, values["BENCHMARK_V15_HOST_AWS_ROLE_ARN"], oidc_trust(account), HOST_POLICY),
        "harness": (HARNESS_ROLE, DEPLOYER_PATH, 3600, values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"], ec2_trust(), HARNESS_POLICY),
        "custody_writer": (custody_name, CUSTODY_PATH, 3600, f"arn:aws:iam::{account}:role{CUSTODY_PATH}{custody_name}", custody_trust(values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"], external_id), CUSTODY_POLICY),
    }
    role_values: dict[str, dict[str, Any]] = {}
    policy_digests: dict[str, str] = {}
    role_arns: set[str] = set()
    for label, (name, path, duration, arn, expected_trust, policy_name) in expected_roles.items():
        observed = role_from_xml(roots[f"aws_{label}_role"]); role_values[label] = observed
        expected_boundary_arn = f"arn:aws:iam::{account}:policy/{BOUNDARY_NAME}" if label == "custody_writer" else None
        if observed != {"name": name, "arn": arn, "path": path, "max_session": duration, "trust": expected_trust, "boundary": expected_boundary_arn} or arn in role_arns:
            raise BootstrapAcceptanceError(f"AWS exact role/trust/path/boundary differs: {label}")
        role_arns.add(arn)
        policy_digests[f"{label}_trust"] = sha256(observed["trust"])
        names = xml_members(roots[f"aws_{label}_inline_names"], "PolicyNames")
        if names != [policy_name] or xml_one(roots[f"aws_{label}_inline_names"], "IsTruncated") != "false":
            raise BootstrapAcceptanceError(f"AWS inline policy-name closure differs: {label}")
        attached = roots[f"aws_{label}_attached"]
        if xml_texts(attached, "PolicyName") or xml_texts(attached, "PolicyArn") or xml_one(attached, "IsTruncated") != "false":
            raise BootstrapAcceptanceError(f"AWS managed policy attachment closure differs: {label}")
        policy_root = roots[f"aws_{label}_inline_policy"]
        if xml_one(policy_root, "RoleName") != name or xml_one(policy_root, "PolicyName") != policy_name:
            raise BootstrapAcceptanceError(f"AWS inline policy identity differs: {label}")
        policy = aws_policy(policy_root)
        if label in {"store_deployer", "host_deployer"}: expected_policy = expected_deployer_policy(label, account, values, contract)
        elif label == "harness":
            expected_policy = {"Version": "2012-10-17", "Statement": [policy_statement("OnlyExactCustodyWriter", ["sts:AssumeRole"], expected_roles["custody_writer"][3], {"StringEquals": {"sts:ExternalId": external_id}})]}
        else:
            substitutions = {
                "AWS::Partition": "aws", "AWS::AccountId": account, "AWS::Region": REGION, "AWS::URLSuffix": "amazonaws.com",
                "HarnessPrincipalArn": values["BENCHMARK_V15_HARNESS_PRINCIPAL_ARN"], "HarnessExternalId": external_id,
                "PrivatePrefix": "private/c5k4/v1.5", "RetentionYears": 3,
                "CustodyBucket": resources["CustodyBucket"][0], "CustodyBucket.Arn": f"arn:aws:s3:::{resources['CustodyBucket'][0]}",
                "CustodyKey": resources["CustodyKey"][0], "CustodyKey.Arn": f"arn:aws:kms:{REGION}:{account}:key/{resources['CustodyKey'][0]}",
                "CustodyWriterRole": custody_name, "CustodyWriterRole.Arn": expected_roles["custody_writer"][3],
            }
            expected_policy = render_template(store_template["Resources"]["CustodyWriterPolicy"]["Properties"]["PolicyDocument"], substitutions)
        if policy != expected_policy: raise BootstrapAcceptanceError(f"AWS exact normalized permission document differs: {label}")
        policy_digests[label] = sha256(policy)

    profile = roots["aws_harness_profile"]
    if xml_one(profile, "InstanceProfileName") != HARNESS_ROLE or xml_one(profile, "Path") != DEPLOYER_PATH or xml_one(profile, "Arn") != f"arn:aws:iam::{account}:instance-profile{DEPLOYER_PATH}{HARNESS_ROLE}" or xml_texts(profile, "RoleName") != [HARNESS_ROLE]:
        raise BootstrapAcceptanceError("AWS harness instance profile differs")
    boundary_meta = roots["aws_boundary_metadata"]
    boundary_arn = f"arn:aws:iam::{account}:policy/{BOUNDARY_NAME}"
    if xml_one(boundary_meta, "Arn") != boundary_arn or xml_one(boundary_meta, "PolicyName") != BOUNDARY_NAME or xml_one(boundary_meta, "Path") != "/":
        raise BootstrapAcceptanceError("AWS boundary metadata differs")
    default_version = xml_one(boundary_meta, "DefaultVersionId")
    boundary_version = roots["aws_boundary_version"]
    if xml_one(boundary_version, "VersionId") != default_version or xml_one(boundary_version, "IsDefaultVersion") != "true":
        raise BootstrapAcceptanceError("AWS boundary default version reconciliation differs")
    boundary_policy = aws_policy(boundary_version, "Document")
    if boundary_policy != expected_boundary(account): raise BootstrapAcceptanceError("AWS exact boundary policy differs")
    policy_digests["custody_writer_boundary"] = sha256(boundary_policy)

    # Requests are checked only after raw state supplies the generated custody name.
    expected_params: dict[str, tuple[str, str, dict[str, str]]] = {
        "aws_caller_identity": ("STS", "GetCallerIdentity", {}),
        "aws_oidc_provider": ("IAM", "GetOpenIDConnectProvider", {"OpenIDConnectProviderArn": provider_arn}),
        "aws_harness_profile": ("IAM", "GetInstanceProfile", {"InstanceProfileName": HARNESS_ROLE}),
        "aws_boundary_metadata": ("IAM", "GetPolicy", {"PolicyArn": boundary_arn}),
        "aws_boundary_version": ("IAM", "GetPolicyVersion", {"PolicyArn": boundary_arn, "VersionId": default_version}),
        "aws_store_change_set_pre_execution": ("CLOUDFORMATION", "DescribeChangeSet", {"StackName": values["BENCHMARK_V15_STACK_NAME"], "ChangeSetName": change_set_name}),
        "aws_store_stack": ("CLOUDFORMATION", "DescribeStacks", {"StackName": values["BENCHMARK_V15_STACK_NAME"]}),
        "aws_store_stack_resources": ("CLOUDFORMATION", "DescribeStackResources", {"StackName": values["BENCHMARK_V15_STACK_NAME"]}),
    }
    for label, (name, _, _, _, _, policy_name) in expected_roles.items():
        expected_params[f"aws_{label}_role"] = ("IAM", "GetRole", {"RoleName": name})
        expected_params[f"aws_{label}_inline_names"] = ("IAM", "ListRolePolicies", {"RoleName": name})
        expected_params[f"aws_{label}_inline_policy"] = ("IAM", "GetRolePolicy", {"RoleName": name, "PolicyName": policy_name})
        expected_params[f"aws_{label}_attached"] = ("IAM", "ListAttachedRolePolicies", {"RoleName": name})
    for receipt_id in AWS_IDS:
        row, _ = receipts[receipt_id]; request = row["request"]
        service, operation, parameters_expected = expected_params[receipt_id]
        url = "https://sts.amazonaws.com/" if service == "STS" else f"https://cloudformation.{REGION}.amazonaws.com/" if service == "CLOUDFORMATION" else "https://iam.amazonaws.com/"
        if request["provider"] != "AWS" or request["service"] != service or request["operation"] != operation or request["method"] != "POST" or request["url"] != url:
            raise BootstrapAcceptanceError(f"arbitrary AWS API request: {receipt_id}")
        if local(roots[receipt_id].tag) != operation + "Response":
            raise BootstrapAcceptanceError(f"AWS response root differs from requested API: {receipt_id}")
        body, _, _, _, _ = decode_exchange(row)
        observed = aws_request(body, operation, service); observed.pop("Action"); observed.pop("Version")
        if observed != parameters_expected: raise BootstrapAcceptanceError(f"AWS API parameters differ: {receipt_id}")
    return times, policy_digests, sha256(thumbprints), candidate_commit


def authority_keys(keys_file: Path, p0a: dict[str, Any]) -> dict[str, bytes]:
    try: supplied = strict_json(keys_file.read_bytes(), "offline authority keys")
    except OSError as exc: raise BootstrapAcceptanceError("cannot read offline authority keys") from exc
    if set(supplied) != {"schema", "keys"} or supplied["schema"] != "c5k4-method-v1.5-offline-a0-authority-keys-1.0":
        raise BootstrapAcceptanceError("offline authority key file shape differs")
    frozen = {row["authority_id"]: row["verification_key_sha256"] for row in p0a["authority_policy"]["independent_authorities"]}
    result: dict[str, bytes] = {}
    for row in supplied["keys"]:
        if not isinstance(row, dict) or set(row) != {"authority_id", "public_key_base64"} or row["authority_id"] in result:
            raise BootstrapAcceptanceError("offline authority key row differs")
        raw = decode_b64(row["public_key_base64"], "offline authority key", 32)
        if len(raw) != 32 or frozen.get(row["authority_id"]) != sha256(raw): raise BootstrapAcceptanceError("offline key differs from P0A roster")
        result[row["authority_id"]] = raw
    if set(result) != set(frozen): raise BootstrapAcceptanceError("offline key closure differs from P0A roster")
    return result


def verify_signatures(value: dict[str, Any], p0a: dict[str, Any], keys: dict[str, bytes], last_observation: datetime) -> None:
    authentication = value["authentication"]; payload = payload_sha256(value)
    if authentication["payload_sha256"] != payload: raise BootstrapAcceptanceError("acceptance payload digest mismatch")
    threshold = p0a["authority_policy"]["required_independent_signature_count"]
    if len(authentication["signatures"]) < threshold: raise BootstrapAcceptanceError("acceptance signature threshold absent")
    seen: set[str] = set()
    for row in authentication["signatures"]:
        authority_id = row["authority_id"]
        if authority_id in seen or authority_id not in keys or row["verification_key_sha256"] != sha256(keys[authority_id]) or row["signed_payload_sha256"] != payload:
            raise BootstrapAcceptanceError("acceptance signer is duplicate, unfrozen, or misbound")
        try: signed_at = datetime.strptime(row["signed_at_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError as exc: raise BootstrapAcceptanceError("acceptance signing time invalid") from exc
        if not last_observation <= signed_at <= last_observation + timedelta(seconds=900):
            raise BootstrapAcceptanceError("acceptance signature time is outside live observation window")
        try: Ed25519PublicKey.from_public_bytes(keys[authority_id]).verify(decode_b64(row["signature_base64"], "acceptance signature", 64), signature_message(payload))
        except InvalidSignature as exc: raise BootstrapAcceptanceError("acceptance signature invalid") from exc
        seen.add(authority_id)


def verify_payload(value: dict[str, Any], schema: dict[str, Any], contract: dict[str, Any], store_template: dict[str, Any], identity: dict[str, Any], p0a: dict[str, Any], keys_file: Path) -> dict[str, Any]:
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]; raise BootstrapAcceptanceError(f"schema rejection at {list(error.absolute_path)}: {error.message}")
    if set(_walk_keys(value)) & FORBIDDEN_KEYS: raise BootstrapAcceptanceError("target/candidate semantic field present")
    if value["a0_identity"] != identity: raise BootstrapAcceptanceError("acceptance A0 canonical reference differs from validated parent")
    transcript = value["transcript"]
    if [row["id"] for row in transcript] != EXPECTED_IDS: raise BootstrapAcceptanceError("raw API transcript ID/order closure differs")
    receipts: dict[str, tuple[dict[str, Any], bytes]] = {}
    request_ids: set[tuple[str, str]] = set(); all_times: list[datetime] = []
    for row in transcript:
        request_body, response_body, request_headers, response_headers, observed_at = decode_exchange(row)
        content_type = response_headers.get("content-type", "")
        if row["request"]["provider"] == "GITHUB" and content_type != "application/json; charset=utf-8":
            raise BootstrapAcceptanceError("GitHub raw response content type differs")
        if row["request"]["provider"] == "AWS" and content_type != "text/xml":
            raise BootstrapAcceptanceError("AWS raw response content type differs")
        request_id_header = "x-github-request-id" if row["request"]["provider"] == "GITHUB" else "x-amzn-requestid"
        request_identity = (row["request"]["provider"], response_headers[request_id_header])
        if request_identity in request_ids: raise BootstrapAcceptanceError("server request ID reused across raw responses")
        request_ids.add(request_identity); all_times.append(observed_at)
        shadow = copy.deepcopy(row); shadow["_request_body"] = request_body; shadow["_date"] = observed_at
        shadow["_request_headers"] = request_headers; shadow["_response_headers"] = response_headers
        shadow["_request_id"] = response_headers[request_id_header]
        receipts[row["id"]] = (shadow, response_body)
    if (max(all_times) - min(all_times)).total_seconds() > 300: raise BootstrapAcceptanceError("raw GitHub/AWS server observation window exceeds 300 seconds")
    values, github_times = parse_github(receipts, contract)
    aws_times, policy_digests, thumbprints_sha256, candidate_commit = parse_aws(receipts, contract, values, store_template)
    if set(github_times + aws_times) != set(all_times): raise BootstrapAcceptanceError("server observation accounting differs")
    keys = authority_keys(keys_file, p0a); verify_signatures(value, p0a, keys, max(all_times))
    return {
        "schema": "c5k4-method-v1.5-aws-github-bootstrap-acceptance-verification-2.0",
        "status": "AUTHENTICATED_LIVE_BOOTSTRAP_PREREQUISITE_SATISFIED",
        "acceptance_payload_sha256": value["authentication"]["payload_sha256"],
        "a0_commit": identity["commit"], "raw_exchange_count": len(transcript),
        "first_server_observation_utc": min(all_times).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_server_observation_utc": max(all_times).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "computed_policy_sha256": policy_digests,
        "bootstrap_candidate_commit": candidate_commit,
        "oidc_provider_thumbprint_list_sha256": thumbprints_sha256,
        "bootstrap_prerequisite_satisfied": True,
        "ami_acceptance_separate_and_required": True,
        "controlled_host_apply_permitted": False,
        "external_mutations": 0,
    }


def publication_fetch(bundle: dict[str, Any]):
    rows = bundle["raw_api_responses"]
    responses: dict[str, bytes] = {}
    for row in rows:
        if row["url"] in responses:
            raise BootstrapAcceptanceError("duplicate P0 publication replay URL")
        responses[row["url"]] = decode_b64(row["body_base64"], "P0 publication replay body")
    used: set[str] = set()
    def fetch(url: str) -> bytes:
        if url not in responses:
            raise BootstrapAcceptanceError("P0 validator requested an uncaptured API URL")
        used.add(url)
        return responses[url]
    return fetch, responses, used


def verify_committed(repo: Path, acceptance_commit: str, keys_file: Path) -> dict[str, Any]:
    parent = topology(repo, acceptance_commit, ACCEPTANCE_PATH)
    acceptance_raw = commit_raw(repo, acceptance_commit, ACCEPTANCE_PATH)
    value = strict_json(acceptance_raw, "committed bootstrap acceptance")
    schema_raw = commit_raw(repo, parent, SCHEMA_REPO_PATH)
    verifier_raw = commit_raw(repo, parent, VERIFIER_REPO_PATH)
    activation_workflow_raw = commit_raw(repo, parent, ACTIVATION_WORKFLOW_PATH)
    if sha256(activation_workflow_raw) != ACTIVATION_WORKFLOW_SHA256:
        raise BootstrapAcceptanceError("A0 parent lacks the exact frozen infrastructure activation workflow")
    if commit_raw(repo, acceptance_commit, SCHEMA_REPO_PATH) != schema_raw or commit_raw(repo, acceptance_commit, VERIFIER_REPO_PATH) != verifier_raw:
        raise BootstrapAcceptanceError("acceptance commit changed schema or verifier")
    if Path(__file__).read_bytes() != verifier_raw: raise BootstrapAcceptanceError("executed verifier differs from exact A0-parent bytes")

    # Resolve the P0A base without importing repository worktree code, then stage
    # the exact A0-parent bytes used for validation into an isolated directory.
    a0 = strict_json(commit_raw(repo, parent, "results/benchmark/v1.5-p0-a0/A0.json"), "A0")
    p0t_commit = a0["p0t"]["commit"]
    p0t = strict_json(commit_raw(repo, p0t_commit, "results/benchmark/v1.5-p0-a0/P0T.json"), "P0T")
    p0a_commit = p0t["p0a"]["commit"]
    p0a_unvalidated = strict_json(commit_raw(repo, p0a_commit, "results/benchmark/v1.5-p0-a0/P0A.json"), "P0A")
    component_bindings = {row["path"]: row for row in p0a_unvalidated["components"]}
    p0_bytes: dict[str, bytes] = {}
    p0_digests: dict[str, str] = {}
    for path in P0_PIN_PATHS:
        raw = commit_raw(repo, parent, path)
        base_raw = commit_raw(repo, p0a_unvalidated["protocol_base_commit"], path)
        binding = component_bindings.get(path)
        if raw != base_raw or not isinstance(binding, dict) or binding.get("sha256") != sha256(raw):
            raise BootstrapAcceptanceError(f"executed P0 dependency differs from P0A/A0-parent bytes: {path}")
        p0_bytes[path] = raw; p0_digests[path] = sha256(raw)

    frozen = value["frozen_bindings"]
    expected = {
        "bootstrap_contract_commit": CONTRACT_COMMIT, "bootstrap_contract_file_sha256": CONTRACT_FILE_SHA256,
        "bootstrap_contract_canonical_sha256": CONTRACT_CANONICAL_SHA256, "controlled_host_preflight_commit": PREFLIGHT_COMMIT,
        "controlled_host_plan_file_sha256": HOST_PLAN_FILE_SHA256, "immutable_store_template_sha256": STORE_TEMPLATE_SHA256,
        "controlled_host_template_sha256": HOST_TEMPLATE_SHA256, "acceptance_schema_sha256": sha256(schema_raw),
        "acceptance_verifier_sha256": sha256(verifier_raw),
        "infrastructure_activation_workflow_sha256": ACTIVATION_WORKFLOW_SHA256,
        "p0_verifier_sha256": p0_digests[P0_VERIFIER_PATH],
        "p0_schema_sha256": {path: p0_digests[path] for path in P0_SCHEMA_PATHS},
    }
    if frozen != expected: raise BootstrapAcceptanceError("acceptance frozen binding closure differs")
    for commit, path, digest in (
        (CONTRACT_COMMIT, CONTRACT_PATH, CONTRACT_FILE_SHA256), (PREFLIGHT_COMMIT, HOST_PLAN_PATH, HOST_PLAN_FILE_SHA256),
        (PREFLIGHT_COMMIT, STORE_TEMPLATE_PATH, STORE_TEMPLATE_SHA256), (PREFLIGHT_COMMIT, HOST_TEMPLATE_PATH, HOST_TEMPLATE_SHA256),
    ):
        if sha256(commit_raw(repo, commit, path)) != digest or sha256(commit_raw(repo, parent, path)) != digest:
            raise BootstrapAcceptanceError(f"frozen/A0-parent bytes differ: {path}")
    contract = strict_json(commit_raw(repo, CONTRACT_COMMIT, CONTRACT_PATH), "bootstrap contract")
    if contract["contract_sha256"] != CONTRACT_CANONICAL_SHA256 or sha256(canonical(without(contract, "contract_sha256"))) != CONTRACT_CANONICAL_SHA256:
        raise BootstrapAcceptanceError("bootstrap contract canonical digest differs")
    store_template = strict_json(commit_raw(repo, PREFLIGHT_COMMIT, STORE_TEMPLATE_PATH), "immutable-store template")
    fetch, replay_responses, replay_used = publication_fetch(value["p0_publication_replay"])
    with tempfile.TemporaryDirectory(prefix="c5k4-p0-pin-") as directory:
        staged = Path(directory)
        for path, raw in p0_bytes.items():
            destination = staged / path; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(raw)
        p0 = _module("method_v15_p0_a0_publication_pinned", staged / P0_VERIFIER_PATH)
        identity = p0.validated_a0_identity(
            repo, parent, require_authoritative=True, authority_keys=keys_file,
            publication_receipt=value["p0_publication_replay"]["a0_publication_receipt"], fetch=fetch,
        )
        p0a = p0.validate_p0a(repo, p0a_commit)
    if replay_used != set(replay_responses) or len(replay_responses) != 7:
        raise BootstrapAcceptanceError("P0 publication replay input closure differs")
    result = verify_payload(value, strict_json(schema_raw, "acceptance schema"), contract, store_template, identity, p0a, keys_file)
    candidate_commit = result["bootstrap_candidate_commit"]
    if sha256(commit_raw(repo, candidate_commit, STORE_TEMPLATE_PATH)) != STORE_TEMPLATE_SHA256:
        raise BootstrapAcceptanceError("authenticated bootstrap candidate lacks the exact immutable-store template")
    if commit_raw(repo, candidate_commit, ACTIVATION_WORKFLOW_PATH) != activation_workflow_raw:
        raise BootstrapAcceptanceError("authenticated bootstrap candidate differs from the exact frozen activation workflow")
    try: git(repo, "merge-base", "--is-ancestor", candidate_commit, parent)
    except BootstrapAcceptanceError as exc: raise BootstrapAcceptanceError("authenticated bootstrap candidate is not in the A0 history") from exc
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--acceptance-commit", required=True)
    parser.add_argument("--authority-keys", type=Path, required=True)
    args = parser.parse_args(argv)
    try: result = verify_committed(args.repo, args.acceptance_commit, args.authority_keys)
    except Exception as exc:
        print(f"bootstrap acceptance verification failed: {exc}", file=sys.stderr); return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":"))); return 0


if __name__ == "__main__": raise SystemExit(main())
