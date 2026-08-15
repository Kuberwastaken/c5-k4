#!/usr/bin/env python3
"""Target-free tests for the frozen Bondy constructor and execution lock."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import networkx as nx

import prospective_bondy_construct as construct
import prospective_bondy_gate as live_gate
import prospective_bondy_search as search
import prospective_bondy_verify as verify

ROOT = Path(__file__).resolve().parents[1]


def pull_fixture(number: int, title: str | None = None) -> dict[str, object]:
    return {
        "number": number,
        "title": title or f"pull {number}",
        "draft": False,
        "updated_at": "2026-08-14T00:00:00Z",
        "head": {"sha": f"head-{number}", "ref": f"head/{number}", "repo": {"full_name": "fork/repo"}},
        "base": {"sha": f"base-{number}", "ref": "main", "repo": {"full_name": "google-deepmind/formal-conjectures"}},
    }


def live_attestation_fixture(empty: bool = False, identity_only_binding: bool = False) -> dict[str, object]:
    pinned = "1" * 40
    pinned_tree = "2" * 40
    live = "3" * 40
    live_tree = "4" * 40
    identity = {**live_gate.pull_identity(pull_fixture(1)), "node_id": "PR_1", "state": "OPEN", "changed_files": 1}
    identity.update({"head_sha": "a" * 40, "base_sha": "b" * 40})
    paths = ["FormalConjectures/Unrelated.lean"]
    bindings = [] if empty else [{
        **identity,
        "changed_paths": paths,
        "changed_paths_sha256": search.canonical_sha256(paths),
    }]
    if identity_only_binding:
        bindings = [dict(identity)]
    closure_entries = [{"path": live_gate.TARGET_PATH}, {"path": "FormalConjectures/Imported.lean"}]
    toolchain = [{"path": "lean-toolchain"}]
    external = [{"name": "mathlib", "rev": "r"}]
    target_raw = "@[category research open, AMS 5]\ntheorem bondy_conjecture : answer(sorry) ↔ True := by\n  sorry\n"
    raw_sha = __import__("hashlib").sha256(target_raw.encode("utf-8")).hexdigest()
    declaration = {"declaration_count": 1, "exact_open_attribute_count": 1, "answer_wrapper_count": 1, "exact_by_sorry_block_count": 1}
    continuity = {
        "pinned": {"commit": pinned, "tree": pinned_tree},
        "live": {"commit": live, "tree": live_tree},
        "merge_base": pinned, "ancestor_verified": True,
        "commits": [{"commit": live, "parents": [pinned], "tree": live_tree, "subject": "unrelated", "changed_paths": ["unrelated"]}],
        "delta": [{"status": "M", "path": "unrelated"}],
        "delta_sha256": search.canonical_sha256([{"status": "M", "path": "unrelated"}]),
        "target": {"path": live_gate.TARGET_PATH, "mode": "100644", "type": "blob", "blob": "5" * 40, "bytes": len(target_raw.encode("utf-8")), "sha256": raw_sha},
        "target_raw_utf8": target_raw, "declaration": declaration,
        "closure_count": 2, "closure_sha256": search.canonical_sha256(closure_entries), "closure_entries": closure_entries,
        "toolchain_sha256": search.canonical_sha256(toolchain), "toolchain": toolchain,
        "external_revisions_sha256": search.canonical_sha256(external), "external_revisions": external,
        "protected_paths": sorted([live_gate.TARGET_PATH, "FormalConjectures/Imported.lean", "lean-toolchain"]),
    }
    snapshot = {
        "main": continuity["live"],
        "continuity": {
            "canonical_sha256": search.canonical_sha256(continuity), "live": continuity["live"],
            "target": continuity["target"], "target_raw_bytes": len(target_raw.encode("utf-8")), "target_raw_sha256": raw_sha,
            "declaration": declaration, "closure_count": 2, "closure_sha256": continuity["closure_sha256"],
            "toolchain_sha256": continuity["toolchain_sha256"], "external_revisions_sha256": continuity["external_revisions_sha256"],
        },
        "known_issue": {"number": 4858, "state": "closed", "state_reason": "completed", "title": "i", "author": "a", "created_at": "t", "updated_at": "t", "closed_at": "2026-08-14T20:25:51Z", "node_id": "I", "is_pull_request": False},
        "known_pr": {"number": 4879, "state": "closed", "draft": False, "merged": True, "merged_at": "2026-08-14T20:25:50Z", "merge_commit_sha": "8781428a922a53914450550218bf14be703d8d69", "title": "p", "author": "a", "head_sha": "a" * 40, "base_sha": "b" * 40, "updated_at": "t", "node_id": "P"},
        "searches": {
            'repo:google-deepmind/formal-conjectures "bondy_conjecture"': [4879],
            'repo:google-deepmind/formal-conjectures "BondyLongestCycles"': [],
            'repo:google-deepmind/formal-conjectures "2606.03696"': [4879],
        },
        "open_pull_binding_surface": {"total_count": len(bindings), "bindings": bindings},
        "repository_total_count": 0,
    }
    local_identities = [
        {"commit": live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT, "subject": "research: define Bondy tip continuity gate", "paths": [live_gate.KNOWN_CONTINUITY_AUDIT_PATH], "kind": "known_continuity_audit"},
        {"commit": live_gate.KNOWN_REPIN_AUDIT_COMMIT, "subject": "research: audit Bondy upstream repin", "paths": [live_gate.KNOWN_REPIN_AUDIT_PATH], "kind": "known_repin_audit"},
        {"commit": "e" * 40, "subject": "freeze v1", "paths": ["scripts/prospective_bondy_gate.py"], "kind": "freeze_introducer"},
        {"commit": "f" * 40, "subject": "freeze v3", "paths": ["scripts/prospective_bondy_gate.py"], "kind": "freeze_introducer"},
        {"commit": "8" * 40, "subject": "freeze v3.1", "paths": ["scripts/prospective_bondy_gate.py"], "kind": "freeze_introducer"},
        {"commit": "7" * 40, "subject": "freeze v3.2", "paths": ["scripts/prospective_bondy_gate.py"], "kind": "freeze_introducer"},
        {"commit": "6" * 40, "subject": "freeze v3.3", "paths": ["scripts/prospective_bondy_gate.py"], "kind": "freeze_introducer"},
        {"commit": live_gate.KNOWN_GRAPH_ROTATION_COMMIT, "subject": live_gate.KNOWN_GRAPH_ROTATION_SUBJECT, "paths": [live_gate.KNOWN_GRAPH_ROTATION_PATH], "kind": "known_graph_rotation"},
        {"commit": live_gate.KNOWN_PREFLIGHT_COMMIT, "subject": "preflight", "paths": ["results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md"], "kind": "known_preflight"},
    ]
    return {
        "schema": "bondy_source_status_duplicate_gate_tip_continuity_v3_3",
        "kind": "source_status_duplicate_gate",
        "status": "PASS",
        "checks": {key: True for key in search.LIVE_GATE_CHECKS},
        "campaign": {"commit": "c" * 40, "tree": "d" * 40},
        "pinned_upstream": {"commit": pinned, "tree": pinned_tree, "path": live_gate.TARGET_PATH, "blob": "5" * 40},
        "live_upstream": continuity["live"], "continuity": continuity,
        "open_pr_dependency_path_matches": [],
        "open_pr_target_path_matches": [],
        "bracket_snapshot_before": snapshot,
        "bracket_snapshot_after": json.loads(json.dumps(snapshot)),
        "graphql_rate_limit_observations": {
            "before": [{"cost": 1, "remaining": 100, "reset_at": "t"}],
            "after": [{"cost": 1, "remaining": 90, "reset_at": "t"}],
        },
        "local_history_hits": [row["commit"] for row in local_identities],
        "local_history_identities": local_identities,
    }


def sealed_attestation_fixture(attestation: dict[str, object]) -> dict[str, object]:
    continuity = attestation["continuity"]
    return {
        "live_gate": {"schema": "bondy_source_status_duplicate_gate_tip_continuity_v3_3"},
        "upstream": attestation["pinned_upstream"],
        "source_sha256": attestation["continuity"]["target"]["sha256"],
        "semantic_closure": {
            "count": continuity["closure_count"], "sha256": continuity["closure_sha256"],
            "toolchain_sha256": continuity["toolchain_sha256"],
            "external_revisions_sha256": continuity["external_revisions_sha256"],
        },
    }


def post_target_safeguard_fixture(attestation: dict[str, object]) -> dict[str, object]:
    source_raw = verify.canonical_bytes(attestation)
    return {
        "schema": "bondy_post_target_status_collision_safeguard_v1",
        "kind": "post_target_status_collision_safeguard",
        "status": "PASS",
        "checks": {
            "live_main_unchanged_after_target": True,
            "fresh_target_blob_and_declaration_unchanged_after_target": True,
            "complete_status_surface_unchanged_after_target": True,
            "complete_open_pr_bindings_after_target": True,
            "no_open_pr_touches_exact_target_path_after_target": True,
            "post_target_graphql_reserve": True,
        },
        "campaign": attestation["campaign"],
        "source_attestation_sha256": hashlib.sha256(source_raw).hexdigest(),
        "pre_gate_snapshot_sha256": search.canonical_sha256(attestation["bracket_snapshot_after"]),
        "post_target_snapshot": json.loads(json.dumps(attestation["bracket_snapshot_after"])),
        "fresh_target": {key: attestation["continuity"]["target"][key] for key in ("path", "type", "blob", "bytes", "sha256")},
        "fresh_declaration": attestation["continuity"]["declaration"],
        "open_pr_target_path_matches": [],
        "graphql_rate_limit_observations": [{"cost": 1, "remaining": 80, "reset_at": "t"}],
    }


class SourceAndGrammarTests(unittest.TestCase):
    def test_s44_source_control_is_exact_minus_one(self) -> None:
        row = construct.source_control()
        self.assertEqual((row["k"], row["t"], row["delta_h"], row["delta_g"]), (4, 4, 3, 7))
        self.assertEqual(row["threshold"], {"numerator": 36, "denominator": 5, "ceiling": 8})
        self.assertEqual(row["scaled_degree_residual"], -1)

    def test_catalogue_is_loopless_two_factor_with_five_components(self) -> None:
        for quotient in range(len(construct.QUOTIENT_CATALOGUE)):
            for permutation in range(len(construct.PORT_PERMUTATIONS)):
                factor = construct.cross_factor(quotient, permutation)
                self.assertEqual(sorted(dict(factor.degree()).values()), [2] * 20)
                self.assertEqual(nx.number_connected_components(factor), 5)
                self.assertTrue(all(u // 4 != v // 4 for u, v in factor.edges()))

    def test_constructor_replays_only_declared_balanced_changes(self) -> None:
        graph, metadata = construct.construct_row((0, 1, 2, 0, 1), 2, 1)
        verdict, gate = construct.constructor_gate(graph, metadata)
        self.assertIn(verdict, {"APPLICABLE", "KNOWN_PROOF_DOMAIN"})
        self.assertEqual(sorted(dict(graph.degree()).values()), [4] * 20)
        self.assertEqual(len(metadata["deleted_edges"]), 10)
        self.assertEqual(len(metadata["added_edges"]), 20)
        self.assertEqual(gate.get("reason"), None)

    def test_noop_and_naive_neutral_factor_are_rejected_before_target(self) -> None:
        graph, metadata = construct.construct_row((0, 0, 0, 0, 0), 0, 0)
        neutral = dict(metadata)
        # Declaring no deletions exposes an integrity failure rather than a row.
        neutral["deleted_edges"] = []
        verdict, gate = construct.constructor_gate(graph, neutral)
        self.assertEqual((verdict, gate["reason"]), ("GATE_FAIL", "undeclared_edge_change"))
        four_cycle_factor = nx.cycle_graph(20)
        neutral["deleted_edges"] = metadata["deleted_edges"]
        neutral["added_edges"] = construct.edge_list(four_cycle_factor)
        altered = construct.source_seed()
        altered.remove_edges_from(metadata["deleted_edges"])
        altered.add_edges_from(neutral["added_edges"])
        verdict, gate = construct.constructor_gate(altered, neutral)
        self.assertNotEqual(verdict, "APPLICABLE")

    def test_claw_free_domain_check_is_exact(self) -> None:
        complete = nx.complete_graph(24)
        self.assertIsNone(construct.induced_claw(complete))
        graph, metadata = construct.construct_row((0, 1, 2, 0, 1), 2, 1)
        verdict, gate = construct.constructor_gate(graph, metadata)
        if verdict == "APPLICABLE":
            witness = gate["induced_claw"]
            center, leaves = witness[0], witness[1:]
            joined = construct.join_separator(graph)
            self.assertTrue(all(joined.has_edge(center, leaf) for leaf in leaves))
            self.assertTrue(all(not joined.has_edge(a, b) for a, b in __import__("itertools").combinations(leaves, 2)))

    def test_connectivity_deletion_audit_covers_every_set_below_four(self) -> None:
        audit = construct.universal_join_connectivity_audit()
        self.assertEqual(audit["sets_checked"], 2325)
        self.assertEqual(audit["sets_checked"], audit["expected_sets"])

    def test_constructor_prefix_is_deterministic_and_deduplicated(self) -> None:
        first = list(construct.generate(24))
        second = list(construct.generate(24))
        self.assertEqual(first, second)
        accepted = [row for row in first if row["constructor_verdict"] == "APPLICABLE"]
        labelled = [row["gate"]["labelled_sha256"] for row in accepted]
        graph6 = [row["gate"]["graph6"] for row in accepted]
        self.assertEqual(len(labelled), len(set(labelled)))
        self.assertEqual(len(graph6), len(set(graph6)))


class TargetIsolationTests(unittest.TestCase):
    def test_workflow_dispatch_strings_never_enter_shell_source(self) -> None:
        workflow = (ROOT / ".github/workflows/bondy-longest-cycles-development.yml").read_text()
        lines = workflow.splitlines()
        run_bodies: list[str] = []
        index = 0
        while index < len(lines):
            if lines[index].lstrip() == "run: |":
                indentation = len(lines[index]) - len(lines[index].lstrip())
                index += 1
                body: list[str] = []
                while index < len(lines) and (not lines[index].strip() or len(lines[index]) - len(lines[index].lstrip()) > indentation):
                    body.append(lines[index])
                    index += 1
                run_bodies.append("\n".join(body))
                continue
            index += 1
        shell_source = "\n".join(run_bodies)
        self.assertNotIn("${{ inputs.", shell_source)
        self.assertIn('--campaign-commit "$CAMPAIGN_COMMIT"', shell_source)
        self.assertNotIn("inputs.activation_token", workflow)
        self.assertNotIn("--activation-token", workflow)
        self.assertIn("BONDY_V33_ACTIVATION_TOKEN: ${{ secrets.BONDY_V33_ACTIVATION_TOKEN }}", workflow)
        self.assertIn("timeout-minutes: 8", workflow)
        self.assertEqual(workflow.count("timeout --signal=TERM --kill-after=6s 60s"), 13)
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn('if test "$target_code" -ne 0 || test "$final_code" -ne 0 || test -z "$expected_status"; then', workflow)
        self.assertIn('if test "$accepted_status" != "$expected_status"; then', workflow)
        self.assertEqual(workflow.count("scripts/prospective_bondy_gate.py"), 2)
        self.assertEqual(workflow.count("--source-attestation /tmp/source-status-attestation.json"), 3)
        self.assertEqual(workflow.count("--post-target-safeguard /tmp/bondy-post-target-safeguard.json"), 2)
        self.assertIn("bondy_enabled_evidence_manifest_v1", workflow)
        self.assertIn("if-no-files-found: error", workflow)
        freeze_verifier = (ROOT / "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/verify_freeze.py").read_text()
        self.assertIn('if set(registry.get("sha256", {})) != REQUIRED_FREEZE_PATHS:', freeze_verifier)
        self.assertIn("CAMPAIGN_COMMIT: ${{ inputs.campaign_commit }}", workflow)

        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "injected"
            malicious = "bad'\nprintf injected > " + str(marker) + "\n"
            environment = dict(os.environ, CAMPAIGN_COMMIT=malicious)
            completed = subprocess.run(
                [
                    "bash",
                    "-c",
                    "python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "
                    '--campaign-commit "$CAMPAIGN_COMMIT"',
                ],
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(completed.stdout), ["--campaign-commit", malicious])
        self.assertFalse(marker.exists())

        failed = subprocess.run(
            ["bash", "-c", 'set +e; target_code=124; final_code=0; expected_status=TERMINAL_VERIFIED; if test "$target_code" -ne 0 || test "$final_code" -ne 0 || test -z "$expected_status"; then exit 1; fi; exit 0'],
            check=False,
        )
        self.assertEqual(failed.returncode, 1)

    def test_constructor_source_contains_no_target_evaluator(self) -> None:
        source = (ROOT / "scripts/prospective_bondy_construct.py").read_text()
        tree = ast.parse(source)
        function_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        forbidden = {"target_evaluate", "maximize_q4", "circumference", "path_cover", "pcov4"}
        self.assertTrue(function_names.isdisjoint(forbidden))

    def test_constructor_tests_do_not_call_proposed_candidate_target(self) -> None:
        with mock.patch.object(search, "target_evaluate", side_effect=AssertionError("target called")), mock.patch.object(
            search, "EndpointPathCoverDP", side_effect=AssertionError("path-cover target called")
        ):
            rows = list(construct.generate(12))
            self.assertEqual(len(rows), 12)

    def test_execution_lock_fails_before_attestation_or_target(self) -> None:
        args = types.SimpleNamespace(
            enable_target=True,
            campaign_commit="0" * 40,
        )
        with mock.patch.dict(os.environ, {"BONDY_V33_ACTIVATION_TOKEN": "BONDY_TARGET_DISABLED"}):
            with self.assertRaisesRegex(RuntimeError, "TARGET_EXECUTION_DISABLED"):
                search.unlock(args)

    def test_activation_secret_cli_transport_and_serialization_are_rejected(self) -> None:
        source = (ROOT / "scripts/prospective_bondy_search.py").read_text()
        self.assertNotIn('parser.add_argument("--activation-token"', source)
        self.assertIn('os.environ.get("BONDY_V33_ACTIVATION_TOKEN", "")', source)
        self.assertIn("ACTIVATION_TOKEN_CLI_TRANSPORT_FORBIDDEN", source)
        canary = "SENSITIVE_ACTIVATION_CANARY_NEVER_SERIALIZE"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cli = subprocess.run(
                ["python3", str(ROOT / "scripts/prospective_bondy_search.py"), "--activation-token", canary],
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            self.assertNotEqual(cli.returncode, 0)
            self.assertNotIn(canary, cli.stdout + cli.stderr)
            self.assertEqual(list(root.iterdir()), [])

            paths = {name: root / name for name in ("source.json", "ledger.jsonl", "candidate.json", "terminal.json", "replay")}
            environment = dict(os.environ, BONDY_V33_ACTIVATION_TOKEN=canary)
            env = subprocess.run(
                [
                    "python3", str(ROOT / "scripts/prospective_bondy_search.py"), "--enable-target",
                    "--campaign-commit", "0" * 40, "--source-attestation", str(paths["source.json"]),
                    "--ledger", str(paths["ledger.jsonl"]), "--candidate", str(paths["candidate.json"]),
                    "--terminal", str(paths["terminal.json"]), "--replay-binary", str(paths["replay"]),
                ],
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            self.assertNotEqual(env.returncode, 0)
            serialized = (env.stdout + env.stderr).encode("utf-8") + b"".join(path.read_bytes() for path in root.iterdir() if path.is_file())
            self.assertNotIn(canary.encode("ascii"), serialized)
            self.assertEqual(json.loads(paths["terminal.json"].read_text())["status"], "GATE_FAIL")

    def test_activation_environment_hashes_exact_bytes_without_trimming(self) -> None:
        token = "synthetic-boundary-token"
        manifest = {
            "target_execution_lock": {
                "activation_token_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
                "token_provisioned": True,
            },
            "runtime": {"python_version": __import__("sys").version.split()[0], "networkx_version": nx.__version__},
        }
        args = types.SimpleNamespace(enable_target=True, campaign_commit="a" * 40)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            search.atomic_json(path, manifest)
            git = lambda *arguments: "a" * 40 if arguments == ("rev-parse", "HEAD") else ""
            with mock.patch.object(search, "MANIFEST", path), mock.patch.object(search, "git", side_effect=git), mock.patch.object(
                search.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)
            ):
                with mock.patch.dict(os.environ, {"BONDY_V33_ACTIVATION_TOKEN": token}):
                    self.assertEqual(search.unlock(args), manifest)
                with mock.patch.dict(os.environ, {"BONDY_V33_ACTIVATION_TOKEN": token + "\n"}):
                    with self.assertRaisesRegex(RuntimeError, "exact_activation_token_mismatch"):
                        search.unlock(args)

    def test_v33_activation_digest_is_rotated_and_historical_digest_cannot_unlock(self) -> None:
        manifest = json.loads((ROOT / "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/manifest.json").read_text())
        current = manifest["target_execution_lock"]["activation_token_sha256"]
        historical_v32 = "09d64624c2861b21d5883cfd276ce49eebce7d9c6f61e47193d50bf894be8e51"
        self.assertEqual(current, "0fb0d55f32eb0cecd7e549a45dba8d5095e073737fe39efbd226c79d6a539d5a")
        self.assertNotEqual(current, historical_v32)
        self.assertEqual(manifest["target_execution_lock"]["exact_preimage_bytes"], 64)
        self.assertIs(manifest["target_execution_lock"]["newline_terminated"], False)
        self.assertEqual(manifest["target_execution_lock"]["actions_secret_name"], "BONDY_V33_ACTIVATION_TOKEN")
        self.assertIs(manifest["target_execution_lock"]["actions_secret_required"], True)
        self.assertEqual(manifest["target_execution_lock"]["state"], "V33_OPEN_PR_SPLIT_GUARD_HASH_PROVISIONED_ACTIONS_SECRET_REQUIRED_DEFAULT_DISABLED")

    def test_v33_live_attestation_requires_full_bracket_and_bindings(self) -> None:
        attestation = live_attestation_fixture()
        manifest = sealed_attestation_fixture(attestation)
        search.validate_live_attestation(attestation, manifest)
        attestation["bracket_snapshot_before"]["open_pull_binding_surface"]["bindings"][0]["head_sha"] = "mutated"
        with self.assertRaisesRegex(RuntimeError, "missing or drifted"):
            search.validate_live_attestation(attestation, manifest)

    def test_structurally_complete_zero_open_set_is_accepted(self) -> None:
        attestation = live_attestation_fixture(empty=True)
        search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_dependency_path_touch_is_non_gating_but_telemetry_is_exact(self) -> None:
        dependency = "FormalConjectures/Imported.lean"
        attestation = live_attestation_fixture()
        binding = attestation["bracket_snapshot_before"]["open_pull_binding_surface"]["bindings"][0]
        binding["changed_paths"] = [dependency]
        binding["changed_paths_sha256"] = search.canonical_sha256(binding["changed_paths"])
        attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
        attestation["open_pr_dependency_path_matches"] = [{"number": 1, "paths": [dependency]}]
        search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

        for forged in ([], [{"number": 1, "paths": ["lean-toolchain"]}]):
            mutated = json.loads(json.dumps(attestation))
            mutated["open_pr_dependency_path_matches"] = forged
            with self.assertRaisesRegex(RuntimeError, "target/dependency telemetry"):
                search.validate_live_attestation(mutated, sealed_attestation_fixture(mutated))

    def test_exact_target_collision_is_recomputed_for_current_and_previous_paths(self) -> None:
        for paths in ([live_gate.TARGET_PATH], [live_gate.TARGET_PATH, "FormalConjectures/RenamedDestination.lean"]):
            for telemetry in ([], [{"number": 1, "paths": [live_gate.TARGET_PATH]}]):
                attestation = live_attestation_fixture()
                binding = attestation["bracket_snapshot_before"]["open_pull_binding_surface"]["bindings"][0]
                binding["changed_paths"] = sorted(paths)
                binding["changed_paths_sha256"] = search.canonical_sha256(binding["changed_paths"])
                attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
                attestation["open_pr_target_path_matches"] = telemetry
                with self.assertRaisesRegex(RuntimeError, "target/dependency telemetry"):
                    search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_post_target_safeguard_verifier_binds_complete_fresh_snapshot(self) -> None:
        attestation = live_attestation_fixture()
        source_raw = verify.canonical_bytes(attestation)
        safeguard = post_target_safeguard_fixture(attestation)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "safeguard.json"
            verify.atomic_json(path, safeguard)
            self.assertEqual(verify.validate_post_target_safeguard(path, attestation, source_raw), hashlib.sha256(path.read_bytes()).hexdigest())

            mutations = (
                lambda row: row["post_target_snapshot"]["continuity"]["target"].update({"blob": "0" * 40}),
                lambda row: row["post_target_snapshot"]["continuity"]["declaration"].update({"declaration_count": 2}),
                lambda row: row["fresh_target"].update({"blob": "0" * 40}),
                lambda row: row["fresh_declaration"].update({"declaration_count": 2}),
                lambda row: row["post_target_snapshot"]["known_issue"].update({"state": "open"}),
                lambda row: row["post_target_snapshot"]["searches"].update({'repo:google-deepmind/formal-conjectures "BondyLongestCycles"': [999]}),
                lambda row: row.update({"open_pr_target_path_matches": [{"number": 1, "paths": [live_gate.TARGET_PATH]}]}),
                lambda row: row.update({"source_attestation_sha256": "0" * 64}),
            )
            for mutate in mutations:
                forged = json.loads(json.dumps(safeguard))
                mutate(forged)
                verify.atomic_json(path, forged)
                with self.assertRaisesRegex(RuntimeError, "post-target status/collision safeguard drift"):
                    verify.validate_post_target_safeguard(path, attestation, source_raw)

    def test_forged_identity_only_file_binding_is_rejected(self) -> None:
        attestation = live_attestation_fixture(identity_only_binding=True)
        with self.assertRaisesRegex(RuntimeError, "file binding schema drift"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_superseded_attestations_are_rejected_without_reinterpretation(self) -> None:
        for schema in (
            "bondy_source_status_attestation_v1",
            "bondy_source_status_duplicate_gate_bracketed_single_scan_v2",
            "bondy_source_status_duplicate_gate_tip_continuity_v3_2",
        ):
            attestation = live_attestation_fixture()
            attestation["schema"] = schema
            with self.assertRaisesRegex(RuntimeError, "missing or drifted"):
                search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_forged_empty_protected_paths_is_rejected_before_target(self) -> None:
        attestation = live_attestation_fixture()
        attestation["continuity"]["protected_paths"] = []
        attestation["bracket_snapshot_before"]["continuity"]["canonical_sha256"] = search.canonical_sha256(attestation["continuity"])
        attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
        with self.assertRaisesRegex(RuntimeError, "delta or binding completeness"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_binding_identity_state_oid_count_and_campaign_are_strict(self) -> None:
        mutations = (("number", 0), ("state", "CLOSED"), ("node_id", ""), ("head_sha", "abc"), ("changed_files", 999))
        for key, value in mutations:
            attestation = live_attestation_fixture()
            attestation["bracket_snapshot_before"]["open_pull_binding_surface"]["bindings"][0][key] = value
            attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
            with self.assertRaisesRegex(RuntimeError, "file binding drift"):
                search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))
        attestation = live_attestation_fixture()
        attestation["campaign"]["tree"] = "short"
        with self.assertRaisesRegex(RuntimeError, "missing or drifted"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_run_rejects_attestation_campaign_tree_before_target(self) -> None:
        attestation = live_attestation_fixture()
        manifest = sealed_attestation_fixture(attestation)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            search.atomic_json(source, attestation)
            args = types.SimpleNamespace(source_attestation=source, campaign_commit="c" * 40)
            with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="e" * 40), mock.patch.object(
                search, "target_evaluate", side_effect=AssertionError("target called")
            ):
                with self.assertRaisesRegex(RuntimeError, "campaign commit/tree drift"):
                    search.run(args)

    def test_run_rejects_bad_duplicate_and_unsorted_delta_before_target(self) -> None:
        variants = (
            [{"status": "NOT_A_GIT_STATUS", "path": "unrelated"}],
            [{"status": "M", "path": "unrelated"}, {"status": "M", "path": "unrelated"}],
            [{"status": "M", "path": "z"}, {"status": "A", "path": "a"}],
        )
        for delta in variants:
            attestation = live_attestation_fixture()
            attestation["continuity"]["delta"] = delta
            attestation["continuity"]["delta_sha256"] = search.canonical_sha256(delta)
            attestation["continuity"]["commits"][0]["changed_paths"] = sorted({row["path"] for row in delta})
            attestation["bracket_snapshot_before"]["continuity"]["canonical_sha256"] = search.canonical_sha256(attestation["continuity"])
            attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
            manifest = sealed_attestation_fixture(attestation)
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "source.json"
                search.atomic_json(source, attestation)
                args = types.SimpleNamespace(source_attestation=source, campaign_commit="c" * 40)
                with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="d" * 40), mock.patch.object(
                    search, "target_evaluate", side_effect=AssertionError("target called")
                ):
                    with self.assertRaisesRegex(RuntimeError, "delta or binding completeness"):
                        search.run(args)

    def test_run_rejects_invalid_pr_number_and_local_history_before_target(self) -> None:
        for mutation in ("number", "history"):
            attestation = live_attestation_fixture()
            if mutation == "number":
                attestation["bracket_snapshot_before"]["open_pull_binding_surface"]["bindings"][0]["number"] = 0
                attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
            else:
                attestation["local_history_hits"] = None
                attestation["local_history_identities"] = "bogus"
            manifest = sealed_attestation_fixture(attestation)
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "source.json"
                search.atomic_json(source, attestation)
                args = types.SimpleNamespace(source_attestation=source, campaign_commit="c" * 40)
                with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="d" * 40), mock.patch.object(
                    search, "target_evaluate", side_effect=AssertionError("target called")
                ):
                    with self.assertRaisesRegex(RuntimeError, "file binding drift|local contamination"):
                        search.run(args)

    def test_run_rejects_too_few_or_too_many_freeze_introducers_before_target(self) -> None:
        for count in (4, 6):
            attestation = live_attestation_fixture()
            identities = attestation["local_history_identities"]
            freeze_indexes = [index for index, row in enumerate(identities) if row["kind"] == "freeze_introducer"]
            if count == 4:
                del identities[freeze_indexes[-1]]
            else:
                identities.insert(
                    freeze_indexes[-1] + 1,
                    {"commit": "9" * 40, "subject": "forged extra freeze", "paths": ["scripts/prospective_bondy_gate.py"], "kind": "freeze_introducer"},
                )
            attestation["local_history_hits"] = [row["commit"] for row in identities]
            manifest = sealed_attestation_fixture(attestation)
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "source.json"
                search.atomic_json(source, attestation)
                args = types.SimpleNamespace(source_attestation=source, campaign_commit="c" * 40)
                with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="d" * 40), mock.patch.object(
                    search, "target_evaluate", side_effect=AssertionError("target called")
                ):
                    with self.assertRaisesRegex(RuntimeError, "local contamination exact history"):
                        search.run(args)

    def test_run_rejects_known_graph_rotation_identity_mutations_before_target(self) -> None:
        for field in ("commit", "subject", "paths"):
            attestation = live_attestation_fixture()
            identities = attestation["local_history_identities"]
            row = next(item for item in identities if item["kind"] == "known_graph_rotation")
            if field == "commit":
                row["commit"] = "5" * 40
                attestation["local_history_hits"] = [item["commit"] for item in identities]
            elif field == "subject":
                row["subject"] = "research: mutated graph rotation"
            else:
                row["paths"] = ["results/expansion/live-search-2026-08-14/mutated-graph-rotation.md"]
            manifest = sealed_attestation_fixture(attestation)
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "source.json"
                search.atomic_json(source, attestation)
                args = types.SimpleNamespace(source_attestation=source, campaign_commit="c" * 40)
                with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="d" * 40), mock.patch.object(
                    search, "target_evaluate", side_effect=AssertionError("target called")
                ):
                    with self.assertRaisesRegex(RuntimeError, "local contamination exact history"):
                        search.run(args)

    def test_stale_output_prevents_target_evaluation(self) -> None:
        attestation = live_attestation_fixture()
        manifest = sealed_attestation_fixture(attestation)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            search.atomic_json(source, attestation)
            ledger = root / "ledger.jsonl"
            ledger.write_text("stale-unverifiable-ledger", encoding="ascii")
            args = types.SimpleNamespace(
                source_attestation=source, campaign_commit="c" * 40, ledger=ledger,
                candidate=root / "candidate.json", terminal=root / "terminal.json",
            )
            with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="d" * 40), mock.patch.object(
                search, "target_evaluate", side_effect=AssertionError("target called")
            ):
                with self.assertRaisesRegex(RuntimeError, "output path already exists"):
                    search.run(args)
            ledger.unlink()
            args.candidate = ledger
            with mock.patch.object(search, "unlock", return_value=manifest), mock.patch.object(search, "git", return_value="d" * 40), mock.patch.object(
                search, "target_evaluate", side_effect=AssertionError("target called")
            ):
                with self.assertRaisesRegex(RuntimeError, "not distinct"):
                    search.run(args)

    def test_changed_file_expansion_bound_and_quota_order_are_strict(self) -> None:
        attestation = live_attestation_fixture()
        binding = attestation["bracket_snapshot_before"]["open_pull_binding_surface"]["bindings"][0]
        binding["changed_paths"] = [f"p/{index}" for index in range(3)]
        binding["changed_paths_sha256"] = search.canonical_sha256(binding["changed_paths"])
        attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
        with self.assertRaisesRegex(RuntimeError, "file binding drift"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))
        attestation = live_attestation_fixture()
        attestation["graphql_rate_limit_observations"]["before"] = [
            {"cost": 1, "remaining": 100, "reset_at": "t"}, {"cost": 1, "remaining": 90, "reset_at": "t"}
        ]
        with self.assertRaisesRegex(RuntimeError, "noncanonical order"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_terminal_schema_rejects_extra_fields(self) -> None:
        terminal = {"schema": "bondy_terminal_v3", "kind": "terminal", "status": "CAP_PREFIX", "handoff": {}, "applicable": 0, "evaluated": 0, "ledger_head": "0" * 64, "extra": True}
        with self.assertRaisesRegex(RuntimeError, "unknown or misplaced"):
            verify.verify_terminal(terminal)

    def test_search_replay_stdout_and_binary_hashes_are_recomputed(self) -> None:
        record = {"status": "Q4_UPPER_BOUND_VERIFIED", "deletion_sets": 1351, "pc_table_bytes": 1048576}
        stdout = b'{"status":"Q4_UPPER_BOUND_VERIFIED","deletion_sets":1351,"pc_table_bytes":1048576}\n'
        source_sha = __import__("hashlib").sha256((ROOT / "scripts/prospective_bondy_replay.cpp").read_bytes()).hexdigest()
        audit = {
            "record": record, "pc_table_sha256": "c" * 64,
            "process_audit": {
                "pid": 7, "returncode": 0, "timed_out": False, "elapsed_seconds_millis": 1,
                "process_group_isolated": True, "process_group_reaped": True, "binary_sha256": "b" * 64,
                "source_sha256": source_sha, "stdout_sha256": __import__("hashlib").sha256(stdout).hexdigest(),
                "reported_status": "Q4_UPPER_BOUND_VERIFIED",
            },
        }
        process = verify.validate_search_replay_audit(audit)
        verify.require_replay_binary_binding(process, {"binary_sha256": "b" * 64})
        audit["process_audit"]["stdout_sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "provenance drift"):
            verify.validate_search_replay_audit(audit)
        with self.assertRaisesRegex(RuntimeError, "binary drift"):
            verify.require_replay_binary_binding(process, {"binary_sha256": "0" * 64})

    def test_ledger_cannot_append_after_seal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = search.DurableLedger(Path(directory) / "ledger.jsonl")
            ledger.append({"kind": "fixture"})
            ledger.seal()
            with self.assertRaisesRegex(RuntimeError, "after durable"):
                ledger.append({"kind": "forbidden"})

    def test_atomic_replace_failure_does_not_publish_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "candidate.json"
            with mock.patch.object(os, "replace", side_effect=OSError("synthetic rename failure")):
                with self.assertRaisesRegex(OSError, "synthetic rename"):
                    search.atomic_json(destination, {"status": "CANDIDATE_FOUND"})
            self.assertFalse(destination.exists())

    def test_cpp_replay_rejects_malformed_and_trailing_tokens_before_dp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "replay"
            subprocess.run(
                ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror",
                 str(ROOT / "scripts/prospective_bondy_replay.cpp"), "-o", str(binary)],
                check=True,
                timeout=30,
            )
            for payload in ("0 1\nnot-an-edge\n", "0 1 trailing-token\n"):
                edge_file = Path(directory) / "malformed.edges"
                table_file = Path(directory) / "must-not-exist.bin"
                edge_file.write_text(payload, encoding="ascii")
                completed = subprocess.run(
                    [str(binary), str(edge_file), str(table_file)],
                    text=True,
                    capture_output=True,
                    timeout=5,
                )
                self.assertEqual(completed.returncode, 3)
                self.assertIn('"status":"GATE_FAIL"', completed.stdout)
                self.assertIn("malformed edge line", completed.stdout)
                self.assertFalse(table_file.exists())

    def test_nonzero_independent_replay_is_gate_failure_not_timeout(self) -> None:
        fake = mock.Mock()
        fake.pid = 123456
        fake.returncode = 2
        fake.communicate.return_value = ('{"status":"REJECT_UPPER_BOUND","removed_mask":1}\n', None)
        fake.poll.return_value = 2
        with mock.patch.object(subprocess, "Popen", return_value=fake):
            with self.assertRaisesRegex(RuntimeError, "nonzero logical/internal exit"):
                search.independent_upper_replay(Path("/bin/true"), [], "0" * 64, 1.0)

    def test_process_group_exit_race_is_always_reaped(self) -> None:
        for helper in (search.terminate_and_reap, verify.terminate_and_reap):
            process = mock.Mock()
            process.pid = 123
            process.poll.side_effect = [None, 0]
            process.communicate.return_value = ("done", None)
            with mock.patch.object(os, "killpg", side_effect=ProcessLookupError):
                self.assertEqual(helper(process), "done")
            process.communicate.assert_called_once()

    def test_synthetic_upper_rejection_counter_witness_replays(self) -> None:
        graph = nx.path_graph(20)
        kept = list(range(1, 20))
        result = {
            "candidate": False,
            "classification": "Q4_UPPER_BOUND_REJECTED",
            "upper_deletion_sets_completed": 2,
            "upper_rejection": {
                "X": [0],
                "removed_mask": 1,
                "kept_mask": (1 << 20) - 2,
                "pc_H_minus_X": 1,
                "cover_H_minus_X": [kept],
            },
        }
        self.assertEqual(verify.validate_upper_rejection(graph, result), {"removed": 1, "paths": 1})

    def test_full_ledger_rejects_unrecognized_fake_target_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = search.DurableLedger(Path(directory) / "ledger.jsonl")
            handoff = {"schema": "bondy_campaign_handoff_v1", "campaign_commit": "c" * 40, "source_attestation_sha256": "a" * 64}
            ledger.append({"kind": "campaign_handoff", "handoff": handoff})
            ledger.append({"kind": "source_control", "record": construct.source_control()})
            applicable = 0
            for row in construct.generate(construct.ROW_LIMIT):
                ledger.append({k: v for k, v in row.items() if k not in ("edges_h", "roles")})
                if row["constructor_verdict"] == "APPLICABLE":
                    applicable += 1
                    ledger.append({
                        "kind": "target_evaluation",
                        "row_index": row["row_index"],
                        "result": {
                            "candidate": False,
                            "classification": "UNRECOGNIZED_FAKE_RESULT",
                            "algorithm": "python_endpoint_path_cover_dp_v1",
                            "dp_digests": {"pc_table_sha256": "0" * 64, "endpoint_table_sha256": "0" * 64},
                            "upper_deletion_sets_completed": 1351,
                            "evaluation_seconds_millis": 0,
                        },
                    })
            ledger.seal()
            records, head = verify.verify_ledger(ledger.path)
            self.assertEqual(sum(verify.semantic_payload(record).get("kind") == "constructor_row" for record in records), 96)
            artifact = {
                "status": "DOMAIN_EXHAUSTED",
                "applicable": applicable,
                "evaluated": applicable,
                "ledger_head": head,
                "handoff": handoff,
            }
            with self.assertRaisesRegex(RuntimeError, "missing or unknown target evaluation classification"):
                verify.verify_ledger_semantics(records, artifact)

    def test_complete_joined_edge_list_round_trips_without_target_evaluation(self) -> None:
        peripheral, _ = construct.construct_row((0, 1, 2, 0, 1), 2, 1)
        joined = construct.join_separator(peripheral)
        edges_g = construct.edge_list(joined)
        self.assertEqual(len(edges_g), 126)
        self.assertEqual(construct.edge_list(construct.graph_from_edges(24, edges_g)), edges_g)


class LiveGateConcurrencyTests(unittest.TestCase):
    def test_import_parser_accepts_only_safe_component_quoted_modules(self) -> None:
        self.assertEqual(
            live_gate.parse_import_module("public import FormalConjecturesForMathlib.Geometry.«2d»"),
            "FormalConjecturesForMathlib.Geometry.2d",
        )
        self.assertEqual(live_gate.parse_import_module("import Batteries.Data.Array.Merge"), "Batteries.Data.Array.Merge")
        self.assertEqual(live_gate.parse_import_module("meta import Init.Data.String.Legacy"), "Init.Data.String.Legacy")
        self.assertEqual(live_gate.parse_import_module("public meta import Qq.Typ"), "Qq.Typ")
        for value in (
            "import Formal.Geometry.«2d",
            "import Formal.Geometry.2d»",
            "import Formal.Geometry.«2.d»",
            "import Formal.Geometry.«»",
            "import Formal.Geometry.«../x»",
            "import Mathlib Qq",
            "import Qq -- trailing",
            "import  Mathlib",
            "import\tMathlib",
            "public  import Mathlib",
            "public\timport Mathlib",
            "meta  import Mathlib",
            "public meta  import Mathlib",
            "meta meta import Mathlib",
            "public meta meta import Mathlib",
            "import",
        ):
            with self.assertRaisesRegex(RuntimeError, "ambiguous Lean import"):
                live_gate.parse_import_module(value)
        for value in ("import all", "import all Mathlib", "public meta import all Mathlib"):
            with self.assertRaisesRegex(RuntimeError, "import all"):
                live_gate.parse_import_module(value)

    def test_import_closure_accepts_exact_frozen_external_prefixes_and_quoted_internal_path(self) -> None:
        root = "Formal/Root.lean"
        quoted = "Formal/Geometry/2d.lean"
        contents = {
            root: b"public import Formal.Geometry.\xc2\xab2d\xc2\xbb\npublic meta import Qq.Typ\nimport Batteries.Data.Array.Merge\n",
            quoted: b"import Mathlib\nimport Lean\nmeta import Init.Data.String.Legacy\n",
        }

        def fake_entry(repo: Path, commit: str, path: str) -> tuple[dict[str, object], bytes]:
            raw = contents[path]
            return {"path": path, "mode": "100644", "type": "blob", "blob": "a" * 40, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}, raw

        def fake_run(args: list[str], **kwargs: object) -> object:
            imported = args[-1].split(":", 1)[1]
            return types.SimpleNamespace(returncode=0 if imported in contents else 1)

        with mock.patch.object(live_gate, "git_entry", side_effect=fake_entry), mock.patch.object(live_gate.subprocess, "run", side_effect=fake_run):
            closure = live_gate.resolve_import_closure(Path("/unused"), "c" * 40, root)
        self.assertEqual([entry["path"] for entry in closure], sorted([root, quoted]))

        contents[root] = b"import Unfrozen.Package\n"
        with mock.patch.object(live_gate, "git_entry", side_effect=fake_entry), mock.patch.object(live_gate.subprocess, "run", side_effect=fake_run):
            with self.assertRaisesRegex(RuntimeError, "unfrozen external Lean import prefix"):
                live_gate.resolve_import_closure(Path("/unused"), "c" * 40, root)

        adversarial = (
            b"import\tMathlib\n",
            b"import  Mathlib\n",
            b"public\timport Mathlib\n",
            b"public  import Mathlib\n",
            b"meta  import Mathlib\n",
            b"public meta  import Mathlib\n",
            b"meta meta import Mathlib\n",
            b"public meta meta import Mathlib\n",
            b"import all Mathlib\n",
            b"public meta import all Mathlib\n",
            b"import/-x-/ Mathlib\n",
            b"public/-x-/ import Mathlib\n",
            b"/-x-/ import Mathlib\n",
            b"public /- outer /- nested -/ comment -/ import Mathlib\n",
            b"import\nMathlib\n",
            b"public\nimport Mathlib\n",
            b"meta\nimport Mathlib\n",
            b"public meta\nimport Mathlib\n",
        )
        for raw in adversarial:
            contents[root] = raw
            with mock.patch.object(live_gate, "git_entry", side_effect=fake_entry), mock.patch.object(live_gate.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError, "Lean import"):
                    live_gate.resolve_import_closure(Path("/unused"), "c" * 40, root)

        contents[root] = b"/- prose mentioning import /- nested import -/ only -/\n-- import in line prose\nimport Mathlib\n"
        with mock.patch.object(live_gate, "git_entry", side_effect=fake_entry), mock.patch.object(live_gate.subprocess, "run", side_effect=fake_run):
            self.assertEqual([entry["path"] for entry in live_gate.resolve_import_closure(Path("/unused"), "c" * 40, root)], [root])

    def test_rest_commit_identity_uses_exact_documented_shape(self) -> None:
        real_shape = {"sha": "a" * 40, "commit": {"tree": {"sha": "b" * 40}}, "url": "ignored REST metadata"}
        self.assertEqual(live_gate.parse_rest_commit_identity(real_shape), {"commit": "a" * 40, "tree": "b" * 40})
        malformed = (
            {"sha": "a" * 40, "tree": {"sha": "b" * 40}},
            {"sha": "a" * 40, "commit": {}},
            {"sha": "a" * 40, "commit": {"tree": {"sha": "short"}}},
            {"sha": "a" * 40, "commit": {"tree": {"sha": "b" * 40}}, "tree": {"sha": "b" * 40}},
        )
        for value in malformed:
            with self.assertRaisesRegex(RuntimeError, "REST"):
                live_gate.parse_rest_commit_identity(value)

    def test_post_target_safeguard_rechecks_main_and_complete_status_collision_surface(self) -> None:
        attestation = live_attestation_fixture()
        live = attestation["live_upstream"]
        rest = {"sha": live["commit"], "commit": {"tree": {"sha": live["tree"]}}}
        target_raw = attestation["continuity"]["target_raw_utf8"].encode("utf-8")
        contents = {
            "path": live_gate.TARGET_PATH,
            "type": "file",
            "encoding": "base64",
            "content": __import__("base64").b64encode(target_raw).decode("ascii"),
            "sha": attestation["continuity"]["target"]["blob"],
            "size": len(target_raw),
        }
        rates = [{"cost": 1, "remaining": 80, "reset_at": "t"}]
        api = lambda path, token: contents if "/contents/" in path else rest
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            output = Path(directory) / "post.json"
            live_gate.atomic_json(source, attestation)
            stable = json.loads(json.dumps(attestation["bracket_snapshot_after"]))
            with mock.patch.object(live_gate, "api", side_effect=api), mock.patch.object(
                live_gate, "bracket_snapshot", return_value=(stable, rates)
            ):
                record = live_gate.run_post_target_safeguard(output, "token", source)
            self.assertEqual(record["status"], "PASS")
            self.assertEqual(record["open_pr_target_path_matches"], [])

            mutations = (
                lambda row: row["continuity"]["target"].update({"blob": "0" * 40}),
                lambda row: row["continuity"]["declaration"].update({"declaration_count": 2}),
                lambda row: row["known_issue"].update({"state": "open"}),
                lambda row: row["searches"].update({'repo:google-deepmind/formal-conjectures "BondyLongestCycles"': [999]}),
                lambda row: row["open_pull_binding_surface"]["bindings"][0]["changed_paths"].append(live_gate.TARGET_PATH),
            )
            for mutate in mutations:
                changed = json.loads(json.dumps(stable))
                mutate(changed)
                with mock.patch.object(live_gate, "api", side_effect=api), mock.patch.object(
                    live_gate, "bracket_snapshot", return_value=(changed, rates)
                ):
                    with self.assertRaisesRegex(RuntimeError, "post-target status/collision safeguard failed closed"):
                        live_gate.run_post_target_safeguard(output, "token", source)

            changed_contents = dict(contents)
            changed_contents["sha"] = "0" * 40
            changed_target_api = lambda path, token: changed_contents if "/contents/" in path else rest
            with mock.patch.object(live_gate, "api", side_effect=changed_target_api), mock.patch.object(
                live_gate, "bracket_snapshot", return_value=(stable, rates)
            ):
                with self.assertRaisesRegex(RuntimeError, "post-target status/collision safeguard failed closed"):
                    live_gate.run_post_target_safeguard(output, "token", source)

            changed_main = {"sha": "9" * 40, "commit": {"tree": {"sha": live["tree"]}}}
            changed_api = lambda path, token: contents if "/contents/" in path else changed_main
            with mock.patch.object(live_gate, "api", side_effect=changed_api), mock.patch.object(
                live_gate, "bracket_snapshot", return_value=(stable, rates)
            ):
                with self.assertRaisesRegex(RuntimeError, "post-target status/collision safeguard failed closed"):
                    live_gate.run_post_target_safeguard(output, "token", source)

    def test_v33_local_history_requires_exact_freeze_introducer_count(self) -> None:
        freezes = [character * 40 for character in "fba76"]
        extra_freeze = "9" * 40
        hits = [
            live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT,
            live_gate.KNOWN_REPIN_AUDIT_COMMIT,
            *freezes,
            live_gate.KNOWN_GRAPH_ROTATION_COMMIT,
            live_gate.KNOWN_PREFLIGHT_COMMIT,
        ]

        def exact_git(*args: str) -> str:
            commit = args[-1]
            if args[0] == "show":
                if commit == live_gate.KNOWN_REPIN_AUDIT_COMMIT:
                    return "research: audit Bondy upstream repin"
                if commit == live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT:
                    return "research: define Bondy tip continuity gate"
                if commit == live_gate.KNOWN_GRAPH_ROTATION_COMMIT:
                    return live_gate.KNOWN_GRAPH_ROTATION_SUBJECT
                return "freeze"
            if args[0] == "diff-tree":
                if commit == live_gate.KNOWN_REPIN_AUDIT_COMMIT:
                    return live_gate.KNOWN_REPIN_AUDIT_PATH
                if commit == live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT:
                    return live_gate.KNOWN_CONTINUITY_AUDIT_PATH
                if commit == live_gate.KNOWN_GRAPH_ROTATION_COMMIT:
                    return live_gate.KNOWN_GRAPH_ROTATION_PATH
                if commit in freezes or commit == extra_freeze:
                    return "scripts/prospective_bondy_gate.py"
                return "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md"
            raise AssertionError(args)

        with mock.patch.object(live_gate, "git", side_effect=exact_git):
            accepted, identities = live_gate.validate_local_contamination(hits)
            too_few, _ = live_gate.validate_local_contamination(hits[:2] + hits[3:])
            too_many, _ = live_gate.validate_local_contamination(hits[:2] + [extra_freeze] + hits[2:])
        self.assertTrue(accepted)
        self.assertFalse(too_few)
        self.assertFalse(too_many)
        self.assertEqual(
            [row["kind"] for row in identities],
            ["known_continuity_audit", "known_repin_audit", "freeze_introducer", "freeze_introducer", "freeze_introducer", "freeze_introducer", "freeze_introducer", "known_graph_rotation", "known_preflight"],
        )

    def test_v33_known_graph_rotation_hash_subject_and_path_are_exact(self) -> None:
        freezes = [character * 40 for character in "fba76"]
        baseline = [
            live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT,
            live_gate.KNOWN_REPIN_AUDIT_COMMIT,
            *freezes,
            live_gate.KNOWN_GRAPH_ROTATION_COMMIT,
            live_gate.KNOWN_PREFLIGHT_COMMIT,
        ]
        for mutation in ("hash", "subject", "path"):
            hits = list(baseline)
            if mutation == "hash":
                hits[hits.index(live_gate.KNOWN_GRAPH_ROTATION_COMMIT)] = "5" * 40

            def exact_git(*args: str) -> str:
                commit = args[-1]
                if args[0] == "show":
                    if commit == live_gate.KNOWN_REPIN_AUDIT_COMMIT:
                        return "research: audit Bondy upstream repin"
                    if commit == live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT:
                        return "research: define Bondy tip continuity gate"
                    if commit == live_gate.KNOWN_GRAPH_ROTATION_COMMIT:
                        return "mutated" if mutation == "subject" else live_gate.KNOWN_GRAPH_ROTATION_SUBJECT
                    return "freeze"
                if args[0] == "diff-tree":
                    if commit == live_gate.KNOWN_REPIN_AUDIT_COMMIT:
                        return live_gate.KNOWN_REPIN_AUDIT_PATH
                    if commit == live_gate.KNOWN_CONTINUITY_AUDIT_COMMIT:
                        return live_gate.KNOWN_CONTINUITY_AUDIT_PATH
                    if commit == live_gate.KNOWN_GRAPH_ROTATION_COMMIT:
                        return "mutated.md" if mutation == "path" else live_gate.KNOWN_GRAPH_ROTATION_PATH
                    if commit in freezes:
                        return "scripts/prospective_bondy_gate.py"
                    return "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md"
                raise AssertionError(args)

            with mock.patch.object(live_gate, "git", side_effect=exact_git):
                accepted, _ = live_gate.validate_local_contamination(hits)
            self.assertFalse(accepted, mutation)

    def test_open_pr_and_changed_file_pagination_are_complete(self) -> None:
        calls: list[str] = []

        def fake_api(path: str, token: str) -> object:
            self.assertEqual(token, "token")
            calls.append(path)
            if "/pulls?state=open" in path:
                page = int(path.rsplit("page=", 1)[1])
                return [pull_fixture(i) for i in range(1, 101)] if page == 1 else [pull_fixture(101)]
            if "/pulls/7/files" in path:
                page = int(path.rsplit("page=", 1)[1])
                return [{"filename": f"p/{i:03d}"} for i in range(100)] if page == 1 else [{"filename": "p/100"}]
            raise AssertionError(path)

        with mock.patch.object(live_gate, "api", side_effect=fake_api):
            self.assertEqual(len(live_gate.all_open_pulls("token")), 101)
            self.assertEqual(live_gate.changed_paths("token", 7), [f"p/{i:03d}" for i in range(101)])
        self.assertTrue(any("pulls?state=open&per_page=100&page=2" in path for path in calls))
        self.assertTrue(any("pulls/7/files?per_page=100&page=2" in path for path in calls))

    def test_single_file_binding_has_deterministic_order(self) -> None:
        pulls = [pull_fixture(9), pull_fixture(2), pull_fixture(5)]
        paths = {9: ["z", "a"], 2: ["d", "c"], 5: ["m", "b"]}
        first_identities = live_gate.open_pull_identities(pulls)
        second_identities = live_gate.open_pull_identities(list(reversed(pulls)))
        with mock.patch.object(live_gate, "changed_paths", side_effect=lambda token, number: paths[number]):
            first = live_gate.bind_changed_paths("token", first_identities)
            second = live_gate.bind_changed_paths("token", second_identities)
        self.assertEqual(first, second)
        self.assertEqual([row["number"] for row in first], [2, 5, 9])
        self.assertEqual([row["changed_paths"] for row in first], [["c", "d"], ["b", "m"], ["a", "z"]])

    def test_each_open_pr_file_catalogue_is_fetched_exactly_once(self) -> None:
        identities = live_gate.open_pull_identities([pull_fixture(2), pull_fixture(5), pull_fixture(9)])
        with mock.patch.object(live_gate, "changed_paths", return_value=["x"]) as scan:
            bindings = live_gate.bind_changed_paths("token", identities)
        self.assertEqual(len(bindings), 3)
        self.assertEqual(sorted(call.args[1] for call in scan.call_args_list), [2, 5, 9])
        self.assertEqual(scan.call_count, 3)

    def test_parallel_pull_worker_error_propagates_fail_closed(self) -> None:
        def paths(token: str, number: int) -> list[str]:
            if number == 5:
                raise RuntimeError("synthetic paginated API failure")
            return [str(number)]

        with mock.patch.object(live_gate, "changed_paths", side_effect=paths):
            with self.assertRaisesRegex(RuntimeError, "synthetic paginated API failure"):
                live_gate.bind_changed_paths(
                    "token", live_gate.open_pull_identities([pull_fixture(2), pull_fixture(5), pull_fixture(9)])
                )

    def test_non_ancestor_is_a_strict_stop(self) -> None:
        completed = types.SimpleNamespace(returncode=1)
        with mock.patch.object(live_gate.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "not an ancestor"):
                live_gate.require_ancestor(Path("/tmp/repo"), "pin", "live")

    def test_declaration_shape_rejects_duplicate_category_wrapper_and_sorry_drift(self) -> None:
        exact = b"@[category research open, AMS 5]\ntheorem bondy_conjecture : answer(sorry) \xe2\x86\x94 True := by\n  sorry\n"
        self.assertEqual(live_gate.exact_declaration_shape(exact)["declaration_count"], 1)
        variants = (
            exact + exact,
            exact.replace(b"research open", b"research solved"),
            exact.replace(b"answer(sorry)", b"answer(False)"),
            exact.replace(b"  sorry", b"  trivial"),
        )
        for variant in variants:
            with self.assertRaisesRegex(RuntimeError, "shape drift"):
                live_gate.exact_declaration_shape(variant)

    @staticmethod
    def graphql_page(rows: list[dict[str, object]], total: int) -> dict[str, object]:
        return {
            "repository": {"pullRequests": {"totalCount": total, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": rows}},
            "rateLimit": {"cost": 1, "remaining": 999, "resetAt": "2026-08-14T00:00:00Z"},
        }

    def test_graphql_zero_set_is_complete_and_truncation_is_rejected(self) -> None:
        zero = self.graphql_page([], 0)
        with mock.patch.object(live_gate, "graphql", side_effect=[zero, zero]):
            self.assertEqual(live_gate.graphql_open_pull_bindings("token")["total_count"], 0)
        truncated = self.graphql_page([], 1)
        with mock.patch.object(live_gate, "graphql", return_value=truncated):
            with self.assertRaisesRegex(RuntimeError, "truncated"):
                live_gate.graphql_open_pull_bindings("token")

    def test_graphql_identity_mutation_including_small_pr_is_rejected(self) -> None:
        row = {
            "id": "PR_7", "number": 7, "state": "OPEN", "title": "x", "isDraft": False, "updatedAt": "t", "headRefOid": "a" * 40,
            "headRefName": "r", "headRepository": {"nameWithOwner": "f/r"},
            "baseRefName": "main", "baseRepository": {"nameWithOwner": "g/f"}, "changedFiles": 1, "baseRefOid": "b" * 40,
            "files": {"totalCount": 1, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"path": "x", "changeType": "MODIFIED"}]},
        }
        final = dict(row)
        final.pop("files")
        final["headRefOid"] = "c" * 40
        with mock.patch.object(live_gate, "graphql", side_effect=[self.graphql_page([row], 1), self.graphql_page([final], 1)]):
            with self.assertRaisesRegex(RuntimeError, "mutated"):
                live_gate.graphql_open_pull_bindings("token")

    def test_graphql_null_identity_bad_change_type_and_low_quota_fail_closed(self) -> None:
        row = {
            "id": "PR_8", "number": 8, "state": "OPEN", "title": "x", "isDraft": False,
            "updatedAt": "t", "headRefOid": "a" * 40, "headRefName": "r", "headRepository": None,
            "baseRefOid": "b" * 40, "baseRefName": "main", "baseRepository": {"nameWithOwner": "g/f"},
            "changedFiles": 1,
            "files": {"totalCount": 1, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"path": "x", "changeType": "UNKNOWN"}]},
        }
        malformed = json.loads(json.dumps(row))
        malformed["id"] = None
        malformed["files"]["nodes"][0]["changeType"] = "MODIFIED"
        with mock.patch.object(live_gate, "graphql", return_value=self.graphql_page([malformed], 1)):
            with self.assertRaisesRegex(RuntimeError, "type/null/state"):
                live_gate.graphql_open_pull_bindings("token")
        with mock.patch.object(live_gate, "graphql", return_value=self.graphql_page([row], 1)):
            with self.assertRaisesRegex(RuntimeError, "path/changeType"):
                live_gate.graphql_open_pull_bindings("token")
        attestation = live_attestation_fixture()
        attestation["graphql_rate_limit_observations"]["before"][0]["remaining"] = 1
        with self.assertRaisesRegex(RuntimeError, "quota reserve"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_issue_search_count_schema_and_uniqueness_are_strict(self) -> None:
        malformed = (
            {"incomplete_results": False, "total_count": 1, "items": []},
            {"incomplete_results": False, "total_count": 1, "items": [{"number": None}]},
            {"incomplete_results": False, "total_count": 2, "items": [{"number": 7}, {"number": 7}]},
        )
        for response in malformed:
            with mock.patch.object(live_gate, "api", return_value=response):
                with self.assertRaises(RuntimeError):
                    live_gate.issue_search("token", "q")

    def test_repeated_cursor_is_rejected_and_file_order_is_canonicalized(self) -> None:
        repeated = {
            "repository": {"pullRequests": {"totalCount": 0, "pageInfo": {"hasNextPage": True, "endCursor": "same"}, "nodes": []}},
            "rateLimit": {"cost": 1, "remaining": 999, "resetAt": "t"},
        }
        with mock.patch.object(live_gate, "graphql", side_effect=[repeated, repeated]):
            with self.assertRaisesRegex(RuntimeError, "repeated"):
                live_gate.graphql_open_pull_bindings("token")
        row = {
            "id": "PR_9", "number": 9, "state": "OPEN", "title": "x", "isDraft": False,
            "updatedAt": "t", "headRefOid": "a" * 40, "headRefName": "r", "headRepository": None,
            "baseRefOid": "b" * 40, "baseRefName": "main", "baseRepository": {"nameWithOwner": "g/f"},
            "changedFiles": 2,
            "files": {"totalCount": 2, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"path": "z", "changeType": "MODIFIED"}, {"path": "a", "changeType": "ADDED"}]},
        }
        final = dict(row)
        final.pop("files")
        with mock.patch.object(live_gate, "graphql", side_effect=[self.graphql_page([row], 1), self.graphql_page([final], 1)]):
            result = live_gate.graphql_open_pull_bindings("token")
        self.assertEqual(result["bindings"][0]["changed_paths"], ["a", "z"])

    def test_graphql_rest_rename_classification_must_be_one_to_one(self) -> None:
        row = {
            "id": "PR_10", "number": 10, "state": "OPEN", "title": "x", "isDraft": False,
            "updatedAt": "t", "headRefOid": "a" * 40, "headRefName": "r", "headRepository": None,
            "baseRefOid": "b" * 40, "baseRefName": "main", "baseRepository": {"nameWithOwner": "g/f"},
            "changedFiles": 1,
            "files": {"totalCount": 1, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"path": "new", "changeType": "RENAMED"}]},
        }
        final = dict(row)
        final.pop("files")
        with mock.patch.object(live_gate, "graphql", side_effect=[self.graphql_page([row], 1), self.graphql_page([final], 1)]), mock.patch.object(
            live_gate, "api", return_value=[{"filename": "new", "status": "modified"}]
        ):
            with self.assertRaisesRegex(RuntimeError, "classification mismatch"):
                live_gate.graphql_open_pull_bindings("token")

    def test_renamed_away_exact_target_is_in_complete_collision_surface(self) -> None:
        row = {
            "id": "PR_11", "number": 11, "state": "OPEN", "title": "x", "isDraft": False,
            "updatedAt": "t", "headRefOid": "a" * 40, "headRefName": "r", "headRepository": None,
            "baseRefOid": "b" * 40, "baseRefName": "main", "baseRepository": {"nameWithOwner": "g/f"},
            "changedFiles": 1,
            "files": {"totalCount": 1, "pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [{"path": "FormalConjectures/RenamedDestination.lean", "changeType": "RENAMED"}]},
        }
        final = dict(row)
        final.pop("files")
        rest = [{"filename": "FormalConjectures/RenamedDestination.lean", "status": "renamed", "previous_filename": live_gate.TARGET_PATH}]
        with mock.patch.object(live_gate, "graphql", side_effect=[self.graphql_page([row], 1), self.graphql_page([final], 1)]), mock.patch.object(
            live_gate, "api", return_value=rest
        ):
            result = live_gate.graphql_open_pull_bindings("token")
        self.assertEqual(
            result["bindings"][0]["changed_paths"],
            sorted([live_gate.TARGET_PATH, "FormalConjectures/RenamedDestination.lean"]),
        )

    def test_pagination_ambiguity_and_protected_delta_are_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "ambiguity"):
            live_gate.page_info({"nodes": [], "pageInfo": {"hasNextPage": True, "endCursor": None}}, "fixture")
        for protected in (live_gate.TARGET_PATH, "FormalConjectures/Imported.lean", "lean-toolchain"):
            attestation = live_attestation_fixture()
            attestation["continuity"]["delta"] = [{"status": "M", "path": protected}]
            attestation["continuity"]["delta_sha256"] = search.canonical_sha256(attestation["continuity"]["delta"])
            attestation["continuity"]["commits"][0]["changed_paths"] = [protected]
            attestation["bracket_snapshot_before"]["continuity"]["canonical_sha256"] = search.canonical_sha256(attestation["continuity"])
            attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
            with self.assertRaisesRegex(RuntimeError, "delta"):
                search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))

    def test_merge_provenance_is_rejected_by_v3_consumer(self) -> None:
        attestation = live_attestation_fixture()
        attestation["continuity"]["commits"][0]["parents"] = ["1" * 40, "5" * 40]
        attestation["bracket_snapshot_before"]["continuity"]["canonical_sha256"] = search.canonical_sha256(attestation["continuity"])
        attestation["bracket_snapshot_after"] = json.loads(json.dumps(attestation["bracket_snapshot_before"]))
        with self.assertRaisesRegex(RuntimeError, "commit chain"):
            search.validate_live_attestation(attestation, sealed_attestation_fixture(attestation))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-free", action="store_true", required=True)
    parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
