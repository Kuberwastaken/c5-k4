#!/usr/bin/env python3
"""Cross-check DeepMind Erdős declarations against the canonical status data.

This is a Phase-0 selector, not a mathematical status oracle.  It deliberately
separates three notions that are easy to conflate:

* ``formalized: yes``: an Erdős problem statement has a formalization;
* ``formal_status: Lean``: a solution has been checked in Lean;
* ``@[category research open]``: DeepMind currently treats this declaration as
  mathematically open.

The script also records syntactic resolution-shape hazards.  A target is never
declared counterexample-eligible from syntax alone; ``REVIEW_FINITE_NEGATION``
means that a human still has to write the literal finite negation certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_STATUS_REVISION = "66dfe4860f73d94ecb1b09b99990a67272b6d16a"
DEFAULT_STATUS_URL = (
    "https://raw.githubusercontent.com/teorth/erdosproblems/"
    f"{DEFAULT_STATUS_REVISION}/data/problems.yaml"
)

OPEN_TAG = re.compile(r"@\[category\s+research\s+open[^]]*\]")
THEOREM = re.compile(r"\b(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)")


@dataclass(frozen=True)
class Declaration:
    problem: str
    path: str
    line: int
    name: str
    statement_sha256: str
    informal_status: str
    formal_solution_status: str
    statement_formalized: str
    answer_placeholder: bool
    eventual_or_limit: bool
    global_constant: bool
    existential_head: bool
    infinite_object: bool
    source_certificate_class: str
    resolution_lane: str


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True
    ).strip()


def load_status(
    path: Path | None, url: str
) -> tuple[list[dict[str, Any]], str, str]:
    if path is not None:
        raw = path.read_bytes()
        source = str(path.resolve())
    else:
        with urllib.request.urlopen(url, timeout=30) as response:
            raw = response.read()
        source = url
    data = yaml.safe_load(raw)
    if not isinstance(data, list):
        raise ValueError("Erdős status data must be a YAML list")
    return data, hashlib.sha256(raw).hexdigest(), source


def declaration_block(text: str, start: int) -> str:
    next_tag = text.find("@[category", start + 1)
    namespace_end = text.find("\nend ", start + 1)
    stops = [x for x in (next_tag, namespace_end) if x != -1]
    end = min(stops) if stops else len(text)
    return text[start:end]


def classify_source(status: str) -> tuple[str, str]:
    if status == "falsifiable":
        return "FINITE_COUNTEREXAMPLE_IF_FALSE", "REVIEW_FINITE_NEGATION"
    if status == "decidable":
        return "FINITE_BOTH_DIRECTIONS", "REVIEW_FINITE_NEGATION"
    if status == "verifiable":
        return "FINITE_CONSTRUCTION_IF_TRUE", "CONSTRUCTION_OR_PROOF"
    if status in {"proved", "disproved", "solved"}:
        return "RESOLVED", "STATUS_OR_PROOF_SYNC"
    return "NOT_KNOWN_FINITE", "PROOF_OR_FAMILY_ONLY"


def scan(repo: Path, statuses: dict[str, dict[str, Any]]) -> list[Declaration]:
    root = repo / "FormalConjectures" / "ErdosProblems"
    rows: list[Declaration] = []
    for path in sorted(root.glob("*.lean"), key=lambda p: int(p.stem)):
        entry = statuses.get(path.stem, {})
        informal = entry.get("informal_status", {}).get("state", "missing")
        formal = entry.get("formal_status", {}).get("state", "missing")
        formalized = entry.get("formalized", {}).get("state", "missing")
        certificate_class, default_lane = classify_source(informal)
        text = path.read_text(encoding="utf-8")
        for match in OPEN_TAG.finditer(text):
            block = declaration_block(text, match.start())
            theorem = THEOREM.search(block)
            if theorem is None:
                continue
            line = text.count("\n", 0, match.start()) + 1
            compact = " ".join(block.split())
            eventual = any(
                token in block
                for token in ("∀ᶠ", "atTop", "IsBigO", "IsLittleO", "Tendsto")
            )
            global_constant = bool(
                re.search(r"∃\s*\(?[A-Za-zα-ωΑ-Ωδ]+\s*:\s*ℝ", block)
                and ("∀ᶠ" in block or "∀ (n" in block or "∀ n" in block)
            )
            existential_head = bool(re.search(r"[:↔]\s*∃", compact))
            infinite_object = any(
                token in block
                for token in ("Set.Infinite", ".Infinite", "Cardinal", "Infinite ")
            )
            lane = default_lane
            if formal == "Lean" or informal in {"proved", "disproved", "solved"}:
                lane = "STATUS_OR_PROOF_SYNC"
            elif eventual or global_constant or infinite_object:
                lane = "PROOF_OR_EXPLICIT_INFINITE_FAMILY"
            elif existential_head and informal not in {"falsifiable", "decidable"}:
                lane = "CONSTRUCTION_OR_GLOBAL_NONEXISTENCE_PROOF"
            rows.append(
                Declaration(
                    problem=path.stem,
                    path=str(path.relative_to(repo)),
                    line=line,
                    name=theorem.group(1),
                    statement_sha256=hashlib.sha256(block.encode()).hexdigest(),
                    informal_status=informal,
                    formal_solution_status=formal,
                    statement_formalized=formalized,
                    answer_placeholder="answer(sorry)" in compact,
                    eventual_or_limit=eventual,
                    global_constant=global_constant,
                    existential_head=existential_head,
                    infinite_object=infinite_object,
                    source_certificate_class=certificate_class,
                    resolution_lane=lane,
                )
            )
    return rows


def markdown(
    rows: list[Declaration], upstream_sha: str, status_sha: str, status_source: str
) -> str:
    lanes = Counter(row.resolution_lane for row in rows)
    source_states = Counter(row.informal_status for row in rows)
    lines = [
        "# Erdős / DeepMind resolution-shape audit",
        "",
        f"- DeepMind upstream SHA: `{upstream_sha}`",
        f"- Erdős status source: `{status_source}`",
        f"- Erdős YAML SHA-256: `{status_sha}`",
        f"- Open DeepMind Erdős declarations: **{len(rows)}**",
        "- This is a syntactic Phase-0 screen; `REVIEW_FINITE_NEGATION` is not",
        "  permission to search or a claim that a counterexample exists.",
        "",
        "## Source-status counts",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(source_states.items()))
    lines.extend(["", "## Resolution-lane counts", ""])
    lines.extend(f"- `{key}`: {value}" for key, value in sorted(lanes.items()))
    lines.extend(
        [
            "",
            "## Declarations",
            "",
            "| problem | declaration | source | formal solution | lane | hazards |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for row in rows:
        hazards = []
        if row.answer_placeholder:
            hazards.append("answer")
        if row.eventual_or_limit:
            hazards.append("eventual/limit")
        if row.global_constant:
            hazards.append("global constant")
        if row.existential_head:
            hazards.append("existential")
        if row.infinite_object:
            hazards.append("infinite")
        lines.append(
            f"| {row.problem} | `{row.name}` | `{row.informal_status}` | "
            f"`{row.formal_solution_status}` | `{row.resolution_lane}` | "
            f"{', '.join(hazards) or 'none detected'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-repo", type=Path, required=True)
    parser.add_argument("--erdos-yaml", type=Path)
    parser.add_argument("--status-url", default=DEFAULT_STATUS_URL)
    parser.add_argument("--jsonl", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    repo = args.formal_repo.resolve()
    data, status_sha, status_source = load_status(args.erdos_yaml, args.status_url)
    statuses = {str(entry["number"]): entry for entry in data}
    rows = scan(repo, statuses)
    upstream_sha = git(repo, "rev-parse", "HEAD")

    if args.jsonl:
        args.jsonl.parent.mkdir(parents=True, exist_ok=True)
        args.jsonl.write_text(
            "".join(json.dumps(asdict(row), sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )
    report = markdown(rows, upstream_sha, status_sha, status_source)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
