#!/usr/bin/env python3
"""Constructor-only tests for the frozen solvable/cyclic-subgroup lane."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import search_solvable_cyclic_subgroups_live as target
import verify_solvable_cyclic_subgroups_certificate as verifier


def fixture_profile(identifier: str) -> dict[str, object]:
    rows = {
        "S3": target.parse_profile_line(
            "@@PROFILE@@\t6\t2,3\t2\t5\ttrue\t1:1,2:3,3:2\t(1,2)|(1,2,3)\t@@END@@",
            target.GroupDescriptor("S3", "SymmetricGroup(3)", "fixture"),
        ),
        "A4": target.parse_profile_line(
            "@@PROFILE@@\t12\t2,3\t2\t8\ttrue\t1:1,2:3,3:8\t(1,2,3)|(1,2)(3,4)\t@@END@@",
            target.GroupDescriptor("A4", "AlternatingGroup(4)", "fixture"),
        ),
        "A5": target.parse_profile_line(
            "@@PROFILE@@\t60\t2,3,5\t3\t32\tfalse\t1:1,2:15,3:20,5:24\t(1,2,3)|(1,2,3,4,5)\t@@END@@",
            target.GroupDescriptor("A5", 'SimpleGroup("A5")', "fixture"),
        ),
    }
    return rows[identifier]


class SolvableCyclicSubgroupsFreezeTests(unittest.TestCase):
    def test_manifest_and_artifact_locks(self) -> None:
        manifest = target.load_and_verify_manifest(target.DEFAULT_MANIFEST)
        self.assertEqual(manifest["evidence_split"], "DEVELOPMENT")
        self.assertEqual(manifest["upstream"]["commit"], target.UPSTREAM_COMMIT)
        self.assertFalse(manifest["candidate_policy"]["public_action"])

    def test_source_documented_a5_histogram_is_exact(self) -> None:
        profile = fixture_profile("A5")
        self.assertEqual(profile["cyclic_subgroups"], 32)
        self.assertEqual(profile["threshold"], 32)
        self.assertEqual(profile["residual"], 0)
        self.assertFalse(profile["solvable"])

    def test_database_gate_uses_fixtures_without_running_gap(self) -> None:
        receipt = target.database_sanity_gate(lambda descriptor: fixture_profile(descriptor.identifier))
        self.assertEqual([row["identifier"] for row in receipt["controls"]], ["S3", "A4", "A5"])
        self.assertEqual(receipt["target_domain_nonsolvable_groups_evaluated"], 0)

    def test_constructor_domains_are_frozen(self) -> None:
        self.assertEqual((target.catalogue_orders().start, target.catalogue_orders().stop), (60, 256))
        self.assertEqual((target.generic_orders().start, target.generic_orders().stop), (256, 2001))
        rows = target.wall_descriptors()
        identifiers = [row.identifier for row in rows]
        for expected in ("A5", "A6", "M11", "J1", "PSU3_4", "Sz8", "PSL2_64", "Aut_PSL2_64"):
            self.assertIn(expected, identifiers)
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_generic_sampling_is_deterministic_and_bounded(self) -> None:
        ids = tuple(range(1, 30))
        first = target.deterministic_generic_ids(360, ids)
        second = target.deterministic_generic_ids(360, reversed(ids))
        self.assertEqual(first, second)
        self.assertEqual(len(first), target.GENERIC_PER_ORDER)
        expected = sorted(
            ids,
            key=lambda identifier: hashlib.sha256(
                f"{target.GENERIC_SEED}:360:{identifier}".encode("ascii")
            ).digest(),
        )[: target.GENERIC_PER_ORDER]
        self.assertEqual(first, tuple(sorted(expected)))

    def test_gap_sources_only_construct_frozen_queries(self) -> None:
        descriptor = target.smallgroup_descriptor(168, 42, "test")
        source = target.profile_gap_source(descriptor)
        self.assertIn("SmallGroup(168,42)", source)
        self.assertIn('SetPrintFormattingStatus("*stdout*",false);;', source)
        self.assertIn("ConjugacyClasses(G)", source)
        self.assertIn("Phi", source)
        self.assertIn("@@PROFILE@@", source)
        self.assertIn("@@END@@", source)
        ids_source = target.ids_gap_source(168)
        self.assertIn("IdsOfAllSmallGroups", ids_source)
        self.assertIn("IsSolvableGroup,false", ids_source)

    def test_wrapped_profile_marker_is_rejected_fail_closed(self) -> None:
        descriptor = target.GroupDescriptor(
            "Aut_A5", 'AutomorphismGroup(SimpleGroup("A5"))', "fixture"
        )
        wrapped = (
            "@@PROFILE@@\t120\t2,3,5\t3\t40\tfalse\t"
            "1:1,2:25,3:20,4:30,5:24,6:20\t(1,2,3,4,5)\n"
            "(6,7,8,9,10)"
        )
        with self.assertRaises(target.SearchError):
            target.parse_profile_line(target.marker_line(wrapped, "@@PROFILE@@"), descriptor)

    def test_hash_chained_fsync_ledger_and_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            ledger = target.DurableLedger(root / "ledger.jsonl", "GENERIC")
            ledger.emit("synthetic", {"value": 7})
            receipt = target.write_terminal(root / "terminal.json", ledger, "PROPOSAL_LIMIT", {"value": 8})
            previous = target.ZERO_SHA256
            for sequence, line in enumerate((root / "ledger.jsonl").read_text().splitlines()):
                row = json.loads(line)
                self.assertEqual(row["sequence"], sequence)
                self.assertEqual(row["previous_row_sha256"], previous)
                claimed = row.pop("row_sha256")
                self.assertEqual(claimed, hashlib.sha256(target.canonical_json(row)).hexdigest())
                previous = claimed
            self.assertEqual(receipt["final_row_sha256"], previous)

    def test_independent_verifier_rejects_non_crossing_shape_without_gap(self) -> None:
        profile = fixture_profile("A5")
        document = {"schema": verifier.CERTIFICATE_SCHEMA, "primary": profile}
        with self.assertRaises(verifier.SearchError):
            verifier.validate_candidate_shape(document)

    def test_workflow_is_manual_read_only_exact_commit_and_hard_capped(self) -> None:
        workflow = target.REPO_ROOT / ".github" / "workflows" / "solvable-cyclic-subgroups-development.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("gap=4.12.1-2build2", text)
        self.assertIn("gap-smallgrp=1.5.3-1", text)
        self.assertIn("gap-primgrp=3.4.4-1", text)
        self.assertIn("timeout --signal=TERM --kill-after=5s 60s", text)
        self.assertNotIn("release", text.lower())


if __name__ == "__main__":
    unittest.main()
