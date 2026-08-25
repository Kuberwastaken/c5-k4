#!/usr/bin/env python3
"""A116150 primary path: a(n) = sum_{j=1..n} (3^j + (-2)^j).
Verify OEIS-claimed primes at n=11,17,71,91,431; then bounded hunt for the
next prime after n=431 using parity filter (a(n) odd iff ceil(n/2) odd,
i.e. n ≡ 2,3 mod 4) plus small-prime modular filters.
"""
import sys
import time
from sympy import isprime


def a_val(n):
    s = 0
    t3, t2 = 0, 0
    for j in range(1, n + 1):
        t3 += 3 ** j
    # closed form for speed: sum 3^j = (3^(n+1)-3)/2 ; sum (-2)^j via loop
    tm = 0
    v = -2
    p = -2
    for j in range(1, n + 1):
        tm += p
        p *= -2
    return (3 ** (n + 1) - 3) // 2 + tm


def a_mod(n, p):
    s = 0
    p3, pm = 1, 1  # 3^j mod p, (-2)^j mod p
    t3 = 0
    tm = 0
    for _ in range(n):
        p3 = p3 * 3 % p
        pm = pm * (-2 % p) % p
        t3 = (t3 + p3) % p
        tm = (tm + pm) % p
    return (t3 + tm) % p


def main():
    mode = sys.argv[1]
    if mode == "verify":
        for n in (11, 17, 71, 91, 431):
            v = a_val(n)
            print(f"a({n}) prime={isprime(v)} digits~{v.bit_length()*30103//100000}")
            assert a_mod(n, 97) == v % 97
        # head check
        head = [sum(3**j + (-2)**j for j in range(1, i+1)) for i in range(1, 6)]
        print("head:", head)
    elif mode == "hunt":
        lo = int(sys.argv[2])
        hi = int(sys.argv[3])
        cap = float(sys.argv[4]) if len(sys.argv) > 4 else 55.0
        SMALL = [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73]
        t0 = time.time()
        tested = []
        for n in range(lo, hi + 1):
            if time.time() - t0 > cap:
                print(f"time cap at n={n}; bracket: no prime in [{lo},{n})")
                break
            if n % 4 not in (2, 3):
                continue
            if any(a_mod(n, p) == 0 for p in SMALL):
                continue
            v = a_val(n)
            tested.append(n)
            if isprime(v):
                print(f"PRIME at n={n} (digits~{v.bit_length()*30103//100000})")
                break
        else:
            print(f"bracket: no prime in [{lo},{hi}]")
        print("full-tested survivors:", tested)


if __name__ == "__main__":
    main()
