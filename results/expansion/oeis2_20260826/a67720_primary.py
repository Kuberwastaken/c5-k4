#!/usr/bin/env python3
"""A067720 primary path: find members of phi(k^2+1)=k*phi(k+1) with k+1
composite (counterexamples to "8 is the only exception").
phi(k+1) by SPF sieve; phi(k^2+1) by sympy.factorint. Exact integers.
"""
import sys
from sympy import factorint


def phi_from_factors(fac):
    r = 1
    for p, e in fac.items():
        r *= (p - 1) * p ** (e - 1)
    return r


def spf_phi_sieve(n):
    phi = list(range(n + 1))
    for i in range(2, n + 1):
        if phi[i] == i:  # prime
            for j in range(i, n + 1, i):
                phi[j] -= phi[j] // i
    return phi


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    phi_table = spf_phi_sieve(hi + 1)
    members = []
    suspects = []
    for k in range(lo, hi + 1):
        kp1 = k + 1
        rhs = k * phi_table[kp1]
        lhs = phi_from_factors(factorint(k * k + 1))
        if lhs == rhs:
            members.append(k)
            if not phi_table[kp1] == phi_table[kp1] or True:
                pass
            # primality of k+1: phi[k+1]==k iff prime
            if phi_table[kp1] != k:
                suspects.append((k, kp1))
    print(f"range [{lo},{hi}]: members found = {len(members)}")
    print("first members:", members[:12])
    print("COUNTEREXAMPLES (member with composite k+1):", suspects)
    # sanity: published head must appear
    pub = [1,2,4,6,8,10,16,36,40,66]
    have = set(members)
    if lo <= 1:
        missing = [x for x in pub if x not in have]
        print("missing from published head:", missing)


if __name__ == "__main__":
    main()
