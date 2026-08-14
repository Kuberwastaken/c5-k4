#!/usr/bin/env python3
"""Fail closed if the joint A109908/A109909 DEVELOPMENT freeze drifts."""
from __future__ import annotations
import ast,hashlib,json,pathlib

ROOT=pathlib.Path(__file__).resolve().parents[4];HERE=pathlib.Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

registry=json.loads((HERE/"freeze-files.json").read_text())
expected={
".github/workflows/oeis-a109908-a109909-development.yml",
"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development/CONTRACT.md",
"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development/controls.json",
"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development/manifest.json",
"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development/resolution-card.json",
"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development/source-status-attestation.json",
"results/expansion/live-search-2026-08-14/oeis-a109908-a109909-development/verify_freeze.py",
"scripts/prospective_oeis_a109908_a109909.py",
"scripts/test_prospective_oeis_a109908_a109909.py",
"scripts/verify_oeis_a109908_a109909_artifacts.py"}
if registry.get("schema")!="oeis-a109908-a109909-freeze-files-v1" or set(registry.get("sha256",{}))!=expected:raise SystemExit("freeze registry coverage drift")
for relative,digest in registry["sha256"].items():
    path=ROOT/relative
    if not path.is_file() or sha(path)!=digest:raise SystemExit(f"frozen file drift: {relative}")

m=json.loads((HERE/"manifest.json").read_text());spec=m["construction"]
if m.get("schema")!="oeis-a109908-a109909-development-freeze-v1" or m.get("development_only")is not True or m.get("target_evaluation_requires_exact_campaign_commit")is not True:raise SystemExit("manifest identity/lock drift")
if (m["internal_seconds"],m["external_search_seconds"],m["external_verify_seconds"])!=(48,54,60):raise SystemExit("cap drift")
if (m["historical_verified_through_n"],m["candidate_n_minimum"],m["candidate_n_maximum"])!=(1_000_000_000,1_000_000_001,1_500_000_000):raise SystemExit("candidate interval drift")
if math_lcm:=__import__('math').lcm(*spec["divisor_primes"]):
    if math_lcm!=spec["divisor_lcm"] or math_lcm<=m["candidate_n_maximum"]//2:raise SystemExit("lcm obstruction drift")
if spec["divisor_primes"]!=[2,3,5,7,11,13,17,19,23,29,31,37,41,43]:raise SystemExit("divisor universe drift")
if (spec["beam_width"],spec["profile_minimum_depth"],spec["construction_prefix_k"],m["shards"])!=(256,10,262144,16):raise SystemExit("profile universe drift")
partial=1
for q in spec["divisor_primes"][:spec["profile_minimum_depth"]]:partial*=q
if partial<=m["candidate_n_maximum"]//2:raise SystemExit("selected-profile lcm obstruction drift")
targets=m["formal_conjectures"]["targets"]
if [(x["sequence"],x["sha256"],x["declaration"]) for x in targets]!=[
('A109908','518c786ad769b81fb2495c0edf6d496205d304aa4fcca064ad94e5c0224afc96','OeisA109908.conjecture'),
('A109909','bb91d62d701549ae907e5f35a81c1c9bb0ba5ff4d7a5446eae643a0e5cf6ba47','OeisA109909.conjecture')]:raise SystemExit("formal target pin drift")
if m["oeis_source"].get("tree")!="658cfbde8e997e6f9c82f774309cda85c9b1da3c":raise SystemExit("OEIS tree pin drift")
status=json.loads((HERE/"source-status-attestation.json").read_text())
if status.get("local_project_commit")!=m["local_parent_commit"] or status.get("linked_public_proof_claim",{}).get("audit")!="PUBLIC_PROOF_CLAIM_AUDITED_INVALID" or status.get("fresh_race_check_required_at_execution")is not True:raise SystemExit("source/prior-art attestation drift")
if (status.get("oeisdata_commit"),status.get("oeisdata_tree"))!=(m["oeis_source"]["commit"],m["oeis_source"]["tree"]):raise SystemExit("OEIS status attestation drift")
card=json.loads((HERE/"resolution-card.json").read_text())
if card.get("logical_class")!="FINITE_UNIVERSAL" or card.get("finite_witness_suffices")is not True or card.get("correlated_cluster_count")!=1:raise SystemExit("resolution-card drift")

search=(ROOT/"scripts/prospective_oeis_a109908_a109909.py").read_text();replay=(ROOT/"scripts/verify_oeis_a109908_a109909_artifacts.py").read_text();tests=(ROOT/"scripts/test_prospective_oeis_a109908_a109909.py").read_text();workflow=(ROOT/".github/workflows/oeis-a109908-a109909-development.yml").read_text();contract=(HERE/"CONTRACT.md").read_text()
for text,name in ((search,"search"),(replay,"replay"),(tests,"tests")):ast.parse(text,filename=name)
for token in ("exact lowercase 40-hex campaign commit required","live source/race drift","live duplicate-search drift","ingestion/release race drift","Nat-safe symmetry failure","factorint(value)","frozen_profiles()","ordinal%M[\"shards\"]","signal.alarm(M[\"internal_seconds\"])","atomic_json(args.output/\"candidate.json\""):
    if token not in search:raise SystemExit(f"search safety token absent: {token}")
for token in ("inverse-paired","proper divisor bound drift","cover_replay","factorization drift","gate identity drift","chain hash drift","frozen profile/order drift","candidate hash drift","terminal reason drift"):
    if token not in replay:raise SystemExit(f"replay safety token absent: {token}")
for token in ("test_nat_safe_full_half_microfixtures","test_congruence_hypotheses_root_pairing_and_properness","test_lcm_obstruction","test_target_free_constructor_boundary","test_compact_cover_and_escape_replay_microfixtures"):
    if token not in tests:raise SystemExit(f"test absent: {token}")
for token in ("workflow_dispatch:","campaign_commit:","54s python scripts/prospective_oeis_a109908_a109909.py search","60s python scripts/verify_oeis_a109908_a109909_artifacts.py","if: always()","shard: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]"):
    if token not in workflow:raise SystemExit(f"workflow token absent: {token}")
for forbidden in ("pull_request:","push:","repository_dispatch","gh issue","gh pr","gh release"):
    if forbidden in workflow:raise SystemExit(f"forbidden workflow authority: {forbidden}")
for token in ("PUBLIC_PROOF_CLAIM_AUDITED_INVALID","gcd(k,q)=1","q=2","tighter even-`n` arm","Q=13,082,761,331,670,030","compact `candidate.json`","No target"):
    if token not in contract:raise SystemExit(f"contract token absent: {token}")
print("A109908/A109909 DEVELOPMENT freeze verified")
