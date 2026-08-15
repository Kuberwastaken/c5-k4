#!/usr/bin/env python3
"""Erdos 982 bounded exact search.

Declaration (upstream 2411d22e, 982.lean):
  n >= 3, p : Fin n -> R^2 injective, IsConvexPolygon p  ->
  exists i, ncard { dist (p i) (p j) : j != i } >= n / 2   (Nat division = floor)

Negation certificate = one strictly-convex n-point configuration with
  for every vertex i:  #{ d(i,j) : j != i }  <=  floor(n/2) - 1.

Search: integer grid (exact: squared distances are integers).
Two monotone prunes, both hereditary downward, so valid on partial sets:
  P1  strict convex position (subset of a strictly convex set is strictly convex)
  P2  per-vertex distinct-distance count (monotone nondecreasing in |S|)
Normalisation: lex-smallest point translated to (0,0).
"""
import sys
import time


def hull_size(pts):
    """Andrew monotone chain, strict turns: returns hull vertex count."""
    P = sorted(pts)
    if len(P) < 3:
        return len(P)
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2:
                ax, ay = h[-2]
                bx, by = h[-1]
                cr = (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax)
                if cr <= 0:      # right turn or collinear -> drop
                    h.pop()
                else:
                    break
            h.append(p)
        return h
    lo = half(P)
    up = half(reversed(P))
    return len(lo) + len(up) - 2


def strictly_convex(pts):
    return hull_size(pts) == len(pts)


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def search(n, N, deadline, ycap=None):
    """All strictly-convex n-subsets of the grid with every vertex having
    <= K distinct distances, K = n//2 - 1. Returns (found, stats)."""
    K = n // 2 - 1
    if ycap is None:
        ycap = N
    # candidate points: lex-min is (0,0), so x>=0 and (x>0 or y>0)
    cand = []
    for x in range(0, N + 1):
        for y in range(-ycap, ycap + 1):
            if x == 0 and y <= 0:
                continue
            cand.append((x, y))
    cand.sort()
    base = (0, 0)
    nodes = 0
    hits = []
    t0 = time.time()

    def rec(S, dsets, start):
        nonlocal nodes
        if time.time() > deadline:
            raise TimeoutError(nodes)
        if len(S) == n:
            hits.append(list(S))
            return True
        # bound: need n - len(S) more points
        for idx in range(start, len(cand)):
            q = cand[idx]
            nodes += 1
            if nodes % 4096 == 0 and time.time() > deadline:
                raise TimeoutError(nodes)
            # P2 incremental
            newq = set()
            ok = True
            for k, p in enumerate(S):
                v = d2(p, q)
                newq.add(v)
                if v not in dsets[k] and len(dsets[k]) + 1 > K:
                    ok = False
                    break
            if not ok or len(newq) > K:
                continue
            # P1
            S2 = S + [q]
            if not strictly_convex(S2):
                continue
            d2s = [dsets[k] | {d2(S[k], q)} for k in range(len(S))] + [newq]
            if rec(S2, d2s, idx + 1):
                return True
        return False

    try:
        rec([base], [set()], 0)
        status = "COMPLETE"
    except TimeoutError:
        status = "TIMEOUT"
    return hits, dict(status=status, nodes=nodes, n=n, N=N, K=K,
                      cand=len(cand), secs=round(time.time() - t0, 1))


def verify(pts):
    """Independent second code path: recompute everything from scratch."""
    n = len(pts)
    assert len(set(pts)) == n
    # strict convexity by an independent test: every point strictly outside
    # the convex hull of the others  <=>  exists integer direction separating.
    # Use: p is a strict vertex iff p is not in conv(others).  Test by LP-free
    # method: p in conv(Q) iff p is in some triangle/segment of Q.
    def in_hull(p, Q):
        m = len(Q)
        for i in range(m):
            for j in range(i + 1, m):
                a, b = Q[i], Q[j]
                cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
                if cr == 0:
                    if (min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and
                            min(a[1], b[1]) <= p[1] <= max(a[1], b[1])):
                        return True
                for k in range(j + 1, m):
                    c = Q[k]
                    s = []
                    for (u, v) in ((a, b), (b, c), (c, a)):
                        s.append((v[0] - u[0]) * (p[1] - u[1]) -
                                 (v[1] - u[1]) * (p[0] - u[0]))
                    if all(x >= 0 for x in s) or all(x <= 0 for x in s):
                        return True
        return False
    conv = all(not in_hull(pts[i], [pts[j] for j in range(n) if j != i])
               for i in range(n))
    counts = [len({d2(pts[i], pts[j]) for j in range(n) if j != i})
              for i in range(n)]
    return conv, counts, min(counts), n // 2


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "search":
        n, N, budget = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
        ycap = int(sys.argv[5]) if len(sys.argv) > 5 else None
        hits, st = search(n, N, time.time() + budget, ycap)
        print(st)
        for h in hits:
            print("HIT", h, verify(h))
    elif mode == "check":
        pts = eval(sys.argv[2])
        print(verify(pts))
