#!/usr/bin/env python3
"""Replay the endpoint convention in CountSimultaneousPrimes for f(X)=X+2."""

import json
from math import floor, isqrt


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for divisor in range(2, isqrt(n) + 1):
        if n % divisor == 0:
            return False
    return True


def formal_count(x: float) -> int:
    return sum(is_prime(n + 2) for n in range(max(0, floor(x) + 1)))


def positive_le_count(x: float) -> int:
    return sum(is_prime(n + 2) for n in range(1, max(1, floor(x) + 1)))


def positive_lt_count(x: float) -> int:
    return sum(is_prime(n + 2) for n in range(1, max(1, int(x))))


def main() -> None:
    rows = []
    for x in (0.0, 1.0, 3.0):
        rows.append(
            {
                "x": int(x),
                "formal": formal_count(x),
                "positive_le": positive_le_count(x),
                "positive_lt": positive_lt_count(x),
            }
        )

    assert rows == [
        {"x": 0, "formal": 1, "positive_le": 0, "positive_lt": 0},
        {"x": 1, "formal": 2, "positive_le": 1, "positive_lt": 0},
        {"x": 3, "formal": 3, "positive_le": 2, "positive_lt": 1},
    ]

    print(
        json.dumps(
            {
                "target": "BatemanHornConjecture.CountSimultaneousPrimes",
                "polynomial": "X+2",
                "rows": rows,
                "classification": "endpoint/source-domain defect; asymptotically inert",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
