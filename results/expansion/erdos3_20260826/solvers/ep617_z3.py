#!/usr/bin/env python
"""EP617 impl C: z3 SAT encoding via DIMACS.
Vars: x_{e,c} = edge e has color c (1-based). Constraints:
  ALO: per edge, >=1 color. AMO: pairwise <=1.
  Balance: for every (r+1)-set S and color k: OR_{e in S} x_{e,k}.
SAT <=> balanced coloring exists <=> erdos_617 fails at (r,n).
Usage: ep617_z3.py N R -> prints verdict + witness assignment if SAT."""
import subprocess, sys
from itertools import combinations

def encode(n, r):
    edges = list(combinations(range(n), 2))
    vid = {}
    nv = 0
    for i in range(len(edges)):
        for c in range(r):
            nv += 1
            vid[(i, c)] = nv
    cls = []
    for i in range(len(edges)):
        cls.append([vid[(i, c)] for c in range(r)])
        for c1 in range(r):
            for c2 in range(c1 + 1, r):
                cls.append([-vid[(i, c1)], -vid[(i, c2)]])
    ksets = [tuple(s) for s in combinations(range(n), r + 1)]
    ks_edges = [tuple(sorted(ei[tuple(sorted(p))] for p in combinations(s, 2))) for s in ksets]
    return edges, vid, cls, ks_edges

def main(n, r):
    edges = list(combinations(range(n), 2))
    global ei
    ei = {e: i for i, e in enumerate(edges)}
    edges2, vid, cls, ks_edges = encode(n, r)
    for S in ks_edges:
        for k in range(r):
            cls.append([vid[(e, k)] for e in S])
    nv = max(v for v in vid.values())
    dim = [f"p cnf {nv} {len(cls)}"]
    for c in cls:
        dim.append(" ".join(map(str, c)) + " 0")
    open("/tmp/ep617.cnf", "w").write("\n".join(dim))
    res = subprocess.run(["z3", "-dimacs", "/tmp/ep617.cnf"],
                         capture_output=True, text=True, timeout=1800)
    out = res.stdout.strip().splitlines()
    verdict = out[0]
    print(f"BAL({n},{r}): {verdict}")
    if verdict == "sat" and len(out) > 1:
        vals = list(map(int, out[1].split()))
        assign = {}
        for v in vals:
            if v < 0:
                continue
            for (e, c), vidv in vid.items():
                if vidv == v:
                    assign[e] = c
        # independent validation of the witness
        bad = 0
        for S in combinations(range(n), r + 1):
            cols = {assign[tuple(sorted(p))] for p in combinations(S, 2)}
            if len(cols) != r:
                bad += 1
        print(f"witness validated: {len(list(combinations(range(n), r+1)))-bad}/{len(list(combinations(range(n), r+1)))} sets balanced")
        print({edges[i]: c for i, c in sorted(assign.items())})

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
