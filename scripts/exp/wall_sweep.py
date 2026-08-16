"""Sign-check-first sweep of the wall transformations for one target.

For every (tight witness, transformation) pair:
  1. build members 1 and 2 only;
  2. record the G3-lite sign of dR (METHOD §A3);
  3. if the sign is wrong or zero -> STOP, the rest of the family is never built;
  4. otherwise extend the family and read residuals, under the A3.1 guard.

Usage:  python3 scripts/exp/wall_sweep.py FP-014 [--witness 4] [--cap 900]
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall_arm as W          # noqa: E402
import wall_families as F     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
_POP = json.load(open(POP))
BY_ID = {t["id"]: t for t in _POP["targets"]}


class TimeOut(Exception):
    pass


def _alarm(sig, frm):
    raise TimeOut()


signal.signal(signal.SIGALRM, _alarm)


def resid(t, g, per_graph_cap=60):
    signal.alarm(per_graph_cap)
    try:
        vals = W.compute(g, only=W.target_invs(t) + ["n"])
        r = W.slack(t["expr"], vals)
    finally:
        signal.alarm(0)
    return r, vals


def sweep(tid, witnesses=None, nwit=5, cap=900.0, maxn=46, verbose=True):
    t = BY_ID[tid]
    used = W.target_invs(t)
    ws = witnesses if witnesses is not None else t["equality_witnesses_graph6"][:nwit]
    t0 = time.time()
    records = []
    crossings = []
    for wc in ws:
        base = W.from_graph6(wc)
        for fname, fn in (
            ("clique_blowup", lambda b: F.fam_clique_blowup(b, (1, 2, 3, 4, 5))),
            ("indep_blowup", lambda b: F.fam_indep_blowup(b, (1, 2, 3, 4))),
            ("subdivision", lambda b: F.fam_subdivision(b, (0, 1, 2))),
            ("corona", lambda b: F.fam_corona(b, (0, 1, 2))),
            ("join_clique", lambda b: F.fam_join_clique(b, (0, 1, 2, 3))),
            ("join_indep", lambda b: F.fam_join_indep(b, (0, 1, 2, 3))),
            ("prism", lambda b: F.fam_prism(b, (1, 2, 3))),
            ("complement", lambda b: F.fam_complement(b)),
            ("line", lambda b: F.fam_line(b)),
        ):
            if time.time() - t0 > cap:
                records.append((wc, fname, "BUDGET", None, []))
                continue
            try:
                members = fn(base)
            except Exception as e:
                records.append((wc, fname, "BUILD-FAIL:%s" % e, None, []))
                continue
            # --- G3-lite sign check on the two smallest members ---
            two = members[:2]
            rs = []
            ok = True
            for (lab, g) in two:
                good, why = W.nondegenerate(g)
                if not good or g.n > maxn:
                    ok = False
                    break
                try:
                    r, _ = resid(t, g)
                except TimeOut:
                    ok = False
                    break
                rs.append(r)
            if not ok or len(rs) < 2:
                records.append((wc, fname, "SIGNCHECK-UNAVAILABLE", None, []))
                if verbose:
                    print("  %-9s %-15s sign check unavailable" % (wc, fname))
                continue
            d = rs[1] - rs[0]
            sgn = "GO" if d < 0 else ("STOP-zero" if d == 0 else "STOP-wrong-sign")
            if verbose:
                print("  %-9s %-15s R1=%-6s R2=%-6s dR=%-6s %s"
                      % (wc, fname, rs[0], rs[1], d, sgn))
            if sgn != "GO":
                records.append((wc, fname, sgn, [str(x) for x in rs], []))
                continue
            # --- trial ---
            trail = []
            for (lab, g) in members:
                if time.time() - t0 > cap:
                    trail.append((lab, "BUDGET"))
                    break
                good, why = W.nondegenerate(g)
                if not good:
                    trail.append((lab, "GUARD:" + why))
                    continue
                if g.n > maxn:
                    trail.append((lab, "MAXN"))
                    continue
                try:
                    r, vals = resid(t, g)
                except TimeOut:
                    trail.append((lab, "TIMEOUT"))
                    continue
                trail.append((lab, str(r)))
                if verbose:
                    print("      %-16s n=%-3d R=%-8s %s" % (
                        lab, g.n, r, " ".join("%s=%s" % (k, vals[k]) for k in used)))
                if r < 0:
                    crossings.append((wc, fname, lab, str(r), W.to_graph6(g)))
                    if verbose:
                        print("      *** CROSSING *** %s" % W.to_graph6(g))
            records.append((wc, fname, "GO", [str(x) for x in rs], trail))
    return records, crossings, time.time() - t0


if __name__ == "__main__":
    tid = sys.argv[1]
    cap = 900.0
    nwit = 5
    if "--cap" in sys.argv:
        cap = float(sys.argv[sys.argv.index("--cap") + 1])
    if "--nwit" in sys.argv:
        nwit = int(sys.argv[sys.argv.index("--nwit") + 1])
    print("== %s  %s" % (tid, BY_ID[tid]["relation"]))
    recs, cross, el = sweep(tid, nwit=nwit, cap=cap)
    print("elapsed %.1fs  crossings: %d" % (el, len(cross)))
    for c in cross:
        print("  ", c)
