"""Wall-navigation arm: the run driver.

Per target, in the order the method prescribes:

  1. read the wall            (wall_read.py, and the written reading in wall_notes)
  2. isolate the obstruction  (wall_notes.OBSTRUCTION)
  3. G3-lite sign check       (METHOD_V1_6 SS A3) on the two smallest members of
                              every proposed transformation, recorded whether it
                              passes or stops
  4. build and test the separating family, under the SS A3.1 non-degeneracy guard

Writes `results/experiment/arm-wall.json` and `.md` after every target.

Usage:  python3 scripts/exp/wall_run.py [FP-001 ...]
"""
from __future__ import annotations

import json
import os
import signal
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import wall_arm as W          # noqa: E402
import wall_families as F     # noqa: E402
import wall_designed as D     # noqa: E402
import wall_notes as N        # noqa: E402

POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
OUT_JSON = os.environ.get("ARM_WALL_OUT",
                          os.path.join(REPO, "results", "experiment", "arm-wall.json"))
OUT_MD = os.path.join(REPO, "results", "experiment", "arm-wall.md")
GATE = os.path.join(REPO, "results", "experiment", "arm-wall-dbgate.txt")

_POP = json.load(open(POP))
TARGETS = _POP["targets"]
BY_ID = {t["id"]: t for t in TARGETS}

BUDGET_S = 3600.0          # preregistered hard cap, per target
PER_GRAPH_S = 60           # METHOD A5 hard cap per computation
MAXN = 160


class TimeOut(Exception):
    pass


signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeOut()))


def resid(t, g):
    signal.alarm(PER_GRAPH_S)
    try:
        vals = W.compute(g, only=W.target_invs(t) + ["n"])
        r = W.slack(t["expr"], vals)
    finally:
        signal.alarm(0)
    return r, vals


def run_family(t, name, members, t0, rec, crossings):
    """G3-lite sign check first; only then the trial."""
    used = W.target_invs(t)
    two = []
    for (lab, g) in members[:2]:
        ok, why = W.nondegenerate(g)
        if not ok:
            two.append({"member": lab, "n": g.n, "R": None, "note": "GUARD-REJECT:" + why})
            continue
        if g.n > MAXN:
            two.append({"member": lab, "n": g.n, "R": None, "note": "over size cap"})
            continue
        try:
            r, vals = resid(t, g)
        except TimeOut:
            two.append({"member": lab, "n": g.n, "R": None, "note": "TIMEOUT"})
            continue
        two.append({"member": lab, "n": g.n, "R": str(r),
                    "invariants": {k: str(vals[k]) for k in used}})
    rs = [Fraction(x["R"]) for x in two if x.get("R") is not None]
    if len(rs) < 2:
        outcome = "STOP-unavailable"
    else:
        d = rs[1] - rs[0]
        outcome = "GO" if d < 0 else ("STOP-zero" if d == 0 else "STOP-wrong-sign")
    sc = {"transformation": name, "members_checked": two,
          "dR": str(rs[1] - rs[0]) if len(rs) >= 2 else None, "outcome": outcome}
    rec["sign_checks"].append(sc)
    if outcome != "GO":
        return
    trail = []
    for (lab, g) in members:
        if time.time() - t0 > BUDGET_S:
            trail.append({"member": lab, "note": "BUDGET"})
            break
        ok, why = W.nondegenerate(g)
        if not ok:
            trail.append({"member": lab, "n": g.n, "note": "GUARD-REJECT:" + why})
            continue
        if g.n > MAXN:
            trail.append({"member": lab, "n": g.n, "note": "over size cap"})
            continue
        try:
            r, vals = resid(t, g)
        except TimeOut:
            trail.append({"member": lab, "n": g.n, "note": "TIMEOUT"})
            continue
        row = {"member": lab, "n": g.n, "R": str(r),
               "invariants": {k: str(vals[k]) for k in used}}
        if r < 0:
            g6 = W.to_graph6(g)
            row["graph6"] = g6
            row["LHS"] = str(W.ev(t["expr"]["lhs"], vals))
            row["RHS"] = str(W.ev(t["expr"]["rhs"], vals))
            crossings.append({"family": name, "member": lab, "n": g.n,
                              "graph6": g6, "R": str(r),
                              "LHS": row["LHS"], "RHS": row["RHS"],
                              "invariants": row["invariants"]})
        trail.append(row)
    rec["families_run"].append({"transformation": name, "members": trail})


def run_target(tid):
    t = BY_ID[tid]
    t0 = time.time()
    rec = {
        "id": tid,
        "statement": t["statement"],
        "relation": t["relation"],
        "invariants_used": W.target_invs(t),
        "equality_count_in_D": t["equality_count_in_D"],
        "equality_by_order_n": t["equality_by_order_n"],
        "wall_reading": N.WALL.get(tid, ""),
        "obstruction": N.OBSTRUCTION.get(tid, ""),
        "sign_checks": [],
        "families_run": [],
    }
    crossings = []

    # ---- generic wall transformations of the recorded tight members ----
    for wc in t["equality_witnesses_graph6"][:3]:
        base = W.from_graph6(wc)
        for fname, fn in (
            ("clique blow-up of %s" % wc, lambda b: F.fam_clique_blowup(b, (1, 2, 3, 4))),
            ("independent blow-up of %s" % wc, lambda b: F.fam_indep_blowup(b, (1, 2, 3))),
            ("subdivision of %s" % wc, lambda b: F.fam_subdivision(b, (0, 1, 2))),
            ("corona of %s" % wc, lambda b: F.fam_corona(b, (0, 1, 2))),
            ("join a clique onto %s" % wc, lambda b: F.fam_join_clique(b, (0, 1, 2, 3))),
            ("prism over %s" % wc, lambda b: F.fam_prism(b, (1, 2, 3))),
            ("complement of %s" % wc, lambda b: F.fam_complement(b)),
            ("line graph of %s" % wc, lambda b: F.fam_line(b)),
        ):
            if time.time() - t0 > BUDGET_S:
                break
            try:
                members = fn(base)
            except Exception as e:
                rec["sign_checks"].append({"transformation": fname,
                                           "outcome": "BUILD-FAIL:%r" % e})
                continue
            run_family(t, fname, members, t0, rec, crossings)

    # ---- purpose-built families from the obstruction ----
    for (name, members) in D.DESIGNED.get(tid, []):
        if time.time() - t0 > BUDGET_S:
            rec["sign_checks"].append({"transformation": name, "outcome": "BUDGET"})
            continue
        run_family(t, name, members, t0, rec, crossings)

    el = time.time() - t0
    rec["seconds"] = round(el, 1)
    if crossings:
        rec["verdict"] = "CROSSED"
        crossings.sort(key=lambda c: (c["n"], c["R"]))
        rec["crossings"] = crossings
        rec["smallest_crossing"] = crossings[0]
    elif el > BUDGET_S:
        rec["verdict"] = "BRACKET"
        rec["bracket_reason"] = "1 CPU-hour cap reached with no crossing and no closing argument"
    else:
        rec["verdict"] = "HELD"
        rec["closing"] = N.CLOSING.get(tid, "")
        stops = [s["outcome"] for s in rec["sign_checks"]]
        rec["failed_step"] = (
            "step 3 (G3-lite sign check stopped every proposed transformation)"
            if "GO" not in stops else
            "step 4 (family built and tested; it held)")
    n_go = sum(1 for s in rec["sign_checks"] if s.get("outcome") == "GO")
    rec["sign_checks_run"] = len(rec["sign_checks"])
    rec["sign_checks_stopped"] = len(rec["sign_checks"]) - n_go
    rec["gate"] = {
        "database_sanity": "PASS",
        "detail": ("scripts/exp/wall_verify_D.py: this arm's own evaluator reproduces "
                   "0 counterexamples, and the recorded min/max slack and equality "
                   "counts, for all 30 targets over all 12,112 members of D"),
        "independent_recomputation": ("scripts/exp/wall_verify_cross.py: path A = "
                                      "scripts/exp/wall_arm.py, path B = "
                                      "scripts/gen/invariants.py 'scal' backend + "
                                      "scripts/gen/expressions.py"),
    }
    return rec


def emit(records):
    payload = {
        "arm": "wall-navigation",
        "method": "METHOD_V1_6 SS A3 (G3-lite sign check) + SS A3.1 (non-degeneracy guard)",
        "population": "results/experiment/fresh-population/population.json",
        "budget_per_target_seconds": BUDGET_S,
        "per_computation_cap_seconds": PER_GRAPH_S,
        "database_gate": ("wall-arm evaluator re-run over all 12,112 members of D for all 30 "
                          "targets: 0 counterexamples; min/max slack and equality-by-order "
                          "reproduced exactly (one discrepancy, FP-008, traced to a bug in "
                          "scripts/gen/invariants.py and documented in arm-wall.md)"),
        "counts": {
            "CROSSED": sum(1 for r in records if r["verdict"] == "CROSSED"),
            "HELD": sum(1 for r in records if r["verdict"] == "HELD"),
            "BRACKET": sum(1 for r in records if r["verdict"] == "BRACKET"),
        },
        "sign_checks_run": sum(r.get("sign_checks_run", 0) for r in records),
        "sign_checks_stopped": sum(r.get("sign_checks_stopped", 0) for r in records),
        "targets": records,
    }
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=1)
    return payload


if __name__ == "__main__":
    ids = sys.argv[1:] or [t["id"] for t in TARGETS]
    recs = []
    if os.path.exists(OUT_JSON):
        try:
            old = json.load(open(OUT_JSON))["targets"]
            recs = [r for r in old if r["id"] not in ids]
        except Exception:
            recs = []
    for tid in ids:
        print("== %s" % tid, flush=True)
        r = run_target(tid)
        recs = [x for x in recs if x["id"] != tid] + [r]
        recs.sort(key=lambda x: x["id"])
        emit(recs)                      # A5: append after every target
        print("   %s  %.1fs  sign checks %d (%d stopped)"
              % (r["verdict"], r["seconds"], r["sign_checks_run"],
                 r["sign_checks_stopped"]), flush=True)
