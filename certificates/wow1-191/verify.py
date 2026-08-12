#!/usr/bin/env python3
"""Exact, dependency-free certificate for the WoW-I #191 counterexample."""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from typing import Iterable


Graph = tuple[frozenset[int], ...]


def triangular_graph(q: int) -> tuple[Graph, tuple[tuple[int, int], ...]]:
    """Construct T(q) = L(K_q), with vertices represented by edges of K_q."""
    if q < 3:
        raise ValueError("q must be at least 3")
    labels = tuple(itertools.combinations(range(q), 2))
    adjacency = tuple(
        frozenset(j for j, other in enumerate(labels) if i != j and set(edge) & set(other))
        for i, edge in enumerate(labels)
    )
    return adjacency, labels


def distances(graph: Graph, source: int) -> tuple[int, ...]:
    result = [-1] * len(graph)
    result[source] = 0
    queue = [source]
    for vertex in queue:
        for neighbor in graph[vertex]:
            if result[neighbor] == -1:
                result[neighbor] = result[vertex] + 1
                queue.append(neighbor)
    assert all(distance >= 0 for distance in result), "graph must be connected"
    return tuple(result)


def parity_coordinates(graph: Graph) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return WoW Odd and Even coordinates; distance zero is even."""
    odd: list[int] = []
    even: list[int] = []
    for vertex in range(len(graph)):
        distance = distances(graph, vertex)
        odd.append(sum(value % 2 == 1 for value in distance))
        even.append(sum(value % 2 == 0 for value in distance))
    return tuple(odd), tuple(even)


def vertex_deficiency(graph: Graph, vertex: int) -> int:
    """Count nonedges in the subgraph induced by the neighbors of vertex."""
    neighbors = sorted(graph[vertex])
    return sum(v not in graph[u] for u, v in itertools.combinations(neighbors, 2))


def maximum_clique(graph: Graph) -> tuple[int, ...]:
    """Exact deterministic Bron--Kerbosch maximum clique search."""
    neighbor_masks = tuple(sum(1 << v for v in neighbors) for neighbors in graph)
    best = 0

    def popcount(mask: int) -> int:
        # int.bit_count was added in Python 3.10; this spelling keeps the
        # certificate portable to older Python 3.
        return bin(mask).count("1")

    def visit(r: int, p: int, x: int) -> None:
        nonlocal best
        if popcount(r) + popcount(p) <= popcount(best):
            return
        if p == 0 and x == 0:
            if popcount(r) > popcount(best):
                best = r
            return
        union = p | x
        pivot = max(
            (u for u in range(len(graph)) if union & (1 << u)),
            key=lambda u: popcount(p & neighbor_masks[u]),
            default=0,
        )
        candidates = p & ~neighbor_masks[pivot]
        while candidates:
            bit = candidates & -candidates
            vertex = bit.bit_length() - 1
            visit(r | bit, p & neighbor_masks[vertex], x & neighbor_masks[vertex])
            p &= ~bit
            x |= bit
            candidates &= ~bit

    visit(0, (1 << len(graph)) - 1, 0)
    return tuple(vertex for vertex in range(len(graph)) if best & (1 << vertex))


def expected(q: int) -> dict[str, int]:
    """Closed forms for T(q), using q rather than its graph order."""
    return {
        "order": q * (q - 1) // 2,
        "degree": 2 * (q - 2),
        "size": q * (q - 1) * (q - 2) // 2,
        # T(3) is the exceptional K_3; the q-1 formula applies from q=4.
        "clique_number": max(3, q - 1),
        "minimum_deficiency": (q - 2) * (q - 3),
        "odd_coordinate": 2 * (q - 2),
        "even_coordinate": q * (q - 1) // 2 - 2 * (q - 2),
    }


def evaluate(q: int) -> dict[str, object]:
    graph, labels = triangular_graph(q)
    degrees = tuple(map(len, graph))
    size = sum(degrees) // 2
    clique_vertices = maximum_clique(graph)
    deficiencies = tuple(vertex_deficiency(graph, vertex) for vertex in range(len(graph)))
    odd, even = parity_coordinates(graph)
    values = {
        "order": len(graph),
        "degree": min(degrees),
        "size": size,
        "clique_number": len(clique_vertices),
        "minimum_deficiency": min(deficiencies),
        "odd_coordinate": min(odd),
        "even_coordinate": min(even),
    }
    assert len(set(degrees)) == len(set(deficiencies)) == len(set(odd)) == len(set(even)) == 1
    assert values == expected(q)
    rhs = Fraction(size, len(clique_vertices))
    return {
        "q": q,
        **values,
        "clique_witness": [list(labels[vertex]) for vertex in clique_vertices],
        "sum_odd": sum(odd),
        "sum_even": sum(even),
        "hypothesis_sum_odd_lt_sum_even": sum(odd) < sum(even),
        "conjectured_upper_bound": {"numerator": rhs.numerator, "denominator": rhs.denominator},
        "conjecture_holds": min(deficiencies) <= rhs,
        "violation_numerator_after_multiplying_by_omega": (
            min(deficiencies) * len(clique_vertices) - size
        ),
    }


def verify(family_through: int = 10) -> dict[str, object]:
    if family_through < 7:
        raise ValueError("family-through must be at least 7")
    checked = [evaluate(q) for q in range(3, family_through + 1)]
    witness = checked[7 - 3]
    assert witness["hypothesis_sum_odd_lt_sum_even"] is True
    assert witness["conjecture_holds"] is False
    assert witness["minimum_deficiency"] == 20
    assert witness["size"] == 105
    assert witness["clique_number"] == 6
    assert witness["conjectured_upper_bound"] == {"numerator": 35, "denominator": 2}
    assert all(
        row["hypothesis_sum_odd_lt_sum_even"] is True and row["conjecture_holds"] is False
        for row in checked
        if int(row["q"]) >= 7
    )
    return {
        "certificate": "WoW-I #191 is false",
        "counterexample": "T(7) = L(K_7)",
        "witness": witness,
        "closed_form_family": {
            "range": "every integer q >= 7",
            "minimum_deficiency": "(q-2)(q-3)",
            "size_over_clique_number": "q(q-2)/2",
            "hypothesis": "sum Odd < sum Even",
        },
        "constructed_family_checked": {"first_q": 3, "last_q": family_through},
    }


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-through", type=int, default=10)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    output = verify(args.family_through)
    print(json.dumps(output, sort_keys=True, indent=None if args.compact else 2))


if __name__ == "__main__":
    main()
