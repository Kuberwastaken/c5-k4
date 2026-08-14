#!/usr/bin/env python3
"""Replay-verify the target-blind Method v1.5 candidate base through P1R.

All protocol/component bytes are read from exact Git objects.  The only
filesystem inputs are immutable evidence objects and the public Ed25519 keys
whose hashes were frozen in the public pre-C authority root.  This verify-only
command never creates P1, asserts public state from local disk, reads target
data, obtains entropy, or performs selection.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


PROTOCOL = "1.5"
OID = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PUBLIC_REMOTE = re.compile(r"^https://github\.com/Kuberwastaken/c5-k4(?:\.git)?$")
PUBLIC_REF = re.compile(r"^refs/(?:heads|tags)/[^ ]+$")

P1_BUILDER_PATH = "scripts/build_benchmark_v15_p1.py"
P1_SCHEMA_PATH = "schemas/benchmark-p1-v1.5.schema.json"
P0_SCHEMA_PATH = "schemas/benchmark-v1.4-p0.schema.json"
INPUT_SCHEMA_PATH = "schemas/benchmark-candidate-base-validation-input-v1.5.schema.json"
OUTPUT_SCHEMA_PATH = "schemas/benchmark-candidate-base-validation-output-v1.5.schema.json"
AUTHORITY_SCHEMA_PATH = "schemas/benchmark-public-readiness-authority-root-v1.5.schema.json"
EVIDENCE_SCHEMA_PATH = "schemas/benchmark-candidate-base-operational-evidence-v1.5.schema.json"
RECOMPILE_SCHEMA_PATH = "schemas/benchmark-candidate-base-independent-recompile-v1.5.schema.json"
PACKAGE_SCHEMA_PATH = "schemas/benchmark-candidate-base-readiness-package-v1.5.schema.json"
P1R_SCHEMA_PATH = "schemas/benchmark-p1r-v1.5.schema.json"
ACTIVATION_RECEIPT_SCHEMA_PATH = "schemas/benchmark-public-p1r-activation-receipt-v1.5.schema.json"
ISOLATED_RUNNER_PATH = "scripts/run_benchmark_v15_isolated_evidence.py"
ISOLATED_RUNNER_SCHEMA_PATH = "schemas/benchmark-candidate-base-isolated-evidence-runner-v1.5.schema.json"
ISOLATED_RUNNER_CONTRACT_PATH = "results/benchmark/v1.5-protocol/candidate-base-isolated-evidence-runner-contract.json"
ISOLATED_RUNNER_TEST_PATH = "scripts/test_run_benchmark_v15_isolated_evidence.py"
VALIDATOR_PATH = "scripts/validate_benchmark_v15_candidate_base.py"
P1A_PATH = "results/benchmark/v1.5-protocol/P1A.json"
P1T_PATH = "results/benchmark/v1.5-protocol/P1T.json"
P1R_PATH = "results/benchmark/v1.5-protocol/P1R.json"
P1T_OBSERVER_WORKFLOW_PATH = ".github/workflows/method-v15-p1t-publication-observer.yml"
P1R_OBSERVER_WORKFLOW_PATH = ".github/workflows/method-v15-p1r-publication-observer.yml"
P1R_PUBLIC_REF = "refs/heads/method-v1.5-p1r"

NATIVE_CONTENT_CLASS = "V1_5_PROTOCOL_ONLY_NO_TARGET_DATA"
INHERITED_CONTENT_CLASS = "INHERITED_V1_4_EXACT"
SOURCE_CONTENT_CLASS = "PROTOCOL_ONLY_NO_TARGET_DATA"
READINESS_DOMAINS = (
    "PARTICIPANT_SCOPE_AND_NONINTERFERENCE",
    "CONTROLLED_HARNESS_DEPLOYMENT_AND_RUNTIME",
    "IMMUTABLE_WORM_STORE",
    "DESTRUCTIVE_GAP_ACCEPTANCE",
    "BROKER_CUSTODY_AND_CAPTURE_REPLAY",
    "CLASSIFIER_CLOSURE",
    "EXPERIMENTER_NONINTERVENTION",
)
FORBIDDEN_DATA_KEYS = {
    "clusters", "eligible_rows", "final_eligible_rows", "selected_rows",
    "selected_clusters", "candidate_identities", "statement", "statement_text",
    "declarations", "candidates", "target_rankings", "target_semantics",
    "residual", "proof_route", "outcomes", "target_identity", "target_identities",
}
SCHEMA_CONTAINER_KEYS = {"properties", "definitions", "$defs", "patternProperties"}
STRUCTURAL_STATEMENT_ROLES = {"immutable_infrastructure_cloudformation"}
DOMAIN_STATUSES = {
    "PARTICIPANT_SCOPE_AND_NONINTERFERENCE": "CANDIDATE_C_PARTICIPANT_NONINTERFERENCE_ACCEPTED",
    "CONTROLLED_HARNESS_DEPLOYMENT_AND_RUNTIME": "CANDIDATE_C_CONTROLLED_HARNESS_ACCEPTED",
    "IMMUTABLE_WORM_STORE": "CANDIDATE_C_IMMUTABLE_WORM_ACCEPTED",
    "DESTRUCTIVE_GAP_ACCEPTANCE": "CANDIDATE_C_DESTRUCTIVE_GAP_ACCEPTED",
    "BROKER_CUSTODY_AND_CAPTURE_REPLAY": "CANDIDATE_C_BROKER_CUSTODY_CAPTURE_REPLAY_ACCEPTED",
    "CLASSIFIER_CLOSURE": "CANDIDATE_C_CLASSIFIER_CLOSURE_ACCEPTED",
    "EXPERIMENTER_NONINTERVENTION": "CANDIDATE_C_EXPERIMENTER_NONINTERVENTION_ACCEPTED",
}

IsolatedEvidenceRunner = Callable[
    [Path, list[str], dict[str, str], int], subprocess.CompletedProcess[bytes]
]


class CandidateBaseError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def domain_digest(domain: str, value: Any) -> str:
    return sha256(domain.encode("ascii") + b"\x00" + canonical_json(value))


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CandidateBaseError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateBaseError(f"{label} is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CandidateBaseError(f"{label} must be a JSON object")
    return value


def schema_validate(value: Any, schema: dict[str, Any], label: str) -> None:
    try:
        jsonschema.Draft7Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        raise CandidateBaseError(f"{label} schema is invalid: {exc.message}") from exc
    errors = sorted(
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in errors
        )
        raise CandidateBaseError(f"{label} schema validation failed: {detail}")


def normalized_repo_path(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise CandidateBaseError(f"{label} must be a string")
    pure = PurePosixPath(value)
    if not pure.parts or pure.is_absolute() or ".." in pure.parts or pure.as_posix() != value:
        raise CandidateBaseError(f"{label} must be normalized and repository-relative")
    return value


class GitRepository:
    def __init__(self, root: Path):
        self.root = root.resolve()
        if not (self.root / ".git").exists():
            raise CandidateBaseError(f"repository is not a Git worktree: {self.root}")

    def run(self, *args: str) -> bytes:
        env = {
            "PATH": "/usr/bin:/bin",
            "HOME": "/nonexistent",
            "LANG": "C",
            "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        try:
            return subprocess.run(
                ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never", "-C", str(self.root), *args],
                check=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            ).stdout
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.decode("utf-8", "replace").strip()
            raise CandidateBaseError(f"git {' '.join(args)} failed: {detail}") from exc

    def exact_commit(self, value: Any, label: str) -> str:
        if not isinstance(value, str) or OID.fullmatch(value) is None:
            raise CandidateBaseError(f"{label} must be an exact lowercase SHA-1 commit OID")
        resolved = self.run("rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
        if resolved != value:
            raise CandidateBaseError(f"{label} did not resolve exactly")
        return value

    def blob(self, commit: str, path: str) -> bytes:
        self.exact_commit(commit, "blob commit")
        normalized_repo_path(path, "blob path")
        return self.run("show", f"{commit}:{path}")

    def tree(self, commit: str) -> str:
        value = self.run("rev-parse", f"{commit}^{{tree}}").decode().strip()
        if OID.fullmatch(value) is None:
            raise CandidateBaseError("root tree is not an exact SHA-1 OID")
        return value

    def parents(self, commit: str) -> list[str]:
        return self.run("show", "-s", "--format=%P", commit).decode().split()

    def changed_paths(self, commit: str) -> list[str]:
        return self.run("diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        self.exact_commit(ancestor, "ancestor commit")
        self.exact_commit(descendant, "descendant commit")
        completed = subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(self.root), "merge-base", "--is-ancestor", ancestor, descendant],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"},
        )
        if completed.returncode not in (0, 1):
            raise CandidateBaseError("cannot evaluate exact Git ancestry")
        return completed.returncode == 0


def verify_public_remote(remote: str, ref: str, commit: str) -> bytes:
    if PUBLIC_REMOTE.fullmatch(remote) is None:
        raise CandidateBaseError("public remote is not the frozen c5-k4 GitHub repository")
    if PUBLIC_REF.fullmatch(ref) is None:
        raise CandidateBaseError("public ref must be a full heads/tags ref")
    env = {
        "PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
    }
    try:
        raw = subprocess.run(
            ["/usr/bin/git", "-c", "http.followRedirects=false", "ls-remote", "--refs", remote, ref],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, timeout=30,
        ).stdout.decode("ascii")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, UnicodeDecodeError) as exc:
        raise CandidateBaseError("cannot authenticate exact commit against the frozen public remote ref") from exc
    rows = [line.split("\t") for line in raw.splitlines() if line]
    if rows != [[commit, ref]]:
        raise CandidateBaseError("public remote ref does not advertise the required exact commit")
    return raw.encode("ascii")


def fetch_github_actions_run(run_id: int) -> dict[str, Any]:
    """Fetch one public Actions run without credentials or redirect authority."""
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id < 1:
        raise CandidateBaseError("GitHub Actions run_id must be a positive integer")
    url = f"https://api.github.com/repos/Kuberwastaken/c5-k4/actions/runs/{run_id}"
    command = [
        "/usr/bin/curl", "--silent", "--show-error", "--fail", "--proto", "=https",
        "--tlsv1.2", "--max-redirs", "0", "--connect-timeout", "10", "--max-time", "30",
        "--header", "Accept: application/vnd.github+json",
        "--header", "X-GitHub-Api-Version: 2022-11-28", url,
    ]
    try:
        completed = subprocess.run(
            command, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C"},
            timeout=35,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise CandidateBaseError("authenticated GitHub Actions run replay failed closed") from exc
    return strict_json(completed.stdout, "GitHub Actions run response")


def actions_run_projection(run: dict[str, Any]) -> dict[str, Any]:
    """Return only server-authenticated fields used as P1R freshness authority."""
    try:
        return {
            "id": run["id"], "run_attempt": run["run_attempt"], "event": run["event"],
            "status": run["status"], "conclusion": run["conclusion"], "head_sha": run["head_sha"],
            "path": run["path"], "head_branch": run["head_branch"], "created_at": run["created_at"],
            "run_started_at": run["run_started_at"], "updated_at": run["updated_at"],
            "repository": run["repository"]["full_name"],
            "head_repository": run["head_repository"]["full_name"],
        }
    except (KeyError, TypeError) as exc:
        raise CandidateBaseError("GitHub Actions run response lacks required authenticated fields") from exc


def verify_p1t_actions_observer(
    repo: GitRepository, candidate: str, p1t_commit: str, p1t_public_ref: str,
    observation: dict[str, Any],
) -> datetime:
    """Replay the public server-side run that establishes P1T observation time."""
    observer = observation["observer"]
    workflow_raw = repo.blob(candidate, P1T_OBSERVER_WORKFLOW_PATH)
    if (
        observer["workflow_path"] != P1T_OBSERVER_WORKFLOW_PATH
        or observer["workflow_blob_sha256"] != sha256(workflow_raw)
        or repo.blob(p1t_commit, P1T_OBSERVER_WORKFLOW_PATH) != workflow_raw
    ):
        raise CandidateBaseError("P1R observer workflow bytes are not frozen unchanged from exact C through P1T")
    run = actions_run_projection(fetch_github_actions_run(observer["run_id"]))
    derived_workflow_ref = f"{P1T_OBSERVER_WORKFLOW_PATH}@refs/heads/{run['head_branch']}"
    if (
        run["id"] != observer["run_id"] or run["run_attempt"] != 1 or observer["run_attempt"] != 1
        or run["repository"] != "Kuberwastaken/c5-k4" or run["head_repository"] != "Kuberwastaken/c5-k4"
        or run["event"] != "push" or run["status"] != "completed" or run["conclusion"] != "success"
        or run["head_sha"] != p1t_commit or run["path"] != P1T_OBSERVER_WORKFLOW_PATH
        or observer["workflow_repository"] != run["repository"]
        or observer["workflow_ref"] != derived_workflow_ref
        or p1t_public_ref != f"refs/heads/{run['head_branch']}"
        or observer["actions_run_projection_sha256"] != domain_digest(
            "c5k4-method-v1.5-p1t-actions-run-projection-1.0", run
        )
    ):
        raise CandidateBaseError("P1R observer does not replay an exact successful public P1T push run")
    created_at = _utc(run["created_at"], "Actions run created_at")
    started_at = _utc(run["run_started_at"], "Actions run run_started_at")
    observed_at = _utc(run["updated_at"], "Actions run updated_at")
    if created_at > started_at or started_at > observed_at or observation["observed_at_utc"] != run["updated_at"]:
        raise CandidateBaseError("P1R observed_at is not the authenticated GitHub server completion timestamp")
    return observed_at


def verify_p1r_publication_observer(
    repo: GitRepository, candidate: str, p1r_commit: str, public_ref: str,
    observer: dict[str, Any],
) -> tuple[dict[str, Any], datetime]:
    """Authenticate the external server-side publication event for P1R."""
    if public_ref != P1R_PUBLIC_REF:
        raise CandidateBaseError("P1R publication ref is not the frozen canonical branch")
    workflow_raw = repo.blob(candidate, P1R_OBSERVER_WORKFLOW_PATH)
    if (
        observer["workflow_path"] != P1R_OBSERVER_WORKFLOW_PATH
        or observer["workflow_blob_sha256"] != sha256(workflow_raw)
        or repo.blob(p1r_commit, P1R_OBSERVER_WORKFLOW_PATH) != workflow_raw
    ):
        raise CandidateBaseError("P1R publication observer workflow is not frozen unchanged from exact C")
    projection = actions_run_projection(fetch_github_actions_run(observer["run_id"]))
    expected_ref = f"{P1R_OBSERVER_WORKFLOW_PATH}@{P1R_PUBLIC_REF}"
    if (
        projection["id"] != observer["run_id"] or projection["run_attempt"] != 1
        or observer["run_attempt"] != 1 or projection["repository"] != "Kuberwastaken/c5-k4"
        or projection["head_repository"] != "Kuberwastaken/c5-k4" or projection["event"] != "push"
        or projection["status"] != "completed" or projection["conclusion"] != "success"
        or projection["head_sha"] != p1r_commit or projection["head_branch"] != "method-v1.5-p1r"
        or projection["path"] != P1R_OBSERVER_WORKFLOW_PATH
        or observer["workflow_repository"] != projection["repository"]
        or observer["workflow_ref"] != expected_ref
        or observer["actions_run_projection_sha256"] != domain_digest(
            "c5k4-method-v1.5-p1r-actions-run-projection-1.0", projection
        )
    ):
        raise CandidateBaseError("P1R publication observer is not an exact successful first-attempt canonical push run")
    created_at = _utc(projection["created_at"], "P1R Actions run created_at")
    started_at = _utc(projection["run_started_at"], "P1R Actions run run_started_at")
    observed_at = _utc(projection["updated_at"], "P1R Actions run updated_at")
    if created_at > started_at or started_at > observed_at or observer["server_observed_at_utc"] != projection["updated_at"]:
        raise CandidateBaseError("P1R activation time is not the authenticated GitHub server completion timestamp")
    return projection, observed_at


def literal_constant(raw: bytes, name: str, label: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(raw.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise CandidateBaseError(f"{label} is not parseable Python") from exc
    matches: list[Any] = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                try:
                    matches.append(ast.literal_eval(node.value))
                except (ValueError, TypeError) as exc:
                    raise CandidateBaseError(f"{label} {name} is not a literal") from exc
    if len(matches) != 1 or not isinstance(matches[0], tuple) or not matches[0]:
        raise CandidateBaseError(f"{label} must define exactly one nonempty literal {name} tuple")
    if any(not isinstance(row, str) or not row for row in matches[0]) or len(set(matches[0])) != len(matches[0]):
        raise CandidateBaseError(f"{label} {name} contains invalid or duplicate roles")
    return matches[0]


def _nonempty(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, (str, list, tuple, dict, set)):
        return bool(value)
    return True


def scan_target_data(
    value: Any, *, label: str, trail: tuple[str, ...] = (), allow_structural_statement: bool = False
) -> None:
    if isinstance(value, dict):
        inside_schema = any(part in SCHEMA_CONTAINER_KEYS for part in trail)
        for key, child in value.items():
            next_trail = (*trail, str(key))
            folded = str(key).casefold()
            structural = allow_structural_statement and folded == "statement"
            if folded in FORBIDDEN_DATA_KEYS and _nonempty(child) and not inside_schema and not structural:
                raise CandidateBaseError(f"{label} contains target-data field {'.'.join(next_trail)}")
            scan_target_data(child, label=label, trail=next_trail, allow_structural_statement=allow_structural_statement)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_target_data(child, label=label, trail=(*trail, str(index)), allow_structural_statement=allow_structural_statement)


def audit_json_blob(raw: bytes, role: str, *, schema_role: bool = False) -> None:
    value = strict_json(raw, role)
    if schema_role:
        try:
            jsonschema.Draft7Validator.check_schema(value)
        except jsonschema.SchemaError as exc:
            raise CandidateBaseError(f"{role} is not a valid Draft-07 schema: {exc.message}") from exc
    scan_target_data(value, label=role, allow_structural_statement=role in STRUCTURAL_STATEMENT_ROLES)


def ref_shape(value: Any, label: str) -> tuple[str, str]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise CandidateBaseError(f"{label} must contain exactly path and sha256")
    path = normalized_repo_path(value["path"], f"{label}.path")
    expected = value["sha256"]
    if not isinstance(expected, str) or SHA256.fullmatch(expected) is None:
        raise CandidateBaseError(f"{label}.sha256 is invalid")
    return path, expected


def bound_blob(repo: GitRepository, commit: str, ref: Any, label: str) -> tuple[str, bytes]:
    path, expected = ref_shape(ref, label)
    raw = repo.blob(commit, path)
    actual = sha256(raw)
    if actual != expected:
        raise CandidateBaseError(f"{label} digest mismatch at exact commit")
    return path, raw


def parse_source_refs(p0a: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any], bool]]:
    for role, ref in p0a["components"].items():
        yield f"components.{role}", ref, False
    for index, producer in enumerate(p0a["allowlisted_registry_producers"]):
        for field in ("executable", "invocation_contract", "input_schema", "output_schema"):
            yield f"allowlisted_registry_producers.{index}.{field}", producer[field], False
    for index, prototype in enumerate(p0a["prototype_artifacts"]):
        yield f"prototype_artifacts.{index}", prototype, True
    yield "target_data_audit_receipt", p0a["target_data_audit_receipt"], False


def compile_closures(repo: GitRepository, candidate: str, config_path: str, p0t_input: dict[str, str]) -> dict[str, Any]:
    builder_raw = repo.blob(candidate, P1_BUILDER_PATH)
    native_roles = literal_constant(builder_raw, "NATIVE_COMPONENTS", "candidate P1 builder")
    inherited_roles = literal_constant(builder_raw, "INHERITED_V1_4_ROLES", "candidate P1 builder")
    config = strict_json(repo.blob(candidate, config_path), "candidate P1 component config")
    if set(config) != {"schema_version", "authority", "components", "v1_4_p0a"}:
        raise CandidateBaseError("candidate P1 component config has an invalid shape")
    if config["schema_version"] != "c5k4-method-v1.5-p1-components-1.0" or config["authority"] != "AUTHORITATIVE_P1":
        raise CandidateBaseError("candidate P1 component config is not authoritative")
    components = config["components"]
    if not isinstance(components, dict) or set(components) != set(native_roles):
        raise CandidateBaseError("candidate native role set differs from exact candidate P1 builder")

    native: dict[str, Any] = {}
    native_rows: list[dict[str, Any]] = []
    audited_json_blobs: set[tuple[str, str]] = set()
    for role in native_roles:
        path, raw = bound_blob(repo, candidate, components[role], f"native.{role}")
        if path.endswith(".json"):
            audit_json_blob(raw, role, schema_role=role.endswith("_schema") or role == "p1_schema")
            audited_json_blobs.add((candidate, path))
        row = {"path": path, "sha256": sha256(raw), "content_class": NATIVE_CONTENT_CLASS}
        native[role] = row
        native_rows.append({"scope": "V1_5_NATIVE", "role": role, **row})

    p0a_path, p0a_at_c = bound_blob(repo, candidate, config["v1_4_p0a"], "v1.4 source P0A")
    p0t_commit = repo.exact_commit(p0t_input["commit"], "v1.4 P0T commit")
    p0t_path = normalized_repo_path(p0t_input["path"], "v1.4 P0T path")
    p0t_raw = repo.blob(p0t_commit, p0t_path)
    if repo.blob(candidate, p0t_path) != p0t_raw:
        raise CandidateBaseError("candidate C does not contain the authenticated P0T bytes")
    p0t = strict_json(p0t_raw, "v1.4 P0T")
    p1_schema = strict_json(repo.blob(candidate, P0_SCHEMA_PATH), "candidate v1.4 P0 schema")
    schema_validate(p0t, p1_schema, "v1.4 P0T")
    if p0t.get("artifact_kind") != "P0T" or p0t.get("protocol_version") != "1.4" or p0t.get("p0a") != config["v1_4_p0a"]:
        raise CandidateBaseError("v1.4 P0T does not authenticate the configured P0A")
    source_commit = repo.exact_commit(p0t.get("p0a_commit"), "v1.4 P0A source commit")
    if repo.parents(p0t_commit) != [source_commit] or repo.changed_paths(p0t_commit) != [p0t_path]:
        raise CandidateBaseError("v1.4 P0T is not a sole-parent one-path attestation of P0A")
    if repo.blob(source_commit, p0a_path) != p0a_at_c:
        raise CandidateBaseError("candidate P0A bytes differ from exact authenticated source commit")
    p0a = strict_json(p0a_at_c, "v1.4 P0A")
    source_schema = strict_json(repo.blob(source_commit, P0_SCHEMA_PATH), "source v1.4 P0 schema")
    schema_validate(p0a, source_schema, "v1.4 P0A")
    if p0a.get("artifact_kind") != "P0A" or p0a.get("authority") != "AUTHORITATIVE_P0" or p0a.get("protocol_version") != "1.4":
        raise CandidateBaseError("v1.4 source is not an authoritative P0A")
    if any(p0a.get(key) for key in ("final_eligible_rows", "selected_clusters", "target_semantics")):
        raise CandidateBaseError("v1.4 P0A contains forbidden target data")

    p0_builder_ref = p0a["components"].get("p0_builder")
    if not isinstance(p0_builder_ref, dict):
        raise CandidateBaseError("source P0A lacks p0_builder binding")
    p0_builder_path, p0_builder_raw = bound_blob(
        repo, source_commit,
        {"path": p0_builder_ref.get("path"), "sha256": p0_builder_ref.get("sha256")},
        "source p0_builder",
    )
    del p0_builder_path
    source_roles = literal_constant(p0_builder_raw, "REQUIRED_COMPONENTS", "source P0 builder")
    if set(p0a["components"]) != set(source_roles):
        raise CandidateBaseError("P0A source role set differs from its exact source P0 builder")
    if set(inherited_roles) - set(source_roles):
        raise CandidateBaseError("candidate inherited role set is absent from full P0A closure")

    source_rows: list[dict[str, Any]] = []
    source_blob_by_path: dict[str, bytes] = {}
    for location, ref, prototype in parse_source_refs(p0a):
        plain = {"path": ref.get("path"), "sha256": ref.get("sha256")} if isinstance(ref, dict) else ref
        path, raw = bound_blob(repo, source_commit, plain, f"source.{location}")
        if prototype:
            if ref.get("authority") != "PRE_P0_NOT_FREEZE" or ref.get("excluded_from_formal_build") is not True:
                raise CandidateBaseError(f"source.{location} is not an excluded prototype")
        elif location.startswith("components.") and ref.get("content_class") != SOURCE_CONTENT_CLASS:
            raise CandidateBaseError(f"source.{location} has wrong content class")
        if path.endswith(".json"):
            role = location.split(".")[-1]
            audit_json_blob(raw, f"source.{location}", schema_role=role.endswith("_schema"))
            audited_json_blobs.add((source_commit, path))
        source_blob_by_path[path] = raw
        source_rows.append({"location": location, "path": path, "sha256": sha256(raw)})

    receipt_path, _ = ref_shape(p0a["target_data_audit_receipt"], "target data audit receipt")
    audit = strict_json(source_blob_by_path[receipt_path], "v1.4 target-data audit receipt")
    expected_audit_rows = [
        {"role": role, "path": p0a["components"][role]["path"], "sha256": p0a["components"][role]["sha256"], "classification": SOURCE_CONTENT_CLASS}
        for role in source_roles
    ]
    if (
        audit.get("schema_version") != "c5k4-method-v1.4-target-data-audit-receipt-1.0"
        or audit.get("audit_rule_sha256") != p0a["components"]["target_data_audit_rule"]["sha256"]
        or audit.get("components") != expected_audit_rows
        or any(audit.get(field) != 0 for field in ("final_eligible_rows_detected", "selected_clusters_detected", "statement_text_detected", "semantic_target_analysis_detected"))
    ):
        raise CandidateBaseError("P0A target-data audit receipt is not the exact zero-detection full closure")

    inherited: dict[str, Any] = {}
    inherited_rows: list[dict[str, Any]] = []
    for role in inherited_roles:
        ref = p0a["components"][role]
        raw = repo.blob(source_commit, ref["path"])
        row = {
            "path": ref["path"], "sha256": sha256(raw), "source_commit": source_commit,
            "content_class": INHERITED_CONTENT_CLASS, "source_content_class": SOURCE_CONTENT_CLASS,
        }
        inherited[role] = row
        inherited_rows.append({"scope": "V1_4_INHERITED", "role": role, **row})

    native_sha = domain_digest("c5k4-method-v1.5-candidate-base-native-closure-1.0", native_rows)
    inherited_sha = domain_digest("c5k4-method-v1.5-candidate-base-inherited-closure-1.0", inherited_rows)
    source_sha = domain_digest("c5k4-method-v1.5-candidate-base-full-source-closure-1.0", source_rows)
    aggregate_sha = domain_digest("c5k4-method-v1.5-candidate-base-closure-1.0", {
        "native_sha256": native_sha, "inherited_sha256": inherited_sha, "full_source_sha256": source_sha,
    })
    audit_rows = native_rows + inherited_rows
    expected_p1a = {
        "schema_version": "c5k4-method-v1.5-p1-1.0", "artifact_kind": "P1A", "authority": "AUTHORITATIVE_P1",
        "protocol_version": PROTOCOL, "components": native,
        "inherited_v1_4": {
            "source_p0a": config["v1_4_p0a"], "source_p0t": {"path": p0t_path, "sha256": sha256(p0t_raw)},
            "source_p0a_commit": source_commit, "source_protocol_version": "1.4",
            "selected_roles": list(inherited_roles), "components": inherited,
            "closure_policy": {"source_p0a_must_validate": True, "roles_selected_by_assembler": True, "manual_digest_copy_forbidden": True, "all_selected_files_revalidated": True},
        },
        "target_data_audit": {
            "algorithm": "STRICT_ROLE_MAP_DIGEST_AND_STRUCTURAL_TARGET_DATA_AUDIT_V1_5",
            "native_component_count": len(native_roles), "inherited_component_count": len(inherited_roles),
            "audited_bindings_sha256": sha256(canonical_json(audit_rows)),
            "candidate_identities_detected": 0, "statement_text_detected": 0,
            "target_rankings_detected": 0, "target_semantic_analysis_detected": 0,
        },
        "chronology_capture": {"allowed_u1_capture_count": 1, "requires_public_p1r_receipt": True, "p1t_alone_activation_permitted": False, "entropy_permitted": False, "selection_permitted": False},
        "prohibitions": {"candidate_identities": True, "statement_text": True, "target_ranking": True, "target_semantic_analysis": True, "entropy": True, "selection": True},
        "candidate_identities": [], "statement_text": [], "target_rankings": [], "target_semantics": [],
    }
    return {
        "native_rows": native_rows, "inherited_rows": inherited_rows, "source_rows": source_rows,
        "native_sha256": native_sha, "inherited_sha256": inherited_sha,
        "full_source_sha256": source_sha, "aggregate_sha256": aggregate_sha,
        "source_commit": source_commit, "p0t_commit": p0t_commit,
        "json_blob_count": len(audited_json_blobs),
        "expected_p1a": expected_p1a,
    }


def _utc(value: str, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise CandidateBaseError(f"{label} must be an exact UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise CandidateBaseError(f"{label} is not a valid timestamp") from exc
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise CandidateBaseError(f"{label} is not UTC")
    return parsed


def _without(value: dict[str, Any], *fields: str) -> dict[str, Any]:
    result = dict(value)
    for field in fields:
        result.pop(field, None)
    return result


def decode_embedded_json(envelope: Any, label: str) -> tuple[dict[str, Any], bytes]:
    if not isinstance(envelope, dict) or set(envelope) != {"encoding", "canonical_json_base64", "sha256"}:
        raise CandidateBaseError(f"{label} has an invalid embedded-JSON envelope")
    if envelope["encoding"] != "BASE64_CANONICAL_JSON_UTF8":
        raise CandidateBaseError(f"{label} encoding is not canonical JSON")
    try:
        raw = base64.b64decode(envelope["canonical_json_base64"], validate=True)
    except ValueError as exc:
        raise CandidateBaseError(f"{label} is not valid base64") from exc
    if sha256(raw) != envelope["sha256"]:
        raise CandidateBaseError(f"{label} byte digest mismatch")
    value = strict_json(raw, label)
    if raw != canonical_json(value):
        raise CandidateBaseError(f"{label} bytes are not canonical JSON")
    return value, raw


def decode_p1_readiness_package(envelope: Any) -> tuple[dict[str, Any], bytes]:
    expected_fields = {
        "schema", "status", "encoding", "canonical_package_base64", "package_sha256",
        "assembler_verification_scope", "activation_authority",
    }
    if not isinstance(envelope, dict) or set(envelope) != expected_fields:
        raise CandidateBaseError("P1A readiness package has an invalid closed envelope")
    if (
        envelope["schema"] != "c5k4-method-v1.5-p1-embedded-readiness-package-1.0"
        or envelope["status"] != "SIGNED_TARGET_BLIND_READINESS_AWAITING_PUBLIC_P1R"
        or envelope["encoding"] != "BASE64_CANONICAL_JSON_UTF8"
        or envelope["assembler_verification_scope"] != "STRUCTURAL_CANONICAL_PACKAGE_ONLY_CRYPTO_UNVERIFIED_AWAITING_PUBLIC_P1R"
        or envelope["activation_authority"] is not False
    ):
        raise CandidateBaseError("P1A readiness package envelope semantics differ from frozen structural-only contract")
    try:
        raw = base64.b64decode(envelope["canonical_package_base64"], validate=True)
    except ValueError as exc:
        raise CandidateBaseError("P1A readiness package is not valid base64") from exc
    if sha256(raw) != envelope["package_sha256"]:
        raise CandidateBaseError("P1A readiness package byte digest mismatch")
    value = strict_json(raw, "P1A readiness package")
    if raw != canonical_json(value):
        raise CandidateBaseError("P1A readiness package bytes are not canonical JSON")
    return value, raw


def signature_message(domain: str, digest: str) -> bytes:
    if SHA256.fullmatch(digest) is None:
        raise CandidateBaseError("signature payload digest is invalid")
    return domain.encode("ascii") + b"\x00" + bytes.fromhex(digest)


def verify_ed25519(raw_key: bytes, signature_text: str, message: bytes, label: str) -> None:
    try:
        signature = base64.b64decode(signature_text, validate=True)
        if len(signature) != 64:
            raise ValueError("wrong signature length")
        Ed25519PublicKey.from_public_bytes(raw_key).verify(signature, message)
    except (ValueError, InvalidSignature) as exc:
        raise CandidateBaseError(f"{label} signature verification failed") from exc


def compiler_refs_v2(repo: GitRepository, candidate: str) -> dict[str, dict[str, str]]:
    paths = {
        "validator": VALIDATOR_PATH,
        "input_schema": INPUT_SCHEMA_PATH,
        "output_schema": OUTPUT_SCHEMA_PATH,
        "authority_root_schema": AUTHORITY_SCHEMA_PATH,
        "operational_evidence_schema": EVIDENCE_SCHEMA_PATH,
        "independent_recompile_schema": RECOMPILE_SCHEMA_PATH,
        "readiness_package_schema": PACKAGE_SCHEMA_PATH,
        "p1r_schema": P1R_SCHEMA_PATH,
        "activation_receipt_schema": ACTIVATION_RECEIPT_SCHEMA_PATH,
        "isolated_evidence_runner": ISOLATED_RUNNER_PATH,
        "isolated_evidence_runner_schema": ISOLATED_RUNNER_SCHEMA_PATH,
        "isolated_evidence_runner_contract": ISOLATED_RUNNER_CONTRACT_PATH,
        "isolated_evidence_runner_test": ISOLATED_RUNNER_TEST_PATH,
    }
    return {name: {"path": path, "sha256": sha256(repo.blob(candidate, path))} for name, path in paths.items()}


def compiler_closure_sha256(refs: dict[str, dict[str, str]]) -> str:
    return domain_digest(
        "c5k4-method-v1.5-candidate-base-compiler-closure-1.0",
        [{"role": role, **refs[role]} for role in (
            "validator", "input_schema", "output_schema", "authority_root_schema",
            "operational_evidence_schema", "independent_recompile_schema",
            "readiness_package_schema", "p1r_schema", "activation_receipt_schema",
            "isolated_evidence_runner", "isolated_evidence_runner_schema",
            "isolated_evidence_runner_contract", "isolated_evidence_runner_test",
        )],
    )


def validate_isolated_runner_a0_binding(
    repo: GitRepository, candidate: str, authority: dict[str, Any],
) -> None:
    schema = strict_json(repo.blob(candidate, ISOLATED_RUNNER_SCHEMA_PATH), "candidate isolated-runner schema")
    contract = strict_json(repo.blob(candidate, ISOLATED_RUNNER_CONTRACT_PATH), "candidate isolated-runner contract")
    schema_validate(contract, schema, "candidate isolated-runner contract")
    if contract.get("operational") is not True or contract.get("status") != "EXACT_C_ISOLATED_EVIDENCE_RUNNER_OPERATIONAL":
        raise CandidateBaseError("exact-C isolated evidence runner is not operationally attested")
    daemon = contract.get("daemon")
    attestation = daemon.get("attestation") if isinstance(daemon, dict) else None
    harness = authority["controlled_harness"]
    if not isinstance(attestation, dict) or (
        attestation.get("signer_id") != harness["signer_id"]
        or attestation.get("verification_key_sha256") != harness["verification_key_sha256"]
    ):
        raise CandidateBaseError("isolated-runner daemon attestation is not bound to public-A0 controlled harness")
    if Path(__file__).resolve().parent.joinpath(Path(ISOLATED_RUNNER_PATH).name).read_bytes() != repo.blob(candidate, ISOLATED_RUNNER_PATH):
        raise CandidateBaseError("running isolated evidence runner bytes differ from exact candidate C")


def prove_running_validator_is_exact_c(repo: GitRepository, candidate: str) -> None:
    expected = repo.blob(candidate, VALIDATOR_PATH)
    running = Path(__file__).resolve().read_bytes()
    if running != expected:
        raise CandidateBaseError("running validator bytes differ from exact candidate C")


def validate_authority_root_v2(
    repo: GitRepository, authority_input: dict[str, Any], p0t_commit: str,
    candidate: str, public_remote_url: str,
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    a0 = repo.exact_commit(authority_input["commit"], "public authority-root commit A0")
    if a0 == candidate or not repo.is_ancestor(p0t_commit, a0) or not repo.is_ancestor(a0, candidate):
        raise CandidateBaseError("required historical order P0T -> A0 -> C is not exact ancestry")
    if len(repo.parents(a0)) > 1:
        raise CandidateBaseError("public authority-root A0 must not be a merge commit")
    tree = repo.tree(a0)
    if tree != authority_input["root_tree"]:
        raise CandidateBaseError("public authority-root tree differs from exact A0")
    verify_public_remote(public_remote_url, authority_input["public_remote_ref"], a0)
    path = normalized_repo_path(authority_input["path"], "authority-root path")
    raw = repo.blob(a0, path)
    schema = strict_json(repo.blob(a0, AUTHORITY_SCHEMA_PATH), "A0 authority-root schema")
    value = strict_json(raw, "public readiness authority root")
    schema_validate(value, schema, "public readiness authority root")
    recorded = value["authority_root_sha256"]
    actual = domain_digest(
        "c5k4-method-v1.5-public-readiness-authority-root-1.0",
        _without(value, "authority_root_sha256"),
    )
    if recorded != actual:
        raise CandidateBaseError("public authority-root self-digest mismatch")
    if repo.blob(candidate, path) != raw or repo.blob(candidate, AUTHORITY_SCHEMA_PATH) != repo.blob(a0, AUTHORITY_SCHEMA_PATH):
        raise CandidateBaseError("candidate C changed public A0 authority bytes/schema")
    if [row["domain"] for row in value["evidence_issuers"]] != list(READINESS_DOMAINS):
        raise CandidateBaseError("A0 evidence issuer domains are missing, duplicated, or out of order")
    if value["experimenters"] != sorted(value["experimenters"], key=lambda row: row["signer_id"]):
        raise CandidateBaseError("A0 experimenter authorities are not canonically ordered")
    if value["independent_recompilers"] != sorted(value["independent_recompilers"], key=lambda row: row["signer_id"]):
        raise CandidateBaseError("A0 independent-recompiler authorities are not canonically ordered")
    rows = [value["controlled_harness"], *value["experimenters"], *value["evidence_issuers"], *value["independent_recompilers"]]
    signer_ids = [row["signer_id"] for row in rows]
    key_hashes = [row["verification_key_sha256"] for row in rows]
    if len(signer_ids) != len(set(signer_ids)) or len(key_hashes) != len(set(key_hashes)):
        raise CandidateBaseError("all A0 signer IDs and verification-key hashes must be globally unique")
    binding = {"commit": a0, "root_tree": tree, "path": path, "sha256": sha256(raw)}
    return value, binding, raw


def authority_rows(authority: dict[str, Any]) -> list[dict[str, Any]]:
    return [authority["controlled_harness"], *authority["experimenters"], *authority["evidence_issuers"], *authority["independent_recompilers"]]


def load_verification_keys(authority: dict[str, Any], rows: list[dict[str, str]]) -> dict[tuple[str, str], bytes]:
    expected = {(row["signer_class"], row["signer_id"]): row["verification_key_sha256"] for row in authority_rows(authority)}
    supplied: dict[tuple[str, str], bytes] = {}
    supplied_hashes: set[str] = set()
    for row in rows:
        identity = (row["signer_class"], row["signer_id"])
        if identity in supplied:
            raise CandidateBaseError("duplicate verification-key signer class/identity")
        path = Path(row["path"])
        if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise CandidateBaseError("verification key must be a non-symlink regular file")
        raw = path.read_bytes()
        if len(raw) != 32:
            raise CandidateBaseError("Ed25519 verification key must contain exactly 32 raw bytes")
        key_sha = sha256(raw)
        if key_sha in supplied_hashes:
            raise CandidateBaseError("verification key bytes are reused across signer identities")
        supplied_hashes.add(key_sha)
        supplied[identity] = raw
    if set(supplied) != set(expected):
        raise CandidateBaseError("verification-key signer set differs from public A0")
    for identity, raw in supplied.items():
        if sha256(raw) != expected[identity]:
            raise CandidateBaseError("verification-key bytes differ from public A0 commitment")
    return supplied


def run_frozen_evidence_verifier(
    verifier_raw: bytes, verifier_sha: str, schema_raw: bytes, artifact_path: Path,
    artifact_sha: str, row: dict[str, Any],
    *, isolated_runner: IsolatedEvidenceRunner | None = None,
) -> None:
    """Run an exact-C verifier only through a separately proved isolation boundary.

    There is intentionally no direct-subprocess fallback.  The production
    caller remains fail-closed until the frozen Linux namespace backend can
    supply a runner that provides a private mount/PID/user/network namespace,
    no repository mount, a read-only input closure, and resource limits.
    """
    if isolated_runner is None:
        raise CandidateBaseError(
            "frozen evidence verifier replay is unavailable: proved isolated runner is not wired"
        )
    with tempfile.TemporaryDirectory(prefix="c5k4-v15-evidence-verifier-") as directory:
        root = Path(directory)
        inputs = root / "inputs"; inputs.mkdir(mode=0o755)
        verifier = inputs / "verifier.py"
        schema = inputs / "artifact.schema.json"
        artifact = inputs / "artifact.json"
        verifier.write_bytes(verifier_raw)
        schema.write_bytes(schema_raw)
        artifact.write_bytes(artifact_path.read_bytes())
        verifier.chmod(0o400); schema.chmod(0o400); artifact.chmod(0o400)
        command = [
            "/usr/local/bin/python3", "-I", "-S", "/inputs/verifier.py", "--candidate-readiness-verify",
            "--artifact", "/inputs/artifact.json", "--schema", "/inputs/artifact.schema.json",
            "--expected-status", row["accepted_status"], "--candidate", row["candidate_commit"],
            "--authority-root", row["authority_root_commit"], "--service-epoch", row["service_epoch_binding_sha256"],
            "--challenge-nonce", row["challenge_nonce"],
        ]
        try:
            completed = isolated_runner(
                root, command,
                {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/nonexistent", "TMPDIR": "/tmp",
                 "LANG": "C", "LC_ALL": "C", "PYTHONNOUSERSITE": "1",
                 "PYTHONHASHSEED": "0", "TZ": "UTC"},
                30,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise CandidateBaseError(f"frozen verifier failed for {row['domain']}") from exc
        if completed.returncode != 0:
            raise CandidateBaseError(f"frozen verifier failed for {row['domain']}")
        result = strict_json(completed.stdout, f"frozen verifier output for {row['domain']}")
        expected = {
            "status": "CANDIDATE_READINESS_EVIDENCE_VERIFIED",
            "artifact_sha256": artifact_sha,
            "verifier_sha256": verifier_sha,
        }
        if result != expected or completed.stdout != canonical_json(expected):
            raise CandidateBaseError(f"frozen verifier output contract failed for {row['domain']}")


def verify_operational_evidence(
    repo: GitRepository, candidate: str, authority_binding: dict[str, Any], authority: dict[str, Any],
    package_envelope: dict[str, Any], evidence_inputs: list[dict[str, str]], keys: dict[tuple[str, str], bytes],
    p1r_observed_at: datetime, isolated_runner: IsolatedEvidenceRunner | None,
) -> tuple[dict[str, Any], str, list[dict[str, str]]]:
    evidence, raw_bundle = decode_embedded_json(package_envelope, "operational evidence bundle")
    schema = strict_json(repo.blob(candidate, EVIDENCE_SCHEMA_PATH), "candidate operational-evidence schema")
    schema_validate(evidence, schema, "operational evidence bundle")
    recorded = evidence["bundle_sha256"]
    actual = domain_digest(
        "c5k4-method-v1.5-candidate-base-operational-evidence-1.0",
        _without(evidence, "bundle_sha256"),
    )
    if recorded != actual or sha256(raw_bundle) != package_envelope["sha256"]:
        raise CandidateBaseError("operational evidence bundle self-digest mismatch")
    if evidence["candidate"]["commit"] != candidate or evidence["candidate"]["root_tree"] != repo.tree(candidate):
        raise CandidateBaseError("operational evidence bundle does not bind exact C/tree")
    if evidence["authority_root"] != authority_binding:
        raise CandidateBaseError("operational evidence bundle does not bind exact public A0")
    if [row["domain"] for row in evidence["evidence"]] != list(READINESS_DOMAINS):
        raise CandidateBaseError("operational evidence domains are missing, duplicated, or out of order")
    if _utc(evidence["compiled_at_utc"], "evidence compiled_at") > p1r_observed_at or _utc(evidence["valid_through_utc"], "evidence valid_through") < p1r_observed_at:
        raise CandidateBaseError("operational evidence bundle is stale at public P1R observation")
    supplied = {row["domain"]: Path(row["path"]) for row in evidence_inputs}
    if len(supplied) != len(evidence_inputs) or set(supplied) != set(READINESS_DOMAINS):
        raise CandidateBaseError("evidence-object input domains are missing or duplicated")
    issuers = {row["domain"]: row for row in authority["evidence_issuers"]}
    nonces: set[str] = set()
    objects: set[tuple[str, str, str]] = set()
    verified_signers: list[dict[str, str]] = []
    for row in evidence["evidence"]:
        domain = row["domain"]
        if row["accepted_status"] != DOMAIN_STATUSES[domain]:
            raise CandidateBaseError(f"typed accepted status mismatch for {domain}")
        if (
            row["candidate_commit"] != candidate
            or row["authority_root_commit"] != authority_binding["commit"]
            or row["service_epoch_binding_sha256"] != evidence["service_epoch_binding_sha256"]
        ):
            raise CandidateBaseError(f"evidence row {domain} has a candidate/A0/epoch binding mismatch")
        if row["challenge_nonce"] in nonces:
            raise CandidateBaseError("operational evidence challenge nonce replay detected")
        nonces.add(row["challenge_nonce"])
        locator = row["artifact"]
        object_identity = (locator["bucket_arn"], locator["object_key"], locator["version_id"])
        if object_identity in objects:
            raise CandidateBaseError("immutable evidence object/version replay detected")
        objects.add(object_identity)
        observed = _utc(row["observed_at_utc"], f"{domain} observed_at")
        valid_through = _utc(row["valid_through_utc"], f"{domain} valid_through")
        retained_through = _utc(locator["retention_until_utc"], f"{domain} retention_until")
        if observed > p1r_observed_at or valid_through < p1r_observed_at or retained_through < p1r_observed_at or observed > valid_through:
            raise CandidateBaseError(f"evidence freshness/retention gap for {domain}")
        path = supplied[domain]
        if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            raise CandidateBaseError(f"evidence object for {domain} must be a non-symlink regular file")
        artifact_raw = path.read_bytes()
        if len(artifact_raw) != locator["size_bytes"] or sha256(artifact_raw) != locator["object_sha256"]:
            raise CandidateBaseError(f"evidence object bytes differ from immutable locator for {domain}")
        schema_path, schema_raw = bound_blob(repo, candidate, row["artifact_schema"], f"{domain} artifact schema")
        del schema_path
        artifact = strict_json(artifact_raw, f"{domain} evidence artifact")
        schema_validate(artifact, strict_json(schema_raw, f"{domain} evidence schema"), f"{domain} evidence artifact")
        if (
            artifact.get("status") != row["accepted_status"]
            or artifact.get("candidate_commit") != candidate
            or artifact.get("authority_root_commit") != authority_binding["commit"]
            or artifact.get("service_epoch_binding_sha256") != evidence["service_epoch_binding_sha256"]
            or artifact.get("challenge_nonce") != row["challenge_nonce"]
            or artifact.get("observed_at_utc") != row["observed_at_utc"]
            or artifact.get("valid_through_utc") != row["valid_through_utc"]
        ):
            raise CandidateBaseError(f"evidence artifact domain bindings/status differ for {domain}")
        digest_field = row["self_digest_field"]
        if artifact.get(digest_field) != domain_digest(
            row["self_digest_domain"], _without(artifact, digest_field, *row["self_digest_excluded_fields"])
        ):
            raise CandidateBaseError(f"evidence artifact self-digest mismatch for {domain}")
        verifier_path, verifier_raw = bound_blob(repo, candidate, row["frozen_verifier"], f"{domain} frozen verifier")
        del verifier_path
        run_frozen_evidence_verifier(
            verifier_raw, sha256(verifier_raw), schema_raw, path, sha256(artifact_raw), row,
            isolated_runner=isolated_runner,
        )
        issuer = issuers[domain]
        if row["issuer"] != {"signer_id": issuer["signer_id"], "verification_key_sha256": issuer["verification_key_sha256"]}:
            raise CandidateBaseError(f"evidence issuer differs from public A0 for {domain}")
        expected_acceptance = domain_digest(
            "c5k4-method-v1.5-candidate-base-operational-evidence-row-1.0",
            _without(row, "acceptance_sha256", "signature"),
        )
        if row["acceptance_sha256"] != expected_acceptance:
            raise CandidateBaseError(f"evidence-row acceptance self-digest mismatch for {domain}")
        identity = ("OPERATIONAL_EVIDENCE_ISSUER", issuer["signer_id"])
        verify_ed25519(
            keys[identity], row["signature"],
            signature_message("c5k4-method-v1.5-operational-evidence-row-signature-1.0", expected_acceptance),
            f"evidence issuer {domain}",
        )
        verified_signers.append({"signer_class": identity[0], "signer_id": identity[1], "verification_key_sha256": issuer["verification_key_sha256"]})
    return evidence, actual, verified_signers


def readiness_payload_source(package: dict[str, Any]) -> dict[str, Any]:
    return {
        key: package[key]
        for key in ("schema", "status", "protocol_version", "candidate", "authority_root", "closures", "operational_evidence", "compiler", "structural_json_key_audit")
    }


def verify_readiness_package_v2(
    repo: GitRepository, candidate: str, authority: dict[str, Any], authority_binding: dict[str, Any],
    closures: dict[str, Any], embedded_package: dict[str, Any], evidence_inputs: list[dict[str, str]],
    keys: dict[tuple[str, str], bytes], p1r_observed_at: datetime,
    isolated_runner: IsolatedEvidenceRunner | None,
) -> tuple[dict[str, Any], list[dict[str, str]], str]:
    package, package_raw = decode_p1_readiness_package(embedded_package)
    package_schema = strict_json(repo.blob(candidate, PACKAGE_SCHEMA_PATH), "candidate readiness-package schema")
    schema_validate(package, package_schema, "P1A readiness package")
    expected_package_digest = domain_digest(
        "c5k4-method-v1.5-candidate-base-readiness-package-1.0", _without(package, "package_sha256")
    )
    if package["package_sha256"] != expected_package_digest or embedded_package["package_sha256"] != sha256(package_raw):
        raise CandidateBaseError("P1A readiness package self/byte digest mismatch")
    if package["candidate"] != {"commit": candidate, "root_tree": repo.tree(candidate)} or package["authority_root"] != authority_binding:
        raise CandidateBaseError("readiness package does not bind exact C/tree/public A0")
    expected_closures = {
        "native": {"row_count": len(closures["native_rows"]), "sha256": closures["native_sha256"]},
        "inherited": {"row_count": len(closures["inherited_rows"]), "sha256": closures["inherited_sha256"]},
        "full_source": {"row_count": len(closures["source_rows"]), "sha256": closures["full_source_sha256"]},
        "aggregate_sha256": closures["aggregate_sha256"],
    }
    if package["closures"] != expected_closures:
        raise CandidateBaseError("readiness package closure differs from exact C/P0A Git-object recompile")
    expected_compiler = compiler_refs_v2(repo, candidate)
    if package["compiler"] != expected_compiler:
        raise CandidateBaseError("readiness package compiler/schema closure differs from exact C")
    expected_audit = {
        "algorithm": "STRUCTURAL_JSON_KEY_AUDIT_V1_5",
        "scope": ["V1_5_NATIVE_JSON_BLOBS", "V1_4_SELECTED_INHERITED_JSON_BLOBS", "V1_4_FULL_P0A_REFERENCED_JSON_BLOBS"],
        "json_blob_count": closures["json_blob_count"],
        "candidate_identities_keys_detected": 0, "statement_text_keys_detected": 0,
        "target_rankings_keys_detected": 0, "target_semantic_analysis_keys_detected": 0,
        "does_not_claim_free_text_or_python_semantic_audit": True,
    }
    if package["structural_json_key_audit"] != expected_audit:
        raise CandidateBaseError("readiness package overstates or differs from performed structural JSON-key audit")
    evidence, evidence_sha, evidence_signers = verify_operational_evidence(
        repo, candidate, authority_binding, authority, package["operational_evidence"], evidence_inputs,
        keys, p1r_observed_at, isolated_runner
    )
    payload_sha = domain_digest("c5k4-method-v1.5-candidate-base-readiness-payload-2.0", readiness_payload_source(package))
    if package["payload_sha256"] != payload_sha:
        raise CandidateBaseError("readiness common payload digest mismatch")
    expected_authority_signers = {
        ("CONTROLLED_HARNESS_READINESS_KEY", authority["controlled_harness"]["signer_id"]): authority["controlled_harness"]["verification_key_sha256"],
        **{("FROZEN_EXPERIMENTER_IDENTITY", row["signer_id"]): row["verification_key_sha256"] for row in authority["experimenters"]},
    }
    observed_authority_signatures: dict[tuple[str, str], dict[str, Any]] = {}
    for row in package["authority_signatures"]:
        identity = (row["signer_class"], row["signer_id"])
        if identity in observed_authority_signatures:
            raise CandidateBaseError("duplicate readiness authority signature")
        observed_authority_signatures[identity] = row
    if set(observed_authority_signatures) != set(expected_authority_signers):
        raise CandidateBaseError("readiness authority signature set differs from public A0")
    verified_signers = list(evidence_signers)
    for identity, key_sha in expected_authority_signers.items():
        row = observed_authority_signatures[identity]
        if row["verification_key_sha256"] != key_sha:
            raise CandidateBaseError("readiness authority signature key differs from public A0")
        verify_ed25519(
            keys[identity], row["signature"],
            signature_message("c5k4-method-v1.5-candidate-base-readiness-signature-2.0", payload_sha),
            f"readiness authority {identity[1]}",
        )
        verified_signers.append({"signer_class": identity[0], "signer_id": identity[1], "verification_key_sha256": key_sha})
    recompile_schema = strict_json(repo.blob(candidate, RECOMPILE_SCHEMA_PATH), "candidate independent-recompile schema")
    allowed_recompilers = {row["signer_id"]: row for row in authority["independent_recompilers"]}
    signer_ids: set[str] = set()
    key_hashes: set[str] = set()
    execution_ids: set[str] = set()
    host_ids: set[str] = set()
    compiler_sha = compiler_closure_sha256(expected_compiler)
    for index, envelope in enumerate(package["independent_recompiles"]):
        attestation, _ = decode_embedded_json(envelope, f"independent recompile {index}")
        schema_validate(attestation, recompile_schema, f"independent recompile {index}")
        expected_attestation_sha = domain_digest(
            "c5k4-method-v1.5-candidate-base-independent-recompile-1.0",
            _without(attestation, "attestation_sha256", "signature"),
        )
        if attestation["attestation_sha256"] != expected_attestation_sha:
            raise CandidateBaseError("independent recompile self-digest mismatch")
        if (
            attestation["payload_sha256"] != payload_sha
            or attestation["closure_aggregate_sha256"] != closures["aggregate_sha256"]
            or attestation["operational_evidence_bundle_sha256"] != evidence_sha
            or attestation["authority_root_commit"] != authority_binding["commit"]
            or attestation["authority_root_sha256"] != authority_binding["sha256"]
            or attestation["compiler_closure_sha256"] != compiler_sha
            or attestation["validator_sha256"] != expected_compiler["validator"]["sha256"]
        ):
            raise CandidateBaseError("independent recompile does not attest the identical common payload/closure")
        signer = attestation["signer"]
        frozen = allowed_recompilers.get(signer["signer_id"])
        if frozen is None or signer != frozen:
            raise CandidateBaseError("independent recompiler differs from public A0")
        if _utc(attestation["completed_at_utc"], "recompile completed_at") > p1r_observed_at:
            raise CandidateBaseError("independent recompile postdates public P1R observation")
        if signer["signer_id"] in signer_ids or signer["verification_key_sha256"] in key_hashes or attestation["execution_id"] in execution_ids or attestation["execution_host_id"] in host_ids:
            raise CandidateBaseError("independent recompiles do not have distinct signer/key/execution/host identities")
        signer_ids.add(signer["signer_id"]); key_hashes.add(signer["verification_key_sha256"])
        execution_ids.add(attestation["execution_id"]); host_ids.add(attestation["execution_host_id"])
        identity = ("INDEPENDENT_RECOMPILER", signer["signer_id"])
        verify_ed25519(
            keys[identity], attestation["signature"],
            signature_message("c5k4-method-v1.5-independent-recompile-signature-1.0", expected_attestation_sha),
            f"independent recompiler {signer['signer_id']}",
        )
        verified_signers.append({"signer_class": identity[0], "signer_id": identity[1], "verification_key_sha256": signer["verification_key_sha256"]})
    if len(signer_ids) < 2:
        raise CandidateBaseError("at least two distinct public-A0-anchored independent recompiles are required")
    return package, sorted(verified_signers, key=lambda row: (row["signer_class"], row["signer_id"])), evidence_sha


def validate_p1_chain_v2(
    repo: GitRepository, candidate: str, transition: dict[str, Any], closures: dict[str, Any],
    authority_input: dict[str, Any], p0t_input: dict[str, Any], public_remote_url: str,
    candidate_public_ref: str,
) -> tuple[dict[str, Any], dict[str, Any], datetime, dict[str, str]]:
    p1a_commit = repo.exact_commit(transition["p1a_commit"], "P1A commit")
    p1t_commit = repo.exact_commit(transition["p1t_commit"], "P1T commit")
    p1r_commit = repo.exact_commit(transition["p1r_commit"], "P1R commit")
    if repo.parents(p1a_commit) != [candidate] or repo.changed_paths(p1a_commit) != [P1A_PATH]:
        raise CandidateBaseError("P1A is not the exact sole-parent one-path child of C")
    if repo.parents(p1t_commit) != [p1a_commit] or repo.changed_paths(p1t_commit) != [P1T_PATH]:
        raise CandidateBaseError("P1T is not the exact sole-parent one-path child of P1A")
    if repo.parents(p1r_commit) != [p1t_commit] or repo.changed_paths(p1r_commit) != [P1R_PATH]:
        raise CandidateBaseError("P1R is not the exact sole-parent one-path child of P1T")
    p1a_raw = repo.blob(p1a_commit, P1A_PATH)
    p1t_raw = repo.blob(p1t_commit, P1T_PATH)
    p1r_raw = repo.blob(p1r_commit, P1R_PATH)
    p1_schema = strict_json(repo.blob(candidate, P1_SCHEMA_PATH), "candidate P1 schema")
    p1r_schema = strict_json(repo.blob(candidate, P1R_SCHEMA_PATH), "candidate P1R schema")
    p1a = strict_json(p1a_raw, "P1A"); schema_validate(p1a, p1_schema, "P1A")
    p1t = strict_json(p1t_raw, "P1T"); schema_validate(p1t, p1_schema, "P1T")
    p1r = strict_json(p1r_raw, "P1R"); schema_validate(p1r, p1r_schema, "P1R")
    expected_p1a = dict(closures["expected_p1a"])
    expected_p1a["candidate_base_readiness"] = p1a["candidate_base_readiness"]
    if p1a != expected_p1a:
        raise CandidateBaseError("committed P1A differs from exact C/P0A closure plus embedded readiness package")
    if (
        p1t["p1a_commit"] != p1a_commit or p1t["p1a"] != {"path": P1A_PATH, "sha256": sha256(p1a_raw)}
        or p1t["attestation_policy"]["allowed_p1t_changed_paths"] != [P1T_PATH]
    ):
        raise CandidateBaseError("P1T does not authenticate exact P1A bytes")
    if p1r["p1t_commit"] != p1t_commit or p1r["p1t"] != {"path": P1T_PATH, "sha256": sha256(p1t_raw)}:
        raise CandidateBaseError("P1R does not authenticate exact P1T bytes")
    observation = p1r["observation"]
    expected_observed = {
        "authority_root": {"ref": authority_input["public_remote_ref"], "commit": authority_input["commit"]},
        "v1_4_p0t": {"ref": p0t_input["public_remote_ref"], "commit": p0t_input["commit"]},
        "candidate_c": {"ref": candidate_public_ref, "commit": candidate},
        "p1t": {"ref": transition["p1t_public_remote_ref"], "commit": p1t_commit},
    }
    if any(observation[key] != value for key, value in expected_observed.items()):
        raise CandidateBaseError("P1R observation does not bind exact public A0/P0T/C/P1T refs")
    raw_rows = [
        verify_public_remote(public_remote_url, authority_input["public_remote_ref"], authority_input["commit"]),
        verify_public_remote(public_remote_url, p0t_input["public_remote_ref"], p0t_input["commit"]),
        verify_public_remote(public_remote_url, observation["candidate_c"]["ref"], candidate),
        verify_public_remote(public_remote_url, transition["p1t_public_remote_ref"], p1t_commit),
    ]
    if observation["ls_remote_stdout_sha256"] != sha256(b"".join(raw_rows)):
        raise CandidateBaseError("P1R public observation transcript/candidate binding mismatch")
    observed_at = verify_p1t_actions_observer(
        repo, candidate, p1t_commit, transition["p1t_public_remote_ref"], observation
    )
    verify_public_remote(public_remote_url, transition["p1r_public_remote_ref"], p1r_commit)
    return p1a, p1r, observed_at, {
        "p1a_commit": p1a_commit, "p1t_commit": p1t_commit, "p1r_commit": p1r_commit,
        "p1r_root_tree": repo.tree(p1r_commit), "p1r_public_remote_ref": transition["p1r_public_remote_ref"],
    }


def compile_diagnostic(
    repository: Path, request: dict[str, Any], request_raw: bytes,
    *, isolated_runner: IsolatedEvidenceRunner | None = None,
) -> dict[str, Any]:
    repo = GitRepository(repository)
    if not isinstance(request, dict) or not isinstance(request.get("candidate"), dict):
        raise CandidateBaseError("validation input lacks a candidate object")
    candidate = repo.exact_commit(request["candidate"].get("commit"), "candidate C")
    input_schema = strict_json(repo.blob(candidate, INPUT_SCHEMA_PATH), "candidate validation input schema")
    schema_validate(request, input_schema, "candidate validation input")
    prove_running_validator_is_exact_c(repo, candidate)
    candidate_input = request["candidate"]
    if repo.tree(candidate) != candidate_input["root_tree"] or len(repo.parents(candidate)) > 1:
        raise CandidateBaseError("candidate C tree/merge status is invalid")
    verify_public_remote(candidate_input["public_remote_url"], candidate_input["public_remote_ref"], candidate)
    p0t = repo.exact_commit(request["v1_4_p0t"]["commit"], "public v1.4 P0T commit")
    if repo.tree(p0t) != request["v1_4_p0t"]["root_tree"] or not repo.is_ancestor(p0t, candidate):
        raise CandidateBaseError("v1.4 P0T is not an exact ancestor of C")
    verify_public_remote(candidate_input["public_remote_url"], request["v1_4_p0t"]["public_remote_ref"], p0t)
    closures = compile_closures(repo, candidate, candidate_input["component_config_path"], request["v1_4_p0t"])
    if closures["p0t_commit"] != p0t or not repo.is_ancestor(closures["source_commit"], p0t):
        raise CandidateBaseError("P0A/P0T source chain differs from closure compiler")
    authority, authority_binding, _ = validate_authority_root_v2(
        repo, request["authority_root"], p0t, candidate, candidate_input["public_remote_url"]
    )
    if isolated_runner is not None:
        validate_isolated_runner_a0_binding(repo, candidate, authority)
    keys = load_verification_keys(authority, request["verification_keys"])
    p1a, _p1r, observed_at, transition = validate_p1_chain_v2(
        repo, candidate, request["p1_transition"], closures, request["authority_root"],
        request["v1_4_p0t"], candidate_input["public_remote_url"], candidate_input["public_remote_ref"]
    )
    package, verified_signers, evidence_sha = verify_readiness_package_v2(
        repo, candidate, authority, authority_binding, closures, p1a["candidate_base_readiness"],
        request["evidence_objects"], keys, observed_at, isolated_runner,
    )
    _projection, p1r_publication_at = verify_p1r_publication_observer(
        repo, candidate, transition["p1r_commit"], transition["p1r_public_remote_ref"],
        request["p1r_publication_observer"],
    )
    if p1r_publication_at < observed_at:
        raise CandidateBaseError("P1R publication observation predates its internal public P1T observation")
    output = {
        "schema": "c5k4-method-v1.5-candidate-base-validation-output-2.0",
        "status": "LOCAL_NONAUTHORITATIVE_REPLAY_VERIFIED", "protocol_version": PROTOCOL,
        "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
        "authority_root": {"commit": authority_binding["commit"], "root_tree": authority_binding["root_tree"]},
        "candidate": {"commit": candidate, "root_tree": repo.tree(candidate)},
        "closures": package["closures"], "readiness_package_sha256": package["package_sha256"],
        "operational_evidence_bundle_sha256": evidence_sha, "verified_signers": verified_signers,
        "p1_transition": transition,
        "p1r_publication_observation": request["p1r_publication_observer"],
        "validation_inputs_sha256": sha256(request_raw),
    }
    output["diagnostic_sha256"] = domain_digest(
        "c5k4-method-v1.5-candidate-base-validation-output-2.0", output
    )
    output_schema = strict_json(repo.blob(candidate, OUTPUT_SCHEMA_PATH), "candidate validation output schema")
    validate_diagnostic(output, output_schema)
    return output


def validate_diagnostic(value: dict[str, Any], schema: dict[str, Any]) -> None:
    schema_validate(value, schema, "candidate validation diagnostic")
    recorded = value["diagnostic_sha256"]
    if recorded != domain_digest(
        "c5k4-method-v1.5-candidate-base-validation-output-2.0", _without(value, "diagnostic_sha256")
    ):
        raise CandidateBaseError("candidate validation diagnostic self-digest mismatch")


def read_immutable_validation_input(path: Path, expected_sha256: str) -> bytes:
    """Read one non-writable, non-symlink input through an O_NOFOLLOW fd."""
    if SHA256.fullmatch(expected_sha256) is None:
        raise CandidateBaseError("validation input digest must be exact lowercase SHA-256")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CandidateBaseError("immutable validation input cannot be opened safely") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_mode & 0o222:
            raise CandidateBaseError("validation input must be a singly-linked non-writable regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    if identity(before) != identity(after):
        raise CandidateBaseError("validation input changed during immutable read")
    raw = b"".join(chunks)
    if len(raw) != before.st_size or sha256(raw) != expected_sha256:
        raise CandidateBaseError("validation input bytes differ from the frozen digest")
    return raw


def activation_receipt_digest(value: dict[str, Any]) -> str:
    return domain_digest(
        "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
        _without(value, "receipt_sha256"),
    )


def load_frozen_isolated_evidence_runner() -> IsolatedEvidenceRunner:
    """Load only the fixed sibling backend; no caller path or callable exists."""
    path = Path(__file__).resolve().parent / Path(ISOLATED_RUNNER_PATH).name
    spec = importlib.util.spec_from_file_location("c5k4_v15_fixed_isolated_evidence_runner", path)
    if spec is None or spec.loader is None:
        raise CandidateBaseError("frozen isolated evidence runner cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as exc:
        raise CandidateBaseError("frozen isolated evidence runner is unavailable") from exc
    runner = getattr(module, "docker_isolated_evidence_runner", None)
    if not callable(runner):
        raise CandidateBaseError("frozen isolated evidence runner API is absent")
    return runner


def verify_public_p1r_activation(
    repository: Path, validation_input: Path, validation_input_sha256: str,
    p1r_commit: str,
) -> dict[str, Any]:
    """Run the full exact-C gate and return its sole authoritative receipt.

    This function imports only the frozen isolation backend.  There is no
    caller-supplied runner, diagnostic shortcut, structural-only acceptance,
    boolean override, or alternate public ref.
    """
    docker_isolated_evidence_runner = load_frozen_isolated_evidence_runner()
    request_raw = read_immutable_validation_input(validation_input, validation_input_sha256)
    request = strict_json(request_raw, "immutable candidate validation input")
    requested_p1r = request.get("p1_transition", {}).get("p1r_commit")
    if not isinstance(p1r_commit, str) or OID.fullmatch(p1r_commit) is None or requested_p1r != p1r_commit:
        raise CandidateBaseError("activation request does not bind the exact immutable-input P1R commit")
    diagnostic = compile_diagnostic(
        repository, request, request_raw, isolated_runner=docker_isolated_evidence_runner
    )
    if (
        diagnostic["status"] != "LOCAL_NONAUTHORITATIVE_REPLAY_VERIFIED"
        or diagnostic["p1_transition"]["p1r_commit"] != p1r_commit
        or diagnostic["p1_transition"]["p1r_public_remote_ref"] != P1R_PUBLIC_REF
        or diagnostic["validation_inputs_sha256"] != validation_input_sha256
    ):
        raise CandidateBaseError("full validation diagnostic differs from the immutable activation request")
    repo = GitRepository(repository)
    candidate = request["candidate"]["commit"]
    p1r_raw = repo.blob(p1r_commit, P1R_PATH)
    receipt = {
        "schema": "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
        "p1r": {"path": P1R_PATH, "sha256": sha256(p1r_raw)},
        "p1r_commit": p1r_commit,
        "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
        "public_observation": diagnostic["p1r_publication_observation"],
        "validation_inputs_sha256": validation_input_sha256,
        "validation_diagnostic_sha256": diagnostic["diagnostic_sha256"],
        "validator": {"path": VALIDATOR_PATH, "sha256": sha256(repo.blob(candidate, VALIDATOR_PATH))},
    }
    receipt["receipt_sha256"] = activation_receipt_digest(receipt)
    receipt_schema = strict_json(
        repo.blob(candidate, ACTIVATION_RECEIPT_SCHEMA_PATH), "candidate public P1R activation receipt schema"
    )
    schema_validate(receipt, receipt_schema, "public P1R activation receipt")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="replay and verify through public P1R")
    verify.add_argument("--repository", type=Path, required=True)
    verify.add_argument("--input", type=Path, required=True)
    verify.add_argument("--diagnostic-output", type=Path)
    activate = commands.add_parser("activate", help="run full exact-C replay and emit public P1R activation receipt")
    activate.add_argument("--repository", type=Path, required=True)
    activate.add_argument("--input", type=Path, required=True)
    activate.add_argument("--input-sha256", required=True)
    activate.add_argument("--p1r-commit", required=True)
    args = parser.parse_args()
    try:
        if args.command == "activate":
            output = verify_public_p1r_activation(
                args.repository, args.input, args.input_sha256, args.p1r_commit
            )
            print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", end="")
        else:
            request_raw = args.input.read_bytes()
            request = strict_json(request_raw, "candidate validation input")
            output = compile_diagnostic(args.repository, request, request_raw)
            rendered = json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
            if args.diagnostic_output is not None:
                args.diagnostic_output.parent.mkdir(parents=True, exist_ok=True)
                args.diagnostic_output.write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")
    except (OSError, CandidateBaseError, jsonschema.ValidationError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
