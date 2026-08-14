#!/usr/bin/env python3
"""Positive and adversarial tests for the inert v1.5 bootstrap contract."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/verify_benchmark_v15_aws_github_bootstrap_contract.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_contract", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class BootstrapContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = module.load_json(module.CONTRACT_PATH)
        cls.schema = module.load_json(module.SCHEMA_PATH)
        cls.workflow = module.ACTIVATION_WORKFLOW.read_text(encoding="utf-8")
        cls.template = module.load_json(module.STORE_TEMPLATE)

    def verify(self, contract=None, workflow=None, template=None):
        return module.verify(
            copy.deepcopy(self.contract if contract is None else contract),
            copy.deepcopy(self.schema),
            activation_workflow_raw=self.workflow if workflow is None else workflow,
            store_template=copy.deepcopy(self.template if template is None else template),
        )

    def test_committed_contract_is_inert_target_blind_and_verifies(self) -> None:
        result = self.verify()
        self.assertEqual(result["status"], "VALID_TARGET_BLIND_NORMATIVE_CONTRACT_NO_AUTHORITY_CLAIMED")
        self.assertEqual(result["external_mutations"], 0)
        self.assertFalse(result["live_authority_accepted"])
        self.assertTrue(result["immutable_store_alignment_verified"])

    def test_schema_is_strict_and_self_digest_is_exact(self) -> None:
        Draft7Validator.check_schema(self.schema)
        self.assertEqual(self.contract["contract_sha256"], module.canonical_digest(self.contract))
        value = copy.deepcopy(self.contract)
        value["unexpected"] = "authority"
        value["contract_sha256"] = module.canonical_digest(value)
        with self.assertRaises(module.BootstrapContractError):
            self.verify(value)

    def test_immutable_subject_audience_and_opt_in_cannot_drift(self) -> None:
        mutations = (
            lambda value: value["repository_identity"].__setitem__("immutable_oidc_subject", "repo:Kuberwastaken/c5-k4:environment:benchmark-v15-production"),
            lambda value: value["repository_identity"].__setitem__("oidc_audience", "https://github.com/Kuberwastaken"),
            lambda value: value["immutable_subject_prerequisite"].__setitem__("required_before_role_creation", False),
            lambda value: value["immutable_subject_prerequisite"].__setitem__("operator_assertion_is_evidence", True),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.contract); mutate(value); value["contract_sha256"] = module.canonical_digest(value)
            with self.subTest(mutate=mutate), self.assertRaises(module.BootstrapContractError):
                self.verify(value)

    def test_shared_principal_general_chaining_or_long_lived_key_fails(self) -> None:
        mutations = (
            lambda value: value["principals"]["controlled_host_deployer"].__setitem__("role_name", value["principals"]["immutable_store_deployer"]["role_name"]),
            lambda value: value["principal_separation"].__setitem__("shared_principal_permitted", True),
            lambda value: value["principal_separation"].__setitem__("unscoped_role_chaining_permitted", True),
            lambda value: value["principal_separation"].__setitem__("long_lived_aws_access_keys_permitted", True),
            lambda value: value["principals"]["controlled_harness_instance"].__setitem__("human_or_github_assumption_permitted", True),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.contract); mutate(value); value["contract_sha256"] = module.canonical_digest(value)
            with self.subTest(mutate=mutate), self.assertRaises(module.BootstrapContractError):
                self.verify(value)

    def test_every_allowed_action_set_is_disjoint_from_forbidden_actions(self) -> None:
        for label in ("immutable_store_deployer", "controlled_host_deployer"):
            privilege = copy.deepcopy(self.contract["principals"][label]["least_privilege"])
            module._assert_allowed_forbidden_disjoint(privilege, label)
            allowed = sorted(module._all_policy_actions(privilege))
            self.assertTrue(allowed)
            privilege["explicitly_forbidden_actions"].append(allowed[0])
            with self.subTest(label=label), self.assertRaises(module.BootstrapContractError):
                module._assert_allowed_forbidden_disjoint(privilege, label)

    def test_modify_instance_attribute_remains_forbidden_not_allowed(self) -> None:
        privilege = self.contract["principals"]["controlled_host_deployer"]["least_privilege"]
        self.assertNotIn("ec2:ModifyInstanceAttribute", module._all_policy_actions(privilege))
        self.assertIn("ec2:ModifyInstanceAttribute", privilege["explicitly_forbidden_actions"])

    def test_only_exact_external_id_bound_custody_hop_is_permitted(self) -> None:
        mutations = (
            lambda value: value["principals"]["immutable_store_deployer"]["custody_writer_creation"].__setitem__("external_id_policy", "NONE"),
            lambda value: value["principals"]["immutable_store_deployer"]["custody_writer_creation"].__setitem__("only_permitted_assume_role_hop", False),
            lambda value: value["principals"]["controlled_harness_instance"].__setitem__("inline_sts_assume_role_policy", "ANY_ROLE"),
            lambda value: value["principal_separation"].__setitem__("only_permitted_assume_role_edge", "ANY"),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.contract); mutate(value); value["contract_sha256"] = module.canonical_digest(value)
            with self.subTest(mutate=mutate), self.assertRaises(module.BootstrapContractError):
                self.verify(value)

        template = copy.deepcopy(self.template)
        statement = template["Resources"]["CustodyWriterRole"]["Properties"]["AssumeRolePolicyDocument"]["Statement"][0]
        statement.pop("Condition")
        with self.assertRaises(module.BootstrapContractError):
            self.verify(template=template)

    def test_boundary_must_preexist_and_match_committed_template(self) -> None:
        value = copy.deepcopy(self.contract)
        boundary = value["principals"]["immutable_store_deployer"]["custody_writer_creation"]["permissions_boundary"]
        boundary["bootstrap_may_create_or_modify"] = True
        value["contract_sha256"] = module.canonical_digest(value)
        with self.assertRaises(module.BootstrapContractError):
            self.verify(value)
        template = copy.deepcopy(self.template)
        template["Resources"]["CustodyWriterRole"]["Properties"].pop("PermissionsBoundary")
        with self.assertRaises(module.BootstrapContractError):
            self.verify(template=template)

    def test_environment_must_be_main_only_reviewed_and_secret_free(self) -> None:
        mutations = (
            lambda value: value["github_environment"].__setitem__("allowed_branch", "*"),
            lambda value: value["github_environment"].__setitem__("required_reviewer_count_minimum", 0),
            lambda value: value["github_environment"]["environment_secrets"].append("AWS_ACCESS_KEY_ID"),
            lambda value: value["github_environment"].__setitem__("prevent_self_review", False),
        )
        for mutate in mutations:
            value = copy.deepcopy(self.contract); mutate(value); value["contract_sha256"] = module.canonical_digest(value)
            with self.subTest(mutate=mutate), self.assertRaises(module.BootstrapContractError):
                self.verify(value)
        with self.assertRaises(module.BootstrapContractError):
            self.verify(workflow=self.workflow + "\n# ${{ secrets.AWS_ACCESS_KEY_ID }}\n")

    def test_variable_closure_is_existing_five_plus_proposed_host_five(self) -> None:
        self.assertEqual(self.contract["github_variables"]["existing_activation_variables"], module.EXISTING_VARIABLES)
        self.assertEqual(self.contract["github_variables"]["proposed_host_bootstrap_variables"], module.HOST_VARIABLES)
        with self.assertRaises(module.BootstrapContractError):
            self.verify(workflow=self.workflow + "\n# ${{ vars.BENCHMARK_V15_UNDECLARED }}\n")
        value = copy.deepcopy(self.contract)
        value["github_variables"]["proposed_host_bootstrap_variables"].append("BENCHMARK_V15_HARNESS_INSTANCE_ID")
        value["contract_sha256"] = module.canonical_digest(value)
        with self.assertRaises(module.BootstrapContractError):
            self.verify(value)

    def test_zero_current_authority_cannot_be_upgraded_by_static_document(self) -> None:
        for field in (
            "aws_credentials_available_to_session", "aws_oidc_provider_verified",
            "immutable_subject_opt_in_verified", "deployer_roles_verified",
            "harness_role_and_profile_verified", "custody_boundary_verified",
            "authority_accepted", "activation_permitted",
        ):
            value = copy.deepcopy(self.contract)
            value["current_external_state"][field] = True
            value["contract_sha256"] = module.canonical_digest(value)
            with self.subTest(field=field), self.assertRaises(module.BootstrapContractError):
                self.verify(value)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"schema":"one","schema":"two"}\n', encoding="utf-8")
            with self.assertRaises(module.BootstrapContractError):
                module.load_json(path)

    def test_cli_is_read_only_and_emits_no_authority_claim(self) -> None:
        result = subprocess.run([sys.executable, str(MODULE_PATH)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["external_mutations"], 0)
        self.assertFalse(output["live_authority_accepted"])


if __name__ == "__main__":
    unittest.main()
