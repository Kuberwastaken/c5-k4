#!/usr/bin/env python3
"""Independent verifier for frozen WOWII 61 cycle/theta bead records."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_cycle_theta_bead_records.jsonl"


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
                raise ValueError("negative degree")
        sequence = sorted(tail, reverse=True)
        states.append(sequence.copy())
    return len(sequence), states


def bfs_diameter(graph: nx.Graph) -> int:
    diameter = 0
    for source in graph:
        distance = {source: 0}
        queue = [source]
        for vertex in queue:
            for neighbor in graph[vertex]:
                if neighbor not in distance:
                    distance[neighbor] = distance[vertex] + 1
                    queue.append(neighbor)
        if len(distance) != graph.number_of_nodes():
            raise ValueError("disconnected")
        diameter = max(diameter, max(distance.values()))
    return diameter


def is_forest(graph: nx.Graph) -> bool:
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


def expected_bead(name: str) -> tuple[nx.Graph, int]:
    if name.startswith("C"):
        order = int(name[1:])
        return nx.cycle_graph(order), order // 2
    match = re.fullmatch(r"Theta\((3|4),(2|3|4|5)\)", name)
    if not match:
        raise ValueError(f"invalid bead name {name}")
    paths, length = map(int, match.groups())
    graph = nx.Graph()
    graph.add_nodes_from((0, 1))
    next_vertex = 2
    for _ in range(paths):
        internal = list(range(next_vertex, next_vertex + length - 1))
        next_vertex += length - 1
        graph.add_edges_from(zip([0, *internal], [*internal, 1]))
    return graph, length


def check_bead(graph: nx.Graph, data: dict[str, object]) -> int:
    expected, rho = expected_bead(str(data["name"]))
    vertices = [int(vertex) for vertex in data["vertices"]]
    if len(vertices) != expected.number_of_nodes() or int(data["order"]) != len(vertices):
        raise ValueError("bead order mismatch")
    mapping = {index: vertices[index] for index in range(len(vertices))}
    expected_edges = {tuple(sorted((mapping[a], mapping[b]))) for a, b in expected.edges()}
    actual_edges = {tuple(sorted(edge)) for edge in graph.subgraph(vertices).edges()}
    if expected_edges != actual_edges:
        raise ValueError("bead edge mismatch")
    if int(data["rho"]) != rho or nx.eccentricity(expected, 0) != rho:
        raise ValueError("bead eccentricity mismatch")
    deleted = int(data["delete"])
    if deleted not in vertices or not is_forest(graph.subgraph(set(vertices) - {deleted})):
        raise ValueError("bead deletion witness mismatch")
    if is_forest(graph.subgraph(vertices)):
        raise ValueError("bead is not cyclic")
    return rho


def verify(row: dict[str, object]) -> None:
    encoded_graph = nx.from_graph6_bytes(str(row["graph6"]).encode())
    graph = nx.Graph()
    graph.add_nodes_from(range(int(row["n"])))
    graph.add_edges_from(tuple(int(vertex) for vertex in edge) for edge in row["edges"])
    if graph.number_of_nodes() != int(row["n"]) or graph.number_of_edges() != int(row["m"]):
        raise ValueError("order/size mismatch")
    if not nx.is_isomorphic(graph, encoded_graph):
        raise ValueError("graph6/labelled-edge-list isomorphism mismatch")
    degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
    residue, trajectory = hh(degrees)
    if degrees != row["degree_sequence"] or trajectory != row["hh_trajectory"]:
        raise ValueError("HH mismatch")
    if residue != int(row["residue"]):
        raise ValueError("residue mismatch")
    left, right = row["left_bead"], row["right_bead"]
    left_rho = check_bead(graph, left)
    right_rho = check_bead(graph, right)
    diameter = bfs_diameter(graph)
    if diameter != 6 + left_rho + right_rho or diameter != int(row["diameter"]):
        raise ValueError("diameter mismatch")
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    u, v = (int(vertex) for vertex in row["attachments"])
    attachments = {
        tuple(sorted((u, int(left["root"])))),
        tuple(sorted((v, int(right["root"])))),
    }
    if not attachments.issubset(bridges):
        raise ValueError("attachment bridge mismatch")
    witness = [int(vertex) for vertex in row["forest_witness"]]
    forest_order = 10 + int(left["order"]) - 1 + int(right["order"]) - 1
    if len(witness) != forest_order or not is_forest(graph.subgraph(witness)):
        raise ValueError("forest lower witness mismatch")
    certificate = row["forest_upper_certificate"]
    if certificate["base_upper"] != 10 or certificate["total_upper"] != forest_order:
        raise ValueError("forest upper mismatch")
    if certificate["left_upper"] != int(left["order"]) - 1:
        raise ValueError("left upper mismatch")
    if certificate["right_upper"] != int(right["order"]) - 1:
        raise ValueError("right upper mismatch")
    ceiling = (diameter + 2) // 3
    residual = forest_order - residue - ceiling
    threshold = forest_order - ceiling + 1
    if residual != int(row["residual"]) or threshold != int(row["required_residue_to_cross"]):
        raise ValueError("final coordinate mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    rows = 0
    candidates = 0
    preserved = 0
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
            preserved += int(row["residue"]) >= 8
    print(json.dumps({
        "event": "INDEPENDENT_REPLAY", "rows": rows,
        "residual_histogram": dict(sorted(residuals.items())),
        "residue_histogram": dict(sorted(residues.items())),
        "diameter_histogram": dict(sorted(diameters.items())),
        "residue_preserved_or_raised": preserved, "candidates": candidates,
        "mismatches": 0, "status": "PASS",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
