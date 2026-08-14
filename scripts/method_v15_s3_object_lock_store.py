#!/usr/bin/env python3
"""PRE-P1 S3 Object Lock immutable-store adapter contract.

This module does not provision AWS resources and is not wired into the delivery
broker.  It defines the fail-closed storage boundary the eventual broker must
use.  The caller injects an S3-compatible client, which keeps the contract
fully testable without credentials or network access.

All returned object references are private custody data.  Nothing in this
module publishes object keys, content hashes, or target bytes.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import unquote

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
CONFIG_SCHEMA = "c5k4-method-v1.5-s3-object-lock-store-config-1.0"
READINESS_SCHEMA = "c5k4-method-v1.5-s3-object-lock-store-readiness-1.0"
STATUS = "PRE_P1_STORE_ADAPTER_NOT_OPERATIONAL"


class ImmutableStoreError(RuntimeError):
    """A fail-closed immutable-store contract violation."""


class S3Client(Protocol):
    """The boto3 S3 calls used by the adapter, expressed structurally."""

    def get_bucket_versioning(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_bucket_location(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_bucket_encryption(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_bucket_policy(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_object_lock_configuration(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_public_access_block(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_bucket_policy_status(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def head_object(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def get_object(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def put_object(self, **kwargs: Any) -> Mapping[str, Any]: ...
    def list_object_versions(self, **kwargs: Any) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class PrivateObjectRef:
    """Private locator; callers must never place this in public artifacts."""

    bucket: str
    key: str
    version_id: str
    sha256: str
    byte_count: int
    retain_until_utc: str


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _schema(name: str) -> dict[str, Any]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def _validate(value: object, name: str) -> None:
    try:
        jsonschema.Draft7Validator(_schema(name), format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.ValidationError as exc:
        raise ImmutableStoreError(f"{name} validation failed: {exc.message}") from exc


def _utc(value: object, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError as exc:
            raise ImmutableStoreError(f"invalid {label}") from exc
    else:
        raise ImmutableStoreError(f"invalid {label}")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ImmutableStoreError(f"invalid {label}")
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _error_code(exc: BaseException) -> str | None:
    response = getattr(exc, "response", None)
    if not isinstance(response, Mapping):
        return None
    error = response.get("Error")
    if not isinstance(error, Mapping):
        return None
    code = error.get("Code")
    return str(code) if code is not None else None


def _add_years(value: datetime, years: int) -> datetime:
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        # February 29 to the last valid day of the target February.
        return value.replace(month=2, day=28, year=value.year + years)


class S3ObjectLockStore:
    """Content-addressed, version-pinned S3 Object Lock COMPLIANCE adapter."""

    def __init__(
        self,
        client: S3Client,
        config: dict[str, Any],
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        _validate(config, "benchmark-s3-object-lock-store-config-v1.5.schema.json")
        self.client = client
        self.config = json.loads(json.dumps(config))
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.horizon = _utc(config["benchmark_horizon_utc"], "benchmark horizon")
        self.retain_until = _utc(config["retention_through_utc"], "retention horizon")
        if self.retain_until <= self.horizon:
            raise ImmutableStoreError("retention must extend past benchmark horizon")

    @property
    def _bucket_args(self) -> dict[str, str]:
        return {
            "Bucket": self.config["bucket"],
            "ExpectedBucketOwner": self.config["expected_bucket_owner"],
        }

    def _key(self, object_sha256: str) -> str:
        return f"{self.config['key_prefix'].rstrip('/')}/objects/{object_sha256[:2]}/{object_sha256}"

    def _default_retention_end(self, now: datetime, row: Mapping[str, Any]) -> datetime:
        days = row.get("Days")
        years = row.get("Years")
        if isinstance(days, int) and not isinstance(days, bool) and days > 0 and years is None:
            return now + timedelta(days=days)
        if isinstance(years, int) and not isinstance(years, bool) and years > 0 and days is None:
            return _add_years(now, years)
        raise ImmutableStoreError("bucket default retention duration missing or ambiguous")

    def _policy(self, raw: object) -> dict[str, Any]:
        if not isinstance(raw, str):
            raise ImmutableStoreError("bucket policy response missing")
        policy: object | None = None
        for candidate in (raw, unquote(raw)):
            try:
                policy = json.loads(candidate)
                break
            except (ValueError, TypeError):
                continue
        if not isinstance(policy, dict):
            raise ImmutableStoreError("bucket policy is not valid JSON object")
        if sha256(canonical_json(policy)) != self.config["bucket_policy_sha256"]:
            raise ImmutableStoreError("bucket policy differs from frozen digest")
        return policy

    @staticmethod
    def _strings(value: object) -> set[str]:
        if isinstance(value, str):
            return {value}
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return set(value)
        return set()

    def _verify_delete_deny(self, policy: Mapping[str, Any]) -> None:
        statements = policy.get("Statement")
        if isinstance(statements, Mapping):
            statements = [statements]
        if not isinstance(statements, list):
            raise ImmutableStoreError("bucket policy lacks statements")
        required_actions = {"s3:DeleteObject", "s3:DeleteObjectVersion"}
        required_resource = f"arn:aws:s3:::{self.config['bucket']}/{self.config['key_prefix'].rstrip('/')}/*"
        for statement in statements:
            if not isinstance(statement, Mapping) or statement.get("Effect") != "Deny" or "Condition" in statement:
                continue
            principal = statement.get("Principal")
            if principal != "*" and principal != {"AWS": "*"}:
                continue
            actions = self._strings(statement.get("Action"))
            if "s3:*" not in actions and not required_actions.issubset(actions):
                continue
            resources = self._strings(statement.get("Resource"))
            if "*" in resources or required_resource in resources:
                return
        raise ImmutableStoreError("bucket policy does not unconditionally deny object deletion")

    def verify_environment(self) -> None:
        """Verify the bucket guardrails without writing a probe object."""

        now = _utc(self.clock(), "adapter clock")
        if self.retain_until <= now:
            raise ImmutableStoreError("configured retention horizon has expired")
        try:
            versioning = self.client.get_bucket_versioning(**self._bucket_args)
            location = self.client.get_bucket_location(**self._bucket_args)
            encryption = self.client.get_bucket_encryption(**self._bucket_args)
            lock = self.client.get_object_lock_configuration(**self._bucket_args)
            public = self.client.get_public_access_block(**self._bucket_args)
            policy = self.client.get_bucket_policy_status(**self._bucket_args)
            policy_document = self.client.get_bucket_policy(**self._bucket_args)
        except Exception as exc:
            raise ImmutableStoreError("S3 environment verification unavailable") from exc

        if versioning.get("Status") != "Enabled":
            raise ImmutableStoreError("bucket versioning is not enabled")
        observed_region = location.get("LocationConstraint")
        if observed_region is None:
            observed_region = "us-east-1"
        elif observed_region == "EU":
            observed_region = "eu-west-1"
        if observed_region != self.config["region"]:
            raise ImmutableStoreError("bucket region differs from configured region")
        rules = encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
        if not isinstance(rules, list) or len(rules) != 1 or not isinstance(rules[0], Mapping):
            raise ImmutableStoreError("bucket default encryption rule is not exact")
        default = rules[0].get("ApplyServerSideEncryptionByDefault")
        if (
            not isinstance(default, Mapping)
            or default.get("SSEAlgorithm") != "aws:kms"
            or default.get("KMSMasterKeyID") != self.config["kms_key_arn"]
            or rules[0].get("BucketKeyEnabled") is not True
        ):
            raise ImmutableStoreError("bucket default KMS encryption does not match frozen key")
        configuration = lock.get("ObjectLockConfiguration")
        if not isinstance(configuration, Mapping) or configuration.get("ObjectLockEnabled") != "Enabled":
            raise ImmutableStoreError("bucket Object Lock is not enabled")
        rule = configuration.get("Rule")
        retention = rule.get("DefaultRetention") if isinstance(rule, Mapping) else None
        if not isinstance(retention, Mapping):
            raise ImmutableStoreError("bucket default retention missing")
        if retention.get("Mode") != "COMPLIANCE":
            raise ImmutableStoreError("bucket default retention is not COMPLIANCE mode")
        if self._default_retention_end(now, retention) < self.retain_until:
            raise ImmutableStoreError("bucket default retention is shorter than required")

        block = public.get("PublicAccessBlockConfiguration")
        required_blocks = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        if not isinstance(block, Mapping) or any(block.get(field) is not True for field in required_blocks):
            raise ImmutableStoreError("bucket public access block is incomplete")
        status = policy.get("PolicyStatus")
        if not isinstance(status, Mapping) or status.get("IsPublic") is not False:
            raise ImmutableStoreError("bucket policy is public or unverifiable")
        self._verify_delete_deny(self._policy(policy_document.get("Policy")))

    def _versions(self, key: str) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
        try:
            response = self.client.list_object_versions(**self._bucket_args, Prefix=key, MaxKeys=3)
        except Exception as exc:
            raise ImmutableStoreError("S3 version inventory unavailable") from exc
        if response.get("IsTruncated") is True:
            raise ImmutableStoreError("content-addressed object has too many versions")
        versions = [row for row in response.get("Versions", []) if isinstance(row, Mapping) and row.get("Key") == key]
        markers = [row for row in response.get("DeleteMarkers", []) if isinstance(row, Mapping) and row.get("Key") == key]
        return versions, markers

    def _require_single_version(self, key: str, expected_version: str | None) -> str | None:
        versions, markers = self._versions(key)
        if markers:
            raise ImmutableStoreError("content-addressed object has a delete marker")
        if not versions:
            if expected_version is None:
                return None
            raise ImmutableStoreError("content-addressed object version is missing")
        if len(versions) != 1:
            raise ImmutableStoreError("content-addressed object has multiple versions")
        version = versions[0].get("VersionId")
        if not isinstance(version, str) or not version or version == "null":
            raise ImmutableStoreError("object version id missing")
        if versions[0].get("IsLatest") is not True:
            raise ImmutableStoreError("content-addressed object version is not latest")
        if expected_version is not None and version != expected_version:
            raise ImmutableStoreError("object version mismatch")
        return version

    def readiness(self, checked_at: datetime | None = None) -> dict[str, Any]:
        """Return a target-blind PRE-P1 diagnostic, never operational readiness."""

        checked = _utc(checked_at or self.clock(), "readiness timestamp")
        verified = True
        reasons = ["P1_NOT_FROZEN", "LIVE_ACCEPTANCE_NOT_RUN", "BROKER_INTEGRATION_NOT_FROZEN"]
        try:
            self.verify_environment()
        except ImmutableStoreError:
            verified = False
            reasons.append("BACKEND_ENVIRONMENT_UNVERIFIED")
        row = {
            "schema": READINESS_SCHEMA,
            "status": STATUS,
            "operational": False,
            "checked_at_utc": _utc_text(checked),
            "config_sha256": sha256(canonical_json(self.config)),
            "backend_environment_verified": verified,
            "target_bytes_publicly_exposed": False,
            "reasons": sorted(reasons),
        }
        _validate(row, "benchmark-s3-object-lock-store-readiness-v1.5.schema.json")
        return row

    def _head(self, key: str, *, version_id: str | None = None) -> Mapping[str, Any] | None:
        arguments: dict[str, Any] = {**self._bucket_args, "Key": key, "ChecksumMode": "ENABLED"}
        if version_id is not None:
            arguments["VersionId"] = version_id
        try:
            return self.client.head_object(**arguments)
        except Exception as exc:
            if version_id is None and _error_code(exc) in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise ImmutableStoreError("S3 HEAD verification unavailable") from exc

    def _verify_locked_version(
        self,
        key: str,
        object_sha256: str,
        byte_count: int,
        version_id: str | None = None,
    ) -> PrivateObjectRef:
        inventory_version = self._require_single_version(key, version_id)
        head = self._head(key, version_id=version_id)
        if head is None:
            raise ImmutableStoreError("content-addressed object missing")
        observed_version = head.get("VersionId")
        if not isinstance(observed_version, str) or not observed_version or observed_version == "null":
            raise ImmutableStoreError("object version id missing")
        if version_id is not None and observed_version != version_id:
            raise ImmutableStoreError("object version mismatch")
        if observed_version != inventory_version:
            raise ImmutableStoreError("HEAD and version inventory disagree")
        if head.get("DeleteMarker") is True:
            raise ImmutableStoreError("content-addressed object is a delete marker")
        if head.get("ContentLength") != byte_count:
            raise ImmutableStoreError("content-addressed object length mismatch")
        metadata = head.get("Metadata")
        if not isinstance(metadata, Mapping) or metadata.get("sha256") != object_sha256:
            raise ImmutableStoreError("content-addressed object metadata mismatch")
        if head.get("ObjectLockMode") != "COMPLIANCE":
            raise ImmutableStoreError("object is not retained in COMPLIANCE mode")
        retained = _utc(head.get("ObjectLockRetainUntilDate"), "object retention date")
        if retained < self.retain_until or retained <= self.horizon:
            raise ImmutableStoreError("object retention is shorter than required")
        if head.get("ServerSideEncryption") != "aws:kms" or head.get("SSEKMSKeyId") != self.config["kms_key_arn"]:
            raise ImmutableStoreError("object KMS encryption does not match frozen key")

        try:
            response = self.client.get_object(
                **self._bucket_args,
                Key=key,
                VersionId=observed_version,
                ChecksumMode="ENABLED",
            )
            body = response.get("Body")
            raw = body.read() if hasattr(body, "read") else body
        except Exception as exc:
            raise ImmutableStoreError("S3 GET verification unavailable") from exc
        if not isinstance(raw, bytes) or len(raw) != byte_count or sha256(raw) != object_sha256:
            raise ImmutableStoreError("content-addressed object bytes mismatch")
        checksum = response.get("ChecksumSHA256")
        expected_checksum = base64.b64encode(bytes.fromhex(object_sha256)).decode("ascii")
        if checksum is not None and checksum != expected_checksum:
            raise ImmutableStoreError("S3 response checksum mismatch")
        if response.get("VersionId") != observed_version:
            raise ImmutableStoreError("GET returned a different object version")
        return PrivateObjectRef(
            bucket=self.config["bucket"], key=key, version_id=observed_version,
            sha256=object_sha256, byte_count=byte_count,
            retain_until_utc=_utc_text(retained),
        )

    def put(self, raw: bytes) -> PrivateObjectRef:
        """Put bytes exactly once, then verify the retained version byte-for-byte."""

        if not isinstance(raw, bytes):
            raise ImmutableStoreError("immutable store accepts bytes only")
        self.verify_environment()
        object_sha256 = sha256(raw)
        key = self._key(object_sha256)
        inventory_version = self._require_single_version(key, None)
        existing = self._head(key)
        if (existing is None) != (inventory_version is None):
            raise ImmutableStoreError("HEAD and version inventory disagree")
        if existing is not None:
            return self._verify_locked_version(key, object_sha256, len(raw), inventory_version)

        checksum = base64.b64encode(bytes.fromhex(object_sha256)).decode("ascii")
        md5 = base64.b64encode(hashlib.md5(raw, usedforsecurity=False).digest()).decode("ascii")
        try:
            response = self.client.put_object(
                **self._bucket_args,
                Key=key,
                Body=raw,
                IfNoneMatch="*",
                ContentMD5=md5,
                ChecksumAlgorithm="SHA256",
                ChecksumSHA256=checksum,
                Metadata={"sha256": object_sha256},
                ObjectLockMode="COMPLIANCE",
                ObjectLockRetainUntilDate=self.retain_until,
                ServerSideEncryption="aws:kms",
                SSEKMSKeyId=self.config["kms_key_arn"],
                BucketKeyEnabled=True,
            )
        except Exception as exc:
            if _error_code(exc) in {"409", "412", "ConditionalRequestConflict", "PreconditionFailed"}:
                # A concurrent writer is acceptable only if the winning immutable
                # object verifies as precisely the same content.
                winner = self._head(key)
                if winner is None:
                    raise ImmutableStoreError("conditional write lost but winner is missing") from exc
                winner_version = self._require_single_version(key, None)
                return self._verify_locked_version(key, object_sha256, len(raw), winner_version)
            raise ImmutableStoreError("S3 immutable put unavailable") from exc
        version_id = response.get("VersionId")
        if not isinstance(version_id, str) or not version_id or version_id == "null":
            raise ImmutableStoreError("put did not return a version id")
        return self._verify_locked_version(key, object_sha256, len(raw), version_id)

    def get(self, reference: PrivateObjectRef) -> bytes:
        """Fetch a private reference only after revalidating its exact locked version."""

        self.verify_environment()
        if (
            len(reference.sha256) != 64
            or any(character not in "0123456789abcdef" for character in reference.sha256)
            or not reference.version_id
            or reference.byte_count < 0
        ):
            raise ImmutableStoreError("private object reference is malformed")
        expected_key = self._key(reference.sha256)
        if reference.bucket != self.config["bucket"] or reference.key != expected_key:
            raise ImmutableStoreError("private object reference is outside the configured store")
        verified = self._verify_locked_version(
            expected_key, reference.sha256, reference.byte_count, reference.version_id
        )
        try:
            response = self.client.get_object(
                **self._bucket_args,
                Key=verified.key,
                VersionId=verified.version_id,
                ChecksumMode="ENABLED",
            )
            body = response.get("Body")
            raw = body.read() if hasattr(body, "read") else body
        except Exception as exc:
            raise ImmutableStoreError("S3 GET unavailable") from exc
        if not isinstance(raw, bytes) or sha256(raw) != verified.sha256 or len(raw) != verified.byte_count:
            raise ImmutableStoreError("content-addressed object bytes mismatch")
        return raw
