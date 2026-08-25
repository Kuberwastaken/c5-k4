#!/usr/bin/env python3
"""A109905 audit: greatest prime k(n-k)+1 over 1<=k<=n/2; zeros claimed exactly {1,6,30,54}."""
import time
from sympy import isprime

def a(n):
    best = 0
    for k in range(1, n // 2 + 1):
        v = k * (n - k) + 1
        if v > best and isprime(v):
            best = v
    return best

print("== head terms vs Lean tests ==")
for n, want in [(1,0),(2,2),(3,3),(4,5),(5,7)]:
    got = a(n)
    print(f"a({n})={got} expect {want} {'OK' if got==want else 'FAIL'}")

t0 = time.time()
zeros = []
N = 20000
for n in range(1, N + 1):
    if time.time() - t0 > 55:
        N = n
        break
    if a(n) == 0:
        zeros.append(n)
print(f"scanned n=1..{N-1} ({time.time()-t0:.1f}s)")
print("zeros found:", zeros)
known = [1, 6, 30, 54]
extra = [z for z in zeros if z not in known]
print("beyond known {1,6,30,54}:", extra if extra else "NONE -> bracket n<=%d" % (N-1))
