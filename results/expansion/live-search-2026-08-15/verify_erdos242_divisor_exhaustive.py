#!/usr/bin/env python3
"""Erdos 242 (Erdos-Straus with distinctness), upstream 242.lean:

  theorem erdos_242 (n : N) (hn : 2 < n) :
      exists x y z : N, 1 <= x /\ x < y /\ y < z /\ (4/n : Q) = 1/x + 1/y + 1/z

Independent code path from the predecessor's `verify_erdos_misc.py es242`
(which looped over y and hit a per-n op cap).  Here the y-loop is replaced by
an exact divisor enumeration, which makes the per-x search *complete*, not
capped:

  4/n - 1/x = p/q  (lowest terms, p,q > 0)
  1/y + 1/z = p/q  <=>  (p*y - q)(p*z - q) = q^2,  p*y - q = d | q^2, d <= q
  => y = (q+d)/p,  z = (q + q^2/d)/p    (both must be integral)

x is forced into n/4 < x <= 3n/4 because 1/x is the largest of the three unit
fractions.  Everything is exact integer arithmetic.
"""
import sys
import time
from math import gcd, isqrt


def spf_sieve(m):
    s = list(range(m + 1))
    i = 2
    while i * i <= m:
        if s[i] == i:
            for j in range(i * i, m + 1, i):
                if s[j] == j:
                    s[j] = i
        i += 1
    return s


def factor_with(nfac, q):
    """Factor q knowing q divides a number whose prime set is nfac.keys()."""
    f = {}
    r = q
    for p in nfac:
        while r % p == 0:
            r //= p
            f[p] = f.get(p, 0) + 1
    assert r == 1, (q, nfac, r)
    return f


def divisors(fac):
    ds = [1]
    for p, e in fac.items():
        ds = [d * p ** k for d in ds for k in range(e + 1)]
    return ds


def solve_exhaustive(n, spf):
    """Return (x,y,z) with 1<=x<y<z and 4/n = 1/x+1/y+1/z, or None.
    Complete: if it returns None, no such triple exists."""
    sols = []
    for x in range(n // 4 + 1, (3 * n) // 4 + 1):
        p0 = 4 * x - n
        if p0 <= 0:
            continue
        q0 = n * x
        g = gcd(p0, q0)
        p, q = p0 // g, q0 // g
        # prime set of q divides prime set of n*x
        pr = set()
        for v in (n, x):
            t = v
            while t > 1:
                pr.add(spf[t])
                t //= spf[t]
        fq = factor_with({a: 1 for a in pr}, q)
        fq2 = {a: 2 * e for a, e in fq.items()}
        for d in divisors(fq2):
            if d > q:
                continue
            if (q + d) % p:
                continue
            y = (q + d) // p
            e = q * q // d
            if (q + e) % p:
                continue
            z = (q + e) // p
            if x < y < z:
                sols.append((x, y, z))
                return sols[0]
    return None


def check(x, y, z, n):
    from fractions import Fraction
    return (1 <= x < y < z and
            Fraction(4, n) == Fraction(1, x) + Fraction(1, y) + Fraction(1, z))


def main(N, budget):
    t0 = time.time()
    spf = spf_sieve(max(N, 4))
    sol = {}
    exhaustive_ns = []
    lifted = 0
    unresolved = []
    for n in range(3, N + 1):
        # 1. lift from a proper divisor d >= 3 that is already solved
        got = None
        d = n
        t = n
        divs = set()
        while t > 1:
            divs.add(spf[t])
            t //= spf[t]
        # all proper divisors >= 3
        alld = [1]
        f = {}
        t = n
        while t > 1:
            f[spf[t]] = f.get(spf[t], 0) + 1
            t //= spf[t]
        for pp, ee in f.items():
            alld = [a * pp ** k for a in alld for k in range(ee + 1)]
        for d in sorted(alld):
            if 3 <= d < n and d in sol:
                x, y, z = sol[d]
                k = n // d
                got = (x * k, y * k, z * k)
                lifted += 1
                break
        if got is None:
            got = solve_exhaustive(n, spf)
            exhaustive_ns.append(n)
        if got is None:
            unresolved.append(n)
        else:
            assert check(*got, n), (n, got)
            sol[n] = got
        if time.time() - t0 > budget:
            return dict(status="TIMEOUT", reached=n, N=N,
                        exhaustive=len(exhaustive_ns), lifted=lifted,
                        unresolved=unresolved, secs=round(time.time() - t0, 1))
    return dict(status="COMPLETE", reached=N, N=N,
                exhaustive=len(exhaustive_ns), lifted=lifted,
                unresolved=unresolved, secs=round(time.time() - t0, 1),
                sample={k: sol[k] for k in (3, 4, 5, 97, N) if k in sol})


if __name__ == "__main__":
    print(main(int(sys.argv[1]), float(sys.argv[2])))
