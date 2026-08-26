#!/usr/bin/env python3
"""A115257 audit (Sun 2013): P_n(x)=Sum C(2k,k)^2 x^k and
Q_n(x)=Sum C(2k,k)^2/(k+1) x^k are IRREDUCIBLE over Q for all n>=1?
Path 1: sympy factor_list over Q.
Path 2: independent Rabin irreducibility certificate modulo several primes
        (sound one-way: irreducible mod good p => irreducible over Q for
        primitive poly with p not dividing content/leading coeff).
One reducible case at small n would CROSSING the conjecture.
"""
from math import comb
from fractions import Fraction
import sympy as sp

x = sp.symbols('x')

def P(n):
    return sp.Poly(sum(comb(2*k, k)**2 * x**k for k in range(n+1)), x)
def Q(n):
    return sp.Poly(sum(Fraction(comb(2*k,k)**2, k+1) * x**k for k in range(n+1)), x)

def rabin_irreducible_over_Q(coeffs, trials=6):
    """coeffs: list of Fraction (low->high). Try random primes; if poly mod p
    passes Rabin's irreducibility test in GF(p)[x], then irreducible over Q."""
    from fractions import Fraction as Fr
    import random
    # clear denominators -> primitive integer poly
    dens = [c.denominator for c in coeffs]
    D = 1
    from math import gcd
    for d_ in dens:
        D = D*d_//gcd(D, d_)
    ints = [int(c*D) for c in coeffs]
    g = 0
    for v in ints: g = gcd(g, abs(v))
    if g > 1:
        ints = [v//g for v in ints]
    deg = len(ints) - 1
    if deg == 0:
        return True
    lead = ints[-1]
    primes = [1000003, 1000033, 1000037, 1000039, 1000081, 1000099, 999983, 1000189]
    for p in primes[:trials]:
        if lead % p == 0:
            continue
        # poly mod p, low->high
        f = [v % p for v in ints]
        # Rabin test: d = deg; check x^(p^d) == x mod f and for each prime q|d,
        # gcd(x^(p^(d/q)) - x, f) == 1
        d = deg
        # distinct-degree factorization shortcut via sympy gf module? implement:
        px = [0, 1]  # x
        def polymulmod(a, b):
            res = [0]*(len(a)+len(b)-1)
            for i, ai in enumerate(a):
                if ai:
                    for j, bj in enumerate(b):
                        res[i+j] = (res[i+j] + ai*bj) % p
            # reduce mod f
            for i in range(len(res)-1, d-1, -1):
                c = res[i]
                if c:
                    for j in range(d+1):
                        res[i-d+j] = (res[i-d+j] - c*f[j]) % p
                res[i] = 0
            return res[:d]
        def polypow(base, e):
            result = [1]
            while e:
                if e & 1:
                    result = polymulmod(result, base)
                base = polymulmod(base, base)
                e >>= 1
            return result
        def polyadd(a, b):
            L = max(len(a), len(b))
            r = [0]*L
            for i in range(L):
                r[i] = ((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % p
            return r
        def polysub(a, b):
            L = max(len(a), len(b))
            r = [0]*L
            for i in range(L):
                r[i] = ((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p
            return r
        def polygcd(a, b):
            def norm(v):
                v = list(v)
                while len(v) > 1 and v[-1] == 0:
                    v.pop()
                return v
            a, b = norm(a), norm(b)
            inv = None
            def inv_mod(v):
                return pow(v, p-2, p)
            while True:
                b = norm(b)
                if len(b) == 1 and b[0] == 0:
                    return a
                ib = inv_mod(b[-1])
                # a mod b
                a = norm(a)
                while len(a) >= len(b) and not (len(a)==1 and a[0]==0):
                    shift = len(a)-len(b)
                    c = a[-1]*ib % p
                    for i in range(len(b)):
                        a[shift+i] = (a[shift+i] - c*b[i]) % p
                    a = norm(a)
                a, b = b, a
            # unreachable
        # x^(p^d) mod f
        h = [1]
        base = polymulmod(px, [1])
        e = p
        dd = d
        while dd:
            if dd & 1:
                h = polymulmod(h, px)
            px2 = polymulmod(px, px)
            # exponentiation by squaring on x^p chain: simpler do powmod
            dd >>= 1
        # too intricate; use straightforward powmod of x to p^d
        def powmod_x(e):
            r = [1]
            b = [0, 1][:d] if d > 1 else [0]
            b = [0, 1]
            b = polymulmod([0,1],[1])
            bb = polymulmod([0,1], [1])  # x mod f
            while e:
                if e & 1:
                    r = polymulmod(r, bb)
                bb = polymulmod(bb, bb)
                e >>= 1
            return r
        xd = powmod_x(p**d)
        x1 = [0,1][:min(2,d)] + ([0]*(d-2)) if d >= 2 else [0,1][:d]
        xmod = polymulmod([0,1], [1])
        lhs = polyadd(xd, [-1 % p])
        rhs = polyadd(xmod, [-1 % p])
        g1 = polygcd(f, polysub(xd, xmod))
        def is_one(gg):
            gg = list(gg)
            while gg and gg[-1] == 0: gg.pop()
            return len(gg) <= 1 and (not gg or gg[0] != 0)
        if not is_one(g1) and not (len(g1)>=1 and g1[0]%p==0 and len(g1)<=1):
            # x^(p^d)!=x mod f => reducible mod p; try next prime
            continue
        okq = True
        import sympy
        for q in sympy.primerange(1, d):
            if d % q == 0:
                hq = powmod_x(p**(d//q))
                gg = polygcd(f, polysub(hq, xmod))
                if not is_one(gg):
                    okq = False
                    break
        if okq and is_one(g1):
            return True   # certified irreducible over GF(p) => over Q
    return None  # no certificate obtained

print("=== Path 1: sympy factor_list over Q ===")
badP, badQ = [], []
import time
t0=time.time()
for n in range(1, 121):
    fp = sp.factor_list(P(n))
    fq = sp.factor_list(Q(n))
    def is_irred(fl, deg):
        return len(fl[1]) == 1 and fl[1][0][1] == 1 and fl[1][0][0].degree() == deg
    if not is_irred(fp, n):
        badP.append((n, [(f.degree(), e) for f, e in fp[1]]))
    if not is_irred(fq, n):
        badQ.append((n, [(f.degree(), e) for f, e in fq[1]]))
    if time.time()-t0 > 55:
        print(f"  TIME CAP at n={n}")
        break
print(f"  scanned n<= {n}: reducible P cases: {badP[:5]}")
print(f"                 reducible Q cases: {badQ[:5]}")

print("=== Path 2: Rabin certificates (independent modular code) ===")
cert = 0
nocert = []
for n in range(1, 41):
    for name, poly in (("P", P(n)), ("Q", Q(n))):
        coeffs = [sp.Rational(c) for c in poly.all_coeffs()][::-1]  # low->high
        r = rabin_irreducible_over_Q(coeffs)
        if r is True:
            cert += 1
        else:
            nocert.append((name, n))
print(f"  certificates obtained: {cert}/80; without certificate: {nocert[:8]}")

print("=== head sums vs OEIS ===")
def a_sum(n):
    return sum(comb(2*k,k)**2 for k in range(n+1))
print("  ", [a_sum(k) for k in range(10)])
print("   expect 1,5,41,441,5341,68845,922621,12701245,178338145,2542242545")
