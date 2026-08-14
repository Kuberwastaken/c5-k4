#!/usr/bin/env python3
"""Fail closed if any executable part of the A105720 freeze drifts."""
import hashlib, json, pathlib, re

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
registry=json.loads((HERE/"freeze-files.json").read_text())
if registry.get("schema")!="oeis-a105720-frozen-files-v1": raise SystemExit("bad freeze registry schema")
for relative,expected in registry["sha256"].items():
    path=ROOT/relative
    if not path.is_file(): raise SystemExit(f"missing frozen file: {relative}")
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=expected: raise SystemExit(f"frozen file drift: {relative}: {actual}")

m=json.loads((HERE/"manifest.json").read_text())
if (m["shards"],m["internal_seconds"],m["external_seconds"],m["child_seconds"])!=(24,54,60,4): raise SystemExit("cap drift")
if set(m["arms"])!={"CATALOGUE","GENERIC","WALL_NAVIGATION"}: raise SystemExit("arm drift")
workflow=(ROOT/".github/workflows/oeis-a105720-development.yml").read_text()
if workflow.count("shard: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]")!=1: raise SystemExit("workflow shard drift")
for token in ("set +e","60s python scripts/search_oeis_a105720.py","terminal-verification.txt","sums_code=$?","final_code=0"):
    if token not in workflow: raise SystemExit(f"workflow safety token absent: {token}")
print("A105720 DEVELOPMENT freeze verified")
