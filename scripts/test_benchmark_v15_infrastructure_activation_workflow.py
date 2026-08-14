#!/usr/bin/env python3
"""Structural safety contract for the manual v1.5 infrastructure workflow."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/method-v15-infrastructure-activation.yml"
WORKFLOW_SHA256 = "b0f1656e6f2dbcb3884f0000cce171bc77afd775df531128b157a3f42cff4ea1"
PINS = [
    ("actions/checkout", "d23441a48e516b6c34aea4fa41551a30e30af803"),
    ("aws-actions/configure-aws-credentials", "61815dcd50bd041e203e49132bacad1fd04d2708"),
]
VARS = {
    "BENCHMARK_V15_AWS_ROLE_ARN", "BENCHMARK_V15_AWS_REGION",
    "BENCHMARK_V15_STACK_NAME", "BENCHMARK_V15_TEMPLATE_SHA256",
    "BENCHMARK_V15_HARNESS_PRINCIPAL_ARN",
}
ALLOWED_AWS = {
    "validate-template", "get-template-summary", "describe-stacks",
    "create-change-set", "wait", "describe-change-set", "execute-change-set",
}
REQUIRED = {
    "python3 scripts/verify_benchmark_v15_immutable_infrastructure.py",
    'test "$HARNESS_PRINCIPAL_ARN" != "$ROLE_ARN"',
    "'harness_external_id_policy': policy",
    "'parameters_sha256': sys.argv[4]",
    'expected="APPLY:${GITHUB_SHA}:${TEMPLATE_DIGEST}:${PARAMETERS_SHA256}"',
    'PLAN) test -z "$CONFIRMATION"',
    'APPLY) test "$CONFIRMATION" = "$expected"',
    "aws cloudformation validate-template",
    "aws cloudformation get-template-summary",
    "aws cloudformation describe-stacks",
    "aws cloudformation create-change-set",
    "aws cloudformation describe-change-set",
    'python3 - "$RUNNER_TEMP/change-set.json" <<\'PY\'',
    "aws cloudformation execute-change-set",
    "steps.plan.outputs.create_permitted == 'true'",
    "--change-set-type CREATE --client-token",
    'ParameterKey=HarnessPrincipalArn,ParameterValue=$HARNESS_PRINCIPAL_ARN',
    "'ParameterKey=PrivatePrefix,ParameterValue=private/c5k4/v1.5'",
    "'ParameterKey=RetentionYears,ParameterValue=3'",
    "resources != expected_resources",
    "set(value.get('Capabilities', [])) != {'CAPABILITY_IAM'}",
    "change.get('Action') != 'Add'",
    "change.get('Replacement') is not None",
}


class ActivationWorkflowError(ValueError):
    pass


def load_workflow() -> tuple[dict, str]:
    raw = WORKFLOW.read_text(encoding="utf-8")
    value = yaml.safe_load(raw)
    if "on" not in value and True in value:
        value["on"] = value.pop(True)
    return value, raw


def keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from keys(child)


def validate(value: dict, raw: str) -> None:
    triggers = value.get("on")
    if not isinstance(triggers, dict) or set(triggers) != {"workflow_dispatch"}:
        raise ActivationWorkflowError("activation workflow is not manual-only")
    inputs = triggers["workflow_dispatch"].get("inputs", {})
    operation = inputs.get("operation", {})
    confirmation = inputs.get("confirmation", {})
    if operation.get("type") != "choice" or operation.get("default") != "PLAN" or operation.get("options") != ["PLAN", "APPLY"] or operation.get("required") is not True:
        raise ActivationWorkflowError("operation input is not default/read-only PLAN")
    if confirmation.get("type") != "string" or confirmation.get("default") != "" or confirmation.get("required") is not False:
        raise ActivationWorkflowError("typed confirmation input differs")
    if value.get("permissions") != {"contents": "read", "id-token": "write"}:
        raise ActivationWorkflowError("OIDC permissions are not exact")
    if set(keys(value)) & {"secrets", "schedule", "push", "pull_request"} or re.search(r"\$\{\{\s*secrets\.", raw, re.I):
        raise ActivationWorkflowError("automatic trigger or credentials secret found")
    concurrency = value.get("concurrency", {})
    if concurrency.get("cancel-in-progress") is not False or "BENCHMARK_V15_STACK_NAME" not in str(concurrency.get("group")):
        raise ActivationWorkflowError("stack-scoped concurrency differs")
    jobs = value.get("jobs", {})
    if set(jobs) != {"plan-and-apply"}:
        raise ActivationWorkflowError("job closure differs")
    job = jobs["plan-and-apply"]
    if job.get("environment") != {"name": "benchmark-v15-production"}:
        raise ActivationWorkflowError("protected production environment is absent")
    steps = job.get("steps", [])
    actions = []
    commands = []
    observed_vars = set(re.findall(r"vars\.([A-Z0-9_]+)", raw))
    if observed_vars != VARS:
        raise ActivationWorkflowError("repository variable authority differs")
    for step in steps:
        if "uses" in step:
            match = re.fullmatch(r"([^@]+)@([0-9a-f]{40})", str(step["uses"]))
            if match is None:
                raise ActivationWorkflowError("action is not commit-pinned")
            actions.append(match.groups())
        commands.append(str(step.get("run", "")))
        for env_value in step.get("env", {}).values():
            text = str(env_value)
            if "secrets." in text:
                raise ActivationWorkflowError("step consumes a long-lived secret")
    if actions != PINS:
        raise ActivationWorkflowError("action set or pin differs")
    if steps[0].get("with", {}).get("persist-credentials") is not False:
        raise ActivationWorkflowError("checkout retains credentials")
    joined = "\n".join([*commands, *(str(step.get("if", "")) for step in steps)])
    for required in REQUIRED:
        if required not in joined:
            raise ActivationWorkflowError(f"required authority/plan/apply check missing: {required}")
    plan_index = next(index for index, step in enumerate(steps) if step.get("id") == "plan")
    apply_index = next(index for index, step in enumerate(steps) if "execute one exact change set" in str(step.get("name", "")))
    if plan_index >= apply_index:
        raise ActivationWorkflowError("apply can precede the read-only plan")
    for match in re.finditer(r"\baws\s+([a-z0-9-]+)(?:\s+([a-z0-9-]+))?", joined):
        if match.group(1) != "cloudformation" or match.group(2) not in ALLOWED_AWS:
            raise ActivationWorkflowError("broad or destructive AWS command found")
    forbidden = (
        "delete-stack", "delete-change-set", "cloudformation deploy", "aws s3 ",
        "aws iam ", "aws kms ", "set -x", "::debug", "tojson(", "target_id",
        "cluster_id", "statement_text", "cat $runner_temp", "tee ",
        "change-set-type update", "stack-update-complete",
        "value.get('clienttoken')", 'change-set.json" "$client_token"',
    )
    if any(token in raw.casefold() for token in forbidden):
        raise ActivationWorkflowError("destruction, target fields, or provider logging found")


def change_set_inspection_script(raw: str) -> str:
    match = re.search(r'python3 - "\$RUNNER_TEMP/change-set\.json" <<\'PY\'\n(.*?)\n          PY', raw, re.DOTALL)
    if match is None:
        raise ActivationWorkflowError("change-set inspection script is absent")
    return "\n".join(line.removeprefix("          ") for line in match.group(1).splitlines()) + "\n"


class InfrastructureActivationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value, cls.raw = load_workflow()

    def test_committed_workflow_is_manual_oidc_and_fail_closed(self) -> None:
        validate(copy.deepcopy(self.value), self.raw)
        self.assertEqual(hashlib.sha256(self.raw.encode()).hexdigest(), WORKFLOW_SHA256)

    def test_any_automatic_trigger_or_secret_fails(self) -> None:
        for mutation in ("push", "schedule", "secret"):
            value = copy.deepcopy(self.value); raw = self.raw
            if mutation == "secret": raw += "\n# ${{ secrets.AWS_ACCESS_KEY_ID }}\n"
            else: value["on"][mutation] = {}
            with self.subTest(mutation=mutation), self.assertRaises(ActivationWorkflowError):
                validate(value, raw)

    def test_plan_default_confirmation_or_environment_relaxation_fails(self) -> None:
        mutations = []
        value = copy.deepcopy(self.value); value["on"]["workflow_dispatch"]["inputs"]["operation"]["default"] = "APPLY"; mutations.append(value)
        value = copy.deepcopy(self.value); value["on"]["workflow_dispatch"]["inputs"]["confirmation"]["required"] = True; mutations.append(value)
        value = copy.deepcopy(self.value); value["jobs"]["plan-and-apply"].pop("environment"); mutations.append(value)
        for value in mutations:
            with self.assertRaises(ActivationWorkflowError): validate(value, self.raw)

    def test_missing_oidc_authority_variable_or_confirmation_check_fails(self) -> None:
        value = copy.deepcopy(self.value); value["permissions"].pop("id-token")
        with self.assertRaises(ActivationWorkflowError): validate(value, self.raw)
        for variable in VARS:
            with self.subTest(variable=variable), self.assertRaises(ActivationWorkflowError):
                validate(copy.deepcopy(self.value), self.raw.replace(f"vars.{variable}", "vars.REMOVED_AUTHORITY"))
        for required in ('expected="APPLY:${GITHUB_SHA}:${TEMPLATE_DIGEST}:${PARAMETERS_SHA256}"', 'APPLY) test "$CONFIRMATION" = "$expected"'):
            value = copy.deepcopy(self.value)
            for step in value["jobs"]["plan-and-apply"]["steps"]:
                if required in str(step.get("run", "")):
                    step["run"] = str(step["run"]).replace(required, "REMOVED_CONFIRMATION_GATE")
                    break
            with self.subTest(required=required), self.assertRaises(ActivationWorkflowError):
                validate(value, self.raw)

    def test_deployer_harness_alias_or_unbound_parameter_drift_fails(self) -> None:
        for required in (
            'test "$HARNESS_PRINCIPAL_ARN" != "$ROLE_ARN"',
            'ParameterKey=HarnessPrincipalArn,ParameterValue=$HARNESS_PRINCIPAL_ARN',
            "'ParameterKey=PrivatePrefix,ParameterValue=private/c5k4/v1.5'",
            "'ParameterKey=RetentionYears,ParameterValue=3'",
            "'harness_external_id_policy': policy",
            "'parameters_sha256': sys.argv[4]",
        ):
            value = copy.deepcopy(self.value)
            for step in value["jobs"]["plan-and-apply"]["steps"]:
                if required in str(step.get("run", "")):
                    step["run"] = str(step["run"]).replace(required, "REMOVED_PARAMETER_BINDING")
                    break
            with self.subTest(required=required), self.assertRaises(ActivationWorkflowError):
                validate(value, self.raw)
        self.assertNotIn("ParameterValue=$ROLE_ARN", self.raw)

    def test_unpinned_or_extra_action_fails(self) -> None:
        value = copy.deepcopy(self.value); value["jobs"]["plan-and-apply"]["steps"][0]["uses"] = "actions/checkout@v6"
        with self.assertRaises(ActivationWorkflowError): validate(value, self.raw)
        value = copy.deepcopy(self.value); value["jobs"]["plan-and-apply"]["steps"].append({"uses": "evil/action@" + "0" * 40})
        with self.assertRaises(ActivationWorkflowError): validate(value, self.raw)

    def test_plan_before_apply_and_every_required_command_are_mandatory(self) -> None:
        for required in REQUIRED:
            value = copy.deepcopy(self.value)
            for step in value["jobs"]["plan-and-apply"]["steps"]:
                if required in str(step.get("run", "")) or required in str(step.get("if", "")):
                    if required in str(step.get("run", "")):
                        step["run"] = str(step["run"]).replace(required, "REMOVED_REQUIRED_GATE")
                    else:
                        step["if"] = str(step["if"]).replace(required, "false")
                    break
            with self.subTest(required=required), self.assertRaises(ActivationWorkflowError):
                validate(value, self.raw)

    def test_documented_describe_change_set_shape_never_uses_synthetic_client_token(self) -> None:
        script = change_set_inspection_script(self.raw)
        self.assertNotIn("ClientToken", script)
        changes = [{"Type": "Resource", "ResourceChange": {"Action": "Add", "LogicalResourceId": logical}} for logical in (
            "CustodyBucket", "CustodyBucketPolicy", "CustodyKey", "CustodyWriterPolicy", "CustodyWriterRole",
        )]
        documented = {"Status": "CREATE_COMPLETE", "ExecutionStatus": "AVAILABLE", "ChangeSetType": "CREATE", "Capabilities": ["CAPABILITY_IAM"], "Changes": changes}
        for payload in (documented, {**documented, "ClientToken": "synthetic-untrusted-echo"}):
            with self.subTest(synthetic_echo="ClientToken" in payload), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "describe-change-set.json"; path.write_text(json.dumps(payload))
                result = subprocess.run([sys.executable, "-", str(path)], input=script, text=True, capture_output=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_delete_broad_aws_target_or_logging_command_fails(self) -> None:
        for command in ("aws cloudformation delete-stack", "aws s3 ls", "aws ec2 describe-instances", "set -x", "echo target_id", "cat $RUNNER_TEMP/change-set.json"):
            value = copy.deepcopy(self.value)
            value["jobs"]["plan-and-apply"]["steps"][-1]["run"] += "\n" + command
            with self.subTest(command=command), self.assertRaises(ActivationWorkflowError):
                validate(value, self.raw + "\n" + command)


if __name__ == "__main__":
    unittest.main()
