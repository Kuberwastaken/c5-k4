#!/usr/bin/env python3
"""Audit and aggregate the 24 TxGraffiti C-C phase-four worker artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

import txgraffiti_cc_phase4_domain as domain
from lint_method_v15_live_search_output import lint_jsonl


AGGREGATE_SCHEMA = "c5k4-txgraffiti-cc-phase4-aggregate-1.0"


def classify(reasons: list[str], crossings: int, errors: list[str]) -> str:
    if errors:
        return "INVALID_RUN"
    if crossings:
        return "VERIFIED_CROSSING"
    if len(reasons) == domain.PARTITION_COUNT and set(reasons) == {"DOMAIN_EXHAUSTED"}:
        return "DOMAIN_EXHAUSTED_ZERO"
    return "BOUNDED_PREFIX_ZERO"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate(
    domain_root: Path,
    selection_root: Path,
    workers_root: Path,
    labelg: Path,
    output_json: Path,
    output_markdown: Path,
) -> dict[str, object]:
    domain_manifest = domain.verify_domain(domain_root)
    selection = domain.verify_selection(domain_root, selection_root)
    errors: list[str] = []
    reasons: list[str] = []
    evaluated_ids: set[str] = set()
    crossings: list[str] = []
    worker_rows: list[dict[str, object]] = []
    total_work_ids: set[str] = set()

    selection_by_partition = {int(row["partition"]): row for row in selection["partitions"]}
    for partition in range(domain.PARTITION_COUNT):
        work_record = selection_by_partition.get(partition)
        if work_record is None:
            errors.append(f"partition {partition}: selection entry missing")
            continue
        work_path = selection_root / str(work_record["path"])
        work_rows = list(domain.load_jsonl(work_path))
        work_ids = {str(row["canonical_sha256"]) for row in work_rows}
        total_work_ids.update(work_ids)
        root = workers_root / f"partition-{partition:02d}"
        ledger_path = root / "ledger.jsonl"
        terminal_path = root / "terminal.json"
        wrapper_path = root / "wrapper-report.json"
        if not all(path.is_file() for path in (ledger_path, terminal_path, wrapper_path)):
            errors.append(f"partition {partition}: worker artifact is incomplete")
            continue
        findings = lint_jsonl(ledger_path, labelg=labelg)
        if findings:
            errors.append(f"partition {partition}: ledger lint {findings[0].code}")
            continue
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
        wrapper = json.loads(wrapper_path.read_text(encoding="utf-8"))
        reason = str(terminal.get("terminal_reason", ""))
        if terminal.get("schema") != "c5k4-txgraffiti-cc-phase4-worker-terminal-1.0":
            errors.append(f"partition {partition}: terminal schema mismatch")
        if int(terminal.get("partition", -1)) != partition:
            errors.append(f"partition {partition}: terminal partition mismatch")
        if reason not in {
            "DOMAIN_EXHAUSTED", "DEADLINE_PREFIX", "SOLVER_INCOMPLETE", "CROSSING_VERIFIED"
        }:
            errors.append(f"partition {partition}: unknown terminal reason")
        if wrapper.get("timed_out") is not False or wrapper.get("scientific_output_valid") is not True:
            errors.append(f"partition {partition}: wrapper did not record a valid normal exit")
        ledger_rows = list(domain.load_jsonl(ledger_path))
        receipt_digest = _sha256(terminal_path)
        if not any(
            row.get("kind") == "checkpoint"
            and row.get("label") == f"phase4_terminal_receipt_sha256:{receipt_digest}"
            for row in ledger_rows
        ):
            errors.append(f"partition {partition}: terminal receipt is not ledger-bound")
        candidates = [row for row in ledger_rows if row.get("kind") == "evaluated_candidate"]
        candidate_ids = [str(row["canonical_sha256"]) for row in candidates]
        if len(candidate_ids) != len(set(candidate_ids)) or not set(candidate_ids) <= work_ids:
            errors.append(f"partition {partition}: evaluated identity is duplicate or outside worklist")
        if evaluated_ids.intersection(candidate_ids):
            errors.append(f"partition {partition}: identity was evaluated by multiple workers")
        evaluated_ids.update(candidate_ids)
        if int(terminal.get("identities_evaluated_this_run", -1)) != len(candidate_ids):
            errors.append(f"partition {partition}: terminal evaluated count mismatch")
        if int(terminal.get("worklist_identities", -1)) != len(work_ids):
            errors.append(f"partition {partition}: terminal worklist count mismatch")
        if reason == "DOMAIN_EXHAUSTED" and set(candidate_ids) != work_ids:
            errors.append(f"partition {partition}: claimed exhaustion without full identity coverage")
        local_crossings = [str(row["canonical_sha256"]) for row in candidates if row.get("crossing") is True]
        crossings.extend(local_crossings)
        if reason == "CROSSING_VERIFIED" and not local_crossings:
            errors.append(f"partition {partition}: crossing terminal lacks a crossing row")
        reasons.append(reason)
        worker_rows.append({
            "partition": partition,
            "terminal_reason": reason,
            "worklist_identities": len(work_ids),
            "evaluated_identities": len(candidate_ids),
            "crossings": len(local_crossings),
            "ledger_sha256": _sha256(ledger_path),
            "terminal_sha256": receipt_digest,
            "wrapper_sha256": _sha256(wrapper_path),
        })

    if len(total_work_ids) != int(selection["unscored_identity_count"]):
        errors.append("selection work partitions are not globally disjoint and complete")
    status = classify(reasons, len(crossings), errors)
    if status == "DOMAIN_EXHAUSTED_ZERO" and evaluated_ids != total_work_ids:
        errors.append("aggregate exhaustion lacks complete unscored identity coverage")
        status = "INVALID_RUN"
    aggregate_row = {
        "schema": AGGREGATE_SCHEMA,
        "status": status,
        "evidence_split": "DEVELOPMENT",
        "domain_manifest_sha256": domain.sha256_file(domain_root / "domain-manifest.json"),
        "selection_manifest_sha256": domain.sha256_file(selection_root / "selection-manifest.json"),
        "construction_states": int(domain_manifest["construction_states_scanned"]),
        "canonical_domain_identities": int(domain_manifest["canonical_identity_count"]),
        "prior_scored_identities": int(selection["scored_identity_count_in_domain"]),
        "unscored_identities": int(selection["unscored_identity_count"]),
        "newly_evaluated_identities": len(evaluated_ids),
        "crossing_identities": sorted(crossings),
        "worker_terminal_reasons": {reason: reasons.count(reason) for reason in sorted(set(reasons))},
        "workers": worker_rows,
        "errors": errors,
    }
    output_json.write_bytes(domain.canonical_json(aggregate_row))
    output_markdown.write_text(
        "# TxGraffiti C-C phase-four aggregate\n\n"
        f"- Status: **{status}**\n"
        f"- Construction states: **{aggregate_row['construction_states']}**\n"
        f"- Canonical identities: **{aggregate_row['canonical_domain_identities']}**\n"
        f"- Prior scored: **{aggregate_row['prior_scored_identities']}**\n"
        f"- Newly evaluated: **{aggregate_row['newly_evaluated_identities']}**\n"
        f"- Verified crossings: **{len(crossings)}**\n"
        f"- Audit errors: **{len(errors)}**\n",
        encoding="utf-8",
    )
    return aggregate_row


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--workers", type=Path, required=True)
    parser.add_argument("--labelg", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args(argv)
    result = aggregate(
        args.domain,
        args.selection,
        args.workers,
        args.labelg,
        args.output_json,
        args.output_markdown,
    )
    return 0 if result["status"] != "INVALID_RUN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
