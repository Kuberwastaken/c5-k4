#!/usr/bin/env python3
"""Phase-one exact child-residual search for the TxGraffiti C-C wall."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import random
import time

import networkx as nx

import method_v15_live_search_runtime as live
import search_txgraffiti_cc_live as base


SEED = 0xCC20260815
INTERNAL_STOP_SECONDS = 54.0
MAX_WALL_CHILDREN_PER_STATE = 16
MAX_WALL_EXPANDED_STATES = 24
MAX_WALL_DEPTH = 3


def two_lift(graph: nx.Graph, mask: int) -> nx.Graph:
    """Return the signed two-lift selected by the bit mask on sorted edges."""
    graph = base.relabel(graph)
    lift = nx.Graph()
    lift.add_nodes_from(range(2 * graph.number_of_nodes()))
    for index, (u, v) in enumerate(sorted(base.normalized_edge(*e) for e in graph.edges())):
        crossed = (mask >> index) & 1
        for sheet in (0, 1):
            lift.add_edge(2 * u + sheet, 2 * v + (sheet ^ crossed))
    return lift


def lift_seeds() -> list[tuple[str, nx.Graph]]:
    return [
        ("K3,3", nx.complete_bipartite_graph(3, 3)),
        ("Petersen", nx.petersen_graph()),
        ("CL5", nx.circular_ladder_graph(5)),
        ("CL6", nx.circular_ladder_graph(6)),
    ]


def run_catalogue(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    seed = nx.complete_bipartite_graph(3, 3)
    edge_count = seed.number_of_edges()
    for mask in range(1 << edge_count):
        if time.monotonic() >= deadline:
            return
        graph = two_lift(seed, mask)
        graph.graph["origin"] = f"complete_two_lift_K3,3_mask_{mask}"
        recorder.evaluate(graph, base.applicable, base.exact_profile)


def run_generic(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    rng = random.Random(SEED)
    seeds = lift_seeds()
    while time.monotonic() < deadline:
        name, seed = rng.choice(seeds)
        mask = rng.randrange(1 << seed.number_of_edges())
        graph = two_lift(seed, mask)
        graph.graph["origin"] = f"random_two_lift_{name}_mask_{mask}"
        recorder.evaluate(graph, base.applicable, base.exact_profile)


def two_switch_pool(graph: nx.Graph) -> list[nx.Graph]:
    """Generate regular connected two-switch children without witness ranking."""
    graph = base.relabel(graph)
    children: list[nx.Graph] = []
    edges = sorted(base.normalized_edge(u, v) for u, v in graph.edges())
    for first, second in itertools.combinations(edges, 2):
        a, b = first
        c, d = second
        if len({a, b, c, d}) != 4:
            continue
        for added in (((a, c), (b, d)), ((a, d), (b, c))):
            added = tuple(base.normalized_edge(*edge) for edge in added)
            if added[0] == added[1] or any(graph.has_edge(*edge) for edge in added):
                continue
            child = graph.copy()
            child.remove_edges_from((first, second))
            child.add_edges_from(added)
            if nx.is_connected(child):
                children.append(child)
    material = nx.to_graph6_bytes(graph, header=False).strip()
    state_seed = SEED ^ int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    random.Random(state_seed).shuffle(children)
    return children[:MAX_WALL_CHILDREN_PER_STATE]


def run_wall(recorder: live.GraphSearchRecorder, deadline: float) -> None:
    seeds = [
        ("K3,3", nx.complete_bipartite_graph(3, 3)),
        ("Petersen", nx.petersen_graph()),
        ("CL5", nx.circular_ladder_graph(5)),
        ("CL6", nx.circular_ladder_graph(6)),
        ("CL9", nx.circular_ladder_graph(9)),
    ]
    queue: list[tuple[nx.Graph, int, int]] = []
    for name, graph in seeds:
        graph.graph["origin"] = f"phase1_wall_seed_{name}"
        profile = base.exact_profile(graph)
        row = recorder.evaluate(graph, base.applicable, lambda _: profile)
        if row is not None and int(profile["objective"]) == 0:
            queue.append((graph, 0, int(profile["independent_domination"])))

    expanded = 0
    while queue and time.monotonic() < deadline and expanded < MAX_WALL_EXPANDED_STATES:
        graph, depth, parent_i = queue.pop(0)
        if depth >= MAX_WALL_DEPTH:
            continue
        expanded += 1
        survivors: list[tuple[nx.Graph, int]] = []
        for child in two_switch_pool(graph):
            if time.monotonic() >= deadline:
                return
            child.graph["origin"] = (
                f"exact_residual_switch_depth_{depth + 1}_parent_i_{parent_i}"
            )
            row = recorder.evaluate(child, base.applicable, base.exact_profile)
            if row is None:
                continue
            objective = int(row["objective"])
            child_i = int(row["payload"]["independent_domination"])
            if objective < 0:
                recorder.ledger.checkpoint("crossing_found_independent_replay_passed")
                return
            if objective == 0 and child_i >= parent_i:
                survivors.append((child, child_i))
        survivors.sort(key=lambda item: item[1], reverse=True)
        queue.extend((child, depth + 1, child_i) for child, child_i in survivors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=live.ARMS, required=True)
    args = parser.parse_args()
    ledger = live.ScientificJsonl.from_environment()
    if args.arm != ledger.arm:
        raise RuntimeError("CLI arm differs from the frozen runtime identity")
    recorder = live.GraphSearchRecorder(ledger, live.LabelgCanonicalizer.from_environment())
    base.database_gate(ledger)
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
