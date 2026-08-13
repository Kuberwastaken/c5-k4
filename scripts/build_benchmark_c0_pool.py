#!/usr/bin/env python3
"""Build semantics-blind Method v1.1 open inventory and cluster pool.

The builder reads one exact ``formal-conjectures`` Git tree without checking it
out.  It records only path, declaration identity, content digests, and a small
set of declaration-header syntax flags.  It never emits statement text.  Open
siblings in one source module are conservatively merged into one question
cluster; a module whose declarations receive different syntax-only strata is
marked ambiguous and is ineligible rather than split.

This is C0 preparation, not C1 selection.  The output has no random ordering,
rank, forecast, or selected-target field.
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


SCHEMA_INVENTORY = "c5k4-open-inventory-1.0"
SCHEMA_POOL = "c5k4-question-cluster-pool-1.0"
OPEN_TAG = re.compile(r"@\[\s*category\s+research\s+open\b[^]]*\]", re.DOTALL)
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
    """Return declaration header through the first top-level-looking ``:=``.

    Open conjecture files conventionally use ``:= by``.  Falling back to the
    entire category block is conservative and still excludes proof text from
    emitted artifacts because only the digest and syntax flags are retained.
    """

    proof = block.find(":=", declaration_end)
    return block[:proof] if proof >= 0 else block


def _matches(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in patterns)


def syntax_metadata(
    path: str, header: str, rules: dict[str, Any], module_text: str = ""
) -> dict[str, bool]:
    path_rules = rules["domain_signals"]["path_regex"]
    syntax_rules = rules["domain_signals"]["header_regex"]
    ordered = rules["graph_scalar_signal"]["header_regex"]
    return {
        "graph_path": _matches(path_rules["GRAPH"], path),
        "graph_header": _matches(syntax_rules["GRAPH"], header),
        "algebra_path": _matches(path_rules["FINITE_ALGEBRA_EQUATIONAL"], path),
        "algebra_header": _matches(syntax_rules["FINITE_ALGEBRA_EQUATIONAL"], header),
        "automata_game_process_path": _matches(path_rules["AUTOMATA_GAME_PROCESS"], path),
        "automata_game_process_header": _matches(
            syntax_rules["AUTOMATA_GAME_PROCESS"], header
        ),
        "ordered_relation_header": _matches(ordered, header),
        "explicit_finite_header": _matches(
            rules["finite_signal"]["header_regex"], header
        ),
        "explicit_finite_path": _matches(
            rules["finite_signal"]["path_regex"], path
        ),
        "explicit_finite_module": _matches(
            rules["finite_signal"]["header_regex"], module_text
        ),
    }


def classify(metadata: dict[str, bool]) -> tuple[str | None, str]:
    graph = metadata["graph_path"] or metadata["graph_header"]
    algebra = metadata["algebra_path"] or metadata["algebra_header"]
    process = (
        metadata["automata_game_process_path"]
        or metadata["automata_game_process_header"]
    )
    finite = (
        metadata["explicit_finite_header"]
        or metadata["explicit_finite_path"]
        or metadata["explicit_finite_module"]
    )
    domains = [name for name, value in (("GRAPH", graph), ("ALGEBRA", algebra), ("PROCESS", process)) if value]
    if len(domains) > 1:
        return None, "MULTIPLE_DOMAIN_SIGNALS"
    if graph:
        if not finite:
            return None, "GRAPH_WITHOUT_FINITE_SIGNAL"
        if metadata["ordered_relation_header"]:
            return "GRAPH_SCALAR_INEQUALITY", "FINITE_GRAPH_WITH_ORDERED_RELATION"
        return "GRAPH_STRUCTURAL_PROPERTY", "FINITE_GRAPH_WITHOUT_ORDERED_RELATION"
    if algebra:
        if finite:
            return "FINITE_ALGEBRA_EQUATIONAL", "ALGEBRA_AND_FINITE_SIGNALS"
        return None, "ALGEBRA_WITHOUT_FINITE_SIGNAL"
    if process:
        return "AUTOMATA_GAME_PROCESS", "AUTOMATA_GAME_PROCESS_PATH_OR_HEADER_SIGNAL"
    if finite:
        return "FINITE_COMBINATORIAL", "EXPLICIT_FINITE_SIGNAL"
    return None, "UNCLASSIFIED_WITHOUT_FINITE_SIGNAL"


def extract(repo: Path, ref: str, rules: dict[str, Any]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    commit = git(repo, "rev-parse", ref).decode().strip()
    tree = git(repo, "rev-parse", f"{ref}^{{tree}}").decode().strip()
    names = git(repo, "ls-tree", "-r", "--name-only", ref, "--", "FormalConjectures").decode().splitlines()
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
            # Any intervening category begins a different declaration block.
            next_category = text.find("@[category", tag.end(), end)
            if next_category >= 0:
                end = next_category
            block = text[tag.start():end]
            match = DECLARATION.search(block, tag.end() - tag.start())
            if match is None:
                raise ValueError(f"open tag without parsed declaration: {path}:{text.count(chr(10), 0, tag.start()) + 1}")
            header = _header(block, match.end())
            metadata = syntax_metadata(path, header, rules, text)
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
        raise AssertionError(f"parsed {len(declarations)} declarations from {raw_open_tags} open tags")
    return {"commit": commit, "tree": tree}, declarations


def build_inventory(upstream: dict[str, str], declarations: list[dict[str, Any]], rules_path: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_INVENTORY,
        "upstream": {
            "repository": "google-deepmind/formal-conjectures",
            **upstream,
            "declaration_root": "FormalConjectures",
        },
        "extraction_policy": {
            "open_marker": "@[category research open ...]",
            "emitted_statement_text": False,
            "permitted_inputs": [
                "git path",
                "open-category marker",
                "declaration kind and name",
                "declaration-header syntax flags",
                "content digests",
            ],
            "classifier_path": str(rules_path),
            "classifier_sha256": sha256_file(rules_path),
        },
        "declaration_count": len(declarations),
        "module_count": len({row["path"] for row in declarations}),
        "declarations": declarations,
    }


def build_pool(inventory: dict[str, Any], inventory_sha: str, rules_path: Path) -> dict[str, Any]:
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
            status = "MACHINE_ELIGIBLE_PENDING_CONTAMINATION"
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
                "eligibility_scope": "PRE_CONTAMINATION",
                "classification_status": status,
                "classification_basis": basis,
            }
        )
    counts = Counter(
        row["machine_stratum"] if row["machine_stratum"] is not None else "AMBIGUOUS_EXCLUDE"
        for row in clusters
    )
    return {
        "schema_version": SCHEMA_POOL,
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
    parser.add_argument("--formal-ref", required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--pool", type=Path, required=True)
    args = parser.parse_args()

    rules = json.loads(args.classifier.read_text(encoding="utf-8"))
    if rules.get("schema_version") != "c5k4-five-strata-classifier-1.0":
        raise ValueError("unsupported classifier schema")
    upstream, declarations = extract(args.formal_repo.resolve(), args.formal_ref, rules)
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
