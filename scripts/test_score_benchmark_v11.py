#!/usr/bin/env python3
"""Regression tests for ledger-derived Method v1.1 aggregate scoring."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SCORER = load_module("benchmark_v11_scorer_tested", HERE / "score_benchmark_v11.py")
FIXTURES = load_module("benchmark_v11_lint_fixtures", HERE / "test_lint_benchmark_v11.py")
SELECTOR = load_module("benchmark_v11_selector_for_score", HERE / "select_benchmark_v11.py")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def favorable(outcome: str) -> dict[str, str]:
    vector = {name: "0.10" for name in SCORER.OUTCOMES}
    vector[outcome] = "0.50"
    return vector


class BenchmarkScoreTests(unittest.TestCase):
    def setUp(self):
        self.fixture = FIXTURES.BenchmarkLintTests(methodName="test_valid_c1_manifest_passes")
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def build_complete(
        self,
        *,
        wall_end: str = "3",
        wall_observed: str = "1",
        omit_second_verification: bool = False,
        invalid_theorem_signal: bool = False,
    ) -> tuple[dict, Path, Path]:
        manifest = self.fixture.manifest()
        randomness = "1" * 64
        manifest["randomness"]["value"] = randomness
        manifest["randomness"]["value_sha256"] = digest(randomness.encode("ascii"))
        pool = {
            "schema_version": SELECTOR.POOL_SCHEMA_VERSION,
            "upstream": {
                "commit": manifest["upstream"]["commit"],
                "tree": manifest["upstream"]["tree"],
            },
            "contamination": {
                "applied": True,
                "inventory_sha256": manifest["contamination"]["inventory"]["sha256"],
                "identity_ambiguity_means_exclusion": True,
            },
            "clusters": [
                {
                    "cluster_id": cluster["cluster_id"],
                    "identity_sha256": cluster["identity_sha256"],
                    "stratum": cluster["stratum"],
                    "eligible": True,
                }
                for cluster in manifest["clusters"]
            ],
        }
        pool_path = self.fixture.root / "score-pool.json"
        pool_path.write_text(json.dumps(pool, indent=2), encoding="utf-8")
        manifest["freeze_artifacts"]["pool_manifest"] = {
            "path": pool_path.name,
            "sha256": digest(pool_path.read_bytes()),
        }
        evidence = SELECTOR.select(pool_path.read_bytes(), randomness)
        evidence_path = self.fixture.root / "score-selection.json"
        evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        manifest["selection"]["evidence"] = {
            "path": evidence_path.name,
            "sha256": digest(evidence_path.read_bytes()),
        }
        by_id = {cluster["cluster_id"]: cluster for cluster in manifest["clusters"]}
        manifest["clusters"] = [by_id[row["cluster_id"]] for row in evidence["selected_clusters"]]
        manifest["phase"] = "COMPLETE"
        manifest["chronology"]["evaluation_started_at_utc"] = "2026-08-14T06:00:00Z"
        manifest["chronology"]["completed_at_utc"] = "2026-08-14T07:00:00Z"

        outcomes = ["CROSS", "THEOREM_STRUCTURE", "TIMEOUT", "PROTOCOL_INVALID"] + ["ZERO_COMPLETE"] * 8
        for index, (cluster, outcome) in enumerate(zip(manifest["clusters"], outcomes)):
            self.fixture.attach_arms(manifest, index)
            cluster["selection_forecast"]["probabilities"] = favorable(outcome)
            cluster["intervention_forecast"]["probabilities"] = favorable(outcome)
            cluster["evaluation_started_at_utc"] = "2026-08-14T06:00:00Z"
            cluster["terminal_outcome"] = outcome
            for arm in SCORER.ARMS:
                cluster["arms"][arm]["status"] = "TERMINATED"

        rows: list[dict] = []
        previous = SCORER.LINTER.ZERO_SHA256

        def append_row(unit: str, arm: str, process: str, event: dict, carrier: str = "0" * 64) -> None:
            nonlocal previous
            cluster = next(item for item in manifest["clusters"] if item["cluster_id"] == unit)
            if arm in SCORER.ARMS:
                contract = cluster["arms"][arm]["contract"]["sha256"]
                transformation = cluster["arms"][arm]["transformation_id"]
            else:
                contract = "a" * 64
                transformation = "terminal-evidence"
            row = {
                "benchmark_id": manifest["benchmark_id"],
                "unit_id": unit,
                "arm": arm,
                "process_id": process,
                "contract_sha256": contract,
                "transformation_id": transformation,
                "carrier_sha256": carrier,
                "previous_row_sha256": previous,
                "wall_seconds": 1,
                "cpu_seconds": 1,
                "evaluated_at_utc": "2026-08-14T06:00:00Z",
                "score_event": event,
            }
            row["row_sha256"] = SCORER.LINTER.canonical_row_sha256(row)
            previous = row["row_sha256"]
            rows.append(row)

        for index, cluster in enumerate(manifest["clusters"]):
            unit = cluster["cluster_id"]
            for arm, end in (("CATALOGUE", "1"), ("GENERIC", "2"), ("WALL_NAVIGATION", wall_end)):
                exceptional_status = (
                    cluster["terminal_outcome"]
                    if arm == "WALL_NAVIGATION" and cluster["terminal_outcome"] in ("TIMEOUT", "PROTOCOL_INVALID")
                    else "COMPLETE"
                )
                append_row(unit, arm, f"{unit}-{arm}", {
                    "kind": "ARM_TERMINAL",
                    "status": exceptional_status,
                    "objective": {
                        "residual_orientation": "SAFE_NONNEGATIVE",
                        "signed_residual": f"-{end}",
                        "frozen_control_residual": "4",
                    } if exceptional_status == "COMPLETE" else None,
                    "controlling_term": (
                        {"forecast_sign": 1, "observed_delta": wall_observed}
                        if arm == "WALL_NAVIGATION" and exceptional_status == "COMPLETE" else None
                    ),
                })

            outcome = cluster["terminal_outcome"]
            theorem = outcome == "THEOREM_STRUCTURE"
            candidate = "f" * 64 if outcome == "CROSS" else None
            append_row(unit, "SHARED_ANALYSIS", f"{unit}-terminal", {
                "kind": "CLUSTER_TERMINAL",
                "terminal_outcome": outcome,
                "theorem_yield": "1/2" if theorem else "0",
                "theorem_evidence": "SIGNAL" if theorem else "NONE",
                "theorem_evidence_sha256": "e" * 64 if theorem else None,
                "independent_countermodel_check": theorem and not invalid_theorem_signal,
                "crossing_candidate_sha256": candidate,
                "crossing_class": "NOVEL" if candidate else "NONE",
            })
            if candidate:
                append_row(unit, "INDEPENDENT_VERIFICATION", f"{unit}-verify-1", {
                    "kind": "INDEPENDENT_VERIFICATION_TERMINAL",
                    "candidate_sha256": candidate,
                    "result": "VERIFIED",
                }, candidate)
                if not omit_second_verification:
                    append_row(unit, "INDEPENDENT_VERIFICATION", f"{unit}-verify-2", {
                        "kind": "INDEPENDENT_VERIFICATION_TERMINAL",
                        "candidate_sha256": candidate,
                        "result": "VERIFIED",
                    }, candidate)

        ledger = self.fixture.root / "scoring-ledger.jsonl"
        ledger.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        manifest["ledgers"] = [{
            "path": ledger.name,
            "sha256": digest(ledger.read_bytes()),
            "append_only": True,
            "hash_chain": "SHA256_CANONICAL_JSON_WITHOUT_ROW_SHA256",
        }]
        manifest_path = self.fixture.manifest_path
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest, manifest_path, ledger

    def test_exact_metrics_and_support_gates(self):
        _, manifest_path, _ = self.build_complete()
        result = SCORER.score_manifest(manifest_path)
        self.assertEqual(result["forecast_scores"]["selection"]["method_brier"], "3/10")
        self.assertEqual(result["forecast_scores"]["selection"]["prior_brier"], "4/5")
        self.assertEqual(result["forecast_scores"]["selection"]["brier_skill"], "5/8")
        self.assertEqual(result["forecast_scores"]["intervention"]["brier_skill"], "5/8")
        self.assertEqual(result["arms"]["CATALOGUE"]["mean_normalized_gain"], "1/4")
        self.assertEqual(result["arms"]["GENERIC"]["mean_normalized_gain"], "1/2")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["mean_normalized_gain"], "5/8")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["cpu_normalized_gain"], "5/8")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["timeout_rate"], "1/12")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["protocol_invalid_rate"], "1/12")
        self.assertEqual(result["paired"]["WALL_NAVIGATION_vs_CATALOGUE"], {"wins": 10, "losses": 2, "ties": 0})
        self.assertEqual(result["controlling_term_sign"]["accuracy"], "1")
        self.assertEqual(result["theorem_yield"]["total"], "1/2")
        self.assertEqual(result["theorem_yield"]["mean"], "1/24")
        self.assertEqual(result["crossings"]["by_class"]["NOVEL"], 1)
        self.assertTrue(result["support"]["PREDICTIVE_SUPPORT"])
        self.assertTrue(result["support"]["DISCOVERY_SUPPORT"])

    def test_safe_nonpositive_residual_orientation(self):
        gain = SCORER._objective_gain({
            "status": "COMPLETE",
            "objective": {
                "residual_orientation": "SAFE_NONPOSITIVE",
                "signed_residual": "3/2",
                "frozen_control_residual": "-2",
            },
        }, "test")
        self.assertEqual(gain, SCORER.Fraction(3, 4))

    def test_support_fails_when_wall_does_not_beat_generic(self):
        _, manifest_path, _ = self.build_complete(wall_end="2")
        result = SCORER.score_manifest(manifest_path)
        self.assertFalse(result["support"]["PREDICTIVE_SUPPORT"])
        self.assertFalse(result["support"]["DISCOVERY_SUPPORT"])
        self.assertFalse(result["support"]["gates"]["wall_mean_gain_beats_generic"])

    def test_support_fails_conservative_sign_gate(self):
        _, manifest_path, _ = self.build_complete(wall_observed="-1")
        result = SCORER.score_manifest(manifest_path)
        self.assertEqual(result["controlling_term_sign"]["accuracy"], "0")
        self.assertFalse(result["support"]["PREDICTIVE_SUPPORT"])

    def test_missing_independent_verifier_fails_closed(self):
        _, manifest_path, _ = self.build_complete(omit_second_verification=True)
        with self.assertRaisesRegex(SCORER.ScoreError, "exactly two independent VERIFIED"):
            SCORER.score_manifest(manifest_path)

    def test_unjustified_theorem_signal_fails_closed(self):
        _, manifest_path, _ = self.build_complete(invalid_theorem_signal=True)
        with self.assertRaisesRegex(SCORER.ScoreError, "independent countermodel"):
            SCORER.score_manifest(manifest_path)

    def test_tampered_ledger_fails_at_linter(self):
        _, manifest_path, ledger = self.build_complete()
        text = ledger.read_text(encoding="utf-8")
        ledger.write_text(
            text.replace('"signed_residual": "-1"', '"signed_residual": "-9"', 1),
            encoding="utf-8",
        )
        with self.assertRaises(SCORER.ScoreError) as caught:
            SCORER.score_manifest(manifest_path)
        self.assertEqual(caught.exception.code, "LINTER_FAILED")

    def test_json_float_metric_is_rejected(self):
        _, manifest_path, ledger = self.build_complete()
        rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        previous = SCORER.LINTER.ZERO_SHA256
        for row in rows:
            if row["score_event"]["kind"] == "ARM_TERMINAL":
                row["score_event"]["objective"]["signed_residual"] = 0.25
                row["previous_row_sha256"] = previous
                row["row_sha256"] = SCORER.LINTER.canonical_row_sha256(row)
                previous = row["row_sha256"]
                break
            previous = row["row_sha256"]
        # Re-chain all following rows so only the score-format rule fails.
        for row in rows[1:]:
            row["previous_row_sha256"] = rows[rows.index(row) - 1]["row_sha256"]
            row["row_sha256"] = SCORER.LINTER.canonical_row_sha256(row)
        ledger.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["ledgers"][0]["sha256"] = digest(ledger.read_bytes())
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        with self.assertRaises(SCORER.ScoreError) as caught:
            SCORER.score_manifest(manifest_path)
        self.assertEqual(caught.exception.code, "RATIONAL")


if __name__ == "__main__":
    unittest.main()
