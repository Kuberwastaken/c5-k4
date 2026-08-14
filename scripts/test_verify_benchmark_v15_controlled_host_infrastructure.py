#!/usr/bin/env python3
"""Adversarial tests for the Method v1.5 controlled-host scaffold."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "controlled_host", HERE / "verify_benchmark_v15_controlled_host_infrastructure.py"
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class ControlledHostInfrastructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(V.PLAN_PATH.read_text())
        cls.schema = json.loads(V.SCHEMA_PATH.read_text())
        cls.template = json.loads(V.TEMPLATE_PATH.read_text())

    def validate_mutation(self, template: dict, plan: dict | None = None) -> None:
        raw = V.canonical(template)
        changed_plan = copy.deepcopy(self.plan if plan is None else plan)
        changed_plan["deployment"]["template_sha256"] = V.sha256(raw)
        without = dict(changed_plan); without.pop("plan_sha256")
        changed_plan["plan_sha256"] = V.sha256(V.PLAN_DOMAIN.encode() + b"\0" + V.canonical(without))
        schema = copy.deepcopy(self.schema)
        schema["properties"]["deployment"]["const"]["template_sha256"] = V.sha256(raw)
        V.validate(changed_plan, schema, template, raw)

    def test_committed_scaffold_is_valid_and_nonauthoritative(self) -> None:
        V.validate(self.plan, self.schema, self.template, V.TEMPLATE_PATH.read_bytes())
        self.assertFalse(self.plan["deployment"]["executed"])
        self.assertFalse(self.plan["deployment"]["activation_permitted"])
        self.assertTrue(self.plan["deployment"]["plan_metadata_only"])
        self.assertFalse(self.plan["deployment"]["role_assumption_is_authority_acceptance"])
        self.assertFalse(self.plan["deployment"]["ami_metadata_is_measurement_acceptance"])
        self.assertIn("LIVE_NITROTPM_AND_DAEMON_ATTESTATION_NOT_YET_CAPTURED", self.plan["external_prerequisites"])

    def test_digest_or_operational_claim_drift_fails(self) -> None:
        for mutation in ("digest", "executed", "activation", "role_acceptance", "ami_acceptance", "apply_gate"):
            plan = copy.deepcopy(self.plan)
            if mutation == "digest": plan["plan_sha256"] = "0" * 64
            if mutation == "executed": plan["deployment"]["executed"] = True
            if mutation == "activation": plan["deployment"]["activation_permitted"] = True
            if mutation == "role_acceptance": plan["deployment"]["role_assumption_is_authority_acceptance"] = True
            if mutation == "ami_acceptance": plan["deployment"]["ami_metadata_is_measurement_acceptance"] = True
            if mutation == "apply_gate": plan["deployment"]["apply_repository_gate"] = "OPEN"
            with self.subTest(mutation=mutation), self.assertRaises(V.ControlledHostPlanError):
                V.validate(plan, self.schema, self.template, V.TEMPLATE_PATH.read_bytes())

    def test_network_access_and_management_channels_fail(self) -> None:
        mutations = {
            "ingress": lambda t: t["Resources"]["ControlledSecurityGroup"]["Properties"].update(SecurityGroupIngress=[{"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "CidrIp": "10.0.0.0/8"}]),
            "egress": lambda t: t["Resources"]["ControlledSecurityGroup"]["Properties"].update(SecurityGroupEgress=[]),
            "public_ip": lambda t: t["Resources"]["ControlledHost"]["Properties"]["NetworkInterfaces"][0].update(AssociatePublicIpAddress=True),
            "ssh_key": lambda t: t["Resources"]["ControlledHost"]["Properties"].update(KeyName="forbidden"),
            "internet_gateway": lambda t: t["Resources"].update(Escape={"Type": "AWS::EC2::InternetGateway", "DeletionPolicy": "Retain", "UpdateReplacePolicy": "Retain"}),
        }
        for name, mutate in mutations.items():
            template = copy.deepcopy(self.template); mutate(template)
            with self.subTest(name=name), self.assertRaises(V.ControlledHostPlanError):
                self.validate_mutation(template)

    def test_tpm_host_persistence_and_isolation_drift_fail(self) -> None:
        mutations = {
            "imds_v1": lambda t: t["Resources"]["ControlledHost"]["Properties"]["MetadataOptions"].update(HttpTokens="optional"),
            "shared_tenancy": lambda t: t["Resources"]["ControlledHost"]["Properties"].update(Tenancy="default"),
            "deleting_ebs": lambda t: t["Resources"]["ControlledHost"]["Properties"]["BlockDeviceMappings"][0]["Ebs"].update(DeleteOnTermination=True),
            "plain_ebs": lambda t: t["Resources"]["ControlledHost"]["Properties"]["BlockDeviceMappings"][0]["Ebs"].update(Encrypted=False),
            "az_mismatch": lambda t: t["Resources"]["ControlledSubnet"]["Properties"].update(AvailabilityZone={"Fn::Select": [1, {"Fn::GetAZs": ""}]}),
            "mutable_image": lambda t: t["Resources"]["ControlledHost"]["Properties"]["UserData"]["Fn::Base64"]["Fn::Join"][1].append("docker pull python:latest\n"),
        }
        for name, mutate in mutations.items():
            template = copy.deepcopy(self.template); mutate(template)
            with self.subTest(name=name), self.assertRaises(V.ControlledHostPlanError):
                self.validate_mutation(template)

    def test_pre_a0_scaffold_cannot_claim_future_candidate_c(self) -> None:
        template = copy.deepcopy(self.template)
        parameters = template["Parameters"]
        parameters["CandidateCommit"] = parameters.pop("ProtocolScaffoldCommit")
        parts = template["Resources"]["ControlledHost"]["Properties"]["UserData"]["Fn::Base64"]["Fn::Join"][1]
        for index, part in enumerate(parts):
            if part == {"Ref": "ProtocolScaffoldCommit"}: parts[index] = {"Ref": "CandidateCommit"}
            if isinstance(part, str): parts[index] = part.replace("--protocol-scaffold-commit", "--candidate-commit")
        with self.assertRaises(V.ControlledHostPlanError):
            self.validate_mutation(template)


if __name__ == "__main__":
    unittest.main()
