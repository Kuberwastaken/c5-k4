#!/usr/bin/env python3
"""Fail closed if the Catch-Up N=24 parity-packed DEVELOPMENT freeze drifts."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


registry = json.loads((HERE / "freeze-files.json").read_text(encoding="utf-8"))
expected = {
    ".github/workflows/catchup-n24-parity-packed-development.yml",
    "results/expansion/live-search-2026-08-14/catchup-n24-parity-packed-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/catchup-n24-parity-packed-development/manifest.json",
    "results/expansion/live-search-2026-08-14/catchup-n24-parity-packed-development/verify_freeze.py",
    "scripts/prospective_catchup_parity_packed.cpp",
    "scripts/test_catchup_parity_packed.py",
    "scripts/verify_catchup_parity_packed.py",
}
if registry.get("schema") != "catchup-n24-parity-packed-frozen-files-v1":
    raise SystemExit("freeze registry schema drift")
if set(registry.get("sha256", {})) != expected:
    raise SystemExit("freeze registry identity/coverage drift")
for relative, digest in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file() or sha256(path) != digest:
        raise SystemExit(f"frozen file drift: {relative}")

manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
if manifest.get("schema") != "catchup-n24-parity-packed-development-v1":
    raise SystemExit("manifest schema drift")
if manifest.get("development_only") is not True or manifest.get("target_evaluated_at_freeze") is not False:
    raise SystemExit("evidence split/target-evaluation drift")
if manifest.get("pre_freeze_local_commit") != "d9ae09fe54af131790e72d12ad8b438a4b1fd9f6":
    raise SystemExit("pre-freeze local history drift")

formal = manifest["formal_conjectures"]
if formal != {
    "commit": "6c0950bec7743f5098c0196c6aee7b22c1ec8005",
    "tree": "5af0d2a3a319ee2458f8cd061db7c49aeba1b35e",
    "path": "FormalConjectures/Paper/CatchUpConjecture.lean",
    "blob_sha1": "ce8251a228ea79a6b2f8414e9eb6b5291a640677",
    "sha256": "7e940f2e37a1794e98fc21454096429da13243669a432b9239743aaf46f1d3c0",
    "declaration": "CatchUp.value_of_even_mul_succ_self_div_two",
    "category": "research open",
}:
    raise SystemExit("formal source pin drift")

for record in manifest["design_inputs"].values():
    path = ROOT / record["path"]
    if not path.is_file() or sha256(path) != record["sha256"]:
        raise SystemExit(f"design-input drift: {record['path']}")

target = manifest["target"]
if target != {
    "n": 24,
    "triangular_sum": 300,
    "premise_even": True,
    "literal_counterexample_values": [-1, 1],
    "draw_disposition": "HOLD_BOUNDED",
    "non_result_disposition": "TIMEOUT_BRACKET",
}:
    raise SystemExit("target semantics drift")

representation = manifest["representation"]
if (
    representation.get("mask_bits") != 24
    or representation.get("word_type") != "uint32_t"
    or representation.get("bytes_per_mask") != 4
    or representation.get("memo_bytes_at_n24") != 67_108_864
    or representation.get("codes") != {"unknown": 0, "loss": 1, "draw": 2, "win": 3}
    or representation.get("slot") != "deficit >> 1"
    or representation.get("shift") != "2 * slot"
    or representation.get("move_order") != "ascending set-bit extraction"
):
    raise SystemExit("packed representation drift")

if manifest.get("source_controls") != [3, 4, 7, 8, 11, 12, 15, 16, 19, 20]:
    raise SystemExit("source-control domain drift")
if manifest.get("target_free_strategy_controls") != {"win_n": 1, "loss_n": 9}:
    raise SystemExit("target-free strategy-control drift")
if manifest.get("known_upstream_issue_pr_ids") != [1324, 1325, 4834]:
    raise SystemExit("known upstream issue/PR surface drift")
if manifest.get("n23_gate") != {
    "value": 0,
    "value_name": "draw",
    "memo_states": 95_451_689,
    "calls": 826_741_149,
    "maximum_solver_seconds": 38,
    "prefreeze_vps_seconds": 10.08,
    "prefreeze_vps_peak_rss_kib": 36_328,
}:
    raise SystemExit("N23 exact/performance gate drift")
if manifest.get("caps") != {
    "n23_internal_seconds": 38,
    "n23_external_seconds": 43,
    "n24_internal_seconds": 54,
    "n24_external_seconds": 60,
    "verifier_external_seconds": 60,
}:
    raise SystemExit("process-cap drift")
if manifest.get("activation") != {
    "default_authorize_n24": False,
    "required_token": "AUTHORIZE_FROZEN_CATCHUP_N24_V1",
    "generic_n24_cli_available": False,
}:
    raise SystemExit("target activation drift")
if manifest.get("incremental_checkpoint_memo_states") != 1_000_000:
    raise SystemExit("incremental evidence cadence drift")
if manifest.get("controlled_signals") != [2, 15]:
    raise SystemExit("controlled-signal drift")
if manifest.get("certificate_publication") != "write .partial then atomically rename only after complete flush":
    raise SystemExit("certificate-publication drift")
if manifest.get("public_action_authorized") is not False:
    raise SystemExit("public authority drift")

cpp = (ROOT / "scripts/prospective_catchup_parity_packed.cpp").read_text(encoding="utf-8")
checker = (ROOT / "scripts/verify_catchup_parity_packed.py").read_text(encoding="utf-8")
tests = (ROOT / "scripts/test_catchup_parity_packed.py").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/catchup-n24-parity-packed-development.yml").read_text(encoding="utf-8")
contract = (HERE / "CONTRACT.md").read_text(encoding="utf-8")
ast.parse(checker, filename="verify_catchup_parity_packed.py")
ast.parse(tests, filename="test_catchup_parity_packed.py")

for token in (
    "std::vector<std::uint32_t> words_",
    "2U * (static_cast<unsigned>(deficit) >> 1U)",
    "((deficit + remaining_sum) & 1) != (total_sum_ & 1)",
    "std::countr_zero(available)",
    "memo_.size() >= next_progress_",
    "next_progress_ += 1'000'000ULL",
    "kExpectedN23States = 95'451'689ULL",
    "kExpectedN23Calls = 826'741'149ULL",
    'run_one(23, "n23_performance_gate", 38.0',
    'run_one(24, "n24_target", 54.0',
    'std::string(mode) == "n24_target"',
    "AUTHORIZE_FROZEN_CATCHUP_N24_V1",
    "write_strategy_dag",
    'std::string(mode) == "small_certificate"',
    "std::filesystem::rename(partial_path, final_path)",
    "g_termination_signal",
    "nonterminal certificate has no edge",
):
    if token not in cpp:
        raise SystemExit(f"solver safety token absent: {token}")
for forbidden in ('--n 24', 'unordered_map<'):
    if forbidden in cpp:
        raise SystemExit(f"forbidden generic/hash target mechanism: {forbidden}")

for token in (
    "independent_absolute_value",
    "N23_STATES = 95_451_689",
    "N23_CALLS = 826_741_149",
    "strategy edge does not strictly reduce mask cardinality",
    "losing node does not certify every legal move",
    "strategy DAG contains unreachable nodes",
    "PASS_TIMEOUT_BRACKET",
):
    if token not in checker:
        raise SystemExit(f"independent verifier token absent: {token}")
for token in (
    "test_absolute_score_reference_matches_every_small_order",
    "test_target_is_mechanically_disabled",
    "test_ledger_rejects_wrong_n23_counts",
    "test_strategy_checker_accepts_minimal_synthetic_win",
    "test_solver_strategy_writer_replays_win_and_loss",
    "test_ledger_rejects_unknown_event_and_early_timeout",
):
    if token not in tests:
        raise SystemExit(f"test token absent: {token}")

for token in (
    "workflow_dispatch:",
    "campaign_commit:",
    "authorize_n24:",
    "default: false",
    "activation_token:",
    "test \"$(git rev-parse HEAD)\" = \"$CAMPAIGN_COMMIT\"",
    "verify_freeze.py",
    "--source-controls",
    "--n23-gate",
    "43s",
    "--n24-target",
    "60s",
    "AUTHORIZE_FROZEN_CATCHUP_N24_V1",
    "if: ${{ inputs.authorize_n24",
    "if: always()",
    "strategy-dag.jsonl",
    "find . -type f ! -name SHA256SUMS",
    "allowed={1324,1325,4834}",
    "Catch-Up issue/PR surface drift",
):
    if token not in workflow:
        raise SystemExit(f"workflow safety token absent: {token}")
for forbidden in ("pull_request:", "push:", "repository_dispatch", "gh issue", "gh pr", "gh release"):
    if forbidden in workflow:
        raise SystemExit(f"forbidden workflow authority: {forbidden}")

for token in (
    "prepared and target-unevaluated",
    "95,451,689",
    "826,741,149",
    "at most 38 seconds",
    "67,108,864 bytes = 64 MiB",
    "internal steady-clock deadline of 54 seconds",
    "complete strategy DAG",
    "authorizes no issue, PR, tag,",
    "release, README edit",
):
    if token not in contract:
        raise SystemExit(f"contract token absent: {token}")

print("Catch-Up N24 parity-packed DEVELOPMENT freeze verified")
