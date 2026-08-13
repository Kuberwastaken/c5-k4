#!/usr/bin/env python3
"""Frozen rooted balanced-biclique bouquet trial for current WOWII 40."""

import importlib.util
import json
import math
import signal
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


SEEDS = [
    ("ears_(2, 2)_twin0", "C}"),
    ("subst_1_3_1_clique_complete", "D~["),
    ("subst_1_3_1_clique_matching", "DjO"),
    ("subst_1_3_1_indep_complete", "Ds["),
    ("subst_2_3_2_indep_complete", "F]oxo"),
    ("subst_1_3_3_1_indep_complete", "Gs\\r_["),
    ("subst_2_4_2_indep_complete", "G]r@xw"),
    ("subst_2_2_4_2_indep_complete", "I]Kp`_NBo"),
    ("subst_2_3_2_3_indep_complete", "I]oxoKE@_"),
    ("subst_2_2_4_2_2_indep_complete", "K]Kp`_NBo@_E"),
]
PARAMETERS = [(3, 2), (4, 2), (2, 3)]


def source_module():
    path = Path(__file__).with_name("prospective_wowii40_block_surgery.py")
    spec = importlib.util.spec_from_file_location("wowii40_checkpoint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bouquet(seed, q, r):
    graph = nx.convert_node_labels_to_integers(seed)
    root = min(graph, key=lambda v: (-graph.degree(v), v))
    nxt = len(graph)
    for _ in range(q):
        left = [root] + list(range(nxt, nxt + r - 1)); nxt += r - 1
        right = list(range(nxt, nxt + r)); nxt += r
        graph.add_nodes_from(left[1:] + right)
        graph.add_edges_from((u, v) for u in left for v in right)
    return graph, root


def exact_path_cover_milp(graph):
    """Maximum spanning linear forest, with exact iterative cycle cuts."""
    edges = list(graph.edges())
    edge_index = {tuple(sorted(edge)): i for i, edge in enumerate(edges)}
    rows, lower, upper = [], [], []
    for vertex in graph:
        row = np.zeros(len(edges))
        for edge in graph.edges(vertex):
            row[edge_index[tuple(sorted(edge))]] = 1
        rows.append(row); lower.append(0); upper.append(2)
    cuts = 0
    while True:
        constraints = LinearConstraint(np.asarray(rows), np.asarray(lower), np.asarray(upper))
        result = milp(
            -np.ones(len(edges)), integrality=np.ones(len(edges)),
            bounds=Bounds(np.zeros(len(edges)), np.ones(len(edges))),
            constraints=constraints,
            options={"time_limit": 20, "mip_rel_gap": 0.0},
        )
        if not result.success:
            raise TimeoutError
        chosen = [edges[i] for i, value in enumerate(result.x) if value > 0.5]
        linear = nx.Graph(); linear.add_nodes_from(graph); linear.add_edges_from(chosen)
        cycles = nx.cycle_basis(linear)
        if not cycles:
            paths = []
            for component in nx.connected_components(linear):
                sub = linear.subgraph(component)
                if len(component) == 1:
                    paths.append([next(iter(component))]); continue
                endpoint = min(v for v in component if sub.degree(v) == 1)
                paths.append(list(nx.dfs_preorder_nodes(sub, endpoint)))
            return len(paths), paths, cuts, len(chosen)
        for cycle in cycles:
            cycle_edges = list(zip(cycle, cycle[1:] + cycle[:1]))
            row = np.zeros(len(edges))
            for edge in cycle_edges:
                row[edge_index[tuple(sorted(edge))]] = 1
            rows.append(row); lower.append(0); upper.append(len(cycle) - 1)
            cuts += 1


def exact_record(module, name, graph, root, q, r):
    graph = nx.convert_node_labels_to_integers(graph)
    n = len(graph); adjacency = [0] * n
    for u, v in graph.edges():
        adjacency[u] |= 1 << v; adjacency[v] |= 1 << u
    start = time.monotonic()
    forest, fw, fc = module.largest_induced(adjacency, module.is_forest_mask)
    bipartite, bw, bc = module.largest_induced(adjacency, module.is_bipartite_mask)
    path_cover, paths, cuts, linear_edges = exact_path_cover_milp(graph)
    rhs = math.ceil((path_cover + bipartite + 1) / 2)
    residual = (n - path_cover) + (n - bipartite) - 2 * (n - forest)
    return {
        "event": "bouquet_evaluated", "name": name, "q": q, "r": r,
        "root": root, "n": n, "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).strip().decode(),
        "forest": forest, "forest_witness": fw,
        "bipartite": bipartite, "bipartite_witness": bw,
        "path_cover": path_cover, "path_cover_paths": paths,
        "path_cover_method": "exact_milp_linear_forest_with_cycle_cuts",
        "path_cover_cycle_cuts": cuts, "linear_forest_edges": linear_edges,
        "rhs": rhs, "slack": forest-rhs, "residual_R": residual,
        "crossing": forest < rhs,
        "search_counts": {"forest_subsets": fc, "bipartite_subsets": bc},
        "seconds": round(time.monotonic()-start, 6),
    }


def main():
    module = source_module(); candidates=[]; excluded=[]
    for q, r in PARAMETERS:
        for name, graph6 in SEEDS:
            graph, root = bouquet(nx.from_graph6_bytes(graph6.encode()), q, r)
            if len(graph) > 18:
                excluded.append({"name": name, "q": q, "r": r, "order": len(graph)})
                continue
            fingerprint=(len(graph),graph.number_of_edges(),nx.weisfeiler_lehman_graph_hash(graph))
            if any(fingerprint==old_fp and nx.is_isomorphic(graph,old_graph)
                   for _,old_graph,old_fp,_,_,_ in candidates):
                continue
            candidates.append((name,graph,fingerprint,root,q,r))
            if len(candidates)>=20: break
        if len(candidates)>=20: break
    records=[exact_record(module,f"bouquet_q{q}_r{r}_of_{name}",graph,root,q,r)
             for name,graph,_,root,q,r in candidates]
    records.sort(key=lambda row:(row['slack'],row['n'],row['name']))
    print(json.dumps({"summary":{"distinct_bouquets":len(records),
        "excluded":excluded,"crossings":sum(r['crossing'] for r in records),"timeouts":0}}))
    for record in records: print(json.dumps(record))


if __name__ == '__main__':
    signal.alarm(60)
    main()
