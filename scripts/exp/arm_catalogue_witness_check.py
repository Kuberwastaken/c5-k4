"""Third check on the catalogue arm's crossings: naive brute force, from graph6.

Independent of both path A and path B.  For each crossed target the smallest
recorded witness is rebuilt **from the graph6 string in
`results/experiment/arm-catalogue.json`** (so the recorded witness itself is
checked), and only the invariants that target actually names are recomputed, by
exhaustive enumeration:

  * alpha / omega            subset dynamic programming over all 2^n subsets;
  * gamma, gamma_t, gamma_2, gamma_i, lambda(v)
                             enumeration of subsets by increasing (decreasing)
                             size, stopping at the first feasible one;
  * mu                       enumeration of sets of pairwise disjoint edges;
  * chi                      explicit colouring search from the lower bound
                             max(omega, ceil(n/alpha)) upward, the colouring
                             checked edge by edge;
  * everything else          direct definition, networkx BFS, float eigenvalues.

Usage:  python3 scripts/exp/arm_catalogue_witness_check.py
"""
from __future__ import annotations

import itertools
import json
import math
import os
from fractions import Fraction

import networkx as nx
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RESULT = os.path.join(ROOT, "results", "experiment", "arm-catalogue.json")

MAX_N = 22                      # 2^n subset DP limit
MAX_EDGES_FOR_MU = 14


def _pc(x):
    return bin(x).count("1")


def _independent_table(adj, n):
    """bytearray T with T[S] = 1 iff S is an independent set."""
    T = bytearray(1 << n)
    T[0] = 1
    for S in range(1, 1 << n):
        v = (S & -S).bit_length() - 1
        T[S] = 1 if (T[S ^ (1 << v)] and not (adj[v] & S)) else 0
    return T


def _min_subset(n, pred, cap=None):
    """Smallest subset size for which `pred(bitmask)` holds."""
    for k in range(0, (cap or n) + 1):
        for T in itertools.combinations(range(n), k):
            S = 0
            for v in T:
                S |= 1 << v
            if pred(S):
                return k
    raise RuntimeError("no feasible subset")


def brute(G, needed):
    nodes = sorted(G.nodes())
    n = len(nodes)
    pos = {v: i for i, v in enumerate(nodes)}
    adj = [0] * n
    for u, v in G.edges():
        adj[pos[u]] |= 1 << pos[v]
        adj[pos[v]] |= 1 << pos[u]
    closed = [adj[v] | (1 << v) for v in range(n)]
    full = (1 << n) - 1
    deg = [_pc(a) for a in adj]
    m = G.number_of_edges()
    out = {}

    def want(*ks):
        return any(k in needed for k in ks)

    indep = None
    if want("alpha", "gamma_i", "chi", "lam_max", "lam_min", "lam_avg"):
        indep = _independent_table(adj, n)
    if want("alpha", "chi"):
        out["alpha"] = max(_pc(S) for S in range(1 << n) if indep[S])
    if want("omega"):
        comp = [full & ~(adj[v] | (1 << v)) for v in range(n)]
        ct = _independent_table(comp, n)
        out["omega"] = max(_pc(S) for S in range(1 << n) if ct[S])

    def dominates(S):
        cov = 0
        for v in range(n):
            if S >> v & 1:
                cov |= closed[v]
        return cov == full

    if want("gamma"):
        out["gamma"] = _min_subset(n, dominates)
    if want("gamma_i"):
        out["gamma_i"] = _min_subset(n, lambda S: indep[S] and dominates(S))
    if want("gamma_t"):
        out["gamma_t"] = _min_subset(n, lambda S: all(adj[v] & S for v in range(n)))
    if want("gamma_2"):
        out["gamma_2"] = _min_subset(
            n, lambda S: all((S >> v & 1) or _pc(adj[v] & S) >= 2 for v in range(n)))

    if want("lam_max", "lam_min", "lam_avg"):
        lam = []
        for v in range(n):
            nb = adj[v]
            best = 0
            sub = nb
            # enumerate subsets of N(v) directly
            S = nb
            while True:
                if indep[S] and _pc(S) > best:
                    best = _pc(S)
                if S == 0:
                    break
                S = (S - 1) & nb
            lam.append(best)
        out["lam_max"], out["lam_min"] = max(lam), min(lam)
        out["lam_avg"] = Fraction(sum(lam), n)

    if want("mu"):
        edges = [(pos[u], pos[v]) for u, v in G.edges()]
        assert len(edges) <= MAX_EDGES_FOR_MU, "mu enumeration too large"
        best = 0
        for r in range(min(len(edges), n // 2), 0, -1):
            for T in itertools.combinations(edges, r):
                seen = set()
                ok = True
                for a, b in T:
                    if a in seen or b in seen:
                        ok = False
                        break
                    seen.add(a)
                    seen.add(b)
                if ok:
                    best = r
                    break
            if best:
                break
        out["mu"] = best

    if want("chi"):
        lb = max(out.get("omega", 1), -(-n // out["alpha"]))
        order = sorted(range(n), key=lambda v: -deg[v])
        for k in range(lb, n + 1):
            colour = [-1] * n

            def rec(i):
                if i == len(order):
                    return True
                v = order[i]
                used = {colour[u] for u in range(n) if adj[v] >> u & 1 and colour[u] >= 0}
                for c in range(k):
                    if c in used:
                        continue
                    colour[v] = c
                    if rec(i + 1):
                        return True
                    colour[v] = -1
                return False

            if rec(0):
                assert all(colour[u] != colour[v] for v in range(n)
                           for u in range(n) if adj[v] >> u & 1)
                out["chi"] = k
                break

    sp = dict(nx.all_pairs_shortest_path_length(G))
    ecc = {v: max(sp[v].values()) for v in nodes}
    simple = {
        "n": n, "m": m,
        "Delta": max(deg), "delta": min(deg), "Sigma2": sorted(deg)[-2],
        "dd": len(set(deg)), "f1": deg.count(1),
        "deg_avg": Fraction(2 * m, n),
        "CW": sum((Fraction(1, 1 + d) for d in deg), Fraction(0)),
        "diam": max(ecc.values()), "rad": min(ecc.values()),
        "ecc_avg": Fraction(sum(ecc.values()), n),
        "dist_even_min": min(sum(1 for u in nodes if sp[v][u] % 2 == 0) for v in nodes),
        "dist_even_max": max(sum(1 for u in nodes if sp[v][u] % 2 == 0) for v in nodes),
        "Tdist_min": min(sum(sp[v].values()) for v in nodes),
        "Tdist_max": max(sum(sp[v].values()) for v in nodes),
        "dist_avg": Fraction(sum(sum(sp[v].values()) for v in nodes), n * (n - 1)),
        "disp_max": max(len({deg[u] for u in range(n) if adj[v] >> u & 1}) for v in range(n)),
        "disp_min": min(len({deg[u] for u in range(n) if adj[v] >> u & 1}) for v in range(n)),
        "disp_avg": Fraction(sum(len({deg[u] for u in range(n) if adj[v] >> u & 1})
                                 for v in range(n)), n),
        "cutv": sum(1 for v in nodes
                    if not nx.is_connected(G.subgraph([u for u in nodes if u != v]))),
        "tri": sum(nx.triangles(G).values()) // 3,
        "kappa": nx.node_connectivity(G),
        "chi_bip": 1 if nx.is_bipartite(G) else 0,
        "chi_reg": 1 if max(deg) == min(deg) else 0,
        "chi_tree": 1 if m == n - 1 else 0,
        "chi_C4free": 0 if any(len(set(G[u]) & set(G[w])) >= 2
                               for u, w in itertools.combinations(nodes, 2)) else 1,
    }
    out.update({k: v for k, v in simple.items() if k in needed})

    if want("res"):
        seq = sorted(deg, reverse=True)
        while seq and seq[0] > 0:
            d = seq[0]
            rest = seq[1:]
            for i in range(d):
                rest[i] -= 1
            seq = sorted(rest, reverse=True)
        out["res"] = len(seq)
    if want("annih"):
        pref, k = 0, 0
        for d in sorted(deg):
            pref += d
            if pref <= m:
                k += 1
            else:
                break
        out["annih"] = k
    if want("spec_floor", "spec_ceil"):
        A = nx.to_numpy_array(G, nodelist=nodes)
        l1 = float(np.max(np.linalg.eigvalsh(A)))
        r = round(l1)
        if abs(l1 - r) < 1e-9:
            out["spec_floor"] = out["spec_ceil"] = int(r)
        else:
            out["spec_floor"], out["spec_ceil"] = int(math.floor(l1)), int(math.ceil(l1))
    return out


def main():
    res = json.load(open(RESULT))
    ok = True
    checked = 0
    for t in res["results"]:
        if t["verdict"] != "CROSSED":
            continue
        cand = [w for w in t["refuting_graphs"]
                if w["n"] <= MAX_N
                and ("mu" not in t["invariants_used"] or w["m"] <= MAX_EDGES_FOR_MU)]
        if not cand:
            print("%-8s %-22s %s" % (t["id"], "-", "no witness inside the brute-force limit"))
            ok = False
            continue
        w = min(cand, key=lambda z: z["n"])
        G = nx.from_graph6_bytes(w["graph6"].encode())
        vals = brute(G, set(t["invariants_used"]))
        bad = {k: (v, str(vals[k])) for k, v in w["invariant_values"].items()
               if str(vals[k]) != v}
        checked += 1
        print("%-8s %-22s n=%-3d %s   %s"
              % (t["id"], w["graph"], w["n"], "agree" if not bad else "DISAGREE",
                 ", ".join("%s=%s" % (k, v) for k, v in sorted(
                     w["invariant_values"].items()))))
        if bad:
            print("    recorded vs brute force:", bad)
            ok = False
    print("third-path brute-force check on %d witnesses: %s"
          % (checked, "ALL AGREE" if ok else "DISAGREEMENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
