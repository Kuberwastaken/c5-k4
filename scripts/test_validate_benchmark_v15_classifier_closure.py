#!/usr/bin/env python3
"""Adversarial tests for Method v1.5 PRE-P1 classifier closure."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_benchmark_v15_classifier_closure.py"
SPEC = importlib.util.spec_from_file_location("v15_classifier_closure", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)
CONTRACT = ROOT / "results/benchmark/v1.5-protocol/five-strata-classifier-contract.json"
CLASSIFIER = ROOT / "results/benchmark/v1.4-protocol/five-strata-classifier.json"
BUILDER = ROOT / "scripts/build_benchmark_v14_pool.py"


class ClassifierClosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.classifier = json.loads(CLASSIFIER.read_text())
        self.contract = json.loads(CONTRACT.read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def classifier_path(self, value: dict) -> Path:
        path = self.root / "classifier.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def contract_path(self, value: dict) -> Path:
        path = self.root / "contract.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def validate_classifier(self, value: dict) -> None:
        V.validate_classifier(value, self.contract)

    def test_inherited_classifier_is_executable_and_exactly_3_3_2_2_2(self) -> None:
        receipt = V.validate(CONTRACT, CLASSIFIER, BUILDER)
        self.assertEqual(receipt["positive_counts"], self.contract["strata_and_quotas"])
        self.assertEqual(receipt["positive_vector_count"], 12)
        self.assertFalse(receipt["target_data_read"])
        self.assertFalse(receipt["real_registry_access"])
        self.assertFalse(receipt["model_or_human_classification"])
        self.assertNotIn("identit", json.dumps(receipt).casefold())
        schema = json.loads(V.READINESS_SCHEMA.read_text())
        self.assertEqual(list(Draft7Validator(schema).iter_errors(receipt)), [])

    def test_prose_only_or_missing_structured_rules_are_rejected(self) -> None:
        for replacement in ("classify graph syntax", {}, None):
            changed = copy.deepcopy(self.classifier)
            changed["domain_signals"] = replacement
            with self.assertRaisesRegex(V.ClassifierClosureError, "executable structured|three domains"):
                self.validate_classifier(changed)

    def test_malformed_or_unsupported_regex_is_rejected(self) -> None:
        for pattern in ("(", r"(Graph)\\1", "x" * 513):
            changed = copy.deepcopy(self.classifier)
            changed["domain_signals"]["path_regex"]["GRAPH"] = [pattern]
            with self.assertRaisesRegex(V.ClassifierClosureError, "regex"):
                self.validate_classifier(changed)

    def test_syntactically_valid_regex_drift_fails_builder_conformance(self) -> None:
        changed = copy.deepcopy(self.classifier)
        changed["domain_signals"]["path_regex"]["GRAPH"] = ["NEVER_MATCH_SYNTHETIC"]
        changed["domain_signals"]["header_regex"]["GRAPH"] = ["NEVER_MATCH_SYNTHETIC"]
        changed["domain_signals"]["module_regex"]["GRAPH"] = ["NEVER_MATCH_SYNTHETIC"]
        with self.assertRaisesRegex(V.ClassifierClosureError, "synthetic positive stratum"):
            V.validate(CONTRACT, self.classifier_path(changed), BUILDER)

    def test_algorithm_branch_or_domain_precedence_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.classifier)
        changed["classification_algorithm"]["branches"][1]["stratum"] = "GRAPH_STRUCTURAL_PROPERTY"
        with self.assertRaisesRegex(V.ClassifierClosureError, "branches differ"):
            self.validate_classifier(changed)
        changed = copy.deepcopy(self.classifier)
        changed["classification_algorithm"]["domain_order"].reverse()
        with self.assertRaisesRegex(V.ClassifierClosureError, "precedence drifted"):
            self.validate_classifier(changed)

    def test_semantic_manual_model_or_identity_fields_are_rejected(self) -> None:
        for key in ("target_identity", "manual_override", "model_prompt", "outcomes"):
            changed = copy.deepcopy(self.classifier)
            changed[key] = []
            with self.assertRaisesRegex(V.ClassifierClosureError, "top-level fields"):
                self.validate_classifier(changed)
        changed = copy.deepcopy(self.classifier)
        changed["permitted_inputs"].append("natural-language mathematical meaning")
        with self.assertRaisesRegex(V.ClassifierClosureError, "syntax-only surface"):
            self.validate_classifier(changed)

    def test_statement_rank_or_selection_output_is_rejected(self) -> None:
        for key in ("statement_text", "random_ranks", "target_selection"):
            changed = copy.deepcopy(self.classifier)
            changed["output_policy"][key] = True
            with self.assertRaisesRegex(V.ClassifierClosureError, "output policy"):
                self.validate_classifier(changed)

    def test_outer_relation_parser_separates_premise_and_nested_terms(self) -> None:
        builder = V.load_builder(BUILDER, self.contract["builder"]["required_callables"])
        counts = V.synthetic_conformance(builder, self.classifier, self.contract)
        self.assertEqual(counts, self.contract["strata_and_quotas"])

    def test_wrong_builder_or_missing_callable_is_rejected(self) -> None:
        with self.assertRaisesRegex(V.ClassifierClosureError, "builder path"):
            V.load_builder(self.root / "other.py", self.contract["builder"]["required_callables"])
        with self.assertRaisesRegex(V.ClassifierClosureError, "lacks required"):
            V.load_builder(BUILDER, [*self.contract["builder"]["required_callables"], "missing_callable"])

    def test_contract_cannot_relax_quota_or_target_blindness(self) -> None:
        changed = copy.deepcopy(self.contract)
        changed["strata_and_quotas"]["GRAPH_SCALAR_INEQUALITY"] = 2
        with self.assertRaises(V.ClassifierClosureError):
            V.validate(self.contract_path(changed), CLASSIFIER, BUILDER)
        changed = copy.deepcopy(self.contract)
        changed["synthetic_conformance"]["real_registry_access"] = True
        with self.assertRaises(V.ClassifierClosureError):
            V.validate(self.contract_path(changed), CLASSIFIER, BUILDER)


if __name__ == "__main__":
    unittest.main()
