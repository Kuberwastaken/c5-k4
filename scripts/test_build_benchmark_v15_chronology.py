#!/usr/bin/env python3
"""Focused offline tests for Method v1.5 chronology capture."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("build_benchmark_v15_chronology.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v15_chronology", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)

OID_A = "a" * 40
OID_B = "b" * 40
OID_C = "c" * 40
OID_D = "d" * 40


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class ChronologyTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = C.ROOT / "results" / "benchmark"
        self.temp = tempfile.TemporaryDirectory(prefix="v15-chronology-test-", dir=parent)
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def u1(self, completed: str = "2026-08-16T20:00:00Z") -> dict:
        _, rule_sha = C.load_rule()
        return {
            "schema": C.SCHEMA,
            "artifact_kind": "U1_CHRONOLOGY_RECEIPT",
            "protocol_version": "1.5",
            "chronology_rule": {
                "path": C.CHRONOLOGY_RULE.relative_to(C.ROOT).as_posix(),
                "sha256": rule_sha,
            },
            "p1": {
                "p1a_commit": OID_A,
                "p1t_commit": OID_B,
                "public_receipt": {
                    "repository": C.PROTOCOL_PUBLIC_REPOSITORY,
                    "ref": C.PROTOCOL_PUBLIC_REF,
                    "observed_tip": OID_B,
                    "verification_completed_at_utc": "2026-08-16T19:00:00Z",
                },
            },
            "upstream": {
                "repository": C.UPSTREAM_REPOSITORY,
                "ref": C.UPSTREAM_REF,
                "fetch_count": 1,
                "retry_count": 0,
                "capture_started_at_utc": "2026-08-16T19:30:00Z",
                "capture_completed_at_utc": completed,
                "commit": OID_C,
                "root_tree": OID_D,
                "formal_conjectures_tree": OID_A,
            },
            "status": "VALID_U1",
        }

    def write(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def test_frozen_schedule_matches_committed_scaffold(self) -> None:
        rule, _ = C.load_rule()
        self.assertEqual(rule["checkpoint_schedule"]["cron"], "17 0 * * *")
        self.assertEqual(C.LAST_CHECKPOINT, "2027-08-15T00:17:00Z")
        for invalid in (
            "2026-08-17T00:16:00Z", "2026-08-17T00:17:01Z",
            "2027-08-16T00:17:00Z",
        ):
            with self.assertRaises(C.ChronologyError, msg=invalid):
                C.checkpoint_time(invalid)

    def test_p1t_requires_exact_direct_parent_and_only_attestation_path(self) -> None:
        p1t_path = self.root / "p1t.json"
        relative = p1t_path.relative_to(C.ROOT).as_posix()
        p1a_raw = b'{"artifact_kind":"P1A"}\n'
        artifact = {
            "artifact_kind": "P1T",
            "protocol_version": "1.5",
            "p1a_commit": OID_A,
            "p1a": {"path": "results/benchmark/v1.5-protocol/P1A.json", "sha256": C.sha256_bytes(p1a_raw)},
            "p1a_published_at_utc": "2026-08-16T18:00:00Z",
            "attestation_policy": {
                "p1a_ancestor_required": True,
                "p1a_bytes_immutable": True,
                "allowed_p1t_changed_paths": [relative],
            },
        }
        p1t_path.write_text(json.dumps(artifact), encoding="utf-8")

        def git_ok(*args: str) -> bytes:
            if args == ("rev-parse", OID_B):
                return (OID_B + "\n").encode()
            if args == ("show", "-s", "--format=%P", OID_B):
                return (OID_A + "\n").encode()
            if args[:4] == ("diff-tree", "--no-commit-id", "--name-only", "-r"):
                return (relative + "\n").encode()
            raise AssertionError(args)

        def committed(commit: str, path: str) -> bytes:
            return p1t_path.read_bytes() if commit == OID_B else p1a_raw

        with mock.patch.object(C, "local_git", side_effect=git_ok), mock.patch.object(C, "commit_file", side_effect=committed):
            C.validate_p1t(p1t_path, OID_B)
        def git_merge(*args: str) -> bytes:
            if args == ("rev-parse", OID_B):
                return (OID_B + "\n").encode()
            if args == ("show", "-s", "--format=%P", OID_B):
                return (OID_A + " " + OID_C + "\n").encode()
            raise AssertionError(args)

        with mock.patch.object(C, "local_git", side_effect=git_merge), mock.patch.object(C, "commit_file", side_effect=committed):
            with self.assertRaisesRegex(C.ChronologyError, "sole parent"):
                C.validate_p1t(p1t_path, OID_B)

    def test_public_receipt_requires_canonical_main_equal_exact_p1t(self) -> None:
        completed = subprocess.CompletedProcess([], 0, f"{OID_B}\t{C.PROTOCOL_PUBLIC_REF}\n".encode(), b"")
        with mock.patch.object(C, "_run", return_value=completed), mock.patch.object(
            C, "_now", side_effect=[utc("2026-08-16T18:00:00Z"), utc("2026-08-16T18:00:01Z")]
        ):
            receipt = C.verify_public_p1t(OID_B)
        self.assertEqual(receipt["repository"], C.PROTOCOL_PUBLIC_REPOSITORY)
        self.assertEqual(receipt["ref"], "refs/heads/main")
        bad = subprocess.CompletedProcess([], 0, f"{OID_C}\t{C.PROTOCOL_PUBLIC_REF}\n".encode(), b"")
        with mock.patch.object(C, "_run", return_value=bad), mock.patch.object(
            C, "_now", side_effect=[utc("2026-08-16T18:00:00Z"), utc("2026-08-16T18:00:01Z")]
        ):
            with self.assertRaisesRegex(C.ChronologyError, "does not resolve exactly"):
                C.verify_public_p1t(OID_B)

    def test_capture_is_one_atomic_no_retry_fetch_of_canonical_main(self) -> None:
        destination = self.root / "upstream.git"
        commands: list[list[str]] = []

        def run(command, cwd=None):
            commands.append(list(command))
            if "init" in command:
                destination.mkdir()
            return subprocess.CompletedProcess(command, 0, b"fetch output\n", b"")

        def bare(_destination: Path, *args: str) -> bytes:
            if args[:2] == ("for-each-ref", "--format=%(refname)"):
                return (C.UPSTREAM_REF + "\n").encode()
            if args[:2] == ("config", "--get-regexp"):
                return b""
            if args == ("fsck", "--full", "--strict"):
                return b""
            if args == ("rev-parse", C.UPSTREAM_REF):
                return (OID_A + "\n").encode()
            if args == ("rev-parse", f"{OID_A}^{{tree}}"):
                return (OID_B + "\n").encode()
            if args == ("rev-parse", f"{OID_A}:FormalConjectures"):
                return (OID_C + "\n").encode()
            if args == ("cat-file", "-t", OID_A):
                return b"commit\n"
            if args == ("cat-file", "-t", OID_C):
                return b"tree\n"
            raise AssertionError(args)

        with mock.patch.object(C, "_run", side_effect=run), mock.patch.object(C, "_bare_git", side_effect=bare), mock.patch.object(
            C, "_now", side_effect=[utc("2026-08-17T00:17:01Z"), utc("2026-08-17T00:17:02Z")]
        ):
            receipt = C.capture_upstream(destination)
        fetches = [command for command in commands if "fetch" in command]
        self.assertEqual(len(fetches), 1)
        self.assertIn("--atomic", fetches[0])
        self.assertIn("--no-tags", fetches[0])
        self.assertIn("--no-write-fetch-head", fetches[0])
        self.assertIn(C.UPSTREAM_REPOSITORY, fetches[0])
        self.assertIn(f"+{C.UPSTREAM_REF}:{C.UPSTREAM_REF}", fetches[0])
        self.assertEqual(receipt["fetch_count"], 1)
        self.assertEqual(receipt["retry_count"], 0)

    def test_u1_capture_must_start_strictly_after_public_p1t_verification(self) -> None:
        p1t = {"p1a_commit": OID_A, "p1a_published_at_utc": "2026-08-16T18:00:00Z"}
        public = {
            "verification_started_at_utc": "2026-08-16T18:30:00Z",
            "verification_completed_at_utc": "2026-08-16T18:30:01Z",
        }
        upstream = {"capture_started_at_utc": "2026-08-16T18:30:01Z"}
        with mock.patch.object(C, "validate_p1t", return_value=p1t), mock.patch.object(C, "verify_public_p1t", return_value=public), mock.patch.object(C, "capture_upstream", return_value=upstream):
            with self.assertRaisesRegex(C.ChronologyError, "strictly after"):
                C.build_u1(self.root / "p1t.json", OID_B, self.root / "bare")

    def test_checkpoint_chain_cannot_skip_duplicate_or_continue_after_pass(self) -> None:
        u1 = self.u1()
        with mock.patch.object(C, "validate_u1", return_value=u1):
            ordinal, previous, scheduled = C.checkpoint_position(u1, None, "2026-08-17T00:17:00Z")
        self.assertEqual((ordinal, previous, scheduled), (1, None, utc("2026-08-17T00:17:00Z")))
        fail = {
            "schema": C.SCHEMA, "artifact_kind": "CHECKPOINT_RECEIPT",
            "checkpoint_ordinal": 1, "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "status": "QUOTA_FAIL",
        }
        fail_path = self.write("fail.json", fail)
        with mock.patch.object(C, "validate_u1", return_value=u1):
            with self.assertRaisesRegex(C.ChronologyError, "skipped"):
                C.checkpoint_position(u1, fail_path, "2026-08-19T00:17:00Z")
        fail["status"] = "QUOTA_PASS_U2"
        self.write("pass.json", fail)
        with self.assertRaisesRegex(C.ChronologyError, "terminal"):
            C.checkpoint_position(u1, self.root / "pass.json", "2026-08-18T00:17:00Z")

    def test_manual_rerun_and_late_checkpoint_are_rejected(self) -> None:
        u1 = self.u1()
        u1_path = self.write("u1.json", u1)
        with mock.patch.object(C, "validate_u1", return_value=u1):
            with self.assertRaisesRegex(C.ChronologyError, "original schedule"):
                C.capture_checkpoint(u1_path, None, "2026-08-17T00:17:00Z", "workflow_dispatch", 1, self.root / "bare1")
            with self.assertRaisesRegex(C.ChronologyError, "original schedule"):
                C.capture_checkpoint(u1_path, None, "2026-08-17T00:17:00Z", "schedule", 2, self.root / "bare2")
            with mock.patch.object(C, "_now", return_value=utc("2026-08-17T06:00:00Z")):
                with self.assertRaisesRegex(C.ChronologyError, "window"):
                    C.capture_checkpoint(u1_path, None, "2026-08-17T00:17:00Z", "schedule", 1, self.root / "bare3")

    def test_quota_certificate_closes_at_first_replayed_pass(self) -> None:
        capture = {
            "schema": C.SCHEMA,
            "artifact_kind": "CHECKPOINT_CAPTURE",
            "protocol_version": "1.5",
            "chronology_rule": {"path": "rule", "sha256": "f" * 64},
            "checkpoint_ordinal": 1,
            "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "basis": {"u1_receipt": {"commit": OID_A}, "previous_checkpoint": None},
            "upstream": {"commit": OID_B, "root_tree": OID_C, "formal_conjectures_tree": OID_D},
        }
        capture_path = self.write("capture.json", capture)
        counts = dict(C.STRATA_QUOTAS)
        aggregates = {
            "eligible_by_stratum": counts, "quotas": dict(C.STRATA_QUOTAS),
            "deficits": {key: 0 for key in C.STRATA_QUOTAS},
            "status": "PASS", "candidate_count": 12,
        }
        certificate = {
            "certificate_sha256": "e" * 64,
            "checkpoint": {"ordinal": 1, "scheduled_for_utc": "2026-08-17T00:17:00Z"},
            "upstream": {"commit": OID_B, "root_tree": OID_C, "formal_conjectures_tree": OID_D},
            "chronology": {"receipt": {"path": capture_path.relative_to(C.ROOT).as_posix(), "sha256": C.sha256_file(capture_path)}},
            "aggregates": aggregates,
        }
        certificate_path = self.write("certificate.json", certificate)
        attestation = {
            "certificate_sha256": "e" * 64,
            "chronology_receipt_sha256": C.sha256_file(capture_path),
            "upstream": {"commit": OID_B, "root_tree": OID_C, "formal_conjectures_tree": OID_D},
        }
        attestation["attestation_sha256"] = C.aggregate.attestation_digest(attestation)
        attestation_path = self.write("attestation.json", attestation)
        with mock.patch.object(C.aggregate, "validate_certificate"), mock.patch.object(C.aggregate, "validate_schema"):
            receipt = C.finalize_checkpoint(capture_path, certificate_path, attestation_path)
        self.assertEqual(receipt["status"], "QUOTA_PASS_U2")
        self.assertEqual(receipt["u2"]["membership_interval"], f"{OID_A}..{OID_B}")
        certificate["aggregates"]["deficits"]["FINITE_COMBINATORIAL"] = 1
        self.write("bad-certificate.json", certificate)
        with self.assertRaisesRegex(C.ChronologyError, "deficits"):
            with mock.patch.object(C.aggregate, "validate_certificate"), mock.patch.object(C.aggregate, "validate_schema"):
                C.finalize_checkpoint(capture_path, self.root / "bad-certificate.json", attestation_path)


if __name__ == "__main__":
    unittest.main()
