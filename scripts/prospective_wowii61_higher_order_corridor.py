#!/usr/bin/env python3
"""Frozen neutral-corridor switch trial for the order-12 WOWII 61 cliff."""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterator

import networkx as nx

from prospective_wowii61_realization_spectrum import SolveTimeout, exact_record
from prospective_wowii61_realization_surgery import run_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "results/expansion/prospective_wowii61_higher_order_corridor_ledger.jsonl"
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_higher_order_corridor_records.jsonl"
SEED_GRAPH6 = "K^qA@A?_A?G?"
SEED_SEQUENCE = (6, 6, 4, 3, 2, 1, 1, 1, 1, 1, 1, 1)
SEED_FOREST = 10
SEED_DIAMETER = 4
MAX_DEPTH = 8
BEAM_WIDTH = 32
RAW_SWITCH_CAP = 128
EVALUATION_CAP = 8_000


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def iso_key(graph: nx.Graph) -> tuple[tuple[int, ...], str]:
    return (
        tuple(sorted((degree for _, degree in graph.degree()), reverse=True)),
        nx.weisfeiler_lehman_graph_hash(graph, iterations=max(3, graph.number_of_nodes())),
    )


class IsoStore:
    def __init__(self) -> None:
        self.buckets: dict[tuple[tuple[int, ...], str], list[nx.Graph]] = defaultdict(list)

    def contains(self, graph: nx.Graph) -> bool:
        return any(nx.is_isomorphic(graph, old) for old in self.buckets[iso_key(graph)])

    def add(self, graph: nx.Graph) -> bool:
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        key = iso_key(graph)
        if any(nx.is_isomorphic(graph, old) for old in self.buckets[key]):
            return False
        self.buckets[key].append(graph.copy())
        return True


def legal_switches(graph: nx.Graph) -> Iterator[tuple[nx.Graph, dict[str, object]]]:
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    emitted = 0
    for index, (a, b) in enumerate(edges):
        for c, d in edges[index + 1:]:
            if len({a, b, c, d}) != 4:
                continue
            for first, second in (((a, c), (b, d)), ((a, d), (b, c))):
                added = (tuple(sorted(first)), tuple(sorted(second)))
                if graph.has_edge(*added[0]) or graph.has_edge(*added[1]):
                    continue
                child = graph.copy()
                removed = ((a, b), (c, d))
                child.remove_edges_from(removed)
                child.add_edges_from(added)
                if not nx.is_connected(child):
                    continue
                yield child, {
                    "removed": [list(edge) for edge in removed],
                    "added": [list(edge) for edge in added],
                }
                emitted += 1
                if emitted >= RAW_SWITCH_CAP:
                    return


def assert_seed() -> tuple[nx.Graph, dict[str, object]]:
    seed = nx.from_graph6_bytes(SEED_GRAPH6.encode())
    record = exact_record(seed)
    expected: dict[str, object] = {
        "degree_sequence": list(SEED_SEQUENCE),
        "residue": 8,
        "diameter": SEED_DIAMETER,
        "ceil_diameter_over_3": 2,
        "forest": SEED_FOREST,
        "residual": 0,
    }
    for field, value in expected.items():
        if record[field] != value:
            raise RuntimeError(f"seed mismatch for {field}: {record[field]} != {value}")
    return seed, record


def search(ledger: Path, records: Path) -> dict[str, object]:
    seed, seed_record = assert_seed()
    append_jsonl(ledger, {
        "event": "SEED_RECOMPUTATION",
        **seed_record,
        "status": "PASS",
        "timestamp_utc": "2026-08-13",
        "public_action": False,
    })
    retained_seen = IsoStore()
    retained_seen.add(seed)
    frontier: list[tuple[nx.Graph, list[dict[str, object]]]] = [(seed, [])]
    total_evaluated = 0
    total_raw = 0
    total_eligible = 0
    total_timeouts = 0
    best_residual = 0
    best_diameter = SEED_DIAMETER
    candidates: list[dict[str, object]] = []
    completed_depth = 0
    deepest_corridor = 0
    for depth in range(1, MAX_DEPTH + 1):
        depth_started = time.monotonic()
        depth_raw = 0
        depth_evaluated = 0
        depth_duplicates = 0
        depth_timeouts = 0
        residual_hist: Counter[int] = Counter()
        diameter_hist: Counter[int] = Counter()
        eligible: list[tuple[dict[str, object], nx.Graph, list[dict[str, object]]]] = []
        depth_seen = IsoStore()
        for parent, parent_path in frontier:
            for child, move in legal_switches(parent):
                depth_raw += 1
                total_raw += 1
                child_sequence = tuple(sorted((degree for _, degree in child.degree()), reverse=True))
                if child_sequence != SEED_SEQUENCE:
                    raise RuntimeError("2-switch changed the frozen degree sequence")
                if retained_seen.contains(child) or not depth_seen.add(child):
                    depth_duplicates += 1
                    continue
                if total_evaluated >= EVALUATION_CAP:
                    break
                try:
                    record = exact_record(child)
                except SolveTimeout:
                    depth_timeouts += 1
                    total_timeouts += 1
                    append_jsonl(ledger, {
                        "event": "TIMEOUT", "depth": depth,
                        "graph6": nx.to_graph6_bytes(child, header=False).decode().strip(),
                        "timestamp_utc": "2026-08-13", "public_action": False,
                    })
                    continue
                depth_evaluated += 1
                total_evaluated += 1
                residual = int(record["residual"])
                diameter = int(record["diameter"])
                forest = int(record["forest"])
                residual_hist[residual] += 1
                diameter_hist[diameter] += 1
                path = [*parent_path, move]
                corridor_eligible = forest <= SEED_FOREST and diameter >= SEED_DIAMETER
                if residual < 0 or corridor_eligible:
                    eligible.append((record, child, path))
                if residual < best_residual or diameter > best_diameter:
                    append_jsonl(ledger, {
                        "event": "IMPROVED_ENDPOINT",
                        "depth": depth,
                        "path": path,
                        **record,
                        "previous_best_residual": best_residual,
                        "previous_best_diameter": best_diameter,
                        "timestamp_utc": "2026-08-13",
                        "public_action": False,
                    })
                    best_residual = min(best_residual, residual)
                    best_diameter = max(best_diameter, diameter)
                if residual < 0:
                    candidate = {
                        "event": "CORRIDOR_CANDIDATE",
                        "depth": depth,
                        "path": path,
                        **record,
                        "timestamp_utc": "2026-08-13",
                        "public_action": False,
                    }
                    append_jsonl(records, candidate)
                    append_jsonl(ledger, candidate)
                    candidates.append(candidate)
            if total_evaluated >= EVALUATION_CAP:
                break
        eligible.sort(key=lambda item: (
            int(item[0]["residual"]) >= 0,
            int(item[0]["residual"]),
            -int(item[0]["ceil_diameter_over_3"]),
            -int(item[0]["diameter"]),
            int(item[0]["forest"]),
            str(item[0]["graph6"]),
        ))
        next_frontier: list[tuple[nx.Graph, list[dict[str, object]]]] = []
        for record, child, path in eligible:
            if len(next_frontier) >= BEAM_WIDTH:
                break
            if not retained_seen.add(child):
                continue
            endpoint = {
                "event": "CORRIDOR_ENDPOINT",
                "depth": depth,
                "path": path,
                **record,
                "timestamp_utc": "2026-08-13",
                "public_action": False,
            }
            append_jsonl(records, endpoint)
            next_frontier.append((child, path))
            deepest_corridor = max(deepest_corridor, depth)
        total_eligible += len(next_frontier)
        completed_depth = depth
        append_jsonl(ledger, {
            "event": "DEPTH_SUMMARY",
            "depth": depth,
            "parents": len(frontier),
            "raw_connected_switches": depth_raw,
            "unique_children_evaluated": depth_evaluated,
            "duplicates_or_revisits": depth_duplicates,
            "eligible_before_beam": len(eligible),
            "retained_after_beam": len(next_frontier),
            "residual_histogram": dict(sorted(residual_hist.items())),
            "diameter_histogram": dict(sorted(diameter_hist.items())),
            "timeouts": depth_timeouts,
            "seconds": time.monotonic() - depth_started,
            "timestamp_utc": "2026-08-13",
            "public_action": False,
        })
        frontier = next_frontier
        if candidates or not frontier or total_evaluated >= EVALUATION_CAP:
            break
    if candidates:
        verdict = "CORRIDOR_CROSSING_UNVERIFIED"
    elif total_timeouts:
        verdict = "INCONCLUSIVE"
    elif deepest_corridor >= 2:
        verdict = "NEUTRAL_CORRIDOR"
    elif best_diameter >= 5:
        verdict = "CEILING_APPROACH"
    else:
        verdict = "HOLD_BOUNDED"
    summary: dict[str, object] = {
        "event": "SEARCH_SUMMARY",
        "completed_depth": completed_depth,
        "raw_connected_switches": total_raw,
        "unique_children_evaluated": total_evaluated,
        "retained_endpoints": total_eligible,
        "deepest_corridor": deepest_corridor,
        "best_residual": best_residual,
        "best_diameter": best_diameter,
        "candidates": candidates,
        "timeouts": total_timeouts,
        "verdict": verdict,
        "timestamp_utc": "2026-08-13",
        "public_action": False,
    }
    append_jsonl(ledger, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "search"), required=True)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    args = parser.parse_args()
    started = time.monotonic()
    if args.phase == "gate":
        result = run_gate(args.ledger)
    else:
        result = search(args.ledger, args.records)
    result["seconds"] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
