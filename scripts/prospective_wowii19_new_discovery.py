#!/usr/bin/env python3
"""Frozen prospective current-DeepMind WOWII 19 discovery sweep."""

import argparse
import itertools
import json
import math
import random
import time
from fractions import Fraction

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


def odd_cycle_blocks(lengths, shape="path", shared=False):
    graph = nx.Graph()
    blocks = []
    cursor = 0
    for length in lengths:
        vertices = list(range(cursor, cursor + length))
        cursor += length
        graph.add_edges_from((vertices[i], vertices[(i + 1) % length]) for i in range(length))
        blocks.append(vertices)
    parents = []
    if shape == "path":
        parents = [(i - 1, i) for i in range(1, len(blocks))]
    elif shape == "star":
        parents = [(0, i) for i in range(1, len(blocks))]
    elif shape == "fork":
        parents = [(0, 1)] + [(1, i) for i in range(2, len(blocks))]
    elif shape == "broom":
        parents = [(i - 1, i) for i in range(1, max(2, len(blocks) - 2))]
        hub = max(0, len(blocks) - 3)
        parents += [(hub, i) for i in range(hub + 1, len(blocks))]
    representatives = [block[0] for block in blocks]
    for left, right in parents:
        if shared:
            graph = nx.contracted_nodes(graph, representatives[left], representatives[right], self_loops=False)
            representatives[right] = representatives[left]
        else:
            graph.add_edge(blocks[left][0], blocks[right][0])
    return nx.convert_node_labels_to_integers(graph)


def substitute(base, sizes, kinds):
    graph = nx.Graph()
    blobs = {}
    cursor = 0
    for vertex in sorted(base):
        blob = list(range(cursor, cursor + sizes[vertex]))
        cursor += sizes[vertex]
        graph.add_nodes_from(blob)
        if kinds[vertex] == "clique":
            graph.add_edges_from(itertools.combinations(blob, 2))
        blobs[vertex] = blob
    for u, v in base.edges():
        graph.add_edges_from((x, y) for x in blobs[u] for y in blobs[v])
    return graph


def local_independence(graph, deadline):
    best_size, best_vertex, best_set = 0, None, []
    for vertex in graph:
        if time.monotonic() > deadline:
            raise TimeoutError
        neighborhood = list(graph[vertex])
        complement = nx.complement(graph.subgraph(neighborhood))
        clique = max(nx.find_cliques(complement), key=len, default=[])
        if len(clique) > best_size:
            best_size, best_vertex, best_set = len(clique), vertex, sorted(clique)
    return best_size, best_vertex, best_set


def bipartite_number(graph, deadline):
    vertices = list(graph)
    checks = 0
    for deletions in range(len(vertices) + 1):
        for removed in itertools.combinations(vertices, deletions):
            checks += 1
            if checks % 2048 == 0 and time.monotonic() > deadline:
                raise TimeoutError
            remaining = set(vertices) - set(removed)
            if nx.is_bipartite(graph.subgraph(remaining)):
                return len(remaining), sorted(remaining), sorted(removed), checks
    raise AssertionError


def bipartite_number_ilp(graph):
    """Exact maximum induced bipartite order via retained/color binaries."""
    vertices = list(graph)
    index = {vertex: offset for offset, vertex in enumerate(vertices)}
    order = len(vertices)
    objective = np.zeros(2 * order)
    objective[:order] = -1
    rows, lower, upper = [], [], []
    for u, v in graph.edges():
        row = np.zeros(2 * order)
        row[index[u]] = -1
        row[index[v]] = -1
        row[order + index[u]] = 1
        row[order + index[v]] = 1
        # If both endpoints are retained, their binary colors sum to one.
        rows.append(row)
        lower.append(-1)
        upper.append(np.inf)
        row = np.zeros(2 * order)
        row[index[u]] = 1
        row[index[v]] = 1
        row[order + index[u]] = 1
        row[order + index[v]] = 1
        rows.append(row)
        lower.append(-np.inf)
        upper.append(3)
    constraints = LinearConstraint(np.asarray(rows), np.asarray(lower), np.asarray(upper))
    result = milp(
        objective,
        integrality=np.ones(2 * order),
        bounds=Bounds(np.zeros(2 * order), np.ones(2 * order)),
        constraints=constraints,
        options={"time_limit": 10, "mip_rel_gap": 0.0},
    )
    if not result.success:
        raise TimeoutError
    witness = sorted(vertices[i] for i in range(order) if result.x[i] > 0.5)
    removed = sorted(set(vertices) - set(witness))
    if not nx.is_bipartite(graph.subgraph(witness)):
        raise AssertionError("MILP returned a non-bipartite witness")
    return len(witness), witness, removed, "scipy_milp_optimal"


def evaluate(name, graph, meta):
    deadline = time.monotonic() + 2
    eccentricity = nx.eccentricity(graph)
    average = Fraction(sum(eccentricity.values()), len(graph))
    local, local_vertex, local_witness = local_independence(graph, deadline)
    try:
        bipartite, bipartite_witness, deletion_witness, checks = bipartite_number(graph, deadline)
    except TimeoutError:
        bipartite, bipartite_witness, deletion_witness, checks = bipartite_number_ilp(graph)
    rhs = math.floor(average + local)
    return {
        "name": name,
        "meta": meta,
        "n": len(graph),
        "m": graph.number_of_edges(),
        "graph6": nx.to_graph6_bytes(graph, header=False).strip().decode(),
        "average_eccentricity": str(average),
        "max_local_independence": local,
        "local_vertex": local_vertex,
        "local_witness": local_witness,
        "rhs": rhs,
        "b": bipartite,
        "bipartite_witness": bipartite_witness,
        "odd_cycle_deletion_witness": deletion_witness,
        "bipartite_subset_checks": checks,
        "slack": bipartite - rhs,
    }


def bases():
    seen = set()

    def emit(name, graph, meta):
        graph = nx.convert_node_labels_to_integers(graph)
        key = (len(graph), graph.number_of_edges(), nx.weisfeiler_lehman_graph_hash(graph))
        if 2 < len(graph) <= 22 and nx.is_connected(graph) and key not in seen:
            seen.add(key)
            return name, graph, meta
        return None

    for blocks in range(2, 7):
        patterns = [
            tuple(3 + 2 * (i % 3) for i in range(blocks)),
            tuple([3] + [5] * (blocks - 1)),
            tuple([7 if i == blocks // 2 else 3 for i in range(blocks)]),
        ]
        for lengths in patterns:
            for shape in ("path", "star", "fork", "broom"):
                for shared in (False, True):
                    item = emit(f"blocks_{lengths}_{shape}_{shared}",
                        odd_cycle_blocks(lengths, shape, shared), {
                            "lane": 1,
                            "lengths": lengths,
                            "shape": shape,
                            "shared": shared,
                        })
                    if item:
                        yield item

    base_graphs = [nx.cycle_graph(length) for length in (3, 5, 7)]
    base_graphs += [odd_cycle_blocks((3, 5), "path", False), odd_cycle_blocks((3, 3, 5), "star", True)]
    for base_index, base in enumerate(base_graphs):
        n = len(base)
        patterns = [
            [1 + (i % 4) for i in range(n)],
            [4 if i == 0 else 1 for i in range(n)],
            [min(4, i + 1) for i in range(n)],
            [3 if i == n // 2 else 1 for i in range(n)],
        ]
        kinds_patterns = [
            ["clique"] * n,
            ["independent" if i % 2 == 0 else "clique" for i in range(n)],
            ["independent"] * n,
        ]
        for pattern_index, sizes in enumerate(patterns):
            for kinds_index, kinds in enumerate(kinds_patterns):
                item = emit(f"substitute_{base_index}_{pattern_index}_{kinds_index}",
                    substitute(base, sizes, kinds), {
                        "lane": 2,
                        "base": base_index,
                        "sizes": sizes,
                        "kinds": kinds,
                    })
                if item:
                    yield item


def surgeries(graph, limit, rng):
    candidates = []
    vertices = list(graph)
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    nonedges = sorted(tuple(sorted(edge)) for edge in nx.non_edges(graph))
    for edge in edges:
        candidates.append(("delete", edge))
    for edge in nonedges:
        candidates.append(("add", edge))
    for u, v in edges:
        for w in vertices:
            if w not in (u, v) and not graph.has_edge(u, w):
                candidates.append(("reattach", (u, v, w)))
    rng.shuffle(candidates)
    emitted = 0
    for operation, data in candidates:
        changed = graph.copy()
        if operation == "delete":
            changed.remove_edge(*data)
        elif operation == "add":
            changed.add_edge(*data)
        else:
            u, v, w = data
            changed.remove_edge(u, v)
            changed.add_edge(u, w)
        if nx.is_connected(changed):
            yield changed, (operation, data)
            emitted += 1
            if emitted >= limit:
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", choices=("base", "surgery"), default="base")
    parser.add_argument("--per-seed", type=int, default=100)
    args = parser.parse_args()
    inputs = list(bases())
    if args.lane == "surgery":
        rng = random.Random(1920260813)
        surgery_inputs = []
        remaining = 5000
        for name, graph, meta in inputs:
            if len(graph) > 20 or remaining <= 0:
                continue
            amount = min(args.per_seed, remaining)
            for index, (changed, operation) in enumerate(surgeries(graph, amount, rng)):
                surgery_inputs.append((f"{name}_surgery_{index}", changed, {
                    **meta,
                    "lane": 3,
                    "parent": name,
                    "operation": operation,
                }))
                remaining -= 1
        inputs = surgery_inputs
    retained, timeouts = [], 0
    for name, graph, meta in inputs:
        try:
            result = evaluate(name, graph, meta)
        except TimeoutError:
            timeouts += 1
            retained.append({"name": name, "n": len(graph), "meta": meta, "status": "TIMEOUT"})
            continue
        if result["slack"] <= 2:
            retained.append(result)
    retained.sort(key=lambda row: (row.get("slack", 999), row["n"]))
    print(json.dumps({"summary": {"evaluated": len(inputs), "retained": len(retained), "timeouts": timeouts}}))
    for row in retained:
        print(json.dumps(row))


if __name__ == "__main__":
    main()
