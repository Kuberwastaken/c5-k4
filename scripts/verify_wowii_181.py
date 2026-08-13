#!/usr/bin/env python3
"""Independent exact verifier for the T(7)=L(K7) disproof of WOWII 181.

The accepted reading takes the periphery of G^2 and measures degrees there,
in G^2.  The alternate audit measures those same vertices' degrees in G.
All optimization is finite subset enumeration; no ILP or certificate code is
imported.
"""

from __future__ import annotations

import itertools
import signal
import time
from collections import Counter
from fractions import Fraction
from math import comb

import networkx as nx


TIME_LIMIT_SECONDS = 60.0
ALPHA_WITNESS = frozenset({0, 11, 18})       # K7 edges 01, 23, 45
BIPARTITE_WITNESS = frozenset({0, 1, 7, 11, 18, 19})
CONNECTED_DOMINATING_WITNESS = frozenset({0, 1, 2, 3, 4})


class VerificationTimeout(RuntimeError):
    pass


def _timeout(_signum: int, _frame: object) -> None:
    raise VerificationTimeout(f"WOWII 181 verification exceeded {TIME_LIMIT_SECONDS:g}s")


def triangular_graph(base_order: int = 7) -> tuple[nx.Graph, tuple[tuple[int, int], ...]]:
    """Construct L(K_base_order) directly from the edges of K_base_order."""

    labels = tuple(itertools.combinations(range(base_order), 2))
    graph = nx.Graph()
    graph.add_nodes_from(range(len(labels)))
    for left, right in itertools.combinations(range(len(labels)), 2):
        if set(labels[left]) & set(labels[right]):
            graph.add_edge(left, right)
    return graph, labels


def is_independent(graph: nx.Graph, selected: frozenset[int]) -> bool:
    return graph.subgraph(selected).number_of_edges() == 0


def independence_number(graph: nx.Graph) -> tuple[int, frozenset[int], int]:
    vertices = tuple(graph)
    tested = 0
    for size in range(len(vertices), -1, -1):
        for subset in itertools.combinations(vertices, size):
            tested += 1
            selected = frozenset(subset)
            if is_independent(graph, selected):
                return size, selected, tested
    raise AssertionError("empty set must be independent")


def bipartite_number(graph: nx.Graph) -> tuple[int, frozenset[int], int]:
    vertices = tuple(graph)
    tested = 0
    for size in range(len(vertices), -1, -1):
        for subset in itertools.combinations(vertices, size):
            tested += 1
            selected = frozenset(subset)
            if nx.is_bipartite(graph.subgraph(selected)):
                return size, selected, tested
    raise AssertionError("empty graph must be bipartite")


def is_connected_dominating(graph: nx.Graph, selected: frozenset[int]) -> bool:
    if not selected or not nx.is_connected(graph.subgraph(selected)):
        return False
    return all(
        vertex in selected or any(neighbor in selected for neighbor in graph.neighbors(vertex))
        for vertex in graph
    )


def connected_domination_number(graph: nx.Graph) -> tuple[int, frozenset[int], int]:
    vertices = tuple(graph)
    tested = 0
    for size in range(1, len(vertices) + 1):
        for subset in itertools.combinations(vertices, size):
            tested += 1
            selected = frozenset(subset)
            if is_connected_dominating(graph, selected):
                return size, selected, tested
    raise AssertionError("connected graph itself must be connected dominating")


def square_periphery_averages(graph: nx.Graph) -> tuple[nx.Graph, frozenset[int], Fraction, Fraction]:
    """Average square degree and alternate original-graph degree on B(G^2)."""

    square = nx.power(graph, 2)
    eccentricities = nx.eccentricity(square)
    maximum = max(eccentricities.values())
    periphery = frozenset(vertex for vertex, value in eccentricities.items() if value == maximum)
    square_average = Fraction(sum(square.degree(vertex) for vertex in periphery), len(periphery))
    graph_average = Fraction(sum(graph.degree(vertex) for vertex in periphery), len(periphery))
    return square, periphery, square_average, graph_average


def spanning_tree_from_connected_dominating(
    graph: nx.Graph, selected: frozenset[int]
) -> nx.Graph:
    """Build a spanning tree whose internal set is the supplied CDS."""

    induced = graph.subgraph(selected)
    tree = nx.minimum_spanning_tree(induced)
    assert set(tree) == set(selected) and nx.is_tree(tree)
    for vertex in graph:
        if vertex in selected:
            continue
        parent = next(neighbor for neighbor in graph.neighbors(vertex) if neighbor in selected)
        tree.add_edge(vertex, parent)
    return tree


def atlas_gate() -> tuple[int, Counter[Fraction], Counter[Fraction]]:
    """Check both readings on every connected Atlas graph of order 2..7."""

    count = 0
    accepted_slacks: Counter[Fraction] = Counter()
    alternate_slacks: Counter[Fraction] = Counter()
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() < 2 or not nx.is_connected(graph):
            continue
        count += 1
        alpha, _, _ = independence_number(graph)
        bipartite, _, _ = bipartite_number(graph)
        gamma_c, _, _ = connected_domination_number(graph)
        leaves = graph.number_of_nodes() - gamma_c
        _, _, accepted_average, alternate_average = square_periphery_averages(graph)
        common = Fraction(leaves + bipartite - alpha)
        accepted_slack = common - accepted_average
        alternate_slack = common - alternate_average
        assert accepted_slack >= 0, (
            "accepted-reading Atlas violation",
            nx.to_graph6_bytes(graph, header=False).decode().strip(),
            accepted_slack,
        )
        assert alternate_slack >= 0, (
            "alternate-reading Atlas violation",
            nx.to_graph6_bytes(graph, header=False).decode().strip(),
            alternate_slack,
        )
        accepted_slacks[accepted_slack] += 1
        alternate_slacks[alternate_slack] += 1
    return count, accepted_slacks, alternate_slacks


def verify_t7() -> tuple[int, int, int]:
    graph, labels = triangular_graph()
    assert len(labels) == comb(7, 2) == 21
    assert graph.number_of_nodes() == 21
    assert graph.number_of_edges() == 105
    assert nx.is_connected(graph)
    assert nx.diameter(graph) == 2
    assert set(dict(graph.degree()).values()) == {10}

    # Independent witness plus exhaustive rejection of every 4-subset.  Any
    # larger independent set would contain an independent 4-subset.
    assert {labels[index] for index in ALPHA_WITNESS} == {(0, 1), (2, 3), (4, 5)}
    assert is_independent(graph, ALPHA_WITNESS)
    rejected_alpha = 0
    for subset in itertools.combinations(tuple(graph), 4):
        rejected_alpha += 1
        assert not is_independent(graph, frozenset(subset))
    alpha = len(ALPHA_WITNESS)
    assert alpha == 3
    assert rejected_alpha == comb(21, 4) == 5_985

    # Bipartite witness plus exhaustive rejection of all 7-subsets.  Any
    # larger bipartite induced graph would contain a bipartite 7-subset.
    assert nx.is_bipartite(graph.subgraph(BIPARTITE_WITNESS))
    rejected_bipartite = 0
    for subset in itertools.combinations(tuple(graph), 7):
        rejected_bipartite += 1
        assert not nx.is_bipartite(graph.subgraph(subset))
    bipartite = len(BIPARTITE_WITNESS)
    assert bipartite == 6
    assert rejected_bipartite == comb(21, 7) == 116_280

    # Connected-domination witness plus exhaustive rejection below size 5.
    assert {labels[index] for index in CONNECTED_DOMINATING_WITNESS} == {
        (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)
    }
    assert is_connected_dominating(graph, CONNECTED_DOMINATING_WITNESS)
    rejected_connected_domination = 0
    for size in range(1, 5):
        for subset in itertools.combinations(tuple(graph), size):
            rejected_connected_domination += 1
            assert not is_connected_dominating(graph, frozenset(subset))
    gamma_c = len(CONNECTED_DOMINATING_WITNESS)
    assert gamma_c == 5
    assert rejected_connected_domination == sum(comb(21, size) for size in range(1, 5)) == 7_546
    leaves = graph.number_of_nodes() - gamma_c
    assert leaves == 16
    spanning_tree = spanning_tree_from_connected_dominating(
        graph, CONNECTED_DOMINATING_WITNESS
    )
    assert set(spanning_tree) == set(graph)
    assert nx.is_tree(spanning_tree)
    leaf_set = frozenset(vertex for vertex, degree in spanning_tree.degree() if degree == 1)
    assert leaf_set == frozenset(graph) - CONNECTED_DOMINATING_WITNESS
    assert len(leaf_set) == leaves

    square, periphery, accepted_average, alternate_average = square_periphery_averages(graph)
    assert periphery == frozenset(graph)
    assert square.number_of_edges() == comb(21, 2)
    assert all(square.has_edge(left, right) for left, right in itertools.combinations(graph, 2))
    assert accepted_average == 20
    assert alternate_average == 10

    lhs = leaves + bipartite
    accepted_rhs = alpha + accepted_average
    alternate_rhs = alpha + alternate_average
    assert lhs == 22
    assert accepted_rhs == 23
    assert lhs < accepted_rhs
    assert alternate_rhs == 13
    assert lhs >= alternate_rhs
    assert lhs - alternate_rhs == 9
    return rejected_alpha, rejected_bipartite, rejected_connected_domination


def main() -> None:
    started = time.monotonic()
    old_handler = signal.signal(signal.SIGALRM, _timeout)
    signal.setitimer(signal.ITIMER_REAL, TIME_LIMIT_SECONDS)
    try:
        rejected_alpha, rejected_bipartite, rejected_connected_domination = verify_t7()
        atlas_count, accepted_slacks, alternate_slacks = atlas_gate()
        assert atlas_count == 995
        assert sum(accepted_slacks.values()) == atlas_count
        assert sum(alternate_slacks.values()) == atlas_count
        assert min(accepted_slacks) == 0
        assert accepted_slacks[Fraction(0)] == 22
        assert min(alternate_slacks) == 1
        assert alternate_slacks[Fraction(1)] == 6
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)

    elapsed = time.monotonic() - started
    assert elapsed < TIME_LIMIT_SECONDS
    print(f"PASS WOWII 181 exact verifier ({elapsed:.3f}s; cap {TIME_LIMIT_SECONDS:g}s)")
    print("T(7)=L(K7): n=21, m=105, connected, 10-regular, diameter=2")
    print(
        f"alpha=3 ({rejected_alpha} four-subsets rejected); "
        f"b=6 ({rejected_bipartite} seven-subsets rejected)"
    )
    print(
        "gamma_c=5 "
        f"({rejected_connected_domination} smaller nonempty subsets rejected), hence Ls=16"
    )
    print("G^2=K21; B(G^2)=V; accepted square-degree average=20")
    print("accepted reading refuted: Ls+b=22 < 23=alpha+20")
    print("alternate in-G degree reading safe on T(7): 22 >= 13 (slack 9)")
    print("Atlas gate: 995 connected order-2..7 graphs, 0 violations on either reading")
    print("accepted reading has 22 equalities; alternate reading minimum slack 1 (6 graphs)")


if __name__ == "__main__":
    main()
