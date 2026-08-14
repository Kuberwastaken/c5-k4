#!/usr/bin/env python3
"""Frozen Graffiti³ Conjecture 23 DEVELOPMENT search.

Importing this module performs no GAP call and evaluates no order-256,
order-512, or wall candidate. Execution is digest-gated by the frozen manifest.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Iterable, Mapping, Sequence


ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
SHARDS = 24
INTERNAL_STOP_SECONDS = 54.0
EXTERNAL_STOP_SECONDS = 60
PER_GAP_QUERY_SECONDS = 4.0
EXPECTED_DATABASE_GATE_COUNT = 2_732
DATABASE_GATE_CHUNKS = 96
DATABASE_GATE_SCHEMA = "c5k4-graffiti3-conjecture23-database-gate-1.0"
DATABASE_GATE_ORDER_COUNTS = {
    1: 1, 2: 1, 3: 1, 4: 2, 5: 1, 7: 1, 8: 5, 9: 2, 11: 1,
    13: 1, 16: 14, 17: 1, 19: 1, 23: 1, 25: 2, 27: 5, 29: 1,
    31: 1, 32: 51, 37: 1, 41: 1, 43: 1, 47: 1, 49: 2, 53: 1,
    59: 1, 61: 1, 64: 267, 67: 1, 71: 1, 73: 1, 79: 1, 81: 15,
    83: 1, 89: 1, 97: 1, 101: 1, 103: 1, 107: 1, 109: 1, 113: 1,
    121: 2, 125: 5, 127: 1, 128: 2_328,
}
CATALOGUE_ORDER = 256
CATALOGUE_COUNT = 56_092
GENERIC_ORDER = 512
GENERIC_COUNT = 10_494_213
GENERIC_LIMIT = 4_096
GENERIC_SEED = "graffiti3-c23-generic-v1"
FREEZE_BASE_COMMIT = "03c6deef4bde0234cfb6db20f7b37d60d15ba9de"
PDF_SHA256 = "9758ec4530febf62bbcee35bd5804d2dda9e226a0878b082a25eaf1c7e4a9f7a"
MANIFEST_SCHEMA = "c5k4-graffiti3-conjecture23-manifest-1.0"
LEDGER_SCHEMA = "c5k4-graffiti3-conjecture23-ledger-1.0"
TERMINAL_SCHEMA = "c5k4-graffiti3-conjecture23-terminal-1.0"
CERTIFICATE_SCHEMA = "c5k4-graffiti3-conjecture23-certificate-1.0"
ZERO_SHA256 = "0" * 64
TERMINAL_REASONS = {
    "DOMAIN_EXHAUSTED", "PROPOSAL_LIMIT", "DEADLINE_PREFIX",
    "CERTIFICATE_FOUND", "SANITY_GATE_FAILED", "WORKER_ERROR",
}

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT / "results" / "expansion" / "live-search-2026-08-14"
    / "graffiti3-conjecture23-manifest.json"
)


class SearchError(ValueError):
    """Frozen input, GAP output, or certificate failure."""


class QueryTimeout(TimeoutError):
    """One separately capped GAP query timed out."""


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json_fsync(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(canonical_json(value))
        handle.flush()
        os.fsync(handle.fileno())


def load_and_verify_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != MANIFEST_SCHEMA:
        raise SearchError("manifest schema drift")
    if value.get("freeze_base_commit") != FREEZE_BASE_COMMIT:
        raise SearchError("freeze base drift")
    if value.get("arms") != list(ARMS) or value.get("shards_per_arm") != SHARDS:
        raise SearchError("arm/shard freeze drift")
    if value.get("internal_stop_seconds") != 54 or value.get("external_stop_seconds") != 60:
        raise SearchError("deadline drift")
    if value.get("per_gap_query_seconds") != 4:
        raise SearchError("GAP query cap drift")
    if value.get("database_gate") != {
        "expected_rows": EXPECTED_DATABASE_GATE_COUNT,
        "chunks": DATABASE_GATE_CHUNKS,
        "shared_preparation_artifact": True,
        "content_addressed": True,
    }:
        raise SearchError("database-gate preparation drift")
    if value.get("source", {}).get("pdf_sha256") != PDF_SHA256:
        raise SearchError("source digest drift")
    expected = {
        "gap": "4.12.1",
        "smallgrp": "1.5.3",
    }
    if value.get("gap_dependencies") != expected:
        raise SearchError("GAP dependency drift")
    for artifact in value.get("artifacts", []):
        target = REPO_ROOT / str(artifact.get("path", ""))
        if not target.is_file() or sha256_file(target) != artifact.get("sha256"):
            raise SearchError(f"artifact digest mismatch: {target}")
    return value


def residual_w(order: int, derived_order: int, center_order: int, classes: int) -> int:
    if min(order, derived_order, center_order, classes) <= 0:
        raise SearchError("group invariants must be positive")
    if order % derived_order:
        raise SearchError("derived subgroup order does not divide group order")
    return 2 * (order // derived_order) + order + 2 * center_order - 4 * classes


@dataclass(frozen=True)
class Profile:
    identity: str
    provenance: str
    order: int
    derived_order: int
    abelianization_order: int
    center_order: int
    conjugacy_classes: int
    residual_w: int
    is_p_group: bool
    gap_expression: str | None = None
    wall_descriptor: Mapping[str, Any] | None = None


@dataclass
class Counters:
    proposed: int = 0
    exact_evaluated: int = 0
    query_timeouts: int = 0
    malformed: int = 0
    crossings: int = 0
    certificates: int = 0


class DurableLedger:
    def __init__(self, path: Path, arm: str, shard: int, campaign_commit: str):
        if arm not in ARMS or not 0 <= shard < SHARDS:
            raise SearchError("invalid ledger assignment")
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.arm = arm
        self.shard = shard
        self.campaign_commit = campaign_commit
        self.sequence = 0
        self.previous = ZERO_SHA256
        self.counters = Counters()
        self.started = time.monotonic()
        if path.exists():
            raise SearchError("ledger path already exists")
        self.emit("start", {"schema": LEDGER_SCHEMA})

    def emit(self, kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA,
            "sequence": self.sequence,
            "previous_row_sha256": self.previous,
            "arm": self.arm,
            "shard": self.shard,
            "campaign_commit": self.campaign_commit,
            "kind": kind,
            "payload": dict(payload),
            "counters": asdict(self.counters),
        }
        row["row_sha256"] = hashlib.sha256(canonical_json(row)).hexdigest()
        with self.path.open("ab") as handle:
            handle.write(canonical_json(row))
            handle.flush()
            os.fsync(handle.fileno())
        self.sequence += 1
        self.previous = row["row_sha256"]
        return row


def write_terminal(path: Path, ledger: DurableLedger, reason: str, extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if reason not in TERMINAL_REASONS:
        raise SearchError("invalid terminal reason")
    ledger.emit("terminal", {"terminal_reason": reason, **dict(extra or {})})
    receipt = {
        "schema": TERMINAL_SCHEMA,
        "terminal_reason": reason,
        "arm": ledger.arm,
        "shard": ledger.shard,
        "campaign_commit": ledger.campaign_commit,
        "ledger_sha256": sha256_file(ledger.path),
        "final_row_sha256": ledger.previous,
        "final_sequence": ledger.sequence - 1,
        "counters": asdict(ledger.counters),
    }
    write_json_fsync(path, receipt)
    return receipt


def gap_profile_source(expression: str, identity: str) -> str:
    # expression is generated only by this frozen module.
    return f'''SetPrintFormattingStatus("*stdout*",false);;
C5K4Profile:=function()
  local G,D,Z;
  G:={expression};; D:=DerivedSubgroup(G);; Z:=Centre(G);;
  Print("@@PROFILE@@\\t{identity}\\t",Size(G),"\\t",Size(D),"\\t",
   Size(FactorGroup(G,D)),"\\t",Size(Z),"\\t",NrConjugacyClasses(G),"\\t",
   IsPGroup(G),"\\t@@END@@\\n");
end;;
C5K4Profile();;
QUIT_GAP(0);
'''


def database_gate_coordinates() -> tuple[tuple[int, int], ...]:
    coordinates = tuple(
        (order, identifier)
        for order, count in DATABASE_GATE_ORDER_COUNTS.items()
        for identifier in range(1, count + 1)
    )
    if len(coordinates) != EXPECTED_DATABASE_GATE_COUNT:
        raise SearchError("frozen database-gate coordinate count drift")
    return coordinates


def database_gate_chunk_coordinates(chunk: int) -> tuple[tuple[int, int], ...]:
    if not 0 <= chunk < DATABASE_GATE_CHUNKS:
        raise SearchError("invalid database-gate chunk")
    coordinates = database_gate_coordinates()
    domain = partition_interval(len(coordinates), DATABASE_GATE_CHUNKS, chunk)
    return tuple(coordinates[index - 1] for index in domain)


def records_sha256(records: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(canonical_json(record))
    return digest.hexdigest()


def coordinate_records(coordinates: Sequence[tuple[int, int]]) -> list[dict[str, int]]:
    return [{"order": order, "id": identifier} for order, identifier in coordinates]


def gap_database_gate_chunk_source(chunk: int, coordinates: Sequence[tuple[int, int]]) -> str:
    gap_coordinates = [[order, identifier] for order, identifier in coordinates]
    return f'''SetPrintFormattingStatus("*stdout*",false);;
C5K4GateChunk:=function(coordinates)
  local coordinate,n,identifier,G,D,Z,w;
  for coordinate in coordinates do
    n:=coordinate[1];; identifier:=coordinate[2];; G:=SmallGroup(n,identifier);;
    D:=DerivedSubgroup(G);; Z:=Centre(G);;
    w:=2*Size(FactorGroup(G,D))+Size(G)+2*Size(Z)-4*NrConjugacyClasses(G);;
    Print("@@GATE_ROW@@\\t",n,"\\t",identifier,"\\t",w,"\\t@@END@@\\n");
  od;
end;;
C5K4GateChunk({gap_coordinates});;
Print("@@GATE_CHUNK@@\\t{chunk}\\t{len(coordinates)}\\t@@END@@\\n");
QUIT_GAP(0);
'''


def run_gap(gap: str, source: str, timeout_seconds: float) -> str:
    timeout_seconds = min(PER_GAP_QUERY_SECONDS, timeout_seconds)
    if timeout_seconds <= 0:
        raise QueryTimeout("deadline reached before GAP query")
    try:
        result = subprocess.run(
            [gap, "-q"], input=source, text=True, capture_output=True,
            timeout=timeout_seconds, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise QueryTimeout("GAP query exceeded separate cap") from exc
    if result.returncode != 0:
        raise SearchError(
            "GAP failed; stdout tail: " + result.stdout[-1000:]
            + "; stderr tail: " + result.stderr[-1000:]
        )
    return result.stdout


def unique_marker(stdout: str, prefix: str) -> str:
    rows = [line for line in stdout.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise SearchError(
            f"expected one {prefix} marker; GAP output tail: {stdout[-1000:]}"
        )
    return rows[0]


def parse_profile(stdout: str, identity: str, provenance: str, expression: str) -> Profile:
    fields = unique_marker(stdout, "@@PROFILE@@").split("\t")
    if len(fields) != 9 or fields[1] != identity or fields[-1] != "@@END@@":
        raise SearchError("malformed profile marker")
    order, derived, abelianization, center, classes = map(int, fields[2:7])
    if fields[7] not in {"true", "false"}:
        raise SearchError("malformed p-group Boolean")
    if abelianization != order // derived:
        raise SearchError("GAP abelianization arithmetic mismatch")
    w = residual_w(order, derived, center, classes)
    return Profile(identity, provenance, order, derived, abelianization, center,
                   classes, w, fields[7] == "true", expression, None)


def parse_database_gate_chunk(
    stdout: str, chunk: int, expected: Sequence[tuple[int, int]],
) -> list[dict[str, int]]:
    terminals = [
        line for line in stdout.splitlines() if line.startswith("@@GATE_CHUNK@@")
    ]
    if len(terminals) != 1:
        raise SearchError(
            "expected one database-gate chunk marker; GAP output tail: "
            + stdout[-1000:]
        )
    terminal = terminals[0].split("\t")
    if (len(terminal) != 4 or terminal[-1] != "@@END@@"
            or int(terminal[1]) != chunk or int(terminal[2]) != len(expected)):
        raise SearchError("malformed database-gate chunk marker")
    rows: list[dict[str, int]] = []
    for line in stdout.splitlines():
        if not line.startswith("@@GATE_ROW@@"):
            continue
        fields = line.split("\t")
        if len(fields) != 5 or fields[-1] != "@@END@@":
            raise SearchError("malformed database-gate row marker")
        order, identifier, residual = map(int, fields[1:4])
        rows.append({"order": order, "id": identifier, "residual_w": residual})
    if [(row["order"], row["id"]) for row in rows] != list(expected):
        raise SearchError("partial or reordered database-gate chunk")
    return rows


def database_gate_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    coordinates = [(int(row["order"]), int(row["id"])) for row in rows]
    if coordinates != list(database_gate_coordinates()):
        raise SearchError("partial or reordered database-gate aggregate")
    residuals = [int(row["residual_w"]) for row in rows]
    by_coordinate = {coordinate: residual for coordinate, residual in zip(coordinates, residuals)}
    summary = {
        "checked": len(rows),
        "negatives": sum(value < 0 for value in residuals),
        "equalities": sum(value == 0 for value in residuals),
        "d8_residual": by_coordinate.get((8, 3), 1),
        "q8_residual": by_coordinate.get((8, 4), 1),
    }
    if (summary["checked"] != EXPECTED_DATABASE_GATE_COUNT
            or summary["negatives"] != 0 or summary["equalities"] <= 0
            or summary["d8_residual"] != 0 or summary["q8_residual"] != 0):
        raise SearchError("source snapshot or extraspecial gate failed")
    return summary


def build_database_gate_preparation(
    rows: Sequence[Mapping[str, Any]], campaign_commit: str, manifest_path: Path,
) -> dict[str, Any]:
    normalized = [
        {"order": int(row["order"]), "id": int(row["id"]),
         "residual_w": int(row["residual_w"])}
        for row in rows
    ]
    summary = database_gate_summary(normalized)
    chunks: list[dict[str, Any]] = []
    cursor = 0
    for chunk in range(DATABASE_GATE_CHUNKS):
        expected = database_gate_chunk_coordinates(chunk)
        chunk_rows = normalized[cursor:cursor + len(expected)]
        cursor += len(expected)
        chunks.append({
            "chunk": chunk,
            "count": len(expected),
            "coordinates_sha256": records_sha256(coordinate_records(expected)),
            "rows_sha256": records_sha256(chunk_rows),
        })
    document: dict[str, Any] = {
        "schema": DATABASE_GATE_SCHEMA,
        "campaign_commit": campaign_commit,
        "source_pdf_sha256": PDF_SHA256,
        "manifest_sha256": sha256_file(manifest_path),
        "per_gap_query_seconds": int(PER_GAP_QUERY_SECONDS),
        "chunk_count": DATABASE_GATE_CHUNKS,
        "coordinate_count": EXPECTED_DATABASE_GATE_COUNT,
        "coordinate_domain_sha256": records_sha256(
            coordinate_records(database_gate_coordinates())
        ),
        "rows_sha256": records_sha256(normalized),
        "summary": summary,
        "chunks": chunks,
        "rows": normalized,
    }
    document["preparation_sha256"] = hashlib.sha256(canonical_json(document)).hexdigest()
    return document


def prepare_database_gate(
    gap: str, campaign_commit: str, manifest_path: Path, output: Path,
) -> dict[str, Any]:
    load_and_verify_manifest(manifest_path)
    rows: list[dict[str, int]] = []
    for chunk in range(DATABASE_GATE_CHUNKS):
        expected = database_gate_chunk_coordinates(chunk)
        stdout = run_gap(
            gap, gap_database_gate_chunk_source(chunk, expected),
            PER_GAP_QUERY_SECONDS,
        )
        rows.extend(parse_database_gate_chunk(stdout, chunk, expected))
    document = build_database_gate_preparation(rows, campaign_commit, manifest_path)
    write_json_fsync(output, document)
    return document


def verify_database_gate_preparation(
    path: Path, campaign_commit: str, manifest_path: Path,
) -> dict[str, Any]:
    if not path.is_file():
        raise SearchError("database-gate preparation missing")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SearchError("database-gate preparation unreadable") from exc
    if not isinstance(document, dict) or document.get("schema") != DATABASE_GATE_SCHEMA:
        raise SearchError("database-gate preparation schema mismatch")
    claimed = document.get("preparation_sha256")
    unsigned = dict(document)
    unsigned.pop("preparation_sha256", None)
    actual = hashlib.sha256(canonical_json(unsigned)).hexdigest()
    if claimed != actual:
        raise SearchError("database-gate preparation content hash mismatch")
    if (document.get("campaign_commit") != campaign_commit
            or document.get("source_pdf_sha256") != PDF_SHA256
            or document.get("manifest_sha256") != sha256_file(manifest_path)
            or document.get("per_gap_query_seconds") != int(PER_GAP_QUERY_SECONDS)
            or document.get("chunk_count") != DATABASE_GATE_CHUNKS
            or document.get("coordinate_count") != EXPECTED_DATABASE_GATE_COUNT):
        raise SearchError("database-gate preparation binding mismatch")
    rows = document.get("rows")
    chunks = document.get("chunks")
    if not isinstance(rows, list) or not isinstance(chunks, list):
        raise SearchError("database-gate preparation payload missing")
    rebuilt = build_database_gate_preparation(rows, campaign_commit, manifest_path)
    if document != rebuilt:
        raise SearchError("database-gate preparation aggregate mismatch")
    return {
        **rebuilt["summary"],
        "preparation_sha256": rebuilt["preparation_sha256"],
        "coordinate_domain_sha256": rebuilt["coordinate_domain_sha256"],
        "rows_sha256": rebuilt["rows_sha256"],
        "chunk_count": rebuilt["chunk_count"],
    }


def partition_interval(total: int, shards: int, shard: int) -> range:
    quotient, remainder = divmod(total, shards)
    start0 = shard * quotient + min(shard, remainder)
    size = quotient + (1 if shard < remainder else 0)
    return range(start0 + 1, start0 + size + 1)


def deterministic_generic_id(shard: int, cursor: int) -> int:
    digest = hashlib.sha256(f"{GENERIC_SEED}:{shard}:{cursor}".encode("ascii")).digest()
    return 1 + int.from_bytes(digest, "big") % GENERIC_COUNT


def binary_rank(vectors: Iterable[int], width: int) -> int:
    basis = [0] * width
    rank = 0
    for raw in vectors:
        value = int(raw)
        while value:
            pivot = value.bit_length() - 1
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def wall_assignments() -> tuple[tuple[int, tuple[int, ...]], ...]:
    rows: list[tuple[int, tuple[int, ...]]] = []
    for dimension in (6, 8):
        for outputs in itertools.product((1, 2, 3), repeat=dimension // 2):
            if binary_rank(outputs, 2) == 2:
                rows.append((dimension, outputs))
    return tuple(rows)


def wall_identity(dimension: int, outputs: Sequence[int]) -> str:
    return f"class2-f2-d{dimension}-w2-" + "".join(str(value) for value in outputs)


def wall_shard_rows(shard: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    return tuple(
        row for row in wall_assignments()
        if int.from_bytes(hashlib.sha256(wall_identity(*row).encode("ascii")).digest(), "big") % SHARDS == shard
    )


def beta_image_rank(dimension: int, outputs: Sequence[int], vector: int) -> int:
    images: list[int] = []
    for pair, mask in enumerate(outputs):
        a, b = 2 * pair, 2 * pair + 1
        if (vector >> a) & 1:
            images.append(mask)  # beta(v,e_b)
        if (vector >> b) & 1:
            images.append(mask)  # beta(v,e_a), sign is identical over F2
    return binary_rank(images, 2)


def wall_profile(dimension: int, outputs: Sequence[int]) -> Profile:
    if dimension not in {6, 8} or len(outputs) != dimension // 2:
        raise SearchError("wall descriptor outside frozen domain")
    if any(value not in {1, 2, 3} for value in outputs) or binary_rank(outputs, 2) != 2:
        raise SearchError("wall commutator image is not the frozen surjective lift")
    order = 1 << (dimension + 2)
    derived = 1 << binary_rank(outputs, 2)
    # Every basis coordinate is paired with a nonzero output mask. Testing
    # beta(v,e_j)=0 for all j therefore forces every coordinate of v to zero.
    radical_dimension = 0
    center = 1 << (2 + radical_dimension)
    classes = sum(1 << (2 - beta_image_rank(dimension, outputs, vector)) for vector in range(1 << dimension))
    identity = wall_identity(dimension, outputs)
    descriptor = {"dimension": dimension, "central_dimension": 2, "pair_outputs": list(outputs)}
    return Profile(identity, "extraspecial commutator-image lift", order, derived,
                   order // derived, center, classes,
                   residual_w(order, derived, center, classes), True, None, descriptor)


def cocycle_value(dimension: int, outputs: Sequence[int], left_v: int, right_v: int) -> int:
    value = 0
    for pair, mask in enumerate(outputs):
        if ((left_v >> (2 * pair)) & 1) and ((right_v >> (2 * pair + 1)) & 1):
            value ^= mask
    return value


def wall_table(dimension: int, outputs: Sequence[int]) -> list[list[int]]:
    size_v = 1 << dimension
    order = size_v << 2
    table: list[list[int]] = []
    for left in range(order):
        lv, lz = left >> 2, left & 3
        row: list[int] = []
        for right in range(order):
            rv, rz = right >> 2, right & 3
            row.append(((lv ^ rv) << 2) | (lz ^ rz ^ cocycle_value(dimension, outputs, lv, rv)))
        table.append(row)
    return table


def gap_table_source(expression: str, identity: str) -> str:
    return f'''SetPrintFormattingStatus("*stdout*",false);;
C5K4Table:=function()
  local G,els,n,i,j;
  G:={expression};; els:=AsSSortedList(G);; n:=Length(els);;
  Print("@@TABLE_BEGIN@@\\t{identity}\\t",n,"\\n");
  for i in [1..n] do
    for j in [1..n] do
      if j>1 then Print(","); fi; Print(PositionSorted(els,els[i]*els[j])-1);
    od; Print("\\n");
  od;
  Print("@@TABLE_END@@\\n");
end;;
C5K4Table();;
QUIT_GAP(0);
'''


def parse_gap_table(stdout: str, identity: str, order: int) -> list[list[int]]:
    lines = stdout.splitlines()
    begin = f"@@TABLE_BEGIN@@\t{identity}\t{order}"
    try:
        start = lines.index(begin)
        finish = lines.index("@@TABLE_END@@", start + 1)
    except ValueError as exc:
        raise SearchError(
            "malformed GAP table marker; GAP output tail: " + stdout[-1000:]
        ) from exc
    rows = [[int(value) for value in line.split(",")] for line in lines[start + 1:finish]]
    if len(rows) != order or any(len(row) != order for row in rows):
        raise SearchError("incomplete GAP multiplication table")
    return rows


def certificate_document(profile: Profile, table: Sequence[Sequence[int]]) -> dict[str, Any]:
    return {
        "schema": CERTIFICATE_SCHEMA,
        "profile": asdict(profile),
        "multiplication_table": [list(row) for row in table],
        "indexing": "zero-based; identity discovered independently",
    }


def deadline_remaining(deadline: float) -> float:
    return deadline - time.monotonic()


def run_assignment(args: argparse.Namespace) -> int:
    load_and_verify_manifest(args.manifest)
    if not (len(args.campaign_commit) == 40 and all(c in "0123456789abcdef" for c in args.campaign_commit)):
        raise SearchError("campaign commit must be exact lowercase 40-hex")
    ledger = DurableLedger(args.ledger, args.arm, args.shard, args.campaign_commit)
    deadline = ledger.started + INTERNAL_STOP_SECONDS
    try:
        gate = verify_database_gate_preparation(
            args.database_gate_preparation, args.campaign_commit, args.manifest,
        )
        ledger.emit("database_sanity_pass", gate)
    except Exception as exc:
        ledger.emit("database_sanity_failure", {"error": type(exc).__name__, "message": str(exc)[:1000]})
        write_terminal(args.terminal, ledger, "SANITY_GATE_FAILED")
        return 3

    seen: set[str] = set()
    exhausted = True
    if args.arm == "CATALOGUE":
        proposals: Iterable[tuple[str, Any]] = (
            ("gap", (f"SmallGroup(256,{identifier})", f"SmallGroup(256,{identifier})", "complete order-256 catalogue"))
            for identifier in partition_interval(CATALOGUE_COUNT, SHARDS, args.shard)
        )
    elif args.arm == "GENERIC":
        def generic_rows() -> Iterable[tuple[str, Any]]:
            cursor = 0
            while cursor < GENERIC_LIMIT:
                identifier = deterministic_generic_id(args.shard, cursor)
                cursor += 1
                key = f"SmallGroup(512,{identifier})"
                if key in seen:
                    continue
                seen.add(key)
                yield "gap", (key, key, f"hash sample shard={args.shard} cursor={cursor-1}")
        proposals = generic_rows()
    else:
        proposals = (("wall", row) for row in wall_shard_rows(args.shard))

    for kind, payload in proposals:
        if deadline_remaining(deadline) <= 0.05:
            exhausted = False
            break
        ledger.counters.proposed += 1
        try:
            if kind == "gap":
                identity, expression, provenance = payload
                stdout = run_gap(args.gap, gap_profile_source(expression, identity), deadline_remaining(deadline))
                profile = parse_profile(stdout, identity, provenance, expression)
            else:
                dimension, outputs = payload
                profile = wall_profile(dimension, outputs)
            if not profile.is_p_group:
                raise SearchError("development proposal is not a p-group")
            ledger.counters.exact_evaluated += 1
            ledger.emit("exact_profile", asdict(profile))
        except QueryTimeout as exc:
            ledger.counters.query_timeouts += 1
            ledger.emit("query_timeout", {"kind": kind, "payload": payload, "message": str(exc)})
            if deadline_remaining(deadline) <= 0.05:
                exhausted = False
                break
            continue
        except Exception as exc:
            ledger.counters.malformed += 1
            ledger.emit("proposal_error", {"kind": kind, "payload": payload, "error": type(exc).__name__, "message": str(exc)[:1000], "mathematical_inference": "NONE"})
            continue

        if profile.residual_w < 0:
            ledger.counters.crossings += 1
            try:
                if profile.gap_expression is not None:
                    table_stdout = run_gap(args.gap, gap_table_source(profile.gap_expression, profile.identity), deadline_remaining(deadline))
                    table = parse_gap_table(table_stdout, profile.identity, profile.order)
                else:
                    assert profile.wall_descriptor is not None
                    table = wall_table(int(profile.wall_descriptor["dimension"]), tuple(profile.wall_descriptor["pair_outputs"]))
                certificate = certificate_document(profile, table)
                write_json_fsync(args.certificate, certificate)
                ledger.counters.certificates += 1
                ledger.emit("candidate_certificate", {"certificate_sha256": sha256_file(args.certificate), "identity": profile.identity, "residual_w": profile.residual_w})
                write_terminal(args.terminal, ledger, "CERTIFICATE_FOUND")
                return 0
            except Exception as exc:
                ledger.emit("candidate_certificate_failure", {"identity": profile.identity, "error": type(exc).__name__, "message": str(exc)[:1000], "mathematical_inference": "CANDIDATE_NOT_ADMITTED"})
                write_terminal(args.terminal, ledger, "WORKER_ERROR")
                return 4

    if not exhausted:
        reason = "DEADLINE_PREFIX"
    elif args.arm == "GENERIC":
        reason = "PROPOSAL_LIMIT"
    else:
        reason = "DOMAIN_EXHAUSTED"
    write_terminal(args.terminal, ledger, reason)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True, choices=ARMS)
    parser.add_argument("--shard", required=True, type=int, choices=range(SHARDS))
    parser.add_argument("--campaign-commit", required=True)
    parser.add_argument("--gap", default="gap")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--database-gate-preparation", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run_assignment(parse_args()))
