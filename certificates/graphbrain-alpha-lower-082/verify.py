#!/usr/bin/env python3
"""Executable certificate for Graph Brain issue #421 lower conjecture 082."""

from __future__ import annotations

import json
import math
from pathlib import Path

GUARD = 1e-6


def rhs(order: int) -> tuple[int, float]:
    raw = math.log(math.tan(order) ** 2) / math.log(10.0)
    return math.floor(raw), raw


def certify() -> dict:
    # K_11 is the smallest complete-graph witness: alpha(K_n)=1.
    k_rhs, k_raw = rhs(11)

    # C5[K_11]: alpha(C5[K_m])=alpha(C5)=2.  Exhaustively, no three
    # vertices can be independent: at most one may be chosen per clique
    # fiber, and three chosen C5 fibers contain an adjacent pair.
    carrier_rhs, carrier_raw = rhs(55)

    data = {
        "source_id": "graphbrain-alpha-lower-082",
        "statement": "independence_number(x) >= floor(log(tan(order(x))^2)/log(10))",
        "angle_convention": "radians (Sage/Python real tan convention)",
        "guard": GUARD,
        "witnesses": [
            {
                "graph": "K11",
                "order": 11,
                "independence_number": 1,
                "raw_rhs": k_raw,
                "rhs": k_rhs,
                "distance_to_nearest_integer": min(k_raw % 1, 1 - k_raw % 1),
            },
            {
                "graph": "C5[K11]",
                "order": 55,
                "independence_number": 2,
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
