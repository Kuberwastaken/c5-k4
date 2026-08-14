#!/usr/bin/env python3
"""Validate and execute one frozen, finite scientific-search shard.

The worker owns its incremental files under ``worker/``.  This runner owns the
terminal classification beside that directory, so an interrupted worker can
never turn a durable prefix into an exhaustion claim merely by returning zero.

Manifest schema (``c5k4-scientific-shards-1.0``)::

    {
      "schema": "c5k4-scientific-shards-1.0",
      "campaign_id": "short-safe-name",
      "campaign_commit": "<40 lowercase hex>",
      "command": ["python3", "scripts/frozen_worker.py"],
      "wall_seconds": 60,
      "shards": [{
        "shard_id": "000",
        "range_start": 0,
        "range_stop": 100,
        "domain_sha256": "<64 lowercase hex>",
        "args": ["--mode", "exact"]
      }]
    }

The worker receives its assignment through ``C5K4_SHARD_*`` variables and must
write ``$C5K4_WORKER_OUTPUT/terminal.json``.  A valid exhaustion attestation is
an exact JSON object with schema ``c5k4-scientific-worker-terminal-1.0``, the
bound shard fields, ``states_scanned == range_stop - range_start``, and terminal
reason ``DOMAIN_EXHAUSTED``.  ``CANDIDATE_FOUND`` is also accepted but is not an
exhaustion claim.  Missing, malformed, or inconsistent attestations are
classified explicitly by this runner.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence


MANIFEST_SCHEMA = "c5k4-scientific-shards-1.0"
WORKER_TERMINAL_SCHEMA = "c5k4-scientific-worker-terminal-1.0"
RUNNER_TERMINAL_SCHEMA = "c5k4-scientific-runner-terminal-1.0"
SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
LOWER_SHA40 = re.compile(r"^[0-9a-f]{40}$")
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_SHARDS = 256
MAX_WALL_SECONDS = 60
ACCEPTED_WORKER_REASONS = frozenset({"DOMAIN_EXHAUSTED", "CANDIDATE_FOUND"})


class ContractError(ValueError):
    """The frozen campaign or worker attestation violates the shard contract."""


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ContractError(
            f"{label} fields differ: expected {sorted(expected)}, got {sorted(value)}"
        )


def _inside_repository(path_text: str, repository: Path) -> Path:
    if not path_text or "\x00" in path_text:
        raise ContractError("manifest path is empty or contains NUL")
    candidate = Path(path_text)
    if candidate.is_absolute():
        raise ContractError("manifest path must be repository-relative")
    resolved = (repository / candidate).resolve()
    try:
        resolved.relative_to(repository.resolve())
    except ValueError as exc:
        raise ContractError("manifest path escapes the repository") from exc
    if not resolved.is_file():
        raise ContractError(f"manifest is not a regular file: {path_text}")
    return resolved


def _string_vector(value: object, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "" if allow_empty else "nonempty "
        raise ContractError(f"{label} must be a {qualifier}JSON string array")
    if any(not isinstance(item, str) or not item or "\x00" in item for item in value):
        raise ContractError(f"{label} contains an empty, non-string, or NUL-bearing value")
    return list(value)


def load_manifest(path: Path, expected_commit: str) -> dict[str, Any]:
    if not LOWER_SHA40.fullmatch(expected_commit):
        raise ContractError("campaign commit must be exact lowercase 40-hex")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("manifest is not a JSON object")
    _exact_keys(
        value,
        {"schema", "campaign_id", "campaign_commit", "command", "wall_seconds", "shards"},
        "manifest",
    )
    if value["schema"] != MANIFEST_SCHEMA:
        raise ContractError("unsupported manifest schema")
    if not isinstance(value["campaign_id"], str) or not SAFE_ID.fullmatch(value["campaign_id"]):
        raise ContractError("campaign_id is not artifact-name safe")
    if value["campaign_commit"] != expected_commit:
        raise ContractError("manifest is not bound to the requested campaign commit")
    value["command"] = _string_vector(value["command"], "command")
    wall_seconds = value["wall_seconds"]
    if type(wall_seconds) is not int or not 1 <= wall_seconds <= MAX_WALL_SECONDS:
        raise ContractError(f"wall_seconds must be an integer in [1,{MAX_WALL_SECONDS}]")
    shards = value["shards"]
    if not isinstance(shards, list) or not 1 <= len(shards) <= MAX_SHARDS:
        raise ContractError(f"shards must contain between 1 and {MAX_SHARDS} rows")
    ids: set[str] = set()
    intervals: list[tuple[int, int, str]] = []
    normalized: list[dict[str, Any]] = []
    fields = {"shard_id", "range_start", "range_stop", "domain_sha256", "args"}
    for index, raw in enumerate(shards):
        if not isinstance(raw, dict):
            raise ContractError(f"shards[{index}] is not an object")
        _exact_keys(raw, fields, f"shards[{index}]")
        shard_id = raw["shard_id"]
        if not isinstance(shard_id, str) or not SAFE_ID.fullmatch(shard_id):
            raise ContractError(f"shards[{index}].shard_id is unsafe")
        if shard_id in ids:
            raise ContractError(f"duplicate shard_id: {shard_id}")
        ids.add(shard_id)
        start, stop = raw["range_start"], raw["range_stop"]
        if type(start) is not int or type(stop) is not int or start < 0 or stop <= start:
            raise ContractError(f"shard {shard_id} has an invalid half-open range")
        digest = raw["domain_sha256"]
        if not isinstance(digest, str) or not LOWER_SHA256.fullmatch(digest):
            raise ContractError(f"shard {shard_id} has an invalid domain_sha256")
        intervals.append((start, stop, shard_id))
        normalized.append({
            **raw,
            "args": _string_vector(raw["args"], f"shard {shard_id} args", allow_empty=True),
        })
    for left, right in zip(sorted(intervals), sorted(intervals)[1:]):
        if right[0] < left[1]:
            raise ContractError(f"shard ranges overlap: {left[2]} and {right[2]}")
    value["shards"] = normalized
    return value


def _select_shard(manifest: Mapping[str, Any], shard_id: str) -> dict[str, Any]:
    matches = [row for row in manifest["shards"] if row["shard_id"] == shard_id]
    if len(matches) != 1:
        raise ContractError(f"shard_id is not present exactly once: {shard_id}")
    return matches[0]


def _runner_terminal(
    manifest: Mapping[str, Any],
    shard: Mapping[str, Any],
    *,
    reason: str,
    worker_returncode: int,
    timed_out: bool,
    wall_milliseconds: int,
    states_scanned: int | None,
    detail: str,
) -> dict[str, Any]:
    return {
        "schema": RUNNER_TERMINAL_SCHEMA,
        "campaign_id": manifest["campaign_id"],
        "campaign_commit": manifest["campaign_commit"],
        "shard_id": shard["shard_id"],
        "range_start": shard["range_start"],
        "range_stop": shard["range_stop"],
        "domain_sha256": shard["domain_sha256"],
        "terminal_reason": reason,
        "worker_returncode": worker_returncode,
        "timed_out": timed_out,
        "wall_milliseconds": wall_milliseconds,
        "states_scanned": states_scanned,
        "detail": detail,
    }


def _validate_worker_terminal(
    path: Path, manifest: Mapping[str, Any], shard: Mapping[str, Any]
) -> tuple[str, int]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"worker terminal is missing or invalid: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("worker terminal is not an object")
    fields = {
        "schema", "campaign_id", "campaign_commit", "shard_id", "range_start",
        "range_stop", "domain_sha256", "states_scanned", "terminal_reason",
    }
    _exact_keys(value, fields, "worker terminal")
    if raw != canonical_bytes(value):
        raise ContractError("worker terminal is not canonical JSON with a final newline")
    bindings = {
        "schema": WORKER_TERMINAL_SCHEMA,
        "campaign_id": manifest["campaign_id"],
        "campaign_commit": manifest["campaign_commit"],
        "shard_id": shard["shard_id"],
        "range_start": shard["range_start"],
        "range_stop": shard["range_stop"],
        "domain_sha256": shard["domain_sha256"],
    }
    for key, expected in bindings.items():
        if value[key] != expected:
            raise ContractError(f"worker terminal binding mismatch: {key}")
    scanned = value["states_scanned"]
    if type(scanned) is not int or scanned < 0 or scanned > shard["range_stop"] - shard["range_start"]:
        raise ContractError("worker states_scanned is outside its assigned finite range")
    reason = value["terminal_reason"]
    if reason not in ACCEPTED_WORKER_REASONS:
        raise ContractError("worker terminal_reason is unsupported")
    if reason == "DOMAIN_EXHAUSTED" and scanned != shard["range_stop"] - shard["range_start"]:
        raise ContractError("DOMAIN_EXHAUSTED does not scan the entire assigned range")
    return reason, scanned


def execute(manifest: dict[str, Any], shard_id: str, output: Path) -> dict[str, Any]:
    shard = _select_shard(manifest, shard_id)
    output = output.resolve()
    if output.exists():
        raise ContractError("output directory must not pre-exist")
    worker_output = output / "worker"
    worker_output.mkdir(parents=True)
    (output / "manifest.json").write_bytes(canonical_bytes(manifest))

    env = os.environ.copy()
    env.update({
        "C5K4_CAMPAIGN_ID": manifest["campaign_id"],
        "C5K4_CAMPAIGN_COMMIT": manifest["campaign_commit"],
        "C5K4_SHARD_ID": shard["shard_id"],
        "C5K4_SHARD_START": str(shard["range_start"]),
        "C5K4_SHARD_STOP": str(shard["range_stop"]),
        "C5K4_SHARD_DOMAIN_SHA256": shard["domain_sha256"],
        "C5K4_WORKER_OUTPUT": str(worker_output),
    })
    command = [*manifest["command"], *shard["args"]]
    started = time.monotonic()
    with (output / "stdout.txt").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
        process = subprocess.Popen(
            command,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        timed_out = False
        try:
            returncode = process.wait(timeout=manifest["wall_seconds"])
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                returncode = process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                returncode = process.wait()
    wall_milliseconds = int((time.monotonic() - started) * 1000)

    states_scanned: int | None = None
    detail = ""
    if timed_out:
        reason = "DEADLINE_PREFIX"
        detail = "runner wall deadline terminated the worker process group"
    elif returncode != 0:
        reason = "WORKER_FAILURE"
        detail = "worker returned nonzero before a valid completion classification"
    else:
        terminal_path = worker_output / "terminal.json"
        if not terminal_path.exists():
            reason = "WORKER_INCOMPLETE"
            detail = "zero exit without a worker terminal attestation"
        else:
            try:
                reason, states_scanned = _validate_worker_terminal(terminal_path, manifest, shard)
            except ContractError as exc:
                reason = "INVALID_WORKER_ATTESTATION"
                detail = str(exc)

    terminal = _runner_terminal(
        manifest,
        shard,
        reason=reason,
        worker_returncode=returncode,
        timed_out=timed_out,
        wall_milliseconds=wall_milliseconds,
        states_scanned=states_scanned,
        detail=detail,
    )
    (output / "runner-terminal.json").write_bytes(canonical_bytes(terminal))
    return terminal


def aggregate(manifest: dict[str, Any], evidence: Path, output: Path) -> dict[str, Any]:
    """Build a small campaign index without copying the per-shard evidence."""

    evidence = evidence.resolve()
    output = output.resolve()
    if output.exists():
        raise ContractError("aggregate output must not pre-exist")
    if not evidence.is_dir():
        raise ContractError("downloaded shard evidence directory is missing")
    expected = {row["shard_id"]: row for row in manifest["shards"]}
    terminals: dict[str, dict[str, Any]] = {}
    for path in sorted(evidence.rglob("runner-terminal.json")):
        try:
            raw = path.read_bytes()
            value = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ContractError(f"cannot read runner terminal {path}: {exc}") from exc
        if not isinstance(value, dict) or raw != canonical_bytes(value):
            raise ContractError(f"runner terminal is not canonical JSON: {path}")
        terminal_fields = {
            "schema", "campaign_id", "campaign_commit", "shard_id", "range_start",
            "range_stop", "domain_sha256", "terminal_reason", "worker_returncode",
            "timed_out", "wall_milliseconds", "states_scanned", "detail",
        }
        _exact_keys(value, terminal_fields, f"runner terminal {path}")
        shard_id = value.get("shard_id")
        if shard_id not in expected:
            raise ContractError(f"runner terminal has an unexpected shard_id: {shard_id}")
        if shard_id in terminals:
            raise ContractError(f"multiple artifacts claim shard_id: {shard_id}")
        shard = expected[shard_id]
        bindings = {
            "schema": RUNNER_TERMINAL_SCHEMA,
            "campaign_id": manifest["campaign_id"],
            "campaign_commit": manifest["campaign_commit"],
            "shard_id": shard_id,
            "range_start": shard["range_start"],
            "range_stop": shard["range_stop"],
            "domain_sha256": shard["domain_sha256"],
        }
        for key, expected_value in bindings.items():
            if value.get(key) != expected_value:
                raise ContractError(f"runner terminal binding mismatch for {shard_id}: {key}")
        reason = value["terminal_reason"]
        scanned = value["states_scanned"]
        range_size = shard["range_stop"] - shard["range_start"]
        if type(value["worker_returncode"]) is not int:
            raise ContractError(f"runner terminal has invalid worker_returncode: {shard_id}")
        if type(value["timed_out"]) is not bool:
            raise ContractError(f"runner terminal has invalid timed_out: {shard_id}")
        if type(value["wall_milliseconds"]) is not int or value["wall_milliseconds"] < 0:
            raise ContractError(f"runner terminal has invalid wall_milliseconds: {shard_id}")
        if scanned is not None and (type(scanned) is not int or not 0 <= scanned <= range_size):
            raise ContractError(f"runner terminal has invalid states_scanned: {shard_id}")
        if reason == "DOMAIN_EXHAUSTED" and scanned != range_size:
            raise ContractError(f"runner exhaustion count is incomplete: {shard_id}")
        if reason == "DEADLINE_PREFIX" and value["timed_out"] is not True:
            raise ContractError(f"deadline prefix lacks runner timeout: {shard_id}")
        terminals[shard_id] = value

    missing = sorted(set(expected) - set(terminals))
    reason_counts: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for shard_id in sorted(terminals):
        terminal = terminals[shard_id]
        reason = str(terminal.get("terminal_reason", "INVALID"))
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        rows.append({
            "shard_id": shard_id,
            "terminal_reason": reason,
            "states_scanned": terminal.get("states_scanned"),
            "range_size": expected[shard_id]["range_stop"] - expected[shard_id]["range_start"],
            "wall_milliseconds": terminal.get("wall_milliseconds"),
        })
    invalid_reasons = sorted(
        reason for reason in reason_counts
        if reason not in {"DOMAIN_EXHAUSTED", "DEADLINE_PREFIX", "CANDIDATE_FOUND"}
    )
    if missing:
        campaign_reason = "INCOMPLETE_EVIDENCE"
    elif invalid_reasons:
        campaign_reason = "INVALID_SHARD_RESULT"
    elif reason_counts.get("CANDIDATE_FOUND", 0):
        campaign_reason = "CANDIDATE_FOUND"
    elif reason_counts.get("DEADLINE_PREFIX", 0):
        campaign_reason = "DEADLINE_PREFIX"
    elif reason_counts == {"DOMAIN_EXHAUSTED": len(expected)}:
        campaign_reason = "DOMAIN_EXHAUSTED"
    else:  # Defensive: all accepted reason combinations are handled above.
        campaign_reason = "INVALID_SHARD_RESULT"

    index = {
        "schema": "c5k4-scientific-campaign-index-1.0",
        "campaign_id": manifest["campaign_id"],
        "campaign_commit": manifest["campaign_commit"],
        "expected_shards": len(expected),
        "observed_shards": len(terminals),
        "missing_shards": missing,
        "terminal_reason_counts": dict(sorted(reason_counts.items())),
        "campaign_terminal_reason": campaign_reason,
        "shards": rows,
    }
    output.mkdir(parents=True)
    (output / "campaign-index.json").write_bytes(canonical_bytes(index))
    return index


def _prepare(args: argparse.Namespace) -> int:
    repository = args.repository.resolve()
    path = _inside_repository(args.manifest, repository)
    manifest = load_manifest(path, args.campaign_commit)
    matrix = {"include": [{"shard_id": row["shard_id"]} for row in manifest["shards"]]}
    sys.stdout.buffer.write(canonical_bytes(matrix))
    return 0


def _execute(args: argparse.Namespace) -> int:
    repository = args.repository.resolve()
    path = _inside_repository(args.manifest, repository)
    manifest = load_manifest(path, args.campaign_commit)
    terminal = execute(manifest, args.shard_id, args.output)
    sys.stdout.buffer.write(canonical_bytes(terminal))
    return 0


def _aggregate(args: argparse.Namespace) -> int:
    repository = args.repository.resolve()
    path = _inside_repository(args.manifest, repository)
    manifest = load_manifest(path, args.campaign_commit)
    index = aggregate(manifest, args.evidence, args.output)
    sys.stdout.buffer.write(canonical_bytes(index))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    for name in ("prepare", "execute", "aggregate"):
        command = subparsers.add_parser(name)
        command.add_argument("--repository", type=Path, default=Path.cwd())
        command.add_argument("--manifest", required=True)
        command.add_argument("--campaign-commit", required=True)
        if name == "execute":
            command.add_argument("--shard-id", required=True)
            command.add_argument("--output", type=Path, required=True)
        elif name == "aggregate":
            command.add_argument("--evidence", type=Path, required=True)
            command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.subcommand == "prepare":
            return _prepare(args)
        if args.subcommand == "execute":
            return _execute(args)
        return _aggregate(args)
    except (ContractError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
