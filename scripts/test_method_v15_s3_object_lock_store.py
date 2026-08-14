#!/usr/bin/env python3
"""Adversarial tests for the PRE-P1 S3 Object Lock store adapter."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import unittest
from urllib.parse import quote

import method_v15_s3_object_lock_store as store


NOW = datetime(2026, 8, 13, 12, 0, 0, tzinfo=timezone.utc)
RETAIN = datetime(2028, 8, 16, 0, 0, 0, tzinfo=timezone.utc)


class FakeS3Error(RuntimeError):
    def __init__(self, code: str):
        super().__init__("fake S3 failure")
        self.response = {"Error": {"Code": code}}


class FakeS3:
    def __init__(self) -> None:
        self.versioning = "Enabled"
        self.region = "ap-south-1"
        self.kms_key_arn = "arn:aws:kms:ap-south-1:123456789012:key/12345678-1234-1234-1234-123456789abc"
        self.lock_enabled = "Enabled"
        self.default_mode = "COMPLIANCE"
        self.default_days: int | None = 1100
        self.default_years: int | None = None
        self.public_blocks = {
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        }
        self.is_public = False
        self.policy = policy()
        self.outage: str | None = None
        self.objects: dict[str, dict[str, object]] = {}
        self.delete_markers: dict[str, list[dict[str, object]]] = {}
        self.put_count = 0
        self.head_version_override: str | None = None
        self.get_version_override: str | None = None
        self.concurrent_winner: bytes | None = None

    def _fail(self, method: str) -> None:
        if self.outage in {"all", method}:
            raise FakeS3Error("ServiceUnavailable")

    def get_bucket_versioning(self, **_: object) -> dict[str, object]:
        self._fail("versioning")
        return {"Status": self.versioning}

    def get_bucket_location(self, **_: object) -> dict[str, object]:
        self._fail("location")
        return {"LocationConstraint": self.region}

    def get_bucket_encryption(self, **_: object) -> dict[str, object]:
        self._fail("encryption")
        return {
            "ServerSideEncryptionConfiguration": {
                "Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms", "KMSMasterKeyID": self.kms_key_arn,
                    },
                    "BucketKeyEnabled": True,
                }]
            }
        }

    def get_object_lock_configuration(self, **_: object) -> dict[str, object]:
        self._fail("lock")
        default: dict[str, object] = {"Mode": self.default_mode}
        if self.default_days is not None:
            default["Days"] = self.default_days
        if self.default_years is not None:
            default["Years"] = self.default_years
        return {
            "ObjectLockConfiguration": {
                "ObjectLockEnabled": self.lock_enabled,
                "Rule": {"DefaultRetention": default},
            }
        }

    def get_public_access_block(self, **_: object) -> dict[str, object]:
        self._fail("public")
        return {"PublicAccessBlockConfiguration": dict(self.public_blocks)}

    def get_bucket_policy_status(self, **_: object) -> dict[str, object]:
        self._fail("policy")
        return {"PolicyStatus": {"IsPublic": self.is_public}}

    def get_bucket_policy(self, **_: object) -> dict[str, object]:
        self._fail("policy-document")
        return {"Policy": quote(json.dumps(self.policy, separators=(",", ":")))}

    def list_object_versions(self, **kwargs: object) -> dict[str, object]:
        self._fail("versions")
        key = str(kwargs["Prefix"])
        versions: list[dict[str, object]] = []
        if key in self.objects:
            versions.append({"Key": key, "VersionId": self.objects[key]["VersionId"], "IsLatest": not self.delete_markers.get(key)})
        return {"IsTruncated": False, "Versions": versions, "DeleteMarkers": list(self.delete_markers.get(key, []))}

    def head_object(self, **kwargs: object) -> dict[str, object]:
        self._fail("head")
        key = str(kwargs["Key"])
        if key not in self.objects:
            raise FakeS3Error("NoSuchKey")
        row = self.objects[key]
        requested = kwargs.get("VersionId")
        if requested is not None and requested != row["VersionId"] and self.head_version_override is None:
            raise FakeS3Error("NoSuchVersion")
        return {
            "VersionId": self.head_version_override or row["VersionId"],
            "ContentLength": len(row["Body"]),
            "Metadata": dict(row["Metadata"]),
            "ObjectLockMode": row.get("ObjectLockMode"),
            "ObjectLockRetainUntilDate": row.get("ObjectLockRetainUntilDate"),
            "ServerSideEncryption": row.get("ServerSideEncryption"),
            "SSEKMSKeyId": row.get("SSEKMSKeyId"),
            "DeleteMarker": row.get("DeleteMarker", False),
        }

    def get_object(self, **kwargs: object) -> dict[str, object]:
        self._fail("get")
        key = str(kwargs["Key"])
        if key not in self.objects:
            raise FakeS3Error("NoSuchKey")
        row = self.objects[key]
        raw = bytes(row["Body"])
        return {
            "VersionId": self.get_version_override or row["VersionId"],
            "Body": io.BytesIO(raw),
            "ChecksumSHA256": base64.b64encode(hashlib.sha256(raw).digest()).decode("ascii"),
        }

    def put_object(self, **kwargs: object) -> dict[str, object]:
        self._fail("put")
        key = str(kwargs["Key"])
        if kwargs.get("IfNoneMatch") != "*":
            raise AssertionError("contract failed to request put-if-absent")
        if self.concurrent_winner is not None:
            winner = self.concurrent_winner
            self.concurrent_winner = None
            object_sha = hashlib.sha256(winner).hexdigest()
            self.put_count += 1
            self.objects[key] = {
                "VersionId": f"version-{self.put_count}", "Body": winner,
                "Metadata": {"sha256": object_sha}, "ObjectLockMode": "COMPLIANCE",
                "ObjectLockRetainUntilDate": RETAIN,
                "ServerSideEncryption": "aws:kms", "SSEKMSKeyId": self.kms_key_arn,
            }
            raise FakeS3Error("PreconditionFailed")
        if key in self.objects:
            raise FakeS3Error("PreconditionFailed")
        self.put_count += 1
        version = f"version-{self.put_count}"
        raw = bytes(kwargs["Body"])
        self.objects[key] = {
            "VersionId": version,
            "Body": raw,
            "Metadata": dict(kwargs["Metadata"]),
            "ObjectLockMode": kwargs["ObjectLockMode"],
            "ObjectLockRetainUntilDate": kwargs["ObjectLockRetainUntilDate"],
            "ServerSideEncryption": kwargs["ServerSideEncryption"],
            "SSEKMSKeyId": kwargs["SSEKMSKeyId"],
        }
        return {"VersionId": version}


def policy() -> dict[str, object]:
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "DenyPrivateCustodyDeletion",
            "Effect": "Deny",
            "Principal": "*",
            "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion"],
            "Resource": "arn:aws:s3:::c5k4-private-custody/private/c5k4/v1.5/*",
        }],
    }


def config() -> dict[str, object]:
    frozen_policy = policy()
    return {
        "schema": store.CONFIG_SCHEMA,
        "status": store.STATUS,
        "backend": "AWS_S3_OBJECT_LOCK",
        "bucket": "c5k4-private-custody",
        "expected_bucket_owner": "123456789012",
        "region": "ap-south-1",
        "key_prefix": "private/c5k4/v1.5",
        "kms_key_arn": "arn:aws:kms:ap-south-1:123456789012:key/12345678-1234-1234-1234-123456789abc",
        "bucket_policy_sha256": store.sha256(store.canonical_json(frozen_policy)),
        "benchmark_horizon_utc": "2027-08-15T00:00:00Z",
        "retention_through_utc": "2028-08-16T00:00:00Z",
        "required_object_lock_mode": "COMPLIANCE",
        "put_if_absent": True,
        "private_only": True,
    }


class S3ObjectLockStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeS3()
        self.adapter = store.S3ObjectLockStore(self.client, config(), clock=lambda: NOW)

    def test_put_if_absent_and_version_pinned_round_trip(self) -> None:
        reference = self.adapter.put(b"private target bytes")
        self.assertEqual(self.adapter.get(reference), b"private target bytes")
        again = self.adapter.put(b"private target bytes")
        self.assertEqual(again, reference)
        self.assertEqual(self.client.put_count, 1)
        record = self.client.objects[reference.key]
        self.assertEqual(record["ObjectLockMode"], "COMPLIANCE")
        self.assertGreaterEqual(record["ObjectLockRetainUntilDate"], RETAIN)

    def test_existing_key_cannot_be_overwritten_or_accepted_with_wrong_bytes(self) -> None:
        raw = b"expected target bytes"
        object_sha = store.sha256(raw)
        key = self.adapter._key(object_sha)
        self.client.objects[key] = {
            "VersionId": "attacker-version",
            "Body": b"different bytes same alleged address",
            "Metadata": {"sha256": object_sha},
            "ObjectLockMode": "COMPLIANCE",
            "ObjectLockRetainUntilDate": RETAIN,
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": self.client.kms_key_arn,
        }
        with self.assertRaisesRegex(store.ImmutableStoreError, "length mismatch|bytes mismatch"):
            self.adapter.put(raw)
        self.assertEqual(self.client.put_count, 0)

    def test_missing_object_retention_fails_closed(self) -> None:
        reference = self.adapter.put(b"retained")
        self.client.objects[reference.key].pop("ObjectLockRetainUntilDate")
        with self.assertRaisesRegex(store.ImmutableStoreError, "retention date"):
            self.adapter.get(reference)

    def test_missing_bucket_default_retention_fails_closed(self) -> None:
        self.client.default_days = None
        with self.assertRaisesRegex(store.ImmutableStoreError, "duration missing or ambiguous"):
            self.adapter.verify_environment()

    def test_governance_bucket_or_object_mode_is_rejected(self) -> None:
        self.client.default_mode = "GOVERNANCE"
        with self.assertRaisesRegex(store.ImmutableStoreError, "not COMPLIANCE"):
            self.adapter.verify_environment()
        self.client.default_mode = "COMPLIANCE"
        reference = self.adapter.put(b"locked")
        self.client.objects[reference.key]["ObjectLockMode"] = "GOVERNANCE"
        with self.assertRaisesRegex(store.ImmutableStoreError, "not retained in COMPLIANCE"):
            self.adapter.get(reference)

    def test_short_bucket_or_object_retention_is_rejected(self) -> None:
        self.client.default_days = 100
        with self.assertRaisesRegex(store.ImmutableStoreError, "shorter than required"):
            self.adapter.verify_environment()
        self.client.default_days = 1100
        reference = self.adapter.put(b"long lived")
        self.client.objects[reference.key]["ObjectLockRetainUntilDate"] = datetime(
            2027, 8, 14, tzinfo=timezone.utc
        )
        with self.assertRaisesRegex(store.ImmutableStoreError, "shorter than required"):
            self.adapter.get(reference)

    def test_version_mismatch_after_put_is_rejected(self) -> None:
        self.client.head_version_override = "different-version"
        with self.assertRaisesRegex(store.ImmutableStoreError, "version mismatch"):
            self.adapter.put(b"version-pinned")

    def test_get_returning_different_version_is_rejected(self) -> None:
        reference = self.adapter.put(b"version-pinned")
        self.client.get_version_override = "different-version"
        with self.assertRaisesRegex(store.ImmutableStoreError, "different object version"):
            self.adapter.get(reference)

    def test_concurrent_412_winner_is_accepted_only_when_exact(self) -> None:
        self.client.concurrent_winner = b"same bytes"
        reference = self.adapter.put(b"same bytes")
        self.assertEqual(self.adapter.get(reference), b"same bytes")
        fresh = FakeS3()
        fresh.concurrent_winner = b"attacker bytes"
        adapter = store.S3ObjectLockStore(fresh, config(), clock=lambda: NOW)
        with self.assertRaisesRegex(store.ImmutableStoreError, "length mismatch|metadata mismatch|bytes mismatch"):
            adapter.put(b"expected bytes")

    def test_delete_marker_and_multiple_version_history_fail_closed(self) -> None:
        reference = self.adapter.put(b"no deletion")
        self.client.delete_markers[reference.key] = [{
            "Key": reference.key, "VersionId": "delete-1", "IsLatest": True,
        }]
        with self.assertRaisesRegex(store.ImmutableStoreError, "delete marker"):
            self.adapter.put(b"no deletion")
        self.client.delete_markers.clear()
        original_versions = self.client.list_object_versions
        self.client.list_object_versions = lambda **kwargs: {
            **original_versions(**kwargs),
            "Versions": [
                {"Key": reference.key, "VersionId": reference.version_id, "IsLatest": True},
                {"Key": reference.key, "VersionId": "extra", "IsLatest": False},
            ],
        }
        with self.assertRaisesRegex(store.ImmutableStoreError, "multiple versions"):
            self.adapter.get(reference)

    def test_kms_mismatch_and_policy_drift_fail_closed(self) -> None:
        self.client.kms_key_arn = "arn:aws:kms:ap-south-1:123456789012:key/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
        with self.assertRaisesRegex(store.ImmutableStoreError, "KMS encryption"):
            self.adapter.verify_environment()
        self.client = FakeS3()
        self.adapter = store.S3ObjectLockStore(self.client, config(), clock=lambda: NOW)
        self.client.policy["Statement"][0]["Action"] = ["s3:DeleteObject"]
        with self.assertRaisesRegex(store.ImmutableStoreError, "frozen digest"):
            self.adapter.verify_environment()

    def test_object_kms_metadata_mismatch_fails_closed(self) -> None:
        reference = self.adapter.put(b"encrypted")
        self.client.objects[reference.key]["SSEKMSKeyId"] = "wrong-key"
        with self.assertRaisesRegex(store.ImmutableStoreError, "object KMS encryption"):
            self.adapter.get(reference)

    def test_environment_or_object_outage_fails_closed_without_raw_bytes(self) -> None:
        secret = b"NEVER PRINT THIS TARGET"
        self.client.outage = "versioning"
        with self.assertRaises(store.ImmutableStoreError) as caught:
            self.adapter.put(secret)
        self.assertNotIn(secret.decode(), str(caught.exception))
        self.client.outage = None
        reference = self.adapter.put(secret)
        self.client.outage = "get"
        with self.assertRaises(store.ImmutableStoreError) as caught:
            self.adapter.get(reference)
        self.assertNotIn(secret.decode(), str(caught.exception))

    def test_tampered_body_and_checksum_fail_closed(self) -> None:
        reference = self.adapter.put(b"authentic")
        row = self.client.objects[reference.key]
        row["Body"] = b"tampered!"
        row["Metadata"] = {"sha256": reference.sha256}
        with self.assertRaisesRegex(store.ImmutableStoreError, "bytes mismatch"):
            self.adapter.get(reference)

    def test_disabled_versioning_object_lock_and_public_bucket_are_rejected(self) -> None:
        mutations = (
            ("versioning", lambda: setattr(self.client, "versioning", "Suspended")),
            ("region", lambda: setattr(self.client, "region", "us-east-1")),
            ("Object Lock", lambda: setattr(self.client, "lock_enabled", "Disabled")),
            ("public access", lambda: self.client.public_blocks.update(BlockPublicPolicy=False)),
            ("policy is public", lambda: setattr(self.client, "is_public", True)),
        )
        for expected, mutate in mutations:
            with self.subTest(expected=expected):
                self.client = FakeS3()
                self.adapter = store.S3ObjectLockStore(self.client, config(), clock=lambda: NOW)
                mutate()
                with self.assertRaisesRegex(store.ImmutableStoreError, expected):
                    self.adapter.verify_environment()

    def test_readiness_is_strict_target_blind_and_never_operational(self) -> None:
        target = b"SECRET CONJECTURE CONTENT"
        self.adapter.put(target)
        row = self.adapter.readiness(NOW)
        encoded = store.canonical_json(row)
        self.assertNotIn(target, encoded)
        self.assertFalse(row["operational"])
        self.assertTrue(row["backend_environment_verified"])
        self.assertFalse(row["target_bytes_publicly_exposed"])
        self.client.outage = "policy"
        unavailable = self.adapter.readiness(NOW)
        self.assertFalse(unavailable["backend_environment_verified"])
        self.assertIn("BACKEND_ENVIRONMENT_UNVERIFIED", unavailable["reasons"])

    def test_config_cannot_claim_operational_or_weaken_guards(self) -> None:
        mutations = (
            lambda row: row.update(status="OPERATIONAL"),
            lambda row: row.update(required_object_lock_mode="GOVERNANCE"),
            lambda row: row.update(put_if_absent=False),
            lambda row: row.update(private_only=False),
            lambda row: row.update(retention_through_utc="2027-08-14T00:00:00Z"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                row = config()
                mutate(row)
                with self.assertRaises(store.ImmutableStoreError):
                    store.S3ObjectLockStore(FakeS3(), row, clock=lambda: NOW)


if __name__ == "__main__":
    unittest.main()
