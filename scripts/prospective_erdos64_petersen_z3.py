#!/usr/bin/env python3
"""Frozen complete cyclic Z3 lift trial for current DeepMind Erdős 64."""

from __future__ import annotations

import hashlib
import itertools
import json
import signal
import time
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_erdos64_petersen_z3_contract.md"
SOURCE_AUDIT = ROOT / "results/expansion/prospective_erdos64_petersen_z3_source_audit.md"
LEDGER = ROOT / "results/expansion/prospective_erdos64_petersen_z3_ledger.jsonl"
CONTRACT_SHA256 = "674795e8f8114389d2986ff305cbb1f1c638716b3b2484e0ff9859e6a7201c3f"
SOURCE_SHA256 = "803c709ca940fb760df0eb21c4a7705b563f354ce64c5e830b7ae01f20e1d400"

BASE_EDGES = ((0, 1), (0, 4), (0, 5), (1, 2), (1, 6), (2, 3),
              (2, 7), (3, 4), (3, 8), (4, 9), (5, 7), (5, 8),
              (6, 8), (6, 9), (7, 9))
TREE_EDGES = frozenset(((0, 1), (0, 4), (0, 5), (1, 2), (1, 6),
                        (3, 4), (4, 9), (5, 7), (5, 8)))
COTREE_EDGES = ((2, 3), (2, 7), (3, 8), (6, 8), (6, 9), (7, 9))
TARGETS = (4, 8, 16)


def emit(row: dict) -> None:
    payload = {"contract_sha256": CONTRACT_SHA256, **row}
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
        handle.flush()
    print(json.dumps(payload, sort_keys=True), flush=True)


def check_freeze() -> None:
    for path, expected in ((CONTRACT, CONTRACT_SHA256),
                           (SOURCE_AUDIT, SOURCE_SHA256)):
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"frozen input changed: {path}: {actual}")


def canonical_edges(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(tuple(sorted(edge)) for edge in graph.edges()))


def find_cycle_length(graph: nx.Graph, target: int,
                      deadline: float) -> list[int] | None:
    """Exact DFS; the start is forced to be the least cycle vertex."""
    adjacency = {u: tuple(sorted(graph[u])) for u in graph}
    for start in sorted(graph):
        path = [start]
        used = {start}

        def dfs(u: int) -> list[int] | None:
            if time.monotonic() > deadline:
                raise TimeoutError
            if len(path) == target:
                return path.copy() if start in adjacency[u] else None
            for v in adjacency[u]:
                if v <= start or v in used:
                    continue
                # Break orientation symmetry at the closing step.
                if len(path) == target - 1 and path[1] > v:
                    continue
                used.add(v)
                path.append(v)
                found = dfs(v)
                if found is not None:
                    return found
                path.pop()
                used.remove(v)
            return None

        found = dfs(start)
        if found is not None:
            return found
    return None


def subset_degree_two_cycle(graph: nx.Graph, target: int,
                            deadline: float) -> list[int] | None:
    """Independent gate oracle: induced target-set is exactly one cycle."""
    # This intentionally recognizes chordless cycles.  On the order<=7 gate,
    # any 4-cycle can be reduced to a chordless triangle or C4; comparison is
    # required only for C4, so explicitly test the four cyclic edges as well.
    for vertices in itertools.combinations(sorted(graph), target):
        if time.monotonic() > deadline:
            raise TimeoutError
        sub = graph.subgraph(vertices)
        if sub.number_of_edges() == target and nx.is_connected(sub) and all(
                degree == 2 for _, degree in sub.degree()):
            return list(vertices)
        # Chorded C4 still contains a C4: test its three pairings.
        if target == 4:
            a, b, c, d = vertices
            for cycle in ((a, b, c, d), (a, b, d, c), (a, c, b, d)):
                if all(graph.has_edge(cycle[i], cycle[(i + 1) % 4])
                       for i in range(4)):
                    return list(cycle)
    return None


def base_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(10))
    graph.add_edges_from(BASE_EDGES)
    return graph


def run_gate(deadline: float) -> bool:
    base = base_graph()
    expected = canonical_edges(nx.petersen_graph())
    witness8 = find_cycle_length(base, 8, deadline)
    base_ok = (canonical_edges(base) == expected and nx.is_connected(base)
               and len(base) == 10 and base.number_of_edges() == 15
               and all(degree == 3 for _, degree in base.degree())
               and witness8 is not None)
    emit({"kind": "base_gate", "valid": base_ok, "n": len(base),
          "m": base.number_of_edges(), "degrees": sorted(dict(base.degree()).values()),
          "cycle8_witness": witness8, "tree_edges": sorted(TREE_EDGES),
          "cotree_edges": COTREE_EDGES})
    if not base_ok:
        return False
    checked = mismatches = 0
    for index, raw in enumerate(nx.graph_atlas_g()):
        if not raw or not nx.is_connected(raw) or len(raw) > 7:
            continue
        graph = nx.convert_node_labels_to_integers(raw)
        for target in TARGETS:
            if target > len(graph):
                continue
            primary = find_cycle_length(graph, target, deadline)
            audit = subset_degree_two_cycle(graph, target, deadline)
            checked += 1
            if (primary is None) != (audit is None):
                mismatches += 1
                emit({"kind": "gate_mismatch", "index": index,
                      "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
                      "target": target, "primary": primary, "audit": audit})
                return False
    emit({"kind": "gate_summary", "classification": "PASS" if not mismatches else "GATE_FAIL",
          "checks": checked, "mismatches": mismatches})
    return mismatches == 0


def lift_graph(assignment: tuple[int, ...]) -> nx.Graph:
    voltage = {edge: 0 for edge in TREE_EDGES}
    voltage.update(dict(zip(COTREE_EDGES, assignment)))
    graph = nx.Graph()
    graph.add_nodes_from(range(30))
    for u, v in BASE_EDGES:
        a = voltage[(u, v)]
        for sheet in range(3):
            graph.add_edge(3 * u + sheet, 3 * v + ((sheet + a) % 3))
    return graph


def reconstruct_independently(assignment: tuple[int, ...]) -> nx.Graph:
    values = dict(zip(COTREE_EDGES, assignment))
    edges = []
    for u, v in reversed(BASE_EDGES):
        shift = values.get((u, v), 0)
        edges.extend((3 * v + ((s + shift) % 3), 3 * u + s) for s in (2, 1, 0))
    return nx.Graph(edges)


def evaluate(deadline: float) -> str:
    evaluated = holds = crossings = timeouts = failures = 0
    assignments = itertools.product(range(3), repeat=6)
    for assignment in assignments:
        if assignment == (0,) * 6:
            continue
        if time.monotonic() > deadline:
            timeouts += 1
            break
        graph = lift_graph(assignment)
        valid = (len(graph) == 30 and graph.number_of_edges() == 45
                 and nx.number_of_selfloops(graph) == 0
                 and nx.is_connected(graph)
                 and all(degree == 3 for _, degree in graph.degree()))
        witnesses = {}
        try:
            for target in TARGETS:
                witnesses[str(target)] = find_cycle_length(graph, target, deadline)
        except TimeoutError:
            emit({"kind": "candidate_timeout", "assignment": assignment,
                  "phase": "primary_cycles"})
            timeouts += 1
            break
        crossing = valid and all(witnesses[str(target)] is None for target in TARGETS)
        audit = None
        if crossing:
            rebuilt = reconstruct_independently(assignment)
            same_edges = canonical_edges(rebuilt) == canonical_edges(graph)
            audit_witnesses = {}
            try:
                for target in TARGETS:
                    audit_witnesses[str(target)] = subset_degree_two_cycle(
                        rebuilt, target, deadline)
            except TimeoutError:
                emit({"kind": "candidate_timeout", "assignment": assignment,
                      "phase": "independent_crossing_audit"})
                timeouts += 1
                break
            audit = {"same_edges": same_edges, "witnesses": audit_witnesses,
                     "absence_verified": same_edges and all(
                         audit_witnesses[str(target)] is None for target in TARGETS)}
            crossing = crossing and audit["absence_verified"]
        failures += not valid
        crossings += crossing
        holds += valid and not crossing
        evaluated += 1
        emit({"kind": "candidate", "index": evaluated - 1,
              "assignment": assignment, "graph6": nx.to_graph6_bytes(
                  graph, header=False).decode().strip(),
              "n": len(graph), "m": graph.number_of_edges(),
              "connected": nx.is_connected(graph), "min_degree": min(dict(graph.degree()).values()),
              "construction_valid": valid, "cycle_witnesses": witnesses,
              "crossing": crossing, "independent_audit": audit})
        if failures or crossings:
            break
    if failures:
        classification = "GATE_FAIL"
    elif crossings:
        classification = "CROSSING_VERIFIED"
    elif timeouts:
        classification = "HOLD_WITH_TIMEOUTS"
    else:
        classification = "HOLD_BOUNDED"
    emit({"kind": "final_classification", "classification": classification,
          "declared": 728, "evaluated": evaluated, "holds": holds,
          "crossings": crossings, "failures": failures, "timeouts": timeouts,
          "public_action": False})
    return classification


def main() -> None:
    signal.alarm(60)
    started = time.monotonic()
    deadline = started + 55.0
    check_freeze()
    if not run_gate(deadline):
        emit({"kind": "final_classification", "classification": "GATE_FAIL",
              "public_action": False})
        return
    evaluate(deadline)


if __name__ == "__main__":
    main()
