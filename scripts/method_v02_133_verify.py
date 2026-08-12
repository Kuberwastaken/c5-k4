#!/usr/bin/env python3
"""Independent verifier for the durable WOWII 133 Trial H2 records.

Unlike the discovery DFS, this checks every vertex subset in descending order
until the induced subgraph is a path.  It verifies the lift rows and one exact
minimum representative from each completed cubic order.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "results/expansion/method_v02_133_search.jsonl"


def subset_is_path(adj: list[int], mask: int) -> bool:
    k = bin(mask).count("1")
    if k == 1:
        return True
    degree_sum = 0
    endpoints = 0
    todo = mask
    while todo:
        bit = todo & -todo
        i = bit.bit_length() - 1
        d = bin(adj[i] & mask).count("1")
        if d > 2 or d == 0:
            return False
        degree_sum += d
        endpoints += d == 1
        todo ^= bit
    if degree_sum != 2 * (k - 1) or endpoints != 2:
        return False
    reached = 0
    frontier = mask & -mask
    while frontier:
        reached |= frontier
        next_frontier = 0
        todo = frontier
        while todo:
            bit = todo & -todo
            i = bit.bit_length() - 1
            next_frontier |= adj[i] & mask & ~reached
            todo ^= bit
        frontier = next_frontier
    return reached == mask


def longest_induced_path_subsets(G: nx.Graph) -> int:
    G = nx.convert_node_labels_to_integers(G)
    n = len(G)
    adj = [sum(1 << j for j in G[i]) for i in range(n)]
    for k in range(n, 0, -1):
        for S in itertools.combinations(range(n), k):
            mask = sum(1 << i for i in S)
            if subset_is_path(adj, mask):
                return k
    raise AssertionError


def local_alpha_bits(G: nx.Graph, v: int) -> int:
    ns = list(G[v])
    for k in range(len(ns), -1, -1):
        for S in itertools.combinations(ns, k):
            if all(not G.has_edge(a, b) for a, b in itertools.combinations(S, 2)):
                return k
    raise AssertionError


def has_c4_common_neighbors(G: nx.Graph) -> bool:
    return any(len(set(G[u]) & set(G[v])) >= 2 for u, v in itertools.combinations(G, 2))


def verify(row: dict) -> None:
    G = nx.from_graph6_bytes(row["graph6"].encode())
    assert nx.is_connected(G)
    assert has_c4_common_neighbors(G) == row["has_c4"]
    ecc = [max(nx.single_source_shortest_path_length(G, v).values()) for v in G]
    assert min(ecc) == row["radius"]
    avg = Fraction(sum(local_alpha_bits(G, v) for v in G), len(G))
    assert str(avg) == row["avg_l"]
    assert avg.numerator // avg.denominator == row["floor_l"]
    p = longest_induced_path_subsets(G)
    assert p == row["path"], (row["name"], p, row["path"])
    correction = 1 if row["has_c4"] else row["floor_l"]
    assert p - row["radius"] - correction == row["residual"]


def main() -> None:
    rows = [json.loads(line) for line in LOG.read_text().splitlines()]
    selected: list[dict] = [r for r in rows if r.get("kind") == "graph" and r.get("stratum") == "lift"]
    # The minimum records duplicate some discovery rows.  Select one unique
    # graph per completed exact order through 20.
    seen_n: set[int] = set()
    for row in rows:
        if row.get("kind") != "minimum" or row["n"] > 20 or row["n"] in seen_n:
            continue
        selected.append(row)
        seen_n.add(row["n"])
    for row in selected:
        verify(row)
        print(f"PASS {row['name']} n={row['n']} path={row['path']} residual={row['residual']}")
    assert len([r for r in selected if r.get("stratum") == "lift"]) == 6
    assert seen_n == {10, 12, 14, 16, 18, 20}
    print(f"PASS independent subset verifier: {len(selected)} durable rows")


if __name__ == "__main__":
    main()
