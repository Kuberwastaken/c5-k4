#!/usr/bin/env python3
"""Frozen decision-first prospective trial for current WOWII #133."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import signal
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = ROOT / "results/expansion/prospective_wowii133_decision_first_addendum.md"
LEDGER = ROOT / "results/expansion/prospective_wowii133_decision_first_ledger.jsonl"
ADDENDUM_SHA256 = "9fff7eee1ec53f6266ec6fd57b7275aa093d72862284f90dba2b535c3d8d1489"

CORE_PATH = ROOT / "scripts/method_v02_133_search.py"
SPEC = importlib.util.spec_from_file_location("wow133_core_decision", CORE_PATH)
assert SPEC and SPEC.loader
CORE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CORE)


class DecisionTimeout(RuntimeError):
    pass


def check_addendum() -> None:
    actual = hashlib.sha256(ADDENDUM.read_bytes()).hexdigest()
    if actual != ADDENDUM_SHA256:
        raise RuntimeError(f"frozen addendum changed: {actual}")


def emit(row: dict) -> None:
    line = json.dumps({"addendum_sha256": ADDENDUM_SHA256, **row}, sort_keys=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
    print(line, flush=True)


def graph6(G: nx.Graph) -> str:
    H = nx.convert_node_labels_to_integers(G, ordering="default")
    return nx.to_graph6_bytes(H, header=False).decode("ascii").strip()


def c4_witness(G: nx.Graph) -> list | None:
    neighborhoods = {v: set(G[v]) for v in G}
    for u, v in itertools.combinations(G, 2):
        common = sorted(neighborhoods[u] & neighborhoods[v], key=repr)
        if len(common) >= 2:
            return [u, common[0], v, common[1]]
    return None


def local_independence(G: nx.Graph, vertex: object) -> tuple[int, list]:
    neighborhood = list(G[vertex])
    for size in range(len(neighborhood), -1, -1):
        for subset in itertools.combinations(neighborhood, size):
            if all(not G.has_edge(u, v) for u, v in itertools.combinations(subset, 2)):
                return size, list(subset)
    raise AssertionError


def target_data(G: nx.Graph) -> dict:
    local_values = []
    local_witnesses = {}
    for vertex in G:
        value, witness = local_independence(G, vertex)
        local_values.append(value)
        local_witnesses[repr(vertex)] = witness
    average = Fraction(sum(local_values), len(local_values))
    floor_l = average.numerator // average.denominator
    eccentricities = {
        vertex: max(nx.single_source_shortest_path_length(G, vertex).values())
        for vertex in G
    }
    center = min(eccentricities, key=lambda v: (eccentricities[v], repr(v)))
    radius = eccentricities[center]
    c4 = c4_witness(G)
    correction = 1 if c4 is not None else floor_l
    return {
        "radius": radius,
        "center": center,
        "eccentricities": {repr(v): value for v, value in eccentricities.items()},
        "floor_l": floor_l,
        "avg_l": str(average),
        "local_values": local_values,
        "local_witnesses": local_witnesses,
        "c4_witness": c4,
        "has_c4": c4 is not None,
        "target": radius + correction,
    }


def find_target_path(G: nx.Graph, target: int, cap: float) -> tuple[list | None, int]:
    deadline = time.monotonic() + cap
    adjacency = {v: set(G[v]) for v in G}
    states = 0

    def extend(path: list, used: set) -> list | None:
        nonlocal states
        states += 1
        if states & 1023 == 0 and time.monotonic() > deadline:
            raise DecisionTimeout
        if len(path) >= target:
            return path.copy()
        endpoint = path[-1]
        forbidden = used - {endpoint}
        for nxt in sorted(adjacency[endpoint] - used, key=repr):
            if adjacency[nxt].isdisjoint(forbidden):
                result = extend(path + [nxt], used | {nxt})
                if result is not None:
                    return result
        return None

    for start in sorted(G, key=repr):
        result = extend([start], {start})
        if result is not None:
            return result, states
    return None, states


def subset_is_path(G: nx.Graph, subset: tuple) -> bool:
    H = G.subgraph(subset)
    if len(H) <= 1:
        return True
    degrees = dict(H.degree()).values()
    return (nx.is_connected(H) and H.number_of_edges() == len(H) - 1
            and sum(value == 1 for value in degrees) == 2
            and max(degrees) <= 2)


def independent_no_target_check(G: nx.Graph, target: int, cap: float) -> tuple[bool, int]:
    deadline = time.monotonic() + cap
    states = 0
    vertices = list(G)
    for subset in itertools.combinations(vertices, target):
        states += 1
        if states & 4095 == 0 and time.monotonic() > deadline:
            raise DecisionTimeout
        if subset_is_path(G, subset):
            return False, states
    return True, states


def evaluate(G: nx.Graph, name: str, stratum: str,
             decision_cap: float = 5.0, exact_cap: float = 20.0) -> dict:
    started = time.monotonic()
    if len(G) < 2 or G.is_multigraph() or nx.number_of_selfloops(G):
        return {"kind": "rejected", "name": name, "stratum": stratum,
                "reason": "not_simple_nontrivial"}
    if not nx.is_connected(G):
        return {"kind": "rejected", "name": name, "stratum": stratum,
                "reason": "disconnected", "n": len(G), "m": G.number_of_edges()}
    # All retained witnesses use the same dense integer coordinate system as
    # graph6.  This is essential after vertex deletion leaves gaps in labels.
    G = nx.convert_node_labels_to_integers(G, ordering="default")
    data = target_data(G)
    base = {
        "name": name, "stratum": stratum, "n": len(G),
        "m": G.number_of_edges(), "graph6": graph6(G), **data,
    }
    try:
        witness, states = find_target_path(G, data["target"], decision_cap)
    except DecisionTimeout:
        return {"kind": "decision_timeout", **base,
                "seconds": round(time.monotonic() - started, 6)}
    if witness is not None:
        return {"kind": "hold_witness", **base, "decision_witness": witness,
                "decision_states": states,
                "seconds": round(time.monotonic() - started, 6)}

    # The exhaustive target search found no target path.  Per the frozen
    # addendum only this branch invokes exact maximization.
    try:
        path, path_witness, exact_states = CORE.longest_induced_path(G, exact_cap)
    except CORE.SolveTimeout:
        return {"kind": "exact_timeout", **base, "decision_states": states,
                "seconds": round(time.monotonic() - started, 6)}
    residual = path - data["target"]
    row = {"kind": "exact_crossing" if residual < 0 else "exact_graph", **base,
           "decision_states": states, "path": path,
           "path_witness": path_witness, "exact_states": exact_states,
           "residual": residual,
           "seconds": round(time.monotonic() - started, 6)}
    if residual < 0:
        try:
            no_target, subset_states = independent_no_target_check(
                G, data["target"], exact_cap
            )
            row["independent_verified"] = no_target and path < data["target"]
            row["independent_states"] = subset_states
        except DecisionTimeout:
            row["independent_verified"] = False
            row["independent_timeout"] = True
    return row


def normalized_projective_vectors(q: int) -> list[tuple[int, int, int]]:
    vectors = set()
    for raw in itertools.product(range(q), repeat=3):
        if raw == (0, 0, 0):
            continue
        first = next(value for value in raw if value)
        inverse = pow(first, q - 2, q)
        vectors.add(tuple((inverse * value) % q for value in raw))
    return sorted(vectors)


def polarity_graph(q: int) -> nx.Graph:
    points = normalized_projective_vectors(q)
    G = nx.Graph()
    G.add_nodes_from(range(len(points)))
    for i, point in enumerate(points):
        for j, other in enumerate(points[i + 1:], i + 1):
            if sum(a * b for a, b in zip(point, other)) % q == 0:
                G.add_edge(i, j)
    return G


def deletion_representatives(G: nx.Graph, cap: int = 24):
    data = target_data(G)
    eccentricities = {int(key): value for key, value in data["eccentricities"].items()}
    values = dict(zip(G, data["local_values"]))
    vertex_buckets = {}
    for vertex in G:
        signature = (G.degree(vertex), eccentricities[vertex], values[vertex])
        vertex_buckets.setdefault(signature, vertex)
    singles = sorted(vertex_buckets.values())
    for index, vertex in enumerate(singles):
        H = G.copy()
        H.remove_node(vertex)
        yield f"delete1:{index}", H

    distances = dict(nx.all_pairs_shortest_path_length(G))
    pair_buckets = {}
    for u, v in itertools.combinations(G, 2):
        first = (G.degree(u), eccentricities[u], values[u])
        second = (G.degree(v), eccentricities[v], values[v])
        signature = tuple(sorted((first, second))) + (distances[u][v], G.has_edge(u, v))
        pair_buckets.setdefault(signature, (u, v))
    for index, pair in enumerate([pair_buckets[key] for key in sorted(pair_buckets)][:cap]):
        H = G.copy()
        H.remove_nodes_from(pair)
        yield f"delete2:{index}", H


def chord_closure(n: int):
    G = nx.cycle_graph(n)
    yield "round0", G.copy()
    for round_index in range(1, 17):
        data = target_data(G)
        witness, _ = find_target_path(G, data["target"], 1.0)
        if witness is None:
            return
        candidates = []
        for i, u in enumerate(witness):
            for v in witness[i + 2:]:
                if G.has_edge(u, v):
                    continue
                H = G.copy()
                H.add_edge(u, v)
                if c4_witness(H) is not None:
                    continue
                new_data = target_data(H)
                if new_data["target"] < data["target"]:
                    continue
                score = (new_data["target"], new_data["radius"],
                         new_data["floor_l"])
                candidates.append((score, graph6(H), H))
        if not candidates:
            return
        best_score = max(score for score, _, _ in candidates)
        _, _, G = min((row for row in candidates if row[0] == best_score),
                      key=lambda row: row[1])
        yield f"round{round_index}", G.copy()


def amalgam(base: nx.Graph, copies: int, mode: str) -> nx.Graph:
    vertices = sorted(base)
    left, right = vertices[:2]

    def mapped(copy: int, vertex: int):
        if mode == "hub" and vertex == left:
            return ("hub",)
        if mode == "chain":
            if vertex == right and copy < copies - 1:
                return ("joint", copy)
            if vertex == left and copy > 0:
                return ("joint", copy - 1)
        return ("copy", copy, vertex)

    G = nx.Graph()
    for copy in range(copies):
        for u, v in base.edges():
            a, b = mapped(copy, u), mapped(copy, v)
            if a != b:
                G.add_edge(a, b)
    return nx.convert_node_labels_to_integers(G, ordering="default")


def discovery_graphs():
    for q in (3, 5, 7):
        base = polarity_graph(q)
        yield f"polarity:q{q}:base", "polarity_base", base
        for suffix, graph in deletion_representatives(base):
            yield f"polarity:q{q}:{suffix}", "polarity_deletion", graph
    for n in range(8, 31):
        for suffix, graph in chord_closure(n):
            yield f"chord:C{n}:{suffix}", "witness_blocking_chord", graph
    for base_name, base in (("Petersen", nx.petersen_graph()),
                            ("polarity-q3", polarity_graph(3))):
        for copies in range(2, 5):
            for mode in ("hub", "chain"):
                yield (f"amalgam:{base_name}:{mode}:{copies}",
                       f"dense_block_{mode}", amalgam(base, copies, mode))


def latest_gate_passed() -> bool:
    if not LEDGER.exists():
        return False
    for line in reversed(LEDGER.read_text(encoding="utf-8").splitlines()):
        row = json.loads(line)
        if row.get("kind") == "gate_summary":
            return row.get("verdict") == "PASS"
    return False


def run_gate(outer_cap: float) -> None:
    started = time.monotonic()
    failures = timeouts = 0
    controls = CORE.controls()
    emit({"kind": "phase_start", "phase": "gate", "controls": len(controls)})
    for index, (name, G) in enumerate(controls):
        if time.monotonic() - started > outer_cap:
            emit({"kind": "gate_summary", "verdict": "GATE_FAIL",
                  "reason": "outer_timeout", "completed": index})
            return
        row = evaluate(G, name, "gate", decision_cap=2.0, exact_cap=5.0)
        exact = CORE.evaluate(G, name, "gate_exact", timeout=5.0)
        exact_holds = exact.get("residual", -1) >= 0
        decision_holds = row["kind"] == "hold_witness"
        agrees = exact_holds and decision_holds
        failures += not agrees
        timeouts += row["kind"].endswith("timeout") or exact["kind"] == "solve_timeout"
        emit({"kind": "gate_row", "name": name, "agrees": agrees,
              "decision_kind": row["kind"], "decision_target": row.get("target"),
              "decision_states": row.get("decision_states"),
              "exact_kind": exact["kind"], "exact_path": exact.get("path"),
              "exact_residual": exact.get("residual")})
        if failures or timeouts:
            break
    verdict = "PASS" if not failures and not timeouts and index + 1 == len(controls) else "GATE_FAIL"
    emit({"kind": "gate_summary", "verdict": verdict, "completed": index + 1,
          "failures": failures, "timeouts": timeouts,
          "seconds": round(time.monotonic() - started, 6)})


def run_search(offset: int, limit: int, outer_cap: float) -> None:
    if not latest_gate_passed():
        raise RuntimeError("decision-first database gate has not passed")
    started = time.monotonic()
    stats = {"completed": 0, "holds": 0, "decision_timeouts": 0,
             "exact_timeouts": 0, "crossings": 0, "c4_rejected": 0}
    emit({"kind": "phase_start", "phase": "search", "offset": offset,
          "limit": limit, "coordinate_schema": "graph6_dense_integer_v2"})
    seen = set()
    unique_index = 0
    selected = 0
    for name, stratum, G in discovery_graphs():
        if selected >= limit or unique_index >= 600:
            break
        code = graph6(G)
        if code in seen or len(G) > 80:
            continue
        seen.add(code)
        discovery_index = unique_index
        unique_index += 1
        if discovery_index < offset:
            continue
        if time.monotonic() - started > outer_cap:
            break
        selected += 1
        if c4_witness(G) is not None:
            stats["c4_rejected"] += 1
            emit({"kind": "candidate_rejected", "name": name, "stratum": stratum,
                  "reason": "has_c4", "n": len(G), "m": G.number_of_edges(),
                  "discovery_index": discovery_index})
            continue
        row = evaluate(G, name, stratum)
        row["discovery_index"] = discovery_index
        emit(row)
        stats["completed"] += 1
        stats["holds"] += row["kind"] == "hold_witness"
        stats["decision_timeouts"] += row["kind"] == "decision_timeout"
        stats["exact_timeouts"] += row["kind"] == "exact_timeout"
        if row["kind"] == "exact_crossing" and row.get("independent_verified"):
            stats["crossings"] += 1
            break
    if stats["crossings"]:
        verdict = "CROSSING_VERIFIED"
    elif not stats["completed"] and not stats["c4_rejected"]:
        verdict = "NO_APPLICABLE_CANDIDATES"
    elif stats["decision_timeouts"] or stats["exact_timeouts"]:
        verdict = "HOLD_WITH_TIMEOUTS"
    else:
        verdict = "HOLD_BOUNDED"
    emit({"kind": "search_summary", "verdict": verdict, "offset": offset,
          "requested": limit, "selected": selected,
          "next_offset": offset + selected, **stats,
          "seconds": round(time.monotonic() - started, 6)})


def run_audit() -> None:
    latest = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("discovery_index") is not None and row.get("graph6"):
            latest[row["discovery_index"]] = row
    failures = []
    max_states = 0
    for index, row in sorted(latest.items()):
        G = nx.from_graph6_bytes(row["graph6"].encode("ascii"))
        data = target_data(G)
        witness = row.get("decision_witness")
        ordered_edges = witness is not None and all(
            G.has_edge(u, v) for u, v in zip(witness, witness[1:])
        )
        no_chords = witness is not None and all(
            not G.has_edge(witness[i], witness[j])
            for i in range(len(witness)) for j in range(i + 2, len(witness))
        )
        valid = (row["kind"] == "hold_witness" and data["c4_witness"] is None
                 and data["target"] == row["target"] and witness is not None
                 and len(witness) >= row["target"] and ordered_edges and no_chords)
        if not valid:
            failures.append(index)
        max_states = max(max_states, row.get("decision_states", 0))
    emit({"kind": "audit_summary", "candidates": len(latest),
          "valid_hold_witnesses": len(latest) - len(failures),
          "failures": failures, "max_decision_states": max_states,
          "verdict": "PASS" if not failures else "FAIL"})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("gate", "search", "count", "audit"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--outer-cap", type=float, default=55.0)
    args = parser.parse_args()
    if not (0 < args.outer_cap < 60) or args.offset < 0 or args.limit < 1:
        parser.error("invalid frozen resource bounds")
    check_addendum()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(59)
    if args.phase == "gate":
        run_gate(args.outer_cap)
    elif args.phase == "count":
        print(sum(1 for _ in itertools.islice(discovery_graphs(), 600)))
    elif args.phase == "audit":
        run_audit()
    else:
        run_search(args.offset, args.limit, args.outer_cap)


if __name__ == "__main__":
    main()
