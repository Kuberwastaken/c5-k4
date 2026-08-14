#!/usr/bin/env python3
"""Fail closed on drift in the A231201 v3 constructor-only freeze."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V22 = ROOT / "results/expansion/live-search-2026-08-14/oeis-a231201-v22-development"

subprocess.run([sys.executable, str(V22 / "verify_freeze.py")], check=True)

registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "oeis-a231201-v3-frozen-files-v1":
    raise SystemExit("bad v3 freeze registry schema")
expected = {
    ".github/workflows/oeis-a231201-v3-development.yml",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v3-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v3-development/CORRECTION.md",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v3-development/manifest.json",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v3-development/source-status-attestation.json",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v3-development/verify_freeze.py",
    "scripts/construct_oeis_a231201_v3.py",
    "scripts/test_oeis_a231201_v3_seed_cegar.py",
    "scripts/verify_oeis_a231201_v3_artifacts.py",
}
if set(registry.get("sha256", {})) != expected:
    raise SystemExit("v3 registry coverage drift")
for relative, want in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"missing v3 frozen file: {relative}")
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(f"v3 frozen file drift: {relative}: {got}")

manifest = json.loads((HERE / "manifest.json").read_text())
if manifest.get("schema") != "oeis-a231201-contaminated-development-freeze-v3-constructor-only":
    raise SystemExit("v3 manifest schema drift")
if (
    manifest.get("classification"),
    manifest.get("phase"),
    manifest.get("search_seconds"),
    manifest.get("internal_seconds"),
    manifest.get("external_seconds"),
    manifest.get("external_kill_after_seconds"),
) != ("CONTAMINATED_DEVELOPMENT", "CONSTRUCTOR_DIAGNOSTIC_ONLY", 48, 54, 60, 6):
    raise SystemExit("v3 classification/budget drift")
if manifest.get("small_basis_initial_rows_by_round") != [192, 256, 320]:
    raise SystemExit("v3 basis schedule drift")
for key in (
    "target_promotion_authorized",
    "mathematical_result_claimed",
    "periodic_cover_backend_present",
    "bounded_x_lt_n_backend_present",
    "frozen_target_domain_evaluated_by_smoke_tests",
    "resumable",
):
    if manifest.get(key) is not False:
        raise SystemExit(f"v3 trust boundary drift: {key}")
if manifest.get("full_seed_required_before_proposal") is not True:
    raise SystemExit("v3 full-seed proposal gate drift")

constructor = (ROOT / "scripts/construct_oeis_a231201_v3.py").read_text()
for token in (
    "deadline = started + 48",
    "size = 192 + 64 * a.round",
    "least_escape_cegar(",
    "escape = least_uncovered_seed(proposal, full_seed)",
    "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC",
    '"target_promotion_authorized": False',
    '"mathematical_result_claimed": False',
    'v21.v2.M["finalization_reserve_seconds"] = 6',
):
    if token not in constructor:
        raise SystemExit(f"v3 constructor guard absent: {token}")
for forbidden in (".bit_count(", "adversary_oeis_a231201_v22", "verify_oeis_a231201_v2_final"):
    if forbidden in constructor:
        raise SystemExit(f"forbidden v3 constructor dependency: {forbidden}")

artifact_verifier = (ROOT / "scripts/verify_oeis_a231201_v3_artifacts.py").read_text()
for token in (
    "v3 nonredundant 192/256/320 basis schedule drift",
    "v3 CEGAR proposal did not cover its master basis",
    "v3 least-escape feedback drift",
    "v3 proposal escaped full cheap-seed closure",
    "v3 terminal contains forbidden target-stage vocabulary",
):
    if token not in artifact_verifier:
        raise SystemExit(f"v3 artifact guard absent: {token}")

tests = (ROOT / "scripts/test_oeis_a231201_v3_seed_cegar.py").read_text()
for token in (
    "test_least_escape_is_added_before_emission",
    "test_no_proposal_is_emitted_while_any_seed_escape_remains",
    "test_frozen_runtime_schedule_and_caps",
):
    if token not in tests:
        raise SystemExit(f"v3 synthetic test guard absent: {token}")
for forbidden in ("order_table(", "periodic_value(", "verify_gate(", "run("):
    if forbidden in tests:
        raise SystemExit(f"v3 synthetic test crossed target boundary: {forbidden}")

workflow = (ROOT / ".github/workflows/oeis-a231201-v3-development.yml").read_text()
for token in (
    "python-version: '3.9.23'",
    "oeis-a231201-v3-development/verify_freeze.py",
    "scripts/test_oeis_a231201_v3_seed_cegar.py",
    "scripts/construct_oeis_a231201_v3.py",
    "scripts/verify_oeis_a231201_v3_artifacts.py",
    'round: [0, 1, 2]',
    'name: "oeis-a231201-v3-gate-',
    'name: "oeis-a231201-v3-c-r${{ matrix.round }}-',
):
    if token not in workflow:
        raise SystemExit(f"v3 workflow safety token absent: {token}")
if workflow.count("--kill-after=6s 60s") != 4:
    raise SystemExit("v3 external-cap edge coverage drift")
for forbidden in (
    "adversary-r",
    "independent-final",
    "candidate-pending",
    "assignment-0",
    "scripts/adversary_",
    "scripts/verify_oeis_a231201_v2_final.py",
):
    if forbidden in workflow:
        raise SystemExit(f"forbidden target-stage job leaked into v3 workflow: {forbidden}")

contract = (HERE / "CONTRACT.md").read_text()
for token in (
    "3,5,29,6,6,22",
    "192, 256, and 320",
    "constructor-only",
    "bounded condition `1 <= x < n`",
    "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC",
):
    if token not in contract:
        raise SystemExit(f"v3 standing absent from contract: {token}")

print("A231201 v3 constructor-only DEVELOPMENT freeze verified")
