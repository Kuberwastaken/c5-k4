#!/usr/bin/env python3
"""Dependency-free exact verifier for the C5[K4] counterexample to WOWII 64.

The only exhaustive searches are over the 1,140 triples and 15,504
five-subsets of a fixed 20-vertex graph.  Heredity of independence and of
being a forest turns those bounded searches into exact global maxima.
"""

from __future__ import annotations

import itertools
import math
import signal
import time


ORDER = 20
BLOCK_SIZE = 4
BLOCK_COUNT = 5
TIME_LIMIT_SECONDS = 60.0


def adjacent(left: int, right: int) -> bool:
    """Adjacency in the five-clique cyclic blow-up C5[K4]."""

    if not (0 <= left < ORDER and 0 <= right < ORDER):
        raise ValueError("vertex outside 0..19")
    if left == right:
        return False
    left_block = left // BLOCK_SIZE
    right_block = right // BLOCK_SIZE
    difference = (left_block - right_block) % BLOCK_COUNT
    return difference in (0, 1, BLOCK_COUNT - 1)


def make_adjacency() -> tuple[int, ...]:
    rows: list[int] = []
    for vertex in range(ORDER):
        row = 0
        for neighbor in range(ORDER):
            if adjacent(vertex, neighbor):
                row |= 1 << neighbor
        rows.append(row)
    return tuple(rows)


def connected(adjacency: tuple[int, ...]) -> bool:
    reached = 1
    frontier = 1
    while frontier:
        next_frontier = 0
        remaining = frontier
        while remaining:
            bit = remaining & -remaining
            vertex = bit.bit_length() - 1
            next_frontier |= adjacency[vertex]
            remaining ^= bit
        frontier = next_frontier & ~reached
        reached |= frontier
    return reached == (1 << ORDER) - 1


def is_independent(vertices: tuple[int, ...], adjacency: tuple[int, ...]) -> bool:
    mask = sum(1 << vertex for vertex in vertices)
    return all(adjacency[vertex] & (mask ^ (1 << vertex)) == 0 for vertex in vertices)


def is_forest(vertices: tuple[int, ...], adjacency: tuple[int, ...]) -> bool:
    """Exact union-find cycle test for the induced graph on ``vertices``."""

    parent = {vertex: vertex for vertex in vertices}

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for index, left in enumerate(vertices):
        for right in vertices[index + 1 :]:
            if not adjacency[left] & (1 << right):
                continue
            left_root = find(left)
            right_root = find(right)
            if left_root == right_root:
                return False
            parent[left_root] = right_root
    return True


def ceil_sqrt(value: int) -> int:
    """Exact integer ceiling of a nonnegative square root."""

    floor = math.isqrt(value)
    return floor if floor * floor == value else floor + 1


def install_timeout() -> None:
    """Add a hard 60-second guard on platforms that provide SIGALRM."""

    if hasattr(signal, "SIGALRM"):
        def timeout_handler(_signum: int, _frame: object) -> None:
            raise TimeoutError(f"verification exceeded {TIME_LIMIT_SECONDS:.0f} seconds")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(TIME_LIMIT_SECONDS))


def main() -> None:
    started = time.monotonic()
    install_timeout()
    adjacency = make_adjacency()

    # Construction and graph invariants.
    assert ORDER == BLOCK_COUNT * BLOCK_SIZE == 20
    assert all(adjacency[vertex] & (1 << vertex) == 0 for vertex in range(ORDER))
    assert all(
        bool(adjacency[left] & (1 << right)) == bool(adjacency[right] & (1 << left))
        for left in range(ORDER)
        for right in range(ORDER)
    )
    degrees = tuple(bin(row).count("1") for row in adjacency)
    assert degrees == (11,) * ORDER
    assert max(degrees) == 11
    assert sum(degrees) // 2 == 110
    assert connected(adjacency)

    # alpha >= 2 from a witness.  Exhausting every triple proves alpha <= 2:
    # every larger independent set would contain an independent triple.
    independent_witness = (0, 8)
    assert is_independent(independent_witness, adjacency)
    triples_checked = 0
    for triple in itertools.combinations(range(ORDER), 3):
        triples_checked += 1
        assert not is_independent(triple, adjacency), f"independent triple: {triple}"
    assert triples_checked == math.comb(ORDER, 3) == 1_140
    alpha = 2

    # f >= 4 from an induced P4.  Exhausting every five-subset proves f <= 4:
    # an induced subgraph of a forest is a forest, so any larger induced
    # forest would contain a five-vertex induced forest.
    forest_witness = (0, 4, 8, 12)
    assert is_forest(forest_witness, adjacency)
    witness_edges = sum(
        adjacent(left, right) for left, right in itertools.combinations(forest_witness, 2)
    )
    assert witness_edges == 3
    five_subsets_checked = 0
    for subset in itertools.combinations(range(ORDER), 5):
        five_subsets_checked += 1
        assert not is_forest(subset, adjacency), f"induced forest of order five: {subset}"
    assert five_subsets_checked == math.comb(ORDER, 5) == 15_504
    forest_number = 4

    # The source defines this as natural-number remainder, not real remainder.
    maximum_degree = max(degrees)
    remainder = ORDER % maximum_degree
    radicand = alpha * (1 + remainder)
    conjectured_lower_bound = ceil_sqrt(radicand)
    assert (remainder, radicand, conjectured_lower_bound) == (9, 20, 5)
    assert forest_number < conjectured_lower_bound

    elapsed = time.monotonic() - started
    assert elapsed < TIME_LIMIT_SECONDS
    if hasattr(signal, "SIGALRM"):
        signal.alarm(0)

    print("PASS: reconstructed C5[K4] as five cyclically joined four-cliques")
    print("PASS: n=20, m=110, connected, degree sequence=(11)^20, Delta=11")
    print(f"PASS: alpha=2 exactly ({triples_checked} triples exhausted; witness {independent_witness})")
    print(
        "PASS: largest induced forest=4 exactly "
        f"({five_subsets_checked} five-subsets exhausted; induced-P4 witness {forest_witness})"
    )
    print("PASS: natural remainder 20 % 11=9; ceil(sqrt(2*(1+9)))=5")
    print(f"COUNTEREXAMPLE: f=4 < 5 (completed in {elapsed:.3f}s)")


if __name__ == "__main__":
    main()
