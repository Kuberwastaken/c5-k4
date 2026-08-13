#!/usr/bin/env python3
"""Frozen canonical Hajós-join trial for current DeepMind Erdős 128."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json

import networkx as nx

from prospective_erdos128_mycielski import c5_blowup, controls, exact_minimum, has_triangle


def hajos_join() -> nx.Graph:
    first = c5_blowup(2)
    second = nx.relabel_nodes(c5_blowup(2), {vertex: vertex + 10 for vertex in range(10)})
    graph = nx.compose(first, second)
    graph.remove_edge(0, 2)
    graph.remove_edge(10, 12)
    graph = nx.contracted_nodes(graph, 0, 10, self_loops=False, copy=False)
    graph.add_edge(2, 12)
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def graph_digest(graph: nx.Graph) -> str:
    data = nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph), header=False).strip()
    return hashlib.sha256(data).hexdigest()


def gate() -> dict:
    rows = []
    for name, graph in controls():
        size, minimum, witness, checked = exact_minimum(graph)
        n = graph.number_of_nodes()
        margin = 50 * minimum - n * n
        row = {
            "name": name,
            "n": n,
            "m": graph.number_of_edges(),
            "triangle_free": not has_triangle(graph),
            "eligible_size": size,
            "minimum_induced_edges": minimum,
            "minimizing_set": witness,
            "subsets_checked": checked,
            "premise_margin": margin,
        }
        rows.append(row)
        if margin > 0:
            raise RuntimeError(f"unexpected strict-premise control: {name}")
    b2 = next(row for row in rows if row["name"] == "B2")
    if b2["premise_margin"] != 0 or b2["minimum_induced_edges"] != 2:
        raise RuntimeError("B2 equality calibration failed")
    return {
        "mode": "gate",
        "status": "PASS",
        "controls": len(rows),
        "unexpected_strict_premise": 0,
        "B2": b2,
        "total_subsets_checked": sum(row["subsets_checked"] for row in rows),
    }


def evaluate() -> dict:
    graph = hajos_join()
    if graph.number_of_nodes() != 19 or graph.number_of_edges() != 39:
        raise RuntimeError("frozen Hajós join size mismatch")
    if has_triangle(graph):
        raise RuntimeError("frozen Hajós join unexpectedly contains a triangle")
    size, minimum, witness, checked = exact_minimum(graph)
    witness_edges = graph.subgraph(witness).number_of_edges()
    if witness_edges != minimum:
        raise RuntimeError("minimum witness replay failed")
    margin = 50 * minimum - graph.number_of_nodes() ** 2
    return {
        "mode": "evaluate",
        "status": "CANDIDATE" if margin > 0 else "PREMISE_FALSE_STRICT",
        "graph6_sha256": graph_digest(graph),
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "triangle_free": True,
        "eligible_size": size,
        "minimum_induced_edges": minimum,
        "minimizing_set": witness,
        "witness_edge_count": witness_edges,
        "subsets_checked": checked,
        "premise_margin": margin,
        "strict_premise": margin > 0,
    }


def independent_verify() -> dict:
    graph = hajos_join()
    n = graph.number_of_nodes()
    target = n // 2
    order = sorted(graph.nodes(), key=lambda vertex: (graph.degree(vertex), vertex))
    best = graph.number_of_edges() + 1
    witness: list[int] | None = None
    states = 0

    def search(position: int, chosen: list[int], edge_count: int) -> None:
        nonlocal best, witness, states
        states += 1
        if edge_count >= best:
            return
        needed = target - len(chosen)
        remaining = len(order) - position
        if needed < 0 or remaining < needed:
            return
        if needed == 0:
            best = edge_count
            witness = sorted(chosen)
            return
        if position == len(order):
            return
        vertex = order[position]
        added = sum(graph.has_edge(vertex, other) for other in chosen)
        search(position + 1, chosen + [vertex], edge_count + added)
        search(position + 1, chosen, edge_count)

    search(0, [], 0)
    if witness is None or graph.subgraph(witness).number_of_edges() != best:
        raise RuntimeError("independent branch-and-bound witness failed")
    return {
        "mode": "verify",
        "eligible_size": target,
        "minimum_induced_edges": best,
        "minimizing_set": witness,
        "witness_edge_count": graph.subgraph(witness).number_of_edges(),
        "states": states,
        "premise_margin": 50 * best - n * n,
        "triangle_count": sum(nx.triangles(graph).values()) // 3,
        "graph6_sha256": graph_digest(graph),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("gate", "evaluate", "verify"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = {"gate": gate, "evaluate": evaluate, "verify": independent_verify}[args.mode]()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
