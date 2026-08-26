#!/usr/bin/env python
"""EP60: exact ex(n,C4) and minimum number of C4 copies among graphs with > ex(n,C4)
edges, for n <= 7 (Erdos-Simonovits 'at least 2 copies' variant sanity).
#C4 computed as (1/2) * sum over vertex pairs of C(common neighbors, 2)
(each C4 contributes its two diagonals)."""
import sys
from math import comb

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

def analyze(masks, n):
    adj = []
    for v in range(n):
        col = 0
        for u in range(n):
            if masks[u] >> v & 1:
                col |= 1 << u
        adj.append(masks[v] | col)
    ne = 0
    s = 0
    for u in range(n):
        for w in range(u + 1, n):
            cn = (adj[u] & adj[w]).bit_count()
            ne += (adj[u] >> w & 1)
            s += comb(cn, 2)
    return ne, s // 2  # each C4 counted twice

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1:]] or [4, 5, 6, 7]
    print("n  ex(n,C4)  minC4@>ex   witness_edges")
    for n in ns:
        best_free = -1
        minc = None
        wit = None
        for masks in gen_graphs(n):
            ne, c4 = analyze(masks, n)
            if c4 == 0:
                if ne > best_free:
                    best_free = ne
            else:
                pass
        # second pass for min C4 above threshold (threshold = best_free)
        for masks in gen_graphs(n):
            ne, c4 = analyze(masks, n)
            if ne > best_free:
                if minc is None or c4 < minc:
                    minc, wit = c4, ne
        print(f"{n}  {best_free}  {minc}  {wit}")
