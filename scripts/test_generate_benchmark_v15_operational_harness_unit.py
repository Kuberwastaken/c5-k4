#!/usr/bin/env python3
"""Adversarial tests for the inert future operational harness-unit generator."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_benchmark_v15_operational_harness_unit.py"
SPEC = importlib.util.spec_from_file_location("generate_v15_operational_unit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def seal(value: dict, key: str) -> dict:
    value[key] = module.digest_object(value, key)
    return value


class OperationalHarnessUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.fs = Path(temporary.name)
        binary = self.fs / "opt/c5k4-benchmark-v15/p1/bin/c5k4-controlled-harness"
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b"#!/bin/sh\nexit 2\n")
        binary.chmod(0o555)
        (self.fs / "opt/c5k4-benchmark-v15/p1").chmod(0o555)
        (self.fs / "opt/c5k4-benchmark-v15/p1/bin").chmod(0o555)
        tls = self.fs / "etc/c5k4-benchmark-v15/credentials/tls"
        tls.mkdir(parents=True)
        cert = tls / "fullchain.pem"; key = tls / "private-key.pem"
        generated = subprocess.run([
            "openssl", "req", "-x509", "-newkey", "ed25519", "-nodes",
            "-keyout", str(key), "-out", str(cert), "-days", "1",
            "-subj", "/CN=harness.example.org",
        ], text=True, capture_output=True)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        cert.chmod(0o444); key.chmod(0o400)

        key_commitment = seal({
            "schema": "c5k4-method-v1.5-operational-noninterference-key-commitment-1.0",
            "status": "FROZEN_P1_NONINTERFERENCE_KEY_COMMITTED", "protocol_version": "1.5",
            "host_id": "ai-vps-controlled-harness", "signing_key_id": "p1-key-1",
            "signature_algorithm": "Ed25519", "verification_key_sha256": "1" * 64,
            "operational": True, "activation_permitted": True, "target_specific": False,
            "commitment_sha256": module.ZERO,
        }, "commitment_sha256")
        worm = seal({
            "schema": "c5k4-method-v1.5-operational-worm-acceptance-1.0",
            "status": "OPERATIONAL_WORM_ACCEPTANCE_PASSED", "store_config_sha256": "2" * 64,
            "object_lock_mode": "COMPLIANCE", "versioning_enabled": True,
            "retention_verified": True, "destructive_write_rejected": True,
            "operational": True, "activation_permitted": True, "acceptance_sha256": module.ZERO,
        }, "acceptance_sha256")
        tests = ["DESTRUCTIVE_WRITE", "TRUNCATION", "SERVICE_RESTART", "OFFLINE_GAP", "SEQUENCE_CONFLICT", "UNEXPECTED_INGRESS"]
        gap = seal({
            "schema": "c5k4-method-v1.5-operational-destructive-gap-acceptance-1.0",
            "status": "OPERATIONAL_DESTRUCTIVE_GAP_ACCEPTANCE_PASSED", "tests": tests,
            "evidence_sha256": {name: format(index + 3, "x") * 64 for index, name in enumerate(tests)},
            "all_passed": True, "operational": True, "activation_permitted": True,
            "acceptance_sha256": module.ZERO,
        }, "acceptance_sha256")
        endpoint_specs = [
            ("GITHUB", "OIDC_JWKS", "token.actions.githubusercontent.com", "20.201.28.1/32"),
            ("GITHUB", "PUBLIC_CHAIN_API", "api.github.com", "20.207.73.82/32"),
            ("AWS", "S3_OBJECT_LOCK", "s3.ap-south-1.amazonaws.com", "13.233.177.1/32"),
            ("AWS", "KMS", "kms.ap-south-1.amazonaws.com", "13.232.81.1/32"),
            ("AWS", "STS", "sts.ap-south-1.amazonaws.com", "13.234.10.1/32"),
        ]
        endpoints = [
            {"provider": provider, "service": service, "hostname": host, "port": 443,
             "protocol": "HTTPS", "tls_sni_required": True, "pinned_cidrs": [cidr]}
            for provider, service, host, cidr in endpoint_specs
        ]
        resolution = self.fs / "etc/c5k4-benchmark-v15/credentials/pinned-hosts"
        resolution.write_text("".join(f"{cidr.split('/')[0]} {host}\n" for _, _, host, cidr in endpoint_specs), encoding="ascii")
        resolution.chmod(0o444)
        self.value = {
            "schema": "c5k4-method-v1.5-operational-controlled-harness-activation-inputs-1.0",
            "status": "P1_OPERATIONAL_ACTIVATION_INPUTS_COMPLETE", "protocol_version": "1.5",
            "host_id": "ai-vps-controlled-harness",
            "p1": {"tree_path": "/opt/c5k4-benchmark-v15/p1", "tree_sha256": module.tree_sha256(self.fs / "opt/c5k4-benchmark-v15/p1"), "commit": "a" * 40},
            "service": {"binary_path": "/opt/c5k4-benchmark-v15/p1/bin/c5k4-controlled-harness", "binary_sha256": module.file_sha256(binary), "activation_binding_path": "/etc/c5k4-benchmark-v15/OPERATIONAL-ACTIVATION.json", "control_socket_path": "/run/c5k4-benchmark-v15/control.sock"},
            "listener": {"https_endpoint": "https://harness.example.org:443/v1/checkpoint", "bind_address": "13.200.253.63", "port": 443},
            "tls": {"certificate_path": "/etc/c5k4-benchmark-v15/credentials/tls/fullchain.pem", "certificate_sha256": module.file_sha256(cert), "private_key_path": "/etc/c5k4-benchmark-v15/credentials/tls/private-key.pem", "private_key_sha256": module.file_sha256(key), "minimum_version": "TLSv1.3", "client_certificate_policy": "OIDC_BEARER_REQUIRED_NO_CLIENT_CERT"},
            "oidc": {"issuer": "https://token.actions.githubusercontent.com", "audience": f"c5k4-method-v1.5:{'b' * 64}", "repository": "Kuberwastaken/c5-k4", "ref": "refs/heads/main", "workflow_ref": "Kuberwastaken/c5-k4/.github/workflows/method-v15-checkpoint.yml@refs/heads/main", "event_name": "schedule", "run_attempt": "1"},
            "noninterference_key_commitment": key_commitment, "worm_acceptance": worm,
            "destructive_gap_acceptance": gap,
            "network": {"default_deny": True, "unlisted_egress_forbidden": True, "dns_policy": "ALLOWLIST_ONLY_PINNED_RESOLUTION", "aws_region": "ap-south-1", "resolution_artifact_path": "/etc/c5k4-benchmark-v15/credentials/pinned-hosts", "resolution_artifact_sha256": module.file_sha256(resolution), "allowed_endpoints": endpoints},
            "target_specific": False, "activation_inputs_sha256": module.ZERO,
        }
        seal(self.value, "activation_inputs_sha256")

    def reseal(self, value: dict) -> dict:
        return seal(value, "activation_inputs_sha256")

    def test_complete_inputs_generate_inert_bound_successor(self) -> None:
        key_path = self.fs / "etc/c5k4-benchmark-v15/credentials/tls/private-key.pem"
        key_mode_before = key_path.stat().st_mode & 0o777
        bundle = module.generate(self.value, self.fs)
        self.assertEqual(bundle["p1_tree_sha256"], self.value["p1"]["tree_sha256"])
        self.assertEqual(bundle["namespace_capabilities"], list(module.NAMESPACES))
        self.assertEqual(bundle["status"], "FIXTURE_UNIT_GENERATED_NONOPERATIONAL")
        self.assertEqual(bundle["validation_environment"], {"filesystem_scope": "FIXTURE_ROOT", "production_root_ownership_proven": False, "pinned_resolution_artifact_verified": True, "runnable_candidate": False})
        self.assertFalse(bundle["installed"]); self.assertFalse(bundle["active"]); self.assertFalse(bundle["activation_permitted"])
        self.assertIn("RestrictNamespaces=user mnt net pid ipc uts cgroup", bundle["unit"]["content"])
        self.assertIn("IPAddressDeny=any", bundle["unit"]["content"])
        self.assertIn("BindReadOnlyPaths=/etc/c5k4-benchmark-v15/credentials/pinned-hosts:/etc/hosts", bundle["unit"]["content"])
        self.assertIn("LoadCredential=tls-private-key:/etc/c5k4-benchmark-v15/credentials/tls/private-key.pem", bundle["unit"]["content"])
        self.assertIn("--tls-private-key=%d/tls-private-key", bundle["unit"]["content"])
        self.assertIn("--control-socket=/run/c5k4-benchmark-v15/control.sock", bundle["unit"]["content"])
        self.assertIn("--tls-certificate=/etc/c5k4-benchmark-v15/credentials/tls/fullchain.pem", bundle["unit"]["content"])
        self.assertNotIn("--tls-private-key=/etc/c5k4-benchmark-v15/credentials/tls/private-key.pem", bundle["unit"]["content"])
        self.assertEqual(bundle["tls_material"], {
            "certificate_source": "/etc/c5k4-benchmark-v15/credentials/tls/fullchain.pem",
            "certificate_sha256": self.value["tls"]["certificate_sha256"],
            "private_key_source": "/etc/c5k4-benchmark-v15/credentials/tls/private-key.pem",
            "private_key_sha256": self.value["tls"]["private_key_sha256"],
            "private_key_runtime_credential": "%d/tls-private-key",
            "credential_loader": "systemd LoadCredential",
            "source_permissions_widened": False,
        })
        self.assertEqual(key_mode_before, 0o400)
        self.assertEqual(key_path.stat().st_mode & 0o777, key_mode_before)
        for endpoint in self.value["network"]["allowed_endpoints"]:
            self.assertIn(f"IPAddressAllow={endpoint['pinned_cidrs'][0]}", bundle["unit"]["content"])
        self.assertEqual(bundle["bundle_sha256"], module.digest_object(bundle, "bundle_sha256"))

    def test_both_schemas_are_draft7_valid(self) -> None:
        for path in (module.INPUT_SCHEMA, module.OUTPUT_SCHEMA):
            Draft7Validator.check_schema(module.load_object(path))

    def test_workflow_and_emitted_network_shape_are_schema_closed(self) -> None:
        wrong_workflow = copy.deepcopy(self.value)
        wrong_workflow["oidc"]["workflow_ref"] = "Kuberwastaken/c5-k4/.github/workflows/other.yml@refs/heads/main"
        self.reseal(wrong_workflow)
        with self.assertRaisesRegex(module.UnitContractError, "schema failure"):
            module.generate(wrong_workflow, self.fs)

        output_schema = module.load_object(module.OUTPUT_SCHEMA)
        bundle = module.generate(self.value, self.fs)
        forged_endpoint = copy.deepcopy(bundle)
        forged_endpoint["network_policy"]["allowed_endpoints"][0]["hostname"] = "evil.example.org"
        self.assertTrue(list(Draft7Validator(output_schema).iter_errors(forged_endpoint)))
        forged_listener = copy.deepcopy(bundle)
        forged_listener["network_policy"]["listener"]["fallback_port"] = 8443
        self.assertTrue(list(Draft7Validator(output_schema).iter_errors(forged_listener)))

    def test_each_acceptance_must_pass_and_self_bind(self) -> None:
        for field, flag in (("worm_acceptance", "retention_verified"), ("destructive_gap_acceptance", "all_passed"), ("noninterference_key_commitment", "operational")):
            mutated = copy.deepcopy(self.value); mutated[field][flag] = False; self.reseal(mutated)
            with self.assertRaisesRegex(module.UnitContractError, "schema failure"):
                module.generate(mutated, self.fs)
        mutated = copy.deepcopy(self.value); mutated["worm_acceptance"]["store_config_sha256"] = "f" * 64; self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "WORM acceptance self-digest"):
            module.generate(mutated, self.fs)

    def test_p1_binary_and_tls_bytes_are_verified(self) -> None:
        cases = [
            ("p1", "tree_sha256", "P1 tree digest"),
            ("service", "binary_sha256", "digest mismatch"),
            ("tls", "certificate_sha256", "digest mismatch"),
            ("tls", "private_key_sha256", "digest mismatch"),
        ]
        for section, field, message in cases:
            mutated = copy.deepcopy(self.value); mutated[section][field] = "f" * 64; self.reseal(mutated)
            with self.assertRaisesRegex(module.UnitContractError, message):
                module.generate(mutated, self.fs)

    def test_tls_key_permissions_fail_closed(self) -> None:
        key = self.fs / "etc/c5k4-benchmark-v15/credentials/tls/private-key.pem"; key.chmod(0o644)
        with self.assertRaisesRegex(module.UnitContractError, "private TLS key permissions"):
            module.generate(self.value, self.fs)

    def test_endpoint_expansion_reordering_or_broad_cidr_fails(self) -> None:
        mutated = copy.deepcopy(self.value); mutated["network"]["allowed_endpoints"].append(copy.deepcopy(mutated["network"]["allowed_endpoints"][0])); self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "schema failure"):
            module.generate(mutated, self.fs)
        mutated = copy.deepcopy(self.value); mutated["network"]["allowed_endpoints"].reverse(); self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "schema failure"):
            module.generate(mutated, self.fs)
        mutated = copy.deepcopy(self.value); mutated["network"]["allowed_endpoints"][0]["pinned_cidrs"] = ["20.0.0.0/8"]; self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "schema failure"):
            module.generate(mutated, self.fs)

    def test_symlinked_immutable_parent_fails_closed(self) -> None:
        real = self.fs / "etc/c5k4-benchmark-v15/credentials/tls-real"
        (self.fs / "etc/c5k4-benchmark-v15/credentials/tls").rename(real)
        (self.fs / "etc/c5k4-benchmark-v15/credentials/tls").symlink_to(real)
        with self.assertRaisesRegex(module.UnitContractError, "symlinked parent"):
            module.generate(self.value, self.fs)

    def test_tls_spki_is_derived_and_mismatched_key_fails(self) -> None:
        bundle = module.generate(self.value, self.fs)
        self.assertEqual(len(bundle["bound_acceptances"]["tls_spki_sha256"]), 64)
        self.assertNotIn("spki_sha256", self.value["tls"])
        foreign_key = self.fs / "foreign-key.pem"
        foreign_cert = self.fs / "foreign-cert.pem"
        generated = subprocess.run([
            "openssl", "req", "-x509", "-newkey", "ed25519", "-nodes",
            "-keyout", str(foreign_key), "-out", str(foreign_cert), "-days", "1",
            "-subj", "/CN=harness.example.org",
        ], text=True, capture_output=True)
        self.assertEqual(generated.returncode, 0, generated.stderr)
        target = self.fs / "etc/c5k4-benchmark-v15/credentials/tls/private-key.pem"
        target.chmod(0o600); target.write_bytes(foreign_key.read_bytes()); target.chmod(0o400)
        mutated = copy.deepcopy(self.value); mutated["tls"]["private_key_sha256"] = module.file_sha256(target); self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "does not match"):
            module.generate(mutated, self.fs)

    def test_resolution_artifact_is_exact_and_digest_bound(self) -> None:
        path = self.fs / "etc/c5k4-benchmark-v15/credentials/pinned-hosts"
        path.chmod(0o644); path.write_text(path.read_text() + "1.1.1.1 example.org\n", encoding="ascii"); path.chmod(0o444)
        mutated = copy.deepcopy(self.value); mutated["network"]["resolution_artifact_sha256"] = module.file_sha256(path); self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "does not exactly bind"):
            module.generate(mutated, self.fs)

    def test_target_semantics_and_unbound_outer_mutation_fail(self) -> None:
        mutated = copy.deepcopy(self.value); mutated["target_id"] = "hidden"; self.reseal(mutated)
        with self.assertRaisesRegex(module.UnitContractError, "schema failure"):
            module.generate(mutated, self.fs)
        mutated = copy.deepcopy(self.value); mutated["oidc"]["audience"] = f"c5k4-method-v1.5:{'c' * 64}"
        with self.assertRaisesRegex(module.UnitContractError, "activation inputs self-digest"):
            module.generate(mutated, self.fs)

    def test_cli_is_deterministic_and_never_writes_or_activates(self) -> None:
        inputs = self.fs / "activation.json"; inputs.write_bytes(module.canonical_bytes(self.value))
        command = [sys.executable, str(SCRIPT), "--activation-inputs", str(inputs), "--filesystem-root", str(self.fs)]
        first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(first.returncode, 0); self.assertEqual(first.stderr, ""); self.assertEqual(first.stdout, second.stdout)
        bundle = json.loads(first.stdout)
        self.assertFalse(bundle["installed"]); self.assertFalse(bundle["active"]); self.assertFalse(bundle["activation_permitted"])
        self.assertFalse((self.fs / "etc/c5k4-benchmark-v15/OPERATIONAL-ACTIVATION.json").exists())

    def test_cli_invalid_input_fails_closed_and_silent(self) -> None:
        inputs = self.fs / "bad.json"; inputs.write_text("{}\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--activation-inputs", str(inputs), "--filesystem-root", str(self.fs)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2); self.assertEqual(result.stdout, ""); self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
