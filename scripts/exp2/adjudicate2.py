"""Adjudicator for experiment v2 (the hereditary-vocabulary three-arm test).

PREREGISTRATION ORDER (binding): this file is committed BEFORE any v2 arm
writes a verdict.  It implements the decision rule of
results/experiment-v2/DESIGN.md exactly as frozen, plus the v1.7 repairs:

  * R3 -- the generic arm is a valid control only if it returns HELD or
    CROSSED (not BRACKET) on >= 75% of scored targets; the bracket count is
    reported next to the endpoint either way.
  * the endpoint and rule are unchanged from v1:
      SUPPORTED    iff wall-unique >= 3  AND  wall-unique >= catalogue total
      FALSIFIED    iff wall-unique <= catalogue-unique
      INCONCLUSIVE otherwise; <20 scored targets is its own inconclusive.
      No-valid-control iff generic brackets > 25% of targets -- reported as a
      failed run, not a result in either direction.

What it does, in order:
 1. Loads each arm file results/experiment-v2/arm-<name>.json (schema identical
    to v1: [{id, verdict, witness_graph6, ...}, ...]).
 2. Re-evaluates every claimed CROSSED witness with ONE common evaluator --
    backend B invariants + the population's own AST in Fraction arithmetic.
    Backend A is what the generator swept at freeze time, so backend B here is
    an independent path (METHOD v1.7 R4 discipline).
 3. Database-sanity gate on every confirmed crossing's READING: the reading is
    re-swept over all of D2 with backend A's cached matrix.  A reading that
    refutes any member of D2 contradicts the population's own freeze record
    and voids the crossing as a bug.
 4. Computes the endpoints and applies the decision rule mechanically.

Usage:
    python3 adjudicate2.py            # needs all three arm files
    python3 adjudicate2.py --partial  # report on whatever exists so far
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.join(HERE, "..", "gen2") not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "gen2")))
sys.path.insert(0, HERE)

from common_eval2 import EXP2, evaluate_target_on_graph, load_targets  # noqa: E402


def load_arm(name):
    p = os.path.join(EXP2, "arm-%s.json" % name)
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        d = json.load(fh)
    rows = d if isinstance(d, list) else d.get("results", d.get("targets", []))
    return {r["id"]: r for r in rows}


def _eval_vec(expr, env):
    """Vectorised exact evaluation of a population AST over SCALE-unit int64
    columns (one column per member of D2).  Mirrors expressions2.evaluate but
    whole-database at once; ceil/floor of negatives use floor division exactly
    as expressions2 does via math.floor/math.ceil on Fractions."""
    import expressions2 as E
    S = E.SCALE
    if "inv" in expr:
        return env[expr["inv"]]
    if "const" in expr:
        return np.full(_N, expr["const"] * S, dtype=np.int64)
    op = expr["op"]
    if op == "add":
        out = _eval_vec(expr["args"][0], env)
        for a in expr["args"][1:]:
            out = out + _eval_vec(a, env)
        return out
    if op == "sub":
        return _eval_vec(expr["args"][0], env) - _eval_vec(expr["args"][1], env)
    if op == "mul":
        return expr["c"] * _eval_vec(expr["arg"], env)
    if op == "ceil_div":
        return E._cd(_eval_vec(expr["arg"], env), expr["d"])
    if op == "floor_div":
        return E._fd(_eval_vec(expr["arg"], env), expr["d"])
    if op == "ceil_ratio":
        return E._cr(_eval_vec(expr["num"], env), _eval_vec(expr["den"], env))
    if op == "floor_ratio":
        return E._fr(_eval_vec(expr["num"], env), _eval_vec(expr["den"], env))
    raise ValueError(op)


_N = 0


def db_sanity(target):
    """Zero-counterexample re-check of one reading over ALL of D2.

    Uses backend A's cached exact matrix (the generator's own freeze-time data,
    sha-recorded in population.json) with a fresh vectorised evaluator written
    for this adjudicator.  Returns the graph6 strings of any counterexample."""
    import graph_db2 as DB
    import invariants2 as I
    import common_eval2 as CE
    from invmatrix import load

    global _N
    M = load("A")
    codes = DB.load_codes()
    assert M.shape[0] == len(codes)
    names = sorted(CE.target_invariants(target))
    cols = {nm: M[:, I.VOCAB.index(nm)] for nm in names}
    _N = M.shape[0]
    env = {nm: cols[nm] for nm in names}
    lhs = _eval_vec(target["expr"]["lhs"], env)
    rhs = _eval_vec(target["expr"]["rhs"], env)
    if target["expr"]["rel"] == "<=":
        bad_idx = np.nonzero(lhs > rhs)[0]
    else:
        bad_idx = np.nonzero(lhs < rhs)[0]
    return [codes[i] for i in bad_idx[:5]], int(bad_idx.size)


def main():
    partial = "--partial" in sys.argv
    targets = load_targets()
    arms = {n: load_arm(n) for n in ("catalogue", "generic", "wall")}
    missing = [n for n, a in arms.items() if a is None]
    if missing and not partial:
        print("arm files missing: %s -- use --partial to adjudicate anyway"
              % missing, file=sys.stderr)
        return 2

    confirmed = {n: set() for n in arms}
    rejected = {n: [] for n in arms}

    for arm_name, arm in arms.items():
        if arm is None:
            continue
        for tid, row in arm.items():
            if row.get("verdict") != "CROSSED":
                continue
            g6 = row.get("witness_graph6") or row.get("graph6")
            if not g6:
                rejected[arm_name].append((tid, "no witness graph6"))
                continue
            try:
                holds, lhs, rhs = evaluate_target_on_graph(targets[tid], g6,
                                                           backend="B")
            except Exception as exc:  # noqa: BLE001
                rejected[arm_name].append((tid, "re-eval failed: %r" % exc))
                continue
            if holds:
                rejected[arm_name].append(
                    (tid, "does NOT refute under common evaluator: %s vs %s"
                     % (lhs, rhs)))
                continue
            try:
                bad, nbad = db_sanity(targets[tid])
            except Exception as exc:  # noqa: BLE001
                rejected[arm_name].append((tid, "db-gate failed to run: %r" % exc))
                continue
            if nbad:
                rejected[arm_name].append(
                    (tid, "reading refutes %d members of D2 (%s...) -- bug, not "
                          "a crossing" % (nbad, bad[:2])))
            else:
                confirmed[arm_name].add(tid)

    scored = set()
    for arm in arms.values():
        if arm:
            scored |= {t for t, r in arm.items()
                       if r.get("verdict") in ("CROSSED", "HELD")}
    brackets = {}
    for n, arm in arms.items():
        if arm:
            brackets[n] = sum(1 for r in arm.values()
                              if r.get("verdict") == "BRACKET")

    wall_unique = confirmed["wall"] - confirmed["catalogue"] - confirmed["generic"]
    cat_unique = confirmed["catalogue"] - confirmed["wall"] - confirmed["generic"]

    print("=== adjudicated (common evaluator, backend B) ===")
    for n in arms:
        print("  %-10s confirmed=%2d  rejected=%d  brackets=%d"
              % (n, len(confirmed[n]), len(rejected[n]), brackets.get(n, "-")))
        for tid, why in rejected[n]:
            print("      REJECTED %s: %s" % (tid, why))
    print("\nscored targets: %d" % len(scored))
    print("wall-unique crossings:      %d %s"
          % (len(wall_unique), sorted(wall_unique)))
    print("catalogue-unique crossings: %d %s"
          % (len(cat_unique), sorted(cat_unique)))
    print("catalogue total crossings:  %d" % len(confirmed["catalogue"]))
    gb = brackets.get("generic", 0)
    print("generic bracket share: %.1f%% (valid control requires <= 25%% and "
          ">=75%% HELD/CROSSED)" % (100.0 * gb / max(1, len(arms["generic"] or {}))))

    verdict = None
    if len(scored) < 20:
        verdict = "INCONCLUSIVE (fewer than 20 scored targets)"
    elif gb * 4 > len(arms["generic"] or {}):
        verdict = "NO VALID CONTROL (R3): generic arm brackets >25% of targets"
    elif len(wall_unique) >= 3 and len(wall_unique) >= len(confirmed["catalogue"]):
        verdict = "H1-v2 SUPPORTED"
    elif len(wall_unique) <= len(cat_unique):
        verdict = "H1-v2 FALSIFIED"
    else:
        verdict = "INCONCLUSIVE"
    print("\nPREREGISTERED VERDICT: %s" % verdict)

    out = {
        "adjudicated_at_commit": None,  # filled by the run wrapper
        "confirmed": {n: sorted(v) for n, v in confirmed.items()},
        "rejected": {n: [(t, w) for t, w in rejected[n]] for n in rejected},
        "scored_targets": len(scored),
        "brackets_by_arm": brackets,
        "endpoints": {
            "wall_unique": sorted(wall_unique),
            "catalogue_unique": sorted(cat_unique),
            "catalogue_total": len(confirmed["catalogue"]),
        },
        "verdict": verdict,
    }
    with open(os.path.join(EXP2, "ADJUDICATION.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
