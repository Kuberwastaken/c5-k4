"""Exact graph-invariant vocabulary for the v2 fresh-population generator.

Every value is an exact `int` or `fractions.Fraction`; no floating-point value
enters any quantity a conjecture can depend on.

What changed from v1 (``scripts/gen/invariants.py``)
----------------------------------------------------
1. **The hereditary induced invariants are first-class and emitted.**
   ``f`` (largest induced forest), ``b`` (largest induced bipartite subgraph),
   ``tree`` (largest induced tree) and ``path`` (largest induced path) join
   ``alpha`` in the emission vocabulary.  v1 computed ``f``/``b`` but forbade
   their use, and never had ``tree``/``path`` at all -- which removed exactly the
   invariants the tested mechanism is about (``results/experiment-v2/DESIGN.md``).
   Cost is managed by an evaluation-order cap plus branch-and-bound with early
   exit (``scripts/gen2/bench_hereditary.py`` measures it), not by dropping them.

2. **The two backends no longer share a polynomial core.**  In v1 both backends
   called one ``_poly_part``, so a bug there was invisible to the cross-check --
   which is precisely how the ``ceil(lambda_1)`` defect reached the frozen
   population (METHOD v1.7 R4).  Here the two backends share **no** code:

     backend ``A`` ("brute")  pure bit-mask arithmetic, own graph6 decoder, no
                              networkx at all; every NP-hard invariant by
                              exhaustive subset enumeration in decreasing (or
                              increasing) size order with early exit.
     backend ``B`` ("alt")    networkx for everything networkx can do; the
                              spectral bracket from the exact integer
                              characteristic polynomial (Newton's identities)
                              and a Taylor-positivity test; the chromatic number
                              by an independent-set cover DP over subsets; the
                              matching number by networkx's blossom code; every
                              other NP-hard invariant by the branch-and-bound
                              solvers that an arm would actually run at
                              n = 20..40.

   ``scripts/gen2/crossval.py`` requires the two to agree on every invariant over
   every member of ``D2`` before the population is frozen.

3. **The v1 ``ceil(lambda_1)`` defect is not reproduced.**  v1 declared
   ``lambda_1`` an integer when ``det(floor(lambda_1) I - A) == 0``, which fires
   whenever *any* eigenvalue equals ``floor(lambda_1)``.  Backend A now also
   requires ``floor(lambda_1) I - A`` to be positive **semi**definite, so no
   smaller eigenvalue can trigger it; backend B decides the same question from
   the characteristic polynomial by a completely different route.

Conventions pinned here (the sources leave them open)
-----------------------------------------------------
  * ``girth``: number of vertices of a shortest cycle; **``n + 1`` if acyclic**.
    Any cycle of an n-vertex graph has at most n vertices, so inside the finite
    universe of quantification ``n+1`` behaves exactly like ``+inf`` while every
    statement stays finitely checkable.
  * ``dist_even(v)``: counts ``v`` itself (distance 0 is even).
  * ``f``, ``b``, ``tree``, ``path`` are **orders** -- numbers of vertices of a
    largest induced forest / bipartite subgraph / tree / path.  A single vertex
    is a tree and a path, so on a connected graph with n >= 2 all four are >= 2.
    This is the convention under which the campaign's C5[K_m] case study reads
    ``f = b = tree = 4``.
  * ``gamma_2``: every vertex outside the set has at least two neighbours in it
    (a vertex settles its own constraint by being selected).

Excluded from the vocabulary on purpose:
  * ``maxine`` -- the greedy "remove a maximum-degree vertex" process is
    tie-break dependent and therefore not an isomorphism invariant.
  * ``p(G)`` (path covering number), ``L_s``/``gamma_c`` (max-leaf spanning tree
    / connected domination), ``alpha'`` (critical independence) -- no exact
    solver here decides them, and no ILP solver is installed.
"""
from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

POPCNT = bytes(bin(i).count("1") for i in range(1 << 16))


def _pc(x: int) -> int:
    c = 0
    while x:
        c += POPCNT[x & 0xFFFF]
        x >>= 16
    return c


# --------------------------------------------------------------------------
# vocabulary declaration
# --------------------------------------------------------------------------
# tier: "P"  polynomial / trivial
#       "N"  NP-hard
#       "H"  NP-hard *and* hereditary-induced (the v2 restriction is about these)
INT_INVARIANTS = [
    # order / size / degrees
    ("n", "P"), ("m", "P"), ("Delta", "P"), ("delta", "P"),
    ("sigma2", "P"), ("Sigma2", "P"), ("dd", "P"), ("f1", "P"),
    # degree-sequence machinery
    ("res", "P"), ("annih", "P"), ("SW", "P"),
    # distance
    ("diam", "P"), ("rad", "P"), ("girth", "P"),
    ("dist_even_min", "P"), ("dist_even_max", "P"),
    ("Tdist_min", "P"), ("Tdist_max", "P"),
    # connectivity / counting / spectral
    ("kappa", "P"), ("cutv", "P"), ("tri", "P"),
    ("disp_max", "P"), ("disp_min", "P"),
    ("spec_floor", "P"), ("spec_ceil", "P"),
    # clique / colouring / matching
    ("omega", "N"), ("chi", "N"), ("mu", "P"),
    ("lam_max", "N"), ("lam_min", "N"),
    # domination family
    ("gamma", "N"), ("gamma_t", "N"), ("gamma_2", "N"), ("gamma_i", "N"),
    # hereditary induced invariants -- the point of v2
    ("alpha", "H"), ("f", "H"), ("b", "H"), ("tree", "H"), ("path", "H"),
    # 0/1 characteristic functions (Graffiti correction terms)
    ("chi_bip", "P"), ("chi_K3free", "P"), ("chi_C4free", "P"),
    ("chi_claw", "P"), ("chi_reg", "P"), ("chi_tree", "P"),
]
FRAC_INVARIANTS = [
    ("deg_avg", "P"), ("ecc_avg", "P"), ("dist_avg", "P"), ("CW", "P"),
    ("lam_avg", "N"), ("disp_avg", "P"),
]
VOCAB = [k for k, _ in INT_INVARIANTS] + [k for k, _ in FRAC_INVARIANTS]
TIER = dict(INT_INVARIANTS + FRAC_INVARIANTS)

# The defining restriction of the v2 population: every emitted target must use at
# least one of these.  `alpha`, `f`, `b`, `tree`, `path` are exactly the
# hereditary induced invariants named in results/experiment-v2/DESIGN.md.
HEREDITARY = ("alpha", "f", "b", "tree", "path")

DISPLAY = {
    "n": "n", "m": "m", "Delta": "Delta", "delta": "delta",
    "sigma2": "sigma_2", "Sigma2": "Sigma_2", "dd": "dd", "f1": "f_1",
    "res": "res", "annih": "A", "SW": "SW",
    "diam": "diam", "rad": "rad", "girth": "girth",
    "dist_even_min": "dist_even_min", "dist_even_max": "dist_even_max",
    "Tdist_min": "Tdist_min", "Tdist_max": "Tdist_max",
    "kappa": "kappa", "cutv": "cutv", "tri": "t",
    "disp_max": "disp_max", "disp_min": "disp_min",
    "spec_floor": "floor(lambda_1)", "spec_ceil": "ceil(lambda_1)",
    "alpha": "alpha", "omega": "omega", "chi": "chi", "mu": "mu",
    "lam_max": "lambda_max", "lam_min": "lambda_min",
    "gamma": "gamma", "gamma_t": "gamma_t", "gamma_2": "gamma_2",
    "gamma_i": "gamma_i",
    "f": "f", "b": "b", "tree": "tree", "path": "path",
    "chi_bip": "chi_bipartite", "chi_K3free": "chi_K3free",
    "chi_C4free": "chi_C4free", "chi_claw": "chi_clawfree",
    "chi_reg": "chi_regular", "chi_tree": "chi_tree",
    "deg_avg": "deg_avg", "ecc_avg": "ecc_avg", "dist_avg": "dist_avg",
    "CW": "CW", "lam_avg": "lambda_avg", "disp_avg": "disp_avg",
}

DEFINITION = {
    "n": "number of vertices",
    "m": "number of edges",
    "Delta": "maximum degree",
    "delta": "minimum degree",
    "sigma2": "second smallest degree of the degree sequence",
    "Sigma2": "second largest degree of the degree sequence",
    "dd": "number of distinct degrees",
    "f1": "number of degree-1 (pendant) vertices",
    "res": "residue: number of zeros left by the Havel-Hakimi process",
    "annih": "annihilation number: largest k with the k smallest degrees summing to at most m",
    "SW": "Szekeres-Wilf invariant: max over subgraphs of the minimum degree (degeneracy)",
    "diam": "diameter", "rad": "radius",
    "girth": "girth (number of vertices of a shortest cycle); n+1 if G is acyclic",
    "dist_even_min": "min over v of #{u : dist(v,u) even}, counting v itself",
    "dist_even_max": "max over v of #{u : dist(v,u) even}, counting v itself",
    "Tdist_min": "min over v of the total distance sum_u dist(v,u)",
    "Tdist_max": "max over v of the total distance sum_u dist(v,u)",
    "kappa": "vertex connectivity",
    "cutv": "number of cut vertices",
    "tri": "number of triangles",
    "disp_max": "max over v of the number of distinct degrees among the neighbours of v",
    "disp_min": "min over v of the number of distinct degrees among the neighbours of v",
    "spec_floor": "floor of the adjacency spectral radius (exact)",
    "spec_ceil": "ceiling of the adjacency spectral radius (exact)",
    "alpha": "independence number: order of a largest induced edgeless subgraph",
    "omega": "clique number",
    "chi": "chromatic number",
    "mu": "matching number",
    "lam_max": "max over v of the local independence lambda(v) = alpha(G[N(v)])",
    "lam_min": "min over v of the local independence lambda(v) = alpha(G[N(v)])",
    "gamma": "domination number",
    "gamma_t": "total domination number",
    "gamma_2": "2-domination number",
    "gamma_i": "independent domination number",
    "f": "forest number: order of a largest induced forest",
    "b": "bipartite number: order of a largest induced bipartite subgraph",
    "tree": "tree number: order of a largest induced tree",
    "path": "path number: order (vertex count) of a largest induced path",
    "chi_bip": "1 if G is bipartite, else 0",
    "chi_K3free": "1 if G is triangle-free, else 0",
    "chi_C4free": "1 if G contains no 4-cycle (not necessarily induced), else 0",
    "chi_claw": "1 if G is claw-free (no induced K_{1,3}), else 0",
    "chi_reg": "1 if G is regular, else 0",
    "chi_tree": "1 if G is a tree, else 0",
    "deg_avg": "average degree 2m/n",
    "ecc_avg": "average eccentricity",
    "dist_avg": "average distance over unordered pairs of distinct vertices",
    "CW": "Caro-Wei invariant sum_v 1/(1+deg v)",
    "lam_avg": "average over v of lambda(v) = alpha(G[N(v)])",
    "disp_avg": "average over v of the number of distinct degrees among the neighbours of v",
}

# How each invariant is computed on each side of the R4 cross-check.  Printed
# verbatim into the generation record so the independence claim is auditable.
CROSSCHECK_PATHS = {
    "n": ("bit-mask decode of graph6", "networkx G.number_of_nodes"),
    "m": ("sum of pop-counts / 2", "networkx G.number_of_edges"),
    "Delta": ("sorted pop-count degree list", "max(dict(G.degree).values())"),
    "delta": ("sorted pop-count degree list", "min(dict(G.degree).values())"),
    "sigma2": ("sorted pop-count degree list", "sorted networkx degree list"),
    "Sigma2": ("sorted pop-count degree list", "sorted networkx degree list"),
    "dd": ("set of pop-count degrees", "set of networkx degrees"),
    "f1": ("count of pop-count degrees == 1", "count of networkx degrees == 1"),
    "res": ("Havel-Hakimi: pop the largest degree, decrement, re-sort the list",
            "Havel-Hakimi in counting-array form, no list is ever re-sorted"),
    "annih": ("early-exit prefix loop over the ascending degree sequence",
              "itertools.accumulate over the networkx degree sequence, counting "
              "prefixes with sum <= m"),
    "SW": ("repeated minimum-degree deletion on bit-masks", "max(networkx.core_number)"),
    "diam": ("own bit-mask BFS from every vertex", "networkx.eccentricity"),
    "rad": ("own bit-mask BFS from every vertex", "networkx.eccentricity"),
    "girth": ("own BFS cross-edge scan", "min over edges e of 1 + dist_{G-e}(u,v) (networkx)"),
    "dist_even_min": ("own bit-mask BFS", "networkx.all_pairs_shortest_path_length"),
    "dist_even_max": ("own bit-mask BFS", "networkx.all_pairs_shortest_path_length"),
    "Tdist_min": ("own bit-mask BFS", "networkx.all_pairs_shortest_path_length"),
    "Tdist_max": ("own bit-mask BFS", "networkx.all_pairs_shortest_path_length"),
    "kappa": ("exhaustive search for a smallest vertex cut over all 2^n subsets",
              "networkx.node_connectivity (max-flow)"),
    "cutv": ("delete v, own BFS connectivity test", "networkx.articulation_points"),
    "tri": ("pop-count of common neighbourhoods over edges", "networkx.triangles"),
    "disp_max": ("bit-mask neighbourhood degree sets", "networkx neighbour iteration"),
    "disp_min": ("bit-mask neighbourhood degree sets", "networkx neighbour iteration"),
    "spec_floor": ("Sylvester leading-minor definiteness of kI-A (Bareiss, integer)",
                   "integer characteristic polynomial (Newton identities) + Taylor positivity"),
    "spec_ceil": ("as spec_floor, plus a positive-semidefiniteness test of floor(l1)I-A",
                  "characteristic polynomial: l1 is an integer iff chi(fl)=0 and all "
                  "higher derivatives at fl are positive"),
    "alpha": ("exhaustive 2^n subset scan, descending size, early exit",
              "greedy-clique-cover-bounded branch and bound"),
    "omega": ("exhaustive 2^n subset scan, descending size, early exit",
              "branch and bound on the complement"),
    "chi": ("DSATUR branch and bound", "independent-set cover DP over all 2^n subsets"),
    "mu": ("maximum-matching DP over all 2^n subsets", "networkx.max_weight_matching"),
    "lam_max": ("exhaustive independent sets inside each neighbourhood",
                "branch and bound inside each neighbourhood"),
    "lam_min": ("exhaustive independent sets inside each neighbourhood",
                "branch and bound inside each neighbourhood"),
    "gamma": ("exhaustive 2^n subset scan, ascending size, early exit",
              "packing-bounded branch and bound"),
    "gamma_t": ("exhaustive 2^n subset scan, ascending size, early exit",
                "packing-bounded branch and bound"),
    "gamma_2": ("exhaustive 2^n subset scan, ascending size, early exit",
                "packing-bounded branch and bound"),
    "gamma_i": ("exhaustive 2^n subset scan, ascending size, early exit",
                "packing-bounded branch and bound"),
    "f": ("exhaustive 2^n subset scan, descending size, early exit",
          "branch on a shortest cycle, bounded by a disjoint cycle packing"),
    "b": ("exhaustive 2^n subset scan, descending size, early exit",
          "branch on a shortest odd cycle, bounded by a disjoint odd-cycle packing"),
    "tree": ("exhaustive 2^n subset scan, descending size, early exit",
             "connected-expansion branch and bound with a reachability bound"),
    "path": ("exhaustive 2^n subset scan, descending size, early exit",
             "endpoint-growth branch and bound with a reachability bound"),
    "chi_bip": ("own 2-colouring BFS", "networkx.is_bipartite"),
    "chi_K3free": ("triangle count == 0 (bit-mask)", "networkx.triangles"),
    "chi_C4free": ("|N(u) & N(v)| >= 2 scan over pairs", "itertools over 4-subsets"),
    "chi_claw": ("bit-mask scan over neighbour triples", "itertools over 4-subsets"),
    "chi_reg": ("Delta == delta on pop-counts", "len(set(networkx degrees)) == 1"),
    "chi_tree": ("m == n-1 (bit-mask)", "networkx.is_tree"),
    "deg_avg": ("Fraction(2m, n) from pop-counts", "Fraction(sum of networkx degrees, n)"),
    "ecc_avg": ("own bit-mask BFS", "networkx.eccentricity"),
    "dist_avg": ("own bit-mask BFS", "networkx.all_pairs_shortest_path_length"),
    "CW": ("Fraction sum over pop-count degrees", "Fraction sum over networkx degrees"),
    "lam_avg": ("exhaustive independent sets inside each neighbourhood",
                "branch and bound inside each neighbourhood"),
    "disp_avg": ("bit-mask neighbourhood degree sets", "networkx neighbour iteration"),
}


# --------------------------------------------------------------------------
# subset tables (shared by every exhaustive routine; built once per order)
# --------------------------------------------------------------------------
_MASKS: Dict[int, List[List[int]]] = {}


def masks_by_size(n: int) -> List[List[int]]:
    tab = _MASKS.get(n)
    if tab is None:
        tab = [[] for _ in range(n + 1)]
        for S in range(1 << n):
            tab[_pc(S)].append(S)
        _MASKS[n] = tab
    return tab


# ==========================================================================
# backend A -- pure bit-mask, exhaustive, no networkx
# ==========================================================================
def _bfs_reach(adj: Sequence[int], S: int, start: int, n: int) -> int:
    seen = 1 << start
    frontier = 1 << start
    while frontier:
        nxt = 0
        f = frontier
        while f:
            v = (f & -f).bit_length() - 1
            f &= f - 1
            nxt |= adj[v]
        nxt &= S & ~seen
        if not nxt:
            break
        seen |= nxt
        frontier = nxt
    return seen


def _connected_A(adj: Sequence[int], S: int, n: int) -> bool:
    if S == 0:
        return True
    start = (S & -S).bit_length() - 1
    return _bfs_reach(adj, S, start, n) == S


def _scan_A(adj: Sequence[int], S: int, n: int) -> Tuple[int, int, bool, int]:
    """(#edges, #components, bipartite?, max internal degree) of G[S]."""
    deg2 = 0
    ncomp = 0
    bip = True
    maxdeg = 0
    rest = S
    colour = {}
    while rest:
        v = (rest & -rest).bit_length() - 1
        ncomp += 1
        colour[v] = 0
        stack = [v]
        seen = 1 << v
        while stack:
            x = stack.pop()
            nb = adj[x] & S
            d = _pc(nb)
            deg2 += d
            if d > maxdeg:
                maxdeg = d
            cx = colour[x]
            while nb:
                y = (nb & -nb).bit_length() - 1
                nb &= nb - 1
                if not (seen >> y & 1):
                    seen |= 1 << y
                    colour[y] = 1 - cx
                    stack.append(y)
                elif colour[y] == cx:
                    bip = False
        rest &= ~seen
    return deg2 // 2, ncomp, bip, maxdeg


def _induced_A(adj: Sequence[int], n: int) -> Dict[str, int]:
    """alpha, omega, f, b, tree, path by exhaustive descending-size scan."""
    tab = masks_by_size(n)
    alpha = omega = 0
    f = b = tree = path = 0
    for k in range(n, 0, -1):
        need_ind = alpha == 0
        need_cl = omega == 0
        need_scan = (f == 0) or (b == 0) or (tree == 0) or (path == 0)
        if not (need_ind or need_cl or need_scan):
            break
        for S in tab[k]:
            if need_ind:
                t = S
                ok = True
                while t:
                    v = (t & -t).bit_length() - 1
                    t &= t - 1
                    if adj[v] & S:
                        ok = False
                        break
                if ok:
                    alpha = k
                    need_ind = False
            if need_cl:
                t = S
                ok = True
                while t:
                    v = (t & -t).bit_length() - 1
                    t &= t - 1
                    if (adj[v] & S) != (S & ~(1 << v)):
                        ok = False
                        break
                if ok:
                    omega = k
                    need_cl = False
            if need_scan:
                e, nc, bp, md = _scan_A(adj, S, n)
                if b == 0 and bp:
                    b = k
                if f == 0 and e == k - nc:
                    f = k
                if tree == 0 and nc == 1 and e == k - 1:
                    tree = k
                if path == 0 and nc == 1 and e == k - 1 and md <= 2:
                    path = k
                need_scan = (f == 0) or (b == 0) or (tree == 0) or (path == 0)
    return {"alpha": alpha, "omega": omega, "f": f, "b": b, "tree": tree, "path": path}


def _domination_A(adj: Sequence[int], n: int) -> Dict[str, int]:
    """gamma, gamma_t, gamma_2, gamma_i by exhaustive ascending-size scan."""
    tab = masks_by_size(n)
    full = (1 << n) - 1
    closed = [adj[v] | (1 << v) for v in range(n)]
    g = gt = g2 = gi = 0
    for k in range(1, n + 1):
        if g and gt and g2 and gi:
            break
        for S in tab[k]:
            cov = 0
            opencov = 0
            t = S
            indep = True
            while t:
                v = (t & -t).bit_length() - 1
                t &= t - 1
                cov |= closed[v]
                opencov |= adj[v]
                if adj[v] & S:
                    indep = False
            dom = cov == full
            if not g and dom:
                g = k
            if not gi and dom and indep:
                gi = k
            if not gt and opencov == full:
                gt = k
            if not g2:
                ok = True
                for v in range(n):
                    if S >> v & 1:
                        continue
                    if _pc(adj[v] & S) < 2:
                        ok = False
                        break
                if ok:
                    g2 = k
            if g and gt and g2 and gi:
                break
    return {"gamma": g, "gamma_t": gt, "gamma_2": g2, "gamma_i": gi}


def _max_independent_exhaustive(adj: Sequence[int], S: int, n: int) -> int:
    """alpha(G[S]) by exhaustive recursion (S is a neighbourhood, so small)."""
    best = 0

    def rec(cand: int, cur: int):
        nonlocal best
        if cur + _pc(cand) <= best:
            return
        if not cand:
            if cur > best:
                best = cur
            return
        v = (cand & -cand).bit_length() - 1
        rec(cand & ~(adj[v] | (1 << v)), cur + 1)
        rec(cand & ~(1 << v), cur)
    rec(S, 0)
    return best


def _chromatic_dsatur(adj: Sequence[int], n: int) -> int:
    order = sorted(range(n), key=lambda v: -_pc(adj[v]))
    best = [n]
    colour = [-1] * n

    def rec(i: int, used: int):
        if used >= best[0]:
            return
        if i == n:
            best[0] = used
            return
        v = order[i]
        forbidden = 0
        for u in range(n):
            if adj[v] >> u & 1 and colour[u] >= 0:
                forbidden |= 1 << colour[u]
        for c in range(used + 1):
            if c < used and (forbidden >> c & 1):
                continue
            colour[v] = c
            rec(i + 1, max(used, c + 1))
            colour[v] = -1
    rec(0, 0)
    return best[0]


def _matching_dp(adj: Sequence[int], n: int) -> int:
    dp = [0] * (1 << n)
    for S in range(1, 1 << n):
        v = (S & -S).bit_length() - 1
        rest = S ^ (1 << v)
        best = dp[rest]
        nb = adj[v] & rest
        while nb:
            u = (nb & -nb).bit_length() - 1
            nb &= nb - 1
            c = 1 + dp[rest ^ (1 << u)]
            if c > best:
                best = c
        dp[S] = best
    return dp[(1 << n) - 1]


def _kappa_A(adj: Sequence[int], n: int) -> int:
    tab = masks_by_size(n)
    full = (1 << n) - 1
    for k in range(0, n - 1):
        for S in tab[k]:
            rem = full & ~S
            if _pc(rem) <= 1:
                continue
            if not _connected_A(adj, rem, n):
                return k
    return n - 1


def _bareiss_leading_minors_positive(M: List[List[int]], n: int) -> bool:
    """True iff every leading principal minor of the symmetric integer M is > 0
    (Sylvester's criterion: M positive definite).  Bareiss keeps every
    intermediate value an exact integer and leaves the k-th leading principal
    minor in position (k, k)."""
    A = [row[:] for row in M]
    prev = 1
    for k in range(n):
        if A[k][k] <= 0:
            return False
        if k == n - 1:
            break
        akk = A[k][k]
        for i in range(k + 1, n):
            aik = A[i][k]
            Ai = A[i]
            Ak = A[k]
            for j in range(k + 1, n):
                Ai[j] = (Ai[j] * akk - aik * Ak[j]) // prev
            Ai[k] = 0
        prev = akk
    return True


def _det_int(M: List[List[int]], n: int) -> int:
    A = [row[:] for row in M]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            piv = None
            for i in range(k + 1, n):
                if A[i][k] != 0:
                    piv = i
                    break
            if piv is None:
                return 0
            A[k], A[piv] = A[piv], A[k]
            sign = -sign
        akk = A[k][k]
        for i in range(k + 1, n):
            aik = A[i][k]
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * akk - aik * A[k][j]) // prev
            A[i][k] = 0
        prev = akk
    return sign * A[n - 1][n - 1]


def _is_psd(M: List[List[int]], n: int) -> bool:
    """Symmetric Gaussian elimination over Fraction: M (symmetric) is positive
    semidefinite iff every pivot is > 0, or is 0 with an identically zero row."""
    A = [[Fraction(x) for x in row] for row in M]
    for k in range(n):
        if A[k][k] < 0:
            return False
        if A[k][k] == 0:
            if any(A[k][j] != 0 for j in range(k, n)):
                return False
            continue
        akk = A[k][k]
        for i in range(k + 1, n):
            if A[i][k]:
                fac = A[i][k] / akk
                for j in range(k, n):
                    A[i][j] -= fac * A[k][j]
    return True


def _spectral_A(adj: Sequence[int], n: int, degs: Sequence[int], m: int) -> Tuple[int, int]:
    """Exact (floor, ceil) of the adjacency spectral radius.

    `lambda_1 < k`  iff  `kI - A` is positive definite (Sylvester leading minors).
    `lambda_1 == k` iff  `kI - A` is positive *semi*definite and singular.
    The second clause is what v1 got wrong: it tested `det(kI - A) == 0` alone,
    which fires whenever *any* eigenvalue equals k.
    """
    A = [[1 if adj[i] >> j & 1 else 0 for j in range(n)] for i in range(n)]

    def shifted(k: int):
        return [[(k if i == j else 0) - A[i][j] for j in range(n)] for i in range(n)]

    # lambda_1 >= max(average degree, sqrt(Delta)); start the walk there.
    k = max(1, (2 * m) // n)
    while not _bareiss_leading_minors_positive(shifted(k), n):
        k += 1
        if k > n + 1:
            raise AssertionError("spectral bracket did not terminate")
    while k - 1 >= 1 and _bareiss_leading_minors_positive(shifted(k - 1), n):
        k -= 1
    fl = k - 1
    M = shifted(fl)
    if _det_int(M, n) != 0:
        return fl, fl + 1
    return (fl, fl) if _is_psd(M, n) else (fl, fl + 1)


def compute_A(adj: Sequence[int], n: int) -> Dict[str, object]:
    """Backend A: bit-mask arithmetic + exhaustive subset enumeration."""
    out: Dict[str, object] = {}
    degs = [_pc(a) for a in adj]
    sdeg = sorted(degs)
    m = sum(sdeg) // 2
    out["n"] = n
    out["m"] = m
    out["Delta"] = sdeg[-1]
    out["delta"] = sdeg[0]
    out["sigma2"] = sdeg[1] if n >= 2 else sdeg[0]
    out["Sigma2"] = sdeg[-2] if n >= 2 else sdeg[-1]
    out["dd"] = len(set(sdeg))
    out["f1"] = sum(1 for d in sdeg if d == 1)
    out["deg_avg"] = Fraction(2 * m, n)
    out["CW"] = sum((Fraction(1, 1 + d) for d in sdeg), Fraction(0))

    s = sorted(sdeg, reverse=True)
    while s and s[0] > 0:
        d = s.pop(0)
        for i in range(d):
            s[i] -= 1
        s.sort(reverse=True)
    out["res"] = len(s)

    tot, kk = 0, 0
    for d in sdeg:
        if tot + d <= m:
            tot += d
            kk += 1
        else:
            break
    out["annih"] = kk

    work = list(adj)
    alive = (1 << n) - 1
    best = 0
    for _ in range(n):
        cur = min((_pc(work[v] & alive), v) for v in range(n) if alive >> v & 1)
        if cur[0] > best:
            best = cur[0]
        alive &= ~(1 << cur[1])
    out["SW"] = best

    ecc, tdist, deven = [], [], []
    wiener = 0
    for src in range(n):
        seen = 1 << src
        frontier = 1 << src
        d = 0
        tot_d = 0
        even_cnt = 1
        while frontier:
            nxt = 0
            fr = frontier
            while fr:
                v = (fr & -fr).bit_length() - 1
                fr &= fr - 1
                nxt |= adj[v]
            nxt &= ~seen
            if not nxt:
                break
            d += 1
            c = _pc(nxt)
            tot_d += d * c
            if d % 2 == 0:
                even_cnt += c
            seen |= nxt
            frontier = nxt
        ecc.append(d)
        tdist.append(tot_d)
        deven.append(even_cnt)
        wiener += tot_d
    out["diam"] = max(ecc)
    out["rad"] = min(ecc)
    out["ecc_avg"] = Fraction(sum(ecc), n)
    out["Tdist_min"] = min(tdist)
    out["Tdist_max"] = max(tdist)
    out["dist_even_min"] = min(deven)
    out["dist_even_max"] = max(deven)
    out["dist_avg"] = Fraction(wiener, n * (n - 1)) if n >= 2 else Fraction(0)

    g = n + 1
    if m >= n:
        for src in range(n):
            dist = {src: 0}
            par = {src: -1}
            order = [src]
            qi = 0
            while qi < len(order):
                v = order[qi]
                qi += 1
                a = adj[v]
                while a:
                    u = (a & -a).bit_length() - 1
                    a &= a - 1
                    if u not in dist:
                        dist[u] = dist[v] + 1
                        par[u] = v
                        order.append(u)
                    elif u != par[v]:
                        c = dist[v] + dist[u] + 1
                        if c < g:
                            g = c
    out["girth"] = g

    out["kappa"] = _kappa_A(adj, n)
    full = (1 << n) - 1
    out["cutv"] = sum(1 for v in range(n)
                      if not _connected_A(adj, full & ~(1 << v), n))
    tri = 0
    for u in range(n):
        a = adj[u] >> (u + 1) << (u + 1)
        while a:
            v = (a & -a).bit_length() - 1
            a &= a - 1
            tri += _pc(adj[u] & adj[v])
    out["tri"] = tri // 3

    disp = []
    for v in range(n):
        ds = set()
        a = adj[v]
        while a:
            u = (a & -a).bit_length() - 1
            a &= a - 1
            ds.add(degs[u])
        disp.append(len(ds))
    out["disp_max"] = max(disp)
    out["disp_min"] = min(disp)
    out["disp_avg"] = Fraction(sum(disp), n)

    out["mu"] = _matching_dp(adj, n)

    out["chi_bip"] = 1 if _scan_A(adj, full, n)[2] else 0
    out["chi_K3free"] = 1 if out["tri"] == 0 else 0
    c4 = 0
    for u in range(n):
        for v in range(u + 1, n):
            if _pc(adj[u] & adj[v]) >= 2:
                c4 = 1
                break
        if c4:
            break
    out["chi_C4free"] = 0 if c4 else 1
    claw = 0
    for v in range(n):
        nb = [u for u in range(n) if adj[v] >> u & 1]
        if len(nb) >= 3:
            for a3, b3, c3 in itertools.combinations(nb, 3):
                if not (adj[a3] >> b3 & 1) and not (adj[a3] >> c3 & 1) \
                        and not (adj[b3] >> c3 & 1):
                    claw = 1
                    break
        if claw:
            break
    out["chi_claw"] = 0 if claw else 1
    out["chi_reg"] = 1 if out["Delta"] == out["delta"] else 0
    out["chi_tree"] = 1 if m == n - 1 else 0

    fl, ce = _spectral_A(adj, n, degs, m)
    out["spec_floor"] = fl
    out["spec_ceil"] = ce

    out.update(_induced_A(adj, n))
    out.update(_domination_A(adj, n))
    out["chi"] = _chromatic_dsatur(adj, n)
    lam = [_max_independent_exhaustive(adj, adj[v], n) for v in range(n)]
    out["lam_max"] = max(lam)
    out["lam_min"] = min(lam)
    out["lam_avg"] = Fraction(sum(lam), n)

    missing = [k for k in VOCAB if k not in out]
    if missing:
        raise AssertionError("backend A missing: %s" % missing)
    return {k: out[k] for k in VOCAB}


# ==========================================================================
# scalable solvers -- branch and bound, no 2^n enumeration.
# These are what an arm would run on a 20..40 vertex candidate counterexample,
# and they are backend B's answer for every NP-hard invariant, so the R4
# cross-check over D2 validates exactly the code the arms depend on.
# ==========================================================================
def max_independent_bb(adj: Sequence[int], S: int, n: int) -> int:
    best = [0]

    def bound(cand: int) -> int:
        rest = cand
        classes = 0
        while rest:
            v = (rest & -rest).bit_length() - 1
            clique = 1 << v
            grow = adj[v] & rest
            while grow:
                u = (grow & -grow).bit_length() - 1
                clique |= 1 << u
                grow &= adj[u]
            rest &= ~clique
            classes += 1
        return classes

    def rec(cand: int, cur: int):
        if not cand:
            if cur > best[0]:
                best[0] = cur
            return
        if cur + bound(cand) <= best[0]:
            return
        v = max((_pc(adj[u] & cand), u) for u in range(n) if cand >> u & 1)[1]
        rec(cand & ~(adj[v] | (1 << v)), cur + 1)
        rec(cand & ~(1 << v), cur)
    rec(S, 0)
    return best[0]


def min_dominating_bb(adj: Sequence[int], n: int, kind: str) -> int:
    """Exact minimum dominating set (gamma / gamma_t / gamma_2 / gamma_i).

    Greedy incumbent, disjoint-pool packing lower bound, branching on the most
    constrained unsatisfied vertex as "take u_i, forbid u_1..u_{i-1}".
    Carried over from v1 unchanged: it survived v1's cross-check on 1,500
    graphs, and is re-checked here on all 273,192.
    """
    closed = [adj[v] | (1 << v) for v in range(n)]
    if kind == "gamma_t" and any(a == 0 for a in adj):
        raise ValueError("total domination undefined with isolated vertices")
    indep = kind == "gamma_i"
    need2 = kind == "gamma_2"
    pool0 = list(adj) if kind == "gamma_t" else closed

    def shortfall(v: int, picked: int) -> int:
        if need2:
            if picked >> v & 1:
                return 0
            return max(0, 2 - _pc(adj[v] & picked))
        return 0 if (pool0[v] & picked) else 1

    picked = 0
    while True:
        short = [v for v in range(n) if shortfall(v, picked)]
        if not short:
            break
        bestu, bestgain = -1, -1
        for u in range(n):
            if picked >> u & 1:
                continue
            if indep and (adj[u] & picked):
                continue
            gain = sum(min(shortfall(v, picked), 1) for v in short if pool0[v] >> u & 1)
            if gain > bestgain:
                bestu, bestgain = u, gain
        if bestu < 0 or bestgain <= 0:
            picked = (1 << n) - 1
            break
        picked |= 1 << bestu
    best = [_pc(picked)]

    def lower_bound(unsat) -> int:
        used = 0
        lb = 0
        for v, need, pl in unsat:
            if pl & used:
                continue
            used |= pl
            lb += 1 if (pl >> v & 1) else need
        return lb

    def rec(picked: int, banned: int, k: int):
        if k >= best[0]:
            return
        unsat = []
        for v in range(n):
            need = shortfall(v, picked)
            if not need:
                continue
            pl = (closed[v] if need2 else pool0[v]) & ~(picked | banned)
            if indep:
                for u in range(n):
                    if (pl >> u & 1) and (adj[u] & picked):
                        pl &= ~(1 << u)
            if not (pl >> v & 1) and _pc(adj[v] & pl) < need:
                return
            unsat.append((v, need, pl))
        if not unsat:
            best[0] = k
            return
        unsat.sort(key=lambda z: (_pc(z[2]), -z[1], z[0]))
        if k + lower_bound(unsat) >= best[0]:
            return
        _, _, pl = unsat[0]
        ban = banned
        for u in range(n):
            if not (pl >> u & 1):
                continue
            rec(picked | (1 << u), ban, k + 1)
            ban |= 1 << u
    rec(0, 0, 0)
    return best[0]


def _short_cycle(adj: Sequence[int], S: int, n: int, odd_only: bool = False):
    """A short (odd) cycle of G[S] as a vertex set, or None."""
    best = None
    lim = 3 if not odd_only else 3
    rest = S
    while rest:
        src = (rest & -rest).bit_length() - 1
        rest &= rest - 1
        dist = {src: 0}
        par = {src: -1}
        order = [src]
        qi = 0
        while qi < len(order):
            v = order[qi]
            qi += 1
            nb = adj[v] & S
            while nb:
                u = (nb & -nb).bit_length() - 1
                nb &= nb - 1
                if u not in dist:
                    dist[u] = dist[v] + 1
                    par[u] = v
                    order.append(u)
                elif u != par[v]:
                    cyc = set()
                    a, b = v, u
                    while a != b:
                        if dist[a] >= dist[b]:
                            cyc.add(a)
                            a = par[a]
                        else:
                            cyc.add(b)
                            b = par[b]
                    cyc.add(a)
                    if len(cyc) < 3:
                        continue
                    if odd_only and len(cyc) % 2 == 0:
                        continue
                    if best is None or len(cyc) < len(best):
                        best = cyc
                        if len(best) == lim:
                            return best
    return best


def _pack_cycles(adj: Sequence[int], S: int, n: int, odd_only: bool = False) -> int:
    rest = S
    k = 0
    while True:
        c = _short_cycle(adj, rest, n, odd_only)
        if c is None:
            return k
        k += 1
        for v in c:
            rest &= ~(1 << v)


def _greedy_induced_acyclic(adj: Sequence[int], n: int, odd_only: bool = False) -> int:
    S = (1 << n) - 1
    while True:
        c = _short_cycle(adj, S, n, odd_only)
        if c is None:
            return _pc(S)
        v = max(c, key=lambda u: (_pc(adj[u] & S), -u))
        S &= ~(1 << v)


MEMO_CAP = 400000


def max_induced_acyclic_bb(adj: Sequence[int], n: int, odd_only: bool) -> int:
    """f (odd_only=False) / b (odd_only=True): branch on a short (odd) cycle,
    upper-bounded by a greedy disjoint (odd) cycle packing, seeded greedily."""
    best = [_greedy_induced_acyclic(adj, n, odd_only)]
    seen = set()

    def rec(S: int):
        sz = _pc(S)
        if sz <= best[0] or S in seen:
            return
        if len(seen) < MEMO_CAP:
            seen.add(S)
        c = _short_cycle(adj, S, n, odd_only)
        if c is None:
            best[0] = sz
            return
        if sz - _pack_cycles(adj, S, n, odd_only) <= best[0]:
            return
        for v in sorted(c):
            rec(S & ~(1 << v))
    rec((1 << n) - 1)
    return best[0]


def max_induced_forest_bb(adj: Sequence[int], n: int) -> int:
    return max_induced_acyclic_bb(adj, n, False)


def max_induced_bipartite_bb(adj: Sequence[int], n: int) -> int:
    return max_induced_acyclic_bb(adj, n, True)


def max_induced_tree_bb(adj: Sequence[int], n: int) -> int:
    """Order of a largest induced tree, by connected expansion.

    State: `T` a connected induced acyclic set, `ext` the vertices that may still
    join it (each has exactly one neighbour in `T`, so adding it keeps `T`
    induced-acyclic and connected), `forb` the vertices excluded on this branch.
    Branch on the first admissible vertex: take it, or forbid it.  Upper bound:
    |T| plus the vertices still reachable from T in G - forb.
    """
    full = (1 << n) - 1
    best = [1 if n else 0]

    def admissible(T: int, forb: int) -> int:
        """Vertices outside T, not forbidden, with exactly one neighbour in T."""
        out = 0
        cand = full & ~T & ~forb
        while cand:
            v = (cand & -cand).bit_length() - 1
            cand &= cand - 1
            if _pc(adj[v] & T) == 1:
                out |= 1 << v
        return out

    def reach_bound(T: int, forb: int) -> int:
        """|T| + |vertices reachable from T in G - forb - (blocked)|."""
        allowed = full & ~forb
        seen = T
        frontier = T
        while frontier:
            nxt = 0
            fr = frontier
            while fr:
                v = (fr & -fr).bit_length() - 1
                fr &= fr - 1
                nxt |= adj[v]
            nxt &= allowed & ~seen
            if not nxt:
                break
            seen |= nxt
            frontier = nxt
        return _pc(seen)

    def rec(T: int, forb: int):
        sz = _pc(T)
        if sz > best[0]:
            best[0] = sz
        ext = admissible(T, forb)
        if not ext:
            return
        if reach_bound(T, forb) <= best[0]:
            return
        v = (ext & -ext).bit_length() - 1
        rec(T | (1 << v), forb)
        rec(T, forb | (1 << v))

    for s in range(n):
        # vertices < s are forbidden: every induced tree is grown from its
        # lowest-indexed vertex exactly once.
        forb0 = (1 << s) - 1
        if n - s <= best[0]:
            break
        rec(1 << s, forb0)
    return best[0]


def max_induced_path_bb(adj: Sequence[int], n: int) -> int:
    """Order of a largest induced path, by growth from one endpoint.

    `P` is an induced path with a fixed start endpoint `s` and a head `h`.  A
    vertex may be appended iff it is adjacent to `h` and to nothing else in `P`.
    Growing from every possible start endpoint reaches every induced path (twice
    -- once from each of its two endpoints, which costs a factor 2 and cannot
    miss anything; restricting to the lower-indexed endpoint would be wrong,
    because the lowest-indexed vertex of an induced path need not be an
    endpoint).
    """
    full = (1 << n) - 1
    best = [1 if n else 0]

    def rec(P: int, h: int, forb: int, blocked: int):
        sz = _pc(P)
        if sz > best[0]:
            best[0] = sz
        cand = adj[h] & ~P & ~forb & ~blocked
        # a candidate must have no other neighbour in P
        good = 0
        c = cand
        while c:
            v = (c & -c).bit_length() - 1
            c &= c - 1
            if _pc(adj[v] & P) == 1:
                good |= 1 << v
        if not good:
            return
        # bound: everything still reachable from the head avoiding blocked/forb
        allowed = full & ~forb & ~blocked & ~P
        seen = 0
        frontier = good
        seen |= good
        while frontier:
            nxt = 0
            fr = frontier
            while fr:
                v = (fr & -fr).bit_length() - 1
                fr &= fr - 1
                nxt |= adj[v]
            nxt &= allowed & ~seen
            if not nxt:
                break
            seen |= nxt
            frontier = nxt
        if sz + _pc(seen) <= best[0]:
            return
        g = good
        skip = 0
        while g:
            v = (g & -g).bit_length() - 1
            g &= g - 1
            # appending v blocks every other neighbour of h and of v
            rec(P | (1 << v), v, forb | skip, blocked | (adj[h] & ~(1 << v)))
            skip |= 1 << v

    for s in range(n):
        rec(1 << s, s, 0, 0)
    return best[0]


# ==========================================================================
# backend B -- networkx + independent algorithms
# ==========================================================================
def _charpoly_int(adj: Sequence[int], n: int) -> List[int]:
    """Coefficients of det(xI - A), highest degree first, exact integers.

    Power sums p_k = trace(A^k) by integer matrix multiplication, then Newton's
    identities.  Shares nothing with backend A's determinant machinery.
    """
    A = [[1 if adj[i] >> j & 1 else 0 for j in range(n)] for i in range(n)]
    P = [row[:] for row in A]
    p = [0] * (n + 1)
    p[0] = n
    for k in range(1, n + 1):
        p[k] = sum(P[i][i] for i in range(n))
        if k < n:
            Q = [[0] * n for _ in range(n)]
            for i in range(n):
                Pi = P[i]
                Qi = Q[i]
                for t in range(n):
                    v = Pi[t]
                    if v:
                        At = A[t]
                        for j in range(n):
                            if At[j]:
                                Qi[j] += v
            P = Q
    # e_0 = 1;  k*e_k = sum_{i=1..k} (-1)^{i-1} e_{k-i} p_i
    e = [Fraction(0)] * (n + 1)
    e[0] = Fraction(1)
    for k in range(1, n + 1):
        acc = Fraction(0)
        for i in range(1, k + 1):
            acc += (-1) ** (i - 1) * e[k - i] * p[i]
        e[k] = acc / k
    coeffs = []
    for k in range(0, n + 1):
        c = (-1) ** k * e[k]
        assert c.denominator == 1, "characteristic polynomial is not integral"
        coeffs.append(int(c))
    return coeffs                          # x^n + c1 x^{n-1} + ... + cn


def _poly_shift_all_derivs_positive(coeffs: List[int], t: int) -> Tuple[bool, bool]:
    """For a monic real-rooted polynomial `chi`, return (chi(t) == 0, every
    derivative chi^{(j)}(t) for j >= 1 is > 0).

    Taylor at t: chi(t+h) = sum_j chi^{(j)}(t) h^j / j!.  All those coefficients
    positive for j >= 1 means chi has no root above t; adding chi(t) > 0 means
    t is above the largest root, and chi(t) == 0 means t *is* the largest root.
    The shifted coefficients are computed by synthetic division, in integers.
    """
    a = coeffs[:]                          # highest degree first
    n = len(a) - 1
    shifted = []                           # chi^{(j)}(t)/j!, j = 0.. n
    for _ in range(n + 1):
        rem = 0
        out = []
        for c in a:
            rem = rem * t + c
            out.append(rem)
        shifted.append(out[-1])
        a = out[:-1]
        if not a:
            break
    val0 = shifted[0]
    rest_pos = all(x > 0 for x in shifted[1:])
    return val0 == 0, rest_pos


def _spectral_B(adj: Sequence[int], n: int) -> Tuple[int, int]:
    """(floor, ceil) of lambda_1 from the exact integer characteristic polynomial.

    `lambda_1 <= Delta <= n-1 < n`, so scanning t down from n the first t that is
    not strictly above lambda_1 settles the bracket:  t == lambda_1 gives
    (t, t); t < lambda_1 gives (t, t+1).
    """
    coeffs = _charpoly_int(adj, n)
    fl = None
    for t in range(n, -1, -1):
        zero, pos = _poly_shift_all_derivs_positive(coeffs, t)
        above = pos and _poly_value(coeffs, t) > 0        # t > lambda_1
        equal = pos and zero                              # t == lambda_1
        if equal:
            return t, t
        if not above:
            fl = t
            break
    assert fl is not None, "spectral bracket (B) failed"
    return fl, fl + 1


def _poly_value(coeffs: List[int], t: int) -> int:
    v = 0
    for c in coeffs:
        v = v * t + c
    return v


def compute_B(G, n: int) -> Dict[str, object]:
    """Backend B: networkx wherever possible, plus independent exact algorithms.

    `G` is a networkx graph whose nodes are exactly 0..n-1.
    """
    import networkx as nx

    out: Dict[str, object] = {}
    degd = dict(G.degree())
    degs = [degd[v] for v in range(n)]
    sdeg = sorted(degs)
    m = G.number_of_edges()
    out["n"] = G.number_of_nodes()
    out["m"] = m
    out["Delta"] = max(sdeg)
    out["delta"] = min(sdeg)
    out["sigma2"] = sdeg[1] if n >= 2 else sdeg[0]
    out["Sigma2"] = sdeg[-2] if n >= 2 else sdeg[-1]
    out["dd"] = len(set(sdeg))
    out["f1"] = sum(1 for d in sdeg if d == 1)
    out["deg_avg"] = Fraction(sum(sdeg), n)
    out["CW"] = sum((Fraction(1, 1 + d) for d in degs), Fraction(0))

    # residue: Havel-Hakimi in counting-array form (no list is ever re-sorted).
    # The decremented vertices are parked in `moved` and only folded back into
    # `cnt` once the whole step is done -- otherwise a vertex demoted from degree
    # d to d-1 is met again at level d-1 and demoted twice in the same step.
    cnt = [0] * (n + 2)
    for d in sdeg:
        cnt[d] += 1
    while True:
        top = max((d for d in range(n, 0, -1) if cnt[d] > 0), default=0)
        if top == 0:
            break
        cnt[top] -= 1
        need = top
        moved = [0] * (n + 2)
        d = top
        while need > 0 and d >= 1:
            take = min(cnt[d], need)
            if take:
                cnt[d] -= take
                moved[d - 1] += take
                need -= take
            d -= 1
        assert need == 0, "degree sequence is not graphical"
        for d in range(n + 1):
            if moved[d]:
                cnt[d] += moved[d]
    out["res"] = cnt[0]

    acc = list(itertools.accumulate(sdeg))
    out["annih"] = sum(1 for x in acc if x <= m)

    out["SW"] = max(nx.core_number(G).values())

    ecc = nx.eccentricity(G)
    out["diam"] = max(ecc.values())
    out["rad"] = min(ecc.values())
    out["ecc_avg"] = Fraction(sum(ecc.values()), n)

    sp = dict(nx.all_pairs_shortest_path_length(G))
    tdist, deven = [], []
    wiener = 0
    for v in range(n):
        row = sp[v]
        s = sum(row.values())
        tdist.append(s)
        wiener += s
        deven.append(sum(1 for u in row if row[u] % 2 == 0))
    out["Tdist_min"] = min(tdist)
    out["Tdist_max"] = max(tdist)
    out["dist_even_min"] = min(deven)
    out["dist_even_max"] = max(deven)
    out["dist_avg"] = Fraction(wiener, n * (n - 1)) if n >= 2 else Fraction(0)

    # girth: for every edge uv, the shortest u-v path in G - uv closes a cycle
    g = n + 1
    for u, v in G.edges():
        H = G.copy()
        H.remove_edge(u, v)
        try:
            d = nx.shortest_path_length(H, u, v)
        except nx.NetworkXNoPath:
            continue
        if d + 1 < g:
            g = d + 1
    out["girth"] = g

    out["kappa"] = nx.node_connectivity(G)
    out["cutv"] = len(list(nx.articulation_points(G)))
    out["tri"] = sum(nx.triangles(G).values()) // 3

    disp = []
    for v in range(n):
        disp.append(len({degd[u] for u in G[v]}))
    out["disp_max"] = max(disp)
    out["disp_min"] = min(disp)
    out["disp_avg"] = Fraction(sum(disp), n)

    out["mu"] = len(nx.max_weight_matching(G, maxcardinality=True))

    out["chi_bip"] = 1 if nx.is_bipartite(G) else 0
    out["chi_K3free"] = 1 if out["tri"] == 0 else 0
    c4 = 0
    for quad in itertools.combinations(range(n), 4):
        H = G.subgraph(quad)
        if H.number_of_edges() >= 4 and min(d for _, d in H.degree()) >= 2:
            c4 = 1
            break
    out["chi_C4free"] = 0 if c4 else 1
    claw = 0
    for quad in itertools.combinations(range(n), 4):
        H = G.subgraph(quad)
        ds = sorted(d for _, d in H.degree())
        if ds == [1, 1, 1, 3]:
            claw = 1
            break
    out["chi_claw"] = 0 if claw else 1
    out["chi_reg"] = 1 if len(set(sdeg)) == 1 else 0
    out["chi_tree"] = 1 if nx.is_tree(G) else 0

    adj = [0] * n
    for u, v in G.edges():
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    full = (1 << n) - 1
    comp = [full & ~(adj[v] | (1 << v)) for v in range(n)]

    fl, ce = _spectral_B(adj, n)
    out["spec_floor"] = fl
    out["spec_ceil"] = ce

    out["alpha"] = max_independent_bb(adj, full, n)
    out["omega"] = max_independent_bb(comp, full, n)
    out["f"] = max_induced_forest_bb(adj, n)
    out["b"] = max_induced_bipartite_bb(adj, n)
    out["tree"] = max_induced_tree_bb(adj, n)
    out["path"] = max_induced_path_bb(adj, n)
    out["gamma"] = min_dominating_bb(adj, n, "gamma")
    out["gamma_t"] = min_dominating_bb(adj, n, "gamma_t")
    out["gamma_2"] = min_dominating_bb(adj, n, "gamma_2")
    out["gamma_i"] = min_dominating_bb(adj, n, "gamma_i")
    lam = [max_independent_bb(adj, adj[v], n) for v in range(n)]
    out["lam_max"] = max(lam)
    out["lam_min"] = min(lam)
    out["lam_avg"] = Fraction(sum(lam), n)
    out["chi"] = _chromatic_cover_dp(adj, n)

    missing = [k for k in VOCAB if k not in out]
    if missing:
        raise AssertionError("backend B missing: %s" % missing)
    return {k: out[k] for k in VOCAB}


def _chromatic_cover_dp(adj: Sequence[int], n: int) -> int:
    """Chromatic number as the minimum number of independent sets covering V,
    by a DP over all 2^n subsets.  Shares nothing with DSATUR."""
    full = (1 << n) - 1
    indep = bytearray(1 << n)
    indep[0] = 1
    for S in range(1, 1 << n):
        v = (S & -S).bit_length() - 1
        rest = S ^ (1 << v)
        indep[S] = 1 if (indep[rest] and not (adj[v] & rest)) else 0
    INF = n + 1
    dp = [INF] * (1 << n)
    dp[0] = 0
    for S in range(1, 1 << n):
        low = S & -S
        sub = S
        bestv = INF
        while sub:
            if (sub & low) and indep[sub]:
                c = dp[S ^ sub]
                if c + 1 < bestv:
                    bestv = c + 1
            sub = (sub - 1) & S
        dp[S] = bestv
    return dp[full]


# --------------------------------------------------------------------------
# public entry point
# --------------------------------------------------------------------------
def compute(code_or_graph, backend: str = "A") -> Dict[str, object]:
    """`code_or_graph` is a graph6 string (backend A) or a networkx graph (B)."""
    if backend == "A":
        from graph_db2 import g6_to_adj
        adj, n = g6_to_adj(code_or_graph)
        return compute_A(adj, n)
    if backend == "B":
        import networkx as nx
        if isinstance(code_or_graph, str):
            G = nx.from_graph6_bytes(code_or_graph.encode())
            G = nx.convert_node_labels_to_integers(G, ordering="sorted")
        else:
            G = code_or_graph
        return compute_B(G, G.number_of_nodes())
    raise ValueError(backend)
