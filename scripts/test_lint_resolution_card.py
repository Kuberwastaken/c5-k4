#!/usr/bin/env python3
"""Regression tests for the Method v1 resolution-card linter."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("lint_resolution_card.py")
SPEC = importlib.util.spec_from_file_location("resolution_card_linter", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)


H64 = "a" * 64
COMMIT = "b" * 40


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def coordinate(value: str) -> dict:
    return {
        "source": "test/status-source",
        "revision": COMMIT,
        "scope": "exact declaration",
        "raw_value": value,
        "captured_at_utc": "2026-08-13T12:00:00Z",
        "evidence": "https://example.test/immutable/blob",
    }


def valid_card(contract_sha: str) -> dict:
    return {
        "$schema": "../../schemas/resolution-card-v1.schema.json",
        "schema_version": LINTER.SCHEMA_VERSION,
        "contract": {"path": "contract.md", "sha256": contract_sha},
        "resolution_card": {
            "logical_class": "FINITE_UNIVERSAL",
            "target_negation": {
                "literal": "There is one finite applicable object with R < 0.",
                "derivation": "Literal negation of the frozen declaration.",
                "declaration_blob_sha256": H64,
            },
            "finite_witness_suffices": True,
            "negation_certificate": {
                "kind": "FINITE_OBJECT_EXACT_CHECK",
                "description": "Object and exact witnesses.",
                "replay": "python3 verify.py",
            },
            "exact_residual": {
                "available": True,
                "expression": "R = LHS - RHS",
                "convention": "HOLDS_NONNEGATIVE",
                "crossing_condition": "R < 0",
            },
        },
        "status_coordinates": {
            "informal_status": coordinate("falsifiable"),
            "formal_solution_status": coordinate("unformalized"),
            "statement_formalized": coordinate("yes"),
            "declaration_status": coordinate("research open"),
        },
        "trial": {
            "lane": "COUNTEREXAMPLE",
            "authorization": "RUN",
            "evidence_split": "DEVELOPMENT",
            "process_wall_cap_seconds": 60,
            "solver_cap_seconds": 55,
            "carrier_identity": {
                "kind": "LABELLED_OBJECT_WITH_ROLES",
                "sha256": H64,
                "canonicalization": "canonical JSON edges and role map",
            },
            "theorem_baselines": [],
            "sign_potential": [
                {
                    "term_id": "premise",
                    "role": "PREMISE_MARGIN",
                    "exact_expression": "P",
                    "predicted_delta": "PINNED",
                    "effect_on_target_residual": "PINNED",
                    "rationale": "preserved",
                },
                {
                    "term_id": "R",
                    "role": "TARGET_RESIDUAL",
                    "exact_expression": "R",
                    "predicted_delta": "DECREASE",
                    "effect_on_target_residual": "DECREASE",
                    "rationale": "crossing direction",
                },
                {
                    "term_id": "cost",
                    "role": "CERTIFICATE_COST",
                    "exact_expression": "states",
                    "predicted_delta": "INCREASE",
                    "effect_on_target_residual": "UNKNOWN",
                    "rationale": "bounded",
                },
            ],
        },
        "ledger": {
            "path": "ledger.jsonl",
            "evidence_split": "DEVELOPMENT",
            "append_only": True,
            "prerequisites": [],
        },
    }


class ResolutionCardLintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.contract = self.root / "contract.md"
        self.contract.write_text("frozen contract\n", encoding="utf-8")
        self.card_path = self.root / "trial_resolution_card.json"

    def tearDown(self):
        self.temp.cleanup()

    def write_card(self, card: dict) -> None:
        self.card_path.write_text(json.dumps(card, indent=2), encoding="utf-8")

    def card(self) -> dict:
        return valid_card(digest(self.contract.read_bytes()))

    def codes(self, card: dict, ledger: Path | None = None) -> set[str]:
        self.write_card(card)
        return {finding.code for finding in LINTER.lint_card(self.card_path, ledger)}

    def test_valid_card_passes_without_materialized_ledger(self):
        self.assertEqual(self.codes(self.card()), set())

    def test_contract_digest_mismatch_is_integrity_error(self):
        card = self.card()
        card["contract"]["sha256"] = H64
        self.assertIn("CONTRACT_DIGEST", self.codes(card))

    def test_nonfinite_class_rejects_finite_counterexample_lane(self):
        card = self.card()
        card["resolution_card"]["logical_class"] = "EXISTENTIAL"
        self.assertTrue({"LOGICAL_CLASS", "LANE_MISMATCH"}.issubset(self.codes(card)))

    def test_stop_only_existential_may_have_no_residual_or_carrier(self):
        card = self.card()
        card["resolution_card"]["logical_class"] = "EXISTENTIAL"
        card["resolution_card"]["finite_witness_suffices"] = False
        card["resolution_card"]["exact_residual"] = {
            "available": False,
            "reason": "A negative answer needs global nonexistence.",
        }
        card["trial"]["lane"] = "STATUS_ONLY"
        card["trial"]["authorization"] = "STOP_ONLY"
        card["trial"]["carrier_identity"] = {
            "kind": "NOT_APPLICABLE",
            "reason": "No construction trial is authorized.",
        }
        card["trial"]["sign_potential"] = []
        self.assertEqual(self.codes(card), set())

    def test_process_cap_and_solver_order_are_enforced(self):
        card = self.card()
        card["trial"]["process_wall_cap_seconds"] = 61
        self.assertIn("SCHEMA", self.codes(card))
        card = self.card()
        card["trial"]["process_wall_cap_seconds"] = 50
        self.assertIn("CAP_ORDER", self.codes(card))

    def test_required_sign_roles_and_baseline_crosscheck(self):
        card = self.card()
        card["trial"]["sign_potential"].pop()
        self.assertIn("SIGN_ROLE", self.codes(card))
        card = self.card()
        card["trial"]["theorem_baselines"] = [
            {"baseline_id": "known173", "statement": "b >= gamma_c + 1"}
        ]
        self.assertIn("BASELINE_SIGN_TABLE", self.codes(card))

    def test_labelled_carrier_must_hash_roles(self):
        card = self.card()
        card["trial"]["carrier_identity"]["canonicalization"] = "sorted graph6 edges"
        self.assertIn("LABELLED_CARRIER", self.codes(card))

    def test_ledger_links_split_artifact_and_cap(self):
        card = self.card()
        self.write_card(card)
        row = {
            "kind": "candidate_evaluated",
            "contract_sha256": card["contract"]["sha256"],
            "resolution_card_sha256": LINTER.sha256_file(self.card_path),
            "evidence_split": "DEVELOPMENT",
            "wall_seconds": 12.5,
            "artifact_sha256": H64,
        }
        ledger = self.root / "ledger.jsonl"
        ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
        self.assertEqual(LINTER.lint_card(self.card_path, ledger), [])

        bad = copy.deepcopy(row)
        bad["evidence_split"] = "CALIBRATION"
        bad["wall_seconds"] = 61
        bad.pop("artifact_sha256")
        ledger.write_text(json.dumps(bad) + "\n", encoding="utf-8")
        codes = {item.code for item in LINTER.lint_card(self.card_path, ledger)}
        self.assertTrue({"LEDGER_SPLIT", "CAP_EXCEEDED", "ARTIFACT_DIGEST"}.issubset(codes))

    def test_timeout_cannot_claim_crossing(self):
        card = self.card()
        self.write_card(card)
        row = {
            "kind": "solve_timeout",
            "contract_sha256": card["contract"]["sha256"],
            "resolution_card_sha256": LINTER.sha256_file(self.card_path),
            "evidence_split": "DEVELOPMENT",
            "wall_seconds": 60,
            "crossing": True,
        }
        ledger = self.root / "ledger.jsonl"
        ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
        self.assertIn("TIMEOUT_CLAIM", {
            item.code for item in LINTER.lint_card(self.card_path, ledger)
        })

    def test_legacy_document_is_warning_only(self):
        legacy = self.root / "legacy.json"
        legacy.write_text('{"schema_version":"method-v0.9"}', encoding="utf-8")
        findings = LINTER.lint_card(legacy)
        self.assertEqual([(f.severity, f.code) for f in findings],
                         [("warning", "LEGACY_SKIPPED")])


if __name__ == "__main__":
    unittest.main()
