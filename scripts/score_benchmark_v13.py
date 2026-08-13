#!/usr/bin/env python3
"""Fail-closed, ledger-derived Method v1.3 full-denominator scorer."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SELECTOR_PATH = HERE / "select_benchmark_v13.py"
SPEC = importlib.util.spec_from_file_location("benchmark_v13_selector_for_score", SELECTOR_PATH)
assert SPEC is not None and SPEC.loader is not None
SELECTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SELECTOR
SPEC.loader.exec_module(SELECTOR)

SCHEMA_VERSION = "c5k4-benchmark-score-input-1.3"
RESULT_VERSION = "c5k4-benchmark-score-result-1.3"
ZERO_SHA256 = "0" * 64
OUTCOMES = (
    "CROSS", "ZERO_COMPLETE", "THEOREM_STRUCTURE", "PRESEARCH_STOP",
    "TIMEOUT", "PROTOCOL_INVALID",
)
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
TOP_LEVEL = {
    "schema_version", "benchmark_id", "phase", "selected_n",
    "aggregate_denominator", "development_prior", "scoring_rule", "selection_replay",
    "clusters", "ledgers",
}


class ScoreError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def row_digest(row: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json({k: v for k, v in row.items() if k != "row_sha256"})).hexdigest()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact(value: Any, where: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (str, int)):
        raise ScoreError("RATIONAL", f"{where} must be an integer or rational string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ScoreError("RATIONAL", f"{where} is not rational: {exc}") from exc


def ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def mean(values: list[Fraction]) -> Fraction:
    if not values:
        raise ScoreError("EMPTY_METRIC", "empty aggregate")
    return sum(values, Fraction()) / len(values)


def hex_digest(value: Any, where: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or value.lower() != value:
        raise ScoreError("SHA256", f"{where} must be 64 lowercase hexadecimal characters")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ScoreError("SHA256", f"{where} is not hexadecimal") from exc
    return value


def git_oid(value: Any, where: str) -> str:
    if not isinstance(value, str) or len(value) != 40 or value.lower() != value:
        raise ScoreError("GIT_OID", f"{where} must be 40 lowercase hexadecimal characters")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ScoreError("GIT_OID", f"{where} is not hexadecimal") from exc
    return value


def resolve(manifest_path: Path, recorded: Any) -> Path:
    if not isinstance(recorded, str) or not recorded:
        raise ScoreError("PATH", "artifact path must be a nonempty string")
    candidate = Path(recorded)
    if candidate.is_absolute():
        return candidate
    for parent in (manifest_path.parent, *manifest_path.parents):
        if (parent / ".git").exists():
            rooted = parent / candidate
            return rooted if rooted.exists() else manifest_path.parent / candidate
    return manifest_path.parent / candidate


def read_reference(manifest_path: Path, reference: Any, where: str) -> bytes:
    if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
        raise ScoreError("REFERENCE", f"{where} must contain exactly path and sha256")
    expected = hex_digest(reference["sha256"], f"{where}.sha256")
    path = resolve(manifest_path, reference["path"])
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ScoreError("REFERENCE", f"cannot read {where}: {exc}") from exc
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ScoreError("REFERENCE_DIGEST", f"{where} digest mismatch")
    return raw


def validate_vector(vector: Any, where: str) -> dict[str, str]:
    if not isinstance(vector, dict) or set(vector) != set(OUTCOMES):
        raise ScoreError("PROBABILITIES", f"{where} must contain exactly the six outcomes")
    values = []
    for outcome in OUTCOMES:
        value = exact(vector[outcome], f"{where}.{outcome}")
        if value <= 0 or value >= 1 or value * 20 != int(value * 20):
            raise ScoreError("PROBABILITIES", f"{where}.{outcome} is not a strict 0.05 increment")
        values.append(value)
    if sum(values, Fraction()) != 1:
        raise ScoreError("PROBABILITIES", f"{where} does not sum exactly to one")
    return vector


def replay_selection(manifest: dict[str, Any], manifest_path: Path) -> list[dict[str, Any]]:
    replay = manifest["selection_replay"]
    required = {
        "evidence", "eligible_pool", "quota_feasibility", "c0_contract",
        "c0_validation_receipt", "verified_randomness", *SELECTOR.ARTIFACT_KEYS,
    }
    if not isinstance(replay, dict) or set(replay) != required:
        raise ScoreError("SELECTION_REPLAY", "selection_replay has incomplete or unknown inputs")
    raw = {name: read_reference(manifest_path, ref, f"selection_replay.{name}") for name, ref in replay.items()}
    try:
        c0 = json.loads(raw["c0_contract"])
        receipt = json.loads(raw["c0_validation_receipt"])
        if receipt.get("schema_version") != "c5k4-c0-validation-receipt-1.3":
            raise ValueError("C0 validation receipt schema is not frozen v1.3")
        if receipt.get("receipt_sha256") != SELECTOR.object_digest(receipt, "receipt_sha256"):
            raise ValueError("C0 validation receipt digest does not replay")
        chronology = c0.get("chronology", {})
        c0t = receipt.get("c0t", {})
        expected_receipt = {
            "c0t": {"path": c0t.get("path"), "file_sha256": hashlib.sha256(raw["c0_contract"]).hexdigest()},
            "c0_artifact_commit": chronology.get("c0_artifact_commit"),
            "c0_attestation_commit": receipt.get("c0_attestation_commit"),
            "direct_nonmerge_parent_verified": True,
            "changed_paths": [c0t.get("path")],
            "committed_bytes_verified": True,
            "publication_observation": c0.get("publication_observation"),
            "c0_published_at_utc": chronology.get("c0_published_at_utc"),
            "future_round_close_at_utc": c0.get("randomness", {}).get("round_closes_at_utc"),
        }
        if any(receipt.get(key) != value for key, value in expected_receipt.items()):
            raise ValueError("C0 validation receipt does not authenticate exact external C0T validation")
        git_oid(receipt.get("c0_attestation_commit"), "c0_validation_receipt.c0_attestation_commit")
        expected = SELECTOR.select(
            raw["eligible_pool"], raw["quota_feasibility"],
            {name: raw[name] for name in SELECTOR.ARTIFACT_KEYS},
            raw["c0_contract"], raw["c0_validation_receipt"], raw["verified_randomness"],
        )
        recorded = json.loads(raw["evidence"])
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoreError("SELECTION_REPLAY", str(exc)) from exc
    if recorded != expected:
        raise ScoreError("SELECTION_REPLAY", "selection evidence is not the exact executable replay")
    selected = expected.get("selected_clusters")
    if not isinstance(selected, list) or len(selected) != 12:
        raise ScoreError("DENOMINATOR", "selection replay did not produce exactly twelve clusters")
    return selected


def load_ledgers(manifest: dict[str, Any], manifest_path: Path, cluster_ids: set[str]) -> list[dict[str, Any]]:
    references = manifest["ledgers"]
    if not isinstance(references, list) or not references:
        raise ScoreError("LEDGER", "at least one ledger is required")
    rows: list[dict[str, Any]] = []
    cpu: dict[tuple[str, str], Fraction] = defaultdict(Fraction)
    processes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for ledger_index, reference in enumerate(references):
        raw = read_reference(manifest_path, reference, f"ledgers[{ledger_index}]")
        previous = ZERO_SHA256
        for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
            if not line.strip():
                continue
            where = f"ledger[{ledger_index}]:{line_number}"
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ScoreError("LEDGER_JSON", f"{where}: {exc}") from exc
            base = {
                "benchmark_id", "unit_id", "arm", "process_id", "contract_sha256",
                "transformation_id", "carrier_sha256", "previous_row_sha256",
                "row_sha256", "wall_seconds", "cpu_seconds", "evaluated_at_utc",
            }
            if not isinstance(row, dict) or not base.issubset(row) or set(row) - base - {"score_event"}:
                raise ScoreError("LEDGER_FIELDS", f"{where} has invalid base fields")
            if row["benchmark_id"] != manifest["benchmark_id"] or row["unit_id"] not in cluster_ids:
                raise ScoreError("LEDGER_IDENTITY", f"{where} is outside the frozen benchmark")
            if row["arm"] not in (*ARMS, "SHARED_ANALYSIS", "INDEPENDENT_VERIFICATION"):
                raise ScoreError("LEDGER_ARM", f"{where} has unknown arm")
            for key in ("contract_sha256", "carrier_sha256", "previous_row_sha256", "row_sha256"):
                hex_digest(row[key], f"{where}.{key}")
            if row["previous_row_sha256"] != previous or row["row_sha256"] != row_digest(row):
                raise ScoreError("LEDGER_CHAIN", f"{where} breaks its ledger hash chain")
            previous = row["row_sha256"]
            wall = exact(row["wall_seconds"], f"{where}.wall_seconds")
            used = exact(row["cpu_seconds"], f"{where}.cpu_seconds")
            if wall < 0 or wall > 60 or used < 0 or used > 60:
                raise ScoreError("LEDGER_CAP", f"{where} exceeds a subprocess cap")
            key = (row["unit_id"], row["arm"])
            cpu[key] += used
            processes[key].add(str(row["process_id"]))
            row["__where"] = where
            rows.append(row)
    for (unit, arm), used in cpu.items():
        process_limit, cpu_limit = ((8, 480) if arm in ARMS else (2, 120) if arm == "INDEPENDENT_VERIFICATION" else (None, 600))
        if used > cpu_limit or (process_limit is not None and len(processes[(unit, arm)]) > process_limit):
            raise ScoreError("LEDGER_TOTAL_CAP", f"{unit}/{arm} exceeds its frozen aggregate cap")
    return rows


def gain(event: dict[str, Any], where: str) -> Fraction:
    status = event.get("status")
    if status not in ("COMPLETE", "TIMEOUT", "PROTOCOL_INVALID"):
        raise ScoreError("ARM_STATUS", f"{where} has invalid status")
    objective = event.get("objective")
    if status != "COMPLETE":
        if objective is not None:
            raise ScoreError("OBJECTIVE", f"{where} incomplete arm must have null objective")
        return Fraction()
    required = {"residual_orientation", "signed_residual", "frozen_control_residual"}
    if not isinstance(objective, dict) or set(objective) != required:
        raise ScoreError("OBJECTIVE", f"{where} has invalid objective fields")
    residual = exact(objective["signed_residual"], f"{where}.signed_residual")
    scale = max(Fraction(1), abs(exact(objective["frozen_control_residual"], f"{where}.control")))
    if objective["residual_orientation"] == "SAFE_NONNEGATIVE":
        return max(Fraction(), -residual) / scale
    if objective["residual_orientation"] == "SAFE_NONPOSITIVE":
        return max(Fraction(), residual) / scale
    raise ScoreError("OBJECTIVE", f"{where} has invalid residual orientation")


def brier(vector: dict[str, str], actual: str) -> Fraction:
    return sum((Fraction(vector[name]) - int(name == actual)) ** 2 for name in OUTCOMES)


def score_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScoreError("INPUT", str(exc)) from exc
    if not isinstance(manifest, dict) or set(manifest) != TOP_LEVEL:
        raise ScoreError("INPUT_FIELDS", "score input has incomplete or unknown top-level fields")
    if manifest["schema_version"] != SCHEMA_VERSION or manifest["phase"] != "COMPLETE":
        raise ScoreError("INCOMPLETE", "scoring requires a COMPLETE v1.3 input")
    if manifest["selected_n"] != 12 or manifest["aggregate_denominator"] != "ALL_SELECTED":
        raise ScoreError("DENOMINATOR", "selected_n=12 and ALL_SELECTED are mandatory")
    try:
        scoring_rule = json.loads(read_reference(manifest_path, manifest["scoring_rule"], "scoring_rule"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoreError("SCORING_RULE", f"scoring rule is not valid JSON: {exc}") from exc
    if (
        not isinstance(scoring_rule, dict)
        or scoring_rule.get("schema_version") != "c5k4-scoring-rule-1.3"
        or scoring_rule.get("selected_n") != 12
        or scoring_rule.get("aggregate_denominator") != "ALL_SELECTED"
    ):
        raise ScoreError("SCORING_RULE", "scoring rule does not freeze the v1.3 full denominator")
    prior = validate_vector(manifest["development_prior"], "development_prior")
    selected = replay_selection(manifest, manifest_path)
    clusters = manifest["clusters"]
    if not isinstance(clusters, list) or len(clusters) != 12:
        raise ScoreError("DENOMINATOR", "clusters must contain all twelve selected units")
    selected_pairs = [(row["cluster_id"], row["identity_sha256"]) for row in selected]
    cluster_pairs = [(row.get("cluster_id"), row.get("identity_sha256")) for row in clusters if isinstance(row, dict)]
    if cluster_pairs != selected_pairs or len(set(cluster_pairs)) != 12:
        raise ScoreError("SELECTION_MEMBERSHIP", "clusters differ from the ordered selection replay")

    cluster_fields = {
        "cluster_id", "identity_sha256", "selection_forecast", "intervention_forecast",
        "runnable", "structural_zero_reason", "terminal_outcome",
    }
    for index, cluster in enumerate(clusters):
        if set(cluster) != cluster_fields:
            raise ScoreError("CLUSTER_FIELDS", f"clusters[{index}] has invalid fields")
        validate_vector(cluster["selection_forecast"], f"clusters[{index}].selection_forecast")
        validate_vector(cluster["intervention_forecast"], f"clusters[{index}].intervention_forecast")
        if cluster["terminal_outcome"] not in OUTCOMES or type(cluster["runnable"]) is not bool:
            raise ScoreError("CLUSTER_STATE", f"clusters[{index}] has invalid state")
        reason = cluster["structural_zero_reason"]
        if cluster["runnable"] and reason is not None:
            raise ScoreError("STRUCTURAL_ZERO", f"{cluster['cluster_id']} runnable cluster has a structural-zero reason")
        if not cluster["runnable"] and (not isinstance(reason, str) or not reason.strip()):
            raise ScoreError("STRUCTURAL_ZERO", f"{cluster['cluster_id']} nonrunnable cluster lacks a reason")

    ids = {row["cluster_id"] for row in clusters}
    rows = load_ledgers(manifest, manifest_path, ids)
    arm_terminal: dict[tuple[str, str], list[tuple[dict, dict]]] = defaultdict(list)
    cluster_terminal: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    verification: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    cpu: dict[tuple[str, str], Fraction] = defaultdict(Fraction)
    for row in rows:
        if row["arm"] in ARMS:
            cpu[(row["unit_id"], row["arm"])] += exact(row["cpu_seconds"], f"{row['__where']}.cpu")
        event = row.get("score_event")
        if event is None:
            continue
        if not isinstance(event, dict):
            raise ScoreError("EVENT", f"{row['__where']} score_event is not an object")
        kind = event.get("kind")
        if kind == "ARM_TERMINAL":
            if row["arm"] not in ARMS or set(event) != {"kind", "status", "objective", "controlling_term"}:
                raise ScoreError("EVENT", f"{row['__where']} invalid arm terminal")
            arm_terminal[(row["unit_id"], row["arm"])].append((row, event))
        elif kind == "CLUSTER_TERMINAL":
            fields = {
                "kind", "terminal_outcome", "theorem_yield", "theorem_evidence",
                "theorem_evidence_sha256", "independent_countermodel_check",
                "crossing_candidate_sha256", "crossing_class", "protocol_invalid_evidence_sha256",
            }
            if row["arm"] != "SHARED_ANALYSIS" or set(event) != fields:
                raise ScoreError("EVENT", f"{row['__where']} invalid cluster terminal")
            cluster_terminal[row["unit_id"]].append((row, event))
        elif kind == "INDEPENDENT_VERIFICATION_TERMINAL":
            if row["arm"] != "INDEPENDENT_VERIFICATION" or set(event) != {"kind", "candidate_sha256", "result"}:
                raise ScoreError("EVENT", f"{row['__where']} invalid verification terminal")
            verification[row["unit_id"]].append((row, event))
        else:
            raise ScoreError("EVENT", f"{row['__where']} unknown score event")

    arm_gains = {arm: [] for arm in ARMS}
    arm_statuses = {arm: [] for arm in ARMS}
    completed = {arm: 0 for arm in ARMS}
    structural_reasons: dict[str, str] = {}
    sign_correct = sign_incorrect = sign_nonevaluable = 0
    theorem_values: list[Fraction] = []
    crossing_classes = {name: 0 for name in ("NOVEL", "RETRO", "AMBIGUOUS", "STATUS_PREEMPTED")}
    certified: list[dict] = []

    def one(mapping: dict, key: Any, description: str):
        values = mapping.get(key, [])
        if len(values) != 1:
            raise ScoreError("CARDINALITY", f"expected one {description}, found {len(values)}")
        return values[0]

    for cluster in clusters:
        unit = cluster["cluster_id"]
        _, terminal = one(cluster_terminal, unit, f"cluster terminal for {unit}")
        theorem = exact(terminal["theorem_yield"], f"{unit}.theorem_yield")
        theorem_kind = terminal["theorem_evidence"]
        theorem_sha = terminal["theorem_evidence_sha256"]
        if theorem not in (Fraction(), Fraction(1, 2), Fraction(1)):
            raise ScoreError("THEOREM", f"{unit} has invalid theorem yield")
        allowed = {Fraction(): {"NONE", "RETROSPECTIVE"}, Fraction(1, 2): {"SIGNAL"}, Fraction(1): {"PROVED"}}
        if theorem_kind not in allowed[theorem] or (theorem == Fraction(1, 2) and terminal["independent_countermodel_check"] is not True):
            raise ScoreError("THEOREM", f"{unit} theorem evidence does not justify yield")
        if theorem > 0:
            hex_digest(theorem_sha, f"{unit}.theorem_evidence_sha256")
        elif theorem_sha is not None:
            raise ScoreError("THEOREM", f"{unit} zero theorem yield has evidence digest")
        theorem_values.append(theorem)

        candidate = terminal["crossing_candidate_sha256"]
        crossing = candidate is not None
        if crossing:
            candidate = hex_digest(candidate, f"{unit}.candidate")
            if terminal["crossing_class"] not in crossing_classes:
                raise ScoreError("CROSSING", f"{unit} invalid crossing class")
            checks = verification.get(unit, [])
            good = [row for row, event in checks if event["result"] == "VERIFIED" and event["candidate_sha256"] == candidate and row["carrier_sha256"] == candidate]
            if len(checks) != 2 or len(good) != 2 or len({row["process_id"] for row in good}) != 2:
                raise ScoreError("CROSSING", f"{unit} lacks exactly two independent matching verifications")
            crossing_classes[terminal["crossing_class"]] += 1
            certified.append(cluster)
        elif terminal["crossing_class"] != "NONE" or verification.get(unit):
            raise ScoreError("CROSSING", f"{unit} non-crossing has crossing evidence")

        invalid_sha = terminal["protocol_invalid_evidence_sha256"]
        protocol_invalid = invalid_sha is not None
        if protocol_invalid:
            hex_digest(invalid_sha, f"{unit}.protocol_invalid_evidence_sha256")

        statuses: dict[str, str] = {}
        if cluster["runnable"]:
            for arm in ARMS:
                row, event = one(arm_terminal, (unit, arm), f"arm terminal for {unit}/{arm}")
                value = gain(event, row["__where"])
                statuses[arm] = event["status"]
                arm_gains[arm].append(value)
                arm_statuses[arm].append(event["status"])
                completed[arm] += int(event["status"] == "COMPLETE")
                controlling = event["controlling_term"]
                if arm == "WALL_NAVIGATION" and event["status"] == "COMPLETE":
                    if not isinstance(controlling, dict) or set(controlling) != {"forecast_sign", "observed_delta"} or controlling["forecast_sign"] not in (-1, 1):
                        raise ScoreError("CONTROLLING_TERM", f"{unit} invalid controlling-term record")
                    observed = exact(controlling["observed_delta"], f"{unit}.observed_delta")
                    observed_sign = (observed > 0) - (observed < 0)
                    if observed_sign == controlling["forecast_sign"]:
                        sign_correct += 1
                    else:
                        sign_incorrect += 1
                elif arm == "WALL_NAVIGATION" and event["status"] != "COMPLETE":
                    if controlling is not None:
                        raise ScoreError("CONTROLLING_TERM", f"{unit}/{arm} incomplete arm must have null controlling term")
                    sign_nonevaluable += 1
                elif controlling is not None:
                    raise ScoreError("CONTROLLING_TERM", f"{unit}/{arm} must have null controlling term")
            if terminal["protocol_invalid_evidence_sha256"] is None and "PROTOCOL_INVALID" in statuses.values():
                raise ScoreError("PROTOCOL_INVALID", f"{unit} invalid arm lacks evidence digest")
        else:
            if any((unit, arm) in arm_terminal for arm in ARMS):
                raise ScoreError("STRUCTURAL_ZERO", f"{unit} nonrunnable cluster has arm terminal rows")
            for arm in ARMS:
                arm_gains[arm].append(Fraction())
                arm_statuses[arm].append("STRUCTURAL_ZERO")
            structural_reasons[unit] = cluster["structural_zero_reason"]
            sign_nonevaluable += 1

        if crossing:
            expected = "CROSS"
        elif theorem > 0:
            expected = "THEOREM_STRUCTURE"
        elif cluster["runnable"] and set(statuses.values()) == {"COMPLETE"}:
            expected = "ZERO_COMPLETE"
        elif cluster["runnable"] and "TIMEOUT" in statuses.values():
            expected = "TIMEOUT"
        elif not cluster["runnable"] and not protocol_invalid:
            expected = "PRESEARCH_STOP"
        elif protocol_invalid or "PROTOCOL_INVALID" in statuses.values():
            expected = "PROTOCOL_INVALID"
        else:
            raise ScoreError("TERMINAL_PRECEDENCE", f"cannot derive terminal outcome for {unit}")
        if terminal["terminal_outcome"] != expected or cluster["terminal_outcome"] != expected:
            raise ScoreError("TERMINAL_PRECEDENCE", f"{unit} terminal outcome violates frozen precedence")
        if terminal["independent_countermodel_check"] not in (True, False):
            raise ScoreError("THEOREM", f"{unit} countermodel flag must be boolean")

    if sign_correct + sign_incorrect + sign_nonevaluable != 12:
        raise ScoreError("DENOMINATOR", "controlling-term counts do not sum to twelve")

    paired = {}
    for baseline in ("CATALOGUE", "GENERIC"):
        deltas = [wall - base for wall, base in zip(arm_gains["WALL_NAVIGATION"], arm_gains[baseline])]
        paired[f"WALL_NAVIGATION_vs_{baseline}"] = {
            "wins": sum(value > 0 for value in deltas),
            "losses": sum(value < 0 for value in deltas),
            "ties": sum(value == 0 for value in deltas),
        }

    arms = {}
    for arm in ARMS:
        total = sum(arm_gains[arm], Fraction())
        observed_cpu = sum((cpu[(cluster["cluster_id"], arm)] for cluster in clusters), Fraction())
        arms[arm] = {
            "selected_n": 12,
            "completed_arm_count": completed[arm],
            "structural_zero_count": arm_statuses[arm].count("STRUCTURAL_ZERO"),
            "total_normalized_gain": ratio(total),
            "mean_normalized_gain": ratio(total / 12),
            "observed_cpu_seconds": ratio(observed_cpu),
            "cpu_normalized_gain": ratio(total / observed_cpu) if observed_cpu else None,
            "timeout_count": arm_statuses[arm].count("TIMEOUT"),
            "timeout_rate_all_selected": ratio(Fraction(arm_statuses[arm].count("TIMEOUT"), 12)),
            "protocol_invalid_count": arm_statuses[arm].count("PROTOCOL_INVALID"),
            "protocol_invalid_rate_all_selected": ratio(Fraction(arm_statuses[arm].count("PROTOCOL_INVALID"), 12)),
        }

    def forecast_score(name: str) -> dict[str, str]:
        method = mean([brier(cluster[f"{name}_forecast"], cluster["terminal_outcome"]) for cluster in clusters])
        baseline = mean([brier(prior, cluster["terminal_outcome"]) for cluster in clusters])
        if baseline == 0:
            raise ScoreError("BRIER", "development-prior Brier is zero")
        return {"n": 12, "method_brier": ratio(method), "prior_brier": ratio(baseline), "brier_skill": ratio(1 - method / baseline)}

    forecasts = {name: forecast_score(name) for name in ("selection", "intervention")}
    wall_mean = Fraction(arms["WALL_NAVIGATION"]["mean_normalized_gain"])
    pair_gate = all(item["wins"] >= item["losses"] for item in paired.values())
    gates = {
        "selection_brier_skill_positive": Fraction(forecasts["selection"]["brier_skill"]) > 0,
        "intervention_brier_skill_positive": Fraction(forecasts["intervention"]["brier_skill"]) > 0,
        "wall_mean_gain_beats_catalogue": wall_mean > Fraction(arms["CATALOGUE"]["mean_normalized_gain"]),
        "wall_mean_gain_beats_generic": wall_mean > Fraction(arms["GENERIC"]["mean_normalized_gain"]),
        "paired_wins_at_least_losses_both": pair_gate,
        "controlling_term_full_denominator_accuracy_at_least_70_percent": Fraction(sign_correct, 12) >= Fraction(7, 10),
    }
    predictive = all(gates.values())
    advantaged = [cluster for cluster in certified if Fraction(cluster["intervention_forecast"]["CROSS"]) > Fraction(cluster["intervention_forecast"]["ZERO_COMPLETE"])]
    discovery = predictive and bool(advantaged)
    terminal_counts = {outcome: sum(cluster["terminal_outcome"] == outcome for cluster in clusters) for outcome in OUTCOMES}

    return {
        "schema_version": RESULT_VERSION,
        "benchmark_id": manifest["benchmark_id"],
        "input_sha256": file_digest(manifest_path),
        "scoring_rule_sha256": manifest["scoring_rule"]["sha256"],
        "selection_evidence_sha256": manifest["selection_replay"]["evidence"]["sha256"],
        "selected_n": 12,
        "aggregate_denominator": "ALL_SELECTED",
        "runnable_n": sum(cluster["runnable"] for cluster in clusters),
        "structural_zeros": structural_reasons,
        "forecast_scores": forecasts,
        "arms": arms,
        "paired": paired,
        "controlling_term_sign": {
            "correct": sign_correct, "incorrect": sign_incorrect,
            "non_evaluable": sign_nonevaluable, "n": 12,
            "full_denominator_accuracy": ratio(Fraction(sign_correct, 12)),
        },
        "terminal_outcomes": {
            "counts": terminal_counts,
            "timeout_rate": ratio(Fraction(terminal_counts["TIMEOUT"], 12)),
            "protocol_invalid_rate": ratio(Fraction(terminal_counts["PROTOCOL_INVALID"], 12)),
        },
        "theorem_yield": {"total": ratio(sum(theorem_values, Fraction())), "mean_all_selected": ratio(sum(theorem_values, Fraction()) / 12)},
        "crossings": {"independently_certified": len(certified), "forecast_advantaged": len(advantaged), "by_class": crossing_classes},
        "support": {
            "PREDICTIVE_SUPPORT": predictive,
            "DISCOVERY_SUPPORT": discovery,
            "gates": {**gates, "independently_certified_forecast_advantaged_crossing": bool(advantaged)},
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = score_manifest(args.manifest)
    except (OSError, ScoreError) as exc:
        code = exc.code if isinstance(exc, ScoreError) else "INPUT"
        print(json.dumps({"error": code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
