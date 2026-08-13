#!/usr/bin/env python3
"""Frozen clique-bead bridge trial for the order-12 WOWII 61 corridor."""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

from prospective_wowii61_realization_spectrum import exact_record, hh_trajectory, is_forest
from prospective_wowii61_realization_surgery import run_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "results/expansion/prospective_wowii61_clique_bead_bridge_ledger.jsonl"
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_clique_bead_bridge_records.jsonl"
BASES = ("KniA@A?_A?G?", "K~Q?PA?_A?G?", "K~IA?Q?_A?G?")
SIZES = tuple(range(3, 11))
EXPECTED_BASE_SEQUENCE = [6, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1]


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def diametral_pairs(graph: nx.Graph) -> list[tuple[int, int]]:
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    diameter = max(max(row.values()) for row in distances.values())
    return sorted(
        (u, v) for u in sorted(graph) for v in sorted(graph)
        if u < v and distances[u][v] == diameter
    )


def attach_beads(
    base: nx.Graph, u: int, v: int, q: int, r: int,
) -> tuple[nx.Graph, list[int], list[int]]:
    graph = nx.Graph(base)
    offset = base.number_of_nodes()
    left = list(range(offset, offset + q))
    right = list(range(offset + q, offset + q + r))
    graph.add_edges_from((a, b) for i, a in enumerate(left) for b in left[i + 1:])
    graph.add_edges_from((a, b) for i, a in enumerate(right) for b in right[i + 1:])
    graph.add_edge(u, left[0])
    graph.add_edge(v, right[0])
    return graph, left, right


def iso_key(graph: nx.Graph) -> tuple[int, tuple[int, ...], str]:
    return (
        graph.number_of_nodes(),
        tuple(sorted((degree for _, degree in graph.degree()), reverse=True)),
        nx.weisfeiler_lehman_graph_hash(graph, iterations=max(3, graph.number_of_nodes())),
    )


def verify_decomposition(
    graph: nx.Graph,
    base: nx.Graph,
    u: int,
    v: int,
    left: list[int],
    right: list[int],
) -> None:
    if graph.is_multigraph() or graph.is_directed() or nx.number_of_selfloops(graph):
        raise RuntimeError("simplicity check failed")
    if not nx.is_connected(graph):
        raise RuntimeError("construction disconnected")
    if set(graph.subgraph(range(12)).edges()) != set(base.edges()):
        raise RuntimeError("base block changed")
    if graph.subgraph(left).number_of_edges() != math.comb(len(left), 2):
        raise RuntimeError("left bead is not complete")
    if graph.subgraph(right).number_of_edges() != math.comb(len(right), 2):
        raise RuntimeError("right bead is not complete")
    cross = []
    for a, b in graph.edges():
        blocks = (a < 12, a in left, a in right), (b < 12, b in left, b in right)
        if blocks[0] != blocks[1]:
            cross.append(tuple(sorted((a, b))))
    if sorted(cross) != sorted(((u, left[0]), (v, right[0]))):
        raise RuntimeError(f"unexpected block edges: {cross}")
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    if tuple(sorted((u, left[0]))) not in bridges or tuple(sorted((v, right[0]))) not in bridges:
        raise RuntimeError("attachment edge is not a bridge")


def evaluate_base(base_index: int, ledger: Path, records: Path) -> dict[str, object]:
    if not 0 <= base_index < len(BASES):
        raise ValueError("base index out of range")
    base_g6 = BASES[base_index]
    base = nx.from_graph6_bytes(base_g6.encode())
    base_record = exact_record(base)
    for field, expected in {
        "degree_sequence": EXPECTED_BASE_SEQUENCE,
        "residue": 8,
        "diameter": 4,
        "forest": 10,
        "residual": 0,
    }.items():
        if base_record[field] != expected:
            raise RuntimeError(f"base {base_g6} mismatch at {field}")
    pairs = diametral_pairs(base)
    total_planned = len(pairs) * len(SIZES) ** 2
    if total_planned > 8_000:
        raise RuntimeError("mechanical base family exceeds global frozen cap")
    append_jsonl(ledger, {
        "event": "BASE_RECOMPUTATION", "base_index": base_index,
        "base_graph6": base_g6, "diametral_pairs": [list(pair) for pair in pairs],
        "planned_constructions": total_planned, **base_record,
        "status": "PASS", "timestamp_utc": "2026-08-13", "public_action": False,
    })
    hist: Counter[int] = Counter()
    residue_hist: Counter[int] = Counter()
    candidates: list[dict[str, object]] = []
    tight = 0
    timeouts = 0
    mismatches = 0
    max_residue = -1
    iso_buckets: dict[tuple[int, tuple[int, ...], str], list[nx.Graph]] = defaultdict(list)
    iso_duplicates = 0
    evaluated = 0
    for u, v in pairs:
        for q in SIZES:
            for r in SIZES:
                started = time.monotonic()
                graph, left, right = attach_beads(base, u, v, q, r)
                verify_decomposition(graph, base, u, v, left, right)
                degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
                trajectory = hh_trajectory(degrees)
                residue = len(trajectory[-1])
                diameter = nx.diameter(graph)
                witness = [*base_record["forest_witness"], left[0], left[1], right[0], right[1]]
                if diameter != 8 or len(witness) != 14 or not is_forest(graph.subgraph(witness)):
                    mismatches += 1
                    append_jsonl(ledger, {
                        "event": "CERTIFICATE_MISMATCH", "base_graph6": base_g6,
                        "attachments": [u, v], "sizes": [q, r], "diameter": diameter,
                        "witness": witness, "timestamp_utc": "2026-08-13",
                        "public_action": False,
                    })
                    continue
                forest = 14
                residual = forest - residue - math.ceil(diameter / 3)
                encoded = nx.to_graph6_bytes(graph, header=False).decode().strip()
                key = iso_key(graph)
                duplicate = any(nx.is_isomorphic(graph, old) for old in iso_buckets[key])
                if duplicate:
                    iso_duplicates += 1
                else:
                    iso_buckets[key].append(graph.copy())
                record: dict[str, object] = {
                    "event": "CLIQUE_BEAD_REALIZATION",
                    "base_index": base_index,
                    "base_graph6": base_g6,
                    "attachments": [u, v],
                    "clique_sizes": [q, r],
                    "n": graph.number_of_nodes(),
                    "m": graph.number_of_edges(),
                    "graph6": encoded,
                    "edges": [list(edge) for edge in sorted(tuple(sorted(e)) for e in graph.edges())],
                    "degree_sequence": degrees,
                    "hh_trajectory": trajectory,
                    "residue": residue,
                    "diameter": diameter,
                    "ceil_diameter_over_3": math.ceil(diameter / 3),
                    "forest": forest,
                    "forest_witness": witness,
                    "forest_upper_certificate": {
                        "base_graph6": base_g6, "base_upper": 10,
                        "left_clique_order": q, "left_upper": 2,
                        "right_clique_order": r, "right_upper": 2,
                        "joining_edges_are_bridges": True, "total_upper": 14,
                    },
                    "residual": residual,
                    "isomorphic_duplicate_within_base": duplicate,
                    "solve_seconds": time.monotonic() - started,
                    "timestamp_utc": "2026-08-13",
                    "public_action": False,
                }
                append_jsonl(records, record)
                evaluated += 1
                hist[residual] += 1
                residue_hist[residue] += 1
                tight += residual == 0
                if residue > max_residue:
                    append_jsonl(ledger, {
                        "event": "IMPROVED_RESIDUE", "base_index": base_index,
                        "previous_max_residue": max_residue, **record,
                    })
                    max_residue = residue
                if residual < 0:
                    candidate = {**record, "event": "CLIQUE_BEAD_CANDIDATE"}
                    append_jsonl(ledger, candidate)
                    candidates.append(candidate)
    summary: dict[str, object] = {
        "event": "BASE_SUMMARY", "base_index": base_index, "base_graph6": base_g6,
        "diametral_pairs": len(pairs), "planned": total_planned,
        "evaluated": evaluated, "isomorphic_duplicates": iso_duplicates,
        "distinct_within_base": evaluated - iso_duplicates,
        "residual_histogram": dict(sorted(hist.items())),
        "residue_histogram": dict(sorted(residue_hist.items())),
        "minimum_residual": min(hist) if hist else None,
        "maximum_residue": max(residue_hist) if residue_hist else None,
        "tight": tight, "candidates": len(candidates), "timeouts": timeouts,
        "certificate_mismatches": mismatches,
        "status": "CANDIDATE_PENDING_REPLAY" if candidates else (
            "PASS" if not mismatches and not timeouts else "INCONCLUSIVE"
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
    if args.phase == "gate":
        result = run_gate(args.ledger)
    else:
        result = evaluate_base(args.base_index, args.ledger, args.records)
    result["seconds"] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
