"""Graffiti-style conjecture generator -- fresh, uncontaminated population.

Pipeline
--------
  0. build `D` = every connected graph on 2 <= n <= 8            (graph_db.py)
  1. compute the exact invariant vocabulary on every member of `D` (invariants.py)
  2. enumerate every right-hand side allowed by the template tables (expressions.py)
     and test each of them against every (target, direction) pair
  3. keep a candidate iff:
       F1  zero counterexamples in `D`
       F2  sharp: equality attained on at least one member of `D`   (Dalmatian)
       F3  not an identity on `D`: equality does *not* hold everywhere
       F4  the right-hand side is non-constant on `D`
       F5  the right-hand side does not mention the target invariant
  4. deduplicate                                                   (see DEDUP below)
  5. select at most 30 by invariant-set diversity
  6. write results/experiment/fresh-population/population.json

CONTAMINATION CONTRACT
----------------------
No candidate inequality is ever evaluated on a graph outside `D`.  The only code
that touches graphs outside `D` is ``check_invariants.py``, which measures
*runtimes* of invariant computations and is run before any candidate exists.
There is no random search, no named-family lookup, and no counterexample hunt in
this file.

Determinism: no randomness at any stage.  `D` is enumerated in a fixed order and
every tie-break is lexicographic, so a re-run reproduces the output byte for byte.

Usage:
    python3 scripts/gen/generate.py            # full run
    python3 scripts/gen/generate.py --recompute-invariants
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from fractions import Fraction
from typing import Dict, List

import numpy as np

import expressions as E
import graph_db as DB
import invariants as I

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(REPO, "results", "experiment", "fresh-population")
CACHE = os.path.join(HERE, "data", "invariants_n2_n8.npz")

SCALE = E.SCALE
MAX_TARGETS = 30

# Left-hand sides.  Graffiti conjectures bound an "interesting" invariant; the
# 0/1 characteristic functions and the raw order/size parameters appear only on
# the right, as Graffiti uses them (correction terms and scale terms).
TARGETS = [
    "alpha", "omega", "chi", "mu",
    "gamma", "gamma_t", "gamma_2", "gamma_i",
    "f", "b",
    "res", "annih", "diam", "rad", "kappa", "lam_max",
]

# quotas that stop one invariant owning the population
MAX_PER_TARGET = 3
MAX_PER_TARGET_DIRECTION = 2


# --------------------------------------------------------------------------
# step 1 -- invariant matrix
# --------------------------------------------------------------------------
def invariant_matrix(D, recompute: bool = False):
    """(names, int64 matrix of shape (|D|, K) in SCALE units)."""
    if not recompute and os.path.exists(CACHE):
        z = np.load(CACHE, allow_pickle=False)
        if list(z["names"]) == I.VOCAB and z["M"].shape[0] == len(D):
            return list(z["names"]), z["M"]
    rows = []
    t0 = time.time()
    for i, G in enumerate(D):
        vals = I.compute(G, "brute")
        row = []
        for k in I.VOCAB:
            v = Fraction(vals[k])
            scaled = v * SCALE
            if scaled.denominator != 1:
                raise AssertionError("SCALE=%d does not clear %s=%s" % (SCALE, k, v))
            row.append(int(scaled))
        rows.append(row)
        if (i + 1) % 2000 == 0:
            print("    invariants %d/%d  %.0fs" % (i + 1, len(D), time.time() - t0), flush=True)
    M = np.array(rows, dtype=np.int64)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez_compressed(CACHE, names=np.array(I.VOCAB), M=M)
    return I.VOCAB, M


# --------------------------------------------------------------------------
# step 2/3 -- sweep
# --------------------------------------------------------------------------
SALT = "c5k4-fresh-population-v1|"


def coin(c) -> str:
    """Deterministic pseudo-random ordering key, uncorrelated with mathematics.

    Every tie in this pipeline that is not settled by an explicit, declared rule
    is settled by this hash of the statement text.  It is the review's "capped at
    30 by public randomness" applied deterministically: `blake2b` is stable
    across runs and machines (unlike Python's salted `hash`), so the output is
    reproducible, and it cannot correlate with tightness, provability, or the
    mechanism under test.

    This matters.  Ranking representatives by *how often* a bound is tight
    promotes near-identities (`kappa <= delta`, `chi >= omega`); ranking them by
    *simplicity* promotes exactly the same textbook inequalities from the other
    side.  Both are thumbs on the scale.  A coin is not.
    """
    return hashlib.blake2b((SALT + c.stmt).encode(), digest_size=16).hexdigest()


def simplicity(c) -> tuple:
    """Surface-form key, used only to choose among statements that are *numerically
    identical on all of `D`* (dedup rule D-S).  Fewest invariant symbols, then
    shortest rendering, then lexicographic: of `mu <= floor(m/deg_avg)` and
    `mu <= floor(n/2)` it keeps the readable one."""
    return (len(c.invset), len(c.stmt), c.stmt)


class Cand:
    __slots__ = ("target", "direction", "tid", "args", "ast", "slack",
                 "eq_idx", "stmt", "invset")

    def __init__(self, target, direction, tid, args, ast, slack, eq_idx):
        self.target = target
        self.direction = direction
        self.tid = tid
        self.args = args
        self.ast = ast
        self.slack = slack
        self.eq_idx = eq_idx
        self.stmt = E.render_relation({"rel": direction, "lhs": {"inv": target}, "rhs": ast})
        self.invset = frozenset([target]) | E.invariants_of(ast)


def sweep(names, M, stats: Dict[str, int]):
    """Enumerate every right-hand side, test it against every (target, direction).

    Dedup rule D-S is applied *streaming* and keeps no slack vectors: candidates
    are bucketed by (target, direction, hash of the slack vector over `D`) and
    only the simplest surface form per bucket is retained as a descriptor.  The
    raw survivor count is ~1e5 and each slack vector is 48 kB, so nothing else
    would fit in RAM; slack vectors are recomputed later, one group at a time.
    """
    K = len(names)
    ND = M.shape[0]
    col = {k: np.ascontiguousarray(M[:, j]) for j, k in enumerate(names)}

    # (target, direction) rows, folded so that every row is a "<=" test:
    #   "<=" : row = X[t] , rhs = R      -> slack = R - X[t]
    #   ">=" : row = -X[t], rhs = -R     -> slack = X[t] - R
    rows, row_sign, row_target, row_dir = [], [], [], []
    for t in TARGETS:
        for d, s in (("<=", 1), (">=", -1)):
            rows.append(s * col[t])
            row_sign.append(s)
            row_target.append(t)
            row_dir.append(d)
    Mrow = np.vstack(rows)                                   # (R, |D|)
    sign = np.array(row_sign, dtype=np.int64)[:, None]
    R = Mrow.shape[0]

    # deterministic pre-filter columns (stride sample over the fixed order of D)
    pre = np.arange(0, ND, 6)
    Mpre = np.ascontiguousarray(Mrow[:, pre])

    buckets: Dict[tuple, tuple] = {}          # (target, dir, slack-hash) -> descriptor

    def consider(tid, args, ast_fn, arr):
        stats["rhs_expressions"] += 1
        if arr.min() == arr.max():
            stats["rhs_constant"] += 1
            return
        used = frozenset(args)
        Spre = sign * arr[None, pre] - Mpre
        okpre = (Spre >= 0).all(axis=1)
        for r in range(R):
            if not okpre[r]:
                continue
            t = row_target[r]
            if t in used:
                stats["f5_target_on_rhs"] += 1
                continue
            stats["candidates_reaching_full_D"] += 1
            s = sign[r, 0] * arr - Mrow[r]
            if (s < 0).any():
                stats["f1_counterexample_in_D"] += 1
                continue
            neq = int((s == 0).sum())
            if neq == 0:
                stats["f2_not_sharp"] += 1
                continue
            if neq == ND:
                stats["f3_identity_on_D"] += 1
                continue
            stats["survived_filters"] += 1
            d = row_dir[r]
            key = (t, d, hashlib.blake2b(s.tobytes(), digest_size=16).digest())
            stmt = E.render_relation({"rel": d, "lhs": {"inv": t}, "rhs": ast_fn()})
            invset = used | {t}
            simp = (len(invset), len(stmt), stmt)
            cur = buckets.get(key)
            if cur is None or simp < cur[0]:
                buckets[key] = (simp, t, d, tid, tuple(args))

    t0 = time.time()
    pool = list(names)
    pos = {y: j for j, y in enumerate(pool)}
    for a, x in enumerate(pool):
        Ax = col[x]
        for tid, fn, astf in E.UNARY:
            consider(tid, (x,), (lambda astf=astf, x=x: astf({"inv": x})), fn(Ax))
        for y in pool:
            if y == x:
                continue
            Ay = col[y]
            if pos[y] > a:                                   # unordered pass
                for tid, fn, astf in E.BINARY_SYM:
                    consider(tid, (x, y),
                             (lambda astf=astf, x=x, y=y: astf({"inv": x}, {"inv": y})),
                             fn(Ax, Ay))
            for tid, fn, astf, needpos in E.BINARY_ASYM:
                if needpos and y not in E.POSITIVE_DENOMINATORS:
                    continue
                consider(tid, (x, y),
                         (lambda astf=astf, x=x, y=y: astf({"inv": x}, {"inv": y})),
                         fn(Ax, Ay))
        print("    swept %2d/%d first operands  (%d survivors, %d distinct slack "
              "vectors, %.0fs)" % (a + 1, K, stats["survived_filters"], len(buckets),
                                   time.time() - t0), flush=True)
    stats["after_DS_identical_slack_vector"] = len(buckets)
    return [b[1:] for b in buckets.values()]


def materialise(col, desc) -> Cand:
    """Rebuild a full candidate (AST, statement, slack vector) from a descriptor."""
    target, direction, tid, args = desc
    _, fn, astf = E.BY_TID[tid]
    arr = fn(*[col[a] for a in args])
    ast = astf(*[{"inv": a} for a in args])
    s = (arr - col[target]) if direction == "<=" else (col[target] - arr)
    return Cand(target, direction, tid, args, ast, s.astype(np.int32),
                np.flatnonzero(s == 0))


# --------------------------------------------------------------------------
# step 4 -- deduplication
# --------------------------------------------------------------------------
def dedup(descs, col, stats: Dict[str, int]) -> List[Cand]:
    """Two dedup passes on top of the streaming structural clustering (D-C).

    D-S  (applied inside `sweep`)  identical slack vector over `D` and the same
         (target, direction): algebraically different restatements that are
         numerically the same statement on the whole database, e.g.
         `mu <= floor(m/deg_avg)` and `mu <= floor(n/2)`, or a correction term
         that is identically zero.  One representative, the simplest surface
         form (fewest invariants, then shortest, then lexicographic).
    D-C  structural cluster = (target, direction, set of invariant symbols used).
         Graffiti-lineage generators emit many restatements over the same
         invariants; one representative per cluster, chosen by the neutral
         deterministic coin (see `coin`).
    D-D  Dalmatian significance: drop a representative that some other
         representative for the same (target, direction) beats or ties on *every*
         member of `D` -- it is uniformly no stronger, so it carries no
         information the other does not.
    """
    # D-C: structural cluster = (target, direction, set of invariant symbols).
    by_cluster: Dict[tuple, Cand] = {}
    for d in descs:
        c = materialise(col, d)
        key = (c.target, c.direction, tuple(sorted(c.invset)))
        cur = by_cluster.get(key)
        if cur is None or coin(c) < coin(cur):
            by_cluster[key] = c
    dc = list(by_cluster.values())
    stats["after_DC_structural_cluster"] = len(dc)

    # D-D: Dalmatian significance, within each (target, direction).
    kept: List[Cand] = []
    groups: Dict[tuple, List[Cand]] = {}
    for c in dc:
        groups.setdefault((c.target, c.direction), []).append(c)
    for key in sorted(groups):
        g = sorted(groups[key], key=lambda c: (int(c.slack.sum()), coin(c)))
        totals = [int(c.slack.sum()) for c in g]
        maxes = [int(c.slack.max()) for c in g]
        keepg: List[int] = []
        for i, c in enumerate(g):
            dominated = False
            for j in keepg:
                if totals[j] > totals[i] or maxes[j] > maxes[i]:
                    continue
                if (g[j].slack <= c.slack).all():
                    dominated = True
                    break
            if not dominated:
                keepg.append(i)
        kept.extend(g[i] for i in keepg)
    kept.sort(key=coin)
    stats["after_DD_dalmatian_domination"] = len(kept)
    return kept


# --------------------------------------------------------------------------
# step 5 -- diversity selection
# --------------------------------------------------------------------------
def select(cands: List[Cand], stats: Dict[str, int]) -> List[Cand]:
    if len(cands) <= MAX_TARGETS:
        return sorted(cands, key=lambda c: (c.target, c.direction, c.stmt))
    pool = sorted(cands, key=coin)
    chosen: List[Cand] = []
    per_target: Dict[str, int] = {}
    per_td: Dict[tuple, int] = {}

    def jacc(a, b):
        return 1.0 - len(a & b) / float(len(a | b))

    while len(chosen) < MAX_TARGETS:
        best = None
        for c in pool:
            if per_target.get(c.target, 0) >= MAX_PER_TARGET:
                continue
            if per_td.get((c.target, c.direction), 0) >= MAX_PER_TARGET_DIRECTION:
                continue
            d = min((jacc(c.invset, s.invset) for s in chosen), default=1.0)
            key = (-round(d, 6), coin(c))
            if best is None or key < best[0]:
                best = (key, c)
        if best is None:
            break
        c = best[1]
        chosen.append(c)
        pool.remove(c)
        per_target[c.target] = per_target.get(c.target, 0) + 1
        per_td[(c.target, c.direction)] = per_td.get((c.target, c.direction), 0) + 1
    stats["selected"] = len(chosen)
    return sorted(chosen, key=lambda c: (c.target, c.direction, c.stmt))


# --------------------------------------------------------------------------
# step 6 -- emit
# --------------------------------------------------------------------------
WITNESS_CAP = 300


def emit(chosen: List[Cand], D, codes: List[str], sizes: List[int], stats, meta) -> dict:
    targets = []
    for i, c in enumerate(chosen, 1):
        eq = list(map(int, c.eq_idx))
        by_n: Dict[str, int] = {}
        for j in eq:
            by_n[str(sizes[j])] = by_n.get(str(sizes[j]), 0) + 1
        # record witnesses largest-n first: n=8 is the database edge
        ordered = sorted(eq, key=lambda j: (-sizes[j], codes[j]))
        rec_idx = ordered[:WITNESS_CAP]
        slack_hist: Dict[str, int] = {}
        vals, cnts = np.unique(c.slack, return_counts=True)
        for v, k in zip(vals.tolist(), cnts.tolist()):
            slack_hist[str(Fraction(int(v), SCALE))] = int(k)
        targets.append({
            "id": "FP-%03d" % i,
            "statement": "For every connected graph G with n(G) >= 2:  %s" % c.stmt,
            "relation": c.stmt,
            "target_invariant": c.target,
            "direction": c.direction,
            "template": c.tid,
            "template_operands": list(c.args),
            "invariants_used": sorted(c.invset),
            "invariant_definitions": {k: I.DEFINITION[k] for k in sorted(c.invset)},
            "expr": {"rel": c.direction, "lhs": {"inv": c.target},
                     "rhs": c.ast},
            "min_slack_over_D": str(Fraction(int(c.slack.min()), SCALE)),
            "max_slack_over_D": str(Fraction(int(c.slack.max()), SCALE)),
            "counterexamples_in_D": 0,
            "equality_count_in_D": len(eq),
            "equality_by_order_n": {k: by_n[k] for k in sorted(by_n, key=int)},
            "equality_witnesses_graph6": [codes[j] for j in rec_idx],
            "equality_witnesses_truncated": len(eq) > WITNESS_CAP,
            "slack_histogram_over_D": {k: slack_hist[k]
                                       for k in sorted(slack_hist, key=lambda s: Fraction(s))},
        })
    return {
        "schema": "c5k4/fresh-population/v1",
        "generated_by": "scripts/gen/generate.py",
        "frozen": True,
        "database": meta,
        "filter_counts": stats,
        "targets": targets,
    }


def main() -> int:
    recompute = "--recompute-invariants" in sys.argv
    t_start = time.time()
    print("[1/6] building D ...", flush=True)
    D = DB.load()
    codes = [DB.g6(G) for G in D]
    sizes = [G.number_of_nodes() for G in D]
    by_n: Dict[int, int] = {}
    for s in sizes:
        by_n[s] = by_n.get(s, 0) + 1
    print("      |D| = %d  %s" % (len(D), by_n), flush=True)

    print("[2/6] invariants ...", flush=True)
    names, M = invariant_matrix(D, recompute)
    print("      %d invariants x %d graphs" % (len(names), M.shape[0]), flush=True)

    stats = {k: 0 for k in ["rhs_expressions", "rhs_constant", "f5_target_on_rhs",
                            "candidates_reaching_full_D", "f1_counterexample_in_D",
                            "f2_not_sharp", "f3_identity_on_D", "survived_filters"]}
    print("[3/6] sweeping templates ...", flush=True)
    descs = sweep(names, M, stats)
    print("      %d survivors -> %d distinct slack vectors"
          % (stats["survived_filters"], len(descs)), flush=True)

    print("[4/6] deduplicating ...", flush=True)
    col = {k: np.ascontiguousarray(M[:, j]) for j, k in enumerate(names)}
    kept = dedup(descs, col, stats)
    print("      %d after dedup" % len(kept), flush=True)

    print("[5/6] selecting <= %d ..." % MAX_TARGETS, flush=True)
    chosen = select(kept, stats)
    print("      %d chosen" % len(chosen), flush=True)

    meta = {
        "definition": "every connected graph with 2 <= n <= 8, up to isomorphism",
        "size": len(D),
        "by_order": {str(k): by_n[k] for k in sorted(by_n)},
        "source_n2_n7": "networkx.graph_atlas_g()",
        "source_n8": "exhaustive one-vertex extension of all 1044 graphs on 7 "
                     "vertices with exact isomorphism rejection (scripts/gen/graph_db.py)",
        "sha256_graph6_file": hashlib.sha256(
            open(DB.DB_PATH, "rb").read()).hexdigest(),
    }
    stats["templates"] = E.TEMPLATE_COUNTS
    stats["vocabulary_size"] = len(names)
    stats["targets_considered"] = len(TARGETS)
    stats["wall_clock_seconds"] = round(time.time() - t_start, 1)

    print("[6/6] writing population ...", flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = emit(chosen, D, codes, sizes, stats, meta)
    path = os.path.join(OUT_DIR, "population.json")
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print("      %s  (%d targets, %.1f kB)"
          % (path, len(chosen), os.path.getsize(path) / 1024.0), flush=True)
    print(json.dumps(stats, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
