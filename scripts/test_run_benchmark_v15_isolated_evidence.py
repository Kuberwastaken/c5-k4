#!/usr/bin/env python3
"""Adversarial contract tests for the exact-C isolated evidence runner."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

import jsonschema


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SPEC = importlib.util.spec_from_file_location("isolated_evidence", HERE / "run_benchmark_v15_isolated_evidence.py")
assert SPEC and SPEC.loader
R = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(R)


def command() -> list[str]:
    return [
        "/usr/local/bin/python3", "-I", "-S", "/inputs/verifier.py", "--candidate-readiness-verify",
        "--artifact", "/inputs/artifact.json", "--schema", "/inputs/artifact.schema.json",
        "--expected-status", "CANDIDATE_C_IMMUTABLE_WORM_ACCEPTED", "--candidate", "a" * 40,
        "--authority-root", "b" * 40, "--service-epoch", "c" * 64, "--challenge-nonce", "d" * 64,
    ]


def operational_contract() -> dict:
    return {
        "runtime_image": {
            "reference": "c5k4/python@sha256:" + "1" * 64,
            "repository_digest": "c5k4/python@sha256:" + "1" * 64,
            "image_id": "sha256:" + "2" * 64,
            "config_env": [],
        },
        "resource_limits": {
            "timeout_seconds": 30, "cpus_nano": 1000000000, "memory_bytes": 536870912,
            "memory_swap_bytes": 536870912, "pids": 32, "nofile": 64, "fsize_bytes": 1048576, "max_output_bytes": 16384,
        },
    }


def container_row(volume: str) -> dict:
    cmd = command()
    return {
        "Image": "sha256:" + "2" * 64,
        "Config": {
            "Image": "c5k4/python@sha256:" + "1" * 64, "User": "65534:65534",
            "Hostname": "c5k4-evidence", "Entrypoint": ["/usr/bin/env"],
            "Cmd": ["-i", *[f"{key}={R.EXPECTED_ENV[key]}" for key in sorted(R.EXPECTED_ENV)], *cmd],
            "WorkingDir": "/", "Env": [],
        },
        "HostConfig": {
            "NetworkMode": "none", "ReadonlyRootfs": True, "CapDrop": ["ALL"],
            "SecurityOpt": ["no-new-privileges=true", "seccomp=builtin"], "CgroupnsMode": "private",
            "IpcMode": "private", "PidMode": "", "UTSMode": "", "PidsLimit": 32,
            "Memory": 536870912, "MemorySwap": 536870912, "NanoCpus": 1000000000,
            "Ulimits": [{"Name": "nofile", "Soft": 64, "Hard": 64}, {"Name": "fsize", "Soft": 1048576, "Hard": 1048576}],
            "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=16777216,mode=1777"},
            "LogConfig": {"Type": "local", "Config": {"max-file": "1", "max-size": "16k"}},
        },
        "Mounts": [{"Type": "volume", "Name": volume, "Destination": "/inputs", "RW": False}],
    }


class FrozenContractTests(unittest.TestCase):
    def test_published_contract_is_valid_and_fail_closed(self) -> None:
        schema = json.loads(R.SCHEMA_PATH.read_text())
        contract = json.loads(R.CONTRACT_PATH.read_text())
        jsonschema.Draft7Validator(schema).validate(contract)
        self.assertFalse(contract["operational"])
        self.assertIsNotNone(contract["runtime_image"])
        self.assertIsNone(contract["daemon"])
        self.assertEqual(contract["runtime_image"]["reference"], "docker.io/library/python:3.13.7-slim-bookworm@sha256:781449467ffb6f04218f09b1ecdcdc7d22b289ee5da9ec498b024e24ad7a6db7")
        self.assertEqual(contract["runtime_image"]["image_id"], "sha256:444ec9cb9b03c3be7c8b18d4a5e82e7cc908e2c0032c0a6e759338a48250b4de")
        with self.assertRaisesRegex(R.IsolatedEvidenceRunnerError, "not operationally attested"):
            R._load_contract()

    def test_operational_shape_requires_digest_image_userns_and_signature(self) -> None:
        schema = json.loads(R.SCHEMA_PATH.read_text())
        contract = json.loads(R.CONTRACT_PATH.read_text())
        contract.update({"operational": True, "status": "EXACT_C_ISOLATED_EVIDENCE_RUNNER_OPERATIONAL", "activation_blockers": []})
        contract["runtime_image"] = {
            "reference": "c5k4/python:3.13@sha256:" + "1" * 64, "repository_digest": "c5k4/python@sha256:" + "1" * 64,
            "image_id": "sha256:" + "2" * 64, "platform": "linux/amd64", "config_user": None,
            "config_env": ["PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305", "PYTHON_VERSION=3.13.7", "PYTHON_SHA256=5462f9099dfd30e238def83c71d91897d8caa5ff6ebc7a50f14d4802cdaaa79a"],
            "config_entrypoint": None, "config_cmd": ["python3"], "config_working_dir": None,
            "verifier_dependency_policy": "PYTHON_3_13_STANDARD_LIBRARY_ONLY",
        }
        contract["daemon"] = {
            "host_id": "harness-1", "engine_version": "25.0.16", "engine_id": "engine-1",
            "security_options": ["name=cgroupns", "name=seccomp,profile=builtin", "name=userns"],
            "cgroup_version": "2", "cgroup_driver": "systemd", "default_runtime": "runc",
            "user_namespace_mode": "daemon-userns-remap", "info_projection_sha256": "3" * 64,
            "attestation": {"signer_id": "harness", "verification_key_base64": "A" * 43 + "=", "verification_key_sha256": "4" * 64, "signature": "A" * 86 + "=="},
        }
        jsonschema.Draft7Validator(schema).validate(contract)
        for mutation in ("mutable_tag", "no_userns", "no_signature"):
            bad = copy.deepcopy(contract)
            if mutation == "mutable_tag": bad["runtime_image"]["reference"] = "python:3.13"
            if mutation == "no_userns": bad["daemon"]["security_options"] = ["name=cgroupns", "name=seccomp,profile=builtin"]
            if mutation == "no_signature": del bad["daemon"]["attestation"]["signature"]
            with self.subTest(mutation=mutation), self.assertRaises(jsonschema.ValidationError):
                jsonschema.Draft7Validator(schema).validate(bad)


class InvocationClosureTests(unittest.TestCase):
    def make_closure(self, root: Path) -> None:
        inputs = root / "inputs"; inputs.mkdir()
        (inputs / "verifier.py").write_text("pass\n")
        (inputs / "artifact.schema.json").write_text("{}\n")
        (inputs / "artifact.json").write_text("{}\n")

    def test_exact_three_file_closure_and_command_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.make_closure(root)
            self.assertEqual(R._validated_inputs(root, command(), dict(R.EXPECTED_ENV), 30), root / "inputs")
            self.assertTrue(all((root / "inputs" / name).stat().st_mode & 0o777 == 0o444 for name in ("verifier.py", "artifact.schema.json", "artifact.json")))

    def test_extra_path_symlink_hardlink_argv_and_environment_fail(self) -> None:
        cases = ("extra", "symlink", "hardlink", "argv", "env")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); self.make_closure(root); argv = command(); env = dict(R.EXPECTED_ENV)
                if case == "extra": (root / "inputs" / "repo-secret").write_text("secret")
                if case == "symlink":
                    (root / "inputs" / "artifact.json").unlink(); (root / "inputs" / "artifact.json").symlink_to("artifact.schema.json")
                if case == "hardlink":
                    (root / "inputs" / "artifact.json").unlink(); os.link(root / "inputs" / "artifact.schema.json", root / "inputs" / "artifact.json")
                if case == "argv": argv += ["--escape", str(ROOT)]
                if case == "env": env["PYTHONPATH"] = str(ROOT)
                with self.assertRaises(R.IsolatedEvidenceRunnerError):
                    R._validated_inputs(root, argv, env, 30)


class EffectiveContainerAuditTests(unittest.TestCase):
    def test_exact_effective_container_is_accepted(self) -> None:
        R._audit_container(container_row("frozen-volume"), operational_contract(), "frozen-volume", command(), dict(R.EXPECTED_ENV))

    def test_every_escape_relevant_mutation_fails(self) -> None:
        mutations = {
            "network": lambda row: row["HostConfig"].update(NetworkMode="bridge"),
            "rootfs": lambda row: row["HostConfig"].update(ReadonlyRootfs=False),
            "caps": lambda row: row["HostConfig"].update(CapDrop=[]),
            "privs": lambda row: row["HostConfig"].update(SecurityOpt=["seccomp=builtin"]),
            "cgroupns": lambda row: row["HostConfig"].update(CgroupnsMode="host"),
            "pidns": lambda row: row["HostConfig"].update(PidMode="host"),
            "mount": lambda row: row["Mounts"].append({"Type": "bind", "Destination": "/repo", "RW": False}),
            "input_rw": lambda row: row["Mounts"][0].update(RW=True),
            "root_user": lambda row: row["Config"].update(User="0:0"),
            "env": lambda row: row["Config"]["Env"].append("PYTHONPATH=/repo"),
            "command": lambda row: row["Config"].update(Cmd=["-c", "open('/escape','w').write('x')"]),
            "memory": lambda row: row["HostConfig"].update(Memory=0),
            "pids": lambda row: row["HostConfig"].update(PidsLimit=0),
            "tmp_exec": lambda row: row["HostConfig"].update(Tmpfs={"/tmp": "rw"}),
        }
        for name, mutate in mutations.items():
            row = container_row("frozen-volume"); mutate(row)
            with self.subTest(name=name), self.assertRaises(R.IsolatedEvidenceRunnerError):
                R._audit_container(row, operational_contract(), "frozen-volume", command(), dict(R.EXPECTED_ENV))

    def test_source_has_no_direct_or_shell_fallback(self) -> None:
        raw = (HERE / "run_benchmark_v15_isolated_evidence.py").read_text()
        self.assertIn('"--pull", "never"', raw)
        self.assertIn('"o=bind,ro,nosuid,nodev,noexec"', raw)
        self.assertNotIn("shell=True", raw)
        self.assertNotIn("/bin/sh", raw)
        self.assertNotIn("linux_namespace_evidence_runner", raw)


if __name__ == "__main__":
    unittest.main()
