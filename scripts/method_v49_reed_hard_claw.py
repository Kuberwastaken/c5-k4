#!/usr/bin/env python3
"""Frozen hard-claw blocker selection and gated evaluation for Reed's bound."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Glucose4

from method_v46_reed_weighted_surgery import exact_profile, normalized_graph, valid_profile, weighted_c5
from method_v48_reed_two_blocker import carrier_partitions


def variable(new_vertex: int, carrier_vertex: int) -> int:
    return 15 * new_vertex + carrier_vertex + 1


def internal_edges(k: int, mask: int) -> list[tuple[int, int]]:
    pairs = list(itertools.combinations(range(k), 2))
    return [edge for bit, edge in enumerate(pairs) if (mask >> bit) & 1]


def carrier_cliques(size: int) -> list[tuple[int, ...]]:
    carrier, _ = weighted_c5((3,) * 5)
    return [
        subset
        for subset in itertools.combinations(range(15), size)
        if all(carrier.has_edge(a, b) for a, b in itertools.combinations(subset, 2))
    ]


def select(k: int, degree_increment: int, clique_increment: int, mask: int) -> dict:
    if not 1 <= k <= 3:
        raise ValueError("k outside frozen range")
    edges = internal_edges(k, mask)
    edge_set = set(edges)
    partitions = carrier_partitions()
    clause_count = 0
    top_id = 15 * k
    with Glucose4() as solver:
        for partition in partitions:
            for assignment in itertools.product(range(8), repeat=k):
                if any(assignment[a] == assignment[b] for a, b in edges):
                    continue
                solver.add_clause(
                    [
                        variable(i, vertex)
                        for i, color in enumerate(assignment)
                        for vertex in partition[color]
                    ]
                )
                clause_count += 1

        for clause in ([variable(0, 0)], [-variable(0, 5)], [-variable(0, 14)]):
            solver.add_clause(clause)
            clause_count += 1

        for vertex in range(15):
            encoding = CardEnc.atmost(
                [variable(i, vertex) for i in range(k)],
                bound=degree_increment,
                top_id=top_id,
                encoding=EncType.seqcounter,
            )
            top_id = encoding.nv
            for clause in encoding.clauses:
                solver.add_clause(clause)
            clause_count += len(encoding.clauses)

        for i in range(k):
            new_internal_degree = sum(i in edge for edge in edges)
            bound = 8 + degree_increment - new_internal_degree
            if bound < 0:
                return {"satisfiable": False, "reason": "negative new-vertex degree bound"}
            encoding = CardEnc.atmost(
                [variable(i, vertex) for vertex in range(15)],
                bound=bound,
                top_id=top_id,
                encoding=EncType.seqcounter,
            )
            top_id = encoding.nv
            for clause in encoding.clauses:
                solver.add_clause(clause)
            clause_count += len(encoding.clauses)

        for new_size in range(1, k + 1):
            for new_clique in itertools.combinations(range(k), new_size):
                if any(tuple(sorted(edge)) not in edge_set for edge in itertools.combinations(new_clique, 2)):
                    continue
                forbidden_carrier_size = 6 + clique_increment - new_size + 1
                if forbidden_carrier_size <= 0:
                    return {"satisfiable": False, "reason": "internal clique exceeds budget"}
                if forbidden_carrier_size <= 6:
                    for clique in carrier_cliques(forbidden_carrier_size):
                        solver.add_clause(
                            [
                                -variable(i, vertex)
                                for i in new_clique
                                for vertex in clique
                            ]
                        )
                        clause_count += 1

        satisfiable = solver.solve()
        model = set(solver.get_model() or [])

    neighborhoods = [
        [vertex for vertex in range(15) if variable(i, vertex) in model]
        for i in range(k)
    ] if satisfiable else None
    return {
        "mode": "select",
        "k": k,
        "degree_increment_budget": degree_increment,
        "clique_increment_budget": clique_increment,
        "coordinate_sum_budget": degree_increment + clique_increment,
        "internal_mask": mask,
        "internal_edges": [list(edge) for edge in edges],
        "clauses": clause_count,
        "satisfiable": satisfiable,
        "neighborhoods": neighborhoods,
    }


def build(k: int, mask: int, neighborhoods: list[list[int]]) -> nx.Graph:
    graph, _ = weighted_c5((3,) * 5)
    graph.add_nodes_from(range(15, 15 + k))
    graph.add_edges_from((15 + a, 15 + b) for a, b in internal_edges(k, mask))
    for i, neighborhood in enumerate(neighborhoods):
        graph.add_edges_from((15 + i, vertex) for vertex in neighborhood)
    return normalized_graph(graph)


def graph_digest(graph: nx.Graph) -> str:
    return hashlib.sha256(nx.to_graph6_bytes(graph, header=False).strip()).hexdigest()


def audit(k: int, mask: int, neighborhoods: list[list[int]]) -> dict:
    graph = build(k, mask, neighborhoods)
    claw = [0, 15, 5, 14]
    claw_valid = (
        all(graph.has_edge(0, leaf) for leaf in claw[1:])
        and all(not graph.has_edge(a, b) for a, b in itertools.combinations(claw[1:], 2))
    )
    complement = nx.complement(graph)
    max_independent = max(nx.find_cliques(complement), key=len)
    return {
        "mode": "audit",
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "graph6_sha256": graph_digest(graph),
        "hard_claw": claw,
        "hard_claw_valid": claw_valid,
        "alpha": len(max_independent),
        "independent_set": sorted(max_independent),
        "complement_connected": nx.is_connected(complement),
        "Rabern_threshold": (graph.number_of_nodes() + 3 - len(max_independent)) / 2,
    }


def evaluate(k: int, mask: int, neighborhoods: list[list[int]]) -> dict:
    graph = build(k, mask, neighborhoods)
    profile = exact_profile(graph)
    if not valid_profile(graph, profile):
        raise RuntimeError("invalid exact certificate")
    return {
        "mode": "evaluate",
        "graph6_sha256": graph_digest(graph),
        "profile": profile.as_dict(),
        "crossing": profile.slack < 0,
    }


def parse_neighborhoods(value: str) -> list[list[int]]:
    parsed = json.loads(value)
    if not isinstance(parsed, list) or not all(isinstance(row, list) for row in parsed):
        raise ValueError("neighborhoods must be a JSON list of lists")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("select", "audit", "evaluate"))
    parser.add_argument("--k", type=int, required=True)
    parser.add_argument("--degree-increment", type=int)
    parser.add_argument("--clique-increment", type=int)
    parser.add_argument("--mask", type=int, required=True)
    parser.add_argument("--neighborhoods")
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.mode == "select":
        result = select(args.k, args.degree_increment, args.clique_increment, args.mask)
    else:
        neighborhoods = parse_neighborhoods(args.neighborhoods)
        result = {"audit": audit, "evaluate": evaluate}[args.mode](args.k, args.mask, neighborhoods)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as stream:
            stream.write(rendered + "\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
