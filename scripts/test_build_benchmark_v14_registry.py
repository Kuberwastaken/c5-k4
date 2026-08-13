#!/usr/bin/env python3
"""Focused tests for the one-shot Method v1.4 production registry builder."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import subprocess


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v14_registry as registry  # noqa: E402


class RegistryBuilderTests(unittest.TestCase):
    def test_git_subprocess_environment_is_exact_and_ambient_free(self) -> None:
        result = subprocess.CompletedProcess([], 0, b"", b"")
        with mock.patch.dict("os.environ", {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "url.file:///tmp/evil.insteadOf",
            "HTTPS_PROXY": "http://127.0.0.1:9",
        }), mock.patch.object(registry.subprocess, "run", return_value=result) as run:
            registry.run_network(["/usr/bin/git", "version"])
        self.assertEqual(run.call_args.kwargs["env"], registry.SAFE_GIT_ENV)
        self.assertNotIn("GIT_CONFIG_COUNT", run.call_args.kwargs["env"])
        self.assertNotIn("HTTPS_PROXY", run.call_args.kwargs["env"])

    def test_repository_initialization_uses_absolute_git_and_exact_environment(self) -> None:
        result = subprocess.CompletedProcess([], 0, b"", b"")
        with mock.patch.object(registry.subprocess, "run", return_value=result) as run:
            registry.initialize_upstream_repository(Path("/tmp/fresh-v14.git"))
        self.assertEqual(run.call_args.args[0][0], "/usr/bin/git")
        self.assertIn("--bare", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["env"], registry.SAFE_GIT_ENV)

    def test_preflight_rejects_noncanonical_public_remote_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialized = root / "materialized.git"
            request = root / "preflight.json"
            request.write_text(json.dumps({
                "schema_version": registry.PREFLIGHT_SCHEMA_VERSION,
                "p0t_commit": "a" * 40,
                "public_remote_url": "file:///tmp/not-public.git",
                "upstream_repository_path": str(materialized),
                "upstream_fetch_command": registry.upstream_fetch_command(materialized),
            }), encoding="utf-8")
            with mock.patch.object(registry, "UPSTREAM_REPOSITORY", materialized), \
                 mock.patch.object(registry, "run_network") as network:
                with self.assertRaisesRegex(registry.RegistryBuildError, "canonical protocol remote"):
                    registry.preflight(request, root / "receipts")
            network.assert_not_called()
            self.assertFalse(materialized.exists())

    def test_preflight_rejects_mutated_upstream_remote_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialized = root / "materialized.git"
            command = registry.upstream_fetch_command(materialized)
            command[command.index(registry.UPSTREAM_REMOTE)] = "file:///tmp/forged-upstream.git"
            request = root / "preflight.json"
            request.write_text(json.dumps({
                "schema_version": registry.PREFLIGHT_SCHEMA_VERSION,
                "p0t_commit": "a" * 40,
                "public_remote_url": registry.PUBLIC_PROTOCOL_REMOTE,
                "upstream_repository_path": str(materialized),
                "upstream_fetch_command": command,
            }), encoding="utf-8")
            with mock.patch.object(registry, "UPSTREAM_REPOSITORY", materialized), \
                 mock.patch.object(registry, "run_network") as network:
                with self.assertRaisesRegex(registry.RegistryBuildError, "fetch command"):
                    registry.preflight(request, root / "receipts")
            network.assert_not_called()

    def test_offline_build_rejects_mutually_consistent_noncanonical_remote(self) -> None:
        forged = "file:///tmp/forged-public.git"
        with self.assertRaisesRegex(registry.RegistryBuildError, "canonical S0"):
            registry.validate_public_remote_binding(
                {"remote_url": forged}, {"protocol": {"public_remote_url": forged}}
            )

    def test_repository_feature_audit_rejects_promisor_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo.git"
            subprocess.run(["/usr/bin/git", "init", "--bare", "--quiet", str(repo)], check=True)
            (repo / "objects/pack/pack-fixture.promisor").touch()
            self.assertIn("promisor-marker", registry.absent_repository_features(repo))

    def test_repository_feature_audit_rejects_hostile_include_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo.git"
            marker = root / "textconv-executed"
            executable = root / "textconv.sh"
            executable.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
            executable.chmod(0o755)
            included = root / "included.gitconfig"
            included.write_text(
                f"[diff \"hostile\"]\n\ttextconv = {executable}\n",
                encoding="utf-8",
            )
            subprocess.run(["/usr/bin/git", "init", "--bare", "--quiet", str(repo)], check=True)
            subprocess.run(
                ["/usr/bin/git", "-C", str(repo), "config", "--local", "include.path", str(included)],
                check=True,
            )

            self.assertIn(
                "executable-local-config", registry.absent_repository_features(repo)
            )
            self.assertFalse(marker.exists())

    def test_authoritative_exemptions_are_exact_two_historical_units(self) -> None:
        ledger = json.loads(
            (ROOT / "results/benchmark/v1.4-protocol/registry-exemption-rule.json").read_text(
                encoding="utf-8"
            )
        )
        policy = json.loads(
            (ROOT / "results/benchmark/v1.4-protocol/provenance-policy.json").read_text(
                encoding="utf-8"
            )
        )
        registry.validate_exemption_ledger(ledger, policy)
        self.assertEqual(len(ledger["units"]), 2)
        self.assertEqual(
            {row["content_schema"] for row in ledger["units"]},
            {
                "c5k4-open-inventory-1.2-prototype",
                "c5k4-question-cluster-pool-1.2-prototype",
            },
        )
        self.assertTrue(
            all("results/benchmark/v1.2-prototype/" in row["locator"] for row in ledger["units"])
        )
        self.assertFalse(ledger["policy"]["global_content_hash_allowlist"])
        self.assertFalse(ledger["policy"]["future_outputs_exemptible"])

    def request_fixture(self) -> dict:
        digest = "1" * 64
        ref = {
            "path": "fixture.json", "file_sha256": digest,
            "canonical_sha256": digest, "schema_version": "fixture-1.0",
            "authority": "FROZEN_PRODUCTION_INPUT",
        }
        return {
            "schema_version": registry.INPUT_SCHEMA_VERSION,
            "authority": "PRODUCTION_AFTER_P0T_S0", "protocol_version": "1.4",
            "build_ordinal": 1, "allowed_build_count": 1,
            "chronology": {
                "p0_artifact_commit": "1" * 40, "p0_attestation_commit": "2" * 40,
                "p0_published_at_utc": "2026-08-13T19:00:00Z", "s0_snapshot_id": "S0",
                "s0_acquired_at_utc": "2026-08-13T19:10:00Z", "s0_snapshot_sha256": "3" * 64,
            },
            "upstream": {
                "repository": "https://github.com/google-deepmind/formal-conjectures.git",
                "remote_ref": "refs/heads/main", "commit": "4" * 40, "tree": "5" * 40,
                "subtree": "FormalConjectures", "resolution_count": 1,
                "materialized_repository_path": "/home/ec2-user/.local/share/c5k4-v14-formal-conjectures.git",
            },
            "producer": {
                "producer_id": "method-v1.4-production-registry-builder",
                "executable_path": "scripts/build_benchmark_v14_registry.py",
                "executable_sha256": digest, "invocation_contract_sha256": digest,
                "input_schema_sha256": digest, "output_schema_sha256": digest,
            },
            "inputs": {name: dict(ref) for name in (
                "p0a", "p0t", "s0", "sources_config", "five_strata_classifier",
                "grouping_rule", "provenance_policy", "source_discovery_boundary",
                "quotas", "registry_exemptions",
            )},
            "resolver_receipts": {"public_p0t": dict(ref), "upstream_main": dict(ref)},
            "controls": {
                "prototype_inputs_permitted": False, "candidate_semantics_inspected": False,
                "entropy_used": False, "selected_clusters": [],
                "selection_or_ranking_permitted": False,
                "create_exclusive_output_directory": True, "overwrite_permitted": False,
            },
            "registry_build_invoked_at_utc": "2026-08-13T19:20:00Z",
        }

    def test_execute_emits_schema_valid_production_envelope_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = self.request_fixture()
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            artifacts = {}
            for artifact_id, version in registry.OUTPUT_SCHEMAS.items():
                rows_key = "strata" if artifact_id == "quota_feasibility" else "records" if artifact_id == "provenance_inventory" else "clusters"
                artifacts[artifact_id] = {"schema_version": version, rows_key: []}
            artifacts["eligible_pool"]["clusters"] = []
            artifacts["quota_feasibility"]["status"] = "FAIL"
            artifacts["quota_feasibility"]["strata"] = [{
                "stratum": stratum, "quota": registry.QUOTAS[stratum], "eligible_count": 0,
                "deficit": registry.QUOTAS[stratum], "surplus": 0,
            } for stratum in registry.STRATA]
            loaded = {"s0": (root / "s0", {"snapshot_sha256": "3" * 64}, b"{}")}
            output_dir = root / "production"
            with mock.patch.object(registry, "validate_protocol_bindings", return_value=loaded), \
                 mock.patch.object(registry, "production_artifacts", return_value=artifacts), \
                 mock.patch.object(registry, "run_network", side_effect=AssertionError("offline build attempted network")) as network:
                output = registry.execute(request_path, root, output_dir)
            network.assert_not_called()
            self.assertEqual(output["feasibility_replay"]["terminal_result"], "NO_ELIGIBLE_BENCHMARK_PRE_C0")
            self.assertEqual(len(output["artifacts"]), 6)
            self.assertTrue((output_dir / "registry-build-output.json").is_file())
            self.assertEqual(output["output_sha256"], registry.object_digest(output, "output_sha256"))

    def test_execute_runs_real_syntax_and_contamination_offline_with_hardened_git(self) -> None:
        """Exercise the complete post-binding production path, not a stub artifact map."""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            formal_repo = root / "formal-conjectures"
            subprocess.run(
                ["/usr/bin/git", "init", "--quiet", "-b", "main", str(formal_repo)],
                check=True,
            )
            subprocess.run(
                ["/usr/bin/git", "-C", str(formal_repo), "config", "user.email", "v14@example.invalid"],
                check=True,
            )
            subprocess.run(
                ["/usr/bin/git", "-C", str(formal_repo), "config", "user.name", "Method v1.4 test"],
                check=True,
            )
            module = formal_repo / "FormalConjectures/GraphFixture.lean"
            module.parent.mkdir()
            module.write_text(
                "import Mathlib.Combinatorics.SimpleGraph.Basic\n"
                "@[category research open]\n"
                "theorem graph_fixture (G : SimpleGraph (Fin 4)) : "
                "G.edgeSet.ncard ≤ 6 := by sorry\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["/usr/bin/git", "-C", str(formal_repo), "add", module.relative_to(formal_repo)],
                check=True,
            )
            subprocess.run(
                ["/usr/bin/git", "-C", str(formal_repo), "commit", "--quiet", "-m", "fixture"],
                check=True,
            )
            commit = subprocess.run(
                ["/usr/bin/git", "-C", str(formal_repo), "rev-parse", "HEAD"],
                check=True,
                stdout=subprocess.PIPE,
            ).stdout.decode().strip()
            tree = subprocess.run(
                ["/usr/bin/git", "-C", str(formal_repo), "rev-parse", "HEAD^{tree}"],
                check=True,
                stdout=subprocess.PIPE,
            ).stdout.decode().strip()

            semantic_tree = root / "semantic-source"
            semantic_tree.mkdir()
            evidence = semantic_tree / "evidence.txt"
            evidence.write_text(
                "Prior discussion names FormalConjectures/GraphFixture.lean exactly.\n",
                encoding="utf-8",
            )
            snapshot_entry, _ = registry.source_snapshot._filesystem_entry_with_raw(
                semantic_tree, "evidence.txt"
            )
            snapshot_entry["layer"] = "CURRENT_TREE"

            classifier_path = ROOT / "results/benchmark/v1.4-protocol/five-strata-classifier.json"
            policy_path = ROOT / "results/benchmark/v1.4-protocol/provenance-policy.json"
            classifier_raw = classifier_path.read_bytes()
            policy_raw = policy_path.read_bytes()
            s0 = {
                "p0a_published_at_utc": "2026-08-13T19:00:00Z",
                "acquired_at_utc": "2026-08-13T19:10:00Z",
                "sources": [{
                    "source_id": "fixture-tree",
                    "kind": "tree",
                    "path": str(semantic_tree),
                    "tree_snapshot": {"entries": [snapshot_entry]},
                }],
            }
            sources_config = {"fixture": "exact S0 tree is supplied above"}
            exemptions = {"complete": True, "units": []}
            loaded = {
                "five_strata_classifier": (
                    classifier_path,
                    json.loads(classifier_raw),
                    classifier_raw,
                ),
                "provenance_policy": (
                    policy_path,
                    json.loads(policy_raw),
                    policy_raw,
                ),
                "s0": (root / "s0.json", s0, registry.pretty_json(s0)),
                "sources_config": (
                    root / "sources.json",
                    sources_config,
                    registry.pretty_json(sources_config),
                ),
                "registry_exemptions": (
                    root / "exemptions.json",
                    exemptions,
                    registry.pretty_json(exemptions),
                ),
            }
            request = self.request_fixture()
            request["upstream"].update({
                "commit": commit,
                "tree": tree,
            })
            request_path = root / "request.json"
            request_path.write_bytes(registry.pretty_json(request))
            output_dir = root / "production"

            real_subprocess_run = subprocess.run
            with mock.patch.object(
                registry, "validate_protocol_bindings", return_value=loaded
            ), mock.patch.object(
                registry, "production_artifacts", wraps=registry.production_artifacts
            ) as production, mock.patch.object(
                registry.syntax, "extract", wraps=registry.syntax.extract
            ) as extract, mock.patch.object(
                registry.contamination, "build", wraps=registry.contamination.build
            ) as contamination_build, mock.patch.object(
                registry.source_snapshot,
                "assert_offline_git_repository",
                wraps=registry.source_snapshot.assert_offline_git_repository,
            ) as isolation_audit, mock.patch.object(
                registry.source_snapshot.subprocess,
                "run",
                wraps=real_subprocess_run,
            ) as git_run, mock.patch.object(
                registry,
                "run_network",
                side_effect=AssertionError("offline production path attempted network"),
            ) as network:
                output = registry.execute(request_path, formal_repo, output_dir)

            network.assert_not_called()
            production.assert_called_once()
            extract.assert_called_once()
            contamination_build.assert_called_once()
            isolation_audit.assert_called()
            self.assertEqual(output["feasibility_replay"]["total_row_count"], 1)
            self.assertEqual(output["feasibility_replay"]["eligible_row_count"], 0)

            eligible = json.loads((output_dir / "eligible-cluster-pool.json").read_bytes())
            self.assertEqual(len(eligible["clusters"]), 1)
            self.assertTrue(eligible["clusters"][0]["semantic_exposure"])
            self.assertFalse(eligible["clusters"][0]["eligible"])
            contamination_inventory = json.loads(
                (output_dir / "contamination-inventory.json").read_bytes()
            )
            self.assertTrue(contamination_inventory["complete"])
            self.assertEqual(contamination_inventory["excluded_cluster_count"], 1)

            commands = [call.args[0] for call in git_run.call_args_list]
            self.assertTrue(commands)
            self.assertTrue(all(command[0] == "/usr/bin/git" for command in commands))
            self.assertTrue(
                all(
                    list(registry.source_snapshot.SAFE_GIT_CONFIG_ARGS)
                    == command[1 : 1 + len(registry.source_snapshot.SAFE_GIT_CONFIG_ARGS)]
                    for command in commands
                )
            )
            self.assertTrue(
                all(call.kwargs.get("env") == registry.source_snapshot.SAFE_GIT_ENV for call in git_run.call_args_list)
            )
            show_commands = [command for command in commands if "show" in command]
            self.assertTrue(show_commands)
            self.assertTrue(
                all("--no-ext-diff" in command and "--no-textconv" in command for command in show_commands)
            )

    def test_preflight_makes_exactly_two_network_calls_and_materializes_destination_ref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            subprocess.run(["git", "init", "--quiet", "-b", "main", str(source)], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "v14@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Method v1.4 test"], check=True)
            (source / "FormalConjectures").mkdir()
            (source / "FormalConjectures/Test.lean").write_text("theorem test : True := by trivial\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "FormalConjectures/Test.lean"], check=True)
            subprocess.run(["git", "-C", str(source), "commit", "--quiet", "-m", "fixture"], check=True)
            commit = subprocess.run(
                ["git", "-C", str(source), "rev-parse", "HEAD"], check=True,
                stdout=subprocess.PIPE,
            ).stdout.decode().strip()
            tree = subprocess.run(
                ["git", "-C", str(source), "rev-parse", "HEAD^{tree}"], check=True,
                stdout=subprocess.PIPE,
            ).stdout.decode().strip()
            materialized = root / "materialized.git"
            request = root / "preflight.json"
            request.write_text(json.dumps({
                "schema_version": registry.PREFLIGHT_SCHEMA_VERSION,
                "p0t_commit": commit,
                "public_remote_url": registry.PUBLIC_PROTOCOL_REMOTE,
                "upstream_repository_path": str(materialized),
                "upstream_fetch_command": registry.upstream_fetch_command(materialized),
            }), encoding="utf-8")

            calls = []
            def fake_network(command: list[str]) -> subprocess.CompletedProcess[bytes]:
                calls.append(command)
                if len(calls) == 1:
                    return subprocess.CompletedProcess(command, 0, f"{commit}\trefs/heads/main\n".encode(), b"public raw\n")
                if len(calls) == 2:
                    local_fetch = list(command)
                    local_fetch[local_fetch.index(registry.UPSTREAM_REMOTE)] = str(source)
                    result = subprocess.run(local_fetch, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    return subprocess.CompletedProcess(command, 0, result.stdout, result.stderr)
                raise AssertionError("third network command attempted")

            with mock.patch.object(registry, "UPSTREAM_REPOSITORY", materialized), \
                 mock.patch.object(registry, "run_network", side_effect=fake_network) as run:
                receipts = registry.preflight(request, root / "receipts")
            self.assertEqual(run.call_count, 2)
            self.assertEqual(calls[0], registry.public_advertisement_command(registry.PUBLIC_PROTOCOL_REMOTE))
            self.assertEqual(calls[1], registry.upstream_fetch_command(materialized))
            self.assertEqual(set(receipts), {"public_p0t", "upstream_main"})
            self.assertTrue((root / "receipts/public-p0t.json").is_file())
            self.assertTrue((root / "receipts/upstream-main.json").is_file())
            self.assertEqual(receipts["upstream_main"]["kind"], "UPSTREAM_MAIN_MATERIALIZATION")
            self.assertEqual(receipts["upstream_main"]["repository_path"], str(materialized))
            self.assertEqual(receipts["upstream_main"]["commit"], commit)
            self.assertEqual(receipts["upstream_main"]["root_tree"], tree)
            self.assertEqual(receipts["upstream_main"]["destination_ref"], registry.UPSTREAM_DESTINATION_REF)
            self.assertTrue(receipts["upstream_main"]["repository_audit"]["fetch_head_absent"])
            self.assertEqual(
                receipts["upstream_main"]["stdout_sha256"],
                registry.sha256(receipts["upstream_main"]["stdout"].encode()),
            )
            self.assertEqual(
                receipts["upstream_main"]["stderr_sha256"],
                registry.sha256(receipts["upstream_main"]["stderr"].encode()),
            )
            self.assertFalse((materialized / "FETCH_HEAD").exists())
            self.assertFalse((materialized / "shallow").exists())
            self.assertEqual(
                subprocess.run(
                    ["git", "-C", str(materialized), "rev-parse", f"{registry.UPSTREAM_DESTINATION_REF}^{{commit}}"],
                    check=True, stdout=subprocess.PIPE,
                ).stdout.decode().strip(),
                commit,
            )

    def test_preflight_rejects_nonfresh_repository_before_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialized = root / "already-exists"
            materialized.mkdir()
            request = root / "preflight.json"
            request.write_text(json.dumps({
                "schema_version": registry.PREFLIGHT_SCHEMA_VERSION,
                "p0t_commit": "a" * 40,
                "public_remote_url": registry.PUBLIC_PROTOCOL_REMOTE,
                "upstream_repository_path": str(materialized),
                "upstream_fetch_command": registry.upstream_fetch_command(materialized),
            }), encoding="utf-8")
            with mock.patch.object(registry, "UPSTREAM_REPOSITORY", materialized), \
                 mock.patch.object(registry, "run_network") as run:
                with self.assertRaisesRegex(registry.RegistryBuildError, "must be absent"):
                    registry.preflight(request, root / "receipts")
            run.assert_not_called()

    def test_public_advertisement_failure_prevents_upstream_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            materialized = root / "materialized"
            request = root / "preflight.json"
            request.write_text(json.dumps({
                "schema_version": registry.PREFLIGHT_SCHEMA_VERSION,
                "p0t_commit": "a" * 40,
                "public_remote_url": registry.PUBLIC_PROTOCOL_REMOTE,
                "upstream_repository_path": str(materialized),
                "upstream_fetch_command": registry.upstream_fetch_command(materialized),
            }), encoding="utf-8")
            response = subprocess.CompletedProcess([], 0, b"b" * 40 + b"\trefs/heads/main\n", b"")
            with mock.patch.object(registry, "UPSTREAM_REPOSITORY", materialized), \
                 mock.patch.object(registry, "run_network", return_value=response) as run:
                with self.assertRaisesRegex(registry.RegistryBuildError, "does not advertise"):
                    registry.preflight(request, root / "receipts")
            self.assertEqual(run.call_count, 1)
            self.assertFalse((root / "receipts").exists())

    def test_output_names_and_production_schemas_are_exact(self) -> None:
        self.assertEqual(
            registry.OUTPUT_FILES,
            {
                "open_inventory": "open-inventory.json",
                "question_cluster_pool": "question-cluster-pool.json",
                "provenance_inventory": "provenance-inventory.json",
                "contamination_inventory": "contamination-inventory.json",
                "eligible_pool": "eligible-cluster-pool.json",
                "quota_feasibility": "quota-feasibility.json",
            },
        )
        self.assertTrue(all("prototype" not in value for value in registry.OUTPUT_SCHEMAS.values()))

    def test_existing_output_fails_before_protocol_or_target_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / "request.json"
            request.write_text("{}\n", encoding="utf-8")
            output = root / "already-there"
            output.mkdir()
            with mock.patch.object(registry, "validate_schema") as validate:
                with self.assertRaisesRegex(registry.RegistryBuildError, "already exists"):
                    registry.execute(request, root, output)
            validate.assert_called_once()

    def test_row_replay_accepts_exact_fail_and_rejects_false_fail(self) -> None:
        rows = []
        for index, stratum in enumerate(registry.STRATA):
            rows.append({
                "cluster_id": f"c{index}", "identity_sha256": f"{index + 1:064x}",
                "stratum": stratum, "eligible": False,
                "machine_classification_unambiguous": True,
                "identity_grouping_complete": True,
                "semantic_exposure": True, "unknown_exposure": False,
                "registry_contact_evidence_count": 0,
            })
        pool = {
            "schema_version": "c5k4-eligible-cluster-pool-1.4",
            "artifact_status": "CONTAMINATION_APPLIED",
            "upstream": {"repository": "google-deepmind/formal-conjectures", "commit": "1" * 40, "tree": "2" * 40},
            "digests": {f"{key}_sha256": "3" * 64 for key in registry.selector.ARTIFACT_KEYS},
            "clusters": rows,
        }
        strata = [{
            "stratum": stratum, "quota": registry.QUOTAS[stratum],
            "eligible_count": 0, "deficit": registry.QUOTAS[stratum], "surplus": 0,
        } for stratum in registry.STRATA]
        feasibility = {
            "schema_version": "c5k4-quota-feasibility-1.4", "status": "FAIL",
            "strata": strata,
        }
        feasibility["certificate_sha256"] = registry.object_digest(feasibility, "certificate_sha256")
        artifacts = {"eligible_pool": pool, "quota_feasibility": feasibility}
        registry.replay_rows(artifacts, {})
        feasibility["strata"][0]["eligible_count"] = 1
        feasibility["certificate_sha256"] = registry.object_digest(feasibility, "certificate_sha256")
        with self.assertRaisesRegex(registry.RegistryBuildError, "does not replay"):
            registry.replay_rows(artifacts, {})

    def test_output_self_digest_omits_only_self_field(self) -> None:
        value = {"schema_version": "x", "answer": 7}
        value["output_sha256"] = registry.object_digest(value, "output_sha256")
        self.assertEqual(value["output_sha256"], registry.object_digest(value, "output_sha256"))
        value["answer"] = 8
        self.assertNotEqual(value["output_sha256"], registry.object_digest(value, "output_sha256"))

    def test_s0_canonical_digest_omits_snapshot_not_input_binding(self) -> None:
        value = {
            "schema_version": "c5k4-source-snapshot-S0-1.4",
            "snapshot_sha256": "1" * 64,
            "sources_config_sha256": "2" * 64,
        }
        self.assertEqual(
            registry.artifact_object_digest(value),
            registry.object_digest(value, "snapshot_sha256"),
        )
        value["sources_config_sha256"] = "3" * 64
        self.assertNotEqual(
            registry.artifact_object_digest(value),
            registry.object_digest({**value, "sources_config_sha256": "2" * 64}, "snapshot_sha256"),
        )

    def test_exemption_ledger_is_unit_exact_and_rule_bound(self) -> None:
        policy = {
            "machine_exemption_required_fields": [
                "source_id", "source_kind", "locator", "role", "content_sha256",
                "content_schema", "unit_identity_sha256", "producer_verified",
                "invocation_contract_verified", "output_digest_verified",
                "bounded_schema_verified", "mixed_unit_rejected",
            ],
            "machine_exemption_required_true": [
                "producer_verified", "invocation_contract_verified",
                "output_digest_verified", "bounded_schema_verified", "mixed_unit_rejected",
            ],
            "machine_roles": ["machine-generated-git-blob"],
            "machine_source_kinds": {"machine-generated-git-blob": ["git"]},
            "bounded_content_schemas": ["c5k4-open-inventory-1.4"],
        }
        row = {
            "source_id": "repo:c5-k4", "source_kind": "git",
            "locator": "git-blob:abc:open-inventory.json",
            "role": "machine-generated-git-blob", "content_sha256": "1" * 64,
            "content_schema": "c5k4-open-inventory-1.4",
            "producer_verified": True, "invocation_contract_verified": True,
            "output_digest_verified": True, "bounded_schema_verified": True,
            "mixed_unit_rejected": True,
        }
        row["unit_identity_sha256"] = registry.contamination.provenance.unit_identity_sha256(row)
        ledger = {
            "schema_version": "c5k4-registry-exemption-rule-1.4",
            "artifact_status": "AUTHORITATIVE_P0_PROTOCOL", "complete": True,
            "policy": {"global_content_hash_allowlist": False}, "units": [row],
            "registry_only_unit_identity_sha256": [row["unit_identity_sha256"]],
        }
        ledger["inventory_sha256"] = registry.object_digest(ledger, "inventory_sha256")
        registry.validate_exemption_ledger(ledger, policy)
        broken = json.loads(json.dumps(ledger))
        broken["units"][0]["locator"] = "git-blob:other:open-inventory.json"
        with self.assertRaisesRegex(registry.RegistryBuildError, "identity"):
            registry.validate_exemption_ledger(broken, policy)

    def test_normalized_source_config_uses_all_s0_kinds(self) -> None:
        s0 = {"sources": [
            {"source_id": "a", "kind": "git_history", "tips": [{"object_id": "1" * 40}], "path": "/a"},
            {"source_id": "b", "kind": "git_user_delta", "head_commit": "2" * 40, "tips": [], "upstream_base_refs": [{"object_id": "3" * 40}], "path": "/b"},
            {"source_id": "c", "kind": "tree", "path": "/c"},
            {"source_id": "d", "kind": "git_sessions", "immutable_commit": "4" * 40, "path": "/d", "session_mirrors": [{"id": "codex", "format": "codex", "ai_chats_subdir": "codex"}]},
            {"source_id": "e", "kind": "release_metadata_snapshot", "path": "/e"},
        ]}
        config = registry.normalize_sources(s0)
        self.assertEqual([row["kind"] for row in config["sources"]], ["git", "git_delta", "tree", "git_sessions", "release_snapshot"])


if __name__ == "__main__":
    unittest.main()
