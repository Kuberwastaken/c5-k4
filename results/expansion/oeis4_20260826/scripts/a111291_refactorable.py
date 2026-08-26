#!/usr/bin/env python3
"""A111291 audit: countRefactorable(x) >= x/(2 log x) for ALL real x > 1.
Lean: countRefactorable x = countNat(floor x); countNat(m) = #{k<=m : tau(k)|k}.

Path 1: explicit REAL counterexamples near 1 (x=1.5, 1.001): LHS=count(1)=1,
        RHS blows up as x->1+ => statement false as formalized.
Path 2: SPF-sieve divisor counts to 10^7; integer-point inequality check
        count(m) >= m/(2 ln m), plus monotone worst-case reduction
        sup_{x in [m,m+1)} RHS at x->(m+1)- => check count(m) >= (m+1)/(2 ln(m+1)).
Outputs: violation set, first-holds threshold, min margins, head counts vs b-file.
"""
from math import isqrt, log

def count_refactorable_naive(m):
    c = 0
    for k in range(1, m + 1):
        tau = sum(1 for d in range(1, isqrt(k) + 1) if k % d == 0)
        if d := True: pass
        tau = -tau if False else tau
        # fix double count
        tau = sum(1 for d in range(1, isqrt(k) + 1) if k % d == 0)
        if isqrt(k)**2 == k:
            tau = 2*tau - 1
        else:
            tau = 2*tau
        if k % tau == 0:
            c += 1
    return c

print("=== PATH 1: real counterexamples near x=1 ===")
for x in (1.5, 1.1, 1.001):
    lhs = count_refactorable_naive(int(x))   # floor x = 1 -> {1}: count 1
    rhs = x / (2*log(x))
    print(f"  x={x}: count={lhs}  x/(2 ln x)={rhs:.3f}  holds={lhs >= rhs}")

print("=== PATH 2: sieve to 10^7 ===")
N = 10_000_000
import numpy as np
t0 = __import__('time').time()
spf_divcount = np.zeros(N + 1, dtype=np.uint8)   # number of divisors mod 256? need exact; use uint32 for safety on small, but tau <= 1344 for n<=1e7 fits uint16
tau = np.ones(N + 1, dtype=np.uint16)
# linear sieve for tau
tau[0] = 0
cnt = np.zeros(N + 1, dtype=np.uint32)  # cnt[n] = number of copies of smallest prime
primes = []
is_comp = bytearray(N + 1)
for i in range(2, N + 1):
    if not is_comp[i]:
        primes.append(i)
        tau[i] = 2
        cnt[i] = 1
    for p in primes:
        ip = i * p
        if ip > N:
            break
        is_comp[ip] = 1
        if i % p == 0:
            cnt[ip] = cnt[i] + 1
            tau[ip] = tau[i] // (cnt[i] + 1) * (cnt[i] + 2)
            break
        else:
            cnt[ip] = 1
            tau[ip] = tau[i] * 2
print(f"  sieve done in {__import__('time').time()-t0:.1f}s")

refac = (np.arange(1, N + 1, dtype=np.uint32) % tau[1:].astype(np.uint32)) == 0
counts = np.cumsum(refac.astype(np.uint32))
print("  heads count(10^n) n=0..7:", [int(counts[10**n - 1]) for n in range(8)])
bfile = []
for line in open('bfiles/b111291.txt'):
    line = line.strip()
    if line and not line.startswith('#'):
        k, v = line.split(); bfile.append(int(v))
mine = [int(counts[10**n - 1]) for n in range(min(8, len(bfile)))]
print("  vs b-file:", bfile[:8], "match:", mine == bfile[:len(mine)])

idx = np.arange(2, N + 1, dtype=np.float64)
lhs = counts[1:].astype(np.float64)
rhs = idx / (2*np.log(idx))
viol = lhs < rhs
vi = np.nonzero(viol)[0]
if len(vi):
    print(f"  INTEGER-POINT violations m with count(m) < m/(2ln m): first 12 m="
          f"{(vi[:12]+2).tolist()} ... total {len(vi)}, last={vi[-1]+2}")
else:
    print("  no integer-point violations")

# monotone worst-case: count(m) >= (m+1)/(2 ln(m+1)) ?
mm = idx[:-1]
worst = (mm + 1)/(2*np.log(mm + 1))
vw = lhs[:-1] < worst
wi = np.nonzero(vw)[0]
print(f"  WORST-CASE (right-endpoint) violations: total {len(wi)}, "
      f"first m={(wi[:12]+2).tolist()}, last m={wi[-1]+2}" if len(wi) else "  none")
