#!/usr/bin/env python3
"""Verify prospective Method v1.5 identity-only generated artifacts.

This verifier deliberately does not maintain an output-hash allowlist.  A
machine-contact proof is tied to one immutable Git blob locator and is emitted
only after the exact artifact has been reproduced twice from a producer,
contract, and inputs that were already present in the output commit's parent.

The replay contract is intentionally narrow: a content-addressed Python
producer writes one JSON artifact to stdout.  Interactive/session output is
not an accepted delivery path, even when its bytes equal a verified artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile
from typing import Any


MANIFEST_SCHEMA = "c5k4-generated-identity-manifest-1.5"
CONTRACT_SCHEMA = "c5k4-generated-identity-replay-contract-1.5"
RECEIPT_SCHEMA = "c5k4-generated-identity-verification-1.5"
SAFE_SURFACE = "IDENTITY_ONLY_V1_5"
HEX_OBJECT = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
SAFE_STRING = re.compile(r"[A-Za-z0-9_./:#@+\-=,]*")

# The executable, not an output claim, fixes the only artifact families that
# may be certified.  Schema versions may become more specific after ``1.5-``.
ARTIFACT_SCHEMAS = {
    "open_inventory": "c5k4-open-inventory-1.5",
    "question_cluster_pool": "c5k4-question-cluster-pool-1.5",
    "eligible_cluster_pool": "c5k4-eligible-cluster-pool-1.5",
    "future_cohort": "c5k4-future-cohort-1.5",
    "identity_counts": "c5k4-registry-identity-counts-1.5",
    "provenance_inventory": "c5k4-provenance-inventory-1.5",
    "quota_feasibility": "c5k4-quota-feasibility-1.5",
}

# A closed safe surface prevents a manifest from declaring prose-shaped output
# safe.  Values may be identifiers, hashes, enums, booleans, integers, lists,
# and dictionaries using these keys only.
SAFE_KEYS = {
    "schema_version", "artifact_kind", "generated_by_sha256", "input_sha256s",
    "declarations", "clusters", "records", "strata", "counts",
    "cluster_id", "declaration_id", "declaration_name", "module_path",
    "source_path", "namespace", "aliases", "alias", "alias_kind",
    "sibling_ids", "equivalent_ids", "negation_ids", "stratum", "status",
    "eligible", "exclusion_codes", "first_introduction_commit", "present_at_u1",
    "development_excluded", "provenance_class", "evidence_counts", "class",
    "count", "quota", "surplus", "deficit", "quota_satisfied", "complete",
    "record_count", "cluster_count", "eligible_cluster_count",
    "required_cluster_count", "all_quotas_satisfied", "sha256", "byte_count",
    "source_id", "source_kind", "locator", "role", "content_sha256",
    "content_schema", "unit_identity_sha256", "commit", "tree", "blob",
}


class VerificationError(ValueError):
    """A fail-closed generated-artifact verification failure."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def unit_identity_sha256(
    source_id: str, source_kind: str, locator: str, role: str,
    content_sha256: str, content_schema: str,
) -> str:
    return sha256(canonical_json({
        "source_id": source_id,
        "source_kind": source_kind,
        "locator": locator,
        "role": role,
        "content_sha256": content_sha256,
        "content_schema": content_schema,
    }))


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        stderr=subprocess.PIPE,
    )


def _exact_commit(repo: Path, value: object, label: str) -> str:
    if not isinstance(value, str) or not HEX_OBJECT.fullmatch(value):
        raise VerificationError(f"{label} must be an exact Git object id")
    try:
        resolved = _git(repo, "rev-parse", f"{value}^{{commit}}").decode().strip()
    except subprocess.CalledProcessError as exc:
        raise VerificationError(f"{label} is not a local commit") from exc
    if resolved != value:
        raise VerificationError(f"{label} does not resolve to itself")
    return resolved


def _safe_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError(f"{label} must be a nonempty repository path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or str(path) != value:
        raise VerificationError(f"{label} must be a normalized relative path")
    return value


def _checked_sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not HEX_SHA256.fullmatch(value):
        raise VerificationError(f"{label} must be a lowercase SHA-256")
    return value


def _blob(repo: Path, commit: str, path: str) -> tuple[str, bytes]:
    try:
        oid = _git(repo, "rev-parse", f"{commit}:{path}").decode().strip()
        raw = _git(repo, "show", f"{commit}:{path}")
    except subprocess.CalledProcessError as exc:
        raise VerificationError(f"missing historical path {path!r} at {commit}") from exc
    if not HEX_OBJECT.fullmatch(oid):
        raise VerificationError(f"historical path {path!r} is not a blob")
    return oid, raw


def _verify_historical_file(repo: Path, commit: str, row: dict[str, Any], label: str) -> bytes:
    if not isinstance(row, dict):
        raise VerificationError(f"{label} must be an object")
    path = _safe_path(row.get("path"), f"{label}.path")
    expected = _checked_sha(row.get("sha256"), f"{label}.sha256")
    _, raw = _blob(repo, commit, path)
    if sha256(raw) != expected:
        raise VerificationError(f"{label} historical bytes do not match")
    return raw


def _schema_matches(kind: object, schema: object) -> bool:
    prefix = ARTIFACT_SCHEMAS.get(kind) if isinstance(kind, str) else None
    return isinstance(schema, str) and prefix is not None and (
        schema == prefix or schema.startswith(prefix + "-")
    )


def _validate_safe_value(value: object, path: str = "$") -> None:
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, str):
        if len(value) > 1024 or not SAFE_STRING.fullmatch(value):
            raise VerificationError(f"unsafe free-form string at {path}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _validate_safe_value(child, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or key not in SAFE_KEYS:
                raise VerificationError(f"key {key!r} is outside the identity-only safe surface at {path}")
            _validate_safe_value(child, f"{path}.{key}")
        return
    raise VerificationError(f"unsupported JSON type at {path}")


def validate_identity_artifact(raw: bytes, kind: str, schema: str) -> dict[str, Any]:
    if b"\x00" in raw:
        raise VerificationError("artifact is not textual JSON")
    try:
        value = json.loads(raw.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError("artifact is not one complete UTF-8 JSON value") from exc
    if not isinstance(value, dict):
        raise VerificationError("artifact must be a JSON object")
    if not _schema_matches(kind, schema) or value.get("schema_version") != schema:
        raise VerificationError("artifact kind/schema is not on the frozen safe surface")
    if value.get("artifact_kind", kind) != kind:
        raise VerificationError("artifact_kind disagrees with the verification claim")
    _validate_safe_value(value)
    return value


def _load_contract(raw: bytes) -> dict[str, Any]:
    try:
        contract = json.loads(raw.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError("replay contract is not UTF-8 JSON") from exc
    required = {
        "schema_version", "producer_path", "argv", "input_paths", "output_mode",
        "artifact_kind", "output_schema_version", "safe_surface", "network",
        "interactive_delivery", "timeout_seconds",
    }
    if not isinstance(contract, dict) or set(contract) != required:
        raise VerificationError("replay contract fields are not exact")
    if contract["schema_version"] != CONTRACT_SCHEMA:
        raise VerificationError("unsupported replay contract schema")
    if contract["output_mode"] != "stdout" or contract["safe_surface"] != SAFE_SURFACE:
        raise VerificationError("contract does not use the bounded identity-only stdout surface")
    if contract["network"] != "FORBIDDEN" or contract["interactive_delivery"] is not False:
        raise VerificationError("contract permits network or interactive delivery")
    timeout = contract["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 60:
        raise VerificationError("contract timeout_seconds must be an integer in 1..60")
    return contract


def _extract_tree(repo: Path, commit: str, target: Path) -> None:
    archive = _git(repo, "archive", "--format=tar", commit)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise VerificationError("unsafe member in Git archive")
        tar.extractall(target, filter="data")


def _replay_once(repo: Path, basis: str, contract: dict[str, Any], producer_path: str) -> bytes:
    argv = contract["argv"]
    if not isinstance(argv, list) or len(argv) < 2 or not all(isinstance(x, str) for x in argv):
        raise VerificationError("contract argv must be a nonempty string array")
    if argv[:2] != ["{PYTHON}", producer_path]:
        raise VerificationError("contract may execute only the verified Python producer")
    for index, arg in enumerate(argv[2:], 2):
        if "\x00" in arg or arg.startswith("/") or ".." in PurePosixPath(arg).parts:
            raise VerificationError(f"unsafe replay argument at argv[{index}]")
    with tempfile.TemporaryDirectory(prefix="c5k4-v15-replay-") as directory:
        root = Path(directory)
        _extract_tree(repo, basis, root)
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1",
            "LC_ALL": "C", "LANG": "C", "TZ": "UTC",
            "HOME": str(root / ".empty-home"), "NO_PROXY": "*", "no_proxy": "*",
        }
        completed = subprocess.run(
            [sys.executable, *argv[1:]], cwd=root, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=contract["timeout_seconds"], check=False,
        )
        if completed.returncode != 0:
            raise VerificationError(f"replay failed with exit code {completed.returncode}")
        if completed.stderr:
            raise VerificationError("replay wrote to stderr")
        return completed.stdout


def verify(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return a locator-specific proof or raise ``VerificationError``."""

    required = {"schema_version", "repository", "basis_commit", "output_commit", "producer", "contract", "inputs", "output"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise VerificationError("manifest fields are not exact")
    if manifest["schema_version"] != MANIFEST_SCHEMA:
        raise VerificationError("unsupported manifest schema")
    repo = Path(manifest["repository"])
    if not repo.is_absolute():
        raise VerificationError("repository must be an absolute local path")
    basis = _exact_commit(repo, manifest["basis_commit"], "basis_commit")
    output_commit = _exact_commit(repo, manifest["output_commit"], "output_commit")
    parents = _git(repo, "rev-list", "--parents", "-n", "1", output_commit).decode().split()
    if len(parents) != 2 or parents[1] != basis:
        raise VerificationError("basis_commit must be the output commit's sole first parent")

    producer_raw = _verify_historical_file(repo, basis, manifest["producer"], "producer")
    del producer_raw
    contract_raw = _verify_historical_file(repo, basis, manifest["contract"], "contract")
    contract = _load_contract(contract_raw)
    producer_path = _safe_path(manifest["producer"].get("path"), "producer.path")
    if contract["producer_path"] != producer_path:
        raise VerificationError("contract producer_path disagrees with manifest")

    inputs = manifest["inputs"]
    if not isinstance(inputs, list):
        raise VerificationError("inputs must be a list")
    input_paths: list[str] = []
    input_shas: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(inputs):
        raw = _verify_historical_file(repo, basis, row, f"inputs[{index}]")
        path = _safe_path(row.get("path"), f"inputs[{index}].path")
        if path in seen:
            raise VerificationError("duplicate input path")
        seen.add(path)
        input_paths.append(path)
        input_shas.append(sha256(raw))
    if contract["input_paths"] != input_paths:
        raise VerificationError("contract input_paths disagree with ordered manifest inputs")

    output = manifest["output"]
    if not isinstance(output, dict) or set(output) != {
        "path", "artifact_kind", "schema_version", "content_sha256", "byte_count", "source_id"
    }:
        raise VerificationError("output fields are not exact")
    output_path = _safe_path(output["path"], "output.path")
    kind = output["artifact_kind"]
    schema = output["schema_version"]
    if contract["artifact_kind"] != kind or contract["output_schema_version"] != schema:
        raise VerificationError("contract artifact kind/schema disagree with output")
    output_oid, raw = _blob(repo, output_commit, output_path)
    if sha256(raw) != _checked_sha(output["content_sha256"], "output.content_sha256"):
        raise VerificationError("committed output content hash mismatch")
    if not isinstance(output["byte_count"], int) or isinstance(output["byte_count"], bool) or len(raw) != output["byte_count"]:
        raise VerificationError("committed output byte_count mismatch")
    try:
        old_oid, _ = _blob(repo, basis, output_path)
    except VerificationError:
        old_oid = None
    if old_oid == output_oid:
        raise VerificationError("output blob did not originate in the output commit")
    validate_identity_artifact(raw, kind, schema)

    replay_a = _replay_once(repo, basis, contract, producer_path)
    replay_b = _replay_once(repo, basis, contract, producer_path)
    if replay_a != replay_b or replay_a != raw:
        raise VerificationError("deterministic exact replay did not reproduce committed bytes")

    source_id = output["source_id"]
    if not isinstance(source_id, str) or not source_id:
        raise VerificationError("output.source_id must be nonempty")
    locator = f"git-blob:{output_oid}:{output_path}"
    role = "machine-generated-git-blob"
    identity = unit_identity_sha256(source_id, "git", locator, role, sha256(raw), schema)
    proof = {
        "schema_version": RECEIPT_SCHEMA,
        "verification_status": "VERIFIED",
        "unit_identity_sha256": identity,
        "source_id": source_id,
        "source_kind": "git",
        "locator": locator,
        "role": role,
        "content_sha256": sha256(raw),
        "content_schema": schema,
        "artifact_kind": kind,
        "repository": str(repo),
        "basis_commit": basis,
        "output_commit": output_commit,
        "producer_sha256": manifest["producer"]["sha256"],
        "contract_sha256": manifest["contract"]["sha256"],
        "input_sha256s": input_shas,
        "historical_inputs_predate_output": True,
        "bounded_safe_surface_verified": True,
        "deterministic_exact_replay_verified": True,
        "locator_specific_proof": True,
        "global_content_hash_allowlist": False,
        "interactive_delivery": False,
    }
    proof["receipt_sha256"] = sha256(canonical_json(proof))
    return proof


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, VerificationError, subprocess.SubprocessError) as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
