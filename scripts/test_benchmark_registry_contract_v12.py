#!/usr/bin/env python3
"""Contract tests for the one Method v1.2 production registry build."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA_PATH = ROOT / "schemas/benchmark-registry-input-v1.2.schema.json"
OUTPUT_SCHEMA_PATH = ROOT / "schemas/benchmark-registry-output-v1.2.schema.json"
CONTRACT_PATH = ROOT / "results/benchmark/v1.2-protocol/registry-build-invocation.json"
HEX64 = "a" * 64


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def validate(schema: dict, value: dict) -> None:
    Draft7Validator(schema, format_checker=FormatChecker()).validate(value)


def file_ref(name: str, authority: str = "FROZEN_PRODUCTION_INPUT") -> dict:
    return {
        "path": f"frozen/{name}.json",
        "file_sha256": HEX64,
        "canonical_sha256": "b" * 64,
        "schema_version": f"c5k4-{name}-1.2",
        "authority": authority,
    }


def input_fixture() -> dict:
    return {
        "schema_version": "c5k4-registry-build-input-1.2",
        "authority": "PRODUCTION_AFTER_P0T_S0",
        "protocol_version": "1.2",
        "build_ordinal": 1,
        "allowed_build_count": 1,
        "chronology": {
            "p0_artifact_commit": "1" * 40,
            "p0_attestation_commit": "2" * 40,
            "p0_published_at_utc": "2026-08-13T20:00:00Z",
            "s0_snapshot_id": "S0",
            "s0_acquired_at_utc": "2026-08-13T20:10:00Z",
            "s0_snapshot_sha256": "3" * 64,
        },
        "upstream": {
            "repository": "https://github.com/google-deepmind/formal-conjectures.git",
            "remote_ref": "refs/heads/main",
            "commit": "4" * 40,
            "tree": "5" * 40,
            "subtree": "FormalConjectures",
            "resolution_count": 1,
        },
        "producer": {
            "producer_id": "method-v1.2-production-registry-builder",
            "executable_path": "scripts/build_benchmark_v12_registry.py",
            "executable_sha256": "6" * 64,
            "invocation_contract_sha256": "7" * 64,
            "input_schema_sha256": "8" * 64,
            "output_schema_sha256": "9" * 64,
        },
        "inputs": {
            "p0a": file_ref("p0a", "AUTHORITATIVE_P0"),
            "p0t": file_ref("p0t", "AUTHORITATIVE_P0T"),
            "s0": file_ref("s0", "AUTHORITATIVE_S0"),
            "sources_config": file_ref("sources-config"),
            "five_strata_classifier": file_ref("five-strata-classifier"),
            "grouping_rule": file_ref("grouping-rule"),
            "provenance_policy": file_ref("provenance-policy"),
            "source_discovery_boundary": file_ref("source-discovery-boundary"),
            "quotas": file_ref("quotas"),
            "registry_exemptions": file_ref("registry-exemptions"),
        },
        "resolver_receipts": {
            "public_p0t": file_ref("p0t-advertisement-receipt"),
            "upstream_main": file_ref("upstream-resolution-receipt"),
        },
        "registry_build_invoked_at_utc": "2026-08-13T20:20:00Z",
        "controls": {
            "prototype_inputs_permitted": False,
            "candidate_semantics_inspected": False,
            "entropy_used": False,
            "selected_clusters": [],
            "selection_or_ranking_permitted": False,
            "create_exclusive_output_directory": True,
            "overwrite_permitted": False,
        },
    }


ARTIFACTS = (
    ("open_inventory", "open-inventory.json", "c5k4-open-inventory-1.2"),
    ("question_cluster_pool", "question-cluster-pool.json", "c5k4-question-cluster-pool-1.2"),
    ("provenance_inventory", "provenance-inventory.json", "c5k4-provenance-inventory-1.2"),
    ("contamination_inventory", "contamination-inventory.json", "c5k4-contamination-inventory-1.2"),
    ("eligible_pool", "eligible-cluster-pool.json", "c5k4-eligible-cluster-pool-1.2"),
    ("quota_feasibility", "quota-feasibility.json", "c5k4-quota-feasibility-1.2"),
)


def output_fixture() -> dict:
    source = input_fixture()
    strata = []
    for stratum, quota, count in (
        ("GRAPH_SCALAR_INEQUALITY", 3, 5),
        ("GRAPH_STRUCTURAL_PROPERTY", 3, 3),
        ("FINITE_ALGEBRA_EQUATIONAL", 2, 8),
        ("AUTOMATA_GAME_PROCESS", 2, 2),
        ("FINITE_COMBINATORIAL", 2, 200),
    ):
        strata.append({
            "stratum": stratum,
            "quota": quota,
            "eligible_count": count,
            "deficit": max(0, quota - count),
            "surplus": max(0, count - quota),
        })
    return {
        "schema_version": "c5k4-registry-build-output-1.2",
        "authority": "PRODUCTION_REGISTRY_BUILD",
        "protocol_version": "1.2",
        "build_ordinal": 1,
        "input_file_sha256": "a" * 64,
        "input_canonical_sha256": "b" * 64,
        "chronology": {
            **source["chronology"],
            "registry_build_completed_at_utc": "2026-08-13T20:21:00Z",
        },
        "upstream": source["upstream"],
        "producer": {key: value for key, value in source["producer"].items() if key != "executable_path"},
        "controls": {
            "prototype_inputs_used": False,
            "candidate_semantics_inspected": False,
            "entropy_used": False,
            "selected_clusters": [],
            "selection_or_ranking_performed": False,
            "output_directory_created_exclusively": True,
            "preexisting_output_replaced": False,
        },
        "artifacts": [
            {
                "artifact_id": artifact_id,
                "path": path,
                "file_sha256": f"{index + 1:064x}",
                "canonical_sha256": f"{index + 11:064x}",
                "schema_version": schema,
                "row_count": 729 if artifact_id != "quota_feasibility" else 5,
            }
            for index, (artifact_id, path, schema) in enumerate(ARTIFACTS)
        ],
        "feasibility_replay": {
            "row_source_artifact_id": "eligible_pool",
            "row_source_canonical_sha256": f"{15:064x}",
            "eligibility_rule": "MACHINE_CLASSIFIED_AND_IDENTITY_COMPLETE_AND_NO_SEMANTIC_OR_UNKNOWN_EXPOSURE",
            "all_rows_replayed": True,
            "total_row_count": 729,
            "eligible_row_count": sum(row[2] for row in ((None, None, 5), (None, None, 3), (None, None, 8), (None, None, 2), (None, None, 200))),
            "quotas": {
                "GRAPH_SCALAR_INEQUALITY": 3,
                "GRAPH_STRUCTURAL_PROPERTY": 3,
                "FINITE_ALGEBRA_EQUATIONAL": 2,
                "AUTOMATA_GAME_PROCESS": 2,
                "FINITE_COMBINATORIAL": 2,
            },
            "strata": strata,
            "status": "PASS",
            "terminal_result": None,
            "entropy_used": False,
            "selected_clusters": [],
        },
        "output_sha256": "f" * 64,
    }


class RegistryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_schema = load(INPUT_SCHEMA_PATH)
        cls.output_schema = load(OUTPUT_SCHEMA_PATH)
        cls.contract = load(CONTRACT_PATH)
        Draft7Validator.check_schema(cls.input_schema)
        Draft7Validator.check_schema(cls.output_schema)

    def test_production_input_and_output_validate(self) -> None:
        validate(self.input_schema, input_fixture())
        validate(self.output_schema, output_fixture())

    def test_pre_p0_or_entropy_or_selection_fail_closed(self) -> None:
        for path, value in (
            (("authority",), "PRE_P0_NOT_FREEZE"),
            (("controls", "prototype_inputs_permitted"), True),
            (("controls", "entropy_used"), True),
            (("controls", "selected_clusters"), ["target"]),
        ):
            fixture = input_fixture()
            target = fixture
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.assertRaises(Exception, msg=str(path)):
                validate(self.input_schema, fixture)

    def test_p0t_s0_upstream_and_digest_bindings_are_mandatory(self) -> None:
        for section, key in (
            ("chronology", "p0_attestation_commit"),
            ("chronology", "s0_snapshot_sha256"),
            ("upstream", "commit"),
            ("upstream", "tree"),
            ("producer", "invocation_contract_sha256"),
            ("inputs", "registry_exemptions"),
        ):
            fixture = input_fixture()
            del fixture[section][key]
            with self.assertRaises(Exception, msg=f"{section}.{key}"):
                validate(self.input_schema, fixture)

    def test_exactly_six_distinct_artifact_kinds_are_required(self) -> None:
        fixture = output_fixture()
        fixture["artifacts"][-1] = copy.deepcopy(fixture["artifacts"][0])
        with self.assertRaises(Exception):
            validate(self.output_schema, fixture)
        fixture = output_fixture()
        fixture["artifacts"].pop()
        with self.assertRaises(Exception):
            validate(self.output_schema, fixture)

    def test_artifact_identity_path_and_schema_cannot_be_cross_wired(self) -> None:
        fixture = output_fixture()
        fixture["artifacts"][0]["path"] = "quota-feasibility.json"
        with self.assertRaises(Exception):
            validate(self.output_schema, fixture)

    def test_feasibility_needs_each_fixed_stratum_and_consistent_branch(self) -> None:
        fixture = output_fixture()
        fixture["feasibility_replay"]["strata"][-1] = copy.deepcopy(
            fixture["feasibility_replay"]["strata"][0]
        )
        with self.assertRaises(Exception):
            validate(self.output_schema, fixture)
        fixture = output_fixture()
        fixture["feasibility_replay"]["terminal_result"] = "NO_ELIGIBLE_BENCHMARK_PRE_C0"
        with self.assertRaises(Exception):
            validate(self.output_schema, fixture)

    def test_output_cannot_claim_entropy_selection_or_overwrite(self) -> None:
        for key, value in (
            ("entropy_used", True),
            ("selected_clusters", ["target"]),
            ("selection_or_ranking_performed", True),
            ("preexisting_output_replaced", True),
        ):
            fixture = output_fixture()
            fixture["controls"][key] = value
            with self.assertRaises(Exception, msg=key):
                validate(self.output_schema, fixture)

    def test_invocation_is_exact_create_exclusive_single_build(self) -> None:
        self.assertEqual(self.contract["execution"]["allowed_build_count"], 1)
        self.assertEqual(self.contract["execution"]["build_ordinal"], 1)
        self.assertTrue(self.contract["execution"]["create_exclusive_output_directory"])
        self.assertFalse(self.contract["execution"]["overwrite_permitted"])
        self.assertFalse(self.contract["execution"]["entropy_permitted"])
        network = self.contract["execution"]["network_boundary"]
        self.assertEqual(network["preflight"]["default"], "FORBIDDEN")
        self.assertEqual(network["preflight"]["total_maximum_calls"], 2)
        self.assertFalse(network["preflight"]["retry_permitted"])
        self.assertFalse(network["production_build"]["network_permitted"])
        self.assertTrue(network["production_build"]["receipt_replay_required"])
        self.assertEqual(
            [row["purpose"] for row in network["preflight"]["allowed_calls"]],
            ["VERIFY_PUBLIC_P0T_ADVERTISEMENT", "SOLE_UPSTREAM_REF_RESOLUTION"],
        )
        self.assertEqual(self.contract["output_artifact_ids"], [row[0] for row in ARTIFACTS])
        self.assertEqual(len(self.contract["required_output_files"]), 7)

    def test_contract_paths_and_schema_ids_are_exact(self) -> None:
        self.assertEqual(self.contract["input_schema"], INPUT_SCHEMA_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(self.contract["output_schema"], OUTPUT_SCHEMA_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(self.input_schema["properties"]["schema_version"]["const"], "c5k4-registry-build-input-1.2")
        self.assertEqual(self.output_schema["properties"]["schema_version"]["const"], "c5k4-registry-build-output-1.2")


if __name__ == "__main__":
    unittest.main()
