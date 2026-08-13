#!/usr/bin/env python3
"""Independent aggregate replay of the frozen private-leaf cone v2."""

from __future__ import annotations

import hashlib
import json


def main() -> None:
    rows = []
    for q in range(2, 33):
        for maximum in range(1, 33):
            degree = q - 1 + maximum
            if degree < 9:
                continue
            for tail_sum in range(q - 1, (q - 1) * maximum + 1):
                rows.append((degree, q, maximum, tail_sum))
    rows.sort()

    digest = hashlib.sha256()
    negatives = 0
    equalities = 0
    even_rows = 0
    odd_rows = 0
    minimum = None
    for degree, q, maximum, tail_sum in rows:
        order = q + maximum + tail_sum
        indep_domination = 1 + tail_sum
        if degree % 2 == 0:
            even_rows += 1
            raw = (degree * degree + 4) * order - (degree + 2) ** 2 * indep_domination
            formula = degree * (degree * degree - 4 * tail_sum)
        else:
            odd_rows += 1
            raw = ((degree * degree + 3) * order
                   - (degree + 1) * (degree + 3) * indep_domination)
            formula = degree * (degree * degree - 1 - 4 * tail_sum)
        assert raw == formula
        assert tail_sum <= (q - 1) * maximum
        if degree % 2 == 0:
            assert degree * degree >= 4 * tail_sum
        else:
            assert degree * degree - 1 >= 4 * tail_sum
        digest.update(f"{degree},{q},{maximum},{tail_sum},{raw}\n".encode())
        negatives += raw < 0
        equalities += raw == 0
        minimum = raw if minimum is None else min(minimum, raw)

    result = {
        "status": "PASS",
        "rows": len(rows),
        "even_rows": even_rows,
        "odd_rows": odd_rows,
        "negative_count": negatives,
        "equality_count": equalities,
        "minimum_residual": minimum,
        "rows_sha256": digest.hexdigest(),
    }
    expected = {
        "rows": 246854,
        "even_rows": 123280,
        "odd_rows": 123574,
        "negative_count": 0,
        "equality_count": 82,
        "minimum_residual": 0,
        "rows_sha256": "0f7c13e9ffb5763ef4cc01503e29b58a805e9667a188861aa39f24ca0ce48acd",
    }
    assert all(result[key] == value for key, value in expected.items())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
