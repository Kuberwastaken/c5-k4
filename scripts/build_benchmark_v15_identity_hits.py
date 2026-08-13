#!/usr/bin/env python3
"""Build the private Method v1.5 target-identity/exposure join.

This executable is deliberately pre-selection and private.  It reopens the
content addressed bytes behind excluding provenance units, verifies those
bytes, and performs only exact, boundary-delimited comparisons against the
machine-generated aliases of future-cohort clusters.  It never emits source
text or the matched alias value.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from typing import Any


SCHEMA = "c5k4-method-v1.5-private-identity-hit-ledger-1.0"
CONTENT_PACK_SCHEMA = "c5k4-method-v1.5-private-provenance-content-pack-1.0"
EXCLUDING_CLASSES = {"SEMANTIC_EXPOSURE", "UNKNOWN"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
# These are the characters from which every frozen alias is composed.  Using
# this common alphabet prevents `foo` from matching `foo_extra` and a target
# path from matching a longer path while still recognizing quoted JSON/text.
ALIAS_CHAR = r"\w./'\-"
MAX_TARGETS = 100_000
MAX_EXCLUDING_UNITS = 1_000_000
MAX_BINDINGS = 100_000


class IdentityHitError(ValueError):
    """A fail-closed identity-hit contract violation."""


def canonical_json(value: Any) -> bytes:
    # Source/provenance ledgers freeze the v1.4 canonical newline convention.
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def content_address(value: dict[str, Any], field: str) -> str:
    unsigned = dict(value)
    unsigned.pop(field, None)
    return sha256(canonical_json(unsigned))


def load_content_pack(pack: dict[str, Any]) -> dict[str, bytes]:
    if set(pack) != {"schema", "publication_permitted", "entries"} or (
        pack.get("schema") != CONTENT_PACK_SCHEMA or pack.get("publication_permitted") is not False
    ):
        raise IdentityHitError("unsupported or non-strict private provenance content pack")
    entries = pack.get("entries")
    if not isinstance(entries, list):
        raise IdentityHitError("private provenance content pack has no entries")
    contents: dict[str, bytes] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"content_sha256", "content_base64"}:
            raise IdentityHitError("private provenance content entry is malformed")
        digest, encoded = entry["content_sha256"], entry["content_base64"]
        if not isinstance(digest, str) or HEX64.fullmatch(digest) is None or not isinstance(encoded, str):
            raise IdentityHitError("private provenance content entry identity is malformed")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, UnicodeError) as exc:
            raise IdentityHitError("private provenance content is not canonical base64") from exc
        if sha256(raw) != digest:
            raise IdentityHitError("private provenance content digest mismatch")
        if digest in contents:
            raise IdentityHitError("duplicate private provenance content digest")
        contents[digest] = raw
    return contents


def _ledger_units(ledgers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not ledgers:
        raise IdentityHitError("at least one complete provenance ledger is required")
    result: list[dict[str, Any]] = []
    seen_units: set[str] = set()
    for ledger in ledgers:
        supplied = ledger.get("ledger_sha256")
        if not isinstance(supplied, str) or supplied != content_address(ledger, "ledger_sha256"):
            raise IdentityHitError("provenance ledger self-digest is invalid")
        if ledger.get("source_complete") is not True or ledger.get("status") not in {
            "CLASSIFIED_COMPLETE", "CLASSIFIED_FAIL_CLOSED",
        }:
            raise IdentityHitError("provenance ledger is incomplete or unclassified")
        if not isinstance(ledger.get("fail_closed"), bool) or (
            ledger["status"] == "CLASSIFIED_FAIL_CLOSED"
        ) != ledger["fail_closed"]:
            raise IdentityHitError("provenance ledger fail-closed status is inconsistent")
        units = ledger.get("units")
        if not isinstance(units, list):
            raise IdentityHitError("provenance ledger units are absent")
        for unit in units:
            if not isinstance(unit, dict):
                raise IdentityHitError("provenance unit is malformed")
            unit_id, digest, provenance_class = (
                unit.get("unit_id"), unit.get("content_sha256"), unit.get("provenance_class")
            )
            if not isinstance(unit_id, str) or not unit_id or unit_id in seen_units:
                raise IdentityHitError("provenance unit identity is absent or duplicated")
            if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
                raise IdentityHitError("provenance unit content digest is malformed")
            if provenance_class not in {
                "SEMANTIC_EXPOSURE", "MACHINE_REGISTRY_CONTACT",
                "IMMUTABLE_SOURCE_CUSTODY", "UNKNOWN",
            }:
                raise IdentityHitError("provenance unit class is invalid")
            seen_units.add(unit_id)
            if provenance_class in EXCLUDING_CLASSES:
                result.append(unit)
        replay_counts = {
            name: sum(unit.get("provenance_class") == name for unit in units)
            for name in (
                "SEMANTIC_EXPOSURE", "MACHINE_REGISTRY_CONTACT",
                "IMMUTABLE_SOURCE_CUSTODY", "UNKNOWN",
            )
        }
        if ledger.get("counts") != replay_counts:
            raise IdentityHitError("provenance ledger counts do not replay")
    return result


def _aliases(row: dict[str, Any]) -> list[tuple[str, str]]:
    aliases: list[tuple[str, str]] = []
    for field, kind in (
        ("cluster_id", "CLUSTER_ID"), ("path", "MODULE_PATH"),
        ("identity_sha256", "IDENTITY_SHA256"),
        ("module_blob_sha256", "MODULE_BLOB_SHA256"),
    ):
        value = row.get(field)
        if not isinstance(value, str) or not value:
            raise IdentityHitError(f"target row has invalid {field}")
        aliases.append((value, kind))
    declarations = row.get("declarations")
    if not isinstance(declarations, list) or not declarations:
        raise IdentityHitError("target row has no declarations")
    for declaration in declarations:
        if not isinstance(declaration, dict):
            raise IdentityHitError("target declaration is malformed")
        for field, kind in (
            ("name", "DECLARATION_NAME"),
            ("statement_header_sha256", "STATEMENT_HEADER_SHA256"),
        ):
            value = declaration.get(field)
            if not isinstance(value, str) or not value:
                raise IdentityHitError(f"target declaration has invalid {field}")
            aliases.append((value, kind))
    return aliases


def target_set_sha256(targets: list[dict[str, Any]]) -> str:
    if len(targets) > MAX_TARGETS:
        raise IdentityHitError("target count exceeds the frozen private-join bound")
    projection = []
    seen: set[str] = set()
    for row in sorted(targets, key=lambda value: value.get("cluster_id", "")):
        cluster_id = row.get("cluster_id")
        if not isinstance(cluster_id, str) or cluster_id in seen:
            raise IdentityHitError("target cluster identity is absent or duplicated")
        seen.add(cluster_id)
        projection.append({"cluster_id": cluster_id, "aliases": _aliases(row)})
    return sha256(canonical_json(projection))


def _exact_hit(raw: bytes, alias: str) -> bool:
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise IdentityHitError("excluding provenance content is not UTF-8") from exc
    pattern = rf"(?<![{ALIAS_CHAR}]){re.escape(alias)}(?![{ALIAS_CHAR}])"
    return re.search(pattern, text) is not None


def build(targets: list[dict[str, Any]], ledgers: list[dict[str, Any]], contents: dict[str, bytes]) -> dict[str, Any]:
    units = _ledger_units(ledgers)
    if len(units) > MAX_EXCLUDING_UNITS:
        raise IdentityHitError("excluding unit count exceeds the frozen private-join bound")
    required_digests = {unit["content_sha256"] for unit in units}
    missing = required_digests - contents.keys()
    if missing:
        raise IdentityHitError("excluding provenance content is unavailable")
    # Reverify every reopened byte stream even when a loader already checked it.
    for digest in required_digests:
        if sha256(contents[digest]) != digest:
            raise IdentityHitError("reopened provenance content digest mismatch")

    clusters = []
    binding_count = 0
    for row in sorted(targets, key=lambda value: value["cluster_id"]):
        bindings = []
        aliases = _aliases(row)
        for unit in sorted(units, key=lambda value: value["unit_id"]):
            kinds = sorted({kind for alias, kind in aliases if _exact_hit(contents[unit["content_sha256"]], alias)})
            if kinds:
                bindings.append({
                    "unit_id": unit["unit_id"],
                    "provenance_class": unit["provenance_class"],
                    "matched_alias_kinds": kinds,
                })
        if bindings:
            clusters.append({
                "cluster_id": row["cluster_id"],
                "identity_sha256": row["identity_sha256"],
                "bindings": bindings,
            })
            binding_count += len(bindings)
            if binding_count > MAX_BINDINGS:
                raise IdentityHitError("identity binding count exceeds the frozen private-join bound")
    output: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "VERIFIED_COMPLETE_PRIVATE_IDENTITY_JOIN",
        "controls": {
            "public_artifact_permitted": False,
            "raw_content_present": False,
            "matched_alias_values_present": False,
            "matching_rule": "UTF8_EXACT_BOUNDARY_DELIMITED_FROZEN_ALIAS",
        },
        "target_set_sha256": target_set_sha256(targets),
        "target_count": len(targets),
        "excluding_unit_count": len(units),
        "binding_count": binding_count,
        "clusters": clusters,
    }
    output["identity_hits_sha256"] = content_address(output, "identity_hits_sha256")
    return output


def exclusion_reasons(row: dict[str, Any], identity_hits: dict[str, Any]) -> set[str]:
    if identity_hits.get("identity_hits_sha256") != content_address(identity_hits, "identity_hits_sha256"):
        raise IdentityHitError("private identity-hit ledger digest is invalid")
    matches = [entry for entry in identity_hits.get("clusters", []) if entry.get("cluster_id") == row.get("cluster_id")]
    if len(matches) > 1:
        raise IdentityHitError("private identity-hit ledger duplicates a cluster")
    reasons: set[str] = set()
    if matches:
        for binding in matches[0]["bindings"]:
            reasons.add("SEMANTIC_EXPOSURE" if binding["provenance_class"] == "SEMANTIC_EXPOSURE" else "UNKNOWN_EXPOSURE")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--provenance-ledger", type=Path, action="append", required=True)
    parser.add_argument("--content-pack", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise IdentityHitError("output already exists; overwrite is forbidden")
    targets_value = json.loads(args.targets.read_bytes())
    targets = targets_value.get("records") if isinstance(targets_value, dict) else None
    if not isinstance(targets, list):
        raise IdentityHitError("targets input has no records array")
    ledgers = [json.loads(path.read_bytes()) for path in args.provenance_ledger]
    contents = load_content_pack(json.loads(args.content_pack.read_bytes()))
    output = build(targets, ledgers, contents)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
