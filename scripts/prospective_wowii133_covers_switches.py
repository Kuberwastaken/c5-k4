#!/usr/bin/env python3
"""Frozen WOWII 133 covers-and-C4-safe-switches trial.

Construction scope is fixed in the matching contract.  Output is append-only.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii133_covers_switches_ledger.jsonl"
CORE_PATH = ROOT / "scripts/method_v02_133_search.py"
SPEC = importlib.util.spec_from_file_location("wow133_core", CORE_PATH)
assert SPEC and SPEC.loader
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)


def append(row: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def g6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph), header=False).decode().strip()


def generalized_petersen(n: int, k: int) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(2 * n))
    for i in range(n):
        graph.add_edge(i, (i + 1) % n)
        graph.add_edge(i, n + i)
        graph.add_edge(n + i, n + (i + k) % n)
    return graph


def normalized_projective_vectors(q: int) -> list[tuple[int, int, int]]:
    vectors = set()
    for raw in itertools.product(range(q), repeat=3):
        if raw == (0, 0, 0):
            continue
        first = next(value for value in raw if value)
        inverse = pow(first, q - 2, q)
        vectors.add(tuple((inverse * value) % q for value in raw))
    return sorted(vectors)


def projective_plane_levi(q: int) -> nx.Graph:
    points = normalized_projective_vectors(q)
    lines = normalized_projective_vectors(q)
    graph = nx.Graph()
    graph.add_nodes_from(range(2 * len(points)))
    offset = len(points)
    for i, point in enumerate(points):
        for j, line in enumerate(lines):
            if sum(a * b for a, b in zip(point, line)) % q == 0:
                graph.add_edge(i, offset + j)
    return graph


def cotree_edges(graph: nx.Graph) -> tuple[list[tuple[int, int]], set[tuple[int, int]]]:
    graph = nx.convert_node_labels_to_integers(graph)
    tree = nx.minimum_spanning_tree(graph)
    tree_edges = {tuple(sorted(edge)) for edge in tree.edges()}
    cotree = sorted(tuple(sorted(edge)) for edge in graph.edges() if tuple(sorted(edge)) not in tree_edges)
    return cotree, tree_edges


def z3_lift(base: nx.Graph, voltages: tuple[int, ...]) -> nx.Graph:
    base = nx.convert_node_labels_to_integers(base)
    cotree, tree_edges = cotree_edges(base)
    voltage = {edge: 0 for edge in tree_edges}
    voltage.update(dict(zip(cotree, voltages)))
    lift = nx.Graph()
    lift.add_nodes_from(range(3 * len(base)))
    for u, v in sorted(tuple(sorted(edge)) for edge in base.edges()):
        shift = voltage[(u, v)]
        for sheet in range(3):
            lift.add_edge(3 * u + sheet, 3 * v + (sheet + shift) % 3)
    return lift


def voltage_assignments(base: nx.Graph, cap: int | None = None):
    rank = base.number_of_edges() - len(base) + 1
    count = 0
    for assignment in itertools.product(range(3), repeat=rank):
        if not any(assignment):
            continue
        yield assignment
        count += 1
        if cap is not None and count >= cap:
            break


def named_graphs():
    fixed = [
        ("Petersen", nx.petersen_graph()),
        ("Heawood", nx.heawood_graph()),
        ("Moebius-Kantor", nx.moebius_kantor_graph()),
        ("Pappus", nx.pappus_graph()),
        ("Desargues", nx.desargues_graph()),
        ("Dodecahedron", nx.dodecahedral_graph()),
        ("McGee", nx.LCF_graph(24, [12, 7, -7], 8)),
    ]
    if hasattr(nx, "tutte_cage_graph"):
        fixed.append(("Tutte-Coxeter", nx.tutte_cage_graph()))
    yield from fixed
    for n in range(5, 21):
        for k in range(1, (n - 1) // 2 + 1):
            graph = generalized_petersen(n, k)
            if nx.is_connected(graph) and not CORE.has_c4(graph):
                yield f"GP({n},{k})", graph


def cover_graphs():
    bases = [
        ("C5", nx.cycle_graph(5), None),
        ("C6", nx.cycle_graph(6), None),
        ("Petersen", nx.petersen_graph(), None),
        ("Heawood", nx.heawood_graph(), 300),
    ]
    for name, base, cap in bases:
        for index, assignment in enumerate(voltage_assignments(base, cap)):
            graph = z3_lift(base, assignment)
            if nx.is_connected(graph):
                yield f"Z3:{name}:{index}", graph


def switch_descendants(graph: nx.Graph):
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    seen = set()
    for first_index, (a, b) in enumerate(edges):
        for c, d in edges[first_index + 1:]:
            if len({a, b, c, d}) != 4:
                continue
            for added in (((a, c), (b, d)), ((a, d), (b, c))):
                added = tuple(sorted(tuple(sorted(edge)) for edge in added))
                if any(graph.has_edge(*edge) for edge in added):
                    continue
                signature = ((a, b), (c, d), added)
                if signature in seen:
                    continue
                seen.add(signature)
                result = graph.copy()
                result.remove_edges_from(((a, b), (c, d)))
                result.add_edges_from(added)
                if nx.is_connected(result) and not CORE.has_c4(result):
                    assert sorted(dict(graph.degree()).values()) == sorted(dict(result.degree()).values())
                    yield signature, result


def discovery_graphs():
    globally_seen = set()

    def unique(name: str, graph: nx.Graph):
        code = g6(graph)
        if code in globally_seen or len(graph) > 42:
            return None
        globally_seen.add(code)
        return name, graph

    for name, graph in named_graphs():
        row = unique(f"named:{name}", graph)
        if row:
            yield row
    for q in (2, 3):
        row = unique(f"incidence:PG(2,{q})", projective_plane_levi(q))
        if row:
            yield row

    connected_petersen_covers = []
    for name, graph in cover_graphs():
        row = unique(name, graph)
        if row:
            yield row
        if name.startswith("Z3:Petersen:") and len(connected_petersen_covers) < 40:
            connected_petersen_covers.append((name, graph))

    switch_count = 0
    switch_bases = [("Petersen", nx.petersen_graph())] + connected_petersen_covers
    for base_name, base in switch_bases:
        for index, (_, graph) in enumerate(switch_descendants(base)):
            row = unique(f"switch:{base_name}:{index}", graph)
            if row:
                yield row
                switch_count += 1
            if switch_count >= 500:
                return


def evaluate(graph: nx.Graph, name: str, stage: str, timeout: float) -> dict:
    row = CORE.evaluate(graph, name, stage, timeout=timeout)
    row["event"] = "graph_evaluated"
    return row


def run_gate() -> None:
    rows = []
    for name, graph in CORE.controls():
        row = evaluate(graph, name, "gate", 10.0)
        append(row)
        rows.append(row)
    bad = sum(row.get("residual", 0) < 0 for row in rows)
    timeouts = sum(row["kind"] == "solve_timeout" for row in rows)
    append({"event": "gate_summary", "graphs": len(rows), "crossings": bad, "timeouts": timeouts})
    if bad or timeouts:
        raise SystemExit("GATE_FAIL")


def run_discovery(offset: int, limit: int) -> None:
    deadline = time.monotonic() + 55.0
    selected = itertools.islice(discovery_graphs(), offset, offset + limit)
    rows = []
    for global_index, (name, graph) in enumerate(selected, offset):
        remaining = deadline - time.monotonic()
        if remaining <= 0.25:
            break
        row = evaluate(graph, name, "discovery", min(10.0, remaining - 0.1))
        row["discovery_index"] = global_index
        append(row)
        rows.append(row)
        if row.get("residual", 0) < 0:
            break
    append({"event": "batch_summary", "offset": offset, "requested": limit,
            "completed": len(rows), "next_offset": offset + len(rows),
            "crossings": sum(row.get("residual", 0) < 0 for row in rows),
            "equalities": sum(row.get("residual") == 0 for row in rows),
            "timeouts": sum(row["kind"] == "solve_timeout" for row in rows),
            "minimum_residual": min((row["residual"] for row in rows if row["kind"] == "graph"), default=None)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("gate", "discovery", "count"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    if args.stage == "gate":
        run_gate()
    elif args.stage == "count":
        print(sum(1 for _ in itertools.islice(discovery_graphs(), 1500)))
    else:
        run_discovery(args.offset, args.limit)


if __name__ == "__main__":
    main()
