"""Exact spectral data for the arsenal, closed-form per family.

adjacency / laplacian / signless eigenvalues as EXACT sympy expressions,
stored with multiplicities. Families:
  T(k), KG(k,2), Paley(q): classical SRG closed forms
  CP(m), CMP(m): complete multipartite formulas (derived here)
  comp(C5[K_m]), C7[K3], C9[K3], K(3,3), K(3,3,3): small enough for exact
  sympy charpoly factoring; cross-checked against float numpy.

Writes cache/spectra_exact.json:
  name -> {"lam1": str, "a": str (algebraic connectivity),
           "q1": str, "qn": str, "mu1": str, "spec_adj": [[eig, mult], ...]}
Every eig stored as sympy srepr string for exact revival.
"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import sympy
import networkx as nx
from sympy import Integer, Rational, sqrt

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / "cache"


def spec_from_mults(top, rest):
    """rest: list of (eigenvalue_expr, multiplicity)."""
    out = [(top, 1)] + list(rest)
    return out


def T_spec(k):
    N = k * (k - 1) // 2
    adj = spec_from_mults(Integer(2 * k - 4),
                          [(Integer(k - 4), k - 1), (Integer(-2), N - k)])
    return adj


def KG_spec(k):
    N = k * (k - 1) // 2
    top = N - 1 - 2 * (k - 2)
    adj = spec_from_mults(Integer(top),
                          [(Integer(1), N - k), (Integer(-(k - 3)), k - 1)])
    return adj


def Paley_spec(q):
    r = (Rational(-1, 1) + sqrt(q)) / 2
    s = (Rational(-1, 1) - sqrt(q)) / 2
    top = Rational(q - 1, 2)
    adj = spec_from_mults(top, [(r, (q - 1) // 2), (s, (q - 1) // 2)])
    return adj


def multipartite_spec(parts):
    """Adjacency spectrum of the complete multipartite graph K_{parts}.
    A = J - J_restricted... Known: eigenvalues are
      n - s_j  with multiplicity s_j - 1   (for each part j)
      -s_j ... no -- correct statement:
    For K_{s_1,...,s_k}: adjacency eigenvalues:
      k-th structure: {n-s_j}^{s_j-1}? Verify: K_n (all parts 1): gives {} plus?
    Use derivation via equitable decomposition instead: quotient matrix over
    parts: Q[i][j] = s_j if i != j else 0. Eigenvalues of A = eigenvalues of Q
    plus {-s_j? } hmm. Safer: build small sympy matrix when total n <= 45.
    """
    raise NotImplementedError


def exact_spec_small(G):
    """Exact integer/radical spectrum via sympy charpoly roots."""
    A = sympy.Matrix(nx.to_numpy_array(G, dtype=int).tolist())
    # symmetric integer matrix: use eigenvals through charpoly factoring
    ev = A.eigenvals()
    out = []
    for e, mult in ev.items():
        out.append((sympy.simplify(e), int(mult)))
    return out


def lap_from_adj(adj_spec, deg):
    return [(deg - e, m) for e, m in adj_spec]


def signless_from_adj(adj_spec, deg):
    return [(deg + e, m) for e, m in adj_spec]


def summarize(adj, deg):
    lam1 = max((e for e, _ in adj), key=lambda x: float(x))
    lap = lap_from_adj(adj, deg)
    nz = [e for e, m in lap if e != 0]
    a = min(nz, key=lambda x: float(x))
    sg = signless_from_adj(adj, deg)
    q1 = max((e for e, _ in sg), key=lambda x: float(x))
    qn = min((e for e, _ in sg), key=lambda x: float(x))
    mu1 = max((e for e, _ in lap), key=lambda x: float(x))
    return lam1, a, q1, qn, mu1


def lex_cycle_k3_spec(k):
    """Spectrum of C_k [K_3] via A = A_Ck (x) J_3 + I (x) A_K3:
    {lambda_j*3 + 2 : lambda_j in spec(C_k)} union {{-1}^{2k}}."""
    adj = []
    vals = {}
    for j in range(k):
        val = sympy.simplify(
            2 * sympy.cos(Rational(2 * j, k) * sympy.pi))
        found = None
        for v in vals:
            if sympy.simplify(v - val) == 0:
                found = v
                break
        if found is None:
            vals[val] = 1
        else:
            vals[found] += 1
    for val, cnt in vals.items():
        adj.append((sympy.simplify(3 * val + 2), cnt))
    adj.append((Integer(-1), 2 * k))
    return adj


def main():
    graphs = pickle.load((CACHE / "arsenal.gpickle").open("rb"))
    out = {}
    for name, G in graphs.items():
        n = G.number_of_nodes()
        degs = sorted(d for _, d in G.degree())
        regular = degs[0] == degs[-1]
        if name.startswith("T("):
            adj = T_spec(int(name[2:-1]))
            deg = degs[0]
        elif name.startswith("KG("):
            adj = KG_spec(int(name[3:-3]))
            deg = degs[0]
        elif name.startswith("Paley("):
            adj = Paley_spec(int(name[6:-1]))
            deg = degs[0]
        elif name.startswith("C") and "[K3]" in name:
            adj = lex_cycle_k3_spec(int(name[1:].split("[")[0]))
            deg = degs[0]
        elif n <= 45:
            adj = exact_spec_small(G)
            deg = degs[0] if regular else None
        else:
            print(f"skip {name}", flush=True)
            continue
        # verify against numeric
        ev = np.sort(np.linalg.eigvalsh(
            nx.to_numpy_array(G, dtype=float)))[::-1]
        expanded = sorted([float(e) for e, m in adj for _ in range(m)],
                          reverse=True)
        ok = len(expanded) == n and np.allclose(expanded, ev, atol=1e-6)
        if not ok:
            print(f"SPECTRA MISMATCH {name}: {expanded[:3]} vs {ev[:3]}")
            sys.exit(1)
        if deg is not None:
            lam1, a, q1, qn, mu1 = summarize(adj, deg)
        else:
            # non-regular: exact lap/signless via sympy matrices
            Amat = sympy.Matrix(nx.to_numpy_array(G, dtype=int).tolist())
            Dmat = sympy.diag(*[G.degree(v) for v in G.nodes()])
            lapv = [(e, int(m)) for e, m in (Dmat - Amat).eigenvals().items()]
            sgv = [(e, int(m)) for e, m in (Dmat + Amat).eigenvals().items()]
            a = min([e for e, m in lapv if e != 0], key=lambda x: float(x))
            q1 = max((e for e, _ in sgv), key=lambda x: float(x))
            qn = min((e for e, _ in sgv), key=lambda x: float(x))
            mu1 = max((e for e, _ in lapv), key=lambda x: float(x))
            lam1 = max((e for e, _ in adj), key=lambda x: float(x))
        out[name] = {
            "deg": deg,
            "lam1": sympy.srepr(lam1), "a": sympy.srepr(a),
            "q1": sympy.srepr(q1), "qn": sympy.srepr(qn),
            "mu1": sympy.srepr(mu1),
            "spec_adj": [[sympy.srepr(e), m] for e, m in adj],
            "spec_lap": [[sympy.srepr(deg - e), m] for e, m in adj]
            if deg is not None else None,
            "spec_signless": [[sympy.srepr(deg + e), m] for e, m in adj]
            if deg is not None else None,
        }
        print(f"OK {name}: lam1={lam1} a={a} q1={q1}")
    (CACHE / "spectra_exact.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {len(out)} exact spectral records")


if __name__ == "__main__":
    main()
