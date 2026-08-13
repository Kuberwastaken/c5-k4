#!/usr/bin/env python3
"""Frozen exact four-sheet S4 permutation-lift trial for WOWII #141."""

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
CONTRACT = ROOT / "results/expansion/prospective_formal_141_s4_cover_contract.md"
LEDGER = ROOT / "results/expansion/prospective_formal_141_s4_cover_ledger.jsonl"
CONTRACT_SHA256 = "7c52fc5ac4c792ef81734aa628a3c3a4e08affe8913f1af4653053c671e59b55"
PARENT_PATH = ROOT / "scripts/prospective_formal_oneoff_141.py"
SPEC = importlib.util.spec_from_file_location("wow141_parent_s4", PARENT_PATH)
assert SPEC and SPEC.loader
PARENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PARENT)

PERMS = tuple(sorted(itertools.permutations(range(4))))
PERM_INDEX = {permutation: index for index, permutation in enumerate(PERMS)}
IDENTITY = PERM_INDEX[(0, 1, 2, 3)]


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    """Return left after right."""
    return tuple(left[right[value]] for value in range(4))


COMPOSE = tuple(tuple(PERM_INDEX[compose(left, right)] for right in PERMS)
                for left in PERMS)
INVERSE = []
for permutation in PERMS:
    inverse = [0] * 4
    for source, target in enumerate(permutation):
        inverse[target] = source
    INVERSE.append(PERM_INDEX[tuple(inverse)])
INVERSE = tuple(INVERSE)
FIXED_POINT_FREE = frozenset(
    rank for rank, permutation in enumerate(PERMS)
    if all(permutation[value] != value for value in range(4)))
FULL_DOMAIN = (1 << len(PERMS)) - 1
SINGLETON_RANK = {1 << rank: rank for rank in range(len(PERMS))}


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


def ranks(mask: int):
    return tuple(rank for rank in range(len(PERMS)) if mask & (1 << rank))


def run_gate(outer_cap: float) -> None:
    started = time.monotonic()
    controls = PARENT.controls()
    emit({"kind": "phase_start", "phase": "gate", "controls": len(controls)})
    failures = timeouts = completed = 0
    for index, (name, raw) in enumerate(controls):
        if time.monotonic() - started > outer_cap:
            timeouts += 1
            break
        graph = nx.convert_node_labels_to_integers(raw, ordering="default")
        data = PARENT.invariants(graph)
        try:
            tree, witness, states = PARENT.exact_largest_induced_tree(graph, 10.0)
        except PARENT.SearchTimeout:
            timeouts += 1
            emit({"kind": "gate_timeout", "name": name, "n": len(graph), **data})
            break
        residual = tree - data["target"]
        valid = PARENT.replay_tree(graph, witness, tree)
        failures += residual < 0 or not valid
        completed = index + 1
        emit({"kind": "gate_row", "name": name, "n": len(graph),
              "m": graph.number_of_edges(), "graph6": PARENT.graph6(graph),
              **data, "tree": tree, "tree_witness": witness,
              "tree_states": states, "residual": residual,
              "certificate_valid": valid})
        if failures:
            break
    verdict = "PASS" if completed == len(controls) and not failures and not timeouts else "GATE_FAIL"
    emit({"kind": "gate_summary", "verdict": verdict, "completed": completed,
          "controls": len(controls), "failures": failures,
          "timeouts": timeouts, "seconds": round(time.monotonic() - started, 6)})


def latest(kind: str) -> dict | None:
    if not LEDGER.exists():
        return None
    for line in reversed(LEDGER.read_text(encoding="utf-8").splitlines()):
        row = json.loads(line)
        if row.get("kind") == kind:
            return row
    return None


def latest_gate_passed() -> bool:
    row = latest("gate_summary")
    return row is not None and row.get("verdict") == "PASS"


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
                operations.append((edge_index[edge], 1 if u < v else -1))
        constraints.append(tuple(operations))
    return cycles, tree_edges, cotree, constraints


def product_rank(constraint: tuple, assignment: tuple[int, ...]) -> int:
    product = IDENTITY
    for (_, direction), rank in zip(constraint, assignment):
        operation = rank if direction == 1 else INVERSE[rank]
        product = COMPOSE[operation][product]
    return product


def noncommute(left: int, right: int) -> bool:
    return COMPOSE[left][right] != COMPOSE[right][left]


def assignment_noncommutative(assignment: list[int]) -> bool:
    return any(noncommute(assignment[i], assignment[j])
               for i in range(len(assignment))
               for j in range(i + 1, len(assignment)))


def domains_can_be_noncommutative(domains: list[int]) -> bool:
    for i in range(len(domains)):
        for j in range(i + 1, len(domains)):
            if any(noncommute(left, right)
                   for left in ranks(domains[i]) for right in ranks(domains[j])):
                return True
    return False


def assignment_transitive(assignment: list[int]) -> bool:
    orbit = {0}
    changed = True
    while changed:
        changed = False
        for rank in assignment:
            permutation = PERMS[rank]
            inverse = PERMS[INVERSE[rank]]
            expanded = orbit | {permutation[value] for value in orbit}
            expanded |= {inverse[value] for value in orbit}
            if expanded != orbit:
                orbit = expanded
                changed = True
    return orbit == set(range(4))


def solve_s4(base: nx.Graph, cap: float, state_cap: int = 250_000) -> tuple[str, dict]:
    started = time.monotonic()
    deadline = started + cap
    cycles, tree_edges, cotree, constraints = permutation_constraints(base)
    propagation_order = sorted(range(len(constraints)),
                               key=lambda index: (len(constraints[index]), index))
    states = local_assignments = 0
    cycle_feasible_leaves = abelian_leaves = intransitive_leaves = 0
    cache: dict[tuple[int, tuple[int, ...]], tuple[int, ...] | None] = {}

    def supports(constraint_index: int, masks: tuple[int, ...]):
        nonlocal local_assignments
        key = (constraint_index, masks)
        if key in cache:
            return cache[key]
        constraint = constraints[constraint_index]
        result = [0] * len(constraint)
        any_valid = False
        for assignment in itertools.product(*(ranks(mask) for mask in masks)):
            local_assignments += 1
            if local_assignments & 4095 == 0 and time.monotonic() > deadline:
                raise SolverTimeout
            if product_rank(constraint, assignment) in FIXED_POINT_FREE:
                any_valid = True
                for position, rank in enumerate(assignment):
                    result[position] |= 1 << rank
        value = tuple(result) if any_valid else None
        cache[key] = value
        return value

    def propagate(domains: list[int]) -> list[int] | None:
        changed = True
        while changed:
            if time.monotonic() > deadline:
                raise SolverTimeout
            changed = False
            for constraint_index in propagation_order:
                constraint = constraints[constraint_index]
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

    def search(domains: list[int]) -> list[int] | None:
        nonlocal states, cycle_feasible_leaves, abelian_leaves, intransitive_leaves
        states += 1
        if states > state_cap or time.monotonic() > deadline:
            raise SolverTimeout
        domains = propagate(domains.copy())
        if domains is None or not domains_can_be_noncommutative(domains):
            return None
        if all(domain in SINGLETON_RANK for domain in domains):
            assignment = [SINGLETON_RANK[domain] for domain in domains]
            cycle_feasible_leaves += 1
            is_noncommutative = assignment_noncommutative(assignment)
            is_transitive = assignment_transitive(assignment)
            abelian_leaves += not is_noncommutative
            intransitive_leaves += not is_transitive
            if is_noncommutative and is_transitive:
                return assignment
            return None
        variable = next(index for index, domain in enumerate(domains)
                        if domain not in SINGLETON_RANK)
        for rank in range(len(PERMS)):
            if domains[variable] & (1 << rank):
                branch = domains.copy()
                branch[variable] = 1 << rank
                result = search(branch)
                if result is not None:
                    return result
        return None

    try:
        solution = search([FULL_DOMAIN] * len(cotree))
    except SolverTimeout:
        return "timeout", {
            "states": states, "state_cap": state_cap, "cycles": len(cycles),
            "tree_edges": tree_edges, "cotree_edges": cotree,
            "cache_entries": len(cache), "local_assignments": local_assignments,
            "cycle_feasible_leaves": cycle_feasible_leaves,
            "abelian_leaves": abelian_leaves,
            "intransitive_leaves": intransitive_leaves,
            "seconds": round(time.monotonic() - started, 6),
        }
    return ("infeasible" if solution is None else "optimal"), {
        "states": states, "state_cap": state_cap, "cycles": len(cycles),
        "tree_edges": tree_edges, "cotree_edges": cotree,
        "permutation_ranks": solution,
        "permutations": None if solution is None else [PERMS[rank] for rank in solution],
        "cache_entries": len(cache), "local_assignments": local_assignments,
        "cycle_feasible_leaves": cycle_feasible_leaves,
        "abelian_leaves": abelian_leaves,
        "intransitive_leaves": intransitive_leaves,
        "noncommutative": False if solution is None else assignment_noncommutative(solution),
        "transitive": False if solution is None else assignment_transitive(solution),
        "seconds": round(time.monotonic() - started, 6),
    }


def run_solver(cap: float) -> None:
    if not latest_gate_passed():
        raise RuntimeError("latest S4 database gate has not passed")
    status, meta = solve_s4(PARENT.seed_graph(), cap)
    emit({"kind": "solver_result", "status": status, **meta})
    if status == "infeasible":
        emit({"kind": "trial_summary", "verdict": "NO_APPLICABLE_CANDIDATES"})
    elif status == "timeout":
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS",
              "reason": "S4_solver"})


def permutation_lift(base: nx.Graph, cotree: list, assignment: list[int]) -> nx.Graph:
    rank_by_edge = {tuple(edge): rank for edge, rank in zip(cotree, assignment)}
    lift = nx.Graph()
    lift.add_nodes_from(range(4 * len(base)))
    for raw_u, raw_v in base.edges():
        u, v = sorted((raw_u, raw_v))
        permutation = PERMS[rank_by_edge.get((u, v), IDENTITY)]
        for sheet in range(4):
            lift.add_edge(4 * u + sheet, 4 * v + permutation[sheet])
    return lift


def validate_lift(base: nx.Graph, lift: nx.Graph, meta: dict) -> dict:
    cycles, _, cotree, constraints = permutation_constraints(base)
    assignment = meta["permutation_ranks"]
    products = []
    for constraint in constraints:
        local = tuple(assignment[variable] for variable, _ in constraint)
        products.append(product_rank(constraint, local))
    fixed_point_free = all(rank in FIXED_POINT_FREE for rank in products)
    fiber_sizes = [sum(vertex // 4 == base_vertex for vertex in lift)
                   for base_vertex in base]
    covering_bijection = True
    for vertex in lift:
        base_vertex = vertex // 4
        projected = [neighbor // 4 for neighbor in lift[vertex]]
        covering_bijection &= (len(projected) == base.degree(base_vertex)
                               and sorted(projected) == sorted(base[base_vertex]))
    lambda_max, local_values, local_witnesses = PARENT.local_profile(lift)
    girth, girth_witness = PARENT.girth_with_witness(lift)
    simple = not lift.is_multigraph() and nx.number_of_selfloops(lift) == 0
    connected = nx.is_connected(lift)
    noncommutative = assignment_noncommutative(assignment)
    transitive = assignment_transitive(assignment)
    valid = (simple and connected and fiber_sizes == [4] * len(base)
             and covering_bijection and fixed_point_free
             and noncommutative and transitive
             and lambda_max == 6 and all(value == 6 for value in local_values)
             and girth >= 6 and len(lift) == 60 and lift.number_of_edges() == 180)
    return {
        "simple": simple, "connected": connected, "n": len(lift),
        "m": lift.number_of_edges(), "fiber_sizes": fiber_sizes,
        "covering_bijection": covering_bijection,
        "cycles_checked": len(cycles), "monodromy_ranks": products,
        "fixed_point_free": fixed_point_free,
        "noncommutative": noncommutative, "transitive": transitive,
        "lambda_max": lambda_max, "local_values": local_values,
        "local_witnesses": local_witnesses,
        "girth": girth, "girth_witness": girth_witness,
        "validated": valid,
    }


def run_candidate(cap: float) -> None:
    meta = latest("solver_result")
    if meta is None or meta.get("status") != "optimal":
        raise RuntimeError("no exact optimal S4 assignment in ledger")
    started = time.monotonic()
    base = PARENT.seed_graph()
    lift = permutation_lift(base, meta["cotree_edges"], meta["permutation_ranks"])
    validation = validate_lift(base, lift, meta)
    data = PARENT.invariants(lift)
    common = {
        "name": "canonical-nonabelian-S4-lift-comp-C5K3",
        "n": len(lift), "m": lift.number_of_edges(),
        "graph6": PARENT.graph6(lift), **data,
        "permutation_ranks": meta["permutation_ranks"],
        "permutations": meta["permutations"],
        "cotree_edges": meta["cotree_edges"], "validation": validation,
    }
    emit({"kind": "candidate_constructed", **common})
    if not validation["validated"]:
        emit({"kind": "trial_summary", "verdict": "GATE_FAIL",
              "reason": "cover_validation"})
        return
    remaining = max(0.1, cap - (time.monotonic() - started))
    try:
        witness, states = PARENT.find_target_tree(lift, data["target"], remaining)
    except PARENT.SearchTimeout:
        emit({"kind": "candidate_result", **common,
              "verdict": "UNRESOLVED_TIMEOUT", "stage": "target_tree"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return
    if witness is not None:
        valid = PARENT.replay_tree(lift, witness, data["target"])
        emit({"kind": "candidate_result", **common, "verdict": "HOLD",
              "tree_lower_bound": data["target"], "tree_witness": witness,
              "tree_states": states, "certificate_valid": valid})
        emit({"kind": "trial_summary", "verdict": "HOLD_BOUNDED",
              "candidates": 1, "crossings": 0, "timeouts": 0})
        return
    remaining = max(0.1, cap - (time.monotonic() - started))
    try:
        tree, witness, states = PARENT.exact_largest_induced_tree(lift, remaining)
    except PARENT.SearchTimeout:
        emit({"kind": "candidate_result", **common,
              "verdict": "UNRESOLVED_TIMEOUT", "stage": "exact_tree"})
        emit({"kind": "trial_summary", "verdict": "HOLD_WITH_TIMEOUTS"})
        return
    residual = tree - data["target"]
    verified = residual < 0 and PARENT.replay_tree(lift, witness, tree)
    verdict = "CROSSING_VERIFIED" if verified else "GATE_FAIL"
    emit({"kind": "candidate_result", **common, "verdict": verdict,
          "tree": tree, "tree_witness": witness, "tree_states": states,
          "residual": residual, "independent_verified": verified})
    emit({"kind": "trial_summary", "verdict": verdict,
          "candidates": 1, "crossings": int(verified), "timeouts": 0})


def run_audit() -> None:
    base = PARENT.seed_graph()
    cycles, _, cotree, constraints = permutation_constraints(base)
    singleton = {}
    for index, constraint in enumerate(constraints):
        if len(constraint) == 1:
            variable, direction = constraint[0]
            singleton.setdefault(variable, {"constraint_index": index,
                                            "cycle": cycles[index],
                                            "direction": direction})
    fpf = sorted(FIXED_POINT_FREE)
    types = {"four_cycles": [], "double_transpositions": []}
    for rank in fpf:
        permutation = PERMS[rank]
        if all(permutation[permutation[value]] == value for value in range(4)):
            types["double_transpositions"].append(rank)
        else:
            types["four_cycles"].append(rank)
    pair = next((left, right) for left in fpf for right in fpf
                if noncommute(left, right))
    emit({
        "kind": "s4_freedom_audit", "verdict": "PASS",
        "cotree_variables": len(cotree),
        "variables_with_singleton_short_cycle": len(singleton),
        "short_cycles": len(cycles), "fixed_point_free_ranks": fpf,
        **types, "noncommuting_rank_pair": pair,
        "noncommuting_permutations": [PERMS[pair[0]], PERMS[pair[1]]],
        "conclusion": "singleton constraints restrict to nine derangements, not an abelian subgroup",
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("gate", "audit", "solve", "candidate"))
    parser.add_argument("--cap", type=float, default=55.0)
    args = parser.parse_args()
    if not 1 < args.cap <= 55:
        parser.error("cap must be in (1,55]")
    signal.alarm(59)
    check_contract()
    if args.phase == "gate":
        run_gate(args.cap)
    elif args.phase == "audit":
        run_audit()
    elif args.phase == "solve":
        run_solver(args.cap)
    else:
        run_candidate(args.cap)


if __name__ == "__main__":
    main()
