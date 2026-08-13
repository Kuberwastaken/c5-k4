#!/usr/bin/env python3
"""Independent ledger audit for the completed Method v0.4 metric trial."""

from collections import Counter
from fractions import Fraction
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results/expansion/method_v04_metric_trial.jsonl"


def main() -> None:
    rows = [json.loads(line) for line in LEDGER.read_text().splitlines()]
    gate = [row for row in rows if row.get("stage") == "gate"]
    grid = [row for row in rows if row.get("stage") == "grid"]
    keys = Counter((row["comet_m"], row["comet_length"]) for row in grid)

    assert len(gate) == 1057
    assert sum(row.get("stage") == "gate_shard_end" for row in rows) == 32
    assert not [row for row in gate if row.get("gate_failure")]
    assert not [row for row in gate if "timeout" in row]
    assert all(not row["crossing184"] and not row["crossing185"] for row in gate)

    expected = {(m, length) for m in range(2, 11) for length in range(1, 31)}
    assert set(keys) == expected
    assert all(count == 1 for count in keys.values())
    assert not [row for row in grid if "timeout" in row]

    for row in grid:
        d_boundary = Fraction(row["d_boundary"])
        d_all = Fraction(row["d_all"])
        r184 = Fraction(row["R184"])
        r185 = Fraction(row["R185"])
        assert r184 == row["T173"] + row["q"] + 2 - 2 * d_boundary
        assert r185 == row["T173"] + row["q"] + 2 - 2 * d_all
        assert row["T173"] >= 0
        assert (r184 < 0) == row["crossing184"]
        assert (r185 < 0) == row["crossing185"]

    minimum184 = min((Fraction(row["R184"]), row["name"]) for row in grid)
    minimum185 = min((Fraction(row["R185"]), row["name"]) for row in grid)
    assert minimum184 == (Fraction(69, 121), "K(2,2)")
    assert minimum185 == (Fraction(20, 33), "K(2,2)")
    assert all(Fraction(row["R184"]) > 0 and Fraction(row["R185"]) > 0 for row in grid)
    print("PASS gate: 1057 rows, 32 shards, no failures or timeouts")
    print("PASS grid: 270/270 unique keys, no duplicates or timeouts")
    print("PASS residual identities; min R184=69/121, min R185=20/33 at K(2,2)")


if __name__ == "__main__":
    main()
