#!/usr/bin/env python3
"""Independently classify the fixed points of the literal A113019 function."""

import json


def digital_root_by_repeated_sums(n: int) -> int:
    while n >= 10:
        n = sum(int(digit) for digit in str(n))
    return n


def sequence_value(n: int) -> int:
    digits = len(str(max(1, n)))
    root = 0 if n == 0 else digital_root_by_repeated_sums(n)
    return digits**root


def main() -> None:
    fixed_points: list[tuple[int, int, int]] = []
    for digit_count in range(1, 11):
        for root in range(1, 10):
            n = digit_count**root
            if len(str(n)) == digit_count and digital_root_by_repeated_sums(n) == root:
                assert sequence_value(n) == n
                fixed_points.append((n, digit_count, root))

    fixed_points.sort()
    assert fixed_points == [
        (1, 1, 1),
        (32, 2, 5),
        (387_420_489, 9, 9),
    ]

    # Exact induction certificate for excluding every digit count d >= 11:
    # 11^9 < 10^10, and ((d+1)/d)^9 <= (12/11)^9 < 10.
    assert 11**9 < 10**10
    assert 12**9 < 10 * 11**9

    print(
        json.dumps(
            {
                "target": "OeisA113019 proposed fixed-point classification",
                "fixed_points": [
                    {"n": n, "decimal_digits": digits, "digital_root": root}
                    for n, digits, root in fixed_points
                ],
                "new_witness": 387_420_489,
                "new_witness_equals": "9^9",
                "exhaustive_digit_bound": 10,
                "large_digit_induction_base": "11^9 < 10^10",
                "large_digit_induction_ratio": "(12/11)^9 < 10",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
