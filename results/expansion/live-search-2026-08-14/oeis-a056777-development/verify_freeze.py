#!/usr/bin/env python3
"""Fail closed if the executable A056777 DEVELOPMENT freeze drifts."""
from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "oeis-a056777-frozen-files-v1": raise SystemExit("bad freeze registry schema")
expected = {
    ".github/workflows/oeis-a056777-development.yml",
    "results/expansion/live-search-2026-08-14/oeis-a056777-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/oeis-a056777-development/duplicate-scan.json",
    "results/expansion/live-search-2026-08-14/oeis-a056777-development/manifest.json",
    "results/expansion/live-search-2026-08-14/oeis-a056777-development/method-wall-certificate.json",
    "results/expansion/live-search-2026-08-14/oeis-a056777-development/source-status-attestation.json",
    "results/expansion/live-search-2026-08-14/oeis-a056777-development/verify_freeze.py",
    "scripts/prepare_oeis_a056777_gate.py",
    "scripts/search_oeis_a056777.py",
    "scripts/test_oeis_a056777_development.py",
    "scripts/verify_oeis_a056777_candidate.py",
}
if set(registry.get("sha256", {})) != expected: raise SystemExit("freeze registry coverage drift")
for relative, digest in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file() or sha(path) != digest: raise SystemExit(f"frozen file drift: {relative}")

m = json.loads((HERE / "manifest.json").read_text())
if (m["internal_seconds"], m["external_search_seconds"], m["external_verify_seconds"]) != (48, 54, 60): raise SystemExit("deadline cap drift")
if m["historical_exclusion_upper_inclusive"] != 10**12 or m["value_minimum"] != 10**12 + 1: raise SystemExit("historical boundary drift")
if set(m["arms"]) != {"REPEATED_POWER_SURGERY", "SQUAREFREE_THREE_BLOCK", "PURE_PRIME_POWER"}: raise SystemExit("constructive arm drift")
if m["value_maximum"] + 12 >= 2**64 or m["arms"]["PURE_PRIME_POWER"].get("theorem_pruned_exponent") != 2: raise SystemExit("64-bit/pruned-square domain drift")
if m["formal_conjectures"]["sha256"] != "2539ce34a7417a5b482d3c6f21a8327198e4890df7f67e6458a522293b1d099c": raise SystemExit("source blob drift")

status = json.loads((HERE / "source-status-attestation.json").read_text())
if status.get("observed_upstream_main") != "05ea0345d09375efac830fac93bf083b654e317e" or status.get("formal_conjectures_status") != "research open" or status.get("upstream_resolution_match_found") is not False: raise SystemExit("current source status drift")
duplicate = json.loads((HERE / "duplicate-scan.json").read_text())
if duplicate.get("provenance_database_match_found") is not True or duplicate.get("novelty_claim_permitted") is not False: raise SystemExit("duplicate disposition drift")

database = json.loads((ROOT / "results/benchmark/v1.4-f0a/registry/eligible-cluster-pool.json").read_text())
matches = []
def visit(value):
    if isinstance(value, dict):
        if value.get("cluster_id") == "fc-module:FormalConjectures/OEIS/56777": matches.append(value)
        for child in value.values(): visit(child)
    elif isinstance(value, list):
        for child in value: visit(child)
visit(database)
if len(matches) != 1: raise SystemExit("A056777 registry cardinality drift")
entry = matches[0]
if (entry.get("classification_status"), entry.get("eligible"), entry.get("semantic_exposure"), entry.get("module_blob_sha256")) != ("AMBIGUOUS_EXCLUDE", False, True, m["formal_conjectures"]["sha256"]): raise SystemExit("A056777 database sanity drift")

contract = (HERE / "CONTRACT.md").read_text()
for token in ("deliberately non-exhaustive", "tuple-domain exhaustion", "ordered factors", "shift 2"):
    if token not in contract: raise SystemExit(f"method-wall contract token absent: {token}")
workflow = (ROOT / ".github/workflows/oeis-a056777-development.yml").read_text()
for token in ("workflow_dispatch:", "60s python scripts/prepare_oeis_a056777_gate.py prepare", "60s python scripts/prepare_oeis_a056777_gate.py verify", "54s python scripts/search_oeis_a056777.py", "60s python scripts/verify_oeis_a056777_candidate.py candidate", "terminal-verification.txt", "if: always()", "final_code=0"):
    if token not in workflow: raise SystemExit(f"workflow safety token absent: {token}")
for forbidden in ("pull_request:", "push:", "repository_dispatch", "gh issue", "gh pr", "gh release"):
    if forbidden in workflow: raise SystemExit(f"forbidden publication token present: {forbidden}")
print("A056777 DEVELOPMENT freeze verified")
