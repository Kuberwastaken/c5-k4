#!/usr/bin/env python3
"""A107247 verification path 1 (sympy-based):
recompute a(n) = sum_{k<=n+1} nonacci(k)^2, check every factorization claim in
`known_prime_and_semiprimes`, and hunt for primes a(n), n>8 (bounded).
"""
import sys
from sympy import isprime, factorint


def nonacci_terms(N):
    f = [0] * (N + 1)
    f[8] = 1
    for n in range(0, N - 8):
        f[n + 9] = sum(f[n:n + 9])
    return f


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    f = nonacci_terms(N + 2)
    a = []
    s = 0
    for k in range(0, N + 2):
        s += f[k] ** 2
        a.append(s)
    # a_lean(n) = a[k] for k = n+1
    lean = lambda n: a[n + 1]
    print("head:", a[:20])
    claims = {
        8: ("prime", None),
        9: ("semiprime", None), 10: ("semiprime", None), 11: ("semiprime", None),
        13: ("semiprime", None), 14: ("semiprime", None), 16: ("semiprime", None),
        17: ("semiprime", None), 27: ("semiprime", None),
    }
    ok_all = True
    for n, (kind, _) in sorted(claims.items()):
        v = lean(n)
        fac = factorint(v)
        nfac = sum(e for e in fac.values())
        ok = (nfac == 1 and isprime(v)) if kind == "prime" else (
            nfac == 2 and isprime(v))
        print(f"a({n}) = {v} factors={fac} -> {kind}? {ok}")
        ok_all &= ok
    print("all claims hold:", ok_all)
    # OEIS %C cross-check in their 1-based indices
    print("OEIS 1-based a(28):", lean(27))
    # bounded prime hunt: n > 8
    found = []
    for n in range(9, min(N, int(sys.argv[2]) if len(sys.argv) > 2 else 300) + 1):
        if isprime(lean(n)):
            found.append(n)
            print("PRIME a(%d) = %d (digits=%d)" % (n, lean(n), len(str(lean(n)))))
            break
    print("prime hunt result:", found)


if __name__ == "__main__":
    main()
