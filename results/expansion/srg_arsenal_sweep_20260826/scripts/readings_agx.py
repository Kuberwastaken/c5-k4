"""Readings for OPEN AutoGraphiX entries against the arsenal.

Exact lhs/rhs closures; spectral values from cache/spectra_exact.json
(closed forms); structural values from the certified battery.
Every reading carries an explicit comparison direction:
  dir=">="  claim: lhs >= rhs ;  dir="<=" claim: lhs <= rhs.
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import sympy
from sympy import Integer, Rational

from xctx import Undef

HERE = Path(__file__).resolve().parent
SPEC = json.load(open(HERE.parent / "cache" / "spectra_exact.json"))


def _ev(s):
    return sympy.sympify(s)


_SP_FRESH_CACHE = {}


def _sp_fresh(name):
    """Numeric spectra for non-arsenal (sanity-corpus) graphs, computed on
    the fly (numpy; margins are far above float noise)."""
    if name in _SP_FRESH_CACHE:
        return _SP_FRESH_CACHE[name]
    import networkx as nx
    from sanity_corpus_graphs import get_graph
    G = get_graph(name)
    A = nx.to_numpy_array(G, dtype=float)
    ev = sorted(np.linalg.eigvalsh(A).tolist(), reverse=True)
    degs = sorted(d for _, d in G.degree())
    adj = [(float(v), 1) for v in ev]
    if degs[0] == degs[0]:
        pass
    Dm = np.diag([float(d) for _, d in G.degree()])
    lapv = sorted(np.linalg.eigvalsh(Dm - A).tolist(), reverse=True)
    sgv = sorted(np.linalg.eigvalsh(Dm + A).tolist(), reverse=True)
    a = min([x for x in lapv if abs(x) > 1e-9])
    out = {"lam1": ev[0], "a": a,
           "q1": sgv[0], "qn": sgv[-1], "mu1": lapv[0],
           "adj": adj, "lap": [(x, 1) for x in lapv],
           "signless": [(x, 1) for x in sgv]}
    _SP_FRESH_CACHE[name] = out
    return out


def sp(name):
    if name not in SPEC:
        return _sp_fresh(name)
    rec = SPEC[name]
    out = {}
    for k in ("lam1", "a", "q1", "qn", "mu1"):
        out[k] = _ev(rec[k])
    for key in ("spec_adj", "spec_lap", "spec_signless"):
        if rec.get(key):
            lst = sorted([(_ev(e), m) for e, m in rec[key]],
                         key=lambda t: -float(t[0]))
            out[key.replace("spec_", "")] = lst
    return out


def R(interp, lhs=None, rhs=None, dir_=">=", premise=None, confidence="high"):
    return {"interp": interp, "lhs": lhs, "rhs": rhs, "premise": premise,
            "dir": dir_, "confidence": confidence}


def _frac(x):
    if isinstance(x, Fraction):
        return Rational(x.numerator, x.denominator)
    return x


def agx_t(n):
    """unique root in (0,1) of t^3+(2n-3)t^2+(n^2-3n+1)t-1=0."""
    x = sympy.Symbol("x")
    poly = x**3 + (2 * n - 3) * x**2 + (n**2 - 3 * n + 1) * x - 1
    roots = sympy.nroots(poly, n=40)
    real = [sympy.re(r) for r in roots
            if abs(sympy.im(r)) < 1e-20 and 0 < float(sympy.re(r)) < 1]
    if len(real) != 1:
        raise Undef(f"C8 t-root not isolated: {roots}")
    return real[0]


def build_C8(X):
    s = sp(X.name)
    n, lam1 = X.n, s["lam1"]
    t = agx_t(n)

    def nu():
        return X.kappa()

    def ke():
        return X.edge_connectivity()
    return [
        R(f"C8a: lam1 - nu <= n - 3 + t (t=t({n}))",
          lambda: lam1 - nu(), lambda: n - 3 + t, dir_="<="),
        R("C8b: lam1 - kappa <= n - 3 + t",
          lambda: lam1 - ke(), lambda: n - 3 + t, dir_="<="),
        R("C8c: lam1/nu <= n - 2 + t",
          lambda: lam1 / nu(), lambda: n - 2 + t, dir_="<="),
        R("C8d: lam1/kappa <= n - 2 + t",
          lambda: lam1 / ke(), lambda: n - 2 + t, dir_="<="),
    ]


def build_C11(X):
    """lambda1 + lambda2 <= n - c - f(n) per n mod 3 class (garbled OCR).

    Faithful reconstruction attempt (survey C11): bound = n - 4/3 - f1(n)
    when n=1 mod 3, n - 5/3?? ... Only the f-expressions are legible:
    f1=(3n-2-sqrt(9n^2-12n+12))/6, f2=(3n-1-sqrt(9n^2-6n+9))/6.
    We encode BOTH candidate groupings per class; gates will filter.
    """
    s = sp(X.name)
    n = X.n
    lam1 = s["lam1"]
    lam2 = s["adj"][1][0]
    f1 = (3 * n - 2 - sympy.sqrt(9 * n**2 - 12 * n + 12)) / 6
    f2 = (3 * n - 1 - sympy.sqrt(9 * n**2 - 6 * n + 9)) / 6
    cls = n % 3
    outs = []
    if cls == 1:
        b = f1
    elif cls == 0:
        b = f2
    else:
        b = Integer(0)
    outs.append(R(f"C11 r1: lam1+lam2 <= n - 4/3 - b(n) [class {cls}]",
                  lambda: lam1 + lam2,
                  lambda: n - Rational(4, 3) - b, dir_="<="))
    outs.append(R(f"C11 r2: lam1+lam2 <= n - b(n) [class {cls}]",
                  lambda: lam1 + lam2, lambda: n - b, dir_="<="))
    return outs


def build_C15(X):
    s = sp(X.name)
    lam2 = s["adj"][1][0]
    om = X.omega()
    m = X.m_edges
    out = [R("C15odd: |lambda2|*omega <= m - 2",
             lambda: abs(lam2) * om, lambda: m - 2, dir_="<=")]
    if X.n % 2 == 0:
        # extremal graph: two K_{n/2} linked by one edge; compare values
        def extremal_val():
            k = X.n // 2
            import networkx as nx
            Gx = nx.disjoint_union(nx.complete_graph(k),
                                   nx.complete_graph(k))
            Gx.add_edge(0, k)
            Amat = sympy.Matrix(nx.to_numpy_array(Gx, dtype=int).tolist())
            evs = sorted([float(v) for v in Amat.eigenvals().values()
                          for _ in range(1)], reverse=True)
            ev_all = sorted(np.linalg.eigvalsh(
                nx.to_numpy_array(Gx, dtype=float)).tolist(), reverse=True)
            lam2e = ev_all[1]
            me = Gx.number_of_edges()
            omee = k + 1  # clique spanning both halves minus... actually k+1
            return abs(lam2e) * omee - me
        out.append(R("C15even: |lambda2|*omega - m <= value at "
                     "extremal graph (two linked K_{n/2})",
                     lambda: abs(lam2) * om - m,
                     lambda: ("ub", extremal_val()), dir_="<="))
    return out


def build_C17(X):
    raise Undef("requires G(n,p,q) construction; not evaluable on arsenal")


def build_C29(X):
    raise Undef("extremal characterization (kite minimum); no explicit "
                "bound value to test on a fixed graph")


def build_C30(X):
    s = sp(X.name)
    a = s["a"]
    tr = X.c["Tdist"]
    vals = [Fraction(tr[v], X.n - 1) for v in tr]
    pie = Fraction(min(vals))
    n = X.n
    if n % 2 == 1:
        bound = (3 * n + 1) / sympy.pi * \
            (1 - sympy.cos(sympy.pi / Rational(n, 2))) / 2
        interp = "C30odd: pi*a >= (3n+1)/pi*(1-cos(pi/n))/2"
    else:
        bound = (3 * n - 2) / sympy.pi * \
            (1 - sympy.cos(sympy.pi / n)) / 2
        interp = "C30even: pi*a >= (3n-2)/pi*(1-cos(pi/2n))/2"
    return [R(interp, lambda: Fraction(pie) * a, lambda: bound, dir_=">=")]


def build_C31(X):
    raise Undef("extremal characterization (kite/lollipop); no explicit "
                "bound value")


def build_C32(X):
    s = sp(X.name)
    return [R("C32: a*mu >= 1", lambda: s["a"] * X.mu(), lambda: 1,
              dir_=">=")]


def build_C33(X):
    s = sp(X.name)
    n, lam1 = X.n, s["lam1"]
    t = agx_t(n)
    return [R("C33a: a - lam1 >= 3 - n - t",
              lambda: s["a"] - lam1, lambda: 3 - n - t, dir_=">=")]


def build_C36(X):
    s = sp(X.name)
    q1, mu1, lam1 = s["q1"], s["mu1"], s["lam1"]
    n = X.n
    dbarS = _frac(X.deg_avg)
    return [
        R("C36a: q1 - 2*dbar <= n - 4 + 4/n",
          lambda: q1 - 2 * dbarS, lambda: n - 4 + Rational(4, n), dir_="<="),
        R("C36b: q1 - dbar <= n - 1",
          lambda: q1 - dbarS, lambda: n - 1, dir_="<="),
        R("C36d: q1 - mu1 <= n - 2",
          lambda: q1 - mu1, lambda: n - 2, dir_="<="),
    ]


def build_C37(X):
    s = sp(X.name)
    sg = s["signless"]
    q2 = sg[1][0]
    dbarS = _frac(X.deg_avg)
    delta, lam1, n = X.delta, s["lam1"], X.n
    Delta = X.Delta
    return [
        R("C37a: q2 - dbar >= -1", lambda: q2 - dbarS, lambda: -1,
          dir_=">="),
        R("C37b: q2 - dbar <= n - 6 + 8/n",
          lambda: q2 - dbarS, lambda: n - 6 + Rational(8, n), dir_="<="),
        R("C37c: q2 - delta >= -1", lambda: q2 - delta, lambda: -1,
          dir_=">="),
        R("C37d: q2 - delta <= n - 3", lambda: q2 - delta, lambda: n - 3,
          dir_="<="),
        R("C37e: Delta - q2 <= n - 2", lambda: Delta - q2, lambda: n - 2,
          dir_="<="),
        R("C37f: q2 - lam1 >= 1 - n - 1/n (page garble)",
          lambda: q2 - lam1, lambda: 1 - n - Rational(1, n), dir_=">="),
    ]


def build_C39(X):
    s = sp(X.name)
    return [R("C39 screen: q1 - qn >= 2*(1-cos(pi/n))",
              lambda: s["q1"] - s["qn"],
              lambda: 2 * (1 - sympy.cos(sympy.pi / X.n)), dir_=">=")]


def build_C40(X):
    s = sp(X.name)
    n = X.n
    return [R("C40: q1 + qn + 2*alpha <= 3n - 2",
              lambda: s["q1"] + s["qn"] + 2 * X.alpha(), lambda: 3 * n - 2,
              dir_="<=")]


def build_C42(X):
    def p_minus():
        dm = X.dm
        nodes = list(X.G.nodes())
        Dm = np.array([[dm[a][b] for b in nodes] for a in nodes],
                      dtype=float)
        ev = np.linalg.eigvalsh(Dm)
        tol = 1e-7
        near0 = int(sum(1 for e in ev if abs(e) <= tol))
        if near0:
            raise Undef(f"{near0} zero distance-eigenvalues; p- ambiguous")
        return int(sum(1 for e in ev if e < -tol))

    prem = None
    if X.t_total() != 0:
        prem = lambda: False
    return [R("C42i: m/alpha <= p-(D)",
              lambda: Fraction(X.m_edges, X.alpha()), lambda: p_minus(),
              dir_="<=", premise=prem),
            R("C42ii: m/alpha <= n - p-(D)",
              lambda: Fraction(X.m_edges, X.alpha()),
              lambda: X.n - p_minus(), dir_="<=", premise=prem)]


AGX_BUILDERS = {
    "agx-survey-C8": build_C8,
    "agx-survey-C11": build_C11,
    "agx-survey-C15": build_C15,
    "agx-survey-C30": build_C30,
    "agx-survey-C32": build_C32,
    "agx-survey-C33": build_C33,
    "agx-survey-C36": build_C36,
    "agx-survey-C37": build_C37,
    "agx-survey-C39": build_C39,
    "agx-survey-C40": build_C40,
    "agx-survey-C42": build_C42,
}
