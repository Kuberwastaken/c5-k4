#!/usr/bin/env python3
"""Authenticate the Method v1.5 checkpoint chain from public Git ancestry.

This verifier does not accept a caller-selected previous receipt.  It derives
the unique previous receipt, its blob, and its introducing commit by walking
the exact publication ref back to P1T.  Every publication commit must be a
single-parent, add-only commit with the frozen path set.  Consequently the
next normal push can only append to the public tip proved here.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Sequence


PUBLIC_REPOSITORY = "https://github.com/Kuberwastaken/c5-k4.git"
PUBLICATION_BRANCH = "method-v1.5-checkpoints"
PUBLICATION_REF = f"refs/remotes/origin/{PUBLICATION_BRANCH}"
U1_PATH = "u1/chronology-receipt.json"
PUBLICATION_FILES = (
    "publication-manifest.json", "quota-certificate.json", "receipt.json",
)
RECEIPT_SCHEMA = "c5k4-method-v1.5-chronology-receipt-1.0"
PROOF_SCHEMA = "c5k4-method-v1.5-public-checkpoint-chain-proof-1.0"
TERMINAL_STATUSES = {
    "QUOTA_PASS_U2", "TERMINAL_QUOTA_DEFICIT", "INVALID_CHRONOLOGY_CAPTURE",
}
NONTERMINAL_STATUSES = {"QUOTA_FAIL", "MISSED"}
OID_RE = re.compile(r"^[0-9a-f]{40}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
LABEL_RE = re.compile(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})T00-17-00Z$")
LAST_CHECKPOINT = "2027-08-15T00:17:00Z"
SAFE_ENV = {
    "PATH": "/usr/bin:/bin", "HOME": "/nonexistent-c5k4-v15-public-chain",
    "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1",
}
SAFE_CONFIG = (
    "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never",
    "-c", "credential.helper=", "-c", "core.fsmonitor=false",
)


class PublicChainError(ValueError):
    """The public checkpoint ref does not prove the frozen append-only chain."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def proof_digest(proof: dict[str, Any]) -> str:
    unsigned = dict(proof)
    unsigned.pop("proof_sha256", None)
    return sha256(canonical_json(unsigned))


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PublicChainError(f"{label} must be an RFC3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PublicChainError(f"invalid {label}") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise PublicChainError(f"{label} must be UTC")
    return parsed


def format_time(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def first_tick_after(value: str) -> datetime:
    completed = parse_time(value, "U1 completion")
    tick = completed.replace(hour=0, minute=17, second=0, microsecond=0)
    return tick if tick > completed else tick + timedelta(days=1)


def _run(repo: Path, args: Sequence[str], *, check: bool = True) -> bytes:
    result = subprocess.run(
        ["/usr/bin/git", *SAFE_CONFIG, "-C", str(repo), *args], env=SAFE_ENV,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise PublicChainError(f"Git failed ({' '.join(args)}): {detail}")
    return result.stdout if result.returncode == 0 else b""


def exact_oid(value: Any, label: str) -> str:
    if not isinstance(value, str) or OID_RE.fullmatch(value) is None:
        raise PublicChainError(f"{label} must be an exact lowercase Git object ID")
    return value


def commit_blob(repo: Path, commit: str, path: str) -> bytes:
    if PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts:
        raise PublicChainError("non-normalized committed path")
    return _run(repo, ("show", f"{commit}:{path}"))


def json_blob(repo: Path, commit: str, path: str) -> tuple[dict[str, Any], bytes]:
    raw = commit_blob(repo, commit, path)
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicChainError(f"{path} at {commit} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PublicChainError(f"{path} at {commit} is not one JSON object")
    return value, raw


def parents(repo: Path, commit: str) -> list[str]:
    return _run(repo, ("show", "-s", "--format=%P", commit)).decode().split()


def changes(repo: Path, commit: str) -> list[tuple[str, str]]:
    lines = _run(
        repo, ("diff-tree", "--no-commit-id", "--name-status", "-r", commit)
    ).decode().splitlines()
    result: list[tuple[str, str]] = []
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 2:
            raise PublicChainError(f"rename/copy or malformed change in {commit}")
        result.append((fields[0], fields[1]))
    return result


def _checkpoint_path(scheduled: str) -> str:
    parsed = parse_time(scheduled, "checkpoint schedule")
    if (parsed.hour, parsed.minute, parsed.second, parsed.microsecond) != (0, 17, 0, 0):
        raise PublicChainError("checkpoint is not an exact 00:17:00Z tick")
    return "checkpoints/" + scheduled.replace(":", "-")


def _validate_u1(value: dict[str, Any], p1t_commit: str) -> str:
    if value.get("schema") != RECEIPT_SCHEMA or value.get("artifact_kind") != "U1_CHRONOLOGY_RECEIPT":
        raise PublicChainError("genesis artifact is not the frozen U1 receipt type")
    if value.get("protocol_version") != "1.5" or value.get("status") != "VALID_U1":
        raise PublicChainError("U1 receipt version/status is invalid")
    if value.get("p1", {}).get("p1t_commit") != p1t_commit:
        raise PublicChainError("U1 receipt is not bound to the genesis parent P1T")
    completed = value.get("upstream", {}).get("capture_completed_at_utc")
    parse_time(completed, "U1 completion")
    return completed


def verify_chain(
    repository: Path, publication_ref: str, p1t_commit: str,
) -> dict[str, Any]:
    """Prove the exact chain currently reachable from the public tracking ref."""
    repo = repository.resolve()
    if not repo.is_dir():
        raise PublicChainError("public Git object store is absent")
    p1t_commit = exact_oid(p1t_commit, "P1T commit")
    if publication_ref != PUBLICATION_REF:
        raise PublicChainError("only the frozen public tracking ref is admissible")
    origin = _run(repo, ("remote", "get-url", "origin")).decode().strip()
    if origin != PUBLIC_REPOSITORY:
        raise PublicChainError("origin is not the frozen public c5-k4 repository")
    if (repo / ".git/shallow").exists() or (repo / "shallow").exists():
        raise PublicChainError("shallow public ancestry cannot prove the checkpoint chain")
    tip = _run(repo, ("rev-parse", "--verify", publication_ref)).decode().strip()
    exact_oid(tip, "public publication tip")
    if _run(repo, ("rev-parse", "--verify", p1t_commit)).decode().strip() != p1t_commit:
        raise PublicChainError("P1T is absent from the authenticated object store")

    reverse: list[str] = []
    cursor = tip
    seen: set[str] = set()
    while cursor != p1t_commit:
        if cursor in seen:
            raise PublicChainError("cycle in public ancestry")
        seen.add(cursor)
        commit_parents = parents(repo, cursor)
        if len(commit_parents) != 1:
            raise PublicChainError("every publication commit must have exactly one parent")
        reverse.append(cursor)
        cursor = commit_parents[0]
    commits = list(reversed(reverse))
    if not commits:
        raise PublicChainError("publication branch has no U1 genesis after P1T")

    genesis = commits[0]
    if changes(repo, genesis) != [("A", U1_PATH)]:
        raise PublicChainError("genesis must add only the frozen U1 receipt path")
    u1, u1_raw = json_blob(repo, genesis, U1_PATH)
    u1_completed = _validate_u1(u1, p1t_commit)
    expected_tick = first_tick_after(u1_completed)
    rows: list[dict[str, Any]] = []
    terminal = False
    for index, commit in enumerate(commits[1:], start=1):
        if terminal:
            raise PublicChainError("public chain continues after its first terminal checkpoint")
        expected_parent = commits[index - 1]
        if parents(repo, commit) != [expected_parent]:
            raise PublicChainError("checkpoint commit does not append to the prior public tip")
        changed = changes(repo, commit)
        if any(status != "A" for status, _ in changed):
            raise PublicChainError("checkpoint commits must be add-only")
        paths = sorted(path for _, path in changed)
        if len(paths) != 3:
            raise PublicChainError("checkpoint commit must add exactly three public artifacts")
        roots = {str(PurePosixPath(path).parent) for path in paths}
        if len(roots) != 1:
            raise PublicChainError("checkpoint artifacts do not share one destination")
        root = roots.pop()
        if sorted(PurePosixPath(path).name for path in paths) != sorted(PUBLICATION_FILES):
            raise PublicChainError("checkpoint commit has an unfrozen artifact set")
        receipt_path = f"{root}/receipt.json"
        receipt, receipt_raw = json_blob(repo, commit, receipt_path)
        json_blob(repo, commit, f"{root}/publication-manifest.json")
        certificate, _ = json_blob(repo, commit, f"{root}/quota-certificate.json")
        if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("artifact_kind") != "CHECKPOINT_RECEIPT":
            raise PublicChainError("public receipt has the wrong frozen type")
        ordinal = receipt.get("checkpoint_ordinal")
        if ordinal != index:
            raise PublicChainError("checkpoint ordinals are not contiguous from one")
        scheduled = receipt.get("scheduled_for_utc")
        if parse_time(scheduled, "checkpoint schedule") != expected_tick:
            raise PublicChainError("checkpoint dates are duplicated, skipped, or reordered")
        expected_root = _checkpoint_path(scheduled)
        if root != expected_root or LABEL_RE.fullmatch(root.removeprefix("checkpoints/")) is None:
            raise PublicChainError("checkpoint path does not encode its exact scheduled tick")
        status = receipt.get("status")
        if status not in NONTERMINAL_STATUSES | TERMINAL_STATUSES:
            raise PublicChainError("checkpoint status is invalid")
        if parse_time(scheduled, "checkpoint schedule") > parse_time(LAST_CHECKPOINT, "hard horizon"):
            raise PublicChainError("checkpoint is after the frozen hard horizon")
        if scheduled == LAST_CHECKPOINT and status not in TERMINAL_STATUSES:
            raise PublicChainError("hard-horizon checkpoint must terminate")
        aggregate_status = certificate.get("aggregates", {}).get("status")
        if status == "QUOTA_PASS_U2" and aggregate_status != "PASS":
            raise PublicChainError("PASS receipt is not supported by its quota certificate")
        if status in {"QUOTA_FAIL", "TERMINAL_QUOTA_DEFICIT"} and aggregate_status != "FAIL":
            raise PublicChainError("FAIL receipt is not supported by its quota certificate")
        prior = receipt.get("basis", {}).get("previous_checkpoint")
        if index == 1:
            if prior is not None:
                raise PublicChainError("first checkpoint falsely claims a predecessor")
        else:
            previous = rows[-1]
            expected_prior = {
                "path": previous["receipt_path"],
                "sha256": previous["receipt_blob_sha256"],
                "commit": previous["commit"],
                "checkpoint_ordinal": previous["ordinal"],
                "scheduled_for_utc": previous["scheduled_for_utc"],
                "status": previous["status"],
            }
            if prior != expected_prior:
                raise PublicChainError("receipt predecessor binding is not the public prior blob/commit")
        row = {
            "ordinal": ordinal, "scheduled_for_utc": scheduled, "status": status,
            "commit": commit, "parent_commit": expected_parent,
            "receipt_path": receipt_path, "receipt_blob_sha256": sha256(receipt_raw),
        }
        rows.append(row)
        terminal = status in TERMINAL_STATUSES
        expected_tick += timedelta(days=1)

    previous = rows[-1] if rows else None
    proof = {
        "schema": PROOF_SCHEMA,
        "repository": PUBLIC_REPOSITORY,
        "ref": publication_ref,
        "p1t_commit": p1t_commit,
        "public_tip_commit": tip,
        "genesis": {
            "commit": genesis, "parent_commit": p1t_commit, "u1_path": U1_PATH,
            "u1_blob_sha256": sha256(u1_raw),
        },
        "checkpoint_count": len(rows),
        "checkpoints": rows,
        "previous_checkpoint": previous,
        "next_checkpoint": None if terminal else {
            "ordinal": len(rows) + 1,
            "scheduled_for_utc": format_time(expected_tick),
            "required_parent_commit": tip,
        },
        "terminal": terminal,
        "normal_push_must_use_lease_tip": tip,
    }
    proof["proof_sha256"] = proof_digest(proof)
    return proof


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise PublicChainError("proof output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--ref", default=PUBLICATION_REF)
    parser.add_argument("--p1t-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        proof = verify_chain(args.repository, args.ref, args.p1t_commit)
        write_json(args.output, proof)
    except (OSError, PublicChainError) as exc:
        print(f"INVALID_PUBLIC_CHECKPOINT_CHAIN: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
