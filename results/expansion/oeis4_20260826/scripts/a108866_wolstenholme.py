#!/usr/bin/env python3
"""A108866 audit: numerator(-2/n + Sum_{k=1..n} 2^k/k) == 0 mod n^2 iff n prime (n>3)?
Per-term exact Fractions both directions => one wrong term = CROSSING.
Path 1: Fraction accumulation.
Path 2: modular computation modulo n^2 with rationals via modular inverses
        (valid since denominators 1..n may share factors with n^2! careful --
        use Fraction only for safety; second path = independent big-int
        common-denominator approach instead).
Also verify sequence head vs OEIS b-file.
"""
from fractions import Fraction
from sympy import isprime

def rat_expr(n):
    s = Fraction(0)
    p = 1
    for k in range(1, n+1):
        p *= 2                      # 2^k exactly
        s += Fraction(p, k)
    return s - Fraction(2, n)

def seq_a(n):
    # numerator of Sum_{k=1..n} 2^k/k
    s = Fraction(0)
    p = 1
    for k in range(1, n+1):
        p *= 2
        s += Fraction(p, k)
    return s.numerator

print("=== sequence head vs OEIS ===")
mine = [0] + [seq_a(n) for n in range(1, 16)]
print(" ", mine)
bf = []
for line in open('bfiles/b108866.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        k,v = line.split(); bf.append((int(k), int(v)))
print("  b-file:", [v for _, v in bf[:17]])
print("  match:", mine == [v for _, v in bf[:len(mine)]])

print("=== Lean tests a_0..a_4 = 0,2,4,20,32 ===")
print("  ", [seq_a(i) for i in range(5)])

print("=== CONJECTURE SCAN n = 4..4000 (both directions; one wrong term = crossing) ===")
t0 = __import__('time').time()
viol_if  = []   # composite satisfying congruence (breaks <= direction)
viol_onlyif = [] # prime failing congruence (breaks => direction)
for n in range(4, 4001):
    num = abs(rat_expr(n).numerator)
    ok_cong = (num % (n*n)) == 0
    pr = isprime(n)
    if pr and not ok_cong:
        viol_onlyif.append(n)
    if (not pr) and ok_cong:
        viol_if.append((n, num))
        print(f"  COMPOSITE PASSES at n={n}: {num} % {n*n} == 0")
    if __import__('time').time() - t0 > 55:
        print(f"  time cap at n={n}")
        break
print(f"  scanned to n={n}")
print("  primes failing congruence:", viol_onlyif if viol_onlyif else "NONE")
print("  composites passing congruence:", viol_if[:10] if viol_if else "NONE")

print("=== PATH 2: independent common-denominator recomputation spot check ===")
def rat_expr_v2(n):
    # lcm-free: sum with denominator D = lcm(1..n)*n ; build via integer ops
    from math import gcd
    D = 1
    for k in range(1, n+1):
        D = D*k//gcd(D, k)
    N = sum((D//k)*(1 << k) for k in range(1, n+1)) - 2*(D//n)
    # value = N/D; reduce
    g = gcd(abs(N), D)
    return (N//g, D//g)
import random
bad = []
for n in random.sample(range(4, 2000), 120):
    nu, de = rat_expr_v2(n)
    if Fraction(nu, de) != rat_expr(n):
        bad.append(n)
print("  path2 mismatches on 120 samples:", bad if bad else "NONE")

print("=== known context: Wolstenholme primes L/R note (A088164: 16843, 2124679) ===")
wp = [16843, 2124679]
for n in wp:
    if n <= 4000: continue
print("  (beyond scan cap; literature-consistent: none expected below 16843)")
