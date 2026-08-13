#!/usr/bin/env python3
"""Frozen two-sheet lift family of K3,3-e for WOWII #141."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import signal
import time
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_formal_141_k33e_two_lift_contract.md"
LEDGER = ROOT / "results/expansion/prospective_formal_141_k33e_two_lift_ledger.jsonl"
PARENT_LEDGER = ROOT / "results/expansion/prospective_formal_141_whitney_switch_ledger.jsonl"
BASELINE = ROOT / "results/expansion/prospective_formal_141_s4_cover_ledger.jsonl"
CONTRACT_SHA256 = "34819826bd78b40b6cad59e2db3f033c52adacacdf9c1305516212c3ba357307"
PARENT_SHA256 = "6c1395d6c1f75bdf4541c56e73f87c407790e1c0c8cc274a22e8d72abaf9056e"
BASELINE_SHA256 = "b10753f8a3c48c5d4bcf5f0c74fed12c2b4c300f699824989d3e09beb4c27d0a"
PARENT_PATH = ROOT / "scripts/prospective_formal_oneoff_141.py"
SPEC = importlib.util.spec_from_file_location("wow141_parent_k33e_lift", PARENT_PATH)
assert SPEC and SPEC.loader
PARENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARENT)

SEED_EDGES = ((0, 4), (0, 5), (1, 2), (1, 4),
              (1, 5), (2, 3), (3, 4), (3, 5))
TREE_EDGES = frozenset(((0, 4), (0, 5), (1, 2), (1, 4), (3, 4)))
COTREE_EDGES = ((1, 5), (2, 3), (3, 5))
VOLTAGES = ("001", "010", "011", "100", "101", "110", "111")


def emit(row: dict) -> None:
    line = json.dumps({"contract_sha256": CONTRACT_SHA256, **row}, sort_keys=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
    print(line, flush=True)


def check_contract() -> None:
    checks = {
        "contract": (CONTRACT, CONTRACT_SHA256),
        "parent_ledger": (PARENT_LEDGER, PARENT_SHA256),
        "baseline_ledger": (BASELINE, BASELINE_SHA256),
    }
    for name, (path, expected) in checks.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"{name} changed: {actual}")


def frozen_gate_rows() -> dict[tuple[str, str], dict]:
    rows = {}
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("kind") == "gate_row":
            rows[(row["name"], row["graph6"])] = row
    return rows


def run_gate(cap: float) -> bool:
    started = time.monotonic()
    controls = PARENT.controls()
    frozen = frozen_gate_rows()
    emit({"kind": "phase_start", "phase": "gate", "controls": len(controls)})
    completed = failures = timeouts = 0
    fields = ("girth", "lambda_max", "target", "tree", "residual")
    for index, (name, raw) in enumerate(controls):
        elapsed = time.monotonic() - started
        if elapsed >= cap:
            timeouts += 1
            break
        graph = nx.convert_node_labels_to_integers(raw, ordering="default")
        graph6 = PARENT.graph6(graph)
        data = PARENT.invariants(graph)
        try:
            tree, witness, states = PARENT.exact_largest_induced_tree(
                graph, min(10.0, cap - elapsed))
        except PARENT.SearchTimeout:
            timeouts += 1
            emit({"kind": "gate_timeout", "index": index, "name": name,
                  "graph6": graph6})
            break
        observed = {**data, "tree": tree, "residual": tree - data["target"]}
        expected = frozen.get((name, graph6))
        matches = expected is not None and all(observed[field] == expected[field]
                                               for field in fields)
        valid = PARENT.replay_tree(graph, witness, tree) and matches
        failures += not valid or observed["residual"] < 0
        completed = index + 1
        emit({"kind": "gate_row", "index": index, "name": name,
              "graph6": graph6, "n": len(graph), "m": graph.number_of_edges(),
              **observed, "tree_witness": witness, "tree_states": states,
              "certificate_valid": valid, "baseline_match": matches})
        if failures:
            break
    verdict = "PASS" if completed == len(controls) and failures == 0 and timeouts == 0 else "GATE_FAIL"
    emit({"kind": "gate_summary", "verdict": verdict, "completed": completed,
          "controls": len(controls), "failures": failures, "timeouts": timeouts,
          "seconds": round(time.monotonic() - started, 6)})
    return verdict == "PASS"


def seed_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(6))
    graph.add_edges_from(SEED_EDGES)
    return graph


def seed_audit() -> bool:
    seed = seed_graph()
    data = PARENT.invariants(seed)
    tree, witness, states = PARENT.exact_largest_induced_tree(seed, 10.0)
    atlas = nx.from_graph6_bytes(b"EhUg")
    matcher = nx.algorithms.isomorphism.GraphMatcher(seed, atlas)
    valid = (
        PARENT.graph6(seed) == "EHvO"
        and data["girth"] == 4 and data["lambda_max"] == 3
        and data["target"] == 4 and tree == 4
        and PARENT.replay_tree(seed, witness, tree)
        and matcher.is_isomorphic()
    )
    emit({"kind": "seed_audit", "valid": valid, "graph6": PARENT.graph6(seed),
          **data, "tree": tree, "residual": tree - data["target"],
          "tree_witness": witness, "tree_states": states,
          "atlas_graph6": "EhUg",
          "seed_to_atlas": dict(sorted(matcher.mapping.items())) if matcher.is_isomorphic() else None})
    return valid


def four_cycles(graph: nx.Graph) -> list[list[int]]:
    cycles = set()
    for vertices in itertools.combinations(sorted(graph), 4):
        start = min(vertices)
        for tail in itertools.permutations(v for v in vertices if v != start):
            cycle = (start,) + tail
            if cycle[1] > cycle[-1]:
                continue
            if all(graph.has_edge(cycle[i], cycle[(i + 1) % 4]) for i in range(4)):
                cycles.add(cycle)
    return [list(cycle) for cycle in sorted(cycles)]


def lift_graph(bits: str) -> tuple[nx.Graph, dict[tuple[int, int], int]]:
    voltage = {edge: 0 for edge in TREE_EDGES}
    voltage.update({edge: int(bit) for edge, bit in zip(COTREE_EDGES, bits)})
    lift = nx.Graph()
    lift.add_nodes_from(range(12))
    for u, v in SEED_EDGES:
        x = voltage[(u, v)]
        for sheet in (0, 1):
            lift.add_edge(2 * u + sheet, 2 * v + (sheet ^ x))
    return lift, voltage


def cover_audit(base: nx.Graph, lift: nx.Graph) -> tuple[bool, list[dict]]:
    rows = []
    valid = True
    for vertex in sorted(lift):
        image = vertex // 2
        neighbor_images = sorted(nbr // 2 for nbr in lift[vertex])
        expected = sorted(base[image])
        okay = neighbor_images == expected and len(neighbor_images) == len(set(neighbor_images))
        valid &= okay
        rows.append({"vertex": vertex, "image": image,
                     "neighbor_images": neighbor_images, "valid": okay})
    return valid, rows


def cycle_parities(cycles: list[list[int]], voltage: dict[tuple[int, int], int]) -> list[dict]:
    rows = []
    for cycle in cycles:
        parity = 0
        for u, v in zip(cycle, cycle[1:] + cycle[:1]):
            parity ^= voltage[tuple(sorted((u, v)))]
        rows.append({"cycle": cycle, "parity": parity})
    return rows


def replay_girth(graph: nx.Graph, girth: int, witness: list[int]) -> bool:
    return (
        girth == len(witness)
        and len(set(witness)) == girth
        and all(graph.has_edge(witness[i], witness[(i + 1) % girth])
                for i in range(girth))
    )


def exact_tree_bitmask(graph: nx.Graph, cap: float) -> tuple[int, list[int], int]:
    """Independent exhaustive audit using adjacency bitmasks."""
    started = time.monotonic()
    n = len(graph)
    adjacency = [sum(1 << neighbor for neighbor in graph[vertex]) for vertex in range(n)]
    best = 0
    witness: list[int] = []
    states = 0
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            states += 1
            if states & 1023 == 0 and time.monotonic() - started > cap:
                raise PARENT.SearchTimeout
            mask = sum(1 << vertex for vertex in subset)
            edges_twice = sum(bin(adjacency[vertex] & mask).count("1")
                              for vertex in subset)
            if edges_twice != 2 * (size - 1):
                continue
            reached = 1 << subset[0]
            frontier = reached
            while frontier:
                bit = frontier & -frontier
                frontier ^= bit
                vertex = bit.bit_length() - 1
                new = adjacency[vertex] & mask & ~reached
                reached |= new
                frontier |= new
            if reached == mask:
                best = size
                witness = list(subset)
    return best, witness, states


def evaluate_family(cap: float) -> str:
    started = time.monotonic()
    base = seed_graph()
    cycles = four_cycles(base)
    emit({"kind": "phase_start", "phase": "family", "candidates": len(VOLTAGES),
          "base_four_cycles": cycles})
    records = []
    graphs = []
    timeouts = failures = crossings = target_raising = 0
    for bits in VOLTAGES:
        remaining = cap - (time.monotonic() - started)
        if remaining <= 0:
            timeouts += 1
            emit({"kind": "candidate_timeout", "voltage": bits, "phase": "outer"})
            break
        graph, voltage = lift_graph(bits)
        cover_valid, cover_rows = cover_audit(base, graph)
        data = PARENT.invariants(graph)
        construction_valid = (
            len(graph) == 12 and graph.number_of_edges() == 16
            and nx.number_of_selfloops(graph) == 0 and not graph.is_multigraph()
            and nx.is_connected(graph) and cover_valid
        )
        target_raising += data["girth"] >= 6
        try:
            target_witness, target_states = PARENT.find_target_tree(
                graph, data["target"], min(10.0, remaining))
            primary_tree, primary_witness, primary_states = PARENT.exact_largest_induced_tree(
                graph, min(20.0, remaining))
            audit_tree, audit_witness, audit_states = exact_tree_bitmask(
                graph, min(20.0, remaining))
        except PARENT.SearchTimeout:
            timeouts += 1
            emit({"kind": "candidate_timeout", "voltage": bits,
                  "phase": "tree_search"})
            continue
        target_valid = target_witness is not None and PARENT.replay_tree(
            graph, target_witness, data["target"])
        primary_valid = PARENT.replay_tree(graph, primary_witness, primary_tree)
        audit_valid = PARENT.replay_tree(graph, audit_witness, audit_tree)
        girth_valid = replay_girth(graph, data["girth"], data["girth_witness"])
        exact_agreement = primary_tree == audit_tree
        residual = primary_tree - data["target"]
        valid = (construction_valid and target_valid and primary_valid and audit_valid
                 and girth_valid and exact_agreement and data["lambda_max"] == 3)
        failures += not valid
        crossings += residual < 0
        parities = cycle_parities(cycles, voltage)
        row = {"kind": "candidate", "voltage": bits,
               "voltage_edges": {f"{u}{v}": value for (u, v), value in voltage.items()},
               "graph6": PARENT.graph6(graph), "n": len(graph),
               "m": graph.number_of_edges(), "degree_multiset": sorted(dict(graph.degree()).values()),
               "connected": nx.is_connected(graph), "construction_valid": construction_valid,
               "cover_valid": cover_valid, "cover_rows": cover_rows,
               "base_four_cycle_parities": parities, **data,
               "girth_certificate_valid": girth_valid,
               "target_tree_found": target_witness is not None,
               "target_tree_witness": target_witness, "target_tree_states": target_states,
               "target_tree_certificate_valid": target_valid,
               "tree": primary_tree, "tree_witness": primary_witness,
               "tree_states": primary_states, "tree_certificate_valid": primary_valid,
               "audit_tree": audit_tree, "audit_tree_witness": audit_witness,
               "audit_tree_states": audit_states, "audit_certificate_valid": audit_valid,
               "exact_tree_agreement": exact_agreement, "residual": residual,
               "crossing": residual < 0, "candidate_valid": valid}
        emit(row)
        records.append(row)
        graphs.append((bits, graph))
        if failures:
            break

    classes: list[list[str]] = []
    for bits, graph in graphs:
        for group in classes:
            representative = next(candidate for label, candidate in graphs if label == group[0])
            if nx.is_isomorphic(graph, representative):
                group.append(bits)
                break
        else:
            classes.append([bits])
    class_consistent = all(
        len({(row["girth"], row["lambda_max"], row["tree"], row["target"], row["residual"])
             for row in records if row["voltage"] in group}) == 1
        for group in classes
    )
    emit({"kind": "isomorphism_audit", "classes": classes,
          "class_count": len(classes), "invariants_consistent": class_consistent})
    failures += not class_consistent or len(records) + timeouts != len(VOLTAGES)
    if failures:
        verdict = "GATE_FAIL"
    elif crossings:
        verdict = "CROSSING_VERIFIED"
    elif timeouts:
        verdict = "HOLD_WITH_TIMEOUTS"
    elif target_raising == 0:
        verdict = "NO_TARGET_RAISING_CANDIDATES"
    else:
        verdict = "HOLD_BOUNDED"
    emit({"kind": "final_classification", "classification": verdict,
          "evaluated": len(records), "declared": len(VOLTAGES),
          "target_raising": target_raising, "crossings": crossings,
          "failures": failures, "timeouts": timeouts,
          "database_sanity": "PASS", "public_action": False,
          "novelty_gate": "TRIGGERED" if verdict == "CROSSING_VERIFIED"
                          else "NOT_TRIGGERED_NO_CROSSING",
          "seconds": round(time.monotonic() - started, 6)})
    return verdict


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "family", "all"), default="all")
    args = parser.parse_args()
    check_contract()
    signal.alarm(60)
    if args.phase in ("gate", "all") and not run_gate(55.0):
        return
    if args.phase in ("family", "all"):
        if not seed_audit():
            emit({"kind": "final_classification", "classification": "GATE_FAIL",
                  "reason": "seed_audit", "public_action": False})
            return
        evaluate_family(55.0)


if __name__ == "__main__":
    main()
