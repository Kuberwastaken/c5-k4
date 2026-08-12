#!/usr/bin/env python3
"""Independent verification of the WOWII 61 Trial H1 machine record."""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "results/expansion/method_v02_61_search.jsonl"


def hh_residue(graph: nx.Graph) -> int:
    seq = sorted(dict(graph.degree()).values(), reverse=True)
    while seq and seq[0]:
        d, seq = seq[0], seq[1:]
        if d > len(seq):
            raise AssertionError("nongraphical sequence")
        seq = sorted([x - 1 if i < d else x for i, x in enumerate(seq)], reverse=True)
        if min(seq, default=0) < 0:
            raise AssertionError("negative HH entry")
    return len(seq)


def cyclic_independent_forest(graph: nx.Graph) -> int:
    nodes = list(graph)
    best = 0
    for mask in range(1 << len(nodes)):
        size = bin(mask).count("1")
        if size <= best:
            continue
        subset = [nodes[i] for i in range(len(nodes)) if mask & (1 << i)]
        sub = graph.subgraph(subset)
        if not nx.cycle_basis(sub):
            best = size
    return best


def main() -> None:
    rows = [json.loads(line) for line in LOG.read_text().splitlines()]
    gate = next(row for row in rows if row["kind"] == "database_gate")
    components = [row for row in rows if row["kind"] == "switch_component"]
    summary = next(row for row in rows if row["kind"] == "summary")

    assert gate["controls"] == 1023
    assert not gate["violations"]
    assert summary["degree_sequence_components"] == 228
    assert summary["evaluated_sum"] == 968
    assert summary["timeouts"] == 0
    assert summary["minimum_residual"] == 0
    assert not summary["negative_components"]

    residuals: Counter[int] = Counter()
    diameters: Counter[int] = Counter()
    checked: set[str] = set()
    for component in components:
        residuals.update({int(k): int(v) for k, v in component["residual_histogram"].items()})
        diameters.update({int(k): int(v) for k, v in component["diameter_histogram"].items()})
        for record in component["best"]:
            code = record["graph6"]
            if code in checked:
                continue
            checked.add(code)
            graph = nx.from_graph6_bytes(code.encode())
            assert nx.is_connected(graph)
            assert hh_residue(graph) == record["residue"]
            assert nx.diameter(graph) == record["diameter"]
            assert cyclic_independent_forest(graph) == record["forest"]
            assert record["residual"] == (
                record["forest"] - record["residue"] - math.ceil(record["diameter"] / 3)
            )
    assert residuals == Counter({1: 592, 2: 337, 0: 36, 3: 3})
    assert diameters == Counter({2: 448, 3: 417, 4: 92, 5: 10, 6: 1})

    principal = next(row for row in components if row["base"] == "C5[K2]")
    assert principal["full_connected_regular_class"] == 60
    assert principal["evaluated"] == 57
    assert principal["layers"] == {"0": 1, "1": 3, "2": 16, "3": 28, "4": 9}
    assert principal["diameter_histogram"] == {"2": 57}
    assert principal["residual_histogram"] == {"1": 2, "2": 52, "3": 3}

    # Directly verify the stated wall example, independent of the discovery
    # optimizer and without trusting its saved witness.
    wall = nx.from_graph6_bytes(b"EhU?")
    assert sorted(dict(wall.degree()).values(), reverse=True) == [3, 2, 2, 2, 2, 1]
    assert hh_residue(wall) == 3
    assert nx.diameter(wall) == 4
    assert cyclic_independent_forest(wall) == 5
    print(f"PASS: {len(checked)} saved extrema independently recomputed; aggregate 968 graphs")


if __name__ == "__main__":
    main()
