#!/usr/bin/env python3
"""Tests for the strict Method v1.5 P1 assembler and attestation boundary."""

from __future__ import annotations

import copy
import base64
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("build_benchmark_v15_p1.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v15_p1", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
P1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P1)


class P1Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="c5k4-v15-p1-test-")
        self.root = Path(self.temp.name)
        original_repo_path = P1.repo_path
        original_repo_relative = P1.repo_relative

        def fixture_repo_path(recorded: str) -> Path:
            prefix = "_test_fixture/"
            if recorded.startswith(prefix):
                return self.root / recorded.removeprefix(prefix)
            return original_repo_path(recorded)

        def fixture_repo_relative(path: Path, *, role: str) -> str:
            try:
                return "_test_fixture/" + path.resolve().relative_to(self.root).as_posix()
            except ValueError:
                return original_repo_relative(path, role=role)

        self.repo_path_patch = mock.patch.object(P1, "repo_path", side_effect=fixture_repo_path)
        self.repo_relative_patch = mock.patch.object(P1, "repo_relative", side_effect=fixture_repo_relative)
        self.repo_path_patch.start()
        self.repo_relative_patch.start()
        self.refs: dict[str, dict[str, str]] = {}
        for role in P1.NATIVE_COMPONENTS:
            path = self.root / f"{role}.json"
            if role.endswith("_schema") or role == "p1_schema":
                value = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "additionalProperties": False,
                }
            else:
                value = {"schema": f"fixture-{role}", "status": "PROTOCOL_ONLY"}
            path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
            self.refs[role] = {
                "path": "_test_fixture/" + path.relative_to(self.root).as_posix(),
                "sha256": P1.sha256_file(path),
            }
        self.config = {
            "schema_version": P1.CONFIG_VERSION,
            "authority": "AUTHORITATIVE_P1",
            "components": copy.deepcopy(self.refs),
            "v1_4_p0a": {
                "path": "results/benchmark/v1.4-p0/P0A.json",
                "sha256": P1.sha256_file(P1.ROOT / "results/benchmark/v1.4-p0/P0A.json"),
            },
        }
        self.config_path = self.root / "components.json"
        def embedded(value: dict) -> dict:
            raw = P1.canonical_json(value)
            return {"encoding": "BASE64_CANONICAL_JSON_UTF8", "canonical_json_base64": base64.b64encode(raw).decode(), "sha256": P1.sha256_bytes(raw)}
        file_ref = {"path": "schemas/example.json", "sha256": "1" * 64}
        signature = base64.b64encode(b"\0" * 64).decode()
        self.readiness = {
            "schema": P1.READINESS_PACKAGE_SCHEMA,
            "status": "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R", "protocol_version": "1.5",
            "candidate": {"commit": "a" * 40, "root_tree": "b" * 40},
            "authority_root": {"commit": "c" * 40, "root_tree": "d" * 40, "path": "results/authority.json", "sha256": "2" * 64},
            "closures": {"native": {"row_count": 1, "sha256": "3" * 64}, "inherited": {"row_count": 1, "sha256": "4" * 64}, "full_source": {"row_count": 1, "sha256": "5" * 64}, "aggregate_sha256": "6" * 64},
            "operational_evidence": embedded({"schema": "fixture-evidence"}),
            "compiler": {key: copy.deepcopy(file_ref) for key in ("validator", "input_schema", "output_schema", "authority_root_schema", "operational_evidence_schema", "independent_recompile_schema", "readiness_package_schema", "p1r_schema", "activation_receipt_schema", "isolated_evidence_runner", "isolated_evidence_runner_schema", "isolated_evidence_runner_contract", "isolated_evidence_runner_test")},
            "structural_json_key_audit": {"algorithm": "STRUCTURAL_JSON_KEY_AUDIT_V1_5", "scope": ["V1_5_NATIVE_JSON_BLOBS", "V1_4_SELECTED_INHERITED_JSON_BLOBS", "V1_4_FULL_P0A_REFERENCED_JSON_BLOBS"], "json_blob_count": 1, "candidate_identities_keys_detected": 0, "statement_text_keys_detected": 0, "target_rankings_keys_detected": 0, "target_semantic_analysis_keys_detected": 0, "does_not_claim_free_text_or_python_semantic_audit": True},
            "payload_sha256": "7" * 64,
            "authority_signatures": [
                {"signer_class": "CONTROLLED_HARNESS_READINESS_KEY", "signer_id": "harness-1", "verification_key_sha256": "8" * 64, "algorithm": "Ed25519", "signature": signature},
                {"signer_class": "FROZEN_EXPERIMENTER_IDENTITY", "signer_id": "experimenter-1", "verification_key_sha256": "9" * 64, "algorithm": "Ed25519", "signature": signature},
            ],
            "independent_recompiles": [embedded({"recompiler": 1}), embedded({"recompiler": 2})],
        }
        self.readiness["package_sha256"] = P1.domain_digest(P1.READINESS_PACKAGE_DOMAIN, self.readiness)
        self.readiness_path = self.root / "candidate-readiness.json"
        self.readiness_path.write_text(json.dumps(self.readiness, indent=2) + "\n", encoding="utf-8")
        self.write_config()

    def tearDown(self) -> None:
        self.repo_relative_patch.stop()
        self.repo_path_patch.stop()
        self.temp.cleanup()

    def write_config(self) -> None:
        self.config_path.write_text(json.dumps(self.config, indent=2) + "\n", encoding="utf-8")

    def build(self) -> dict:
        self.write_config()
        return P1.assemble_p1a(self.config_path, self.readiness_path)

    def test_p1a_binds_closed_native_map_and_derived_v14_closure(self) -> None:
        p1a = self.build()
        self.assertEqual(set(p1a["components"]), set(P1.NATIVE_COMPONENTS))
        self.assertEqual(p1a["inherited_v1_4"]["selected_roles"], list(P1.INHERITED_V1_4_ROLES))
        self.assertEqual(set(p1a["inherited_v1_4"]["components"]), set(P1.INHERITED_V1_4_ROLES))
        self.assertTrue(all(
            row["content_class"] == P1.INHERITED_CONTENT_CLASS
            for row in p1a["inherited_v1_4"]["components"].values()
        ))
        P1.validate_p1a(p1a)
        self.assertEqual(P1.validate_embedded_candidate_readiness(p1a["candidate_base_readiness"]), self.readiness)

    def test_p1a_readiness_package_is_closed_canonical_and_self_authenticated(self) -> None:
        p1a = self.build()
        changed = copy.deepcopy(p1a)
        changed["candidate_base_readiness"]["package_sha256"] = "0" * 64
        with self.assertRaises(P1.P1Error):
            P1.validate_p1a(changed)
        changed = copy.deepcopy(self.readiness)
        changed["payload_sha256"] = "0" * 64
        self.readiness_path.write_text(json.dumps(changed) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(P1.P1Error, "self-digest"):
            self.build()

    def test_p1a_readiness_rejects_single_recompiler_or_single_authority_signature(self) -> None:
        for field in ("independent_recompiles", "authority_signatures"):
            value = copy.deepcopy(self.readiness)
            value[field] = value[field][:1]
            value.pop("package_sha256")
            value["package_sha256"] = P1.domain_digest(P1.READINESS_PACKAGE_DOMAIN, value)
            self.readiness_path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(P1.P1Error, "schema validation"):
                self.build()

    def test_pre_p1_closure_includes_runner_custody_and_delivery_boundary(self) -> None:
        required = {
            "checkpoint_runner", "checkpoint_runner_contract_test",
            "checkpoint_publication_manifest_schema", "checkpoint_runner_private_input_schema",
            "terminal_chronology_gap_certificate_schema", "public_checkpoint_chain_verifier",
            "public_checkpoint_chain_proof_schema", "private_custody_verifier",
            "private_custody_verifier_contract_test", "private_custody_batch_schema",
            "private_custody_coverage_certificate_schema", "public_custody_sealed_binding_schema",
            "delivery_broker", "delivery_broker_contract_test", "delivery_broker_config_schema",
            "controlled_delivery_service_boundary", "controlled_delivery_service_acceptance_tests",
            "delivery_broker_state_schema", "delivery_broker_receipt_schema",
            "delivery_broker_readiness_schema",
            "s3_object_lock_store", "s3_object_lock_store_contract_test",
            "s3_object_lock_store_config_schema", "s3_object_lock_store_readiness_schema",
            "s3_delivery_broker_adapter", "s3_delivery_broker_adapter_contract_test",
            "private_s3_object_reference_schema",
            "arm_capability_matrix", "arm_capability_matrix_schema",
            "arm_execution_envelope_schema", "arm_execution_envelope_validator",
            "arm_execution_envelope_contract_test",
            "runner_private_input_assembler", "runner_private_input_assembler_contract_test",
            "runner_private_input_assembly_schema", "private_artifact_locator_schema",
            "operational_private_custody_evidence_schema",
            "broker_custody_compiler", "broker_custody_compiler_contract_test",
            "private_worm_object_inventory_schema", "private_broker_service_epoch_schema",
            "private_custody_compiler_output_schema",
            "arm_triplet_launcher", "arm_triplet_launcher_contract_test",
            "arm_triplet_claim_schema", "arm_triplet_combined_record_schema",
            "triplet_isolation_backend", "triplet_isolation_backend_contract_test",
            "triplet_isolation_plan_schema", "triplet_isolation_acceptance_schema",
            "triplet_isolation_readiness_schema",
            "checkpoint_capture_orchestrator", "checkpoint_capture_orchestrator_contract_test",
            "checkpoint_capture_plan_schema", "checkpoint_capture_readiness_schema",
            "participant_ledger", "participant_ledger_schema", "noninterference_receipt",
            "noninterference_receipt_schema", "participant_noninterference_verifier",
            "operational_noninterference_receipt_schema",
            "noninterference_key_commitment", "noninterference_key_commitment_schema",
            "operational_noninterference_key_commitment_schema",
            "participant_noninterference_contract_test", "p1_role_resolver",
            "p1_role_resolver_contract_test", "p1_role_resolution_schema",
            "p1_role_resolution_readiness_schema", "linux_isolation_acceptance",
            "linux_isolation_acceptance_contract_test",
            "controlled_harness_service_contract", "controlled_harness_service_contract_schema",
            "target_blind_checkpoint_request_schema", "controlled_harness_response_schema",
            "controlled_harness_service", "controlled_harness_service_contract_test",
            "triplet_production_adapter", "triplet_production_adapter_contract_test",
            "production_isolation_attestation_schema", "production_triplet_acceptance_certificate_schema",
            "five_strata_classifier_contract", "five_strata_classifier_contract_schema",
            "five_strata_classifier_readiness_schema", "five_strata_classifier_closure_validator",
            "five_strata_classifier_closure_contract_test",
            "immutable_infrastructure_plan", "immutable_infrastructure_cloudformation",
            "immutable_infrastructure_verifier", "immutable_infrastructure_contract_test",
            "immutable_live_acceptance_evidence_schema", "immutable_live_acceptance_verifier",
            "immutable_live_acceptance_contract_test",
            "operational_controlled_harness_activation_schema", "operational_controlled_harness_unit_schema",
            "operational_harness_unit_generator", "operational_harness_unit_generator_contract_test",
            "controlled_harness_deployment_contract", "controlled_harness_deployment_contract_schema",
            "controlled_harness_deployment_verifier", "controlled_harness_deployment_contract_test",
            "controlled_harness_systemd_unit", "controlled_harness_sysusers_asset",
            "controlled_harness_tmpfiles_asset", "controlled_harness_network_policy",
            "controlled_harness_destructive_gap_plan",
            "controlled_harness_activation_continuity_verifier",
            "controlled_harness_activation_continuity_contract_test",
            "controlled_harness_https_daemon_contract",
            "controlled_harness_https_daemon_contract_schema",
            "controlled_harness_https_daemon", "controlled_harness_https_daemon_contract_test",
            "candidate_base_validator", "candidate_base_validator_contract_test",
            "public_readiness_authority_root_schema", "candidate_base_operational_evidence_schema",
            "candidate_base_independent_recompile_schema", "candidate_base_readiness_package_schema",
            "candidate_base_validation_input_schema", "candidate_base_validation_output_schema", "p1r_schema",
            "public_p1r_activation_receipt_schema",
            "isolated_evidence_runner", "isolated_evidence_runner_schema",
            "isolated_evidence_runner_contract", "isolated_evidence_runner_test",
            "candidate_base_readiness_spec", "candidate_base_readiness_spec_schema",
            "candidate_base_readiness_spec_contract_test", "candidate_base_validator_independent_audit",
            "candidate_base_validator_independent_audit_schema", "candidate_base_validator_independent_audit_contract_test",
            "operational_authority_gap", "operational_authority_gap_schema", "operational_authority_gap_contract_test",
            "pass_pool_builder", "pass_pool_schema", "pass_pool_builder_contract_test",
            "c0_publication_contract", "c0_publication_contract_schema", "c0_publication_contract_test",
            "c0_v15_builder", "c0_v15_schema", "c0_v15_builder_contract_test",
            "infrastructure_activation_workflow", "infrastructure_activation_workflow_contract_test",
            "candidate_base_security_schema_contract_test", "public_p1r_verifier",
            "public_p1r_verifier_contract_test", "p1t_publication_observer_workflow",
            "p1t_publication_observer_workflow_contract_test", "p1t_publication_observer_validator",
            "p1t_publication_observer_validator_contract_test", "p1r_publication_observer_workflow",
            "p1r_publication_observer_workflow_contract_test", "p1r_publication_observer_validator",
            "p1r_publication_observer_validator_contract_test", "c0_observer_workflow", "c0_observer_workflow_contract_test",
        }
        self.assertLessEqual(required, set(P1.NATIVE_COMPONENTS))
        p1a = self.build()
        self.assertLessEqual(required, set(p1a["components"]))

    def test_missing_or_extra_native_role_fails_closed(self) -> None:
        del self.config["components"][P1.NATIVE_COMPONENTS[-1]]
        with self.assertRaisesRegex(P1.P1Error, "missing"):
            self.build()
        self.config["components"][P1.NATIVE_COMPONENTS[-1]] = copy.deepcopy(
            self.refs[P1.NATIVE_COMPONENTS[-1]]
        )
        self.config["components"]["not_frozen"] = copy.deepcopy(self.refs[P1.NATIVE_COMPONENTS[0]])
        with self.assertRaisesRegex(P1.P1Error, "extra"):
            self.build()

    def test_native_digest_drift_and_content_class_drift_fail(self) -> None:
        role = "chronology_builder"
        self.config["components"][role]["sha256"] = "0" * 64
        with self.assertRaisesRegex(P1.P1Error, "SHA-256 mismatch"):
            self.build()
        self.config["components"][role] = copy.deepcopy(self.refs[role])
        p1a = self.build()
        p1a["components"][role]["content_class"] = "UNKNOWN"
        with self.assertRaises(P1.P1Error):
            P1.validate_p1a(p1a)

    def test_populated_target_data_in_protocol_json_is_rejected(self) -> None:
        role = "future_cohort_rule"
        path = P1.repo_path(self.refs[role]["path"])
        path.write_text(json.dumps({"clusters": [{"id": "future-target"}]}) + "\n", encoding="utf-8")
        self.config["components"][role]["sha256"] = P1.sha256_file(path)
        with self.assertRaisesRegex(P1.P1Error, "forbidden target-data"):
            self.build()

    def test_json_schema_target_field_names_are_definitions_not_data(self) -> None:
        role = "future_registry_output_schema"
        path = P1.repo_path(self.refs[role]["path"])
        path.write_text(json.dumps({
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"declarations": {"type": "array"}, "statement_text": {"type": "string"}},
        }) + "\n", encoding="utf-8")
        self.config["components"][role]["sha256"] = P1.sha256_file(path)
        p1a = self.build()
        P1.validate_p1a(p1a)

    def test_v14_closure_cannot_be_manually_changed_or_partially_inherited(self) -> None:
        p1a = self.build()
        role = "budget_rule"
        p1a["inherited_v1_4"]["components"][role]["sha256"] = "0" * 64
        with self.assertRaises(P1.P1Error):
            P1.validate_p1a(p1a)
        p1a = self.build()
        p1a["inherited_v1_4"]["selected_roles"].pop()
        with self.assertRaises(P1.P1Error):
            P1.validate_p1a(p1a)

    def test_invalid_v14_source_p0a_fails_before_inheritance(self) -> None:
        source = json.loads((P1.ROOT / "results/benchmark/v1.4-p0/P0A.json").read_text())
        source["components"]["budget_rule"]["sha256"] = "0" * 64
        path = self.root / "bad-p0a.json"
        path.write_text(json.dumps(source) + "\n", encoding="utf-8")
        self.config["v1_4_p0a"] = {
            "path": "_test_fixture/" + path.relative_to(self.root).as_posix(),
            "sha256": P1.sha256_file(path),
        }
        with self.assertRaisesRegex(P1.P1Error, "does not authenticate|does not validate"):
            self.build()

    def test_p1a_forbidden_output_arrays_are_schema_closed(self) -> None:
        p1a = self.build()
        for field in ("candidate_identities", "statement_text", "target_rankings", "target_semantics"):
            changed = copy.deepcopy(p1a)
            changed[field] = ["forbidden"]
            with self.assertRaises(P1.P1Error, msg=field):
                P1.validate_p1a(changed)

    def test_audit_binding_covers_exact_native_and_inherited_rows(self) -> None:
        p1a = self.build()
        self.assertEqual(p1a["target_data_audit"]["native_component_count"], len(P1.NATIVE_COMPONENTS))
        self.assertEqual(p1a["target_data_audit"]["inherited_component_count"], len(P1.INHERITED_V1_4_ROLES))
        changed = copy.deepcopy(p1a)
        changed["target_data_audit"]["audited_bindings_sha256"] = "0" * 64
        with self.assertRaisesRegex(P1.P1Error, "audit"):
            P1.validate_p1a(changed)

    def test_materializer_never_infers_missing_roles(self) -> None:
        assignments = [f"{role}={self.refs[role]['path']}" for role in P1.NATIVE_COMPONENTS]
        value = P1.materialize_config(assignments, "results/benchmark/v1.4-p0/P0A.json")
        self.assertEqual(value["components"], self.config["components"])
        with self.assertRaisesRegex(P1.P1Error, "exactly cover"):
            P1.materialize_config(assignments[:-1], "results/benchmark/v1.4-p0/P0A.json")

    def test_p1t_authenticates_committed_p1a_without_self_reference(self) -> None:
        p1a_path = self.root / "P1A.json"
        P1.write_json(p1a_path, self.build())
        p1t_path = self.root / "P1T.json"
        relative = P1.repo_relative(p1t_path, role="P1T fixture")
        original_commit_file = P1.commit_file
        def committed(commit: str, path: str) -> bytes:
            return p1a_path.read_bytes() if commit == "a" * 40 else original_commit_file(commit, path)
        with mock.patch.object(P1, "commit_file", side_effect=committed):
            p1t = P1.assemble_p1t(p1a_path, "a" * 40, "2026-08-14T00:00:00Z", relative)
            P1.validate_p1t(p1t)
        self.assertEqual(p1t["p1a_commit"], "a" * 40)
        self.assertNotIn("p1t_commit", p1t)

    def test_p1t_rejects_wrong_parent_merge_or_changed_path(self) -> None:
        p1a_path = self.root / "P1A.json"
        P1.write_json(p1a_path, self.build())
        p1t_path = self.root / "P1T.json"
        relative = P1.repo_relative(p1t_path, role="P1T fixture")
        original_commit_file = P1.commit_file
        def committed(commit: str, path: str) -> bytes:
            return p1a_path.read_bytes() if commit == "a" * 40 else original_commit_file(commit, path)
        with mock.patch.object(P1, "commit_file", side_effect=committed):
            p1t = P1.assemble_p1t(p1a_path, "a" * 40, "2026-08-14T00:00:00Z", relative)
        P1.write_json(p1t_path, p1t)

        original_git = P1.git
        def fake_git(*args: str) -> bytes:
            if args == ("rev-parse", "b" * 40):
                return ("b" * 40 + "\n").encode()
            if args[:3] == ("show", "-s", "--format=%P"):
                return ("a" * 40 + " " + "c" * 40 + "\n").encode()
            return original_git(*args)

        def fake_commit(commit: str, path: str) -> bytes:
            if commit == "a" * 40:
                return p1a_path.read_bytes()
            if commit == "b" * 40:
                return p1t_path.read_bytes()
            return original_commit_file(commit, path)

        with mock.patch.object(P1, "git", side_effect=fake_git), mock.patch.object(P1, "commit_file", side_effect=fake_commit):
            with self.assertRaisesRegex(P1.P1Error, "non-merge"):
                P1.validate_p1t(p1t, p1t_commit="b" * 40, artifact_path=p1t_path)

    def test_p1r_is_exact_one_path_child_and_only_activation_boundary(self) -> None:
        p1a = self.build()
        p1a_raw = json.dumps(p1a, sort_keys=True, indent=2).encode() + b"\n"
        p1t = {
            "schema_version": P1.SCHEMA_VERSION, "artifact_kind": "P1T", "protocol_version": "1.5",
            "p1a": {"path": "results/benchmark/v1.5-protocol/P1A.json", "sha256": P1.sha256_bytes(p1a_raw)},
            "p1a_commit": "a" * 40, "p1a_published_at_utc": "2026-08-14T00:00:00Z",
            "attestation_policy": {"p1a_ancestor_required": True, "p1a_bytes_immutable": True, "allowed_p1t_changed_paths": ["results/benchmark/v1.5-protocol/P1T.json"]},
        }
        p1t_raw = json.dumps(p1t, sort_keys=True, indent=2).encode() + b"\n"
        bind = lambda ref, commit: {"ref": ref, "commit": commit}
        p1r = {
            "schema_version": "c5k4-method-v1.5-p1r-1.0", "artifact_kind": "P1R",
            "status": "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY", "protocol_version": "1.5",
            "p1t": {"path": "results/benchmark/v1.5-protocol/P1T.json", "sha256": P1.sha256_bytes(p1t_raw)},
            "p1t_commit": "b" * 40,
            "observation": {
                "public_remote_url": "https://github.com/Kuberwastaken/c5-k4",
                "authority_root": bind("refs/tags/a0", "d" * 40), "v1_4_p0t": bind("refs/tags/p0t", "e" * 40),
                "candidate_c": bind("refs/tags/c", "f" * 40), "p1t": bind("refs/tags/p1t", "b" * 40),
                "observed_at_utc": "2026-08-14T00:01:00Z", "ls_remote_stdout_sha256": "1" * 64,
                "observer": {
                    "workflow_repository": "Kuberwastaken/c5-k4",
                    "workflow_path": ".github/workflows/method-v15-p1t-publication-observer.yml",
                    "workflow_ref": ".github/workflows/method-v15-p1t-publication-observer.yml@refs/heads/main",
                    "workflow_blob_sha256": "2" * 64, "run_id": 1, "run_attempt": 1,
                    "actions_run_projection_sha256": "3" * 64,
                },
            },
            "activation_policy": {"structural_draft_only": True, "p1r_is_activation_boundary": False, "p1t_alone_is_activation_boundary": False, "full_exact_c_replay_required": True, "p1r_parent_must_be_exact_p1t": True, "allowed_p1r_changed_paths": [P1.P1R_PATH], "public_p1r_ref_required": True},
        }
        original_git, original_commit_file = P1.git, P1.commit_file

        def committed(commit: str, path: str) -> bytes:
            if commit == "a" * 40:
                return p1a_raw
            if commit == "b" * 40:
                return p1t_raw
            return original_commit_file(commit, path)

        def valid_git(*args: str) -> bytes:
            if args in (("rev-parse", "b" * 40), ("rev-parse", "c" * 40)):
                return (args[1] + "\n").encode()
            if args[:3] == ("show", "-s", "--format=%P"):
                return (("a" if args[-1] == "b" * 40 else "b") * 40 + "\n").encode()
            if args[:4] == ("diff-tree", "--no-commit-id", "--name-only", "-r"):
                return (("results/benchmark/v1.5-protocol/P1T.json" if args[-1] == "b" * 40 else P1.P1R_PATH) + "\n").encode()
            return original_git(*args)

        with mock.patch.object(P1, "git", side_effect=valid_git), mock.patch.object(P1, "commit_file", side_effect=committed):
            P1.validate_p1r(p1r, p1r_commit="c" * 40)
            self.assertFalse(p1r["activation_policy"]["p1t_alone_is_activation_boundary"])

            def wrong_p1t_parent(*args: str) -> bytes:
                if args[:3] == ("show", "-s", "--format=%P") and args[-1] == "b" * 40:
                    return ("0" * 40 + "\n").encode()
                return valid_git(*args)

            with mock.patch.object(P1, "git", side_effect=wrong_p1t_parent):
                with self.assertRaisesRegex(P1.P1Error, "P1T must be"):
                    P1.validate_p1r(p1r, p1r_commit="c" * 40)

            def extra_p1t_path(*args: str) -> bytes:
                if args[:4] == ("diff-tree", "--no-commit-id", "--name-only", "-r") and args[-1] == "b" * 40:
                    return b"results/benchmark/v1.5-protocol/P1T.json\nextra.txt\n"
                return valid_git(*args)

            with mock.patch.object(P1, "git", side_effect=extra_p1t_path):
                with self.assertRaisesRegex(P1.P1Error, "P1T changed paths"):
                    P1.validate_p1r(p1r, p1r_commit="c" * 40)

            def wrong_p1r_parent(*args: str) -> bytes:
                if args[:3] == ("show", "-s", "--format=%P") and args[-1] == "c" * 40:
                    return ("0" * 40 + "\n").encode()
                return valid_git(*args)

            with mock.patch.object(P1, "git", side_effect=wrong_p1r_parent):
                with self.assertRaisesRegex(P1.P1Error, "P1R must be"):
                    P1.validate_p1r(p1r, p1r_commit="c" * 40)

            def extra_p1r_path(*args: str) -> bytes:
                if args[:4] == ("diff-tree", "--no-commit-id", "--name-only", "-r") and args[-1] == "c" * 40:
                    return (P1.P1R_PATH + "\nextra.txt\n").encode()
                return valid_git(*args)

            with mock.patch.object(P1, "git", side_effect=extra_p1r_path):
                with self.assertRaisesRegex(P1.P1Error, "P1R changed paths"):
                    P1.validate_p1r(p1r, p1r_commit="c" * 40)


if __name__ == "__main__":
    unittest.main()
