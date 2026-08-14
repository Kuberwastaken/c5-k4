#!/usr/bin/env python3
"""Prepare the immutable A067720 source/status/catalogue gate."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import shutil
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "results/expansion/live-search-2026-08-14/oeis-a067720-development"
MANIFEST = HERE / "manifest.json"
M = json.loads(MANIFEST.read_text())
SCHEMA = "oeis-a067720-gate-v1"
KNOWN_PATH_TOUCHES = {
    (4198, "1cda50fe1496260c6fe6177543542dcc7acca1fb", "7387a319aad73fae84ab7088c5b2af1bca1736755ecc07c6a0d1ce7e47112282"):
        "NON_RESOLVING_STALE_NORMALIZATION",
    (4688, "5e22a9f1dac70e763f3a33dd9eeba59dd008b03f", "301a72ec827dedbc4e31baf87bf5a61d7380dacdabf89623ada0102288d6333e"):
        "NON_RESOLVING_MODULE_MAINTENANCE",
}
SEARCH_QUERIES = {
    "upstream_sequence": 'repo:google-deepmind/formal-conjectures "A067720"',
    "upstream_declaration": 'repo:google-deepmind/formal-conjectures "prime_add_one_of_a"',
    "local_sequence": 'repo:Kuberwastaken/c5-k4 "A067720"',
    "local_declaration": 'repo:Kuberwastaken/c5-k4 "prime_add_one_of_a"',
}


def sha(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def self_hash(value: dict) -> str:
    copy = dict(value)
    copy.pop("attestation_sha256", None)
    return hashlib.sha256(canonical(copy)).hexdigest()


def atomic_json(path: pathlib.Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def exact_commit(value: str) -> str:
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("exact lowercase campaign commit required")
    return value


def is_prime_64(n: int) -> bool:
    """Deterministic Miller--Rabin for n < 2^64."""
    if n < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % prime == 0:
            return n == prime
    odd, twos = n - 1, 0
    while odd % 2 == 0:
        odd //= 2; twos += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0:
            continue
        residue = pow(base, odd, n)
        if residue in (1, n - 1):
            continue
        for _ in range(twos - 1):
            residue = residue * residue % n
            if residue == n - 1:
                break
        else:
            return False
    return True


def parse_bfile(path: pathlib.Path) -> list[tuple[int, int]]:
    if sha(path) != M["oeis_bfile"]["sha256"]:
        raise ValueError("b-file hash drift")
    rows = []
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if len(fields) != 2:
            raise ValueError("malformed b-file row")
        rows.append((int(fields[0]), int(fields[1])))
    spec = M["oeis_bfile"]
    if len(rows) != spec["rows"] or [i for i, _ in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("b-file index coverage drift")
    if list(rows[-1]) != [spec["last_index"], spec["last_value"]]:
        raise ValueError("b-file terminal row drift")
    if any(left[1] >= right[1] for left, right in zip(rows, rows[1:])):
        raise ValueError("b-file values are not strictly increasing")
    return rows


def verify_catalogue(path: pathlib.Path) -> dict:
    rows = parse_bfile(path)
    stream = hashlib.sha256(); exceptions = []
    for index, k in rows:
        successor, endpoint = k + 1, k * k + 1
        if k == 8:
            if successor != 3**2 or endpoint != 5 * 13:
                raise ValueError("known exception factorization drift")
            phi_successor, phi_endpoint = 3 * 2, 4 * 12
            exceptions.append([index, k])
            successor_status = "3^2"; endpoint_status = "5*13"
        else:
            if not is_prime_64(successor) or not is_prime_64(endpoint):
                raise ValueError(f"catalogue row {index} left prime-prime baseline")
            phi_successor, phi_endpoint = successor - 1, endpoint - 1
            successor_status = endpoint_status = "prime"
        residual = phi_endpoint - k * phi_successor
        if residual != 0:
            raise ValueError(f"catalogue row {index} fails defining equality")
        stream.update(f"{index},{k},{successor_status},{endpoint_status},{phi_successor},{phi_endpoint},0\n".encode("ascii"))
    if exceptions != [[5, 8]]:
        raise ValueError("source exception uniqueness drift")
    return {
        "rows": len(rows), "first": list(rows[0]), "last": list(rows[-1]),
        "prime_prime_rows": len(rows) - 1, "composite_successor_rows": exceptions,
        "verified_row_stream_sha256": stream.hexdigest(),
    }


def api_request(url: str, token: str, body: dict | None = None) -> dict | list:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("User-Agent", "c5-k4-a067720-gate")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def search_items(token: str, query: str) -> dict:
    encoded = urllib.parse.urlencode({"q": query, "per_page": 100})
    value = api_request(f"https://api.github.com/search/issues?{encoded}", token)
    assert isinstance(value, dict)
    if value.get("incomplete_results") is not False:
        raise ValueError(f"GitHub search incomplete for {query}")
    if value.get("total_count") != len(value.get("items", [])) or value["total_count"] > 100:
        raise ValueError(f"GitHub search truncated for {query}")
    return {"query": query, "total_count": value["total_count"], "incomplete_results": False,
            "items": [{"number": item["number"], "state": item["state"], "title": item["title"],
                       "is_pull_request": "pull_request" in item, "url": item["html_url"]}
                      for item in value["items"]]}


def touches_target(files: list[dict]) -> bool:
    target = M["formal_conjectures"]["path"]
    return any(item.get("path") == target or item.get("filename") == target or
               item.get("previousFilename") == target or item.get("previous_filename") == target
               for item in files)


def open_pull_path_matches(token: str) -> tuple[int, list[dict], list[int]]:
    query = """query($cursor:String){repository(owner:\"google-deepmind\",name:\"formal-conjectures\"){pullRequests(states:OPEN,first:100,after:$cursor){nodes{number title url headRefOid files(first:100){nodes{path changeType} pageInfo{hasNextPage}}}pageInfo{hasNextPage endCursor}}}}"""
    cursor = None; total = 0; matches = []; expanded = []
    while True:
        response = api_request("https://api.github.com/graphql", token,
                               {"query": query, "variables": {"cursor": cursor}})
        assert isinstance(response, dict)
        if response.get("errors"):
            raise ValueError(f"GitHub GraphQL errors: {response['errors']}")
        page = response["data"]["repository"]["pullRequests"]
        for pull in page["nodes"]:
            total += 1
            files = pull["files"]["nodes"]
            needs_rest = pull["files"]["pageInfo"]["hasNextPage"] or any(
                item.get("changeType") == "RENAMED" for item in files)
            if needs_rest:
                expanded.append(pull["number"]); files = []; page_number = 1
                while True:
                    page_files = api_request(
                        f"https://api.github.com/repos/google-deepmind/formal-conjectures/pulls/{pull['number']}/files?per_page=100&page={page_number}", token)
                    assert isinstance(page_files, list)
                    files.extend(page_files)
                    if len(page_files) < 100:
                        break
                    page_number += 1
            if touches_target(files):
                current_path_present = any(item.get("path") == M["formal_conjectures"]["path"] or
                                           item.get("filename") == M["formal_conjectures"]["path"] for item in files)
                content_digest = None
                if current_path_present:
                    content = api_request(
                        f"https://api.github.com/repos/google-deepmind/formal-conjectures/contents/{M['formal_conjectures']['path']}?ref={pull['headRefOid']}", token)
                    assert isinstance(content, dict)
                    raw = base64.b64decode(content["content"], validate=False)
                    content_digest = hashlib.sha256(raw).hexdigest()
                key = (pull["number"], pull["headRefOid"], content_digest)
                matches.append({"number": pull["number"], "title": pull["title"], "url": pull["url"],
                                "head_sha": pull["headRefOid"], "content_sha256": content_digest,
                                "classification": KNOWN_PATH_TOUCHES.get(
                                    key, "UNREVIEWED_RENAMED_TARGET_PATH" if not current_path_present
                                    else "UNREVIEWED_TARGET_PATH_TOUCH")})
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return total, matches, expanded


def live_audit(output: pathlib.Path, token: str) -> None:
    commit = api_request("https://api.github.com/repos/google-deepmind/formal-conjectures/commits/main", token)
    assert isinstance(commit, dict)
    total, path_matches, expanded = open_pull_path_matches(token)
    searches = {name: search_items(token, query) for name, query in SEARCH_QUERIES.items()}
    ingestion = api_request("https://api.github.com/repos/google-deepmind/formal-conjectures/pulls/1878", token)
    assert isinstance(ingestion, dict)
    known_ingestion_pull = {"number": ingestion["number"], "state": ingestion["state"],
                            "merged_at": ingestion["merged_at"], "merge_commit_sha": ingestion["merge_commit_sha"]}
    releases = []; release_page_sizes = []; page_number = 1
    while True:
        page = api_request(f"https://api.github.com/repos/Kuberwastaken/c5-k4/releases?per_page=100&page={page_number}", token)
        assert isinstance(page, list)
        release_page_sizes.append(len(page)); releases.extend(page)
        if len(page) < 100:
            break
        page_number += 1
    local_release_matches = []
    for release in releases:
        haystack = "\n".join(str(release.get(key) or "") for key in ("name", "tag_name", "body"))
        if "A067720" in haystack or "prime_add_one_of_a" in haystack:
            local_release_matches.append({"id": release["id"], "tag_name": release["tag_name"], "url": release["html_url"]})
    value = {
        "schema": "oeis-a067720-live-duplicate-audit-v1",
        "upstream_head": commit["sha"], "upstream_tree": commit["commit"]["tree"]["sha"],
        "queries": SEARCH_QUERIES, "searches": searches, "open_pull_requests_scanned": total,
        "known_ingestion_pull": known_ingestion_pull,
        "pulls_requiring_full_file_pagination": expanded,
        "open_target_path_matches": path_matches,
        "release_page_sizes": release_page_sizes, "releases_scanned": len(releases),
        "local_release_matches": local_release_matches,
    }
    atomic_json(output, value)


def verify_live_audit(path: pathlib.Path) -> dict:
    raw = path.read_bytes(); value = json.loads(raw)
    if raw != canonical(value):
        raise ValueError("live audit is not canonical JSON bytes")
    required = {"schema", "upstream_head", "upstream_tree", "queries", "searches",
                "known_ingestion_pull",
                "open_pull_requests_scanned", "pulls_requiring_full_file_pagination",
                "open_target_path_matches", "release_page_sizes", "releases_scanned",
                "local_release_matches"}
    if set(value) != required or value["schema"] != "oeis-a067720-live-duplicate-audit-v1":
        raise ValueError("live audit schema drift")
    if value["upstream_head"] != M["formal_conjectures"]["commit"] or value["upstream_tree"] != M["formal_conjectures"]["tree"]:
        raise ValueError("live upstream head/tree drift")
    if value["queries"] != SEARCH_QUERIES or set(value["searches"]) != set(SEARCH_QUERIES):
        raise ValueError("exact GitHub search query mapping drift")
    upstream_allowed = {1878, 1456}
    for name, search in value["searches"].items():
        if set(search) != {"query", "total_count", "incomplete_results", "items"} or search["query"] != SEARCH_QUERIES[name] or search["incomplete_results"] is not False or search["total_count"] != len(search["items"]):
            raise ValueError(f"search completeness drift in {name}")
        items = search["items"]
        numbers = {item["number"] for item in items}
        if name.startswith("upstream_"):
            if not numbers <= upstream_allowed:
                raise ValueError(f"new upstream exact-search item in {name}: {sorted(numbers - upstream_allowed)}")
        elif items:
            raise ValueError(f"local duplicate claim in {name}")
    seq = {item["number"]: item for item in value["searches"]["upstream_sequence"]["items"]}
    if set(seq) != {1878, 1456} or (seq[1878]["state"], seq[1878]["is_pull_request"]) != ("closed", True) or (seq[1456]["state"], seq[1456]["is_pull_request"]) != ("closed", False):
        raise ValueError("known ingestion/identifier search baseline drift")
    declaration = {item["number"]: item for item in value["searches"]["upstream_declaration"]["items"]}
    if set(declaration) != {1878} or (declaration[1878]["state"], declaration[1878]["is_pull_request"]) != ("closed", True):
        raise ValueError("declaration-name search baseline drift")
    if value["known_ingestion_pull"] != {"number": 1878, "state": "closed",
                                          "merged_at": "2026-01-27T15:30:27Z",
                                          "merge_commit_sha": "2e7ff5eeba593908427463753fb363fe61af4863"}:
        raise ValueError("merged ingestion PR status drift")
    path_rows = value["open_target_path_matches"]
    path_row_keys = {"number", "title", "url", "head_sha", "content_sha256", "classification"}
    if not isinstance(path_rows, list) or len(path_rows) != len(KNOWN_PATH_TOUCHES) or any(
            not isinstance(item, dict) or set(item) != path_row_keys or type(item["number"]) is not int or
            not all(isinstance(item[key], str) for key in ("title", "url", "head_sha", "content_sha256", "classification"))
            for item in path_rows):
        raise ValueError("open PR target-path row schema/cardinality drift")
    observed_keys = [(item["number"], item["head_sha"], item["content_sha256"]) for item in path_rows]
    if len(set(observed_keys)) != len(observed_keys):
        raise ValueError("duplicate open PR target-path row")
    observed_touches = {key: item["classification"] for key, item in zip(observed_keys, path_rows)}
    if observed_touches != KNOWN_PATH_TOUCHES:
        raise ValueError("open PR target-path touch requires exact frozen classification")
    if value["local_release_matches"]:
        raise ValueError("local release already names target")
    sizes = value["release_page_sizes"]
    if not isinstance(sizes, list) or not sizes or any(not isinstance(size, int) or size < 0 or size > 100 for size in sizes) or any(size != 100 for size in sizes[:-1]) or sizes[-1] >= 100 or sum(sizes) != value["releases_scanned"]:
        raise ValueError("release pagination completeness drift")
    if not isinstance(value["open_pull_requests_scanned"], int) or value["open_pull_requests_scanned"] < 1:
        raise ValueError("open PR enumeration is empty")
    return value


def verify_sources(lean: pathlib.Path, live_lean: pathlib.Path, source: pathlib.Path,
                   bfile: pathlib.Path, live_audit_path: pathlib.Path) -> dict:
    expected = M["formal_conjectures"]["sha256"]
    if sha(lean) != expected or sha(live_lean) != expected:
        raise ValueError("pinned/live Lean source hash drift")
    text = lean.read_text(encoding="utf-8")
    for token in ("def A (k : ℕ) : Prop", "theorem a_of_primes", "@[category research open, AMS 11]",
                  "theorem prime_add_one_of_a {k : ℕ}", "(hne : k ≠ 8)", ": (k + 1).Prime"):
        if token not in text:
            raise ValueError("Lean declaration/status drift")
    if sha(source) != M["oeis_source"]["sha256"]:
        raise ValueError("OEIS source hash drift")
    source_text = source.read_text(encoding="utf-8")
    for token in ("%I A067720 #18 Nov 21 2020 14:01:32", "a(n)+1 is prime except for a(5)=8",
                  "Is a(5)=8 the only additional value?"):
        if token not in source_text:
            raise ValueError("OEIS statement drift")
    live = verify_live_audit(live_audit_path)
    return {"catalogue": verify_catalogue(bfile), "live_duplicate_audit_sha256": sha(live_audit_path),
            "open_pull_requests_scanned": live["open_pull_requests_scanned"]}


def prepare(lean: pathlib.Path, live_lean: pathlib.Path, source: pathlib.Path, bfile: pathlib.Path,
            live_audit_path: pathlib.Path, output: pathlib.Path, commit: str) -> None:
    commit = exact_commit(commit)
    table = verify_sources(lean, live_lean, source, bfile, live_audit_path)
    output.mkdir(parents=True, exist_ok=False); snapshots = output / "snapshots"; snapshots.mkdir()
    inputs = ((lean, "67720.lean"), (live_lean, "67720-live.lean"), (source, "A067720.seq"),
              (bfile, "b067720.txt"), (live_audit_path, "live-duplicate-audit.json"))
    for incoming, name in inputs:
        with incoming.open("rb") as src, (snapshots / name).open("xb") as dst:
            shutil.copyfileobj(src, dst); dst.flush(); os.fsync(dst.fileno())
    value = {"schema": SCHEMA, "campaign_commit": commit, "manifest_sha256": sha(MANIFEST),
             "source_commit": M["formal_conjectures"]["commit"], "table": table,
             "snapshots": {name: sha(snapshots / name) for _, name in inputs}}
    value["attestation_sha256"] = self_hash(value)
    atomic_json(output / "gate-attestation.json", value)


def verify(bundle: pathlib.Path, commit: str) -> dict:
    commit = exact_commit(commit); raw = (bundle / "gate-attestation.json").read_bytes(); value = json.loads(raw)
    if raw != canonical(value):
        raise ValueError("gate attestation is not canonical JSON bytes")
    required = {"schema", "campaign_commit", "manifest_sha256", "source_commit", "table", "snapshots", "attestation_sha256"}
    if set(value) != required or value["schema"] != SCHEMA or value["attestation_sha256"] != self_hash(value):
        raise ValueError("gate identity/self-hash drift")
    if value["campaign_commit"] != commit or value["manifest_sha256"] != sha(MANIFEST) or value["source_commit"] != M["formal_conjectures"]["commit"]:
        raise ValueError("gate binding drift")
    snapshots = bundle / "snapshots"
    actual = verify_sources(snapshots / "67720.lean", snapshots / "67720-live.lean",
                            snapshots / "A067720.seq", snapshots / "b067720.txt",
                            snapshots / "live-duplicate-audit.json")
    expected = {name: sha(snapshots / name) for name in value["snapshots"]}
    if value["table"] != actual or value["snapshots"] != expected:
        raise ValueError("gate semantic/snapshot drift")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="mode", required=True)
    live = sub.add_parser("live-audit"); live.add_argument("output", type=pathlib.Path); live.add_argument("--github-token")
    prep = sub.add_parser("prepare"); prep.add_argument("lean", type=pathlib.Path); prep.add_argument("live_lean", type=pathlib.Path); prep.add_argument("source", type=pathlib.Path); prep.add_argument("bfile", type=pathlib.Path); prep.add_argument("live_audit", type=pathlib.Path); prep.add_argument("output", type=pathlib.Path); prep.add_argument("--campaign-commit", required=True)
    check = sub.add_parser("verify"); check.add_argument("bundle", type=pathlib.Path); check.add_argument("--campaign-commit", required=True)
    args = parser.parse_args()
    if args.mode == "live-audit":
        token = args.github_token or os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN or --github-token is required")
        live_audit(args.output, token)
    elif args.mode == "prepare": prepare(args.lean, args.live_lean, args.source, args.bfile, args.live_audit, args.output, args.campaign_commit)
    else: verify(args.bundle, args.campaign_commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
