#!/usr/bin/env python3
"""Derive Method v1.1 aggregate scores from a COMPLETE manifest and its ledgers.

The scorer deliberately accepts no hand-written aggregate fields.  It first
runs the benchmark linter, then reconstructs terminal evidence, objective
gains, CPU use, forecast scores, and support gates from hash-chained JSONL.
All score arithmetic is exact ``fractions.Fraction`` arithmetic.
"""

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
LINTER_PATH = HERE / "lint_benchmark_v11.py"
SPEC = importlib.util.spec_from_file_location("benchmark_v11_linter_for_score", LINTER_PATH)
assert SPEC is not None and SPEC.loader is not None
LINTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LINTER
SPEC.loader.exec_module(LINTER)

OUTCOMES = LINTER.OUTCOMES
ARMS = LINTER.ARMS
SCORE_VERSION = "c5k4-benchmark-score-1.1"


class ScoreError(ValueError):
    """A fail-closed scoring error carrying a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _fraction(value: Any, location: str, *, positive: bool = False) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (str, int)):
        raise ScoreError("RATIONAL", f"{location} must be an integer or rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ScoreError("RATIONAL", f"{location} is not a rational: {exc}") from exc
    if positive and result <= 0:
        raise ScoreError("RATIONAL", f"{location} must be positive")
    return result


def _ratio(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _mean(values: list[Fraction]) -> Fraction:
    if not values:
        raise ScoreError("EMPTY_METRIC", "cannot take the mean of an empty metric")
    return sum(values, Fraction(0)) / len(values)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_rows(manifest: dict[str, Any], manifest_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for reference in manifest["ledgers"]:
        ledger_path = LINTER.resolve_path(manifest_path, reference["path"])
        for line_number, raw in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            row["__location"] = f"{ledger_path}:{line_number}"
            rows.append(row)
    return rows


def _brier(probabilities: dict[str, str], actual: str) -> Fraction:
    return sum(
        (Fraction(probabilities[outcome]) - int(outcome == actual)) ** 2
        for outcome in OUTCOMES
    )


def _forecast_score(
    clusters: list[dict[str, Any]], forecast_name: str, prior: dict[str, str]
) -> dict[str, Any]:
    eligible = [cluster for cluster in clusters if cluster[forecast_name] is not None]
    method = [_brier(cluster[forecast_name]["probabilities"], cluster["terminal_outcome"]) for cluster in eligible]
    baseline = [_brier(prior, cluster["terminal_outcome"]) for cluster in eligible]
    method_mean = _mean(method)
    prior_mean = _mean(baseline)
    if prior_mean == 0:
        raise ScoreError("ZERO_PRIOR_BRIER", f"{forecast_name} has zero prior Brier score")
    return {
        "n": len(eligible),
        "method_brier": _ratio(method_mean),
        "prior_brier": _ratio(prior_mean),
        "brier_skill": _ratio(1 - method_mean / prior_mean),
    }


def _event(row: dict[str, Any]) -> dict[str, Any] | None:
    value = row.get("score_event")
    if value is None:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
        raise ScoreError("SCORE_EVENT", f"{row['__location']}.score_event must be an object with kind")
    return value


def _single(mapping: dict[Any, list[Any]], key: Any, description: str) -> Any:
    values = mapping.get(key, [])
    if len(values) != 1:
        raise ScoreError("TERMINAL_CARDINALITY", f"expected exactly one {description}; found {len(values)}")
    return values[0]


def _objective_gain(event: dict[str, Any], location: str) -> Fraction:
    status = event.get("status")
    if status not in ("COMPLETE", "TIMEOUT", "PROTOCOL_INVALID"):
        raise ScoreError("ARM_STATUS", f"{location}.status is invalid")
    objective = event.get("objective")
    if status != "COMPLETE":
        if objective is not None:
            raise ScoreError("ARM_OBJECTIVE", f"{location}.objective must be null unless status is COMPLETE")
        return Fraction(0)
    required = {"residual_orientation", "signed_residual", "frozen_control_residual"}
    if not isinstance(objective, dict) or set(objective) != required:
        raise ScoreError(
            "ARM_OBJECTIVE",
            f"{location}.objective must contain only residual_orientation/signed_residual/frozen_control_residual",
        )
    residual = _fraction(objective["signed_residual"], f"{location}.objective.signed_residual")
    control = _fraction(
        objective["frozen_control_residual"],
        f"{location}.objective.frozen_control_residual",
    )
    scale = max(Fraction(1), abs(control))
    if objective["residual_orientation"] == "SAFE_NONNEGATIVE":
        return max(Fraction(0), -residual) / scale
    if objective["residual_orientation"] == "SAFE_NONPOSITIVE":
        return max(Fraction(0), residual) / scale
    raise ScoreError("ARM_OBJECTIVE", f"{location}.objective.residual_orientation is invalid")


def _sign(value: Fraction) -> int:
    return (value > 0) - (value < 0)


def score_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    findings = LINTER.lint_manifest(manifest_path)
    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        first = errors[0]
        raise ScoreError("LINTER_FAILED", f"{first.code} {first.path}: {first.message} ({len(errors)} error(s))")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clusters = manifest["clusters"]
    if manifest["phase"] != "COMPLETE" or len(clusters) != 12:
        raise ScoreError("INCOMPLETE_BENCHMARK", "scoring requires a COMPLETE twelve-cluster manifest")
    if not manifest["ledgers"]:
        raise ScoreError("MISSING_LEDGERS", "scoring requires at least one content-addressed ledger")

    rows = _load_rows(manifest, manifest_path)
    arm_terminal: dict[tuple[str, str], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    cluster_terminal: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    verification: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    cpu_by_arm: dict[tuple[str, str], Fraction] = defaultdict(Fraction)

    cluster_ids = {cluster["cluster_id"] for cluster in clusters}
    for row in rows:
        unit = row["unit_id"]
        arm = row["arm"]
        if unit in cluster_ids and arm in ARMS:
            cpu_by_arm[(unit, arm)] += _fraction(row["cpu_seconds"], f"{row['__location']}.cpu_seconds")
        event = _event(row)
        if event is None:
            continue
        kind = event["kind"]
        if kind == "ARM_TERMINAL":
            if set(event) != {"kind", "status", "objective", "controlling_term"}:
                raise ScoreError("SCORE_EVENT_FIELDS", f"{row['__location']} ARM_TERMINAL has unexpected/missing fields")
            if arm not in ARMS:
                raise ScoreError("SCORE_EVENT_ARM", f"{row['__location']} ARM_TERMINAL must use a discovery arm")
            arm_terminal[(unit, arm)].append((row, event))
        elif kind == "CLUSTER_TERMINAL":
            required = {
                "kind", "terminal_outcome", "theorem_yield", "theorem_evidence",
                "theorem_evidence_sha256", "independent_countermodel_check",
                "crossing_candidate_sha256", "crossing_class",
            }
            if set(event) != required:
                raise ScoreError("SCORE_EVENT_FIELDS", f"{row['__location']} CLUSTER_TERMINAL has unexpected/missing fields")
            if arm != "SHARED_ANALYSIS":
                raise ScoreError("SCORE_EVENT_ARM", f"{row['__location']} CLUSTER_TERMINAL must use SHARED_ANALYSIS")
            cluster_terminal[unit].append((row, event))
        elif kind == "INDEPENDENT_VERIFICATION_TERMINAL":
            if set(event) != {"kind", "candidate_sha256", "result"}:
                raise ScoreError("SCORE_EVENT_FIELDS", f"{row['__location']} verification has unexpected/missing fields")
            if arm != "INDEPENDENT_VERIFICATION":
                raise ScoreError("SCORE_EVENT_ARM", f"{row['__location']} verification must use INDEPENDENT_VERIFICATION")
            verification[unit].append((row, event))
        else:
            raise ScoreError("SCORE_EVENT_KIND", f"{row['__location']} has unknown score event {kind!r}")

    gains: dict[str, list[Fraction]] = {arm: [] for arm in ARMS}
    statuses: dict[str, list[str]] = {arm: [] for arm in ARMS}
    cpu: dict[str, Fraction] = {arm: Fraction(0) for arm in ARMS}
    per_unit_gain: dict[tuple[str, str], Fraction] = {}
    sign_correct = 0
    sign_evaluable = 0
    sign_total = 0
    theorem_values: list[Fraction] = []
    theorem_kinds = {"PROVED": 0, "SIGNAL": 0, "RETROSPECTIVE": 0, "NONE": 0}
    crossing_classes = {"NOVEL": 0, "RETRO": 0, "AMBIGUOUS": 0, "STATUS_PREEMPTED": 0}
    certified_crossings: list[dict[str, Any]] = []

    for cluster in clusters:
        unit = cluster["cluster_id"]
        _, terminal = _single(cluster_terminal, unit, f"CLUSTER_TERMINAL for {unit}")
        if terminal.get("terminal_outcome") != cluster["terminal_outcome"]:
            raise ScoreError("TERMINAL_MISMATCH", f"{unit} ledger and manifest terminal outcomes differ")

        theorem_yield = _fraction(terminal.get("theorem_yield"), f"{unit}.theorem_yield")
        theorem_kind = terminal.get("theorem_evidence")
        theorem_digest = terminal.get("theorem_evidence_sha256")
        countermodel = terminal.get("independent_countermodel_check")
        if theorem_yield not in (Fraction(0), Fraction(1, 2), Fraction(1)):
            raise ScoreError("THEOREM_YIELD", f"{unit} theorem_yield must be 0, 1/2, or 1")
        expected = {Fraction(0): {"NONE", "RETROSPECTIVE"}, Fraction(1, 2): {"SIGNAL"}, Fraction(1): {"PROVED"}}
        if theorem_kind not in expected[theorem_yield]:
            raise ScoreError("THEOREM_EVIDENCE", f"{unit} theorem evidence does not justify its yield")
        if theorem_yield == Fraction(1, 2) and countermodel is not True:
            raise ScoreError("THEOREM_EVIDENCE", f"{unit} theorem signal lacks an independent countermodel check")
        if theorem_yield > 0:
            if not isinstance(theorem_digest, str) or len(theorem_digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in theorem_digest):
                raise ScoreError("THEOREM_EVIDENCE", f"{unit} positive theorem yield lacks an evidence SHA-256")
        elif theorem_digest is not None:
            raise ScoreError("THEOREM_EVIDENCE", f"{unit} zero theorem yield must have null evidence SHA-256")
        if not isinstance(countermodel, bool):
            raise ScoreError("THEOREM_EVIDENCE", f"{unit} independent_countermodel_check must be boolean")
        if cluster["terminal_outcome"] == "THEOREM_STRUCTURE" and theorem_yield == 0:
            raise ScoreError("THEOREM_EVIDENCE", f"{unit} THEOREM_STRUCTURE has zero theorem yield")
        theorem_values.append(theorem_yield)
        theorem_kinds[theorem_kind] += 1

        candidate = terminal.get("crossing_candidate_sha256")
        crossing_class = terminal.get("crossing_class")
        if cluster["terminal_outcome"] == "CROSS":
            if not isinstance(candidate, str) or len(candidate) != 64 or any(c not in "0123456789abcdefABCDEF" for c in candidate):
                raise ScoreError("CROSSING_EVIDENCE", f"{unit} CROSS lacks a candidate SHA-256")
            checks = verification.get(unit, [])
            good = [
                row for row, event in checks
                if event.get("candidate_sha256", "").lower() == candidate.lower()
                and event.get("result") == "VERIFIED"
                and row["carrier_sha256"].lower() == candidate.lower()
            ]
            if len(checks) != 2 or len({str(row["process_id"]) for row in good}) != 2 or len(good) != 2:
                raise ScoreError("CROSSING_EVIDENCE", f"{unit} CROSS requires exactly two independent VERIFIED rows")
            if crossing_class not in crossing_classes:
                raise ScoreError("CROSSING_EVIDENCE", f"{unit} CROSS has invalid crossing_class")
            crossing_classes[crossing_class] += 1
            certified_crossings.append(cluster)
        elif candidate is not None or crossing_class != "NONE":
            raise ScoreError("CROSSING_EVIDENCE", f"{unit} non-CROSS terminal must have null candidate and NONE class")
        elif verification.get(unit):
            raise ScoreError("CROSSING_EVIDENCE", f"{unit} non-CROSS terminal has extraneous verification rows")

        if cluster["runnable"] is True:
            if any(cluster["arms"][arm]["status"] != "TERMINATED" for arm in ARMS):
                raise ScoreError("ARM_NOT_TERMINATED", f"{unit} has a non-terminated frozen arm")
            unit_statuses: dict[str, str] = {}
            for arm in ARMS:
                row, event = _single(arm_terminal, (unit, arm), f"ARM_TERMINAL for {unit}/{arm}")
                gain = _objective_gain(event, f"{row['__location']}.score_event")
                status = event["status"]
                gains[arm].append(gain)
                statuses[arm].append(status)
                cpu[arm] += cpu_by_arm[(unit, arm)]
                per_unit_gain[(unit, arm)] = gain
                unit_statuses[arm] = status
                controlling = event.get("controlling_term")
                if arm == "WALL_NAVIGATION":
                    sign_total += 1
                    if status == "COMPLETE":
                        if not isinstance(controlling, dict) or set(controlling) != {"forecast_sign", "observed_delta"}:
                            raise ScoreError("CONTROLLING_TERM", f"{unit} wall terminal lacks controlling-term evidence")
                        forecast_sign = controlling["forecast_sign"]
                        if isinstance(forecast_sign, bool) or forecast_sign not in (-1, 1):
                            raise ScoreError(
                                "CONTROLLING_TERM",
                                f"{unit} forecast_sign must be a preregistered nonzero direction",
                            )
                        observed = _fraction(controlling["observed_delta"], f"{unit}.observed_delta")
                        sign_evaluable += 1
                        sign_correct += int(forecast_sign == _sign(observed))
                    elif controlling is not None:
                        raise ScoreError("CONTROLLING_TERM", f"{unit} incomplete wall arm must have null controlling_term")
                elif controlling is not None:
                    raise ScoreError("CONTROLLING_TERM", f"{unit}/{arm} baseline must have null controlling_term")
            if cluster["terminal_outcome"] == "ZERO_COMPLETE" and set(unit_statuses.values()) != {"COMPLETE"}:
                raise ScoreError("TERMINAL_EVIDENCE", f"{unit} ZERO_COMPLETE requires three completed arms")
            if cluster["terminal_outcome"] == "TIMEOUT" and "TIMEOUT" not in unit_statuses.values():
                raise ScoreError("TERMINAL_EVIDENCE", f"{unit} TIMEOUT lacks a timed-out arm")
            if cluster["terminal_outcome"] == "PROTOCOL_INVALID" and "PROTOCOL_INVALID" not in unit_statuses.values():
                raise ScoreError("TERMINAL_EVIDENCE", f"{unit} PROTOCOL_INVALID lacks an invalid arm")
        else:
            if any((unit, arm) in arm_terminal for arm in ARMS):
                raise ScoreError("NONRUNNABLE_ARM", f"{unit} has arm terminal rows despite being nonrunnable")
            if cluster["terminal_outcome"] not in ("PRESEARCH_STOP", "THEOREM_STRUCTURE", "PROTOCOL_INVALID"):
                raise ScoreError("TERMINAL_EVIDENCE", f"{unit} nonrunnable terminal outcome is inconsistent")

    runnable_n = sum(cluster["runnable"] is True for cluster in clusters)
    if runnable_n == 0:
        raise ScoreError("NO_RUNNABLE_UNITS", "arm comparison requires at least one runnable unit")

    arm_result: dict[str, Any] = {}
    for arm in ARMS:
        total_gain = sum(gains[arm], Fraction(0))
        arm_cpu = cpu[arm]
        if total_gain > 0 and arm_cpu <= 0:
            raise ScoreError("CPU_EVIDENCE", f"{arm} has positive gain but no observed CPU time")
        arm_result[arm] = {
            "n": len(gains[arm]),
            "mean_normalized_gain": _ratio(total_gain / len(gains[arm])),
            "total_normalized_gain": _ratio(total_gain),
            "total_cpu_seconds": _ratio(arm_cpu),
            "cpu_normalized_gain": (
                "0" if total_gain == 0 else _ratio(total_gain / arm_cpu)
            ),
            "timeouts": statuses[arm].count("TIMEOUT"),
            "timeout_rate": _ratio(Fraction(statuses[arm].count("TIMEOUT"), len(statuses[arm]))),
            "protocol_invalid": statuses[arm].count("PROTOCOL_INVALID"),
            "protocol_invalid_rate": _ratio(Fraction(statuses[arm].count("PROTOCOL_INVALID"), len(statuses[arm]))),
        }

    paired: dict[str, Any] = {}
    for baseline in ("CATALOGUE", "GENERIC"):
        comparisons = [
            per_unit_gain[(cluster["cluster_id"], "WALL_NAVIGATION")]
            - per_unit_gain[(cluster["cluster_id"], baseline)]
            for cluster in clusters if cluster["runnable"] is True
        ]
        paired[f"WALL_NAVIGATION_vs_{baseline}"] = {
            "wins": sum(delta > 0 for delta in comparisons),
            "losses": sum(delta < 0 for delta in comparisons),
            "ties": sum(delta == 0 for delta in comparisons),
        }

    if any(cluster["intervention_forecast"] is None for cluster in clusters):
        raise ScoreError(
            "MISSING_INTERVENTION_FORECAST",
            "COMPLETE scoring requires both frozen forecasts for all twelve clusters",
        )
    prior = manifest["freeze_artifacts"]["development_prior"]["probabilities"]
    selection_score = _forecast_score(clusters, "selection_forecast", prior)
    intervention_score = _forecast_score(clusters, "intervention_forecast", prior)
    selection_positive = Fraction(selection_score["brier_skill"]) > 0
    intervention_positive = Fraction(intervention_score["brier_skill"]) > 0
    wall_mean = Fraction(arm_result["WALL_NAVIGATION"]["mean_normalized_gain"])
    beats_catalogue = wall_mean > Fraction(arm_result["CATALOGUE"]["mean_normalized_gain"])
    beats_generic = wall_mean > Fraction(arm_result["GENERIC"]["mean_normalized_gain"])
    paired_catalogue = paired["WALL_NAVIGATION_vs_CATALOGUE"]
    paired_generic = paired["WALL_NAVIGATION_vs_GENERIC"]
    paired_gate = (
        paired_catalogue["wins"] >= paired_catalogue["losses"]
        and paired_generic["wins"] >= paired_generic["losses"]
    )
    sign_accuracy = Fraction(sign_correct, sign_evaluable) if sign_evaluable else None
    sign_gate = sign_accuracy is not None and sign_accuracy >= Fraction(7, 10)
    predictive = all((selection_positive, intervention_positive, beats_catalogue, beats_generic, paired_gate, sign_gate))

    forecast_advantaged = [
        cluster for cluster in certified_crossings
        if Fraction(cluster["intervention_forecast"]["probabilities"]["CROSS"])
        > Fraction(cluster["intervention_forecast"]["probabilities"]["ZERO_COMPLETE"])
    ]
    discovery = predictive and bool(forecast_advantaged)

    return {
        "schema_version": SCORE_VERSION,
        "benchmark_id": manifest["benchmark_id"],
        "manifest_sha256": _sha256_file(manifest_path),
        "cluster_count": len(clusters),
        "runnable_cluster_count": runnable_n,
        "forecast_scores": {
            "selection": selection_score,
            "intervention": intervention_score,
        },
        "arms": arm_result,
        "paired": paired,
        "controlling_term_sign": {
            "correct": sign_correct,
            "evaluable": sign_evaluable,
            "total_runnable": sign_total,
            "accuracy": _ratio(sign_accuracy) if sign_accuracy is not None else None,
        },
        "theorem_yield": {
            "total": _ratio(sum(theorem_values, Fraction(0))),
            "mean": _ratio(_mean(theorem_values)),
            "proved": theorem_kinds["PROVED"],
            "signals": theorem_kinds["SIGNAL"],
            "retrospective": theorem_kinds["RETROSPECTIVE"],
        },
        "crossings": {
            "independently_certified": len(certified_crossings),
            "forecast_advantaged": len(forecast_advantaged),
            "by_class": crossing_classes,
        },
        "support": {
            "PREDICTIVE_SUPPORT": predictive,
            "DISCOVERY_SUPPORT": discovery,
            "gates": {
                "selection_brier_skill_positive": selection_positive,
                "intervention_brier_skill_positive": intervention_positive,
                "wall_mean_gain_beats_catalogue": beats_catalogue,
                "wall_mean_gain_beats_generic": beats_generic,
                "paired_wins_at_least_losses_both": paired_gate,
                "controlling_term_sign_accuracy_at_least_70_percent": sign_gate,
                "independently_certified_forecast_advantaged_crossing": bool(forecast_advantaged),
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, help="write canonical pretty JSON instead of stdout")
    args = parser.parse_args(argv)
    try:
        result = score_manifest(args.manifest)
    except (OSError, json.JSONDecodeError, ScoreError) as exc:
        code = exc.code if isinstance(exc, ScoreError) else "INPUT"
        print(json.dumps({"error": code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
