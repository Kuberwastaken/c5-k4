#!/usr/bin/env python3
"""Exact verifier for the dumbbell-family disproof of WOWII 176."""

from itertools import combinations
import networkx as nx


def dumbbell(length: int) -> nx.Graph:
    """Two triangles joined at distinguished vertices by a length-edge path."""
    graph = nx.Graph()
    path = list(range(length + 1))
    graph.add_edges_from(zip(path, path[1:]))
    graph.add_edges_from(((path[0], length + 1), (path[0], length + 2),
                          (length + 1, length + 2)))
    graph.add_edges_from(((path[-1], length + 3), (path[-1], length + 4),
                          (length + 3, length + 4)))
    return graph


def bipartite_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(len(vertices), 0, -1):
        if any(nx.is_bipartite(graph.subgraph(s)) for s in combinations(vertices, size)):
            return size
    raise AssertionError


def connected_domination_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(1, len(vertices) + 1):
        for chosen in combinations(vertices, size):
            selected = set(chosen)
            if size > 1 and not nx.is_connected(graph.subgraph(selected)):
                continue
            if all(v in selected or any(u in selected for u in graph.neighbors(v)) for v in graph):
                return size
    raise AssertionError


def square_max_set_and_distances(graph: nx.Graph) -> tuple[set[int], int, int]:
    square = nx.power(graph, 2)
    degrees = dict(square.degree())
    maximum = max(degrees.values())
    selected = {v for v, degree in degrees.items() if degree == maximum}
    pairs = tuple(combinations(selected, 2))
    if not pairs:
        return selected, 0, 0
    in_graph = min(nx.shortest_path_length(graph, u, v) for u, v in pairs)
    in_square = min(nx.shortest_path_length(square, u, v) for u, v in pairs)
    return selected, in_graph, in_square


def check_conjecture(graph: nx.Graph, square_reading: bool = False) -> bool:
    n = graph.number_of_nodes()
    leaves = n - connected_domination_number(graph)
    b = bipartite_number(graph)
    _, in_graph, in_square = square_max_set_and_distances(graph)
    return leaves + b >= n + (in_square if square_reading else in_graph)


def main() -> None:
    atlas = [g for g in nx.graph_atlas_g() if 2 <= len(g) <= 7 and nx.is_connected(g)]
    assert all(check_conjecture(g) for g in atlas)
    assert all(check_conjecture(g, square_reading=True) for g in atlas)

    for length in range(5, 13):
        graph = dumbbell(length)
        n = length + 5
        b = bipartite_number(graph)
        gamma_c = connected_domination_number(graph)
        leaves = n - gamma_c
        maximum_set, distance_g, distance_square = square_max_set_and_distances(graph)
        assert (n, b, gamma_c, leaves) == (length + 5, length + 3, length + 1, 4)
        assert maximum_set == {1, length - 1}
        assert distance_g == length - 2
        assert distance_square == (length - 1) // 2
        assert leaves + b < n + distance_g
        assert (leaves + b < n + distance_square) == (length >= 7)

    print(f"atlas gate: {len(atlas)} connected graphs on 2..7 vertices, both readings hold")
    print("D_L, L=5..12: exact subset computations match closed forms")
    print("published in-G reading fails for every L>=5; all-in-G^2 reading fails for L>=7")
    print(f"smallest ambiguity-free witness D_7: {nx.to_graph6_bytes(dumbbell(7), header=False).decode().strip()}")


if __name__ == "__main__":
    main()
