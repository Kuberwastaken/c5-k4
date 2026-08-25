#!/usr/bin/env python3
"""A110475 primary path v2: bitset-based pairwise-sum coverage.
S = {p^k, k>=2} U {squarefree pq}; rep = union of (S << s) for s in S.
Python big-int bitmask makes each shift/OR ~O(B/64) words."""
import sys


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
    # SPF sieve
    spf = bytearray()  # not used; use sympy-free linear sieve via smallest prime
    spf = list(range(B + 1))
    i = 2
    while i * i <= B:
        if spf[i] == i:
            step = i
            start = i * i
            for j in range(start, B + 1, step):
                if spf[j] == j:
                    spf[j] = i
        i += 1

    def is_squarefree_semiprime(n):
        # exactly two distinct primes, exponents 1
        p = spf[n]
        if p == n:
            return False
        n2 = n // p
        if n2 % p == 0:
            return False
        return spf[n2] == n2

    S_mask = 0
    cnt = 0
    vals = []
    for p in range(2, B + 1):
        if spf[p] != p:
            continue
        pk = p * p
        while pk <= B:
            vals.append(pk)
            pk *= p
        # squarefree semiprimes p*q, q>p
        q = p
        while True:
            q += 1
            if p * q > B:
                break
            if spf[q] == q:  # q prime, q>p
                vals.append(p * q)
    vals = sorted(set(vals))
    cnt = len(vals)
    print(f"|S| up to {B}: {cnt}")
    Sset = set(vals)
    Sbits = 0
    for v in vals:
        Sbits |= 1 << v
    rep = 0  # sums of TWO elements only (x = y allowed)
    for x in vals:
        if 2 * x > B:
            break
        rep |= Sbits << x
    exceptional = {1, 2, 3, 4, 5, 6, 7, 9, 11}
    bad = []
    for m in range(12, B + 1):
        if m in exceptional:
            continue
        if not ((rep >> m) & 1):
            bad.append(m)
            if len(bad) >= 30:
                break
    print("unrepresentable m outside exceptional set:", bad)
    # sanity: exceptional members unrepresentable?
    print("exceptional represented?:", [(m, (rep >> m) & 1) for m in sorted(exceptional)])


if __name__ == "__main__":
    main()
