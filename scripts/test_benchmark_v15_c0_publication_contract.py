#!/usr/bin/env python3
"""Fail-closed tests for the pre-activation Method v1.5 C0 contract."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "results/benchmark/v1.5-protocol/c0-publication-contract.json"
SCHEMA_PATH = ROOT / "schemas/benchmark-c0-publication-contract-v1.5.schema.json"


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft7Validator.check_schema(cls.schema)

    def validate(self, value: dict) -> None:
        jsonschema.Draft7Validator(self.schema).validate(value)

    def test_contract_is_closed_and_explicitly_non_authoritative(self) -> None:
        self.validate(self.contract)
        self.assertFalse(self.contract["c0_authority_available"])
        self.assertFalse(self.contract["planned_c0t"]["current_artifact_permitted"])
        self.assertFalse(self.contract["planned_c0a"]["may_claim_frozen"])

    def test_pass_pool_gate_precedes_every_c0_artifact(self) -> None:
        lifecycle = self.contract["required_lifecycle"]
        pool = lifecycle.index("REPLAY_PASS_POOL_SCHEMA_DIGEST_COUNTS_AND_U2_BINDING")
        c0a = lifecycle.index("COMPILE_C0A_WITH_STATUS_AWAITING_C0_PUBLICATION_ATTESTATION")
        self.assertLess(pool, c0a)
        self.assertTrue(self.contract["planned_c0a"]["must_bind_authenticated_pass_pool"])
        self.assertTrue(self.contract["planned_c0a"]["must_bind_authenticated_p1r"])
        self.assertTrue(self.contract["planned_c0t"]["pass_pool_bound_must_be_true"])
        self.assertTrue(self.contract["planned_c0t"]["p1r_bound_must_be_true"])
        self.assertTrue(self.contract["pass_pool_gate"]["canonical_pre_entropy_object_required"])
        self.assertFalse(self.contract["pass_pool_gate"]["standalone_publication_required"])
        self.assertTrue(self.contract["pass_pool_gate"]["exact_embedded_object_sha256_required"])

    def test_u2_triplet_and_first_pass_are_mandatory(self) -> None:
        gate = self.contract["public_checkpoint_gate"]
        self.assertEqual(gate["preterminal_statuses_allowed"], ["QUOTA_FAIL"])
        self.assertEqual(gate["terminal_status_required"], "QUOTA_PASS_U2")
        self.assertTrue(gate["u2_public_triplet_same_commit_required"])
        self.assertFalse(gate["private_replay_attestation_bytes_claimed_public"])

    def test_publication_topology_and_observer_are_not_caller_selected(self) -> None:
        topology = self.contract["publication_topology"]
        self.assertEqual(topology["ref"], "refs/heads/method-v1.5-c0")
        self.assertEqual(topology["c0a_parent"], "TERMINAL_FIRST_PASS_U2_COMMIT")
        self.assertEqual(topology["c0t_parent"], "EXACT_C0A_COMMIT")
        self.assertFalse(topology["merge_commits_permitted"])
        self.assertIn("AUTHENTICATE_PUBLIC_P1R_ACTIVATION_BOUNDARY", self.contract["required_lifecycle"])
        self.assertTrue(self.contract["prohibited"]["bare_p1t_as_activation_authority"])
        observation = self.contract["publication_observation"]
        self.assertEqual(observation["source"], "GITHUB_ACTIONS_PUSH_RUN_OBSERVATION")
        self.assertFalse(observation["caller_supplied_timestamp_is_authority"])
        self.assertTrue(observation["completion_must_precede_drand_close"])

    def test_authority_cannot_be_enabled_by_editing_one_flag(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["c0_authority_available"] = True
        with self.assertRaises(jsonschema.ValidationError):
            self.validate(bad)
        bad = copy.deepcopy(self.contract)
        bad["planned_c0t"]["current_artifact_permitted"] = True
        with self.assertRaises(jsonschema.ValidationError):
            self.validate(bad)

    def test_pass_pool_or_observation_weakening_fails_schema(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["pass_pool_gate"]["candidate_count_must_replay"] = False
        with self.assertRaises(jsonschema.ValidationError):
            self.validate(bad)
        bad = copy.deepcopy(self.contract)
        bad["publication_observation"]["source"] = "CALLER_TIMESTAMP"
        with self.assertRaises(jsonschema.ValidationError):
            self.validate(bad)
        bad = copy.deepcopy(self.contract)
        bad["publication_topology"]["merge_commits_permitted"] = True
        with self.assertRaises(jsonschema.ValidationError):
            self.validate(bad)


if __name__ == "__main__":
    unittest.main()
