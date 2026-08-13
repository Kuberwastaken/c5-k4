#!/usr/bin/env python3
"""Frozen prospective WOWII 291 construction sweep; prints JSONL only."""

import argparse
import json
import random

import networkx as nx
import pulp


def clique_block_graph(sizes, cycle=False, rotate=False):
    graph = nx.Graph()
    blocks = []
    next_vertex = 0
    for size in sizes:
        block = list(range(next_vertex, next_vertex + size))
        next_vertex += size
        graph.add_edges_from((u, v) for i, u in enumerate(block) for v in block[i + 1 :])
        blocks.append(block)
    edge_count = len(blocks) if cycle else len(blocks) - 1
    for i in range(edge_count):
        j = (i + 1) % len(blocks)
        left = blocks[i][i % len(blocks[i])] if rotate else blocks[i][0]
        right = blocks[j][i % len(blocks[j])] if rotate else blocks[j][0]
        graph.add_edge(left, right)
    return graph


def hh_step(sequence):
    if not sequence:
        return []
    degree, *rest = sequence
    return sorted([max(0, x - 1) for x in rest[:degree]] + rest[degree:], reverse=True)


def zero_step(graph):
    sequence = sorted((degree for _, degree in graph.degree()), reverse=True)
    trace = [sequence]
    step = 0
    while sequence and 0 not in sequence:
        sequence = hh_step(sequence)
        step += 1
        trace.append(sequence)
    return step, trace


def total_domination_ilp(graph):
    problem = pulp.LpProblem("total_domination", pulp.LpMinimize)
    variables = {v: pulp.LpVariable(f"x_{v}", cat="Binary") for v in graph}
    problem += pulp.lpSum(variables.values())
    for v in graph:
        problem += pulp.lpSum(variables[u] for u in graph.neighbors(v)) >= 1
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=60)
    status = problem.solve(solver)
    if pulp.LpStatus[status] != "Optimal":
        return None, pulp.LpStatus[status], []
    witness = sorted(v for v in graph if pulp.value(variables[v]) > 0.5)
    return len(witness), "Optimal", witness


def is_total_dominating(graph, vertices):
    chosen = set(vertices)
    return all(any(neighbor in chosen for neighbor in graph.neighbors(v)) for v in graph)


def total_domination_upper_bound(graph, target):
    """Fast discard certificate: return a total dominating set of size <= target."""
    orders = [
        sorted(graph, key=lambda v: (graph.degree(v), v)),
        sorted(graph, key=lambda v: (-graph.degree(v), v)),
        list(graph),
    ]
    for order in orders:
        chosen = set(graph)
        for vertex in order:
            trial = chosen - {vertex}
            if is_total_dominating(graph, trial):
                chosen = trial
        if len(chosen) <= target:
            return sorted(chosen)
    return None


def evaluate(name, graph, meta):
    if len(graph) <= 2 or not nx.is_connected(graph):
        return None
    triangle_values = nx.triangles(graph)
    minimum = min(triangle_values.values())
    frequency = sum(value == minimum for value in triangle_values.values())
    k_zero, trace = zero_step(graph)
    rhs = k_zero + frequency
    discard_witness = total_domination_upper_bound(graph, rhs)
    if discard_witness is not None:
        gamma, status, witness = len(discard_witness), "UpperBoundHolds", discard_witness
    elif rhs >= len(graph):
        gamma, status, witness = len(graph), "TrivialUpperBoundHolds", list(graph)
    else:
        gamma, status, witness = total_domination_ilp(graph)
    result = {
        "name": name,
        "meta": meta,
        "n": len(graph),
        "m": graph.number_of_edges(),
        "degree_sequence": sorted((d for _, d in graph.degree()), reverse=True),
        "triangle_min": minimum,
        "triangle_min_frequency": frequency,
        "k_zero": k_zero,
        "rhs": rhs,
        "gamma_t": gamma,
        "ilp_status": status,
        "witness": witness,
        "hh_trace": trace,
    }
    result["slack"] = None if gamma is None else result["rhs"] - gamma
    result["exact_gamma"] = status == "Optimal"
    return result


def lane_one():
    seen = set()
    for blocks in range(2, 9):
        patterns = [
            tuple(range(3, 3 + blocks)),
            tuple(reversed(range(3, 3 + blocks))),
            tuple(3 + (i % 2) * min(4, blocks) for i in range(blocks)),
            tuple([3] + [min(9, 4 + i) for i in range(blocks - 1)]),
        ]
        for sizes in patterns:
            if max(sizes) > 9 or sizes in seen:
                continue
            seen.add(sizes)
            yield f"block_path_{'-'.join(map(str, sizes))}", clique_block_graph(sizes), {
                "lane": 1,
                "sizes": sizes,
            }


def lane_two():
    for blocks in range(3, 9):
        for size in range(3, 7):
            if blocks * size > 42:
                continue
            sizes = (size,) * blocks
            for cycle in (False, True):
                yield f"regular_{'cycle' if cycle else 'path'}_{blocks}x{size}", clique_block_graph(
                    sizes, cycle=cycle, rotate=True
                ), {"lane": 2, "blocks": blocks, "size": size, "cycle": cycle}


def switches(graph, limit, rng):
    edges = sorted(tuple(sorted(edge)) for edge in graph.edges())
    candidates = []
    for index, (a, b) in enumerate(edges):
        for c, d in edges[index + 1 :]:
            if len({a, b, c, d}) < 4:
                continue
            for new_edges in (((a, c), (b, d)), ((a, d), (b, c))):
                if any(graph.has_edge(*edge) for edge in new_edges):
                    continue
                candidates.append(((a, b), (c, d), new_edges))
    rng.shuffle(candidates)
    for old_one, old_two, new_edges in candidates[:limit]:
        switched = graph.copy()
        switched.remove_edges_from((old_one, old_two))
        switched.add_edges_from(new_edges)
        if nx.is_connected(switched):
            yield switched, (old_one, old_two, new_edges)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", choices=("base", "surgery"), default="base")
    parser.add_argument("--surgery-limit", type=int, default=2000)
    args = parser.parse_args()
    results = []
    bases = list(lane_one()) + list(lane_two())
    if args.lane == "base":
        inputs = bases
    else:
        rng = random.Random(29120260813)
        inputs = []
        remaining = 20000
        for name, graph, meta in bases:
            if len(graph) > 36 or remaining <= 0:
                continue
            per_seed = min(args.surgery_limit, remaining)
            for index, (switched, surgery) in enumerate(switches(graph, per_seed, rng)):
                inputs.append((f"{name}_switch_{index}", switched, {
                    **meta,
                    "lane": 3,
                    "parent": name,
                    "surgery": surgery,
                }))
                remaining -= 1
    for name, graph, meta in inputs:
        result = evaluate(name, graph, meta)
        if result is not None and (result["slack"] is None or
            (result["exact_gamma"] and result["slack"] <= 2)):
            results.append(result)
    results.sort(key=lambda item: (999 if item["slack"] is None else item["slack"], item["n"]))
    print(json.dumps({"summary": {"evaluated": len(inputs), "retained": len(results)}}))
    for result in results:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
