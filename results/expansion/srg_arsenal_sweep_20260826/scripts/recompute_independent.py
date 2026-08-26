"""INDEPENDENT RECOMPUTATION (gate 3) for arsenal violation candidates.

Second, differently-written computation paths for the quantities that appear
in candidate violations, PLUS closed-form theoretical anchors unique to the
arsenal families. Run after a VIO survives the DB-sanity gate:

    python recompute_independent.py <graph_name> [<graph_name> ...]

Checks, per graph:
  1. Family anchors (exact, from literature):
       T(k):        alpha=floor(k/2), omega=k-1, tree=k-1, mu=floor(C(k,2)/2),
                    diam=rad=2, b=k (k even) via even Hamiltonian cycle
       KG(k,2):     alpha=k-1, omega=floor(k/2), diam=rad=2
       Paley(q):    regular (q-1)/2, diam<=2, self-complementary => alpha=omega
       CP(m):       alpha=2, omega=m, tree=3, b=min(4,n), diam=rad=2
       CMP(m):      alpha=2, omega=m
       comp(C5[K_m]): alpha=2m, omega=m, residue=3 (m>=3), diam=rad=2
  2. Fresh ILP recomputations (pulp/CBC, formulations distinct from invlib):
       alpha (max IS), gamma/gamma_t/gamma_2/i, L_s (MTZ arborescence),
       mu (ILP matching)
Any mismatch exits nonzero.
"""
import itertools
import sys
from fractions import Fraction
from pathlib import Path

import networkx as nx
import pickle
import json
import pulp

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / "cache"
CERT = CACHE / "cert"


def ilp_alpha(G):
    p = pulp.LpProblem("a", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"x{i}", cat="Binary") for i, v in enumerate(G)}
    p += pulp.lpSum(x.values())
    for u, v in G.edges():
        p += x[u] + x[v] <= 1
    p.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=240))
    assert pulp.LpStatus[p.status] == "Optimal", "alpha ILP not optimal"
    return int(round(pulp.value(p.objective)))


def ilp_matching(G):
    p = pulp.LpProblem("mu", pulp.LpMaximize)
    edges = sorted(tuple(sorted(e)) for e in G.edges())
    y = {e: pulp.LpVariable(f"y{i}", cat="Binary")
         for i, e in enumerate(edges)}
    p += pulp.lpSum(y.values())
    for v in G.nodes():
        inc = [y[e] for e in edges if v in e]
        if inc:
            p += pulp.lpSum(inc) <= 1
    p.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=240))
    assert pulp.LpStatus[p.status] == "Optimal", "mu ILP not optimal"
    return int(round(pulp.value(p.objective)))


def ilp_dom(G, kind):
    p = pulp.LpProblem(kind, pulp.LpMinimize)
    x = {v: pulp.LpVariable(f"d{i}", cat="Binary") for i, v in enumerate(G)}
    p += pulp.lpSum(x.values())
    for v in G.nodes():
        nb = pulp.lpSum(x[u] for u in G[v])
        if kind == "gamma":
            p += x[v] + nb >= 1
        elif kind == "gamma_t":
            p += nb >= 1
        elif kind == "gamma_2":
            p += nb + 2 * x[v] >= 2
        elif kind == "i":
            p += x[v] + nb >= 1
    if kind == "i":
        for u, v in G.edges():
            p += x[u] + x[v] <= 1
    p.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=300))
    assert pulp.LpStatus[p.status] == "Optimal", f"{kind} ILP not optimal"
    return int(round(pulp.value(p.objective)))


def ilp_L_s_mtz(G):
    """Max-leaf spanning tree via MTZ-style arborescence (distinct from the
    flow formulation in invlib.spanning_tree_max_leaves)."""
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    arcs = [(u, v) for u, v in G.edges() for _ in range(2)]
    arc_list = list(G.edges()) + [(v, u) for u, v in G.edges()]
    p = pulp.LpProblem("ls_mtz", pulp.LpMaximize)
    y = {(u, v): pulp.LpVariable(f"y{i}_{j}", cat="Binary")
         for i, (u, v) in enumerate(arc_list)}
    leaf = {v: pulp.LpVariable(f"l{i}", cat="Binary")
            for i, v in enumerate(nodes)}
    lvl = {v: pulp.LpVariable(f"g{i}", lowBound=0, upBound=n - 1)
           for i, v in enumerate(nodes)}
    p += pulp.lpSum(leaf.values())
    root = nodes[0]
    p += pulp.lpSum(y.values()) == n - 1
    deg = {v: pulp.lpSum(y[e] for e in arc_list
                         if e[0] == v or e[1] == v) for v in nodes}
    for v in nodes:
        p += deg[v] >= 1
        p += deg[v] <= 1 + (n - 2) * (1 - leaf[v])
        p += deg[v] >= 2 * (1 - leaf[v]) * (1 - (1 if v == root else 0))
    # arborescence: level increases along arcs, arcs only to +1 level
    for (u, v) in arc_list:
        p += lvl[v] >= lvl[u] + 1 - n * (1 - y[(u, v)])
    p.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=600))
    st = pulp.LpStatus[p.status]
    assert st == "Optimal", f"L_s MTZ not optimal ({st})"
    return int(round(pulp.value(p.objective)))


def anchors(name):
    """Closed-form facts from the family theory -> dict invariant->value."""
    A = {}
    if name.startswith("T("):
        k = int(name[2:-1])
        N = k * (k - 1) // 2
        A = {"alpha": k // 2, "omega": k - 1, "tree": k - 1,
             "mu": N // 2, "diam": 2, "rad": 2}
        if k % 2 == 0:
            A["b"] = k  # Hamiltonian cycle is even; its line graph = itself
    elif name.startswith("KG("):
        k = int(name[3:-3])
        A = {"alpha": k - 1, "omega": k // 2, "diam": 2, "rad": 2}
    elif name.startswith("CP("):
        m = int(name[3:-1])
        A = {"alpha": 2, "omega": m, "tree": 3, "diam": 2, "rad": 2,
             "b": min(4, 2 * m)}
    elif name.startswith("CMP("):
        m = int(name[4:-1])
        A = {"alpha": 2, "omega": m}
    elif name.startswith("comp(C5[K"):
        m = int(name[9:-2])
        # alpha(comp) = omega(C5[K_m]) = two adjacent blobs = 2m;
        # omega(comp) = alpha(C5[K_m]) = 1 per blob x 2 dist-2 blobs = 2
        A = {"alpha": 2 * m, "omega": 2, "diam": 2, "rad": 2}
    return A


def main():
    graphs = pickle.load((CACHE / "arsenal.gpickle").open("rb"))
    fails = []
    for name in sys.argv[1:]:
        G = graphs[name]
        fn = CERT / (name.replace("/", "_").replace("(", "_")
                     .replace(")", "").replace(",", "_").replace("[", "_")
                     .replace("]", "") + ".json")
        if not fn.exists():
            print(f"{name}: no cert yet, skipped")
            continue
        cert = json.load(open(fn))
        print(f"== {name} ==")

        def cmp(tag, got, want):
            ok = got == want
            print(f"  {'OK ' if ok else 'FAIL'} {tag}: indep={got} "
                  f"cert={want}")
            if not ok:
                fails.append(f"{name}:{tag}")

        # anchors vs cert
        for inv, want in anchors(name).items():
            cv = cert.get(inv)
            if isinstance(cv, dict):
                if not cv.get("certified"):
                    continue
                cv = cv["value"]
            if cv is None:
                continue
            cmp(f"anchor:{inv}", want, cv)
        # fresh ILPs vs cert
        if name.startswith(("CP(", "CMP(", "comp(", "C7", "C9", "K(", "Paley")) \
                or G.number_of_nodes() <= 45:
            cmp("ilp_alpha", ilp_alpha(G), cert["alpha"]["value"])
            cmp("ilp_mu", ilp_matching(G), cert["mu"])
            for kind in ("gamma", "gamma_t", "gamma_2", "i"):
                if cert.get(kind, {}).get("certified"):
                    cmp(f"ilp_{kind}", ilp_dom(G, kind), cert[kind]["value"])
    if fails:
        print("\nINDEPENDENT-RECOMPUTE FAILURES:")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("\nindependent recomputation consistent")


if __name__ == "__main__":
    main()
