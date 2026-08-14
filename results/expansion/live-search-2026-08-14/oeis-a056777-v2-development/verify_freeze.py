#!/usr/bin/env python3
"""Fail closed if the executable A056777 v2 DEVELOPMENT freeze drifts."""
from __future__ import annotations

import ast, hashlib, json, math, pathlib

HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def sha(path:pathlib.Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()

registry=json.loads((HERE/"freeze-files.json").read_text())
if registry.get("schema")!="oeis-a056777-v2-frozen-files-v1":raise SystemExit("bad freeze registry schema")
expected={
 ".github/workflows/oeis-a056777-v2-development.yml",
 "results/expansion/live-search-2026-08-14/oeis-a056777-v2-development/CONTRACT.md",
 "results/expansion/live-search-2026-08-14/oeis-a056777-v2-development/denominator-window-certificate.json",
 "results/expansion/live-search-2026-08-14/oeis-a056777-v2-development/duplicate-scan.json",
 "results/expansion/live-search-2026-08-14/oeis-a056777-v2-development/manifest.json",
 "results/expansion/live-search-2026-08-14/oeis-a056777-v2-development/source-status-attestation.json",
 "results/expansion/live-search-2026-08-14/oeis-a056777-v2-development/verify_freeze.py",
 "scripts/prepare_oeis_a056777_v2_gate.py","scripts/search_oeis_a056777_v2.py",
 "scripts/test_oeis_a056777_v2_development.py","scripts/verify_oeis_a056777_v2_candidate.py"}
if set(registry.get("sha256",{}))!=expected:raise SystemExit("freeze registry coverage drift")
for relative,digest in registry["sha256"].items():
 path=ROOT/relative
 if not path.is_file() or sha(path)!=digest:raise SystemExit(f"frozen file drift: {relative}")

m=json.loads((HERE/"manifest.json").read_text())
if (m["internal_seconds"],m["external_search_seconds"],m["external_verify_seconds"])!=(48,54,60):raise SystemExit("deadline cap drift")
if (m["r_rank_first"],m["r_rank_last"],m["block_prime_rank_first"],m["block_prime_rank_last"])!=(385,640,1,640):raise SystemExit("rank domain drift")
if set(m["arms"])!={"REPEATED_LOWER","REPEATED_UPPER"}:raise SystemExit("orientation drift")
if m["historical_exclusion_upper_inclusive"]!=10**12 or m["value_minimum"]!=10**12+1 or m["value_maximum"]+12>=2**64:raise SystemExit("band drift")
if m["prior_freeze"]!={"manifest_sha256":"5c7c4fb1153f365ecaac7b5309c5ed4f96bf3db7c64078e344d8f2b3aaa43b7c","repeated_power_base_rank_last":384,"squarefree_smallest_rank_last":96,"squarefree_middle_prime_offsets":96,"squarefree_terminal_prime_offsets":256,"pure_prime_power_covered":True}:raise SystemExit("prior-domain exclusion drift")

status=json.loads((HERE/"source-status-attestation.json").read_text());duplicate=json.loads((HERE/"duplicate-scan.json").read_text())
if status.get("audited_at_utc")!="2026-08-14T17:03:05Z" or status.get("inherited_v1_attestation_sha256")!="c0e1d08c34a1508b0ca93b3b9b12b59342e3d1753582c8951e683bdfc2d9288e" or status.get("formal_conjectures_status")!="research open" or status.get("upstream_resolution_match_found") is not False:raise SystemExit("source status drift")
maintenance=status.get("open_exact_path_maintenance_prs")
if maintenance!={"numbers":[3691,4025,4356,4428],"classification":"NON_RESOLVING_AUXILIARY_MAINTENANCE","rationale":"Each PR changes only two push_neg calls to push Not in already proved auxiliary modular lemmas; the A056777 target declaration, research-open category, and sorry state are untouched. Exact A056777/declaration open issue and PR searches are empty."}:raise SystemExit("exact-path maintenance PR classification drift")
if duplicate.get("inherited_v1_duplicate_scan_sha256")!="1d5e3c4c0618a6681b5c1df5097768518afad50c26945273cad2ee716a51f363" or duplicate.get("provenance_database_match_found") is not True or duplicate.get("novelty_claim_permitted") is not False:raise SystemExit("duplicate gate drift")
v1=ROOT/"results/expansion/live-search-2026-08-14/oeis-a056777-development"
if sha(v1/"manifest.json")!=m["prior_freeze"]["manifest_sha256"] or sha(v1/"source-status-attestation.json")!=status["inherited_v1_attestation_sha256"] or sha(v1/"duplicate-scan.json")!=duplicate["inherited_v1_duplicate_scan_sha256"]:raise SystemExit("inherited v1 gate drift")
database=json.loads((ROOT/"results/benchmark/v1.4-f0a/registry/eligible-cluster-pool.json").read_text());matches=[]
def visit(value):
 if isinstance(value,dict):
  if value.get("cluster_id")=="fc-module:FormalConjectures/OEIS/56777":matches.append(value)
  for child in value.values():visit(child)
 elif isinstance(value,list):
  for child in value:visit(child)
visit(database)
if len(matches)!=1 or (matches[0].get("classification_status"),matches[0].get("eligible"),matches[0].get("semantic_exposure"),matches[0].get("module_blob_sha256"))!=("AMBIGUOUS_EXCLUDE",False,True,m["formal_conjectures"]["sha256"]):raise SystemExit("database duplicate gate drift")

# Recompute the finite index constants and the strict completeness widths using
# only frozen bounds.  No tuple's p, q, n, primality, or target equations run.
flags=bytearray(b"\x01")*8193;flags[:2]=b"\x00\x00"
for p in range(2,math.isqrt(8192)+1):
 if flags[p]:flags[p*p:8193:p]=b"\x00"*(((8192-p*p)//p)+1)
primes=[n for n,flag in enumerate(flags) if flag][:640]
proof=json.loads((HERE/"denominator-window-certificate.json").read_text());qmax=primes[-2]*primes[-1];tmin=primes[0]+primes[1];tmax=primes[-2]+primes[-1]
if sha(ROOT/"results/expansion/live-search-2026-08-14/oeis-a056777-near-wall-surgery.md")!=proof["surgery_note_sha256"]:raise SystemExit("surgery source drift")
if (len(primes),640*639//2,primes[384],primes[639],qmax,tmin,tmax)!=(proof["prime_count"],proof["semiprime_block_count"],proof["first_r"],proof["last_r"],proof["q_max"],proof["t_plus_u_min"],proof["t_plus_u_max"]):raise SystemExit("window proof constants drift")
widths={"REPEATED_LOWER":[],"REPEATED_UPPER":[]}
for rank in range(385,641):
 r=primes[rank-1]
 pmin=(m["value_minimum"]+r*r-1)//(r*r);bound=24+qmax*max(abs(2*tmin-2*r-1),abs(2*tmax-2*r-1));widths["REPEATED_LOWER"].append(bound//pmin+1)
 pmin=(m["value_minimum"]+qmax-1)//qmax;bound=max(abs(12+r*r*(2*r+1-2*tmin)),abs(12+r*r*(2*r+1-2*tmax)));widths["REPEATED_UPPER"].append(bound//pmin+1)
if [widths["REPEATED_LOWER"][0],widths["REPEATED_LOWER"][-1]]!=proof["repeated_lower_width_first_last"] or [widths["REPEATED_UPPER"][0],widths["REPEATED_UPPER"][-1]]!=proof["repeated_upper_width_first_last"] or proof.get("target_values_evaluated_to_prepare_certificate")!=0:raise SystemExit("window proof width drift")

search=(ROOT/"scripts/search_oeis_a056777_v2.py").read_text();verifier=(ROOT/"scripts/verify_oeis_a056777_v2_candidate.py").read_text();contract=(HERE/"CONTRACT.md").read_text();workflow=(ROOT/".github/workflows/oeis-a056777-v2-development.yml").read_text()
for token in ("24+qblock*(2*total-2*r-1)","12+r*r*(2*r+1-2*total)","semiprime_index", "PRIOR_FROZEN", "Never touch the"):
 if token not in search:raise SystemExit(f"search algebra/safety token absent: {token}")
for token in ("build_pairs","independent_result","candidate omission","preceding checkpoint","ROW_KEYS","raw.endswith(b\"\\n\")","byte-canonical","first_survivor[0]!=visited-1"):
 if token not in verifier:raise SystemExit(f"independent verifier token absent: {token}")
if ast.dump(ast.parse(search))==ast.dump(ast.parse(verifier)):raise SystemExit("runner/verifier are not separate implementations")
tests=(ROOT/"scripts/test_oeis_a056777_v2_development.py").read_text()
for token in ("test_formulas_8_9_10","Target-free","no_ledger_append_occurs_after_durable_certificate","certificate_rename_failure","ledger_requires_exact_ascii_newline_and_canonical_rows","replay_rejects_early_candidate_followed_by_later_state"):
 if token not in tests:raise SystemExit(f"test token absent: {token}")
for token in ("workflow_dispatch:","54s python scripts/search_oeis_a056777_v2.py","60s python scripts/verify_oeis_a056777_v2_candidate.py candidate","terminal-verification.txt","if: always()","final_code=0"):
 if token not in workflow:raise SystemExit(f"workflow safety token absent: {token}")
for forbidden in ("pull_request:","push:","repository_dispatch","gh issue","gh pr","gh release"):
 if forbidden in workflow:raise SystemExit(f"forbidden publication token present: {forbidden}")
for token in ("first 640 primes","(8)","(9 reversed)","never appends to the","raw bytes","first survivor"):
 if token not in contract:raise SystemExit(f"contract token absent: {token}")
print("A056777 v2 DEVELOPMENT freeze verified")
