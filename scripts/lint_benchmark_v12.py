#!/usr/bin/env python3
"""Fail-closed validator for Method v1.2 benchmark manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover
    raise SystemExit("jsonschema is required") from exc

try:
    from select_benchmark_v12 import ARTIFACT_KEYS, canonical_json, select as replay_selection
except ModuleNotFoundError:  # pragma: no cover
    from scripts.select_benchmark_v12 import ARTIFACT_KEYS, canonical_json, select as replay_selection

try:
    from score_benchmark_v12 import ScoreError, score_manifest as replay_score
except ModuleNotFoundError:  # pragma: no cover
    from scripts.score_benchmark_v12 import ScoreError, score_manifest as replay_score


SCHEMA_VERSION = "c5k4-benchmark-1.2"
SCHEMA = Path(__file__).parents[1] / "schemas" / "benchmark-v1.2.schema.json"
ZERO_SHA256 = "0" * 64
STRATA = (
    "GRAPH_SCALAR_INEQUALITY", "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL", "AUTOMATA_GAME_PROCESS",
    "FINITE_COMBINATORIAL",
)
QUOTAS = dict(zip(STRATA, (3, 3, 2, 2, 2)))
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
C1_PHASES = {"C1_SELECTED", "EVALUATING", "COMPLETE", "PROTOCOL_INVALID"}
C0_PHASES = {"C0_FROZEN", *C1_PHASES}
ALLOWED_ATTESTATION_CHANGES = {
    "p0": {"phase", "chronology.p0_attestation_commit", "chronology.p0_published_at_utc"},
    "f0": {"phase", "chronology.f0_attestation_commit", "chronology.f0_published_at_utc"},
    "c0": {"phase", "chronology.c0_attestation_commit", "chronology.c0_published_at_utc"},
    "c1": {"phase", "chronology.c1_attestation_commit", "chronology.c1_frozen_at_utc"},
    "r0": {"phase", "chronology.r0_attestation_commit", "chronology.completed_at_utc"},
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_row_sha256(row: dict[str, Any]) -> str:
    return sha256(canonical_json({k: v for k, v in row.items() if k != "row_sha256"}))


def canonical_object_sha256(value: dict[str, Any], digest_key: str | None = None) -> str:
    if digest_key:
        value = {key: item for key, item in value.items() if key != digest_key}
    return sha256(canonical_json(value))


def _repo_root(path: Path) -> Path:
    for parent in (path.parent, *path.parents):
        if (parent / ".git").exists():
            return parent
    return path.parent


def resolve_path(manifest_path: Path, recorded: str) -> Path:
    path = Path(recorded)
    if path.is_absolute():
        return path
    rooted = _repo_root(manifest_path) / path
    return rooted if rooted.exists() else manifest_path.parent / path


def timestamp(value: str | None) -> datetime | None:
    return None if value is None else datetime.fromisoformat(value.removesuffix("Z") + "+00:00")


def schema_findings(manifest: dict[str, Any]) -> list[Finding]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    return [
        Finding("error", "SCHEMA", ".".join(map(str, error.absolute_path)) or "$", error.message)
        for error in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))
    ]


def _references(manifest: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    protocol = manifest["protocol"]
    for name in ("p0_artifact", "p0_attestation", "upstream_resolution_rule"):
        yield f"protocol.{name}", protocol[name]
    for index, ref in enumerate(protocol["prototype_artifacts"]):
        yield f"protocol.prototype_artifacts.{index}", ref
    for index, snapshot in enumerate([manifest["source_snapshots"]["s0"], *manifest["source_snapshots"]["supplemental"]]):
        yield f"source_snapshots.{index}", {"path": snapshot["path"], "sha256": snapshot["file_sha256"]}
    for name, ref in manifest["freeze_artifacts"].items():
        if ref is not None:
            yield f"freeze_artifacts.{name}", ref
    raw = manifest["randomness"]["verified_artifact"]
    if raw is not None:
        yield "randomness.verified_artifact", raw
    evidence = manifest["selection"]["evidence"]
    if evidence is not None:
        yield "selection.evidence", evidence
    for i, cluster in enumerate(manifest["clusters"]):
        for field in ("shared_analysis_contract", "independent_verification_contract", "terminal_evidence", "theorem_evidence", "crossing_verification"):
            if cluster[field] is not None:
                yield f"clusters.{i}.{field}", cluster[field]
        if cluster["arms"]:
            for arm in ARMS:
                yield f"clusters.{i}.arms.{arm}.contract", cluster["arms"][arm]["contract"]
    for i, record in enumerate(manifest["provenance"]["records"]):
        for field in ("input_artifact", "output_artifact"):
            if record[field] is not None:
                yield f"provenance.records.{i}.{field}", record[field]
    for i, ledger in enumerate(manifest["ledgers"]):
        yield f"ledgers.{i}", ledger
    if manifest["scoring"] is not None:
        yield "scoring.input", manifest["scoring"]["input"]
        yield "scoring.result", manifest["scoring"]["result"]


def _load_json(path: Path, code: str, location: str, error: Any) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        error(code, location, str(exc))
        return None
    if not isinstance(value, dict):
        error(code, location, "artifact must be a JSON object")
        return None
    return value


def semantic_findings(manifest: dict[str, Any], manifest_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    def error(code: str, path: str, message: str) -> None:
        findings.append(Finding("error", code, path, message))

    artifact_bytes: dict[str, bytes] = {}
    for location, reference in _references(manifest):
        path = resolve_path(manifest_path, reference["path"])
        if not path.is_file():
            error("ARTIFACT_MISSING", f"{location}.path", f"artifact does not exist: {path}")
            continue
        raw = path.read_bytes()
        artifact_bytes[location] = raw
        if sha256(raw) != reference["sha256"]:
            error("ARTIFACT_DIGEST", f"{location}.sha256", "artifact SHA-256 mismatch")

    phase = manifest["phase"]
    chronology = manifest["chronology"]
    times = {key: timestamp(value) for key, value in chronology.items() if key.endswith("_utc")}
    feasibility = manifest["quota_feasibility"]
    randomness = manifest["randomness"]
    clusters = manifest["clusters"]
    freeze = manifest["freeze_artifacts"]

    # Prototype artifacts may be retained as audit context, never promoted to a freeze.
    authoritative_paths = {ref["path"] for key, ref in freeze.items() if ref is not None}
    for index, ref in enumerate(manifest["protocol"]["prototype_artifacts"]):
        if ref["path"] in authoritative_paths:
            error("PROTOTYPE_AUTHORITATIVE", f"protocol.prototype_artifacts.{index}", "PRE_P0 prototype cannot satisfy an authoritative freeze slot")

    # P0/S0/source completeness and chronology.
    required_p0 = ("p0_artifact_commit", "p0_attestation_commit", "p0_published_at_utc")
    if phase != "PROTOCOL_DESIGN" and any(chronology[key] is None for key in required_p0):
        error("P0_REQUIRED", "chronology", "post-design phases require P0A/P0T publication")
    if times["p0_published_at_utc"] and times["s0_acquired_at_utc"] and not times["p0_published_at_utc"] < times["s0_acquired_at_utc"]:
        error("P0_S0_CHRONOLOGY", "chronology.s0_acquired_at_utc", "P0T publication must predate S0")
    snapshots = [manifest["source_snapshots"]["s0"], *manifest["source_snapshots"]["supplemental"]]
    if manifest["source_snapshots"]["canonical_sha256"] != canonical_object_sha256(manifest["source_snapshots"], "canonical_sha256"):
        error("SOURCE_SNAPSHOTS_DIGEST", "source_snapshots.canonical_sha256", "inline snapshot-set digest does not replay")
    if not manifest["source_snapshots"]["complete"] or any(not row["complete"] for row in snapshots):
        error("SOURCE_SNAPSHOT_INCOMPLETE", "source_snapshots", "every semantic source snapshot must complete")
    if chronology["s0_acquired_at_utc"] != snapshots[0]["acquired_at_utc"]:
        error("S0_MISMATCH", "chronology.s0_acquired_at_utc", "chronology must match the S0 snapshot")
    for index, snapshot in enumerate(snapshots):
        source_path = resolve_path(manifest_path, snapshot["path"])
        source = _load_json(source_path, "SOURCE_SNAPSHOT_PARSE", f"source_snapshots.{index}", error)
        if source is None:
            continue
        expected_schema = "c5k4-source-snapshot-S0-1.2" if index == 0 else "c5k4-source-snapshot-supplemental-1.2"
        if source.get("schema_version") != expected_schema or source.get("snapshot_id") != snapshot["snapshot_id"]:
            error("SOURCE_SNAPSHOT_SCHEMA", f"source_snapshots.{index}", "snapshot schema/id mismatch")
        if source.get("complete") is not True or source.get("candidate_semantics_inspected") is not False:
            error("SOURCE_SNAPSHOT_INCOMPLETE", f"source_snapshots.{index}", "snapshot must be complete and non-semantic")
        if source.get("snapshot_sha256") != snapshot["snapshot_sha256"] or canonical_object_sha256(source, "snapshot_sha256") != snapshot["snapshot_sha256"]:
            error("SOURCE_SNAPSHOT_DIGEST", f"source_snapshots.{index}", "internal snapshot digest does not replay")
        if source.get("corpus_sha256") != snapshot["corpus_sha256"] or source.get("acquired_at_utc") != snapshot["acquired_at_utc"]:
            error("SOURCE_SNAPSHOT_BINDING", f"source_snapshots.{index}", "inline snapshot metadata differs from artifact")
    if times["c0_published_at_utc"]:
        for index, snapshot in enumerate(snapshots):
            if timestamp(snapshot["acquired_at_utc"]) >= times["c0_published_at_utc"]:
                error("SNAPSHOT_AFTER_C0", f"source_snapshots.{index}", "all source snapshots must predate C0")

    # Provenance classes are exclusive by schema; semantic/unknown identity evidence excludes.
    producers = {row["producer_id"]: row for row in manifest["provenance"]["allowlisted_producers"]}
    input_schema = _load_json(resolve_path(manifest_path, freeze["registry_input_schema"]["path"]), "REGISTRY_SCHEMA_PARSE", "freeze_artifacts.registry_input_schema", error)
    output_schema = _load_json(resolve_path(manifest_path, freeze["registry_output_schema"]["path"]), "REGISTRY_SCHEMA_PARSE", "freeze_artifacts.registry_output_schema", error)
    record_ids: set[str] = set()
    for index, record in enumerate(manifest["provenance"]["records"]):
        location = f"provenance.records.{index}"
        if record["unit_id"] in record_ids:
            error("PROVENANCE_DUPLICATE_UNIT", location, "each scanned unit must have exactly one provenance record")
        record_ids.add(record["unit_id"])
        if record["mixed"]:
            error("PROVENANCE_MIXED", location, "mixed source units fail closed")
        if record["class"] == "MACHINE_REGISTRY_CONTACT":
            if record["producer_id"] not in producers or not record["schema_valid"] or record["input_sha256"] is None or record["output_sha256"] is None or record["input_artifact"] is None or record["output_artifact"] is None:
                error("PROVENANCE_LAUNDERING", location, "registry contact needs a frozen producer, invocation, inputs, and schema-valid output")
            else:
                for field, schema in (("input_artifact", input_schema), ("output_artifact", output_schema)):
                    value = _load_json(resolve_path(manifest_path, record[field]["path"]), "REGISTRY_ARTIFACT_PARSE", f"{location}.{field}", error)
                    if value is not None and schema is not None:
                        validation = list(jsonschema.Draft7Validator(schema).iter_errors(value))
                        if validation:
                            error("REGISTRY_SCHEMA_INVALID", f"{location}.{field}", validation[0].message)
                        if field == "output_artifact" and (
                            value.get("output_sha256") != canonical_object_sha256(value, "output_sha256")
                            or value.get("feasibility_replay", {}).get("row_source_artifact_id") != "eligible_pool"
                        ):
                            error("REGISTRY_OUTPUT_REPLAY", f"{location}.{field}", "registry output self-digest/eligible-row replay binding is invalid")
                if record["input_artifact"]["sha256"] != record["input_sha256"] or record["output_artifact"]["sha256"] != record["output_sha256"]:
                    error("PROVENANCE_DIGEST_BINDING", location, "provenance digests differ from bounded artifacts")
        elif record["producer_id"] is not None or record["schema_valid"]:
            error("PROVENANCE_LAUNDERING", location, "semantic/unknown source cannot be relabeled through machine provenance")

    pool_path = resolve_path(manifest_path, freeze["eligible_pool"]["path"])
    pool = _load_json(pool_path, "POOL_PARSE", "freeze_artifacts.eligible_pool", error)
    counts: Counter[str] = Counter()
    pool_rows: dict[str, dict[str, Any]] = {}
    if pool is not None:
        if pool.get("schema_version") != "c5k4-eligible-cluster-pool-1.2":
            error("POOL_SCHEMA", "freeze_artifacts.eligible_pool", "prototype or unknown pool schema cannot be authoritative")
        if pool.get("upstream") != {key: manifest["upstream"][key] for key in ("repository", "commit", "tree")}:
            error("UPSTREAM_MISMATCH", "freeze_artifacts.eligible_pool", "pool upstream pin differs from manifest")
        expected_digests = {f"{key}_sha256": freeze[key]["sha256"] for key in ARTIFACT_KEYS}
        if pool.get("digests") != expected_digests:
            error("POOL_DIGEST_BINDING", "freeze_artifacts.eligible_pool", "pool does not bind all six authoritative inputs")
        for i, row in enumerate(pool.get("clusters", [])):
            if not isinstance(row, dict) or not isinstance(row.get("cluster_id"), str):
                error("POOL_ROW", f"pool.clusters.{i}", "malformed pool row")
                continue
            pool_rows[row["cluster_id"]] = row
            semantic = bool(row.get("semantic_exposure"))
            unknown = bool(row.get("unknown_exposure"))
            expected = bool(row.get("machine_classification_unambiguous")) and bool(row.get("identity_grouping_complete")) and not semantic and not unknown
            if row.get("eligible") is not expected:
                error("ELIGIBILITY_INTERSECTION", f"pool.clusters.{i}.eligible", "eligible must be exact classification/grouping/no-semantic-or-unknown intersection")
            # Registry-only evidence stays visible but does not exclude.
            if row.get("eligible") and row.get("registry_contact_evidence_count", 0) < 0:
                error("REGISTRY_EVIDENCE", f"pool.clusters.{i}", "registry evidence count must be nonnegative")
            if row.get("eligible") and row.get("stratum") in STRATA:
                counts[row["stratum"]] += 1

    if phase == "PROTOCOL_DESIGN":
        if pool_rows or clusters or manifest["selection"]["evidence"] is not None or manifest["ledgers"] or manifest["aggregates"] is not None or manifest["scoring"] is not None:
            error("P0_TARGET_ROWS", "$", "P0 protocol design may not contain final target, selection, evaluation, or score rows")
        if randomness["state"] != "UNARMED" or any(value is not None for value in chronology.values()) or any(manifest["commit_pairs"].values()):
            error("PROTOCOL_DESIGN_SHAPE", "$", "protocol design must precede all phase chronology and entropy")
    if phase == "PRE_C0_FEASIBILITY":
        later = ("f0_artifact_commit", "c0_artifact_commit", "randomness_retrieved_at_utc", "c1_artifact_commit", "evaluation_started_at_utc", "r0_artifact_commit", "completed_at_utc")
        if randomness["state"] != "UNARMED" or clusters or manifest["selection"]["evidence"] is not None or any(chronology[key] is not None for key in later):
            error("PRE_C0_SHAPE", "$", "feasibility phase has no entropy, selected targets, or later chronology")

    # Replay the gate from rows; aggregates are never trusted.
    expected_strata = [{"stratum": s, "quota": QUOTAS[s], "eligible_count": counts[s], "deficit": max(0, QUOTAS[s] - counts[s]), "surplus": max(0, counts[s] - QUOTAS[s])} for s in STRATA]
    if feasibility["strata"] != expected_strata:
        error("FEASIBILITY_REPLAY", "quota_feasibility.strata", "counts/deficits do not replay from every pool row")
    expected_status = "PASS" if all(not row["deficit"] for row in expected_strata) else "FAIL"
    if feasibility["status"] != expected_status:
        error("FEASIBILITY_STATUS", "quota_feasibility.status", f"row replay requires {expected_status}")
    if pool is not None:
        expected_fd = sha256(pool_path.read_bytes())
        expected_cd = canonical_object_sha256(pool)
        if feasibility["digests"]["eligible_pool_file_sha256"] != expected_fd or feasibility["digests"]["eligible_pool_canonical_sha256"] != expected_cd:
            error("FEASIBILITY_POOL_DIGEST", "quota_feasibility.digests", "pool digests do not replay")
    if feasibility["certificate_sha256"] != canonical_object_sha256(feasibility, "certificate_sha256"):
        error("FEASIBILITY_CERTIFICATE_DIGEST", "quota_feasibility.certificate_sha256", "canonical certificate digest mismatch")
    for key in ARTIFACT_KEYS:
        expected = freeze[key]["sha256"]
        if feasibility["digests"][f"{key}_sha256"] != expected:
            error("FEASIBILITY_INPUT_DIGEST", f"quota_feasibility.digests.{key}_sha256", "certificate input digest mismatch")

    fail_phase = phase == "NO_ELIGIBLE_BENCHMARK_PRE_C0"
    if fail_phase:
        forbidden = ("c0_artifact_commit", "c0_attestation_commit", "c0_published_at_utc", "randomness_retrieved_at_utc", "c1_artifact_commit", "c1_attestation_commit", "c1_frozen_at_utc", "evaluation_started_at_utc", "r0_artifact_commit", "r0_attestation_commit", "completed_at_utc")
        if feasibility["status"] != "FAIL": error("FAIL_PHASE_GATE", "quota_feasibility.status", "pre-C0 terminal requires FAIL")
        if randomness["state"] != "UNARMED" or freeze["c0_randomness_contract"] is not None or freeze["c0_validation_receipt"] is not None:
            error("FAILED_GATE_BEACON", "randomness", "failed gate cannot arm or attach randomness")
        if clusters or manifest["selection"]["evidence"] or manifest["ledgers"] or manifest["aggregates"] is not None or manifest["scoring"] is not None or any(chronology[k] is not None for k in forbidden):
            error("PRE_C0_TERMINAL_SHAPE", "$", "pre-C0 failure has no C0/C1/selection/evaluation/result evidence")
        if chronology["f0_artifact_commit"] is not None or chronology["f0_attestation_commit"] is not None:
            error("CIRCULAR_F0", "chronology", "F0 scientific artifact cannot name F0A or F0T")
    if phase in C0_PHASES and feasibility["status"] != "PASS":
        error("C0_BEFORE_PASS", "phase", "only a replayed PASS gate can enter C0")
    if phase in C0_PHASES and (randomness["state"] == "UNARMED" or freeze["c0_randomness_contract"] is None):
        error("C0_RANDOMNESS_REQUIRED", "randomness", "C0 must arm one frozen future round")
    if randomness["state"] != "UNARMED" and times["c0_published_at_utc"] and timestamp(randomness["round_closes_at_utc"]) <= times["c0_published_at_utc"]:
        error("RANDOMNESS_NOT_FUTURE", "randomness.round_closes_at_utc", "round must close after C0T publication")
    if phase == "C0_FROZEN" and (randomness["state"] != "ARMED" or clusters or manifest["selection"]["evidence"] is not None):
        error("C0_SHAPE", "$", "C0 has null entropy and no selection")
    if phase == "C0_FROZEN" and chronology["c0_attestation_commit"] is not None:
        error("CIRCULAR_C0", "chronology.c0_attestation_commit", "C0T cannot contain its own commit ID")
    if phase == "C1_SELECTED":
        if chronology["c0_attestation_commit"] is None or freeze["c0_validation_receipt"] is None:
            error("C0_EXTERNAL_VALIDATION_REQUIRED", "chronology.c0_attestation_commit", "C1A must bind an externally validated C0T receipt/commit")
        if chronology["c1_artifact_commit"] is not None or chronology["c1_attestation_commit"] is not None:
            error("CIRCULAR_C1", "chronology", "C1A cannot name C1A or C1T")

    # Commit pairs prove null self-reference, direct ancestry, identical artifact tree, and allowlisted changes.
    # A phase artifact cannot name its own artifact/attestation commits.  A
    # pair becomes manifest evidence only in a strictly later phase.
    required_pairs = {"p0"} if phase != "PROTOCOL_DESIGN" else set()
    if phase in C1_PHASES: required_pairs.add("c0")
    if phase in {"EVALUATING", "COMPLETE", "PROTOCOL_INVALID"}: required_pairs.add("c1")
    forbidden_pairs = set()
    if phase == "NO_ELIGIBLE_BENCHMARK_PRE_C0": forbidden_pairs.add("f0")
    if phase == "C0_FROZEN": forbidden_pairs.add("c0")
    if phase == "C1_SELECTED": forbidden_pairs.add("c1")
    if phase == "COMPLETE": forbidden_pairs.add("r0")
    for name, pair in manifest["commit_pairs"].items():
        if name in required_pairs and pair is None:
            error("ATTESTATION_REQUIRED", f"commit_pairs.{name}", f"phase requires {name.upper()}A/{name.upper()}T")
        if name in forbidden_pairs and pair is not None:
            error("CIRCULAR_ATTESTATION", f"commit_pairs.{name}", "phase artifact cannot contain its own artifact/attestation commit pair")
        if pair is None: continue
        if pair["artifact_commit"] == pair["attestation_commit"] or pair["attested_artifact_commit"] != pair["artifact_commit"] or pair["attestation_parent"] != pair["artifact_commit"]:
            error("ATTESTATION_ANCESTRY", f"commit_pairs.{name}", "attestation must be distinct, directly descend from, and identify artifact commit")
        if pair["artifact_tree_sha256"] != pair["attested_artifact_tree_sha256"]:
            error("ATTESTATION_ARTIFACT_DRIFT", f"commit_pairs.{name}", "content-addressed artifact tree changed")
        if not set(pair["changed_fields"]).issubset(ALLOWED_ATTESTATION_CHANGES[name]):
            error("ATTESTATION_CHANGES", f"commit_pairs.{name}.changed_fields", "attestation changed non-allowlisted fields")

    # C1 is exact selector replay and all selected declarations remain pinned/in denominator.
    if phase in C1_PHASES:
        if len(clusters) != 12 or Counter(row["stratum"] for row in clusters) != Counter(QUOTAS):
            error("C1_QUOTAS", "clusters", "C1 requires exactly twelve unique fixed-quota clusters")
        ids = [row["cluster_id"] for row in clusters]
        if len(set(ids)) != 12: error("C1_UNIQUENESS", "clusters", "selected cluster IDs must be unique")
        evidence_ref = manifest["selection"]["evidence"]
        if evidence_ref is None:
            error("SELECTION_EVIDENCE_REQUIRED", "selection.evidence", "C1 needs replay evidence")
        else:
            evidence_path = resolve_path(manifest_path, evidence_ref["path"])
            evidence = _load_json(evidence_path, "SELECTION_EVIDENCE_PARSE", "selection.evidence", error)
            selector_artifacts = {key: artifact_bytes.get(f"freeze_artifacts.{key}") for key in ARTIFACT_KEYS}
            c0_ref = freeze["c0_randomness_contract"]
            raw_ref = randomness["verified_artifact"]
            receipt_ref = freeze["c0_validation_receipt"]
            if c0_ref and receipt_ref and raw_ref and all(value is not None for value in selector_artifacts.values()):
                try:
                    replayed = replay_selection(pool_path.read_bytes(), resolve_path(manifest_path, freeze["feasibility_certificate"]["path"]).read_bytes(), selector_artifacts, resolve_path(manifest_path, c0_ref["path"]).read_bytes(), resolve_path(manifest_path, receipt_ref["path"]).read_bytes(), resolve_path(manifest_path, raw_ref["path"]).read_bytes())
                except (OSError, ValueError) as exc:
                    error("SELECTION_REPLAY", "selection.evidence", str(exc))
                else:
                    if evidence != replayed: error("SELECTION_REPLAY_DRIFT", "selection.evidence", "selection is not exact deterministic replay")
                    selected = evidence.get("selected_clusters", []) if evidence else []
                    if [row.get("cluster_id") for row in selected] != ids: error("SELECTION_MEMBERSHIP", "clusters", "manifest membership/order differs from replay")
        checkout = manifest["upstream"].get("checkout_path")
        for i, cluster in enumerate(clusters):
            row = pool_rows.get(cluster["cluster_id"])
            if not row or row.get("identity_sha256") != cluster["identity_sha256"] or row.get("stratum") != cluster["stratum"] or not row.get("eligible"):
                error("POST_C1_REPLACEMENT", f"clusters.{i}", "cluster is not the exact eligible pool row selected at C1")
            for j, declaration in enumerate(cluster["declarations"]):
                pure = PurePosixPath(declaration["path"])
                if pure.is_absolute() or ".." in pure.parts or pure.parts[0] != "FormalConjectures":
                    error("UPSTREAM_PATH", f"clusters.{i}.declarations.{j}", "declaration escapes FormalConjectures/")
                if checkout:
                    local = resolve_path(manifest_path, checkout).joinpath(*pure.parts)
                    if not local.is_file() or sha256(local.read_bytes()) != declaration["file_sha256"]:
                        error("UPSTREAM_DECLARATION_DIGEST", f"clusters.{i}.declarations.{j}", "pinned source digest mismatch")

    global_budget = manifest["budgets"]["discovery_arm"]
    for i, cluster in enumerate(clusters):
        arms = cluster["arms"]
        evaluation = timestamp(cluster["evaluation_started_at_utc"])
        if cluster["runnable"] is True:
            if arms is None or cluster["shared_analysis_contract"] is None or cluster["independent_verification_contract"] is None:
                error("RUNNABLE_CONTRACTS", f"clusters.{i}", "runnable cluster needs shared, three arm, and verification contracts")
            if cluster["structural_zero"] is not None: error("STRUCTURAL_ZERO_RUNNABLE", f"clusters.{i}", "runnable cluster cannot get structural zero")
        elif cluster["runnable"] is False:
            if arms is not None or cluster["structural_zero"] is None:
                error("STRUCTURAL_ZERO_REQUIRED", f"clusters.{i}", "nonrunnable cluster needs exactly one structural-zero/tie record and no arms")
        if arms:
            signatures = []
            for arm_name in ARMS:
                arm = arms[arm_name]
                signature = (arm["process_count"], arm["process_wall_cap_seconds"], arm["cpu_budget_seconds"])
                signatures.append(signature)
                if signature != (global_budget["process_count"], global_budget["process_wall_cap_seconds"], global_budget["cpu_budget_seconds"]):
                    error("UNEQUAL_ARM_BUDGET", f"clusters.{i}.arms.{arm_name}", "arm differs from frozen 8x60/480 signature")
                if not arm["no_adaptation"]: error("ARM_ADAPTATION", f"clusters.{i}.arms.{arm_name}", "adaptation is forbidden")
                frozen = timestamp(arm["frozen_at_utc"]); started = timestamp(arm["started_at_utc"])
                if evaluation and frozen and frozen > evaluation: error("PREFREEZE_EVALUATION", f"clusters.{i}.arms.{arm_name}", "contract freeze follows evaluation")
                if started and frozen and started < frozen: error("PREFREEZE_EVALUATION", f"clusters.{i}.arms.{arm_name}", "arm started before contract freeze")
            if len(set(signatures)) != 1: error("UNEQUAL_ARM_BUDGET", f"clusters.{i}.arms", "discovery budgets differ")

    if phase == "COMPLETE":
        if any(row["terminal_outcome"] is None or row["terminal_evidence"] is None for row in clusters):
            error("TERMINAL_INCOMPLETE", "clusters", "all twelve selected clusters require terminal evidence")
        aggregates = manifest["aggregates"]
        if aggregates is None:
            error("AGGREGATES_REQUIRED", "aggregates", "complete benchmark needs ledger-derived aggregates")
        else:
            runnable_n = sum(row["runnable"] is True for row in clusters)
            zero_n = sum(row["structural_zero"] is not None for row in clusters)
            completed = {arm: sum(bool(row["arms"]) and row["arms"][arm]["status"] == "TERMINATED" for row in clusters) for arm in ARMS}
            if aggregates["selected_n"] != 12 or aggregates["aggregate_denominator"] != "ALL_SELECTED" or aggregates["runnable_n"] != runnable_n or aggregates["structural_zero_n"] != zero_n or aggregates["completed_arm_counts"] != completed:
                error("DENOMINATOR_SHRINKAGE", "aggregates", "headline aggregates must replay over all twelve selected clusters")
        if chronology["r0_artifact_commit"] is not None or chronology["r0_attestation_commit"] is not None:
            error("CIRCULAR_R0", "chronology", "R0 scientific artifact cannot name R0A or R0T")
        scoring = manifest["scoring"]
        if scoring is None:
            error("SCORING_REPLAY_REQUIRED", "scoring", "COMPLETE requires content-addressed scorer input and result")
        else:
            input_path = resolve_path(manifest_path, scoring["input"]["path"])
            result_path = resolve_path(manifest_path, scoring["result"]["path"])
            recorded = _load_json(result_path, "SCORE_RESULT_PARSE", "scoring.result", error)
            try:
                replayed_score = replay_score(input_path)
            except (OSError, ScoreError, ValueError) as exc:
                error("SCORING_REPLAY", "scoring.input", str(exc))
            else:
                if recorded != replayed_score:
                    error("SCORING_REPLAY_DRIFT", "scoring.result", "recorded scores differ from exact ledger-derived scorer replay")

    return findings


def ledger_findings(manifest: dict[str, Any], manifest_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    def error(code: str, path: str, message: str) -> None: findings.append(Finding("error", code, path, message))
    clusters = {row["cluster_id"]: row for row in manifest["clusters"]}
    usage: dict[tuple[str, str], dict[str, Any]] = defaultdict(lambda: {"cpu": 0.0, "processes": set()})
    for ledger_index, ref in enumerate(manifest["ledgers"]):
        path = resolve_path(manifest_path, ref["path"])
        if not path.is_file(): continue
        previous = ZERO_SHA256
        for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip(): continue
            where = f"{path}:{line_no}"
            try: row = json.loads(raw)
            except json.JSONDecodeError as exc: error("LEDGER_JSON", where, str(exc)); continue
            required = {"benchmark_id", "unit_id", "arm", "process_id", "contract_sha256", "previous_row_sha256", "row_sha256", "wall_seconds", "cpu_seconds", "evaluated_at_utc"}
            if not isinstance(row, dict) or not required.issubset(row): error("LEDGER_FIELDS", where, "ledger row fields missing"); continue
            if row["benchmark_id"] != manifest["benchmark_id"]: error("LEDGER_BENCHMARK", where, "benchmark mismatch")
            if row["unit_id"] not in clusters: error("LEDGER_UNIT", where, "unit is not selected")
            if row["arm"] not in (*ARMS, "SHARED_ANALYSIS", "INDEPENDENT_VERIFICATION"): error("LEDGER_ARM", where, "unknown arm")
            if row["previous_row_sha256"] != previous: error("LEDGER_CHAIN", where, "broken append-only chain")
            calculated = canonical_row_sha256(row)
            if row["row_sha256"] != calculated: error("LEDGER_ROW_DIGEST", where, "row digest mismatch")
            previous = row["row_sha256"]
            if not isinstance(row["wall_seconds"], (int, float)) or isinstance(row["wall_seconds"], bool) or not 0 <= row["wall_seconds"] <= 60: error("LEDGER_WALL_CAP", where, "wall cap exceeded")
            if not isinstance(row["cpu_seconds"], (int, float)) or isinstance(row["cpu_seconds"], bool) or not 0 <= row["cpu_seconds"] <= 60: error("LEDGER_CPU_CAP", where, "per-tree CPU cap exceeded")
            evaluated = timestamp(row["evaluated_at_utc"])
            cluster = clusters.get(row["unit_id"])
            if cluster and cluster["evaluation_started_at_utc"] and evaluated < timestamp(cluster["evaluation_started_at_utc"]): error("LEDGER_BEFORE_EVALUATION", where, "row predates cluster evaluation")
            usage[(row["unit_id"], row["arm"])]["cpu"] += float(row["cpu_seconds"])
            usage[(row["unit_id"], row["arm"])]["processes"].add(str(row["process_id"]))
    budgets = manifest["budgets"]
    for (unit, arm), observed in usage.items():
        budget = budgets["discovery_arm"] if arm in ARMS else budgets["independent_verification"] if arm == "INDEPENDENT_VERIFICATION" else budgets["shared_analysis"]
        if len(observed["processes"]) > budget["process_count"]: error("LEDGER_PROCESS_TOTAL", f"{unit}.{arm}", "process-tree cap exceeded")
        if observed["cpu"] > budget["cpu_budget_seconds"]: error("LEDGER_CPU_TOTAL", f"{unit}.{arm}", "CPU budget exceeded")
    return findings


def lint_manifest(path: Path) -> list[Finding]:
    try: manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: return [Finding("error", "INPUT", str(path), str(exc))]
    if not isinstance(manifest, dict): return [Finding("error", "INPUT", str(path), "manifest must be an object")]
    if manifest.get("schema_version") != SCHEMA_VERSION: return [Finding("error", "SCHEMA_VERSION", str(path), f"expected {SCHEMA_VERSION}")]
    findings = schema_findings(manifest)
    if findings: return findings
    findings.extend(semantic_findings(manifest, path))
    findings.extend(ledger_findings(manifest, path))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("manifest", type=Path); parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv); findings = lint_manifest(args.manifest.resolve())
    if args.format == "json": print(json.dumps([asdict(row) for row in findings], indent=2))
    else:
        for row in findings: print(f"{row.severity.upper()} {row.code} {row.path}: {row.message}")
        print(f"benchmark-v1.2 lint: {len(findings)} error(s)")
    return bool(findings)


if __name__ == "__main__": raise SystemExit(main())
