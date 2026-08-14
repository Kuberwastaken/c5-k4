#!/usr/bin/env python3
"""Fail closed if any executable part of the A063880 freeze drifts."""
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[3]
registry=json.loads((HERE/"freeze-files.json").read_text())
if registry.get("schema")!="oeis-a063880-frozen-files-v1": raise SystemExit("bad freeze registry schema")
expected={".github/workflows/oeis-a063880-development.yml","results/expansion/live-search-2026-08-14/oeis-a063880-development/CONTRACT.md","results/expansion/live-search-2026-08-14/oeis-a063880-development/manifest.json","results/expansion/live-search-2026-08-14/oeis-a063880-development/source-status-attestation.json","results/expansion/live-search-2026-08-14/oeis-a063880-development/verify_freeze.py","scripts/prepare_oeis_a063880_gate.py","scripts/search_oeis_a063880.py","scripts/test_oeis_a063880_development.py","scripts/verify_oeis_a063880_candidate.py"}
if set(registry.get("sha256",{}))!=expected: raise SystemExit("freeze registry coverage drift")
for relative,expected in registry["sha256"].items():
    path=ROOT/relative
    if not path.is_file(): raise SystemExit(f"missing frozen file: {relative}")
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=expected: raise SystemExit(f"frozen file drift: {relative}: {actual}")
m=json.loads((HERE/"manifest.json").read_text())
if (m["shards"],m["internal_seconds"],m["external_seconds"],m["child_seconds"])!=(24,54,60,4): raise SystemExit("cap drift")
if set(m["arms"])!={"CATALOGUE","GENERIC","WALL_NAVIGATION"}: raise SystemExit("arm drift")
if m["historical_exclusion_upper_exclusive"]!=10**18 or m["universe"]["minimum_core"]!=10**18: raise SystemExit("historical-boundary drift")
workflow=(ROOT/".github/workflows/oeis-a063880-development.yml").read_text()
for token in ("set +e","60s python scripts/search_oeis_a063880.py","terminal-verification.txt","sums_code=$?","final_code=0"):
    if token not in workflow: raise SystemExit(f"workflow safety token absent: {token}")
print("A063880 DEVELOPMENT freeze verified")
