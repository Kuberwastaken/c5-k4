#!/usr/bin/env python3
"""Fail closed if the executable A108569 DEVELOPMENT freeze drifts."""
from __future__ import annotations
import ast, hashlib, json, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

registry=json.loads((HERE/"freeze-files.json").read_text())
expected={
".github/workflows/oeis-a108569-development.yml",
"lean/Oeis108569EnumerationBridge.lean",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/CONTRACT.md",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/duplicate-scan.json",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/manifest.json",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/method-wall-certificate.json",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/resolution-card.json",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/source-status-attestation.json",
"results/expansion/live-search-2026-08-14/oeis-a108569-development/verify_freeze.py",
"scripts/prepare_oeis_a108569_gate.py","scripts/search_oeis_a108569.py",
"scripts/test_oeis_a108569_development.py","scripts/verify_oeis_a108569_candidate.py"}
if registry.get("schema")!="oeis-a108569-frozen-files-v1" or set(registry.get("sha256",{}))!=expected:
    raise SystemExit("freeze registry identity/coverage drift")
for relative,digest in registry["sha256"].items():
    path=ROOT/relative
    if not path.is_file() or sha(path)!=digest: raise SystemExit(f"frozen file drift: {relative}")

manifest=json.loads((HERE/"manifest.json").read_text())
if manifest.get("schema")!="oeis-a108569-development-freeze-v1" or manifest.get("development_only") is not True:
    raise SystemExit("manifest identity drift")
if (manifest["internal_seconds"],manifest["external_search_seconds"],manifest["external_verify_seconds"])!=(48,54,60):
    raise SystemExit("cap drift")
if manifest["shards"]!=24 or manifest["k_maximum"]!=2_000_000_000 or manifest["endpoint_exclusive_maximum"]!=4_000_000_000:
    raise SystemExit("domain drift")
formal=manifest["formal_conjectures"]
if (formal["commit"],formal["tree"],formal["path"],formal["blob_sha1"],formal["sha256"],formal["declaration"],formal["category"])!=(
"6c0950bec7743f5098c0196c6aee7b22c1ec8005","5af0d2a3a319ee2458f8cd061db7c49aeba1b35e",
"FormalConjectures/OEIS/108569.lean","daf4427246c28b56a429646958a2c38ca4cf04fa",
"0e62b2d15f41a2b2dbcc568a63abd3644e8429fa7befdec7cc2d0e96cc6244f8",
"OeisA108569.conjecture","research open"): raise SystemExit("formal pin drift")
if manifest["oeis_source"]["path"]!="seq/A108/A108569.seq" or manifest["oeis_source"]["sha256"]!="66a98eb6032c98c12f6bf8250c30356775c434fae4ca4cc2b8ed98eb04d83d9f":
    raise SystemExit("OEIS source pin drift")
if manifest["oeis_bfile"]!={"url":"https://oeis.org/A108569/b108569.txt","sha256":"a84aa7eb3295768365d07e081bcaf7b4f0b6d412b6e0615128d615148c238544","rows":384,"first_index":1,"first_value":1,"last_index":384,"last_value":997694}:
    raise SystemExit("b-file pin drift")
if manifest.get("catalogue_control")!={"verified_row_stream_sha256":"d140a3345fcdad615fffef3a193216095e6f143f924d4c600155a9f54e1cad11","even_lift_checks":383,"divisor_lift_checks":6511,"sophie_germain_controls":5}:
    raise SystemExit("catalogue control pin drift")
bridge=manifest.get("enumeration_bridge",{})
if bridge!={"path":"lean/Oeis108569EnumerationBridge.lean","sha256":"f04975ea522a36681a2a467ec0e8c0d65d41689f8b96699654b41aa07ba0a2bd","mathlib_commit":"a3a10db0e9d66acbebf76c5e6a135066525ac900","target_free":True,"compiled_warning_as_error":True,"concrete_candidate_status":"PENDING_FORMALIZATION"} or sha(ROOT/bridge["path"])!=bridge["sha256"]:
    raise SystemExit("enumeration bridge drift")
spec=manifest["profile_catalogues"]
if spec["core_support_counts"]!={"1":482,"2":33584,"3":745665} or spec["endpoint_entries"]!=880891 or spec["endpoint_stream_sha256"]!="a15e04d2f9db38ebb894e1f6831e72aaf99a7b2427196dd781ddbe43de83a248":
    raise SystemExit("catalogue pin drift")
if (spec["catalogue_only_benchmark_elapsed_seconds"],spec["catalogue_only_benchmark_peak_rss_kib"])!=(13.56,313876):
    raise SystemExit("benchmark pin drift")
if set(manifest["arms"])!={"CATALOGUE_LIFT_CONTROL","ODD_CORE_PROFILES","ODD_COLLISION_WALL"}:
    raise SystemExit("arm drift")
if manifest.get("local_parent_commit")!="cc2c4927e414e4c2799fa308a7b865be90e79574":
    raise SystemExit("local parent boundary drift")
status=json.loads((HERE/"source-status-attestation.json").read_text())
duplicate=json.loads((HERE/"duplicate-scan.json").read_text())
if status.get("local_project_commit")!=manifest["local_parent_commit"] or duplicate.get("local_project_commit")!=manifest["local_parent_commit"]:
    raise SystemExit("local history attestation drift")

prepare=(ROOT/"scripts/prepare_oeis_a108569_gate.py").read_text()
search=(ROOT/"scripts/search_oeis_a108569.py").read_text()
verifier=(ROOT/"scripts/verify_oeis_a108569_candidate.py").read_text()
tests=(ROOT/"scripts/test_oeis_a108569_development.py").read_text()
workflow=(ROOT/".github/workflows/oeis-a108569-development.yml").read_text()
contract=(HERE/"CONTRACT.md").read_text()
for source,name in ((prepare,"prepare"),(search,"search"),(verifier,"verifier")):
    ast.parse(source,filename=name)
for token in ("OPEN_PULL_COUNT = 279","FULL_FILE_PAGE_SIZES","INGESTION_TARGET_FILE","previous_filename",
              "upstream_release_page_sizes","SOPHIE_GERMAIN_CONTROLS","verify_catalogue","live upstream head/tree drift"):
    if token not in prepare: raise SystemExit(f"gate token absent: {token}")
for token in ("TARGET_ARMS = (\"ODD_CORE_PROFILES\", \"ODD_COLLISION_WALL\")","SUPPORT_RHO_MISMATCH",
              "EXPONENT_LATTICE_MISMATCH","support_pair_completed","SUPPORT_PAIR_COMPLETE",
              "signal.alarm(M[\"internal_seconds\"])","atomic_json(args.certificate","SEMANTIC_CANDIDATE_ONLY"):
    if token not in search and token!="SEMANTIC_CANDIDATE_ONLY": raise SystemExit(f"search token absent: {token}")
for token in ("i := Nat.count A k","Nat.nth_count","not a Lean proof","canonical(expected)",
              "odd_profile_domain_only","false domain exhaustion","checkpoint boundary/semantic replay drift"):
    if token not in verifier: raise SystemExit(f"verifier token absent: {token}")
for token in ("test_target_free_profile_constructor_pins","test_live_audit_rejects_pagination_omission_and_zero_forgery",
              "test_core_rejects_rho_before_residual","test_lattice_rejects_before_residual",
              "test_checkpoint_pair_and_interval_boundaries","test_candidate_atomic_commit_precedes_no_ledger_append"):
    if token not in tests: raise SystemExit(f"test token absent: {token}")
for token in ("workflow_dispatch:","54s python scripts/search_oeis_a108569.py",
              "60s python scripts/verify_oeis_a108569_candidate.py candidate",
              "60s python scripts/verify_oeis_a108569_candidate.py terminal","if: always()",
              "arm: [ODD_CORE_PROFILES, ODD_COLLISION_WALL]","final_code=0",
              "test \"$(git show -s --format=%P HEAD)\" = \"cc2c4927e414e4c2799fa308a7b865be90e79574\"",
              "validate-lean-bridge:","ref: a3a10db0e9d66acbebf76c5e6a135066525ac900",
              "240s lake exe cache get","180s lake env lean -DwarningAsError=true",
              "#print axioms A108569EnumerationBridge.exists_pos_index_of_member",
              "! grep -F 'sorryAx'"):
    if token not in workflow: raise SystemExit(f"workflow safety token absent: {token}")
for forbidden in ("pull_request:","push:","repository_dispatch","gh issue","gh pr","gh release"):
    if forbidden in workflow: raise SystemExit(f"forbidden workflow authority: {forbidden}")
for token in ("fail-closed pre-evaluation dispatch","31830066668","880,891","13.56 seconds","no target evaluation, dispatch",
              "compiled, no-`sorry` Lean lemma"):
    if token not in contract: raise SystemExit(f"contract token absent: {token}")
print("A108569 DEVELOPMENT freeze verified")
