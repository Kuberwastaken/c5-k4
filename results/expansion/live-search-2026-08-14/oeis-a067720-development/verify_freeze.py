#!/usr/bin/env python3
"""Fail closed if the executable A067720 DEVELOPMENT freeze drifts."""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "oeis-a067720-frozen-files-v1":
    raise SystemExit("bad freeze registry schema")
expected = {
    ".github/workflows/oeis-a067720-development.yml",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/duplicate-scan.json",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/manifest.json",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/method-wall-certificate.json",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/resolution-card.json",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/source-status-attestation.json",
    "results/expansion/live-search-2026-08-14/oeis-a067720-development/verify_freeze.py",
    "scripts/prepare_oeis_a067720_gate.py", "scripts/search_oeis_a067720.py",
    "scripts/test_oeis_a067720_development.py", "scripts/verify_oeis_a067720_candidate.py",
}
if set(registry.get("sha256", {})) != expected:
    raise SystemExit("freeze registry coverage drift")
for relative, digest in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file() or sha(path) != digest:
        raise SystemExit(f"frozen file drift: {relative}")

manifest = json.loads((HERE / "manifest.json").read_text())
if manifest.get("schema") != "oeis-a067720-development-freeze-v1" or manifest.get("development_only") is not True:
    raise SystemExit("manifest identity drift")
if (manifest["internal_seconds"], manifest["external_search_seconds"], manifest["external_verify_seconds"]) != (48, 54, 60):
    raise SystemExit("deadline cap drift")
if manifest["shards"] != 24 or manifest["checkpoint_interval"] != 128 or manifest["k_maximum"] != 2_000_000_000:
    raise SystemExit("domain/checkpoint drift")
if set(manifest["arms"]) != {"SUCCESSOR_PROFILE_SURGERY", "TOTIENT_RATIO_WALL"}:
    raise SystemExit("arm drift")
profiles = manifest["profile_catalogues"]
expected_profile_constants = {
    "successor_prime_rank_last": 512,
    "successor_single_exponents": list(range(2, 13)),
    "successor_mixed_exponent_pairs": [[1, 1], [1, 2], [2, 1], [2, 2], [1, 3], [3, 1]],
    "endpoint_prime_rank_last": 768,
    "endpoint_single_exponents": list(range(1, 17)),
    "endpoint_mixed_exponent_pairs": [[1, 1], [1, 2], [2, 1], [2, 2], [1, 3], [3, 1]],
    "endpoint_entries": 1771382,
    "endpoint_stream_sha256": "36fde67d9061e145ad13433ee3970b389a1b89fec68383d05d86cc5ec66aba9f",
    "catalogue_only_benchmark_cap_seconds": 48,
}
if profiles != expected_profile_constants:
    raise SystemExit("profile catalogue drift")
if (manifest["arms"]["SUCCESSOR_PROFILE_SURGERY"]["eligible_profiles"],
    manifest["arms"]["SUCCESSOR_PROFILE_SURGERY"]["profile_stream_sha256"]) != (
        824, "874265641522493fd4937f2230560c70947972b46c6d4ddc744a35cd9a0a09e5"):
    raise SystemExit("single-successor stream drift")
if (manifest["arms"]["TOTIENT_RATIO_WALL"]["eligible_profiles"],
    manifest["arms"]["TOTIENT_RATIO_WALL"]["profile_stream_sha256"]) != (
        269943, "3839a9808e6b6a9b2960eabbfca42656c99b61c22c87d10ba7db6a453b2de84e"):
    raise SystemExit("mixed-successor stream drift")

formal = manifest["formal_conjectures"]
if (formal["commit"], formal["tree"], formal["path"], formal["sha256"], formal["declaration"], formal["category"]) != (
    "05ea0345d09375efac830fac93bf083b654e317e", "002d0d472115157683c0ecf7f2290f2383bea58f",
    "FormalConjectures/OEIS/67720.lean", "af8ae5ba8ebed4d7252b9cee3d6cb7e304f7971282db7f8954ce2f0da99d249e",
    "OeisA67720.prime_add_one_of_a", "research open"):
    raise SystemExit("formal source pin drift")
if manifest["oeis_source"]["sha256"] != "13c478e7850f14ecf1f3ed5a78a28ffee42ef6429539943b87a068fe3c761aa4" or manifest["oeis_bfile"] != {
    "url": "https://oeis.org/A067720/b067720.txt", "sha256": "c50d6120a72dfda1f6bf82642407007ea68604c76788a8e98c2f43cfeb9bb928",
    "rows": 10000, "last_index": 10000, "last_value": 1548870}:
    raise SystemExit("OEIS pin drift")

status = json.loads((HERE / "source-status-attestation.json").read_text())
duplicate = json.loads((HERE / "duplicate-scan.json").read_text())
card = json.loads((HERE / "resolution-card.json").read_text())
wall = json.loads((HERE / "method-wall-certificate.json").read_text())
if status.get("audited_at_utc") != "2026-08-14T17:38:27Z" or status.get("source_reading") != "UNAMBIGUOUS" or status.get("formal_conjectures_status") != "research open" or status.get("known_exception") != 8 or status.get("disposition") != "DEVELOPMENT_ONLY_UNCLAIMED_AT_FREEZE":
    raise SystemExit("source/status attestation drift")
maintenance = status.get("open_exact_path_maintenance_prs")
if set(maintenance or {}) != {"4198", "4688"} or maintenance["4198"].get("classification") != "NON_RESOLVING_STALE_NORMALIZATION" or maintenance["4688"].get("classification") != "NON_RESOLVING_MODULE_MAINTENANCE":
    raise SystemExit("open exact-path maintenance classification drift")
touches = duplicate.get("open_pull_request_target_path_matches")
if duplicate.get("audited_at_utc") != "2026-08-14T17:38:27Z" or duplicate.get("resolution_match_found") is not False or [item.get("number") for item in touches or []] != [4198, 4688] or duplicate.get("local_release_claims") != []:
    raise SystemExit("duplicate scan drift")
required_card = {"logical_class": "FINITE_UNIVERSAL", "finite_witness_suffices": True,
                 "answer_placeholder": False, "eventual_quantifier": False,
                 "global_constant_quantifier": False, "unbounded_auxiliary_search": False,
                 "source_reading": "UNAMBIGUOUS", "development_set": True}
if any(card.get(key) != value for key, value in required_card.items()):
    raise SystemExit("resolution-card drift")
if wall.get("evaluation_rule") != "no residual is evaluated unless both profiles satisfy the exact rigid translation" or wall.get("known_exception", {}).get("k") != 8:
    raise SystemExit("method-wall certificate drift")

prepare = (ROOT / "scripts/prepare_oeis_a067720_gate.py").read_text()
search = (ROOT / "scripts/search_oeis_a067720.py").read_text()
verifier = (ROOT / "scripts/verify_oeis_a067720_candidate.py").read_text()
tests = (ROOT / "scripts/test_oeis_a067720_development.py").read_text()
workflow = (ROOT / ".github/workflows/oeis-a067720-development.yml").read_text()
contract = (HERE / "CONTRACT.md").read_text()
for token in ("open_pull_path_matches", "previous_filename", "changeType", "release_page_sizes", "SEARCH_QUERIES", "known_ingestion_pull", "incomplete_results", "total_count", "path_row_keys", "duplicate open PR target-path row", "verify_catalogue",
              "live upstream head/tree drift", "catalogue row {index} left prime-prime baseline"):
    if token not in prepare:
        raise SystemExit(f"source/status gate token absent: {token}")
for token in ("endpoint_catalogue", "successor_profiles", "NO_TRANSLATED_ENDPOINT_PROFILE",
              "No fallible ledger write is allowed after it", "signal.alarm(M[\"internal_seconds\"])"):
    if token not in search:
        raise SystemExit(f"search algebra/safety token absent: {token}")
for token in ("independent_primes", "certificate is not canonical JSON bytes", "ledger noncanonical-byte drift",
              "first survivor and final visited state", "terminal visited must be a nonnegative integer",
              "terminal certificate_present must be Boolean", "false frozen-domain exhaustion"):
    if token not in verifier:
        raise SystemExit(f"independent verifier token absent: {token}")
if ast.dump(ast.parse(search)) == ast.dump(ast.parse(verifier)):
    raise SystemExit("runner/verifier are not separate implementations")
for token in ("Target-free", "test_no_residual_evaluation_without_endpoint_profile",
              "test_certificate_rename_failure", "test_no_ledger_append_after_durable_candidate",
              "test_live_duplicate_snapshot_requires_complete_known_baseline", "test_renamed_away_target_is_a_path_touch",
              "test_ledger_rejects_missing_newline_whitespace_and_extra_key", "test_terminal_rejects_extra_key_and_negative_or_boolean_visited",
              "test_replay_rejects_early_survivor_followed_by_later_state"):
    if token not in tests:
        raise SystemExit(f"test token absent: {token}")
for token in ("workflow_dispatch:", "54s python scripts/search_oeis_a067720.py",
              "60s python scripts/verify_oeis_a067720_candidate.py candidate",
              "60s python scripts/verify_oeis_a067720_candidate.py terminal", "if: always()", "final_code=0"):
    if token not in workflow:
        raise SystemExit(f"workflow safety token absent: {token}")
for forbidden in ("pull_request:", "push:", "repository_dispatch", "gh issue", "gh pr", "gh release"):
    if forbidden in workflow:
        raise SystemExit(f"forbidden publication token present: {forbidden}")
for token in ("never scans", "1,771,382", "48-second", "no issue, pull request, release"):
    if token not in contract:
        raise SystemExit(f"contract token absent: {token}")

print("A067720 DEVELOPMENT freeze verified")
