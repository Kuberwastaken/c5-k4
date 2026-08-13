#!/usr/bin/env python3
"""Discover and freeze Method v1.2 semantic-source boundaries without semantics.

Only filesystem names, Git/release metadata, and current-tree bytes needed for
hashing are read during discovery. Commit messages, transcript turns, release
bodies, and candidate semantics are never decoded, inspected, or emitted.
The production ``acquire`` command is unavailable until a P0 attestation is
locally valid and its P0T commit is advertised by the recorded public remote.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any, Iterable
import unicodedata


POLICY_SCHEMA = "c5k4-source-path-purpose-policy-1.2"
CONFIG_SCHEMA = "c5k4-semantic-sources-config-1.2"
PROTOTYPE_CONFIG_SCHEMA = CONFIG_SCHEMA + "-prototype"
P0_SCHEMA = "c5k4-method-v1.2-p0-1.0"
SNAPSHOT_SCHEMA = "c5k4-source-snapshot-S0-1.2"
HEX_COMMIT = re.compile(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
RFC3339_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
REF_PREFIXES = ("refs/",)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def pretty_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def content_address(value: dict[str, Any], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return sha256(canonical_json(unsigned))


def discovery_contract_sha256(
    projects_root: Path,
    ai_chats_repo: Path | None,
    session_mirror_specs: list[str],
    release_specs: list[str],
) -> str:
    """Freeze the complete source boundary before S0, including local roots."""

    return sha256(discovery_contract_bytes(projects_root, ai_chats_repo, session_mirror_specs, release_specs))


def discovery_contract_bytes(
    projects_root: Path,
    ai_chats_repo: Path | None,
    session_mirror_specs: list[str],
    release_specs: list[str],
) -> bytes:
    return canonical_json(
        {
            "tool": "build_benchmark_v12_source_snapshot.py/discover",
            "projects_root": str(projects_root.resolve()),
            "ai_chats_repo": None if ai_chats_repo is None else str(ai_chats_repo.resolve()),
            "session_mirror_specs": sorted(session_mirror_specs),
            "release_snapshot_specs": sorted(release_specs),
        }
    )


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value, raw


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("schema_version") != POLICY_SCHEMA:
        raise ValueError(f"policy schema_version must be {POLICY_SCHEMA!r}")
    if policy.get("default") != "EXCLUDE_UNKNOWN":
        raise ValueError("policy must fail closed with default EXCLUDE_UNKNOWN")
    rules = policy.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("policy rules must be a nonempty list")
    for field in ("required_session_mirror_ids", "required_release_snapshot_ids"):
        values = policy.get(field)
        if not isinstance(values, list) or not all(
            isinstance(value, str) and value for value in values
        ) or len(values) != len(set(values)):
            raise ValueError(f"policy {field} must be a unique string list")
    ids: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get("id"), str):
            raise ValueError("every policy rule needs a string id")
        if rule["id"] in ids:
            raise ValueError(f"duplicate policy rule {rule['id']!r}")
        ids.add(rule["id"])
        if rule.get("decision") not in {"INCLUDE_SEMANTIC", "EXCLUDE_NONRESEARCH"}:
            raise ValueError(f"policy rule {rule['id']!r} has invalid decision")
        if not isinstance(rule.get("purpose"), str) or not rule["purpose"]:
            raise ValueError(f"policy rule {rule['id']!r} needs a purpose")
        if rule.get("decision") == "INCLUDE_SEMANTIC" and rule.get("source_kind") not in {
            "git_history", "git_user_delta", "tree"
        }:
            raise ValueError(f"included policy rule {rule['id']!r} needs source_kind")
        try:
            re.compile(rule.get("relative_path_regex", ""))
        except re.error as exc:
            raise ValueError(f"policy rule {rule['id']!r} has invalid regex") from exc


def classify_path(relative: str, policy: dict[str, Any]) -> dict[str, Any]:
    matches = [
        rule
        for rule in policy["rules"]
        if re.fullmatch(rule["relative_path_regex"], relative)
    ]
    if len(matches) > 1:
        raise ValueError(f"path {relative!r} matches multiple frozen policy rules")
    if not matches:
        return {
            "decision": "EXCLUDE_UNKNOWN",
            "policy_rule_id": None,
            "purpose": "UNCLASSIFIED_PATH_FAILS_CLOSED",
        }
    rule = matches[0]
    return {
        "decision": rule["decision"],
        "policy_rule_id": rule["id"],
        "purpose": rule["purpose"],
        **({"source_kind": rule["source_kind"]} if "source_kind" in rule else {}),
    }


def discover_project_directories(root: Path) -> list[Path]:
    """Enumerate every immediate directory; none may vanish by repository type."""

    if not root.is_dir():
        raise FileNotFoundError(root)
    return sorted(
        (path for path in root.iterdir() if path.is_dir()),
        key=lambda path: path.name.encode(),
    )


def repository_tips(repo: Path) -> list[dict[str, str]]:
    rows = git(
        repo,
        "for-each-ref",
        "--format=%(refname)%00%(objectname)%00%(objecttype)",
        *REF_PREFIXES,
    ).decode("utf-8", "strict").splitlines()
    tips = []
    for row in rows:
        ref, object_id, object_type = row.split("\0")
        tips.append({"ref": ref, "object_id": object_id, "object_type": object_type})
    tips.sort(key=lambda row: row["ref"].encode())
    if not tips:
        head = git(repo, "rev-parse", "HEAD").decode().strip()
        tips = [{"ref": "HEAD", "object_id": head, "object_type": "commit"}]
    return tips


def object_set(repo: Path, commits: Iterable[str]) -> dict[str, Any]:
    """Hash reachable object identities/types/sizes without reading blob payloads."""

    commit_list = sorted(set(commits))
    object_ids = git(
        repo, "rev-list", "--objects", "--no-object-names", *commit_list
    ).decode().splitlines()
    object_ids = sorted(set(object_ids))
    checked = git(
        repo,
        "cat-file",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        input_bytes=(("\n".join(object_ids) + "\n").encode() if object_ids else b""),
    ).decode().splitlines()
    records = sorted(checked)
    digest = sha256(("\n".join(records) + "\n").encode())
    return {
        "object_count": len(records),
        "object_metadata_sha256": digest,
    }


def _git_paths(raw: bytes) -> list[str]:
    paths = []
    for value in raw.split(b"\0"):
        if not value:
            continue
        original = value.decode("utf-8", "strict")
        path = unicodedata.normalize("NFC", original)
        if path != original:
            raise ValueError(f"Git path is not NFC-normalized: {original!r}")
        if path.startswith("/") or path in {"", ".", ".."} or ".." in Path(path).parts:
            raise ValueError(f"unsafe Git path {path!r}")
        paths.append(path)
    if len(paths) != len(set(paths)):
        raise ValueError("normalizing Git paths produced a collision")
    return sorted(paths, key=lambda value: value.encode())


def _index(repo: Path) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    rows = git(repo, "ls-files", "--stage", "-z").split(b"\0")
    normalized_seen: dict[str, str] = {}
    for raw in rows:
        if not raw:
            continue
        metadata, path_raw = raw.split(b"\t", 1)
        mode, object_id, stage = metadata.decode().split()
        path_original = path_raw.decode("utf-8", "strict")
        path = unicodedata.normalize("NFC", path_original)
        if path != path_original:
            raise ValueError(f"index path is not NFC-normalized: {path_original!r}")
        if path.startswith("/") or ".." in Path(path).parts:
            raise ValueError(f"unsafe index path {path!r}")
        if path in normalized_seen and normalized_seen[path] != path_original:
            raise ValueError("normalizing index paths produced a collision")
        normalized_seen[path] = path_original
        if stage != "0":
            raise ValueError(f"unmerged index path cannot be snapshotted: {path}")
        result[path] = (mode, object_id)
    return result


def _entry(
    relative: str,
    layer: str,
    state: str,
    mode: str,
    kind: str,
    raw: bytes,
    selector: dict[str, Any],
) -> dict[str, Any]:
    return {
        "relative_path": relative,
        "layer": layer,
        "state": state,
        "mode": mode,
        "type": kind,
        "byte_count": len(raw),
        "sha256": sha256(raw),
        "selector": selector,
    }


def _filesystem_entry(repo: Path, relative: str) -> dict[str, Any]:
    path = repo / relative
    try:
        info = path.lstat()
    except FileNotFoundError:
        return _entry(
            relative, "WORKTREE", "DELETED", "000000", "DELETED", b"", {"kind": "absent"}
        )
    if stat.S_ISLNK(info.st_mode):
        raw = os.readlink(path).encode("utf-8", "surrogateescape")
        mode, kind = "120000", "SYMLINK"
    elif stat.S_ISREG(info.st_mode):
        raw = path.read_bytes()
        mode = "100755" if info.st_mode & stat.S_IXUSR else "100644"
        kind = "REGULAR"
    else:
        raise ValueError(f"unsupported worktree object type: {relative}")
    return _entry(
        relative, "WORKTREE", "PRESENT", mode, kind, raw, {"kind": "filesystem"}
    )


def worktree_overlay(repo: Path, head: str) -> dict[str, Any]:
    """Content-address every staged, unstaged, and untracked nonignored state."""

    index = _index(repo)
    staged = _git_paths(git(repo, "diff", "--cached", "--name-only", "-z", "--no-renames", head))
    unstaged = _git_paths(git(repo, "diff", "--name-only", "-z", "--no-renames"))
    untracked = _git_paths(git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
    entries: list[dict[str, Any]] = []
    for relative in staged:
        indexed = index.get(relative)
        if indexed is None:
            entries.append(
                _entry(relative, "INDEX", "DELETED", "000000", "DELETED", b"", {"kind": "absent"})
            )
            continue
        mode, object_id = indexed
        raw = git(repo, "cat-file", "blob", object_id)
        kind = "SYMLINK" if mode == "120000" else "REGULAR"
        if mode not in {"100644", "100755", "120000"}:
            raise ValueError(f"unsupported index mode {mode!r}: {relative}")
        entries.append(
            _entry(
                relative,
                "INDEX",
                "PRESENT",
                mode,
                kind,
                raw,
                {"kind": "git_blob", "object_id": object_id},
            )
        )
    for relative in sorted(set(unstaged) | set(untracked), key=lambda value: value.encode()):
        entries.append(_filesystem_entry(repo, relative))
    entries.sort(key=lambda row: (row["relative_path"].encode(), row["layer"]))
    result = {
        "complete": True,
        "base_head_commit": head,
        "entries": entries,
    }
    result["inventory_sha256"] = sha256(canonical_json(entries))
    return result


def _verify_overlay_entry(repo: Path, entry: dict[str, Any]) -> None:
    selector = entry["selector"]
    if selector["kind"] == "git_blob":
        raw = git(repo, "cat-file", "blob", selector["object_id"])
    elif selector["kind"] == "filesystem":
        current = _filesystem_entry(repo, entry["relative_path"])
        raw = (
            os.readlink(repo / entry["relative_path"]).encode("utf-8", "surrogateescape")
            if current["type"] == "SYMLINK"
            else (repo / entry["relative_path"]).read_bytes()
        )
        for key in ("state", "mode", "type"):
            if current[key] != entry[key]:
                raise ValueError(f"worktree overlay metadata drifted: {entry['relative_path']}")
    elif selector["kind"] == "absent":
        raw = b""
        if entry["layer"] == "WORKTREE" and os.path.lexists(repo / entry["relative_path"]):
            raise ValueError(f"deleted worktree path reappeared: {entry['relative_path']}")
        if entry["layer"] == "INDEX" and entry["relative_path"] in _index(repo):
            raise ValueError(f"deleted index path reappeared: {entry['relative_path']}")
    else:
        raise ValueError("unknown worktree overlay selector")
    if len(raw) != entry["byte_count"] or sha256(raw) != entry["sha256"]:
        raise ValueError(f"worktree overlay bytes drifted: {entry['relative_path']}")


def verify_worktree_overlay(repo: Path, expected: dict[str, Any], head: str) -> None:
    if expected.get("base_head_commit") != head:
        raise ValueError("worktree overlay base HEAD mismatch")
    current = worktree_overlay(repo, head)
    if current != expected:
        raise ValueError("worktree overlay inventory drifted")
    for entry in expected["entries"]:
        _verify_overlay_entry(repo, entry)


def remote_urls(repo: Path) -> list[dict[str, str]]:
    rows = []
    names = git(repo, "remote").decode().splitlines()
    for name in sorted(names):
        url = git(repo, "remote", "get-url", name).decode().strip()
        rows.append({"name": name, "url": url})
    return rows


def repo_record(repo: Path, root: Path, classification: dict[str, Any]) -> dict[str, Any]:
    relative = repo.relative_to(root).as_posix()
    base = {
        "source_id": "repo:" + relative,
        "kind": "git_history",
        "path": str(repo.resolve()),
        "relative_path": relative,
        **classification,
    }
    if classification["decision"] != "INCLUDE_SEMANTIC":
        return base
    tips = repository_tips(repo)
    commits = [row["object_id"] for row in tips]
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    objects = object_set(repo, [*commits, head])
    overlay = worktree_overlay(repo, head)
    record = {
        **base,
        "head_commit": head,
        "tips": tips,
        "remotes": remote_urls(repo),
        "worktree_overlay": overlay,
        **objects,
    }
    record["corpus_sha256"] = sha256(
        canonical_json(
            {
                "git_object_metadata_sha256": objects["object_metadata_sha256"],
                "worktree_overlay_inventory_sha256": overlay["inventory_sha256"],
            }
        )
    )
    record["complete"] = True
    record["failure"] = None
    return record


def _upstream_refs(repo: Path) -> list[dict[str, str]]:
    rows = [
        row for row in repository_tips(repo)
        if row["ref"].startswith("refs/remotes/upstream/")
    ]
    if not rows:
        raise ValueError("git_user_delta source has no refs/remotes/upstream/* base")
    return rows


def git_user_delta_record(
    repo: Path, root: Path, classification: dict[str, Any]
) -> dict[str, Any]:
    record = repo_record(repo, root, classification)
    upstream = _upstream_refs(repo)
    all_tips = [row["object_id"] for row in record["tips"]]
    upstream_tips = [row["object_id"] for row in upstream]
    user_commits = git(
        repo, "rev-list", *sorted(set(all_tips + [record["head_commit"]])), "--not", *sorted(set(upstream_tips))
    ).decode().splitlines()
    user_commits = sorted(set(user_commits))
    record.update(
        kind="git_user_delta",
        upstream_base_refs=upstream,
        user_commit_ids=user_commits,
        user_commit_set_sha256=sha256(canonical_json(user_commits)),
    )
    # Contamination scans only user commits plus the complete current overlay;
    # upstream registry objects remain pinned audit inputs, not semantic units.
    record["corpus_sha256"] = sha256(
        canonical_json(
            {
                "user_commit_set_sha256": record["user_commit_set_sha256"],
                "worktree_overlay_inventory_sha256": record["worktree_overlay"]["inventory_sha256"],
            }
        )
    )
    return record


TREE_IGNORED_DIRS = {
    ".git", ".lake", ".venv", "node_modules", "vendor", "__pycache__",
    "graphify-out", ".pytest_cache", "dist", "build", "target",
}


def tree_inventory(root: Path) -> dict[str, Any]:
    entries = []
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        kept_directories = []
        for name in sorted(directories):
            path = current_path / name
            if name in TREE_IGNORED_DIRS:
                continue
            if path.is_symlink():
                relative = path.relative_to(root).as_posix()
                entries.append(_filesystem_entry(root, relative))
            else:
                kept_directories.append(name)
        directories[:] = kept_directories
        for name in sorted(files):
            path = current_path / name
            relative_original = path.relative_to(root).as_posix()
            relative = unicodedata.normalize("NFC", relative_original)
            if relative != relative_original:
                raise ValueError(f"tree path is not NFC-normalized: {relative_original!r}")
            entries.append(_filesystem_entry(root, relative))
    entries.sort(key=lambda row: row["relative_path"].encode())
    # Tree rows have one CURRENT_TREE layer rather than Git's WORKTREE layer.
    for row in entries:
        row["layer"] = "CURRENT_TREE"
    result = {"complete": True, "ignored_directories": sorted(TREE_IGNORED_DIRS), "entries": entries}
    result["inventory_sha256"] = sha256(canonical_json(entries))
    return result


def tree_record(root: Path, projects_root: Path, classification: dict[str, Any]) -> dict[str, Any]:
    relative = root.relative_to(projects_root).as_posix()
    inventory = tree_inventory(root)
    return {
        "source_id": "tree:" + relative,
        "kind": "tree",
        "path": str(root.resolve()),
        "relative_path": relative,
        **classification,
        "tree_snapshot": inventory,
        "corpus_sha256": inventory["inventory_sha256"],
        "complete": True,
        "failure": None,
    }


def _local_session_inventory(root: Path, repo: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    records = []
    for path in sorted(root.rglob("*.jsonl")):
        if path.is_file():
            object_id = git(repo, "hash-object", "--stdin", input_bytes=path.read_bytes()).decode().strip()
            records.append(f"{path.relative_to(root).as_posix()}\0{object_id}")
    return {
        "unit_count": len(records),
        "inventory_sha256": sha256(("\n".join(records) + "\n").encode()),
        "records": records,
    }


def _git_session_inventory(repo: Path, commit: str, subdir: str) -> dict[str, Any]:
    rows = git(repo, "ls-tree", "-r", "-z", commit, "--", subdir).split(b"\0")
    records = []
    prefix = subdir.rstrip("/") + "/"
    for raw in rows:
        if not raw:
            continue
        metadata, path_raw = raw.split(b"\t", 1)
        _mode, kind, object_id = metadata.decode().split()
        path = path_raw.decode("utf-8", "strict")
        if kind == "blob" and path.endswith(".jsonl"):
            relative = path.removeprefix(prefix)
            records.append(f"{relative}\0{object_id}")
    records.sort()
    return {
        "unit_count": len(records),
        "inventory_sha256": sha256(("\n".join(records) + "\n").encode()),
        "records": records,
    }


def _session_mirror(spec: str, ai_repo: Path, commit: str) -> dict[str, Any]:
    mirror_id, separator, remainder = spec.partition("=")
    parts = remainder.split(":", 2)
    if not separator or not mirror_id or len(parts) != 3:
        raise ValueError("session mirror must be ID=FORMAT:LOCAL_ROOT:AI_CHATS_SUBDIR")
    fmt, local_text, subdir = parts
    if fmt not in {"codex", "claude"} or not local_text or not subdir:
        raise ValueError(f"invalid session mirror {mirror_id!r}")
    local = _local_session_inventory(Path(local_text).resolve(), ai_repo)
    mirrored = _git_session_inventory(ai_repo, commit, subdir)
    archived = set(mirrored["records"])
    missing_or_stale = sorted(record for record in local["records"] if record not in archived)
    agrees = not missing_or_stale
    return {
        "id": mirror_id,
        "format": fmt,
        "local_root": str(Path(local_text).resolve()),
        "ai_chats_subdir": subdir,
        "unit_count": local["unit_count"],
        "inventory_sha256": local["inventory_sha256"],
        "mirror_agrees": agrees,
        "archived_unit_count": mirrored["unit_count"],
        "missing_or_stale_local_count": len(missing_or_stale),
        "failure": None if agrees else "LOCAL_SESSION_MIRROR_MISMATCH",
    }


def ai_chats_record(repo: Path, mirror_specs: list[str]) -> dict[str, Any]:
    if not (repo / ".git").exists():
        raise FileNotFoundError(f"ai-chats is not a Git worktree: {repo}")
    commit = git(repo, "rev-parse", "HEAD").decode().strip()
    mirrors = [_session_mirror(spec, repo, commit) for spec in mirror_specs]
    mirrors.sort(key=lambda row: row["id"].encode())
    if worktree_overlay(repo, commit)["entries"]:
        raise ValueError("ai-chats must be committed before its immutable session snapshot")
    objects = object_set(repo, [commit])
    record = {
        "source_id": "sessions:ai-chats",
        "kind": "git_sessions",
        "path": str(repo.resolve()),
        "immutable_commit": commit,
        "remotes": remote_urls(repo),
        "session_mirrors": mirrors,
        **objects,
        "corpus_sha256": objects["object_metadata_sha256"],
    }
    record["complete"] = all(row["mirror_agrees"] for row in mirrors)
    record["failure"] = None if record["complete"] else "UNPINNED_OR_UNSYNCED_SESSION_STATE"
    return record


def release_record(spec: str) -> dict[str, Any]:
    source_id, separator, path_text = spec.partition("=")
    if not separator or not source_id or not path_text:
        raise ValueError("release snapshot must be SOURCE_ID=PATH")
    path = Path(path_text).resolve()
    raw = path.read_bytes()
    # Validate only the export envelope. Never traverse names/bodies here.
    value = json.loads(raw)
    if not isinstance(value, (list, dict)):
        raise ValueError(f"release snapshot {source_id!r} must be JSON")
    return {
        "source_id": "releases:" + source_id,
        "kind": "release_metadata_snapshot",
        "path": str(path),
        "byte_count": len(raw),
        "corpus_sha256": sha256(raw),
        "complete": True,
        "failure": None,
    }


def validate_p0(
    p0t: dict[str, Any],
    repo: Path,
    policy_sha256: str,
    expected_discovery_contract_sha256: str,
    p0t_commit: str,
    public_remote_url: str,
    p0t_artifact_raw: bytes,
) -> dict[str, str]:
    """Validate the real non-self-referential P0T and derive its bindings."""

    if p0t.get("schema_version") != P0_SCHEMA:
        raise ValueError(f"P0 attestation schema must be {P0_SCHEMA!r}")
    if p0t.get("artifact_kind") != "P0T":
        raise ValueError("P0 binding must identify artifact_kind P0T")
    p0a_commit = p0t.get("p0a_commit")
    for field, value in (("p0a_commit", p0a_commit), ("p0t_commit", p0t_commit)):
        if not isinstance(value, str) or not HEX_COMMIT.fullmatch(value):
            raise ValueError(f"{field} must be an exact commit")
        resolved = git(repo, "rev-parse", value).decode().strip()
        if resolved.casefold() != value.casefold():
            raise ValueError(f"{field} is not locally available as an exact commit")
    parents = git(repo, "show", "-s", "--format=%P", p0t_commit).decode().split()
    if parents != [p0a_commit]:
        raise ValueError("P0T must have P0A as its exact sole parent")
    timestamp = p0t.get("p0a_published_at_utc")
    if not isinstance(timestamp, str) or not RFC3339_UTC.fullmatch(timestamp):
        raise ValueError("p0a_published_at_utc must be whole-second RFC3339 UTC")
    p0a_ref = p0t.get("p0a")
    if not isinstance(p0a_ref, dict) or set(p0a_ref) != {"path", "sha256"}:
        raise ValueError("P0T p0a reference must contain exactly path and sha256")
    allowed = p0t.get("attestation_policy", {}).get("allowed_p0t_changed_paths")
    if p0t.get("attestation_policy", {}).get("p0a_ancestor_required") is not True or p0t.get("attestation_policy", {}).get("p0a_bytes_immutable") is not True:
        raise ValueError("P0T attestation policy does not enforce ancestry and immutable P0A bytes")
    if not isinstance(allowed, list) or len(allowed) != 1:
        raise ValueError("P0T must allow exactly its one attestation path")
    changed = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", p0t_commit).decode().splitlines()
    if changed != allowed:
        raise ValueError("P0T commit changed paths outside its attestation")
    committed_p0t = git(repo, "show", f"{p0t_commit}:{allowed[0]}")
    if committed_p0t != p0t_artifact_raw:
        raise ValueError("supplied P0T artifact differs from committed P0T bytes")
    p0a_raw = git(repo, "show", f"{p0a_commit}:{p0a_ref['path']}")
    if sha256(p0a_raw) != p0a_ref["sha256"]:
        raise ValueError("P0T does not authenticate committed P0A bytes")
    p0a = json.loads(p0a_raw)
    if not isinstance(p0a, dict) or p0a.get("artifact_kind") != "P0A":
        raise ValueError("committed P0A artifact is invalid")
    components = p0a.get("components", {})
    for role, expected in (
        ("source_path_policy", policy_sha256),
        ("source_discovery_contract", expected_discovery_contract_sha256),
    ):
        component = components.get(role)
        if not isinstance(component, dict) or component.get("sha256") != expected:
            raise ValueError(f"P0A does not freeze the expected {role}")
        committed = git(repo, "show", f"{p0a_commit}:{component['path']}")
        if sha256(committed) != expected:
            raise ValueError(f"P0A {role} committed bytes disagree")
    if not isinstance(public_remote_url, str) or not public_remote_url:
        raise ValueError("public_remote_url must be nonempty")
    advertised = subprocess.run(
        ["git", "ls-remote", public_remote_url], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout.decode().splitlines()
    advertised_ids = {line.split()[0].casefold() for line in advertised if line.split()}
    if p0t_commit.casefold() not in advertised_ids:
        raise ValueError("P0T is not advertised by the recorded public remote")
    return {
        "p0a_commit": p0a_commit,
        "p0t_commit": p0t_commit.lower(),
        "p0a_published_at_utc": timestamp,
        "public_remote_url": public_remote_url,
    }


def build_config(
    projects_root: Path,
    policy_path: Path,
    ai_chats_repo: Path | None,
    session_mirror_specs: list[str],
    release_specs: list[str],
    p0_attestation_path: Path | None,
    p0t_commit: str | None,
    public_remote_url: str | None,
    protocol_repo: Path,
) -> dict[str, Any]:
    policy, policy_raw = load_json(policy_path)
    validate_policy(policy)
    policy_sha = sha256(policy_raw)
    contract_sha = discovery_contract_sha256(
        projects_root, ai_chats_repo, session_mirror_specs, release_specs
    )
    p0 = None
    if p0_attestation_path is not None:
        p0, p0_raw = load_json(p0_attestation_path)
        if p0t_commit is None or public_remote_url is None:
            raise ValueError("production discovery requires --p0t-commit and --public-remote-url")
        p0_binding = validate_p0(
            p0, protocol_repo, policy_sha, contract_sha, p0t_commit, public_remote_url, p0_raw
        )
    else:
        p0_binding = None

    discovered = []
    for path in discover_project_directories(projects_root.resolve()):
        relative = path.relative_to(projects_root.resolve()).as_posix()
        classification = classify_path(relative, policy)
        if classification["decision"] != "INCLUDE_SEMANTIC":
            discovered.append({
                "source_id": "path:" + relative,
                "kind": "excluded_directory",
                "path": str(path.resolve()),
                "relative_path": relative,
                **classification,
            })
            continue
        source_kind = classification["source_kind"]
        if source_kind == "git_history":
            discovered.append(repo_record(path, projects_root.resolve(), classification))
        elif source_kind == "git_user_delta":
            discovered.append(git_user_delta_record(path, projects_root.resolve(), classification))
        elif source_kind == "tree":
            discovered.append(tree_record(path, projects_root.resolve(), classification))
        else:  # validate_policy makes this unreachable.
            raise ValueError(f"unknown included source kind {source_kind!r}")
    sources = [row for row in discovered if row["decision"] == "INCLUDE_SEMANTIC"]
    if ai_chats_repo is not None:
        sources.append(ai_chats_record(ai_chats_repo.resolve(), session_mirror_specs))
    sources.extend(release_record(spec) for spec in release_specs)
    sources.sort(key=lambda row: row["source_id"].encode())
    excluded = [row for row in discovered if row["decision"] != "INCLUDE_SEMANTIC"]
    excluded.sort(key=lambda row: row["source_id"].encode())
    unknown = [row for row in excluded if row["decision"] == "EXCLUDE_UNKNOWN"]
    incomplete = [row for row in sources if not row.get("complete", False)]
    mirror_ids = {
        mirror["id"]
        for row in sources
        if row["kind"] == "git_sessions"
        for mirror in row["session_mirrors"]
    }
    release_ids = {
        row["source_id"].removeprefix("releases:")
        for row in sources
        if row["kind"] == "release_metadata_snapshot"
    }
    missing_mirrors = sorted(set(policy["required_session_mirror_ids"]) - mirror_ids)
    missing_releases = sorted(set(policy["required_release_snapshot_ids"]) - release_ids)
    result: dict[str, Any] = {
        "schema_version": CONFIG_SCHEMA if p0 else PROTOTYPE_CONFIG_SCHEMA,
        "prototype_only": p0 is None,
        "candidate_semantics_inspected": False,
        "discovery_operations": [
            "PATH_NAMES",
            "GIT_REFS_AND_OBJECT_METADATA",
            "GIT_REMOTE_URLS",
            "WORKTREE_STATUS_PATHS",
            "RELEASE_EXPORT_BYTE_HASH",
        ],
        "projects_root": str(projects_root.resolve()),
        "source_path_policy": {
            "path": str(policy_path.resolve()),
            "sha256": policy_sha,
        },
        "source_discovery_contract_sha256": contract_sha,
        "protocol": p0_binding,
        "sources": sources,
        "nonresearch_exclusions": excluded,
        "complete": not unknown and not incomplete and ai_chats_repo is not None and not missing_mirrors and not missing_releases,
        "failures": {
            "unknown_path_count": len(unknown),
            "incomplete_source_count": len(incomplete),
            "ai_chats_missing": ai_chats_repo is None,
            "missing_required_session_mirror_ids": missing_mirrors,
            "missing_required_release_snapshot_ids": missing_releases,
        },
    }
    result["sources_config_sha256"] = content_address(result, "sources_config_sha256")
    return result


def verify_config_sources(config: dict[str, Any]) -> None:
    if config.get("schema_version") != CONFIG_SCHEMA or config.get("prototype_only") is not False:
        raise ValueError("S0 requires a non-prototype sources config produced after public P0")
    if config.get("sources_config_sha256") != content_address(config, "sources_config_sha256"):
        raise ValueError("sources config content address mismatch")
    if not config.get("complete"):
        raise ValueError("sources config is incomplete")
    for source in config["sources"]:
        path = Path(source["path"])
        if source["kind"] == "git_history":
            head = git(path, "rev-parse", "HEAD").decode().strip()
            if head != source["head_commit"] or repository_tips(path) != source["tips"]:
                raise ValueError(f"Git source drifted after discovery: {source['source_id']}")
            current = object_set(path, [head, *[row["object_id"] for row in source["tips"]]])
            if any(current[key] != source[key] for key in current):
                raise ValueError(f"Git corpus drifted after discovery: {source['source_id']}")
            verify_worktree_overlay(path, source["worktree_overlay"], head)
            expected_corpus = sha256(
                canonical_json(
                    {
                        "git_object_metadata_sha256": current["object_metadata_sha256"],
                        "worktree_overlay_inventory_sha256": source["worktree_overlay"]["inventory_sha256"],
                    }
                )
            )
            if source.get("corpus_sha256") != expected_corpus:
                raise ValueError(f"source corpus digest mismatch: {source['source_id']}")
        elif source["kind"] == "git_user_delta":
            head = git(path, "rev-parse", "HEAD").decode().strip()
            if head != source["head_commit"] or repository_tips(path) != source["tips"]:
                raise ValueError(f"Git delta source drifted: {source['source_id']}")
            replay = git_user_delta_record(
                path,
                Path(config["projects_root"]),
                {key: source[key] for key in ("decision", "policy_rule_id", "purpose", "source_kind")},
            )
            for key in ("upstream_base_refs", "user_commit_ids", "user_commit_set_sha256", "worktree_overlay", "corpus_sha256"):
                if replay[key] != source[key]:
                    raise ValueError(f"Git delta corpus drifted: {source['source_id']}")
        elif source["kind"] == "tree":
            current = tree_inventory(path)
            if current != source["tree_snapshot"] or source.get("corpus_sha256") != current["inventory_sha256"]:
                raise ValueError(f"unversioned tree drifted: {source['source_id']}")
        elif source["kind"] == "git_sessions":
            if git(path, "rev-parse", "HEAD").decode().strip() != source["immutable_commit"] or worktree_overlay(path, source["immutable_commit"])["entries"]:
                raise ValueError("ai-chats commit/worktree drifted after discovery")
            current = object_set(path, [source["immutable_commit"]])
            if any(current[key] != source[key] for key in current):
                raise ValueError("ai-chats corpus drifted after discovery")
            for mirror in source["session_mirrors"]:
                local = _local_session_inventory(Path(mirror["local_root"]), path)
                pinned = _git_session_inventory(path, source["immutable_commit"], mirror["ai_chats_subdir"])
                if (
                    not set(local["records"]).issubset(set(pinned["records"]))
                    or local["unit_count"] != mirror["unit_count"]
                    or local["inventory_sha256"] != mirror["inventory_sha256"]
                ):
                    raise ValueError(f"local session mirror drifted: {mirror['id']}")
        elif source["kind"] == "release_metadata_snapshot":
            raw = path.read_bytes()
            if len(raw) != source["byte_count"] or sha256(raw) != source["corpus_sha256"]:
                raise ValueError(f"release snapshot drifted: {source['source_id']}")
        else:
            raise ValueError(f"unknown source kind {source['kind']!r}")


def acquire_s0(
    config_path: Path,
    policy_path: Path,
    attestation_path: Path,
    protocol_repo: Path,
    p0t_commit: str,
    public_remote_url: str,
    acquired_at: str,
) -> dict[str, Any]:
    if not RFC3339_UTC.fullmatch(acquired_at):
        raise ValueError("acquired_at must be whole-second RFC3339 UTC")
    config, config_raw = load_json(config_path)
    if config.get("schema_version") != CONFIG_SCHEMA or config.get("prototype_only") is not False:
        raise ValueError("S0 requires a non-prototype sources config produced after public P0")
    policy, policy_raw = load_json(policy_path)
    validate_policy(policy)
    attestation, attestation_raw = load_json(attestation_path)
    policy_sha = sha256(policy_raw)
    binding = validate_p0(
        attestation,
        protocol_repo,
        policy_sha,
        config["source_discovery_contract_sha256"],
        p0t_commit,
        public_remote_url,
        attestation_raw,
    )
    published = dt.datetime.fromisoformat(binding["p0a_published_at_utc"].replace("Z", "+00:00"))
    acquired = dt.datetime.fromisoformat(acquired_at.replace("Z", "+00:00"))
    if acquired <= published:
        raise ValueError("S0 acquisition must occur after P0 publication")
    if config.get("source_path_policy", {}).get("sha256") != policy_sha:
        raise ValueError("sources config policy digest mismatch")
    if config.get("protocol") != binding:
        raise ValueError("sources config was not bound to this P0 attestation")
    if sha256(config_raw) == config.get("sources_config_sha256"):
        # The field is an internal content address (excluding itself), never a
        # misleading whole-file hash.
        raise ValueError("ambiguous sources config digest construction")
    verify_config_sources(config)
    result: dict[str, Any] = {
        "schema_version": SNAPSHOT_SCHEMA,
        "snapshot_id": "S0",
        "acquired_at_utc": acquired_at,
        "p0a_commit": binding["p0a_commit"],
        "p0t_commit": binding["p0t_commit"],
        "p0a_published_at_utc": binding["p0a_published_at_utc"],
        "source_path_policy_sha256": policy_sha,
        "source_discovery_contract_sha256": config["source_discovery_contract_sha256"],
        "sources_config_sha256": config["sources_config_sha256"],
        "sources_config_file_sha256": sha256(config_raw),
        "candidate_semantics_inspected": False,
        "complete": True,
        "sources": [dict(source, acquired_at_utc=acquired_at) for source in config["sources"]],
        "nonresearch_exclusions": config["nonresearch_exclusions"],
    }
    result["corpus_sha256"] = sha256(canonical_json(result["sources"]))
    result["snapshot_sha256"] = content_address(result, "snapshot_sha256")
    return result


def write_output(value: dict[str, Any], output: Path | None) -> None:
    encoded = pretty_json(value)
    if output:
        output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    discover = subparsers.add_parser("discover")
    discover.add_argument("--projects-root", type=Path, required=True)
    discover.add_argument("--policy", type=Path, required=True)
    discover.add_argument("--ai-chats-repo", type=Path)
    discover.add_argument("--session-mirror", action="append", default=[])
    discover.add_argument("--release-snapshot", action="append", default=[])
    discover.add_argument("--p0-attestation", type=Path)
    discover.add_argument("--p0t-commit")
    discover.add_argument("--public-remote-url")
    discover.add_argument("--protocol-repo", type=Path, default=Path.cwd())
    discover.add_argument("--output", type=Path)
    acquire = subparsers.add_parser("acquire")
    acquire.add_argument("--sources-config", type=Path, required=True)
    acquire.add_argument("--policy", type=Path, required=True)
    acquire.add_argument("--p0-attestation", type=Path, required=True)
    acquire.add_argument("--p0t-commit", required=True)
    acquire.add_argument("--public-remote-url", required=True)
    acquire.add_argument("--protocol-repo", type=Path, default=Path.cwd())
    acquire.add_argument("--acquired-at", required=True)
    acquire.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "discover":
        value = build_config(
            args.projects_root,
            args.policy,
            args.ai_chats_repo,
            args.session_mirror,
            args.release_snapshot,
            args.p0_attestation,
            args.p0t_commit,
            args.public_remote_url,
            args.protocol_repo,
        )
    else:
        value = acquire_s0(
            args.sources_config,
            args.policy,
            args.p0_attestation,
            args.protocol_repo,
            args.p0t_commit,
            args.public_remote_url,
            args.acquired_at,
        )
    write_output(value, args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
