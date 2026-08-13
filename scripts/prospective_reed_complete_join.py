#!/usr/bin/env python3
"""Frozen prospective complete-join trial for finite Reed conjecture."""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_reed_complete_join_ledger.jsonl"


class SolveTimeout(RuntimeError):
    pass


def append(row: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def graph6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph), header=False).decode().strip()


def c5_clique_blowup(m: int) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(5 * m))
    for u, v in itertools.combinations(graph, 2):
        bu, bv = u // m, v // m
        if bu == bv or (bu - bv) % 5 in (1, 4):
            graph.add_edge(u, v)
    return graph


def complete_join(left: nx.Graph, t: int) -> nx.Graph:
    graph = nx.convert_node_labels_to_integers(left)
    old = list(graph)
    new = list(range(len(old), len(old) + t))
    graph.add_nodes_from(new)
    graph.add_edges_from(itertools.combinations(new, 2))
    graph.add_edges_from(itertools.product(old, new))
    return graph


def carrier_coloring(m: int) -> dict[int, int]:
    """Optimal coloring of C5[K_m] by matching nonadjacent blob vertices."""
    remaining = {blob: list(range(blob * m, (blob + 1) * m)) for blob in range(5)}
    coloring: dict[int, int] = {}
    color = 0
    for _ in range(m // 2):
        for blob in range(5):
            other = (blob + 2) % 5
            for vertex in (remaining[blob].pop(), remaining[other].pop()):
                coloring[vertex] = color
            color += 1
    if m % 2:
        for left, right in ((0, 2), (1, 3)):
            coloring[remaining[left].pop()] = color
            coloring[remaining[right].pop()] = color
            color += 1
        coloring[remaining[4].pop()] = color
    assert all(not vertices for vertices in remaining.values())
    return coloring


def joined_carrier_coloring(m: int, t: int) -> dict[int, int]:
    coloring = carrier_coloring(m)
    next_color = max(coloring.values(), default=-1) + 1
    for offset in range(t):
        coloring[5 * m + offset] = next_color + offset
    return coloring


def clique_number(graph: nx.Graph) -> tuple[int, list[int]]:
    if not graph:
        return 0, []
    clique = max(nx.find_cliques(graph), key=len)
    return len(clique), sorted(clique)


def greedy_coloring(graph: nx.Graph) -> dict[int, int]:
    return nx.coloring.greedy_color(graph, strategy="saturation_largest_first")


def k_coloring(graph: nx.Graph, k: int, deadline: float) -> dict[int, int] | None:
    nodes = list(graph)
    if not nodes:
        return {}
    neighbors = {v: set(graph[v]) for v in nodes}
    colors: dict[int, int] = {}
    forbidden = {v: set() for v in nodes}
    calls = 0

    def search() -> bool:
        nonlocal calls
        calls += 1
        if calls & 4095 == 0 and time.monotonic() > deadline:
            raise SolveTimeout
        if len(colors) == len(nodes):
            return True
        uncolored = [v for v in nodes if v not in colors]
        vertex = max(uncolored, key=lambda v: (len(forbidden[v]), len(neighbors[v]), -v))
        used = set(colors.values())
        candidates = [color for color in sorted(used) if color < k and color not in forbidden[vertex]]
        if len(used) < k:
            candidates.append(len(used))
        for color in candidates:
            colors[vertex] = color
            changed = []
            failed = False
            for neighbor in neighbors[vertex]:
                if neighbor not in colors and color not in forbidden[neighbor]:
                    forbidden[neighbor].add(color)
                    changed.append(neighbor)
                    if len(forbidden[neighbor]) == k:
                        failed = True
            if not failed and search():
                return True
            for neighbor in changed:
                forbidden[neighbor].remove(color)
            del colors[vertex]
        return False

    return dict(colors) if search() else None


def exact_chromatic_number(graph: nx.Graph, timeout: float = 55.0) -> tuple[int, dict[int, int], int, int]:
    started = time.monotonic()
    deadline = started + timeout
    clique_lower, _ = clique_number(graph)
    alpha, _ = clique_number(nx.complement(graph))
    cardinality_lower = 0 if not graph else (len(graph) + alpha - 1) // alpha
    lower = max(clique_lower, cardinality_lower)
    greedy = greedy_coloring(graph)
    upper = max(greedy.values(), default=-1) + 1
    for k in range(lower, upper):
        coloring = k_coloring(graph, k, deadline)
        if coloring is not None:
            return k, coloring, lower, upper
    return upper, greedy, lower, upper


def replay_coloring(graph: nx.Graph, coloring: dict[int, int], chi: int) -> None:
    assert set(coloring) == set(graph)
    assert all(0 <= color < chi for color in coloring.values())
    assert all(coloring[u] != coloring[v] for u, v in graph.edges())


def evaluate(graph: nx.Graph, name: str, stage: str, timeout: float = 55.0) -> dict:
    started = time.monotonic()
    chi, coloring, lower, greedy_upper = exact_chromatic_number(graph, timeout)
    replay_coloring(graph, coloring, chi)
    omega, clique = clique_number(graph)
    delta = max((degree for _, degree in graph.degree()), default=0)
    slack = omega + delta + 2 - 2 * chi
    return {
        "event": "graph_evaluated", "stage": stage, "name": name,
        "graph6": graph6(graph), "n": len(graph), "m_edges": graph.number_of_edges(),
        "chi": chi, "omega": omega, "Delta": delta, "slack": slack,
        "clique_lower": lower, "greedy_upper": greedy_upper,
        "clique_witness": clique,
        "color_classes": [sorted(v for v, color in coloring.items() if color == c) for c in range(chi)],
        "seconds": round(time.monotonic() - started, 6),
    }


def evaluate_certified(graph: nx.Graph, name: str, stage: str,
                       coloring: dict[int, int], exact_lower: int) -> dict:
    started = time.monotonic()
    chi = max(coloring.values(), default=-1) + 1
    replay_coloring(graph, coloring, chi)
    assert chi == exact_lower
    omega, clique = clique_number(graph)
    delta = max((degree for _, degree in graph.degree()), default=0)
    return {
        "event": "graph_evaluated", "stage": stage, "name": name,
        "graph6": graph6(graph), "n": len(graph), "m_edges": graph.number_of_edges(),
        "chi": chi, "omega": omega, "Delta": delta,
        "slack": omega + delta + 2 - 2 * chi,
        "chromatic_lower": exact_lower,
        "lower_certificate": "alpha(carrier)=2; joined clique vertices are universal and pairwise adjacent",
        "clique_witness": clique,
        "color_classes": [sorted(v for v, color in coloring.items() if color == c) for c in range(chi)],
        "seconds": round(time.monotonic() - started, 6),
    }


def run_gate() -> None:
    rows = []
    for index, graph in enumerate(nx.graph_atlas_g()):
        row = evaluate(graph, f"atlas:{index}", "gate", timeout=5.0)
        append(row)
        rows.append(row)
    controls = []
    for m in range(1, 7):
        exact_chi = (5 * m + 1) // 2
        row = evaluate_certified(c5_clique_blowup(m), f"C5[K{m}]", "control",
                                 carrier_coloring(m), exact_chi)
        row["expected_slack"] = 0 if m % 2 else 1
        row["prediction_match"] = row["slack"] == row["expected_slack"]
        append(row)
        controls.append(row)
    bad = sum(row["slack"] < 0 for row in rows)
    append({"event": "gate_summary", "atlas_graphs": len(rows), "crossings": bad,
            "minimum_slack": min(row["slack"] for row in rows),
            "control_prediction_failures": sum(not row["prediction_match"] for row in controls)})
    if bad or any(not row["prediction_match"] for row in controls):
        raise SystemExit("GATE_FAIL")


def run_discovery() -> None:
    rows = []
    for m in (1, 3, 5, 7):
        base = c5_clique_blowup(m)
        base_chi = (5 * m + 1) // 2
        base_row = evaluate_certified(base, f"base:C5[K{m}]", "base",
                                      carrier_coloring(m), base_chi)
        append(base_row)
        assert base_row["slack"] == 0
        for t in range(1, 13):
            row = evaluate_certified(complete_join(base, t), f"J({m},{t})", "discovery",
                                     joined_carrier_coloring(m, t), base_chi + t)
            row.update({
                "m_parameter": m, "t_parameter": t,
                "predicted_chi": (5 * m + 1) // 2 + t,
                "predicted_omega": 2 * m + t,
                "predicted_Delta": 5 * m + t - 1,
                "predicted_slack": 2 * m,
            })
            row["prediction_match"] = all((row[key] == row[f"predicted_{key}"])
                                          for key in ("chi", "omega", "Delta", "slack"))
            append(row)
            rows.append(row)
    append({"event": "discovery_summary", "graphs": len(rows),
            "crossings": sum(row["slack"] < 0 for row in rows),
            "prediction_failures": sum(not row["prediction_match"] for row in rows),
            "minimum_slack": min(row["slack"] for row in rows),
            "maximum_seconds": max(row["seconds"] for row in rows)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("gate", "discovery"))
    args = parser.parse_args()
    if args.stage == "gate":
        run_gate()
    else:
        run_discovery()


if __name__ == "__main__":
    main()
