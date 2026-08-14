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

    def activation(self, path: str = "results/benchmark/v1.5-protocol/P1R.json", sha: str = "e" * 64) -> dict:
        value = {
            "schema": "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
            "p1r": {"path": path, "sha256": sha}, "p1r_commit": OID_D,
            "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
            "public_observation": {
                "workflow_repository": "Kuberwastaken/c5-k4",
                "workflow_path": ".github/workflows/method-v15-p1r-publication-observer.yml",
                "workflow_blob_sha256": "a" * 64,
                "workflow_ref": ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r",
                "run_id": 1, "run_attempt": 1,
                "server_observed_at_utc": "2026-08-16T19:00:00Z",
                "actions_run_projection_sha256": "b" * 64,
            },
            "validation_inputs_sha256": "c" * 64,
            "validation_diagnostic_sha256": "d" * 64,
            "validator": {"path": "scripts/validate_benchmark_v15_candidate_base.py", "sha256": "f" * 64},
        }
        value["receipt_sha256"] = C.sha256_bytes(
            b"c5k4-method-v1.5-public-p1r-activation-receipt-1.0\0" + C.canonical_json(value)
        )
        return value

    def u1(self, completed: str = "2026-08-16T20:00:00Z") -> dict:
        _, rule_sha = C.load_rule()
        activation = self.activation()
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
                "p1r_commit": OID_D,
                "p1r_artifact": {"path": "results/benchmark/v1.5-protocol/P1R.json", "sha256": "e" * 64},
                "validation_input": {"path": "results/benchmark/v1.5-protocol/validation-input.json", "sha256": "c" * 64},
                "activation_receipt": activation,
                "p1r_activation_sha256": C.sha256_bytes(C.canonical_json(activation)),
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

    def test_u1_requires_full_public_p1r_verifier_and_exact_receipt(self) -> None:
        p1r_path = self.root / "p1r.json"
        p1r_path.write_text("{}\n", encoding="utf-8")
        validation_input = self.write("validation-input.json", {"frozen": True})
        with self.assertRaisesRegex(C.ChronologyError, "not wired"):
            C.require_public_p1r_activation(p1r_path, OID_D, None)
        expected = self.activation(p1r_path.relative_to(C.ROOT).as_posix(), C.sha256_file(p1r_path))
        expected["validation_inputs_sha256"] = C.sha256_file(validation_input)
        expected["receipt_sha256"] = C.sha256_bytes(
            b"c5k4-method-v1.5-public-p1r-activation-receipt-1.0\0"
            + C.canonical_json({k: v for k, v in expected.items() if k != "receipt_sha256"})
        )
        self.assertEqual(
            C.require_public_p1r_activation(
                p1r_path, OID_D, lambda *_, **__: expected,
                validation_input_path=validation_input,
            ),
            expected,
        )
        with self.assertRaisesRegex(C.ChronologyError, "exact P1R"):
            C.require_public_p1r_activation(
                p1r_path, OID_D,
                lambda *_, **__: {**expected, "activation_boundary": "BARE_P1T"},
                validation_input_path=validation_input,
            )

    def test_structural_p1r_or_bare_p1t_cannot_authorize_u1_capture(self) -> None:
        with mock.patch.object(C, "validate_p1r_structure", return_value=({}, {})), mock.patch.object(
            C, "capture_upstream"
        ) as capture:
            with self.assertRaisesRegex(C.ChronologyError, "not wired"):
                C.build_u1(
                    self.root / "p1t.json", OID_B, self.root / "p1r.json", OID_D,
                    self.root / "bare", activation_verifier=None,
                )
        capture.assert_not_called()

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

    def test_u1_capture_must_start_strictly_after_public_p1r_activation(self) -> None:
        p1t = {"p1a_commit": OID_A, "p1a_published_at_utc": "2026-08-16T18:00:00Z"}
        activation = self.activation("p1r.json")
        upstream = {"capture_started_at_utc": "2026-08-16T18:30:01Z"}
        with mock.patch.object(C, "validate_p1r_structure", return_value=(p1t, {})), mock.patch.object(
            C, "require_public_p1r_activation", return_value=activation
        ), mock.patch.object(C, "capture_upstream", return_value=upstream):
            with self.assertRaisesRegex(C.ChronologyError, "strictly after"):
                C.build_u1(
                    self.root / "p1t.json", OID_B, self.root / "p1r.json", OID_D,
                    self.root / "bare", activation_verifier=lambda *_: activation,
                )

    def test_u1_uses_public_server_time_and_seals_full_receipt_digest(self) -> None:
        validation_input = self.write("sealed-validation-input.json", {"frozen": True})
        p1t_path = self.write("p1t.json", {"artifact_kind": "P1T"})
        p1r_path = self.write("p1r.json", {"artifact_kind": "P1R"})
        activation = self.activation("p1r.json")
        activation["validation_inputs_sha256"] = C.sha256_file(validation_input)
        activation["receipt_sha256"] = C.sha256_bytes(
            b"c5k4-method-v1.5-public-p1r-activation-receipt-1.0\0"
            + C.canonical_json({k: v for k, v in activation.items() if k != "receipt_sha256"})
        )
        upstream = {
            "capture_started_at_utc": "2026-08-16T19:00:01Z",
            "capture_completed_at_utc": "2026-08-16T19:00:02Z",
        }
        with mock.patch.object(C, "validate_p1r_structure", return_value=({"p1a_commit": OID_A}, {})), mock.patch.object(
            C, "require_public_p1r_activation", return_value=activation
        ), mock.patch.object(C, "capture_upstream", return_value=upstream):
            value = C.build_u1(
                p1t_path, OID_B, p1r_path, OID_D,
                self.root / "bare", activation_verifier=lambda *_: activation,
                validation_input_path=validation_input,
            )
        self.assertNotIn("activation_verified_at_utc", value["p1"])
        self.assertEqual(value["p1"]["activation_receipt"], activation)
        self.assertEqual(
            value["p1"]["p1r_activation_sha256"],
            C.sha256_bytes(C.canonical_json(activation)),
        )

    def test_position_is_derived_only_from_authenticated_chain_proof(self) -> None:
        u1 = self.u1()
        chain = {
            "terminal": False, "checkpoint_count": 0, "previous_checkpoint": None,
            "next_checkpoint": {"ordinal": 1, "scheduled_for_utc": "2026-08-17T00:17:00Z"},
        }
        ordinal, previous, scheduled = C.checkpoint_position(
            u1, chain, "2026-08-17T00:17:00Z"
        )
        self.assertEqual((ordinal, previous, scheduled), (1, None, utc("2026-08-17T00:17:00Z")))
        with self.assertRaisesRegex(C.ChronologyError, "authenticated next"):
            C.checkpoint_position(u1, chain, "2026-08-18T00:17:00Z")
        chain["terminal"] = True
        chain["next_checkpoint"] = None
        with self.assertRaisesRegex(C.ChronologyError, "terminal"):
            C.checkpoint_position(u1, chain, "2026-08-17T00:17:00Z")

    def test_chain_proof_is_replayed_not_trusted_as_caller_json(self) -> None:
        proof = {
            "schema": C.public_chain.PROOF_SCHEMA,
            "public_tip_commit": OID_A,
        }
        proof["proof_sha256"] = C.public_chain.proof_digest(proof)
        path = self.write("chain-proof.json", proof)
        with mock.patch.object(C.public_chain, "verify_chain", return_value=proof):
            self.assertEqual(
                C.validate_public_chain_proof(path, self.root, C.public_chain.PUBLICATION_REF, OID_B),
                proof,
            )
        altered = dict(proof)
        altered["public_tip_commit"] = OID_C
        altered["proof_sha256"] = C.public_chain.proof_digest(altered)
        altered_path = self.write("altered-chain-proof.json", altered)
        with mock.patch.object(C.public_chain, "verify_chain", return_value=proof):
            with self.assertRaisesRegex(C.ChronologyError, "differs from replay"):
                C.validate_public_chain_proof(
                    altered_path, self.root, C.public_chain.PUBLICATION_REF, OID_B
                )

    def test_manual_rerun_and_late_checkpoint_are_rejected(self) -> None:
        u1 = self.u1()
        u1_path = self.write("u1.json", u1)
        basis = (u1, 1, None, utc("2026-08-17T00:17:00Z"), {})
        with mock.patch.object(C, "_checkpoint_basis", return_value=basis):
            with self.assertRaisesRegex(C.ChronologyError, "original schedule"):
                C.capture_checkpoint(u1_path, self.root / "proof", self.root, C.public_chain.PUBLICATION_REF, "2026-08-17T00:17:00Z", "workflow_dispatch", 1, self.root / "bare1")
            with self.assertRaisesRegex(C.ChronologyError, "original schedule"):
                C.capture_checkpoint(u1_path, self.root / "proof", self.root, C.public_chain.PUBLICATION_REF, "2026-08-17T00:17:00Z", "schedule", 2, self.root / "bare2")
            with mock.patch.object(C, "_now", return_value=utc("2026-08-17T06:00:00Z")):
                with self.assertRaisesRegex(C.ChronologyError, "window"):
                    C.capture_checkpoint(u1_path, self.root / "proof", self.root, C.public_chain.PUBLICATION_REF, "2026-08-17T00:17:00Z", "schedule", 1, self.root / "bare3")

    def test_expired_unpublished_tick_is_terminal_not_caught_up(self) -> None:
        u1 = self.u1()
        basis = (u1, 1, None, utc("2026-08-17T00:17:00Z"), {})
        with mock.patch.object(C, "_checkpoint_basis", return_value=basis), mock.patch.object(
            C, "_now", return_value=utc("2026-08-18T00:17:00Z")
        ):
            receipt = C.record_missed_checkpoint(
                self.root / "u1", self.root / "proof", self.root,
                C.public_chain.PUBLICATION_REF, "2026-08-17T00:17:00Z",
            )
        self.assertEqual(receipt["status"], "INVALID_CHRONOLOGY_CAPTURE")
        self.assertFalse(receipt["terminal_horizon"])

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
