#!/usr/bin/env python3
"""Frozen WOWII 305 database gate and partial-join complement trial.

The coordinator never constructs a prospective G(s,d) until every database
row has been computed and independently replayed.  Each graph is evaluated in
a fresh process with a 55-second internal alarm and a 60-second external cap.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/method_v05_305_trial.jsonl"
VERIFY_LEDGER = ROOT / "results/expansion/method_v05_305_trial.verify.jsonl"
INTERNAL_CAP = 55
SELECTION_COMMIT = "925d56dea3aaa6246560f42890e1d6fc6ee5c3a8"


class InternalTimeout(RuntimeError):
    pass


def alarm_handler(_signum, _frame):
    raise InternalTimeout("worker exceeded the internal 55-second deadline")


def graph6(graph: nx.Graph) -> str:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(graph, header=False).decode().strip()


def from_graph6(value: str) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.from_graph6_bytes(value.encode()), ordering="sorted")


def clique_cycle_blowup(weights: tuple[int, ...]) -> nx.Graph:
    graph = nx.Graph()
    bags: list[list[int]] = []
    cursor = 0
    for weight in weights:
        bag = list(range(cursor, cursor + weight))
        cursor += weight
        bags.append(bag)
        graph.add_nodes_from(bag)
        graph.add_edges_from(combinations(bag, 2))
    for i in range(len(weights)):
        graph.add_edges_from((u, v) for u in bags[i] for v in bags[(i + 1) % len(weights)])
    return graph


def endpoint_barbell(length: int) -> nx.Graph:
    graph = nx.path_graph(length + 1)
    cursor = length + 1
    for endpoint in (0, length):
        extra = [cursor, cursor + 1]
        cursor += 2
        graph.add_edges_from(combinations([endpoint, *extra], 2))
    return graph


def triangular_graph(order: int) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.line_graph(nx.complete_graph(order)), ordering="sorted")


def gate_controls() -> list[dict]:
    """The complete frozen gate, including explicit duplicate named rows."""
    rows: list[dict] = []

    def add(name: str, graph: nx.Graph, group: str) -> None:
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        rows.append({"name": name, "group": group, "graph6": graph6(graph)})

    for atlas_index, graph in enumerate(nx.graph_atlas_g()):
        if 3 <= len(graph) <= 7 and nx.is_connected(graph):
            add(f"atlas:{atlas_index}", graph, "connected_graph_atlas_n3_n7")
    for n in range(3, 13):
        add(f"P{n}", nx.path_graph(n), "paths")
        add(f"C{n}", nx.cycle_graph(n), "cycles")
    for r in range(2, 11):
        add(f"K1,{r}", nx.star_graph(r), "stars")
    for a in range(1, 7):
        for b in range(a, 7):
            add(f"K{a},{b}", nx.complete_bipartite_graph(a, b), "complete_bipartite")
    for n in range(3, 11):
        add(f"K{n}", nx.complete_graph(n), "complete_explicit_not_applicable")
    add("Petersen", nx.petersen_graph(), "named_required")
    add("K3,3", nx.complete_bipartite_graph(3, 3), "named_required")
    add("K7", nx.complete_graph(7), "named_required")
    add("T(7)", triangular_graph(7), "named_required")
    add("carrier:C5[K4]", clique_cycle_blowup((4,) * 5), "named_required")
    for size in range(1, 9):
        add(f"C5[K{size}]", clique_cycle_blowup((size,) * 5), "calibration_family")
    for length in (6, 8, 10):
        add(f"D_{length}", endpoint_barbell(length), "existing_project_control")
    project_weights = (
        (2, 2, 2, 2, 2), (3, 3, 3, 3, 3), (4, 4, 4, 4, 4),
        (5, 5, 5, 5, 5), (6, 6, 6, 6, 6), (8, 8, 8, 8, 8),
        (4, 4, 3, 4, 3), (4, 2, 4, 2, 4), (4, 1, 4, 1, 4),
        (3, 1, 3, 1, 3), (5, 5, 4, 5, 4),
    )
    for weights in project_weights:
        add(f"project:B{weights}", clique_cycle_blowup(weights), "existing_project_control")
    return rows


def partial_join_complement(s: int, d: int) -> nx.Graph:
    """Construct G(s,d)=complement(H(s,d)) exactly as preregistered."""
    if not (2 <= s <= 8 and 1 <= d < s):
        raise ValueError("outside frozen grid")
    auxiliary = nx.Graph()
    auxiliary.add_nodes_from(range(5 * s))
    for i in range(5):
        for a in range(s):
            for offset in range(d):
                b = (a + offset) % s
                auxiliary.add_edge(i * s + a, ((i + 1) % 5) * s + b)
    return nx.complement(auxiliary)


def grid_rows() -> list[dict]:
    """Generate all 28 labels, then deduplicate isomorphically with aliases."""
    representatives: list[dict] = []
    rep_graphs: list[nx.Graph] = []
    for s in range(2, 9):
        for d in range(1, s):
            graph = partial_join_complement(s, d)
            alias = [s, d]
            match = next((i for i, other in enumerate(rep_graphs)
                          if len(other) == len(graph)
                          and other.number_of_edges() == graph.number_of_edges()
                          and nx.is_isomorphic(other, graph)), None)
            if match is not None:
                representatives[match]["aliases"].append(alias)
                continue
            rep_graphs.append(graph)
            representatives.append({
                "name": f"G({s},{d})", "s": s, "d": d,
                "aliases": [alias], "graph6": graph6(graph),
            })
    assert sum(len(row["aliases"]) for row in representatives) == 28
    return representatives


def is_total_dominating(neighborhood_masks: list[int], chosen_mask: int) -> bool:
    return all(neighbors & chosen_mask for neighbors in neighborhood_masks)


def total_domination_bitset(graph: nx.Graph, deadline: float) -> tuple[int, list[int]]:
    nodes = list(graph)
    neighborhood_masks = [sum(1 << u for u in graph[v]) for v in nodes]
    for size in range(1, len(nodes) + 1):
        for ordinal, chosen in enumerate(combinations(nodes, size)):
            if ordinal % 4096 == 0 and time.monotonic() >= deadline:
                raise InternalTimeout("bitset total-domination enumeration reached deadline")
            mask = sum(1 << v for v in chosen)
            if is_total_dominating(neighborhood_masks, mask):
                return size, list(chosen)
    raise AssertionError("connected nontrivial graph has no total dominating set")


def complement_edge_data_bitset(graph: nx.Graph) -> tuple[list[int], list[list[int]], list[list[int]]]:
    n = len(graph)
    all_mask = (1 << n) - 1
    graph_masks = [sum(1 << u for u in graph[v]) for v in graph]
    complement_masks = [all_mask ^ (1 << v) ^ graph_masks[v] for v in graph]
    values: list[tuple[tuple[int, int], int]] = []
    for u in range(n):
        remaining = complement_masks[u] & ~((1 << (u + 1)) - 1)
        while remaining:
            bit = remaining & -remaining
            v = bit.bit_length() - 1
            values.append(((u, v), bin(complement_masks[u] | complement_masks[v]).count("1")))
            remaining ^= bit
    multiset = sorted(value for _, value in values)
    if not multiset:
        return [], [], []
    minimum, maximum = multiset[0], multiset[-1]
    minimizing = [list(edge) for edge, value in values if value == minimum]
    maximizing = [list(edge) for edge, value in values if value == maximum]
    return multiset, minimizing, maximizing


def evaluate(item: dict, stage: str, index: int) -> dict:
    graph = from_graph6(item["graph6"])
    if len(graph) <= 2:
        return dict(item, stage=stage, index=index, status="NOT_APPLICABLE_HYPOTHESES",
                    n=len(graph), m_edges=graph.number_of_edges(), gamma_t=None,
                    total_dominating_set=None, complement_edge_neighborhood_multiset=None,
                    minimizing_complement_edges=None, maximizing_complement_edges=None,
                    m_complement_edge_neighborhood=None, M_complement_edge_neighborhood=None,
                    T306=None, R305=None, crossing=None,
                    reason="WOWII 305 requires n(G)>2")
    if not nx.is_connected(graph):
        raise AssertionError("source hypotheses require a connected graph")
    started = time.monotonic()
    deadline = started + INTERNAL_CAP - 0.5
    gamma_t, witness = total_domination_bitset(graph, deadline)
    multiset, minimizing, maximizing = complement_edge_data_bitset(graph)
    row = dict(item)
    row.update({
        "stage": stage, "index": index, "status": "OK", "n": len(graph),
        "m_edges": graph.number_of_edges(), "gamma_t": gamma_t,
        "total_dominating_set": witness,
        "total_domination_witness_replay": is_total_dominating(
            [sum(1 << u for u in graph[v]) for v in graph], sum(1 << v for v in witness)),
        "method": "bitset exact subset enumeration + direct complement bit unions",
        "elapsed_seconds": round(time.monotonic() - started, 6),
    })
    if not multiset:
        row.update({
            "status": "NOT_APPLICABLE_EDGE_DOMAIN",
            "complement_edge_neighborhood_multiset": [],
            "minimizing_complement_edges": [], "maximizing_complement_edges": [],
            "m_complement_edge_neighborhood": None, "M_complement_edge_neighborhood": None,
            "T306": None, "R305": None, "crossing": None,
        })
        return row
    small, large = multiset[0], multiset[-1]
    t306 = 2 * (small // 2) - gamma_t
    r305 = (2 * large + 2) // 3 - gamma_t
    row.update({
        "complement_edge_neighborhood_multiset": multiset,
        "minimizing_complement_edges": minimizing,
        "maximizing_complement_edges": maximizing,
        "m_complement_edge_neighborhood": small,
        "M_complement_edge_neighborhood": large,
        "T306": t306, "R305": r305, "crossing": r305 < 0,
        "obstruction_identity_rhs": t306 + (2 * large + 2) // 3 - 2 * (small // 2),
    })
    if not row["total_domination_witness_replay"]:
        row["gate_failure"] = "failed total-domination witness replay"
    elif t306 < 0:
        row["gate_failure"] = "negative proved WOWII 306 baseline"
    elif row["obstruction_identity_rhs"] != r305:
        row["gate_failure"] = "obstruction identity mismatch"
    elif stage == "gate" and r305 < 0:
        row["gate_failure"] = "unexpected source-statement crossing"
    elif stage == "gate" and item.get("name") == "C5[K2]" and (gamma_t, large, r305) != (3, 6, 1):
        row["gate_failure"] = (
            f"frozen calibration mismatch: observed (gamma_t,M,R305)={(gamma_t, large, r305)}, "
            "required (3,6,1)"
        )
    return row


def append(row: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def worker(stage: str, index: int) -> None:
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(INTERNAL_CAP)
    item = (gate_controls() if stage == "gate" else grid_rows())[index]
    try:
        row = evaluate(item, stage, index)
    except InternalTimeout as error:
        row = dict(item, stage=stage, index=index, status="TIMEOUT_BRACKET", error=str(error))
    except Exception as error:
        row = dict(item, stage=stage, index=index, status="ERROR",
                   error=f"{type(error).__name__}: {error}")
    finally:
        signal.alarm(0)
    print(json.dumps(row, sort_keys=True, separators=(",", ":")), flush=True)


def completed(stage: str) -> dict[int, dict]:
    if not LEDGER.exists():
        return {}
    rows: dict[int, dict] = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if (row.get("stage") == stage and isinstance(row.get("index"), int)
                and row.get("status") in {"OK", "NOT_APPLICABLE_EDGE_DOMAIN",
                                          "NOT_APPLICABLE_HYPOTHESES"}):
            rows[row["index"]] = row
    return rows


def invoke(stage: str, index: int) -> dict:
    command = ["timeout", "--signal=TERM", "--kill-after=5s", "60s", sys.executable,
               str(Path(__file__).resolve()), "worker", stage, str(index)]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=65)
    except subprocess.TimeoutExpired:
        return {"stage": stage, "index": index, "status": "TIMEOUT_BRACKET",
                "error": "external Python supervisor exceeded 65 seconds"}
    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout.strip().splitlines()[-1])
    return {"stage": stage, "index": index,
            "status": "TIMEOUT_BRACKET" if result.returncode in (124, 137) else "ERROR",
            "error": f"external worker exit={result.returncode}: {result.stderr.strip()}"}


def gate_is_independently_verified() -> bool:
    gate = completed("gate")
    expected = len(gate_controls())
    allowed = {"OK", "NOT_APPLICABLE_EDGE_DOMAIN", "NOT_APPLICABLE_HYPOTHESES"}
    if len(gate) != expected or any(row.get("status") not in allowed or row.get("gate_failure")
                                    for row in gate.values()):
        return False
    calibration = next((row for row in gate.values() if row.get("name") == "C5[K2]"), None)
    if calibration is None or (calibration.get("gamma_t"),
                               calibration.get("M_complement_edge_neighborhood"),
                               calibration.get("R305")) != (3, 6, 1):
        return False
    if not VERIFY_LEDGER.exists():
        return False
    verified: dict[int, dict] = {}
    for line in VERIFY_LEDGER.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("stage") == "gate_verify" and isinstance(row.get("index"), int):
            verified[row["index"]] = row
    return len(verified) == expected and all(row.get("status") == "PASS" for row in verified.values())


def run_stage(stage: str) -> None:
    if stage == "grid" and not gate_is_independently_verified():
        raise SystemExit("gate and independent replay are incomplete; frozen grid remains unconstructed")
    items = gate_controls() if stage == "gate" else grid_rows()
    done = completed(stage)
    if not LEDGER.exists():
        append({"stage": "trial_start", "target": "WOWII 305", "selection_commit": SELECTION_COMMIT,
                "internal_cap_seconds": 55, "external_cap_seconds": 60,
                "prospective_rows_constructed": False})
    for index in range(len(items)):
        if index in done:
            continue
        row = invoke(stage, index)
        append(row)
        failure = row.get("status") not in {"OK", "NOT_APPLICABLE_EDGE_DOMAIN",
                                            "NOT_APPLICABLE_HYPOTHESES"} or row.get("gate_failure")
        if failure or row.get("crossing"):
            append({"stage": f"{stage}_stop", "index": index,
                    "reason": "crossing_pending_independent_replay" if row.get("crossing")
                    else "disagreement_failure_or_timeout"})
            return
    if stage == "gate":
        rows = completed("gate")
        calibration = next((row for row in rows.values() if row.get("name") == "C5[K2]"), None)
        if calibration is None or (calibration.get("gamma_t"),
                                   calibration.get("M_complement_edge_neighborhood"),
                                   calibration.get("R305")) != (3, 6, 1):
            append({"stage": "gate_stop", "reason": "frozen_calibration_disagreement",
                    "observed": None if calibration is None else {
                        "gamma_t": calibration.get("gamma_t"),
                        "M": calibration.get("M_complement_edge_neighborhood"),
                        "R305": calibration.get("R305")}})
            return
    append({"stage": f"{stage}_complete", "rows": len(items),
            "labelled_aliases": 28 if stage == "grid" else None})


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    worker_parser = sub.add_parser("worker")
    worker_parser.add_argument("stage", choices=("gate", "grid"))
    worker_parser.add_argument("index", type=int)
    sub.add_parser("run-gate")
    sub.add_parser("run-grid")
    sub.add_parser("counts")
    args = parser.parse_args()
    if args.command == "worker":
        worker(args.stage, args.index)
    elif args.command == "run-gate":
        run_stage("gate")
    elif args.command == "run-grid":
        run_stage("grid")
    else:
        print(json.dumps({"gate": len(gate_controls()), "grid_representatives": "LOCKED",
                          "grid_labelled_rows": 28}, sort_keys=True))


if __name__ == "__main__":
    main()
