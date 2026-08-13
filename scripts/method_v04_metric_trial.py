#!/usr/bin/env python3
"""Exact bounded WOWII 184/185 Method v0.4 trial.

The commands are deliberately shardable so every invoking process can receive
an external 60-second wall-clock cap. JSON records are flushed one at a time.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations
import json
import signal
import time

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


SOLVE_CAP = 55.0  # outer process is capped at 60 s
OUTPUT_PATH: str | None = None


class SolveTimeout(RuntimeError):
    pass


class alarm:
    def __init__(self, seconds: int = 55):
        self.seconds = seconds
        self.old = None

    def __enter__(self):
        def handler(_signum, _frame):
            raise SolveTimeout(f"exact solve exceeded {self.seconds}s")
        self.old = signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc, tb):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.old)


def emit(row: dict) -> None:
    line = json.dumps(row, sort_keys=True)
    if OUTPUT_PATH is None:
        print(line, flush=True)
    else:
        with open(OUTPUT_PATH, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def frac(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def graph6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(graph, header=False).decode().strip()


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
        graph.add_nodes_from(extra)
        graph.add_edges_from(combinations([endpoint, *extra], 2))
    return graph


def triangular_graph(order: int) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.line_graph(nx.complete_graph(order)), ordering="sorted")


def rooted_comet(m: int, length: int) -> nx.Graph:
    graph = clique_cycle_blowup((m,) * 5)
    root = 0
    previous = root
    for vertex in range(5 * m, 5 * m + length):
        graph.add_edge(previous, vertex)
        previous = vertex
    return graph


def brute_bipartite_number(graph: nx.Graph) -> tuple[int, list[int], float]:
    nodes = list(graph)
    start = time.monotonic()
    with alarm():
        for removed_size in range(len(nodes) + 1):
            for removed in combinations(nodes, removed_size):
                selected = sorted(set(nodes) - set(removed))
                if nx.is_bipartite(graph.subgraph(selected)):
                    return len(selected), selected, time.monotonic() - start
    raise AssertionError("empty induced subgraph must be bipartite")


def brute_connected_domination(graph: nx.Graph) -> tuple[int, list[int], float]:
    nodes = list(graph)
    all_nodes = set(nodes)
    start = time.monotonic()
    with alarm():
        for size in range(1, len(nodes) + 1):
            for chosen_tuple in combinations(nodes, size):
                chosen = set(chosen_tuple)
                if size > 1 and not nx.is_connected(graph.subgraph(chosen)):
                    continue
                dominated = chosen | set().union(*(set(graph[v]) for v in chosen))
                if dominated == all_nodes:
                    return size, sorted(chosen), time.monotonic() - start
    raise AssertionError("connected graph must have a connected dominating set")


def mip_bipartite_number(graph: nx.Graph) -> tuple[int, list[int], float]:
    n = len(graph)
    edges = list(graph.edges())
    variables = 2 * n
    matrix = lil_matrix((2 * len(edges), variables), dtype=float)
    upper = np.empty(2 * len(edges))
    for i, (u, v) in enumerate(edges):
        matrix[2 * i, u] = matrix[2 * i, v] = 1
        matrix[2 * i, n + u] = matrix[2 * i, n + v] = -1
        upper[2 * i] = 1
        matrix[2 * i + 1, u] = matrix[2 * i + 1, v] = 1
        matrix[2 * i + 1, n + u] = matrix[2 * i + 1, n + v] = 1
        upper[2 * i + 1] = 3
    objective = np.r_[-np.ones(n), np.zeros(n)]
    start = time.monotonic()
    result = milp(
        objective,
        integrality=np.ones(variables),
        bounds=Bounds(np.zeros(variables), np.ones(variables)),
        constraints=LinearConstraint(matrix.tocsr(), -np.inf, upper),
        options={"time_limit": SOLVE_CAP, "mip_rel_gap": 0.0},
    )
    elapsed = time.monotonic() - start
    if result.status != 0 or result.x is None:
        raise SolveTimeout(f"bipartite MILP status={result.status}: {result.message}")
    selected = [v for v in range(n) if result.x[v] > 0.5]
    assert nx.is_bipartite(graph.subgraph(selected))
    value = len(selected)
    assert abs(result.fun + value) < 1e-6
    return value, selected, elapsed


def mip_connected_domination(graph: nx.Graph) -> tuple[int, list[int], float]:
    n = len(graph)
    arcs = [(u, v) for u, v in graph.edges() for u, v in ((u, v), (v, u))]
    # x, root-choice y, source flow s, directed edge flows f
    x0, y0, s0, f0 = 0, n, 2 * n, 3 * n
    variables = f0 + len(arcs)
    rows: list[tuple[dict[int, float], float, float]] = []
    for v in range(n):
        rows.append(({u: 1 for u in set(graph[v]) | {v}}, 1, np.inf))
    rows.append(({y0 + v: 1 for v in range(n)}, 1, 1))
    for v in range(n):
        rows.append(({y0 + v: 1, x0 + v: -1}, -np.inf, 0))
        rows.append(({s0 + v: 1, y0 + v: -n}, -np.inf, 0))
    for i, (u, v) in enumerate(arcs):
        rows.append(({f0 + i: 1, x0 + u: -n}, -np.inf, 0))
        rows.append(({f0 + i: 1, x0 + v: -n}, -np.inf, 0))
    for v in range(n):
        coefficients = {s0 + v: 1, x0 + v: -1}
        for i, (u, w) in enumerate(arcs):
            if w == v:
                coefficients[f0 + i] = coefficients.get(f0 + i, 0) + 1
            if u == v:
                coefficients[f0 + i] = coefficients.get(f0 + i, 0) - 1
        rows.append((coefficients, 0, 0))
    matrix = lil_matrix((len(rows), variables), dtype=float)
    lower = np.empty(len(rows))
    upper = np.empty(len(rows))
    for i, (coefficients, lo, hi) in enumerate(rows):
        for j, value in coefficients.items():
            matrix[i, j] = value
        lower[i], upper[i] = lo, hi
    objective = np.zeros(variables)
    objective[:n] = 1
    lb = np.zeros(variables)
    ub = np.full(variables, n, dtype=float)
    ub[:2 * n] = 1
    integrality = np.zeros(variables)
    integrality[:2 * n] = 1
    start = time.monotonic()
    result = milp(
        objective,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"time_limit": SOLVE_CAP, "mip_rel_gap": 0.0},
    )
    elapsed = time.monotonic() - start
    if result.status != 0 or result.x is None:
        raise SolveTimeout(f"connected-domination MILP status={result.status}: {result.message}")
    selected = [v for v in range(n) if result.x[v] > 0.5]
    assert nx.is_connected(graph.subgraph(selected)) or len(selected) == 1
    assert set(selected) | set().union(*(set(graph[v]) for v in selected)) == set(graph)
    value = len(selected)
    assert abs(result.fun - value) < 1e-6
    return value, selected, elapsed


def exact_bipartite_number(graph: nx.Graph) -> tuple[int, list[int], float, str]:
    if len(graph) <= 14:
        value, witness, elapsed = brute_bipartite_number(graph)
        return value, witness, elapsed, "subset"
    value, witness, elapsed = mip_bipartite_number(graph)
    return value, witness, elapsed, "milp"


def exact_connected_domination(graph: nx.Graph) -> tuple[int, list[int], float, str]:
    if len(graph) <= 14:
        value, witness, elapsed = brute_connected_domination(graph)
        return value, witness, elapsed, "subset"
    value, witness, elapsed = mip_connected_domination(graph)
    return value, witness, elapsed, "milp"


def graph_square(graph: nx.Graph) -> nx.Graph:
    square = nx.Graph()
    square.add_nodes_from(graph)
    distances = dict(nx.all_pairs_shortest_path_length(graph, cutoff=2))
    square.add_edges_from((u, v) for u, v in combinations(graph, 2) if distances[u].get(v, 3) <= 2)
    return square


def metric_profile(graph: nx.Graph) -> tuple[nx.Graph, list[int], Fraction, Fraction]:
    square = graph_square(graph)
    distances = dict(nx.all_pairs_shortest_path_length(square))
    eccentricities = {u: max(row.values()) for u, row in distances.items()}
    maximum = max(eccentricities.values())
    boundary = sorted(u for u, value in eccentricities.items() if value == maximum)
    n = len(square)
    total_boundary = sum(distances[u][v] for u in boundary for v in square if v != u)
    total_all = sum(distances[u][v] for u in square for v in square if v != u)
    return square, boundary, Fraction(total_boundary, len(boundary) * (n - 1)), Fraction(total_all, n * (n - 1))


def evaluate(graph: nx.Graph, name: str, stage: str) -> dict:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    if len(graph) < 2 or not nx.is_connected(graph):
        raise ValueError("trial graphs must be connected and nontrivial")
    b, b_witness, b_seconds, b_solver = exact_bipartite_number(graph)
    gamma_c, gc_witness, gc_seconds, gc_solver = exact_connected_domination(graph)
    n = len(graph)
    leaves = 2 if n == 2 else n - gamma_c
    square, boundary, d_boundary, d_all = metric_profile(graph)
    delta_square = max(dict(square.degree()).values())
    q = n - 1 - delta_square
    theorem_slack = leaves + b - (n + 1)
    r184 = Fraction(leaves + b - delta_square) - 2 * d_boundary
    r185 = Fraction(leaves + b - delta_square) - 2 * d_all
    assert r184 == theorem_slack + q + 2 - 2 * d_boundary
    assert r185 == theorem_slack + q + 2 - 2 * d_all
    assert theorem_slack >= 0
    return {
        "stage": stage,
        "name": name,
        "graph6": graph6(graph),
        "n": n,
        "m_edges": graph.number_of_edges(),
        "square_edges": square.number_of_edges(),
        "square_delta": delta_square,
        "q": q,
        "square_periphery": boundary,
        "d_boundary": frac(d_boundary),
        "d_all": frac(d_all),
        "gamma_c": gamma_c,
        "gamma_c_witness": gc_witness,
        "Ls": leaves,
        "b": b,
        "b_witness": b_witness,
        "T173": theorem_slack,
        "R184": frac(r184),
        "R185": frac(r185),
        "crossing184": r184 < 0,
        "crossing185": r185 < 0,
        "b_solver": b_solver,
        "gc_solver": gc_solver,
        "b_seconds": round(b_seconds, 6),
        "gc_seconds": round(gc_seconds, 6),
    }


def controls() -> list[tuple[str, nx.Graph, bool]]:
    rows: list[tuple[str, nx.Graph, bool]] = []
    seen: set[str] = set()
    def add(name: str, graph: nx.Graph, equality: bool = False) -> None:
        key = graph6(nx.convert_node_labels_to_integers(graph, ordering="sorted"))
        if key not in seen:
            seen.add(key)
            rows.append((name, graph, equality))
        elif equality:
            # Equality controls must remain explicit even if a named graph was seen.
            rows.append((name, graph, equality))
    for index, graph in enumerate(nx.graph_atlas_g()):
        if 2 <= len(graph) <= 7 and nx.is_connected(graph):
            add(f"atlas:{index}", graph)
    for n in range(2, 13):
        add(f"P{n}", nx.path_graph(n))
        if n >= 3:
            add(f"C{n}", nx.cycle_graph(n))
    for r in range(2, 11):
        add(f"K1,{r}", nx.star_graph(r))
    for n in range(2, 11):
        add(f"K{n}", nx.complete_graph(n))
    for a in range(1, 7):
        for b in range(a, 7):
            add(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
    for m in range(1, 9):
        add(f"C5[K{m}]", clique_cycle_blowup((m,) * 5))
    add("Petersen", nx.petersen_graph())
    add("T(7)", triangular_graph(7))
    for length in (6, 8, 10):
        add(f"D_{length}", endpoint_barbell(length))
    equality_weights = ((2, 2, 2, 2, 2), (3, 3, 3, 3, 3), (4, 4, 4, 4, 4),
                        (5, 5, 5, 5, 5), (6, 6, 6, 6, 6), (8, 8, 8, 8, 8),
                        (4, 4, 3, 4, 3), (4, 2, 4, 2, 4), (4, 1, 4, 1, 4),
                        (3, 1, 3, 1, 3), (5, 5, 4, 5, 4))
    for weights in equality_weights:
        add(f"equality:B{weights}", clique_cycle_blowup(weights), equality=True)
    return rows


def run_lock() -> None:
    emit({
        "stage": "normalization_lock",
        "source": "data/INVARIANT-GLOSSARY.md primary verbatim definitions",
        "B": "vertices of maximum eccentricity",
        "d_boundary": "average of all positive dist_H(b,v), b in B(H), v in V(H)",
        "d_all": "average of all dist_H(u,v), u != v",
        "normalization": "ordered pairs excluding zero self-pairs",
        "selection_formula_changed": False,
        "note": "the later compute hint saying avg_v dist(v,B) conflicts with the primary verbatim definition and is not used",
    })


def run_gate(shard: int, shards: int) -> None:
    rows = controls()
    selected = [(i, row) for i, row in enumerate(rows) if i % shards == shard]
    emit({"stage": "gate_shard_start", "shard": shard, "shards": shards, "total_controls": len(rows), "selected": len(selected)})
    for index, (name, graph, equality_expected) in selected:
        try:
            row = evaluate(graph, name, "gate")
            row.update({"gate_index": index, "equality_expected": equality_expected})
            if row["crossing184"] or row["crossing185"]:
                row["gate_failure"] = "negative residual"
            elif equality_expected and (row["R184"] != "0" or row["R185"] != "0"):
                row["gate_failure"] = "recorded equality mismatch"
            else:
                row["gate_failure"] = None
            emit(row)
        except SolveTimeout as error:
            emit({"stage": "gate", "gate_index": index, "name": name, "timeout": str(error), "gate_failure": "timeout"})
    emit({"stage": "gate_shard_end", "shard": shard, "shards": shards})


def run_grid(m: int, length_min: int, length_max: int) -> None:
    emit({"stage": "grid_shard_start", "m": m, "length_min": length_min, "length_max": length_max})
    for length in range(length_min, length_max + 1):
        name = f"K({m},{length})"
        try:
            row = evaluate(rooted_comet(m, length), name, "grid")
            row.update({"comet_m": m, "comet_length": length})
            emit(row)
            if row["crossing184"] or row["crossing185"]:
                emit({"stage": "grid_stop", "m": m, "length": length, "reason": "crossing requires independent verification"})
                return
        except SolveTimeout as error:
            emit({"stage": "grid", "name": name, "comet_m": m, "comet_length": length, "timeout": str(error)})
    emit({"stage": "grid_shard_end", "m": m, "length_min": length_min, "length_max": length_max})


def main() -> None:
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("lock")
    gate = sub.add_parser("gate")
    gate.add_argument("--shard", type=int, required=True)
    gate.add_argument("--shards", type=int, default=32)
    grid = sub.add_parser("grid")
    grid.add_argument("--m", type=int, choices=range(2, 11), required=True)
    grid.add_argument("--length-min", type=int, choices=range(1, 31), default=1)
    grid.add_argument("--length-max", type=int, choices=range(1, 31), default=30)
    args = parser.parse_args()
    OUTPUT_PATH = args.output
    if args.command == "lock":
        run_lock()
    elif args.command == "gate":
        run_gate(args.shard, args.shards)
    else:
        if args.length_min > args.length_max:
            parser.error("--length-min must not exceed --length-max")
        run_grid(args.m, args.length_min, args.length_max)


if __name__ == "__main__":
    main()
