#!/usr/bin/env python3
"""Frozen prospective joint trial for current DeepMind WOWII 145 and 146.

The contract is results/expansion/prospective_wowii145_146_contract.md.  This
script only appends JSON records to the associated ledger.  A geodesic or
explicitly grown induced tree is a rigorous lower bound; exact subset search
is invoked only when that lower bound does not already certify both bounds.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii145_146_ledger.jsonl"


def append(record: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def graph6(graph: nx.Graph) -> str:
    return nx.to_graph6_bytes(nx.convert_node_labels_to_integers(graph), header=False).decode().strip()


def cycle_clique_blowup(sizes: tuple[int, ...]) -> nx.Graph:
    graph = nx.Graph()
    blobs: list[list[int]] = []
    for size in sizes:
        blob = list(range(graph.number_of_nodes(), graph.number_of_nodes() + size))
        graph.add_nodes_from(blob)
        graph.add_edges_from(itertools.combinations(blob, 2))
        blobs.append(blob)
    for index in range(5):
        graph.add_edges_from(itertools.product(blobs[index], blobs[(index + 1) % 5]))
    graph.graph["blobs"] = blobs
    return graph


def attach_tail(graph: nx.Graph, attachment: int, length: int) -> nx.Graph:
    result = graph.copy()
    previous = attachment
    for _ in range(length):
        vertex = result.number_of_nodes()
        result.add_edge(previous, vertex)
        previous = vertex
    return result


def attach_pendant_clique(graph: nx.Graph, attachment: int, size: int) -> nx.Graph:
    result = graph.copy()
    block = list(range(result.number_of_nodes(), result.number_of_nodes() + size))
    result.add_nodes_from(block)
    result.add_edges_from(itertools.combinations(block, 2))
    result.add_edge(attachment, block[0])
    return result


def portal_surgery(m: int, portals: int, tail: int) -> nx.Graph:
    graph = cycle_clique_blowup((m,) * 5)
    blobs = graph.graph["blobs"]
    graph.remove_edges_from(list(itertools.product(blobs[0], blobs[1])))
    for index in range(portals):
        graph.add_edge(blobs[0][index], blobs[1][index])
    if tail:
        graph = attach_tail(graph, blobs[0][0], tail)
    return graph


def metric_terms(graph: nx.Graph) -> tuple[int, int, list[int], dict[int, dict[int, int]]]:
    distances = {u: dict(row) for u, row in nx.all_pairs_shortest_path_length(graph)}
    eccentricity = {u: max(row.values()) for u, row in distances.items()}
    diameter = max(eccentricity.values())
    boundary = sorted(u for u, value in eccentricity.items() if value == diameter)
    outside = set(graph) - set(boundary)
    ecc_set = max((min(distances[u][v] for v in boundary) for u in outside), default=0)
    square_radius = math.ceil(min(eccentricity.values()) / 2)
    return diameter, ecc_set, boundary, distances


def complement_local_independence_min(graph: nx.Graph) -> int:
    values = []
    vertices = set(graph)
    for vertex in graph:
        nonneighbors = vertices - {vertex} - set(graph[vertex])
        if not nonneighbors:
            values.append(0)
            continue
        induced = graph.subgraph(nonneighbors)
        values.append(max(len(clique) for clique in nx.find_cliques(induced)))
    return min(values)


def is_induced_tree_mask(adjacency: list[int], mask: int) -> bool:
    count = bin(mask).count("1")
    if count == 0:
        return False
    edges_twice = sum(bin(adjacency[v] & mask).count("1") for v in range(len(adjacency)) if mask >> v & 1)
    if edges_twice != 2 * (count - 1):
        return False
    seen = 0
    frontier = mask & -mask
    while frontier:
        seen |= frontier
        neighbours = 0
        scan = frontier
        while scan:
            bit = scan & -scan
            scan ^= bit
            neighbours |= adjacency[bit.bit_length() - 1]
        frontier = neighbours & mask & ~seen
    return seen == mask


def greedy_tree_witness(graph: nx.Graph, distances: dict[int, dict[int, int]]) -> list[int]:
    nodes = list(graph)
    source, target = max(((u, v) for u in nodes for v in nodes), key=lambda pair: distances[pair[0]][pair[1]])
    best = list(nx.shortest_path(graph, source, target))
    for root in nodes:
        for reverse in (False, True):
            chosen = {root}
            while True:
                candidates = [v for v in nodes if v not in chosen and len(set(graph[v]) & chosen) == 1]
                if not candidates:
                    break
                candidates.sort(key=lambda v: (graph.degree(v), v), reverse=reverse)
                chosen.add(candidates[0])
            induced = graph.subgraph(chosen)
            if nx.is_tree(induced) and len(chosen) > len(best):
                best = sorted(chosen)
    return best


def exact_largest_induced_tree(graph: nx.Graph, stop_below: int | None = None) -> tuple[int, list[int], int]:
    nodes = list(graph)
    index = {v: i for i, v in enumerate(nodes)}
    adjacency = [sum(1 << index[w] for w in graph[v]) for v in nodes]
    checked = 0
    lower = stop_below or 1
    for size in range(len(nodes), lower - 1, -1):
        for chosen in itertools.combinations(range(len(nodes)), size):
            checked += 1
            mask = sum(1 << v for v in chosen)
            if is_induced_tree_mask(adjacency, mask):
                return size, [nodes[v] for v in chosen], checked
    return lower - 1, [], checked


def evaluate(graph: nx.Graph, name: str, stage: str, force_exact: bool = False) -> dict:
    started = time.monotonic()
    assert graph.number_of_nodes() > 1 and nx.is_connected(graph)
    diameter, ecc_set, boundary, distances = metric_terms(graph)
    radius = nx.radius(graph)
    square_radius = math.ceil(radius / 2)
    local_min = complement_local_independence_min(graph)
    witness = greedy_tree_witness(graph, distances)
    tree_lower = len(witness)
    lower145 = None if local_min == 0 else tree_lower * local_min - 2 * ecc_set
    lower146 = None if square_radius == 0 else tree_lower * square_radius - 2 * ecc_set
    needs_exact = force_exact or (local_min > 0 and lower145 < 0) or (square_radius > 0 and lower146 < 0)
    exact = None
    checked = 0
    if needs_exact and graph.number_of_nodes() <= 22:
        exact, exact_witness, checked = exact_largest_induced_tree(graph)
        witness = exact_witness
    tree_value = exact if exact is not None else tree_lower
    residual145 = None if local_min == 0 else tree_value * local_min - 2 * ecc_set
    residual146 = None if square_radius == 0 else tree_value * square_radius - 2 * ecc_set
    crossing145 = exact is not None and local_min > 0 and residual145 < 0
    crossing146 = exact is not None and square_radius > 0 and residual146 < 0
    inconclusive = needs_exact and exact is None
    return {
        "event": "graph_evaluated", "stage": stage, "name": name,
        "graph6": graph6(graph), "n": len(graph), "m": graph.number_of_edges(),
        "diameter": diameter, "radius": radius, "boundary": boundary,
        "ecc_set": ecc_set, "local_independence_min_complement": local_min,
        "square_radius": square_radius, "tree_lower": tree_lower,
        "tree_exact": exact, "tree_witness": sorted(witness),
        "subsets_checked": checked, "residual145": residual145,
        "residual146": residual146, "crossing145": crossing145,
        "crossing146": crossing146, "inconclusive": inconclusive,
        "seconds": round(time.monotonic() - started, 6),
    }


def named_controls() -> list[tuple[str, nx.Graph]]:
    rows = [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    rows += [("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()),
             ("K3,3", nx.complete_bipartite_graph(3, 3)), ("K7", nx.complete_graph(7))]
    rows += [(f"K1,{n}", nx.star_graph(n)) for n in range(2, 8)]
    rows += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b)) for a in range(2, 5) for b in range(a, 7)]
    rows += [(f"C5[K{m}]", cycle_clique_blowup((m,) * 5)) for m in range(1, 5)]
    return rows


def run_gate() -> None:
    rows = []
    for index, graph in enumerate(nx.graph_atlas_g()):
        if len(graph) > 1 and nx.is_connected(graph):
            rows.append(evaluate(graph, f"atlas:{index}", "gate", force_exact=True))
    for name, graph in named_controls():
        rows.append(evaluate(graph, name, "gate", force_exact=len(graph) <= 12))
    for row in rows:
        append(row)
    append({"event": "gate_summary", "graphs": len(rows),
            "atlas_graphs": sum(row["name"].startswith("atlas:") for row in rows),
            "crossings145": sum(row["crossing145"] for row in rows),
            "crossings146": sum(row["crossing146"] for row in rows),
            "inconclusive": sum(row["inconclusive"] for row in rows)})


def trial_graphs():
    yielded: set[str] = set()

    def emit(name: str, graph: nx.Graph):
        if len(graph) > 30:
            return None
        code = graph6(graph)
        if code in yielded:
            return None
        yielded.add(code)
        return name, graph

    unequal = 0
    for sizes in itertools.product(range(1, 7), repeat=5):
        if len(set(sizes)) == 1 or sum(sizes) > 22:
            continue
        canonical = min(tuple(sizes[i:] + sizes[:i]) for i in range(5))
        reverse = tuple(reversed(sizes))
        canonical = min(canonical, min(tuple(reverse[i:] + reverse[:i]) for i in range(5)))
        if sizes != canonical:
            continue
        row = emit(f"unequal:{','.join(map(str, sizes))}", cycle_clique_blowup(sizes))
        if row:
            yield row
            unequal += 1
        if unequal >= 800:
            break

    base = cycle_clique_blowup((4,) * 5)
    for length in range(1, 9):
        row = emit(f"carrier:tail:{length}", attach_tail(base, 0, length))
        if row:
            yield row
    for relation, attachment in (("same", 1), ("adjacent", 4), ("distance2", 8)):
        for left in range(1, 7):
            for right in range(1, 7):
                graph = attach_tail(base, 0, left)
                graph = attach_tail(graph, attachment, right)
                row = emit(f"carrier:two_tails:{relation}:{left}:{right}", graph)
                if row:
                    yield row

    for size in range(2, 7):
        row = emit(f"carrier:pendant_clique:{size}", attach_pendant_clique(base, 0, size))
        if row:
            yield row
        for tail in range(1, 5):
            graph = attach_tail(base, 0, tail)
            graph = attach_pendant_clique(graph, graph.number_of_nodes() - 1, size)
            row = emit(f"carrier:tail_block:{tail}:{size}", graph)
            if row:
                yield row
    for left in range(2, 7):
        for right in range(2, 7):
            graph = attach_pendant_clique(base, 0, left)
            graph = attach_pendant_clique(graph, 8, right)
            row = emit(f"carrier:two_blocks:{left}:{right}", graph)
            if row:
                yield row

    for m in range(2, 6):
        for portals in (1, 2):
            for tail in range(0, 7):
                row = emit(f"portal:m{m}:p{portals}:t{tail}", portal_surgery(m, portals, tail))
                if row:
                    yield row


def run_discovery() -> None:
    count = crossings = inconclusive = 0
    best145: list[tuple[int, str]] = []
    best146: list[tuple[int, str]] = []
    for name, graph in trial_graphs():
        if count >= 4000:
            break
        row = evaluate(graph, name, "discovery")
        append(row)
        count += 1
        crossings += int(row["crossing145"] or row["crossing146"])
        inconclusive += int(row["inconclusive"])
        if row["residual145"] is not None:
            best145.append((row["residual145"], name))
        if row["residual146"] is not None:
            best146.append((row["residual146"], name))
    append({"event": "discovery_summary", "graphs": count, "crossing_graphs": crossings,
            "inconclusive": inconclusive, "smallest_certified_lower_residual145": sorted(best145)[:20],
            "smallest_certified_lower_residual146": sorted(best146)[:20]})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("gate", "discovery"))
    args = parser.parse_args()
    if args.stage == "gate":
        run_gate()
    else:
        run_discovery()


if __name__ == "__main__":
    main()
