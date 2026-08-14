#!/usr/bin/env python3
"""Offline structural validator for the Method v1.5 checkpoint workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1].resolve()
WORKFLOW = ROOT / ".github/workflows/method-v15-checkpoint.yml"
CONTRACT = ROOT / "results/benchmark/v1.5-protocol/checkpoint-invocation-contract.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(workflow: Path, contract_path: Path, *, runtime: bool = False) -> None:
    text = workflow.read_text(encoding="utf-8")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("schema") != "c5k4-method-v1.5-checkpoint-invocation-contract-1.0":
        raise ValueError("unexpected invocation-contract schema")

    header = text.split("permissions:", 1)[0]
    if not re.search(r"(?m)^on:\n  schedule:\n    - cron: '17 0 \* \* \*'\n$", header):
        raise ValueError("workflow must have exactly the frozen schedule trigger")
    for forbidden in ("workflow_dispatch:", "push:", "pull_request:", "workflow_call:"):
        if forbidden in header:
            raise ValueError(f"forbidden workflow trigger: {forbidden}")
    if "group: method-v15-checkpoint-publication" not in text or "cancel-in-progress: false" not in text:
        raise ValueError("checkpoint publication is not serialized without cancellation")
    if "contents: write" not in text or "id-token: write" not in text:
        raise ValueError("scheduler lacks bounded publication or signed-request permission")
    runtime_gate = text.find("--runtime >/dev/null 2>&1")
    if runtime_gate < 0 or runtime_gate > text.find("git fetch --no-tags origin"):
        raise ValueError("pre-P1 silent fail-closed gate does not precede publication-chain access")
    for required in (
        "github.event_name", "github.run_attempt", "sha256sum .github/workflows/method-v15-checkpoint.yml",
        "git checkout --detach \"$frozen_commit\"", "git push --atomic origin \"HEAD:refs/heads/",
        "verify_benchmark_v15_public_checkpoint_chain.py",
        "TERMINAL_CHRONOLOGY_GAP", "c5k4-method-v1.5-target-blind-checkpoint-request-1.0",
        "ACTIONS_ID_TOKEN_REQUEST_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_URL",
        "X-C5K4-Request-SHA256", "--pinnedpubkey \"$harness_pin\"",
        "--max-filesize \"$max_response_bytes\"", "--max-time \"$max_response_seconds\"",
        "controlled harness response is not the exact bounded triplet",
        "jq -er '.next_checkpoint.scheduled_for_utc'",
        "test \"$(git rev-parse HEAD)\" = \"$CHAIN_TIP\"",
        "test ! -e \"$checkpoint_tree/$destination\"",
    ):
        if required not in text:
            raise ValueError(f"workflow is missing required frozen behavior: {required}")
    for forbidden in ("--force", "workflow_dispatch", "repository_dispatch", "pull_request_target"):
        if forbidden in text:
            raise ValueError(f"workflow contains forbidden behavior: {forbidden}")

    trigger = contract.get("trigger", {})
    if trigger != {
        "event": "schedule", "cron": "17 0 * * *", "run_attempt": 1,
        "manual_dispatch_permitted": False, "push_trigger_permitted": False,
        "reusable_trigger_permitted": False,
    }:
        raise ValueError("contract trigger differs from the frozen schedule-only rule")
    stopping = contract.get("stopping", {})
    if stopping.get("first_quota_pass_is_terminal") is not True:
        raise ValueError("first quota PASS is not terminal")
    if stopping.get("last_scheduled_checkpoint_utc") != "2027-08-15T00:17:00Z":
        raise ValueError("hard horizon differs from chronology rule")
    if stopping.get("missed_tick_catchup_permitted") is not False or stopping.get("expired_gap_terminal_status") != "INVALID_CHRONOLOGY_CAPTURE":
        raise ValueError("expired checkpoint gap is not terminal and fail-closed")
    publication = contract.get("publication", {})
    if publication.get("files") != ["publication-manifest.json", "quota-certificate.json", "receipt.json"]:
        raise ValueError("publication allowlist is not exact")
    if publication.get("logs_permitted") is not False or publication.get("overwrite_permitted") is not False:
        raise ValueError("publication permits logs or overwrite")
    if publication.get("pass_full_pool_publication") != "SEPARATE_PRE_ENTROPY_PHASE_ONLY":
        raise ValueError("PASS pool is not deferred to a separate pre-entropy phase")
    inputs = contract.get("inputs", {})
    if inputs.get("previous_receipt_rule") != "DERIVED_ONLY_BY_GIT_AUTHENTICATED_PUBLIC_CHAIN_PROOF":
        raise ValueError("previous receipt is not derived from authenticated Git ancestry")
    if inputs.get("publication_genesis") != "SOLE_PARENT_P1T_ADD_ONLY_U1_RECEIPT":
        raise ValueError("publication genesis is not anchored directly to P1T")
    if publication.get("server_update_rule") != "ATOMIC_NORMAL_FAST_FORWARD_PUSH_FROM_VERIFIED_PUBLIC_TIP":
        raise ValueError("publication does not require an atomic normal fast-forward push")
    runner = contract.get("runner", {})
    if runner.get("path") != "scripts/run_benchmark_v15_checkpoint.py":
        raise ValueError("runner path contract is not exact")
    if runner.get("execution_location") != "DEDICATED_CONTROLLED_HARNESS_ONLY" or runner.get("github_hosted_execution_permitted") is not False:
        raise ValueError("checkpoint runner is not confined to the controlled harness")
    if runner.get("github_hosted_private_input_permitted") is not False:
        raise ValueError("GitHub-hosted execution permits private target-bearing input")
    harness = contract.get("controlled_harness", {})
    if harness.get("authentication") != "GITHUB_ACTIONS_OIDC_TOKEN":
        raise ValueError("controlled harness request is not GitHub-signed")
    if harness.get("request_signature_binding") != "OIDC_AUDIENCE_SUFFIX_IS_SHA256_OF_CANONICAL_REQUEST_BYTES":
        raise ValueError("signed request is not bound to canonical request bytes")
    if harness.get("target_identities_permitted_in_request") is not False or harness.get("statement_text_permitted_in_request") is not False:
        raise ValueError("controlled-harness request is not target-blind")
    if harness.get("response_shape") != "EXACT_THREE_FILE_JSON_OBJECT" or harness.get("response_files") != publication.get("files"):
        raise ValueError("controlled harness response is not the exact publication triplet")
    if harness.get("response_manifest_must_bind_request_sha256") is not True or harness.get("response_logs_permitted") is not False:
        raise ValueError("controlled harness response is not request-bound and log-free")
    if harness.get("max_response_bytes") != 1048576 or harness.get("max_response_seconds") != 300:
        raise ValueError("controlled harness response is not bounded")
    if harness.get("request_fields") != [
        "schema", "protocol_version", "scheduled_for_utc", "mode",
        "public_chain_proof_sha256", "public_tip_commit", "p1t_commit",
        "workflow_run_id", "run_attempt",
    ]:
        raise ValueError("target-blind request shape is not exact")
    forbidden_workflow_terms = ("--private-input", "private_input", "runner_temp_relative_path")
    if any(term in text for term in forbidden_workflow_terms):
        raise ValueError("GitHub-hosted workflow handles target-bearing private input")
    if 'python3 "$RUNNER_PATH"' in text or 'python "$RUNNER_PATH"' in text:
        raise ValueError("GitHub-hosted workflow executes the controlled-harness runner")
    request_literal = text.split("          request = {", 1)
    if len(request_literal) != 2:
        raise ValueError("target-blind request literal is absent")
    request_literal = request_literal[1].split("          }", 1)[0]
    if any(term in request_literal for term in ("cluster_id", "declarations", "records", "statement_text", "target_identity")):
        raise ValueError("signed scheduler request contains target-bearing data")
    certificate = contract.get("aggregate_certificate", {})
    if certificate.get("identity_rows_permitted") is not False or certificate.get("statement_text_permitted") is not False:
        raise ValueError("aggregate certificate permits target-bearing content")
    required_bindings = {
        "upstream_commit", "upstream_root_tree", "upstream_formal_conjectures_tree",
        "runner_sha256", "workflow_sha256", "invocation_contract_sha256",
        "chronology_rule_sha256", "future_cohort_rule_sha256", "input_schema_sha256",
        "output_schema_sha256", "grouping_rule_sha256", "classifier_sha256",
        "source_ledger_sha256", "counts_by_stratum", "quota_by_stratum",
        "deficits_by_stratum", "status", "registry_sha256",
        "deterministic_replay_contract_sha256",
    }
    if set(certificate.get("must_bind", [])) != required_bindings:
        raise ValueError("aggregate certificate binding set is incomplete or unbounded")

    expected = contract.get("frozen", {}).get("workflow_sha256")
    runner_sha = contract.get("runner", {}).get("sha256")
    active = contract.get("status") == "FROZEN_P1_EXECUTABLE"
    if active:
        if not isinstance(expected, str) or HEX64.fullmatch(expected) is None or digest(workflow) != expected:
            raise ValueError("active contract does not bind the exact workflow bytes")
        if not isinstance(runner_sha, str) or HEX64.fullmatch(runner_sha) is None:
            raise ValueError("active contract does not bind the checkpoint runner")
        for key in ("https_endpoint", "tls_spki_sha256", "oidc_audience_prefix"):
            if not isinstance(harness.get(key), str) or not harness[key]:
                raise ValueError("active contract does not bind the controlled harness")
        if not harness["https_endpoint"].startswith("https://") or not harness["tls_spki_sha256"].startswith("sha256//"):
            raise ValueError("active controlled harness transport is not HTTPS and SPKI-pinned")
    elif runtime:
        raise ValueError("pre-P1 checkpoint scaffold is intentionally non-executable")


class WorkflowContractMutationTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        workflow = root / "workflow.yml"
        contract = root / "contract.json"
        workflow.write_bytes(WORKFLOW.read_bytes())
        contract.write_bytes(CONTRACT.read_bytes())
        return temporary, workflow, contract

    def test_scaffold_validates_offline_but_not_at_runtime(self) -> None:
        validate(WORKFLOW, CONTRACT)
        with self.assertRaisesRegex(ValueError, "intentionally non-executable"):
            validate(WORKFLOW, CONTRACT, runtime=True)

    def test_manual_trigger_is_rejected(self) -> None:
        temporary, workflow, contract = self.fixture()
        with temporary:
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "  schedule:\n", "  workflow_dispatch:\n  schedule:\n", 1
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "frozen schedule trigger|forbidden workflow trigger"):
                validate(workflow, contract)

    def test_cancellation_is_rejected(self) -> None:
        temporary, workflow, contract = self.fixture()
        with temporary:
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "cancel-in-progress: false", "cancel-in-progress: true", 1
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "not serialized"):
                validate(workflow, contract)

    def test_pre_p1_gate_must_remain_silent_and_first(self) -> None:
        temporary, workflow, contract = self.fixture()
        with temporary:
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "--runtime >/dev/null 2>&1", "--runtime", 1
                ), encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "silent fail-closed gate"):
                validate(workflow, contract)

    def test_active_contract_requires_exact_workflow_hash(self) -> None:
        temporary, workflow, contract_path = self.fixture()
        with temporary:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["status"] = "FROZEN_P1_EXECUTABLE"
            contract["frozen"]["workflow_sha256"] = "0" * 64
            contract["runner"]["sha256"] = "1" * 64
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact workflow bytes"):
                validate(workflow, contract_path)

    def test_github_workflow_cannot_stage_private_input(self) -> None:
        temporary, workflow, contract = self.fixture()
        with temporary:
            workflow.write_text(
                workflow.read_text(encoding="utf-8") + "\n# --private-input secret\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "target-bearing private input"):
                validate(workflow, contract)

    def test_unsigned_harness_request_is_rejected(self) -> None:
        temporary, workflow, contract = self.fixture()
        with temporary:
            value = json.loads(contract.read_text(encoding="utf-8"))
            value["controlled_harness"]["authentication"] = "NONE"
            contract.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not GitHub-signed"):
                validate(workflow, contract)

    def test_target_identity_cannot_enter_signed_request(self) -> None:
        temporary, workflow, contract = self.fixture()
        with temporary:
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    '              "protocol_version": "1.5",\n',
                    '              "protocol_version": "1.5",\n              "cluster_id": "secret",\n',
                    1,
                ), encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "signed scheduler request contains"):
                validate(workflow, contract)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--runtime", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(WorkflowContractMutationTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    try:
        validate(args.workflow.resolve(), args.contract.resolve(), runtime=args.runtime)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Method v1.5 checkpoint workflow contract: FAIL: {exc}")
        return 2
    print("Method v1.5 checkpoint workflow contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
