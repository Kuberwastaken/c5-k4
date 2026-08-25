#!/usr/bin/env python3
"""A110475 independent path 2: build S by trial-division factorization of every
n (no shared sieve code with primary), then for each m decide representability
by scanning pairs directly. Verifies unrepresentable set == {1..7,9,11}."""
import sys


def a_of(n):
    x, d, c = n, 0, 0
    p = 2
    while p * p <= x:
        if x % p == 0:
            d += 1
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            if e > 1:
                c += 1
        p += 1
    if x > 1:
        d += 1
    return (d - 1) + c


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    vals = [n for n in range(1, B + 1) if a_of(n) == 1]
    sset = set(vals)
    exceptional = {1, 2, 3, 4, 5, 6, 7, 9, 11}
    bad = []
    for m in range(1, B + 1):
        ok = any((m - x) in sset for x in vals if x <= m // 2)
        if not ok and m not in exceptional:
            bad.append(m)
            if len(bad) > 20:
                break
        if ok and m in exceptional:
            print("CONTRADICTION: exceptional member", m, "is representable")
    print(f"independent scan to {B}: unrepresentable outside exceptional:", bad)
    # spot checks
    for m, expect in [(15, True), (21, True), (27, True), (11, False), (4, False)]:
        got = any((m - x) in sset for x in vals if x <= m // 2)
        print(f"m={m} representable={got} expected={expect}", "OK" if got == expect else "MISMATCH")


if __name__ == "__main__":
    main()
