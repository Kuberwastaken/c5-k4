#!/usr/bin/env python3
"""A102722 independent path: high-precision mpmath evaluation of
a(n) = floor(n*H_n - S(n)) with S(n)=sum_{k<=n} floor(n/k) computed exactly by
quotient grouping (integer arithmetic), and n*H_n at 60 significant digits
(error ~1e-55 << distance of a typical value from an integer boundary).
Purpose: verify the asymptotic a(n)/n -> 1-gamma numerically and confirm the
Dirichlet-hyperbola error behaviour  a(n) = (1-gamma)n + O(sqrt n).
"""
import math
import sys
from mpmath import mp, mpf

mp.dps = 60


def sum_floor_div(n):
    total = 0
    k = 1
    while k <= n:
        q = n // k
        last = n // q
        total += q * (last - k + 1)
        k = last + 1
    return total


def harmonic_mp(n):
    # exact rational sum evaluated in high precision pairwise to limit error
    s = mpf(0)
    for k in range(1, n + 1):
        s += mpf(1) / k
    return s


def main():
    Ns = [int(x) for x in sys.argv[1:]] or [1000, 10000]
    gamma = mp.euler
    print(f"{'n':>10} {'a(n)':>14} {'a(n)/n':>16} {'1-gamma':>16} {'ratio-(1-g)':>12}")
    for n in Ns:
        H = harmonic_mp(n)
        S = sum_floor_div(n)
        val = n * H - S
        a = int(mp.floor(val))
        r = a / n
        target = 1 - gamma
        print(f"{n:>10} {a:>14} {mp.nstr(r,12):>16} {mp.nstr(target,12):>16} {mp.nstr(r-target,8):>12}")
    # sqrt-n error check on the largest n
    n = Ns[-1]
    H = harmonic_mp(n)
    a = int(mp.floor(n * H - sum_floor_div(n)))
    err = abs(a - (1 - gamma) * n)
    print(f"abs deviation at n={n}: {mp.nstr(err,6)}  (sqrt(n)={math.isqrt(n)}, n^0.75={int(n**0.75)})")


if __name__ == "__main__":
    main()
