#!/usr/bin/env python3
"""Adversarial tests for the v1.5 pre-registry classifier runtime binding."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_benchmark_v15_classifier_runtime.py"
SPEC = importlib.util.spec_from_file_location("v15_classifier_runtime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


COMPONENT_PATHS = {
    "five_strata_classifier": "results/benchmark/v1.4-protocol/five-strata-classifier.json",
    "syntax_pool_builder": "scripts/build_benchmark_v14_pool.py",
    "classifier_closure_contract": "results/benchmark/v1.5-protocol/five-strata-classifier-contract.json",
    "classifier_closure_validator": "scripts/validate_benchmark_v15_classifier_closure.py",
    "classifier_closure_readiness_schema": "schemas/benchmark-five-strata-classifier-readiness-v1.5.schema.json",
}


class RuntimeBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        parent = ROOT / "results/benchmark"
        self.temp = tempfile.TemporaryDirectory(prefix="v15-classifier-runtime-test-", dir=parent)
        self.root = Path(self.temp.name)
        self.roles = {}
        for name, path in COMPONENT_PATHS.items():
            closure, role = V.EXPECTED_COMPONENTS[name]
            self.roles[name] = {
                "closure": closure,
                "role": role,
                "path": path,
                "sha256": V.sha256((ROOT / path).read_bytes()),
            }
        self.readiness = V.closure.validate(
            ROOT / COMPONENT_PATHS["classifier_closure_contract"],
            ROOT / COMPONENT_PATHS["five_strata_classifier"],
            ROOT / COMPONENT_PATHS["syntax_pool_builder"],
        )
        self.readiness_path = self.root / "readiness.json"
        self.write_json(self.readiness_path, self.readiness)
        self.resolution = self.role_resolution()
        self.resolution_path = self.root / "resolution.json"
        self.write_json(self.resolution_path, self.resolution)
        self.binding = self.binding_fixture()
        self.binding_path = self.root / "binding.json"
        self.write_binding()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def write_json(path: Path, value: dict) -> None:
        path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n")

    def role_resolution(self) -> dict:
        rows = []
        for name, bound in self.roles.items():
            rows.append({
                **bound,
                "content_class": "INHERITED_V1_4_EXACT" if bound["closure"] == "INHERITED_V1_4" else "V1_5_PROTOCOL_ONLY_NO_TARGET_DATA",
                "selector_paths": [f"components.classifier_runtime.{name}"],
            })
        value = {
            "schema": "c5k4-method-v1.5-p1-role-resolution-1.0",
            "status": "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE",
            "operational": True,
            "target_data_present": False,
            "publication": {
                "repository": "https://github.com/Kuberwastaken/c5-k4.git",
                "ref": "refs/remotes/origin/main",
                "published_tip_commit": "1" * 40,
            },
            "p1": {
                "p1a_commit": "2" * 40, "p1a_path": "results/benchmark/v1.5-p1/p1a.json", "p1a_sha256": "3" * 64,
                "p1t_commit": "4" * 40, "p1t_path": "results/benchmark/v1.5-p1/p1t.json", "p1t_sha256": "5" * 64,
            },
            "manifest": {"path": "results/benchmark/v1.5-protocol/checkpoint-component-manifest.json", "sha256": "6" * 64},
            "resolved_role_count": len(rows),
            "resolved_roles": sorted(rows, key=lambda row: (row["closure"], row["role"])),
        }
        value["resolution_sha256"] = V.sha256(V.canonical_json(value))
        return value

    def binding_fixture(self) -> dict:
        return {
            "schema": "c5k4-method-v1.5-classifier-runtime-binding-1.0",
            "status": "FROZEN_P1_PRE_REGISTRY_CLASSIFIER_BINDING",
            "target_data_access_permitted": False,
            "future_registry_invocation_started": False,
            "p1_role_resolution": {"path": str(self.resolution_path), "sha256": V.sha256(self.resolution_path.read_bytes())},
            "classifier_readiness_receipt": {"path": str(self.readiness_path), "sha256": V.sha256(self.readiness_path.read_bytes())},
            "consumed_classifier": {
                "path": str(ROOT / COMPONENT_PATHS["five_strata_classifier"]),
                "sha256": self.roles["five_strata_classifier"]["sha256"],
            },
            "components": copy.deepcopy(self.roles),
        }

    def write_binding(self) -> None:
        self.write_json(self.binding_path, self.binding)

    def refresh_resolution_ref(self) -> None:
        self.write_json(self.resolution_path, self.resolution)
        self.binding["p1_role_resolution"]["sha256"] = V.sha256(self.resolution_path.read_bytes())
        self.write_binding()

    def test_authenticates_actual_runtime_before_registry_without_target_output(self) -> None:
        result = V.verify(self.binding_path)
        self.assertEqual(result["status"], "CLASSIFIER_RUNTIME_AUTHENTICATED_BEFORE_REGISTRY")
        self.assertFalse(result["target_data_read"])
        self.assertFalse(result["future_registry_invocation_started"])
        encoded = json.dumps(result).casefold()
        for forbidden in ("cluster_id", "candidate_id", "statement_text", "target_identity"):
            self.assertNotIn(forbidden, encoded)

    def test_wrong_executing_worktree_builder_bytes_are_rejected(self) -> None:
        wrong = self.root / "build_benchmark_v14_pool.py"
        wrong.write_bytes((ROOT / COMPONENT_PATHS["syntax_pool_builder"]).read_bytes() + b"\n# drift\n")
        with mock.patch.object(V.future.syntax, "__file__", str(wrong)):
            with self.assertRaisesRegex(V.RuntimeBindingError, "executing future-cohort"):
                V.verify(self.binding_path)

    def test_component_digest_or_p1_role_binding_drift_is_rejected(self) -> None:
        self.binding["components"]["five_strata_classifier"]["sha256"] = "0" * 64
        self.write_binding()
        with self.assertRaisesRegex(V.RuntimeBindingError, "differs from authenticated P1 role"):
            V.verify(self.binding_path)

    def test_classifier_bytes_actually_consumed_by_registry_are_bound(self) -> None:
        wrong = self.root / "classifier.json"
        wrong.write_bytes((ROOT / COMPONENT_PATHS["five_strata_classifier"]).read_bytes() + b" ")
        self.binding["consumed_classifier"] = {
            "path": str(wrong), "sha256": V.sha256(wrong.read_bytes())
        }
        self.write_binding()
        with self.assertRaisesRegex(V.RuntimeBindingError, "not the P1-authenticated classifier"):
            V.verify(self.binding_path)

    def test_resolution_digest_tamper_is_rejected(self) -> None:
        self.resolution["resolution_sha256"] = "0" * 64
        self.refresh_resolution_ref()
        with self.assertRaisesRegex(V.RuntimeBindingError, "self-digest"):
            V.verify(self.binding_path)

    def test_readiness_file_or_self_digest_tamper_is_rejected(self) -> None:
        self.readiness_path.write_bytes(self.readiness_path.read_bytes() + b" ")
        with self.assertRaisesRegex(V.RuntimeBindingError, "byte digest mismatch"):
            V.verify(self.binding_path)
        self.write_json(self.readiness_path, self.readiness)
        changed = copy.deepcopy(self.readiness)
        changed["contract_sha256"] = "0" * 64
        self.write_json(self.readiness_path, changed)
        self.binding["classifier_readiness_receipt"]["sha256"] = V.sha256(self.readiness_path.read_bytes())
        self.write_binding()
        with self.assertRaisesRegex(V.RuntimeBindingError, "self-digest"):
            V.verify(self.binding_path)

    def test_contract_drift_is_rejected_before_any_registry_call(self) -> None:
        original = ROOT / COMPONENT_PATHS["classifier_closure_contract"]
        changed = json.loads(original.read_text())
        changed["status"] = "RELAXED"
        replacement = self.root / "contract.json"
        self.write_json(replacement, changed)
        relative = replacement.relative_to(ROOT).as_posix()
        digest = V.sha256(replacement.read_bytes())
        row = next(row for row in self.resolution["resolved_roles"] if row["role"] == "classifier_closure_contract")
        row["path"], row["sha256"] = relative, digest
        self.resolution["resolution_sha256"] = V.sha256(V.canonical_json({key: value for key, value in self.resolution.items() if key != "resolution_sha256"}))
        self.binding["components"]["classifier_closure_contract"]["path"] = relative
        self.binding["components"]["classifier_closure_contract"]["sha256"] = digest
        self.refresh_resolution_ref()
        with self.assertRaisesRegex(V.RuntimeBindingError, "closure replay failed"):
            V.verify(self.binding_path)

    def test_missing_required_p1_role_is_rejected(self) -> None:
        self.resolution["resolved_roles"] = [row for row in self.resolution["resolved_roles"] if row["role"] != "syntax_pool_builder"]
        self.resolution["resolved_role_count"] -= 1
        self.resolution["resolution_sha256"] = V.sha256(V.canonical_json({key: value for key, value in self.resolution.items() if key != "resolution_sha256"}))
        self.refresh_resolution_ref()
        with self.assertRaisesRegex(V.RuntimeBindingError, "omits"):
            V.verify(self.binding_path)

    def test_post_registry_or_target_access_claim_is_schema_rejected(self) -> None:
        self.binding["future_registry_invocation_started"] = True
        self.write_binding()
        with self.assertRaisesRegex(V.RuntimeBindingError, "schema failed"):
            V.verify(self.binding_path)

    def test_component_parent_symlink_cannot_escape_repository(self) -> None:
        outside = Path("/tmp") / f"{self.root.name}-outside-classifier.json"
        outside.write_bytes((ROOT / COMPONENT_PATHS["five_strata_classifier"]).read_bytes())
        link = self.root / "escape"
        link.symlink_to(outside.parent, target_is_directory=True)
        escaped = (link / outside.name).relative_to(ROOT).as_posix()
        digest = V.sha256(outside.read_bytes())
        row = next(row for row in self.resolution["resolved_roles"] if row["role"] == "five_strata_classifier")
        row["path"], row["sha256"] = escaped, digest
        self.resolution["resolution_sha256"] = V.sha256(V.canonical_json({key: value for key, value in self.resolution.items() if key != "resolution_sha256"}))
        self.binding["components"]["five_strata_classifier"]["path"] = escaped
        self.binding["components"]["five_strata_classifier"]["sha256"] = digest
        self.refresh_resolution_ref()
        try:
            with self.assertRaisesRegex(V.RuntimeBindingError, "outside the protocol repository"):
                V.verify(self.binding_path)
        finally:
            outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
