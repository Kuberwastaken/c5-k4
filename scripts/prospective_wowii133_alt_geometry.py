#!/usr/bin/env python3
"""Frozen prospective alternate-geometry search for current WOWII #133."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import signal
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_wowii133_alt_geometry_contract.md"
LEDGER = ROOT / "results/expansion/prospective_wowii133_alt_geometry_ledger.jsonl"
CONTRACT_SHA256 = "ca7e13b019bb5316169771d8f859d08cdfa816174a530cd73065f6f4c3ddb1b3"


class SolveTimeout(RuntimeError):
    pass


def alarm_handler(_signum: int, _frame: object) -> None:
    raise TimeoutError("outer 60-second process cap")


def check_contract() -> None:
    actual = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if actual != CONTRACT_SHA256:
        raise RuntimeError(f"frozen contract changed: {actual}")


def emit(row: dict) -> None:
    row = {"contract_sha256": CONTRACT_SHA256, **row}
    line = json.dumps(row, sort_keys=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
    print(line, flush=True)


def graph6(G: nx.Graph) -> str:
    H = nx.convert_node_labels_to_integers(G, ordering="sorted")
    return nx.to_graph6_bytes(H, header=False).decode().strip()


def c4_witness(G: nx.Graph) -> list | None:
    neighborhoods = {v: set(G[v]) for v in G}
    for u, v in itertools.combinations(G, 2):
        common = sorted(neighborhoods[u] & neighborhoods[v], key=repr)
        if len(common) >= 2:
            return [u, common[0], v, common[1]]
    return None


def local_independence(G: nx.Graph, v: object) -> tuple[int, list]:
    neighbors = list(G[v])
    for size in range(len(neighbors), -1, -1):
        for subset in itertools.combinations(neighbors, size):
            if all(not G.has_edge(x, y) for x, y in itertools.combinations(subset, 2)):
                return size, list(subset)
    raise AssertionError


def local_profile(G: nx.Graph) -> tuple[int, Fraction, list[int], dict[str, list]]:
    values: list[int] = []
    witnesses: dict[str, list] = {}
    for v in G:
        value, witness = local_independence(G, v)
        values.append(value)
        witnesses[repr(v)] = witness
    average = Fraction(sum(values), len(values))
    return average.numerator // average.denominator, average, values, witnesses


def radius_with_witness(G: nx.Graph) -> tuple[int, object, dict[str, int]]:
    eccentricities = {
        v: max(nx.single_source_shortest_path_length(G, v).values()) for v in G
    }
    center = min(eccentricities, key=lambda v: (eccentricities[v], repr(v)))
    return eccentricities[center], center, {repr(v): e for v, e in eccentricities.items()}


def longest_induced_path(G: nx.Graph, cap: float) -> tuple[int, list, int]:
    deadline = time.monotonic() + cap
    adjacency = {v: set(G[v]) for v in G}
    best: list = []
    states = 0

    def extend(path: list, used: set) -> None:
        nonlocal best, states
        states += 1
        if states & 4095 == 0 and time.monotonic() > deadline:
            raise SolveTimeout
        if len(path) > len(best):
            best = path.copy()
        endpoint = path[-1]
        forbidden = used - {endpoint}
        for nxt in sorted(adjacency[endpoint] - used, key=repr):
            if adjacency[nxt].isdisjoint(forbidden):
                used.add(nxt)
                path.append(nxt)
                extend(path, used)
                path.pop()
                used.remove(nxt)

    for start in sorted(G, key=repr):
        extend([start], {start})
    return len(best), best, states


def subset_is_path(G: nx.Graph, subset: tuple) -> bool:
    H = G.subgraph(subset)
    if len(H) == 1:
        return True
    degrees = dict(H.degree())
    return (
        nx.is_connected(H)
        and H.number_of_edges() == len(H) - 1
        and sum(d == 1 for d in degrees.values()) == 2
        and max(degrees.values()) <= 2
    )


def independent_path_check(G: nx.Graph, expected: int, cap: float) -> list:
    deadline = time.monotonic() + cap
    vertices = list(G)
    for size in range(len(vertices), 0, -1):
        for index, subset in enumerate(itertools.combinations(vertices, size)):
            if index & 4095 == 0 and time.monotonic() > deadline:
                raise SolveTimeout
            if subset_is_path(G, subset):
                if size != expected:
                    raise AssertionError((size, expected, subset))
                return list(subset)
    raise AssertionError


def evaluate(G: nx.Graph, name: str, stratum: str, solve_cap: float,
             independently_verify: bool = True) -> dict:
    start = time.monotonic()
    if len(G) < 2 or G.is_multigraph() or nx.number_of_selfloops(G):
        return {"kind": "rejected", "name": name, "stratum": stratum,
                "reason": "not_simple_nontrivial"}
    if not nx.is_connected(G):
        return {"kind": "rejected", "name": name, "stratum": stratum,
                "reason": "disconnected"}
    witness = c4_witness(G)
    has_c4 = witness is not None
    radius, center, eccentricities = radius_with_witness(G)
    floor_l, average_l, local_values, local_witnesses = local_profile(G)
    try:
        path, path_witness, states = longest_induced_path(G, solve_cap)
    except SolveTimeout:
        return {
            "kind": "solve_timeout", "name": name, "stratum": stratum,
            "n": len(G), "m": G.number_of_edges(), "graph6": graph6(G),
            "has_c4": has_c4, "c4_witness": witness, "radius": radius,
            "center": center, "floor_l": floor_l, "avg_l": str(average_l),
            "seconds": round(time.monotonic() - start, 6),
        }
    correction = 1 if has_c4 else floor_l
    residual = path - radius - correction
    row = {
        "kind": "graph", "name": name, "stratum": stratum,
        "n": len(G), "m": G.number_of_edges(), "graph6": graph6(G),
        "connected": True, "has_c4": has_c4, "c4_witness": witness,
        "radius": radius, "center": center, "eccentricities": eccentricities,
        "floor_l": floor_l, "avg_l": str(average_l),
        "local_values": local_values, "local_witnesses": local_witnesses,
        "path": path, "path_witness": path_witness, "states": states,
        "residual": residual, "seconds": round(time.monotonic() - start, 6),
    }
    if independently_verify and residual <= 0:
        try:
            row["independent_path_witness"] = independent_path_check(
                G, path, min(solve_cap, 55.0)
            )
            row["independent_verified"] = True
        except SolveTimeout:
            row["independent_verified"] = False
            row["independent_timeout"] = True
    return row


def gate_controls() -> list[tuple[str, nx.Graph]]:
    controls: list[tuple[str, nx.Graph]] = []
    for G in nx.graph_atlas_g():
        if 2 <= len(G) <= 7 and nx.is_connected(G):
            controls.append((f"atlas:{graph6(G)}", G))
    controls += [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    controls += [
        ("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()),
        ("K3,3", nx.complete_bipartite_graph(3, 3)), ("K7", nx.complete_graph(7)),
    ]
    controls += [(f"K1,{n}", nx.star_graph(n)) for n in range(2, 8)]
    controls += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
                 for a, b in [(2, 3), (2, 4), (3, 4), (4, 4)]]
    return controls


def projective_plane_incidence(q: int) -> nx.Graph:
    G = nx.Graph()
    affine_points = [("P", x, y) for x in range(q) for y in range(q)]
    infinity_points = [("I", m) for m in range(q)] + [("I", "v")]
    slope_lines = [("L", m, b) for m in range(q) for b in range(q)]
    vertical_lines = [("V", a) for a in range(q)]
    infinity_line = ("Z",)
    G.add_nodes_from(affine_points + infinity_points, bipartite=0)
    G.add_nodes_from(slope_lines + vertical_lines + [infinity_line], bipartite=1)
    for x in range(q):
        for y in range(q):
            point = ("P", x, y)
            for m in range(q):
                G.add_edge(point, ("L", m, (y - m * x) % q))
            G.add_edge(point, ("V", x))
    for m in range(q):
        for b in range(q):
            G.add_edge(("I", m), ("L", m, b))
        G.add_edge(("I", m), infinity_line)
    for a in range(q):
        G.add_edge(("I", "v"), ("V", a))
    G.add_edge(("I", "v"), infinity_line)
    # The point-at-infinity labels deliberately mix integers and the marker
    # ``"v"``.  NetworkX's sorted ordering compares those tuple fields and is
    # therefore not defined on Python 3; insertion order is deterministic here.
    return nx.convert_node_labels_to_integers(G, ordering="default")


def subdivided_complete(n: int) -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(("v", i) for i in range(n))
    for i, j in itertools.combinations(range(n), 2):
        edge_node = ("e", i, j)
        G.add_edge(("v", i), edge_node)
        G.add_edge(edge_node, ("v", j))
    return nx.convert_node_labels_to_integers(G, ordering="sorted")


def named_bases() -> list[tuple[str, nx.Graph]]:
    tutte_coxeter = nx.LCF_graph(30, [-13, -9, 7, -7, 9, 13], 5)
    return [
        ("Petersen", nx.petersen_graph()),
        ("Heawood", nx.heawood_graph()),
        ("Moebius-Kantor", nx.moebius_kantor_graph()),
        ("Pappus", nx.pappus_graph()),
        ("Desargues", nx.desargues_graph()),
        ("Dodecahedron", nx.dodecahedral_graph()),
        ("Tutte-Coxeter", tutte_coxeter),
        ("Hoffman-Singleton", nx.hoffman_singleton_graph()),
    ]


def incidence_bases() -> list[tuple[str, nx.Graph]]:
    result = [(f"PG(2,{q})-Levi", projective_plane_incidence(q)) for q in (2, 3)]
    result += [(f"S(K{n})", subdivided_complete(n)) for n in range(5, 10)]
    return result


def edge_representatives(G: nx.Graph, limit: int = 8) -> list[tuple]:
    distances = dict(nx.all_pairs_shortest_path_length(G))
    buckets: dict[tuple, tuple] = {}
    for u, v in G.edges():
        common = len(set(G[u]) & set(G[v]))
        signature = (
            min(G.degree(u), G.degree(v)), max(G.degree(u), G.degree(v)), common,
            tuple(sorted(distances[u].values())), tuple(sorted(distances[v].values())),
        )
        edge = tuple(sorted((u, v), key=repr))
        buckets.setdefault(signature, edge)
    return [buckets[key] for key in sorted(buckets, key=repr)[:limit]]


def substitute_edge(G: nx.Graph, edge: tuple, length: int) -> tuple[nx.Graph, list]:
    H = G.copy()
    u, v = edge
    H.remove_edge(u, v)
    previous = u
    new_vertices = []
    for index in range(length - 1):
        node = max((x for x in H if isinstance(x, int)), default=-1) + 1
        H.add_edge(previous, node)
        new_vertices.append(node)
        previous = node
    H.add_edge(previous, v)
    return H, new_vertices


def attach_path(G: nx.Graph, root: object, length: int) -> nx.Graph:
    H = G.copy()
    previous = root
    for _ in range(length):
        node = max((x for x in H if isinstance(x, int)), default=-1) + 1
        H.add_edge(previous, node)
        previous = node
    return H


class LineageDeduper:
    def __init__(self) -> None:
        self.buckets: dict[str, list[nx.Graph]] = {}

    def add(self, G: nx.Graph) -> bool:
        digest = nx.weisfeiler_lehman_graph_hash(G)
        bucket = self.buckets.setdefault(digest, [])
        if any(nx.is_isomorphic(G, old) for old in bucket):
            return False
        bucket.append(G.copy())
        return True


def run_gate(solve_cap: float, outer_cap: float) -> None:
    start = time.monotonic()
    bad = timeouts = 0
    controls = gate_controls()
    emit({"kind": "phase_start", "phase": "gate", "rows": len(controls)})
    for index, (name, G) in enumerate(controls):
        if time.monotonic() - start > outer_cap:
            emit({"kind": "phase_stop", "phase": "gate", "reason": "outer_cap",
                  "completed": index, "bad": bad, "timeouts": timeouts})
            return
        row = evaluate(G, name, "gate", solve_cap, independently_verify=False)
        emit(row)
        bad += row.get("residual", 0) < 0
        timeouts += row["kind"] == "solve_timeout"
        if bad:
            emit({"kind": "summary", "phase": "gate", "verdict": "GATE_FAIL",
                  "completed": index + 1, "bad": bad, "timeouts": timeouts})
            return
    verdict = "PASS" if not timeouts else "GATE_INCOMPLETE"
    emit({"kind": "summary", "phase": "gate", "verdict": verdict,
          "completed": len(controls), "bad": bad, "timeouts": timeouts,
          "seconds": round(time.monotonic() - start, 6)})


def candidate_stream(base_filter: str | None = None):
    named = named_bases()
    named_names = {name for name, _ in named}
    for base_name, base in named + incidence_bases():
        if base_filter is not None and base_name != base_filter:
            continue
        base_stratum = "cage_base" if base_name in named_names else "incidence_base"
        yield base_name, base_stratum, base
        original_n = len(base)
        deduper = LineageDeduper()
        deduper.add(base)
        for edge_index, edge in enumerate(edge_representatives(base)):
            for length in (2, 3, 4):
                substituted, new_vertices = substitute_edge(base, edge, length)
                if len(substituted) - original_n > 6 or not deduper.add(substituted):
                    continue
                sub_name = f"{base_name}:edge{edge_index}:path{length}"
                yield sub_name, "clean_edge_substitution", substituted
                sites = list(edge) + new_vertices
                for site_index, site in enumerate(sites[:8]):
                    for height in (1, 2, 3):
                        attached = attach_path(substituted, site, height)
                        if len(attached) - original_n > 6 or not deduper.add(attached):
                            continue
                        yield (f"{sub_name}:site{site_index}:pendant{height}",
                               "sparse_shifted_attachment", attached)
        for site in sorted(base, key=repr)[:8]:
            for height in (1, 2, 3):
                attached = attach_path(base, site, height)
                if len(attached) - original_n <= 6 and deduper.add(attached):
                    yield (f"{base_name}:base-site{site}:pendant{height}",
                           "sparse_shifted_attachment", attached)


def gate_passed() -> bool:
    if not LEDGER.exists():
        return False
    for line in reversed(LEDGER.read_text(encoding="utf-8").splitlines()):
        row = json.loads(line)
        if row.get("phase") == "gate" and row.get("kind") == "summary":
            return row.get("verdict") == "PASS"
    return False


def run_search(solve_cap: float, outer_cap: float, candidate_cap: int,
               base_filter: str | None, skip: int) -> None:
    if not gate_passed():
        raise RuntimeError("latest ledger has no passing database-sanity gate")
    start = time.monotonic()
    stats = {"candidates": 0, "c4_rejected": 0, "timeouts": 0,
             "equalities": 0, "crossings": 0, "minimum_residual": None}
    emit({"kind": "phase_start", "phase": "search", "candidate_cap": candidate_cap,
          "base_filter": base_filter, "skip": skip})
    stream_index = 0
    for name, stratum, G in candidate_stream(base_filter):
        if stream_index < skip:
            stream_index += 1
            continue
        stream_index += 1
        if stats["candidates"] >= candidate_cap or time.monotonic() - start > outer_cap:
            break
        if len(G) > 56:
            emit({"kind": "rejected", "phase": "search", "name": name,
                  "stratum": stratum, "reason": "order_cap", "n": len(G)})
            continue
        witness = c4_witness(G)
        if witness is not None:
            stats["c4_rejected"] += 1
            emit({"kind": "rejected", "phase": "search", "name": name,
                  "stratum": stratum, "reason": "has_c4", "c4_witness": witness,
                  "n": len(G), "m": G.number_of_edges()})
            continue
        stats["candidates"] += 1
        row = evaluate(G, name, stratum, solve_cap)
        emit(row)
        if row["kind"] == "solve_timeout":
            stats["timeouts"] += 1
            continue
        residual = row["residual"]
        current = stats["minimum_residual"]
        stats["minimum_residual"] = residual if current is None else min(current, residual)
        stats["equalities"] += residual == 0
        if residual < 0 and row.get("independent_verified"):
            stats["crossings"] += 1
            emit({"kind": "verified_crossing", "phase": "search", **row})
            break
        if residual <= 0 and not row.get("independent_verified"):
            stats["timeouts"] += 1
    if stats["crossings"]:
        verdict = "CROSSING_VERIFIED"
    elif stats["candidates"] == 0:
        verdict = "NO_APPLICABLE_CANDIDATES"
    elif stats["timeouts"]:
        verdict = "HOLD_WITH_TIMEOUTS"
    else:
        verdict = "HOLD_BOUNDED"
    emit({"kind": "summary", "phase": "search", "verdict": verdict,
          "base_filter": base_filter, "skip": skip,
          **stats, "seconds": round(time.monotonic() - start, 6)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["gate", "search"])
    parser.add_argument("--solve-cap", type=float, default=3.0)
    parser.add_argument("--outer-cap", type=float, default=54.0)
    parser.add_argument("--candidate-cap", type=int, default=1500)
    parser.add_argument("--base", help="restrict search to one frozen base family")
    parser.add_argument("--skip", type=int, default=0,
                        help="skip this many deterministic stream candidates")
    args = parser.parse_args()
    if not (0 < args.solve_cap <= 55 and 0 < args.outer_cap < 60) or args.skip < 0:
        parser.error("caps violate frozen contract")
    check_contract()
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(59)
    emit({"kind": "session_start", "phase": args.phase,
          "solve_cap": args.solve_cap, "outer_cap": args.outer_cap})
    if args.phase == "gate":
        run_gate(args.solve_cap, args.outer_cap)
    else:
        run_search(args.solve_cap, args.outer_cap, min(args.candidate_cap, 1500),
                   args.base, args.skip)


if __name__ == "__main__":
    main()
