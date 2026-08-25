#!/usr/bin/env python3
"""A114216 audit: a(0)=0; a(n)=odd part of a(n-1)+prime(n).
   Question: is a(33900) the LAST term equal to 1?"""
import time
from sympy import isprime, nextprime

def gen(N):
    out = [0] * (N + 2)
    p = 2
    for n in range(1, N + 1):
        v = out[n - 1] + p
        while v % 2 == 0:
            v //= 2
        out[n] = v
        p = nextprime(p)
    return out

t0 = time.time()
N = 60000
seq = gen(N)
print(f"generated to n={N} ({time.time()-t0:.1f}s)")
ones = [n for n in range(1, N + 1) if seq[n] == 1]
last_one = max(ones)
print("a(33900)==1:", seq[33900] == 1)
print("count of ones:", len(ones), "last index with a=1:", last_one)
viol = [n for n in ones if n > 33900]
print("indices >33900 with a(n)=1 (crossing if any):", viol if viol else "NONE")
print("head vs Lean tests: a1..a5 =", seq[1:6], "expect [1,1,3,5,1]")
