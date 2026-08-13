#!/usr/bin/env python3
"""Discover and freeze Method v1.2 semantic-source boundaries without semantics.

Only filesystem names and Git/release object metadata are read during discovery.
Git blobs, commit messages, transcript turns, and release bodies are never read.
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
import subprocess
import sys
from typing import Any, Iterable


POLICY_SCHEMA = "c5k4-source-path-purpose-policy-1.2"
CONFIG_SCHEMA = "c5k4-semantic-sources-config-1.2"
PROTOTYPE_CONFIG_SCHEMA = CONFIG_SCHEMA + "-prototype"
P0_SCHEMA = "c5k4-protocol-attestation-1.2"
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

    return sha256(
        canonical_json(
            {
                "tool": "build_benchmark_v12_source_snapshot.py/discover",
                "projects_root": str(projects_root.resolve()),
                "ai_chats_repo": None if ai_chats_repo is None else str(ai_chats_repo.resolve()),
                "session_mirror_specs": sorted(session_mirror_specs),
                "release_snapshot_specs": sorted(release_specs),
            }
        )
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
    }


def discover_git_repositories(root: Path) -> list[Path]:
    """Find worktrees using directory names only, pruning known bulk internals."""

    if not root.is_dir():
        raise FileNotFoundError(root)
    found: list[Path] = []
    pruned = {".git", ".lake", ".venv", "node_modules", "vendor", "graphify-out"}
    for current, directories, _files in os.walk(root):
        directories[:] = sorted(name for name in directories if name not in pruned)
        current_path = Path(current)
        if (current_path / ".git").exists():
            found.append(current_path)
            directories[:] = []
    return sorted(found, key=lambda path: path.relative_to(root).as_posix().encode())


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
        "corpus_sha256": digest,
    }


def worktree_clean(repo: Path) -> bool:
    # Status codes and paths are not semantic contents; dirty trees cannot be pinned.
    return not bool(git(repo, "status", "--porcelain=v1", "--untracked-files=all"))


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
    record = {
        **base,
        "head_commit": head,
        "tips": tips,
        "remotes": remote_urls(repo),
        "worktree_clean": worktree_clean(repo),
        **object_set(repo, [*commits, head]),
    }
    record["complete"] = record["worktree_clean"]
    record["failure"] = None if record["complete"] else "UNPINNED_WORKTREE_STATE"
    return record


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
    agrees = local["records"] == mirrored["records"]
    return {
        "id": mirror_id,
        "format": fmt,
        "local_root": str(Path(local_text).resolve()),
        "ai_chats_subdir": subdir,
        "unit_count": local["unit_count"],
        "inventory_sha256": local["inventory_sha256"],
        "mirror_agrees": agrees,
        "failure": None if agrees else "LOCAL_SESSION_MIRROR_MISMATCH",
    }


def ai_chats_record(repo: Path, mirror_specs: list[str]) -> dict[str, Any]:
    if not (repo / ".git").exists():
        raise FileNotFoundError(f"ai-chats is not a Git worktree: {repo}")
    commit = git(repo, "rev-parse", "HEAD").decode().strip()
    mirrors = [_session_mirror(spec, repo, commit) for spec in mirror_specs]
    mirrors.sort(key=lambda row: row["id"].encode())
    record = {
        "source_id": "sessions:ai-chats",
        "kind": "git_sessions",
        "path": str(repo.resolve()),
        "immutable_commit": commit,
        "remotes": remote_urls(repo),
        "worktree_clean": worktree_clean(repo),
        "session_mirrors": mirrors,
        **object_set(repo, [commit]),
    }
    record["complete"] = record["worktree_clean"] and all(row["mirror_agrees"] for row in mirrors)
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
    attestation: dict[str, Any],
    repo: Path,
    policy_sha256: str,
    expected_discovery_contract_sha256: str | None = None,
) -> None:
    if attestation.get("schema_version") != P0_SCHEMA:
        raise ValueError(f"P0 attestation schema must be {P0_SCHEMA!r}")
    for field in ("p0_artifact_commit", "p0_attestation_commit"):
        if not isinstance(attestation.get(field), str) or not HEX_COMMIT.fullmatch(attestation[field]):
            raise ValueError(f"{field} must be an exact commit")
        resolved = git(repo, "rev-parse", attestation[field]).decode().strip()
        if resolved.casefold() != attestation[field].casefold():
            raise ValueError(f"{field} is not locally available as an exact commit")
    subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", attestation["p0_artifact_commit"], attestation["p0_attestation_commit"]],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    timestamp = attestation.get("p0_published_at_utc")
    if not isinstance(timestamp, str) or not RFC3339_UTC.fullmatch(timestamp):
        raise ValueError("p0_published_at_utc must be whole-second RFC3339 UTC")
    if attestation.get("source_path_policy_sha256") != policy_sha256:
        raise ValueError("P0 does not freeze this source path-purpose policy")
    contract_sha = attestation.get("source_discovery_contract_sha256")
    if not isinstance(contract_sha, str) or not HEX_SHA256.fullmatch(contract_sha):
        raise ValueError("P0 must freeze a source_discovery_contract_sha256")
    if expected_discovery_contract_sha256 is not None and contract_sha != expected_discovery_contract_sha256:
        raise ValueError("P0 source-discovery invocation contract does not match")
    remote = attestation.get("public_remote_url")
    if not isinstance(remote, str) or not remote:
        raise ValueError("P0 attestation needs public_remote_url")
    advertised = subprocess.run(
        ["git", "ls-remote", remote], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout.decode().splitlines()
    advertised_ids = {line.split()[0].casefold() for line in advertised if line.split()}
    if attestation["p0_attestation_commit"].casefold() not in advertised_ids:
        raise ValueError("P0T is not advertised by the recorded public remote")


def build_config(
    projects_root: Path,
    policy_path: Path,
    ai_chats_repo: Path | None,
    session_mirror_specs: list[str],
    release_specs: list[str],
    p0_attestation_path: Path | None,
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
        p0, _ = load_json(p0_attestation_path)
        validate_p0(p0, protocol_repo, policy_sha, contract_sha)

    discovered = []
    for repo in discover_git_repositories(projects_root.resolve()):
        relative = repo.relative_to(projects_root.resolve()).as_posix()
        discovered.append(repo_record(repo, projects_root.resolve(), classify_path(relative, policy)))
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
        "protocol": None if p0 is None else {
            key: p0[key]
            for key in ("p0_artifact_commit", "p0_attestation_commit", "p0_published_at_utc", "public_remote_url")
        },
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
            if head != source["head_commit"] or repository_tips(path) != source["tips"] or not worktree_clean(path):
                raise ValueError(f"Git source drifted after discovery: {source['source_id']}")
            current = object_set(path, [head, *[row["object_id"] for row in source["tips"]]])
            if any(current[key] != source[key] for key in current):
                raise ValueError(f"Git corpus drifted after discovery: {source['source_id']}")
        elif source["kind"] == "git_sessions":
            if git(path, "rev-parse", "HEAD").decode().strip() != source["immutable_commit"] or not worktree_clean(path):
                raise ValueError("ai-chats commit/worktree drifted after discovery")
            current = object_set(path, [source["immutable_commit"]])
            if any(current[key] != source[key] for key in current):
                raise ValueError("ai-chats corpus drifted after discovery")
            for mirror in source["session_mirrors"]:
                local = _local_session_inventory(Path(mirror["local_root"]), path)
                pinned = _git_session_inventory(path, source["immutable_commit"], mirror["ai_chats_subdir"])
                if (
                    local["records"] != pinned["records"]
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
    acquired_at: str,
) -> dict[str, Any]:
    if not RFC3339_UTC.fullmatch(acquired_at):
        raise ValueError("acquired_at must be whole-second RFC3339 UTC")
    config, config_raw = load_json(config_path)
    if config.get("schema_version") != CONFIG_SCHEMA or config.get("prototype_only") is not False:
        raise ValueError("S0 requires a non-prototype sources config produced after public P0")
    policy, policy_raw = load_json(policy_path)
    validate_policy(policy)
    attestation, _ = load_json(attestation_path)
    policy_sha = sha256(policy_raw)
    validate_p0(attestation, protocol_repo, policy_sha)
    published = dt.datetime.fromisoformat(attestation["p0_published_at_utc"].replace("Z", "+00:00"))
    acquired = dt.datetime.fromisoformat(acquired_at.replace("Z", "+00:00"))
    if acquired <= published:
        raise ValueError("S0 acquisition must occur after P0 publication")
    if config.get("source_path_policy", {}).get("sha256") != policy_sha:
        raise ValueError("sources config policy digest mismatch")
    if config.get("source_discovery_contract_sha256") != attestation.get("source_discovery_contract_sha256"):
        raise ValueError("sources config discovery contract mismatch")
    expected_protocol = {
        key: attestation[key]
        for key in ("p0_artifact_commit", "p0_attestation_commit", "p0_published_at_utc", "public_remote_url")
    }
    if config.get("protocol") != expected_protocol:
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
        "p0_artifact_commit": attestation["p0_artifact_commit"],
        "p0_attestation_commit": attestation["p0_attestation_commit"],
        "p0_published_at_utc": attestation["p0_published_at_utc"],
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
    discover.add_argument("--protocol-repo", type=Path, default=Path.cwd())
    discover.add_argument("--output", type=Path)
    acquire = subparsers.add_parser("acquire")
    acquire.add_argument("--sources-config", type=Path, required=True)
    acquire.add_argument("--policy", type=Path, required=True)
    acquire.add_argument("--p0-attestation", type=Path, required=True)
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
            args.protocol_repo,
        )
    else:
        value = acquire_s0(
            args.sources_config,
            args.policy,
            args.p0_attestation,
            args.protocol_repo,
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
