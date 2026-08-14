#!/usr/bin/env python3
"""Inert PRE-P1 composition contract for one Method v1.5 CAPTURE checkpoint.

The module deliberately has no operational adapter.  Its CLI is silent and
always refuses before P1 without reading a file, opening a network client, or
writing an artifact.  ``TestCaptureDag`` exists only to exercise the frozen
ordering and fail-closed semantics with injected, side-effect-free callbacks.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PLAN_SCHEMA = "c5k4-method-v1.5-checkpoint-capture-plan-1.0"
READINESS_SCHEMA = "c5k4-method-v1.5-checkpoint-capture-readiness-1.0"
STATUS = "PRE_P1_CAPTURE_ORCHESTRATOR_NOT_OPERATIONAL"
STAGES = (
    "PUBLIC_CHAIN_VERIFY",
    "U2_PRIMARY_ACQUIRE",
    "U2_PRIMARY_WORM_COMMIT",
    "U2_PRIMARY_DELIVER",
    "PROVENANCE_SOURCE_SNAPSHOT",
    "FUTURE_REGISTRY_PRIMARY",
    "U2_REPLAY_ACQUIRE",
    "U2_REPLAY_WORM_COMMIT",
    "U2_REPLAY_DELIVER",
    "FUTURE_REGISTRY_REPLAY",
    "BROKER_CUSTODY_COMPILE",
    "RUNNER_PRIVATE_INPUT_ASSEMBLE",
    "AGGREGATE_FINALIZE_HANDOFF",
    "PUBLICATION_MANIFEST_BUILD",
)
ROLES = (
    "public_checkpoint_chain_verifier",
    "vendor_base_builder",
    "delivery_broker",
    "s3_object_lock_store",
    "broker_custody_compiler",
    "source_snapshot_builder",
    "provenance_classifier",
    "future_cohort_builder",
    "runner_private_input_assembler",
    "aggregate_certificate_builder",
    "checkpoint_runner",
    "checkpoint_publication_manifest_schema",
)
FORBIDDEN_PUBLIC_KEYS = frozenset({
    "cluster_id", "declarations", "identity", "identities", "records",
    "statement", "statement_text", "target", "target_id", "target_identity",
    "target_identities", "candidate_identities", "outcome", "outcomes",
    "ranking", "rankings", "entropy", "logs", "stdout", "stderr",
})


class CaptureError(ValueError):
    """A test-DAG contract condition failed."""


StageCallback = Callable[[dict[str, Any]], dict[str, Any]]


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def content_digest(value: Mapping[str, Any], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return hashlib.sha256(canonical_json(unsigned)).hexdigest()


def _load_schema(filename: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))


def _validate_schema(value: dict[str, Any], filename: str) -> None:
    try:
        Draft7Validator(
            _load_schema(filename), format_checker=FormatChecker()
        ).validate(value)
    except Exception as exc:
        raise CaptureError(f"artifact fails {filename}") from exc


def build_plan() -> dict[str, Any]:
    """Return the non-executable plan used by contract tests and future P1."""
    value: dict[str, Any] = {
        "schema": PLAN_SCHEMA,
        "artifact_kind": "PRIVATE_CHECKPOINT_CAPTURE_PLAN",
        "protocol_version": "1.5",
        "status": STATUS,
        "execution_permitted": False,
        "stage_order": list(STAGES),
        "role_references": [
            {"role": role, "binding": "AUTHENTICATED_P1_ROLE_REQUIRED"}
            for role in ROLES
        ],
        "invariants": {
            "p1_role_authentication_required": True,
            "fresh_acquisition_count": 2,
            "distinct_acquisitions_required": True,
            "exact_registry_replay_required": True,
            "worm_commit_before_delivery_required": True,
            "manifest_built_last": True,
            "retry_permitted": False,
            "terminal_failure_sticky": True,
            "target_bearing_public_return_permitted": False,
            "production_claim_permitted": False,
        },
    }
    value["plan_sha256"] = content_digest(value, "plan_sha256")
    return value


def readiness() -> dict[str, Any]:
    """Return an in-memory, explicitly non-operational readiness statement."""
    value: dict[str, Any] = {
        "schema": READINESS_SCHEMA,
        "artifact_kind": "CHECKPOINT_CAPTURE_READINESS",
        "protocol_version": "1.5",
        "status": STATUS,
        "executable": False,
        "network_client_constructed": False,
        "filesystem_mutation_permitted": False,
        "p1_role_closure_authenticated": False,
        "source_custody_operational": False,
        "worm_store_operational": False,
        "triplet_isolation_operational": False,
        "production_claim_permitted": False,
        "blockers": [
            "P1_ROLE_CLOSURE_NOT_FROZEN",
            "SOURCE_CUSTODY_NOT_OPERATIONAL",
            "WORM_STORE_NOT_LIVE_ACCEPTED",
            "TRIPLET_ISOLATION_NOT_OPERATIONAL",
            "CAPTURE_ORCHESTRATOR_NOT_P1_ACTIVATED",
        ],
    }
    value["readiness_sha256"] = content_digest(value, "readiness_sha256")
    return value


def validate_plan(plan: dict[str, Any]) -> None:
    _validate_schema(plan, "benchmark-checkpoint-capture-plan-v1.5.schema.json")
    if plan["plan_sha256"] != content_digest(plan, "plan_sha256"):
        raise CaptureError("plan self-digest mismatch")
    if tuple(item["role"] for item in plan["role_references"]) != ROLES:
        raise CaptureError("role references are not exact, ordered, and unique")


def validate_readiness(value: dict[str, Any]) -> None:
    _validate_schema(
        value, "benchmark-checkpoint-capture-readiness-v1.5.schema.json"
    )
    if value["readiness_sha256"] != content_digest(value, "readiness_sha256"):
        raise CaptureError("readiness self-digest mismatch")


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(
        char not in "0123456789abcdef" for char in value
    ):
        raise CaptureError(f"invalid {label}")
    return value


def _exact_result(result: Any, fields: set[str], stage: str) -> dict[str, Any]:
    if not isinstance(result, dict) or set(result) != fields:
        raise CaptureError(f"{stage} returned an invalid private result")
    return result


def _assert_target_blind(value: Any) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_PUBLIC_KEYS.intersection(key.casefold() for key in value):
            raise CaptureError("public return contains target-bearing material")
        for child in value.values():
            _assert_target_blind(child)
    elif isinstance(value, list):
        for child in value:
            _assert_target_blind(child)


class TestCaptureDag:
    """One-shot in-memory executor for injected acceptance-test callbacks only."""

    def __init__(self, plan: dict[str, Any], callbacks: Mapping[str, StageCallback]):
        self.plan = copy.deepcopy(plan)
        self.callbacks = dict(callbacks)
        self.state = "READY_FOR_TEST_ONLY"
        self.terminal_reason: str | None = None
        self.invoked: list[str] = []

    def _fail(self, message: str) -> None:
        self.state = "LOCKED_INVALID"
        self.terminal_reason = message
        raise CaptureError(message)

    def _invoke(self, stage: str, context: dict[str, Any]) -> dict[str, Any]:
        if stage in self.invoked:
            self._fail(f"stage retry forbidden: {stage}")
        callback = self.callbacks.get(stage)
        if callback is None:
            self._fail(f"missing injected callback: {stage}")
        self.invoked.append(stage)
        try:
            result = callback(copy.deepcopy(context))
        except Exception as exc:
            self.state = "LOCKED_INVALID"
            self.terminal_reason = f"stage failed: {stage}"
            raise CaptureError(self.terminal_reason) from exc
        if not isinstance(result, dict):
            self._fail(f"{stage} did not return a private record")
        return copy.deepcopy(result)

    def run(self, scheduled_for_utc: str) -> dict[str, Any]:
        """Exercise the DAG once; this is not a production execution path."""
        if self.state != "READY_FOR_TEST_ONLY":
            raise CaptureError("capture DAG is terminal and cannot be retried")
        try:
            validate_plan(self.plan)
            if set(self.callbacks) != set(STAGES):
                self._fail("injected callback set does not exactly match the plan")
            context: dict[str, Any] = {
                "scheduled_for_utc": scheduled_for_utc,
                "plan_sha256": self.plan["plan_sha256"],
                "private_stage_results": {},
            }
            for stage in STAGES:
                result = self._invoke(stage, context)
                self._validate_stage(stage, result, context)
                context["private_stage_results"][stage] = result
            public = {
                "schema": "c5k4-method-v1.5-checkpoint-capture-test-result-1.0",
                "artifact_kind": "TARGET_BLIND_TEST_DAG_RESULT",
                "protocol_version": "1.5",
                "status": "PRE_P1_TEST_DAG_COMPLETE_NOT_OPERATIONAL",
                "scheduled_for_utc": scheduled_for_utc,
                "plan_sha256": self.plan["plan_sha256"],
                "public_chain_proof_sha256": context["private_stage_results"]
                    ["PUBLIC_CHAIN_VERIFY"]["public_chain_proof_sha256"],
                "completed_stage_count": len(self.invoked),
                "manifest_sha256": context["private_stage_results"]
                    ["PUBLICATION_MANIFEST_BUILD"]["artifact_sha256"],
            }
            _assert_target_blind(public)
            self.state = "COMPLETE_TEST_ONLY"
            return public
        except CaptureError:
            if self.state != "LOCKED_INVALID":
                self.state = "LOCKED_INVALID"
                self.terminal_reason = "capture DAG validation failed"
            raise

    def _validate_stage(
        self, stage: str, result: dict[str, Any], context: dict[str, Any]
    ) -> None:
        prior = context["private_stage_results"]
        if stage == "PUBLIC_CHAIN_VERIFY":
            _exact_result(result, {"public_chain_proof_sha256"}, stage)
            _sha(result["public_chain_proof_sha256"], "public chain proof digest")
            return
        if stage in {"U2_PRIMARY_ACQUIRE", "U2_REPLAY_ACQUIRE"}:
            _exact_result(
                result,
                {"acquisition_id", "content_sha256", "fresh_repository"},
                stage,
            )
            if not isinstance(result["acquisition_id"], str) or not result["acquisition_id"]:
                self._fail(f"{stage} has no acquisition identity")
            _sha(result["content_sha256"], f"{stage} content digest")
            if result["fresh_repository"] is not True:
                self._fail(f"{stage} is not a fresh acquisition")
            if stage == "U2_REPLAY_ACQUIRE":
                primary = prior["U2_PRIMARY_ACQUIRE"]
                if result["acquisition_id"] == primary["acquisition_id"]:
                    self._fail("primary and replay acquisitions are not distinct")
            return
        if stage.endswith("_WORM_COMMIT"):
            acquire_stage = stage.replace("_WORM_COMMIT", "_ACQUIRE")
            acquire = prior[acquire_stage]
            _exact_result(
                result,
                {"acquisition_id", "content_sha256", "worm_version_id", "durable"},
                stage,
            )
            if (
                result["acquisition_id"] != acquire["acquisition_id"]
                or result["content_sha256"] != acquire["content_sha256"]
                or not isinstance(result["worm_version_id"], str)
                or not result["worm_version_id"]
                or result["durable"] is not True
            ):
                self._fail(f"{stage} is not an exact durable WORM commit")
            return
        if stage.endswith("_DELIVER"):
            prefix = stage.removesuffix("_DELIVER")
            acquire = prior[f"{prefix}_ACQUIRE"]
            worm = prior[f"{prefix}_WORM_COMMIT"]
            _exact_result(
                result,
                {"acquisition_id", "content_sha256", "worm_version_id", "delivered"},
                stage,
            )
            if (
                result["acquisition_id"] != acquire["acquisition_id"]
                or result["content_sha256"] != acquire["content_sha256"]
                or result["worm_version_id"] != worm["worm_version_id"]
                or worm["durable"] is not True
                or result["delivered"] is not True
            ):
                self._fail(f"{stage} was not delivered from the prior WORM version")
            return
        if stage in {"FUTURE_REGISTRY_PRIMARY", "FUTURE_REGISTRY_REPLAY"}:
            _exact_result(result, {"artifact_sha256"}, stage)
            _sha(result["artifact_sha256"], f"{stage} artifact digest")
            if stage == "FUTURE_REGISTRY_REPLAY" and result["artifact_sha256"] != prior[
                "FUTURE_REGISTRY_PRIMARY"
            ]["artifact_sha256"]:
                self._fail("fresh registry replay is not byte-identical")
            return
        _exact_result(result, {"artifact_sha256"}, stage)
        _sha(result["artifact_sha256"], f"{stage} artifact digest")
        if stage == "PUBLICATION_MANIFEST_BUILD":
            if self.invoked != list(STAGES):
                self._fail("publication manifest was not built last")


def main(_argv: list[str] | None = None) -> int:
    """Fail silently before P1; intentionally do not inspect argv or the host."""
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
