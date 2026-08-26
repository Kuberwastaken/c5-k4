#!/usr/bin/env python3
"""A105565 audit.
a(n) = 1 iff exactly 5 Fibonacci numbers have exactly n digits (n>=1).
Conjecture (OEIS %C / Lean): beta-2 < S(n) - alpha*n < beta-1 for all n>=1,
  alpha = log(10)/log(phi) - 4, beta = log(5)/(2 log(phi)) - 1.

Path 0: verify Lean def faithfulness incl. maxK = 5n+10 sufficiency:
        largest fib index with < 10^n digits must be < 5n+10.
Path 1: EXACT digit-length counting of F_0..F_K by big ints; indicator a(n);
        S(n) integers; compare to OEIS %S head and b-file.
Path 2: Iverson-bracket formula a(n) = [ {n*alpha + beta} < alpha ] (n>1)
        via mpmath dps=60 -> independent term generation.
Inequality check: per-term with high-precision constants; record min margins.
Universal claim => HOLD_NUMERIC label (infinitary), per-term verified in range.
"""
import mpmath as mp
import sys
sys.set_int_max_str_digits(20000)
mp.mp.dps = 60

# --- Path 0/1: exact fibs ---
K_MAX_DIGITS = 6001            # digits up to 6000
fibs = [0, 1]
while len(str(fibs[-1])) <= K_MAX_DIGITS:
    fibs.append(fibs[-1] + fibs[-2])
# index of first fib with >= d digits
def count_fibs_with_d_digits(d):
    lo, hi = 10**(d-1), 10**d
    import bisect
    L = bisect.bisect_left(fibs, lo)
    R = bisect.bisect_left(fibs, hi)
    return R - L

def a_exact(n):
    if n == 0: return 0
    return 1 if count_fibs_with_d_digits(n) == 5 else 0

print("=== Path 0: maxK=5n+10 sufficiency (Lean filter bound) ===")
ok_all = True
for n in range(1, 300):
    import bisect
    hi = 10**n
    last_k = bisect.bisect_left(fibs, hi) - 1   # largest index with fib(k) < 10^n
    if not (last_k < 5*n + 10):
        ok_all = False
        print(f"  n={n}: UNSAFE maxK, needed index {last_k}")
print("  maxK=5n+10 safe for n=1..299:", ok_all)
# asymptotic: index ~ n*log10(e)*ln(10)/log(phi)... = n/log10(phi)+O(1); 4.785n+c << 5n+10
print("  (index ~ n*4.78497 + 1.67 so safe for all large n)")

print("=== Path 1: exact indicator vs OEIS %S ===")
S_head = ''.join(open('oeis_pages/A105565.txt').read().split('%S A105565 ')[1].split('\n')[0:1])
oeis_head = [int(x) for x in S_head.split(',')[0:34] if x.strip()]
mine = [a_exact(n) for n in range(1, 35)]
print("  OEIS %S:", oeis_head)
print("  mine   :", mine)
print("  match:", mine == oeis_head)

bf = []
for line in open('bfiles/b105565.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        k,v = line.split(); bf.append((int(k), int(v)))
mm = [(k, a_exact(k)) for k, _ in bf[:120]]
print("  b-file (first 120) match:", mm == bf[:120])

print("=== Path 2: Iverson formula [{n*alpha+beta} < alpha], n=2..3000 ===")
alpha = mp.log(10)/mp.log(mp.mpf('1.6180339887498948482045868343656381177203')) - 4 \
        if False else mp.log(10)/mp.log((1+mp.sqrt(5))/2) - 4
beta  = mp.log(5)/(2*mp.log((1+mp.sqrt(5))/2)) - 1
mism = []
for n in range(2, 3001):
    frac_part = (n*alpha + beta) % 1
    iv = 1 if frac_part < alpha else 0
    if iv != a_exact(n):
        mism.append(n)
        if len(mism) > 5: break
print("  mismatches n=2..3000:", mism if mism else "NONE")

print("=== INEQUALITY beta-2 < S(n)-alpha*n < beta-1 (per-term, n<=3000) ===")
worst_lo, worst_hi, bad = 1e18, 1e18, []
Sn = 0
for n in range(1, 3001):
    Sn += a_exact(n)
    resid = Sn - alpha*n
    m1 = resid - (beta - 2)
    m2 = (beta - 1) - resid
    worst_lo = min(worst_lo, m1); worst_hi = min(worst_hi, m2)
    if m1 <= 0 or m2 <= 0:
        bad.append((n, float(resid)))
        if len(bad) > 5: break
print("  violations:", bad if bad else f"NONE for n=1..3000")
print(f"  min margins: lower {float(worst_lo):.6e}, upper {float(worst_hi):.6e}")
print(f"  constants: alpha={float(alpha):.12f} beta={float(beta):.12f}")
print("  HOLD_NUMERIC: infinitary claim labelled numeric-evidence-only")
