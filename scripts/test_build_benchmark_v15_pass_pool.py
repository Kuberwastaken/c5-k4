#!/usr/bin/env python3
"""Adversarial offline tests for the Method v1.5 pre-entropy PASS pool."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("build_benchmark_v15_pass_pool.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v15_pass_pool", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)

AGG_TEST_SCRIPT = Path(__file__).with_name(
    "test_build_benchmark_v15_aggregate_certificate.py"
)
AGG_SPEC = importlib.util.spec_from_file_location(
    "benchmark_v15_aggregate_fixture", AGG_TEST_SCRIPT,
)
assert AGG_SPEC is not None and AGG_SPEC.loader is not None
AF = importlib.util.module_from_spec(AGG_SPEC)
AGG_SPEC.loader.exec_module(AF)


class PassPoolTests(unittest.TestCase):
    def activation(self) -> dict:
        value = {
            "schema": P.public_chain.P1R_RECEIPT_DOMAIN.decode(),
            "p1r": {"path": P.public_chain.P1R_PATH, "sha256": "7" * 64},
            "p1r_commit": self.p1r_commit,
            "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
            "public_observation": {
                "workflow_repository": "Kuberwastaken/c5-k4",
                "workflow_path": ".github/workflows/method-v15-p1r-publication-observer.yml",
                "workflow_blob_sha256": "4" * 64,
                "workflow_ref": ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r",
                "run_id": 1, "run_attempt": 1,
                "server_observed_at_utc": "2026-08-16T19:00:00Z",
                "actions_run_projection_sha256": "5" * 64,
            },
            "validation_inputs_sha256": "6" * 64,
            "validation_diagnostic_sha256": "9" * 64,
            "validator": {"path": "scripts/validate_benchmark_v15_candidate_base.py", "sha256": "a" * 64},
        }
        value["receipt_sha256"] = P.sha256_bytes(
            P.public_chain.P1R_RECEIPT_DOMAIN + b"\0" + P.canonical_json(value)
        )
        return value

    def setUp(self) -> None:
        self.source = AF.AggregateCertificateTests(
            "test_pass_certificate_is_aggregate_only_and_pool_is_separate"
        )
        self.source.setUp()
        self.root = self.source.root
        self.p1t_commit = self.source.commit
        self.p1r_commit = self.source.commit
        self.genesis_commit = "b" * 40
        self.pass_commit = "c" * 40
        self.prior_proof_path = self.write("prior-proof.json", self.prior_proof())

        chronology = self.source.chronology()
        chronology["basis"] = {
            "u1_receipt": {
                "path": "u1/chronology-receipt.json",
                "sha256": "8" * 64,
                "commit": self.source.commit,
                "publication_commit": self.genesis_commit,
                "p1r_commit": self.p1r_commit,
                "p1r_activation_sha256": P.sha256_bytes(P.canonical_json(self.activation())),
                "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
            },
            "previous_checkpoint": None,
            "public_chain_proof": {
                "sha256": P.sha256_file(self.prior_proof_path),
                "proof_sha256": self.prior_proof()["proof_sha256"],
                "public_tip_commit": self.genesis_commit,
            },
        }
        self.source.chronology_path.write_text(
            json.dumps(chronology, sort_keys=True) + "\n", encoding="utf-8"
        )
        registry = self.source.registry()
        registry["quota_certificate"]["prior_checkpoint_chain_sha256"] = self.prior_proof()["proof_sha256"]
        self.source.resign_registry(registry)
        self.source.registry_path.write_text(
            json.dumps(registry, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.certificate = self.source.build()
        self.certificate_path = self.write("certificate.json", self.certificate)
        self.registry = json.loads(self.source.registry_path.read_text(encoding="utf-8"))
        self.attestation = self.replay_attestation()
        self.attestation_path = self.write("attestation.json", self.attestation)
        self.receipt = self.pass_receipt()
        self.receipt_path = self.write("pass-receipt.json", self.receipt)
        self.pass_proof = self.final_proof()
        self.pass_proof_path = self.write("pass-proof.json", self.pass_proof)

    def tearDown(self) -> None:
        self.source.tearDown()

    def write(self, name: str, value: dict) -> Path:
        path = self.root / name
        path.write_bytes(P.canonical_json(value))
        return path

    def prior_proof(self) -> dict:
        proof = {
            "schema": P.public_chain.PROOF_SCHEMA,
            "repository": P.public_chain.PUBLIC_REPOSITORY,
            "ref": P.public_chain.PUBLICATION_REF,
            "p1r_commit": self.p1r_commit,
            "p1r_activation": self.activation(),
            "p1r_activation_sha256": P.sha256_bytes(P.canonical_json(self.activation())),
            "public_tip_commit": self.genesis_commit,
            "genesis": {
                "commit": self.genesis_commit,
                "parent_commit": self.p1r_commit,
                "u1_path": P.public_chain.U1_PATH,
                "u1_blob_sha256": "8" * 64,
            },
            "checkpoint_count": 0,
            "checkpoints": [],
            "previous_checkpoint": None,
            "next_checkpoint": {
                "ordinal": 1,
                "scheduled_for_utc": "2026-08-17T00:17:00Z",
                "required_parent_commit": self.genesis_commit,
            },
            "terminal": False,
            "normal_push_must_use_lease_tip": self.genesis_commit,
        }
        proof["proof_sha256"] = P.public_chain.proof_digest(proof)
        return proof

    def replay_attestation(self) -> dict:
        upstream = self.certificate["upstream"]
        value = {
            "schema": "c5k4-method-v1.5-scheduled-replay-attestation-1.0",
            "status": "INDEPENDENT_EXACT_REPLAY_PASS",
            "certificate_sha256": self.certificate["certificate_sha256"],
            "chronology_receipt_sha256": self.certificate["chronology"]["receipt"]["sha256"],
            "private_registry_sha256": P.sha256_file(self.source.registry_path),
            "registry_unsigned_projection_sha256": self.registry["registry_sha256"],
            "upstream": {
                key: upstream[key]
                for key in ("commit", "root_tree", "formal_conjectures_tree")
            },
            "verifier": {
                "path": "scripts/build_benchmark_v15_aggregate_certificate.py",
                "sha256": P.sha256_file(
                    P.ROOT / "scripts/build_benchmark_v15_aggregate_certificate.py"
                ),
            },
        }
        value["attestation_sha256"] = P.aggregate.attestation_digest(value)
        return value

    def pass_receipt(self) -> dict:
        upstream = self.certificate["upstream"]
        return {
            "schema": "c5k4-method-v1.5-chronology-receipt-1.0",
            "artifact_kind": "CHECKPOINT_RECEIPT",
            "protocol_version": "1.5",
            "chronology_rule": {"path": "rule", "sha256": "7" * 64},
            "checkpoint_ordinal": 1,
            "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "basis": {
                "u1_receipt": {
                    "path": "u1/chronology-receipt.json",
                    "sha256": "8" * 64,
                    "commit": self.registry["upstream"]["u1_commit"],
                    "publication_commit": self.genesis_commit,
                    "p1r_commit": self.p1r_commit,
                    "p1r_activation_sha256": P.sha256_bytes(P.canonical_json(self.activation())),
                    "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
                },
                "previous_checkpoint": None,
                "public_chain_proof": {
                    "sha256": P.sha256_file(self.prior_proof_path),
                    "proof_sha256": self.prior_proof()["proof_sha256"],
                    "public_tip_commit": self.genesis_commit,
                },
            },
            "capture": {
                "path": self.certificate["chronology"]["receipt"]["path"],
                "sha256": self.certificate["chronology"]["receipt"]["sha256"],
                "commit": upstream["commit"],
                "root_tree": upstream["root_tree"],
                "formal_conjectures_tree": upstream["formal_conjectures_tree"],
            },
            "quota_certificate": {
                **P.aggregate.relative_ref(self.certificate_path, "aggregate certificate"),
                "certificate_sha256": self.certificate["certificate_sha256"],
                "aggregates": self.certificate["aggregates"],
            },
            "replay_attestation": {
                **P.aggregate.relative_ref(self.attestation_path, "replay attestation"),
                "attestation_sha256": self.attestation["attestation_sha256"],
            },
            "terminal_horizon": False,
            "u2": {
                "commit": upstream["commit"],
                "root_tree": upstream["root_tree"],
                "formal_conjectures_tree": upstream["formal_conjectures_tree"],
                "u1_is_ancestor": True,
                "membership_interval": self.registry["upstream"]["ancestry_interval"],
            },
            "status": "QUOTA_PASS_U2",
        }

    def final_proof(self) -> dict:
        prior = json.loads(self.prior_proof_path.read_text(encoding="utf-8"))
        row = {
            "ordinal": 1,
            "scheduled_for_utc": "2026-08-17T00:17:00Z",
            "status": "QUOTA_PASS_U2",
            "commit": self.pass_commit,
            "parent_commit": prior["public_tip_commit"],
            "receipt_path": "checkpoints/2026-08-17T00-17-00Z/receipt.json",
            "receipt_blob_sha256": P.sha256_file(self.receipt_path),
        }
        proof = {
            "schema": P.public_chain.PROOF_SCHEMA,
            "repository": P.public_chain.PUBLIC_REPOSITORY,
            "ref": P.public_chain.PUBLICATION_REF,
            "p1r_commit": self.p1r_commit,
            "p1r_activation": prior["p1r_activation"],
            "p1r_activation_sha256": prior["p1r_activation_sha256"],
            "public_tip_commit": self.pass_commit,
            "genesis": prior["genesis"],
            "checkpoint_count": 1,
            "checkpoints": [row],
            "previous_checkpoint": row,
            "next_checkpoint": None,
            "terminal": True,
            "normal_push_must_use_lease_tip": self.pass_commit,
        }
        proof["proof_sha256"] = P.public_chain.proof_digest(proof)
        return proof

    def build(self, *, auth_binding: dict | None = None, replayed: dict | None = None) -> dict:
        binding = self.certificate["p1_binding"] if auth_binding is None else auth_binding
        final = self.pass_proof if replayed is None else replayed
        with mock.patch.object(
            P.aggregate, "authenticate_p1", return_value=({}, {}, {}, binding)
        ), mock.patch.object(P.public_chain, "verify_chain", return_value=final):
            return P.build_pool(
                self.source.registry_path,
                self.certificate_path,
                self.attestation_path,
                self.receipt_path,
                self.prior_proof_path,
                self.pass_proof_path,
                self.source.manifest_path,
                self.source.manifest_path,
                self.source.manifest_path,
                self.source.repo,
            )

    def resign_pool(self, value: dict) -> dict:
        value["pool_sha256"] = P.pool_digest(value)
        return value

    def test_builds_complete_target_blind_embeddable_pool(self) -> None:
        pool = self.build()
        P.validate_pool(pool)
        self.assertEqual(len(pool["clusters"]), 12)
        self.assertEqual(pool["replay"]["eligible_by_stratum"], P.QUOTAS)
        self.assertEqual(pool["replay"]["deficits"], {key: 0 for key in P.STRATA})
        self.assertFalse(pool["publication_boundary"]["standalone_publication_claimed"])
        self.assertTrue(pool["publication_boundary"]["c0a_embedding_required"])
        self.assertFalse(pool["selection_contract"]["selection_permitted"])
        self.assertEqual(
            set(pool["clusters"][0]),
            {"cluster_id", "identity_sha256", "stratum", "eligible"},
        )
        serialized = P.canonical_json(pool).decode()
        for forbidden in (
            "FormalConjectures/Fixture", "fixture0", "declarations",
            "statement_header_sha256", "module_blob_sha256", "classification_basis",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_canonical_object_and_file_bytes_are_stable(self) -> None:
        first = self.build()
        second = self.build()
        self.assertEqual(P.canonical_json(first), P.canonical_json(second))
        one = self.root / "pool-one.json"
        two = self.root / "pool-two.json"
        P.write_json(one, first)
        P.write_json(two, second)
        self.assertEqual(one.read_bytes(), P.canonical_json(first))
        self.assertEqual(one.read_bytes(), two.read_bytes())
        self.assertEqual(first["pool_sha256"], P.pool_digest(first))

    def test_schema_rejects_semantic_outcome_ranking_entropy_and_selection_payloads(self) -> None:
        base = self.build()
        for key in (
            "statement_text", "target_semantics", "outcomes", "ranking",
            "entropy", "selection", "publication_commit",
        ):
            bad = copy.deepcopy(base)
            bad[key] = "forbidden"
            self.resign_pool(bad)
            with self.assertRaises(P.PassPoolError, msg=key):
                P.validate_pool(bad)
        bad = copy.deepcopy(base)
        bad["clusters"][0]["statement_text"] = "False"
        self.resign_pool(bad)
        with self.assertRaises(P.PassPoolError):
            P.validate_pool(bad)

    def test_incomplete_duplicate_unsorted_and_count_tampering_fail(self) -> None:
        base = self.build()
        bad = copy.deepcopy(base)
        bad["clusters"].pop()
        self.resign_pool(bad)
        with self.assertRaises(P.PassPoolError):
            P.validate_pool(bad)
        bad = copy.deepcopy(base)
        bad["clusters"][1]["identity_sha256"] = bad["clusters"][0]["identity_sha256"]
        self.resign_pool(bad)
        with self.assertRaisesRegex(P.PassPoolError, "repeats|order"):
            P.validate_pool(bad)
        bad = copy.deepcopy(base)
        bad["clusters"][0], bad["clusters"][1] = bad["clusters"][1], bad["clusters"][0]
        self.resign_pool(bad)
        with self.assertRaisesRegex(P.PassPoolError, "canonical"):
            P.validate_pool(bad)
        bad = copy.deepcopy(base)
        bad["replay"]["candidate_count"] += 1
        self.resign_pool(bad)
        with self.assertRaisesRegex(P.PassPoolError, "counts"):
            P.validate_pool(bad)

    def test_private_registry_exact_bytes_and_independent_replay_are_required(self) -> None:
        original = self.source.registry_path.read_bytes()
        self.source.registry_path.write_bytes(original + b" ")
        with self.assertRaisesRegex(P.PassPoolError, "bytes"):
            self.build()
        self.source.registry_path.write_bytes(original)
        bad_attestation = copy.deepcopy(self.attestation)
        bad_attestation["private_registry_sha256"] = "0" * 64
        bad_attestation["attestation_sha256"] = P.aggregate.attestation_digest(bad_attestation)
        self.attestation_path.write_bytes(P.canonical_json(bad_attestation))
        with self.assertRaisesRegex(P.PassPoolError, "registry/certificate/U2"):
            self.build()

    def test_private_runtime_inputs_may_live_outside_repository_without_locator_leak(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c5k4-v15-private-") as external:
            external_root = Path(external).resolve()
            self.assertFalse(external_root.is_relative_to(P.ROOT))
            registry_path = external_root / "private-registry.json"
            attestation_path = external_root / "replay-attestation.json"
            registry_path.write_bytes(self.source.registry_path.read_bytes())
            attestation_path.write_bytes(self.attestation_path.read_bytes())
            with mock.patch.object(
                P.aggregate, "authenticate_p1",
                return_value=({}, {}, {}, self.certificate["p1_binding"]),
            ), mock.patch.object(
                P.public_chain, "verify_chain", return_value=self.pass_proof,
            ):
                pool = P.build_pool(
                    registry_path,
                    self.certificate_path,
                    attestation_path,
                    self.receipt_path,
                    self.prior_proof_path,
                    self.pass_proof_path,
                    self.source.manifest_path,
                    self.source.manifest_path,
                    self.source.manifest_path,
                    self.source.repo,
                )
        serialized = P.canonical_json(pool).decode()
        self.assertNotIn(str(external_root), serialized)
        self.assertEqual(
            set(pool["source_bindings"]["private_registry"]),
            {"role", "file_sha256", "registry_sha256"},
        )
        self.assertEqual(
            set(pool["source_bindings"]["replay_attestation"]),
            {"role", "file_sha256", "attestation_sha256"},
        )

    def test_exact_p1_binding_is_reauthenticated(self) -> None:
        wrong = copy.deepcopy(self.certificate["p1_binding"])
        wrong["p1t_commit"] = "0" * 40
        with self.assertRaisesRegex(P.PassPoolError, "exact P1A/P1T"):
            self.build(auth_binding=wrong)

    def test_pre_pass_proof_must_be_all_fail_and_exact_receipt_basis(self) -> None:
        prior = json.loads(self.prior_proof_path.read_text(encoding="utf-8"))
        prior["next_checkpoint"]["ordinal"] = 2
        prior["proof_sha256"] = P.public_chain.proof_digest(prior)
        self.prior_proof_path.write_bytes(P.canonical_json(prior))
        with self.assertRaisesRegex(P.PassPoolError, "pre-pass|different pre-pass"):
            self.build()

    def test_final_proof_must_replay_public_ref_and_add_exact_pass_receipt(self) -> None:
        forged = copy.deepcopy(self.pass_proof)
        forged["checkpoints"][0]["status"] = "QUOTA_FAIL"
        forged["previous_checkpoint"] = forged["checkpoints"][0]
        forged["proof_sha256"] = P.public_chain.proof_digest(forged)
        self.pass_proof_path.write_bytes(P.canonical_json(forged))
        with self.assertRaisesRegex(P.PassPoolError, "QUOTA_PASS_U2"):
            self.build(replayed=forged)
        self.pass_proof_path.write_bytes(P.canonical_json(self.pass_proof))
        replayed_other = copy.deepcopy(self.pass_proof)
        replayed_other["checkpoints"][0]["receipt_blob_sha256"] = "0" * 64
        replayed_other["previous_checkpoint"] = replayed_other["checkpoints"][0]
        replayed_other["proof_sha256"] = P.public_chain.proof_digest(replayed_other)
        with self.assertRaisesRegex(P.PassPoolError, "differs from replay"):
            self.build(replayed=replayed_other)

    def test_nonpass_aggregate_cannot_create_pool(self) -> None:
        failed = copy.deepcopy(self.certificate)
        counts = copy.deepcopy(failed["aggregates"]["eligible_by_stratum"])
        counts["GRAPH_SCALAR_INEQUALITY"] = 2
        failed["aggregates"].update({
            "eligible_by_stratum": counts,
            "deficits": {
                key: max(0, P.QUOTAS[key] - counts[key]) for key in P.STRATA
            },
            "candidate_count": sum(counts.values()),
            "status": "FAIL",
        })
        failed["certificate_sha256"] = P.aggregate.unsigned_digest(failed)
        self.certificate_path.write_bytes(P.canonical_json(failed))
        with self.assertRaisesRegex(P.PassPoolError, "quota PASS"):
            self.build()


if __name__ == "__main__":
    unittest.main()
