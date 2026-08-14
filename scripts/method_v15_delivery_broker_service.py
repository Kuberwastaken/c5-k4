#!/usr/bin/env python3
"""PRE-P1 one-shot service boundary for the controlled VPS delivery broker.

The only currently permitted mode is ``--acceptance-test``.  An operational
invocation is refused until a production immutable-store adapter is configured
and accepted; the committed broker config intentionally makes that impossible.
This wrapper does not intercept stock Codex, Claude, shells, browsers, or Mac
traffic.  It captures only commands explicitly launched through this program.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import errno
import fcntl
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
from typing import BinaryIO, Callable, Sequence

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import method_v15_delivery_broker as broker


class ServiceError(RuntimeError):
    """The controlled service boundary cannot safely proceed."""


class OperationalRefusal(ServiceError):
    """Production prerequisites are deliberately absent."""


def timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_private_key(path: Path) -> Ed25519PrivateKey:
    """Load a raw Ed25519 seed from a non-linked, owner-only regular file."""
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise ServiceError("signing key file is missing") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ServiceError("signing key must be a regular file, not a link or device")
    if metadata.st_uid != os.getuid():
        raise ServiceError("signing key is not owned by the service user")
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise ServiceError("signing key permissions must be exactly 0600")
    if metadata.st_nlink != 1:
        raise ServiceError("signing key must have exactly one filesystem link")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
            raise ServiceError("signing key changed while opening")
        raw = os.read(descriptor, 33)
    finally:
        os.close(descriptor)
    if len(raw) != 32:
        raise ServiceError("signing key must contain exactly one 32-byte Ed25519 seed")
    return Ed25519PrivateKey.from_private_bytes(raw)


class SingleWriterLock:
    """Nonblocking process-scoped exclusive lock held for the service lifetime."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        self.descriptor = os.open(path, flags, 0o600)
        os.fchmod(self.descriptor, 0o600)
        try:
            fcntl.flock(self.descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(self.descriptor)
            self.descriptor = -1
            if exc.errno in {errno.EACCES, errno.EAGAIN}:
                raise ServiceError("another delivery-broker writer is active") from exc
            raise

    def close(self) -> None:
        if self.descriptor >= 0:
            fcntl.flock(self.descriptor, fcntl.LOCK_UN)
            os.close(self.descriptor)
            self.descriptor = -1

    def __enter__(self) -> "SingleWriterLock":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def require_production_store(config: dict[str, object]) -> None:
    store = config.get("store")
    if not isinstance(store, dict):
        raise OperationalRefusal("production immutable-store configuration is missing")
    if store.get("production_backend") is None or store.get("production_locator") is None:
        raise OperationalRefusal("production immutable-store adapter is not configured")
    if store.get("retention_acceptance") is not True:
        raise OperationalRefusal("production immutable-store retention is not accepted")
    raise OperationalRefusal("no production immutable-store adapter implementation exists")


class BrokerService:
    """Exclusive one-shot command wrapper around :class:`DeliveryBroker`."""

    def __init__(
        self,
        root: Path,
        config: dict[str, object],
        private_key: Ed25519PrivateKey,
        *,
        acceptance_test: bool,
        clock: Callable[[], datetime] | None = None,
        sleep: Callable[[float], None] | None = None,
    ):
        if not acceptance_test:
            require_production_store(config)
        self.root = root
        self.config = config
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.sleep = sleep or time.sleep
        self.writer_lock = SingleWriterLock(root / "service-writer.lock")
        try:
            self.broker = broker.DeliveryBroker(root, config, private_key)
        except Exception:
            self.writer_lock.close()
            raise

    def close(self) -> None:
        self.writer_lock.close()

    def __enter__(self) -> "BrokerService":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _now(self) -> str:
        return timestamp(self.clock())

    def _heartbeat(self) -> None:
        self.broker.heartbeat(self._now())

    def _capture_return(self, raw: bytes, channel: str) -> bytes:
        now = self._now()
        transaction = self.broker.prepare(raw, channel, now)
        self.broker.start(transaction, now)
        return self.broker.finish(transaction, "DELIVER", now)

    def _deliver_captured(self, raw: bytes, channel: str, sink: BinaryIO) -> None:
        now = self._now()
        transaction = self.broker.prepare(raw, channel, now)
        self.broker.start(transaction, now)
        try:
            sink.write(raw)
            sink.flush()
        except Exception:
            self.broker.finish(transaction, "ABORT", self._now())
            raise
        self.broker.finish(transaction, "DELIVER", self._now())

    def deliver_result(self, completed: subprocess.CompletedProcess[bytes], stdout: BinaryIO, stderr: BinaryIO) -> None:
        """Deliver captured child streams through terminal receipt boundaries."""
        self._deliver_captured(completed.stdout, "caller:stdout", stdout)
        self._deliver_captured(completed.stderr, "caller:stderr", stderr)

    def run(self, command: Sequence[str], stdin_bytes: bytes) -> subprocess.CompletedProcess[bytes]:
        if not command:
            raise ServiceError("wrapped command must be nonempty")
        self._heartbeat()
        now = self._now()
        stdin_transaction = self.broker.prepare(stdin_bytes, "subprocess:stdin", now)
        self.broker.start(stdin_transaction, now)
        with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
            try:
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout_file, stderr=stderr_file)
            except Exception:
                self.broker._lock("command creation failed after START")
                raise
            try:
                assert process.stdin is not None
                process.stdin.write(stdin_bytes)
                process.stdin.close()
                self.broker.finish(stdin_transaction, "DELIVER", self._now())
            except Exception:
                process.kill()
                process.wait()
                # Partial child consumption is unknowable; make the state sticky-invalid.
                self.broker._lock("indeterminate subprocess stdin delivery")
                raise

            heartbeat_seconds = int(self.config["heartbeat_interval_seconds"])
            next_heartbeat = self.clock().timestamp() + max(1, heartbeat_seconds // 2)
            try:
                while process.poll() is None:
                    current = self.clock()
                    if current.timestamp() >= next_heartbeat:
                        self.broker.heartbeat(timestamp(current))
                        next_heartbeat = current.timestamp() + max(1, heartbeat_seconds // 2)
                    self.sleep(min(0.05, max(0.01, heartbeat_seconds / 4)))
            except Exception:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                self.broker._lock("command supervision failed")
                raise
            stdout_file.seek(0)
            stderr_file.seek(0)
            captured_stdout = self._capture_return(stdout_file.read(), "subprocess:stdout")
            captured_stderr = self._capture_return(stderr_file.read(), "subprocess:stderr")
            return subprocess.CompletedProcess(list(command), process.returncode, captured_stdout, captured_stderr)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--acceptance-test", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    try:
        if not args.acceptance_test:
            require_production_store(config)
        key = load_private_key(args.key)
        stdin_bytes = sys.stdin.buffer.read()
        with BrokerService(args.root, config, key, acceptance_test=args.acceptance_test) as service:
            completed = service.run(args.command, stdin_bytes)
            service.deliver_result(completed, sys.stdout.buffer, sys.stderr.buffer)
    except (ServiceError, broker.BrokerError) as exc:
        print(f"PRE_P1_DELIVERY_REFUSED: {exc}", file=sys.stderr)
        return 78
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
