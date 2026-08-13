#!/usr/bin/env python3
"""Contract tests for the target-blind Method v1.5 source boundary."""

from __future__ import annotations

import json
from pathlib import Path
import re
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
    "PROJECT_ROOT_CLASSIFIED_COLLECTION",
    "SESSION_ARCHIVE",
    "CHAT_ARCHIVE_GIT_REPOSITORY",
    "RELEASE_EXPORT",
    "ISSUE_PR_EXPORT",
    "GENERATED_ARTIFACT",
    "GENERATED_ARTIFACT_COLLECTION",
}
FROZEN_PROJECT_CHILDREN = {
    "--continue", "--resume", "--reusme", "breakthroughmaxxing", "c5-k4",
    "claurst", "conway99-c3-orbits-lean", "cookie", "formal-conjectures",
    "formal-conjectures-counterexamples", "formal-conjectures-wowii309",
    "grok-build", "hive", "hive-logo", "hive-mind",
    "kuberwastaken.github.io", "linkedin-forensics", "marketing-outbound",
    "megaphone", "permanental-dominance-n4", "reimann", "resume",
    "scratch", "sira-router", "subagentmaxxing", "vpsmaxxing-logo",
    "wanless-778-lean", "wowii-63-85-counterexample", "zeta-23-lean",
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

    def test_boundary_is_target_blind_and_spans_the_whole_interval(self) -> None:
        value = self.boundary
        self.assertEqual(value["schema"], "c5k4-method-v1.5-source-boundary-1.0")
        self.assertEqual(value["status"], "PRE_P1_TARGET_BLIND")
        self.assertEqual(value["scope"]["lower_endpoint"], "PUBLIC_P1T_RECEIPT")
        self.assertEqual(value["scope"]["upper_endpoint"], "PRE_SELECTION_SOURCE_CUTOFF")
        self.assertEqual(value["scope"]["interval"], "P1T_EXCLUSIVE_CUTOFF_INCLUSIVE")
        self.assertTrue(value["scope"]["covers_new_sources_introduced_during_interval"])
        self.assertFalse(value["scope"]["candidate_identity_joined"])
        self.assertFalse(value["scope"]["candidate_semantics_inspected"])
        forbidden = re.compile(
            r"(?:cluster_id|conjecture_id|statement_text|selected_clusters|candidate_ids)",
            re.IGNORECASE,
        )
        self.assertIsNone(forbidden.search(json.dumps(value, sort_keys=True)))

    def test_origin_and_exposure_are_separate_exhaustive_axes(self) -> None:
        axes = self.boundary["axes"]
        self.assertEqual(set(axes), {"origin", "exposure", "orthogonality"})
        self.assertEqual(set(axes["origin"]["values"]), ORIGINS)
        self.assertEqual(set(axes["exposure"]["values"]), EXPOSURES)
        self.assertGreaterEqual(len(axes["orthogonality"]), 5)
        sources = self.boundary["required_sources"]
        for source in sources:
            self.assertTrue(set(source["origin_values_allowed"]) <= ORIGINS)
            self.assertTrue(set(source["exposure_values_allowed"]) <= EXPOSURES)
            self.assertNotIn("provenance_class", source)
            self.assertNotIn("origin_to_exposure", source)
        # The same TOOL origin can have multiple dispositions.  This guards
        # against silently reconstructing a one-axis provenance model.
        tool_exposures = set().union(*(
            set(row["exposure_values_allowed"])
            for row in sources if "TOOL" in row["origin_values_allowed"]
        ))
        self.assertEqual(tool_exposures, EXPOSURES)

    def test_every_required_source_family_is_present_once_or_more(self) -> None:
        sources = self.boundary["required_sources"]
        ids = [row["source_id"] for row in sources]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({row["kind"] for row in sources}, REQUIRED_SOURCE_KINDS)
        by_id = {row["source_id"]: row for row in sources}
        required_ids = {
            "projects-research", "codex-local-sessions", "claude-local-sessions",
            "synchronized-ai-chats", "github-c5k4-releases",
            "github-c5k4-issues-pull-requests",
            "github-formal-conjectures-issues-pull-requests",
            "github-c5k4-actions", "declared-external-generated-artifacts",
        }
        self.assertEqual(set(by_id), required_ids)
        self.assertEqual(by_id["codex-local-sessions"]["locator"], "/home/ec2-user/.codex/sessions")
        self.assertEqual(by_id["claude-local-sessions"]["locator"], "/home/ec2-user/.claude/projects")
        self.assertEqual(by_id["synchronized-ai-chats"]["locator"], "/home/ec2-user/.local/share/ai-chats")
        self.assertIn("comments,reviews,timeline", by_id["github-c5k4-issues-pull-requests"]["locator"])
        self.assertIn("comments,reviews,timeline", by_id["github-formal-conjectures-issues-pull-requests"]["locator"])
        self.assertIn("runs,jobs,logs,artifacts", by_id["github-c5k4-actions"]["locator"])
        self.assertTrue(all(row["complete_when"] for row in sources))

    def test_interval_capture_cannot_be_claimed_from_endpoints_alone(self) -> None:
        capture = self.boundary["capture"]
        journal = capture["event_journal"]
        self.assertIn("P1 and cutoff endpoint trees alone do not establish interval completeness", journal["rule"])
        self.assertEqual(journal["gap_or_overflow"], "FAIL_CLOSED")
        self.assertEqual(capture["session_sync"]["maximum_expected_interval_seconds"], 300)
        self.assertTrue(capture["session_sync"]["local_and_archive_required"])
        self.assertEqual(capture["platform_exports"]["api_or_permission_gap"], "FAIL_CLOSED")
        self.assertEqual(capture["generated_artifacts"]["declaration_time"], "before producer invocation")
        self.assertEqual(capture["generated_artifacts"]["undeclared_or_unbounded"], "UNKNOWN")

    def test_failure_policy_is_uniformly_fail_closed(self) -> None:
        policy = self.boundary["failure_policy"]
        for key in (
            "missing_required_source", "unclassified_source_or_unit", "coverage_gap",
            "source_drift_during_capture", "new_research_path_not_matched_by_frozen_policy",
        ):
            self.assertEqual(policy[key], "FAIL_CLOSED")
        self.assertEqual(policy["unsupported_or_malformed_record"], "UNKNOWN")
        self.assertEqual(policy["unproved_delivery_path"], "UNKNOWN")
        self.assertEqual(policy["mixed_unit"], "UNKNOWN")
        self.assertEqual(policy["manual_exemption"], "FORBIDDEN")
        self.assertEqual(policy["target_identity_based_reclassification"], "FORBIDDEN")

    def test_path_policy_classifies_frozen_root_exactly_once(self) -> None:
        policy = self.policy
        self.assertEqual(policy["schema"], "c5k4-source-path-purpose-policy-1.5")
        self.assertEqual(policy["default"], "FAIL_UNCLASSIFIED")
        self.assertTrue(policy["matching"]["full_match_required"])
        self.assertTrue(policy["matching"]["exactly_one_rule_required"])
        rules = policy["rules"]
        self.assertEqual(len({row["id"] for row in rules}), len(rules))
        for name in FROZEN_PROJECT_CHILDREN:
            matches = [row for row in rules if re.fullmatch(row["relative_path_regex"], name)]
            self.assertEqual(len(matches), 1, name)
        self.assertEqual(
            {path.name for path in Path(policy["root"]).iterdir()},
            FROZEN_PROJECT_CHILDREN,
            "P1 must fail if the project-root boundary gains or loses a path",
        )
        self.assertFalse(any(re.fullmatch(row["relative_path_regex"], "future-unknown-research") for row in rules))

    def test_policy_preserves_vendor_partition_and_overlay_capture(self) -> None:
        rules = {row["id"]: row for row in self.policy["rules"]}
        self.assertEqual(
            rules["upstream-formal-conjectures"]["capture_profile"],
            "GIT_VENDOR_PARTITION_AND_OVERLAY",
        )
        self.assertEqual(
            rules["primary-research"]["capture_profile"],
            "GIT_HISTORY_OVERLAY_AND_GENERATED_ARTIFACTS",
        )
        self.assertEqual(
            rules["unversioned-mathematics-research"]["capture_profile"],
            "TREE_EVENT_JOURNAL_AND_ENDPOINT",
        )


if __name__ == "__main__":
    unittest.main()
