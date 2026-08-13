#!/usr/bin/env python3
"""Acquire and audit a Method v1.5 immutable vendor base.

The acquisition is deliberately narrower than a clone: initialize a previously
absent bare SHA-1 repository, perform one atomic no-refmap fetch into one
namespaced ref, and emit a content-addressed receipt.  The receipt authenticates
custody only.  It is not evidence that any source text was shown to a person or
language model.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable


SCHEMA = "c5k4-method-v1.5-vendor-base-receipt-1.0"
HEX40 = re.compile(r"[0-9a-f]{40}")
SAFE_ENV = {
    "HOME": "/nonexistent",
    "LANG": "C",
    "LC_ALL": "C",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_NO_LAZY_FETCH": "1",
    "GIT_NO_REPLACE_OBJECTS": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "/bin/false",
    "SSH_ASKPASS": "/bin/false",
}
SAFE_CONFIG = (
    "-c", "core.hooksPath=/dev/null",
    "-c", "core.fsmonitor=false",
    "-c", "diff.external=",
    "-c", "diff.trustExitCode=false",
    "-c", "filter.lfs.process=",
    "-c", "filter.lfs.smudge=",
    "-c", "filter.lfs.required=false",
)


class VendorBaseError(ValueError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def self_digest(receipt: dict[str, Any]) -> str:
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    return sha256(canonical_json(unsigned))


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["/usr/bin/git", *SAFE_CONFIG, "-C", str(repo), *args], check=check,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SAFE_ENV,
    )


def fetch_command(repository: Path, remote: str, remote_ref: str, destination_ref: str) -> list[str]:
    if not remote_ref.startswith("refs/heads/"):
        raise VendorBaseError("vendor remote ref must be a full heads ref")
    if not destination_ref.startswith("refs/c5k4-benchmark/v1.5/vendor/"):
        raise VendorBaseError("destination ref must use the frozen v1.5 vendor namespace")
    return [
        "/usr/bin/git", *SAFE_CONFIG,
        "-c", "protocol.version=2", "-c", "http.followRedirects=false",
        "-c", "fetch.fsckObjects=true", "-c", "transfer.fsckObjects=true",
        "-C", str(repository), "fetch", "--porcelain", "--atomic", "--no-tags",
        "--no-recurse-submodules", "--no-write-fetch-head", "--no-auto-maintenance",
        "--no-auto-gc", "--no-write-commit-graph", "--no-progress", "--refmap=",
        remote, f"{remote_ref}:{destination_ref}",
    ]


def _git_path(repository: Path, relative: str) -> Path:
    value = git(repository, "rev-parse", "--git-path", relative).stdout.decode().strip()
    path = Path(value)
    return path if path.is_absolute() else repository / path


def audit_repository(repository: Path, destination_ref: str) -> dict[str, Any]:
    """Prove that resolution depends only on this bare object store."""

    if not repository.is_dir():
        raise VendorBaseError("vendor repository is absent")
    if git(repository, "rev-parse", "--is-bare-repository").stdout.strip() != b"true":
        raise VendorBaseError("vendor repository is not bare")
    object_format = git(repository, "rev-parse", "--show-object-format").stdout.decode().strip()
    if object_format != "sha1":
        raise VendorBaseError("vendor repository must use SHA-1 object identities")

    forbidden_paths = ("FETCH_HEAD", "shallow", "objects/info/alternates", "info/grafts")
    present = [name for name in forbidden_paths if os.path.lexists(_git_path(repository, name))]
    if present:
        raise VendorBaseError("forbidden repository state: " + ", ".join(present))
    pack = _git_path(repository, "objects/pack")
    if pack.is_dir() and any(item.name.endswith(".promisor") for item in pack.iterdir()):
        raise VendorBaseError("forbidden promisor object marker")

    config = git(repository, "config", "--local", "--null", "--list").stdout
    entries = [entry for entry in config.decode("utf-8", "surrogateescape").split("\0") if entry]
    keys = [entry.split("\n", 1)[0].casefold() for entry in entries]
    allowed = {"core.repositoryformatversion", "core.filemode", "core.bare", "extensions.objectformat"}
    unexpected = sorted(key for key in keys if key not in allowed)
    if unexpected:
        raise VendorBaseError("unexpected local Git configuration: " + ", ".join(unexpected))

    refs = git(repository, "for-each-ref", "--format=%(refname)%00%(objectname)%00%(objecttype)").stdout
    rows = [row.split("\0") for row in refs.decode().splitlines() if row]
    if len(rows) != 1 or rows[0][0] != destination_ref or rows[0][2] != "commit":
        raise VendorBaseError("vendor repository must contain exactly its destination commit ref")
    if any(row[0].startswith("refs/replace/") for row in rows):
        raise VendorBaseError("replace refs are forbidden")
    commit = rows[0][1]
    if not HEX40.fullmatch(commit):
        raise VendorBaseError("resolved vendor commit is not a SHA-1 commit")
    tree = git(repository, "rev-parse", f"{commit}^{{tree}}").stdout.decode().strip()
    fsck = git(repository, "fsck", "--strict", "--connectivity-only", "--no-dangling", commit, check=False)
    if fsck.returncode != 0:
        raise VendorBaseError("vendor object connectivity/fsck failed")
    return {
        "object_format": object_format,
        "commit": commit,
        "root_tree": tree,
        "refs": [{"ref": rows[0][0], "object_id": commit, "object_type": "commit"}],
        "connectivity_fsck_stdout_sha256": sha256(fsck.stdout),
        "connectivity_fsck_stderr_sha256": sha256(fsck.stderr),
    }


def acquire(
    repository: Path,
    remote: str,
    remote_ref: str,
    destination_ref: str,
    *,
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    acquired_at_utc: str | None = None,
) -> dict[str, Any]:
    """Execute the one-shot acquisition.  A failed attempt is never reused."""

    if os.path.lexists(repository):
        raise VendorBaseError("vendor repository path must be previously absent")
    repository.parent.mkdir(parents=True, exist_ok=True)
    init = ["/usr/bin/git", *SAFE_CONFIG, "init", "--bare", "--quiet", "--object-format=sha1", str(repository)]
    runner(init, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SAFE_ENV)
    command = fetch_command(repository, remote, remote_ref, destination_ref)
    fetched = runner(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SAFE_ENV)
    audit = audit_repository(repository, destination_ref)
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "AUTHENTICATED_IMMUTABLE_SOURCE_CUSTODY",
        "acquired_at_utc": acquired_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repository_path": str(repository.resolve()),
        "fresh_repository": True,
        "bare_repository": True,
        "remote": remote,
        "remote_ref": remote_ref,
        "destination_ref": destination_ref,
        "fetch_command": command,
        "fetch_stdout_sha256": sha256(fetched.stdout),
        "fetch_stderr_sha256": sha256(fetched.stderr),
        "audit": audit,
        "retry_count": 0,
    }
    receipt["receipt_sha256"] = self_digest(receipt)
    return receipt


def validate_receipt(receipt: dict[str, Any], repository: Path | None = None) -> None:
    if receipt.get("schema") != SCHEMA or receipt.get("status") != "AUTHENTICATED_IMMUTABLE_SOURCE_CUSTODY":
        raise VendorBaseError("invalid vendor receipt schema or status")
    if receipt.get("receipt_sha256") != self_digest(receipt):
        raise VendorBaseError("vendor receipt self digest mismatch")
    if receipt.get("fresh_repository") is not True or receipt.get("bare_repository") is not True or receipt.get("retry_count") != 0:
        raise VendorBaseError("vendor receipt does not attest one fresh bare attempt")
    path = repository or Path(str(receipt.get("repository_path", "")))
    if str(path.resolve()) != receipt.get("repository_path"):
        raise VendorBaseError("vendor receipt repository path mismatch")
    expected_command = fetch_command(
        path, str(receipt.get("remote", "")), str(receipt.get("remote_ref", "")),
        str(receipt.get("destination_ref", "")),
    )
    if receipt.get("fetch_command") != expected_command:
        raise VendorBaseError("vendor receipt fetch command is not canonical")
    audited = audit_repository(path, str(receipt.get("destination_ref", "")))
    if audited != receipt.get("audit"):
        raise VendorBaseError("live vendor repository does not match receipt")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--remote", required=True)
    parser.add_argument("--remote-ref", required=True)
    parser.add_argument("--destination-ref", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if os.path.lexists(args.output):
        raise VendorBaseError("receipt output must be previously absent")
    receipt = acquire(args.repository, args.remote, args.remote_ref, args.destination_ref)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(receipt, sort_keys=True, indent=2).encode() + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
