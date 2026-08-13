#!/usr/bin/env python3
"""Frozen serial cube-chain trial for current WOWII 61."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections import Counter
from pathlib import Path

import networkx as nx

from prospective_wowii61_realization_spectrum import exact_record, hh_trajectory, is_forest
from prospective_wowii61_realization_surgery import run_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "results/expansion/prospective_wowii61_cube_chain_ledger.jsonl"
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_cube_chain_records.jsonl"
BASES = ("KniA@A?_A?G?", "K~Q?PA?_A?G?", "K~IA?Q?_A?G?")
LENGTHS = tuple(range(1, 9))
CUBE_WITNESS = (0, 1, 2, 4, 5)
EXPECTED_TOTAL = 832


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def canonical_cube() -> nx.Graph:
    """Fixed Q3 labelling with root 0, antipode 7, and v0.50 witness labels."""
    original = nx.cubical_graph()
    return nx.relabel_nodes(original, {6: 7, 7: 6}, copy=True)


def cube_gate(ledger: Path) -> bool:
    cube = canonical_cube()
    six_forests = []
    for subset in itertools.combinations(sorted(cube), 6):
        if is_forest(cube.subgraph(subset)):
            six_forests.append(list(subset))
    witness_ok = is_forest(cube.subgraph(CUBE_WITNESS))
    record = {
        "event": "CUBE_GATE", "n": cube.number_of_nodes(),
        "m": cube.number_of_edges(), "root": 0, "port": 7,
        "root_port_distance": nx.shortest_path_length(cube, 0, 7),
        "root_eccentricity": nx.eccentricity(cube, 0),
        "forest": 5, "forest_witness": list(CUBE_WITNESS),
        "six_vertex_subsets_checked": math.comb(8, 6),
        "six_vertex_forests": six_forests,
        "graph6": nx.to_graph6_bytes(cube, header=False).decode().strip(),
        "status": "PASS" if (
            cube.number_of_nodes() == 8 and cube.number_of_edges() == 12
            and nx.shortest_path_length(cube, 0, 7) == 3
            and nx.eccentricity(cube, 0) == 3 and witness_ok and not six_forests
        ) else "INCONCLUSIVE",
        "timestamp_utc": "2026-08-13", "public_action": False,
    }
    append_jsonl(ledger, record)
    return record["status"] == "PASS"


def diametral_pairs(graph: nx.Graph) -> list[tuple[int, int]]:
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    diameter = max(max(row.values()) for row in distances.values())
    return sorted((u, v) for u in graph for v in graph if u < v and distances[u][v] == diameter)


def add_chain(
    graph: nx.Graph, attach_vertex: int, length: int, offset: int,
) -> tuple[list[list[int]], list[tuple[int, int]], int]:
    cube = canonical_cube()
    blocks: list[list[int]] = []
    bridges: list[tuple[int, int]] = []
    previous = attach_vertex
    next_offset = offset
    for _ in range(length):
        mapping = {vertex: next_offset + vertex for vertex in cube}
        graph.add_edges_from((mapping[a], mapping[b]) for a, b in cube.edges())
        bridge = tuple(sorted((previous, mapping[0])))
        graph.add_edge(*bridge)
        bridges.append(bridge)
        block = [mapping[vertex] for vertex in sorted(cube)]
        blocks.append(block)
        previous = mapping[7]
        next_offset += 8
    return blocks, bridges, next_offset


def construct(
    base: nx.Graph, u: int, v: int, left_length: int, right_length: int,
) -> tuple[nx.Graph, list[list[int]], list[list[int]], list[tuple[int, int]]]:
    graph = nx.Graph(base)
    left_blocks, left_bridges, offset = add_chain(graph, u, left_length, 12)
    right_blocks, right_bridges, _ = add_chain(graph, v, right_length, offset)
    return graph, left_blocks, right_blocks, [*left_bridges, *right_bridges]


def verify_decomposition(
    graph: nx.Graph, base: nx.Graph, blocks: list[list[int]], expected_bridges: list[tuple[int, int]],
) -> None:
    if graph.is_multigraph() or graph.is_directed() or nx.number_of_selfloops(graph):
        raise RuntimeError("simplicity mismatch")
    if not nx.is_connected(graph):
        raise RuntimeError("connectivity mismatch")
    if set(graph.subgraph(range(12)).edges()) != set(base.edges()):
        raise RuntimeError("base block mismatch")
    cube = canonical_cube()
    membership = {vertex: index for index, block in enumerate(blocks) for vertex in block}
    actual_cross = set()
    for block in blocks:
        mapping = {index: block[index] for index in range(8)}
        expected_edges = {tuple(sorted((mapping[a], mapping[b]))) for a, b in cube.edges()}
        if set(tuple(sorted(edge)) for edge in graph.subgraph(block).edges()) != expected_edges:
            raise RuntimeError("cube block mismatch")
    for a, b in graph.edges():
        side_a = -1 if a < 12 else membership[a]
        side_b = -1 if b < 12 else membership[b]
        if side_a != side_b:
            actual_cross.add(tuple(sorted((a, b))))
    expected = set(expected_bridges)
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    if actual_cross != expected or not expected.issubset(bridges):
        raise RuntimeError("chain bridge mismatch")


def evaluate_base(base_index: int, ledger: Path, records: Path) -> dict[str, object]:
    base_g6 = BASES[base_index]
    base = nx.from_graph6_bytes(base_g6.encode())
    base_record = exact_record(base)
    for field, expected in {
        "degree_sequence": [6, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1],
        "residue": 8, "diameter": 4, "forest": 10, "residual": 0,
    }.items():
        if base_record[field] != expected:
            raise RuntimeError(f"base mismatch at {field}")
    pairs = diametral_pairs(base)
    total = sum(len(diametral_pairs(nx.from_graph6_bytes(g6.encode()))) for g6 in BASES) * len(LENGTHS) ** 2
    if total != EXPECTED_TOTAL:
        raise RuntimeError("family count mismatch")
    planned = len(pairs) * len(LENGTHS) ** 2
    append_jsonl(ledger, {
        "event": "BASE_RECOMPUTATION", "base_index": base_index,
        "base_graph6": base_g6, "diametral_pairs": [list(pair) for pair in pairs],
        "planned": planned, **base_record, "status": "PASS",
        "timestamp_utc": "2026-08-13", "public_action": False,
    })
    residual_hist: Counter[int] = Counter()
    residue_hist: Counter[int] = Counter()
    diameter_hist: Counter[int] = Counter()
    candidates = 0
    mismatches = 0
    evaluated = 0
    best_residual: int | None = None
    for u, v in pairs:
        for left_length in LENGTHS:
            for right_length in LENGTHS:
                started = time.monotonic()
                graph, left_blocks, right_blocks, bridges = construct(
                    base, u, v, left_length, right_length,
                )
                blocks = [*left_blocks, *right_blocks]
                verify_decomposition(graph, base, blocks, bridges)
                degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
                trajectory = hh_trajectory(degrees)
                residue = len(trajectory[-1])
                predicted_diameter = 4 * (left_length + right_length + 1)
                diameter = nx.diameter(graph)
                forest_order = 10 + 5 * (left_length + right_length)
                witness = [
                    *base_record["forest_witness"],
                    *(block[index] for block in blocks for index in CUBE_WITNESS),
                ]
                if diameter != predicted_diameter or len(witness) != forest_order or not is_forest(graph.subgraph(witness)):
                    mismatches += 1
                    append_jsonl(ledger, {
                        "event": "CERTIFICATE_MISMATCH", "base_index": base_index,
                        "attachments": [u, v], "chain_lengths": [left_length, right_length],
                        "diameter": diameter, "predicted_diameter": predicted_diameter,
                        "timestamp_utc": "2026-08-13", "public_action": False,
                    })
                    continue
                ceiling = math.ceil(diameter / 3)
                residual = forest_order - residue - ceiling
                threshold = forest_order - ceiling + 1
                record: dict[str, object] = {
                    "event": "CUBE_CHAIN_REALIZATION", "base_index": base_index,
                    "base_graph6": base_g6, "attachments": [u, v],
                    "chain_lengths": [left_length, right_length],
                    "left_blocks": left_blocks, "right_blocks": right_blocks,
                    "joining_bridges": [list(edge) for edge in bridges],
                    "n": graph.number_of_nodes(), "m": graph.number_of_edges(),
                    "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
                    "edges": [list(edge) for edge in sorted(tuple(sorted(e)) for e in graph.edges())],
                    "degree_sequence": degrees, "hh_trajectory": trajectory,
                    "residue": residue, "diameter": diameter,
                    "ceil_diameter_over_3": ceiling, "forest": forest_order,
                    "forest_witness": witness,
                    "forest_upper_certificate": {
                        "base_upper": 10, "cube_upper": 5,
                        "cube_blocks": left_length + right_length,
                        "joining_edges_are_bridges": True, "total_upper": forest_order,
                    },
                    "required_residue_to_cross": threshold, "residual": residual,
                    "solve_seconds": time.monotonic() - started,
                    "timestamp_utc": "2026-08-13", "public_action": False,
                }
                append_jsonl(records, record)
                evaluated += 1
                residual_hist[residual] += 1
                residue_hist[residue] += 1
                diameter_hist[diameter] += 1
                if best_residual is None or residual < best_residual:
                    append_jsonl(ledger, {"event": "IMPROVED_RESIDUAL", "previous": best_residual, **record})
                    best_residual = residual
                if residual < 0:
                    candidates += 1
                    append_jsonl(ledger, {**record, "event": "CUBE_CHAIN_CANDIDATE"})
    summary: dict[str, object] = {
        "event": "BASE_SUMMARY", "base_index": base_index, "base_graph6": base_g6,
        "diametral_pairs": len(pairs), "planned": planned, "evaluated": evaluated,
        "residual_histogram": dict(sorted(residual_hist.items())),
        "residue_histogram": dict(sorted(residue_hist.items())),
        "diameter_histogram": dict(sorted(diameter_hist.items())),
        "minimum_residual": min(residual_hist) if residual_hist else None,
        "candidates": candidates, "certificate_mismatches": mismatches,
        "timeouts": 0, "status": "CANDIDATE_PENDING_REPLAY" if candidates else (
            "PASS" if not mismatches else "INCONCLUSIVE"
        ), "timestamp_utc": "2026-08-13", "public_action": False,
    }
    append_jsonl(ledger, summary)
    return summary


def ledger_cube_passed(ledger: Path) -> bool:
    if not ledger.exists():
        return False
    with ledger.open(encoding="utf-8") as handle:
        return any(json.loads(line).get("event") == "CUBE_GATE" and json.loads(line).get("status") == "PASS" for line in handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "cube", "base"), required=True)
    parser.add_argument("--base-index", type=int, default=0)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    started = time.monotonic()
    if args.phase == "gate":
        result = run_gate(args.ledger)
    elif args.phase == "cube":
        passed = cube_gate(args.ledger)
        result = {"event": "CUBE_GATE_SUMMARY", "status": "PASS" if passed else "INCONCLUSIVE"}
    else:
        if not ledger_cube_passed(args.ledger):
            raise RuntimeError("passing cube gate required")
        result = evaluate_base(args.base_index, args.ledger, args.records)
    result["seconds"] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

