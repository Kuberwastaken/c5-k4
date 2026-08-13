#!/usr/bin/env python3
"""Focused tests for the Method v1.5 Git provenance partition."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_v15_vendor_bases as vendor
import partition_git_provenance_v15 as partition
from test_build_benchmark_v15_vendor_bases import make_bare, receipt_for, run


def source_from_bare(base: Path, bare: Path, commit: str) -> Path:
    source = base / "research"
    run("git", "clone", "-q", str(bare), str(source))
    # The namespaced-only bare repository has no HEAD, so establish the base explicitly.
    run("git", "checkout", "-q", "-b", "main", commit, cwd=source)
    run("git", "config", "user.name", "Fixture", cwd=source)
    run("git", "config", "user.email", "fixture@example.invalid", cwd=source)
    return source


def fixture(base: Path) -> tuple[Path, dict]:
    bare, commit = make_bare(base)
    return source_from_bare(base, bare, commit), receipt_for(bare)


def commit_file(repo: Path, path: str, text: str, message: str = "user delta") -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    run("git", "add", path, cwd=repo)
    run("git", "commit", "-q", "-m", message, cwd=repo)
    return run("git", "rev-parse", "HEAD", cwd=repo)


class PartitionTests(unittest.TestCase):
    def test_exact_base_blob_is_custody_and_user_delta_is_semantic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, receipt = fixture(Path(tmp))
            commit_file(repo, "new.txt", "user\n")
            result = partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")
            base = [unit for unit in result["units"] if unit["role"] == "vendor-base-blob"]
            deltas = [unit for unit in result["units"] if unit["role"] == "user-path-delta"]
            self.assertEqual([unit["provenance_class"] for unit in base], [partition.IMMUTABLE] * 2)
            self.assertEqual({unit["path"] for unit in base}, {"a.txt", "nested/b.txt"})
            self.assertTrue(deltas)
            self.assertTrue(all(unit["provenance_class"] == partition.SEMANTIC for unit in deltas))
            self.assertFalse(result["fail_closed"])

    def test_rename_or_copy_never_inherits_vendor_custody(self) -> None:
        for operation in ("rename", "copy"):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as tmp:
                repo, receipt = fixture(Path(tmp))
                if operation == "rename":
                    run("git", "mv", "a.txt", "renamed.txt", cwd=repo)
                else:
                    (repo / "copied.txt").write_bytes((repo / "a.txt").read_bytes())
                    run("git", "add", "copied.txt", cwd=repo)
                run("git", "commit", "-q", "-m", operation, cwd=repo)
                result = partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")
                opaque = [unit for unit in result["units"] if unit.get("status", "").startswith(("R", "C"))]
                self.assertTrue(opaque)
                self.assertTrue(all(unit["provenance_class"] == partition.UNKNOWN for unit in opaque))
                self.assertTrue(result["fail_closed"])

    def test_cherry_pick_is_a_non_vendor_semantic_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, receipt = fixture(Path(tmp))
            base = run("git", "rev-parse", "HEAD", cwd=repo)
            run("git", "checkout", "-q", "-b", "topic", cwd=repo)
            picked = commit_file(repo, "topic.txt", "topic\n", "topic")
            run("git", "checkout", "-q", "main", cwd=repo)
            commit_file(repo, "main.txt", "main\n", "diverge main")
            run("git", "cherry-pick", picked, cwd=repo)
            self.assertNotEqual(run("git", "rev-parse", "HEAD", cwd=repo), picked)
            result = partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")
            messages = [unit for unit in result["units"] if unit["role"] == "user-commit-message"]
            self.assertTrue(messages)
            self.assertTrue(all(unit["provenance_class"] == partition.SEMANTIC for unit in messages))
            self.assertEqual(result["vendor_base_commit"], base)

    def test_unattested_merge_fails_closed_but_exact_attestation_is_semantic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, receipt = fixture(Path(tmp))
            run("git", "checkout", "-q", "-b", "topic", cwd=repo)
            commit_file(repo, "topic.txt", "topic\n")
            run("git", "checkout", "-q", "main", cwd=repo)
            commit_file(repo, "main.txt", "main\n")
            run("git", "merge", "-q", "--no-ff", "topic", "-m", "merge topic", cwd=repo)
            merge = run("git", "rev-parse", "HEAD", cwd=repo)
            parents = run("git", "show", "-s", "--format=%P", merge, cwd=repo).split()
            rejected = partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")
            merge_units = [unit for unit in rejected["units"] if unit.get("commit") == merge]
            self.assertTrue(any(unit["provenance_class"] == partition.UNKNOWN for unit in merge_units))
            accepted = partition.partition_repository(
                repo, "HEAD", receipt, source_id="fixture",
                merge_attestations={merge: {
                    "commit": merge, "parents": parents,
                    "attestation_sha256": partition.merge_attestation_sha256(merge, parents),
                }},
            )
            merge_units = [unit for unit in accepted["units"] if unit.get("commit") == merge]
            self.assertTrue(all(unit["provenance_class"] == partition.SEMANTIC for unit in merge_units))

            forged = partition.partition_repository(
                repo, "HEAD", receipt, source_id="fixture",
                merge_attestations={merge: {"commit": merge, "parents": parents, "attestation_sha256": "1" * 64}},
            )
            merge_units = [unit for unit in forged["units"] if unit.get("commit") == merge]
            self.assertTrue(any(unit["provenance_class"] == partition.UNKNOWN for unit in merge_units))

    def test_worktree_overlay_is_semantic_and_unmerged_index_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, receipt = fixture(Path(tmp))
            (repo / "a.txt").write_text("dirty\n", encoding="utf-8")
            result = partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")
            overlay = [unit for unit in result["units"] if unit["role"] == "worktree-overlay"]
            self.assertEqual([unit["provenance_class"] for unit in overlay], [partition.SEMANTIC])

    def test_uncommitted_rename_overlay_is_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, receipt = fixture(Path(tmp))
            run("git", "mv", "a.txt", "renamed.txt", cwd=repo)
            result = partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")
            overlay = [unit for unit in result["units"] if unit["role"] == "worktree-overlay"]
            self.assertEqual(len(overlay), 1)
            self.assertEqual(overlay[0]["provenance_class"], partition.UNKNOWN)
            self.assertEqual(overlay[0]["old_path"], "a.txt")

    def test_receipt_tampering_and_non_descendant_history_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, receipt = fixture(Path(tmp))
            tampered = json.loads(json.dumps(receipt))
            tampered["audit"]["root_tree"] = "0" * 40
            with self.assertRaises(vendor.VendorBaseError):
                partition.partition_repository(repo, "HEAD", tampered, source_id="fixture")
            run("git", "checkout", "-q", "--orphan", "unrelated", cwd=repo)
            run("git", "rm", "-q", "-rf", ".", cwd=repo)
            commit_file(repo, "other.txt", "other\n")
            with self.assertRaisesRegex(partition.PartitionError, "does not descend"):
                partition.partition_repository(repo, "HEAD", receipt, source_id="fixture")


if __name__ == "__main__":
    unittest.main()
