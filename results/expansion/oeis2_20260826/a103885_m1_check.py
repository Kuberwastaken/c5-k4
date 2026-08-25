#!/usr/bin/env python3
"""A103885: verify the m=1 instance of the recurrence conjecture exactly.
Unknown quadratic P(x)=p2 x^2+p1 x+p0, Q(x)=q2 x^2+q1 x+q0.
Recurrence (m=1):
 (2n+1)(2n+2) P(n) a(n+1) - (2n-1)(2n-2) P(-n) a(n-1) = Q(n^2) a(n).
Build exact rational linear system from a(n) data; check consistency."""
from fractions import Fraction
from itertools import product


def a_of(n):
    if n == 0:
        return Fraction(1)
    from math import comb
    return sum(Fraction(comb(n, k) * comb(2 * n + k - 1, n - 1)) for k in range(n + 1))


def main():
    N = 14  # equations from n=1..N
    a = [a_of(i) for i in range(N + 3)]

    def P_basis(x):
        # P(n) coefficients on (p0,p1,p2): 1, x, x^2 ; P(-n) uses -n
        return [(Fraction(1), Fraction(x), Fraction(x * x))]

    rows = []
    rhs = []
    for n in range(1, N + 1):
        c1 = (2 * n + 1) * (2 * n + 2) * a[n + 1]
        c2 = -(2 * n - 1) * (2 * n - 2) * a[n - 1]
        # term1 uses P(n): p0 + p1 n + p2 n^2 scaled by c1
        # term2 uses P(-n): p0 - p1 n + p2 n^2 scaled by c2
        row = [
            c1 * 1 + c2 * 1,
            c1 * n + c2 * (-n),
            c1 * n * n + c2 * n * n,
            -a[n] * n ** 4,
            -a[n] * n ** 2,
            -a[n],
        ]
        rows.append([Fraction(x) for x in row])
        rhs.append(Fraction(0))

    # solve homogeneous system: find nonzero solution via elimination
    import copy
    M = copy.deepcopy(rows)
    R = len(M)
    C = len(M[0])
    pivots = []
    r = 0
    for c in range(C):
        piv = None
        for i in range(r, R):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [x / pv for x in M[r]]
        for i in range(R):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == R:
            break
    free = [c for c in range(C) if c not in pivots]
    print(f"rank {r} of {C} unknowns -> solution space dim {len(free)}")
    if not free:
        print("only trivial solution => NO valid P,Q => CONJECTURE FALSE at m=1!")
        return
    # construct one solution: set first free var = 1
    sol = [Fraction(0)] * C
    sol[free[0]] = Fraction(1)
    for i, c in enumerate(pivots):
        sol[c] = -sum(M[i][cc] * sol[cc] for cc in free) if False else M[i][free[0]] * (-1)
    # verify all equations with this solution
    ok = True
    for i, n in enumerate(range(1, N + 1)):
        val = sum(rows[i][j] * sol[j] for j in range(C))
        if val != 0:
            ok = False
    p0, p1, p2, q0, q1, q2 = sol
    print(f"P(x) = {p2}x^2 + {p1}x + {p0}")
    print(f"Q(x) = {q2}x^2 + {q1}x + {q0}")
    # check claimed P(2,n) = 5n^2-5n+1 symmetry P(n)==P(1-n) and Q form
    sym = all(sol[0] + sol[1]*x + sol[2]*x*x == sol[0] + sol[1]*(1-x) + sol[2]*(1-x)**2 for x in range(-5, 6))
    print("recurrence consistent for all tested n:", ok)
    print("P symmetric about 1/2:", sym)


if __name__ == "__main__":
    main()
