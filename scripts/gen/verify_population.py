"""Independent re-verification of the frozen population against `D`.

The generator's sweep works in scaled int64 with numpy.  This script re-derives
every claim in ``population.json`` through a completely different code path:

  * invariants recomputed from the graphs (not read from the generator's cache),
  * the statements evaluated from their JSON ASTs with `fractions.Fraction`
    arithmetic by ``expressions.evaluate`` (no scaling, no integer division),

and checks, for every target:

  1. zero counterexamples over all of `D`;
  2. the recorded ``min_slack_over_D`` and ``max_slack_over_D``;
  3. the recorded ``equality_count_in_D`` and ``equality_by_order_n``;
  4. that every recorded graph6 witness really attains equality;
  5. that the recorded relation string renders from the recorded AST.

A second pass re-checks a deterministic sample with the ``scal`` invariant
backend, so the NP-hard invariants are also confirmed by unrelated algorithms.

This script reads only `D`.  It evaluates nothing on any graph outside `D`.

Usage:
    python3 scripts/gen/verify_population.py
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from fractions import Fraction

import expressions as E
import graph_db as DB
import invariants as I

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment", "fresh-population", "population.json")
SEED = 20260815


def main() -> int:
    pop = json.load(open(POP))
    targets = pop["targets"]
    D = DB.load()
    codes = [DB.g6(G) for G in D]
    by_code = {c: i for i, c in enumerate(codes)}
    print("population: %d targets;  |D| = %d" % (len(targets), len(D)))

    bad = []
    minsl = [None] * len(targets)
    maxsl = [None] * len(targets)
    eqcnt = [0] * len(targets)
    eqbyn = [dict() for _ in targets]
    t0 = time.time()
    for gi, G in enumerate(D):
        vals = I.compute(G, "brute")
        n = G.number_of_nodes()
        for ti, t in enumerate(targets):
            s = E.slack(t["expr"], vals)
            if s < 0:
                bad.append((t["id"], codes[gi], str(s)))
            if minsl[ti] is None or s < minsl[ti]:
                minsl[ti] = s
            if maxsl[ti] is None or s > maxsl[ti]:
                maxsl[ti] = s
            if s == 0:
                eqcnt[ti] += 1
                eqbyn[ti][str(n)] = eqbyn[ti].get(str(n), 0) + 1
        if (gi + 1) % 3000 == 0:
            print("  ... %d/%d  %.0fs" % (gi + 1, len(D), time.time() - t0), flush=True)

    problems = []
    if bad:
        problems.append("COUNTEREXAMPLES IN D: %s" % bad[:10])
    for ti, t in enumerate(targets):
        if str(minsl[ti]) != t["min_slack_over_D"]:
            problems.append("%s min slack %s != %s" % (t["id"], minsl[ti], t["min_slack_over_D"]))
        if str(maxsl[ti]) != t["max_slack_over_D"]:
            problems.append("%s max slack %s != %s" % (t["id"], maxsl[ti], t["max_slack_over_D"]))
        if eqcnt[ti] != t["equality_count_in_D"]:
            problems.append("%s equality count %d != %d"
                            % (t["id"], eqcnt[ti], t["equality_count_in_D"]))
        if eqbyn[ti] != t["equality_by_order_n"]:
            problems.append("%s equality-by-n %s != %s"
                            % (t["id"], eqbyn[ti], t["equality_by_order_n"]))
        if E.render_relation(t["expr"]) != t["relation"]:
            problems.append("%s relation string does not render from its AST" % t["id"])
        for w in t["equality_witnesses_graph6"]:
            if w not in by_code:
                problems.append("%s witness %s is not in D" % (t["id"], w))
                continue
            v = I.compute(D[by_code[w]], "brute")
            if E.slack(t["expr"], v) != 0:
                problems.append("%s witness %s is not tight" % (t["id"], w))
        if t["counterexamples_in_D"] != 0:
            problems.append("%s claims a counterexample in D" % t["id"])

    print("full-D re-verification done in %.0fs" % (time.time() - t0))

    # second pass: independent invariant algorithms on a deterministic sample
    rng = random.Random(SEED)
    sample = sorted(rng.sample(range(len(D)), 300))
    mism = 0
    for gi in sample:
        a = I.compute(D[gi], "brute")
        b = I.compute(D[gi], "scal")
        for t in targets:
            if E.slack(t["expr"], a) != E.slack(t["expr"], b):
                mism += 1
                problems.append("%s slack differs between backends on %s" % (t["id"], codes[gi]))
    print("backend cross-check on %d graphs x %d targets: %d mismatches"
          % (len(sample), len(targets), mism))

    if problems:
        print("\nFAIL (%d problems):" % len(problems))
        for p in problems[:40]:
            print("  " + p)
        return 1
    print("\nPASS: all %d targets reproduce exactly on an independent code path."
          % len(targets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
