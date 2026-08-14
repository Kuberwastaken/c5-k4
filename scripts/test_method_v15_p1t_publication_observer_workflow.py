#!/usr/bin/env python3
"""Adversarial contract tests for the frozen P1T publication observer."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/method-v15-p1t-publication-observer.yml"
CHECKOUT = "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803"
SPEC = importlib.util.spec_from_file_location("p1t_observer", ROOT / "scripts/verify_benchmark_v15_p1t_publication.py")
assert SPEC and SPEC.loader
OBSERVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OBSERVER)


def parsed(raw: str) -> dict:
    value = yaml.load(raw, Loader=yaml.BaseLoader)
    if not isinstance(value, dict):
        raise ValueError("workflow must be a mapping")
    return value


def validate_contract(value: dict) -> None:
    if set(value) != {"name", "on", "permissions", "jobs"}:
        raise ValueError("workflow top-level closure differs")
    if value["on"] != {"push": {"branches": ["method-v1.5-p1"], "paths": [OBSERVER.P1T_PATH]}}:
        raise ValueError("workflow trigger is not exact branch/path push")
    if value["permissions"] != {"contents": "read"}:
        raise ValueError("workflow permissions are not read-only")
    if set(value["jobs"]) != {"observe-exact-p1t-publication"}:
        raise ValueError("workflow job closure differs")
    job = value["jobs"]["observe-exact-p1t-publication"]
    if job.get("runs-on") != "ubuntu-24.04" or len(job.get("steps", [])) != 2:
        raise ValueError("workflow runner/step closure differs")
    checkout, verify = job["steps"]
    if checkout.get("uses") != CHECKOUT or checkout.get("with") != {"fetch-depth": "2", "persist-credentials": "false"}:
        raise ValueError("checkout is not immutable and credential-free")
    script = verify.get("run", "")
    if (
        verify.get("shell") != "bash" or verify.get("env") != {"EXPECTED_PATH": OBSERVER.P1T_PATH}
        or 'test "$GITHUB_RUN_ATTEMPT" = "1"' not in script
        or 'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"' not in script
        or 'python3 scripts/verify_benchmark_v15_p1t_publication.py --commit "$GITHUB_SHA"' not in script
    ):
        raise ValueError("strict first-attempt observer validator is absent")


class WorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.value = parsed(WORKFLOW.read_text(encoding="utf-8"))

    def test_exact_contract_accepts(self) -> None:
        validate_contract(self.value)

    def test_broad_trigger_permissions_tag_rerun_or_weak_validator_rejected(self) -> None:
        mutations = []
        for mutate in (
            lambda v: v["on"]["push"].__setitem__("branches", ["main"]),
            lambda v: v["permissions"].__setitem__("contents", "write"),
            lambda v: v["jobs"]["observe-exact-p1t-publication"]["steps"][0].__setitem__("uses", "actions/checkout@v6"),
            lambda v: v["jobs"]["observe-exact-p1t-publication"]["steps"][1].__setitem__("run", "true"),
            lambda v: v["jobs"]["observe-exact-p1t-publication"].__setitem__("runs-on", "ubuntu-latest"),
        ):
            value = copy.deepcopy(self.value); mutate(value); mutations.append(value)
        for value in mutations:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_contract(value)


class ExactPublicationValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.git("init", "-q", "-b", "method-v1.5-p1")
        self.git("config", "user.name", "Observer Test")
        self.git("config", "user.email", "observer@example.invalid")
        p1a = {"artifact_kind": "P1A", "protocol_version": "1.5", "authority": "AUTHORITATIVE_P1"}
        self.write(OBSERVER.P1A_PATH, p1a)
        self.git("add", "-A"); self.git("commit", "-qm", "P1A")
        self.p1a = self.git("rev-parse", "HEAD")
        p1a_raw = (self.root / OBSERVER.P1A_PATH).read_bytes()
        import hashlib
        p1t = {
            "schema_version": "c5k4-method-v1.5-p1-1.0", "artifact_kind": "P1T", "protocol_version": "1.5",
            "p1a": {"path": OBSERVER.P1A_PATH, "sha256": hashlib.sha256(p1a_raw).hexdigest()},
            "p1a_commit": self.p1a, "p1a_published_at_utc": "2026-08-14T12:00:00Z",
            "attestation_policy": {"p1a_ancestor_required": True, "p1a_bytes_immutable": True, "allowed_p1t_changed_paths": [OBSERVER.P1T_PATH]},
        }
        self.write(OBSERVER.P1T_PATH, p1t)
        self.git("add", "-A"); self.git("commit", "-qm", "P1T")
        self.p1t = self.git("rev-parse", "HEAD")
        self.old_root = OBSERVER.ROOT; OBSERVER.ROOT = self.root

    def tearDown(self) -> None:
        OBSERVER.ROOT = self.old_root
        self.tmp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

    def write(self, path: str, value: dict) -> None:
        destination = self.root / path; destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    def test_exact_one_path_publication_accepts(self) -> None:
        OBSERVER.validate(self.p1t)

    def test_extra_changed_path_rejected(self) -> None:
        (self.root / "extra.txt").write_text("escape\n", encoding="utf-8")
        self.git("add", "-A"); self.git("commit", "-qm", "extra")
        with self.assertRaisesRegex(OBSERVER.ObserverError, "exactly the canonical P1T path"):
            OBSERVER.validate(self.git("rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
