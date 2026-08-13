#!/usr/bin/env python3
"""Adversarial tests for the Method v1.5 public checkpoint Git chain."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import jsonschema


SCRIPT = Path(__file__).with_name("verify_benchmark_v15_public_checkpoint_chain.py")
SPEC = importlib.util.spec_from_file_location("v15_public_chain", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


class PublicChainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="v15-public-chain-")
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.git("remote", "add", "origin", C.PUBLIC_REPOSITORY)
        self.write("protocol.txt", b"P1 frozen\n")
        self.git("add", "protocol.txt")
        self.git("commit", "-qm", "P1T")
        self.p1t = self.oid("HEAD")
        self.primary_branch = self.git("branch", "--show-current").decode().strip()
        self.u1_receipt = {
            "schema": C.RECEIPT_SCHEMA, "artifact_kind": "U1_CHRONOLOGY_RECEIPT",
            "protocol_version": "1.5", "status": "VALID_U1",
            "p1": {"p1t_commit": self.p1t},
            "upstream": {"capture_completed_at_utc": "2026-08-16T20:00:00Z"},
        }
        self.write_json(C.U1_PATH, self.u1_receipt)
        self.git("add", C.U1_PATH)
        self.git("commit", "-qm", "U1 genesis")
        self.genesis = self.oid("HEAD")
        self.git("update-ref", C.PUBLICATION_REF, self.genesis)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str, check: bool = True) -> bytes:
        result = subprocess.run(
            ["git", "-C", str(self.repo), *args], check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if check and result.returncode:
            raise AssertionError(result.stderr.decode())
        return result.stdout

    def oid(self, ref: str) -> str:
        return self.git("rev-parse", ref).decode().strip()

    def write(self, path: str, raw: bytes) -> None:
        destination = self.repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)

    def write_json(self, path: str, value: dict) -> bytes:
        raw = json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"
        self.write(path, raw)
        return raw

    def append_checkpoint(
        self, ordinal: int, scheduled: str, status: str = "QUOTA_FAIL",
        *, prior_override: object = ...,
    ) -> tuple[str, dict, bytes]:
        root = "checkpoints/" + scheduled.replace(":", "-")
        if ordinal == 1:
            prior = None
        else:
            prior_path = self.prior_path
            prior = {
                "path": prior_path, "sha256": C.sha256(self.prior_raw),
                "commit": self.prior_commit, "checkpoint_ordinal": ordinal - 1,
                "scheduled_for_utc": self.prior_receipt["scheduled_for_utc"],
                "status": self.prior_receipt["status"],
            }
        if prior_override is not ...:
            prior = prior_override
        receipt = {
            "schema": C.RECEIPT_SCHEMA, "artifact_kind": "CHECKPOINT_RECEIPT",
            "protocol_version": "1.5", "checkpoint_ordinal": ordinal,
            "scheduled_for_utc": scheduled, "status": status,
            "basis": {"previous_checkpoint": prior},
        }
        self.write_json(f"{root}/publication-manifest.json", {"ordinal": ordinal})
        self.write_json(f"{root}/quota-certificate.json", {
            "ordinal": ordinal,
            "aggregates": {"status": "PASS" if status == "QUOTA_PASS_U2" else "FAIL"},
        })
        raw = self.write_json(f"{root}/receipt.json", receipt)
        self.git("add", root)
        self.git("commit", "-qm", f"checkpoint {ordinal}")
        commit = self.oid("HEAD")
        self.git("update-ref", C.PUBLICATION_REF, commit)
        self.prior_path, self.prior_raw = f"{root}/receipt.json", raw
        self.prior_commit, self.prior_receipt = commit, receipt
        return commit, receipt, raw

    def verify(self) -> dict:
        return C.verify_chain(self.repo, C.PUBLICATION_REF, self.p1t)

    def test_valid_chain_derives_public_previous_blob_commit_and_next_tick(self) -> None:
        first, _, raw = self.append_checkpoint(1, "2026-08-17T00:17:00Z")
        proof = self.verify()
        self.assertEqual(proof["previous_checkpoint"]["commit"], first)
        self.assertEqual(proof["previous_checkpoint"]["receipt_blob_sha256"], C.sha256(raw))
        self.assertEqual(proof["next_checkpoint"], {
            "ordinal": 2, "scheduled_for_utc": "2026-08-18T00:17:00Z",
            "required_parent_commit": first,
        })
        self.assertEqual(proof["normal_push_must_use_lease_tip"], first)
        self.assertEqual(proof["proof_sha256"], C.proof_digest(proof))
        schema = json.loads(
            (SCRIPT.parents[1] / "schemas/benchmark-public-checkpoint-chain-proof-v1.5.schema.json").read_text()
        )
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(proof)

    def test_skipped_date_and_forged_previous_binding_fail_closed(self) -> None:
        self.append_checkpoint(1, "2026-08-17T00:17:00Z")
        self.append_checkpoint(2, "2026-08-19T00:17:00Z")
        with self.assertRaisesRegex(C.PublicChainError, "duplicated, skipped"):
            self.verify()

        self.git("reset", "--hard", self.prior_commit + "^")
        self.git("update-ref", C.PUBLICATION_REF, self.oid("HEAD"))
        self.append_checkpoint(2, "2026-08-18T00:17:00Z", prior_override=None)
        with self.assertRaisesRegex(C.PublicChainError, "predecessor binding"):
            self.verify()

    def test_extra_path_and_non_add_change_fail_closed(self) -> None:
        root = "checkpoints/2026-08-17T00-17-00Z"
        self.append_checkpoint(1, "2026-08-17T00:17:00Z")
        self.write(f"{root}/extra.txt", b"not frozen\n")
        self.git("add", f"{root}/extra.txt")
        self.git("commit", "-qm", "extra commit")
        self.git("update-ref", C.PUBLICATION_REF, self.oid("HEAD"))
        with self.assertRaisesRegex(C.PublicChainError, "exactly three"):
            self.verify()

    def test_merge_commit_and_ref_not_descending_from_p1t_fail_closed(self) -> None:
        self.append_checkpoint(1, "2026-08-17T00:17:00Z")
        self.git("checkout", "-qb", "side", self.genesis)
        self.write("side.txt", b"side\n")
        self.git("add", "side.txt")
        self.git("commit", "-qm", "side")
        self.git("checkout", "-q", self.primary_branch)
        self.git("merge", "--no-ff", "-qm", "merge forbidden", "side")
        self.git("update-ref", C.PUBLICATION_REF, self.oid("HEAD"))
        with self.assertRaisesRegex(C.PublicChainError, "exactly one parent"):
            self.verify()

        other = self.repo.parent / (self.repo.name + "-other")
        subprocess.run(["git", "init", "-q", str(other)], check=True)
        subprocess.run(["git", "-C", str(other), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(other), "config", "user.email", "test@example.invalid"], check=True)
        (other / "x").write_text("x")
        subprocess.run(["git", "-C", str(other), "add", "x"], check=True)
        subprocess.run(["git", "-C", str(other), "commit", "-qm", "unrelated"], check=True)
        self.git("fetch", str(other), "HEAD:refs/heads/unrelated")
        self.git("update-ref", C.PUBLICATION_REF, self.oid("refs/heads/unrelated"))
        with self.assertRaises(C.PublicChainError):
            self.verify()

    def test_first_pass_is_terminal(self) -> None:
        self.append_checkpoint(1, "2026-08-17T00:17:00Z", "QUOTA_PASS_U2")
        proof = self.verify()
        self.assertTrue(proof["terminal"])
        self.assertIsNone(proof["next_checkpoint"])
        self.append_checkpoint(2, "2026-08-18T00:17:00Z", "QUOTA_FAIL")
        with self.assertRaisesRegex(C.PublicChainError, "continues after"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
