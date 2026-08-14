#!/usr/bin/env python3
"""Validate Method v1.5's inherited executable classifier without target access.

The validator reads only the frozen classifier, its pool-builder executable,
and a target-free contract.  Conformance uses in-process synthetic syntax
vectors; it never opens a formal-conjectures checkout or emits fixture text.
"""

from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA = ROOT / "schemas/benchmark-five-strata-classifier-contract-v1.5.schema.json"
READINESS_SCHEMA = ROOT / "schemas/benchmark-five-strata-classifier-readiness-v1.5.schema.json"
EXPECTED_CLASSIFIER_KEYS = {
    "schema_version", "scope", "upstream", "permitted_inputs", "forbidden_inputs",
    "domain_signals", "graph_scalar_signal", "finite_signal",
    "classification_algorithm", "parser_contract", "cluster_rule", "output_policy",
}
DOMAINS = ("GRAPH", "FINITE_ALGEBRA_EQUATIONAL", "AUTOMATA_GAME_PROCESS")
STRATA = (
    "GRAPH_SCALAR_INEQUALITY", "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL", "AUTOMATA_GAME_PROCESS", "FINITE_COMBINATORIAL",
)
EXPECTED_BRANCHES = [
    ("GRAPH and not FINITE", None, "GRAPH_WITHOUT_FINITE_SIGNAL"),
    ("GRAPH and FINITE and OUTER_ORDERED_RELATION_CONCLUSION", "GRAPH_SCALAR_INEQUALITY", "FINITE_GRAPH_WITH_OUTER_ORDERED_CONCLUSION"),
    ("GRAPH and FINITE and not OUTER_ORDERED_RELATION_CONCLUSION", "GRAPH_STRUCTURAL_PROPERTY", "FINITE_GRAPH_WITHOUT_OUTER_ORDERED_CONCLUSION"),
    ("FINITE_ALGEBRA_EQUATIONAL and FINITE", "FINITE_ALGEBRA_EQUATIONAL", "ALGEBRA_AND_FINITE_SIGNALS"),
    ("FINITE_ALGEBRA_EQUATIONAL and not FINITE", None, "ALGEBRA_WITHOUT_FINITE_SIGNAL"),
    ("AUTOMATA_GAME_PROCESS", "AUTOMATA_GAME_PROCESS", "AUTOMATA_GAME_PROCESS_SYNTAX_SIGNAL"),
    ("no specialized domain and FINITE", "FINITE_COMBINATORIAL", "EXPLICIT_FINITE_SIGNAL"),
    ("otherwise", None, "UNCLASSIFIED_WITHOUT_FINITE_SIGNAL"),
]
FORBIDDEN_KEY_FRAGMENTS = (
    "target_id", "candidate_id", "cluster_id", "declaration_id",
    "proof_route", "counterexample", "outcome", "manual_override", "model_prompt",
)
ALLOWED_INPUTS = {
    "source path", "declaration kind and name", "declaration header syntax tokens",
    "source-module import and type syntax tokens", "open-category marker", "content digests",
}


class ClassifierClosureError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load(path: Path, where: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClassifierClosureError(f"cannot read {where}: {exc}") from exc
    if not isinstance(value, dict):
        raise ClassifierClosureError(f"{where} must be one JSON object")
    return value, raw


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).casefold()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _strict_regex_list(value: Any, where: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ClassifierClosureError(f"{where} must be a regex string array")
    for pattern in value:
        if len(pattern) > 512 or "(?P" in pattern or re.search(r"\\[1-9]", pattern):
            raise ClassifierClosureError(f"{where} contains an unsupported regex construct")
        try:
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
        except re.error as exc:
            raise ClassifierClosureError(f"{where} contains an invalid regex: {exc}") from exc
    return value


def validate_classifier(classifier: dict[str, Any], contract: dict[str, Any]) -> None:
    if set(classifier) != EXPECTED_CLASSIFIER_KEYS:
        raise ClassifierClosureError("classifier top-level fields are not exact executable closure")
    if classifier.get("schema_version") != contract["classifier"]["accepted_schema"]:
        raise ClassifierClosureError("classifier schema is not the inherited production schema")
    if set(classifier.get("permitted_inputs", [])) != ALLOWED_INPUTS:
        raise ClassifierClosureError("classifier permitted inputs are not the fixed syntax-only surface")
    forbidden = " ".join(classifier.get("forbidden_inputs", [])).casefold()
    for phrase in ("mathematical interpretation", "known proof or counterexample", "target-specific compute", "random rank or target selection"):
        if phrase not in forbidden:
            raise ClassifierClosureError(f"classifier does not forbid {phrase}")
    bad_keys = sorted({key for key in _walk_keys(classifier) if any(fragment in key for fragment in FORBIDDEN_KEY_FRAGMENTS)})
    if bad_keys:
        raise ClassifierClosureError(f"classifier contains target/semantic fields: {bad_keys}")

    signals = classifier.get("domain_signals")
    if not isinstance(signals, dict) or set(signals) != {"path_regex", "header_regex", "module_regex"}:
        raise ClassifierClosureError("domain_signals must be executable structured rules")
    expected_domains = {
        "path_regex": set(DOMAINS),
        "header_regex": set(DOMAINS),
        "module_regex": {"GRAPH", "AUTOMATA_GAME_PROCESS"},
    }
    for surface in ("path_regex", "header_regex", "module_regex"):
        table = signals[surface]
        if not isinstance(table, dict) or set(table) != expected_domains[surface]:
            raise ClassifierClosureError(f"domain_signals.{surface} has the wrong executable domains")
        for domain in expected_domains[surface]:
            _strict_regex_list(table[domain], f"domain_signals.{surface}.{domain}")
    finite = classifier.get("finite_signal")
    if not isinstance(finite, dict) or set(finite) != {"path_regex", "header_regex", "module_regex"}:
        raise ClassifierClosureError("finite_signal must define all three syntax surfaces")
    for surface in finite:
        _strict_regex_list(finite[surface], f"finite_signal.{surface}")
    scalar = classifier.get("graph_scalar_signal")
    if not isinstance(scalar, dict) or set(scalar) != {"outer_conclusion_relation_regex"}:
        raise ClassifierClosureError("graph scalar signal is not executable")
    _strict_regex_list(scalar["outer_conclusion_relation_regex"], "graph_scalar_signal.outer_conclusion_relation_regex")

    algorithm = classifier.get("classification_algorithm")
    if not isinstance(algorithm, dict) or set(algorithm) != {"domain_order", "multiple_domain_signals", "branches"}:
        raise ClassifierClosureError("classification algorithm is absent or prose-only")
    if algorithm["domain_order"] != list(DOMAINS) or algorithm["multiple_domain_signals"] != "MULTIPLE_DOMAIN_SIGNALS":
        raise ClassifierClosureError("classification domain precedence drifted")
    observed = []
    if not isinstance(algorithm["branches"], list):
        raise ClassifierClosureError("classification branches must be structured rows")
    for row in algorithm["branches"]:
        if not isinstance(row, dict) or set(row) != {"when", "stratum", "basis"}:
            raise ClassifierClosureError("classification branch fields are not exact")
        observed.append((row["when"], row["stratum"], row["basis"]))
    if observed != EXPECTED_BRANCHES:
        raise ClassifierClosureError("classification branches differ from the executable builder")
    parser = classifier.get("parser_contract")
    if not isinstance(parser, dict) or parser.get("ordered_relation_scope") != "outer conclusion top level only" or parser.get("regex_flags") != ["IGNORECASE", "DOTALL"]:
        raise ClassifierClosureError("outer-conclusion parser contract drifted")
    cluster = classifier.get("cluster_rule")
    if not isinstance(cluster, dict) or cluster.get("sampling_unit") != "ONE_SOURCE_MODULE_CONSERVATIVE_MERGE" or cluster.get("otherwise") != "AMBIGUOUS_EXCLUDE":
        raise ClassifierClosureError("classifier cluster rule is not conservative")
    output = classifier.get("output_policy")
    if not isinstance(output, dict) or any(output.get(key) is not False for key in ("statement_text", "random_ranks", "target_selection")):
        raise ClassifierClosureError("classifier output policy permits semantic or selection output")


def load_builder(path: Path, required: list[str]):
    if path.resolve() != (ROOT / "scripts/build_benchmark_v14_pool.py").resolve():
        raise ClassifierClosureError("builder path is not the inherited syntax_pool_builder")
    spec = importlib.util.spec_from_file_location("v15_classifier_builder_under_test", path)
    if spec is None or spec.loader is None:
        raise ClassifierClosureError("cannot load inherited syntax pool builder")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    missing = [name for name in required if not callable(getattr(module, name, None))]
    if missing:
        raise ClassifierClosureError(f"builder lacks required callable(s): {missing}")
    return module


def metadata(**true_values: bool) -> dict[str, bool]:
    keys = (
        "graph_path", "graph_header", "graph_module", "algebra_path", "algebra_header",
        "automata_game_process_path", "automata_game_process_header", "automata_game_process_module",
        "outer_ordered_relation_conclusion", "explicit_finite_header", "explicit_finite_path",
        "explicit_finite_module",
    )
    value = {key: False for key in keys}
    value.update(true_values)
    return value


def synthetic_conformance(builder: Any, classifier: dict[str, Any], contract: dict[str, Any]) -> dict[str, int]:
    # These are deliberately generic syntax vectors, not real registry rows.
    # Each passes through the classifier's regex tables and the actual builder
    # parser, covering path/header/module signal surfaces.
    vectors = [
        ("FormalConjectures/GraphConjectureSynthetic.lean", "theorem synthetic (n : Fin 4) : 1 ≤ 2", "", "GRAPH_SCALAR_INEQUALITY"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (G : SimpleGraph (Fin 4)) : 1 ≤ 2", "", "GRAPH_SCALAR_INEQUALITY"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (n : Fin 4) : 1 ≤ 2", "import Mathlib\n#check SimpleGraph", "GRAPH_SCALAR_INEQUALITY"),
        ("FormalConjectures/GraphConjectureSynthetic.lean", "theorem synthetic (n : Fin 4) : True", "", "GRAPH_STRUCTURAL_PROPERTY"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (G : SimpleGraph (Fin 4)) : True", "", "GRAPH_STRUCTURAL_PROPERTY"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (n : Fin 4) : True", "import Mathlib\n#check SimpleGraph", "GRAPH_STRUCTURAL_PROPERTY"),
        ("FormalConjectures/EquationalTheories/Synthetic.lean", "theorem synthetic (n : Fin 4) : True", "", "FINITE_ALGEBRA_EQUATIONAL"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (G : Group (Fin 4)) : True", "", "FINITE_ALGEBRA_EQUATIONAL"),
        ("FormalConjectures/SyntheticAutomaton.lean", "theorem synthetic (n : Nat) : True", "", "AUTOMATA_GAME_PROCESS"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (n : Nat) : True", "import Mathlib\n#check Automaton", "AUTOMATA_GAME_PROCESS"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (n : Fin 4) : True", "", "FINITE_COMBINATORIAL"),
        ("FormalConjectures/Synthetic.lean", "theorem synthetic (n : Nat) : True", "import Mathlib\n#check Finset", "FINITE_COMBINATORIAL"),
    ]
    observed_rows = []
    for path, header, module_text, expected_stratum in vectors:
        declaration_end = header.index("synthetic") + len("synthetic")
        row = builder.syntax_metadata(path, header, declaration_end, classifier, module_text)
        result = builder.classify(row)[0]
        if result != expected_stratum:
            raise ClassifierClosureError("classifier regex/parser path failed a synthetic positive stratum")
        observed_rows.append(result)
    counts = Counter(observed_rows)
    expected = contract["synthetic_conformance"]["required_positive_vector_counts"]
    observed = {stratum: counts[stratum] for stratum in STRATA}
    if observed != expected or counts[None]:
        raise ClassifierClosureError("builder does not realize the exact synthetic 3/3/2/2/2 suite")
    negative = [
        (metadata(graph_path=True, algebra_path=True, explicit_finite_header=True), "MULTIPLE_DOMAIN_SIGNALS"),
        (metadata(graph_path=True), "GRAPH_WITHOUT_FINITE_SIGNAL"),
        (metadata(algebra_path=True), "ALGEBRA_WITHOUT_FINITE_SIGNAL"),
        (metadata(), "UNCLASSIFIED_WITHOUT_FINITE_SIGNAL"),
    ]
    for row, basis in negative:
        if builder.classify(row) != (None, basis):
            raise ClassifierClosureError(f"builder negative conformance failed: {basis}")

    patterns = classifier["graph_scalar_signal"]["outer_conclusion_relation_regex"]
    premise = "theorem synthetic (G : SimpleGraph (Fin 4)) : 1 < 2 → True"
    end = premise.index("synthetic") + len("synthetic")
    conclusion = builder.declaration_conclusion(premise, end)
    if builder.has_outer_ordered_relation(conclusion, patterns):
        raise ClassifierClosureError("ordered premise leaked into scalar classification")
    nested = "theorem synthetic (G : SimpleGraph (Fin 4)) : (1 < 2) ∧ True"
    end = nested.index("synthetic") + len("synthetic")
    conclusion = builder.declaration_conclusion(nested, end)
    if builder.has_outer_ordered_relation(conclusion, patterns):
        raise ClassifierClosureError("nested ordered term leaked into scalar classification")
    return observed


def validate(contract_path: Path, classifier_path: Path, builder_path: Path) -> dict[str, Any]:
    contract, contract_raw = load(contract_path, "classifier closure contract")
    schema, _ = load(CONTRACT_SCHEMA, "classifier closure schema")
    errors = sorted(Draft7Validator(schema).iter_errors(contract), key=lambda error: list(error.path))
    if errors:
        raise ClassifierClosureError("classifier closure contract schema failed: " + "; ".join(error.message for error in errors))
    classifier, classifier_raw = load(classifier_path, "classifier")
    validate_classifier(classifier, contract)
    builder = load_builder(builder_path, contract["builder"]["required_callables"])
    counts = synthetic_conformance(builder, classifier, contract)
    receipt = {
        "schema": "c5k4-method-v1.5-five-strata-classifier-readiness-1.0",
        "status": "PRE_P1_TARGET_BLIND_CLASSIFIER_CLOSURE_READY",
        "target_data_read": False,
        "real_registry_access": False,
        "model_or_human_classification": False,
        "entropy_used": False,
        "selection_performed": False,
        "contract_sha256": sha256(contract_raw),
        "classifier_sha256": sha256(classifier_raw),
        "builder_sha256": sha256(builder_path.read_bytes()),
        "positive_vector_count": sum(counts.values()),
        "positive_counts": counts,
        "negative_property_count": len(contract["synthetic_conformance"]["required_negative_properties"]),
    }
    receipt["receipt_sha256"] = sha256(canonical_json(receipt))
    readiness_schema, _ = load(READINESS_SCHEMA, "classifier readiness schema")
    errors = sorted(Draft7Validator(readiness_schema).iter_errors(receipt), key=lambda error: list(error.path))
    if errors:
        raise ClassifierClosureError("classifier readiness schema failed: " + "; ".join(error.message for error in errors))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--builder", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.contract.resolve(), args.classifier.resolve(), args.builder.resolve())
    except ClassifierClosureError as exc:
        print(f"PRE_P1_CLASSIFIER_CLOSURE_REFUSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
