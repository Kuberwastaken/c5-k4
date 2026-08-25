#!/usr/bin/env python3
"""A103662 audit: smallest base b>1 with b^n zeroless (no digit 0); a(n)=b^n.
   Lean conjectures: (i) only finitely many n admit such b; (ii) n=40 admits none."""
import time
from sympy import isprime

def zeroless(x):
    s = str(x)
    return "0" not in s

def least_base(n, cap=4000):
    for b in range(2, cap):
        if zeroless(b ** n):
            return b
    return None

t0 = time.time()
print("== head terms vs published ==")
try:
    pub = {}
    for line in open("/Users/kuber.mehta/Personal-Projects/c5-k4/results/expansion/oeis3_20260826/bfiles/b103662.txt"):
        if line.startswith("#") or not line.strip(): continue
        i, v = line.split(); pub[int(i)] = int(v)
    for n in sorted(pub)[:8]:
        b = least_base(n)
        val = b ** n if b else 0
        print(f"n={n}: least base={b} -> a={val} published={pub[n]} {'OK' if val==pub[n] else 'FAIL'}")
except FileNotFoundError:
    for n in [1,2,3]:
        print(f"n={n}: base={least_base(n)}")

print("\n== n=40 hunt (Lean conjecture.variants.a_40: no valid base) ==")
t0 = time.time()
found = None
B = 20000
for b in range(2, B):
    v = b ** 40
    if not zeroless(v):
        continue
    found = b
    break
print(f"bases scanned to {B} ({time.time()-t0:.1f}s): first zeroless 40th power base:", found)

print("\n== which small n have bases at all ==")
t0 = time.time()
have = []
for n in range(1, 60):
    b = least_base(n, cap=600)
    if b:
        have.append((n, b))
print("n with zeroless power (base<=600):", have[:20])
