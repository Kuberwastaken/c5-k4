#!/usr/bin/env python3
"""Frozen Andrásfai-successor trial for current DeepMind Erdős 23."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_erdos23_andrasfai_ledger.jsonl"


def append(row: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, nodes=sorted(G), header=False).decode().strip()


def maxcut_exhaustive(G: nx.Graph) -> tuple[int, list[int]]:
    nodes = sorted(G)
    if not nodes:
        return 0, []
    anchor, rest = nodes[0], nodes[1:]
    best = -1
    best_side: list[int] = []
    for mask in range(1 << len(rest)):
        side = {anchor}
        side.update(rest[i] for i in range(len(rest)) if mask >> i & 1)
        value = sum((u in side) != (v in side) for u, v in G.edges())
        if value > best:
            best = value
            best_side = sorted(side)
    return best, best_side


def maxcut_milp(G: nx.Graph) -> tuple[int, list[int], dict]:
    nodes = sorted(G)
    edges = sorted(tuple(sorted(edge)) for edge in G.edges())
    n, m = len(nodes), len(edges)
    index = {v: i for i, v in enumerate(nodes)}
    matrix = lil_matrix((4 * m + 1, n + m), dtype=float)
    lower = np.full(4 * m + 1, -np.inf)
    upper = np.zeros(4 * m + 1)
    row = 0
    for j, (u, v) in enumerate(edges):
        iu, iv, iy = index[u], index[v], n + j
        for cu, cv, cy, bound in ((-1, -1, 1, 0), (1, 1, 1, 2), (1, -1, -1, 0), (-1, 1, -1, 0)):
            matrix[row, iu], matrix[row, iv], matrix[row, iy] = cu, cv, cy
            upper[row] = bound
            row += 1
    # Break complement symmetry by fixing the least vertex on side zero.
    matrix[row, index[nodes[0]]] = 1
    upper[row] = 0
    objective = np.zeros(n + m)
    objective[n:] = -1
    result = milp(
        c=objective,
        integrality=np.ones(n + m),
        bounds=Bounds(np.zeros(n + m), np.ones(n + m)),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"time_limit": 55.0, "mip_rel_gap": 0.0},
    )
    if not result.success or result.mip_gap != 0:
        raise RuntimeError(f"maxcut MILP incomplete: {result.status} {result.message} gap={result.mip_gap}")
    side = [v for v in nodes if result.x[index[v]] > 0.5]
    value = sum((u in side) != (v in side) for u, v in edges)
    return value, side, {"mip_gap": float(result.mip_gap), "mip_node_count": int(result.mip_node_count)}


def replay_cut(G: nx.Graph, side: list[int]) -> dict:
    S = set(side)
    crossing = [sorted((u, v)) for u, v in G.edges() if (u in S) != (v in S)]
    deleted = [sorted((u, v)) for u, v in G.edges() if (u in S) == (v in S)]
    H = nx.Graph()
    H.add_nodes_from(G)
    H.add_edges_from(crossing)
    return {
        "cut": len(crossing),
        "deleted_count": len(deleted),
        "deleted_edges": deleted,
        "kept_bipartite": nx.is_bipartite(H),
    }


def triangle_free_direct(G: nx.Graph) -> bool:
    for u in G:
        neighbors = sorted(G[u])
        for i, v in enumerate(neighbors):
            for w in neighbors[i + 1 :]:
                if G.has_edge(v, w):
                    return False
    return True


def c5() -> nx.Graph:
    return nx.cycle_graph(5)


def andrasfai(k: int) -> nx.Graph:
    n = 3 * k - 1
    generators = {1 + 3 * i for i in range(k)}
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in range(u + 1, n):
            if (v - u) % n in generators or (u - v) % n in generators:
                G.add_edge(u, v)
    return G


def independent_blowup(Q: nx.Graph, bag: int) -> nx.Graph:
    G = nx.Graph()
    for q in sorted(Q):
        G.add_nodes_from(q * bag + a for a in range(bag))
    for u, v in Q.edges():
        for a in range(bag):
            for b in range(bag):
                G.add_edge(u * bag + a, v * bag + b)
    return G


def lift_side(quotient_side: list[int], bag: int) -> list[int]:
    return [q * bag + a for q in quotient_side for a in range(bag)]


def evaluate_blowup(Q: nx.Graph, bag: int) -> dict:
    G = independent_blowup(Q, bag)
    qcut, qside = maxcut_exhaustive(Q)
    side = lift_side(qside, bag)
    replay = replay_cut(G, side)
    beta = G.number_of_edges() - replay["cut"]
    parameter = G.number_of_nodes() // 5
    assert replay["cut"] == bag * bag * qcut
    assert beta == bag * bag * (Q.number_of_edges() - qcut)
    assert replay["kept_bipartite"]
    return {
        "graph6": graph6(G),
        "graph6_sha256": hashlib.sha256(graph6(G).encode()).hexdigest(),
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "parameter": parameter,
        "bound": parameter * parameter,
        "triangle_free": triangle_free_direct(G),
        "quotient_n": Q.number_of_nodes(),
        "quotient_m": Q.number_of_edges(),
        "quotient_maxcut": qcut,
        "quotient_side": qside,
        "lifted_side": side,
        "maxcut": replay["cut"],
        "deleted_count": replay["deleted_count"],
        "deleted_edges": replay["deleted_edges"],
        "kept_bipartite": replay["kept_bipartite"],
        "slack": parameter * parameter - beta,
    }


def gate() -> dict:
    upstream = Path("/Users/kuber.mehta/Projects/formal-conjectures")
    commit = subprocess.run(
        ["git", "rev-parse", "upstream/main"], cwd=upstream, check=True,
        capture_output=True, text=True, timeout=10,
    ).stdout.strip()
    source = subprocess.run(
        ["git", "show", "upstream/main:FormalConjectures/ErdosProblems/23.lean"],
        cwd=upstream, check=True, capture_output=True, text=True, timeout=10,
    ).stdout
    blob = subprocess.run(
        ["git", "hash-object", "--stdin"], input=source, check=True,
        capture_output=True, text=True, timeout=10,
    ).stdout.strip()
    source_ok = (
        commit == "d16e05aded22b8c467a0a27c14b2311f53185006"
        and blob == "346d29667313a32382bbf42b87588d53bb208400"
        and "@[category research open, AMS 5]\ntheorem erdos_23" in source
        and "G.CliqueFree 3" in source
        and "Fintype.card V = 5 * n" in source
    )
    atlas = []
    failures = []
    for G0 in nx.graph_atlas_g():
        if G0.number_of_nodes() != 5 or not nx.is_connected(G0):
            continue
        G = nx.convert_node_labels_to_integers(G0, ordering="sorted")
        if not triangle_free_direct(G):
            continue
        cut, side = maxcut_exhaustive(G)
        replay = replay_cut(G, side)
        beta = G.number_of_edges() - cut
        row = {"graph6": graph6(G), "m": G.number_of_edges(), "maxcut": cut, "beta": beta, "side": side}
        atlas.append(row)
        if beta > 1 or not replay["kept_bipartite"]:
            failures.append(row)

    balanced = []
    for bag in range(1, 6):
        row = evaluate_blowup(c5(), bag)
        row["bag"] = bag
        balanced.append(row)
        if row["slack"] != 0 or not row["triangle_free"]:
            failures.append({"balanced_bag": bag, "row": row})

    P = nx.petersen_graph()
    pcut, pside = maxcut_exhaustive(P)
    prep = replay_cut(P, pside)
    petersen = {"graph6": graph6(P), "n": 10, "m": 15, "maxcut": pcut, "beta": 15 - pcut, "bound": 4, "side": pside}
    if petersen["beta"] > 4 or not prep["kept_bipartite"]:
        failures.append({"petersen": petersen})

    bipartite = []
    for a, b in ((1, 4), (2, 3), (4, 6), (5, 5)):
        G = nx.complete_bipartite_graph(a, b)
        if G.number_of_nodes() % 5:
            continue
        cut, side = maxcut_exhaustive(G)
        row = {"name": f"K{a},{b}", "n": G.number_of_nodes(), "m": G.number_of_edges(), "maxcut": cut, "beta": G.number_of_edges() - cut, "side": side}
        bipartite.append(row)
        if row["beta"] != 0:
            failures.append(row)

    if not source_ok:
        failures.append({"source_gate": {"commit": commit, "blob": blob}})
    result = {
        "event": "DB_GATE",
        "status": "PASS" if not failures else "FAIL",
        "upstream_commit": commit,
        "source_blob": blob,
        "source_gate_replayed": source_ok,
        "source_status": "research open",
        "atlas_connected_triangle_free_order5": len(atlas),
        "atlas": atlas,
        "balanced_equality_controls": balanced,
        "petersen": petersen,
        "complete_bipartite_controls": bipartite,
        "failures": failures,
        "candidate_evaluations": 0,
        "public_action": False,
    }
    append(result)
    return result


def gate_passed() -> bool:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    gates = [r for r in rows if r.get("event") == "DB_GATE"]
    return bool(gates and gates[-1].get("status") == "PASS" and gates[-1].get("source_gate_replayed"))


def development_v2() -> dict:
    if not gate_passed():
        row = {"event": "VERDICT_V2", "status": "DB_SANITY_REJECT", "public_action": False}
        append(row)
        return row
    k, bag = 14, 5
    Q = andrasfai(k)
    qcut, qside, solver = maxcut_milp(Q)
    G = independent_blowup(Q, bag)
    side = lift_side(qside, bag)
    replay = replay_cut(G, side)
    parameter = G.number_of_nodes() // 5
    beta = G.number_of_edges() - replay["cut"]
    row = {
        "event": "GRAPH_EVALUATED_V2",
        "k": k,
        "graph6": graph6(G),
        "graph6_sha256": hashlib.sha256(graph6(G).encode()).hexdigest(),
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "parameter": parameter,
        "bound": parameter * parameter,
        "triangle_free": triangle_free_direct(G),
        "quotient_n": Q.number_of_nodes(),
        "quotient_m": Q.number_of_edges(),
        "quotient_maxcut": qcut,
        "quotient_side": qside,
        "lifted_side": side,
        "maxcut": replay["cut"],
        "deleted_count": replay["deleted_count"],
        "deleted_edges_sha256": hashlib.sha256(json.dumps(replay["deleted_edges"], separators=(",", ":")).encode()).hexdigest(),
        "kept_bipartite": replay["kept_bipartite"],
        "slack": parameter * parameter - beta,
        "solver": solver,
        "candidate": parameter * parameter - beta < 0,
        "public_action": False,
    }
    if not row["triangle_free"] or not row["kept_bipartite"] or row["n"] != 5 * parameter:
        raise RuntimeError("v2 premise/witness replay failed")
    append(row)
    verdict = {
        "event": "VERDICT_V2",
        "status": "CANDIDATE_ADVERSARIAL" if row["candidate"] else "HOLD_BOUNDED",
        "development_graphs": 1,
        "parameter": 41,
        "known_finite_domain_excluded": True,
        "slack": row["slack"],
        "independent_audit_required": True,
        "public_action": False,
    }
    append(verdict)
    return verdict


def development() -> dict:
    if not gate_passed():
        row = {"event": "VERDICT", "status": "DB_SANITY_REJECT", "public_action": False}
        append(row)
        return row
    rows = []
    for k in (3, 4, 5, 6):
        Q = andrasfai(k)
        row = {"event": "GRAPH_EVALUATED", "k": k, **evaluate_blowup(Q, 5), "public_action": False}
        if not row["triangle_free"] or row["n"] != 5 * row["parameter"]:
            raise RuntimeError("premise replay failed")
        row["candidate"] = row["slack"] < 0
        append(row)
        rows.append(row)
    candidates = [r for r in rows if r["candidate"]]
    result = {
        "event": "VERDICT",
        "status": "CANDIDATE_ADVERSARIAL" if candidates else "HOLD_BOUNDED",
        "development_graphs": len(rows),
        "orders": [r["n"] for r in rows],
        "slacks": [r["slack"] for r in rows],
        "candidate_count": len(candidates),
        "candidate_graph6": [r["graph6"] for r in candidates],
        "independent_audit_required": True,
        "public_action": False,
    }
    append(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("gate", "development", "development-v2"))
    args = parser.parse_args()
    if args.phase == "gate":
        result = gate()
    elif args.phase == "development":
        result = development()
    else:
        result = development_v2()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
