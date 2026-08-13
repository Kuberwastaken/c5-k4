#!/usr/bin/env python3
"""Frozen v47 Reed color-blocker audit and exact evaluation."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json

import networkx as nx

from method_v46_reed_weighted_surgery import (
    exact_profile,
    maximum_clique,
    normalized_graph,
    valid_profile,
    weighted_c5,
)


NEIGHBORHOOD = [0, 1, 2, 3, 4, 12, 13, 6, 9]
NEW_VERTEX = 15
FROZEN_CLAW = [0, NEW_VERTEX, 5, 14]


def frozen_graph() -> nx.Graph:
    graph, _ = weighted_c5((3, 3, 3, 3, 3))
    graph.add_node(NEW_VERTEX)
    graph.add_edges_from((NEW_VERTEX, vertex) for vertex in NEIGHBORHOOD)
    return normalized_graph(graph)


def graph_digest(graph: nx.Graph) -> str:
    data = nx.to_graph6_bytes(normalized_graph(graph), header=False).strip()
    return hashlib.sha256(data).hexdigest()


def is_induced_claw(graph: nx.Graph, vertices: list[int]) -> bool:
    center, *leaves = vertices
    return (
        all(graph.has_edge(center, leaf) for leaf in leaves)
        and all(not graph.has_edge(a, b) for a, b in itertools.combinations(leaves, 2))
    )


def induced_witness(graph: nx.Graph, kind: str) -> list[int] | None:
    for vertices in itertools.combinations(graph.nodes(), 5):
        subgraph = graph.subgraph(vertices)
        degrees = sorted(degree for _, degree in subgraph.degree())
        if kind == "P5" and nx.is_connected(subgraph) and degrees == [1, 1, 2, 2, 2]:
            return list(vertices)
        if kind == "chair" and nx.is_connected(subgraph) and degrees == [1, 1, 1, 2, 3]:
            return list(vertices)
    return None


def audit() -> dict:
    graph = frozen_graph()
    complement = nx.complement(graph)
    independent_set, alpha_states = maximum_clique(
        [
            sum(1 << neighbor for neighbor in complement.neighbors(vertex))
            for vertex in complement.nodes()
        ]
    )
    p5 = induced_witness(graph, "P5")
    chair = induced_witness(graph, "chair")
    high_degree = [vertex for vertex, degree in graph.degree() if degree >= 5]
    high_degree_stable = all(
        not graph.has_edge(a, b) for a, b in itertools.combinations(high_degree, 2)
    )
    odd_cycle = [0, 3, 6, 9, 12]
    odd_cycle_induced = graph.subgraph(odd_cycle).number_of_edges() == 5
    return {
        "mode": "audit",
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "graph6_sha256": graph_digest(graph),
        "explicit_claw": FROZEN_CLAW,
        "explicit_claw_valid": is_induced_claw(graph, FROZEN_CLAW),
        "alpha": len(independent_set),
        "independent_set": independent_set,
        "alpha_states": alpha_states,
        "complement_connected": nx.is_connected(complement),
        "induced_P5": p5,
        "induced_chair": chair,
        "high_degree_vertices_stable": high_degree_stable,
        "induced_high_degree_C5": odd_cycle if odd_cycle_induced else None,
        "static_domain_checks": {
            "claw_free": False,
            "quasi_line": False,
            "alpha_at_most_2": len(independent_set) <= 2,
            "disconnected_complement": not nx.is_connected(complement),
            "P5_free": p5 is None,
            "chair_free": chair is None,
            "high_degree_vertices_stable": high_degree_stable,
            "every_induced_odd_cycle_has_degree_at_most_3": False,
        },
        "conditional_Rabern_2008_threshold": (graph.number_of_nodes() + 3 - len(independent_set)) / 2,
    }


def evaluate() -> dict:
    graph = frozen_graph()
    profile = exact_profile(graph)
    if not valid_profile(graph, profile):
        raise RuntimeError("invalid exact certificate")
    if not is_induced_claw(graph, FROZEN_CLAW):
        raise RuntimeError("frozen claw witness failed")
    return {
        "mode": "evaluate",
        "graph6_sha256": graph_digest(graph),
        "profile": profile.as_dict(),
        "explicit_claw": FROZEN_CLAW,
        "explicit_claw_valid": True,
        "crossing": profile.slack < 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("audit", "evaluate"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = audit() if args.mode == "audit" else evaluate()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
