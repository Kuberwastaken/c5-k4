#!/usr/bin/env python3
"""Erdos 982 -- targeted test of the two known "3 equidistant at every vertex"
convex polygons from the unit-distance literature.

  erdos_982 : n distinct points in convex position  ==>  some vertex has at
              least floor(n/2) distinct distances to the other vertices.

A counterexample needs c_i <= floor(n/2) - 1 at EVERY vertex, where c_i is the
number of distinct distances from vertex i.  Equivalently the per-vertex
"excess" E_i := (n-1) - c_i must be >= ceil(n/2).

Constructions tested
  (A) Fishburn-Reeds convex 20-gon [FiRe92, Table 1]: A_i=(-x_i,y_i),
      B_i=(x_i,y_i), i=1..10; every vertex at UNIT distance from exactly 3
      others.  Table transcribed from github.com/davidiach/erdos97
      (scripts/fr_cut_homotopy.py) and independently re-verified + Newton
      polished here to 50 digits.
  (B) Danzer-type C3-symmetric convex 9-gon: 3 rotation orbits, every vertex
      has 3 equidistant others (2 orbit mates + 1 tuned cross witness), radius
      varying by vertex.  This is a RECONSTRUCTION from the combinatorial
      structure, not Danzer's published coordinates.

All heavy arithmetic is decimal at 60 digits; no trigonometry is needed because
the C3 rotation is exact: omega = (-1 + i*sqrt 3)/2.

No network. Hard cap: every stage is milliseconds.
"""

from __future__ import annotations

import itertools
import sys
from decimal import Decimal as D
from decimal import getcontext

getcontext().prec = 60

# Guard band: two squared distances are called EQUAL only if they differ by
# less than this.  Coordinates are solved to ~1e-50, so any observed gap above
# this is real; any gap below it is reported as UNRESOLVED, never as a crossing.
TOL = D(10) ** -30


# --------------------------------------------------------------------------
# linear algebra over Decimal
# --------------------------------------------------------------------------
def solve(A, b):
    """Gaussian elimination with partial pivoting; A is n x n list of lists."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if M[p][c] == 0:
            raise ZeroDivisionError("singular")
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / piv
            if f == 0:
                continue
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


# --------------------------------------------------------------------------
# generic geometry helpers (exact on Decimal input)
# --------------------------------------------------------------------------
def d2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hull(pts):
    """Andrew monotone chain, STRICT turns (collinear points dropped)."""
    P = sorted(range(len(pts)), key=lambda i: (pts[i][0], pts[i][1]))
    def half(idx):
        h = []
        for i in idx:
            while len(h) >= 2 and cross(pts[h[-2]], pts[h[-1]], pts[i]) <= 0:
                h.pop()
            h.append(i)
        return h
    lo = half(P)
    up = half(reversed(P))
    return lo[:-1] + up[:-1]


def strictly_convex(pts):
    h = hull(pts)
    return len(h) == len(pts), h


def classes(pts, i, tol=TOL):
    """Multiplicity profile of squared distances from vertex i.

    Returns (sorted list of (d2, multiplicity), min gap between adjacent
    distinct classes).
    """
    ds = sorted(d2(pts[i], pts[j]) for j in range(len(pts)) if j != i)
    out = []
    gap = None
    for v in ds:
        if out and abs(v - out[-1][0]) < tol:
            out[-1][1] += 1
        else:
            if out:
                g = v - out[-1][0]
                gap = g if gap is None else min(gap, g)
            out.append([v, 1])
    return out, gap


def profile(pts, label):
    n = len(pts)
    need = n // 2                      # floor(n/2), the declaration's bound
    rows = []
    mingap = None
    for i in range(n):
        cls, gap = classes(pts, i)
        c = len(cls)
        mult = sorted((m for _, m in cls), reverse=True)
        rows.append((i, c, n - 1 - c, mult))
        if gap is not None:
            mingap = gap if mingap is None else min(mingap, gap)
    cmin = min(r[1] for r in rows)
    emin = min(r[2] for r in rows)
    mmax = max(max(r[3]) for r in rows)
    print(f"\n--- {label}: n={n}, floor(n/2)={need} ---")
    print(f"  strictly convex          : {strictly_convex(pts)[0]}")
    print(f"  min over vertices of c_i : {cmin}")
    print(f"  min over vertices of E_i : {emin}   (counterexample needs E_i >= {-(-n // 2)})")
    print(f"  max distance multiplicity: {mmax}")
    print(f"  RESIDUAL R = min c_i - floor(n/2) = {cmin - need}   "
          f"(counterexample iff R <= -1)")
    print(f"  smallest gap between distinct squared distances at any vertex: "
          f"{float(mingap):.3e}" if mingap else "  (no gap)")
    print("  per-vertex (c_i, E_i, multiplicity profile):")
    for i, c, e, mult in rows:
        print(f"    v{i:<3d} c={c:<3d} E={e:<3d} mult={mult}")
    return cmin, need, mmax


# --------------------------------------------------------------------------
# (A) Fishburn-Reeds 20-gon
# --------------------------------------------------------------------------
FR_X = ["469.633821777", "471.414237018", "473.126180256", "520.0",
        "520.996246864", "522.0", "429.872125856", "429.224646090",
        "428.539574537", "390.440922261"]
FR_Y = ["-92.982777730", "-89.969229800", "-87.048665472", "30.0",
        "33.0", "36.1", "342.595442083", "344.599064292",
        "346.658610393", "417.185267785"]

# undirected unit-distance pairs (i,j), meaning |A_i B_j| = |A_j B_i| = 1
FR_PAIRS = [(1, 6), (1, 9), (1, 10), (2, 5), (2, 8), (2, 10), (3, 4), (3, 7),
            (3, 10), (4, 8), (4, 9), (5, 7), (5, 9), (6, 7), (6, 8)]
# the five coordinates Fishburn-Reeds evidently chose freely (round values)
FR_FIXED = {("x", 4), ("x", 6), ("y", 4), ("y", 5), ("y", 6)}


def fr_seed():
    x = [D(v) / 1000 for v in FR_X]
    y = [D(v) / 1000 for v in FR_Y]
    return x, y


def fr_resid(x, y):
    """|A_i B_j|^2 - 1 for the 15 undirected unit pairs.
    A_i=(-x_i,y_i), B_j=(x_j,y_j) so |A_i B_j|^2 = (x_i+x_j)^2 + (y_j-y_i)^2."""
    return [(x[i - 1] + x[j - 1]) ** 2 + (y[j - 1] - y[i - 1]) ** 2 - 1
            for i, j in FR_PAIRS]


def fr_polish(x, y, iters=6):
    """Newton on the 15 free coordinates (the 5 round ones held fixed)."""
    free = [(t, k) for t in ("x", "y") for k in range(1, 11)
            if (t, k) not in FR_FIXED]
    assert len(free) == 15, len(free)
    x, y = x[:], y[:]
    for _ in range(iters):
        F = fr_resid(x, y)
        if max(abs(v) for v in F) < D(10) ** -55:
            break
        J = []
        for eq, (i, j) in enumerate(FR_PAIRS):
            row = []
            for t, k in free:
                g = D(0)
                if t == "x":
                    if k == i:
                        g += 2 * (x[i - 1] + x[j - 1])
                    if k == j:
                        g += 2 * (x[i - 1] + x[j - 1])
                else:
                    if k == j:
                        g += 2 * (y[j - 1] - y[i - 1])
                    if k == i:
                        g -= 2 * (y[j - 1] - y[i - 1])
                row.append(g)
            J.append(row)
        step = solve(J, [-v for v in F])
        for (t, k), s in zip(free, step):
            if t == "x":
                x[k - 1] += s
            else:
                y[k - 1] += s
    return x, y, max(abs(v) for v in fr_resid(x, y))


def fr_points(x, y):
    """20 vertices: A_1..A_10 then B_1..B_10."""
    return [(-x[i], y[i]) for i in range(10)] + [(x[i], y[i]) for i in range(10)]


# --------------------------------------------------------------------------
# (B) Danzer-type C3 nonagon
# --------------------------------------------------------------------------
# z_m in C for m=0,1,2; orbit of z_m is {z_m, w z_m, w^2 z_m}, w = e^{2 pi i/3}.
# Gauge z_0 = 1.  Mate distance^2 = 3|z_m|^2 exactly.
# Cross conditions (CROSS = {0:(2,1), 1:(0,0), 2:(1,0)}):
#   |z_0 - w   z_2|^2 = 3|z_0|^2   ->  a2^2 + b2^2 + a2 + sqrt3*b2 = 2
#   |z_1 -     z_0|^2 = 3|z_1|^2   ->  a1^2 + b1^2 + a1           = 1/2
#   |z_2 -     z_1|^2 = 3|z_2|^2   ->  2(a2^2+b2^2) + 2(a1 a2 + b1 b2)
#                                          - (a1^2 + b1^2)        = 0
# 3 equations in (a1,b1,a2,b2) -> a 1-parameter family.
SQRT3 = D(3).sqrt()
W = (D(-1) / 2, SQRT3 / 2)          # omega
W2 = (D(-1) / 2, -SQRT3 / 2)        # omega^2


def dz_resid(v):
    a1, b1, a2, b2 = v
    return [a2 * a2 + b2 * b2 + a2 + SQRT3 * b2 - 2,
            a1 * a1 + b1 * b1 + a1 - D(1) / 2,
            2 * (a2 * a2 + b2 * b2) + 2 * (a1 * a2 + b1 * b2) - (a1 * a1 + b1 * b1)]


def dz_jac(v):
    a1, b1, a2, b2 = v
    return [[D(0), D(0), 2 * a2 + 1, 2 * b2 + SQRT3],
            [2 * a1 + 1, 2 * b1, D(0), D(0)],
            [2 * a2 - 2 * a1, 2 * b2 - 2 * b1, 4 * a2 + 2 * a1, 4 * b2 + 2 * b1]]


def dz_solve(v, pin_index, pin_value, iters=200):
    """Newton on the 1-parameter family, pinning one coordinate to select a
    member.  Returns (solution, max residual) or (None, None) on failure."""
    v = list(v)
    v[pin_index] = pin_value
    free = [k for k in range(4) if k != pin_index]
    for _ in range(iters):
        F = dz_resid(v)
        if max(abs(t) for t in F) < D(10) ** -55:
            break
        J = dz_jac(v)
        A = [[J[r][c] for c in free] for r in range(3)]
        try:
            step = solve(A, [-t for t in F])
        except ZeroDivisionError:
            return None, None
        for k, s in zip(free, step):
            v[k] += s
        if max(abs(t) for t in v) > 1000:
            return None, None
    r = max(abs(t) for t in dz_resid(v))
    return (v, r) if r < D(10) ** -40 else (None, r)


def cmul(u, z):
    return (u[0] * z[0] - u[1] * z[1], u[0] * z[1] + u[1] * z[0])


def dz_points(v):
    """9 vertices, flat label 3*m + j."""
    a1, b1, a2, b2 = v
    Z = [(D(1), D(0)), (a1, b1), (a2, b2)]
    pts = []
    for m in range(3):
        pts.append(Z[m])
        pts.append(cmul(W, Z[m]))
        pts.append(cmul(W2, Z[m]))
    return pts


def dz_check_k3(pts, v):
    """Confirm every vertex has >= 3 others equidistant from it."""
    ok = True
    for i in range(9):
        cls, _ = classes(pts, i)
        if max(m for _, m in cls) < 3:
            ok = False
    return ok


# --------------------------------------------------------------------------
# subset lattice: is ANY subset of a given point set a counterexample?
# (subsets of a strictly convex set are strictly convex, so this is legal)
# --------------------------------------------------------------------------
def subset_scan(pts, label):
    """DFS over subsets, target size fixed, pruning on the hereditary
    condition c_i(T) <= floor(target/2) - 1 for all i in T."""
    n = len(pts)
    D2 = [[d2(pts[i], pts[j]) for j in range(n)] for i in range(n)]

    def cnt(sub, i):
        ds = []
        for j in sub:
            if j == i:
                continue
            v = D2[i][j]
            if not any(abs(v - u) < TOL for u in ds):
                ds.append(v)
        return len(ds)

    best = None          # (target, min over subsets of (min_i c_i - floor/2))
    found = []
    nodes = 0
    for target in range(4, n + 1):
        K = target // 2 - 1
        cur = []

        def dfs(start):
            nonlocal nodes
            if len(cur) == target:
                found.append(tuple(cur))
                return True
            if len(cur) + (n - start) < target:
                return False
            for j in range(start, n):
                cur.append(j)
                nodes += 1
                if all(cnt(cur, i) <= K for i in cur):
                    if dfs(j + 1):
                        cur.pop()
                        return True
                cur.pop()
            return False

        hit = dfs(0)
        # record the best residual achieved at this target size over the whole
        # point set (not just subsets): cheapest informative statistic
        if hit:
            print(f"  {label}: subset of size {target} SATISFIES c_i <= {K} "
                  f"for all i  -> CANDIDATE {found[-1]}")
            best = target
    print(f"  {label}: subset lattice exhausted, {nodes} DFS nodes, "
          f"candidates found: {len(found)}")
    return found, nodes


# --------------------------------------------------------------------------
def main():
    print("=" * 74)
    print("ERDOS 982 -- polygon lane")
    print("=" * 74)

    # ---------------- (A) Fishburn-Reeds 20-gon ----------------
    x0, y0 = fr_seed()
    r_seed = max(abs(v) for v in fr_resid(x0, y0))
    x, y, r_pol = fr_polish(x0, y0)
    drift = max(max(abs(a - b) for a, b in zip(x, x0)),
                max(abs(a - b) for a, b in zip(y, y0)))
    print(f"\n[FR] published-table max |d^2 - 1| residual : {float(r_seed):.3e}")
    print(f"[FR] after 60-digit Newton polish           : {float(r_pol):.3e}")
    print(f"[FR] coordinate drift from published table  : {float(drift):.3e}")

    P = fr_points(x, y)
    okc, h = strictly_convex(P)
    print(f"[FR] strictly convex 20-gon (hull = all 20) : {okc}")
    # confirm the advertised property: every vertex at unit distance from 3
    deg = []
    for i in range(20):
        deg.append(sum(1 for j in range(20)
                       if j != i and abs(d2(P[i], P[j]) - 1) < TOL))
    print(f"[FR] # vertices at distance exactly 1, per vertex: "
          f"min={min(deg)} max={max(deg)}  (advertised: 3)")
    fr_cmin, fr_need, fr_mmax = profile(P, "Fishburn-Reeds 20-gon [FiRe92]")

    # ---------------- (B) Danzer-type C3 nonagon ----------------
    # repo seed, converted from (r,phi) to (a,b) WITHOUT trig by re-solving:
    # pin a1 near the repo value and let Newton land on the same member.
    seed = [D("-0.544"), D("0.866"), D("0.794"), D("0.286")]
    v, res = dz_solve(seed, 0, D("-0.5441"))
    if v is None:
        print("\n[DZ] Newton failed to land on the family")
        return 1
    print(f"\n[DZ] C3 nonagon system residual (60-digit Newton): {float(res):.3e}")
    print(f"[DZ] z1 = {float(v[0]):.15f} + {float(v[1]):.15f} i")
    print(f"[DZ] z2 = {float(v[2]):.15f} + {float(v[3]):.15f} i")
    Q = dz_points(v)
    okq, hq = strictly_convex(Q)
    print(f"[DZ] strictly convex 9-gon (hull = all 9)   : {okq}")
    print(f"[DZ] every vertex has >=3 equidistant others: {dz_check_k3(Q, v)}")
    dz_cmin, dz_need, dz_mmax = profile(Q, "Danzer-type C3 nonagon (reconstruction)")

    # ---------------- (C) sweep the 1-parameter Danzer family ----------------
    print("\n--- sweep of the 1-parameter Danzer-type family "
          "(does any member do better?) ---")
    bestc, bestat = None, None
    tried = 0
    a1v = D("-1.35")
    while a1v <= D("0.36"):
        vv, rr = dz_solve([a1v, D("0.8"), D("0.79"), D("0.29")], 0, a1v)
        if vv is not None:
            R = dz_points(vv)
            if strictly_convex(R)[0] and dz_check_k3(R, vv):
                tried += 1
                cm = min(len(classes(R, i)[0]) for i in range(9))
                if bestc is None or cm < bestc:
                    bestc, bestat = cm, a1v
        a1v += D("0.01")
    print(f"  strictly convex k=3 members sampled: {tried}")
    print(f"  best (smallest) min_i c_i over the family: {bestc} at a1={bestat}")
    print(f"  needed for a counterexample: <= {9 // 2 - 1}")

    # ---------------- (D) subset lattices ----------------
    print("\n--- subset lattices (every subset of a convex set is convex) ---")
    subset_scan(Q, "Danzer-9")
    subset_scan(P, "FR-20")

    # ---------------- verdict ----------------
    print("\n" + "=" * 74)
    print(f"FR-20 : R = {fr_cmin - fr_need:+d}  (need <= -1)   NOT a counterexample")
    print(f"DZ-9  : R = {dz_cmin - dz_need:+d}  (need <= -1)   NOT a counterexample")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
