#!/usr/bin/env python
"""EP60 impl 2 (networkx): recount ex(n,C4) and the min-C4-above-ex witnesses found by
impl 1. C4 count via per-4-subset induced edge count: m=4->1, m=5->2, m=6->3."""
import itertools
import networkx as nx

def c4_count(G):
    """#C4 as subgraph = (1/2) sum over vertex pairs of C(common nbrs, 2)."""
    tot = 0
    V = list(G.nodes)
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            cn = sum(1 for _ in nx.common_neighbors(G, V[i], V[j]))
            tot += cn * (cn - 1) // 2
    return tot // 2

def ex_and_min(n):
    edges = list(itertools.combinations(range(n), 2))
    best_free = -1
    graphs = []
    for bits in range(1 << len(edges)):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for i, e in enumerate(edges):
            if bits >> i & 1:
                G.add_edge(*e)
        c4 = c4_count(G)
        ne = G.number_of_edges()
        if c4 == 0 and ne > best_free:
            best_free = ne
        graphs.append((ne, c4, bits))
    minc, wit = None, None
    for ne, c4, bits in graphs:
        if ne > best_free and (minc is None or c4 < minc):
            minc, wit, wbits = c4, ne, bits
    return best_free, minc, wit, wbits, edges

if __name__ == "__main__":
    import sys
    for n in [int(x) for x in sys.argv[1:]] or [4, 5, 6]:
        exv, minc, wit, wbits, edges = ex_and_min(n)
        print(f"n={n}: ex={exv} minC4@>ex={minc} at |E|={wit}")
        if wbits is not None and minc == 1:
            W = [e for i, e in enumerate(edges) if wbits >> i & 1]
            print("   single-C4 witness edges:", W)
