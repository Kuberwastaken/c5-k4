"""Steps 3-4 of the wall-arm method: sign checks and family trials.

`sign_check(tid, members)` implements METHOD_V1_6 §A3 (G3-lite): evaluate the
proposed transformation on the two smallest members of the intended family and
report the sign of the change in the target residual.  A wrong or zero sign is
a stop -- the caller must not run the trial.

`trial(tid, members)` implements step 4 with the §A3.1 non-degeneracy guard:
every generated member is checked against the statement's own hypotheses
(simple, connected, n >= 2, no isolated/collapsed vertex) before its residual is
read.
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall_arm as W  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
_POP = json.load(open(POP))
BY_ID = {t["id"]: t for t in _POP["targets"]}


def residual(tid, g):
    """Signed residual R = slack; R < 0 is a crossing."""
    t = BY_ID[tid]
    vals = W.compute(g, only=W.target_invs(t) + ["n", "m"])
    return W.slack(t["expr"], vals), vals


def sign_check(tid, members, note=""):
    """G3-lite, METHOD §A3.  `members` = [(label, G), (label, G)] -- the two
    smallest members of the intended family, in increasing order."""
    t = BY_ID[tid]
    rows = []
    for (lab, g) in members:
        ok, why = W.nondegenerate(g)
        if not ok:
            rows.append((lab, g.n, None, "DEGENERATE: " + why))
            continue
        r, vals = residual(tid, g)
        rows.append((lab, g.n, r,
                     " ".join("%s=%s" % (k, vals[k]) for k in W.target_invs(t))))
    print("  G3-lite sign check [%s] %s" % (tid, note))
    for (lab, n, r, extra) in rows:
        print("    %-28s n=%-3s R=%-8s %s" % (lab, n, r, extra))
    rs = [r for (_, _, r, _) in rows if r is not None]
    if len(rs) < 2:
        print("    -> STOP (degenerate members)")
        return "STOP-degenerate", rows
    d = rs[1] - rs[0]
    verdict = "GO" if d < 0 else ("STOP-zero" if d == 0 else "STOP-wrong-sign")
    print("    dR = %s  -> %s" % (d, verdict))
    return verdict, rows


def trial(tid, members, cap_s=3600.0, quiet=False):
    """Run the family.  Returns (best_slack, crossings, log)."""
    t0 = time.time()
    best = None
    crossings = []
    log = []
    tt = BY_ID[tid]
    used = W.target_invs(tt)
    for (lab, g) in members:
        if time.time() - t0 > cap_s:
            log.append((lab, None, "BUDGET"))
            break
        ok, why = W.nondegenerate(g)
        if not ok:
            log.append((lab, None, "GUARD-REJECT:" + why))
            if not quiet:
                print("    %-30s n=%-3d GUARD-REJECT %s" % (lab, g.n, why))
            continue
        r, vals = residual(tid, g)
        log.append((lab, str(r), W.to_graph6(g) if g.n < 63 else ""))
        if best is None or r < best[0]:
            best = (r, lab, g)
        if r < 0:
            crossings.append((lab, r, g))
        if not quiet:
            print("    %-30s n=%-3d R=%-8s %s" % (
                lab, g.n, r,
                " ".join("%s=%s" % (k, vals[k]) for k in used)))
    return best, crossings, log
