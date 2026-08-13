#!/usr/bin/env python3
"""Independent subset verifier for closest frozen #133 cover/switch rows."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/prospective_wowii133_covers_switches_ledger.jsonl"
VERIFY_PATH = ROOT / "scripts/method_v02_133_verify.py"
SPEC = importlib.util.spec_from_file_location("wow133_verify", VERIFY_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def main() -> None:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    discovery = [row for row in rows if row.get("stratum") == "discovery" and row.get("kind") == "graph"]
    selected = []
    seen = set()
    for row in sorted(discovery, key=lambda item: (item["residual"], item["n"], item["name"])):
        if row["graph6"] in seen or row["n"] > 20:
            continue
        selected.append(row)
        seen.add(row["graph6"])
        if len(selected) == 12:
            break
    assert selected and selected[0]["residual"] == 0
    for row in selected:
        VERIFY.verify(row)
        print(f"PASS {row['name']} n={row['n']} path={row['path']} residual={row['residual']}")
    print(f"PASS independent descending-subset verifier: {len(selected)} rows")


if __name__ == "__main__":
    main()
