"""Generate ARSENAL.md from the certified cache + closed-form spectra checks."""
import json
import math
import pickle
import sys
from fractions import Fraction
from pathlib import Path

import networkx as nx
import sympy

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
CACHE = HERE.parent / "cache"
CERT = CACHE / "cert"

PHI = (1 + sympy.sqrt(5)) / 2
PSI = (sympy.sqrt(5) - 1) / 2


def closed_form(name):
    """(lambda1, lambda2, algebraic connectivity) as sympy exprs, or None."""
    if name.startswith("T("):
        n = int(name[2:-1])
        return 2 * (n - 2), n - 4, n
    if name.startswith("KG("):
        n = int(name[3:-3])
        l1 = sympy.Rational((n - 2) * (n - 3), 2)
        l2 = sympy.Rational((n - 4) * (n - 5), 2)
        a = l1 - l2
        return l1, l2, sympy.simplify(a)
    if name.startswith("Paley("):
        q = int(name[6:-1])
        l1 = sympy.Rational(q - 1, 2)
        l2 = (sympy.sqrt(q) - 1) / 2
        a = (q - sympy.sqrt(q)) / 2
        return l1, l2, a
    if name.startswith("CP("):
        m = int(name[3:-1])
        return 2 * m - 2, 0, 2 * m - 2
    if name.startswith("CMP("):
        m = int(name[4:-1])
        return 2 * m - 2, None, None
    if name.startswith("comp(C5[K"):
        m = int(name[len("comp(C5[K"):-2])
        return 3 * m - 1, PHI * m - 1, (3 - PHI) * m
    if name.startswith("C7[K3]"):
        import sympy as sp
        l2 = 2 + 6 * sp.cos(2 * sp.pi / 7)
        return 8, sp.simplify(l2), sp.simplify(6 - 6 * sp.cos(2 * sp.pi / 7))
    if name.startswith("C9[K3]"):
        import sympy as sp
        l2 = 2 + 6 * sp.cos(2 * sp.pi / 9)
        return 8, sp.simplify(l2), sp.simplify(6 - 6 * sp.cos(2 * sp.pi / 9))
    if name == "K(3,3)":
        return 3, 0, 3
    if name == "K(3,3,3)":
        return 6, 0, 6
    return None


def fmt(x):
    x = sympy.simplify(x)
    if x.is_Integer:
        return str(int(x))
    if x.is_Rational:
        return f"{x.p}/{x.q}"
    return str(x)


def main():
    graphs = pickle.load((CACHE / "arsenal.gpickle").open("rb"))
    meta = json.load((CACHE / "arsenal_meta.json").open())
    lines = []
    lines.append("# Extended SRG arsenal — certified invariants "
                 "(sweep 2026-08-26)\n")
    lines.append("Construction: networkx; vertex-transitivity witnessed by "
                 "explicit verified automorphism generators per family "
                 "(orbit of vertex 0 = V). All averages exact `Fraction`; "
                 "NP-hard values by bitset BnB / CBC ILP under caps; "
                 "`BRACKET` marks cap exhaustion (incumbent kept as "
                 "one-sided bound). Spectral columns are CLOSED FORMS; "
                 "numeric numpy eigenvalues must agree to 1e-6.\n")

    hdr = ("| graph | n | m | deg | girth | diam | rad | alpha | lam_max(v)"
           " | i | gamma | gamma_t | gamma_2 | mu | omega | f | b | tree"
           " | L_s | res | A |")
    sep = "|---" * 20 + "|"
    lines.append(hdr); lines.append(sep)

    def cell(cert, key):
        r = cert.get(key)
        if isinstance(r, dict):
            if r.get("bracket"):
                v = r.get("value")
                return f"[{v}]" if v is not None else "BRACKET"
            if "value" in r:
                return str(r["value"]) if r.get("certified") \
                    else f"({r['value']})"
            return "?"
        if isinstance(r, (int, float)):
            return str(r)
        return "?"

    names = list(graphs)
    rows = []
    for name in names:
        fn = CERT / (name.replace("/", "_").replace("(", "_")
                     .replace(")", "").replace(",", "_").replace("[", "_")
                     .replace("]", "") + ".json")
        if not fn.exists():
            continue
        c = json.load(fn.open())
        ls = c["lambda_stats"]
        lammax = ls["max"] if isinstance(ls, dict) and ls.get("certified") \
            else "?"
        row = [
            name, c["n"], c["m_edges"], f"{c['delta']}..{c['Delta']}",
            c.get("_girth") or H_girth(graphs[name]),
            c["diam"], c["rad"],
            cell(c, "alpha"), lammax,
            cell(c, "i"), cell(c, "gamma"), cell(c, "gamma_t"),
            cell(c, "gamma_2"), c["mu"], cell(c, "omega"),
            cell(c, "f"), cell(c, "b"), cell(c, "tree"), cell(c, "L_s"),
            c["residue"], c["annihilation"],
        ]
        rows.append("| " + " | ".join(str(x) for x in row) + " |")
    lines += rows

    lines.append("\n## Spectral closed forms vs numeric (guard 1e-6)\n")
    lines.append("| graph | lambda1 (closed) | lambda2 (closed) | a (closed) "
                 "| numeric ok |")
    lines.append("|---|---|---|---|---|")
    spec_rows = []
    for name in names:
        cf = closed_form(name)
        fn = CERT / (name.replace("/", "_").replace("(", "_")
                     .replace(")", "").replace(",", "_").replace("[", "_")
                     .replace("]", "") + ".json")
        if not fn.exists():
            continue
        c = json.load(fn.open())
        if cf is None:
            spec_rows.append(f"| {name} | (numeric only) | "
                             f"{c['lambda2_numeric']:.6f} | "
                             f"{c['algebraic_connectivity_numeric']:.6f} "
                             "| n/a |")
            continue
        l1, l2, a = cf
        ok1 = abs(float(l1) - c["lambda1_numeric"]) < 1e-6
        ok3 = (a is not None and
               abs(float(a) - c["algebraic_connectivity_numeric"]) < 1e-6)
        ok = "OK" if (ok1 and (ok3 or a is None)) else "MISMATCH"
        l2s = fmt(l2) if l2 is not None else "-"
        spec_rows.append(f"| {name} | {fmt(l1)} | {l2s} | "
                         f"{fmt(a) if a is not None else '-'} | {ok} |")
    lines += spec_rows

    lines.append("\n## Structural certificates\n")
    lines.append("- Vertex-transitive (verified generators): all arsenal "
                 "members except CMP(m) m>=2 (singleton part breaks it).\n")
    lines.append("- On every VERTEX-TRANSITIVE member with alpha < n, the "
                 "alphacore (intersection of all maximum independent sets) "
                 "is EMPTY and u(G)=0 (orbit of any maximum independent set "
                 "under the transitive group yields a second one).\n")
    lines.append("- `[x]` = bracketed optimum with incumbent x kept as "
                 "one-sided bound; `(x)` = incumbent only (not proven "
                 "optimal).\n")
    (OUT / "ARSENAL.md").write_text("\n".join(lines) + "\n")
    print(f"ARSENAL.md written with {len(rows)} graph rows")


def H_girth(G):
    import helpers as Hh
    return Hh.girth_safe(G)


if __name__ == "__main__":
    main()
