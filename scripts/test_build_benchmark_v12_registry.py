#!/usr/bin/env python3
"""Focused tests for the one-shot Method v1.2 production registry builder."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import subprocess


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v12_registry as registry  # noqa: E402


class RegistryBuilderTests(unittest.TestCase):
    def test_authoritative_exemptions_are_exact_two_historical_units(self) -> None:
        ledger = json.loads(
            (ROOT / "results/benchmark/v1.2-protocol/registry-exemption-rule.json").read_text(
                encoding="utf-8"
            )
        )
        policy = json.loads(
            (ROOT / "results/benchmark/v1.2-protocol/provenance-policy.json").read_text(
                encoding="utf-8"
            )
        )
        registry.validate_exemption_ledger(ledger, policy)
        self.assertEqual(len(ledger["units"]), 2)
        self.assertEqual(
            {row["content_schema"] for row in ledger["units"]},
            {
                "c5k4-open-inventory-1.2-prototype",
                "c5k4-question-cluster-pool-1.2-prototype",
            },
        )
        self.assertFalse(ledger["policy"]["global_content_hash_allowlist"])
        self.assertFalse(ledger["policy"]["future_outputs_exemptible"])

    def request_fixture(self) -> dict:
        digest = "1" * 64
        ref = {
            "path": "fixture.json", "file_sha256": digest,
            "canonical_sha256": digest, "schema_version": "fixture-1.0",
            "authority": "FROZEN_PRODUCTION_INPUT",
        }
        return {
            "schema_version": registry.INPUT_SCHEMA_VERSION,
            "authority": "PRODUCTION_AFTER_P0T_S0", "protocol_version": "1.2",
            "build_ordinal": 1, "allowed_build_count": 1,
            "chronology": {
                "p0_artifact_commit": "1" * 40, "p0_attestation_commit": "2" * 40,
                "p0_published_at_utc": "2026-08-13T19:00:00Z", "s0_snapshot_id": "S0",
                "s0_acquired_at_utc": "2026-08-13T19:10:00Z", "s0_snapshot_sha256": "3" * 64,
            },
            "upstream": {
                "repository": "https://github.com/google-deepmind/formal-conjectures.git",
                "remote_ref": "refs/heads/main", "commit": "4" * 40, "tree": "5" * 40,
                "subtree": "FormalConjectures", "resolution_count": 1,
            },
            "producer": {
                "producer_id": "method-v1.2-production-registry-builder",
                "executable_path": "scripts/build_benchmark_v12_registry.py",
                "executable_sha256": digest, "invocation_contract_sha256": digest,
                "input_schema_sha256": digest, "output_schema_sha256": digest,
            },
            "inputs": {name: dict(ref) for name in (
                "p0a", "p0t", "s0", "sources_config", "five_strata_classifier",
                "grouping_rule", "provenance_policy", "source_discovery_boundary",
                "quotas", "registry_exemptions",
            )},
            "resolver_receipts": {"public_p0t": dict(ref), "upstream_main": dict(ref)},
            "controls": {
                "prototype_inputs_permitted": False, "candidate_semantics_inspected": False,
                "entropy_used": False, "selected_clusters": [],
                "selection_or_ranking_permitted": False,
                "create_exclusive_output_directory": True, "overwrite_permitted": False,
            },
            "registry_build_invoked_at_utc": "2026-08-13T19:20:00Z",
        }

    def test_execute_emits_schema_valid_production_envelope_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = self.request_fixture()
            request_path = root / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            artifacts = {}
            for artifact_id, version in registry.OUTPUT_SCHEMAS.items():
                rows_key = "strata" if artifact_id == "quota_feasibility" else "records" if artifact_id == "provenance_inventory" else "clusters"
                artifacts[artifact_id] = {"schema_version": version, rows_key: []}
            artifacts["eligible_pool"]["clusters"] = []
            artifacts["quota_feasibility"]["status"] = "FAIL"
            artifacts["quota_feasibility"]["strata"] = [{
                "stratum": stratum, "quota": registry.QUOTAS[stratum], "eligible_count": 0,
                "deficit": registry.QUOTAS[stratum], "surplus": 0,
            } for stratum in registry.STRATA]
            loaded = {"s0": (root / "s0", {"snapshot_sha256": "3" * 64}, b"{}")}
            output_dir = root / "production"
            with mock.patch.object(registry, "validate_protocol_bindings", return_value=loaded), \
                 mock.patch.object(registry, "production_artifacts", return_value=artifacts):
                output = registry.execute(request_path, root, output_dir)
            self.assertEqual(output["feasibility_replay"]["terminal_result"], "NO_ELIGIBLE_BENCHMARK_PRE_C0")
            self.assertEqual(len(output["artifacts"]), 6)
            self.assertTrue((output_dir / "registry-build-output.json").is_file())
            self.assertEqual(output["output_sha256"], registry.object_digest(output, "output_sha256"))

    def test_preflight_makes_exactly_two_calls_and_freezes_raw_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            commit = "a" * 40
            request = root / "preflight.json"
            request.write_text(json.dumps({
                "schema_version": registry.PREFLIGHT_SCHEMA_VERSION,
                "p0t_commit": commit,
                "public_remote_url": "https://example.invalid/protocol.git",
                "upstream_resolution_command": [
                    "git", "ls-remote", "https://github.com/google-deepmind/formal-conjectures.git",
                    "refs/heads/main",
                ],
                "resolved_at_utc": "2026-08-13T20:00:00Z",
            }), encoding="utf-8")
            responses = [
                subprocess.CompletedProcess([], 0, f"{commit}\trefs/heads/main\n".encode(), b""),
                subprocess.CompletedProcess([], 0, f"{'b' * 40}\trefs/heads/main\n".encode(), b""),
            ]
            with mock.patch.object(registry.subprocess, "run", side_effect=responses) as run:
                receipts = registry.preflight(request, root / "receipts")
            self.assertEqual(run.call_count, 2)
            self.assertEqual(set(receipts), {"public_p0t", "upstream_main"})
            self.assertTrue((root / "receipts/public-p0t.json").is_file())
            self.assertTrue((root / "receipts/upstream-main.json").is_file())
            self.assertEqual(
                receipts["upstream_main"]["stdout_sha256"],
                registry.sha256(receipts["upstream_main"]["stdout"].encode()),
            )

    def test_output_names_and_production_schemas_are_exact(self) -> None:
        self.assertEqual(
            registry.OUTPUT_FILES,
            {
                "open_inventory": "open-inventory.json",
                "question_cluster_pool": "question-cluster-pool.json",
                "provenance_inventory": "provenance-inventory.json",
                "contamination_inventory": "contamination-inventory.json",
                "eligible_pool": "eligible-cluster-pool.json",
                "quota_feasibility": "quota-feasibility.json",
            },
        )
        self.assertTrue(all("prototype" not in value for value in registry.OUTPUT_SCHEMAS.values()))

    def test_existing_output_fails_before_protocol_or_target_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / "request.json"
            request.write_text("{}\n", encoding="utf-8")
            output = root / "already-there"
            output.mkdir()
            with mock.patch.object(registry, "validate_schema") as validate:
                with self.assertRaisesRegex(registry.RegistryBuildError, "already exists"):
                    registry.execute(request, root, output)
            validate.assert_called_once()

    def test_row_replay_accepts_exact_fail_and_rejects_false_fail(self) -> None:
        rows = []
        for index, stratum in enumerate(registry.STRATA):
            rows.append({
                "cluster_id": f"c{index}", "identity_sha256": f"{index + 1:064x}",
                "stratum": stratum, "eligible": False,
                "machine_classification_unambiguous": True,
                "identity_grouping_complete": True,
                "semantic_exposure": True, "unknown_exposure": False,
                "registry_contact_evidence_count": 0,
            })
        pool = {
            "schema_version": "c5k4-eligible-cluster-pool-1.2",
            "artifact_status": "CONTAMINATION_APPLIED",
            "upstream": {"repository": "google-deepmind/formal-conjectures", "commit": "1" * 40, "tree": "2" * 40},
            "digests": {f"{key}_sha256": "3" * 64 for key in registry.selector.ARTIFACT_KEYS},
            "clusters": rows,
        }
        strata = [{
            "stratum": stratum, "quota": registry.QUOTAS[stratum],
            "eligible_count": 0, "deficit": registry.QUOTAS[stratum], "surplus": 0,
        } for stratum in registry.STRATA]
        feasibility = {
            "schema_version": "c5k4-quota-feasibility-1.2", "status": "FAIL",
            "strata": strata,
        }
        feasibility["certificate_sha256"] = registry.object_digest(feasibility, "certificate_sha256")
        artifacts = {"eligible_pool": pool, "quota_feasibility": feasibility}
        registry.replay_rows(artifacts, {})
        feasibility["strata"][0]["eligible_count"] = 1
        feasibility["certificate_sha256"] = registry.object_digest(feasibility, "certificate_sha256")
        with self.assertRaisesRegex(registry.RegistryBuildError, "does not replay"):
            registry.replay_rows(artifacts, {})

    def test_output_self_digest_omits_only_self_field(self) -> None:
        value = {"schema_version": "x", "answer": 7}
        value["output_sha256"] = registry.object_digest(value, "output_sha256")
        self.assertEqual(value["output_sha256"], registry.object_digest(value, "output_sha256"))
        value["answer"] = 8
        self.assertNotEqual(value["output_sha256"], registry.object_digest(value, "output_sha256"))

    def test_s0_canonical_digest_omits_snapshot_not_input_binding(self) -> None:
        value = {
            "schema_version": "c5k4-source-snapshot-S0-1.2",
            "snapshot_sha256": "1" * 64,
            "sources_config_sha256": "2" * 64,
        }
        self.assertEqual(
            registry.artifact_object_digest(value),
            registry.object_digest(value, "snapshot_sha256"),
        )
        value["sources_config_sha256"] = "3" * 64
        self.assertNotEqual(
            registry.artifact_object_digest(value),
            registry.object_digest({**value, "sources_config_sha256": "2" * 64}, "snapshot_sha256"),
        )

    def test_exemption_ledger_is_unit_exact_and_rule_bound(self) -> None:
        policy = {
            "machine_exemption_required_fields": [
                "source_id", "source_kind", "locator", "role", "content_sha256",
                "content_schema", "unit_identity_sha256", "producer_verified",
                "invocation_contract_verified", "output_digest_verified",
                "bounded_schema_verified", "mixed_unit_rejected",
            ],
            "machine_exemption_required_true": [
                "producer_verified", "invocation_contract_verified",
                "output_digest_verified", "bounded_schema_verified", "mixed_unit_rejected",
            ],
            "machine_roles": ["machine-generated-git-blob"],
            "machine_source_kinds": {"machine-generated-git-blob": ["git"]},
            "bounded_content_schemas": ["c5k4-open-inventory-1.2"],
        }
        row = {
            "source_id": "repo:c5-k4", "source_kind": "git",
            "locator": "git-blob:abc:open-inventory.json",
            "role": "machine-generated-git-blob", "content_sha256": "1" * 64,
            "content_schema": "c5k4-open-inventory-1.2",
            "producer_verified": True, "invocation_contract_verified": True,
            "output_digest_verified": True, "bounded_schema_verified": True,
            "mixed_unit_rejected": True,
        }
        row["unit_identity_sha256"] = registry.contamination.provenance.unit_identity_sha256(row)
        ledger = {
            "schema_version": "c5k4-registry-exemption-rule-1.2",
            "artifact_status": "AUTHORITATIVE_P0_PROTOCOL", "complete": True,
            "policy": {"global_content_hash_allowlist": False}, "units": [row],
            "registry_only_unit_identity_sha256": [row["unit_identity_sha256"]],
        }
        ledger["inventory_sha256"] = registry.object_digest(ledger, "inventory_sha256")
        registry.validate_exemption_ledger(ledger, policy)
        broken = json.loads(json.dumps(ledger))
        broken["units"][0]["locator"] = "git-blob:other:open-inventory.json"
        with self.assertRaisesRegex(registry.RegistryBuildError, "identity"):
            registry.validate_exemption_ledger(broken, policy)

    def test_normalized_source_config_uses_all_s0_kinds(self) -> None:
        s0 = {"sources": [
            {"source_id": "a", "kind": "git_history", "tips": [{"object_id": "1" * 40}], "path": "/a"},
            {"source_id": "b", "kind": "git_user_delta", "head_commit": "2" * 40, "tips": [], "upstream_base_refs": [{"object_id": "3" * 40}], "path": "/b"},
            {"source_id": "c", "kind": "tree", "path": "/c"},
            {"source_id": "d", "kind": "git_sessions", "immutable_commit": "4" * 40, "path": "/d", "session_mirrors": [{"id": "codex", "format": "codex", "ai_chats_subdir": "codex"}]},
            {"source_id": "e", "kind": "release_metadata_snapshot", "path": "/e"},
        ]}
        config = registry.normalize_sources(s0)
        self.assertEqual([row["kind"] for row in config["sources"]], ["git", "git_delta", "tree", "git_sessions", "release_snapshot"])


if __name__ == "__main__":
    unittest.main()
