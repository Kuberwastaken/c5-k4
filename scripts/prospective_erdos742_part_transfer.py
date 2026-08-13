#!/usr/bin/env python3
"""Frozen K5,5 -> K4,6 premise-preserving Murty--Simon trial."""

from __future__ import annotations

import argparse
import hashlib
import json

import networkx as nx


def diameter(graph: nx.Graph) -> int | None:
    return nx.diameter(graph) if nx.is_connected(graph) else None


def deletion_profiles(graph: nx.Graph) -> list[dict]:
    rows = []
    for edge in sorted((min(a, b), max(a, b)) for a, b in graph.edges()):
        deleted = graph.copy()
        deleted.remove_edge(*edge)
        rows.append({
            "edge": list(edge),
            "connected": nx.is_connected(deleted),
            "diameter": diameter(deleted),
            "endpoint_distance": nx.shortest_path_length(deleted, *edge)
                if nx.is_connected(deleted) else None,
        })
    return rows


def exact_record(name: str, graph: nx.Graph) -> dict:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    deletions = deletion_profiles(graph) if diameter(graph) == 2 else []
    critical = diameter(graph) == 2 and all(row["diameter"] != 2 for row in deletions)
    n = graph.number_of_nodes()
    bound = n * n // 4
    return {
        "name": name,
        "n": n,
        "m": graph.number_of_edges(),
        "diameter": diameter(graph),
        "diameter2critical": critical,
        "bound": bound,
        "slack": bound - graph.number_of_edges(),
        "deletions": deletions,
        "graph6_sha256": hashlib.sha256(
            nx.to_graph6_bytes(graph, header=False).strip()).hexdigest(),
    }


def gate() -> dict:
    rows = []
    for atlas_index, graph in enumerate(nx.graph_atlas_g()):
        if 3 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph):
            row = exact_record(f"atlas_{atlas_index}", graph)
            if row["diameter2critical"]:
                row["atlas_index"] = atlas_index
                rows.append(row)
    named = {
        "K2,2": nx.complete_bipartite_graph(2, 2),
        "K2,3": nx.complete_bipartite_graph(2, 3),
        "K3,3": nx.complete_bipartite_graph(3, 3),
        "Petersen": nx.petersen_graph(),
        "K5,5": nx.complete_bipartite_graph(5, 5),
    }
    controls = {name: exact_record(name, graph) for name, graph in named.items()}
    violations = [row for row in rows if row["slack"] < 0]
    violations += [row for row in controls.values() if row["diameter2critical"] and row["slack"] < 0]
    carrier = controls["K5,5"]
    if (carrier["m"], carrier["diameter"], carrier["diameter2critical"], carrier["slack"]) != (25, 2, True, 0):
        raise RuntimeError("K5,5 equality calibration failed")
    if violations:
        raise RuntimeError("database gate found a Murty--Simon violation")
    return {
        "mode": "gate",
        "status": "PASS",
        "atlas_diameter2critical_graphs": len(rows),
        "violations": 0,
        "atlas_edge_deletions_checked": sum(len(row["deletions"]) for row in rows),
        "controls": controls,
    }


def evaluate() -> dict:
    graph = nx.complete_bipartite_graph(4, 6)
    row = exact_record("K4,6", graph)
    expected = (10, 24, 2, True, 25, 1)
    actual = (row["n"], row["m"], row["diameter"], row["diameter2critical"], row["bound"], row["slack"])
    if actual != expected:
        raise RuntimeError(f"development mismatch: {actual} != {expected}")
    return {"mode": "evaluate", "status": "COMPLETE_HOLD", **row}


def verify() -> dict:
    graph = nx.complete_bipartite_graph(4, 6)
    part_a = set(range(4))
    part_b = set(range(4, 10))
    cross_edges = all(graph.has_edge(a, b) for a in part_a for b in part_b)
    no_internal = all(not graph.has_edge(a, b) for part in (part_a, part_b)
                      for a in part for b in part if a < b)
    endpoint_checks = []
    for a in sorted(part_a):
        for b in sorted(part_b):
            deleted = graph.copy()
            deleted.remove_edge(a, b)
            endpoint_checks.append({
                "edge": [a, b],
                "distance_after_deletion": nx.shortest_path_length(deleted, a, b),
            })
    return {
        "mode": "verify",
        "complete_bipartite_replay": cross_edges and no_internal,
        "part_sizes": [len(part_a), len(part_b)],
        "edge_count_product": len(part_a) * len(part_b),
        "all_deleted_endpoint_distances_three": all(
            row["distance_after_deletion"] == 3 for row in endpoint_checks),
        "endpoint_checks": endpoint_checks,
        "bound": (len(part_a) + len(part_b)) ** 2 // 4,
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
