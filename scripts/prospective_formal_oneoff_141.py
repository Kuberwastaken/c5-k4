#!/usr/bin/env python3
"""Frozen exact one-off for current formal-conjectures WOWII #141."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import signal
import time
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_formal_oneoff_141_contract.md"
LEDGER = ROOT / "results/expansion/prospective_formal_oneoff_141_ledger.jsonl"
CONTRACT_SHA256 = "32f26e75f9773e7dc3340eaf9e7fe571e7fa496779b1205f9c96421c8f3d1dda"


class SearchTimeout(RuntimeError):
    pass


def check_contract() -> None:
    actual = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if actual != CONTRACT_SHA256:
        raise RuntimeError(f"frozen contract changed: {actual}")


def emit(row: dict) -> None:
    line = json.dumps({"contract_sha256": CONTRACT_SHA256, **row}, sort_keys=True)
    with LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
    print(line, flush=True)


def graph6(G: nx.Graph) -> str:
    H = nx.convert_node_labels_to_integers(G, ordering="default")
    return nx.to_graph6_bytes(H, header=False).decode("ascii").strip()


def seed_graph() -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(range(15))
    for part in range(5):
        other = (part + 2) % 5
        for i in range(3):
            for j in range(3):
                G.add_edge(3 * part + i, 3 * other + j)
    return G


def girth_with_witness(G: nx.Graph) -> tuple[int, list]:
    best = len(G) + 1
    witness = []
    for u, v in G.edges():
        H = G.copy()
        H.remove_edge(u, v)
        try:
            path = nx.shortest_path(H, u, v)
        except nx.NetworkXNoPath:
            continue
        if len(path) < best:
            best = len(path)
            witness = path
    return (0, []) if not witness else (best, witness)


def local_independence(G: nx.Graph, vertex: int) -> tuple[int, list[int]]:
    neighbors = list(G[vertex])
    for size in range(len(neighbors), -1, -1):
        for subset in itertools.combinations(neighbors, size):
            if all(not G.has_edge(u, v) for u, v in itertools.combinations(subset, 2)):
                return size, list(subset)
    raise AssertionError


def local_profile(G: nx.Graph) -> tuple[int, list[int], dict[str, list[int]]]:
    values = []
    witnesses = {}
    for vertex in G:
        value, witness = local_independence(G, vertex)
        values.append(value)
        witnesses[str(vertex)] = witness
    return max(values), values, witnesses


def is_tree_subset(G: nx.Graph, subset: tuple | list) -> bool:
    H = G.subgraph(subset)
    return len(H) > 0 and nx.is_connected(H) and H.number_of_edges() == len(H) - 1


def exact_largest_induced_tree(G: nx.Graph, cap: float) -> tuple[int, list, int]:
    deadline = time.monotonic() + cap
    vertices = list(G)
    states = 0
    for size in range(len(vertices), 0, -1):
        for subset in itertools.combinations(vertices, size):
            states += 1
            if states & 4095 == 0 and time.monotonic() > deadline:
                raise SearchTimeout
            if is_tree_subset(G, subset):
                return size, list(subset), states
    raise AssertionError


def find_target_tree(G: nx.Graph, target: int, cap: float) -> tuple[list | None, int]:
    if target <= 1:
        return [next(iter(G))], 1
    deadline = time.monotonic() + cap
    adjacency = {v: set(G[v]) for v in G}
    states = 0
    seen = set()

    def extend(chosen: frozenset) -> list | None:
        nonlocal states
        states += 1
        if states & 2047 == 0 and time.monotonic() > deadline:
            raise SearchTimeout
        if len(chosen) >= target:
            return sorted(chosen)
        key = tuple(sorted(chosen))
        if key in seen:
            return None
        seen.add(key)
        boundary = set().union(*(adjacency[v] for v in chosen)) - set(chosen)
        for nxt in sorted(boundary):
            if len(adjacency[nxt] & set(chosen)) == 1:
                result = extend(chosen | {nxt})
                if result is not None:
                    return result
        return None

    for start in sorted(G):
        result = extend(frozenset({start}))
        if result is not None:
            return result, states
    return None, states


def invariants(G: nx.Graph) -> dict:
    girth, girth_witness = girth_with_witness(G)
    lambda_max, local_values, local_witnesses = local_profile(G)
    target = girth // 2 - 1 + lambda_max
    return {"girth": girth, "girth_witness": girth_witness,
            "lambda_max": lambda_max, "local_values": local_values,
            "local_witnesses": local_witnesses, "target": target}


def replay_tree(G: nx.Graph, witness: list, expected: int) -> bool:
    return len(witness) == expected and len(set(witness)) == expected and is_tree_subset(G, witness)


def controls() -> list[tuple[str, nx.Graph]]:
    rows = []
    for G in nx.graph_atlas_g():
        if 2 <= len(G) <= 7 and nx.is_connected(G):
            rows.append((f"atlas:{graph6(G)}", G))
    rows += [(f"C{n}", nx.cycle_graph(n)) for n in range(3, 13)]
    rows += [(f"P{n}", nx.path_graph(n)) for n in range(2, 13)]
    rows += [(f"K1,{r}", nx.star_graph(r)) for r in range(2, 11)]
    rows += [(f"K{n}", nx.complete_graph(n)) for n in range(2, 11)]
    rows += [(f"K{a},{b}", nx.complete_bipartite_graph(a, b))
             for a in range(1, 7) for b in range(a, 7)]
    rows += [("Petersen", nx.petersen_graph()), ("seed:comp-C5K3", seed_graph())]
    return rows


def run_gate(outer_cap: float) -> None:
    started = time.monotonic()
    rows = controls()
    emit({"kind": "phase_start", "phase": "gate", "controls": len(rows)})
    failures = timeouts = 0
    for index, (name, raw) in enumerate(rows):
        if time.monotonic() - started > outer_cap:
            emit({"kind": "gate_summary", "verdict": "GATE_FAIL",
                  "reason": "outer_timeout", "completed": index})
            return
        G = nx.convert_node_labels_to_integers(raw, ordering="default")
        data = invariants(G)
        try:
            tree, witness, states = exact_largest_induced_tree(G, min(10.0, outer_cap))
        except SearchTimeout:
            timeouts += 1
            emit({"kind": "gate_timeout", "name": name, "n": len(G), **data})
            break
        residual = tree - data["target"]
        valid = replay_tree(G, witness, tree)
        failures += residual < 0 or not valid
        emit({"kind": "gate_row", "name": name, "n": len(G),
              "m": G.number_of_edges(), "graph6": graph6(G), **data,
              "tree": tree, "tree_witness": witness, "tree_states": states,
              "residual": residual, "certificate_valid": valid})
        if failures:
            break
    verdict = "PASS" if not failures and not timeouts and index + 1 == len(rows) else "GATE_FAIL"
    emit({"kind": "gate_summary", "verdict": verdict, "completed": index + 1,
          "failures": failures, "timeouts": timeouts,
          "seconds": round(time.monotonic() - started, 6)})


def latest_gate_passed() -> bool:
    if not LEDGER.exists():
        return False
    for line in reversed(LEDGER.read_text(encoding="utf-8").splitlines()):
        row = json.loads(line)
        if row.get("kind") == "gate_summary":
            return row.get("verdict") == "PASS"
    return False


def short_cycles(G: nx.Graph) -> list[tuple[int, ...]]:
    vertices = sorted(G)
    cycles = []
    for size in (4, 5):
        for subset in itertools.combinations(vertices, size):
            start = subset[0]
            for tail in itertools.permutations(subset[1:]):
                cycle = (start,) + tail
                if cycle[1] > cycle[-1]:
                    continue
                if all(G.has_edge(cycle[i], cycle[(i + 1) % size]) for i in range(size)):
                    cycles.append(cycle)
    return cycles


def spanning_tree_and_cotree(G: nx.Graph) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    root = min(G)
    tree = nx.bfs_tree(G, root, sort_neighbors=sorted).to_undirected()
    tree_edges = sorted(tuple(sorted(edge)) for edge in tree.edges())
    tree_set = set(tree_edges)
    cotree = sorted(tuple(sorted(edge)) for edge in G.edges()
                    if tuple(sorted(edge)) not in tree_set)
    return tree_edges, cotree


def solve_voltages(G: nx.Graph, cap: float) -> tuple[str, dict]:
    cycles = short_cycles(G)
    tree_edges, cotree = spanning_tree_and_cotree(G)
    cotree_index = {edge: index for index, edge in enumerate(cotree)}
    edge_count = len(cotree)
    cycle_count = len(cycles)
    # Variables: cotree voltages x, quotient integers k, residue selectors y.
    variable_count = edge_count + 2 * cycle_count
    matrix = lil_matrix((cycle_count, variable_count), dtype=float)
    for row, cycle in enumerate(cycles):
        for u, v in zip(cycle, cycle[1:] + cycle[:1]):
            edge = tuple(sorted((u, v)))
            if edge in cotree_index:
                matrix[row, cotree_index[edge]] += 1 if u < v else -1
        matrix[row, edge_count + row] = -3
        matrix[row, edge_count + cycle_count + row] = -1
    objective = np.zeros(variable_count)
    objective[:edge_count] = np.arange(1, edge_count + 1)
    lower = np.concatenate((np.zeros(edge_count),
                            np.full(cycle_count, -10.0),
                            np.zeros(cycle_count)))
    upper = np.concatenate((np.full(edge_count, 2.0),
                            np.full(cycle_count, 10.0),
                            np.ones(cycle_count)))
    result = milp(c=objective, integrality=np.ones(variable_count),
                  bounds=Bounds(lower, upper),
                  constraints=LinearConstraint(matrix.tocsr(),
                                               np.ones(cycle_count),
                                               np.ones(cycle_count)),
                  options={"time_limit": cap, "presolve": True})
    meta = {"milp_status": int(result.status), "milp_message": result.message,
            "base_short_cycles": cycle_count, "tree_edges": tree_edges,
            "cotree_edges": cotree, "objective": None if result.fun is None else float(result.fun)}
    if result.status == 2:
        return "infeasible", meta
    if result.x is None or result.status != 0:
        return "timeout", meta
    voltages = [int(round(value)) for value in result.x[:edge_count]]
    meta["voltages"] = voltages
    return "optimal", meta


def exact_mod3_feasibility(G: nx.Graph, cap: float) -> tuple[list[int] | None, int, int]:
    """Exact finite-domain replay of the nonzero circulation constraints."""
    deadline = time.monotonic() + cap
    cycles = short_cycles(G)
    _, cotree = spanning_tree_and_cotree(G)
    edge_index = {edge: index for index, edge in enumerate(cotree)}
    constraints = []
    for cycle in cycles:
        coefficients = {}
        for u, v in zip(cycle, cycle[1:] + cycle[:1]):
            edge = tuple(sorted((u, v)))
            if edge in edge_index:
                index = edge_index[edge]
                coefficients[index] = (coefficients.get(index, 0)
                                       + (1 if u < v else -1)) % 3
        constraints.append(tuple(sorted((i, c) for i, c in coefficients.items() if c)))
    variable_constraints = [[] for _ in cotree]
    for constraint_index, constraint in enumerate(constraints):
        for variable, _ in constraint:
            variable_constraints[variable].append(constraint_index)
    states = 0

    def propagate(domains: list[int]) -> list[int] | None:
        changed = True
        while changed:
            if time.monotonic() > deadline:
                raise SearchTimeout
            changed = False
            for constraint in constraints:
                variables = [variable for variable, _ in constraint]
                coefficients = [coefficient for _, coefficient in constraint]
                values = [[x for x in range(3) if domains[v] & (1 << x)]
                          for v in variables]
                supports = [0] * len(variables)
                any_valid = False
                for assignment in itertools.product(*values):
                    if sum(c * x for c, x in zip(coefficients, assignment)) % 3:
                        any_valid = True
                        for position, value in enumerate(assignment):
                            supports[position] |= 1 << value
                if not any_valid:
                    return None
                for position, variable in enumerate(variables):
                    narrowed = domains[variable] & supports[position]
                    if not narrowed:
                        return None
                    if narrowed != domains[variable]:
                        domains[variable] = narrowed
                        changed = True
        return domains

    singleton_value = {1: 0, 2: 1, 4: 2}

    def search(domains: list[int]) -> list[int] | None:
        nonlocal states
        states += 1
        domains = propagate(domains.copy())
        if domains is None:
            return None
        if all(domain in singleton_value for domain in domains):
            return [singleton_value[domain] for domain in domains]
        variable = min(
            (i for i, domain in enumerate(domains) if domain not in singleton_value),
            key=lambda i: (bin(domains[i]).count("1"),
                           -len(variable_constraints[i]), i),
        )
        for value in range(3):
            if domains[variable] & (1 << value):
                branch = domains.copy()
                branch[variable] = 1 << value
                result = search(branch)
                if result is not None:
                    return result
        return None

    solution = search([0b111] * len(cotree))
    return solution, states, len(constraints)


def voltage_lift(G: nx.Graph, cotree: list, voltages: list[int]) -> nx.Graph:
    voltage = {edge: value for edge, value in zip(cotree, voltages)}
    H = nx.Graph()
    H.add_nodes_from(range(3 * len(G)))
    for raw_u, raw_v in G.edges():
        u, v = sorted((raw_u, raw_v))
        shift = voltage.get((u, v), 0)
        for sheet in range(3):
            H.add_edge(3 * u + sheet, 3 * v + (sheet + shift) % 3)
    return H


def validate_lift(base: nx.Graph, lift: nx.Graph, meta: dict) -> dict:
    voltages = meta["voltages"]
    cotree = [tuple(edge) for edge in meta["cotree_edges"]]
    voltage = {edge: value for edge, value in zip(cotree, voltages)}
    edge_ok = True
    for raw_u, raw_v in base.edges():
        u, v = sorted((raw_u, raw_v))
        shift = voltage.get((u, v), 0)
        for sheet in range(3):
            edge_ok &= lift.has_edge(3 * u + sheet, 3 * v + (sheet + shift) % 3)
    fiber_degrees = all(lift.degree(3 * v + sheet) == base.degree(v)
                        for v in base for sheet in range(3))
    _, base_values, _ = local_profile(base)
    _, lift_values, _ = local_profile(lift)
    local_ok = sorted(lift_values) == sorted(base_values * 3)
    girth, _ = girth_with_witness(lift)
    return {"simple": not lift.is_multigraph() and nx.number_of_selfloops(lift) == 0,
            "connected": nx.is_connected(lift), "edge_lift_ok": edge_ok,
            "fiber_degrees_ok": fiber_degrees, "local_profile_ok": local_ok,
            "short_cycles_eliminated": girth >= 6, "validated": edge_ok and fiber_degrees
            and local_ok and nx.is_connected(lift) and girth >= 6}


def run_trial(outer_cap: float) -> None:
    if not latest_gate_passed():
        raise RuntimeError("latest exact database gate has not passed")
    started = time.monotonic()
    base = seed_graph()
    emit({"kind": "phase_start", "phase": "trial", "transformation": "canonical_Z3_voltage_lift"})
    status, meta = solve_voltages(base, min(55.0, outer_cap - 1.0))
    emit({"kind": "voltage_solver", "status": status, **meta,
          "seconds": round(time.monotonic() - started, 6)})
    if status == "infeasible":
        emit({"kind": "trial_summary", "verdict": "NO_APPLICABLE_CANDIDATES"})
        return
    if status != "optimal":
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS",
              "reason": "voltage_solver"})
        return
    lift = voltage_lift(base, meta["cotree_edges"], meta["voltages"])
    validation = validate_lift(base, lift, meta)
    data = invariants(lift)
    row = {"kind": "candidate", "name": "canonical-Z3-lift-comp-C5K3",
           "n": len(lift), "m": lift.number_of_edges(), "graph6": graph6(lift),
           **data, "voltages": meta["voltages"], "cotree_edges": meta["cotree_edges"],
           "validation": validation}
    if not validation["validated"]:
        emit({**row, "verdict": "GATE_FAIL"})
        emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
              "reason": "lift_validation"})
        return
    remaining = max(0.1, outer_cap - (time.monotonic() - started) - 0.5)
    try:
        witness, states = find_target_tree(lift, data["target"], min(remaining, 55.0))
    except SearchTimeout:
        emit({**row, "verdict": "UNRESOLVED_TIMEOUT", "stage": "target_tree"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return
    if witness is not None:
        valid = replay_tree(lift, witness, data["target"])
        emit({**row, "verdict": "HOLD", "tree_lower_bound": data["target"],
              "tree_witness": witness, "tree_states": states,
              "certificate_valid": valid})
        emit({"kind": "trial_summary", "verdict": "HOLD_BOUNDED",
              "candidates": 1, "crossings": 0, "timeouts": 0})
        return
    # Exhaustive target failure is already decision-exact; retain the frozen
    # exact-maximum fallback for a complete numeric record.
    remaining = max(0.1, outer_cap - (time.monotonic() - started) - 0.5)
    try:
        tree, witness, states = exact_largest_induced_tree(lift, min(remaining, 55.0))
    except SearchTimeout:
        emit({**row, "verdict": "UNRESOLVED_TIMEOUT", "stage": "exact_tree"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return
    residual = tree - data["target"]
    verified = replay_tree(lift, witness, tree) and residual < 0
    verdict = "CROSSING_VERIFIED" if verified else "GATE_FAIL"
    emit({**row, "verdict": verdict, "tree": tree, "tree_witness": witness,
          "tree_states": states, "residual": residual,
          "independent_verified": verified})
    emit({"kind": "trial_summary", "verdict": verdict, "candidates": 1,
          "crossings": int(verified), "timeouts": 0})


def run_audit(outer_cap: float) -> None:
    started = time.monotonic()
    try:
        solution, states, constraints = exact_mod3_feasibility(
            seed_graph(), min(55.0, outer_cap)
        )
    except SearchTimeout:
        emit({"kind": "infeasibility_audit", "verdict": "TIMEOUT"})
        return
    emit({"kind": "infeasibility_audit",
          "verdict": "PASS" if solution is None else "FAIL",
          "exact_solution": solution, "constraints": constraints,
          "search_states": states,
          "seconds": round(time.monotonic() - started, 6)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("gate", "trial", "audit"))
    parser.add_argument("--outer-cap", type=float, default=55.0)
    args = parser.parse_args()
    if not 1 < args.outer_cap < 60:
        parser.error("outer cap must be between one and 60 seconds")
    check_contract()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(59)
    if args.phase == "gate":
        run_gate(args.outer_cap)
    elif args.phase == "audit":
        run_audit(args.outer_cap)
    else:
        run_trial(args.outer_cap)


if __name__ == "__main__":
    main()
