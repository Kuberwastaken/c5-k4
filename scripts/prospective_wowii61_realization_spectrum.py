#!/usr/bin/env python3
"""Frozen realization-spectrum trial for current WOWII 61.

The script has two independent phases. ``exhaustive8`` consumes nauty's
connected unlabelled order-eight class. ``sample`` enumerates graphical
degree-sequence strata in the frozen priority order and samples multiple
connected nonisomorphic realizations. Machine rows are flushed incrementally.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import signal
import subprocess
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Iterator

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "results/expansion/prospective_wowii61_realization_spectrum_records.jsonl"
SEED = 61006120260813


class SolveTimeout(RuntimeError):
    pass


def _alarm_handler(_signum: int, _frame: object) -> None:
    raise SolveTimeout("60-second exact-solve cap reached")


def append_jsonl(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()


def hh_trajectory(degrees: Iterable[int]) -> list[list[int]]:
    sequence = sorted((int(d) for d in degrees), reverse=True)
    states = [sequence.copy()]
    while sequence and sequence[0] > 0:
        d = sequence.pop(0)
        if d > len(sequence):
            raise ValueError("nongraphical sequence during Havel--Hakimi")
        for i in range(d):
            sequence[i] -= 1
            if sequence[i] < 0:
                raise ValueError("negative Havel--Hakimi term")
        sequence.sort(reverse=True)
        states.append(sequence.copy())
    return states


def residue_from_degrees(degrees: Iterable[int]) -> int:
    return len(hh_trajectory(degrees)[-1])


def is_forest(graph: nx.Graph) -> bool:
    return graph.number_of_edges() == graph.number_of_nodes() - nx.number_connected_components(graph)


def largest_induced_forest(graph: nx.Graph, cap_seconds: int = 60) -> tuple[int, tuple[int, ...]]:
    nodes = tuple(sorted(graph.nodes()))
    old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(cap_seconds)
    try:
        for size in range(len(nodes), 0, -1):
            for subset in itertools.combinations(nodes, size):
                if is_forest(graph.subgraph(subset)):
                    return size, subset
        return 0, ()
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def exact_record(graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    if graph.number_of_nodes() < 2 or not nx.is_connected(graph):
        raise ValueError("WOWII 61 requires a nontrivial connected graph")
    degrees = sorted((d for _, d in graph.degree()), reverse=True)
    trajectory = hh_trajectory(degrees)
    started = time.monotonic()
    forest, witness = largest_induced_forest(graph)
    elapsed = time.monotonic() - started
    diameter = nx.diameter(graph)
    residual = forest - len(trajectory[-1]) - math.ceil(diameter / 3)
    return {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "degree_sequence": degrees,
        "hh_trajectory": trajectory,
        "residue": len(trajectory[-1]),
        "diameter": diameter,
        "ceil_diameter_over_3": math.ceil(diameter / 3),
        "forest": forest,
        "forest_witness": list(witness),
        "residual": residual,
        "solve_seconds": elapsed,
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "edges": [list(edge) for edge in sorted(tuple(sorted(e)) for e in graph.edges())],
    }


def wl_key(graph: nx.Graph) -> tuple[tuple[int, ...], str]:
    return (
        tuple(sorted((d for _, d in graph.degree()), reverse=True)),
        nx.weisfeiler_lehman_graph_hash(graph, iterations=max(3, graph.number_of_nodes())),
    )


def add_nonisomorphic(store: dict[tuple[tuple[int, ...], str], list[nx.Graph]], graph: nx.Graph) -> bool:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    key = wl_key(graph)
    if any(nx.is_isomorphic(graph, old) for old in store[key]):
        return False
    store[key].append(graph.copy())
    return True


def exhaustive_order_eight(geng: Path, records: Path) -> dict[str, object]:
    process = subprocess.run(
        [str(geng), "-cq", "8"], check=True, text=True, stdout=subprocess.PIPE,
        timeout=60,
    )
    lines = [line for line in process.stdout.splitlines() if line and not line.startswith(">")]
    spectra: dict[tuple[int, ...], list[dict[str, object]]] = defaultdict(list)
    residual_hist: Counter[int] = Counter()
    timeouts = 0
    best: list[dict[str, object]] = []
    for index, line in enumerate(lines, 1):
        graph = nx.from_graph6_bytes(line.encode())
        try:
            record = exact_record(graph)
        except SolveTimeout:
            timeouts += 1
            append_jsonl(records, {"event": "TIMEOUT", "phase": "exhaustive8", "graph6": line})
            continue
        record.update({"event": "REALIZATION", "phase": "exhaustive8", "index": index})
        append_jsonl(records, record)
        sequence = tuple(int(x) for x in record["degree_sequence"])
        spectra[sequence].append(record)
        residual_hist[int(record["residual"])] += 1
        best.append(record)
        best.sort(key=lambda row: (int(row["residual"]), -int(row["diameter"]), int(row["forest"]), str(row["graph6"])))
        del best[10:]
    cliffs = []
    for sequence, rows in spectra.items():
        values = [int(row["residual"]) for row in rows]
        if min(values) == 0 and max(values) - min(values) >= 2:
            cliffs.append({
                "degree_sequence": list(sequence),
                "realizations": len(rows),
                "minimum_residual": min(values),
                "maximum_residual": max(values),
                "minimum_examples": [row["graph6"] for row in rows if int(row["residual"]) == min(values)][:3],
                "maximum_examples": [row["graph6"] for row in rows if int(row["residual"]) == max(values)][:3],
            })
    return {
        "event": "EXHAUSTIVE_ORDER_8_SUMMARY",
        "graphs": len(lines),
        "evaluated": sum(residual_hist.values()),
        "degree_sequences": len(spectra),
        "timeouts": timeouts,
        "minimum_residual": min(residual_hist) if residual_hist else None,
        "residual_histogram": dict(sorted(residual_hist.items())),
        "realization_cliffs": cliffs,
        "best": best,
    }


def positive_partitions(n: int) -> Iterator[tuple[int, ...]]:
    def rec(remaining: int, last: int, prefix: list[int]) -> Iterator[tuple[int, ...]]:
        if remaining == 0:
            sequence = tuple(prefix)
            if sum(sequence) % 2 == 0 and sum(sequence) >= 2 * (n - 1) and nx.is_graphical(sequence, method="eg"):
                yield sequence
            return
        for degree in range(min(last, n - 1), 0, -1):
            yield from rec(remaining - 1, degree, prefix + [degree])
    yield from rec(n, n - 1, [])


def connect_realization(graph: nx.Graph) -> nx.Graph | None:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    if nx.is_connected(graph):
        return graph
    for _ in range(512):
        components = [set(c) for c in nx.connected_components(graph)]
        if len(components) == 1:
            return graph
        first = components[0]
        rest = set().union(*components[1:])
        edges_first = [e for e in graph.edges() if e[0] in first and e[1] in first]
        edges_rest = [e for e in graph.edges() if e[0] in rest and e[1] in rest]
        improved = False
        for a, b in edges_first:
            for c, d in edges_rest:
                for added in (((a, c), (b, d)), ((a, d), (b, c))):
                    candidate = graph.copy()
                    candidate.remove_edges_from(((a, b), (c, d)))
                    candidate.add_edges_from(added)
                    if nx.number_connected_components(candidate) < len(components):
                        graph = candidate
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
        if not improved:
            return None
    return graph if nx.is_connected(graph) else None


def sampled_realizations(sequence: tuple[int, ...], rng: random.Random, limit: int, attempts: int) -> list[nx.Graph]:
    seed = connect_realization(nx.havel_hakimi_graph(sequence))
    if seed is None:
        return []
    store: dict[tuple[tuple[int, ...], str], list[nx.Graph]] = defaultdict(list)
    result: list[nx.Graph] = []
    if add_nonisomorphic(store, seed):
        result.append(seed)
    current = seed.copy()
    for _ in range(attempts):
        candidate = current.copy()
        switches = 1 + rng.randrange(max(1, min(8, candidate.number_of_edges() // 2)))
        try:
            nx.double_edge_swap(candidate, nswap=switches, max_tries=max(100, 30 * switches), seed=rng)
        except (nx.NetworkXAlgorithmError, nx.NetworkXError):
            continue
        if not nx.is_connected(candidate):
            continue
        current = candidate
        if add_nonisomorphic(store, candidate):
            result.append(candidate)
            if len(result) >= limit:
                break
    return result


def sequence_manifest(min_order: int, max_order: int, max_sequences: int) -> list[tuple[int, ...]]:
    sequences = []
    for n in range(min_order, max_order + 1):
        sequences.extend(positive_partitions(n))
    sequences.sort(key=lambda s: (-residue_from_degrees(s), sum(s), s))
    return sequences[:max_sequences]


def sample_sequences(
    records: Path, start: int, count: int, max_sequences: int,
    realization_limit: int, attempts: int,
) -> dict[str, object]:
    manifest = sequence_manifest(8, 12, max_sequences)
    chosen = manifest[start:start + count]
    rng = random.Random(SEED + start)
    residual_hist: Counter[int] = Counter()
    realization_counts: Counter[int] = Counter()
    timeouts = 0
    evaluated = 0
    negative = []
    cliffs = []
    best = []
    for offset, sequence in enumerate(chosen):
        sequence_index = start + offset
        graphs = sampled_realizations(sequence, rng, realization_limit, attempts)
        rows = []
        for realization_index, graph in enumerate(graphs):
            try:
                record = exact_record(graph)
            except SolveTimeout:
                timeouts += 1
                append_jsonl(records, {
                    "event": "TIMEOUT", "phase": "sample", "sequence_index": sequence_index,
                    "degree_sequence": list(sequence),
                })
                continue
            record.update({
                "event": "REALIZATION", "phase": "sample", "sequence_index": sequence_index,
                "realization_index": realization_index,
            })
            append_jsonl(records, record)
            rows.append(record)
            evaluated += 1
            residual_hist[int(record["residual"])] += 1
            if int(record["residual"]) < 0:
                negative.append(record)
            best.append(record)
            best.sort(key=lambda row: (int(row["residual"]), -int(row["diameter"]), int(row["forest"]), str(row["graph6"])))
            del best[10:]
        realization_counts[len(rows)] += 1
        if rows:
            values = [int(row["residual"]) for row in rows]
            if min(values) == 0 and max(values) - min(values) >= 2:
                cliffs.append({
                    "degree_sequence": list(sequence), "sequence_index": sequence_index,
                    "realizations": len(rows), "minimum_residual": min(values),
                    "maximum_residual": max(values),
                    "minimum_examples": [row["graph6"] for row in rows if int(row["residual"]) == min(values)][:3],
                    "maximum_examples": [row["graph6"] for row in rows if int(row["residual"]) == max(values)][:3],
                })
    return {
        "event": "SEQUENCE_BATCH_SUMMARY",
        "start": start,
        "requested_sequences": count,
        "completed_sequences": len(chosen),
        "manifest_sequences": len(manifest),
        "evaluated_realizations": evaluated,
        "timeouts": timeouts,
        "minimum_residual": min(residual_hist) if residual_hist else None,
        "residual_histogram": dict(sorted(residual_hist.items())),
        "realizations_per_sequence_histogram": dict(sorted(realization_counts.items())),
        "negative": negative,
        "realization_cliffs": cliffs,
        "best": best,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, default=DEFAULT_RECORDS)
    parser.add_argument("--phase", choices=("exhaustive8", "sample"), required=True)
    parser.add_argument("--geng", type=Path)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--max-sequences", type=int, default=20000)
    parser.add_argument("--realization-limit", type=int, default=2)
    parser.add_argument("--attempts", type=int, default=256)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="omit the verbose best-realization payload from stdout",
    )
    args = parser.parse_args()
    started = time.monotonic()
    if args.phase == "exhaustive8":
        if args.geng is None or not args.geng.is_file():
            raise SystemExit("--geng must name an existing nauty executable")
        result = exhaustive_order_eight(args.geng, args.records)
    else:
        result = sample_sequences(
            args.records, args.start, args.count, args.max_sequences,
            args.realization_limit, args.attempts,
        )
    result["seconds"] = time.monotonic() - started
    if args.summary_only:
        result.pop("best", None)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
