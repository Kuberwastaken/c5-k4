#!/usr/bin/env python3
"""A108301 audit + repair development: digital sums of Fermat numbers F_n=2^(2^n)+1.
   Textbook-sorry claim: a(0),a(1),a(5),a(6),a(7),a(11) are prime.
   Path 1: str-digit summation. Path 2: chunked divmod base-10^k extraction."""
import sys
import time
sys.set_int_max_str_digits(20_000_000)
from sympy import isprime

def digitsum_str(x):
    return sum(map(int, str(x)))

def digitsum_chunk(x, k=9):
    """Independent path: repeated divmod by 10^k, sum digits of remainders."""
    mod = 10 ** k
    s = 0
    while x:
        x, r = divmod(x, mod)
        while r:
            r, d = divmod(r, 10)
            s += d
    return s

def fermat(n):
    return 2 ** (2 ** n) + 1

print("== paths agree + published head ==")
pub_head = {0: 3, 1: 5, 2: 8, 3: 14, 4: 26}
for n in range(0, 6):
    v1, v2 = digitsum_str(fermat(n)), digitsum_chunk(fermat(n))
    print(f"a({n})={v1} paths_agree={v1==v2} matches_pub={v1==pub_head.get(n,v1)}")

print("\n== six claimed prime values ==")
claims = [0, 1, 5, 6, 7, 11]
results = {}
for n in claims:
    ds = digitsum_str(fermat(n))
    pr = isprime(ds)
    results[n] = (ds, pr)
    print(f"a({n}) = {ds} -> prime? {pr}")
print("ALL SIX CONJUNCTS VERIFY:", all(pr for _, pr in results.values()))

print("\n== composite context values ==")
for n in [2, 3, 4, 8, 9]:
    ds = digitsum_str(fermat(n))
    print(f"a({n}) = {ds} prime? {isprime(ds)}")

print("\n== hunt beyond n=11 within cap ==")
t0 = time.time()
found = []
scanned = []
for n in range(12, 40):
    if time.time() - t0 > 50:
        break
    ds = digitsum_str(fermat(n))
    scanned.append(n)
    if isprime(ds):
        found.append((n, ds))
print(f"scanned n=12..{scanned[-1] if scanned else '?'} ({time.time()-t0:.1f}s)")
print("primes found beyond n=11:", found if found else "NONE")
