#!/usr/bin/env python3
"""Frozen Method v0.8 trial for arXiv:2607.06396, Conjecture 4."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_arxiv2607_alontarsi_petersen_subdivision_contract.json"
ADDENDUM = ROOT / "results/expansion/prospective_arxiv2607_alontarsi_petersen_subdivision_oracle_addendum.json"
LEDGER = ROOT / "results/expansion/prospective_arxiv2607_alontarsi_petersen_subdivision_ledger.jsonl"
SOLVER_LIMIT = 40.0


def canonical_edges(graph: nx.Graph) -> list[tuple[int, int]]:
    return sorted((min(u, v), max(u, v)) for u, v in graph.edges())


def cycles_as_edge_sets(graph: nx.Graph) -> list[frozenset[tuple[int, int]]]:
    found: set[frozenset[tuple[int, int]]] = set()
    for cycle in nx.simple_cycles(graph):
        if len(cycle) < 3:
            continue
        edges = frozenset(
            (min(cycle[i], cycle[(i + 1) % len(cycle)]), max(cycle[i], cycle[(i + 1) % len(cycle)]))
            for i in range(len(cycle))
        )
        found.add(edges)
    return sorted(found, key=lambda x: (len(x), sorted(x)))


def exact_scc(graph: nx.Graph) -> dict:
    edges = canonical_edges(graph)
    if not edges:
        return {"scc": 0, "cycle_count": 0, "chosen_cycles": [], "solver": "empty"}
    cycles = cycles_as_edge_sets(graph)
    if not cycles:
        raise RuntimeError("applicable graph has edges but no cycles")
    index = {e: i for i, e in enumerate(edges)}
    cover = np.zeros((len(edges), len(cycles)), dtype=float)
    for j, cycle in enumerate(cycles):
        for edge in cycle:
            cover[index[edge], j] = 1.0
    objective = np.asarray([len(c) for c in cycles], dtype=float)
    result = milp(
        objective,
        integrality=np.ones(len(cycles)),
        bounds=Bounds(np.zeros(len(cycles)), np.ones(len(cycles))),
        constraints=LinearConstraint(cover, np.ones(len(edges)), np.full(len(edges), np.inf)),
        options={"time_limit": SOLVER_LIMIT, "mip_rel_gap": 0.0},
    )
    if not result.success or result.fun is None or result.x is None:
        raise TimeoutError(f"MILP status={result.status}: {result.message}")
    rounded = int(round(float(result.fun)))
    if abs(float(result.fun) - rounded) > 1e-7:
        raise RuntimeError(f"nonintegral objective {result.fun}")
    chosen = [sorted(cycles[j]) for j, value in enumerate(result.x) if value > 0.5]
    covered = {edge for cycle in chosen for edge in cycle}
    if covered != set(edges) or sum(len(c) for c in chosen) != rounded:
        raise RuntimeError("returned cover failed exact replay")
    return {
        "scc": rounded,
        "cycle_count": len(cycles),
        "chosen_cycles": chosen,
        "solver": "scipy.optimize.milp/HiGHS",
        "mip_gap": float(getattr(result, "mip_gap", 0.0) or 0.0),
    }


def independent_dp_scc(graph: nx.Graph) -> int:
    """Independent oracle: edge-subset cycles plus exact mask DP."""
    edges = canonical_edges(graph)
    edge_count = len(edges)
    if edge_count == 0:
        return 0
    cycles: list[int] = []
    for mask in range(1, 1 << edge_count):
        degrees: dict[int, int] = {}
        selected = []
        for i, (u, v) in enumerate(edges):
            if mask & (1 << i):
                selected.append((u, v))
                degrees[u] = degrees.get(u, 0) + 1
                degrees[v] = degrees.get(v, 0) + 1
        if len(selected) < 3 or any(value != 2 for value in degrees.values()):
            continue
        auxiliary = nx.Graph()
        auxiliary.add_edges_from(selected)
        if nx.is_connected(auxiliary):
            cycles.append(mask)
    full = (1 << edge_count) - 1
    infinity = 10 ** 9
    dp = [infinity] * (1 << edge_count)
    dp[0] = 0
    for covered in range(1 << edge_count):
        if dp[covered] == infinity:
            continue
        for cycle in cycles:
            combined = covered | cycle
            candidate = dp[covered] + bin(cycle).count("1")
            if candidate < dp[combined]:
                dp[combined] = candidate
    if dp[full] == infinity:
        raise RuntimeError("independent oracle found no cover")
    return dp[full]


def append(row: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()


def applicable(graph: nx.Graph) -> bool:
    return graph.number_of_nodes() >= 2 and nx.is_connected(graph) and graph.number_of_edges() > 0 and not list(nx.bridges(graph))


def graph_record(graph: nx.Graph) -> dict:
    edges = canonical_edges(graph)
    payload = json.dumps(edges, separators=(",", ":"))
    return {
        "n": graph.number_of_nodes(),
        "m": graph.number_of_edges(),
        "edges": edges,
        "graph6": nx.to_graph6_bytes(graph, header=False).decode().strip(),
        "edge_digest_sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }


def solve_row(kind: str, name: str, graph: nx.Graph, **extra: object) -> dict:
    base = {"kind": kind, "name": name, "applicable": applicable(graph), **graph_record(graph), **extra}
    if not base["applicable"]:
        return {**base, "verdict": "NOT_APPLICABLE"}
    started = time.monotonic()
    answer = exact_scc(graph)
    elapsed = time.monotonic() - started
    residual = 7 * graph.number_of_edges() - 5 * answer["scc"]
    return {
        **base,
        **answer,
        "residual": residual,
        "elapsed_seconds": round(elapsed, 6),
        "verdict": "HOLD" if residual >= 0 else "VIOLATED",
    }


def named_controls() -> list[tuple[str, nx.Graph]]:
    values: list[tuple[str, nx.Graph]] = []
    values += [(f"C{n}", nx.cycle_graph(n)) for n in range(5, 10)]
    values += [("P7", nx.path_graph(7)), ("Petersen", nx.petersen_graph()), ("K3,3", nx.complete_bipartite_graph(3, 3)), ("K7", nx.complete_graph(7))]
    values += [(f"K1,{n}", nx.star_graph(n)) for n in range(2, 7)]
    values += [("K2,3", nx.complete_bipartite_graph(2, 3)), ("K2,4", nx.complete_bipartite_graph(2, 4))]
    return values


def run_gate(contract_sha: str) -> None:
    if LEDGER.exists():
        raise SystemExit(f"refusing to overwrite existing ledger: {LEDGER}")
    append({"kind": "run_start", "phase": "database_gate", "contract_sha256": contract_sha})
    c5 = solve_row("microfixture", "C5", nx.cycle_graph(5))
    petersen = solve_row("microfixture", "Petersen", nx.petersen_graph())
    append(c5)
    append(petersen)
    if (c5.get("scc"), c5.get("residual")) != (5, 10) or (petersen.get("scc"), petersen.get("residual")) != (21, 0):
        append({"kind": "gate_summary", "outcome": "GATE_FAIL", "reason": "microfixture mismatch"})
        raise SystemExit(2)

    applicable_count = 0
    for index, graph in enumerate(nx.graph_atlas_g()):
        if not (2 <= graph.number_of_nodes() <= 7 and nx.is_connected(graph)):
            continue
        row = solve_row("atlas_control", f"atlas_{index}", graph, atlas_index=index)
        append(row)
        if row["applicable"]:
            applicable_count += 1
            if row.get("residual", -1) < 0:
                append({"kind": "gate_summary", "outcome": "CORRUPT_OR_ERRATUM", "witness": f"atlas_{index}"})
                raise SystemExit(3)
    for name, graph in named_controls():
        row = solve_row("named_control", name, graph)
        append(row)
        if row["applicable"] and row.get("residual", -1) < 0:
            append({"kind": "gate_summary", "outcome": "CORRUPT_OR_ERRATUM", "witness": name})
            raise SystemExit(3)
    append({"kind": "gate_summary", "outcome": "PASS", "applicable_atlas_graphs": applicable_count})


def subdivided_petersen(t: int) -> tuple[nx.Graph, dict]:
    graph = nx.petersen_graph()
    if not graph.has_edge(0, 1):
        raise RuntimeError("frozen labelled edge (0,1) absent")
    graph.remove_edge(0, 1)
    previous = 0
    path = [0]
    for offset in range(t):
        vertex = 10 + offset
        graph.add_edge(previous, vertex)
        path.append(vertex)
        previous = vertex
    graph.add_edge(previous, 1)
    path.append(1)
    roles = {
        "original_vertices": {str(i): f"p{i}" for i in range(10)},
        "subdivision_vertices": {str(10 + i): f"x{i + 1}" for i in range(t)},
        "subdivision_path": path,
    }
    return graph, roles


def ledger_has_gate_pass(contract_sha: str) -> bool:
    if not LEDGER.exists():
        return False
    rows = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows[0].get("contract_sha256") == contract_sha and any(row.get("kind") == "gate_summary" and row.get("outcome") == "PASS" for row in rows)


def run_oracle_audit(contract_sha: str) -> None:
    if not ledger_has_gate_pass(contract_sha):
        raise SystemExit("primary database gate has not passed")
    existing = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]
    unfinished = sum(row.get("kind") == "phase_start" and row.get("phase") == "independent_oracle_audit" for row in existing) - sum(row.get("kind") == "oracle_audit_summary" for row in existing)
    if unfinished > 0:
        append({"kind": "oracle_audit_attempt_summary", "outcome": "PROTOCOL_DEVIATION", "reason": "Python runtime lacks int.bit_count; stopped before first oracle row", "preserved_attempts": unfinished})
    addendum_sha = hashlib.sha256(ADDENDUM.read_bytes()).hexdigest()
    append({"kind": "phase_start", "phase": "independent_oracle_audit", "contract_sha256": contract_sha, "addendum_sha256": addendum_sha})
    primary_rows = {
        row["name"]: row
        for row in (json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip())
        if row.get("kind") in {"atlas_control", "microfixture"}
    }
    mismatches = []
    audited = 0
    for index, graph in enumerate(nx.graph_atlas_g()):
        name = f"atlas_{index}"
        if not (2 <= graph.number_of_nodes() <= 6 and applicable(graph)):
            continue
        value = independent_dp_scc(graph)
        primary = primary_rows[name]["scc"]
        row = {"kind": "oracle_audit", "name": name, "n": graph.number_of_nodes(), "m": graph.number_of_edges(), "primary_scc": primary, "independent_scc": value, "match": primary == value}
        append(row)
        audited += 1
        if primary != value:
            mismatches.append(name)
    for name, graph, expected in (("C5_oracle", nx.cycle_graph(5), 5), ("Petersen_oracle", nx.petersen_graph(), 21)):
        value = independent_dp_scc(graph)
        row = {"kind": "oracle_audit", "name": name, "n": graph.number_of_nodes(), "m": graph.number_of_edges(), "expected_scc": expected, "independent_scc": value, "match": expected == value}
        append(row)
        audited += 1
        if expected != value:
            mismatches.append(name)
    append({"kind": "oracle_audit_summary", "outcome": "PASS" if not mismatches else "GATE_FAIL", "audited": audited, "mismatches": mismatches, "addendum_sha256": addendum_sha})
    if mismatches:
        raise SystemExit(5)


def ledger_has_oracle_pass() -> bool:
    if not LEDGER.exists():
        return False
    return any(
        row.get("kind") == "oracle_audit_summary" and row.get("outcome") == "PASS"
        for row in (json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip())
    )


def run_family(contract_sha: str) -> None:
    if not ledger_has_gate_pass(contract_sha):
        raise SystemExit("database gate has not passed under this contract")
    if not ledger_has_oracle_pass():
        raise SystemExit("independent oracle audit has not passed")
    append({"kind": "phase_start", "phase": "family", "contract_sha256": contract_sha})
    mismatches = []
    for t in range(1, 13):
        graph, roles = subdivided_petersen(t)
        roles_payload = json.dumps(roles, sort_keys=True, separators=(",", ":"))
        row = solve_row(
            "family",
            f"Petersen_subdivide_0_1_t{t}",
            graph,
            t=t,
            roles=roles,
            role_digest_sha256=hashlib.sha256(roles_payload.encode()).hexdigest(),
            predicted_m=15 + t,
            predicted_scc=21 + t,
            predicted_residual=2 * t,
        )
        row["prediction_match"] = (
            row.get("m") == row["predicted_m"]
            and row.get("scc") == row["predicted_scc"]
            and row.get("residual") == row["predicted_residual"]
            and row.get("applicable") is True
        )
        append(row)
        if not row["prediction_match"]:
            mismatches.append(t)
    outcome = "THEOREM_SHADOW" if not mismatches else "GATE_FAIL"
    append({
        "kind": "family_summary",
        "outcome": outcome,
        "prediction_confirmed": not mismatches,
        "rows": 12,
        "mismatched_t": mismatches,
        "proof_obstruction": "Every cover suppresses to a Petersen cover, so scc>=21+t. Petersen edge-transitivity transports a 21-cover with a singly covered edge to (0,1), giving scc<=21+t.",
    })
    if mismatches:
        raise SystemExit(4)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("gate", "oracle-audit", "family"))
    args = parser.parse_args()
    contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if args.phase == "gate":
        run_gate(contract_sha)
    elif args.phase == "oracle-audit":
        run_oracle_audit(contract_sha)
    else:
        run_family(contract_sha)


if __name__ == "__main__":
    main()
