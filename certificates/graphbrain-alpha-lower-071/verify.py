#!/usr/bin/env python3
"""Executable certificate for Graph Brain issue #421 lower conjecture 071."""

from __future__ import annotations

import json
import math
from pathlib import Path

GUARD = 1e-6


def rhs(matching_number: int) -> tuple[int, float]:
    raw = 2.0 * math.tan(matching_number) - 2.0
    return math.floor(raw), raw


def certify() -> dict:
    # K28 has alpha=1 and a perfect matching, so mu=14.
    simple_rhs, simple_raw = rhs(14)

    # C7[K4] has alpha(C7)=3.  It has 28 vertices and the explicit pairing
    # (fiber i, vertices 0-1 and 2-3) supplies a perfect matching, so mu=14.
    carrier_rhs, carrier_raw = rhs(14)

    data = {
        "source_id": "graphbrain-alpha-lower-071",
        "statement": "independence_number(x) >= floor(2*tan(matching_number(x)) - 2)",
        "angle_convention": "radians (Sage/Python real tan convention)",
        "guard": GUARD,
        "witnesses": [
            {
                "graph": "K28",
                "order": 28,
                "matching_number": 14,
                "independence_number": 1,
                "raw_rhs": simple_raw,
                "rhs": simple_rhs,
                "distance_to_nearest_integer": min(
                    simple_raw % 1, 1 - simple_raw % 1
                ),
            },
            {
                "graph": "C7[K4]",
                "order": 28,
                "matching_number": 14,
                "independence_number": 3,
                "raw_rhs": carrier_raw,
                "rhs": carrier_rhs,
                "distance_to_nearest_integer": min(
                    carrier_raw % 1, 1 - carrier_raw % 1
                ),
            },
        ],
    }
    for witness in data["witnesses"]:
        assert witness["distance_to_nearest_integer"] > GUARD
        assert witness["independence_number"] < witness["rhs"]
    return data


if __name__ == "__main__":
    actual = certify()
    expected = json.loads(Path(__file__).with_name("certificate.json").read_text())
    assert actual == expected
    print(json.dumps(actual, indent=2))
