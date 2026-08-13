#!/usr/bin/env python3
"""Frozen line-graph trial from the ten WOWII 40 checkpoint equality rows."""

import importlib.util
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx


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


def source_module():
    path = Path(__file__).with_name("prospective_wowii40_block_surgery.py")
    spec = importlib.util.spec_from_file_location("wowii40_checkpoint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decode(graph6):
    return nx.convert_node_labels_to_integers(nx.from_graph6_bytes(graph6.encode()))


def exact_record(module, name, graph):
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph)
    adjacency = [0] * n
    for u, v in graph.edges():
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u
    start = time.monotonic()
    forest, forest_witness, forest_checks = module.largest_induced(adjacency, module.is_forest_mask)
    bipartite, bipartite_witness, bipartite_checks = module.largest_induced(
        adjacency, module.is_bipartite_mask)
    pathable, path_witnesses = module.pathable_masks(adjacency)
    full = (1 << n) - 1
    if pathable[full]:
        path_cover = 1
        paths = [path_witnesses[full]]
        path_method = "hamiltonian_full_mask"
    else:
        path_cover, paths, _ = module.exact_path_cover(adjacency)
        path_method = "exact_partition_dp"
    rhs = math.ceil((path_cover + bipartite + 1) / 2)
    residual = (n - path_cover) + (n - bipartite) - 2 * (n - forest)
    return {
        "event": "linegraph_evaluated", "name": name, "n": n,
        "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).strip().decode(),
        "forest": forest, "forest_witness": forest_witness,
        "bipartite": bipartite, "bipartite_witness": bipartite_witness,
        "path_cover": path_cover, "path_cover_paths": paths,
        "path_method": path_method, "rhs": rhs, "slack": forest - rhs,
        "residual_R": residual, "crossing": forest < rhs,
        "search_counts": {"forest_subsets": forest_checks,
                          "bipartite_subsets": bipartite_checks},
        "seconds": round(time.monotonic() - start, 6),
    }


def main():
    module = source_module()
    candidates = []
    excluded = []
    for name, graph6, forest, bipartite, path_cover in SEEDS:
        graph = decode(graph6)
        residual = (len(graph) - path_cover) + (len(graph) - bipartite) - 2 * (len(graph) - forest)
        if residual not in (1, 2):
            raise AssertionError((name, residual))
        line = nx.convert_node_labels_to_integers(nx.line_graph(graph))
        if not (3 <= len(line) <= 18 and nx.is_connected(line)):
            excluded.append({"name": name, "line_order": len(line)})
            continue
        fingerprint = (len(line), line.number_of_edges(), nx.weisfeiler_lehman_graph_hash(line))
        duplicate = False
        for _, old, old_fingerprint in candidates:
            if fingerprint == old_fingerprint and nx.is_isomorphic(line, old):
                duplicate = True
                break
        if not duplicate:
            candidates.append((name, line, fingerprint))
    records = [exact_record(module, f"line_of_{name}", graph)
               for name, graph, _ in candidates]
    records.sort(key=lambda row: (row["slack"], row["n"], row["name"]))
    print(json.dumps({"summary": {
        "checkpoint_seeds": len(SEEDS), "excluded_over_order": excluded,
        "distinct_line_graphs": len(candidates),
        "crossings": sum(row["crossing"] for row in records),
        "timeouts": 0,
    }}))
    for record in records:
        print(json.dumps(record))


if __name__ == "__main__":
    signal.alarm(60)
    main()
