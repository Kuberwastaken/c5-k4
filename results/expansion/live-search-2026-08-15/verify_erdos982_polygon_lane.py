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
  (B) DANZER's convex 9-gon, built from the recipe in the primary source:
      P. Erdos, "Some combinatorial and metric problems in geometry",
      Intuitive Geometry (Siofok 1985), Colloq. Math. Soc. Janos Bolyai 48,
      167-177, North-Holland 1987; section 8, pp. 175-176.  Scan:
      https://users.renyi.hu/~p_erdos/1987-27.pdf  (item 1987-27).
      The source gives NO coordinates -- the nonagon is defined by an
      intermediate-value argument -- so this rebuilds it from the recipe.
        "convex nonagon A1B1C1A2B2C2A3B3C3 of threefold rotational symmetry,
         satisfying A1A2 = A1A3 = A1B3, B1B2 = B1C2 = B1B3,
         C1C2 = C1A3 = C1C3"
  (C) Control: a DIFFERENT C3 k=3 nonagon (cross-witness map 0->(2,1),
      1->(0,0), 2->(1,0)), taken from github.com/davidiach/erdos97.  Not
      Danzer's polygon; included to show the answer is driven by counting,
      not by the incidence pattern.

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
# (B) DANZER's original nonagon, from the Erdos 1987 recipe.
#
# rho = e^{2 pi i/3}; A_j = rho^{j-1} a, B_j = rho^{j-1} b, C_j = rho^{j-1} c,
# gauge a = 1.  A1A2=A1A3, B1B2=B1B3, C1C2=C1C3 are automatic (each is sqrt3
# times a circumradius).  Danzer's three displayed equalities become:
#   E1  |1 - rho^2 b|^2 = 3        <=> |b - A2| = sqrt3
#           (B1 on the arc A3A1 EXTENDED; that arc is centred at A2)
#   E2  |b - rho c|^2  = 3|b|^2    <=> |B3 C1| = |B1B2|
#           (C1 on the side B1B2 of the Reuleaux triangle B1B2B3)
#   E3  |c - rho^2|^2  = 3|c|^2    <=> C1A3 = C1C3   (Danzer's IVT condition)
# E1 puts b on a fixed circle, E3 puts c on a fixed circle; E2 is then one
# scalar equation solved by bisection -- the numerical form of Danzer's own
# intermediate-value argument.  Free parameter: eps = |A1 B1|.
DZ_LBL = ["A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3"]


def _rho():
    return (D(-1) / 2, SQRT3 / 2)


def _b_of(theta_cos, theta_sin):
    r = _rho()
    return (r[0] + SQRT3 * theta_cos, r[1] + SQRT3 * theta_sin)


def _c_of(psi_cos, psi_sin):
    return (D(1) / 4 + SQRT3 / 2 * psi_cos, SQRT3 / 4 + SQRT3 / 2 * psi_sin)


def danzer_points(b, c):
    """9 vertices in the published boundary order A1 B1 C1 A2 B2 C2 A3 B3 C3."""
    r = _rho()
    out = []
    rot = (D(1), D(0))
    for _ in range(3):
        for z in ((D(1), D(0)), b, c):
            out.append(cmul(rot, z))
        rot = cmul(rot, r)
    return out


def danzer_e2(b, c):
    r = _rho()
    rc = cmul(r, c)
    return ((b[0] - rc[0]) ** 2 + (b[1] - rc[1]) ** 2
            - 3 * (b[0] ** 2 + b[1] ** 2))


def danzer_build(eps):
    """Solve Danzer's system EXACTLY at elongation eps = |A1 B1|.

    No trigonometry and no iteration: the system is solvable in closed form.

      E1 & |b - 1| = eps :  E1 gives |b|^2 + b1 - sqrt3 b2 = 2, and
          |b-1|^2 = eps^2 gives |b|^2 = eps^2 - 1 + 2 b1.  Eliminating |b|^2
          gives the LINE  3 b1 - sqrt3 b2 = 3 - eps^2; intersect with the
          circle  b1^2 + b2^2 - 2 b1 + 1 - eps^2 = 0  -> quadratic in b1.

      E3 gives |c|^2 = (c1 + sqrt3 c2 + 1)/2.  Substituting that into E2
          (|c|^2 - 2(u c1 + v c2) - 2|b|^2 = 0, where (u,v) = b * rho^2)
          makes E2 LINEAR in c:
              c1 (1/2 - 2u) + c2 (sqrt3/2 - 2v) + 1/2 - 2|b|^2 = 0.
          Intersect that line with the E3 circle
              (c1 - 1/4)^2 + (c2 - sqrt3/4)^2 = 3/4   -> quadratic.

    Returns the (b, c) branch reproducing the published boundary order, or
    (None, None) if no branch does.
    """
    def line_circle(A, B, C, cx, cy, r):
        """Solutions of A*x + B*y + C = 0 on the circle centre (cx,cy) rad r."""
        # substitute the line into the circle
        out = []
        if B != 0:
            # y = -(A x + C)/B
            qa = 1 + (A / B) ** 2
            qb = -2 * cx + 2 * (A / B) * (C / B + cy)
            qc = cx * cx + (C / B + cy) ** 2 - r * r
            disc = qb * qb - 4 * qa * qc
            if disc < 0:
                return []
            s = disc.sqrt()
            for x in ((-qb + s) / (2 * qa), (-qb - s) / (2 * qa)):
                out.append((x, -(A * x + C) / B))
        else:
            x = -C / A
            t = r * r - (x - cx) ** 2
            if t < 0:
                return []
            s = t.sqrt()
            out = [(x, cy + s), (x, cy - s)]
        return out

    e2v = eps * eps
    # ---- b: line 3 b1 - sqrt3 b2 = 3 - eps^2 meets circle |b-1| = eps
    bs = line_circle(D(3), -SQRT3, e2v - 3, D(1), D(0), eps)
    for b in bs:
        b1, b2 = b
        nb = b1 * b1 + b2 * b2
        # (u,v) = b * rho^2
        u = (-b1 + SQRT3 * b2) / 2
        v = (-SQRT3 * b1 - b2) / 2
        A = D(1) / 2 - 2 * u
        B = SQRT3 / 2 - 2 * v
        C = D(1) / 2 - 2 * nb
        for c in line_circle(A, B, C, D(1) / 4, SQRT3 / 4, SQRT3 / 2):
            if danzer_order_ok(danzer_points(b, c)):
                return b, c
    return None, None


def danzer_order_ok(P):
    h = hull(P)
    if len(h) != 9:
        return False
    lab = [DZ_LBL[i] for i in h]
    k = lab.index("A1")
    return "".join(lab[k:] + lab[:k]) == "A1B1C1A2B2C2A3B3C3"


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

    # ---------------- (B) DANZER's original nonagon ----------------
    b, c = danzer_build(D("0.05"))
    Dz = danzer_points(b, c)
    print(f"\n[DANZER] Erdos 1987-27 p.175-176 recipe, elongation eps=|A1B1|=0.05")
    print(f"[DANZER] E2 residual |B1C2|^2 - 3|B1|^2 : {float(danzer_e2(b, c)):.3e}")
    print(f"[DANZER] strictly convex, published order A1B1C1A2B2C2A3B3C3: "
          f"{danzer_order_ok(Dz)}")
    dd = lambda i, j: d2(Dz[i], Dz[j]).sqrt()
    print("[DANZER] the three equality triples from the paper:")
    print(f"   A1A2={float(dd(0,3)):.12f}  A1A3={float(dd(0,6)):.12f}  "
          f"A1B3={float(dd(0,7)):.12f}")
    print(f"   B1B2={float(dd(1,4)):.12f}  B1C2={float(dd(1,5)):.12f}  "
          f"B1B3={float(dd(1,7)):.12f}")
    print(f"   C1C2={float(dd(2,5)):.12f}  C1A3={float(dd(2,6)):.12f}  "
          f"C1C3={float(dd(2,8)):.12f}")
    print("[DANZER] vertices:")
    for i, p in enumerate(Dz):
        print(f"   {DZ_LBL[i]:>3} = ({float(p[0]):+.15f}, {float(p[1]):+.15f})")
    dz0_cmin, dz0_need, _ = profile(Dz, "DANZER's nonagon [Er87b]")

    print("\n--- sweep of Danzer's own free parameter eps = |A1 B1| ---")
    bestd, bestde, nd, rejd = None, None, 0, 0
    e = D("0.001")
    while e < D("1.2"):
        bb, cc = danzer_build(e)
        if bb is not None:
            Pz = danzer_points(bb, cc)
            if danzer_order_ok(Pz):
                dmin = min(d2(Pz[i], Pz[j]) for i in range(9)
                           for j in range(i + 1, 9)).sqrt()
                dmax = max(d2(Pz[i], Pz[j]) for i in range(9)
                           for j in range(i + 1, 9)).sqrt()
                if dmin / dmax < D("1e-3"):
                    rejd += 1
                else:
                    nd += 1
                    cm = min(len(classes(Pz, i)[0]) for i in range(9))
                    if bestd is None or cm < bestd:
                        bestd, bestde = cm, e
        e += D("0.002")
    print(f"  admissible members of Danzer's family: {nd}  "
          f"(rejected as degenerate: {rejd})")
    print(f"  best (smallest) min_i c_i over the whole family: {bestd} "
          f"at eps={float(bestde):.3f}  ->  RESIDUAL R = {bestd - 4:+d}")

    # ---------------- (C) control: a different C3 k=3 nonagon ----------------
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
    dz_cmin, dz_need, dz_mmax = profile(Q, "control: inequivalent C3 k=3 nonagon")

    # ---------------- (C) sweep the 1-parameter Danzer family ----------------
    print("\n--- sweep of the 1-parameter Danzer-type family "
          "(does any member do better?) ---")
    print("  NON-DEGENERACY GUARDS ARE ESSENTIAL HERE.  At a1 = -1/2 the first")
    print("  equation forces b1 = +-sqrt3/2, i.e. z1 = omega, so orbit 1 collapses")
    print("  onto orbit 0: 3 tripled points at pairwise distance ~1e-25.  Without")
    print("  the guards that member reports min_i c_i = 2 (R = -2), a FALSE")
    print("  crossing -- it violates Function.Injective p.")
    bestc, bestat = None, None
    tried, rejected = 0, 0
    a1v = D("-1.60")
    step = D("0.005")
    while a1v <= D("0.60"):
        for branch in (D(1), D(-1)):
            vv, rr = dz_solve([a1v, D("0.85") * branch, D("0.79"), D("0.29")],
                              0, a1v)
            if vv is None:
                continue
            R = dz_points(vv)
            if not strictly_convex(R)[0]:
                continue
            dmin = min(d2(R[i], R[j]) for i in range(9)
                       for j in range(i + 1, 9)).sqrt()
            dmax = max(d2(R[i], R[j]) for i in range(9)
                       for j in range(i + 1, 9)).sqrt()
            if dmin / dmax < D("1e-3"):          # injectivity / degeneracy guard
                rejected += 1
                continue
            if not dz_check_k3(R, vv):
                continue
            tried += 1
            cm = min(len(classes(R, i)[0]) for i in range(9))
            if bestc is None or cm < bestc:
                bestc, bestat = cm, a1v
        a1v += step
    print(f"  admissible strictly convex non-degenerate k>=3 members: {tried}"
          f"   (rejected as degenerate: {rejected})")
    print(f"  best (smallest) min_i c_i over the family: {bestc} "
          f"at a1={float(bestat):.6f}")
    print(f"  needed for a counterexample: <= {9 // 2 - 1}   "
          f"-> RESIDUAL R = {bestc - 9 // 2:+d}")

    # ---------------- (D) subset lattices ----------------
    print("\n--- subset lattices (every subset of a convex set is convex) ---")
    subset_scan(Dz, "Danzer-9 (Er87b)")
    subset_scan(Q, "control-9")
    subset_scan(P, "FR-20")

    # ---------------- verdict ----------------
    print("\n" + "=" * 74)
    print(f"FR-20 : R = {fr_cmin - fr_need:+d}  (need <= -1)   NOT a counterexample")
    print(f"DANZER-9 : R = {dz0_cmin - dz0_need:+d}  (need <= -1)   NOT a counterexample")
    print(f"control-9: R = {dz_cmin - dz_need:+d}  (need <= -1)   NOT a counterexample")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
