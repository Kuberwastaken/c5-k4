#!/usr/bin/env python3
"""Independent verifier for the frozen WOWII 61 cube-chain records."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_cube_chain_records.jsonl"
WITNESS = (0, 1, 2, 4, 5)


def cube() -> nx.Graph:
    return nx.relabel_nodes(nx.cubical_graph(), {6: 7, 7: 6}, copy=True)


def hh(degrees: list[int]) -> tuple[int, list[list[int]]]:
    sequence = sorted(degrees, reverse=True)
    states = [sequence.copy()]
    while sequence and sequence[0] > 0:
        head = sequence[0]
        tail = sequence[1:]
        if head > len(tail):
            raise ValueError("nongraphical")
        for index in range(head):
            tail[index] -= 1
            if tail[index] < 0:
                raise ValueError("negative HH value")
        sequence = sorted(tail, reverse=True)
        states.append(sequence.copy())
    return len(sequence), states


def diameter(graph: nx.Graph) -> int:
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
        seen.add(start)
        stack = [(start, -1)]
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


def verify(row: dict[str, object]) -> None:
    graph = nx.Graph()
    graph.add_nodes_from(range(int(row["n"])))
    graph.add_edges_from(tuple(int(value) for value in edge) for edge in row["edges"])
    encoded = nx.from_graph6_bytes(str(row["graph6"]).encode())
    if not nx.is_isomorphic(graph, encoded):
        raise ValueError("graph6 mismatch")
    if graph.number_of_edges() != int(row["m"]):
        raise ValueError("size mismatch")
    degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
    residue, trajectory = hh(degrees)
    if degrees != row["degree_sequence"] or trajectory != row["hh_trajectory"]:
        raise ValueError("HH trajectory mismatch")
    if residue != int(row["residue"]):
        raise ValueError("residue mismatch")
    left_blocks = [[int(value) for value in block] for block in row["left_blocks"]]
    right_blocks = [[int(value) for value in block] for block in row["right_blocks"]]
    blocks = [*left_blocks, *right_blocks]
    canonical = cube()
    for block in blocks:
        expected = {
            tuple(sorted((block[a], block[b]))) for a, b in canonical.edges()
        }
        actual = {tuple(sorted(edge)) for edge in graph.subgraph(block).edges()}
        if actual != expected:
            raise ValueError("cube block mismatch")
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    joining = {tuple(sorted(int(value) for value in edge)) for edge in row["joining_bridges"]}
    if not joining.issubset(bridges) or len(joining) != len(blocks):
        raise ValueError("joining bridge mismatch")
    measured_diameter = diameter(graph)
    a, b = (int(value) for value in row["chain_lengths"])
    if measured_diameter != 4 * (a + b + 1) or measured_diameter != int(row["diameter"]):
        raise ValueError("diameter mismatch")
    witness = [int(value) for value in row["forest_witness"]]
    predicted_forest = 10 + 5 * (a + b)
    if len(witness) != predicted_forest or not forest(graph.subgraph(witness)):
        raise ValueError("forest witness mismatch")
    certificate = row["forest_upper_certificate"]
    if certificate["base_upper"] != 10 or certificate["cube_upper"] != 5:
        raise ValueError("forest upper coordinate mismatch")
    if certificate["cube_blocks"] != a + b or certificate["total_upper"] != predicted_forest:
        raise ValueError("forest upper sum mismatch")
    ceiling = (measured_diameter + 2) // 3
    residual = predicted_forest - residue - ceiling
    threshold = predicted_forest - ceiling + 1
    if residual != int(row["residual"]) or threshold != int(row["required_residue_to_cross"]):
        raise ValueError("final coordinate mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    rows = 0
    candidates = 0
    residuals: Counter[int] = Counter()
    residues: Counter[int] = Counter()
    diameters: Counter[int] = Counter()
    with args.records.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            verify(row)
            rows += 1
            residuals[int(row["residual"])] += 1
            residues[int(row["residue"])] += 1
            diameters[int(row["diameter"])] += 1
            candidates += int(row["residual"]) < 0
    print(json.dumps({
        "event": "INDEPENDENT_REPLAY", "rows": rows,
        "residual_histogram": dict(sorted(residuals.items())),
        "residue_histogram": dict(sorted(residues.items())),
        "diameter_histogram": dict(sorted(diameters.items())),
        "minimum_residual": min(residuals), "candidates": candidates,
        "mismatches": 0, "status": "PASS",
    }, sort_keys=True))


if __name__ == "__main__":
    main()

