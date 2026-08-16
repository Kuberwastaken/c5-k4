"""Graffiti-style conjecture generator -- v2 fresh, uncontaminated population.

Pipeline
--------
  0. `D2` = every connected graph on 2 <= n <= 9, 273,192 graphs   (graph_db2.py)
  1. the exact 51-invariant vocabulary on every member, twice, on two backends
     that share no code                                (invariants2.py, invmatrix.py)
  1b **R4 gate**: the two backends must agree on every invariant over the whole
     of `D2` before anything is frozen                            (crossval.py)
  2. enumerate every right-hand side allowed by the template tables and test it
     against every (target, direction) pair                    (expressions2.py)
  3. keep a candidate iff:
       F1  zero counterexamples in `D2`
       F2  sharp: equality attained on at least one member of `D2`   (Dalmatian)
       F3  not an identity on `D2`
       F4  the right-hand side is non-constant on `D2`
       F5  the right-hand side does not mention the target invariant
       F6  the statement uses at least one hereditary induced invariant
           (`alpha`, `f`, `b`, `tree`, `path`) -- the v2 restriction
  4. deduplicate: D-S identical slack vector, D-C structural cluster,
     D-D Dalmatian domination
  5. select at most 30 by invariant-set diversity
  6. write results/experiment-v2/population/population.json

What is different from v1 and why
---------------------------------
* `D2` is one vertex further out (`n <= 9`, 273,192 graphs, against v1's
  `n <= 8`, 12,112).  v1's targets fell to plain annealing 14 times in 30; the
  design calls the weak database edge the likely cause.
* `f`, `b`, `tree`, `path` are **in** the emission vocabulary.  v1 dropped `f`
  and `b` on runtime and never had `tree`/`path`, which removed exactly the
  invariants the tested mechanism is about.
* F6 is new and is the population's defining restriction.

CONTAMINATION CONTRACT
----------------------
No candidate inequality is ever evaluated on a graph outside `D2`.  There is no
random search, no named-family lookup, no counterexample hunt and no import of
any arm instrument anywhere in `scripts/gen2/`.  The only code that touches
graphs outside `D2` is `bench_hereditary.py`, which measures invariant runtimes
and cross-checks two implementations of the same invariant against each other; it
prints timings and agreement flags only, and it is run before any candidate
exists.

Determinism: no randomness at any stage; `D2` is enumerated in a fixed order and
every tie-break is a fixed `blake2b` hash or lexicographic, so a re-run
reproduces `population.json` byte for byte.

Usage:
    python3 scripts/gen2/generate2.py
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from fractions import Fraction
from typing import Dict, List, Tuple

import numpy as np

import expressions2 as E
import graph_db2 as DB
import invariants2 as I
import invmatrix

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(REPO, "results", "experiment-v2", "population")
CROSSVAL_OK = os.path.join(HERE, "data", "crossval_ok.json")

SCALE = E.SCALE
MAX_TARGETS = 30
SALT = "c5k4-fresh-population-v2|"

# Left-hand sides.  As in v1, the order/size parameters and the 0/1
# characteristic functions appear only on the right, which is how Graffiti uses
# them.  Unlike v1, nothing is excluded for runtime: `f`, `b`, `tree` and `path`
# are targets in their own right, which is the point of v2.
TARGETS = [
    "alpha", "omega", "chi", "mu",
    "gamma", "gamma_t", "gamma_2", "gamma_i",
    "f", "b", "tree", "path",
    "res", "annih", "diam", "rad", "kappa", "lam_max",
]
HEREDITARY = frozenset(I.HEREDITARY)

MAX_PER_TARGET = 3
MAX_PER_TARGET_DIRECTION = 2

PRE_STRIDE = 37          # deterministic stride sample used to pre-reject candidates
DOM_STRIDE = 25          # deterministic stride sample used to pre-reject dominations
WITNESS_CAP = 300


def coin(stmt: str) -> str:
    """Deterministic pseudo-random ordering key, uncorrelated with mathematics.

    Every tie not settled by an explicit declared rule is settled by this hash of
    the statement text.  Ranking representatives by *how often* a bound is tight
    promotes near-identities; ranking them by *simplicity* promotes exactly the
    same textbook inequalities from the other side.  Both are thumbs on the
    scale, and ranking by tightness in particular would be optimising for the
    mechanism under test.  A coin is not.  `blake2b` is stable across runs and
    machines, unlike Python's salted `hash`.
    """
    return hashlib.blake2b((SALT + stmt).encode(), digest_size=16).hexdigest()


def build(target: str, direction: str, tid: str, args: Tuple[str, ...]):
    """(ast, statement, invariant set) for a candidate descriptor."""
    _, _, astf = E.BY_TID[tid]
    ast = astf(*[{"inv": a} for a in args])
    stmt = E.render_relation({"rel": direction, "lhs": {"inv": target}, "rhs": ast})
    return ast, stmt, frozenset(args) | {target}


def slack_of(col, desc, target_col=None):
    target, direction, tid, args = desc
    _, fn, _ = E.BY_TID[tid]
    arr = fn(*[col[a] for a in args])
    t = col[target] if target_col is None else target_col
    return (arr - t) if direction == "<=" else (t - arr)


# --------------------------------------------------------------------------
# step 2/3 -- sweep
# --------------------------------------------------------------------------
def sweep(names, M, stats: Dict[str, int]):
    K = len(names)
    ND = M.shape[0]
    col = {k: np.ascontiguousarray(M[:, j]) for j, k in enumerate(names)}

    rows, row_sign, row_target, row_dir = [], [], [], []
    for t in TARGETS:
        for d, s in (("<=", 1), (">=", -1)):
            rows.append(s * col[t])
            row_sign.append(s)
            row_target.append(t)
            row_dir.append(d)
    Mrow = np.vstack(rows)
    sign = np.array(row_sign, dtype=np.int64)[:, None]
    R = Mrow.shape[0]

    pre = np.arange(0, ND, PRE_STRIDE)
    Mpre = np.ascontiguousarray(Mrow[:, pre])
    stats["prefilter_sample_size"] = int(len(pre))

    buckets: Dict[tuple, tuple] = {}

    def consider(tid, args, arr):
        stats["rhs_expressions"] += 1
        if arr.min() == arr.max():
            stats["f4_rhs_constant_on_D2"] += 1
            return
        used = frozenset(args)
        okpre = None
        for r in range(R):
            t = row_target[r]
            if t in used:
                stats["f5_target_on_rhs"] += 1
                continue
            invset = used | {t}
            if not (invset & HEREDITARY):
                stats["f6_no_hereditary_invariant"] += 1
                continue
            if okpre is None:
                okpre = ((sign * arr[None, pre] - Mpre) >= 0).all(axis=1)
            if not okpre[r]:
                stats["prefilter_rejected"] += 1
                continue
            stats["candidates_reaching_full_D2"] += 1
            s = sign[r, 0] * arr - Mrow[r]
            if (s < 0).any():
                stats["f1_counterexample_in_D2"] += 1
                continue
            neq = int((s == 0).sum())
            if neq == 0:
                stats["f2_not_sharp"] += 1
                continue
            if neq == ND:
                stats["f3_identity_on_D2"] += 1
                continue
            stats["survived_filters"] += 1
            d = row_dir[r]
            key = (t, d, hashlib.blake2b(s.tobytes(), digest_size=16).digest())
            _, stmt, iset = build(t, d, tid, args)
            simp = (len(iset), len(stmt), stmt)
            cur = buckets.get(key)
            if cur is None or simp < cur[0]:
                buckets[key] = (simp, t, d, tid, tuple(args))

    t0 = time.time()
    pool = list(names)
    pos = {y: j for j, y in enumerate(pool)}
    for a, x in enumerate(pool):
        Ax = col[x]
        for tid, fn, _ in E.UNARY:
            consider(tid, (x,), fn(Ax))
        for y in pool:
            if y == x:
                continue
            Ay = col[y]
            if pos[y] > a:
                for tid, fn, _ in E.BINARY_SYM:
                    consider(tid, (x, y), fn(Ax, Ay))
            for tid, fn, _, needpos in E.BINARY_ASYM:
                if needpos and y not in E.POSITIVE_DENOMINATORS:
                    continue
                consider(tid, (x, y), fn(Ax, Ay))
        print("    swept %2d/%d first operands  (%d survivors, %d distinct slack "
              "vectors, %.0fs)" % (a + 1, K, stats["survived_filters"], len(buckets),
                                   time.time() - t0), flush=True)
    stats["after_DS_identical_slack_vector"] = len(buckets)
    return [b[1:] for b in buckets.values()], col


# --------------------------------------------------------------------------
# step 4 -- deduplication
# --------------------------------------------------------------------------
def dedup(descs, col, ND: int, stats: Dict[str, int]):
    """D-C structural cluster, then D-D Dalmatian domination.

    Memory note: 273,192 int64 slack entries is 2.2 MB per candidate, so unlike
    v1 nothing here keeps a slack vector for more than one candidate at a time.
    D-C needs no slack at all (its key is the invariant set and its tie-break is
    the coin).  D-D pre-rejects dominations on a fixed stride sample -- sound,
    because a domination that fails on a subset fails on the whole -- and only
    confirms the survivors on the full vector.
    """
    by_cluster: Dict[tuple, tuple] = {}
    for d in descs:
        target, direction, tid, args = d
        _, stmt, iset = build(target, direction, tid, args)
        key = (target, direction, tuple(sorted(iset)))
        c = coin(stmt)
        cur = by_cluster.get(key)
        if cur is None or c < cur[0]:
            by_cluster[key] = (c, d, stmt, iset)
    dc = list(by_cluster.values())
    stats["after_DC_structural_cluster"] = len(dc)

    groups: Dict[tuple, List[tuple]] = {}
    for c, d, stmt, iset in dc:
        groups.setdefault((d[0], d[1]), []).append((c, d, stmt, iset))

    dom_idx = np.arange(0, ND, DOM_STRIDE)
    colsub = {k: np.ascontiguousarray(v[dom_idx]) for k, v in col.items()}

    kept: List[tuple] = []
    t0 = time.time()
    for key in sorted(groups):
        g = groups[key]
        stat = []
        for c, d, stmt, iset in g:
            s = slack_of(col, d)
            stat.append((int(s.sum()), int(s.max())))
        order = sorted(range(len(g)), key=lambda i: (stat[i][0], g[i][0]))
        keepg: List[int] = []
        subv: Dict[int, np.ndarray] = {}
        for i in order:
            ci = subv.get(i)
            if ci is None:
                ci = slack_of(colsub, g[i][1])
                subv[i] = ci
            dominated = False
            for j in keepg:
                if stat[j][0] > stat[i][0] or stat[j][1] > stat[i][1]:
                    continue
                if not (subv[j] <= ci).all():
                    continue
                if (slack_of(col, g[j][1]) <= slack_of(col, g[i][1])).all():
                    dominated = True
                    break
            if not dominated:
                keepg.append(i)
            else:
                subv.pop(i, None)
        kept.extend(g[i] for i in keepg)
        print("    D-D %-24s %5d -> %4d  (%.0fs)"
              % ("%s %s" % key, len(g), len(keepg), time.time() - t0), flush=True)
    kept.sort(key=lambda z: z[0])
    stats["after_DD_dalmatian_domination"] = len(kept)
    return kept


# --------------------------------------------------------------------------
# step 5 -- diversity selection
# --------------------------------------------------------------------------
def select(cands, stats: Dict[str, int]):
    if len(cands) <= MAX_TARGETS:
        stats["selected"] = len(cands)
        return sorted(cands, key=lambda z: (z[1][0], z[1][1], z[2]))
    pool = sorted(cands, key=lambda z: z[0])
    chosen: List[tuple] = []
    per_target: Dict[str, int] = {}
    per_td: Dict[tuple, int] = {}

    def jacc(a, b):
        return 1.0 - len(a & b) / float(len(a | b))

    while len(chosen) < MAX_TARGETS:
        best = None
        for z in pool:
            t, dirn = z[1][0], z[1][1]
            if per_target.get(t, 0) >= MAX_PER_TARGET:
                continue
            if per_td.get((t, dirn), 0) >= MAX_PER_TARGET_DIRECTION:
                continue
            dmin = min((jacc(z[3], s[3]) for s in chosen), default=1.0)
            k = (-round(dmin, 6), z[0])
            if best is None or k < best[0]:
                best = (k, z)
        if best is None:
            break
        z = best[1]
        chosen.append(z)
        pool.remove(z)
        per_target[z[1][0]] = per_target.get(z[1][0], 0) + 1
        per_td[(z[1][0], z[1][1])] = per_td.get((z[1][0], z[1][1]), 0) + 1
    stats["selected"] = len(chosen)
    return sorted(chosen, key=lambda z: (z[1][0], z[1][1], z[2]))


# --------------------------------------------------------------------------
# step 6 -- emit
# --------------------------------------------------------------------------
def emit(chosen, col, codes, sizes, stats, meta) -> dict:
    targets = []
    for i, (_, desc, stmt, iset) in enumerate(chosen, 1):
        target, direction, tid, args = desc
        ast, _, _ = build(target, direction, tid, args)
        s = slack_of(col, desc)
        eq = np.flatnonzero(s == 0).tolist()
        by_n: Dict[str, int] = {}
        for j in eq:
            by_n[str(sizes[j])] = by_n.get(str(sizes[j]), 0) + 1
        ordered = sorted(eq, key=lambda j: (-sizes[j], codes[j]))
        slack_hist: Dict[str, int] = {}
        vals, cnts = np.unique(s, return_counts=True)
        for v, k in zip(vals.tolist(), cnts.tolist()):
            slack_hist[str(Fraction(int(v), SCALE))] = int(k)
        targets.append({
            "id": "FP2-%03d" % i,
            "statement": "For every connected graph G with n(G) >= 2:  %s" % stmt,
            "relation": stmt,
            "target_invariant": target,
            "direction": direction,
            "template": tid,
            "template_operands": list(args),
            "invariants_used": sorted(iset),
            "hereditary_invariants_used": sorted(iset & HEREDITARY),
            "invariant_definitions": {k: I.DEFINITION[k] for k in sorted(iset)},
            "expr": {"rel": direction, "lhs": {"inv": target}, "rhs": ast},
            "min_slack_over_D": str(Fraction(int(s.min()), SCALE)),
            "max_slack_over_D": str(Fraction(int(s.max()), SCALE)),
            "counterexamples_in_D": 0,
            "equality_count_in_D": len(eq),
            "equality_by_order_n": {k: by_n[k] for k in sorted(by_n, key=int)},
            "equality_witnesses_graph6": [codes[j] for j in ordered[:WITNESS_CAP]],
            "equality_witnesses_truncated": len(eq) > WITNESS_CAP,
            "slack_histogram_over_D": {k: slack_hist[k] for k in
                                       sorted(slack_hist, key=lambda x: Fraction(x))},
        })
    return {
        "schema": "c5k4/fresh-population/v2",
        "generated_by": "scripts/gen2/generate2.py",
        "frozen": True,
        "note": "`D` in every field name below denotes the v2 database D2 "
                "(all connected graphs with 2 <= n <= 9); the field names are "
                "kept identical to the v1 population schema.",
        "population_restriction": "every target uses at least one hereditary "
                                  "induced invariant from {alpha, f, b, tree, path}",
        "database": meta,
        "filter_counts": stats,
        "targets": targets,
    }


def main() -> int:
    t_start = time.time()
    if not os.path.exists(CROSSVAL_OK):
        raise SystemExit("R4 gate: run scripts/gen2/crossval.py first (%s missing)"
                         % CROSSVAL_OK)
    with open(CROSSVAL_OK) as fh:
        cv = json.load(fh)
    if not cv.get("passed") or cv.get("total_mismatches") != 0:
        raise SystemExit("R4 gate: cross-validation did not pass; refusing to freeze")

    print("[1/6] loading D2 ...", flush=True)
    codes = DB.load_codes()
    sizes = [ord(c[0]) - 63 for c in codes]
    by_n: Dict[int, int] = {}
    for s in sizes:
        by_n[s] = by_n.get(s, 0) + 1
    print("      |D2| = %d  %s" % (len(codes), by_n), flush=True)
    assert cv["database"]["sha256_graph6_file"] == DB.sha256_db(), \
        "R4 gate: crossval ran against a different database file"

    print("[2/6] invariants (backend A; backend B already agreed on all of D2) ...",
          flush=True)
    M = invmatrix.load("A", codes)
    names = list(I.VOCAB)
    print("      %d invariants x %d graphs, all emitted (v1 excluded f and b here)"
          % (len(names), M.shape[0]), flush=True)

    jj = {k: j for j, k in enumerate(names)}
    for k in E.POSITIVE_DENOMINATORS:
        assert int(M[:, jj[k]].min()) > 0, \
            "denominator %s is not positive everywhere on D2" % k
    print("      denominator check: all %d admissible denominators > 0 on all of D2"
          % len(E.POSITIVE_DENOMINATORS), flush=True)

    stats = {k: 0 for k in ["rhs_expressions", "f4_rhs_constant_on_D2",
                            "f5_target_on_rhs", "f6_no_hereditary_invariant",
                            "prefilter_rejected", "candidates_reaching_full_D2",
                            "f1_counterexample_in_D2", "f2_not_sharp",
                            "f3_identity_on_D2", "survived_filters"]}
    print("[3/6] sweeping templates ...", flush=True)
    descs, col = sweep(names, M, stats)
    print("      %d survivors -> %d distinct slack vectors"
          % (stats["survived_filters"], len(descs)), flush=True)

    print("[4/6] deduplicating ...", flush=True)
    kept = dedup(descs, col, M.shape[0], stats)
    print("      %d after dedup" % len(kept), flush=True)

    print("[5/6] selecting <= %d ..." % MAX_TARGETS, flush=True)
    chosen = select(kept, stats)
    print("      %d chosen" % len(chosen), flush=True)

    meta = {
        "definition": "every connected graph with 2 <= n <= 9, up to isomorphism",
        "size": len(codes),
        "by_order": {str(k): by_n[k] for k in sorted(by_n)},
        "boundary": "complete through n = 9; no graph on n >= 10 is in D2 and no "
                    "candidate was evaluated on any graph outside D2",
        "source": "nauty 2.8.8 `geng -c n` for n = 2..9; counts verified against "
                  "OEIS A001349 and completeness re-proved independently by "
                  "exhaustive one-vertex extension (scripts/gen2/graph_db2.py --verify)",
        "sha256_graph6_file": DB.sha256_db(),
    }
    stats["templates"] = E.TEMPLATE_COUNTS
    stats["vocabulary_computed"] = len(I.VOCAB)
    stats["vocabulary_emitted"] = len(names)
    stats["excluded_for_runtime"] = []
    stats["targets_considered"] = len(TARGETS)
    stats["hereditary_invariants"] = list(I.HEREDITARY)

    print("[6/6] writing population ...", flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = emit(chosen, col, codes, sizes, stats, meta)
    path = os.path.join(OUT_DIR, "population.json")
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print("      %s  (%d targets, %.1f kB)"
          % (path, len(chosen), os.path.getsize(path) / 1024.0), flush=True)
    print(json.dumps(stats, indent=1))
    # deliberately NOT part of the frozen artifact: a wall-clock field would make
    # two runs differ and break byte-for-byte reproducibility.
    print("wall clock: %.1fs" % (time.time() - t_start))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
