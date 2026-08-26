#!/usr/bin/env python3
"""A114137 audit: a(n) = first odd semiprime > 2^n minus 2^n.
Lean tests: a_1=7,a_2=5,a_3=1,a_4=5,a_5=1 vs OEIS b-file (offset 0: 8,7,5,1,...).
conjecture1: 'does 1 occur infinitely often?' => answer(sorry) iff Infinite set.
conjecture2: 'does every odd number occur?'
Both infinitary => bounded numeric evidence ONLY (HOLD_NUMERIC labels):
compute a(n) for n<=140 by scanning odd candidates above 2^n with factorint.
"""
from sympy import factorint
import time

def is_odd_semiprime(m):
    if m % 2 == 0:
        return False
    f = factorint(m)
    return sum(f.values()) == 2

def next_gap(n, cap=10**7):
    m = 1 << n
    s = m + 1 if m % 2 == 0 else m + 2   # smallest odd candidate > m
    while s - m <= cap:
        if is_odd_semiprime(s):
            return s - m
        s += 2
    return None

print("=== head n=0..12 ===")
t0 = time.time()
vals = {}
for n in range(0, 13):
    vals[n] = next_gap(n)
print(" ", [vals[n] for n in range(13)])
bf = []
for line in open('bfiles/b114137.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        k,v = line.split(); bf.append((int(k), int(v)))
mine = [(k, vals[k]) for k,_ in bf[:13]]
print("  b-file:", bf[:13])
print("  match:", mine == bf[:13])

print("=== Lean tests a_1..a_5 = 7,5,1,5,1 ===")
print("  ", [vals[1], vals[2], vals[3], vals[4], vals[5]])

print("=== scan n=0..150 (cap 55 s) ===")
res = {}
t0 = time.time()
last_n = None
for n in range(0, 151):
    g = next_gap(n)
    if g is None:
        print(f"  cap exceeded at n={n}")
        break
    res[n] = g
    last_n = n
    if time.time() - t0 > 50:
        break
print(f"  computed n<= {last_n}")
ones = [n for n,g in res.items() if g == 1]
odds_seen = sorted(set(res.values()))
all_odd = set(range(1, max(res.values())+1, 2))
missing = sorted(all_odd - set(res.values()))
import collections
dist = collections.Counter(res.values())
print(f"  gaps==1 count: {len(ones)} occurrences at n={ones[:15]}...")
print(f"  distinct gap values seen ({len(odds_seen)}): {odds_seen[:40]}")
print(f"  odd values <= max-gap NOT yet seen: {missing[:20]}")
print("  HOLD_NUMERIC: both conjectures infinitary; evidence-only")
