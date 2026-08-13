#!/usr/bin/env python3
"""Frozen one-graph Mycielski trial for current DeepMind Erdős 128."""

import argparse
import itertools
import json
import os
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_erdos128_mycielski_ledger.jsonl"


class SolveTimeout(Exception):
    pass


def alarm_handler(_signum, _frame):
    raise SolveTimeout


def append(record):
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        out.flush()
        os.fsync(out.fileno())


def c5_blowup(m):
    graph = nx.Graph()
    for i in range(5):
        graph.add_nodes_from((i, a) for a in range(m))
    for i in range(5):
        graph.add_edges_from(((i, a), ((i + 1) % 5, b))
                             for a in range(m) for b in range(m))
    return nx.convert_node_labels_to_integers(graph)


def mycielski(graph):
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    result = nx.Graph(graph)
    result.add_nodes_from(range(n, 2 * n + 1))
    for u, v in graph.edges():
        result.add_edge(u, n + v)
        result.add_edge(v, n + u)
    result.add_edges_from((2 * n, n + v) for v in graph)
    return result


def has_triangle(graph):
    return any(value for value in nx.triangles(graph).values())


def exact_minimum(graph):
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    k = n // 2
    adjacency = [0] * n
    for u, v in graph.edges():
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    best = graph.number_of_edges() + 1
    witness = None
    checked = 0
    old = signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(50)
    try:
        for vertices in itertools.combinations(range(n), k):
            mask = sum(1 << v for v in vertices)
            edges = sum(bin(adjacency[v] & mask).count("1") for v in vertices) // 2
            checked += 1
            if edges < best:
                best, witness = edges, list(vertices)
                if best == 0:
                    break
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    return k, best, witness, checked


def record(name, family, graph):
    graph = nx.convert_node_labels_to_integers(graph)
    start = time.monotonic()
    k, minimum, witness, checked = exact_minimum(graph)
    n = len(graph)
    witness_edges = graph.subgraph(witness).number_of_edges()
    assert witness_edges == minimum
    margin = 50 * minimum - n * n
    triangle_free = not has_triangle(graph)
    return {
        "event": "graph_evaluated", "name": name, "family": family,
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "n": n, "m": graph.number_of_edges(), "triangle_free": triangle_free,
        "eligible_size": k, "minimum_induced_edges": minimum,
        "minimizing_set": witness, "witness_edge_count": witness_edges,
        "subsets_checked": checked, "premise_margin": margin,
        "premise_strict": margin > 0,
        "classification": ("CANDIDATE" if triangle_free and margin > 0
                           else "PREMISE_FALSE_STRICT"),
        "seconds": round(time.monotonic() - start, 6),
    }


def controls():
    seen = set()
    for index, graph in enumerate(nx.graph_atlas_g()):
        if 3 <= len(graph) <= 7 and nx.is_connected(graph) and not has_triangle(graph):
            key = nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph),
                                     header=False).decode().strip()
            if key not in seen:
                seen.add(key)
                yield f"atlas_{index}", graph
    named = [("C5", nx.cycle_graph(5)), ("C7", nx.cycle_graph(7)),
             ("petersen", nx.petersen_graph()),
             ("K2_3", nx.complete_bipartite_graph(2, 3)),
             ("K3_3", nx.complete_bipartite_graph(3, 3))]
    for item in named:
        yield item
    for m in range(1, 5):
        yield f"B{m}", c5_blowup(m)


def gate():
    total = 0
    for name, graph in controls():
        row = record(name, "db_sanity", graph)
        append(row)
        total += 1
        if row["premise_strict"]:
            append({"event": "db_sanity_reject", "name": name,
                    "reason": "unexpected triangle-free strict-premise control"})
            print(json.dumps({"classification": "DB_SANITY_REJECT", "name": name}))
            return
        if name == "B2" and row["premise_margin"] != 0:
            append({"event": "db_sanity_reject", "name": name,
                    "reason": "balanced blow-up equality calibration failed"})
            print(json.dumps({"classification": "DB_SANITY_REJECT", "name": name}))
            return
    append({"event": "db_sanity_passed", "controls": total,
            "unexpected_strict_premise": 0, "selected_carrier_equalities": 1})
    print(json.dumps({"classification": "DB_SANITY_PASS", "controls": total}))


def evaluate():
    prior = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    if not any(row.get("event") == "db_sanity_passed" for row in prior):
        raise RuntimeError("complete DB sanity gate required")
    if any(row.get("family") == "mycielski_development" for row in prior):
        print(json.dumps({"classification": "ALREADY_EVALUATED"}))
        return
    base = c5_blowup(2)
    graph = mycielski(base)
    try:
        row = record("mycielski_of_B2", "mycielski_development", graph)
    except SolveTimeout:
        append({"event": "graph_timeout", "name": "mycielski_of_B2",
                "classification": "TIMEOUT_BRACKET"})
        print(json.dumps({"classification": "TIMEOUT_BRACKET"}))
        return
    append(row)
    verdict = "CANDIDATE" if row["classification"] == "CANDIDATE" else "HOLD_BOUNDED"
    append({"event": "trial_final", "verdict": verdict,
            "development_graphs": 1, "candidate": row["classification"] == "CANDIDATE"})
    print(json.dumps({"classification": verdict, "margin": row["premise_margin"],
                      "minimum_edges": row["minimum_induced_edges"]}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("gate", "evaluate"))
    args = parser.parse_args()
    if not LEDGER.exists():
        append({"event": "contract_frozen", "date": "2026-08-13",
                "target": "FormalConjectures/ErdosProblems/128.lean",
                "upstream_commit": "9a1636c4030039f70cf78b866c216d8b6c5f35b0",
                "transformation": "single Mycielski lift of B2",
                "development_graph_cap": 1, "evaluated_before_freeze": False,
                "public_action": False})
    if args.phase == "gate":
        gate()
    else:
        evaluate()


if __name__ == "__main__":
    main()
