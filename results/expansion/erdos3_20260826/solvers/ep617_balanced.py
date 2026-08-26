#!/usr/bin/env python
"""EP617: exhaustive search for 'balanced' r-colorings of K_n in which EVERY (r+1)-subset
of vertices sees all r colors on its induced edges (negation of erdos_617's conclusion).
BAL(n,r) SAT <=> erdos_617 FAILS at (r,n); UNSAT <=> conjecture holds at (r,n).

DFS over edges with per-(r+1)-set seen-mask forward checking.
Anchors: BAL(4,2)&BAL(5,2) SAT (C4 resp. C5 2-colorings), BAL(6,2) UNSAT (R(3,3)=6).
"""
import sys, time
from itertools import combinations

def solve(n, r, node_cap=50_000_000, deadline=None):
    edges = list(combinations(range(n), 2))
    ei = {e: i for i, e in enumerate(edges)}
    m = len(edges)
    ksets = [tuple(s) for s in combinations(range(n), r + 1)]
    # for each (r+1)-set: edge indices of its clique
    ks_edges = [tuple(ei[tuple(sorted(p))] for p in combinations(s, 2)) for s in ksets]
    full = (1 << r) - 1
    color = [-1] * m

    # edge processing order: keep lex order (closes sets reasonably early)
    order = list(range(m))
    pos_of = [0] * m
    for pos, eidx in enumerate(order):
        pos_of[eidx] = pos

    # for incremental updates: sets containing each edge
    sets_of_edge = [[] for _ in range(m)]
    for si, elist in enumerate(ks_edges):
        for x in elist:
            sets_of_edge[x].append(si)

    nodes = 0
    stack = []  # (edge_pos, color_tried)

    def feasible_from(pos, seen, uncol):
        # called after coloring edge at pos-1; checks affected sets
        x = order[pos - 1]
        for si in sets_of_edge[x]:
            sm = seen[si]
            if uncol[si] == 0:
                if sm != full:
                    return False
            else:
                if bin(sm).count("1") + uncol[si] < r:
                    return False
        return True

    def rec(pos, seen, uncol):
        nonlocal nodes
        if pos == m:
            return True
        nodes += 1
        if nodes > node_cap or (deadline and time.time() > deadline):
            raise TimeoutError
        x = order[pos]
        for cval in range(r):
            color[x] = cval
            changed = []
            ok = True
            for si in sets_of_edge[x]:
                changed.append((si, seen[si], uncol[si]))
                seen[si] |= 1 << cval
                uncol[si] -= 1
                if uncol[si] == 0:
                    if seen[si] != full:
                        ok = False
                        # don't break: keep bookkeeping consistent for undo
                elif bin(seen[si]).count("1") + uncol[si] < r:
                    ok = False
            if ok and rec(pos + 1, seen, uncol):
                return True
            for si, sm, uc in changed:
                seen[si] = sm
                uncol[si] = uc
            color[x] = -1
        return False

    seen = [0] * len(ksets)
    uncol = [len(el) for el in ks_edges]
    # symmetry break: edge 0 gets color 0 (color-permutation class rep)
    x0 = order[0]
    color[x0] = 0
    for si in sets_of_edge[x0]:
        seen[si] |= 1
        uncol[si] -= 1
    try:
        sat = rec(1, seen, uncol)
        return (("SAT" if sat else "UNSAT"), color, nodes)
    except TimeoutError:
        return ("TIMEOUT", None, nodes)

if __name__ == "__main__":
    n, r = int(sys.argv[1]), int(sys.argv[2])
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 50_000_000
    t0 = time.time()
    res, col, nodes = solve(n, r, node_cap=cap, deadline=t0 + 300)
    print(f"BAL({n},{r}): {res}  nodes={nodes}  time={time.time()-t0:.1f}s")
    if res == "SAT":
        es = list(combinations(range(n), 2))
        print("witness coloring:", {es[i]: col[i] for i in range(len(es))})
