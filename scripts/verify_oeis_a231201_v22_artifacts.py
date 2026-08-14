#!/usr/bin/env python3
"""Inherited v2 artifact checks plus v2.2 deadline-evidence checks."""
from __future__ import annotations

import argparse
import json
import pathlib
import verify_oeis_a231201_v2_artifacts as inherited
from adversary_oeis_a231201_v22 import (
    FINALIZATION_RESERVE_SECONDS,
    SEARCH_SECONDS,
    STREAM_SCHEME,
)


def _hex_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )


def verify_deadline_evidence(ledger_path: pathlib.Path, terminal: dict) -> None:
    """Verify a v2.2 deadline receipt without replaying its large frontier."""

    count, last = inherited.chain(ledger_path)
    if (
        terminal.get("ledger_rows"),
        terminal.get("final_row_sha256"),
        terminal.get("ledger_sha256"),
    ) != (count, last, inherited.sha(ledger_path)):
        raise ValueError("v2.2 terminal/ledger binding drift")
    rows = [json.loads(line) for line in ledger_path.read_text().splitlines()]
    if not rows:
        raise ValueError("empty v2.2 deadline ledger")
    row = rows[-1]
    result = terminal.get("result") or {}
    if row.get("schema") != "oeis-a231201-v22-adversary-level-v1":
        raise ValueError("v2.2 deadline row schema drift")
    if terminal.get("operational_version") != "v2.2":
        raise ValueError("v2.2 terminal version drift")
    if terminal.get("status") != "ADVERSARY_DEADLINE":
        raise ValueError("v2.2 deadline terminal status drift")
    if row.get("status") != "ADVERSARY_DEADLINE" or result.get("status") != "ADVERSARY_DEADLINE":
        raise ValueError("v2.2 deadline result drift")
    keys = (
        "level",
        "q",
        "cursor",
        "input_states",
        "input_processed",
        "partial_states",
        "partial_queue_sha256",
        "partial_queue_hash_scheme",
    )
    if any(result.get(key) != row.get(key) for key in keys):
        raise ValueError("v2.2 deadline ledger/result drift")
    if not isinstance(result.get("partial_states"), int) or result["partial_states"] < 0:
        raise ValueError("v2.2 partial-state count drift")
    if not _hex_digest(result.get("partial_queue_sha256")):
        raise ValueError("v2.2 partial digest drift")
    if result.get("partial_queue_hash_scheme") != STREAM_SCHEME:
        raise ValueError("v2.2 partial digest scheme drift")
    cursor = result.get("cursor")
    if not isinstance(cursor, dict) or any(
        not isinstance(cursor.get(key), int)
        for key in (
            "input_index",
            "input_residue",
            "input_modulus",
            "split_index",
            "split_value",
        )
    ):
        raise ValueError("v2.2 cursor drift")
    if (
        terminal.get("search_seconds"),
        terminal.get("finalization_reserve_seconds"),
        terminal.get("exit_status"),
    ) != (SEARCH_SECONDS, FINALIZATION_RESERVE_SECONDS, 75):
        raise ValueError("v2.2 deadline budget/exit drift")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=["construction", "adversary", "final"])
    p.add_argument("ledger", type=pathlib.Path)
    p.add_argument("terminal", type=pathlib.Path)
    p.add_argument("payload", type=pathlib.Path)
    p.add_argument("work", type=pathlib.Path)
    p.add_argument("--gate", type=pathlib.Path, required=True)
    p.add_argument("--candidate", type=pathlib.Path, required=True)
    p.add_argument("--campaign-commit", required=True)
    p.add_argument("--arm", choices=inherited.M["arms"], required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--round", type=int, required=True)
    a = p.parse_args()
    doc = json.loads(a.terminal.read_text())
    inherited.common(a, doc)
    getattr(inherited, a.stage)(a, doc)
    if a.stage == "adversary":
        if (
            doc.get("operational_version"),
            doc.get("search_seconds"),
            doc.get("finalization_reserve_seconds"),
        ) != ("v2.2", SEARCH_SECONDS, FINALIZATION_RESERVE_SECONDS):
            raise ValueError("v2.2 adversary version/budget drift")
        if doc.get("status") == "ADVERSARY_DEADLINE":
            verify_deadline_evidence(a.ledger, doc)
    print('{"verified":true,"operational_version":"v2.2"}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
