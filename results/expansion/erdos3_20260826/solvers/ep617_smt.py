#!/usr/bin/env python
"""EP617 impl C2: SMT-LIB2 encoding for z3 with native symmetry breaking.
Vars: (declare-const c_i Int) for edge i, domain {0..r-1} via assertions.
Balance: for every (r+1)-set S, color k: (or (=> (= c_e k) true) ...) expressed as
  (or (= c_e0 k) (= c_e1 k) ...).
Symmetry breaking (first-occurrence along edge index order):
  c_0 = 0 ; c_i <= 1 + max(c_j, j<i)  encoded via running max aux var m_i:
  m_0 = 0 ; m_i = max(m_{i-1}, c_{i-1}); assert c_i <= m_i + 1.
Usage: ep617_smt.py N R [timeout_s] -> prints sat/unsat."""
import subprocess, sys
from itertools import combinations

def main(n, r, tmo=1800):
    edges = list(combinations(range(n), 2))
    ei = {e: i for i, e in enumerate(edges)}
    m = len(edges)
    L = []
    L.append("(set-logic QF_LIA)")
    for i in range(m):
        L.append(f"(declare-const c{i} Int)")
    for i in range(m):
        L.append(f"(assert (and (>= c{i} 0) (<= c{i} {r-1})))")
    L.append("(assert (= c0 0))")
    # running max
    L.append("(declare-const mx0 Int)")
    L.append("(assert (= mx0 0))")
    for i in range(1, m):
        L.append(f"(declare-const mx{i} Int)")
        L.append(f"(assert (= mx{i} (ite (> mx{i-1} c{i-1}) mx{i-1} c{i-1})))")
        L.append(f"(assert (<= c{i} (+ mx{i} 1)))")
    ks_edges = []
    for s in combinations(range(n), r + 1):
        ks_edges.append(tuple(ei[tuple(sorted(p))] for p in combinations(s, 2)))
    for S in ks_edges:
        for k in range(r):
            L.append("(assert (or " + " ".join(f"(= c{e} {k})" for e in S) + "))")
    L.append("(check-sat)")
    L.append("(get-model)")
    open("/tmp/ep617.smt2", "w").write("\n".join(L))
    try:
        res = subprocess.run(["z3", "-smt2", "/tmp/ep617.smt2"],
                             capture_output=True, text=True, timeout=tmo)
        out = res.stdout.strip().splitlines()
        verdict = out[0] if out else "NO-OUTPUT"
        print(f"BAL({n},{r}): {verdict}")
        if verdict == "sat":
            vals = {}
            for line in out:
                if line.startswith(("(define-fun c", "(define-fun mx")):
                    parts = line.split()
                    if parts[1][0] == "c":
                        idx = int(parts[1][1:])
                        v = parts[-1].rstrip(")").strip()
                        vals[idx] = int(v)
            bad = 0
            tot = 0
            for S in combinations(range(n), r + 1):
                tot += 1
                cols = {vals[ei[tuple(sorted(p))]] for p in combinations(S, 2)}
                if len(cols) != r:
                    bad += 1
            print(f"witness validated: {tot-bad}/{tot} sets balanced")
            print({edges[i]: c for i, c in sorted(vals.items())})
    except subprocess.TimeoutExpired:
        print(f"BAL({n},{r}): TIMEOUT after {tmo}s")

if __name__ == "__main__":
    n, r = int(sys.argv[1]), int(sys.argv[2])
    tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 1800
    main(n, r, tmo)
