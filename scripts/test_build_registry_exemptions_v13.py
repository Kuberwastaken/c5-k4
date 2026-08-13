#!/usr/bin/env python3
"""Tests for provenance-bound Method v1.3 registry exemptions."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_registry_exemptions_v13 as exemptions


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class Fixture:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        run_git(self.repo, "config", "user.name", "Test")
        run_git(self.repo, "config", "user.email", "test@example.com")
        self.generator = self.repo / "scripts" / "generate.py"
        self.generator.parent.mkdir()
        self.generator.write_text("print('deterministic generator')\n", encoding="utf-8")
        self.artifact = (
            json.dumps(
                {"schema_version": "c5k4-open-inventory-1.3", "declarations": []},
                sort_keys=True,
                indent=2,
            )
            + "\n"
        ).encode()
        target = self.repo / "results" / "open-inventory.json"
        target.parent.mkdir()
        target.write_bytes(self.artifact)
        # An identical byte sequence in a non-registered path must not inherit
        # the exemption merely because its content hash is equal.
        (self.repo / "discussion.json").write_bytes(self.artifact)
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-qm", "generated fixture")
        self.commit = run_git(self.repo, "rev-parse", "HEAD")
        self.invocation = {"cmd": "python3 scripts/generate.py --output -"}
        self.invocation_sha = exemptions.invocation_sha256(
            "exec_command", self.invocation
        )

    def ledger(self, *, raw: bytes | None = None) -> dict:
        artifact = self.artifact if raw is None else raw
        return {
            "schema_version": exemptions.LEDGER_SCHEMA,
            "trusted_generators": [
                {
                    "id": "open-inventory-generator",
                    "repo": str(self.repo),
                    "ref": self.commit,
                    "path": "scripts/generate.py",
                    "sha256": exemptions.sha256(self.generator.read_bytes()),
                }
            ],
            "outputs": [
                {
                    "id": "inventory-v13",
                    "artifact_kind": "open_inventory",
                    "schema_version": "c5k4-open-inventory-1.3",
                    "generator_id": "open-inventory-generator",
                    "content_sha256": exemptions.sha256(artifact),
                    "byte_count": len(artifact),
                    "git_paths": ["results/open-inventory.json"],
                    "invocation_sha256s": [self.invocation_sha],
                }
            ],
        }


class RegistryExemptionTests(unittest.TestCase):
    def test_git_match_is_bound_to_registered_path_and_verified_generator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            sources = {
                "schema_version": exemptions.SOURCE_SCHEMA,
                "sources": [
                    {"id": "campaign", "kind": "git", "path": str(fixture.repo), "tips": [fixture.commit]}
                ],
            }
            result = exemptions.build(fixture.ledger(), sources)
            self.assertTrue(result["complete"])
            self.assertEqual(len(result["units"]), 1)
            self.assertIn("results/open-inventory.json", result["units"][0]["locator"])
            self.assertNotIn("discussion.json", result["units"][0]["locator"])
            self.assertNotEqual(
                result["units"][0]["content_sha256"],
                result["units"][0]["unit_identity_sha256"],
            )

    def test_generator_ref_and_content_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            ledger = fixture.ledger()
            ledger["trusted_generators"][0]["ref"] = "HEAD"
            with self.assertRaisesRegex(ValueError, "exact"):
                exemptions.validate_and_index_ledger(ledger)
            ledger = fixture.ledger()
            ledger["trusted_generators"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "content hash mismatch"):
                exemptions.validate_and_index_ledger(ledger)

    def test_codex_tool_output_matches_only_paired_recorded_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            session = fixture.repo / "sessions" / "one.jsonl"
            session.parent.mkdir()
            rows = [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": fixture.artifact.decode()}],
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call",
                        "call_id": "call-1",
                        "name": "exec_command",
                        "arguments": json.dumps(fixture.invocation),
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "function_call_output",
                        "call_id": "call-1",
                        "output": fixture.artifact.decode(),
                    },
                },
            ]
            session.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
            run_git(fixture.repo, "add", "sessions/one.jsonl")
            run_git(fixture.repo, "commit", "-qm", "session fixture")
            session_commit = run_git(fixture.repo, "rev-parse", "HEAD")
            sources = {
                "schema_version": exemptions.SOURCE_SCHEMA,
                "sources": [
                    {
                        "id": "codex-snapshot",
                        "kind": "git_sessions",
                        "path": str(fixture.repo),
                        "ref": session_commit,
                        "subdir": "sessions",
                        "format": "codex",
                    }
                ],
            }
            result = exemptions.build(fixture.ledger(), sources)
            self.assertTrue(result["complete"])
            self.assertEqual(len(result["units"]), 1)
            self.assertEqual(result["units"][0]["role"], "codex-tool-output")

            ledger = fixture.ledger()
            ledger["outputs"][0]["invocation_sha256s"] = ["0" * 64]
            result = exemptions.build(ledger, sources)
            self.assertFalse(result["complete"])
            self.assertEqual(result["units"], [])

    def test_claude_tool_output_is_role_bound_and_keeps_physical_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            tool_input = {"command": "python3 scripts/generate.py --output -"}
            invocation = exemptions.invocation_sha256("Bash", tool_input)
            ledger = fixture.ledger()
            ledger["outputs"][0]["invocation_sha256s"] = [invocation]
            session = fixture.repo / "claude" / "one.jsonl"
            session.parent.mkdir()
            rows = [
                "{partial synchronized row",
                json.dumps(
                    {
                        "type": "assistant",
                        "message": {
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": "tool-1",
                                    "name": "Bash",
                                    "input": tool_input,
                                }
                            ]
                        },
                    }
                ),
                json.dumps(
                    {
                        "type": "user",
                        "toolUseResult": {"stdout": fixture.artifact.decode()},
                        "message": {
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": "tool-1",
                                    "content": fixture.artifact.decode(),
                                }
                            ]
                        },
                    }
                ),
            ]
            session.write_text("\n".join(rows) + "\n")
            run_git(fixture.repo, "add", "claude/one.jsonl")
            run_git(fixture.repo, "commit", "-qm", "claude session fixture")
            commit = run_git(fixture.repo, "rev-parse", "HEAD")
            sources = {
                "schema_version": exemptions.SOURCE_SCHEMA,
                "sources": [
                    {
                        "id": "claude-snapshot",
                        "kind": "git_sessions",
                        "path": str(fixture.repo),
                        "ref": commit,
                        "subdir": "claude",
                        "format": "claude",
                    }
                ],
            }
            result = exemptions.build(ledger, sources)
            self.assertTrue(result["complete"])
            self.assertEqual(result["units"][0]["role"], "claude-tool-output")
            self.assertTrue(result["units"][0]["locator"].endswith(":3"))

    def test_mixed_prose_cannot_be_registered_as_machine_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            prose = b'{"schema_version":"c5k4-open-inventory-1.3"}\nDiscussion follows.'
            claim = fixture.ledger(raw=prose)["outputs"][0]
            with self.assertRaisesRegex(ValueError, "one complete JSON"):
                exemptions.validate_machine_artifact(prose, claim)

    def test_quota_feasibility_reports_each_deficit_without_statements(self) -> None:
        pool = {
            "schema_version": "c5k4-eligible-cluster-pool-1.3",
            "clusters": [
                {"cluster_id": "a", "stratum": "A", "eligible": True},
                {"cluster_id": "b", "stratum": "A", "eligible": True},
                {"cluster_id": "c", "stratum": "B", "eligible": True},
                {"cluster_id": "d", "stratum": "B", "eligible": False},
            ],
        }
        result = exemptions.quota_feasibility(pool, {"A": 2, "B": 2})
        self.assertFalse(result["all_quotas_satisfied"])
        self.assertEqual(result["eligible_cluster_count"], 3)
        self.assertEqual(result["strata"][0]["deficit"], 0)
        self.assertEqual(result["strata"][1]["deficit"], 1)


if __name__ == "__main__":
    unittest.main()
