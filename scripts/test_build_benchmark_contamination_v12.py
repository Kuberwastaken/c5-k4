#!/usr/bin/env python3
"""Regression tests for the provenance-aware Method v1.2 replay."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_contamination_v12 as replay


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def fixture_pool(clusters: list[dict]) -> dict:
    return {
        "schema_version": "c5k4-question-cluster-pool-1.2-prototype",
        "artifact_status": "PRE_P0_PROTOTYPE_NOT_A_FREEZE",
        "upstream": {"commit": "1" * 40, "tree": "2" * 40},
        "clusters": clusters,
    }


def cluster(cluster_id: str, path: str, name: str, stratum: str = "FINITE_COMBINATORIAL") -> dict:
    return {
        "cluster_id": cluster_id,
        "identity_sha256": replay.sha256(cluster_id.encode()),
        "path": path,
        "module_blob_sha256": "3" * 64,
        "declarations": [{"name": name, "kind": "theorem", "category_line": 1, "statement_header_sha256": "4" * 64}],
        "machine_stratum": stratum,
        "stratum": stratum,
        "classification_status": "CLASSIFIED",
        "classification_basis": "fixture",
        "grouping_rule": "ONE_SOURCE_MODULE_CONSERVATIVE_MERGE",
        "eligibility_scope": "PRE_CONTAMINATION_SYNTAX_ONLY",
        "eligible": True,
    }


def config(source: dict) -> dict:
    return {
        "schema_version": replay.CONFIG_SCHEMA,
        "artifact_status": replay.ARTIFACT_STATUS,
        "sources": [source],
    }


def exemptions(units: list[dict] | None = None) -> dict:
    return {"complete": True, "units": units or []}


def empty_overlay(head: str) -> dict:
    entries: list[dict] = []
    return {
        "complete": True,
        "base_head_commit": head,
        "inventory_sha256": replay.sha256(replay.canonical_json(entries)),
        "entries": entries,
    }


class ReplayTests(unittest.TestCase):
    def test_aliases_require_numeric_namespace_anchor(self) -> None:
        wow = cluster(
            "wow",
            "FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean",
            "conjecture19",
        )
        aliases = replay.aliases_for(wow)
        self.assertIn("wowii 19", aliases)
        self.assertNotIn("conjecture19", aliases)
        self.assertNotIn("conjecture 19", aliases)
        self.assertIn(
            "formalconjectures writtenonthewallii graphconjecture19 conjecture19",
            aliases,
        )
        erdos = cluster("erdos", "FormalConjectures/ErdosProblems/23.lean", "erdos_23")
        self.assertIn("erdos 23", replay.aliases_for(erdos))
        self.assertNotIn("23", replay.aliases_for(erdos))

    def test_git_units_split_commit_paths_and_blobs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "config", "user.name", "Test")
            git(repo, "config", "user.email", "test@example.com")
            (repo / "one.txt").write_text("Erdos 23\n", encoding="utf-8")
            (repo / "two.txt").write_text("unrelated\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "two files")
            tip = git(repo, "rev-parse", "HEAD")
            overlay = replay.source_snapshot.worktree_overlay(repo, tip)
            rows = list(
                replay.iter_git_history(
                    repo,
                    {"id": "history", "tips": [tip], "registry_units": {}},
                )
            )
            self.assertEqual(sum(row["role"] == "commit-message" for row in rows), 1)
            self.assertEqual(sum(row["role"] == "git-metadata" for row in rows), 2)
            self.assertEqual(sum(row["role"] == "repo-code" for row in rows), 2)
            self.assertFalse(any(b"Erdos 23" in row["raw"] and b"unrelated" in row["raw"] for row in rows))

    def test_registry_contact_is_provenance_bound_not_content_global(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "config", "user.name", "Test")
            git(repo, "config", "user.email", "test@example.com")
            raw = b'Erdos 23\n'
            (repo / "registered.json").write_bytes(raw)
            (repo / "copy.json").write_bytes(raw)
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "machine and copied prose")
            tip = git(repo, "rev-parse", "HEAD")
            blob = git(repo, "rev-parse", f"{tip}:registered.json")
            content_sha = replay.sha256(raw)
            locator = f"git-blob:{blob}:registered.json"
            identity = replay.sha256(b"bound identity")
            unit_row = {
                "source_id": "history",
                "locator": locator,
                "role": "machine-generated-git-blob",
                "content_sha256": content_sha,
                "content_schema": None,
                "unit_identity_sha256": identity,
                "producer_verified": True,
                "invocation_contract_verified": True,
                "output_digest_verified": True,
                "bounded_schema_verified": True,
                "mixed_unit_rejected": True,
            }
            result, _, _ = replay.build(
                fixture_pool([cluster("x", "FormalConjectures/ErdosProblems/23.lean", "erdos_23")]),
                config({"id": "history", "kind": "git", "path": str(repo), "tips": [tip], "worktree_overlay": replay.source_snapshot.worktree_overlay(repo, tip)}),
                exemptions([unit_row]),
            )
            row = result["clusters"][0]
            # The raw fixture is not a bounded-schema JSON artifact, so even a
            # path-bound proof must fail closed rather than become machine contact.
            self.assertEqual(row["evidence_by_provenance_class"]["MACHINE_REGISTRY_CONTACT"], 0)
            self.assertEqual(row["evidence_by_provenance_class"]["UNKNOWN"], 1)
            self.assertEqual(row["evidence_by_provenance_class"]["SEMANTIC_SOURCE"], 1)
            self.assertEqual(row["exposure_status"], "EXPOSED")

    def test_uncapped_evidence_and_feasibility_are_recomputed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(73):
                (root / f"note-{index}.txt").write_text("Erdos Problem 23\n", encoding="utf-8")
            pool = fixture_pool([cluster("x", "FormalConjectures/ErdosProblems/23.lean", "erdos_23")])
            inventory, overlay, certificate = replay.build(
                pool,
                config({"id": "tree", "kind": "tree", "path": str(root)}),
                exemptions(),
            )
            row = inventory["clusters"][0]
            self.assertEqual(row["evidence_total"], 73)
            self.assertEqual(len(row["evidence"]), 73)
            self.assertIsNone(inventory["evidence_cap"])
            self.assertFalse(overlay["clusters"][0]["eligible"])
            self.assertEqual(certificate["artifact_status"], replay.ARTIFACT_STATUS)
            self.assertEqual(certificate["result"], "FAIL")
            self.assertFalse(certificate["entropy_used"])
            self.assertEqual(certificate["selected_cluster_ids"], [])

    def test_malformed_session_unit_is_unknown_and_excluding(self) -> None:
        pool = fixture_pool([cluster("x", "FormalConjectures/ErdosProblems/23.lean", "erdos_23")])
        units = list(
            replay.session_units(
                b'{"broken":"Erdos 23"\n',
                "codex",
                "sessions",
                "git_sessions",
                "one.jsonl",
                {},
            )
        )
        self.assertEqual(units[0]["provenance_class"], "UNKNOWN")
        self.assertIn("x", replay.match_aliases(replay.alias_trie(pool)[0], units[0]["raw"]))

    def test_missing_source_fails_closed_without_alias_hit(self) -> None:
        pool = fixture_pool([cluster("x", "FormalConjectures/ErdosProblems/23.lean", "erdos_23")])
        inventory, overlay, _ = replay.build(
            pool,
            config({"id": "missing", "kind": "tree", "path": "/definitely/missing"}),
            exemptions(),
        )
        self.assertFalse(inventory["complete"])
        self.assertEqual(inventory["clusters"][0]["exposure_basis"], "INCOMPLETE_SOURCE_FAIL_CLOSED")
        self.assertFalse(overlay["clusters"][0]["eligible"])

    def test_worktree_overlay_omission_or_byte_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "config", "user.name", "Test")
            git(repo, "config", "user.email", "test@example.com")
            (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "base")
            tip = git(repo, "rev-parse", "HEAD")
            (repo / "current.txt").write_text("Erdos 23\n", encoding="utf-8")
            overlay = replay.source_snapshot.worktree_overlay(repo, tip)
            source = {"id": "history", "kind": "git", "path": str(repo), "tips": [tip], "worktree_overlay": overlay}
            rows = list(replay.iter_worktree_overlay(repo, source))
            self.assertTrue(any(row["role"] == "repo-code" for row in rows))
            omitted = json.loads(json.dumps(overlay))
            omitted["entries"] = []
            omitted["inventory_sha256"] = replay.sha256(replay.canonical_json([]))
            with self.assertRaisesRegex(ValueError, "drifted"):
                list(replay.iter_worktree_overlay(repo, {**source, "worktree_overlay": omitted}))
            (repo / "current.txt").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "drifted"):
                list(replay.iter_worktree_overlay(repo, source))


if __name__ == "__main__":
    unittest.main()
