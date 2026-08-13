#!/usr/bin/env python3
"""Regression tests for Method v1.3 full-denominator scoring."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("score_benchmark_v13.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v13_scorer_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
SCORER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCORER
SPEC.loader.exec_module(SCORER)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def forecast(outcome: str) -> dict[str, str]:
    result = {name: "0.10" for name in SCORER.OUTCOMES}
    result[outcome] = "0.50"
    return result


class ScoreV13Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest_path = self.root / "score-input.json"
        self.selected = [
            {
                "cluster_id": f"cluster-{index:02d}",
                "identity_sha256": f"{index + 1:064x}",
                "stratum": "GRAPH_SCALAR_INEQUALITY",
                "shuffle_position": index + 1,
            }
            for index in range(12)
        ]
        self.evidence = {
            "schema_version": "c5k4-benchmark-selection-1.3",
            "status": "SELECTED",
            "selected_clusters": self.selected,
            "evidence_sha256": "e" * 64,
        }
        self.references = {}
        names = (
            "eligible_pool", "quota_feasibility", *SCORER.SELECTOR.ARTIFACT_KEYS,
            "verified_randomness",
        )
        for name in names:
            raw = json.dumps({"fixture": name}, sort_keys=True).encode()
            path = self.root / f"{name}.json"
            path.write_bytes(raw)
            self.references[name] = {"path": path.name, "sha256": digest(raw)}
        self.c0_contract = {
            "schema_version": "c5k4-c0-randomness-contract-1.3",
            "phase": "C0_FROZEN",
            "chronology": {
                "p0_artifact_commit": "1" * 40,
                "p0_attestation_commit": "2" * 40,
                "p0_published_at_utc": "2026-08-13T00:00:00Z",
                "s0_acquired_at_utc": "2026-08-13T01:00:00Z",
                "c0_artifact_commit": "3" * 40,
                "c0_attestation_commit": None,
                "c0_published_at_utc": "2026-08-13T02:00:00Z",
            },
            "randomness": {
                "source": "League of Entropy drand",
                "chain_hash": SCORER.SELECTOR.DRAND_CHAIN_HASH,
                "round": 1,
                "round_closes_at_utc": "2026-08-14T00:00:00Z",
                "value": None,
            },
            "published_at_utc": "2026-08-13T02:00:00Z",
            "publication_observation": {
                "source": "GITHUB_COMMIT_API_OBSERVATION",
                "observed_commit": "3" * 40,
                "observed_at_utc": "2026-08-13T02:00:00Z",
            },
        }
        c0_raw = json.dumps(self.c0_contract, sort_keys=True).encode()
        c0_path = self.root / "c0_contract.json"
        c0_path.write_bytes(c0_raw)
        self.references["c0_contract"] = {"path": c0_path.name, "sha256": digest(c0_raw)}
        receipt = {
            "schema_version": "c5k4-c0-validation-receipt-1.3",
            "c0t": {"path": "results/benchmark/v1.3-c0/c0t.json", "file_sha256": digest(c0_raw)},
            "c0_artifact_commit": "3" * 40,
            "c0_attestation_commit": "4" * 40,
            "direct_nonmerge_parent_verified": True,
            "changed_paths": ["results/benchmark/v1.3-c0/c0t.json"],
            "committed_bytes_verified": True,
            "publication_observation": self.c0_contract["publication_observation"],
            "c0_published_at_utc": "2026-08-13T02:00:00Z",
            "future_round_close_at_utc": "2026-08-14T00:00:00Z",
        }
        receipt["receipt_sha256"] = SCORER.SELECTOR.object_digest(receipt, "receipt_sha256")
        receipt_raw = json.dumps(receipt, sort_keys=True).encode()
        receipt_path = self.root / "c0_validation_receipt.json"
        receipt_path.write_bytes(receipt_raw)
        self.references["c0_validation_receipt"] = {"path": receipt_path.name, "sha256": digest(receipt_raw)}
        evidence_raw = json.dumps(self.evidence, sort_keys=True).encode()
        evidence_path = self.root / "selection.json"
        evidence_path.write_bytes(evidence_raw)
        self.references["evidence"] = {"path": evidence_path.name, "sha256": digest(evidence_raw)}

    def tearDown(self):
        self.temp.cleanup()

    def build(
        self,
        *,
        nonrunnable: set[int] = {1, 2, 3},
        timeout: int | None = None,
        protocol_invalid: int | None = None,
    ) -> tuple[dict, Path]:
        clusters = []
        for index, selected in enumerate(self.selected):
            runnable = index not in nonrunnable
            if index == 0:
                outcome = "CROSS"
            elif index == 1 and not runnable:
                outcome = "THEOREM_STRUCTURE"
            elif not runnable:
                outcome = "PRESEARCH_STOP"
            else:
                outcome = "ZERO_COMPLETE"
            if index == timeout:
                outcome = "TIMEOUT"
            if index == protocol_invalid:
                outcome = "PROTOCOL_INVALID"
            clusters.append({
                "cluster_id": selected["cluster_id"],
                "identity_sha256": selected["identity_sha256"],
                "selection_forecast": forecast(outcome),
                "intervention_forecast": forecast(outcome),
                "runnable": runnable,
                "structural_zero_reason": None if runnable else f"phase-0-stop-{index}",
                "terminal_outcome": outcome,
            })
        manifest = {
            "schema_version": SCORER.SCHEMA_VERSION,
            "benchmark_id": "heldout-v13",
            "phase": "COMPLETE",
            "selected_n": 12,
            "aggregate_denominator": "ALL_SELECTED",
            "development_prior": {
                "CROSS": "0.20", "ZERO_COMPLETE": "0.20",
                "THEOREM_STRUCTURE": "0.20", "PRESEARCH_STOP": "0.15",
                "TIMEOUT": "0.15", "PROTOCOL_INVALID": "0.10",
            },
            "scoring_rule": {},
            "selection_replay": self.references,
            "clusters": clusters,
            "ledgers": [],
        }
        scoring_rule_source = Path(__file__).parents[1] / "results" / "benchmark" / "v1.3-protocol" / "scoring-rule.json"
        scoring_rule = self.root / "scoring-rule.json"
        scoring_rule.write_bytes(scoring_rule_source.read_bytes())
        manifest["scoring_rule"] = {
            "path": scoring_rule.name,
            "sha256": digest(scoring_rule.read_bytes()),
        }

        rows = []
        previous = SCORER.ZERO_SHA256

        def append(unit: str, arm: str, process: str, event: dict, carrier: str = "0" * 64):
            nonlocal previous
            row = {
                "benchmark_id": manifest["benchmark_id"], "unit_id": unit,
                "arm": arm, "process_id": process, "contract_sha256": "a" * 64,
                "transformation_id": "frozen-fixture", "carrier_sha256": carrier,
                "previous_row_sha256": previous, "wall_seconds": "1",
                "cpu_seconds": "1", "evaluated_at_utc": "2026-09-01T00:00:00Z",
                "score_event": event,
            }
            row["row_sha256"] = SCORER.row_digest(row)
            previous = row["row_sha256"]
            rows.append(row)

        for index, cluster in enumerate(clusters):
            unit = cluster["cluster_id"]
            if cluster["runnable"]:
                for arm, residual in (
                    ("CATALOGUE", "-1"), ("GENERIC", "-2"),
                    ("WALL_NAVIGATION", "-3"),
                ):
                    status = "COMPLETE"
                    if arm == "WALL_NAVIGATION" and index == timeout:
                        status = "TIMEOUT"
                    if arm == "WALL_NAVIGATION" and index == protocol_invalid:
                        status = "PROTOCOL_INVALID"
                    append(unit, arm, f"{unit}-{arm}", {
                        "kind": "ARM_TERMINAL", "status": status,
                        "objective": {
                            "residual_orientation": "SAFE_NONNEGATIVE",
                            "signed_residual": residual,
                            "frozen_control_residual": "4",
                        } if status == "COMPLETE" else None,
                        "controlling_term": (
                            {"forecast_sign": 1, "observed_delta": "1"}
                            if arm == "WALL_NAVIGATION" and status == "COMPLETE" else None
                        ),
                    })
            theorem = index == 1 and not cluster["runnable"]
            candidate = "f" * 64 if index == 0 else None
            append(unit, "SHARED_ANALYSIS", f"{unit}-terminal", {
                "kind": "CLUSTER_TERMINAL",
                "terminal_outcome": cluster["terminal_outcome"],
                "theorem_yield": "1/2" if theorem else "0",
                "theorem_evidence": "SIGNAL" if theorem else "NONE",
                "theorem_evidence_sha256": "d" * 64 if theorem else None,
                "independent_countermodel_check": theorem,
                "crossing_candidate_sha256": candidate,
                "crossing_class": "NOVEL" if candidate else "NONE",
                "protocol_invalid_evidence_sha256": "c" * 64 if index == protocol_invalid else None,
            })
            if candidate:
                for verifier in (1, 2):
                    append(unit, "INDEPENDENT_VERIFICATION", f"{unit}-verify-{verifier}", {
                        "kind": "INDEPENDENT_VERIFICATION_TERMINAL",
                        "candidate_sha256": candidate, "result": "VERIFIED",
                    }, candidate)

        ledger = self.root / "ledger.jsonl"
        ledger.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        manifest["ledgers"] = [{"path": ledger.name, "sha256": digest(ledger.read_bytes())}]
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest, ledger

    def score(self, **kwargs):
        self.build(**kwargs)
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence) as replay:
            result = SCORER.score_manifest(self.manifest_path)
        replay.assert_called_once()
        args = replay.call_args.args
        self.assertEqual(len(args), 6)
        self.assertEqual(args[4], (self.root / "c0_validation_receipt.json").read_bytes())
        return result

    def test_full_denominator_structural_zeros_and_ties(self):
        result = self.score()
        self.assertEqual(result["selected_n"], 12)
        self.assertEqual(result["runnable_n"], 9)
        self.assertEqual(len(result["structural_zeros"]), 3)
        self.assertEqual(result["arms"]["CATALOGUE"]["mean_normalized_gain"], "3/16")
        self.assertEqual(result["arms"]["GENERIC"]["mean_normalized_gain"], "3/8")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["mean_normalized_gain"], "9/16")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["structural_zero_count"], 3)
        self.assertEqual(result["paired"]["WALL_NAVIGATION_vs_GENERIC"], {"wins": 9, "losses": 0, "ties": 3})
        self.assertEqual(result["controlling_term_sign"], {
            "correct": 9, "incorrect": 0, "non_evaluable": 3, "n": 12,
            "full_denominator_accuracy": "3/4",
        })
        self.assertEqual(result["theorem_yield"]["mean_all_selected"], "1/24")
        self.assertTrue(result["support"]["PREDICTIVE_SUPPORT"])
        self.assertTrue(result["support"]["DISCOVERY_SUPPORT"])

    def test_non_evaluable_units_count_against_sign_gate(self):
        result = self.score(nonrunnable={1, 2, 3, 4})
        self.assertEqual(result["controlling_term_sign"]["full_denominator_accuracy"], "2/3")
        self.assertFalse(result["support"]["PREDICTIVE_SUPPORT"])

    def test_all_structural_zeros_impute_no_cpu_value(self):
        result = self.score(nonrunnable=set(range(12)))
        for arm in SCORER.ARMS:
            self.assertEqual(result["arms"][arm]["structural_zero_count"], 12)
            self.assertEqual(result["arms"][arm]["mean_normalized_gain"], "0")
            self.assertIsNone(result["arms"][arm]["cpu_normalized_gain"])
        self.assertEqual(result["paired"]["WALL_NAVIGATION_vs_CATALOGUE"], {
            "wins": 0, "losses": 0, "ties": 12,
        })

    def test_timeout_and_protocol_invalid_rates_use_twelve(self):
        result = self.score(nonrunnable={1, 2, 3}, timeout=4, protocol_invalid=5)
        self.assertEqual(result["terminal_outcomes"]["timeout_rate"], "1/12")
        self.assertEqual(result["terminal_outcomes"]["protocol_invalid_rate"], "1/12")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["timeout_rate_all_selected"], "1/12")
        self.assertEqual(result["arms"]["WALL_NAVIGATION"]["protocol_invalid_rate_all_selected"], "1/12")

    def test_denominator_shrink_fails_closed(self):
        manifest, _ = self.build()
        manifest["selected_n"] = 11
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence):
            with self.assertRaisesRegex(SCORER.ScoreError, "selected_n=12"):
                SCORER.score_manifest(self.manifest_path)

    def test_selection_evidence_must_equal_replay(self):
        self.build()
        changed = dict(self.evidence)
        changed["status"] = "TAMPERED"
        with patch.object(SCORER.SELECTOR, "select", return_value=changed):
            with self.assertRaisesRegex(SCORER.ScoreError, "exact executable replay"):
                SCORER.score_manifest(self.manifest_path)

    def test_external_c0t_receipt_tamper_fails_before_selector(self):
        manifest, _ = self.build()
        path = self.root / "c0_validation_receipt.json"
        receipt = json.loads(path.read_text())
        receipt["direct_nonmerge_parent_verified"] = False
        path.write_text(json.dumps(receipt, sort_keys=True))
        manifest["selection_replay"]["c0_validation_receipt"]["sha256"] = digest(path.read_bytes())
        self.manifest_path.write_text(json.dumps(manifest))
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence) as replay:
            with self.assertRaisesRegex(SCORER.ScoreError, "receipt digest does not replay"):
                SCORER.score_manifest(self.manifest_path)
        replay.assert_not_called()

    def test_external_c0t_receipt_requires_exact_c0_bytes(self):
        manifest, _ = self.build()
        path = self.root / "c0_contract.json"
        c0 = json.loads(path.read_text())
        c0["publication_observation"]["source"] = "TAMPERED"
        path.write_text(json.dumps(c0, sort_keys=True))
        manifest["selection_replay"]["c0_contract"]["sha256"] = digest(path.read_bytes())
        self.manifest_path.write_text(json.dumps(manifest))
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence) as replay:
            with self.assertRaisesRegex(SCORER.ScoreError, "does not authenticate exact external C0T"):
                SCORER.score_manifest(self.manifest_path)
        replay.assert_not_called()

    def test_scoring_rule_is_content_addressed(self):
        manifest, _ = self.build()
        rule_path = self.root / manifest["scoring_rule"]["path"]
        rule_path.write_text("{}", encoding="utf-8")
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence):
            with self.assertRaisesRegex(SCORER.ScoreError, "digest mismatch"):
                SCORER.score_manifest(self.manifest_path)

    def test_nonrunnable_arm_row_fails(self):
        _, ledger = self.build()
        rows = [json.loads(line) for line in ledger.read_text().splitlines()]
        target = rows[0].copy()
        target["unit_id"] = "cluster-02"
        target["process_id"] = "illegal-arm"
        rows.append(target)
        previous = SCORER.ZERO_SHA256
        for row in rows:
            row["previous_row_sha256"] = previous
            row["row_sha256"] = SCORER.row_digest(row)
            previous = row["row_sha256"]
        ledger.write_text("".join(json.dumps(row) + "\n" for row in rows))
        manifest = json.loads(self.manifest_path.read_text())
        manifest["ledgers"][0]["sha256"] = digest(ledger.read_bytes())
        self.manifest_path.write_text(json.dumps(manifest))
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence):
            with self.assertRaisesRegex(SCORER.ScoreError, "nonrunnable cluster has arm"):
                SCORER.score_manifest(self.manifest_path)

    def test_terminal_precedence_fails_closed(self):
        manifest, ledger = self.build()
        manifest["clusters"][1]["terminal_outcome"] = "PRESEARCH_STOP"
        rows = [json.loads(line) for line in ledger.read_text().splitlines()]
        for row in rows:
            event = row.get("score_event", {})
            if row["unit_id"] == "cluster-01" and event.get("kind") == "CLUSTER_TERMINAL":
                event["terminal_outcome"] = "PRESEARCH_STOP"
        previous = SCORER.ZERO_SHA256
        for row in rows:
            row["previous_row_sha256"] = previous
            row["row_sha256"] = SCORER.row_digest(row)
            previous = row["row_sha256"]
        ledger.write_text("".join(json.dumps(row) + "\n" for row in rows))
        manifest["ledgers"][0]["sha256"] = digest(ledger.read_bytes())
        self.manifest_path.write_text(json.dumps(manifest))
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence):
            with self.assertRaisesRegex(SCORER.ScoreError, "precedence"):
                SCORER.score_manifest(self.manifest_path)

    def test_tampered_ledger_fails_chain(self):
        _, ledger = self.build()
        ledger.write_text(ledger.read_text().replace('"signed_residual": "-1"', '"signed_residual": "-9"', 1))
        manifest = json.loads(self.manifest_path.read_text())
        manifest["ledgers"][0]["sha256"] = digest(ledger.read_bytes())
        self.manifest_path.write_text(json.dumps(manifest))
        with patch.object(SCORER.SELECTOR, "select", return_value=self.evidence):
            with self.assertRaisesRegex(SCORER.ScoreError, "hash chain"):
                SCORER.score_manifest(self.manifest_path)


if __name__ == "__main__":
    unittest.main()
