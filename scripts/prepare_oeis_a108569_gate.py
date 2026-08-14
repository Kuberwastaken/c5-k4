#!/usr/bin/env python3
"""Prepare the immutable A108569 source/status/race/database gate."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import pathlib
import shutil
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = ROOT / "results/expansion/live-search-2026-08-14/oeis-a108569-development"
MANIFEST = HERE / "manifest.json"
M = json.loads(MANIFEST.read_text())
SCHEMA = "oeis-a108569-gate-v1"
SEARCH_QUERIES = {
    "upstream_sequence": 'repo:google-deepmind/formal-conjectures "A108569"',
    "upstream_declaration": 'repo:google-deepmind/formal-conjectures "OeisA108569.conjecture"',
    "local_sequence": 'repo:Kuberwastaken/c5-k4 "A108569"',
    "local_declaration": 'repo:Kuberwastaken/c5-k4 "OeisA108569.conjecture"',
}
INGESTION = {
    "number": 4450, "state": "closed", "merged_at": "2026-08-13T12:46:43Z",
    "merge_commit_sha": "d7032450c559849f2a345f80582688c76b25ffcb",
    "head_sha": "3bd4f0260009869c95d02bfb143e08b82a2aa43d",
}
OPEN_PULL_COUNT = 280
FULL_FILE_PAGE_SIZES = {
    3422: [100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,19],
    4004: [100,91], 4198: [100,100,100,100,100,100,100,100,100,66],
    4356: [100,18], 4417: [100,100,100,100,85], 4428: [100,24],
    4496: [1], 4576: [1], 4688: [100,100,100,100,100,100,100,100,50],
}
INGESTION_TARGET_FILE = {
    "filename": "FormalConjectures/OEIS/108569.lean", "status": "added",
    "sha": "daf4427246c28b56a429646958a2c38ca4cf04fa", "previous_filename": None,
}
SOPHIE_GERMAIN_CONTROLS = {5: 110, 11: 506, 23: 2162, 29: 3422, 41: 6806}


def sha(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def self_hash(value: dict) -> str:
    copy = dict(value); copy.pop("attestation_sha256", None)
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


def factor(n: int) -> tuple[tuple[int, int], ...]:
    if type(n) is not int or n < 1:
        raise ValueError("positive integer required")
    factors = []; remaining = n; divisor = 2
    while divisor * divisor <= remaining:
        if remaining % divisor:
            divisor = 3 if divisor == 2 else divisor + 2
            continue
        exponent = 0
        while remaining % divisor == 0:
            remaining //= divisor; exponent += 1
        factors.append((divisor, exponent))
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        factors.append((remaining, 1))
    return tuple(factors)


def factor_product(factors: tuple[tuple[int, int], ...]) -> int:
    return math.prod(prime ** exponent for prime, exponent in factors)


def totient_factors(factors: tuple[tuple[int, int], ...]) -> int:
    return math.prod((prime - 1) * prime ** (exponent - 1) for prime, exponent in factors)


def phi(n: int) -> tuple[int, tuple[tuple[int, int], ...]]:
    factors = factor(n)
    if factor_product(factors) != n:
        raise RuntimeError("incomplete factorization")
    return totient_factors(factors), factors


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
    if len(rows) != spec["rows"] or [i for i, _ in rows] != list(range(spec["first_index"], spec["last_index"] + 1)):
        raise ValueError("b-file index coverage drift")
    if list(rows[0]) != [spec["first_index"], spec["first_value"]] or list(rows[-1]) != [spec["last_index"], spec["last_value"]]:
        raise ValueError("b-file endpoint row drift")
    if any(left[1] >= right[1] for left, right in zip(rows, rows[1:])):
        raise ValueError("b-file values are not strictly increasing")
    return rows


def divisors(n: int) -> list[int]:
    answer = [1]
    for prime, exponent in factor(n):
        answer = [base * prime ** power for base in answer for power in range(exponent + 1)]
    return sorted(answer)


def verify_catalogue(path: pathlib.Path) -> dict:
    rows = parse_bfile(path); stream = hashlib.sha256()
    even_lift_checks = divisor_lift_checks = 0
    for index, k in rows:
        phi_k, factors_k = phi(k); endpoint = k + phi_k
        phi_endpoint, factors_endpoint = phi(endpoint)
        if phi_endpoint != phi_k:
            raise ValueError(f"catalogue row {index} fails defining equality")
        if k % 2 == 0:
            doubled = 2 * k; phi_doubled, doubled_factors = phi(doubled)
            lifted_endpoint = doubled + phi_doubled
            phi_lifted, lifted_factors = phi(lifted_endpoint)
            if phi_doubled != 2 * phi_k or phi_lifted != phi_doubled:
                raise ValueError(f"even lift identity fails at row {index}")
            even_lift_checks += 1
        for multiplier in divisors(math.gcd(phi_k, k)):
            if multiplier == 1:
                continue
            lifted = multiplier * k; phi_lifted_k, lifted_k_factors = phi(lifted)
            lifted_endpoint = lifted + phi_lifted_k
            phi_lifted_endpoint, lifted_endpoint_factors = phi(lifted_endpoint)
            if phi_lifted_endpoint != phi_lifted_k:
                raise ValueError(f"divisor lift identity fails at row {index}, multiplier {multiplier}")
            divisor_lift_checks += 1
        stream.update(canonical({
            "index": index, "k": k, "factors_k": [list(item) for item in factors_k],
            "phi_k": phi_k, "endpoint": endpoint,
            "factors_endpoint": [list(item) for item in factors_endpoint],
            "phi_endpoint": phi_endpoint, "residual": 0}))
    if rows[0] != (1, 1) or any(k % 2 for _, k in rows[1:]):
        raise ValueError("source parity wall drift")
    source_values = {k for _, k in rows}; sophie_checks = []
    for prime, expected in SOPHIE_GERMAIN_CONTROLS.items():
        if factor(prime) != ((prime, 1),) or factor(2 * prime + 1) != ((2 * prime + 1, 1),):
            raise ValueError("Sophie-Germain control prime drift")
        constructed = 2 * prime * (2 * prime + 1)
        if constructed != expected or constructed not in source_values:
            raise ValueError("Sophie-Germain control missing from catalogue")
        phi_constructed, constructed_factors = phi(constructed)
        endpoint = constructed + phi_constructed
        phi_endpoint, endpoint_factors = phi(endpoint)
        if phi_endpoint != phi_constructed:
            raise ValueError("Sophie-Germain source identity drift")
        sophie_checks.append({"p": prime, "k": constructed,
                              "factors_k": [list(x) for x in constructed_factors],
                              "factors_endpoint": [list(x) for x in endpoint_factors]})
    return {
        "rows": len(rows), "first": list(rows[0]), "last": list(rows[-1]),
        "odd_rows": [[index, k] for index, k in rows if k % 2],
        "even_rows": sum(k % 2 == 0 for _, k in rows),
        "even_lift_checks": even_lift_checks, "divisor_lift_checks": divisor_lift_checks,
        "sophie_germain_controls": sophie_checks,
        "verified_row_stream_sha256": stream.hexdigest(),
    }


def api_request(url: str, token: str, body: dict | None = None) -> dict | list:
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("User-Agent", "c5-k4-a108569-gate")
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


def rest_pull_files(token: str, number: int) -> tuple[list[dict], list[int]]:
    files = []; page_sizes = []; page = 1
    while True:
        values = api_request(
            f"https://api.github.com/repos/google-deepmind/formal-conjectures/pulls/{number}/files?per_page=100&page={page}", token)
        assert isinstance(values, list)
        page_sizes.append(len(values)); files.extend(values)
        if len(values) < 100:
            break
        page += 1
    return files, page_sizes


def open_pull_path_matches(token: str) -> tuple[int, list[dict], dict[int, list[int]]]:
    query = """query($cursor:String){repository(owner:\"google-deepmind\",name:\"formal-conjectures\"){pullRequests(states:OPEN,first:100,after:$cursor){nodes{number title url headRefOid files(first:100){nodes{path changeType} pageInfo{hasNextPage}}}pageInfo{hasNextPage endCursor}}}}"""
    cursor = None; total = 0; matches = []; expanded = {}
    while True:
        response = api_request("https://api.github.com/graphql", token, {"query": query, "variables": {"cursor": cursor}})
        assert isinstance(response, dict)
        if response.get("errors"):
            raise ValueError(f"GitHub GraphQL errors: {response['errors']}")
        page = response["data"]["repository"]["pullRequests"]
        for pull in page["nodes"]:
            total += 1; files = pull["files"]["nodes"]
            needs_rest = pull["files"]["pageInfo"]["hasNextPage"] or any(item.get("changeType") == "RENAMED" for item in files)
            if needs_rest:
                files, sizes = rest_pull_files(token, pull["number"]); expanded[pull["number"]] = sizes
            if touches_target(files):
                current = any(item.get("path") == M["formal_conjectures"]["path"] or item.get("filename") == M["formal_conjectures"]["path"] for item in files)
                digest = None
                if current:
                    content = api_request(f"https://api.github.com/repos/google-deepmind/formal-conjectures/contents/{M['formal_conjectures']['path']}?ref={pull['headRefOid']}", token)
                    assert isinstance(content, dict)
                    digest = hashlib.sha256(base64.b64decode(content["content"], validate=False)).hexdigest()
                matches.append({"number": pull["number"], "title": pull["title"], "url": pull["url"],
                                "head_sha": pull["headRefOid"], "content_sha256": digest,
                                "classification": "UNREVIEWED_TARGET_PATH_TOUCH" if current else "UNREVIEWED_RENAMED_TARGET_PATH"})
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return total, matches, expanded


def live_audit(output: pathlib.Path, token: str) -> None:
    commit = api_request("https://api.github.com/repos/google-deepmind/formal-conjectures/commits/main", token)
    assert isinstance(commit, dict)
    total, path_matches, expanded = open_pull_path_matches(token)
    searches = {name: search_items(token, query) for name, query in SEARCH_QUERIES.items()}
    ingestion = api_request("https://api.github.com/repos/google-deepmind/formal-conjectures/pulls/4450", token)
    assert isinstance(ingestion, dict)
    ingestion_files, ingestion_page_sizes = rest_pull_files(token, 4450)
    ingestion_target_rows = [{
        "filename": item.get("filename"), "status": item.get("status"), "sha": item.get("sha"),
        "previous_filename": item.get("previous_filename")}
        for item in ingestion_files
        if item.get("filename") == M["formal_conjectures"]["path"] or
           item.get("previous_filename") == M["formal_conjectures"]["path"]]
    ingestion_identity = {"number": ingestion["number"], "state": ingestion["state"],
                          "merged_at": ingestion["merged_at"], "merge_commit_sha": ingestion["merge_commit_sha"],
                          "head_sha": ingestion["head"]["sha"],
                          "target_file_records": ingestion_target_rows,
                          "file_page_sizes": ingestion_page_sizes, "files_scanned": len(ingestion_files)}
    upstream_releases = []; upstream_release_page_sizes = []; page = 1
    while True:
        values = api_request(f"https://api.github.com/repos/google-deepmind/formal-conjectures/releases?per_page=100&page={page}", token)
        assert isinstance(values, list)
        upstream_release_page_sizes.append(len(values)); upstream_releases.extend(values)
        if len(values) < 100:
            break
        page += 1
    releases = []; release_page_sizes = []; page = 1
    while True:
        values = api_request(f"https://api.github.com/repos/Kuberwastaken/c5-k4/releases?per_page=100&page={page}", token)
        assert isinstance(values, list)
        release_page_sizes.append(len(values)); releases.extend(values)
        if len(values) < 100:
            break
        page += 1
    local_release_matches = []
    for release in releases:
        haystack = "\n".join(str(release.get(key) or "") for key in ("name", "tag_name", "body"))
        if "A108569" in haystack or "OeisA108569.conjecture" in haystack:
            local_release_matches.append({"id": release["id"], "tag_name": release["tag_name"], "url": release["html_url"]})
    upstream_release_matches = []
    for release in upstream_releases:
        haystack = "\n".join(str(release.get(key) or "") for key in ("name", "tag_name", "body"))
        if "A108569" in haystack or "OeisA108569.conjecture" in haystack:
            upstream_release_matches.append({"id": release["id"], "tag_name": release["tag_name"], "url": release["html_url"]})
    value = {
        "schema": "oeis-a108569-live-duplicate-audit-v1",
        "upstream_head": commit["sha"], "upstream_tree": commit["commit"]["tree"]["sha"],
        "queries": SEARCH_QUERIES, "searches": searches,
        "known_ingestion_pull": ingestion_identity,
        "open_pull_requests_scanned": total,
        "pulls_requiring_full_file_pagination": sorted(expanded),
        "full_file_pagination_page_sizes": {str(k): v for k, v in sorted(expanded.items())},
        "open_target_path_matches": path_matches,
        "release_page_sizes": release_page_sizes, "releases_scanned": len(releases),
        "local_release_matches": local_release_matches,
        "upstream_release_page_sizes": upstream_release_page_sizes,
        "upstream_releases_scanned": len(upstream_releases),
        "upstream_release_matches": upstream_release_matches,
    }
    atomic_json(output, value)


def verify_live_audit(path: pathlib.Path) -> dict:
    raw = path.read_bytes(); value = json.loads(raw)
    if raw != canonical(value):
        raise ValueError("live audit is not canonical JSON bytes")
    required = {"schema", "upstream_head", "upstream_tree", "queries", "searches", "known_ingestion_pull",
                "open_pull_requests_scanned", "pulls_requiring_full_file_pagination",
                "full_file_pagination_page_sizes",
                "open_target_path_matches", "release_page_sizes", "releases_scanned", "local_release_matches",
                "upstream_release_page_sizes", "upstream_releases_scanned", "upstream_release_matches"}
    if set(value) != required or value["schema"] != "oeis-a108569-live-duplicate-audit-v1":
        raise ValueError("live audit schema drift")
    if (value["upstream_head"], value["upstream_tree"]) != (M["formal_conjectures"]["commit"], M["formal_conjectures"]["tree"]):
        raise ValueError("live upstream head/tree drift")
    if value["queries"] != SEARCH_QUERIES or set(value["searches"]) != set(SEARCH_QUERIES):
        raise ValueError("exact GitHub search query mapping drift")
    for name, search in value["searches"].items():
        if set(search) != {"query", "total_count", "incomplete_results", "items"} or search["query"] != SEARCH_QUERIES[name] or search["incomplete_results"] is not False or search["total_count"] != len(search["items"]):
            raise ValueError(f"search completeness drift in {name}")
        if search["items"]:
            raise ValueError(f"new duplicate/claim search item in {name}")
    ingestion = value["known_ingestion_pull"]
    identity = {key: ingestion.get(key) for key in INGESTION}
    if identity != INGESTION or ingestion.get("target_file_records") != [INGESTION_TARGET_FILE] or ingestion.get("file_page_sizes") != [75] or ingestion.get("files_scanned") != 75:
        raise ValueError("merged ingestion PR #4450 identity/path drift")
    sizes = ingestion.get("file_page_sizes")
    if not isinstance(sizes, list) or not sizes or any(type(x) is not int or not 0 <= x <= 100 for x in sizes) or any(x != 100 for x in sizes[:-1]) or sizes[-1] >= 100 or sum(sizes) != ingestion.get("files_scanned"):
        raise ValueError("ingestion file pagination drift")
    if value["open_target_path_matches"]:
        raise ValueError("open PR target-path touch is a race stop")
    if value["open_pull_requests_scanned"] != OPEN_PULL_COUNT:
        raise ValueError("open PR count drift")
    expanded = value["pulls_requiring_full_file_pagination"]
    page_receipts = value["full_file_pagination_page_sizes"]
    if set(expanded) != set(FULL_FILE_PAGE_SIZES) or set(page_receipts) != {str(x) for x in FULL_FILE_PAGE_SIZES}:
        raise ValueError("full-file pagination set/receipt drift")
    for number in expanded:
        sizes = page_receipts[str(number)]
        if sizes != FULL_FILE_PAGE_SIZES[number]:
            raise ValueError("full-file pagination page-size drift")
    if value["local_release_matches"]:
        raise ValueError("local release already names target")
    if value["upstream_release_matches"]:
        raise ValueError("upstream release already names target")
    sizes = value["release_page_sizes"]
    if sizes != [11] or value["releases_scanned"] != 11:
        raise ValueError("release pagination completeness drift")
    if value["upstream_release_page_sizes"] != [1] or value["upstream_releases_scanned"] != 1:
        raise ValueError("upstream release pagination completeness drift")
    return value


def verify_sources(lean: pathlib.Path, live_lean: pathlib.Path, source: pathlib.Path,
                   bfile: pathlib.Path, live_audit_path: pathlib.Path) -> dict:
    expected = M["formal_conjectures"]["sha256"]
    if sha(lean) != expected or sha(live_lean) != expected:
        raise ValueError("pinned/live Lean source hash drift")
    text = lean.read_text(encoding="utf-8")
    for token in ("def A (k : ℕ) : Prop := 0 < k ∧ φ k = φ (k + φ k)", "noncomputable def a",
                  "n.nth A", "@[category research open, AMS 11]", "theorem conjecture : ∀ n, 0 < n → Even (a n) := by", "sorry"):
        if token not in text:
            raise ValueError("Lean declaration/status drift")
    if sha(source) != M["oeis_source"]["sha256"]:
        raise ValueError("OEIS source hash drift")
    source_text = source.read_text(encoding="utf-8")
    for token in ("%I A108569 #14 Sep 08 2022 08:45:19", "phi(n) = phi(n + phi(n))",
                  "Except for the first term all terms are even", "m divides gcd(phi(n),n)", "%O A108569 1,2"):
        if token not in source_text:
            raise ValueError("OEIS statement/lift/offset drift")
    live = verify_live_audit(live_audit_path)
    return {"catalogue": verify_catalogue(bfile), "live_duplicate_audit_sha256": sha(live_audit_path),
            "open_pull_requests_scanned": live["open_pull_requests_scanned"],
            "ingestion_files_scanned": live["known_ingestion_pull"]["files_scanned"]}


def prepare(lean: pathlib.Path, live_lean: pathlib.Path, source: pathlib.Path, bfile: pathlib.Path,
            live_audit_path: pathlib.Path, output: pathlib.Path, commit: str) -> None:
    commit = exact_commit(commit); table = verify_sources(lean, live_lean, source, bfile, live_audit_path)
    output.mkdir(parents=True, exist_ok=False); snapshots = output / "snapshots"; snapshots.mkdir()
    inputs = ((lean, "108569.lean"), (live_lean, "108569-live.lean"), (source, "A108569.seq"),
              (bfile, "b108569.txt"), (live_audit_path, "live-duplicate-audit.json"))
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
    actual = verify_sources(snapshots / "108569.lean", snapshots / "108569-live.lean",
                            snapshots / "A108569.seq", snapshots / "b108569.txt",
                            snapshots / "live-duplicate-audit.json")
    expected = {name: sha(snapshots / name) for name in value["snapshots"]}
    if value["table"] != actual or value["snapshots"] != expected:
        raise ValueError("gate semantic/snapshot drift")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="mode", required=True)
    live = sub.add_parser("live-audit"); live.add_argument("output", type=pathlib.Path); live.add_argument("--github-token")
    prep = sub.add_parser("prepare")
    for name in ("lean", "live_lean", "source", "bfile", "live_audit", "output"):
        prep.add_argument(name, type=pathlib.Path)
    prep.add_argument("--campaign-commit", required=True)
    check = sub.add_parser("verify"); check.add_argument("bundle", type=pathlib.Path); check.add_argument("--campaign-commit", required=True)
    args = parser.parse_args()
    if args.mode == "live-audit":
        token = args.github_token or os.environ.get("GITHUB_TOKEN")
        if not token:
            raise SystemExit("GITHUB_TOKEN or --github-token is required")
        live_audit(args.output, token)
    elif args.mode == "prepare":
        prepare(args.lean, args.live_lean, args.source, args.bfile, args.live_audit, args.output, args.campaign_commit)
    else:
        verify(args.bundle, args.campaign_commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
