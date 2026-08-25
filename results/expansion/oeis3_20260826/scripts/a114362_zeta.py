#!/usr/bin/env python3
"""A114362 audit: numerators of zeta(4n)/zeta(2n)^2 via Bernoulli formula;
   verify head terms vs b-file; numeric bracket for conjecture2's O(11^-n) residual."""
import sys
from fractions import Fraction
import mpmath as mp

def bernoulli(n):
    # exact Bernoulli via sympy
    from sympy import bernoulli as sb
    return Fraction(int(sb(n).p), int(sb(n).q))

def Qnum(n):
    if n == 0:
        return 2
    b4 = bernoulli(4 * n)
    b2 = bernoulli(2 * n)
    from math import comb
    binom = comb(4 * n, 2 * n)
    q = -2 * b4 / (b2 * b2 * binom)
    return q.numerator

print("== head via Bernoulli formula vs published ==")
pub = {0: 2, 1: 2, 2: 6, 3: 691}
for n in range(0, 8):
    v = Qnum(n)
    print(f"a({n}) = {v} {'OK' if pub.get(n)==v else ''}")

print("\n== conjecture2 numeric bracket: (1-t)/(1+t) - sum_{p<=7} p^-n = O(11^-n) ==")
mp.mp.dps = 60
def t_of(n):
    return mp.zeta(2*n) / (mp.zeta(n) ** 2)

for n in [5, 10, 15, 20, 30]:
    t = t_of(n)
    lhs = (1 - t) / (1 + t) - (mp.mpf(2)**-n + mp.mpf(3)**-n + mp.mpf(5)**-n + mp.mpf(7)**-n)
    ref = mp.mpf(11) ** -n
    print(f"n={n}: residual={float(lhs):.3e} 11^-n={float(ref):.3e} ratio={float(abs(lhs)/ref):.4f}")
