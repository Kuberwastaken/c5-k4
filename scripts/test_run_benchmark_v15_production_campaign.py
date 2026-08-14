#!/usr/bin/env python3
"""Adversarial bootstrap tests; no production helper or target is executed."""

from __future__ import annotations

import base64
import ast
import copy
import errno
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("v15_production_campaign_test_target", ROOT / "scripts" / "run_benchmark_v15_production_campaign.py")
assert SPEC is not None and SPEC.loader is not None
campaign = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = campaign
SPEC.loader.exec_module(campaign)
H = "a" * 64


class ProductionCampaignTests(unittest.TestCase):
    def setUp(self) -> None:
        self.keys = {role: Ed25519PrivateKey.generate() for role in campaign.ROLES}
        self.public = {role: key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw) for role, key in self.keys.items()}
        self.ids = [f"cluster-{index:02d}" for index in range(12)]
        self.ancestry_sha = "c" * 64
        self.activation = self.make_activation()
        self.closure_calls = 0

    def sign_section(self, role, section):
        section["signature"] = {
            "signer_id": campaign.SIGNER_IDS[role], "key_sha256": hashlib.sha256(self.public[role]).hexdigest(),
            "algorithm": "Ed25519", "signature_base64": base64.b64encode(self.keys[role].sign(campaign._signature_payload(role, section))).decode(),
        }

    def make_activation(self):
        c1 = {"status": "VERIFIED_C1_TWELVE_CLUSTER_SELECTION", "repository_path": "/private/campaign", "repository_uid": 0, "repository_gid": 0, "repository_mode": 0o700, "c1_attestation_commit": "1" * 40, "selected_cluster_ids": self.ids, "selection_sha256": hashlib.sha256(campaign.canonical_bytes(self.ids)).hexdigest()}
        freeze = {"status": "TWELVE_EXECUTION_ENVELOPES_FROZEN", "repository_path": "/private/campaign", "repository_uid": 0, "repository_gid": 0, "repository_mode": 0o700, "c1_attestation_commit": "1" * 40, "run_freeze_commit": "2" * 40, "triplets": [{"cluster_id": item, "envelope_path": f"/private/campaign/envelopes/{item}.json", "envelope_sha256": f"{index + 1:064x}"} for index, item in enumerate(self.ids)]}
        target_rows = []
        for index, item in enumerate(self.ids):
            target_path, target_sha = f"/private/targets/{item}", f"{index + 100:064x}"
            target_rows.append({"cluster_id": item, "path": target_path, "sha256": target_sha, "argv_by_arm": {arm: ["/inputs/COMMON_TARGET_BUNDLE", "--arm", arm] for arm in campaign.ARMS}, "allowed_roots_by_arm": {arm: [{"root_role": "COMMON_TARGET_BUNDLE", "path": target_path, "sha256": target_sha, "uid": 1000, "gid": 1000, "mode": 0o500}, {"root_role": f"{arm}_CONTRACT", "path": f"/private/inputs/{item}/{arm}", "sha256": f"{index + 200:064x}", "uid": 1000, "gid": 1000, "mode": 0o400}] for arm in campaign.ARMS}, "private_roots_by_arm": {arm: {"path": f"/private/results/{item}/{arm}", "uid": 1000, "gid": 1000, "mode": 0o700} for arm in campaign.ARMS}, "uses_ilp": index == 0, "ilp_cap_seconds": 60 if index == 0 else None})
        targets = {"status": "SEALED_PRIVATE_TARGET_BUNDLE_VERIFIED", "private_only": True, "targets": target_rows}
        closure = {role: {"path": path, "sha256": H} for role, path in campaign.EXPECTED_CLOSURE_PATHS.items()}
        harness = {
            "status": "CONTROLLED_HARNESS_PRODUCTION_ACCEPTED", "host_id": "ai-vps-controlled-harness",
            "host_fingerprint_sha256": H, "runtime_sha256": H,
            "executor_binary_path": str(campaign.EXECUTOR_PATH), "executor_binary_sha256": H,
            "fixture_runtime_sha256": "b" * 64, "production_runtime_distinct": True,
            "network_default_deny": True, "target_output_private": True,
            "authority_key_digests": {role: hashlib.sha256(self.public[role]).hexdigest() for role in campaign.ROLES},
            "implementation_closure": closure,
            "executor_acceptance": {"binary_path": str(campaign.EXECUTOR_PATH), "binary_sha256": H, "descriptor_pinned_inputs": True, "network_namespace_default_deny": True, "cgroup_v2_cpu_accounting": True, "whole_tree_cgroup_kill": True, "setsid_escape_contained": True, "wall_cap_seconds": 60, "ilp_cap_seconds": 60},
            "journal_acceptance": {"backend": "AWS_S3_OBJECT_LOCK_COMPLIANCE", "append_only": True, "signed_entries": True, "crash_recovery": "RESUME_OR_TERMINAL_REJECT", "caller_deletion_can_reauthorize": False, "acceptance_sha256": H},
            "accepted_at_utc": "2027-01-01T00:00:00Z",
        }
        for role, section in (("c1", c1), ("freeze", freeze), ("private_targets", targets), ("harness", harness)): self.sign_section(role, section)
        value = {"schema": "c5k4-method-v1.5-production-campaign-activation-1.0", "status": "POST_C1_PRODUCTION_CAMPAIGN_AUTHORIZED", "protocol_version": "1.5", "c1": c1, "freeze": freeze, "private_targets": targets, "harness": harness, "activation_sha256": H}
        value["activation_sha256"] = campaign.digest_object(value, "activation_sha256")
        return value

    def closure(self, _):
        self.closure_calls += 1
        result = {role: ROOT for role in campaign.EXPECTED_CLOSURE_PATHS}
        result["launcher"] = Path(campaign.__file__).resolve()
        result["activation_schema"] = ROOT / "schemas" / "benchmark-production-campaign-activation-v1.5.schema.json"
        result["receipt_schema"] = ROOT / "schemas" / "benchmark-production-campaign-receipt-v1.5.schema.json"
        return result

    def ancestry(self, _): return self.ancestry_sha

    @staticmethod
    def locator(object_sha=H, unique=H):
        return {"backend": "AWS_S3_OBJECT_LOCK_COMPLIANCE", "bucket_sha256": H, "key_sha256": unique, "version_id_sha256": hashlib.sha256((unique + "version").encode()).hexdigest(), "object_sha256": object_sha, "retention_mode": "COMPLIANCE", "signed_journal_entry_sha256": object_sha}

    def sign_tree(self, tree):
        unsigned = {key: value for key, value in tree.items() if key not in {"completion_sha256", "journal_locator", "signature"}}
        digest = hashlib.sha256(campaign.canonical_bytes(unsigned)).hexdigest()
        tree["completion_sha256"] = digest
        tree["signature"] = {"signer_id": campaign.SIGNER_IDS["harness"], "key_sha256": hashlib.sha256(self.public["harness"]).hexdigest(), "algorithm": "Ed25519", "signature_base64": base64.b64encode(self.keys["harness"].sign(campaign.TREE_RECEIPT_DOMAIN + b"\0" + bytes.fromhex(digest))).decode()}

    def make_receipt(self, fail_first=False):
        triplets = []
        for cluster_index, cluster in enumerate(self.ids):
            trees = []
            for arm in campaign.ARMS:
                for tree_index in range(8):
                    target = self.activation["private_targets"]["targets"][cluster_index]
                    roots = target["allowed_roots_by_arm"][arm]; base = target["private_roots_by_arm"][arm]
                    private = {"path": f"{base['path']}/tree-{tree_index}", "uid": base["uid"], "gid": base["gid"], "mode": base["mode"]}
                    invocation = {"cluster_id_sha256": hashlib.sha256(cluster.encode()).hexdigest(), "envelope_sha256": self.activation["freeze"]["triplets"][cluster_index]["envelope_sha256"], "arm": arm, "tree_index": tree_index, "wall_cap_seconds": 60, "ilp_cap_seconds": 60 if cluster_index == 0 else None, "network_policy": "DENY", "executor_binary_sha256": H, "argv_sha256": hashlib.sha256(campaign.canonical_bytes(target["argv_by_arm"][arm])).hexdigest(), "allowed_root_manifest_sha256": hashlib.sha256(campaign.canonical_bytes(roots)).hexdigest(), "private_root_sha256": hashlib.sha256(campaign.canonical_bytes(private)).hexdigest()}
                    descriptor_sha = hashlib.sha256(campaign.canonical_bytes({"allowed_roots": roots, "private_root": private})).hexdigest()
                    evidence_hashes = {"descriptor_manifest": descriptor_sha, "namespace_inode_set": H, "process_tree_audit": H, "cgroup_v2": H}
                    evidence = {name: self.locator(evidence_hashes[name], hashlib.sha256(f"evidence-{cluster_index}-{arm}-{tree_index}-{name}".encode()).hexdigest()) for name in evidence_hashes}
                    success = not (fail_first and cluster_index == 0 and arm == "CATALOGUE" and tree_index == 0)
                    tree = {"tree_id": f"{arm}-{tree_index}", "invocation": invocation, "invocation_sha256": hashlib.sha256(campaign.canonical_bytes(invocation)).hexdigest(), "completion_sha256": H, "accepted": success, "returncode": 0 if success else 3, "timed_out": False, "network_denied": success, "descriptor_pinned_inputs": True, "whole_tree_cgroup_killed_or_reaped": True, "setsid_escape_contained": True, "descriptor_manifest_sha256": descriptor_sha, "namespace_inode_set_sha256": H, "process_tree_audit_sha256": H, "cgroup_v2_sha256": H, "cpu_usec": 1, "wall_milliseconds": 1, "ilp_cap_seconds": 60 if cluster_index == 0 else None, "stdout_sha256": H, "stderr_sha256": H, "artifact_sha256": H, "evidence_locators": evidence, "journal_locator": self.locator(), "signature": {}}
                    self.sign_tree(tree); trees.append(tree)
            triplets.append({"cluster_id_sha256": hashlib.sha256(cluster.encode()).hexdigest(), "envelope_sha256": self.activation["freeze"]["triplets"][cluster_index]["envelope_sha256"], "tree_count": 24, "trees": trees, "accepted": all(tree["accepted"] for tree in trees)})
        tree_maps = [{tree["tree_id"]: tree for tree in row["trees"]} for row in triplets]
        entries, prior = [], campaign.ZERO_SHA256
        def add_entry(state, triplet_index, tree_id, payload):
            nonlocal prior
            unsigned = {"sequence": len(entries), "state": state, "triplet_index": triplet_index, "tree_id": tree_id, "prior_entry_sha256": prior, "payload_sha256": payload}
            digest = hashlib.sha256(campaign.canonical_bytes(unsigned)).hexdigest()
            locator = self.locator(digest, hashlib.sha256(f"journal-{len(entries)}".encode()).hexdigest())
            entry = {**unsigned, "entry_sha256": digest, "locator": locator, "signature": {"signer_id": campaign.SIGNER_IDS["harness"], "key_sha256": hashlib.sha256(self.public["harness"]).hexdigest(), "algorithm": "Ed25519", "signature_base64": base64.b64encode(self.keys["harness"].sign(campaign.JOURNAL_ENTRY_DOMAIN + b"\0" + bytes.fromhex(digest))).decode()}}
            entries.append(entry); prior = digest
            return locator
        add_entry("PREPARE", None, None, self.activation["activation_sha256"])
        ordered_ids = [f"{arm}-{index}" for arm in campaign.ARMS for index in range(8)]
        for cluster_index in range(12):
            for tree_id in ordered_ids: add_entry("START", cluster_index, tree_id, tree_maps[cluster_index][tree_id]["invocation_sha256"])
            for tree_id in ordered_ids: tree_maps[cluster_index][tree_id]["journal_locator"] = add_entry("COMPLETE", cluster_index, tree_id, tree_maps[cluster_index][tree_id]["completion_sha256"])
        final_payload = hashlib.sha256(campaign.canonical_bytes([tree_maps[index][tree_id]["completion_sha256"] for index in range(12) for tree_id in ordered_ids])).hexdigest()
        final_locator = add_entry("FINALIZE", None, None, final_payload)
        receipt = {"schema": "c5k4-method-v1.5-production-campaign-receipt-1.0", "status": "PRODUCTION_CAMPAIGN_REJECTED_AFTER_COMPLETE_BARRIERS" if fail_first else "PRODUCTION_CAMPAIGN_TERMINATED", "protocol_version": "1.5", "activation_sha256": self.activation["activation_sha256"], "c1_attestation_commit": "1" * 40, "run_freeze_commit": "2" * 40, "git_ancestry_verified": True, "git_ancestry_evidence_locator": self.locator(self.ancestry_sha, "d" * 64), "triplet_count": 12, "arm_count": 36, "process_tree_count": 288, "budget": {"trees_per_arm": 8, "wall_seconds_per_tree": 60, "cpu_seconds_per_arm_max": 480, "ilp_cap_seconds": 60}, "network_policy": "DENY", "target_output_revealed": False, "journal_root": final_locator, "journal": {"entry_count": 578, "entries": entries}, "triplets": triplets, "receipt_sha256": H, "signature": {}}
        unsigned = {key: value for key, value in receipt.items() if key not in {"receipt_sha256", "signature"}}
        digest = hashlib.sha256(campaign.canonical_bytes(unsigned)).hexdigest(); receipt["receipt_sha256"] = digest
        receipt["signature"] = {"signer_id": campaign.SIGNER_IDS["harness"], "key_sha256": hashlib.sha256(self.public["harness"]).hexdigest(), "algorithm": "Ed25519", "signature_base64": base64.b64encode(self.keys["harness"].sign(campaign.RECEIPT_DOMAIN + b"\0" + bytes.fromhex(digest))).decode()}
        return receipt

    def raw_activation(self): return campaign.canonical_bytes(self.activation)

    def resign_receipt(self, receipt):
        unsigned = {key: value for key, value in receipt.items() if key not in {"receipt_sha256", "signature"}}
        digest = hashlib.sha256(campaign.canonical_bytes(unsigned)).hexdigest(); receipt["receipt_sha256"] = digest
        receipt["signature"]["signature_base64"] = base64.b64encode(self.keys["harness"].sign(campaign.RECEIPT_DOMAIN + b"\0" + bytes.fromhex(digest))).decode()

    def test_valid_bootstrap_and_signed_receipt_verify_all_288(self):
        receipt = self.make_receipt()
        activation, closure, ancestry = campaign._authenticate_activation(self.raw_activation(), self.public, self.closure, self.ancestry)
        result = campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)
        self.assertEqual(sum(len(row["trees"]) for row in result["triplets"]), 288)

    def test_same_key_wrong_role_and_wrong_identity_fail_before_closure_or_helper(self):
        same = {role: self.public["c1"] for role in campaign.ROLES}
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "four distinct"):
            campaign._authenticate_activation(self.raw_activation(), same, self.closure, self.ancestry)
        wrong = dict(self.public); wrong["c1"], wrong["freeze"] = wrong["freeze"], wrong["c1"]
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "role-pinned"):
            campaign._authenticate_activation(self.raw_activation(), wrong, self.closure, self.ancestry)
        altered = copy.deepcopy(self.activation); altered["c1"]["signature"]["signer_id"] = campaign.SIGNER_IDS["freeze"]
        altered["activation_sha256"] = campaign.digest_object(altered, "activation_sha256")
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "signer identity"):
            campaign._authenticate_activation(campaign.canonical_bytes(altered), self.public, self.closure, self.ancestry)
        self.assertEqual(self.closure_calls, 0)

    def test_every_bad_role_signature_fails_before_closure_and_helper(self):
        for role in campaign.ROLES:
            altered = copy.deepcopy(self.activation)
            altered[role]["signature"]["signature_base64"] = base64.b64encode(b"\0" * 64).decode()
            altered["activation_sha256"] = campaign.digest_object(altered, "activation_sha256")
            closure_calls = []; helper_calls = []
            with self.subTest(role=role):
                with self.assertRaisesRegex(campaign.ProductionCampaignError, f"{role} signature"):
                    campaign._authenticate_activation(campaign.canonical_bytes(altered), self.public, lambda value: closure_calls.append(value), self.ancestry)
            self.assertEqual(closure_calls, []); self.assertEqual(helper_calls, [])

    def test_production_api_has_no_injected_helper_or_closure_surface(self):
        self.assertEqual(set(inspect.signature(campaign.execute_campaign).parameters), {"raw"})
        self.assertEqual(set(inspect.signature(campaign.authenticate_activation).parameters), {"raw"})

    def test_bootstrap_has_no_repository_local_or_dynamic_import(self):
        source = Path(campaign.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module.split(".")[0]
            for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
        }
        self.assertFalse(imported & {"scripts", "run_benchmark_v15_triplet", "method_v15_triplet_production_adapter", "method_v15_triplet_production_runtime", "run_benchmark_v14_job", "importlib"})

    def test_installed_helper_requires_descriptor_pinned_root_owned_elf(self):
        metadata = SimpleNamespace(st_mode=stat.S_IFREG | 0o555, st_nlink=1, st_uid=0, st_gid=0)
        no_caps = OSError(errno.ENODATA, "none")
        with mock.patch.object(campaign.os, "open", return_value=91), mock.patch.object(campaign.os, "fstat", return_value=metadata), mock.patch.object(campaign.os, "read", side_effect=[b"#!/bin/sh\n", b""]), mock.patch.object(campaign.os, "getxattr", side_effect=no_caps), mock.patch.object(campaign.os, "close"), mock.patch.object(campaign.subprocess, "run") as run:
            with self.assertRaisesRegex(campaign.ProductionCampaignError, "provenance"):
                campaign.InstalledCampaignHelper().run(b"{}", hashlib.sha256(b"#!/bin/sh\n").hexdigest())
            run.assert_not_called()

        elf = b"\x7fELF" + b"accepted-helper"
        completed = SimpleNamespace(returncode=0, stdout=b"{}")
        with mock.patch.object(campaign.os, "open", return_value=92), mock.patch.object(campaign.os, "fstat", return_value=metadata), mock.patch.object(campaign.os, "read", side_effect=[elf, b""]), mock.patch.object(campaign.os, "getxattr", side_effect=no_caps), mock.patch.object(campaign.os, "close"), mock.patch.object(campaign.subprocess, "run", return_value=completed) as run:
            self.assertEqual(campaign.InstalledCampaignHelper().run(b"sealed", hashlib.sha256(elf).hexdigest()), b"{}")
            args, kwargs = run.call_args
            self.assertEqual(args[0][0], "/proc/self/fd/92")
            self.assertEqual(kwargs["pass_fds"], (92,))

        setid = SimpleNamespace(st_mode=stat.S_IFREG | stat.S_ISUID | 0o555, st_nlink=1, st_uid=0, st_gid=0)
        with mock.patch.object(campaign.os, "open", return_value=93), mock.patch.object(campaign.os, "fstat", return_value=setid), mock.patch.object(campaign.os, "read", side_effect=[elf, b""]), mock.patch.object(campaign.os, "getxattr", side_effect=no_caps), mock.patch.object(campaign.os, "close"), mock.patch.object(campaign.subprocess, "run") as run:
            with self.assertRaisesRegex(campaign.ProductionCampaignError, "provenance"):
                campaign.InstalledCampaignHelper().run(b"sealed", hashlib.sha256(elf).hexdigest())
            run.assert_not_called()
        with mock.patch.object(campaign.os, "open", return_value=94), mock.patch.object(campaign.os, "fstat", return_value=metadata), mock.patch.object(campaign.os, "read", side_effect=[elf, b""]), mock.patch.object(campaign.os, "getxattr", return_value=b"capability"), mock.patch.object(campaign.os, "close"), mock.patch.object(campaign.subprocess, "run") as run:
            with self.assertRaisesRegex(campaign.ProductionCampaignError, "provenance"):
                campaign.InstalledCampaignHelper().run(b"sealed", hashlib.sha256(elf).hexdigest())
            run.assert_not_called()

    def test_strict_completion_types_duplicate_tree_and_budget_evidence_fail(self):
        mutations = (("network_denied", 1), ("timed_out", 0), ("returncode", False), ("cpu_usec", 60_000_001), ("wall_milliseconds", 60_001), ("descriptor_pinned_inputs", 1))
        activation, closure, ancestry = campaign._authenticate_activation(self.raw_activation(), self.public, self.closure, self.ancestry)
        for key, value in mutations:
            receipt = self.make_receipt(); receipt["triplets"][0]["trees"][0][key] = value
            # Re-sign outer receipt only: malformed or stale inner evidence must fail.
            unsigned = {k: v for k, v in receipt.items() if k not in {"receipt_sha256", "signature"}}
            digest = hashlib.sha256(campaign.canonical_bytes(unsigned)).hexdigest(); receipt["receipt_sha256"] = digest
            receipt["signature"]["signature_base64"] = base64.b64encode(self.keys["harness"].sign(campaign.RECEIPT_DOMAIN + b"\0" + bytes.fromhex(digest))).decode()
            with self.subTest(key=key), self.assertRaises(campaign.ProductionCampaignError):
                campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)
        receipt = self.make_receipt(); receipt["triplets"][0]["trees"][1] = copy.deepcopy(receipt["triplets"][0]["trees"][0])
        unsigned = {k: v for k, v in receipt.items() if k not in {"receipt_sha256", "signature"}}; digest = hashlib.sha256(campaign.canonical_bytes(unsigned)).hexdigest(); receipt["receipt_sha256"] = digest; receipt["signature"]["signature_base64"] = base64.b64encode(self.keys["harness"].sign(campaign.RECEIPT_DOMAIN + b"\0" + bytes.fromhex(digest))).decode()
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "exact 24"):
            campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)

    def test_arbitrarily_resigned_root_or_private_binding_cannot_replace_activation(self):
        activation, closure, ancestry = campaign._authenticate_activation(self.raw_activation(), self.public, self.closure, self.ancestry)
        for field in ("allowed_root_manifest_sha256", "private_root_sha256", "argv_sha256"):
            receipt = self.make_receipt(); tree = receipt["triplets"][0]["trees"][0]
            tree["invocation"][field] = "f" * 64
            tree["invocation_sha256"] = hashlib.sha256(campaign.canonical_bytes(tree["invocation"])).hexdigest()
            self.sign_tree(tree); self.resign_receipt(receipt)
            with self.subTest(field=field), self.assertRaisesRegex(campaign.ProductionCampaignError, "replayably bound"):
                campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)

    def test_evidence_locator_mismatch_and_journal_gap_or_replay_fail(self):
        activation, closure, ancestry = campaign._authenticate_activation(self.raw_activation(), self.public, self.closure, self.ancestry)
        receipt = self.make_receipt(); tree = receipt["triplets"][0]["trees"][0]
        tree["evidence_locators"]["cgroup_v2"]["object_sha256"] = "f" * 64
        self.sign_tree(tree); self.resign_receipt(receipt)
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "exact WORM object"):
            campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)
        for mutation in ("gap", "replay"):
            receipt = self.make_receipt()
            if mutation == "gap": receipt["journal"]["entries"][10]["sequence"] = 11
            else: receipt["journal"]["entries"][10] = copy.deepcopy(receipt["journal"]["entries"][9])
            self.resign_receipt(receipt)
            with self.subTest(mutation=mutation), self.assertRaises(campaign.ProductionCampaignError):
                campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)

    def test_duplicate_json_key_and_non_40_hex_commit_fail_before_closure(self):
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "duplicate JSON key"):
            campaign._authenticate_activation(b'{"schema":1,"schema":2}', self.public, self.closure, self.ancestry)
        altered = copy.deepcopy(self.activation); altered["c1"]["c1_attestation_commit"] = "1" * 64; self.sign_section("c1", altered["c1"]); altered["activation_sha256"] = campaign.digest_object(altered, "activation_sha256")
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "40-hex"):
            campaign._authenticate_activation(campaign.canonical_bytes(altered), self.public, self.closure, self.ancestry)

    def test_fixture_digest_cannot_masquerade_as_private_target(self):
        altered = copy.deepcopy(self.activation)
        altered["private_targets"]["targets"][0]["sha256"] = H
        self.sign_section("private_targets", altered["private_targets"])
        altered["activation_sha256"] = campaign.digest_object(altered, "activation_sha256")
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "masquerades"):
            campaign._authenticate_activation(campaign.canonical_bytes(altered), self.public, self.closure, self.ancestry)

    def test_private_root_overlap_and_writable_input_mode_are_rejected(self):
        overlap = copy.deepcopy(self.activation)
        overlap["private_targets"]["targets"][1]["private_roots_by_arm"]["CATALOGUE"] = copy.deepcopy(overlap["private_targets"]["targets"][0]["private_roots_by_arm"]["CATALOGUE"])
        self.sign_section("private_targets", overlap["private_targets"]); overlap["activation_sha256"] = campaign.digest_object(overlap, "activation_sha256")
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "writable roots overlap"):
            campaign._authenticate_activation(campaign.canonical_bytes(overlap), self.public, self.closure, self.ancestry)
        writable = copy.deepcopy(self.activation)
        writable["private_targets"]["targets"][0]["allowed_roots_by_arm"]["CATALOGUE"][0]["mode"] = 0o700
        self.sign_section("private_targets", writable["private_targets"]); writable["activation_sha256"] = campaign.digest_object(writable, "activation_sha256")
        with self.assertRaisesRegex(campaign.ProductionCampaignError, "input root identity/mode"):
            campaign._authenticate_activation(campaign.canonical_bytes(writable), self.public, self.closure, self.ancestry)

    def test_wrong_same_boot_host_fails_before_closure_files_or_executor(self):
        harness = copy.deepcopy(self.activation["harness"])
        harness["host_fingerprint_sha256"] = "f" * 64
        with mock.patch.object(campaign, "host_fingerprint", return_value="e" * 64), self.assertRaisesRegex(campaign.ProductionCampaignError, "host/runtime/network"):
            campaign.verify_immutable_closure(harness)

    def test_git_ancestry_is_recomputed_from_exact_commits_and_envelope_blobs(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary).resolve()
            def git(*args):
                return subprocess.run(["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE, env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}).stdout.strip().decode()
            git("init", "-q"); git("config", "user.name", "test"); git("config", "user.email", "test@example.invalid")
            git("commit", "--allow-empty", "-q", "-m", "C1"); c1 = git("rev-parse", "HEAD")
            rows = []
            (repo / "envelopes").mkdir()
            for index, cluster in enumerate(self.ids):
                envelope = {"cluster_id": cluster, "envelope_sha256": campaign.ZERO_SHA256}
                envelope["envelope_sha256"] = campaign.digest_object(envelope, "envelope_sha256")
                path = repo / "envelopes" / f"{cluster}.json"; path.write_bytes(campaign.canonical_bytes(envelope))
                rows.append({"cluster_id": cluster, "envelope_path": str(path), "envelope_sha256": envelope["envelope_sha256"]})
            git("add", "envelopes"); git("commit", "-q", "-m", "freeze"); freeze = git("rev-parse", "HEAD")
            value = copy.deepcopy(self.activation)
            value["c1"]["repository_path"] = str(repo); value["c1"]["c1_attestation_commit"] = c1
            metadata = repo.lstat()
            for section in (value["c1"], value["freeze"]): section["repository_uid"] = metadata.st_uid; section["repository_gid"] = metadata.st_gid; section["repository_mode"] = stat.S_IMODE(metadata.st_mode)
            value["freeze"]["repository_path"] = str(repo); value["freeze"]["c1_attestation_commit"] = c1; value["freeze"]["run_freeze_commit"] = freeze; value["freeze"]["triplets"] = rows
            self.assertRegex(campaign.verify_git_ancestry(value), "^[0-9a-f]{64}$")
            value["freeze"]["run_freeze_commit"] = "f" * 40
            with self.assertRaisesRegex(campaign.ProductionCampaignError, "Git verification"):
                campaign.verify_git_ancestry(value)

    def test_signed_terminal_rejection_is_verifiable_but_never_success(self):
        activation, closure, ancestry = campaign._authenticate_activation(self.raw_activation(), self.public, self.closure, self.ancestry)
        receipt = self.make_receipt(fail_first=True)
        verified = campaign._verify_receipt(campaign.canonical_bytes(receipt), activation, closure, self.public["harness"], ancestry)
        self.assertEqual(verified["status"], "PRODUCTION_CAMPAIGN_REJECTED_AFTER_COMPLETE_BARRIERS")


if __name__ == "__main__": unittest.main()
