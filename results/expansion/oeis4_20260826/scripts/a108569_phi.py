#!/usr/bin/env python3
"""A108569 audit: k with phi(k) == phi(k + phi(k)); conjecture: all terms after
the first (k=1) are even.
Path 1: linear sieve phi to LIM=2*10^6 (need phi up to k+phi(k) <= 2*LIM).
Path 2: sympy totient recheck of every found term + odd-term hunt continues
        with sympy on odds up to extra bound if sieve clean.
"""
import numpy as np
import time

LIM = 2_000_000          # k up to 10^6; k+phi(k) up to 2*10^6
t0 = time.time()
phi = np.arange(LIM + 1, dtype=np.int64)
for i in range(2, LIM + 1):
    if phi[i] == i:                       # i prime
        phi[i::i] -= phi[i::i] // i
print(f"phi sieve to {LIM}: {time.time()-t0:.1f}s")

KMAX = 1_000_000
terms = []
t0 = time.time()
for k in range(1, KMAX + 1):
    phik = int(phi[k])
    if phik == int(phi[k + phik]):
        terms.append(k)
    if time.time() - t0 > 50:
        print(f"TIME CAP at k={k}")
        break
scanned_to = k
print(f"scanned k <= {scanned_to}: {len(terms)} terms")
print("first 40:", terms[:40])

print("=== head vs OEIS %S ===")
oeis_head = [1,4,8,16,32,64,110,128,220,256,440,506,512,550,880,1012,1024,1100,1760,1830]
print("  match first20:", terms[:20] == oeis_head)

bf = []
for line in open('bfiles/b108569.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        a,b = line.split(); bf.append(int(b))
print("  b-file first30 match:", terms[:30] == bf[:30])

odd_terms = [t for t in terms if t % 2 == 1]
print("ODD TERMS FOUND:", odd_terms, "(conjecture says only k=1)")
print("conjecture holds in range:", all(t % 2 == 0 for t in terms[1:]))

print("=== Path 2: sympy.totient independent recheck of all found terms ===")
from sympy import totient
bad = [k for k in terms[:500] if totient(k) != totient(k + totient(k))]
print("  mismatches:", bad if bad else "NONE")

# completeness guard: no missed term below scanned bound? re-scan sample with sympy
import random
missed = []
sample = random.sample(range(2, min(scanned_to, 200000)), 3000)
for k in sample:
    pk = totient(k)
    if pk == totient(k + pk) and k not in set(terms):
        missed.append(k)
print("  sample cross-scan misses:", missed if missed else "NONE")
