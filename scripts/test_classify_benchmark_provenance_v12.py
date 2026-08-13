#!/usr/bin/env python3
"""Regression tests for Method v1.2 provenance classification."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

import classify_benchmark_provenance_v12 as provenance


ROOT = Path(__file__).parents[1]
POLICY_PATH = ROOT / "results/benchmark/v1.2-prototype/provenance-policy.json"


class ProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = provenance.load_policy(POLICY_PATH)
        self.unit = {
            "source_id": "frozen-session-snapshot",
            "source_kind": "git_sessions",
            "locator": "session-blob:" + "1" * 40 + ":sessions/run.jsonl:7",
            "role": "custom-tool-output",
            "content_sha256": "2" * 64,
            "content_schema": "c5k4-registry-identity-counts-1.2",
            "mixed": False,
            "malformed": False,
        }
        self.exemption = {
            **{key: self.unit[key] for key in (
                "source_id", "source_kind", "locator", "role",
                "content_sha256", "content_schema"
            )},
            "unit_identity_sha256": provenance.unit_identity_sha256(self.unit),
            "producer_verified": True,
            "invocation_contract_verified": True,
            "output_digest_verified": True,
            "bounded_schema_verified": True,
            "mixed_unit_rejected": True,
        }

    def classified(self, unit=None, exemption=None):
        return provenance.classify_unit(
            self.unit if unit is None else unit,
            self.exemption if exemption is None else exemption,
            self.policy,
        )["provenance_class"]

    def test_paired_bounded_identity_count_output_is_machine_contact(self) -> None:
        self.assertEqual(self.classified(), provenance.MACHINE_REGISTRY_CONTACT)
        decision = provenance.identity_decision(
            provenance.MACHINE_REGISTRY_CONTACT,
            [{"matched": True, "alias_kind": "DECLARATION_ID"}],
            self.policy,
        )
        self.assertTrue(decision["identity_hit"])
        self.assertFalse(decision["excludes_cluster"])

    def test_assistant_or_user_turn_cannot_launder_exempt_bytes(self) -> None:
        for role in ("assistant-turn", "user-turn"):
            unit = {**self.unit, "role": role}
            exemption = {**self.exemption, "role": role}
            exemption["unit_identity_sha256"] = provenance.unit_identity_sha256(unit)
            self.assertEqual(self.classified(unit, exemption), provenance.SEMANTIC_SOURCE)

    def test_same_bytes_at_other_locator_do_not_inherit_exemption(self) -> None:
        copied = {**self.unit, "locator": "session-blob:" + "3" * 40 + ":sessions/run.jsonl:8"}
        self.assertEqual(self.classified(copied, self.exemption), provenance.UNKNOWN)

    def test_mixed_machine_json_and_prose_is_unknown(self) -> None:
        mixed = {**self.unit, "mixed": True}
        self.assertEqual(self.classified(mixed, self.exemption), provenance.UNKNOWN)

    def test_unverified_or_unbounded_tool_output_is_unknown(self) -> None:
        unverified = copy.deepcopy(self.exemption)
        unverified["invocation_contract_verified"] = False
        self.assertEqual(self.classified(exemption=unverified), provenance.UNKNOWN)
        unbounded = {**self.unit, "content_schema": "text/plain"}
        self.assertEqual(self.classified(unbounded, self.exemption), provenance.UNKNOWN)

    def test_machine_role_in_wrong_source_kind_is_unknown(self) -> None:
        wrong_kind = {**self.unit, "source_kind": "tree"}
        exemption = {**self.exemption, "source_kind": "tree"}
        exemption["unit_identity_sha256"] = provenance.unit_identity_sha256(wrong_kind)
        self.assertEqual(self.classified(wrong_kind, exemption), provenance.UNKNOWN)

    def test_repo_scripts_and_prose_are_semantic(self) -> None:
        for role in ("repo-script", "repo-code", "repo-prose", "commit-message"):
            unit = {**self.unit, "role": role, "content_schema": None}
            self.assertEqual(self.classified(unit, None), provenance.SEMANTIC_SOURCE)

    def test_git_metadata_and_path_lists_are_unknown_and_identity_excludes(self) -> None:
        for role in ("git-metadata", "git-path-list"):
            unit = {**self.unit, "role": role, "content_schema": None}
            classified = self.classified(unit, None)
            self.assertEqual(classified, provenance.UNKNOWN)
            decision = provenance.identity_decision(
                classified,
                [{"matched": True, "alias_kind": "FULL_PATH"}],
                self.policy,
            )
            self.assertTrue(decision["excludes_cluster"])

    def test_generic_alias_list_collision_needs_namespace_anchor(self) -> None:
        aliases = [
            {"matched": True, "alias_kind": "GENERIC_ALIAS", "normalized": "conjecture 7"},
            {"matched": True, "alias_kind": "DECLARATION_NAME", "normalized": "graphconjecture7"},
        ]
        decision = provenance.identity_decision(provenance.SEMANTIC_SOURCE, aliases, self.policy)
        self.assertFalse(decision["identity_hit"])
        anchored = {**aliases[1], "namespace_anchor": "google-deepmind/formal-conjectures"}
        decision = provenance.identity_decision(
            provenance.SEMANTIC_SOURCE, [*aliases, anchored], self.policy
        )
        self.assertTrue(decision["identity_hit"])
        self.assertTrue(decision["excludes_cluster"])

    def test_conflicting_exemption_records_fail_closed(self) -> None:
        conflicting = {**self.exemption, "producer_verified": False}
        with self.assertRaisesRegex(ValueError, "conflicting"):
            provenance.exemption_index([self.exemption, conflicting])

    def test_policy_is_machine_readable_and_declares_exactly_three_classes(self) -> None:
        raw = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(raw["unit_classes"]), provenance.CLASSES)
        self.assertTrue(raw["invariants"]["exactly_one_class_per_scan_unit"])


if __name__ == "__main__":
    unittest.main()
