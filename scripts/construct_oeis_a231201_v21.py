#!/usr/bin/env python3
"""Python-3.9-compatible v2.1 constructor entry point.

The v2 constructor is immutable evidence.  This module replaces only the two
constructor routines that used ``int.bit_count`` and then delegates the frozen
CLI/run protocol to v2.
"""
from __future__ import annotations

import pathlib
import time

import construct_oeis_a231201_v2 as v2


def population_count(value: int) -> int:
    """Return the number of set bits using operations available in Python 3.9."""
    if value < 0:
        raise ValueError("population_count requires a nonnegative integer")
    return bin(value).count("1")


def coverage_score(
    assignment: dict[int, int],
    inc: dict[tuple[int, int], int],
    row_count: int,
    skip: int | None = None,
    replace: tuple[int, int] | None = None,
) -> tuple[int, int, tuple[int, ...]]:
    once = 0
    multiple = 0
    for q in v2.M["primes"][2:]:
        if q == skip:
            continue
        bits = inc.get((q, assignment[q]), 0)
        new_multiple = multiple | (once & bits)
        once = (once ^ bits) & ~new_multiple
        multiple = new_multiple
    if replace is not None:
        bits = inc.get(replace, 0)
        new_multiple = multiple | (once & bits)
        once = (once ^ bits) & ~new_multiple
    mask = (1 << row_count) - 1
    score_assignment = tuple(
        assignment[q] if replace is None or q != replace[0] else replace[1]
        for q in v2.M["primes"]
    )
    return (
        population_count(mask & ~(once | multiple)),
        population_count(once),
        score_assignment,
    )


def greedy(
    xs: list[int], cell: str, deadline: float, rotation: int = 0
) -> tuple[dict[int, int], dict]:
    inc = v2.incidence(xs)
    assignment = v2.cell_fixed(cell)
    uncovered = (1 << len(xs)) - 1
    moves = 0
    for q in v2.M["primes"][2:]:
        a = min(
            range(q),
            key=lambda residue: (
                -population_count(inc.get((q, residue), 0) & uncovered),
                residue,
            ),
        )
        assignment[q] = a
        uncovered &= ~inc.get((q, a), 0)
    best = coverage_score(assignment, inc, len(xs))
    improved = True
    while (
        time.monotonic() < deadline
        and moves < v2.M["greedy"]["max_moves"]
        and uncovered
    ):
        improved = False
        for q in v2.M["primes"][2:]:
            if time.monotonic() >= deadline:
                break
            choice = min(
                range(q),
                key=lambda residue: coverage_score(
                    assignment, inc, len(xs), skip=q, replace=(q, residue)
                ),
            )
            if choice != assignment[q]:
                assignment[q] = choice
                moves += 1
                improved = True
        covered = 0
        for q in v2.M["primes"][2:]:
            covered |= inc.get((q, assignment[q]), 0)
        uncovered = ((1 << len(xs)) - 1) & ~covered
        score = coverage_score(assignment, inc, len(xs))
        if score < best:
            best = score
        if uncovered and not improved:
            row = (uncovered & -uncovered).bit_length() - 1
            q = v2.M["primes"][
                2
                + (
                    (row + rotation + moves)
                    // v2.M["greedy"]["perturbation_period"]
                    % 53
                )
            ]
            assignment[q] = v2.direct_value(q, xs[row])
            moves += 1
    final_score = coverage_score(assignment, inc, len(xs))
    return assignment, {
        "moves": moves,
        "uncovered": final_score[0],
        "singly_covered": final_score[1],
        "score_assignment": list(final_score[2]),
        "best_lexicographic_score": {
            "uncovered": best[0],
            "singly_covered": best[1],
            "assignment": list(best[2]),
        },
        "least_prime_prefix": v2.least_prime_prefix(assignment, inc, len(xs)),
    }


def compressed_cp(
    xs: list[int],
    cell: str,
    hint: dict[int, int],
    deadline: float,
    ledger: v2.Ledger,
    *,
    growth_pool: list[int] | None = None,
    logical_start: int = 0,
    work: pathlib.Path | None = None,
    artifacts: dict | None = None,
) -> tuple[str, dict[int, int] | None, int]:
    from ortools.sat.python import cp_model

    fixed = v2.cell_fixed(cell)
    inc = v2.incidence(xs)
    rounds = 0
    last = "UNKNOWN"
    while rounds < v2.M["cp_slices_per_construction"] and time.monotonic() < deadline:
        logical = logical_start + rounds
        if (
            growth_pool is not None
            and logical > 0
            and logical % v2.M["small_basis"]["growth_every_rounds"] == 0
        ):
            old = len(xs)
            wanted = min(
                len(growth_pool), old + v2.M["small_basis"]["growth_rows"]
            )
            delta = [x for x in growth_pool if x not in set(xs)][: wanted - old]
            xs.extend(delta)
            inc = v2.incidence(xs)
            delta_path = work / f"basis-delta-{logical:04d}.json"
            v2.atomic_json(
                delta_path,
                {
                    "schema": "oeis-a231201-v2-basis-delta-v1",
                    "logical_master_round": logical,
                    "previous_rows": old,
                    "added_exponents": delta,
                    "ordered_basis_rows": len(xs),
                },
            )
            artifacts[delta_path.name] = v2.sha(delta_path)
            ledger.append(
                {
                    "schema": "oeis-a231201-v2-basis-growth-v1",
                    "logical_master_round": logical,
                    "previous_rows": old,
                    "added_rows": len(delta),
                    "basis_rows": len(xs),
                    "delta_sha256": artifacts[delta_path.name],
                }
            )
        model = cp_model.CpModel()
        choose = {}
        ordered = []
        for q in v2.M["primes"][2:]:
            residues = sorted(a for a in range(q) if inc.get((q, a), 0))
            ranked = sorted(
                residues,
                key=lambda residue: (-population_count(inc[q, residue]), residue),
            )
            for residue in ranked:
                choose[q, residue] = model.new_bool_var(f"a_{q}_{residue}")
                ordered.append(choose[q, residue])
            model.add(sum(choose[q, residue] for residue in residues) <= 1)
        for i, x in enumerate(xs):
            model.add_bool_or(
                choose[q, v2.direct_value(q, x)]
                for q in v2.M["primes"][2:]
                if (q, v2.direct_value(q, x)) in choose
            )
        for (q, residue), var in choose.items():
            model.add_hint(var, int(hint.get(q) == residue))
        model.add_decision_strategy(
            ordered, cp_model.CHOOSE_FIRST, cp_model.SELECT_MAX_VALUE
        )
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(
            v2.M["cp_slice_seconds"], max(0.001, deadline - time.monotonic())
        )
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = 0
        status = solver.solve(model)
        last = solver.status_name(status)
        rounds += 1
        ledger.append(
            {
                "schema": "oeis-a231201-v2-cp-slice-v1",
                "slice": rounds - 1,
                "status": last,
                "basis_rows": len(xs),
                "wall_time": solver.wall_time,
                "branches": solver.num_branches,
                "conflicts": solver.num_conflicts,
                "remaining_seconds": max(0, deadline - time.monotonic()),
            }
        )
        if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
            result = dict(fixed)
            for q in v2.M["primes"][2:]:
                picked = [
                    residue
                    for residue in range(q)
                    if (q, residue) in choose and solver.value(choose[q, residue])
                ]
                result[q] = picked[0] if picked else (hint[q] if q in hint else 0)
            return last, result, rounds
        if status == cp_model.INFEASIBLE:
            return last, None, rounds
    return last, None, rounds


# The frozen v2 run function resolves these names in the v2 module.  Replace
# exactly the incompatible implementations before exposing its unchanged CLI.
v2.coverage_score = coverage_score
v2.greedy = greedy
v2.compressed_cp = compressed_cp


def main() -> int:
    return v2.main()


if __name__ == "__main__":
    raise SystemExit(main())
