#!/usr/bin/env python3
"""Exact small-graph audit of the known WOWII 173 baseline wall."""

from fractions import Fraction
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


def mean_distance(graph: nx.Graph) -> Fraction:
    vertices = tuple(graph.nodes)
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    pairs = tuple(combinations(vertices, 2))
    return sum((Fraction(distances[u][v]) for u, v in pairs), Fraction()) / len(pairs)


def main() -> None:
    atlas = [
        graph
        for graph in nx.graph_atlas_g()
        if 2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph)
    ]
    diameter_two = []
    equality = 0
    for graph in atlas:
        gamma_c = connected_domination_number(graph)
        b = bipartite_number(graph)
        assert b >= gamma_c + 1
        equality += b == gamma_c + 1

        if nx.diameter(graph) != 2:
            continue
        diameter_two.append(graph)
        square = graph_square(graph)
        n = graph.number_of_nodes()
        assert nx.is_isomorphic(square, nx.complete_graph(n))
        maximum_degree = max(dict(square.degree()).values())
        radius = nx.radius(square)
        average_distance = mean_distance(square)
        periphery = set(nx.periphery(square))
        assert periphery == set(square.nodes)
        assert maximum_degree + 2 * radius == n + 1
        assert maximum_degree + 2 * average_distance == n + 1
        assert max(dict(square.subgraph(periphery).degree()).values()) + 2 == n + 1

    print(f"atlas gate: {len(atlas)} connected graphs on 2..7 vertices")
    print(f"WOWII 173 form b >= gamma_c+1: all hold; {equality} are tight")
    print(f"diameter-two graphs: {len(diameter_two)}")
    print("176 and 182--185 standard square readings reduce to the 173 n+1 wall")


if __name__ == "__main__":
    main()
