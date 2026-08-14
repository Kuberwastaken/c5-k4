#!/usr/bin/env python3
"""Focused tests for Method v1.5 provenance classification."""

from __future__ import annotations

import copy
from pathlib import Path
import unittest

import classify_benchmark_provenance_v15 as provenance


ROOT = Path(__file__).parents[1]


class ProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.unit = {
            "source_id": "repo:c5-k4", "source_kind": "git",
            "locator": "git-blob:" + "1" * 40 + ":results/open-inventory.json",
            "role": "machine-generated-git-blob", "content_sha256": "2" * 64,
            "content_schema": "c5k4-open-inventory-1.5", "mixed": False, "malformed": False,
        }
        self.proof = {
            **{key: self.unit[key] for key in (
                "source_id", "source_kind", "locator", "role", "content_sha256", "content_schema"
            )},
            "schema_version": "c5k4-generated-identity-verification-1.5",
            "verification_status": "VERIFIED",
            "unit_identity_sha256": provenance.unit_identity_sha256(self.unit),
            "historical_inputs_predate_output": True,
            "bounded_safe_surface_verified": True,
            "deterministic_exact_replay_verified": True,
            "locator_specific_proof": True,
            "global_content_hash_allowlist": False,
            "interactive_delivery": False,
        }

    def classified(self, unit=None, proof=None):
        return provenance.classify_unit(
            self.unit if unit is None else unit,
            self.proof if proof is None else proof,
        )["provenance_class"]

    def test_verified_replay_is_machine_registry_contact(self) -> None:
        self.assertEqual(self.classified(), provenance.MACHINE_REGISTRY_CONTACT)

    def test_same_bytes_at_other_locator_are_unknown(self) -> None:
        copied = {**self.unit, "locator": self.unit["locator"].replace("open-inventory", "discussion")}
        self.assertEqual(self.classified(copied, self.proof), provenance.UNKNOWN)

    def test_hash_only_or_false_replay_proof_is_unknown(self) -> None:
        hash_only = {"content_sha256": self.unit["content_sha256"]}
        self.assertEqual(self.classified(proof=hash_only), provenance.UNKNOWN)
        false_replay = {**self.proof, "deterministic_exact_replay_verified": False}
        self.assertEqual(self.classified(proof=false_replay), provenance.UNKNOWN)

    def test_interactive_tool_outputs_never_auto_exempt(self) -> None:
        for role in ("codex-tool-output", "claude-tool-output", "agent-tool-output", "custom-tool-output"):
            unit = {**self.unit, "source_kind": "git_sessions", "role": role}
            proof = {**self.proof, "source_kind": "git_sessions", "role": role}
            proof["unit_identity_sha256"] = provenance.unit_identity_sha256(unit)
            self.assertEqual(self.classified(unit, proof), provenance.SEMANTIC_EXPOSURE)

    def test_mixed_or_malformed_fail_unknown_before_proof(self) -> None:
        self.assertEqual(self.classified({**self.unit, "mixed": True}, self.proof), provenance.UNKNOWN)
        self.assertEqual(self.classified({"role": "machine-generated-git-blob"}, self.proof), provenance.UNKNOWN)

    def test_legacy_unverifiable_custody_claim_is_unknown(self) -> None:
        unit = {**self.unit, "source_kind": "git_vendor", "role": "vendor-base-blob"}
        proof = {
            **{key: unit[key] for key in (
                "source_id", "source_kind", "locator", "role", "content_sha256", "content_schema"
            )},
            "schema_version": "c5k4-immutable-source-custody-receipt-1.5",
            "verification_status": "VERIFIED", "unit_identity_sha256": provenance.unit_identity_sha256(unit),
            "authenticated_fresh_bare_capture": True, "base_commit_verified": True,
            "base_tree_verified": True, "no_semantic_rendering_evidenced": True,
            "locator_specific_proof": True,
        }
        self.assertEqual(self.classified(unit, proof), provenance.UNKNOWN)
        broken = copy.deepcopy(proof)
        broken["base_tree_verified"] = False
        self.assertEqual(self.classified(unit, broken), provenance.UNKNOWN)

    def test_semantic_or_unknown_excludes_cluster(self) -> None:
        self.assertFalse(provenance.cluster_excluded([
            {"provenance_class": provenance.MACHINE_REGISTRY_CONTACT},
            {"provenance_class": provenance.IMMUTABLE_SOURCE_CUSTODY},
        ]))
        self.assertTrue(provenance.cluster_excluded([
            {"provenance_class": provenance.UNKNOWN}
        ]))

    def test_ontology_declares_exactly_four_classes(self) -> None:
        ontology = provenance.load_ontology(ROOT / "results/benchmark/v1.5-protocol/provenance-ontology.json")
        self.assertEqual(set(ontology["classes"]), provenance.CLASSES)

    def test_ontology_distinguishes_outside_delivery_from_participant_ingress_gap(self) -> None:
        ontology = provenance.load_ontology(ROOT / "results/benchmark/v1.5-protocol/provenance-ontology.json")
        classification = ontology["classification"]
        self.assertFalse(
            classification["outside_nonparticipant_delivery_with_proved_zero_ingress_creates_unit"]
        )
        self.assertTrue(
            classification["possible_unregistered_participant_ingress_is_protocol_invalid"]
        )
        boundary = ontology["source_boundary"]
        self.assertIn("zero ingress", boundary["excluded_surface_condition"])
        self.assertNotIn("retained Codex and Claude sessions", boundary["includes"])
        principles = " ".join(ontology["principles"])
        self.assertIn("no human participants and no model endpoints", principles)
        self.assertIn("PROTOCOL_INVALID", principles)


if __name__ == "__main__":
    unittest.main()
