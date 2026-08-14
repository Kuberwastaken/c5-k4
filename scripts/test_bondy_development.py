#!/usr/bin/env python3
"""Target-free tests for the frozen Bondy constructor and execution lock."""

from __future__ import annotations

import argparse
import ast
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
    identities = [] if empty else [live_gate.pull_identity(pull_fixture(1))]
    paths = ["FormalConjectures/Unrelated.lean"]
    bindings = [] if empty else [{
        **identities[0],
        "changed_paths": paths,
        "changed_paths_sha256": search.canonical_sha256(paths),
    }]
    if identity_only_binding:
        bindings = [dict(identities[0])]
    snapshot = {
        "main": "pinned",
        "searches": {},
        "open_pulls": identities,
        "repository_total_count": 0,
    }
    return {
        "schema": "bondy_source_status_duplicate_gate_bracketed_single_scan_v2",
        "kind": "source_status_duplicate_gate",
        "status": "PASS",
        "checks": {key: True for key in search.LIVE_GATE_CHECKS},
        "upstream": {"commit": "pinned"},
        "open_pr_target_path_matches": [],
        "bracket_snapshot_before": snapshot,
        "open_pr_file_bindings": bindings,
        "bracket_snapshot_after": json.loads(json.dumps(snapshot)),
        "local_history_hits": [],
        "local_history_identities": [],
    }


def sealed_attestation_fixture(attestation: dict[str, object]) -> dict[str, object]:
    identities = attestation["bracket_snapshot_before"]["open_pulls"]
    bindings = attestation["open_pr_file_bindings"]
    return {"gate": {
        "checks_sha256": search.canonical_sha256(attestation["checks"]),
        "bracket_snapshot_sha256": search.canonical_sha256(attestation["bracket_snapshot_before"]),
        "file_bindings_sha256": search.canonical_sha256(bindings),
        "full_record_sha256": __import__("hashlib").sha256(search.canonical_bytes(attestation)).hexdigest(),
        "open_pr_identities": len(identities),
        "file_bindings": len(bindings),
    }}


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
        self.assertIn('--activation-token "$ACTIVATION_TOKEN"', shell_source)
        self.assertIn("CAMPAIGN_COMMIT: ${{ inputs.campaign_commit }}", workflow)
        self.assertIn("ACTIVATION_TOKEN: ${{ inputs.activation_token }}", workflow)

        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "injected"
            malicious = "bad'\nprintf injected > " + str(marker) + "\n"
            environment = dict(os.environ, CAMPAIGN_COMMIT=malicious, ACTIVATION_TOKEN=malicious)
            completed = subprocess.run(
                [
                    "bash",
                    "-c",
                    "python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "
                    '--campaign-commit "$CAMPAIGN_COMMIT" --activation-token "$ACTIVATION_TOKEN"',
                ],
                env=environment,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(json.loads(completed.stdout), ["--campaign-commit", malicious, "--activation-token", malicious])
            self.assertFalse(marker.exists())

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
            activation_token="BONDY_TARGET_DISABLED",
        )
        with self.assertRaisesRegex(RuntimeError, "TARGET_EXECUTION_DISABLED"):
            search.unlock(args)

    def test_v2_live_attestation_requires_full_bracket_and_bindings(self) -> None:
        manifest = {
            "live_gate": {"schema": "bondy_source_status_duplicate_gate_bracketed_single_scan_v2"},
            "upstream": {"commit": "pinned"},
        }
        attestation = live_attestation_fixture()
        sealed = sealed_attestation_fixture(attestation)
        search.validate_live_attestation(attestation, manifest, sealed)
        attestation["open_pr_file_bindings"][0]["head_sha"] = "mutated"
        with self.assertRaisesRegex(RuntimeError, "missing or drifted"):
            search.validate_live_attestation(attestation, manifest, sealed)

    def test_forged_zero_identity_pass_is_rejected(self) -> None:
        manifest = {"live_gate": {"schema": "bondy_source_status_duplicate_gate_bracketed_single_scan_v2"}, "upstream": {"commit": "pinned"}}
        attestation = live_attestation_fixture(empty=True)
        with self.assertRaisesRegex(RuntimeError, "nonempty sealed count drift"):
            search.validate_live_attestation(attestation, manifest, sealed_attestation_fixture(attestation))

    def test_forged_identity_only_file_binding_is_rejected(self) -> None:
        manifest = {"live_gate": {"schema": "bondy_source_status_duplicate_gate_bracketed_single_scan_v2"}, "upstream": {"commit": "pinned"}}
        attestation = live_attestation_fixture(identity_only_binding=True)
        with self.assertRaisesRegex(RuntimeError, "file binding schema drift"):
            search.validate_live_attestation(attestation, manifest, sealed_attestation_fixture(attestation))

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
    def test_v2_local_history_accepts_only_exact_repin_audit(self) -> None:
        freeze = "f" * 40
        hits = [live_gate.KNOWN_REPIN_AUDIT_COMMIT, freeze, live_gate.KNOWN_PREFLIGHT_COMMIT]

        def exact_git(*args: str) -> str:
            commit = args[-1]
            if args[0] == "show":
                return "research: audit Bondy upstream repin" if commit == live_gate.KNOWN_REPIN_AUDIT_COMMIT else "freeze"
            if args[0] == "diff-tree":
                if commit == live_gate.KNOWN_REPIN_AUDIT_COMMIT:
                    return live_gate.KNOWN_REPIN_AUDIT_PATH
                if commit == freeze:
                    return "scripts/prospective_bondy_gate.py"
                return "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md"
            raise AssertionError(args)

        with mock.patch.object(live_gate, "git", side_effect=exact_git):
            accepted, identities = live_gate.validate_local_contamination(hits)
        self.assertTrue(accepted)
        self.assertEqual([row["kind"] for row in identities], ["known_repin_audit", "freeze_introducer", "known_preflight"])

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

    def test_head_base_update_and_open_close_races_fail_bracket(self) -> None:
        target = "@[category research open, AMS 5]\nanswer(sorry) ↔ True\n".encode("utf-8")
        before = {
            "main": live_gate.UPSTREAM_COMMIT,
            "searches": live_gate.ALLOWED_SEARCH_RESULTS,
            "open_pulls": [live_gate.pull_identity(pull_fixture(12, "before"))],
            "repository_total_count": 0,
        }

        def exact_api(path: str, token: str) -> object:
            if "/git/commits/" in path:
                return {"tree": {"sha": live_gate.UPSTREAM_TREE}}
            if "/git/blobs/" in path:
                return {"sha": live_gate.TARGET_BLOB}
            if path.endswith(f"/issues/{live_gate.KNOWN_ISSUE}"):
                return {"number": live_gate.KNOWN_ISSUE, "state": "closed"}
            if path.endswith(f"/pulls/{live_gate.KNOWN_PR}"):
                return {"number": live_gate.KNOWN_PR, "state": "closed", "merged_at": "2026-08-14T20:25:50Z"}
            raise AssertionError(path)

        def exact_git(*args: str) -> str:
            if args[0] == "log":
                return live_gate.KNOWN_PREFLIGHT_COMMIT
            if args[0] == "show":
                return "known preflight"
            if args[0] == "diff-tree":
                return "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md"
            raise AssertionError(args)

        mutations = {}
        for name, field in (("head", "head_sha"), ("base", "base_sha"), ("updated", "updated_at")):
            mutated = json.loads(json.dumps(before))
            mutated["open_pulls"][0][field] += "-mutated"
            mutations[name] = mutated
        closed = json.loads(json.dumps(before))
        closed["open_pulls"] = []
        mutations["open_close"] = closed

        for name, after in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory, mock.patch.object(
                live_gate, "bracket_snapshot", side_effect=[before, after]
            ), mock.patch.object(live_gate, "bind_changed_paths", return_value=[{
                **before["open_pulls"][0],
                "changed_paths": ["unrelated.lean"],
                "changed_paths_sha256": live_gate.canonical_sha256(["unrelated.lean"]),
            }]), mock.patch.object(live_gate, "api", side_effect=exact_api), mock.patch.object(
                live_gate, "get_bytes", return_value=target
            ), mock.patch.object(live_gate, "git", side_effect=exact_git), mock.patch.object(
                live_gate, "TARGET_SHA256", live_gate.sha256(target)
            ):
                output = Path(directory) / "must-fail.json"
                with self.assertRaisesRegex(RuntimeError, "failed closed"):
                    live_gate.run(output, "token", None)
                record = json.loads(output.read_text())
                self.assertEqual(record["schema"], "bondy_source_status_duplicate_gate_bracketed_single_scan_v2")
                self.assertTrue(record["checks"]["file_bindings_exact"])
                self.assertFalse(record["checks"]["bracket_snapshot_stable"])
                self.assertNotEqual(record["bracket_snapshot_before"], record["bracket_snapshot_after"])
                if name == "open_close":
                    self.assertFalse(record["checks"]["open_pr_set_stable"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-free", action="store_true", required=True)
    parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
