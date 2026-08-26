#!/usr/bin/env python
"""EP85: f(n) = smallest k such that every n-vertex graph with minDegree >= k contains C4.

Implementation 1 (this file): canonical enumeration by vertex-addition with adjacency
bitmasks; C4 (as a subgraph, not induced) <=> some pair of vertices shares >= 2 common
neighbors. f(n) = max{delta(G) : G C4-free} + 1 (empty graph shows the set is nonempty
for n>=0; for n>=1 delta ranges down to 0 so f(n)>=1).
"""
import sys

def gen_graphs(n):
    """Yield adjacency masks for all graphs on n labeled vertices (canonical order)."""
    masks = [0] * n
    def rec(v):
        if v == n:
            yield tuple(masks)
            return
        for sub in range(1 << v):
            m = 0
            for u in range(v):
                if sub >> u & 1:
                    m |= 1 << u
            masks[v] = m
            yield from rec(v + 1)
    return rec(0)

def c4_free(masks):
    n = len(masks)
    nb = []
    for v in range(n):
        m = masks[v]
        nv = 0
        for u in range(n):
            if masks[u] >> v & 1:
                nv |= 1 << u
        nb.append(m | nv)
    for u in range(n):
        au = nb[u]
        for w in range(u + 1, n):
            x = au & nb[w]
            if x.bit_count() >= 2:
                return False
    return True

def min_degree(masks):
    n = len(masks)
    best = n
    for v in range(n):
        d = 0
        for u in range(n):
            d += (masks[v] >> u & 1) | (masks[u] >> v & 1)
        if d < best:
            best = d
    return best

def f_table(ns):
    out = {}
    for n in ns:
        maxdelta = -1
        wit = None
        for masks in gen_graphs(n):
            if c4_free(masks):
                d = min_degree(masks)
                if d > maxdelta:
                    maxdelta, wit = d, masks
        out[n] = (maxdelta + 1, wit)
    return out

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or list(range(1, 8))
    t = f_table(ns)
    for n in ns:
        fv, wit = t[n]
        print(f"f({n}) = {fv}   witness(C4-free, delta=f-1): {[f'{u}' for u in range(n)] if wit is None else wit}")
