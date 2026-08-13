#!/usr/bin/env python3
"""Frozen sparse high-feedback bead bridge trial for WOWII 61."""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from prospective_wowii61_realization_spectrum import (
    exact_record,
    hh_trajectory,
    is_forest,
    largest_induced_forest,
)
from prospective_wowii61_realization_surgery import run_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "results/expansion/prospective_wowii61_sparse_feedback_bead_ledger.jsonl"
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_sparse_feedback_bead_records.jsonl"
BASES = ("KniA@A?_A?G?", "K~Q?PA?_A?G?", "K~IA?Q?_A?G?")
EXPECTED_BASE_SEQUENCE = [6, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1]
EXPECTED_TOTAL = 468


@dataclass(frozen=True)
class Bead:
    name: str
    graph: nx.Graph
    root: int
    predicted_order: int
    predicted_rho: int
    predicted_forest: int


def menu() -> tuple[Bead, ...]:
    petersen = nx.petersen_graph()
    petersen_sub = nx.Graph(petersen)
    petersen_sub.remove_edge(0, 1)
    petersen_sub.add_edges_from(((0, 10), (10, 1)))
    return (
        Bead("Prism3", nx.circular_ladder_graph(3), 0, 6, 2, 4),
        Bead("K3,3", nx.complete_bipartite_graph(3, 3), 0, 6, 2, 4),
        Bead("Cube3", nx.cubical_graph(), 0, 8, 3, 6),
        Bead("Petersen", petersen, 0, 10, 2, 7),
        Bead("PetersenSub", petersen_sub, 10, 11, 3, 8),
        Bead("Heawood", nx.heawood_graph(), 0, 14, 3, 10),
    )


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def certify_beads(ledger: Path) -> tuple[dict[str, dict[str, object]], bool]:
    certificates: dict[str, dict[str, object]] = {}
    mismatch = False
    for bead in menu():
        graph = nx.convert_node_labels_to_integers(bead.graph, ordering="sorted")
        # Root labels are unchanged for all fixed constructors under sorted integer relabelling.
        rho = nx.eccentricity(graph, bead.root)
        forest_order, witness = largest_induced_forest(graph)
        record: dict[str, object] = {
            "event": "BEAD_CERTIFICATE", "name": bead.name,
            "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
            "n": graph.number_of_nodes(), "m": graph.number_of_edges(),
            "root": bead.root, "root_eccentricity": rho,
            "forest": forest_order, "forest_witness": list(witness),
            "feedback_loss": graph.number_of_nodes() - forest_order,
            "predicted_order": bead.predicted_order,
            "predicted_rho": bead.predicted_rho,
            "predicted_forest": bead.predicted_forest,
            "timestamp_utc": "2026-08-13", "public_action": False,
        }
        status = (
            graph.number_of_nodes() == bead.predicted_order
            and rho == bead.predicted_rho
            and forest_order == bead.predicted_forest
        )
        record["status"] = "PASS" if status else "MISMATCH"
        mismatch |= not status
        append_jsonl(ledger, record)
        certificates[bead.name] = record
    summary = {
        "event": "BEAD_GATE", "beads": len(certificates),
        "mismatches": int(mismatch), "status": "PASS" if not mismatch else "INCONCLUSIVE",
        "timestamp_utc": "2026-08-13", "public_action": False,
    }
    append_jsonl(ledger, summary)
    return certificates, not mismatch


def diametral_pairs(graph: nx.Graph) -> list[tuple[int, int]]:
    distances = dict(nx.all_pairs_shortest_path_length(graph))
    diameter = max(max(row.values()) for row in distances.values())
    return sorted((u, v) for u in graph for v in graph if u < v and distances[u][v] == diameter)


def attach(
    base: nx.Graph, u: int, v: int, left: Bead, right: Bead,
) -> tuple[nx.Graph, dict[str, object], dict[str, object]]:
    left_graph = nx.convert_node_labels_to_integers(left.graph, ordering="sorted")
    right_graph = nx.convert_node_labels_to_integers(right.graph, ordering="sorted")
    left_map = {node: 12 + node for node in left_graph}
    right_offset = 12 + left_graph.number_of_nodes()
    right_map = {node: right_offset + node for node in right_graph}
    graph = nx.Graph(base)
    graph.add_edges_from((left_map[a], left_map[b]) for a, b in left_graph.edges())
    graph.add_edges_from((right_map[a], right_map[b]) for a, b in right_graph.edges())
    graph.add_edge(u, left_map[left.root])
    graph.add_edge(v, right_map[right.root])
    return graph, {
        "name": left.name, "vertices": sorted(left_map.values()),
        "root": left_map[left.root],
    }, {
        "name": right.name, "vertices": sorted(right_map.values()),
        "root": right_map[right.root],
    }


def verify_blocks(
    graph: nx.Graph, base: nx.Graph, u: int, v: int,
    left: dict[str, object], right: dict[str, object],
) -> None:
    if graph.is_multigraph() or graph.is_directed() or nx.number_of_selfloops(graph):
        raise RuntimeError("simplicity mismatch")
    if not nx.is_connected(graph):
        raise RuntimeError("connectivity mismatch")
    if set(graph.subgraph(range(12)).edges()) != set(base.edges()):
        raise RuntimeError("base block mismatch")
    left_vertices = set(int(value) for value in left["vertices"])
    right_vertices = set(int(value) for value in right["vertices"])
    cross = set()
    for a, b in graph.edges():
        side_a = 0 if a < 12 else (1 if a in left_vertices else 2)
        side_b = 0 if b < 12 else (1 if b in left_vertices else 2)
        if side_a != side_b:
            cross.add(tuple(sorted((a, b))))
    expected = {
        tuple(sorted((u, int(left["root"])))),
        tuple(sorted((v, int(right["root"])))),
    }
    bridges = {tuple(sorted(edge)) for edge in nx.bridges(graph)}
    if cross != expected or not expected.issubset(bridges):
        raise RuntimeError("bridge decomposition mismatch")


def evaluate_base(
    base_index: int, certificates: dict[str, dict[str, object]],
    ledger: Path, records: Path,
) -> dict[str, object]:
    beads = menu()
    base_g6 = BASES[base_index]
    base = nx.from_graph6_bytes(base_g6.encode())
    base_record = exact_record(base)
    for field, expected in {
        "degree_sequence": EXPECTED_BASE_SEQUENCE, "residue": 8,
        "diameter": 4, "forest": 10, "residual": 0,
    }.items():
        if base_record[field] != expected:
            raise RuntimeError(f"base mismatch at {field}")
    pairs = diametral_pairs(base)
    total = sum(len(diametral_pairs(nx.from_graph6_bytes(g6.encode()))) for g6 in BASES) * len(beads) ** 2
    if total != EXPECTED_TOTAL:
        raise RuntimeError("frozen family count mismatch")
    planned = len(pairs) * len(beads) ** 2
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
        for left_bead in beads:
            for right_bead in beads:
                started = time.monotonic()
                graph, left, right = attach(base, u, v, left_bead, right_bead)
                verify_blocks(graph, base, u, v, left, right)
                left_cert = certificates[left_bead.name]
                right_cert = certificates[right_bead.name]
                degrees = sorted((degree for _, degree in graph.degree()), reverse=True)
                trajectory = hh_trajectory(degrees)
                residue = len(trajectory[-1])
                predicted_diameter = 6 + int(left_cert["root_eccentricity"]) + int(right_cert["root_eccentricity"])
                diameter = nx.diameter(graph)
                forest_order = 10 + int(left_cert["forest"]) + int(right_cert["forest"])
                left_vertices = [int(value) for value in left["vertices"]]
                right_vertices = [int(value) for value in right["vertices"]]
                witness = [
                    *base_record["forest_witness"],
                    *(left_vertices[int(index)] for index in left_cert["forest_witness"]),
                    *(right_vertices[int(index)] for index in right_cert["forest_witness"]),
                ]
                if diameter != predicted_diameter or len(witness) != forest_order or not is_forest(graph.subgraph(witness)):
                    mismatches += 1
                    append_jsonl(ledger, {
                        "event": "CERTIFICATE_MISMATCH", "base_index": base_index,
                        "attachments": [u, v], "left": left_bead.name,
                        "right": right_bead.name, "diameter": diameter,
                        "predicted_diameter": predicted_diameter,
                        "timestamp_utc": "2026-08-13", "public_action": False,
                    })
                    continue
                ceiling = math.ceil(diameter / 3)
                residual = forest_order - residue - ceiling
                threshold = forest_order - ceiling + 1
                record: dict[str, object] = {
                    "event": "SPARSE_FEEDBACK_BEAD_REALIZATION",
                    "base_index": base_index, "base_graph6": base_g6,
                    "attachments": [u, v], "left_bead": left,
                    "right_bead": right, "n": graph.number_of_nodes(),
                    "m": graph.number_of_edges(),
                    "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
                    "edges": [list(edge) for edge in sorted(tuple(sorted(e)) for e in graph.edges())],
                    "degree_sequence": degrees, "hh_trajectory": trajectory,
                    "residue": residue, "diameter": diameter,
                    "ceil_diameter_over_3": ceiling, "forest": forest_order,
                    "forest_witness": witness,
                    "forest_upper_certificate": {
                        "base_upper": 10,
                        "left_name": left_bead.name, "left_upper": left_cert["forest"],
                        "right_name": right_bead.name, "right_upper": right_cert["forest"],
                        "joining_edges_are_bridges": True, "total_upper": forest_order,
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
                if best_residual is None or residual < best_residual:
                    append_jsonl(ledger, {"event": "IMPROVED_RESIDUAL", "previous": best_residual, **record})
                    best_residual = residual
                if residual < 0:
                    candidates += 1
                    append_jsonl(ledger, {**record, "event": "SPARSE_BEAD_CANDIDATE"})
    summary: dict[str, object] = {
        "event": "BASE_SUMMARY", "base_index": base_index,
        "base_graph6": base_g6, "diametral_pairs": len(pairs),
        "planned": planned, "evaluated": evaluated,
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


def load_certificates(ledger: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    if ledger.exists():
        with ledger.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if row.get("event") == "BEAD_CERTIFICATE" and row.get("status") == "PASS":
                    result[str(row["name"])] = row
    if set(result) != {bead.name for bead in menu()}:
        raise RuntimeError("complete passing bead gate required before development")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "beads", "base"), required=True)
    parser.add_argument("--base-index", type=int, default=0)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    started = time.monotonic()
    if args.phase == "gate":
        result = run_gate(args.ledger)
    elif args.phase == "beads":
        certificates, passed = certify_beads(args.ledger)
        result = {"event": "BEAD_GATE_SUMMARY", "beads": len(certificates), "status": "PASS" if passed else "INCONCLUSIVE"}
    else:
        result = evaluate_base(args.base_index, load_certificates(args.ledger), args.ledger, args.records)
    result["seconds"] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

