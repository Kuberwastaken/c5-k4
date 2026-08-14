#!/usr/bin/env python3
"""Build and audit the target-blind TxGraffiti C-C phase-four domain.

This module deliberately knows nothing about the conjecture objective.  It
maps the 5,320 frozen phase-three construction states to exact nauty graph
identities, deduplicates them once, and writes disjoint identity partitions.
The separate selector reads only identity fields from earlier scientific
ledgers when it removes already-scored graphs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Sequence

import networkx as nx

import method_v15_live_search_runtime as live
import search_txgraffiti_cc_phase2 as phase2
import search_txgraffiti_cc_phase3 as phase3


DOMAIN_SCHEMA = "c5k4-txgraffiti-cc-phase4-domain-1.0"
STATE_SCHEMA = "c5k4-txgraffiti-cc-phase4-construction-state-1.0"
IDENTITY_SCHEMA = "c5k4-txgraffiti-cc-phase4-canonical-identity-1.0"
SELECTION_SCHEMA = "c5k4-txgraffiti-cc-phase4-selection-1.0"
PARTITION_COUNT = 24
EXPECTED_STATES = 5320


class Phase4DomainError(ValueError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl(path: Path, rows: Iterable[Mapping[str, object]]) -> int:
    count = 0
    with path.open("xb") as stream:
        for row in rows:
            stream.write(canonical_json(dict(row)))
            count += 1
        stream.flush()
    return count


def load_jsonl(path: Path) -> Iterator[dict[str, object]]:
    with path.open("rb") as stream:
        for line_number, raw in enumerate(stream, 1):
            if not raw.endswith(b"\n"):
                raise Phase4DomainError(f"{path}:{line_number}: truncated JSONL row")
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise Phase4DomainError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict) or raw != canonical_json(row):
                raise Phase4DomainError(f"{path}:{line_number}: row is not canonical JSON")
            yield row


def construction_records() -> list[dict[str, object]]:
    """Enumerate the frozen quotient states without computing the target."""
    rows: list[dict[str, object]] = []
    for encoded in phase3.BASE_GRAPH6:
        graph = nx.from_graph6_bytes(encoded.encode("ascii"))
        for pairing in phase3.pairing_orbit_representatives(graph):
            material = (encoded + "|" + repr(pairing)).encode("ascii")
            rows.append({
                "state_key_sha256": hashlib.sha256(material).hexdigest(),
                "base_graph6": encoded,
                "pairing": [list(pair) for pair in pairing],
            })
    rows.sort(key=lambda row: str(row["state_key_sha256"]))
    if len(rows) != EXPECTED_STATES:
        raise Phase4DomainError(f"frozen constructor produced {len(rows)}, expected {EXPECTED_STATES}")
    if len({str(row["state_key_sha256"]) for row in rows}) != EXPECTED_STATES:
        raise Phase4DomainError("construction-state keys are not unique")
    return rows


def graph_from_record(row: Mapping[str, object]):
    encoded = str(row["base_graph6"])
    graph = nx.from_graph6_bytes(encoded.encode("ascii"))
    raw_pairing = row["pairing"]
    if not isinstance(raw_pairing, list):
        raise Phase4DomainError("state pairing is not a list")
    pairing = phase2.normalized_pairing([
        (int(pair[0]), int(pair[1])) for pair in raw_pairing
    ])
    return phase2.build_graph(phase2.state_from_base(
        graph, pairing, f"phase4_t2_base_{encoded}_pairing_orbit"
    ))


def partition_for(canonical_sha256: str, partition_count: int = PARTITION_COUNT) -> int:
    if len(canonical_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in canonical_sha256):
        raise Phase4DomainError("canonical identity is not a lowercase SHA-256")
    if partition_count < 1:
        raise Phase4DomainError("partition count must be positive")
    return int(canonical_sha256, 16) % partition_count


def _file_record(root: Path, path: Path, rows: int) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "rows": rows,
        "sha256": sha256_file(path),
    }


def build_domain(output: Path, labelg: Path, *, partition_count: int = PARTITION_COUNT) -> dict[str, object]:
    """Build the complete target-blind state-to-identity manifest."""
    output = output.resolve()
    if output.exists():
        raise Phase4DomainError("domain output must not pre-exist")
    output.mkdir(parents=True)
    partitions_dir = output / "identity-partitions"
    partitions_dir.mkdir()
    canonicalizer = live.LabelgCanonicalizer(labelg)

    state_rows: list[dict[str, object]] = []
    identities: dict[str, dict[str, object]] = {}
    for state in construction_records():
        graph = graph_from_record(state)
        canonical = canonicalizer.canonicalize(graph)
        partition = partition_for(canonical.sha256, partition_count)
        state_row = {
            "schema": STATE_SCHEMA,
            **state,
            "canonical_graph6": canonical.graph6,
            "canonical_sha256": canonical.sha256,
            "partition": partition,
        }
        state_rows.append(state_row)
        identity = identities.get(canonical.sha256)
        if identity is None:
            identities[canonical.sha256] = {
                "schema": IDENTITY_SCHEMA,
                "canonical_graph6": canonical.graph6,
                "canonical_sha256": canonical.sha256,
                "partition": partition,
                "construction_multiplicity": 1,
                "representative_state": {
                    "state_key_sha256": state["state_key_sha256"],
                    "base_graph6": state["base_graph6"],
                    "pairing": state["pairing"],
                },
            }
        else:
            identity["construction_multiplicity"] = int(identity["construction_multiplicity"]) + 1

    identity_rows = sorted(identities.values(), key=lambda row: str(row["canonical_sha256"]))
    states_path = output / "construction-states.jsonl"
    identities_path = output / "canonical-identities.jsonl"
    files: dict[str, object] = {
        "construction_states": _file_record(output, states_path, write_jsonl(states_path, state_rows)),
        "canonical_identities": _file_record(output, identities_path, write_jsonl(identities_path, identity_rows)),
        "partitions": [],
    }
    partition_files: list[dict[str, object]] = []
    for partition in range(partition_count):
        path = partitions_dir / f"partition-{partition:02d}.jsonl"
        rows = [row for row in identity_rows if int(row["partition"]) == partition]
        partition_files.append({
            "partition": partition,
            **_file_record(output, path, write_jsonl(path, rows)),
        })
    files["partitions"] = partition_files
    manifest = {
        "schema": DOMAIN_SCHEMA,
        "terminal_reason": "DOMAIN_EXHAUSTED",
        "target_blind": True,
        "target_fields_forbidden": ["objective", "crossing", "independent_domination", "minimum_maximal_matching"],
        "construction_states_expected": EXPECTED_STATES,
        "construction_states_scanned": len(state_rows),
        "canonical_identity_count": len(identity_rows),
        "construction_multiplicity_sum": sum(int(row["construction_multiplicity"]) for row in identity_rows),
        "partition_count": partition_count,
        "partition_rule": "int(canonical_sha256,16) mod partition_count",
        "canonicalization": "nauty labelg exact canonical graph6",
        "labelg_sha256": sha256_file(labelg),
        "files": files,
    }
    (output / "domain-manifest.json").write_bytes(canonical_json(manifest))
    verify_domain(output)
    return manifest


def scored_identities(paths: Iterable[Path]) -> tuple[set[str], list[dict[str, object]]]:
    """Read only canonical identities from prior scientific ledgers."""
    scored: set[str] = set()
    sources: list[dict[str, object]] = []
    for path in sorted({item.resolve() for item in paths}):
        rows = 0
        for row in load_jsonl(path):
            if row.get("kind") != "evaluated_candidate":
                continue
            digest = str(row.get("canonical_sha256", ""))
            partition_for(digest)
            scored.add(digest)
            rows += 1
        try:
            display_path = path.relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            display_path = path.name
        sources.append({"path": display_path, "evaluated_rows": rows, "sha256": sha256_file(path)})
    return scored, sources


def unscored_partition_rows(
    rows: Iterable[Mapping[str, object]], scored: set[str], partition: int
) -> list[dict[str, object]]:
    retained: list[dict[str, object]] = []
    prior = ""
    for raw in rows:
        row = dict(raw)
        digest = str(row.get("canonical_sha256", ""))
        if row.get("schema") != IDENTITY_SCHEMA or partition_for(digest) != partition:
            raise Phase4DomainError("domain partition contains a misassigned identity")
        if digest <= prior:
            raise Phase4DomainError("domain partition identities are not strictly sorted")
        prior = digest
        if digest not in scored:
            retained.append(row)
    return retained


def select_unscored(
    domain: Path,
    output: Path,
    scored_ledgers: Iterable[Path],
) -> dict[str, object]:
    domain = domain.resolve()
    output = output.resolve()
    if output.exists():
        raise Phase4DomainError("selection output must not pre-exist")
    manifest = verify_domain(domain)
    output.mkdir(parents=True)
    scored, sources = scored_identities(scored_ledgers)
    domain_ids: set[str] = set()
    partitions: list[dict[str, object]] = []
    for file_row in manifest["files"]["partitions"]:
        partition = int(file_row["partition"])
        source = domain / str(file_row["path"])
        source_rows = list(load_jsonl(source))
        for row in source_rows:
            digest = str(row["canonical_sha256"])
            domain_ids.add(digest)
        retained = unscored_partition_rows(source_rows, scored, partition)
        target = output / f"work-partition-{partition:02d}.jsonl"
        partitions.append({
            "partition": partition,
            "domain_rows": int(file_row["rows"]),
            "already_scored_rows": int(file_row["rows"]) - len(retained),
            **_file_record(output, target, write_jsonl(target, retained)),
        })
    selection = {
        "schema": SELECTION_SCHEMA,
        "domain_manifest_sha256": sha256_file(domain / "domain-manifest.json"),
        "domain_identity_count": int(manifest["canonical_identity_count"]),
        "scored_identity_count_in_domain": len(scored & domain_ids),
        "unscored_identity_count": sum(int(row["rows"]) for row in partitions),
        "scored_sources": sources,
        "partitions": partitions,
    }
    (output / "selection-manifest.json").write_bytes(canonical_json(selection))
    verify_selection(domain, output)
    return selection


def _verify_file(root: Path, record: Mapping[str, object]) -> Path:
    path = root / str(record["path"])
    if not path.is_file() or sha256_file(path) != record.get("sha256"):
        raise Phase4DomainError(f"file authority mismatch: {path}")
    if sum(1 for _ in load_jsonl(path)) != record.get("rows"):
        raise Phase4DomainError(f"row count mismatch: {path}")
    return path


def verify_domain(root: Path) -> dict[str, object]:
    root = root.resolve()
    manifest_path = root / "domain-manifest.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    if manifest_raw != canonical_json(manifest):
        raise Phase4DomainError("domain manifest is not canonical JSON")
    if manifest.get("schema") != DOMAIN_SCHEMA or manifest.get("target_blind") is not True:
        raise Phase4DomainError("domain manifest identity is invalid")
    if manifest.get("terminal_reason") != "DOMAIN_EXHAUSTED":
        raise Phase4DomainError("domain manifest is not an exhausted finite enumeration")
    if manifest.get("construction_states_scanned") != EXPECTED_STATES:
        raise Phase4DomainError("domain did not scan all 5,320 construction states")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise Phase4DomainError("domain file inventory is missing")
    states = list(load_jsonl(_verify_file(root, files["construction_states"])))
    identities = list(load_jsonl(_verify_file(root, files["canonical_identities"])))
    forbidden = set(manifest["target_fields_forbidden"])
    if any(forbidden.intersection(row) for row in states + identities):
        raise Phase4DomainError("target-bearing field leaked into target-blind domain")
    state_keys = {str(row["state_key_sha256"]) for row in states}
    identity_ids = {str(row["canonical_sha256"]) for row in identities}
    if len(states) != EXPECTED_STATES or len(state_keys) != EXPECTED_STATES:
        raise Phase4DomainError("construction-state coverage is not exact")
    if len(identity_ids) != len(identities) or len(identities) != manifest["canonical_identity_count"]:
        raise Phase4DomainError("canonical identities are not globally deduplicated")
    if sum(int(row["construction_multiplicity"]) for row in identities) != EXPECTED_STATES:
        raise Phase4DomainError("identity multiplicities do not cover the construction domain")
    actual_multiplicities: dict[str, int] = {}
    state_identity: dict[str, str] = {}
    prior_state_key = ""
    for row in states:
        state_key = str(row["state_key_sha256"])
        digest = str(row["canonical_sha256"])
        graph6 = str(row["canonical_graph6"])
        expected_digest = hashlib.sha256(
            b"c5k4-exact-canonical-graph6-v1\0" + graph6.encode("ascii")
        ).hexdigest()
        if state_key <= prior_state_key or digest != expected_digest or digest not in identity_ids:
            raise Phase4DomainError("state map order or canonical identity binding is invalid")
        prior_state_key = state_key
        state_identity[state_key] = digest
        actual_multiplicities[digest] = actual_multiplicities.get(digest, 0) + 1
    for row in identities:
        digest = str(row["canonical_sha256"])
        graph6 = str(row["canonical_graph6"])
        expected_digest = hashlib.sha256(
            b"c5k4-exact-canonical-graph6-v1\0" + graph6.encode("ascii")
        ).hexdigest()
        representative = row.get("representative_state")
        if not isinstance(representative, dict):
            raise Phase4DomainError("canonical identity lacks a representative state")
        state_key = str(representative.get("state_key_sha256", ""))
        if digest != expected_digest or state_identity.get(state_key) != digest:
            raise Phase4DomainError("canonical identity is not bound to its representative state")
        if actual_multiplicities.get(digest) != int(row["construction_multiplicity"]):
            raise Phase4DomainError("canonical identity multiplicity is incorrect")
    partition_ids: set[str] = set()
    partitions = files.get("partitions")
    if not isinstance(partitions, list) or len(partitions) != manifest["partition_count"]:
        raise Phase4DomainError("partition inventory is incomplete")
    for record in partitions:
        partition = int(record["partition"])
        for row in load_jsonl(_verify_file(root, record)):
            digest = str(row["canonical_sha256"])
            if digest in partition_ids or int(row["partition"]) != partition:
                raise Phase4DomainError("identity partitions overlap or misassign an identity")
            if partition_for(digest, int(manifest["partition_count"])) != partition:
                raise Phase4DomainError("identity violates the frozen partition rule")
            partition_ids.add(digest)
    if partition_ids != identity_ids:
        raise Phase4DomainError("identity partitions do not exhaust the canonical domain")
    return manifest


def verify_selection(domain: Path, selection_root: Path) -> dict[str, object]:
    domain_manifest = verify_domain(domain)
    path = selection_root.resolve() / "selection-manifest.json"
    selection = json.loads(path.read_text(encoding="utf-8"))
    if selection.get("schema") != SELECTION_SCHEMA:
        raise Phase4DomainError("selection manifest identity is invalid")
    if selection.get("domain_manifest_sha256") != sha256_file(domain.resolve() / "domain-manifest.json"):
        raise Phase4DomainError("selection is not bound to this domain")
    seen: set[str] = set()
    for record in selection["partitions"]:
        partition = int(record["partition"])
        for row in load_jsonl(_verify_file(selection_root.resolve(), record)):
            digest = str(row["canonical_sha256"])
            if digest in seen or partition_for(digest, int(domain_manifest["partition_count"])) != partition:
                raise Phase4DomainError("work partitions overlap or contain a misassigned identity")
            seen.add(digest)
    if len(seen) != selection.get("unscored_identity_count"):
        raise Phase4DomainError("unscored work denominator is inconsistent")
    if len(seen) + int(selection.get("scored_identity_count_in_domain", -1)) != int(domain_manifest["canonical_identity_count"]):
        raise Phase4DomainError("scored and unscored identities do not partition the domain")
    return selection


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--labelg", type=Path, required=True)
    build.add_argument("--partition-count", type=int, default=PARTITION_COUNT)
    select = sub.add_parser("select")
    select.add_argument("--domain", type=Path, required=True)
    select.add_argument("--output", type=Path, required=True)
    select.add_argument("--scored-ledger", type=Path, action="append", default=[])
    verify = sub.add_parser("verify")
    verify.add_argument("--domain", type=Path, required=True)
    verify.add_argument("--selection", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            build_domain(args.output, args.labelg, partition_count=args.partition_count)
        elif args.command == "select":
            select_unscored(args.domain, args.output, args.scored_ledger)
        else:
            verify_domain(args.domain)
            if args.selection is not None:
                verify_selection(args.domain, args.selection)
    except (OSError, KeyError, TypeError, ValueError, Phase4DomainError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
