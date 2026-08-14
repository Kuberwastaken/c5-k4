"""Target-free catalogue, gate, transaction, and mutation tests for A067720."""
from __future__ import annotations

import hashlib
import copy
import json
import pathlib
import signal
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest import mock

import prepare_oeis_a067720_gate as prep
import search_oeis_a067720 as search
import verify_oeis_a067720_candidate as independent


class A067720FreezeTests(unittest.TestCase):
    def test_frozen_caps_arms_and_resolution_shape(self):
        self.assertEqual((prep.M["internal_seconds"], prep.M["external_search_seconds"],
                          prep.M["external_verify_seconds"]), (48, 54, 60))
        self.assertEqual(prep.M["shards"], 24)
        self.assertEqual(set(prep.M["arms"]), {"SUCCESSOR_PROFILE_SURGERY", "TOTIENT_RATIO_WALL"})
        card = json.loads((prep.HERE / "resolution-card.json").read_text())
        self.assertEqual(card["logical_class"], "FINITE_UNIVERSAL")
        self.assertTrue(card["finite_witness_suffices"])
        self.assertFalse(any(card[key] for key in ("answer_placeholder", "eventual_quantifier",
                                                   "global_constant_quantifier", "unbounded_auxiliary_search")))

    def test_full_endpoint_catalogue_is_target_free_and_inside_cap(self):
        """Build profiles only: no rigid translation and no target residual."""
        started = time.monotonic(); catalogue = search.endpoint_catalogue(); elapsed = time.monotonic() - started
        spec = prep.M["profile_catalogues"]
        self.assertEqual(len(catalogue), spec["endpoint_entries"])
        self.assertEqual(search.catalogue_digest(catalogue), spec["endpoint_stream_sha256"])
        self.assertLess(elapsed, spec["catalogue_only_benchmark_cap_seconds"])

    def test_successor_profile_streams_match_independent_generator(self):
        for arm, spec in prep.M["arms"].items():
            discovery = []
            digest = hashlib.sha256()
            for ordinal, value, factors, profile in search.successor_profiles(arm):
                row = {"ordinal": ordinal, "value": value, "factors": [list(item) for item in factors], "profile": profile}
                digest.update(search.canonical(row)); discovery.append(row)
            replay = [{"ordinal": ordinal, "value": value, "factors": factors, "profile": profile}
                      for ordinal, value, factors, profile in independent.profiles(arm)]
            self.assertEqual(discovery, replay)
            self.assertEqual(len(discovery), spec["eligible_profiles"])
            self.assertEqual(digest.hexdigest(), spec["profile_stream_sha256"])

    def test_no_residual_evaluation_without_endpoint_profile(self):
        profiles = [(0, 9, ((3, 2),), {"signature": "SINGLE", "prime_ranks": [2], "exponents": [2]})]
        with mock.patch.object(search, "endpoint_catalogue", return_value={}), \
             mock.patch.object(search, "successor_profiles", return_value=iter(profiles)), \
             mock.patch.object(search, "evaluate_translation", side_effect=AssertionError("residual evaluated")):
            rows = list(search.tuples("SUCCESSOR_PROFILE_SURGERY", 0, {8}))
        self.assertEqual(rows[0][1]["stop"], "NO_TRANSLATED_ENDPOINT_PROFILE")

    def test_known_exception_is_control_never_candidate(self):
        profiles = [(0, 9, ((3, 2),), {"signature": "SINGLE", "prime_ranks": [2], "exponents": [2]})]
        with mock.patch.object(search, "endpoint_catalogue", return_value={65: ((5, 1), (13, 1))}), \
             mock.patch.object(search, "successor_profiles", return_value=iter(profiles)):
            coordinate, outcome = next(search.tuples("SUCCESSOR_PROFILE_SURGERY", 0, {8}))
        self.assertEqual((coordinate["endpoint_factors"], outcome["residual"], outcome["stop"]),
                         ([[5, 1], [13, 1]], 0, "KNOWN_EXCEPTION_CONTROL"))

    def test_small_source_database_sanity_fixture(self):
        rows = "1 1\n2 2\n3 4\n4 6\n5 8\n6 10\n"
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "b.txt"; path.write_text(rows, encoding="ascii")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with mock.patch.dict(prep.M["oeis_bfile"], {"sha256": digest, "rows": 6,
                                                        "last_index": 6, "last_value": 10}, clear=False):
                result = prep.verify_catalogue(path)
        self.assertEqual((result["rows"], result["prime_prime_rows"], result["composite_successor_rows"]),
                         (6, 5, [[5, 8]]))

    def test_live_duplicate_snapshot_requires_complete_known_baseline(self):
        value = {
            "schema": "oeis-a067720-live-duplicate-audit-v1",
            "upstream_head": prep.M["formal_conjectures"]["commit"],
            "upstream_tree": prep.M["formal_conjectures"]["tree"],
            "queries": dict(prep.SEARCH_QUERIES),
            "searches": {
                "upstream_sequence": {"query": prep.SEARCH_QUERIES["upstream_sequence"], "total_count": 2, "incomplete_results": False,
                                      "items": [{"number": 1878, "state": "closed", "is_pull_request": True},
                                                {"number": 1456, "state": "closed", "is_pull_request": False}]},
                "upstream_declaration": {"query": prep.SEARCH_QUERIES["upstream_declaration"], "total_count": 1, "incomplete_results": False,
                                         "items": [{"number": 1878, "state": "closed", "is_pull_request": True}]},
                "local_sequence": {"query": prep.SEARCH_QUERIES["local_sequence"], "total_count": 0, "incomplete_results": False, "items": []},
                "local_declaration": {"query": prep.SEARCH_QUERIES["local_declaration"], "total_count": 0, "incomplete_results": False, "items": []}},
            "known_ingestion_pull": {"number": 1878, "state": "closed", "merged_at": "2026-01-27T15:30:27Z",
                                      "merge_commit_sha": "2e7ff5eeba593908427463753fb363fe61af4863"},
            "open_pull_requests_scanned": 281, "pulls_requiring_full_file_pagination": [3422],
            "open_target_path_matches": [
                {"number": 4198, "head_sha": "1cda50fe1496260c6fe6177543542dcc7acca1fb",
                 "content_sha256": "7387a319aad73fae84ab7088c5b2af1bca1736755ecc07c6a0d1ce7e47112282",
                 "classification": "NON_RESOLVING_STALE_NORMALIZATION", "title": "Update 35.lean",
                 "url": "https://github.com/google-deepmind/formal-conjectures/pull/4198"},
                {"number": 4688, "head_sha": "5e22a9f1dac70e763f3a33dd9eeba59dd008b03f",
                 "content_sha256": "301a72ec827dedbc4e31baf87bf5a61d7380dacdabf89623ada0102288d6333e",
                 "classification": "NON_RESOLVING_MODULE_MAINTENANCE", "title": "chore: modulize FormalConjectures/",
                 "url": "https://github.com/google-deepmind/formal-conjectures/pull/4688"}],
            "local_release_matches": [],
            "release_page_sizes": [11], "releases_scanned": 11,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "live.json"; path.write_bytes(prep.canonical(value))
            self.assertEqual(prep.verify_live_audit(path)["open_pull_requests_scanned"], 281)
            wrong = copy.deepcopy(value); wrong["queries"]["local_sequence"] = "wrong query"
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "query mapping"):
                prep.verify_live_audit(path)
            wrong = copy.deepcopy(value); wrong["searches"]["upstream_declaration"]["query"] = "wrong query"
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "completeness drift"):
                prep.verify_live_audit(path)
            wrong = copy.deepcopy(value); wrong["searches"]["upstream_sequence"]["items"][1]["state"] = "open"
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "baseline drift"):
                prep.verify_live_audit(path)
            wrong = copy.deepcopy(value); wrong["known_ingestion_pull"]["merged_at"] = None
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "merged ingestion"):
                prep.verify_live_audit(path)
            wrong = copy.deepcopy(value); wrong["release_page_sizes"] = [100]
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "release pagination"):
                prep.verify_live_audit(path)
            wrong = copy.deepcopy(value); wrong["open_target_path_matches"].append({"number": 9999, "head_sha": "0" * 40,
                                                                                     "content_sha256": "0" * 64,
                                                                                     "classification": "UNREVIEWED_TARGET_PATH_TOUCH",
                                                                                     "title": "synthetic", "url": "https://example.invalid/9999"})
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "schema/cardinality"):
                prep.verify_live_audit(path)
            wrong = copy.deepcopy(value); wrong["open_target_path_matches"].append(
                copy.deepcopy(wrong["open_target_path_matches"][0]))
            path.write_bytes(prep.canonical(wrong))
            with self.assertRaisesRegex(ValueError, "schema/cardinality"):
                prep.verify_live_audit(path)

    def test_renamed_away_target_is_a_path_touch(self):
        target = prep.M["formal_conjectures"]["path"]
        self.assertTrue(prep.touches_target([{"filename": "FormalConjectures/OEIS/New.lean",
                                              "previous_filename": target, "status": "renamed"}]))
        self.assertTrue(prep.touches_target([{"path": target, "changeType": "MODIFIED"}]))
        self.assertFalse(prep.touches_target([{"filename": "FormalConjectures/OEIS/Other.lean"}]))

    def test_hash_chain_rejects_byte_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "ledger.jsonl"; ledger = search.Ledger(path)
            ledger.append(search.progress("1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0, 0, None, None,
                                          {name: 0 for name in search.STOPS})); ledger.close()
            rows, digest = independent.chain(path, "1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0)
            self.assertEqual(digest, rows[0]["row_sha256"])
            path.write_text(path.read_text().replace('"last_coordinate":null', '"last_coordinate":{}'))
            with self.assertRaisesRegex(ValueError, "hash-chain"):
                independent.chain(path, "1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0)

    def test_ledger_rejects_missing_newline_whitespace_and_extra_key(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "ledger.jsonl"; ledger = search.Ledger(path)
            payload = search.progress("1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0, 0, None, None,
                                      {name: 0 for name in search.STOPS})
            ledger.append(payload); ledger.close(); original = path.read_bytes()
            path.write_bytes(original.rstrip(b"\n"))
            with self.assertRaisesRegex(ValueError, "noncanonical"):
                independent.chain(path, "1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0)
            path.write_bytes(b" " + original)
            with self.assertRaisesRegex(ValueError, "noncanonical"):
                independent.chain(path, "1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0)
            row = json.loads(original); row.pop("row_sha256"); row["extra"] = 1
            row["row_sha256"] = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
            path.write_bytes(independent.canonical(row))
            with self.assertRaisesRegex(ValueError, "key drift"):
                independent.chain(path, "1" * 40, "SUCCESSOR_PROFILE_SURGERY", 0)

    def test_terminal_rejects_extra_key_and_negative_or_boolean_visited(self):
        base = {"schema": "oeis-a067720-terminal-v1", "campaign_commit": "1" * 40,
                "source_commit": prep.M["formal_conjectures"]["commit"], "gate_attestation_sha256": "0" * 64,
                "arm": "SUCCESSOR_PROFILE_SURGERY", "shard": 0, "algebraic_profile_domain_only": True,
                "catalogue_rows": 10000, "visited": 0, "last_coordinate": None, "last_outcome": None,
                "counts": {name: 0 for name in independent.STOPS}, "terminal_reason": "CAP_PREFIX",
                "certificate_present": False, "worker_error": None, "ledger_rows": 0,
                "final_row_sha256": independent.ZERO, "ledger_sha256": "0" * 64}
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory); terminal_path = root / "terminal.json"; ledger_path = root / "ledger"
            for mutation, pattern in (({"extra": 1}, "key drift"), ({"visited": -1}, "numeric field"),
                                      ({"visited": False}, "numeric field"), ({"shard": False}, "numeric field"),
                                      ({"certificate_present": 0}, "must be Boolean")):
                document = {**base, **mutation}; terminal_path.write_bytes(independent.canonical(document))
                with mock.patch.object(independent, "verify", return_value={}), \
                     mock.patch.object(independent, "chain", return_value=([], independent.ZERO)):
                    with self.assertRaisesRegex(ValueError, pattern):
                        independent.terminal(ledger_path, terminal_path, None, root, "1" * 40,
                                             "SUCCESSOR_PROFILE_SURGERY", 0)

    def test_replay_rejects_early_survivor_followed_by_later_state(self):
        zero = {"schema": "oeis-a067720-progress-v1", "campaign_commit": "1" * 40,
                "arm": "SUCCESSOR_PROFILE_SURGERY", "shard": 0, "visited": 0,
                "last_coordinate": None, "last_outcome": None,
                "counts": {name: 0 for name in independent.STOPS}}
        coordinate = {"successor_profile_ordinal": 0}; later = {"successor_profile_ordinal": 1}
        outcomes = [(coordinate, {"stop": "SURVIVOR"}), (later, {"stop": "RESIDUAL_NONZERO"})]
        terminal = {"visited": 2, "arm": "SUCCESSOR_PROFILE_SURGERY", "shard": 0,
                    "algebraic_profile_domain_only": True, "last_coordinate": later,
                    "last_outcome": outcomes[-1][1], "counts": {name: (1 if name in {"SURVIVOR", "RESIDUAL_NONZERO"} else 0) for name in independent.STOPS},
                    "terminal_reason": "CERTIFICATE_FOUND"}
        with mock.patch.object(independent, "independent_tuples", return_value=iter(outcomes)):
            with self.assertRaisesRegex(ValueError, "first survivor and final"):
                independent.replay(terminal, [zero], {"coordinate": coordinate}, set())

    def test_alarm_is_deferred_through_atomic_state_transition(self):
        previous = signal.getsignal(signal.SIGALRM); state = []
        signal.signal(signal.SIGALRM, search.alarm_handler)
        try:
            with self.assertRaises(search.Deadline):
                with search.block_alarm():
                    state.append("committed"); signal.raise_signal(signal.SIGALRM)
            self.assertEqual(state, ["committed"])
        finally:
            signal.signal(signal.SIGALRM, previous)

    @staticmethod
    def args(root: pathlib.Path) -> SimpleNamespace:
        gate = root / "gate"; (gate / "snapshots").mkdir(parents=True)
        (gate / "gate-attestation.json").write_text("{}\n")
        (gate / "snapshots/b067720.txt").write_text("1 8\n")
        return SimpleNamespace(arm="SUCCESSOR_PROFILE_SURGERY", shard=0,
                               campaign_commit="1" * 40, gate_bundle=gate,
                               ledger=root / "ledger.jsonl", terminal=root / "terminal.json",
                               certificate=root / "certificate.json")

    def test_certificate_rename_failure_preserves_pre_candidate_prefix(self):
        coordinate = {"successor": 25}; outcome = {"stop": "SURVIVOR", "k": 24, "endpoint": 577}
        with tempfile.TemporaryDirectory() as directory:
            args = self.args(pathlib.Path(directory)); real = search.atomic_json
            def fail_certificate(path, value):
                if path == args.certificate:
                    raise OSError("synthetic certificate rename failure")
                return real(path, value)
            with mock.patch.object(search, "verify", return_value={"table": {"catalogue": {"rows": 1}}}), \
                 mock.patch.object(search, "parse_bfile", return_value=[(1, 8)]), \
                 mock.patch.object(search, "tuples", return_value=iter([(coordinate, outcome)])), \
                 mock.patch.object(search, "make_certificate", return_value={"schema": "synthetic"}), \
                 mock.patch.object(search, "atomic_json", side_effect=fail_certificate):
                self.assertEqual(search.run(args), 21)
            terminal = json.loads(args.terminal.read_text())
            self.assertEqual((terminal["terminal_reason"], terminal["visited"], terminal["certificate_present"]),
                             ("WORKER_ERROR", 0, False))

    def test_no_ledger_append_after_durable_candidate(self):
        coordinate = {"successor": 25}; outcome = {"stop": "SURVIVOR", "k": 24, "endpoint": 577}
        calls = 0; actual_append = search.Ledger.append
        def forbid_second(ledger, payload):
            nonlocal calls; calls += 1
            if calls == 2:
                raise AssertionError("post-certificate ledger append")
            return actual_append(ledger, payload)
        with tempfile.TemporaryDirectory() as directory:
            args = self.args(pathlib.Path(directory))
            with mock.patch.object(search, "verify", return_value={"table": {"catalogue": {"rows": 1}}}), \
                 mock.patch.object(search, "parse_bfile", return_value=[(1, 8)]), \
                 mock.patch.object(search, "tuples", return_value=iter([(coordinate, outcome)])), \
                 mock.patch.object(search, "make_certificate", return_value={"schema": "synthetic"}), \
                 mock.patch.object(search.Ledger, "append", new=forbid_second):
                self.assertEqual(search.run(args), 0)
            terminal = json.loads(args.terminal.read_text())
            self.assertEqual((terminal["terminal_reason"], terminal["visited"], terminal["certificate_present"], calls),
                             ("CERTIFICATE_FOUND", 1, True, 1))


if __name__ == "__main__":
    unittest.main()
