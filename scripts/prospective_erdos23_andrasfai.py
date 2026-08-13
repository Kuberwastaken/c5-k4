#!/usr/bin/env python3
"""Frozen Andrásfai-successor trial for current DeepMind Erdős 23."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import networkx as nx


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

    result = {
        "event": "DB_GATE",
        "status": "PASS" if not failures else "FAIL",
        "upstream_commit": "d16e05aded22b8c467a0a27c14b2311f53185006",
        "source_blob": "346d29667313a32382bbf42b87588d53bb208400",
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
    return bool(gates and gates[-1].get("status") == "PASS")


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
    parser.add_argument("--phase", required=True, choices=("gate", "development"))
    args = parser.parse_args()
    result = gate() if args.phase == "gate" else development()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
