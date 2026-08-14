#!/usr/bin/env python3
"""Adversarial offline tests for the Method v1.5 C1 bridge."""

from __future__ import annotations

import copy
import base64
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


SCRIPT = Path(__file__).with_name("select_benchmark_v15.py")
SPEC = importlib.util.spec_from_file_location("select_benchmark_v15_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


def rows(extra: int = 1) -> list[dict]:
    result = []
    counter = 0
    for stratum in C.STRATA:
        for _ in range(C.QUOTAS[stratum] + extra):
            counter += 1
            result.append({"cluster_id": f"cluster-{counter:03d}", "identity_sha256": f"{counter:064x}", "stratum": stratum, "eligible": True})
    return result


def randomness(c0t: dict, c0t_commit: str, *, retrieved: str = "2026-08-20T00:01:00Z") -> dict:
    signature = "11" * 96
    value = C.sha256(bytes.fromhex(signature))
    beacon = {"round": 42, "randomness": value, "signature": signature, "previous_signature": "22" * 96}
    return {
        "schema_version": C.DRAND_SCHEMA,
        "c0_binding": {"artifact_commit": c0t["c0a_commit"], "attestation_commit": c0t_commit, "published_at_utc": c0t["publication_observation"]["github_run"]["completed_at_utc"]},
        "retrieval": {"source": "League of Entropy drand", "retrieved_at_utc": retrieved, "relays": [{"url": "https://api.drand.sh"}, {"url": "https://api2.drand.sh"}]},
        "chain": {"hash": C.CHAIN_HASH}, "round": 42, "round_closes_at_utc": "2026-08-20T00:00:00Z",
        "beacon": beacon, "beacon_canonical_sha256": C.sha256(json.dumps(beacon, sort_keys=True, separators=(",", ":")).encode()),
        "randomness": value, "randomness_sha256": C.sha256(value.encode()), "signature_sha256": C.sha256(bytes.fromhex(signature)),
        "verification": {key: True for key in ("c0_contract", "future_round", "exact_round", "official_relay_equality", "frozen_chain_info", "bls_signature", "randomness_equals_sha256_signature")},
    }


class C1BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = rows()
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.custodian_private = Ed25519PrivateKey.generate()
        self.custodian_key = self.custodian_private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        def locator(name: str, object_sha256: str) -> dict:
            return {"scheme": "S3_OBJECT_LOCK_VERSION", "bucket_arn": "arn:aws:s3:::c5k4-fixture", "object_key": f"evidence/{name}.json", "version_id": f"version-{name}", "object_sha256": object_sha256, "size_bytes": 2, "retention_until_utc": "2026-08-30T00:00:00Z"}
        evidence = {"evidence": [
            {"domain": "BROKER_CUSTODY_AND_CAPTURE_REPLAY", "artifact": locator("custody", "5" * 64), "issuer": {"verification_key_sha256": C.sha256(self.custodian_key)}},
            {"domain": "IMMUTABLE_WORM_STORE", "artifact": locator("immutable", "6" * 64)},
        ]}
        evidence_raw = C.canonical(evidence)
        evidence_envelope = {"encoding": "BASE64_CANONICAL_JSON_UTF8", "canonical_json_base64": base64.b64encode(evidence_raw).decode(), "sha256": C.sha256(evidence_raw)}
        package = {
            "authority_root": {"commit": "1" * 40, "root_tree": "2" * 40, "path": "authority.json", "sha256": "3" * 64},
            "operational_evidence": evidence_envelope,
            "authority_signatures": [{"signer_class": "CONTROLLED_HARNESS_READINESS_KEY", "verification_key_sha256": C.sha256(self.public_key)}],
        }
        package_raw = C.canonical(package)
        self.p1a = {"fixture": "p1a", "candidate_base_readiness": {"encoding": "BASE64_CANONICAL_JSON_UTF8", "canonical_package_base64": base64.b64encode(package_raw).decode(), "package_sha256": C.sha256(package_raw)}}
        self.authority_projection = C.derive_authority_projection(self.p1a)
        self.p1a_raw = C.canonical(self.p1a)
        self.pool = {"pool_sha256": "7" * 64, "clusters": self.rows, "p1_binding": {"p1a": {"sha256": C.sha256(self.p1a_raw)}, "p1r": {"path": "P1R", "sha256": "8" * 64}, "p1r_commit": "b" * 40}}
        self.c0a = {"artifact_kind": "C0A", "pass_pool": self.pool}
        self.c0a["artifact_sha256"] = C.digest(self.c0a)
        self.c0a_raw = C.canonical(self.c0a)
        self.c0t_commit = "c" * 40
        self.c0t = {
            "c0a": {"path": "results/benchmark/v1.5-protocol/C0A.json", "sha256": C.sha256(self.c0a_raw)}, "c0a_commit": "a" * 40,
            "randomness_contract": {"round": 42, "round_closes_at_utc": "2026-08-20T00:00:00Z"},
            "publication_observation": {"github_run": {"completed_at_utc": "2026-08-19T23:59:00Z"}},
            "p1_activation": {"p1r": copy.deepcopy(self.pool["p1_binding"]["p1r"]), "p1r_commit": self.pool["p1_binding"]["p1r_commit"]},
        }
        self.randomness = randomness(self.c0t, self.c0t_commit)
        self.private = {
            "schema": C.IDENTITY_SCHEMA, "status": "SEALED_PRE_C1_IDENTITY_MAP", "pool_sha256": self.pool["pool_sha256"],
            "authority_projection_sha256": self.authority_projection["projection_sha256"], "custody_binding_sha256": self.authority_projection["custody_binding_sha256"], "immutable_acceptance_sha256": self.authority_projection["immutable_acceptance_sha256"],
            "identities": [{"cluster_id": row["cluster_id"], "identity_sha256": row["identity_sha256"], "private_locator_sha256": C.sha256(("private:" + row["cluster_id"]).encode())} for row in self.rows],
        }
        self.private["artifact_sha256"] = C.private_transition_digest(self.private)
        signature = self.private_key.sign(C.PRIVATE_TRANSITION_DOMAIN + b"\0" + bytes.fromhex(self.private["artifact_sha256"]))
        self.private["signature"] = {"algorithm": "Ed25519", "key_sha256": C.sha256(self.public_key), "signature_base64": base64.b64encode(signature).decode()}
        selector_path = C.ROOT / "scripts/select_benchmark_v14.py"
        selector_spec = importlib.util.spec_from_file_location("fixture_v14_selector", selector_path)
        assert selector_spec is not None and selector_spec.loader is not None
        self.sampler = importlib.util.module_from_spec(selector_spec); selector_spec.loader.exec_module(self.sampler)
        self.sampler_ref = {"path": "scripts/select_benchmark_v14.py", "sha256": C.sha256(selector_path.read_bytes())}
        fetcher_path = C.ROOT / "tools/benchmark-drand/fetch-and-verify-v14.mjs"
        self.fetcher_ref = {"path": "tools/benchmark-drand/fetch-and-verify-v14.mjs", "sha256": C.sha256(fetcher_path.read_bytes())}

    def compile(self, *, private_raw: bytes | None = None, random: dict | None = None) -> dict:
        with mock.patch.object(C, "validate_c0t", return_value=copy.deepcopy(self.c0t)), \
             mock.patch.object(C, "validate_pool", return_value=copy.deepcopy(self.rows)), \
             mock.patch.object(C, "load_inherited_sampler", return_value=(self.sampler, self.sampler_ref, self.fetcher_ref)), \
             mock.patch.object(C, "replay_drand", return_value="9" * 64):
            return C.compile_c1a(
                self.c0a_raw, C.canonical({"fixture": "c0t"}), self.c0t_commit, self.p1a_raw,
                C.canonical(self.randomness if random is None else random),
                C.canonical(self.private) if private_raw is None else private_raw, self.public_key,
                c1a_path="results/benchmark/v1.5-protocol/C1A.json", c1t_path="results/benchmark/v1.5-protocol/C1T.json",
            )

    def test_c0_adapter_delegates_full_live_replay_without_fetch_injection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); c0a_path = root / "C0A.json"; c0t_path = root / "C0T.json"
            c0a = {"artifact_kind": "C0A"}; c0a_raw = C.canonical(c0a); c0a_path.write_bytes(c0a_raw); c0t_path.write_bytes(C.canonical({"artifact_kind": "C0T", "c0a_commit": "b" * 40}))
            validator = mock.Mock(); loader = mock.Mock(return_value=(c0a, c0a_raw, {}, b"{}\n"))
            module = type("CanonicalC0", (), {"validate_c0t": validator, "load_c0a": loader, "C0A_PATH": "C0A.json"})()
            spec = mock.Mock(); spec.loader = mock.Mock()
            with mock.patch.object(C, "ROOT", root), mock.patch.object(C.importlib.util, "spec_from_file_location", return_value=spec), mock.patch.object(C.importlib.util, "module_from_spec", return_value=module):
                observed_c0a, observed_c0t = C.authenticate_canonical_c0(c0a_path, c0t_path, "a" * 40, root / "activation.json", root / "replay.json")
            self.assertEqual(observed_c0a, c0a); self.assertEqual(observed_c0t, {"artifact_kind": "C0T", "c0a_commit": "b" * 40})
            kwargs = validator.call_args.kwargs
            self.assertNotIn("fetch", kwargs)
            self.assertEqual(kwargs["c0t_commit"], "a" * 40); self.assertEqual(kwargs["artifact_path"], c0t_path)

    def test_every_authoritative_cli_path_hits_canonical_c0_and_capture_shim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); empty = root / "empty.json"; empty.write_bytes(b"{}\n"); key = root / "key"; key.write_bytes(b"0" * 32)
            common = ["--c0a", str(empty), "--c0t", str(empty), "--p1a", str(empty), "--randomness", str(empty), "--private-transition", str(empty), "--private-transition-key", str(key), "--activation-receipt", str(empty), "--pass-pool-replay-input", str(empty), "--c0t-commit", "a" * 40]
            cases = [
                ["compile-c1a", *common, "--c1a-path", "C1A.json", "--c1t-path", "C1T.json", "--output", str(root / "out-a")],
                ["compile-c1t", "--c1a", str(empty), "--c1a-commit", "b" * 40, "--output", str(root / "out-t"), *common],
                ["compile-c1-authority", "--c1a", str(empty), "--c1a-commit", "b" * 40, "--c1t", str(empty), "--c1t-commit", "c" * 40, "--authority-private-key", str(key), "--output", str(root / "out-r"), *common],
                ["compile-envelope-freeze", "--c1a", str(empty), "--c1a-commit", "b" * 40, "--c1t", str(empty), "--c1t-commit", "c" * 40, "--c1-authority", str(empty), "--c1-authority-key", str(key), "--run-freeze-commit", "d" * 40, "--envelope-closure-commit", "e" * 40, "--matrix", str(empty), "--envelope", str(empty), "--private-custodian", str(empty), "--private-custodian-key", str(key), "--output", str(root / "out-f"), *common],
            ]
            for argv in cases:
                validator = mock.Mock(side_effect=RuntimeError("full-live-C0-replay"))
                module = type("CanonicalC0", (), {"validate_c0t": validator, "C0A_PATH": "C0A.json"})()
                spec = mock.Mock(); spec.loader = mock.Mock()
                with self.subTest(command=argv[0]), mock.patch.object(C.importlib.util, "spec_from_file_location", return_value=spec), mock.patch.object(C.importlib.util, "module_from_spec", return_value=module), mock.patch.object(sys, "argv", [str(SCRIPT), *argv]), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): C.main()
                validator.assert_called_once()
                self.assertNotIn("fetch", validator.call_args.kwargs)
                self.assertEqual(validator.call_args.kwargs["c0t_commit"], "a" * 40)
            fabricated = [*cases[0], "--github-run", str(empty), "--github-run-list", str(empty), "--github-ref", str(empty)]
            stderr = io.StringIO()
            with mock.patch.object(sys, "argv", [str(SCRIPT), *fabricated]), contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit): C.main()
            self.assertIn("unrecognized arguments", stderr.getvalue())

    def test_inherited_sampler_compiles_exact_33222_selection_nonproduction(self) -> None:
        c1a = self.compile()
        self.assertEqual(len(c1a["selected_clusters"]), 12)
        self.assertEqual({s: sum(row["stratum"] == s for row in c1a["selected_clusters"]) for s in C.STRATA}, C.QUOTAS)
        self.assertFalse(c1a["production_permitted"])
        self.assertFalse(c1a["sealed_private_identity_transition"]["private_locators_disclosed"])
        C.validate_c1a(c1a)
        c1t = C.compile_c1t(c1a, "d" * 40)
        self.assertEqual(c1t["selected_clusters"], c1a["selected_clusters"])
        self.assertFalse(c1t["production_permitted"])
        C.validate_c1t(c1t, c1a)

    def test_entropy_gate_runs_before_private_identity_decode(self) -> None:
        early = randomness(self.c0t, self.c0t_commit, retrieved="2026-08-19T23:59:59Z")
        with self.assertRaisesRegex(C.C1Error, "before the future round closed"):
            self.compile(private_raw=b"not-json-and-must-not-be-decoded", random=early)

    def test_wrong_round_relay_or_signature_fails_closed(self) -> None:
        cases = []
        wrong_round = copy.deepcopy(self.randomness); wrong_round["round"] = 43; cases.append(wrong_round)
        wrong_relay = copy.deepcopy(self.randomness); wrong_relay["retrieval"]["relays"][1]["url"] = "https://evil.invalid"; cases.append(wrong_relay)
        wrong_sig = copy.deepcopy(self.randomness); wrong_sig["beacon"]["signature"] = "33" * 96; cases.append(wrong_sig)
        for value in cases:
            with self.subTest(value=value), self.assertRaises(C.C1Error):
                C.validate_randomness(value, self.c0t, self.c0t_commit)

    def test_semantic_material_is_rejected_before_c1(self) -> None:
        for value in ({"nested": {"statement-text": "x"}}, {"rows": [{"proof_route": "x"}]}):
            with self.subTest(value=value), self.assertRaises(C.C1Error):
                C.reject_semantics(value)

    def test_private_transition_must_cover_exact_pool_without_semantics(self) -> None:
        changed = copy.deepcopy(self.private); changed["identities"].pop(); changed["artifact_sha256"] = C.private_transition_digest(changed)
        with self.assertRaises(C.C1Error):
            C.validate_private_transition(changed, self.rows, self.pool["pool_sha256"], self.public_key, self.authority_projection)
        changed = copy.deepcopy(self.private); changed["identities"][0]["statement"] = "forbidden"; changed["artifact_sha256"] = C.private_transition_digest(changed)
        with self.assertRaises(C.C1Error):
            C.validate_private_transition(changed, self.rows, self.pool["pool_sha256"], self.public_key, self.authority_projection)

    def test_c1_mutations_cannot_enable_production_or_change_quota(self) -> None:
        c1a = self.compile()
        changed = copy.deepcopy(c1a); changed["production_permitted"] = True; changed["artifact_sha256"] = C.digest(changed)
        with self.assertRaises(C.C1Error): C.validate_c1a(changed)
        changed = copy.deepcopy(c1a); changed["selected_clusters"][0]["stratum"] = C.STRATA[-1]; changed["artifact_sha256"] = C.digest(changed)
        with self.assertRaises(C.C1Error): C.validate_c1a(changed)
        changed = copy.deepcopy(c1a); changed["selected_clusters"][1]["identity_sha256"] = changed["selected_clusters"][0]["identity_sha256"]; changed["artifact_sha256"] = C.digest(changed)
        with self.assertRaises(C.C1Error): C.validate_c1a(changed)
        changed = copy.deepcopy(c1a); changed["selected_clusters"][0]["shuffle_position"] = 2; changed["artifact_sha256"] = C.digest(changed)
        with self.assertRaises(C.C1Error): C.validate_c1a(changed)

    def test_c1t_rejects_recomputed_duplicate_and_reordered_artifacts(self) -> None:
        c1a = self.compile(); c1t = C.compile_c1t(c1a, "d" * 40)
        duplicate = copy.deepcopy(c1t)
        duplicate["selected_clusters"][1]["cluster_id"] = duplicate["selected_clusters"][0]["cluster_id"]
        duplicate["selected_clusters"][1]["identity_sha256"] = duplicate["selected_clusters"][0]["identity_sha256"]
        duplicate["artifact_sha256"] = C.digest(duplicate)
        with self.assertRaisesRegex(C.C1Error, "duplicate"):
            C.validate_c1t(duplicate, c1a)
        reordered = copy.deepcopy(c1t); reordered["selected_clusters"][0], reordered["selected_clusters"][1] = reordered["selected_clusters"][1], reordered["selected_clusters"][0]
        reordered["artifact_sha256"] = C.digest(reordered)
        with self.assertRaises(C.C1Error):
            C.validate_c1t(reordered, c1a)

    def test_caller_cannot_introduce_authority_root_or_locator_hashes(self) -> None:
        attacker = Ed25519PrivateKey.generate()
        attacker_public = attacker.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        changed = copy.deepcopy(self.private)
        changed["artifact_sha256"] = C.private_transition_digest(changed)
        changed["signature"] = {"algorithm": "Ed25519", "key_sha256": C.sha256(attacker_public), "signature_base64": base64.b64encode(attacker.sign(C.PRIVATE_TRANSITION_DOMAIN + b"\0" + bytes.fromhex(changed["artifact_sha256"]))).decode()}
        with self.assertRaisesRegex(C.C1Error, "key binding"):
            C.validate_private_transition(changed, self.rows, self.pool["pool_sha256"], attacker_public, self.authority_projection)
        changed = copy.deepcopy(self.private); changed["custody_binding_sha256"] = "f" * 64
        changed["artifact_sha256"] = C.private_transition_digest(changed)
        changed["signature"] = {"algorithm": "Ed25519", "key_sha256": C.sha256(self.public_key), "signature_base64": base64.b64encode(self.private_key.sign(C.PRIVATE_TRANSITION_DOMAIN + b"\0" + bytes.fromhex(changed["artifact_sha256"]))).decode()}
        with self.assertRaisesRegex(C.C1Error, "authority projection"):
            C.validate_private_transition(changed, self.rows, self.pool["pool_sha256"], self.public_key, self.authority_projection)
        selected = self.compile()["selected_clusters"]; ids = [row["cluster_id"] for row in selected]
        receipt = {"status": "PRIVATE_CUSTODIAN_SELECTED_TARGETS_ACCEPTED", "c1t_commit": "d" * 40, "run_freeze_commit": "e" * 40, "selected_cluster_ids": ids, "selection_sha256": C.sha256(C.canonical(ids)), "ordered_selected_clusters_sha256": C.sha256(C.canonical(selected)), "authority_projection_sha256": self.authority_projection["projection_sha256"], "custody_binding_sha256": self.authority_projection["custody_binding_sha256"], "immutable_acceptance_sha256": self.authority_projection["immutable_acceptance_sha256"]}
        receipt["signature"] = {"algorithm": "Ed25519", "key_sha256": C.sha256(attacker_public), "signature_base64": base64.b64encode(attacker.sign(C.PRIVATE_CUSTODIAN_DOMAIN + b"\0" + C.canonical(receipt))).decode()}
        with self.assertRaisesRegex(C.C1Error, "signature binding"):
            C.verify_private_custodian_receipt(receipt, attacker_public, selected, "d" * 40, "e" * 40, self.authority_projection)

    def test_run_freeze_git_closure_rejects_extra_committed_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            def run(*args: str) -> str:
                return subprocess.run(["git", "-C", str(repository), *args], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
            run("init", "-q"); run("config", "user.name", "C1 Test"); run("config", "user.email", "c1@example.invalid")
            matrix = repository / "matrix.json"; matrix.write_bytes(b"matrix\n")
            run("add", matrix.name); run("commit", "-qm", "C1T"); c1t_commit = run("rev-parse", "HEAD")
            authority = repository / "authority.json"; authority.write_bytes(b"authority\n")
            run("add", authority.name); run("commit", "-qm", "run freeze"); freeze_commit = run("rev-parse", "HEAD")
            custodian = repository / "custodian.json"; custodian.write_bytes(b"custodian\n")
            envelopes = []
            for index in range(12):
                path = repository / f"envelope-{index:02d}.json"; path.write_bytes(f"{index}\n".encode()); envelopes.append(path)
            rogue = repository / "rogue.json"; rogue.write_bytes(b"not in closure\n")
            run("add", custodian.name, rogue.name, *[path.name for path in envelopes]); run("commit", "-qm", "bad closure"); closure_commit = run("rev-parse", "HEAD")
            with self.assertRaisesRegex(C.C1Error, "does not add exactly"):
                C.verify_run_freeze_git_closure(repository, c1t_commit, freeze_commit, closure_commit, authority, authority.read_bytes(), custodian, custodian.read_bytes(), envelopes, matrix)

    def test_domain_signed_c1_authority_still_cannot_authorize_production(self) -> None:
        c1a = self.compile(); c1t = C.compile_c1t(c1a, "d" * 40)
        seed = self.private_key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
        receipt = C.compile_c1_authority_receipt(c1a, c1t, "e" * 40, seed, self.authority_projection)
        key = Ed25519PrivateKey.from_private_bytes(seed).public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        C.validate_c1_authority_receipt(receipt, key, self.authority_projection)
        self.assertFalse(receipt["production_permitted"])
        changed = copy.deepcopy(receipt); changed["ordered_selected_clusters_sha256"] = "0" * 64
        with self.assertRaises(C.C1Error): C.validate_c1_authority_receipt(changed, key, self.authority_projection)

    def test_p1a_or_private_signature_swap_cannot_select(self) -> None:
        with mock.patch.object(C, "validate_c0t", return_value=copy.deepcopy(self.c0t)), \
             mock.patch.object(C, "validate_pool", return_value=copy.deepcopy(self.rows)):
            with self.assertRaisesRegex(C.C1Error, "P1A bytes"):
                C.compile_c1a(self.c0a_raw, C.canonical({"fixture": "c0t"}), self.c0t_commit, b'{"wrong":true}\n', C.canonical(self.randomness), C.canonical(self.private), self.public_key, c1a_path="a", c1t_path="b")
        changed = copy.deepcopy(self.private); changed["signature"]["signature_base64"] = base64.b64encode(b"0" * 64).decode()
        with self.assertRaisesRegex(C.C1Error, "signature"):
            C.validate_private_transition(changed, self.rows, self.pool["pool_sha256"], self.public_key, self.authority_projection)

    def test_p1a_inherited_selector_binding_is_exact(self) -> None:
        p1a = {"inherited_v1_4": {"components": {
            "selector": {**self.sampler_ref, "content_class": "INHERITED_V1_4_EXACT"},
            "drand_fetcher": {**self.fetcher_ref, "content_class": "INHERITED_V1_4_EXACT"},
        }}}
        module, observed, fetcher = C.load_inherited_sampler(p1a)
        self.assertEqual(observed, self.sampler_ref); self.assertEqual(fetcher, self.fetcher_ref); self.assertEqual(module.QUOTAS, C.QUOTAS)
        p1a["inherited_v1_4"]["components"]["selector"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(C.C1Error, "differs"):
            C.load_inherited_sampler(p1a)

    def test_twelve_envelopes_private_custodian_and_run_freeze_share_one_selection(self) -> None:
        fixture_path = C.ROOT / "scripts/test_benchmark_v15_execution_envelope.py"
        spec = importlib.util.spec_from_file_location("c1_envelope_fixture", fixture_path)
        assert spec is not None and spec.loader is not None
        fixture = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture)
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repo"; repository.mkdir()
            def run(*args: str) -> str:
                return subprocess.run(["git", "-C", str(repository), *args], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
            run("init", "-q"); run("config", "user.name", "C1 Test"); run("config", "user.email", "c1@example.invalid")
            matrix_path = repository / "matrix.json"; matrix_path.write_bytes(fixture.MATRIX_PATH.read_bytes()); matrix = json.loads(matrix_path.read_text())
            run("add", "matrix.json"); run("commit", "-qm", "C1T boundary"); c1t_commit = run("rev-parse", "HEAD")
            c1a = self.compile(); c1t = C.compile_c1t(c1a, "d" * 40)
            authority_seed = self.private_key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
            authority = C.compile_c1_authority_receipt(c1a, c1t, c1t_commit, authority_seed, self.authority_projection)
            authority_path = repository / "authority.json"; authority_path.write_bytes(C.canonical(authority))
            run("add", "authority.json"); run("commit", "-qm", "run freeze authority"); run_commit = run("rev-parse", "HEAD")
            authority_key = self.public_key; custodian_key = self.custodian_key
            ids = [row["cluster_id"] for row in c1t["selected_clusters"]]
            custodian = {"status": "PRIVATE_CUSTODIAN_SELECTED_TARGETS_ACCEPTED", "c1t_commit": c1t_commit, "run_freeze_commit": run_commit, "selected_cluster_ids": ids, "selection_sha256": C.sha256(C.canonical(ids)), "ordered_selected_clusters_sha256": C.sha256(C.canonical(c1t["selected_clusters"])), "authority_projection_sha256": self.authority_projection["projection_sha256"], "custody_binding_sha256": self.authority_projection["custody_binding_sha256"], "immutable_acceptance_sha256": self.authority_projection["immutable_acceptance_sha256"]}
            custodian["signature"] = {"algorithm": "Ed25519", "key_sha256": C.sha256(custodian_key), "signature_base64": base64.b64encode(self.custodian_private.sign(C.PRIVATE_CUSTODIAN_DOMAIN + b"\0" + C.canonical(custodian))).decode()}
            custodian_path = repository / "custodian.json"; custodian_path.write_bytes(C.canonical(custodian))
            paths = []
            for index, cluster_id in enumerate(ids):
                envelope = fixture.post_c1_envelope(matrix)
                envelope["target_execution"]["cluster_id"] = cluster_id
                envelope["target_execution"]["c1_attestation_commit"] = c1t_commit
                envelope["target_execution"]["run_freeze_commit"] = run_commit
                envelope = fixture.seal(envelope, "envelope_sha256")
                path = repository / f"envelope-{index:02d}.json"; path.write_bytes(C.canonical(envelope)); paths.append(path)
            run("add", "custodian.json", *[path.name for path in paths]); run("commit", "-qm", "envelope closure"); closure_commit = run("rev-parse", "HEAD")
            closure = C.compile_envelope_freeze(c1a, c1t, c1t_commit, authority, authority_key, self.authority_projection, run_commit, closure_commit, matrix_path, authority_path, paths, custodian, custodian_key, custodian_path, repository=repository)
            C.validate_envelope_freeze(closure); self.assertFalse(closure["production_permitted"])
            bad = copy.deepcopy(custodian); bad["selected_cluster_ids"].reverse()
            with self.assertRaises(C.C1Error):
                C.verify_private_custodian_receipt(bad, custodian_key, c1t["selected_clusters"], c1t_commit, run_commit, self.authority_projection)


if __name__ == "__main__":
    unittest.main()
