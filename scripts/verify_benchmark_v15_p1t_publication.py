#!/usr/bin/env python3
"""Strict, dependency-free observer for one public Method v1.5 P1T commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
P1A_PATH = "results/benchmark/v1.5-protocol/P1A.json"
P1T_PATH = "results/benchmark/v1.5-protocol/P1T.json"
OID = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ObserverError(ValueError):
    pass


def git(*args: str) -> bytes:
    try:
        return subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(ROOT), *args],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"},
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise ObserverError("sanitized Git query failed") from exc


def pairs(rows: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in rows:
        if key in result:
            raise ObserverError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict(raw: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ObserverError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ObserverError(f"{label} must be an object")
    return value


def validate(commit: str) -> None:
    if OID.fullmatch(commit) is None or git("rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
        raise ObserverError("P1T commit must be an exact lowercase object ID")
    parents = git("show", "-s", "--format=%P", commit).decode().split()
    if len(parents) != 1:
        raise ObserverError("P1T must have exactly one parent")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines() != [P1T_PATH]:
        raise ObserverError("P1T commit must change exactly the canonical P1T path")
    raw = git("show", f"{commit}:{P1T_PATH}")
    if (ROOT / P1T_PATH).read_bytes() != raw:
        raise ObserverError("checkout P1T bytes differ from exact commit bytes")
    value = strict(raw, "P1T")
    if set(value) != {"schema_version", "artifact_kind", "protocol_version", "p1a", "p1a_commit", "p1a_published_at_utc", "attestation_policy"}:
        raise ObserverError("P1T fields differ from the frozen closed shape")
    if value["schema_version"] != "c5k4-method-v1.5-p1-1.0" or value["artifact_kind"] != "P1T" or value["protocol_version"] != "1.5":
        raise ObserverError("P1T identity/version mismatch")
    if value["p1a_commit"] != parents[0] or OID.fullmatch(str(value["p1a_commit"])) is None:
        raise ObserverError("P1T parent is not exact embedded P1A commit")
    policy = value["attestation_policy"]
    if policy != {"p1a_ancestor_required": True, "p1a_bytes_immutable": True, "allowed_p1t_changed_paths": [P1T_PATH]}:
        raise ObserverError("P1T topology policy mismatch")
    p1a_ref = value["p1a"]
    if not isinstance(p1a_ref, dict) or set(p1a_ref) != {"path", "sha256"} or p1a_ref["path"] != P1A_PATH or HEX64.fullmatch(str(p1a_ref["sha256"])) is None:
        raise ObserverError("P1T P1A binding shape/path mismatch")
    p1a_raw = git("show", f"{parents[0]}:{P1A_PATH}")
    if hashlib.sha256(p1a_raw).hexdigest() != p1a_ref["sha256"]:
        raise ObserverError("P1T does not authenticate exact P1A bytes")
    p1a = strict(p1a_raw, "P1A")
    if p1a.get("artifact_kind") != "P1A" or p1a.get("protocol_version") != "1.5" or p1a.get("authority") != "AUTHORITATIVE_P1":
        raise ObserverError("authenticated parent is not a Method v1.5 authoritative P1A")
    timestamp = value["p1a_published_at_utc"]
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise ObserverError("P1A publication timestamp is not UTC")
    try:
        datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError as exc:
        raise ObserverError("P1A publication timestamp is invalid") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    try:
        validate(args.commit)
    except (OSError, ObserverError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
