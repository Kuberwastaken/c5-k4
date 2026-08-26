#!/usr/bin/env python3
"""A11545 (A011545) audit.
a(n) = floor(pi * 10^n): first n+1 decimal digits of pi as integer.
conjecture1 (Haken 1977): no term is a perfect square.
conjecture2: no integer strictly inside (pi*10^n, pi/arctan(10^-n)).
Both infinitary => HOLD_NUMERIC; per-term checks in range with precision guards.

Path 1: mpmath pi to N digits; a(n) via floor; square test by isqrt.
Path 2 (independence for conj2): interval width analysis - integer exists iff
fractional part of pi*10^n exceeds 1 - delta_n, delta_n = pi*10^n*(1/arctan(eps)*eps - 1)
with eps=10^-n; compute per-term margins.
Also verify %F formula a(n)=floor(pi*10^n) against b-file head.
"""
import mpmath as mp
from math import isqrt
import sys
sys.set_int_max_str_digits(200000)

NDIG = 6200          # a(n) reliable up to n ~ NDIG-50
mp.mp.dps = NDIG + 60
pi = mp.pi

print("=== head vs b-file ===")
bf = []
for line in open('bfiles/b011545.txt'):
    line=line.strip()
    if line and not line.startswith('#'):
        k,v = line.split(); bf.append((int(k), int(v)))
ok = True
for k, v in bf[:12]:
    mine = int(mp.floor(pi * mp.mpf(10)**k))
    if mine != v:
        ok = False
        print(f"  MISMATCH n={k}")
print("  b-file first 12 match:", ok)
print("  head:", [int(k) for k,_ in bf[:8]])

print("=== CONJECTURE1: no square terms, n<=6000 ===")
t0 = __import__('time').time()
sq_hits = []
min_margin = None
for n in range(0, 6001):
    an = int(mp.floor(pi * mp.mpf(10)**n))
    r = isqrt(an)
    margin = min(an - r*r, (r+1)*(r+1) - an)   # >0 iff not square
    if an == r*r:
        sq_hits.append(n)
        print(f"  SQUARE at n={n}!!!")
    if min_margin is None or margin < min_margin:
        min_margin = margin; argmin = n
    if __import__('time').time() - t0 > 55:
        print(f"  time cap at n={n}")
        break
print(f"  scanned n<= {n}; squares found: {sq_hits if sq_hits else 'NONE'}")
print(f"  min distance-to-nearest-square: {min_margin} at n~{argmin} (Haken margin)")

print("=== CONJECTURE2: no integer in (pi*10^n, pi/arctan(10^-n)), n<=1200 ===")
t0 = __import__('time').time()
hits = []
worst = None
for n in range(1, 1201):
    x = pi * mp.mpf(10)**n
    hi = pi / mp.atan(mp.mpf(10)**(-n))
    fx = x - mp.floor(x)
    width = hi - x
    # integer strictly inside iff frac(x) + width >= 1 (then floor(x)+1 < hi... check strict)
    if fx + width >= 1:
        hits.append((n, float(fx), float(width)))
    if worst is None or (1 - fx - width) < worst[1]:
        worst = (n, 1 - fx - width)
    if __import__('time').time() - t0 > 40:
        break
print(f"  scanned n<= {n}: integers inside intervals: {hits[:4] if hits else 'NONE'}")
print(f"  closest approach to containing an integer: n={worst[0]}, slack={float(worst[1]):.3e}")
print("  (equivalence note: contains-integer <=> next digits of pi are 999..., same")
print("   phenomenon as conj1's square question via Haken/Gardner analysis)")
