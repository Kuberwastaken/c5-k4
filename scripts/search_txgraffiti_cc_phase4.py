#!/usr/bin/env python3
"""Evaluate one precomputed TxGraffiti C-C phase-four identity partition."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import time
from typing import Sequence

import method_v15_live_search_runtime as live
import search_txgraffiti_cc_live as base
import search_txgraffiti_cc_phase2 as phase2
import txgraffiti_cc_phase4_domain as domain


INTERNAL_STOP_SECONDS = 54.0
SOLVER_CAP_SECONDS = 4.0
TERMINAL_SCHEMA = "c5k4-txgraffiti-cc-phase4-worker-terminal-1.0"
TERMINAL_REASONS = {
    "DOMAIN_EXHAUSTED",
    "DEADLINE_PREFIX",
    "SOLVER_INCOMPLETE",
    "CROSSING_VERIFIED",
}

base.SOLVER_CAP_SECONDS = SOLVER_CAP_SECONDS


def arm_tree_for_partition(partition: int) -> tuple[str, int]:
    if not 0 <= partition < domain.PARTITION_COUNT:
        raise domain.Phase4DomainError("partition is outside the frozen 24-way domain")
    return live.ARMS[partition // 8], partition % 8


def write_terminal(
    path: Path,
    *,
    partition: int,
    reason: str,
    total: int,
    evaluated: int,
    next_index: int,
) -> str:
    if reason not in TERMINAL_REASONS:
        raise domain.Phase4DomainError("invalid worker terminal reason")
    value = {
        "schema": TERMINAL_SCHEMA,
        "partition": partition,
        "terminal_reason": reason,
        "worklist_identities": total,
        "identities_evaluated_this_run": evaluated,
        "next_unscored_index": next_index,
        "domain_exhausted": reason == "DOMAIN_EXHAUSTED",
        "remaining_unscored_identities": total - next_index,
    }
    raw = domain.canonical_json(value)
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def run_partition(
    worklist: Path,
    partition: int,
    terminal: Path,
    labelg: Path,
) -> None:
    arm, tree = arm_tree_for_partition(partition)
    ledger = live.ScientificJsonl.from_environment()
    if (ledger.arm, ledger.tree_index) != (arm, tree):
        raise domain.Phase4DomainError("runtime arm/tree does not match the frozen partition")
    base.database_gate(ledger)
    canonicalizer = live.LabelgCanonicalizer(labelg)
    rows = list(domain.load_jsonl(worklist))
    prior = ""
    for row in rows:
        digest = str(row.get("canonical_sha256", ""))
        if row.get("schema") != domain.IDENTITY_SCHEMA:
            raise domain.Phase4DomainError("worklist contains a non-identity row")
        if domain.partition_for(digest) != partition:
            raise domain.Phase4DomainError("worklist identity is assigned to another partition")
        if digest <= prior:
            raise domain.Phase4DomainError("worklist identities are not strictly sorted")
        prior = digest

    deadline = ledger.started + INTERNAL_STOP_SECONDS
    evaluated = 0
    reason = "DOMAIN_EXHAUSTED"
    next_index = len(rows)
    for index, row in enumerate(rows):
        if time.monotonic() >= deadline:
            reason = "DEADLINE_PREFIX"
            next_index = index
            break
        ledger.counters.proposed += 1
        representative = row.get("representative_state")
        if not isinstance(representative, dict):
            raise domain.Phase4DomainError("identity lacks a representative construction state")
        graph = domain.graph_from_record(representative)
        canonical = canonicalizer.canonicalize(graph)
        if (
            canonical.sha256 != row.get("canonical_sha256")
            or canonical.graph6 != row.get("canonical_graph6")
        ):
            raise domain.Phase4DomainError("representative state does not replay its canonical identity")
        ledger.counters.canonical_unique += 1
        if not base.applicable(graph):
            raise domain.Phase4DomainError("frozen identity no longer satisfies the target hypotheses")
        ledger.counters.hypothesis_survivor += 1
        try:
            result = dict(phase2.exact_profile(graph))
        except RuntimeError as exc:
            if not str(exc).startswith("binary ILP did not prove optimality:"):
                raise
            reason = "SOLVER_INCOMPLETE"
            next_index = index
            break
        objective = result.pop("objective")
        crossing = result.pop("crossing")
        ledger.evaluated_candidate(
            canonical,
            objective=objective,
            crossing=crossing,
            payload={**result, "phase4_partition": partition, "phase4_work_index": index},
        )
        evaluated += 1
        if crossing:
            ledger.checkpoint("crossing_found_independent_replay_passed")
            reason = "CROSSING_VERIFIED"
            next_index = index + 1
            break
    terminal_sha256 = write_terminal(
        terminal,
        partition=partition,
        reason=reason,
        total=len(rows),
        evaluated=evaluated,
        next_index=next_index,
    )
    ledger.checkpoint(f"phase4_terminal_reason:{reason}")
    ledger.checkpoint(f"phase4_terminal_receipt_sha256:{terminal_sha256}")
    ledger.finish()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worklist", type=Path, required=True)
    parser.add_argument("--partition", type=int, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--labelg", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        run_partition(
            args.worklist,
            args.partition,
            args.terminal,
            args.labelg,
        )
    except (OSError, KeyError, TypeError, ValueError, domain.Phase4DomainError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
