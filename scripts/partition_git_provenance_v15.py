#!/usr/bin/env python3
"""Partition Git evidence into vendor custody, semantic deltas, and unknowns.

This module never promotes bytes merely because they equal vendor bytes.  Only
objects at the exact authenticated vendor base commit/path receive immutable
custody.  All later commits and overlays are excluding semantic evidence;
operations capable of obscuring provenance fail closed as UNKNOWN unless an
exact merge attestation was frozen in advance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

import build_benchmark_v15_vendor_bases as vendor


SCHEMA = "c5k4-method-v1.5-git-provenance-partition-1.0"
CUSTODY_PROOF_SCHEMA = "c5k4-method-v1.5-git-custody-locator-proof-1.0"
IMMUTABLE = "IMMUTABLE_SOURCE_CUSTODY"
SEMANTIC = "SEMANTIC_EXPOSURE"
UNKNOWN = "UNKNOWN"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
UNIT_IDENTITY_FIELDS = (
    "source_id", "source_kind", "locator", "role", "content_sha256", "content_schema",
)


class PartitionError(ValueError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *args: str, check: bool = True, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    command = list(args)
    if command and command[0] in {"diff", "diff-tree", "show"}:
        command[1:1] = ["--no-ext-diff", "--no-textconv"]
    return subprocess.run(
        ["/usr/bin/git", *vendor.SAFE_CONFIG, "-C", str(repo), *command], input=input_bytes,
        check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=vendor.SAFE_ENV,
    )


def audit_source_repository(repo: Path) -> None:
    """Reject mechanisms that can substitute or lazily obtain Git objects."""

    if not repo.is_dir() or git(repo, "rev-parse", "--git-dir", check=False).returncode != 0:
        raise PartitionError("source is not a Git repository")
    for relative, label in (("shallow", "shallow"), ("objects/info/alternates", "alternates"), ("info/grafts", "grafts")):
        raw = git(repo, "rev-parse", "--git-path", relative).stdout.decode().strip()
        path = Path(raw) if Path(raw).is_absolute() else repo / raw
        if os.path.lexists(path):
            raise PartitionError(f"source repository uses forbidden {label} state")
    refs = git(repo, "for-each-ref", "refs/replace", "--format=%(refname)").stdout
    if refs.strip():
        raise PartitionError("source repository has forbidden replace refs")
    config = git(repo, "config", "--local", "--null", "--list").stdout.decode("utf-8", "surrogateescape")
    keys = [entry.split("\n", 1)[0].casefold() for entry in config.split("\0") if entry]
    forbidden = re.compile(
        r"(?:extensions\.partialclone|remote\..*\.promisor|include\.path|includeif\..*\.path|"
        r"core\.replacerefs|diff\.external|diff\..*\.(?:command|textconv)|filter\..*\.(?:process|smudge|clean))"
    )
    if any(forbidden.fullmatch(key) for key in keys):
        raise PartitionError("source repository has forbidden executable/promisor configuration")
    pack_raw = git(repo, "rev-parse", "--git-path", "objects/pack").stdout.decode().strip()
    pack = Path(pack_raw) if Path(pack_raw).is_absolute() else repo / pack_raw
    if pack.is_dir() and any(item.name.endswith(".promisor") for item in pack.iterdir()):
        raise PartitionError("source repository has promisor object markers")


def _unit(source_id: str, locator: str, role: str, content_sha256: str, cls: str, reason: str, **extra: Any) -> dict[str, Any]:
    value = {
        "source_id": source_id,
        "source_kind": "git_provenance_partition",
        "locator": locator,
        "role": role,
        "content_sha256": content_sha256,
        "content_schema": None,
        "provenance_class": cls,
        "classification_reason": reason,
        **extra,
    }
    value["unit_identity_sha256"] = sha256(canonical_json({key: value[key] for key in UNIT_IDENTITY_FIELDS}))
    return value


def custody_locator_proof(unit: dict[str, Any], vendor_receipt: dict[str, Any]) -> dict[str, Any]:
    """Bind one exact partitioned base blob to its authenticated vendor receipt."""

    vendor_repo = Path(str(vendor_receipt.get("repository_path", "")))
    vendor.validate_receipt(vendor_receipt, vendor_repo)
    expected_identity = sha256(canonical_json({key: unit.get(key) for key in UNIT_IDENTITY_FIELDS}))
    if unit.get("unit_identity_sha256") != expected_identity:
        raise PartitionError("custody unit identity does not replay")
    if (
        unit.get("source_kind") != "git_provenance_partition"
        or unit.get("role") != "vendor-base-blob"
        or unit.get("provenance_class") != IMMUTABLE
        or unit.get("classification_reason") != "EXACT_PATH_AND_BLOB_AT_AUTHENTICATED_VENDOR_BASE"
    ):
        raise PartitionError("custody proof requires one exact immutable vendor-base blob")
    match = re.fullmatch(r"git-blob:([0-9a-f]{40}):(.+)", str(unit.get("locator", "")))
    if match is None or match.groups() != (unit.get("git_blob"), unit.get("path")):
        raise PartitionError("custody unit locator does not bind its blob and path")
    audit = vendor_receipt["audit"]
    if (
        unit.get("vendor_base_commit") != audit["commit"]
        or unit.get("vendor_base_tree") != audit["root_tree"]
        or unit.get("acquisition_receipt_sha256") != vendor_receipt["receipt_sha256"]
    ):
        raise PartitionError("custody unit does not bind the authenticated vendor base")
    entries = dict(tree_blobs(vendor_repo, audit["commit"]))
    if entries.get(unit["path"]) != unit["git_blob"]:
        raise PartitionError("custody path/blob is absent from the authenticated vendor tree")
    if blob_sha256(vendor_repo, unit["git_blob"]) != unit["content_sha256"]:
        raise PartitionError("custody blob content digest does not replay")
    binding = {key: unit.get(key) for key in UNIT_IDENTITY_FIELDS}
    binding.update({
        "unit_identity_sha256": expected_identity,
        "git_blob": unit["git_blob"],
        "path": unit["path"],
        "vendor_base_commit": unit["vendor_base_commit"],
        "vendor_base_tree": unit["vendor_base_tree"],
        "acquisition_receipt_sha256": unit["acquisition_receipt_sha256"],
        "locator_specific": True,
    })
    proof: dict[str, Any] = {
        "schema": CUSTODY_PROOF_SCHEMA,
        "status": "VERIFIED_IMMUTABLE_SOURCE_CUSTODY",
        "locator_binding": binding,
        "vendor_receipt": vendor_receipt,
        "verification": {
            "vendor_receipt_live_replay": True,
            "base_commit_and_tree_match": True,
            "path_and_blob_match": True,
            "blob_content_sha256_match": True,
            "no_semantic_rendering_evidenced": True,
        },
    }
    proof["proof_sha256"] = sha256(canonical_json(proof))
    return proof


def tree_blobs(repo: Path, commit: str) -> list[tuple[str, str]]:
    raw = git(repo, "ls-tree", "-r", "-z", "--full-tree", commit).stdout
    rows: list[tuple[str, str]] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, path_raw = record.split(b"\t", 1)
        _mode, kind, oid = metadata.decode("ascii").split(" ")
        if kind != "blob":
            raise PartitionError(f"vendor tree contains unsupported {kind} entry")
        rows.append((path_raw.decode("utf-8", "surrogateescape"), oid))
    return sorted(rows, key=lambda row: row[0].encode("utf-8", "surrogateescape"))


def blob_sha256(repo: Path, oid: str) -> str:
    if not HEX40.fullmatch(oid):
        raise PartitionError("invalid Git blob identity")
    return sha256(git(repo, "cat-file", "blob", oid).stdout)


def parse_name_status(raw: bytes) -> list[tuple[str, tuple[str, ...]]]:
    fields = raw.split(b"\0")
    if fields and not fields[-1]:
        fields.pop()
    rows: list[tuple[str, tuple[str, ...]]] = []
    index = 0
    while index < len(fields):
        status = fields[index].decode("ascii")
        index += 1
        path_count = 2 if status.startswith(("R", "C")) else 1
        if index + path_count > len(fields):
            raise PartitionError("malformed Git name-status stream")
        paths = tuple(field.decode("utf-8", "surrogateescape") for field in fields[index:index + path_count])
        rows.append((status, paths))
        index += path_count
    return rows


def _commit_parents(repo: Path, commit: str) -> list[str]:
    fields = git(repo, "show", "-s", "--format=%P", commit).stdout.decode().strip().split()
    if not all(HEX40.fullmatch(parent) for parent in fields):
        raise PartitionError("invalid commit parent identity")
    return fields


def merge_attestation_sha256(commit: str, parents: list[str]) -> str:
    return sha256(canonical_json({"commit": commit, "parents": parents}))


def partition_repository(
    repo: Path,
    ref: str,
    vendor_receipt: dict[str, Any],
    *,
    source_id: str,
    merge_attestations: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    vendor_repo = Path(vendor_receipt.get("repository_path", ""))
    vendor.validate_receipt(vendor_receipt, vendor_repo)
    audit_source_repository(repo)
    head = git(repo, "rev-parse", f"{ref}^{{commit}}").stdout.decode().strip()
    base = str(vendor_receipt["audit"]["commit"])
    if git(repo, "cat-file", "-e", f"{base}^{{commit}}", check=False).returncode != 0:
        raise PartitionError("authenticated vendor base is absent from source repository")
    source_base_tree = git(repo, "rev-parse", f"{base}^{{tree}}").stdout.decode().strip()
    if source_base_tree != vendor_receipt["audit"]["root_tree"]:
        raise PartitionError("source repository vendor base tree differs from receipt")
    if git(repo, "merge-base", "--is-ancestor", base, head, check=False).returncode != 0:
        raise PartitionError("source ref does not descend from authenticated vendor base")

    receipt_sha = str(vendor_receipt["receipt_sha256"])
    units: list[dict[str, Any]] = []
    for path, oid in tree_blobs(vendor_repo, base):
        units.append(_unit(
            source_id, f"git-blob:{oid}:{path}", "vendor-base-blob", blob_sha256(vendor_repo, oid),
            IMMUTABLE, "EXACT_PATH_AND_BLOB_AT_AUTHENTICATED_VENDOR_BASE",
            git_blob=oid, path=path, vendor_base_commit=base,
            vendor_base_tree=vendor_receipt["audit"]["root_tree"], acquisition_receipt_sha256=receipt_sha,
        ))

    attestations = merge_attestations or {}
    commits = git(repo, "rev-list", "--reverse", "--topo-order", f"{base}..{head}").stdout.decode().splitlines()
    for commit in commits:
        parents = _commit_parents(repo, commit)
        merge = len(parents) > 1
        attestation = attestations.get(commit)
        merge_ok = (
            not merge or isinstance(attestation, dict)
            and attestation.get("commit") == commit
            and attestation.get("parents") == parents
            and isinstance(attestation.get("attestation_sha256"), str)
            and attestation["attestation_sha256"] == merge_attestation_sha256(commit, parents)
        )
        cls = SEMANTIC if merge_ok else UNKNOWN
        reason = "NON_VENDOR_COMMIT" if not merge else "ATTESTED_NON_VENDOR_MERGE" if merge_ok else "UNATTESTED_MERGE"
        message = git(repo, "show", "-s", "--format=%B", commit).stdout
        units.append(_unit(source_id, f"git-commit:{commit}:message", "user-commit-message", sha256(message), cls, reason, commit=commit, parents=parents))
        if not parents:
            raise PartitionError("non-vendor root commit is not attributable")
        raw = git(repo, "diff-tree", "-r", "--name-status", "-z", "-M", "-C", "--find-copies-harder", "--no-commit-id", parents[0], commit).stdout
        for status, paths in parse_name_status(raw):
            opaque_operation = status.startswith(("R", "C"))
            delta_cls = UNKNOWN if opaque_operation or not merge_ok else SEMANTIC
            delta_reason = (
                "RENAME_OR_COPY_CANNOT_INHERIT_VENDOR_CUSTODY" if opaque_operation
                else "UNATTESTED_MERGE_DELTA" if not merge_ok
                else "NON_VENDOR_PATH_DELTA"
            )
            units.append(_unit(
                source_id, f"git-delta:{commit}:{status}:" + "->".join(paths), "user-path-delta",
                sha256(canonical_json({"commit": commit, "status": status, "paths": paths})),
                delta_cls, delta_reason, commit=commit, status=status, paths=list(paths),
            ))

    unmerged = git(repo, "ls-files", "-u", "-z").stdout
    if unmerged:
        raise PartitionError("unmerged index entries make overlay provenance unknown")
    overlay_fields = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split(b"\0")
    if overlay_fields and not overlay_fields[-1]:
        overlay_fields.pop()
    overlay_index = 0
    while overlay_index < len(overlay_fields):
        record = overlay_fields[overlay_index]
        overlay_index += 1
        if len(record) < 4:
            raise PartitionError("malformed worktree overlay record")
        status = record[:2].decode("ascii", "replace")
        path = record[3:].decode("utf-8", "surrogateescape")
        old_path = None
        opaque_operation = "R" in status or "C" in status
        if opaque_operation:
            if overlay_index >= len(overlay_fields):
                raise PartitionError("rename/copy overlay is missing its source path")
            old_path = overlay_fields[overlay_index].decode("utf-8", "surrogateescape")
            overlay_index += 1
        units.append(_unit(
            source_id, f"worktree-overlay:{status}:{path}", "worktree-overlay",
            sha256(canonical_json({"status": status, "path": path, "old_path": old_path})),
            UNKNOWN if opaque_operation else SEMANTIC,
            "RENAME_OR_COPY_OVERLAY_PROVENANCE_UNKNOWN" if opaque_operation else "NON_VENDOR_WORKTREE_OR_INDEX_OVERLAY",
            status=status, path=path, old_path=old_path,
        ))

    counts = {name: sum(unit["provenance_class"] == name for unit in units) for name in (IMMUTABLE, SEMANTIC, UNKNOWN)}
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "source_id": source_id,
        "repository_path": str(repo.resolve()),
        "ref": ref,
        "head_commit": head,
        "vendor_base_commit": base,
        "vendor_receipt_sha256": receipt_sha,
        "units": units,
        "counts": counts,
        "fail_closed": counts[UNKNOWN] > 0,
    }
    result["partition_sha256"] = sha256(canonical_json(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--vendor-receipt", required=True, type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--merge-attestations", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if os.path.lexists(args.output):
        raise PartitionError("partition output must be previously absent")
    receipt = json.loads(args.vendor_receipt.read_bytes())
    attestations = json.loads(args.merge_attestations.read_bytes()) if args.merge_attestations else None
    result = partition_repository(args.repository, args.ref, receipt, source_id=args.source_id, merge_attestations=attestations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(result, sort_keys=True, indent=2).encode() + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
