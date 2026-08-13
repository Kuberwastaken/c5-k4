#!/usr/bin/env python3
"""Reproduce the frozen C5[K3] reuse catalogue and adjacent two-blocker."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose4

from method_v46_reed_weighted_surgery import (
    adjacency_masks,
    exact_profile,
    maximum_clique,
    normalized_graph,
    valid_profile,
    weighted_c5,
)


NX = (0, 1, 2, 3, 4, 5, 12, 13, 14)
NY = (6, 7, 8, 9, 10, 11, 12, 13, 14)
X, Y = 15, 16


def carrier_partitions() -> list[tuple[tuple[int, ...], ...]]:
    carrier, _ = weighted_c5((3,) * 5)
    complement = nx.complement(carrier)
    result: list[tuple[tuple[int, ...], ...]] = []

    def match(remaining: set[int], pairs: list[tuple[int, int]], singleton: int) -> None:
        if not remaining:
            result.append(tuple(tuple(sorted(pair)) for pair in pairs) + ((singleton,),))
            return
        left = min(remaining)
        for right in sorted(remaining - {left}):
            if complement.has_edge(left, right):
                match(remaining - {left, right}, pairs + [(left, right)], singleton)

    for singleton in carrier.nodes():
        match(set(carrier.nodes()) - {singleton}, [], singleton)
    return result


def clauses_for_budget(
    partitions: list[tuple[tuple[int, ...], ...]], delta_max: int, omega_max: int
) -> list[list[int]]:
    carrier, _ = weighted_c5((3,) * 5)
    ax = lambda vertex: vertex + 1
    ay = lambda vertex: 16 + vertex
    clauses: list[list[int]] = []
    for partition in partitions:
        for i, left_class in enumerate(partition):
            for j, right_class in enumerate(partition):
                if i != j:
                    clauses.append(
                        [ax(vertex) for vertex in left_class]
                        + [ay(vertex) for vertex in right_class]
                    )

    carrier_bound = delta_max - 8
    if carrier_bound == 1:
        clauses.extend([[-ax(vertex), -ay(vertex)] for vertex in carrier.nodes()])
    elif carrier_bound < 1:
        raise ValueError("unsupported maximum-degree budget")

    neighborhood_bound = delta_max - 1
    first_cardinality = CardEnc.atmost(
        [ax(vertex) for vertex in carrier.nodes()],
        bound=neighborhood_bound,
        top_id=30,
        encoding=EncType.seqcounter,
    )
    clauses.extend(first_cardinality.clauses)
    top_id = max(abs(literal) for clause in clauses for literal in clause)
    second_cardinality = CardEnc.atmost(
        [ay(vertex) for vertex in carrier.nodes()],
        bound=neighborhood_bound,
        top_id=top_id,
        encoding=EncType.seqcounter,
    )
    clauses.extend(second_cardinality.clauses)

    six_cliques = [tuple(clique) for clique in nx.find_cliques(carrier) if len(clique) == 6]
    if omega_max == 6:
        five_cliques = {
            tuple(sorted(subset))
            for clique in six_cliques
            for subset in itertools.combinations(clique, 5)
        }
        for clique in six_cliques:
            clauses.append([-ax(vertex) for vertex in clique])
            clauses.append([-ay(vertex) for vertex in clique])
        for clique in five_cliques:
            clauses.append(
                list(itertools.chain.from_iterable((-ax(vertex), -ay(vertex)) for vertex in clique))
            )
    elif omega_max == 7:
        for clique in six_cliques:
            clauses.append(
                list(itertools.chain.from_iterable((-ax(vertex), -ay(vertex)) for vertex in clique))
            )
    else:
        raise ValueError("unsupported clique budget")
    return clauses


def solve_budget(
    partitions: list[tuple[tuple[int, ...], ...]], delta_max: int, omega_max: int
) -> dict:
    clauses = clauses_for_budget(partitions, delta_max, omega_max)
    with Glucose4(bootstrap_with=clauses) as solver:
        satisfiable = solver.solve()
        model = set(solver.get_model() or [])
    return {
        "Delta_max": delta_max,
        "omega_max": omega_max,
        "clauses": len(clauses),
        "satisfiable": satisfiable,
        "N15": [vertex for vertex in range(15) if vertex + 1 in model] if satisfiable else None,
        "N16": [vertex for vertex in range(15) if 16 + vertex in model] if satisfiable else None,
    }


def catalogue() -> dict:
    partitions = carrier_partitions()
    singleton_counts = {
        str(vertex): sum(partition[-1] == (vertex,) for partition in partitions)
        for vertex in range(15)
    }
    budgets = [
        solve_budget(partitions, 9, 6),
        solve_budget(partitions, 10, 6),
        solve_budget(partitions, 10, 7),
    ]
    expected = [list(NX), list(NY)]
    actual = [budgets[-1]["N15"], budgets[-1]["N16"]]
    if actual != expected:
        raise RuntimeError(f"deterministic first model changed: {actual} != {expected}")
    return {
        "mode": "catalogue",
        "partitions": len(partitions),
        "shape": [2, 2, 2, 2, 2, 2, 2, 1],
        "singleton_counts": singleton_counts,
        "budgets": budgets,
    }


def frozen_graph() -> nx.Graph:
    graph, _ = weighted_c5((3,) * 5)
    graph.add_nodes_from((X, Y))
    graph.add_edge(X, Y)
    graph.add_edges_from((X, vertex) for vertex in NX)
    graph.add_edges_from((Y, vertex) for vertex in NY)
    return normalized_graph(graph)


def digest(graph: nx.Graph) -> str:
    return hashlib.sha256(nx.to_graph6_bytes(graph, header=False).strip()).hexdigest()


def induced_claw(graph: nx.Graph) -> list[int] | None:
    for center in graph.nodes():
        for leaves in itertools.combinations(graph.neighbors(center), 3):
            if all(not graph.has_edge(a, b) for a, b in itertools.combinations(leaves, 2)):
                return [center, *leaves]
    return None


def audit() -> dict:
    graph = frozen_graph()
    complement = nx.complement(graph)
    independent, states = maximum_clique(adjacency_masks(complement))
    alpha = len(independent)
    return {
        "mode": "audit",
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "graph6_sha256": digest(graph),
        "induced_claw": induced_claw(graph),
        "alpha": alpha,
        "independent_set": independent,
        "alpha_states": states,
        "complement_connected": nx.is_connected(complement),
        "Rabern_threshold": (graph.number_of_nodes() + 3 - alpha) / 2,
    }


def evaluate() -> dict:
    graph = frozen_graph()
    profile = exact_profile(graph)
    if not valid_profile(graph, profile):
        raise RuntimeError("invalid exact certificate")
    return {
        "mode": "evaluate",
        "graph6_sha256": digest(graph),
        "profile": profile.as_dict(),
        "induced_claw": induced_claw(graph),
        "crossing": profile.slack < 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("catalogue", "audit", "evaluate"))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = {"catalogue": catalogue, "audit": audit, "evaluate": evaluate}[args.mode]()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
