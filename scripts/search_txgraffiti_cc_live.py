#!/usr/bin/env python3
"""Frozen three-arm live search for the TxGraffiti i(G) <= mu*(G) wall."""

from __future__ import annotations

import argparse
import itertools
import math
import os
from pathlib import Path
import random
import time

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix

import method_v15_live_search_runtime as live


SEED = 0xCC20260814
INTERNAL_STOP_SECONDS = 54.0
SOLVER_CAP_SECONDS = 8.0


def normalized_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def relabel(graph: nx.Graph) -> nx.Graph:
    return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def applicable(graph: nx.Graph) -> bool:
    if graph.is_directed() or graph.is_multigraph() or graph.number_of_nodes() == 0:
        return False
    if not nx.is_connected(graph):
        return False
    degrees = {degree for _, degree in graph.degree()}
    return len(degrees) == 1 and next(iter(degrees)) >= 3


def solve_binary(
    objective: np.ndarray,
    rows: list[np.ndarray],
    lower: list[float],
    upper: list[float],
) -> tuple[int, np.ndarray]:
    size = len(objective)
    constraints = LinearConstraint(
        csr_matrix(np.vstack(rows)), np.asarray(lower), np.asarray(upper)
    )
    result = milp(
        objective,
        integrality=np.ones(size),
        bounds=Bounds(np.zeros(size), np.ones(size)),
        constraints=constraints,
        options={"time_limit": SOLVER_CAP_SECONDS, "presolve": True},
    )
    if result.status != 0 or result.fun is None or result.x is None:
        raise RuntimeError(f"binary ILP did not prove optimality: {result.message}")
    value = int(round(float(result.fun)))
    if abs(float(result.fun) - value) > 1e-7:
        raise RuntimeError("binary ILP returned a nonintegral optimum")
    return value, result.x


def independent_domination(graph: nx.Graph) -> tuple[int, tuple[int, ...]]:
    graph = relabel(graph)
    n = graph.number_of_nodes()
    rows: list[np.ndarray] = []
    lower: list[float] = []
    upper: list[float] = []
    for u, v in graph.edges():
        row = np.zeros(n)
        row[u] = row[v] = 1
        rows.append(row)
        lower.append(-np.inf)
        upper.append(1)
    for vertex in graph:
        row = np.zeros(n)
        row[vertex] = 1
        for neighbor in graph.neighbors(vertex):
            row[neighbor] = 1
        rows.append(row)
        lower.append(1)
        upper.append(np.inf)
    value, solution = solve_binary(np.ones(n), rows, lower, upper)
    witness = tuple(index for index, chosen in enumerate(solution) if chosen > 0.5)
    if len(witness) != value:
        raise RuntimeError("independent-domination witness has the wrong size")
    return value, witness


def minimum_maximal_matching(
    graph: nx.Graph,
) -> tuple[int, tuple[tuple[int, int], ...]]:
    graph = relabel(graph)
    edges = sorted(normalized_edge(u, v) for u, v in graph.edges())
    edge_index = {edge: index for index, edge in enumerate(edges)}
    rows: list[np.ndarray] = []
    lower: list[float] = []
    upper: list[float] = []
    for vertex in graph:
        row = np.zeros(len(edges))
        for edge in graph.edges(vertex):
            row[edge_index[normalized_edge(*edge)]] = 1
        rows.append(row)
        lower.append(-np.inf)
        upper.append(1)
    for u, v in edges:
        row = np.zeros(len(edges))
        for index, (a, b) in enumerate(edges):
            if {u, v} & {a, b}:
                row[index] = 1
        rows.append(row)
        lower.append(1)
        upper.append(np.inf)
    value, solution = solve_binary(np.ones(len(edges)), rows, lower, upper)
    witness = tuple(edges[index] for index, chosen in enumerate(solution) if chosen > 0.5)
    if len(witness) != value:
        raise RuntimeError("minimum-maximal-matching witness has the wrong size")
    return value, witness


def exact_profile(graph: nx.Graph) -> dict[str, object]:
    graph = relabel(graph)
    independent, independent_witness = independent_domination(graph)
    matching, matching_witness = minimum_maximal_matching(graph)
    residual = matching - independent
    payload: dict[str, object] = {
        "objective": residual,
        "crossing": residual < 0,
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "degree": next(iter(dict(graph.degree()).values())),
        "independent_domination": independent,
        "minimum_maximal_matching": matching,
        "independent_dominating_witness": list(independent_witness),
        "maximal_matching_witness": [list(edge) for edge in matching_witness],
        "origin": str(graph.graph.get("origin", "unspecified")),
    }
    if residual < 0:
        replay_i = brute_independent_domination(graph)
        replay_mu = brute_minimum_maximal_matching(graph)
        payload["independent_replay"] = {"i": replay_i, "mu_star": replay_mu}
        if (replay_i, replay_mu) != (independent, matching):
            raise RuntimeError("negative residual failed independent replay")
    return payload


def independent_and_dominating(graph: nx.Graph, vertices: tuple[int, ...]) -> bool:
    chosen = set(vertices)
    if any(u in chosen and v in chosen for u, v in graph.edges()):
        return False
    dominated = set(chosen)
    for vertex in chosen:
        dominated.update(graph.neighbors(vertex))
    return len(dominated) == graph.number_of_nodes()


def brute_independent_domination(graph: nx.Graph) -> int:
    nodes = tuple(graph.nodes())
    for size in range(1, len(nodes) + 1):
        if any(independent_and_dominating(graph, choice) for choice in itertools.combinations(nodes, size)):
            return size
    raise RuntimeError("finite graph has no independent dominating set")


def brute_minimum_maximal_matching(graph: nx.Graph) -> int:
    nodes = tuple(graph.nodes())
    n = len(nodes)
    for unmatched_size in range(n, -1, -1):
        if (n - unmatched_size) % 2:
            continue
        for unmatched_tuple in itertools.combinations(nodes, unmatched_size):
            unmatched = set(unmatched_tuple)
            if any(u in unmatched and v in unmatched for u, v in graph.edges()):
                continue
            remaining = [vertex for vertex in nodes if vertex not in unmatched]
            matching = nx.max_weight_matching(graph.subgraph(remaining), maxcardinality=True)
            if 2 * len(matching) == len(remaining):
                return len(matching)
    raise RuntimeError("finite graph has no maximal matching")


def all_independent_dominating_sets(graph: nx.Graph, size: int) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(choice)
        for choice in itertools.combinations(graph.nodes(), size)
        if independent_and_dominating(graph, choice)
    )


def c5_clique_blowup(width: int) -> nx.Graph:
    graph = nx.Graph()
    for blob in range(5):
        vertices = [blob * width + offset for offset in range(width)]
        graph.add_edges_from(itertools.combinations(vertices, 2))
        next_vertices = [((blob + 1) % 5) * width + offset for offset in range(width)]
        graph.add_edges_from(itertools.product(vertices, next_vertices))
    graph.graph["origin"] = f"C5[K{width}]"
    return graph


def named_graphs() -> list[nx.Graph]:
    rows: list[nx.Graph] = []

    def add(graph: nx.Graph, name: str) -> None:
        graph = relabel(graph)
        graph.graph["origin"] = name
        if graph.number_of_nodes() <= 24:
            rows.append(graph)

    for n in range(4, 11):
        add(nx.complete_graph(n), f"K{n}")
    for n in range(3, 9):
        add(nx.complete_bipartite_graph(n, n), f"K{n},{n}")
    for name, constructor in (
        ("Petersen", nx.petersen_graph),
        ("Heawood", nx.heawood_graph),
        ("Moebius-Kantor", nx.moebius_kantor_graph),
        ("Pappus", nx.pappus_graph),
        ("Desargues", nx.desargues_graph),
        ("dodecahedral", nx.dodecahedral_graph),
        ("Frucht", nx.frucht_graph),
    ):
        add(constructor(), name)
    for n in range(3, 11):
        add(nx.circular_ladder_graph(n), f"circular_ladder_{n}")
    for width in range(2, 6):
        add(c5_clique_blowup(width), f"C5[K{width}]")
    add(nx.complement(c5_clique_blowup(4)), "complement_C5[K4]")
    return rows


def atlas_graphs() -> list[nx.Graph]:
    rows: list[nx.Graph] = []
    for index, graph in enumerate(nx.graph_atlas_g()):
        graph = relabel(graph)
        graph.graph["origin"] = f"atlas_{index}"
        if applicable(graph):
            rows.append(graph)
    return rows


def database_gate(ledger: live.ScientificJsonl) -> None:
    rows = atlas_graphs()
    controls = [
        (nx.complete_graph(4), (1, 2)),
        (nx.complete_bipartite_graph(3, 3), (3, 3)),
        (nx.petersen_graph(), (3, 3)),
    ]
    for graph in rows:
        profile = exact_profile(graph)
        if int(profile["objective"]) < 0:
            raise RuntimeError("database-sanity gate found an Atlas violation")
    for graph, expected in controls:
        profile = exact_profile(graph)
        observed = (
            int(profile["independent_domination"]),
            int(profile["minimum_maximal_matching"]),
        )
        if observed != expected:
            raise RuntimeError(f"named gate mismatch: {observed} != {expected}")
    ledger.checkpoint(f"database_sanity_gate_passed:{len(rows)}_atlas_rows")


def evaluate_rows(
    recorder: live.GraphSearchRecorder,
    rows: list[nx.Graph],
    deadline: float,
) -> None:
    for graph in rows:
        if time.monotonic() >= deadline:
            break
        recorder.evaluate(graph, applicable, exact_profile)


def run_catalogue(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    evaluate_rows(recorder, atlas_graphs() + named_graphs(), deadline)


def run_generic(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    rng = random.Random(SEED)
    valid_coordinates = [
        (n, degree)
        for n in range(8, 21)
        for degree in range(3, min(8, n - 1) + 1)
        if n * degree % 2 == 0
    ]
    while time.monotonic() < deadline:
        n, degree = rng.choice(valid_coordinates)
        try:
            graph = nx.random_regular_graph(degree, n, seed=rng.randrange(2**63))
        except nx.NetworkXError:
            continue
        graph.graph["origin"] = f"generic_n{n}_r{degree}"
        recorder.evaluate(graph, applicable, exact_profile)


def wall_seeds() -> list[nx.Graph]:
    rows = [
        nx.complement(c5_clique_blowup(4)),
        nx.petersen_graph(),
        nx.complete_bipartite_graph(3, 3),
    ]
    rows.extend(nx.circular_ladder_graph(n) for n in (3, 5, 6, 9))
    names = ["complement_C5[K4]", "Petersen", "K3,3", "CL3", "CL5", "CL6", "CL9"]
    for graph, name in zip(rows, names):
        graph.graph["origin"] = f"wall_seed_{name}"
    return [relabel(graph) for graph in rows]


def switch_candidates(
    graph: nx.Graph,
    matching: tuple[tuple[int, int], ...],
    minimum_sets: tuple[frozenset[int], ...],
) -> list[tuple[int, nx.Graph]]:
    matching_edges = {normalized_edge(*edge) for edge in matching}
    matched_vertices = {vertex for edge in matching_edges for vertex in edge}
    unmatched = set(graph) - matched_vertices
    candidates: list[tuple[int, nx.Graph]] = []
    edges = sorted(normalized_edge(u, v) for u, v in graph.edges())
    for first, second in itertools.combinations(edges, 2):
        if first in matching_edges or second in matching_edges:
            continue
        a, b = first
        c, d = second
        if len({a, b, c, d}) != 4:
            continue
        for added in (((a, c), (b, d)), ((a, d), (b, c))):
            added = tuple(normalized_edge(*edge) for edge in added)
            if added[0] == added[1] or any(graph.has_edge(*edge) for edge in added):
                continue
            if any(set(edge) <= unmatched for edge in added):
                continue
            child = graph.copy()
            child.remove_edges_from((first, second))
            child.add_edges_from(added)
            if not nx.is_connected(child):
                continue
            killed = sum(not independent_and_dominating(child, tuple(row)) for row in minimum_sets)
            child.graph["origin"] = (
                f"targeted_switch_killed_{killed}_of_{len(minimum_sets)}"
            )
            candidates.append((killed, child))
    candidates.sort(key=lambda row: row[0], reverse=True)
    return candidates[:80]


def run_wall(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    queue: list[tuple[nx.Graph, int]] = [(seed, 0) for seed in wall_seeds()]
    expanded = 0
    while queue and time.monotonic() < deadline and expanded < 24:
        graph, depth = queue.pop(0)
        profile = exact_profile(graph)
        row = recorder.evaluate(graph, applicable, lambda _: profile)
        if row is None or int(profile["objective"]) != 0 or depth > 2:
            continue
        matching = tuple(tuple(edge) for edge in profile["maximal_matching_witness"])
        minimum_sets = all_independent_dominating_sets(
            graph, int(profile["independent_domination"])
        )
        if not minimum_sets:
            raise RuntimeError("equality state has no minimum independent dominating set")
        expanded += 1
        for _, child in switch_candidates(graph, matching, minimum_sets):
            if time.monotonic() >= deadline:
                break
            child_profile = exact_profile(child)
            child_row = recorder.evaluate(child, applicable, lambda _: child_profile)
            if child_row is not None and int(child_profile["objective"]) == 0 and depth < 2:
                queue.append((child, depth + 1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=live.ARMS, required=True)
    args = parser.parse_args()
    ledger = live.ScientificJsonl.from_environment()
    if args.arm != ledger.arm:
        raise RuntimeError("CLI arm differs from the frozen runtime identity")
    canonicalizer = live.LabelgCanonicalizer.from_environment()
    recorder = live.GraphSearchRecorder(ledger, canonicalizer)
    database_gate(ledger)
    deadline = ledger.started + INTERNAL_STOP_SECONDS
    if args.arm == "CATALOGUE":
        run_catalogue(recorder, deadline)
    elif args.arm == "GENERIC":
        run_generic(recorder, deadline)
    else:
        run_wall(recorder, deadline)
    ledger.finish()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
