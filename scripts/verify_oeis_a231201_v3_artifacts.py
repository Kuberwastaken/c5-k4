#!/usr/bin/env python3
"""Independent structural checks for v3 constructor/diagnostic artifacts."""
from __future__ import annotations

import argparse
import json
import pathlib

import construct_oeis_a231201_v2 as v2_constructor
import construct_oeis_a231201_v21 as v21_constructor
import oeis_a231201_v2_common as common
import verify_oeis_a231201_v2_artifacts as inherited
from construct_oeis_a231201_v3 import V3_MANIFEST_PATH


def _assignment(value: dict, cell: str) -> dict[int, int]:
    assignment = {int(k): int(v) for k, v in value.items()}
    common.validate_assignment(assignment, cell)
    return assignment


def _covers(assignment: dict[int, int], xs: list[int]) -> bool:
    return all(
        any(
            inherited.direct_value(q, x) == assignment[q]
            for q in inherited.M["primes"]
        )
        for x in xs
    )


def _least_uncovered(assignment: dict[int, int], xs: list[int]):
    for x in xs:
        if not any(
            inherited.direct_value(q, x) == assignment[q]
            for q in inherited.M["primes"]
        ):
            return x
    return None


def verify_v3(a: argparse.Namespace, terminal: dict) -> None:
    rows = [json.loads(line) for line in a.ledger.read_text().splitlines()]
    if terminal.get("schema") != "oeis-a231201-v3-construction-terminal-v1":
        raise ValueError("v3 terminal schema drift")
    if terminal.get("status") not in {
        "PREREQUISITE_NOT_RUN",
        "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC",
        "BASIS_INFEASIBLE_UNVERIFIED",
        "CONSTRUCTION_CAP_NO_PROPOSAL",
        "WORKER_ERROR",
    }:
        raise ValueError("v3 terminal vocabulary drift")
    if (
        terminal.get("base_manifest_sha256"),
        terminal.get("v3_manifest_sha256"),
    ) != (common.sha(common.MANIFEST_PATH), common.sha(V3_MANIFEST_PATH)):
        raise ValueError("v3 manifest binding drift")
    if (
        terminal.get("search_seconds"),
        terminal.get("internal_seconds"),
        terminal.get("external_seconds"),
    ) != (48, 54, 60):
        raise ValueError("v3 budget drift")
    if (
        terminal.get("diagnostic_only"),
        terminal.get("target_promotion_authorized"),
        terminal.get("mathematical_result_claimed"),
    ) != (True, False, False):
        raise ValueError("v3 diagnostic trust boundary drift")
    forbidden_terminal_keys = {
        key
        for key in terminal
        if "candidate" in key.lower()
        or "pending" in key.lower()
        or "adversary" in key.lower()
    }
    if forbidden_terminal_keys:
        raise ValueError("v3 terminal contains forbidden target-stage vocabulary")
    present = a.payload.is_file()
    if present != bool(terminal.get("proposal_present")):
        raise ValueError("v3 proposal presence drift")
    if present != (
        terminal.get("status") == "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC"
    ):
        raise ValueError("v3 proposal/status drift")
    expected_exit = (
        0
        if terminal.get("status")
        in {
            "FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC",
            "BASIS_INFEASIBLE_UNVERIFIED",
        }
        else 75
    )
    if terminal.get("exit_status") != expected_exit:
        raise ValueError("v3 status/exit drift")
    if not present and (
        terminal.get("proposal_sha256") is not None
        or terminal.get("proposal_artifact_sha256") is not None
    ):
        raise ValueError("absent v3 proposal has a digest")
    if terminal.get("status") == "PREREQUISITE_NOT_RUN":
        if terminal.get("gate_attestation_sha256") is not None:
            raise ValueError("v3 prerequisite gate encoding drift")
    elif terminal.get("gate_attestation_sha256") != inherited.verified_gate(a):
        raise ValueError("v3 gate binding drift")
    for relative, digest in terminal.get("artifacts", {}).items():
        path = a.work / relative if relative.startswith("basis-") else a.payload.parent / relative
        if not path.is_file() or common.sha(path) != digest:
            raise ValueError("v3 artifact binding drift")

    initial_path = a.work / "basis-0000.json"
    final_path = a.work / "basis-final.json"
    if terminal.get("status") == "PREREQUISITE_NOT_RUN":
        if (
            present
            or terminal.get("basis_rows") != 0
            or terminal.get("artifacts")
            or initial_path.exists()
            or final_path.exists()
        ):
            raise ValueError("v3 prerequisite artifact encoding drift")
        return
    if not initial_path.is_file() or not final_path.is_file():
        if terminal.get("status") != "WORKER_ERROR":
            raise ValueError("v3 ready stage lacks basis evidence")
        return

    full_seed = common.active_rows(
        a.cell,
        list(range(common.M["seed"]["lo"], common.M["seed"]["hi"] + 1)),
    )
    if present:
        proposal_doc = json.loads(a.payload.read_text())
        proposal = _assignment(proposal_doc.get("proposal", {}), a.cell)
        if proposal_doc.get("schema") != "oeis-a231201-v3-full-seed-proposal-v1":
            raise ValueError("v3 proposal schema drift")
        if (
            proposal_doc.get("base_manifest_sha256"),
            proposal_doc.get("v3_manifest_sha256"),
            proposal_doc.get("gate_attestation_sha256"),
            proposal_doc.get("campaign_commit"),
            proposal_doc.get("arm"),
            proposal_doc.get("cell"),
            proposal_doc.get("round"),
            proposal_doc.get("slot"),
        ) != (
            common.sha(common.MANIFEST_PATH),
            common.sha(V3_MANIFEST_PATH),
            terminal.get("gate_attestation_sha256"),
            a.campaign_commit,
            a.arm,
            a.cell,
            a.round,
            0,
        ):
            raise ValueError("v3 proposal identity drift")
        if (
            proposal_doc.get("full_seed_lo"),
            proposal_doc.get("full_seed_hi"),
            proposal_doc.get("active_seed_rows"),
        ) != (common.M["seed"]["lo"], common.M["seed"]["hi"], len(full_seed)):
            raise ValueError("v3 proposal seed-bound drift")
        if (
            proposal_doc.get("diagnostic_only"),
            proposal_doc.get("target_promotion_authorized"),
            proposal_doc.get("mathematical_result_claimed"),
        ) != (True, False, False):
            raise ValueError("v3 proposal trust boundary drift")
        if any(
            "candidate" in key.lower()
            or "pending" in key.lower()
            or "adversary" in key.lower()
            for key in proposal_doc
        ):
            raise ValueError("v3 proposal contains forbidden target-stage vocabulary")
        if not _covers(proposal, full_seed):
            raise ValueError("v3 proposal escaped full cheap-seed closure")
        digest = common.assignment_hash(proposal)
        if (
            proposal_doc.get("proposal_sha256"),
            terminal.get("proposal_sha256"),
            terminal.get("proposal_artifact_sha256"),
        ) != (digest, digest, common.sha(a.payload)):
            raise ValueError("v3 proposal digest drift")
        if a.arm == "SMALL_BASIS_CEGAR" and not any(
            row.get("schema") == "oeis-a231201-v3-seed-closure-v1"
            and row.get("status") == "FULL_SEED_COVERED"
            and row.get("active_seed_rows") == len(full_seed)
            and row.get("attempts", 0) > 0
            for row in rows
        ):
            raise ValueError("v3 small-basis proposal lacks seed-closure receipt")
        basis_path = a.work / "basis-final.json"
        basis = json.loads(basis_path.read_text()).get("ordered_exponents")
        inc = v2_constructor.incidence(basis)
        score = v21_constructor.coverage_score(proposal, inc, len(basis))
        prefix = v2_constructor.least_prime_prefix(proposal, inc, len(basis))
        if (
            proposal_doc.get("basis_rows"),
            proposal_doc.get("basis_sha256"),
            proposal_doc.get("active_seed_rows"),
            proposal_doc.get("proposal_rank"),
        ) != (
            len(basis),
            common.sha(basis_path),
            len(full_seed),
            {
                "uncovered_rows": score[0],
                "least_prime_prefix": prefix,
                "assignment": list(score[2]),
            },
        ):
            raise ValueError("v3 proposal rank/basis drift")

    if a.arm != "SMALL_BASIS_CEGAR":
        return

    initial_doc = json.loads(initial_path.read_text())
    initial = initial_doc.get("ordered_exponents")
    expected_rows = 192 + 64 * a.round
    permutation = common.active_rows(a.cell, common.low_discrepancy_seed())
    if initial != permutation[:expected_rows]:
        raise ValueError("v3 nonredundant 192/256/320 basis schedule drift")

    current = list(initial)
    delta_attempts = set()
    for path in sorted(a.work.glob("basis-cegar-delta-*.json")):
        doc = json.loads(path.read_text())
        if doc.get("schema") != "oeis-a231201-v3-least-escape-feedback-v1":
            raise ValueError("v3 CEGAR delta schema drift")
        attempt = doc.get("attempt")
        if not isinstance(attempt, int) or attempt < 0 or attempt in delta_attempts:
            raise ValueError("v3 CEGAR attempt drift")
        delta_attempts.add(attempt)
        proposal = _assignment(doc.get("proposal", {}), a.cell)
        if doc.get("proposal_sha256") != common.assignment_hash(proposal):
            raise ValueError("v3 CEGAR proposal digest drift")
        if not _covers(proposal, current):
            raise ValueError("v3 CEGAR proposal did not cover its master basis")
        escape = _least_uncovered(proposal, full_seed)
        if (
            doc.get("previous_rows"),
            doc.get("ordered_basis_rows"),
            doc.get("least_uncovered_x"),
        ) != (len(current), len(current) + 1, escape):
            raise ValueError("v3 least-escape feedback drift")
        if escape is None or escape in current:
            raise ValueError("v3 CEGAR feedback made no progress")
        digest = common.sha(path)
        matching = [
            row
            for row in rows
            if row.get("schema") == "oeis-a231201-v3-least-escape-feedback-v1"
            and row.get("attempt") == attempt
        ]
        if len(matching) != 1 or (
            matching[0].get("previous_rows"),
            matching[0].get("basis_rows"),
            matching[0].get("least_uncovered_x"),
            matching[0].get("delta_sha256"),
            matching[0].get("proposal_sha256"),
            matching[0].get("status"),
        ) != (
            len(current),
            len(current) + 1,
            escape,
            digest,
            doc["proposal_sha256"],
            "LEAST_ESCAPE_ADDED",
        ):
            raise ValueError("v3 CEGAR delta/ledger binding drift")
        current.append(escape)

    final = json.loads(final_path.read_text()).get(
        "ordered_exponents"
    )
    if final != current:
        raise ValueError("v3 final basis/CEGAR chain drift")
    feasible_attempts = {
        row.get("attempt")
        for row in rows
        if row.get("schema") == "oeis-a231201-v3-cp-slice-v1"
        and row.get("status") in {"FEASIBLE", "OPTIMAL"}
    }
    closure_attempts = set()
    for row in rows:
        if row.get("schema") == "oeis-a231201-v3-seed-closure-v1":
            attempts = row.get("attempts")
            if isinstance(attempts, int) and attempts > 0:
                closure_attempts.add(attempts - 1)
    if feasible_attempts != delta_attempts | closure_attempts:
        raise ValueError("v3 feasible-solve/least-escape accounting drift")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("ledger", type=pathlib.Path)
    p.add_argument("terminal", type=pathlib.Path)
    p.add_argument("payload", type=pathlib.Path)
    p.add_argument("work", type=pathlib.Path)
    p.add_argument("--gate", type=pathlib.Path, required=True)
    p.add_argument("--campaign-commit", required=True)
    p.add_argument("--arm", choices=inherited.M["arms"], required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--round", type=int, choices=[0, 1, 2], required=True)
    a = p.parse_args()
    terminal = json.loads(a.terminal.read_text())
    inherited.common(a, terminal)
    verify_v3(a, terminal)
    print('{"verified":true,"operational_version":"v3-constructor-only"}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
