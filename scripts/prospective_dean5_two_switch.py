#!/usr/bin/env python3
"""Frozen Dean k=5 two-switch trial.

Run the database gate first with ``--phase gate``.  Development refuses to
run unless the append-only ledger contains a passing gate record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_dean5_two_switch_ledger.jsonl"


def append(row: dict) -> None:
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def graph6(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, nodes=sorted(G), header=False).decode().strip()


def c5k2() -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(range(10))
    for i in range(5):
        G.add_edge(2 * i, 2 * i + 1)
        for a in range(2):
            for b in range(2):
                G.add_edge(2 * i + a, 2 * ((i + 1) % 5) + b)
    return G


def find_cycle(G: nx.Graph, length: int) -> list[int] | None:
    """Find a simple undirected cycle with the requested edge length."""
    if length < 3 or length > G.number_of_nodes():
        return None
    nodes = sorted(G)
    for start in nodes:
        # Requiring start to be the least cycle vertex removes rotations and
        # is only a search optimization, not part of the witness checker.
        path = [start]
        used = {start}

        def dfs(v: int) -> list[int] | None:
            if len(path) == length:
                return list(path) if G.has_edge(v, start) else None
            for w in sorted(G[v]):
                if w <= start or w in used:
                    continue
                used.add(w)
                path.append(w)
                ans = dfs(w)
                if ans is not None:
                    return ans
                path.pop()
                used.remove(w)
            return None

        answer = dfs(start)
        if answer is not None:
            return answer
    return None


def replay_cycle(G: nx.Graph, cycle: list[int], divisor: int = 5) -> bool:
    """Independent direct replay, deliberately separate from DFS state."""
    if len(cycle) < 3 or len(cycle) % divisor != 0:
        return False
    if len(set(cycle)) != len(cycle):
        return False
    return all(G.has_edge(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle)))


def min_degree(G: nx.Graph) -> int:
    return min((degree for _, degree in G.degree()), default=0)


def valid_switch_outputs(G: nx.Graph):
    edges = sorted(tuple(sorted(e)) for e in G.edges())
    for e1, e2 in combinations(edges, 2):
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) != 4:
            continue
        for replacement in (((a, c), (b, d)), ((a, d), (b, c))):
            r1, r2 = (tuple(sorted(replacement[0])), tuple(sorted(replacement[1])))
            if G.has_edge(*r1) or G.has_edge(*r2):
                continue
            H = G.copy()
            H.remove_edges_from((e1, e2))
            H.add_edges_from((r1, r2))
            yield (e1, e2, tuple(sorted((r1, r2)))), H


def atlas_gate() -> dict:
    checked = 0
    eligible = 0
    witnesses = []
    failures = []
    for G0 in nx.graph_atlas_g():
        n = G0.number_of_nodes()
        if not (2 <= n <= 7) or not nx.is_connected(G0):
            continue
        checked += 1
        G = nx.convert_node_labels_to_integers(G0, ordering="sorted")
        if min_degree(G) < 5:
            continue
        eligible += 1
        witness = find_cycle(G, 5)
        if witness is None or not replay_cycle(G, witness):
            failures.append(graph6(G))
        else:
            witnesses.append({"graph6": graph6(G), "n": n, "min_degree": min_degree(G), "cycle": witness})

    B = c5k2()
    base5 = find_cycle(B, 5)
    base10 = find_cycle(B, 10)
    base_ok = (
        min_degree(B) == 5
        and base5 is not None
        and base10 is not None
        and replay_cycle(B, base5)
        and replay_cycle(B, base10)
    )
    status = "PASS" if not failures and base_ok else "FAIL"
    row = {
        "event": "DB_GATE",
        "status": status,
        "source_status": "research open",
        "upstream_commit": "d16e05aded22b8c467a0a27c14b2311f53185006",
        "source_blob": "4a65620a7ff37a6d3f005f6db3705e26d793b3cf",
        "atlas_connected_orders_2_through_7": checked,
        "atlas_eligible_min_degree_ge_5": eligible,
        "atlas_witnesses": witnesses,
        "atlas_failures": failures,
        "base": {
            "graph6": graph6(B),
            "n": 10,
            "m": B.number_of_edges(),
            "min_degree": min_degree(B),
            "cycle5": base5,
            "cycle10": base10,
        },
        "candidate_evaluations": 0,
        "public_action": False,
    }
    append(row)
    return row


def gate_passed() -> bool:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    gates = [row for row in rows if row.get("event") == "DB_GATE"]
    return bool(gates and gates[-1].get("status") == "PASS")


def exact_iso_class_count(graphs: list[nx.Graph]) -> int:
    """Invariant buckets followed by exact VF2 comparisons within each bucket."""
    buckets: dict[str, list[nx.Graph]] = defaultdict(list)
    for G in graphs:
        # Plain WL cannot separate regular graphs at all.  Per-vertex triangle
        # counts are isomorphism-invariant and make a much sharper initial
        # colouring; exact VF2 still decides every collision.
        nx.set_node_attributes(G, nx.triangles(G), "triangles")
        key = nx.weisfeiler_lehman_graph_hash(G, node_attr="triangles", iterations=10)
        buckets[key].append(G)
    total = 0
    for bucket in buckets.values():
        representatives: list[nx.Graph] = []
        for G in bucket:
            if not any(nx.is_isomorphic(G, H) for H in representatives):
                representatives.append(G)
        total += len(representatives)
    return total


def summarize_completed_records() -> dict:
    """Finish a capped run after all graph rows were durably written."""
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
    enumerated = {row["depth"]: row for row in rows if row.get("event") == "DEPTH_ENUMERATED"}
    evaluated = [row for row in rows if row.get("event") == "GRAPH_EVALUATED"]
    by_depth: dict[int, list[dict]] = defaultdict(list)
    for row in evaluated:
        by_depth[row["depth"]].append(row)
    expected = {depth: enumerated[depth]["unique_labelled_graphs"] for depth in (1, 2)}
    observed = {depth: len(by_depth[depth]) for depth in (1, 2)}
    append({
        "event": "PROCESS_CAP_RECOVERY",
        "status": "EVALUATIONS_COMPLETE_SUMMARY_INCOMPLETE",
        "prior_process_cap_seconds": 60,
        "expected_graph_rows": expected,
        "observed_graph_rows": observed,
        "scope_change": False,
        "public_action": False,
    })
    if observed != expected:
        verdict = {
            "event": "VERDICT",
            "status": "INCONCLUSIVE",
            "reason": "durable graph-row counts do not match frozen enumeration",
            "expected": expected,
            "observed": observed,
            "public_action": False,
        }
        append(verdict)
        return verdict

    depth_summaries = {}
    histogram = Counter()
    all_candidates = []
    for depth in (1, 2):
        graphs = []
        seen = set()
        for row in by_depth[depth]:
            g6 = row["graph6"]
            if g6 in seen:
                verdict = {"event": "VERDICT", "status": "INCONCLUSIVE", "reason": "duplicate graph row", "depth": depth, "graph6": g6, "public_action": False}
                append(verdict)
                return verdict
            seen.add(g6)
            G = nx.from_graph6_bytes(g6.encode())
            graphs.append(G)
            if min_degree(G) != row["min_degree"]:
                raise RuntimeError("minimum-degree replay mismatch")
            if row["cycle5"] is not None and not replay_cycle(G, row["cycle5"]):
                raise RuntimeError("5-cycle replay mismatch")
            if row["cycle10"] is not None and not replay_cycle(G, row["cycle10"]):
                raise RuntimeError("10-cycle replay mismatch")
            histogram[(depth, row["profile"])] += 1
            if row["candidate"]:
                all_candidates.append(g6)
        iso_count = exact_iso_class_count(graphs)
        depth_summaries[str(depth)] = {
            "unique_labelled_graphs": len(graphs),
            "exact_isomorphism_classes": iso_count,
            "candidates": sum(bool(row["candidate"]) for row in by_depth[depth]),
        }
        append({"event": "RECOVERED_DEPTH_COMPLETE", "depth": depth, **depth_summaries[str(depth)]})

    verdict = {
        "event": "VERDICT",
        "status": "CANDIDATE" if all_candidates else "HOLD_BOUNDED",
        "development_graphs": sum(observed.values()),
        "depth_summaries": depth_summaries,
        "profile_histogram": {f"d{d}:{p}": n for (d, p), n in sorted(histogram.items())},
        "candidate_count": len(all_candidates),
        "candidate_graph6": all_candidates,
        "independent_audit_required": True,
        "recovered_after_summary_cap": True,
        "public_action": False,
    }
    append(verdict)
    return verdict


def development() -> dict:
    if not gate_passed():
        row = {"event": "VERDICT", "status": "DB_SANITY_REJECT", "reason": "no passing DB_GATE", "public_action": False}
        append(row)
        return row

    base = c5k2()
    levels: dict[int, dict[str, tuple[nx.Graph, dict | None]]] = {0: {graph6(base): (base, None)}}
    for depth in (1, 2):
        labelled: dict[str, tuple[nx.Graph, dict]] = {}
        generated = 0
        for parent_g6, (G, _) in sorted(levels[depth - 1].items()):
            for switch, H in valid_switch_outputs(G):
                generated += 1
                g6 = graph6(H)
                if g6 not in labelled:
                    labelled[g6] = (
                        H,
                        {"parent_graph6": parent_g6, "removed": switch[:2], "added": switch[2]},
                    )
        levels[depth] = labelled
        append({
            "event": "DEPTH_ENUMERATED",
            "depth": depth,
            "raw_valid_switches": generated,
            "unique_labelled_graphs": len(labelled),
            "public_action": False,
        })

    total = 0
    candidates: list[dict] = []
    hist = Counter()
    depth_summaries = {}
    for depth in (1, 2):
        graphs_for_iso = []
        depth_candidates = 0
        for index, (g6, (G, provenance)) in enumerate(sorted(levels[depth].items()), start=1):
            total += 1
            graphs_for_iso.append(G)
            md = min_degree(G)
            cycle5 = find_cycle(G, 5)
            cycle10 = find_cycle(G, 10)
            replay5 = cycle5 is not None and replay_cycle(G, cycle5)
            replay10 = cycle10 is not None and replay_cycle(G, cycle10)
            if cycle5 is not None and not replay5 or cycle10 is not None and not replay10:
                append({"event": "EXACTNESS_FAILURE", "depth": depth, "graph6": g6})
                raise RuntimeError("cycle witness replay failed")
            profile = f"c5={int(cycle5 is not None)},c10={int(cycle10 is not None)}"
            hist[(depth, profile)] += 1
            candidate = md >= 5 and cycle5 is None and cycle10 is None
            if candidate:
                depth_candidates += 1
            row = {
                "event": "GRAPH_EVALUATED",
                "depth": depth,
                "index_at_depth": index,
                "graph6": g6,
                "graph6_sha256": hashlib.sha256(g6.encode()).hexdigest(),
                "n": G.number_of_nodes(),
                "m": G.number_of_edges(),
                "min_degree": md,
                "cycle5": cycle5,
                "cycle10": cycle10,
                "profile": profile,
                "candidate": candidate,
                "provenance": provenance,
                "public_action": False,
            }
            append(row)
            if candidate:
                candidates.append(row)
            if index % 100 == 0:
                append({"event": "CHECKPOINT", "depth": depth, "completed": index, "candidates": depth_candidates})

        iso_count = exact_iso_class_count(graphs_for_iso)
        depth_summaries[str(depth)] = {
            "unique_labelled_graphs": len(graphs_for_iso),
            "exact_isomorphism_classes": iso_count,
            "candidates": depth_candidates,
        }
        append({"event": "DEPTH_COMPLETE", "depth": depth, **depth_summaries[str(depth)]})

    verdict = "CANDIDATE" if candidates else "HOLD_BOUNDED"
    row = {
        "event": "VERDICT",
        "status": verdict,
        "development_graphs": total,
        "depth_summaries": depth_summaries,
        "profile_histogram": {f"d{d}:{p}": n for (d, p), n in sorted(hist.items())},
        "candidate_count": len(candidates),
        "candidate_graph6": [row["graph6"] for row in candidates],
        "independent_audit_required": True,
        "public_action": False,
    }
    append(row)
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("gate", "development", "summarize"), required=True)
    args = parser.parse_args()
    if args.phase == "gate":
        result = atlas_gate()
    elif args.phase == "development":
        result = development()
    else:
        result = summarize_completed_records()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
