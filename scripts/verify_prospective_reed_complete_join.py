#!/usr/bin/env python3
"""Independent verifier for the frozen Reed complete-join trial."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_reed_complete_join_ledger.jsonl"


def main() -> None:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    discovery = [row for row in rows if row.get("stage") == "discovery"]
    assert len(discovery) == 48
    for row in discovery:
        graph = nx.from_graph6_bytes(row["graph6"].encode())
        m, t = row["m_parameter"], row["t_parameter"]
        universal = {v for v in graph if graph.degree(v) == len(graph) - 1}
        assert len(universal) == t
        carrier = graph.subgraph(set(graph) - universal).copy()
        assert len(carrier) == 5 * m
        assert all(graph.has_edge(u, v) for u in universal for v in carrier)
        assert nx.is_clique(graph, universal) if hasattr(nx, "is_clique") else all(
            graph.has_edge(u, v) for u in universal for v in universal if u != v)

        alpha = max(map(len, nx.find_cliques(nx.complement(carrier))))
        omega_carrier = max(map(len, nx.find_cliques(carrier)))
        assert alpha == 2 and omega_carrier == 2 * m

        classes = row["color_classes"]
        coloring = {vertex: color for color, vertices in enumerate(classes) for vertex in vertices}
        assert set(coloring) == set(graph)
        assert all(coloring[u] != coloring[v] for u, v in graph.edges())

        chi_lower = (len(carrier) + alpha - 1) // alpha + t
        assert len(classes) == chi_lower == row["chi"]
        omega = omega_carrier + t
        delta = max(dict(graph.degree()).values())
        assert (omega, delta) == (row["omega"], row["Delta"])
        assert omega + delta + 2 - 2 * chi_lower == row["slack"] == 2 * m
        assert row["prediction_match"]
    print("PASS independent join-decomposition verifier: 48/48 rows")


if __name__ == "__main__":
    main()
