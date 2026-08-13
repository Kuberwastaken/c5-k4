#!/usr/bin/env python3
"""Independent CBC/PuLP recomputation and certificate audit for WOWII 179."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import networkx as nx
import pulp


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/method_v04_179_trial.jsonl"
OUT = ROOT / "results/expansion/method_v04_179_trial.verify.jsonl"
CAP = 55


class InternalTimeout(RuntimeError):
    pass


def alarm_handler(_signum, _frame):
    raise InternalTimeout("verification exceeded internal 55-second deadline")


def solve(problem: pulp.LpProblem) -> None:
    status = problem.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=CAP, gapRel=0.0, threads=1))
    if status != pulp.LpStatusOptimal:
        raise InternalTimeout(f"CBC status {pulp.LpStatus[status]}")


def verify_certificates(row: dict, graph: nx.Graph) -> None:
    tree = nx.Graph()
    tree.add_nodes_from(graph)
    tree.add_edges_from(map(tuple, row["spanning_tree_edges"]))
    assert nx.is_tree(tree)
    assert all(graph.has_edge(u, v) for u, v in tree.edges())
    leaves = [1] if len(graph) == 2 else sorted(v for v, degree in tree.degree() if degree == 1)
    assert leaves == row["leaf_vertices"] and len(leaves) == row["Ls"]
    selected = row["bipartition_left"] + row["bipartition_right"]
    assert len(selected) == row["b"] and len(set(selected)) == len(selected)
    assert nx.is_bipartite(graph.subgraph(selected))
    dominating = set(row["dominating_set"])
    assert dominating | set().union(*(set(graph[v]) for v in dominating)) == set(graph)
    assert len(dominating) == row["gamma"]
    for vertex, witness in enumerate(row["local_independence_witnesses"]):
        assert set(witness) <= set(graph[vertex])
        assert graph.subgraph(witness).number_of_edges() == 0
        assert len(witness) == row["local_independence_values"][vertex]
    assert row["local_independence_values"][row["lambda_max_vertex"]] == row["lambda_max"]
    assert row["lambda_max_witness"] == row["local_independence_witnesses"][row["lambda_max_vertex"]]


def bipartite_number(graph: nx.Graph) -> int:
    x = pulp.LpVariable.dicts("selected", list(graph), cat="Binary")
    color = pulp.LpVariable.dicts("color", list(graph), cat="Binary")
    problem = pulp.LpProblem("maximum induced bipartite", pulp.LpMaximize)
    problem += pulp.lpSum(x.values())
    for u, v in graph.edges():
        problem += x[u] + x[v] - color[u] - color[v] <= 1
        problem += x[u] + x[v] + color[u] + color[v] <= 3
    solve(problem)
    return round(pulp.value(problem.objective))


def domination_number(graph: nx.Graph) -> int:
    x = pulp.LpVariable.dicts("dom", list(graph), cat="Binary")
    problem = pulp.LpProblem("minimum domination", pulp.LpMinimize)
    problem += pulp.lpSum(x.values())
    for v in graph:
        problem += pulp.lpSum(x[u] for u in set(graph[v]) | {v}) >= 1
    solve(problem)
    return round(pulp.value(problem.objective))


def connected_domination_number(graph: nx.Graph) -> int:
    n = len(graph)
    if n == 2:
        return 1  # frozen rooted-leaf convention: Ls(K2)=n-gamma_c=1
    arcs = [(u, v) for u, v in graph.edges() for u, v in ((u, v), (v, u))]
    x = pulp.LpVariable.dicts("cd", list(graph), cat="Binary")
    root = pulp.LpVariable.dicts("root", list(graph), cat="Binary")
    source = pulp.LpVariable.dicts("source", list(graph), lowBound=0, upBound=n)
    flow = pulp.LpVariable.dicts("flow", arcs, lowBound=0, upBound=n)
    problem = pulp.LpProblem("minimum connected domination", pulp.LpMinimize)
    problem += pulp.lpSum(x.values())
    for v in graph:
        problem += pulp.lpSum(x[u] for u in set(graph[v]) | {v}) >= 1
    problem += pulp.lpSum(root.values()) == 1
    for v in graph:
        problem += root[v] <= x[v]
        problem += source[v] <= n * root[v]
    for u, v in arcs:
        problem += flow[(u, v)] <= n * x[u]
        problem += flow[(u, v)] <= n * x[v]
    for v in graph:
        incoming = pulp.lpSum(flow[(u, w)] for u, w in arcs if w == v)
        outgoing = pulp.lpSum(flow[(u, w)] for u, w in arcs if u == v)
        problem += source[v] + incoming - outgoing == x[v]
    solve(problem)
    return round(pulp.value(problem.objective))


def independence_number(graph: nx.Graph) -> int:
    x = pulp.LpVariable.dicts("independent", list(graph), cat="Binary")
    problem = pulp.LpProblem("maximum independent set", pulp.LpMaximize)
    problem += pulp.lpSum(x.values())
    for u, v in graph.edges():
        problem += x[u] + x[v] <= 1
    solve(problem)
    value = pulp.value(problem.objective)
    return 0 if value is None else round(value)


def verify_one(row: dict) -> dict:
    graph = nx.from_graph6_bytes(row["graph6"].encode())
    verify_certificates(row, graph)
    b = bipartite_number(graph)
    gamma = domination_number(graph)
    gamma_c = connected_domination_number(graph)
    leaves = len(graph) - gamma_c
    local = [independence_number(graph.subgraph(list(graph[v])).copy()) for v in graph]
    delta = max(dict(graph.degree()).values())
    t173 = leaves + b - (len(graph) + 1)
    q179 = delta + gamma + max(local) - (len(graph) + 1)
    residual = leaves + b - delta - gamma - max(local)
    expected = (row["Ls"], row["b"], row["gamma"], row["local_independence_values"],
                row["Delta"], row["T173"], row["Q179"], row["R179"])
    actual = (leaves, b, gamma, local, delta, t173, q179, residual)
    assert actual == expected, (actual, expected)
    assert residual == t173 - q179
    return {"stage": f"{row['stage']}_verify", "index": row["index"], "name": row["name"],
            "graph6": row["graph6"], "status": "PASS", "independent_values": {
                "Ls": leaves, "b": b, "gamma": gamma, "local": local, "R179": residual},
            "solver": "CBC/PuLP induced-bipartite + domination + connected-domination + local-MIS"}


def append(row: dict) -> None:
    with OUT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def worker(stage: str, index: int) -> None:
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(CAP)
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    source = next(row for row in rows if row.get("stage") == stage and row.get("index") == index)
    try:
        result = verify_one(source)
    except InternalTimeout as error:
        result = {"stage": f"{stage}_verify", "index": index, "name": source.get("name"),
                  "status": "TIMEOUT_BRACKET", "error": str(error)}
    except Exception as error:
        result = {"stage": f"{stage}_verify", "index": index, "name": source.get("name"),
                  "status": "FAIL", "error": f"{type(error).__name__}: {error}"}
    finally:
        signal.alarm(0)
    print(json.dumps(result, sort_keys=True), flush=True)


def run(stage: str) -> None:
    source_rows = {row["index"]: row for row in map(json.loads, LEDGER.read_text().splitlines())
                   if row.get("stage") == stage and row.get("status") == "OK"}
    done = {}
    if OUT.exists():
        done = {row["index"]: row for row in map(json.loads, OUT.read_text().splitlines())
                if row.get("stage") == f"{stage}_verify"}
    for index in sorted(source_rows):
        if index in done:
            continue
        command = ["timeout", "--signal=TERM", "--kill-after=5s", "60s", sys.executable,
                   str(Path(__file__).resolve()), "worker", stage, str(index)]
        result = subprocess.run(command, text=True, capture_output=True, timeout=65)
        if result.returncode == 0 and result.stdout.strip():
            row = json.loads(result.stdout.strip().splitlines()[-1])
        else:
            row = {"stage": f"{stage}_verify", "index": index, "name": source_rows[index].get("name"),
                   "status": "TIMEOUT_BRACKET" if result.returncode == 124 else "FAIL",
                   "error": f"external verifier exit={result.returncode}: {result.stderr.strip()}"}
        append(row)
        if row["status"] != "PASS":
            return
    append({"stage": f"{stage}_verification_complete", "rows": len(source_rows)})


def audit() -> None:
    trial = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    verification = [json.loads(line) for line in OUT.read_text().splitlines()]
    gate = [row for row in trial if row.get("stage") == "gate"]
    grid = [row for row in trial if row.get("stage") == "grid"]
    gate_v = [row for row in verification if row.get("stage") == "gate_verify"]
    grid_v = [row for row in verification if row.get("stage") == "grid_verify"]
    assert [row["index"] for row in gate] == list(range(1043))
    assert all(row["status"] == "OK" and not row.get("gate_failure") for row in gate[:1042])
    assert gate[1042]["name"] == "T(7)" and gate[1042]["status"] == "TIMEOUT_BRACKET"
    assert all(row["T173"] >= 0 and row["R179"] == row["T173"] - row["Q179"]
               and not row["crossing"] for row in gate[:1042])
    assert [row["index"] for row in gate_v] == list(range(1039))
    assert all(row["status"] == "PASS" for row in gate_v[:1038])
    assert gate_v[1038]["name"] == "C5[K5]" and gate_v[1038]["status"] == "TIMEOUT_BRACKET"
    assert not grid and not grid_v
    assert any(row.get("stage") == "gate_stop" and row.get("index") == 1042 for row in trial)
    assert any(row.get("stage") == "pre_grid_family_identity" for row in trial)
    print("PASS stopped-ledger audit: primary 1042 OK then T(7) TIMEOUT_BRACKET")
    print("PASS independent ledger: 1038 PASS then C5[K5] TIMEOUT_BRACKET")
    print("PASS no grid rows; all admitted identities/crossing flags consistent")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    worker_parser = sub.add_parser("worker")
    worker_parser.add_argument("stage", choices=("gate", "grid"))
    worker_parser.add_argument("index", type=int)
    sub.add_parser("run-gate")
    sub.add_parser("run-grid")
    sub.add_parser("audit")
    args = parser.parse_args()
    if args.command == "worker":
        worker(args.stage, args.index)
    elif args.command == "run-gate":
        run("gate")
    elif args.command == "run-grid":
        run("grid")
    else:
        audit()


if __name__ == "__main__":
    main()
