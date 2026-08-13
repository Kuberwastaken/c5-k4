#!/usr/bin/env python3
"""Frozen all-one-edge-deletions trial from the v49 Reed graph."""

from __future__ import annotations

import argparse
import hashlib
import json

from method_v46_reed_weighted_surgery import exact_profile, valid_profile
from method_v49_reed_hard_claw import build, graph_digest


NEIGHBORHOODS = [
    [0, 1, 2, 3, 4, 6, 7, 8, 9],
    [0, 1, 2, 3, 4, 10, 11, 12, 13, 14],
    [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
]
BASE_DIGEST = "d662f7a28227f590393b86cda3834a51805ae6a55f93def531b23f6f00f5a7da"


def base_graph():
    return build(3, 0, NEIGHBORHOODS)


def canonical_menu() -> list[tuple[int, int]]:
    return sorted((min(left, right), max(left, right)) for left, right in base_graph().edges())


def menu_digest(menu: list[tuple[int, int]]) -> str:
    encoded = json.dumps(menu, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def enumerate_menu() -> dict:
    graph = base_graph()
    if graph_digest(graph) != BASE_DIGEST:
        raise RuntimeError("v49 base graph digest mismatch")
    profile = exact_profile(graph)
    if (profile.chi, profile.omega, profile.delta, profile.slack) != (9, 7, 10, 1):
        raise RuntimeError("v49 base coordinates mismatch")
    menu = canonical_menu()
    if len(menu) != 89:
        raise RuntimeError(f"expected 89 base edges, got {len(menu)}")
    return {
        "mode": "menu",
        "base_graph6_sha256": graph_digest(graph),
        "base_profile": profile.as_dict(),
        "menu_size": len(menu),
        "menu": [list(edge) for edge in menu],
        "menu_sha256": menu_digest(menu),
    }


def evaluate() -> dict:
    menu = canonical_menu()
    rows = []
    for index, edge in enumerate(menu):
        graph = base_graph()
        graph.remove_edge(*edge)
        profile = exact_profile(graph)
        if not valid_profile(graph, profile):
            raise RuntimeError(f"invalid exact certificate at row {index}")
        row = {
            "index": index,
            "deleted_edge": list(edge),
            "graph6_sha256": graph_digest(graph),
            "profile": profile.as_dict(),
        }
        rows.append(row)
        if profile.slack < 0:
            return {
                "mode": "evaluate",
                "status": "HALTED_NUMERICAL_CROSSING",
                "menu_sha256": menu_digest(menu),
                "evaluated": len(rows),
                "rows": rows,
                "crossing": row,
            }
    minimum_slack = min(row["profile"]["slack"] for row in rows)
    histogram: dict[str, int] = {}
    coordinate_histogram: dict[str, int] = {}
    for row in rows:
        slack_key = str(row["profile"]["slack"])
        histogram[slack_key] = histogram.get(slack_key, 0) + 1
        profile = row["profile"]
        coordinate_key = f"chi={profile['chi']},omega={profile['omega']},Delta={profile['delta']},slack={profile['slack']}"
        coordinate_histogram[coordinate_key] = coordinate_histogram.get(coordinate_key, 0) + 1
    return {
        "mode": "evaluate",
        "status": "COMPLETE_NO_CROSSING",
        "menu_sha256": menu_digest(menu),
        "evaluated": len(rows),
        "minimum_slack": minimum_slack,
        "slack_histogram": histogram,
        "coordinate_histogram": coordinate_histogram,
        "closest_rows": [row for row in rows if row["profile"]["slack"] == minimum_slack],
        "rows": rows,
        "crossing": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("menu", "evaluate"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = enumerate_menu() if args.mode == "menu" else evaluate()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
