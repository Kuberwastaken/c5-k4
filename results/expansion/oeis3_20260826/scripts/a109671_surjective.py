#!/usr/bin/env python3
"""A109671 audit: a(1)=1, a(2n)=a(n), odd: |a(2n+1)-a(2n-1)|=a(n) smallest positive.
   Conjecture: sequence contains every positive integer."""
import time
from functools import lru_cache

N = 4_000_000
a = [0] * (N + 1)
if N >= 1:
    a[1] = 1
t0 = time.time()
for n in range(2, N + 1):
    if n % 2 == 0:
        a[n] = a[n // 2]
    else:
        prev = a[n - 2]
        mid = a[(n - 1) // 2]
        a[n] = prev - mid if prev > mid else prev + mid

print(f"built to {N} ({time.time()-t0:.1f}s)")
print("head:", a[1:20])
seen = set(x for x in a[1:] if x)
mx = max(seen)
missing = [m for m in range(1, min(mx, 2000) + 1) if m not in seen]
print("max value seen:", mx, "distinct count:", len(seen))
print("positive integers <=2000 never appearing:", missing[:20] if missing else "NONE")
