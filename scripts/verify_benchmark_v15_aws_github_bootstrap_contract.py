#!/usr/bin/env python3
"""Statically verify the inert Method v1.5 AWS/GitHub bootstrap contract.

This verifier performs no network call and no mutation.  It proves only that the
repository artifact freezes the intended external bootstrap boundary; it never
turns that boundary into live authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import sys

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "results/benchmark/v1.5-protocol/aws-github-bootstrap-contract.json"
SCHEMA_PATH = ROOT / "schemas/benchmark-aws-github-bootstrap-contract-v1.5.schema.json"
ACTIVATION_WORKFLOW = ROOT / ".github/workflows/method-v15-infrastructure-activation.yml"
STORE_TEMPLATE = ROOT / "infra/benchmark-v1.5/immutable-store/cloudformation.json"

SUBJECT = "repo:Kuberwastaken@97027230/c5-k4@1331829034:environment:benchmark-v15-production"
AUDIENCE = "sts.amazonaws.com"
EXISTING_VARIABLES = [
    "BENCHMARK_V15_AWS_REGION",
    "BENCHMARK_V15_TEMPLATE_SHA256",
    "BENCHMARK_V15_STACK_NAME",
    "BENCHMARK_V15_AWS_ROLE_ARN",
    "BENCHMARK_V15_HARNESS_PRINCIPAL_ARN",
]
HOST_VARIABLES = [
    "BENCHMARK_V15_HOST_STACK_NAME",
    "BENCHMARK_V15_HOST_TEMPLATE_SHA256",
    "BENCHMARK_V15_HOST_AMI_ID",
    "BENCHMARK_V15_HOST_AMI_MEASUREMENTS_SHA256",
    "BENCHMARK_V15_HOST_AWS_ROLE_ARN",
]
FORBIDDEN_SEMANTIC_KEYS = {
    "cluster_id", "candidate_id", "candidate_ids", "statement_text",
    "target_id", "target_ids", "target_ranking", "conjecture_id",
}


class BootstrapContractError(ValueError):
    pass


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise BootstrapContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_pairs)
    if not isinstance(value, dict):
        raise BootstrapContractError(f"JSON root is not an object: {path}")
    return value


def canonical_digest(value: dict) -> str:
    payload = copy.deepcopy(value)
    payload.pop("contract_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def _walk_keys(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _all_policy_actions(privilege: dict) -> set[str]:
    actions: set[str] = set()
    for key, value in privilege.items():
        if key.endswith("_actions") and key != "explicitly_forbidden_actions":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise BootstrapContractError(f"malformed action list: {key}")
            actions.update(value)
    return actions


def _assert_allowed_forbidden_disjoint(privilege: dict, label: str) -> None:
    allowed = _all_policy_actions(privilege)
    forbidden_value = privilege.get("explicitly_forbidden_actions")
    if not isinstance(forbidden_value, list) or not all(isinstance(item, str) for item in forbidden_value):
        raise BootstrapContractError(f"malformed forbidden action list: {label}")
    forbidden = set(forbidden_value)
    overlap = sorted(allowed & forbidden)
    if overlap:
        raise BootstrapContractError(f"allowed/forbidden action overlap for {label}: {overlap}")


def verify(
    contract: dict,
    schema: dict,
    *,
    activation_workflow_raw: str,
    store_template: dict,
) -> dict:
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(contract), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        raise BootstrapContractError(f"schema rejection at {list(first.path)}: {first.message}")
    if contract["contract_sha256"] != canonical_digest(contract):
        raise BootstrapContractError("contract_sha256 is not the canonical self-digest")

    if set(_walk_keys(contract)) & FORBIDDEN_SEMANTIC_KEYS:
        raise BootstrapContractError("target/candidate semantic field present")
    scope = contract["scope"]
    if not scope["normative_only"] or any(
        scope[key]
        for key in (
            "external_mutation_authorized", "provisioning_performed",
            "live_acceptance_claimed", "credential_possession_claimed",
            "target_data_permitted", "target_specific",
        )
    ):
        raise BootstrapContractError("inert target-blind scope was widened")

    identity = contract["repository_identity"]
    prerequisite = contract["immutable_subject_prerequisite"]
    if identity["immutable_oidc_subject"] != SUBJECT or prerequisite["accepted_subject"] != SUBJECT:
        raise BootstrapContractError("immutable OIDC subject differs")
    if identity["oidc_audience"] != AUDIENCE:
        raise BootstrapContractError("OIDC audience differs")
    if prerequisite["status"] != "EXTERNAL_OPT_IN_REQUIRED" or not prerequisite["required_before_role_creation"]:
        raise BootstrapContractError("immutable-subject opt-in is not an external prerequisite")
    if prerequisite["operator_assertion_is_evidence"] or not prerequisite["live_api_receipt_required"]:
        raise BootstrapContractError("subject customization can be accepted without a live receipt")

    principals = contract["principals"]
    deployers = [principals["immutable_store_deployer"], principals["controlled_host_deployer"]]
    role_names = [row["role_name"] for row in deployers] + [principals["controlled_harness_instance"]["role_name"]]
    if len(role_names) != len(set(role_names)):
        raise BootstrapContractError("principal roles are not pairwise distinct")
    for label, deployer in zip(("immutable_store_deployer", "controlled_host_deployer"), deployers):
        trust = deployer["trust"]
        if trust["action"] != "sts:AssumeRoleWithWebIdentity" or trust["role_chaining_permitted"]:
            raise BootstrapContractError("deployer trust permits role chaining")
        if trust["conditions"] != {
            "token.actions.githubusercontent.com:aud": AUDIENCE,
            "token.actions.githubusercontent.com:sub": SUBJECT,
        }:
            raise BootstrapContractError("deployer trust is not exact immutable OIDC")
        privilege = deployer["least_privilege"]
        _assert_allowed_forbidden_disjoint(privilege, label)
        actions = _all_policy_actions(privilege)
        if "sts:AssumeRole" in actions or "*" in actions or any("Administrator" in action for action in actions):
            raise BootstrapContractError("deployer permission allows chaining or broad administration")
        if not privilege["wildcard_administrator_policy_forbidden"]:
            raise BootstrapContractError("wildcard administrator policy is not forbidden")
    store_actions = _all_policy_actions(deployers[0]["least_privilege"])
    if "iam:PassRole" in store_actions:
        raise BootstrapContractError("immutable-store deployer may pass a role")
    host = deployers[1]["least_privilege"]
    if "iam:PassRole" not in _all_policy_actions(host) or host["iam_pass_role_constraint"] != "EXACT_CONTROLLED_HARNESS_INSTANCE_ROLE_TO_EC2_ONLY":
        raise BootstrapContractError("host deployer PassRole is absent or unconstrained")
    if host["iam_pass_role_resource"] != "EXACT_BENCHMARK_V15_HARNESS_PRINCIPAL_ARN" or host["iam_pass_role_condition"] != {"iam:PassedToService": "ec2.amazonaws.com"}:
        raise BootstrapContractError("host deployer PassRole resource/service constraint differs")

    harness = principals["controlled_harness_instance"]
    if harness["trust_principal"] != "ec2.amazonaws.com" or harness["trust_action"] != "sts:AssumeRole":
        raise BootstrapContractError("harness trust is not EC2 instance-profile-only")
    if harness["human_or_github_assumption_permitted"] or harness["unscoped_role_chaining_permitted"]:
        raise BootstrapContractError("harness permits human/GitHub assumption or unscoped role chaining")
    if not harness["role_and_instance_profile_must_preexist"] or not harness["role_and_instance_profile_names_must_match"] or not harness["host_stack_consumes_preexisting_profile_name_only"]:
        raise BootstrapContractError("harness role/profile are not distinct pre-existing matched authorities")
    if harness["inline_sts_assume_role_policy"] != "EXACT_CUSTODY_WRITER_ROLE_WITH_FROZEN_EXTERNAL_ID_ONLY":
        raise BootstrapContractError("harness AssumeRole permission is not the one frozen custody hop")
    custody = deployers[0]["custody_writer_creation"]
    boundary = custody["permissions_boundary"]
    if not boundary["must_preexist"] or boundary["bootstrap_may_create_or_modify"] or not boundary["live_digest_receipt_required"]:
        raise BootstrapContractError("custody-writer boundary is not pre-existing and receipt-bound")
    if harness["custody_access_model"] != "SINGLE_EXTERNAL_ID_BOUND_CUSTODY_WRITER_ASSUME_ROLE_HOP":
        raise BootstrapContractError("harness custody access differs from the one permitted hop")
    if not custody["created_only_by_immutable_store_stack"] or custody["trust_principal"] != "EXACT_CONTROLLED_HARNESS_ROLE_ARN" or custody["trust_action"] != "sts:AssumeRole" or not custody["only_permitted_assume_role_hop"]:
        raise BootstrapContractError("custody-writer creation/trust differs")
    if custody["external_id_policy"] != "SHA256(candidate_commit:template_sha256:stack_name:harness_principal_arn)":
        raise BootstrapContractError("custody-writer external ID policy differs")

    separation = contract["principal_separation"]
    if not separation["all_role_arns_pairwise_distinct"] or separation["shared_principal_permitted"] or separation["unscoped_role_chaining_permitted"] or separation["long_lived_aws_access_keys_permitted"]:
        raise BootstrapContractError("principal separation is weakened")
    if separation["only_permitted_assume_role_edge"] != "CONTROLLED_HARNESS_TO_CUSTODY_WRITER_WITH_EXACT_EXTERNAL_ID":
        raise BootstrapContractError("the one permitted role-assumption edge differs")
    environment = contract["github_environment"]
    if not environment["protected"] or environment["allowed_branch"] != "main" or environment["tags_permitted"]:
        raise BootstrapContractError("GitHub environment is not protected main-only")
    if environment["required_reviewer_count_minimum"] < 1 or not environment["prevent_self_review"]:
        raise BootstrapContractError("GitHub environment lacks an independent review gate")
    if environment["environment_secrets"] or environment["repository_secrets_consumed"] or not environment["oidc_only"]:
        raise BootstrapContractError("GitHub environment permits secrets or non-OIDC credentials")

    variables = contract["github_variables"]
    if variables["existing_activation_variables"] != EXISTING_VARIABLES:
        raise BootstrapContractError("existing activation variable closure differs")
    if variables["proposed_host_bootstrap_variables"] != HOST_VARIABLES:
        raise BootstrapContractError("host bootstrap variable closure differs")
    if variables["values_recorded_in_contract"] or variables["secrets_permitted_as_variables"]:
        raise BootstrapContractError("variable values or secrets entered the normative contract")
    observed_workflow_variables = sorted(set(re.findall(r"vars\.([A-Z0-9_]+)", activation_workflow_raw)))
    if observed_workflow_variables != sorted(EXISTING_VARIABLES):
        raise BootstrapContractError("committed activation workflow no longer consumes exactly the existing five variables")
    if "secrets." in activation_workflow_raw or "environment:\n      name: benchmark-v15-production" not in activation_workflow_raw:
        raise BootstrapContractError("activation workflow bypasses the secret-free protected environment")

    current = contract["current_external_state"]
    if current["github_repository_variable_count"] != 0 or current["github_environment_count"] != 0:
        raise BootstrapContractError("contract improperly claims current GitHub authority")
    boolean_state = [value for key, value in current.items() if key not in {"observation_class", "observed_at_utc", "github_repository_variable_count", "github_environment_count"}]
    if any(boolean_state):
        raise BootstrapContractError("contract improperly claims current external authority")

    # The immutable-store template intentionally contains exactly one
    # HarnessPrincipalArn -> CustodyWriterRole external-ID-bound AssumeRole hop.
    resources = store_template.get("Resources", {})
    custody_role = resources.get("CustodyWriterRole", {})
    statements = custody_role.get("Properties", {}).get("AssumeRolePolicyDocument", {}).get("Statement", [])
    exact_hops = [row for row in statements if (
        row.get("Action") == "sts:AssumeRole"
        and row.get("Principal", {}).get("AWS") == {"Ref": "HarnessPrincipalArn"}
    )]
    if len(exact_hops) != 1 or exact_hops[0].get("Condition") != {"StringEquals": {"sts:ExternalId": {"Ref": "HarnessExternalId"}}}:
        raise BootstrapContractError("immutable-store template lacks the exact one permitted external-ID hop")
    if custody_role.get("Properties", {}).get("PermissionsBoundary") != {"Fn::Sub": "arn:${AWS::Partition}:iam::${AWS::AccountId}:policy/c5k4-v1-5-custody-writer-boundary"}:
        raise BootstrapContractError("immutable-store custody role lacks the frozen pre-existing boundary")
    alignment = contract["immutable_store_alignment"]
    if not alignment["custody_writer_created_by_immutable_store_stack"] or not alignment["preexisting_permissions_boundary_required"] or not alignment["harness_to_custody_writer_external_id_hop_required"]:
        raise BootstrapContractError("immutable-store alignment is incomplete")
    if alignment["any_other_assume_role_hop_permitted"] or alignment["static_contract_is_live_acceptance"] or not alignment["separate_live_acceptance_required"]:
        raise BootstrapContractError("static bootstrap contract overclaims authority")

    return {
        "schema": "c5k4-method-v1.5-aws-github-bootstrap-contract-verification-1.0",
        "status": "VALID_TARGET_BLIND_NORMATIVE_CONTRACT_NO_AUTHORITY_CLAIMED",
        "contract_sha256": contract["contract_sha256"],
        "external_mutations": 0,
        "live_authority_accepted": False,
        "immutable_store_alignment_verified": True,
    }


def main() -> int:
    try:
        result = verify(
            load_json(CONTRACT_PATH),
            load_json(SCHEMA_PATH),
            activation_workflow_raw=ACTIVATION_WORKFLOW.read_text(encoding="utf-8"),
            store_template=load_json(STORE_TEMPLATE),
        )
    except Exception as exc:
        print(f"bootstrap contract verification failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
