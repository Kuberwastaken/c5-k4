#!/usr/bin/env python3
"""Security-unit tests for the verify-only candidate-base validator."""

from __future__ import annotations

import copy
import base64
from datetime import timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("candidate_base_validator", HERE / "validate_benchmark_v15_candidate_base.py")
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class FakeRepo:
    def __init__(self, workflow: bytes = b"frozen observer\n") -> None:
        self.workflow = workflow

    def blob(self, commit: str, path: str) -> bytes:
        if path not in {V.P1T_OBSERVER_WORKFLOW_PATH, V.P1R_OBSERVER_WORKFLOW_PATH}:
            raise AssertionError(path)
        return self.workflow


def actions_run() -> dict:
    return {
        "id": 17, "run_attempt": 1, "event": "push", "status": "completed", "conclusion": "success",
        "head_sha": "b" * 40, "head_branch": "method-v1.5-p1", "path": V.P1T_OBSERVER_WORKFLOW_PATH,
        "created_at": "2026-08-14T10:00:00Z", "run_started_at": "2026-08-14T10:00:01Z",
        "updated_at": "2026-08-14T10:00:02Z", "repository": {"full_name": "Kuberwastaken/c5-k4"},
        "head_repository": {"full_name": "Kuberwastaken/c5-k4"},
    }


def observation(run: dict) -> dict:
    projected = V.actions_run_projection(run)
    return {
        "observed_at_utc": run["updated_at"],
        "observer": {
            "workflow_repository": "Kuberwastaken/c5-k4", "workflow_path": V.P1T_OBSERVER_WORKFLOW_PATH,
            "workflow_ref": f"{V.P1T_OBSERVER_WORKFLOW_PATH}@refs/heads/method-v1.5-p1",
            "workflow_blob_sha256": V.sha256(b"frozen observer\n"), "run_id": 17, "run_attempt": 1,
            "actions_run_projection_sha256": V.domain_digest(
                "c5k4-method-v1.5-p1t-actions-run-projection-1.0", projected
            ),
        },
    }


def p1r_actions_run() -> dict:
    value = actions_run()
    value.update({
        "id": 23, "head_sha": "c" * 40, "head_branch": "method-v1.5-p1r",
        "path": V.P1R_OBSERVER_WORKFLOW_PATH, "updated_at": "2026-08-14T10:01:02Z",
    })
    return value


def p1r_observer(run: dict) -> dict:
    projection = V.actions_run_projection(run)
    return {
        "workflow_repository": "Kuberwastaken/c5-k4", "workflow_path": V.P1R_OBSERVER_WORKFLOW_PATH,
        "workflow_ref": f"{V.P1R_OBSERVER_WORKFLOW_PATH}@{V.P1R_PUBLIC_REF}",
        "workflow_blob_sha256": V.sha256(b"frozen observer\n"), "run_id": 23, "run_attempt": 1,
        "server_observed_at_utc": run["updated_at"],
        "actions_run_projection_sha256": V.domain_digest(
            "c5k4-method-v1.5-p1r-actions-run-projection-1.0", projection
        ),
    }


class ObserverReplayTests(unittest.TestCase):
    def verify(self, obs: dict, run: dict) -> None:
        with mock.patch.object(V, "fetch_github_actions_run", return_value=run):
            value = V.verify_p1t_actions_observer(
                FakeRepo(), "a" * 40, "b" * 40, "refs/heads/method-v1.5-p1", obs
            )
        self.assertEqual(value.tzinfo, timezone.utc)

    def test_exact_authenticated_run_accepts(self) -> None:
        run = actions_run(); self.verify(observation(run), run)

    def test_forged_timestamp_run_workflow_head_and_rerun_fail_closed(self) -> None:
        cases = []
        run = actions_run(); obs = observation(run); obs["observed_at_utc"] = "2099-01-01T00:00:00Z"; cases.append((obs, run))
        run = actions_run(); obs = observation(run); obs["observer"]["run_id"] = 18; cases.append((obs, run))
        run = actions_run(); obs = observation(run); obs["observer"]["workflow_path"] = ".github/workflows/other.yml"; cases.append((obs, run))
        run = actions_run(); run["head_sha"] = "c" * 40; obs = observation(run); cases.append((obs, run))
        run = actions_run(); run["run_attempt"] = 2; obs = observation(run); obs["observer"]["run_attempt"] = 2; cases.append((obs, run))
        for obs, run in cases:
            with self.subTest(obs=obs, run=run), mock.patch.object(V, "fetch_github_actions_run", return_value=run), self.assertRaises(V.CandidateBaseError):
                V.verify_p1t_actions_observer(FakeRepo(), "a" * 40, "b" * 40, "refs/heads/method-v1.5-p1", obs)

    def test_exact_p1r_publication_run_accepts(self) -> None:
        run = p1r_actions_run(); observer = p1r_observer(run)
        with mock.patch.object(V, "fetch_github_actions_run", return_value=run):
            projection, observed = V.verify_p1r_publication_observer(
                FakeRepo(), "a" * 40, "c" * 40, V.P1R_PUBLIC_REF, observer
            )
        self.assertEqual(projection["head_sha"], "c" * 40)
        self.assertEqual(observed.tzinfo, timezone.utc)

    def test_p1r_wrong_ref_timestamp_run_workflow_head_or_rerun_rejected(self) -> None:
        base_run = p1r_actions_run()
        cases = []
        observer = p1r_observer(base_run); observer["server_observed_at_utc"] = "2099-01-01T00:00:00Z"; cases.append((observer, base_run, V.P1R_PUBLIC_REF))
        observer = p1r_observer(base_run); observer["run_id"] = 24; cases.append((observer, base_run, V.P1R_PUBLIC_REF))
        observer = p1r_observer(base_run); observer["workflow_path"] = ".github/workflows/other.yml"; cases.append((observer, base_run, V.P1R_PUBLIC_REF))
        run = p1r_actions_run(); run["head_sha"] = "d" * 40; cases.append((p1r_observer(run), run, V.P1R_PUBLIC_REF))
        run = p1r_actions_run(); run["run_attempt"] = 2; observer = p1r_observer(run); observer["run_attempt"] = 2; cases.append((observer, run, V.P1R_PUBLIC_REF))
        cases.append((p1r_observer(base_run), base_run, "refs/heads/main"))
        for observer, run, public_ref in cases:
            with self.subTest(observer=observer, run=run, ref=public_ref), mock.patch.object(V, "fetch_github_actions_run", return_value=run), self.assertRaises(V.CandidateBaseError):
                V.verify_p1r_publication_observer(FakeRepo(), "a" * 40, "c" * 40, public_ref, observer)


class IsolationBoundaryTests(unittest.TestCase):
    def test_no_direct_subprocess_fallback_executes_malicious_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); artifact = root / "artifact.json"; marker = root / "escaped"
            artifact.write_text("{}\n", encoding="utf-8")
            malicious = f"from pathlib import Path; Path({str(marker)!r}).write_text('escaped')\n".encode()
            row = {
                "domain": "IMMUTABLE_WORM_STORE", "accepted_status": "x", "candidate_commit": "a" * 40,
                "authority_root_commit": "b" * 40, "service_epoch_binding_sha256": "c" * 64,
                "challenge_nonce": "nonce",
            }
            with self.assertRaisesRegex(V.CandidateBaseError, "proved isolated runner is not wired"):
                V.run_frozen_evidence_verifier(malicious, V.sha256(malicious), b"{}\n", artifact, V.sha256(b"{}\n"), row)
            self.assertFalse(marker.exists())


class ImmutableActivationInputTests(unittest.TestCase):
    def test_exact_nonwritable_single_link_input_accepts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation-input.json"; raw = b'{"exact":true}\n'
            path.write_bytes(raw); path.chmod(0o444)
            self.assertEqual(V.read_immutable_validation_input(path, V.sha256(raw)), raw)

    def test_writable_symlink_hardlink_and_digest_drift_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / "input.json"; raw = b"{}\n"; path.write_bytes(raw)
            with self.assertRaises(V.CandidateBaseError):
                V.read_immutable_validation_input(path, V.sha256(raw))
            path.chmod(0o444)
            with self.assertRaises(V.CandidateBaseError):
                V.read_immutable_validation_input(path, "0" * 64)
            link = root / "symlink.json"; link.symlink_to(path)
            with self.assertRaises(V.CandidateBaseError):
                V.read_immutable_validation_input(link, V.sha256(raw))
            hard = root / "hard.json"; os.link(path, hard)
            with self.assertRaises(V.CandidateBaseError):
                V.read_immutable_validation_input(path, V.sha256(raw))


class ActivationReceiptProjectionTests(unittest.TestCase):
    def test_receipt_binds_input_diagnostic_validator_p1r_and_public_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); candidate = "a" * 40; p1r = "c" * 40
            request = {"candidate": {"commit": candidate}, "p1_transition": {"p1r_commit": p1r}}
            raw = V.canonical_json(request); input_path = root / "input.json"; input_path.write_bytes(raw); input_path.chmod(0o444)
            observer = p1r_observer(p1r_actions_run())
            diagnostic = {
                "status": "LOCAL_NONAUTHORITATIVE_REPLAY_VERIFIED",
                "p1_transition": {"p1r_commit": p1r, "p1r_public_remote_ref": V.P1R_PUBLIC_REF},
                "validation_inputs_sha256": V.sha256(raw), "diagnostic_sha256": "d" * 64,
                "p1r_publication_observation": observer,
            }
            schema_raw = (HERE.parent / V.ACTIVATION_RECEIPT_SCHEMA_PATH).read_bytes()

            class Repo:
                def __init__(self, path: Path) -> None:
                    del path
                def blob(self, commit: str, path: str) -> bytes:
                    if path == V.P1R_PATH:
                        return b"exact p1r bytes\n"
                    if path == V.VALIDATOR_PATH:
                        return b"exact validator bytes\n"
                    if path == V.ACTIVATION_RECEIPT_SCHEMA_PATH:
                        return schema_raw
                    raise AssertionError((commit, path))

            with mock.patch.object(V, "compile_diagnostic", return_value=diagnostic), mock.patch.object(V, "GitRepository", Repo):
                receipt = V.verify_public_p1r_activation(root, input_path, V.sha256(raw), p1r)
            self.assertEqual(receipt["validation_inputs_sha256"], V.sha256(raw))
            self.assertEqual(receipt["validation_diagnostic_sha256"], "d" * 64)
            self.assertEqual(receipt["public_observation"], observer)
            self.assertEqual(receipt["p1r"]["sha256"], V.sha256(b"exact p1r bytes\n"))
            self.assertEqual(receipt["receipt_sha256"], V.activation_receipt_digest(receipt))
            changed = copy.deepcopy(receipt); changed["validation_diagnostic_sha256"] = "e" * 64
            self.assertNotEqual(changed["receipt_sha256"], V.activation_receipt_digest(changed))


class P1ReadinessEnvelopeTests(unittest.TestCase):
    def test_exact_structural_only_envelope_decodes_and_drift_rejects(self) -> None:
        package = {"schema": "fixture"}; raw = V.canonical_json(package)
        envelope = {
            "schema": "c5k4-method-v1.5-p1-embedded-readiness-package-1.0",
            "status": "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R",
            "encoding": "BASE64_CANONICAL_JSON_UTF8", "canonical_package_base64": base64.b64encode(raw).decode(),
            "package_sha256": V.sha256(raw),
            "assembler_verification_scope": "STRUCTURAL_CANONICAL_PACKAGE_ONLY_CRYPTO_UNVERIFIED_AWAITING_PUBLIC_P1R",
            "activation_authority": False,
        }
        self.assertEqual(V.decode_p1_readiness_package(envelope), (package, raw))
        changed = copy.deepcopy(envelope); changed["activation_authority"] = True
        with self.assertRaises(V.CandidateBaseError):
            V.decode_p1_readiness_package(changed)


class LegacyApiRemovalTests(unittest.TestCase):
    def test_public_minting_api_and_status_are_absent(self) -> None:
        raw = (HERE / "validate_benchmark_v15_candidate_base.py").read_text(encoding="utf-8")
        for forbidden in (
            "PUBLIC_P1_TRANSITION_AUTHENTICATED", "def compile_acceptance(", "def verify_readiness(",
            "def validate_transition(", "def write_output(", "ZERO_AUDIT",
        ):
            self.assertNotIn(forbidden, raw)
        self.assertIn('"status": "LOCAL_NONAUTHORITATIVE_REPLAY_VERIFIED"', raw)

    def test_cli_exposes_verify_only(self) -> None:
        completed = subprocess.run(
            ["python3", str(HERE / "validate_benchmark_v15_candidate_base.py"), "--help"],
            check=True, text=True, stdout=subprocess.PIPE,
        )
        self.assertIn("verify", completed.stdout)
        self.assertNotIn("compile-acceptance", completed.stdout)


if __name__ == "__main__":
    unittest.main()
