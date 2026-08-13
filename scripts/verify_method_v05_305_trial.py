#!/usr/bin/env python3
"""Independent NetworkX/set + CBC replay for the frozen WOWII 305 trial."""

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
LEDGER = ROOT / "results/expansion/method_v05_305_trial.jsonl"
OUT = ROOT / "results/expansion/method_v05_305_trial.verify.jsonl"
CAP = 55


class InternalTimeout(RuntimeError):
    pass


def alarm_handler(_signum, _frame):
    raise InternalTimeout("verification exceeded the internal 55-second deadline")


def append(row: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def total_domination_ilp(graph: nx.Graph) -> tuple[int, list[int]]:
    variables = pulp.LpVariable.dicts("total_dom", list(graph), cat="Binary")
    problem = pulp.LpProblem("minimum_total_domination", pulp.LpMinimize)
    problem += pulp.lpSum(variables.values())
    for vertex in graph:
        problem += pulp.lpSum(variables[neighbor] for neighbor in graph[vertex]) >= 1
    status = problem.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=CAP, gapRel=0.0, threads=1))
    if status != pulp.LpStatusOptimal:
        raise InternalTimeout(f"CBC status {pulp.LpStatus[status]}")
    witness = sorted(vertex for vertex in graph if variables[vertex].value() > 0.5)
    return len(witness), witness


def complement_edge_data_sets(graph: nx.Graph) -> tuple[list[int], list[list[int]], list[list[int]]]:
    complement = nx.complement(graph)
    values = [(tuple(sorted((u, v))), len(set(complement[u]) | set(complement[v])))
              for u, v in complement.edges()]
    values.sort()
    multiset = sorted(value for _, value in values)
    if not multiset:
        return [], [], []
    minimum, maximum = multiset[0], multiset[-1]
    return (multiset, [list(edge) for edge, value in values if value == minimum],
            [list(edge) for edge, value in values if value == maximum])


def replay_total_domination(graph: nx.Graph, witness: list[int]) -> bool:
    chosen = set(witness)
    return all(set(graph[vertex]) & chosen for vertex in graph)


def verify_one(row: dict) -> dict:
    graph = nx.convert_node_labels_to_integers(
        nx.from_graph6_bytes(row["graph6"].encode()), ordering="sorted")
    encoded = nx.to_graph6_bytes(graph, header=False).decode().strip()
    if encoded != row["graph6"]:
        raise AssertionError("graph6 replay mismatch")
    if row["status"] == "NOT_APPLICABLE_HYPOTHESES":
        if len(graph) > 2 or row.get("gamma_t") is not None or row.get("R305") is not None:
            raise AssertionError("invalid hypothesis-inapplicable record")
        return {"stage": f"{row['stage']}_verify", "index": row["index"], "name": row["name"],
                "graph6": encoded, "status": "PASS",
                "independent_values": {"n": len(graph), "applicable": False},
                "method": "independent source-hypothesis replay"}
    gamma_t, ilp_witness = total_domination_ilp(graph)
    multiset, minimizing, maximizing = complement_edge_data_sets(graph)
    if not replay_total_domination(graph, row["total_dominating_set"]):
        raise AssertionError("primary total-domination witness fails direct replay")
    if not replay_total_domination(graph, ilp_witness):
        raise AssertionError("ILP total-domination witness fails direct replay")
    if gamma_t != row["gamma_t"]:
        raise AssertionError(f"gamma_t disagreement: ILP={gamma_t}, bitset={row['gamma_t']}")
    expected_edge_data = (row["complement_edge_neighborhood_multiset"],
                          row["minimizing_complement_edges"], row["maximizing_complement_edges"])
    if (multiset, minimizing, maximizing) != expected_edge_data:
        raise AssertionError("complement edge-neighborhood data disagreement")
    if not multiset:
        if row["status"] != "NOT_APPLICABLE_EDGE_DOMAIN" or any(
                row[key] is not None for key in ("T306", "R305")):
            raise AssertionError("empty complement domain was assigned a numerical value")
        values = {"gamma_t": gamma_t, "T306": None, "R305": None}
    else:
        small, large = multiset[0], multiset[-1]
        t306 = 2 * (small // 2) - gamma_t
        r305 = (2 * large + 2) // 3 - gamma_t
        actual = (small, large, t306, r305, r305 < 0)
        expected = (row["m_complement_edge_neighborhood"],
                    row["M_complement_edge_neighborhood"], row["T306"], row["R305"], row["crossing"])
        if actual != expected:
            raise AssertionError(f"invariant disagreement: actual={actual}, expected={expected}")
        if t306 < 0:
            raise AssertionError("proved WOWII 306 baseline violated")
        values = {"gamma_t": gamma_t, "m": small, "M": large, "T306": t306, "R305": r305}
    return {"stage": f"{row['stage']}_verify", "index": row["index"], "name": row["name"],
            "graph6": encoded, "status": "PASS", "independent_values": values,
            "ilp_total_dominating_set": ilp_witness,
            "minimality_certificate": "CBC proved no smaller feasible binary total-dominating set",
            "method": "NetworkX sets + independently formulated CBC binary optimization + direct witness replay"}


def source_row(stage: str, index: int) -> dict:
    found = None
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if (row.get("stage") == stage and row.get("index") == index
                and row.get("status") in {"OK", "NOT_APPLICABLE_EDGE_DOMAIN",
                                          "NOT_APPLICABLE_HYPOTHESES"}):
            found = row
    if found is not None:
        return found
    raise KeyError((stage, index))


def worker(stage: str, index: int) -> None:
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(CAP)
    source = source_row(stage, index)
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
    print(json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)


def run(stage: str) -> None:
    sources = {row["index"]: row for row in map(json.loads, LEDGER.read_text(encoding="utf-8").splitlines())
               if row.get("stage") == stage and row.get("status") in {
                   "OK", "NOT_APPLICABLE_EDGE_DOMAIN", "NOT_APPLICABLE_HYPOTHESES"}}
    done: dict[int, dict] = {}
    if OUT.exists():
        done = {row["index"]: row for row in map(json.loads, OUT.read_text(encoding="utf-8").splitlines())
                if (row.get("stage") == f"{stage}_verify" and isinstance(row.get("index"), int)
                    and row.get("status") == "PASS")}
    for index in sorted(sources):
        if index in done:
            continue
        command = ["timeout", "--signal=TERM", "--kill-after=5s", "60s", sys.executable,
                   str(Path(__file__).resolve()), "worker", stage, str(index)]
        try:
            result = subprocess.run(command, text=True, capture_output=True, timeout=65)
        except subprocess.TimeoutExpired:
            row = {"stage": f"{stage}_verify", "index": index, "name": sources[index].get("name"),
                   "status": "TIMEOUT_BRACKET", "error": "external Python supervisor exceeded 65 seconds"}
        else:
            if result.returncode == 0 and result.stdout.strip():
                row = json.loads(result.stdout.strip().splitlines()[-1])
            else:
                row = {"stage": f"{stage}_verify", "index": index, "name": sources[index].get("name"),
                       "status": "TIMEOUT_BRACKET" if result.returncode in (124, 137) else "FAIL",
                       "error": f"external verifier exit={result.returncode}: {result.stderr.strip()}"}
        append(row)
        if row["status"] != "PASS":
            append({"stage": f"{stage}_verification_stop", "index": index,
                    "reason": "disagreement_failure_or_timeout"})
            return
        if stage == "grid" and sources[index].get("crossing"):
            append({"stage": "grid_crossing_reproduced", "index": index,
                    "name": sources[index]["name"], "R305": sources[index]["R305"]})
            return
    append({"stage": f"{stage}_verification_complete", "rows": len(sources)})


def audit() -> None:
    trial = [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines()]
    verification = [json.loads(line) for line in OUT.read_text(encoding="utf-8").splitlines()]
    admissible = {"OK", "NOT_APPLICABLE_EDGE_DOMAIN", "NOT_APPLICABLE_HYPOTHESES"}
    gate_by_index = {row["index"]: row for row in trial
                     if row.get("stage") == "gate" and row.get("status") in admissible}
    gate_v_by_index = {row["index"]: row for row in verification
                       if row.get("stage") == "gate_verify" and row.get("status") == "PASS"}
    gate = [gate_by_index[index] for index in sorted(gate_by_index)]
    gate_v = [gate_v_by_index[index] for index in sorted(gate_v_by_index)]
    assert gate and len(gate) == len(gate_v)
    assert all(row["status"] in {"OK", "NOT_APPLICABLE_EDGE_DOMAIN", "NOT_APPLICABLE_HYPOTHESES"}
               and not row.get("gate_failure")
               for row in gate)
    assert all(row["status"] == "PASS" for row in gate_v)
    calibration = next(row for row in gate if row["name"] == "C5[K2]")
    assert (calibration["gamma_t"], calibration["M_complement_edge_neighborhood"], calibration["R305"]) == (3, 8, 3)
    stop_positions = [i for i, row in enumerate(trial) if row.get("stage") == "post_run_audit_stop"
                      and row.get("status") == "FROZEN_CALIBRATION_DISAGREEMENT"]
    assert len(stop_positions) == 1
    assert any(row.get("stage") == "post_run_audit_stop_verify"
               and row.get("status") == "CONFIRMED_FROZEN_CALIBRATION_DISAGREEMENT"
               for row in verification)
    assert all(row["T306"] is None or row["T306"] >= 0 for row in gate)
    grid_by_index = {row["index"]: row for row in trial
                     if row.get("stage") == "grid" and row.get("status") == "OK"}
    grid_v_by_index = {row["index"]: row for row in verification
                       if row.get("stage") == "grid_verify" and row.get("status") == "PASS"}
    grid = [grid_by_index[index] for index in sorted(grid_by_index)]
    grid_v = [grid_v_by_index[index] for index in sorted(grid_v_by_index)]
    if grid:
        # The only accepted bad chronology is the immutable incident already
        # preserved in this ledger: exactly 28 excluded rows, all before the
        # post-run audit stop. Any later/future grid append fails this audit.
        grid_positions = [i for i, row in enumerate(trial) if row.get("stage") == "grid"]
        assert len(grid_positions) == 28 and max(grid_positions) < stop_positions[0]
        assert [row["index"] for row in grid_v] == [row["index"] for row in grid]
        assert all(row["status"] == "PASS" for row in grid_v)
        aliases = sum(len(row["aliases"]) for row in grid)
        assert aliases == 28
        assert all(row["gamma_t"] == 2
                   and row["m_complement_edge_neighborhood"] == 4 * row["d"]
                   and row["M_complement_edge_neighborhood"] == 4 * row["d"] for row in grid)
        minimum = min(row["R305"] for row in grid)
        argmin = [[row["s"], row["d"]] for row in grid if row["R305"] == minimum]
        assert minimum == 1 and argmin == [[s, 1] for s in range(2, 9)]
        outcome = "EXCLUDED_PROTOCOL_VIOLATION"
    else:
        aliases = 0
        outcome = "GRID_NOT_RUN"
    print(json.dumps({"status": "PASS", "gate_rows": len(gate), "grid_representatives": len(grid),
                      "grid_labelled_aliases": aliases, "outcome": outcome,
                      "frozen_calibration_observed": {"gamma_t": 3, "M": 8, "R305": 3},
                      "excluded_grid_min_R305": 1,
                      "excluded_grid_argmin": [[s, 1] for s in range(2, 9)]}, sort_keys=True))


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
