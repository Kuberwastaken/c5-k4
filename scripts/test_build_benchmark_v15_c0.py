#!/usr/bin/env python3
"""Adversarial tests for the target-blind Method v1.5 C0 bridge."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("build_benchmark_v15_c0.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v15_c0_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
C0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C0)

POOL_TEST_SCRIPT = Path(__file__).with_name("test_build_benchmark_v15_pass_pool.py")
POOL_SPEC = importlib.util.spec_from_file_location("benchmark_v15_pool_fixture", POOL_TEST_SCRIPT)
assert POOL_SPEC is not None and POOL_SPEC.loader is not None
PT = importlib.util.module_from_spec(POOL_SPEC)
POOL_SPEC.loader.exec_module(PT)


class C0BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = PT.PassPoolTests("test_builds_complete_target_blind_embeddable_pool")
        self.fixture.setUp()
        self.pool = self.fixture.build()
        self.source_root = C0.ROOT
        self.temp = tempfile.TemporaryDirectory(prefix="v15-c0-test-")
        self.root = Path(self.temp.name) / "repository"
        workflow_source = self.source_root / ".github/workflows/method-v15-c0a-publication-observer.yml"
        workflow_target = self.root / ".github/workflows/method-v15-c0a-publication-observer.yml"
        workflow_target.parent.mkdir(parents=True)
        workflow_target.write_bytes(workflow_source.read_bytes())
        self.root_patch = mock.patch.object(C0, "ROOT", self.root)
        self.root_patch.start()
        self.pool_path = self.root / "results/benchmark/fixture-pool.json"
        self.pool_path.parent.mkdir(parents=True)
        self.pool_path.write_bytes(C0.canonical_json(self.pool))
        self.c0a_path = C0.ROOT / C0.C0A_PATH
        self.c0t_path = C0.ROOT / C0.C0T_PATH
        self.workflow_path = ".github/workflows/method-v15-c0a-publication-observer.yml"
        self.c0a_path.parent.mkdir(parents=True)
        self.sources = {
            name: self.root / f"unused-{name}.json" for name in (
                "private_registry", "aggregate_certificate", "replay_attestation", "pass_receipt",
                "prior_public_chain_proof", "pass_public_chain_proof", "p1a", "p1t",
            )
        }
        # A round safely beyond all fixture observations.
        self.round = ((int(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp()) - C0.LEGACY_GENESIS) // 30) + 1
        self.c0a_commit = "d" * 40
        self.c0t_commit = "e" * 40
        self.run_id = 456789
        self.p1_activation = {
            "p1r": {"path": C0.P1R_PATH, "sha256": "a" * 64},
            "p1r_commit": "b" * 40,
            "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
        }

    def tearDown(self) -> None:
        self.root_patch.stop()
        self.temp.cleanup()
        self.fixture.tearDown()

    def build_c0a(self) -> dict:
        with mock.patch.object(C0.pass_pool, "build_pool", return_value=copy.deepcopy(self.pool)) as replay:
            value = C0.assemble_c0a(
                self.pool_path, source_paths=self.sources, public_repository=self.root,
                future_drand_round=self.round,
                c0a_path=self.c0a_path.relative_to(C0.ROOT).as_posix(),
                c0t_path=self.c0t_path.relative_to(C0.ROOT).as_posix(),
                workflow_path=self.workflow_path,
                activation_verifier=self.activation_stub,
            )
        replay.assert_called_once()
        return value

    def activation_stub(self, pool: dict) -> dict:
        # Strict unit boundary for topology/observer tests. Production exposes
        # no CLI switch that can install this stand-in.
        if pool.get("pool_sha256") != self.pool["pool_sha256"]:
            raise C0.C0Error("fixture P1R verifier received a different pool")
        return copy.deepcopy(self.p1_activation)

    def install_c0a(self) -> dict:
        value = self.build_c0a()
        self.c0a_path.write_bytes(C0.canonical_json(value))
        return value

    def run_object(self, **updates) -> bytes:
        value = {
            "id": self.run_id, "run_attempt": 1, "event": "push", "status": "completed", "conclusion": "success",
            "head_sha": self.c0a_commit, "head_branch": C0.PUBLICATION_BRANCH,
            "path": self.workflow_path + "@refs/heads/method-v1.5-c0",
            "url": f"https://api.github.com/repos/{C0.REPOSITORY_SLUG}/actions/runs/{self.run_id}",
            "html_url": f"https://github.com/{C0.REPOSITORY_SLUG}/actions/runs/{self.run_id}",
            "created_at": "2026-08-20T00:00:00Z",
            "run_started_at": "2026-08-20T00:00:00Z", "updated_at": "2026-08-20T00:01:00Z",
            "repository": {"full_name": C0.REPOSITORY_SLUG},
        }
        value.update(updates)
        return json.dumps(value, sort_keys=True).encode()

    def committed_file(self, c0a: dict, commit: str, path: str) -> bytes:
        if commit != self.c0a_commit:
            raise AssertionError((commit, path))
        if path == c0a["publication_topology"]["c0a_path"]:
            return self.c0a_path.read_bytes()
        if path == self.workflow_path:
            return (C0.ROOT / self.workflow_path).read_bytes()
        raise AssertionError((commit, path))

    def c0a_git(self, c0a: dict):
        return (
            mock.patch.object(C0, "parents", return_value=[self.pool["public_chain"]["pass_publication_commit"]]),
            mock.patch.object(C0, "changed_paths", return_value=[c0a["publication_topology"]["c0a_path"]]),
            mock.patch.object(C0, "commit_file", side_effect=lambda commit, path: self.committed_file(c0a, commit, path)),
        )

    def build_c0t(self, raw: bytes | None = None) -> tuple[dict, bytes, dict]:
        c0a = self.install_c0a()
        raw = self.run_object() if raw is None else raw
        parent_patch, paths_patch, file_patch = self.c0a_git(c0a)
        with parent_patch, paths_patch, file_patch:
            value = C0.assemble_c0t(
                self.c0a_path, self.c0a_commit, self.run_id,
                api_fetch=lambda _url: raw, activation_verifier=self.activation_stub,
            )
        return value, raw, c0a

    def test_c0a_reauthenticates_and_embeds_exact_pool_without_authority_claim(self) -> None:
        value = self.build_c0a()
        self.assertEqual(value["pass_pool"], self.pool)
        self.assertEqual(value["authority"], "NO_LIVE_C0_AUTHORITY_CLAIMED")
        self.assertEqual(value["status"], "AWAITING_C0_PUBLICATION_ATTESTATION")
        self.assertEqual(
            value["publication_topology"]["terminal_u2_commit"],
            self.pool["public_chain"]["pass_publication_commit"],
        )
        self.assertFalse(value["randomness_contract"]["entropy_used"])
        self.assertIsNone(value["randomness_contract"]["value"])

    def test_c0a_rejects_pool_not_identical_to_source_replay(self) -> None:
        altered = copy.deepcopy(self.pool)
        altered["clusters"][0]["cluster_id"] += "-changed"
        altered["pool_sha256"] = C0.pass_pool.pool_digest(altered)
        self.pool_path.write_bytes(C0.canonical_json(altered))
        with mock.patch.object(C0.pass_pool, "build_pool", return_value=self.pool):
            with self.assertRaisesRegex(C0.C0Error, "reauthenticated canonical object"):
                C0.assemble_c0a(
                    self.pool_path, source_paths=self.sources, public_repository=self.root,
                    future_drand_round=self.round,
                    c0a_path=self.c0a_path.relative_to(C0.ROOT).as_posix(),
                    c0t_path=self.c0t_path.relative_to(C0.ROOT).as_posix(),
                    workflow_path=self.workflow_path,
                    activation_verifier=self.activation_stub,
                )

    def test_c0a_fails_closed_when_upstream_p1_or_pool_reauthentication_fails(self) -> None:
        with mock.patch.object(C0.pass_pool, "build_pool", side_effect=C0.pass_pool.PassPoolError("P1 activation absent")):
            with self.assertRaisesRegex(C0.C0Error, "P1 activation absent"):
                C0.assemble_c0a(
                    self.pool_path, source_paths=self.sources, public_repository=self.root,
                    future_drand_round=self.round,
                    c0a_path=self.c0a_path.relative_to(C0.ROOT).as_posix(),
                    c0t_path=self.c0t_path.relative_to(C0.ROOT).as_posix(), workflow_path=self.workflow_path,
                    activation_verifier=self.activation_stub,
                )

    def test_c0a_rejects_missing_boolean_or_p1t_only_activation(self) -> None:
        cases = (
            (None, "bare P1A/P1T"),
            (True, "caller booleans"),
            (lambda _pool: {"p1t_commit": "1" * 40}, "exact frozen binding"),
        )
        for verifier, message in cases:
            with self.subTest(message=message), \
                 mock.patch.object(C0.pass_pool, "build_pool", return_value=copy.deepcopy(self.pool)):
                with self.assertRaisesRegex(C0.C0Error, message):
                    C0.assemble_c0a(
                        self.pool_path, source_paths=self.sources, public_repository=self.root,
                        future_drand_round=self.round,
                        c0a_path=self.c0a_path.relative_to(C0.ROOT).as_posix(),
                        c0t_path=self.c0t_path.relative_to(C0.ROOT).as_posix(),
                        workflow_path=self.workflow_path,
                        activation_verifier=verifier,  # type: ignore[arg-type]
                    )

    def test_c0a_rejects_target_semantics_entropy_or_selection(self) -> None:
        for key, payload in (
            ("target_semantics", ["forbidden"]), ("entropy", "00" * 32), ("selected_clusters", ["c1"]),
        ):
            value = self.build_c0a()
            value[key] = payload
            value["artifact_sha256"] = C0.artifact_digest(value)
            with self.assertRaises(C0.C0Error):
                C0.validate_c0a(value)

    def test_c0a_commit_must_be_sole_child_and_one_path(self) -> None:
        c0a = self.install_c0a()
        with mock.patch.object(C0, "parents", return_value=["1" * 40, "2" * 40]), \
             mock.patch.object(C0, "changed_paths", return_value=[c0a["publication_topology"]["c0a_path"]]):
            with self.assertRaisesRegex(C0.C0Error, "direct nonmerge child"):
                C0.validate_c0a_commit(c0a, self.c0a_commit, self.c0a_path)
        with mock.patch.object(C0, "parents", return_value=[self.pool["public_chain"]["pass_publication_commit"]]), \
             mock.patch.object(C0, "changed_paths", return_value=["extra", c0a["publication_topology"]["c0a_path"]]):
            with self.assertRaisesRegex(C0.C0Error, "exactly its one frozen path"):
                C0.validate_c0a_commit(c0a, self.c0a_commit, self.c0a_path)

    def test_legacy_builder_cannot_mint_or_accept_c0t(self) -> None:
        with self.assertRaisesRegex(C0.C0Error, "strict repository/run-list/rules/ancestry adapter"):
            C0.assemble_c0t(
                self.c0a_path, self.c0a_commit, self.run_id,
                api_fetch=lambda _url: self.run_object(), activation_verifier=self.activation_stub,
            )
        with self.assertRaisesRegex(C0.C0Error, "commit-optional C0T validation is forbidden"):
            C0.validate_c0t({}, c0t_commit=self.c0t_commit, artifact_path=self.c0t_path)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        duplicate_c0a = b'{"schema":"x","schema":"x"}\n'
        self.c0a_path.write_bytes(duplicate_c0a)
        with self.assertRaisesRegex(C0.C0Error, "duplicate JSON key"):
            C0.load_json(self.c0a_path, "duplicate C0A")

    def test_contract_requires_exact_embedded_pool_and_one_path_bridge(self) -> None:
        contract = json.loads((self.source_root / "results/benchmark/v1.5-protocol/c0-publication-contract.json").read_text())
        self.assertTrue(contract["pass_pool_gate"]["canonical_object_sha256_required"])
        self.assertEqual(contract["publication_topology"]["c0a_change"], "ADD_EXACTLY_ONE_C0A_PATH")
        self.assertEqual(contract["publication_topology"]["c0t_change"], "ADD_EXACTLY_ONE_C0T_PATH")
        self.assertFalse(contract["publication_observation"]["caller_supplied_timestamp_is_authority"])


if __name__ == "__main__":
    unittest.main()
