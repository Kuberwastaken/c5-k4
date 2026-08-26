#!/usr/bin/env python3
"""A103151 audit: #{(p,q) odd primes : 2n+1 = 2p + q}, p <= n forced by q >= 1.
Lean def counts p in [0,n] with p prime, p != 2, q=2n+1-2p prime.
Conjecture a(n) >= 1 for n >= 4 (Levy/Lemoine type; OEIS %C calls it 'stronger
than Goldbach' - source wording, audited separately below).
Path 1: full counts via sieve for n<=20000 vs b-file head.
Path 2: early-exit EXISTENCE scan to 10^6 (conjecture needs only a(n)>=1).
"""
import numpy as np
import time

PIG = 3_100_000
sieve = np.ones(PIG + 1, dtype=bool)
sieve[:2] = False
for i in range(2, int(PIG**.5) + 1):
    if sieve[i]:
        sieve[i*i::i] = False
isprime = sieve

print("=== PATH 1: full counts n=1..20000 ===")
t0 = time.time()
counts = []
for n in range(1, 20001):
    m = 2*n + 1
    c = 0
    # iterate odd primes p<=n
    for p in range(3, n + 1, 2):
        if isprime[p] and m - 2*p > 1 and isprime[m - 2*p]:
            c += 1
    counts.append(c)
print(f"  ({time.time()-t0:.1f}s)")
head = counts[:17]
print("  computed head:", head)
oeis_head = [0,0,0,1,1,2,1,3,2,2,2,3,3,4,2,4,2]
print("  OEIS %S head :", oeis_head)
print("  match:", head == oeis_head)

bf = []
for line in open('bfiles/b103151.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        k,v = line.split(); bf.append((int(k), int(v)))
mine = [(k, counts[k-1]) for k, _ in bf[:60]]
print("  b-file (60) match:", mine == bf[:60])

print("=== Lean test values a_1..a_5 ===")
print("  ", counts[0:5], "(expect 0,0,0,1,1)")

print("=== PATH 2: existence scan n=4..1_500_000 (early exit) ===")
t0 = time.time()
fails = []
n = 4
while n <= 1_500_000:
    m = 2*n + 1
    found = False
    for p in range(3, n + 1, 2):
        if not isprime[p]:
            continue
        q = m - 2*p
        if q > 1 and isprime[q]:
            found = True
            break
        if time.time() - t0 > 55:
            break
    if not found:
        fails.append(n)
        if len(fails) > 10: break
    n += 1
    if time.time() - t0 > 55:
        print(f"  TIME CAP at n={n}")
        break
print(f"  scanned to n={n}: violations={fails if fails else 'NONE'}")
