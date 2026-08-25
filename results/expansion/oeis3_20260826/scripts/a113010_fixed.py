#!/usr/bin/env python3
"""A113010 audit: fixed points of d(n)^s(n) (digits count to digit-sum power).
   Claim: only 1 and 32."""
import time

def a(n):
    ds = 0
    x = n
    if x == 0:
        return 1
    nd = 0
    while x:
        x, r = divmod(x, 10)
        ds += r
        nd += 1
    return nd ** ds

t0 = time.time()
fix = []
N = 2_000_000
for n in range(1, N + 1):
    if a(n) == n:
        fix.append(n)
print(f"scanned 1..{N} ({time.time()-t0:.1f}s)")
print("fixed points:", fix)
print("beyond {1,32}:", [x for x in fix if x not in (1, 32)] or "NONE")

print("spot checks: a(32)=%d, a(1)=%d" % (a(32), a(1)))
