#!/usr/bin/env python3
"""A113250/A113252/A113255 audit: odd-index terms of linear recurrences are perfect squares."""
import sys
from sympy import perfect_power, integer_nthroot

def gen(init, c3, c4, N):
    out = list(init)
    while len(out) <= N:
        n = len(out)
        out.append(c3 * -out[n - 1] * 4 // 4)  # placeholder
    return out

def gen250(N):
    a = [-1, 4, 32, 64]
    while len(a) <= N:
        n = len(a)
        a.append(-4 * a[n-1] + 64 * a[n-3] + 256 * a[n-4])
    return a

def gen252(N):
    a = [-1, 4, 92, 784]
    while len(a) <= N:
        n = len(a)
        a.append(-4 * a[n-1] + 144 * a[n-3] + 1296 * a[n-4])
    return a

def gen255(N):
    a = [-1, 4, 227, 5329]
    while len(a) <= N:
        n = len(a)
        a.append(-4 * a[n-1] + 324 * a[n-3] + 6561 * a[n-4])
    return a

import time
for name, fn, m in [("A113250", gen250, 4), ("A113252", gen252, 6), ("A113255", gen255, 9)]:
    t0 = time.time()
    N = 400
    seq = fn(N)
    bad = []
    for n in range(0, N + 1, 2):          # odd indices 2k+1
        v = seq[n + 1]
        if v >= 0:
            r, ok = integer_nthroot(v, 2)
            sq = ok
        else:
            sq = False
        if not sq:
            bad.append((n + 1, v))
    print(f"{name} (m={m}): odd-index nonsquares up to index {N}:",
          bad[:5] if bad else f"NONE ({time.time()-t0:.1f}s)")
