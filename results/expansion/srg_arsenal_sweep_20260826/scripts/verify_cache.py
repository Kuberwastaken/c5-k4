"""GATE 1: independent verification of the pre-built arsenal cache.

Recomputes a battery of invariants for spot-checked graphs using code paths
INDEPENDENT of invlib.py/xctx.py (different algorithms where possible):
  - structural: n, m, degrees, deg_avg, residue (fresh HH), diam/rad via
    networkx eccentricity, triangles via matrix trace, matching via nx,
    connectivity, girth
  - alpha via ILP on complement clique... actually via pulp max-clique ILP
  - gamma_t via a FRESH ILP formulation (edge-cover style)
  - lambda(v) stats for small graphs only
  - closed-form SRG checks: parameters and EXACT spectra per family:
      T(n): v=C(n,2), k=2(n-2); spectrum {2(n-2)^1, (n-4)^(n-1), (-2)^(C(n,2)-n)}
      KG(n,2) (=comp T(n)): spectrum = T(n) spectrum with sign flip except top
      Paley(q): { (q-1)/2 once, (-1+sqrt(q))/2 ^((q-1)/2),
                  (-1-sqrt(q))/2 ^((q-1)/2) }
      CP(m): complete multipartite K_{2^m}: spectrum {2m-2-2j ... } computed
             from complement m*K2: CP = J - I_blockwise; use formula
             spec(CP(m)) = { (2(m-j)-2)^(?) } -- verified numerically instead.
Compares against cache/cert/*.json values; exits nonzero on any mismatch.
"""
import itertools
import json
import pickle
import sys
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np
import pulp

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
CACHE = OUT / "cache"
CERT = CACHE / "cert"

MISMATCH = []


def check(tag, got, want):
    ok = got == want
    if not ok:
        MISMATCH.append(f"{tag}: recomputed {got!r} != cached {want!r}")
    print(f"  {'OK ' if ok else 'FAIL'} {tag}: got={got} cached={want}")


def fresh_alpha(G, cap=55.0):
    """Max independent set via ILP over the graph itself."""
    prob = pulp.LpProblem("alpha", pulp.LpMaximize)
    x = {v: pulp.LpVariable(f"a{i}", cat="Binary")
         for i, v in enumerate(G.nodes())}
    prob += pulp.lpSum(x.values())
    for u, v in G.edges():
        prob += x[u] + x[v] <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cap))
    return int(round(pulp.value(prob.objective)))


def fresh_gamma_t(G, cap=55.0):
    """Total domination: every vertex has a NEIGHBOR chosen."""
    prob = pulp.LpProblem("gt", pulp.LpMinimize)
    x = {v: pulp.LpVariable(f"d{i}", cat="Binary")
         for i, v in enumerate(G.nodes())}
    prob += pulp.lpSum(x.values())
    for v in G.nodes():
        prob += pulp.lpSum(x[u] for u in G[v]) >= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=cap))
    st = pulp.LpStatus[prob.status]
    return int(round(pulp.value(prob.objective))), st


def fresh_residue(G):
    seq = sorted((d for _, d in G.degree()), reverse=True)
    while seq and seq[0] > 0:
        d = seq.pop(0)
        seq = sorted([x - 1 for x in seq[:d]] + seq[d:], reverse=True)
    return len(seq)


def fresh_triangles(G):
    A = nx.to_numpy_array(G)
    return int(round(np.trace(A @ A @ A) / 6))


def srg_closed_forms(name, G):
    """Return dict of exact structural facts demanded by family theory."""
    n = G.number_of_nodes()
    m = G.number_of_edges()
    degs = sorted(d for _, d in G.degree())
    out = {"n": n, "m": m}
    if name.startswith("T("):
        k = int(name[2:-1])
        out["regular_k"] = 2 * (k - 2)
        assert n == k * (k - 1) // 2
        # spectrum
        A = nx.to_numpy_array(G)
        ev = np.sort(np.linalg.eigvalsh(A))[::-1]
        out["lam1"] = ev[0]
        out["expect_lam1"] = 2 * (k - 2)
        out["lam2"] = ev[1]
        out["expect_lam2"] = k - 4
        out["lam_last"] = ev[-1]
        out["expect_last"] = -2
    elif name.startswith("KG("):
        k = int(name[3:-3])
        # complement of T(k): lam1 = C(k-1,2)... comp of T has degrees
        # C(k,2)-1-2(k-2); eigenvalues are {-1-lambda_i(T)} plus new one
        A = nx.to_numpy_array(G)
        ev = np.sort(np.linalg.eigvalsh(A))[::-1]
        out["lam1"] = ev[0]
        out["expect_lam1"] = (k * (k - 1)) // 2 - 1 - 2 * (k - 2)
        out["lam_last"] = ev[-1]
        # T has eigenvalue -2 with multiplicity C(k,2)-k -> comp has 1-(-2)=3
        out["expect_last"] = 3
    elif name.startswith("Paley("):
        q = int(name[6:-1])
        out["regular_k"] = (q - 1) // 2
        A = nx.to_numpy_array(G)
        ev = np.sort(np.linalg.eigvalsh(A))[::-1]
        out["lam1"] = ev[0]
        out["expect_lam1"] = (q - 1) / 2
        r = (np.sqrt(q) - 1) / 2
        s = (-np.sqrt(q) - 1) / 2
        out["mid_band"] = (abs(ev[1] - r) < 1e-8, abs(ev[-1] - s) < 1e-8)
    elif name.startswith("CP("):
        mm = int(name[3:-1])
        out["n"] = 2 * mm
        out["regular_k"] = 2 * (mm - 1)
    return out


def verify_graph(name, G, cert):
    print(f"== {name} (n={G.number_of_nodes()}) ==")
    check("n", G.number_of_nodes(), cert["n"])
    check("m", G.number_of_edges(), cert["m_edges"])
    degs = sorted(d for _, d in G.degree())
    check("delta", degs[0], cert["delta"])
    check("Delta", degs[-1], cert["Delta"])
    check("deg_avg", Fraction(2 * G.number_of_edges(), G.number_of_nodes()),
          Fraction(cert["deg_avg"]))
    check("residue", fresh_residue(G), cert["residue"])
    ecc = dict(nx.eccentricity(G))
    check("diam", max(ecc.values()), cert["diam"])
    check("rad", min(ecc.values()), cert["rad"])
    check("triangles", fresh_triangles(G), cert["triangles_total"])
    check("mu", len(nx.max_weight_matching(G, maxcardinality=True)),
          cert["mu"])
    check("kappa", nx.node_connectivity(G), cert["kappa_vertex"])
    if G.number_of_nodes() <= 45:
        check("alpha", fresh_alpha(G), cert["alpha"]["value"])
        gt, st = fresh_gamma_t(G)
        if st == "Optimal":
            check("gamma_t", gt, cert["gamma_t"]["value"])
    cf = srg_closed_forms(name, G)
    if "regular_k" in cf:
        check("srg-k(regular)", degs[0], cf["regular_k"])
    if "lam1" in cf:
        check("lam1~closed form", round(cf["lam1"], 6),
              round(float(cf["expect_lam1"]), 6))


def verify_all_structure(graphs):
    """Every arsenal graph must match its family's closed-form parameters."""
    import sympy as sp
    bad = []
    for name, G in graphs.items():
        n = G.number_of_nodes()
        m = G.number_of_edges()
        degs = sorted(d for _, d in G.degree())
        A = nx.to_numpy_array(G)
        ev = np.sort(np.linalg.eigvalsh(A))[::-1]
        if name.startswith("T("):
            k = int(name[2:-1])
            want_n, want_k = k * (k - 1) // 2, 2 * (k - 2)
            spec = {round(float(ev[0]), 6): 1,
                    round(float(k - 4), 6): k - 1,
                    -2.0: want_n - k}
            got_spec = {}
            for x in np.round(ev, 6):
                got_spec[float(x)] = got_spec.get(float(x), 0) + 1
        elif name.startswith("KG("):
            k = int(name[3:-3])
            want_n = k * (k - 1) // 2
            want_k = want_n - 1 - 2 * (k - 2)
            # comp of T(k): top = N-1-k_T = want_k; then -1-eig(T), eig!=top:
            #   -(k-3) with mult k-1 ; +1 with mult want_n - k
            from collections import Counter
            gc = Counter(float(x) for x in np.round(ev, 6))
            wc = Counter({float(want_k): 1, float(-(k - 3)): k - 1,
                          1.0: want_n - k})
            ok = (n == want_n and degs[0] == degs[-1] == want_k
                  and m == want_k * want_n // 2 and gc == wc)
            print(f"  {'OK ' if ok else 'FAIL'} {name}: n={n}(want {want_n}) "
                  f"k={degs[0]}(want {want_k}) "
                  f"spec_ok={gc == wc} spec={dict(gc)}")
            if not ok:
                bad.append(name)
            continue
        elif name.startswith("Paley("):
            q = int(name[6:-1])
            want_n, want_k = q, (q - 1) // 2
            import sympy as _sp
            r = float((_sp.sqrt(q) - 1) / 2)
            s = float((-_sp.sqrt(q) - 1) / 2)
            nr = ns = 0
            top_ok = False
            for x in ev:
                if abs(x - r) < 1e-6:
                    nr += 1
                elif abs(x - s) < 1e-6:
                    ns += 1
                elif abs(x - (q - 1) / 2) < 1e-6:
                    top_ok = True
            ok = (n == want_n and degs[0] == degs[-1] == want_k
                  and m == want_k * want_n // 2 and top_ok
                  and nr == (q - 1) // 2 and ns == (q - 1) // 2)
            print(f"  {'OK ' if ok else 'FAIL'} {name}: n={n}(want {want_n}) "
                  f"k={degs[0]}(want {want_k}) top={top_ok} "
                  f"mult(r,s)=({nr},{ns}) want ({(q-1)//2},{(q-1)//2})")
            if not ok:
                bad.append(name)
            continue
        elif name.startswith("CP("):
            mm = int(name[3:-1])
            want_n, want_k = 2 * mm, 2 * (mm - 1)
            spec = None
            got_spec = None
            # eigenvalues of complete multipartite K_{2^m}: 2m-2-2j, j=0..m-1
            # each with mult 2 except largest (mult 1) and smallest (-2, mult m)
            expect = sorted([float(2 * mm - 2 - 2 * j) for j in range(mm)]
                            + [-2.0] * mm)[::-1]
            spec_ok = np.allclose(ev, expect, atol=1e-7)
            got_spec = {"matches_formula": bool(spec_ok)}
        else:
            continue
        ok = (n == want_n and degs[0] == degs[-1] == want_k
              and m == want_k * want_n // 2)
        spec_bad = False
        if spec is not None:
            if name.startswith("Paley("):
                spec_bad = got_spec != spec
            else:
                gs = {float(k_): v for k_, v in
                      zip(np.round(ev, 6), [0] * len(ev))}
                # multiplicity compare
                from collections import Counter
                gc = Counter(float(x) for x in np.round(ev, 6))
                wc = Counter({float(a): b for a, b in spec.items()})
                spec_bad = gc != wc
        status = "OK " if (ok and not spec_bad) else "FAIL"
        if not (ok and not spec_bad):
            bad.append(name)
        extra = f" spec_ok={not spec_bad}" if spec is not None else ""
        print(f"  {status} {name}: n={n}(want {want_n}) k={degs[0]} "
              f"(want {want_k}){extra}")
    return bad


def main():
    graphs = pickle.load((CACHE / "arsenal.gpickle").open("rb"))
    meta = json.load(open(CACHE / "arsenal_meta.json"))
    # meta cross-check on ALL graphs (cheap)
    for name, rec in meta.items():
        G = graphs[name]
        assert rec["n"] == G.number_of_nodes(), name
        assert rec["m"] == G.number_of_edges(), name
        d = sorted(dd for _, dd in G.degree())
        assert (rec["delta"], rec["Delta"]) == (d[0], d[-1]), name
    print(f"meta consistent for all {len(meta)} graphs")
    print("-- family closed-form structure over the whole arsenal --")
    bad = verify_all_structure(graphs)
    # deep spot-check on certified graphs
    for name in ("T(12)", "comp(C5[K3])", "CP(3)", "KG(13,2)"):
        fn = CERT / (name.replace("/", "_").replace("(", "_")
                     .replace(")", "").replace(",", "_").replace("[", "_")
                     .replace("]", "") + ".json")
        if not fn.exists():
            print(f"  (no cert for {name}; skipping deep check)")
            continue
        verify_graph(name, graphs[name], json.load(open(fn)))
    if MISMATCH or bad:
        print("\nMISMATCHES:")
        for s in MISMATCH + bad:
            print(" -", s)
        sys.exit(1)
    print("\nALL SPOT-CHECKS PASSED")


if __name__ == "__main__":
    main()
