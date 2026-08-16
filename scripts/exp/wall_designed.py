"""Per-target wall readings, isolated obstructions, and purpose-built families.

Everything here was written after step 1 (read the wall) and step 2 (isolate the
obstruction) for the target in question; the families are the step-4
constructions those two steps pointed at.  The sign checks in `wall_run.py` are
run on the first two members of each family, in the order given, before any
further member is built.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall_arm as W  # noqa: E402


# ---------------------------------------------------------------- constructors
def dstar(a, b):
    edges = [(0, 1)]
    nn = 2
    for _ in range(a):
        edges.append((0, nn)); nn += 1
    for _ in range(b):
        edges.append((1, nn)); nn += 1
    return W.G(nn, edges)


def apex(H):
    edges = [(i + 1, j + 1) for (i, j) in H.edges()]
    edges += [(0, i + 1) for i in range(H.n)]
    return W.G(H.n + 1, edges)


def pendant_apex(H):
    edges = [(i + 2, j + 2) for (i, j) in H.edges()]
    edges += [(1, i + 2) for i in range(H.n)]
    edges += [(0, 1)]
    return W.G(H.n + 2, edges)


def multipartite(parts):
    return W.blowup(W.complete(len(parts)), parts, clique=False)


def amalgam(H, k, v=0):
    """k disjoint copies of H, all identified at vertex v (one cut vertex)."""
    edges = []
    nn = 1
    for _ in range(k):
        mp = {}
        for i in range(H.n):
            if i == v:
                mp[i] = 0
            else:
                mp[i] = nn
                nn += 1
        for (a, b) in H.edges():
            edges.append((mp[a], mp[b]))
    return W.G(nn, edges)


def chain_of_blocks(H, k, a=0, b=1):
    edges = []
    nn = 0
    prev_b = None
    for _ in range(k):
        mp = {}
        for i in range(H.n):
            if i == a and prev_b is not None:
                mp[i] = prev_b
            else:
                mp[i] = nn
                nn += 1
        for (x, y) in H.edges():
            edges.append((mp[x], mp[y]))
        prev_b = mp[b]
    return W.G(nn, edges)


def star_of_stars(d):
    edges = []
    nn = 1
    for i in range(1, d + 1):
        c = nn
        nn += 1
        edges.append((0, c))
        for _ in range(i):
            edges.append((c, nn))
            nn += 1
    return W.G(nn, edges)


def spider(k, L):
    edges = []
    nn = 1
    for _ in range(k):
        prev = 0
        for _ in range(L):
            edges.append((prev, nn))
            prev = nn
            nn += 1
    return W.G(nn, edges)


def caterpillar(L, p):
    edges = [(i, i + 1) for i in range(L - 1)]
    nn = L
    for i in range(1, L - 1):
        for _ in range(p):
            edges.append((i, nn))
            nn += 1
    return W.G(nn, edges)


def disj(*gs):
    cur = gs[0]
    for g in gs[1:]:
        cur = W.disjoint(cur, g)
    return cur


def g6(s):
    return W.from_graph6(s)


def cblow(s, m):
    b = g6(s)
    return W.blowup(b, [m] * b.n, clique=True)


def iblow(s, m):
    b = g6(s)
    return W.blowup(b, [m] * b.n, clique=False)


# --------------------------------------------------------------- the families
# DESIGNED[tid] = list of (transformation name, [(member label, graph), ...])
DESIGNED = {

    "FP-001": [
        ("widen the parts of the tight complete-bipartite wall",
         [("K_{%s}" % ",".join(map(str, p)), multipartite(p))
          for p in [[1, 2], [1, 3], [2, 3], [2, 4], [1, 5], [3, 5], [2, 8], [4, 12], [6, 18]]]),
        ("add a third part (break biregularity)",
         [("K_{%s}" % ",".join(map(str, p)), multipartite(p))
          for p in [[1, 1, 2], [1, 2, 3], [1, 2, 6], [1, 3, 9], [2, 3, 12]]]),
    ],

    "FP-002": [
        ("grow the number of triangles in the apex core",
         [("pendant+(K1 v %dK3)" % j, pendant_apex(disj(*[W.complete(3)] * j)))
          for j in range(1, 6)]),
        ("swap the core for one with smaller alpha+chi",
         [("pendant+(K1 v C5)", pendant_apex(W.cycle(5))),
          ("pendant+(K1 v (C5 u K3))", pendant_apex(disj(W.cycle(5), W.complete(3)))),
          ("pendant+(K1 v Petersen)", pendant_apex(W.kneser(5, 2)))]),
    ],

    "FP-007": [
        ("stretch the tight path by one vertex",
         [("P_%d" % L, W.path(L)) for L in range(7, 15)]),
        ("subdivide every edge of the tight P_8",
         [("sub^%d(P_8)" % k, W.subdivide(g6("G_CKJ?"), k)) for k in (0, 1, 2)]),
    ],

    "FP-008": [
        ("grow the tight star by one leaf",
         [("K_{1,%d}" % s, W.star(s)) for s in range(4, 14)]),
        ("index the star family by ceil(lambda_1)=k, i.e. s=k^2 (where the floor steps)",
         [("K_{1,%d}" % (k * k), W.star(k * k)) for k in range(2, 6)]),
    ],

    "FP-009": [
        ("corona: hang a pendant on every vertex of the tight member",
         [("(G@KqS[) o %dK1" % k, W.corona(g6("G@KqS["), k) if k else g6("G@KqS["))
          for k in (0, 1, 2)]),
    ],

    "FP-010": [
        ("subdivision of K_k (an independent gamma-set with all outside degrees 2)",
         [("sub(K_%d)" % k, W.subdivide(W.complete(k), 1)) for k in (3, 4, 5, 6, 7)]),
        ("friendship graphs (C4-free, gamma = 1)",
         [("F_%d" % k, amalgam(W.cycle(3), k)) for k in (1, 2, 3, 5, 8)]),
    ],

    "FP-011": [
        ("stretch: Tdist_min ~ n^2/4 against m = n-1",
         [("P_%d" % L, W.path(L)) for L in [4, 6, 9, 12, 16, 20, 26]]),
        ("spider: keep gamma low while Tdist_min grows",
         [("spider(3,%d)" % L, spider(3, L)) for L in [1, 2, 4, 6, 8]]),
    ],

    "FP-012": [
        ("corona of a diameter-2 core: pins dist_even_max at n/2, pushes gamma_2 to n/2+gamma(core)",
         [("(%s) o K1" % nm, W.corona(h, 1)) for nm, h in
          [("K3", W.complete(3)), ("C5", W.cycle(5)), ("C6", W.cycle(6)),
           ("C7", W.cycle(7)), ("Petersen", W.kneser(5, 2))]]),
        ("corona of the tight 8-vertex trees",
         [("(GHCGdO) o %dK1" % k, W.corona(g6("GHCGdO"), k) if k else g6("GHCGdO"))
          for k in (0, 1)]),
    ],

    "FP-013": [
        ("flower: add petals; Delta grows by 2 per petal, Sigma_2 pinned at 2",
         [("flower_C3^%d" % k, amalgam(W.cycle(3), k)) for k in [2, 3, 4, 6, 8, 10]]),
        ("hub joined to a perfect matching",
         [("apex(%dK_2)" % k, apex(W.blowup(W.G(k, []), [2] * k, clique=True)))
          for k in [2, 3, 4, 6, 8, 10]]),
    ],

    "FP-014": [
        ("prism: G x K_k doubles dist_even_min while gamma_2 only doubles",
         [("(GC|v~w) x K_%d" % k, g6("GC|v~w") if k == 1 else
           W.cartesian(g6("GC|v~w"), W.complete(k))) for k in (1, 2, 3)]),
        ("line graph of the tight member",
         [("GC|v~w", g6("GC|v~w")), ("L(GC|v~w)", W.line_graph(g6("GC|v~w")))]),
    ],

    "FP-015": [
        ("grow both leaf sets of the tight double star S(3,3)",
         [("S(%d,%d)" % (a, a), dstar(a, a)) for a in range(1, 8)]),
        ("independent blow-up of the tight member",
         [("(G_ACDo)[I%d]" % m, iblow("G_ACDo", m)) for m in (1, 2, 3)]),
    ],

    "FP-016": [
        ("independent blow-up: alpha and gamma_i scale, gamma stays 2",
         [("(G@N~vo)[I%d]" % m, iblow("G@N~vo", m)) for m in (1, 2, 3, 4)]),
    ],

    "FP-017": [
        ("lengthen the caterpillar spine: one new cut vertex per step",
         [("caterpillar(%d,1)" % L, caterpillar(L, 1)) for L in [4, 5, 6, 8, 10, 14]]),
        ("chain of triangles: one new cut vertex per block",
         [("chain_K3^%d" % k, chain_of_blocks(W.cycle(3), k, 0, 1)) for k in [2, 3, 4, 6, 8]]),
    ],

    "FP-018": [
        ("raise disp_min while holding gamma (regularise the neighbourhoods)",
         [("K_{%d,%d}" % (a, a), W.complete_bipartite(a, a)) for a in (2, 3, 4, 6)]),
    ],

    "FP-019": [
        ("kill the triangles and hold kappa (cycles and their blow-ups)",
         [("C_%d" % L, W.cycle(L)) for L in (5, 7, 9, 13, 21)]),
    ],

    "FP-020": [
        ("force every vertex to see many distinct degrees, keep one cut vertex",
         [("K1 v (K_{1..%d} u K1)" % k,
           apex(W.disjoint(multipartite(list(range(1, k + 1))), W.G(1, []))))
          for k in range(2, 7)]),
        ("index by q = the integer value of the floor term",
         [("q=0: K1 v (K_{1,2} u K1)", apex(W.disjoint(multipartite([1, 2]), W.G(1, [])))),
          ("q=1: K1 v (K_{1..5} u K1)",
           apex(W.disjoint(multipartite([1, 2, 3, 4, 5]), W.G(1, [])))),
          ("q=2: K1 v (K_{1..8} u K1)",
           apex(W.disjoint(multipartite([1, 2, 3, 4, 5, 6, 7, 8]), W.G(1, []))))]),
    ],

    "FP-021": [
        ("grow the bipartite lobe of the glued pair",
         [("2 x K_{%d,%d} glued" % (a, a), amalgam(W.complete_bipartite(a, a), 2))
          for a in (2, 3, 4, 5)]),
        ("amalgamate k lobes of K_{4,4} at one vertex (kappa drops to 1)",
         [("%d x K_{4,4} glued" % k, amalgam(W.complete_bipartite(4, 4), k))
          for k in (1, 2, 3, 4)]),
    ],

    "FP-022": [
        ("line graph: dd rises, lambda_max stays 2 on a locally-bipartite wall",
         [("GBj]j{", g6("GBj]j{")), ("L(GBj]j{)", W.line_graph(g6("GBj]j{")))]),
    ],

    "FP-023": [
        ("stretch the tight path P_8",
         [("P_%d" % L, W.path(L)) for L in range(7, 16)]),
        ("corona of the tight member (pendants force gamma_2 up, lambda_max pinned)",
         [("(GBO`MO) o %dK1" % k, W.corona(g6("GBO`MO"), k) if k else g6("GBO`MO"))
          for k in (0, 1)]),
    ],

    "FP-024": [
        ("push the matching past ceil(n/2) (regular and near-regular blow-ups)",
         [("(G?F~vo)[K%d]" % m, cblow("G?F~vo", m)) for m in (1, 2, 3)]),
    ],

    "FP-025": [
        ("raise lam_min against delta (complete multipartite, then blow-ups)",
         [("K_{%d,%d}" % (a, a), W.complete_bipartite(a, a)) for a in (2, 3, 4, 6)]),
        ("cocktail-party graphs: delta = n-2, lam_min = 2",
         [("K_%dx2" % k, multipartite([2] * k)) for k in (2, 3, 4, 6, 8)]),
    ],

    "FP-026": [
        ("star of stars: raise disp_max (distinct branch degrees) against floor(lambda_1)",
         [("SoS(%d)" % d, star_of_stars(d)) for d in range(2, 12)]),
        ("index by q = the value of the RHS floor term",
         [("q=2: SoS(2)", star_of_stars(2)), ("q=3: SoS(9)", star_of_stars(9))]),
    ],

    "FP-027": [
        ("push ecc_avg towards 2*rad (bipartite, all-peripheral)",
         [("C_%d" % L, W.cycle(L)) for L in (6, 8, 12, 16, 24)]),
        ("caterpillar / broom: many peripheral vertices, one centre",
         [("caterpillar(%d,2)" % L, caterpillar(L, 2)) for L in (4, 5, 6, 8, 10)]),
    ],

    "FP-028": [
        ("break res <= alpha + CW - 1 by driving CW below 1 (impossible; blow-ups tried)",
         [("K_%d" % k, W.complete(k)) for k in (2, 3, 5, 8, 12)]),
    ],

    "FP-029": [
        ("clique blow-up of the tight 8-vertex tree-like member",
         [("(G@O_n?)[K%d]" % m, cblow("G@O_n?", m)) for m in (1, 2, 3, 4)]),
        ("corona of the same member",
         [("(G@O_n?) o %dK1" % k, W.corona(g6("G@O_n?"), k) if k else g6("G@O_n?"))
          for k in (0, 1, 2)]),
    ],

    "FP-030": [
        ("join a dominating clique: dd jumps by one, gamma_t and res pinned",
         [("(G?\\~f[) + K%d" % k, g6("G?\\~f[") if k == 0 else
           W.join(g6("G?\\~f["), W.complete(k))) for k in (0, 1, 2, 3)]),
    ],
}
