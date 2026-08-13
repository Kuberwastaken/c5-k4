#!/usr/bin/env python3
"""Validate a frozen Method v1.1 prospective-benchmark manifest.

The JSON schema fixes the shape.  This linter supplies the cross-field checks
that JSON Schema cannot express: exact probability arithmetic, the twelve-unit
quota, contamination disjointness, equal budgets, chronology, pinned upstream
paths, and append-only ledger hash chains.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

try:
    from select_benchmark_v11 import select as replay_selection
except ModuleNotFoundError:  # imported as ``scripts.lint_benchmark_v11``
    from scripts.select_benchmark_v11 import select as replay_selection

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - environment/setup failure
    raise SystemExit("jsonschema is required: python3 -m pip install jsonschema") from exc


SCHEMA_VERSION = "c5k4-benchmark-1.1"
SCHEMA = Path(__file__).parents[1] / "schemas" / "benchmark-v1.1.schema.json"
ZERO_SHA256 = "0" * 64
OUTCOMES = (
    "CROSS",
    "ZERO_COMPLETE",
    "THEOREM_STRUCTURE",
    "PRESEARCH_STOP",
    "TIMEOUT",
    "PROTOCOL_INVALID",
)
QUOTAS = {
    "GRAPH_SCALAR_INEQUALITY": 3,
    "GRAPH_STRUCTURAL_PROPERTY": 3,
    "FINITE_ALGEBRA_EQUATIONAL": 2,
    "AUTOMATA_GAME_PROCESS": 2,
    "FINITE_COMBINATORIAL": 2,
}
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
POST_C0_PHASES = {
    "C0_FROZEN",
    "C1_SELECTED",
    "EVALUATING",
    "COMPLETE",
    "NO_ELIGIBLE_BENCHMARK",
}
POST_C1_PHASES = {"C1_SELECTED", "EVALUATING", "COMPLETE"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_row_sha256(row: dict[str, Any]) -> str:
    """Digest a ledger row after removing its self-authenticating digest."""

    payload = {key: value for key, value in row.items() if key != "row_sha256"}
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(encoded)


def _repo_root(path: Path) -> Path:
    for parent in (path.parent, *path.parents):
        if (parent / ".git").exists():
            return parent
    return path.parent


def resolve_path(manifest_path: Path, recorded: str) -> Path:
    candidate = Path(recorded)
    if candidate.is_absolute():
        return candidate
    rooted = _repo_root(manifest_path) / candidate
    if rooted.exists():
        return rooted
    return manifest_path.parent / candidate


def _timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")


def schema_findings(manifest: dict[str, Any]) -> list[Finding]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    findings = []
    for error in sorted(validator.iter_errors(manifest), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        findings.append(Finding("error", "SCHEMA", location, error.message))
    return findings


def _file_references(manifest: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    yield "upstream.open_inventory", manifest["upstream"]["open_inventory"]
    for name, value in manifest["freeze_artifacts"].items():
        yield f"freeze_artifacts.{name}", value
    yield "contamination.inventory", manifest["contamination"]["inventory"]
    if manifest["selection"]["evidence"] is not None:
        yield "selection.evidence", manifest["selection"]["evidence"]
    if manifest["randomness"]["verification"]["raw_artifact"] is not None:
        yield "randomness.verification.raw_artifact", manifest["randomness"]["verification"]["raw_artifact"]
    for cluster_index, cluster in enumerate(manifest["clusters"]):
        for contract_name in (
            "shared_analysis_contract",
            "independent_verification_contract",
        ):
            reference = cluster.get(contract_name)
            if reference is not None:
                yield f"clusters.{cluster_index}.{contract_name}", reference
        if cluster["arms"] is None:
            continue
        for arm_name in ARMS:
            yield (
                f"clusters.{cluster_index}.arms.{arm_name}.contract",
                cluster["arms"][arm_name]["contract"],
            )
    for ledger_index, ledger in enumerate(manifest["ledgers"]):
        yield f"ledgers.{ledger_index}", ledger


def _probability_findings(
    vector: dict[str, str], location: str, error: Any
) -> None:
    try:
        values = [Fraction(vector[outcome]) for outcome in OUTCOMES]
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        error("PROBABILITY_PARSE", location, f"not an exact rational vector: {exc}")
        return
    if any(value <= 0 or value >= 1 for value in values):
        error("PROBABILITY_ENDPOINT", location, "probabilities must lie strictly between 0 and 1")
    if any(value.denominator > 20 or value * 20 != int(value * 20) for value in values):
        error("PROBABILITY_INCREMENT", location, "probabilities must use increments of exactly 0.05")
    if sum(values, Fraction(0)) != 1:
        error("PROBABILITY_SIMPLEX", location, f"probabilities sum to {sum(values)}, not 1")


def semantic_findings(manifest: dict[str, Any], manifest_path: Path) -> list[Finding]:
    findings: list[Finding] = []

    def error(code: str, path: str, message: str) -> None:
        findings.append(Finding("error", code, path, message))

    # Every artifact named by a freeze or evaluation record is content-addressed.
    for location, reference in _file_references(manifest):
        path = resolve_path(manifest_path, reference["path"])
        if not path.is_file():
            error("ARTIFACT_MISSING", f"{location}.path", f"artifact does not exist: {path}")
        elif sha256_file(path).lower() != reference["sha256"].lower():
            error("ARTIFACT_DIGEST", f"{location}.sha256", "artifact SHA-256 mismatch")

    _probability_findings(
        manifest["freeze_artifacts"]["development_prior"]["probabilities"],
        "freeze_artifacts.development_prior.probabilities",
        error,
    )

    phase = manifest["phase"]
    chronology = manifest["chronology"]
    clusters = manifest["clusters"]
    randomness = manifest["randomness"]
    raw_randomness = randomness["verification"]["raw_artifact"]
    times = {key: _timestamp(value) for key, value in chronology.items() if key.endswith("_utc")}
    round_close = _timestamp(randomness["round_closes_at_utc"])

    if phase == "PROTOCOL_DESIGN":
        if clusters:
            error("PREMATURE_SELECTION", "clusters", "protocol design cannot contain selected clusters")
        if any(value is not None for value in chronology.values()):
            error("PREMATURE_FREEZE", "chronology", "protocol design chronology must remain null")
        if randomness["value"] is not None or randomness["value_sha256"] is not None:
            error("PREMATURE_RANDOMNESS", "randomness.value", "future value must be unknown before C0")
        if raw_randomness is not None:
            error("PREMATURE_RANDOMNESS_ARTIFACT", "randomness.verification.raw_artifact", "future raw response must be unknown before C0")
        if manifest["selection"]["evidence"] is not None:
            error("PREMATURE_SELECTION_EVIDENCE", "selection.evidence", "protocol design cannot contain C1 evidence")

    if phase in POST_C0_PHASES:
        if chronology["c0_commit"] is None or times["c0_published_at_utc"] is None:
            error("C0_REQUIRED", "chronology", f"phase {phase} requires a published C0")
    if times["c0_published_at_utc"] is not None and round_close is not None:
        if round_close <= times["c0_published_at_utc"]:
            error("RANDOMNESS_NOT_FUTURE", "randomness.round_closes_at_utc", "round must close after C0 is public")

    if phase == "C0_FROZEN":
        if clusters:
            error("PREMATURE_SELECTION", "clusters", "C0 cannot already contain C1 selections")
        if randomness["value"] is not None or randomness["value_sha256"] is not None:
            error("PREMATURE_RANDOMNESS", "randomness.value", "C0 must not know the future value")
        if raw_randomness is not None:
            error("PREMATURE_RANDOMNESS_ARTIFACT", "randomness.verification.raw_artifact", "C0 must not contain the future raw response")
        if manifest["selection"]["evidence"] is not None:
            error("PREMATURE_SELECTION_EVIDENCE", "selection.evidence", "C0 cannot contain C1 evidence")
        for key in ("randomness_retrieved_at_utc", "c1_frozen_at_utc", "evaluation_started_at_utc", "completed_at_utc"):
            if times[key] is not None:
                error("PREMATURE_CHRONOLOGY", f"chronology.{key}", "timestamp is later than C0")

    if phase in POST_C1_PHASES or phase == "NO_ELIGIBLE_BENCHMARK":
        if randomness["value"] is None or randomness["value_sha256"] is None:
            error("RANDOMNESS_REQUIRED", "randomness", f"phase {phase} requires the unlocked value and digest")
        elif sha256_bytes(randomness["value"].encode("utf-8")) != randomness["value_sha256"].lower():
            error("RANDOMNESS_DIGEST", "randomness.value_sha256", "digest is not SHA-256 of UTF-8 value")
        required = ("randomness_retrieved_at_utc", "c1_frozen_at_utc")
        if chronology["c1_commit"] is None or any(times[key] is None for key in required):
            error("C1_REQUIRED", "chronology", f"phase {phase} requires randomness retrieval and C1")
        if raw_randomness is None:
            error("RANDOMNESS_ARTIFACT_REQUIRED", "randomness.verification.raw_artifact", f"phase {phase} requires frozen verified relay responses")
        if manifest["selection"]["evidence"] is None:
            error("SELECTION_EVIDENCE_REQUIRED", "selection.evidence", f"phase {phase} requires sampler evidence")

    if phase in POST_C1_PHASES:
        if len(clusters) != 12:
            error("CLUSTER_COUNT", "clusters", f"C1 must freeze exactly 12 clusters; found {len(clusters)}")
        counts = Counter(cluster["stratum"] for cluster in clusters)
        if counts != Counter(QUOTAS):
            error("STRATA_QUOTAS", "clusters", f"observed {dict(counts)}; required {QUOTAS}")
    elif phase == "NO_ELIGIBLE_BENCHMARK":
        if len(clusters) >= 12:
            error("NO_ELIGIBLE_SHAPE", "clusters", "NO_ELIGIBLE_BENCHMARK requires an incomplete selection")
        if times["evaluation_started_at_utc"] is not None:
            error("NO_ELIGIBLE_EVALUATION", "chronology.evaluation_started_at_utc", "no evaluation is allowed")

    evidence_reference = manifest["selection"]["evidence"]
    if evidence_reference is not None:
        evidence_path = resolve_path(manifest_path, evidence_reference["path"])
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            error("SELECTION_EVIDENCE_PARSE", "selection.evidence.path", f"cannot parse sampler evidence: {exc}")
        else:
            recorded_digest = evidence.get("evidence_sha256")
            unsigned = {key: value for key, value in evidence.items() if key != "evidence_sha256"}
            computed_digest = sha256_bytes(json.dumps(
                unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8"))
            if recorded_digest != computed_digest:
                error("SELECTION_EVIDENCE_DIGEST", "selection.evidence.path", "internal sampler evidence digest mismatch")
            expected_status = "NO_ELIGIBLE_BENCHMARK" if phase == "NO_ELIGIBLE_BENCHMARK" else "SELECTED"
            if evidence.get("status") != expected_status:
                error("SELECTION_EVIDENCE_STATUS", "selection.evidence.path", "sampler status disagrees with benchmark phase")
            selected_ids = [row.get("cluster_id") for row in evidence.get("selected_clusters", []) if isinstance(row, dict)]
            if selected_ids != [cluster["cluster_id"] for cluster in clusters]:
                error("SELECTION_EVIDENCE_MEMBERSHIP", "selection.evidence.path", "sampler selection disagrees with manifest clusters")
            evidence_randomness = evidence.get("randomness", {})
            if evidence_randomness.get("value") != randomness["value"] or evidence_randomness.get("value_sha256") != randomness["value_sha256"]:
                error("SELECTION_EVIDENCE_RANDOMNESS", "selection.evidence.path", "sampler randomness disagrees with manifest")
            evidence_upstream = evidence.get("pool", {}).get("upstream")
            if evidence_upstream != {"commit": manifest["upstream"]["commit"], "tree": manifest["upstream"]["tree"]}:
                error("SELECTION_EVIDENCE_UPSTREAM", "selection.evidence.path", "sampler upstream disagrees with manifest")
            if evidence.get("quotas") != QUOTAS:
                error("SELECTION_EVIDENCE_QUOTAS", "selection.evidence.path", "sampler quotas disagree with frozen quotas")
            pool_path = resolve_path(manifest_path, manifest["freeze_artifacts"]["pool_manifest"]["path"])
            if randomness["value"] is not None:
                try:
                    replayed = replay_selection(pool_path.read_bytes(), randomness["value"])
                except (OSError, ValueError) as exc:
                    error("SELECTION_REPLAY", "freeze_artifacts.pool_manifest.path", f"cannot replay frozen C1: {exc}")
                else:
                    if replayed != evidence:
                        error("SELECTION_REPLAY", "selection.evidence.path", "sampler evidence is not the exact replay of frozen pool and randomness")

    ids = [cluster["cluster_id"] for cluster in clusters]
    identities = [cluster["identity_sha256"].lower() for cluster in clusters]
    if len(ids) != len(set(ids)):
        error("CLUSTER_UNIQUENESS", "clusters", "cluster_id values must be unique")
    if len(identities) != len(set(identities)):
        error("IDENTITY_UNIQUENESS", "clusters", "identity digests must be unique")

    contaminated_ids = set(manifest["contamination"]["excluded_cluster_ids"])
    contaminated_identities = {
        digest.lower() for digest in manifest["contamination"]["excluded_identity_sha256s"]
    }
    contaminated_declarations = {
        digest.lower() for digest in manifest["contamination"]["excluded_declaration_sha256s"]
    }
    if contaminated_ids.intersection(ids):
        error("CONTAMINATED_CLUSTER", "clusters", "selected cluster_id appears in contamination inventory")
    if contaminated_identities.intersection(identities):
        error("CONTAMINATED_IDENTITY", "clusters", "selected identity appears in contamination inventory")

    declaration_keys: list[tuple[str, str]] = []
    declaration_hashes: list[str] = []
    declaration_root = manifest["upstream"]["declaration_root"]
    checkout_recorded = manifest["upstream"].get("checkout_path")
    checkout = resolve_path(manifest_path, checkout_recorded) if checkout_recorded else None
    checkout_root = checkout.resolve() if checkout is not None else None
    for cluster_index, cluster in enumerate(clusters):
        for declaration_index, declaration in enumerate(cluster["declarations"]):
            location = f"clusters.{cluster_index}.declarations.{declaration_index}"
            pure = PurePosixPath(declaration["path"])
            if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0] != declaration_root:
                error("UPSTREAM_PATH", f"{location}.path", "declaration must stay below pinned FormalConjectures/")
            declaration_keys.append((declaration["path"], declaration["declaration_name"]))
            declaration_hashes.append(declaration["file_sha256"].lower())
            if checkout_root is not None:
                local = checkout_root.joinpath(*pure.parts)
                try:
                    local.relative_to(checkout_root)
                except ValueError:
                    error("UPSTREAM_PATH", f"{location}.path", "declaration escapes pinned checkout")
                if not local.is_file():
                    error("UPSTREAM_DECLARATION_MISSING", f"{location}.path", f"not found in checkout: {local}")
                elif sha256_file(local).lower() != declaration["file_sha256"].lower():
                    error("UPSTREAM_DECLARATION_DIGEST", f"{location}.file_sha256", "pinned declaration digest mismatch")
    if len(declaration_keys) != len(set(declaration_keys)):
        error("DECLARATION_UNIQUENESS", "clusters", "one declaration occurs in more than one cluster")
    if contaminated_declarations.intersection(declaration_hashes):
        error("CONTAMINATED_DECLARATION", "clusters", "selected declaration digest appears in contamination inventory")

    # Exact forecasts and equal, isolated arm budgets.
    global_arm_budget = manifest["budgets"]["discovery_arm"]
    if global_arm_budget["cpu_budget_seconds"] > global_arm_budget["process_count"] * global_arm_budget["process_wall_cap_seconds"]:
        error("CPU_TOTAL", "budgets.discovery_arm.cpu_budget_seconds", "CPU budget exceeds process_count times wall cap")
    verification = manifest["budgets"]["independent_verification"]
    if verification["cpu_budget_seconds"] > verification["process_count"] * verification["process_wall_cap_seconds"]:
        error("CPU_TOTAL", "budgets.independent_verification.cpu_budget_seconds", "CPU budget exceeds process_count times wall cap")

    for index, cluster in enumerate(clusters):
        for forecast_name in ("selection_forecast", "intervention_forecast"):
            forecast = cluster[forecast_name]
            if forecast is not None:
                _probability_findings(forecast["probabilities"], f"clusters.{index}.{forecast_name}.probabilities", error)
        if phase in POST_C1_PHASES and cluster["selection_forecast"] is None:
            error("SELECTION_FORECAST", f"clusters.{index}.selection_forecast", "C1 requires a frozen selection forecast")

        if cluster["runnable"] is True:
            if cluster["arms"] is None or cluster["intervention_forecast"] is None or cluster["arms_frozen_at_utc"] is None:
                error("RUNNABLE_CONTRACT", f"clusters.{index}", "runnable unit requires intervention forecast and three frozen arms")
        elif cluster["runnable"] is False and cluster["arms"] is not None:
            error("STOPPED_ARMS", f"clusters.{index}.arms", "presearch-stopped unit cannot activate discovery arms")

        if cluster["arms"] is not None:
            signatures = []
            for arm_name in ARMS:
                arm = cluster["arms"][arm_name]
                signature = (
                    arm["process_count"],
                    arm["process_wall_cap_seconds"],
                    arm["cpu_budget_seconds"],
                )
                signatures.append(signature)
                global_signature = (
                    global_arm_budget["process_count"],
                    global_arm_budget["process_wall_cap_seconds"],
                    global_arm_budget["cpu_budget_seconds"],
                )
                if signature != global_signature:
                    error("ARM_GLOBAL_BUDGET", f"clusters.{index}.arms.{arm_name}", "arm differs from frozen global budget")
            if len(set(signatures)) != 1:
                error("ARM_BUDGET_EQUALITY", f"clusters.{index}.arms", "all three discovery arms must receive identical budgets")

        selection_time = _timestamp(cluster["selection_forecast"]["frozen_at_utc"]) if cluster["selection_forecast"] else None
        intervention_time = _timestamp(cluster["intervention_forecast"]["frozen_at_utc"]) if cluster["intervention_forecast"] else None
        arms_time = _timestamp(cluster["arms_frozen_at_utc"])
        evaluation_time = _timestamp(cluster["evaluation_started_at_utc"])
        if selection_time and times["c1_frozen_at_utc"] and selection_time > times["c1_frozen_at_utc"]:
            error("SELECTION_FORECAST_LATE", f"clusters.{index}.selection_forecast", "selection forecast must be frozen by C1")
        if selection_time and times["randomness_retrieved_at_utc"] and selection_time < times["randomness_retrieved_at_utc"]:
            error("SELECTION_FORECAST_EARLY", f"clusters.{index}.selection_forecast", "selection forecast cannot predate the randomness unlock")
        if intervention_time and times["c1_frozen_at_utc"] and intervention_time < times["c1_frozen_at_utc"]:
            error("INTERVENTION_FORECAST_EARLY", f"clusters.{index}.intervention_forecast", "intervention forecast cannot predate C1/source review")
        if intervention_time and arms_time and intervention_time > arms_time:
            error("INTERVENTION_FORECAST_LATE", f"clusters.{index}.intervention_forecast", "intervention forecast must precede arm freeze")
        if arms_time and times["c1_frozen_at_utc"] and arms_time < times["c1_frozen_at_utc"]:
            error("ARM_FREEZE_EARLY", f"clusters.{index}.arms_frozen_at_utc", "arm freeze cannot predate C1")
        if arms_time and evaluation_time and arms_time > evaluation_time:
            error("ARM_FREEZE_LATE", f"clusters.{index}.arms_frozen_at_utc", "arm contracts must precede evaluation")
        if evaluation_time:
            if cluster["runnable"] is not True:
                error("NONRUNNABLE_EVALUATION", f"clusters.{index}.evaluation_started_at_utc", "only runnable units can start arms")
            if times["randomness_retrieved_at_utc"] is None or times["c1_frozen_at_utc"] is None:
                error("EVALUATION_BEFORE_UNLOCK", f"clusters.{index}.evaluation_started_at_utc", "evaluation requires unlock and C1")
            else:
                if evaluation_time < times["randomness_retrieved_at_utc"] or evaluation_time < times["c1_frozen_at_utc"]:
                    error("EVALUATION_BEFORE_UNLOCK", f"clusters.{index}.evaluation_started_at_utc", "evaluation predates unlock or C1")
            if times["evaluation_started_at_utc"] and evaluation_time < times["evaluation_started_at_utc"]:
                error("CLUSTER_EVALUATION_EARLY", f"clusters.{index}.evaluation_started_at_utc", "cluster evaluation predates the benchmark evaluation start")

    ordered = [
        ("c0_published_at_utc", times["c0_published_at_utc"]),
        ("randomness.round_closes_at_utc", round_close),
        ("randomness_retrieved_at_utc", times["randomness_retrieved_at_utc"]),
        ("c1_frozen_at_utc", times["c1_frozen_at_utc"]),
        ("evaluation_started_at_utc", times["evaluation_started_at_utc"]),
        ("completed_at_utc", times["completed_at_utc"]),
    ]
    present = [(name, value) for name, value in ordered if value is not None]
    for (left_name, left), (right_name, right) in zip(present, present[1:]):
        if right < left:
            error("CHRONOLOGY", f"chronology.{right_name}", f"{right_name} predates {left_name}")

    if phase == "EVALUATING" and times["evaluation_started_at_utc"] is None:
        error("EVALUATION_TIMESTAMP", "chronology.evaluation_started_at_utc", "EVALUATING requires a start time")
    if phase == "COMPLETE":
        if times["completed_at_utc"] is None:
            error("COMPLETION_TIMESTAMP", "chronology.completed_at_utc", "COMPLETE requires a completion time")
        if any(cluster["terminal_outcome"] is None for cluster in clusters):
            error("TERMINAL_OUTCOME", "clusters", "COMPLETE requires all twelve terminal outcomes")

    return findings


def ledger_findings(manifest: dict[str, Any], manifest_path: Path) -> list[Finding]:
    findings: list[Finding] = []

    def error(code: str, path: str, message: str) -> None:
        findings.append(Finding("error", code, path, message))

    clusters = {cluster["cluster_id"]: cluster for cluster in manifest["clusters"]}
    usage: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"cpu": 0.0, "processes": set()})
    global_eval = _timestamp(manifest["chronology"]["evaluation_started_at_utc"])
    c1 = _timestamp(manifest["chronology"]["c1_frozen_at_utc"])
    unlock = _timestamp(manifest["chronology"]["randomness_retrieved_at_utc"])

    for ledger_index, reference in enumerate(manifest["ledgers"]):
        ledger_path = resolve_path(manifest_path, reference["path"])
        if not ledger_path.is_file():
            continue  # already emitted by semantic_findings
        previous = ZERO_SHA256
        for line_number, raw in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            location = f"{ledger_path}:{line_number}"
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                error("LEDGER_JSON", location, str(exc))
                continue
            if not isinstance(row, dict):
                error("LEDGER_ROW", location, "row must be an object")
                continue
            required = {
                "benchmark_id",
                "unit_id",
                "arm",
                "process_id",
                "contract_sha256",
                "transformation_id",
                "carrier_sha256",
                "previous_row_sha256",
                "row_sha256",
                "wall_seconds",
                "cpu_seconds",
                "evaluated_at_utc",
            }
            missing = sorted(required.difference(row))
            if missing:
                error("LEDGER_FIELDS", location, f"missing required fields: {', '.join(missing)}")
                continue
            if row["benchmark_id"] != manifest["benchmark_id"]:
                error("LEDGER_BENCHMARK", location, "benchmark_id mismatch")
            cluster = clusters.get(row["unit_id"])
            if cluster is None:
                error("LEDGER_UNIT", location, "unit_id is not a frozen cluster")
            arm_name = row["arm"]
            if arm_name not in (*ARMS, "SHARED_ANALYSIS", "INDEPENDENT_VERIFICATION"):
                error("LEDGER_ARM", location, f"unknown arm {arm_name!r}")
            if str(row["previous_row_sha256"]).lower() != previous:
                error("LEDGER_CHAIN", location, f"previous digest should be {previous}")
            calculated = canonical_row_sha256(row)
            if str(row["row_sha256"]).lower() != calculated:
                error("LEDGER_ROW_DIGEST", location, f"row digest should be {calculated}")
            previous = str(row["row_sha256"]).lower()

            for field in ("contract_sha256", "carrier_sha256", "previous_row_sha256", "row_sha256"):
                value = row[field]
                if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdefABCDEF" for char in value):
                    error("LEDGER_SHA256", f"{location}.{field}", "must be a 64-digit hexadecimal SHA-256")
            wall = row["wall_seconds"]
            cpu = row["cpu_seconds"]
            if isinstance(wall, bool) or not isinstance(wall, (int, float)) or wall < 0 or wall > 60:
                error("LEDGER_WALL_CAP", location, "wall_seconds must lie in [0, 60]")
            if isinstance(cpu, bool) or not isinstance(cpu, (int, float)) or cpu < 0 or cpu > 60:
                error("LEDGER_CPU_CAP", location, "one subprocess cpu_seconds must lie in [0, 60]")

            try:
                evaluated = _timestamp(row["evaluated_at_utc"])
            except (TypeError, ValueError):
                evaluated = None
                error("LEDGER_TIMESTAMP", location, "evaluated_at_utc is not a UTC timestamp")
            if evaluated is not None and (unlock is None or c1 is None or evaluated < unlock or evaluated < c1):
                error("LEDGER_BEFORE_UNLOCK", location, "ledger evaluation predates unlock or C1")
            if evaluated is not None and global_eval is not None and evaluated < global_eval:
                error("LEDGER_BEFORE_EVALUATION", location, "row predates benchmark evaluation start")

            if cluster is not None and arm_name in ARMS and cluster["arms"] is not None:
                arm = cluster["arms"][arm_name]
                if row["contract_sha256"].lower() != arm["contract"]["sha256"].lower():
                    error("LEDGER_CONTRACT", location, "contract digest differs from frozen arm")
                if row["transformation_id"] != arm["transformation_id"]:
                    error("LEDGER_TRANSFORMATION", location, "transformation differs from frozen arm")
            usage[(row["unit_id"], arm_name)]["cpu"] += float(cpu) if isinstance(cpu, (int, float)) and not isinstance(cpu, bool) else 0.0
            usage[(row["unit_id"], arm_name)]["processes"].add(str(row["process_id"]))

    discovery_budget = manifest["budgets"]["discovery_arm"]
    verification_budget = manifest["budgets"]["independent_verification"]
    shared_budget = manifest["budgets"]["shared_analysis"]
    for (unit_id, arm_name), observed in usage.items():
        if arm_name in ARMS:
            process_limit = discovery_budget["process_count"]
            cpu_limit = discovery_budget["cpu_budget_seconds"]
        elif arm_name == "INDEPENDENT_VERIFICATION":
            process_limit = verification_budget["process_count"]
            cpu_limit = verification_budget["cpu_budget_seconds"]
        else:
            process_limit = None
            cpu_limit = shared_budget["cpu_budget_seconds"]
        if process_limit is not None and len(observed["processes"]) > process_limit:
            error("LEDGER_PROCESS_TOTAL", f"ledgers.{unit_id}.{arm_name}", f"uses {len(observed['processes'])} processes; cap is {process_limit}")
        if observed["cpu"] > cpu_limit:
            error("LEDGER_CPU_TOTAL", f"ledgers.{unit_id}.{arm_name}", f"uses {observed['cpu']} CPU-seconds; cap is {cpu_limit}")

    return findings


def lint_manifest(manifest_path: Path) -> list[Finding]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [Finding("error", "INPUT", str(manifest_path), str(exc))]
    if not isinstance(manifest, dict):
        return [Finding("error", "INPUT", str(manifest_path), "manifest must be a JSON object")]
    if manifest.get("schema_version") != SCHEMA_VERSION:
        return [Finding("error", "SCHEMA_VERSION", str(manifest_path), f"expected {SCHEMA_VERSION}")]
    findings = schema_findings(manifest)
    if findings:
        return findings
    findings.extend(semantic_findings(manifest, manifest_path))
    findings.extend(ledger_findings(manifest, manifest_path))
    return findings


def print_findings(findings: list[Finding], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps([asdict(item) for item in findings], indent=2, sort_keys=True))
        return
    for finding in findings:
        print(f"{finding.severity.upper()} {finding.code} {finding.path}: {finding.message}")
    print(f"benchmark-v1.1 lint: {sum(item.severity == 'error' for item in findings)} error(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    findings = lint_manifest(args.manifest.resolve())
    print_findings(findings, args.format)
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
