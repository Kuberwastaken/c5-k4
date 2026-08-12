#!/usr/bin/env python3
"""Independent expansion check for the WOWII 382e quotient engine."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations
import random

import networkx as nx

from method_v02_382e_search import evaluate_substitution


def expand(quotient: nx.Graph, weights: tuple[int, ...], substitution: str) -> nx.Graph:
    graph = nx.Graph()
    bags = []
    next_vertex = 0
    for weight in weights:
        bag = list(range(next_vertex, next_vertex + weight))
        next_vertex += weight
        bags.append(bag)
        graph.add_nodes_from(bag)
        if substitution == "clique":
            graph.add_edges_from(combinations(bag, 2))
    for first, second in quotient.edges:
        graph.add_edges_from((u, v) for u in bags[first] for v in bags[second])
    return graph


def minimum_parameter(graph: nx.Graph, threshold: int) -> int:
    vertices = tuple(graph.nodes)
    for size in range(1, len(vertices) + 1):
        for chosen_tuple in combinations(vertices, size):
            chosen = set(chosen_tuple)
            if all(
                vertex in chosen
                or len(set(graph.neighbors(vertex)) & chosen) >= threshold
                for vertex in vertices
            ):
                return size
    raise AssertionError("no feasible set")


def direct_maxine(graph: nx.Graph) -> tuple[int, int]:
    vertices = tuple(sorted(graph.nodes))
    initial = frozenset(vertices)

    def maxima(state: frozenset[int]) -> tuple[list[int], int]:
        degrees = {
            vertex: len(set(graph.neighbors(vertex)) & state) for vertex in state
        }
        maximum = max(degrees.values(), default=0)
        return [vertex for vertex, degree in degrees.items() if degree == maximum], maximum

    state = initial
    while True:
        candidates, maximum = maxima(state)
        if maximum == 0:
            deterministic = len(state)
            break
        state = state - {min(candidates)}

    @lru_cache(maxsize=None)
    def best(state: frozenset[int]) -> int:
        candidates, maximum = maxima(state)
        if maximum == 0:
            return len(state)
        return max(best(state - {vertex}) for vertex in candidates)

    return deterministic, best(initial)


def main() -> None:
    rng = random.Random(382_2026)
    atlas = [
        nx.convert_node_labels_to_integers(graph)
        for graph in nx.graph_atlas_g()
        if 3 <= len(graph) <= 6 and nx.is_connected(graph)
    ]
    checked = 0
    for _ in range(250):
        quotient = atlas[rng.randrange(len(atlas))]
        total = rng.randint(len(quotient), 12)
        weights = [1] * len(quotient)
        for _ in range(total - len(quotient)):
            weights[rng.randrange(len(weights))] += 1
        weights_tuple = tuple(weights)
        substitution = ("false", "clique")[rng.randrange(2)]
        graph = expand(quotient, weights_tuple, substitution)
        quotient_record = evaluate_substitution(
            quotient, weights_tuple, substitution, 60.0
        )
        direct_det, direct_best = direct_maxine(graph)
        direct_gamma = minimum_parameter(graph, 1)
        direct_gamma_2 = minimum_parameter(graph, 2)
        assert quotient_record["gamma"] == direct_gamma
        assert quotient_record["gamma_2"] == direct_gamma_2
        assert quotient_record["maxine_det"] == direct_det
        assert quotient_record["maxine_best"] == direct_best
        checked += 1
    print(f"PASS: {checked} explicit expansions agree on gamma, gamma_2, and both Maxine readings")


if __name__ == "__main__":
    main()
