#!/usr/bin/env python3
"""V2.2 exact adversary with bounded, O(1) deadline finalization."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import time
import traceback
from typing import Callable, Iterable

from oeis_a231201_v2_common import (
    M,
    MANIFEST_PATH,
    Ledger,
    assignment_hash,
    atomic_json,
    exact_commit,
    order_table,
    periodic_value,
    sha,
    validate_assignment,
)
from prepare_oeis_a231201_gate import verify as verify_gate


SEARCH_SECONDS = 48
FINALIZATION_RESERVE_SECONDS = 6
STREAM_SCHEME = "ascii-r-comma-m-newline-insertion-order-v1"


class QueueStreamDigest:
    """The historical queue hash, updated once as each state is appended."""

    def __init__(self) -> None:
        self._hash = hashlib.sha256()
        self.count = 0

    def append(self, state: tuple[int, int]) -> None:
        r, modulus = state
        self._hash.update(f"{r},{modulus}\n".encode("ascii"))
        self.count += 1

    def hexdigest(self) -> str:
        # hashlib.digest() copies its fixed-size internal state.  It does not
        # revisit the queue, so this remains O(1) at the deadline.
        return self._hash.hexdigest()


def refine(
    assignment: dict[int, int],
    deadline: float,
    ledger: Ledger,
    *,
    table: Iterable[tuple[int, int, int]] | None = None,
    value_at: Callable[[int, int], int] = periodic_value,
    clock: Callable[[], float] = time.monotonic,
) -> dict:
    """Refine every live CRT state, stopping with a durable exact prefix.

    Completed levels and partial levels retain deterministic insertion order.
    Sorting was never part of the set semantics: each generated state is still
    visited exactly once at the next level.  Avoiding the historical sort also
    prevents an unbounded operation from starting after the search deadline.
    """

    states = [(0, 1)]
    for level, (q, order, modulus) in enumerate(order_table() if table is None else table):
        following: list[tuple[int, int]] = []
        digest = QueueStreamDigest()
        processed = 0
        best: tuple[int, int] | None = None
        for input_index, (r, current) in enumerate(states):
            limit = math.lcm(current, modulus)
            for split_index, value in enumerate(range(r, limit, current)):
                if clock() >= deadline:
                    cursor = {
                        "input_index": input_index,
                        "input_residue": r,
                        "input_modulus": current,
                        "split_index": split_index,
                        "split_value": value,
                    }
                    result = {
                        "status": "ADVERSARY_DEADLINE",
                        "level": level,
                        "q": q,
                        "cursor": cursor,
                        "input_states": len(states),
                        "input_processed": processed,
                        "partial_states": digest.count,
                        "partial_queue_sha256": digest.hexdigest(),
                        "partial_queue_hash_scheme": STREAM_SCHEME,
                    }
                    ledger.append(
                        {
                            "schema": "oeis-a231201-v22-adversary-level-v1",
                            **result,
                        }
                    )
                    return result
                if value_at(q, value) != assignment[q]:
                    state = (value, limit)
                    following.append(state)
                    digest.append(state)
                    key = (value if value > 0 else limit, limit)
                    if best is None or key < (
                        best[0] if best[0] > 0 else best[1],
                        best[1],
                    ):
                        best = state
            processed += 1
        ledger.append(
            {
                "schema": "oeis-a231201-v22-adversary-level-v1",
                "level": level,
                "q": q,
                "order": order,
                "modulus": modulus,
                "status": "DOMAIN_EXHAUSTED",
                "input_states": len(states),
                "input_processed": processed,
                "output_states": digest.count,
                "queue_sha256": digest.hexdigest(),
                "queue_hash_scheme": STREAM_SCHEME,
            }
        )
        states = following
        if not states:
            return {"status": "COMPLETE_COVER", "level": level, "states": []}
    # `best` was maintained while appending the final level, so neither a sort
    # nor a linear min/hash pass is needed after the last deadline check.
    assert best is not None
    r, modulus = best
    return {
        "status": "UNCOVERED_CLASS",
        "x": r if r > 0 else modulus,
        "residue": r,
        "modulus": modulus,
        "final_states": len(states),
        "queue_sha256": digest.hexdigest(),
        "queue_hash_scheme": STREAM_SCHEME,
    }


def run(a: argparse.Namespace) -> int:
    started = time.monotonic()
    ledger = Ledger(a.ledger)
    candidate = None
    gate_hash = None
    assignment_digest = None
    assignment_artifact_digest = None
    if not a.assignment.is_file():
        ledger.append(
            {
                "schema": "oeis-a231201-v2-adversary-not-run-v1",
                "campaign_commit": a.campaign_commit,
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "slot": a.slot,
                "status": "NOT_RUN",
                "reason": "ABSENT_ASSIGNMENT",
            }
        )
        ledger.close()
        atomic_json(
            a.output,
            {
                "schema": "oeis-a231201-v2-adversary-terminal-v1",
                "campaign_commit": a.campaign_commit,
                "manifest_sha256": sha(MANIFEST_PATH),
                "gate_attestation_sha256": None,
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "slot": a.slot,
                "assignment_sha256": None,
                "assignment_artifact_sha256": None,
                "status": "NOT_RUN",
                "result": None,
                "candidate_present": False,
                "candidate_sha256": None,
                "exit_status": None,
                "ledger_rows": ledger.seq,
                "final_row_sha256": ledger.previous,
                "ledger_sha256": sha(a.ledger),
                "elapsed_seconds": time.monotonic() - started,
                "operational_version": "v2.2",
                "search_seconds": SEARCH_SECONDS,
                "finalization_reserve_seconds": FINALIZATION_RESERVE_SECONDS,
            },
        )
        return 78
    status = "PREREQUISITE_NOT_RUN"
    result = {"status": "PREREQUISITE_NOT_RUN"}
    try:
        if a.prerequisite_check_exit_code:
            raise ValueError(f"outer prerequisite check failed: {a.prerequisite_check_exit_code}")
        exact_commit(a.campaign_commit)
        verify_gate(a.gate, a.campaign_commit)
        gate_hash = sha(a.gate / "gate-attestation.json")
        doc = json.loads(a.assignment.read_text())
        assignment = {int(k): int(v) for k, v in doc["assignment"].items()}
        validate_assignment(assignment, a.cell)
        assignment_digest = assignment_hash(assignment)
        assignment_artifact_digest = sha(a.assignment)
        if (
            doc.get("schema") != "oeis-a231201-v2-assignment-v1"
            or doc.get("assignment_sha256") != assignment_digest
            or doc.get("manifest_sha256") != sha(MANIFEST_PATH)
            or doc.get("gate_attestation_sha256") != gate_hash
        ):
            raise ValueError("assignment schema/hash/source drift")
        if (
            doc.get("campaign_commit"),
            doc.get("arm"),
            doc.get("cell"),
            doc.get("round"),
            doc.get("slot"),
        ) != (a.campaign_commit, a.arm, a.cell, a.round, a.slot):
            raise ValueError("assignment identity drift")
        result = refine(assignment, started + SEARCH_SECONDS, ledger)
        status = (
            "COVER_FOUND_PENDING_VERIFY"
            if result["status"] == "COMPLETE_COVER"
            else result["status"]
        )
        if status == "COVER_FOUND_PENDING_VERIFY":
            candidate = {
                "schema": "oeis-a231201-v2-cover-pending-v1",
                "campaign_commit": a.campaign_commit,
                "manifest_sha256": sha(MANIFEST_PATH),
                "gate_attestation_sha256": doc["gate_attestation_sha256"],
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "slot": a.slot,
                "assignment_sha256": doc["assignment_sha256"],
                "assignment": doc["assignment"],
            }
            atomic_json(a.candidate, candidate)
    except BaseException:
        if gate_hash is not None:
            status = "WORKER_ERROR"
            result = {"status": "WORKER_ERROR"}
        ledger.append(
            {
                "schema": "oeis-a231201-v22-adversary-error-v1",
                "campaign_commit": a.campaign_commit,
                "arm": a.arm,
                "cell": a.cell,
                "round": a.round,
                "slot": a.slot,
                "status": status,
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        ledger.close()
        receipt = {
            "schema": "oeis-a231201-v2-adversary-terminal-v1",
            "campaign_commit": a.campaign_commit,
            "manifest_sha256": sha(MANIFEST_PATH),
            "gate_attestation_sha256": gate_hash,
            "arm": a.arm,
            "cell": a.cell,
            "round": a.round,
            "slot": a.slot,
            "assignment_sha256": assignment_digest,
            "assignment_artifact_sha256": assignment_artifact_digest,
            "status": status,
            "result": result,
            "candidate_present": candidate is not None,
            "candidate_sha256": sha(a.candidate) if candidate is not None else None,
            "ledger_rows": ledger.seq,
            "final_row_sha256": ledger.previous,
            "ledger_sha256": sha(a.ledger),
            "elapsed_seconds": time.monotonic() - started,
            "exit_status": 0
            if status in {"COVER_FOUND_PENDING_VERIFY", "UNCOVERED_CLASS"}
            else 75,
            "operational_version": "v2.2",
            "search_seconds": SEARCH_SECONDS,
            "finalization_reserve_seconds": FINALIZATION_RESERVE_SECONDS,
        }
        atomic_json(a.output, receipt)
    return receipt["exit_status"]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--assignment", type=pathlib.Path, required=True)
    p.add_argument("--ledger", type=pathlib.Path, required=True)
    p.add_argument("--output", type=pathlib.Path, required=True)
    p.add_argument("--candidate", type=pathlib.Path, required=True)
    p.add_argument("--gate", type=pathlib.Path, required=True)
    p.add_argument("--prerequisite-check-exit-code", type=int, default=0)
    p.add_argument("--campaign-commit", required=True)
    p.add_argument("--arm", choices=M["arms"], required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--round", type=int, required=True)
    p.add_argument("--slot", type=int, choices=[0], required=True)
    return run(p.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
