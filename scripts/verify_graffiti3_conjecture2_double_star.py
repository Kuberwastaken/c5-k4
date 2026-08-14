#!/usr/bin/env python3
"""Independent exact verifier for the Graffiti³ Conjecture 2 counterexample.

This file deliberately does not import the discovery worker.  It reconstructs
the double star, recomputes closed distance-two balls and the independence
number, then checks a rational-square upper certificate for the radical sum.
"""

from __future__ import annotations

from fractions import Fraction
import json


def double_star(left: int, right: int) -> list[set[int]]:
    if left < 1 or right < 1:
        raise ValueError("both leaf sides must be positive")
    graph = [set() for _ in range(left + right + 2)]

    def add_edge(u: int, v: int) -> None:
        graph[u].add(v)
        graph[v].add(u)

    add_edge(0, 1)
    for vertex in range(2, left + 2):
        add_edge(0, vertex)
    for vertex in range(left + 2, left + right + 2):
        add_edge(1, vertex)
    return graph


def closed_two_ball_sizes(graph: list[set[int]]) -> list[int]:
    values: list[int] = []
    for source in range(len(graph)):
        seen = {source}
        frontier = {source}
        for _ in range(2):
            frontier = {v for u in frontier for v in graph[u]} - seen
            seen.update(frontier)
        values.append(len(seen))
    return values


def tree_independence_number(graph: list[set[int]]) -> int:
    """Exact include/exclude dynamic program, rejecting a non-tree input."""
    seen: set[int] = set()

    def visit(vertex: int, parent: int) -> tuple[int, int]:
        if vertex in seen:
            raise ValueError("input is not a tree")
        seen.add(vertex)
        excluded = 0
        included = 1
        for child in graph[vertex]:
            if child == parent:
                continue
            child_excluded, child_included = visit(child, vertex)
            excluded += max(child_excluded, child_included)
            included += child_excluded
        return excluded, included

    excluded, included = visit(0, -1)
    if len(seen) != len(graph):
        raise ValueError("input is disconnected")
    if sum(map(len, graph)) // 2 != len(graph) - 1:
        raise ValueError("input is not a tree")
    return max(excluded, included)


def verify() -> dict[str, object]:
    graph = double_star(11, 12)
    d2 = closed_two_ball_sizes(graph)
    assert d2[:2] == [25, 25]
    assert d2[2:13] == [13] * 11
    assert d2[13:] == [14] * 12
    assert tree_independence_number(graph) == 23
    leaves = set(range(2, 25))
    assert all(not (graph[u] & leaves) for u in leaves)

    # Strict outward bounds, certified by integer squaring.
    sqrt13_upper = Fraction(1803, 500)
    sqrt14_upper = Fraction(1871, 500)
    assert sqrt13_upper > 0 and sqrt13_upper**2 > 13
    assert sqrt14_upper > 0 and sqrt14_upper**2 > 14

    rga2_upper = 1 + Fraction(55, 19) * sqrt13_upper + Fraction(40, 13) * sqrt14_upper
    assert rga2_upper == Fraction(566921, 24700)
    assert Fraction(23) - rga2_upper == Fraction(1179, 24700)
    assert rga2_upper < 23

    balanced = double_star(12, 12)
    assert closed_two_ball_sizes(balanced) == [26, 26] + [14] * 24
    assert tree_independence_number(balanced) == 24
    sqrt91_upper = Fraction(191, 20)
    assert sqrt91_upper**2 > 91
    assert 1 + Fraction(12, 5) * sqrt91_upper < 24

    # The balanced-family squared gap is positive at 12 and strictly
    # increasing thereafter: P'(k)>0 follows from P''(k)>0 for k>=12.
    def polynomial(k: int) -> int:
        return 4 * k**4 - 36 * k**3 - 87 * k**2 - 40 * k + 16

    def derivative(k: int) -> int:
        return 16 * k**3 - 108 * k**2 - 174 * k - 40

    def second_derivative(k: int) -> int:
        return 48 * k**2 - 216 * k - 174

    assert polynomial(12) == 7744
    assert derivative(12) > 0 and second_derivative(12) > 0
    # P'''(k)=96k-216 is positive for k>=12, so P'' and then P' stay positive.
    assert 96 * 12 - 216 > 0

    return {
        "schema": "c5k4-graffiti3-conjecture2-independent-verifier-1.0",
        "witness": "DS(11,12)",
        "vertices": len(graph),
        "edges": sum(map(len, graph)) // 2,
        "independence_number": 23,
        "d2_profile": {"centers": 25, "left_leaves": 13, "right_leaves": 14},
        "rga2_expression": "1 + 55*sqrt(13)/19 + 40*sqrt(14)/13",
        "rga2_rational_upper": [rga2_upper.numerator, rga2_upper.denominator],
        "certified_gap_below_alpha": [1179, 24700],
        "balanced_family_first_certified_parameter": 12,
        "verdict": "COUNTEREXAMPLE_VERIFIED",
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True, indent=2))
