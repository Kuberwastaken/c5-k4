#!/usr/bin/env python3
"""Independent replay for frozen WOWII 61 clique-bead bridge records."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_clique_bead_bridge_records.jsonl"


def hh(degrees: list[int]) -> tuple[int, list[list[int]]]:
    sequence = sorted(degrees, reverse=True)
    states = [sequence.copy()]
    while sequence and sequence[0]:
        head, rest = sequence[0], sequence[1:]
        if head > len(rest):
            raise ValueError("nongraphical")
        rest = [value - 1 if index < head else value for index, value in enumerate(rest)]
        if min(rest, default=0) < 0:
            raise ValueError("negative residual degree")
        sequence = sorted(rest, reverse=True)
        states.append(sequence.copy())
    return len(sequence), states


def bfs_diameter(graph: nx.Graph) -> int:
    result = 0
    for source in graph:
        distances = {source: 0}
        queue = [source]
        for vertex in queue:
            for neighbor in graph[vertex]:
                if neighbor not in distances:
                    distances[neighbor] = distances[vertex] + 1
                    queue.append(neighbor)
        if len(distances) != graph.number_of_nodes():
            raise ValueError("disconnected")
        result = max(result, max(distances.values()))
    return result


def forest(graph: nx.Graph) -> bool:
    seen: set[int] = set()
    for start in graph:
        if start in seen:
            continue
        stack = [(start, -1)]
        seen.add(start)
        while stack:
            vertex, parent = stack.pop()
            for neighbor in graph[vertex]:
                if neighbor == parent:
                    continue
                if neighbor in seen:
                    return False
                seen.add(neighbor)
                stack.append((neighbor, vertex))
    return True


def verify_row(row: dict[str, object]) -> None:
    graph = nx.from_graph6_bytes(str(row["graph6"]).encode())
    if graph.number_of_nodes() != int(row["n"]) or graph.number_of_edges() != int(row["m"]):
        raise ValueError("order/size mismatch")
    if sorted([list(sorted(edge)) for edge in graph.edges()]) != row["edges"]:
        raise ValueError("edge-list mismatch")
    degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
    residue, trajectory = hh(degrees)
    if degrees != row["degree_sequence"] or trajectory != row["hh_trajectory"]:
        raise ValueError("degree/HH mismatch")
    if residue != int(row["residue"]):
        raise ValueError("residue mismatch")
    diameter = bfs_diameter(graph)
    if diameter != int(row["diameter"]) or diameter != 8:
        raise ValueError("diameter mismatch")
    witness = [int(vertex) for vertex in row["forest_witness"]]
    if len(witness) != 14 or not forest(graph.subgraph(witness)):
        raise ValueError("forest witness mismatch")
    base = nx.from_graph6_bytes(str(row["base_graph6"]).encode())
    q, r = (int(value) for value in row["clique_sizes"])
    left = list(range(12, 12 + q))
    right = list(range(12 + q, 12 + q + r))
    if graph.subgraph(left).number_of_edges() != q * (q - 1) // 2:
        raise ValueError("left clique mismatch")
    if graph.subgraph(right).number_of_edges() != r * (r - 1) // 2:
        raise ValueError("right clique mismatch")
    if set(graph.subgraph(range(12)).edges()) != set(base.edges()):
        raise ValueError("base mismatch")
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    attachments = [int(value) for value in row["attachments"]]
    expected_bridges = {
        tuple(sorted((attachments[0], left[0]))),
        tuple(sorted((attachments[1], right[0]))),
    }
    if not expected_bridges.issubset(bridges):
        raise ValueError("bridge mismatch")
    # The base's exact forest upper bound is 10; each complete block has upper
    # bound 2. Bridges create no cross-block cycle, so the additive upper is 14.
    certificate = row["forest_upper_certificate"]
    if certificate["base_upper"] != 10 or certificate["left_upper"] != 2:
        raise ValueError("upper certificate mismatch")
    if certificate["right_upper"] != 2 or certificate["total_upper"] != 14:
        raise ValueError("upper certificate mismatch")
    residual = 14 - residue - (diameter + 2) // 3
    if residual != int(row["residual"]):
        raise ValueError("residual mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    residuals: Counter[int] = Counter()
    residues: Counter[int] = Counter()
    rows = 0
    with args.records.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            verify_row(row)
            rows += 1
            residuals[int(row["residual"])] += 1
            residues[int(row["residue"])] += 1
    print(json.dumps({
        "event": "INDEPENDENT_REPLAY",
        "rows": rows,
        "residual_histogram": dict(sorted(residuals.items())),
        "residue_histogram": dict(sorted(residues.items())),
        "mismatches": 0,
        "status": "PASS",
    }, sort_keys=True))


if __name__ == "__main__":
    main()

