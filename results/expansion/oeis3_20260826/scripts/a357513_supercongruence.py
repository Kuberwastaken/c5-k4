#!/usr/bin/env python3
"""A357513 audit: exact supercongruence check
   a(p-1) == 0 mod p^4 for primes p>=3 except p=7 ("proved by AlphaProof", sorry body).
   Independent path 2: compute numerator via Fraction then reduce mod p^4.
"""
from sympy import binomial, isprime
from fractions import Fraction

def u_m_exact(m, n):
    """numerator of sum_{k=1}^n C(n,k)^2 C(n+k,k)^2 / k^(2m+1), exact."""
    tot = Fraction(0)
    for k in range(1, n + 1):
        c1 = binomial(n, k)
        c2 = binomial(n + k, k)
        tot += Fraction(c1 * c1 * c2 * c2, k ** (2 * m + 1))
    return tot.numerator

def u_m_mod(m, n, mod):
    """path 2: all-modular evaluation with modular inverses (valid when gcd(k,mod)=1
       for all k<=n; we use it only when mod=p^4, p>n)."""
    tot = 0
    for k in range(1, n + 1):
        c1 = binomial(n, k) % mod
        c2 = binomial(n + k, k) % mod
        inv = pow(k, -1, mod)
        tot = (tot + c1 * c1 % mod * c2 % mod * c2 % mod * pow(inv, 2 * m + 1, mod)) % mod
    return tot

print("== path 1: exact Fractions, numerator mod p^4 ==")
primes = [p for p in range(3, 60) if isprime(p)]
for p in primes:
    val = u_m_exact(1, p - 1) % (p ** 4)
    flag = "OK(zero)" if val == 0 else "NONZERO"
    mark = " <-- exception" if p == 7 else ""
    print(f"p={p}: a(p-1) mod p^4 = {val} {flag}{mark}")

print("\n== path 2: fully modular recomputation (cross-check) ==")
for p in [3, 5, 7, 11, 13, 17]:
    print(f"p={p}: modular u(1,p-1) mod p^4 = {u_m_mod(1, p-1, p**4)}")

print("\n== negative control: composites must NOT generally vanish ==")
import sympy
comps = [c for c in range(4, 30) if not sympy.isprime(c)]
bad = []
for n in comps:
    val = u_m_exact(1, n - 1) % (n ** 2)   # conjecture only speaks of primes at p^4
    if val == 0:
        bad.append(n)
print("composites with u(1,n-1)==0 mod n^2 (informational):", bad)

print("\n== general_supercongruence spot-checks: u(m,p-1) mod p^4 ==")
for m in [0, 2, 3]:
    row = []
    for p in [3, 5, 7, 11, 13]:
        v = u_m_exact(m, p - 1) % (p ** 4)
        row.append(f"p={p}:{'0' if v==0 else 'X'}")
    print(f"m={m}: " + " ".join(row))
