#!/usr/bin/env python3
"""Structural contract for the target-blind offline infrastructure workflow."""

from __future__ import annotations

import copy
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "method-v15-infrastructure-validation.yml"
ACTION_PINS = {
    "actions/checkout": "d23441a48e516b6c34aea4fa41551a30e30af803",
    "actions/setup-python": "ece7cb06caefa5fff74198d8649806c4678c61a1",
}
REQUIRED_PATHS = {
    ".github/workflows/method-v15-infrastructure-validation.yml",
    "infra/benchmark-v1.5/immutable-store/**",
    "infra/benchmark-v1.5/controlled-host/**",
    ".github/workflows/method-v15-controlled-host-activation.yml",
    "results/benchmark/v1.5-protocol/aws-github-bootstrap-contract.json",
    "results/benchmark/v1.5-protocol/controlled-host-provisioning-plan.json",
    "schemas/benchmark-aws-github-bootstrap-contract-v1.5.schema.json",
    "schemas/benchmark-controlled-host-provisioning-plan-v1.5.schema.json",
    "scripts/verify_benchmark_v15_aws_github_bootstrap_contract.py",
    "scripts/test_verify_benchmark_v15_aws_github_bootstrap_contract.py",
    "scripts/verify_benchmark_v15_controlled_host_infrastructure.py",
    "scripts/test_verify_benchmark_v15_controlled_host_infrastructure.py",
    "scripts/test_benchmark_v15_controlled_host_activation_workflow.py",
    "scripts/*benchmark_v15_immutable*.py",
    "scripts/method_v15_s3_object_lock_store.py",
    "scripts/test_method_v15_s3_object_lock_store.py",
    "scripts/test_benchmark_v15_infrastructure_validation_workflow.py",
    "schemas/benchmark-s3-object-lock-store-*.schema.json",
    "schemas/benchmark-operational-controlled-harness-activation-v1.5.schema.json",
    "schemas/benchmark-runner-private-input-assembly-v1.5.schema.json",
}
REQUIRED_COMMANDS = {
    "cryptography==44.0.1",
    "jsonschema==3.2.0",
    "PyYAML==6.0.2",
    "python scripts/test_benchmark_v15_infrastructure_validation_workflow.py",
    "python scripts/verify_benchmark_v15_immutable_infrastructure.py",
    "python scripts/test_verify_benchmark_v15_immutable_infrastructure.py",
    "python scripts/test_verify_benchmark_v15_immutable_live_acceptance.py",
    "python scripts/test_method_v15_s3_object_lock_store.py",
    "python scripts/verify_benchmark_v15_aws_github_bootstrap_contract.py",
    "python scripts/test_verify_benchmark_v15_aws_github_bootstrap_contract.py",
    "python scripts/verify_benchmark_v15_controlled_host_infrastructure.py",
    "python scripts/test_verify_benchmark_v15_controlled_host_infrastructure.py",
    "python scripts/test_benchmark_v15_controlled_host_activation_workflow.py",
    "bootstrap/controlled-host JSON closure is incomplete",
    "Draft7Validator.check_schema",
    "target-bearing field in",
    "CloudFormation template digest mismatch",
    "immutable policy commitment mismatch",
    "git status --porcelain=v1 --untracked-files=all",
}


class WorkflowContractError(ValueError):
    pass


def load_workflow(path: Path = WORKFLOW) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise WorkflowContractError("workflow is not one YAML object")
    # YAML 1.1 treats unquoted `on` as boolean true.
    if "on" not in value and True in value:
        value["on"] = value.pop(True)
    return value, raw


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def validate_workflow(value: dict, raw: str) -> None:
    if value.get("permissions") != {"contents": "read"}:
        raise WorkflowContractError("permissions must be exactly contents:read")
    forbidden_keys = {"env", "environment", "secrets"}
    keys = {key.casefold() for key in walk_keys(value)}
    if forbidden_keys & keys or "id-token" in keys:
        raise WorkflowContractError("workflow requests an environment, secret, or OIDC permission")
    if re.search(r"\$\{\{\s*secrets\.", raw, re.I) or "ACTIONS_ID_TOKEN" in raw:
        raise WorkflowContractError("workflow consumes a secret or OIDC token")

    triggers = value.get("on")
    if not isinstance(triggers, dict) or set(triggers) != {"push", "pull_request"}:
        raise WorkflowContractError("offline workflow triggers are not exact")
    for event in ("push", "pull_request"):
        config = triggers[event]
        if not isinstance(config, dict) or set(config.get("paths", [])) != REQUIRED_PATHS:
            raise WorkflowContractError(f"{event} path trigger closure differs")
    if triggers["push"].get("branches") != ["main"]:
        raise WorkflowContractError("push trigger is not confined to main")

    jobs = value.get("jobs")
    if not isinstance(jobs, dict) or set(jobs) != {"offline-validation"}:
        raise WorkflowContractError("workflow job closure differs")
    job = jobs["offline-validation"]
    if "env" in job or "permissions" in job or job.get("runs-on") != "ubuntu-24.04":
        raise WorkflowContractError("job adds authority/environment or changes runner")
    steps = job.get("steps")
    if not isinstance(steps, list) or not steps:
        raise WorkflowContractError("workflow has no validation steps")
    observed_actions: list[tuple[str, str]] = []
    commands: list[str] = []
    for step in steps:
        if not isinstance(step, dict) or "env" in step:
            raise WorkflowContractError("step is malformed or declares an environment")
        if "uses" in step:
            match = re.fullmatch(r"([^@]+)@([0-9a-f]{40})", str(step["uses"]))
            if match is None:
                raise WorkflowContractError("action is not pinned to a 40-hex commit")
            observed_actions.append((match.group(1), match.group(2)))
        if "run" in step:
            commands.append(str(step["run"]))
    if observed_actions != list(ACTION_PINS.items()):
        raise WorkflowContractError("action set or commit pin differs")
    checkout = steps[0]
    if checkout.get("uses") != f"actions/checkout@{ACTION_PINS['actions/checkout']}" or checkout.get("with", {}).get("persist-credentials") is not False:
        raise WorkflowContractError("checkout retains credentials or differs")
    joined = "\n".join(commands)
    for required in REQUIRED_COMMANDS:
        if required not in joined:
            raise WorkflowContractError(f"required offline check missing: {required}")
    forbidden_commands = (
        "aws ", "aws-cli", "configure-aws-credentials", "cloudformation deploy",
        "cloudformation create", "curl ", "wget ", "--emit-acceptance-bundle",
    )
    lowered = joined.casefold()
    if any(command in lowered for command in forbidden_commands):
        raise WorkflowContractError("workflow contains a network, AWS, provisioning, or operational-emit command")


class InfrastructureValidationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value, cls.raw = load_workflow()

    def test_committed_workflow_is_exactly_offline_and_read_only(self) -> None:
        validate_workflow(copy.deepcopy(self.value), self.raw)

    def test_permission_escalation_or_environment_fails(self) -> None:
        for mutation in ("contents-write", "id-token", "environment", "secret"):
            value = copy.deepcopy(self.value)
            raw = self.raw
            if mutation == "contents-write": value["permissions"]["contents"] = "write"
            elif mutation == "id-token": value["permissions"]["id-token"] = "write"
            elif mutation == "environment": value["jobs"]["offline-validation"]["environment"] = "production"
            else: raw += "\n# ${{ secrets.AWS_ACCESS_KEY_ID }}\n"
            with self.subTest(mutation=mutation), self.assertRaises(WorkflowContractError):
                validate_workflow(value, raw)

    def test_trigger_omission_or_expansion_fails(self) -> None:
        value = copy.deepcopy(self.value); value["on"].pop("pull_request")
        with self.assertRaises(WorkflowContractError): validate_workflow(value, self.raw)
        value = copy.deepcopy(self.value); value["on"]["push"]["paths"].pop()
        with self.assertRaises(WorkflowContractError): validate_workflow(value, self.raw)
        value = copy.deepcopy(self.value); value["on"]["workflow_dispatch"] = {}
        with self.assertRaises(WorkflowContractError): validate_workflow(value, self.raw)

    def test_unpinned_substituted_or_extra_action_fails(self) -> None:
        for use in ("actions/checkout@v6", "actions/checkout@" + "0" * 40, "evil/action@" + "1" * 40):
            value = copy.deepcopy(self.value)
            value["jobs"]["offline-validation"]["steps"][0]["uses"] = use
            with self.subTest(use=use), self.assertRaises(WorkflowContractError):
                validate_workflow(value, self.raw)
        value = copy.deepcopy(self.value)
        value["jobs"]["offline-validation"]["steps"].append({"uses": "actions/setup-python@" + ACTION_PINS["actions/setup-python"]})
        with self.assertRaises(WorkflowContractError):
            validate_workflow(value, self.raw)

    def test_every_required_command_is_independently_mandatory(self) -> None:
        for required in REQUIRED_COMMANDS:
            value = copy.deepcopy(self.value)
            for step in value["jobs"]["offline-validation"]["steps"]:
                if required in str(step.get("run", "")):
                    step["run"] = str(step["run"]).replace(required, "REMOVED_REQUIRED_CHECK")
                    break
            with self.subTest(required=required), self.assertRaisesRegex(WorkflowContractError, "required offline check missing"):
                validate_workflow(value, self.raw)

    def test_aws_network_provisioning_or_operational_emit_command_fails(self) -> None:
        for command in ("aws s3 ls", "curl https://example.org", "cloudformation deploy", "--emit-acceptance-bundle"):
            value = copy.deepcopy(self.value)
            value["jobs"]["offline-validation"]["steps"][-1]["run"] += "\n" + command
            with self.subTest(command=command), self.assertRaises(WorkflowContractError):
                validate_workflow(value, self.raw)


if __name__ == "__main__":
    unittest.main()
