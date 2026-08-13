#!/usr/bin/env python3
"""Black-box checks for prospective_catchup_exact.cpp JSONL output."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


CONTROLS = (3, 4, 7, 8, 11, 12, 15, 16, 19, 20)
CONTRACT = "ab99508a9f5b924088897dbaf967c8f7125ae2380c5e061e7e9721c76a999403"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("solver", type=Path)
    args = parser.parse_args()
    process = subprocess.run(
        [str(args.solver.resolve()), "--calibrate"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    if process.returncode != 0:
        sys.stderr.write(process.stderr)
        return process.returncode
    rows = [json.loads(line) for line in process.stdout.splitlines()]
    starts = [row for row in rows if row["event"] == "run_start"]
    results = [row for row in rows if row["event"] == "result"]
    assert [row["n"] for row in starts] == list(CONTROLS)
    assert [row["n"] for row in results] == list(CONTROLS)
    assert all(row["contract_sha256"] == CONTRACT for row in starts)
    assert all(row["move_order"] == "ascending" for row in starts)
    assert all(row["value"] == 0 for row in results)
    assert all(row["matches_expected"] is True for row in results)
    assert all(0 <= row["memo_load"] <= 0.7 for row in results)
    print(json.dumps({"status": "PASS", "controls": list(CONTROLS)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
