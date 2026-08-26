#!/usr/bin/env python
"""EP82: F(n) = min over n-vertex graphs G of maxreg(G), where maxreg(G) is the largest
number of vertices in an INDUCED subgraph of G that is regular (all vertices same degree,
including degree 0 = independent set; single vertex counts as regular).

Impl 1: canonical vertex-addition bitmask enumeration; for each graph, scan vertex
subsets in decreasing size and test regularity via bit-twiddling degree computation.
"""
import sys

def gen_graphs(n):
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

def full_adj(masks, n):
    adj = []
    for v in range(n):
        a = masks[v]
        col = 0
        for u in range(n):
            if masks[u] >> v & 1:
                col |= 1 << u
        adj.append(a | col)
    return adj

def maxreg(adj, n):
    # subsets encoded as bitmasks of vertices, size descending
    best = 1  # any single vertex is 0-regular
    subs = sorted(range(1 << n), key=lambda s: -s.bit_count())
    for s in subs:
        if s.bit_count() <= best:
            return best
        degs = []
        ok = True
        for v in range(n):
            if s >> v & 1:
                d = (adj[v] & s).bit_count()
                if degs and d != degs[0]:
                    ok = False
                    break
                degs.append(d)
        if ok:
            return s.bit_count()
    return best

def F(ns):
    out = {}
    for n in ns:
        mn = None
        wit = None
        for masks in gen_graphs(n):
            adj = full_adj(masks, n)
            r = maxreg(adj, n)
            if mn is None or r < mn:
                mn, wit = r, masks
        out[n] = (mn, wit)
    return out

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or list(range(1, 7))
    t = F(ns)
    for n in ns:
        print(f"F({n}) = {t[n][0]}   extremal graph adjacency-masks: {t[n][1]}")
