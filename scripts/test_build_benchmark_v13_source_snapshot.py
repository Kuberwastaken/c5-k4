#!/usr/bin/env python3
"""Tests for semantics-blind Method v1.3 source discovery and S0 acquisition."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_v13_source_snapshot as snapshot


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
                            "source_kind": "git_history",
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

    def config(
        self,
        attestation: Path | None = None,
        protocol_repo: Path | None = None,
        p0t_commit: str | None = None,
        public_remote_url: str | None = None,
    ) -> dict:
        return snapshot.build_config(
            self.projects,
            self.policy,
            self.ai_chats,
            self.mirrors,
            [f"project={self.release}"],
            attestation,
            p0t_commit,
            public_remote_url,
            protocol_repo or self.research,
        )

    def contract_raw(self) -> bytes:
        return snapshot.discovery_contract_bytes(
            self.projects,
            self.ai_chats,
            self.mirrors,
            [f"project={self.release}"],
        )


def public_protocol(root: Path, policy: Path, contract_raw: bytes) -> tuple[Path, Path, str, str]:
    repo = root / "protocol"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    run_git(repo, "config", "user.name", "Test")
    run_git(repo, "config", "user.email", "test@example.com")
    policy_target = repo / "source-policy.json"
    policy_target.write_bytes(policy.read_bytes())
    contract_target = repo / "source-contract.json"
    # Its exact file digest is the frozen invocation-contract digest.
    contract_target.write_bytes(contract_raw)
    p0a_artifact = repo / "p0a.json"
    p0a_value = {
        "schema_version": snapshot.P0_SCHEMA,
        "artifact_kind": "P0A",
        "components": {
            "source_path_policy": {"path": "source-policy.json", "sha256": snapshot.sha256(policy_target.read_bytes())},
            "source_discovery_contract": {"path": "source-contract.json", "sha256": snapshot.sha256(contract_target.read_bytes())},
        },
    }
    p0a_artifact.write_text(snapshot.pretty_json(p0a_value), encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-qm", "freeze protocol")
    p0a = run_git(repo, "rev-parse", "HEAD")
    p0t_path = repo / "p0t.json"
    attestation = {
        "schema_version": snapshot.P0_SCHEMA,
        "artifact_kind": "P0T",
        "protocol_version": "1.3",
        "p0a": {"path": "p0a.json", "sha256": snapshot.sha256(p0a_artifact.read_bytes())},
        "p0a_commit": p0a,
        "p0a_published_at_utc": "2026-08-13T10:00:00Z",
        "attestation_policy": {
            "p0a_ancestor_required": True,
            "p0a_bytes_immutable": True,
            "allowed_p0t_changed_paths": ["p0t.json"],
        },
    }
    p0t_path.write_text(snapshot.pretty_json(attestation), encoding="utf-8")
    run_git(repo, "add", "p0t.json")
    run_git(repo, "commit", "-qm", "attest protocol")
    p0t = run_git(repo, "rev-parse", "HEAD")
    remote = root / "public.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    run_git(repo, "remote", "add", "public", str(remote))
    run_git(repo, "push", "-q", "public", "HEAD:refs/heads/main")
    return repo, p0t_path, p0t, str(remote)


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
                None,
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

    def test_unknown_nongit_directory_is_discovered_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            unknown = fixture.projects / "mystery-tree"
            unknown.mkdir()
            (unknown / "note.txt").write_text("must not vanish\n")
            result = fixture.config()
            rows = [row for row in result["nonresearch_exclusions"] if row["relative_path"] == "mystery-tree"]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["decision"], "EXCLUDE_UNKNOWN")
            self.assertFalse(result["complete"])

    def test_dirty_research_worktree_is_content_addressed_not_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            tracked = fixture.research / "README"
            tracked.write_text("staged bytes\n", encoding="utf-8")
            run_git(fixture.research, "add", "README")
            tracked.write_text("unstaged bytes\n", encoding="utf-8")
            untracked = fixture.research / "new.bin"
            untracked.write_bytes(b"\x00\x01untracked")
            result = fixture.config()
            self.assertTrue(result["complete"])
            source = next(row for row in result["sources"] if row["kind"] == "git_history")
            entries = source["worktree_overlay"]["entries"]
            self.assertEqual(
                [(row["relative_path"], row["layer"]) for row in entries],
                [("README", "INDEX"), ("README", "WORKTREE"), ("new.bin", "WORKTREE")],
            )
            staged, unstaged, binary = entries
            self.assertEqual(staged["selector"]["kind"], "git_blob")
            self.assertEqual(staged["sha256"], snapshot.sha256(b"staged bytes\n"))
            self.assertEqual(unstaged["sha256"], snapshot.sha256(b"unstaged bytes\n"))
            self.assertEqual(binary["byte_count"], len(b"\x00\x01untracked"))
            self.assertEqual(
                source["worktree_overlay"]["inventory_sha256"],
                snapshot.sha256(snapshot.canonical_json(entries)),
            )

    def test_s0_rejects_index_and_worktree_overlay_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            (fixture.research / "README").write_text("frozen staged\n")
            run_git(fixture.research, "add", "README")
            (fixture.research / "new.txt").write_text("frozen untracked\n")
            protocol, attestation_path, p0t, remote = public_protocol(
                Path(directory), fixture.policy, fixture.contract_raw()
            )
            config = fixture.config(attestation_path, protocol, p0t, remote)
            config_path = Path(directory) / "sources-dirty.json"
            config_path.write_text(snapshot.pretty_json(config), encoding="utf-8")
            snapshot.acquire_s0(
                config_path,
                fixture.policy,
                attestation_path,
                protocol,
                p0t,
                remote,
                "2026-08-13T10:00:01Z",
            )
            (fixture.research / "new.txt").write_text("drift\n")
            with self.assertRaisesRegex(ValueError, "overlay inventory drifted"):
                snapshot.acquire_s0(
                    config_path,
                    fixture.policy,
                    attestation_path,
                    protocol,
                    p0t,
                    remote,
                    "2026-08-13T10:00:02Z",
                )

    def test_staged_and_worktree_deletions_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            (fixture.research / "staged-delete").write_text("gone from index\n")
            (fixture.research / "worktree-delete").write_text("gone from worktree\n")
            run_git(fixture.research, "add", ".")
            run_git(fixture.research, "commit", "-qm", "deletion fixtures")
            (fixture.research / "staged-delete").unlink()
            run_git(fixture.research, "add", "staged-delete")
            (fixture.research / "worktree-delete").unlink()
            source = snapshot.repo_record(
                fixture.research,
                fixture.projects,
                {"decision": "INCLUDE_SEMANTIC", "policy_rule_id": "research", "purpose": "RESEARCH", "source_kind": "git_history"},
            )
            entries = source["worktree_overlay"]["entries"]
            self.assertEqual(
                [(row["relative_path"], row["layer"], row["state"]) for row in entries],
                [
                    ("staged-delete", "INDEX", "DELETED"),
                    ("worktree-delete", "WORKTREE", "DELETED"),
                ],
            )
            self.assertTrue(all(row["sha256"] == snapshot.sha256(b"") for row in entries))

    def test_unsynced_local_session_mirror_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            (fixture.codex / "session.jsonl").write_text("changed\n")
            result = fixture.config()
            self.assertFalse(result["complete"])
            sessions = next(row for row in result["sources"] if row["kind"] == "git_sessions")
            self.assertFalse(sessions["complete"])

    def test_local_session_retention_may_be_subset_of_complete_archive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = Fixture(Path(directory))
            archived = fixture.ai_chats / "codex" / "archived.jsonl"
            archived.write_text('{"old":"archived"}\n')
            run_git(fixture.ai_chats, "add", ".")
            run_git(fixture.ai_chats, "commit", "-qm", "older archived session")
            result = fixture.config()
            self.assertTrue(result["complete"])
            sessions = next(row for row in result["sources"] if row["kind"] == "git_sessions")
            codex = next(row for row in sessions["session_mirrors"] if row["id"] == "codex")
            self.assertEqual(codex["unit_count"], 1)
            self.assertEqual(codex["archived_unit_count"], 2)
            self.assertTrue(codex["mirror_agrees"])

    def test_unversioned_tree_is_content_addressed_and_ignores_build_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tree = root / "scratch"
            tree.mkdir()
            (tree / "research.txt").write_text("current research\n")
            cache = tree / "node_modules"
            cache.mkdir()
            (cache / "ignored.txt").write_text("cache\n")
            classification = {
                "decision": "INCLUDE_SEMANTIC",
                "policy_rule_id": "tree",
                "purpose": "UNVERSIONED_RESEARCH_TREE",
                "source_kind": "tree",
            }
            record = snapshot.tree_record(tree, root, classification)
            self.assertEqual(
                [row["relative_path"] for row in record["tree_snapshot"]["entries"]],
                ["research.txt"],
            )
            (tree / "research.txt").write_text("drift\n")
            with self.assertRaisesRegex(ValueError, "unversioned tree drifted"):
                config = {
                    "schema_version": snapshot.CONFIG_SCHEMA,
                    "prototype_only": False,
                    "complete": True,
                    "projects_root": str(root),
                    "sources": [record],
                }
                config["sources_config_sha256"] = snapshot.content_address(
                    config, "sources_config_sha256"
                )
                snapshot.verify_config_sources(config)

    def test_formal_registry_records_only_user_delta_as_semantic_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            projects = root / "projects"
            repo = make_repo(projects / "formal-conjectures", {"registry.lean": "upstream\n"})
            upstream = run_git(repo, "rev-parse", "HEAD")
            run_git(repo, "update-ref", "refs/remotes/upstream/main", upstream)
            (repo / "user-note.txt").write_text("user work\n")
            run_git(repo, "add", ".")
            run_git(repo, "commit", "-qm", "user research")
            (repo / "current.txt").write_text("uncommitted\n")
            classification = {
                "decision": "INCLUDE_SEMANTIC",
                "policy_rule_id": "upstream-registry-user-delta",
                "purpose": "USER_COMMITS_AND_CURRENT_TREE_EXCLUDING_UPSTREAM_BASE",
                "source_kind": "git_user_delta",
            }
            record = snapshot.git_user_delta_record(repo, projects, classification)
            self.assertEqual(record["upstream_base_refs"][0]["object_id"], upstream)
            self.assertNotIn(upstream, record["user_commit_ids"])
            self.assertEqual(len(record["user_commit_ids"]), 1)
            self.assertEqual(
                [row["relative_path"] for row in record["worktree_overlay"]["entries"]],
                ["current.txt"],
            )

    def test_policy_classifies_frozen_project_directory_fixture(self) -> None:
        policy_path = Path(__file__).resolve().parents[1] / "results/benchmark/v1.3-protocol/source-path-purpose-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        snapshot.validate_policy(policy)
        names = (
            "c5-k4",
            "formal-conjectures",
            "marketing-outbound",
            "permanental-dominance-n4",
            "reimann",
            "scratch",
            "subagentmaxxing",
        )
        decisions = {name: snapshot.classify_path(name, policy) for name in names}
        self.assertFalse([name for name, row in decisions.items() if row["decision"] == "EXCLUDE_UNKNOWN"])
        for name in ("reimann", "subagentmaxxing"):
            self.assertEqual(decisions[name]["decision"], "INCLUDE_SEMANTIC")
            self.assertEqual(decisions[name]["source_kind"], "git_history")
        self.assertEqual(decisions["formal-conjectures"]["source_kind"], "git_user_delta")
        for name in ("permanental-dominance-n4", "scratch"):
            self.assertEqual(decisions[name]["source_kind"], "tree")

    def test_authoritative_discovery_contract_is_exact_invocation_bytes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        contract = root / "results/benchmark/v1.3-protocol/source-discovery-contract.json"
        expected = snapshot.discovery_contract_bytes(
            Path("/Users/kuber.mehta/Projects"),
            Path("/home/ec2-user/.local/share/c5k4-v13-ai-chats-snapshot"),
            [
                "claude-local=claude:/home/ec2-user/.local/share/c5k4-v13-session-snapshot/claude:claude",
                "codex-local=codex:/home/ec2-user/.local/share/c5k4-v13-session-snapshot/codex:codex",
            ],
            [
                "c5-k4-github=/Users/kuber.mehta/Projects/c5-k4/"
                "results/benchmark/v1.3-s0/c5-k4-github-releases.json"
            ],
        )
        self.assertEqual(contract.read_bytes(), expected)

    def test_s0_requires_public_p0_and_rechecks_every_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = Fixture(root)
            protocol, attestation_path, p0t, remote = public_protocol(
                root, fixture.policy, fixture.contract_raw()
            )
            config = fixture.config(attestation_path, protocol, p0t, remote)
            self.assertEqual(config["schema_version"], snapshot.CONFIG_SCHEMA)
            self.assertFalse(config["prototype_only"])
            config_path = root / "sources.json"
            config_path.write_text(snapshot.pretty_json(config), encoding="utf-8")
            s0 = snapshot.acquire_s0(
                config_path,
                fixture.policy,
                attestation_path,
                protocol,
                p0t,
                remote,
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
                    p0t,
                    remote,
                    "2026-08-13T10:00:02Z",
                )

    def test_public_p0_freezes_complete_discovery_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = Fixture(root)
            protocol, attestation_path, p0t, remote = public_protocol(
                root, fixture.policy, b"wrong contract\n"
            )
            with self.assertRaisesRegex(ValueError, "source_discovery_contract"):
                fixture.config(attestation_path, protocol, p0t, remote)

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
                {"decision": "INCLUDE_SEMANTIC", "policy_rule_id": "research", "purpose": "RESEARCH", "source_kind": "git_history"},
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
            protocol, attestation_path, p0t, remote = public_protocol(
                root, fixture.policy, fixture.contract_raw()
            )
            config_path = root / "prototype.json"
            config_path.write_text(snapshot.pretty_json(fixture.config()), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-prototype"):
                snapshot.acquire_s0(
                    config_path,
                    fixture.policy,
                    attestation_path,
                    protocol,
                    p0t,
                    remote,
                    "2026-08-13T10:00:01Z",
                )


if __name__ == "__main__":
    unittest.main()
