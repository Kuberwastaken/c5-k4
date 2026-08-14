#!/usr/bin/env python3
"""Fail closed on drift in the A231201 v2.1 operational correction."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V2 = ROOT / "results/expansion/live-search-2026-08-14/oeis-a231201-v2-development"

# First prove that every inherited v2 executable and contract remains exactly
# frozen; v2.1 is not allowed to silently repair or reinterpret that history.
subprocess.run([sys.executable, str(V2 / "verify_freeze.py")], check=True)

registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "oeis-a231201-v21-frozen-files-v1":
    raise SystemExit("bad v2.1 freeze registry schema")
expected = {
    ".github/workflows/oeis-a231201-v21-development.yml",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v21-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v21-development/CORRECTION.md",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v21-development/manifest.json",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v21-development/source-status-attestation.json",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v21-development/verify_freeze.py",
    "scripts/construct_oeis_a231201_v21.py",
    "scripts/test_oeis_a231201_v21_constructor_paths.py",
}
if set(registry.get("sha256", {})) != expected:
    raise SystemExit("v2.1 registry coverage drift")
for relative, want in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"missing v2.1 frozen file: {relative}")
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(f"v2.1 frozen file drift: {relative}: {got}")

v2_registry = V2 / "freeze-files.json"
if hashlib.sha256(v2_registry.read_bytes()).hexdigest() != (
    "44de5d1720f4c2a026868e9c61e720691523213b8cabde873785fd1079ab4ba0"
):
    raise SystemExit("inherited v2 registry drift")

manifest = json.loads((HERE / "manifest.json").read_text())
if manifest.get("schema") != "oeis-a231201-contaminated-development-freeze-v2.1":
    raise SystemExit("v2.1 manifest schema drift")
if manifest.get("classification") != "CONTAMINATED_DEVELOPMENT":
    raise SystemExit("classification drift")
if (
    manifest.get("internal_seconds"),
    manifest.get("external_seconds"),
    manifest.get("external_kill_after_seconds"),
) != (54, 60, 6):
    raise SystemExit("54/60 cap drift")
if manifest.get("frozen_target_domain_evaluated_by_smoke_tests") is not False:
    raise SystemExit("smoke-test trust boundary drift")
if manifest.get("synthetic_target_format_assignment_constructed_by_smoke_tests") is not True:
    raise SystemExit("synthetic assignment disclosure drift")

constructor = (ROOT / "scripts/construct_oeis_a231201_v21.py").read_text()
if ".bit_count(" in constructor:
    raise SystemExit("Python-3.9-incompatible bit_count call present")
for token in (
    "def population_count(",
    "bin(value).count(\"1\")",
    "def coverage_score(",
    "def greedy(",
    "def compressed_cp(",
    "v2.coverage_score = coverage_score",
    "v2.greedy = greedy",
    "v2.compressed_cp = compressed_cp",
):
    if token not in constructor:
        raise SystemExit(f"v2.1 constructor correction absent: {token}")

tests = (ROOT / "scripts/test_oeis_a231201_v21_constructor_paths.py").read_text()
for token in (
    "test_python39_population_count",
    "test_deterministic_greedy_repair_path_on_synthetic_rows",
    "test_compressed_set_cover_cp_path_with_mock_solver_boundary",
    "test_small_basis_cegar_path_with_mock_growth_and_solver_boundaries",
    "mock.patch.dict(sys.modules, _fake_ortools_modules())",
):
    if token not in tests:
        raise SystemExit(f"constructor-path smoke guard absent: {token}")
for forbidden in ("subprocess", "adversary_oeis_a231201", "verify_oeis_a231201_v2_final"):
    if forbidden in tests:
        raise SystemExit(f"smoke test crossed target boundary: {forbidden}")

workflow = (ROOT / ".github/workflows/oeis-a231201-v21-development.yml").read_text()
for token in (
    "python-version: '3.9.23'",
    "scripts/test_oeis_a231201_v21_constructor_paths.py",
    "oeis-a231201-v21-development/verify_freeze.py",
    "scripts/construct_oeis_a231201_v21.py",
    "--kill-after=6s 60s",
    'name: "oeis-a231201-v21-gate-',
    'path: "${{ runner.temp }}/a231201-v21-gate/"',
):
    if token not in workflow:
        raise SystemExit(f"v2.1 workflow safety token absent: {token}")
if workflow.count("scripts/construct_oeis_a231201_v21.py") != 3:
    raise SystemExit("v2.1 constructor round coverage drift")
if "python scripts/construct_oeis_a231201_v2.py" in workflow:
    raise SystemExit("workflow still dispatches incompatible v2 constructor")
if workflow.count("--kill-after=6s 60s") != 8:  # gate + three constructors + three adversaries + final
    raise SystemExit("external cap edge coverage drift")

correction = (HERE / "CORRECTION.md").read_text()
if "31809864013" not in correction or "no mathematical result" not in correction:
    raise SystemExit("failed-run standing absent")

print("A231201 v2.1 contaminated DEVELOPMENT freeze verified")
