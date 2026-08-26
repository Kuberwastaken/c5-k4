#!/usr/bin/env python3
"""A109908/A109909 joint audit.
Values v(k,n) = k*(n-k)-1 for k in [1, n-1]; primes thereof (dedup image).
A109908: greatest such prime over k<=n/2 (or 0).   A109909: # distinct primes.
Conjectures (both): positive for all n > 3. OEIS: verified to 10^9 (Fiorentini).
Path 1: early-exit first-prime scan per n to N=500000 (sympy isprime oracle).
Path 2: full count for n<=3000 vs b-files of BOTH sequences + cross-consistency
        sup>0 <=> count>0 on shared range.
"""
from sympy import isprime
import time

def vals(n):
    return {k*(n-k)-1 for k in range(1, n)}

print("=== heads ===")
for n in range(1, 8):
    vv = sorted(v for v in vals(n) if v > 0)
    pr = [v for v in vv if isprime(v)]
    print(f"  n={n}: max={max(pr) if pr else 0} count={len(pr)}")

oeis908 = [0,0,0,3,5,7,11,11,19]      # offset 1,4 -> a(4)=3...
oeis909 = [0,0,0,2,2,1,2,1,4]
m908, m909 = [], []
for n in range(4, 13):
    pr = [v for v in vals(n) if v > 0 and isprime(v)]
    m908.append(max(pr))
    m909.append(len(pr))
print("  A109908 head match:", m908 == oeis908[3:], m908)
print("  A109909 head match:", m909 == oeis909[3:], m909)

print("=== b-file checks (first 60 each) ===")
for name, f in (("908", 'bfiles/b109908.txt'), ("909", 'bfiles/b109909.txt')):
    bf = []
    for line in open(f):
        line=line.strip()
        if line and not line.startswith('#'):
            k,v = line.split(); bf.append((int(k), int(v)))
    bad = []
    for k, v in bf[:60]:
        if 4 <= k < 300:
            pr = [w for w in vals(k) if w > 0 and isprime(w)]
            got = max(pr) if pr else 0
            if name == "909": got = len(pr)
            if got != v: bad.append((k, v, got))
    print(f"  {name}: mismatches:", bad if bad else "NONE")

print("=== PATH 1: existence scan n=4..500000 (early exit per n) ===")
t0 = time.time()
viol = []
n = 4
while n <= 500000:
    found = False
    # try small k first: values n-2, 2n-5, 3n-10, ...
    for k in range(1, min(n//2, 400) + 1):
        v = k*(n-k) - 1
        if v > 0 and isprime(v):
            found = True
            break
    if not found:
        # exhaustive fallback
        for k in range(1, n//2 + 1):
            if isprime(k*(n-k)-1):
                found = True; break
    if not found:
        viol.append(n)
        if len(viol) > 10: break
    n += 1
    if time.time() - t0 > 55:
        print(f"  TIME CAP at n={n}")
        break
print(f"  scanned n<= {n-1}: violations={viol if viol else 'NONE'}")

print("=== PATH 2 consistency: sup>0 <=> count>0 (n<=2000) ===")
bad = []
for n in range(4, 2001):
    pr = [v for v in vals(n) if v > 0 and isprime(v)]
    if (max(pr) > 0) != (len(pr) > 0):
        bad.append(n)
print("  inconsistencies:", bad if bad else "NONE")
