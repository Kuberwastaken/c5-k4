"""Exact graph-invariant vocabulary for the fresh-population generator.

Every value is an exact `int` or `fractions.Fraction`; no floating point is used
anywhere in a value that a conjecture can depend on.

Two independent backends compute the same vocabulary:

  * ``brute``  -- exhaustive bitmask enumeration over all `2^n` vertex subsets.
                  Exact by construction, used for the database `D` (`n <= 8`).
  * ``scal``   -- branch-and-bound / polynomial algorithms with no subset
                  enumeration.  Used to check that a statement is decidable on a
                  20--40 vertex graph inside the 60 s cap, and as the second,
                  independent code path required by the project's verification
                  discipline.

``scripts/gen/check_invariants.py`` cross-checks the two backends.

Definitions follow ``data/INVARIANT-GLOSSARY.md`` (DeLaVina's WOWII definitions
database).  Two conventions are pinned here because the sources leave them open:

  * ``girth``: number of vertices of a shortest cycle; **``n + 1`` if `G` is
    acyclic**.  Any cycle of a graph on `n` vertices has at most `n` vertices, so
    within the finite universe `n+1` behaves exactly like the usual `+inf`, while
    keeping every statement finite-checkable.
  * ``dist_even(v)``/``dist_odd(v)``: `v` itself is counted (distance 0 is even),
    matching ``scripts/profile_c5k4.py`` and the WOWII page examples.

Excluded from the vocabulary on purpose:
  * ``maxine`` -- the greedy "remove a maximum-degree vertex" process is
    tie-break dependent and therefore not an isomorphism invariant.
  * ``p(G)`` (path covering number), ``path(G)`` (longest induced path),
    ``tree(G)`` (largest induced tree), ``L_s``/``gamma_c`` (max-leaf spanning
    tree / connected domination), ``alpha'`` (critical independence) -- no exact
    solver available here decides them inside the 60 s cap at n = 30..40.

Present in the vocabulary but excluded from *emission* on measured runtime:
  * ``f`` (largest induced forest) and ``b`` (largest induced bipartite
    subgraph).  Both exceed 20 s on G(40, 0.3) and G(40, 0.5) with the solvers
    below, so a statement using them could not be decided by any arm inside the
    cap.  They are still computed on `D` and cross-checked between backends; the
    exclusion is enforced by ``generate.EXCLUDED_FOR_RUNTIME`` and the numbers
    are in ``check_target_budget.py``.
"""
from __future__ import annotations

import itertools
from fractions import Fraction
from typing import Dict, List, Sequence

import networkx as nx

POPCNT = [bin(i).count("1") for i in range(1 << 16)]


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
#       "N"  NP-hard but measured fast (see check_invariants.py) on n <= 40
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
    # connectivity / counting
    ("kappa", "P"), ("cutv", "P"), ("tri", "P"),
    ("disp_max", "P"), ("disp_min", "P"),
    ("spec_floor", "P"), ("spec_ceil", "P"),
    # independence / clique / colouring
    ("alpha", "N"), ("omega", "N"), ("chi", "N"), ("mu", "P"),
    ("lam_max", "N"), ("lam_min", "N"),
    # domination family
    ("gamma", "N"), ("gamma_t", "N"), ("gamma_2", "N"), ("gamma_i", "N"),
    # induced-order invariants
    ("f", "N"), ("b", "N"),
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

# LaTeX-free display names used in the emitted statements.
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
    "f": "f", "b": "b",
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
    "spec_floor": "floor of the adjacency spectral radius (exact, via principal minors)",
    "spec_ceil": "ceiling of the adjacency spectral radius (exact, via principal minors)",
    "alpha": "independence number",
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


# --------------------------------------------------------------------------
# shared, backend-independent, polynomial-time pieces
# --------------------------------------------------------------------------
def _base(G: nx.Graph) -> Dict[str, object]:
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    adj = [0] * n
    for u, v in G.edges():
        if u == v:
            raise ValueError("self loops not supported")
        adj[idx[u]] |= 1 << idx[v]
        adj[idx[v]] |= 1 << idx[u]
    return {"nodes": nodes, "idx": idx, "n": n, "adj": adj}


def _poly_part(G: nx.Graph, adj: Sequence[int], n: int) -> Dict[str, object]:
    """Everything that needs no subset search."""
    out: Dict[str, object] = {}
    m = G.number_of_edges()
    degs = [_pc(a) for a in adj]
    sdeg = sorted(degs)
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

    # residue + annihilation
    s = sorted(sdeg, reverse=True)
    while s and s[0] > 0:
        d = s.pop(0)
        for i in range(d):
            s[i] -= 1
        s.sort(reverse=True)
    out["res"] = len(s)
    tot, k = 0, 0
    for d in sdeg:
        if tot + d <= m:
            tot += d
            k += 1
        else:
            break
    out["annih"] = k

    # Szekeres-Wilf = degeneracy = max over subgraphs of min degree
    work = list(adj)
    alive = (1 << n) - 1
    best = 0
    for _ in range(n):
        cur = min((_pc(work[v] & alive), v) for v in range(n) if alive >> v & 1)
        best = max(best, cur[0])
        alive &= ~(1 << cur[1])
    out["SW"] = best

    # distances (BFS from every vertex, bitmask frontier)
    ecc, tdist, deven = [], [], []
    wiener = 0
    for src in range(n):
        seen = 1 << src
        frontier = 1 << src
        d = 0
        tot_d = 0
        even_cnt = 1                       # src itself, distance 0
        while frontier:
            nxt = 0
            for v in range(n):
                if frontier >> v & 1:
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

    # girth (BFS from every vertex, exact); n+1 if acyclic
    g = n + 1
    if m >= n:                             # a connected acyclic graph has m = n-1
        for src in range(n):
            dist = {src: 0}
            par = {src: -1}
            order = [src]
            qi = 0
            while qi < len(order):
                v = order[qi]
                qi += 1
                a = adj[v]
                for u in range(n):
                    if not (a >> u & 1):
                        continue
                    if u not in dist:
                        dist[u] = dist[v] + 1
                        par[u] = v
                        order.append(u)
                    elif u != par[v]:
                        g = min(g, dist[v] + dist[u] + 1)
    out["girth"] = g

    out["kappa"] = nx.node_connectivity(G)
    out["cutv"] = len(list(nx.articulation_points(G)))
    out["tri"] = sum(nx.triangles(G).values()) // 3

    disp = []
    for v in range(n):
        ds = {degs[u] for u in range(n) if adj[v] >> u & 1}
        disp.append(len(ds))
    out["disp_max"] = max(disp)
    out["disp_min"] = min(disp)
    out["disp_avg"] = Fraction(sum(disp), n)

    out["mu"] = len(nx.max_weight_matching(G, maxcardinality=True))

    # characteristic functions
    out["chi_bip"] = 1 if nx.is_bipartite(G) else 0
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
            for trio in itertools.combinations(nb, 3):
                a, b, c = trio
                if not (adj[a] >> b & 1) and not (adj[a] >> c & 1) and not (adj[b] >> c & 1):
                    claw = 1
                    break
        if claw:
            break
    out["chi_claw"] = 0 if claw else 1
    out["chi_reg"] = 1 if out["Delta"] == out["delta"] else 0
    out["chi_tree"] = 1 if m == n - 1 else 0

    lo, hi = _spectral_bracket(adj, n)
    out["spec_floor"] = lo
    out["spec_ceil"] = hi
    return out


def _det_int(M: List[List[int]]) -> int:
    """Exact integer determinant, Bareiss fraction-free elimination."""
    n = len(M)
    if n == 0:
        return 1
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
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
            A[i][k] = 0
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


def _spectral_bracket(adj: Sequence[int], n: int):
    """Exact (floor, ceil) of the adjacency spectral radius lambda_1.

    `lambda_1 < k` iff `kI - A` is positive definite iff every leading principal
    minor of `kI - A` is strictly positive (Sylvester).  All minors are integer
    determinants, so the test is exact.
    """
    A = [[1 if adj[i] >> j & 1 else 0 for j in range(n)] for i in range(n)]

    def lt(k: int) -> bool:                # lambda_1 < k ?
        M = [[(k if i == j else 0) - A[i][j] for j in range(n)] for i in range(n)]
        for s in range(1, n + 1):
            if _det_int([row[:s] for row in M[:s]]) <= 0:
                return False
        return True

    hi = 0
    while not lt(hi + 1) and hi <= n:
        hi += 1
    hi += 1                                # smallest integer k with lambda_1 < k
    # lambda_1 in [hi-1, hi)
    fl = hi - 1
    # lambda_1 == fl exactly iff det(fl*I - A) == 0 and lambda_1 >= fl
    M = [[(fl if i == j else 0) - A[i][j] for j in range(n)] for i in range(n)]
    if _det_int(M) == 0:
        return fl, fl
    return fl, fl + 1


# --------------------------------------------------------------------------
# backend "brute" -- exhaustive subset enumeration (exact, for n <= ~20)
# --------------------------------------------------------------------------
def _brute_part(adj: Sequence[int], n: int) -> Dict[str, object]:
    full = (1 << n) - 1
    closed = [adj[v] | (1 << v) for v in range(n)]
    alpha = omega = 0
    f = b = 0
    gamma = gamma_t = gamma_2 = gamma_i = n + 1

    for S in range(1, 1 << n):
        size = _pc(S)
        indep = True
        clique = True
        edges2 = 0
        maxdeg = 0
        for v in range(n):
            if not (S >> v & 1):
                continue
            d = _pc(adj[v] & S)
            edges2 += d
            if d:
                indep = False
            if d != size - 1:
                clique = False
            if d > maxdeg:
                maxdeg = d
        if indep and size > alpha:
            alpha = size
        if clique and size > omega:
            omega = size

        # domination predicates
        if size < gamma or size < gamma_t or size < gamma_2 or size < gamma_i:
            cov = 0
            for v in range(n):
                if S >> v & 1:
                    cov |= closed[v]
            dom = cov == full
            if dom and size < gamma:
                gamma = size
            if dom and indep and size < gamma_i:
                gamma_i = size
            if size < gamma_t:
                tot = all((adj[v] & S) for v in range(n))
                if tot:
                    gamma_t = size
            if size < gamma_2:
                if all((S >> v & 1) or _pc(adj[v] & S) >= 2 for v in range(n)):
                    gamma_2 = size

        # induced-order predicates (only worth testing above the current best)
        if size > f or size > b:
            ncomp, bip = _components_bipartite(adj, S, n)
            edges = edges2 // 2
            if size > f and edges == size - ncomp:
                f = size
            if size > b and bip:
                b = size

    lam = []
    for v in range(n):
        lam.append(_max_independent_in(adj, adj[v], n))
    return {
        "alpha": alpha, "omega": omega, "f": f, "b": b,
        "gamma": gamma, "gamma_t": gamma_t, "gamma_2": gamma_2, "gamma_i": gamma_i,
        "lam_max": max(lam), "lam_min": min(lam),
        "lam_avg": Fraction(sum(lam), n),
        "chi": _chromatic_brute(adj, n),
    }


def _components_bipartite(adj: Sequence[int], S: int, n: int):
    rest = S
    ncomp = 0
    bip = True
    while rest:
        v = (rest & -rest).bit_length() - 1
        ncomp += 1
        colour = {v: 0}
        stack = [v]
        seen = 1 << v
        while stack:
            x = stack.pop()
            nb = adj[x] & S
            while nb:
                y = (nb & -nb).bit_length() - 1
                nb &= nb - 1
                if not (seen >> y & 1):
                    seen |= 1 << y
                    colour[y] = 1 - colour[x]
                    stack.append(y)
                elif colour[y] == colour[x]:
                    bip = False
        rest &= ~seen
    return ncomp, bip


def _max_independent_in(adj: Sequence[int], S: int, n: int) -> int:
    """Independence number of G[S] by exhaustive search (S small: a neighbourhood)."""
    verts = [v for v in range(n) if S >> v & 1]
    best = 0

    def rec(cand: int, cur: int):
        nonlocal best
        if cur + _pc(cand) <= best:
            return
        if not cand:
            best = max(best, cur)
            return
        v = (cand & -cand).bit_length() - 1
        rec(cand & ~(adj[v] | (1 << v)), cur + 1)     # take v
        rec(cand & ~(1 << v), cur)                    # drop v
    rec(S, 0)
    return best


def _chromatic_brute(adj: Sequence[int], n: int) -> int:
    """Exact chromatic number by DSATUR branch and bound."""
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


# --------------------------------------------------------------------------
# backend "scal" -- no subset enumeration; usable at n = 20..40
# --------------------------------------------------------------------------
def _max_independent_bb(adj: Sequence[int], S: int, n: int) -> int:
    """Max independent set inside `S` by greedy-colouring-bounded branch & bound."""
    best = [0]

    def bound(cand: int) -> int:
        """Greedy clique cover of G[cand]; alpha(G[cand]) <= number of cliques."""
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
        # branch on a vertex of maximum degree inside cand
        v = max((_pc(adj[u] & cand), u) for u in range(n) if cand >> u & 1)[1]
        rec(cand & ~(adj[v] | (1 << v)), cur + 1)
        rec(cand & ~(1 << v), cur)
    rec(S, 0)
    return best[0]


def _min_dominating(adj: Sequence[int], n: int, kind: str) -> int:
    """Exact minimum dominating set of the requested `kind`, branch and bound.

    kind in {"gamma", "gamma_t", "gamma_2", "gamma_i"}.

    Three things make this fast enough to decide a 40-vertex graph:

    * a greedy feasible solution seeds the incumbent, so pruning bites at once;
    * a **disjoint-neighbourhood packing lower bound** -- collect unsatisfied
      vertices whose candidate pools are pairwise disjoint; each needs its own
      picks, so the sum of their shortfalls is a valid bound.  On sparse graphs
      (paths, trees, grids) this is nearly exact and collapses the search;
    * branching on the most constrained unsatisfied vertex as
      "take `u_i`, forbid `u_1..u_{i-1}`", which is exhaustive and visits no
      subset twice.
    """
    closed = [adj[v] | (1 << v) for v in range(n)]
    if kind == "gamma_t" and any(a == 0 for a in adj):
        raise ValueError("total domination undefined with isolated vertices")
    indep = kind == "gamma_i"
    need2 = kind == "gamma_2"
    # pool[v] = vertices whose selection helps satisfy v
    pool0 = list(adj) if kind == "gamma_t" else closed

    def shortfall(v: int, picked: int) -> int:
        if need2:
            if picked >> v & 1:
                return 0
            return max(0, 2 - _pc(adj[v] & picked))
        return 0 if (pool0[v] & picked) else 1

    # ---- greedy incumbent -------------------------------------------------
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
            picked = (1 << n) - 1                    # fall back: everything
            break
        picked |= 1 << bestu
    best = [_pc(picked)]

    # ---- branch and bound -------------------------------------------------
    def lower_bound(unsat) -> int:
        """Disjoint-pool packing bound.

        If two unsatisfied vertices have disjoint candidate pools, no single pick
        can help both, so their minimum costs add.  A vertex that may be selected
        itself costs 1 however large its shortfall, because selecting it settles
        the constraint outright -- that distinction is what `gamma_2` needs.
        """
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
            # v is settled either by selecting v itself, or by `need` neighbours
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


def _cycle_in(adj: Sequence[int], S: int, n: int, odd_only: bool = False):
    """A short cycle (or short odd cycle) of `G[S]`, as a vertex set, or None."""
    best = None
    for src in range(n):
        if not (S >> src & 1):
            continue
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
                        if len(best) == 3:
                            return best
    return best


def _pack_cycles(adj: Sequence[int], S: int, n: int, odd_only: bool = False) -> int:
    """Greedy vertex-disjoint (odd) cycle packing of `G[S]`.

    Every packed cycle needs one of its own vertices deleted, so the packing size
    is a lower bound on the feedback vertex set (odd cycle transversal, when
    `odd_only`), and `|S| - k` bounds the largest induced forest (bipartite
    subgraph) from above.
    """
    rest = S
    k = 0
    while True:
        c = _cycle_in(adj, rest, n, odd_only)
        if c is None:
            return k
        k += 1
        for v in c:
            rest &= ~(1 << v)


def _greedy_induced_acyclic(adj: Sequence[int], n: int, odd_only: bool = False) -> int:
    """Feasible solution: repeatedly delete a highest-degree vertex of a witnessed cycle."""
    S = (1 << n) - 1
    while True:
        c = _cycle_in(adj, S, n, odd_only)
        if c is None:
            return _pc(S)
        v = max(c, key=lambda u: (_pc(adj[u] & S), -u))
        S &= ~(1 << v)


def _max_induced_acyclic_bb(adj: Sequence[int], n: int, odd_only: bool) -> int:
    """Largest induced forest (`odd_only=False`) or induced bipartite subgraph (True).

    Branch on a short (odd) cycle -- one of its vertices must go -- bounded above
    by the disjoint cycle packing and seeded with a greedy feasible solution.
    """
    best = [_greedy_induced_acyclic(adj, n, odd_only)]
    seen = set()

    def rec(S: int):
        sz = _pc(S)
        if sz <= best[0] or S in seen:
            return
        seen.add(S)
        c = _cycle_in(adj, S, n, odd_only)
        if c is None:
            best[0] = sz
            return
        if sz - _pack_cycles(adj, S, n, odd_only) <= best[0]:
            return
        for v in sorted(c):
            rec(S & ~(1 << v))
    rec((1 << n) - 1)
    return best[0]


def _max_induced_forest_bb(adj: Sequence[int], n: int) -> int:
    return _max_induced_acyclic_bb(adj, n, False)


def _max_induced_bipartite_bb(adj: Sequence[int], n: int) -> int:
    return _max_induced_acyclic_bb(adj, n, True)


def _scal_part(G: nx.Graph, adj: Sequence[int], n: int) -> Dict[str, object]:
    full = (1 << n) - 1
    comp = [full & ~(adj[v] | (1 << v)) for v in range(n)]
    lam = [_max_independent_bb(adj, adj[v], n) for v in range(n)]
    return {
        "alpha": _max_independent_bb(adj, full, n),
        "omega": _max_independent_bb(comp, full, n),
        "chi": _chromatic_brute(adj, n),
        "f": _max_induced_forest_bb(adj, n),
        "b": _max_induced_bipartite_bb(adj, n),
        "gamma": _min_dominating(adj, n, "gamma"),
        "gamma_t": _min_dominating(adj, n, "gamma_t"),
        "gamma_2": _min_dominating(adj, n, "gamma_2"),
        "gamma_i": _min_dominating(adj, n, "gamma_i"),
        "lam_max": max(lam), "lam_min": min(lam),
        "lam_avg": Fraction(sum(lam), n),
    }


# --------------------------------------------------------------------------
# public entry point
# --------------------------------------------------------------------------
def compute(G: nx.Graph, backend: str = "brute") -> Dict[str, object]:
    if not nx.is_connected(G):
        raise ValueError("G must be connected")
    base = _base(G)
    adj, n = base["adj"], base["n"]
    out = _poly_part(G, adj, n)
    if backend == "brute":
        out.update(_brute_part(adj, n))
    elif backend == "scal":
        out.update(_scal_part(G, adj, n))
    else:
        raise ValueError(backend)
    missing = [k for k in VOCAB if k not in out]
    if missing:
        raise AssertionError("missing invariants: %s" % missing)
    return {k: out[k] for k in VOCAB}
