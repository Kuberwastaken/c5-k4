#!/usr/bin/env python3
"""Synthetic v2.2 deadline tests; no frozen target assignment is evaluated."""
from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
import unittest

from adversary_oeis_a231201_v22 import (
    FINALIZATION_RESERVE_SECONDS,
    SEARCH_SECONDS,
    STREAM_SCHEME,
    QueueStreamDigest,
    refine,
)
from oeis_a231201_v2_common import Ledger, sha
from verify_oeis_a231201_v22_artifacts import verify_deadline_evidence


class StepClock:
    def __init__(self, live_calls: int) -> None:
        self.live_calls = live_calls
        self.calls = 0

    def __call__(self) -> float:
        self.calls += 1
        return 0.0 if self.calls <= self.live_calls else 2.0


class V22DeadlineTests(unittest.TestCase):
    def test_stream_digest_matches_historical_queue_encoding(self) -> None:
        states = [(7, 30), (0, 1), (12345678901234567890, 99991)]
        stream = QueueStreamDigest()
        expected = hashlib.sha256()
        for state in states:
            stream.append(state)
            expected.update(f"{state[0]},{state[1]}\n".encode("ascii"))
        self.assertEqual(stream.count, len(states))
        self.assertEqual(stream.hexdigest(), expected.hexdigest())
        historical_completed = hashlib.sha256()
        for state in sorted(states):
            historical_completed.update(f"{state[0]},{state[1]}\n".encode("ascii"))
        self.assertNotEqual(stream.hexdigest(), historical_completed.hexdigest())

    def test_large_synthetic_frontier_finalizes_and_verifies(self) -> None:
        # This is a synthetic one-level split.  It does not call order_table,
        # periodic_value, the source gate, or any frozen target assignment.
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            ledger_path = root / "ledger.jsonl"
            ledger = Ledger(ledger_path)
            clock = StepClock(live_calls=200_000)
            result = refine(
                {997: 0},
                1.0,
                ledger,
                table=[(997, 1, 1_000_003)],
                value_at=lambda _q, _x: 1,
                clock=clock,
            )
            ledger.close()
            self.assertEqual(result["status"], "ADVERSARY_DEADLINE")
            self.assertGreaterEqual(result["partial_states"], 199_000)
            self.assertEqual(result["partial_queue_hash_scheme"], STREAM_SCHEME)
            terminal = {
                "status": "ADVERSARY_DEADLINE",
                "result": result,
                "operational_version": "v2.2",
                "search_seconds": SEARCH_SECONDS,
                "finalization_reserve_seconds": FINALIZATION_RESERVE_SECONDS,
                "exit_status": 75,
                "ledger_rows": ledger.seq,
                "final_row_sha256": ledger.previous,
                "ledger_sha256": sha(ledger_path),
            }
            terminal_path = root / "terminal.json"
            terminal_path.write_text(json.dumps(terminal, sort_keys=True) + "\n")
            verify_deadline_evidence(ledger_path, json.loads(terminal_path.read_text()))


if __name__ == "__main__":
    unittest.main()
