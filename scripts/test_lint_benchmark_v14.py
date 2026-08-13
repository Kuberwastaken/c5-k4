#!/usr/bin/env python3
"""Regression fixtures for the Method v1.4 fail-closed linter."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("lint_benchmark_v14.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v14_linter", SCRIPT)
assert SPEC and SPEC.loader
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)

OID = "a" * 40
TREE = "b" * 40
H = "c" * 64
STRATA = [
    "GRAPH_SCALAR_INEQUALITY", "GRAPH_SCALAR_INEQUALITY", "GRAPH_SCALAR_INEQUALITY",
    "GRAPH_STRUCTURAL_PROPERTY", "GRAPH_STRUCTURAL_PROPERTY", "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL", "FINITE_ALGRA_EQUATIONAL",  # repaired in setUp
    "AUTOMATA_GAME_PROCESS", "AUTOMATA_GAME_PROCESS",
    "FINITE_COMBINATORIAL", "FINITE_COMBINATORIAL",
]


class BenchmarkV14LintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest_path = self.root / "benchmark.json"
        self.refs: dict[str, dict] = {}
        for name in (
            "p0a", "p0t", "rule", "open_inventory", "classifier", "provenance_policy",
            "registry_input_schema", "registry_output_schema", "provenance_inventory",
            "contamination_inventory", "source_snapshots", "prior", "library", "scoring",
            "stopping", "c0", "randomness", "selection", "terminal", "ledger",
            "score_input", "score_result",
            "c0_receipt",
        ):
            self.write_artifact(name, {"schema_version": f"fixture-{name}"})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_artifact(self, name: str, value: object) -> dict:
        path = self.root / f"{name}.json"
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        ref = {"path": path.name, "sha256": LINTER.sha256(path.read_bytes())}
        self.refs[name] = ref
        return copy.deepcopy(ref)

    @staticmethod
    def pair(name: str) -> dict:
        base = (name[0] * 40) if name[0] in "abcdef" else OID
        attestation = ("f" if base[0] != "f" else "e") * 40
        return {
            "artifact_commit": base, "attestation_commit": attestation,
            "artifact_self_reference": None, "attested_artifact_commit": base,
            "attestation_parent": base, "artifact_tree_sha256": H,
            "attested_artifact_tree_sha256": H,
            "changed_fields": ["phase"],
        }

    def pool_row(self, index: int, stratum: str) -> dict:
        return {
            "cluster_id": f"cluster-{index:02d}", "identity_sha256": f"{index + 1:064x}",
            "stratum": stratum, "machine_classification_unambiguous": True,
            "identity_grouping_complete": True, "semantic_exposure": False,
            "unknown_exposure": False, "registry_contact_evidence_count": 1,
            "eligible": True,
        }

    def manifest(self, *, feasible: bool, complete: bool = False) -> dict:
        strata = copy.deepcopy(STRATA)
        strata[7] = "FINITE_ALGEBRA_EQUATIONAL"
        if not feasible:
            strata.pop()
        freeze = {
            "open_inventory": copy.deepcopy(self.refs["open_inventory"]),
            "classifier": copy.deepcopy(self.refs["classifier"]),
            "provenance_policy": copy.deepcopy(self.refs["provenance_policy"]),
            "registry_input_schema": copy.deepcopy(self.refs["registry_input_schema"]),
            "registry_output_schema": copy.deepcopy(self.refs["registry_output_schema"]),
            "provenance_inventory": copy.deepcopy(self.refs["provenance_inventory"]),
            "contamination_inventory": copy.deepcopy(self.refs["contamination_inventory"]),
            "source_snapshots": copy.deepcopy(self.refs["source_snapshots"]),
            "eligible_pool": None, "feasibility_certificate": None,
            "c0_randomness_contract": copy.deepcopy(self.refs["c0"]) if feasible else None,
            "c0_validation_receipt": copy.deepcopy(self.refs["c0_receipt"]) if feasible else None,
            "development_prior": copy.deepcopy(self.refs["prior"]),
            "transformation_library": copy.deepcopy(self.refs["library"]),
            "scoring_rule": copy.deepcopy(self.refs["scoring"]),
            "stopping_rule": copy.deepcopy(self.refs["stopping"]),
        }
        s0 = {
            "schema_version": "c5k4-source-snapshot-S0-1.4", "snapshot_id": "S0",
            "acquired_at_utc": "2026-08-13T01:00:00Z", "candidate_semantics_inspected": False,
            "complete": True, "corpus_sha256": H, "snapshot_sha256": H,
        }
        s0["snapshot_sha256"] = LINTER.canonical_object_sha256(s0, "snapshot_sha256")
        freeze["source_snapshots"] = self.write_artifact("source_snapshots", s0)
        digest_keys = {f"{key}_sha256": freeze[key]["sha256"] for key in LINTER.ARTIFACT_KEYS}
        pool = {
            "schema_version": "c5k4-eligible-cluster-pool-1.4",
            "artifact_status": "CONTAMINATION_APPLIED",
            "upstream": {"repository": "google-deepmind/formal-conjectures", "commit": OID, "tree": TREE},
            "digests": digest_keys,
            "clusters": [self.pool_row(i, s) for i, s in enumerate(strata)],
        }
        freeze["eligible_pool"] = self.write_artifact("pool", pool)
        counts = {s: strata.count(s) for s in LINTER.STRATA}
        cert = {
            "schema_version": "c5k4-quota-feasibility-1.4", "phase": "PRE_C0_FEASIBILITY",
            "status": "PASS" if feasible else "FAIL",
            "upstream": pool["upstream"],
            "chronology": {"p0_artifact_commit": OID, "p0_attestation_commit": "d" * 40, "p0_published_at_utc": "2026-08-13T00:00:00Z", "s0_acquired_at_utc": "2026-08-13T01:00:00Z", "feasibility_checked_at_utc": "2026-08-13T02:00:00Z"},
            "entropy_used": False, "selected_clusters": [],
            "digests": {
                "eligible_pool_file_sha256": freeze["eligible_pool"]["sha256"],
                "eligible_pool_canonical_sha256": LINTER.canonical_object_sha256(pool),
                **digest_keys,
            },
            "quotas": copy.deepcopy(LINTER.QUOTAS),
            "strata": [{"stratum": s, "quota": LINTER.QUOTAS[s], "eligible_count": counts[s], "deficit": max(0, LINTER.QUOTAS[s] - counts[s]), "surplus": max(0, counts[s] - LINTER.QUOTAS[s])} for s in LINTER.STRATA],
            "certificate_sha256": H,
        }
        cert["certificate_sha256"] = LINTER.canonical_object_sha256(cert, "certificate_sha256")
        freeze["feasibility_certificate"] = self.write_artifact("feasibility", cert)
        phase = "COMPLETE" if complete else ("C1_SELECTED" if feasible else "NO_ELIGIBLE_BENCHMARK_PRE_C0")
        clusters = []
        if feasible:
            for i, s in enumerate(strata):
                clusters.append({
                    "cluster_id": f"cluster-{i:02d}", "identity_sha256": f"{i + 1:064x}", "stratum": s,
                    "declarations": [{"path": f"FormalConjectures/Fixture/P{i}.lean", "declaration_name": f"p{i}", "file_sha256": f"{100+i:064x}"}],
                    "selection_forecast": {}, "intervention_forecast": None,
                    "runnable": False if complete else None,
                    "structural_zero": ({"reason": "PHASE_0_STOP", "CATALOGUE": 0, "GENERIC": 0, "WALL_NAVIGATION": 0, "wall_vs_catalogue": "TIE", "wall_vs_generic": "TIE"} if complete else None),
                    "shared_analysis_contract": None, "independent_verification_contract": None,
                    "evaluation_started_at_utc": None, "arms": None,
                    "terminal_outcome": "PRESEARCH_STOP" if complete else None,
                    "terminal_evidence": copy.deepcopy(self.refs["terminal"]) if complete else None,
                    "theorem_evidence": None, "crossing_verification": None,
                })
        selected = [{"cluster_id": row["cluster_id"]} for row in clusters]
        self.write_artifact("selection", {"selected_clusters": selected})
        chronology = {
            "p0_artifact_commit": OID, "p0_attestation_commit": "d" * 40, "p0_published_at_utc": "2026-08-13T00:00:00Z",
            "s0_acquired_at_utc": "2026-08-13T01:00:00Z", "feasibility_checked_at_utc": "2026-08-13T02:00:00Z",
            "f0_artifact_commit": None, "f0_attestation_commit": None,
            "f0_published_at_utc": "2026-08-13T03:00:00Z" if not feasible else None,
            "c0_artifact_commit": "1" * 40 if feasible else None, "c0_attestation_commit": "2" * 40 if feasible else None,
            "c0_published_at_utc": "2026-08-13T03:00:00Z" if feasible else None,
            "randomness_retrieved_at_utc": "2026-08-13T05:00:00Z" if feasible else None,
            "c1_artifact_commit": "3" * 40 if complete else None, "c1_attestation_commit": "4" * 40 if complete else None,
            "c1_frozen_at_utc": "2026-08-13T06:00:00Z" if feasible else None,
            "evaluation_started_at_utc": "2026-08-13T07:00:00Z" if complete else None,
            "r0_artifact_commit": None, "r0_attestation_commit": None,
            "completed_at_utc": "2026-08-13T08:00:00Z" if complete else None,
        }
        chain = {"hash": "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce", "public_key": "868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31", "scheme_id": "pedersen-bls-chained", "genesis_time": 1595431050, "period_seconds": 30}
        randomness = ({"state": "VERIFIED", "source": "League of Entropy drand", "round": 9, "round_closes_at_utc": "2026-08-13T04:00:00Z", "chain": chain, "relays": ["https://api.drand.sh", "https://api2.drand.sh"], "selection_algorithm": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES", "value": "01" * 32, "value_sha256": LINTER.sha256(("01" * 32).encode()), "verified_artifact": copy.deepcopy(self.refs["randomness"])} if feasible else {"state": "UNARMED", "source": None, "round": None, "round_closes_at_utc": None, "chain": None, "relays": [], "selection_algorithm": None, "value": None, "value_sha256": None, "verified_artifact": None})
        manifest = {
            "$schema": "schemas/benchmark-v1.4.schema.json", "schema_version": LINTER.SCHEMA_VERSION, "benchmark_id": "v14-fixture", "phase": phase,
            "protocol": {"p0_artifact": copy.deepcopy(self.refs["p0a"]), "p0_attestation": copy.deepcopy(self.refs["p0t"]), "target_rows_present": False, "upstream_resolution_rule": copy.deepcopy(self.refs["rule"]), "prototype_artifacts": []},
            "source_snapshots": {"s0": {"snapshot_id": "S0", "path": freeze["source_snapshots"]["path"], "file_sha256": freeze["source_snapshots"]["sha256"], "snapshot_sha256": s0["snapshot_sha256"], "acquired_at_utc": "2026-08-13T01:00:00Z", "corpus_sha256": H, "complete": True, "immutable_ref": "git:s0"}, "supplemental": [], "complete": True, "canonical_sha256": freeze["source_snapshots"]["sha256"]},
            "upstream": {"repository": "google-deepmind/formal-conjectures", "commit": OID, "tree": TREE, "declaration_root": "FormalConjectures"},
            "freeze_artifacts": freeze,
            "provenance": {"policy": "SEMANTIC_OR_UNKNOWN_EXCLUDES_REGISTRY_ONLY_VISIBLE", "sources_complete": True, "allowlisted_producers": [{"producer_id": "builder", "executable_sha256": H, "invocation_contract_sha256": H, "input_schema_sha256": H, "output_schema_sha256": H}], "records": []},
            "quota_feasibility": cert, "randomness": randomness,
            "selection": {"sampling_unit": "QUESTION_CLUSTER", "target_cluster_count": 12, "quotas": copy.deepcopy(LINTER.QUOTAS), "no_backfill": True, "relaxed_exclusion": False, "replacement_events": [], "evidence": copy.deepcopy(self.refs["selection"]) if feasible else None},
            "budgets": {"shared_analysis": {"process_count": 10, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 600}, "discovery_arm": {"process_count": 8, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 480}, "independent_verification": {"process_count": 2, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 120}},
            "chronology": chronology,
            "commit_pairs": {"p0": self.pair("a"), "f0": None, "c0": self.pair("b") if feasible else None, "c1": self.pair("c") if complete else None, "r0": None},
            "clusters": clusters, "ledgers": [],
            "aggregates": ({"selected_n": 12, "aggregate_denominator": "ALL_SELECTED", "runnable_n": 0, "completed_arm_counts": {a: 0 for a in LINTER.ARMS}, "structural_zero_n": 12, "derived_from_ledgers": True, "hand_authored": False} if complete else None),
            "scoring": ({"input": copy.deepcopy(self.refs["score_input"]), "result": copy.deepcopy(self.refs["score_result"])} if complete else None),
        }
        manifest["source_snapshots"]["canonical_sha256"] = LINTER.canonical_object_sha256(
            manifest["source_snapshots"], "canonical_sha256"
        )
        return manifest

    def codes(self, manifest: dict, *, replay: bool = False) -> set[str]:
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        evidence = json.loads((self.root / "selection.json").read_text())
        context = patch.object(LINTER, "replay_selection", return_value=evidence) if replay else patch.object(LINTER, "replay_selection", side_effect=ValueError("fixture replay disabled"))
        with context, patch.object(LINTER, "replay_score", return_value={"schema_version": "fixture-score_result"}):
            return {row.code for row in LINTER.lint_manifest(self.manifest_path)}

    def test_positive_pre_c0_fail(self) -> None:
        self.assertEqual(self.codes(self.manifest(feasible=False)), set())

    def test_positive_feasible_c1_and_complete(self) -> None:
        self.assertEqual(self.codes(self.manifest(feasible=True), replay=True), set())
        self.assertEqual(self.codes(self.manifest(feasible=True, complete=True), replay=True), set())

    def test_c0t_is_noncircular_and_c1_binds_external_validation(self) -> None:
        m = self.manifest(feasible=True)
        m["phase"] = "C0_FROZEN"
        m["clusters"] = []
        m["selection"]["evidence"] = None
        m["randomness"]["state"] = "ARMED"
        m["randomness"]["value"] = None
        m["randomness"]["value_sha256"] = None
        m["randomness"]["verified_artifact"] = None
        m["freeze_artifacts"]["c0_validation_receipt"] = None
        m["chronology"]["c0_attestation_commit"] = None
        for key in ("randomness_retrieved_at_utc", "c1_artifact_commit", "c1_attestation_commit", "c1_frozen_at_utc"):
            m["chronology"][key] = None
        m["commit_pairs"]["c0"] = None
        self.assertEqual(self.codes(m), set())
        m["chronology"]["c0_attestation_commit"] = "2" * 40
        self.assertIn("CIRCULAR_C0", self.codes(m))

    def test_negative_provenance_laundering_and_mixed_unit(self) -> None:
        m = self.manifest(feasible=False)
        m["provenance"]["records"] = [{"unit_id": "u", "class": "MACHINE_REGISTRY_CONTACT", "identity_evidence_count": 1, "mixed": True, "producer_id": "missing", "input_sha256": None, "output_sha256": None, "input_artifact": None, "output_artifact": None, "schema_valid": False}]
        self.assertTrue({"PROVENANCE_MIXED", "PROVENANCE_LAUNDERING"}.issubset(self.codes(m)))

    def test_negative_missing_source_snapshot(self) -> None:
        m = self.manifest(feasible=False); m["source_snapshots"]["s0"]["complete"] = False
        self.assertIn("SCHEMA", self.codes(m))

    def test_negative_false_feasibility_counts(self) -> None:
        m = self.manifest(feasible=False); m["quota_feasibility"]["strata"][-1]["eligible_count"] += 1
        self.assertIn("FEASIBILITY_REPLAY", self.codes(m))

    def test_negative_beacon_on_failed_gate(self) -> None:
        m = self.manifest(feasible=False); m["freeze_artifacts"]["c0_randomness_contract"] = copy.deepcopy(self.refs["c0"])
        self.assertIn("FAILED_GATE_BEACON", self.codes(m))

    def test_negative_c0_before_pass_and_nonfuture_round(self) -> None:
        m = self.manifest(feasible=True); m["quota_feasibility"]["status"] = "FAIL"
        self.assertIn("C0_BEFORE_PASS", self.codes(m, replay=True))
        m = self.manifest(feasible=True); m["randomness"]["round_closes_at_utc"] = "2026-08-13T02:00:00Z"
        self.assertIn("RANDOMNESS_NOT_FUTURE", self.codes(m, replay=True))

    def test_negative_selection_replay_and_quota_drift(self) -> None:
        m = self.manifest(feasible=True)
        self.assertIn("SELECTION_REPLAY", self.codes(m))
        m = self.manifest(feasible=True); m["clusters"][0]["stratum"] = "FINITE_COMBINATORIAL"
        self.assertIn("C1_QUOTAS", self.codes(m, replay=True))

    def test_negative_post_c1_replacement(self) -> None:
        m = self.manifest(feasible=True); m["clusters"][0]["cluster_id"] = "replacement"
        self.assertIn("POST_C1_REPLACEMENT", self.codes(m, replay=True))

    def test_negative_unequal_arm_budget_and_prefreeze_evaluation(self) -> None:
        m = self.manifest(feasible=True, complete=True); c = m["clusters"][0]; c["runnable"] = True; c["structural_zero"] = None; c["shared_analysis_contract"] = copy.deepcopy(self.refs["terminal"]); c["independent_verification_contract"] = copy.deepcopy(self.refs["terminal"]); c["evaluation_started_at_utc"] = "2026-08-13T07:00:00Z"
        arm = {"contract": copy.deepcopy(self.refs["terminal"]), "process_count": 8, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 480, "seed": "s", "parameter_grid": {}, "transformation_id": "t", "no_adaptation": True, "frozen_at_utc": "2026-08-13T07:30:00Z", "started_at_utc": "2026-08-13T07:00:00Z", "status": "TERMINATED"}
        c["arms"] = {a: copy.deepcopy(arm) for a in LINTER.ARMS}; c["arms"]["GENERIC"]["cpu_budget_seconds"] = 479
        self.assertIn("SCHEMA", self.codes(m, replay=True))
        c["arms"]["GENERIC"]["cpu_budget_seconds"] = 480
        self.assertIn("PREFREEZE_EVALUATION", self.codes(m, replay=True))

    def test_negative_broken_ledger_chain(self) -> None:
        m = self.manifest(feasible=True, complete=True)
        row = {"benchmark_id": m["benchmark_id"], "unit_id": m["clusters"][0]["cluster_id"], "arm": "SHARED_ANALYSIS", "process_id": "p", "contract_sha256": H, "previous_row_sha256": "1" * 64, "wall_seconds": 1, "cpu_seconds": 1, "evaluated_at_utc": "2026-08-13T07:00:00Z"}; row["row_sha256"] = LINTER.canonical_row_sha256(row)
        self.write_artifact("ledger", {})
        path = self.root / "ledger.json"; path.write_text(json.dumps(row) + "\n"); m["ledgers"] = [{"path": path.name, "sha256": LINTER.sha256(path.read_bytes()), "append_only": True, "hash_chain": "SHA256_CANONICAL_JSON_WITHOUT_ROW_SHA256"}]
        self.assertIn("LEDGER_CHAIN", self.codes(m, replay=True))

    def test_negative_denominator_shrinkage(self) -> None:
        m = self.manifest(feasible=True, complete=True); m["aggregates"]["runnable_n"] = 1
        self.assertIn("DENOMINATOR_SHRINKAGE", self.codes(m, replay=True))


if __name__ == "__main__": unittest.main()
