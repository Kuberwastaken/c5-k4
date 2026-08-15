#!/usr/bin/env python3
"""Replay the C4-factor Hamiltonicity theorem on every frozen Bondy row.

This is a theorem-shadow verifier, not a search.  It reconstructs the exact
96-row v3.5 grammar, builds the factor-incidence scaffold, finds a compatible
Euler tour, and maps that tour back to a Hamilton cycle of the peripheral
graph.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
CONSTRUCTOR_PATH = ROOT / "scripts" / "prospective_bondy_construct.py"


def load_constructor():
    spec = importlib.util.spec_from_file_location("prospective_bondy_construct", CONSTRUCTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen Bondy constructor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def c4_components(factor: nx.Graph) -> list[tuple[int, ...]]:
    components = [tuple(sorted(component)) for component in nx.connected_components(factor)]
    components.sort()
    if len(components) != 5:
        raise AssertionError("factor does not have five components")
    for component in components:
        induced = factor.subgraph(component)
        if len(component) != 4 or induced.number_of_edges() != 4:
            raise AssertionError("factor component is not a four-cycle")
        if set(dict(induced.degree()).values()) != {2}:
            raise AssertionError("factor component is not 2-regular")
    return components


def opposite_classes(factor: nx.Graph, component: tuple[int, ...]) -> dict[int, int]:
    opposite_edges = sorted(
        tuple(sorted((u, v)))
        for index, u in enumerate(component)
        for v in component[index + 1 :]
        if not factor.has_edge(u, v)
    )
    if len(opposite_edges) != 2 or set(opposite_edges[0]).intersection(opposite_edges[1]):
        raise AssertionError("four-cycle opposite-pair partition drift")
    classes: dict[int, int] = {}
    for class_index, pair in enumerate(opposite_edges):
        for edge_id in pair:
            classes[edge_id] = class_index
    if set(classes) != set(component):
        raise AssertionError("opposite-pair classes do not cover the component")
    return classes


def compatible_euler_tour(
    endpoints: dict[int, tuple[tuple[str, int], tuple[str, int]]],
    transition_class: dict[tuple[tuple[str, int], int], int],
) -> tuple[list[int], int]:
    incident: dict[tuple[str, int], list[int]] = {}
    for edge_id, (left, right) in endpoints.items():
        incident.setdefault(left, []).append(edge_id)
        incident.setdefault(right, []).append(edge_id)
    for edge_ids in incident.values():
        edge_ids.sort()

    expansions = 0
    all_mask = (1 << len(endpoints)) - 1

    def other(edge_id: int, vertex: tuple[str, int]) -> tuple[str, int]:
        left, right = endpoints[edge_id]
        if vertex == left:
            return right
        if vertex == right:
            return left
        raise AssertionError("edge is not incident with scaffold vertex")

    def visit(
        start_vertex: tuple[str, int],
        first_edge: int,
        current_vertex: tuple[str, int],
        incoming_edge: int,
        used_mask: int,
        sequence: list[int],
    ) -> list[int] | None:
        nonlocal expansions
        expansions += 1
        if expansions > 1_000_000:
            raise RuntimeError("compatible-Euler replay expansion cap exceeded")
        if used_mask == all_mask:
            if current_vertex != start_vertex:
                return None
            if transition_class[(current_vertex, incoming_edge)] == transition_class[(current_vertex, first_edge)]:
                return None
            return list(sequence)
        incoming_class = transition_class[(current_vertex, incoming_edge)]
        for next_edge in incident[current_vertex]:
            bit = 1 << next_edge
            if used_mask & bit:
                continue
            if transition_class[(current_vertex, next_edge)] == incoming_class:
                continue
            sequence.append(next_edge)
            answer = visit(
                start_vertex,
                first_edge,
                other(next_edge, current_vertex),
                next_edge,
                used_mask | bit,
                sequence,
            )
            if answer is not None:
                return answer
            sequence.pop()
        return None

    for first_edge in sorted(endpoints):
        for start_vertex, current_vertex in (endpoints[first_edge], endpoints[first_edge][::-1]):
            answer = visit(
                start_vertex,
                first_edge,
                current_vertex,
                first_edge,
                1 << first_edge,
                [first_edge],
            )
            if answer is not None:
                return answer, expansions
    raise AssertionError("Kotzig-compatible Euler tour was not found")


def verify_row(construct, row_index: int, params: tuple[object, ...]) -> dict[str, object]:
    graph, metadata = construct.construct_row(*params)
    verdict, _gate = construct.constructor_gate(graph, metadata)
    if verdict != "APPLICABLE":
        raise AssertionError(f"raw row {row_index} is not applicable: {verdict}")

    internal = nx.Graph()
    internal.add_nodes_from(range(construct.H_ORDER))
    internal.add_edges_from(
        (u, v) for u, v in graph.edges() if u // construct.T == v // construct.T
    )
    external = construct.graph_from_edges(construct.H_ORDER, metadata["added_edges"])
    internal_components = c4_components(internal)
    external_components = c4_components(external)
    if set(internal.edges()).intersection(external.edges()):
        raise AssertionError("the two four-cycle factors are not edge-disjoint")
    if {tuple(sorted(edge)) for edge in graph.edges()} != {
        tuple(sorted(edge)) for edge in list(internal.edges()) + list(external.edges())
    }:
        raise AssertionError("peripheral graph is not the exact union of its factors")

    internal_of = {vertex: index for index, component in enumerate(internal_components) for vertex in component}
    external_of = {vertex: index for index, component in enumerate(external_components) for vertex in component}
    endpoints = {
        vertex: (("I", internal_of[vertex]), ("X", external_of[vertex]))
        for vertex in range(construct.H_ORDER)
    }
    if len(set(endpoints.values())) != construct.H_ORDER:
        raise AssertionError("scaffold has parallel edges instead of K5,5 minus a matching")
    incidence = [[0] * 5 for _ in range(5)]
    for left, right in endpoints.values():
        incidence[left[1]][right[1]] += 1
    if any(value not in {0, 1} for row in incidence for value in row):
        raise AssertionError("scaffold is not simple")
    if any(sum(row) != 4 for row in incidence):
        raise AssertionError("scaffold left degree drift")
    if any(sum(incidence[i][j] for i in range(5)) != 4 for j in range(5)):
        raise AssertionError("scaffold right degree drift")
    missing = [(i, j) for i in range(5) for j in range(5) if incidence[i][j] == 0]
    if len(missing) != 5 or len({i for i, _ in missing}) != 5 or len({j for _, j in missing}) != 5:
        raise AssertionError("scaffold is not K5,5 minus a perfect matching")

    transition_class: dict[tuple[tuple[str, int], int], int] = {}
    for side, factor, components in (
        ("I", internal, internal_components),
        ("X", external, external_components),
    ):
        for index, component in enumerate(components):
            for edge_id, class_index in opposite_classes(factor, component).items():
                transition_class[((side, index), edge_id)] = class_index

    tour, expansions = compatible_euler_tour(endpoints, transition_class)
    if sorted(tour) != list(range(construct.H_ORDER)):
        raise AssertionError("Euler tour does not use every scaffold edge exactly once")
    for u, v in zip(tour, tour[1:] + tour[:1]):
        if not graph.has_edge(u, v):
            raise AssertionError("compatible Euler tour did not map to a Hamilton cycle")

    return {
        "row_index": row_index,
        "missing_matching": missing,
        "hamilton_cycle": tour,
        "compatible_euler_expansions": expansions,
    }


def main() -> None:
    construct = load_constructor()
    rows = []
    for row_index, params in enumerate(construct.frozen_parameter_rows()):
        rows.append(verify_row(construct, row_index, params))
    if len(rows) != construct.ROW_LIMIT:
        raise AssertionError("frozen row count drift")
    payload = {
        "classification": "THEOREM_SHADOW_REPLAY_VERIFIED",
        "constructor": str(CONSTRUCTOR_PATH.relative_to(ROOT)),
        "rows_verified": len(rows),
        "scaffold": "K5,5 minus a perfect matching",
        "hamilton_cycles_verified": len(rows),
        "maximum_compatible_euler_expansions": max(row["compatible_euler_expansions"] for row in rows),
        "row_certificate_sha256": hashlib.sha256(canonical_bytes(rows)).hexdigest(),
    }
    print(json.dumps(payload, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
