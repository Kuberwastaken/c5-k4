#!/usr/bin/env python3
"""Independent GAP verifier for a solvable_of_cyc_lt candidate certificate."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence


CERTIFICATE_SCHEMA = "c5k4-solvable-cyclic-subgroups-certificate-1.0"
MARKER = "@@INDEPENDENT@@"


class SearchError(ValueError):
    pass


class GapQueryTimeout(TimeoutError):
    pass


def independent_gap_source(expression: str) -> str:
    if not expression or any(token in expression for token in (";", "\n", "\r")):
        raise SearchError("unsafe or empty frozen GAP expression")
    return f'''SetInfoLevel(InfoWarning,0);;
G0 := {expression};;
G := Image(IsomorphismPermGroup(G0));;
classes := ConjugacyClassesSubgroups(G);;
cyclicClasses := Filtered(classes, c -> IsCyclic(Representative(c)));;
cyc := Sum(cyclicClasses, Size);;
pf := Set(FactorsInt(Size(G)));;
Print("{MARKER}\\t", Size(G), "\\t", JoinStringsWithSeparator(List(pf,String),","),
  "\\t", IsSolvableGroup(G), "\\t", cyc, "\\t", Length(classes), "\\n");;
QUIT_GAP(0);;
'''


def _run(gap: str, source: str, timeout_seconds: float) -> str:
    if timeout_seconds <= 0:
        raise GapQueryTimeout("no independent-verification time remains")
    try:
        completed = subprocess.run(
            [gap, "-q", "-b"],
            input=source,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
            env={**os.environ, "LC_ALL": "C.UTF-8", "TZ": "UTC"},
        )
    except subprocess.TimeoutExpired as exc:
        raise GapQueryTimeout("independent subgroup-class replay timed out") from exc
    if completed.returncode != 0:
        raise SearchError(f"independent GAP exited {completed.returncode}: {completed.stderr[-1000:]}")
    return completed.stdout


def validate_candidate_shape(document: Mapping[str, Any]) -> Mapping[str, Any]:
    if document.get("schema") != CERTIFICATE_SCHEMA:
        raise SearchError("wrong certificate schema")
    primary = document.get("primary")
    if not isinstance(primary, Mapping):
        raise SearchError("primary certificate record is absent")
    required = {
        "gap_expression", "order", "prime_factors", "num_prime_factors",
        "cyclic_subgroups", "solvable", "threshold", "residual",
        "element_order_histogram", "permutation_generators",
    }
    if not required.issubset(primary):
        raise SearchError("primary certificate record is incomplete")
    if primary["solvable"] is not False or int(primary["residual"]) >= 0:
        raise SearchError("document is not a primary counterexample candidate")
    if int(primary["threshold"]) != 1 << (int(primary["num_prime_factors"]) + 2):
        raise SearchError("primary threshold arithmetic is inconsistent")
    if int(primary["residual"]) != int(primary["cyclic_subgroups"]) - int(primary["threshold"]):
        raise SearchError("primary residual arithmetic is inconsistent")
    return primary


def verify_candidate_document(document: Mapping[str, Any], gap: str, timeout_seconds: float) -> dict[str, Any]:
    primary = validate_candidate_shape(document)
    output = _run(gap, independent_gap_source(str(primary["gap_expression"])), timeout_seconds)
    rows = [line for line in output.splitlines() if line.startswith(MARKER)]
    if len(rows) != 1:
        raise SearchError("independent GAP marker missing or duplicated")
    fields = rows[0].split("\t")
    if len(fields) != 6 or fields[3] not in {"true", "false"}:
        raise SearchError("malformed independent GAP marker")
    replay = {
        "method": "GAP conjugacy classes of subgroups; sum conjugacy-class sizes for cyclic representatives",
        "order": int(fields[1]),
        "prime_factors": [int(value) for value in fields[2].split(",") if value],
        "solvable": fields[3] == "true",
        "cyclic_subgroups": int(fields[4]),
        "subgroup_conjugacy_classes": int(fields[5]),
    }
    if replay["order"] != primary["order"]:
        raise SearchError("independent order mismatch")
    if replay["prime_factors"] != primary["prime_factors"]:
        raise SearchError("independent prime-factor mismatch")
    if replay["solvable"] is not False:
        raise SearchError("independent replay says group is solvable")
    if replay["cyclic_subgroups"] != primary["cyclic_subgroups"]:
        raise SearchError("independent cyclic-subgroup count mismatch")
    replay["threshold"] = 1 << (len(replay["prime_factors"]) + 2)
    replay["residual"] = replay["cyclic_subgroups"] - replay["threshold"]
    if replay["residual"] >= 0:
        raise SearchError("independent replay does not cross the conjectured wall")
    replay["verified"] = True
    return replay


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--gap", default="gap")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.candidate.read_text(encoding="utf-8"))
        replay = verify_candidate_document(document, args.gap, args.timeout_seconds)
    except (OSError, ValueError, SearchError, GapQueryTimeout) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(replay, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
