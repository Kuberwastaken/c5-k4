#!/usr/bin/env python3
"""A239957 audit: Sun's k^2+1 primitive root conjecture.
   Reading A (Lean): exists exact integer g=k^2+1 with 1<=g<p and order_p(g)=p-1.
   Reading B (residue): exists k with k^2+1 being a primitive root mod p
   (i.e., its RESIDUE has order p-1), no size constraint.
   Compare both over primes; any prime failing reading A while passing B pins
   the readings apart."""
import time
from sympy import isprime

def factorize(m):
    fs = {}
    d = 2
    while d * d <= m:
        while m % d == 0:
            fs[d] = fs.get(d, 0) + 1
            m //= d
        d += 1
    if m > 1:
        fs[m] = fs.get(m, 0) + 1
    return fs

def is_pr_mod(g, p, pfs):
    """order of g mod p equals p-1?"""
    g %= p
    if g == 0:
        return False
    for q in pfs:
        if pow(g, (p - 1) // q, p) == 1:
            return False
    return True

t0 = time.time()
failsA = []
both_ok = 0
primes = [p for p in range(2, 3000) if isprime(p)]
for p in primes:
    pfs = factorize(p - 1)
    okB = False
    okA = False
    for k in range(0, p):
        v = k * k + 1
        if is_pr_mod(v, p, pfs):
            okB = True
            if v < p:
                okA = True
                break
    if not okB:
        failsA.append((p, "NO-ROOT-EITHER"))
    elif not okA:
        failsA.append((p, "only-residue-root"))
    else:
        both_ok += 1
print(f"scanned {len(primes)} primes to {primes[-1]} ({time.time()-t0:.1f}s)")
sep = [f for f in failsA if f[1] == "only-residue-root"]
none_ = [f for f in failsA if f[1] == "NO-ROOT-EITHER"]
print("primes where only the RESIDUE reading witnesses:", sep[:10])
print("count:", len(sep))
print("primes failing BOTH readings:", none_[:10])
print("reading-A OK count:", both_ok)
