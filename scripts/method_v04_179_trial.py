#!/usr/bin/env python3
"""Frozen exact WOWII 179 gate and private-neighborhood split-clique trial.

The coordinator appends one JSON record per graph.  Every graph is evaluated
in a fresh worker wrapped by an external 60-second timeout; the worker has an
internal 55-second alarm and HiGHS time limits.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/method_v04_179_trial.jsonl"
VERIFY_LEDGER = ROOT / "results/expansion/method_v04_179_trial.verify.jsonl"
INTERNAL_CAP = 55


class InternalTimeout(RuntimeError):
    pass


def alarm_handler(_signum, _frame):
    raise InternalTimeout("worker exceeded the internal 55-second deadline")


def g6(graph: nx.Graph) -> str:
    graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
    return nx.to_graph6_bytes(graph, header=False).decode().strip()


def from_g6(value: str) -> nx.Graph:
    return nx.from_graph6_bytes(value.encode())


def clique_cycle_blowup(weights: tuple[int, ...]) -> nx.Graph:
    graph = nx.Graph()
    bags: list[list[int]] = []
    cursor = 0
    for weight in weights:
        bag = list(range(cursor, cursor + weight))
        cursor += weight
        bags.append(bag)
        graph.add_nodes_from(bag)
        graph.add_edges_from(combinations(bag, 2))
    for i in range(len(weights)):
        graph.add_edges_from((u, v) for u in bags[i] for v in bags[(i + 1) % len(weights)])
    return graph


def endpoint_barbell(length: int) -> nx.Graph:
    graph = nx.path_graph(length + 1)
    cursor = length + 1
    for endpoint in (0, length):
        extra = [cursor, cursor + 1]
        cursor += 2
        graph.add_edges_from(combinations([endpoint, *extra], 2))
    return graph


def triangular_graph(order: int) -> nx.Graph:
    return nx.convert_node_labels_to_integers(nx.line_graph(nx.complete_graph(order)), ordering="sorted")


def split_clique(p: int, profile: tuple[int, ...]) -> nx.Graph:
    graph = nx.complete_graph(p)
    cursor = p
    for hub, size in enumerate(profile):
        for private in range(cursor, cursor + size):
            graph.add_edge(hub, private)
        cursor += size
    return graph


def controls() -> list[dict]:
    rows: list[dict] = []
    seen: dict[str, int] = {}

    def add(name: str, graph: nx.Graph, assertion: str | None = None, force: bool = False) -> None:
        graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
        key = g6(graph)
        if key in seen and not force:
            rows[seen[key]]["aliases"].append(name)
            if assertion and assertion not in rows[seen[key]]["assertions"]:
                rows[seen[key]]["assertions"].append(assertion)
            return
        if key not in seen:
            seen[key] = len(rows)
        rows.append({"name": name, "aliases": [name], "graph6": key,
                     "assertions": [assertion] if assertion else []})

    for index, graph in enumerate(nx.graph_atlas_g()):
        if 2 <= len(graph) <= 7 and nx.is_connected(graph):
            add(f"atlas:{index}", graph)
    for n in range(2, 13):
        add(f"P{n}", nx.path_graph(n))
        if n >= 3:
            add(f"C{n}", nx.cycle_graph(n))
    for r in range(2, 11):
        add(f"K1,{r}", nx.star_graph(r), "star_equality")
    for n in range(2, 11):
        add(f"K{n}", nx.complete_graph(n), "complete_equality")
    for a in range(1, 7):
        for b in range(a, 7):
            add(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
    add("Petersen", nx.petersen_graph())
    add("K3,3", nx.complete_bipartite_graph(3, 3))
    add("K7", nx.complete_graph(7), "complete_equality")
    for m in range(1, 9):
        add(f"C5[K{m}]", clique_cycle_blowup((m,) * 5))
    add("T(7)", triangular_graph(7))
    for length in (6, 8, 10):
        add(f"D_{length}", endpoint_barbell(length))
    project_weights = (
        (2, 2, 2, 2, 2), (3, 3, 3, 3, 3), (4, 4, 4, 4, 4),
        (5, 5, 5, 5, 5), (6, 6, 6, 6, 6), (8, 8, 8, 8, 8),
        (4, 4, 3, 4, 3), (4, 2, 4, 2, 4), (4, 1, 4, 1, 4),
        (3, 1, 3, 1, 3), (5, 5, 4, 5, 4),
    )
    for weights in project_weights:
        # These project controls were explicit rows in the preceding v0.4 gate;
        # retain them even when a uniform member duplicates a named carrier.
        add(f"project:B{weights}", clique_cycle_blowup(weights), force=True)
    return rows


def grid() -> list[dict]:
    profiles = ((1, 1, 1, 1), (2, 1, 1, 1), (3, 1, 1, 1), (3, 2, 1, 1))
    rows: list[dict] = []
    for p in (3, 4, 5, 6):
        for s in range(2, min(p, 4) + 1):
            for raw in profiles:
                profile = raw[:s]
                graph = split_clique(p, profile)
                if any(nx.is_isomorphic(graph, from_g6(row["graph6"])) for row in rows):
                    continue
                rows.append({"name": f"H({p};{','.join(map(str, profile))})", "p": p,
                             "s": s, "profile": list(profile), "graph6": g6(graph)})
    return rows


def solve_milp(objective, integrality, lb, ub, rows, maximize=False):
    matrix = lil_matrix((len(rows), len(objective)), dtype=float)
    lower = np.empty(len(rows))
    upper = np.empty(len(rows))
    for i, (coefficients, lo, hi) in enumerate(rows):
        for j, value in coefficients.items():
            matrix[i, j] = value
        lower[i], upper[i] = lo, hi
    c = -np.asarray(objective, dtype=float) if maximize else np.asarray(objective, dtype=float)
    result = milp(c, integrality=np.asarray(integrality), bounds=Bounds(lb, ub),
                  constraints=LinearConstraint(matrix.tocsr(), lower, upper),
                  options={"time_limit": INTERNAL_CAP, "mip_rel_gap": 0.0})
    if result.status != 0 or result.x is None:
        raise InternalTimeout(f"HiGHS status={result.status}: {result.message}")
    return result


def max_leaf_tree(graph: nx.Graph) -> tuple[int, list[list[int]], list[int]]:
    n = len(graph)
    if n == 2:
        edge = list(graph.edges())[0]
        # Frozen source convention: K_2 has one rooted spanning-tree leaf.
        return 1, [list(edge)], [1]
    edges = list(graph.edges())
    arcs = [(u, v) for u, v in edges for u, v in ((u, v), (v, u))]
    z0, f0, l0 = 0, len(edges), len(edges) + len(arcs)
    variables = l0 + n
    rows = []
    rows.append(({z0 + i: 1 for i in range(len(edges))}, n - 1, n - 1))
    for i, (u, v) in enumerate(arcs):
        edge_index = edges.index((u, v)) if (u, v) in edges else edges.index((v, u))
        rows.append(({f0 + i: 1, z0 + edge_index: -(n - 1)}, -np.inf, 0))
    root = 0
    for v in range(n):
        coefficients = {}
        for i, (u, w) in enumerate(arcs):
            if u == v:
                coefficients[f0 + i] = coefficients.get(f0 + i, 0) + 1
            if w == v:
                coefficients[f0 + i] = coefficients.get(f0 + i, 0) - 1
        rhs = n - 1 if v == root else -1
        rows.append((coefficients, rhs, rhs))
    incident = {v: [] for v in graph}
    for i, (u, v) in enumerate(edges):
        incident[u].append(z0 + i)
        incident[v].append(z0 + i)
    for v in graph:
        coefficients = {index: 1 for index in incident[v]}
        coefficients[l0 + v] = n - 2
        rows.append((coefficients, -np.inf, n - 1))
    objective = np.zeros(variables)
    objective[l0:l0 + n] = 1
    lb = np.zeros(variables)
    ub = np.full(variables, n - 1, dtype=float)
    ub[:len(edges)] = 1
    ub[l0:l0 + n] = 1
    integrality = np.zeros(variables)
    integrality[:len(edges)] = 1
    integrality[l0:l0 + n] = 1
    result = solve_milp(objective, integrality, lb, ub, rows, maximize=True)
    chosen = [list(edge) for i, edge in enumerate(edges) if result.x[z0 + i] > .5]
    tree = nx.Graph(chosen)
    tree.add_nodes_from(graph)
    assert nx.is_tree(tree)
    leaves = sorted(v for v, degree in tree.degree() if degree == 1)
    return len(leaves), chosen, leaves


def bipartite_number(graph: nx.Graph) -> tuple[int, list[int], list[int]]:
    n = len(graph)
    rows = []
    for u, v in graph.edges():
        rows.append(({u: 1, v: 1, n + u: -1, n + v: -1}, -np.inf, 1))
        rows.append(({u: 1, v: 1, n + u: 1, n + v: 1}, -np.inf, 3))
    objective = np.r_[np.ones(n), np.zeros(n)]
    result = solve_milp(objective, np.ones(2 * n), np.zeros(2 * n), np.ones(2 * n), rows, maximize=True)
    selected = sorted(v for v in graph if result.x[v] > .5)
    coloring = nx.bipartite.color(graph.subgraph(selected)) if selected else {}
    left = sorted(v for v in selected if coloring[v] == 0)
    right = sorted(v for v in selected if coloring[v] == 1)
    return len(selected), left, right


def domination_number(graph: nx.Graph) -> tuple[int, list[int]]:
    n = len(graph)
    rows = []
    for v in graph:
        rows.append(({u: 1 for u in set(graph[v]) | {v}}, 1, np.inf))
    result = solve_milp(np.ones(n), np.ones(n), np.zeros(n), np.ones(n), rows)
    chosen = sorted(v for v in graph if result.x[v] > .5)
    return len(chosen), chosen


def maximum_independent_set(graph: nx.Graph) -> list[int]:
    # Exact maximum clique search in the complement, independent of floating point.
    complement = nx.complement(graph)
    best: list[int] = []

    def expand(chosen: list[int], candidates: set[int]) -> None:
        nonlocal best
        if len(chosen) + len(candidates) <= len(best):
            return
        if not candidates:
            if len(chosen) > len(best):
                best = chosen[:]
            return
        while candidates:
            if len(chosen) + len(candidates) <= len(best):
                return
            vertex = min(candidates)
            candidates.remove(vertex)
            expand(chosen + [vertex], candidates & set(complement[vertex]))
        if len(chosen) > len(best):
            best = chosen[:]

    expand([], set(graph))
    return sorted(best)


def evaluate(item: dict, stage: str, index: int) -> dict:
    graph = from_g6(item["graph6"])
    if len(graph) < 2 or not nx.is_connected(graph):
        raise AssertionError("graph must be connected and nontrivial")
    started = time.monotonic()
    leaves, tree_edges, leaf_vertices = max_leaf_tree(graph)
    b, b_left, b_right = bipartite_number(graph)
    gamma, dominating = domination_number(graph)
    local_values = []
    local_witnesses = []
    for vertex in graph:
        witness = maximum_independent_set(graph.subgraph(list(graph[vertex])).copy())
        local_values.append(len(witness))
        local_witnesses.append(witness)
    maximizing_vertex = min(v for v, value in enumerate(local_values) if value == max(local_values))
    local_max = local_values[maximizing_vertex]
    n = len(graph)
    delta = max(dict(graph.degree()).values())
    t173 = leaves + b - (n + 1)
    q179 = delta + gamma + local_max - (n + 1)
    residual = leaves + b - delta - gamma - local_max
    assert residual == t173 - q179
    row = dict(item)
    row.update({
        "stage": stage, "index": index, "status": "OK", "n": n,
        "m": graph.number_of_edges(), "Ls": leaves, "spanning_tree_edges": tree_edges,
        "leaf_vertices": leaf_vertices, "b": b, "bipartition_left": b_left,
        "bipartition_right": b_right, "Delta": delta, "gamma": gamma,
        "dominating_set": dominating, "local_independence_values": local_values,
        "local_independence_witnesses": local_witnesses,
        "lambda_max": local_max, "lambda_max_vertex": maximizing_vertex,
        "lambda_max_witness": local_witnesses[maximizing_vertex],
        "T173": t173, "Q179": q179, "R179": residual,
        "crossing": residual < 0, "elapsed_seconds": round(time.monotonic() - started, 6),
        "solver": "SciPy HiGHS MILP + exact branch-and-bound local alpha",
    })
    if t173 < 0:
        row["gate_failure"] = "negative WOWII 173 baseline"
    for assertion in item.get("assertions", []):
        if residual != 0:
            row["gate_failure"] = f"{assertion} failed"
    if stage == "gate" and residual < 0:
        row["gate_failure"] = "unexpected source crossing"
    return row


def append(row: dict, path: Path = LEDGER) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def worker(stage: str, index: int) -> None:
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(INTERNAL_CAP)
    item = (controls() if stage == "gate" else grid())[index]
    try:
        row = evaluate(item, stage, index)
    except InternalTimeout as error:
        row = dict(item, stage=stage, index=index, status="TIMEOUT_BRACKET", error=str(error))
    except Exception as error:
        row = dict(item, stage=stage, index=index, status="ERROR", error=f"{type(error).__name__}: {error}")
    finally:
        signal.alarm(0)
    print(json.dumps(row, sort_keys=True), flush=True)


def completed(stage: str) -> dict[int, dict]:
    if not LEDGER.exists():
        return {}
    answer = {}
    for line in LEDGER.read_text().splitlines():
        row = json.loads(line)
        if row.get("stage") == stage and isinstance(row.get("index"), int):
            answer[row["index"]] = row
    return answer


def invoke(stage: str, index: int) -> dict:
    command = ["timeout", "--signal=TERM", "--kill-after=5s", "60s", sys.executable,
               str(Path(__file__).resolve()), "worker", stage, str(index)]
    result = subprocess.run(command, text=True, capture_output=True, timeout=65)
    if result.returncode == 0 and result.stdout.strip():
        return json.loads(result.stdout.strip().splitlines()[-1])
    return {"stage": stage, "index": index, "status": "TIMEOUT_BRACKET" if result.returncode == 124 else "ERROR",
            "error": f"external worker exit={result.returncode}: {result.stderr.strip()}"}


def gate_is_verified() -> bool:
    expected = len(controls())
    rows = completed("gate")
    if len(rows) != expected or any(row.get("status") != "OK" or row.get("gate_failure") for row in rows.values()):
        return False
    if not VERIFY_LEDGER.exists():
        return False
    verified = {}
    for line in VERIFY_LEDGER.read_text().splitlines():
        row = json.loads(line)
        if row.get("stage") == "gate_verify":
            verified[row["index"]] = row
    return len(verified) == expected and all(row.get("status") == "PASS" for row in verified.values())


def run_stage(stage: str) -> None:
    if stage == "grid" and not gate_is_verified():
        raise SystemExit("gate is not complete and independently verified; frozen grid remains locked")
    items = controls() if stage == "gate" else grid()
    done = completed(stage)
    if not LEDGER.exists():
        append({"stage": "trial_start", "target": "WOWII 179", "commit": "2265037bef0d806995c4f0d3c4a01ae9d2270f43",
                "internal_cap_seconds": 55, "external_cap_seconds": 60})
    for index in range(len(items)):
        if index in done:
            continue
        row = invoke(stage, index)
        append(row)
        if row.get("status") != "OK" or row.get("gate_failure") or row.get("crossing"):
            append({"stage": f"{stage}_stop", "index": index,
                    "reason": "crossing requires protocol stop" if row.get("crossing") else "failure or timeout"})
            return
    append({"stage": f"{stage}_complete", "rows": len(items)})


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    worker_parser = sub.add_parser("worker")
    worker_parser.add_argument("stage", choices=("gate", "grid"))
    worker_parser.add_argument("index", type=int)
    sub.add_parser("run-gate")
    sub.add_parser("run-grid")
    sub.add_parser("counts")
    args = parser.parse_args()
    if args.command == "worker":
        worker(args.stage, args.index)
    elif args.command == "run-gate":
        run_stage("gate")
    elif args.command == "run-grid":
        run_stage("grid")
    else:
        print(json.dumps({"gate": len(controls()), "grid": len(grid())}, sort_keys=True))


if __name__ == "__main__":
    main()
