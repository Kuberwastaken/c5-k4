#!/usr/bin/env python3
"""Regression tests for the Method v1.1 contamination-inventory builder."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_contamination_inventory as inventory


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True)


class InventoryTests(unittest.TestCase):
    def test_alias_boundary_and_no_bare_numeric_alias(self) -> None:
        aliases = inventory.aliases_for(
            "FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean",
            ["conjecture19"],
        )
        self.assertIn("wowii 19", aliases)
        haystack = inventory.normalized_tokens("WOWII 191 was discussed")
        self.assertNotIn(" wowii 19 ", haystack)
        erdos_aliases = inventory.aliases_for(
            "FormalConjectures/ErdosProblems/23.lean", ["erdos_23"]
        )
        self.assertNotIn("23", erdos_aliases)
        self.assertIn("erdos 23", erdos_aliases)

    def test_fail_closed_on_missing_source(self) -> None:
        clusters = [
            {
                "cluster_id": "x",
                "identity_sha256": "1" * 64,
                "source_blob_sha256": "2" * 64,
                "aliases": ["erdos 23"],
            }
        ]
        _, rows = inventory.scan(
            {
                "sources": [
                    {
                        "id": "missing",
                        "kind": "sessions",
                        "format": "codex",
                        "path": "/definitely/missing",
                    }
                ]
            },
            clusters,
            set(),
        )
        self.assertEqual(rows[0]["exposure_status"], "EXPOSED")
        self.assertEqual(rows[0]["exposure_basis"], "CONSERVATIVE_UNCERTAINTY")

    def test_session_parser_skips_tool_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "response_item",
                                "payload": {
                                    "type": "function_call_output",
                                    "output": "Erdos 23",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "response_item",
                                "payload": {
                                    "type": "message",
                                    "role": "assistant",
                                    "content": [
                                        {"type": "output_text", "text": "Erdos 23"}
                                    ],
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            units = list(inventory.iter_sessions(Path(directory), "codex", "sessions"))
            self.assertEqual(len(units), 1)
            self.assertEqual(units[0]["role"], "assistant")

    def test_git_session_parser_pins_commit_and_skips_tool_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            transcript = repo / "codex" / "session.jsonl"
            transcript.parent.mkdir(parents=True)
            transcript.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "response_item",
                                "payload": {
                                    "type": "function_call_output",
                                    "output": "Erdos 23",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "response_item",
                                "payload": {
                                    "type": "message",
                                    "role": "user",
                                    "content": [
                                        {"type": "input_text", "text": "Erdos 24"}
                                    ],
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "add", "codex/session.jsonl")
            git(
                repo,
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-qm",
                "fixture",
            )
            commit = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
            ).strip()
            units = list(
                inventory.iter_git_sessions(
                    repo, commit, "codex", "codex", "sessions:codex"
                )
            )
            self.assertEqual(len(units), 1)
            self.assertEqual(units[0]["role"], "user")
            with self.assertRaisesRegex(ValueError, "exact commit"):
                list(
                    inventory.iter_git_sessions(
                        repo, "HEAD", "codex", "codex", "sessions:codex"
                    )
                )

    def test_partial_session_row_is_scanned_conservatively(self) -> None:
        raw = b'{"type":"response_item","text":"Erdos 23'
        units = list(
            inventory.session_bytes_units(raw, "codex", "sessions", "partial.jsonl")
        )
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["role"], "malformed-json-raw")

    def test_registry_parser_groups_open_siblings_by_module(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            source = repo / "FormalConjectures" / "X" / "Question.lean"
            source.parent.mkdir(parents=True)
            source.write_text(
                "@[category research open, AMS 5]\n"
                "theorem question_one : True := by sorry\n"
                "@[category research open, AMS 5]\n"
                "theorem question_two : True := by sorry\n"
                "@[category research solved, AMS 5]\n"
                "theorem old : True := by trivial\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "add", "FormalConjectures/X/Question.lean")
            git(
                repo,
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-qm",
                "fixture",
            )
            upstream, clusters = inventory.open_clusters(repo, "HEAD")
            self.assertEqual(len(clusters), 1)
            self.assertEqual(
                [row["name"] for row in clusters[0]["declarations"]],
                ["question_one", "question_two"],
            )
            self.assertEqual(len(upstream["commit"]), 40)
            self.assertEqual(len(clusters[0]["identity_sha256"]), 64)

    def test_git_delta_excludes_vendor_base_and_keeps_user_touch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "config", "user.name", "Test")
            git(repo, "config", "user.email", "test@example.com")
            (repo / "GraphConjecture19.lean").write_text(
                "conjecture19 registry only\n", encoding="utf-8"
            )
            git(repo, "add", "GraphConjecture19.lean")
            git(repo, "commit", "-qm", "vendor")
            vendor = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
            ).strip()
            git(repo, "update-ref", "refs/remotes/upstream/main", vendor)
            (repo / "GraphConjecture20.lean").write_text(
                "targeted proof\n", encoding="utf-8"
            )
            git(repo, "add", "GraphConjecture20.lean")
            git(repo, "commit", "-qm", "work on WOWII 20")
            units = list(
                inventory.iter_git_delta(repo, "delta", "refs/remotes/upstream/")
            )
            corpus = "\n".join(unit["text"] for unit in units)
            self.assertNotIn("conjecture19 registry only", corpus)
            self.assertIn("WOWII 20", corpus)

    def test_template_configuration_is_not_executable(self) -> None:
        with self.assertRaisesRegex(ValueError, "template_only"):
            inventory.validate_config(
                {
                    "schema_version": inventory.CONFIG_SCHEMA,
                    "template_only": True,
                    "sources": [{"id": "example", "kind": "tree", "path": "/tmp"}],
                }
            )

    def test_build_emits_benchmark_exclusion_sets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "formal"
            source = repo / "FormalConjectures" / "ErdosProblems" / "23.lean"
            source.parent.mkdir(parents=True)
            source.write_text(
                "@[category research open, AMS 5]\n"
                "theorem erdos_23 : True := by sorry\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            git(repo, "add", "FormalConjectures/ErdosProblems/23.lean")
            git(
                repo,
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "-qm",
                "fixture",
            )
            commit = subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
            ).strip()
            artifacts = root / "artifacts"
            artifacts.mkdir()
            (artifacts / "note.md").write_text("Prior work on Erdős Problem 23.\n")
            config = root / "sources.json"
            config.write_text(
                json.dumps(
                    {
                        "schema_version": inventory.CONFIG_SCHEMA,
                        "template_only": False,
                        "sources": [
                            {"id": "tree:fixture", "kind": "tree", "path": str(artifacts)}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = inventory.build_inventory(repo, commit, config)
            self.assertEqual(len(result["clusters"]), 1)
            self.assertEqual(result["clusters"][0]["exposure_status"], "EXPOSED")
            self.assertEqual(result["excluded_cluster_ids"], [result["clusters"][0]["cluster_id"]])
            self.assertEqual(
                result["excluded_identity_sha256s"],
                [result["clusters"][0]["identity_sha256"]],
            )
            self.assertEqual(
                result["excluded_declaration_sha256s"],
                [result["clusters"][0]["source_blob_sha256"]],
            )

    def test_exemption_is_unit_exact_and_research_worktree_still_counts(self) -> None:
        clusters = [
            {
                "cluster_id": "x",
                "identity_sha256": "1" * 64,
                "source_blob_sha256": "2" * 64,
                "aliases": ["erdos 23"],
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "open-inventory.json"
            generated.write_text('{"name":"Erdos 23"}\n', encoding="utf-8")
            exempt = inventory.sha256(generated.read_bytes())
            _, rows = inventory.scan(
                {
                    "sources": [
                        {"id": "worktree", "kind": "tree", "path": str(root)}
                    ]
                },
                clusters,
                {exempt},
            )
            self.assertEqual(rows[0]["exposure_status"], "UNEXPOSED")

            (root / "research.md").write_text(
                "We investigated Erdos 23.\n", encoding="utf-8"
            )
            _, rows = inventory.scan(
                {
                    "sources": [
                        {"id": "worktree", "kind": "tree", "path": str(root)}
                    ]
                },
                clusters,
                {exempt},
            )
            self.assertEqual(rows[0]["exposure_status"], "EXPOSED")
            self.assertEqual(rows[0]["evidence_total"], 1)


if __name__ == "__main__":
    unittest.main()
