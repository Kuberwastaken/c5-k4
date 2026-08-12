#!/usr/bin/env python3
"""Independent checks for the bounded Method v0.1 barbell trial.

The discovery program uses bit-mask optimizers and a custom graph-square
constructor.  This verifier uses NetworkX induced subgraphs, set operations,
and ``nx.power`` on the historical controls, then checks the closed forms of
the entire preregistered endpoint-clique grid.
"""

from itertools import combinations

import networkx as nx

from search_method_v01_barbell import (
    endpoint_clique_barbell,
    profile,
)


def slow_connected_domination_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(1, len(vertices) + 1):
        for chosen in combinations(vertices, size):
            selected = set(chosen)
            if size > 1 and not nx.is_connected(graph.subgraph(selected)):
                continue
            dominated = selected | {
                neighbor for vertex in selected for neighbor in graph.neighbors(vertex)
            }
            if dominated == set(vertices):
                return size
    raise AssertionError


def slow_bipartite_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(len(vertices), -1, -1):
        for chosen in combinations(vertices, size):
            if nx.is_bipartite(graph.subgraph(chosen)):
                return size
    raise AssertionError


def slow_independence_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(len(vertices), -1, -1):
        for chosen in combinations(vertices, size):
            if graph.subgraph(chosen).number_of_edges() == 0:
                return size
    raise AssertionError


def slow_lambda_max(graph: nx.Graph) -> int:
    return max(slow_independence_number(graph.subgraph(tuple(graph.neighbors(v))))
               for v in graph)


def slow_values(graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    n = len(graph)
    gamma_c = slow_connected_domination_number(graph)
    leaves = n if n == 2 else n - gamma_c
    b = slow_bipartite_number(graph)
    alpha = slow_independence_number(graph)
    local = slow_lambda_max(graph)
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    evens = [sum(d % 2 == 0 for d in distances[v].values()) for v in graph]
    square = nx.power(graph, 2)
    eccentricities = nx.eccentricity(square)
    maximum_eccentricity = max(eccentricities.values())
    boundary = {v for v, value in eccentricities.items() if value == maximum_eccentricity}
    delta_square = max(square.degree(v) for v in boundary)
    delta_graph = max(graph.degree(v) for v in boundary)
    diameter = nx.diameter(graph)
    return {
        "gamma_c": gamma_c,
        "Ls": leaves,
        "b": b,
        "alpha": alpha,
        "lambda_max": local,
        "even_min_self": min(evens),
        "even_max_self": max(evens),
        "diameter": diameter,
        "square_periphery": tuple(sorted(boundary)),
        "delta_B_square_in_square": delta_square,
        "delta_B_square_in_graph": delta_graph,
    }


def check_fast_against_slow() -> int:
    graphs = [
        graph for graph in nx.graph_atlas_g()
        if 2 <= len(graph) <= 7 and nx.is_connected(graph)
    ]
    fields = tuple(slow_values(nx.path_graph(2)))
    for index, graph in enumerate(graphs):
        fast = profile(graph, f"atlas_validation_{index}")
        slow = slow_values(graph)
        for field in fields:
            assert getattr(fast, field) == slow[field], (index, field, getattr(fast, field), slow[field])
        decoded = nx.from_graph6_bytes(fast.graph6.encode())
        assert nx.is_isomorphic(graph, decoded)
    return len(graphs)


def check_endpoint_closed_forms() -> int:
    checked = 0
    for length in range(2, 11):
        for left in range(2, 6):
            for right in range(left, 6):
                item = profile(endpoint_clique_barbell(length, left, right),
                               f"K{left}-P{length}-K{right}")
                assert item.n == length + left + right - 1
                assert item.gamma_c == length + 1
                assert item.Ls == left + right - 2
                assert item.b == length + 3
                assert item.alpha == length // 2 + 2
                assert item.lambda_max == 2
                assert item.diameter == length + 2
                assert item.R174 == 1
                expected_parity_residual = 0 if length % 2 == 0 else left - 1
                assert item.R169 == expected_parity_residual
                assert item.R180_self == expected_parity_residual
                assert item.R180_without_self == expected_parity_residual + 1
                expected_square_residual = left - 2 if length % 2 == 0 else left - 1
                assert item.R182_square == expected_square_residual
                assert item.R182_graph == expected_square_residual + 1
                checked += 1
    return checked


def main() -> None:
    atlas_count = check_fast_against_slow()
    endpoint_count = check_endpoint_closed_forms()
    print(f"independent slow-path agreement: {atlas_count} connected Atlas graphs")
    print(f"endpoint closed forms: {endpoint_count} preregistered members")
    print("graph6 round trips: all Atlas controls")


if __name__ == "__main__":
    main()
