"""Database-sanity gate for the catalogue arm.

Re-evaluates *this arm's reading* of all 30 frozen targets over the whole
generating database `D` (all connected graphs on 2 <= n <= 8), through both code
paths, and compares against what ``population.json`` records.  A reading that
"refutes" a member of `D` is a bug in the reading, not a crossing.

Checks per target:
  * counterexamples in `D` under path A and under path B (must be 0);
  * equality count and the full slack histogram vs the recorded ones;
  * every recorded ``equality_witnesses_graph6`` really attains equality.

Also cross-checks the two invariant paths on every graph of `D`.

Usage:  python3 scripts/exp/arm_catalogue_gate.py [--jobs N] [--out FILE]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "gen"))

import graph_db                                            # noqa: E402
import expressions                                         # noqa: E402  campaign evaluator
import arm_catalogue_patha as PA                           # noqa: E402
import arm_catalogue_pathb as PB                           # noqa: E402

POP = os.path.join(ROOT, "results", "experiment", "fresh-population", "population.json")

_TARGETS = None


def _init(targets):
    global _TARGETS
    _TARGETS = targets


def _work(codes):
    """Evaluate every target on a chunk of `D`; return per-target slack counters."""
    hist_a = [collections.Counter() for _ in _TARGETS]
    hist_b = [collections.Counter() for _ in _TARGETS]
    ce_a = [[] for _ in _TARGETS]
    ce_b = [[] for _ in _TARGETS]
    inv_mismatch = []
    eq_witness = {}                       # g6 -> {tid: slack string}
    hist_gen = [collections.Counter() for _ in _TARGETS]   # generator's own spec_ceil
    ce_gen = [[] for _ in _TARGETS]
    for code in codes:
        G = graph_db.from_g6(code)
        va, _, ex = PA.invariants(G)
        vb = PB.invariants(G)
        va_gen = dict(va)
        va_gen["spec_ceil"] = ex["gen_spec_ceil"]
        for k in PB.DEFINITIONS:
            if va[k] != vb[k]:
                inv_mismatch.append((code, k, str(va[k]), str(vb[k])))
        for i, t in enumerate(_TARGETS):
            e = t["expr"]
            sa = expressions.slack(e, va)
            lb, rb = PB.sides(e, vb)
            sb = (rb - lb) if e["rel"] == "<=" else (lb - rb)
            if sa != sb:
                inv_mismatch.append((code, "slack:" + t["id"], str(sa), str(sb)))
            hist_a[i][str(sa)] += 1
            hist_b[i][str(sb)] += 1
            if sa < 0:
                ce_a[i].append(code)
            if sb < 0:
                ce_b[i].append(code)
            if sa == 0:
                eq_witness.setdefault(code, set()).add(t["id"])
            if "spec_ceil" in t["invariants_used"]:
                sg = expressions.slack(e, va_gen)
                hist_gen[i][str(sg)] += 1
                if sg < 0:
                    ce_gen[i].append(code)
    eq_witness = {k: sorted(v) for k, v in eq_witness.items()}
    return hist_a, hist_b, ce_a, ce_b, inv_mismatch, eq_witness, hist_gen, ce_gen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--out", default=os.path.join(HERE, "gate_result.json"))
    args = ap.parse_args()

    pop = json.load(open(POP))
    targets = pop["targets"]

    t0 = time.time()
    codes = graph_db.build()                     # rebuilt from scripts/gen, not read
    rebuild_seconds = time.time() - t0
    digest = hashlib.sha256(("\n".join(codes) + "\n").encode()).hexdigest()
    recorded = pop["database"]["sha256_graph6_file"]
    print("rebuilt D: %d graphs in %.1fs; sha256 %s (recorded %s) -> %s"
          % (len(codes), rebuild_seconds, digest[:16], recorded[:16],
             "MATCH" if digest == recorded else "MISMATCH"), flush=True)
    assert len(codes) == pop["database"]["size"], (len(codes), pop["database"]["size"])

    order = sorted(codes, key=lambda c: (graph_db.from_g6(c).number_of_nodes(), c))
    chunks = [order[i::args.jobs * 4] for i in range(args.jobs * 4)]

    import multiprocessing as mp
    t0 = time.time()
    hist_a = [collections.Counter() for _ in targets]
    hist_b = [collections.Counter() for _ in targets]
    ce_a = [[] for _ in targets]
    ce_b = [[] for _ in targets]
    hist_g = [collections.Counter() for _ in targets]
    ce_g = [[] for _ in targets]
    mism = []
    eqw = {}
    with mp.Pool(args.jobs, initializer=_init, initargs=(targets,)) as pool:
        for k, (ha, hb, ca, cb, mm, ew, hg, cg) in enumerate(
                pool.imap_unordered(_work, chunks)):
            for i in range(len(targets)):
                hist_a[i].update(ha[i])
                hist_b[i].update(hb[i])
                hist_g[i].update(hg[i])
                ce_a[i].extend(ca[i])
                ce_b[i].extend(cb[i])
                ce_g[i].extend(cg[i])
            mism.extend(mm)
            eqw.update(ew)
            print("  chunk %d/%d done (%.1fs)" % (k + 1, len(chunks), time.time() - t0), flush=True)
    elapsed = time.time() - t0

    report = {
        "database_rebuilt": len(codes),
        "database_sha256": digest,
        "database_sha256_recorded": recorded,
        "database_sha256_match": digest == recorded,
        "invariant_path_mismatches": mism[:200],
        "invariant_path_mismatch_count": len(mism),
        "seconds": elapsed,
        "rebuild_seconds": rebuild_seconds,
        "targets": {},
    }
    for i, t in enumerate(targets):
        rec = {str(k): v for k, v in t["slack_histogram_over_D"].items()}
        mine = dict(hist_a[i])
        wit_ok = all(t["id"] in eqw.get(w, []) for w in t["equality_witnesses_graph6"])
        report["targets"][t["id"]] = {
            "counterexamples_in_D_pathA": len(ce_a[i]),
            "counterexamples_in_D_pathB": len(ce_b[i]),
            "counterexample_examples": sorted(set(ce_a[i]) | set(ce_b[i]))[:10],
            "equality_count_mine": mine.get("0", 0),
            "equality_count_recorded": t["equality_count_in_D"],
            "histogram_matches_recorded": mine == rec,
            "histogram_diff": None if mine == rec else {
                k: [rec.get(k), mine.get(k)]
                for k in sorted(set(rec) | set(mine), key=lambda s: Fraction(s))
                if rec.get(k) != mine.get(k)
            },
            "all_recorded_equality_witnesses_attain_equality": wit_ok,
            "pathA_pathB_slack_agree": not any(
                m[1] == "slack:" + t["id"] for m in mism),
            # the gate the preregistration actually specifies: a reading that
            # "refutes" a member of D is a bug in the reading, not a crossing.
            "gate": "PASS" if (len(ce_a[i]) == 0 and len(ce_b[i]) == 0) else "FAIL",
        }
        if "spec_ceil" in t["invariants_used"]:
            gen = dict(hist_g[i])
            report["targets"][t["id"]]["generator_spec_ceil_reading"] = {
                "counterexamples_in_D": len(ce_g[i]),
                "equality_count": gen.get("0", 0),
                "histogram_matches_recorded": gen == rec,
            }
    json.dump(report, open(args.out, "w"), indent=1)
    npass = sum(1 for v in report["targets"].values() if v["gate"] == "PASS")
    nhist = sum(1 for v in report["targets"].values() if v["histogram_matches_recorded"])
    print("gate: %d/%d PASS, %d/%d histograms identical to population.json, "
          "%d invariant/slack path mismatches, %.1fs"
          % (npass, len(targets), nhist, len(targets), len(mism), elapsed))
    print("written:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
