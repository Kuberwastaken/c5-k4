#!/usr/bin/env python3
"""Tests for isolated Method v1.3 C0A/C0T assembly."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("build_benchmark_v13_c0.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v13_c0_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
C0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_digest(value: dict, key: str) -> str:
    return hashlib.sha256(C0.canonical_json({k: v for k, v in value.items() if k != key})).hexdigest()


class C0Tests(unittest.TestCase):
    def setUp(self):
        parent = C0.ROOT / "results" / "benchmark"
        self.temp = tempfile.TemporaryDirectory(prefix="v13-c0-test-", dir=parent)
        self.root = Path(self.temp.name)
        self.refs = {}

        def install(name: str, value: dict):
            path = self.root / f"{name}.json"
            path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
            ref = {"path": path.relative_to(C0.ROOT).as_posix(), "sha256": digest(path)}
            self.refs[name] = ref
            return value

        components = {}
        for role in C0.P0.REQUIRED_COMPONENTS:
            path = self.root / f"component-{role}.txt"
            path.write_text(role, encoding="utf-8")
            components[role] = {
                "path": path.relative_to(C0.ROOT).as_posix(),
                "sha256": digest(path),
                "content_class": "PROTOCOL_ONLY_NO_TARGET_DATA",
            }
        self.component_refs = {name: {"path": row["path"], "sha256": row["sha256"]} for name, row in components.items()}
        receipt_path = self.root / "audit.json"
        receipt = {
            "schema_version": "c5k4-method-v1.3-target-data-audit-receipt-1.0",
            "audit_rule_sha256": components["target_data_audit_rule"]["sha256"],
            "components": [{"role": role, "path": components[role]["path"], "sha256": components[role]["sha256"], "classification": "PROTOCOL_ONLY_NO_TARGET_DATA"} for role in C0.P0.REQUIRED_COMPONENTS],
            "final_eligible_rows_detected": 0, "selected_clusters_detected": 0,
            "statement_text_detected": 0, "semantic_target_analysis_detected": 0,
        }
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        producer_refs = {}
        for name in ("producer", "contract", "input", "output"):
            path = self.root / name
            path.write_text(name)
            producer_refs[name] = {"path": path.relative_to(C0.ROOT).as_posix(), "sha256": digest(path)}
        p0a = {
            "schema_version": C0.P0.SCHEMA_VERSION, "artifact_kind": "P0A",
            "authority": "AUTHORITATIVE_P0", "protocol_version": "1.3",
            "components": components,
            "allowlisted_registry_producers": [{
                "producer_id": "builder", "executable": producer_refs["producer"],
                "invocation_contract": producer_refs["contract"], "input_schema": producer_refs["input"],
                "output_schema": producer_refs["output"],
            }],
            "prototype_artifacts": [],
            "target_data_audit_receipt": {"path": receipt_path.relative_to(C0.ROOT).as_posix(), "sha256": digest(receipt_path)},
            "registry_build": {"allowed_build_count": 1, "requires_p0t": True, "entropy_permitted": False, "upstream_resolution_component": "upstream_ref_rule"},
            "prohibitions": {"final_eligible_pool": True, "selection": True, "target_ranking": True, "statement_text": True, "semantic_target_analysis": True},
            "final_eligible_rows": [], "selected_clusters": [], "target_semantics": [],
        }
        install("p0a", p0a)
        p0t = {
            "schema_version": C0.P0.SCHEMA_VERSION, "artifact_kind": "P0T", "protocol_version": "1.3",
            "p0a": self.refs["p0a"], "p0a_commit": "1" * 40,
            "p0a_published_at_utc": "2026-08-13T00:00:00Z",
            "attestation_policy": {"p0a_ancestor_required": True, "p0a_bytes_immutable": True, "allowed_p0t_changed_paths": ["p0t.json"]},
        }
        install("p0t", p0t)
        s0 = {
            "schema_version": C0.SOURCE.SNAPSHOT_SCHEMA, "snapshot_id": "S0",
            "acquired_at_utc": "2026-08-13T01:00:00Z", "p0_artifact_commit": "1" * 40,
            "p0_attestation_commit": "2" * 40, "p0_published_at_utc": "2026-08-13T00:00:00Z",
            "source_path_policy_sha256": "3" * 64, "source_discovery_contract_sha256": "4" * 64,
            "sources_config_sha256": "5" * 64, "sources_config_file_sha256": "6" * 64,
            "candidate_semantics_inspected": False, "complete": True, "sources": [],
            "nonresearch_exclusions": [], "corpus_sha256": hashlib.sha256(C0.canonical_json([])).hexdigest(),
        }
        s0["snapshot_sha256"] = object_digest(s0, "snapshot_sha256")
        install("s0", s0)

        artifacts = {}
        for index, name in enumerate(C0.SELECTOR.ARTIFACT_KEYS):
            artifacts[name] = install(name, {"fixture": name, "n": index})
        upstream = {"repository": "google-deepmind/formal-conjectures", "commit": "7" * 40, "tree": "8" * 40}
        clusters = []
        cursor = 0
        for stratum, quota in C0.SELECTOR.QUOTAS.items():
            for _ in range(quota):
                cursor += 1
                clusters.append({"cluster_id": f"c-{cursor}", "identity_sha256": f"{cursor:064x}", "stratum": stratum, "eligible": True})
        pool = {
            "schema_version": C0.SELECTOR.POOL_SCHEMA_VERSION, "artifact_status": "CONTAMINATION_APPLIED",
            "upstream": upstream,
            "digests": {f"{name}_sha256": self.refs[name]["sha256"] for name in C0.SELECTOR.ARTIFACT_KEYS},
            "clusters": clusters,
        }
        install("eligible_pool", pool)
        strata = [{"stratum": s, "quota": q, "eligible_count": q, "deficit": 0, "surplus": 0} for s, q in C0.SELECTOR.QUOTAS.items()]
        feasibility = {
            "schema_version": C0.SELECTOR.FEASIBILITY_SCHEMA_VERSION, "status": "PASS",
            "phase": "PRE_C0_FEASIBILITY", "entropy_used": False, "selected_clusters": [],
            "upstream": upstream, "quotas": C0.SELECTOR.QUOTAS,
            "digests": {
                "eligible_pool_file_sha256": self.refs["eligible_pool"]["sha256"],
                "eligible_pool_canonical_sha256": hashlib.sha256(C0.SELECTOR.canonical_json(pool)).hexdigest(),
                **{f"{name}_sha256": self.refs[name]["sha256"] for name in C0.SELECTOR.ARTIFACT_KEYS},
            },
            "strata": strata,
            "chronology": {
                "p0_artifact_commit": "1" * 40, "p0_attestation_commit": "2" * 40,
                "p0_published_at_utc": "2026-08-13T00:00:00Z", "s0_acquired_at_utc": "2026-08-13T01:00:00Z",
                "feasibility_checked_at_utc": "2026-08-13T02:00:00Z",
            },
        }
        feasibility["certificate_sha256"] = C0.SELECTOR.object_digest(feasibility, "certificate_sha256")
        install("quota_feasibility", feasibility)
        round_number = ((int(datetime(2026, 8, 14, tzinfo=timezone.utc).timestamp()) - C0.LEGACY_GENESIS) // 30) + 1
        self.config = {
            "schema_version": C0.CONFIG_VERSION,
            "p0a": self.refs["p0a"], "p0t": self.refs["p0t"], "s0": self.refs["s0"],
            "eligible_pool": self.refs["eligible_pool"], "quota_feasibility": self.refs["quota_feasibility"],
            "selector_artifacts": {name: self.refs[name] for name in C0.SELECTOR.ARTIFACT_KEYS},
            "protocol_components": self.component_refs, "future_drand_round": round_number,
        }
        self.config_path = self.root / "config.json"

    def tearDown(self):
        self.temp.cleanup()

    def build(self):
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        with mock.patch.object(C0.P0, "validate_p0a", return_value=None), mock.patch.object(C0.P0, "validate_p0t", return_value=None):
            return C0.assemble_c0a(self.config_path)

    def test_c0a_replays_gate_and_binds_every_exact_hash(self):
        c0a = self.build()
        self.assertEqual(set(c0a["bindings"]["selector_artifacts"]), set(C0.SELECTOR.ARTIFACT_KEYS))
        self.assertEqual(set(c0a["bindings"]["protocol_components"]), set(C0.P0.REQUIRED_COMPONENTS))
        self.assertEqual(c0a["bindings"]["selection_algorithm"]["name"], "UNBIASED_DOMAIN_SEPARATED_SHA256_FISHER_YATES")
        self.assertFalse(c0a["entropy_used"])
        self.assertEqual(c0a["selected_clusters"], [])
        self.assertIsNone(c0a["randomness"]["value"])
        self.assertEqual(c0a["randomness"]["round_closes_at_utc"], C0.close_time(c0a["randomness"]["round"]))

    def test_failed_feasibility_cannot_enter_c0(self):
        path = C0.repo_path(self.refs["quota_feasibility"]["path"])
        value = json.loads(path.read_text()); value["status"] = "FAIL"
        value["certificate_sha256"] = C0.SELECTOR.object_digest(value, "certificate_sha256")
        path.write_text(json.dumps(value)); self.config["quota_feasibility"]["sha256"] = digest(path)
        with self.assertRaisesRegex(C0.C0Error, "not PASS"):
            self.build()

    def test_c0a_rejects_entropy_selection_or_wrong_derived_close(self):
        value = self.build(); value["selected_clusters"] = [{"forbidden": True}]
        with self.assertRaises(C0.C0Error): C0.validate_c0a(value, authenticate_bindings=False)
        value = self.build(); value["randomness"]["round_closes_at_utc"] = "2026-08-14T00:00:01Z"
        with self.assertRaisesRegex(C0.C0Error, "legacy genesis"):
            C0.validate_c0a(value, authenticate_bindings=False)

    def test_c0t_is_future_and_selector_compatible(self):
        c0a = self.build(); path = self.root / "c0a.json"; C0.write_json(path, c0a)
        relative = (self.root / "c0t.json").relative_to(C0.ROOT).as_posix()
        observed = "2026-08-13T03:00:00Z"
        with mock.patch.object(C0, "commit_file", return_value=path.read_bytes()), mock.patch.object(C0.P0, "validate_p0a", return_value=None), mock.patch.object(C0.P0, "validate_p0t", return_value=None):
            c0t = C0.assemble_c0t(path, "9" * 40, observed, relative)
            C0.validate_c0t(c0t)
        self.assertIsNone(c0t["chronology"]["c0_attestation_commit"])
        self.assertEqual(c0t["schema_version"], C0.SELECTOR.C0_SCHEMA_VERSION)
        feasibility = json.loads(C0.repo_path(self.refs["quota_feasibility"]["path"]).read_text())
        randomness = {
            "schema_version": C0.SELECTOR.RANDOMNESS_SCHEMA_VERSION,
            "round": c0t["randomness"]["round"],
            "c0_binding": {
                "artifact_commit": "9" * 40, "attestation_commit": "a" * 40,
                "published_at_utc": observed,
            },
            "round_closes_at_utc": c0t["randomness"]["round_closes_at_utc"],
            "chain": {"hash": C0.LEGACY_CHAIN_HASH},
            "retrieval": {"retrieved_at_utc": c0t["randomness"]["round_closes_at_utc"]},
            "verification": {name: True for name in (
                "exact_round", "official_relay_equality", "frozen_chain_info",
                "bls_signature", "randomness_equals_sha256_signature",
            )},
            "randomness": "b" * 64,
            "randomness_sha256": hashlib.sha256(("b" * 64).encode()).hexdigest(),
            "beacon": {
                "round": c0t["randomness"]["round"], "randomness": "b" * 64,
                "signature": "00" * 96,
            },
        }
        c0t_raw = json.dumps(c0t).encode()
        receipt = {
            "schema_version": "c5k4-c0-validation-receipt-1.3",
            "c0t": {"path": relative, "file_sha256": C0.sha256(c0t_raw)},
            "c0_artifact_commit": "9" * 40, "c0_attestation_commit": "a" * 40,
            "direct_nonmerge_parent_verified": True, "changed_paths": [relative],
            "committed_bytes_verified": True,
            "publication_observation": c0t["publication_observation"],
            "c0_published_at_utc": observed,
            "future_round_close_at_utc": c0t["randomness"]["round_closes_at_utc"],
        }
        receipt["receipt_sha256"] = C0.SELECTOR.object_digest(receipt, "receipt_sha256")
        # The selector accepts the exact C0T bytes plus content-addressed live
        # validation receipt, then reaches the deliberately bad signature.
        with self.assertRaisesRegex(ValueError, "SHA256\(signature\)"):
            C0.SELECTOR.validate_future_entropy(
                C0.repo_path(self.refs["eligible_pool"]["path"]).read_bytes(),
                feasibility, c0t_raw, json.dumps(receipt).encode(),
                json.dumps(randomness).encode(),
            )

    def test_c0t_rejects_nonfuture_publication(self):
        c0a = self.build(); path = self.root / "c0a.json"; C0.write_json(path, c0a)
        with mock.patch.object(C0, "commit_file", return_value=path.read_bytes()), mock.patch.object(C0.P0, "validate_p0a", return_value=None), mock.patch.object(C0.P0, "validate_p0t", return_value=None):
            with self.assertRaisesRegex(C0.C0Error, "precede the frozen round"):
                C0.assemble_c0t(path, "9" * 40, c0a["randomness"]["round_closes_at_utc"], "c0t.json")

    def test_committed_c0t_must_be_direct_nonmerge_single_path(self):
        c0a = self.build(); a = self.root / "c0a.json"; C0.write_json(a, c0a)
        t = self.root / "c0t.json"; relative = t.relative_to(C0.ROOT).as_posix()
        with mock.patch.object(C0, "commit_file", return_value=a.read_bytes()), mock.patch.object(C0.P0, "validate_p0a", return_value=None), mock.patch.object(C0.P0, "validate_p0t", return_value=None):
            c0t = C0.assemble_c0t(a, "9" * 40, "2026-08-13T03:00:00Z", relative)
        C0.write_json(t, c0t)
        def fake_git(*args):
            if args == ("rev-parse", "a" * 40): return ("a" * 40 + "\n").encode()
            if args[:3] == ("show", "-s", "--format=%P"): return ("9" * 40 + "\n").encode()
            if args[:4] == ("diff-tree", "--no-commit-id", "--name-only", "-r"): return (relative + "\n").encode()
            raise AssertionError(args)
        def fake_file(commit, path): return a.read_bytes() if commit == "9" * 40 else t.read_bytes()
        with mock.patch.object(C0, "git", side_effect=fake_git), mock.patch.object(C0, "commit_file", side_effect=fake_file), mock.patch.object(C0.P0, "validate_p0a", return_value=None), mock.patch.object(C0.P0, "validate_p0t", return_value=None):
            C0.validate_c0t(c0t, c0t_commit="a" * 40, artifact_path=t)
            receipt = C0.validation_receipt(c0t, "a" * 40, t)
        self.assertEqual(receipt["c0_attestation_commit"], "a" * 40)
        self.assertEqual(receipt["c0t"]["file_sha256"], digest(t))
        self.assertEqual(
            receipt["receipt_sha256"],
            C0.sha256(C0.canonical_json({k: v for k, v in receipt.items() if k != "receipt_sha256"})),
        )

    def test_protocol_component_drift_fails_closed(self):
        role = "scoring_rule"
        path = C0.repo_path(self.component_refs[role]["path"]); path.write_text("drift")
        self.config["protocol_components"][role]["sha256"] = digest(path)
        with self.assertRaisesRegex(C0.C0Error, "differs from P0A"):
            self.build()


if __name__ == "__main__": unittest.main()
