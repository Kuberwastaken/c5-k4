"""GENERIC ARM -- third-code-path audit of every recorded crossing.

The standing verification bar asks for one independent recomputation.  This adds
a *third* one, deliberately using different algorithms again -- mostly library
routines and naive exhaustive enumeration rather than the arm's bitmask
branch-and-bound or `scripts/gen`'s solvers:

  n, m, degrees, dd, f1, res, annih  -- direct from `networkx` degree lists
  diam, rad, ecc, distances          -- `networkx.shortest_path_length`
  cutv, kappa, tri, mu               -- `networkx.articulation_points`,
                                        `node_connectivity`, `triangles`,
                                        `max_weight_matching`
  alpha, omega, lam_*                -- `networkx.max_weight_clique` (exact)
  chi                                -- minimum cover of V by independent sets,
                                        solved as an exact set-cover over all
                                        maximal independent sets (a different
                                        formulation from both DSATUR searches)
  gamma, gamma_t, gamma_2, gamma_i   -- naive `itertools.combinations` over all
                                        vertex subsets in increasing size
  spec_floor, spec_ceil              -- exact integer Sylvester test, with the
                                        floating-point spectral radius printed
                                        alongside for adjudication

Usage:
    python3 scripts/exp/generic/audit_crossings.py
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "gen"))

import networkx as nx                     # noqa: E402
import numpy as np                        # noqa: E402
import ginv                               # noqa: E402
import expressions as EXPR                # noqa: E402

EXPDIR = os.path.join(ROOT, "results", "experiment")


def naive(G: nx.Graph, keys):
    n = G.number_of_nodes()
    V = sorted(G.nodes())
    deg = dict(G.degree())
    sdeg = sorted(deg[v] for v in V)
    m = G.number_of_edges()
    out = {}
    sp = dict(nx.all_pairs_shortest_path_length(G))

    def need(k):
        return k in keys

    out["n"] = n
    out["m"] = m
    out["Delta"] = max(sdeg)
    out["delta"] = min(sdeg)
    out["Sigma2"] = sdeg[-2]
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
    tot, k = 0, 0
    for i, d in enumerate(sorted(sdeg)):
        tot += d
        if tot <= m:
            k = i + 1
    out["annih"] = k

    ecc = {v: max(sp[v].values()) for v in V}
    out["diam"] = max(ecc.values())
    out["rad"] = min(ecc.values())
    out["ecc_avg"] = Fraction(sum(ecc.values()), n)
    out["Tdist_min"] = min(sum(sp[v].values()) for v in V)
    out["Tdist_max"] = max(sum(sp[v].values()) for v in V)
    dev = {v: sum(1 for u in V if sp[v][u] % 2 == 0) for v in V}
    out["dist_even_min"] = min(dev.values())
    out["dist_even_max"] = max(dev.values())
    out["dist_avg"] = Fraction(sum(sum(sp[v].values()) for v in V), n * (n - 1))

    out["cutv"] = len(set(nx.articulation_points(G)))
    out["kappa"] = nx.node_connectivity(G)
    out["tri"] = sum(nx.triangles(G).values()) // 3
    disp = [len({deg[u] for u in G[v]}) for v in V]
    out["disp_max"] = max(disp)
    out["disp_min"] = min(disp)
    out["disp_avg"] = Fraction(sum(disp), n)
    out["mu"] = len(nx.max_weight_matching(G, maxcardinality=True))
    out["chi_bip"] = 1 if nx.is_bipartite(G) else 0
    out["chi_reg"] = 1 if max(sdeg) == min(sdeg) else 0
    out["chi_tree"] = 1 if m == n - 1 else 0
    c4 = any(len(set(G[u]) & set(G[v])) >= 2
             for u, v in itertools.combinations(V, 2))
    out["chi_C4free"] = 0 if c4 else 1

    C = nx.complement(G)
    if need("alpha"):
        out["alpha"] = len(nx.max_weight_clique(C, weight=None)[0])
    if need("omega"):
        out["omega"] = len(nx.max_weight_clique(G, weight=None)[0])
    if need("lam_max") or need("lam_min") or need("lam_avg"):
        lam = []
        for v in V:
            H = G.subgraph(list(G[v]))
            lam.append(0 if H.number_of_nodes() == 0
                       else len(nx.max_weight_clique(nx.complement(H),
                                                     weight=None)[0]))
        out["lam_max"] = max(lam)
        out["lam_min"] = min(lam)
        out["lam_avg"] = Fraction(sum(lam), n)
    if need("chi"):
        out["chi"] = _chi_setcover(G)
    for kind in ("gamma", "gamma_t", "gamma_2", "gamma_i"):
        if need(kind):
            out[kind] = _dom_naive(G, V, kind)
    if need("spec_floor") or need("spec_ceil"):
        n_, adj = ginv.from_graph6(nx.to_graph6_bytes(
            nx.convert_node_labels_to_integers(G, ordering="sorted"),
            header=False).decode().strip())
        keep = ginv.SPEC_CONVENTION
        ginv.SPEC_CONVENTION = "true"
        f, c = ginv.spectral_floor_ceil(n_, adj)
        ginv.SPEC_CONVENTION = keep
        out["spec_floor"], out["spec_ceil"] = f, c
        A = nx.to_numpy_array(G)
        out["_lambda1_float"] = float(max(np.linalg.eigvalsh(A)))
    return out


def _chi_setcover(G: nx.Graph) -> int:
    """chi(G) = fewest independent sets covering V; exact set cover over all
    maximal independent sets (found by Bron-Kerbosch on the complement)."""
    V = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(V)}
    n = len(V)
    C = nx.complement(G)
    sets = []
    for cl in nx.find_cliques(C):          # maximal cliques of Gbar = max. ind. sets of G
        mask = 0
        for v in cl:
            mask |= 1 << idx[v]
        sets.append(mask)
    full = (1 << n) - 1
    for k in range(1, n + 1):
        if _cover(sets, full, k):
            return k
    return n


def _cover(sets, remaining, k) -> bool:
    if remaining == 0:
        return True
    if k == 0:
        return False
    v = (remaining & -remaining).bit_length() - 1
    for s in sets:
        if s >> v & 1:
            if _cover(sets, remaining & ~s, k - 1):
                return True
    return False


def _dom_naive(G: nx.Graph, V, kind) -> int:
    adjs = {v: set(G[v]) for v in V}
    closed = {v: adjs[v] | {v} for v in V}
    n = len(V)
    for size in range(1, n + 1):
        for S in itertools.combinations(V, size):
            T = set(S)
            if kind == "gamma":
                if all(closed[v] & T for v in V):
                    return size
            elif kind == "gamma_t":
                if all(adjs[v] & T for v in V):
                    return size
            elif kind == "gamma_i":
                if all(closed[v] & T for v in V) and \
                        all(not (adjs[u] & T) for u in T):
                    return size
            else:                                    # gamma_2
                if all((v in T) or len(adjs[v] & T) >= 2 for v in V):
                    return size
    return n


def main() -> int:
    res = json.load(open(os.path.join(EXPDIR, "arm-generic.json")))
    pop = {t["id"]: t for t in json.load(
        open(os.path.join(EXPDIR, "fresh-population", "population.json")))["targets"]}
    audit = []
    allok = True
    for row in res["targets"]:
        if row["verdict"] != "CROSSED":
            continue
        tid = row["id"]
        t = pop[tid]
        g6 = row["refuting_graph6"]
        G = nx.from_graph6_bytes(g6.encode())
        keys = ginv.invariants_of(t["expr"]["lhs"]) | ginv.invariants_of(t["expr"]["rhs"])
        vals = naive(G, keys)
        lhs = EXPR.evaluate(t["expr"]["lhs"], vals)
        rhs = EXPR.evaluate(t["expr"]["rhs"], vals)
        sl = EXPR.slack(t["expr"], vals)
        ok = (sl < 0 and str(lhs) == row["lhs_at_witness"]
              and str(rhs) == row["rhs_at_witness"]
              and nx.is_connected(G))
        allok = allok and ok
        entry = {"id": tid, "graph6": g6, "n": G.number_of_nodes(),
                 "third_path_lhs": str(lhs), "third_path_rhs": str(rhs),
                 "third_path_slack": str(sl),
                 "arm_lhs": row["lhs_at_witness"], "arm_rhs": row["rhs_at_witness"],
                 "connected": bool(nx.is_connected(G)),
                 "status": "PASS" if ok else "FAIL",
                 "invariants": {k: str(vals[k]) for k in sorted(keys)}}
        if "_lambda1_float" in vals:
            entry["lambda_1_float"] = round(vals["_lambda1_float"], 10)
        audit.append(entry)
        print("%s  n=%d  LHS=%s RHS=%s slack=%s  %s"
              % (tid, entry["n"], lhs, rhs, sl, entry["status"]), flush=True)
    out = {"note": "third independent code path (networkx primitives, exact "
                   "set-cover chromatic number, naive itertools domination) "
                   "recomputing every recorded crossing",
           "all_pass": allok, "crossings": audit}
    with open(os.path.join(EXPDIR, "arm-generic-runs", "_audit3.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("third-path audit: %d crossings, all_pass=%s" % (len(audit), allok))
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
