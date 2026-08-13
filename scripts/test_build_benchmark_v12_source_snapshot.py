#!/usr/bin/env python3
"""Tests for semantics-blind Method v1.2 source discovery and S0 acquisition."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_v12_source_snapshot as snapshot


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_repo(path: Path, files: dict[str, str] | None = None) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    run_git(path, "config", "user.name", "Test")
    run_git(path, "config", "user.email", "test@example.com")
    for relative, content in (files or {"README": "fixture\n"}).items():
        target = path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    run_git(path, "add", ".")
    run_git(path, "commit", "-qm", "fixture")
    return path


class Fixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.projects = root / "projects"
        self.research = make_repo(self.projects / "math-research")
        self.nonresearch = make_repo(self.projects / "marketing")
        self.ai_chats = make_repo(
            root / "ai-chats",
            {
                "codex/session.jsonl": '{"type":"fixture"}\n',
                "claude/session.jsonl": '{"type":"fixture"}\n',
            },
        )
        self.codex = root / "local-codex"
        self.claude = root / "local-claude"
        self.codex.mkdir()
        self.claude.mkdir()
        (self.codex / "session.jsonl").write_text('{"type":"fixture"}\n')
        (self.claude / "session.jsonl").write_text('{"type":"fixture"}\n')
        self.release = root / "releases.json"
        self.release.write_text("[]\n", encoding="utf-8")
        self.policy = root / "policy.json"
        self.policy.write_text(
            snapshot.pretty_json(
                {
                    "schema_version": snapshot.POLICY_SCHEMA,
                    "default": "EXCLUDE_UNKNOWN",
                    "required_session_mirror_ids": ["codex", "claude"],
                    "required_release_snapshot_ids": ["project"],
                    "rules": [
                        {
                            "id": "research",
                            "relative_path_regex": "math-research",
                            "decision": "INCLUDE_SEMANTIC",
                            "purpose": "RESEARCH",
                        },
                        {
                            "id": "marketing",
                            "relative_path_regex": "marketing",
                            "decision": "EXCLUDE_NONRESEARCH",
                            "purpose": "NONRESEARCH",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.mirrors = [
            f"codex=codex:{self.codex}:codex",
            f"claude=claude:{self.claude}:claude",
        ]

    def config(self, attestation: Path | None = None, protocol_repo: Path | None = None) -> dict:
        return snapshot.build_config(
            self.projects,
            self.policy,
            self.ai_chats,
            self.mirrors,
            [f"project={self.release}"],
            attestation,
            protocol_repo or self.research,
        )


def public_protocol(root: Path, policy: Path, contract_sha: str) -> tuple[Path, Path, dict]:
    repo = make_repo(root / "protocol")
    p0a = run_git(repo, "rev-parse", "HEAD")
    (repo / "attestation-placeholder").write_text("P0T\n")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-qm", "attest protocol")
    p0t = run_git(repo, "rev-parse", "HEAD")
    remote = root / "public.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    run_git(repo, "remote", "add", "public", str(remote))
    run_git(repo, "push", "-q", "public", "HEAD:refs/heads/main")
    attestation = {
        "schema_version": snapshot.P0_SCHEMA,
        "p0_artifact_commit": p0a,
        "p0_attestation_commit": p0t,
        "p0_published_at_utc": "2026-08-13T10:00:00Z",
        "source_path_policy_sha256": snapshot.sha256(policy.read_bytes()),
        "source_discovery_contract_sha256": contract_sha,
        "public_remote_url": str(remote),
    }
    path = root / "p0.json"
    path.write_text(snapshot.pretty_json(attestation), encoding="utf-8")
    return repo, path, attestation


class SourceSnapshotTests(unittest.TestCase):
    def test_prototype_discovers_pins_and_exclusions_without_semantic_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            result = fixture.config()
            self.assertEqual(result["schema_version"], snapshot.PROTOTYPE_CONFIG_SCHEMA)
            self.assertTrue(result["prototype_only"])
            self.assertTrue(result["complete"])
            self.assertFalse(result["candidate_semantics_inspected"])
            self.assertEqual(len(result["nonresearch_exclusions"]), 1)
            research = next(row for row in result["sources"] if row["kind"] == "git_history")
            self.assertTrue(research["tips"][0]["object_id"])
            self.assertGreater(research["object_count"], 0)
            sessions = next(row for row in result["sources"] if row["kind"] == "git_sessions")
            self.assertTrue(all(row["mirror_agrees"] for row in sessions["session_mirrors"]))
            self.assertEqual(
                result["sources_config_sha256"],
                snapshot.content_address(result, "sources_config_sha256"),
            )
            rendered = snapshot.pretty_json(result)
            self.assertNotIn('{"type":"fixture"}', rendered)

    def test_unknown_repository_and_missing_required_sources_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            make_repo(fixture.projects / "unclassified")
            result = snapshot.build_config(
                fixture.projects,
                fixture.policy,
                None,
                [],
                [],
                None,
                fixture.research,
            )
            self.assertFalse(result["complete"])
            self.assertEqual(result["failures"]["unknown_path_count"], 1)
            self.assertTrue(result["failures"]["ai_chats_missing"])
            self.assertEqual(
                result["failures"]["missing_required_session_mirror_ids"],
                ["claude", "codex"],
            )

    def test_unsynced_local_session_mirror_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            (fixture.codex / "session.jsonl").write_text("changed\n")
            result = fixture.config()
            self.assertFalse(result["complete"])
            sessions = next(row for row in result["sources"] if row["kind"] == "git_sessions")
            self.assertFalse(sessions["complete"])

    def test_s0_requires_public_p0_and_rechecks_every_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = Fixture(root)
            contract_sha = snapshot.discovery_contract_sha256(
                fixture.projects, fixture.ai_chats, fixture.mirrors, [f"project={fixture.release}"]
            )
            protocol, attestation_path, _ = public_protocol(root, fixture.policy, contract_sha)
            config = fixture.config(attestation_path, protocol)
            self.assertEqual(config["schema_version"], snapshot.CONFIG_SCHEMA)
            self.assertFalse(config["prototype_only"])
            config_path = root / "sources.json"
            config_path.write_text(snapshot.pretty_json(config), encoding="utf-8")
            s0 = snapshot.acquire_s0(
                config_path,
                fixture.policy,
                attestation_path,
                protocol,
                "2026-08-13T10:00:01Z",
            )
            self.assertEqual(s0["snapshot_id"], "S0")
            self.assertTrue(s0["complete"])
            self.assertEqual(s0["snapshot_sha256"], snapshot.content_address(s0, "snapshot_sha256"))

            fixture.release.write_text("[{}]\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "release snapshot drifted"):
                snapshot.acquire_s0(
                    config_path,
                    fixture.policy,
                    attestation_path,
                    protocol,
                    "2026-08-13T10:00:02Z",
                )

    def test_public_p0_freezes_complete_discovery_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = Fixture(root)
            protocol, attestation_path, _ = public_protocol(root, fixture.policy, "0" * 64)
            with self.assertRaisesRegex(ValueError, "invocation contract"):
                fixture.config(attestation_path, protocol)

    def test_detached_head_is_pinned_even_when_ref_tips_do_not_move(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            result = fixture.config()
            research = next(row for row in result["sources"] if row["kind"] == "git_history")
            old = research["head_commit"]
            (fixture.research / "second").write_text("second\n")
            run_git(fixture.research, "add", ".")
            run_git(fixture.research, "commit", "-qm", "second")
            new = run_git(fixture.research, "rev-parse", "HEAD")
            run_git(fixture.research, "checkout", "-q", old)
            detached = snapshot.repo_record(
                fixture.research,
                fixture.projects,
                {"decision": "INCLUDE_SEMANTIC", "policy_rule_id": "research", "purpose": "RESEARCH"},
            )
            self.assertEqual(detached["head_commit"], old)
            run_git(fixture.research, "checkout", "-q", new)
            replay = {
                "schema_version": snapshot.CONFIG_SCHEMA,
                "prototype_only": False,
                "complete": True,
                "sources": [detached],
            }
            replay["sources_config_sha256"] = snapshot.content_address(
                replay, "sources_config_sha256"
            )
            with self.assertRaisesRegex(ValueError, "Git source drifted"):
                snapshot.verify_config_sources(replay)

    def test_prototype_config_can_never_be_acquired_as_s0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = Fixture(root)
            contract_sha = snapshot.discovery_contract_sha256(
                fixture.projects, fixture.ai_chats, fixture.mirrors, [f"project={fixture.release}"]
            )
            protocol, attestation_path, _ = public_protocol(root, fixture.policy, contract_sha)
            config_path = root / "prototype.json"
            config_path.write_text(snapshot.pretty_json(fixture.config()), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-prototype"):
                snapshot.acquire_s0(
                    config_path,
                    fixture.policy,
                    attestation_path,
                    protocol,
                    "2026-08-13T10:00:01Z",
                )


if __name__ == "__main__":
    unittest.main()
