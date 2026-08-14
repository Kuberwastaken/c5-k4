#!/usr/bin/env python3
"""Strict offline verifier for the Method v1.5 attestable-AMI contract."""

from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "infra/benchmark-v1.5/attestable-ami/plan.json"
PLAN_SCHEMA_PATH = ROOT / "schemas/benchmark-attestable-ami-plan-v1.5.schema.json"
RECEIPT_SCHEMA_PATH = ROOT / "schemas/benchmark-attestable-ami-receipt-v1.5.schema.json"
AUTHORITY_SCHEMA_PATH = ROOT / "schemas/benchmark-attestable-ami-authority-binding-v1.5.schema.json"
PLAN_DOMAIN = b"c5k4-method-v1.5-attestable-ami-plan-1.0\0"
BUILD_DOMAIN = b"c5k4-method-v1.5-attestable-ami-build-1.0\0"
MEASUREMENT_DOMAIN = b"c5k4-method-v1.5-attestable-ami-measurement-1.0\0"
PREBUILD_DOMAIN = b"c5k4-method-v1.5-attestable-ami-prebuild-authorization-1.0\0"
POSTMEASUREMENT_DOMAIN = b"c5k4-method-v1.5-attestable-ami-postmeasurement-acceptance-1.0\0"
POLICY_BINDING = {"receipt_schema": "c5k4-method-v1.5-attestable-ami-acceptance-receipt-1.0", "policy_version": "c5k4-method-v1.5-attestable-ami-acceptance-policy-1.0"}
FORBIDDEN_KEYS = {"target", "target_id", "cluster", "cluster_id", "conjecture", "conjecture_id", "statement_text", "candidate_identity", "outcome", "ranking"}
PINNED_P0_COMPONENT_SHA256 = {
    "scripts/verify_benchmark_v15_p0_a0_publication.py": "b1ba019b6f8aea6b4f6445c437396ea9a52998749dd9eb049766a9b0bde04599",
    "schemas/benchmark-p0a-v1.5.schema.json": "15289315646dfbc14d40b34517825e0fe18b71d214e21adc1bb72d029433a7bc",
    "schemas/benchmark-p0t-v1.5.schema.json": "464a7ac205a8c86399a25c597a1518419d2be78465a8e98f016f3df5ee9f7485",
    "schemas/benchmark-a0-v1.5.schema.json": "b847eadad6d1b49449fd8e39b02c2464353636fa7997c2d038677c0d0567841f",
    "schemas/benchmark-p0-publication-receipt-v1.5.schema.json": "d5ea2c0f91ea1ab4714ca73a1d7ecb1c736394a6eac97d728d9adbf820162a7a",
}


class AmiAcceptanceError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise AmiAcceptanceError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result
    try:
        value = json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AmiAcceptanceError(f"invalid strict JSON in {path}") from exc
    if not isinstance(value, dict):
        raise AmiAcceptanceError(f"top level is not an object in {path}")
    return value


def strict_bytes(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in items:
            if key in out: raise AmiAcceptanceError(f"duplicate JSON key in {label}: {key}")
            out[key] = value
        return out
    try: value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc: raise AmiAcceptanceError(f"invalid JSON in {label}") from exc
    if not isinstance(value, dict): raise AmiAcceptanceError(f"{label} is not an object")
    return value


def schema_validate(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value), key=lambda e: list(e.path))
    if errors:
        raise AmiAcceptanceError(f"{label} schema violation: {errors[0].message}")


def scan_target_blind(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.casefold().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise AmiAcceptanceError(f"target-bearing field forbidden at {path}.{key}")
            scan_target_blind(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_target_blind(child, f"{path}[{index}]")


def validate_plan(plan: dict[str, Any], schema: dict[str, Any]) -> None:
    schema_validate(plan, schema, "plan")
    unsigned = copy.deepcopy(plan)
    recorded = unsigned.pop("plan_sha256")
    if recorded != sha256(PLAN_DOMAIN + canonical(unsigned)):
        raise AmiAcceptanceError("plan self-digest mismatch")
    acceptance = plan["acceptance_contract"]
    if acceptance["authority_binding_schema_sha256"] != sha256(AUTHORITY_SCHEMA_PATH.read_bytes()):
        raise AmiAcceptanceError("authority-binding policy schema digest mismatch")
    pinned_files = (("receipt_schema_sha256", RECEIPT_SCHEMA_PATH), ("verifier_sha256", Path(__file__)))
    if any(acceptance[field] != sha256(path.read_bytes()) for field, path in pinned_files):
        raise AmiAcceptanceError("receipt/verifier policy closure digest mismatch")
    if acceptance["policy_sha256"] != sha256(canonical(POLICY_BINDING)):
        raise AmiAcceptanceError("receipt signature policy digest mismatch")
    if acceptance["authority_freeze_chronology"] != "P0A_A0_FREEZES_POLICY_AND_HARNESS_KEY_THEN_PREBUILD_AUTHORIZATION_THEN_POSTMEASUREMENT_ACCEPTANCE":
        raise AmiAcceptanceError("authority freeze chronology does not separate pre-build authorization from post-measurement acceptance")
    scan_target_blind({key: value for key, value in plan.items() if key != "prohibited_data"})
    build = plan["build_contract"]
    if build["source_provenance_required"] != ["source_ami_id", "source_owner_account_id", "source_release", "source_region", "source_image_creation_date", "source_image_sha256"]:
        raise AmiAcceptanceError("AL2023 provenance closure differs")
    if build["destination_identity_required"] != ["ami_id", "owner_account_id", "region", "image_creation_date"]:
        raise AmiAcceptanceError("destination AMI identity closure differs")
    if (build["boot_mode"], build["tpm_support"], build["hypervisor"]) != ("uefi", "v2.0", "nitro"):
        raise AmiAcceptanceError("UEFI/NitroTPM contract differs")
    transition = plan["future_transition"]
    if transition != {"current": "PLAN_ONLY", "next": "BUILD_CREATE_NEW_AMI_THEN_INDEPENDENT_ACCEPTANCE", "create_only": True, "update_existing_ami_permitted": False, "delete_or_deregister_permitted": False, "launch_or_activation_permitted_by_plan": False}:
        raise AmiAcceptanceError("future transition is not plan-only and create-only")


def _public_key(raw: bytes, label: str) -> Ed25519PublicKey:
    if len(raw) != 32:
        raise AmiAcceptanceError(f"{label} Ed25519 public key must be exactly 32 raw bytes")
    return Ed25519PublicKey.from_public_bytes(raw)


def _verify_section(section: dict[str, Any], domain: bytes, key_raw: bytes, label: str) -> None:
    signature = section["signature"]
    if signature["key_sha256"] != sha256(key_raw):
        raise AmiAcceptanceError(f"{label} key commitment mismatch")
    unsigned = copy.deepcopy(section)
    unsigned.pop("signature")
    payload = domain + canonical(unsigned)
    if signature["signed_payload_sha256"] != sha256(payload):
        raise AmiAcceptanceError(f"{label} signed payload digest mismatch")
    try:
        signature_raw = base64.b64decode(signature["signature_base64"], validate=True)
        if len(signature_raw) != 64:
            raise ValueError("wrong signature length")
        _public_key(key_raw, label).verify(signature_raw, payload)
    except (InvalidSignature, ValueError) as exc:
        raise AmiAcceptanceError(f"{label} Ed25519 signature invalid") from exc


def _git(repo: Path, *args: str) -> bytes:
    environment = {
        "HOME": "/nonexistent/c5k4-ami-verifier",
        "PATH": "/usr/bin:/bin",
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_LITERAL_PATHSPECS": "1",
    }
    command = [
        "/usr/bin/git", "--no-pager", "--no-replace-objects",
        "-c", "core.hooksPath=/dev/null",
        "-c", "core.fsmonitor=false",
        "-c", "credential.helper=",
        "-c", "protocol.file.allow=never",
        "-c", "protocol.ext.allow=never",
        "-C", str(repo), *args,
    ]
    try: return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment).stdout
    except subprocess.CalledProcessError as exc: raise AmiAcceptanceError("sanitized P0/A0 Git-object traversal failed") from exc


def _one_path_parent(repo: Path, commit: str, path: str) -> str:
    if re.fullmatch(r"[0-9a-f]{40}", commit) is None: raise AmiAcceptanceError("P0/A0 commit is not an exact object ID")
    if _git(repo, "cat-file", "-t", commit) != b"commit\n": raise AmiAcceptanceError("P0/A0 identity is not a commit")
    parents = _git(repo, "show", "-s", "--format=%P", commit).decode().split()
    changed = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "--no-renames", "--no-ext-diff", "-r", commit).decode().splitlines()
    if len(parents) != 1 or changed != [path]: raise AmiAcceptanceError("P0/A0 sole-parent one-path topology differs")
    return parents[0]


def _commit_raw(repo: Path, commit: str, path: str) -> bytes:
    return _git(repo, "show", f"{commit}:{path}")


def bootstrap_p0_validator(repo: Path, a0_commit: str, *, verifier_path: Path | None = None):
    a0_path, p0t_path, p0a_path = "results/benchmark/v1.5-p0-a0/A0.json", "results/benchmark/v1.5-p0-a0/P0T.json", "results/benchmark/v1.5-p0-a0/P0A.json"
    p0t_commit = _one_path_parent(repo, a0_commit, a0_path); a0 = strict_bytes(_commit_raw(repo, a0_commit, a0_path), "A0")
    if a0.get("p0t", {}).get("commit") != p0t_commit: raise AmiAcceptanceError("A0 does not bind its exact P0T parent")
    p0a_commit = _one_path_parent(repo, p0t_commit, p0t_path); p0t = strict_bytes(_commit_raw(repo, p0t_commit, p0t_path), "P0T")
    if p0t.get("p0a", {}).get("commit") != p0a_commit: raise AmiAcceptanceError("P0T does not bind its exact P0A parent")
    _one_path_parent(repo, p0a_commit, p0a_path); p0a = strict_bytes(_commit_raw(repo, p0a_commit, p0a_path), "P0A")
    rows = p0a.get("components"); index = {row.get("path"): row for row in rows if isinstance(row, dict)} if isinstance(rows, list) else {}
    required = [*PINNED_P0_COMPONENT_SHA256, "schemas/benchmark-attestable-ami-plan-v1.5.schema.json"]
    for path in required:
        row = index.get(path); raw = _commit_raw(repo, p0a_commit, path)
        blob_oid = _git(repo, "rev-parse", f"{p0a_commit}:{path}").decode().strip()
        pinned = PINNED_P0_COMPONENT_SHA256.get(path)
        if pinned is not None and (sha256(raw) != pinned or sha256((ROOT / path).read_bytes()) != pinned):
            raise AmiAcceptanceError(f"P0 component differs from immutable reviewed hash: {path}")
        if not isinstance(row, dict) or row.get("blob_oid") != blob_oid or row.get("sha256") != sha256(raw) or (ROOT / path).read_bytes() != raw:
            raise AmiAcceptanceError(f"local/P0A component binding differs: {path}")
    expected_path = (ROOT / required[0]).resolve(); module_path = (verifier_path or expected_path).resolve()
    if module_path != expected_path or module_path.read_bytes() != _commit_raw(repo, p0a_commit, required[0]): raise AmiAcceptanceError("substituted local P0/A0 validator module rejected")
    spec = importlib.util.spec_from_file_location("p0_a0", module_path)
    if not spec or not spec.loader:
        raise AmiAcceptanceError("strict P0/A0 validator cannot be loaded")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def validated_a0_context(repo: Path, commit: str, authority_keys: Path, publication_receipt: dict[str, Any], plan: dict[str, Any], *, verifier_path: Path | None = None) -> dict[str, Any]:
    module = bootstrap_p0_validator(repo, commit, verifier_path=verifier_path)
    try: identity = module.validated_a0_identity(repo, commit, authority_keys=authority_keys, publication_receipt=publication_receipt)
    except Exception as exc: raise AmiAcceptanceError("strict P0/A0 authority validation failed") from exc
    required = {"schema", "commit", "root_tree", "artifact", "authority_roster_sha256", "ami_authority_binding_policy_template_sha256", "external_harness_verification_key_sha256", "nitrotpm_key_generation_attestation_sha256", "nitrotpm_key_policy", "a0_authorized_at_utc", "a0_publication_observed_at_utc", "a0_publication_run_id", "status", "activation_authority"}
    if set(identity) != required: raise AmiAcceptanceError("validated A0 identity projection has a different closed shape")
    return identity


def _verify_authority_artifact(value: dict[str, Any], digest_field: str, domain: bytes, authority_key: bytes, expected_key_sha256: str) -> None:
    auth = value["authentication"]
    if sha256(authority_key) != expected_key_sha256 or auth["authority_key_sha256"] != expected_key_sha256:
        raise AmiAcceptanceError("AMI authority key differs from strict validated A0 identity")
    digest_input = copy.deepcopy(value); digest_input.pop("authentication"); recorded = digest_input.pop(digest_field)
    if recorded != sha256(canonical(digest_input)):
        raise AmiAcceptanceError(f"{digest_field} self-digest mismatch")
    signed = copy.deepcopy(value); signed.pop("authentication"); payload = domain + canonical(signed)
    if auth["signed_payload_sha256"] != sha256(payload):
        raise AmiAcceptanceError("AMI authority signed payload digest mismatch")
    try:
        _public_key(authority_key, "A0 AMI authority").verify(base64.b64decode(auth["signature_base64"], validate=True), payload)
    except (InvalidSignature, ValueError) as exc:
        raise AmiAcceptanceError("AMI authority signature invalid") from exc


def validate_prebuild(value: dict[str, Any], schema: dict[str, Any], plan: dict[str, Any], a0_identity: dict[str, Any], authority_key: bytes) -> None:
    schema_validate(value, schema, "pre-build authorization")
    if value["a0_identity"] != a0_identity:
        raise AmiAcceptanceError("pre-build authorization does not contain the strict validated A0 identity")
    if value["plan_sha256"] != plan["plan_sha256"] or value["policy_sha256"] != a0_identity["ami_authority_binding_policy_template_sha256"]:
        raise AmiAcceptanceError("pre-build authorization differs from immutable plan/A0 policy")
    if _utc(value["cloudtrail_key_lookup_start_time_utc"], "key lookup start") >= _utc(value["cloudtrail_key_lookup_end_time_utc"], "key lookup end"):
        raise AmiAcceptanceError("CloudTrail key lookup range is empty or reversed")
    _verify_authority_artifact(value, "authorization_sha256", PREBUILD_DOMAIN, authority_key, a0_identity["external_harness_verification_key_sha256"])


def validate_postmeasurement(value: dict[str, Any], schema: dict[str, Any], plan: dict[str, Any], prebuild: dict[str, Any], measurement: dict[str, Any], authority_key: bytes, a0_identity: dict[str, Any]) -> None:
    schema_validate(value, schema, "post-measurement acceptance")
    if value["plan_sha256"] != plan["plan_sha256"] or value["prebuild_authorization_sha256"] != prebuild["authorization_sha256"]:
        raise AmiAcceptanceError("post-measurement acceptance is not bound to plan/pre-build authorization")
    expected = {"build_section_sha256": sha256(canonical(measurement["_bound_build_section"])), "measurement_section_sha256": sha256(canonical({key: item for key, item in measurement.items() if key != "_bound_build_section"})), "ami_id": measurement["ami_id"], "owner_account_id": measurement["owner_account_id"], "region": measurement["region"], "reference_bundle_sha256": measurement["reference_bundle_sha256"], "pcr_map_sha256": sha256(canonical(measurement["pcrs"])), "tpm_event_log_sha256": measurement["tpm_event_log_sha256"]}
    if any(value[key] != item for key, item in expected.items()):
        raise AmiAcceptanceError("post-measurement AMI/PCR/reference/event-log binding differs")
    _verify_authority_artifact(value, "acceptance_sha256", POSTMEASUREMENT_DOMAIN, authority_key, a0_identity["external_harness_verification_key_sha256"])


def _utc(value: Any, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None: raise ValueError("timezone absent")
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError) as exc:
        raise AmiAcceptanceError(f"invalid CloudTrail {label} timestamp") from exc


def _key_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise AmiAcceptanceError("ListPublicKeys validity time is not AWS CLI ISO-8601 text")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0): raise ValueError("not UTC")
        return parsed.astimezone(timezone.utc)
    except ValueError as exc: raise AmiAcceptanceError("invalid UTC ListPublicKeys ISO-8601 validity time") from exc


def _strict_b64(value: Any, label: str) -> bytes:
    try: return base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as exc: raise AmiAcceptanceError(f"{label} is not canonical base64") from exc


def _aws_list_public_keys(region: str, start_time: str, end_time: str, expected_role_arn: str) -> bytes:
    if os.environ.get("AWS_ROLE_ARN") != expected_role_arn or not os.environ.get("AWS_WEB_IDENTITY_TOKEN_FILE"):
        raise AmiAcceptanceError("authenticated live CloudTrail ListPublicKeys requires the exact PREBUILD OIDC role")
    environment = {"HOME": "/nonexistent/c5k4-ami-verifier", "PATH": "/usr/bin:/bin", "LC_ALL": "C", "AWS_PAGER": "", "AWS_CLI_AUTO_PROMPT": "off", "AWS_CONFIG_FILE": "/dev/null", "AWS_SHARED_CREDENTIALS_FILE": "/dev/null", "AWS_EC2_METADATA_DISABLED": "true"}
    for name in ("AWS_ROLE_ARN", "AWS_WEB_IDENTITY_TOKEN_FILE", "AWS_ROLE_SESSION_NAME"):
        if name in os.environ: environment[name] = os.environ[name]
    command = ["/usr/bin/aws", "cloudtrail", "list-public-keys", "--region", region, "--start-time", start_time, "--end-time", end_time, "--output", "json", "--no-cli-pager"]
    try: return subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, timeout=60).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc: raise AmiAcceptanceError("authenticated live CloudTrail ListPublicKeys lookup failed closed") from exc


def _verify_cloudtrail_builder_start_with_response(start: dict[str, Any], prebuild: dict[str, Any], response_raw: bytes) -> None:
    if not isinstance(start.get("digest_chain"), list) or len(start["digest_chain"]) < 2:
        raise AmiAcceptanceError("CloudTrail evidence is not an actual AWS digest-file chain")
    if start["region"] != prebuild["cloudtrail_region"]: raise AmiAcceptanceError("CloudTrail digest/ListPublicKeys region mismatch")
    response = strict_bytes(response_raw, "CloudTrail ListPublicKeys response")
    if set(response) != {"PublicKeyList"} or not isinstance(response["PublicKeyList"], list):
        raise AmiAcceptanceError("ListPublicKeys response has unexpected shape")
    request_start, request_end = _utc(prebuild["cloudtrail_key_lookup_start_time_utc"], "ListPublicKeys start"), _utc(prebuild["cloudtrail_key_lookup_end_time_utc"], "ListPublicKeys end")
    chain = start["digest_chain"]
    parsed_chain: list[tuple[dict[str, Any], bytes, dict[str, Any]]] = []
    for index, envelope in enumerate(chain):
        raw = _strict_b64(envelope["uncompressed_base64"], "CloudTrail digest file")
        if sha256(raw) != envelope["uncompressed_sha256"]: raise AmiAcceptanceError("CloudTrail digest-file content hash mismatch")
        digest = strict_bytes(raw, "CloudTrail digest file")
        if digest.get("digestS3Bucket") != envelope["s3_bucket"] or digest.get("digestS3Object") != envelope["s3_object"]:
            raise AmiAcceptanceError("CloudTrail digest file was not retrieved from its recorded S3 location")
        if digest.get("digestSignatureAlgorithm") != "SHA256withRSA" or envelope["signature_algorithm"] != "SHA256withRSA":
            raise AmiAcceptanceError("CloudTrail digest signature algorithm differs from AWS format")
        expected_source = "S3_X_AMZ_META_SIGNATURE" if index == 0 else "SUCCESSOR_PREVIOUS_DIGEST_SIGNATURE"
        if envelope["signature_source"] != expected_source: raise AmiAcceptanceError("CloudTrail digest signature source is not authentic")
        parsed_chain.append((envelope, raw, digest))
    for index, (envelope, raw, digest) in enumerate(parsed_chain):
        digest_end = _utc(digest.get("digestEndTime"), "digest end")
        if not request_start <= digest_end <= request_end: raise AmiAcceptanceError("digest time is outside frozen ListPublicKeys request range")
        if digest.get("awsAccountId") != start["aws_account_id"]: raise AmiAcceptanceError("CloudTrail digest account mismatch")
        if f"/CloudTrail-Digest/{start['region']}/" not in envelope["s3_object"]: raise AmiAcceptanceError("CloudTrail digest path region mismatch")
        fingerprint = digest.get("digestPublicKeyFingerprint")
        matches = []
        for item in response["PublicKeyList"]:
            if not isinstance(item, dict) or set(item) != {"Value", "ValidityStartTime", "ValidityEndTime", "Fingerprint"}: continue
            validity_start, validity_end = _key_time(item["ValidityStartTime"]), _key_time(item["ValidityEndTime"])
            if validity_start >= validity_end: raise AmiAcceptanceError("ListPublicKeys validity range is empty or reversed")
            if item.get("Fingerprint") == fingerprint and validity_start <= digest_end <= validity_end: matches.append(item)
        if len(matches) != 1: raise AmiAcceptanceError("no unique region/time-valid ListPublicKeys fingerprint matches digest")
        try:
            public_der = base64.b64decode(matches[0]["Value"], validate=True)
            key = serialization.load_der_public_key(public_der)
            if not isinstance(key, rsa.RSAPublicKey): raise ValueError("not RSA")
            previous_signature = digest.get("previousDigestSignature")
            signing_string = f"{digest['digestEndTime']}\n{envelope['s3_bucket']}/{envelope['s3_object']}\n{sha256(raw)}\n{previous_signature or ''}".encode()
            key.verify(bytes.fromhex(envelope["signature_hex"]), signing_string, padding.PKCS1v15(), hashes.SHA256())
        except (ValueError, TypeError, InvalidSignature) as exc:
            raise AmiAcceptanceError("AWS CloudTrail digest-file SHA256withRSA signature invalid") from exc
        if index + 1 < len(parsed_chain):
            prior_envelope, prior_raw, _ = parsed_chain[index + 1]
            if (digest.get("previousDigestS3Bucket"), digest.get("previousDigestS3Object"), digest.get("previousDigestHashAlgorithm"), digest.get("previousDigestHashValue"), digest.get("previousDigestSignature")) != (prior_envelope["s3_bucket"], prior_envelope["s3_object"], "SHA-256", sha256(prior_raw), prior_envelope["signature_hex"]):
                raise AmiAcceptanceError("CloudTrail previous-digest hash/signature/location chain invalid")
        elif any(digest.get(field) is not None for field in ("previousDigestS3Bucket", "previousDigestS3Object", "previousDigestHashValue", "previousDigestHashAlgorithm", "previousDigestSignature")):
            raise AmiAcceptanceError("CloudTrail supplied digest chain does not terminate at a starting digest")
    current_digest = parsed_chain[0][2]
    log_envelope = start["log_file"]
    log_raw = _strict_b64(log_envelope["uncompressed_base64"], "CloudTrail log file")
    if sha256(log_raw) != log_envelope["uncompressed_sha256"]: raise AmiAcceptanceError("CloudTrail uncompressed log-file hash mismatch")
    log_rows = current_digest.get("logFiles")
    referenced = [row for row in log_rows if isinstance(row, dict) and row.get("s3Bucket") == log_envelope["s3_bucket"] and row.get("s3Object") == log_envelope["s3_object"]] if isinstance(log_rows, list) else []
    if len(referenced) != 1 or referenced[0].get("hashAlgorithm") != "SHA-256" or referenced[0].get("hashValue") != sha256(log_raw):
        raise AmiAcceptanceError("CloudTrail digest does not authenticate exact uncompressed log file")
    if f"/CloudTrail/{start['region']}/" not in log_envelope["s3_object"]: raise AmiAcceptanceError("CloudTrail log path region mismatch")
    log = strict_bytes(log_raw, "CloudTrail log file")
    records = log.get("Records")
    events = [row for row in records if isinstance(row, dict) and row.get("eventID") == start["event_id"]] if isinstance(records, list) else []
    if len(events) != 1: raise AmiAcceptanceError("exact RunInstances event is absent or duplicated in authenticated log")
    event = events[0]; request = event.get("requestParameters")
    if not isinstance(request, dict) or request.get("clientToken") != "c5k4-prebuild-" + prebuild["authorization_sha256"]:
        raise AmiAcceptanceError("CloudTrail RunInstances request does not bind exact pre-build authorization")
    projection = {"event_id": event.get("eventID"), "event_name": event.get("eventName"), "event_time_utc": event.get("eventTime"), "aws_account_id": event.get("recipientAccountId"), "region": event.get("awsRegion"), "prebuild_authorization_sha256": prebuild["authorization_sha256"], "request_parameters_sha256": sha256(canonical(request))}
    if any(start[key] != value for key, value in projection.items()): raise AmiAcceptanceError("parsed CloudTrail event projection/request digest differs")
    event_time = _utc(event.get("eventTime"), "event")
    if not _utc(referenced[0].get("oldestEventTime"), "log oldest event") <= event_time <= _utc(referenced[0].get("newestEventTime"), "log newest event"):
        raise AmiAcceptanceError("RunInstances event time lies outside authenticated log range")


def verify_cloudtrail_builder_start(start: dict[str, Any], prebuild: dict[str, Any]) -> None:
    response = _aws_list_public_keys(prebuild["cloudtrail_region"], prebuild["cloudtrail_key_lookup_start_time_utc"], prebuild["cloudtrail_key_lookup_end_time_utc"], prebuild["cloudtrail_lookup_role_arn"])
    _verify_cloudtrail_builder_start_with_response(start, prebuild, response)


def validate_receipt(receipt: dict[str, Any], schema: dict[str, Any], plan: dict[str, Any], plan_schema: dict[str, Any], builder_key: bytes, measurer_key: bytes, prebuild: dict[str, Any], postmeasurement: dict[str, Any], authority_schema: dict[str, Any], authority_key: bytes, a0_identity: dict[str, Any]) -> None:
    validate_plan(plan, plan_schema)
    schema_validate(receipt, schema, "receipt")
    scan_target_blind(receipt)
    validate_prebuild(prebuild, authority_schema, plan, a0_identity, authority_key)
    if receipt["plan_sha256"] != plan["plan_sha256"]:
        raise AmiAcceptanceError("receipt is not bound to the accepted plan")
    if receipt["prebuild_authorization_sha256"] != prebuild["authorization_sha256"] or receipt["postmeasurement_acceptance_sha256"] != postmeasurement["acceptance_sha256"]:
        raise AmiAcceptanceError("final receipt does not bind the exact pre-build and post-measurement authority artifacts")
    unsigned_receipt = copy.deepcopy(receipt); recorded = unsigned_receipt.pop("receipt_sha256")
    if recorded != sha256(canonical(unsigned_receipt)):
        raise AmiAcceptanceError("receipt self-digest mismatch")
    if builder_key == measurer_key:
        raise AmiAcceptanceError("builder and independent measurer keys must differ")
    build, measurement = receipt["build"], receipt["measurement"]
    if build["signature"]["signer_id"] == measurement["signature"]["signer_id"]:
        raise AmiAcceptanceError("builder and independent measurer identities must differ")
    expected_binding = {"plan_sha256": plan["plan_sha256"], **POLICY_BINDING}
    if build["binding"] != expected_binding or measurement["binding"] != expected_binding:
        raise AmiAcceptanceError("signed section plan/schema/policy binding mismatch")
    if prebuild["builder"] != {"signer_id": build["signature"]["signer_id"], "key_sha256": sha256(builder_key)}:
        raise AmiAcceptanceError("builder key is not the exact authority-precommitted key")
    if prebuild["measurer"] != {"signer_id": measurement["signature"]["signer_id"], "key_sha256": sha256(measurer_key)}:
        raise AmiAcceptanceError("measurer key is not the exact authority-precommitted key")
    _verify_section(build, BUILD_DOMAIN, builder_key, "builder")
    _verify_section(measurement, MEASUREMENT_DOMAIN, measurer_key, "measurer")
    measurement_for_acceptance = copy.deepcopy(measurement); measurement_for_acceptance["_bound_build_section"] = build
    contract = plan["build_contract"]
    ami = build["ami"]
    for key in ("architecture", "boot_mode", "tpm_support", "virtualization_type", "hypervisor", "root_device_type", "public", "root_volume_encrypted"):
        if ami[key] != contract[key]:
            raise AmiAcceptanceError(f"AMI property differs from frozen plan: {key}")
    if build["source"]["family"] != contract["image_family"]:
        raise AmiAcceptanceError("source is not Amazon Linux 2023")
    if build["bootstrap"]["artifact_size_bytes"] > contract["bootstrap"]["maximum_bytes"] or build["bootstrap"]["installed_path"] != contract["bootstrap"]["installed_path"]:
        raise AmiAcceptanceError("bootstrap artifact is not bounded by the frozen plan")
    if build["bootstrap"]["artifact_sha256"] != prebuild["bootstrap_artifact_sha256"]:
        raise AmiAcceptanceError("bootstrap artifact digest is not the authority-precommitted digest")
    if build["source"]["source_owner_account_id"] != contract["official_source_owner_account_id"]:
        raise AmiAcceptanceError("AL2023 source owner is not the frozen official account")
    if build["source"]["source_image_sha256"] != prebuild["source_manifest_sha256"]:
        raise AmiAcceptanceError("AL2023 source manifest is not the authority-precommitted digest")
    if not prebuild["cloudtrail_lookup_role_arn"].startswith(f"arn:aws:iam::{ami['owner_account_id']}:role/"):
        raise AmiAcceptanceError("CloudTrail lookup OIDC role is not in the destination AMI account")
    runtime = build["runtime"]
    if any(runtime[key] != contract["runtime"][key] for key in ("image_reference", "manifest_sha256", "image_id", "daemon_config")):
        raise AmiAcceptanceError("runtime manifest/config differs from frozen plan")
    if runtime["daemon_config_sha256"] != sha256(canonical(runtime["daemon_config"])):
        raise AmiAcceptanceError("runtime daemon config digest mismatch")
    for key in ("ami_id", "owner_account_id", "region"):
        if measurement[key] != ami[key]:
            raise AmiAcceptanceError(f"measurement/build AMI cross-binding mismatch: {key}")
    expected_pcrs = [str(item) for item in plan["measurement_contract"]["required_pcrs"]]
    if list(measurement["pcrs"].keys()) != expected_pcrs:
        raise AmiAcceptanceError("PCR closure or ordering differs from frozen plan")
    if measurement["reference_bundle_format"] != plan["measurement_contract"]["reference_bundle_format"]:
        raise AmiAcceptanceError("reference-measurement bundle format differs")
    validate_postmeasurement(postmeasurement, authority_schema, plan, prebuild, measurement_for_acceptance, authority_key, a0_identity)
    if receipt["transition"] != {"operation": "ACCEPT_NEWLY_CREATED_AMI", "existing_ami_mutated": False, "delete_or_deregister_permitted": False, "launch_or_activation_authorized": False}:
        raise AmiAcceptanceError("receipt transition is not non-launch acceptance of a newly created AMI")
    try:
        source_time = datetime.fromisoformat(build["source"]["source_image_creation_date"].replace("Z", "+00:00"))
        start = build["cloudtrail_builder_start"]
        chronology = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in (a0_identity["a0_publication_observed_at_utc"], prebuild["authorized_at_utc"], start["event_time_utc"], ami["image_creation_date"], build["built_at_utc"], measurement["measured_at_utc"], postmeasurement["accepted_at_utc"], receipt["accepted_at_utc"])]
    except ValueError as exc:
        raise AmiAcceptanceError("AMI chronology contains an invalid timestamp") from exc
    if source_time > chronology[3] or chronology != sorted(chronology):
        raise AmiAcceptanceError("chronology must be source <= destination and A0 <= prebuild authorization <= destination/build <= measurement <= postmeasurement acceptance <= final receipt")
    event_unsigned = {key: item for key, item in start.items() if key != "event_sha256"}
    verify_cloudtrail_builder_start(start, prebuild)
    if start["aws_account_id"] != ami["owner_account_id"] or start["region"] != ami["region"]:
        raise AmiAcceptanceError("immutable CloudTrail builder-start evidence does not bind pre-build authorization and destination")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--builder-public-key", type=Path)
    parser.add_argument("--measurer-public-key", type=Path)
    parser.add_argument("--prebuild-authorization", type=Path)
    parser.add_argument("--postmeasurement-acceptance", type=Path)
    parser.add_argument("--authority-public-key", type=Path)
    parser.add_argument("--a0-commit")
    parser.add_argument("--a0-authority-keys", type=Path)
    parser.add_argument("--a0-publication-receipt", type=Path)
    args = parser.parse_args()
    plan, plan_schema = strict_json(PLAN_PATH), strict_json(PLAN_SCHEMA_PATH)
    validate_plan(plan, plan_schema)
    supplied = [args.receipt, args.builder_public_key, args.measurer_public_key, args.prebuild_authorization, args.postmeasurement_acceptance, args.authority_public_key, args.a0_commit, args.a0_authority_keys, args.a0_publication_receipt]
    if any(supplied) and not all(supplied):
        raise AmiAcceptanceError("receipt verification requires strict P0/A0 inputs, pre-build authorization, post-measurement acceptance, and all three public keys")
    if args.receipt:
        a0_identity = validated_a0_context(ROOT, args.a0_commit, args.a0_authority_keys, strict_json(args.a0_publication_receipt), plan)
        validate_receipt(strict_json(args.receipt), strict_json(RECEIPT_SCHEMA_PATH), plan, plan_schema, args.builder_public_key.read_bytes(), args.measurer_public_key.read_bytes(), strict_json(args.prebuild_authorization), strict_json(args.postmeasurement_acceptance), strict_json(AUTHORITY_SCHEMA_PATH), args.authority_public_key.read_bytes(), a0_identity)
        print("attestable AMI receipt independently authenticated and accepted")
    else:
        print("attestable AMI plan verified; no AMI build, acceptance, launch, or authority claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
