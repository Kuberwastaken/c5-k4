#!/usr/bin/env python3
"""Erdos 779 (Deaconescu), upstream 779.lean:

  theorem erdos_779 (n : N) (hn : n >= 1) :
    let P := prod i in range (n+1), nth Nat.Prime i
    exists p, p.Prime /\ (P + p).Prime /\ nth Nat.Prime n < p /\ p < P

nth Nat.Prime is 0-indexed, so range (n+1) = the first n+1 primes and
nth Nat.Prime n is the largest of them.  With the site's 1-indexed N = n+1,
hn : n >= 1 is exactly the site's N > 1.  No index divergence.

Finding a witness p is the whole verification: the literal negation for a
fixed n is "every prime p in (p_max, P) has P+p composite", which is finite but
astronomically large; the positive direction is cheap.
"""
import sys
import time

SMALL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
         67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]
# deterministic MR bound for the first 13 prime bases
DET = 3317044064679887385961981


def is_prime(m, bases=SMALL):
    if m < 2:
        return False
    for p in SMALL:
        if m % p == 0:
            return m == p
    d, s = m - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in bases:
        x = pow(a, d, m)
        if x == 1 or x == m - 1:
            continue
        for _ in range(s - 1):
            x = x * x % m
            if x == m - 1:
                break
        else:
            return False
    return True


def primes_upto(m):
    sieve = bytearray([1]) * (m + 1)
    sieve[0:2] = b"\x00\x00"
    i = 2
    while i * i <= m:
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
        i += 1
    return [i for i in range(m + 1) if sieve[i]]


def main(nmax, budget):
    t0 = time.time()
    pr = primes_upto(2000)
    rows = []
    P = 1
    for n in range(0, nmax + 1):
        P *= pr[n]                      # P = product of first n+1 primes
        if n < 1:
            continue                    # hn : n >= 1
        pmax = pr[n]                    # nth Nat.Prime n, the largest factor
        # least prime p with pmax < p < P and P + p prime
        cand = pmax + 1
        tried = 0
        found = None
        while cand < P:
            if is_prime(cand):
                tried += 1
                if is_prime(P + cand):
                    found = cand
                    break
            cand += 1
        rows.append((n, pmax, P if P < 10 ** 12 else f"{len(str(P))}d",
                     found, tried, (P + found) < DET if found else None))
        if time.time() - t0 > budget:
            return rows, dict(status="TIMEOUT", reached=n,
                              secs=round(time.time() - t0, 1))
    return rows, dict(status="COMPLETE", reached=nmax,
                      secs=round(time.time() - t0, 1))


if __name__ == "__main__":
    rows, st = main(int(sys.argv[1]), float(sys.argv[2]))
    print(st)
    print("n | p_max=nth Prime n | P | least witness p | #primes tried | P+p below det-MR bound")
    for r in rows:
        print(" | ".join(str(x) for x in r))
