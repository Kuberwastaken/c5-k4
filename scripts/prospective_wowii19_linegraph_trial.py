#!/usr/bin/env python3
"""Frozen WOWII 19 line-graph trial; emits append-only JSONL records."""

import argparse
import importlib.util
import itertools
import json
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


def load_module(filename, module_name):
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVALUATOR = load_module("prospective_wowii19_new_discovery.py", "wowii19_eval")
SQUARE = load_module("prospective_wowii19_square_trial.py", "wowii19_seeds")


def emit(row):
    print(json.dumps(row, sort_keys=True), flush=True)


def canonical_key(graph):
    return (len(graph), graph.number_of_edges(), nx.weisfeiler_lehman_graph_hash(graph))


def named_controls():
    rows = []
    rows.extend((f"C{n}", nx.cycle_graph(n)) for n in range(5, 10))
    rows.extend([
        ("P7", nx.path_graph(7)),
        ("Petersen", nx.petersen_graph()),
        ("K3,3", nx.complete_bipartite_graph(3, 3)),
        ("K7", nx.complete_graph(7)),
    ])
    rows.extend((f"K1,{n - 1}", nx.star_graph(n - 1)) for n in range(3, 9))
    rows.extend(
        (f"K{a},{b}", nx.complete_bipartite_graph(a, b))
        for a in range(2, 6) for b in range(a, 7)
    )
    unique = []
    for name, graph in rows:
        graph = nx.convert_node_labels_to_integers(graph)
        if any(canonical_key(graph) == canonical_key(old) and nx.is_isomorphic(graph, old)
               for _, old in unique):
            continue
        unique.append((name, graph))
    return unique


def gate():
    started = time.monotonic()
    rows = []
    for index, graph in enumerate(nx.graph_atlas_g()):
        if 2 <= len(graph) <= 7 and nx.is_connected(graph):
            rows.append((f"atlas:{index}", nx.convert_node_labels_to_integers(graph), "atlas"))
    rows.extend((name, graph, "named") for name, graph in named_controls())
    crossings = tight = timeouts = 0
    by_set = {"atlas": 0, "named": 0}
    for name, graph, source_set in rows:
        by_set[source_set] += 1
        try:
            result = EVALUATOR.evaluate(name, graph, {"stage": "db_gate", "set": source_set})
            result["event"] = "DB_GATE_ROW"
            crossings += result["slack"] < 0
            tight += result["slack"] == 0
            emit(result)
        except TimeoutError:
            timeouts += 1
            emit({"event": "DB_GATE_ROW", "name": name, "set": source_set,
                  "status": "TIMEOUT", "n": len(graph)})
    emit({"event": "DB_GATE_SUMMARY", "counts": by_set, "rows": len(rows),
          "crossings": crossings, "tight": tight, "timeouts": timeouts,
          "seconds": round(time.monotonic() - started, 6),
          "status": "PASS" if crossings == 0 and timeouts == 0 else "REJECT"})


def line_graph_representatives():
    representatives = []
    out_of_scope = []
    for name, graph6 in SQUARE.SEEDS:
        seed = nx.convert_node_labels_to_integers(nx.from_graph6_bytes(graph6.encode()))
        transformed = nx.convert_node_labels_to_integers(nx.line_graph(seed))
        if len(transformed) > 60:
            out_of_scope.append((name, graph6, len(transformed)))
            continue
        fingerprint = canonical_key(transformed)
        duplicate = None
        for row in representatives:
            if fingerprint == row[3] and nx.is_isomorphic(transformed, row[1]):
                duplicate = row
                break
        if duplicate is None:
            representatives.append([name, transformed, [name], fingerprint, graph6])
        else:
            duplicate[2].append(name)
    return representatives, out_of_scope


def development(skip=0, take=None):
    started = time.monotonic()
    representatives, out_of_scope = line_graph_representatives()
    if skip == 0:
        for name, graph6, order in out_of_scope:
            emit({"event": "DEVELOPMENT_ROW", "name": f"line_of_{name}",
                  "seed_graph6": graph6, "status": "OUT_OF_SCOPE", "n": order})
    crossings = tight = timeouts = 0
    selected = representatives[skip:] if take is None else representatives[skip:skip + take]
    for name, graph, aliases, _, seed_graph6 in selected:
        try:
            result = EVALUATOR.evaluate(
                f"line_of_{name}", graph,
                {"stage": "development", "transformation": "line_graph",
                 "seed_aliases": aliases, "seed_graph6": seed_graph6},
            )
            result["event"] = "DEVELOPMENT_ROW"
            result["edge_list"] = [list(edge) for edge in sorted(graph.edges())]
            crossings += result["slack"] < 0
            tight += result["slack"] == 0
            emit(result)
        except TimeoutError:
            timeouts += 1
            emit({"event": "DEVELOPMENT_ROW", "name": f"line_of_{name}",
                  "seed_graph6": seed_graph6, "status": "TIMEOUT", "n": len(graph)})
    verdict = "CANDIDATE" if crossings else ("INCONCLUSIVE" if timeouts else "HOLD_BOUNDED")
    emit({"event": "DEVELOPMENT_CHUNK_SUMMARY", "seed_rows": len(SQUARE.SEEDS),
          "distinct_in_scope": len(representatives), "out_of_scope": len(out_of_scope),
          "skip": skip, "selected": len(selected),
          "crossings": crossings, "tight": tight, "timeouts": timeouts,
          "seconds": round(time.monotonic() - started, 6), "verdict": verdict})


def exhaustive_bipartite_number(graph, deadline):
    vertices = tuple(graph)
    for size in range(len(vertices), -1, -1):
        for subset in itertools.combinations(vertices, size):
            if time.monotonic() > deadline:
                raise TimeoutError
            if nx.is_bipartite(graph.subgraph(subset)):
                return size, list(subset)
    raise AssertionError


def audit(graph6):
    """Independent small-candidate audit, deliberately not using the primary evaluator."""
    graph = nx.convert_node_labels_to_integers(nx.from_graph6_bytes(graph6.encode()))
    if len(graph) > 28:
        emit({"event": "INDEPENDENT_AUDIT", "graph6": graph6,
              "status": "INCONCLUSIVE", "reason": "independent exhaustive cap n=28"})
        return
    deadline = time.monotonic() + 60
    bipartite, witness = exhaustive_bipartite_number(graph, deadline)
    eccentricities = dict(nx.all_pairs_shortest_path_length(graph))
    ecc = {v: max(distances.values()) for v, distances in eccentricities.items()}
    local_values = {}
    local_witnesses = {}
    for vertex in graph:
        neighborhood = list(graph.neighbors(vertex))
        best = []
        for size in range(len(neighborhood), -1, -1):
            found = next((list(s) for s in itertools.combinations(neighborhood, size)
                          if graph.subgraph(s).number_of_edges() == 0), None)
            if found is not None:
                best = found
                break
        local_values[vertex] = len(best)
        local_witnesses[vertex] = best
    local_vertex = max(local_values, key=local_values.get)
    numerator = sum(ecc.values())
    rhs = (numerator + len(graph) * local_values[local_vertex]) // len(graph)
    emit({"event": "INDEPENDENT_AUDIT", "graph6": graph6, "status": "PASS",
          "n": len(graph), "b": bipartite, "bipartite_witness": witness,
          "eccentricity_sum": numerator, "average_denominator": len(graph),
          "local_max": local_values[local_vertex], "local_vertex": local_vertex,
          "local_witness": local_witnesses[local_vertex], "rhs": rhs,
          "slack": bipartite - rhs})


def edge_domain_bipartite(seed):
    """Maximize a bipartite degree-at-most-two seed-edge set."""
    vertices = list(seed)
    vertex_index = {v: i for i, v in enumerate(vertices)}
    edges = list(seed.edges())
    edge_count = len(edges)
    objective = np.zeros(edge_count + len(vertices))
    objective[:edge_count] = -1
    rows, lower, upper = [], [], []
    for edge_index, (u, v) in enumerate(edges):
        row = np.zeros(edge_count + len(vertices))
        row[edge_index] = -1
        row[edge_count + vertex_index[u]] = 1
        row[edge_count + vertex_index[v]] = 1
        rows.append(row); lower.append(0); upper.append(np.inf)
        row = np.zeros(edge_count + len(vertices))
        row[edge_index] = 1
        row[edge_count + vertex_index[u]] = 1
        row[edge_count + vertex_index[v]] = 1
        rows.append(row); lower.append(-np.inf); upper.append(2)
    for vertex in vertices:
        row = np.zeros(edge_count + len(vertices))
        for edge_index, edge in enumerate(edges):
            if vertex in edge:
                row[edge_index] = 1
        rows.append(row); lower.append(-np.inf); upper.append(2)
    result = milp(
        objective, integrality=np.ones(edge_count + len(vertices)),
        bounds=Bounds(np.zeros(edge_count + len(vertices)),
                      np.ones(edge_count + len(vertices))),
        constraints=LinearConstraint(np.asarray(rows), np.asarray(lower), np.asarray(upper)),
        options={"time_limit": 60, "mip_rel_gap": 0.0},
    )
    if not result.success:
        raise TimeoutError
    selected = [edges[i] for i in range(edge_count) if result.x[i] > 0.5]
    witness = nx.Graph()
    witness.add_nodes_from(vertices)
    witness.add_edges_from(selected)
    if max(dict(witness.degree()).values(), default=0) > 2 or not nx.is_bipartite(witness):
        raise AssertionError("invalid edge-domain witness")
    return len(selected), [list(edge) for edge in selected]


def audit_ledger(skip=0, take=None):
    ledger = Path(__file__).parents[1] / "results/expansion/prospective_wowii19_linegraph_ledger.jsonl"
    completed = []
    seen = set()
    for line in ledger.read_text().splitlines():
        row = json.loads(line)
        if row.get("event") != "DEVELOPMENT_ROW" or "slack" not in row:
            continue
        if row["name"] in seen:
            continue
        seen.add(row["name"])
        completed.append(row)
    selected_rows = completed[skip:] if take is None else completed[skip:skip + take]
    passes = mismatches = timeouts = 0
    for row in selected_rows:
        seed_graph6 = row["meta"]["seed_graph6"]
        seed = nx.convert_node_labels_to_integers(nx.from_graph6_bytes(seed_graph6.encode()))
        transformed = nx.convert_node_labels_to_integers(nx.line_graph(seed))
        serialized = nx.from_graph6_bytes(row["graph6"].encode())
        isomorphic = nx.is_isomorphic(transformed, serialized)
        eccentricity = nx.eccentricity(transformed)
        eccentricity_sum = sum(eccentricity.values())
        local = 0
        local_witness = []
        for vertex in transformed:
            neighborhood = list(transformed.neighbors(vertex))
            complement = nx.complement(transformed.subgraph(neighborhood))
            witness = max(nx.find_cliques(complement), key=len, default=[])
            if len(witness) > local:
                local, local_witness = len(witness), list(witness)
        try:
            bipartite, edge_witness = edge_domain_bipartite(seed)
        except TimeoutError:
            timeouts += 1
            emit({"event": "INDEPENDENT_EDGE_DOMAIN_AUDIT", "name": row["name"],
                  "status": "TIMEOUT", "seed_graph6": seed_graph6})
            continue
        rhs = (eccentricity_sum + len(transformed) * local) // len(transformed)
        agrees = (isomorphic and bipartite == row["b"] and local == row["max_local_independence"]
                  and rhs == row["rhs"] and bipartite - rhs == row["slack"])
        passes += agrees
        mismatches += not agrees
        emit({"event": "INDEPENDENT_EDGE_DOMAIN_AUDIT", "name": row["name"],
              "status": "PASS" if agrees else "MISMATCH", "seed_graph6": seed_graph6,
              "line_graph_isomorphic": isomorphic, "n": len(transformed),
              "eccentricity_sum": eccentricity_sum, "local_max": local,
              "local_witness": local_witness, "b": bipartite,
              "selected_seed_edges": edge_witness, "rhs": rhs,
              "slack": bipartite - rhs})
    emit({"event": "INDEPENDENT_AUDIT_CHUNK_SUMMARY", "completed_total": len(completed),
          "skip": skip, "selected": len(selected_rows), "passes": passes,
          "mismatches": mismatches, "timeouts": timeouts})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", choices=("gate", "development", "audit", "audit-ledger"), required=True)
    parser.add_argument("--graph6")
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--take", type=int)
    args = parser.parse_args()
    if args.lane == "gate":
        gate()
    elif args.lane == "development":
        development(args.skip, args.take)
    elif args.lane == "audit-ledger":
        audit_ledger(args.skip, args.take)
    elif not args.graph6:
        parser.error("--graph6 is required for --lane audit")
    else:
        audit(args.graph6)


if __name__ == "__main__":
    main()
