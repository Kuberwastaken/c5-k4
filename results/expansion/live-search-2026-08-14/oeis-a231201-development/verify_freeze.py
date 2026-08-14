#!/usr/bin/env python3
"""Fail closed if any executable or contractual part of the A231201 freeze drifts."""
import hashlib,json,pathlib,re
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[3]
registry=json.loads((HERE/"freeze-files.json").read_text())
if registry.get("schema")!="oeis-a231201-frozen-files-v1": raise SystemExit("bad freeze registry schema")
expected={
 ".github/workflows/oeis-a231201-development.yml",
 "results/expansion/live-search-2026-08-14/oeis-a231201-development/CONTRACT.md",
 "results/expansion/live-search-2026-08-14/oeis-a231201-development/PRE_FREEZE_CORRECTION.md",
 "results/expansion/live-search-2026-08-14/oeis-a231201-development/contamination-control-l327.json",
 "results/expansion/live-search-2026-08-14/oeis-a231201-development/manifest.json",
 "results/expansion/live-search-2026-08-14/oeis-a231201-development/source-status-attestation.json",
 "results/expansion/live-search-2026-08-14/oeis-a231201-development/verify_freeze.py",
 "scripts/oeis_a231201_common.py","scripts/prepare_oeis_a231201_gate.py","scripts/search_oeis_a231201.py",
 "scripts/test_oeis_a231201_development.py","scripts/verify_oeis_a231201_artifacts.py","scripts/verify_oeis_a231201_coverage.py"}
if set(registry.get("sha256",{}))!=expected: raise SystemExit("freeze registry coverage drift")
for relative,want in registry["sha256"].items():
    path=ROOT/relative
    if not path.is_file(): raise SystemExit(f"missing frozen file: {relative}")
    got=hashlib.sha256(path.read_bytes()).hexdigest()
    if got!=want: raise SystemExit(f"frozen file drift: {relative}: {got}")
m=json.loads((HERE/"manifest.json").read_text())
if (m["internal_seconds"],m["external_seconds"],m["external_kill_after_seconds"])!=(54,60,6): raise SystemExit("deadline cap drift")
if m["initial_exponents"]!={"lo":1,"hi":4096} or m["gate_exact_prefix"]!=72 or m["gate_chunks"]!=8 or m.get("resumable") is not False: raise SystemExit("corrected gate/seed/resume drift")
if len(m["primes"])!=55 or m["primes"][-1]!=257 or m["solver"]!={"package":"ortools","version":"9.15.6755","workers":1,"random_seed":0,"objective":None}: raise SystemExit("finite universe/solver drift")
if set(m["partition"]["arms"].values())!={0,1} or m["partition"]["shards"]!=[0,1,2]: raise SystemExit("assignment partition drift")
correction=(HERE/"PRE_FREEZE_CORRECTION.md").read_text()
for token in ("supersedes the preflight","least positive representative","x=0` seed is removed","n=1,...,72"):
    if token not in correction: raise SystemExit(f"pre-freeze correction token absent: {token}")
coverage=(ROOT/"scripts/verify_oeis_a231201_coverage.py").read_text()
independent=coverage[coverage.index("def independent_coverage"):coverage.index("def final")]
if "=refine(" in independent.replace(" ","") or "VERIFICATION_FAILED_UNCOVERED_CLASS" not in coverage: raise SystemExit("independent verifier drift")
workflow=(ROOT/".github/workflows/oeis-a231201-development.yml").read_text()
for token in ("set +e","--kill-after=6s 60s","ortools==9.15.6755","arm: [A2_EQ_0, A2_EQ_1]","shard: [0, 1, 2]","diagnostic-attestation.json","contamination-control-l327.json","artifact-verification.txt","final-verification.json"):
    if token not in workflow: raise SystemExit(f"workflow safety token absent: {token}")
print("A231201 contaminated DEVELOPMENT freeze verified")
