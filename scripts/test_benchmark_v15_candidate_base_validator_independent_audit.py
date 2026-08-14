#!/usr/bin/env python3
"""Contract and adversarial tests for the independent candidate-validator audit."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "results/benchmark/v1.5-protocol/candidate-base-validator-independent-audit.json"
SCHEMA_PATH = ROOT / "schemas/benchmark-candidate-base-validator-independent-audit-v1.5.schema.json"

EXPECTED_FINDINGS = [
    "MISSING_TWO_INDEPENDENT_RECOMPILES",
    "OPERATIONAL_EVIDENCE_HASHES_NOT_VALIDATED",
    "CANDIDATE_SELECTED_UNANCHORED_OVERLAPPING_KEYS",
    "P1A_P1T_LACK_REPLAYABLE_SIGNED_AUTHORITY",
    "LOCAL_O_EXCL_NOT_PUBLIC_APPEND_ONLY",
    "UNANCHORED_LOCAL_P0_CHAIN",
    "RUNNING_VALIDATOR_DRIFT",
    "FRESHNESS_GAP",
    "OVERSTRONG_TARGET_AUDIT",
    "CANDIDATE_CONTROLLED_BOOTSTRAP",
]


def canonical_digest(value: dict) -> str:
    payload = copy.deepcopy(value)
    payload.pop("audit_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


class CandidateValidatorIndependentAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(cls.schema)
        cls.validator = Draft7Validator(cls.schema)

    def assert_artifact(self, value: dict) -> None:
        self.validator.validate(value)
        self.assertEqual(value["audit_sha256"], canonical_digest(value))

    def test_artifact_is_target_blind_blocking_and_non_authoritative(self) -> None:
        self.assert_artifact(self.artifact)
        self.assertEqual(self.artifact["status"], "BLOCKED_REDESIGN_REQUIRED")
        self.assertEqual(
            self.artifact["artifact_class"],
            "TARGET_BLIND_NON_AUTHORITATIVE_INDEPENDENT_DESIGN_AUDIT",
        )
        scope = self.artifact["scope"]
        self.assertTrue(scope["target_blind"])
        self.assertFalse(scope["target_data_consumed"])
        self.assertFalse(scope["target_data_present"])
        self.assertFalse(scope["live_readiness_claimed"])
        self.assertFalse(scope["operational_authority_claimed"])
        self.assertFalse(scope["implementation_acceptance_claimed"])
        self.assertFalse(scope["audit_subject_is_frozen_revision"])

    def test_all_ten_blocking_findings_are_present_once_in_required_order(self) -> None:
        findings = self.artifact["findings"]
        self.assertEqual([row["id"] for row in findings], EXPECTED_FINDINGS)
        self.assertEqual(len({row["id"] for row in findings}), 10)
        self.assertTrue(all(row["severity"] == "BLOCKING" for row in findings))
        conclusion = self.artifact["audit_conclusion"]
        self.assertEqual(conclusion["finding_count"], len(findings))
        self.assertEqual(conclusion["blocking_finding_count"], len(findings))
        self.assertFalse(conclusion["candidate_base_readiness_accepted"])
        self.assertFalse(conclusion["p1_publication_readiness_accepted"])
        self.assertFalse(conclusion["scientific_activation_permitted"])

    def test_remediation_topology_is_exact_and_only_p1r_activates(self) -> None:
        topology = self.artifact["required_remediation_topology"]
        sequence = ["P0A", "P0T", "A0", "C", "P1A", "P1T", "P1R"]
        self.assertEqual(topology["exact_sequence"], sequence)
        self.assertEqual([row["stage"] for row in topology["stages"]], sequence)
        self.assertEqual(
            [row["scientific_activation_boundary"] for row in topology["stages"]],
            [False, False, False, False, False, False, True],
        )
        self.assertEqual(self.artifact["activation_gate"]["activation_boundary"], "P1R")
        self.assertTrue(
            all(
                value is False
                for value in self.artifact["activation_gate"]["before_valid_p1r"].values()
            )
        )

    def test_audit_cannot_be_reinterpreted_as_readiness_or_acceptance(self) -> None:
        non_authority = self.artifact["non_authority"]
        negative_claims = [key for key in non_authority if key.startswith("this_audit_")]
        self.assertTrue(negative_claims)
        self.assertTrue(all(non_authority[key] is False for key in negative_claims))
        self.assertTrue(non_authority["supersession_requires_new_implementation_and_separate_signed_public_receipts"])
        gate = self.artifact["activation_gate"]
        self.assertFalse(gate["p1a_is_activation"])
        self.assertFalse(gate["p1t_is_activation"])
        self.assertFalse(gate["local_receipt_is_activation"])
        self.assertFalse(gate["schema_conformance_is_activation"])
        self.assertFalse(gate["operator_override_permitted"])

    def test_schema_and_digest_reject_public_accidents(self) -> None:
        mutations = (
            lambda value: value.__setitem__("status", "READY"),
            lambda value: value["scope"].__setitem__("live_readiness_claimed", True),
            lambda value: value["scope"].__setitem__("target_data_present", True),
            lambda value: value["audit_conclusion"].__setitem__("scientific_activation_permitted", True),
            lambda value: value["findings"].pop(),
            lambda value: value["findings"][0].__setitem__("severity", "ADVISORY"),
            lambda value: value["required_remediation_topology"].__setitem__("exact_sequence", ["C", "P1A", "P1T"]),
            lambda value: value["required_remediation_topology"]["stages"][5].__setitem__("scientific_activation_boundary", True),
            lambda value: value["activation_gate"].__setitem__("activation_boundary", "P1T"),
            lambda value: value["activation_gate"]["before_valid_p1r"].__setitem__("u1_capture_permitted", True),
            lambda value: value["non_authority"].__setitem__("this_audit_is_live_readiness", True),
            lambda value: value.__setitem__("candidate_identities", ["forbidden-target"]),
            lambda value: value.__setitem__("audit_sha256", "0" * 64),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                value = copy.deepcopy(self.artifact)
                mutate(value)
                if value["audit_sha256"] != "0" * 64:
                    value["audit_sha256"] = canonical_digest(value)
                with self.assertRaises((ValidationError, AssertionError)):
                    self.assert_artifact(value)


if __name__ == "__main__":
    unittest.main()
