#!/usr/bin/env python3
"""Static and content verification for the disabled Bondy freeze."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
import prospective_bondy_construct as construct  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "bondy-freeze-files-v1":
    raise SystemExit("freeze registry schema drift")
for relative, expected in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file() or digest(path) != expected:
        raise SystemExit(f"freeze content drift: {relative}")

manifest = json.loads((HERE / "manifest.json").read_text())
if manifest["evidence_class"] != "CONTAMINATED_DEVELOPMENT":
    raise SystemExit("evidence-class drift")
if manifest["slice"] != {"k": 4, "t": 4, "h_order": 20, "g_order": 24, "large_graph_cutoff": 108}:
    raise SystemExit("k/t/order theorem-boundary drift")
if manifest["caps"] != {"internal_search_seconds": 48, "internal_finalize_seconds": 54, "external_process_seconds": 60, "term_to_kill_seconds": 6, "independent_verify_seconds": 60}:
    raise SystemExit("48/54/60 process cap drift")
if manifest["runtime"] != {"python_version": "3.11.9", "networkx_version": "3.3", "discovery_algorithm": "python_endpoint_path_cover_dp_v1", "replay_algorithm": "cpp_endpoint_path_cover_dp_v1"}:
    raise SystemExit("runtime/algorithm provenance drift")
if manifest["live_gate"] != {"schema": "bondy_source_status_duplicate_gate_bracketed_single_scan_v1", "snapshot_workers": 24, "open_pull_page_size": 100, "changed_file_page_size": 100, "changed_file_scans_per_pr": 1, "deterministic_order": ["pull_number", "changed_path"], "bracket_identity_snapshot_equality": True, "open_pr_set_equality": True, "file_binding_identity_equality": True}:
    raise SystemExit("parallel live-gate contract drift")
if manifest["target_execution_lock"] != {
    "enabled_by_default": False,
    "token_provisioned": False,
    "activation_token_sha256": "f" * 64,
    "state": "TARGET_DISABLED_NO_ACTIVATION_TOKEN_EXISTS",
}:
    raise SystemExit("prepared target execution is not mechanically disabled")
grammar = manifest["grammar"]
if grammar["row_limit"] != construct.ROW_LIMIT or grammar["quotient_catalogue"] != [[list(c) for c in row] for row in construct.QUOTIENT_CATALOGUE]:
    raise SystemExit("quotient catalogue drift")
if grammar["perfect_matchings"] != [[list(e) for e in row] for row in construct.PERFECT_MATCHINGS]:
    raise SystemExit("perfect-matching order drift")
if grammar["port_permutations"] != [list(row) for row in construct.PORT_PERMUTATIONS]:
    raise SystemExit("port-permutation order drift")
if construct.source_control()["scaled_degree_residual"] != -1:
    raise SystemExit("source minus-one control drift")

constructor_source = (ROOT / "scripts/prospective_bondy_construct.py").read_text()
constructor_tree = ast.parse(constructor_source)
constructor_functions = {node.name for node in ast.walk(constructor_tree) if isinstance(node, ast.FunctionDef)}
if constructor_functions & {"target_evaluate", "maximize_q4", "cover_fixed_vertices", "circumference", "path_cover"}:
    raise SystemExit("constructor-only module contains a forbidden target evaluator")

search = (ROOT / "scripts/prospective_bondy_search.py").read_text()
for token in (
    "campaign_commit_is_not_checked_out_HEAD",
    "exact_activation_token_mismatch",
    "activation_token_not_provisioned",
    "frozen_python_version_mismatch",
    "frozen_networkx_version_mismatch",
    "EndpointPathCoverDP",
    "start_new_session=True",
    "os.killpg",
    "endpoint path-cover DP deadline",
    "pc_table_sha256",
    "independent_upper_replay",
    "GATE_FAIL:independent replay nonzero logical/internal exit",
    "upper-rejection counter-cover replay failed",
    '"edges_g"',
    '"provenance"',
    "ledger append after durable candidate/terminal",
):
    if token not in search:
        raise SystemExit(f"search safety token absent: {token}")
if "import pulp" in search or "PULP_CBC" in search or ".solve(" in search:
    raise SystemExit("external discovery solver present")

verifier = (ROOT / "scripts/prospective_bondy_verify.py").read_text()
for token in (
    "list(construct.generate(construct.ROW_LIMIT))",
    "constructor indices are not contiguous frozen order",
    "truncated false DOMAIN_EXHAUSTED",
    "candidate/evaluation artifact is not bound to exact final ledger row",
    "deletion_sets",
    "compile_replay",
    "binary_sha256",
    "validate_upper_rejection",
    "candidate complete joined edge list drift",
    "candidate search timing/version provenance drift",
    "missing or unknown target evaluation classification",
    "target classification/candidate Boolean disagreement",
    "EXPECTED_PYTHON_VERSION = \"3.11.9\"",
    "EXPECTED_NETWORKX_VERSION = \"3.3\"",
):
    if token not in verifier:
        raise SystemExit(f"verifier semantic token absent: {token}")

gate = (ROOT / "scripts/prospective_bondy_gate.py").read_text()
for token in (
    "ALLOWED_SEARCH_RESULTS",
    "all_open_pulls",
    "incomplete_results",
    "bracket_snapshot_stable",
    "open_pr_set_stable",
    "file_bindings_exact",
    "bondy_source_status_duplicate_gate_bracketed_single_scan_v1",
    "bracket_snapshot",
    "bind_changed_paths",
    "SNAPSHOT_WORKERS = 24",
    "ThreadPoolExecutor",
    "cancel_futures=True",
    "changed_paths_sha256",
    "head_sha",
    "base_sha",
    "exact_local_contamination_history",
    "no_open_pr_touches_target",
):
    if token not in gate:
        raise SystemExit(f"source/status gate token absent: {token}")

tests = (ROOT / "scripts/test_bondy_development.py").read_text()
for token in (
    "--target-free",
    "test_s44_source_control_is_exact_minus_one",
    "test_constructor_tests_do_not_call_proposed_candidate_target",
    "test_execution_lock_fails_before_attestation_or_target",
    "test_atomic_replace_failure_does_not_publish_candidate",
    "test_cpp_replay_rejects_malformed_and_trailing_tokens_before_dp",
    "test_nonzero_independent_replay_is_gate_failure_not_timeout",
    "test_synthetic_upper_rejection_counter_witness_replays",
    "test_complete_joined_edge_list_round_trips_without_target_evaluation",
    "test_full_ledger_rejects_unrecognized_fake_target_result",
    "test_open_pr_and_changed_file_pagination_are_complete",
    "test_single_file_binding_has_deterministic_order",
    "test_each_open_pr_file_catalogue_is_fetched_exactly_once",
    "test_parallel_pull_worker_error_propagates_fail_closed",
    "test_head_base_update_and_open_close_races_fail_bracket",
):
    if token not in tests:
        raise SystemExit(f"target-free test token absent: {token}")

workflow = (ROOT / ".github/workflows/bondy-longest-cycles-development.yml").read_text()
for token in (
    "workflow_dispatch:",
    "inputs.enable_target == true",
    "--campaign-commit '${{ inputs.campaign_commit }}'",
    "--activation-token '${{ inputs.activation_token }}'",
    "timeout --signal=TERM --kill-after=6s 60s",
    "target_code='${{ steps.target.outputs.target_code }}'",
    "provisional-evidence",
    "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803",
    "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1",
    "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
    "expected_status=CANDIDATE_VERIFIED",
    "expected_status=TERMINAL_VERIFIED",
    "accepted_status=$(python",
    'python-version: "3.11.9"',
):
    if token not in workflow:
        raise SystemExit(f"workflow safety token absent: {token}")
for forbidden in ("gh release", "gh issue", "gh pr", "git push", "create-release"):
    if forbidden in workflow:
        raise SystemExit(f"forbidden publication token present: {forbidden}")

contract = (HERE / "CONTRACT.md").read_text()
for token in (
    "True ↔ RHS",
    "scaled premise residual",
    "Pure edge addition is a strict stop",
    "q_4(H)<=16",
    "1,351",
    "4,845",
    "No timeout",
    "does not authorize execution",
    "CPython `3.11.9`",
    "NetworkX `3.3`",
    "bounded 24-worker pool",
):
    if token not in contract:
        raise SystemExit(f"contract requirement absent: {token}")

print("BONDY_FREEZE_VERIFIED_TARGET_DISABLED")
