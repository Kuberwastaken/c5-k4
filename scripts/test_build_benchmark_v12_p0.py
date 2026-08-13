#!/usr/bin/env python3
"""Tests for deterministic Method v1.2 P0 assembly and attestation."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("build_benchmark_v12_p0.py")
SPEC = importlib.util.spec_from_file_location("benchmark_v12_p0", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
P0 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class P0Tests(unittest.TestCase):
    def setUp(self) -> None:
        parent = P0.ROOT / "results" / "benchmark"
        self.temp = tempfile.TemporaryDirectory(prefix="v12-p0-test-", dir=parent)
        self.root = Path(self.temp.name)
        self.refs: dict[str, dict[str, str]] = {}
        for role in P0.REQUIRED_COMPONENTS:
            if role in P0.JSON_CONTRACTS:
                version, keys = P0.JSON_CONTRACTS[role]
                value = {key: None for key in keys}
                value["schema_version"] = version
                path = self.root / f"{role}.json"
                path.write_text(json.dumps(value, indent=2), encoding="utf-8")
            elif role in P0.JSON_SCHEMA_ROLES:
                path = self.root / f"{role}.json"
                path.write_text(json.dumps({
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "additionalProperties": False,
                }), encoding="utf-8")
            else:
                path = self.root / f"{role}.txt"
                path.write_text(f"frozen protocol component {role}\n", encoding="utf-8")
            self.refs[role] = {
                "path": path.relative_to(P0.ROOT).as_posix(),
                "sha256": digest(path),
            }
        for name in ("producer", "contract", "input-schema", "output-schema"):
            path = self.root / f"{name}.txt"
            path.write_text(f"{name}\n", encoding="utf-8")
            self.refs[name] = {
                "path": path.relative_to(P0.ROOT).as_posix(),
                "sha256": digest(path),
            }
        prototype_dir = self.root / "v1.2-prototype"
        prototype_dir.mkdir()
        self.prototype = prototype_dir / "syntax-only.json"
        self.prototype.write_text('{"authority":"PRE_P0_NOT_FREEZE"}\n', encoding="utf-8")
        self.config = {
            "schema_version": P0.CONFIG_VERSION,
            "authority": "AUTHORITATIVE_P0",
            "components": {role: copy.deepcopy(self.refs[role]) for role in P0.REQUIRED_COMPONENTS},
            "allowlisted_registry_producers": [{
                "producer_id": "registry-builder-v1",
                "executable": copy.deepcopy(self.refs["producer"]),
                "invocation_contract": copy.deepcopy(self.refs["contract"]),
                "input_schema": copy.deepcopy(self.refs["input-schema"]),
                "output_schema": copy.deepcopy(self.refs["output-schema"]),
            }],
            "prototype_artifacts": [{
                "path": self.prototype.relative_to(P0.ROOT).as_posix(),
                "sha256": digest(self.prototype),
                "authority": "PRE_P0_NOT_FREEZE",
                "excluded_from_formal_build": True,
            }],
        }
        self.receipt = self.root / "target-data-audit-receipt.json"
        self.write_receipt()
        self.config["target_data_audit_receipt"] = {
            "path": self.receipt.relative_to(P0.ROOT).as_posix(),
            "sha256": digest(self.receipt),
        }
        self.config_path = self.root / "components.json"
        self.write_config()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_config(self) -> None:
        self.config_path.write_text(json.dumps(self.config, indent=2), encoding="utf-8")

    def write_receipt(self, **overrides: object) -> None:
        receipt = {
            "schema_version": "c5k4-method-v1.2-target-data-audit-receipt-1.0",
            "audit_rule_sha256": self.refs["target_data_audit_rule"]["sha256"],
            "components": [
                {
                    "role": role,
                    "path": self.refs[role]["path"],
                    "sha256": self.refs[role]["sha256"],
                    "classification": "PROTOCOL_ONLY_NO_TARGET_DATA",
                }
                for role in P0.REQUIRED_COMPONENTS
            ],
            "final_eligible_rows_detected": 0,
            "selected_clusters_detected": 0,
            "statement_text_detected": 0,
            "semantic_target_analysis_detected": 0,
        }
        receipt.update(overrides)
        self.receipt.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    def build(self) -> dict:
        self.write_config()
        return P0.assemble_p0a(self.config_path)

    def test_authoritative_p0a_binds_every_required_digest(self) -> None:
        p0a = self.build()
        self.assertEqual(set(p0a["components"]), set(P0.REQUIRED_COMPONENTS))
        self.assertEqual(p0a["final_eligible_rows"], [])
        self.assertEqual(p0a["selected_clusters"], [])
        self.assertEqual(p0a["target_semantics"], [])
        self.assertNotIn("p0a_commit", p0a)
        self.assertNotIn("p0a_sha256", p0a)
        P0.validate_p0a(p0a)

    def test_pre_p0_config_cannot_become_authoritative(self) -> None:
        self.config["authority"] = "PRE_P0_NOT_FREEZE"
        with self.assertRaisesRegex(P0.P0Error, "cannot assemble authoritative"):
            self.build()

    def test_missing_component_and_digest_drift_fail_closed(self) -> None:
        del self.config["components"]["selection_stratum_priors"]
        with self.assertRaisesRegex(P0.P0Error, "missing"):
            self.build()
        self.config["components"]["selection_stratum_priors"] = copy.deepcopy(
            self.refs["selection_stratum_priors"]
        )
        self.config["components"]["selector"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(P0.P0Error, "SHA-256 mismatch"):
            self.build()

    def test_source_boundary_and_forecast_baselines_are_independent_required_components(self) -> None:
        required = set(P0.REQUIRED_COMPONENTS)
        self.assertTrue({
            "source_discovery_contract",
            "source_path_policy",
            "development_prior",
            "selection_forecast_rule",
            "selection_stratum_priors",
            "intervention_forecast_rule",
        }.issubset(required))
        for role in ("source_discovery_contract", "source_path_policy", "development_prior"):
            changed = copy.deepcopy(self.config)
            del changed["components"][role]
            self.config = changed
            with self.assertRaisesRegex(P0.P0Error, "missing"):
                self.build()
            self.config["components"][role] = copy.deepcopy(self.refs[role])

    def test_prototype_cannot_fill_authoritative_role(self) -> None:
        self.config["components"]["selector"] = {
            "path": self.prototype.relative_to(P0.ROOT).as_posix(),
            "sha256": digest(self.prototype),
        }
        with self.assertRaisesRegex(P0.P0Error, "prototype area"):
            self.build()

    def test_final_rows_or_target_semantics_are_schema_forbidden(self) -> None:
        p0a = self.build()
        for field in ("final_eligible_rows", "selected_clusters", "target_semantics"):
            changed = copy.deepcopy(p0a)
            changed[field] = [{"forbidden": True}]
            with self.assertRaises(P0.P0Error, msg=field):
                P0.validate_p0a(changed)

    def test_target_data_audit_must_cover_every_exact_component_and_find_zero(self) -> None:
        self.write_receipt(statement_text_detected=1)
        self.config["target_data_audit_receipt"]["sha256"] = digest(self.receipt)
        with self.assertRaisesRegex(P0.P0Error, "statement_text_detected"):
            self.build()
        self.write_receipt()
        receipt = json.loads(self.receipt.read_text())
        receipt["components"].pop()
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        self.config["target_data_audit_receipt"]["sha256"] = digest(self.receipt)
        with self.assertRaisesRegex(P0.P0Error, "exactly cover"):
            self.build()

    def test_receipt_is_deterministically_generated_from_exact_components(self) -> None:
        receipt = P0.generate_audit_receipt(self.config)
        expected = json.loads(self.receipt.read_text())
        self.assertEqual(receipt, expected)
        self.assertEqual(len(receipt["components"]), 25)

    def test_audit_rejects_forbidden_target_data_fields(self) -> None:
        role = "development_prior"
        path = P0.repo_path(self.config["components"][role]["path"])
        value = json.loads(path.read_text())
        value["clusters"] = [{"cluster_id": "must-not-exist"}]
        path.write_text(json.dumps(value), encoding="utf-8")
        self.config["components"][role]["sha256"] = digest(path)
        with self.assertRaisesRegex(P0.P0Error, "top-level keys differ|forbidden target-data"):
            P0.generate_audit_receipt(self.config)

    def test_audit_rejects_wrong_protocol_version_and_top_level_keys(self) -> None:
        role = "quotas"
        path = P0.repo_path(self.config["components"][role]["path"])
        value = json.loads(path.read_text())
        value["schema_version"] = "wrong"
        path.write_text(json.dumps(value), encoding="utf-8")
        self.config["components"][role]["sha256"] = digest(path)
        with self.assertRaisesRegex(P0.P0Error, "schema_version"):
            P0.generate_audit_receipt(self.config)

    def test_json_schema_property_named_clusters_is_not_target_data(self) -> None:
        role = "benchmark_schema"
        path = P0.repo_path(self.config["components"][role]["path"])
        value = json.loads(path.read_text())
        value["properties"] = {"clusters": {"type": "array", "maxItems": 0}}
        path.write_text(json.dumps(value), encoding="utf-8")
        self.config["components"][role]["sha256"] = digest(path)
        receipt = P0.generate_audit_receipt(self.config)
        self.assertEqual(receipt["final_eligible_rows_detected"], 0)

    def test_p0t_authenticates_already_committed_p0a_without_self_reference(self) -> None:
        p0a = self.build()
        p0a_path = self.root / "p0a.json"
        P0.write_json(p0a_path, p0a)
        commit = "a" * 40
        p0t_relative = (self.root / "p0t.json").relative_to(P0.ROOT).as_posix()
        with mock.patch.object(P0, "commit_file", return_value=p0a_path.read_bytes()):
            p0t = P0.assemble_p0t(
                p0a_path, commit, "2026-08-14T00:00:00Z", p0t_relative
            )
            P0.validate_p0t(p0t)
        self.assertEqual(p0t["p0a_commit"], commit)
        self.assertEqual(p0t["p0a"]["sha256"], digest(p0a_path))
        self.assertNotIn("p0t_commit", p0t)

    def test_p0t_rejects_committed_byte_drift(self) -> None:
        p0a = self.build()
        p0a_path = self.root / "p0a.json"
        P0.write_json(p0a_path, p0a)
        with mock.patch.object(P0, "commit_file", return_value=b"different\n"):
            with self.assertRaisesRegex(P0.P0Error, "bytes differ"):
                P0.assemble_p0t(
                    p0a_path,
                    "a" * 40,
                    "2026-08-14T00:00:00Z",
                    (self.root / "p0t.json").relative_to(P0.ROOT).as_posix(),
                )

    def test_committed_p0t_must_be_direct_single_path_attestation(self) -> None:
        p0a = self.build()
        p0a_path = self.root / "p0a.json"
        P0.write_json(p0a_path, p0a)
        p0t_path = self.root / "p0t.json"
        relative = p0t_path.relative_to(P0.ROOT).as_posix()
        with mock.patch.object(P0, "commit_file", return_value=p0a_path.read_bytes()):
            p0t = P0.assemble_p0t(p0a_path, "a" * 40, "2026-08-14T00:00:00Z", relative)
        P0.write_json(p0t_path, p0t)

        def fake_git(*args: str) -> bytes:
            if args == ("rev-parse", "b" * 40):
                return ("b" * 40 + "\n").encode()
            if args == ("rev-parse", "b" * 40 + "^"):
                return ("a" * 40 + "\n").encode()
            if args[:3] == ("show", "-s", "--format=%P"):
                return ("a" * 40 + "\n").encode()
            if args[:4] == ("diff-tree", "--no-commit-id", "--name-only", "-r"):
                return (relative + "\n").encode()
            raise AssertionError(args)

        def fake_commit_file(commit: str, path: str) -> bytes:
            return p0a_path.read_bytes() if commit == "a" * 40 else p0t_path.read_bytes()

        with mock.patch.object(P0, "git", side_effect=fake_git), mock.patch.object(
            P0, "commit_file", side_effect=fake_commit_file
        ):
            P0.validate_p0t(p0t, p0t_commit="b" * 40, artifact_path=p0t_path)


if __name__ == "__main__":
    unittest.main()
