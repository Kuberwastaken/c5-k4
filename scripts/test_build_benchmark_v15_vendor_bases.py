#!/usr/bin/env python3
"""Focused negative tests for Method v1.5 vendor acquisition."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import build_benchmark_v15_vendor_bases as vendor


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(args, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()


def make_bare(base: Path) -> tuple[Path, str]:
    source = base / "source"
    source.mkdir()
    run("git", "init", "-q", "-b", "main", cwd=source)
    run("git", "config", "user.name", "Fixture", cwd=source)
    run("git", "config", "user.email", "fixture@example.invalid", cwd=source)
    (source / "a.txt").write_text("vendor\n", encoding="utf-8")
    (source / "nested").mkdir()
    (source / "nested/b.txt").write_text("nested vendor\n", encoding="utf-8")
    run("git", "add", "a.txt", "nested/b.txt", cwd=source)
    run("git", "commit", "-q", "-m", "vendor base", cwd=source)
    commit = run("git", "rev-parse", "HEAD", cwd=source)
    bare = base / "vendor.git"
    run("git", "init", "--bare", "-q", "--object-format=sha1", str(bare))
    run(
        "git", "-C", str(bare), "fetch", "--no-tags", "--no-write-fetch-head", "--refmap=",
        str(source), f"{commit}:refs/c5k4-benchmark/v1.5/vendor/fixture",
    )
    return bare, commit


def receipt_for(repo: Path) -> dict:
    audit = vendor.audit_repository(repo, "refs/c5k4-benchmark/v1.5/vendor/fixture")
    value = {
        "schema": vendor.SCHEMA,
        "status": "AUTHENTICATED_IMMUTABLE_SOURCE_CUSTODY",
        "acquired_at_utc": "2026-08-13T00:00:00Z",
        "repository_path": str(repo.resolve()),
        "fresh_repository": True,
        "bare_repository": True,
        "remote": "https://example.invalid/vendor.git",
        "remote_ref": "refs/heads/main",
        "destination_ref": "refs/c5k4-benchmark/v1.5/vendor/fixture",
        "fetch_command": vendor.fetch_command(
            repo, "https://example.invalid/vendor.git", "refs/heads/main",
            "refs/c5k4-benchmark/v1.5/vendor/fixture",
        ),
        "fetch_stdout_sha256": vendor.sha256(b""),
        "fetch_stderr_sha256": vendor.sha256(b""),
        "audit": audit,
        "retry_count": 0,
    }
    value["receipt_sha256"] = vendor.self_digest(value)
    return value


class VendorBaseTests(unittest.TestCase):
    def test_fetch_command_is_one_ref_atomic_and_non_mutating(self) -> None:
        command = vendor.fetch_command(
            Path("/tmp/absent.git"), "https://example.invalid/vendor.git", "refs/heads/main",
            "refs/c5k4-benchmark/v1.5/vendor/u1",
        )
        for flag in ("--atomic", "--no-tags", "--no-write-fetch-head", "--refmap=", "--no-recurse-submodules"):
            self.assertIn(flag, command)
        self.assertEqual(command[-1], "refs/heads/main:refs/c5k4-benchmark/v1.5/vendor/u1")

    def test_audit_and_receipt_bind_exact_commit_tree_and_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, commit = make_bare(Path(tmp))
            receipt = receipt_for(repo)
            vendor.validate_receipt(receipt)
            self.assertEqual(receipt["audit"]["commit"], commit)
            tampered = json.loads(json.dumps(receipt))
            tampered["audit"]["commit"] = "0" * 40
            with self.assertRaisesRegex(vendor.VendorBaseError, "self digest"):
                vendor.validate_receipt(tampered)

    def test_repository_must_be_previously_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "exists"
            existing.mkdir()
            with self.assertRaisesRegex(vendor.VendorBaseError, "previously absent"):
                vendor.acquire(existing, "x", "refs/heads/main", "refs/c5k4-benchmark/v1.5/vendor/u1")

    def test_audit_rejects_alternates_promisor_replace_and_config_tricks(self) -> None:
        mutations = (
            lambda repo: (repo / "objects/info/alternates").write_text("/tmp/foreign\n"),
            lambda repo: (repo / "objects/pack/fake.promisor").touch(),
            lambda repo: run("git", "-C", str(repo), "update-ref", "refs/replace/" + receipt_for(repo)["audit"]["commit"], receipt_for(repo)["audit"]["commit"]),
            lambda repo: run("git", "-C", str(repo), "config", "remote.origin.promisor", "true"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as tmp:
                repo, _ = make_bare(Path(tmp))
                mutate(repo)
                with self.assertRaises(vendor.VendorBaseError):
                    vendor.audit_repository(repo, "refs/c5k4-benchmark/v1.5/vendor/fixture")

    def test_audit_rejects_shallow_and_unexpected_remote_config(self) -> None:
        for name, mutation in (
            ("shallow", lambda repo: (repo / "shallow").write_text("0" * 40 + "\n")),
            ("remote", lambda repo: run("git", "-C", str(repo), "config", "remote.origin.url", "https://example.invalid/x")),
        ):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                repo, _ = make_bare(Path(tmp))
                mutation(repo)
                with self.assertRaises(vendor.VendorBaseError):
                    vendor.audit_repository(repo, "refs/c5k4-benchmark/v1.5/vendor/fixture")


if __name__ == "__main__":
    unittest.main()
