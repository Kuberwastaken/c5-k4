#!/usr/bin/env python3
"""Strict, dependency-free observer for one public Method v1.5 P1R draft commit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
P1T_PATH = "results/benchmark/v1.5-protocol/P1T.json"
P1R_PATH = "results/benchmark/v1.5-protocol/P1R.json"
OID = re.compile(r"^[0-9a-f]{40}$")


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
        raise ObserverError("P1R commit must be an exact lowercase object ID")
    parents = git("show", "-s", "--format=%P", commit).decode().split()
    if len(parents) != 1:
        raise ObserverError("P1R must have exactly one parent")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines() != [P1R_PATH]:
        raise ObserverError("P1R commit must change exactly the canonical P1R path")
    raw = git("show", f"{commit}:{P1R_PATH}")
    if (ROOT / P1R_PATH).read_bytes() != raw:
        raise ObserverError("checkout P1R bytes differ from exact commit bytes")
    value = strict(raw, "P1R")
    if set(value) != {"schema_version", "artifact_kind", "status", "protocol_version", "p1t", "p1t_commit", "observation", "activation_policy"}:
        raise ObserverError("P1R fields differ from the frozen closed draft shape")
    if (
        value["schema_version"] != "c5k4-method-v1.5-p1r-1.0" or value["artifact_kind"] != "P1R"
        or value["status"] != "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY"
        or value["protocol_version"] != "1.5"
    ):
        raise ObserverError("P1R draft identity/version/status mismatch")
    if value["p1t_commit"] != parents[0] or OID.fullmatch(str(value["p1t_commit"])) is None:
        raise ObserverError("P1R parent is not exact embedded P1T commit")
    expected_policy = {
        "structural_draft_only": True, "p1r_is_activation_boundary": False,
        "p1t_alone_is_activation_boundary": False, "full_exact_c_replay_required": True,
        "p1r_parent_must_be_exact_p1t": True, "allowed_p1r_changed_paths": [P1R_PATH],
        "public_p1r_ref_required": True,
    }
    if value["activation_policy"] != expected_policy:
        raise ObserverError("P1R draft falsely claims activation or has a changed topology policy")
    p1t_ref = value["p1t"]
    if not isinstance(p1t_ref, dict) or set(p1t_ref) != {"path", "sha256"} or p1t_ref["path"] != P1T_PATH:
        raise ObserverError("P1R P1T binding shape/path mismatch")
    p1t_raw = git("show", f"{parents[0]}:{P1T_PATH}")
    if hashlib.sha256(p1t_raw).hexdigest() != p1t_ref["sha256"]:
        raise ObserverError("P1R does not authenticate exact P1T bytes")
    p1t = strict(p1t_raw, "P1T")
    if p1t.get("artifact_kind") != "P1T" or p1t.get("protocol_version") != "1.5":
        raise ObserverError("authenticated parent is not Method v1.5 P1T")
    observation = value["observation"]
    p1t_binding = observation.get("p1t") if isinstance(observation, dict) else None
    if (
        not isinstance(p1t_binding, dict) or set(p1t_binding) != {"ref", "commit"}
        or not isinstance(p1t_binding.get("ref"), str) or not p1t_binding["ref"].startswith("refs/")
        or p1t_binding.get("commit") != parents[0]
    ):
        raise ObserverError("P1R internal observation does not bind exact P1T")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    try:
        validate(args.commit)
    except (OSError, ObserverError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
