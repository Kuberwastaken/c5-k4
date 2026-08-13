#!/usr/bin/env python3
"""Build the deterministic Method v1.5 post-freeze future cohort.

The builder compares two independently authenticated upstream-main receipts.
U1 is the first canonical tip captured after the public v1.5 freeze; U2 is a
later canonical tip.  A cluster can enter the cohort only when it is open at
U2, absent from the open-cluster registry at U1, first appears in the Git
ancestry interval U1..U2, and has no identity trace in the permanent v1.4
exclusion closure or the ancestry reachable from U1.

Only bounded identity and classification metadata are emitted.  In
particular, this program emits no statement text, outcomes, ranks, entropy,
or target-specific semantic annotations.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).parents[1].resolve()
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v14_pool as syntax  # noqa: E402
import build_benchmark_v15_identity_hits as identity_hits  # noqa: E402


SCHEMA_VERSION = "c5k4-future-cohort-registry-1.5"
CHECKPOINT_CHAIN_SCHEMA_VERSION = "c5k4-future-cohort-checkpoint-chain-1.5"
STRATA = (
    "GRAPH_SCALAR_INEQUALITY", "GRAPH_STRUCTURAL_PROPERTY",
    "FINITE_ALGEBRA_EQUATIONAL", "AUTOMATA_GAME_PROCESS", "FINITE_COMBINATORIAL",
)
QUOTAS = {
    "GRAPH_SCALAR_INEQUALITY": 3, "GRAPH_STRUCTURAL_PROPERTY": 3,
    "FINITE_ALGEBRA_EQUATIONAL": 2, "AUTOMATA_GAME_PROCESS": 2,
    "FINITE_COMBINATORIAL": 2,
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SAFE_GIT_CONFIG_ARGS = (
    "-c", "core.hooksPath=/dev/null",
    "-c", "core.fsmonitor=false",
    "-c", "diff.external=",
    "-c", "diff.trustExitCode=false",
    "-c", "filter.lfs.process=",
    "-c", "filter.lfs.smudge=",
    "-c", "filter.lfs.required=false",
)
SAFE_GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/nonexistent-c5k4-v15",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_OPTIONAL_LOCKS": "0",
    "GIT_TERMINAL_PROMPT": "0",
}


class FutureCohortError(ValueError):
    """A fail-closed future-cohort contract violation."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def pretty_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def registry_digest(output: dict[str, Any]) -> str:
    """Digest the explicit unsigned projection (both digest slots omitted)."""
    projection = json.loads(canonical_json(output))
    projection.pop("registry_sha256", None)
    quota = projection.get("quota_certificate")
    if isinstance(quota, dict):
        quota.pop("registry_sha256", None)
    return sha256(canonical_json(projection))


def load_object(path: Path, where: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FutureCohortError(f"cannot read {where}: {exc}") from exc
    if not isinstance(value, dict):
        raise FutureCohortError(f"{where} must be one JSON object")
    return value


def git(repo: Path, *args: str, check: bool = True) -> bytes:
    result = subprocess.run(
        ["/usr/bin/git", *SAFE_GIT_CONFIG_ARGS, "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=SAFE_GIT_ENV,
    )
    if check and result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise FutureCohortError(f"Git command failed ({' '.join(args)}): {detail}")
    if not check and result.returncode != 0:
        return b""
    return result.stdout


def _receipt_identity(receipt: dict[str, Any], label: str) -> dict[str, Any]:
    if all(key in receipt for key in ("repository_path", "commit", "root_tree")):
        return receipt
    if isinstance(receipt.get("upstream"), dict):
        return receipt["upstream"]
    if isinstance(receipt.get("capture"), dict):
        return receipt["capture"]
    raise FutureCohortError(f"{label} has no authenticated repository identity")


def authenticate_receipt(
    receipt: dict[str, Any], label: str, repository: Path | None = None
) -> dict[str, Any]:
    """Authenticate the identity fields of a U1/U2 resolver receipt offline."""

    identity = _receipt_identity(receipt, label)
    repository_text = str(repository) if repository is not None else identity.get("repository_path")
    commit = identity.get("commit")
    tree = identity.get("root_tree")
    if not isinstance(repository_text, str) or not repository_text:
        raise FutureCohortError(f"{label}.repository_path is required")
    if not isinstance(commit, str) or HEX40.fullmatch(commit) is None:
        raise FutureCohortError(f"{label}.commit must be a lowercase SHA-1")
    if not isinstance(tree, str) or HEX40.fullmatch(tree) is None:
        raise FutureCohortError(f"{label}.root_tree must be a lowercase SHA-1")
    repo = Path(repository_text).resolve()
    if not repo.is_dir():
        raise FutureCohortError(f"{label} repository is absent: {repo}")
    actual_commit = git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    actual_tree = git(repo, "rev-parse", "--verify", f"{commit}^{{tree}}").decode().strip()
    if actual_commit != commit or actual_tree != tree:
        raise FutureCohortError(f"{label} commit/tree authentication failed")
    destination_ref = identity.get("destination_ref")
    if destination_ref is not None:
        if not isinstance(destination_ref, str) or not destination_ref.startswith("refs/"):
            raise FutureCohortError(f"{label}.destination_ref is malformed")
        resolved = git(repo, "rev-parse", "--verify", destination_ref).decode().strip()
        if resolved != commit:
            raise FutureCohortError(f"{label} destination ref does not resolve to its commit")
    return {"repo": repo, "commit": commit, "tree": tree}


def validate_policies(grouping: dict[str, Any], classifier: dict[str, Any]) -> None:
    if grouping.get("unit") != "QUESTION_CLUSTER":
        raise FutureCohortError("grouping policy does not define question clusters")
    if grouping.get("manual_grouping_after_p0") is not False:
        raise FutureCohortError("grouping policy permits post-freeze manual grouping")
    if grouping.get("statement_semantics_permitted") is not False:
        raise FutureCohortError("grouping policy permits statement semantics")
    output_policy = classifier.get("output_policy")
    if not isinstance(output_policy, dict):
        raise FutureCohortError("classifier output policy is absent")
    for forbidden in ("statement_text", "random_ranks", "target_selection"):
        if output_policy.get(forbidden) is not False:
            raise FutureCohortError(f"classifier permits forbidden output: {forbidden}")


def validate_provenance_ledgers(ledgers: list[dict[str, Any]]) -> None:
    if not ledgers:
        raise FutureCohortError("at least one complete provenance ledger is required")
    for ledger in ledgers:
        supplied_digest = ledger.get("ledger_sha256")
        if supplied_digest != identity_hits.content_address(ledger, "ledger_sha256"):
            raise FutureCohortError("provenance ledger self-digest is invalid")
        if ledger.get("status") not in {"CLASSIFIED_COMPLETE", "CLASSIFIED_FAIL_CLOSED"}:
            raise FutureCohortError("provenance ledger status is invalid")
        if ledger.get("source_complete") is not True or not isinstance(ledger.get("units"), list):
            raise FutureCohortError("provenance ledger is incomplete")
        counts = Counter(unit.get("provenance_class") for unit in ledger["units"])
        expected = {
            key: counts.get(key, 0) for key in (
                "SEMANTIC_EXPOSURE", "MACHINE_REGISTRY_CONTACT",
                "IMMUTABLE_SOURCE_CUSTODY", "UNKNOWN",
            )
        }
        if ledger.get("counts") != expected:
            raise FutureCohortError("provenance ledger counts do not replay")


def load_content_pack(pack: dict[str, Any]) -> dict[str, bytes]:
    try:
        return identity_hits.load_content_pack(pack)
    except identity_hits.IdentityHitError as exc:
        raise FutureCohortError(str(exc)) from exc


def extract_pool(
    repo: Path, commit: str, tree: str, classifier: dict[str, Any], classifier_path: Path
) -> dict[str, Any]:
    old_commit, old_tree = syntax.PINNED_COMMIT, syntax.PINNED_TREE
    syntax.PINNED_COMMIT, syntax.PINNED_TREE = commit, tree
    try:
        upstream, declarations = syntax.extract(repo, classifier, enforce_pin=True)
    finally:
        syntax.PINNED_COMMIT, syntax.PINNED_TREE = old_commit, old_tree
    inventory = syntax.build_inventory(upstream, declarations, classifier_path)
    return syntax.build_pool(inventory, sha256(canonical_json(inventory)), classifier_path)


def exclusion_index(pool: dict[str, Any]) -> dict[str, set[str]]:
    rows = pool.get("clusters")
    if not isinstance(rows, list):
        raise FutureCohortError("v1.4 exclusion artifact has no clusters array")
    index = {
        "cluster_id": set(), "path": set(), "identity_sha256": set(),
        "module_blob_sha256": set(), "statement_header_sha256": set(),
        "declaration_name": set(),
    }
    for position, row in enumerate(rows):
        if not isinstance(row, dict):
            raise FutureCohortError(f"v1.4 exclusion row {position} is not an object")
        for key in ("cluster_id", "path", "identity_sha256", "module_blob_sha256"):
            value = row.get(key)
            if isinstance(value, str) and value:
                index[key].add(value)
        declarations = row.get("declarations")
        if not isinstance(declarations, list):
            raise FutureCohortError(f"v1.4 exclusion row {position} has invalid declarations")
        for declaration in declarations:
            if not isinstance(declaration, dict):
                raise FutureCohortError("v1.4 exclusion declaration is not an object")
            name = declaration.get("name")
            header = declaration.get("statement_header_sha256")
            if isinstance(name, str) and name:
                index["declaration_name"].add(name)
            if isinstance(header, str) and header:
                index["statement_header_sha256"].add(header)
    return index


def current_cluster_index(pool: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        row["cluster_id"]: row
        for row in pool["clusters"]
        if isinstance(row, dict) and isinstance(row.get("cluster_id"), str)
    }


def reachable(repo: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["/usr/bin/git", *SAFE_GIT_CONFIG_ARGS, "-C", str(repo),
         "merge-base", "--is-ancestor", ancestor, descendant],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=SAFE_GIT_ENV,
    )
    if result.returncode not in (0, 1):
        raise FutureCohortError("cannot evaluate receipt ancestry")
    return result.returncode == 0


def prior_path_history(repo: Path, u1: str, path: str) -> bool:
    return bool(git(repo, "log", "--format=%H", u1, "--", path).strip())


def prior_blob_history(repo: Path, u1: str, u2: str, path: str) -> bool:
    blob = git(repo, "rev-parse", f"{u2}:{path}").decode().strip()
    objects = git(repo, "rev-list", "--objects", u1, "--", "FormalConjectures")
    return any(line.split(b" ", 1)[0].decode() == blob for line in objects.splitlines())


def prior_name_history(repo: Path, u1: str, name: str) -> bool:
    # Pickaxe inspects content changes reachable from U1; it does not use dates.
    return bool(
        git(repo, "log", "--format=%H", "-F", f"-S{name}", u1, "--", "FormalConjectures").strip()
    )


def introduction_commits(repo: Path, u2: str, path: str) -> list[str]:
    raw = git(
        repo, "log", "--follow", "--diff-filter=A", "--format=%H", u2, "--", path
    )
    return [line.decode() for line in raw.splitlines() if line]


def introduction_has_formal_deletion(repo: Path, introduction: str) -> bool:
    """Treat coupled add/delete history as an unresolvable identity ambiguity."""
    parents = git(repo, "show", "-s", "--format=%P", introduction).decode().split()
    if len(parents) != 1:
        return True
    deleted = git(
        repo, "diff", "--name-only", "--diff-filter=D", parents[0], introduction,
        "--", "FormalConjectures",
    ).decode().splitlines()
    return any(path.endswith(".lean") for path in deleted)


def checkpoint_context(
    receipt: dict[str, Any], public_chain_proof: dict[str, Any]
) -> dict[str, Any]:
    ordinal = receipt.get("checkpoint_ordinal")
    if not isinstance(ordinal, int) or ordinal < 1:
        raise FutureCohortError("checkpoint ordinal is invalid")
    scheduled = receipt.get("scheduled_for_utc")
    if not isinstance(scheduled, str) or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T00:17:00Z", scheduled
    ) is None:
        raise FutureCohortError("checkpoint schedule label is invalid")
    label = "checkpoint-" + scheduled[:10]
    basis = receipt.get("basis")
    if not isinstance(basis, dict):
        raise FutureCohortError("checkpoint basis is absent")
    proof_ref = basis.get("public_chain_proof")
    if not isinstance(proof_ref, dict):
        raise FutureCohortError("checkpoint basis has no authenticated public-chain proof")
    claimed_digest = public_chain_proof.get("proof_sha256")
    unsigned = dict(public_chain_proof)
    unsigned.pop("proof_sha256", None)
    if (
        not isinstance(claimed_digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", claimed_digest) is None
        or claimed_digest != sha256(canonical_json(unsigned))
        or proof_ref.get("proof_sha256") != claimed_digest
        or proof_ref.get("public_tip_commit") != public_chain_proof.get("public_tip_commit")
    ):
        raise FutureCohortError("public checkpoint-chain proof binding is invalid")
    checkpoints = public_chain_proof.get("checkpoints")
    next_checkpoint = public_chain_proof.get("next_checkpoint")
    if (
        public_chain_proof.get("terminal") is not False
        or not isinstance(checkpoints, list)
        or public_chain_proof.get("checkpoint_count") != len(checkpoints)
        or len(checkpoints) != ordinal - 1
        or any(row.get("status") != "QUOTA_FAIL" for row in checkpoints if isinstance(row, dict))
        or any(not isinstance(row, dict) for row in checkpoints)
        or not isinstance(next_checkpoint, dict)
        or next_checkpoint.get("ordinal") != ordinal
        or next_checkpoint.get("scheduled_for_utc") != scheduled
    ):
        raise FutureCohortError("public chain does not prove every prior checkpoint failed")
    return {"ordinal": ordinal, "label": label, "prior_sha": claimed_digest}


def permanent_exclusion_reasons(row: dict[str, Any], index: dict[str, set[str]]) -> set[str]:
    reasons = set()
    for key in ("cluster_id", "path", "identity_sha256", "module_blob_sha256"):
        if row.get(key) in index[key]:
            reasons.add("V14_EXCLUSION_" + key.upper())
    for declaration in row.get("declarations", []):
        if declaration.get("name") in index["declaration_name"]:
            reasons.add("V14_EXCLUSION_DECLARATION_NAME")
        if declaration.get("statement_header_sha256") in index["statement_header_sha256"]:
            reasons.add("V14_EXCLUSION_STATEMENT_HEADER")
    return reasons


def identity_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "cluster_id": row["cluster_id"],
        "identity_sha256": row["identity_sha256"],
        "path": row["path"],
        "module_blob_sha256": row["module_blob_sha256"],
        "declarations": [
            {
                "name": declaration["name"],
                "kind": declaration["kind"],
                "category_line": declaration["category_line"],
                "statement_header_sha256": declaration["statement_header_sha256"],
            }
            for declaration in row["declarations"]
        ],
        "machine_stratum": row["machine_stratum"],
        "classification_basis": row["classification_basis"],
    }


def build(
    u1_receipt: dict[str, Any],
    u2_receipt: dict[str, Any],
    v14_pool: dict[str, Any],
    grouping: dict[str, Any],
    classifier: dict[str, Any],
    classifier_path: Path,
    *,
    input_digests: dict[str, str],
    repository: Path | None = None,
    provenance_ledgers: list[dict[str, Any]] | None = None,
    provenance_contents: dict[str, bytes] | None = None,
    public_chain_proof: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_policies(grouping, classifier)
    ledgers = provenance_ledgers or []
    validate_provenance_ledgers(ledgers)
    u1 = authenticate_receipt(u1_receipt, "U1", repository)
    u2 = authenticate_receipt(u2_receipt, "U2", repository)
    if not reachable(u2["repo"], u1["commit"], u2["commit"]):
        raise FutureCohortError("U1 is not an ancestor of U2 in the authenticated U2 repository")

    u1_pool = extract_pool(u2["repo"], u1["commit"], u1["tree"], classifier, classifier_path)
    u2_pool = extract_pool(u2["repo"], u2["commit"], u2["tree"], classifier, classifier_path)
    prior_open = current_cluster_index(u1_pool)
    excluded = exclusion_index(v14_pool)
    records = []
    candidate_rows = [
        row for row in u2_pool["clusters"] if row["cluster_id"] not in prior_open
    ]
    try:
        private_identity_hits = identity_hits.build(
            candidate_rows, ledgers, provenance_contents or {}
        )
    except identity_hits.IdentityHitError as exc:
        raise FutureCohortError(f"private identity join failed closed: {exc}") from exc

    for row in sorted(u2_pool["clusters"], key=lambda item: item["cluster_id"]):
        # An existing U1 cluster remains outside the future cohort even if its
        # statement or metadata changed after the freeze.
        if row["cluster_id"] in prior_open:
            continue
        reasons = permanent_exclusion_reasons(row, excluded)
        reasons.update(identity_hits.exclusion_reasons(row, private_identity_hits))
        if row.get("machine_stratum") is None or row.get("eligible") is not True:
            reasons.add("AMBIGUOUS_OR_UNCLASSIFIED")
        path = row["path"]
        if prior_path_history(u2["repo"], u1["commit"], path):
            reasons.add("PATH_REACHABLE_BEFORE_U1")
        if prior_blob_history(u2["repo"], u1["commit"], u2["commit"], path):
            reasons.add("BLOB_REACHABLE_BEFORE_U1")
        for declaration in row["declarations"]:
            if prior_name_history(u2["repo"], u1["commit"], declaration["name"]):
                reasons.add("DECLARATION_NAME_REACHABLE_BEFORE_U1")

        additions = introduction_commits(u2["repo"], u2["commit"], path)
        if len(additions) != 1:
            reasons.add("AMBIGUOUS_INTRODUCTION_HISTORY")
            introduction = None
        else:
            introduction = additions[0]
            if reachable(u2["repo"], introduction, u1["commit"]):
                reasons.add("INTRODUCTION_REACHABLE_BEFORE_U1")
            if not reachable(u2["repo"], introduction, u2["commit"]):
                reasons.add("INTRODUCTION_NOT_REACHABLE_FROM_U2")
            if introduction_has_formal_deletion(u2["repo"], introduction):
                reasons.add("COINTRODUCED_WITH_FORMAL_DELETION_OR_RENAME")

        record = identity_row(row)
        record.update({
            "first_introduction_commit": introduction,
            "first_introduction_tree": (
                git(u2["repo"], "rev-parse", f"{introduction}^{{tree}}").decode().strip()
                if introduction is not None else None
            ),
            "membership_status": "INCLUDE" if not reasons else "EXCLUDE",
            "exclusion_reasons": sorted(reasons),
        })
        records.append(record)

    reason_counts: Counter[str] = Counter()
    stratum_counts: Counter[str] = Counter()
    for row in records:
        reason_counts.update(row["exclusion_reasons"])
        if row["membership_status"] == "INCLUDE":
            stratum_counts[row["machine_stratum"]] += 1
    output = {
        "schema_version": SCHEMA_VERSION,
        "authority": "SCHEDULED_IDENTITY_ONLY_CHECKPOINT",
        "upstream": {
            "repository": "https://github.com/google-deepmind/formal-conjectures.git",
            "u1_commit": u1["commit"], "u1_tree": u1["tree"],
            "u2_commit": u2["commit"], "u2_tree": u2["tree"],
            "ancestry_interval": f'{u1["commit"]}..{u2["commit"]}',
        },
        "inputs": dict(sorted(input_digests.items())),
        "controls": {
            "statement_text_present": False,
            "outcomes_present": False,
            "ranking_present": False,
            "entropy_used": False,
            "selection_permitted": False,
            "first_introduction_basis": "GIT_ANCESTRY_AND_TREE_CONTENT",
            "v14_exclusion_cluster_count": len(v14_pool["clusters"]),
        },
        "counts": {
            "u1_open_clusters": len(u1_pool["clusters"]),
            "u2_open_clusters": len(u2_pool["clusters"]),
            "delta_records": len(records),
            "included": sum(row["membership_status"] == "INCLUDE" for row in records),
            "excluded": sum(row["membership_status"] == "EXCLUDE" for row in records),
            "eligible_by_stratum": {
                stratum: stratum_counts.get(stratum, 0) for stratum in STRATA
            },
            "exclusion_reasons": dict(sorted(reason_counts.items())),
        },
        "records": records,
    }
    eligible_by_stratum = {
        stratum: stratum_counts.get(stratum, 0) for stratum in STRATA
    }
    deficits = {
        stratum: max(0, QUOTAS[stratum] - eligible_by_stratum[stratum])
        for stratum in STRATA
    }
    if public_chain_proof is None:
        raise FutureCohortError("authenticated public checkpoint-chain proof is required")
    checkpoint = checkpoint_context(u2_receipt, public_chain_proof)
    output["quota_certificate"] = {
        "checkpoint_ordinal": checkpoint["ordinal"],
        "checkpoint_label": checkpoint["label"],
        "commit": u2["commit"], "tree": u2["tree"],
        "quotas": dict(QUOTAS),
        "eligible_by_stratum": eligible_by_stratum,
        "deficits": deficits,
        "status": "PASS" if not any(deficits.values()) else "FAIL",
        "candidate_count": sum(eligible_by_stratum.values()),
        "prior_checkpoint_chain_sha256": checkpoint["prior_sha"],
        "all_prior_valid_checkpoints_failed": True,
        "first_passing_checkpoint": not any(deficits.values()),
    }
    digest = registry_digest(output)
    output["quota_certificate"]["registry_sha256"] = digest
    output["registry_sha256"] = digest
    return output


def checkpoint_chain(
    u1_receipt: dict[str, Any],
    checkpoints: list[dict[str, Any]],
    v14_pool: dict[str, Any],
    grouping: dict[str, Any],
    classifier: dict[str, Any],
    classifier_path: Path,
    *,
    input_digests: dict[str, str],
    provenance_ledgers: list[dict[str, Any]],
    provenance_contents: dict[str, bytes] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Evaluate scheduled checkpoints in order and select the first quota PASS.

    Chronology gaps are terminal and never enter this quota-evaluation helper.
    """

    if not checkpoints:
        raise FutureCohortError("checkpoint manifest must be nonempty")
    certificates = []
    selected = None
    previous_ordinal = 0
    for checkpoint in checkpoints:
        ordinal = checkpoint.get("checkpoint_ordinal")
        label = checkpoint.get("checkpoint_label")
        status = checkpoint.get("capture_status")
        terminal = checkpoint.get("terminal_horizon") is True
        if not isinstance(ordinal, int) or ordinal != previous_ordinal + 1:
            raise FutureCohortError("checkpoint ordinals must be contiguous from one")
        previous_ordinal = ordinal
        if not isinstance(label, str) or not label:
            raise FutureCohortError("checkpoint label is required")
        if status == "MISSED":
            raise FutureCohortError("a missed checkpoint is a terminal chronology failure")
        if status != "CAPTURED" or not isinstance(checkpoint.get("receipt"), dict):
            raise FutureCohortError("captured checkpoint needs one embedded receipt")
        registry = build(
            u1_receipt, checkpoint["receipt"], v14_pool, grouping, classifier,
            classifier_path, input_digests=input_digests,
            provenance_ledgers=provenance_ledgers,
            provenance_contents=provenance_contents,
            public_chain_proof=checkpoint.get("public_chain_proof"),
        )
        quota = registry["quota_certificate"]
        certificate = {
            "checkpoint_ordinal": ordinal, "checkpoint_label": label,
            "capture_status": "CAPTURED", "terminal_horizon": terminal,
            "commit": registry["upstream"]["u2_commit"],
            "tree": registry["upstream"]["u2_tree"],
            "quotas": quota["quotas"],
            "eligible_by_stratum": quota["eligible_by_stratum"],
            "deficits": quota["deficits"], "status": quota["status"],
            "candidate_count": quota["candidate_count"],
            "registry_sha256": registry["registry_sha256"],
        }
        certificates.append(certificate)
        if quota["status"] == "PASS":
            selected = registry
            break
    first = certificates[-1] if selected is not None else None
    chain = {
        "schema_version": CHECKPOINT_CHAIN_SCHEMA_VERSION,
        "authority": "FIRST_SCHEDULED_QUOTA_PASS_OR_HARD_TERMINAL",
        "inputs": dict(sorted(input_digests.items())),
        "controls": {
            "checkpoint_ordering": "CONTIGUOUS_PREREGISTERED_ORDINAL",
            "missed_checkpoint_recreation_permitted": False,
            "manual_close_permitted": False,
            "backfill_permitted": False,
            "statement_text_present": False, "outcomes_present": False,
            "ranking_present": False, "entropy_used": False,
        },
        "checkpoint_certificates": certificates,
        "first_passing_ordinal": (
            first["checkpoint_ordinal"] if selected is not None else None
        ),
        "selected_u2_commit": (
            selected["upstream"]["u2_commit"] if selected is not None else None
        ),
        "selected_u2_tree": (
            selected["upstream"]["u2_tree"] if selected is not None else None
        ),
        "terminal_horizon_reached": any(
            row["terminal_horizon"] for row in certificates
        ) and selected is None,
    }
    chain["chain_sha256"] = sha256(canonical_json(chain))
    return chain, selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--u1-receipt", type=Path, required=True)
    parser.add_argument("--u2-receipt", type=Path, required=True)
    parser.add_argument("--v14-exclusion", type=Path, required=True)
    parser.add_argument("--grouping-rule", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--provenance-ledger", type=Path, action="append", required=True)
    parser.add_argument("--provenance-content-pack", type=Path, required=True)
    parser.add_argument("--public-chain-proof", type=Path, required=True)
    parser.add_argument(
        "--repository", type=Path,
        help="ephemeral authenticated U2 object store containing U1 ancestry",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "u1_receipt": args.u1_receipt.resolve(),
        "u2_receipt": args.u2_receipt.resolve(),
        "v14_exclusion": args.v14_exclusion.resolve(),
        "grouping_rule": args.grouping_rule.resolve(),
        "classifier": args.classifier.resolve(),
        "provenance_content_pack": args.provenance_content_pack.resolve(),
        "public_chain_proof": args.public_chain_proof.resolve(),
    }
    for index, ledger_path in enumerate(args.provenance_ledger):
        paths[f"provenance_ledger_{index}"] = ledger_path.resolve()
    if args.output.exists():
        raise FutureCohortError("output already exists; overwrite is forbidden")
    values = {name: load_object(path, name) for name, path in paths.items()}
    output = build(
        values["u1_receipt"], values["u2_receipt"], values["v14_exclusion"],
        values["grouping_rule"], values["classifier"], paths["classifier"],
        input_digests={name + "_sha256": sha256_file(path) for name, path in paths.items()},
        repository=None if args.repository is None else args.repository.resolve(),
        provenance_ledgers=[
            values[f"provenance_ledger_{index}"]
            for index in range(len(args.provenance_ledger))
        ],
        provenance_contents=load_content_pack(values["provenance_content_pack"]),
        public_chain_proof=values["public_chain_proof"],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(pretty_json(output))
    print(json.dumps({"output": str(args.output), **output["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
