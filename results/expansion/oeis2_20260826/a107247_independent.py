#!/usr/bin/env python3
"""A107247 independent path 2: no sympy.
Terms built by rolling-window addition; primality by trial division;
semiprimality by complete trial-division factorization (feasible at these sizes).
"""
def main():
    N = 30
    f = [0] * (N + 12)
    f[8] = 1
    for n in range(0, N - 2):
        f[n + 9] = sum(f[n:n + 9])

    def factors(v):
        fs, d = {}, 2
        while d * d <= v:
            while v % d == 0:
                fs[d] = fs.get(d, 0) + 1
                v //= d
            d += 1
        if v > 1:
            fs[v] = fs.get(v, 0) + 1
        return fs

    s = 0
    a = {}
    for k in range(N + 2):
        s += f[k] ** 2
        a[k] = s
    lean = lambda n: a[n + 1]
    checks = {9: 6, 10: 22, 11: 86, 13: 1366, 14: 5462, 16: 87382,
              17: 348503, 27: 358201316657}
    ok = True
    for n, expect in sorted(checks.items()):
        fac = factors(lean(n))
        good = lean(n) == expect and len(fac) == 2 and all(e == 1 for e in fac.values())
        ok &= good
        print(n, lean(n), fac, good)
    print("independent verification:", ok)


if __name__ == "__main__":
    main()
