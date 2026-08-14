#!/usr/bin/env python3
"""Static, target-free integrity verifier for the Bondy v3 freeze."""

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


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "bondy-freeze-files-v3":
    raise SystemExit("v3 freeze registry schema drift")
REQUIRED_FREEZE_PATHS = {
    ".github/workflows/bondy-longest-cycles-development.yml",
    "scripts/prospective_bondy_construct.py", "scripts/prospective_bondy_gate.py",
    "scripts/prospective_bondy_search.py", "scripts/prospective_bondy_replay.cpp",
    "scripts/prospective_bondy_verify.py", "scripts/test_bondy_development.py",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/activation-gate-validation.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/invalid-preactivation-gate-timeout.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/invalid-run-31845837185.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/manifest.json",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/math-audit.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/parallel-live-gate-validation.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/preflight.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/q4-algorithm-design.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/semantic-closure-v3.json",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/source-status-attestation.json",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/tip-continuity-policy-audit.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/upstream-drift-repin-audit.md",
    "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/verify_freeze.py",
}
if set(registry.get("sha256", {})) != REQUIRED_FREEZE_PATHS:
    raise SystemExit("v3 freeze registry exact protected-path set drift")
for relative, expected in registry.get("sha256", {}).items():
    path = ROOT / relative
    if not path.is_file() or digest(path) != expected:
        raise SystemExit(f"freeze content drift: {relative}")

manifest = json.loads((HERE / "manifest.json").read_text())
if manifest.get("seal_version") != "bondy-longest-cycles-development-v3" or manifest.get("supersedes") != "bondy-longest-cycles-development-v2":
    raise SystemExit("v3 seal identity drift")
if manifest.get("live_gate", {}).get("schema") != "bondy_source_status_duplicate_gate_tip_continuity_v3":
    raise SystemExit("v3-only live gate drift")
if manifest.get("upstream") != {
    "commit": "b5acb0ff13e38084105b7fe020ba0d59c1925bc5",
    "tree": "4f6c9bd17fdfdc264f54b26862ce768743da5d63",
    "path": "FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean",
    "blob": "c4c5cb1983936860d5a4a7208b3f04bd201290d4",
}:
    raise SystemExit("historical upstream anchor drift")

closure = json.loads((HERE / "semantic-closure-v3.json").read_text())
frozen = manifest.get("semantic_closure", {})
if (
    closure.get("schema") != "bondy_semantic_closure_v3"
    or closure.get("pinned_commit") != manifest["upstream"]["commit"]
    or closure.get("pinned_tree") != manifest["upstream"]["tree"]
    or closure.get("root") != manifest["upstream"]["path"]
    or closure.get("closure_count") != len(closure.get("entries", []))
    or closure.get("closure_count") == 0
    or closure.get("toolchain_count") != len(closure.get("toolchain", []))
    or canonical_sha256(closure.get("entries")) != closure.get("closure_sha256")
    or closure.get("closure_sha256") != frozen.get("sha256")
    or canonical_sha256(closure.get("toolchain")) != closure.get("toolchain_sha256")
    or closure.get("toolchain_sha256") != frozen.get("toolchain_sha256")
    or canonical_sha256(closure.get("external_revisions")) != closure.get("external_revisions_sha256")
    or closure.get("external_revisions_sha256") != frozen.get("external_revisions_sha256")
    or frozen.get("count") != closure.get("closure_count")
):
    raise SystemExit("semantic closure/toolchain freeze drift")

attestation = json.loads((HERE / "source-status-attestation.json").read_text())
if (
    attestation.get("schema") != "bondy_source_status_attestation_v3"
    or attestation.get("seal_version") != manifest["seal_version"]
    or attestation.get("status") != "PENDING_AUTHENTICATED_LIVE_GATE_RATE_LIMITED"
    or attestation.get("live_gate_schema") != manifest["live_gate"]["schema"]
    or attestation.get("historical_upstream") != manifest["upstream"]
    or attestation.get("workflow_enabled_by_default") is not False
    or attestation.get("target_evaluated") is not False
):
    raise SystemExit("pending v3 source/status record drift")

grammar = manifest["grammar"]
if grammar["row_limit"] != construct.ROW_LIMIT or construct.source_control()["scaled_degree_residual"] != -1:
    raise SystemExit("constructor grammar/source control drift")
constructor_tree = ast.parse((ROOT / "scripts/prospective_bondy_construct.py").read_text())
if {node.name for node in ast.walk(constructor_tree) if isinstance(node, ast.FunctionDef)} & {"target_evaluate", "circumference", "path_cover"}:
    raise SystemExit("constructor-only module contains target evaluator")

gate = (ROOT / "scripts/prospective_bondy_gate.py").read_text()
search = (ROOT / "scripts/prospective_bondy_search.py").read_text()
workflow = (ROOT / ".github/workflows/bondy-longest-cycles-development.yml").read_text()
for token in (
    "bondy_source_status_duplicate_gate_tip_continuity_v3", "semantic-closure-v3.json",
    "merge-base", "--is-ancestor", "--name-status", "OPEN_PULL_IDENTITY_QUERY",
    "changeType", "previous_filename", "whole-gate monotonic deadline",
):
    if token not in gate:
        raise SystemExit(f"v3 gate token absent: {token}")
for token in ("bondy_source_status_duplicate_gate_tip_continuity_v3", "canonical JSON", "protected_paths", "validate_live_attestation"):
    if token not in search:
        raise SystemExit(f"v3 search-lock token absent: {token}")
for forbidden in ("bracketed_single_scan_v2", "bondy_source_status_attestation_v2"):
    if forbidden in gate or forbidden in search:
        raise SystemExit(f"legacy attestation path remains reachable: {forbidden}")
for token in ("fetch-depth: 0", "One complete v3 live continuity gate", "inputs.enable_target == true", "if: always()"):
    if token not in workflow:
        raise SystemExit(f"v3 workflow token absent: {token}")
if workflow.count("scripts/prospective_bondy_gate.py") != 1:
    raise SystemExit("workflow must execute the quota-expensive live gate exactly once")
for forbidden in ("gh release", "gh issue", "gh pr", "git push", "create-release"):
    if forbidden in workflow:
        raise SystemExit(f"forbidden publication token present: {forbidden}")

print("BONDY_V3_FREEZE_VERIFIED_TARGET_DISABLED")
