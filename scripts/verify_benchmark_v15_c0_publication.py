#!/usr/bin/env python3
"""Observe, compile, and verify the repository-only Method v1.5 C0 chain.

The push observer validates an exact committed C0A but emits no live receipt.
Only a later read-only replay of a completed GitHub Actions run may compile
C0T.  The CLI has no caller-supplied run-object or timestamp escape hatch.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft7Validator, FormatChecker, RefResolver

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark_v15_c0 as bridge  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
C0A_PATH = "results/benchmark/v1.5-protocol/C0A.json"
C0T_PATH = "results/benchmark/v1.5-protocol/C0T.json"
ACTIVATION_RECEIPT_PATH = "results/benchmark/v1.5-protocol/P1R-activation-receipt.json"
PASS_POOL_REPLAY_INPUT_PATH = "results/benchmark/v1.5-protocol/C0-pass-pool-replay-input.json"
WORKFLOW_PATH = ".github/workflows/method-v15-c0a-publication-observer.yml"
WORKFLOW_REF = WORKFLOW_PATH + "@refs/heads/method-v1.5-c0"
OBSERVATION_SCHEMA_PATH = ROOT / "schemas/benchmark-c0-publication-observation-v1.5.schema.json"
REPLAY_SCHEMA_PATH = ROOT / "schemas/benchmark-c0-pass-pool-replay-input-v1.5.schema.json"
ACTIVATION_SCHEMA_PATH = ROOT / "schemas/benchmark-public-p1r-activation-receipt-v1.5.schema.json"
OBSERVATION_SCHEMA = "c5k4-method-v1.5-c0a-publication-observation-1.0"
C0T_SCHEMA = bridge.SCHEMA
REPOSITORY = "Kuberwastaken/c5-k4"
REPOSITORY_ID = 1331829034
REPOSITORY_NODE_ID = "R_kgDOT2IZKg"
REF = "refs/heads/method-v1.5-c0"
BRANCH = "method-v1.5-c0"
GITHUB_API_VERSION = "2022-11-28"
GITHUB_ACCEPT = "application/vnd.github+json"
OID = re.compile(r"^[0-9a-f]{40}$")
Fetch = Callable[[str], bytes]


class PublicationError(ValueError):
    """The public C0 chronology or server observation is not authentic."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def without(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result.pop(key, None)
    return result


def domain_digest(domain: str, value: dict[str, Any]) -> str:
    return sha256(domain.encode("ascii") + b"\0" + canonical_json(value))


def strict_pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in rows:
        if key in value:
            raise PublicationError(f"duplicate JSON key: {key!r}")
        value[key] = item
    return value


def strict(raw: bytes, label: str) -> dict[str, Any]:
    value = strict_value(raw, label)
    if not isinstance(value, dict):
        raise PublicationError(f"{label} must be exactly one JSON object")
    return value


def strict_value(raw: bytes, label: str) -> Any:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicationError(f"{label} is not strict UTF-8 JSON") from exc
    return value


def load(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PublicationError(f"cannot read exact {label}") from exc
    return strict(raw, label), raw


def schema_validate(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema, _ = load(schema_path, f"{label} schema")
    store: dict[str, Any] = {}
    if schema_path == bridge.SCHEMA_PATH:
        observation_schema, _ = load(OBSERVATION_SCHEMA_PATH, "observation schema")
        store[observation_schema["$id"]] = observation_schema
    resolver = RefResolver.from_schema(schema, store=store)
    errors = sorted(
        Draft7Validator(schema, resolver=resolver, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '$'}: {error.message}" for error in errors
        )
        raise PublicationError(f"{label} schema validation failed: {rendered}")


def git(*args: str) -> bytes:
    env = {
        "PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
    }
    try:
        return subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never", *args],
            cwd=ROOT, env=env, check=True, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise PublicationError("sanitized local Git replay failed") from exc


def exact_commit(commit: str) -> None:
    if OID.fullmatch(commit) is None:
        raise PublicationError("commit must be an exact lowercase Git object ID")
    if git("rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
        raise PublicationError("commit does not resolve to the exact requested object")


def commit_file(commit: str, path: str) -> bytes:
    exact_commit(commit)
    try:
        return git("show", f"{commit}:{path}")
    except PublicationError:
        raise


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value) is None:
        raise PublicationError(f"{label} must be whole-second RFC3339 UTC")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PublicationError(f"{label} is invalid") from exc


def validate_activation_receipt(receipt: dict[str, Any], raw: bytes, pool: dict[str, Any]) -> None:
    if raw != canonical_json(receipt):
        raise PublicationError("P1R activation receipt is not exact canonical JSON")
    schema_validate(receipt, ACTIVATION_SCHEMA_PATH, "P1R activation receipt")
    expected_self = domain_digest(
        "c5k4-method-v1.5-public-p1r-activation-receipt-1.0",
        without(receipt, "receipt_sha256"),
    )
    binding = pool["p1_binding"]
    if (
        receipt.get("receipt_sha256") != expected_self
        or sha256(raw) != binding.get("p1r_activation_sha256")
        or receipt.get("p1r_commit") != binding.get("p1r_commit")
        or receipt.get("p1r") != binding.get("p1r")
        or receipt.get("activation_boundary") != "PUBLIC_AUTHENTICATED_P1R"
    ):
        raise PublicationError("exact P1R activation receipt does not match the frozen pass-pool chronology")


def repository_file(ref: dict[str, Any], parent_commit: str, label: str) -> Path:
    if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
        raise PublicationError(f"{label} is not an exact file binding")
    path = ref.get("path")
    if not isinstance(path, str):
        raise PublicationError(f"{label} path is invalid")
    candidate = (ROOT / path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise PublicationError(f"{label} escapes the repository") from exc
    try:
        raw = candidate.read_bytes()
    except OSError as exc:
        raise PublicationError(f"{label} exact bytes are unavailable") from exc
    if sha256(raw) != ref.get("sha256") or commit_file(parent_commit, path) != raw:
        raise PublicationError(f"{label} digest or terminal committed bytes differ")
    return candidate


def replay_pass_pool(c0a: dict[str, Any], replay_input_path: Path) -> None:
    replay, replay_raw = load(replay_input_path, "pass-pool replay input")
    if replay_input_path.resolve() != (ROOT / PASS_POOL_REPLAY_INPUT_PATH).resolve():
        raise PublicationError("pass-pool replay input must use its frozen repository path")
    parent = c0a["publication_topology"]["terminal_u2_commit"]
    if commit_file(parent, PASS_POOL_REPLAY_INPUT_PATH) != replay_raw:
        raise PublicationError("pass-pool replay input differs from terminal committed bytes")
    if replay_raw != canonical_json(replay):
        raise PublicationError("pass-pool replay input is not canonical JSON")
    schema_validate(replay, REPLAY_SCHEMA_PATH, "pass-pool replay input")
    names = (
        "producer", "private_registry", "aggregate_certificate", "replay_attestation",
        "pass_receipt", "prior_public_chain_proof", "pass_public_chain_proof",
        "p1a", "p1t", "p1r", "validation_input",
    )
    paths = {name: repository_file(replay[name], parent, name) for name in names}
    public_repository = (ROOT / replay["public_repository"]).resolve()
    try:
        public_repository.relative_to(ROOT)
    except ValueError as exc:
        raise PublicationError("public repository replay path escapes this checkout") from exc
    if not (public_repository / "HEAD").is_file() and not (public_repository / ".git").exists():
        raise PublicationError("exact public repository clone required for pass-pool replay is absent")
    try:
        expected = bridge.pass_pool.build_pool(
            paths["private_registry"], paths["aggregate_certificate"], paths["replay_attestation"],
            paths["pass_receipt"], paths["prior_public_chain_proof"], paths["pass_public_chain_proof"],
            paths["p1a"], paths["p1t"], paths["p1r"], public_repository,
            validation_input_path=paths["validation_input"],
        )
    except (OSError, bridge.pass_pool.PassPoolError) as exc:
        raise PublicationError(f"independent exact pass-pool producer replay failed: {exc}") from exc
    embedded = c0a["pass_pool"]
    if (
        canonical_json(expected) != canonical_json(embedded)
        or sha256(canonical_json(expected)) != c0a["pass_pool_binding"]["canonical_object_sha256"]
        or expected["pool_sha256"] != c0a["pass_pool_binding"]["pool_sha256"]
    ):
        raise PublicationError("independent pass-pool producer/source replay differs from embedded C0A")


def load_c0a(
    commit: str, activation_receipt_path: Path, replay_input_path: Path,
) -> tuple[dict[str, Any], bytes, dict[str, Any], bytes]:
    c0a_raw = commit_file(commit, C0A_PATH)
    c0a = strict(c0a_raw, "committed C0A")
    try:
        bridge.validate_c0a(c0a)
    except bridge.C0Error as exc:
        raise PublicationError(f"committed C0A is invalid: {exc}") from exc
    topology = c0a["publication_topology"]
    if (
        topology.get("c0a_path") != C0A_PATH or topology.get("c0t_path") != C0T_PATH
        or c0a.get("workflow_binding", {}).get("path") != WORKFLOW_PATH
    ):
        raise PublicationError("C0A does not bind the frozen artifact and observer paths")
    try:
        bridge.validate_c0a_commit(c0a, commit, ROOT / C0A_PATH)
    except (OSError, ValueError, bridge.C0Error) as exc:
        raise PublicationError(f"C0A is not the exact one-path child of terminal U2: {exc}") from exc
    if (ROOT / C0A_PATH).read_bytes() != c0a_raw:
        raise PublicationError("checkout C0A bytes differ from the observed commit")
    receipt, receipt_raw = load(activation_receipt_path, "P1R activation receipt")
    if activation_receipt_path.resolve() != (ROOT / ACTIVATION_RECEIPT_PATH).resolve():
        raise PublicationError("P1R activation receipt must use its frozen repository path")
    if commit_file(c0a["publication_topology"]["terminal_u2_commit"], ACTIVATION_RECEIPT_PATH) != receipt_raw:
        raise PublicationError("P1R activation receipt differs from terminal committed bytes")
    validate_activation_receipt(receipt, receipt_raw, c0a["pass_pool"])
    p1 = c0a["p1_activation"]
    if p1 != {key: receipt[key] for key in ("p1r", "p1r_commit", "activation_boundary")}:
        raise PublicationError("C0A P1 activation projection differs from the exact activation receipt")
    replay_pass_pool(c0a, replay_input_path)
    workflow_raw = commit_file(commit, WORKFLOW_PATH)
    if sha256(workflow_raw) != c0a["workflow_binding"]["sha256"]:
        raise PublicationError("committed observer workflow differs from the C0A workflow binding")
    return c0a, c0a_raw, receipt, receipt_raw


def live_fetch(url: str) -> bytes:
    headers = {
        "Accept": GITHUB_ACCEPT, "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "c5k4-method-v1.5-c0-observer",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise PublicationError("authenticated GitHub API replay requires GITHUB_TOKEN")
    headers["Authorization"] = "Bearer " + token
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            raw = response.read(2_000_001)
    except OSError as exc:
        raise PublicationError(f"read-only GitHub Actions replay failed: {exc}") from exc
    if len(raw) > 2_000_000:
        raise PublicationError("GitHub run object exceeds the frozen size bound")
    return raw


def observation_digest(value: dict[str, Any]) -> str:
    return domain_digest(OBSERVATION_SCHEMA, without(value, "receipt_sha256"))


def _exhaustive_run_listing(fetch: Fetch, *, c0a_commit: str, run_id: int) -> str:
    encoded_workflow = urllib.parse.quote(WORKFLOW_PATH, safe="")
    pages: list[dict[str, Any]] = []
    runs: list[dict[str, Any]] = []
    total: int | None = None
    page = 1
    while True:
        query = urllib.parse.urlencode({
            "event": "push", "head_sha": c0a_commit, "per_page": 100, "page": page,
        })
        url = f"https://api.github.com/repos/{REPOSITORY}/actions/workflows/{encoded_workflow}/runs?{query}"
        listing = strict(fetch(url), f"GitHub workflow run listing page {page}")
        rows = listing.get("workflow_runs")
        count = listing.get("total_count")
        if type(count) is not int or count < 0 or not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise PublicationError("GitHub workflow run listing page has an invalid closed projection")
        if total is None:
            total = count
        if count != total or len(rows) > 100:
            raise PublicationError("GitHub workflow run pagination count changed during replay")
        pages.append(listing)
        runs.extend(rows)
        # A full page may have a successor even when a stale/capped total says
        # otherwise.  Only a short terminal page proves enumeration exhausted.
        if len(rows) < 100:
            break
        if page >= 1000:
            raise PublicationError("GitHub workflow run pagination is incomplete or unbounded")
        page += 1
    ids = [row.get("id") for row in runs]
    if (
        len(runs) != total or any(type(run_id_value) is not int or run_id_value < 1 for run_id_value in ids)
        or len(set(ids)) != len(runs)
    ):
        raise PublicationError("GitHub workflow run pagination is incomplete or duplicates runs")
    if any(row.get("head_sha") != c0a_commit or row.get("event") != "push" for row in runs):
        raise PublicationError("exact-head GitHub workflow query returned a foreign run")
    if len(runs) != 1:
        raise PublicationError("exact C0A push must have one unique GitHub workflow run globally")
    selected = runs[0]
    if (
        selected.get("id") != run_id or selected.get("run_attempt") != 1
        or selected.get("status") != "completed" or selected.get("conclusion") != "success"
    ):
        raise PublicationError("chosen run is not the unique first-attempt success for exact C0A push")
    projection = {
        "api_version": GITHUB_API_VERSION, "workflow": WORKFLOW_PATH,
        "query": {"event": "push", "head_sha": c0a_commit, "per_page": 100},
        "total_count": total, "pages": pages,
    }
    return sha256(canonical_json(projection))


def _require_public_ref(raw: bytes, expected_tip: str) -> str:
    ref = strict(raw, "GitHub public ref object")
    target = ref.get("object")
    if (
        ref.get("ref") != REF or not isinstance(target, dict)
        or target.get("type") != "commit" or target.get("sha") != expected_tip
    ):
        raise PublicationError("current GitHub public C0 ref is rewritten or does not equal the required tip")
    return sha256(canonical_json(ref))


def _server_repository_and_governance(
    fetch: Fetch, *, base_commit: str, expected_tip: str, expected_commits: list[str],
) -> dict[str, Any]:
    repo_url = f"https://api.github.com/repos/{REPOSITORY}"
    repository = strict(fetch(repo_url), "GitHub repository object")
    if (
        repository.get("id") != REPOSITORY_ID or repository.get("node_id") != REPOSITORY_NODE_ID
        or repository.get("full_name") != REPOSITORY or repository.get("private") is not False
    ):
        raise PublicationError("GitHub repository numeric/node identity differs from the frozen authority")
    ref_url = f"https://api.github.com/repos/{REPOSITORY}/git/ref/heads/{urllib.parse.quote(BRANCH, safe='')}"
    ref_digest = _require_public_ref(fetch(ref_url), expected_tip)
    rules_url = f"https://api.github.com/repos/{REPOSITORY}/rules/branches/{urllib.parse.quote(BRANCH, safe='')}"
    rules = strict_value(fetch(rules_url), "GitHub effective branch rules")
    if not isinstance(rules, list) or any(not isinstance(rule, dict) for rule in rules):
        raise PublicationError("GitHub effective branch rules projection must be an array")
    rule_types = [rule.get("type") for rule in rules]
    if rule_types.count("deletion") != 1 or rule_types.count("non_fast_forward") != 1:
        raise PublicationError("C0 branch must have exactly one active no-delete and no-force-push rule")
    compare_url = f"https://api.github.com/repos/{REPOSITORY}/compare/{base_commit}...{expected_tip}"
    comparison = strict(fetch(compare_url), "GitHub ancestry comparison")
    commits = comparison.get("commits")
    observed_commits = [row.get("sha") for row in commits] if isinstance(commits, list) and all(isinstance(row, dict) for row in commits) else None
    if (
        comparison.get("status") != "ahead" or comparison.get("ahead_by") != len(expected_commits)
        or comparison.get("behind_by") != 0 or comparison.get("total_commits") != len(expected_commits)
        or comparison.get("base_commit", {}).get("sha") != base_commit
        or comparison.get("merge_base_commit", {}).get("sha") != base_commit
        or observed_commits != expected_commits
    ):
        raise PublicationError("GitHub compare audit does not prove the exact append-only C0 ancestry")
    return {
        "repository_id": REPOSITORY_ID, "repository_node_id": REPOSITORY_NODE_ID,
        "repository_projection_sha256": sha256(canonical_json(repository)),
        "ref_projection_sha256": ref_digest,
        "protection_source": "GITHUB_EFFECTIVE_BRANCH_RULES_API",
        "protection_projection_sha256": sha256(canonical_json(rules)),
        "no_force_push": True, "no_delete": True,
        "ancestry_base_commit": base_commit, "ancestry_tip_commit": expected_tip,
        "ancestry_commits": expected_commits,
        "ancestry_projection_sha256": sha256(canonical_json(comparison)),
    }


def _compile_observation_live(
    c0a_commit: str, run_id: int, activation_receipt_path: Path, replay_input_path: Path,
    *, expected_ref_tip: str | None = None, validate_capture: bool = True,
) -> dict[str, Any]:
    c0a, c0a_raw, activation, activation_raw = load_c0a(c0a_commit, activation_receipt_path, replay_input_path)
    api_url = f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{run_id}"
    raw = live_fetch(api_url)
    run = strict(raw, "GitHub Actions run object")
    repository = run.get("repository")
    run_path = run.get("path")
    if isinstance(run_path, str):
        run_path = run_path.split("@", 1)[0]
    expected = {
        "id": run_id, "run_attempt": 1, "event": "push", "status": "completed",
        "conclusion": "success", "head_sha": c0a_commit, "head_branch": BRANCH,
        "url": api_url, "html_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
    }
    for key, wanted in expected.items():
        if run.get(key) != wanted:
            raise PublicationError(f"GitHub server run {key} differs from the frozen C0A publication")
    if (
        not isinstance(repository, dict) or repository.get("id") != REPOSITORY_ID
        or repository.get("node_id") != REPOSITORY_NODE_ID or repository.get("full_name") != REPOSITORY
        or run_path != WORKFLOW_PATH
    ):
        raise PublicationError("GitHub server run repository/workflow differs from the frozen observer")
    created, started, completed = run.get("created_at"), run.get("run_started_at"), run.get("updated_at")
    created_time = parse_time(created, "GitHub run creation")
    started_time = parse_time(started, "GitHub run start")
    completed_time = parse_time(completed, "GitHub run completion")
    listing_digest = _exhaustive_run_listing(live_fetch, c0a_commit=c0a_commit, run_id=run_id)
    tip = expected_ref_tip or c0a_commit
    ancestry_commits = [c0a_commit] if tip == c0a_commit else [c0a_commit, tip]
    governance = _server_repository_and_governance(
        live_fetch, base_commit=c0a["publication_topology"]["terminal_u2_commit"],
        expected_tip=tip, expected_commits=ancestry_commits,
    )
    close = parse_time(c0a["randomness_contract"]["round_closes_at_utc"], "future drand close")
    if not created_time <= started_time <= completed_time < close:
        raise PublicationError("chronology must satisfy GitHub create <= start <= completion < drand close")
    pool = c0a["pass_pool"]
    observation = {
        "schema": OBSERVATION_SCHEMA, "artifact_kind": "C0A_PUBLICATION_OBSERVATION",
        "protocol_version": "1.5", "status": "C0A_PUBLICATION_AUTHENTICATED_PRE_DRAND_CLOSE",
        "authority": "GITHUB_SERVER_ACTIONS_RUN_REPLAY", "repository": REPOSITORY, "ref": REF,
        "api_contract": {
            "accept": GITHUB_ACCEPT, "version": GITHUB_API_VERSION,
            "authentication": "GITHUB_TOKEN_BEARER_REQUIRED", "read_only": True,
        },
        "repository_identity": {
            "id": REPOSITORY_ID, "node_id": REPOSITORY_NODE_ID, "full_name": REPOSITORY,
        },
        "c0a": {"path": C0A_PATH, "commit": c0a_commit, "sha256": sha256(c0a_raw)},
        "chronology": {
            "p1r_commit": activation["p1r_commit"], "p1r_activation_receipt_sha256": sha256(activation_raw),
            "u1_commit": pool["upstream"]["u1_commit"], "u1_tree": pool["upstream"]["u1_tree"],
            "u2_commit": pool["upstream"]["u2_commit"], "u2_tree": pool["upstream"]["u2_tree"],
            "pass_publication_commit": pool["public_chain"]["pass_publication_commit"],
            "c0a_parent_commit": c0a["publication_topology"]["terminal_u2_commit"],
        },
        "pass_pool": {
            "pool_sha256": c0a["pass_pool_binding"]["pool_sha256"],
            "canonical_object_sha256": c0a["pass_pool_binding"]["canonical_object_sha256"],
        },
        "workflow": {"path": WORKFLOW_PATH, "ref": WORKFLOW_REF, "committed_sha256": c0a["workflow_binding"]["sha256"]},
        "github_run": {
            "run_id": run_id, "run_attempt": 1, "event": "push", "status": "completed", "conclusion": "success",
            "head_sha": c0a_commit, "head_branch": BRANCH, "created_at_utc": created,
            "started_at_utc": started, "completed_at_utc": completed, "api_url": api_url,
            "html_url": expected["html_url"], "captured_run_object_sha256": sha256(raw),
        },
        "server_evidence": {
            **governance,
            "run_object_projection_sha256": sha256(canonical_json(run)),
            "run_listing_projection_sha256": listing_digest,
        },
        "randomness": {
            "chain_hash": c0a["randomness_contract"]["chain_hash"], "round": c0a["randomness_contract"]["round"],
            "round_closes_at_utc": c0a["randomness_contract"]["round_closes_at_utc"], "value": None,
        },
        "publication_boundary": copy.deepcopy(c0a["publication_boundary"]),
    }
    observation["receipt_sha256"] = observation_digest(observation)
    if validate_capture:
        validate_observation(observation)
    else:
        schema_validate(observation, OBSERVATION_SCHEMA_PATH, "current C0 publication replay")
        if observation["receipt_sha256"] != observation_digest(observation):
            raise PublicationError("current C0 publication replay self-digest is invalid")
    return observation


def compile_observation(
    c0a_commit: str, run_id: int, activation_receipt_path: Path, replay_input_path: Path,
) -> dict[str, Any]:
    """Authoritatively compile an observation using only authenticated live replay."""
    return _compile_observation_live(c0a_commit, run_id, activation_receipt_path, replay_input_path)


def validate_observation(value: dict[str, Any]) -> None:
    schema_validate(value, OBSERVATION_SCHEMA_PATH, "C0A publication observation")
    if value.get("receipt_sha256") != observation_digest(value):
        raise PublicationError("C0A publication observation self-digest is invalid")
    chronology = value["chronology"]
    if chronology["c0a_parent_commit"] != chronology["pass_publication_commit"]:
        raise PublicationError("C0A observation does not preserve the terminal pass-publication parent")
    if value["github_run"]["head_sha"] != value["c0a"]["commit"]:
        raise PublicationError("GitHub run does not bind the exact C0A commit")
    if value["api_contract"] != {
        "accept": GITHUB_ACCEPT, "version": GITHUB_API_VERSION,
        "authentication": "GITHUB_TOKEN_BEARER_REQUIRED", "read_only": True,
    } or value["repository_identity"] != {
        "id": REPOSITORY_ID, "node_id": REPOSITORY_NODE_ID, "full_name": REPOSITORY,
    }:
        raise PublicationError("C0A observation API or repository authority is not frozen")
    evidence = value["server_evidence"]
    if (
        evidence["repository_id"] != REPOSITORY_ID
        or evidence["repository_node_id"] != REPOSITORY_NODE_ID
        or evidence["no_force_push"] is not True or evidence["no_delete"] is not True
        or evidence["ancestry_base_commit"] != chronology["c0a_parent_commit"]
        or evidence["ancestry_tip_commit"] != value["c0a"]["commit"]
        or evidence["ancestry_commits"] != [value["c0a"]["commit"]]
    ):
        raise PublicationError("C0A observation lacks exact protected append-only ancestry evidence")


def stable_observation_projection(value: dict[str, Any]) -> dict[str, Any]:
    """Projection that is replayable after the public ref advances from C0A to C0T."""
    projected = without(value, "receipt_sha256")
    evidence = projected["server_evidence"]
    for key in (
        "ref_projection_sha256", "ancestry_base_commit", "ancestry_tip_commit",
        "ancestry_commits", "ancestry_projection_sha256",
    ):
        evidence.pop(key)
    return projected


def c0t_digest(value: dict[str, Any]) -> str:
    return bridge.artifact_digest(value)


def compile_c0t(
    c0a_commit: str, run_id: int, activation_receipt_path: Path, replay_input_path: Path,
) -> dict[str, Any]:
    c0a, c0a_raw, activation, _activation_raw = load_c0a(c0a_commit, activation_receipt_path, replay_input_path)
    observation = compile_observation(c0a_commit, run_id, activation_receipt_path, replay_input_path)
    c0t = {
        "schema": C0T_SCHEMA, "artifact_kind": "C0T", "protocol_version": "1.5",
        "status": "C0_FROZEN_PRE_ENTROPY_ATTESTED", "authority": "LIVE_GITHUB_ACTIONS_OBSERVATION",
        "c0a": {"path": C0A_PATH, "sha256": sha256(c0a_raw)}, "c0a_commit": c0a_commit,
        "p1_activation": {key: copy.deepcopy(activation[key]) for key in ("p1r", "p1r_commit", "activation_boundary")},
        "pass_pool_binding": {
            "canonical_object_sha256": c0a["pass_pool_binding"]["canonical_object_sha256"],
            "pool_sha256": c0a["pass_pool_binding"]["pool_sha256"], "pass_pool_bound": True,
        },
        "randomness_contract": copy.deepcopy(c0a["randomness_contract"]),
        "publication_topology": copy.deepcopy(c0a["publication_topology"]),
        "publication_observation": observation,
        "attestation_policy": {
            "c0a_direct_parent_required": True, "nonmerge_required": True, "c0a_bytes_immutable": True,
            "allowed_c0t_changed_paths": [C0T_PATH],
        },
        "publication_boundary": copy.deepcopy(c0a["publication_boundary"]),
    }
    c0t["artifact_sha256"] = c0t_digest(c0t)
    _validate_c0t_live(c0t, activation_receipt_path=activation_receipt_path, replay_input_path=replay_input_path)
    return c0t


def _validate_c0t_live(
    value: dict[str, Any], *, activation_receipt_path: Path, replay_input_path: Path,
    c0t_commit: str | None = None, artifact_path: Path | None = None,
) -> None:
    schema_validate(value, bridge.SCHEMA_PATH, "C0T")
    if value.get("artifact_sha256") != c0t_digest(value):
        raise PublicationError("C0T self-digest is invalid")
    observation = value["publication_observation"]
    validate_observation(observation)
    c0a_commit = value["c0a_commit"]
    c0a, c0a_raw, activation, _activation_raw = load_c0a(c0a_commit, activation_receipt_path, replay_input_path)
    expected = _compile_observation_live(
        c0a_commit, observation["github_run"]["run_id"], activation_receipt_path,
        replay_input_path, expected_ref_tip=c0t_commit or c0a_commit,
        validate_capture=c0t_commit is None,
    )
    if c0t_commit is None and observation != expected:
        raise PublicationError("C0T observation differs from a direct GitHub server replay")
    if c0t_commit is not None and stable_observation_projection(observation) != stable_observation_projection(expected):
        raise PublicationError("C0T observation differs from stable GitHub server evidence replay")
    if value["c0a"]["sha256"] != sha256(c0a_raw):
        raise PublicationError("C0T does not bind exact committed C0A bytes")
    expected_activation = {
        "p1r": activation["p1r"], "p1r_commit": activation["p1r_commit"],
        "activation_boundary": "PUBLIC_AUTHENTICATED_P1R",
    }
    if (
        value["p1_activation"] != expected_activation
        or value["pass_pool_binding"] != {
            "canonical_object_sha256": c0a["pass_pool_binding"]["canonical_object_sha256"],
            "pool_sha256": c0a["pass_pool_binding"]["pool_sha256"], "pass_pool_bound": True,
        }
        or value["randomness_contract"] != c0a["randomness_contract"]
        or value["publication_topology"] != c0a["publication_topology"]
        or value["publication_boundary"] != c0a["publication_boundary"]
    ):
        raise PublicationError("C0T changed a frozen P1R, U1/U2, pass-pool, randomness, topology, or boundary binding")
    if c0t_commit is None:
        return
    if artifact_path is None:
        raise PublicationError("exact C0T commit verification requires --artifact")
    exact_commit(c0t_commit)
    if git("show", "-s", "--format=%P", c0t_commit).decode().split() != [c0a_commit]:
        raise PublicationError("C0T must be the direct nonmerge child of exact C0A")
    if git("diff-tree", "--no-commit-id", "--name-status", "-r", c0t_commit).decode().splitlines() != [f"A\t{C0T_PATH}"]:
        raise PublicationError("C0T commit must add exactly the frozen C0T path")
    if artifact_path.resolve() != (ROOT / C0T_PATH).resolve() or commit_file(c0t_commit, C0T_PATH) != artifact_path.read_bytes():
        raise PublicationError("C0T artifact path/bytes differ from the exact commit")


def validate_c0t(
    value: dict[str, Any], *, activation_receipt_path: Path, replay_input_path: Path,
    c0t_commit: str, artifact_path: Path,
) -> None:
    """Authoritatively accept only an exact committed C0T after live replay."""
    _validate_c0t_live(
        value, activation_receipt_path=activation_receipt_path,
        replay_input_path=replay_input_path, c0t_commit=c0t_commit, artifact_path=artifact_path,
    )


def write_new(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise PublicationError("output already exists; overwrite is forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    observe = commands.add_parser("observe-c0a", help="validate the exact push commit; emit no receipt")
    observe.add_argument("--commit", required=True)
    observe.add_argument("--activation-receipt", type=Path, default=ROOT / ACTIVATION_RECEIPT_PATH)
    observe.add_argument("--pass-pool-replay-input", type=Path, default=ROOT / PASS_POOL_REPLAY_INPUT_PATH)
    compile_command = commands.add_parser("compile-c0t", help="replay a completed live run and compile C0T")
    compile_command.add_argument("--c0a-commit", required=True); compile_command.add_argument("--run-id", type=int, required=True)
    compile_command.add_argument("--activation-receipt", type=Path, default=ROOT / ACTIVATION_RECEIPT_PATH)
    compile_command.add_argument("--pass-pool-replay-input", type=Path, default=ROOT / PASS_POOL_REPLAY_INPUT_PATH)
    compile_command.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify-c0t", help="replay live server evidence and verify C0T")
    verify.add_argument("--artifact", type=Path, required=True); verify.add_argument("--activation-receipt", type=Path, default=ROOT / ACTIVATION_RECEIPT_PATH)
    verify.add_argument("--pass-pool-replay-input", type=Path, default=ROOT / PASS_POOL_REPLAY_INPUT_PATH)
    verify.add_argument("--commit", required=True)
    args = parser.parse_args()
    try:
        if args.command == "observe-c0a":
            load_c0a(args.commit, args.activation_receipt.resolve(), args.pass_pool_replay_input.resolve())
            print(f"VALID_C0A_PUBLICATION_COMMIT {args.commit}")
        elif args.command == "compile-c0t":
            write_new(args.output.resolve(), compile_c0t(
                args.c0a_commit, args.run_id, args.activation_receipt.resolve(), args.pass_pool_replay_input.resolve(),
            ))
        else:
            value, _ = load(args.artifact.resolve(), "C0T")
            validate_c0t(
                value, activation_receipt_path=args.activation_receipt.resolve(),
                replay_input_path=args.pass_pool_replay_input.resolve(), c0t_commit=args.commit,
                artifact_path=args.artifact.resolve(),
            )
            print("VALID_C0T_PUBLICATION")
    except (OSError, PublicationError) as exc:
        print(f"INVALID_C0_PUBLICATION: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
