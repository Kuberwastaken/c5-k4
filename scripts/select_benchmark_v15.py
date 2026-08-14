#!/usr/bin/env python3
"""Offline Method v1.5 future-drand selection and C1 freeze compiler.

The compiler never fetches entropy and never opens target statements.  It
accepts an already verified, two-relay/BLS drand artifact only after validating
the exact C0T and its embedded pre-entropy pool.  Selection inherits the exact
v1.4 sampler bytes authenticated by P1A.  C1A/C1T contain opaque identities
only; private locators remain sealed.  The envelope-closure command remains
explicitly non-executable until separate signed production acceptances exist.
"""

from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any, Mapping

import jsonschema
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/benchmark-c1-v1.5.schema.json"
C0T_SCHEMA_PATH = ROOT / "schemas/benchmark-v1.5-c0.schema.json"
POOL_SCHEMA_PATH = ROOT / "schemas/benchmark-pass-pool-v1.5.schema.json"
C1_SCHEMA = "c5k4-method-v1.5-c1-1.0"
DRAND_SCHEMA = "c5k4-drand-randomness-artifact-1"
IDENTITY_SCHEMA = "c5k4-method-v1.5-sealed-private-identity-transition-1.0"
CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
OFFLINE_DRAND_REPLAY = ROOT / "tools/benchmark-drand/verify-v15-artifact.mjs"
PRIVATE_TRANSITION_SCHEMA_PATH = ROOT / "schemas/benchmark-private-c1-transition-v1.5.schema.json"
PRIVATE_TRANSITION_DOMAIN = b"c5k4/method-v1.5/private-identity-transition/v1"
C1_AUTHORITY_SCHEMA_PATH = ROOT / "schemas/benchmark-c1-authority-receipt-v1.5.schema.json"
C1_AUTHORITY_DOMAIN = b"c5k4/method-v1.5/C1-authority/v1"
ENVELOPE_FREEZE_SCHEMA_PATH = ROOT / "schemas/benchmark-c1-envelope-freeze-v1.5.schema.json"
PRIVATE_CUSTODIAN_DOMAIN = b"c5k4/method-v1.5/private-custodian/v1"
AUTHORITY_PROJECTION_DOMAIN = b"c5k4/method-v1.5/C1-authority-projection/v1"
STRATA = (
    "GRAPH_SCALAR_INEQUALITY", "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL", "AUTOMATA_GAME_PROCESS", "FINITE_COMBINATORIAL",
)
QUOTAS = dict(zip(STRATA, (3, 3, 2, 2, 2)))
SEMANTIC_KEYS = {
    "statement", "statement_text", "declaration", "declarations", "theorem",
    "conjecture", "target_semantics", "proof_route", "residual", "outcome",
    "outcomes", "candidate", "candidates", "transformation", "parameter_grid",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class C1Error(ValueError):
    """A chronology, entropy, identity, or freeze invariant failed closed."""


def canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(value: Mapping[str, Any], field: str = "artifact_sha256") -> str:
    return sha256(canonical({key: child for key, child in value.items() if key != field}))


def strict(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in rows:
            if key in result:
                raise C1Error(f"{label} has duplicate key {key!r}")
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise C1Error(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise C1Error(f"{label} must be one object")
    return value


def schema_validate(value: Any, path: Path, label: str) -> None:
    schema = strict(path.read_bytes(), f"{label} schema")
    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(value), key=lambda e: list(e.absolute_path))
    if errors:
        where = ".".join(map(str, errors[0].absolute_path)) or "$"
        raise C1Error(f"{label} schema failure at {where}: {errors[0].message}")


def reject_semantics(value: Any, trail: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            folded = key.casefold().replace("-", "_")
            if folded in SEMANTIC_KEYS:
                raise C1Error(f"target semantics forbidden before C1: {'.'.join((*trail, key))}")
            reject_semantics(child, (*trail, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_semantics(child, (*trail, str(index)))


def parse_time(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise C1Error(f"{label} must be UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise C1Error(f"{label} is invalid") from exc
    return parsed.astimezone(timezone.utc)


def repo_path(recorded: str) -> Path:
    pure = PurePosixPath(recorded)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or pure.as_posix() != recorded:
        raise C1Error("repository path is not normalized")
    path = (ROOT / Path(*pure.parts)).resolve()
    if ROOT not in path.parents:
        raise C1Error("repository path escapes root")
    return path


def ref(path: Path, label: str) -> dict[str, str]:
    if not path.is_file() or path.is_symlink():
        raise C1Error(f"{label} is not a regular file")
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise C1Error(f"{label} must be repository-local") from exc
    return {"path": relative, "sha256": sha256(path.read_bytes())}


def validate_c0t(value: dict[str, Any]) -> dict[str, Any]:
    schema_validate(value, C0T_SCHEMA_PATH, "C0T")
    expected = digest(value)
    if value.get("artifact_sha256") != expected:
        raise C1Error("C0T self digest mismatch")
    reject_semantics(value)
    boundary = value["publication_boundary"]
    if boundary != {
        "target_blind": True, "entropy_present": False, "selection_present": False,
        "ranking_present": False, "statement_text_present": False,
        "target_semantics_present": False, "outcomes_present": False,
    }:
        raise C1Error("C0T is not the exact target-blind pre-entropy boundary")
    contract = value["randomness_contract"]
    if contract["value"] is not None or contract["entropy_used"] is not False or contract["selection_performed"] is not False:
        raise C1Error("C0T already contains entropy or selection")
    return value


def authenticate_canonical_c0(
    c0a_path: Path, c0t_path: Path, c0t_commit: str, activation_receipt: Path,
    replay_input: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Delegate authority to C0's public strict live verifier.

    C1 never supplies a fetch callback or caller-authored capture bytes.  The
    C0 verifier owns the complete server replay: run, exhaustive run listing,
    repository identity, public ref, effective branch rules, and comparison
    ancestry, in addition to exact committed C0A/C0T/P1 inputs.
    """
    verifier_path = ROOT / "scripts/verify_benchmark_v15_c0_publication.py"
    spec = importlib.util.spec_from_file_location("c5k4_v15_canonical_c0_verifier", verifier_path)
    if spec is None or spec.loader is None:
        raise C1Error("canonical C0 verifier is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    c0t = strict(c0t_path.read_bytes(), "C0T")
    try:
        module.validate_c0t(
            c0t, activation_receipt_path=activation_receipt, replay_input_path=replay_input,
            c0t_commit=c0t_commit, artifact_path=c0t_path,
        )
        c0a, c0a_raw, _activation, _activation_raw = module.load_c0a(
            c0t["c0a_commit"], activation_receipt, replay_input,
        )
    except Exception as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise C1Error(f"canonical C0 replay failed: {exc}") from exc
    if c0a_path.resolve() != (ROOT / module.C0A_PATH).resolve() or c0a_path.read_bytes() != c0a_raw:
        raise C1Error("supplied C0A path/bytes differ from canonical committed C0A")
    return c0a, c0t


def validate_pool(pool: dict[str, Any], c0t: dict[str, Any]) -> list[dict[str, Any]]:
    schema_validate(pool, POOL_SCHEMA_PATH, "pass pool")
    if pool.get("pool_sha256") != digest(pool, "pool_sha256"):
        raise C1Error("pass-pool self digest mismatch")
    reject_semantics(pool)
    binding = c0t["pass_pool_binding"]
    if binding["pool_sha256"] != pool["pool_sha256"] or binding["canonical_object_sha256"] != sha256(canonical(pool)):
        raise C1Error("C0T does not bind the exact pre-entropy pass pool")
    if pool["selection_contract"]["quotas"] != QUOTAS or pool["selection_contract"]["selection_permitted"] is not False:
        raise C1Error("pass pool does not preserve the frozen 3/3/2/2/2 pre-entropy contract")
    rows = pool["clusters"]
    if len({row["cluster_id"] for row in rows}) != len(rows) or len({row["identity_sha256"] for row in rows}) != len(rows):
        raise C1Error("pass pool duplicates an identity")
    if any(sum(row["stratum"] == stratum for row in rows) < QUOTAS[stratum] for stratum in STRATA):
        raise C1Error("pass pool no longer satisfies every quota")
    return rows


def replay_drand(c0a: dict[str, Any], c0t: dict[str, Any], c0t_commit: str, value: dict[str, Any]) -> str:
    bundle = {"artifact": value, "c0a": c0a, "c0t": c0t, "c0t_commit": c0t_commit}
    try:
        completed = subprocess.run(
            ["/usr/bin/node", str(OFFLINE_DRAND_REPLAY)], input=canonical(bundle),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=30,
            env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C"},
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        detail = getattr(exc, "stderr", b"").decode(errors="replace").strip()
        raise C1Error(f"offline drand BLS replay failed: {detail}") from exc
    observed = completed.stdout.decode().strip()
    if HEX64.fullmatch(observed) is None:
        raise C1Error("offline drand verifier returned an invalid receipt")
    return observed


def validate_randomness(value: dict[str, Any], c0t: dict[str, Any], c0t_commit: str, *, c0a: dict[str, Any] | None = None) -> bytes:
    if value.get("schema_version") != DRAND_SCHEMA or set(value) != {
        "schema_version", "c0_binding", "retrieval", "chain", "round", "round_closes_at_utc",
        "beacon", "beacon_canonical_sha256", "randomness", "randomness_sha256",
        "signature_sha256", "verification",
    }:
        raise C1Error("verified randomness artifact has an invalid closed shape")
    contract = c0t["randomness_contract"]
    if value["c0_binding"] != {
        "artifact_commit": c0t["c0a_commit"], "attestation_commit": c0t_commit,
        "published_at_utc": c0t["publication_observation"]["github_run"]["completed_at_utc"],
    }:
        raise C1Error("randomness artifact does not bind exact C0A/C0T chronology")
    if value["round"] != contract["round"] or value["round_closes_at_utc"] != contract["round_closes_at_utc"]:
        raise C1Error("randomness round differs from C0T")
    if value.get("chain", {}).get("hash") != CHAIN_HASH:
        raise C1Error("randomness chain differs from the frozen drand chain")
    if parse_time(value["retrieval"].get("retrieved_at_utc"), "randomness retrieval") < parse_time(contract["round_closes_at_utc"], "drand close"):
        raise C1Error("randomness was obtained before the future round closed")
    relays = value["retrieval"].get("relays")
    if not isinstance(relays, list) or [row.get("url") for row in relays] != ["https://api.drand.sh", "https://api2.drand.sh"]:
        raise C1Error("randomness lacks the exact two official relay captures")
    required = {
        "c0_contract", "future_round", "exact_round", "official_relay_equality",
        "frozen_chain_info", "bls_signature", "randomness_equals_sha256_signature",
    }
    checks = value.get("verification")
    if not isinstance(checks, dict) or any(checks.get(key) is not True for key in required):
        raise C1Error("randomness verifier did not pass every inherited check")
    beacon = value.get("beacon")
    if not isinstance(beacon, dict) or beacon.get("round") != contract["round"]:
        raise C1Error("beacon round mismatch")
    randomness = beacon.get("randomness")
    signature = beacon.get("signature")
    if not isinstance(randomness, str) or HEX64.fullmatch(randomness) is None:
        raise C1Error("beacon randomness is malformed")
    if not isinstance(signature, str) or len(signature) != 192:
        raise C1Error("beacon signature is malformed")
    try:
        signature_raw = bytes.fromhex(signature)
    except ValueError as exc:
        raise C1Error("beacon signature is malformed") from exc
    if sha256(signature_raw) != randomness or value["randomness"] != randomness:
        raise C1Error("randomness is not SHA256 of the verified beacon signature")
    if value["randomness_sha256"] != sha256(randomness.encode()) or value["signature_sha256"] != sha256(signature_raw):
        raise C1Error("randomness artifact digest mismatch")
    if value["beacon_canonical_sha256"] != sha256(json.dumps(beacon, sort_keys=True, separators=(",", ":")).encode()):
        raise C1Error("beacon canonical digest mismatch")
    if c0a is not None:
        replay_drand(c0a, c0t, c0t_commit, value)
    return bytes.fromhex(randomness)


def load_inherited_sampler(p1a: dict[str, Any]) -> tuple[Any, dict[str, str], dict[str, str]]:
    try:
        components = p1a["inherited_v1_4"]["components"]
        row = components["selector"]
        fetcher = components["drand_fetcher"]
    except (KeyError, TypeError) as exc:
        raise C1Error("P1A lacks the inherited v1.4 selector") from exc
    path = repo_path(row.get("path"))
    if row.get("sha256") != sha256(path.read_bytes()) or row.get("content_class") != "INHERITED_V1_4_EXACT":
        raise C1Error("P1A selector binding differs from current exact bytes")
    spec = importlib.util.spec_from_file_location("c5k4_v15_inherited_v14_selector", path)
    if spec is None or spec.loader is None:
        raise C1Error("cannot load inherited selector")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if tuple(module.STRATA) != STRATA or module.QUOTAS != QUOTAS:
        raise C1Error("inherited selector quotas/strata differ from v1.5 freeze")
    fetcher_path = repo_path(fetcher.get("path"))
    if fetcher.get("sha256") != sha256(fetcher_path.read_bytes()) or fetcher.get("content_class") != "INHERITED_V1_4_EXACT":
        raise C1Error("P1A drand verifier binding differs from current exact bytes")
    return module, {"path": row["path"], "sha256": row["sha256"]}, {"path": fetcher["path"], "sha256": fetcher["sha256"]}


def private_transition_digest(value: Mapping[str, Any]) -> str:
    return sha256(canonical({key: child for key, child in value.items() if key not in {"artifact_sha256", "signature"}}))


def _decode_embedded(value: Any, label: str) -> tuple[dict[str, Any], bytes]:
    if not isinstance(value, dict) or value.get("encoding") != "BASE64_CANONICAL_JSON_UTF8":
        raise C1Error(f"{label} is not canonical embedded JSON")
    payload_field = "canonical_package_base64" if "canonical_package_base64" in value else "canonical_json_base64"
    digest_field = "package_sha256" if payload_field == "canonical_package_base64" else "sha256"
    try:
        raw = base64.b64decode(value[payload_field], validate=True)
    except (KeyError, ValueError) as exc:
        raise C1Error(f"{label} base64 is invalid") from exc
    child = strict(raw, label)
    if raw != canonical(child) or value.get(digest_field) != sha256(raw):
        raise C1Error(f"{label} canonical bytes/digest mismatch")
    return child, raw


def derive_authority_projection(p1a: dict[str, Any]) -> dict[str, Any]:
    """Project C1 authority only from the already authenticated P1 readiness bytes.

    The canonical C0 verifier has already replayed full exact-C P1 validation,
    including the public-A0 authority signatures and immutable evidence objects.
    C1 therefore consumes their signed projection; it never accepts a new root.
    """
    package, package_raw = _decode_embedded(p1a.get("candidate_base_readiness"), "P1 readiness package")
    evidence, evidence_raw = _decode_embedded(package.get("operational_evidence"), "P1 operational evidence")
    signatures = package.get("authority_signatures")
    harness = [row for row in signatures if isinstance(row, dict) and row.get("signer_class") == "CONTROLLED_HARNESS_READINESS_KEY"] if isinstance(signatures, list) else []
    if len(harness) != 1 or HEX64.fullmatch(str(harness[0].get("verification_key_sha256"))) is None:
        raise C1Error("P1 readiness package lacks one authenticated controlled-harness authority")
    rows = evidence.get("evidence")
    if not isinstance(rows, list) or len({row.get("domain") for row in rows if isinstance(row, dict)}) != len(rows):
        raise C1Error("P1 operational evidence domain set is duplicate or invalid")
    by_domain = {row["domain"]: row for row in rows}
    try:
        custody_row = by_domain["BROKER_CUSTODY_AND_CAPTURE_REPLAY"]
        custody = custody_row["artifact"]["object_sha256"]
        custodian_key = custody_row["issuer"]["verification_key_sha256"]
        immutable = by_domain["IMMUTABLE_WORM_STORE"]["artifact"]["object_sha256"]
        root = package["authority_root"]
    except (KeyError, TypeError) as exc:
        raise C1Error("P1 readiness package lacks authenticated custody/immutable authority") from exc
    if any(HEX64.fullmatch(str(item)) is None for item in (custody, custodian_key, immutable, root.get("sha256"))):
        raise C1Error("P1 authority projection contains malformed authenticated digests")
    value = {
        "source": "CANONICAL_C0_AUTHENTICATED_P1_READINESS",
        "p1_readiness_package_sha256": sha256(package_raw),
        "p1_operational_evidence_sha256": sha256(evidence_raw),
        "authority_root": copy.deepcopy(root),
        "authority_key_sha256": harness[0]["verification_key_sha256"],
        "custodian_key_sha256": custodian_key,
        "custody_locator": copy.deepcopy(custody_row["artifact"]),
        "immutable_locator": copy.deepcopy(by_domain["IMMUTABLE_WORM_STORE"]["artifact"]),
        "custody_binding_sha256": custody,
        "immutable_acceptance_sha256": immutable,
    }
    value["projection_sha256"] = sha256(AUTHORITY_PROJECTION_DOMAIN + b"\0" + canonical(value))
    return value


def validate_private_transition(
    value: dict[str, Any], rows: list[dict[str, Any]], pool_sha: str,
    public_key: bytes, authority: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    schema_validate(value, PRIVATE_TRANSITION_SCHEMA_PATH, "private transition")
    if value.get("schema") != IDENTITY_SCHEMA or value.get("status") != "SEALED_PRE_C1_IDENTITY_MAP" or value.get("pool_sha256") != pool_sha:
        raise C1Error("sealed private identity transition lacks exact pool authority")
    if value.get("artifact_sha256") != private_transition_digest(value):
        raise C1Error("sealed private identity transition self digest mismatch")
    expected_projection = authority["projection_sha256"]
    if (
        value.get("authority_projection_sha256") != expected_projection
        or value.get("custody_binding_sha256") != authority["custody_binding_sha256"]
        or value.get("immutable_acceptance_sha256") != authority["immutable_acceptance_sha256"]
    ):
        raise C1Error("sealed private identity transition differs from canonical C0/P1 authority projection")
    if len(public_key) != 32 or value["signature"]["key_sha256"] != sha256(public_key) or sha256(public_key) != authority["authority_key_sha256"]:
        raise C1Error("sealed private identity transition key binding mismatch")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            base64.b64decode(value["signature"]["signature_base64"], validate=True),
            PRIVATE_TRANSITION_DOMAIN + b"\0" + bytes.fromhex(value["artifact_sha256"]),
        )
    except (ValueError, InvalidSignature) as exc:
        raise C1Error("sealed private identity transition signature mismatch") from exc
    reject_semantics(value)
    identities = value.get("identities")
    if not isinstance(identities, list):
        raise C1Error("sealed identity transition lacks identities")
    by_id = {row.get("cluster_id"): row for row in identities if isinstance(row, dict)}
    pool_by_id = {row["cluster_id"]: row for row in rows}
    if set(by_id) != set(pool_by_id) or len(by_id) != len(identities):
        raise C1Error("sealed identity transition differs from complete pool")
    for cluster_id, item in by_id.items():
        if set(item) != {"cluster_id", "identity_sha256", "private_locator_sha256"}:
            raise C1Error("sealed identity row has an invalid shape")
        if item["identity_sha256"] != pool_by_id[cluster_id]["identity_sha256"] or HEX64.fullmatch(str(item["private_locator_sha256"])) is None:
            raise C1Error("sealed identity row does not bind pool identity and private locator")
    return by_id


def compile_c1a(
    c0a_raw: bytes, c0t_raw: bytes, c0t_commit: str, p1a_raw: bytes, randomness_raw: bytes,
    private_transition_raw: bytes, private_transition_key: bytes, *, c1a_path: str, c1t_path: str,
) -> dict[str, Any]:
    if HEX40.fullmatch(c0t_commit) is None:
        raise C1Error("C0T commit must be an exact SHA-1 object ID")
    c0t = validate_c0t(strict(c0t_raw, "C0T"))
    if c0t["c0a"]["sha256"] != sha256(c0a_raw):
        raise C1Error("C0T does not bind exact C0A bytes")
    c0a = strict(c0a_raw, "C0A")
    if c0a.get("artifact_kind") != "C0A" or c0a.get("artifact_sha256") != digest(c0a):
        raise C1Error("C0A is not a self-authenticating pre-entropy artifact")
    reject_semantics(c0a)
    pool = c0a.get("pass_pool")
    if not isinstance(pool, dict):
        raise C1Error("C0A does not embed the exact pass pool")
    rows = validate_pool(pool, c0t)
    p1a = strict(p1a_raw, "P1A")
    p1_binding = pool.get("p1_binding")
    if not isinstance(p1_binding, dict) or p1_binding.get("p1a", {}).get("sha256") != sha256(p1a_raw):
        raise C1Error("supplied P1A bytes differ from the canonical C0 pass-pool binding")
    if c0t.get("p1_activation", {}).get("p1r") != p1_binding.get("p1r") or c0t.get("p1_activation", {}).get("p1r_commit") != p1_binding.get("p1r_commit"):
        raise C1Error("C0T P1R ancestry differs from the pass-pool P1A/P1R binding")
    sampler, sampler_ref, fetcher_ref = load_inherited_sampler(p1a)
    # Entropy closes and validates before private identity bytes are decoded.
    seed = validate_randomness(strict(randomness_raw, "verified randomness"), c0t, c0t_commit, c0a=c0a)
    private = strict(private_transition_raw, "sealed private identity transition")
    authority = derive_authority_projection(p1a)
    private_by_id = validate_private_transition(private, rows, pool["pool_sha256"], private_transition_key, authority)
    selected: list[dict[str, Any]] = []
    strata_evidence: list[dict[str, Any]] = []
    for index, stratum in enumerate(STRATA):
        candidates = [{"cluster_id": row["cluster_id"], "identity_sha256": row["identity_sha256"]} for row in rows if row["stratum"] == stratum]
        shuffled, consumption = sampler.shuffle_rows(candidates, seed, index)
        quota = QUOTAS[stratum]
        for position, row in enumerate(shuffled[:quota], 1):
            selected.append({**row, "stratum": stratum, "shuffle_position": position})
        strata_evidence.append({"stratum": stratum, "quota": quota, "eligible_count": len(shuffled), "entropy_consumption": consumption})
    if len(selected) != 12 or len({row["cluster_id"] for row in selected}) != 12:
        raise C1Error("selection did not produce twelve unique clusters")
    private_selected = [{"cluster_id": row["cluster_id"], "identity_sha256": row["identity_sha256"], "private_locator_sha256": private_by_id[row["cluster_id"]]["private_locator_sha256"]} for row in selected]
    value = {
        "schema": C1_SCHEMA, "artifact_kind": "C1A", "protocol_version": "1.5",
        "status": "C1_SELECTION_COMPILED_AWAITING_ATTESTATION", "production_permitted": False,
        "c0t": {"commit": c0t_commit, "sha256": sha256(c0t_raw)},
        "pre_entropy_pool": {"pool_sha256": pool["pool_sha256"], "canonical_sha256": sha256(canonical(pool)), "cluster_count": len(rows)},
        "inherited_sampler": sampler_ref,
        "randomness": {"artifact_sha256": sha256(randomness_raw), "round": c0t["randomness_contract"]["round"], "round_closes_at_utc": c0t["randomness_contract"]["round_closes_at_utc"], "randomness_sha256": sha256(seed.hex().encode()), "inherited_drand_verifier": fetcher_ref, "offline_replay": {"path": OFFLINE_DRAND_REPLAY.relative_to(ROOT).as_posix(), "sha256": sha256(OFFLINE_DRAND_REPLAY.read_bytes())}},
        "quotas": QUOTAS, "strata": strata_evidence, "selected_clusters": selected,
        "sealed_private_identity_transition": {"artifact_sha256": sha256(private_transition_raw), "transition_sha256": private["artifact_sha256"], "selected_binding_sha256": sha256(canonical(private_selected)), "private_locators_disclosed": False, "authority_projection_sha256": authority["projection_sha256"], "custody_binding_sha256": authority["custody_binding_sha256"], "immutable_acceptance_sha256": authority["immutable_acceptance_sha256"], "authority_key_sha256": authority["authority_key_sha256"]},
        "publication_topology": {"c0t_commit": c0t_commit, "c1a_path": c1a_path, "c1t_path": c1t_path, "c1a_change": "ADD_EXACTLY_ONE_C1A_PATH", "c1t_change": "ADD_EXACTLY_ONE_C1T_PATH", "merge_commits_permitted": False},
        "semantic_boundary": {"opaque_identities_only": True, "statement_text_present": False, "target_semantics_present": False, "outcomes_present": False},
    }
    value["artifact_sha256"] = digest(value)
    validate_c1a(value)
    return value


def validate_c1a(value: dict[str, Any]) -> None:
    schema_validate(value, SCHEMA_PATH, "C1")
    if value.get("artifact_kind") != "C1A" or value.get("artifact_sha256") != digest(value):
        raise C1Error("C1A is invalid")
    counts = {stratum: sum(row["stratum"] == stratum for row in value["selected_clusters"]) for stratum in STRATA}
    identities = {row["identity_sha256"] for row in value["selected_clusters"]}
    positions = {
        stratum: sorted(row["shuffle_position"] for row in value["selected_clusters"] if row["stratum"] == stratum)
        for stratum in STRATA
    }
    expected_positions = {stratum: list(range(1, QUOTAS[stratum] + 1)) for stratum in STRATA}
    expected_order = [(stratum, position) for stratum in STRATA for position in expected_positions[stratum]]
    observed_order = [(row["stratum"], row["shuffle_position"]) for row in value["selected_clusters"]]
    if counts != QUOTAS or len({row["cluster_id"] for row in value["selected_clusters"]}) != 12 or len(identities) != 12 or positions != expected_positions or observed_order != expected_order:
        raise C1Error("C1A quotas or uniqueness do not replay")
    if value["production_permitted"] is not False:
        raise C1Error("unattested C1A cannot authorize production")


def compile_c1t(c1a: dict[str, Any], c1a_commit: str) -> dict[str, Any]:
    validate_c1a(c1a)
    if HEX40.fullmatch(c1a_commit) is None:
        raise C1Error("C1A commit must be exact")
    value = {
        "schema": C1_SCHEMA, "artifact_kind": "C1T", "protocol_version": "1.5",
        "status": "C1_FROZEN_TWELVE_CLUSTER_SELECTION", "production_permitted": False,
        "c1a": {"commit": c1a_commit, "sha256": sha256(canonical(c1a))},
        "c0t_commit": c1a["c0t"]["commit"], "quotas": copy.deepcopy(c1a["quotas"]),
        "selected_clusters": copy.deepcopy(c1a["selected_clusters"]),
        "sealed_private_identity_transition": copy.deepcopy(c1a["sealed_private_identity_transition"]),
        "attestation_policy": {"c1a_direct_parent_required": True, "nonmerge_required": True, "c1a_bytes_immutable": True, "allowed_c1t_changed_paths": [c1a["publication_topology"]["c1t_path"]]},
        "semantic_boundary": copy.deepcopy(c1a["semantic_boundary"]),
    }
    value["artifact_sha256"] = digest(value)
    validate_c1t(value, c1a)
    return value


def validate_c1t(value: dict[str, Any], c1a: dict[str, Any] | None = None) -> None:
    schema_validate(value, SCHEMA_PATH, "C1")
    if value.get("artifact_kind") != "C1T" or value.get("artifact_sha256") != digest(value):
        raise C1Error("C1T is invalid")
    selected = value["selected_clusters"]
    if value["quotas"] != QUOTAS or len(selected) != 12 or value["production_permitted"] is not False:
        raise C1Error("C1T does not preserve the frozen non-production selection")
    if len({row["cluster_id"] for row in selected}) != 12 or len({row["identity_sha256"] for row in selected}) != 12:
        raise C1Error("C1T contains duplicate cluster or identity artifacts")
    expected_order = [(stratum, position) for stratum in STRATA for position in range(1, QUOTAS[stratum] + 1)]
    if [(row["stratum"], row["shuffle_position"]) for row in selected] != expected_order:
        raise C1Error("C1T selection order/positions differ from the sampler contract")
    if c1a is None:
        raise C1Error("C1T validation requires exact independently replayed C1A bytes")
    validate_c1a(c1a)
    if (
        value["c1a"]["sha256"] != sha256(canonical(c1a))
        or value["c0t_commit"] != c1a["c0t"]["commit"]
        or value["quotas"] != c1a["quotas"]
        or selected != c1a["selected_clusters"]
        or value["sealed_private_identity_transition"] != c1a["sealed_private_identity_transition"]
        or value["semantic_boundary"] != c1a["semantic_boundary"]
        or value["attestation_policy"]["allowed_c1t_changed_paths"] != [c1a["publication_topology"]["c1t_path"]]
    ):
        raise C1Error("C1T does not exactly replay C1A selection and bindings")


def compile_c1_authority_receipt(
    c1a: dict[str, Any], c1t: dict[str, Any], c1t_commit: str, authority_private_key: bytes,
    authority: dict[str, Any],
) -> dict[str, Any]:
    validate_c1a(c1a); validate_c1t(c1t, c1a)
    if c1t["c1a"]["sha256"] != sha256(canonical(c1a)) or c1t["selected_clusters"] != c1a["selected_clusters"]:
        raise C1Error("C1 authority inputs do not preserve exact C1A selection")
    if len(authority_private_key) != 32:
        raise C1Error("C1 authority private key must be a raw Ed25519 seed")
    private_key = Ed25519PrivateKey.from_private_bytes(authority_private_key)
    public_key = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    transition = c1a["sealed_private_identity_transition"]
    if (
        sha256(public_key) != authority["authority_key_sha256"]
        or transition["authority_key_sha256"] != authority["authority_key_sha256"]
        or transition["authority_projection_sha256"] != authority["projection_sha256"]
        or transition["custody_binding_sha256"] != authority["custody_binding_sha256"]
        or transition["immutable_acceptance_sha256"] != authority["immutable_acceptance_sha256"]
    ):
        raise C1Error("C1 authority key/bindings were not projected by canonical C0/P1")
    value = {
        "schema": "c5k4-method-v1.5-c1-authority-receipt-1.0", "artifact_kind": "C1_AUTHORITY_RECEIPT", "protocol_version": "1.5",
        "status": "C1_SELECTION_SIGNED_AWAITING_ENVELOPE_FREEZE", "production_permitted": False,
        "c1t": {"commit": c1t_commit, "sha256": sha256(canonical(c1t))}, "c0t_commit": c1t["c0t_commit"],
        "randomness_artifact_sha256": c1a["randomness"]["artifact_sha256"], "sampler": copy.deepcopy(c1a["inherited_sampler"]),
        "quotas": copy.deepcopy(c1a["quotas"]), "ordered_selected_clusters_sha256": sha256(canonical(c1a["selected_clusters"])), "selected_cluster_count": 12,
        "authority_projection": copy.deepcopy(authority),
        "private_transition": {key: c1a["sealed_private_identity_transition"][key] for key in ("transition_sha256", "selected_binding_sha256", "custody_binding_sha256", "immutable_acceptance_sha256", "authority_key_sha256")},
        "envelope_freeze_complete": False,
    }
    payload = C1_AUTHORITY_DOMAIN + b"\0" + canonical(value)
    value["signature"] = {"algorithm": "Ed25519", "key_sha256": sha256(public_key), "signature_base64": base64.b64encode(private_key.sign(payload)).decode()}
    validate_c1_authority_receipt(value, public_key, authority)
    return value


def validate_c1_authority_receipt(value: dict[str, Any], public_key: bytes, authority: dict[str, Any]) -> None:
    schema_validate(value, C1_AUTHORITY_SCHEMA_PATH, "C1 authority receipt")
    if value.get("authority_projection") != authority or value["private_transition"]["authority_key_sha256"] != authority["authority_key_sha256"]:
        raise C1Error("C1 authority receipt differs from canonical C0/P1 authority projection")
    if (
        value["private_transition"]["custody_binding_sha256"] != authority["custody_binding_sha256"]
        or value["private_transition"]["immutable_acceptance_sha256"] != authority["immutable_acceptance_sha256"]
    ):
        raise C1Error("C1 authority receipt operational bindings differ from authenticated upstream bytes")
    if len(public_key) != 32 or value["signature"]["key_sha256"] != sha256(public_key) or sha256(public_key) != authority["authority_key_sha256"]:
        raise C1Error("C1 authority verification key mismatch")
    unsigned = {key: child for key, child in value.items() if key != "signature"}
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            base64.b64decode(value["signature"]["signature_base64"], validate=True),
            C1_AUTHORITY_DOMAIN + b"\0" + canonical(unsigned),
        )
    except (ValueError, InvalidSignature) as exc:
        raise C1Error("C1 authority signature mismatch") from exc
    if value["production_permitted"] is not False or value["envelope_freeze_complete"] is not False:
        raise C1Error("C1 authority receipt cannot bypass envelope freeze")


def verify_private_custodian_receipt(
    value: dict[str, Any], public_key: bytes, selected: list[dict[str, Any]], c1t_commit: str, run_freeze_commit: str,
    authority: dict[str, Any],
) -> None:
    required = {"status", "c1t_commit", "run_freeze_commit", "selected_cluster_ids", "selection_sha256", "ordered_selected_clusters_sha256", "authority_projection_sha256", "custody_binding_sha256", "immutable_acceptance_sha256", "signature"}
    if set(value) != required or value.get("status") != "PRIVATE_CUSTODIAN_SELECTED_TARGETS_ACCEPTED":
        raise C1Error("private custodian receipt shape/status invalid")
    selected_ids = [row["cluster_id"] for row in selected]
    if value["c1t_commit"] != c1t_commit or value["run_freeze_commit"] != run_freeze_commit or value["selected_cluster_ids"] != selected_ids:
        raise C1Error("private custodian receipt differs from C1/run-freeze selection")
    if value["selection_sha256"] != sha256(canonical(selected_ids)):
        raise C1Error("private custodian ordered selection digest mismatch")
    if value["ordered_selected_clusters_sha256"] != sha256(canonical(selected)):
        raise C1Error("private custodian identity/stratum selection digest mismatch")
    if (
        value["authority_projection_sha256"] != authority["projection_sha256"]
        or value["custody_binding_sha256"] != authority["custody_binding_sha256"]
        or value["immutable_acceptance_sha256"] != authority["immutable_acceptance_sha256"]
    ):
        raise C1Error("private custodian operational bindings differ from authenticated upstream bytes")
    signature = value.get("signature")
    if not isinstance(signature, dict) or set(signature) != {"algorithm", "key_sha256", "signature_base64"} or signature["algorithm"] != "Ed25519" or signature["key_sha256"] != sha256(public_key) or sha256(public_key) != authority["custodian_key_sha256"]:
        raise C1Error("private custodian signature binding invalid")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            base64.b64decode(signature["signature_base64"], validate=True),
            PRIVATE_CUSTODIAN_DOMAIN + b"\0" + canonical({key: child for key, child in value.items() if key != "signature"}),
        )
    except (ValueError, InvalidSignature) as exc:
        raise C1Error("private custodian signature mismatch") from exc


def compile_envelope_freeze(
    c1a: dict[str, Any], c1t: dict[str, Any], c1t_commit: str,
    c1_authority: dict[str, Any], c1_authority_key: bytes, authority: dict[str, Any],
    run_freeze_commit: str, envelope_closure_commit: str, matrix_path: Path,
    c1_authority_path: Path, envelope_paths: list[Path],
    private_custodian: dict[str, Any], private_custodian_key: bytes, private_custodian_path: Path,
    *, repository: Path = ROOT,
) -> dict[str, Any]:
    validate_c1t(c1t, c1a); validate_c1_authority_receipt(c1_authority, c1_authority_key, authority)
    if c1_authority["c1t"]["commit"] != c1t_commit or c1_authority["c1t"]["sha256"] != sha256(canonical(c1t)):
        raise C1Error("C1 authority receipt does not bind exact C1T")
    if HEX40.fullmatch(run_freeze_commit) is None or HEX40.fullmatch(envelope_closure_commit) is None or len(envelope_paths) != 12:
        raise C1Error("run-freeze commit or twelve-envelope closure absent")
    selected_ids = [row["cluster_id"] for row in c1t["selected_clusters"]]
    selected_digest = sha256(canonical(c1t["selected_clusters"]))
    if c1_authority["ordered_selected_clusters_sha256"] != selected_digest:
        raise C1Error("C1 authority ordered selection differs from C1T")
    verify_private_custodian_receipt(private_custodian, private_custodian_key, c1t["selected_clusters"], c1t_commit, run_freeze_commit, authority)
    verify_run_freeze_git_closure(
        repository, c1t_commit, run_freeze_commit, envelope_closure_commit,
        c1_authority_path, canonical(c1_authority), private_custodian_path, canonical(private_custodian),
        envelope_paths, matrix_path,
    )
    validator_path = ROOT / "scripts/validate_benchmark_v15_execution_envelope.py"
    spec = importlib.util.spec_from_file_location("c5k4_v15_c1_envelope_validator", validator_path)
    if spec is None or spec.loader is None:
        raise C1Error("execution-envelope validator unavailable")
    validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
    matrix_raw = matrix_path.read_bytes(); matrix = strict(matrix_raw, "capability matrix")
    validator.validate_matrix(matrix)
    rows = []
    for cluster_id, path in zip(selected_ids, envelope_paths):
        raw = path.read_bytes(); envelope = strict(raw, "execution envelope")
        try:
            validator.validate_envelope(envelope, matrix)
        except Exception as exc:
            raise C1Error(f"execution envelope invalid: {exc}") from exc
        target = envelope.get("target_execution")
        if envelope.get("status") != "POST_C1_RUN_FREEZE_DRAFT_NOT_EXECUTABLE" or not isinstance(target, dict):
            raise C1Error("envelope is not the exact non-executable post-C1 freeze shape")
        if target.get("cluster_id") != cluster_id or target.get("c1_attestation_commit") != c1t_commit or target.get("run_freeze_commit") != run_freeze_commit:
            raise C1Error("envelope C1/run-freeze/cluster binding mismatch")
        rows.append({"cluster_id": cluster_id, "path": path.resolve().relative_to(repository.resolve()).as_posix(), "file_sha256": sha256(raw), "envelope_sha256": envelope["envelope_sha256"]})
    value = {
        "schema": "c5k4-method-v1.5-c1-envelope-freeze-1.0", "status": "TWELVE_EXECUTION_ENVELOPES_BOUND_AWAITING_OPERATIONAL_ACCEPTANCE", "protocol_version": "1.5", "production_permitted": False,
        "c1_authority_receipt_sha256": sha256(canonical(c1_authority)), "c1t_commit": c1t_commit, "run_freeze_commit": run_freeze_commit, "envelope_closure_commit": envelope_closure_commit,
        "authority_projection": copy.deepcopy(authority),
        "ordered_selected_clusters_sha256": selected_digest, "capability_matrix": {"path": matrix_path.resolve().relative_to(repository.resolve()).as_posix(), "sha256": sha256(matrix_raw)},
        "private_custodian_receipt_sha256": sha256(canonical(private_custodian)), "envelopes": rows, "envelope_count": 12, "all_envelopes_non_executable": True,
    }
    value["artifact_sha256"] = digest(value); validate_envelope_freeze(value)
    return value


def validate_envelope_freeze(value: dict[str, Any]) -> None:
    schema_validate(value, ENVELOPE_FREEZE_SCHEMA_PATH, "envelope freeze")
    if value.get("artifact_sha256") != digest(value) or value.get("production_permitted") is not False:
        raise C1Error("envelope freeze is invalid or claims production authority")
    ids = [row["cluster_id"] for row in value["envelopes"]]
    if len(ids) != len(set(ids)) or len(ids) != 12:
        raise C1Error("envelope freeze does not bind twelve unique clusters")


def git(*args: str) -> bytes:
    return subprocess.run(["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(ROOT), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C"}).stdout


def git_at(repository: Path, *args: str) -> bytes:
    return subprocess.run(
        ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-C", str(repository), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent", "LANG": "C", "LC_ALL": "C"},
    ).stdout


def _relative_to(repository: Path, path: Path, label: str) -> str:
    if path.is_symlink() or not path.is_file():
        raise C1Error(f"{label} must be a regular non-symlink file")
    try:
        return path.resolve().relative_to(repository.resolve()).as_posix()
    except ValueError as exc:
        raise C1Error(f"{label} must be repository-local") from exc


def _exact_commit(repository: Path, commit: str, label: str) -> None:
    if HEX40.fullmatch(commit) is None:
        raise C1Error(f"{label} is not an exact object ID")
    try:
        if git_at(repository, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip() != commit:
            raise C1Error(f"{label} does not resolve exactly")
    except subprocess.CalledProcessError as exc:
        raise C1Error(f"{label} is unavailable") from exc


def _added_paths(repository: Path, commit: str) -> list[str]:
    lines = git_at(repository, "diff-tree", "--no-commit-id", "--name-status", "-r", commit).decode().splitlines()
    if any(not line.startswith("A\t") for line in lines):
        raise C1Error("freeze topology may only add its frozen artifacts")
    return [line.split("\t", 1)[1] for line in lines]


def verify_run_freeze_git_closure(
    repository: Path, c1t_commit: str, run_freeze_commit: str, envelope_closure_commit: str,
    authority_path: Path, authority_raw: bytes, custodian_path: Path, custodian_raw: bytes,
    envelope_paths: list[Path], matrix_path: Path,
) -> None:
    """Replay the non-circular C1T -> authority -> envelope closure topology."""
    for oid, label in ((c1t_commit, "C1T commit"), (run_freeze_commit, "run-freeze commit"), (envelope_closure_commit, "envelope-closure commit")):
        _exact_commit(repository, oid, label)
    if git_at(repository, "show", "-s", "--format=%P", run_freeze_commit).decode().split() != [c1t_commit]:
        raise C1Error("run-freeze commit must be the direct nonmerge child of C1T")
    if git_at(repository, "show", "-s", "--format=%P", envelope_closure_commit).decode().split() != [run_freeze_commit]:
        raise C1Error("envelope closure must be the direct nonmerge child of run-freeze")
    authority_rel = _relative_to(repository, authority_path, "C1 authority receipt")
    custodian_rel = _relative_to(repository, custodian_path, "private custodian receipt")
    envelope_rels = [_relative_to(repository, path, "execution envelope") for path in envelope_paths]
    if len(set(envelope_rels)) != 12:
        raise C1Error("envelope closure paths are not twelve unique repository paths")
    if _added_paths(repository, run_freeze_commit) != [authority_rel]:
        raise C1Error("run-freeze commit must add exactly the C1 authority receipt")
    expected_closure = sorted([custodian_rel, *envelope_rels])
    if sorted(_added_paths(repository, envelope_closure_commit)) != expected_closure:
        raise C1Error("envelope-closure commit does not add exactly custodian plus twelve envelopes")
    bound = [(run_freeze_commit, authority_rel, authority_raw), (envelope_closure_commit, custodian_rel, custodian_raw)]
    bound.extend((envelope_closure_commit, rel, path.read_bytes()) for rel, path in zip(envelope_rels, envelope_paths))
    matrix_rel = _relative_to(repository, matrix_path, "capability matrix")
    bound.append((run_freeze_commit, matrix_rel, matrix_path.read_bytes()))
    for commit, relative, raw in bound:
        try:
            committed = git_at(repository, "show", f"{commit}:{relative}")
        except subprocess.CalledProcessError as exc:
            raise C1Error(f"freeze closure lacks committed artifact {relative}") from exc
        if committed != raw:
            raise C1Error(f"freeze closure bytes differ for {relative}")


def verify_commit_artifact(value: dict[str, Any], commit: str, path: Path, expected_parent: str, kind: str) -> None:
    if HEX40.fullmatch(commit) is None or git("rev-parse", commit).decode().strip() != commit:
        raise C1Error(f"{kind} commit is not an exact object ID")
    if git("show", "-s", "--format=%P", commit).decode().split() != [expected_parent]:
        raise C1Error(f"{kind} must be a direct nonmerge child")
    relative = path.resolve().relative_to(ROOT).as_posix()
    if git("diff-tree", "--no-commit-id", "--name-status", "-r", commit).decode().splitlines() != [f"A\t{relative}"]:
        raise C1Error(f"{kind} commit must add exactly one frozen path")
    if git("show", f"{commit}:{relative}") != path.read_bytes() or strict(path.read_bytes(), kind) != value:
        raise C1Error(f"{kind} committed bytes differ")


def write_new(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise C1Error("output already exists; overwrite forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("compile-c1a")
    for name in ("c0a", "c0t", "p1a", "randomness", "private-transition", "private-transition-key"):
        a.add_argument("--" + name, type=Path, required=True)
    for name in ("activation-receipt", "pass-pool-replay-input"):
        a.add_argument("--" + name, type=Path, required=True)
    a.add_argument("--c0t-commit", required=True); a.add_argument("--c1a-path", required=True); a.add_argument("--c1t-path", required=True); a.add_argument("--output", type=Path, required=True)
    t = sub.add_parser("compile-c1t"); t.add_argument("--c1a", type=Path, required=True); t.add_argument("--c1a-commit", required=True); t.add_argument("--output", type=Path, required=True)
    for name in ("c0a", "c0t", "p1a", "randomness", "private-transition", "private-transition-key", "activation-receipt", "pass-pool-replay-input"):
        t.add_argument("--" + name, type=Path, required=True)
    t.add_argument("--c0t-commit", required=True)
    r = sub.add_parser("compile-c1-authority")
    r.add_argument("--c1a", type=Path, required=True); r.add_argument("--c1a-commit", required=True)
    r.add_argument("--c1t", type=Path, required=True); r.add_argument("--c1t-commit", required=True)
    r.add_argument("--authority-private-key", type=Path, required=True); r.add_argument("--output", type=Path, required=True)
    for name in ("c0a", "c0t", "p1a", "randomness", "private-transition", "private-transition-key", "activation-receipt", "pass-pool-replay-input"):
        r.add_argument("--" + name, type=Path, required=True)
    r.add_argument("--c0t-commit", required=True)
    freeze = sub.add_parser("compile-envelope-freeze")
    freeze.add_argument("--c1a", type=Path, required=True); freeze.add_argument("--c1a-commit", required=True)
    freeze.add_argument("--c1t", type=Path, required=True); freeze.add_argument("--c1t-commit", required=True)
    freeze.add_argument("--c1-authority", type=Path, required=True); freeze.add_argument("--c1-authority-key", type=Path, required=True)
    freeze.add_argument("--run-freeze-commit", required=True); freeze.add_argument("--envelope-closure-commit", required=True); freeze.add_argument("--matrix", type=Path, required=True)
    freeze.add_argument("--envelope", type=Path, action="append", required=True)
    freeze.add_argument("--private-custodian", type=Path, required=True); freeze.add_argument("--private-custodian-key", type=Path, required=True)
    for name in ("c0a", "c0t", "p1a", "randomness", "private-transition", "private-transition-key", "activation-receipt", "pass-pool-replay-input"):
        freeze.add_argument("--" + name, type=Path, required=True)
    freeze.add_argument("--c0t-commit", required=True)
    freeze.add_argument("--output", type=Path, required=True)
    commit_check = sub.add_parser("verify-commit"); commit_check.add_argument("--artifact", type=Path, required=True); commit_check.add_argument("--commit", required=True)
    check = sub.add_parser("validate"); check.add_argument("--artifact", type=Path, required=True); check.add_argument("--c1a", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "compile-c1a":
            authenticate_canonical_c0(
                args.c0a.resolve(), args.c0t.resolve(), args.c0t_commit,
                args.activation_receipt.resolve(), args.pass_pool_replay_input.resolve(),
            )
            if args.output.resolve() != repo_path(args.c1a_path):
                raise C1Error("C1A output differs from frozen one-path topology")
            value = compile_c1a(args.c0a.read_bytes(), args.c0t.read_bytes(), args.c0t_commit, args.p1a.read_bytes(), args.randomness.read_bytes(), args.private_transition.read_bytes(), args.private_transition_key.read_bytes(), c1a_path=args.c1a_path, c1t_path=args.c1t_path)
            write_new(args.output, value)
        elif args.command == "compile-c1t":
            c1a = strict(args.c1a.read_bytes(), "C1A")
            authenticate_canonical_c0(
                args.c0a.resolve(), args.c0t.resolve(), args.c0t_commit,
                args.activation_receipt.resolve(), args.pass_pool_replay_input.resolve(),
            )
            replayed = compile_c1a(
                args.c0a.read_bytes(), args.c0t.read_bytes(), args.c0t_commit,
                args.p1a.read_bytes(), args.randomness.read_bytes(), args.private_transition.read_bytes(), args.private_transition_key.read_bytes(),
                c1a_path=c1a["publication_topology"]["c1a_path"],
                c1t_path=c1a["publication_topology"]["c1t_path"],
            )
            if replayed != c1a:
                raise C1Error("C1T independent replay differs from committed C1A selection")
            verify_commit_artifact(c1a, args.c1a_commit, args.c1a.resolve(), args.c0t_commit, "C1A")
            if args.output.resolve() != repo_path(c1a["publication_topology"]["c1t_path"]):
                raise C1Error("C1T output differs from frozen one-path topology")
            value = compile_c1t(c1a, args.c1a_commit); write_new(args.output, value)
        elif args.command == "compile-c1-authority":
            c1a = strict(args.c1a.read_bytes(), "C1A"); c1t = strict(args.c1t.read_bytes(), "C1T")
            authenticate_canonical_c0(
                args.c0a.resolve(), args.c0t.resolve(), args.c0t_commit,
                args.activation_receipt.resolve(), args.pass_pool_replay_input.resolve(),
            )
            replayed = compile_c1a(
                args.c0a.read_bytes(), args.c0t.read_bytes(), args.c0t_commit,
                args.p1a.read_bytes(), args.randomness.read_bytes(), args.private_transition.read_bytes(), args.private_transition_key.read_bytes(),
                c1a_path=c1a["publication_topology"]["c1a_path"], c1t_path=c1a["publication_topology"]["c1t_path"],
            )
            if replayed != c1a or args.c0t_commit != c1a["c0t"]["commit"]:
                raise C1Error("C1 authority independent replay differs from C1A")
            verify_commit_artifact(c1a, args.c1a_commit, args.c1a.resolve(), c1a["c0t"]["commit"], "C1A")
            verify_commit_artifact(c1t, args.c1t_commit, args.c1t.resolve(), args.c1a_commit, "C1T")
            authority = derive_authority_projection(strict(args.p1a.read_bytes(), "P1A"))
            write_new(args.output, compile_c1_authority_receipt(c1a, c1t, args.c1t_commit, args.authority_private_key.read_bytes(), authority))
        elif args.command == "compile-envelope-freeze":
            c1a = strict(args.c1a.read_bytes(), "C1A"); c1t = strict(args.c1t.read_bytes(), "C1T"); authority_receipt = strict(args.c1_authority.read_bytes(), "C1 authority")
            private = strict(args.private_custodian.read_bytes(), "private custodian")
            authenticate_canonical_c0(args.c0a.resolve(), args.c0t.resolve(), args.c0t_commit, args.activation_receipt.resolve(), args.pass_pool_replay_input.resolve())
            replayed = compile_c1a(args.c0a.read_bytes(), args.c0t.read_bytes(), args.c0t_commit, args.p1a.read_bytes(), args.randomness.read_bytes(), args.private_transition.read_bytes(), args.private_transition_key.read_bytes(), c1a_path=c1a["publication_topology"]["c1a_path"], c1t_path=c1a["publication_topology"]["c1t_path"])
            if replayed != c1a:
                raise C1Error("envelope freeze independent replay differs from C1A")
            verify_commit_artifact(c1a, args.c1a_commit, args.c1a.resolve(), c1a["c0t"]["commit"], "C1A")
            verify_commit_artifact(c1t, args.c1t_commit, args.c1t.resolve(), c1t["c1a"]["commit"], "C1T")
            authority_projection = derive_authority_projection(strict(args.p1a.read_bytes(), "P1A"))
            value = compile_envelope_freeze(
                c1a, c1t, args.c1t_commit, authority_receipt, args.c1_authority_key.read_bytes(), authority_projection,
                args.run_freeze_commit, args.envelope_closure_commit, args.matrix.resolve(), args.c1_authority.resolve(),
                [path.resolve() for path in args.envelope], private, args.private_custodian_key.read_bytes(), args.private_custodian.resolve(),
            )
            write_new(args.output, value)
        elif args.command == "verify-commit":
            value = strict(args.artifact.read_bytes(), "C1 artifact")
            if value.get("artifact_kind") == "C1A":
                validate_c1a(value); parent = value["c0t"]["commit"]
            elif value.get("artifact_kind") == "C1T":
                changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", value["c1a"]["commit"]).decode().splitlines()
                if len(changed) != 1:
                    raise C1Error("C1A commit does not add exactly one replay source")
                c1a = strict(git("show", f'{value["c1a"]["commit"]}:{changed[0]}'), "committed C1A")
                validate_c1t(value, c1a); parent = value["c1a"]["commit"]
            else:
                raise C1Error("verify-commit accepts only C1A or C1T")
            verify_commit_artifact(value, args.commit, args.artifact.resolve(), parent, value["artifact_kind"])
        else:
            value = strict(args.artifact.read_bytes(), "C1 artifact")
            if value.get("artifact_kind") == "C1A":
                validate_c1a(value)
            elif args.c1a is not None:
                validate_c1t(value, strict(args.c1a.read_bytes(), "C1A"))
            else:
                raise C1Error("C1T validation requires --c1a for exact replay")
    except (OSError, C1Error, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
