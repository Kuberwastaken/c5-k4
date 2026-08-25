#!/usr/bin/env python3
"""A110835: smallest m>0 such that no prime in [n*m, n*(m+1)] inclusive.

Primary implementation: incremental sieve of Eratosthenes via sympy primerange
per interval window. Reports a(n) for n=1..N and flags a(n) < n.
60-second cap enforced by caller.
"""
import sys
from sympy import isprime, sieve


def a_of_n(n, m_cap):
    """Smallest m>=1 with no prime in [n*m, n*(m+1)], searching m<=m_cap.
    Returns None if not found within cap."""
    for m in range(1, m_cap + 1):
        lo = n * m
        hi = n * (m + 1)
        # exact primality test on each integer in the closed interval
        if all(not isprime(p) for p in range(lo, hi + 1)):
            return m
    return None


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    M_CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    bad = []
    for n in range(1, N + 1):
        m = a_of_n(n, M_CAP)
        if m is None:
            print(f"a({n}) > {M_CAP} (search exhausted)")
            break
        flag = "" if m >= n else "  <-- VIOLATES a(n)>=n"
        print(f"a({n}) = {m}{flag}")
        if m < n:
            bad.append((n, m))
    print("violations:", bad)


if __name__ == "__main__":
    main()
