#!/usr/bin/env python3
"""Immutable source/status/duplicate gate; never evaluates a graph target."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

UPSTREAM_COMMIT = "b5acb0ff13e38084105b7fe020ba0d59c1925bc5"
UPSTREAM_TREE = "4f6c9bd17fdfdc264f54b26862ce768743da5d63"
UPSTREAM_URL = "https://github.com/google-deepmind/formal-conjectures.git"
TARGET_PATH = "FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean"
TARGET_BLOB = "c4c5cb1983936860d5a4a7208b3f04bd201290d4"
TARGET_SHA256 = "562fbbb0ec47041a61017bb85ec0c7e9aa6fc98cf132be3022268a7dc60e9004"
PAPER_SHA256 = "56213cd6384cc2111864d67150c41e1426608c59b1b009c6752acab9be3487fb"
KNOWN_ISSUE = 4858
KNOWN_PR = 4879
KNOWN_ISSUE_CLOSED_AT = "2026-08-14T20:25:51Z"
KNOWN_PR_MERGED_AT = "2026-08-14T20:25:50Z"
KNOWN_PR_MERGE_COMMIT = "8781428a922a53914450550218bf14be703d8d69"
KNOWN_PREFLIGHT_COMMIT = "d22eb07173794848fd375b5675059946ee3860b5"
KNOWN_REPIN_AUDIT_COMMIT = "e17905b1d62048f43bab89e06625aebdcf280faf"
KNOWN_REPIN_AUDIT_PATH = "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/upstream-drift-repin-audit.md"
KNOWN_CONTINUITY_AUDIT_COMMIT = "c4d327479110cf51f2aae126d12e2fbc609c0921"
KNOWN_CONTINUITY_AUDIT_PATH = "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/tip-continuity-policy-audit.md"
HERE = Path(__file__).resolve().parents[1] / "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development"
SEMANTIC_CLOSURE = HERE / "semantic-closure-v3.json"
SEARCH_QUERIES = (
    'repo:google-deepmind/formal-conjectures "bondy_conjecture"',
    'repo:google-deepmind/formal-conjectures "BondyLongestCycles"',
    'repo:google-deepmind/formal-conjectures "2606.03696"',
)
ALLOWED_SEARCH_RESULTS = {
    SEARCH_QUERIES[0]: [4879],
    SEARCH_QUERIES[1]: [],
    SEARCH_QUERIES[2]: [4879],
}
SNAPSHOT_WORKERS = 24
ACTIVE_DEADLINE: float | None = None


def remaining_timeout(cap: float = 20.0) -> float:
    if ACTIVE_DEADLINE is None:
        return cap
    remaining = ACTIVE_DEADLINE - time.monotonic()
    if remaining <= 0.25:
        raise TimeoutError("whole-gate monotonic deadline")
    return min(cap, remaining)


def api(path: str, token: str) -> object:
    request = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "c5-k4-bondy-frozen-gate",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=remaining_timeout()) as response:
        return json.load(response)


def graphql(query: str, variables: dict[str, object], token: str) -> dict[str, object]:
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}, separators=(",", ":")).encode("ascii"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "c5-k4-bondy-v3-continuity-gate",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=remaining_timeout()) as response:
        value = json.load(response)
    if not isinstance(value, dict) or value.get("errors") or not isinstance(value.get("data"), dict):
        raise RuntimeError("GraphQL error, truncation, or rate-limit response")
    return value["data"]


OPEN_PULL_QUERY = """
query($cursor:String) { repository(owner:"google-deepmind",name:"formal-conjectures") {
  pullRequests(first:100,after:$cursor,states:OPEN,orderBy:{field:CREATED_AT,direction:ASC}) {
    totalCount pageInfo { hasNextPage endCursor }
    nodes { id number state title isDraft updatedAt headRefOid headRefName headRepository { nameWithOwner }
      baseRefOid baseRefName baseRepository { nameWithOwner }
      changedFiles files(first:100) { totalCount pageInfo { hasNextPage endCursor } nodes { path changeType } } }
  }
} rateLimit { cost remaining resetAt } }
"""
OPEN_PULL_IDENTITY_QUERY = """
query($cursor:String) { repository(owner:"google-deepmind",name:"formal-conjectures") {
  pullRequests(first:100,after:$cursor,states:OPEN,orderBy:{field:CREATED_AT,direction:ASC}) {
    totalCount pageInfo { hasNextPage endCursor }
    nodes { id number state title isDraft updatedAt headRefOid headRefName headRepository { nameWithOwner }
      baseRefOid baseRefName baseRepository { nameWithOwner } changedFiles }
  }
} rateLimit { cost remaining resetAt } }
"""
MORE_FILES_QUERY = """
query($number:Int!,$cursor:String!) { repository(owner:"google-deepmind",name:"formal-conjectures") {
  pullRequest(number:$number) { number updatedAt headRefOid baseRefOid changedFiles
    files(first:100,after:$cursor) { totalCount pageInfo { hasNextPage endCursor } nodes { path changeType } } }
} rateLimit { cost remaining resetAt } }
"""


def page_info(connection: object, label: str) -> tuple[list[dict[str, object]], bool, str | None]:
    if not isinstance(connection, dict) or not isinstance(connection.get("nodes"), list) or not isinstance(connection.get("pageInfo"), dict):
        raise RuntimeError(f"{label} GraphQL pagination shape drift")
    nodes = connection["nodes"]
    if any(not isinstance(node, dict) for node in nodes):
        raise RuntimeError(f"{label} GraphQL node drift")
    info = connection["pageInfo"]
    more = info.get("hasNextPage")
    cursor = info.get("endCursor")
    if not isinstance(more, bool) or (more and (not isinstance(cursor, str) or not cursor)):
        raise RuntimeError(f"{label} GraphQL pagination ambiguity")
    return nodes, more, cursor if isinstance(cursor, str) else None


def graphql_open_pull_bindings(token: str) -> dict[str, object]:
    rate_limits: list[dict[str, object]] = []

    def checked_graphql(query: str, variables: dict[str, object]) -> dict[str, object]:
        remaining_timeout()
        data = graphql(query, variables, token)
        rate = data.get("rateLimit")
        if (
            not isinstance(rate, dict)
            or isinstance(rate.get("cost"), bool) or not isinstance(rate.get("cost"), int)
            or isinstance(rate.get("remaining"), bool) or not isinstance(rate.get("remaining"), int)
            or not isinstance(rate.get("resetAt"), str) or not rate["resetAt"]
            or rate["cost"] <= 0 or rate["remaining"] < 0
        ):
            raise RuntimeError("GraphQL rate-limit identity missing")
        rate_limits.append({"cost": rate["cost"], "remaining": rate["remaining"], "reset_at": rate["resetAt"]})
        return data

    def list_rows(query: str) -> tuple[list[dict[str, object]], int]:
        result: list[dict[str, object]] = []
        cursor: str | None = None
        expected_total: int | None = None
        seen_cursors: set[str] = set()
        while True:
            data = checked_graphql(query, {"cursor": cursor})
            repository = data.get("repository")
            if not isinstance(repository, dict):
                raise RuntimeError("GraphQL repository missing")
            connection = repository.get("pullRequests")
            nodes, more, cursor = page_info(connection, "open pulls")
            total = connection.get("totalCount") if isinstance(connection, dict) else None
            if isinstance(total, bool) or not isinstance(total, int) or total < 0:
                raise RuntimeError("open-pull totalCount missing")
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise RuntimeError("open-pull totalCount mutated during pagination")
            result.extend(nodes)
            if more:
                if cursor in seen_cursors:
                    raise RuntimeError("repeated open-pull pagination cursor")
                seen_cursors.add(cursor)
            if not more:
                if len(result) != expected_total:
                    raise RuntimeError("open-pull pagination truncated")
                return result, expected_total

    def identity(row: dict[str, object]) -> dict[str, object]:
        head_repo = row.get("headRepository")
        base_repo = row.get("baseRepository")
        required_strings = ("id", "state", "title", "updatedAt", "headRefOid", "headRefName", "baseRefOid", "baseRefName")
        if (
            any(not isinstance(row.get(key), str) or not row[key] for key in required_strings)
            or row.get("state") != "OPEN"
            or any(len(row[key]) != 40 or any(c not in "0123456789abcdef" for c in row[key]) for key in ("headRefOid", "baseRefOid"))
            or isinstance(row.get("number"), bool) or not isinstance(row.get("number"), int) or row["number"] <= 0
            or not isinstance(row.get("isDraft"), bool)
            or isinstance(row.get("changedFiles"), bool) or not isinstance(row.get("changedFiles"), int) or row["changedFiles"] < 0
            or (head_repo is not None and (not isinstance(head_repo, dict) or not isinstance(head_repo.get("nameWithOwner"), str)))
            or not isinstance(base_repo, dict) or not isinstance(base_repo.get("nameWithOwner"), str)
        ):
            raise RuntimeError("open-pull identity type/null/state drift")
        return {
            "node_id": row["id"],
            "number": row["number"],
            "state": row["state"],
            "title": row["title"],
            "draft": row["isDraft"],
            "updated_at": row["updatedAt"],
            "head_sha": row["headRefOid"],
            "head_ref": row["headRefName"],
            "head_repo": head_repo.get("nameWithOwner") if isinstance(head_repo, dict) else None,
            "base_sha": row["baseRefOid"],
            "base_ref": row["baseRefName"],
            "base_repo": base_repo.get("nameWithOwner") if isinstance(base_repo, dict) else None,
            "changed_files": row["changedFiles"],
        }

    rows, open_total = list_rows(OPEN_PULL_QUERY)
    if len({int(row["number"]) for row in rows}) != len(rows):
        raise RuntimeError("duplicate open-pull identity")

    def complete(row: dict[str, object]) -> dict[str, object]:
        number = int(row["number"])
        connection = row.get("files")
        nodes, more, cursor = page_info(connection, f"pull {number} files")
        file_total = connection.get("totalCount") if isinstance(connection, dict) else None
        changed_total = row.get("changedFiles")
        if isinstance(file_total, bool) or not isinstance(file_total, int) or file_total < 0 or file_total != changed_total:
            raise RuntimeError("pull changedFiles/files totalCount mismatch")
        file_nodes_all = list(nodes)
        seen_file_cursors: set[str] = set()
        while more:
            if cursor in seen_file_cursors:
                raise RuntimeError("repeated pull-file pagination cursor")
            seen_file_cursors.add(cursor)
            data = checked_graphql(MORE_FILES_QUERY, {"number": number, "cursor": cursor})
            repository = data.get("repository")
            pull = repository.get("pullRequest") if isinstance(repository, dict) else None
            if (
                not isinstance(pull, dict)
                or isinstance(pull.get("number"), bool) or not isinstance(pull.get("number"), int) or pull["number"] != number
                or isinstance(pull.get("changedFiles"), bool) or not isinstance(pull.get("changedFiles"), int)
                or pull.get("updatedAt") != row.get("updatedAt")
                or pull.get("headRefOid") != row.get("headRefOid")
                or pull.get("baseRefOid") != row.get("baseRefOid")
                or pull.get("changedFiles") != changed_total
            ):
                raise RuntimeError("pull mutated during changed-file pagination")
            file_nodes, more, cursor = page_info(pull.get("files"), f"pull {number} files")
            paged_total = pull["files"].get("totalCount")
            if isinstance(paged_total, bool) or not isinstance(paged_total, int) or paged_total != file_total:
                raise RuntimeError("pull file totalCount drift")
            file_nodes_all.extend(file_nodes)
        allowed_change_types = {"ADDED", "CHANGED", "COPIED", "DELETED", "MODIFIED", "RENAMED"}
        if any(
            not isinstance(node.get("path"), str) or not node["path"]
            or not isinstance(node.get("changeType"), str) or node["changeType"] not in allowed_change_types
            for node in file_nodes_all
        ):
            raise RuntimeError("pull file path/changeType type drift")
        paths = [node["path"] for node in file_nodes_all]
        if len(paths) != file_total or len(set(paths)) != file_total:
            raise RuntimeError("duplicate, truncated, or noncanonical changed path")
        paths.sort()
        if any(node.get("changeType") == "RENAMED" for node in file_nodes_all):
            rest_rows: list[dict[str, object]] = []
            page = 1
            while True:
                page_rows = api(f"/repos/google-deepmind/formal-conjectures/pulls/{number}/files?per_page=100&page={page}", token)
                if not isinstance(page_rows, list) or any(not isinstance(item, dict) for item in page_rows):
                    raise RuntimeError("renamed-file REST fallback shape drift")
                rest_rows.extend(page_rows)
                if len(page_rows) < 100:
                    break
                page += 1
            if len(rest_rows) != file_total or sorted(str(item.get("filename")) for item in rest_rows) != sorted(paths):
                raise RuntimeError("renamed-file REST fallback does not bind GraphQL paths")
            graphql_renamed = {node["path"] for node in file_nodes_all if node["changeType"] == "RENAMED"}
            rest_renamed = {item.get("filename") for item in rest_rows if item.get("status") == "renamed"}
            if graphql_renamed != rest_renamed:
                raise RuntimeError("GraphQL/REST renamed-file classification mismatch")
            for item in rest_rows:
                if item.get("filename") in graphql_renamed:
                    previous = item.get("previous_filename")
                    if not isinstance(previous, str) or not previous:
                        raise RuntimeError("renamed-away path unavailable")
                    paths.append(previous)
        paths = sorted(paths)
        if paths != sorted(set(paths)):
            raise RuntimeError("duplicate or noncanonical changed path")
        return {
            **identity(row),
            "changed_paths": paths,
            "changed_paths_sha256": canonical_sha256(paths),
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=SNAPSHOT_WORKERS) as pool:
        bindings = list(pool.map(complete, rows))
    bindings.sort(key=lambda row: int(row["number"]))
    initial_identities = sorted((identity(row) for row in rows), key=lambda row: int(row["number"]))
    final_rows, final_total = list_rows(OPEN_PULL_IDENTITY_QUERY)
    final_identities = sorted((identity(row) for row in final_rows), key=lambda row: int(row["number"]))
    if open_total != final_total or initial_identities != final_identities:
        raise RuntimeError("open-pull set or identity mutated during bracket pagination")
    identity_keys = (
        "node_id", "number", "state", "title", "draft", "updated_at", "head_sha", "head_ref", "head_repo",
        "base_sha", "base_ref", "base_repo", "changed_files",
    )
    if [{key: row[key] for key in identity_keys} for row in bindings] != initial_identities:
        raise RuntimeError("changed-file bindings do not match bracket identities")
    return {"total_count": open_total, "bindings": bindings, "rate_limits": rate_limits}


def get_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "c5-k4-bondy-frozen-gate"})
    with urllib.request.urlopen(request, timeout=remaining_timeout()) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, timeout=remaining_timeout()).strip()


def validate_local_contamination(hits: list[str]) -> tuple[bool, list[dict[str, object]]]:
    identities: list[dict[str, object]] = []
    allowed_roots = (
        "scripts/prospective_bondy_",
        "scripts/test_bondy_",
        "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/",
        ".github/workflows/bondy-longest-cycles-development.yml",
    )
    freeze_introducers = 0
    for commit in hits:
        subject = git("show", "-s", "--format=%s", commit)
        paths = sorted(git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines())
        if commit == KNOWN_PREFLIGHT_COMMIT:
            kind = "known_preflight"
        elif commit == KNOWN_REPIN_AUDIT_COMMIT:
            kind = "known_repin_audit"
            if subject != "research: audit Bondy upstream repin" or paths != [KNOWN_REPIN_AUDIT_PATH]:
                return False, identities
        elif commit == KNOWN_CONTINUITY_AUDIT_COMMIT:
            kind = "known_continuity_audit"
            if subject != "research: define Bondy tip continuity gate" or paths != [KNOWN_CONTINUITY_AUDIT_PATH]:
                return False, identities
        else:
            kind = "freeze_introducer"
        if kind == "freeze_introducer":
            freeze_introducers += 1
            if not paths or not all(any(path.startswith(root) for root in allowed_roots) for path in paths):
                return False, identities
            if "scripts/prospective_bondy_gate.py" not in paths:
                return False, identities
        identities.append({"commit": commit, "subject": subject, "paths": paths, "kind": kind})
    return (
        KNOWN_PREFLIGHT_COMMIT in hits
        and KNOWN_REPIN_AUDIT_COMMIT in hits
        and KNOWN_CONTINUITY_AUDIT_COMMIT in hits
        and freeze_introducers <= 2
    ), identities


def atomic_json(path: Path, value: object) -> None:
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def changed_paths(token: str, number: int) -> list[str]:
    paths: list[str] = []
    page = 1
    while True:
        rows = api(f"/repos/google-deepmind/formal-conjectures/pulls/{number}/files?per_page=100&page={page}", token)
        if not isinstance(rows, list):
            raise RuntimeError("pull-file response is not a list")
        paths.extend(str(row["filename"]) for row in rows)
        if len(rows) < 100:
            return paths
        page += 1


def all_open_pulls(token: str) -> list[dict[str, object]]:
    pulls: list[dict[str, object]] = []
    page = 1
    while True:
        rows = api(f"/repos/google-deepmind/formal-conjectures/pulls?state=open&per_page=100&page={page}", token)
        if not isinstance(rows, list):
            raise RuntimeError("open-pull response is not a list")
        pulls.extend(rows)
        if len(rows) < 100:
            return pulls
        page += 1


def canonical_sha256(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def local_git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=not binary, timeout=remaining_timeout()
    )


def git_entry(repo: Path, commit: str, path: str) -> tuple[dict[str, object], bytes]:
    listing = str(local_git(repo, "ls-tree", commit, "--", path)).strip().split()
    if len(listing) != 4 or listing[3] != path:
        raise RuntimeError(f"missing or ambiguous Git tree entry: {path}")
    raw = bytes(local_git(repo, "show", f"{commit}:{path}", binary=True))
    return {
        "path": path,
        "mode": listing[0],
        "type": listing[1],
        "blob": listing[2],
        "bytes": len(raw),
        "sha256": sha256(raw),
    }, raw


def resolve_import_closure(
    repo: Path, commit: str, root: str, external_prefixes: tuple[str, ...] = ("Mathlib", "Lean")
) -> list[dict[str, object]]:
    seen: set[str] = set()
    pending = [root]
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        entry, raw = git_entry(repo, commit, path)
        if entry["mode"] != "100644" or entry["type"] != "blob":
            raise RuntimeError("semantic closure contains a non-regular blob")
        seen.add(path)
        for line in raw.decode("utf-8").splitlines():
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("public import ")):
                continue
            match = re.fullmatch(r"(?:public\s+)?import\s+([A-Za-z0-9_.]+)", stripped)
            if match is None:
                raise RuntimeError("ambiguous Lean import syntax in semantic closure")
            module = match.group(1)
            imported = module.replace(".", "/") + ".lean"
            exists = subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{imported}"],
                capture_output=True,
                timeout=remaining_timeout(),
            ).returncode == 0
            if exists:
                pending.append(imported)
            elif module.startswith("FormalConjectures"):
                raise RuntimeError("unresolved in-repository Lean import")
            elif not any(module == prefix or module.startswith(prefix + ".") for prefix in external_prefixes):
                raise RuntimeError("unfrozen external Lean import prefix")
    return [git_entry(repo, commit, path)[0] for path in sorted(seen)]


def exact_declaration_shape(raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8")
    declarations = list(re.finditer(r"(?m)^theorem\s+bondy_conjecture\s*:", text))
    exact_block = re.findall(
        r"(?ms)^@\[category research open, AMS 5\]\n"
        r"theorem bondy_conjecture\s*:.*?answer\(sorry\)\s*↔.*?:= by\n  sorry\n",
        text,
    )
    result = {
        "declaration_count": len(declarations),
        "exact_open_attribute_count": text.count("@[category research open, AMS 5]\ntheorem bondy_conjecture"),
        "answer_wrapper_count": text.count("answer(sorry) ↔"),
        "exact_by_sorry_block_count": len(exact_block),
    }
    if result != {
        "declaration_count": 1,
        "exact_open_attribute_count": 1,
        "answer_wrapper_count": 1,
        "exact_by_sorry_block_count": 1,
    }:
        raise RuntimeError("Bondy declaration/category/wrapper/sorry shape drift")
    return result


def require_ancestor(repo: Path, pinned: str, live: str) -> str:
    if subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", pinned, live],
        timeout=remaining_timeout(),
    ).returncode != 0:
        raise RuntimeError("frozen commit is not an ancestor of live main")
    merge_base = str(local_git(repo, "merge-base", pinned, live)).strip()
    if merge_base != pinned:
        raise RuntimeError("live history merge-base drift")
    return merge_base


def prepare_continuity(live_commit: str, live_tree: str) -> dict[str, object]:
    frozen = json.loads(SEMANTIC_CLOSURE.read_text())
    if (
        frozen.get("schema") != "bondy_semantic_closure_v3"
        or frozen.get("pinned_commit") != UPSTREAM_COMMIT
        or frozen.get("pinned_tree") != UPSTREAM_TREE
        or frozen.get("root") != TARGET_PATH
        or frozen.get("resolution") != {
            "external_import_prefixes": ["Mathlib", "Lean"],
            "module_to_path": "dot_to_slash_plus_dot_lean",
            "syntax": "exact_single_module_import_per_line",
        }
        or frozen.get("closure_count") != len(frozen.get("entries", []))
        or frozen.get("toolchain_count") != len(frozen.get("toolchain", []))
        or canonical_sha256(frozen.get("entries")) != frozen.get("closure_sha256")
        or canonical_sha256(frozen.get("toolchain")) != frozen.get("toolchain_sha256")
        or canonical_sha256(frozen.get("external_revisions")) != frozen.get("external_revisions_sha256")
    ):
        raise RuntimeError("semantic closure freeze missing or wrong schema")
    with tempfile.TemporaryDirectory(prefix="bondy-v3-upstream-") as directory:
        repo = Path(directory)
        subprocess.run(["git", "init", "-q", str(repo)], check=True, timeout=remaining_timeout(10))
        subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", UPSTREAM_URL], check=True, timeout=remaining_timeout(10))
        subprocess.run(
            ["git", "-C", str(repo), "fetch", "-q", "--no-tags", "--depth=256", "origin", UPSTREAM_COMMIT, live_commit],
            check=True, timeout=remaining_timeout(),
        )
        pinned_commit_tree = str(local_git(repo, "show", "-s", "--format=%T", UPSTREAM_COMMIT)).strip()
        fetched_live_tree = str(local_git(repo, "show", "-s", "--format=%T", live_commit)).strip()
        if pinned_commit_tree != UPSTREAM_TREE or fetched_live_tree != live_tree:
            raise RuntimeError("pinned or live root-tree identity drift")
        merge_base = require_ancestor(repo, UPSTREAM_COMMIT, live_commit)

        prefixes = tuple(frozen["resolution"]["external_import_prefixes"])
        pinned_closure = resolve_import_closure(repo, UPSTREAM_COMMIT, frozen["root"], prefixes)
        live_closure = resolve_import_closure(repo, live_commit, frozen["root"], prefixes)
        if pinned_closure != frozen["entries"] or live_closure != frozen["entries"]:
            raise RuntimeError("pinned or live semantic import closure drift")
        toolchain: list[dict[str, object]] = []
        expected_toolchain_paths = sorted(entry["path"] for entry in frozen["toolchain"])
        for checked_commit in (UPSTREAM_COMMIT, live_commit):
            root_names = str(local_git(repo, "ls-tree", "--name-only", checked_commit)).splitlines()
            discovered = sorted(path for path in root_names if path == "lean-toolchain" or path == "lake-manifest.json" or path.startswith("lakefile."))
            if discovered != expected_toolchain_paths:
                raise RuntimeError("added, removed, or renamed root toolchain/lock file")
        for expected in frozen["toolchain"]:
            pinned_entry, _ = git_entry(repo, UPSTREAM_COMMIT, expected["path"])
            live_entry, _ = git_entry(repo, live_commit, expected["path"])
            if pinned_entry != expected or live_entry != expected:
                raise RuntimeError("pinned or live toolchain/lock drift")
            toolchain.append(live_entry)
        _, live_manifest_raw = git_entry(repo, live_commit, "lake-manifest.json")
        packages = json.loads(live_manifest_raw)["packages"]
        external = [
            {key: package.get(key) for key in ("name", "scope", "type", "url", "rev", "inputRev", "subDir", "configFile")}
            for package in packages
        ]
        external.sort(key=lambda row: str(row["name"]))
        if external != frozen["external_revisions"]:
            raise RuntimeError("external dependency revision drift")
        if canonical_sha256(external) != frozen["external_revisions_sha256"]:
            raise RuntimeError("external dependency revision digest drift")

        target_entry, target_raw = git_entry(repo, live_commit, TARGET_PATH)
        frozen_target = next((entry for entry in frozen["entries"] if entry["path"] == TARGET_PATH), None)
        pinned_target_entry, pinned_target_raw = git_entry(repo, UPSTREAM_COMMIT, TARGET_PATH)
        if frozen_target is None or pinned_target_entry != frozen_target or target_entry != frozen_target or target_raw != pinned_target_raw:
            raise RuntimeError("live target entry or raw bytes drift")
        declaration = exact_declaration_shape(target_raw)

        diff_raw = bytes(local_git(repo, "diff", "--name-status", "-z", "--no-renames", UPSTREAM_COMMIT, live_commit, binary=True))
        delta = []
        fields = diff_raw.split(b"\0")
        if fields[-1:] != [b""] or (len(fields) - 1) % 2:
            raise RuntimeError("complete local Git NUL diff parse failure")
        for index in range(0, len(fields) - 1, 2):
            status = fields[index].decode("ascii")
            path = fields[index + 1].decode("utf-8")
            if status not in {"A", "M", "D", "T", "U"} or not path:
                raise RuntimeError("complete local Git diff parse failure")
            delta.append({"status": status, "path": path})
        delta.sort(key=lambda row: (row["path"], row["status"]))
        protected = {entry["path"] for entry in frozen["entries"] + frozen["toolchain"]}
        if any(row["path"] in protected for row in delta):
            raise RuntimeError("live delta intersects semantic closure or toolchain")

        commits = []
        revs = str(local_git(repo, "rev-list", "--reverse", "--parents", f"{UPSTREAM_COMMIT}..{live_commit}")).splitlines()
        for line in revs:
            fields = line.split()
            commit = fields[0]
            if len(fields) != 2:
                raise RuntimeError("merge commit in live continuity range requires parent-indexed provenance")
            commit_path_raw = bytes(local_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-z", "--no-renames", "-r", commit, binary=True))
            commit_path_fields = commit_path_raw.split(b"\0")
            if commit_path_fields[-1:] != [b""]:
                raise RuntimeError("per-commit NUL path provenance parse failure")
            commit_paths = sorted(field.decode("utf-8") for field in commit_path_fields[:-1])
            if not commit_paths or commit_paths != sorted(set(commit_paths)):
                raise RuntimeError("empty, duplicate, or noncanonical per-commit path provenance")
            commits.append({
                "commit": commit,
                "parents": fields[1:],
                "tree": str(local_git(repo, "show", "-s", "--format=%T", commit)).strip(),
                "subject": str(local_git(repo, "show", "-s", "--format=%s", commit)).strip(),
                "changed_paths": commit_paths,
            })
        if not commits and live_commit != UPSTREAM_COMMIT:
            raise RuntimeError("descendant history enumeration is incomplete")
        return {
            "pinned": {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE},
            "live": {"commit": live_commit, "tree": live_tree},
            "merge_base": merge_base,
            "ancestor_verified": True,
            "commits": commits,
            "delta": delta,
            "delta_sha256": canonical_sha256(delta),
            "target": target_entry,
            "target_raw_utf8": target_raw.decode("utf-8"),
            "declaration": declaration,
            "closure_count": frozen["closure_count"],
            "closure_sha256": frozen["closure_sha256"],
            "closure_entries": frozen["entries"],
            "toolchain_sha256": frozen["toolchain_sha256"],
            "toolchain": toolchain,
            "external_revisions_sha256": frozen["external_revisions_sha256"],
            "external_revisions": external,
            "protected_paths": sorted(protected),
        }


def pull_identity(pull: dict[str, object]) -> dict[str, object]:
    return {
        "number": int(pull["number"]),
        "title": str(pull["title"]),
        "draft": bool(pull.get("draft", False)),
        "updated_at": str(pull["updated_at"]),
        "head_sha": str(pull["head"]["sha"]),
        "head_ref": str(pull["head"]["ref"]),
        "head_repo": pull["head"].get("repo", {}).get("full_name") if pull["head"].get("repo") else None,
        "base_sha": str(pull["base"]["sha"]),
        "base_ref": str(pull["base"]["ref"]),
        "base_repo": pull["base"].get("repo", {}).get("full_name") if pull["base"].get("repo") else None,
    }


def open_pull_identities(pulls: list[dict[str, object]]) -> list[dict[str, object]]:
    ordered = sorted(pulls, key=lambda row: int(row["number"]))
    if len({int(pull["number"]) for pull in ordered}) != len(ordered):
        raise RuntimeError("duplicate open-pull identity")
    return [pull_identity(pull) for pull in ordered]


def bind_changed_paths(
    token: str,
    identities: list[dict[str, object]],
    executor: concurrent.futures.Executor | None = None,
) -> list[dict[str, object]]:
    ordered = sorted(identities, key=lambda row: int(row["number"]))
    if ordered != identities or len({int(pull["number"]) for pull in ordered}) != len(ordered):
        raise RuntimeError("changed paths require canonical open-pull identities")
    owned = executor is None
    pool = executor or concurrent.futures.ThreadPoolExecutor(max_workers=SNAPSHOT_WORKERS)
    futures = {int(pull["number"]): pool.submit(changed_paths, token, int(pull["number"])) for pull in ordered}
    snapshot: list[dict[str, object]] = []
    try:
        # Resolve by PR number rather than completion order, so scheduling can
        # never affect canonical attestation bytes. Worker errors propagate.
        for pull in ordered:
            paths = sorted(futures[int(pull["number"])].result())
            snapshot.append({**pull, "changed_paths": paths, "changed_paths_sha256": canonical_sha256(paths)})
        return snapshot
    finally:
        if owned:
            pool.shutdown(wait=True, cancel_futures=True)


def issue_search(token: str, query: str) -> list[int]:
    result = api("/search/issues?q=" + urllib.parse.quote(query) + "&per_page=100", token)
    if not isinstance(result, dict) or result.get("incomplete_results") is not False:
        raise RuntimeError("incomplete or unexpectedly large issue/PR search")
    total = result.get("total_count")
    items = result.get("items")
    if (
        isinstance(total, bool) or not isinstance(total, int) or not 0 <= total <= 100
        or not isinstance(items, list) or len(items) != total
        or any(not isinstance(item, dict) or isinstance(item.get("number"), bool) or not isinstance(item.get("number"), int) or item["number"] <= 0 for item in items)
    ):
        raise RuntimeError("issue/PR search count or item schema drift")
    numbers = sorted(item["number"] for item in items)
    if numbers != sorted(set(numbers)):
        raise RuntimeError("duplicate issue/PR search identity")
    return numbers


def continuity_surface(continuity: dict[str, object]) -> dict[str, object]:
    """Compact exact binding to the one canonical continuity object."""
    return {
        "canonical_sha256": canonical_sha256(continuity),
        "live": continuity["live"],
        "target": continuity["target"],
        "target_raw_bytes": len(continuity["target_raw_utf8"].encode("utf-8")),
        "target_raw_sha256": sha256(continuity["target_raw_utf8"].encode("utf-8")),
        "declaration": continuity["declaration"],
        "closure_count": continuity["closure_count"],
        "closure_sha256": continuity["closure_sha256"],
        "toolchain_sha256": continuity["toolchain_sha256"],
        "external_revisions_sha256": continuity["external_revisions_sha256"],
    }


def bracket_snapshot(token: str, continuity: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    repo = "/repos/google-deepmind/formal-conjectures"
    with concurrent.futures.ThreadPoolExecutor(max_workers=SNAPSHOT_WORKERS) as pool:
        main_future = pool.submit(api, repo + "/commits/main", token)
        search_futures = {query: pool.submit(issue_search, token, query) for query in SEARCH_QUERIES}
        bindings_future = pool.submit(graphql_open_pull_bindings, token)
        issue_future = pool.submit(api, repo + f"/issues/{KNOWN_ISSUE}", token)
        pull_future = pool.submit(api, repo + f"/pulls/{KNOWN_PR}", token)
        repositories_future = pool.submit(
            api,
            "/search/repositories?q=" + urllib.parse.quote('"Bondy" "longest cycles" counterexample') + "&per_page=100",
            token,
        )
        main = main_future.result()
        binding_surface = bindings_future.result()
        issue = issue_future.result()
        pull = pull_future.result()
        searches = {query: search_futures[query].result() for query in SEARCH_QUERIES}
        repositories = repositories_future.result()
    if not isinstance(main, dict) or not isinstance(main.get("tree"), dict):
        raise RuntimeError("main-commit response is not an object")
    if not isinstance(issue, dict) or not isinstance(pull, dict) or not isinstance(repositories, dict):
        raise RuntimeError("known issue/PR or repository-search response is not an object")
    if issue.get("number") != KNOWN_ISSUE or pull.get("number") != KNOWN_PR:
        raise RuntimeError("known issue/PR identity drift")
    if not isinstance(pull.get("head"), dict) or not isinstance(pull.get("base"), dict):
        raise RuntimeError("known PR ref identity missing")
    if not isinstance(pull.get("user"), dict) or not isinstance(issue.get("user"), dict):
        raise RuntimeError("known issue/PR author identity missing")
    issue_strings = (issue.get("title"), issue["user"].get("login"), issue.get("created_at"), issue.get("updated_at"), issue.get("closed_at"), issue.get("node_id"))
    pull_strings = (
        pull.get("title"), pull["user"].get("login"), pull.get("merged_at"), pull.get("merge_commit_sha"),
        pull["head"].get("sha"), pull["base"].get("sha"), pull.get("updated_at"), pull.get("node_id"),
    )
    if any(not isinstance(value, str) or not value for value in issue_strings + pull_strings):
        raise RuntimeError("known issue/PR exact identity field missing")
    if not isinstance(repositories, dict):
        raise RuntimeError("repository-search response is not an object")
    if repositories.get("incomplete_results") is not False:
        raise RuntimeError("incomplete standalone-repository search")
    if (
        not isinstance(main.get("sha"), str) or len(main["sha"]) != 40
        or not isinstance(main["tree"].get("sha"), str) or len(main["tree"]["sha"]) != 40
        or isinstance(repositories.get("total_count"), bool) or not isinstance(repositories.get("total_count"), int)
    ):
        raise RuntimeError("live main or repository count type drift")
    snapshot = {
        "main": {"commit": main.get("sha"), "tree": main["tree"].get("sha")},
        "continuity": continuity_surface(continuity),
        "known_issue": {
            "number": issue.get("number"), "state": issue.get("state"), "state_reason": issue.get("state_reason"),
            "title": issue.get("title"), "author": issue["user"].get("login"),
            "created_at": issue.get("created_at"), "updated_at": issue.get("updated_at"), "closed_at": issue.get("closed_at"),
            "node_id": issue.get("node_id"),
            "is_pull_request": "pull_request" in issue,
        },
        "known_pr": {
            "number": pull.get("number"), "state": pull.get("state"), "draft": pull.get("draft"), "merged": pull.get("merged"),
            "merged_at": pull.get("merged_at"), "merge_commit_sha": pull.get("merge_commit_sha"),
            "title": pull.get("title"), "author": pull["user"].get("login"),
            "head_sha": pull["head"].get("sha"), "base_sha": pull["base"].get("sha"),
            "updated_at": pull.get("updated_at"), "node_id": pull.get("node_id"),
        },
        "searches": searches,
        "open_pull_binding_surface": {"total_count": binding_surface["total_count"], "bindings": binding_surface["bindings"]},
        "repository_total_count": int(repositories.get("total_count", -1)),
    }
    return snapshot, binding_surface["rate_limits"]


def run(output: Path, token: str, paper: Path | None) -> dict[str, object]:
    global ACTIVE_DEADLINE
    ACTIVE_DEADLINE = time.monotonic() + 58.0
    if not token:
        raise RuntimeError("GH_TOKEN is required; source/status gate fails closed")
    repo = "/repos/google-deepmind/formal-conjectures"
    preliminary = api(repo + "/commits/main", token)
    if not isinstance(preliminary, dict) or not isinstance(preliminary.get("tree"), dict):
        raise RuntimeError("live main identity unavailable")
    live_commit = preliminary.get("sha")
    live_tree = preliminary["tree"].get("sha")
    if not isinstance(live_commit, str) or not isinstance(live_tree, str):
        raise RuntimeError("live main commit/tree unavailable")
    continuity = prepare_continuity(live_commit, live_tree)
    before, before_rate_limits = bracket_snapshot(token, continuity)
    before_cost = sum(row["cost"] for row in before_rate_limits)
    if not before_rate_limits or min(row["remaining"] for row in before_rate_limits) < before_cost + 25:
        raise RuntimeError("insufficient GraphQL reserve for complete second bracket")
    protected = set(continuity["protected_paths"])
    touching = [
        {"number": int(pull["number"]), "paths": sorted(protected.intersection(pull["changed_paths"]))}
        for pull in before["open_pull_binding_surface"]["bindings"] if protected.intersection(pull["changed_paths"])
    ]
    local_hits = git("log", "--all", "--format=%H", "-Sbondy_conjecture", "--", ".").splitlines()
    local_ok, local_identities = validate_local_contamination(local_hits)
    after, after_rate_limits = bracket_snapshot(token, continuity)
    if not after_rate_limits or min(row["remaining"] for row in after_rate_limits) < 25:
        raise RuntimeError("GraphQL post-bracket safety reserve exhausted")
    expected_issue = before["known_issue"]
    expected_pr = before["known_pr"]
    checks = {
        "bracket_snapshot_stable": before == after,
        "live_main_stable": before["main"] == continuity["live"],
        "historical_anchor_exact": continuity["pinned"] == {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE},
        "frozen_commit_is_live_ancestor": continuity["ancestor_verified"] is True and continuity["merge_base"] == UPSTREAM_COMMIT,
        "complete_delta_disjoint": not any(row["path"] in protected for row in continuity["delta"]),
        "live_target_exact": continuity["target"]["blob"] == TARGET_BLOB and continuity["target"]["sha256"] == TARGET_SHA256,
        "declaration_shape_exact": continuity["declaration"] == {"declaration_count": 1, "exact_open_attribute_count": 1, "answer_wrapper_count": 1, "exact_by_sorry_block_count": 1},
        "semantic_closure_exact": before["continuity"]["canonical_sha256"] == canonical_sha256(continuity) and canonical_sha256(continuity["closure_entries"]) == continuity["closure_sha256"],
        "toolchain_and_external_revisions_exact": canonical_sha256(continuity["toolchain"]) == continuity["toolchain_sha256"] and canonical_sha256(continuity["external_revisions"]) == continuity["external_revisions_sha256"],
        "complete_open_pr_bindings": before["open_pull_binding_surface"]["total_count"] == len(before["open_pull_binding_surface"]["bindings"]),
        "no_open_pr_touches_protected_paths": touching == [],
        "exact_allowed_search_result_sets": before["searches"] == ALLOWED_SEARCH_RESULTS,
        "known_ingestion_issue_exact": expected_issue["number"] == KNOWN_ISSUE and expected_issue["state"] == "closed" and expected_issue["state_reason"] == "completed" and expected_issue["closed_at"] == KNOWN_ISSUE_CLOSED_AT and expected_issue["is_pull_request"] is False,
        "known_ingestion_pr_exact": expected_pr["number"] == KNOWN_PR and expected_pr["state"] == "closed" and expected_pr["draft"] is False and expected_pr["merged"] is True and expected_pr["merged_at"] == KNOWN_PR_MERGED_AT and expected_pr["merge_commit_sha"] == KNOWN_PR_MERGE_COMMIT,
        "exact_local_contamination_history": local_ok,
        "no_standalone_repository_hit": before["repository_total_count"] == 0,
    }
    checks["paper_sha256"] = paper is not None and paper.is_file() and sha256(paper.read_bytes()) == PAPER_SHA256
    record = {
        "schema": "bondy_source_status_duplicate_gate_tip_continuity_v3",
        "kind": "source_status_duplicate_gate",
        "status": "PASS" if all(checks.values()) else "GATE_FAIL",
        "checks": checks,
        "campaign": {"commit": git("rev-parse", "HEAD"), "tree": git("show", "-s", "--format=%T", "HEAD")},
        "pinned_upstream": {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE, "path": TARGET_PATH, "blob": TARGET_BLOB},
        "live_upstream": continuity["live"],
        "continuity": continuity,
        "open_pr_protected_path_matches": touching,
        "bracket_snapshot_before": before,
        "bracket_snapshot_after": after,
        "graphql_rate_limit_observations": {
            "before": sorted(before_rate_limits, key=lambda row: (row["remaining"], row["cost"], row["reset_at"])),
            "after": sorted(after_rate_limits, key=lambda row: (row["remaining"], row["cost"], row["reset_at"])),
        },
        "local_history_hits": local_hits,
        "local_history_identities": local_identities,
    }
    atomic_json(output, record)
    if record["status"] != "PASS":
        raise RuntimeError("source/status/duplicate gate failed closed")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--paper", type=Path, required=True)
    args = parser.parse_args()
    run(args.output, os.environ.get("GH_TOKEN", ""), args.paper)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
