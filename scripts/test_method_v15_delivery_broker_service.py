#!/usr/bin/env python3
"""Operational-acceptance tests for the PRE-P1 broker service boundary."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import method_v15_delivery_broker as broker
import method_v15_delivery_broker_service as service


def at(seconds: int) -> datetime:
    return datetime(2026, 8, 13, 12, 0, seconds, tzinfo=timezone.utc)


def instant(seconds: float) -> datetime:
    return datetime(2026, 8, 13, 12, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)


class FixedClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        return self.value


class AdvancingClock:
    def __init__(self, value: datetime):
        self.value = value

    def __call__(self) -> datetime:
        result = self.value
        self.value += timedelta(seconds=1)
        return result


class FailingSink:
    def write(self, _: bytes) -> int:
        raise OSError("sink unavailable")

    def flush(self) -> None:
        pass


class ServiceFixture:
    def __init__(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "state"
        self.key = Ed25519PrivateKey.generate()
        self.key_path = Path(self.temp.name) / "host.key"
        self.key_path.write_bytes(self.key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption()))
        self.key_path.chmod(0o600)
        self.config = broker.test_config(self.root)
        self.config_path = Path(self.temp.name) / "config.json"
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")

    def close(self) -> None:
        self.temp.cleanup()


class BrokerServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.f = ServiceFixture()

    def tearDown(self) -> None:
        self.f.close()

    def open(self, clock: object | None = None, **kwargs: object) -> service.BrokerService:
        return service.BrokerService(self.f.root, self.f.config, self.f.key, acceptance_test=True, clock=clock or FixedClock(at(0)), **kwargs)

    def test_single_writer_rejects_concurrent_service(self) -> None:
        first = self.open()
        try:
            with self.assertRaisesRegex(service.ServiceError, "another delivery-broker writer"):
                self.open()
        finally:
            first.close()
        reopened = self.open()
        reopened.close()

    def test_restart_continues_receipt_chain_and_heartbeat(self) -> None:
        with self.open(FixedClock(at(0))) as first:
            result = first.run([sys.executable, "-c", "print('one', end='')"], b"")
            first_tip = first.broker.state["last_receipt_sha256"]
        with self.open(FixedClock(at(1))) as second:
            result2 = second.run([sys.executable, "-c", "print('two', end='')"], b"")
            self.assertNotEqual(second.broker.state["last_receipt_sha256"], first_tip)
            self.assertEqual(result.stdout + result2.stdout, b"onetwo")
            sequences = [json.loads(path.read_text())["sequence_number"] for path in second.broker._receipt_files()]
            self.assertEqual(sequences, list(range(len(sequences))))

    def test_restart_with_stale_heartbeat_locks_before_command(self) -> None:
        with self.open(FixedClock(at(0))) as first:
            first.broker.heartbeat("2026-08-13T12:00:00Z")
        late = FixedClock(datetime(2026, 8, 13, 12, 4, 1, tzinfo=timezone.utc))
        with self.open(late) as second:
            with self.assertRaisesRegex(broker.BrokerError, "heartbeat stale"):
                second.run([sys.executable, "-c", "print('must not run')"], b"")
        self.assertTrue((self.f.root / "LOCKED_INVALID").exists())

    def test_long_running_command_emits_heartbeats(self) -> None:
        config = self.f.config
        config["heartbeat_interval_seconds"] = 1
        with service.BrokerService(self.f.root, config, self.f.key, acceptance_test=True) as wrapper:
            result = wrapper.run([sys.executable, "-c", "import time; time.sleep(1.15); print('done', end='')"], b"")
            self.assertEqual(result.stdout, b"done")
            rows = [json.loads(path.read_text()) for path in wrapper.broker._receipt_files()]
            self.assertGreaterEqual(sum(row["event_kind"] == "HEARTBEAT" for row in rows), 2)

    def test_heartbeat_scheduler_uses_last_signed_timestamp_not_later_sample(self) -> None:
        schedule = service.HeartbeatScheduler("2026-08-13T12:00:00Z", 1)
        # The initial receipt was signed at 00.999 and encoded as :00.  A later
        # scheduler sample at 01.001 must not postpone the next emission to :02.
        self.assertTrue(schedule.is_due(instant(1.001)))
        schedule.emitted(instant(1.001), "2026-08-13T12:00:01Z")
        self.assertLessEqual(schedule.next_due, instant(2.0))
        self.assertEqual(schedule.hard_deadline, instant(2.0))

    def test_heartbeat_scheduler_duplicate_second_and_jitter_never_skip_bound(self) -> None:
        schedule = service.HeartbeatScheduler("2026-08-13T12:00:00Z", 1)
        observed_signed = []
        for current in (instant(0.001), instant(0.62), instant(1.001), instant(1.83), instant(2.0)):
            if schedule.is_due(current):
                signed = service.timestamp(current)
                schedule.emitted(current, signed)
                observed_signed.append(broker.utc(signed))
        self.assertGreaterEqual(len(observed_signed), 3)
        gaps = [int((right - left).total_seconds()) for left, right in zip(observed_signed, observed_signed[1:])]
        self.assertTrue(all(0 <= gap <= 1 for gap in gaps), gaps)

    def test_heartbeat_scheduler_rejects_poll_after_true_signed_deadline(self) -> None:
        schedule = service.HeartbeatScheduler("2026-08-13T12:00:00Z", 1)
        with self.assertRaisesRegex(service.ServiceError, "escaped"):
            schedule.emitted(instant(2.0), "2026-08-13T12:00:02Z")

    def test_command_stdin_stdout_stderr_are_content_addressed(self) -> None:
        command = [sys.executable, "-c", "import sys; x=sys.stdin.buffer.read(); sys.stdout.buffer.write(x.upper()); sys.stderr.buffer.write(b'warn:'+x)"]
        with self.open() as wrapper:
            result = wrapper.run(command, b"private")
            self.assertEqual(result.stdout, b"PRIVATE")
            self.assertEqual(result.stderr, b"warn:private")
            prepares = [json.loads(path.read_text()) for path in wrapper.broker._receipt_files() if json.loads(path.read_text())["event_kind"] == "PREPARE"]
            self.assertEqual([row["delivery_channel"] for row in prepares], ["subprocess:stdin", "subprocess:stdout", "subprocess:stderr"])
            self.assertEqual([wrapper.broker.store.get(row["payload_sha256"]) for row in prepares], [b"private", b"PRIVATE", b"warn:private"])
            stdout_sink, stderr_sink = io.BytesIO(), io.BytesIO()
            wrapper.deliver_result(result, stdout_sink, stderr_sink)
            self.assertEqual((stdout_sink.getvalue(), stderr_sink.getvalue()), (b"PRIVATE", b"warn:private"))
            prepares = [json.loads(path.read_text()) for path in wrapper.broker._receipt_files() if json.loads(path.read_text())["event_kind"] == "PREPARE"]
            self.assertEqual([row["delivery_channel"] for row in prepares[-2:]], ["caller:stdout", "caller:stderr"])

    def test_empty_stdout_and_stderr_are_still_receipted(self) -> None:
        with self.open() as wrapper:
            wrapper.run([sys.executable, "-c", "pass"], b"")
            prepares = [json.loads(path.read_text()) for path in wrapper.broker._receipt_files() if json.loads(path.read_text())["event_kind"] == "PREPARE"]
            self.assertEqual(len(prepares), 3)
            self.assertTrue(all(row["payload_byte_count"] == 0 for row in prepares))

    def test_final_caller_sink_failure_is_aborted(self) -> None:
        with self.open() as wrapper:
            result = wrapper.run([sys.executable, "-c", "print('captured', end='')"], b"")
            with self.assertRaisesRegex(OSError, "sink unavailable"):
                wrapper.deliver_result(result, FailingSink(), io.BytesIO())
            last = json.loads(wrapper.broker._receipt_files()[-1].read_text())
            self.assertEqual((last["event_kind"], last["delivery_channel"]), ("ABORT", "caller:stdout"))

    def test_durable_key_loader_requires_raw_owner_only_single_link_file(self) -> None:
        loaded = service.load_private_key(self.f.key_path)
        self.assertEqual(loaded.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw), self.f.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))
        self.f.key_path.chmod(0o640)
        with self.assertRaisesRegex(service.ServiceError, "exactly 0600"):
            service.load_private_key(self.f.key_path)
        self.f.key_path.chmod(0o600)
        hardlink = self.f.key_path.with_name("hardlink.key")
        os.link(self.f.key_path, hardlink)
        with self.assertRaisesRegex(service.ServiceError, "exactly one"):
            service.load_private_key(self.f.key_path)

    def test_key_loader_rejects_symlink_and_wrong_length(self) -> None:
        symlink = self.f.key_path.with_name("link.key")
        symlink.symlink_to(self.f.key_path)
        with self.assertRaisesRegex(service.ServiceError, "regular file"):
            service.load_private_key(symlink)
        wrong = self.f.key_path.with_name("wrong.key")
        wrong.write_bytes(b"x" * 31)
        wrong.chmod(0o600)
        with self.assertRaisesRegex(service.ServiceError, "exactly one 32-byte"):
            service.load_private_key(wrong)

    def test_operational_mode_refuses_unset_production_store(self) -> None:
        with self.assertRaisesRegex(service.OperationalRefusal, "not configured"):
            service.BrokerService(self.f.root, self.f.config, self.f.key, acceptance_test=False)
        self.assertFalse((self.f.root / "state.json").exists())

    def test_even_claimed_production_fields_refuse_missing_adapter(self) -> None:
        config = json.loads(json.dumps(self.f.config))
        config["store"].update(production_backend="TEST_CLAIM", production_locator="opaque://claim", retention_acceptance=True)
        with self.assertRaisesRegex(service.OperationalRefusal, "no production.*implementation"):
            service.require_production_store(config)

    def test_cli_acceptance_mode_preserves_streams_and_operational_mode_refuses(self) -> None:
        script = Path(service.__file__)
        base = [sys.executable, str(script), "--root", str(self.f.root), "--config", str(self.f.config_path), "--key", str(self.f.key_path)]
        command = ["--", sys.executable, "-c", "import sys; x=sys.stdin.buffer.read(); sys.stdout.buffer.write(x[::-1]); sys.stderr.buffer.write(b'err')"]
        accepted = subprocess.run(base + ["--acceptance-test"] + command, input=b"abc", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((accepted.returncode, accepted.stdout, accepted.stderr), (0, b"cba", b"err"))
        refused_root = Path(self.f.temp.name) / "refused"
        refused = subprocess.run([sys.executable, str(script), "--root", str(refused_root), "--config", str(self.f.config_path), "--key", str(self.f.key_path)] + command, input=b"do not consume", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(refused.returncode, 78)
        self.assertIn(b"production immutable-store adapter is not configured", refused.stderr)
        self.assertFalse(refused_root.exists())


if __name__ == "__main__":
    unittest.main()
