#!/usr/bin/env python3
"""Adversarial tests for the inert Method v1.5 CAPTURE orchestrator."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft7Validator


SCRIPT = Path(__file__).with_name("method_v15_checkpoint_capture_orchestrator.py")
SPEC = importlib.util.spec_from_file_location("method_v15_capture", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)
H1, H2, HR = "1" * 64, "2" * 64, "a" * 64


def callbacks(*, fail_at: str | None = None, same_acquisition: bool = False,
              replay_digest: str = HR) -> tuple[dict[str, object], list[str]]:
    calls: list[str] = []

    def callback(stage: str):
        def run(context: dict) -> dict:
            calls.append(stage)
            if fail_at == stage:
                raise RuntimeError("injected failure")
            if stage == "PUBLIC_CHAIN_VERIFY":
                return {"public_chain_proof_sha256": "9" * 64}
            if stage == "U2_PRIMARY_ACQUIRE":
                return {"acquisition_id": "primary", "content_sha256": H1,
                        "fresh_repository": True}
            if stage == "U2_REPLAY_ACQUIRE":
                return {"acquisition_id": "primary" if same_acquisition else "replay",
                        "content_sha256": H2, "fresh_repository": True}
            if stage == "U2_PRIMARY_WORM_COMMIT":
                return {"acquisition_id": "primary", "content_sha256": H1,
                        "worm_version_id": "worm-primary", "durable": True}
            if stage == "U2_REPLAY_WORM_COMMIT":
                return {"acquisition_id": "primary" if same_acquisition else "replay",
                        "content_sha256": H2, "worm_version_id": "worm-replay",
                        "durable": True}
            if stage == "U2_PRIMARY_DELIVER":
                return {"acquisition_id": "primary", "content_sha256": H1,
                        "worm_version_id": "worm-primary", "delivered": True}
            if stage == "U2_REPLAY_DELIVER":
                return {"acquisition_id": "primary" if same_acquisition else "replay",
                        "content_sha256": H2, "worm_version_id": "worm-replay",
                        "delivered": True}
            if stage == "FUTURE_REGISTRY_PRIMARY":
                return {"artifact_sha256": HR}
            if stage == "FUTURE_REGISTRY_REPLAY":
                return {"artifact_sha256": replay_digest}
            return {"artifact_sha256": HR}
        return run

    return {stage: callback(stage) for stage in C.STAGES}, calls


class CaptureOrchestratorTests(unittest.TestCase):
    def test_plan_and_readiness_are_strict_and_self_authenticated(self) -> None:
        plan, ready = C.build_plan(), C.readiness()
        C.validate_plan(plan)
        C.validate_readiness(ready)
        for filename in (
            "benchmark-checkpoint-capture-plan-v1.5.schema.json",
            "benchmark-checkpoint-capture-readiness-v1.5.schema.json",
        ):
            schema = json.loads((C.ROOT / "schemas" / filename).read_text())
            Draft7Validator.check_schema(schema)
        broken = copy.deepcopy(plan)
        broken["execution_permitted"] = True
        with self.assertRaises(C.CaptureError):
            C.validate_plan(broken)
        broken = copy.deepcopy(ready)
        broken["production_claim_permitted"] = True
        with self.assertRaises(C.CaptureError):
            C.validate_readiness(broken)

    def test_injected_dag_has_exact_order_and_target_blind_return(self) -> None:
        fake, calls = callbacks()
        dag = C.TestCaptureDag(C.build_plan(), fake)
        result = dag.run("2026-08-14T00:17:00Z")
        self.assertEqual(calls, list(C.STAGES))
        self.assertEqual(dag.state, "COMPLETE_TEST_ONLY")
        self.assertEqual(result["completed_stage_count"], len(C.STAGES))
        self.assertNotIn("private_stage_results", result)
        C._assert_target_blind(result)
        with self.assertRaisesRegex(C.CaptureError, "cannot be retried"):
            dag.run("2026-08-14T00:17:00Z")
        self.assertEqual(calls, list(C.STAGES))

    def test_worm_commit_is_required_before_delivery(self) -> None:
        fake, calls = callbacks()
        fake["U2_PRIMARY_WORM_COMMIT"] = lambda _context: {
            "acquisition_id": "primary", "content_sha256": H1,
            "worm_version_id": "worm-primary", "durable": False,
        }
        dag = C.TestCaptureDag(C.build_plan(), fake)
        with self.assertRaisesRegex(C.CaptureError, "durable WORM"):
            dag.run("2026-08-14T00:17:00Z")
        self.assertEqual(dag.state, "LOCKED_INVALID")
        self.assertNotIn("U2_PRIMARY_DELIVER", calls)

    def test_acquisitions_must_be_distinct_and_replay_exact(self) -> None:
        fake, _ = callbacks(same_acquisition=True)
        dag = C.TestCaptureDag(C.build_plan(), fake)
        with self.assertRaisesRegex(C.CaptureError, "not distinct"):
            dag.run("2026-08-14T00:17:00Z")
        fake, _ = callbacks(replay_digest="b" * 64)
        dag = C.TestCaptureDag(C.build_plan(), fake)
        with self.assertRaisesRegex(C.CaptureError, "not byte-identical"):
            dag.run("2026-08-14T00:17:00Z")

    def test_failure_is_sticky_and_never_retried(self) -> None:
        fake, calls = callbacks(fail_at="PROVENANCE_SOURCE_SNAPSHOT")
        dag = C.TestCaptureDag(C.build_plan(), fake)
        with self.assertRaisesRegex(C.CaptureError, "stage failed"):
            dag.run("2026-08-14T00:17:00Z")
        first_calls = list(calls)
        with self.assertRaisesRegex(C.CaptureError, "cannot be retried"):
            dag.run("2026-08-14T00:17:00Z")
        self.assertEqual(calls, first_calls)
        self.assertEqual(dag.state, "LOCKED_INVALID")

    def test_manifest_callback_is_last_and_callback_set_is_exact(self) -> None:
        fake, _ = callbacks()
        del fake["PUBLICATION_MANIFEST_BUILD"]
        dag = C.TestCaptureDag(C.build_plan(), fake)
        with self.assertRaisesRegex(C.CaptureError, "exactly match"):
            dag.run("2026-08-14T00:17:00Z")
        self.assertEqual(dag.invoked, [])
        self.assertEqual(dag.state, "LOCKED_INVALID")

    def test_target_bearing_public_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(C.CaptureError, "target-bearing"):
            C._assert_target_blind({"safe": [{"cluster_id": "secret"}]})

    def test_cli_is_silent_and_does_not_create_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v15-capture-cli-") as temporary:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", "must-not-exist"],
                cwd=temporary, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(result.stderr, b"")
            self.assertEqual(list(Path(temporary).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
