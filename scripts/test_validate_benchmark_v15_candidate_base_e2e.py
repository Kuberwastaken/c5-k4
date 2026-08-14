#!/usr/bin/env python3
"""Monolithic signed end-to-end test for the Method v1.5 P1R gate.

The happy path uses real Git objects and real Ed25519 signatures.  Only the
public-network lookup and the fixed isolated-runner process boundary are
replaced by deterministic fakes.
"""

from __future__ import annotations

import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SPEC = importlib.util.spec_from_file_location(
    "candidate_base_validator_e2e", HERE / "validate_benchmark_v15_candidate_base.py"
)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def write_json(path: Path, value: object) -> bytes:
    raw = V.canonical_json(value)
    write(path, raw)
    return raw


def embedded(value: dict[str, object]) -> dict[str, str]:
    raw = V.canonical_json(value)
    return {
        "encoding": "BASE64_CANONICAL_JSON_UTF8",
        "canonical_json_base64": base64.b64encode(raw).decode("ascii"),
        "sha256": V.sha256(raw),
    }


def p1_embedded(value: dict[str, object]) -> dict[str, object]:
    raw = V.canonical_json(value)
    return {
        "schema": "c5k4-method-v1.5-p1-embedded-readiness-package-1.0",
        "status": "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R",
        "encoding": "BASE64_CANONICAL_JSON_UTF8",
        "canonical_package_base64": base64.b64encode(raw).decode("ascii"),
        "package_sha256": V.sha256(raw),
        "assembler_verification_scope":
            "STRUCTURAL_CANONICAL_PACKAGE_ONLY_CRYPTO_UNVERIFIED_AWAITING_PUBLIC_P1R",
        "activation_authority": False,
    }


class SignedTopologyFixture:
    P0A_PATH = "results/benchmark/v1.4-protocol/P0A.json"
    P0T_PATH = "results/benchmark/v1.4-protocol/P0T.json"
    A0_PATH = "results/benchmark/v1.5-protocol/A0.json"
    CONFIG_PATH = "results/benchmark/v1.5-protocol/e2e-components.json"
    ARTIFACT_SCHEMA_PATH = "schemas/e2e-operational-evidence.schema.json"
    VERIFIER_PATH = "scripts/e2e_operational_evidence_verifier.py"
    PUBLIC_REMOTE = "https://github.com/Kuberwastaken/c5-k4"
    REFS = {
        "a0": "refs/tags/method-v1.5-e2e-a0",
        "p0t": "refs/tags/method-v1.4-e2e-p0t",
        "candidate": "refs/tags/method-v1.5-e2e-c",
        "p1t": "refs/heads/method-v1.5-p1",
        "p1r": V.P1R_PUBLIC_REF,
    }

    def __init__(self, root: Path) -> None:
        self.root = root
        self.keys: dict[tuple[str, str], Ed25519PrivateKey] = {}
        self.key_paths: list[dict[str, str]] = []
        self.evidence_paths: list[dict[str, str]] = []
        self.remote_bindings: dict[str, str] = {}
        self.actions_runs: dict[int, dict[str, object]] = {}
        self._init_git()
        self._generate_authorities()
        self._build_p0_source()
        self._build_p0t()
        self._build_a0()
        self._build_candidate()
        self._build_signed_readiness_and_transition()
        self._build_request()

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        return result.stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")

    def tree(self, commit: str) -> str:
        return self.git("rev-parse", f"{commit}^{{tree}}")

    def _init_git(self) -> None:
        self.root.mkdir(parents=True)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Candidate E2E")
        self.git("config", "user.email", "candidate-e2e@example.invalid")

    def _generate_authorities(self) -> None:
        identities = [
            ("CONTROLLED_HARNESS_READINESS_KEY", "harness"),
            ("FROZEN_EXPERIMENTER_IDENTITY", "experimenter"),
            *(("OPERATIONAL_EVIDENCE_ISSUER", f"issuer-{i}") for i in range(7)),
            ("INDEPENDENT_RECOMPILER", "recompiler-a"),
            ("INDEPENDENT_RECOMPILER", "recompiler-b"),
        ]
        key_root = self.root.parent / "keys"
        key_root.mkdir()
        for signer_class, signer_id in identities:
            private = Ed25519PrivateKey.generate()
            public = private.public_key().public_bytes(
                serialization.Encoding.Raw, serialization.PublicFormat.Raw
            )
            path = key_root / f"{signer_id}.pub"
            path.write_bytes(public)
            self.keys[(signer_class, signer_id)] = private
            self.key_paths.append({
                "signer_class": signer_class, "signer_id": signer_id, "path": str(path)
            })

    def public_row(self, signer_class: str, signer_id: str, **extra: object) -> dict[str, object]:
        private = self.keys[(signer_class, signer_id)]
        raw = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return {
            "signer_class": signer_class, **extra, "signer_id": signer_id,
            "verification_key_sha256": V.sha256(raw),
        }

    def sign(self, identity: tuple[str, str], domain: str, digest: str) -> str:
        return base64.b64encode(
            self.keys[identity].sign(V.signature_message(domain, digest))
        ).decode("ascii")

    def _build_p0_source(self) -> None:
        p0_builder = b'REQUIRED_COMPONENTS = ("p0_builder", "target_data_audit_rule")\n'
        audit_rule = b"target-blind e2e audit rule\n"
        write(self.root / "scripts/e2e_p0_builder.py", p0_builder)
        write(self.root / "docs/e2e-target-data-audit-rule.txt", audit_rule)
        permissive_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#", "type": "object"
        }
        write_json(self.root / V.P0_SCHEMA_PATH, permissive_schema)
        components = {
            "p0_builder": {
                "path": "scripts/e2e_p0_builder.py", "sha256": V.sha256(p0_builder),
                "content_class": V.SOURCE_CONTENT_CLASS,
            },
            "target_data_audit_rule": {
                "path": "docs/e2e-target-data-audit-rule.txt", "sha256": V.sha256(audit_rule),
                "content_class": V.SOURCE_CONTENT_CLASS,
            },
        }
        receipt = {
            "schema_version": "c5k4-method-v1.4-target-data-audit-receipt-1.0",
            "audit_rule_sha256": V.sha256(audit_rule),
            "components": [
                {"role": role, "path": row["path"], "sha256": row["sha256"],
                 "classification": V.SOURCE_CONTENT_CLASS}
                for role, row in components.items()
            ],
            "final_eligible_rows_detected": 0, "selected_clusters_detected": 0,
            "statement_text_detected": 0, "semantic_target_analysis_detected": 0,
        }
        receipt_raw = write_json(
            self.root / "results/benchmark/v1.4-protocol/e2e-target-data-audit.json", receipt
        )
        p0a = {
            "schema_version": "c5k4-method-v1.4-p0-1.0", "artifact_kind": "P0A",
            "authority": "AUTHORITATIVE_P0", "protocol_version": "1.4",
            "components": components, "allowlisted_registry_producers": [],
            "prototype_artifacts": [],
            "target_data_audit_receipt": {
                "path": "results/benchmark/v1.4-protocol/e2e-target-data-audit.json",
                "sha256": V.sha256(receipt_raw),
            },
            "final_eligible_rows": [], "selected_clusters": [], "target_semantics": [],
        }
        self.p0a_raw = write_json(self.root / self.P0A_PATH, p0a)
        self.p0a = self.commit("e2e P0A source")

    def _build_p0t(self) -> None:
        p0t = {
            "schema_version": "c5k4-method-v1.4-p0-1.0", "artifact_kind": "P0T",
            "protocol_version": "1.4",
            "p0a": {"path": self.P0A_PATH, "sha256": V.sha256(self.p0a_raw)},
            "p0a_commit": self.p0a,
        }
        self.p0t_raw = write_json(self.root / self.P0T_PATH, p0t)
        self.p0t = self.commit("e2e P0T")

    def _build_a0(self) -> None:
        shutil.copy2(REPO / V.AUTHORITY_SCHEMA_PATH, self.root / V.AUTHORITY_SCHEMA_PATH)
        issuers = [
            self.public_row("OPERATIONAL_EVIDENCE_ISSUER", f"issuer-{index}", domain=domain)
            for index, domain in enumerate(V.READINESS_DOMAINS)
        ]
        authority = {
            "schema": "c5k4-method-v1.5-public-readiness-authority-root-1.0",
            "status": "PUBLIC_PRE_C_READINESS_AUTHORITIES_FROZEN",
            "protocol_version": "1.5", "authority_epoch_id": "epoch-e2e",
            "created_at_utc": "2026-08-14T09:00:00Z", "target_specific": False,
            "controlled_harness": self.public_row("CONTROLLED_HARNESS_READINESS_KEY", "harness"),
            "experimenters": [self.public_row("FROZEN_EXPERIMENTER_IDENTITY", "experimenter")],
            "evidence_issuers": issuers,
            "independent_recompilers": [
                self.public_row("INDEPENDENT_RECOMPILER", "recompiler-a"),
                self.public_row("INDEPENDENT_RECOMPILER", "recompiler-b"),
            ],
            "nonintervention_contract_sha256": "1" * 64,
            "challenge_namespace_sha256": "2" * 64,
        }
        authority["authority_root_sha256"] = V.domain_digest(
            "c5k4-method-v1.5-public-readiness-authority-root-1.0", authority
        )
        self.authority_raw = write_json(self.root / self.A0_PATH, authority)
        self.authority = authority
        self.a0 = self.commit("e2e pre-C authority root")

    def _copy_candidate_file(self, relative: str) -> None:
        write(self.root / relative, (REPO / relative).read_bytes())

    def _build_candidate(self) -> None:
        for relative in (
            V.VALIDATOR_PATH, V.INPUT_SCHEMA_PATH, V.OUTPUT_SCHEMA_PATH,
            V.EVIDENCE_SCHEMA_PATH, V.RECOMPILE_SCHEMA_PATH, V.PACKAGE_SCHEMA_PATH,
            V.P1R_SCHEMA_PATH, V.ACTIVATION_RECEIPT_SCHEMA_PATH,
            V.ISOLATED_RUNNER_PATH, V.ISOLATED_RUNNER_SCHEMA_PATH,
            V.ISOLATED_RUNNER_TEST_PATH, V.P1_SCHEMA_PATH,
        ):
            self._copy_candidate_file(relative)
        write(self.root / V.P1_BUILDER_PATH, b'NATIVE_COMPONENTS = ("protocol_document",)\nINHERITED_V1_4_ROLES = ("p0_builder",)\n')
        workflow = b"name: frozen-e2e-observer\n"
        write(self.root / V.P1T_OBSERVER_WORKFLOW_PATH, workflow)
        write(self.root / V.P1R_OBSERVER_WORKFLOW_PATH, workflow)
        self.workflow_raw = workflow
        protocol_raw = write_json(
            self.root / "results/benchmark/v1.5-protocol/e2e-protocol.json",
            {"schema": "c5k4-e2e-protocol-1.0", "target_specific": False},
        )
        artifact_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#", "type": "object",
            "required": ["status", "candidate_commit", "authority_root_commit",
                         "service_epoch_binding_sha256", "challenge_nonce", "observed_at_utc",
                         "valid_through_utc", "artifact_sha256", "signature"],
            "additionalProperties": False,
            "properties": {
                "status": {"type": "string"}, "candidate_commit": {"type": "string"},
                "authority_root_commit": {"type": "string"},
                "service_epoch_binding_sha256": {"type": "string"},
                "challenge_nonce": {"type": "string"}, "observed_at_utc": {"type": "string"},
                "valid_through_utc": {"type": "string"}, "artifact_sha256": {"type": "string"},
                "signature": {"type": "string"},
            },
        }
        self.artifact_schema_raw = write_json(self.root / self.ARTIFACT_SCHEMA_PATH, artifact_schema)
        self.verifier_raw = b"# exact-C frozen verifier; executed only behind isolated runner\n"
        write(self.root / self.VERIFIER_PATH, self.verifier_raw)
        contract = json.loads((REPO / V.ISOLATED_RUNNER_CONTRACT_PATH).read_text())
        contract.update({
            "status": "EXACT_C_ISOLATED_EVIDENCE_RUNNER_OPERATIONAL", "operational": True,
            "daemon": {
                "host_id": "e2e-host", "engine_version": "27.5.1", "engine_id": "e2e-engine",
                "security_options": ["name=cgroupns", "name=seccomp,profile=builtin", "name=userns"],
                "cgroup_version": "2", "cgroup_driver": "systemd", "default_runtime": "runc",
                "user_namespace_mode": "daemon-userns-remap", "info_projection_sha256": "3" * 64,
                "attestation": {
                    "signer_id": "harness",
                    "verification_key_base64": base64.b64encode(
                        self.keys[("CONTROLLED_HARNESS_READINESS_KEY", "harness")].public_key().public_bytes(
                            serialization.Encoding.Raw, serialization.PublicFormat.Raw
                        )
                    ).decode("ascii"),
                    "verification_key_sha256": self.authority["controlled_harness"]["verification_key_sha256"],
                    "signature": base64.b64encode(b"x" * 64).decode("ascii"),
                },
            },
            "activation_blockers": [],
        })
        write_json(self.root / V.ISOLATED_RUNNER_CONTRACT_PATH, contract)
        config = {
            "schema_version": "c5k4-method-v1.5-p1-components-1.0", "authority": "AUTHORITATIVE_P1",
            "components": {"protocol_document": {
                "path": "results/benchmark/v1.5-protocol/e2e-protocol.json",
                "sha256": V.sha256(protocol_raw),
            }},
            "v1_4_p0a": {"path": self.P0A_PATH, "sha256": V.sha256(self.p0a_raw)},
        }
        write_json(self.root / self.CONFIG_PATH, config)
        self.candidate = self.commit("e2e exact candidate C")
        self.candidate_tree = self.tree(self.candidate)
        self.remote_bindings = {
            self.REFS["a0"]: self.a0, self.REFS["p0t"]: self.p0t,
            self.REFS["candidate"]: self.candidate,
        }

    def _fake_remote_bytes(self, ref: str, commit: str) -> bytes:
        return f"{commit}\t{ref}\n".encode("ascii")

    def _build_signed_readiness_and_transition(self) -> None:
        repo = V.GitRepository(self.root)
        p0t_input = {
            "commit": self.p0t, "root_tree": self.tree(self.p0t), "path": self.P0T_PATH,
            "public_remote_ref": self.REFS["p0t"],
        }
        closures = V.compile_closures(repo, self.candidate, self.CONFIG_PATH, p0t_input)
        self.closures = closures
        authority_binding = {
            "commit": self.a0, "root_tree": self.tree(self.a0), "path": self.A0_PATH,
            "sha256": V.sha256(self.authority_raw),
        }
        epoch = "4" * 64
        evidence_rows = []
        evidence_root = self.root.parent / "evidence"
        evidence_root.mkdir()
        for index, domain in enumerate(V.READINESS_DOMAINS):
            issuer_id = f"issuer-{index}"
            artifact = {
                "status": V.DOMAIN_STATUSES[domain], "candidate_commit": self.candidate,
                "authority_root_commit": self.a0, "service_epoch_binding_sha256": epoch,
                "challenge_nonce": f"{index + 10:064x}",
                "observed_at_utc": "2026-08-14T10:00:00Z",
                "valid_through_utc": "2026-08-15T10:00:00Z", "signature": "opaque",
            }
            artifact["artifact_sha256"] = V.domain_digest(
                f"c5k4-method-v1.5-e2e-{index}", V._without(artifact, "signature")
            )
            artifact_raw = V.canonical_json(artifact)
            artifact_path = evidence_root / f"{index}.json"
            artifact_path.write_bytes(artifact_raw)
            row = {
                "domain": domain, "accepted_status": V.DOMAIN_STATUSES[domain],
                "artifact": {
                    "scheme": "S3_OBJECT_LOCK_VERSION", "bucket_arn": "arn:aws:s3:::c5k4-e2e",
                    "object_key": f"evidence/{index}.json", "version_id": f"version-{index}",
                    "object_sha256": V.sha256(artifact_raw), "size_bytes": len(artifact_raw),
                    "retention_until_utc": "2026-08-16T10:00:00Z",
                },
                "artifact_schema": {"path": self.ARTIFACT_SCHEMA_PATH, "sha256": V.sha256(self.artifact_schema_raw)},
                "frozen_verifier": {"path": self.VERIFIER_PATH, "sha256": V.sha256(self.verifier_raw)},
                "verifier_protocol": "C5K4_CANDIDATE_READINESS_VERIFY_V1",
                "self_digest_field": "artifact_sha256", "self_digest_domain": f"c5k4-method-v1.5-e2e-{index}",
                "self_digest_excluded_fields": ["signature"], "candidate_commit": self.candidate,
                "authority_root_commit": self.a0, "service_epoch_binding_sha256": epoch,
                "challenge_nonce": artifact["challenge_nonce"], "observed_at_utc": artifact["observed_at_utc"],
                "valid_through_utc": artifact["valid_through_utc"],
                "issuer": {"signer_id": issuer_id,
                           "verification_key_sha256": self.authority["evidence_issuers"][index]["verification_key_sha256"]},
            }
            row["acceptance_sha256"] = V.domain_digest(
                "c5k4-method-v1.5-candidate-base-operational-evidence-row-1.0", row
            )
            row["signature"] = self.sign(
                ("OPERATIONAL_EVIDENCE_ISSUER", issuer_id),
                "c5k4-method-v1.5-operational-evidence-row-signature-1.0", row["acceptance_sha256"]
            )
            evidence_rows.append(row)
            self.evidence_paths.append({"domain": domain, "path": str(artifact_path)})
        evidence = {
            "schema": "c5k4-method-v1.5-candidate-base-operational-evidence-1.0",
            "status": "CANDIDATE_BASE_TYPED_OPERATIONAL_EVIDENCE_ACCEPTED", "protocol_version": "1.5",
            "candidate": {"commit": self.candidate, "root_tree": self.candidate_tree},
            "authority_root": authority_binding, "service_epoch_binding_sha256": epoch,
            "compiled_at_utc": "2026-08-14T10:00:01Z", "valid_through_utc": "2026-08-15T10:00:00Z",
            "evidence": evidence_rows,
        }
        evidence["bundle_sha256"] = V.domain_digest(
            "c5k4-method-v1.5-candidate-base-operational-evidence-1.0", evidence
        )
        evidence_envelope = embedded(evidence)
        closure_summary = {
            "native": {"row_count": len(closures["native_rows"]), "sha256": closures["native_sha256"]},
            "inherited": {"row_count": len(closures["inherited_rows"]), "sha256": closures["inherited_sha256"]},
            "full_source": {"row_count": len(closures["source_rows"]), "sha256": closures["full_source_sha256"]},
            "aggregate_sha256": closures["aggregate_sha256"],
        }
        compiler = V.compiler_refs_v2(repo, self.candidate)
        package = {
            "schema": "c5k4-method-v1.5-candidate-base-readiness-package-1.0",
            "status": "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R", "protocol_version": "1.5",
            "candidate": {"commit": self.candidate, "root_tree": self.candidate_tree},
            "authority_root": authority_binding, "closures": closure_summary,
            "operational_evidence": evidence_envelope, "compiler": compiler,
            "structural_json_key_audit": {
                "algorithm": "STRUCTURAL_JSON_KEY_AUDIT_V1_5",
                "scope": ["V1_5_NATIVE_JSON_BLOBS", "V1_4_SELECTED_INHERITED_JSON_BLOBS",
                          "V1_4_FULL_P0A_REFERENCED_JSON_BLOBS"],
                "json_blob_count": closures["json_blob_count"], "candidate_identities_keys_detected": 0,
                "statement_text_keys_detected": 0, "target_rankings_keys_detected": 0,
                "target_semantic_analysis_keys_detected": 0,
                "does_not_claim_free_text_or_python_semantic_audit": True,
            },
        }
        package["payload_sha256"] = V.domain_digest(
            "c5k4-method-v1.5-candidate-base-readiness-payload-2.0", V.readiness_payload_source(package)
        )
        package["authority_signatures"] = []
        for signer_class, signer_id in (
            ("CONTROLLED_HARNESS_READINESS_KEY", "harness"),
            ("FROZEN_EXPERIMENTER_IDENTITY", "experimenter"),
        ):
            public = self.public_row(signer_class, signer_id)
            package["authority_signatures"].append({
                **public, "algorithm": "Ed25519",
                "signature": self.sign(
                    (signer_class, signer_id),
                    "c5k4-method-v1.5-candidate-base-readiness-signature-2.0", package["payload_sha256"]
                ),
            })
        package["independent_recompiles"] = []
        for index, signer_id in enumerate(("recompiler-a", "recompiler-b")):
            signer = self.public_row("INDEPENDENT_RECOMPILER", signer_id)
            attestation = {
                "schema": "c5k4-method-v1.5-candidate-base-independent-recompile-1.0",
                "status": "INDEPENDENT_EXACT_C_RECOMPILE_PASSED", "protocol_version": "1.5",
                "payload_sha256": package["payload_sha256"],
                "closure_aggregate_sha256": closures["aggregate_sha256"],
                "operational_evidence_bundle_sha256": evidence["bundle_sha256"],
                "authority_root_commit": self.a0, "authority_root_sha256": authority_binding["sha256"],
                "compiler_closure_sha256": V.compiler_closure_sha256(compiler),
                "validator_sha256": compiler["validator"]["sha256"],
                "execution_id": f"execution-{index}", "execution_host_id": f"host-{index}",
                "completed_at_utc": f"2026-08-14T10:00:0{2 + index}Z", "signer": signer,
            }
            attestation["attestation_sha256"] = V.domain_digest(
                "c5k4-method-v1.5-candidate-base-independent-recompile-1.0", attestation
            )
            attestation["signature"] = self.sign(
                ("INDEPENDENT_RECOMPILER", signer_id),
                "c5k4-method-v1.5-independent-recompile-signature-1.0",
                attestation["attestation_sha256"],
            )
            package["independent_recompiles"].append(embedded(attestation))
        package["package_sha256"] = V.domain_digest(
            "c5k4-method-v1.5-candidate-base-readiness-package-1.0", package
        )
        self.package = package
        p1a = copy.deepcopy(closures["expected_p1a"])
        p1a["candidate_base_readiness"] = p1_embedded(package)
        self.p1a_raw = write_json(self.root / V.P1A_PATH, p1a)
        self.p1a_commit = self.commit("e2e P1A")
        p1t = {
            "schema_version": "c5k4-method-v1.5-p1-1.0", "artifact_kind": "P1T",
            "protocol_version": "1.5", "p1a": {"path": V.P1A_PATH, "sha256": V.sha256(self.p1a_raw)},
            "p1a_commit": self.p1a_commit, "p1a_published_at_utc": "2026-08-14T10:00:04Z",
            "attestation_policy": {"p1a_ancestor_required": True, "p1a_bytes_immutable": True,
                                   "allowed_p1t_changed_paths": [V.P1T_PATH]},
        }
        self.p1t_raw = write_json(self.root / V.P1T_PATH, p1t)
        self.p1t_commit = self.commit("e2e P1T")
        self.remote_bindings[self.REFS["p1t"]] = self.p1t_commit
        p1t_run = self._actions_run(
            101, self.p1t_commit, "method-v1.5-p1", V.P1T_OBSERVER_WORKFLOW_PATH,
            "2026-08-14T10:01:02Z",
        )
        self.actions_runs[101] = p1t_run
        projection = V.actions_run_projection(p1t_run)
        transcript = b"".join(
            self._fake_remote_bytes(ref, commit) for ref, commit in (
                (self.REFS["a0"], self.a0), (self.REFS["p0t"], self.p0t),
                (self.REFS["candidate"], self.candidate), (self.REFS["p1t"], self.p1t_commit),
            )
        )
        observation = {
            "public_remote_url": self.PUBLIC_REMOTE,
            "authority_root": {"ref": self.REFS["a0"], "commit": self.a0},
            "v1_4_p0t": {"ref": self.REFS["p0t"], "commit": self.p0t},
            "candidate_c": {"ref": self.REFS["candidate"], "commit": self.candidate},
            "p1t": {"ref": self.REFS["p1t"], "commit": self.p1t_commit},
            "observed_at_utc": p1t_run["updated_at"], "ls_remote_stdout_sha256": V.sha256(transcript),
            "observer": {
                "workflow_repository": "Kuberwastaken/c5-k4", "workflow_path": V.P1T_OBSERVER_WORKFLOW_PATH,
                "workflow_ref": f"{V.P1T_OBSERVER_WORKFLOW_PATH}@{self.REFS['p1t']}",
                "workflow_blob_sha256": V.sha256(self.workflow_raw), "run_id": 101, "run_attempt": 1,
                "actions_run_projection_sha256": V.domain_digest(
                    "c5k4-method-v1.5-p1t-actions-run-projection-1.0", projection
                ),
            },
        }
        p1r = {
            "schema_version": "c5k4-method-v1.5-p1r-1.0", "artifact_kind": "P1R",
            "status": "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY", "protocol_version": "1.5",
            "p1t": {"path": V.P1T_PATH, "sha256": V.sha256(self.p1t_raw)}, "p1t_commit": self.p1t_commit,
            "observation": observation,
            "activation_policy": {"structural_draft_only": True, "p1r_is_activation_boundary": False,
                                  "p1t_alone_is_activation_boundary": False, "full_exact_c_replay_required": True,
                                  "p1r_parent_must_be_exact_p1t": True,
                                  "allowed_p1r_changed_paths": [V.P1R_PATH], "public_p1r_ref_required": True},
        }
        self.p1r_raw = write_json(self.root / V.P1R_PATH, p1r)
        self.p1r_commit = self.commit("e2e P1R")
        self.remote_bindings[self.REFS["p1r"]] = self.p1r_commit
        p1r_run = self._actions_run(
            102, self.p1r_commit, "method-v1.5-p1r", V.P1R_OBSERVER_WORKFLOW_PATH,
            "2026-08-14T10:02:02Z",
        )
        self.actions_runs[102] = p1r_run
        p1r_projection = V.actions_run_projection(p1r_run)
        self.publication_observer = {
            "workflow_repository": "Kuberwastaken/c5-k4", "workflow_path": V.P1R_OBSERVER_WORKFLOW_PATH,
            "workflow_ref": f"{V.P1R_OBSERVER_WORKFLOW_PATH}@{V.P1R_PUBLIC_REF}",
            "workflow_blob_sha256": V.sha256(self.workflow_raw), "run_id": 102, "run_attempt": 1,
            "server_observed_at_utc": p1r_run["updated_at"],
            "actions_run_projection_sha256": V.domain_digest(
                "c5k4-method-v1.5-p1r-actions-run-projection-1.0", p1r_projection
            ),
        }

    @staticmethod
    def _actions_run(run_id: int, head: str, branch: str, path: str, updated: str) -> dict[str, object]:
        return {
            "id": run_id, "run_attempt": 1, "event": "push", "status": "completed",
            "conclusion": "success", "head_sha": head, "head_branch": branch, "path": path,
            "created_at": "2026-08-14T10:01:00Z", "run_started_at": "2026-08-14T10:01:01Z",
            "updated_at": updated, "repository": {"full_name": "Kuberwastaken/c5-k4"},
            "head_repository": {"full_name": "Kuberwastaken/c5-k4"},
        }

    def _build_request(self) -> None:
        self.request = {
            "schema": "c5k4-method-v1.5-candidate-base-validation-input-2.0", "protocol_version": "1.5",
            "authority_root": {"commit": self.a0, "root_tree": self.tree(self.a0), "path": self.A0_PATH,
                               "public_remote_ref": self.REFS["a0"]},
            "v1_4_p0t": {"commit": self.p0t, "root_tree": self.tree(self.p0t), "path": self.P0T_PATH,
                          "public_remote_ref": self.REFS["p0t"]},
            "candidate": {"commit": self.candidate, "root_tree": self.candidate_tree,
                          "public_remote_url": self.PUBLIC_REMOTE, "public_remote_ref": self.REFS["candidate"],
                          "component_config_path": self.CONFIG_PATH},
            "p1_transition": {"p1a_commit": self.p1a_commit, "p1a_path": V.P1A_PATH,
                              "p1t_commit": self.p1t_commit, "p1t_path": V.P1T_PATH,
                              "p1t_public_remote_ref": self.REFS["p1t"],
                              "p1r_commit": self.p1r_commit, "p1r_path": V.P1R_PATH,
                              "p1r_public_remote_ref": self.REFS["p1r"]},
            "p1r_publication_observer": self.publication_observer,
            "evidence_objects": self.evidence_paths, "verification_keys": self.key_paths,
        }
        self.request_raw = V.canonical_json(self.request)

    def fake_public_remote(self, remote: str, ref: str, commit: str) -> bytes:
        if remote != self.PUBLIC_REMOTE or self.remote_bindings.get(ref) != commit:
            raise V.CandidateBaseError("deterministic public remote mismatch")
        return self._fake_remote_bytes(ref, commit)

    def fake_fetch_actions(self, run_id: int) -> dict[str, object]:
        if run_id not in self.actions_runs:
            raise V.CandidateBaseError("deterministic Actions run mismatch")
        return copy.deepcopy(self.actions_runs[run_id])

    @staticmethod
    def isolated_runner(root: Path, command: list[str], env: dict[str, str], timeout: int) -> subprocess.CompletedProcess[bytes]:
        expected_prefix = ["/usr/local/bin/python3", "-I", "-S", "/inputs/verifier.py", "--candidate-readiness-verify"]
        assert command[:5] == expected_prefix, command[:5]
        assert env["PYTHONNOUSERSITE"] == "1" and timeout == 30
        verifier = (root / "inputs/verifier.py").read_bytes()
        artifact = (root / "inputs/artifact.json").read_bytes()
        result = {
            "status": "CANDIDATE_READINESS_EVIDENCE_VERIFIED",
            "artifact_sha256": V.sha256(artifact), "verifier_sha256": V.sha256(verifier),
        }
        return subprocess.CompletedProcess(command, 0, V.canonical_json(result), b"")


class CandidateBaseEndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.fixture = SignedTopologyFixture(Path(self.temp.name) / "repo")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def patches(self):
        return (
            mock.patch.object(V, "verify_public_remote", side_effect=self.fixture.fake_public_remote),
            mock.patch.object(V, "fetch_github_actions_run", side_effect=self.fixture.fake_fetch_actions),
        )

    def compile(self, request: dict[str, object] | None = None) -> dict[str, object]:
        request = request or self.fixture.request
        raw = V.canonical_json(request)
        remote, actions = self.patches()
        with remote, actions:
            return V.compile_diagnostic(
                self.fixture.root, request, raw, isolated_runner=self.fixture.isolated_runner
            )

    def test_full_signed_git_topology_compiles_rich_diagnostic_and_activation_receipt(self) -> None:
        diagnostic = self.compile()
        self.assertEqual(diagnostic["status"], "LOCAL_NONAUTHORITATIVE_REPLAY_VERIFIED")
        self.assertEqual(diagnostic["activation_boundary"], "PUBLIC_AUTHENTICATED_P1R")
        self.assertEqual(diagnostic["p1_transition"]["p1r_commit"], self.fixture.p1r_commit)
        self.assertEqual(len(diagnostic["verified_signers"]), 11)
        self.assertEqual(
            {row["signer_class"] for row in diagnostic["verified_signers"]},
            {"CONTROLLED_HARNESS_READINESS_KEY", "FROZEN_EXPERIMENTER_IDENTITY",
             "OPERATIONAL_EVIDENCE_ISSUER", "INDEPENDENT_RECOMPILER"},
        )
        input_path = Path(self.temp.name) / "activation-input.json"
        input_path.write_bytes(self.fixture.request_raw)
        input_path.chmod(0o444)
        remote, actions = self.patches()
        with remote, actions, mock.patch.object(
            V, "load_frozen_isolated_evidence_runner", return_value=self.fixture.isolated_runner
        ):
            receipt = V.verify_public_p1r_activation(
                self.fixture.root, input_path, V.sha256(self.fixture.request_raw), self.fixture.p1r_commit
            )
        self.assertEqual(receipt["p1r_commit"], self.fixture.p1r_commit)
        self.assertEqual(receipt["p1r"]["sha256"], V.sha256(self.fixture.p1r_raw))
        self.assertEqual(receipt["validation_diagnostic_sha256"], diagnostic["diagnostic_sha256"])
        self.assertEqual(receipt["validator"]["sha256"], V.sha256((HERE / V.VALIDATOR_PATH.split('/')[-1]).read_bytes()))
        self.assertEqual(receipt["receipt_sha256"], V.activation_receipt_digest(receipt))

    def test_canonical_p1r_ref_is_mandatory(self) -> None:
        request = copy.deepcopy(self.fixture.request)
        request["p1_transition"]["p1r_public_remote_ref"] = "refs/heads/not-canonical"
        with self.assertRaises(V.CandidateBaseError):
            self.compile(request)

    def test_authenticated_actions_receipt_content_drift_is_rejected(self) -> None:
        self.fixture.actions_runs[102]["head_sha"] = "f" * 40
        with self.assertRaisesRegex(V.CandidateBaseError, "publication observer"):
            self.compile()

    def test_schema_or_running_candidate_drift_is_rejected(self) -> None:
        write_json(self.fixture.root / V.INPUT_SCHEMA_PATH, {"type": "object", "additionalProperties": True})
        drift = self.fixture.commit("post-C schema drift")
        request = copy.deepcopy(self.fixture.request)
        request["candidate"]["commit"] = drift
        request["candidate"]["root_tree"] = self.fixture.tree(drift)
        request["candidate"]["public_remote_ref"] = "refs/tags/drift"
        self.fixture.remote_bindings["refs/tags/drift"] = drift
        with self.assertRaisesRegex(V.CandidateBaseError, "running validator bytes|P1A"):
            self.compile(request)

    def test_receipt_digest_binds_p1r_and_diagnostic_content(self) -> None:
        diagnostic = self.compile()
        receipt = {
            "schema": "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
            "p1r": {"path": V.P1R_PATH, "sha256": V.sha256(self.fixture.p1r_raw)},
            "p1r_commit": self.fixture.p1r_commit, "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
            "public_observation": self.fixture.publication_observer,
            "validation_inputs_sha256": V.sha256(self.fixture.request_raw),
            "validation_diagnostic_sha256": diagnostic["diagnostic_sha256"],
            "validator": {"path": V.VALIDATOR_PATH, "sha256": V.sha256((HERE / V.VALIDATOR_PATH.split('/')[-1]).read_bytes())},
        }
        receipt["receipt_sha256"] = V.activation_receipt_digest(receipt)
        changed = copy.deepcopy(receipt)
        changed["p1r"]["sha256"] = "9" * 64
        self.assertNotEqual(changed["receipt_sha256"], V.activation_receipt_digest(changed))
        changed = copy.deepcopy(receipt)
        changed["validation_diagnostic_sha256"] = "8" * 64
        self.assertNotEqual(changed["receipt_sha256"], V.activation_receipt_digest(changed))


if __name__ == "__main__":
    unittest.main()
