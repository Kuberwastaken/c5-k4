#!/usr/bin/env python3
"""Exact, dependency-free certificate for Written on the Wall I #889."""

from __future__ import annotations

import argparse
import json
from collections import deque
from fractions import Fraction
from itertools import combinations
from typing import Any


Adjacency = tuple[frozenset[int], ...]


def complement_c5_clique_blowup(blob_size: int = 4) -> Adjacency:
    """Construct the complement of C5[K_blob_size].

    Its five blobs are independent.  Two vertices in different blobs are
    adjacent exactly when their blob indices differ by 2 modulo 5.
    """
    if blob_size < 1:
        raise ValueError("blob_size must be positive")
    order = 5 * blob_size
    neighbors = [set() for _ in range(order)]
    for u, v in combinations(range(order), 2):
        blob_difference = (u // blob_size - v // blob_size) % 5
        if blob_difference in (2, 3):
            neighbors[u].add(v)
            neighbors[v].add(u)
    return tuple(frozenset(row) for row in neighbors)


def distances_from(graph: Adjacency, source: int) -> tuple[int, ...]:
    distances = [-1] * len(graph)
    distances[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in sorted(graph[vertex]):
            if distances[neighbor] == -1:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)
    return tuple(distances)


def is_triangle_free(graph: Adjacency) -> bool:
    return all(not (graph[u] & graph[v]) for u in range(len(graph)) for v in graph[u] if u < v)


def blue_graph_for_triangle_free_property(graph: Adjacency) -> Adjacency:
    """Return the #822 blue graph for P = the class of triangle-free graphs.

    Only nonedges of G are colored.  A nonedge uv is blue exactly when adding
    uv leaves G triangle-free, equivalently when u and v have no common neighbor.
    """
    blue = [set() for _ in graph]
    for u, v in combinations(range(len(graph)), 2):
        if v not in graph[u] and not (graph[u] & graph[v]):
            blue[u].add(v)
            blue[v].add(u)
    return tuple(frozenset(row) for row in blue)


def clique_number(graph: Adjacency) -> int:
    """Compute omega exactly by deterministic exhaustive search."""
    for size in range(len(graph), 0, -1):
        for vertices in combinations(range(len(graph)), size):
            if all(v in graph[u] for u, v in combinations(vertices, 2)):
                return size
    return 0


def certificate() -> dict[str, Any]:
    graph = complement_c5_clique_blowup(4)
    order = len(graph)
    degrees = tuple(len(row) for row in graph)
    distance_rows = tuple(distances_from(graph, vertex) for vertex in range(order))
    blue = blue_graph_for_triangle_free_property(graph)

    edge_count = sum(degrees) // 2
    connected = all(distance >= 0 for distance in distance_rows[0])
    diameter = max(max(row) for row in distance_rows)
    odd_distance_counts = tuple(
        sum(distance >= 0 and distance % 2 == 1 for distance in row)
        for row in distance_rows
    )
    w = max(odd_distance_counts)
    blue_edge_count = sum(map(len, blue)) // 2
    blue_clique_number = clique_number(blue)
    required_blue_clique_size = Fraction(w, 4)

    # Structural hypotheses and the exact numerical contradiction.
    assert (order, edge_count) == (20, 80)
    assert connected
    assert len(set(degrees)) == 1 and degrees[0] == 8
    assert is_triangle_free(graph)
    assert diameter == 2
    assert set(odd_distance_counts) == {8}

    # An independent local characterization checks that every nonedge would
    # create a triangle when added.  Therefore #822 colors no pair blue.
    nonedges = [
        (u, v)
        for u, v in combinations(range(order), 2)
        if v not in graph[u]
    ]
    assert nonedges
    assert all(graph[u] & graph[v] for u, v in nonedges)
    assert blue_edge_count == 0
    assert blue_clique_number == 1
    assert required_blue_clique_size.denominator == 1
    assert blue_clique_number < required_blue_clique_size

    return {
        "conjecture": "Written on the Wall I #889",
        "witness": "complement of C5[K4]",
        "graph": {
            "order": order,
            "size": edge_count,
            "degree": degrees[0],
            "connected": connected,
            "triangle_free": True,
            "diameter": diameter,
        },
        "odd_distance": {
            "counts_by_vertex": list(odd_distance_counts),
            "w": w,
        },
        "blue_graph": {
            "edges": blue_edge_count,
            "clique_number": blue_clique_number,
        },
        "claimed_clique_size": required_blue_clique_size.numerator,
        "contradiction": f"{blue_clique_number} < {required_blue_clique_size.numerator}",
        "verified": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    result = certificate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        graph = result["graph"]
        print(
            "verified WoW-I #889 counterexample: "
            f"complement of C5[K4] is connected, {graph['degree']}-regular, "
            f"triangle-free, diameter {graph['diameter']}; w=8, "
            "omega(blue)=1 < w/4=2"
        )


if __name__ == "__main__":
    main()
