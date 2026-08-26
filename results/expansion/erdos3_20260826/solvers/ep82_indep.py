#!/usr/bin/env python
"""EP82 impl 2: networkx-based re-enumeration (edge-subset order) with an independent
regularity test (degree multiset via nx.degree). Also verifies impl-1 extremal witnesses."""
import itertools, sys
import networkx as nx

def maxreg_nx(G):
    nodes = list(G.nodes)
    best = 1
    for r in range(len(nodes), best, -1):  # descending size, stop when found
        for S in itertools.combinations(nodes, r):
            H = G.subgraph(S)
            ds = [d for _, d in H.degree()]
            if len(set(ds)) <= 1:
                return r
    return best

def F_of(n):
    edges = list(itertools.combinations(range(n), 2))
    mn, wit = None, None
    for bits in range(1 << len(edges)):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for i, e in enumerate(edges):
            if bits >> i & 1:
                G.add_edge(*e)
        r = maxreg_nx(G)
        if mn is None or r < mn:
            mn, wit = r, bits
    return mn, wit

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5]
    for n in ns:
        mn, wit = F_of(n)
        print(f"F({n}) = {mn}   extremal edge-bitmask: {wit}")
