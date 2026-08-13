#!/usr/bin/env python3
"""Frozen nonabelian S3 permutation-lift trial for WOWII #141."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import signal
import time
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/expansion/prospective_formal_141_s3_cover_contract.md"
LEDGER = ROOT / "results/expansion/prospective_formal_141_s3_cover_ledger.jsonl"
CONTRACT_SHA256 = "48975702b8a4dc91fa37f79e088eb5df23131ef31d11a0d8ccd1e90c3ff9669d"

PARENT_PATH = ROOT / "scripts/prospective_formal_oneoff_141.py"
SPEC = importlib.util.spec_from_file_location("wow141_parent", PARENT_PATH)
assert SPEC and SPEC.loader
PARENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARENT)

PERMS = tuple(sorted(itertools.permutations(range(3))))
PERM_INDEX = {permutation: index for index, permutation in enumerate(PERMS)}
IDENTITY = PERM_INDEX[(0, 1, 2)]
FIXED_POINT_FREE = frozenset(
    index for index, permutation in enumerate(PERMS)
    if all(permutation[value] != value for value in range(3))
)


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    """Return left after right."""
    return tuple(left[right[value]] for value in range(3))


COMPOSE = tuple(tuple(PERM_INDEX[compose(left, right)] for right in PERMS)
                for left in PERMS)
INVERSE = []
for permutation in PERMS:
    inverse = [0, 0, 0]
    for source, target in enumerate(permutation):
        inverse[target] = source
    INVERSE.append(PERM_INDEX[tuple(inverse)])
INVERSE = tuple(INVERSE)


class SolverTimeout(RuntimeError):
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


def run_gate(outer_cap: float) -> None:
    started = time.monotonic()
    controls = PARENT.controls()
    emit({"kind": "phase_start", "phase": "gate", "controls": len(controls)})
    failures = timeouts = 0
    for index, (name, raw) in enumerate(controls):
        if time.monotonic() - started > outer_cap:
            emit({"kind": "gate_summary", "verdict": "GATE_FAIL",
                  "reason": "outer_timeout", "completed": index})
            return
        G = nx.convert_node_labels_to_integers(raw, ordering="default")
        data = PARENT.invariants(G)
        try:
            tree, witness, states = PARENT.exact_largest_induced_tree(G, 10.0)
        except PARENT.SearchTimeout:
            timeouts += 1
            emit({"kind": "gate_timeout", "name": name, "n": len(G), **data})
            break
        residual = tree - data["target"]
        valid = PARENT.replay_tree(G, witness, tree)
        failures += residual < 0 or not valid
        emit({"kind": "gate_row", "name": name, "n": len(G),
              "m": G.number_of_edges(), "graph6": PARENT.graph6(G), **data,
              "tree": tree, "tree_witness": witness, "tree_states": states,
              "residual": residual, "certificate_valid": valid})
        if failures:
            break
    verdict = "PASS" if not failures and not timeouts and index + 1 == len(controls) else "GATE_FAIL"
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


def permutation_constraints(base: nx.Graph):
    cycles = PARENT.short_cycles(base)
    tree_edges, cotree = PARENT.spanning_tree_and_cotree(base)
    edge_index = {edge: index for index, edge in enumerate(cotree)}
    constraints = []
    for cycle in cycles:
        operations = []
        for u, v in zip(cycle, cycle[1:] + cycle[:1]):
            edge = tuple(sorted((u, v)))
            if edge in edge_index:
                operations.append((edge_index[edge], -1 if u > v else 1))
        constraints.append(tuple(operations))
    return cycles, tree_edges, cotree, constraints


def product_rank(constraint: tuple, assignment: tuple[int, ...]) -> int:
    product = IDENTITY
    for (_, direction), rank in zip(constraint, assignment):
        operation = rank if direction == 1 else INVERSE[rank]
        product = COMPOSE[operation][product]
    return product


def solve_s3(base: nx.Graph, cap: float, state_cap: int = 250_000) -> tuple[str, dict]:
    started = time.monotonic()
    deadline = started + cap
    cycles, tree_edges, cotree, constraints = permutation_constraints(base)
    states = 0
    cache = {}

    def supports(constraint_index: int, masks: tuple[int, ...]):
        key = (constraint_index, masks)
        if key in cache:
            return cache[key]
        constraint = constraints[constraint_index]
        domains = [tuple(rank for rank in range(6) if mask & (1 << rank))
                   for mask in masks]
        result_supports = [0] * len(constraint)
        any_valid = False
        for assignment in itertools.product(*domains):
            if product_rank(constraint, assignment) in FIXED_POINT_FREE:
                any_valid = True
                for position, rank in enumerate(assignment):
                    result_supports[position] |= 1 << rank
        value = tuple(result_supports) if any_valid else None
        cache[key] = value
        return value

    def propagate(domains: list[int]) -> list[int] | None:
        changed = True
        while changed:
            if time.monotonic() > deadline:
                raise SolverTimeout
            changed = False
            for constraint_index, constraint in enumerate(constraints):
                masks = tuple(domains[variable] for variable, _ in constraint)
                support = supports(constraint_index, masks)
                if support is None:
                    return None
                for position, (variable, _) in enumerate(constraint):
                    narrowed = domains[variable] & support[position]
                    if not narrowed:
                        return None
                    if narrowed != domains[variable]:
                        domains[variable] = narrowed
                        changed = True
        return domains

    singleton_rank = {1 << rank: rank for rank in range(6)}

    def search(domains: list[int]) -> list[int] | None:
        nonlocal states
        states += 1
        if states > state_cap or time.monotonic() > deadline:
            raise SolverTimeout
        domains = propagate(domains.copy())
        if domains is None:
            return None
        if all(domain in singleton_rank for domain in domains):
            return [singleton_rank[domain] for domain in domains]
        variable = next(index for index, domain in enumerate(domains)
                        if domain not in singleton_rank)
        for rank in range(6):
            if domains[variable] & (1 << rank):
                branch = domains.copy()
                branch[variable] = 1 << rank
                result = search(branch)
                if result is not None:
                    return result
        return None

    try:
        solution = search([(1 << 6) - 1] * len(cotree))
    except SolverTimeout:
        return "timeout", {"states": states, "cycles": len(cycles),
                           "tree_edges": tree_edges, "cotree_edges": cotree,
                           "cache_entries": len(cache),
                           "seconds": round(time.monotonic() - started, 6)}
    return ("infeasible" if solution is None else "optimal"), {
        "states": states, "cycles": len(cycles), "tree_edges": tree_edges,
        "cotree_edges": cotree, "permutation_ranks": solution,
        "permutations": None if solution is None else [PERMS[rank] for rank in solution],
        "cache_entries": len(cache), "seconds": round(time.monotonic() - started, 6),
    }


def permutation_lift(base: nx.Graph, cotree: list, ranks: list[int]) -> nx.Graph:
    rank_by_edge = {tuple(edge): rank for edge, rank in zip(cotree, ranks)}
    lift = nx.Graph()
    lift.add_nodes_from(range(3 * len(base)))
    for raw_u, raw_v in base.edges():
        u, v = sorted((raw_u, raw_v))
        permutation = PERMS[rank_by_edge.get((u, v), IDENTITY)]
        for sheet in range(3):
            lift.add_edge(3 * u + sheet, 3 * v + permutation[sheet])
    return lift


def validate_assignment(base: nx.Graph, lift: nx.Graph, meta: dict) -> dict:
    cycles, _, cotree, constraints = permutation_constraints(base)
    ranks = meta["permutation_ranks"]
    monodromies = []
    fixed_point_free = True
    for constraint in constraints:
        assignment = tuple(ranks[variable] for variable, _ in constraint)
        product = product_rank(constraint, assignment)
        monodromies.append(product)
        fixed_point_free &= product in FIXED_POINT_FREE
    exact_edges = True
    rank_by_edge = {tuple(edge): rank for edge, rank in zip(cotree, ranks)}
    for raw_u, raw_v in base.edges():
        u, v = sorted((raw_u, raw_v))
        permutation = PERMS[rank_by_edge.get((u, v), IDENTITY)]
        for sheet in range(3):
            exact_edges &= lift.has_edge(3 * u + sheet, 3 * v + permutation[sheet])
    degree_ok = all(lift.degree(3 * v + sheet) == base.degree(v)
                    for v in base for sheet in range(3))
    lambda_max, values, _ = PARENT.local_profile(lift)
    girth, girth_witness = PARENT.girth_with_witness(lift)
    simple = not lift.is_multigraph() and nx.number_of_selfloops(lift) == 0
    connected = nx.is_connected(lift)
    local_ok = lambda_max == 6 and all(value == 6 for value in values)
    valid = (fixed_point_free and exact_edges and degree_ok and simple
             and connected and local_ok and girth >= 6)
    return {"cycles_checked": len(cycles), "monodromy_ranks": monodromies,
            "fixed_point_free": fixed_point_free, "exact_edges": exact_edges,
            "degree_ok": degree_ok, "simple": simple, "connected": connected,
            "lambda_max": lambda_max, "all_local_values_six": local_ok,
            "girth": girth, "girth_witness": girth_witness, "validated": valid}


def run_trial(outer_cap: float) -> None:
    if not latest_gate_passed():
        raise RuntimeError("latest S3-lane database gate has not passed")
    started = time.monotonic()
    base = PARENT.seed_graph()
    emit({"kind": "phase_start", "phase": "trial",
          "transformation": "nonabelian_S3_permutation_lift"})
    status, meta = solve_s3(base, min(55.0, outer_cap - 0.5))
    emit({"kind": "solver_result", "status": status, **meta})
    if status == "infeasible":
        emit({"kind": "trial_summary", "verdict": "NO_APPLICABLE_CANDIDATES"})
        return
    if status != "optimal":
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS",
              "reason": "S3_solver"})
        return
    lift = permutation_lift(base, meta["cotree_edges"], meta["permutation_ranks"])
    validation = validate_assignment(base, lift, meta)
    data = PARENT.invariants(lift)
    row = {"kind": "candidate", "name": "canonical-S3-lift-comp-C5K3",
           "n": len(lift), "m": lift.number_of_edges(),
           "graph6": PARENT.graph6(lift), **data,
           "permutation_ranks": meta["permutation_ranks"],
           "permutations": meta["permutations"],
           "cotree_edges": meta["cotree_edges"], "validation": validation}
    emit({"kind": "candidate_constructed", "name": row["name"],
          "n": row["n"], "m": row["m"], "graph6": row["graph6"],
          "girth": row["girth"], "lambda_max": row["lambda_max"],
          "target": row["target"], "validation": validation})
    if not validation["validated"]:
        emit({**row, "verdict": "GATE_FAIL"})
        emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
              "reason": "cover_validation"})
        return
    remaining = max(0.1, outer_cap - (time.monotonic() - started) - 0.5)
    try:
        witness, states = PARENT.find_target_tree(lift, data["target"],
                                                  min(55.0, remaining))
    except PARENT.SearchTimeout:
        emit({**row, "verdict": "UNRESOLVED_TIMEOUT", "stage": "target_tree"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return
    if witness is not None:
        valid = PARENT.replay_tree(lift, witness, data["target"])
        emit({**row, "verdict": "HOLD", "tree_lower_bound": data["target"],
              "tree_witness": witness, "tree_states": states,
              "certificate_valid": valid})
        emit({"kind": "trial_summary", "verdict": "HOLD_BOUNDED",
              "candidates": 1, "crossings": 0, "timeouts": 0})
        return
    remaining = max(0.1, outer_cap - (time.monotonic() - started) - 0.5)
    try:
        tree, witness, states = PARENT.exact_largest_induced_tree(
            lift, min(55.0, remaining)
        )
    except PARENT.SearchTimeout:
        emit({**row, "verdict": "UNRESOLVED_TIMEOUT", "stage": "exact_tree"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return
    residual = tree - data["target"]
    verified = PARENT.replay_tree(lift, witness, tree) and residual < 0
    verdict = "CROSSING_VERIFIED" if verified else "GATE_FAIL"
    emit({**row, "verdict": verdict, "tree": tree, "tree_witness": witness,
          "tree_states": states, "residual": residual,
          "independent_verified": verified})
    emit({"kind": "trial_summary", "verdict": verdict,
          "candidates": 1, "crossings": int(verified), "timeouts": 0})


def run_audit() -> None:
    base = PARENT.seed_graph()
    cycles, _, cotree, constraints = permutation_constraints(base)
    singleton_cycles = {}
    for index, constraint in enumerate(constraints):
        if len(constraint) == 1:
            variable, direction = constraint[0]
            singleton_cycles.setdefault(variable, {
                "constraint_index": index, "cycle": cycles[index],
                "direction": direction,
            })
    forced_ranks = sorted(FIXED_POINT_FREE)
    closed = all(COMPOSE[left][right] in FIXED_POINT_FREE | {IDENTITY}
                 for left in FIXED_POINT_FREE | {IDENTITY}
                 for right in FIXED_POINT_FREE | {IDENTITY})
    commutative = all(COMPOSE[left][right] == COMPOSE[right][left]
                      for left in FIXED_POINT_FREE | {IDENTITY}
                      for right in FIXED_POINT_FREE | {IDENTITY})
    complete = len(singleton_cycles) == len(cotree)
    emit({"kind": "nonabelian_reduction_audit",
          "verdict": "PASS" if complete and closed and commutative else "FAIL",
          "cotree_variables": len(cotree),
          "variables_with_singleton_short_cycle": len(singleton_cycles),
          "singleton_cycles": singleton_cycles,
          "forced_permutation_ranks": forced_ranks,
          "forced_permutations": [PERMS[rank] for rank in forced_ranks],
          "forced_subgroup": "A3_isomorphic_Z3",
          "subgroup_closed": closed, "subgroup_commutative": commutative,
          "conclusion": "every feasible S3 assignment reduces to the parent Z3 class"})


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
        run_audit()
    else:
        run_trial(args.outer_cap)


if __name__ == "__main__":
    main()
