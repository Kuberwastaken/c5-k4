#!/usr/bin/env python3
"""Python-3.9-compatible v3 seed-closure constructor.

V3 is deliberately a constructor/diagnostic phase.  It never calls the
periodic-cover adversary and never creates a conjecture candidate.  A
SMALL_BASIS_CEGAR proposal is returned to the inherited evidence writer only
after it covers every active exponent in the frozen cheap seed 1..4096.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import platform
import time
import traceback
from typing import Callable, Optional, Sequence, Tuple

import construct_oeis_a231201_v21 as v21


Assignment = dict[int, int]
SolveOnce = Callable[[list[int], Assignment, float, int], Tuple[str, Optional[Assignment]]]
ROOT = pathlib.Path(__file__).resolve().parents[1]
V3_MANIFEST_PATH = (
    ROOT
    / "results/expansion/live-search-2026-08-14/oeis-a231201-v3-development/manifest.json"
)


def least_uncovered_seed(assignment: Assignment, ordered_exponents: Sequence[int]) -> Optional[int]:
    """Return the least exponent missed by all selected residues, if one exists."""

    for x in ordered_exponents:
        if not any(
            v21.v2.direct_value(q, x) == assignment[q]
            for q in v21.v2.M["primes"]
        ):
            return x
    return None


def least_escape_cegar(
    basis: list[int],
    full_seed: Sequence[int],
    hint: Assignment,
    deadline: float,
    solve_once: SolveOnce,
    on_escape: Callable[[int, int, int, Assignment], None],
    *,
    max_iterations: int,
) -> Tuple[str, Optional[Assignment], int]:
    """Solve, add the exact least missed seed row, and repeat under one cap.

    The function is intentionally independent of OR-Tools so synthetic tests
    can prove the no-premature-emission boundary without evaluating the frozen
    target order table, periodic predicate, source gate, or any target
    assignment.
    """

    attempts = 0
    current_hint = dict(hint)
    last = "UNKNOWN"
    while attempts < max_iterations and time.monotonic() < deadline:
        last, proposal = solve_once(basis, current_hint, deadline, attempts)
        attempts += 1
        if proposal is None:
            if last == "INFEASIBLE":
                return last, None, attempts
            continue
        escape = least_uncovered_seed(proposal, full_seed)
        if escape is None:
            return last, proposal, attempts
        if escape in basis:
            raise ValueError("least-escape CEGAR made no progress")
        previous_rows = len(basis)
        basis.append(escape)
        on_escape(escape, previous_rows, attempts - 1, proposal)
        current_hint = proposal
    return last, None, attempts


def _cp_solve_once(
    basis: list[int],
    cell: str,
    hint: Assignment,
    deadline: float,
    ledger,
    attempt: int,
) -> Tuple[str, Optional[Assignment]]:
    from ortools.sat.python import cp_model

    fixed = v21.v2.cell_fixed(cell)
    inc = v21.v2.incidence(basis)
    model = cp_model.CpModel()
    choose = {}
    ordered = []
    for q in v21.v2.M["primes"][2:]:
        residues = sorted(a for a in range(q) if inc.get((q, a), 0))
        ranked = sorted(
            residues,
            key=lambda residue: (-v21.population_count(inc[q, residue]), residue),
        )
        for residue in ranked:
            choose[q, residue] = model.new_bool_var(f"a_{q}_{residue}")
            ordered.append(choose[q, residue])
        model.add(sum(choose[q, residue] for residue in residues) <= 1)
    for x in basis:
        model.add_bool_or(
            choose[q, v21.v2.direct_value(q, x)]
            for q in v21.v2.M["primes"][2:]
            if (q, v21.v2.direct_value(q, x)) in choose
        )
    for (q, residue), var in choose.items():
        model.add_hint(var, int(hint.get(q) == residue))
    model.add_decision_strategy(
        ordered, cp_model.CHOOSE_FIRST, cp_model.SELECT_MAX_VALUE
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = min(
        v21.v2.M["cp_slice_seconds"], max(0.001, deadline - time.monotonic())
    )
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    status = solver.solve(model)
    name = solver.status_name(status)
    ledger.append(
        {
            "schema": "oeis-a231201-v3-cp-slice-v1",
            "attempt": attempt,
            "status": name,
            "basis_rows": len(basis),
            "wall_time": solver.wall_time,
            "branches": solver.num_branches,
            "conflicts": solver.num_conflicts,
            "remaining_seconds": max(0, deadline - time.monotonic()),
        }
    )
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return name, None
    result = dict(fixed)
    for q in v21.v2.M["primes"][2:]:
        picked = [
            residue
            for residue in range(q)
            if (q, residue) in choose and solver.value(choose[q, residue])
        ]
        result[q] = picked[0] if picked else (hint[q] if q in hint else 0)
    return name, result


def compressed_cp(
    xs: list[int],
    cell: str,
    hint: Assignment,
    deadline: float,
    ledger,
    *,
    growth_pool: Optional[list[int]] = None,
    logical_start: int = 0,
    work: Optional[pathlib.Path] = None,
    artifacts: Optional[dict] = None,
) -> Tuple[str, Optional[Assignment], int]:
    """Delegate normal CP; enforce full-seed closure for SMALL_BASIS only."""

    if growth_pool is None:
        return v21.compressed_cp(
            xs,
            cell,
            hint,
            deadline,
            ledger,
            growth_pool=None,
            logical_start=logical_start,
            work=work,
            artifacts=artifacts,
        )
    if work is None or artifacts is None:
        raise ValueError("v3 CEGAR requires durable work/artifact paths")
    full_seed = v21.v2.active_rows(
        cell,
        list(
            range(
                v21.v2.M["seed"]["lo"],
                v21.v2.M["seed"]["hi"] + 1,
            )
        ),
    )

    def solve_once(
        current_basis: list[int],
        current_hint: Assignment,
        current_deadline: float,
        attempt: int,
    ) -> Tuple[str, Optional[Assignment]]:
        return _cp_solve_once(
            current_basis,
            cell,
            current_hint,
            current_deadline,
            ledger,
            attempt,
        )

    def on_escape(
        escape: int, previous_rows: int, attempt: int, proposal: Assignment
    ) -> None:
        path = work / f"basis-cegar-delta-{attempt:04d}.json"
        proposal_digest = v21.v2.assignment_hash(proposal)
        v21.v2.atomic_json(
            path,
            {
                "schema": "oeis-a231201-v3-least-escape-feedback-v1",
                "attempt": attempt,
                "previous_rows": previous_rows,
                "least_uncovered_x": escape,
                "ordered_basis_rows": previous_rows + 1,
                "proposal_sha256": proposal_digest,
                "proposal": {
                    str(q): proposal[q] for q in v21.v2.M["primes"]
                },
            },
        )
        digest = v21.v2.sha(path)
        artifacts[path.name] = digest
        ledger.append(
            {
                "schema": "oeis-a231201-v3-least-escape-feedback-v1",
                "attempt": attempt,
                "previous_rows": previous_rows,
                "least_uncovered_x": escape,
                "basis_rows": previous_rows + 1,
                "delta_sha256": digest,
                "proposal_sha256": proposal_digest,
                "status": "LEAST_ESCAPE_ADDED",
            }
        )

    status, assignment, attempts = least_escape_cegar(
        xs,
        full_seed,
        hint,
        deadline,
        solve_once,
        on_escape,
        max_iterations=4096,
    )
    if assignment is not None:
        if least_uncovered_seed(assignment, full_seed) is not None:
            raise AssertionError("v3 attempted to emit before full-seed closure")
        ledger.append(
            {
                "schema": "oeis-a231201-v3-seed-closure-v1",
                "status": "FULL_SEED_COVERED",
                "seed_lo": v21.v2.M["seed"]["lo"],
                "seed_hi": v21.v2.M["seed"]["hi"],
                "active_seed_rows": len(full_seed),
                "basis_rows": len(xs),
                "attempts": attempts,
            }
        )
    return status, assignment, attempts


# Preserve v2/v2.1 on disk.  Patch only this process's inherited primitives.
# Three logical rounds now begin with 192, 256, and 320 low-discrepancy rows.
v21.v2.M["small_basis"]["growth_every_rounds"] = 3
v21.v2.M["finalization_reserve_seconds"] = 6


def run(a: argparse.Namespace) -> int:
    started = time.monotonic()
    deadline = started + 48
    ledger = v21.v2.Ledger(a.ledger)
    artifacts = {}
    proposal = None
    status = "PREREQUISITE_NOT_RUN"
    rounds = 0
    fixed = {}
    gate_hash = None
    prerequisite_error = None
    stage_ready = False
    basis = []
    try:
        v21.v2.exact_commit(a.campaign_commit)
        fixed = v21.v2.cell_fixed(a.cell)
        if a.prerequisite_check_exit_code:
            raise ValueError(
                f"outer prerequisite check failed: {a.prerequisite_check_exit_code}"
            )
        v21.v2.verify_gate(a.gate, a.campaign_commit)
        gate_hash = v21.v2.sha(a.gate / "gate-attestation.json")
        stage_ready = True
        status = "CONSTRUCTION_CAP_NO_PROPOSAL"
        full_seed = v21.v2.active_rows(
            a.cell,
            list(
                range(
                    v21.v2.M["seed"]["lo"],
                    v21.v2.M["seed"]["hi"] + 1,
                )
            ),
        )
        if a.arm == "SMALL_BASIS_CEGAR":
            permutation = v21.v2.active_rows(a.cell, v21.v2.low_discrepancy_seed())
            size = 192 + 64 * a.round
            basis = permutation[:size]
        else:
            permutation = None
            basis = list(full_seed)
        initial_doc = {
            "schema": "oeis-a231201-v3-basis-v1",
            "campaign_commit": a.campaign_commit,
            "arm": a.arm,
            "cell": a.cell,
            "round": a.round,
            "fixed": fixed,
            "ordered_exponents": basis,
            "diagnostic_only": True,
        }
        v21.v2.atomic_json(a.work / "basis-0000.json", initial_doc)
        artifacts["basis-0000.json"] = v21.v2.sha(a.work / "basis-0000.json")
        ledger.append(
            {
                "schema": "oeis-a231201-v3-basis-bound-v1",
                "campaign_commit": a.campaign_commit,
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "basis_rows": len(basis),
                "basis_sha256": artifacts["basis-0000.json"],
                "full_seed_rows": len(full_seed),
                "diagnostic_only": True,
            }
        )
        hint, _stats = v21.greedy(basis, a.cell, deadline, rotation=a.round)
        if a.arm == "DETERMINISTIC_GREEDY_REPAIR":
            assignment, stats = v21.greedy(
                basis, a.cell, deadline, rotation=a.round
            )
            rounds = 1
            solver_status = (
                "HEURISTIC_COMPLETE" if stats["uncovered"] == 0 else "HEURISTIC_PARTIAL"
            )
            ledger.append(
                {
                    "schema": "oeis-a231201-v3-greedy-round-v1",
                    "campaign_commit": a.campaign_commit,
                    "arm": a.arm,
                    "cell": a.cell,
                    "round": a.round,
                    "basis_rows": len(basis),
                    **stats,
                    "remaining_seconds": max(0, deadline - time.monotonic()),
                }
            )
        else:
            solver_status, assignment, rounds = compressed_cp(
                basis,
                a.cell,
                hint,
                deadline,
                ledger,
                growth_pool=permutation,
                logical_start=a.round,
                work=a.work,
                artifacts=artifacts,
            )
        final_doc = {
            "schema": "oeis-a231201-v3-basis-final-v1",
            "campaign_commit": a.campaign_commit,
            "arm": a.arm,
            "cell": a.cell,
            "round": a.round,
            "ordered_exponents": basis,
            "diagnostic_only": True,
        }
        v21.v2.atomic_json(a.work / "basis-final.json", final_doc)
        artifacts["basis-final.json"] = v21.v2.sha(a.work / "basis-final.json")
        if assignment is not None and v21.v2.assignment_covers(assignment, basis):
            v21.v2.validate_assignment(assignment, a.cell)
            escape = least_uncovered_seed(assignment, full_seed)
            if escape is not None:
                raise ValueError(
                    f"proposal attempted before full seed closure; least escape {escape}"
                )
            digest = v21.v2.assignment_hash(assignment)
            inc = v21.v2.incidence(basis)
            score = v21.coverage_score(assignment, inc, len(basis))
            proposal = {
                "schema": "oeis-a231201-v3-full-seed-proposal-v1",
                "campaign_commit": a.campaign_commit,
                "base_manifest_sha256": v21.v2.sha(v21.v2.MANIFEST_PATH),
                "v3_manifest_sha256": v21.v2.sha(V3_MANIFEST_PATH),
                "gate_attestation_sha256": gate_hash,
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "slot": 0,
                "basis_rows": len(basis),
                "basis_sha256": artifacts["basis-final.json"],
                "full_seed_lo": v21.v2.M["seed"]["lo"],
                "full_seed_hi": v21.v2.M["seed"]["hi"],
                "active_seed_rows": len(full_seed),
                "proposal_rank": {
                    "uncovered_rows": score[0],
                    "least_prime_prefix": v21.v2.least_prime_prefix(
                        assignment, inc, len(basis)
                    ),
                    "assignment": list(score[2]),
                },
                "proposal_sha256": digest,
                "proposal": {
                    str(q): assignment[q] for q in v21.v2.M["primes"]
                },
                "diagnostic_only": True,
                "target_promotion_authorized": False,
                "mathematical_result_claimed": False,
            }
            v21.v2.atomic_json(a.proposal, proposal)
            artifacts[a.proposal.name] = v21.v2.sha(a.proposal)
            status = "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC"
        elif solver_status == "INFEASIBLE":
            status = "BASIS_INFEASIBLE_UNVERIFIED"
    except BaseException:
        prerequisite_error = traceback.format_exc()
        if stage_ready:
            status = "WORKER_ERROR"
        ledger.append(
            {
                "schema": "oeis-a231201-v3-error-v1",
                "campaign_commit": a.campaign_commit,
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "status": status,
                "traceback": prerequisite_error,
            }
        )
    finally:
        ledger.close()
        exit_status = (
            0
            if status
            in {
                "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC",
                "BASIS_INFEASIBLE_UNVERIFIED",
            }
            else 75
        )
        terminal = {
            "schema": "oeis-a231201-v3-construction-terminal-v1",
            "campaign_commit": a.campaign_commit,
            "base_manifest_sha256": v21.v2.sha(v21.v2.MANIFEST_PATH),
            "v3_manifest_sha256": v21.v2.sha(V3_MANIFEST_PATH),
            "gate_attestation_sha256": gate_hash,
            "python": platform.python_version(),
            "arm": a.arm,
            "cell": a.cell,
            "round": a.round,
            "fixed": fixed,
            "status": status,
            "prerequisite_error": prerequisite_error,
            "basis_rows": len(basis),
            "construction_rounds": rounds,
            "proposal_present": proposal is not None,
            "proposal_sha256": proposal and proposal["proposal_sha256"],
            "proposal_artifact_sha256": (
                v21.v2.sha(a.proposal) if proposal is not None else None
            ),
            "target_promotion_authorized": False,
            "mathematical_result_claimed": False,
            "diagnostic_only": True,
            "artifacts": artifacts,
            "ledger_rows": ledger.seq,
            "final_row_sha256": ledger.previous,
            "ledger_sha256": v21.v2.sha(a.ledger),
            "elapsed_seconds": time.monotonic() - started,
            "search_seconds": 48,
            "internal_seconds": 54,
            "external_seconds": 60,
            "exit_status": exit_status,
        }
        v21.v2.atomic_json(a.terminal, terminal)
    return terminal["exit_status"]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=v21.v2.M["arms"], required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--round", type=int, choices=[0, 1, 2], required=True)
    p.add_argument("--campaign-commit", required=True)
    p.add_argument("--gate", type=pathlib.Path, required=True)
    p.add_argument("--work", type=pathlib.Path, required=True)
    p.add_argument("--ledger", type=pathlib.Path, required=True)
    p.add_argument("--terminal", type=pathlib.Path, required=True)
    p.add_argument("--proposal", type=pathlib.Path, required=True)
    p.add_argument("--prerequisite-check-exit-code", type=int, default=0)
    args = p.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
