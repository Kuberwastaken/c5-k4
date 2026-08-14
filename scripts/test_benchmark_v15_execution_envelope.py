#!/usr/bin/env python3
"""Adversarial contract tests for the Method v1.5 arm envelope."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_benchmark_v15_execution_envelope.py"
SPEC = importlib.util.spec_from_file_location("validate_benchmark_v15_execution_envelope", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

MATRIX_PATH = ROOT / "results/benchmark/v1.5-protocol/arm-capability-matrix.json"
ZERO = "0" * 64
ONE = "1" * 64
COMMIT_A = "a" * 40
COMMIT_B = "b" * 40


def seal(value: dict, key: str) -> dict:
    value[key] = validator.content_digest(value, key)
    return value


def fixed_rules() -> dict:
    return {
        "arms": list(validator.ARMS),
        "all_three_pending_barrier": True,
        "validate_complete_triplet_before_claim": True,
        "equal_discovery_budget": {
            "process_trees_per_arm": 8,
            "wall_seconds_per_tree": 60,
            "cpu_seconds_per_arm_max": 480,
        },
        "baseline_contract_precommit_before_wall_analysis": True,
        "no_adaptation": True,
        "cross_arm_result_inputs": [],
        "continue_after_crossing": True,
        "result_reveal": "ONLY_AFTER_ALL_THREE_ARMS_TERMINATE",
        "intermediate_result_delivery_permitted": False,
        "one_shot_claim_required": True,
        "claim_update_rule": "APPEND_ONLY_ATOMIC_NORMAL_FAST_FORWARD",
        "network_policy": "DENY",
        "filesystem_isolation": "SEPARATE_READ_ONLY_INPUT_AND_PRIVATE_WRITABLE_MOUNT_NAMESPACES",
        "shared_writable_root_permitted": False,
        "target_process_launching_implemented": False,
    }


def scaffold(matrix: dict) -> dict:
    return seal({
        "schema": "c5k4-method-v1.5-execution-envelope-1.0",
        "artifact_kind": "THREE_ARM_EXECUTION_ENVELOPE",
        "protocol_version": "1.5",
        "status": "PRE_P1_SCAFFOLD_NOT_EXECUTABLE",
        "target_specific_fields_present": False,
        "capability_matrix": {
            "path": "results/benchmark/v1.5-protocol/arm-capability-matrix.json",
            "sha256": matrix["matrix_sha256"],
        },
        "fixed_rules": fixed_rules(),
        "target_execution": None,
        "envelope_sha256": ZERO,
    }, "envelope_sha256")


def post_c1_envelope(matrix: dict) -> dict:
    output_paths = {
        "CATALOGUE_RESULT": "/sealed-results/catalogue",
        "GENERIC_RESULT": "/sealed-results/generic",
        "WALL_NAVIGATION_RESULT": "/sealed-results/wall",
    }
    roots = []
    for index, role in enumerate(matrix["root_roles"]):
        result = role in output_paths
        roots.append({
            "root_role": role,
            "path": output_paths[role] if result else f"inputs/{index:02d}-{role.lower()}.json",
            "sha256": None if result else f"{index + 1:064x}",
            "access": "PRIVATE_RESULT_OUTPUT" if result else "READ_ONLY_INPUT",
        })
    by_role = {root["root_role"]: root for root in roots}

    def contract(role: str) -> dict:
        return {"path": by_role[role]["path"], "sha256": by_role[role]["sha256"]}

    arms = {}
    for arm, contract_role, writable in (
        ("CATALOGUE", "CATALOGUE_CONTRACT", output_paths["CATALOGUE_RESULT"]),
        ("GENERIC", "GENERIC_CONTRACT", output_paths["GENERIC_RESULT"]),
        ("WALL_NAVIGATION", "WALL_CONTRACT", output_paths["WALL_NAVIGATION_RESULT"]),
    ):
        arms[arm] = {
            "status": "PENDING",
            "contract": contract(contract_role),
            "seed": f"seed-{arm.lower()}",
            "parameter_grid": {"frozen": [0, 1]},
            "transformation_id": f"frozen-{arm.lower()}",
            "process_tree_count": 8,
            "process_tree_wall_cap_seconds": 60,
            "cpu_budget_seconds": 480,
            "no_adaptation": True,
            "continue_after_crossing": True,
            "cross_arm_result_inputs": [],
            "allowed_digest_root_roles": list(matrix["capabilities"][arm]["allowed_root_roles"]),
            "forbidden_digest_root_roles": list(matrix["capabilities"][arm]["forbidden_root_roles"]),
            "writable_root": writable,
        }
    value = {
        "schema": "c5k4-method-v1.5-execution-envelope-1.0",
        "artifact_kind": "THREE_ARM_EXECUTION_ENVELOPE",
        "protocol_version": "1.5",
        "status": "POST_C1_RUN_FREEZE_DRAFT_NOT_EXECUTABLE",
        "target_specific_fields_present": True,
        "capability_matrix": {
            "path": "results/benchmark/v1.5-protocol/arm-capability-matrix.json",
            "sha256": matrix["matrix_sha256"],
        },
        "fixed_rules": fixed_rules(),
        "target_execution": {
            "benchmark_id": "method-v1.5-fixture",
            "cluster_id": "future-cluster-fixture",
            "campaign_checkout": "/campaign/c5-k4",
            "c1_attestation_commit": COMMIT_A,
            "run_freeze_commit": COMMIT_B,
            "digest_roots": roots,
            "baseline_contract_precommit": {
                "commit": COMMIT_A,
                "recorded_at_utc": "2027-01-01T00:00:00Z",
                "CATALOGUE": copy.deepcopy(arms["CATALOGUE"]["contract"]),
                "GENERIC": copy.deepcopy(arms["GENERIC"]["contract"]),
            },
            "wall_analysis_first_delivered_at_utc": "2027-01-01T00:00:01Z",
            "arms": arms,
            "one_shot_claim": {
                "state": "UNCLAIMED",
                "claim_ref": "refs/heads/method-v1.5-execution-claims",
                "claim_nonce_sha256": ONE,
                "prior_claims_permitted": False,
                "update_rule": "APPEND_ONLY_ATOMIC_NORMAL_FAST_FORWARD",
            },
            "reveal": {
                "condition": "ALL_THREE_ARMS_TERMINATED",
                "intermediate_logs_permitted": False,
                "intermediate_artifacts_permitted": False,
                "combined_record_only": True,
            },
        },
        "envelope_sha256": ZERO,
    }
    return seal(value, "envelope_sha256")


class ExecutionEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))

    def validate(self, value: dict) -> None:
        validator.validate_envelope(value, self.matrix)

    def mutate(self, value: dict, change) -> dict:
        altered = copy.deepcopy(value)
        change(altered)
        return seal(altered, "envelope_sha256")

    def test_target_free_matrix_and_scaffold_validate(self) -> None:
        validator.validate_matrix(self.matrix)
        self.validate(scaffold(self.matrix))

    def test_complete_post_c1_triplet_contract_validates_without_launching(self) -> None:
        value = post_c1_envelope(self.matrix)
        self.validate(value)
        self.assertFalse(value["fixed_rules"]["target_process_launching_implemented"])

    def test_pre_p1_scaffold_rejects_target_execution(self) -> None:
        value = scaffold(self.matrix)
        value["target_execution"] = post_c1_envelope(self.matrix)["target_execution"]
        value["envelope_sha256"] = validator.content_digest(value, "envelope_sha256")
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure|target-specific"):
            self.validate(value)

    def test_unequal_arm_budget_is_rejected(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["arms"]["GENERIC"].__setitem__("cpu_budget_seconds", 479))
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure"):
            self.validate(value)

    def test_nonpending_arm_breaks_common_barrier(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["arms"]["CATALOGUE"].__setitem__("status", "RUNNING"))
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure|PENDING barrier"):
            self.validate(value)

    def test_baseline_precommit_must_precede_wall_analysis(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["baseline_contract_precommit"].__setitem__("recorded_at_utc", "2027-01-01T00:00:01Z"))
        with self.assertRaisesRegex(validator.EnvelopeError, "does not precede"):
            self.validate(value)

    def test_baseline_contract_cannot_change_after_precommit(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["baseline_contract_precommit"]["CATALOGUE"].__setitem__("sha256", ZERO))
        with self.assertRaisesRegex(validator.EnvelopeError, "changed after"):
            self.validate(value)

    def test_catalogue_cannot_receive_wall_analysis(self) -> None:
        def change(row: dict) -> None:
            arm = row["target_execution"]["arms"]["CATALOGUE"]
            arm["allowed_digest_root_roles"].append("WALL_ANALYSIS")
            arm["forbidden_digest_root_roles"].remove("WALL_ANALYSIS")
        value = self.mutate(post_c1_envelope(self.matrix), change)
        with self.assertRaisesRegex(validator.EnvelopeError, "allowed digest-root closure"):
            self.validate(value)

    def test_result_root_cannot_become_an_input(self) -> None:
        def change(row: dict) -> None:
            arm = row["target_execution"]["arms"]["GENERIC"]
            arm["allowed_digest_root_roles"].append("CATALOGUE_RESULT")
            arm["forbidden_digest_root_roles"].remove("CATALOGUE_RESULT")
        value = self.mutate(post_c1_envelope(self.matrix), change)
        with self.assertRaisesRegex(validator.EnvelopeError, "allowed digest-root closure|consumes"):
            self.validate(value)

    def test_preexecution_result_root_cannot_claim_a_digest(self) -> None:
        def change(row: dict) -> None:
            for root in row["target_execution"]["digest_roots"]:
                if root["root_role"] == "CATALOGUE_RESULT":
                    root["sha256"] = ZERO
        value = self.mutate(post_c1_envelope(self.matrix), change)
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure|already has a digest"):
            self.validate(value)

    def test_readonly_input_root_requires_a_digest(self) -> None:
        def change(row: dict) -> None:
            for root in row["target_execution"]["digest_roots"]:
                if root["root_role"] == "WALL_ANALYSIS":
                    root["sha256"] = None
        value = self.mutate(post_c1_envelope(self.matrix), change)
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure"):
            self.validate(value)

    def test_cross_arm_result_argument_is_rejected(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["arms"]["WALL_NAVIGATION"]["cross_arm_result_inputs"].append("catalogue/result.json"))
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure"):
            self.validate(value)

    def test_adaptation_is_rejected(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["arms"]["WALL_NAVIGATION"].__setitem__("no_adaptation", False))
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure"):
            self.validate(value)

    def test_writable_roots_must_be_pairwise_disjoint(self) -> None:
        def change(row: dict) -> None:
            row["target_execution"]["arms"]["GENERIC"]["writable_root"] = "/sealed-results/catalogue/nested"
            for root in row["target_execution"]["digest_roots"]:
                if root["root_role"] == "GENERIC_RESULT":
                    root["path"] = "/sealed-results/catalogue/nested"
        value = self.mutate(post_c1_envelope(self.matrix), change)
        with self.assertRaisesRegex(validator.EnvelopeError, "writable root.*overlap|writable roots overlap"):
            self.validate(value)

    def test_writable_root_cannot_overlap_campaign_checkout(self) -> None:
        def change(row: dict) -> None:
            row["target_execution"]["arms"]["CATALOGUE"]["writable_root"] = "/campaign/c5-k4/output"
            for root in row["target_execution"]["digest_roots"]:
                if root["root_role"] == "CATALOGUE_RESULT":
                    root["path"] = "/campaign/c5-k4/output"
        value = self.mutate(post_c1_envelope(self.matrix), change)
        with self.assertRaisesRegex(validator.EnvelopeError, "campaign checkout"):
            self.validate(value)

    def test_intermediate_reveal_is_rejected(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["reveal"].__setitem__("intermediate_logs_permitted", True))
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure|embargoed"):
            self.validate(value)

    def test_reusable_claim_is_rejected(self) -> None:
        value = self.mutate(post_c1_envelope(self.matrix), lambda row: row["target_execution"]["one_shot_claim"].__setitem__("prior_claims_permitted", True))
        with self.assertRaisesRegex(validator.EnvelopeError, "schema failure|one-shot"):
            self.validate(value)

    def test_matrix_digest_tampering_is_rejected(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["matrix_sha256"] = ZERO
        with self.assertRaisesRegex(validator.EnvelopeError, "self-digest"):
            validator.validate_matrix(matrix)

    def test_envelope_digest_tampering_is_rejected(self) -> None:
        value = post_c1_envelope(self.matrix)
        value["envelope_sha256"] = ZERO
        with self.assertRaisesRegex(validator.EnvelopeError, "self-digest"):
            self.validate(value)


if __name__ == "__main__":
    unittest.main()
