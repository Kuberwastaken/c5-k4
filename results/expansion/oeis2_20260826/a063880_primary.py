#!/usr/bin/env python3
"""A063880 primary path: enumerate members of sigma(n) = 2*usigma(n).
Checks:
  (1) congruence n % 216 == 108 for all members;
  (2) every member n decomposes as d * s with d a MEMBER, s squarefree,
      gcd(d, s) = 1 (existence of a 'primitive below' decomposition);
  (3) primitive members (no proper divisor in the sequence).
"""
import sys


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 500000
    # linear sieve: smallest prime factor + sigma + usigma
    spf = list(range(B + 1))
    primes = []
    for i in range(2, B + 1):
        if spf[i] == i:
            primes.append(i)
        for p in primes:
            if p * i > B:
                break
            spf[p * i] = p
            if i % p == 0:
                break

    sigma = [0] * (B + 1)
    usig = [0] * (B + 1)
    sigma[1] = 1
    usig[1] = 1
    for n in range(2, B + 1):
        p = spf[n]
        # peel p^e
        pe = p
        m = n
        while m % p == 0:
            m //= p
            pe_next = pe * p
            # careful: recompute directly instead
            break
        # simpler: factor n/pow(p,e) already computed? do direct factor peel
        e = 0
        m = n
        while m % p == 0:
            m //= p
            e += 1
        sig_pe = (p ** (e + 1) - 1) // (p - 1)
        usig_pe = p ** e + 1
        if m == 1:
            sigma[n] = sig_pe
            usig[n] = usig_pe
        else:
            sigma[n] = sig_pe * sigma[m]
            usig[n] = usig_pe * usig[m]

    members = [n for n in range(1, B + 1) if sigma[n] == 2 * usig[n]]
    print(f"members up to {B}: {len(members)}")
    print("first:", members[:15])
    bad_cong = [n for n in members if n % 216 != 108]
    print("CROSSING candidates (member with n%216 != 108):", bad_cong[:10])

    mset = set(members)
    nodecomp = []
    for n in members:
        ok = False
        for d in range(1, n + 1):
            if n % d:
                continue
            s = n // d
            if d in mset:
                # s squarefree and gcd(d,s)==1?
                sf = True
                t = s
                p = spf[t] if t > 1 else 1
                while t > 1:
                    p = spf[t]
                    t //= p
                    if t % p == 0:
                        sf = False
                        break
                if sf and d % p != 0 if False else sf:
                    import math
                    if math.gcd(d, s) == 1:
                        ok = True
                        break
        if not ok:
            nodecomp.append(n)
            if len(nodecomp) >= 10:
                break
    print("members WITHOUT primitive-below decomposition:", nodecomp)

    prim = []
    for n in members:
        is_prim = not any(n % d == 0 and d < n and d in mset for d in range(1, n // 2 + 1))
        if is_prim:
            prim.append(n)
    print("primitive members up to B:", prim[:20])


if __name__ == "__main__":
    main()
