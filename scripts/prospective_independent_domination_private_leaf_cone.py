#!/usr/bin/env python3
"""Protocol-locked arithmetic cone for independent-domination Conjecture 1.6."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import urllib.request


UPSTREAM = Path("/Users/kuber.mehta/Projects/formal-conjectures")
SOURCE_PATH = "FormalConjectures/Arxiv/2107.00295/IndependentDomination.lean"
ARXIV_SOURCE = "https://export.arxiv.org/e-print/2107.00295"


def command(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(
        args, cwd=cwd, check=True, capture_output=True, text=True, timeout=55
    ).stdout.strip()


def live_gate() -> dict:
    command("git", "fetch", "upstream", "main", "--quiet", cwd=UPSTREAM)
    commit = command("git", "rev-parse", "upstream/main", cwd=UPSTREAM)
    source = command("git", "show", f"upstream/main:{SOURCE_PATH}", cwd=UPSTREAM)
    blob = command("git", "rev-parse", f"upstream/main:{SOURCE_PATH}", cwd=UPSTREAM)

    required_source = (
        "theorem independentDominationEven",
        "theorem independentDominationOdd",
        "@[category research open, AMS 5]",
        "(D + 2)^2 * i ≤ (D^2 + 4) * n",
        "(D + 1) * (D + 3) * i ≤ (D^2 + 3) * n",
    )
    missing_source = [needle for needle in required_source if needle not in source]

    with urllib.request.urlopen(ARXIV_SOURCE, timeout=30) as response:
        archive = response.read()
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        tex_member = tar.getmember("main.tex")
        extracted = tar.extractfile(tex_member)
        if extracted is None:
            raise RuntimeError("arXiv main.tex extraction failed")
        tex = extracted.read().decode("utf-8")
    required_paper = (
        "Conjecture 1.6",
        "D \\in \\{5,6,7,8\\}",
        "maximum degree at most $4$",
        "H\\left(\\left\\lfloor\\frac{D}{2}\\right\\rfloor+1",
    )
    missing_paper = [needle for needle in required_paper if needle not in tex]

    query = (
        'repo:google-deepmind/formal-conjectures '
        '("2107.00295" OR "independentDominationEven" OR '
        '"independentDominationOdd")'
    )
    search_raw = command(
        "gh", "api", "-X", "GET", "search/issues", "-f", f"q={query}",
        "-f", "per_page=100"
    )
    hits = json.loads(search_raw)["items"]
    relevant = [
        {
            "number": item["number"],
            "state": item["state"],
            "title": item["title"],
            "kind": "pull_request" if "pull_request" in item else "issue",
            "url": item["html_url"],
        }
        for item in hits
        if item["number"] in (227, 1373)
    ]
    unexpected = [item["number"] for item in hits if item["number"] not in (227, 1373, 4278)]

    failures = []
    if missing_source:
        failures.append({"source_literals_missing": missing_source})
    if missing_paper:
        failures.append({"paper_literals_missing": missing_paper})
    if {item["number"] for item in relevant} != {227, 1373}:
        failures.append({"expected_addition_history_missing": relevant})
    if unexpected:
        failures.append({"unexpected_exact_search_hits": unexpected})
    return {
        "event": "LIVE_SOURCE_PRIOR_ART_GATE",
        "status": "PASS" if not failures else "STOP",
        "upstream_commit": commit,
        "source_path": SOURCE_PATH,
        "source_blob": blob,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "declarations": ["independentDominationEven", "independentDominationOdd"],
        "source_status": "research open",
        "paper_source": ARXIV_SOURCE,
        "paper_main_tex_sha256": hashlib.sha256(tex.encode()).hexdigest(),
        "known_domain": {
            "proved": "D<=4",
            "authors_report_checked_but_omit_proofs": [5, 6, 7, 8],
            "uncovered_search_requirement": "D>=9",
        },
        "github_exact_search_hits": relevant,
        "github_search_interpretation":
            "issue 227 and merged PR 1373 add the open declarations; no exact hit resolves them",
        "failures": failures,
        "candidate_evaluations": 0,
        "public_action": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("gate",))
    args = parser.parse_args()
    result = live_gate() if args.mode == "gate" else None
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
