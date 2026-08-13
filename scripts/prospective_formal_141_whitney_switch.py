#!/usr/bin/env python3
"""Frozen unique-triangle Whitney-switch trial for WOWII #141."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_formal_141_whitney_switch_contract.md"
LEDGER = ROOT / "results/expansion/prospective_formal_141_whitney_switch_ledger.jsonl"
BASELINE = ROOT / "results/expansion/prospective_formal_141_s4_cover_ledger.jsonl"
CONTRACT_SHA256 = "0d756cd52f81303ec8be70ae1917b73ea62682adb0c20a20519ecfa64de22422"
BASELINE_SHA256 = "b10753f8a3c48c5d4bcf5f0c74fed12c2b4c300f699824989d3e09beb4c27d0a"
PARENT_PATH = ROOT / "scripts/prospective_formal_oneoff_141.py"
SPEC = importlib.util.spec_from_file_location("wow141_parent_whitney", PARENT_PATH)
assert SPEC and SPEC.loader
PARENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARENT)


def check_contract() -> None:
    actual = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if actual != CONTRACT_SHA256:
        raise RuntimeError(f"frozen contract changed: {actual}")
    baseline = hashlib.sha256(BASELINE.read_bytes()).hexdigest()
    if baseline != BASELINE_SHA256:
        raise RuntimeError(f"selection ledger changed: {baseline}")


def emit(row: dict) -> None:
    line = json.dumps({"contract_sha256": CONTRACT_SHA256, **row}, sort_keys=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
    print(line, flush=True)


def baseline_rows() -> dict[tuple[str, str], dict]:
    rows = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("kind") == "gate_row":
            rows[(row["name"], row["graph6"])] = row
    return rows


def replay_gate(cap: float) -> bool:
    started = time.monotonic()
    controls = PARENT.controls()
    frozen = baseline_rows()
    emit({"kind": "phase_start", "phase": "gate", "controls": len(controls)})
    completed = failures = timeouts = 0
    fields = ("girth", "lambda_max", "target", "tree", "residual")
    for index, (name, raw) in enumerate(controls):
        elapsed = time.monotonic() - started
        if elapsed >= cap:
            timeouts += 1
            break
        graph = nx.convert_node_labels_to_integers(raw, ordering="default")
        graph6 = PARENT.graph6(graph)
        expected = frozen.get((name, graph6))
        data = PARENT.invariants(graph)
        try:
            tree, witness, states = PARENT.exact_largest_induced_tree(
                graph, min(10.0, cap - elapsed))
        except PARENT.SearchTimeout:
            timeouts += 1
            emit({"kind": "gate_timeout", "index": index, "name": name,
                  "graph6": graph6})
            break
        residual = tree - data["target"]
        observed = {**data, "tree": tree, "residual": residual}
        replayed = PARENT.replay_tree(graph, witness, tree)
        matches = expected is not None and all(observed[field] == expected[field]
                                               for field in fields)
        valid = replayed and matches and residual >= 0
        failures += not valid
        completed = index + 1
        emit({"kind": "gate_row", "index": index, "name": name,
              "graph6": graph6, "n": len(graph), "m": graph.number_of_edges(),
              **observed, "tree_witness": witness, "tree_states": states,
              "certificate_valid": replayed, "baseline_match": matches})
        if failures:
            break
    verdict = "PASS" if completed == len(controls) and not failures and not timeouts else "GATE_FAIL"
    emit({"kind": "gate_summary", "verdict": verdict, "completed": completed,
          "controls": len(controls), "failures": failures, "timeouts": timeouts,
          "seconds": round(time.monotonic() - started, 6)})
    return verdict == "PASS"


def triangle_list(graph: nx.Graph) -> list[list[int]]:
    result = []
    for a in sorted(graph):
        for b in sorted(v for v in graph[a] if v > a):
            for c in sorted(v for v in graph[b] if v > b):
                if graph.has_edge(a, c):
                    result.append([a, b, c])
    return result


def seed_and_candidate() -> tuple[nx.Graph, nx.Graph]:
    seed = nx.from_graph6_bytes(b"EhdW")
    candidate = seed.copy()
    candidate.remove_edges_from([(0, 1), (4, 5)])
    candidate.add_edges_from([(0, 5), (1, 4)])
    return seed, candidate


def preexisting_isomorphism(candidate: nx.Graph) -> tuple[dict, dict[int, int]] | None:
    """Identify the candidate with a frozen gate row; do not re-optimize it."""
    for row in baseline_rows().values():
        if row["n"] != len(candidate) or row["m"] != candidate.number_of_edges():
            continue
        control = nx.from_graph6_bytes(row["graph6"].encode("ascii"))
        matcher = nx.algorithms.isomorphism.GraphMatcher(candidate, control)
        if matcher.is_isomorphic():
            return row, dict(sorted(matcher.mapping.items()))
    return None


def evaluate_candidate(cap: float) -> str:
    started = time.monotonic()
    seed, candidate = seed_and_candidate()
    expected_seed_edges = [(0, 1), (0, 4), (1, 2), (1, 5),
                           (2, 3), (3, 4), (3, 5), (4, 5)]
    seed_edges = sorted(tuple(sorted(edge)) for edge in seed.edges())
    candidate_edges = sorted(tuple(sorted(edge)) for edge in candidate.edges())
    construction_valid = (
        seed_edges == expected_seed_edges
        and not candidate.is_multigraph()
        and nx.number_of_selfloops(candidate) == 0
        and len(candidate) == 6
        and candidate.number_of_edges() == 8
        and nx.is_connected(candidate)
        and sorted(dict(seed.degree()).values()) == sorted(dict(candidate.degree()).values())
        and set(seed_edges) - set(candidate_edges) == {(0, 1), (4, 5)}
        and set(candidate_edges) - set(seed_edges) == {(0, 5), (1, 4)}
    )
    seed_data = PARENT.invariants(seed)
    data = PARENT.invariants(candidate)
    triangles_seed = triangle_list(seed)
    triangles_candidate = triangle_list(candidate)
    emit({"kind": "candidate_construction", "construction_valid": construction_valid,
          "seed_graph6": PARENT.graph6(seed), "candidate_graph6": PARENT.graph6(candidate),
          "seed_edges": seed_edges, "candidate_edges": candidate_edges,
          "seed_degree_multiset": sorted(dict(seed.degree()).values()),
          "candidate_degree_multiset": sorted(dict(candidate.degree()).values()),
          "seed_triangles": triangles_seed, "candidate_triangles": triangles_candidate,
          "seed_invariants": seed_data, "candidate_invariants": data})
    if not construction_valid or triangles_seed != [[3, 4, 5]] or triangles_candidate:
        emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
              "reason": "construction_or_triangle_certificate"})
        return "GATE_FAIL"

    alias = preexisting_isomorphism(candidate)
    if alias is None:
        emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
              "reason": "missing_preexisting_isomorphism"})
        return "GATE_FAIL"
    alias_row, candidate_to_control = alias
    control_to_candidate = {control: vertex for vertex, control in candidate_to_control.items()}
    transported_tree = [control_to_candidate[v] for v in alias_row["tree_witness"]]
    alias_valid = (
        alias_row["tree"] == 4
        and alias_row["residual"] == 0
        and PARENT.replay_tree(candidate, transported_tree, alias_row["tree"])
    )
    emit({"kind": "preexisting_isomorphism_certificate",
          "control_name": alias_row["name"], "control_graph6": alias_row["graph6"],
          "candidate_to_control": candidate_to_control,
          "transported_tree_witness": transported_tree,
          "exact_tree_from_frozen_gate": alias_row["tree"],
          "exact_residual_from_frozen_gate": alias_row["residual"],
          "certificate_valid": alias_valid})
    if not alias_valid:
        emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
              "reason": "preexisting_isomorphism_certificate"})
        return "GATE_FAIL"

    remaining = max(0.001, min(55.0, cap - (time.monotonic() - started)))
    try:
        witness, states = PARENT.find_target_tree(candidate, data["target"], remaining)
    except PARENT.SearchTimeout:
        emit({"kind": "candidate_timeout", "phase": "target_tree_decision"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return "HOLD_WITH_TIMEOUTS"
    if witness is not None:
        valid = PARENT.replay_tree(candidate, witness, data["target"])
        emit({"kind": "target_tree_decision", "found": True,
              "target": data["target"], "witness": witness,
              "states": states, "certificate_valid": valid})
        if not valid:
            emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
                  "reason": "target_witness_replay"})
            return "GATE_FAIL"
        prediction = {"girth": 4, "lambda_max": 3, "tree_lower_bound": 4,
                      "target": 4, "residual_lower_bound": 0}
        observed = {"girth": data["girth"], "lambda_max": data["lambda_max"],
                    "tree_lower_bound": len(witness), "target": data["target"],
                    "residual_lower_bound": len(witness) - data["target"]}
        emit({"kind": "prediction_replay", "prediction": prediction,
              "observed": observed, "matches": prediction == observed})
        emit({"kind": "trial_summary", "verdict": "HOLD_BOUNDED",
              "candidate_graph6": PARENT.graph6(candidate),
              "residual_lower_bound": len(witness) - data["target"]})
        emit({"kind": "final_classification", "classification": "HOLD_BOUNDED",
              "candidate_graph6": PARENT.graph6(candidate),
              "database_sanity": "PASS", "timeouts": 0,
              "exact_tuple": {"girth": data["girth"],
                              "lambda_max": data["lambda_max"],
                              "tree": alias_row["tree"], "target": data["target"],
                              "residual": alias_row["residual"]},
              "exact_tree_source": f"explicit isomorphism to frozen gate control {alias_row['name']}",
              "prediction_matched": prediction == observed,
              "novelty_gate": "NOT_TRIGGERED_NO_CROSSING", "public_action": False})
        return "HOLD_BOUNDED"

    remaining = max(0.001, min(55.0, cap - (time.monotonic() - started)))
    try:
        tree, maximum_witness, maximum_states = PARENT.exact_largest_induced_tree(
            candidate, remaining)
    except PARENT.SearchTimeout:
        emit({"kind": "candidate_timeout", "phase": "exact_tree_fallback"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return "HOLD_WITH_TIMEOUTS"
    residual = tree - data["target"]
    emit({"kind": "exact_tree_fallback", "tree": tree,
          "witness": maximum_witness, "states": maximum_states,
          "residual": residual,
          "certificate_valid": PARENT.replay_tree(candidate, maximum_witness, tree)})
    verdict = "CROSSING_VERIFIED" if residual < 0 else "HOLD_BOUNDED"
    emit({"kind": "trial_summary", "verdict": verdict,
          "candidate_graph6": PARENT.graph6(candidate), "residual": residual})
    return verdict


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "candidate", "all"), default="all")
    args = parser.parse_args()
    check_contract()
    signal.alarm(60)
    if args.phase in ("gate", "all") and not replay_gate(55.0):
        return
    if args.phase == "candidate" or args.phase == "all":
        evaluate_candidate(55.0)


if __name__ == "__main__":
    main()
