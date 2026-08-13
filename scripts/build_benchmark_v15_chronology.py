#!/usr/bin/env python3
"""Capture and validate Method v1.5 P1/U1/U2 chronology receipts.

The two capture commands are intentionally one-shot.  Each performs one
direct, atomic fetch of canonical upstream ``main`` into a fresh isolated bare
repository.  They contain no retry, fallback-ref, or repinning path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

import build_benchmark_v15_aggregate_certificate as aggregate


ROOT = Path(__file__).parents[1].resolve()
CHRONOLOGY_RULE = ROOT / "results/benchmark/v1.5-protocol/chronology-rule.json"
UPSTREAM_REPOSITORY = "https://github.com/google-deepmind/formal-conjectures.git"
UPSTREAM_REF = "refs/heads/main"
PROTOCOL_PUBLIC_REPOSITORY = "https://github.com/Kuberwastaken/c5-k4.git"
PROTOCOL_PUBLIC_REF = "refs/heads/main"
CHECKPOINT_HOUR = 0
CHECKPOINT_MINUTE = 17
CHECKPOINT_START_DEADLINE_HOUR = 6
LAST_CHECKPOINT = "2027-08-15T00:17:00Z"
LAST_CHECKPOINT_DEADLINE = "2027-08-15T06:00:00Z"
SCHEMA = "c5k4-method-v1.5-chronology-receipt-1.0"
OID_RE = re.compile(r"^[0-9a-f]{40}$")
SAFE_ENV = {
    **os.environ,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_ASKPASS": "/bin/false",
    "GIT_SSH_COMMAND": "ssh -oBatchMode=yes",
}
SAFE_CONFIG = (
    "-c", "core.hooksPath=/dev/null",
    "-c", "protocol.file.allow=never",
    "-c", "credential.helper=",
)


class ChronologyError(ValueError):
    """A frozen chronology invariant failed."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _now() -> datetime:
    return datetime.now(timezone.utc)


def format_time(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ChronologyError("timestamp must be timezone-aware UTC")
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ChronologyError(f"{label} must be an RFC3339 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ChronologyError(f"invalid {label}: {value!r}") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ChronologyError(f"{label} must be UTC")
    return parsed


def exact_oid(value: Any, label: str) -> str:
    if not isinstance(value, str) or OID_RE.fullmatch(value) is None:
        raise ChronologyError(f"{label} must be an exact lowercase SHA-1 object ID")
    return value


def repo_relative(path: Path, label: str) -> str:
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise ChronologyError(f"{label} must be inside the repository") from exc
    pure = PurePosixPath(relative)
    if not pure.parts or ".." in pure.parts:
        raise ChronologyError(f"{label} is not a normalized repository-relative path")
    return relative


def _run(command: Sequence[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            list(command), cwd=cwd, env=SAFE_ENV, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", "replace").strip()
        raise ChronologyError(f"command failed without retry: {list(command)!r}: {stderr}") from exc


def local_git(*args: str) -> bytes:
    return _run(("/usr/bin/git", *SAFE_CONFIG, "-C", str(ROOT), *args)).stdout


def commit_file(commit: str, path: str) -> bytes:
    exact_oid(commit, "commit")
    try:
        return local_git("show", f"{commit}:{path}")
    except ChronologyError as exc:
        raise ChronologyError(f"committed path {path!r} is unavailable at {commit}") from exc


def load_rule() -> tuple[dict[str, Any], str]:
    raw = CHRONOLOGY_RULE.read_bytes()
    try:
        rule = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ChronologyError("frozen chronology rule is invalid JSON") from exc
    if rule.get("schema") != "c5k4-method-v1.5-chronology-rule-1.0":
        raise ChronologyError("unsupported chronology rule")
    horizon = rule.get("fixed_horizon", {})
    schedule = rule.get("checkpoint_schedule", {})
    if (
        horizon.get("last_scheduled_checkpoint_utc") != LAST_CHECKPOINT
        or horizon.get("capture_start_deadline_utc") != LAST_CHECKPOINT_DEADLINE
        or schedule.get("cron") != "17 0 * * *"
        or schedule.get("timezone") != "UTC"
        or schedule.get("valid_start_before_utc_time") != "06:00:00"
        or schedule.get("allowed_event") != "schedule"
        or schedule.get("manual_dispatch_is_checkpoint") is not False
        or schedule.get("rerun_is_checkpoint") is not False
    ):
        raise ChronologyError("chronology implementation and frozen checkpoint schedule differ")
    return rule, sha256_bytes(raw)


def validate_p1t(artifact_path: Path, p1t_commit: str) -> dict[str, Any]:
    """Enforce the P1A -> P1T direct, one-path attestation boundary."""
    p1t_commit = exact_oid(p1t_commit, "P1T commit")
    relative = repo_relative(artifact_path, "P1T artifact")
    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChronologyError("P1T artifact is not valid UTF-8 JSON") from exc
    if artifact.get("artifact_kind") != "P1T" or artifact.get("protocol_version") != "1.5":
        raise ChronologyError("expected a Method v1.5 P1T artifact")
    p1a_commit = exact_oid(artifact.get("p1a_commit"), "P1A commit")
    p1a = artifact.get("p1a")
    if not isinstance(p1a, dict) or set(p1a) != {"path", "sha256"}:
        raise ChronologyError("P1T p1a binding must contain exactly path and sha256")
    p1a_path = p1a.get("path")
    if not isinstance(p1a_path, str) or PurePosixPath(p1a_path).is_absolute() or ".." in PurePosixPath(p1a_path).parts:
        raise ChronologyError("P1A path must be normalized and repository-relative")
    p1a_sha = p1a.get("sha256")
    if not isinstance(p1a_sha, str) or re.fullmatch(r"[0-9a-f]{64}", p1a_sha) is None:
        raise ChronologyError("P1A digest must be an exact lowercase SHA-256")
    policy = artifact.get("attestation_policy")
    expected_policy = {
        "p1a_ancestor_required": True,
        "p1a_bytes_immutable": True,
        "allowed_p1t_changed_paths": [relative],
    }
    if policy != expected_policy:
        raise ChronologyError("P1T attestation policy/path differs from the frozen two-commit boundary")
    parse_time(artifact.get("p1a_published_at_utc"), "P1A publication time")

    resolved = local_git("rev-parse", p1t_commit).decode().strip()
    if resolved != p1t_commit:
        raise ChronologyError("P1T commit resolved through a ref or abbreviation")
    parents = local_git("show", "-s", "--format=%P", p1t_commit).decode().split()
    if parents != [p1a_commit]:
        raise ChronologyError("P1T must be a non-merge commit whose sole parent is exact P1A")
    changed = local_git("diff-tree", "--no-commit-id", "--name-only", "-r", p1t_commit).decode().splitlines()
    if changed != [relative]:
        raise ChronologyError(f"P1T changed paths {changed!r}, expected only {relative!r}")
    if commit_file(p1t_commit, relative) != artifact_path.read_bytes():
        raise ChronologyError("working P1T bytes differ from committed P1T bytes")
    p1a_raw = commit_file(p1a_commit, p1a_path)
    if sha256_bytes(p1a_raw) != p1a_sha:
        raise ChronologyError("P1T does not authenticate exact committed P1A bytes")
    return artifact


def verify_public_p1t(p1t_commit: str) -> dict[str, Any]:
    """Make the one public-receipt observation required before U1."""
    command = (
        "/usr/bin/git", *SAFE_CONFIG, "ls-remote", "--refs",
        PROTOCOL_PUBLIC_REPOSITORY, PROTOCOL_PUBLIC_REF,
    )
    started = _now()
    result = _run(command)
    completed = _now()
    lines = result.stdout.decode("utf-8", "strict").splitlines()
    expected = f"{p1t_commit}\t{PROTOCOL_PUBLIC_REF}"
    if lines != [expected]:
        raise ChronologyError("public main does not resolve exactly to P1T")
    return {
        "repository": PROTOCOL_PUBLIC_REPOSITORY,
        "ref": PROTOCOL_PUBLIC_REF,
        "command": list(command),
        "observed_tip": p1t_commit,
        "verification_started_at_utc": format_time(started),
        "verification_completed_at_utc": format_time(completed),
        "stdout_sha256": sha256_bytes(result.stdout),
        "stderr_sha256": sha256_bytes(result.stderr),
    }


def _bare_git(destination: Path, *args: str) -> bytes:
    return _run(("/usr/bin/git", *SAFE_CONFIG, "--git-dir", str(destination), *args)).stdout


def capture_upstream(destination: Path) -> dict[str, Any]:
    """Perform exactly one isolated atomic fetch of canonical upstream main."""
    if destination.exists():
        raise ChronologyError("capture destination must not already exist")
    destination.parent.mkdir(parents=True, exist_ok=True)
    init_command = ("/usr/bin/git", *SAFE_CONFIG, "init", "--bare", str(destination))
    _run(init_command)
    fetch_command = (
        "/usr/bin/git", *SAFE_CONFIG, "--git-dir", str(destination), "fetch",
        "--atomic", "--force", "--no-tags", "--no-write-fetch-head",
        UPSTREAM_REPOSITORY, f"+{UPSTREAM_REF}:{UPSTREAM_REF}",
    )
    started = _now()
    result = _run(fetch_command)
    completed = _now()

    refs = _bare_git(destination, "for-each-ref", "--format=%(refname)").decode().splitlines()
    if refs != [UPSTREAM_REF]:
        raise ChronologyError(f"isolated capture has unexpected refs: {refs!r}")
    if _bare_git(destination, "config", "--get-regexp", r"^remote\.").strip():
        raise ChronologyError("isolated capture must not configure a remote")
    if (destination / "shallow").exists() or (destination / "objects/info/alternates").exists():
        raise ChronologyError("shallow repositories and object alternates are forbidden")
    extensions = _bare_git(destination, "config", "--get-regexp", r"^(extensions\.|remote\..*\.promisor)").strip()
    if extensions:
        raise ChronologyError("promisor or repository extensions are forbidden")
    _bare_git(destination, "fsck", "--full", "--strict")
    commit = exact_oid(_bare_git(destination, "rev-parse", UPSTREAM_REF).decode().strip(), "upstream main commit")
    root_tree = exact_oid(_bare_git(destination, "rev-parse", f"{commit}^{{tree}}").decode().strip(), "upstream root tree")
    subtree = exact_oid(_bare_git(destination, "rev-parse", f"{commit}:FormalConjectures").decode().strip(), "FormalConjectures tree")
    if _bare_git(destination, "cat-file", "-t", commit).decode().strip() != "commit":
        raise ChronologyError("captured upstream tip is not a commit")
    if _bare_git(destination, "cat-file", "-t", subtree).decode().strip() != "tree":
        raise ChronologyError("captured FormalConjectures object is not a tree")
    return {
        "repository": UPSTREAM_REPOSITORY,
        "ref": UPSTREAM_REF,
        "init_command": list(init_command),
        "fetch_command": list(fetch_command),
        "fetch_count": 1,
        "retry_count": 0,
        "capture_started_at_utc": format_time(started),
        "capture_completed_at_utc": format_time(completed),
        "stdout_sha256": sha256_bytes(result.stdout),
        "stderr_sha256": sha256_bytes(result.stderr),
        "commit": commit,
        "root_tree": root_tree,
        "formal_conjectures_tree": subtree,
        "refs": refs,
        "bare": True,
        "shallow": False,
        "promisor": False,
        "alternates": False,
        "remote_count": 0,
        "connectivity_fsck": "PASS",
    }


def build_u1(p1t_path: Path, p1t_commit: str, destination: Path) -> dict[str, Any]:
    _, rule_sha = load_rule()
    p1t = validate_p1t(p1t_path, p1t_commit)
    public = verify_public_p1t(p1t_commit)
    upstream = capture_upstream(destination)
    if parse_time(public["verification_completed_at_utc"], "P1T public receipt") >= parse_time(
        upstream["capture_started_at_utc"], "U1 capture start"
    ):
        raise ChronologyError("U1 must start strictly after completed public P1T verification")
    if parse_time(p1t["p1a_published_at_utc"], "P1A publication") > parse_time(
        public["verification_started_at_utc"], "P1T verification start"
    ):
        raise ChronologyError("P1A publication cannot postdate P1T public verification")
    return {
        "schema": SCHEMA,
        "artifact_kind": "U1_CHRONOLOGY_RECEIPT",
        "protocol_version": "1.5",
        "chronology_rule": {
            "path": CHRONOLOGY_RULE.relative_to(ROOT).as_posix(),
            "sha256": rule_sha,
        },
        "p1": {
            "p1a_commit": p1t["p1a_commit"],
            "p1t_commit": p1t_commit,
            "p1t_artifact": {
                "path": repo_relative(p1t_path, "P1T artifact"),
                "sha256": sha256_file(p1t_path),
            },
            "public_receipt": public,
        },
        "upstream": upstream,
        "status": "VALID_U1",
    }


def validate_u1(receipt_path: Path) -> dict[str, Any]:
    try:
        value = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChronologyError("U1 receipt is not valid UTF-8 JSON") from exc
    _, rule_sha = load_rule()
    if value.get("schema") != SCHEMA or value.get("artifact_kind") != "U1_CHRONOLOGY_RECEIPT":
        raise ChronologyError("expected a v1.5 U1 chronology receipt")
    if value.get("protocol_version") != "1.5" or value.get("status") != "VALID_U1":
        raise ChronologyError("U1 receipt status/version is invalid")
    if value.get("chronology_rule") != {
        "path": CHRONOLOGY_RULE.relative_to(ROOT).as_posix(), "sha256": rule_sha
    }:
        raise ChronologyError("U1 receipt does not bind the current frozen chronology rule")
    p1 = value.get("p1", {})
    exact_oid(p1.get("p1a_commit"), "receipt P1A commit")
    p1t = exact_oid(p1.get("p1t_commit"), "receipt P1T commit")
    public = p1.get("public_receipt", {})
    if public.get("repository") != PROTOCOL_PUBLIC_REPOSITORY or public.get("ref") != PROTOCOL_PUBLIC_REF or public.get("observed_tip") != p1t:
        raise ChronologyError("U1 public P1T receipt is not canonical")
    public_done = parse_time(public.get("verification_completed_at_utc"), "P1T public receipt")
    upstream = value.get("upstream", {})
    if upstream.get("repository") != UPSTREAM_REPOSITORY or upstream.get("ref") != UPSTREAM_REF:
        raise ChronologyError("U1 upstream source/ref is not canonical main")
    if upstream.get("fetch_count") != 1 or upstream.get("retry_count") != 0:
        raise ChronologyError("U1 receipt does not prove one no-retry fetch")
    exact_oid(upstream.get("commit"), "U1 commit")
    exact_oid(upstream.get("root_tree"), "U1 root tree")
    exact_oid(upstream.get("formal_conjectures_tree"), "U1 FormalConjectures tree")
    if public_done >= parse_time(upstream.get("capture_started_at_utc"), "U1 capture start"):
        raise ChronologyError("U1 receipt chronology does not satisfy public P1T < U1")
    return value


def checkpoint_time(value: Any) -> datetime:
    parsed = parse_time(value, "scheduled checkpoint")
    if parsed.hour != CHECKPOINT_HOUR or parsed.minute != CHECKPOINT_MINUTE or parsed.second or parsed.microsecond:
        raise ChronologyError("checkpoint label must be an exact daily 00:17:00Z tick")
    if parsed > parse_time(LAST_CHECKPOINT, "last checkpoint"):
        raise ChronologyError("checkpoint is after the frozen terminal horizon")
    return parsed


def first_checkpoint_after(u1: dict[str, Any]) -> datetime:
    completed = parse_time(u1["upstream"]["capture_completed_at_utc"], "U1 completion")
    tick = completed.replace(hour=CHECKPOINT_HOUR, minute=CHECKPOINT_MINUTE, second=0, microsecond=0)
    if tick <= completed:
        tick += timedelta(days=1)
    return tick


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChronologyError("previous checkpoint is not valid UTF-8 JSON") from exc
    if value.get("schema") != SCHEMA or value.get("artifact_kind") != "CHECKPOINT_RECEIPT":
        raise ChronologyError("previous artifact is not a v1.5 checkpoint receipt")
    checkpoint_time(value.get("scheduled_for_utc"))
    if value.get("status") not in {"QUOTA_FAIL", "MISSED", "QUOTA_PASS_U2", "TERMINAL_QUOTA_DEFICIT", "INVALID_CHRONOLOGY_CAPTURE"}:
        raise ChronologyError("previous checkpoint status is invalid")
    return value


def checkpoint_position(
    u1: dict[str, Any], previous_path: Path | None, scheduled_for: str
) -> tuple[int, dict[str, Any] | None, datetime]:
    scheduled = checkpoint_time(scheduled_for)
    first = first_checkpoint_after(u1)
    if previous_path is None:
        if scheduled != first:
            raise ChronologyError("first checkpoint is not the first daily 00:17 tick strictly after U1")
        return 1, None, scheduled
    previous = load_checkpoint(previous_path)
    if previous["status"] in {"QUOTA_PASS_U2", "TERMINAL_QUOTA_DEFICIT", "INVALID_CHRONOLOGY_CAPTURE"}:
        raise ChronologyError("checkpoint chain is already terminal")
    expected = checkpoint_time(previous["scheduled_for_utc"]) + timedelta(days=1)
    if scheduled != expected:
        raise ChronologyError("checkpoint chain skipped, duplicated, or reordered a daily tick")
    ordinal = previous.get("checkpoint_ordinal")
    if not isinstance(ordinal, int) or ordinal < 1:
        raise ChronologyError("previous checkpoint ordinal is invalid")
    return ordinal + 1, previous, scheduled


def _checkpoint_basis(
    u1_path: Path, previous_path: Path | None, scheduled_for: str
) -> tuple[dict[str, Any], int, dict[str, Any] | None, datetime, dict[str, Any]]:
    u1 = validate_u1(u1_path)
    ordinal, previous, scheduled = checkpoint_position(u1, previous_path, scheduled_for)
    basis = {
        "u1_receipt": {
            "path": repo_relative(u1_path, "U1 receipt"),
            "sha256": sha256_file(u1_path),
            "commit": u1["upstream"]["commit"],
        },
        "previous_checkpoint": None if previous_path is None else {
            "path": repo_relative(previous_path, "previous checkpoint"),
            "sha256": sha256_file(previous_path),
            "checkpoint_ordinal": previous["checkpoint_ordinal"],
            "scheduled_for_utc": previous["scheduled_for_utc"],
            "status": previous["status"],
        },
    }
    return u1, ordinal, previous, scheduled, basis


def capture_checkpoint(
    u1_path: Path,
    previous_path: Path | None,
    scheduled_for: str,
    event_name: str,
    run_attempt: int,
    destination: Path,
) -> dict[str, Any]:
    """Capture one valid schedule-triggered daily checkpoint (not its quota verdict)."""
    u1, ordinal, _, scheduled, basis = _checkpoint_basis(u1_path, previous_path, scheduled_for)
    if event_name != "schedule" or run_attempt != 1:
        raise ChronologyError("only an original schedule event may create a checkpoint capture")
    observed = _now()
    deadline = scheduled.replace(hour=CHECKPOINT_START_DEADLINE_HOUR, minute=0)
    if not (scheduled <= observed < deadline):
        raise ChronologyError("scheduled checkpoint did not start in its [00:17,06:00) UTC window")
    upstream = capture_upstream(destination)
    actual = parse_time(upstream["capture_started_at_utc"], "checkpoint fetch start")
    if not (scheduled <= actual < deadline):
        raise ChronologyError("actual checkpoint fetch began outside its frozen window")
    try:
        _bare_git(destination, "merge-base", "--is-ancestor", u1["upstream"]["commit"], upstream["commit"])
    except ChronologyError as exc:
        raise ChronologyError("checkpoint tip is not a connected descendant of U1") from exc
    return {
        "schema": SCHEMA,
        "artifact_kind": "CHECKPOINT_CAPTURE",
        "protocol_version": "1.5",
        "chronology_rule": u1["chronology_rule"],
        "checkpoint_ordinal": ordinal,
        "scheduled_for_utc": scheduled_for,
        "trigger": {"event_name": event_name, "run_attempt": run_attempt},
        "basis": basis,
        "upstream": upstream,
        "status": "AWAITING_MACHINE_QUOTA_CERTIFICATE",
    }


def record_missed_checkpoint(
    u1_path: Path, previous_path: Path | None, scheduled_for: str
) -> dict[str, Any]:
    u1, ordinal, _, scheduled, basis = _checkpoint_basis(u1_path, previous_path, scheduled_for)
    deadline = scheduled.replace(hour=CHECKPOINT_START_DEADLINE_HOUR, minute=0)
    observed = _now()
    if observed < deadline:
        raise ChronologyError("a checkpoint cannot be declared missed before its start deadline")
    terminal = scheduled == parse_time(LAST_CHECKPOINT, "last checkpoint")
    return {
        "schema": SCHEMA,
        "artifact_kind": "CHECKPOINT_RECEIPT",
        "protocol_version": "1.5",
        "chronology_rule": u1["chronology_rule"],
        "checkpoint_ordinal": ordinal,
        "scheduled_for_utc": scheduled_for,
        "basis": basis,
        "capture": None,
        "quota_certificate": None,
        "recorded_at_utc": format_time(observed),
        "terminal_horizon": terminal,
        "status": "INVALID_CHRONOLOGY_CAPTURE" if terminal else "MISSED",
    }


STRATA_QUOTAS = {
    "GRAPH_SCALAR_INEQUALITY": 3,
    "GRAPH_STRUCTURAL_PROPERTY": 3,
    "FINITE_ALGEBRA_EQUATIONAL": 2,
    "AUTOMATA_GAME_PROCESS": 2,
    "FINITE_COMBINATORIAL": 2,
}


def finalize_checkpoint(
    capture_path: Path, certificate_path: Path, replay_attestation_path: Path
) -> dict[str, Any]:
    try:
        capture = json.loads(capture_path.read_text(encoding="utf-8"))
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        replay_attestation = json.loads(replay_attestation_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ChronologyError("capture or quota certificate is not valid UTF-8 JSON") from exc
    if capture.get("schema") != SCHEMA or capture.get("artifact_kind") != "CHECKPOINT_CAPTURE":
        raise ChronologyError("expected a v1.5 checkpoint capture")
    try:
        aggregate.validate_certificate(certificate)
        aggregate.validate_schema(
            replay_attestation, aggregate.ATTESTATION_SCHEMA_PATH, "replay attestation"
        )
    except aggregate.CertificateError as exc:
        raise ChronologyError(f"invalid aggregate/replay proof: {exc}") from exc
    if replay_attestation.get("attestation_sha256") != aggregate.attestation_digest(replay_attestation):
        raise ChronologyError("replay attestation self-digest is invalid")
    if replay_attestation.get("certificate_sha256") != certificate.get("certificate_sha256"):
        raise ChronologyError("replay attestation authenticates another aggregate certificate")
    if certificate["checkpoint"]["ordinal"] != capture["checkpoint_ordinal"] or certificate["checkpoint"]["scheduled_for_utc"] != capture["scheduled_for_utc"]:
        raise ChronologyError("aggregate certificate identifies a different checkpoint")
    upstream = certificate["upstream"]
    if any(upstream[key] != capture["upstream"][key] for key in ("commit", "root_tree", "formal_conjectures_tree")):
        raise ChronologyError("aggregate certificate is not bound to captured upstream trees")
    if replay_attestation.get("upstream") != {key: upstream[key] for key in ("commit", "root_tree", "formal_conjectures_tree")}:
        raise ChronologyError("replay attestation upstream binding differs")
    if certificate["chronology"]["receipt"] != {
        "path": repo_relative(capture_path, "checkpoint capture"),
        "sha256": sha256_file(capture_path),
    } or replay_attestation.get("chronology_receipt_sha256") != sha256_file(capture_path):
        raise ChronologyError("aggregate/replay proof authenticates another capture")
    aggregates = certificate["aggregates"]
    if aggregates["quotas"] != STRATA_QUOTAS or set(aggregates["eligible_by_stratum"]) != set(STRATA_QUOTAS) or set(aggregates["deficits"]) != set(STRATA_QUOTAS):
        raise ChronologyError("aggregate certificate does not cover exact frozen strata/quotas")
    included = aggregates["eligible_by_stratum"]
    if any(not isinstance(included[key], int) or included[key] < 0 for key in STRATA_QUOTAS):
        raise ChronologyError("quota counts must be nonnegative integers")
    deficits = {key: max(0, quota - included[key]) for key, quota in STRATA_QUOTAS.items()}
    if aggregates["deficits"] != deficits:
        raise ChronologyError("quota deficits are not replayable from aggregate counts")
    passed = not any(deficits.values())
    if aggregates["status"] != ("PASS" if passed else "FAIL"):
        raise ChronologyError("quota certificate status differs from replayed deficits")
    if aggregates["candidate_count"] != sum(included.values()):
        raise ChronologyError("candidate count differs from aggregate stratum counts")
    scheduled = checkpoint_time(capture["scheduled_for_utc"])
    terminal = scheduled == parse_time(LAST_CHECKPOINT, "last checkpoint")
    status = "QUOTA_PASS_U2" if passed else ("TERMINAL_QUOTA_DEFICIT" if terminal else "QUOTA_FAIL")
    return {
        "schema": SCHEMA,
        "artifact_kind": "CHECKPOINT_RECEIPT",
        "protocol_version": "1.5",
        "chronology_rule": capture["chronology_rule"],
        "checkpoint_ordinal": capture["checkpoint_ordinal"],
        "scheduled_for_utc": capture["scheduled_for_utc"],
        "basis": capture["basis"],
        "capture": {
            "path": repo_relative(capture_path, "checkpoint capture"),
            "sha256": sha256_file(capture_path),
            "commit": capture["upstream"]["commit"],
            "root_tree": capture["upstream"]["root_tree"],
            "formal_conjectures_tree": capture["upstream"]["formal_conjectures_tree"],
        },
        "quota_certificate": {
            "path": repo_relative(certificate_path, "quota certificate"),
            "sha256": sha256_file(certificate_path),
            "certificate_sha256": certificate["certificate_sha256"],
            "aggregates": aggregates,
        },
        "replay_attestation": {
            "path": repo_relative(replay_attestation_path, "replay attestation"),
            "sha256": sha256_file(replay_attestation_path),
            "attestation_sha256": replay_attestation["attestation_sha256"],
        },
        "terminal_horizon": terminal,
        "u2": None if not passed else {
            "commit": capture["upstream"]["commit"],
            "root_tree": capture["upstream"]["root_tree"],
            "formal_conjectures_tree": capture["upstream"]["formal_conjectures_tree"],
            "u1_is_ancestor": True,
            "membership_interval": f"{capture['basis']['u1_receipt']['commit']}..{capture['upstream']['commit']}",
        },
        "status": status,
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise ChronologyError("chronology output already exists; overwrite/retry is forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    u1 = commands.add_parser("capture-u1")
    u1.add_argument("--p1t-artifact", type=Path, required=True)
    u1.add_argument("--p1t-commit", required=True)
    u1.add_argument("--bare-destination", type=Path, required=True)
    u1.add_argument("--output", type=Path, required=True)
    capture = commands.add_parser("capture-checkpoint")
    capture.add_argument("--u1-receipt", type=Path, required=True)
    capture.add_argument("--previous-receipt", type=Path)
    capture.add_argument("--scheduled-for-utc", required=True)
    capture.add_argument("--event-name", required=True)
    capture.add_argument("--run-attempt", type=int, required=True)
    capture.add_argument("--bare-destination", type=Path, required=True)
    capture.add_argument("--output", type=Path, required=True)
    missed = commands.add_parser("record-missed")
    missed.add_argument("--u1-receipt", type=Path, required=True)
    missed.add_argument("--previous-receipt", type=Path)
    missed.add_argument("--scheduled-for-utc", required=True)
    missed.add_argument("--output", type=Path, required=True)
    finalize = commands.add_parser("finalize-checkpoint")
    finalize.add_argument("--capture", type=Path, required=True)
    finalize.add_argument("--quota-certificate", type=Path, required=True)
    finalize.add_argument("--replay-attestation", type=Path, required=True)
    finalize.add_argument("--output", type=Path, required=True)
    check = commands.add_parser("validate-u1")
    check.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "capture-u1":
            value = build_u1(args.p1t_artifact.resolve(), args.p1t_commit, args.bare_destination.resolve())
            write_json(args.output.resolve(), value)
        elif args.command == "capture-checkpoint":
            value = capture_checkpoint(
                args.u1_receipt.resolve(),
                None if args.previous_receipt is None else args.previous_receipt.resolve(),
                args.scheduled_for_utc, args.event_name, args.run_attempt,
                args.bare_destination.resolve(),
            )
            write_json(args.output.resolve(), value)
        elif args.command == "record-missed":
            value = record_missed_checkpoint(
                args.u1_receipt.resolve(),
                None if args.previous_receipt is None else args.previous_receipt.resolve(),
                args.scheduled_for_utc,
            )
            write_json(args.output.resolve(), value)
        elif args.command == "finalize-checkpoint":
            value = finalize_checkpoint(
                args.capture.resolve(), args.quota_certificate.resolve(),
                args.replay_attestation.resolve(),
            )
            write_json(args.output.resolve(), value)
        else:
            validate_u1(args.receipt.resolve())
    except (ChronologyError, OSError) as exc:
        print(f"INVALID_CHRONOLOGY_CAPTURE: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
