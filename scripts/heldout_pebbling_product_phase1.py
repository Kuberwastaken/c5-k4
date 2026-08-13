#!/usr/bin/env python3
"""Exact Phase-1 evaluator for the frozen Lemke-square threshold shell."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = ROOT / "results/expansion/heldout_pebbling_product_phase1_addendum.md"
PHASE0 = ROOT / "results/expansion/heldout_pebbling_product_phase0_contract.md"
LEDGER = ROOT / "results/expansion/heldout_pebbling_product_phase1_ledger.jsonl"
ADDENDUM_SHA = "16750a88d66776005942f6be0c33134e1b1f7d941b8f58d9a930c2bfa6dbc388"
PHASE0_SHA = "87fd502e85fb6e43dce2d06903c77799678698770abfed6e0dafd6e0cfabb265"
DEADLINE = 55.0
BATCHES = [(i, i + 504) for i in range(0, 4032, 504)]
FACTOR_EDGES = [
    (0, 1), (0, 2), (1, 3), (2, 4), (2, 5), (2, 6),
    (3, 4), (3, 5), (3, 6), (3, 7), (4, 7), (5, 7), (6, 7),
]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append(row):
    with LEDGER.open("a", encoding="utf-8") as out:
        out.write(canonical(row) + "\n")
        out.flush()


def rows():
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line]


def check_contracts():
    if sha_file(ADDENDUM) != ADDENDUM_SHA:
        raise RuntimeError("Phase-1 addendum digest mismatch")
    if sha_file(PHASE0) != PHASE0_SHA:
        raise RuntimeError("Phase-0 contract digest mismatch")


def adjacency(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if u == v:
            raise RuntimeError("loop in graph")
        adj[u].add(v)
        adj[v].add(u)
    return [tuple(sorted(x)) for x in adj]


def shortest_path(adj, source, target):
    parent = {source: None}
    queue = collections.deque([source])
    while queue:
        v = queue.popleft()
        if v == target:
            break
        for w in adj[v]:
            if w not in parent:
                parent[w] = v
                queue.append(w)
    if target not in parent:
        return None
    path = []
    v = target
    while v is not None:
        path.append(v)
        v = parent[v]
    return list(reversed(path))


def primary_relay(adj, initial, root, extra):
    path = shortest_path(adj, extra, root)
    if path is None:
        return None
    state = list(initial)
    moves = []
    intermediates = [state.copy()]
    for source, target in zip(path, path[1:]):
        if target not in adj[source] or state[source] < 2:
            return None
        sb, tb = state[source], state[target]
        state[source] -= 2
        state[target] += 1
        moves.append({"source": source, "target": target,
                      "source_before": sb, "target_before": tb,
                      "source_after": state[source], "target_after": state[target]})
        intermediates.append(state.copy())
    if state[root] < 1:
        return None
    return {"path": path, "moves": moves, "intermediate_distributions": intermediates,
            "final": state}


def bfs_reachable(adj, initial, root):
    """Independent exact oracle for deliberately small calibration states."""
    start = tuple(initial)
    queue = collections.deque([start])
    seen = {start}
    while queue:
        state = queue.popleft()
        if state[root] >= 1:
            return True
        for source, count in enumerate(state):
            if count < 2:
                continue
            for target in adj[source]:
                nxt = list(state)
                nxt[source] -= 2
                nxt[target] += 1
                key = tuple(nxt)
                if key not in seen:
                    seen.add(key)
                    queue.append(key)
    return False


def control_graphs():
    return {
        "K2": (2, [(0, 1)]),
        "P3": (3, [(0, 1), (1, 2)]),
        "K3": (3, [(0, 1), (0, 2), (1, 2)]),
        "C4": (4, [(0, 1), (1, 2), (2, 3), (0, 3)]),
    }


def gate():
    check_contracts()
    old = rows()
    if len(old) != 4 or any(r.get("event") == "product_state" for r in old):
        raise RuntimeError("ledger is not in frozen zero-state condition")
    started = time.monotonic()
    checks = 0
    for name, (n, edges) in control_graphs().items():
        adj = adjacency(n, edges)
        for root in range(n):
            lower = [1] * n
            lower[root] = 0
            if bfs_reachable(adj, lower, root):
                append({"event": "calibration", "status": "FAIL", "graph": name,
                        "root": root, "kind": "lower_state"})
                raise RuntimeError("independent oracle accepted immobile lower state")
            checks += 1
            for extra in range(n):
                if extra == root:
                    continue
                initial = lower.copy()
                initial[extra] += 1
                primary = primary_relay(adj, initial, root, extra)
                independent = bfs_reachable(adj, initial, root)
                if primary is None or not independent:
                    append({"event": "calibration", "status": "FAIL", "graph": name,
                            "root": root, "extra": extra, "kind": "threshold_shell"})
                    raise RuntimeError("primary/independent calibration mismatch")
                checks += 1
        if time.monotonic() - started > DEADLINE:
            raise TimeoutError("gate internal deadline")
        append({"event": "calibration_graph", "status": "PASS", "graph": name,
                "vertices": n})
    append({"event": "phase1_unlock", "status": "PASS", "calibration_checks": checks,
            "primary_oracle":"shortest-path literal replay",
            "independent_oracle":"full finite-state BFS",
            "product_states_constructed": 0,
            "elapsed_seconds": round(time.monotonic() - started, 6)})
    print(canonical({"status": "PASS", "calibration_checks": checks}))


def product_record():
    roles = []
    for a in range(8):
        for b in range(8):
            roles.append({"index": 8 * a + b, "label": f"(v{a+1},v{b+1})",
                          "factor_G": f"v{a+1}", "factor_H": f"v{b+1}"})
    edges = set()
    for a, b in FACTOR_EDGES:
        for h in range(8):
            edges.add(tuple(sorted((8 * a + h, 8 * b + h))))
        for g in range(8):
            edges.add(tuple(sorted((8 * g + a, 8 * g + b))))
    edges = sorted(edges)
    labelled = {"roles": roles, "edges": edges}
    return roles, edges, hashlib.sha256(canonical(labelled).encode()).hexdigest()


def state_pairs():
    return [(root, extra) for root in range(64) for extra in range(64) if extra != root]


def batch(start, end):
    check_contracts()
    if (start, end) not in BATCHES:
        raise RuntimeError("batch not in frozen partition")
    old = rows()
    if not any(r.get("event") == "phase1_unlock" and r.get("status") == "PASS" for r in old):
        raise RuntimeError("gate has not unlocked product construction")
    completed = [r for r in old if r.get("event") == "product_state"]
    if len(completed) != start or [r["index"] for r in completed] != list(range(start)):
        raise RuntimeError("batch does not continue append-only state prefix")
    if any(r.get("event") in ("candidate_lower_bound", "timeout_bracket") for r in old):
        raise RuntimeError("terminal stop already recorded")
    roles, edges, graph_digest = product_record()
    adj = adjacency(64, edges)
    labelled_edges = [[roles[u]["label"], roles[v]["label"]] for u, v in edges]
    role_map = {r["label"]: {"index": r["index"], "factor_G": r["factor_G"],
                             "factor_H": r["factor_H"]} for r in roles}
    pairs = state_pairs()
    started = time.monotonic()
    for index in range(start, end):
        if time.monotonic() - started > DEADLINE:
            append({"event": "timeout_bracket", "outcome": "TIMEOUT_BRACKET",
                    "next_index": index, "batch": [start, end]})
            raise TimeoutError("batch internal deadline")
        root, extra = pairs[index]
        initial = [1] * 64
        initial[root] = 0
        initial[extra] = 2
        replay = primary_relay(adj, initial, root, extra)
        if replay is None:
            # A fresh graph-path implementation is the independent check here.
            alternate = shortest_path([tuple(sorted(x, reverse=True)) for x in adj], extra, root)
            append({"event": "candidate_lower_bound", "outcome": "CANDIDATE_LOWER_BOUND",
                    "index": index, "root": roles[root]["label"],
                    "extra": roles[extra]["label"], "alternate_vertex_path": alternate,
                    "note": "candidate only; not a product-conjecture disproof"})
            raise RuntimeError("primary exact relay found no witness")
        labelled_path = [roles[v]["label"] for v in replay["path"]]
        labelled_moves = [{**m, "source_label": roles[m["source"]]["label"],
                           "target_label": roles[m["target"]]["label"]} for m in replay["moves"]]
        state_material = {"graph_digest": graph_digest, "root": root, "extra": extra,
                          "initial": initial}
        append({"event": "product_state", "status": "REACHABLE", "index": index,
                "batch": [start, end], "root": roles[root]["label"],
                "extra": roles[extra]["label"], "root_index": root, "extra_index": extra,
                "labelled_product_edges": labelled_edges, "role_map": role_map,
                "labelled_graph_sha256": graph_digest,
                "initial_distribution": initial, "final_distribution": replay["final"],
                "shortest_path": labelled_path, "moves": labelled_moves,
                "intermediate_distributions": replay["intermediate_distributions"],
                "distance": len(replay["moves"]), "final_root_count": replay["final"][root],
                "final_total": sum(replay["final"]),
                "labelled_state_sha256": hashlib.sha256(canonical(state_material).encode()).hexdigest()})
    append({"event": "batch_complete", "status": "PASS", "batch": [start, end],
            "states": end - start, "elapsed_seconds": round(time.monotonic() - started, 6)})
    print(canonical({"status": "PASS", "batch": [start, end], "states": end-start}))


def replay_stored(row):
    edge_indices = set()
    inverse = {label: data["index"] for label, data in row["role_map"].items()}
    for a, b in row["labelled_product_edges"]:
        edge_indices.add(tuple(sorted((inverse[a], inverse[b]))))
    state = row["initial_distribution"].copy()
    if len(state) != 64 or sum(state) != 64:
        return False
    for move in row["moves"]:
        source, target = move["source"], move["target"]
        if tuple(sorted((source, target))) not in edge_indices or state[source] < 2:
            return False
        state[source] -= 2
        state[target] += 1
    return state == row["final_distribution"] and state[row["root_index"]] >= 1


def finalize():
    check_contracts()
    old = rows()
    states = [r for r in old if r.get("event") == "product_state"]
    if len(states) != 4032 or [r["index"] for r in states] != list(range(4032)):
        raise RuntimeError("state ledger is not complete and consecutive")
    if any(r.get("event") in ("candidate_lower_bound", "timeout_bracket") for r in old):
        raise RuntimeError("terminal non-hold row exists")
    started = time.monotonic()
    histogram = collections.Counter()
    for row in states:
        if time.monotonic() - started > DEADLINE:
            raise TimeoutError("final replay internal deadline")
        if not replay_stored(row):
            raise RuntimeError(f"fresh replay failed at state {row['index']}")
        if row["distance"] != len(row["moves"]) or row["final_root_count"] != 1 \
                or row["final_total"] != 64 - row["distance"]:
            raise RuntimeError(f"prediction coordinate mismatch at state {row['index']}")
        histogram[row["distance"]] += 1
    append({"event": "phase1_outcome", "outcome": "PREDICTION_CONFIRMED",
            "states": 4032, "reachable": 4032, "unreachable": 0, "timeouts": 0,
            "distance_histogram": dict(sorted(histogram.items())),
            "fresh_literal_replays": 4032,
            "scope":"frozen support-63 single-extra shell only",
            "elapsed_seconds": round(time.monotonic() - started, 6)})
    print(canonical({"outcome":"PREDICTION_CONFIRMED","states":4032,
                     "distance_histogram":dict(sorted(histogram.items()))}))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("gate")
    bp = sub.add_parser("batch")
    bp.add_argument("--start", type=int, required=True)
    bp.add_argument("--end", type=int, required=True)
    sub.add_parser("finalize")
    args = parser.parse_args()
    if args.command == "gate":
        gate()
    elif args.command == "batch":
        batch(args.start, args.end)
    else:
        finalize()


if __name__ == "__main__":
    main()
