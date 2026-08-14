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
        self.p1r_raw = self.write_json(C.P1R_PATH, {"artifact_kind": "P1R"})
        self.git("add", "protocol.txt", C.P1R_PATH)
        self.git("commit", "-qm", "P1R activation")
        self.p1r = self.oid("HEAD")
        self.validation_input = self.repo / "validation-input.json"
        self.validation_input.write_bytes(b'{"frozen":true}\n')
        validation_sha = C.sha256(self.validation_input.read_bytes())
        activation = {
            "schema": C.P1R_RECEIPT_DOMAIN.decode(),
            "p1r": {"path": C.P1R_PATH, "sha256": C.sha256(self.p1r_raw)},
            "p1r_commit": self.p1r,
            "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
            "public_observation": {
                "workflow_repository": "Kuberwastaken/c5-k4",
                "workflow_path": ".github/workflows/method-v15-p1r-publication-observer.yml",
                "workflow_blob_sha256": "a" * 64,
                "workflow_ref": ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r",
                "run_id": 1, "run_attempt": 1,
                "server_observed_at_utc": "2026-08-16T19:00:00Z",
                "actions_run_projection_sha256": "b" * 64,
            },
            "validation_inputs_sha256": validation_sha,
            "validation_diagnostic_sha256": "c" * 64,
            "validator": {"path": "scripts/validate_benchmark_v15_candidate_base.py", "sha256": "d" * 64},
        }
        activation["receipt_sha256"] = C.sha256(
            C.P1R_RECEIPT_DOMAIN + b"\0" + C.canonical_json(activation)
        )
        self.primary_branch = self.git("branch", "--show-current").decode().strip()
        self.u1_receipt = {
            "schema": C.RECEIPT_SCHEMA, "artifact_kind": "U1_CHRONOLOGY_RECEIPT",
            "protocol_version": "1.5", "status": "VALID_U1",
            "p1": {
                "p1r_commit": self.p1r,
                "p1r_artifact": {"path": C.P1R_PATH, "sha256": C.sha256(self.p1r_raw)},
                "activation_receipt": activation,
                "p1r_activation_sha256": C.sha256(C.canonical_json(activation)),
                "validation_input": {
                    "path": "results/benchmark/v1.5-protocol/validation-input.json",
                    "sha256": validation_sha,
                },
            },
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
        activation = self.u1_receipt["p1"]["activation_receipt"]
        return C.verify_chain(
            self.repo, C.PUBLICATION_REF, self.p1r,
            activation_verifier=lambda *_: activation,
            validation_input_path=self.validation_input,
        )

    def test_bare_p1r_structure_without_full_verifier_fails_closed(self) -> None:
        with self.assertRaisesRegex(C.PublicChainError, "not wired"):
            C.verify_chain(self.repo, C.PUBLICATION_REF, self.p1r)

    def test_u1_activation_receipt_must_match_full_verifier(self) -> None:
        forged_u1 = json.loads(json.dumps(self.u1_receipt))
        forged_u1["p1"]["activation_receipt"]["activation_boundary"] = "FORGED"
        with self.assertRaisesRegex(C.PublicChainError, "exact authenticated P1R"):
            C._validate_u1(
                forged_u1, self.p1r,
                self.u1_receipt["p1"]["activation_receipt"],
            )

    def test_rich_activation_receipt_and_canonical_digest_are_not_downgradable(self) -> None:
        activation = self.u1_receipt["p1"]["activation_receipt"]
        C.validate_p1r_activation_receipt(
            activation, self.p1r, C.sha256(self.p1r_raw),
            C.sha256(self.validation_input.read_bytes()),
        )
        for mutate in (
            lambda row: row.pop("validator"),
            lambda row: row["public_observation"].__setitem__("run_attempt", 2),
            lambda row: row.__setitem__("receipt_sha256", "0" * 64),
        ):
            forged = json.loads(json.dumps(activation))
            mutate(forged)
            with self.assertRaises(C.PublicChainError):
                C.validate_p1r_activation_receipt(
                    forged, self.p1r, C.sha256(self.p1r_raw),
                    C.sha256(self.validation_input.read_bytes()),
                )
        forged_u1 = json.loads(json.dumps(self.u1_receipt))
        forged_u1["p1"]["p1r_activation_sha256"] = "0" * 64
        with self.assertRaisesRegex(C.PublicChainError, "canonical P1R activation digest"):
            C._validate_u1(forged_u1, self.p1r, activation)

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

    def test_merge_commit_and_ref_not_descending_from_p1r_fail_closed(self) -> None:
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
