#!/usr/bin/env python3
"""Synthetic v3 seed-CEGAR tests; no frozen target is evaluated."""
from __future__ import annotations

import time
import unittest
from unittest import mock

import construct_oeis_a231201_v3 as constructor


class V3SeedCegarTests(unittest.TestCase):
    def test_least_escape_is_added_before_emission(self) -> None:
        basis = [10]
        full_seed = [10, 11]
        first = {2: 0, 3: 0, 5: 0, 7: 3}
        second = {2: 0, 3: 0, 5: 0, 7: 1}
        calls = []
        feedback = []

        def fake_direct(q: int, x: int) -> int:
            if q in (2, 3):
                return 1
            if q == 5:
                return 0 if x == 10 else 1
            return 2 if x == 10 else 1

        def solve_once(current_basis, _hint, _deadline, attempt):
            calls.append((list(current_basis), attempt))
            return ("FEASIBLE", first if attempt == 0 else second)

        with mock.patch.object(constructor.v21.v2, "direct_value", fake_direct), mock.patch.object(
            constructor.v21.v2, "M", {"primes": [2, 3, 5, 7]}
        ):
            status, emitted, attempts = constructor.least_escape_cegar(
                basis,
                full_seed,
                first,
                time.monotonic() + 1.0,
                solve_once,
                lambda x, old, attempt, proposal: feedback.append(
                    (x, old, attempt, proposal)
                ),
                max_iterations=4,
            )
        self.assertEqual((status, emitted, attempts), ("FEASIBLE", second, 2))
        self.assertEqual(feedback, [(11, 1, 0, first)])
        self.assertEqual(calls, [([10], 0), ([10, 11], 1)])

    def test_no_proposal_is_emitted_while_any_seed_escape_remains(self) -> None:
        basis = [1]
        full_seed = [1, 2, 3]
        proposal = {2: 0, 3: 0, 5: 0}
        feedback = []

        def fake_direct(q: int, x: int) -> int:
            if q in (2, 3):
                return 1
            return 0 if x == 1 else x

        with mock.patch.object(constructor.v21.v2, "direct_value", fake_direct), mock.patch.object(
            constructor.v21.v2, "M", {"primes": [2, 3, 5]}
        ):
            status, emitted, attempts = constructor.least_escape_cegar(
                basis,
                full_seed,
                proposal,
                time.monotonic() + 1.0,
                lambda *_args: ("FEASIBLE", proposal),
                lambda x, old, attempt, candidate: feedback.append(
                    (x, old, attempt, candidate)
                ),
                max_iterations=1,
            )
        self.assertEqual((status, emitted, attempts), ("FEASIBLE", None, 1))
        self.assertEqual(feedback, [(2, 1, 0, proposal)])
        self.assertEqual(basis, [1, 2])

    def test_frozen_runtime_schedule_and_caps(self) -> None:
        self.assertEqual(
            (
                constructor.v21.v2.M["small_basis"]["initial_rows"],
                constructor.v21.v2.M["small_basis"]["growth_rows"],
                constructor.v21.v2.M["small_basis"]["growth_every_rounds"],
            ),
            (192, 64, 3),
        )
        self.assertEqual(
            (
                constructor.v21.v2.M["internal_seconds"],
                constructor.v21.v2.M["finalization_reserve_seconds"],
                constructor.v21.v2.M["external_seconds"],
            ),
            (54, 6, 60),
        )


if __name__ == "__main__":
    unittest.main()
