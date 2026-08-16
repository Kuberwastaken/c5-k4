"""Second, independent code path for the catalogue arm of the three-arm test.

Nothing here imports ``scripts/gen/invariants.py``.  Every invariant used by the
frozen population is recomputed from scratch, with a deliberately different
algorithm from the campaign's:

  * independence / clique / local independence  -> ``networkx.max_weight_clique``
    (exact) on G or its complement, instead of the campaign's bitmask
    branch-and-bound;
  * chromatic number, matching number and the four domination numbers -> SAT
    (``python-sat``) with cardinality constraints, instead of DSATUR
    branch-and-bound / blossom / packing-bounded branch-and-bound;
  * distances -> ``networkx`` BFS instead of bitmask-frontier BFS;
  * vertex connectivity -> vertex-splitting max-flow written here, instead of
    ``networkx.node_connectivity``;
  * spectral radius bracket -> float ``numpy.linalg.eigvalsh`` with an integrality
    guard, instead of exact Sylvester principal minors.

Definitions are taken verbatim from ``invariant_definitions`` in
``results/experiment/fresh-population/population.json`` (see ``DEFINITIONS``
below, which the driver asserts against the population file).

Also provides an independent evaluator for the population's expression AST.
"""
from __future__ import annotations

import itertools
import math
import time
from fractions import Fraction

import networkx as nx
import numpy as np

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Solver

SAT_NAME = "cadical153"


def _sat():
    try:
        return Solver(name=SAT_NAME)
    except Exception:                                    # pragma: no cover
        return Solver(name="m22")


# Definitions as shipped in population.json; asserted by the driver.
DEFINITIONS = {
    "CW": "Caro-Wei invariant sum_v 1/(1+deg v)",
    "Delta": "maximum degree",
    "Sigma2": "second largest degree of the degree sequence",
    "Tdist_max": "max over v of the total distance sum_u dist(v,u)",
    "Tdist_min": "min over v of the total distance sum_u dist(v,u)",
    "alpha": "independence number",
    "annih": "annihilation number: largest k with the k smallest degrees summing to at most m",
    "chi": "chromatic number",
    "chi_C4free": "1 if G contains no 4-cycle (not necessarily induced), else 0",
    "chi_bip": "1 if G is bipartite, else 0",
    "chi_reg": "1 if G is regular, else 0",
    "chi_tree": "1 if G is a tree, else 0",
    "cutv": "number of cut vertices",
    "dd": "number of distinct degrees",
    "deg_avg": "average degree 2m/n",
    "delta": "minimum degree",
    "diam": "diameter",
    "disp_avg": "average over v of the number of distinct degrees among the neighbours of v",
    "disp_max": "max over v of the number of distinct degrees among the neighbours of v",
    "disp_min": "min over v of the number of distinct degrees among the neighbours of v",
    "dist_avg": "average distance over unordered pairs of distinct vertices",
    "dist_even_max": "max over v of #{u : dist(v,u) even}, counting v itself",
    "dist_even_min": "min over v of #{u : dist(v,u) even}, counting v itself",
    "ecc_avg": "average eccentricity",
    "f1": "number of degree-1 (pendant) vertices",
    "gamma": "domination number",
    "gamma_2": "2-domination number",
    "gamma_i": "independent domination number",
    "gamma_t": "total domination number",
    "kappa": "vertex connectivity",
    "lam_avg": "average over v of lambda(v) = alpha(G[N(v)])",
    "lam_max": "max over v of the local independence lambda(v) = alpha(G[N(v)])",
    "lam_min": "min over v of the local independence lambda(v) = alpha(G[N(v)])",
    "m": "number of edges",
    "mu": "matching number",
    "n": "number of vertices",
    "omega": "clique number",
    "rad": "radius",
    "res": "residue: number of zeros left by the Havel-Hakimi process",
    "spec_ceil": "ceiling of the adjacency spectral radius (exact, via principal minors)",
    "spec_floor": "floor of the adjacency spectral radius (exact, via principal minors)",
    "tri": "number of triangles",
}


# --------------------------------------------------------------------------
# exact independence / clique via networkx max_weight_clique
# --------------------------------------------------------------------------
def _alpha(G):
    if G.number_of_nodes() == 0:
        return 0
    if G.number_of_nodes() == 1:
        return 1
    _, w = nx.max_weight_clique(nx.complement(G), None)
    return int(w)


def _omega(G):
    if G.number_of_nodes() == 0:
        return 0
    _, w = nx.max_weight_clique(G, None)
    return int(w)


# --------------------------------------------------------------------------
# SAT helpers
# --------------------------------------------------------------------------
def _sat_min_subset(n, clauses_fn, lo, hi, extra_lits=None):
    """Smallest k in [lo, hi] for which the encoded predicate is satisfiable.

    ``clauses_fn(pool)`` returns (clauses, sel_vars) where sel_vars are the n
    selection literals whose cardinality is being minimised.
    """
    for k in range(lo, hi + 1):
        pool = IDPool()
        clauses, sel = clauses_fn(pool)
        card = CardEnc.atmost(lits=sel, bound=k, vpool=pool, encoding=EncType.seqcounter)
        with _sat() as s:
            for c in clauses:
                s.add_clause(c)
            for c in card.clauses:
                s.add_clause(c)
            if s.solve():
                return k
    raise RuntimeError("no feasible solution up to %d" % hi)


def _bits(x):
    out = []
    while x:
        b = x & -x
        out.append(b.bit_length() - 1)
        x ^= b
    return out


def _dom_clauses(adj, n, kind):
    """Clause builder for the four domination variants.

      gamma    every v has a selected vertex in N[v]
      gamma_t  every v has a selected vertex in N(v)
      gamma_2  every v is selected, or has >= 2 selected neighbours
      gamma_i  gamma, plus the selected set is independent
    """
    closed = [adj[v] | (1 << v) for v in range(n)]

    def f(pool):
        x = [pool.id(("x", v)) for v in range(n)]
        cl = []
        if kind == "gamma":
            for v in range(n):
                cl.append([x[u] for u in _bits(closed[v])])
        elif kind == "gamma_t":
            for v in range(n):
                cl.append([x[u] for u in _bits(adj[v])])
        elif kind == "gamma_i":
            for v in range(n):
                cl.append([x[u] for u in _bits(closed[v])])
            for u in range(n):
                for w in _bits(adj[u]):
                    if u < w:
                        cl.append([-x[u], -x[w]])
        elif kind == "gamma_2":
            # "not x_v -> at least 2 of N(v)", encoded as: for every u in N(v),
            # (x_v or some neighbour other than u).  Together these say exactly
            # that at most one neighbour can be unselected unless x_v holds.
            for v in range(n):
                nb = _bits(adj[v])
                for u in nb:
                    cl.append([x[v]] + [x[w] for w in nb if w != u])
                if len(nb) < 2:
                    cl.append([x[v]])
        else:
            raise ValueError(kind)
        return cl, x
    return f


def _chromatic(G, omega_lb, alpha_lb=None):
    """Exact chromatic number by SAT.

    Returns ``(chi, colouring)`` where ``colouring`` is a proper chi-colouring
    indexed by ``sorted(G.nodes())`` -- an explicit, independently checkable
    certificate for the upper bound.
    """
    n = G.number_of_nodes()
    if n == 0:
        return 0, []
    nodes = sorted(G.nodes())
    pos = {v: i for i, v in enumerate(nodes)}
    if G.number_of_edges() == 0:
        return 1, [0] * n
    clique, _ = nx.max_weight_clique(G, None)
    clique = sorted(pos[v] for v in clique)
    edges = [(pos[u], pos[v]) for u, v in G.edges()]

    # upper bound: greedy DSATUR, with its colouring kept as the certificate
    gc = nx.coloring.greedy_color(G, strategy="DSATUR")
    best_col = [gc[v] for v in nodes]
    ub = max(best_col) + 1
    lb = max(omega_lb, len(clique))
    if alpha_lb:
        lb = max(lb, -(-n // alpha_lb))          # chi >= n / alpha
    if lb >= ub:
        return ub, best_col

    for k in range(lb, ub):
        pool = IDPool()
        x = [[pool.id(("c", v, c)) for c in range(k)] for v in range(n)]
        cl = []
        for v in range(n):
            cl.append(list(x[v]))
            for a in range(k):
                for b in range(a + 1, k):
                    cl.append([-x[v][a], -x[v][b]])
        for u, v in edges:
            for c in range(k):
                cl.append([-x[u][c], -x[v][c]])
        for i, v in enumerate(clique[:k]):        # symmetry breaking
            cl.append([x[v][i]])
        with _sat() as s:
            for c in cl:
                s.add_clause(c)
            if s.solve():
                model = set(lit for lit in s.get_model() if lit > 0)
                col = [next(c for c in range(k) if x[v][c] in model) for v in range(n)]
                return k, col
    return ub, best_col


def _matching_number(G):
    """Maximum matching size by SAT (edge selection + degree-<=1 + cardinality)."""
    edges = list(G.edges())
    if not edges:
        return 0
    inc = {v: [] for v in G.nodes()}
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    best = 0
    lo, hi = 1, min(len(edges), G.number_of_nodes() // 2)
    for k in range(hi, lo - 1, -1):
        pool = IDPool()
        e = [pool.id(("e", i)) for i in range(len(edges))]
        cl = []
        for v, lst in inc.items():
            for a in range(len(lst)):
                for b in range(a + 1, len(lst)):
                    cl.append([-e[lst[a]], -e[lst[b]]])
        card = CardEnc.atleast(lits=e, bound=k, vpool=pool, encoding=EncType.seqcounter)
        with _sat() as s:
            for c in cl:
                s.add_clause(c)
            for c in card.clauses:
                s.add_clause(c)
            if s.solve():
                best = k
                break
    return best


# --------------------------------------------------------------------------
# vertex connectivity: vertex splitting + max flow, written here
# --------------------------------------------------------------------------
def _split_digraph(G):
    D = nx.DiGraph()
    INF = G.number_of_nodes() + 10
    for v in G.nodes():
        D.add_edge(("i", v), ("o", v), capacity=1)
    for u, v in G.edges():
        D.add_edge(("o", u), ("i", v), capacity=INF)
        D.add_edge(("o", v), ("i", u), capacity=INF)
    return D, INF


def _kappa(G):
    nodes = list(G.nodes())
    n = len(nodes)
    if n <= 1:
        return 0
    nonadj = [(u, v) for u, v in itertools.combinations(nodes, 2) if not G.has_edge(u, v)]
    if not nonadj:
        return n - 1
    D, INF = _split_digraph(G)
    best = n
    for s, t in nonadj:
        D[("i", s)][("o", s)]["capacity"] = INF
        D[("i", t)][("o", t)]["capacity"] = INF
        val = int(nx.maximum_flow_value(D, ("o", s), ("i", t)))
        D[("i", s)][("o", s)]["capacity"] = 1
        D[("i", t)][("o", t)]["capacity"] = 1
        if val < best:
            best = val
    return best


# --------------------------------------------------------------------------
# main entry point
# --------------------------------------------------------------------------
def invariants(G, timed=False):
    """All 42 invariants named by the frozen population, exact int/Fraction.

    With ``timed=True`` returns ``(values, per-block seconds)`` using the same
    block names as path A (``poly``, ``alpha``, ``omega``, ``chi``, ``lam``,
    ``gamma``, ``gamma_t``, ``gamma_2``, ``gamma_i``); ``mu`` is charged to
    ``poly``, matching path A where it lives inside ``_poly_part``.
    """
    assert nx.is_connected(G), "G must be connected"
    _t = {k: 0.0 for k in ("poly", "alpha", "omega", "chi", "lam",
                           "gamma", "gamma_t", "gamma_2", "gamma_i")}
    _t0 = time.monotonic()
    nodes = sorted(G.nodes())
    n = len(nodes)
    pos = {v: i for i, v in enumerate(nodes)}
    m = G.number_of_edges()
    adj = [0] * n
    for u, v in G.edges():
        adj[pos[u]] |= 1 << pos[v]
        adj[pos[v]] |= 1 << pos[u]

    deg = [G.degree(v) for v in nodes]
    sdeg = sorted(deg)
    out = {}
    out["n"] = n
    out["m"] = m
    out["Delta"] = sdeg[-1]
    out["delta"] = sdeg[0]
    out["Sigma2"] = sdeg[-2]
    out["dd"] = len(set(sdeg))
    out["f1"] = sdeg.count(1)
    out["deg_avg"] = Fraction(2 * m, n)
    out["CW"] = sum((Fraction(1, 1 + d) for d in deg), Fraction(0))

    # residue: Havel-Hakimi, implemented with a multiset counter
    seq = sorted(deg, reverse=True)
    while seq and seq[0] > 0:
        d = seq[0]
        rest = seq[1:]
        for i in range(d):
            rest[i] -= 1
        seq = sorted(rest, reverse=True)
    out["res"] = len(seq)

    # annihilation: prefix sums of the ascending degree sequence
    pref = 0
    k = 0
    for d in sdeg:
        pref += d
        if pref <= m:
            k += 1
        else:
            break
    out["annih"] = k

    # distances via networkx BFS
    sp = dict(nx.all_pairs_shortest_path_length(G))
    ecc = {}
    tdist = {}
    deven = {}
    wiener = 0
    for v in nodes:
        dv = sp[v]
        ecc[v] = max(dv.values())
        tdist[v] = sum(dv.values())
        deven[v] = sum(1 for u in nodes if dv[u] % 2 == 0)
        wiener += tdist[v]
    out["diam"] = max(ecc.values())
    out["rad"] = min(ecc.values())
    out["ecc_avg"] = Fraction(sum(ecc.values()), n)
    out["Tdist_min"] = min(tdist.values())
    out["Tdist_max"] = max(tdist.values())
    out["dist_even_min"] = min(deven.values())
    out["dist_even_max"] = max(deven.values())
    out["dist_avg"] = Fraction(wiener, n * (n - 1))

    out["kappa"] = _kappa(G)

    cutv = 0
    for v in nodes:
        H = G.copy()
        H.remove_node(v)
        if H.number_of_nodes() and not nx.is_connected(H):
            cutv += 1
    out["cutv"] = cutv

    tri = 0
    for a in range(n):
        for b in range(a + 1, n):
            if adj[a] >> b & 1:
                tri += bin(adj[a] & adj[b] & ~((1 << (b + 1)) - 1)).count("1")
    out["tri"] = tri

    degmap = {v: G.degree(v) for v in nodes}
    disp = [len({degmap[u] for u in G[v]}) for v in nodes]
    out["disp_max"] = max(disp)
    out["disp_min"] = min(disp)
    out["disp_avg"] = Fraction(sum(disp), n)

    # spectral radius bracket, float with an integrality guard
    A = np.zeros((n, n))
    for u, v in G.edges():
        A[pos[u], pos[v]] = 1.0
        A[pos[v], pos[u]] = 1.0
    lam1 = float(np.max(np.linalg.eigvalsh(A)))
    r = round(lam1)
    if abs(lam1 - r) < 1e-9:
        out["spec_floor"] = int(r)
        out["spec_ceil"] = int(r)
    else:
        out["spec_floor"] = int(math.floor(lam1))
        out["spec_ceil"] = int(math.ceil(lam1))

    out["mu"] = _matching_number(G)

    out["chi_bip"] = 1 if nx.is_bipartite(G) else 0
    c4 = any(len(set(G[u]) & set(G[v])) >= 2
             for u, v in itertools.combinations(nodes, 2))
    out["chi_C4free"] = 0 if c4 else 1
    out["chi_reg"] = 1 if out["Delta"] == out["delta"] else 0
    out["chi_tree"] = 1 if m == n - 1 else 0
    _t["poly"] = time.monotonic() - _t0

    _t0 = time.monotonic()
    out["alpha"] = _alpha(G)
    _t["alpha"] = time.monotonic() - _t0

    _t0 = time.monotonic()
    out["omega"] = _omega(G)
    _t["omega"] = time.monotonic() - _t0

    _t0 = time.monotonic()
    lam = []
    for v in nodes:
        nb = list(G[v])
        lam.append(_alpha(G.subgraph(nb)) if nb else 0)
    out["lam_max"] = max(lam)
    out["lam_min"] = min(lam)
    out["lam_avg"] = Fraction(sum(lam), n)
    _t["lam"] = time.monotonic() - _t0

    _t0 = time.monotonic()
    out["chi"], _colouring = _chromatic(G, out["omega"], out["alpha"])
    _t["chi"] = time.monotonic() - _t0
    out["_chi_colouring"] = _colouring

    for kind in ("gamma", "gamma_t", "gamma_2", "gamma_i"):
        _t0 = time.monotonic()
        out[kind] = _sat_min_subset(n, _dom_clauses(adj, n, kind), 1, n)
        _t[kind] = time.monotonic() - _t0

    return (out, _t) if timed else out


# --------------------------------------------------------------------------
# independent evaluator for the population's expression AST
# --------------------------------------------------------------------------
def ev(node, vals):
    if "inv" in node:
        return Fraction(vals[node["inv"]])
    if "const" in node:
        return Fraction(node["const"])
    op = node["op"]
    if op == "add":
        tot = Fraction(0)
        for a in node["args"]:
            tot += ev(a, vals)
        return tot
    if op == "sub":
        a, b = node["args"]
        return ev(a, vals) - ev(b, vals)
    if op == "mul":
        return Fraction(node["c"]) * ev(node["arg"], vals)
    if op == "ceil_div":
        q = ev(node["arg"], vals) / Fraction(node["d"])
        return Fraction(-((-q.numerator) // q.denominator))
    if op == "floor_div":
        q = ev(node["arg"], vals) / Fraction(node["d"])
        return Fraction(q.numerator // q.denominator)
    if op == "ceil_ratio":
        den = ev(node["den"], vals)
        if den <= 0:
            raise ZeroDivisionError("non-positive denominator")
        q = ev(node["num"], vals) / den
        return Fraction(-((-q.numerator) // q.denominator))
    if op == "floor_ratio":
        den = ev(node["den"], vals)
        if den <= 0:
            raise ZeroDivisionError("non-positive denominator")
        q = ev(node["num"], vals) / den
        return Fraction(q.numerator // q.denominator)
    raise ValueError(op)


def sides(expr, vals):
    return ev(expr["lhs"], vals), ev(expr["rhs"], vals)


def holds(expr, vals):
    lhs, rhs = sides(expr, vals)
    return lhs <= rhs if expr["rel"] == "<=" else lhs >= rhs
