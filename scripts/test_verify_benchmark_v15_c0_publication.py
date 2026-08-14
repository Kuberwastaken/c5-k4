#!/usr/bin/env python3
"""Adversarial tests for the Method v1.5 public C0 observer chain."""

from __future__ import annotations

import copy
import importlib.util
import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("verify_benchmark_v15_c0_publication.py")
SPEC = importlib.util.spec_from_file_location("v15_c0_publication_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class PublicC0Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.c0a_commit = "a" * 40
        self.parent = "b" * 40
        self.run_id = 87654321
        self.receipt = {
            "schema": "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
            "p1r": {"path": "results/benchmark/v1.5-protocol/P1R.json", "sha256": "1" * 64},
            "p1r_commit": "2" * 40, "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
            "public_observation": {
                "workflow_repository": "Kuberwastaken/c5-k4",
                "workflow_path": ".github/workflows/method-v15-p1r-publication-observer.yml",
                "workflow_blob_sha256": "3" * 64,
                "workflow_ref": ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r",
                "run_id": 1, "run_attempt": 1, "server_observed_at_utc": "2026-08-01T00:00:00Z",
                "actions_run_projection_sha256": "4" * 64,
            },
            "validation_inputs_sha256": "5" * 64, "validation_diagnostic_sha256": "6" * 64,
            "validator": {"path": "scripts/validate_benchmark_v15_candidate_base.py", "sha256": "7" * 64},
        }
        self.receipt["receipt_sha256"] = V.domain_digest(
            "c5k4-method-v1.5-public-p1r-activation-receipt-1.0", V.without(self.receipt, "receipt_sha256")
        )
        self.receipt_raw = V.canonical_json(self.receipt)
        self.c0a_raw = b'{"committed":"c0a"}\n'
        self.c0a = {
            "p1_activation": {key: copy.deepcopy(self.receipt[key]) for key in ("p1r", "p1r_commit", "activation_boundary")},
            "pass_pool": {
                "p1_binding": {
                    "p1r": copy.deepcopy(self.receipt["p1r"]), "p1r_commit": self.receipt["p1r_commit"],
                    "p1r_activation_sha256": V.sha256(self.receipt_raw),
                },
                "upstream": {"u1_commit": "8" * 40, "u1_tree": "9" * 40, "u2_commit": "c" * 40, "u2_tree": "d" * 40},
                "public_chain": {"pass_publication_commit": self.parent},
            },
            "pass_pool_binding": {"pool_sha256": "e" * 64, "canonical_object_sha256": "f" * 64},
            "workflow_binding": {"path": V.WORKFLOW_PATH, "sha256": "0" * 64},
            "randomness_contract": {
                "source": "League of Entropy drand", "chain_hash": V.bridge.LEGACY_CHAIN_HASH,
                "round": 6400000, "round_closes_at_utc": "2026-09-01T00:00:00Z",
                "value": None, "entropy_used": False, "selection_performed": False,
            },
            "publication_topology": {
                "repository": "https://github.com/Kuberwastaken/c5-k4", "ref": V.REF,
                "terminal_u2_commit": self.parent, "c0a_path": V.C0A_PATH, "c0t_path": V.C0T_PATH,
                "c0a_change": "ADD_EXACTLY_ONE_C0A_PATH", "c0t_change": "ADD_EXACTLY_ONE_C0T_PATH",
                "merge_commits_permitted": False,
            },
            "publication_boundary": {
                "target_blind": True, "entropy_present": False, "selection_present": False,
                "ranking_present": False, "statement_text_present": False,
                "target_semantics_present": False, "outcomes_present": False,
            },
        }
        self.c0a["pass_pool"]["pool_sha256"] = "e" * 64
        self.c0a["pass_pool_binding"]["canonical_object_sha256"] = V.sha256(V.canonical_json(self.c0a["pass_pool"]))

    def run_raw(self, **updates: object) -> bytes:
        value = {
            "id": self.run_id, "run_attempt": 1, "event": "push", "status": "completed",
            "conclusion": "success", "head_sha": self.c0a_commit, "head_branch": V.BRANCH,
            "url": f"https://api.github.com/repos/{V.REPOSITORY}/actions/runs/{self.run_id}",
            "html_url": f"https://github.com/{V.REPOSITORY}/actions/runs/{self.run_id}",
            "path": V.WORKFLOW_REF, "created_at": "2026-08-20T00:00:00Z",
            "run_started_at": "2026-08-20T00:00:01Z", "updated_at": "2026-08-20T00:01:00Z",
            "repository": {"id": V.REPOSITORY_ID, "node_id": V.REPOSITORY_NODE_ID, "full_name": V.REPOSITORY},
        }
        value.update(updates)
        return json.dumps(value, sort_keys=True).encode()

    def loaded(self, *_args: object, **_kwargs: object):
        return copy.deepcopy(self.c0a), self.c0a_raw, copy.deepcopy(self.receipt), self.receipt_raw

    def fetcher(
        self, run_raw: bytes | None = None, *, ref_tip: str | None = None,
        duplicate_run: bool = False, repository_id: int | None = None,
        rules: list[dict] | None = None, comparison_updates: dict | None = None,
    ):
        def fetch(url: str) -> bytes:
            if "/actions/runs/" in url:
                return run_raw or self.run_raw()
            if "/actions/workflows/" in url:
                row = json.loads((run_raw or self.run_raw()).decode())
                other = {**row, "id": row["id"] + 1}
                runs = [row, other] if duplicate_run else [row]
                return json.dumps({"total_count": len(runs), "workflow_runs": runs}).encode()
            if "/git/ref/heads/" in url:
                return json.dumps({"ref": V.REF, "object": {"type": "commit", "sha": ref_tip or self.c0a_commit}}).encode()
            if "/rules/branches/" in url:
                return json.dumps(rules if rules is not None else [{"type": "deletion"}, {"type": "non_fast_forward"}]).encode()
            if "/compare/" in url:
                tip = ref_tip or self.c0a_commit
                commits = [self.c0a_commit] if tip == self.c0a_commit else [self.c0a_commit, tip]
                value = {
                    "status": "ahead", "ahead_by": len(commits), "behind_by": 0,
                    "total_commits": len(commits), "base_commit": {"sha": self.parent},
                    "merge_base_commit": {"sha": self.parent},
                    "commits": [{"sha": commit} for commit in commits],
                }
                value.update(comparison_updates or {})
                return json.dumps(value).encode()
            if url == f"https://api.github.com/repos/{V.REPOSITORY}":
                return json.dumps({
                    "id": repository_id if repository_id is not None else V.REPOSITORY_ID,
                    "node_id": V.REPOSITORY_NODE_ID, "full_name": V.REPOSITORY, "private": False,
                }).encode()
            raise AssertionError(url)
        return fetch

    def compile_observation(self, raw: bytes | None = None) -> dict:
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw)):
            return V.compile_observation(
                self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
            )

    def test_compiler_binds_p1r_u1_u2_pass_pool_commit_run_and_server_times(self) -> None:
        value = self.compile_observation()
        self.assertEqual(value["chronology"]["p1r_commit"], self.receipt["p1r_commit"])
        self.assertEqual(value["chronology"]["u1_commit"], self.c0a["pass_pool"]["upstream"]["u1_commit"])
        self.assertEqual(value["chronology"]["u2_commit"], self.c0a["pass_pool"]["upstream"]["u2_commit"])
        self.assertEqual(value["chronology"]["c0a_parent_commit"], self.parent)
        self.assertEqual(value["github_run"]["head_sha"], self.c0a_commit)
        self.assertEqual(value["github_run"]["run_attempt"], 1)
        self.assertEqual(value["api_contract"]["version"], V.GITHUB_API_VERSION)
        self.assertEqual(value["repository_identity"]["id"], V.REPOSITORY_ID)
        self.assertTrue(value["server_evidence"]["no_force_push"])
        self.assertTrue(value["server_evidence"]["no_delete"])
        self.assertEqual(value["receipt_sha256"], V.observation_digest(value))

    def test_wrong_head_attempt_workflow_or_repository_fails_closed(self) -> None:
        cases = (
            self.run_raw(head_sha="f" * 40), self.run_raw(run_attempt=2),
            self.run_raw(path=".github/workflows/other.yml"), self.run_raw(repository={"full_name": "fork/c5-k4"}),
        )
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(V.PublicationError):
                self.compile_observation(raw)

    def test_incomplete_failed_or_late_run_cannot_mint_observation(self) -> None:
        cases = (
            self.run_raw(status="in_progress", conclusion=None), self.run_raw(conclusion="failure"),
            self.run_raw(updated_at="2026-09-01T00:00:00Z"),
            self.run_raw(created_at="2026-08-20T00:02:00Z"),
        )
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(V.PublicationError):
                self.compile_observation(raw)

    def test_run_must_be_unique_first_success_and_public_ref_must_be_exact(self) -> None:
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(duplicate_run=True)):
            with self.assertRaisesRegex(V.PublicationError, "one unique"):
                V.compile_observation(
                    self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
                )
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(ref_tip="f" * 40)):
            with self.assertRaisesRegex(V.PublicationError, "rewritten"):
                V.compile_observation(
                    self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
                )

    def test_exact_head_query_exhausts_all_pages_and_has_no_day_scope(self) -> None:
        seen: list[str] = []
        row = json.loads(self.run_raw().decode())
        page_one = [{**row, "id": index + 1} for index in range(100)]
        page_two: list[dict] = []
        def fetch(url: str) -> bytes:
            seen.append(url)
            page = 2 if "page=2" in url else 1
            return json.dumps({"total_count": 100, "workflow_runs": page_two if page == 2 else page_one}).encode()
        with self.assertRaisesRegex(V.PublicationError, "one unique"):
            V._exhaustive_run_listing(fetch, c0a_commit=self.c0a_commit, run_id=self.run_id)
        self.assertEqual(len(seen), 2)
        self.assertTrue(all(f"head_sha={self.c0a_commit}" in url for url in seen))
        self.assertTrue(all("created=" not in url and "branch=" not in url for url in seen))

    def test_repository_identity_protection_and_compare_ancestry_fail_closed(self) -> None:
        cases = (
            (self.fetcher(repository_id=1), "numeric/node identity"),
            (self.fetcher(rules=[{"type": "deletion"}]), "no-delete and no-force-push"),
            (self.fetcher(rules=[{"type": "non_fast_forward"}]), "no-delete and no-force-push"),
            (self.fetcher(comparison_updates={"merge_base_commit": {"sha": "0" * 40}}), "append-only"),
        )
        for fetch, message in cases:
            with self.subTest(message=message), mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
                 mock.patch.object(V, "live_fetch", side_effect=fetch), \
                 self.assertRaisesRegex(V.PublicationError, message):
                V.compile_observation(
                    self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
                )

    def test_projection_digests_and_api_version_are_receipt_bound(self) -> None:
        value = self.compile_observation()
        evidence = value["server_evidence"]
        for key in (
            "run_object_projection_sha256", "run_listing_projection_sha256",
            "repository_projection_sha256", "ref_projection_sha256",
            "protection_projection_sha256", "ancestry_projection_sha256",
        ):
            self.assertRegex(evidence[key], r"^[0-9a-f]{64}$")
        altered = copy.deepcopy(value)
        altered["api_contract"]["version"] = "2099-01-01"
        altered["receipt_sha256"] = V.observation_digest(altered)
        with self.assertRaises(V.PublicationError):
            V.validate_observation(altered)

    def test_live_fetch_requires_authentication_and_pins_api_headers(self) -> None:
        with mock.patch.dict(V.os.environ, {}, clear=True), self.assertRaisesRegex(V.PublicationError, "requires GITHUB_TOKEN"):
            V.live_fetch("https://api.github.com/repos/Kuberwastaken/c5-k4")
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b"{}"
        with mock.patch.dict(V.os.environ, {"GITHUB_TOKEN": "fixture-token"}, clear=True), \
             mock.patch.object(V.urllib.request, "urlopen", return_value=response) as opened:
            self.assertEqual(V.live_fetch("https://api.github.com/repos/Kuberwastaken/c5-k4"), b"{}")
        request = opened.call_args.args[0]
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(headers["accept"], V.GITHUB_ACCEPT)
        self.assertEqual(headers["x-github-api-version"], V.GITHUB_API_VERSION)
        self.assertEqual(headers["authorization"], "Bearer fixture-token")

    def test_caller_generated_endpoint_json_cannot_enter_authoritative_apis(self) -> None:
        for function in (V.compile_observation, V.compile_c0t, V.validate_c0t):
            parameters = inspect.signature(function).parameters
            self.assertNotIn("fetch", parameters)
            self.assertNotIn("run_json", parameters)
            self.assertNotIn("capture", parameters)
        validate_parameters = inspect.signature(V.validate_c0t).parameters
        self.assertIs(validate_parameters["c0t_commit"].default, inspect.Parameter.empty)
        self.assertIs(validate_parameters["artifact_path"].default, inspect.Parameter.empty)
        fabricated = self.fetcher()
        with self.assertRaises(TypeError):
            V.compile_c0t(
                self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
                fetch=fabricated,  # type: ignore[call-arg]
            )
        with self.assertRaises(TypeError):
            V.validate_c0t(
                {}, activation_receipt_path=Path("unused"), replay_input_path=Path("unused-replay"),
                c0t_commit="f" * 40, artifact_path=Path("unused-c0t"),
                fetch=fabricated,  # type: ignore[call-arg]
            )

    def test_duplicate_run_keys_and_caller_target_fields_are_rejected(self) -> None:
        duplicate = self.run_raw().replace(b'"event": "push"', b'"event": "push", "event": "push"')
        with self.assertRaisesRegex(V.PublicationError, "duplicate JSON key"):
            self.compile_observation(duplicate)
        value = self.compile_observation()
        value["selected_clusters"] = ["forbidden"]
        value["receipt_sha256"] = V.observation_digest(value)
        with self.assertRaises(V.PublicationError):
            V.validate_observation(value)

    def test_activation_receipt_requires_canonical_bytes_self_digest_and_pool_digest(self) -> None:
        V.validate_activation_receipt(self.receipt, self.receipt_raw, self.c0a["pass_pool"])
        altered = copy.deepcopy(self.receipt)
        altered["validation_inputs_sha256"] = "a" * 64
        with self.assertRaises(V.PublicationError):
            V.validate_activation_receipt(altered, V.canonical_json(altered), self.c0a["pass_pool"])
        with self.assertRaisesRegex(V.PublicationError, "canonical JSON"):
            V.validate_activation_receipt(self.receipt, json.dumps(self.receipt, indent=2).encode(), self.c0a["pass_pool"])

    def test_pass_pool_is_independently_recompiled_with_exact_committed_sources(self) -> None:
        bound = {"path": "scripts/build_benchmark_v15_pass_pool.py", "sha256": "a" * 64}
        replay = {
            "schema": "c5k4-method-v1.5-c0-pass-pool-replay-input-1.0", "protocol_version": "1.5",
            "producer": bound,
            **{name: {"path": f"results/benchmark/{name}.json", "sha256": "b" * 64} for name in (
                "private_registry", "aggregate_certificate", "replay_attestation", "pass_receipt",
                "prior_public_chain_proof", "pass_public_chain_proof", "p1a", "p1t", "p1r", "validation_input",
            )},
            "public_repository": ".",
        }
        raw = V.canonical_json(replay)
        with mock.patch.object(V, "load", return_value=(replay, raw)), \
             mock.patch.object(V, "commit_file", return_value=raw), \
             mock.patch.object(V, "repository_file", return_value=Path("exact")) as source, \
             mock.patch.object(V.bridge.pass_pool, "build_pool", return_value=copy.deepcopy(self.c0a["pass_pool"])) as build:
            V.replay_pass_pool(self.c0a, V.ROOT / V.PASS_POOL_REPLAY_INPUT_PATH)
        self.assertEqual(source.call_count, 11)
        build.assert_called_once()
        altered = copy.deepcopy(self.c0a["pass_pool"]); altered["unbound"] = True
        with mock.patch.object(V, "load", return_value=(replay, raw)), \
             mock.patch.object(V, "commit_file", return_value=raw), \
             mock.patch.object(V, "repository_file", return_value=Path("exact")), \
             mock.patch.object(V.bridge.pass_pool, "build_pool", return_value=altered), \
             self.assertRaisesRegex(V.PublicationError, "differs from embedded"):
            V.replay_pass_pool(self.c0a, V.ROOT / V.PASS_POOL_REPLAY_INPUT_PATH)

    def test_replay_manifest_cannot_substitute_the_frozen_pass_pool_producer(self) -> None:
        replay = {
            "schema": "c5k4-method-v1.5-c0-pass-pool-replay-input-1.0", "protocol_version": "1.5",
            "producer": {"path": "scripts/evil.py", "sha256": "a" * 64},
            **{name: {"path": f"results/benchmark/{name}.json", "sha256": "b" * 64} for name in (
                "private_registry", "aggregate_certificate", "replay_attestation", "pass_receipt",
                "prior_public_chain_proof", "pass_public_chain_proof", "p1a", "p1t", "p1r", "validation_input",
            )},
            "public_repository": ".",
        }
        with mock.patch.object(V, "load", return_value=(replay, V.canonical_json(replay))), \
             mock.patch.object(V, "commit_file", return_value=V.canonical_json(replay)), self.assertRaises(V.PublicationError):
            V.replay_pass_pool(self.c0a, V.ROOT / V.PASS_POOL_REPLAY_INPUT_PATH)

    def test_c0t_is_target_blind_and_live_replay_is_mandatory(self) -> None:
        raw = self.run_raw()
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw)):
            c0t = V.compile_c0t(
                self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
            )
        self.assertIsNone(c0t["randomness_contract"]["value"])
        self.assertFalse(c0t["randomness_contract"]["entropy_used"])
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw)):
            V._validate_c0t_live(
                c0t, activation_receipt_path=Path("unused"), replay_input_path=Path("unused-replay"),
            )
        forged = copy.deepcopy(c0t)
        forged["publication_observation"]["github_run"]["completed_at_utc"] = "2026-08-20T00:00:59Z"
        forged["publication_observation"]["receipt_sha256"] = V.observation_digest(forged["publication_observation"])
        forged["artifact_sha256"] = V.c0t_digest(forged)
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw)), \
             self.assertRaisesRegex(V.PublicationError, "direct GitHub server replay"):
            V._validate_c0t_live(
                forged, activation_receipt_path=Path("unused"), replay_input_path=Path("unused-replay"),
            )

    def test_verify_requires_exact_c0t_direct_child_one_path_commit_and_public_tip(self) -> None:
        raw = self.run_raw(); c0t_commit = "f" * 40
        with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
             mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw)):
            c0t = V.compile_c0t(
                self.c0a_commit, self.run_id, Path("unused"), Path("unused-replay"),
            )
        artifact = V.ROOT / V.C0T_PATH
        artifact.write_bytes(V.canonical_json(c0t))
        def good_git(*args: str) -> bytes:
            if args[:3] == ("show", "-s", "--format=%P"):
                return (self.c0a_commit + "\n").encode()
            if args[:4] == ("diff-tree", "--no-commit-id", "--name-status", "-r"):
                return f"A\t{V.C0T_PATH}\n".encode()
            raise AssertionError(args)
        try:
            with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
                 mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw, ref_tip=c0t_commit)), \
                 mock.patch.object(V, "exact_commit"), mock.patch.object(V, "git", side_effect=good_git), \
                 mock.patch.object(V, "commit_file", return_value=artifact.read_bytes()):
                V.validate_c0t(
                    c0t, activation_receipt_path=Path("unused"), replay_input_path=Path("unused-replay"),
                    c0t_commit=c0t_commit, artifact_path=artifact,
                )
            def wrong_parent(*args: str) -> bytes:
                if args[:3] == ("show", "-s", "--format=%P"):
                    return ("0" * 40 + "\n").encode()
                return good_git(*args)
            with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
                 mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw, ref_tip=c0t_commit)), \
                 mock.patch.object(V, "exact_commit"), mock.patch.object(V, "git", side_effect=wrong_parent), \
                 self.assertRaisesRegex(V.PublicationError, "direct nonmerge child"):
                V.validate_c0t(
                    c0t, activation_receipt_path=Path("unused"), replay_input_path=Path("unused-replay"),
                    c0t_commit=c0t_commit, artifact_path=artifact,
                )
            with mock.patch.object(V, "load_c0a", side_effect=self.loaded), \
                 mock.patch.object(V, "live_fetch", side_effect=self.fetcher(raw, ref_tip="0" * 40)), \
                 self.assertRaisesRegex(V.PublicationError, "rewritten"):
                V.validate_c0t(
                    c0t, activation_receipt_path=Path("unused"), replay_input_path=Path("unused-replay"),
                    c0t_commit=c0t_commit, artifact_path=artifact,
                )
        finally:
            artifact.unlink(missing_ok=True)

    def test_cli_exposes_no_caller_run_json_or_timestamp_authority(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn('add_argument("--run-json"', text)
        self.assertNotIn('add_argument("--observed-at"', text)
        self.assertIn('add_argument("--commit", required=True)', text)
        workflow = (V.ROOT / V.WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotIn("upload-artifact", workflow)
        self.assertNotIn("workflow_dispatch", workflow)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "verify-c0t", "--artifact", "missing.json"],
            cwd=V.ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--commit", result.stderr)
        canonical_schema = json.loads((V.ROOT / "schemas/benchmark-v1.5-c0.schema.json").read_text())
        allowed = canonical_schema["definitions"]["c0t"]["properties"]["attestation_policy"]["properties"]["allowed_c0t_changed_paths"]
        self.assertEqual(allowed, {"const": [V.C0T_PATH]})

    def test_canonical_c0_and_observer_chain_are_in_the_p1_native_manifest(self) -> None:
        import build_benchmark_v15_p1 as p1
        required = {
            "c0_v15_builder", "c0_v15_schema", "c0_observer_workflow", "c0_observer_workflow_contract_test",
            "c0_publication_verifier", "c0_publication_verifier_contract_test",
            "c0_publication_observation_schema", "c0_pass_pool_replay_input_schema",
        }
        self.assertLessEqual(required, set(p1.NATIVE_COMPONENTS))
        manifest = json.loads((V.ROOT / "results/benchmark/v1.5-protocol/checkpoint-component-manifest.json").read_text())
        schema = json.loads((V.ROOT / "schemas/benchmark-checkpoint-component-manifest-v1.5.schema.json").read_text())
        V.Draft7Validator(schema).validate(manifest)
        selectors = manifest["components"]["c0_publication"]
        self.assertEqual(selectors["canonical_builder"]["role"], "c0_v15_builder")
        self.assertEqual(selectors["verifier"]["role"], "c0_publication_verifier")


if __name__ == "__main__":
    unittest.main()
