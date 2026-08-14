#!/usr/bin/env python3
"""Structural tests for the target-blind candidate-base readiness specification."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "results/benchmark/v1.5-protocol/candidate-base-commit-readiness-spec.json"
SCHEMA_PATH = ROOT / "schemas/benchmark-candidate-base-commit-readiness-spec-v1.5.schema.json"


class CandidateBaseCommitReadinessSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(cls.schema)

    def validate(self, value: dict) -> None:
        Draft7Validator(self.schema).validate(value)

    def test_normative_spec_validates_without_claiming_readiness(self) -> None:
        self.validate(self.spec)
        self.assertEqual(self.spec["status"], "PRE_P1_NORMATIVE_SPEC_NOT_READINESS_EVIDENCE")
        self.assertTrue(all(value is False for value in self.spec["current_state"].values()))
        self.assertEqual(self.spec["target_blindness"]["current_candidate_identities"], [])
        self.assertEqual(self.spec["target_blindness"]["current_statement_text"], [])

    def test_exact_c_closures_and_non_circular_transition_are_frozen(self) -> None:
        self.assertEqual(self.spec["candidate_base_commit"]["symbol"], "C")
        self.assertEqual(self.spec["closure"]["native_v1_5"]["commit"], "EXACT_C")
        self.assertEqual(
            self.spec["closure"]["source_v1_4"]["scope"],
            "FULL_P0A_REFERENCED_SOURCE_CLOSURE_NOT_ONLY_SELECTED_ROLES",
        )
        p1a = self.spec["p1_transition"]["p1a"]
        self.assertEqual((p1a["parent_count"], p1a["sole_parent"]), (1, "EXACT_C"))
        self.assertEqual(p1a["changed_path_count"], 1)
        self.assertTrue(p1a["parent_tree_recompile_required"])

    def test_pre_and_post_p1_boundary_is_public_p1t_not_p1a_creation(self) -> None:
        machine = self.spec["phase_machine"]
        self.assertEqual(machine["p1_boundary"], "PUBLIC_AUTHENTICATED_P1T_RECEIPT_NOT_P1A_FILE_CREATION")
        self.assertTrue(all(not row["execution_permitted"] for row in machine["pre_p1"]))
        self.assertFalse(machine["post_p1"][0]["target_semantics_permitted"])
        self.assertTrue(machine["post_p1"][1]["target_semantics_permitted"])

    def test_composite_signatures_recompile_and_abstention_are_mandatory(self) -> None:
        compilation = self.spec["readiness_compilation"]
        self.assertEqual(compilation["independent_recompile"]["minimum_independent_recompiles"], 2)
        self.assertTrue(compilation["independent_recompile"]["all_component_signatures_reverified"])
        self.assertEqual(
            compilation["composite_signature"]["required_signer_classes"],
            ["CONTROLLED_HARNESS_READINESS_KEY", "EVERY_FROZEN_EXPERIMENTER_IDENTITY"],
        )
        abstention = self.spec["experimenter_nonintervention"]
        self.assertEqual(abstention["machine_detectable_contact"], "EXCLUDE_CONFLICTED_CLUSTER_BEFORE_QUOTA_AND_SELECTION")
        self.assertEqual(abstention["unreported_or_unattributable_contact"], "FAIL_CLOSED_PROTOCOL_INVALID")

    def test_schema_rejects_readiness_upgrade_and_transition_weakening(self) -> None:
        for mutation in (
            lambda x: x["current_state"].__setitem__("operational", True),
            lambda x: x["p1_transition"]["p1a"].__setitem__("parent_count", 2),
            lambda x: x["readiness_compilation"]["independent_recompile"].__setitem__("minimum_independent_recompiles", 1),
            lambda x: x["experimenter_nonintervention"].__setitem__("target_identity_exception", "ALLOWED"),
            lambda x: x["target_blindness"]["current_candidate_identities"].append("future:cluster"),
        ):
            value = copy.deepcopy(self.spec)
            mutation(value)
            with self.assertRaises(Exception):
                self.validate(value)


if __name__ == "__main__":
    unittest.main()
