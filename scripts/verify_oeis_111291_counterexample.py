#!/usr/bin/env python3
"""Replay A111291's real-domain counterexample and integer calibration."""

import json
from math import floor, log


def divisor_counts(limit: int) -> list[int]:
    counts = [0] * (limit + 1)
    for divisor in range(1, limit + 1):
        for multiple in range(divisor, limit + 1, divisor):
            counts[multiple] += 1
    return counts


def main() -> None:
    integer_limit = 1_000_000
    tau = divisor_counts(integer_limit)
    prefix = 0
    integer_failures: list[tuple[int, int, float]] = []
    minimum_margin = (float("inf"), 0, 0, 0.0)

    for x in range(1, integer_limit + 1):
        if x % tau[x] == 0:
            prefix += 1
        if x >= 2:
            rhs = x / (2 * log(x))
            margin = prefix - rhs
            if margin < minimum_margin[0]:
                minimum_margin = (margin, x, prefix, rhs)
            if margin < 0:
                integer_failures.append((x, prefix, rhs))

    x = 1.5
    count_at_x = sum(
        1 for k in range(1, floor(x) + 1) if k % tau[k] == 0
    )
    rhs_at_x = x / (2 * log(x))

    assert count_at_x == 1
    assert rhs_at_x > 1
    assert not integer_failures

    print(
        json.dumps(
            {
                "candidate": "FormalConjectures/OEIS/111291.lean:conjecture",
                "x": "3/2",
                "count_refactorable": count_at_x,
                "rhs_approx": rhs_at_x,
                "conjecture_holds": False,
                "integer_calibration_limit": integer_limit,
                "integer_failures": 0,
                "minimum_integer_margin": {
                    "margin": minimum_margin[0],
                    "x": minimum_margin[1],
                    "count": minimum_margin[2],
                    "rhs": minimum_margin[3],
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
