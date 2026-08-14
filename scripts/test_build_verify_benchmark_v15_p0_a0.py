#!/usr/bin/env python3
"""Adversarial tests for the repository-only Method v1.5 P0/A0 chain."""

from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parent.parent


def module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


BUILD = module("p0_a0_build", "scripts/build_benchmark_v15_p0_a0.py")
VERIFY = module("p0_a0_verify", "scripts/verify_benchmark_v15_p0_a0_publication.py")


class ChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(); self.repo = Path(self.tmp.name)
        self.git("init", "-q", "-b", "method-v1.5-p0")
        self.git("config", "user.name", "P0 Test"); self.git("config", "user.email", "p0@example.invalid")
        for required in BUILD.REQUIRED_COMPONENTS:
            if required.endswith(".json"):
                self.write_raw(required, b"{}\n")
            else:
                self.write_raw(required, b"frozen target-blind component\n")
        self.git("add", "-A"); self.git("commit", "-qm", "protocol base")
        self.base = self.git("rev-parse", "HEAD")
        self.private_keys = [Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()]
        self.authorities = []
        for index, key in enumerate(self.private_keys, 1):
            raw = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            self.authorities.append({
                "authority_id": f"independent-{index}", "verification_key_sha256": hashlib.sha256(raw).hexdigest(),
                "key_origin": "EXTERNAL_PUBLIC_KEY_HASH_FROZEN_BEFORE_P0A",
            })
        roster = {"required_independent_signature_count": 2, "independent_authorities": self.authorities}
        self.policy = {
            **roster,
            "authority_roster_sha256": BUILD.domain_digest("c5k4-method-v1.5-a0-authority-roster-1.0", roster),
            "attestable_ami_authority_binding_policy_sha256": BUILD.domain_digest(
                "c5k4-method-v1.5-attestable-ami-authority-binding-policy-template-1.0",
                [BUILD.blob_binding(self.repo, self.base, path) for path in BUILD.AMI_POLICY_COMPONENTS],
            ),
            "harness_key_policy": {
                "algorithm": "Ed25519", "storage": "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY",
                "verification_key_hash_known_at_p0a": False, "raw_private_key_egress_permitted": False,
            },
        }
        self.component_paths = sorted(BUILD.REQUIRED_COMPONENTS)
        self.p0a = BUILD.build_p0a(self.repo, self.base, {"component_paths": self.component_paths}, self.policy)
        self.write(BUILD.P0A_PATH, self.p0a); self.commit_only(BUILD.P0A_PATH, "P0A"); self.p0a_commit = self.git("rev-parse", "HEAD")
        p0a_fetch = self.api_fetch("P0A", self.p0a_commit, 41)
        self.p0a_receipt = VERIFY.compile_actions_observation(self.repo, kind="P0A", commit=self.p0a_commit, run_id=41, fetch=p0a_fetch)
        self.p0t = BUILD.build_p0t(
            self.repo, self.p0a_commit, self.p0a_receipt,
            observation_verifier=lambda repo, artifact, kind, commit: VERIFY.replay_actions_observation(repo, artifact, kind=kind, commit=commit, fetch=p0a_fetch),
        )
        self.write(BUILD.P0T_PATH, self.p0t); self.commit_only(BUILD.P0T_PATH, "P0T"); self.p0t_commit = self.git("rev-parse", "HEAD")
        p0t_fetch = self.api_fetch("P0T", self.p0t_commit, 42)
        self.p0t_receipt = VERIFY.compile_actions_observation(self.repo, kind="P0T", commit=self.p0t_commit, run_id=42, fetch=p0t_fetch)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

    def write_raw(self, path: str, raw: bytes) -> None:
        destination = self.repo / path; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(raw)

    def write(self, path: str, value: dict) -> None:
        self.write_raw(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())

    def commit_only(self, path: str, message: str) -> None:
        self.git("add", path); self.git("commit", "-qm", message)

    @staticmethod
    def accept_observation(repo: Path, receipt: dict, kind: str, commit: str) -> None:
        return None

    def receipt(self, kind: str, path: str, commit: str) -> dict:
        raw = (self.repo / path).read_bytes()
        run_id = 41 if kind == "P0A" else 42
        minute = 0 if kind == "P0A" else 2
        actions = {
                "repository": "Kuberwastaken/c5-k4", "repository_id": 1331829034, "api_version": "2022-11-28",
                "workflow_path": ".github/workflows/method-v15-p0-publication-observer.yml",
                "workflow_commit": commit,
                "workflow_blob_sha256": hashlib.sha256(self.git_bytes("show", f"{commit}:.github/workflows/method-v15-p0-publication-observer.yml")).hexdigest(),
                "event": "push", "branch": "method-v1.5-p0", "ref": "refs/heads/method-v1.5-p0", "head_sha": commit,
                "run_id": run_id, "run_attempt": 1, "status": "completed", "conclusion": "success",
                "created_at_utc": f"2026-08-14T01:0{minute}:00Z", "run_started_at_utc": f"2026-08-14T01:0{minute}:10Z", "updated_at_utc": f"2026-08-14T01:0{minute + 1}:00Z",
                "captured_run_object_sha256": "a" * 64, "captured_listing_sha256": "b" * 64, "captured_ref_sha256": "c" * 64,
                "api_projection_sha256": "0" * 64,
        }
        unsigned = dict(actions); unsigned.pop("api_projection_sha256"); unsigned.pop("captured_ref_sha256")
        actions["api_projection_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", unsigned)
        value = {
            "schema": "c5k4-method-v1.5-p0-publication-receipt-1.0",
            "source": "LIVE_GITHUB_SERVER_ACTIONS_REPLAY",
            "subject": {"artifact_kind": kind, "path": path, "commit": commit, "sha256": hashlib.sha256(raw).hexdigest()},
            "actions_run": actions,
            "capture": {"authenticated_by": "scripts/verify_benchmark_v15_p0_a0_publication.py", "network_fetch_performed_by_builder": True, "credentials_embedded": False, "raw_api_response_published": False, "server_observation_claim_requires_independent_validation": True, "live_replay_required_by_builder": True},
            "receipt_sha256": "0" * 64,
        }
        value["receipt_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", value, "receipt_sha256")
        return value

    def git_bytes(self, *args: str) -> bytes:
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, stdout=subprocess.PIPE).stdout

    def api_fetch(self, kind: str, commit: str, run_id: int, *, run_mutation=None, duplicate: bool = False):
        run_url, listing_url, ref_url = VERIFY._api_urls(run_id, commit)
        minute = {"P0A": 0, "P0T": 2, "A0": 4}[kind]
        run = {
            "id": run_id, "run_attempt": 1, "event": "push", "status": "completed", "conclusion": "success",
            "head_sha": commit, "head_branch": "method-v1.5-p0", "url": run_url,
            "html_url": f"https://github.com/Kuberwastaken/c5-k4/actions/runs/{run_id}",
            "path": ".github/workflows/method-v15-p0-publication-observer.yml@refs/heads/method-v1.5-p0",
            "created_at": f"2026-08-14T01:0{minute}:00Z", "run_started_at": f"2026-08-14T01:0{minute}:10Z", "updated_at": f"2026-08-14T01:0{minute + 1}:00Z",
            "repository": {"id": 1331829034, "full_name": "Kuberwastaken/c5-k4"},
        }
        if run_mutation is not None:
            run_mutation(run)
        selected = {key: run.get(key) for key in ("id", "run_attempt", "event", "status", "conclusion", "head_sha", "head_branch")}
        listing_runs = [selected, copy.deepcopy(selected)] if duplicate else [selected]
        listing = {"total_count": len(listing_runs), "workflow_runs": listing_runs}
        ref = {"ref": "refs/heads/method-v1.5-p0", "object": {"type": "commit", "sha": self.git("rev-parse", "HEAD")}}
        responses = {run_url: json.dumps(run, sort_keys=True).encode(), listing_url: json.dumps(listing, sort_keys=True).encode(), ref_url: json.dumps(ref, sort_keys=True).encode()}
        return lambda url: responses[url]

    @staticmethod
    def combined_fetch(*fetchers):
        def fetch(url: str) -> bytes:
            for candidate in fetchers:
                try:
                    return candidate(url)
                except KeyError:
                    continue
            raise KeyError(url)
        return fetch

    def identity_fetch(self, a0_commit: str, a0_run_id: int, *, a0_mutation=None):
        return self.combined_fetch(
            self.api_fetch("P0A", self.p0a_commit, 41),
            self.api_fetch("P0T", self.p0t_commit, 42),
            self.api_fetch("A0", a0_commit, a0_run_id, run_mutation=a0_mutation),
        )

    def commit_a0(self, value: dict, message: str = "A0") -> str:
        self.write(BUILD.A0_PATH, value); self.commit_only(BUILD.A0_PATH, message)
        return self.git("rev-parse", "HEAD")

    def authoritative_a0(self, harness_hash: str = "d" * 64) -> tuple[dict, Path]:
        value = BUILD.build_a0_draft(self.repo, self.p0t_commit, self.p0t_receipt, observation_verifier=self.accept_observation)
        value["status"] = "EXTERNALLY_AUTHORIZED_A0"
        value["a0_authorized_at_utc"] = "2026-08-14T01:03:30Z"
        value["external_harness_authority"] = {
            "algorithm": "Ed25519", "key_policy": "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY",
            "verification_key_sha256": harness_hash, "nitrotpm_key_generation_attestation_sha256": "e" * 64,
            "attestable_ami_authority_binding_policy_sha256": self.policy["attestable_ami_authority_binding_policy_sha256"],
            "generated_externally": True, "raw_private_key_published": False,
        }
        value["activation_policy"] = {
            "activation_authority": True, "fail_closed": True,
            "nitrotpm_sealed_verification_key_hash_present": True,
            "required_independent_signatures_present": True,
            "external_activation_ceremony_required": True, "repository_builder_can_activate": False,
            "local_preview_only": False, "publication_permitted": True,
        }
        value["independent_authority_signatures"] = []
        value["a0_payload_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-a0-activation-payload-1.0", VERIFY._payload(value))
        message = b"c5k4-method-v1.5-a0-authority-signature-1.0\x00" + bytes.fromhex(value["a0_payload_sha256"])
        key_rows = []
        for authority, private in zip(self.authorities, self.private_keys):
            public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
            value["independent_authority_signatures"].append({
                "authority_id": authority["authority_id"], "verification_key_sha256": authority["verification_key_sha256"],
                "algorithm": "Ed25519", "signed_payload_sha256": value["a0_payload_sha256"],
                "signature_base64": base64.b64encode(private.sign(message)).decode(),
            })
            key_rows.append({"authority_id": authority["authority_id"], "public_key_base64": base64.b64encode(public).decode()})
        value["a0_sha256"] = BUILD.self_digest("c5k4-method-v1.5-a0-1.0", value, "a0_sha256")
        key_path = self.repo / "offline-keys.json"
        key_path.write_text(json.dumps({"schema": "c5k4-method-v1.5-offline-a0-authority-keys-1.0", "keys": key_rows}))
        return value, key_path

    def test_draft_is_local_preview_and_cannot_be_published_or_upgraded(self) -> None:
        draft = BUILD.build_a0_draft(self.repo, self.p0t_commit, self.p0t_receipt, observation_verifier=self.accept_observation)
        VERIFY.validate_a0_preview(self.repo, self.p0t_commit, draft)
        commit = self.commit_a0(draft)
        with self.assertRaisesRegex(VERIFY.PublicationError, "local preview.*must not be committed"):
            VERIFY.validate_a0(self.repo, commit)
        with self.assertRaisesRegex(VERIFY.PublicationError, "local preview.*must not be committed"):
            VERIFY.validated_a0_identity(self.repo, commit)
        authoritative, keys = self.authoritative_a0()
        child = self.commit_a0(authoritative, "forbidden draft upgrade")
        with self.assertRaises(VERIFY.PublicationError):
            VERIFY.validate_a0(self.repo, child, authority_keys=keys)

    def test_builder_rejects_target_key_and_unfrozen_ami_policy(self) -> None:
        with self.assertRaisesRegex(BUILD.ChainError, "target-bearing key"):
            BUILD.build_p0a(self.repo, self.base, {"component_paths": self.component_paths, "target_id": "x"}, self.policy)
        bad = copy.deepcopy(self.policy); bad.pop("attestable_ami_authority_binding_policy_sha256")
        with self.assertRaises(BUILD.ChainError):
            BUILD.build_p0a(self.repo, self.base, {"component_paths": self.component_paths}, bad)

    def test_exact_component_closure_rejects_omission_and_addition(self) -> None:
        with self.assertRaisesRegex(BUILD.ChainError, "exact frozen"):
            BUILD.build_p0a(self.repo, self.base, {"component_paths": self.component_paths[:-1]}, self.policy)
        self.write_raw("extra.json", b"{}\n")
        with self.assertRaisesRegex(BUILD.ChainError, "exact frozen"):
            BUILD.build_p0a(self.repo, self.base, {"component_paths": sorted([*self.component_paths, "extra.json"])}, self.policy)

    def test_verifier_reruns_target_audit_and_checks_json_count(self) -> None:
        self.git("checkout", "-qb", "target-exploit", self.base)
        attacked = "schemas/benchmark-a0-v1.5.schema.json"
        self.write_raw(attacked, b'{"candidate_identities":["hidden"]}\n')
        self.git("add", attacked); self.git("commit", "-qm", "target-bearing base")
        attacked_base = self.git("rev-parse", "HEAD")
        malicious = copy.deepcopy(self.p0a); malicious["protocol_base_commit"] = attacked_base
        malicious["components"] = [BUILD.blob_binding(self.repo, attacked_base, path) for path in self.component_paths]
        malicious["components_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-p0a-components-1.0", malicious["components"])
        malicious["p0a_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0a-1.0", malicious, "p0a_sha256")
        self.write(BUILD.P0A_PATH, malicious); self.commit_only(BUILD.P0A_PATH, "malicious P0A")
        with self.assertRaisesRegex(VERIFY.PublicationError, "target-data field"):
            VERIFY.validate_p0a(self.repo, self.git("rev-parse", "HEAD"))

        self.git("checkout", "-qb", "count-exploit", self.base)
        false_count = copy.deepcopy(self.p0a); false_count["target_data_audit"]["json_component_count"] += 1
        false_count["p0a_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0a-1.0", false_count, "p0a_sha256")
        self.write(BUILD.P0A_PATH, false_count); self.commit_only(BUILD.P0A_PATH, "false count")
        with self.assertRaisesRegex(VERIFY.PublicationError, "audit count"):
            VERIFY.validate_p0a(self.repo, self.git("rev-parse", "HEAD"))

    def test_live_actions_replay_authenticates_server_and_raw_projection(self) -> None:
        fetch = self.api_fetch("P0A", self.p0a_commit, 91)
        receipt = VERIFY.compile_actions_observation(self.repo, kind="P0A", commit=self.p0a_commit, run_id=91, fetch=fetch)
        VERIFY.replay_actions_observation(self.repo, receipt, kind="P0A", commit=self.p0a_commit, fetch=fetch)
        BUILD.build_p0t(
            self.repo, self.p0a_commit, receipt,
            observation_verifier=lambda repo, artifact, kind, commit: VERIFY.replay_actions_observation(repo, artifact, kind=kind, commit=commit, fetch=fetch),
        )
        drift = self.api_fetch("P0A", self.p0a_commit, 91, run_mutation=lambda run: run.__setitem__("unexpected_server_field", True))
        with self.assertRaisesRegex(VERIFY.PublicationError, "differs from authenticated"):
            VERIFY.replay_actions_observation(self.repo, receipt, kind="P0A", commit=self.p0a_commit, fetch=drift)

    def test_live_actions_replay_rejects_wrong_repo_attempt_and_duplicate_run(self) -> None:
        cases = [
            self.api_fetch("P0A", self.p0a_commit, 92, run_mutation=lambda run: run["repository"].__setitem__("id", 1)),
            self.api_fetch("P0A", self.p0a_commit, 92, run_mutation=lambda run: run.__setitem__("run_attempt", 2)),
            self.api_fetch("P0A", self.p0a_commit, 92, duplicate=True),
        ]
        for fetch in cases:
            with self.subTest(fetch=fetch), self.assertRaises(VERIFY.PublicationError):
                VERIFY.compile_actions_observation(self.repo, kind="P0A", commit=self.p0a_commit, run_id=92, fetch=fetch)

    def test_live_actions_replay_exhausts_pagination_before_uniqueness_decision(self) -> None:
        run_id = 95
        base = self.api_fetch("P0A", self.p0a_commit, run_id)
        _, listing_url, _ = VERIFY._api_urls(run_id, self.p0a_commit)
        selected = {"id": run_id, "run_attempt": 1, "event": "push", "status": "completed", "conclusion": "success", "head_sha": self.p0a_commit, "head_branch": "method-v1.5-p0"}
        unrelated = {**selected, "id": 1000, "head_sha": "0" * 40}
        called: list[str] = []
        def paginated(url: str) -> bytes:
            called.append(url)
            if url == listing_url:
                return json.dumps({"total_count": 101, "workflow_runs": [selected, *[unrelated] * 99]}).encode()
            if url == listing_url + "&page=2":
                return json.dumps({"total_count": 101, "workflow_runs": [selected]}).encode()
            return base(url)
        with self.assertRaisesRegex(VERIFY.PublicationError, "unique first-attempt"):
            VERIFY.compile_actions_observation(self.repo, kind="P0A", commit=self.p0a_commit, run_id=run_id, fetch=paginated)
        self.assertIn(listing_url + "&page=2", called)

    def test_live_replay_rejects_self_rehashed_fabricated_embedded_timestamp(self) -> None:
        forged = copy.deepcopy(self.p0a_receipt)
        forged["actions_run"]["created_at_utc"] = "2026-08-14T00:59:00Z"
        unsigned = dict(forged["actions_run"]); unsigned.pop("api_projection_sha256"); unsigned.pop("captured_ref_sha256")
        forged["actions_run"]["api_projection_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", unsigned)
        forged["receipt_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", forged, "receipt_sha256")
        fetch = self.api_fetch("P0A", self.p0a_commit, 41)
        with self.assertRaisesRegex(VERIFY.PublicationError, "differs from authenticated"):
            VERIFY.replay_actions_observation(self.repo, forged, kind="P0A", commit=self.p0a_commit, fetch=fetch, allow_ref_advance=True)

    def test_a0_identity_rejects_threshold_signed_fabricated_p0t_server_time(self) -> None:
        value, keys = self.authoritative_a0()
        forged = value["p0t_publication_receipt"]
        forged["actions_run"]["updated_at_utc"] = "2026-08-14T01:02:50Z"
        unsigned = dict(forged["actions_run"]); unsigned.pop("api_projection_sha256"); unsigned.pop("captured_ref_sha256")
        forged["actions_run"]["api_projection_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", unsigned)
        forged["receipt_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", forged, "receipt_sha256")
        value["independent_authority_signatures"] = []
        value["a0_payload_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-a0-activation-payload-1.0", VERIFY._payload(value))
        message = b"c5k4-method-v1.5-a0-authority-signature-1.0\x00" + bytes.fromhex(value["a0_payload_sha256"])
        for authority, private in zip(self.authorities, self.private_keys):
            value["independent_authority_signatures"].append({
                "authority_id": authority["authority_id"], "verification_key_sha256": authority["verification_key_sha256"],
                "algorithm": "Ed25519", "signed_payload_sha256": value["a0_payload_sha256"],
                "signature_base64": base64.b64encode(private.sign(message)).decode(),
            })
        value["a0_sha256"] = BUILD.self_digest("c5k4-method-v1.5-a0-1.0", value, "a0_sha256")
        commit = self.commit_a0(value)
        a0_fetch = self.api_fetch("A0", commit, 96)
        publication = VERIFY.compile_actions_observation(self.repo, kind="A0", commit=commit, run_id=96, fetch=a0_fetch)
        fetch = self.identity_fetch(commit, 96)
        with self.assertRaisesRegex(VERIFY.PublicationError, "differs from authenticated"):
            VERIFY.validated_a0_identity(self.repo, commit, authority_keys=keys, publication_receipt=publication, fetch=fetch)

    def test_same_run_or_nonsequential_push_cannot_bridge_p0a_to_p0t(self) -> None:
        bad = copy.deepcopy(self.p0t_receipt)
        bad["actions_run"]["run_id"] = self.p0a_receipt["actions_run"]["run_id"]
        unsigned = dict(bad["actions_run"]); unsigned.pop("api_projection_sha256"); unsigned.pop("captured_ref_sha256")
        bad["actions_run"]["api_projection_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", unsigned)
        bad["receipt_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", bad, "receipt_sha256")
        with self.assertRaisesRegex(BUILD.ChainError, "distinct sequential pushes"):
            BUILD.build_a0_draft(self.repo, self.p0t_commit, bad, observation_verifier=self.accept_observation)

    def test_repository_builder_has_no_authoritative_a0_and_delegates_live_replay(self) -> None:
        source = (ROOT / "scripts/build_benchmark_v15_p0_a0.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("a0-draft")', source)
        self.assertNotIn('sub.add_parser("a0")', source)
        for forbidden in ("urllib", "requests", "socket", "boto3", "gh api", "git push"):
            self.assertNotIn(forbidden, source)

    def test_receipt_substitution_and_extra_path_are_rejected(self) -> None:
        bad = copy.deepcopy(self.p0t_receipt); bad["actions_run"]["head_sha"] = self.p0a_commit
        bad["receipt_sha256"] = BUILD.self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", bad, "receipt_sha256")
        with self.assertRaisesRegex(BUILD.ChainError, "head SHA"):
            BUILD.build_a0_draft(self.repo, self.p0t_commit, bad, observation_verifier=self.accept_observation)
        draft = BUILD.build_a0_draft(self.repo, self.p0t_commit, self.p0t_receipt, observation_verifier=self.accept_observation)
        self.write(BUILD.A0_PATH, draft); self.write_raw("escape.txt", b"escape\n")
        self.git("add", "-A"); self.git("commit", "-qm", "bad A0")
        with self.assertRaisesRegex(VERIFY.PublicationError, "change exactly"):
            VERIFY.validate_a0(self.repo, self.git("rev-parse", "HEAD"))

    def test_authoritative_a0_requires_exact_frozen_keys_and_valid_signatures(self) -> None:
        value, keys = self.authoritative_a0(); commit = self.commit_a0(value)
        VERIFY.validate_a0(self.repo, commit, require_authoritative=True, authority_keys=keys)
        VERIFY.validate_a0_publication_structure(self.repo, commit)
        a0_fetch = self.api_fetch("A0", commit, 93)
        publication = VERIFY.compile_actions_observation(self.repo, kind="A0", commit=commit, run_id=93, fetch=a0_fetch)
        live = self.identity_fetch(commit, 93); replayed_urls: list[str] = []
        def fetch(url: str) -> bytes:
            replayed_urls.append(url); return live(url)
        identity = VERIFY.validated_a0_identity(self.repo, commit, authority_keys=keys, publication_receipt=publication, fetch=fetch)
        self.assertEqual(identity["commit"], commit)
        self.assertEqual(identity["authority_roster_sha256"], self.policy["authority_roster_sha256"])
        self.assertEqual(identity["external_harness_verification_key_sha256"], "d" * 64)
        self.assertEqual(identity["nitrotpm_key_generation_attestation_sha256"], "e" * 64)
        self.assertEqual(identity["nitrotpm_key_policy"], "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY")
        self.assertEqual(identity["a0_authorized_at_utc"], "2026-08-14T01:03:30Z")
        self.assertEqual(identity["a0_publication_observed_at_utc"], "2026-08-14T01:05:00Z")
        self.assertEqual([identity["github_server_replay"][stage]["run_id"] for stage in ("p0a", "p0t", "a0")], [41, 42, 93])
        for run_id in (41, 42, 93):
            self.assertTrue(any(url.endswith(f"/actions/runs/{run_id}") for url in replayed_urls))
        self.assertTrue(identity["activation_authority"])
        wrong = self.repo / "wrong-keys.json"
        replacement = Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        wrong.write_text(json.dumps({"schema": "c5k4-method-v1.5-offline-a0-authority-keys-1.0", "keys": [
            {"authority_id": "independent-1", "public_key_base64": base64.b64encode(replacement).decode()},
            json.loads(keys.read_text())["keys"][1],
        ]}))
        with self.assertRaisesRegex(VERIFY.PublicationError, "frozen authority roster"):
            VERIFY.validate_a0(self.repo, commit, require_authoritative=True, authority_keys=wrong)

    def test_harness_key_must_differ_from_every_independent_authority(self) -> None:
        value, keys = self.authoritative_a0(self.authorities[0]["verification_key_sha256"])
        commit = self.commit_a0(value)
        with self.assertRaisesRegex(VERIFY.PublicationError, "must differ"):
            VERIFY.validate_a0(self.repo, commit, authority_keys=keys)

    def test_a0_identity_rejects_publication_before_signed_authority_time(self) -> None:
        value, keys = self.authoritative_a0(); commit = self.commit_a0(value)
        def early(run):
            run["created_at"] = "2026-08-14T01:03:00Z"
            run["run_started_at"] = "2026-08-14T01:03:05Z"
            run["updated_at"] = "2026-08-14T01:03:20Z"
        a0_fetch = self.api_fetch("A0", commit, 94, run_mutation=early)
        receipt = VERIFY.compile_actions_observation(self.repo, kind="A0", commit=commit, run_id=94, fetch=a0_fetch)
        fetch = self.identity_fetch(commit, 94, a0_mutation=early)
        with self.assertRaisesRegex(VERIFY.PublicationError, "live-replayed.*chronology"):
            VERIFY.validated_a0_identity(self.repo, commit, authority_keys=keys, publication_receipt=receipt, fetch=fetch)

    def test_parent_digest_and_ami_policy_substitution_are_rejected(self) -> None:
        value, keys = self.authoritative_a0()
        value["external_harness_authority"]["attestable_ami_authority_binding_policy_sha256"] = "f" * 64
        value["a0_payload_sha256"] = BUILD.domain_digest("c5k4-method-v1.5-a0-activation-payload-1.0", VERIFY._payload(value))
        value["a0_sha256"] = BUILD.self_digest("c5k4-method-v1.5-a0-1.0", value, "a0_sha256")
        commit = self.commit_a0(value)
        with self.assertRaises(VERIFY.PublicationError):
            VERIFY.validate_a0(self.repo, commit, require_authoritative=True, authority_keys=keys)


if __name__ == "__main__":
    unittest.main()
