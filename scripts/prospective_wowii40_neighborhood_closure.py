#!/usr/bin/env python3
"""Frozen neighborhood-closure trial from the ten WOWII 40 equality rows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii40_neighborhood_closure_ledger.jsonl"
SEEDS = [
    ("ears_(2, 2)_twin0", "C}", 3, 3, 1),
    ("subst_1_3_1_clique_complete", "D~[", 3, 3, 1),
    ("subst_1_3_1_clique_matching", "DjO", 4, 4, 2),
    ("subst_1_3_1_indep_complete", "Ds[", 4, 5, 1),
    ("subst_2_3_2_indep_complete", "F]oxo", 5, 7, 1),
    ("subst_1_3_3_1_indep_complete", "Gs\\r_[", 5, 8, 1),
    ("subst_2_4_2_indep_complete", "G]r@xw", 5, 8, 1),
    ("subst_2_2_4_2_indep_complete", "I]Kp`_NBo", 7, 10, 2),
    ("subst_2_3_2_3_indep_complete", "I]oxoKE@_", 7, 10, 2),
    ("subst_2_2_4_2_2_indep_complete", "K]Kp`_NBo@_E", 9, 12, 4),
]


def append(record: dict[str, object]) -> None:
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        out.flush()


def source_module():
    path = Path(__file__).with_name("prospective_wowii40_block_surgery.py")
    spec = importlib.util.spec_from_file_location("wowii40_checkpoint", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def decode(graph6: str) -> nx.Graph:
    graph = nx.from_graph6_bytes(graph6.encode())
    return nx.convert_node_labels_to_integers(graph)


def exact_record(module, name: str, family: str, graph: nx.Graph) -> dict[str, object]:
    graph = nx.convert_node_labels_to_integers(nx.Graph(graph))
    n = len(graph)
    adjacency = [0] * n
    for u, v in graph.edges():
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    start = time.monotonic()
    forest, forest_witness, forest_checks = module.largest_induced(
        adjacency, module.is_forest_mask)
    bipartite, bipartite_witness, bipartite_checks = module.largest_induced(
        adjacency, module.is_bipartite_mask)
    pathable, path_witnesses = module.pathable_masks(adjacency)
    full = (1 << n) - 1
    if pathable[full]:
        path_cover = 1
        paths = [path_witnesses[full]]
        path_method = "hamiltonian_full_mask"
        path_transitions = 0
    else:
        path_cover, paths, path_transitions = module.exact_path_cover(adjacency)
        path_method = "exact_partition_dp"
    rhs = math.ceil((path_cover + bipartite + 1) / 2)
    residual = (n - path_cover) + (n - bipartite) - 2 * (n - forest)
    return {
        "event": "graph_evaluated", "name": name, "family": family,
        "n": n, "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).strip().decode(),
        "edges": sorted([u, v] for u, v in graph.edges()),
        "forest": forest, "forest_witness": forest_witness,
        "bipartite": bipartite, "bipartite_witness": bipartite_witness,
        "path_cover": path_cover, "path_cover_paths": paths,
        "path_method": path_method, "rhs": rhs,
        "slack": forest - rhs, "residual_R": residual,
        "parity_epsilon": (path_cover + bipartite + 1) % 2,
        "crossing": forest < rhs,
        "search_counts": {
            "forest_subsets": forest_checks,
            "bipartite_subsets": bipartite_checks,
            "path_cover_transitions": path_transitions,
        },
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


def neighborhood_closure(graph: nx.Graph, vertex: int) -> tuple[nx.Graph, int]:
    closed = nx.Graph(graph)
    missing = [(u, w) for u in graph.neighbors(vertex)
               for w in graph.neighbors(vertex)
               if u < w and not graph.has_edge(u, w)]
    closed.add_edges_from(missing)
    return nx.convert_node_labels_to_integers(closed), len(missing)


def sanity(module) -> None:
    start = time.monotonic()
    rows = []
    for name, graph in controls():
        row = exact_record(module, name, "db_sanity", graph)
        rows.append(row)
        if row["crossing"]:
            append({"event": "db_sanity_reject", "control": row})
            print(json.dumps({"classification": "DB_SANITY_REJECT", "control": name}))
            return
    append({
        "event": "db_sanity_passed", "controls": len(rows),
        "crossings": 0, "tight": sum(row["slack"] == 0 for row in rows),
        "set": "connected Graph Atlas orders 3..7; P_n,C_n,K_n orders 3..9; Petersen; K(a,b), 2<=a<=b<=6",
        "method": "exact subset maxima and exact Hamiltonian-subset path-cover DP",
        "process_seconds": round(time.monotonic() - start, 6),
    })
    print(json.dumps({"classification": "DB_SANITY_PASS", "controls": len(rows)}))


def evaluate(module) -> None:
    events = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines()]
    if not any(row.get("event") == "db_sanity_passed" for row in events):
        raise RuntimeError("DB sanity must pass before transformed evaluation")

    verified_seeds = []
    candidates: list[tuple[str, nx.Graph, int, str]] = []
    for name, graph6, expected_f, expected_b, expected_p in SEEDS:
        graph = decode(graph6)
        seed = exact_record(module, name, "checkpoint_seed", graph)
        actual = (seed["forest"], seed["bipartite"], seed["path_cover"])
        expected = (expected_f, expected_b, expected_p)
        if actual != expected:
            raise AssertionError((name, expected, actual))
        epsilon = (expected_p + expected_b + 1) % 2
        if 2 * expected_f != expected_p + expected_b + 1 + epsilon:
            raise AssertionError((name, "parity wall failed"))
        verified_seeds.append({
            "name": name, "n": len(graph), "f": expected_f,
            "b": expected_b, "p": expected_p, "epsilon": epsilon,
            "R": 1 + epsilon,
        })
        for vertex in graph.nodes():
            closed, added = neighborhood_closure(graph, vertex)
            if added == 0 or not nx.is_connected(closed) or not (3 <= len(closed) <= 12):
                continue
            candidate_name = f"closure_{name}_v{vertex}"
            candidates.append((candidate_name, closed, added, name))

    deduplicated: list[tuple[str, nx.Graph, int, str]] = []
    buckets: dict[tuple[int, int, str], list[nx.Graph]] = {}
    for item in candidates:
        name, graph, added, source = item
        key = (len(graph), graph.number_of_edges(), nx.weisfeiler_lehman_graph_hash(graph))
        bucket = buckets.setdefault(key, [])
        if any(nx.is_isomorphic(graph, old) for old in bucket):
            continue
        bucket.append(graph)
        deduplicated.append(item)
    if len(deduplicated) > 120:
        raise AssertionError("frozen candidate cap exceeded")

    append({"event": "checkpoint_identity_verified", "seeds": verified_seeds})
    results = []
    for name, graph, added, source in deduplicated:
        row = exact_record(module, name, "neighborhood_closure", graph)
        row["source_seed"] = source
        row["edges_added"] = added
        append(row)
        results.append(row)
    summary = {
        "event": "neighborhood_closure_trial_complete",
        "raw_closures": len(candidates), "distinct_closures": len(results),
        "crossings": sum(bool(row["crossing"]) for row in results),
        "tight": sum(row["slack"] == 0 for row in results),
        "minimum_slack": min((row["slack"] for row in results), default=None),
        "timeouts": 0,
    }
    append(summary)
    print(json.dumps(summary, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("sanity", "evaluate"))
    args = parser.parse_args()
    signal.alarm(60)
    module = source_module()
    if args.phase == "sanity":
        sanity(module)
    else:
        evaluate(module)


if __name__ == "__main__":
    main()
