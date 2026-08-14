#!/usr/bin/env python3
"""Pure, inert verification boundary for the Method v1.5 controlled harness.

There is deliberately no listener, command-line entry point, JWKS client, or
target-corpus reader here.  An operational harness must inject a signature/JWKS
verifier, an authenticated public-chain binding, a durable one-shot replay
ledger, and an executor.  The committed PRE_P1 contract rejects all requests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Protocol

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "results/benchmark/v1.5-protocol/controlled-harness-service-contract.json"
CONTRACT_SCHEMA_PATH = ROOT / "schemas/benchmark-controlled-harness-service-contract-v1.5.schema.json"
PUBLIC_FILES = ("publication-manifest.json", "quota-certificate.json", "receipt.json")
MODES = {"CAPTURE", "TERMINAL_CHRONOLOGY_GAP"}
FORBIDDEN_KEYS = {
    "cluster_id", "cluster_ids", "declarations", "records", "statement",
    "statement_text", "target", "target_id", "target_identity", "target_identities",
    "outcome", "outcomes", "ranking", "rankings", "logs", "stdout", "stderr",
}


class HarnessError(ValueError):
    """A fail-closed authentication, chronology, replay, or boundary failure."""


class JWKSVerifier(Protocol):
    """Inject signature/JWKS plus expiry, not-before, issuer, and audience checks."""

    def __call__(self, token: str, *, issuer: str, audience: str) -> dict[str, Any]: ...


class ReplayLedger(Protocol):
    """Atomically and durably reserve both request digest and scheduled tick."""

    def reserve(self, *, scheduled_for_utc: str, request_sha256: str, workflow_run_id: str) -> bool: ...


Executor = Callable[[dict[str, Any], str], dict[str, Any]]


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError(f"invalid {label}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"invalid {label}")
    return value


def validate(value: dict[str, Any], schema_path: Path, label: str) -> None:
    try:
        Draft7Validator(load_object(schema_path, "schema")).validate(value)
    except Exception as exc:
        raise HarnessError(f"{label} fails its exact schema") from exc


def validate_contract(contract: dict[str, Any], *, require_operational: bool) -> None:
    validate(contract, CONTRACT_SCHEMA_PATH, "service contract")
    operational = contract["status"] == "FROZEN_P1_EXECUTABLE"
    if require_operational and not operational:
        raise HarnessError("controlled harness is PRE_P1 and nonoperational")
    if operational:
        transport = contract["transport"]
        oidc = contract["oidc"]
        p1t = contract["binding"]["p1t_commit"]
        if transport["listener_permitted"] is not True:
            raise HarnessError("operational contract does not permit its listener")
        if not isinstance(transport["https_endpoint"], str) or not transport["https_endpoint"].startswith("https://"):
            raise HarnessError("operational endpoint is not exact HTTPS")
        if not isinstance(transport["tls_spki_sha256"], str) or not transport["tls_spki_sha256"].startswith("sha256//"):
            raise HarnessError("operational endpoint is not SPKI-pinned")
        if not isinstance(oidc["audience_prefix"], str) or not oidc["audience_prefix"]:
            raise HarnessError("OIDC audience prefix is not frozen")
        if not isinstance(oidc["workflow_ref"], str) or not oidc["workflow_ref"]:
            raise HarnessError("workflow OIDC claim is not frozen")
        if not isinstance(p1t, str) or len(p1t) != 40 or any(c not in "0123456789abcdef" for c in p1t):
            raise HarnessError("P1T binding is not frozen")


def parse_request(raw: bytes, contract: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if not raw or len(raw) > contract["request"]["max_bytes"]:
        raise HarnessError("request exceeds the exact size boundary")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError("request is not UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise HarnessError("request is not one JSON object")
    if canonical_json(value) != raw:
        raise HarnessError("request bytes are not canonical JSON")
    validate(value, ROOT / contract["request"]["schema_path"], "request")
    if value["mode"] not in MODES:
        raise HarnessError("request mode is not frozen")
    return value, sha256(raw)


def verify_claims(
    token: str, request: dict[str, Any], request_sha256: str,
    contract: dict[str, Any], verifier: JWKSVerifier,
) -> dict[str, Any]:
    oidc = contract["oidc"]
    audience = f"{oidc['audience_prefix']}:{request_sha256}"
    try:
        claims = verifier(token, issuer=oidc["issuer"], audience=audience)
    except Exception as exc:
        raise HarnessError("OIDC signature/JWKS verification failed") from exc
    if not isinstance(claims, dict):
        raise HarnessError("OIDC verifier did not return claims")
    expected = {
        "iss": oidc["issuer"], "aud": audience,
        "repository": oidc["repository"], "ref": oidc["ref"],
        "workflow_ref": oidc["workflow_ref"], "event_name": oidc["event_name"],
        "run_attempt": oidc["run_attempt"], "run_id": request["workflow_run_id"],
    }
    for key, value in expected.items():
        if claims.get(key) != value:
            raise HarnessError(f"OIDC claim mismatch: {key}")
    return claims


def verify_public_binding(request: dict[str, Any], binding: dict[str, Any], contract: dict[str, Any]) -> None:
    exact_keys = {
        "p1t_commit", "public_chain_proof_sha256", "public_tip_commit",
        "scheduled_for_utc", "mode", "chain_terminal",
    }
    if not isinstance(binding, dict) or set(binding) != exact_keys:
        raise HarnessError("public-chain binding shape is not exact")
    expected = {
        "p1t_commit": request["p1t_commit"],
        "public_chain_proof_sha256": request["public_chain_proof_sha256"],
        "public_tip_commit": request["public_tip_commit"],
        "scheduled_for_utc": request["scheduled_for_utc"],
        "mode": request["mode"],
    }
    for key, value in expected.items():
        if binding.get(key) != value:
            raise HarnessError(f"public-chain binding mismatch: {key}")
    if request["p1t_commit"] != contract["binding"]["p1t_commit"]:
        raise HarnessError("request is not bound to frozen P1T")
    if binding["chain_terminal"] is not False:
        raise HarnessError("public checkpoint chain is already terminal")


def assert_target_blind(value: Any) -> None:
    if isinstance(value, dict):
        keys = {str(key).casefold() for key in value}
        if keys.intersection(FORBIDDEN_KEYS):
            raise HarnessError("bounded response contains target-bearing or diagnostic content")
        for child in value.values():
            assert_target_blind(child)
    elif isinstance(value, list):
        for child in value:
            assert_target_blind(child)


def validate_response(response: dict[str, Any], request_sha256: str, contract: dict[str, Any]) -> bytes:
    if not isinstance(response, dict) or tuple(sorted(response)) != tuple(sorted(PUBLIC_FILES)):
        raise HarnessError("executor did not return the exact bounded three-file object")
    validate(response, ROOT / contract["response"]["schema_path"], "response")
    if response["publication-manifest.json"].get("request_sha256") != request_sha256:
        raise HarnessError("publication manifest is not bound to the request digest")
    assert_target_blind(response)
    raw = canonical_json(response)
    if len(raw) > contract["response"]["max_bytes"]:
        raise HarnessError("bounded response exceeds its size limit")
    return raw


def verify_and_execute(
    *, raw_request: bytes, oidc_token: str, public_binding: dict[str, Any],
    verifier: JWKSVerifier, replay_ledger: ReplayLedger, executor: Executor,
    contract: dict[str, Any] | None = None,
) -> bytes:
    """Authenticate one request, consume its tick once, and return bounded JSON.

    The durable replay reservation intentionally occurs before executor entry
    and is never rolled back, even if execution or response validation fails.
    """

    selected = load_object(CONTRACT_PATH, "service contract") if contract is None else contract
    validate_contract(selected, require_operational=True)
    request, request_sha256 = parse_request(raw_request, selected)
    verify_claims(oidc_token, request, request_sha256, selected, verifier)
    verify_public_binding(request, public_binding, selected)
    if not replay_ledger.reserve(
        scheduled_for_utc=request["scheduled_for_utc"],
        request_sha256=request_sha256,
        workflow_run_id=request["workflow_run_id"],
    ):
        raise HarnessError("duplicate request or checkpoint tick")
    response = executor(request, request_sha256)
    return validate_response(response, request_sha256, selected)
