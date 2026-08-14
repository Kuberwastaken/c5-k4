#!/usr/bin/env python3
"""Frozen GAP-backed DEVELOPMENT search for solvable_of_cyc_lt.

Importing this module constructs no group and evaluates no target.  Actual
execution requires the digest-locked manifest and a pinned GAP installation.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Mapping, Sequence


ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
INTERNAL_STOP_SECONDS = 54.0
EXTERNAL_STOP_SECONDS = 60
PER_QUERY_MAX_SECONDS = 8.0
DIAGNOSTIC_MAX_BYTES = 4096
UPSTREAM_COMMIT = "942fb149e782a56c2719c543ab58e093f733acb4"
UPSTREAM_BLOB = "cb099f09a40eab0149b3332979d92e190ef44def"
UPSTREAM_DECLARATION = "Arxiv.«2604.08040».solvable_of_cyc_lt"
FREEZE_BASE_COMMIT = "b9bb628abc8458188f9995c2613d27465e53639c"
GAP_VERSION = "4.12.1"
SMALLGRP_VERSION = "1.5.3"
PRIMGRP_VERSION = "3.4.4"
LEDGER_SCHEMA = "c5k4-solvable-cyclic-subgroups-jsonl-1.0"
TERMINAL_SCHEMA = "c5k4-solvable-cyclic-subgroups-terminal-1.0"
CERTIFICATE_SCHEMA = "c5k4-solvable-cyclic-subgroups-certificate-1.0"
MANIFEST_SCHEMA = "c5k4-solvable-cyclic-subgroups-manifest-1.0"
ZERO_SHA256 = "0" * 64
GENERIC_SEED = "cb099f09a40eab0149b3332979d92e190ef44def"
GENERIC_PER_ORDER = 4
GENERIC_GLOBAL_LIMIT = 1024
TERMINAL_REASONS = {
    "DOMAIN_EXHAUSTED",
    "PROPOSAL_LIMIT",
    "SEARCH_EXHAUSTED",
    "DEADLINE_PREFIX",
    "CERTIFICATE_FOUND",
    "SANITY_GATE_FAILED",
    "WORKER_ERROR",
}

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT / "results" / "expansion" / "live-search-2026-08-14"
    / "solvable-cyclic-subgroups-manifest.json"
)


class SearchError(ValueError):
    """Raised when frozen inputs or exact GAP output fail closed."""


class GapQueryTimeout(TimeoutError):
    """Raised when one separately capped GAP query exceeds its allowance."""


class GapDescriptorError(SearchError):
    """A single frozen descriptor produced no admissible exact profile."""

    def __init__(self, reason: str, diagnostic: Mapping[str, Any]):
        super().__init__(reason)
        self.reason = reason
        self.diagnostic = dict(diagnostic)


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_and_verify_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != MANIFEST_SCHEMA:
        raise SearchError("wrong solvable-cyclic-subgroups manifest schema")
    upstream = value.get("upstream", {})
    if upstream.get("commit") != UPSTREAM_COMMIT or upstream.get("blob") != UPSTREAM_BLOB:
        raise SearchError("upstream source pin drift")
    if upstream.get("declaration") != UPSTREAM_DECLARATION:
        raise SearchError("upstream declaration drift")
    if value.get("freeze_base_commit") != FREEZE_BASE_COMMIT:
        raise SearchError("freeze-base commit drift")
    if value.get("arms") != list(ARMS):
        raise SearchError("frozen arm list drift")
    if value.get("internal_stop_seconds") != int(INTERNAL_STOP_SECONDS):
        raise SearchError("internal deadline drift")
    if value.get("external_stop_seconds") != EXTERNAL_STOP_SECONDS:
        raise SearchError("external deadline drift")
    if value.get("descriptor_error_policy") != {
        "action": "DURABLE_SKIP",
        "mathematical_inference": "NONE",
        "stdout_max_bytes": DIAGNOSTIC_MAX_BYTES,
        "stderr_max_bytes": DIAGNOSTIC_MAX_BYTES,
    }:
        raise SearchError("descriptor-error policy drift")
    dependencies = value.get("gap_dependencies", {})
    if dependencies != {
        "gap": GAP_VERSION,
        "smallgrp": SMALLGRP_VERSION,
        "primgrp": PRIMGRP_VERSION,
    }:
        raise SearchError("GAP dependency lock drift")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise SearchError("artifact lock is absent")
    for artifact in artifacts:
        artifact_path = REPO_ROOT / str(artifact.get("path", ""))
        if not artifact_path.is_file() or sha256_file(artifact_path) != artifact.get("sha256"):
            raise SearchError(f"frozen artifact digest mismatch: {artifact_path}")
    return value


@dataclass(frozen=True)
class GroupDescriptor:
    identifier: str
    expression: str
    provenance: str


@dataclass(frozen=True)
class GapProcessResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass
class Counters:
    proposed: int = 0
    exact_evaluated: int = 0
    query_timeouts: int = 0
    descriptor_errors: int = 0
    nonsolvable: int = 0
    objective_scored: int = 0
    primary_candidates: int = 0
    certificates: int = 0


def catalogue_orders() -> range:
    return range(60, 256)


def generic_orders() -> range:
    return range(256, 2001)


def prime_powers_through_64() -> tuple[int, ...]:
    # 4, 5 and 9 duplicate the separately named A5/A6 controls.
    return (7, 8, 11, 13, 16, 17, 19, 23, 25, 27, 29, 31, 32, 37, 41, 43, 47, 49, 53, 59, 61, 64)


def wall_descriptors() -> tuple[GroupDescriptor, ...]:
    bases = [
        GroupDescriptor("A5", 'SimpleGroup("A5")', "source equality control"),
        GroupDescriptor("A6", 'SimpleGroup("A6")', "source simple-socle shortlist"),
        GroupDescriptor("A7", 'SimpleGroup("A7")', "source simple-socle shortlist"),
        GroupDescriptor("A8", 'SimpleGroup("A8")', "source simple-socle shortlist"),
        GroupDescriptor("M11", 'SimpleGroup("M11")', "source simple-socle shortlist"),
        GroupDescriptor("J1", 'SimpleGroup("J1")', "source simple-socle shortlist"),
        GroupDescriptor("PSU3_4", 'SimpleGroup("U(3,4)")', "source simple-socle shortlist"),
        GroupDescriptor("Sz8", 'SimpleGroup("Sz(8)")', "source simple-socle shortlist"),
    ]
    for q in prime_powers_through_64():
        bases.append(GroupDescriptor(f"PSL2_{q}", f'SimpleGroup("L(2,{q})")', "PSL2 socle replacement"))
    rows: list[GroupDescriptor] = []
    for base in bases:
        rows.append(base)
        rows.append(GroupDescriptor(f"Aut_{base.identifier}", f"AutomorphismGroup({base.expression})", "almost-simple endpoint"))
    # These are calibration-only pinned directions, never candidate-family retuning.
    for prime in (7, 11, 13):
        rows.append(
            GroupDescriptor(
                f"A5_x_C{prime}",
                f'DirectProduct(SimpleGroup("A5"),CyclicGroup({prime}))',
                "coprime direct-product equality control",
            )
        )
    return tuple(rows)


def smallgroup_descriptor(order: int, identifier: int, provenance: str) -> GroupDescriptor:
    if order < 1 or identifier < 1:
        raise SearchError("SmallGroup coordinates must be positive")
    return GroupDescriptor(f"SmallGroup({order},{identifier})", f"SmallGroup({order},{identifier})", provenance)


def deterministic_generic_ids(order: int, identifiers: Sequence[int]) -> tuple[int, ...]:
    unique = sorted(set(int(value) for value in identifiers))
    ranked = sorted(
        unique,
        key=lambda identifier: hashlib.sha256(
            f"{GENERIC_SEED}:{order}:{identifier}".encode("ascii")
        ).digest(),
    )
    return tuple(sorted(ranked[:GENERIC_PER_ORDER]))


def _gap_string_list(values: str) -> list[str]:
    if values == "":
        return []
    return values.split(",")


def parse_profile_line(line: str, descriptor: GroupDescriptor) -> dict[str, Any]:
    fields = line.rstrip("\n").split("\t")
    if len(fields) != 9 or fields[0] != "@@PROFILE@@" or fields[8] != "@@END@@":
        raise SearchError("malformed GAP profile marker")
    order = int(fields[1])
    prime_factors = tuple(int(value) for value in _gap_string_list(fields[2]))
    t = int(fields[3])
    cyclic_subgroups = int(fields[4])
    if fields[5] not in {"true", "false"}:
        raise SearchError("malformed GAP solvability Boolean")
    histogram: list[dict[str, int]] = []
    total_elements = 0
    recomputed_cyclic = 0
    for pair in _gap_string_list(fields[6]):
        element_order_raw, count_raw = pair.split(":", 1)
        element_order, count = int(element_order_raw), int(count_raw)
        if element_order < 1 or count < 1:
            raise SearchError("invalid element-order histogram entry")
        phi = euler_phi(element_order)
        if count % phi:
            raise SearchError("element-order population is not divisible by Euler phi")
        histogram.append({"element_order": element_order, "count": count})
        total_elements += count
        recomputed_cyclic += count // phi
    if total_elements != order or recomputed_cyclic != cyclic_subgroups:
        raise SearchError("GAP profile failed independent integer histogram arithmetic")
    if t != len(prime_factors) or tuple(sorted(set(prime_factors))) != prime_factors:
        raise SearchError("prime-factor profile is inconsistent")
    threshold = 1 << (t + 2)
    return {
        "identifier": descriptor.identifier,
        "gap_expression": descriptor.expression,
        "provenance": descriptor.provenance,
        "order": order,
        "prime_factors": list(prime_factors),
        "num_prime_factors": t,
        "cyclic_subgroups": cyclic_subgroups,
        "solvable": fields[5] == "true",
        "element_order_histogram": histogram,
        "permutation_generators": fields[7].split("|") if fields[7] else [],
        "threshold": threshold,
        "residual": cyclic_subgroups - threshold,
    }


def euler_phi(n: int) -> int:
    if n < 1:
        raise SearchError("Euler phi requires a positive integer")
    result = n
    divisor = 2
    remaining = n
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            while remaining % divisor == 0:
                remaining //= divisor
            result -= result // divisor
        divisor += 1
    if remaining > 1:
        result -= result // remaining
    return result


def profile_gap_source(descriptor: GroupDescriptor) -> str:
    return f'''SetInfoLevel(InfoWarning,0);;
SetPrintFormattingStatus("*stdout*",false);;
Print("@@QUERY_BEGIN@@\\n");;
G0 := {descriptor.expression};;
G := Image(IsomorphismPermGroup(G0));;
cc := ConjugacyClasses(G);;
ords := Set(List(cc, c -> Order(Representative(c))));;
hist := List(ords, d -> [d, Sum(Filtered(cc, c -> Order(Representative(c)) = d), Size)]);;
cyc := Sum(hist, x -> x[2] / Phi(x[1]));;
pf := Set(FactorsInt(Size(G)));;
gens := List(GeneratorsOfGroup(G), String);;
Print("@@PROFILE@@\\t", Size(G), "\\t",
  JoinStringsWithSeparator(List(pf,String),","), "\\t", Length(pf), "\\t", cyc, "\\t",
  IsSolvableGroup(G), "\\t",
  JoinStringsWithSeparator(List(hist,x -> Concatenation(String(x[1]),":",String(x[2]))),","), "\\t",
  JoinStringsWithSeparator(gens,"|"), "\\t@@END@@\\n");;
QUIT_GAP(0);;
'''


def environment_gap_source() -> str:
    return '''SetInfoLevel(InfoWarning,0);;
sg := PackageInfo("smallgrp");;
pg := PackageInfo("primgrp");;
Print("@@ENV@@\\t", GAPInfo.Version, "\\t", sg[1].Version, "\\t", pg[1].Version, "\\n");;
QUIT_GAP(0);;
'''


def ids_gap_source(order: int) -> str:
    if order < 1:
        raise SearchError("group order must be positive")
    return f'''SetInfoLevel(InfoWarning,0);;
if SmallGroupsAvailable({order}) then
  ids := IdsOfAllSmallGroups(Size,{order},IsSolvableGroup,false);;
  Print("@@IDS@@\\tAVAILABLE\\t", JoinStringsWithSeparator(List(ids,x -> String(x[2])),","), "\\n");
else
  Print("@@IDS@@\\tUNAVAILABLE\\t\\n");
fi;;
QUIT_GAP(0);;
'''


def run_gap_capture(gap: str, source: str, timeout_seconds: float) -> GapProcessResult:
    if timeout_seconds <= 0:
        raise GapQueryTimeout("no time remains for GAP query")
    try:
        completed = subprocess.run(
            [gap, "-q", "-b"],
            input=source,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
            env={**os.environ, "LC_ALL": "C.UTF-8", "TZ": "UTC"},
        )
    except subprocess.TimeoutExpired as exc:
        raise GapQueryTimeout("separately capped GAP query timed out") from exc
    return GapProcessResult(completed.returncode, completed.stdout, completed.stderr)


def bounded_diagnostic(text: str, limit: int = DIAGNOSTIC_MAX_BYTES) -> dict[str, Any]:
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        rendered = encoded.decode("utf-8", errors="replace")
        truncated = False
    else:
        half = limit // 2
        rendered = (
            encoded[:half].decode("utf-8", errors="replace")
            + "\n@@DIAGNOSTIC_TRUNCATED@@\n"
            + encoded[-half:].decode("utf-8", errors="replace")
        )
        truncated = True
    return {"bytes": len(encoded), "truncated": truncated, "text": rendered}


def process_diagnostic(result: GapProcessResult) -> dict[str, Any]:
    return {
        "returncode": result.returncode,
        "stdout": bounded_diagnostic(result.stdout),
        "stderr": bounded_diagnostic(result.stderr),
    }


def run_gap_script(gap: str, source: str, timeout_seconds: float) -> str:
    result = run_gap_capture(gap, source, timeout_seconds)
    if result.returncode != 0:
        raise SearchError(f"GAP exited {result.returncode}: {result.stderr[-1000:]}")
    return result.stdout


def marker_line(output: str, prefix: str) -> str:
    rows = [line for line in output.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise SearchError(f"expected exactly one {prefix} marker")
    return rows[0]


def query_profile(gap: str, descriptor: GroupDescriptor, timeout_seconds: float) -> dict[str, Any]:
    result = run_gap_capture(gap, profile_gap_source(descriptor), timeout_seconds)
    diagnostic = process_diagnostic(result)
    if result.returncode != 0:
        raise GapDescriptorError("GAP_NONZERO_EXIT", diagnostic)
    try:
        line = marker_line(result.stdout, "@@PROFILE@@")
    except SearchError as exc:
        raise GapDescriptorError("PROFILE_MARKER_MISSING_OR_DUPLICATE", diagnostic) from exc
    try:
        return parse_profile_line(line, descriptor)
    except (SearchError, ValueError) as exc:
        raise GapDescriptorError("PROFILE_MARKER_MALFORMED", diagnostic) from exc


def query_nonsolvable_ids(gap: str, order: int, timeout_seconds: float) -> tuple[bool, tuple[int, ...]]:
    output = run_gap_script(gap, ids_gap_source(order), timeout_seconds)
    fields = marker_line(output, "@@IDS@@").split("\t")
    if len(fields) != 3 or fields[1] not in {"AVAILABLE", "UNAVAILABLE"}:
        raise SearchError("malformed GAP SmallGroups marker")
    identifiers = tuple(int(value) for value in _gap_string_list(fields[2]))
    if any(value < 1 for value in identifiers) or len(set(identifiers)) != len(identifiers):
        raise SearchError("invalid SmallGroups identifier list")
    return fields[1] == "AVAILABLE", identifiers


def database_sanity_gate(evaluate: Callable[[GroupDescriptor], dict[str, Any]]) -> dict[str, Any]:
    controls = (
        (GroupDescriptor("S3", "SymmetricGroup(3)", "solvable control"), 6, 5, True, -11),
        (GroupDescriptor("A4", "AlternatingGroup(4)", "solvable control"), 12, 8, True, -8),
        (GroupDescriptor("A5", 'SimpleGroup("A5")', "source equality control"), 60, 32, False, 0),
    )
    rows: list[dict[str, Any]] = []
    for descriptor, order, cyclic_subgroups, solvable, residual in controls:
        profile = evaluate(descriptor)
        observed = (profile["order"], profile["cyclic_subgroups"], profile["solvable"], profile["residual"])
        expected = (order, cyclic_subgroups, solvable, residual)
        if observed != expected:
            raise SearchError(f"database-sanity control failed: {descriptor.identifier}")
        rows.append(profile)
    return {
        "controls": rows,
        "source_documented_nonsolvable_controls": ["A5"],
        "target_domain_nonsolvable_groups_evaluated": 0,
    }


class DurableLedger:
    def __init__(self, path: Path, arm: str):
        if arm not in ARMS:
            raise SearchError("arm is outside the frozen manifest")
        if path.exists() and path.stat().st_size:
            raise SearchError("ledger must be a fresh file")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.arm = arm
        self.started = time.monotonic()
        self.sequence = 0
        self.previous = ZERO_SHA256
        self.counters = Counters()
        self.emit("checkpoint", {"label": "started"})

    def emit(self, kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA,
            "kind": kind,
            "arm": self.arm,
            "sequence": self.sequence,
            "elapsed_milliseconds": int((time.monotonic() - self.started) * 1000),
            "counters": asdict(self.counters),
            "previous_row_sha256": self.previous,
            **dict(payload),
        }
        row["row_sha256"] = hashlib.sha256(canonical_json(row)).hexdigest()
        raw = canonical_json(row)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            view = memoryview(raw)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:  # pragma: no cover
                    raise OSError("short durable ledger write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.previous = row["row_sha256"]
        self.sequence += 1
        return row


def durable_write_new(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(canonical_json(value))
        while view:
            written = os.write(descriptor, view)
            if written <= 0:  # pragma: no cover
                raise OSError("short durable certificate write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_terminal(path: Path, ledger: DurableLedger, reason: str, cursor: Mapping[str, Any]) -> dict[str, Any]:
    if reason not in TERMINAL_REASONS:
        raise SearchError("unknown terminal reason")
    terminal = ledger.emit("terminal", {"terminal_reason": reason, "cursor": dict(cursor)})
    receipt = {
        "schema": TERMINAL_SCHEMA,
        "arm": ledger.arm,
        "terminal_reason": reason,
        "cursor": dict(cursor),
        "counters": asdict(ledger.counters),
        "final_row_sha256": terminal["row_sha256"],
    }
    durable_write_new(path, receipt)
    return receipt


class SearchRecorder:
    def __init__(self, gap: str, ledger: DurableLedger, deadline: float, certificate_path: Path):
        self.gap = gap
        self.ledger = ledger
        self.deadline = deadline
        self.certificate_path = certificate_path

    def remaining(self) -> float:
        return self.deadline - time.monotonic()

    def evaluate(self, descriptor: GroupDescriptor, cursor: Mapping[str, Any]) -> bool:
        self.ledger.counters.proposed += 1
        allowance = min(PER_QUERY_MAX_SECONDS, max(0.0, self.remaining() - 1.0))
        try:
            profile = query_profile(self.gap, descriptor, allowance)
        except GapQueryTimeout:
            self.ledger.counters.query_timeouts += 1
            self.ledger.emit("evaluation_timeout", {"descriptor": asdict(descriptor), "cursor": dict(cursor)})
            return False
        except GapDescriptorError as exc:
            self.ledger.counters.descriptor_errors += 1
            self.ledger.emit(
                "descriptor_error",
                {
                    "descriptor": asdict(descriptor),
                    "cursor": dict(cursor),
                    "descriptor_status": exc.reason,
                    "diagnostic": exc.diagnostic,
                    "mathematical_inference": "NONE",
                },
            )
            return False
        self.ledger.counters.exact_evaluated += 1
        self.ledger.counters.objective_scored += 1
        if not profile["solvable"]:
            self.ledger.counters.nonsolvable += 1
        crossing = (not profile["solvable"]) and profile["residual"] < 0
        profile["crossing"] = crossing
        profile["cursor"] = dict(cursor)
        self.ledger.emit("evaluated_group", profile)
        if not crossing:
            return False
        self.ledger.counters.primary_candidates += 1
        certificate = {
            "schema": CERTIFICATE_SCHEMA,
            "upstream_commit": UPSTREAM_COMMIT,
            "upstream_blob": UPSTREAM_BLOB,
            "declaration": UPSTREAM_DECLARATION,
            "logical_scope": "intended finite-universal RHS of answer-wrapped declaration",
            "primary": profile,
            "independent_verification": None,
            "status": "PRIMARY_CANDIDATE",
        }
        from verify_solvable_cyclic_subgroups_certificate import verify_candidate_document

        allowance = min(PER_QUERY_MAX_SECONDS, max(0.0, self.remaining() - 1.0))
        try:
            replay = verify_candidate_document(certificate, self.gap, allowance)
        # The independent verifier is deliberately self-contained and owns its
        # own TimeoutError/ValueError subclasses.  Catch by standard base class
        # so an unverified primary row is preserved rather than promoted or
        # converted into a whole-worker failure.
        except (TimeoutError, ValueError) as exc:
            self.ledger.emit(
                "primary_candidate_unverified",
                {"candidate": certificate, "verification_error": type(exc).__name__ + ": " + str(exc)},
            )
            return False
        certificate["independent_verification"] = replay
        certificate["status"] = "INDEPENDENTLY_VERIFIED"
        durable_write_new(self.certificate_path, certificate)
        self.ledger.counters.certificates += 1
        self.ledger.emit("certificate_found", {"certificate": certificate})
        return True


def validate_gap_environment(gap: str, timeout_seconds: float) -> dict[str, str]:
    output = run_gap_script(gap, environment_gap_source(), timeout_seconds)
    fields = marker_line(output, "@@ENV@@").split("\t")
    if len(fields) != 4:
        raise SearchError("malformed GAP environment marker")
    observed = {"gap": fields[1], "smallgrp": fields[2], "primgrp": fields[3]}
    expected = {"gap": GAP_VERSION, "smallgrp": SMALLGRP_VERSION, "primgrp": PRIMGRP_VERSION}
    if observed != expected:
        raise SearchError(f"GAP environment drift: {observed}")
    return observed


def run_catalogue(recorder: SearchRecorder) -> tuple[str, dict[str, Any]]:
    for order in catalogue_orders():
        if recorder.remaining() <= 1.0:
            return "DEADLINE_PREFIX", {"next_order": order}
        try:
            available, identifiers = query_nonsolvable_ids(
                recorder.gap, order, min(PER_QUERY_MAX_SECONDS, recorder.remaining() - 1.0)
            )
        except GapQueryTimeout:
            recorder.ledger.counters.query_timeouts += 1
            recorder.ledger.emit("order_index_timeout", {"order": order})
            continue
        if not available:
            recorder.ledger.emit("order_unavailable", {"order": order})
            continue
        for identifier in identifiers:
            if recorder.remaining() <= 1.0:
                return "DEADLINE_PREFIX", {"next_order": order, "next_identifier": identifier}
            descriptor = smallgroup_descriptor(order, identifier, "complete SmallGroups catalogue 60..255")
            if recorder.evaluate(descriptor, {"order": order, "identifier": identifier}):
                return "CERTIFICATE_FOUND", {"order": order, "identifier": identifier}
    return "DOMAIN_EXHAUSTED", {"next_order": 256}


def run_generic(recorder: SearchRecorder) -> tuple[str, dict[str, Any]]:
    selected = 0
    for order in generic_orders():
        if selected >= GENERIC_GLOBAL_LIMIT:
            return "PROPOSAL_LIMIT", {"selected": selected, "next_order": order}
        if recorder.remaining() <= 1.0:
            return "DEADLINE_PREFIX", {"selected": selected, "next_order": order}
        try:
            available, identifiers = query_nonsolvable_ids(
                recorder.gap, order, min(PER_QUERY_MAX_SECONDS, recorder.remaining() - 1.0)
            )
        except GapQueryTimeout:
            recorder.ledger.counters.query_timeouts += 1
            recorder.ledger.emit("order_index_timeout", {"order": order})
            continue
        if not available:
            continue
        for identifier in deterministic_generic_ids(order, identifiers):
            if selected >= GENERIC_GLOBAL_LIMIT:
                return "PROPOSAL_LIMIT", {"selected": selected, "next_order": order}
            if recorder.remaining() <= 1.0:
                return "DEADLINE_PREFIX", {"selected": selected, "next_order": order, "next_identifier": identifier}
            selected += 1
            descriptor = smallgroup_descriptor(order, identifier, "deterministic stratified SmallGroups sample 256..2000")
            if recorder.evaluate(descriptor, {"order": order, "identifier": identifier, "selected": selected}):
                return "CERTIFICATE_FOUND", {"order": order, "identifier": identifier, "selected": selected}
    return "SEARCH_EXHAUSTED", {"selected": selected, "next_order": 2001}


def run_wall_navigation(recorder: SearchRecorder) -> tuple[str, dict[str, Any]]:
    rows = wall_descriptors()
    for index, descriptor in enumerate(rows):
        if recorder.remaining() <= 1.0:
            return "DEADLINE_PREFIX", {"next_index": index, "next_identifier": descriptor.identifier}
        if recorder.evaluate(descriptor, {"wall_index": index}):
            return "CERTIFICATE_FOUND", {"wall_index": index, "identifier": descriptor.identifier}
    return "SEARCH_EXHAUSTED", {"next_index": len(rows)}


def run_worker(
    arm: str,
    gap: str,
    ledger_path: Path,
    terminal_path: Path,
    certificate_path: Path,
    manifest_path: Path,
) -> None:
    load_and_verify_manifest(manifest_path)
    ledger = DurableLedger(ledger_path, arm)
    deadline = ledger.started + INTERNAL_STOP_SECONDS
    try:
        environment = validate_gap_environment(gap, min(PER_QUERY_MAX_SECONDS, deadline - time.monotonic() - 1.0))
        ledger.emit("gap_environment", environment)
        gate = database_sanity_gate(
            lambda descriptor: query_profile(
                gap, descriptor, min(PER_QUERY_MAX_SECONDS, deadline - time.monotonic() - 1.0)
            )
        )
        ledger.emit("database_sanity_gate", gate)
    except Exception as exc:
        write_terminal(
            terminal_path,
            ledger,
            "SANITY_GATE_FAILED",
            {"exception_type": type(exc).__name__, "message": str(exc)},
        )
        raise
    recorder = SearchRecorder(gap, ledger, deadline, certificate_path)
    try:
        if arm == "CATALOGUE":
            reason, cursor = run_catalogue(recorder)
        elif arm == "GENERIC":
            reason, cursor = run_generic(recorder)
        else:
            reason, cursor = run_wall_navigation(recorder)
    except Exception as exc:
        write_terminal(
            terminal_path,
            ledger,
            "WORKER_ERROR",
            {"exception_type": type(exc).__name__, "message": str(exc)},
        )
        raise
    write_terminal(terminal_path, ledger, reason, cursor)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--gap", default="gap")
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        run_worker(args.arm, args.gap, args.ledger, args.terminal, args.certificate, args.manifest)
    except (OSError, SearchError, GapQueryTimeout, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
