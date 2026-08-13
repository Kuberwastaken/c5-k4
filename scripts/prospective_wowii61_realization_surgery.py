#!/usr/bin/env python3
"""Frozen degree-preserving 2-switch surgery trial for WOWII 61 cliffs."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator

import networkx as nx

from prospective_wowii61_realization_spectrum import (
    SolveTimeout,
    exact_record,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "results/expansion/prospective_wowii61_realization_spectrum_records.jsonl"
DEFAULT_LEDGER = ROOT / "results/expansion/prospective_wowii61_realization_surgery_ledger.jsonl"
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_realization_surgery_records.jsonl"
GLOBAL_EVALUATION_CAP = 25_000


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def graph6(graph: nx.Graph) -> str:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(graph, header=False).decode().strip()


def wl_key(graph: nx.Graph) -> tuple[tuple[int, ...], str]:
    return (
        tuple(sorted((degree for _, degree in graph.degree()), reverse=True)),
        nx.weisfeiler_lehman_graph_hash(graph, iterations=max(3, graph.number_of_nodes())),
    )


class IsoStore:
    def __init__(self) -> None:
        self.buckets: dict[tuple[tuple[int, ...], str], list[nx.Graph]] = defaultdict(list)

    def contains(self, graph: nx.Graph) -> bool:
        return any(nx.is_isomorphic(graph, old) for old in self.buckets[wl_key(graph)])

    def add(self, graph: nx.Graph) -> bool:
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        key = wl_key(graph)
        if any(nx.is_isomorphic(graph, old) for old in self.buckets[key]):
            return False
        self.buckets[key].append(graph.copy())
        return True


def c5_clique_blowup(size: int) -> nx.Graph:
    graph = nx.Graph()
    for block in range(5):
        vertices = [block * size + offset for offset in range(size)]
        graph.add_edges_from(itertools.combinations(vertices, 2))
        next_vertices = [((block + 1) % 5) * size + offset for offset in range(size)]
        graph.add_edges_from(itertools.product(vertices, next_vertices))
    return graph


def named_controls() -> Iterator[tuple[str, nx.Graph]]:
    for n in range(5, 11):
        yield f"C{n}", nx.cycle_graph(n)
    for n in range(2, 11):
        yield f"P{n}", nx.path_graph(n)
    yield "Petersen", nx.petersen_graph()
    yield "K3,3", nx.complete_bipartite_graph(3, 3)
    for n in range(2, 11):
        yield f"K{n}", nx.complete_graph(n)
    for n in range(2, 13):
        yield f"K1,{n - 1}", nx.star_graph(n - 1)
    for left in range(2, 7):
        for right in range(left, 13 - left):
            yield f"K{left},{right}", nx.complete_bipartite_graph(left, right)
    yield "C5[K2]", c5_clique_blowup(2)


def distinct_controls() -> list[tuple[str, nx.Graph]]:
    controls: list[tuple[str, nx.Graph]] = []
    store = IsoStore()
    for index, candidate in enumerate(nx.graph_atlas_g()):
        if 2 <= candidate.number_of_nodes() <= 7 and nx.is_connected(candidate) and store.add(candidate):
            controls.append((f"atlas:{index}", nx.convert_node_labels_to_integers(candidate)))
    for name, candidate in named_controls():
        if store.add(candidate):
            controls.append((name, nx.convert_node_labels_to_integers(candidate)))
    return controls


def run_gate(ledger: Path) -> dict[str, object]:
    residuals: Counter[int] = Counter()
    timeouts = 0
    violations: list[dict[str, object]] = []
    maximum_diameter = 0
    controls = distinct_controls()
    for name, candidate in controls:
        try:
            record = exact_record(candidate)
        except SolveTimeout:
            timeouts += 1
            append_jsonl(ledger, {
                "event": "DATABASE_GATE_TIMEOUT", "name": name,
                "timestamp_utc": "2026-08-13", "public_action": False,
            })
            continue
        residuals[int(record["residual"])] += 1
        maximum_diameter = max(maximum_diameter, int(record["diameter"]))
        if int(record["residual"]) < 0:
            violations.append({"name": name, **record})
    result: dict[str, object] = {
        "event": "DATABASE_GATE",
        "controls": len(controls),
        "minimum_residual": min(residuals) if residuals else None,
        "maximum_diameter": maximum_diameter,
        "residual_histogram": dict(sorted(residuals.items())),
        "violations": violations,
        "timeouts": timeouts,
        "status": "PASS" if not violations and not timeouts else "PAUSE",
        "timestamp_utc": "2026-08-13",
        "public_action": False,
    }
    append_jsonl(ledger, result)
    return result


def load_cliff_strata(source: Path) -> list[tuple[tuple[int, ...], list[dict[str, object]]]]:
    groups: dict[tuple[int, ...], list[dict[str, object]]] = defaultdict(list)
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("phase") != "exhaustive8":
                continue
            sequence = tuple(int(value) for value in row["degree_sequence"])
            groups[sequence].append(row)
    cliffs = []
    for sequence, rows in groups.items():
        residuals = [int(row["residual"]) for row in rows]
        if min(residuals) == 0 and max(residuals) - min(residuals) >= 2:
            cliffs.append((sequence, rows))
    cliffs.sort(key=lambda item: item[0])
    if len(cliffs) != 36:
        raise RuntimeError(f"frozen cliff count mismatch: expected 36, got {len(cliffs)}")
    return cliffs


def legal_switches(graph: nx.Graph, raw_cap: int = 256) -> Iterator[tuple[nx.Graph, dict[str, object]]]:
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
                if emitted >= raw_cap:
                    return


def prior_evaluations(ledger: Path) -> int:
    total = 0
    if not ledger.exists():
        return total
    with ledger.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("event") == "SURGERY_STRATUM_SUMMARY":
                total += int(row.get("children_evaluated", 0))
    return total


def run_seed(
    seed_row: dict[str, object],
    records: Path,
    remaining_budget: int,
    max_depth: int = 4,
    beam_width: int = 64,
) -> dict[str, object]:
    seed_graph = nx.from_graph6_bytes(str(seed_row["graph6"]).encode())
    seed_exact = exact_record(seed_graph)
    for field in ("degree_sequence", "residue", "diameter", "forest", "residual"):
        if seed_exact[field] != seed_row[field]:
            raise RuntimeError(f"seed recomputation mismatch for {seed_row['graph6']}: {field}")
    seed_sequence = tuple(int(value) for value in seed_exact["degree_sequence"])
    seed_forest = int(seed_exact["forest"])
    seed_diameter = int(seed_exact["diameter"])
    seed_residual = int(seed_exact["residual"])
    retained = IsoStore()
    retained.add(seed_graph)
    frontier: list[tuple[nx.Graph, list[dict[str, object]]]] = [(seed_graph, [])]
    children_evaluated = 0
    retained_count = 0
    timeouts = 0
    raw_switches = 0
    directional_drops = 0
    diameter_lifts = 0
    negatives: list[dict[str, object]] = []
    residual_hist: Counter[int] = Counter()
    depth_hist: Counter[int] = Counter()
    for depth in range(1, max_depth + 1):
        candidates: list[tuple[dict[str, object], nx.Graph, list[dict[str, object]]]] = []
        depth_seen = IsoStore()
        for parent, parent_path in frontier:
            for child, move in legal_switches(parent):
                raw_switches += 1
                child_sequence = tuple(sorted((degree for _, degree in child.degree()), reverse=True))
                if child_sequence != seed_sequence:
                    raise RuntimeError("2-switch changed the degree sequence")
                if retained.contains(child) or not depth_seen.add(child):
                    continue
                if children_evaluated >= remaining_budget:
                    break
                try:
                    record = exact_record(child)
                except SolveTimeout:
                    timeouts += 1
                    continue
                children_evaluated += 1
                residual_hist[int(record["residual"])] += 1
                if int(record["residual"]) < 0:
                    negatives.append(record)
                eligible = int(record["forest"]) <= seed_forest and (
                    int(record["diameter"]) > seed_diameter
                    or int(record["residual"]) < seed_residual
                )
                if eligible:
                    path = [*parent_path, move]
                    candidates.append((record, child, path))
            if children_evaluated >= remaining_budget:
                break
        candidates.sort(key=lambda item: (
            int(item[0]["residual"]), -int(item[0]["diameter"]),
            int(item[0]["forest"]), str(item[0]["graph6"]),
        ))
        frontier = []
        for record, child, path in candidates:
            if len(frontier) >= beam_width:
                break
            if not retained.add(child):
                continue
            retained_count += 1
            depth_hist[depth] += 1
            if int(record["residual"]) < seed_residual:
                directional_drops += 1
            elif int(record["diameter"]) > seed_diameter:
                diameter_lifts += 1
            endpoint = {
                "event": "SURGERY_ENDPOINT",
                "seed_graph6": seed_row["graph6"],
                "depth": depth,
                "path": path,
                **record,
                "timestamp_utc": "2026-08-13",
                "public_action": False,
            }
            append_jsonl(records, endpoint)
            frontier.append((child, path))
        if not frontier or children_evaluated >= remaining_budget:
            break
    return {
        "seed_graph6": seed_row["graph6"],
        "seed_forest": seed_forest,
        "seed_diameter": seed_diameter,
        "children_evaluated": children_evaluated,
        "raw_switches": raw_switches,
        "retained": retained_count,
        "depth_histogram": dict(sorted(depth_hist.items())),
        "residual_histogram": dict(sorted(residual_hist.items())),
        "directional_drops": directional_drops,
        "diameter_lifts": diameter_lifts,
        "negative": negatives,
        "timeouts": timeouts,
        "no_eligible_move": retained_count == 0,
    }


def run_strata(
    source: Path,
    ledger: Path,
    records: Path,
    start: int,
    count: int,
) -> dict[str, object]:
    cliffs = load_cliff_strata(source)
    chosen = cliffs[start:start + count]
    used = prior_evaluations(ledger)
    summaries: list[dict[str, object]] = []
    for stratum_index, (sequence, rows) in enumerate(chosen, start=start):
        if used >= GLOBAL_EVALUATION_CAP:
            break
        seeds = sorted(
            (row for row in rows if int(row["residual"]) == 0),
            key=lambda row: str(row["graph6"]),
        )
        seed_summaries = []
        for seed in seeds:
            if used >= GLOBAL_EVALUATION_CAP:
                break
            summary = run_seed(seed, records, GLOBAL_EVALUATION_CAP - used)
            used += int(summary["children_evaluated"])
            seed_summaries.append(summary)
        stratum_summary: dict[str, object] = {
            "event": "SURGERY_STRATUM_SUMMARY",
            "stratum_index": stratum_index,
            "degree_sequence": list(sequence),
            "realizations_in_exact_stratum": len(rows),
            "tight_seeds": len(seeds),
            "completed_seeds": len(seed_summaries),
            "children_evaluated": sum(int(row["children_evaluated"]) for row in seed_summaries),
            "raw_switches": sum(int(row["raw_switches"]) for row in seed_summaries),
            "retained": sum(int(row["retained"]) for row in seed_summaries),
            "directional_drops": sum(int(row["directional_drops"]) for row in seed_summaries),
            "diameter_lifts": sum(int(row["diameter_lifts"]) for row in seed_summaries),
            "no_eligible_seeds": sum(bool(row["no_eligible_move"]) for row in seed_summaries),
            "negative": [item for row in seed_summaries for item in row["negative"]],
            "timeouts": sum(int(row["timeouts"]) for row in seed_summaries),
            "seed_summaries": seed_summaries,
            "timestamp_utc": "2026-08-13",
            "public_action": False,
        }
        append_jsonl(ledger, stratum_summary)
        summaries.append(stratum_summary)
    return {
        "event": "SURGERY_BATCH_SUMMARY",
        "start": start,
        "requested_strata": count,
        "completed_strata": len(summaries),
        "children_evaluated": sum(int(row["children_evaluated"]) for row in summaries),
        "retained": sum(int(row["retained"]) for row in summaries),
        "directional_drops": sum(int(row["directional_drops"]) for row in summaries),
        "diameter_lifts": sum(int(row["diameter_lifts"]) for row in summaries),
        "negative": [item for row in summaries for item in row["negative"]],
        "timeouts": sum(int(row["timeouts"]) for row in summaries),
        "global_evaluations_after": used,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "strata"), required=True)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=4)
    args = parser.parse_args()
    started = time.monotonic()
    if args.phase == "gate":
        result = run_gate(args.ledger)
    else:
        result = run_strata(args.source, args.ledger, args.records, args.start, args.count)
    result["seconds"] = time.monotonic() - started
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

