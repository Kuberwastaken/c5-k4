#!/usr/bin/env python3
"""Exact small-graph audit of the unresolved WOWII 183 extremal profile.

For H = G^2, put r = rad(H) and q = n - 1 - Delta(H).  The only profile
not already covered by WOWII 173 is q = 2*r - 3.  This script exhausts the
connected Graph Atlas graphs, independently recomputes b and gamma_c, and
checks the distance-layer rigidity forced by equality in q >= 2*r - 3.
"""

import argparse
import sys
from itertools import combinations

import networkx as nx


def connected_domination_number(graph: nx.Graph) -> int:
    vertices = tuple(graph.nodes)
    for size in range(1, len(vertices) + 1):
        for chosen in combinations(vertices, size):
            selected = set(chosen)
            if size > 1 and not nx.is_connected(graph.subgraph(selected)):
                continue
            dominated = selected | {u for v in selected for u in graph.neighbors(v)}
            if len(dominated) == len(vertices):
                return size
    raise AssertionError("connected graph has no connected dominating set")


def bipartite_number(graph: nx.Graph) -> int:
    vertices = tuple(graph.nodes)
    for size in range(len(vertices), 0, -1):
        for chosen in combinations(vertices, size):
            if nx.is_bipartite(graph.subgraph(chosen)):
                return size
    raise AssertionError("nonempty graph has no bipartite induced subgraph")


def graph_square(graph: nx.Graph) -> nx.Graph:
    square = nx.Graph()
    square.add_nodes_from(graph)
    lengths = dict(nx.all_pairs_shortest_path_length(graph, cutoff=2))
    square.add_edges_from(
        (u, v)
        for u, v in combinations(graph.nodes, 2)
        if lengths[u].get(v, 3) <= 2
    )
    return square


def equality_layer_profiles(graph: nx.Graph, square: nx.Graph) -> list[tuple[int, ...]]:
    """Return layer-size profiles at maximum-degree vertices of G^2.

    In the extremal q profile every such vertex must have eccentricity 2r-1
    in G and exactly one vertex in each layer 3,...,2r-1.
    """

    r = nx.radius(square)
    delta = max(dict(square.degree()).values())
    profiles = []
    for vertex, degree in square.degree():
        if degree != delta:
            continue
        distances = nx.single_source_shortest_path_length(graph, vertex)
        eccentricity = max(distances.values())
        profile = tuple(
            sum(distance == layer for distance in distances.values())
            for layer in range(eccentricity + 1)
        )
        assert eccentricity == 2 * r - 1
        assert profile[3:] == (1,) * (2 * r - 3)
        profiles.append(profile)
    return profiles


def read_graph6(path: str):
    stream = sys.stdin.buffer if path == "-" else open(path, "rb")
    try:
        for line in stream:
            if line.strip() and not line.startswith(b">"):
                yield nx.from_graph6_bytes(line.strip())
    finally:
        if path != "-":
            stream.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--graph6",
        help="audit a graph6 catalogue instead of the connected Graph Atlas; use - for stdin",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="suppress individual graph6 records for tight examples",
    )
    args = parser.parse_args()
    if args.graph6:
        graphs = read_graph6(args.graph6)
        gate_name = "graph6 catalogue"
    else:
        graphs = [
            graph
            for graph in nx.graph_atlas_g()
            if 2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph)
        ]
        gate_name = "Graph Atlas orders 2..7"
    graph_count = 0
    critical_count = 0
    nonbipartite_count = 0
    minimum_excess = None
    tight_count = 0
    tight_records = []

    for graph in graphs:
        if not nx.is_connected(graph):
            continue
        graph_count += 1
        square = graph_square(graph)
        n = graph.number_of_nodes()
        r = nx.radius(square)
        q = n - 1 - max(dict(square.degree()).values())
        assert q >= 2 * r - 3
        if q != 2 * r - 3:
            continue

        profiles = equality_layer_profiles(graph, square)
        gamma_c = connected_domination_number(graph)
        b = bipartite_number(graph)
        excess = b - gamma_c - 1
        record = (graph, r, q, gamma_c, b, excess, profiles)
        critical_count += 1
        if nx.is_bipartite(graph):
            continue
        nonbipartite_count += 1
        minimum_excess = excess if minimum_excess is None else min(minimum_excess, excess)
        assert excess >= 1
        if excess == 1:
            tight_count += 1
            if not args.summary_only:
                tight_records.append(record)

    print(f"{gate_name} gate: {graph_count} connected graphs")
    print(f"q=2r-3 profile: {critical_count} graphs ({nonbipartite_count} nonbipartite)")
    print(f"nonbipartite minimum b-gamma_c-1: {minimum_excess}")
    print(f"lemma equality b=gamma_c+2: {tight_count} graphs")
    for graph, r, q, gamma_c, b, excess, profiles in tight_records:
        graph6 = nx.to_graph6_bytes(graph, header=False).decode().strip()
        print(
            "tight",
            f"g6={graph6}",
            f"n={graph.number_of_nodes()}",
            f"m={graph.number_of_edges()}",
            f"r={r}",
            f"q={q}",
            f"gamma_c={gamma_c}",
            f"b={b}",
            f"profiles={profiles}",
        )


if __name__ == "__main__":
    main()
