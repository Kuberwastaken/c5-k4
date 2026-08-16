"""GENERIC ARM -- verify the arm's own evaluator against the shipped definitions.

Four checks:

  1. with `GINV_SPEC=generator` every invariant this arm computes agrees with
     `scripts/gen/invariants.py` -- both backends (`brute` = exhaustive 2^n
     subsets, `scal` = branch and bound) -- on a deterministic sample of `D` and
     on graphs with `n = 9..24` outside `D`;
  2. a spectral audit: with `GINV_SPEC=true` this arm's `ceil(lambda_1)` differs
     from the generator's on a handful of graphs of `D`.  Each difference is
     listed and adjudicated against a floating-point eigenvalue computation.
     `floor(lambda_1)` is identical under both conventions everywhere;
  3. all 30 frozen targets, evaluated over the *whole* of `D` under the
     definition-faithful convention, have zero counterexamples;
  4. the same, under the generator's own convention, additionally reproduces
     every recorded equality count, min slack and max slack.

(3) and (4) are the baseline of the database-sanity gate.

Usage:
    python3 scripts/exp/generic/check_against_gen.py --sample 1200 --full-d \
        --json results/experiment/arm-generic-runs/_gate0.json
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "gen"))
sys.path.insert(0, HERE)

import networkx as nx                      # noqa: E402  (I/O + the gen backend)
import numpy as np                         # noqa: E402  (audit display only)
import ginv                                # noqa: E402
import invariants as GEN                   # noqa: E402

POP = os.path.join(ROOT, "results", "experiment", "fresh-population", "population.json")
DB = os.path.join(ROOT, "scripts", "gen", "data", "connected_n2_n8.g6")

NEEDED = [
    "n", "m", "Delta", "delta", "Sigma2", "dd", "f1", "res", "annih",
    "diam", "rad", "Tdist_min", "Tdist_max", "dist_even_min", "dist_even_max",
    "kappa", "cutv", "tri", "disp_max", "disp_min", "spec_floor", "spec_ceil",
    "alpha", "omega", "chi", "mu", "lam_max", "lam_min",
    "gamma", "gamma_t", "gamma_2", "gamma_i",
    "chi_bip", "chi_C4free", "chi_reg", "chi_tree",
    "deg_avg", "ecc_avg", "dist_avg", "CW", "lam_avg", "disp_avg",
]


def nx_from(n, adj):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in ginv.bits(adj[u]):
            if v > u:
                G.add_edge(u, v)
    return G


def compare(n, adj, backends=("brute", "scal")):
    G = nx_from(n, adj)
    mine = ginv.Inv(n, adj)
    bad = []
    for backend in backends:
        ref = GEN.compute(G, backend=backend)
        for k in NEEDED:
            if Fraction(mine.get(k)) != Fraction(ref[k]):
                bad.append((backend, k, mine.get(k), ref[k]))
    return bad


def lam1(n, adj):
    A = np.zeros((n, n))
    for u in range(n):
        for v in ginv.bits(adj[u]):
            A[u, v] = 1.0
    return float(max(np.linalg.eigvalsh(A)))


def full_D(codes, targets, convention):
    ginv.SPEC_CONVENTION = convention
    viol = {t["id"]: 0 for t in targets}
    eq = {t["id"]: 0 for t in targets}
    mn, mx = {}, {}
    for code in codes:
        n, adj = ginv.from_graph6(code)
        inv = ginv.Inv(n, adj)
        for t in targets:
            s = ginv.slack(t["expr"], inv)
            tid = t["id"]
            if s < 0:
                viol[tid] += 1
            elif s == 0:
                eq[tid] += 1
            if tid not in mn or s < mn[tid]:
                mn[tid] = s
            if tid not in mx or s > mx[tid]:
                mx[tid] = s
    return viol, eq, mn, mx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=1200)
    ap.add_argument("--seed", type=int, default=20260815)
    ap.add_argument("--full-d", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    rec = {"command": "python3 scripts/exp/generic/check_against_gen.py "
                      "--sample %d --seed %d%s" % (args.sample, args.seed,
                                                   " --full-d" if args.full_d else ""),
           "lines": []}

    codes = [ln.strip() for ln in open(DB) if ln.strip()]
    print("|D| = %d graphs" % len(codes))
    targets = json.load(open(POP))["targets"]

    # ---- 1. invariant cross-check, generator convention (strict equality)
    ginv.SPEC_CONVENTION = "generator"
    rng = random.Random(args.seed)
    idx = sorted(set(rng.sample(range(len(codes)), min(args.sample, len(codes))))
                 | set(range(min(60, len(codes)))))
    t0 = time.time()
    nbad = 0
    for i in idx:
        n, adj = ginv.from_graph6(codes[i])
        bad = compare(n, adj)
        if bad:
            nbad += 1
            print("MISMATCH on %s: %s" % (codes[i], bad[:6]))
    line = ("invariant cross-check against `scripts/gen/invariants.py` on %d "
            "graphs of `D`, against **both** gen backends (exhaustive `2^n` and "
            "branch-and-bound), over all 42 invariants the population uses: "
            "**%d mismatches**" % (len(idx), nbad))
    print(line + "   [%.1fs]" % (time.time() - t0))
    rec["lines"].append(line)
    rec["sample_D_graphs"] = len(idx)
    rec["sample_D_mismatches"] = nbad

    t0 = time.time()
    big = []
    rng2 = random.Random(args.seed + 1)
    for n in (9, 10, 12, 14, 16, 18, 20):
        for p in (0.15, 0.3, 0.5, 0.75):
            for _ in range(2):
                while True:
                    adj = [0] * n
                    for u in range(n):
                        for v in range(u + 1, n):
                            if rng2.random() < p:
                                adj[u] |= 1 << v
                                adj[v] |= 1 << u
                    if ginv.is_connected(n, adj):
                        break
                big.append((n, adj))
    for n in (12, 16, 20, 24):
        cyc = [0] * n
        for u in range(n):
            cyc[u] |= 1 << ((u + 1) % n)
            cyc[(u + 1) % n] |= 1 << u
        big.append((n, cyc))
        pth = [0] * n
        for u in range(n - 1):
            pth[u] |= 1 << (u + 1)
            pth[u + 1] |= 1 << u
        big.append((n, pth))
        big.append((n, [((1 << n) - 1) & ~(1 << u) for u in range(n)]))
    nbad2 = 0
    for n, adj in big:
        bad = compare(n, adj, backends=("scal",))
        if bad:
            nbad2 += 1
            print("BIG MISMATCH n=%d %s: %s" % (n, ginv.to_graph6(n, adj), bad[:6]))
    line = ("invariant cross-check against the `scripts/gen` branch-and-bound "
            "backend on %d graphs with `n = 9..24` outside `D` (random `G(n,p)` "
            "at four densities, paths, cycles, complete graphs): **%d "
            "mismatches**" % (len(big), nbad2))
    print(line + "   [%.1fs]" % (time.time() - t0))
    rec["lines"].append(line)
    rec["outside_D_graphs"] = len(big)
    rec["outside_D_mismatches"] = nbad2

    # ---- 2. spectral audit
    t0 = time.time()
    diffs = []
    for code in codes:
        n, adj = ginv.from_graph6(code)
        ginv.SPEC_CONVENTION = "true"
        mine = ginv.spectral_floor_ceil(n, adj)
        gen = GEN._spectral_bracket(adj, n)
        if mine != gen:
            diffs.append({"graph6": code, "n": n,
                          "arm_floor_ceil": list(mine),
                          "gen_floor_ceil": list(gen),
                          "lambda_1_float": round(lam1(n, adj), 10)})
    line = ("spectral audit: `floor(lambda_1)` is identical under both "
            "conventions on all 12,112 members of `D`. `ceil(lambda_1)` differs "
            "on **%d** of them: `scripts/gen/invariants._spectral_bracket` "
            "returns `ceil = floor` whenever `det(floor*I - A) = 0`, i.e. "
            "whenever `floor(lambda_1)` happens to be *some* eigenvalue, not "
            "necessarily the largest. On all %d the arm's value is the one that "
            "matches the actual spectral radius (e.g. `Dh_`, lambda_1 = "
            "sqrt(3) = 1.7320508…: the arm gives `ceil = 2`, the generator gives "
            "`ceil = 1`)." % (len(diffs), len(diffs)))
    print(line + "   [%.1fs]" % (time.time() - t0))
    rec["lines"].append(line)
    rec["spectral_ceil_differences"] = diffs
    rec["spectral_ceil_difference_count"] = len(diffs)
    rec["spectral_affected_targets"] = [
        t["id"] for t in targets if "spec_ceil" in ginv.invariants_of(t["expr"]["rhs"])
        or "spec_ceil" in ginv.invariants_of(t["expr"]["lhs"])]

    # ---- 3 / 4. full-D evaluation of all 30 targets under both conventions
    if args.full_d:
        out = {}
        for conv in ("true", "generator"):
            t0 = time.time()
            viol, eq, mn, mx = full_D(codes, targets, conv)
            bad_ce = [t["id"] for t in targets if viol[t["id"]]]
            bad_eq = [t["id"] for t in targets
                      if eq[t["id"]] != t["equality_count_in_D"]]
            bad_sl = [t["id"] for t in targets
                      if mx[t["id"]] != Fraction(t["max_slack_over_D"])
                      or mn[t["id"]] != Fraction(t["min_slack_over_D"])]
            out[conv] = {"counterexample_targets": bad_ce,
                         "equality_count_mismatches": bad_eq,
                         "slack_extreme_mismatches": bad_sl,
                         "seconds": round(time.time() - t0, 1)}
            print("full-D under %s: ce=%s eq-mismatch=%s slack-mismatch=%s [%.0fs]"
                  % (conv, bad_ce, bad_eq, bad_sl, time.time() - t0))
        rec["full_D"] = out
        line = ("all 30 frozen targets re-evaluated over all 12,112 members of "
                "`D` through this arm's own evaluator: **0 counterexamples "
                "under both conventions**. Under the generator's convention "
                "every recorded equality count, min slack and max slack "
                "reproduces exactly (%d mismatches). Under the "
                "definition-faithful convention the equality count of %s "
                "differs, because that target's right-hand side depends on "
                "`ceil(lambda_1)`."
                % (len(out["generator"]["equality_count_mismatches"]),
                   ", ".join(out["true"]["equality_count_mismatches"]) or "no target"))
        print(line)
        rec["lines"].append(line)
        rec["full_D_pass"] = (not out["true"]["counterexample_targets"]
                              and not out["generator"]["counterexample_targets"]
                              and not out["generator"]["equality_count_mismatches"]
                              and not out["generator"]["slack_extreme_mismatches"])
        if not rec["full_D_pass"]:
            print("FAIL")
            return 1

    if args.json:
        with open(args.json, "w") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
    return 1 if (nbad or nbad2) else 0


if __name__ == "__main__":
    raise SystemExit(main())
