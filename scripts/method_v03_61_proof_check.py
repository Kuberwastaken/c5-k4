#!/usr/bin/env python3
"""Fixed-ledger checks for Method v0.3 Lane P3 (WOWII 61).

This checker reads only the at-most-ten saved extrema from each switch-component row
in the frozen Method v0.2 JSONL ledger.  It performs no graph generation, no
two-switch traversal, and no degree-sequence expansion.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter
from functools import lru_cache
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/method_v02_61_search.jsonl"
EXPECTED_SHA256 = "0a71a74b64b682e733026c9ed24e21808f7336b0d13aee21c3eb7ac7cf942e98"


def popcount(mask: int) -> int:
    return bin(mask).count("1")


def hh_residue(graph: nx.Graph) -> int:
    sequence = sorted(dict(graph.degree()).values(), reverse=True)
    while sequence and sequence[0] > 0:
        degree = sequence.pop(0)
        if degree > len(sequence):
            raise AssertionError("nongraphical sequence in frozen ledger")
        for index in range(degree):
            sequence[index] -= 1
            if sequence[index] < 0:
                raise AssertionError("negative Havel--Hakimi term")
        sequence.sort(reverse=True)
    return len(sequence)


def maxine_range(graph: nx.Graph) -> tuple[int, int]:
    """Minimum/maximum terminal order over all maximum-degree deletion ties."""

    order = graph.number_of_nodes()
    adjacency = [sum(1 << neighbor for neighbor in graph.neighbors(vertex)) for vertex in range(order)]

    @lru_cache(maxsize=None)
    def visit(mask: int) -> tuple[int, int]:
        degrees = [
            popcount(adjacency[vertex] & mask) if mask & (1 << vertex) else -1
            for vertex in range(order)
        ]
        maximum = max(degrees)
        if maximum <= 0:
            terminal = popcount(mask)
            return terminal, terminal
        children = [
            visit(mask ^ (1 << vertex))
            for vertex, degree in enumerate(degrees)
            if degree == maximum
        ]
        return min(child[0] for child in children), max(child[1] for child in children)

    return visit((1 << order) - 1)


def diametral_geodesics(graph: nx.Graph) -> tuple[int, list[tuple[int, ...]]]:
    diameter = nx.diameter(graph)
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    paths: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for source in graph:
        for target in graph:
            if source >= target or distances[source][target] != diameter:
                continue
            for path_list in nx.all_shortest_paths(graph, source, target):
                path = tuple(path_list)
                path = min(path, tuple(reversed(path)))
                if path not in seen:
                    seen.add(path)
                    paths.append(path)
    return diameter, paths


def is_forest(graph: nx.Graph, mask: int) -> bool:
    vertices = [vertex for vertex in graph if mask & (1 << vertex)]
    induced = graph.subgraph(vertices)
    return induced.number_of_edges() == induced.number_of_nodes() - nx.number_connected_components(induced)


def best_forest_submask(graph: nx.Graph) -> list[int]:
    """For each mask, the largest induced-forest order in that mask."""

    order = graph.number_of_nodes()
    limit = 1 << order
    best = [popcount(mask) if is_forest(graph, mask) else -1 for mask in range(limit)]
    for bit in range(order):
        for mask in range(limit):
            if mask & (1 << bit):
                best[mask] = max(best[mask], best[mask ^ (1 << bit)])
    return best


def independent_masks(graph: nx.Graph, size: int) -> list[int]:
    masks: list[int] = []
    for vertices in itertools.combinations(range(graph.number_of_nodes()), size):
        if graph.subgraph(vertices).number_of_edges() == 0:
            masks.append(sum(1 << vertex for vertex in vertices))
    return masks


def assert_local_countermodel(code: str, independent_vertices: set[int], path: tuple[int, ...]) -> None:
    graph = nx.from_graph6_bytes(code.encode())
    residue = hh_residue(graph)
    diameter = nx.diameter(graph)
    target = residue + math.ceil(diameter / 3)
    assert graph.subgraph(independent_vertices).number_of_edges() == 0
    assert len(independent_vertices) == residue
    assert len(path) == diameter + 1
    assert all(graph.has_edge(left, right) for left, right in zip(path, path[1:]))
    assert nx.shortest_path_length(graph, path[0], path[-1]) == diameter
    union_mask = sum(1 << vertex for vertex in independent_vertices | set(path))
    best = best_forest_submask(graph)
    assert best[union_mask] == target - 1
    assert best[(1 << graph.number_of_nodes()) - 1] == target


def packing_reaches(path: tuple[int, ...], independent: int, target: int) -> bool:
    """Whether P\\I has target vertices at pairwise path distance at least 3."""

    positions = [index for index, vertex in enumerate(path) if not independent & (1 << vertex)]
    optimum: list[int] = []
    for index, position in enumerate(positions):
        optimum.append(
            1
            + max(
                (optimum[earlier] for earlier in range(index) if position - positions[earlier] >= 3),
                default=0,
            )
        )
    return max(optimum, default=0) >= target


def main() -> None:
    payload = LEDGER.read_bytes()
    assert hashlib.sha256(payload).hexdigest() == EXPECTED_SHA256
    rows = [json.loads(line) for line in payload.decode().splitlines()]
    codes = list(
        dict.fromkeys(
            record["graph6"]
            for row in rows
            if row.get("kind") == "switch_component"
            for record in row["best"]
        )
    )
    assert len(codes) == 823

    maxine_gaps: Counter[tuple[int, int]] = Counter()
    strict_maxine: list[str] = []
    exchange_counts: Counter[str] = Counter()
    packing_counts: Counter[str] = Counter()
    exchange_all_all_failures: list[str] = []

    for code in codes:
        graph = nx.from_graph6_bytes(code.encode())
        residue = hh_residue(graph)
        minimum_maxine, maximum_maxine = maxine_range(graph)
        assert residue <= minimum_maxine <= maximum_maxine
        maxine_gaps[(minimum_maxine - residue, maximum_maxine - residue)] += 1
        if minimum_maxine > residue:
            strict_maxine.append(code)

        diameter, paths = diametral_geodesics(graph)
        target = math.ceil(diameter / 3)
        independent_sets = independent_masks(graph, residue)
        best = best_forest_submask(graph)

        exchange_matrix: list[list[bool]] = []
        packing_matrix: list[list[bool]] = []
        for independent in independent_sets:
            exchange_row: list[bool] = []
            packing_row: list[bool] = []
            for path in paths:
                path_mask = sum(1 << vertex for vertex in path)
                exchange_row.append(best[independent | path_mask] >= residue + target)
                packing_row.append(packing_reaches(path, independent, target))
            exchange_matrix.append(exchange_row)
            packing_matrix.append(packing_row)

        exchange_properties = {
            "all_I_all_P": all(all(row) for row in exchange_matrix),
            "all_I_some_P": all(any(row) for row in exchange_matrix),
            "some_I_all_P": any(all(row) for row in exchange_matrix),
            "some_I_some_P": any(any(row) for row in exchange_matrix),
        }
        packing_properties = {
            "all_I_all_P": all(all(row) for row in packing_matrix),
            "all_I_some_P": all(any(row) for row in packing_matrix),
            "some_I_all_P": any(all(row) for row in packing_matrix),
            "some_I_some_P": any(any(row) for row in packing_matrix),
        }
        exchange_counts.update(key for key, holds in exchange_properties.items() if holds)
        packing_counts.update(key for key, holds in packing_properties.items() if holds)
        if not exchange_properties["all_I_all_P"]:
            exchange_all_all_failures.append(code)

        # The rigorous quarter-diameter packing lemma must hold uniformly.
        quarter_target = math.ceil(diameter / 4)
        assert all(
            packing_reaches(path, independent, quarter_target)
            for independent in independent_sets
            for path in paths
        )

    assert maxine_gaps == Counter(
        {
            (0, 0): 423,
            (1, 1): 246,
            (0, 1): 144,
            (2, 2): 7,
            (0, 2): 2,
            (1, 2): 1,
        }
    )
    assert len(strict_maxine) == 254
    assert strict_maxine[0] == "DLS"
    assert exchange_counts == Counter(
        {"all_I_all_P": 821, "all_I_some_P": 823, "some_I_all_P": 823, "some_I_some_P": 823}
    )
    assert packing_counts == Counter(
        {"all_I_all_P": 731, "all_I_some_P": 751, "some_I_all_P": 817, "some_I_some_P": 823}
    )
    assert exchange_all_all_failures == ["FHAXG", "FXAXG"]
    assert_local_countermodel("FHAXG", {0, 1, 3, 6}, (0, 5, 3, 2, 1))
    assert_local_countermodel("FXAXG", {0, 1, 3, 4}, (1, 2, 0, 5, 4))

    print(f"PASS: frozen ledger SHA-256 {EXPECTED_SHA256}")
    print("PASS: 823 saved switch extrema only; no graph generation")
    print(f"PASS: Maxine >= residue throughout; strict in {len(strict_maxine)} extrema (first DLS)")
    print("PASS: quarter-diameter packing/exchange lemma holds for every residue-set/geodesic pair")
    print("REFUTED: third-diameter exchange inside I union P for every I,P")
    print("COUNTERMODELS: FHAXG, FXAXG (821/823 graphs satisfy the universal local form)")
    print("OBSERVED ONLY: suitable-path and suitable-residue-set variants hold on 823/823")


if __name__ == "__main__":
    main()
