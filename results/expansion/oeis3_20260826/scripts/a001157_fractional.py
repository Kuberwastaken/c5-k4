#!/usr/bin/env python3
"""A001157 (inventory id 1157) audit: Sun's Oct 15 2015 conjecture —
   for each k>=2 the fractional parts of sigma_k(n)/n^k are pairwise distinct over n>=1.
   Any collision (k, n1, n2) is a CROSSING candidate against both Sun and Lean."""
from fractions import Fraction
import time

def sigma_k_frac(k, n):
    s = 0
    d = 1
    i = 1
    while i * i <= n:
        if n % i == 0:
            j = n // i
            s += i ** (-k) if False else Fraction(1, i ** k)
            if j != i:
                s += Fraction(1, j ** k)
        i += 1
    return s - 1  # subtract 1 to keep fractions small; fractional part unaffected

def frac(f):
    return f - int(f)

t0 = time.time()
print("== collision hunt: fixed k, all pairs n1<n2 <= N ==")
K = 6          # k = 2..7
N = 3000       # per-k bound; restart budget below keeps total under cap
collisions = []
for k in range(2, K + 1):
    if time.time() - t0 > 55:
        print("time cap")
        break
    seen = {}
    hit_k = None
    for n in range(1, N + 1):
        f = frac(sigma_k_frac(k, n))
        if f in seen:
            hit_k = (seen[f], n)
            collisions.append((k, seen[f], n))
            break
        seen[f] = n
    print(f"k={k}: no collision among n<=N" if not hit_k else f"k={k}: COLLISION {hit_k}")
    if hit_k:
        break

print(f"({time.time()-t0:.1f}s)")
print("collisions found:", collisions if collisions else "NONE")

print("\n== spot values vs OEIS-style expectations ==")
# sanity: sigma_2(2)/4 = 5/4 frac 1/4 etc.
for n in [1, 2, 3, 4, 6]:
    print(f"n={n}: frac(sigma_2(n)/n^2) = {frac(sigma_k_frac(2,n))}")
