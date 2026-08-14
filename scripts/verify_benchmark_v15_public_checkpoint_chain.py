#!/usr/bin/env python3
"""Authenticate the Method v1.5 checkpoint chain from public Git ancestry.

This verifier does not accept a caller-selected previous receipt.  It derives
the unique previous receipt, its blob, and its introducing commit by walking
the exact publication ref back to the authenticated P1R activation boundary.
Every publication commit must be a
single-parent, add-only commit with the frozen path set.  Consequently the
next normal push can only append to the public tip proved here.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any, Sequence


PUBLIC_REPOSITORY = "https://github.com/Kuberwastaken/c5-k4.git"
PUBLICATION_BRANCH = "method-v1.5-checkpoints"
PUBLICATION_REF = f"refs/remotes/origin/{PUBLICATION_BRANCH}"
U1_PATH = "u1/chronology-receipt.json"
P1R_PATH = "results/benchmark/v1.5-protocol/P1R.json"
P1R_RECEIPT_DOMAIN = b"c5k4-method-v1.5-public-p1r-activation-receipt-1.0"
PUBLICATION_FILES = (
    "publication-manifest.json", "quota-certificate.json", "receipt.json",
)
RECEIPT_SCHEMA = "c5k4-method-v1.5-chronology-receipt-1.0"
PROOF_SCHEMA = "c5k4-method-v1.5-public-checkpoint-chain-proof-1.0"
TERMINAL_STATUSES = {
    "QUOTA_PASS_U2", "TERMINAL_QUOTA_DEFICIT", "INVALID_CHRONOLOGY_CAPTURE",
}
NONTERMINAL_STATUSES = {"QUOTA_FAIL", "MISSED"}
OID_RE = re.compile(r"^[0-9a-f]{40}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
LABEL_RE = re.compile(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})T00-17-00Z$")
LAST_CHECKPOINT = "2027-08-15T00:17:00Z"
SAFE_ENV = {
    "PATH": "/usr/bin:/bin", "HOME": "/nonexistent-c5k4-v15-public-chain",
    "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1",
}
SAFE_CONFIG = (
    "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never",
    "-c", "credential.helper=", "-c", "core.fsmonitor=false",
)


class PublicChainError(ValueError):
    """The public checkpoint ref does not prove the frozen append-only chain."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def proof_digest(proof: dict[str, Any]) -> str:
    unsigned = dict(proof)
    unsigned.pop("proof_sha256", None)
    return sha256(canonical_json(unsigned))


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PublicChainError(f"{label} must be an RFC3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PublicChainError(f"invalid {label}") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise PublicChainError(f"{label} must be UTC")
    return parsed


def format_time(value: datetime) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def first_tick_after(value: str) -> datetime:
    completed = parse_time(value, "U1 completion")
    tick = completed.replace(hour=0, minute=17, second=0, microsecond=0)
    return tick if tick > completed else tick + timedelta(days=1)


def _run(repo: Path, args: Sequence[str], *, check: bool = True) -> bytes:
    result = subprocess.run(
        ["/usr/bin/git", *SAFE_CONFIG, "-C", str(repo), *args], env=SAFE_ENV,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and result.returncode:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise PublicChainError(f"Git failed ({' '.join(args)}): {detail}")
    return result.stdout if result.returncode == 0 else b""


def exact_oid(value: Any, label: str) -> str:
    if not isinstance(value, str) or OID_RE.fullmatch(value) is None:
        raise PublicChainError(f"{label} must be an exact lowercase Git object ID")
    return value


def commit_blob(repo: Path, commit: str, path: str) -> bytes:
    if PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts:
        raise PublicChainError("non-normalized committed path")
    return _run(repo, ("show", f"{commit}:{path}"))


def json_blob(repo: Path, commit: str, path: str) -> tuple[dict[str, Any], bytes]:
    raw = commit_blob(repo, commit, path)
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicChainError(f"{path} at {commit} is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PublicChainError(f"{path} at {commit} is not one JSON object")
    return value, raw


def parents(repo: Path, commit: str) -> list[str]:
    return _run(repo, ("show", "-s", "--format=%P", commit)).decode().split()


def changes(repo: Path, commit: str) -> list[tuple[str, str]]:
    lines = _run(
        repo, ("diff-tree", "--no-commit-id", "--name-status", "-r", commit)
    ).decode().splitlines()
    result: list[tuple[str, str]] = []
    for line in lines:
        fields = line.split("\t")
        if len(fields) != 2:
            raise PublicChainError(f"rename/copy or malformed change in {commit}")
        result.append((fields[0], fields[1]))
    return result


def _checkpoint_path(scheduled: str) -> str:
    parsed = parse_time(scheduled, "checkpoint schedule")
    if (parsed.hour, parsed.minute, parsed.second, parsed.microsecond) != (0, 17, 0, 0):
        raise PublicChainError("checkpoint is not an exact 00:17:00Z tick")
    return "checkpoints/" + scheduled.replace(":", "-")


def _validate_u1(value: dict[str, Any], p1r_commit: str, expected_activation: dict[str, Any]) -> str:
    if value.get("schema") != RECEIPT_SCHEMA or value.get("artifact_kind") != "U1_CHRONOLOGY_RECEIPT":
        raise PublicChainError("genesis artifact is not the frozen U1 receipt type")
    if value.get("protocol_version") != "1.5" or value.get("status") != "VALID_U1":
        raise PublicChainError("U1 receipt version/status is invalid")
    p1_scope = value.get("p1", {})
    if p1_scope.get("p1r_commit") != p1r_commit:
        raise PublicChainError("U1 receipt is not bound to the genesis parent P1R")
    activation = p1_scope.get("activation_receipt")
    if (
        activation != expected_activation
        or not isinstance(activation, dict)
        or activation.get("p1r") != p1_scope.get("p1r_artifact")
    ):
        raise PublicChainError("U1 receipt lacks the exact authenticated P1R activation receipt")
    expected_activation_sha = sha256(canonical_json(activation))
    if p1_scope.get("p1r_activation_sha256") != expected_activation_sha:
        raise PublicChainError("U1 receipt has a different canonical P1R activation digest")
    validation_input = p1_scope.get("validation_input")
    if (
        not isinstance(validation_input, dict)
        or set(validation_input) != {"path", "sha256"}
        or validation_input.get("sha256") != activation.get("validation_inputs_sha256")
    ):
        raise PublicChainError("U1 receipt validation-input reference differs from activation")
    completed = value.get("upstream", {}).get("capture_completed_at_utc")
    parse_time(completed, "U1 completion")
    return completed


def verify_chain(
    repository: Path, publication_ref: str, p1r_commit: str,
    *, activation_verifier: Any | None = None,
    validation_input_path: Path | None = None,
) -> dict[str, Any]:
    """Prove the exact chain currently reachable from the public tracking ref."""
    repo = repository.resolve()
    if not repo.is_dir():
        raise PublicChainError("public Git object store is absent")
    p1r_commit = exact_oid(p1r_commit, "P1R commit")
    if publication_ref != PUBLICATION_REF:
        raise PublicChainError("only the frozen public tracking ref is admissible")
    origin = _run(repo, ("remote", "get-url", "origin")).decode().strip()
    if origin != PUBLIC_REPOSITORY:
        raise PublicChainError("origin is not the frozen public c5-k4 repository")
    if (repo / ".git/shallow").exists() or (repo / "shallow").exists():
        raise PublicChainError("shallow public ancestry cannot prove the checkpoint chain")
    tip = _run(repo, ("rev-parse", "--verify", publication_ref)).decode().strip()
    exact_oid(tip, "public publication tip")
    if _run(repo, ("rev-parse", "--verify", p1r_commit)).decode().strip() != p1r_commit:
        raise PublicChainError("P1R is absent from the authenticated object store")
    if activation_verifier is None or not callable(activation_verifier):
        raise PublicChainError("full public P1R activation verifier is not wired")
    if validation_input_path is None:
        raise PublicChainError("frozen candidate validation input is not wired")
    p1r_raw = commit_blob(repo, p1r_commit, P1R_PATH)
    try:
        validation_input_sha256 = sha256(validation_input_path.read_bytes())
    except OSError as exc:
        raise PublicChainError("frozen candidate validation input is unavailable") from exc
    try:
        activation = activation_verifier(
            repo, validation_input_path, validation_input_sha256, p1r_commit,
        )
    except Exception as exc:
        raise PublicChainError(f"public P1R activation verification failed: {exc}") from exc
    validate_p1r_activation_receipt(
        activation, p1r_commit, sha256(p1r_raw), validation_input_sha256,
    )
    activation_sha256 = sha256(canonical_json(activation))

    reverse: list[str] = []
    cursor = tip
    seen: set[str] = set()
    while cursor != p1r_commit:
        if cursor in seen:
            raise PublicChainError("cycle in public ancestry")
        seen.add(cursor)
        commit_parents = parents(repo, cursor)
        if len(commit_parents) != 1:
            raise PublicChainError("every publication commit must have exactly one parent")
        reverse.append(cursor)
        cursor = commit_parents[0]
    commits = list(reversed(reverse))
    if not commits:
        raise PublicChainError("publication branch has no U1 genesis after P1R")

    genesis = commits[0]
    if changes(repo, genesis) != [("A", U1_PATH)]:
        raise PublicChainError("genesis must add only the frozen U1 receipt path")
    u1, u1_raw = json_blob(repo, genesis, U1_PATH)
    u1_completed = _validate_u1(u1, p1r_commit, activation)
    expected_tick = first_tick_after(u1_completed)
    rows: list[dict[str, Any]] = []
    terminal = False
    for index, commit in enumerate(commits[1:], start=1):
        if terminal:
            raise PublicChainError("public chain continues after its first terminal checkpoint")
        expected_parent = commits[index - 1]
        if parents(repo, commit) != [expected_parent]:
            raise PublicChainError("checkpoint commit does not append to the prior public tip")
        changed = changes(repo, commit)
        if any(status != "A" for status, _ in changed):
            raise PublicChainError("checkpoint commits must be add-only")
        paths = sorted(path for _, path in changed)
        if len(paths) != 3:
            raise PublicChainError("checkpoint commit must add exactly three public artifacts")
        roots = {str(PurePosixPath(path).parent) for path in paths}
        if len(roots) != 1:
            raise PublicChainError("checkpoint artifacts do not share one destination")
        root = roots.pop()
        if sorted(PurePosixPath(path).name for path in paths) != sorted(PUBLICATION_FILES):
            raise PublicChainError("checkpoint commit has an unfrozen artifact set")
        receipt_path = f"{root}/receipt.json"
        receipt, receipt_raw = json_blob(repo, commit, receipt_path)
        json_blob(repo, commit, f"{root}/publication-manifest.json")
        certificate, _ = json_blob(repo, commit, f"{root}/quota-certificate.json")
        if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("artifact_kind") != "CHECKPOINT_RECEIPT":
            raise PublicChainError("public receipt has the wrong frozen type")
        ordinal = receipt.get("checkpoint_ordinal")
        if ordinal != index:
            raise PublicChainError("checkpoint ordinals are not contiguous from one")
        scheduled = receipt.get("scheduled_for_utc")
        if parse_time(scheduled, "checkpoint schedule") != expected_tick:
            raise PublicChainError("checkpoint dates are duplicated, skipped, or reordered")
        expected_root = _checkpoint_path(scheduled)
        if root != expected_root or LABEL_RE.fullmatch(root.removeprefix("checkpoints/")) is None:
            raise PublicChainError("checkpoint path does not encode its exact scheduled tick")
        status = receipt.get("status")
        if status not in NONTERMINAL_STATUSES | TERMINAL_STATUSES:
            raise PublicChainError("checkpoint status is invalid")
        if parse_time(scheduled, "checkpoint schedule") > parse_time(LAST_CHECKPOINT, "hard horizon"):
            raise PublicChainError("checkpoint is after the frozen hard horizon")
        if scheduled == LAST_CHECKPOINT and status not in TERMINAL_STATUSES:
            raise PublicChainError("hard-horizon checkpoint must terminate")
        aggregate_status = certificate.get("aggregates", {}).get("status")
        if status == "QUOTA_PASS_U2" and aggregate_status != "PASS":
            raise PublicChainError("PASS receipt is not supported by its quota certificate")
        if status in {"QUOTA_FAIL", "TERMINAL_QUOTA_DEFICIT"} and aggregate_status != "FAIL":
            raise PublicChainError("FAIL receipt is not supported by its quota certificate")
        prior = receipt.get("basis", {}).get("previous_checkpoint")
        if index == 1:
            if prior is not None:
                raise PublicChainError("first checkpoint falsely claims a predecessor")
        else:
            previous = rows[-1]
            expected_prior = {
                "path": previous["receipt_path"],
                "sha256": previous["receipt_blob_sha256"],
                "commit": previous["commit"],
                "checkpoint_ordinal": previous["ordinal"],
                "scheduled_for_utc": previous["scheduled_for_utc"],
                "status": previous["status"],
            }
            if prior != expected_prior:
                raise PublicChainError("receipt predecessor binding is not the public prior blob/commit")
        row = {
            "ordinal": ordinal, "scheduled_for_utc": scheduled, "status": status,
            "commit": commit, "parent_commit": expected_parent,
            "receipt_path": receipt_path, "receipt_blob_sha256": sha256(receipt_raw),
        }
        rows.append(row)
        terminal = status in TERMINAL_STATUSES
        expected_tick += timedelta(days=1)

    previous = rows[-1] if rows else None
    proof = {
        "schema": PROOF_SCHEMA,
        "repository": PUBLIC_REPOSITORY,
        "ref": publication_ref,
        "p1r_commit": p1r_commit,
        "p1r_activation": activation,
        "p1r_activation_sha256": activation_sha256,
        "public_tip_commit": tip,
        "genesis": {
            "commit": genesis, "parent_commit": p1r_commit, "u1_path": U1_PATH,
            "u1_blob_sha256": sha256(u1_raw),
        },
        "checkpoint_count": len(rows),
        "checkpoints": rows,
        "previous_checkpoint": previous,
        "next_checkpoint": None if terminal else {
            "ordinal": len(rows) + 1,
            "scheduled_for_utc": format_time(expected_tick),
            "required_parent_commit": tip,
        },
        "terminal": terminal,
        "normal_push_must_use_lease_tip": tip,
    }
    proof["proof_sha256"] = proof_digest(proof)
    return proof


def validate_p1r_activation_receipt(
    receipt: Any, p1r_commit: str, p1r_blob_sha256: str,
    validation_input_sha256: str,
) -> None:
    if not isinstance(receipt, dict) or set(receipt) != {
        "schema", "p1r", "p1r_commit", "activation_boundary", "public_observation",
        "validation_inputs_sha256", "validation_diagnostic_sha256", "validator",
        "receipt_sha256",
    }:
        raise PublicChainError("public P1R verifier returned a non-exact rich activation receipt")
    if (
        receipt["schema"] != P1R_RECEIPT_DOMAIN.decode()
        or receipt["p1r"] != {"path": P1R_PATH, "sha256": p1r_blob_sha256}
        or receipt["p1r_commit"] != p1r_commit
        or receipt["activation_boundary"] != "PUBLIC_AUTHENTICATED_P1R"
        or receipt["validation_inputs_sha256"] != validation_input_sha256
    ):
        raise PublicChainError("public P1R receipt exact artifact/input binding differs")
    sha_fields = (
        receipt["validation_diagnostic_sha256"], receipt["receipt_sha256"],
    )
    if any(not isinstance(value, str) or SHA_RE.fullmatch(value) is None for value in sha_fields):
        raise PublicChainError("public P1R receipt digest is malformed")
    validator = receipt["validator"]
    if (
        not isinstance(validator, dict) or set(validator) != {"path", "sha256"}
        or validator["path"] != "scripts/validate_benchmark_v15_candidate_base.py"
        or not isinstance(validator["sha256"], str) or SHA_RE.fullmatch(validator["sha256"]) is None
    ):
        raise PublicChainError("public P1R receipt validator binding differs")
    observation = receipt["public_observation"]
    if not isinstance(observation, dict) or set(observation) != {
        "workflow_repository", "workflow_path", "workflow_blob_sha256", "workflow_ref",
        "run_id", "run_attempt", "server_observed_at_utc", "actions_run_projection_sha256",
    }:
        raise PublicChainError("public P1R receipt observation shape differs")
    if (
        observation["workflow_repository"] != "Kuberwastaken/c5-k4"
        or observation["workflow_path"] != ".github/workflows/method-v15-p1r-publication-observer.yml"
        or observation["workflow_ref"] != ".github/workflows/method-v15-p1r-publication-observer.yml@refs/heads/method-v1.5-p1r"
        or not isinstance(observation["run_id"], int) or isinstance(observation["run_id"], bool)
        or observation["run_id"] < 1 or observation["run_attempt"] != 1
        or any(
            not isinstance(observation[key], str) or SHA_RE.fullmatch(observation[key]) is None
            for key in ("workflow_blob_sha256", "actions_run_projection_sha256")
        )
    ):
        raise PublicChainError("public P1R receipt public observation differs")
    parse_time(observation["server_observed_at_utc"], "P1R public observation")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if receipt["receipt_sha256"] != sha256(P1R_RECEIPT_DOMAIN + b"\0" + canonical_json(unsigned)):
        raise PublicChainError("public P1R receipt self-digest is invalid")


def candidate_activation_adapter(
    repository: Path, validation_input: Path, validation_input_sha256: str,
    p1r_commit: str,
) -> dict[str, Any]:
    try:
        from validate_benchmark_v15_candidate_base import verify_public_p1r_activation
    except (ImportError, OSError) as exc:
        raise PublicChainError("candidate public activation adapter is unavailable") from exc
    return verify_public_p1r_activation(
        repository, validation_input, validation_input_sha256, p1r_commit,
    )


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise PublicChainError("proof output already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--ref", default=PUBLICATION_REF)
    parser.add_argument("--p1r-commit", required=True)
    parser.add_argument("--validation-input", type=Path, required=True)
    parser.add_argument("--validation-input-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if sha256(args.validation_input.read_bytes()) != args.validation_input_sha256:
            raise PublicChainError("validation input differs from its frozen CLI digest")
        proof = verify_chain(
            args.repository, args.ref, args.p1r_commit,
            activation_verifier=candidate_activation_adapter,
            validation_input_path=args.validation_input,
        )
        write_json(args.output, proof)
    except (OSError, PublicChainError) as exc:
        print(f"INVALID_PUBLIC_CHECKPOINT_CHAIN: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
