#!/usr/bin/env python3
"""Build the pinned, syntax-only Method v1.3 prototype inventory and pool.

This registry-contact executable reads only the pinned Git tree and emits
paths, declaration metadata, allowlisted syntax flags, fixed labels, and
digests. It never emits source or statement text, random ranks, or a target
selection. The output is a pre-P0 prototype, not a v1.3 freeze artifact.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any


PINNED_COMMIT = "3f08b849788e5e73d52069c616469ea995aac7d7"
PINNED_TREE = "a41c32dda2ed1544836f1761887bc0d3da00b8f0"
SCHEMA_INVENTORY = "c5k4-open-inventory-1.3-prototype"
SCHEMA_POOL = "c5k4-question-cluster-pool-1.3-prototype"
OPEN_TAG = re.compile(r"@\[\s*category\s+research\s+open\b[^]]*\]", re.DOTALL)
ANY_CATEGORY = re.compile(r"@\[\s*category\b")
DECLARATION = re.compile(
    r"\b(?:(?:noncomputable|private|protected)\s+)*"
    r"(theorem|lemma|def|abbrev)\s+([^\s(:]+)"
)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def pretty_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _header(block: str, declaration_end: int) -> str:
    proof = block.find(":=", declaration_end)
    return block[:proof] if proof >= 0 else block


def _matches(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in patterns)


def _scan_top_level(text: str):
    """Yield ``(offset, character)`` outside (), [], and {} syntax groups."""

    stack: list[str] = []
    closing = {"(": ")", "[": "]", "{": "}"}
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
        elif char in closing:
            stack.append(closing[char])
        elif stack and char == stack[-1]:
            stack.pop()
        elif not stack:
            yield index, char
        index += 1


def _strip_outer_parentheses(text: str) -> str:
    """Remove balanced parentheses enclosing the complete expression."""

    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        closes_at_end = False
        for index, char in enumerate(text):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    closes_at_end = index == len(text) - 1
                    break
        if not closes_at_end:
            break
        text = text[1:-1].strip()
    return text


def declaration_conclusion(header: str, declaration_end: int) -> str:
    """Return the conclusion after binders and top-level implication premises."""

    tail = header[declaration_end:]
    colon = next((i for i, char in _scan_top_level(tail) if char == ":"), None)
    if colon is None:
        return ""
    conclusion = _strip_outer_parentheses(tail[colon + 1 :])

    # A top-level implication premise is a hypothesis, not the conclusion
    # relation. Repeatedly retain only the final implication consequent.
    while True:
        arrows = []
        top = {i for i, _ in _scan_top_level(conclusion)}
        for match in re.finditer(r"→|->", conclusion):
            if match.start() in top:
                arrows.append(match)
        if not arrows:
            break
        conclusion = _strip_outer_parentheses(conclusion[arrows[-1].end() :])
    return conclusion


def has_outer_ordered_relation(conclusion: str, patterns: list[str]) -> bool:
    """Test ordered tokens only at the outer syntactic level of a conclusion."""

    top = {i for i, _ in _scan_top_level(conclusion)}
    for pattern in patterns:
        for match in re.finditer(pattern, conclusion, re.IGNORECASE | re.DOTALL):
            if match.start() in top:
                return True
    return False


def syntax_metadata(
    path: str,
    header: str,
    declaration_end: int,
    rules: dict[str, Any],
    module_text: str,
) -> dict[str, bool]:
    path_rules = rules["domain_signals"]["path_regex"]
    header_rules = rules["domain_signals"]["header_regex"]
    module_rules = rules["domain_signals"]["module_regex"]
    conclusion = declaration_conclusion(header, declaration_end)
    return {
        "graph_path": _matches(path_rules["GRAPH"], path),
        "graph_header": _matches(header_rules["GRAPH"], header),
        "graph_module": _matches(module_rules["GRAPH"], module_text),
        "algebra_path": _matches(path_rules["FINITE_ALGEBRA_EQUATIONAL"], path),
        "algebra_header": _matches(header_rules["FINITE_ALGEBRA_EQUATIONAL"], header),
        "automata_game_process_path": _matches(path_rules["AUTOMATA_GAME_PROCESS"], path),
        "automata_game_process_header": _matches(
            header_rules["AUTOMATA_GAME_PROCESS"], header
        ),
        "automata_game_process_module": _matches(
            module_rules["AUTOMATA_GAME_PROCESS"], module_text
        ),
        "outer_ordered_relation_conclusion": has_outer_ordered_relation(
            conclusion, rules["graph_scalar_signal"]["outer_conclusion_relation_regex"]
        ),
        "explicit_finite_header": _matches(
            rules["finite_signal"]["header_regex"], header
        ),
        "explicit_finite_path": _matches(rules["finite_signal"]["path_regex"], path),
        "explicit_finite_module": _matches(
            rules["finite_signal"]["module_regex"], module_text
        ),
    }


def classify(metadata: dict[str, bool]) -> tuple[str | None, str]:
    graph = metadata["graph_path"] or metadata["graph_header"] or metadata["graph_module"]
    algebra = metadata["algebra_path"] or metadata["algebra_header"]
    process = (
        metadata["automata_game_process_path"]
        or metadata["automata_game_process_header"]
        or metadata["automata_game_process_module"]
    )
    finite = (
        metadata["explicit_finite_header"]
        or metadata["explicit_finite_path"]
        or metadata["explicit_finite_module"]
    )
    domains = [
        name
        for name, value in (("GRAPH", graph), ("ALGEBRA", algebra), ("PROCESS", process))
        if value
    ]
    if len(domains) > 1:
        return None, "MULTIPLE_DOMAIN_SIGNALS"
    if graph:
        if not finite:
            return None, "GRAPH_WITHOUT_FINITE_SIGNAL"
        if metadata["outer_ordered_relation_conclusion"]:
            return "GRAPH_SCALAR_INEQUALITY", "FINITE_GRAPH_WITH_OUTER_ORDERED_CONCLUSION"
        return "GRAPH_STRUCTURAL_PROPERTY", "FINITE_GRAPH_WITHOUT_OUTER_ORDERED_CONCLUSION"
    if algebra:
        if finite:
            return "FINITE_ALGEBRA_EQUATIONAL", "ALGEBRA_AND_FINITE_SIGNALS"
        return None, "ALGEBRA_WITHOUT_FINITE_SIGNAL"
    if process:
        return "AUTOMATA_GAME_PROCESS", "AUTOMATA_GAME_PROCESS_SYNTAX_SIGNAL"
    if finite:
        return "FINITE_COMBINATORIAL", "EXPLICIT_FINITE_SIGNAL"
    return None, "UNCLASSIFIED_WITHOUT_FINITE_SIGNAL"


def extract(
    repo: Path, rules: dict[str, Any], *, enforce_pin: bool = True
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    commit = git(repo, "rev-parse", PINNED_COMMIT).decode().strip()
    tree = git(repo, "rev-parse", f"{PINNED_COMMIT}^{{tree}}").decode().strip()
    if enforce_pin and (commit != PINNED_COMMIT or tree != PINNED_TREE):
        raise ValueError("formal-conjectures commit/tree does not match the v1.3 prototype pin")
    ref = commit
    names = git(
        repo, "ls-tree", "-r", "--name-only", ref, "--", "FormalConjectures"
    ).decode().splitlines()
    declarations: list[dict[str, Any]] = []
    raw_open_tags = 0
    for path in sorted(name for name in names if name.endswith(".lean")):
        raw = git(repo, "show", f"{ref}:{path}")
        text = raw.decode("utf-8", "strict")
        tags = list(OPEN_TAG.finditer(text))
        raw_open_tags += len(tags)
        module_sha = sha256(raw)
        for index, tag in enumerate(tags):
            end = tags[index + 1].start() if index + 1 < len(tags) else len(text)
            next_category = ANY_CATEGORY.search(text, tag.end(), end)
            if next_category is not None:
                end = next_category.start()
            block = text[tag.start() : end]
            match = DECLARATION.search(block, tag.end() - tag.start())
            if match is None:
                line = text.count(chr(10), 0, tag.start()) + 1
                raise ValueError(f"open tag without parsed declaration: {path}:{line}")
            header = _header(block, match.end())
            metadata = syntax_metadata(path, header, match.end(), rules, text)
            stratum, basis = classify(metadata)
            declarations.append(
                {
                    "declaration_id": f"{path}::{match.group(2)}",
                    "path": path,
                    "name": match.group(2),
                    "kind": match.group(1),
                    "category_line": text.count("\n", 0, tag.start()) + 1,
                    "module_blob_sha256": module_sha,
                    "statement_header_sha256": sha256(header.encode("utf-8")),
                    "syntax_metadata": metadata,
                    "machine_stratum": stratum,
                    "classification_basis": basis,
                }
            )
    if raw_open_tags != len(declarations):
        raise AssertionError(
            f"parsed {len(declarations)} declarations from {raw_open_tags} open tags"
        )
    return {"commit": commit, "tree": tree}, declarations


def build_inventory(
    upstream: dict[str, str], declarations: list[dict[str, Any]], rules_path: Path
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_INVENTORY,
        "artifact_status": "PRE_P0_PROTOTYPE_NOT_A_FREEZE",
        "upstream": {
            "repository": "google-deepmind/formal-conjectures",
            **upstream,
            "declaration_root": "FormalConjectures",
        },
        "extraction_policy": {
            "open_marker": "@[category research open ...]",
            "emitted_statement_text": False,
            "emitted_random_ranks": False,
            "emitted_target_selection": False,
            "classifier_path": str(rules_path),
            "classifier_sha256": sha256_file(rules_path),
        },
        "declaration_count": len(declarations),
        "module_count": len({row["path"] for row in declarations}),
        "declarations": declarations,
    }


def build_pool(
    inventory: dict[str, Any], inventory_sha: str, rules_path: Path
) -> dict[str, Any]:
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in inventory["declarations"]:
        by_path[row["path"]].append(row)
    clusters = []
    for path in sorted(by_path):
        rows = sorted(by_path[path], key=lambda row: (row["category_line"], row["name"]))
        strata = {row["machine_stratum"] for row in rows}
        if None in strata or len(strata) != 1:
            stratum = None
            status = "AMBIGUOUS_EXCLUDE"
            basis = "DECLARATION_CLASSIFICATIONS_DISAGREE_OR_AMBIGUOUS"
        else:
            stratum = next(iter(strata))
            status = "MACHINE_ELIGIBLE_PENDING_PROVENANCE"
            basis = "UNANIMOUS_DECLARATION_CLASSIFICATION"
        identity = {
            "path": path,
            "module_blob_sha256": rows[0]["module_blob_sha256"],
            "declarations": [
                {"name": row["name"], "statement_header_sha256": row["statement_header_sha256"]}
                for row in rows
            ],
        }
        clusters.append(
            {
                "cluster_id": "fc-module:" + path.removesuffix(".lean"),
                "identity_sha256": sha256(canonical_json(identity)),
                "grouping_rule": "ONE_SOURCE_MODULE_CONSERVATIVE_MERGE",
                "path": path,
                "module_blob_sha256": rows[0]["module_blob_sha256"],
                "declarations": [
                    {
                        "name": row["name"],
                        "kind": row["kind"],
                        "category_line": row["category_line"],
                        "statement_header_sha256": row["statement_header_sha256"],
                    }
                    for row in rows
                ],
                "machine_stratum": stratum,
                "stratum": stratum,
                "eligible": stratum is not None,
                "eligibility_scope": "PRE_PROVENANCE_PROTOTYPE",
                "classification_status": status,
                "classification_basis": basis,
            }
        )
    counts = Counter(
        row["machine_stratum"]
        if row["machine_stratum"] is not None
        else "AMBIGUOUS_EXCLUDE"
        for row in clusters
    )
    return {
        "schema_version": SCHEMA_POOL,
        "artifact_status": "PRE_P0_PROTOTYPE_NOT_A_FREEZE",
        "upstream": inventory["upstream"],
        "open_inventory_sha256": inventory_sha,
        "classifier": {"path": str(rules_path), "sha256": sha256_file(rules_path)},
        "selection_fields_present": False,
        "random_order_present": False,
        "grouping_rule": "ONE_SOURCE_MODULE_CONSERVATIVE_MERGE",
        "cluster_count": len(clusters),
        "counts_by_machine_stratum": dict(sorted(counts.items())),
        "clusters": clusters,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-repo", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    args = parser.parse_args()

    rules = json.loads(args.classifier.read_text(encoding="utf-8"))
    if rules.get("schema_version") != "c5k4-five-strata-classifier-1.3-prototype":
        raise ValueError("unsupported classifier schema")
    if rules.get("upstream", {}).get("commit") != PINNED_COMMIT:
        raise ValueError("classifier commit pin mismatch")
    if rules.get("upstream", {}).get("tree") != PINNED_TREE:
        raise ValueError("classifier tree pin mismatch")
    upstream, declarations = extract(args.formal_repo.resolve(), rules)
    inventory = build_inventory(upstream, declarations, args.classifier)
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    args.inventory.write_text(pretty_json(inventory), encoding="utf-8")
    pool = build_pool(inventory, sha256_file(args.inventory), args.classifier)
    args.pool.parent.mkdir(parents=True, exist_ok=True)
    args.pool.write_text(pretty_json(pool), encoding="utf-8")
    print(
        json.dumps(
            {
                "commit": upstream["commit"],
                "tree": upstream["tree"],
                "declarations": len(declarations),
                "clusters": pool["cluster_count"],
                "strata": pool["counts_by_machine_stratum"],
                "inventory_sha256": sha256_file(args.inventory),
                "pool_sha256": sha256_file(args.pool),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
