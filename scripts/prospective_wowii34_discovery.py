#!/usr/bin/env python3
"""Frozen prospective sweep for the current DeepMind WOWII 34 reading."""

import json
import math
import time
from fractions import Fraction

import networkx as nx


def relabel(graph):
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def clique_blowup(base, sizes):
    graph = nx.Graph()
    blobs = {}
    cursor = 0
    for vertex in sorted(base):
        size = sizes[vertex]
        blob = list(range(cursor, cursor + size))
        cursor += size
        graph.add_edges_from((u, v) for i, u in enumerate(blob) for v in blob[i + 1 :])
        graph.add_nodes_from(blob)
        blobs[vertex] = blob
    for u, v in base.edges():
        graph.add_edges_from((x, y) for x in blobs[u] for y in blobs[v])
    return graph


def layered_graph(sizes, clique_layers, skip_alternate=False):
    graph = nx.Graph()
    layers = []
    cursor = 0
    for index, size in enumerate(sizes):
        layer = list(range(cursor, cursor + size))
        cursor += size
        graph.add_nodes_from(layer)
        if clique_layers:
            graph.add_edges_from((u, v) for i, u in enumerate(layer) for v in layer[i + 1 :])
        layers.append(layer)
    for index in range(len(layers) - 1):
        graph.add_edges_from((u, v) for u in layers[index] for v in layers[index + 1])
    if skip_alternate:
        for index in range(0, len(layers) - 2, 2):
            graph.add_edges_from((u, v) for u in layers[index] for v in layers[index + 2])
    return graph


def portal_blocks(sizes, join):
    graph = nx.Graph()
    blocks = []
    cursor = 0
    for size in sizes:
        block = list(range(cursor, cursor + size))
        cursor += size
        graph.add_edges_from((u, v) for i, u in enumerate(block) for v in block[i + 1 :])
        blocks.append(block)
    for index in range(len(blocks) - 1):
        left, right = blocks[index], blocks[index + 1]
        if join == "edge":
            graph.add_edge(left[-1], right[0])
        elif join == "bipartite2":
            graph.add_edges_from((u, v) for u in left[-2:] for v in right[:2])
    return graph


def exact_distance_rhs(graph):
    eccentricity = nx.eccentricity(graph)
    radius = min(eccentricity.values())
    center = {v for v, value in eccentricity.items() if value == radius}
    maximum_degree = max(dict(graph.degree()).values())
    max_vertices = {v for v, value in graph.degree() if value == maximum_degree}
    distances = dict(nx.all_pairs_shortest_path_length(graph))

    def average_to(vertices):
        return Fraction(sum(min(distances[v][s] for s in vertices) for v in graph), len(graph))

    center_average = average_to(center)
    max_average = average_to(max_vertices)
    total = center_average + max_average
    return math.ceil(total), center_average, max_average, sorted(center), sorted(max_vertices)


def longest_induced_path(graph, deadline):
    adjacency = {v: set(graph[v]) for v in graph}
    best = ()
    visited_states = set()
    calls = 0

    def extend(path, used):
        nonlocal best, calls
        calls += 1
        if calls % 4096 == 0 and time.monotonic() > deadline:
            raise TimeoutError
        if len(path) > len(best):
            best = tuple(path)
        endpoint = path[-1]
        state = (frozenset(used), endpoint)
        if state in visited_states:
            return
        visited_states.add(state)
        forbidden = used - {endpoint}
        for candidate in adjacency[endpoint] - used:
            if adjacency[candidate].isdisjoint(forbidden):
                extend(path + [candidate], used | {candidate})

    for start in graph:
        extend([start], {start})
    return len(best), list(best), calls, len(visited_states)


def constructions():
    seen = set()

    def emit(name, graph, meta):
        graph = relabel(graph)
        signature = nx.weisfeiler_lehman_graph_hash(graph)
        key = (len(graph), graph.number_of_edges(), signature)
        if len(graph) <= 24 and len(graph) > 2 and nx.is_connected(graph) and key not in seen:
            seen.add(key)
            return name, graph, meta
        return None

    bases = []
    for order in range(3, 9):
        bases.append((f"P{order}", nx.path_graph(order), "path"))
        bases.append((f"C{order}", nx.cycle_graph(order), "cycle"))
    for left in range(2, 5):
        for right in range(left, 6):
            bases.append((f"K{left},{right}", nx.complete_bipartite_graph(left, right), "bipartite"))
    for base_name, base, base_kind in bases:
        n = len(base)
        patterns = [
            [1 + (i % 3) for i in range(n)],
            [min(5, i + 1) for i in range(n)],
            [min(5, n - i) for i in range(n)],
            [1 if i != n // 2 else 5 for i in range(n)],
            [5 if i in (0, n - 1) else 1 for i in range(n)],
        ]
        for index, sizes in enumerate(patterns):
            item = emit(f"blowup_{base_name}_{index}", clique_blowup(base, sizes), {
                "lane": 1,
                "base": base_kind,
                "sizes": sizes,
            })
            if item:
                yield item

    for layers in range(3, 9):
        patterns = [
            [1 + i % 4 for i in range(layers)],
            [1 if i in (0, layers - 1) else 3 for i in range(layers)],
            [4 if i == layers // 2 else 1 for i in range(layers)],
            [2 + (i % 2) for i in range(layers)],
        ]
        for sizes in patterns:
            for clique_layers in (False, True):
                for skip in (False, True):
                    item = emit(f"layers_{layers}_{sizes}_{clique_layers}_{skip}",
                        layered_graph(sizes, clique_layers, skip), {
                            "lane": 2,
                            "sizes": sizes,
                            "clique_layers": clique_layers,
                            "skip_alternate": skip,
                        })
                    if item:
                        yield item

    for blocks in range(2, 8):
        patterns = [
            [3 + i % 4 for i in range(blocks)],
            [3 if i == 0 else 5 for i in range(blocks)],
            [3 + (i % 2) * 2 for i in range(blocks)],
        ]
        for sizes in patterns:
            for join in ("edge", "bipartite2"):
                item = emit(f"blocks_{sizes}_{join}", portal_blocks(sizes, join), {
                    "lane": 3,
                    "sizes": sizes,
                    "join": join,
                })
                if item:
                    yield item

    product_bases = [nx.path_graph(i) for i in range(3, 7)] + [nx.cycle_graph(i) for i in range(4, 8)]
    factors = [nx.path_graph(2), nx.complete_graph(2), nx.complete_graph(3), nx.cycle_graph(4)]
    for i, base in enumerate(product_bases):
        for j, factor in enumerate(factors):
            for kind, product in (("strong", nx.strong_product), ("lex", nx.lexicographic_product)):
                item = emit(f"product_{kind}_{i}_{j}", product(base, factor), {
                    "lane": 4,
                    "kind": kind,
                })
                if item:
                    yield item


def main():
    retained = []
    evaluated = 0
    timeouts = 0
    for name, graph, meta in constructions():
        evaluated += 1
        rhs, center_average, max_average, center, max_vertices = exact_distance_rhs(graph)
        try:
            path_order, witness, calls, states = longest_induced_path(graph, time.monotonic() + 60)
            slack = path_order - rhs
        except TimeoutError:
            timeouts += 1
            retained.append({"name": name, "meta": meta, "n": len(graph), "status": "TIMEOUT"})
            continue
        if slack <= 2:
            retained.append({
                "name": name,
                "meta": meta,
                "n": len(graph),
                "m": graph.number_of_edges(),
                "graph6": nx.to_graph6_bytes(graph, header=False).strip().decode(),
                "center": center,
                "max_degree_vertices": max_vertices,
                "distavg_center": str(center_average),
                "distavg_max_degree": str(max_average),
                "ceil_sum": rhs,
                "path": path_order,
                "path_witness": witness,
                "slack": slack,
                "dfs_calls": calls,
                "dfs_states": states,
            })
    retained.sort(key=lambda row: (row.get("slack", 999), row["n"]))
    print(json.dumps({"summary": {"evaluated": evaluated, "retained": len(retained), "timeouts": timeouts}}))
    for row in retained:
        print(json.dumps(row))


if __name__ == "__main__":
    main()
