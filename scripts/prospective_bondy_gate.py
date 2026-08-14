#!/usr/bin/env python3
"""Immutable source/status/duplicate gate; never evaluates a graph target."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

UPSTREAM_COMMIT = "5a5af706fa5bef3f09606554d393c9170d2b27e8"
UPSTREAM_TREE = "0ef534e06d27e22e68e4cfd5081f2a5e28ebe73a"
TARGET_PATH = "FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean"
TARGET_BLOB = "c4c5cb1983936860d5a4a7208b3f04bd201290d4"
TARGET_SHA256 = "562fbbb0ec47041a61017bb85ec0c7e9aa6fc98cf132be3022268a7dc60e9004"
PAPER_SHA256 = "56213cd6384cc2111864d67150c41e1426608c59b1b009c6752acab9be3487fb"
KNOWN_ISSUE = 4858
KNOWN_PR = 4879
KNOWN_PREFLIGHT_COMMIT = "d22eb07173794848fd375b5675059946ee3860b5"
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
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def get_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "c5-k4-bondy-frozen-gate"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


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
        paths = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        kind = "known_preflight" if commit == KNOWN_PREFLIGHT_COMMIT else "freeze_introducer"
        if kind == "freeze_introducer":
            freeze_introducers += 1
            if not paths or not all(any(path.startswith(root) for root in allowed_roots) for path in paths):
                return False, identities
            if "scripts/prospective_bondy_gate.py" not in paths:
                return False, identities
        identities.append({"commit": commit, "subject": subject, "paths": paths, "kind": kind})
    return KNOWN_PREFLIGHT_COMMIT in hits and freeze_introducers <= 1, identities


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
    if not isinstance(result, dict) or result.get("incomplete_results") is not False or int(result.get("total_count", -1)) > 100:
        raise RuntimeError("incomplete or unexpectedly large issue/PR search")
    return sorted(int(item["number"]) for item in result.get("items", []))


def bracket_snapshot(token: str) -> dict[str, object]:
    repo = "/repos/google-deepmind/formal-conjectures"
    with concurrent.futures.ThreadPoolExecutor(max_workers=SNAPSHOT_WORKERS) as pool:
        main_future = pool.submit(api, repo + "/commits/main", token)
        search_futures = {query: pool.submit(issue_search, token, query) for query in SEARCH_QUERIES}
        pulls_future = pool.submit(all_open_pulls, token)
        repositories_future = pool.submit(
            api,
            "/search/repositories?q=" + urllib.parse.quote('"Bondy" "longest cycles" counterexample') + "&per_page=100",
            token,
        )
        pulls = open_pull_identities(pulls_future.result())
        main = main_future.result()
        searches = {query: search_futures[query].result() for query in SEARCH_QUERIES}
        repositories = repositories_future.result()
    if not isinstance(main, dict):
        raise RuntimeError("main-commit response is not an object")
    if not isinstance(repositories, dict):
        raise RuntimeError("repository-search response is not an object")
    if repositories.get("incomplete_results") is not False:
        raise RuntimeError("incomplete standalone-repository search")
    return {
        "main": main.get("sha"),
        "searches": searches,
        "open_pulls": pulls,
        "repository_total_count": int(repositories.get("total_count", -1)),
    }


def run(output: Path, token: str, paper: Path | None) -> dict[str, object]:
    if not token:
        raise RuntimeError("GH_TOKEN is required; source/status gate fails closed")
    repo = "/repos/google-deepmind/formal-conjectures"
    before = bracket_snapshot(token)
    file_bindings = bind_changed_paths(token, before["open_pulls"])
    commit = api(repo + "/git/commits/" + UPSTREAM_COMMIT, token)
    target = get_bytes(
        "https://raw.githubusercontent.com/google-deepmind/formal-conjectures/"
        + UPSTREAM_COMMIT + "/" + TARGET_PATH
    )
    blob = api(repo + "/git/blobs/" + TARGET_BLOB, token)
    touching = [int(pull["number"]) for pull in file_bindings if TARGET_PATH in pull["changed_paths"]]
    issue = api(repo + f"/issues/{KNOWN_ISSUE}", token)
    pull = api(repo + f"/pulls/{KNOWN_PR}", token)
    local_hits = git("log", "--all", "--format=%H", "-Sbondy_conjecture", "--", ".").splitlines()
    local_ok, local_identities = validate_local_contamination(local_hits)
    after = bracket_snapshot(token)
    before_numbers = [int(pull["number"]) for pull in before["open_pulls"]]
    after_numbers = [int(pull["number"]) for pull in after["open_pulls"]]
    binding_identities = [
        {key: value for key, value in pull.items() if key not in ("changed_paths", "changed_paths_sha256")}
        for pull in file_bindings
    ]
    checks = {
        "bracket_snapshot_stable": before == after,
        "open_pr_set_stable": before_numbers == after_numbers,
        "file_bindings_exact": binding_identities == before["open_pulls"],
        "main_commit": before["main"] == UPSTREAM_COMMIT,
        "tree": commit.get("tree", {}).get("sha") == UPSTREAM_TREE,
        "target_sha256": sha256(target) == TARGET_SHA256,
        "blob_sha1": blob.get("sha") == TARGET_BLOB,
        "category_open": "@[category research open, AMS 5]" in target.decode("utf-8"),
        "opaque_answer_wrapper": "answer(sorry) ↔" in target.decode("utf-8"),
        "no_open_pr_touches_target": touching == [],
        "exact_allowed_search_result_sets": before["searches"] == ALLOWED_SEARCH_RESULTS,
        "known_ingestion_issue_exact": issue.get("number") == KNOWN_ISSUE and issue.get("state") == "closed" and "pull_request" not in issue,
        "known_ingestion_pr_exact": pull.get("number") == KNOWN_PR and pull.get("state") == "closed" and pull.get("merged_at") == "2026-08-14T20:25:50Z",
        "exact_local_contamination_history": local_ok,
        "no_standalone_repository_hit": before["repository_total_count"] == 0,
    }
    if paper is not None:
        checks["paper_sha256"] = paper.is_file() and sha256(paper.read_bytes()) == PAPER_SHA256
    record = {
        "schema": "bondy_source_status_duplicate_gate_bracketed_single_scan_v1",
        "kind": "source_status_duplicate_gate",
        "status": "PASS" if all(checks.values()) else "GATE_FAIL",
        "checks": checks,
        "upstream": {"commit": UPSTREAM_COMMIT, "tree": UPSTREAM_TREE, "path": TARGET_PATH, "blob": TARGET_BLOB},
        "open_pr_target_path_matches": touching,
        "bracket_snapshot_before": before,
        "open_pr_file_bindings": file_bindings,
        "bracket_snapshot_after": after,
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
    parser.add_argument("--paper", type=Path)
    args = parser.parse_args()
    run(args.output, os.environ.get("GH_TOKEN", ""), args.paper)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
