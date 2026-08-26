#!/usr/bin/env python3
"""A109074 audit v2 — corrected A005156 handling.
A005156(n) = (1/2^n) * Prod_{k=1..n} (6k-2)!(2k-1)!/((4k-1)!(4k-2)!)
  (Razumov/Stroganov; PROVED by Kuperberg per OEIS %F).
=> A005156(n)/A005156(n-1) = (6n-2)!(2n-1)! / (2*(4n-1)!(4n-2)!)
And frac(n) = C(6n-2,2n)/(2*C(4n-1,2n)) simplifies to exactly that expression.
So the CORRECTED relation frac n = A005156(n)/A005156(n-1) is a THEOREM.
Path 1: exact Fractions vs OEIS b005156.txt values.
Path 2: symbolic sympy equality for generic n.
"""
from fractions import Fraction
from math import comb

def frac(n):
    if n == 0:
        return Fraction(1, 2)
    return Fraction(comb(6*n-2, 2*n), 2*comb(4*n-1, 2*n))

print("=== PATH 1: frac(n) vs A005156(n)/A005156(n-1), b-file values ===")
A = {}
for line in open('bfiles/b005156.txt'):
    line = line.strip()
    if line:
        k, v = line.split(); A[int(k)] = int(v)
ok = all(frac(n) == Fraction(A[n], A[n-1]) for n in range(1, min(300, max(A)) + 1))
print(f"  frac(n) == A(n)/A(n-1) for n=1..{min(300, max(A))}: {ok}")

print("=== OEIS-as-written shift (n+1)/n: ===")
ok2 = all(frac(n) == Fraction(A[n+1], A[n]) for n in range(1, 50))
print("  frac(n) == A(n+1)/A(n) for n=1..49:", ok2)

print("=== Lean literal statement (b = A001764): refuted at n=1 (see run1): 1 != 3 ===")

print("=== PATH 2: symbolic identity ===")
import sympy as sp
n = sp.symbols('n', positive=True, integer=True)
lhs = sp.factorial(6*n-2)/(sp.factorial(2*n)*sp.factorial(4*n-2)) \
      * (sp.factorial(2*n)*sp.factorial(2*n-1))/(2*sp.factorial(4*n-1))
# = frac(n) after cancelling C-forms:
lhs_simplified = sp.simplify(lhs)
rhs = sp.factorial(6*n-2)*sp.factorial(2*n-1)/(2*sp.factorial(4*n-1)*sp.factorial(4*n-2))
print("  simplify(frac-as-factorials) == ratio-expression:",
      sp.simplify(lhs_simplified - rhs) == 0)

print("=== numerators a-file vs b-file head (16) ===")
bf = []
for line in open('bfiles/b109074.txt'):
    line = line.strip()
    if not line or line.startswith('#'): continue
    k, v = line.split(); bf.append((int(k), int(v)))
mine = [(k, frac(k).numerator) for k, _ in bf[:16]]
print("  match:", mine == bf[:16])
