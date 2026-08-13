#!/usr/bin/env python3
"""Adversarial tests for the PRE-P1 target-blind custody contracts."""

from __future__ import annotations

import base64
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import sys
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_benchmark_v15_private_custody as custody


START = datetime(2026, 8, 13, 0, 0, tzinfo=timezone.utc)


def timestamp(seconds: int) -> str:
    return (START + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


class Fixture:
    def __init__(self) -> None:
        self.keys = {
            host: Ed25519PrivateKey.generate() for host in ("companion-mac", "ai-vps")
        }
        self.blob = b"opaque delivered byte stream"
        self.blob_sha = hashlib.sha256(self.blob).hexdigest()
        self.blobs = {self.blob_sha: self.blob}

    def public_keys(self) -> dict[tuple[str, str], bytes]:
        return {
            (host, f"pre-p1-{host}"): key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            for host, key in self.keys.items()
        }

    def record(
        self,
        sequence: int,
        previous: str | None,
        seconds: int,
        *,
        event: str = "HEARTBEAT",
        boot: str = "boot-a",
    ) -> dict:
        payload = self.blob_sha if event not in {"HEARTBEAT", "RESTART"} else custody.EMPTY_SHA256
        count = len(self.blob) if event not in {"HEARTBEAT", "RESTART"} else 0
        record = {
            "sequence_number": sequence,
            "previous_receipt_sha256": previous,
            "event_kind": event,
            "payload_sha256": payload,
            "payload_byte_count": count,
            "delivery_channel": "session-capture",
            "observed_at_utc": timestamp(seconds),
            "boot_id": boot,
        }
        record["receipt_sha256"] = custody.record_digest(record)
        return record

    def batch(
        self,
        host: str,
        batch_sequence: int,
        previous_batch: str | None,
        records: list[dict],
    ) -> dict:
        batch = {
            "schema": custody.BATCH_SCHEMA,
            "status": "PRE_P1_PRIVATE_CUSTODY_NOT_OPERATIONAL",
            "protocol_version": "1.5",
            "host_id": host,
            "signing_key_id": f"pre-p1-{host}",
            "signature_algorithm": "Ed25519",
            "batch_sequence": batch_sequence,
            "previous_batch_sha256": previous_batch,
            "boot_id": records[0]["boot_id"],
            "captured_from_utc": records[0]["observed_at_utc"],
            "captured_through_utc": records[-1]["observed_at_utc"],
            "maximum_heartbeat_interval_seconds": 300,
            "first_record_sequence": records[0]["sequence_number"],
            "last_record_sequence": records[-1]["sequence_number"],
            "records": records,
        }
        batch["batch_sha256"] = custody.batch_digest(batch)
        batch["signature"] = base64.b64encode(
            self.keys[host].sign(bytes.fromhex(batch["batch_sha256"]))
        ).decode()
        return batch

    def host_batches(self, host: str, *, late: bool = False) -> list[dict]:
        offset = 60 if late else 0
        first = self.record(0, None, offset)
        second = self.record(1, first["receipt_sha256"], 240 + offset, event="DELIVERY")
        return [self.batch(host, 0, None, [first, second])]

    def valid(self) -> tuple[list[dict], dict]:
        batches = self.host_batches("companion-mac") + self.host_batches("ai-vps")
        certificate = custody.verify_coverage(
            batches,
            self.public_keys(),
            self.blobs,
            ["companion-mac", "ai-vps"],
            timestamp(0),
            timestamp(240),
        )
        return batches, certificate


class CustodyContractTests(unittest.TestCase):
    def test_valid_two_host_chain_and_public_binding_are_pre_p1(self) -> None:
        fixture = Fixture()
        _, certificate = fixture.valid()
        binding = custody.public_sealed_binding(certificate, b"opaque authenticated envelope")
        self.assertEqual(certificate["status"], "PRE_P1_VERIFIED_CONTRACT_NOT_OPERATIONAL")
        self.assertEqual(binding["status"], "PRE_P1_PUBLIC_BINDING_NOT_OPERATIONAL")
        self.assertNotIn("host_id", binding)
        self.assertNotIn(fixture.blob.decode(), str(binding))

    def test_chain_splice_or_rewrite_is_rejected_even_when_resigned(self) -> None:
        fixture = Fixture()
        batches = fixture.host_batches("companion-mac")
        first = batches[0]["records"][0]
        batches[0]["records"][1]["previous_receipt_sha256"] = "0" * 64
        batches[0]["records"][1]["receipt_sha256"] = custody.record_digest(batches[0]["records"][1])
        batches[0] = fixture.batch("companion-mac", 0, None, batches[0]["records"])
        with self.assertRaisesRegex(custody.CustodyError, "chain splice"):
            custody.verify_coverage(batches, fixture.public_keys(), fixture.blobs, ["companion-mac"], timestamp(0), timestamp(240))
        self.assertIsNotNone(first)

    def test_missing_sequence_and_heartbeat_gap_are_rejected(self) -> None:
        fixture = Fixture()
        first = fixture.record(0, None, 0)
        skipped = fixture.record(2, first["receipt_sha256"], 240)
        batch = fixture.batch("ai-vps", 0, None, [first, skipped])
        with self.assertRaisesRegex(custody.CustodyError, "record sequence"):
            custody.verify_coverage([batch], fixture.public_keys(), fixture.blobs, ["ai-vps"], timestamp(0), timestamp(240))

        late = fixture.record(1, first["receipt_sha256"], 301)
        batch = fixture.batch("ai-vps", 0, None, [first, late])
        with self.assertRaisesRegex(custody.CustodyError, "heartbeat"):
            custody.verify_coverage([batch], fixture.public_keys(), fixture.blobs, ["ai-vps"], timestamp(0), timestamp(301))

    def test_sequence_overflow_and_unmarked_restart_are_rejected(self) -> None:
        fixture = Fixture()
        first = fixture.record(0, None, 0)
        overflow = fixture.record(custody.MAX_SEQUENCE, first["receipt_sha256"], 240)
        batch = fixture.batch("ai-vps", 0, None, [first, overflow])
        with self.assertRaisesRegex(custody.CustodyError, "sequence"):
            custody.verify_coverage([batch], fixture.public_keys(), fixture.blobs, ["ai-vps"], timestamp(0), timestamp(240))

        first_batch = fixture.batch("ai-vps", 0, None, [first])
        changed_boot = fixture.record(1, first["receipt_sha256"], 240, boot="boot-b")
        second_batch = fixture.batch("ai-vps", 1, first_batch["batch_sha256"], [changed_boot])
        with self.assertRaisesRegex(custody.CustodyError, "without an explicit restart"):
            custody.verify_coverage([first_batch, second_batch], fixture.public_keys(), fixture.blobs, ["ai-vps"], timestamp(0), timestamp(240))

    def test_payload_blob_mismatch_is_rejected(self) -> None:
        fixture = Fixture()
        batches = fixture.host_batches("ai-vps")
        with self.assertRaisesRegex(custody.CustodyError, "payload blob mismatch"):
            custody.verify_coverage(batches, fixture.public_keys(), {fixture.blob_sha: b"wrong"}, ["ai-vps"], timestamp(0), timestamp(240))

    def test_cross_host_coverage_gap_is_rejected(self) -> None:
        fixture = Fixture()
        batches = fixture.host_batches("companion-mac") + fixture.host_batches("ai-vps", late=True)
        with self.assertRaisesRegex(custody.CustodyError, "does not cover"):
            custody.verify_coverage(batches, fixture.public_keys(), fixture.blobs, ["companion-mac", "ai-vps"], timestamp(0), timestamp(240))

    def test_forbidden_private_fields_cannot_enter_public_binding(self) -> None:
        fixture = Fixture()
        _, certificate = fixture.valid()
        binding = custody.public_sealed_binding(certificate, b"opaque authenticated envelope")
        contaminated = deepcopy(binding)
        contaminated["host_id"] = "ai-vps"
        with self.assertRaises(custody.CustodyError):
            custody.validate_public_binding(contaminated)

        contaminated = deepcopy(binding)
        contaminated["payload_sha256"] = fixture.blob_sha
        with self.assertRaises(custody.CustodyError):
            custody.validate_public_binding(contaminated)


if __name__ == "__main__":
    unittest.main()
