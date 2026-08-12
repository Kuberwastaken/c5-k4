#!/usr/bin/env python3
"""Independent exact verifier for the C5[K4] disproof of WOWII 309.

The verifier reconstructs the graph, uses finite enumeration only, audits all
six recorded readings, and checks the source reading on every applicable
connected Graph Atlas graph.  It imports no discovery or certificate code.
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
TOTAL_DOMINATING_WITNESS = frozenset({0, 4, 8})


class VerificationTimeout(RuntimeError):
    pass


def _timeout(_signum: int, _frame: object) -> None:
    raise VerificationTimeout(f"WOWII 309 verification exceeded {TIME_LIMIT_SECONDS:g}s")


def c5_clique_blowup(blob_size: int = 4) -> nx.Graph:
    """Construct C5[K_blob_size] directly, with consecutive integer labels."""

    graph = nx.Graph()
    blobs = [tuple(range(index * blob_size, (index + 1) * blob_size)) for index in range(5)]
    graph.add_nodes_from(itertools.chain.from_iterable(blobs))
    for blob in blobs:
        graph.add_edges_from(itertools.combinations(blob, 2))
    for index in range(5):
        graph.add_edges_from(itertools.product(blobs[index], blobs[(index + 1) % 5]))
    return graph


def is_total_dominating(
    graph: nx.Graph, selected: frozenset[int]
) -> bool:
    """Every vertex, including selected vertices, has a selected neighbor."""

    return all(any(neighbor in selected for neighbor in graph.neighbors(vertex)) for vertex in graph)


def total_domination_number(graph: nx.Graph) -> int:
    vertices = tuple(graph)
    for size in range(1, len(vertices) + 1):
        for subset in itertools.combinations(vertices, size):
            if is_total_dominating(graph, frozenset(subset)):
                return size
    raise AssertionError("connected nontrivial graph has no total dominating set")


def distance_audit(graph: nx.Graph) -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    """Return dist-even counts with/without self and even-horizontal counts."""

    including_self: dict[int, int] = {}
    excluding_self: dict[int, int] = {}
    even_horizontal: dict[int, int] = {}
    for vertex in graph:
        distances = nx.single_source_shortest_path_length(graph, vertex)
        assert len(distances) == graph.number_of_nodes()
        including_self[vertex] = sum(distance % 2 == 0 for distance in distances.values())
        excluding_self[vertex] = including_self[vertex] - 1
        even_horizontal[vertex] = sum(
            distances[left] == distances[right] and distances[left] % 2 == 0
            for left, right in graph.edges()
        )
    return including_self, excluding_self, even_horizontal


def neighborhood_readings(graph: nx.Graph) -> tuple[list[int], list[int], list[int]]:
    """Evaluate the three recorded readings of the final neighborhood term.

    The lists range over the same unordered nonedges of G (edges of bar(G)):
    N_G(nonedge), N_barG(edge) with endpoints removed, and the literal union
    of open complement neighborhoods (which includes the adjacent endpoints).
    """

    complement = nx.complement(graph)
    in_graph: list[int] = []
    in_complement_excluding_endpoints: list[int] = []
    in_complement_including_endpoints: list[int] = []
    for left, right in complement.edges():
        graph_union = set(graph.neighbors(left)) | set(graph.neighbors(right))
        complement_union = set(complement.neighbors(left)) | set(complement.neighbors(right))
        in_graph.append(len(graph_union))
        in_complement_excluding_endpoints.append(len(complement_union - {left, right}))
        in_complement_including_endpoints.append(len(complement_union))
    return in_graph, in_complement_excluding_endpoints, in_complement_including_endpoints


def source_terms(graph: nx.Graph) -> tuple[int, int | None]:
    """Maximum correction and chosen complement-neighborhood minimum.

    The source reading counts the base vertex in dist_even and takes the union
    of open neighborhoods in bar(G).  For a complement edge, that union
    contains both endpoints.  A complete graph has no minimum and returns None.
    """

    dist_even, _, horizontal = distance_audit(graph)
    correction = max(dist_even[vertex] - horizontal[vertex] for vertex in graph)
    _, _, complement_including = neighborhood_readings(graph)
    minimum = min(complement_including) if complement_including else None
    return correction, minimum


def atlas_gate() -> tuple[int, int, int, Counter[Fraction]]:
    """Check the chosen source reading on connected Atlas graphs of order >2."""

    connected = 0
    applicable = 0
    undefined_complete = 0
    slacks: Counter[Fraction] = Counter()
    for graph in nx.graph_atlas_g():
        if graph.number_of_nodes() <= 2 or not nx.is_connected(graph):
            continue
        connected += 1
        correction, minimum = source_terms(graph)
        if minimum is None:
            # Exactly K3,...,K7: the complement-edge minimum is undefined.
            undefined_complete += 1
            continue
        applicable += 1
        gamma_t = total_domination_number(graph)
        rhs = Fraction(correction + minimum, 2)
        slack = rhs - gamma_t
        assert slack >= 0, (
            "Atlas sanity-gate violation",
            nx.to_graph6_bytes(graph, header=False).decode().strip(),
            gamma_t,
            rhs,
        )
        slacks[slack] += 1
    return connected, applicable, undefined_complete, slacks


def verify_carrier() -> tuple[list[Fraction], int]:
    graph = c5_clique_blowup()
    assert graph.number_of_nodes() == 20
    assert graph.number_of_edges() == 110
    assert nx.is_connected(graph)
    assert set(dict(graph.degree()).values()) == {11}

    # Explicit upper bound and exhaustive lower bound for gamma_t=3.
    assert is_total_dominating(graph, TOTAL_DOMINATING_WITNESS)
    lower_subsets = 0
    for size in range(3):
        for subset in itertools.combinations(tuple(graph), size):
            lower_subsets += 1
            assert not is_total_dominating(graph, frozenset(subset))
    assert lower_subsets == 1 + 20 + comb(20, 2) == 211
    gamma_t = total_domination_number(graph)
    assert gamma_t == 3

    dist_including, dist_excluding, horizontal = distance_audit(graph)
    assert set(dist_including.values()) == {9}
    assert set(dist_excluding.values()) == {8}
    assert set(horizontal.values()) == {28}

    n_graph, n_complement_excluding, n_complement_including = neighborhood_readings(graph)
    assert len(n_graph) == len(n_complement_excluding) == len(n_complement_including) == 80
    assert set(n_graph) == {18}
    assert set(n_complement_excluding) == {14}
    assert set(n_complement_including) == {16}

    readings: list[Fraction] = []
    for dist_even in (9, 8):
        correction = dist_even - 28
        for neighborhood_minimum in (18, 14, 16):
            rhs = Fraction(correction + neighborhood_minimum, 2)
            readings.append(rhs)
            assert gamma_t > rhs
    assert readings == [
        Fraction(-1, 2),
        Fraction(-5, 2),
        Fraction(-3, 2),
        Fraction(-1, 1),
        Fraction(-3, 1),
        Fraction(-2, 1),
    ]

    source_correction, source_minimum = source_terms(graph)
    assert source_correction == -19
    assert source_minimum == 16
    assert Fraction(source_correction + source_minimum, 2) == Fraction(-3, 2)
    return readings, lower_subsets


def main() -> None:
    started = time.monotonic()
    old_handler = signal.signal(signal.SIGALRM, _timeout)
    signal.setitimer(signal.ITIMER_REAL, TIME_LIMIT_SECONDS)
    try:
        readings, lower_subsets = verify_carrier()
        connected, applicable, undefined, slacks = atlas_gate()
        assert (connected, applicable, undefined) == (994, 989, 5)
        assert sum(slacks.values()) == applicable
        assert min(slacks) == 0
        assert slacks[Fraction(0)] == 36
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)

    elapsed = time.monotonic() - started
    assert elapsed < TIME_LIMIT_SECONDS
    rendered = ", ".join(str(value) for value in readings)
    print(f"PASS WOWII 309 exact verifier ({elapsed:.3f}s; cap {TIME_LIMIT_SECONDS:g}s)")
    print(
        "C5[K4]: n=20, m=110, connected and 11-regular; "
        f"gamma_t=3 via {sorted(TOTAL_DOMINATING_WITNESS)}, {lower_subsets} smaller subsets rejected"
    )
    print("all 20 vertices: dist_even=9 (8 excluding self), even_horizontal=28")
    print(
        "six RHS readings all fail "
        f"([N_G(nonedge), N_bar-excl, N_bar-incl], self then no-self): [{rendered}]; "
        "chosen source RHS=-3/2"
    )
    print(
        f"Atlas gate: {applicable}/{connected} connected order-3..7 graphs applicable, "
        f"{undefined} complete undefined, 0 violations ({slacks[Fraction(0)]} equalities)"
    )


if __name__ == "__main__":
    main()
