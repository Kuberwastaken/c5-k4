#!/usr/bin/env python3
"""Adversarial tests for v1.5 activation identity/evidence continuity."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_benchmark_v15_activation_continuity.py"
SPEC = importlib.util.spec_from_file_location("verify_v15_activation_continuity", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class ActivationContinuityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = {
            "service_identity": {"name": "canonical-service"},
            "resources": {
                "p1_checkout": {"path": "/opt/canonical/p1"},
                "private_roots": ["/var/lib/canonical", "/var/cache/canonical"],
                "control_sockets": ["/run/canonical/control.sock"],
                "credential_roots": ["/etc/canonical/credentials"],
            },
        }
        self.deployment = {
            "identity": {"user": "canonical-service", "group": "canonical-service"},
            "paths": {
                "p1_checkout": {"path": "/opt/canonical/p1"},
                "private_state": {"path": "/var/lib/canonical"},
                "private_cache": {"path": "/var/cache/canonical"},
                "runtime": {"path": "/run/canonical"},
                "configuration": {"path": "/etc/canonical"},
                "credential_root": {"path": "/etc/canonical/credentials"},
            },
        }
        self.activation = {"p1": {"tree_path": "/opt/canonical/p1", "tree_sha256": "1" * 64}}
        self.unit = {
            "p1_tree_sha256": "1" * 64,
            "unit": {"content": "\n".join([
                "[Service]", "User=canonical-service", "Group=canonical-service",
                "WorkingDirectory=/var/lib/canonical",
                "ReadWritePaths=/var/lib/canonical /var/cache/canonical /run/canonical",
            ])},
        }

    def verify(self) -> None:
        module.check_identity_continuity(self.ledger, self.deployment, self.activation, self.unit)

    def test_one_aligned_identity_and_path_closure_passes(self) -> None:
        self.verify()

    def test_service_identity_substitution_fails(self) -> None:
        for location in ("deployment", "unit_user", "unit_group"):
            deployment = copy.deepcopy(self.deployment)
            unit = copy.deepcopy(self.unit)
            if location == "deployment":
                deployment["identity"]["user"] = "other-service"
            else:
                unit["unit"]["content"] = unit["unit"]["content"].replace(
                    "User=canonical-service" if location == "unit_user" else "Group=canonical-service",
                    "User=other-service" if location == "unit_user" else "Group=other-service",
                )
            with self.assertRaisesRegex(module.ContinuityError, "service identity"):
                module.check_identity_continuity(self.ledger, deployment, self.activation, unit)

    def test_each_p1_binding_must_agree(self) -> None:
        deployment = copy.deepcopy(self.deployment)
        deployment["paths"]["p1_checkout"]["path"] = "/opt/other/p1"
        with self.assertRaisesRegex(module.ContinuityError, "deployment P1"):
            module.check_identity_continuity(self.ledger, deployment, self.activation, self.unit)
        activation = copy.deepcopy(self.activation)
        activation["p1"]["tree_path"] = "/opt/other/p1"
        with self.assertRaisesRegex(module.ContinuityError, "activation P1"):
            module.check_identity_continuity(self.ledger, self.deployment, activation, self.unit)
        unit = copy.deepcopy(self.unit)
        unit["p1_tree_sha256"] = "2" * 64
        with self.assertRaisesRegex(module.ContinuityError, "activation P1 tree"):
            module.check_identity_continuity(self.ledger, self.deployment, self.activation, unit)

    def test_private_or_extra_writable_root_fails(self) -> None:
        deployment = copy.deepcopy(self.deployment)
        deployment["paths"]["private_state"]["path"] = "/var/lib/other"
        with self.assertRaisesRegex(module.ContinuityError, "private roots"):
            module.check_identity_continuity(self.ledger, deployment, self.activation, self.unit)
        unit = copy.deepcopy(self.unit)
        unit["unit"]["content"] += " /tmp/unregistered"
        with self.assertRaisesRegex(module.ContinuityError, "writable path outside"):
            module.check_identity_continuity(self.ledger, self.deployment, self.activation, unit)

    def test_socket_and_credential_roots_must_stay_inside_deployment(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["resources"]["control_sockets"] = ["/tmp/control.sock"]
        with self.assertRaisesRegex(module.ContinuityError, "control socket"):
            module.check_identity_continuity(ledger, self.deployment, self.activation, self.unit)
        ledger = copy.deepcopy(self.ledger)
        ledger["resources"]["credential_roots"] = ["/root/secret"]
        with self.assertRaisesRegex(module.ContinuityError, "credential root"):
            module.check_identity_continuity(ledger, self.deployment, self.activation, self.unit)

    def test_duplicate_or_missing_unit_directive_fails(self) -> None:
        for content in (
            self.unit["unit"]["content"].replace("User=canonical-service\n", ""),
            self.unit["unit"]["content"] + "\nUser=canonical-service",
        ):
            unit = copy.deepcopy(self.unit)
            unit["unit"]["content"] = content
            with self.assertRaisesRegex(module.ContinuityError, "exactly one User"):
                module.check_identity_continuity(self.ledger, self.deployment, self.activation, unit)

    def test_committed_static_audit_accepts_one_canonical_interface(self) -> None:
        self.assertIsNone(module.verify_committed_pre_p1_continuity())

    def test_reconciled_deployment_uses_canonical_ledger_naming(self) -> None:
        ledger = module.load_object(module.PROTOCOL / "participant-ledger.json")
        deployment = module.load_object(module.PROTOCOL / "controlled-harness-deployment-contract.json")
        self.assertEqual(ledger["service_identity"]["name"], "c5k4-benchmark-v15")
        self.assertEqual(deployment["identity"]["user"], "c5k4-benchmark-v15")
        self.assertEqual(ledger["resources"]["p1_checkout"]["path"], "/opt/c5k4-benchmark-v15/p1")
        self.assertEqual(deployment["paths"]["p1_checkout"]["path"], "/opt/c5k4-benchmark-v15/p1")

    def test_target_material_is_rejected_recursively(self) -> None:
        for key in ("target_id", "cluster_id", "statement_text", "outcome"):
            with self.assertRaisesRegex(module.ContinuityError, "target-bearing"):
                module.reject_target_material({"nested": [{key: "forbidden"}]})

    def interface_fixture(self) -> tuple[dict, dict, dict, dict]:
        endpoint = "https://harness.example.org:443/v1/checkpoint"
        invocation = {
            "controlled_harness": {
                "https_endpoint": endpoint,
                "oidc_audience_prefix": "c5k4-method-v1.5",
                "request_signature_binding": "OIDC_AUDIENCE_SUFFIX_IS_SHA256_OF_CANONICAL_REQUEST_BYTES",
            },
            "frozen": {
                "workflow_path": ".github/workflows/method-v15-checkpoint.yml",
                "workflow_sha256": module.hashlib.sha256((ROOT / ".github/workflows/method-v15-checkpoint.yml").read_bytes()).hexdigest(),
            },
        }
        oidc = {
            "issuer": "https://token.actions.githubusercontent.com",
            "audience_prefix": "c5k4-method-v1.5",
            "repository": "Kuberwastaken/c5-k4",
            "ref": "refs/heads/main",
            "workflow_ref": "Kuberwastaken/c5-k4/.github/workflows/method-v15-checkpoint.yml@refs/heads/main",
            "event_name": "schedule",
            "run_attempt": "1",
        }
        service = {"transport": {"https_endpoint": endpoint}, "oidc": oidc}
        activation = {"listener": {"https_endpoint": endpoint}, "oidc": dict(oidc)}
        unit = {
            "network_policy": {"listener": {"https_endpoint": endpoint}},
            "bound_acceptances": {"oidc_config_sha256": module.hashlib.sha256(module.canonical_bytes(activation["oidc"])).hexdigest()},
        }
        return invocation, service, activation, unit

    def test_canonical_request_interface_passes_and_prep1_nulls_are_not_mismatches(self) -> None:
        invocation, service, activation, unit = self.interface_fixture()
        workflow = (ROOT / ".github/workflows/method-v15-checkpoint.yml").read_bytes()
        result = module.check_request_interface_continuity(invocation, service, activation, unit, require_operational=True, workflow_bytes=workflow)
        self.assertTrue(result["audience_operationally_bound"])
        self.assertTrue(result["endpoint_operationally_bound"])
        invocation["controlled_harness"]["https_endpoint"] = None
        invocation["controlled_harness"]["oidc_audience_prefix"] = None
        service["transport"]["https_endpoint"] = None
        service["oidc"]["audience_prefix"] = None
        result = module.check_request_interface_continuity(invocation, service, activation, unit, require_operational=False)
        self.assertFalse(result["audience_operationally_bound"])
        self.assertFalse(result["endpoint_operationally_bound"])
        with self.assertRaisesRegex(module.ContinuityError, "PRE-P1 null"):
            module.check_request_interface_continuity(invocation, service, activation, unit, require_operational=True, workflow_bytes=workflow)

    def test_audience_prefix_and_endpoint_path_splits_fail(self) -> None:
        invocation, service, activation, unit = self.interface_fixture()
        activation["oidc"]["audience_prefix"] = "c5k4-v15-checkpoint"
        with self.assertRaisesRegex(module.ContinuityError, "audience prefix differs"):
            module.check_request_interface_continuity(invocation, service, activation, unit, require_operational=True, workflow_bytes=(ROOT / ".github/workflows/method-v15-checkpoint.yml").read_bytes())
        invocation, service, activation, unit = self.interface_fixture()
        unit["network_policy"]["listener"]["https_endpoint"] = "https://harness.example.org:443/"
        with self.assertRaisesRegex(module.ContinuityError, "endpoint path differs"):
            module.check_request_interface_continuity(invocation, service, activation, unit, require_operational=True, workflow_bytes=(ROOT / ".github/workflows/method-v15-checkpoint.yml").read_bytes())

    def test_cli_is_silent_and_accepts_only_explicit_static_audit(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--audit-committed-pre-p1"],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")
        no_mode = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(no_mode.returncode, 2)
        self.assertEqual(no_mode.stdout, "")
        self.assertEqual(no_mode.stderr, "")

    def test_digest_binding_is_order_deterministic(self) -> None:
        left = {"a": 1, "b": 2, "sha256": "0" * 64}
        right = {"b": 2, "sha256": "f" * 64, "a": 1}
        self.assertEqual(module.digest_object(left, "sha256"), module.digest_object(right, "sha256"))


if __name__ == "__main__":
    unittest.main()
