#!/usr/bin/env python3
"""Shared exact apparatus for the WOWII 305 + 308 trial (trial_305_308).

Everything exact (Fraction/int). Two independent engines for gamma_t
(enumeration certificates + ILP), exhaustive tie-break reachable-set
computation for maxine, and the four frozen readings of |N_bar(G)(e)|.
No spectral quantities are used anywhere.
"""

from __future__ import annotations

import itertools
import math
from fractions import Fraction

import networkx as nx

# --------------------------------------------------------------------------
# gamma_t — engine A: ascending-k subset enumeration with witness certificate


def is_total_dominating(g: nx.Graph, s) -> bool:
    sset = set(s)
    return all(any(w in sset for w in g.neighbors(v)) for v in g)


def gamma_t_enum(g: nx.Graph):
    """Return (size, witness frozenset). Exact; ascending k with first hit."""
    verts = tuple(g)
    for k in range(1, len(verts) + 1):
        for sub in itertools.combinations(verts, k):
            if is_total_dominating(g, sub):
                return k, frozenset(sub)
    raise AssertionError("no total dominating set (disconnected?)")


# --------------------------------------------------------------------------
# gamma_t — engine B: ILP (pulp/CBC), independent formulation


def gamma_t_ilp(g: nx.Graph, time_limit=55):
    import pulp

    verts = list(g)
    prob = pulp.LpProblem("gamma_t", pulp.LpMinimize)
    x = {v: pulp.LpVariable(f"x_{v}", cat="Binary") for v in verts}
    prob += pulp.lpSum(x.values())
    for u in verts:
        # TOTAL domination: every vertex needs a *neighbor* in the set.
        prob += pulp.lpSum(x[w] for w in g.neighbors(u)) >= 1
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    status = prob.solve(solver)
    if pulp.LpStatus[status] != "Optimal":
        return None, None, pulp.LpStatus[status]
    witness = frozenset(v for v in verts if x[v].value() > 0.5)
    assert is_total_dominating(g, witness)
    return len(witness), witness, "Optimal"


# --------------------------------------------------------------------------
# maxine — closed-neighborhood greedy; reachable set over ALL deterministic
# tie-break rules (exhaustive branching, memoized on the remaining vertex set).


def maxine_reachable(g: nx.Graph) -> set:
    """All values of |S| reachable by any run of the frozen greedy."""
    adj = {v: frozenset(g.neighbors(v)) for v in g}
    memo: dict = {}

    def solve(state: frozenset) -> set:
        if state in memo:
            return memo[state]
        # degrees inside induced subgraph
        maxdeg, maxverts = 0, []
        for v in state:
            d = len(adj[v] & state)
            if d > maxdeg:
                maxdeg, maxverts = d, [v]
            elif d == maxdeg:
                maxverts.append(v)
        if maxdeg == 0:  # discrete: everything remaining joins S
            res = {len(state)}
        else:
            res = set()
            seen_moves = set()
            for v in maxverts:
                move = state - (adj[v] & state) - {v}
                if move in seen_moves:
                    continue
                seen_moves.add(move)
                res |= {r + 1 for r in solve(move)}
        memo[state] = res
        return res

    return solve(frozenset(g))


def maxine_det(g: nx.Graph) -> int:
    """Deterministic default rule: lowest-label maximum-degree vertex."""
    cur = g.copy()
    count = 0
    while True:
        if cur.number_of_edges() == 0:
            return count + cur.number_of_nodes()
        maxdeg = max(dict(cur.degree()).values())
        v = min(u for u, d in cur.degree() if d == maxdeg)
        closed = set(cur.neighbors(v)) | {v}
        cur.remove_nodes_from(closed)
        count += 1


# --------------------------------------------------------------------------
# The four frozen readings of |N_bar(G)(e)|


def nbar_readings(g: nx.Graph) -> dict:
    comp = nx.complement(g)
    n = g.number_of_nodes()
    nonedges = [
        (u, v)
        for u, v in itertools.combinations(tuple(g), 2)
        if not g.has_edge(u, v)
    ]
    b_vals, a_vals, c_vals, d_vals = [], [], [], []
    for u, v in comp.edges():
        cu, cv = set(comp[u]), set(comp[v])
        union = cu | cv
        b_vals.append(len(union))
        a_vals.append(len(union - {u, v}))
        assert b_vals[-1] == n - len(set(g[u]) & set(g[v]))
    for u, v in g.edges():
        union = set(comp[u]) | set(comp[v])
        c_vals.append(len(union))
        assert union.isdisjoint({u, v})
        assert c_vals[-1] == n - 2 - len(set(g[u]) & set(g[v]))
    for u, v in nonedges:
        d_vals.append(len(set(g[u]) | set(g[v])))
    return {"B": b_vals, "A": a_vals, "C": c_vals, "D": d_vals}


READINGS = {
    "B": "comp-edge incl (309-locked): e in E(barG), open union in barG incl endpoints",
    "A": "comp-edge excl: e in E(barG), union minus endpoints",
    "C": "G-edge in bar: e in E(G), open union in barG",
    "D": "N_G(nonedge): e nonedge of G, open union in G",
}


# --------------------------------------------------------------------------
# Residuals


def residual_305(vals, gamma_t: int):
    """R = ceil((2/3)*max|N_bar(e)|) - gamma_t, exact Fraction."""
    if not vals:
        return None
    m = Fraction(max(vals))
    rhs = math.ceil(Fraction(2, 3) * m)
    return Fraction(rhs - gamma_t)


def residual_308(vals, gamma_t: int, maxine_val: int):
    """R = (maxine + min|N_bar(e)|)/2 - gamma_t, exact Fraction."""
    if not vals:
        return None
    return Fraction(maxine_val + min(vals), 2) - gamma_t


# --------------------------------------------------------------------------
# Named graph builders


def cycle_blowup(w):
    """Lexicographic blow-up of the cycle C_len(w) by cliques of sizes w."""
    k = len(w)
    g = nx.Graph()
    blobs = []
    start = 0
    for size in w:
        blobs.append(list(range(start, start + size)))
        start += size
    g.add_nodes_from(itertools.chain.from_iterable(blobs))
    for blob in blobs:
        g.add_edges_from(itertools.combinations(blob, 2))
    for i in range(k):
        for u in blobs[i]:
            for v in blobs[(i + 1) % k]:
                g.add_edge(u, v)
    return g


def c5_blowup(w):
    return cycle_blowup(w)


def line_T(k):
    return nx.convert_node_labels_to_integers(nx.line_graph(nx.complete_graph(k)))


def cocktail_party(k):
    g = nx.Graph()
    vs = range(2 * k)
    g.add_nodes_from(vs)
    for u, v in itertools.combinations(vs, 2):
        if u != (v ^ 1):
            g.add_edge(u, v)
    return g


def diamond():
    g = nx.complete_graph(4)
    g.remove_edge(2, 3)
    return nx.convert_node_labels_to_integers(g)


def subdivided_c5(extra):  # extra internal vertices on rim edge 0-1
    g = nx.cycle_graph(5)
    if extra:
        g.remove_edge(0, 1)
        nx.add_path(g, [0] + [100 + i for i in range(extra)] + [1])
    return nx.convert_node_labels_to_integers(g)


def named_controls():
    out = {}
    for n in range(5, 10):
        out[f"C{n}"] = nx.cycle_graph(n)
    out["P7"] = nx.path_graph(7)
    out["Petersen"] = nx.petersen_graph()
    out["K3,3"] = nx.complete_bipartite_graph(3, 3)
    out["K7"] = nx.complete_graph(7)
    for n in range(3, 9):
        out[f"K1,{n}"] = nx.star_graph(n)
    for n in range(2, 7):
        out[f"K{n},{n}"] = nx.complete_bipartite_graph(n, n)
    return out


def atlas_connected(min_n=3, max_n=7):
    for g in nx.graph_atlas_g():
        n = g.number_of_nodes()
        if min_n <= n <= max_n and nx.is_connected(g):
            yield g


# --------------------------------------------------------------------------
# Full row evaluation


def evaluate(g: nx.Graph, engines=("enum",)):
    row = {
        "n": g.number_of_nodes(),
        "connected": nx.is_connected(g),
    }
    gt_e, wit = gamma_t_enum(g)
    row["gamma_t"] = gt_e
    row["witness"] = sorted(wit)
    if "ilp" in engines:
        gt_i, wit_i, st = gamma_t_ilp(g)
        row["gamma_t_ilp"] = gt_i
        row["engines_agree"] = gt_i == gt_e
    mx = maxine_reachable(g)
    row["maxmin"] = min(mx)
    row["maxmax"] = max(mx)
    row["maxset"] = sorted(mx)
    row["maxdet"] = maxine_det(g)
    rdgs = nbar_readings(g)
    for key, vals in rdgs.items():
        if not vals:
            row[f"applicable_{key}"] = False
            continue
        row[f"applicable_{key}"] = True
        row[f"max_{key}"] = max(vals)
        row[f"min_{key}"] = min(vals)
        row[f"R305_{key}"] = residual_305(vals, gt_e)
        row[f"R308min_{key}"] = residual_308(vals, gt_e, min(mx))
        row[f"R308max_{key}"] = residual_308(vals, gt_e, max(mx))
    return row
