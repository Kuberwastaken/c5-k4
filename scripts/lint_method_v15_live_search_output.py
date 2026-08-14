#!/usr/bin/env python3
"""Lint one per-tree Method v1.5 live-search scientific JSONL stream."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent


def _load_runtime() -> Any:
    path = HERE / "method_v15_live_search_runtime.py"
    spec = importlib.util.spec_from_file_location("c5k4_v15_live_runtime_for_lint", path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError("cannot load live-search runtime")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUNTIME = _load_runtime()


@dataclass(frozen=True)
class Finding:
    code: str
    line: int
    message: str

    def as_dict(self) -> dict[str, object]:
        return {"code": self.code, "line": self.line, "message": self.message}


def _finding(code: str, line: int, message: str) -> Finding:
    return Finding(code, line, message)


def lint_jsonl(
    path: Path,
    *,
    allow_timeout_prefix: bool = False,
    labelg: Path | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    canonicalizer = None
    if labelg is None:
        findings.append(_finding("LABELG_REQUIRED", 0, "exact canonical identities require the frozen labelg"))
    else:
        try:
            canonicalizer = RUNTIME.LabelgCanonicalizer(labelg)
        except RUNTIME.LiveSearchRuntimeError as exc:
            findings.append(_finding("LABELG_INVALID", 0, str(exc)))
    try:
        raw_lines = path.read_bytes().splitlines(keepends=True)
    except OSError as exc:
        return [_finding("OUTPUT_MISSING", 0, str(exc))]
    if not raw_lines:
        return [_finding("OUTPUT_EMPTY", 0, "no durable scientific row exists")]

    previous = RUNTIME.ZERO_SHA256
    prior_counters = {field: 0 for field in RUNTIME.COUNTER_FIELDS}
    prior_elapsed = -1
    prior_cpu = -1
    identity: tuple[str, str] | None = None
    seen_canonical: set[str] = set()
    rows: list[dict[str, Any]] = []
    for line_number, raw in enumerate(raw_lines, 1):
        if not raw.endswith(b"\n"):
            findings.append(_finding("TRUNCATED_ROW", line_number, "final row lacks newline"))
            continue
        try:
            row = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            findings.append(_finding("INVALID_JSON", line_number, str(exc)))
            continue
        if not isinstance(row, dict):
            findings.append(_finding("ROW_TYPE", line_number, "row is not an object"))
            continue
        rows.append(row)
        if raw != RUNTIME.canonical_bytes(row):
            findings.append(_finding("NONCANONICAL_JSON", line_number, "row bytes are not canonical JSON"))
        required = {
            "schema", "kind", "arm", "tree_id", "sequence",
            "elapsed_milliseconds", "cpu_milliseconds", "counters",
            "previous_row_sha256", "row_sha256",
        }
        if not required <= set(row):
            findings.append(_finding("MISSING_FIELDS", line_number, "common row fields are incomplete"))
            continue
        if row["schema"] != RUNTIME.SCHEMA or row["arm"] not in RUNTIME.ARMS:
            findings.append(_finding("CONTRACT_IDENTITY", line_number, "schema or arm is invalid"))
        current_identity = (row["arm"], row["tree_id"])
        if identity is None:
            identity = current_identity
        elif current_identity != identity:
            findings.append(_finding("TREE_MIX", line_number, "multiple tree identities share one stream"))
        if row["tree_id"] not in {f'{row["arm"]}-{index}' for index in range(8)}:
            findings.append(_finding("TREE_ID", line_number, "tree id does not begin with its arm"))
        if type(row["sequence"]) is not int or row["sequence"] != line_number - 1:
            findings.append(_finding("SEQUENCE", line_number, "sequence is not contiguous from zero"))
        unsigned = {key: value for key, value in row.items() if key != "row_sha256"}
        calculated = hashlib.sha256(RUNTIME.canonical_bytes(unsigned)).hexdigest()
        if row["previous_row_sha256"] != previous:
            findings.append(_finding("CHAIN", line_number, "previous-row digest mismatch"))
        if row["row_sha256"] != calculated:
            findings.append(_finding("ROW_DIGEST", line_number, "row self-digest mismatch"))
        previous = row["row_sha256"] if isinstance(row["row_sha256"], str) else ""

        counters = row["counters"]
        if not isinstance(counters, dict) or set(counters) != set(RUNTIME.COUNTER_FIELDS):
            findings.append(_finding("COUNTER_FIELDS", line_number, "five-counter schema is not exact"))
            continue
        if any(type(counters[field]) is not int or counters[field] < 0 for field in RUNTIME.COUNTER_FIELDS):
            findings.append(_finding("COUNTER_TYPES", line_number, "counters must be nonnegative integers"))
            continue
        values = [counters[field] for field in RUNTIME.COUNTER_FIELDS]
        if values != sorted(values, reverse=True):
            findings.append(_finding("COUNTER_ORDER", line_number, "useful-work counters violate stage containment"))
        if any(counters[field] < prior_counters[field] for field in RUNTIME.COUNTER_FIELDS):
            findings.append(_finding("COUNTER_REGRESSION", line_number, "useful-work counters regressed"))
        if row["kind"] == "evaluated_candidate":
            candidate_fields = {"canonical_graph6", "canonical_sha256", "objective", "crossing", "payload"}
            if not candidate_fields <= set(row):
                findings.append(_finding("CANDIDATE_FIELDS", line_number, "evaluated candidate is incomplete"))
            elif counters["exact_evaluated"] != prior_counters["exact_evaluated"] + 1:
                findings.append(_finding("EXACT_COUNT", line_number, "candidate row must advance exact_evaluated once"))
            else:
                if row["objective"] is not None and (
                    isinstance(row["objective"], bool) or not isinstance(row["objective"], (int, str))
                ):
                    findings.append(_finding("OBJECTIVE_TYPE", line_number, "objective is not exact"))
                if row["objective"] is not None and type(row["crossing"]) is not bool:
                    findings.append(_finding("CROSSING_TYPE", line_number, "scored candidate lacks boolean crossing"))
                if not isinstance(row["payload"], dict):
                    findings.append(_finding("PAYLOAD_TYPE", line_number, "candidate payload is not an object"))
                try:
                    graph6 = str(row["canonical_graph6"])
                    encoded = graph6.encode("ascii", "strict")
                    graph = RUNTIME.nx.from_graph6_bytes(encoded)
                    digest = hashlib.sha256(
                        b"c5k4-exact-canonical-graph6-v1\0" + encoded
                    ).hexdigest()
                except Exception as exc:
                    findings.append(_finding("CANONICAL_GRAPH6", line_number, f"invalid graph6: {exc}"))
                    digest = ""
                if row["canonical_sha256"] != digest:
                    findings.append(_finding("CANONICAL_DIGEST", line_number, "canonical graph digest mismatch"))
                if canonicalizer is not None and digest:
                    try:
                        independently = canonicalizer.canonicalize(graph)
                    except RUNTIME.LiveSearchRuntimeError as exc:
                        findings.append(_finding("CANONICAL_REPLAY", line_number, str(exc)))
                    else:
                        if independently.graph6 != graph6 or independently.sha256 != row["canonical_sha256"]:
                            findings.append(_finding(
                                "NONCANONICAL_GRAPH", line_number,
                                "graph6 is valid but is not the exact labelg canonical representative",
                            ))
                if digest in seen_canonical:
                    findings.append(_finding("DUPLICATE_CANONICAL", line_number, "canonical graph was evaluated twice"))
                seen_canonical.add(digest)
                scored_delta = counters["objective_scored"] - prior_counters["objective_scored"]
                if (row["objective"] is None and scored_delta != 0) or (row["objective"] is not None and scored_delta != 1):
                    findings.append(_finding("SCORED_COUNT", line_number, "objective_scored does not match the candidate"))
        elif row["kind"] == "checkpoint":
            if not isinstance(row.get("label"), str) or not row["label"]:
                findings.append(_finding("CHECKPOINT_LABEL", line_number, "checkpoint label is empty"))
        elif row["kind"] == "summary":
            if row.get("status") != "COMPLETED":
                findings.append(_finding("SUMMARY_STATUS", line_number, "summary status is invalid"))
            if line_number != len(raw_lines):
                findings.append(_finding("NONTERMINAL_SUMMARY", line_number, "summary is not the final row"))
        else:
            findings.append(_finding("ROW_KIND", line_number, "unknown scientific row kind"))
        prior_counters = dict(counters)

        elapsed, cpu = row["elapsed_milliseconds"], row["cpu_milliseconds"]
        if type(elapsed) is not int or type(cpu) is not int or elapsed < prior_elapsed or cpu < prior_cpu:
            findings.append(_finding("CLOCKS", line_number, "elapsed/CPU clocks are invalid or regressed"))
        if type(elapsed) is int and elapsed > RUNTIME.WALL_CAP_SECONDS * 1000:
            findings.append(_finding("WALL_CAP", line_number, "row was emitted after the 60 second cap"))
        prior_elapsed, prior_cpu = elapsed, cpu

    if not rows:
        findings.append(_finding("NO_VALID_ROWS", 0, "no parseable scientific rows exist"))
    elif rows[0].get("kind") != "checkpoint" or rows[0].get("label") != "started":
        findings.append(_finding("START_ROW", 1, "stream does not begin with the durable started checkpoint"))
    if not allow_timeout_prefix:
        if rows[-1].get("kind") != "summary" or rows[-1].get("status") != "COMPLETED":
            findings.append(_finding("TERMINAL_SUMMARY", len(raw_lines), "successful output lacks a completed summary"))
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--labelg", type=Path, required=True)
    parser.add_argument("--allow-timeout-prefix", action="store_true")
    args = parser.parse_args(argv)
    findings = lint_jsonl(
        args.jsonl, allow_timeout_prefix=args.allow_timeout_prefix, labelg=args.labelg
    )
    for finding in findings:
        print(json.dumps(finding.as_dict(), sort_keys=True))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
