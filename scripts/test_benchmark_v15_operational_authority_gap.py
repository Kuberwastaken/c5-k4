#!/usr/bin/env python3
"""Structural and adversarial tests for the v1.5 authority-gap contract."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "results/benchmark/v1.5-protocol/operational-authority-gap.json"
SCHEMA_PATH = ROOT / "schemas/benchmark-operational-authority-gap-v1.5.schema.json"


def canonical_digest(value: dict) -> str:
    payload = copy.deepcopy(value)
    payload.pop("gap_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


class OperationalAuthorityGapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(cls.schema)
        cls.validator = Draft7Validator(cls.schema)

    def assert_contract(self, value: dict) -> None:
        self.validator.validate(value)
        self.assertEqual(value["gap_sha256"], canonical_digest(value))

    def test_contract_is_target_blind_normative_gap_not_live_acceptance(self) -> None:
        self.assert_contract(self.contract)
        self.assertEqual(
            self.contract["status"],
            "PRE_P1_EXTERNAL_OPERATIONAL_AUTHORITY_REQUIRED",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["normative_only"])
        self.assertFalse(scope["live_acceptance"])
        self.assertFalse(scope["continuing_host_state_claimed"])
        self.assertFalse(scope["credential_possession_claimed"])
        self.assertFalse(scope["provisioning_performed"])
        self.assertFalse(scope["target_data_consumed"])
        self.assertFalse(scope["target_data_present"])

    def test_current_gaps_are_negative_acceptance_facts_without_secrets(self) -> None:
        accepted = self.contract["accepted_current_authority"]
        self.assertTrue(accepted)
        self.assertTrue(all(value is False for value in accepted.values()))
        facts = self.contract["pre_p1_gap_facts"]
        self.assertEqual(
            facts["fact_class"],
            "FROZEN_PRE_P1_DISCLOSED_GAP_LABELS_NOT_CONTINUOUS_TELEMETRY",
        )
        self.assertFalse(facts["live_state_authority"])
        self.assertFalse(facts["secret_values_recorded"])
        self.assertFalse(facts["host_identifiers_recorded"])
        self.assertFalse(facts["container_identifiers_recorded"])
        self.assertEqual(
            facts["conditions"],
            [
                "NO_AWS_CREDENTIAL_OR_PROVISIONING_AUTHORITY_ACCEPTED",
                "GITHUB_IMMUTABLE_RELEASES_DISABLED_AT_PRE_P1_ASSESSMENT",
                "GITHUB_RELEASE_DELETION_AND_ATTESTATION_DELETION_REMAIN_AUTHORIZED_TO_WRITE_PRINCIPALS",
                "SAME_HOST_MANDATORY_ACCESS_CONTROL_NOT_ACCEPTED_AS_ENFORCING",
                "SAME_HOST_INTERACTIVE_ROOT_EQUIVALENCE_NOT_EXCLUDED",
                "SAME_HOST_MARKETING_WORKLOAD_NONINTERFERENCE_NOT_PROVED",
            ],
        )

    def test_github_is_only_a_secondary_encrypted_transparency_witness(self) -> None:
        github = self.contract["github_origin_assessment"]
        self.assertEqual(github["permitted_role"], "SECONDARY_PUBLIC_TRANSPARENCY_WITNESS_ONLY")
        self.assertFalse(github["authoritative_private_worm_store"])
        self.assertFalse(github["fixed_horizon_retention_proved"])
        self.assertFalse(github["destructive_operation_denial_proved"])
        self.assertFalse(github["least_privilege_create_without_delete_proved"])
        self.assertFalse(github["release_attestation_is_retention_authority"])
        witness = github["future_witness_requirements"]
        self.assertTrue(witness["fixed_asset_count_and_fixed_padded_sizes"])
        self.assertTrue(witness["authenticated_encryption_before_upload"])
        self.assertFalse(witness["plaintext_or_decryption_key_in_git_actions"])
        self.assertFalse(witness["draft_release_is_custody_acceptance"])
        self.assertFalse(witness["witness_can_replace_external_retention_authority"])

        pack = self.contract["encrypted_pack_boundary"]
        self.assertEqual(pack["public_payload_class"], "FIXED_SHAPE_AUTHENTICATED_CIPHERTEXT_ONLY")
        self.assertFalse(pack["ciphertext_publication_is_plaintext_custody"])
        self.assertFalse(pack["encryption_alone_proves_retention"])
        self.assertFalse(pack["encryption_alone_proves_noninterference"])
        self.assertIn("DECRYPTION_KEYS", pack["public_metadata_must_not_contain"])

    def test_minimum_external_authority_is_exact_and_independent(self) -> None:
        rows = self.contract["minimum_external_authority"]
        self.assertEqual(
            [row["authority_class"] for row in rows],
            [
                "INDEPENDENT_FIXED_HORIZON_RETENTION_AUTHORITY",
                "DEDICATED_ISOLATION_AUTHORITY",
                "PROTECTED_CUSTODY_KEY_AUTHORITY",
                "APPEND_ONLY_PUBLICATION_AUTHORITY",
            ],
        )
        retention, isolation, keys, publication = rows
        self.assertFalse(retention["may_be_same_principal_as_experimenter"])
        self.assertFalse(retention["may_be_github_release_immutability_alone"])
        self.assertFalse(isolation["may_be_current_general_ai_session_host"])
        self.assertFalse(isolation["coexistence_without_proved_zero_ingress"])
        self.assertFalse(keys["raw_private_key_repository_role"])
        self.assertFalse(keys["operator_disclosure_is_key_acceptance"])
        self.assertFalse(publication["general_repository_admin_token_accepted"])
        self.assertFalse(publication["manual_publication_override"])

    def test_only_separate_dual_signed_exact_base_acceptance_can_supersede(self) -> None:
        supersession = self.contract["supersession"]
        self.assertFalse(supersession["gap_artifact_is_mutated_into_acceptance"])
        self.assertTrue(supersession["separate_live_acceptance_required"])
        self.assertIsNone(supersession["current_acceptance_path"])
        self.assertIsNone(supersession["current_acceptance_sha256"])
        self.assertIsNone(supersession["current_signature"])
        self.assertEqual(
            supersession["required_signer_classes"],
            [
                "INDEPENDENT_FIXED_HORIZON_RETENTION_AUTHORITY",
                "CONTROLLED_HARNESS_READINESS_KEY",
            ],
        )
        self.assertIn("EXACT_CANDIDATE_BASE_COMMIT_AND_ROOT_TREE", supersession["acceptance_must_bind"])
        self.assertIn("ZERO_TARGET_DATA_STRUCTURAL_AUDIT", supersession["acceptance_must_bind"])
        self.assertFalse(supersession["fixture_is_acceptance"])
        self.assertFalse(supersession["unsigned_document_is_acceptance"])
        self.assertFalse(supersession["operator_statement_is_acceptance"])
        self.assertFalse(supersession["github_setting_receipt_alone_is_acceptance"])
        self.assertTrue(supersession["independent_verification_required"])

    def test_every_pre_p1_publication_and_scientific_transition_is_closed(self) -> None:
        gate = self.contract["publication_gate"]
        false_fields = [key for key in gate if key.endswith("_permitted")]
        self.assertEqual(
            false_fields,
            [
                "p1a_publication_permitted",
                "p1t_publication_permitted",
                "u1_capture_permitted",
                "checkpoint_capture_permitted",
                "entropy_permitted",
                "selection_permitted",
                "target_semantic_inspection_permitted",
            ],
        )
        self.assertTrue(all(gate[key] is False for key in false_fields))

    def test_schema_and_digest_reject_authority_upgrades_and_target_injection(self) -> None:
        mutations = (
            lambda value: value["accepted_current_authority"].__setitem__("aws_operational_authority", True),
            lambda value: value["github_origin_assessment"].__setitem__("authoritative_private_worm_store", True),
            lambda value: value["github_origin_assessment"]["future_witness_requirements"].__setitem__("witness_can_replace_external_retention_authority", True),
            lambda value: value["minimum_external_authority"].pop(0),
            lambda value: value["minimum_external_authority"][1].__setitem__("may_be_current_general_ai_session_host", True),
            lambda value: value["supersession"].__setitem__("required_signer_classes", ["CONTROLLED_HARNESS_READINESS_KEY"]),
            lambda value: value["supersession"].__setitem__("fixture_is_acceptance", True),
            lambda value: value["publication_gate"].__setitem__("p1a_publication_permitted", True),
            lambda value: value["encrypted_pack_boundary"]["public_metadata_may_contain"].append("CANDIDATE_IDENTITIES"),
            lambda value: value.__setitem__("candidate_identities", ["future-cluster-1"]),
            lambda value: value.__setitem__("gap_sha256", "0" * 64),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                value = copy.deepcopy(self.contract)
                mutate(value)
                with self.assertRaises((ValidationError, AssertionError)):
                    self.assert_contract(value)


if __name__ == "__main__":
    unittest.main()
