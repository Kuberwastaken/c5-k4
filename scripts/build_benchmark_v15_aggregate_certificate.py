#!/usr/bin/env python3
"""Build and replay Method v1.5's identity-sealed checkpoint certificate.

The private future-cohort registry is an input, never a publication artifact at
a failed checkpoint.  This program publishes only five stratum counts and the
cryptographic bindings needed for a later exact-byte, isolated replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft7Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_benchmark_v15_future_cohort as future_registry  # noqa: E402
import build_benchmark_v15_p1 as p1  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/benchmark-scheduled-aggregate-certificate-v1.5.schema.json"
ATTESTATION_SCHEMA_PATH = ROOT / "schemas/benchmark-scheduled-replay-attestation-v1.5.schema.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas/benchmark-future-registry-output-v1.5.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/benchmark-checkpoint-component-manifest-v1.5.schema.json"
SCHEMA = "c5k4-method-v1.5-scheduled-aggregate-certificate-1.0"
UPSTREAM_REPOSITORY = "https://github.com/google-deepmind/formal-conjectures.git"
UPSTREAM_REF = "refs/heads/main"
LAST_CHECKPOINT = "2027-08-15T00:17:00Z"
STRATA = (
    "GRAPH_SCALAR_INEQUALITY",
    "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL",
    "AUTOMATA_GAME_PROCESS",
    "FINITE_COMBINATORIAL",
)
QUOTAS = dict(zip(STRATA, (3, 3, 2, 2, 2)))
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OID_RE = re.compile(r"^[0-9a-f]{40}$")


class CertificateError(ValueError):
    """A sealed-publication or deterministic-replay invariant failed."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CertificateError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise CertificateError(f"{label} must be a JSON object")
    return value


def relative_ref(path: Path, label: str) -> dict[str, str]:
    try:
        relative = path.resolve(strict=True).relative_to(ROOT).as_posix()
    except (OSError, ValueError) as exc:
        raise CertificateError(f"{label} must be an existing file inside the repository") from exc
    pure = PurePosixPath(relative)
    if not pure.parts or ".." in pure.parts or pure.is_absolute():
        raise CertificateError(f"{label} has a non-normalized path")
    return {"path": relative, "sha256": sha256_file(path.resolve())}


def exact_oid(value: Any, label: str) -> str:
    if not isinstance(value, str) or OID_RE.fullmatch(value) is None:
        raise CertificateError(f"{label} must be an exact lowercase SHA-1 object ID")
    return value


def validate_schema(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = load_json(schema_path, f"{label} schema")
    try:
        Draft7Validator(schema, format_checker=FormatChecker()).validate(value)
    except Exception as exc:
        raise CertificateError(f"{label} fails its strict JSON schema: {exc}") from exc


def authenticate_p1(
    p1a_path: Path, p1t_path: Path, p1t_commit: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return the only component closure an aggregate certificate may trust."""
    p1a_value = load_json(p1a_path, "P1A")
    p1t_value = load_json(p1t_path, "P1T")
    try:
        p1.validate_p1a(p1a_value)
        p1.validate_p1t(p1t_value, p1t_commit=p1t_commit, artifact_path=p1t_path)
    except p1.P1Error as exc:
        raise CertificateError(f"P1A/P1T authentication failed: {exc}") from exc
    if p1t_value["p1a"]["path"] != relative_ref(p1a_path, "P1A")["path"]:
        raise CertificateError("P1T authenticates a different P1A path")
    if p1t_value["p1a"]["sha256"] != sha256_file(p1a_path):
        raise CertificateError("P1T authenticates different P1A bytes")
    binding = {
        "p1a": relative_ref(p1a_path, "P1A"),
        "p1t": relative_ref(p1t_path, "P1T"),
        "p1a_commit": p1t_value["p1a_commit"],
        "p1t_commit": p1t_commit,
    }
    return p1a_value, p1t_value, binding


def _resolve_selector(selector: Any, p1a_value: dict[str, Any], label: str) -> dict[str, str]:
    if not isinstance(selector, dict) or set(selector) != {"closure", "role"}:
        raise CertificateError(f"{label} is not an exact P1 role selector")
    closure, role = selector.get("closure"), selector.get("role")
    if closure == "NATIVE_V1_5":
        source = p1a_value.get("components", {})
    elif closure == "INHERITED_V1_4":
        source = p1a_value.get("inherited_v1_4", {}).get("components", {})
    else:
        raise CertificateError(f"{label} selects an unknown P1 closure")
    row = source.get(role) if isinstance(source, dict) else None
    if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not isinstance(row.get("sha256"), str):
        raise CertificateError(f"{label} selects absent P1 role {role!r}")
    return {"path": row["path"], "sha256": row["sha256"]}


def load_components(
    manifest_path: Path, p1a_value: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(manifest_path, "checkpoint component manifest")
    validate_schema(manifest, MANIFEST_SCHEMA_PATH, "checkpoint component manifest")
    frozen_manifest = p1a_value.get("components", {}).get("checkpoint_component_manifest")
    frozen_schema = p1a_value.get("components", {}).get("checkpoint_component_manifest_schema")
    if (
        not isinstance(frozen_manifest, dict)
        or {"path": frozen_manifest.get("path"), "sha256": frozen_manifest.get("sha256")}
        != relative_ref(manifest_path, "checkpoint component manifest")
        or not isinstance(frozen_schema, dict)
        or {"path": frozen_schema.get("path"), "sha256": frozen_schema.get("sha256")}
        != relative_ref(MANIFEST_SCHEMA_PATH, "checkpoint component manifest schema")
    ):
        raise CertificateError("component manifest/schema are not the exact P1-native bindings")

    def resolve_tree(value: Any, trail: tuple[str, ...] = ()) -> Any:
        if isinstance(value, dict) and set(value) == {"closure", "role"}:
            return _resolve_selector(value, p1a_value, ".".join(trail))
        if isinstance(value, dict):
            return {key: resolve_tree(child, (*trail, key)) for key, child in value.items()}
        return value

    return resolve_tree(manifest["components"]), resolve_tree(manifest["runtime_inputs"])


def bind_runtime_inputs(
    internal: dict[str, Any], ledger_paths: list[Path], content_pack_path: Path,
    runtime_contract: dict[str, Any],
) -> dict[str, Any]:
    if not ledger_paths:
        raise CertificateError("at least one actual provenance ledger must be sealed")
    ledger_schema_ref = runtime_contract["provenance_ledgers"]["item_schema"]
    content_schema_ref = runtime_contract["provenance_content_pack"]["schema"]
    ledger_schema_path = ROOT / ledger_schema_ref["path"]
    content_schema_path = ROOT / content_schema_ref["path"]
    ledgers = []
    inputs = internal.get("inputs", {})
    for index, path in enumerate(ledger_paths):
        value = load_json(path, f"provenance ledger {index}")
        validate_schema(value, ledger_schema_path, f"provenance ledger {index}")
        file_sha = sha256_file(path)
        if value.get("ledger_sha256") != future_registry.identity_hits.content_address(value, "ledger_sha256"):
            raise CertificateError(f"provenance ledger {index} self-digest is invalid")
        if inputs.get(f"provenance_ledger_{index}_sha256") != file_sha:
            raise CertificateError(f"private registry does not bind provenance ledger {index} bytes")
        ledgers.append({"position": index, "file_sha256": file_sha, "ledger_sha256": value["ledger_sha256"]})
    unexpected = sorted(
        key for key in inputs
        if re.fullmatch(r"provenance_ledger_[0-9]+_sha256", key)
        and int(key.removeprefix("provenance_ledger_").removesuffix("_sha256")) >= len(ledger_paths)
    )
    if unexpected:
        raise CertificateError("private registry binds additional unsealed provenance ledgers")
    content_pack = load_json(content_pack_path, "provenance content pack")
    validate_schema(content_pack, content_schema_path, "provenance content pack")
    content_sha = sha256_file(content_pack_path)
    if inputs.get("provenance_content_pack_sha256") != content_sha:
        raise CertificateError("private registry does not bind provenance content-pack bytes")
    return {
        "provenance_ledgers": ledgers,
        "provenance_content_pack_sha256": content_sha,
    }


def chronology_identity(receipt: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if receipt.get("artifact_kind") != "CHECKPOINT_CAPTURE" or receipt.get("protocol_version") != "1.5":
        raise CertificateError("aggregate certificate requires the scheduled CHECKPOINT_CAPTURE chronology receipt")
    if receipt.get("status") != "AWAITING_MACHINE_QUOTA_CERTIFICATE":
        raise CertificateError("chronology capture is not awaiting its machine quota certificate")
    trigger = receipt.get("trigger")
    if trigger != {"event_name": "schedule", "run_attempt": 1}:
        raise CertificateError("manual dispatches and reruns cannot produce an aggregate certificate")
    upstream = receipt.get("upstream")
    if not isinstance(upstream, dict):
        raise CertificateError("chronology capture has no upstream identity")
    if upstream.get("repository") != UPSTREAM_REPOSITORY or upstream.get("ref") != UPSTREAM_REF:
        raise CertificateError("chronology capture is not canonical upstream main")
    for key in ("commit", "root_tree", "formal_conjectures_tree"):
        exact_oid(upstream.get(key), f"chronology upstream {key}")
    return upstream, trigger


def checkpoint_chain_digest(receipt: dict[str, Any], internal: dict[str, Any]) -> str:
    quota = internal.get("quota_certificate", {})
    digest = quota.get("prior_checkpoint_chain_sha256")
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        raise CertificateError("private registry has no exact prior checkpoint-chain digest")
    proof = receipt.get("basis", {}).get("public_chain_proof")
    if not isinstance(proof, dict) or proof.get("proof_sha256") != digest:
        raise CertificateError("private registry is not bound to the authenticated public-chain proof")
    return digest


def derive_aggregates(internal: dict[str, Any]) -> dict[str, Any]:
    records = internal.get("records")
    if not isinstance(records, list):
        raise CertificateError("private registry records are missing")
    counts = {stratum: 0 for stratum in STRATA}
    for record in records:
        if not isinstance(record, dict):
            raise CertificateError("private registry record is malformed")
        if record.get("membership_status") == "INCLUDE":
            stratum = record.get("machine_stratum")
            if stratum not in counts:
                raise CertificateError("included record has a non-frozen stratum")
            counts[stratum] += 1
    deficits = {key: max(0, QUOTAS[key] - counts[key]) for key in STRATA}
    status = "PASS" if not any(deficits.values()) else "FAIL"
    aggregates = {
        "eligible_by_stratum": counts,
        "quotas": dict(QUOTAS),
        "deficits": deficits,
        "candidate_count": sum(counts.values()),
        "status": status,
    }
    quota = internal.get("quota_certificate")
    expected = {
        "eligible_by_stratum": counts,
        "quotas": dict(QUOTAS),
        "deficits": deficits,
        "candidate_count": sum(counts.values()),
        "status": status,
    }
    if not isinstance(quota, dict) or any(quota.get(key) != value for key, value in expected.items()):
        raise CertificateError("private registry quota fields differ from record-derived aggregates")
    return aggregates


def _registry_identity(internal: dict[str, Any]) -> tuple[str, str]:
    upstream = internal.get("upstream", {})
    if upstream.get("repository") != UPSTREAM_REPOSITORY:
        raise CertificateError("private registry does not bind canonical upstream")
    return exact_oid(upstream.get("u2_commit"), "registry U2 commit"), exact_oid(upstream.get("u2_tree"), "registry U2 tree")


def unsigned_digest(certificate: dict[str, Any]) -> str:
    unsigned = dict(certificate)
    unsigned.pop("certificate_sha256", None)
    return sha256_bytes(canonical_json(unsigned))


def attestation_digest(attestation: dict[str, Any]) -> str:
    unsigned = dict(attestation)
    unsigned.pop("attestation_sha256", None)
    return sha256_bytes(canonical_json(unsigned))


def build_certificate(
    chronology_path: Path, registry_path: Path, manifest_path: Path,
    p1a_path: Path, p1t_path: Path, p1t_commit: str,
    provenance_ledger_paths: list[Path], provenance_content_pack_path: Path,
) -> dict[str, Any]:
    p1a_value, _p1t_value, p1_binding = authenticate_p1(p1a_path, p1t_path, p1t_commit)
    frozen_components, runtime_contract = load_components(manifest_path, p1a_value)
    chronology = load_json(chronology_path, "chronology receipt")
    internal = load_json(registry_path, "private registry")
    validate_schema(internal, REGISTRY_SCHEMA_PATH, "private registry")
    expected_registry_digest = future_registry.registry_digest(internal)
    if (
        internal.get("registry_sha256") != expected_registry_digest
        or internal.get("quota_certificate", {}).get("registry_sha256")
        != expected_registry_digest
    ):
        raise CertificateError("private registry unsigned projection digest is invalid")
    upstream, trigger = chronology_identity(chronology)
    registry_commit, registry_tree = _registry_identity(internal)
    if registry_commit != upstream["commit"] or registry_tree != upstream["root_tree"]:
        raise CertificateError("private registry tip/tree differs from chronology receipt")
    quota = internal["quota_certificate"]
    if quota.get("checkpoint_ordinal") != chronology.get("checkpoint_ordinal"):
        raise CertificateError("private registry checkpoint ordinal differs from chronology")
    scheduled = chronology.get("scheduled_for_utc")
    expected_label = f"checkpoint-{scheduled[:10]}" if isinstance(scheduled, str) else None
    if quota.get("checkpoint_label") != expected_label:
        raise CertificateError("private registry checkpoint label differs from chronology")
    if quota.get("commit") != registry_commit or quota.get("tree") != registry_tree:
        raise CertificateError("private registry quota certificate tip/tree is inconsistent")
    aggregates = derive_aggregates(internal)
    runtime_inputs = bind_runtime_inputs(
        internal, provenance_ledger_paths, provenance_content_pack_path, runtime_contract,
    )
    if quota.get("first_passing_checkpoint") is not (aggregates["status"] == "PASS"):
        raise CertificateError("private registry first-pass flag differs from replayed status")
    certificate = {
        "schema": SCHEMA,
        "artifact_kind": "SCHEDULED_AGGREGATE_CERTIFICATE",
        "protocol_version": "1.5",
        "publication_boundary": {
            "identities_present": False,
            "statements_present": False,
            "outcomes_present": False,
            "ranking_present": False,
            "entropy_present": False,
            "failed_checkpoint_publication": "CERTIFICATE_AND_CHRONOLOGY_RECEIPT_ONLY",
        },
        "checkpoint": {
            "ordinal": chronology["checkpoint_ordinal"],
            "scheduled_for_utc": scheduled,
            "trigger": trigger["event_name"],
            "run_attempt": trigger["run_attempt"],
            "terminal_horizon": scheduled == LAST_CHECKPOINT,
        },
        "upstream": {
            "repository": UPSTREAM_REPOSITORY,
            "ref": UPSTREAM_REF,
            "commit": upstream["commit"],
            "root_tree": upstream["root_tree"],
            "formal_conjectures_tree": upstream["formal_conjectures_tree"],
        },
        "chronology": {
            "receipt": relative_ref(chronology_path, "chronology receipt"),
            "prior_checkpoint_chain_sha256": checkpoint_chain_digest(chronology, internal),
            "all_prior_valid_checkpoints_failed": quota.get("all_prior_valid_checkpoints_failed"),
        },
        "p1_binding": p1_binding,
        "component_manifest": relative_ref(manifest_path, "checkpoint component manifest"),
        "frozen_components": frozen_components,
        "aggregates": aggregates,
        "sealed_replay": {
            "private_registry_sha256": sha256_file(registry_path),
            "private_registry_schema_sha256": sha256_file(REGISTRY_SCHEMA_PATH),
            "runtime_inputs": runtime_inputs,
            "aggregate_extractor": relative_ref(Path(__file__), "aggregate extractor"),
            "deterministic_exact_byte_replay_required": True,
            "fresh_isolated_reacquisition_required": True,
            "exact_commit_and_trees_required": True,
            "generic_generated_artifact_verifier_authoritative": False,
            "pass_pool_publication": "SEPARATE_PRE_ENTROPY_ARTIFACT",
        },
    }
    certificate["certificate_sha256"] = unsigned_digest(certificate)
    validate_certificate(certificate)
    return certificate


def validate_certificate(certificate: dict[str, Any]) -> None:
    validate_schema(certificate, SCHEMA_PATH, "aggregate certificate")
    if certificate["certificate_sha256"] != unsigned_digest(certificate):
        raise CertificateError("aggregate certificate self-digest is invalid")
    counts = certificate["aggregates"]["eligible_by_stratum"]
    deficits = {key: max(0, QUOTAS[key] - counts[key]) for key in STRATA}
    expected_status = "PASS" if not any(deficits.values()) else "FAIL"
    if certificate["aggregates"]["deficits"] != deficits:
        raise CertificateError("published deficits do not replay from aggregate counts")
    if certificate["aggregates"]["candidate_count"] != sum(counts.values()):
        raise CertificateError("published candidate count does not replay")
    if certificate["aggregates"]["status"] != expected_status:
        raise CertificateError("published status does not replay")


def _git(repository: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "credential.helper=",
             "-C", str(repository), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        raise CertificateError(f"isolated replay repository check failed: {exc.stderr.decode('utf-8', 'replace').strip()}") from exc
    return result.stdout.decode("utf-8", "strict").strip()


def validate_bound_ref(ref: dict[str, str], label: str) -> None:
    path = ROOT / ref["path"]
    if not path.is_file() or sha256_file(path) != ref["sha256"]:
        raise CertificateError(f"{label} bytes differ from the frozen certificate binding")


def replay_certificate(
    certificate: dict[str, Any], chronology_path: Path, private_registry_path: Path,
    repository: Path, provenance_ledger_paths: list[Path], provenance_content_pack_path: Path,
) -> dict[str, Any]:
    """Validate an independently re-executed private registry, not a cached artifact claim.

    The caller must reacquire the canonical repository into a fresh isolated
    object store and run the bound registry invocation.  This validator then
    requires its private output to be byte-identical to the sealed output; a
    generic generated-artifact verifier is deliberately not accepted as proof.
    """
    validate_certificate(certificate)
    p1_binding = certificate["p1_binding"]
    p1a_value, _p1t_value, replayed_p1_binding = authenticate_p1(
        ROOT / p1_binding["p1a"]["path"], ROOT / p1_binding["p1t"]["path"],
        p1_binding["p1t_commit"],
    )
    if replayed_p1_binding != p1_binding:
        raise CertificateError("replayed P1 binding differs from aggregate certificate")
    frozen_components, runtime_contract = load_components(
        ROOT / certificate["component_manifest"]["path"], p1a_value,
    )
    if frozen_components != certificate["frozen_components"]:
        raise CertificateError("P1-resolved components differ from aggregate certificate")
    validate_bound_ref(certificate["chronology"]["receipt"], "chronology receipt")
    if chronology_path.resolve() != (ROOT / certificate["chronology"]["receipt"]["path"]).resolve():
        raise CertificateError("replay chronology path differs from the sealed receipt path")
    for component, bindings in certificate["frozen_components"].items():
        for role, ref in bindings.items():
            validate_bound_ref(ref, f"{component}.{role}")
    validate_bound_ref(certificate["sealed_replay"]["aggregate_extractor"], "aggregate extractor")
    if sha256_file(REGISTRY_SCHEMA_PATH) != certificate["sealed_replay"]["private_registry_schema_sha256"]:
        raise CertificateError("private registry schema differs from the frozen binding")
    upstream = certificate["upstream"]
    if _git(repository, "rev-parse", "--verify", f'{upstream["commit"]}^{{commit}}') != upstream["commit"]:
        raise CertificateError("isolated repository does not contain exact checkpoint commit")
    if _git(repository, "rev-parse", f'{upstream["commit"]}^{{tree}}') != upstream["root_tree"]:
        raise CertificateError("isolated repository root tree differs")
    if _git(repository, "rev-parse", f'{upstream["commit"]}:FormalConjectures') != upstream["formal_conjectures_tree"]:
        raise CertificateError("isolated repository FormalConjectures tree differs")
    if sha256_file(private_registry_path) != certificate["sealed_replay"]["private_registry_sha256"]:
        raise CertificateError("re-executed private registry is not exact-byte deterministic")
    internal = load_json(private_registry_path, "re-executed private registry")
    validate_schema(internal, REGISTRY_SCHEMA_PATH, "re-executed private registry")
    if internal.get("registry_sha256") != future_registry.registry_digest(internal):
        raise CertificateError("replayed registry unsigned projection digest is invalid")
    if derive_aggregates(internal) != certificate["aggregates"]:
        raise CertificateError("re-executed private registry aggregates differ from certificate")
    runtime_inputs = bind_runtime_inputs(
        internal, provenance_ledger_paths, provenance_content_pack_path, runtime_contract,
    )
    if runtime_inputs != certificate["sealed_replay"]["runtime_inputs"]:
        raise CertificateError("replayed runtime inputs differ from sealed ledger/content-pack set")
    attestation = {
        "schema": "c5k4-method-v1.5-scheduled-replay-attestation-1.0",
        "status": "INDEPENDENT_EXACT_REPLAY_PASS",
        "certificate_sha256": certificate["certificate_sha256"],
        "chronology_receipt_sha256": sha256_file(chronology_path),
        "private_registry_sha256": sha256_file(private_registry_path),
        "registry_unsigned_projection_sha256": internal["registry_sha256"],
        "upstream": {
            "commit": upstream["commit"], "root_tree": upstream["root_tree"],
            "formal_conjectures_tree": upstream["formal_conjectures_tree"],
        },
        "verifier": relative_ref(Path(__file__), "replay verifier"),
    }
    attestation["attestation_sha256"] = attestation_digest(attestation)
    validate_schema(attestation, ATTESTATION_SCHEMA_PATH, "replay attestation")
    return attestation


def write_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise CertificateError("certificate output already exists; overwrite is forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--chronology-receipt", type=Path, required=True)
    build.add_argument("--private-registry", type=Path, required=True)
    build.add_argument("--component-manifest", type=Path, required=True)
    build.add_argument("--p1a", type=Path, required=True)
    build.add_argument("--p1t", type=Path, required=True)
    build.add_argument("--p1t-commit", required=True)
    build.add_argument("--provenance-ledger", type=Path, action="append", required=True)
    build.add_argument("--provenance-content-pack", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("validate")
    check.add_argument("--certificate", type=Path, required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--certificate", type=Path, required=True)
    replay.add_argument("--chronology-receipt", type=Path, required=True)
    replay.add_argument("--private-registry", type=Path, required=True)
    replay.add_argument("--isolated-repository", type=Path, required=True)
    replay.add_argument("--provenance-ledger", type=Path, action="append", required=True)
    replay.add_argument("--provenance-content-pack", type=Path, required=True)
    replay.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            value = build_certificate(
                args.chronology_receipt.resolve(), args.private_registry.resolve(),
                args.component_manifest.resolve(),
                args.p1a.resolve(), args.p1t.resolve(), args.p1t_commit,
                [path.resolve() for path in args.provenance_ledger],
                args.provenance_content_pack.resolve(),
            )
            write_json(args.output.resolve(), value)
        elif args.command == "validate":
            validate_certificate(load_json(args.certificate.resolve(), "aggregate certificate"))
        else:
            attestation = replay_certificate(
                load_json(args.certificate.resolve(), "aggregate certificate"),
                args.chronology_receipt.resolve(), args.private_registry.resolve(),
                args.isolated_repository.resolve(),
                [path.resolve() for path in args.provenance_ledger],
                args.provenance_content_pack.resolve(),
            )
            write_json(args.output.resolve(), attestation)
    except (CertificateError, OSError) as exc:
        print(f"INVALID_AGGREGATE_CERTIFICATE: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
