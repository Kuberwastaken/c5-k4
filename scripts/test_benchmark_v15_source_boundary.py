#!/usr/bin/env python3
"""Contract tests for the target-blind Method v1.5 delivery boundary."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "results/benchmark/v1.5-protocol"
BOUNDARY_PATH = PROTOCOL / "source-boundary.json"
PATH_POLICY_PATH = PROTOCOL / "source-path-purpose-policy.json"

ORIGINS = {
    "AUTHENTICATED_UPSTREAM", "USER", "ASSISTANT", "TOOL", "PLATFORM",
    "SESSION_METADATA", "UNPARSEABLE", "UNKNOWN",
}
EXPOSURES = {
    "SEMANTIC_EXPOSURE", "MACHINE_REGISTRY_CONTACT",
    "IMMUTABLE_SOURCE_CUSTODY", "UNKNOWN",
}
REQUIRED_SOURCE_KINDS = {
    "AUTHENTICATED_GIT_SOURCE",
    "DEDICATED_RESEARCH_REPOSITORY_COLLECTION",
    "HOST_SESSION_DELIVERY_JOURNAL",
    "PRIVATE_IMMUTABLE_CONTENT_STORE",
    "OWNED_PUBLIC_DELIVERY_JOURNAL",
    "DECLARED_GENERATED_DELIVERY_COLLECTION",
}
REQUIRED_SOURCE_IDS = {
    "authenticated-upstream-formal-conjectures-git",
    "dedicated-research-repositories",
    "mac-participant-model-delivery-journal",
    "vps-participant-model-delivery-journal",
    "authenticated-private-delivery-content-store",
    "owned-public-delivery-events",
    "declared-generated-deliveries",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} must contain one object")
    return value


class SourceBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.boundary = load(BOUNDARY_PATH)
        cls.policy = load(PATH_POLICY_PATH)

    def test_boundary_is_target_blind_pre_p1_and_explicitly_inert(self) -> None:
        value = self.boundary
        self.assertEqual(value["schema"], "c5k4-method-v1.5-source-boundary-1.1")
        self.assertEqual(value["status"], "PRE_P1_CAPTURE_NOT_OPERATIONAL")
        self.assertFalse(value["executable"])
        self.assertEqual(value["scope"]["lower_endpoint"], "PUBLIC_P1T_RECEIPT")
        self.assertEqual(value["scope"]["upper_endpoint"], "PRE_SELECTION_SOURCE_CUTOFF")
        self.assertEqual(value["scope"]["interval"], "P1T_EXCLUSIVE_CUTOFF_INCLUSIVE")
        self.assertEqual(
            value["scope"]["boundary_principle"],
            "ACTUAL_AUTHENTICATED_DELIVERY_NOT_GLOBAL_PUBLIC_AVAILABILITY",
        )
        self.assertFalse(value["scope"]["candidate_identity_joined"])
        self.assertFalse(value["scope"]["candidate_semantics_inspected"])
        self.assertFalse(value["activation"]["p1_publication_permitted"])
        self.assertFalse(value["activation"]["retroactive_reconstruction_permitted"])
        self.assertGreaterEqual(len(value["activation"]["currently_unset"]), 5)

    def test_origin_and_exposure_remain_orthogonal(self) -> None:
        axes = self.boundary["axes"]
        self.assertEqual(set(axes), {"origin", "exposure", "orthogonality"})
        self.assertEqual(set(axes["origin"]["values"]), ORIGINS)
        self.assertEqual(set(axes["exposure"]["values"]), EXPOSURES)
        self.assertGreaterEqual(len(axes["orthogonality"]), 5)
        sources = self.boundary["required_sources"]
        for source in sources:
            self.assertTrue(set(source["origin_values_allowed"]) <= ORIGINS)
            self.assertTrue(set(source["exposure_values_allowed"]) <= EXPOSURES)
            self.assertNotIn("origin_to_exposure", source)
        tool_exposures = set().union(*(
            set(row["exposure_values_allowed"])
            for row in sources if "TOOL" in row["origin_values_allowed"]
        ))
        self.assertEqual(tool_exposures, EXPOSURES)

    def test_required_sources_are_delivery_sources_not_global_surveillance(self) -> None:
        sources = self.boundary["required_sources"]
        ids = [row["source_id"] for row in sources]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), REQUIRED_SOURCE_IDS)
        self.assertEqual({row["kind"] for row in sources}, REQUIRED_SOURCE_KINDS)
        self.assertTrue(all(row["complete_when"] for row in sources))
        by_id = {row["source_id"]: row for row in sources}
        self.assertEqual(
            by_id["authenticated-upstream-formal-conjectures-git"]["locator"],
            "https://github.com/google-deepmind/formal-conjectures.git#refs/heads/main",
        )
        self.assertEqual(
            by_id["authenticated-private-delivery-content-store"]["locator"],
            "PRE_P1_UNSET",
        )
        serialized = json.dumps(sources, sort_keys=True)
        self.assertNotIn("global-issues-pulls-comments", serialized)
        self.assertNotIn("all-actions-runs-jobs-logs-artifacts", serialized)
        self.assertNotIn("ALL_RECORDS_CREATED_UPDATED_OR_DELETED", serialized)

    def test_impossible_global_sources_are_explicitly_disclaimed(self) -> None:
        exclusions = self.boundary["explicit_non_sources"]
        locators = {row["locator"] for row in exclusions}
        self.assertIn(
            "github:google-deepmind/formal-conjectures:global-issues-pulls-comments-reviews-timeline",
            locators,
        )
        self.assertIn(
            "github:Kuberwastaken/c5-k4:all-actions-runs-jobs-logs-artifacts",
            locators,
        )
        self.assertIn("all-files-under-/Users/kuber.mehta/Projects", locators)
        self.assertTrue(all(row["reason"] for row in exclusions))

    def test_host_capture_requires_signed_unbroken_hash_chains(self) -> None:
        capture = self.boundary["capture"]
        journals = capture["host_journals"]
        self.assertEqual(set(journals["required_hosts"]), {"companion-mac", "ai-vps"})
        self.assertEqual(journals["maximum_heartbeat_interval_seconds"], 300)
        self.assertEqual(
            set(journals["required_record_fields"]),
            {
                "host_id", "sequence_number", "previous_receipt_sha256",
                "payload_sha256", "payload_byte_count", "delivery_channel",
                "observed_at_utc", "signing_key_id", "signature",
            },
        )
        self.assertEqual(journals["gap_or_fork"], "FAIL_CLOSED_PROTOCOL_INVALID")
        sessions = capture["session_capture"]
        self.assertFalse(sessions["best_effort_rsync_is_completeness_proof"])
        self.assertFalse(sessions["git_mirror_alone_is_completeness_proof"])
        store = capture["immutable_content_store"]
        self.assertTrue(store["required"])
        self.assertIsNone(store["locator"])
        self.assertIsNone(store["authentication"])
        self.assertIsNone(store["retention_through_utc"])

    def test_every_unproved_delivery_or_capture_gap_fails_closed(self) -> None:
        policy = self.boundary["failure_policy"]
        for key in (
            "missing_required_source", "unclassified_source_or_unit",
            "coverage_gap", "source_drift_during_capture",
            "new_delivery_channel_not_in_frozen_ledger", "heartbeat_or_sequence_gap",
            "missing_or_invalid_signature", "missing_content_addressed_blob",
            "participant_used_unjournaled_device_or_browser",
        ):
            self.assertIn("FAIL_CLOSED", policy[key])
        self.assertEqual(policy["unsupported_or_malformed_record"], "UNKNOWN")
        self.assertEqual(policy["unproved_delivery_path"], "UNKNOWN")
        self.assertEqual(policy["mixed_unit"], "UNKNOWN")
        self.assertEqual(policy["manual_exemption"], "FORBIDDEN")
        self.assertEqual(policy["target_identity_based_reclassification"], "FORBIDDEN")

    def test_path_policy_uses_only_two_explicit_dedicated_roots(self) -> None:
        policy = self.policy
        self.assertEqual(policy["schema"], "c5k4-source-path-purpose-policy-1.5")
        self.assertEqual(policy["status"], "PRE_P1_CAPTURE_NOT_OPERATIONAL")
        self.assertEqual(policy["root_model"], "EXPLICIT_DEDICATED_ROOTS_ONLY")
        self.assertEqual(policy["default"], "FAIL_OUTSIDE_FROZEN_RESEARCH_ROOTS")
        self.assertTrue(policy["matching"]["exact_path_required"])
        self.assertTrue(policy["matching"]["exactly_one_rule_required"])
        roots = policy["roots"]
        self.assertEqual(
            {row["absolute_path"] for row in roots},
            {
                "/Users/kuber.mehta/Projects/c5-k4",
                "/Users/kuber.mehta/Projects/formal-conjectures",
            },
        )
        self.assertEqual(len({row["id"] for row in roots}), len(roots))
        self.assertTrue(all(row["decision"] == "INCLUDE" for row in roots))
        self.assertNotIn("/Users/kuber.mehta/Projects", {row["absolute_path"] for row in roots})

    def test_session_endpoints_cover_both_formats_on_both_hosts(self) -> None:
        endpoints = self.policy["session_delivery_endpoints"]
        self.assertEqual(
            {(row["host_id"], row["format"]) for row in endpoints},
            {
                ("companion-mac", "codex"), ("companion-mac", "claude"),
                ("ai-vps", "codex"), ("ai-vps", "claude"),
            },
        )
        self.assertEqual(len({row["absolute_path"] for row in endpoints}), 4)
        constraints = " ".join(self.policy["operational_constraints"])
        self.assertIn("fails closed", constraints)
        self.assertIn("healthy signed host delivery journal", constraints)


if __name__ == "__main__":
    unittest.main()
