"""R4 -- cross-validate every invariant against a second independent
implementation, over the whole of `D2`, **before** the population is frozen.

METHOD v1.7 R4:

    Every invariant in a generation vocabulary is validated against a second
    independent implementation over the whole database before the population is
    frozen, not after.  Three solver bugs were caught pre-freeze by exactly this
    discipline; the one that escaped was the one implemented only once.

The one that escaped was ``ceil(lambda_1)``.  v1's two backends shared a single
``_poly_part``, so every polynomial invariant -- including the spectral bracket
-- was implemented once and cross-checked against itself.  In v2 the backends
share no code at all (see ``invariants2.py``); ``invariants2.CROSSCHECK_PATHS``
records, per invariant, what the two paths actually are.

This script also re-runs v1's defective rule on all of `D2` as a regression
witness, to show that the discipline catches the class of bug that escaped.

Output: ``data/crossval_ok.json``.  ``generate2.py`` refuses to run without it,
so the population cannot be frozen before the check has passed.

Usage:
    python3 scripts/gen2/crossval.py
"""
from __future__ import annotations

import json
import os
import time
from fractions import Fraction
from typing import Dict, List

import numpy as np

import graph_db2 as DB
import invariants2 as I
import invmatrix
from expressions2 import SCALE

HERE = os.path.dirname(os.path.abspath(__file__))
OK_PATH = os.path.join(HERE, "data", "crossval_ok.json")


def v1_rule_is_wrong(adj: List[int], n: int, fl: int, ce: int) -> bool:
    """Would v1's `ceil(lambda_1)` rule get this graph wrong?

    v1 computed `floor(lambda_1)` exactly the way backend A does (smallest
    integer k with `kI - A` positive definite, minus one), and then declared
    `lambda_1` an integer whenever `det(fl*I - A) == 0`.  That determinant
    vanishes whenever *any* eigenvalue equals `fl`, not only when the spectral
    radius does.  So v1's answer is wrong exactly when the true ceiling is
    `fl + 1` **and** `fl` is an eigenvalue of `A`.  Reproduced only to count how
    many members of `D2` it would corrupt; not part of the v2 vocabulary.
    """
    if ce == fl:
        return False
    M = [[(fl if i == j else 0) - (1 if adj[i] >> j & 1 else 0) for j in range(n)]
         for i in range(n)]
    return I._det_int(M, n) == 0


def main() -> int:
    codes = DB.load_codes()
    sizes = [ord(c[0]) - 63 for c in codes]
    print("|D2| = %d" % len(codes), flush=True)

    t0 = time.time()
    MA = invmatrix.load("A", codes)
    print("backend A matrix ready  %.0fs" % (time.time() - t0), flush=True)
    t0 = time.time()
    MB = invmatrix.load("B", codes)
    print("backend B matrix ready  %.0fs" % (time.time() - t0), flush=True)

    assert MA.shape == MB.shape == (len(codes), len(I.VOCAB))

    report: Dict[str, dict] = {}
    total_mismatch = 0
    print("\n== R4 cross-validation: backend A vs backend B on all %d members ==" % len(codes))
    print("%-14s %-10s %s" % ("invariant", "mismatches", "paths (A | B)"))
    for j, k in enumerate(I.VOCAB):
        diff = np.flatnonzero(MA[:, j] != MB[:, j])
        total_mismatch += len(diff)
        ex = []
        for idx in diff[:5]:
            ex.append({"graph6": codes[int(idx)], "n": sizes[int(idx)],
                       "A": str(Fraction(int(MA[idx, j]), SCALE)),
                       "B": str(Fraction(int(MB[idx, j]), SCALE))})
        pa, pb = I.CROSSCHECK_PATHS[k]
        report[k] = {"mismatches": int(len(diff)), "examples": ex,
                     "path_A": pa, "path_B": pb}
        print("%-14s %-10d %s | %s" % (k, len(diff), pa, pb))

    # --- regression witness: v1's ceil(lambda_1) rule over all of D2 ---------
    print("\n== regression witness: v1's ceil(lambda_1) rule on all of %d members ==" % len(codes))
    jc = I.VOCAB.index("spec_ceil")
    jf = I.VOCAB.index("spec_floor")
    wrong = []
    t0 = time.time()
    for i, code in enumerate(codes):
        adj, n = DB.g6_to_adj(code)
        if v1_rule_is_wrong(adj, n, int(MA[i, jf]) // SCALE, int(MA[i, jc]) // SCALE):
            wrong.append(code)
        if (i + 1) % 50000 == 0:
            print("   %d/%d  %.0fs" % (i + 1, len(codes), time.time() - t0), flush=True)
    by_n: Dict[str, int] = {}
    for c in wrong:
        key = str(ord(c[0]) - 63)
        by_n[key] = by_n.get(key, 0) + 1
    n8 = sum(v for k, v in by_n.items() if int(k) <= 8)
    print("   v1's rule is wrong on %d of %d members of D2  (by order: %s)"
          % (len(wrong), len(codes), by_n))
    print("   restricted to n <= 8 (v1's database D): %d wrong of 12,112 -- "
          "v1's own post-hoc audit found 19 %s"
          % (n8, "(REPRODUCED)" if n8 == 19 else "(DOES NOT MATCH)"))
    print("   first 5: %s" % wrong[:5])

    # --- third path: v1's own generator, on the n <= 8 slice both share -------
    v1cache = os.path.join(os.path.dirname(HERE), "gen", "data", "invariants_n2_n8.npz")
    v1g6 = os.path.join(os.path.dirname(HERE), "gen", "data", "connected_n2_n8.g6")
    v1_report: Dict[str, dict] = {}
    if os.path.exists(v1cache) and os.path.exists(v1g6):
        print("\n== third path: v1's generator (scripts/gen) on the shared n <= 8 slice ==")
        z = np.load(v1cache, allow_pickle=False)
        v1names = [str(x) for x in z["names"]]
        M1 = z["M"]                                   # v1 SCALE = 840
        with open(v1g6) as fh:
            v1codes = [ln.strip() for ln in fh if ln.strip()]
        v1codes.sort(key=lambda c: (ord(c[0]) - 63, c))
        idx1 = {c: i for i, c in enumerate(DB.canonical_list(v1codes))}
        head = [i for i, c in enumerate(codes) if ord(c[0]) - 63 <= 8]
        canon2 = DB.canonical_list([codes[i] for i in head])
        pairs = [(i2, idx1[c]) for i2, c in zip(head, canon2)]
        assert len(pairs) == len(v1codes) == 12112, "n<=8 slice does not line up"
        rows2 = np.array([p[0] for p in pairs])
        rows1 = np.array([p[1] for p in pairs])
        print("%-14s %s" % ("invariant", "disagreements with v1 over 12,112 graphs"))
        for k in I.VOCAB:
            if k not in v1names:
                continue
            a = MA[rows2, I.VOCAB.index(k)]           # SCALE = 2520
            c = M1[rows1, v1names.index(k)] * 3       # 840 -> 2520
            d = np.flatnonzero(a != c)
            v1_report[k] = {"disagreements": int(len(d)),
                            "examples_graph6_v2": [codes[int(rows2[t])] for t in d[:5]]}
            if len(d):
                print("%-14s %d   <-- v1 defect" % (k, len(d)))
        clean = [k for k, v in v1_report.items() if v["disagreements"] == 0]
        print("   %d of the %d shared invariants agree everywhere; disagreements only on: %s"
              % (len(clean), len(v1_report),
                 sorted(k for k, v in v1_report.items() if v["disagreements"])))

    payload = {
        "database": {"size": len(codes),
                     "definition": "every connected graph with 2 <= n <= 9, up to isomorphism",
                     "sha256_graph6_file": DB.sha256_db()},
        "vocabulary_size": len(I.VOCAB),
        "total_mismatches": int(total_mismatch),
        "per_invariant": report,
        "v1_generator_third_path_n_le_8": v1_report,
        "v1_spec_ceil_rule_regression": {
            "wrong_on": len(wrong), "of": len(codes), "by_order_n": by_n,
            "wrong_on_n_le_8": n8,
            "v1_reported_wrong_on_n_le_8": 19,
            "first_examples_graph6": wrong[:20],
            "note": "reproduction of the v1 defect recorded in METHOD v1.7 R4; "
                    "not part of the v2 vocabulary",
        },
        "passed": total_mismatch == 0,
    }
    os.makedirs(os.path.dirname(OK_PATH), exist_ok=True)
    with open(OK_PATH, "w") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")
    print("\nTOTAL MISMATCHES: %d  ->  %s" % (total_mismatch,
                                              "PASS" if total_mismatch == 0 else "FAIL"))
    print("wrote %s" % OK_PATH)
    return 0 if total_mismatch == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
