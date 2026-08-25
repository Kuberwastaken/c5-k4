#!/usr/bin/env python3
"""A104320 audit: number of zero ternary digits of 2^n.
   Sloane conjecture (Lean research-open): a(n)>0 for ALL n>15.
   Any n>15 with a(n)=0 is a CROSSING against the formalization."""
import sys, time

def ternary_zeros(x):
    d = []
    while x:
        x, r = divmod(x, 3)
        d.append(r)
    return d.count(0)

print("== head terms vs published ==")
pub = None
try:
    vals = []
    for line in open("../bfiles/bA104320.txt"):
        if line.startswith("#") or not line.strip():
            continue
        i, v = line.split()
        vals.append((int(i), int(v)))
    pub = vals
    print("b-file entries:", len(pub), "head:", vals[:12])
except FileNotFoundError:
    print("no b-file")

t0 = time.time()
bad = []
N = 4000
for n in range(0, N):
    if time.time() - t0 > 55:
        N = n
        break
    z = ternary_zeros(2 ** n)
    if n > 15 and z == 0:
        bad.append(n)
print(f"scanned n=0..{N-1} ({time.time()-t0:.1f}s)")
print("violations of a(n)>0 for n>15:", bad if bad else "NONE")
if pub:
    mism = [(i, v, ternary_zeros(2**i)) for i, v in pub[:200] if ternary_zeros(2**i) != v]
    print("b-file mismatches in first 200:", mism if mism else "none")
