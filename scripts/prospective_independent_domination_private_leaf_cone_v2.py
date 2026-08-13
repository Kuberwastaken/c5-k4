#!/usr/bin/env python3
"""Fresh semantic-gated private-leaf cone trial for Conjecture 1.6."""

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


def semantic_gate() -> dict:
    command("git", "fetch", "upstream", "main", "--quiet", cwd=UPSTREAM)
    commit = command("git", "rev-parse", "upstream/main", cwd=UPSTREAM)
    source = command("git", "show", f"upstream/main:{SOURCE_PATH}", cwd=UPSTREAM)
    blob = command("git", "rev-parse", f"upstream/main:{SOURCE_PATH}", cwd=UPSTREAM)
    lean_semantics = (
        "theorem independentDominationEven",
        "theorem independentDominationOdd",
        "@[category research open, AMS 5]",
        "(D + 2)^2 * i ≤ (D^2 + 4) * n",
        "(D + 1) * (D + 3) * i ≤ (D^2 + 3) * n",
        "0 < G.minDegree",
    )

    with urllib.request.urlopen(ARXIV_SOURCE, timeout=30) as response:
        archive = response.read()
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        extracted = tar.extractfile("main.tex")
        if extracted is None:
            raise RuntimeError("arXiv main.tex extraction failed")
        tex = extracted.read().decode("utf-8")
    paper_semantics = (
        "\\begin{conjecture}\\label{con:idset-general}",
        "\\frac{D^2+4}{(D+2)^2}|V(G)|",
        "\\frac{D^2+3}{(D+1)(D+3)}|V(G)|",
        "D \\in \\{5,6,7,8\\}",
        "maximum degree at most $4$",
    )

    query = (
        'repo:google-deepmind/formal-conjectures '
        '("2107.00295" OR "independentDominationEven" OR '
        '"independentDominationOdd")'
    )
    hits = json.loads(command(
        "gh", "api", "-X", "GET", "search/issues", "-f", f"q={query}",
        "-f", "per_page=100"
    ))["items"]
    relevant = [
        {
            "number": item["number"],
            "state": item["state"],
            "title": item["title"],
            "kind": "pull_request" if "pull_request" in item else "issue",
            "url": item["html_url"],
        }
        for item in hits if item["number"] in (227, 1373)
    ]
    exact_resolution_hits = [
        item["number"] for item in hits if item["number"] not in (227, 1373, 4278)
    ]
    failures = []
    missing_lean = [needle for needle in lean_semantics if needle not in source]
    missing_paper = [needle for needle in paper_semantics if needle not in tex]
    if missing_lean:
        failures.append({"lean_semantics_missing": missing_lean})
    if missing_paper:
        failures.append({"paper_semantics_missing": missing_paper})
    if {item["number"] for item in relevant} != {227, 1373}:
        failures.append({"addition_history_missing": relevant})
    if exact_resolution_hits:
        failures.append({"unexpected_exact_search_hits": exact_resolution_hits})
    return {
        "event": "SEMANTIC_SOURCE_STATUS_PRIOR_ART_GATE",
        "trial": "PRIVATE_LEAF_CONE_V2",
        "status": "PASS" if not failures else "STOP",
        "upstream_commit": commit,
        "source_path": SOURCE_PATH,
        "source_blob": blob,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_status": "research open",
        "semantic_checks": {
            "lean": list(lean_semantics),
            "paper": list(paper_semantics),
        },
        "paper_source": ARXIV_SOURCE,
        "paper_main_tex_sha256": hashlib.sha256(tex.encode()).hexdigest(),
        "known_domain": {
            "proved": "D<=4",
            "authors_report_checked_but_omit_proofs": [5, 6, 7, 8],
            "development_requires": "D>=9",
        },
        "github_exact_search_hits": relevant,
        "github_search_interpretation":
            "issue 227 and merged PR 1373 add the open declarations; no exact hit resolves them",
        "failures": failures,
        "candidate_evaluations": 0,
        "public_action": False,
    }


def canonical_vector(q: int, maximum: int, tail_sum: int) -> list[int]:
    vector = [maximum] + [1] * (q - 1)
    remaining = tail_sum - (q - 1)
    for index in range(1, q):
        added = min(maximum - 1, remaining)
        vector[index] += added
        remaining -= added
    if remaining != 0:
        raise RuntimeError("canonical vector distribution failed")
    return vector


def evaluate_cone() -> dict:
    triples = sorted(
        (q - 1 + maximum, q, maximum, tail_sum)
        for q in range(2, 33)
        for maximum in range(1, 33)
        for tail_sum in range(q - 1, (q - 1) * maximum + 1)
        if q - 1 + maximum >= 9
    )
    digest = hashlib.sha256()
    minimum = None
    equality_rows = []
    even_count = 0
    odd_count = 0
    for index, (degree, q, maximum, tail_sum) in enumerate(triples, 1):
        vector = canonical_vector(q, maximum, tail_sum)
        if min(vector) < 1 or max(vector) != maximum or sum(vector) - maximum != tail_sum:
            raise RuntimeError("canonical vector replay failed")
        order = q + maximum + tail_sum
        indep_domination = 1 + tail_sum
        if degree % 2 == 0:
            even_count += 1
            raw = (degree**2 + 4) * order - (degree + 2) ** 2 * indep_domination
            reduced = degree * (degree**2 - 4 * tail_sum)
            parity = "even"
        else:
            odd_count += 1
            raw = ((degree**2 + 3) * order
                   - (degree + 1) * (degree + 3) * indep_domination)
            reduced = degree * (degree**2 - 1 - 4 * tail_sum)
            parity = "odd"
        if raw != reduced:
            raise RuntimeError("raw/reduced residual identity failed")
        row_key = f"{degree},{q},{maximum},{tail_sum},{raw}\n".encode()
        digest.update(row_key)
        row = {
            "index": index,
            "D": degree,
            "q": q,
            "M": maximum,
            "T": tail_sum,
            "n": order,
            "i": indep_domination,
            "parity": parity,
            "residual": raw,
            "canonical_p": vector,
        }
        if minimum is None or raw < minimum["residual"]:
            minimum = row
        if raw == 0:
            equality_rows.append(row)
        if raw < 0:
            return {
                "event": "ARITHMETIC_CONE_V2_RESULT",
                "trial": "PRIVATE_LEAF_CONE_V2",
                "status": "NEGATIVE_STOP",
                "candidate_evaluations": index,
                "candidate": row,
                "rows_sha256": digest.hexdigest(),
                "independent_graph_novelty_verification_required": True,
                "public_action": False,
            }
    return {
        "event": "ARITHMETIC_CONE_V2_RESULT",
        "trial": "PRIVATE_LEAF_CONE_V2",
        "status": "HOLD_BOUNDED_EXTRACT_THEOREM",
        "candidate_evaluations": len(triples),
        "negative_count": 0,
        "even_rows": even_count,
        "odd_rows": odd_count,
        "minimum": minimum,
        "equality_count": len(equality_rows),
        "equality_rows": equality_rows,
        "rows_sha256": digest.hexdigest(),
        "theorem_extraction_required": True,
        "public_action": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("gate", "evaluate"))
    args = parser.parse_args()
    result = semantic_gate() if args.mode == "gate" else evaluate_cone()
    print(json.dumps(result, sort_keys=True))
    if result["status"] in ("STOP", "NEGATIVE_STOP"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
