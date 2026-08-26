#!/usr/bin/env python3
"""A105720 audit: a(n) = sum of primes p_n..p_{2n}; squares iff n in {3,6,4072}?
Path 1: own numpy sieve to p_{2*Nmax}, sliding-window sums, isqrt square test.
Path 2: sympy primerange independent term generation for heads + spot windows.
Verify OEIS claims: a(3)=6^2, a(6)=13^2, a(4072)=15735^2; prime-at-n list.
"""
import numpy as np
from math import isqrt
import time
import sympy

NMAX = 20000                      # audit n up to NMAX -> need primes up to p_(2*NMAX)
# upper bound for p_m: m ln m + m lnln m for m=40000 ~ 40000*(10.60+2.35)=518k; use 600k
PIG = 600000
t0 = time.time()
sieve = np.ones(PIG + 1, dtype=bool)
sieve[:2] = False
for i in range(2, int(PIG**.5) + 1):
    if sieve[i]:
        sieve[i*i::i] = False
primes = np.nonzero(sieve)[0]
assert len(primes) > 2 * NMAX + 1, f"need {2*NMAX} primes, have {len(primes)}"
print(f"primes to {PIG}: {len(primes)} ({time.time()-t0:.1f}s)")

p = primes.astype(np.int64)
# prefix sums
cs = np.concatenate([[0], np.cumsum(p)])
def a_path1(n):
    # sum_{k=n..2n} p_k (1-indexed) = cs[2n] - cs[n-1]
    return int(cs[2*n] - cs[n - 1])

print("=== head vs OEIS %S ===")
head = [a_path1(n) for n in range(1, 20)]
print(" ", head)
print("  match:", head == [5,15,36,67,112,169,240,323,424,539,662,803,964,1133,1312,1523,1746,1987,2246])

print("=== claimed squares ===")
for n, root in ((3, 6), (6, 13), (4072, 15735)):
    v = a_path1(n)
    print(f"  a({n}) = {v} = {root}^2? {v == root*root}")

print("=== Path 2: sympy independent recompute (heads + random windows) ===")
ok = True
for n in list(range(1, 30)) + [100, 777, 4072, 9999, 15000]:
    pr = list(sympy.primerange(1, 600000))
    s = sum(pr[n-1:2*n])
    if s != a_path1(n):
        ok = False
        print(f"  MISMATCH at n={n}")
print("  path2 agreement:", ok)

print(f"=== SQUARE HUNT n=1..{NMAX} (cap 60 s) ===")
sq = []
t0 = time.time()
for n in range(1, NMAX + 1):
    v = a_path1(n)
    r = isqrt(v)
    if r*r == v:
        sq.append((n, r))
    if time.time() - t0 > 55:
        print(f"  time cap at n={n}")
        break
print(f"  scanned n<= {n}; squares found: {sq}")

print("=== prime-at-n spot check (%C: n=1,4,16,18,22 -> 5,67,1523,1987,3119) ===")
for n, val in ((1,5),(4,67),(16,1523),(18,1987),(22,3119),(36,9323)):
    print(f"  n={n}: a={a_path1(n)} expect {val} {'OK' if a_path1(n)==val else 'FAIL'}")
