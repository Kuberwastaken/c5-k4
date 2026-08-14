#!/usr/bin/env python3
"""Verify exact Method v1.5 P0A -> P0T -> A0 publication chronology offline."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


ROOT = Path(__file__).resolve().parent.parent
P0A_PATH = "results/benchmark/v1.5-p0-a0/P0A.json"
P0T_PATH = "results/benchmark/v1.5-p0-a0/P0T.json"
A0_PATH = "results/benchmark/v1.5-p0-a0/A0.json"
SCHEMAS = {
    "P0A": "schemas/benchmark-p0a-v1.5.schema.json",
    "P0T": "schemas/benchmark-p0t-v1.5.schema.json",
    "A0": "schemas/benchmark-a0-v1.5.schema.json",
    "RECEIPT": "schemas/benchmark-p0-publication-receipt-v1.5.schema.json",
}
OID = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY = "Kuberwastaken/c5-k4"
REPOSITORY_ID = 1331829034
BRANCH = "method-v1.5-p0"
REF = "refs/heads/method-v1.5-p0"
WORKFLOW_PATH = ".github/workflows/method-v15-p0-publication-observer.yml"
AMI_POLICY_COMPONENTS = (
    "scripts/verify_benchmark_v15_attestable_ami_acceptance.py",
    "schemas/benchmark-attestable-ami-plan-v1.5.schema.json",
    "schemas/benchmark-attestable-ami-receipt-v1.5.schema.json",
    "schemas/benchmark-attestable-ami-authority-binding-v1.5.schema.json",
    "infra/benchmark-v1.5/attestable-ami/plan.json",
)
REQUIRED_COMPONENTS = {
    ".github/workflows/method-v15-p0-publication-observer.yml",
    "results/benchmark/v1.5-p0-a0/OFFLINE_PUBLICATION_WORKFLOW.md",
    "schemas/benchmark-a0-v1.5.schema.json", "schemas/benchmark-p0a-v1.5.schema.json",
    "schemas/benchmark-p0t-v1.5.schema.json", "schemas/benchmark-p0-publication-receipt-v1.5.schema.json",
    "scripts/build_benchmark_v15_p0_a0.py", "scripts/verify_benchmark_v15_p0_a0_publication.py",
    "scripts/test_build_verify_benchmark_v15_p0_a0.py", "scripts/test_method_v15_p0_publication_observer_workflow.py",
    *AMI_POLICY_COMPONENTS,
}
TARGET_DATA_KEYS = {"clusters", "eligible_rows", "final_eligible_rows", "selected_rows", "selected_clusters", "candidate_identities", "statement", "statement_text", "declarations", "candidates", "target_rankings", "target_semantics", "residual", "proof_route", "outcomes", "target_identity", "target_identities"}
SCHEMA_CONTAINER_KEYS = {"properties", "definitions", "$defs", "patternProperties"}


class PublicationError(ValueError):
    pass


def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in rows:
        if key in result:
            raise PublicationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def strict(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicationError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PublicationError(f"{label} must be a JSON object")
    return value


def load(path: Path) -> dict[str, Any]:
    try:
        return strict(path.read_bytes(), str(path))
    except OSError as exc:
        raise PublicationError(f"cannot read {path}") from exc


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + canonical(value)).hexdigest()


def self_digest(domain: str, value: dict[str, Any], field: str) -> str:
    unsigned = dict(value); unsigned.pop(field, None)
    return digest(domain, unsigned)


def git(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(repo), *args],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1"},
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise PublicationError("sanitized Git query failed") from exc


def exact_commit(repo: Path, commit: str) -> None:
    if OID.fullmatch(commit) is None or git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
        raise PublicationError("publication commit is not an exact lowercase SHA-1 object ID")


def commit_raw(repo: Path, commit: str, path: str) -> bytes:
    return git(repo, "show", f"{commit}:{path}")


def schema_validate(value: dict[str, Any], kind: str) -> None:
    schema = load(ROOT / SCHEMAS[kind])
    store: dict[str, dict[str, Any]] = {schema["$id"]: schema}
    for other in SCHEMAS.values():
        candidate = load(ROOT / other)
        store[candidate["$id"]] = candidate
        store[Path(other).name] = candidate
    resolver = jsonschema.RefResolver.from_schema(schema, store=store)
    try:
        jsonschema.Draft7Validator(schema, resolver=resolver, format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.ValidationError as exc:
        raise PublicationError(f"{kind} schema failure at {list(exc.absolute_path)}: {exc.message}") from exc


def audit_json_component(value: Any, path: str, trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        inside_schema = any(part in SCHEMA_CONTAINER_KEYS for part in trail)
        for key, child in value.items():
            nonempty = child is not None and child is not False and child not in ("", [], {})
            if str(key).casefold() in TARGET_DATA_KEYS and nonempty and not inside_schema:
                raise PublicationError(f"{path} contains populated target-data field {'.'.join((*trail, str(key)))}")
            audit_json_component(child, path, (*trail, str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            audit_json_component(child, path, (*trail, str(index)))


def topology(repo: Path, commit: str, path: str) -> str:
    exact_commit(repo, commit)
    parents = git(repo, "show", "-s", "--format=%P", commit).decode().split()
    if len(parents) != 1:
        raise PublicationError(f"{path} publication must have exactly one parent")
    changed = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()
    if changed != [path]:
        raise PublicationError(f"publication commit must change exactly {path}")
    return parents[0]


def validate_receipt(repo: Path, receipt: dict[str, Any], kind: str, commit: str, path: str, raw: bytes) -> None:
    schema_validate(receipt, "RECEIPT")
    expected_subject = {"artifact_kind": kind, "path": path, "commit": commit, "sha256": hashlib.sha256(raw).hexdigest()}
    if receipt["subject"] != expected_subject or receipt["actions_run"]["head_sha"] != commit:
        raise PublicationError("Actions receipt does not bind the exact published artifact")
    projection = receipt["actions_run"]
    if projection["workflow_commit"] != commit:
        raise PublicationError("Actions receipt workflow commit differs from exact subject commit")
    workflow_raw = commit_raw(repo, commit, projection["workflow_path"])
    if projection["workflow_blob_sha256"] != hashlib.sha256(workflow_raw).hexdigest():
        raise PublicationError("Actions receipt workflow digest differs from exact commit bytes")
    projection_unsigned = dict(projection); projection_unsigned.pop("api_projection_sha256", None); projection_unsigned.pop("captured_ref_sha256", None)
    if projection["api_projection_sha256"] != digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", projection_unsigned):
        raise PublicationError("Actions bounded API projection digest mismatch")
    if receipt["receipt_sha256"] != self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", receipt, "receipt_sha256"):
        raise PublicationError("Actions receipt canonical digest mismatch")


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PublicationError(f"{label} is not a UTC timestamp")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise PublicationError(f"{label} is invalid") from exc


def live_fetch(url: str) -> bytes:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "c5k4-method-v1.5-p0-observer"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            raw = response.read(2_000_001)
    except OSError as exc:
        raise PublicationError(f"read-only GitHub Actions replay failed: {exc}") from exc
    if len(raw) > 2_000_000:
        raise PublicationError("GitHub API response exceeds the frozen size bound")
    return raw


def _api_urls(run_id: int, commit: str) -> tuple[str, str, str]:
    workflow = urllib.parse.quote(WORKFLOW_PATH, safe="")
    run_url = f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{run_id}"
    listing_url = f"https://api.github.com/repos/{REPOSITORY}/actions/workflows/{workflow}/runs?branch={BRANCH}&event=push&head_sha={commit}&per_page=100"
    ref_url = f"https://api.github.com/repos/{REPOSITORY}/git/ref/heads/{urllib.parse.quote(BRANCH, safe='')}"
    return run_url, listing_url, ref_url


def _server_projection(repo: Path, *, kind: str, commit: str, run_id: int, fetch: Any) -> tuple[dict[str, Any], bytes]:
    if kind not in {"P0A", "P0T", "A0"}:
        raise PublicationError("Actions observation subject kind is invalid")
    exact_commit(repo, commit)
    if kind == "P0A":
        validate_p0a(repo, commit)
    elif kind == "P0T":
        validate_p0t(repo, commit)
    else:
        validate_a0_publication_structure(repo, commit)
    run_url, listing_url, ref_url = _api_urls(run_id, commit)
    run_raw = fetch(run_url); run = strict(run_raw, "GitHub Actions run")
    repository = run.get("repository"); run_path = run.get("path")
    if isinstance(run_path, str): run_path = run_path.split("@", 1)[0]
    expected = {"id": run_id, "run_attempt": 1, "event": "push", "status": "completed", "conclusion": "success", "head_sha": commit, "head_branch": BRANCH, "url": run_url, "html_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}"}
    for key, wanted in expected.items():
        if run.get(key) != wanted:
            raise PublicationError(f"GitHub server run {key} differs from exact {kind} publication")
    if not isinstance(repository, dict) or repository.get("full_name") != REPOSITORY or repository.get("id") != REPOSITORY_ID or run_path != WORKFLOW_PATH:
        raise PublicationError("GitHub run repository id/name or workflow path differs")
    created, started, completed = run.get("created_at"), run.get("run_started_at"), run.get("updated_at")
    if not parse_time(created, "run creation") <= parse_time(started, "run start") <= parse_time(completed, "run completion"):
        raise PublicationError("GitHub run chronology must satisfy create <= start <= completion")
    listing_pages: list[dict[str, Any]] = []
    first = strict(fetch(listing_url), "GitHub workflow run listing page 1")
    total_count = first.get("total_count"); first_runs = first.get("workflow_runs")
    if not isinstance(total_count, int) or isinstance(total_count, bool) or total_count < 0 or total_count > 10_000 or not isinstance(first_runs, list):
        raise PublicationError("GitHub workflow listing has invalid bounded total_count/workflow_runs")
    listing_pages.append(first)
    page_count = max(1, (total_count + 99) // 100)
    runs: list[Any] = list(first_runs)
    for page in range(2, page_count + 1):
        page_value = strict(fetch(f"{listing_url}&page={page}"), f"GitHub workflow run listing page {page}")
        if page_value.get("total_count") != total_count or not isinstance(page_value.get("workflow_runs"), list):
            raise PublicationError("GitHub paginated workflow listing changed total or shape")
        listing_pages.append(page_value); runs.extend(page_value["workflow_runs"])
    if len(runs) != total_count:
        raise PublicationError("GitHub workflow listing pagination is incomplete or overlapping")
    matching = [row for row in runs if isinstance(row, dict) and row.get("head_sha") == commit and row.get("event") == "push"]
    if len(matching) != 1 or matching[0].get("id") != run_id or matching[0].get("run_attempt") != 1 or matching[0].get("conclusion") != "success":
        raise PublicationError("run is not the unique first-attempt success for exact commit")
    ref_raw = fetch(ref_url); ref = strict(ref_raw, "GitHub public ref")
    target = ref.get("object")
    if ref.get("ref") != REF or not isinstance(target, dict) or target.get("type") != "commit" or OID.fullmatch(str(target.get("sha"))) is None:
        raise PublicationError("GitHub public ref response is invalid")
    tip = target["sha"]
    try:
        git(repo, "merge-base", "--is-ancestor", commit, tip)
    except PublicationError as exc:
        raise PublicationError("GitHub public ref does not contain the observed commit without rewrite") from exc
    workflow_raw = commit_raw(repo, commit, WORKFLOW_PATH)
    selected_listing = {key: matching[0].get(key) for key in ("id", "run_attempt", "event", "status", "conclusion", "head_sha", "head_branch")}
    projection: dict[str, Any] = {
        "repository": REPOSITORY, "repository_id": REPOSITORY_ID, "api_version": "2022-11-28", "workflow_path": WORKFLOW_PATH,
        "workflow_commit": commit, "workflow_blob_sha256": hashlib.sha256(workflow_raw).hexdigest(),
        "event": "push", "branch": BRANCH, "ref": REF, "head_sha": commit, "run_id": run_id,
        "run_attempt": 1, "status": "completed", "conclusion": "success",
        "created_at_utc": created, "run_started_at_utc": started, "updated_at_utc": completed,
        "captured_run_object_sha256": hashlib.sha256(run_raw).hexdigest(),
        "captured_listing_sha256": hashlib.sha256(canonical({"pages": listing_pages})).hexdigest(),
        "captured_ref_sha256": hashlib.sha256(canonical(ref)).hexdigest(),
        "api_projection_sha256": "0" * 64,
    }
    unsigned = dict(projection); unsigned.pop("api_projection_sha256"); unsigned.pop("captured_ref_sha256")
    projection["api_projection_sha256"] = digest("c5k4-method-v1.5-p0-actions-api-projection-1.0", unsigned)
    return projection, run_raw


def compile_actions_observation(repo: Path, *, kind: str, commit: str, run_id: int, fetch: Any = live_fetch) -> dict[str, Any]:
    path = {"P0A": P0A_PATH, "P0T": P0T_PATH, "A0": A0_PATH}.get(kind)
    if path is None:
        raise PublicationError("Actions observation artifact kind is invalid")
    artifact_raw = commit_raw(repo, commit, path)
    projection, _ = _server_projection(repo, kind=kind, commit=commit, run_id=run_id, fetch=fetch)
    receipt: dict[str, Any] = {
        "schema": "c5k4-method-v1.5-p0-publication-receipt-1.0", "source": "LIVE_GITHUB_SERVER_ACTIONS_REPLAY",
        "subject": {"artifact_kind": kind, "path": path, "commit": commit, "sha256": hashlib.sha256(artifact_raw).hexdigest()},
        "actions_run": projection,
        "capture": {"authenticated_by": "scripts/verify_benchmark_v15_p0_a0_publication.py", "network_fetch_performed_by_builder": True, "credentials_embedded": False, "raw_api_response_published": False, "server_observation_claim_requires_independent_validation": True, "live_replay_required_by_builder": True},
        "receipt_sha256": "0" * 64,
    }
    receipt["receipt_sha256"] = self_digest("c5k4-method-v1.5-p0-publication-receipt-1.0", receipt, "receipt_sha256")
    validate_receipt(repo, receipt, kind, commit, path, artifact_raw)
    return receipt


def replay_actions_observation(repo: Path, receipt: dict[str, Any], *, kind: str, commit: str, fetch: Any = live_fetch, allow_ref_advance: bool = False) -> dict[str, Any]:
    path = {"P0A": P0A_PATH, "P0T": P0T_PATH, "A0": A0_PATH}.get(kind)
    if path is None:
        raise PublicationError("Actions replay artifact kind is invalid")
    raw = commit_raw(repo, commit, path)
    validate_receipt(repo, receipt, kind, commit, path, raw)
    observed, _ = _server_projection(repo, kind=kind, commit=commit, run_id=receipt["actions_run"]["run_id"], fetch=fetch)
    expected = dict(receipt["actions_run"]); actual = dict(observed)
    if allow_ref_advance:
        expected.pop("captured_ref_sha256", None); actual.pop("captured_ref_sha256", None)
    if actual != expected:
        raise PublicationError("live GitHub replay differs from authenticated observation artifact")
    return observed


def validate_p0a(repo: Path, commit: str) -> dict[str, Any]:
    parent = topology(repo, commit, P0A_PATH)
    raw = commit_raw(repo, commit, P0A_PATH); value = strict(raw, "P0A")
    schema_validate(value, "P0A")
    if value["protocol_base_commit"] != parent:
        raise PublicationError("P0A base commit is not its exact sole parent")
    paths: list[str] = []
    for component in value["components"]:
        path = component["path"]
        paths.append(path)
        component_raw = commit_raw(repo, parent, path)
        blob_oid = git(repo, "rev-parse", f"{parent}:{path}").decode().strip()
        if component != {"path": path, "blob_oid": blob_oid, "sha256": hashlib.sha256(component_raw).hexdigest()}:
            raise PublicationError(f"P0A component binding differs from exact base bytes: {path}")
    if paths != sorted(set(paths)):
        raise PublicationError("P0A component bindings are not unique and sorted")
    if set(paths) != REQUIRED_COMPONENTS:
        raise PublicationError("P0A components differ from the exact frozen P0/A0 and AMI policy closure")
    json_count = 0
    for component in value["components"]:
        if Path(component["path"]).suffix.casefold() == ".json":
            audit_json_component(strict(commit_raw(repo, parent, component["path"]), component["path"]), component["path"])
            json_count += 1
    if value["target_data_audit"] != {"algorithm": "STRUCTURAL_JSON_KEY_AUDIT_V1_5", "json_component_count": json_count, "populated_target_data_fields_detected": 0, "free_text_or_python_semantic_audit_claimed": False}:
        raise PublicationError("P0A target-data audit count/result differs from exact base bytes")
    if value["components_sha256"] != digest("c5k4-method-v1.5-p0a-components-1.0", value["components"]):
        raise PublicationError("P0A component closure digest mismatch")
    policy = value["authority_policy"]
    component_index = {row["path"]: row for row in value["components"]}
    try:
        ami_components = [component_index[path] for path in AMI_POLICY_COMPONENTS]
    except KeyError as exc:
        raise PublicationError("P0A omits a required AMI authority-binding policy component") from exc
    ami_policy_digest = digest("c5k4-method-v1.5-attestable-ami-authority-binding-policy-template-1.0", ami_components)
    if policy["attestable_ami_authority_binding_policy_sha256"] != ami_policy_digest:
        raise PublicationError("P0A AMI authority-binding policy digest mismatch")
    roster = {"required_independent_signature_count": policy["required_independent_signature_count"], "independent_authorities": policy["independent_authorities"]}
    if policy["authority_roster_sha256"] != digest("c5k4-method-v1.5-a0-authority-roster-1.0", roster):
        raise PublicationError("P0A authority roster digest mismatch")
    ids = [row["authority_id"] for row in policy["independent_authorities"]]
    keys = [row["verification_key_sha256"] for row in policy["independent_authorities"]]
    if len(ids) != len(set(ids)) or len(keys) != len(set(keys)):
        raise PublicationError("P0A authorities are not independent")
    if policy["required_independent_signature_count"] > len(ids):
        raise PublicationError("P0A signature threshold exceeds its frozen authority roster")
    if value["p0a_sha256"] != self_digest("c5k4-method-v1.5-p0a-1.0", value, "p0a_sha256"):
        raise PublicationError("P0A canonical digest mismatch")
    return value


def validate_p0t(repo: Path, commit: str) -> tuple[dict[str, Any], dict[str, Any]]:
    parent = topology(repo, commit, P0T_PATH)
    raw = commit_raw(repo, commit, P0T_PATH); value = strict(raw, "P0T")
    schema_validate(value, "P0T")
    p0a = validate_p0a(repo, parent)
    p0a_raw = commit_raw(repo, parent, P0A_PATH)
    expected = {"path": P0A_PATH, "commit": parent, "sha256": hashlib.sha256(p0a_raw).hexdigest(), "canonical_sha256": p0a["p0a_sha256"]}
    if value["p0a"] != expected:
        raise PublicationError("P0T does not authenticate its exact P0A parent")
    validate_receipt(repo, value["p0a_publication_receipt"], "P0A", parent, P0A_PATH, p0a_raw)
    if value["p0t_sha256"] != self_digest("c5k4-method-v1.5-p0t-1.0", value, "p0t_sha256"):
        raise PublicationError("P0T canonical digest mismatch")
    return value, p0a


def _payload(value: dict[str, Any]) -> dict[str, Any]:
    return {key: child for key, child in value.items() if key not in {"a0_payload_sha256", "a0_sha256", "independent_authority_signatures"}}


def _verify_authority_signatures(value: dict[str, Any], p0a: dict[str, Any], keys_file: Path | None) -> None:
    if keys_file is None:
        raise PublicationError("authoritative A0 validation requires offline --authority-keys")
    supplied = load(keys_file)
    if set(supplied) != {"schema", "keys"} or supplied["schema"] != "c5k4-method-v1.5-offline-a0-authority-keys-1.0" or not isinstance(supplied["keys"], list):
        raise PublicationError("offline authority-key file has an invalid closed shape")
    key_map: dict[str, bytes] = {}
    for row in supplied["keys"]:
        if not isinstance(row, dict) or set(row) != {"authority_id", "public_key_base64"}:
            raise PublicationError("offline authority-key row has an invalid shape")
        try:
            raw = base64.b64decode(row["public_key_base64"], validate=True)
        except (ValueError, TypeError) as exc:
            raise PublicationError("offline authority public key is not canonical base64") from exc
        if len(raw) != 32 or row["authority_id"] in key_map:
            raise PublicationError("offline authority keys must be distinct 32-byte Ed25519 keys")
        key_map[row["authority_id"]] = raw
    policy = p0a["authority_policy"]
    frozen = {row["authority_id"]: row["verification_key_sha256"] for row in policy["independent_authorities"]}
    if value["external_harness_authority"]["verification_key_sha256"] in set(frozen.values()):
        raise PublicationError("NitroTPM harness key must differ from every independent authority key")
    signatures = value["independent_authority_signatures"]
    if len(signatures) < policy["required_independent_signature_count"]:
        raise PublicationError("required independent A0 signatures are absent")
    seen: set[str] = set()
    message = b"c5k4-method-v1.5-a0-authority-signature-1.0\x00" + bytes.fromhex(value["a0_payload_sha256"])
    for signature in signatures:
        authority_id = signature["authority_id"]
        if authority_id in seen or authority_id not in frozen or authority_id not in key_map:
            raise PublicationError("A0 signature authority is duplicate, unfrozen, or missing its offline key")
        key = key_map[authority_id]
        if hashlib.sha256(key).hexdigest() != frozen[authority_id] or signature["verification_key_sha256"] != frozen[authority_id]:
            raise PublicationError("A0 signature key does not match the P0A-frozen authority roster")
        if signature["signed_payload_sha256"] != value["a0_payload_sha256"]:
            raise PublicationError("A0 signature binds a different payload")
        try:
            Ed25519PublicKey.from_public_bytes(key).verify(base64.b64decode(signature["signature_base64"], validate=True), message)
        except (InvalidSignature, ValueError) as exc:
            raise PublicationError("invalid independent A0 authority signature") from exc
        seen.add(authority_id)


def _validate_a0_content(repo: Path, parent: str, value: dict[str, Any], authority_keys: Path | None, *, verify_signatures: bool = True) -> dict[str, Any]:
    schema_validate(value, "A0")
    p0t, p0a = validate_p0t(repo, parent)
    p0t_raw = commit_raw(repo, parent, P0T_PATH)
    expected = {"path": P0T_PATH, "commit": parent, "sha256": hashlib.sha256(p0t_raw).hexdigest(), "canonical_sha256": p0t["p0t_sha256"]}
    if value["p0t"] != expected:
        raise PublicationError("A0 does not authenticate its exact P0T parent")
    validate_receipt(repo, value["p0t_publication_receipt"], "P0T", parent, P0T_PATH, p0t_raw)
    p0a_run = p0t["p0a_publication_receipt"]["actions_run"]
    p0t_run = value["p0t_publication_receipt"]["actions_run"]
    if p0a_run["run_id"] == p0t_run["run_id"] or not parse_time(p0a_run["updated_at_utc"], "P0A completion") < parse_time(p0t_run["created_at_utc"], "P0T creation"):
        raise PublicationError("P0A and P0T require distinct sequential pushes and Actions runs")
    component_index = {row["path"]: row for row in p0a["components"]}
    expected_ami_contract = {
        "policy_template_sha256": p0a["authority_policy"]["attestable_ami_authority_binding_policy_sha256"],
        "components": [component_index[path] for path in AMI_POLICY_COMPONENTS],
        "future_live_binding_sha256": None,
    }
    if value["ami_authority_binding_contract"] != expected_ami_contract:
        raise PublicationError("A0 AMI policy/schema/verifier bindings differ from exact P0A closure")
    if value["a0_payload_sha256"] != digest("c5k4-method-v1.5-a0-activation-payload-1.0", _payload(value)):
        raise PublicationError("A0 activation payload digest mismatch")
    if value["a0_sha256"] != self_digest("c5k4-method-v1.5-a0-1.0", value, "a0_sha256"):
        raise PublicationError("A0 canonical digest mismatch")
    authoritative = value["status"] == "EXTERNALLY_AUTHORIZED_A0"
    if authoritative:
        harness = value["external_harness_authority"]
        authorized = parse_time(value["a0_authorized_at_utc"], "A0 authority time")
        if not parse_time(p0t_run["updated_at_utc"], "P0T completion") < authorized:
            raise PublicationError("A0 authority time must follow authenticated P0T publication")
        if harness["attestable_ami_authority_binding_policy_sha256"] != p0a["authority_policy"]["attestable_ami_authority_binding_policy_sha256"]:
            raise PublicationError("A0 harness authority does not match the P0A-frozen AMI authority-binding policy")
        frozen_hashes = {row["verification_key_sha256"] for row in p0a["authority_policy"]["independent_authorities"]}
        if harness["verification_key_sha256"] in frozen_hashes:
            raise PublicationError("NitroTPM harness key must differ from every independent authority key")
        if len(value["independent_authority_signatures"]) < p0a["authority_policy"]["required_independent_signature_count"]:
            raise PublicationError("required independent A0 signatures are absent")
        if verify_signatures:
            _verify_authority_signatures(value, p0a, authority_keys)
    return value


def validate_a0_preview(repo: Path, p0t_commit: str, value: dict[str, Any]) -> dict[str, Any]:
    """Validate an uncommitted draft preview against exact committed P0T."""
    exact_commit(repo, p0t_commit)
    if value.get("status") != "NONAUTHORITATIVE_DRAFT_AWAITING_EXTERNAL_NITROTPM_KEY_AND_SIGNATURES":
        raise PublicationError("local A0 preview must have the nonauthoritative draft status")
    return _validate_a0_content(repo, p0t_commit, value, None)


def validate_a0(repo: Path, commit: str, *, require_authoritative: bool = True, authority_keys: Path | None = None) -> dict[str, Any]:
    """Validate the single publishable A0 commit; committed drafts always fail."""
    parent = topology(repo, commit, A0_PATH)
    raw = commit_raw(repo, commit, A0_PATH); value = strict(raw, "A0")
    validated = _validate_a0_content(repo, parent, value, authority_keys)
    if validated["status"] != "EXTERNALLY_AUTHORIZED_A0":
        raise PublicationError("A0 draft is a local preview only and must not be committed or published")
    return validated


def validate_a0_publication_structure(repo: Path, commit: str) -> dict[str, Any]:
    """Observer-only structural gate; this never grants activation authority."""
    parent = topology(repo, commit, A0_PATH)
    value = strict(commit_raw(repo, commit, A0_PATH), "A0")
    validated = _validate_a0_content(repo, parent, value, None, verify_signatures=False)
    if validated["status"] != "EXTERNALLY_AUTHORIZED_A0":
        raise PublicationError("A0 observer refuses a published local draft")
    return validated


def validated_a0_identity(repo: Path, commit: str, *, require_authoritative: bool = True, authority_keys: Path | None = None, publication_receipt: dict[str, Any] | None = None, fetch: Any = live_fetch) -> dict[str, Any]:
    """Return the closed identity projection consumed by post-A0 live verifiers."""
    value = validate_a0(repo, commit, require_authoritative=require_authoritative, authority_keys=authority_keys)
    if publication_receipt is None:
        raise PublicationError("validated A0 identity requires a live-replayed A0 publication receipt")
    p0t_commit = value["p0t"]["commit"]
    p0t = strict(commit_raw(repo, p0t_commit, P0T_PATH), "P0T")
    p0a_commit = p0t["p0a"]["commit"]
    p0a = strict(commit_raw(repo, p0a_commit, P0A_PATH), "P0A")
    p0a_replay = replay_actions_observation(repo, p0t["p0a_publication_receipt"], kind="P0A", commit=p0a_commit, fetch=fetch, allow_ref_advance=True)
    p0t_replay = replay_actions_observation(repo, value["p0t_publication_receipt"], kind="P0T", commit=p0t_commit, fetch=fetch, allow_ref_advance=True)
    a0_replay = replay_actions_observation(repo, publication_receipt, kind="A0", commit=commit, fetch=fetch)
    p0a_completed = parse_time(p0a_replay["updated_at_utc"], "replayed P0A completion")
    p0t_created = parse_time(p0t_replay["created_at_utc"], "replayed P0T creation")
    p0t_completed = parse_time(p0t_replay["updated_at_utc"], "replayed P0T completion")
    authorized = parse_time(value["a0_authorized_at_utc"], "A0 authority time")
    a0_created = parse_time(a0_replay["created_at_utc"], "replayed A0 publication creation")
    publication_time = parse_time(a0_replay["updated_at_utc"], "replayed A0 publication completion")
    if p0a_replay["run_id"] == p0t_replay["run_id"] or not p0a_completed < p0t_created <= p0t_completed < authorized <= a0_created <= publication_time:
        raise PublicationError("live-replayed P0A/P0T/A0 server chronology is invalid")
    tree = git(repo, "show", "-s", "--format=%T", commit).decode().strip()
    if OID.fullmatch(tree) is None:
        raise PublicationError("A0 root tree is not an exact lowercase SHA-1 object ID")
    raw = commit_raw(repo, commit, A0_PATH)
    return {
        "schema": "c5k4-method-v1.5-validated-a0-identity-1.0",
        "commit": commit, "root_tree": tree,
        "artifact": {"path": A0_PATH, "sha256": hashlib.sha256(raw).hexdigest(), "canonical_sha256": value["a0_sha256"]},
        "authority_roster_sha256": p0a["authority_policy"]["authority_roster_sha256"],
        "ami_authority_binding_policy_template_sha256": value["ami_authority_binding_contract"]["policy_template_sha256"],
        "external_harness_verification_key_sha256": value["external_harness_authority"]["verification_key_sha256"],
        "nitrotpm_key_generation_attestation_sha256": value["external_harness_authority"]["nitrotpm_key_generation_attestation_sha256"],
        "nitrotpm_key_policy": value["external_harness_authority"]["key_policy"],
        "a0_authorized_at_utc": value["a0_authorized_at_utc"],
        "a0_publication_observed_at_utc": a0_replay["updated_at_utc"],
        "a0_publication_run_id": a0_replay["run_id"],
        "github_server_replay": {
            "api_version": "2022-11-28",
            "p0a": {key: p0a_replay[key] for key in ("run_id", "head_sha", "created_at_utc", "run_started_at_utc", "updated_at_utc", "captured_run_object_sha256", "captured_listing_sha256", "captured_ref_sha256", "api_projection_sha256")},
            "p0t": {key: p0t_replay[key] for key in ("run_id", "head_sha", "created_at_utc", "run_started_at_utc", "updated_at_utc", "captured_run_object_sha256", "captured_listing_sha256", "captured_ref_sha256", "api_projection_sha256")},
            "a0": {key: a0_replay[key] for key in ("run_id", "head_sha", "created_at_utc", "run_started_at_utc", "updated_at_utc", "captured_run_object_sha256", "captured_listing_sha256", "captured_ref_sha256", "api_projection_sha256")}
        },
        "status": value["status"], "activation_authority": value["activation_policy"]["activation_authority"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT); parser.add_argument("--commit")
    parser.add_argument("--stage", choices=["p0a", "p0t", "a0", "a0-observer", "a0-preview", "actions-observation", "actions-replay"], required=True)
    parser.add_argument("--require-authoritative", action="store_true")
    parser.add_argument("--authority-keys", type=Path)
    parser.add_argument("--print-identity", action="store_true")
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--p0t-commit")
    parser.add_argument("--artifact-kind", choices=["P0A", "P0T"])
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--publication-receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.stage == "actions-observation":
            if args.commit is None or args.artifact_kind is None or args.run_id is None:
                raise PublicationError("actions-observation requires --commit, --artifact-kind, and --run-id")
            print(json.dumps(compile_actions_observation(args.repo, kind=args.artifact_kind, commit=args.commit, run_id=args.run_id), indent=2, sort_keys=True))
        elif args.stage == "actions-replay":
            if args.commit is None or args.artifact_kind is None or args.artifact is None:
                raise PublicationError("actions-replay requires --commit, --artifact-kind, and --artifact")
            replay_actions_observation(args.repo, load(args.artifact), kind=args.artifact_kind, commit=args.commit)
        elif args.stage == "a0-preview":
            if args.artifact is None or args.p0t_commit is None or args.commit is not None or args.print_identity:
                raise PublicationError("a0-preview requires only --artifact and --p0t-commit")
            validate_a0_preview(args.repo, args.p0t_commit, load(args.artifact))
        elif args.commit is None:
            raise PublicationError("published stages require --commit")
        elif args.stage == "p0a": validate_p0a(args.repo, args.commit)
        elif args.stage == "p0t": validate_p0t(args.repo, args.commit)
        elif args.stage == "a0-observer": validate_a0_publication_structure(args.repo, args.commit)
        else:
            if args.print_identity:
                if args.publication_receipt is None:
                    raise PublicationError("--print-identity requires --publication-receipt")
                print(json.dumps(validated_a0_identity(args.repo, args.commit, require_authoritative=args.require_authoritative, authority_keys=args.authority_keys, publication_receipt=load(args.publication_receipt)), sort_keys=True, separators=(",", ":")))
            else:
                validate_a0(args.repo, args.commit, require_authoritative=args.require_authoritative, authority_keys=args.authority_keys)
    except (OSError, PublicationError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
