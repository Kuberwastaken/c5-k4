#!/usr/bin/env python3
"""Static safety contract for controlled-host PLAN/APPLY automation."""

from __future__ import annotations

import copy
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/method-v15-controlled-host-activation.yml"
PINS = [
    ("actions/checkout", "d23441a48e516b6c34aea4fa41551a30e30af803"),
    ("aws-actions/configure-aws-credentials", "61815dcd50bd041e203e49132bacad1fd04d2708"),
]
VARS = {
    "BENCHMARK_V15_HOST_STACK_NAME", "BENCHMARK_V15_HOST_TEMPLATE_SHA256",
    "BENCHMARK_V15_HOST_AMI_ID", "BENCHMARK_V15_HOST_AMI_MEASUREMENTS_SHA256",
    "BENCHMARK_V15_HOST_AWS_ROLE_ARN",
    "BENCHMARK_V15_AWS_REGION", "BENCHMARK_V15_HARNESS_PRINCIPAL_ARN",
}
REQUIRED = {
    "python3 scripts/verify_benchmark_v15_controlled_host_infrastructure.py",
    '[[ "$GITHUB_REF" == refs/heads/main ]]',
    'test "$HARNESS_PRINCIPAL_ARN" != "$ROLE_ARN"',
    "aws ec2 describe-images",
    "'OwnerId': sys.argv[3]",
    "'BootMode': 'uefi'",
    "'TpmSupport': 'v2.0'",
    "image.get('DeprecationTime') not in (None, '')",
    "aws iam get-role",
    "aws iam get-instance-profile",
    "aws cloudformation validate-template",
    "aws cloudformation describe-stacks",
    "APPLY is blocked: no committed verifier-authenticated immutable-OIDC/deployer bootstrap acceptance exists.",
    "without making an authority or measurement-acceptance claim",
    "without accepting its trust policy",
}


class WorkflowError(ValueError):
    pass


def load() -> tuple[dict, str]:
    raw = WORKFLOW.read_text()
    value = yaml.safe_load(raw)
    if "on" not in value and True in value: value["on"] = value.pop(True)
    return value, raw


def keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key); yield from keys(child)
    elif isinstance(value, list):
        for child in value: yield from keys(child)


def validate(value: dict, raw: str) -> None:
    on = value.get("on")
    if not isinstance(on, dict) or set(on) != {"workflow_dispatch"}:
        raise WorkflowError("workflow is not manual only")
    inputs = on["workflow_dispatch"].get("inputs", {})
    if inputs.get("operation", {}).get("options") != ["PLAN", "APPLY"] or inputs.get("operation", {}).get("default") != "PLAN":
        raise WorkflowError("operation is not default-read-only PLAN")
    if inputs.get("confirmation", {}).get("default") != "" or inputs.get("confirmation", {}).get("required") is not False:
        raise WorkflowError("typed confirmation differs")
    if value.get("permissions") != {"contents": "read", "id-token": "write"}:
        raise WorkflowError("OIDC/content permissions differ")
    if set(keys(value)) & {"push", "schedule", "pull_request", "secrets"} or re.search(r"\$\{\{\s*secrets\.", raw):
        raise WorkflowError("automatic trigger or long-lived secret found")
    job = value.get("jobs", {}).get("plan-only")
    if set(value.get("jobs", {})) != {"plan-only"} or job.get("environment") != {"name": "benchmark-v15-production"}:
        raise WorkflowError("protected environment/job closure differs")
    if set(re.findall(r"vars\.([A-Z0-9_]+)", raw)) != VARS:
        raise WorkflowError("GitHub variable closure differs")
    actions = []
    for step in job.get("steps", []):
        if "uses" in step:
            match = re.fullmatch(r"([^@]+)@([0-9a-f]{40})", str(step["uses"]))
            if match is None: raise WorkflowError("action is not commit pinned")
            actions.append(match.groups())
    if actions != PINS or job["steps"][0].get("with", {}).get("persist-credentials") is not False:
        raise WorkflowError("action set or credential persistence differs")
    for token in REQUIRED:
        if token not in raw: raise WorkflowError(f"required safety check missing: {token}")
    aws_calls = {(m.group(1), m.group(2)) for m in re.finditer(r"\baws\s+([a-z0-9-]+)\s+([a-z0-9-]+)", raw)}
    allowed = {
        ("ec2", "describe-images"), ("iam", "get-role"), ("iam", "get-instance-profile"),
        ("cloudformation", "validate-template"), ("cloudformation", "describe-stacks"),
    }
    if not aws_calls <= allowed:
        raise WorkflowError("workflow contains an unapproved AWS API operation")
    forbidden = (
        "delete-stack", "update-stack", "create-change-set", "execute-change-set", "change-set-type", "create-role", "put-role-policy",
        "create-instance-profile", "add-role-to-instance-profile", "authorize-security-group-ingress",
        "aws ssm", "send-command", "ec2-instance-connect", "self-hosted", "docker pull",
        "candidatecommit", "parameterkey=candidatecommit", "capability_named_iam", "set -x",
    )
    if any(token in raw.casefold() for token in forbidden):
        raise WorkflowError("workflow grants mutation, access, mutable image, IAM creation, or future-C authority")


class ControlledHostWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value, cls.raw = load()

    def test_committed_workflow_is_manual_oidc_plan_only(self) -> None:
        validate(copy.deepcopy(self.value), self.raw)

    def test_automatic_trigger_secret_or_unpinned_action_fails(self) -> None:
        value = copy.deepcopy(self.value); value["on"]["push"] = {}
        with self.assertRaises(WorkflowError): validate(value, self.raw)
        with self.assertRaises(WorkflowError): validate(copy.deepcopy(self.value), self.raw + "\n# ${{ secrets.AWS_KEY }}")
        value = copy.deepcopy(self.value); value["jobs"]["plan-only"]["steps"][0]["uses"] = "actions/checkout@v6"
        with self.assertRaises(WorkflowError): validate(value, self.raw)

    def test_missing_ami_owner_tpm_deprecation_or_profile_check_fails(self) -> None:
        for token in ("'OwnerId': sys.argv[3]", "'TpmSupport': 'v2.0'", "image.get('DeprecationTime') not in (None, '')", "aws iam get-instance-profile"):
            with self.subTest(token=token), self.assertRaises(WorkflowError):
                validate(copy.deepcopy(self.value), self.raw.replace(token, "REMOVED_REQUIRED_GATE"))

    def test_apply_write_iam_creation_management_or_future_c_binding_fails(self) -> None:
        for command in ("aws cloudformation create-change-set", "aws cloudformation update-stack", "aws iam create-role", "aws ssm send-command", "CandidateCommit", "--capabilities CAPABILITY_NAMED_IAM"):
            with self.subTest(command=command), self.assertRaises(WorkflowError):
                validate(copy.deepcopy(self.value), self.raw + "\n# " + command)

    def test_apply_gate_and_host_role_are_independently_mandatory(self) -> None:
        gate = "APPLY is blocked: no committed verifier-authenticated immutable-OIDC/deployer bootstrap acceptance exists."
        with self.assertRaises(WorkflowError):
            validate(copy.deepcopy(self.value), self.raw.replace(gate, "REMOVED_APPLY_GATE"))
        with self.assertRaises(WorkflowError):
            validate(copy.deepcopy(self.value), self.raw.replace("vars.BENCHMARK_V15_HOST_AWS_ROLE_ARN", "vars.BENCHMARK_V15_AWS_ROLE_ARN"))


if __name__ == "__main__":
    unittest.main()
