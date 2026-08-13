#!/usr/bin/env python3
"""Validate Method v1 resolution-card sidecars and their JSONL ledgers.

Legacy contracts remain historical evidence. Strict validation is activated only
by ``schema_version == c5k4-resolution-card-1.0``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - environment/setup failure
    raise SystemExit("jsonschema is required: python3 -m pip install jsonschema") from exc


SCHEMA_VERSION = "c5k4-resolution-card-1.0"
SCHEMA = Path(__file__).parents[1] / "schemas" / "resolution-card-v1.schema.json"
SHA_KEYS = ("carrier_sha256", "artifact_sha256")
REQUIRED_SIGN_ROLES = {"PREMISE_MARGIN", "TARGET_RESIDUAL", "CERTIFICATE_COST"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_root(path: Path) -> Path:
    for parent in (path.parent, *path.parents):
        if (parent / ".git").exists():
            return parent
    return path.parent


def resolve_path(card_path: Path, recorded: str) -> Path:
    candidate = Path(recorded)
    if candidate.is_absolute():
        return candidate
    rooted = repo_root(card_path) / candidate
    if rooted.exists():
        return rooted
    return card_path.parent / candidate


def schema_findings(card: dict[str, Any]) -> list[Finding]:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    findings = []
    for error in sorted(validator.iter_errors(card), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        findings.append(Finding("error", "SCHEMA", location, error.message))
    return findings


def semantic_findings(card: dict[str, Any], card_path: Path) -> list[Finding]:
    findings: list[Finding] = []

    def error(code: str, path: str, message: str) -> None:
        findings.append(Finding("error", code, path, message))

    contract = resolve_path(card_path, card["contract"]["path"])
    if not contract.is_file():
        error("CONTRACT_MISSING", "contract.path", f"contract does not exist: {contract}")
    elif sha256_file(contract).lower() != card["contract"]["sha256"].lower():
        error("CONTRACT_DIGEST", "contract.sha256", "contract SHA-256 mismatch")

    resolution = card["resolution_card"]
    trial = card["trial"]
    logical_class = resolution["logical_class"]
    lane = trial["lane"]
    run = trial["authorization"] == "RUN"
    finite = resolution["finite_witness_suffices"]

    if logical_class == "FINITE_UNIVERSAL":
        if not finite:
            error("LOGICAL_CLASS", "resolution_card.finite_witness_suffices",
                  "FINITE_UNIVERSAL requires a finite witness")
    elif finite:
        error("LOGICAL_CLASS", "resolution_card.finite_witness_suffices",
              f"{logical_class} cannot be resolved negatively by one finite witness")

    allowed_run_lanes = {
        "FINITE_UNIVERSAL": {"COUNTEREXAMPLE", "SYMBOLIC_PROOF"},
        "ASYMPTOTIC_UNIFORM": {"SYMBOLIC_PROOF"},
        "EXISTENTIAL": {"CONSTRUCTION", "SYMBOLIC_PROOF"},
        "FIXED_OPTIMUM_OR_ANSWER": {"FIXED_VALUE", "SYMBOLIC_PROOF"},
    }
    if run and lane not in allowed_run_lanes[logical_class]:
        error("LANE_MISMATCH", "trial.lane",
              f"{logical_class} cannot run in lane {lane}")
    if run and lane == "COUNTEREXAMPLE" and not resolution["exact_residual"]["available"]:
        error("RESIDUAL_REQUIRED", "resolution_card.exact_residual",
              "a runnable counterexample trial requires an exact residual bridge")

    carrier = trial["carrier_identity"]
    if run and carrier["kind"] == "NOT_APPLICABLE":
        error("CARRIER_REQUIRED", "trial.carrier_identity",
              "a runnable trial requires a hashed carrier or constructor")
    if carrier["kind"] == "LABELLED_OBJECT_WITH_ROLES" and "role" not in carrier["canonicalization"].lower():
        error("LABELLED_CARRIER", "trial.carrier_identity.canonicalization",
              "labelled carrier canonicalization must include the role map")

    process_cap = trial["process_wall_cap_seconds"]
    solver_cap = trial.get("solver_cap_seconds")
    if solver_cap is not None and solver_cap > process_cap:
        error("CAP_ORDER", "trial.solver_cap_seconds",
              "solver cap cannot exceed the process wall-clock cap")

    if trial["evidence_split"] != card["ledger"]["evidence_split"]:
        error("SPLIT_MISMATCH", "ledger.evidence_split",
              "trial and ledger evidence splits differ")
    for index, prerequisite in enumerate(card["ledger"]["prerequisites"]):
        prerequisite_path = resolve_path(card_path, prerequisite["path"])
        location = f"ledger.prerequisites.{index}"
        if not prerequisite_path.is_file():
            error("PREREQUISITE_MISSING", location,
                  f"prerequisite ledger does not exist: {prerequisite_path}")
        elif sha256_file(prerequisite_path).lower() != prerequisite["sha256"].lower():
            error("PREREQUISITE_DIGEST", f"{location}.sha256",
                  "prerequisite ledger SHA-256 mismatch")
    if trial["evidence_split"] == "HELDOUT" and "preregistered_commit" not in trial:
        error("HELDOUT_FREEZE", "trial.preregistered_commit",
              "held-out work requires a preregistration commit")

    rows = trial["sign_potential"]
    ids = [row["term_id"] for row in rows]
    if len(ids) != len(set(ids)):
        error("DUPLICATE_TERM", "trial.sign_potential", "term_id values must be unique")
    roles = [row["role"] for row in rows]
    if run:
        for role in sorted(REQUIRED_SIGN_ROLES):
            count = roles.count(role)
            if count != 1:
                error("SIGN_ROLE", "trial.sign_potential",
                      f"runnable trial requires exactly one {role} row; found {count}")

    baseline_ids = [row["baseline_id"] for row in trial["theorem_baselines"]]
    if len(baseline_ids) != len(set(baseline_ids)):
        error("DUPLICATE_BASELINE", "trial.theorem_baselines",
              "baseline_id values must be unique")
    sign_baselines = {row["term_id"] for row in rows if row["role"] == "THEOREM_BASELINE"}
    if set(baseline_ids) != sign_baselines:
        error("BASELINE_SIGN_TABLE", "trial.sign_potential",
              "theorem baseline IDs must exactly match THEOREM_BASELINE term IDs")

    return findings


def _row_label(row: dict[str, Any]) -> str:
    return str(row.get("kind", row.get("event", ""))).lower()


def _is_evaluated_row(row: dict[str, Any]) -> bool:
    label = _row_label(row)
    return any(token in label for token in ("candidate", "evaluat", "microfixture", "control", "graph"))


def ledger_findings(
    card: dict[str, Any], card_path: Path, ledger_path: Path
) -> list[Finding]:
    findings: list[Finding] = []
    expected_contract = card["contract"]["sha256"].lower()
    expected_card = sha256_file(card_path).lower()
    expected_split = card["ledger"]["evidence_split"]
    cap = card["trial"]["process_wall_cap_seconds"]

    if not ledger_path.is_file():
        return [Finding("error", "LEDGER_MISSING", "ledger.path",
                        f"ledger does not exist: {ledger_path}")]

    for number, raw in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        location = f"{ledger_path}:{number}"
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            findings.append(Finding("error", "LEDGER_JSON", location, str(exc)))
            continue
        if not isinstance(row, dict):
            findings.append(Finding("error", "LEDGER_ROW", location, "row must be an object"))
            continue

        if str(row.get("contract_sha256", "")).lower() != expected_contract:
            findings.append(Finding("error", "LEDGER_CONTRACT", location,
                                    "missing or mismatched contract_sha256"))
        if str(row.get("resolution_card_sha256", "")).lower() != expected_card:
            findings.append(Finding("error", "LEDGER_CARD", location,
                                    "missing or mismatched resolution_card_sha256"))
        if row.get("evidence_split") != expected_split:
            findings.append(Finding("error", "LEDGER_SPLIT", location,
                                    "row evidence_split differs from its ledger"))

        wall = row.get("wall_seconds")
        if not isinstance(wall, (int, float)) or isinstance(wall, bool) or wall < 0:
            findings.append(Finding("error", "LEDGER_DURATION", location,
                                    "wall_seconds must be a nonnegative number"))
        elif wall > cap:
            findings.append(Finding("error", "CAP_EXCEEDED", location,
                                    f"wall_seconds {wall} exceeds cap {cap}"))

        if _is_evaluated_row(row) and not any(row.get(key) for key in SHA_KEYS):
            findings.append(Finding("error", "ARTIFACT_DIGEST", location,
                                    "evaluated row lacks carrier_sha256 or artifact_sha256"))

        if "timeout" in _row_label(row):
            status_text = " ".join(
                str(row.get(key, "")) for key in ("status", "verdict", "outcome")
            ).upper()
            forbidden = bool(row.get("crossing") is True or row.get("absence") is True
                             or row.get("exact_optimum") is not None
                             or "CROSSING_VERIFIED" in status_text
                             or "NEW_UNAMBIGUOUS_DISPROOF" in status_text)
            if forbidden:
                findings.append(Finding("error", "TIMEOUT_CLAIM", location,
                                        "timeout row makes an exact absence/optimum/crossing claim"))

    return findings


def lint_card(card_path: Path, ledger_override: Path | None = None) -> list[Finding]:
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [Finding("error", "INPUT", str(card_path), str(exc))]
    if not isinstance(card, dict):
        return [Finding("error", "INPUT", str(card_path), "card must be a JSON object")]
    if card.get("schema_version") != SCHEMA_VERSION:
        return [Finding("warning", "LEGACY_SKIPPED", str(card_path),
                        "strict Method v1 validation does not apply")]

    findings = schema_findings(card)
    if findings:
        return findings
    findings.extend(semantic_findings(card, card_path))

    ledger = ledger_override
    if ledger is None:
        recorded = resolve_path(card_path, card["ledger"]["path"])
        if recorded.exists():
            ledger = recorded
    if ledger is not None:
        findings.extend(ledger_findings(card, card_path, ledger))
    return findings


def find_cards(root: Path) -> Iterable[Path]:
    yield from sorted(root.glob("results/expansion/*_resolution_card.json"))


def legacy_findings(root: Path) -> list[Finding]:
    findings = []
    for pattern in ("*_contract.md", "*_contract.json"):
        for contract in sorted((root / "results" / "expansion").glob(pattern)):
            sidecar = contract.with_name(contract.name.rsplit("_contract", 1)[0] + "_resolution_card.json")
            if not sidecar.exists():
                findings.append(Finding("warning", "LEGACY_NO_SIDECAR", str(contract),
                                        "legacy contract has no Method v1 resolution card"))
    return findings


def print_findings(findings: list[Finding], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps([asdict(item) for item in findings], indent=2, sort_keys=True))
        return
    for item in findings:
        print(f"{item.severity.upper()} {item.code} {item.path}: {item.message}")
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    print(f"resolution-card lint: {errors} error(s), {warnings} warning(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", nargs="?", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--check-repo", action="store_true")
    parser.add_argument("--legacy-report", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    if bool(args.card) == bool(args.check_repo):
        parser.error("provide exactly one CARD or --check-repo")
    if args.ledger and args.check_repo:
        parser.error("--ledger is valid only with one CARD")

    findings: list[Finding] = []
    if args.card:
        findings.extend(lint_card(args.card.resolve(), args.ledger.resolve() if args.ledger else None))
    else:
        root = Path(__file__).parents[1]
        for card in find_cards(root):
            findings.extend(lint_card(card))
        if args.legacy_report:
            findings.extend(legacy_findings(root))
    print_findings(findings, args.format)

    if any(item.code == "INPUT" for item in findings):
        return 2
    integrity = {"CONTRACT_DIGEST", "PREREQUISITE_DIGEST", "LEDGER_CONTRACT",
                 "LEDGER_CARD", "LEDGER_SPLIT", "CAP_EXCEEDED", "TIMEOUT_CLAIM"}
    if any(item.severity == "error" and item.code in integrity for item in findings):
        return 3
    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
