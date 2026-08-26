#!/usr/bin/env python
"""EP600/EP80 joint solver.

e(n,r): minimal e such that every n-vertex graph with >=e edges, every edge in a triangle,
has some edge in >=r triangles.
  e(n,r) = 1 + max{|E(G)| : G hyp-satisfying, maxbook(G) <= r-1}   (0 if no hyp graph)

f_c(n): minimal bookNumber among graphs with |E|>=ceil(c n^2) and every edge in a triangle;
        0 if none exists (matches sInf empty = 0 in Nat).
One pass over all graphs computes both. Impl 1: canonical vertex-addition bitmasks."""
import sys
from fractions import Fraction

def gen_graphs(n):
    masks = [0] * n
    def rec(v):
        if v == n:
            yield tuple(masks)
            return
        for sub in range(1 << v):
            m = 0
            for u in range(v):
                if sub >> u & 1:
                    m |= 1 << u
            masks[v] = m
            yield from rec(v + 1)
    return rec(0)

def analyze(masks, n):
    adj = []
    for v in range(n):
        col = 0
        for u in range(n):
            if masks[u] >> v & 1:
                col |= 1 << u
        adj.append(masks[v] | col)
    edges = [(u, v) for u in range(n) for v in range(u + 1, n)
             if (adj[u] >> v) & 1]
    ne = len(edges)
    maxbook = 0
    minbook = 0  # 0 with no edges = hypothesis satisfied vacuously
    if edges:
        minbook = ne
        for u, v in edges:
            b = (adj[u] & adj[v]).bit_count()
            if b > maxbook:
                maxbook = b
            if b < minbook:
                minbook = b
    return ne, maxbook, minbook

def tables(ns, cs):
    eres = {}   # (n,r) -> e(n,r)
    fres = {}   # (n,c) -> f_c(n)
    for n in ns:
        # bad[r]: max |E| among hyp-graphs with maxbook <= r-1 ; index by r
        bad = {}
        adm = {}  # c -> min bookNumber among admissible
        thresh = {c: -(-Fraction(c).limit_denominator(1000) * n * n) for c in []}
        for masks in gen_graphs(n):
            ne, mb, mb1 = analyze(masks, n)
            if mb1 >= 1 or ne == 0:  # hypothesis: EVERY edge in a triangle (vacuous if none)
                for r in (2, 3, 4, 5):
                    if mb < r:
                        bad[r] = max(bad.get(r, -1), ne)
                for c in cs:
                    if Fraction(str(c)) * n * n <= ne:
                        cur = adm.get(c)
                        if cur is None or mb < cur:
                            adm[c] = mb
        for r in (2, 3, 4, 5):
            eres[(n, r)] = bad.get(r, -1) + 1
        for c in cs:
            fres[(n, c)] = adm.get(c, 0)
    return eres, fres

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")]
    cs = [float(x) for x in sys.argv[2].split(",")]
    eres, fres = tables(ns, cs)
    print("== e(n,r) ==")
    for n in ns:
        row = [f"e({n},{r})={eres[(n,r)]}" for r in (2, 3, 4, 5)]
        print("  ".join(row))
    print("differences e(n,3)-e(n,2), e(n,4)-e(n,3):")
    for n in ns:
        print(f"  n={n}: {eres[(n,3)]-eres[(n,2)]} {eres[(n,4)]-eres[(n,3)]}")
    print("== f_c(n) ==")
    for n in ns:
        print(f"  n={n}: " + "  ".join(f"f_{c}={fres[(n,c)]}" for c in cs))
    print("== duality check: (f_c(n) >= r) <=> (e(n,r) <= c*n*n) for each n,c,r in 2..5 ==")
    ok = True
    for n in ns:
        for c in cs:
            cn2 = Fraction(str(c)) * n * n
            for r in (2, 3, 4, 5):
                lhs = fres[(n, c)] >= r
                rhs = eres[(n, r)] <= cn2
                if lhs != rhs:
                    ok = False
                    print(f"  MISMATCH n={n} c={c} r={r}: f>=r is {lhs}, e<=cn2 is {rhs}"
                          f" (f={fres[(n,c)]}, e={eres[(n,r)]}, cn2={float(cn2)})")
    print("duality holds everywhere:" , ok)
