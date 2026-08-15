#!/usr/bin/env python3
"""Erdos 982 — second, structurally different exact search (K = n//2 - 1 = 2).

Key structural reduction (valid, not a heuristic):
  a counterexample needs every vertex i to have <= K distinct distances to the
  other n-1 vertices.  Translate the lex-smallest vertex to the origin; then the
  other n-1 vertices all lie on the union of at most K circles centred at the
  origin.  So enumerate the radius set first, then do a pruned DFS inside that
  tiny point set.  This is complete for the declared box, and is an independent
  code path from e982.py (which walks the whole grid).

Box: x in [0,N], y in [-N,N], origin = lex-smallest vertex.
"""
import sys
import time
from itertools import combinations


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def hull_size(pts):
    P = sorted(pts)
    if len(P) < 3:
        return len(P)
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2:
                ax, ay = h[-2]; bx, by = h[-1]
                if (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) <= 0:
                    h.pop()
                else:
                    break
            h.append(p)
        return h
    return len(half(P)) + len(half(list(reversed(P)))) - 2


def run(n, N, budget):
    K = n // 2 - 1
    assert K == 2, "this routine is specialised to K=2 (n in {6,7})"
    t0 = time.time()
    # circles centred at the origin inside the box, lex > origin
    circ = {}
    for x in range(0, N + 1):
        for y in range(-N, N + 1):
            if x == 0 and y <= 0:
                continue
            circ.setdefault(x * x + y * y, []).append((x, y))
    radii = sorted(circ)
    stats = dict(n=n, N=N, K=K, radii=len(radii), pairs=0, sets=0, dfs=0)
    hits = []

    def dfs(S, dsets, pool, need):
        stats['dfs'] += 1
        if need == 0:
            hits.append(list(S))
            return True
        if len(pool) < need:
            return False
        for i, q in enumerate(pool):
            newq = set()
            ok = True
            for k, p in enumerate(S):
                v = d2(p, q)
                newq.add(v)
                if v not in dsets[k] and len(dsets[k]) >= K:
                    ok = False
                    break
            if not ok or len(newq) > K:
                continue
            S2 = S + [q]
            if hull_size(S2) != len(S2):
                continue
            nd = [dsets[k] | {d2(S[k], q)} for k in range(len(S))] + [newq]
            if dfs(S2, nd, pool[i + 1:], need - 1):
                return True
        return False

    # one circle, then two circles
    groups = []
    for r in radii:
        groups.append((circ[r],))
    for a in range(len(radii)):
        ra = radii[a]
        for b in range(a + 1, len(radii)):
            groups.append((circ[ra], circ[radii[b]]))

    for g in groups:
        if time.time() - t0 > budget:
            return hits, dict(stats, status='TIMEOUT',
                              secs=round(time.time() - t0, 1))
        pool = sorted(p for c in g for p in c)
        stats['pairs'] += 1
        if len(pool) < n - 1:
            continue
        stats['sets'] += 1
        if dfs([(0, 0)], [set()], pool, n - 1):
            break
    return hits, dict(stats, status='COMPLETE',
                      secs=round(time.time() - t0, 1))


if __name__ == "__main__":
    n, N, budget = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    hits, st = run(n, N, budget)
    print(st)
    for h in hits:
        print("HIT", h)
