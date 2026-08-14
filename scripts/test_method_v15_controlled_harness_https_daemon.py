#!/usr/bin/env python3
"""Offline fixture tests for the Method v1.5 HTTPS daemon adapter."""

from __future__ import annotations

import copy
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("method_v15_controlled_harness_https_daemon.py")
SPEC = importlib.util.spec_from_file_location("v15_https_daemon", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)
OID = "a" * 40
TIP = "b" * 40
PROOF = "c" * 64


class MemoryLedger:
    def __init__(self) -> None:
        self.ticks: set[str] = set()
        self.hashes: set[str] = set()

    def reserve(self, *, scheduled_for_utc: str, request_sha256: str, workflow_run_id: str) -> bool:
        if scheduled_for_utc in self.ticks or request_sha256 in self.hashes:
            return False
        self.ticks.add(scheduled_for_utc); self.hashes.add(request_sha256)
        return True


class FixtureProviders:
    def __init__(self, owner: "DaemonTests") -> None:
        self.owner = owner
        self.binding_calls = 0

    def public_binding(self, *, raw_request: bytes, request_sha256: str) -> dict:
        self.binding_calls += 1
        request = json.loads(raw_request)
        return {
            "p1r_commit": request["p1r_commit"],
            "p1r_activation_sha256": request["p1r_activation_sha256"],
            "public_chain_proof_sha256": request["public_chain_proof_sha256"],
            "public_tip_commit": request["public_tip_commit"],
            "scheduled_for_utc": request["scheduled_for_utc"],
            "mode": request["mode"],
            "chain_terminal": False,
        }

    def verifier(self, token: str, *, issuer: str, audience: str) -> dict:
        self.owner.audiences.append(audience)
        request = self.owner.requests_by_digest[audience.rsplit(":", 1)[-1]]
        return {
            "iss": issuer, "aud": audience, "repository": "Kuberwastaken/c5-k4",
            "ref": "refs/heads/main", "workflow_ref": self.owner.workflow_ref,
            "event_name": "schedule", "run_attempt": "1", "run_id": request["workflow_run_id"],
        }

    def executor(self, request: dict, request_sha256: str) -> dict:
        return {
            "publication-manifest.json": {"schema": "c5k4-method-v1.5-checkpoint-publication-manifest-1.0", "request_sha256": request_sha256},
            "quota-certificate.json": {"schema": "c5k4-method-v1.5-scheduled-aggregate-certificate-1.0"},
            "receipt.json": {"schema": "c5k4-method-v1.5-chronology-receipt-1.0"},
        }


class DaemonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow_ref = "Kuberwastaken/c5-k4/.github/workflows/method-v15-checkpoint.yml@refs/heads/main"
        self.daemon = D.load_contract()
        self.daemon["status"] = "FROZEN_P1_EXECUTABLE"
        self.daemon["transport"].update({"listener_permitted": True, "https_endpoint": "https://harness.invalid:443/v1/checkpoint", "bind_address": "127.0.0.1"})
        self.service = D.SERVICE.load_object(D.SERVICE.CONTRACT_PATH, "contract")
        self.service["transport"]["tls_spki_sha256"] = "sha256//fixture"
        self.service["oidc"]["workflow_ref"] = self.workflow_ref
        self.service["binding"]["p1r_artifact_sha256"] = "e" * 64
        self.service["binding"]["p1r_commit"] = OID
        self.service["binding"]["p1r_activation_receipt_self_sha256"] = "f" * 64
        self.service["binding"]["p1r_activation_sha256"] = "9" * 64
        self.service["binding"]["activation_boundary"] = "PUBLIC_AUTHENTICATED_P1R"
        self.audiences: list[str] = []
        self.requests_by_digest: dict[str, dict] = {}
        self.providers = FixtureProviders(self)
        self.adapter = D.HTTPSAdapter(daemon_contract=self.daemon, service_contract=self.service, providers=self.providers, replay_ledger=MemoryLedger())

    def p1r_fixture(self, root: Path) -> tuple[dict, Path]:
        value = {
            "schema_version": "c5k4-method-v1.5-p1r-1.0", "artifact_kind": "P1R",
            "status": "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY", "protocol_version": "1.5",
            "p1t": {"path": "results/benchmark/v1.5-protocol/P1T.json", "sha256": "d" * 64},
            "p1t_commit": "b" * 40,
            "observation": {
                "public_remote_url": "https://github.com/Kuberwastaken/c5-k4",
                "authority_root": {"ref": "refs/tags/method-v1.5-a0", "commit": "1" * 40},
                "v1_4_p0t": {"ref": "refs/tags/method-v1.4-p0t", "commit": "2" * 40},
                "candidate_c": {"ref": "refs/tags/method-v1.5-c", "commit": "3" * 40},
                "p1t": {"ref": "refs/heads/method-v1.5-p1", "commit": "b" * 40},
                "observed_at_utc": "2026-08-15T00:00:00Z", "ls_remote_stdout_sha256": "e" * 64,
                "observer": {
                    "workflow_repository": "Kuberwastaken/c5-k4",
                    "workflow_path": ".github/workflows/method-v15-p1t-publication-observer.yml",
                    "workflow_ref": ".github/workflows/method-v15-p1t-publication-observer.yml@refs/heads/main",
                    "workflow_blob_sha256": "f" * 64, "run_id": 1, "run_attempt": 1,
                    "actions_run_projection_sha256": "9" * 64,
                },
            },
            "activation_policy": {
                "structural_draft_only": True, "p1r_is_activation_boundary": False,
                "p1t_alone_is_activation_boundary": False, "full_exact_c_replay_required": True,
                "p1r_parent_must_be_exact_p1t": True,
                "allowed_p1r_changed_paths": ["results/benchmark/v1.5-protocol/P1R.json"],
                "public_p1r_ref_required": True,
            },
        }
        path = root / "P1R.json"; path.write_bytes(D.canonical_json(value))
        checkout_root = root / "checkout"
        checkout_path = checkout_root / "results/benchmark/v1.5-protocol/P1R.json"
        checkout_path.parent.mkdir(parents=True); checkout_path.write_bytes(path.read_bytes())
        activation = {
            "p1": {"tree_path": str(checkout_root), "checkout_commit": OID},
            "p1r_activation": {
                "installed_artifact_path": str(path),
                "receipt": {
                    "schema": "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
                    "p1r": {"path": "results/benchmark/v1.5-protocol/P1R.json", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
                    "p1r_commit": OID, "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
                    "public_observation": {
                        "workflow_repository": "Kuberwastaken/c5-k4",
                        "workflow_path": ".github/workflows/method-v15-p1r-publication-observer.yml",
                        "workflow_blob_sha256": "4" * 64,
                        "workflow_ref": ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r",
                        "run_id": 2, "run_attempt": 1, "server_observed_at_utc": "2026-08-15T01:00:00Z",
                        "actions_run_projection_sha256": "5" * 64,
                    },
                    "validation_inputs_sha256": "6" * 64, "validation_diagnostic_sha256": "7" * 64,
                    "validator": {"path": "scripts/validate_benchmark_v15_candidate_base.py", "sha256": "8" * 64},
                    "receipt_sha256": "0" * 64,
                },
            },
        }
        receipt = activation["p1r_activation"]["receipt"]
        receipt["receipt_sha256"] = hashlib.sha256(
            D.P1R_RECEIPT_DOMAIN + b"\0" + D.canonical_json({key: item for key, item in receipt.items() if key != "receipt_sha256"})
        ).hexdigest()
        return activation, path

    def request(self, *, tick: str = "2026-08-15T00:17:00Z", run_id: str = "123456789") -> tuple[dict, bytes, str]:
        value = {
            "schema": "c5k4-method-v1.5-target-blind-checkpoint-request-1.0", "protocol_version": "1.5",
            "scheduled_for_utc": tick, "mode": "CAPTURE", "public_chain_proof_sha256": PROOF,
            "public_tip_commit": TIP, "p1r_commit": OID, "workflow_run_id": run_id, "run_attempt": 1,
            "p1r_activation_sha256": "9" * 64,
        }
        raw = D.SERVICE.canonical_json(value)
        digest = D.SERVICE.sha256(raw)
        self.requests_by_digest[digest] = value
        return value, raw, digest

    def invoke(self, *, method: str = "POST", path: str = "/v1/checkpoint", raw: bytes | None = None, digest: str | None = None, extra_headers=(), content_type: str = "application/json", token: str = "signed.jwt"):
        if raw is None:
            _, raw, actual_digest = self.request()
            if digest is None:
                digest = actual_digest
        elif digest is None:
            digest = D.SERVICE.sha256(raw)
        headers = [
            ("Content-Type", content_type), ("Content-Length", str(len(raw))),
            ("X-C5K4-Request-SHA256", digest), ("Authorization", "Bearer " + token), *extra_headers,
        ]
        return self.adapter.handle(method=method, path=path, headers=headers, body=raw)

    def test_committed_contract_is_pre_p1_and_cli_never_listens(self) -> None:
        committed = D.load_contract()
        self.assertEqual(committed["status"], "PRE_P1_NONOPERATIONAL_NO_LISTENER")
        self.assertFalse(committed["transport"]["listener_permitted"])
        self.assertEqual(D.main([]), 2)
        self.assertEqual(D.main(["--check-config"]), 0)

    def test_forged_frozen_contract_cannot_import_provider_create_replay_or_bind(self) -> None:
        forged = copy.deepcopy(self.daemon)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract = root / "forged.json"
            contract.write_bytes(D.canonical_json(forged))
            replay_parent = root / "state"
            forged["paths"]["replay_ledger"] = str(replay_parent / "replay.sqlite3")
            with (
                mock.patch.object(D, "load_providers") as load_providers,
                mock.patch.object(D, "serve") as serve,
                mock.patch.object(D, "SQLiteReplayLedger") as ledger,
            ):
                self.assertEqual(D.main(["--contract", str(contract)]), 2)
            load_providers.assert_not_called()
            serve.assert_not_called()
            ledger.assert_not_called()
            self.assertFalse(replay_parent.exists())

    def test_unauthenticated_activation_fails_before_provider_or_replay_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            activation = root / "activation.json"
            activation.write_bytes(D.canonical_json({"activation_inputs_sha256": "0" * 64}))
            replay_parent = root / "state"
            with (
                mock.patch.object(D, "load_providers") as load_providers,
                mock.patch.object(D, "serve") as serve,
                mock.patch.object(D, "SQLiteReplayLedger") as ledger,
            ):
                status = D.main([
                    "--activation-binding", str(activation),
                    "--expected-binding-sha256", "0" * 64,
                    "--daemon-contract", str(root / "daemon-contract.json"),
                    "--control-socket", str(root / "control.sock"),
                    "--tls-certificate", str(root / "certificate.pem"),
                    "--tls-private-key", str(root / "private-key.pem"),
                ])
            self.assertEqual(status, 2)
            load_providers.assert_not_called()
            serve.assert_not_called()
            ledger.assert_not_called()
            self.assertFalse(replay_parent.exists())

    def test_p1r_activation_requires_exact_artifact_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            activation, path = self.p1r_fixture(Path(directory))
            value, receipt_sha = D.authenticate_p1r_artifact(activation)
            self.assertEqual(value["artifact_kind"], "P1R")
            self.assertEqual(receipt_sha, activation["p1r_activation"]["receipt"]["receipt_sha256"])
            for label, mutate in (
                ("digest", lambda item: item["p1r_activation"]["receipt"]["p1r"].__setitem__("sha256", "0" * 64)),
                ("boundary", lambda item: item["p1r_activation"]["receipt"].__setitem__("activation_boundary", "P1T")),
            ):
                forged = copy.deepcopy(activation); mutate(forged)
                with self.subTest(label=label), self.assertRaises(D.DaemonError):
                    D.authenticate_p1r_artifact(forged)
            wrong_checkout = copy.deepcopy(activation)
            wrong_checkout["p1"]["checkout_commit"] = "b" * 40
            with self.assertRaisesRegex(D.DaemonError, "checkout"):
                D.authenticate_p1r_artifact(wrong_checkout)
            path.write_bytes(b"{}\n")
            with self.assertRaisesRegex(D.DaemonError, "digest mismatch"):
                D.authenticate_p1r_artifact(activation)

    def test_canonical_paths_path_tls_and_audience_are_exact(self) -> None:
        committed = D.load_contract()
        self.assertEqual(committed["identity"]["service"], "c5k4-benchmark-v15")
        self.assertEqual(committed["paths"]["p1"], "/opt/c5k4-benchmark-v15/p1")
        self.assertEqual(committed["paths"]["credentials"], "/etc/c5k4-benchmark-v15/credentials")
        self.assertEqual(committed["paths"]["daemon_contract"], "/etc/c5k4-benchmark-v15/credentials/https-daemon-contract.json")
        self.assertEqual(committed["paths"]["provider_module"], "/opt/c5k4-benchmark-v15/p1/bin/c5k4_harness_providers.py")
        self.assertEqual(committed["paths"]["control_socket"], "/run/c5k4-benchmark-v15/control.sock")
        self.assertEqual(committed["transport"]["path"], "/v1/checkpoint")
        self.assertEqual(committed["transport"]["tls_version"], "TLSv1.3_ONLY")
        self.assertEqual(committed["oidc"]["audience_prefix"], "c5k4-method-v1.5")
        context = mock.Mock()
        with mock.patch.object(D.ssl, "SSLContext", return_value=context):
            built = D.tls13_context(Path("certificate.pem"), Path("private-key.pem"))
        self.assertIs(built, context)
        self.assertEqual(context.minimum_version, D.ssl.TLSVersion.TLSv1_3)
        self.assertEqual(context.maximum_version, D.ssl.TLSVersion.TLSv1_3)

    def test_spki_pin_is_curl_base64_der_digest_and_rejects_key_mismatch(self) -> None:
        public_pem = b"fixture public PEM"
        public_der = b"fixture DER SubjectPublicKeyInfo"
        with mock.patch.object(D, "openssl", side_effect=[public_pem, public_der, public_der, b"hostname ok"]):
            pin = D.derive_tls_spki(Path("certificate.pem"), Path("private-key.pem"), "https://harness.invalid:443/v1/checkpoint")
        expected = "sha256//" + base64.b64encode(hashlib.sha256(public_der).digest()).decode("ascii")
        self.assertEqual(pin, expected)
        self.assertNotEqual(pin, "sha256//" + hashlib.sha256(public_der).hexdigest())
        with mock.patch.object(D, "openssl", side_effect=[public_pem, public_der, b"different DER"]):
            with self.assertRaisesRegex(D.DaemonError, "does not match"):
                D.derive_tls_spki(Path("certificate.pem"), Path("private-key.pem"), "https://harness.invalid:443/v1/checkpoint")
        with mock.patch.object(D, "openssl", side_effect=[public_pem, public_der, public_der, D.DaemonError("hostname rejected")]):
            with self.assertRaisesRegex(D.DaemonError, "hostname rejected"):
                D.derive_tls_spki(Path("certificate.pem"), Path("private-key.pem"), "https://wrong.invalid:443/v1/checkpoint")

    def test_success_composes_existing_verifier_and_returns_exact_three_files(self) -> None:
        _, raw, digest = self.request()
        status, headers, body = self.invoke(raw=raw, digest=digest)
        self.assertEqual(status, 200)
        self.assertEqual(dict(headers)["Content-Type"], "application/json")
        self.assertEqual(sorted(json.loads(body)), sorted(D.SERVICE.PUBLIC_FILES))
        self.assertEqual(self.audiences, ["c5k4-method-v1.5:" + digest])

    def test_transport_rejects_wrong_method_path_type_size_hash_or_bearer_silently(self) -> None:
        cases = [
            {"method": "GET"}, {"path": "/"}, {"path": "/v1/checkpoint/"},
            {"content_type": "application/json; charset=utf-8"}, {"digest": "0" * 64}, {"token": ""},
        ]
        for values in cases:
            with self.subTest(values=values):
                status, headers, body = self.invoke(**values)
                self.assertNotEqual(status, 200)
                self.assertEqual(body, b"")
                self.assertEqual(dict(headers)["Content-Length"], "0")
        status, _, body = self.invoke(raw=b"x" * 8193, digest=D.SERVICE.sha256(b"x" * 8193))
        self.assertEqual((status, body), (413, b""))

    def test_duplicate_security_headers_fail_before_provider(self) -> None:
        status, _, body = self.invoke(extra_headers=(("Authorization", "Bearer other.jwt"),))
        self.assertEqual((status, body), (401, b""))
        self.assertEqual(self.providers.binding_calls, 0)

    def test_legacy_audience_prefix_and_root_endpoint_are_not_accepted(self) -> None:
        legacy = copy.deepcopy(self.daemon); legacy["oidc"]["audience_prefix"] = "c5k4-v15-checkpoint"
        with self.assertRaisesRegex(D.DaemonError, "audience"):
            D.HTTPSAdapter(daemon_contract=legacy, service_contract=self.service, providers=self.providers, replay_ledger=MemoryLedger())
        legacy = copy.deepcopy(self.daemon); legacy["transport"]["path"] = "/"
        with self.assertRaisesRegex(D.DaemonError, "path"):
            D.HTTPSAdapter(daemon_contract=legacy, service_contract=self.service, providers=self.providers, replay_ledger=MemoryLedger())

    def test_sqlite_replay_reservation_survives_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.sqlite3"
            first = D.SQLiteReplayLedger(path)
            self.assertTrue(first.reserve(scheduled_for_utc="tick", request_sha256="a" * 64, workflow_run_id="1"))
            second = D.SQLiteReplayLedger(path)
            self.assertFalse(second.reserve(scheduled_for_utc="tick", request_sha256="b" * 64, workflow_run_id="2"))
            self.assertFalse(second.reserve(scheduled_for_utc="other", request_sha256="a" * 64, workflow_run_id="2"))

    def test_adapter_serializes_requests_one_at_a_time(self) -> None:
        active = 0
        maximum = 0
        guard = threading.Lock()
        original = self.providers.public_binding
        def slow_binding(**values):
            nonlocal active, maximum
            with guard:
                active += 1; maximum = max(maximum, active)
            time.sleep(0.03)
            try:
                return original(**values)
            finally:
                with guard:
                    active -= 1
        self.providers.public_binding = slow_binding  # type: ignore[method-assign]
        requests = [self.request(tick=f"2026-0{month}-15T00:17:00Z", run_id=str(month)) for month in (8, 9)]
        statuses: list[int] = []
        threads = [threading.Thread(target=lambda raw=raw, digest=digest: statuses.append(self.invoke(raw=raw, digest=digest)[0])) for _, raw, digest in requests]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(sorted(statuses), [200, 200])
        self.assertEqual(maximum, 1)


if __name__ == "__main__":
    unittest.main()
