#!/usr/bin/env python3
"""Adversarial offline tests for the v1.5 aggregate publication boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_benchmark_v15_aggregate_certificate.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v15_aggregate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
A = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A)
H = "a" * 64


class AggregateCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = A.ROOT / "results" / "benchmark"
        self.temp = tempfile.TemporaryDirectory(prefix="v1.5-aggregate-test-", dir=parent)
        self.root = Path(self.temp.name)
        self.repo = self.root / "isolated-upstream"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.invalid"], check=True)
        (self.repo / "FormalConjectures").mkdir()
        (self.repo / "FormalConjectures" / "Fixture.lean").write_text("theorem fixture : True := by trivial\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "FormalConjectures/Fixture.lean"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "fixture"], check=True)
        self.commit = self.git("rev-parse", "HEAD")
        self.tree = self.git("rev-parse", "HEAD^{tree}")
        self.formal_tree = self.git("rev-parse", "HEAD:FormalConjectures")
        self.chronology_path = self.write("chronology.json", self.chronology())
        self.registry_path = self.write("private-registry.json", self.registry())
        self.manifest_path = self.write("components.json", self.manifest())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True,
            stdout=subprocess.PIPE, text=True,
        ).stdout.strip()

    def write(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def chronology(self) -> dict:
        return {
            "schema": "c5k4-method-v1.5-chronology-receipt-1.0",
            "artifact_kind": "CHECKPOINT_CAPTURE",
            "protocol_version": "1.5",
            "checkpoint_ordinal": 1,
            "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "trigger": {"event_name": "schedule", "run_attempt": 1},
            "basis": {
                "u1_receipt": {"commit": self.commit, "path": "u1.json", "sha256": H},
                "previous_checkpoint": None,
            },
            "upstream": {
                "repository": A.UPSTREAM_REPOSITORY,
                "ref": A.UPSTREAM_REF,
                "commit": self.commit,
                "root_tree": self.tree,
                "formal_conjectures_tree": self.formal_tree,
            },
            "status": "AWAITING_MACHINE_QUOTA_CERTIFICATE",
        }

    def record(self, index: int, stratum: str) -> dict:
        return {
            "cluster_id": f"private:fixture-{index}",
            "identity_sha256": f"{index + 1:064x}",
            "path": f"FormalConjectures/Fixture{index}.lean",
            "module_blob_sha256": H,
            "declarations": [{
                "name": f"fixture{index}", "kind": "theorem", "category_line": 1,
                "statement_header_sha256": H,
            }],
            "machine_stratum": stratum,
            "classification_basis": "TYPE_SHAPE",
            "first_introduction_commit": self.commit,
            "first_introduction_tree": self.tree,
            "membership_status": "INCLUDE",
            "exclusion_reasons": [],
        }

    def registry(self) -> dict:
        sequence = [key for key, quota in A.QUOTAS.items() for _ in range(quota)]
        records = [self.record(index, stratum) for index, stratum in enumerate(sequence)]
        counts = dict(A.QUOTAS)
        prior = A.sha256_bytes(A.canonical_json({"authority": "V15_CHECKPOINT_CHAIN_GENESIS", "u1_commit": self.commit}))
        registry = {
            "schema_version": "c5k4-future-cohort-registry-1.5",
            "authority": "SCHEDULED_IDENTITY_ONLY_CHECKPOINT",
            "upstream": {
                "repository": A.UPSTREAM_REPOSITORY,
                "u1_commit": self.commit, "u1_tree": self.tree,
                "u2_commit": self.commit, "u2_tree": self.tree,
                "ancestry_interval": f"{self.commit}..{self.commit}",
            },
            "inputs": {"chronology_receipt_sha256": H},
            "controls": {
                "statement_text_present": False, "outcomes_present": False,
                "ranking_present": False, "entropy_used": False,
                "selection_permitted": False,
                "first_introduction_basis": "GIT_ANCESTRY_AND_TREE_CONTENT",
                "v14_exclusion_cluster_count": 728,
            },
            "counts": {
                "u1_open_clusters": 0, "u2_open_clusters": len(records),
                "delta_records": len(records), "included": len(records), "excluded": 0,
                "eligible_by_stratum": counts, "exclusion_reasons": {},
            },
            "quota_certificate": {
                "checkpoint_ordinal": 1, "checkpoint_label": "checkpoint-2026-08-17",
                "commit": self.commit, "tree": self.tree,
                "quotas": dict(A.QUOTAS), "eligible_by_stratum": counts,
                "deficits": {key: 0 for key in A.STRATA}, "status": "PASS",
                "candidate_count": len(records), "prior_checkpoint_chain_sha256": prior,
                "all_prior_valid_checkpoints_failed": True,
                "first_passing_checkpoint": True, "registry_sha256": H,
            },
            "records": records,
            "registry_sha256": H,
        }
        digest = A.future_registry.registry_digest(registry)
        registry["quota_certificate"]["registry_sha256"] = digest
        registry["registry_sha256"] = digest
        return registry

    def manifest(self) -> dict:
        registry_executable = "scripts/build_benchmark_v15_future_cohort.py"
        registry_policy = "results/benchmark/v1.5-protocol/future-cohort-rule.json"
        registry_schema = "schemas/benchmark-future-registry-output-v1.5.schema.json"
        return {
            "registry": {
                "executable": registry_executable,
                "policy": registry_policy,
                "schema": registry_schema,
                "invocation_contract": "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json",
            },
            "classifier": {
                "executable": registry_executable,
                "policy": registry_policy,
                "schema": registry_schema,
            },
            "grouping": {
                "executable": registry_executable,
                "policy": registry_policy,
                "schema": registry_schema,
            },
            "provenance": {
                "executable": "scripts/classify_benchmark_provenance_v15.py",
                "policy": "results/benchmark/v1.5-protocol/provenance-ontology.json",
                "schema": "schemas/benchmark-provenance-ledger-v1.5.schema.json",
                "source_ledger": "schemas/benchmark-provenance-ledger-v1.5.schema.json",
            },
        }

    def build(self) -> dict:
        return A.build_certificate(self.chronology_path, self.registry_path, self.manifest_path)

    def resign(self, certificate: dict) -> dict:
        certificate["certificate_sha256"] = A.unsigned_digest(certificate)
        return certificate

    def resign_registry(self, registry: dict) -> dict:
        digest = A.future_registry.registry_digest(registry)
        registry["quota_certificate"]["registry_sha256"] = digest
        registry["registry_sha256"] = digest
        return registry

    def test_pass_certificate_is_aggregate_only_and_pool_is_separate(self) -> None:
        certificate = self.build()
        A.validate_certificate(certificate)
        self.assertEqual(certificate["aggregates"]["eligible_by_stratum"], A.QUOTAS)
        self.assertEqual(certificate["aggregates"]["status"], "PASS")
        self.assertEqual(certificate["sealed_replay"]["pass_pool_publication"], "SEPARATE_PRE_ENTROPY_ARTIFACT")
        self.assertFalse(certificate["sealed_replay"]["generic_generated_artifact_verifier_authoritative"])
        serialized = json.dumps(certificate, sort_keys=True)
        for forbidden in ("cluster_id", "declarations", "membership_status", "FormalConjectures/Fixture0"):
            self.assertNotIn(forbidden, serialized)

    def test_fail_certificate_publishes_exact_five_counts_and_no_identities(self) -> None:
        registry = self.registry()
        registry["records"] = registry["records"][:1]
        counts = {key: int(key == "GRAPH_SCALAR_INEQUALITY") for key in A.STRATA}
        deficits = {key: max(0, A.QUOTAS[key] - counts[key]) for key in A.STRATA}
        registry["counts"].update(delta_records=1, included=1, eligible_by_stratum=counts)
        registry["quota_certificate"].update(
            eligible_by_stratum=counts, deficits=deficits, status="FAIL",
            candidate_count=1, first_passing_checkpoint=False,
        )
        self.resign_registry(registry)
        self.registry_path.write_text(json.dumps(registry) + "\n")
        certificate = self.build()
        self.assertEqual(certificate["aggregates"]["status"], "FAIL")
        self.assertEqual(set(certificate["aggregates"]["eligible_by_stratum"]), set(A.STRATA))
        self.assertEqual(certificate["publication_boundary"]["failed_checkpoint_publication"], "CERTIFICATE_AND_CHRONOLOGY_RECEIPT_ONLY")
        self.assertNotIn("records", certificate)

    def test_schema_rejects_identity_statement_outcome_ranking_and_entropy_fields(self) -> None:
        base = self.build()
        for key in ("records", "cluster_id", "statement", "outcomes", "ranking", "entropy"):
            bad = copy.deepcopy(base)
            bad[key] = []
            self.resign(bad)
            with self.assertRaises(A.CertificateError, msg=key):
                A.validate_certificate(bad)

    def test_tampered_counts_deficits_status_and_self_digest_fail(self) -> None:
        base = self.build()
        bad = copy.deepcopy(base)
        bad["aggregates"]["candidate_count"] += 1
        self.resign(bad)
        with self.assertRaisesRegex(A.CertificateError, "candidate count"):
            A.validate_certificate(bad)
        bad = copy.deepcopy(base)
        bad["aggregates"]["deficits"]["GRAPH_SCALAR_INEQUALITY"] = 1
        self.resign(bad)
        with self.assertRaisesRegex(A.CertificateError, "deficits"):
            A.validate_certificate(bad)
        bad = copy.deepcopy(base)
        bad["certificate_sha256"] = "0" * 64
        with self.assertRaisesRegex(A.CertificateError, "self-digest"):
            A.validate_certificate(bad)

    def test_manual_rerun_wrong_tip_and_inconsistent_private_counts_fail(self) -> None:
        chronology = self.chronology()
        chronology["trigger"]["event_name"] = "workflow_dispatch"
        self.chronology_path.write_text(json.dumps(chronology) + "\n")
        with self.assertRaisesRegex(A.CertificateError, "Manual|reruns|manual"):
            self.build()
        self.chronology_path.write_text(json.dumps(self.chronology()) + "\n")
        registry = self.registry()
        registry["quota_certificate"]["candidate_count"] = 99
        self.resign_registry(registry)
        self.registry_path.write_text(json.dumps(registry) + "\n")
        with self.assertRaisesRegex(A.CertificateError, "record-derived"):
            self.build()

    def test_exact_byte_isolated_replay_passes_and_cached_or_wrong_tree_fails(self) -> None:
        certificate = self.build()
        attestation = A.replay_certificate(certificate, self.chronology_path, self.registry_path, self.repo)
        A.validate_schema(attestation, A.ATTESTATION_SCHEMA_PATH, "replay attestation")
        self.assertEqual(attestation["certificate_sha256"], certificate["certificate_sha256"])
        self.assertEqual(attestation["private_registry_sha256"], A.sha256_file(self.registry_path))
        bad_attestation = copy.deepcopy(attestation)
        bad_attestation["certificate_sha256"] = "0" * 64
        self.assertNotEqual(
            bad_attestation["attestation_sha256"], A.attestation_digest(bad_attestation)
        )
        tampered = self.root / "tampered-registry.json"
        tampered.write_bytes(self.registry_path.read_bytes() + b" ")
        with self.assertRaisesRegex(A.CertificateError, "exact-byte deterministic"):
            A.replay_certificate(certificate, self.chronology_path, tampered, self.repo)
        bad = copy.deepcopy(certificate)
        bad["upstream"]["formal_conjectures_tree"] = "0" * 40
        self.resign(bad)
        with self.assertRaisesRegex(A.CertificateError, "FormalConjectures tree"):
            A.replay_certificate(bad, self.chronology_path, self.registry_path, self.repo)

    def test_registry_unsigned_projection_mutation_is_rejected(self) -> None:
        registry = self.registry()
        registry["counts"]["u1_open_clusters"] += 1
        self.registry_path.write_text(json.dumps(registry) + "\n")
        with self.assertRaisesRegex(A.CertificateError, "unsigned projection"):
            self.build()

    def test_component_and_chronology_bindings_are_exact(self) -> None:
        certificate = self.build()
        bad = copy.deepcopy(certificate)
        bad["frozen_components"]["registry"]["executable"]["sha256"] = "0" * 64
        self.resign(bad)
        with self.assertRaisesRegex(A.CertificateError, "registry.executable bytes"):
            A.replay_certificate(bad, self.chronology_path, self.registry_path, self.repo)
        other = self.write("other-chronology.json", self.chronology())
        with self.assertRaisesRegex(A.CertificateError, "path differs"):
            A.replay_certificate(certificate, other, self.registry_path, self.repo)


if __name__ == "__main__":
    unittest.main()
