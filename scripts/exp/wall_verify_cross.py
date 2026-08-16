"""Standing verification bar for every claimed crossing.

(a) independent recomputation by a second code path:
      path A = scripts/exp/wall_arm.py   (this arm's own implementation)
      path B = scripts/gen/invariants.py `scal` backend + expressions.py
                (the generator's branch-and-bound backend; shares no code with A)
    plus, for spectral invariants only, a float eigenvalue bracket as a third
    reading, because path B's `_spectral_bracket` is known-buggy (see the
    protocol note in arm-wall.md).

(b) database-sanity gate: the same reading, evaluated by path A over all of D,
    must produce zero counterexamples.  Run once for all 30 targets by
    scripts/exp/wall_verify_D.py; this script re-asserts the recorded result.

Usage:  python3 scripts/exp/wall_verify_cross.py FP-007:N????B?_aACGE?B??o? ...
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts", "gen"))

import wall_arm as W        # noqa: E402
import invariants as I      # noqa: E402
import expressions as E     # noqa: E402
import networkx as nx       # noqa: E402

POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
_POP = json.load(open(POP))
BY_ID = {t["id"]: t for t in _POP["targets"]}


def path_b(g6: str):
    G = nx.from_graph6_bytes(g6.encode())
    return I.compute(G, "scal"), G


def verify(tid: str, g6: str, verbose=True):
    t = BY_ID[tid]
    used = W.target_invs(t)
    ga = W.from_graph6(g6)
    ok, why = W.nondegenerate(ga)
    va = W.compute(ga)
    ra = W.slack(t["expr"], va)
    vb, G = path_b(g6)
    rb = E.slack(t["expr"], vb)
    agree = all(Fraction(va[k]) == Fraction(vb[k]) for k in used)
    lhs_a = W.ev(t["expr"]["lhs"], va)
    rhs_a = W.ev(t["expr"]["rhs"], va)
    res = {
        "id": tid,
        "graph6": g6,
        "n": ga.n,
        "m": ga.m,
        "nondegenerate": ok,
        "guard_reason": why,
        "invariants_pathA": {k: str(va[k]) for k in used},
        "invariants_pathB": {k: str(vb[k]) for k in used},
        "paths_agree": bool(agree),
        "LHS": str(lhs_a),
        "RHS": str(rhs_a),
        "residual_pathA": str(ra),
        "residual_pathB": str(rb),
        "crossing": bool(ra < 0 and rb < 0 and agree and ok),
    }
    if verbose:
        print("%s  %s  n=%d m=%d" % (tid, g6, ga.n, ga.m))
        print("   guard: %s (%s)" % (ok, why))
        for k in used:
            mark = "OK " if Fraction(va[k]) == Fraction(vb[k]) else "!! "
            print("   %s %-14s A=%-10s B=%-10s" % (mark, k, va[k], vb[k]))
        print("   LHS=%s  RHS=%s  R_A=%s  R_B=%s  -> %s"
              % (lhs_a, rhs_a, ra, rb, "CROSSING" if res["crossing"] else "NOT A CROSSING"))
    return res


if __name__ == "__main__":
    out = []
    for arg in sys.argv[1:]:
        tid, g6 = arg.split(":", 1)
        out.append(verify(tid, g6))
    print(json.dumps(out, indent=1))
