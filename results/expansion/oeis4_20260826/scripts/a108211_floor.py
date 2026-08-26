#!/usr/bin/env python3
"""A108211 audit: floor(1 / (1/(4n) - log 2 + sum_{k=n+1..2n} 1/k)) == 16n^2+1 ?

RIGOROUS PATH (Path 1): log 2 enclosed in a rational interval via the
alternating-style series  log 2 = 2*artanh(1/3)*? -> use
log 2 = ln( (1+1/3)/(1-1/3) ) = 2 * sum_{j>=0} (1/3)^{2j+1}/(2j+1).
Partial sums give LOWER bound; add proven tail bound for UPPER.
D(n) := 1/(4n) - log2 + H_{2n}-H_n  is DECREASING in log2 =>
D in [D(rational hi log2), D(rational lo log2)]. E=1/D in reciprocal interval.
Check 16n^2+1 <= E < 16n^2+2  <=>  1/(16n^2+2) < D <= 1/(16n^2+1).

FLOAT PATH (Path 2): mpmath dps=60 direct evaluation, margin recorded;
loop n to 10^6 with double-only where margin > 1e-9 (else escalate).
"""
from fractions import Fraction as Fr
import time

def log2_interval(K):
    """[lo, hi] rational bounds with width < 2*(1/9)^{K+1}/(2(K+1)+1)."""
    lo = Fr(0)
    for j in range(K + 1):
        lo += 2 * Fr(1, 3**(2*j+1) * (2*j+1))
    tail = 2 * Fr(1, 3**(K+2)) / (2*(K+1)+1) * Fr(9, 8)  # geometric bound on rest
    return lo, lo + tail

def H_range(n):
    """H_{2n} - H_n exactly as Fraction."""
    s = Fr(0)
    for k in range(n+1, 2*n+1):
        s += Fr(1, k)
    return s

def check_rigorous(n, K=70):
    lo_l2, hi_l2 = log2_interval(K)
    H = H_range(n)
    D_lo = Fr(1, 4*n) - hi_l2 + H     # smallest D
    D_hi = Fr(1, 4*n) - lo_l2 + H     # largest D
    # need 1/(16n^2+2) < D <= 1/(16n^2+1); sufficient: D_lo > 1/(16n^2+2) and D_hi <= 1/(16n^2+1)
    c1 = D_lo > Fr(1, 16*n*n + 2)
    c2 = D_hi <= Fr(1, 16*n*n + 1)
    return c1 and c2, D_hi, D_lo

print("=== PATH 1: rigorous rational-interval checks ===")
t0 = time.time()
bad = []
N1 = 400
for n in range(1, N1 + 1):
    ok, Dh, Dl = check_rigorous(n)
    if not ok:
        bad.append(n)
        print(f"  n={n}: RIGOROUS CHECK FAILED (D in [{float(Dl):.6g},{float(Dh):.6g}]")
print(f"  n=1..{N1}: all floor-identities rigorously confirmed" if not bad else f"  FAILURES: {bad}")
print(f"  ({time.time()-t0:.1f}s)")

print("=== margin analysis at sample n ===")
for n in (1, 2, 10, 100, 397):
    _, Dh, Dl = check_rigorous(n)
    gap = min(Fr(1, 16*n*n+2), Fr(1, 16*n*n+1))
    print(f"  n={n}: |interval| ~ {float(Dh-Dl):.3e} vs gap ~ {float(gap - (16*n*n)*(Dh-Dl)):.3e}")

print("=== PATH 2: mpmath dps=60, n=1..200000 ===")
import mpmath as mp
mp.mp.dps = 60
log2 = mp.log(2)
def holds_mp(n):
    D = mp.mpf(1)/(4*n) - log2 + mp.nsum(lambda k: 1/k, [n+1, 2*n]) if n < 500 else \
        mp.mpf(1)/(4*n) - log2 + mp.fsum(1/mp.mpf(k) for k in range(n+1, 2*n+1))
    E = 1/D
    return mp.floor(E) == 16*n*n + 1, float(E - (16*n*n+1)), float((16*n*n+2) - E)
worst_lo, worst_hi = 1e9, 1e9
fails = []
t0 = time.time()
for n in range(1, 200001):
    h, m1, m2 = holds_mp(n)
    worst_lo = min(worst_lo, m1); worst_hi = min(worst_hi, m2)
    if not h:
        fails.append(n)
        if len(fails) > 5: break
    if time.time() - t0 > 55:
        print(f"  time cap at n={n}")
        break
print(f"  checked up to n={n}: failures={fails[:6] if fails else 'NONE'}")
print(f"  min margins: E-(16n^2+1) >= {worst_lo:.3e};  (16n^2+2)-E >= {worst_hi:.3e}")

print("=== head values vs OEIS/b-file ===")
vals = []
p = 1
sieve_ok = True
# independent primality-free check unnecessary; just verify formula terms 17,65,...
def a_lean(n):
    return 16*n*n + 1
print("  a(n)=16n^2+1 head:", [a_lean(k) for k in range(1, 8)])
bf = open('bfiles/b108211.txt').read().split()
print("  b-file head      :", bf[2:16])
