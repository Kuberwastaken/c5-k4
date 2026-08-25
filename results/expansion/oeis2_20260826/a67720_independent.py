#!/usr/bin/env python3
"""A067720 independent path 2: NO sympy. Own Pollard-rho factoring,
deterministic Miller-Rabin, and a different totient pipeline.
Searches k in [lo,hi] for members with composite k+1."""
import sys
import random


def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def pollard(n):
    if n % 2 == 0:
        return 2
    while True:
        x = random.randrange(2, n)
        y = x
        c = random.randrange(1, n)
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = __import__("math").gcd(abs(x - y), n)
        if d != n:
            return d


def factor(n, out):
    if n == 1:
        return
    if is_prime(n):
        out[n] = out.get(n, 0) + 1
        return
    d = pollard(n)
    factor(d, out)
    factor(n // d, out)


def phi(n, fac):
    r = n
    for p in fac:
        r = r // p * (p - 1)
    return r


def small_phi_table(n):
    # different construction: product over distinct primes via trial division per value
    table = [0] * (n + 1)
    for v in range(1, n + 1):
        x, res = v, v
        pp = 2
        while pp * pp <= x:
            if x % pp == 0:
                res -= res // pp
                while x % pp == 0:
                    x //= pp
            pp += 1
        if x > 1:
            res -= res // x
        table[v] = res
    return table


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    tab = small_phi_table(hi + 1)
    suspects = []
    count = 0
    for k in range(lo, hi + 1):
        fac = {}
        factor(k * k + 1, fac)
        lhs = phi(k * k + 1, fac)
        rhs = k * tab[k + 1]
        if lhs == rhs:
            count += 1
            if tab[k + 1] != k:  # composite k+1
                suspects.append((k, k + 1))
    print(f"independent scan [{lo},{hi}]: {count} members")
    print("COUNTEREXAMPLES:", suspects)


if __name__ == "__main__":
    main()
