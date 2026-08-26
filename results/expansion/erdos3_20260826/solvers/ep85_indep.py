#!/usr/bin/env python
"""EP85 implementation 2: independent path — enumerate all 2^(n choose 2) edge subsets
directly via itertools/bitint over a fixed edge list, use networkx for min-degree and
C4-subgraph detection (via common-neighbor counting on nx graph)."""
import itertools, sys
import networkx as nx

def c4_free_nx(G):
    for u in G.nodes:
        for w in G.nodes:
            if u < w:
                cn = sum(1 for x in nx.common_neighbors(G, u, w))
                if cn >= 2:
                    return False
    return True

def f_of(n):
    best_delta = -1
    edges = list(itertools.combinations(range(n), 2))
    m = len(edges)
    for bits in range(1 << m):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for i, (u, v) in enumerate(edges):
            if bits >> i & 1:
                G.add_edge(u, v)
        if c4_free_nx(G):
            d = min(dict(G.degree()).values())
            if d > best_delta:
                best_delta = d
                wit = bits
    return best_delta + 1

if __name__ == "__main__":
    for n in [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]:
        print(f"f({n}) = {f_of(n)}")
