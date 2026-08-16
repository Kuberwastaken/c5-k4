"""Database-sanity gate / calibration for the wall arm.

Runs the wall arm's OWN invariant code path (scripts/exp/wall_arm.py) over all
12,112 members of D and re-derives, for every one of the 30 frozen targets:
zero counterexamples, min/max slack, equality count, equality-by-order.

If this passes, the wall arm's evaluator agrees with the frozen population on
every graph the population was built from -- which is exactly the gate the
protocol requires before any claimed crossing outside D is believed.

Usage:  python3 scripts/exp/wall_verify_D.py [nproc]
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall_arm as W  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
DB = os.path.join(REPO, "scripts", "gen", "data", "connected_n2_n8.g6")

_POP = json.load(open(POP))
TARGETS = _POP["targets"]


def work(codes):
    out = []
    for c in codes:
        g = W.from_graph6(c)
        vals = W.compute(g)
        sl = [W.slack(t["expr"], vals) for t in TARGETS]
        out.append((c, g.n, sl))
    return out


def main():
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    codes = [ln.strip() for ln in open(DB) if ln.strip()]
    print("|D| = %d, %d targets" % (len(codes), len(TARGETS)), flush=True)
    chunks = [codes[i::nproc * 4] for i in range(nproc * 4)]
    t0 = time.time()
    with mp.Pool(nproc) as pool:
        res = pool.map(work, chunks)
    rows = [r for chunk in res for r in chunk]
    print("computed %d graphs in %.0fs" % (len(rows), time.time() - t0), flush=True)

    problems = []
    for ti, t in enumerate(TARGETS):
        mn = None
        mx = None
        eq = 0
        eqn = {}
        bad = []
        for (c, n, sl) in rows:
            s = sl[ti]
            if s < 0:
                bad.append((c, str(s)))
            if mn is None or s < mn:
                mn = s
            if mx is None or s > mx:
                mx = s
            if s == 0:
                eq += 1
                eqn[str(n)] = eqn.get(str(n), 0) + 1
        if bad:
            problems.append("%s: %d counterexamples IN D, e.g. %s" % (t["id"], len(bad), bad[:3]))
        if str(mn) != t["min_slack_over_D"]:
            problems.append("%s min slack %s != %s" % (t["id"], mn, t["min_slack_over_D"]))
        if str(mx) != t["max_slack_over_D"]:
            problems.append("%s max slack %s != %s" % (t["id"], mx, t["max_slack_over_D"]))
        if eq != t["equality_count_in_D"]:
            problems.append("%s eq count %d != %d" % (t["id"], eq, t["equality_count_in_D"]))
        if eqn != t["equality_by_order_n"]:
            problems.append("%s eq-by-n %s != %s" % (t["id"], eqn, t["equality_by_order_n"]))

    if problems:
        print("FAIL (%d):" % len(problems))
        for p in problems[:60]:
            print("  " + p)
        return 1
    print("PASS: wall-arm code path reproduces all 30 targets exactly over all of D.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
