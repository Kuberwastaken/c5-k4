#!/usr/bin/env python3
"""Independently replay the counterexample to formalized OEIS A109074."""

from fractions import Fraction
from math import comb
import json


def frac(n: int) -> Fraction:
    return Fraction(comb(6 * n - 2, 2 * n), 2 * comb(4 * n - 1, 2 * n))


def formal_b(n: int) -> int:
    return comb(3 * n, n) // (2 * n + 1)


def main() -> None:
    n = 1
    lhs = frac(n)
    b_n = formal_b(n)
    b_next = formal_b(n + 1)
    rhs = Fraction(b_next, b_n)

    assert lhs == 1
    assert b_n == 1
    assert b_next == 3
    assert rhs == 3
    assert lhs != rhs

    print(
        json.dumps(
            {
                "candidate": "FormalConjectures/OEIS/109074.lean:conjecture",
                "n": n,
                "frac_n": str(lhs),
                "formal_b_n": b_n,
                "formal_b_n_plus_1": b_next,
                "formal_rhs": str(rhs),
                "conjecture_holds": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
