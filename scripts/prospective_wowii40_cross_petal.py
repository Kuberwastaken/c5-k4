#!/usr/bin/env python3
"""Frozen cross-petal incompatibility trial for current WOWII #40."""

import argparse
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
LEDGER = ROOT / "results/expansion/prospective_wowii40_cross_petal_ledger.jsonl"
CAP = min(50, int(os.environ.get("WOWII40_CROSS_PETAL_CAP", "12")))
SEEDS = [
    ("c4_wall", "C]", 3, 4, 1),
    ("wall_8a", "Gs\\r_[", 5, 8, 1),
    ("wall_8b", "G]r@xw", 5, 8, 1),
    ("wall_8c", "GS\\r_[", 5, 8, 1),
    ("wall_8d", "GsLr_[", 5, 8, 1),
]
PATTERNS = ("parallel_ring", "crossed_ring", "primary_incompatibility")


class SolveTimeout(Exception):
    pass


def alarm_handler(_signum, _frame):
    raise SolveTimeout


def append(record):
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        out.flush()
        os.fsync(out.fileno())


def source_module():
    path = Path(__file__).with_name("prospective_wowii40_block_surgery.py")
    spec = importlib.util.spec_from_file_location("wowii40_source", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decode(graph6):
    return nx.convert_node_labels_to_integers(nx.from_graph6_bytes(graph6.encode()))


def exact_record(module, name, family, graph):
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
        pathable, witnesses = module.pathable_masks(adjacency)
        full = (1 << n) - 1
        if pathable[full]:
            path_cover, paths, pc = 1, [witnesses[full]], 0
        else:
            path_cover, paths, pc = module.exact_path_cover(adjacency)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
    rhs = math.ceil((path_cover + bipartite + 1) / 2)
    residual = (n - path_cover) + (n - bipartite) - 2 * (n - forest)
    return {
        "event": "graph_evaluated", "name": name, "family": family,
        "n": n, "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "edges": sorted([u, v] for u, v in graph.edges()),
        "forest": forest, "forest_witness": fw,
        "bipartite": bipartite, "bipartite_witness": bw,
        "path_cover": path_cover, "path_cover_paths": paths,
        "rhs": rhs, "slack": forest - rhs, "residual_R": residual,
        "crossing": forest < rhs,
        "search_counts": {"forest_subsets": fc, "bipartite_subsets": bc,
                          "path_cover_transitions": pc},
        "seconds": round(time.monotonic() - start, 6),
    }


def controls():
    for index, graph in enumerate(nx.graph_atlas_g()):
        if 3 <= len(graph) <= 7 and nx.is_connected(graph):
            yield f"atlas_{index}", graph
    for n in range(3, 10):
        yield f"path_{n}", nx.path_graph(n)
        yield f"cycle_{n}", nx.cycle_graph(n)
        yield f"complete_{n}", nx.complete_graph(n)
    yield "petersen", nx.petersen_graph()
    for a in range(2, 7):
        for b in range(a, 7):
            yield f"complete_bipartite_{a}_{b}", nx.complete_bipartite_graph(a, b)


def terminals(graph):
    colors = nx.bipartite.color(graph)
    if colors[0] != 0:
        colors = {v: 1 - color for v, color in colors.items()}
    left = sorted((v for v in graph if colors[v] == 0),
                  key=lambda v: (-graph.degree(v), v))
    right = sorted((v for v in graph if colors[v] == 1),
                   key=lambda v: (-graph.degree(v), v))
    if len(left) < 2 or len(right) < 2:
        raise AssertionError("each frozen seed must have two terminals per side")
    return left[:2], right[:2]


def compose(seed_graphs, pattern):
    result = nx.Graph()
    interfaces = []
    offset = 0
    for graph in seed_graphs:
        graph = nx.convert_node_labels_to_integers(graph)
        left, right = terminals(graph)
        mapping = {v: v + offset for v in graph}
        result = nx.compose(result, nx.relabel_nodes(graph, mapping))
        interfaces.append(([mapping[v] for v in left], [mapping[v] for v in right]))
        offset += len(graph)
    q = len(interfaces)
    if pattern in ("parallel_ring", "crossed_ring"):
        for i in range(q):
            left, _ = interfaces[i]
            _, next_right = interfaces[(i + 1) % q]
            if pattern == "parallel_ring":
                result.add_edge(left[0], next_right[0])
                result.add_edge(left[1], next_right[1])
            else:
                result.add_edge(left[0], next_right[1])
                result.add_edge(left[1], next_right[0])
    else:
        for i, j in itertools.combinations(range(q), 2):
            result.add_edge(interfaces[i][0][0], interfaces[j][1][0])
            result.add_edge(interfaces[j][0][0], interfaces[i][1][0])
    return nx.convert_node_labels_to_integers(result)


def sanity(module):
    start = time.monotonic()
    total = tight = 0
    for name, graph in controls():
        row = exact_record(module, name, "db_sanity", graph)
        total += 1
        tight += int(row["slack"] == 0)
        if row["crossing"]:
            append({"event": "db_sanity_reject", "control": row})
            print(json.dumps({"classification": "DB_SANITY_REJECT", "control": name}))
            return
    append({"event": "db_sanity_passed", "controls": total, "crossings": 0,
            "tight": tight, "process_seconds": round(time.monotonic() - start, 6)})
    print(json.dumps({"classification": "DB_SANITY_PASS", "controls": total}))


def candidate_specs():
    c4 = SEEDS[0]
    yield ((c4,) * 3)
    yield ((c4,) * 4)
    for left, right in itertools.combinations_with_replacement(SEEDS[1:], 2):
        yield (left, right)


def evaluate(module):
    prior = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    if not any(row.get("event") == "db_sanity_passed" for row in prior):
        raise RuntimeError("DB sanity must pass before development")
    verified = {}
    for name, graph6, expected_f, expected_b, expected_p in SEEDS:
        graph = decode(graph6)
        row = exact_record(module, name, "equality_seed", graph)
        actual = (row["forest"], row["bipartite"], row["path_cover"])
        if actual != (expected_f, expected_b, expected_p) or row["residual_R"] != 1:
            raise AssertionError((name, actual, row["residual_R"]))
        verified[name] = graph
    append({"event": "equality_seeds_verified", "seeds": list(verified)})

    raw = []
    for spec in candidate_specs():
        for pattern in PATTERNS:
            names = [item[0] for item in spec]
            graph = compose([verified[name] for name in names], pattern)
            name = f"{pattern}_of_{'_'.join(names)}"
            if 12 <= len(graph) <= 16 and nx.is_connected(graph):
                raw.append((name, pattern, names, graph))
    candidates = []
    buckets = {}
    for item in raw:
        graph = item[3]
        key = (len(graph), graph.number_of_edges(), nx.weisfeiler_lehman_graph_hash(graph))
        bucket = buckets.setdefault(key, [])
        if any(nx.is_isomorphic(graph, old) for old in bucket):
            continue
        bucket.append(graph)
        candidates.append(item)
    if len(candidates) > 36:
        raise AssertionError("frozen cap exceeded")
    completed = {row.get("name") for row in prior if row.get("event") == "graph_evaluated"}
    results = []
    for name, pattern, seed_names, graph in candidates:
        if name in completed:
            continue
        try:
            row = exact_record(module, name, "cross_petal_incompatibility", graph)
        except SolveTimeout:
            append({"event": "graph_timeout", "name": name, "pattern": pattern,
                    "seeds": seed_names, "n": len(graph), "solve_seconds": CAP})
            continue
        row["pattern"] = pattern
        row["seeds"] = seed_names
        append(row)
        results.append(row)
        if row["crossing"]:
            append({"event": "trial_stopped_on_crossing", "name": name,
                    "graph6": row["graph6"]})
            print(json.dumps({"crossing": name, "evaluated": len(results)}))
            return
    append({"event": "cross_petal_pass_complete", "raw": len(raw),
            "distinct": len(candidates), "evaluated_this_run": len(results),
            "crossings_this_run": sum(row["crossing"] for row in results)})
    print(json.dumps({"distinct": len(candidates), "evaluated": len(results),
                      "crossings": sum(row["crossing"] for row in results)}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("sanity", "evaluate"))
    args = parser.parse_args()
    module = source_module()
    if not LEDGER.exists():
        append({"event": "cross_petal_contract_frozen", "date": "2026-08-13",
                "seed_count": 5, "patterns": list(PATTERNS),
                "candidate_cap": 36, "orders": [12, 16],
                "solve_seconds": CAP, "evaluated_before_freeze": False,
                "public_action": False})
    if args.phase == "sanity":
        sanity(module)
    else:
        evaluate(module)


if __name__ == "__main__":
    main()
