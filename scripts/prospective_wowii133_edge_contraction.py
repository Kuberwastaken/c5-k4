#!/usr/bin/env python3
"""Frozen decision-first Heawood edge-contraction trial for WOWII #133."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_wowii133_edge_contraction_contract.md"
LEDGER = ROOT / "results/expansion/prospective_wowii133_edge_contraction_ledger.jsonl"
CONTRACT_SHA256 = "d927753cee849e43e91551250a4f8bbba80c49a55f68c92941743119b6a749a9"


def load_decision_module():
    path = ROOT / "scripts/prospective_wowii133_decision_first.py"
    spec = importlib.util.spec_from_file_location("wowii133_decision", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def check_contract() -> None:
    actual = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if actual != CONTRACT_SHA256:
        raise RuntimeError(f"frozen contract changed: {actual}")


def emit(row: dict[str, object]) -> None:
    record = {"contract_sha256": CONTRACT_SHA256, **row}
    line = json.dumps(record, sort_keys=True, separators=(",", ":"))
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(line + "\n")
        out.flush()
    print(line, flush=True)


def graph6(graph: nx.Graph) -> str:
    dense = nx.convert_node_labels_to_integers(graph, ordering="default")
    return nx.to_graph6_bytes(dense, header=False).decode().strip()


def projective_plane_levi_2() -> nx.Graph:
    vectors = [raw for raw in itertools.product(range(2), repeat=3)
               if raw != (0, 0, 0)]
    graph = nx.Graph()
    graph.add_nodes_from(("P", point) for point in vectors)
    graph.add_nodes_from(("L", line) for line in vectors)
    for point in vectors:
        for line in vectors:
            if sum(a * b for a, b in zip(point, line)) % 2 == 0:
                graph.add_edge(("P", point), ("L", line))
    return nx.convert_node_labels_to_integers(graph, ordering="default")


def contract_edge(graph: nx.Graph, edge: tuple[int, int]) -> nx.Graph:
    u, v = edge
    contracted = nx.contracted_nodes(graph, u, v, self_loops=False, copy=True)
    return nx.convert_node_labels_to_integers(nx.Graph(contracted), ordering="default")


def latest_gate_passed() -> bool:
    if not LEDGER.exists():
        return False
    for line in reversed(LEDGER.read_text(encoding="utf-8").splitlines()):
        row = json.loads(line)
        if row.get("event") == "db_sanity_summary":
            return row.get("verdict") == "PASS"
    return False


def run_gate(decision) -> None:
    started = time.monotonic()
    controls = decision.CORE.controls()
    failures = timeouts = 0
    emit({"event": "db_sanity_started", "controls": len(controls)})
    completed = 0
    for index, (name, graph) in enumerate(controls):
        if time.monotonic() - started >= 55.0:
            timeouts += 1
            break
        row = decision.evaluate(
            graph, name, "edge_contraction_gate", decision_cap=2.0, exact_cap=5.0)
        exact = decision.CORE.evaluate(
            graph, name, "edge_contraction_gate_exact", timeout=5.0)
        decision_holds = row["kind"] == "hold_witness"
        exact_holds = exact["kind"] == "graph" and exact["residual"] >= 0
        agrees = decision_holds and exact_holds
        timed_out = row["kind"].endswith("timeout") or exact["kind"] == "solve_timeout"
        failures += not agrees and not timed_out
        timeouts += timed_out
        completed = index + 1
        emit({
            "event": "db_sanity_row", "index": index, "name": name,
            "decision_kind": row["kind"], "decision_target": row.get("target"),
            "decision_witness": row.get("decision_witness"),
            "exact_kind": exact["kind"], "exact_path": exact.get("path"),
            "exact_residual": exact.get("residual"), "agrees": agrees,
        })
        if failures or timeouts:
            break
    verdict = "PASS" if completed == len(controls) and not failures and not timeouts else "FAIL"
    emit({
        "event": "db_sanity_summary", "verdict": verdict,
        "controls": len(controls), "completed": completed,
        "failures": failures, "timeouts": timeouts,
        "seconds": round(time.monotonic() - started, 6),
    })
    print(json.dumps({"verdict": verdict, "controls": completed}))


def run_trial(decision) -> None:
    if not latest_gate_passed():
        raise RuntimeError("DB sanity must pass before candidate evaluation")
    started = time.monotonic()
    inputs = [
        ("networkx_heawood", nx.heawood_graph()),
        ("pg_2_2_levi", projective_plane_levi_2()),
    ]
    profiles = []
    for name, graph in inputs:
        exact = decision.CORE.evaluate(graph, name, "input_profile", timeout=10.0)
        coordinates = {
            "kind": exact.get("kind"), "n": exact.get("n"), "m": exact.get("m"),
            "has_c4": exact.get("has_c4"), "path": exact.get("path"),
            "radius": exact.get("radius"), "floor_l": exact.get("floor_l"),
            "avg_l": exact.get("avg_l"), "residual": exact.get("residual"),
            "graph6": exact.get("graph6"), "path_witness": exact.get("path_witness"),
        }
        expected = ("graph", 14, 21, False, 7, 3, 3, "3", 1)
        actual = tuple(coordinates[key] for key in
                       ("kind", "n", "m", "has_c4", "path", "radius",
                        "floor_l", "avg_l", "residual"))
        if actual != expected:
            emit({"event": "input_profile_reject", "name": name,
                  "expected": expected, "actual": actual})
            raise RuntimeError(f"input profile mismatch for {name}: {actual}")
        profiles.append({"name": name, **coordinates})
    emit({"event": "input_profiles_verified", "profiles": profiles,
          "inputs_isomorphic": nx.is_isomorphic(inputs[0][1], inputs[1][1])})

    raw = []
    for source, graph in inputs:
        graph = nx.convert_node_labels_to_integers(graph, ordering="default")
        for edge in sorted(tuple(sorted(pair)) for pair in graph.edges()):
            candidate = contract_edge(graph, edge)
            raw.append((source, edge, candidate))
    if len(raw) != 42:
        raise AssertionError(("raw contraction count", len(raw)))

    buckets: dict[tuple[int, int, str], list[int]] = {}
    distinct: list[dict[str, object]] = []
    for source, edge, graph in raw:
        key = (len(graph), graph.number_of_edges(), nx.weisfeiler_lehman_graph_hash(graph))
        duplicate = None
        for index in buckets.setdefault(key, []):
            if nx.is_isomorphic(graph, distinct[index]["graph"]):
                duplicate = index
                break
        origin = {"source": source, "edge": edge}
        if duplicate is not None:
            distinct[duplicate]["origins"].append(origin)
            continue
        index = len(distinct)
        buckets[key].append(index)
        distinct.append({"graph": graph, "origins": [origin]})
    if len(distinct) > 42:
        raise AssertionError("frozen distinct cap exceeded")

    rows = []
    for index, item in enumerate(distinct):
        graph = item["graph"]
        c4 = decision.c4_witness(graph)
        if not nx.is_connected(graph) or c4 is not None:
            emit({"event": "candidate_rejected", "index": index,
                  "connected": nx.is_connected(graph), "c4_witness": c4,
                  "origins": item["origins"], "graph6": graph6(graph)})
            continue
        row = decision.evaluate(
            graph, f"heawood_edge_contraction_{index}", "edge_contraction",
            decision_cap=55.0, exact_cap=55.0)
        row.update({"event": "candidate_evaluated", "index": index,
                    "origins": item["origins"]})
        emit(row)
        rows.append(row)

    crossings = [row for row in rows if row["kind"] == "exact_crossing"]
    timeouts = [row for row in rows if row["kind"].endswith("timeout")]
    holds = [row for row in rows if row["kind"] == "hold_witness"]
    verdict = ("CANDIDATE" if crossings else
               "INCONCLUSIVE" if timeouts else "HOLD_BOUNDED")
    emit({
        "event": "edge_contraction_trial_complete", "verdict": verdict,
        "raw_contractions": len(raw), "distinct_candidates": len(distinct),
        "evaluated": len(rows), "hold_witnesses": len(holds),
        "crossings": len(crossings), "timeouts": len(timeouts),
        "exact_candidate_maximizations": sum(
            row["kind"] in ("exact_graph", "exact_crossing") for row in rows),
        "seconds": round(time.monotonic() - started, 6),
    })
    print(json.dumps({"verdict": verdict, "distinct": len(distinct),
                      "crossings": len(crossings), "timeouts": len(timeouts)}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("gate", "trial"))
    args = parser.parse_args()
    signal.alarm(60)
    check_contract()
    decision = load_decision_module()
    if args.phase == "gate":
        run_gate(decision)
    else:
        run_trial(decision)


if __name__ == "__main__":
    main()
