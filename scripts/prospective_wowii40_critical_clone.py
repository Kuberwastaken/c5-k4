#!/usr/bin/env python3
"""Frozen critical false-twin rays from canonical WOWII #40 R=1 rows."""

import importlib.util
import itertools
import json
import math
import os
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
SOURCE_LEDGER = ROOT / "results/expansion/prospective_wowii40_block_surgery_ledger.jsonl"
LEDGER = ROOT / "results/expansion/prospective_wowii40_critical_clone_ledger.jsonl"
CAP = min(50, int(os.environ.get("WOWII40_CLONE_SOLVE_CAP", "8")))


class SolveTimeout(Exception):
    pass


def alarm_handler(_signum, _frame):
    raise SolveTimeout


def source_module():
    path = Path(__file__).with_name("prospective_wowii40_block_surgery.py")
    spec = importlib.util.spec_from_file_location("wowii40_source", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def append(record):
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def canonical_r1_seeds():
    rows = [json.loads(line) for line in SOURCE_LEDGER.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    names, seen = [], set()
    for row in rows:
        if row.get("event") in {"graph_evaluated", "graph_timeout"}:
            name = row.get("name")
            if name not in seen:
                seen.add(name)
                names.append(name)
    official = set(names[:1200])
    exact = {row["name"]: row for row in rows
             if row.get("event") == "graph_evaluated" and row.get("name") in official}
    seeds = []
    for name, row in exact.items():
        residual = ((row["n"] - row["path_cover"]) + (row["n"] - row["bipartite"])
                    - 2 * (row["n"] - row["forest"]))
        if row["slack"] == 0 and residual == 1:
            seeds.append((name, row, nx.from_graph6_bytes(row["graph6"].encode())))
    assert len(seeds) == 13
    return sorted(seeds)


def maximum_forest_masks(module, graph, size):
    graph = nx.convert_node_labels_to_integers(graph)
    adjacency = [0] * len(graph)
    for u, v in graph.edges():
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    result = []
    for vertices in itertools.combinations(range(len(graph)), size):
        mask = sum(1 << v for v in vertices)
        if module.is_forest_mask(adjacency, mask):
            result.append(mask)
    return adjacency, result


def orbit_representatives(graph):
    remaining = set(graph.nodes())
    representatives = []
    matcher = nx.algorithms.isomorphism.GraphMatcher(graph, graph)
    automorphisms = list(matcher.isomorphisms_iter())
    while remaining:
        v = min(remaining)
        orbit = {mapping[v] for mapping in automorphisms}
        representatives.append(v)
        remaining -= orbit
    return representatives


def critical_vertices(module, graph, forest_size):
    graph = nx.convert_node_labels_to_integers(graph)
    adjacency, masks = maximum_forest_masks(module, graph, forest_size)
    result = []
    for v in orbit_representatives(graph):
        containing = [mask for mask in masks if mask >> v & 1]
        if containing and all(bin(adjacency[v] & mask).count("1") >= 2
                              for mask in containing):
            result.append(v)
    return result, len(masks)


def false_twin_lift(graph, vertex, class_size):
    graph = nx.convert_node_labels_to_integers(graph)
    result = nx.Graph(graph)
    neighbors = list(graph.neighbors(vertex))
    for _ in range(class_size - 1):
        twin = len(result)
        result.add_node(twin)
        result.add_edges_from((twin, neighbor) for neighbor in neighbors)
    return nx.convert_node_labels_to_integers(result)


def exact_record(module, name, seed_row, graph, vertex, class_size, maximum_forests):
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    adjacency = [0] * n
    for u, v in graph.edges():
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    old = signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(CAP)
    start = time.monotonic()
    try:
        forest, fw, fc = module.largest_induced(adjacency, module.is_forest_mask)
        bipartite, bw, bc = module.largest_induced(adjacency, module.is_bipartite_mask)
        path_cover, paths, pc = module.exact_path_cover(adjacency)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    rhs = math.ceil((path_cover + bipartite + 1) / 2)
    residual = (n - path_cover) + (n - bipartite) - 2 * (n - forest)
    return {
        "event": "critical_clone_evaluated", "name": name,
        "seed_name": seed_row["name"], "seed_graph6": seed_row["graph6"],
        "cloned_vertex": vertex, "clone_class_size": class_size,
        "seed_maximum_forest_count": maximum_forests,
        "n": n, "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "edges": sorted([u, v] for u, v in graph.edges()),
        "forest": forest, "forest_witness": fw,
        "bipartite": bipartite, "bipartite_witness": bw,
        "path_cover": path_cover, "path_cover_paths": paths,
        "rhs": rhs, "slack": forest - rhs, "residual_R": residual,
        "crossing": forest < rhs,
        "delta": {"forest": forest - seed_row["forest"],
                  "bipartite": bipartite - seed_row["bipartite"],
                  "path_cover": path_cover - seed_row["path_cover"],
                  "R": residual - 1},
        "search_counts": {"forest_subsets": fc, "bipartite_subsets": bc,
                          "path_cover_transitions": pc},
        "seconds": round(time.monotonic() - start, 6),
    }


def main():
    module = source_module()
    completed = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("event") == "critical_clone_evaluated":
                completed.add(row["name"])
    candidates, seen = [], []
    for seed_name, seed_row, graph in canonical_r1_seeds():
        graph = nx.convert_node_labels_to_integers(graph)
        vertices, maximum_forests = critical_vertices(module, graph, seed_row["forest"])
        for vertex in vertices:
            for order in range(12, 17):
                class_size = order - len(graph) + 1
                transformed = false_twin_lift(graph, vertex, class_size)
                fingerprint = (len(transformed), transformed.number_of_edges(),
                               nx.weisfeiler_lehman_graph_hash(transformed))
                if any(fingerprint == old_fp and nx.is_isomorphic(transformed, old_graph)
                       for old_fp, old_graph in seen):
                    continue
                seen.append((fingerprint, transformed))
                name = f"clone_{seed_name}_v{vertex}_k{class_size}"
                candidates.append((name, seed_row, transformed, vertex,
                                   class_size, maximum_forests))
    candidates = candidates[:80]
    if not LEDGER.exists():
        append({"event": "critical_clone_contract_frozen", "r1_seeds": 13,
                "orders": [12, 16], "candidate_cap": 80,
                "solve_seconds": CAP, "evaluated_before_freeze": False})
    evaluated = timeouts = 0
    for name, seed_row, graph, vertex, class_size, maximum_forests in candidates:
        if name in completed:
            continue
        try:
            record = exact_record(module, name, seed_row, graph, vertex,
                                  class_size, maximum_forests)
        except SolveTimeout:
            append({"event": "critical_clone_timeout", "name": name,
                    "n": len(graph), "solve_seconds": CAP})
            timeouts += 1
            continue
        append(record)
        evaluated += 1
        if record["crossing"]:
            append({"event": "critical_clone_stopped_on_crossing",
                    "name": name, "graph6": record["graph6"]})
            print(json.dumps({"evaluated": evaluated, "timeouts": timeouts,
                              "crossing": name}))
            return
    append({"event": "critical_clone_pass_complete", "candidate_count": len(candidates),
            "evaluated_this_run": evaluated, "timeouts_this_run": timeouts})
    print(json.dumps({"candidates": len(candidates), "evaluated": evaluated,
                      "timeouts": timeouts, "crossing": None}))


if __name__ == "__main__":
    main()
