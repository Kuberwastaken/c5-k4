#!/usr/bin/env python3
"""A105210 audit: Cormier-Selfridge starts {1,393,412,668,932} pairwise non-merging.
   Run all five in parallel; check no shared term up to bound."""
import time
from sympy import factorint

def spf_sum(n):
    if n <= 1:
        return 0
    return sum(p for p in factorint(n) if p < n)

def run(start, cap):
    out = [None, start]
    cur = start
    while cur < cap:
        cur = cur + 1 + spf_sum(cur)
        out.append(cur)
    return out

t0 = time.time()
CAP = 2_000_000
seqs = {k: run(k, CAP) for k in [1, 393, 412, 668, 932]}
print(f"ran all five starts to >={CAP} ({time.time()-t0:.1f}s)")
for k, s in seqs.items():
    print(f"start {k}: {len(s)-1} terms, last={s[-1]}")

# head vs Lean tests for main sequence (393)
print("393 head:", seqs[393][1:6], "expect [393,528,545,660,682]")

# pairwise intersection below cap
import itertools
for j, k in itertools.combinations([1, 393, 412, 668, 932], 2):
    s1, s2 = set(seqs[j][1:]), set(seqs[k][1:])
    inter = s1 & s2
    if inter:
        print(f"MERGE between {j} and {k}: sample shared terms {sorted(inter)[:5]}")
    else:
        print(f"{j} vs {k}: disjoint below {CAP}")
