#!/usr/bin/env python3
"""Frozen H(5,5) leaf-transfer trial for independent domination Conj. 1.6."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def h_graph(q: int, p: int) -> nx.Graph:
    graph = nx.complete_graph(q)
    cursor = q
    for center in range(q):
        leaves = range(cursor, cursor + p)
        graph.add_edges_from((center, leaf) for leaf in leaves)
        cursor += p
    return graph


def is_independent_dominating(graph: nx.Graph, subset: set[int]) -> bool:
    if any(a in subset and b in subset for a, b in graph.edges()):
        return False
    return all(vertex in subset or any(neighbor in subset for neighbor in graph.neighbors(vertex))
               for vertex in graph.nodes())


def exact_bruteforce(graph: nx.Graph) -> tuple[int, list[int], int]:
    nodes = sorted(graph.nodes())
    checked = 0
    for size in range(len(nodes) + 1):
        for subset in itertools.combinations(nodes, size):
            checked += 1
            if is_independent_dominating(graph, set(subset)):
                return size, list(subset), checked
    raise RuntimeError("no independent dominating set")


def exact_milp(graph: nx.Graph) -> dict:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    n = graph.number_of_nodes()
    rows = graph.number_of_edges() + n
    matrix = lil_matrix((rows, n), dtype=float)
    lower = np.full(rows, -np.inf)
    upper = np.full(rows, np.inf)
    row = 0
    for left, right in graph.edges():
        matrix[row, left] = 1
        matrix[row, right] = 1
        upper[row] = 1
        row += 1
    for vertex in graph.nodes():
        matrix[row, vertex] = 1
        for neighbor in graph.neighbors(vertex):
            matrix[row, neighbor] = 1
        lower[row] = 1
        row += 1
    result = milp(
        c=np.ones(n),
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"time_limit": 50.0},
    )
    if not result.success:
        raise RuntimeError(f"MILP failed: status={result.status}, message={result.message}")
    witness = [vertex for vertex, value in enumerate(result.x) if value > 0.5]
    if not is_independent_dominating(graph, set(witness)):
        raise RuntimeError("MILP witness replay failed")
    return {
        "i": int(round(result.fun)),
        "witness": witness,
        "mip_node_count": int(result.mip_node_count),
        "mip_gap": float(result.mip_gap),
    }


def residual(graph: nx.Graph, independent_domination: int) -> dict:
    n = graph.number_of_nodes()
    degree = max(dict(graph.degree()).values())
    if degree % 2 == 0:
        left = (degree + 2) ** 2 * independent_domination
        right = (degree ** 2 + 4) * n
        parity = "even"
    else:
        left = (degree + 1) * (degree + 3) * independent_domination
        right = (degree ** 2 + 3) * n
        parity = "odd"
    return {"n": n, "D": degree, "i": independent_domination,
            "parity": parity, "left": left, "right": right, "residual": right - left}


def gate() -> dict:
    rows = []
    for index, graph in enumerate(nx.graph_atlas_g()):
        if 2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph):
            value, witness, checked = exact_bruteforce(graph)
            row = {"atlas_index": index, **residual(graph, value),
                   "witness": witness, "subsets_checked": checked}
            rows.append(row)
            if row["residual"] < 0:
                raise RuntimeError(f"Atlas violation at {index}")
    controls = {}
    for q, p in ((2, 1), (2, 2), (3, 2), (3, 3)):
        graph = h_graph(q, p)
        value, witness, checked = exact_bruteforce(graph)
        controls[f"H({q},{p})"] = {**residual(graph, value), "witness": witness,
                                    "subsets_checked": checked}
    carrier = h_graph(5, 5)
    carrier_milp = exact_milp(carrier)
    carrier_row = {**residual(carrier, carrier_milp["i"]), **carrier_milp}
    if (carrier_row["D"], carrier_row["i"], carrier_row["residual"]) != (9, 21, 0):
        raise RuntimeError("H(5,5) equality calibration failed")
    return {
        "mode": "gate", "status": "PASS", "atlas_graphs": len(rows),
        "atlas_violations": 0,
        "atlas_subsets_checked": sum(row["subsets_checked"] for row in rows),
        "minimum_atlas_residual": min(row["residual"] for row in rows),
        "controls": controls, "carrier": carrier_row,
    }


def development_graph() -> nx.Graph:
    graph = h_graph(5, 5)
    graph.remove_edge(0, 5)
    graph.add_edge(1, 5)
    return graph


def digest(graph: nx.Graph) -> str:
    return hashlib.sha256(nx.to_graph6_bytes(graph, header=False).strip()).hexdigest()


def evaluate() -> dict:
    graph = development_graph()
    solution = exact_milp(graph)
    row = {**residual(graph, solution["i"]), **solution}
    if (row["n"], row["D"], row["i"], row["residual"]) != (30, 10, 20, 240):
        raise RuntimeError("development coordinates differ from frozen prediction")
    return {
        "mode": "evaluate", "status": "COMPLETE_HOLD", **row,
        "isolate_free": min(dict(graph.degree()).values()) > 0,
        "center_degrees": [graph.degree(vertex) for vertex in range(5)],
        "graph6_sha256": digest(graph),
    }


def verify() -> dict:
    graph = development_graph()
    leaf_counts = [sum(graph.degree(neighbor) == 1 for neighbor in graph.neighbors(center))
                   for center in range(5)]
    candidates = [{center} | {leaf for other in range(5) if other != center
                              for leaf in graph.neighbors(other) if graph.degree(leaf) == 1}
                  for center in range(5)]
    all_leaves = {vertex for vertex in graph if graph.degree(vertex) == 1}
    candidates.append(all_leaves)
    valid = [candidate for candidate in candidates if is_independent_dominating(graph, candidate)]
    minimum = min(valid, key=lambda candidate: (len(candidate), sorted(candidate)))
    return {
        "mode": "verify", "leaf_counts": leaf_counts,
        "candidate_sizes": [len(candidate) for candidate in candidates],
        "all_candidates_valid": len(valid) == len(candidates),
        "structural_minimum": len(minimum), "witness": sorted(minimum),
        "witness_replay": is_independent_dominating(graph, minimum),
        "residual": residual(graph, len(minimum)),
        "graph6_sha256": digest(graph),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("gate", "evaluate", "verify"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = {"gate": gate, "evaluate": evaluate, "verify": verify}[args.mode]()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
