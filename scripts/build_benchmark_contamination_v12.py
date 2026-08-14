#!/usr/bin/env python3
"""Replay Method v1.2 identity exposure without reading target semantics.

The input pool already contains registry-derived identity metadata.  This
program searches source units only for exact identity aliases, classifies each
unit by provenance, and emits hashes/locators rather than snippets.  It never
opens the pinned registry and never selects or orders a target.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterator
import unicodedata

import classify_benchmark_provenance_v12 as provenance
import build_benchmark_v12_source_snapshot as source_snapshot


SCHEMA = "c5k4-contamination-inventory-1.2-prototype"
CONFIG_SCHEMA = "c5k4-contamination-sources-1.2-prototype"
OVERLAY_SCHEMA = "c5k4-eligible-cluster-pool-1.2-prototype"
FEASIBILITY_SCHEMA = "c5k4-quota-feasibility-1.2-prototype"
ARTIFACT_STATUS = "PRE_P0_NOT_FREEZE"
PROVENANCE_CLASSES = (
    "SEMANTIC_SOURCE",
    "MACHINE_REGISTRY_CONTACT",
    "UNKNOWN",
)
QUOTAS = {
    "GRAPH_SCALAR_INEQUALITY": 3,
    "GRAPH_STRUCTURAL_PROPERTY": 3,
    "FINITE_ALGEBRA_EQUATIONAL": 2,
    "AUTOMATA_GAME_PROCESS": 2,
    "FINITE_COMBINATORIAL": 2,
}
HEX_COMMIT = re.compile(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})")


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_bytes,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def normalized_tokens(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text)
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    return " " + re.sub(r"[^a-z0-9]+", " ", folded.casefold()).strip() + " "


def aliases_for(cluster: dict[str, Any]) -> list[str]:
    """Return exact registry identities and only namespace-anchored shortcuts."""

    path = cluster["path"]
    source = Path(path)
    module = path.removesuffix(".lean")
    aliases = {path, module}
    for declaration in cluster["declarations"]:
        name = declaration["name"]
        # A declaration name alone has no namespace anchor.  Only its full
        # registry identity is safe for semantics-blind replay.
        aliases.update({f"{path}::{name}", f"{module}::{name}"})

    # Numeric conveniences exist only together with their namespace anchor.
    if "ErdosProblems" in source.parts and source.stem.isdigit():
        number = source.stem
        aliases.update({f"Erdos {number}", f"Erdos Problem {number}"})
    if "WrittenOnTheWallII" in source.parts:
        match = re.fullmatch(r"GraphConjecture(\d+[a-z]?)", source.stem)
        if match:
            number = match.group(1)
            aliases.update(
                {
                    f"WOWII {number}",
                    f"WOW II {number}",
                    f"WOWII GraphConjecture {number}",
                    f"WOW II Graph Conjecture {number}",
                }
            )
    return sorted({normalized_tokens(alias).strip() for alias in aliases})


def content_schema(raw: bytes) -> str | None:
    try:
        value = json.loads(raw.decode("utf-8", "strict"), parse_int=str)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    schema = value.get("schema_version") if isinstance(value, dict) else None
    return schema if isinstance(schema, str) else None


def unit(
    source_id: str,
    source_kind: str,
    locator: str,
    role: str,
    raw: bytes,
    provenance_class: str,
    *,
    unit_identity_sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_kind": source_kind,
        "locator": locator,
        "role": role,
        "raw": raw,
        "content_sha256": sha256(raw),
        "content_schema": content_schema(raw),
        "byte_count": len(raw),
        "provenance_class": provenance_class,
        "unit_identity_sha256": unit_identity_sha256,
        "mixed": False,
        "malformed": provenance_class == "UNKNOWN" and role in {"malformed-json-raw", "non-object-json", "malformed-git-diff-entry", "malformed-release-row"},
    }


def text_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    values = []
    for block in content:
        if isinstance(block, dict) and block.get("type") in {
            "text",
            "input_text",
            "output_text",
        } and isinstance(block.get("text"), str):
            values.append(block["text"])
    return "\n".join(values)


def session_units(
    raw: bytes,
    fmt: str,
    source_id: str,
    source_kind: str,
    relative: str,
    registry_units: dict[tuple[str, str, str, str], str],
) -> Iterator[dict[str, Any]]:
    calls: dict[str, tuple[str, object]] = {}
    for line_number, line in enumerate(raw.decode("utf-8", "strict").splitlines(), 1):
        locator = f"{relative}:{line_number}"
        try:
            row = json.loads(line, parse_int=str)
        except json.JSONDecodeError:
            yield unit(source_id, source_kind, locator, "malformed-json-raw", line.encode(), "UNKNOWN")
            continue
        if not isinstance(row, dict):
            yield unit(source_id, source_kind, locator, "non-object-json", line.encode(), "UNKNOWN")
            continue

        if fmt == "codex":
            payload = row.get("payload", {})
            if row.get("type") == "response_item" and isinstance(payload, dict):
                if payload.get("type") in {"message", "agent_message"}:
                    role = payload.get("role", "assistant-agent")
                    value = text_content(payload.get("content"))
                    if value and role in {"user", "assistant", "assistant-agent"}:
                        semantic_role = "user-turn" if role == "user" else "assistant-turn"
                        yield unit(source_id, source_kind, locator, semantic_role, value.encode("utf-8", "surrogatepass"), "SEMANTIC_SOURCE")
                    elif value:
                        yield unit(source_id, source_kind, locator, "unclassified", value.encode("utf-8", "surrogatepass"), "UNKNOWN")
                elif payload.get("type") == "function_call" and isinstance(payload.get("call_id"), str):
                    arguments: object = payload.get("arguments")
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            arguments = None
                    if arguments is not None:
                        calls[payload["call_id"]] = (str(payload.get("name", "")), arguments)
                        yield unit(source_id, source_kind, locator, "tool-call", canonical_json({"tool_name": payload.get("name"), "tool_input": arguments}), "UNKNOWN")
                elif payload.get("type") == "function_call_output":
                    output = payload.get("output")
                    call = calls.get(payload.get("call_id"))
                    if not isinstance(output, str) or call is None:
                        yield unit(source_id, source_kind, locator, "unpaired-tool-output", line.encode(), "UNKNOWN")
                    else:
                        raw_output = output.encode("utf-8", "surrogatepass")
                        key = (source_id, locator, "codex-tool-output", sha256(raw_output))
                        identity = registry_units.get(key)
                        classification = "MACHINE_REGISTRY_CONTACT" if identity else "UNKNOWN"
                        yield unit(source_id, source_kind, locator, "codex-tool-output", raw_output, classification, unit_identity_sha256=identity)
            elif row.get("type") == "turn_context":
                value = payload.get("summary") if isinstance(payload, dict) else None
                if isinstance(value, str) and value:
                    yield unit(source_id, source_kind, locator, "assistant-turn", value.encode("utf-8", "surrogatepass"), "SEMANTIC_SOURCE")
        elif fmt == "claude":
            content = row.get("message", {}).get("content", [])
            if row.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use" and isinstance(block.get("id"), str):
                        calls[block["id"]] = (str(block.get("name", "")), block.get("input"))
                        yield unit(source_id, source_kind, locator, "tool-call", canonical_json({"tool_name": block.get("name"), "tool_input": block.get("input")}), "UNKNOWN")
            if row.get("type") in {"user", "assistant"} and isinstance(content, list):
                natural = [block for block in content if not (isinstance(block, dict) and block.get("type") in {"tool_use", "tool_result"})]
                value = text_content(natural)
                if value:
                    semantic_role = "user-turn" if row["type"] == "user" else "assistant-turn"
                    yield unit(source_id, source_kind, locator, semantic_role, value.encode("utf-8", "surrogatepass"), "SEMANTIC_SOURCE")
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_result":
                        continue
                    output = text_content(block.get("content"))
                    raw_output = output.encode("utf-8", "surrogatepass")
                    call = calls.get(block.get("tool_use_id"))
                    if not output or call is None:
                        yield unit(source_id, source_kind, locator, "unpaired-tool-output", line.encode(), "UNKNOWN")
                        continue
                    key = (source_id, locator, "claude-tool-output", sha256(raw_output))
                    identity = registry_units.get(key)
                    classification = "MACHINE_REGISTRY_CONTACT" if identity else "UNKNOWN"
                    yield unit(source_id, source_kind, locator, "claude-tool-output", raw_output, classification, unit_identity_sha256=identity)
        else:
            raise ValueError(f"unknown session format: {fmt}")


def iter_git_history(repo: Path, source: dict[str, Any]) -> Iterator[dict[str, Any]]:
    source_id = source["id"]
    tips = source["tips"]
    commits = git(repo, "rev-list", *tips).decode().splitlines()
    seen_blobs: set[tuple[str, str]] = set()
    for commit in commits:
        message = git(repo, "show", "-s", "--format=%B", commit)
        yield unit(source_id, "git", f"commit:{commit}", "commit-message", message, "SEMANTIC_SOURCE")
        entries = git(repo, "diff-tree", "--root", "--no-renames", "--no-commit-id", "--raw", "-r", commit).decode().splitlines()
        for entry in entries:
            metadata, _, path = entry.partition("\t")
            parts = metadata.split()
            if len(parts) < 5 or not path:
                yield unit(source_id, "git", f"tree-entry:{commit}", "malformed-git-diff-entry", entry.encode(), "UNKNOWN")
                continue
            blob = parts[3]
            path_raw = path.encode("utf-8", "surrogatepass")
            yield unit(source_id, "git", f"git-path:{commit}:{path}", "git-metadata", path_raw, "UNKNOWN")
            if set(blob) == {"0"} or (blob, path) in seen_blobs:
                continue
            seen_blobs.add((blob, path))
            raw = git(repo, "cat-file", "blob", blob)
            if b"\x00" in raw:
                continue
            key = (source_id, f"git-blob:{blob}:{path}", "machine-generated-git-blob", sha256(raw))
            identity = source["registry_units"].get(key)
            provenance = "MACHINE_REGISTRY_CONTACT" if identity else "SEMANTIC_SOURCE"
            yield unit(source_id, "git", f"git-blob:{blob}:{path}", "machine-generated-git-blob" if identity else "repo-code", raw, provenance, unit_identity_sha256=identity)


def iter_git_delta(repo: Path, source: dict[str, Any]) -> Iterator[dict[str, Any]]:
    source_id = source["id"]
    excluded = source["excluded_commits"]
    commits = git(repo, "rev-list", *source["tips"], "--not", *excluded).decode().splitlines()
    for commit in commits:
        message = git(repo, "show", "-s", "--format=%B", commit)
        yield unit(source_id, "git_delta", f"commit:{commit}", "commit-message", message, "SEMANTIC_SOURCE")
        names = git(repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()
        for path in names:
            yield unit(source_id, "git_delta", f"changed-path:{commit}:{path}", "git-metadata", path.encode(), "UNKNOWN")
        patch = git(repo, "show", "--format=", "--unified=0", "--no-ext-diff", commit).decode("utf-8", "replace").splitlines()
        for line_number, line in enumerate(patch, 1):
            if line.startswith("+") and not line.startswith("+++"):
                raw = line[1:].encode("utf-8", "surrogatepass")
                yield unit(source_id, "git_delta", f"added-line:{commit}:{line_number}", "repo-code", raw, "SEMANTIC_SOURCE")


def expected_git_corpus_sha256(
    source: dict[str, Any], overlay_inventory_sha256: str
) -> str:
    """Reconstruct the corpus binding defined by the frozen Git source kind."""

    kind = source.get("kind")
    if kind == "git":
        binding_key = "git_object_metadata_sha256"
        source_key = "object_metadata_sha256"
    elif kind in {"git_delta", "git_user_delta"}:
        binding_key = "user_commit_set_sha256"
        source_key = "user_commit_set_sha256"
    else:
        raise ValueError(f"unsupported Git corpus binding kind: {kind!r}")
    binding_sha256 = source.get(source_key)
    if not isinstance(binding_sha256, str):
        raise ValueError(f"git source {source.get('id')!r} lacks {source_key}")
    return sha256(
        canonical_json(
            {
                binding_key: binding_sha256,
                "worktree_overlay_inventory_sha256": overlay_inventory_sha256,
            }
        )
    )


def iter_worktree_overlay(repo: Path, source: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Validate and scan a source-snapshot overlay exactly, failing on drift."""

    overlay = source.get("worktree_overlay")
    if not isinstance(overlay, dict) or overlay.get("complete") is not True:
        raise ValueError(f"git source {source['id']!r} lacks a complete worktree_overlay")
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    if overlay.get("base_head_commit") != head:
        raise ValueError(f"worktree overlay HEAD drift: {source['id']}")
    # Independently enumerate the live index/worktree so omitted rows fail.
    source_snapshot.verify_worktree_overlay(repo, overlay, head)
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise ValueError("worktree_overlay.entries must be a list")
    if overlay.get("inventory_sha256") != sha256(canonical_json(entries)):
        raise ValueError("worktree_overlay inventory digest mismatch")
    if source.get("complete") is True and "corpus_sha256" not in source:
        raise ValueError(f"frozen git source {source['id']!r} lacks corpus_sha256")
    if "corpus_sha256" in source:
        expected_corpus = expected_git_corpus_sha256(
            source, overlay["inventory_sha256"]
        )
        if source["corpus_sha256"] != expected_corpus:
            raise ValueError(f"git source corpus binding mismatch: {source['id']}")
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("worktree overlay entry must be an object")
        path = entry.get("relative_path")
        layer = entry.get("layer")
        if not isinstance(path, str) or not path or layer not in {"INDEX", "WORKTREE"}:
            raise ValueError("worktree overlay entry path/layer is invalid")
        if (path, layer) in seen:
            raise ValueError("duplicate worktree overlay path/layer")
        seen.add((path, layer))
        selector = entry.get("selector")
        if not isinstance(selector, dict):
            raise ValueError("worktree overlay selector is invalid")
        kind = selector.get("kind")
        state = entry.get("state")
        if state == "DELETED" and kind == "absent":
            raw = b""
        elif state == "PRESENT" and kind == "git_blob" and layer == "INDEX":
            object_id = selector.get("object_id")
            if not isinstance(object_id, str) or not object_id:
                raise ValueError("INDEX overlay lacks object_id")
            raw = git(repo, "cat-file", "blob", object_id)
        elif state == "PRESENT" and kind == "filesystem" and layer == "WORKTREE":
            filesystem_path = repo / path
            if entry.get("type") == "SYMLINK":
                raw = filesystem_path.readlink().as_posix().encode()
            else:
                raw = filesystem_path.read_bytes()
        else:
            raise ValueError("worktree overlay state/selector/layer conflict")
        if len(raw) != entry.get("byte_count") or sha256(raw) != entry.get("sha256"):
            raise ValueError(f"worktree overlay drift: {source['id']}:{layer}:{path}")
        yield unit(source["id"], "git", f"worktree-path:{layer}:{path}", "git-metadata", path.encode(), "UNKNOWN")
        if state == "PRESENT" and b"\x00" not in raw:
            yield unit(source["id"], "git", f"worktree:{layer}:{entry['sha256']}:{path}", "repo-code", raw, "SEMANTIC_SOURCE")


def iter_tree(root: Path, source: dict[str, Any]) -> Iterator[dict[str, Any]]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    ignored = {".git", "node_modules", ".lake", ".venv", "__pycache__", "graphify-out"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        relative = str(path.relative_to(root))
        yield unit(source["id"], "tree", f"tree-path:{relative}", "git-metadata", relative.encode(), "UNKNOWN")
        raw = path.read_bytes()
        if b"\x00" not in raw:
            yield unit(source["id"], "tree", f"tree:{relative}", "repo-code", raw, "SEMANTIC_SOURCE")


def iter_source(source: dict[str, Any], registry_units: dict[tuple[str, str, str, str], str]) -> Iterator[dict[str, Any]]:
    kind = source["kind"]
    root = Path(source["path"])
    if kind == "git":
        effective = source
        if source.get("capture_worktree_overlay") is True:
            head = git(root, "rev-parse", "HEAD").decode().strip()
            effective = {**source, "worktree_overlay": source_snapshot.worktree_overlay(root, head)}
        # Verify and materialize mutable filesystem selectors immediately;
        # scanning a large immutable Git history must not widen the drift race.
        overlay_units = list(iter_worktree_overlay(root, effective))
        yield from iter_git_history(root, {**effective, "registry_units": registry_units})
        yield from overlay_units
    elif kind == "git_delta":
        yield from iter_git_delta(root, source)
    elif kind == "tree":
        yield from iter_tree(root, source)
    elif kind == "git_sessions":
        entries = git(root, "ls-tree", "-r", source["ref"], "--", source["subdir"]).decode().splitlines()
        for entry in sorted(entries):
            metadata, _, relative = entry.partition("\t")
            parts = metadata.split()
            if len(parts) != 3 or not relative.endswith(".jsonl"):
                continue
            blob = parts[2]
            immutable_relative = f"session-blob:{blob}:{relative}"
            yield from session_units(git(root, "show", f"{source['ref']}:{relative}"), source["format"], source["id"], kind, immutable_relative, registry_units)
    elif kind == "release_snapshot":
        data = json.loads(root.read_text(encoding="utf-8"), parse_int=str)
        if not isinstance(data, list):
            raise ValueError("release snapshot must be a list")
        for index, row in enumerate(data):
            if not isinstance(row, dict):
                raw = canonical_json(row)
                yield unit(source["id"], kind, f"release:{index}", "malformed-release-row", raw, "UNKNOWN")
                continue
            for field in ("tag_name", "tagName", "name", "body"):
                value = row.get(field)
                if isinstance(value, str) and value:
                    yield unit(source["id"], kind, f"release:{index}:{field}", "human-message", value.encode(), "SEMANTIC_SOURCE")
    else:
        raise ValueError(f"unknown source kind: {kind}")


def validate_config(config: dict[str, Any]) -> None:
    if config.get("schema_version") != CONFIG_SCHEMA:
        raise ValueError(f"config schema_version must be {CONFIG_SCHEMA!r}")
    if config.get("artifact_status") != ARTIFACT_STATUS:
        raise ValueError(f"config artifact_status must be {ARTIFACT_STATUS!r}")
    sources = config.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("config.sources must be a nonempty list")
    ids = []
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            raise ValueError("each source needs a string id")
        ids.append(source["id"])
        kind = source.get("kind")
        if kind in {"git", "git_delta"}:
            tips = source.get("tips")
            if not isinstance(tips, list) or not tips or not all(isinstance(x, str) and HEX_COMMIT.fullmatch(x) for x in tips):
                raise ValueError(f"source {source['id']} needs exact tips")
        if kind == "git" and not isinstance(source.get("worktree_overlay"), dict):
            if source.get("capture_worktree_overlay") is not True:
                raise ValueError(f"source {source['id']} needs worktree_overlay")
        if kind == "git_delta":
            excluded = source.get("excluded_commits")
            if not isinstance(excluded, list) or not excluded or not all(isinstance(x, str) and HEX_COMMIT.fullmatch(x) for x in excluded):
                raise ValueError(f"source {source['id']} needs exact excluded_commits")
        if kind == "git_sessions" and (not isinstance(source.get("ref"), str) or not HEX_COMMIT.fullmatch(source["ref"])):
            raise ValueError(f"source {source['id']} needs exact ref")
    if len(ids) != len(set(ids)):
        raise ValueError("source ids must be unique")


def registry_unit_index(exemptions: dict[str, Any]) -> dict[tuple[str, str, str, str], str]:
    if exemptions.get("complete") is not True:
        raise ValueError("registry exemptions must be complete")
    index = {}
    for row in exemptions.get("units", []):
        key = (row["source_id"], row["locator"], row["role"], row["content_sha256"])
        index[key] = row["unit_identity_sha256"]
    return index


def registry_exemption_index(exemptions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if exemptions.get("complete") is not True:
        raise ValueError("registry exemptions must be complete")
    return provenance.exemption_index(exemptions.get("units", []))


def alias_trie(pool: dict[str, Any]) -> tuple[dict, dict[str, list[str]]]:
    trie: dict = {}
    aliases: dict[str, list[str]] = {}
    for cluster in pool["clusters"]:
        cluster_aliases = aliases_for(cluster)
        aliases[cluster["cluster_id"]] = cluster_aliases
        for alias in cluster_aliases:
            node = trie
            for token in alias.split():
                node = node.setdefault(token, {})
            node.setdefault(None, []).append((cluster["cluster_id"], alias))
    return trie, aliases


def match_aliases(trie: dict, raw: bytes) -> dict[str, set[str]]:
    tokens = normalized_tokens(raw.decode("utf-8", "replace")).split()
    matches: dict[str, set[str]] = defaultdict(set)
    for start in range(len(tokens)):
        node = trie
        cursor = start
        while cursor < len(tokens):
            node = node.get(tokens[cursor])
            if node is None:
                break
            for cluster_id, alias in node.get(None, ()):
                matches[cluster_id].add(alias)
            cursor += 1
    return matches


def build(pool: dict[str, Any], config: dict[str, Any], exemptions: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    validate_config(config)
    if pool.get("artifact_status") != "PRE_P0_PROTOTYPE_NOT_A_FREEZE":
        raise ValueError("input pool is not the tracked pre-P0 prototype")
    registry_units = registry_unit_index(exemptions)
    exemption_by_identity = registry_exemption_index(exemptions)
    policy_path = Path(__file__).resolve().parents[1] / "results/benchmark/v1.2-prototype/provenance-policy.json"
    policy = provenance.load_policy(policy_path)
    trie, aliases = alias_trie(pool)
    evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    totals: dict[str, Counter] = defaultdict(Counter)
    source_audit = []
    all_complete = True
    matches_by_content_sha256: dict[str, dict[str, set[str]]] = {}
    for source in config["sources"]:
        count = Counter()
        corpus = hashlib.sha256()
        evidence_corpus = hashlib.sha256()
        failure = None
        try:
            for record in iter_source(source, registry_units):
                identity = provenance.unit_identity_sha256(record)
                classified = provenance.classify_unit(record, exemption_by_identity.get(identity), policy)
                provenance_class = classified["provenance_class"]
                count[provenance_class] += 1
                corpus.update(canonical_json({key: classified.get(key) for key in ("locator", "role", "content_sha256", "content_schema", "provenance_class", "unit_identity_sha256")}))
                matched_clusters = matches_by_content_sha256.get(record["content_sha256"])
                if matched_clusters is None:
                    matched_clusters = match_aliases(trie, record["raw"])
                    matches_by_content_sha256[record["content_sha256"]] = matched_clusters
                for cluster_id, matched in matched_clusters.items():
                    item = {
                        "source_id": source["id"],
                        "locator": record["locator"],
                        "role": record["role"],
                        "provenance_class": provenance_class,
                        "classification_reason": classified["classification_reason"],
                        "content_sha256": record["content_sha256"],
                        "unit_identity_sha256": classified["unit_identity_sha256"],
                        "matched_alias_sha256s": sorted(sha256(value.encode()) for value in matched),
                    }
                    evidence[cluster_id].append(item)
                    totals[cluster_id][provenance_class] += 1
                    evidence_corpus.update(canonical_json(item))
        except Exception as exc:
            all_complete = False
            failure = f"{type(exc).__name__}: {exc}"
        source_audit.append(
            {
                "id": source["id"],
                "kind": source.get("kind"),
                "complete": failure is None,
                "failure": failure,
                "unit_count": sum(count.values()),
                "units_by_provenance_class": {name: count[name] for name in PROVENANCE_CLASSES},
                "corpus_sha256": corpus.hexdigest(),
                "identity_evidence_sha256": evidence_corpus.hexdigest(),
            }
        )

    rows = []
    for cluster in pool["clusters"]:
        cluster_id = cluster["cluster_id"]
        hits = sorted(evidence[cluster_id], key=lambda row: (row["source_id"], row["locator"], row["role"], row["content_sha256"]))
        excluding = totals[cluster_id]["SEMANTIC_SOURCE"] + totals[cluster_id]["UNKNOWN"]
        if excluding:
            status, basis = "EXPOSED", "SEMANTIC_OR_UNKNOWN_IDENTITY_EVIDENCE"
        elif not all_complete:
            status, basis = "EXPOSED", "INCOMPLETE_SOURCE_FAIL_CLOSED"
        else:
            status, basis = "UNEXPOSED", "NO_EXCLUDING_IDENTITY_EVIDENCE"
        rows.append(
            {
                "cluster_id": cluster_id,
                "identity_sha256": cluster["identity_sha256"],
                "path": cluster["path"],
                "alias_set_sha256": sha256(canonical_json(aliases[cluster_id])),
                "exposure_status": status,
                "exposure_basis": basis,
                "evidence_total": len(hits),
                "evidence_by_provenance_class": {name: totals[cluster_id][name] for name in PROVENANCE_CLASSES},
                "evidence_sha256": sha256(canonical_json(hits)),
                "evidence": hits,
            }
        )
    exposed = {row["cluster_id"] for row in rows if row["exposure_status"] == "EXPOSED"}
    inventory: dict[str, Any] = {
        "schema_version": SCHEMA,
        "artifact_status": ARTIFACT_STATUS,
        "decision_input": "IDENTITY_AND_PROVENANCE_METADATA_ONLY",
        "statement_text_inspected": False,
        "evidence_cap": None,
        "global_content_hash_exemptions": False,
        "pool_sha256": sha256(canonical_json(pool)),
        "config_sha256": sha256(canonical_json(config)),
        "registry_exemptions_sha256": sha256(canonical_json(exemptions)),
        "complete": all_complete,
        "source_audit": source_audit,
        "excluded_cluster_count": len(exposed),
        "excluded_cluster_ids": sorted(exposed),
        "clusters": rows,
    }
    inventory["inventory_sha256"] = sha256(canonical_json(inventory))

    overlay_rows = []
    by_id = {row["cluster_id"]: row for row in rows}
    for cluster in pool["clusters"]:
        exposure = by_id[cluster["cluster_id"]]
        final_eligible = cluster.get("eligible") is True and exposure["exposure_status"] == "UNEXPOSED"
        overlay_rows.append(
            {
                **cluster,
                "pre_contamination_eligible": cluster.get("eligible") is True,
                "eligible": final_eligible,
                "contamination_status": exposure["exposure_status"],
                "contamination_basis": exposure["exposure_basis"],
                "contamination_evidence_total": exposure["evidence_total"],
                "contamination_evidence_sha256": exposure["evidence_sha256"],
            }
        )
    overlay: dict[str, Any] = {
        "schema_version": OVERLAY_SCHEMA,
        "artifact_status": ARTIFACT_STATUS,
        "upstream": pool["upstream"],
        "source_pool_sha256": sha256(canonical_json(pool)),
        "contamination_inventory_sha256": inventory["inventory_sha256"],
        "eligibility_rule": "MACHINE_CLASSIFIED_AND_IDENTITY_COMPLETE_AND_NO_SEMANTIC_OR_UNKNOWN_EXPOSURE",
        "entropy_used": False,
        "selected_cluster_ids": [],
        "clusters": overlay_rows,
    }
    overlay["eligible_pool_sha256"] = sha256(canonical_json(overlay))

    counts = Counter(row.get("stratum") for row in overlay_rows if row["eligible"])
    strata = []
    for stratum, quota in QUOTAS.items():
        eligible = counts[stratum]
        strata.append({"stratum": stratum, "quota": quota, "eligible_count": eligible, "surplus": max(0, eligible - quota), "deficit": max(0, quota - eligible)})
    feasible = all(row["deficit"] == 0 for row in strata)
    certificate: dict[str, Any] = {
        "schema_version": FEASIBILITY_SCHEMA,
        "artifact_status": ARTIFACT_STATUS,
        "phase": "PRE_C0_FEASIBILITY_PROTOTYPE",
        "result": "PASS" if feasible else "FAIL",
        "terminal_result": None if feasible else "NO_ELIGIBLE_BENCHMARK_PRE_C0_PROTOTYPE",
        "entropy_used": False,
        "selected_cluster_ids": [],
        "required_cluster_count": sum(QUOTAS.values()),
        "eligible_cluster_count": sum(counts.values()),
        "pool_sha256": overlay["eligible_pool_sha256"],
        "contamination_inventory_sha256": inventory["inventory_sha256"],
        "strata": strata,
    }
    certificate["certificate_sha256"] = sha256(canonical_json(certificate))
    return inventory, overlay, certificate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--registry-exemptions", type=Path, required=True)
    parser.add_argument("--inventory-output", type=Path, required=True)
    parser.add_argument("--eligible-output", type=Path, required=True)
    parser.add_argument("--feasibility-output", type=Path, required=True)
    args = parser.parse_args()
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    exemptions = json.loads(args.registry_exemptions.read_text(encoding="utf-8"))
    outputs = build(pool, config, exemptions)
    for path, value in zip((args.inventory_output, args.eligible_output, args.feasibility_output), outputs):
        path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
