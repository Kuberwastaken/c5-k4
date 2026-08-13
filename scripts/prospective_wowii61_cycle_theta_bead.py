#!/usr/bin/env python3
"""Frozen low-degree cycle/theta bead bridge trial for WOWII 61."""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from prospective_wowii61_realization_spectrum import exact_record, hh_trajectory, is_forest
from prospective_wowii61_realization_surgery import run_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "results/expansion/prospective_wowii61_cycle_theta_bead_ledger.jsonl"
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_cycle_theta_bead_records.jsonl"
BASES = ("KniA@A?_A?G?", "K~Q?PA?_A?G?", "K~IA?Q?_A?G?")
EXPECTED_BASE_SEQUENCE = [6, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1]
EXPECTED_TOTAL = 4_212


@dataclass(frozen=True)
class BeadSpec:
    kind: str
    first: int
    second: int = 0

    @property
    def name(self) -> str:
        return f"C{self.first}" if self.kind == "cycle" else f"Theta({self.first},{self.second})"


def bead_menu() -> tuple[BeadSpec, ...]:
    return tuple(
        [BeadSpec("cycle", length) for length in range(3, 13)]
        + [BeadSpec("theta", paths, length) for paths in (3, 4) for length in range(2, 6)]
    )


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def make_bead(spec: BeadSpec) -> tuple[nx.Graph, int, int, int]:
    """Return bead, root, a feedback deletion vertex, and root eccentricity."""
    if spec.kind == "cycle":
        graph = nx.cycle_graph(spec.first)
        return graph, 0, spec.first - 1, spec.first // 2
    paths, length = spec.first, spec.second
    graph = nx.Graph()
    root, terminal = 0, 1
    graph.add_nodes_from((root, terminal))
    next_vertex = 2
    for _ in range(paths):
        internal = list(range(next_vertex, next_vertex + length - 1))
        next_vertex += length - 1
        graph.add_edges_from(zip([root, *internal], [*internal, terminal]))
    return graph, root, terminal, length


def diametral_pairs(graph: nx.Graph) -> list[tuple[int, int]]:
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    diameter = max(max(row.values()) for row in distances.values())
    return sorted(
        (u, v) for u in graph for v in graph if u < v and distances[u][v] == diameter
    )


def attach(
    base: nx.Graph, u: int, v: int, left_spec: BeadSpec, right_spec: BeadSpec,
) -> tuple[nx.Graph, dict[str, object], dict[str, object]]:
    left_graph, left_root, left_delete, left_rho = make_bead(left_spec)
    right_graph, right_root, right_delete, right_rho = make_bead(right_spec)
    left_map = {node: 12 + node for node in left_graph}
    right_offset = 12 + left_graph.number_of_nodes()
    right_map = {node: right_offset + node for node in right_graph}
    graph = nx.Graph(base)
    graph.add_edges_from((left_map[a], left_map[b]) for a, b in left_graph.edges())
    graph.add_edges_from((right_map[a], right_map[b]) for a, b in right_graph.edges())
    graph.add_edge(u, left_map[left_root])
    graph.add_edge(v, right_map[right_root])
    left = {
        "name": left_spec.name,
        "vertices": sorted(left_map.values()),
        "root": left_map[left_root],
        "delete": left_map[left_delete],
        "order": left_graph.number_of_nodes(),
        "rho": left_rho,
    }
    right = {
        "name": right_spec.name,
        "vertices": sorted(right_map.values()),
        "root": right_map[right_root],
        "delete": right_map[right_delete],
        "order": right_graph.number_of_nodes(),
        "rho": right_rho,
    }
    return graph, left, right


def verify_blocks(
    graph: nx.Graph, base: nx.Graph, u: int, v: int,
    left: dict[str, object], right: dict[str, object],
) -> None:
    if graph.is_multigraph() or graph.is_directed() or nx.number_of_selfloops(graph):
        raise RuntimeError("simplicity failure")
    if not nx.is_connected(graph):
        raise RuntimeError("connectivity failure")
    if set(graph.subgraph(range(12)).edges()) != set(base.edges()):
        raise RuntimeError("base block mismatch")
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    expected = {
        tuple(sorted((u, int(left["root"])))),
        tuple(sorted((v, int(right["root"])))),
    }
    if not expected.issubset(bridges):
        raise RuntimeError("joining bridge mismatch")
    block_edges = []
    left_vertices = set(int(x) for x in left["vertices"])
    right_vertices = set(int(x) for x in right["vertices"])
    for a, b in graph.edges():
        side_a = 0 if a < 12 else (1 if a in left_vertices else 2)
        side_b = 0 if b < 12 else (1 if b in left_vertices else 2)
        if side_a != side_b:
            block_edges.append(tuple(sorted((a, b))))
    if set(block_edges) != expected:
        raise RuntimeError("unexpected inter-block edge")


def evaluate_base(base_index: int, ledger: Path, records: Path) -> dict[str, object]:
    menu = bead_menu()
    if len(menu) != 18:
        raise RuntimeError("frozen bead menu count mismatch")
    base_g6 = BASES[base_index]
    base = nx.from_graph6_bytes(base_g6.encode())
    base_record = exact_record(base)
    for field, expected in {
        "degree_sequence": EXPECTED_BASE_SEQUENCE, "residue": 8,
        "diameter": 4, "forest": 10, "residual": 0,
    }.items():
        if base_record[field] != expected:
            raise RuntimeError(f"base mismatch: {field}")
    pairs = diametral_pairs(base)
    planned = len(pairs) * len(menu) ** 2
    if sum(len(diametral_pairs(nx.from_graph6_bytes(g6.encode()))) for g6 in BASES) * len(menu) ** 2 != EXPECTED_TOTAL:
        raise RuntimeError("global frozen family count mismatch")
    append_jsonl(ledger, {
        "event": "BASE_RECOMPUTATION", "base_index": base_index,
        "base_graph6": base_g6, "diametral_pairs": [list(pair) for pair in pairs],
        "planned": planned, **base_record, "status": "PASS",
        "timestamp_utc": "2026-08-13", "public_action": False,
    })
    residual_hist: Counter[int] = Counter()
    residue_hist: Counter[int] = Counter()
    diameter_hist: Counter[int] = Counter()
    preserved = 0
    candidates = 0
    mismatches = 0
    best_residual: int | None = None
    evaluated = 0
    for u, v in pairs:
        for left_spec in menu:
            for right_spec in menu:
                started = time.monotonic()
                graph, left, right = attach(base, u, v, left_spec, right_spec)
                verify_blocks(graph, base, u, v, left, right)
                degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
                trajectory = hh_trajectory(degrees)
                residue = len(trajectory[-1])
                predicted_diameter = 6 + int(left["rho"]) + int(right["rho"])
                diameter = nx.diameter(graph)
                predicted_forest = 10 + int(left["order"]) - 1 + int(right["order"]) - 1
                witness = [
                    *base_record["forest_witness"],
                    *(x for x in left["vertices"] if x != left["delete"]),
                    *(x for x in right["vertices"] if x != right["delete"]),
                ]
                if diameter != predicted_diameter or len(witness) != predicted_forest or not is_forest(graph.subgraph(witness)):
                    mismatches += 1
                    append_jsonl(ledger, {
                        "event": "CERTIFICATE_MISMATCH", "base_index": base_index,
                        "attachments": [u, v], "left": left_spec.name,
                        "right": right_spec.name, "diameter": diameter,
                        "predicted_diameter": predicted_diameter,
                        "timestamp_utc": "2026-08-13", "public_action": False,
                    })
                    continue
                forest = predicted_forest
                ceiling = math.ceil(diameter / 3)
                residual = forest - residue - ceiling
                threshold = forest - ceiling + 1
                record: dict[str, object] = {
                    "event": "CYCLE_THETA_REALIZATION", "base_index": base_index,
                    "base_graph6": base_g6, "attachments": [u, v],
                    "left_bead": left, "right_bead": right,
                    "n": graph.number_of_nodes(), "m": graph.number_of_edges(),
                    "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
                    "edges": [list(edge) for edge in sorted(tuple(sorted(e)) for e in graph.edges())],
                    "degree_sequence": degrees, "hh_trajectory": trajectory,
                    "residue": residue, "diameter": diameter,
                    "ceil_diameter_over_3": ceiling, "forest": forest,
                    "forest_witness": witness,
                    "forest_upper_certificate": {
                        "base_upper": 10,
                        "left_order": left["order"], "left_upper": int(left["order"]) - 1,
                        "right_order": right["order"], "right_upper": int(right["order"]) - 1,
                        "joining_edges_are_bridges": True, "total_upper": forest,
                    },
                    "required_residue_to_cross": threshold,
                    "residual": residual, "solve_seconds": time.monotonic() - started,
                    "timestamp_utc": "2026-08-13", "public_action": False,
                }
                append_jsonl(records, record)
                evaluated += 1
                residual_hist[residual] += 1
                residue_hist[residue] += 1
                diameter_hist[diameter] += 1
                preserved += residue >= 8
                if best_residual is None or residual < best_residual:
                    append_jsonl(ledger, {
                        "event": "IMPROVED_RESIDUAL", "previous": best_residual,
                        **record,
                    })
                    best_residual = residual
                if residual < 0:
                    candidates += 1
                    append_jsonl(ledger, {**record, "event": "CYCLE_THETA_CANDIDATE"})
    summary: dict[str, object] = {
        "event": "BASE_SUMMARY", "base_index": base_index,
        "base_graph6": base_g6, "diametral_pairs": len(pairs),
        "planned": planned, "evaluated": evaluated,
        "residual_histogram": dict(sorted(residual_hist.items())),
        "residue_histogram": dict(sorted(residue_hist.items())),
        "diameter_histogram": dict(sorted(diameter_hist.items())),
        "minimum_residual": min(residual_hist) if residual_hist else None,
        "residue_preserved_or_raised": preserved, "candidates": candidates,
        "certificate_mismatches": mismatches, "timeouts": 0,
        "status": "CANDIDATE_PENDING_REPLAY" if candidates else (
            "PASS" if not mismatches else "INCONCLUSIVE"
        ),
        "timestamp_utc": "2026-08-13", "public_action": False,
    }
    append_jsonl(ledger, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "base"), required=True)
    parser.add_argument("--base-index", type=int, default=0)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    started = time.monotonic()
    result = run_gate(args.ledger) if args.phase == "gate" else evaluate_base(
        args.base_index, args.ledger, args.records,
    )
    result["seconds"] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

