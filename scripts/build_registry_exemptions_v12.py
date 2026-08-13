#!/usr/bin/env python3
"""Build provenance-bound registry-only exemptions for Method v1.2.

This program never searches target statements.  It starts from a frozen ledger
of outputs of known generators, verifies each generator at an exact Git commit,
and recognizes an output only when all of the following agree:

* artifact kind and machine schema;
* exact byte length and SHA-256;
* an allowed Git path or a recorded tool invocation; and
* a source/role which cannot be an assistant or user discussion turn.

The resulting exemption key is a hash of the source id, immutable locator,
role, and content hash.  It is deliberately not a global content-hash allowlist:
copying a generated JSON object into prose or another path does not exempt that
new scan unit.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterator


SCHEMA = "c5k4-registry-exemptions-1.2-draft"
LEDGER_SCHEMA = "c5k4-generator-provenance-ledger-1.2-draft"
SOURCE_SCHEMA = "c5k4-registry-exemption-sources-1.2-draft"
HEX_COMMIT = re.compile(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")

# These are structural machine-artifact classes, not target classifications.
# A ledger cannot create a new exemptible prose-shaped class by assertion.
ARTIFACT_SCHEMA_PREFIXES = {
    "open_inventory": ("c5k4-open-inventory-",),
    "question_cluster_pool": ("c5k4-question-cluster-pool-",),
    "eligible_cluster_pool": ("c5k4-eligible-cluster-pool-",),
    "selection_evidence": ("c5k4-benchmark-selection-",),
    "syntax_classifier": ("c5k4-five-strata-classifier-",),
}

DEFAULT_QUOTAS = {
    "GRAPH_SCALAR_INEQUALITY": 3,
    "GRAPH_STRUCTURAL_PROPERTY": 3,
    "FINITE_ALGEBRA_EQUATIONAL": 2,
    "AUTOMATA_GAME_PROCESS": 2,
    "FINITE_COMBINATORIAL": 2,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def exact_commit(repo: Path, ref: str, label: str) -> str:
    if not HEX_COMMIT.fullmatch(ref):
        raise ValueError(f"{label} must be an exact 40- or 64-hex commit")
    resolved = git(repo, "rev-parse", ref).decode().strip()
    if resolved.casefold() != ref.casefold():
        raise ValueError(f"{label} does not resolve to itself")
    return resolved.lower()


def invocation_sha256(tool_name: str, tool_input: object) -> str:
    """Hash the structured tool call, without shell parsing or normalization."""

    return sha256(canonical_json({"tool_name": tool_name, "tool_input": tool_input}))


def unit_identity_sha256(
    source_id: str, locator: str, role: str, content_sha256: str
) -> str:
    return sha256(
        canonical_json(
            {
                "source_id": source_id,
                "locator": locator,
                "role": role,
                "content_sha256": content_sha256,
            }
        )
    )


def validate_machine_artifact(raw: bytes, claim: dict[str, Any]) -> None:
    """Validate only the envelope/schema, never declaration semantics."""

    if b"\x00" in raw:
        raise ValueError(f"artifact {claim['id']!r} is not textual JSON")
    try:
        value = json.loads(raw.decode("utf-8", "strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"artifact {claim['id']!r} is not one complete JSON value") from exc
    if not isinstance(value, dict):
        raise ValueError(f"artifact {claim['id']!r} must be a JSON object")
    kind = claim["artifact_kind"]
    prefixes = ARTIFACT_SCHEMA_PREFIXES.get(kind)
    if prefixes is None:
        raise ValueError(f"artifact {claim['id']!r} has unsupported kind {kind!r}")
    schema = value.get("schema_version")
    if schema != claim["schema_version"] or not any(
        isinstance(schema, str) and schema.startswith(prefix) for prefix in prefixes
    ):
        raise ValueError(f"artifact {claim['id']!r} machine schema does not agree")


def _validate_sha(value: object, label: str) -> None:
    if not isinstance(value, str) or not HEX_SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase SHA-256")


def validate_and_index_ledger(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if ledger.get("schema_version") != LEDGER_SCHEMA:
        raise ValueError(f"ledger schema_version must be {LEDGER_SCHEMA!r}")
    generators = ledger.get("trusted_generators")
    if not isinstance(generators, list) or not generators:
        raise ValueError("trusted_generators must be a nonempty list")
    indexed: dict[str, dict[str, Any]] = {}
    for row in generators:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("each trusted generator needs a string id")
        if row["id"] in indexed:
            raise ValueError(f"duplicate generator id {row['id']!r}")
        repo = Path(row["repo"])
        exact_commit(repo, row["ref"], f"generator {row['id']} ref")
        _validate_sha(row.get("sha256"), f"generator {row['id']} sha256")
        raw = git(repo, "show", f"{row['ref']}:{row['path']}")
        if sha256(raw) != row["sha256"]:
            raise ValueError(f"generator {row['id']!r} content hash mismatch")
        indexed[row["id"]] = row

    outputs = ledger.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("outputs must be a nonempty list")
    seen: set[str] = set()
    for claim in outputs:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            raise ValueError("each output claim needs a string id")
        if claim["id"] in seen:
            raise ValueError(f"duplicate output id {claim['id']!r}")
        seen.add(claim["id"])
        if claim.get("generator_id") not in indexed:
            raise ValueError(f"output {claim['id']!r} has unknown generator")
        _validate_sha(claim.get("content_sha256"), f"output {claim['id']} content_sha256")
        if not isinstance(claim.get("byte_count"), int) or claim["byte_count"] < 1:
            raise ValueError(f"output {claim['id']!r} needs a positive byte_count")
        paths = claim.get("git_paths", [])
        invocations = claim.get("invocation_sha256s", [])
        if not isinstance(paths, list) or not all(isinstance(x, str) and x for x in paths):
            raise ValueError(f"output {claim['id']!r} git_paths must be strings")
        if not isinstance(invocations, list):
            raise ValueError(f"output {claim['id']!r} invocation_sha256s must be a list")
        for digest in invocations:
            _validate_sha(digest, f"output {claim['id']} invocation_sha256")
        if not paths and not invocations:
            raise ValueError(f"output {claim['id']!r} has no bounded discovery route")
        # Check kind/schema policy before any source is searched.
        prefixes = ARTIFACT_SCHEMA_PREFIXES.get(claim.get("artifact_kind"))
        if prefixes is None or not any(
            isinstance(claim.get("schema_version"), str)
            and claim["schema_version"].startswith(prefix)
            for prefix in prefixes
        ):
            raise ValueError(f"output {claim['id']!r} has unsupported kind/schema")
    return indexed


def validate_sources(config: dict[str, Any]) -> None:
    if config.get("schema_version") != SOURCE_SCHEMA:
        raise ValueError(f"source schema_version must be {SOURCE_SCHEMA!r}")
    sources = config.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("sources must be a nonempty list")
    ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            raise ValueError("each source needs a string id")
        if source["id"] in ids:
            raise ValueError(f"duplicate source id {source['id']!r}")
        ids.add(source["id"])
        if source.get("kind") not in {"git", "git_sessions"}:
            raise ValueError(f"unsupported source kind {source.get('kind')!r}")
        repo = Path(source["path"])
        if source["kind"] == "git":
            tips = source.get("tips")
            if not isinstance(tips, list) or not tips:
                raise ValueError(f"git source {source['id']!r} needs exact tips")
            for tip in tips:
                exact_commit(repo, tip, f"source {source['id']} tip")
        else:
            exact_commit(repo, source["ref"], f"source {source['id']} ref")
            if source.get("format") not in {"codex", "claude"}:
                raise ValueError(f"session source {source['id']!r} has bad format")
            if not isinstance(source.get("subdir"), str):
                raise ValueError(f"session source {source['id']!r} needs subdir")


def _claim_accepts(claim: dict[str, Any], raw: bytes) -> bool:
    if len(raw) != claim["byte_count"] or sha256(raw) != claim["content_sha256"]:
        return False
    validate_machine_artifact(raw, claim)
    return True


def iter_git_matches(
    source: dict[str, Any], claims: list[dict[str, Any]]
) -> Iterator[dict[str, Any]]:
    repo = Path(source["path"])
    by_path: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        for path in claim.get("git_paths", []):
            by_path.setdefault(path, []).append(claim)
    seen: set[tuple[str, str, str]] = set()
    for path in sorted(by_path):
        commits = git(repo, "rev-list", *source["tips"], "--", path).decode().splitlines()
        for commit in commits:
            try:
                blob = git(repo, "rev-parse", f"{commit}:{path}").decode().strip()
                raw = git(repo, "show", f"{commit}:{path}")
            except subprocess.CalledProcessError:
                continue
            for claim in by_path[path]:
                key = (claim["id"], blob, path)
                if key in seen or not _claim_accepts(claim, raw):
                    continue
                seen.add(key)
                locator = f"git-blob:{blob}:{path}"
                role = "machine-generated-git-blob"
                yield {
                    "claim_id": claim["id"],
                    "artifact_kind": claim["artifact_kind"],
                    "generator_id": claim["generator_id"],
                    "source_id": source["id"],
                    "source_kind": "git",
                    "locator": locator,
                    "role": role,
                    "content_schema": claim["schema_version"],
                    "content_sha256": claim["content_sha256"],
                    "byte_count": len(raw),
                    "unit_identity_sha256": unit_identity_sha256(
                        source["id"], locator, role, claim["content_sha256"]
                    ),
                    "producer_verified": True,
                    "invocation_contract_verified": True,
                    "output_digest_verified": True,
                    "bounded_schema_verified": True,
                    "mixed_unit_rejected": True,
                }


def _content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    values = []
    for block in content:
        if isinstance(block, dict) and block.get("type") in {
            "text", "input_text", "output_text"
        } and isinstance(block.get("text"), str):
            values.append(block["text"])
    return "\n".join(values)


def codex_tool_units(rows: list[dict[str, Any]], relative: str) -> Iterator[dict[str, Any]]:
    calls: dict[str, tuple[str, object]] = {}
    for line_number, row in enumerate(rows, 1):
        payload = row.get("payload", {})
        if row.get("type") != "response_item" or not isinstance(payload, dict):
            continue
        if payload.get("type") == "function_call" and isinstance(payload.get("call_id"), str):
            arguments: object = payload.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    continue
            calls[payload["call_id"]] = (str(payload.get("name", "")), arguments)
        elif payload.get("type") == "function_call_output":
            call = calls.get(payload.get("call_id"))
            output = payload.get("output")
            if call and isinstance(output, str):
                yield {
                    "locator": f"{relative}:{line_number}",
                    "role": "codex-tool-output",
                    "raw": output.encode("utf-8", "surrogatepass"),
                    "invocation_sha256": invocation_sha256(*call),
                }


def claude_tool_units(rows: list[dict[str, Any]], relative: str) -> Iterator[dict[str, Any]]:
    calls: dict[str, tuple[str, object]] = {}
    for line_number, row in enumerate(rows, 1):
        content = row.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        if row.get("type") == "assistant":
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use" and isinstance(block.get("id"), str):
                    calls[block["id"]] = (str(block.get("name", "")), block.get("input"))
        elif row.get("type") == "user":
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                call = calls.get(block.get("tool_use_id"))
                output = _content_text(block.get("content"))
                if call and output:
                    yield {
                        "locator": f"{relative}:{line_number}",
                        "role": "claude-tool-output",
                        "raw": output.encode("utf-8", "surrogatepass"),
                        "invocation_sha256": invocation_sha256(*call),
                    }


def iter_session_matches(
    source: dict[str, Any], claims: list[dict[str, Any]]
) -> Iterator[dict[str, Any]]:
    repo = Path(source["path"])
    names = git(
        repo, "ls-tree", "-r", "--name-only", source["ref"], "--", source["subdir"]
    ).decode().splitlines()
    by_invocation: dict[str, list[dict[str, Any]]] = {}
    for claim in claims:
        for digest in claim.get("invocation_sha256s", []):
            by_invocation.setdefault(digest, []).append(claim)
    parser = codex_tool_units if source["format"] == "codex" else claude_tool_units
    for relative in sorted(path for path in names if path.endswith(".jsonl")):
        raw = git(repo, "show", f"{source['ref']}:{relative}")
        rows = []
        for line in raw.decode("utf-8", "strict").splitlines():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                # Preserve physical line numbers.  A malformed row cannot prove
                # a tool role/call pairing, but deleting it would change every
                # later locator and therefore the unit-identity hash.
                value = {}
            rows.append(value if isinstance(value, dict) else {})
        for unit in parser(rows, relative):
            for claim in by_invocation.get(unit["invocation_sha256"], []):
                if not _claim_accepts(claim, unit["raw"]):
                    continue
                content_sha = sha256(unit["raw"])
                yield {
                    "claim_id": claim["id"],
                    "artifact_kind": claim["artifact_kind"],
                    "generator_id": claim["generator_id"],
                    "source_id": source["id"],
                    "source_kind": "git_sessions",
                    "locator": unit["locator"],
                    "role": unit["role"],
                    "content_schema": claim["schema_version"],
                    "content_sha256": content_sha,
                    "byte_count": len(unit["raw"]),
                    "invocation_sha256": unit["invocation_sha256"],
                    "unit_identity_sha256": unit_identity_sha256(
                        source["id"], unit["locator"], unit["role"], content_sha
                    ),
                    "producer_verified": True,
                    "invocation_contract_verified": True,
                    "output_digest_verified": True,
                    "bounded_schema_verified": True,
                    "mixed_unit_rejected": True,
                }


def quota_feasibility(pool: dict[str, Any], quotas: dict[str, int]) -> dict[str, Any]:
    """Report feasibility from emitted pool metadata only."""

    rows = pool.get("clusters")
    if not isinstance(rows, list):
        raise ValueError("pool.clusters must be a list")
    counts = Counter(
        row.get("stratum")
        for row in rows
        if isinstance(row, dict) and row.get("eligible") is True
    )
    strata = []
    for stratum, quota in quotas.items():
        if not isinstance(quota, int) or quota < 0:
            raise ValueError("quotas must be nonnegative integers")
        eligible = counts[stratum]
        strata.append(
            {
                "stratum": stratum,
                "quota": quota,
                "eligible_count": eligible,
                "surplus": max(0, eligible - quota),
                "deficit": max(0, quota - eligible),
                "quota_satisfied": eligible >= quota,
            }
        )
    return {
        "pool_schema_version": pool.get("schema_version"),
        "pool_sha256": sha256(canonical_json(pool)),
        "eligible_cluster_count": sum(counts.values()),
        "required_cluster_count": sum(quotas.values()),
        "all_quotas_satisfied": all(row["quota_satisfied"] for row in strata),
        "strata": strata,
    }


def build(
    ledger: dict[str, Any],
    sources: dict[str, Any],
    *,
    pool: dict[str, Any] | None = None,
    quotas: dict[str, int] | None = None,
) -> dict[str, Any]:
    validate_and_index_ledger(ledger)
    validate_sources(sources)
    claims = ledger["outputs"]
    matches = []
    source_audit = []
    for source in sources["sources"]:
        try:
            found = list(
                iter_git_matches(source, claims)
                if source["kind"] == "git"
                else iter_session_matches(source, claims)
            )
            matches.extend(found)
            source_audit.append(
                {"id": source["id"], "kind": source["kind"], "complete": True, "matches": len(found), "failure": None}
            )
        except Exception as exc:
            source_audit.append(
                {"id": source["id"], "kind": source.get("kind"), "complete": False, "matches": 0, "failure": f"{type(exc).__name__}: {exc}"}
            )
    matched_claims = {row["claim_id"] for row in matches}
    unmatched = sorted(claim["id"] for claim in claims if claim["id"] not in matched_claims)
    complete = all(row["complete"] for row in source_audit) and not unmatched
    unique = {row["unit_identity_sha256"]: row for row in matches}
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "policy": {
            "decision_input": "REGISTRY_AND_PROVENANCE_METADATA_ONLY",
            "statement_text_inspected": False,
            "discussion_roles_exemptible": False,
            "exemption_key": "SHA256_CANONICAL_JSON_SOURCE_ID_LOCATOR_ROLE_CONTENT_SHA256",
            "global_content_hash_allowlist": False,
        },
        "ledger_sha256": sha256(canonical_json(ledger)),
        "sources_sha256": sha256(canonical_json(sources)),
        "source_audit": source_audit,
        "complete": complete,
        "unmatched_claim_ids": unmatched,
        "units": sorted(unique.values(), key=lambda row: row["unit_identity_sha256"]),
        "registry_only_unit_identity_sha256": sorted(unique),
    }
    if pool is not None:
        result["quota_feasibility"] = quota_feasibility(pool, quotas or DEFAULT_QUOTAS)
    result["inventory_sha256"] = sha256(canonical_json(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--pool", type=Path)
    parser.add_argument("--quotas", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8")) if args.pool else None
    quotas = json.loads(args.quotas.read_text(encoding="utf-8")) if args.quotas else None
    result = build(ledger, sources, pool=pool, quotas=quotas)
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
