#!/usr/bin/env python3
"""Build a deterministic, semantics-blind Method v1.1 contamination inventory.

The builder extracts only registry/path/declaration-name metadata from a pinned
``formal-conjectures`` Git tree. It does not inspect candidate semantics while
deciding exposure. It scans frozen artifact sources for identity aliases and
emits hashes and locators, never matched snippets.

``UNEXPOSED`` is permitted only when every configured source completes. Any
source failure conservatively changes every otherwise unmatched provisional
cluster to ``EXPOSED`` with basis ``CONSERVATIVE_UNCERTAINTY``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from typing import Iterator


SCHEMA = "c5k4-contamination-inventory-1.0-draft"
CONFIG_SCHEMA = "c5k4-contamination-sources-1.0-draft"
OPEN_RE = re.compile(
    r"@\[\s*category\s+research\s+open\b.*?\]\s*"
    r"(?:(?:noncomputable|private|protected)\s+)*"
    r"(?:theorem|lemma|def|abbrev)\s+([^\s(:]+)",
    re.DOTALL,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()


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


def camel_words(value: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)


def aliases_for(path: str, declarations: list[str]) -> list[str]:
    """Generate identity aliases from path and declaration registry metadata."""

    source = Path(path)
    stem = source.stem
    aliases = {path, *declarations}
    # Bare numeric stems generate catastrophic false positives in transcripts.
    if not stem.isdigit():
        aliases.update({stem, camel_words(stem)})

    wowii = re.fullmatch(r"GraphConjecture(\d+[a-z]?)", stem)
    if wowii:
        number = wowii.group(1)
        aliases.update(
            {
                f"WOWII {number}",
                f"WOW II {number}",
                f"conjecture {number}",
                f"Graph Conjecture {number}",
                f"conjecture{number}",
            }
        )
    if "WrittenOnTheWallII" in source.parts and re.fullmatch(r"\d+[a-z]?", stem):
        aliases.update({f"WOWII {stem}", f"WOW II {stem}", f"conjecture {stem}"})
    if "ErdosProblems" in source.parts and stem.isdigit():
        aliases.update({f"Erdos {stem}", f"Erdos Problem {stem}", f"erdos_{stem}"})

    normalized = {normalized_tokens(alias).strip() for alias in aliases if len(alias) >= 3}
    return sorted(alias for alias in normalized if len(alias) >= 3)


def open_clusters(repo: Path, ref: str) -> tuple[dict, list[dict]]:
    """Extract conservative source-module clusters from one exact Git tree."""

    commit = git(repo, "rev-parse", ref).decode().strip()
    tree = git(repo, "rev-parse", f"{ref}^{{tree}}").decode().strip()
    names = git(
        repo, "ls-tree", "-r", "--name-only", ref, "--", "FormalConjectures"
    ).decode().splitlines()
    clusters = []
    for path in sorted(name for name in names if name.endswith(".lean")):
        raw = git(repo, "show", f"{ref}:{path}")
        text = raw.decode("utf-8", "strict")
        matches = list(OPEN_RE.finditer(text))
        if not matches:
            continue
        declarations = [match.group(1) for match in matches]
        aliases = aliases_for(path, declarations)
        file_sha = sha256(raw)
        identity = {
            "path": path,
            "declarations": declarations,
            "file_sha256": file_sha,
        }
        clusters.append(
            {
                "cluster_id": "fc-module:" + path.removesuffix(".lean"),
                "identity_sha256": sha256(canonical_json(identity)),
                "grouping_rule": "ONE_SOURCE_MODULE_CONSERVATIVE_MERGE",
                "path": path,
                "source_blob_sha256": file_sha,
                "declarations": [
                    {
                        "name": match.group(1),
                        "category_line": text.count("\n", 0, match.start()) + 1,
                    }
                    for match in matches
                ],
                "aliases": aliases,
                "alias_set_sha256": sha256(canonical_json(aliases)),
            }
        )
    return {"commit": commit, "tree": tree}, clusters


def text_unit(source_id: str, locator: str, role: str, text: str) -> dict:
    raw = text.encode("utf-8", "surrogatepass")
    return {
        "source_id": source_id,
        "locator": locator,
        "role": role,
        "unit_sha256": sha256(raw),
        "text": text,
    }


def content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    output = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") in {"text", "input_text", "output_text"}:
            value = block.get("text")
            if isinstance(value, str):
                output.append(value)
    return "\n".join(output)


def iter_sessions(root: Path, fmt: str, source_id: str) -> Iterator[dict]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    for path in sorted(root.rglob("*.jsonl")):
        relative = str(path.relative_to(root))
        with path.open(encoding="utf-8", errors="strict") as handle:
            for line_number, line in enumerate(handle, 1):
                row = json.loads(line)
                if fmt == "codex":
                    payload = row.get("payload", {})
                    if row.get("type") == "response_item" and payload.get("type") == "message":
                        role = payload.get("role")
                        if role in {"user", "assistant"}:
                            value = content_text(payload.get("content"))
                            if value:
                                yield text_unit(
                                    source_id, f"{relative}:{line_number}", role, value
                                )
                    elif (
                        row.get("type") == "response_item"
                        and payload.get("type") == "agent_message"
                    ):
                        value = content_text(payload.get("content"))
                        if value:
                            yield text_unit(
                                source_id,
                                f"{relative}:{line_number}",
                                "assistant-agent",
                                value,
                            )
                    elif row.get("type") == "turn_context":
                        value = payload.get("summary")
                        if isinstance(value, str) and value:
                            yield text_unit(
                                source_id,
                                f"{relative}:{line_number}",
                                "compaction-summary",
                                value,
                            )
                elif fmt == "claude":
                    # Tool outputs often echo the entire registry and are not proof that
                    # a human or model considered a target's semantics.
                    if row.get("type") not in {"user", "assistant"} or row.get("toolUseResult"):
                        continue
                    value = content_text(row.get("message", {}).get("content"))
                    if value:
                        yield text_unit(
                            source_id, f"{relative}:{line_number}", row["type"], value
                        )
                else:
                    raise ValueError(f"unknown session format: {fmt}")


def iter_release_snapshot(path: Path, source_id: str) -> Iterator[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("release snapshot must be a JSON list")
    for index, row in enumerate(data):
        if not isinstance(row, dict):
            raise ValueError("release snapshot rows must be objects")
        fields = [
            str(row.get(key, ""))
            for key in ("tag_name", "tagName", "name", "body")
        ]
        yield text_unit(
            source_id, f"release:{index}", "release-metadata", "\n".join(fields)
        )


def iter_tree(root: Path, source_id: str) -> Iterator[dict]:
    if not root.is_dir():
        raise FileNotFoundError(root)
    ignored = {".git", "node_modules", ".lake", ".venv", "__pycache__"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in ignored for part in path.parts):
            continue
        relative = str(path.relative_to(root))
        raw = path.read_bytes()
        yield text_unit(source_id, f"tree-path:{relative}", "tree-path", relative)
        if b"\x00" not in raw:
            yield text_unit(
                source_id,
                f"tree:{relative}",
                "tree-file",
                raw.decode("utf-8", "replace"),
            )


def iter_git(repo: Path, source_id: str, include_worktree: bool) -> Iterator[dict]:
    if not (repo / ".git").exists():
        raise FileNotFoundError(f"not a Git repository: {repo}")
    log = git(repo, "log", "--all", "--format=%H%x00%B%x00", "--name-only", "-z")
    yield text_unit(
        source_id, "git-log-and-paths", "git-metadata", log.decode("utf-8", "replace")
    )

    objects: dict[str, str] = {}
    for line in git(repo, "rev-list", "--objects", "--all").decode(
        "utf-8", "replace"
    ).splitlines():
        object_id, _, path = line.partition(" ")
        objects.setdefault(object_id, path)
    object_ids = list(objects)
    checks = git(
        repo,
        "cat-file",
        "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        input_bytes=("\n".join(object_ids) + "\n").encode(),
    ).decode().splitlines()
    wanted = []
    for row in checks:
        object_id, kind, size = row.split()
        if kind == "blob":
            wanted.append((object_id, int(size), objects[object_id]))

    process = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin and process.stdout
    for object_id, expected_size, object_path in wanted:
        process.stdin.write((object_id + "\n").encode())
        process.stdin.flush()
        header = process.stdout.readline().decode().split()
        size = int(header[2])
        raw = process.stdout.read(size)
        process.stdout.read(1)
        if size != expected_size:
            raise ValueError("git cat-file size mismatch")
        if object_path:
            yield text_unit(
                source_id, f"blob-path:{object_id}", "git-path", object_path
            )
        if b"\x00" not in raw:
            yield text_unit(
                source_id,
                f"blob:{object_id}:{object_path}",
                "git-blob",
                raw.decode("utf-8", "replace"),
            )
    process.stdin.close()
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, process.args)

    if include_worktree:
        for path in sorted(repo.rglob("*")):
            if not path.is_file() or ".git" in path.parts:
                continue
            raw = path.read_bytes()
            relative = str(path.relative_to(repo))
            yield text_unit(
                source_id, f"worktree-path:{relative}", "worktree-path", relative
            )
            if b"\x00" not in raw:
                yield text_unit(
                    source_id,
                    f"worktree:{relative}",
                    "worktree-file",
                    raw.decode("utf-8", "replace"),
                )


def iter_git_delta(repo: Path, source_id: str, excluded_ref_prefix: str) -> Iterator[dict]:
    """Scan commits not reachable from a registry vendor's refs.

    This avoids treating a vendor checkout of the complete declaration registry
    as universal exposure. User-only commit metadata, paths, and added lines
    remain evidence.
    """

    refs = git(repo, "for-each-ref", "--format=%(refname)").decode().splitlines()
    excluded = sorted(ref for ref in refs if ref.startswith(excluded_ref_prefix))
    if not excluded:
        raise ValueError(f"no excluded refs matching {excluded_ref_prefix!r}")
    commits = git(repo, "rev-list", "--all", "--not", *excluded).decode().splitlines()
    for commit in commits:
        metadata = git(repo, "show", "-s", "--format=%H%n%B", commit).decode(
            "utf-8", "replace"
        )
        yield text_unit(source_id, f"commit:{commit}", "git-delta-metadata", metadata)
        names = git(
            repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit
        )
        yield text_unit(
            source_id,
            f"changed-paths:{commit}",
            "git-delta-paths",
            names.decode("utf-8", "replace"),
        )
        patch = git(repo, "show", "--format=", "--unified=0", "--no-ext-diff", commit)
        added = [
            line[1:]
            for line in patch.decode("utf-8", "replace").splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        if added:
            yield text_unit(
                source_id,
                f"added-lines:{commit}",
                "git-delta-added-lines",
                "\n".join(added),
            )


def load_exemptions(path: Path | None) -> tuple[set[str], str | None]:
    if path is None:
        return set(), None
    raw = path.read_bytes()
    data = json.loads(raw)
    return set(data.get("registry_only_unit_sha256", [])), sha256(raw)


def validate_config(config: dict) -> None:
    if config.get("schema_version") != CONFIG_SCHEMA:
        raise ValueError(f"config schema_version must be {CONFIG_SCHEMA!r}")
    if config.get("template_only") is True:
        raise ValueError("refusing to run a template_only source configuration")
    sources = config.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("config sources must be a nonempty list")
    identities = [source.get("id") for source in sources if isinstance(source, dict)]
    if len(identities) != len(sources) or any(not value for value in identities):
        raise ValueError("every source must be an object with a nonempty id")
    if len(identities) != len(set(identities)):
        raise ValueError("source ids must be unique")


def scan(
    config: dict, clusters: list[dict], exemptions: set[str]
) -> tuple[list[dict], list[dict]]:
    evidence = {cluster["cluster_id"]: [] for cluster in clusters}
    evidence_total = {cluster["cluster_id"]: 0 for cluster in clusters}
    source_records = []
    complete = True
    alias_index = [
        (cluster["cluster_id"], alias)
        for cluster in clusters
        for alias in cluster["aliases"]
    ]
    for source in config["sources"]:
        source_id = source["id"]
        count = 0
        corpus = hashlib.sha256()
        failure = None
        try:
            kind = source["kind"]
            if kind == "git":
                units = iter_git(
                    Path(source["path"]), source_id, source.get("include_worktree", False)
                )
            elif kind == "git_delta":
                units = iter_git_delta(
                    Path(source["path"]), source_id, source["excluded_ref_prefix"]
                )
            elif kind == "sessions":
                units = iter_sessions(Path(source["path"]), source["format"], source_id)
            elif kind == "release_snapshot":
                units = iter_release_snapshot(Path(source["path"]), source_id)
            elif kind == "tree":
                units = iter_tree(Path(source["path"]), source_id)
            else:
                raise ValueError(f"unknown source kind: {kind}")
            for unit in units:
                count += 1
                corpus.update(
                    canonical_json(
                        {
                            key: unit[key]
                            for key in ("locator", "role", "unit_sha256")
                        }
                    )
                )
                if unit["unit_sha256"] in exemptions:
                    continue
                haystack = normalized_tokens(unit.pop("text"))
                for cluster_id, alias in alias_index:
                    if f" {alias} " in haystack:
                        evidence_total[cluster_id] += 1
                        if len(evidence[cluster_id]) < 50:
                            evidence[cluster_id].append(
                                {
                                    "source_id": source_id,
                                    "locator": unit["locator"],
                                    "role": unit["role"],
                                    "unit_sha256": unit["unit_sha256"],
                                    "matched_alias_sha256": sha256(alias.encode()),
                                }
                            )
        except Exception as error:  # fail closed in output; never silently pass.
            complete = False
            failure = f"{type(error).__name__}: {error}"
        source_records.append(
            {
                "id": source_id,
                "kind": source.get("kind"),
                "units": count,
                "corpus_sha256": corpus.hexdigest(),
                "complete": failure is None,
                "failure": failure,
            }
        )

    output = []
    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        hits = evidence[cluster_id]
        if hits:
            status, basis = "EXPOSED", "DIRECT_IDENTITY_MATCH"
        elif not complete:
            status, basis = "EXPOSED", "CONSERVATIVE_UNCERTAINTY"
        else:
            status, basis = "UNEXPOSED", "COMPLETE_NO_IDENTITY_MATCH"
        row = dict(cluster)
        row.update(
            exposure_status=status,
            exposure_basis=basis,
            evidence_total=evidence_total[cluster_id],
            evidence_truncated=evidence_total[cluster_id] > len(hits),
            evidence=hits,
        )
        output.append(row)
    return source_records, output


def build_inventory(
    formal_repo: Path,
    formal_ref: str,
    config_path: Path,
    exemptions_path: Path | None = None,
) -> dict:
    if not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", formal_ref):
        raise ValueError("formal_ref must be an exact 40- or 64-hex commit, not a branch")
    resolved_ref = git(formal_repo, "rev-parse", formal_ref).decode().strip()
    if resolved_ref.casefold() != formal_ref.casefold():
        raise ValueError("formal_ref does not resolve to itself as an exact commit")
    config_raw = config_path.read_bytes()
    config = json.loads(config_raw)
    validate_config(config)
    upstream, clusters = open_clusters(formal_repo, formal_ref)
    exemptions, exemptions_sha = load_exemptions(exemptions_path)
    sources, rows = scan(config, clusters, exemptions)
    exposed = [row for row in rows if row["exposure_status"] == "EXPOSED"]
    result = {
        "schema_version": SCHEMA,
        "upstream": upstream,
        "config_sha256": sha256(config_raw),
        "sources": sources,
        "registry_exemption_count": len(exemptions),
        "registry_exemptions_sha256": exemptions_sha,
        "excluded_cluster_ids": sorted(row["cluster_id"] for row in exposed),
        "excluded_identity_sha256s": sorted(row["identity_sha256"] for row in exposed),
        # The benchmark schema uses file digests for declaration exclusion, so
        # one exposed sibling conservatively excludes every open sibling in the
        # same source module.
        "excluded_declaration_sha256s": sorted(
            {row["source_blob_sha256"] for row in exposed}
        ),
        "clusters": rows,
    }
    result["inventory_sha256"] = sha256(canonical_json(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-repo", type=Path, required=True)
    parser.add_argument("--formal-ref", required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--registry-exemptions", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_inventory(
        args.formal_repo, args.formal_ref, args.config, args.registry_exemptions
    )
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
