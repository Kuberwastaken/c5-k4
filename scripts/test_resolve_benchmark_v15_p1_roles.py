#!/usr/bin/env python3
"""Adversarial tests for authenticated Method v1.5 P1 role resolution."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import jsonschema


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "resolve_benchmark_v15_p1_roles", HERE / "resolve_benchmark_v15_p1_roles.py"
)
assert SPEC and SPEC.loader
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"


P1_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "oneOf": [
        {"type": "object", "required": ["artifact_kind", "authority", "components", "inherited_v1_4"],
         "properties": {"artifact_kind": {"const": "P1A"}, "authority": {"const": "AUTHORITATIVE_P1"}}},
        {"type": "object", "required": ["artifact_kind", "p1a", "p1a_commit", "attestation_policy"],
         "properties": {"artifact_kind": {"const": "P1T"}}},
    ],
}
MANIFEST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object", "additionalProperties": False,
    "required": ["schema", "authority", "components"],
    "properties": {
        "schema": {"const": "test-manifest"},
        "authority": {"const": "RESOLVE_ONLY_THROUGH_AUTHENTICATED_P1"},
        "components": {"type": "object", "minProperties": 1},
    },
}


class Fixture:
    native_roles = (
        "p1_builder", "p1_schema", "checkpoint_component_manifest",
        "checkpoint_component_manifest_schema", "runner",
    )
    inherited_roles = ("grouping_rule",)

    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Role Resolver Test")
        self.git("remote", "add", "origin", "https://example.invalid/test.git")
        (self.root / "scripts").mkdir()
        (self.root / "schemas").mkdir()
        (self.root / "results").mkdir()
        builder = (
            "NATIVE_COMPONENTS = " + repr(self.native_roles) + "\n" +
            "INHERITED_V1_4_ROLES = " + repr(self.inherited_roles) + "\n"
        ).encode()
        self.write("scripts/build_benchmark_v15_p1.py", builder)
        self.write("schemas/p1.json", encoded(P1_SCHEMA))
        self.write("schemas/manifest.json", encoded(MANIFEST_SCHEMA))
        self.write("scripts/runner.py", b"#!/usr/bin/env python3\n")
        self.write("scripts/group.py", b"GROUPING = True\n")
        self.manifest = {
            "schema": "test-manifest",
            "authority": "RESOLVE_ONLY_THROUGH_AUTHENTICATED_P1",
            "components": {
                "runner": {"closure": "NATIVE_V1_5", "role": "runner"},
                "grouping": {"closure": "INHERITED_V1_4", "role": "grouping_rule"},
                # Repeated aliases are intentional and resolve to one exact role.
                "runner_runtime": {"closure": "NATIVE_V1_5", "role": "runner"},
            },
        }
        self.write("results/manifest.json", encoded(self.manifest))
        self.git("add", ".")
        self.git("commit", "-qm", "components")
        self.p1a = self.make_p1a()
        self.write("results/P1A.json", encoded(self.p1a))
        self.git("add", "results/P1A.json")
        self.git("commit", "-qm", "P1A")
        self.p1a_commit = self.git("rev-parse", "HEAD").strip()
        self.p1t = {
            "artifact_kind": "P1T",
            "p1a_commit": self.p1a_commit,
            "p1a": {"path": "results/P1A.json", "sha256": digest(encoded(self.p1a))},
            "attestation_policy": {"allowed_p1t_changed_paths": ["results/P1T.json"]},
        }
        self.write("results/P1T.json", encoded(self.p1t))
        self.git("add", "results/P1T.json")
        self.git("commit", "-qm", "P1T")
        self.p1t_commit = self.git("rev-parse", "HEAD").strip()
        self.git("update-ref", "refs/remotes/origin/main", self.p1t_commit)

    def close(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.root), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ).stdout

    def write(self, path: str, raw: bytes) -> None:
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)

    def ref(self, path: str, inherited: bool = False) -> dict[str, str]:
        row = {
            "path": path, "sha256": digest((self.root / path).read_bytes()),
            "content_class": "INHERITED_V1_4_EXACT" if inherited else "V1_5_PROTOCOL_ONLY_NO_TARGET_DATA",
        }
        if inherited:
            row.update({"source_commit": "0" * 40, "source_content_class": "PROTOCOL_ONLY_NO_TARGET_DATA"})
        return row

    def make_p1a(self) -> dict:
        native = {
            "p1_builder": self.ref("scripts/build_benchmark_v15_p1.py"),
            "p1_schema": self.ref("schemas/p1.json"),
            "checkpoint_component_manifest": self.ref("results/manifest.json"),
            "checkpoint_component_manifest_schema": self.ref("schemas/manifest.json"),
            "runner": self.ref("scripts/runner.py"),
        }
        inherited = {"grouping_rule": self.ref("scripts/group.py", True)}
        return {
            "artifact_kind": "P1A", "authority": "AUTHORITATIVE_P1",
            "components": native,
            "inherited_v1_4": {"selected_roles": ["grouping_rule"], "components": inherited},
        }

    def resolve(self) -> dict:
        return resolver.resolve_published_roles(
            self.root, self.p1t_commit, "results/P1T.json",
            expected_origin="https://example.invalid/test.git",
        )


class RoleResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = Fixture()

    def tearDown(self) -> None:
        self.fx.close()

    def test_exact_published_closure_resolves_once_per_role(self) -> None:
        proof = self.fx.resolve()
        self.assertTrue(proof["operational"])
        self.assertFalse(proof["target_data_present"])
        self.assertEqual(proof["resolved_role_count"], 2)
        runner = next(row for row in proof["resolved_roles"] if row["role"] == "runner")
        self.assertEqual(len(runner["selector_paths"]), 2)
        schema = json.loads((HERE.parent / "schemas/benchmark-p1-role-resolution-v1.5.schema.json").read_text())
        # Production constants are intentionally stricter than the injected test origin.
        production_shape = copy.deepcopy(proof)
        production_shape["publication"]["repository"] = resolver.PUBLIC_ORIGIN
        jsonschema.Draft7Validator(schema).validate(production_shape)

    def test_readiness_is_inert_and_schema_closed(self) -> None:
        value = resolver.readiness()
        self.assertFalse(value["operational"])
        self.assertFalse(value["caller_operational_override_accepted"])
        schema = json.loads((HERE.parent / "schemas/benchmark-p1-role-resolution-readiness-v1.5.schema.json").read_text())
        jsonschema.Draft7Validator(schema).validate(value)
        forged = dict(value, operational=True)
        self.assertTrue(list(jsonschema.Draft7Validator(schema).iter_errors(forged)))

    def test_unpublished_p1t_is_refused(self) -> None:
        self.fx.git("update-ref", "refs/remotes/origin/main", self.fx.p1a_commit)
        with self.assertRaisesRegex(resolver.RoleResolutionError, "not published"):
            self.fx.resolve()

    def test_dirty_worktree_component_is_refused(self) -> None:
        self.fx.write("scripts/runner.py", b"forged = True\n")
        with self.assertRaisesRegex(resolver.RoleResolutionError, "uncommitted/wrong-tree"):
            self.fx.resolve()

    def test_wrong_head_tree_component_is_refused(self) -> None:
        self.fx.write("scripts/runner.py", b"later = True\n")
        self.fx.git("add", "scripts/runner.py")
        self.fx.git("commit", "-qm", "change frozen role")
        self.fx.git("update-ref", "refs/remotes/origin/main", "HEAD")
        with self.assertRaisesRegex(resolver.RoleResolutionError, "wrong-tree"):
            self.fx.resolve()

    def test_missing_selector_role_is_refused(self) -> None:
        altered = copy.deepcopy(self.fx.manifest)
        altered["components"]["runner"]["role"] = "absent"
        self.fx.write("results/manifest.json", encoded(altered))
        self.fx.p1a["components"]["checkpoint_component_manifest"]["sha256"] = digest(encoded(altered))
        self._replace_pair(extra_stage="results/manifest.json")
        with self.assertRaisesRegex(resolver.RoleResolutionError, "missing NATIVE_V1_5 role absent"):
            self.fx.resolve()

    def test_extra_p1_role_is_refused(self) -> None:
        # A later forged P1 pair cannot reuse the authenticated builder's closed map.
        self.fx.p1a["components"]["extra"] = self.fx.ref("scripts/runner.py")
        self._replace_pair()
        with self.assertRaisesRegex(resolver.RoleResolutionError, "missing or extra native"):
            self.fx.resolve()

    def test_ambiguous_cross_closure_role_is_refused(self) -> None:
        self.fx.p1a["inherited_v1_4"]["components"]["runner"] = self.fx.ref("scripts/group.py", True)
        self.fx.p1a["inherited_v1_4"]["selected_roles"].append("runner")
        self._replace_pair()
        with self.assertRaisesRegex(resolver.RoleResolutionError, "ambiguous"):
            self.fx.resolve()

    def test_duplicate_json_role_key_is_refused(self) -> None:
        raw = encoded(self.fx.p1a)
        marker = b'"p1_builder": {'
        start = raw.index(marker)
        duplicate = b'"p1_builder": {},\n      '
        tampered = raw[:start] + duplicate + raw[start:]
        self.fx.write("results/P1A.json", tampered)
        self.fx.git("add", "results/P1A.json")
        self.fx.git("commit", "-qm", "duplicate-key P1A")
        p1a_commit = self.fx.git("rev-parse", "HEAD").strip()
        p1t = copy.deepcopy(self.fx.p1t)
        p1t["p1a_commit"] = p1a_commit
        p1t["p1a"]["sha256"] = digest(tampered)
        self.fx.write("results/P1T2.json", encoded(dict(p1t, attestation_policy={"allowed_p1t_changed_paths": ["results/P1T2.json"]})))
        self.fx.git("add", "results/P1T2.json")
        self.fx.git("commit", "-qm", "duplicate-key P1T")
        commit = self.fx.git("rev-parse", "HEAD").strip()
        self.fx.git("update-ref", "refs/remotes/origin/main", commit)
        with self.assertRaisesRegex(resolver.RoleResolutionError, "duplicate JSON key"):
            resolver.resolve_published_roles(self.fx.root, commit, "results/P1T2.json", expected_origin="https://example.invalid/test.git")

    def test_digest_substitution_is_refused(self) -> None:
        self.fx.p1a["components"]["runner"]["sha256"] = "f" * 64
        self._replace_pair()
        with self.assertRaisesRegex(resolver.RoleResolutionError, "digest mismatch|wrong-tree"):
            self.fx.resolve()

    def _replace_pair(self, extra_stage: str | None = None) -> None:
        self.fx.write("results/P1A2.json", encoded(self.fx.p1a))
        paths = ["results/P1A2.json"]
        if extra_stage is not None:
            paths.append(extra_stage)
        self.fx.git("add", *paths)
        self.fx.git("commit", "-qm", "replacement P1A")
        p1a_commit = self.fx.git("rev-parse", "HEAD").strip()
        p1t = copy.deepcopy(self.fx.p1t)
        p1t["p1a_commit"] = p1a_commit
        p1t["p1a"] = {"path": "results/P1A2.json", "sha256": digest(encoded(self.fx.p1a))}
        p1t["attestation_policy"]["allowed_p1t_changed_paths"] = ["results/P1T2.json"]
        self.fx.write("results/P1T2.json", encoded(p1t))
        self.fx.git("add", "results/P1T2.json")
        self.fx.git("commit", "-qm", "replacement P1T")
        self.fx.p1t_commit = self.fx.git("rev-parse", "HEAD").strip()
        self.fx.git("update-ref", "refs/remotes/origin/main", self.fx.p1t_commit)
        # resolve() uses the original path; update it for replacement cases.
        original = self.fx.resolve
        self.fx.resolve = lambda: resolver.resolve_published_roles(
            self.fx.root, self.fx.p1t_commit, "results/P1T2.json",
            expected_origin="https://example.invalid/test.git",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
