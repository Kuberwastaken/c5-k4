#!/usr/bin/env python3
"""Regression tests for the Method v1.1 benchmark-manifest linter."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("lint_benchmark_v11.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v11_linter", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)

SELECTOR_SCRIPT = Path(__file__).with_name("select_benchmark_v11.py")
SELECTOR_SPEC = importlib.util.spec_from_file_location("benchmark_v11_selector_test", SELECTOR_SCRIPT)
assert SELECTOR_SPEC is not None and SELECTOR_SPEC.loader is not None
SELECTOR = importlib.util.module_from_spec(SELECTOR_SPEC)
SELECTOR_SPEC.loader.exec_module(SELECTOR)


H64 = "a" * 64
OID = "b" * 40
PROBABILITIES = {
    "CROSS": "0.20",
    "ZERO_COMPLETE": "0.20",
    "THEOREM_STRUCTURE": "0.20",
    "PRESEARCH_STOP": "0.15",
    "TIMEOUT": "0.15",
    "PROTOCOL_INVALID": "0.10",
}
STRATA = (
    ["GRAPH_SCALAR_INEQUALITY"] * 3
    + ["GRAPH_STRUCTURAL_PROPERTY"] * 3
    + ["FINITE_ALGEBRA_EQUATIONAL"] * 2
    + ["AUTOMATA_GAME_PROCESS"] * 2
    + ["FINITE_COMBINATORIAL"] * 2
)
RANDOMNESS = "01" * 32


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class BenchmarkLintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest_path = self.root / "benchmark.json"
        self.artifacts: dict[str, dict[str, str]] = {}
        for name in (
            "inventory",
            "pool",
            "classifier",
            "prior",
            "library",
            "scoring",
            "stopping",
            "contamination",
            "arm",
            "raw",
        ):
            path = self.root / f"{name}.txt"
            path.write_text(f"frozen {name}\n", encoding="utf-8")
            self.artifacts[name] = {"path": path.name, "sha256": digest(path.read_bytes())}
        pool = {
            "schema_version": SELECTOR.POOL_SCHEMA_VERSION,
            "upstream": {"commit": OID, "tree": "c" * 40},
            "contamination": {
                "applied": True,
                "inventory_sha256": "f" * 64,
                "identity_ambiguity_means_exclusion": True,
            },
            "clusters": [
                {
                    "cluster_id": f"cluster-{index:02d}",
                    "identity_sha256": f"{index + 1:064x}",
                    "stratum": stratum,
                    "eligible": True,
                }
                for index, stratum in enumerate(STRATA)
            ],
        }
        pool_path = self.root / "pool.txt"
        pool_path.write_text(json.dumps(pool, indent=2), encoding="utf-8")
        self.artifacts["pool"] = {"path": pool_path.name, "sha256": digest(pool_path.read_bytes())}
        selection = SELECTOR.select(pool_path.read_bytes(), RANDOMNESS)
        self.selection = selection
        selection_path = self.root / "selection.json"
        selection_path.write_text(json.dumps(selection, indent=2), encoding="utf-8")
        self.artifacts["selection"] = {
            "path": selection_path.name,
            "sha256": digest(selection_path.read_bytes()),
        }

    def tearDown(self):
        self.temp.cleanup()

    def forecast(self, frozen: str = "2026-08-14T03:00:00Z") -> dict:
        return {"frozen_at_utc": frozen, "probabilities": copy.deepcopy(PROBABILITIES)}

    def manifest(self) -> dict:
        clusters = []
        for selected in self.selection["selected_clusters"]:
            index = int(selected["cluster_id"].removeprefix("cluster-"))
            stratum = selected["stratum"]
            clusters.append({
                "cluster_id": selected["cluster_id"],
                "identity_sha256": selected["identity_sha256"],
                "stratum": stratum,
                "declarations": [{
                    "path": f"FormalConjectures/Test/Problem{index}.lean",
                    "declaration_name": f"problem_{index}",
                    "file_sha256": f"{index + 101:064x}",
                }],
                "selection_forecast": self.forecast(),
                "intervention_forecast": None,
                "runnable": None,
                "arms_frozen_at_utc": None,
                "evaluation_started_at_utc": None,
                "arms": None,
                "terminal_outcome": None,
            })
        value = RANDOMNESS
        return {
            "$schema": "schemas/benchmark-v1.1.schema.json",
            "schema_version": LINTER.SCHEMA_VERSION,
            "benchmark_id": "heldout-001",
            "phase": "C1_SELECTED",
            "upstream": {
                "repository": "google-deepmind/formal-conjectures",
                "commit": OID,
                "tree": "c" * 40,
                "declaration_root": "FormalConjectures",
                "open_inventory": copy.deepcopy(self.artifacts["inventory"]),
            },
            "freeze_artifacts": {
                "pool_manifest": copy.deepcopy(self.artifacts["pool"]),
                "classifier": copy.deepcopy(self.artifacts["classifier"]),
                "development_prior": {
                    **copy.deepcopy(self.artifacts["prior"]),
                    "probabilities": copy.deepcopy(PROBABILITIES),
                },
                "transformation_library": copy.deepcopy(self.artifacts["library"]),
                "scoring_rule": copy.deepcopy(self.artifacts["scoring"]),
                "stopping_rule": copy.deepcopy(self.artifacts["stopping"]),
            },
            "contamination": {
                "inventory": copy.deepcopy(self.artifacts["contamination"]),
                "excluded_cluster_ids": [],
                "excluded_identity_sha256s": [],
                "excluded_declaration_sha256s": [],
                "identity_ambiguity_means_exclusion": True,
            },
            "randomness": {
                "source": "League of Entropy drand legacy mainnet",
                "round": 123456,
                "round_closes_at_utc": "2026-08-14T01:00:00Z",
                "chain": {
                    "hash": "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce",
                    "public_key": "868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c529eeda66c7293784a9402801af31",
                    "scheme_id": "pedersen-bls-chained",
                    "genesis_time": 1595431050,
                    "period_seconds": 30,
                },
                "relays": ["https://api.drand.sh", "https://api2.drand.sh"],
                "verification": {
                    "library": "drand-client",
                    "library_version": "1.4.2",
                    "require_exact_round": True,
                    "require_relay_equality": True,
                    "require_bls_signature": True,
                    "require_randomness_sha256_signature": True,
                    "raw_artifact": copy.deepcopy(self.artifacts["raw"]),
                },
                "selection_algorithm": "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES_V1",
                "value": value,
                "value_sha256": digest(value.encode("utf-8")),
            },
            "selection": {
                "sampling_unit": "QUESTION_CLUSTER",
                "target_cluster_count": 12,
                "quotas": {
                    "GRAPH_SCALAR_INEQUALITY": 3,
                    "GRAPH_STRUCTURAL_PROPERTY": 3,
                    "FINITE_ALGEBRA_EQUATIONAL": 2,
                    "AUTOMATA_GAME_PROCESS": 2,
                    "FINITE_COMBINATORIAL": 2,
                },
                "no_backfill": True,
                "relaxed_exclusion": False,
                "backfill_events": [],
                "insufficient_stratum_outcome": "NO_ELIGIBLE_BENCHMARK",
                "evidence": copy.deepcopy(self.artifacts["selection"]),
            },
            "budgets": {
                "shared_analysis": {"cpu_budget_seconds": 600, "process_wall_cap_seconds": 60},
                "discovery_arm": {"process_count": 8, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 480},
                "independent_verification": {"process_count": 2, "process_wall_cap_seconds": 60, "cpu_budget_seconds": 120},
            },
            "chronology": {
                "c0_commit": "d" * 40,
                "c0_published_at_utc": "2026-08-14T00:00:00Z",
                "randomness_retrieved_at_utc": "2026-08-14T02:00:00Z",
                "c1_commit": "e" * 40,
                "c1_frozen_at_utc": "2026-08-14T03:00:00Z",
                "evaluation_started_at_utc": None,
                "completed_at_utc": None,
            },
            "clusters": clusters,
            "ledgers": [],
        }

    def attach_arms(self, manifest: dict, cluster_index: int = 0) -> None:
        cluster = manifest["clusters"][cluster_index]
        cluster["runnable"] = True
        cluster["intervention_forecast"] = self.forecast("2026-08-14T04:00:00Z")
        cluster["arms_frozen_at_utc"] = "2026-08-14T05:00:00Z"
        cluster["arms"] = {}
        for arm_name in LINTER.ARMS:
            cluster["arms"][arm_name] = {
                "contract": copy.deepcopy(self.artifacts["arm"]),
                "process_count": 8,
                "process_wall_cap_seconds": 60,
                "cpu_budget_seconds": 480,
                "seed": f"seed-{arm_name}",
                "parameter_grid": {"only_grid": [1, 2]},
                "transformation_id": f"frozen-{arm_name.lower()}",
                "no_adaptation": True,
                "status": "PENDING",
            }

    def write(self, manifest: dict) -> None:
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def codes(self, manifest: dict) -> set[str]:
        self.write(manifest)
        return {finding.code for finding in LINTER.lint_manifest(self.manifest_path)}

    def test_valid_c1_manifest_passes(self):
        self.assertEqual(self.codes(self.manifest()), set())

    def test_exact_probability_simplex(self):
        manifest = self.manifest()
        manifest["clusters"][0]["selection_forecast"]["probabilities"]["CROSS"] = "0.25"
        self.assertIn("PROBABILITY_SIMPLEX", self.codes(manifest))
        manifest = self.manifest()
        manifest["freeze_artifacts"]["development_prior"]["probabilities"]["CROSS"] = 0.20
        self.assertIn("SCHEMA", self.codes(manifest))

    def test_exact_twelve_quotas_and_cluster_uniqueness(self):
        manifest = self.manifest()
        manifest["clusters"][0]["stratum"] = "FINITE_COMBINATORIAL"
        self.assertIn("STRATA_QUOTAS", self.codes(manifest))
        manifest = self.manifest()
        manifest["clusters"][1]["cluster_id"] = manifest["clusters"][0]["cluster_id"]
        manifest["clusters"][1]["identity_sha256"] = manifest["clusters"][0]["identity_sha256"]
        codes = self.codes(manifest)
        self.assertTrue({"CLUSTER_UNIQUENESS", "IDENTITY_UNIQUENESS"}.issubset(codes))

    def test_no_backfill_is_schema_locked(self):
        manifest = self.manifest()
        manifest["selection"]["no_backfill"] = False
        manifest["selection"]["backfill_events"] = [{"replacement": "x"}]
        self.assertIn("SCHEMA", self.codes(manifest))

    def test_contamination_must_be_disjoint(self):
        manifest = self.manifest()
        first = manifest["clusters"][0]
        manifest["contamination"]["excluded_cluster_ids"] = [first["cluster_id"]]
        manifest["contamination"]["excluded_identity_sha256s"] = [first["identity_sha256"]]
        manifest["contamination"]["excluded_declaration_sha256s"] = [first["declarations"][0]["file_sha256"]]
        codes = self.codes(manifest)
        self.assertTrue({"CONTAMINATED_CLUSTER", "CONTAMINATED_IDENTITY", "CONTAMINATED_DECLARATION"}.issubset(codes))

    def test_paths_are_confined_to_pinned_formal_conjectures_tree(self):
        manifest = self.manifest()
        manifest["clusters"][0]["declarations"][0]["path"] = "FormalConjectures/../escape.lean"
        self.assertIn("UPSTREAM_PATH", self.codes(manifest))
        manifest = self.manifest()
        manifest["upstream"]["repository"] = "somewhere/else"
        self.assertIn("SCHEMA", self.codes(manifest))

    def test_equal_arm_budgets_and_hard_caps(self):
        manifest = self.manifest()
        self.attach_arms(manifest)
        manifest["clusters"][0]["arms"]["GENERIC"]["cpu_budget_seconds"] = 420
        codes = self.codes(manifest)
        self.assertTrue({"ARM_GLOBAL_BUDGET", "ARM_BUDGET_EQUALITY"}.issubset(codes))
        manifest = self.manifest()
        manifest["budgets"]["discovery_arm"]["process_wall_cap_seconds"] = 61
        self.assertIn("SCHEMA", self.codes(manifest))

    def test_future_randomness_and_chronology(self):
        manifest = self.manifest()
        manifest["randomness"]["round_closes_at_utc"] = "2026-08-13T23:00:00Z"
        self.assertIn("RANDOMNESS_NOT_FUTURE", self.codes(manifest))
        manifest = self.manifest()
        manifest["randomness"]["value_sha256"] = H64
        self.assertIn("RANDOMNESS_DIGEST", self.codes(manifest))
        manifest = self.manifest()
        manifest["chronology"]["c1_frozen_at_utc"] = "2026-08-14T01:30:00Z"
        self.assertIn("CHRONOLOGY", self.codes(manifest))
        manifest = self.manifest()
        manifest["randomness"]["verification"]["raw_artifact"] = None
        self.assertIn("RANDOMNESS_ARTIFACT_REQUIRED", self.codes(manifest))

    def test_forecasts_and_arm_contracts_precede_evaluation(self):
        manifest = self.manifest()
        self.attach_arms(manifest)
        manifest["clusters"][0]["intervention_forecast"]["frozen_at_utc"] = "2026-08-14T05:30:00Z"
        manifest["clusters"][0]["evaluation_started_at_utc"] = "2026-08-14T04:45:00Z"
        codes = self.codes(manifest)
        self.assertTrue({"INTERVENTION_FORECAST_LATE", "ARM_FREEZE_LATE"}.issubset(codes))

    def test_protocol_design_leaves_future_and_freezes_null(self):
        manifest = self.manifest()
        manifest["phase"] = "PROTOCOL_DESIGN"
        manifest["randomness"]["verification"]["raw_artifact"] = None
        self.assertTrue({"PREMATURE_SELECTION", "PREMATURE_FREEZE", "PREMATURE_RANDOMNESS"}.issubset(self.codes(manifest)))

    def test_selection_evidence_is_required_and_authenticated(self):
        manifest = self.manifest()
        manifest["selection"]["evidence"] = None
        self.assertIn("SELECTION_EVIDENCE_REQUIRED", self.codes(manifest))
        manifest = self.manifest()
        selection_path = self.root / "selection.json"
        evidence = json.loads(selection_path.read_text())
        evidence["selected_clusters"][0]["cluster_id"] = "tampered"
        selection_path.write_text(json.dumps(evidence, indent=2))
        manifest["selection"]["evidence"]["sha256"] = digest(selection_path.read_bytes())
        codes = self.codes(manifest)
        self.assertTrue({"SELECTION_EVIDENCE_DIGEST", "SELECTION_EVIDENCE_MEMBERSHIP"}.issubset(codes))

    def make_row(self, manifest: dict, previous: str, process: str, cpu: float = 1.0) -> dict:
        row = {
            "benchmark_id": manifest["benchmark_id"],
            "unit_id": manifest["clusters"][0]["cluster_id"],
            "arm": "INDEPENDENT_VERIFICATION",
            "process_id": process,
            "contract_sha256": H64,
            "transformation_id": "verify-only",
            "carrier_sha256": "f" * 64,
            "previous_row_sha256": previous,
            "wall_seconds": min(cpu, 60),
            "cpu_seconds": cpu,
            "evaluated_at_utc": "2026-08-14T06:00:00Z",
        }
        row["row_sha256"] = LINTER.canonical_row_sha256(row)
        return row

    def install_ledger(self, manifest: dict, rows: list[dict]) -> Path:
        ledger = self.root / "ledger.jsonl"
        ledger.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        manifest["ledgers"] = [{
            "path": ledger.name,
            "sha256": digest(ledger.read_bytes()),
            "append_only": True,
            "hash_chain": "SHA256_CANONICAL_JSON_WITHOUT_ROW_SHA256",
        }]
        return ledger

    def test_hash_chained_ledger_and_tamper_detection(self):
        manifest = self.manifest()
        first = self.make_row(manifest, LINTER.ZERO_SHA256, "p0")
        second = self.make_row(manifest, first["row_sha256"], "p1")
        self.install_ledger(manifest, [first, second])
        self.assertEqual(self.codes(manifest), set())

        second["previous_row_sha256"] = H64
        self.install_ledger(manifest, [first, second])
        codes = self.codes(manifest)
        self.assertTrue({"LEDGER_CHAIN", "LEDGER_ROW_DIGEST"}.issubset(codes))

    def test_ledger_process_and_cpu_totals(self):
        manifest = self.manifest()
        rows = []
        previous = LINTER.ZERO_SHA256
        for index in range(3):
            row = self.make_row(manifest, previous, f"p{index}", cpu=50)
            rows.append(row)
            previous = row["row_sha256"]
        self.install_ledger(manifest, rows)
        codes = self.codes(manifest)
        self.assertTrue({"LEDGER_PROCESS_TOTAL", "LEDGER_CPU_TOTAL"}.issubset(codes))

    def test_artifact_digests_are_checked(self):
        manifest = self.manifest()
        manifest["freeze_artifacts"]["pool_manifest"]["sha256"] = H64
        self.assertIn("ARTIFACT_DIGEST", self.codes(manifest))


if __name__ == "__main__":
    unittest.main()
