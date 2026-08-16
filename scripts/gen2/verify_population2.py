"""Re-derive every claim in the frozen v2 `population.json` on an independent path.

The generator swept **backend A**'s invariant matrix in scaled `int64` numpy.
This verifier re-checks each frozen target using

  * **backend B**'s invariant values (networkx + branch and bound + the
    characteristic polynomial), which share no code with backend A, and
  * the JSON `expr` AST evaluated in exact `fractions.Fraction` arithmetic by
    `expressions2.evaluate`, not the numpy template functions,

over every member of `D2`.  For each target it re-checks: zero counterexamples,
the recorded min and max slack, the recorded equality count and its breakdown by
order, that every recorded graph6 witness really attains equality, and that the
`relation` string renders from the recorded AST.

Usage:
    python3 scripts/gen2/verify_population2.py
"""
from __future__ import annotations

import json
import multiprocessing as mp
import os
import sys
import time
from fractions import Fraction
from typing import Dict, List

import numpy as np

import expressions2 as E
import graph_db2 as DB
import invariants2 as I
import invmatrix

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
POP = os.path.join(REPO, "results", "experiment-v2", "population", "population.json")

_TARGETS: List[dict] = []
_NAMES: List[str] = []


def _init(targets, names):
    global _TARGETS, _NAMES
    _TARGETS = targets
    _NAMES = names


def _chunk(args):
    lo, rows = args
    out = []
    for r, row in enumerate(rows):
        vals = {k: Fraction(int(v), E.SCALE) for k, v in zip(_NAMES, row)}
        out.append([E.slack(t["expr"], vals) for t in _TARGETS])
    return lo, out


def main() -> int:
    with open(POP) as fh:
        pop = json.load(fh)
    targets = pop["targets"]
    codes = DB.load_codes()
    sizes = [ord(c[0]) - 63 for c in codes]
    assert pop["database"]["size"] == len(codes)
    assert pop["database"]["sha256_graph6_file"] == DB.sha256_db()
    print("population: %d targets; D2: %d graphs" % (len(targets), len(codes)), flush=True)

    MB = invmatrix.load("B", codes)
    names = list(I.VOCAB)

    for t in targets:
        want = t["relation"]
        got = E.render_relation(t["expr"])
        assert want == got, "%s: relation does not render from its AST: %r vs %r" % (
            t["id"], want, got)
    print("render: all %d relation strings reproduce from their ASTs" % len(targets))

    t0 = time.time()
    W = int(os.environ.get("GEN2_WORKERS", "6"))
    step = 4000
    jobs = [(lo, MB[lo:lo + step].tolist()) for lo in range(0, len(codes), step)]
    minsl = [None] * len(targets)
    maxsl = [None] * len(targets)
    neg = [0] * len(targets)
    eqn: List[Dict[int, int]] = [dict() for _ in targets]
    eqcodes: List[set] = [set() for _ in targets]
    done = 0
    with mp.Pool(W, initializer=_init, initargs=(targets, names)) as pool:
        for lo, block in pool.imap_unordered(_chunk, jobs):
            for r, slacks in enumerate(block):
                i = lo + r
                for j, s in enumerate(slacks):
                    if s < 0:
                        neg[j] += 1
                    if minsl[j] is None or s < minsl[j]:
                        minsl[j] = s
                    if maxsl[j] is None or s > maxsl[j]:
                        maxsl[j] = s
                    if s == 0:
                        eqn[j][sizes[i]] = eqn[j].get(sizes[i], 0) + 1
                        eqcodes[j].add(codes[i])
            done += len(block)
            if done % 40000 < step:
                print("    %d/%d  %.0fs" % (done, len(codes), time.time() - t0), flush=True)

    bad = 0
    for j, t in enumerate(targets):
        errs = []
        if neg[j] != 0:
            errs.append("%d counterexamples" % neg[j])
        if str(minsl[j]) != t["min_slack_over_D"]:
            errs.append("min slack %s != %s" % (minsl[j], t["min_slack_over_D"]))
        if str(maxsl[j]) != t["max_slack_over_D"]:
            errs.append("max slack %s != %s" % (maxsl[j], t["max_slack_over_D"]))
        tot = sum(eqn[j].values())
        if tot != t["equality_count_in_D"]:
            errs.append("equality count %d != %d" % (tot, t["equality_count_in_D"]))
        rec = {int(k): v for k, v in t["equality_by_order_n"].items()}
        if rec != eqn[j]:
            errs.append("equality-by-order %s != %s" % (eqn[j], rec))
        missing = [c for c in t["equality_witnesses_graph6"] if c not in eqcodes[j]]
        if missing:
            errs.append("%d recorded witnesses are not tight (e.g. %s)"
                        % (len(missing), missing[:3]))
        if errs:
            bad += 1
            print("FAIL %s: %s" % (t["id"], "; ".join(errs)))
    print("full-D2 re-verification done in %.0fs" % (time.time() - t0))
    if bad:
        print("FAIL: %d of %d targets do not reproduce" % (bad, len(targets)))
        return 1
    print("PASS: all %d targets reproduce exactly on an independent code path "
          "(backend B values, Fraction AST evaluation, all %d graphs)."
          % (len(targets), len(codes)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
