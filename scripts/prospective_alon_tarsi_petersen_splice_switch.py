#!/usr/bin/env python3
"""Frozen Alon--Tarsi Petersen-splice switch trial.

The search grammar is fixed in the accompanying contract.  This script appends
one JSON line after the gate and after each retained candidate.
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_alon_tarsi_petersen_splice_switch_ledger.jsonl"


def emit(record: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def canonical_cycles(graph: nx.Graph) -> list[frozenset[tuple[int, int]]]:
    found: dict[frozenset[tuple[int, int]], None] = {}
    for vertices in nx.simple_cycles(graph):
        if len(vertices) < 3:
            continue
        cycle = frozenset(
            edge(vertices[i], vertices[(i + 1) % len(vertices)])
            for i in range(len(vertices))
        )
        found[cycle] = None
    return sorted(found, key=lambda c: (len(c), sorted(c)))


def minimum_cycle_cover_milp(graph: nx.Graph) -> tuple[int, int, str]:
    edges = sorted(edge(u, v) for u, v in graph.edges())
    cycles = canonical_cycles(graph)
    if edges and not cycles:
        raise RuntimeError("nonempty graph has no cycles")
    incidence = -np.asarray(
        [[int(e in cycle) for cycle in cycles] for e in edges], dtype=float
    )
    result = milp(
        np.asarray([len(cycle) for cycle in cycles], dtype=float),
        integrality=np.ones(len(cycles)),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(incidence, -np.inf, -1),
        options={"time_limit": 10.0},
    )
    if result.status != 0 or result.fun is None:
        raise RuntimeError(f"HiGHS did not prove optimality: {result.message}")
    return int(round(result.fun)), len(cycles), result.message


def minimum_cycle_cover_dp(graph: nx.Graph) -> int:
    edges = sorted(edge(u, v) for u, v in graph.edges())
    if len(edges) > 20:
        raise ValueError("edge-mask oracle intentionally capped at 20 edges")
    edge_index = {e: i for i, e in enumerate(edges)}
    cycles = canonical_cycles(graph)
    masks = [sum(1 << edge_index[e] for e in cycle) for cycle in cycles]
    weights = [len(cycle) for cycle in cycles]
    infinity = 10**9
    values = [infinity] * (1 << len(edges))
    values[0] = 0
    for mask in range(len(values)):
        old = values[mask]
        if old == infinity:
            continue
        for cycle_mask, weight in zip(masks, weights):
            new_mask = mask | cycle_mask
            candidate = old + weight
            if candidate < values[new_mask]:
                values[new_mask] = candidate
    return values[-1]


def independent_branch_and_bound(graph: nx.Graph) -> int:
    edges = sorted(edge(u, v) for u, v in graph.edges())
    edge_index = {e: i for i, e in enumerate(edges)}
    cycles = canonical_cycles(graph)
    encoded = [
        (sum(1 << edge_index[e] for e in cycle), len(cycle)) for cycle in cycles
    ]
    by_edge: list[list[tuple[int, int]]] = [[] for _ in edges]
    for item in encoded:
        mask, _ = item
        for i in range(len(edges)):
            if mask & (1 << i):
                by_edge[i].append(item)
    full = (1 << len(edges)) - 1
    best = [10**9]
    seen: dict[int, int] = {}

    def search(mask: int, cost: int) -> None:
        if cost >= best[0] or seen.get(mask, 10**9) <= cost:
            return
        seen[mask] = cost
        if mask == full:
            best[0] = cost
            return
        uncovered = [i for i in range(len(edges)) if not mask & (1 << i)]
        pivot = min(uncovered, key=lambda i: len(by_edge[i]))
        options = sorted(
            by_edge[pivot], key=lambda x: (-(x[0] & ~mask).bit_count() / x[1], x[1])
        )
        for cycle_mask, weight in options:
            search(mask | cycle_mask, cost + weight)

    search(0, 0)
    return best[0]


def petersen_splice() -> nx.Graph:
    first = nx.petersen_graph()
    second = nx.relabel_nodes(nx.petersen_graph(), lambda v: v + 10)
    graph = nx.compose(first, second)
    graph.remove_edges_from([(0, 1), (10, 11)])
    graph.add_edges_from([(0, 10), (1, 11)])
    return graph


def assert_premises(graph: nx.Graph) -> None:
    assert not graph.is_multigraph()
    assert nx.number_of_selfloops(graph) == 0
    assert nx.is_connected(graph)
    assert not list(nx.bridges(graph))


def gate() -> None:
    controls = [(nx.cycle_graph(n), n) for n in (3, 4, 5)]
    petersen = nx.petersen_graph()
    controls.append((petersen, 21))
    for graph, expected in controls:
        exact, _, _ = minimum_cycle_cover_milp(graph)
        oracle = minimum_cycle_cover_dp(graph)
        assert exact == expected == oracle

    carrier = petersen_splice()
    assert_premises(carrier)
    exact, cycle_count, _ = minimum_cycle_cover_milp(carrier)
    assert exact == 42

    atlas_checked = 0
    for graph in nx.graph_atlas_g():
        if not (2 <= graph.number_of_nodes() <= 6):
            continue
        if graph.number_of_edges() == 0 or not nx.is_connected(graph):
            continue
        if list(nx.bridges(graph)):
            continue
        exact, _, _ = minimum_cycle_cover_milp(graph)
        oracle = minimum_cycle_cover_dp(graph)
        assert exact == oracle
        assert 5 * exact <= 7 * graph.number_of_edges()
        atlas_checked += 1
    emit(
        {
            "event": "database_gate_passed",
            "atlas_checked": atlas_checked,
            "petersen_tau": 21,
            "carrier_edges": carrier.number_of_edges(),
            "carrier_tau": exact if False else 42,
            "carrier_cycle_count": cycle_count,
            "independent_carrier_lower_bound": 42,
        }
    )


def candidates(carrier: nx.Graph):
    switched = edge(0, 10)
    internal = sorted(
        edge(u, v)
        for u, v in carrier.edges()
        if edge(u, v) not in {edge(0, 10), edge(1, 11)}
        and not ({u, v} & {0, 10})
    )
    for u, v in internal:
        new_edges = (edge(0, u), edge(10, v))
        if new_edges[0] == new_edges[1]:
            continue
        graph = carrier.copy()
        graph.remove_edges_from([switched, edge(u, v)])
        if any(graph.has_edge(*e) for e in new_edges):
            continue
        graph.add_edges_from(new_edges)
        if not nx.is_connected(graph) or list(nx.bridges(graph)):
            continue
        yield (u, v), new_edges, graph


def main() -> None:
    started = time.monotonic()
    gate()
    carrier = petersen_splice()
    retained = 0
    crossings = 0
    for old_edge, new_edges, graph in candidates(carrier):
        assert_premises(graph)
        exact, cycle_count, status = minimum_cycle_cover_milp(graph)
        residual = 5 * exact - 7 * graph.number_of_edges()
        record = {
            "event": "candidate",
            "id": f"switch_{old_edge[0]}_{old_edge[1]}",
            "deleted": [[0, 10], list(old_edge)],
            "added": [list(new_edges[0]), list(new_edges[1])],
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "bridgeless": True,
            "cycle_count": cycle_count,
            "tau": exact,
            "cleared_residual": residual,
            "solver": "scipy_highs_milp",
            "solver_status": status,
        }
        if residual > 0:
            oracle = independent_branch_and_bound(graph)
            record["independent_tau"] = oracle
            record["oracle_agrees"] = oracle == exact
            if oracle != exact:
                emit(record)
                raise RuntimeError("crossing oracle mismatch")
            crossings += 1
        emit(record)
        retained += 1
    emit(
        {
            "event": "trial_complete",
            "retained": retained,
            "crossings": crossings,
            "elapsed_seconds": round(time.monotonic() - started, 6),
        }
    )
    print(json.dumps({"retained": retained, "crossings": crossings}, sort_keys=True))


if __name__ == "__main__":
    main()
