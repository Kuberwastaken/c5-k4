#!/usr/bin/env python3
"""A034693 (inventory 34693) audit: smallest k with n*k+1 prime.
   Verify solved counterexample claim (n=19, k<1+19^0.74 all composite);
   verify exists_k conjecture to a bound; compute a(n) head vs b-file."""
import time
from sympy import isprime

def least_k(n, cap=100000):
    for k in range(1, cap):
        if isprime(n * k + 1):
            return k
    return None

print("== head values vs Lean tests ==")
for n, want in [(1,1),(2,1),(3,2),(7,4)]:
    got = least_k(n)
    print(f"a({n})={got} expect {want} {'OK' if got==want else 'FAIL'}")

print("\n== the SOLVED claim: exponent .74 fails at n=19 ==")
# bound: 1 + 19^0.74 ; all integer k < that give composite 19k+1
import math
bound = 1 + 19 ** 0.74
print(f"numeric bound = {bound:.4f}; so k ranges over 0..{math.ceil(bound)-1}")
allc = all(not isprime(19 * k + 1) for k in range(0, math.ceil(bound)))
print("all 19k+1 composite in range:", allc)
vals = [(k, 19*k+1, "prime" if isprime(19*k+1) else f"composite={sorted(__import__('sympy').factorint(19*k+1))}") for k in range(0, math.ceil(bound))]
for k, v, s in vals:
    print(f"  k={k}: {v} {s}")

print("\n== exists_k: least prime 1 mod n is < n^2? scan n<=5000 ==")
t0 = time.time()
bad = []
for n in range(2, 5001):
    if time.time() - t0 > 50:
        print("cap", n)
        break
    lk = least_k(n, cap=max(100, n))
    if lk is None or lk >= n:
        bad.append(n)
print(f"scanned n<= {n} ({time.time()-t0:.1f}s); violations of exists_k:", bad if bad else "NONE")

print("\n== exists_k_stronger spot check: k < 1+n^.75 ==")
t0 = time.time()
viol = []
for n in range(2, 20000):
    if time.time() - t0 > 20:
        break
    lk = least_k(n, cap=max(100, n))
    if lk is not None and not (lk < 1 + n ** 0.75):
        viol.append(n)
print(f"n scanned to {n}: violations of stronger bound:", viol[:5] if viol else "NONE")
