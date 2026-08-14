#!/usr/bin/env python3
"""Verify the frozen, target-blind Method v1.5 controlled-host scaffold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "results/benchmark/v1.5-protocol/controlled-host-provisioning-plan.json"
SCHEMA_PATH = ROOT / "schemas/benchmark-controlled-host-provisioning-plan-v1.5.schema.json"
TEMPLATE_PATH = ROOT / "infra/benchmark-v1.5/controlled-host/cloudformation.json"
PLAN_DOMAIN = "c5k4-method-v1.5-controlled-host-provisioning-plan-1.0"

EXPECTED_RESOURCES = {
    "ControlledVpc": "AWS::EC2::VPC",
    "ControlledSubnet": "AWS::EC2::Subnet",
    "ControlledRouteTable": "AWS::EC2::RouteTable",
    "ControlledSubnetRouteTableAssociation": "AWS::EC2::SubnetRouteTableAssociation",
    "ControlledSecurityGroup": "AWS::EC2::SecurityGroup",
    "ControlledHost": "AWS::EC2::Instance",
}
FORBIDDEN_TYPES = {
    "AWS::EC2::InternetGateway", "AWS::EC2::NatGateway", "AWS::EC2::Route",
    "AWS::EC2::VPCEndpoint", "AWS::IAM::Role", "AWS::IAM::Policy",
    "AWS::SSM::Association", "AWS::EC2::KeyPair", "AWS::ElasticLoadBalancingV2::LoadBalancer",
}
REQUIRED_BOOTSTRAP_TOKENS = {
    "/usr/local/sbin/c5k4-v15-controlled-host-bootstrap",
    "--docker-executable /usr/bin/docker",
    "--docker-security-options name=cgroupns,name=seccomp,profile=builtin,name=userns",
    "--docker-cgroup-version 2 --docker-cgroup-driver systemd --docker-runtime runc",
    "docker.io/library/python:3.13.7-slim-bookworm@sha256:781449467ffb6f04218f09b1ecdcdc7d22b289ee5da9ec498b024e24ad7a6db7",
    "sha256:444ec9cb9b03c3be7c8b18d4a5e82e7cc908e2c0032c0a6e759338a48250b4de",
    "--key-policy NITROTPM_PCR_SEALED_ED25519",
    "--projection-policy CANONICAL_TARGET_FREE_SIGNED_LOCAL_ONLY",
    "/var/lib/c5k4-benchmark-v15/bootstrap-projection.json",
}
FORBIDDEN_TEXT = {
    "target_id", "cluster_id", "statement_text", "candidate_identity", "github actions runner",
    "actions.runner", "ssm-agent", "ec2-instance-connect", "authorized_keys", "docker pull",
    "curl ", "wget ", "0.0.0.0/0", "::/0", "AWS::EC2::InternetGateway", "AWS::EC2::NatGateway",
}


class ControlledHostPlanError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()

    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ControlledHostPlanError(f"duplicate JSON key in {path}")
            value[key] = item
        return value

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ControlledHostPlanError(f"invalid strict JSON in {path}") from exc
    if not isinstance(value, dict):
        raise ControlledHostPlanError(f"top level is not an object in {path}")
    return value, raw


def joined_user_data(value: Any) -> str:
    if not isinstance(value, dict) or set(value) != {"Fn::Base64"}:
        raise ControlledHostPlanError("user data is not a single CloudFormation Base64 expression")
    join = value["Fn::Base64"]
    if not isinstance(join, dict) or set(join) != {"Fn::Join"}:
        raise ControlledHostPlanError("user data does not use the frozen Join expression")
    separator, parts = join["Fn::Join"]
    if separator != "" or not isinstance(parts, list):
        raise ControlledHostPlanError("user-data Join grammar differs")
    rendered = ""
    for part in parts:
        if isinstance(part, str):
            rendered += part
        elif part in ({"Ref": "ProtocolScaffoldCommit"}, {"Ref": "AttestableAmiMeasurementsSha256"}):
            rendered += f"<{part['Ref']}>"
        else:
            raise ControlledHostPlanError("user data contains an unapproved dynamic reference")
    return rendered


def validate(plan: dict[str, Any], schema: dict[str, Any], template: dict[str, Any], template_raw: bytes) -> None:
    try:
        jsonschema.Draft7Validator(schema).validate(plan)
    except jsonschema.ValidationError as exc:
        raise ControlledHostPlanError("controlled-host plan does not validate") from exc
    without_digest = dict(plan); recorded = without_digest.pop("plan_sha256")
    expected_plan = sha256(PLAN_DOMAIN.encode() + b"\0" + canonical(without_digest))
    if recorded != expected_plan:
        raise ControlledHostPlanError("controlled-host plan self-digest mismatch")
    if plan["deployment"]["template_sha256"] != sha256(template_raw):
        raise ControlledHostPlanError("controlled-host template digest mismatch")
    deployment = plan["deployment"]
    if (
        deployment.get("activation_permitted") is not False
        or deployment.get("plan_metadata_only") is not True
        or deployment.get("apply_repository_gate") != "BLOCKED_AWAITING_VERIFIER_AUTHENTICATED_BOOTSTRAP_ACCEPTANCE"
        or deployment.get("role_assumption_is_authority_acceptance") is not False
        or deployment.get("ami_metadata_is_measurement_acceptance") is not False
    ):
        raise ControlledHostPlanError("controlled-host plan overstates bootstrap or AMI authority")
    required_missing_authority = {
        "VERIFIER_AUTHENTICATED_IMMUTABLE_OIDC_AND_DEPLOYER_BOOTSTRAP_ACCEPTANCE_NOT_YET_FROZEN",
        "INDEPENDENT_ATTESTABLE_AMI_MEASUREMENT_ACCEPTANCE_NOT_YET_AUTHENTICATED",
    }
    if not required_missing_authority <= set(plan["external_prerequisites"]):
        raise ControlledHostPlanError("controlled-host plan omits unresolved bootstrap authority")

    if set(template) != {"AWSTemplateFormatVersion", "Description", "Parameters", "Resources", "Outputs"}:
        raise ControlledHostPlanError("CloudFormation top-level closure differs")
    parameters = template["Parameters"]
    if set(parameters) != {"AttestableAmiId", "AttestableAmiMeasurementsSha256", "ProtocolScaffoldCommit", "HarnessInstanceProfileName"}:
        raise ControlledHostPlanError("CloudFormation parameter closure differs")
    if parameters["AttestableAmiId"].get("Type") != "AWS::EC2::Image::Id":
        raise ControlledHostPlanError("AMI is not a typed externally supplied image ID")
    if parameters["AttestableAmiMeasurementsSha256"].get("AllowedPattern") != "^[0-9a-f]{64}$":
        raise ControlledHostPlanError("AMI measurement digest grammar differs")

    resources = template["Resources"]
    observed = {name: row.get("Type") for name, row in resources.items()}
    if observed != EXPECTED_RESOURCES or set(observed.values()) & FORBIDDEN_TYPES:
        raise ControlledHostPlanError("controlled-host resource closure differs")
    for name, row in resources.items():
        if row.get("DeletionPolicy") != "Retain" or row.get("UpdateReplacePolicy") != "Retain":
            raise ControlledHostPlanError(f"resource retention policy differs: {name}")

    vpc = resources["ControlledVpc"]["Properties"]
    if vpc.get("InstanceTenancy") != "default" or vpc.get("EnableDnsHostnames") is not False:
        raise ControlledHostPlanError("bootstrap VPC is not the frozen inert network")
    subnet = resources["ControlledSubnet"]["Properties"]
    if subnet.get("MapPublicIpOnLaunch") is not False or subnet.get("AssignIpv6AddressOnCreation") is not False:
        raise ControlledHostPlanError("controlled subnet permits a public address")
    if subnet.get("AvailabilityZone") != {"Fn::Select": [0, {"Fn::GetAZs": ""}]}:
        raise ControlledHostPlanError("controlled subnet is not pinned to the host availability zone")
    security = resources["ControlledSecurityGroup"]["Properties"]
    if security.get("SecurityGroupIngress") != [] or security.get("SecurityGroupEgress") != [{
        "Description": "Explicitly replace AWS default egress with unreachable loopback-only destination",
        "IpProtocol": "-1", "CidrIp": "127.0.0.1/32",
    }]:
        raise ControlledHostPlanError("bootstrap security group is not exact no-ingress/no-general-egress")

    host = resources["ControlledHost"]["Properties"]
    required_host = {
        "DisableApiTermination": True, "EbsOptimized": True, "InstanceInitiatedShutdownBehavior": "stop",
        "InstanceType": "m6i.large", "Monitoring": True, "SourceDestCheck": True, "Tenancy": "dedicated",
    }
    if any(host.get(key) != value for key, value in required_host.items()):
        raise ControlledHostPlanError("controlled-host persistence/dedication properties differ")
    if host.get("ImageId") != {"Ref": "AttestableAmiId"} or host.get("IamInstanceProfile") != {"Ref": "HarnessInstanceProfileName"}:
        raise ControlledHostPlanError("host AMI or authority binding differs")
    if host.get("AvailabilityZone") != subnet.get("AvailabilityZone"):
        raise ControlledHostPlanError("controlled host and subnet availability zones differ")
    metadata = host.get("MetadataOptions")
    if metadata != {"HttpEndpoint": "enabled", "HttpProtocolIpv6": "disabled", "HttpPutResponseHopLimit": 1, "HttpTokens": "required", "InstanceMetadataTags": "disabled"}:
        raise ControlledHostPlanError("IMDSv2 policy differs")
    mappings = host.get("BlockDeviceMappings")
    if not isinstance(mappings, list) or len(mappings) != 1:
        raise ControlledHostPlanError("root-volume closure differs")
    ebs = mappings[0].get("Ebs", {})
    if mappings[0].get("DeviceName") != "/dev/xvda" or ebs.get("Encrypted") is not True or ebs.get("DeleteOnTermination") is not False or ebs.get("VolumeType") != "gp3":
        raise ControlledHostPlanError("persistent encrypted root EBS policy differs")
    interfaces = host.get("NetworkInterfaces")
    if not isinstance(interfaces, list) or len(interfaces) != 1 or interfaces[0].get("AssociatePublicIpAddress") is not False:
        raise ControlledHostPlanError("host network interface is not private and singular")
    if "KeyName" in host:
        raise ControlledHostPlanError("SSH key material is permitted")

    user_data = joined_user_data(host.get("UserData"))
    missing = {token for token in REQUIRED_BOOTSTRAP_TOKENS if token not in user_data}
    if missing:
        raise ControlledHostPlanError(f"frozen bootstrap contract token missing: {sorted(missing)}")
    if "--candidate-commit" in user_data or "CandidateCommit" in json.dumps(template):
        raise ControlledHostPlanError("pre-A0 host scaffold claims a future candidate-C binding")
    if "--protocol-scaffold-commit '<ProtocolScaffoldCommit>'" not in user_data:
        raise ControlledHostPlanError("pre-A0 bootstrap does not bind its non-authoritative scaffold commit")
    full_text = json.dumps(template, sort_keys=True).casefold()
    if any(token.casefold() in full_text for token in FORBIDDEN_TEXT):
        raise ControlledHostPlanError("template contains network, access, target, mutable-image, or runner capability")
    if template.get("Outputs") != {}:
        raise ControlledHostPlanError("bootstrap stack exports an unauthenticated runtime value")


def main() -> int:
    plan, _ = strict_json(PLAN_PATH)
    schema, _ = strict_json(SCHEMA_PATH)
    template, template_raw = strict_json(TEMPLATE_PATH)
    validate(plan, schema, template, template_raw)
    print("controlled-host provisioning scaffold verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
