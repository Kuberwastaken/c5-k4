#!/usr/bin/env python3
"""A113257 Q2 square-exclusion scan (committed for reproducibility).
A perfect square is 0 or a quadratic residue mod every prime; each failing
(a(n) mod p) is an explicit proof that a(n) is not a square.
"""
PRIMES = [3,5,7,11,13,17,19,23,29,31,37,41]
QR = {p: {pow(x, 2, p) for x in range(p)} for p in PRIMES}
KILL_PRIMES = [113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251]
QR_KILL = {p: {pow(x, 2, p) for x in range(p)} for p in KILL_PRIMES}


def a_mod(n, p):
    s = 0
    for i in range(1, n + 1):
        s = (s + pow(i * i, (n - i + 1) * (n - i + 1), p)) % p
    return s


def main():
    N = int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 2500
    survivors = []
    for n in range(3, N + 1):
        ps = list(QR.items())
        if all(a_mod(n, p) in s for p, s in ps):
            kill = [p for p in KILL_PRIMES if a_mod(n, p) not in QR_KILL[p]]
            status = f"KILLED by p={kill[0]}" if kill else "still standing"
            print(f"survivor n={n}: {status}")
            if kill:
                continue
            survivors.append(n)
    print("unexcluded square candidates up to n=%d: %s" % (N, survivors))


if __name__ == "__main__":
    main()
