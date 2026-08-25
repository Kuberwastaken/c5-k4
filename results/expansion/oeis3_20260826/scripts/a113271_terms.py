#!/usr/bin/env python3
"""A113271 audit: exact terms by two independent paths + prime hunt (60s caps)."""
import time
from sympy import isprime, factorint

# Path 1: Lean formula a(n) = sum_{i=0}^{n} 2^(i * 2^(n-i))
def a_lean(n):
    return sum(2 ** (i * 2 ** (n - i)) for i in range(n + 1))

# Path 2: OEIS %%e expansion form a(n) = sum_{k=0}^{n} (2^k)^(2^(n-k)) -- algebraically
# same but computed via pow towers without sharing intermediate code shape
def a_oeis(n):
    total = 0
    for k in range(n + 1):
        base = 2 ** k
        total += base ** (2 ** (n - k))
    return total

published = [1, 3, 9, 41, 593, 135457, 8606778433,
             36893769626691833985]
print("== head-term reproduction (paths 1 & 2 vs published %S/%T) ==")
ok = True
for n, p in enumerate(published):
    v1, v2 = a_lean(n), a_oeis(n)
    tag = "OK" if v1 == v2 == p else "MISMATCH"
    ok &= (tag == "OK")
    print(f"a({n}): path1={v1==p} path2={v2==p} {tag}")
print("all head terms reproduced:", ok)

print("\n== the two conflicting claims ==")
print("543 factorization:", factorint(543), "-> prime?", isprime(543))
print("a(5) =", a_lean(5))
print("a(5) factorization:", factorint(a_lean(5)), "-> prime?", isprime(a_lean(5)))
print("is 543 a term anywhere in published head?", 543 in published)

print("\n== next-prime hunt (conjecture1: sInf{n>4 | a(n) prime}) ==")
t0 = time.time()
for n in range(5, 12):
    if time.time() - t0 > 55:
        print(f"time cap reached before n={n}")
        break
    t1 = time.time()
    v = a_lean(n)
    d = len(str(v))
    p = isprime(v)
    print(f"n={n}: digits={d} prime={p} ({time.time()-t1:.1f}s)")
    if not p:
        f = None
        if d <= 25:
            f = factorint(v)
            print(f"   factors: {f}")
