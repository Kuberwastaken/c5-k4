#!/usr/bin/env python3
"""Fail closed on any executable or contractual drift in the A231201 v2 freeze."""
import hashlib,json,pathlib
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[3]
registry=json.loads((HERE/"freeze-files.json").read_text())
if registry.get("schema")!="oeis-a231201-v2-frozen-files-v1": raise SystemExit("bad v2 freeze registry schema")
expected={
 ".github/workflows/oeis-a231201-v2-development.yml",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-design-scout.md",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development/CONTRACT.md",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development/CORRECTION.md",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development/V1_RESULT_ADDENDUM.md",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development/manifest.json",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development/source-status-attestation.json",
 "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development/verify_freeze.py",
 "scripts/adversary_oeis_a231201_v2.py","scripts/construct_oeis_a231201_v2.py","scripts/oeis_a231201_v2_common.py",
 "scripts/prepare_oeis_a231201_v2_gate.py","scripts/record_oeis_a231201_v2_execution.py","scripts/test_oeis_a231201_v2_constructors.py",
 "scripts/verify_oeis_a231201_v2_artifacts.py","scripts/verify_oeis_a231201_v2_execution.py","scripts/verify_oeis_a231201_v2_final.py"}
if set(registry.get("sha256",{}))!=expected: raise SystemExit("v2 registry coverage drift")
for relative,want in registry["sha256"].items():
    path=ROOT/relative
    if not path.is_file(): raise SystemExit(f"missing v2 frozen file: {relative}")
    got=hashlib.sha256(path.read_bytes()).hexdigest()
    if got!=want: raise SystemExit(f"v2 frozen file drift: {relative}: {got}")
v1_registry=ROOT/"results/expansion/live-search-2026-08-14/oeis-a231201-development/freeze-files.json"
if hashlib.sha256(v1_registry.read_bytes()).hexdigest()!="0ad5de66077602e8ae173aa9b9bd81b0dd47b5792689c232d254e5f90c7d05bb": raise SystemExit("v1 freeze registry drift")
m=json.loads((HERE/"manifest.json").read_text())
if (m["internal_seconds"],m["external_seconds"],m["external_kill_after_seconds"])!=(54,60,6): raise SystemExit("54/60 cap drift")
if m["cp_slice_seconds"]>15 or m["cp_slices_per_construction"]!=3 or m["construction_rounds"]!=3 or m["assignment_slots_per_round"]!=1 or m["resumable"] is not False: raise SystemExit("frozen limit drift")
if len(m["primes"])!=55 or m["primes"][-1]!=257 or m["combined_period"]!="249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200": raise SystemExit("arithmetic universe drift")
if m["arms"]!=["COMPRESSED_SET_COVER_CP","DETERMINISTIC_GREEDY_REPAIR","SMALL_BASIS_CEGAR"] or len(m["partition_cells"])!=6: raise SystemExit("arm/cell matrix drift")
if m["small_basis"]!={"initial_rows":192,"growth_rows":64,"growth_every_rounds":4,"permutation":"sort x=1..4096 by (12-bit reversal of x-1, x)","salt":"A231201-v2-low-discrepancy-2026-08-14"}: raise SystemExit("small-basis freeze drift")
if m["forbidden_statuses"]!=["NO_COMPLETE_COVER"]: raise SystemExit("forbidden vocabulary drift")
workflow=(ROOT/".github/workflows/oeis-a231201-v2-development.yml").read_text()
for token in ("construct-r0:\n    needs: [validate-frozen-harness, prepare-database-gate]\n    if: always()","adversary-r0:","construct-r1:","adversary-r1:","construct-r2:","adversary-r2:","independent-final:","--kill-after=6s 60s","if: always()","continue-on-error: true","stage-diagnostic-terminal.json","STAGE_TERMINAL_UNAVAILABLE","Finalize stage diagnostic and checksums","record_oeis_a231201_v2_execution.py","--prerequisite-check-exit-code","round: [0, 1, 2]","COMPRESSED_SET_COVER_CP, DETERMINISTIC_GREEDY_REPAIR, SMALL_BASIS_CEGAR"):
    if token not in workflow: raise SystemExit(f"workflow safety token absent: {token}")
if workflow.count("verify_oeis_a231201_v2_execution.py")!=10: raise SystemExit("predecessor execution edge coverage drift")
if "360s" in workflow or "360" in json.dumps(m): raise SystemExit("superseded cap present")
constructor=(ROOT/"scripts/construct_oeis_a231201_v2.py").read_text()
for token in ("model.add(sum(","<=1)","model.add_hint","add_decision_strategy","DUPLICATE_ASSIGNMENT_SKIPPED","original_assignment_artifact_sha256","original_adversary_receipt_sha256","singly_covered","least_prime_prefix","basis-delta-","bit_count()"):
    if token not in constructor: raise SystemExit(f"constructor invariant absent: {token}")
final=(ROOT/"scripts/verify_oeis_a231201_v2_final.py").read_text()
independent=final[final.index("def independent_coverage"):final.index("def crt_all")]
if "refine(" in independent or "VERIFICATION_FAILED_UNCOVERED_CLASS" not in final: raise SystemExit("independent-final drift")
artifact=(ROOT/"scripts/verify_oeis_a231201_v2_artifacts.py").read_text()
for token in ("verified_gate(a)","read_candidate","COMPLETE_COVER","crt_all(assignment)","forged final CRT/result","candidate_sha256"):
    if token not in artifact: raise SystemExit(f"artifact verifier guard absent: {token}")
execution=(ROOT/"scripts/record_oeis_a231201_v2_execution.py").read_text()
if "a.artifact_verifier_exit_code or a.prerequisite_check_exit_code or a.stage_exit_code" not in execution: raise SystemExit("execution precedence drift")
predecessor=(ROOT/"scripts/verify_oeis_a231201_v2_execution.py").read_text()
for token in ('--terminal','prerequisite!=0','artifact!=0','job!=stage_code','CAP_EXHAUSTED_NO_ASSIGNMENT','NOT_RUN','ADVERSARY_DEADLINE','WORKER_ERROR'):
    if token not in predecessor: raise SystemExit(f"predecessor-success verifier drift: {token}")
tests=(ROOT/"scripts/test_oeis_a231201_v2_constructors.py").read_text()
for forbidden_import in ("import construct_oeis_a231201_v2","import adversary_oeis_a231201_v2","import verify_oeis_a231201_v2_final"):
    if forbidden_import in tests: raise SystemExit("tests import target evaluator")
addendum=(HERE/"V1_RESULT_ADDENDUM.md").read_text()
if 'final_verifier_status="NOT_RUN"' not in addendum or '`final_verifier_exit_code=null`' not in addendum: raise SystemExit("v1 absent-final correction drift")
print("A231201 v2 contaminated DEVELOPMENT freeze verified")
