"""Constructor and mutation tests only; no A056777 target range is searched."""
from __future__ import annotations

import json
import itertools
import pathlib
import signal
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import prepare_oeis_a056777_gate as prep
import search_oeis_a056777 as search
import verify_oeis_a056777_candidate as independent


class FreezeTests(unittest.TestCase):
    def test_caps_boundary_and_arms(self):
        self.assertEqual((prep.M["internal_seconds"], prep.M["external_search_seconds"], prep.M["external_verify_seconds"]), (48, 54, 60))
        self.assertEqual((prep.M["historical_exclusion_upper_inclusive"], prep.M["value_minimum"]), (10**12, 10**12 + 1))
        self.assertEqual(set(prep.M["arms"]), {"REPEATED_POWER_SURGERY", "SQUAREFREE_THREE_BLOCK", "PURE_PRIME_POWER"})
        self.assertLess(prep.M["value_maximum"] + 12, 2**64)

    def test_factorizers_are_distinct_and_exact_on_fixtures(self):
        fixtures = {65: [(5, 1), (13, 1)], 72: [(2, 3), (3, 2)], 1001: [(7, 1), (11, 1), (13, 1)], 1000003: [(1000003, 1)]}
        for n, expected in fixtures.items():
            self.assertEqual(search.factor(n), expected)
            self.assertEqual(independent.refactor(n), expected)
        self.assertIsNot(search.factor, independent.refactor)

    def test_constructive_tuple_slices_are_canonical_and_independently_rebuilt(self):
        shapes = {
            "REPEATED_POWER_SURGERY": lambda f: len(f) == 2 and f[0][1] >= 2 and f[1][1] == 1,
            "SQUAREFREE_THREE_BLOCK": lambda f: len(f) == 3 and all(e == 1 for _, e in f),
            "PURE_PRIME_POWER": lambda f: len(f) == 1 and f[0][1] >= 3,
        }
        seen = set()
        for arm, predicate in shapes.items():
            generated = list(itertools.islice(search.arm_states(arm, 0), 3))
            rebuilt = list(itertools.islice(independent.independent_states(arm, 0), 3))
            self.assertEqual(generated, rebuilt)
            self.assertEqual(len(generated), 3)
            for coordinate, n, factors in generated:
                self.assertTrue(predicate(factors)); self.assertEqual(n, __import__('math').prod(p**e for p, e in factors))
                self.assertNotIn(n, seen); seen.add(n)
                if arm != "PURE_PRIME_POWER": self.assertEqual(coordinate["p_rank"], 1)

    def test_method_wall_algebra(self):
        # x(gap-x)=12 has only these positive factor-pair solutions.
        solutions = [(x, gap) for x in range(1, 13) for gap in range(x + 1, 20) if x * (gap - x) == 12]
        self.assertEqual(solutions, [(1, 13), (2, 8), (3, 7), (4, 7), (6, 8), (12, 13)])
        # Odd-prime pairs have even gap; ordered c=a+x <= d=b-x leaves x=2.
        self.assertEqual([(x, gap) for x, gap in solutions if gap % 2 == 0 and 2*x <= gap], [(2, 8)])

    def test_arithmetic_fixture_and_quadruple_witness_parser(self):
        self.assertEqual(search.arithmetic([(2, 3), (3, 2)]), (24, 195))
        self.assertEqual(search.prime_quadruple_witness(65), 5)
        self.assertIsNone(search.prime_quadruple_witness(66))

    def test_k_wall_symbolic_controls(self):
        def kval(n, factors):
            phi, sigma = search.arithmetic(factors); return sigma + phi - 2*n
        self.assertEqual(kval(35, [(5, 1), (7, 1)]), 2)
        self.assertEqual(kval(49, [(7, 2)]), 1)
        self.assertEqual([(a, b) for a in range(1, 13) for b in range(a, 13) if a*b == 12 and b-a > 0], [(1, 12), (2, 6), (3, 4)])
        wall = json.loads((prep.HERE / "method-wall-certificate.json").read_text())
        self.assertEqual(wall["squarefree_semiprime_wall"]["ordered_survivor_shift"], 2)
        self.assertEqual(wall["prime_square_prune"]["prime_solutions"], [])

    def test_ledger_chain_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "ledger.jsonl"; ledger = search.Ledger(path)
            ledger.append({"schema": "oeis-a056777-progress-v1", "campaign_commit": "1" * 40, "arm": "REPEATED_POWER_SURGERY", "shard": 0, "visited": 0}); ledger.close()
            rows, digest = independent.chain(path, "1" * 40, "REPEATED_POWER_SURGERY", 0)
            self.assertEqual((len(rows), digest), (1, rows[0]["row_sha256"]))
            path.write_text(path.read_text().replace('"visited":0', '"visited":1'))
            with self.assertRaisesRegex(ValueError, "hash-chain"):
                independent.chain(path, "1" * 40, "REPEATED_POWER_SURGERY", 0)

    def test_sigalrm_is_deferred_until_atomic_commit_finishes(self):
        previous = signal.getsignal(signal.SIGALRM); state = []
        signal.signal(signal.SIGALRM, search.alarm_handler)
        try:
            with self.assertRaises(search.Deadline):
                with search.block_alarm():
                    state.append("fully-committed")
                    signal.raise_signal(signal.SIGALRM)
            self.assertEqual(state, ["fully-committed"])
        finally:
            signal.signal(signal.SIGALRM, previous)

    def test_worker_exception_gets_truthful_terminal_receipt(self):
        def broken_states(_arm, _shard):
            raise RuntimeError("synthetic worker failure")
            yield
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory); gate = root / "gate"; gate.mkdir()
            (gate / "gate-attestation.json").write_text("{}\n")
            args = SimpleNamespace(arm="REPEATED_POWER_SURGERY", shard=0, campaign_commit="1"*40,
                                   gate_bundle=gate, ledger=root/"ledger.jsonl", terminal=root/"terminal.json",
                                   certificate=root/"certificate.json")
            with mock.patch.object(search, "verify"), mock.patch.object(search, "arm_states", broken_states):
                self.assertEqual(search.run(args), 21)
            terminal = json.loads(args.terminal.read_text())
            self.assertEqual((terminal["terminal_reason"], terminal["visited"], terminal["certificate_present"]), ("WORKER_ERROR", 0, False))
            independent.validate_worker_error("WORKER_ERROR", terminal["worker_error"])
            corrupted = dict(terminal["worker_error"]); corrupted["message_sha256"] = "0"*64
            with self.assertRaisesRegex(ValueError, "digest"):
                independent.validate_worker_error("WORKER_ERROR", corrupted)

    def test_certificate_write_failure_leaves_prior_prefix_authoritative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory); gate = root / "gate"; gate.mkdir()
            (gate / "gate-attestation.json").write_text("{}\n")
            args = SimpleNamespace(arm="PURE_PRIME_POWER", shard=0, campaign_commit="1"*40,
                                   gate_bundle=gate, ledger=root/"ledger.jsonl", terminal=root/"terminal.json",
                                   certificate=root/"certificate.json")
            real_atomic = search.atomic_json
            def selective_failure(path, value):
                if path == args.certificate: raise OSError("synthetic certificate rename failure")
                return real_atomic(path, value)
            one_state = lambda _arm, _shard: iter([({"global_ordinal": 0, "exponent": 3, "p_offset_in_root_interval": 0, "p": 2}, 8, [(2, 3)])])
            fake_certificate = lambda *_args: {"schema": "synthetic-candidate"}
            with (mock.patch.object(search, "verify"), mock.patch.object(search, "arm_states", one_state),
                  mock.patch.object(search, "factor", return_value=[(2, 3)]),
                  mock.patch.object(search, "certificate", side_effect=fake_certificate),
                  mock.patch.object(search, "atomic_json", side_effect=selective_failure)):
                self.assertEqual(search.run(args), 21)
            terminal = json.loads(args.terminal.read_text())
            self.assertEqual((terminal["terminal_reason"], terminal["visited"], terminal["certificate_present"]), ("WORKER_ERROR", 0, False))
            self.assertFalse(args.certificate.exists())

    def test_status_and_duplicate_attestations_are_fail_closed(self):
        status = json.loads((prep.HERE / "source-status-attestation.json").read_text())
        duplicate = json.loads((prep.HERE / "duplicate-scan.json").read_text())
        self.assertEqual(status["observed_upstream_main"], "05ea0345d09375efac830fac93bf083b654e317e")
        self.assertEqual(status["formal_conjectures_status"], "research open")
        self.assertTrue(duplicate["provenance_database_match_found"])
        self.assertFalse(duplicate["novelty_claim_permitted"])


if __name__ == "__main__": unittest.main()
