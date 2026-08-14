#!/usr/bin/env python3
"""Adversarial tests for the inert Method v1.5 controlled harness boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("method_v15_controlled_harness_service.py")
SPEC = importlib.util.spec_from_file_location("v15_harness", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
H = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)
OID = "a" * 40
TIP = "b" * 40
PROOF = "c" * 64
TICK = "2026-08-15T00:17:00Z"


class Ledger:
    def __init__(self) -> None:
        self.ticks: set[str] = set()
        self.hashes: set[str] = set()

    def reserve(self, *, scheduled_for_utc: str, request_sha256: str, workflow_run_id: str) -> bool:
        if scheduled_for_utc in self.ticks or request_sha256 in self.hashes:
            return False
        self.ticks.add(scheduled_for_utc)
        self.hashes.add(request_sha256)
        return True


class HarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = H.load_object(H.CONTRACT_PATH, "contract")
        self.contract["status"] = "FROZEN_P1_EXECUTABLE"
        self.contract["transport"] = {
            "listener_permitted": True,
            "https_endpoint": "https://harness.invalid/v1/checkpoint",
            "tls_spki_sha256": "sha256//fixture",
        }
        self.contract["oidc"]["audience_prefix"] = "c5k4-v15-checkpoint"
        self.contract["oidc"]["workflow_ref"] = "Kuberwastaken/c5-k4/.github/workflows/method-v15-checkpoint.yml@refs/heads/main"
        self.contract["binding"]["p1r_artifact_sha256"] = "e" * 64
        self.contract["binding"]["p1r_commit"] = OID
        self.contract["binding"]["p1r_activation_receipt_self_sha256"] = "f" * 64
        self.contract["binding"]["p1r_activation_sha256"] = "9" * 64
        self.contract["binding"]["activation_boundary"] = "PUBLIC_AUTHENTICATED_P1R"
        self.request = {
            "schema": "c5k4-method-v1.5-target-blind-checkpoint-request-1.0",
            "protocol_version": "1.5",
            "scheduled_for_utc": TICK,
            "mode": "CAPTURE",
            "public_chain_proof_sha256": PROOF,
            "public_tip_commit": TIP,
            "p1r_commit": OID,
            "p1r_activation_sha256": "9" * 64,
            "workflow_run_id": "123456789",
            "run_attempt": 1,
        }
        self.raw = H.canonical_json(self.request)
        self.request_sha = H.sha256(self.raw)
        self.binding = {
            "p1r_commit": OID,
            "p1r_activation_sha256": "9" * 64,
            "public_chain_proof_sha256": PROOF,
            "public_tip_commit": TIP,
            "scheduled_for_utc": TICK,
            "mode": "CAPTURE",
            "chain_terminal": False,
        }
        self.calls: list[tuple[str, str]] = []

    def verifier(self, token: str, *, issuer: str, audience: str) -> dict:
        self.calls.append((issuer, audience))
        self.assertEqual(token, "signed.jwt")
        return {
            "iss": issuer, "aud": audience,
            "repository": "Kuberwastaken/c5-k4", "ref": "refs/heads/main",
            "workflow_ref": "Kuberwastaken/c5-k4/.github/workflows/method-v15-checkpoint.yml@refs/heads/main",
            "event_name": "schedule", "run_attempt": "1", "run_id": "123456789",
        }

    def response(self, request: dict, request_sha: str) -> dict:
        return {
            "publication-manifest.json": {
                "schema": "c5k4-method-v1.5-checkpoint-publication-manifest-1.0",
                "request_sha256": request_sha,
            },
            "quota-certificate.json": {"schema": "c5k4-method-v1.5-scheduled-aggregate-certificate-1.0"},
            "receipt.json": {"schema": "c5k4-method-v1.5-chronology-receipt-1.0"},
        }

    def invoke(self, **overrides):
        values = {
            "raw_request": self.raw, "oidc_token": "signed.jwt",
            "public_binding": self.binding, "verifier": self.verifier,
            "replay_ledger": Ledger(), "executor": self.response,
            "contract": self.contract,
        }
        values.update(overrides)
        return H.verify_and_execute(**values)

    def test_committed_contract_is_nonoperational_without_listener(self) -> None:
        committed = H.load_object(H.CONTRACT_PATH, "contract")
        H.validate_contract(committed, require_operational=False)
        self.assertEqual(committed["status"], "PRE_P1_NONOPERATIONAL_NO_LISTENER")
        self.assertFalse(committed["transport"]["listener_permitted"])
        with self.assertRaisesRegex(H.HarnessError, "PRE_P1"):
            H.verify_and_execute(
                raw_request=self.raw, oidc_token="signed.jwt", public_binding=self.binding,
                verifier=self.verifier, replay_ledger=Ledger(), executor=self.response,
            )

    def test_valid_request_uses_injected_jwks_verifier_and_returns_exact_triplet(self) -> None:
        raw = self.invoke()
        value = json.loads(raw)
        self.assertEqual(sorted(value), sorted(H.PUBLIC_FILES))
        self.assertEqual(value["publication-manifest.json"]["request_sha256"], self.request_sha)
        self.assertEqual(self.calls, [(
            "https://token.actions.githubusercontent.com",
            "c5k4-v15-checkpoint:" + self.request_sha,
        )])

    def test_noncanonical_or_oversize_request_is_rejected_before_oidc(self) -> None:
        with self.assertRaisesRegex(H.HarnessError, "canonical"):
            self.invoke(raw_request=json.dumps(self.request, indent=2).encode())
        with self.assertRaisesRegex(H.HarnessError, "size"):
            self.invoke(raw_request=b"x" * 8193)
        self.assertEqual(self.calls, [])

    def test_extra_field_and_unknown_mode_are_rejected(self) -> None:
        value = dict(self.request); value["target_identity"] = "secret"
        with self.assertRaisesRegex(H.HarnessError, "exact schema"):
            self.invoke(raw_request=H.canonical_json(value))
        value = dict(self.request); value["mode"] = "OTHER"
        with self.assertRaisesRegex(H.HarnessError, "exact schema"):
            self.invoke(raw_request=H.canonical_json(value))

    def test_every_required_oidc_claim_is_exact(self) -> None:
        for key in ("iss", "aud", "repository", "ref", "workflow_ref", "event_name", "run_attempt", "run_id"):
            def wrong(token, *, issuer, audience, changed=key):
                claims = self.verifier(token, issuer=issuer, audience=audience)
                claims[changed] = "wrong"
                return claims
            with self.subTest(key=key), self.assertRaisesRegex(H.HarnessError, key):
                self.invoke(verifier=wrong)

    def test_signature_failure_is_fail_closed(self) -> None:
        def bad_verifier(token, *, issuer, audience):
            raise RuntimeError("JWKS reject")
        with self.assertRaisesRegex(H.HarnessError, "signature/JWKS"):
            self.invoke(verifier=bad_verifier)

    def test_p1_chain_tip_proof_tick_and_mode_are_exact(self) -> None:
        for key in ("p1r_commit", "p1r_activation_sha256", "public_chain_proof_sha256", "public_tip_commit", "scheduled_for_utc", "mode"):
            binding = dict(self.binding)
            binding[key] = ("d" * 40 if "commit" in key else "wrong")
            with self.subTest(key=key), self.assertRaisesRegex(H.HarnessError, key):
                self.invoke(public_binding=binding)

    def test_operational_contract_requires_full_authenticated_p1r_receipt(self) -> None:
        for key in ("p1r_artifact_sha256", "p1r_commit", "p1r_activation_receipt_self_sha256", "p1r_activation_sha256", "activation_boundary"):
            contract = copy.deepcopy(self.contract)
            contract["binding"][key] = None
            with self.subTest(key=key), self.assertRaises(H.HarnessError):
                H.validate_contract(contract, require_operational=True)
        request = copy.deepcopy(self.request)
        request["p1r_activation_sha256"] = "8" * 64
        with self.assertRaisesRegex(H.HarnessError, "full authenticated P1R"):
            self.invoke(
                raw_request=H.canonical_json(request),
                public_binding={**self.binding, "p1r_activation_sha256": "8" * 64},
            )
        binding = dict(self.binding); binding["chain_terminal"] = True
        with self.assertRaisesRegex(H.HarnessError, "already terminal"):
            self.invoke(public_binding=binding)

    def test_duplicate_request_and_distinct_request_for_same_tick_are_rejected(self) -> None:
        ledger = Ledger()
        self.invoke(replay_ledger=ledger)
        with self.assertRaisesRegex(H.HarnessError, "duplicate"):
            self.invoke(replay_ledger=ledger)
        changed = dict(self.request); changed["workflow_run_id"] = "987654321"
        raw = H.canonical_json(changed)
        def changed_verifier(token, *, issuer, audience):
            claims = self.verifier(token, issuer=issuer, audience=audience)
            claims["run_id"] = "987654321"
            return claims
        with self.assertRaisesRegex(H.HarnessError, "duplicate"):
            self.invoke(raw_request=raw, replay_ledger=ledger, verifier=changed_verifier)

    def test_failed_execution_consumes_tick_without_rollback(self) -> None:
        ledger = Ledger()
        def fail(request, request_sha):
            raise RuntimeError("executor failure")
        with self.assertRaisesRegex(RuntimeError, "executor failure"):
            self.invoke(replay_ledger=ledger, executor=fail)
        with self.assertRaisesRegex(H.HarnessError, "duplicate"):
            self.invoke(replay_ledger=ledger)

    def test_response_must_be_exact_bounded_target_blind_and_request_bound(self) -> None:
        extra = self.response(self.request, self.request_sha); extra["debug.json"] = {}
        with self.assertRaisesRegex(H.HarnessError, "exact bounded"):
            self.invoke(executor=lambda *_: extra)
        leaked = self.response(self.request, self.request_sha); leaked["receipt.json"]["cluster_id"] = "secret"
        with self.assertRaisesRegex(H.HarnessError, "target-bearing"):
            self.invoke(executor=lambda *_: leaked)
        unbound = self.response(self.request, "0" * 64)
        with self.assertRaisesRegex(H.HarnessError, "not bound"):
            self.invoke(executor=lambda *_: unbound)
        huge = self.response(self.request, self.request_sha); huge["receipt.json"]["padding"] = "x" * 1048576
        with self.assertRaisesRegex(H.HarnessError, "size"):
            self.invoke(executor=lambda *_: huge)

    def test_terminal_gap_is_the_only_other_mode(self) -> None:
        request = dict(self.request); request["mode"] = "TERMINAL_CHRONOLOGY_GAP"
        binding = dict(self.binding); binding["mode"] = "TERMINAL_CHRONOLOGY_GAP"
        raw = H.canonical_json(request)
        output = self.invoke(raw_request=raw, public_binding=binding)
        self.assertEqual(sorted(json.loads(output)), sorted(H.PUBLIC_FILES))


if __name__ == "__main__":
    unittest.main()
