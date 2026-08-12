#!/usr/bin/env python3
"""Exact independent verification of the resolved TxGraffiti C-D statement.

C-D conjectured that the saturation number (minimum size of a maximal
matching) is at most the harmonic index for every nontrivial connected graph.
The friendship graph F_4 is a published counterexample.  This verifier uses
exact rational arithmetic and two independent saturation-number algorithms.
"""

from fractions import Fraction
from itertools import combinations

import networkx as nx


def harmonic_index(graph: nx.Graph) -> Fraction:
    return sum(
        (Fraction(2, graph.degree[u] + graph.degree[v]) for u, v in graph.edges),
        Fraction(),
    )


def is_maximal_matching(graph: nx.Graph, edges: tuple[tuple[int, int], ...]) -> bool:
    covered = {vertex for edge in edges for vertex in edge}
    if len(covered) != 2 * len(edges):
        return False
    return all(u in covered or v in covered for u, v in graph.edges)


def saturation_by_edge_subsets(graph: nx.Graph) -> int:
    """Bottom-up exhaustive enumeration of matchings."""
    edges = tuple(graph.edges)
    for size in range(1, graph.number_of_nodes() // 2 + 1):
        if any(is_maximal_matching(graph, chosen) for chosen in combinations(edges, size)):
            return size
    raise AssertionError("nontrivial graph has no maximal matching")


def has_perfect_matching(graph: nx.Graph) -> bool:
    if graph.number_of_nodes() % 2:
        return False
    matching = nx.algorithms.matching.max_weight_matching(graph, maxcardinality=True)
    return 2 * len(matching) == graph.number_of_nodes()


def saturation_by_unmatched_sets(graph: nx.Graph) -> int:
    """Use: M maximal iff its unmatched vertices form an independent set."""
    vertices = tuple(graph.nodes)
    for unmatched_size in range(graph.number_of_nodes(), -1, -1):
        if unmatched_size % 2 != graph.number_of_nodes() % 2:
            continue
        for unmatched in combinations(vertices, unmatched_size):
            if graph.subgraph(unmatched).number_of_edges() != 0:
                continue
            remainder = graph.subgraph(set(vertices) - set(unmatched))
            if has_perfect_matching(remainder):
                return (graph.number_of_nodes() - unmatched_size) // 2
    raise AssertionError("failed to recover a maximal matching")


def friendship(blades: int) -> nx.Graph:
    graph = nx.Graph()
    hub = 2 * blades
    for blade in range(blades):
        a, b = 2 * blade, 2 * blade + 1
        graph.add_edges_from(((a, b), (hub, a), (hub, b)))
    return graph


def named_gate_graphs() -> list[tuple[str, nx.Graph]]:
    graphs: list[tuple[str, nx.Graph]] = []
    graphs.extend((f"C{n}", nx.cycle_graph(n)) for n in range(5, 10))
    graphs.extend(
        [
            ("P7", nx.path_graph(7)),
            ("Petersen", nx.petersen_graph()),
            ("K3,3", nx.complete_bipartite_graph(3, 3)),
            ("K7", nx.complete_graph(7)),
        ]
    )
    graphs.extend((f"K1,{n}", nx.star_graph(n)) for n in range(2, 8))
    graphs.extend(
        (f"K{a},{b}", nx.complete_bipartite_graph(a, b))
        for a in range(2, 5)
        for b in range(a, 6)
    )
    return graphs


def verify(graph: nx.Graph) -> tuple[int, Fraction]:
    first = saturation_by_edge_subsets(graph)
    second = saturation_by_unmatched_sets(graph)
    assert first == second
    return first, harmonic_index(graph)


def main() -> None:
    atlas = [
        graph
        for graph in nx.graph_atlas_g()
        if 2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph)
    ]
    for graph in atlas:
        saturation, harmonic = verify(graph)
        assert Fraction(saturation) <= harmonic

    for name, graph in named_gate_graphs():
        saturation, harmonic = verify(graph)
        assert Fraction(saturation) <= harmonic, (name, saturation, harmonic)

    counterexample = friendship(4)
    saturation, harmonic = verify(counterexample)
    assert counterexample.number_of_nodes() == 9
    assert nx.is_connected(counterexample)
    assert saturation == 4
    assert harmonic == Fraction(18, 5)
    assert Fraction(saturation) > harmonic

    print(f"atlas gate: {len(atlas)} connected graphs on 2..7 vertices, all hold")
    print(f"named gate: {len(named_gate_graphs())} graphs, all hold")
    print(f"F4: mu*={saturation} > H={harmonic} (gap={Fraction(saturation)-harmonic})")
    print("two independent saturation-number computations agree throughout")


if __name__ == "__main__":
    main()
