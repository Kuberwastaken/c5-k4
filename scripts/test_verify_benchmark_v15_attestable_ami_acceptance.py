#!/usr/bin/env python3
"""Adversarial tests for the Method v1.5 attestable-AMI acceptance contract."""

from __future__ import annotations

import base64
import copy
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ami_acceptance", HERE / "verify_benchmark_v15_attestable_ami_acceptance.py")
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(V)


def public_raw(key: Ed25519PrivateKey) -> bytes:
    return key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


class AttestableAmiAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = V.strict_json(V.PLAN_PATH)
        cls.plan_schema = V.strict_json(V.PLAN_SCHEMA_PATH)
        cls.receipt_schema = V.strict_json(V.RECEIPT_SCHEMA_PATH)
        cls.builder = Ed25519PrivateKey.generate()
        cls.measurer = Ed25519PrivateKey.generate()
        cls.authority = Ed25519PrivateKey.generate()
        cls.cloudtrail = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.cloudtrail_public_der = cls.cloudtrail.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.PKCS1)
        cls.cloudtrail_fingerprint = "31e8b5433410dfb61a9dc45cc65b22ff"
        response = {"PublicKeyList": [{"Value": base64.b64encode(cls.cloudtrail_public_der).decode(), "ValidityStartTime": "2026-08-14T00:00:00+00:00", "ValidityEndTime": "2026-08-15T00:00:00+00:00", "Fingerprint": cls.cloudtrail_fingerprint}]}
        cls.cloudtrail_response_raw = V.canonical(response)

    def cloudtrail_evidence(self, prebuild: dict, receipt: dict) -> dict:
        account, region, bucket = receipt["build"]["ami"]["owner_account_id"], receipt["build"]["ami"]["region"], "c5k4-cloudtrail-fixture"
        event = {"eventID": "12345678-1234-1234-1234-123456789abc", "eventName": "RunInstances", "eventTime": "2026-08-14T09:45:00Z", "recipientAccountId": account, "awsRegion": region, "requestParameters": {"clientToken": "c5k4-prebuild-" + prebuild["authorization_sha256"], "imageId": "ami-builder0000000001"}}
        log_object = f"AWSLogs/{account}/CloudTrail/{region}/2026/08/14/{account}_CloudTrail_{region}_20260814T0945Z_fixture.json.gz"
        log_raw = V.canonical({"Records": [event]})
        previous_object = f"AWSLogs/{account}/CloudTrail-Digest/{region}/2026/08/14/{account}_CloudTrail-Digest_{region}_fixture_{region}_20260814T090100Z.json.gz"
        previous_digest = {"awsAccountId": account, "digestStartTime": "2026-08-14T08:01:00Z", "digestEndTime": "2026-08-14T09:01:00Z", "digestS3Bucket": bucket, "digestS3Object": previous_object, "digestPublicKeyFingerprint": self.cloudtrail_fingerprint, "digestSignatureAlgorithm": "SHA256withRSA", "newestEventTime": None, "oldestEventTime": None, "previousDigestS3Bucket": None, "previousDigestS3Object": None, "previousDigestHashValue": None, "previousDigestHashAlgorithm": None, "previousDigestSignature": None, "logFiles": []}
        previous_raw = V.canonical(previous_digest)
        previous_signing = f"{previous_digest['digestEndTime']}\n{bucket}/{previous_object}\n{V.sha256(previous_raw)}\n".encode()
        previous_signature = self.cloudtrail.sign(previous_signing, padding.PKCS1v15(), hashes.SHA256()).hex()
        current_object = f"AWSLogs/{account}/CloudTrail-Digest/{region}/2026/08/14/{account}_CloudTrail-Digest_{region}_fixture_{region}_20260814T100100Z.json.gz"
        current_digest = {"awsAccountId": account, "digestStartTime": "2026-08-14T09:01:00Z", "digestEndTime": "2026-08-14T10:01:00Z", "digestS3Bucket": bucket, "digestS3Object": current_object, "digestPublicKeyFingerprint": self.cloudtrail_fingerprint, "digestSignatureAlgorithm": "SHA256withRSA", "newestEventTime": event["eventTime"], "oldestEventTime": event["eventTime"], "previousDigestS3Bucket": bucket, "previousDigestS3Object": previous_object, "previousDigestHashValue": V.sha256(previous_raw), "previousDigestHashAlgorithm": "SHA-256", "previousDigestSignature": previous_signature, "logFiles": [{"s3Bucket": bucket, "s3Object": log_object, "hashValue": V.sha256(log_raw), "hashAlgorithm": "SHA-256", "newestEventTime": event["eventTime"], "oldestEventTime": event["eventTime"]}]}
        current_raw = V.canonical(current_digest)
        current_signing = f"{current_digest['digestEndTime']}\n{bucket}/{current_object}\n{V.sha256(current_raw)}\n{previous_signature}".encode()
        current_signature = self.cloudtrail.sign(current_signing, padding.PKCS1v15(), hashes.SHA256()).hex()
        return {"event_id": event["eventID"], "event_name": event["eventName"], "event_time_utc": event["eventTime"], "aws_account_id": account, "region": region, "prebuild_authorization_sha256": prebuild["authorization_sha256"], "request_parameters_sha256": V.sha256(V.canonical(event["requestParameters"])), "digest_chain": [{"s3_bucket": bucket, "s3_object": current_object, "uncompressed_base64": base64.b64encode(current_raw).decode(), "uncompressed_sha256": V.sha256(current_raw), "signature_hex": current_signature, "signature_algorithm": "SHA256withRSA", "signature_source": "S3_X_AMZ_META_SIGNATURE"}, {"s3_bucket": bucket, "s3_object": previous_object, "uncompressed_base64": base64.b64encode(previous_raw).decode(), "uncompressed_sha256": V.sha256(previous_raw), "signature_hex": previous_signature, "signature_algorithm": "SHA256withRSA", "signature_source": "SUCCESSOR_PREVIOUS_DIGEST_SIGNATURE"}], "log_file": {"s3_bucket": bucket, "s3_object": log_object, "uncompressed_base64": base64.b64encode(log_raw).decode(), "uncompressed_sha256": V.sha256(log_raw)}}

    def base_receipt(self) -> dict:
        daemon = copy.deepcopy(self.plan["build_contract"]["runtime"]["daemon_config"])
        return {
            "schema": "c5k4-method-v1.5-attestable-ami-acceptance-receipt-1.0",
            "status": "INDEPENDENTLY_MEASURED_AMI_ACCEPTED_FOR_CREATE_ONLY_TRANSITION",
            "protocol_version": "1.5", "target_specific": False, "plan_sha256": self.plan["plan_sha256"], "prebuild_authorization_sha256": "0" * 64, "postmeasurement_acceptance_sha256": "0" * 64,
            "build": {
                "binding": {"plan_sha256": self.plan["plan_sha256"], **V.POLICY_BINDING},
                "ami": {"ami_id": "ami-0123456789abcdef0", "owner_account_id": "123456789012", "region": "ap-south-1", "image_creation_date": "2026-08-14T10:00:00Z", "architecture": "x86_64", "boot_mode": "uefi", "tpm_support": "v2.0", "virtualization_type": "hvm", "hypervisor": "nitro", "root_device_type": "ebs", "public": False, "root_volume_encrypted": True},
                "source": {"family": "Amazon Linux 2023", "source_ami_id": "ami-0fedcba9876543210", "source_owner_account_id": "137112412989", "source_release": "2023.8.20250818", "source_region": "ap-south-1", "source_image_creation_date": "2025-08-18T00:00:00Z", "source_image_sha256": "1" * 64},
                "bootstrap": {"artifact_sha256": "2" * 64, "artifact_size_bytes": 65536, "installed_path": "/usr/local/sbin/c5k4-v15-controlled-host-bootstrap", "network_fetch_during_first_boot": False},
                "runtime": {"image_reference": self.plan["build_contract"]["runtime"]["image_reference"], "manifest_sha256": self.plan["build_contract"]["runtime"]["manifest_sha256"], "image_id": self.plan["build_contract"]["runtime"]["image_id"], "daemon_config": daemon, "daemon_config_sha256": V.sha256(V.canonical(daemon))},
                "built_at_utc": "2026-08-14T10:05:00Z", "signature": {}
            },
            "measurement": {"binding": {"plan_sha256": self.plan["plan_sha256"], **V.POLICY_BINDING}, "ami_id": "ami-0123456789abcdef0", "owner_account_id": "123456789012", "region": "ap-south-1", "fresh_boot": True, "tpm_event_log_sha256": "3" * 64, "hash_bank": "sha256", "pcrs": {str(i): format(i + 4, "064x") for i in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]}, "reference_bundle_format": "c5k4-method-v1.5-al2023-reference-measurements-1.0", "reference_bundle_sha256": "e" * 64, "remeasurement_reproduced": True, "measured_at_utc": "2026-08-14T11:00:00Z", "signature": {}},
            "transition": {"operation": "ACCEPT_NEWLY_CREATED_AMI", "existing_ami_mutated": False, "delete_or_deregister_permitted": False, "launch_or_activation_authorized": False},
            "accepted_at_utc": "2026-08-14T13:00:00Z", "receipt_sha256": "0" * 64
        }

    def sign(self, receipt: dict, builder=None, measurer=None) -> dict:
        builder, measurer = builder or self.builder, measurer or self.measurer
        for name, key, domain, signer in (("build", builder, V.BUILD_DOMAIN, "independent-builder"), ("measurement", measurer, V.MEASUREMENT_DOMAIN, "independent-measurer")):
            section = receipt[name]; unsigned = copy.deepcopy(section); unsigned.pop("signature")
            payload = domain + V.canonical(unsigned)
            section["signature"] = {"signer_id": signer, "key_sha256": V.sha256(public_raw(key)), "algorithm": "Ed25519", "signed_payload_sha256": V.sha256(payload), "signature_base64": base64.b64encode(key.sign(payload)).decode()}
        unsigned_receipt = copy.deepcopy(receipt); unsigned_receipt.pop("receipt_sha256")
        receipt["receipt_sha256"] = V.sha256(V.canonical(unsigned_receipt))
        return receipt

    def validate(self, receipt: dict, builder=None, measurer=None, prebuild=None, postmeasurement=None, a0=None, post_accepted_at="2026-08-14T12:00:00Z") -> None:
        builder, measurer = builder or self.builder, measurer or self.measurer
        a0 = a0 or self.a0_identity()
        prebuild = prebuild or self.prebuild(builder, measurer, a0=a0)
        if "cloudtrail_builder_start" not in receipt["build"]:
            receipt["build"]["cloudtrail_builder_start"] = self.cloudtrail_evidence(prebuild, receipt)
            self.sign(receipt, builder, measurer)
        postmeasurement = postmeasurement or self.postmeasurement(prebuild, receipt=receipt, accepted_at=post_accepted_at)
        receipt["prebuild_authorization_sha256"] = prebuild["authorization_sha256"]
        receipt["postmeasurement_acceptance_sha256"] = postmeasurement["acceptance_sha256"]
        unsigned = copy.deepcopy(receipt); unsigned.pop("receipt_sha256"); receipt["receipt_sha256"] = V.sha256(V.canonical(unsigned))
        with mock.patch.object(V, "_aws_list_public_keys", return_value=self.cloudtrail_response_raw):
            V.validate_receipt(receipt, self.receipt_schema, self.plan, self.plan_schema, public_raw(builder), public_raw(measurer), prebuild, postmeasurement, V.strict_json(V.AUTHORITY_SCHEMA_PATH), public_raw(self.authority), a0)

    def a0_identity(self, authorized_at="2026-08-14T09:00:00Z"):
        return {"schema": "c5k4-method-v1.5-validated-a0-identity-1.0", "commit": "a" * 40, "root_tree": "b" * 40, "artifact": {"path": "results/benchmark/v1.5-p0-a0/A0.json", "sha256": "c" * 64, "canonical_sha256": "d" * 64}, "authority_roster_sha256": "e" * 64, "ami_authority_binding_policy_template_sha256": "f" * 64, "external_harness_verification_key_sha256": V.sha256(public_raw(self.authority)), "nitrotpm_key_generation_attestation_sha256": "9" * 64, "nitrotpm_key_policy": "NITROTPM_PCR_SEALED_ON_CONTROLLED_HOST_ONLY", "a0_authorized_at_utc": "2026-08-14T08:50:00Z", "a0_publication_observed_at_utc": authorized_at, "a0_publication_run_id": 12345, "status": "EXTERNALLY_AUTHORIZED_A0", "activation_authority": True}

    def prebuild(self, builder=None, measurer=None, plan_sha256=None, a0=None, authorized_at="2026-08-14T09:30:00Z") -> dict:
        builder, measurer = builder or self.builder, measurer or self.measurer
        a0 = a0 or self.a0_identity()
        value = {"schema": "c5k4-method-v1.5-attestable-ami-prebuild-authorization-1.0", "status": "A0_AUTHORIZED_BEFORE_AMI_BUILD", "protocol_version": "1.5", "plan_sha256": plan_sha256 or self.plan["plan_sha256"], "policy_sha256": a0["ami_authority_binding_policy_template_sha256"], "a0_identity": a0, "builder": {"signer_id": "independent-builder", "key_sha256": V.sha256(public_raw(builder))}, "measurer": {"signer_id": "independent-measurer", "key_sha256": V.sha256(public_raw(measurer))}, "official_source_owner_account_id": "137112412989", "source_manifest_sha256": "1" * 64, "bootstrap_artifact_sha256": "2" * 64, "cloudtrail_region": "ap-south-1", "cloudtrail_key_lookup_start_time_utc": "2026-08-14T08:00:00Z", "cloudtrail_key_lookup_end_time_utc": "2026-08-14T11:00:00Z", "cloudtrail_lookup_role_arn": "arn:aws:iam::123456789012:role/c5k4-cloudtrail-readonly", "cloudtrail_key_policy": "AUTHENTICATED_LIVE_AWS_CLOUDTRAIL_LISTPUBLICKEYS_EXACT_BINARY_UNDER_PRECOMMITTED_READ_ONLY_OIDC_ROLE", "authorized_at_utc": authorized_at, "authorization_sha256": "0" * 64, "authentication": {}}
        self.sign_authority(value, "authorization_sha256", V.PREBUILD_DOMAIN)
        return value

    def postmeasurement(self, prebuild, receipt=None, accepted_at="2026-08-14T12:00:00Z"):
        receipt = receipt or self.sign(self.base_receipt())
        measurement, build = receipt["measurement"], receipt["build"]
        value = {"schema": "c5k4-method-v1.5-attestable-ami-postmeasurement-acceptance-1.0", "status": "A0_AUTHORITY_ACCEPTED_INDEPENDENT_MEASUREMENT", "protocol_version": "1.5", "plan_sha256": self.plan["plan_sha256"], "prebuild_authorization_sha256": prebuild["authorization_sha256"], "build_section_sha256": V.sha256(V.canonical(build)), "measurement_section_sha256": V.sha256(V.canonical(measurement)), "ami_id": measurement["ami_id"], "owner_account_id": measurement["owner_account_id"], "region": measurement["region"], "reference_bundle_sha256": measurement["reference_bundle_sha256"], "pcr_map_sha256": V.sha256(V.canonical(measurement["pcrs"])), "tpm_event_log_sha256": measurement["tpm_event_log_sha256"], "accepted_at_utc": accepted_at, "acceptance_sha256": "0" * 64, "authentication": {}}
        self.sign_authority(value, "acceptance_sha256", V.POSTMEASUREMENT_DOMAIN)
        return value

    def sign_authority(self, value, digest_field, domain):
        unsigned = copy.deepcopy(value); unsigned.pop("authentication"); unsigned.pop(digest_field); value[digest_field] = V.sha256(V.canonical(unsigned))
        signed = copy.deepcopy(value); signed.pop("authentication"); payload = domain + V.canonical(signed)
        value["authentication"] = {"authority_key_sha256": V.sha256(public_raw(self.authority)), "algorithm": "Ed25519", "signed_payload_sha256": V.sha256(payload), "signature_base64": base64.b64encode(self.authority.sign(payload)).decode()}

    def test_immutable_plan_and_schema_valid_post_a0_activation_pass(self) -> None:
        V.validate_plan(self.plan, self.plan_schema)
        self.validate(self.sign(self.base_receipt()))
        self.assertFalse(self.plan["authority_claimed"])
        self.assertFalse(self.plan["future_transition"]["launch_or_activation_permitted_by_plan"])

    def test_signed_sections_cannot_be_replayed_under_another_plan(self) -> None:
        receipt = self.sign(self.base_receipt())
        receipt["plan_sha256"] = "f" * 64
        unsigned = copy.deepcopy(receipt); unsigned.pop("receipt_sha256")
        receipt["receipt_sha256"] = V.sha256(V.canonical(unsigned))
        with self.assertRaisesRegex(V.AmiAcceptanceError, "bound"):
            self.validate(receipt)

    def test_provenance_owner_and_measurement_cross_binding_fail(self) -> None:
        mutations = {
            "wrong_family": lambda r: r["build"]["source"].update(family="Amazon Linux 2"),
            "owner_mismatch": lambda r: r["measurement"].update(owner_account_id="999999999999"),
            "ami_mismatch": lambda r: r["measurement"].update(ami_id="ami-11111111111111111"),
            "legacy_boot": lambda r: r["build"]["ami"].update(boot_mode="legacy-bios"),
            "no_tpm": lambda r: r["build"]["ami"].update(tpm_support="none"),
        }
        for name, mutate in mutations.items():
            receipt = self.base_receipt(); mutate(receipt); self.sign(receipt)
            with self.subTest(name=name), self.assertRaises(V.AmiAcceptanceError): self.validate(receipt)

    def test_bootstrap_runtime_pcr_and_reference_drift_fail(self) -> None:
        def daemon_change(receipt, key, value):
            daemon = receipt["build"]["runtime"]["daemon_config"]
            daemon[key] = value
            receipt["build"]["runtime"]["daemon_config_sha256"] = V.sha256(V.canonical(daemon))
        mutations = {
            "oversize_bootstrap": lambda r: r["build"]["bootstrap"].update(artifact_size_bytes=1048577),
            "uncommitted_bootstrap": lambda r: r["build"]["bootstrap"].update(artifact_sha256="9" * 64),
            "uncommitted_source_manifest": lambda r: r["build"]["source"].update(source_image_sha256="8" * 64),
            "unofficial_source_owner": lambda r: r["build"]["source"].update(source_owner_account_id="999999999999"),
            "mutable_runtime": lambda r: r["build"]["runtime"].update(image_reference="docker.io/library/python:latest"),
            "config_digest": lambda r: r["build"]["runtime"].update(daemon_config_sha256="0" * 64),
            "selinux_permissive": lambda r: daemon_change(r, "selinux", "permissive"),
            "security_options_incomplete": lambda r: daemon_change(r, "security_options", ["name=cgroupns"]),
            "missing_pcr": lambda r: r["measurement"]["pcrs"].pop("10"),
            "wrong_bundle": lambda r: r["measurement"].update(reference_bundle_format="unbound"),
        }
        for name, mutate in mutations.items():
            receipt = self.base_receipt(); mutate(receipt); self.sign(receipt)
            with self.subTest(name=name), self.assertRaises(V.AmiAcceptanceError): self.validate(receipt)

    def test_source_build_and_fresh_measurement_chronology_is_monotonic(self) -> None:
        mutations = {
            "source_after_destination": lambda r: r["build"]["source"].update(source_image_creation_date="2026-08-14T10:01:00Z"),
            "destination_after_build": lambda r: r["build"]["ami"].update(image_creation_date="2026-08-14T10:06:00Z"),
            "build_after_measurement": lambda r: r["build"].update(built_at_utc="2026-08-14T11:01:00Z"),
        }
        for name, mutate in mutations.items():
            receipt = self.base_receipt(); mutate(receipt); self.sign(receipt)
            with self.subTest(name=name), self.assertRaisesRegex(V.AmiAcceptanceError, "chronology"): self.validate(receipt)
        receipt = self.base_receipt(); receipt["accepted_at_utc"] = "2026-08-14T11:30:00Z"; self.sign(receipt)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "chronology"): self.validate(receipt)
        receipt = self.sign(self.base_receipt())
        with self.assertRaisesRegex(V.AmiAcceptanceError, "chronology"):
            pre = self.prebuild(authorized_at="2026-08-14T10:01:00Z"); self.validate(receipt, prebuild=pre)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "chronology"):
            pre = self.prebuild(); self.validate(receipt, prebuild=pre, post_accepted_at="2026-08-14T10:30:00Z")
        with self.assertRaisesRegex(V.AmiAcceptanceError, "chronology"):
            a0 = self.a0_identity("2026-08-14T09:31:00Z"); pre = self.prebuild(a0=a0, authorized_at="2026-08-14T09:30:00Z"); self.validate(receipt, a0=a0, prebuild=pre)

    def test_strict_a0_identity_cannot_be_replaced_by_self_asserted_coordinates(self) -> None:
        receipt = self.sign(self.base_receipt())
        forged = self.a0_identity(); forged["commit"] = "f" * 40
        pre = self.prebuild(a0=forged)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "strict validated A0"):
            self.validate(receipt, prebuild=pre, a0=self.a0_identity())

    def test_forged_lightweight_or_movable_a0_tag_is_not_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory); (repo / "forged.txt").write_text("forged")
            for command in (("init", "-q"), ("config", "user.email", "test@example.invalid"), ("config", "user.name", "test"), ("add", "."), ("commit", "-qm", "forged"), ("tag", "method-v1.5-a0")):
                subprocess.run(["git", "-C", str(repo), *command], check=True)
            commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            with self.assertRaises(V.AmiAcceptanceError):
                V.validated_a0_context(repo, commit, repo / "attacker-keys.json", {}, self.plan)

    def test_substituted_worktree_p0_validator_is_rejected_before_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"; repo.mkdir(); subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True); subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True)
            required = ["scripts/verify_benchmark_v15_p0_a0_publication.py", "schemas/benchmark-p0a-v1.5.schema.json", "schemas/benchmark-p0t-v1.5.schema.json", "schemas/benchmark-a0-v1.5.schema.json", "schemas/benchmark-p0-publication-receipt-v1.5.schema.json", "schemas/benchmark-attestable-ami-plan-v1.5.schema.json"]
            for relative in required:
                target = repo / relative; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes((V.ROOT / relative).read_bytes())
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            rows = []
            for relative in required:
                blob = subprocess.check_output(["git", "-C", str(repo), "rev-parse", f"HEAD:{relative}"]).decode().strip(); rows.append({"path": relative, "blob_oid": blob, "sha256": V.sha256((repo / relative).read_bytes())})
            p0a_path = repo / "results/benchmark/v1.5-p0-a0/P0A.json"; p0a_path.parent.mkdir(parents=True); p0a_path.write_text(json.dumps({"components": rows}) + "\n")
            subprocess.run(["git", "-C", str(repo), "add", str(p0a_path.relative_to(repo))], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "P0A"], check=True); p0a = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            p0t_path = repo / "results/benchmark/v1.5-p0-a0/P0T.json"; p0t_path.write_text(json.dumps({"p0a": {"commit": p0a}}) + "\n"); subprocess.run(["git", "-C", str(repo), "add", str(p0t_path.relative_to(repo))], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "P0T"], check=True); p0t = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            a0_path = repo / "results/benchmark/v1.5-p0-a0/A0.json"; a0_path.write_text(json.dumps({"p0t": {"commit": p0t}}) + "\n"); subprocess.run(["git", "-C", str(repo), "add", str(a0_path.relative_to(repo))], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "A0"], check=True); a0 = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            substituted = Path(directory) / "verify.py"; substituted.write_bytes((V.ROOT / required[0]).read_bytes() + b"\n# attacker substitution\n")
            with self.assertRaisesRegex(V.AmiAcceptanceError, "substituted"):
                V.bootstrap_p0_validator(repo, a0, verifier_path=substituted)

    def test_coherent_malicious_p0a_chain_cannot_replace_reviewed_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory); subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True); subprocess.run(["git", "-C", str(repo), "config", "user.name", "test"], check=True)
            required = [*V.PINNED_P0_COMPONENT_SHA256, "schemas/benchmark-attestable-ami-plan-v1.5.schema.json"]
            for relative in required:
                target = repo / relative; target.parent.mkdir(parents=True, exist_ok=True); raw = (V.ROOT / relative).read_bytes()
                if relative == "scripts/verify_benchmark_v15_p0_a0_publication.py": raw += b"\n# coherent attacker validator\n"
                target.write_bytes(raw)
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "malicious base"], check=True)
            rows = []
            for relative in required:
                blob = subprocess.check_output(["git", "-C", str(repo), "rev-parse", f"HEAD:{relative}"]).decode().strip(); rows.append({"path": relative, "blob_oid": blob, "sha256": V.sha256((repo / relative).read_bytes())})
            p0a_path = repo / "results/benchmark/v1.5-p0-a0/P0A.json"; p0a_path.parent.mkdir(parents=True); p0a_path.write_text(json.dumps({"components": rows}) + "\n")
            subprocess.run(["git", "-C", str(repo), "add", str(p0a_path.relative_to(repo))], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "P0A"], check=True); p0a = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            p0t_path = repo / "results/benchmark/v1.5-p0-a0/P0T.json"; p0t_path.write_text(json.dumps({"p0a": {"commit": p0a}}) + "\n"); subprocess.run(["git", "-C", str(repo), "add", str(p0t_path.relative_to(repo))], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "P0T"], check=True); p0t = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            a0_path = repo / "results/benchmark/v1.5-p0-a0/A0.json"; a0_path.write_text(json.dumps({"p0t": {"commit": p0t}}) + "\n"); subprocess.run(["git", "-C", str(repo), "add", str(a0_path.relative_to(repo))], check=True); subprocess.run(["git", "-C", str(repo), "commit", "-qm", "A0"], check=True); a0 = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip()
            with self.assertRaisesRegex(V.AmiAcceptanceError, "immutable reviewed hash"):
                V.bootstrap_p0_validator(repo, a0)

    def test_postmeasurement_digest_rejects_resigned_source_or_date_changes(self) -> None:
        receipt = self.base_receipt(); pre = self.prebuild()
        self.validate(receipt, prebuild=pre)
        accepted = self.postmeasurement(pre, receipt=receipt)
        for name, mutate in {
            "source": lambda r: r["build"]["source"].update(source_release="2023.9.20250901"),
            "destination_date": lambda r: r["build"]["ami"].update(image_creation_date="2026-08-14T09:55:00Z"),
            "measurement_date": lambda r: r["measurement"].update(measured_at_utc="2026-08-14T11:01:00Z"),
        }.items():
            changed = copy.deepcopy(receipt); mutate(changed); self.sign(changed)
            with self.subTest(name=name), self.assertRaisesRegex(V.AmiAcceptanceError, "binding differs"):
                self.validate(changed, prebuild=pre, postmeasurement=accepted)

    def test_fabricated_cloudtrail_event_time_account_region_or_request_fails(self) -> None:
        receipt = self.base_receipt(); pre = self.prebuild(); self.validate(receipt, prebuild=pre)
        start = receipt["build"]["cloudtrail_builder_start"]
        for field, value in (("event_time_utc", "2026-08-14T08:00:00Z"), ("aws_account_id", "999999999999"), ("region", "us-east-1")):
            forged = copy.deepcopy(start); forged[field] = value
            with self.subTest(field=field), self.assertRaises(V.AmiAcceptanceError):
                V._verify_cloudtrail_builder_start_with_response(forged, pre, self.cloudtrail_response_raw)
        forged = copy.deepcopy(start)
        log = json.loads(base64.b64decode(forged["log_file"]["uncompressed_base64"])); log["Records"][0]["requestParameters"]["clientToken"] = "retrospective-fabrication"
        log_raw = V.canonical(log); forged["log_file"]["uncompressed_base64"] = base64.b64encode(log_raw).decode(); forged["log_file"]["uncompressed_sha256"] = V.sha256(log_raw)
        current = json.loads(base64.b64decode(forged["digest_chain"][0]["uncompressed_base64"])); current["logFiles"][0]["hashValue"] = V.sha256(log_raw)
        current_raw = V.canonical(current); envelope = forged["digest_chain"][0]; envelope["uncompressed_base64"] = base64.b64encode(current_raw).decode(); envelope["uncompressed_sha256"] = V.sha256(current_raw)
        signing = f"{current['digestEndTime']}\n{envelope['s3_bucket']}/{envelope['s3_object']}\n{V.sha256(current_raw)}\n{current['previousDigestSignature']}".encode(); envelope["signature_hex"] = self.cloudtrail.sign(signing, padding.PKCS1v15(), hashes.SHA256()).hex()
        with self.assertRaisesRegex(V.AmiAcceptanceError, "request"):
            V._verify_cloudtrail_builder_start_with_response(forged, pre, self.cloudtrail_response_raw)

    def test_local_key_or_legacy_custom_payload_cannot_replace_aws_evidence(self) -> None:
        receipt = self.base_receipt(); pre = self.prebuild(); self.validate(receipt, prebuild=pre)
        start = receipt["build"]["cloudtrail_builder_start"]
        custom = copy.deepcopy(start); custom["digest_chain"] = {"previous_digest_sha256": "6" * 64, "signature_algorithm": "RSA-PKCS1v15-SHA256", "signature_base64": "attacker"}
        with self.assertRaisesRegex(V.AmiAcceptanceError, "actual AWS"):
            V._verify_cloudtrail_builder_start_with_response(custom, pre, self.cloudtrail_response_raw)
        rogue = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        rogue_der = rogue.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.PKCS1)
        response = {"PublicKeyList": [{"Value": base64.b64encode(rogue_der).decode(), "ValidityStartTime": "2026-08-14T00:00:00+00:00", "ValidityEndTime": "2026-08-15T00:00:00+00:00", "Fingerprint": self.cloudtrail_fingerprint}]}; raw = V.canonical(response)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "signature invalid"):
            V._verify_cloudtrail_builder_start_with_response(start, pre, raw)

    def test_production_list_public_keys_fails_closed_without_exact_oidc_role(self) -> None:
        self.assertNotIn("list_public_keys", inspect.signature(V.validate_receipt).parameters)
        self.assertEqual(list(inspect.signature(V.verify_cloudtrail_builder_start).parameters), ["start", "prebuild"])
        with mock.patch.dict(V.os.environ, {}, clear=True), self.assertRaisesRegex(V.AmiAcceptanceError, "exact PREBUILD OIDC role"):
            V._aws_list_public_keys("ap-south-1", "2026-08-14T08:00:00Z", "2026-08-14T11:00:00Z", "arn:aws:iam::123456789012:role/c5k4-cloudtrail-readonly")

    def test_real_aws_cli_iso_key_times_pass_and_old_numeric_shape_fails(self) -> None:
        receipt, pre = self.base_receipt(), self.prebuild()
        start = self.cloudtrail_evidence(pre, receipt)
        V._verify_cloudtrail_builder_start_with_response(start, pre, self.cloudtrail_response_raw)
        numeric = json.loads(self.cloudtrail_response_raw)
        numeric["PublicKeyList"][0]["ValidityStartTime"] = "1700000000.0"
        numeric["PublicKeyList"][0]["ValidityEndTime"] = "1900000000.0"
        with self.assertRaisesRegex(V.AmiAcceptanceError, "ISO-8601"):
            V._verify_cloudtrail_builder_start_with_response(start, pre, V.canonical(numeric))
        reversed_range = json.loads(self.cloudtrail_response_raw)
        reversed_range["PublicKeyList"][0]["ValidityStartTime"], reversed_range["PublicKeyList"][0]["ValidityEndTime"] = reversed_range["PublicKeyList"][0]["ValidityEndTime"], reversed_range["PublicKeyList"][0]["ValidityStartTime"]
        with self.assertRaisesRegex(V.AmiAcceptanceError, "empty or reversed"):
            V._verify_cloudtrail_builder_start_with_response(start, pre, V.canonical(reversed_range))

    def test_arbitrary_keys_and_non_a0_authority_cannot_authorize(self) -> None:
        rogue = Ed25519PrivateKey.generate()
        receipt = self.sign(self.base_receipt(), rogue, self.measurer)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "precommitted"):
            self.validate(receipt, rogue, self.measurer, prebuild=self.prebuild())

    def test_signature_independence_and_create_only_transition_fail_closed(self) -> None:
        receipt = self.base_receipt(); pre = self.prebuild(); self.validate(receipt, prebuild=pre); accepted = self.postmeasurement(pre, receipt=receipt)
        receipt["build"]["signature"]["signature_base64"] = base64.b64encode(b"x" * 64).decode()
        unsigned = copy.deepcopy(receipt); unsigned.pop("receipt_sha256")
        receipt["receipt_sha256"] = V.sha256(V.canonical(unsigned))
        with self.assertRaisesRegex(V.AmiAcceptanceError, "signature"): self.validate(receipt, prebuild=pre, postmeasurement=accepted)
        same = self.sign(self.base_receipt(), self.builder, self.builder)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "must differ"): self.validate(same, self.builder, self.builder)
        update = self.base_receipt(); update["transition"]["operation"] = "UPDATE"; self.sign(update)
        with self.assertRaises(V.AmiAcceptanceError): self.validate(update)

    def test_plan_digest_duplicate_keys_and_target_fields_fail(self) -> None:
        plan = copy.deepcopy(self.plan); plan["plan_sha256"] = "0" * 64
        with self.assertRaisesRegex(V.AmiAcceptanceError, "self-digest"): V.validate_plan(plan, self.plan_schema)
        with self.assertRaisesRegex(V.AmiAcceptanceError, "target-bearing"): V.scan_target_blind({"target_id": "forbidden"})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"; path.write_text('{"schema":"a","schema":"b"}')
            with self.assertRaisesRegex(V.AmiAcceptanceError, "duplicate"): V.strict_json(path)


if __name__ == "__main__":
    unittest.main()
