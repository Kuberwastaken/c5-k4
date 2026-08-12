#!/usr/bin/env python3
"""Executable certificate and DB-sanity gate for WoW I #724."""

import math

import networkx as nx
import numpy as np

EPS = 1e-6


def h_graph(m: int) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(5 * m))
    for u in graph:
        for v in range(u + 1, 5 * m):
            a, b = u // m, v // m
            if a != b and (a - b) % 5 in (2, 3):
                graph.add_edge(u, v)
    return graph


def independence_number(graph: nx.Graph) -> int:
    return max(map(len, nx.find_cliques(nx.complement(graph))))


def value(graph: nx.Graph):
    eigenvalues = np.linalg.eigvalsh(nx.to_numpy_array(graph, dtype=float))
    nonnegative = int(np.sum(eigenvalues >= -EPS))
    nonnegative_values = eigenvalues[eigenvalues >= -EPS]
    smallest_nonnegative = float(min(nonnegative_values, key=abs))
    lhs = nonnegative - float(eigenvalues[-1]) + smallest_nonnegative
    return lhs, independence_number(graph), eigenvalues, nonnegative


def check_family() -> None:
    for m in range(1, 9):
        graph = h_graph(m)
        lhs, alpha, eigenvalues, nonnegative = value(graph)
        assert nx.is_connected(graph)
        assert nx.is_regular(graph)
        assert sum(nx.triangles(graph).values()) == 0
        assert graph.number_of_nodes() == 5 * m
        assert graph.number_of_edges() == 5 * m * m
        assert alpha == 2 * m
        assert nonnegative == 5 * m - 2
        if m >= 2:
            assert abs(lhs - (3 * m - 2)) < EPS

        expected = sorted(
            [2 * m]
            + [((math.sqrt(5) - 1) * m / 2)] * 2
            + [0.0] * (5 * m - 5)
            + [(-((math.sqrt(5) + 1) * m / 2))] * 2
        )
        assert np.allclose(eigenvalues, expected, atol=EPS, rtol=0)
        assert (lhs > alpha + EPS) == (m >= 3)


def named_graphs():
    yield from ((f"C{n}", nx.cycle_graph(n)) for n in range(5, 10))
    yield "P7", nx.path_graph(7)
    yield "Petersen", nx.petersen_graph()
    yield "K3,3", nx.complete_bipartite_graph(3, 3)
    yield "K7", nx.complete_graph(7)
    yield from ((f"S{n}", nx.star_graph(n - 1)) for n in range(3, 9))
    yield from ((f"K2,{n}", nx.complete_bipartite_graph(2, n)) for n in range(2, 8))


def check_gate() -> tuple[int, int]:
    atlas = [g for g in nx.graph_atlas_g() if g and nx.is_connected(g)]
    for graph in atlas:
        lhs, alpha, _, _ = value(graph)
        assert lhs <= alpha + EPS
    named = list(named_graphs())
    for name, graph in named:
        lhs, alpha, _, _ = value(graph)
        assert lhs <= alpha + EPS, name
    return len(atlas), len(named)


if __name__ == "__main__":
    check_family()
    atlas_count, named_count = check_gate()
    lhs, alpha, _, nonnegative = value(h_graph(4))
    print("WoW I #724 certificate: PASS")
    print(f"H_4: nonnegative={nonnegative}, lhs={lhs:.12g}, alpha={alpha}")
    print(f"DB-sanity: {atlas_count} connected Atlas + {named_count} named graphs")
