#!/usr/bin/env python3
"""Authenticated bootstrap for the Method v1.5 production campaign.

This file never imports repository execution code and never owns campaign
state.  It verifies four role-pinned authorities and the immutable exact-C
closure first, then passes the sealed activation bytes to one root-owned P1
helper.  The helper is solely responsible for Git ancestry, descriptor-pinned
inputs, the durable WORM claim/journal, all 288 isolated trees, and signed
per-tree evidence.  The bootstrap releases only the helper's signed receipt.
"""

from __future__ import annotations

import argparse
import base64
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Any, Callable, Mapping, Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import jsonschema


ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
ROLES = ("c1", "freeze", "private_targets", "harness")
SIGNER_IDS = {
    "c1": "C1_SELECTION_AUTHORITY",
    "freeze": "RUN_FREEZE_AUTHORITY",
    "private_targets": "PRIVATE_TARGET_CUSTODIAN",
    "harness": "CONTROLLED_HARNESS_AUTHORITY",
}
AUTHORITY_KEY_PATHS = {
    "c1": Path("/etc/c5k4-benchmark-v15/credentials/c1-authority.pub"),
    "freeze": Path("/etc/c5k4-benchmark-v15/credentials/freeze-authority.pub"),
    "private_targets": Path("/etc/c5k4-benchmark-v15/credentials/private-target-custodian.pub"),
    "harness": Path("/etc/c5k4-benchmark-v15/credentials/harness-acceptance.pub"),
}
EXECUTOR_PATH = Path("/opt/c5k4-benchmark-v15/p1/bin/c5k4-triplet-tree-executor")
MAX_ACTIVATION_BYTES = 4 * 1024 * 1024
MAX_RECEIPT_BYTES = 8 * 1024 * 1024
CAMPAIGN_WALL_CAP_SECONDS = 18_600
DOMAINS = {role: f"c5k4/method-v1.5/production/{role}-receipt/v1".encode() for role in ROLES}
RECEIPT_DOMAIN = b"c5k4/method-v1.5/production/campaign-receipt/v1"
TREE_RECEIPT_DOMAIN = b"c5k4/method-v1.5/production/tree-completion/v1"
JOURNAL_ENTRY_DOMAIN = b"c5k4/method-v1.5/production/worm-journal-entry/v1"
ZERO_SHA256 = "0" * 64
EXPECTED_CLOSURE_PATHS = {
    "launcher": "/opt/c5k4-benchmark-v15/p1/bin/run-benchmark-v15-production-campaign",
    "runtime": "/opt/c5k4-benchmark-v15/p1/lib/method_v15_triplet_production_runtime.py",
    "triplet": "/opt/c5k4-benchmark-v15/p1/lib/run_benchmark_v15_triplet.py",
    "adapter": "/opt/c5k4-benchmark-v15/p1/lib/method_v15_triplet_production_adapter.py",
    "v14_runner": "/opt/c5k4-benchmark-v15/p1/lib/run_benchmark_v14_job.py",
    "activation_schema": "/opt/c5k4-benchmark-v15/p1/schemas/benchmark-production-campaign-activation-v1.5.schema.json",
    "receipt_schema": "/opt/c5k4-benchmark-v15/p1/schemas/benchmark-production-campaign-receipt-v1.5.schema.json",
}


class ProductionCampaignError(ValueError):
    pass


class ProductionCampaignRejected(ProductionCampaignError):
    def __init__(self, receipt: dict[str, Any]):
        super().__init__("production campaign terminated rejected; immutable receipt verified")
        self.receipt = receipt


class SilentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ProductionCampaignError(f"argument contract rejected: {message}")


class CampaignHelper(Protocol):
    def run(self, activation_bytes: bytes, executor_sha256: str) -> bytes: ...


ClosureVerifier = Callable[[dict[str, Any]], dict[str, Path]]
AncestryVerifier = Callable[[dict[str, Any]], str]


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_object(value: Mapping[str, Any], omitted: str) -> str:
    return hashlib.sha256(canonical_bytes({key: item for key, item in value.items() if key != omitted})).hexdigest()


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ProductionCampaignError(f"duplicate JSON key rejected: {key}")
        value[key] = item
    return value


def strict_object(raw: bytes, label: str, maximum: int) -> dict[str, Any]:
    if not raw or len(raw) > maximum or b"\0" in raw:
        raise ProductionCampaignError(f"{label} size or NUL contract rejected")
    try:
        value = json.loads(raw, object_pairs_hook=_no_duplicates)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProductionCampaignError(f"{label} is not strict JSON") from exc
    if not isinstance(value, dict):
        raise ProductionCampaignError(f"{label} must be one object")
    return value


def _sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _git_oid(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(char in "0123456789abcdef" for char in value)


def _signature_payload(role: str, value: Mapping[str, Any]) -> bytes:
    return DOMAINS[role] + b"\0" + canonical_bytes({key: item for key, item in value.items() if key != "signature"})


def load_role_keys() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for role in ROLES:
        path = AUTHORITY_KEY_PATHS[role]
        try:
            metadata = path.lstat(); resolved = path.resolve(strict=True)
            raw = path.read_bytes()
        except OSError as exc:
            raise ProductionCampaignError(f"{role} authority key is absent") from exc
        if (
            resolved != path or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
            or (metadata.st_uid, metadata.st_gid) != (0, 0)
            or stat.S_IMODE(metadata.st_mode) & 0o022 or len(raw) != 32
        ):
            raise ProductionCampaignError(f"{role} authority key is not immutable root-owned raw Ed25519 content")
        cursor = path.parent
        while cursor != Path("/"):
            parent = cursor.lstat()
            if not stat.S_ISDIR(parent.st_mode) or (parent.st_uid, parent.st_gid) != (0, 0) or stat.S_IMODE(parent.st_mode) & 0o022:
                raise ProductionCampaignError(f"{role} authority key has a mutable/non-root parent")
            cursor = cursor.parent
        result[role] = raw
    if len(set(result.values())) != 4:
        raise ProductionCampaignError("the four role-pinned authority keys are not distinct")
    return result


def _verify_role(role: str, section: dict[str, Any], role_keys: Mapping[str, bytes]) -> None:
    if set(role_keys) != set(ROLES) or len(set(role_keys.values())) != 4:
        raise ProductionCampaignError("exactly four distinct role-pinned keys are required")
    signature = section.get("signature")
    if not isinstance(signature, dict) or set(signature) != {"signer_id", "key_sha256", "algorithm", "signature_base64"}:
        raise ProductionCampaignError(f"{role} signature shape differs")
    key = role_keys[role]
    if (
        signature["signer_id"] != SIGNER_IDS[role] or signature["algorithm"] != "Ed25519"
        or signature["key_sha256"] != hashlib.sha256(key).hexdigest()
    ):
        raise ProductionCampaignError(f"{role} signer identity or role-pinned key differs")
    try:
        raw_signature = base64.b64decode(signature["signature_base64"], validate=True)
        if len(raw_signature) != 64:
            raise ValueError("wrong signature length")
        Ed25519PublicKey.from_public_bytes(key).verify(raw_signature, _signature_payload(role, section))
    except (ValueError, InvalidSignature) as exc:
        raise ProductionCampaignError(f"{role} signature is invalid") from exc


def _bootstrap_shape(value: dict[str, Any], role_keys: Mapping[str, bytes]) -> None:
    expected = {"schema", "status", "protocol_version", *ROLES, "activation_sha256"}
    if set(value) != expected or value.get("schema") != "c5k4-method-v1.5-production-campaign-activation-1.0" or value.get("status") != "POST_C1_PRODUCTION_CAMPAIGN_AUTHORIZED" or value.get("protocol_version") != "1.5":
        raise ProductionCampaignError("activation bootstrap shape/status differs")
    if not _sha(value["activation_sha256"]) or value["activation_sha256"] != digest_object(value, "activation_sha256"):
        raise ProductionCampaignError("activation self-digest mismatch")
    for role in ROLES:
        if not isinstance(value[role], dict):
            raise ProductionCampaignError(f"{role} receipt is not an object")
        _verify_role(role, value[role], role_keys)
    expected_authorities = {role: hashlib.sha256(role_keys[role]).hexdigest() for role in ROLES}
    if value["harness"].get("authority_key_digests") != expected_authorities or len(set(expected_authorities.values())) != 4:
        raise ProductionCampaignError("harness acceptance does not precommit the four role-key identities")
    c1, freeze, targets = value["c1"], value["freeze"], value["private_targets"]
    if not _git_oid(c1.get("c1_attestation_commit")) or freeze.get("c1_attestation_commit") != c1["c1_attestation_commit"] or not _git_oid(freeze.get("run_freeze_commit")):
        raise ProductionCampaignError("C1/freeze commits are not exact 40-hex identities")
    selected = c1.get("selected_cluster_ids")
    frozen = freeze.get("triplets")
    private = targets.get("targets")
    if not isinstance(selected, list) or len(selected) != 12 or len(set(selected)) != 12 or not isinstance(frozen, list) or not isinstance(private, list) or len(frozen) != 12 or len(private) != 12:
        raise ProductionCampaignError("activation is not exactly twelve unique sealed triplets")
    if [row.get("cluster_id") for row in frozen if isinstance(row, dict)] != selected or [row.get("cluster_id") for row in private if isinstance(row, dict)] != selected:
        raise ProductionCampaignError("C1/freeze/private-target closures differ")


def _immutable_file(path: Path, expected_sha256: str, label: str) -> Path:
    try:
        metadata = path.lstat(); resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ProductionCampaignError(f"{label} is absent") from exc
    if (
        resolved != path or not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
        or (metadata.st_uid, metadata.st_gid) != (0, 0) or stat.S_IMODE(metadata.st_mode) & 0o022
        or hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256
    ):
        raise ProductionCampaignError(f"{label} is not exact immutable root-owned content")
    cursor = path.parent
    while cursor != Path("/"):
        info = cursor.lstat()
        if not stat.S_ISDIR(info.st_mode) or (info.st_uid, info.st_gid) != (0, 0) or stat.S_IMODE(info.st_mode) & 0o022:
            raise ProductionCampaignError(f"{label} has a mutable/non-root parent")
        cursor = cursor.parent
    return path


def host_fingerprint() -> str:
    try:
        boot = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()
        machine = Path("/etc/machine-id").read_text(encoding="ascii").strip()
    except OSError as exc:
        raise ProductionCampaignError("same-boot host identity is unavailable") from exc
    if not boot or not machine:
        raise ProductionCampaignError("same-boot host identity is empty")
    uname = os.uname()
    return hashlib.sha256(canonical_bytes({"boot_id": boot, "machine_id": machine, "kernel": uname.release, "machine": uname.machine})).hexdigest()


def verify_immutable_closure(harness: dict[str, Any]) -> dict[str, Path]:
    closure = harness.get("implementation_closure")
    if not isinstance(closure, dict) or set(closure) != set(EXPECTED_CLOSURE_PATHS):
        raise ProductionCampaignError("harness exact-C implementation closure differs")
    if (
        harness.get("host_fingerprint_sha256") != host_fingerprint()
        or harness.get("runtime_sha256") != closure.get("runtime", {}).get("sha256")
        or harness.get("production_runtime_distinct") is not True
        or harness.get("runtime_sha256") == harness.get("fixture_runtime_sha256")
        or harness.get("network_default_deny") is not True
        or harness.get("target_output_private") is not True
    ):
        raise ProductionCampaignError("harness host/runtime/network acceptance differs")
    result: dict[str, Path] = {}
    for role, expected_path in EXPECTED_CLOSURE_PATHS.items():
        row = closure[role]
        if not isinstance(row, dict) or set(row) != {"path", "sha256"} or row["path"] != expected_path or not _sha(row["sha256"]):
            raise ProductionCampaignError(f"harness {role} closure row differs")
        result[role] = _immutable_file(Path(row["path"]), row["sha256"], role)
    executor = harness.get("executor_acceptance")
    journal = harness.get("journal_acceptance")
    if not isinstance(executor, dict) or not isinstance(journal, dict):
        raise ProductionCampaignError("executor or journal acceptance is absent")
    required_executor = {
        "binary_path": str(EXECUTOR_PATH), "descriptor_pinned_inputs": True,
        "network_namespace_default_deny": True, "cgroup_v2_cpu_accounting": True,
        "whole_tree_cgroup_kill": True, "setsid_escape_contained": True,
        "wall_cap_seconds": 60, "ilp_cap_seconds": 60,
    }
    if any(executor.get(key) != item for key, item in required_executor.items()) or not _sha(executor.get("binary_sha256")):
        raise ProductionCampaignError("real executor enforcement acceptance differs")
    if harness.get("executor_binary_path") != executor["binary_path"] or harness.get("executor_binary_sha256") != executor["binary_sha256"]:
        raise ProductionCampaignError("harness executor provenance fields disagree")
    _immutable_file(EXECUTOR_PATH, executor["binary_sha256"], "production executor")
    executor_metadata = EXECUTOR_PATH.lstat()
    if stat.S_IMODE(executor_metadata.st_mode) != 0o555 or executor_metadata.st_mode & (stat.S_ISUID | stat.S_ISGID):
        raise ProductionCampaignError("production executor mode is not exactly root-owned 0555 without setid")
    try:
        capability = os.getxattr(EXECUTOR_PATH, "security.capability", follow_symlinks=False)
    except OSError as exc:
        if exc.errno not in {errno.ENODATA, errno.ENOTSUP, errno.EOPNOTSUPP}:
            raise ProductionCampaignError("production executor file capabilities cannot be inspected") from exc
    else:
        if capability:
            raise ProductionCampaignError("production executor has forbidden file capabilities")
    required_journal = {
        "backend": "AWS_S3_OBJECT_LOCK_COMPLIANCE", "append_only": True,
        "signed_entries": True, "crash_recovery": "RESUME_OR_TERMINAL_REJECT",
        "caller_deletion_can_reauthorize": False,
    }
    if any(journal.get(key) != item for key, item in required_journal.items()) or not _sha(journal.get("acceptance_sha256")):
        raise ProductionCampaignError("durable WORM journal acceptance differs")
    return result


def _validate_schema(value: object, path: Path, label: str) -> None:
    schema = strict_object(path.read_bytes(), f"{label} schema", MAX_ACTIVATION_BYTES)
    errors = sorted(jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        location = ".".join(str(item) for item in errors[0].absolute_path) or "$"
        raise ProductionCampaignError(f"{label} schema failure at {location}: {errors[0].message}")


def _post_schema_invariants(value: dict[str, Any]) -> None:
    harness = value["harness"]
    forbidden_target_digests = {
        harness["runtime_sha256"], harness["fixture_runtime_sha256"],
        harness["executor_acceptance"]["binary_sha256"],
        *(row["sha256"] for row in harness["implementation_closure"].values()),
    }
    all_input_paths: list[Path] = []
    all_private_paths: list[Path] = []
    for target in value["private_targets"]["targets"]:
        path = Path(target["path"])
        if not path.is_absolute() or any(part in {".", ".."} for part in path.parts):
            raise ProductionCampaignError("private target locator is not normalized and absolute")
        if target["sha256"] in forbidden_target_digests:
            raise ProductionCampaignError("fixture, launcher, runtime, schema, or executor masquerades as a private target")
        for arm in ARMS:
            argv = target["argv_by_arm"][arm]
            if argv[0] != "/inputs/COMMON_TARGET_BUNDLE" or any("\0" in item or "\n" in item or "\r" in item for item in argv):
                raise ProductionCampaignError("private target argv escapes the sealed COMMON_TARGET_BUNDLE")
            roots = target["allowed_roots_by_arm"][arm]
            if len({root["root_role"] for root in roots}) != len(roots):
                raise ProductionCampaignError("allowed input root roles are not unique")
            common = [root for root in roots if root["root_role"] == "COMMON_TARGET_BUNDLE"]
            if len(common) != 1 or common[0]["path"] != target["path"] or common[0]["sha256"] != target["sha256"]:
                raise ProductionCampaignError("COMMON_TARGET_BUNDLE does not equal the signed private target")
            for root in roots:
                path = Path(root["path"])
                if not path.is_absolute() or any(part in {".", ".."} for part in path.parts) or type(root["uid"]) is not int or type(root["gid"]) is not int or type(root["mode"]) is not int or root["mode"] & (0o222 | stat.S_ISUID | stat.S_ISGID):
                    raise ProductionCampaignError("allowed input root identity/mode is not exact")
                all_input_paths.append(path)
            private = target["private_roots_by_arm"][arm]
            private_path = Path(private["path"])
            if not private_path.is_absolute() or any(part in {".", ".."} for part in private_path.parts) or type(private["uid"]) is not int or type(private["gid"]) is not int or private["mode"] != 0o700:
                raise ProductionCampaignError("private writable root identity/mode is not exact 0700")
            all_private_paths.append(private_path)
    def overlap(left: Path, right: Path) -> bool:
        try: right.relative_to(left); return True
        except ValueError: pass
        try: left.relative_to(right); return True
        except ValueError: return False
    if any(overlap(left, right) for index, left in enumerate(all_private_paths) for right in all_private_paths[index + 1:]):
        raise ProductionCampaignError("the 36 signed private writable roots overlap")
    if any(overlap(private, source) for private in all_private_paths for source in all_input_paths):
        raise ProductionCampaignError("a signed private writable root overlaps an authenticated input root")


def _git(repo: Path, *args: str) -> bytes:
    command = ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never", "-C", str(repo), *args]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False, env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"})
    if result.returncode != 0:
        raise ProductionCampaignError("offline C1/freeze Git verification failed")
    return result.stdout


def verify_git_ancestry(value: dict[str, Any]) -> str:
    c1, freeze = value["c1"], value["freeze"]
    if c1["repository_path"] != freeze["repository_path"]:
        raise ProductionCampaignError("C1 and freeze locators name different repositories")
    identity = (c1.get("repository_uid"), c1.get("repository_gid"), c1.get("repository_mode"))
    if identity != (freeze.get("repository_uid"), freeze.get("repository_gid"), freeze.get("repository_mode")) or any(type(item) is not int for item in identity):
        raise ProductionCampaignError("C1 and freeze repository identities differ")
    repo = Path(c1["repository_path"])
    try:
        resolved = repo.resolve(strict=True); metadata = repo.lstat()
    except OSError as exc:
        raise ProductionCampaignError("C1/freeze repository locator is absent") from exc
    if resolved != repo or not stat.S_ISDIR(metadata.st_mode) or identity != (metadata.st_uid, metadata.st_gid, stat.S_IMODE(metadata.st_mode)) or identity[2] & 0o022:
        raise ProductionCampaignError("C1/freeze repository locator is linked or non-directory")
    c1_oid, freeze_oid = c1["c1_attestation_commit"], freeze["run_freeze_commit"]
    if _git(repo, "rev-parse", "--verify", f"{c1_oid}^{{commit}}").strip().decode() != c1_oid or _git(repo, "rev-parse", "--verify", f"{freeze_oid}^{{commit}}").strip().decode() != freeze_oid:
        raise ProductionCampaignError("C1/freeze locators do not resolve to the exact commits")
    _git(repo, "merge-base", "--is-ancestor", c1_oid, freeze_oid)
    envelope_blobs = []
    for row in freeze["triplets"]:
        path = Path(row["envelope_path"])
        try: relative = path.relative_to(repo).as_posix()
        except ValueError as exc: raise ProductionCampaignError("frozen envelope locator escapes its repository") from exc
        committed = _git(repo, "show", f"{freeze_oid}:{relative}")
        current = path.read_bytes()
        if committed != current:
            raise ProductionCampaignError("private envelope bytes differ from the frozen Git blob")
        envelope = strict_object(committed, "frozen execution envelope", MAX_ACTIVATION_BYTES)
        if envelope.get("envelope_sha256") != row["envelope_sha256"] or digest_object(envelope, "envelope_sha256") != row["envelope_sha256"]:
            raise ProductionCampaignError("frozen envelope self-digest differs from its signed locator")
        envelope_blobs.append(hashlib.sha256(committed).hexdigest())
    proof = {"repository_path_sha256": hashlib.sha256(str(repo).encode()).hexdigest(), "c1_attestation_commit": c1_oid, "run_freeze_commit": freeze_oid, "envelope_blob_sha256s": envelope_blobs}
    return hashlib.sha256(canonical_bytes(proof)).hexdigest()


def _authenticate_activation(raw: bytes, role_keys: Mapping[str, bytes], closure_verifier: ClosureVerifier, ancestry_verifier: AncestryVerifier) -> tuple[dict[str, Any], dict[str, Path], str]:
    value = strict_object(raw, "production activation", MAX_ACTIVATION_BYTES)
    _bootstrap_shape(value, role_keys)
    closure = closure_verifier(value["harness"])
    if Path(__file__).resolve() != closure["launcher"]:
        raise ProductionCampaignError("executing launcher is not the exact accepted root-owned launcher")
    _validate_schema(value, closure["activation_schema"], "production activation")
    _post_schema_invariants(value)
    return value, closure, ancestry_verifier(value)


def authenticate_activation(raw: bytes) -> tuple[dict[str, Any], dict[str, Path], str]:
    """Production authentication has no injectable trust or filesystem seam."""

    return _authenticate_activation(raw, load_role_keys(), verify_immutable_closure, verify_git_ancestry)


def _verify_receipt(raw: bytes, activation: dict[str, Any], closure: dict[str, Path], harness_key: bytes, ancestry_sha256: str) -> dict[str, Any]:
    receipt = strict_object(raw, "production campaign receipt", MAX_RECEIPT_BYTES)
    _validate_schema(receipt, closure["receipt_schema"], "production campaign receipt")
    signature = receipt.get("signature", {})
    if signature.get("signer_id") != SIGNER_IDS["harness"] or signature.get("key_sha256") != hashlib.sha256(harness_key).hexdigest() or signature.get("algorithm") != "Ed25519":
        raise ProductionCampaignError("campaign receipt signer is not the role-pinned harness")
    unsigned = {key: item for key, item in receipt.items() if key not in {"receipt_sha256", "signature"}}
    digest = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
    if receipt.get("receipt_sha256") != digest or receipt.get("activation_sha256") != activation["activation_sha256"]:
        raise ProductionCampaignError("campaign receipt digest/binding differs")
    try:
        Ed25519PublicKey.from_public_bytes(harness_key).verify(base64.b64decode(signature["signature_base64"], validate=True), RECEIPT_DOMAIN + b"\0" + bytes.fromhex(digest))
    except (ValueError, InvalidSignature) as exc:
        raise ProductionCampaignError("campaign receipt signature is invalid") from exc
    if type(receipt.get("triplet_count")) is not int or receipt["triplet_count"] != 12 or type(receipt.get("arm_count")) is not int or receipt["arm_count"] != 36 or type(receipt.get("process_tree_count")) is not int or receipt["process_tree_count"] != 288:
        raise ProductionCampaignError("campaign receipt count types/values differ")
    if (
        receipt.get("c1_attestation_commit") != activation["c1"]["c1_attestation_commit"]
        or receipt.get("run_freeze_commit") != activation["freeze"]["run_freeze_commit"]
        or receipt.get("git_ancestry_verified") is not True
        or receipt.get("git_ancestry_evidence_locator", {}).get("object_sha256") != ancestry_sha256
        or receipt.get("network_policy") != "DENY"
        or receipt.get("target_output_revealed") is not False
    ):
        raise ProductionCampaignError("campaign receipt chronology/network/reveal binding differs")
    triplets = receipt.get("triplets")
    if not isinstance(triplets, list) or len(triplets) != 12:
        raise ProductionCampaignError("campaign receipt lacks twelve replayable triplets")
    expected_tree_ids = {f"{arm}-{index}" for arm in ARMS for index in range(8)}
    accepted_all = True
    for index, row in enumerate(triplets):
        expected_cluster = activation["c1"]["selected_cluster_ids"][index]
        expected_envelope = activation["freeze"]["triplets"][index]["envelope_sha256"]
        if (
            row.get("cluster_id_sha256") != hashlib.sha256(expected_cluster.encode()).hexdigest()
            or row.get("envelope_sha256") != expected_envelope
            or type(row.get("tree_count")) is not int or row["tree_count"] != 24
        ):
            raise ProductionCampaignError("triplet receipt mapping differs from C1/freeze order")
        trees = row.get("trees")
        if not isinstance(trees, list) or len(trees) != 24 or {tree.get("tree_id") for tree in trees if isinstance(tree, dict)} != expected_tree_ids:
            raise ProductionCampaignError("triplet receipt does not map the exact 24 trees")
        target = activation["private_targets"]["targets"][index]
        uses_ilp = target["uses_ilp"]
        for tree in trees:
            arm, tree_index_text = tree["tree_id"].rsplit("-", 1)
            invocation = tree.get("invocation")
            roots = target["allowed_roots_by_arm"][arm]
            private_base = target["private_roots_by_arm"][arm]
            expected_private = {"path": f"{private_base['path']}/tree-{tree_index_text}", "uid": private_base["uid"], "gid": private_base["gid"], "mode": private_base["mode"]}
            expected_descriptor_manifest = hashlib.sha256(canonical_bytes({"allowed_roots": roots, "private_root": expected_private})).hexdigest()
            if not isinstance(invocation, dict) or (
                invocation.get("cluster_id_sha256") != row["cluster_id_sha256"]
                or invocation.get("envelope_sha256") != row["envelope_sha256"]
                or invocation.get("arm") != arm
                or type(invocation.get("tree_index")) is not int or invocation["tree_index"] != int(tree_index_text)
                or type(invocation.get("wall_cap_seconds")) is not int or invocation["wall_cap_seconds"] != 60
                or invocation.get("ilp_cap_seconds") != (60 if uses_ilp else None)
                or invocation.get("network_policy") != "DENY"
                or invocation.get("executor_binary_sha256") != activation["harness"]["executor_acceptance"]["binary_sha256"]
                or invocation.get("argv_sha256") != hashlib.sha256(canonical_bytes(target["argv_by_arm"][arm])).hexdigest()
                or invocation.get("allowed_root_manifest_sha256") != hashlib.sha256(canonical_bytes(roots)).hexdigest()
                or invocation.get("private_root_sha256") != hashlib.sha256(canonical_bytes(expected_private)).hexdigest()
                or tree.get("descriptor_manifest_sha256") != expected_descriptor_manifest
                or tree.get("invocation_sha256") != hashlib.sha256(canonical_bytes(invocation)).hexdigest()
            ):
                raise ProductionCampaignError("tree invocation is not replayably bound to its triplet and executor")
            tree_signature = tree["signature"]
            strict_success = (
                tree.get("network_denied") is True and tree.get("timed_out") is False
                and type(tree.get("returncode")) is int and tree["returncode"] == 0
                and tree.get("descriptor_pinned_inputs") is True
                and tree.get("whole_tree_cgroup_killed_or_reaped") is True
                and tree.get("setsid_escape_contained") is True
            )
            if (
                tree_signature["signer_id"] != SIGNER_IDS["harness"]
                or tree_signature["key_sha256"] != hashlib.sha256(harness_key).hexdigest()
                or tree_signature["algorithm"] != "Ed25519"
                or type(tree.get("accepted")) is not bool or tree["accepted"] is not strict_success
                or type(tree.get("network_denied")) is not bool or type(tree.get("timed_out")) is not bool
                or (tree.get("returncode") is not None and type(tree.get("returncode")) is not int)
                or type(tree.get("descriptor_pinned_inputs")) is not bool
                or type(tree.get("whole_tree_cgroup_killed_or_reaped")) is not bool
                or type(tree.get("setsid_escape_contained")) is not bool
                or type(tree.get("cpu_usec")) is not int or not 0 <= tree["cpu_usec"] <= 60_000_000
                or type(tree.get("wall_milliseconds")) is not int or not 0 <= tree["wall_milliseconds"] <= 60_000
                or tree.get("ilp_cap_seconds") != (60 if uses_ilp else None)
            ):
                raise ProductionCampaignError("tree completion type, budget, or enforcement evidence differs")
            tree_unsigned = {key: item for key, item in tree.items() if key not in {"completion_sha256", "journal_locator", "signature"}}
            tree_digest = hashlib.sha256(canonical_bytes(tree_unsigned)).hexdigest()
            if tree.get("completion_sha256") != tree_digest:
                raise ProductionCampaignError("tree completion self-digest mismatch")
            try:
                Ed25519PublicKey.from_public_bytes(harness_key).verify(
                    base64.b64decode(tree_signature["signature_base64"], validate=True),
                    TREE_RECEIPT_DOMAIN + b"\0" + bytes.fromhex(tree_digest),
                )
            except (ValueError, InvalidSignature) as exc:
                raise ProductionCampaignError("tree completion signature is invalid") from exc
            evidence_pairs = {
                "descriptor_manifest": "descriptor_manifest_sha256", "namespace_inode_set": "namespace_inode_set_sha256",
                "process_tree_audit": "process_tree_audit_sha256", "cgroup_v2": "cgroup_v2_sha256",
            }
            if any(tree["evidence_locators"][locator]["object_sha256"] != tree[digest] for locator, digest in evidence_pairs.items()):
                raise ProductionCampaignError("an enforcement evidence digest is not bound to its exact WORM object")
        arm_cpu = {
            arm: sum(tree["cpu_usec"] for tree in trees if tree["tree_id"].startswith(arm + "-"))
            for arm in ARMS
        }
        if any(value > 480_000_000 for value in arm_cpu.values()):
            raise ProductionCampaignError("per-arm CPU budget exceeded")
        row_success = all(tree["accepted"] is True for tree in trees)
        if type(row.get("accepted")) is not bool or row["accepted"] is not row_success:
            raise ProductionCampaignError("triplet accepted flag differs from strict tree evidence")
        if not row_success:
            accepted_all = False
    expected_status = "PRODUCTION_CAMPAIGN_TERMINATED" if accepted_all else "PRODUCTION_CAMPAIGN_REJECTED_AFTER_COMPLETE_BARRIERS"
    if receipt.get("status") != expected_status:
        raise ProductionCampaignError("campaign terminal status differs from tree evidence")
    _verify_journal(receipt, activation, harness_key)
    return receipt


def _verify_journal(receipt: dict[str, Any], activation: dict[str, Any], harness_key: bytes) -> None:
    entries = receipt.get("journal", {}).get("entries")
    if not isinstance(entries, list) or len(entries) != 578 or receipt["journal"].get("entry_count") != 578:
        raise ProductionCampaignError("durable journal is not the exact 578-entry campaign state machine")
    tree_maps = [{tree["tree_id"]: tree for tree in row["trees"]} for row in receipt["triplets"]]
    expected: list[tuple[str, int | None, str | None, str]] = [("PREPARE", None, None, activation["activation_sha256"])]
    ordered_ids = [f"{arm}-{index}" for arm in ARMS for index in range(8)]
    for triplet_index in range(12):
        expected.extend(("START", triplet_index, tree_id, tree_maps[triplet_index][tree_id]["invocation_sha256"]) for tree_id in ordered_ids)
        expected.extend(("COMPLETE", triplet_index, tree_id, tree_maps[triplet_index][tree_id]["completion_sha256"]) for tree_id in ordered_ids)
    final_payload = hashlib.sha256(canonical_bytes([tree_maps[index][tree_id]["completion_sha256"] for index in range(12) for tree_id in ordered_ids])).hexdigest()
    expected.append(("FINALIZE", None, None, final_payload))
    previous = ZERO_SHA256
    locator_versions: set[tuple[str, str, str]] = set()
    complete_locators: dict[tuple[int, str], dict[str, Any]] = {}
    for sequence, (entry, wanted) in enumerate(zip(entries, expected)):
        state, triplet_index, tree_id, payload = wanted
        if (
            type(entry.get("sequence")) is not int or entry["sequence"] != sequence
            or entry.get("state") != state or entry.get("triplet_index") != triplet_index
            or entry.get("tree_id") != tree_id or entry.get("prior_entry_sha256") != previous
            or entry.get("payload_sha256") != payload
        ):
            raise ProductionCampaignError("WORM journal has a gap, replay, reorder, or payload mismatch")
        unsigned = {key: item for key, item in entry.items() if key not in {"entry_sha256", "locator", "signature"}}
        digest = hashlib.sha256(canonical_bytes(unsigned)).hexdigest()
        locator = entry["locator"]; signature = entry["signature"]
        if (
            entry.get("entry_sha256") != digest or locator.get("object_sha256") != digest
            or locator.get("signed_journal_entry_sha256") != digest
            or signature.get("signer_id") != SIGNER_IDS["harness"]
            or signature.get("key_sha256") != hashlib.sha256(harness_key).hexdigest()
        ):
            raise ProductionCampaignError("journal entry is not self-bound to its signed immutable object")
        version = (locator["bucket_sha256"], locator["key_sha256"], locator["version_id_sha256"])
        if version in locator_versions:
            raise ProductionCampaignError("journal reuses an immutable object version")
        locator_versions.add(version)
        try:
            Ed25519PublicKey.from_public_bytes(harness_key).verify(base64.b64decode(signature["signature_base64"], validate=True), JOURNAL_ENTRY_DOMAIN + b"\0" + bytes.fromhex(digest))
        except (ValueError, InvalidSignature) as exc:
            raise ProductionCampaignError("journal entry signature is invalid") from exc
        if state == "COMPLETE": complete_locators[(triplet_index, tree_id)] = locator
        previous = digest
    if receipt["journal_root"] != entries[-1]["locator"]:
        raise ProductionCampaignError("journal root is not the immutable FINALIZE entry")
    for triplet_index, trees in enumerate(tree_maps):
        for tree_id, tree in trees.items():
            if tree["journal_locator"] != complete_locators[(triplet_index, tree_id)]:
                raise ProductionCampaignError("tree completion locator is not its durable COMPLETE journal entry")


class InstalledCampaignHelper:
    def run(self, activation_bytes: bytes, executor_sha256: str) -> bytes:
        try:
            descriptor = os.open(EXECUTOR_PATH, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
            metadata = os.fstat(descriptor)
            chunks = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk: break
                chunks.append(chunk)
            raw_executor = b"".join(chunks)
            try:
                descriptor_capability = os.getxattr(f"/proc/self/fd/{descriptor}", "security.capability")
            except OSError as exc:
                if exc.errno not in {errno.ENODATA, errno.ENOTSUP, errno.EOPNOTSUPP}:
                    raise ProductionCampaignError("descriptor-pinned executor capabilities cannot be inspected") from exc
                descriptor_capability = b""
            if (
                not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
                or (metadata.st_uid, metadata.st_gid) != (0, 0) or stat.S_IMODE(metadata.st_mode) & 0o022
                or stat.S_IMODE(metadata.st_mode) != 0o555 or metadata.st_mode & (stat.S_ISUID | stat.S_ISGID)
                or descriptor_capability
                or not raw_executor.startswith(b"\x7fELF")
                or hashlib.sha256(raw_executor).hexdigest() != executor_sha256
            ):
                raise ProductionCampaignError("descriptor-pinned executor provenance differs")
            process = subprocess.run(
                [f"/proc/self/fd/{descriptor}", "--production-campaign", "--expected-self-sha256", executor_sha256],
                input=activation_bytes, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, pass_fds=(descriptor,),
                check=False, timeout=CAMPAIGN_WALL_CAP_SECONDS,
                env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C", "TZ": "UTC"},
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ProductionCampaignError("production helper could not be descriptor-pinned") from exc
        finally:
            if "descriptor" in locals(): os.close(descriptor)
        if process.returncode != 0 or len(process.stdout) > MAX_RECEIPT_BYTES:
            raise ProductionCampaignError("production helper failed closed")
        return process.stdout


def execute_campaign(raw: bytes) -> dict[str, Any]:
    role_keys = load_role_keys()
    activation, closure, ancestry_sha256 = _authenticate_activation(raw, role_keys, verify_immutable_closure, verify_git_ancestry)
    # There is deliberately no local claim or state directory.  The accepted
    # helper atomically PREPAREs the WORM journal before it opens target bytes.
    receipt_raw = InstalledCampaignHelper().run(raw, activation["harness"]["executor_acceptance"]["binary_sha256"])
    receipt = _verify_receipt(receipt_raw, activation, closure, role_keys["harness"], ancestry_sha256)
    if receipt["status"] != "PRODUCTION_CAMPAIGN_TERMINATED":
        raise ProductionCampaignRejected(receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = SilentParser(description=__doc__)
    parser.add_argument("--activation", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        raw = args.activation.read_bytes()
        execute_campaign(raw)
        return 0
    except (OSError, ProductionCampaignError, ValueError):
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
