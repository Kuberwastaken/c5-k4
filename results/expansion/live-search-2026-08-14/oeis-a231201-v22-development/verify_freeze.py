#!/usr/bin/env python3
"""Fail closed on drift in the A231201 v2.2 operational correction."""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
V21 = ROOT / "results/expansion/live-search-2026-08-14/oeis-a231201-v21-development"

subprocess.run([sys.executable, str(V21 / "verify_freeze.py")], check=True)

registry = json.loads((HERE / "freeze-files.json").read_text())
if registry.get("schema") != "oeis-a231201-v22-frozen-files-v1":
    raise SystemExit("bad v2.2 freeze registry schema")
expected = {
    ".github/workflows/oeis-a231201-v22-development.yml",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v22-development/CONTRACT.md",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v22-development/CORRECTION.md",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v22-development/manifest.json",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v22-development/source-status-attestation.json",
    "results/expansion/live-search-2026-08-14/oeis-a231201-v22-development/verify_freeze.py",
    "scripts/adversary_oeis_a231201_v22.py",
    "scripts/test_oeis_a231201_v22_adversary_deadline.py",
    "scripts/verify_oeis_a231201_v22_artifacts.py",
}
if set(registry.get("sha256", {})) != expected:
    raise SystemExit("v2.2 registry coverage drift")
for relative, want in registry["sha256"].items():
    path = ROOT / relative
    if not path.is_file():
        raise SystemExit(f"missing v2.2 frozen file: {relative}")
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != want:
        raise SystemExit(f"v2.2 frozen file drift: {relative}: {got}")

manifest = json.loads((HERE / "manifest.json").read_text())
if manifest.get("schema") != "oeis-a231201-contaminated-development-freeze-v2.2":
    raise SystemExit("v2.2 manifest schema drift")
if manifest.get("classification") != "CONTAMINATED_DEVELOPMENT":
    raise SystemExit("classification drift")
if (
    manifest.get("search_seconds"),
    manifest.get("internal_seconds"),
    manifest.get("finalization_reserve_seconds"),
    manifest.get("external_seconds"),
    manifest.get("external_kill_after_seconds"),
) != (48, 54, 6, 60, 6):
    raise SystemExit("48/54/60 budget drift")
if manifest.get("frozen_target_domain_evaluated_by_smoke_tests") is not False:
    raise SystemExit("smoke-test trust boundary drift")
if manifest.get("deduplicates_states") is not False or manifest.get("resumable") is not False:
    raise SystemExit("state/resume semantics drift")

adversary = (ROOT / "scripts/adversary_oeis_a231201_v22.py").read_text()
for token in (
    "SEARCH_SECONDS = 48",
    "FINALIZATION_RESERVE_SECONDS = 6",
    "class QueueStreamDigest:",
    "partial_queue_hash_scheme",
    "following.append(state)",
    "digest.append(state)",
    '"operational_version": "v2.2"',
):
    if token not in adversary:
        raise SystemExit(f"v2.2 adversary guard absent: {token}")
for forbidden in ("following.sort(", "queue_hash(following)", "min(states"):
    if forbidden in adversary:
        raise SystemExit(f"unbounded v2.2 post-deadline operation present: {forbidden}")

tests = (ROOT / "scripts/test_oeis_a231201_v22_adversary_deadline.py").read_text()
for token in (
    "live_calls=200_000",
    "test_large_synthetic_frontier_finalizes_and_verifies",
    "verify_deadline_evidence",
    "table=[(997, 1, 1_000_003)]",
    "value_at=lambda _q, _x: 1",
):
    if token not in tests:
        raise SystemExit(f"synthetic deadline guard absent: {token}")
for forbidden in ("order_table(", "periodic_value(", "verify_gate(", "run("):
    if forbidden in tests:
        raise SystemExit(f"synthetic test crossed frozen target boundary: {forbidden}")

workflow = (ROOT / ".github/workflows/oeis-a231201-v22-development.yml").read_text()
for token in (
    "python-version: '3.9.23'",
    "oeis-a231201-v22-development/verify_freeze.py",
    "scripts/test_oeis_a231201_v22_adversary_deadline.py",
    "scripts/construct_oeis_a231201_v21.py",
    "scripts/adversary_oeis_a231201_v22.py",
    "scripts/verify_oeis_a231201_v22_artifacts.py",
    "--kill-after=6s 60s",
    'name: "oeis-a231201-v22-gate-',
):
    if token not in workflow:
        raise SystemExit(f"v2.2 workflow safety token absent: {token}")
if workflow.count("scripts/construct_oeis_a231201_v21.py") != 3:
    raise SystemExit("v2.2 inherited constructor coverage drift")
if workflow.count("scripts/adversary_oeis_a231201_v22.py") != 3:
    raise SystemExit("v2.2 adversary round coverage drift")
if workflow.count("--kill-after=6s 60s") != 8:
    raise SystemExit("external cap edge coverage drift")
if "oeis-a231201-v21-" in workflow:
    raise SystemExit("v2.1 artifact name leaked into v2.2 workflow")

correction = (HERE / "CORRECTION.md").read_text()
for token in ("31811239530", "six", "zero candidates", "no mathematical result"):
    if token not in correction:
        raise SystemExit(f"failed-run standing absent: {token}")

print("A231201 v2.2 contaminated DEVELOPMENT freeze verified")
