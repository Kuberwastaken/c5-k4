#!/usr/bin/env python3
"""A113258 audit v2: perfect powers after a(4)=125.
   Modular pre-filtering for exponent candidates, exact integer_nthroot only on survivors."""
import time
from sympy import integer_nthroot

def build(n):
    import math
    f = [math.factorial(i) for i in range(0, n + 2)]
    return sum(f[i] ** f[n - i + 1] for i in range(1, n + 1))

def is_perfect_power(x):
    """Returns (True, (base,e)) or (False, None). Filters exponents via e-th power
       residue sets modulo small primes before exact checks."""
    if x < 4:
        return False, None
    bl = x.bit_length()
    mods = [13, 17, 19, 23, 29]
    res_sets = {}
    def eth_powers_mod(e, m):
        key = (e, m)
        if key not in res_sets:
            s = set()
            c = 1
            for _ in range(m):
                s.add(pow(c, e, m))
                c = (c + 1) % m
            res_sets[key] = s
        return res_sets[key]
    xm = [x % m for m in mods]
    e = 2
    while e <= bl:
        ok = True
        for idx, m in enumerate(mods):
            if xm[idx] not in eth_powers_mod(e, m):
                ok = False
                break
        if ok:
            r, exact = integer_nthroot(x, e)
            if exact:
                return True, (r, e)
        e += 1
    return False, None

print("== head terms ==")
for n, want in [(1,1),(2,3),(3,11),(4,125)]:
    got = build(n)
    print(f"a({n})={got} {'OK' if got==want else 'FAIL'}")
print("a(4)=125=5^3 itself is a power (excluded: question asks AFTER a(4))")

t0 = time.time()
for n in range(5, 11):
    t1 = time.time()
    v = build(n)
    pp, w = is_perfect_power(v)
    print(f"n={n}: digits={len(str(v))} perfect_power={pp} {w or ''} ({time.time()-t1:.1f}s)")
    if time.time() - t0 > 55:
        print("overall cap reached")
        break
