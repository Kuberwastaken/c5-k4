#!/usr/bin/env python3
"""Contract tests for the reusable scientific-shard runner."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "c5k4_scientific_shard_runner", HERE / "run_scientific_shard_campaign.py"
)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)
COMMIT = "a" * 40
DIGEST = "b" * 64


def manifest(command: list[str], *, stop: int = 3) -> dict[str, object]:
    return {
        "schema": RUNNER.MANIFEST_SCHEMA,
        "campaign_id": "unit-campaign",
        "campaign_commit": COMMIT,
        "command": command,
        "wall_seconds": 1,
        "shards": [{
            "shard_id": "s0",
            "range_start": 0,
            "range_stop": stop,
            "domain_sha256": DIGEST,
            "args": ["worker-arg"],
        }],
    }


class ShardRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def worker(self, body: str) -> list[str]:
        path = self.root / "worker.py"
        path.write_text(body, encoding="utf-8")
        return [sys.executable, str(path)]

    def run_one(self, value: dict[str, object], name: str = "result") -> dict[str, object]:
        path = self.root / "manifest.json"
        path.write_bytes(RUNNER.canonical_bytes(value))
        frozen = RUNNER.load_manifest(path, COMMIT)
        return RUNNER.execute(frozen, "s0", self.root / name)

    def test_exact_exhaustion_requires_full_bound_attestation(self) -> None:
        command = self.worker(
            """import json, os
from pathlib import Path
value = {
  'schema': 'c5k4-scientific-worker-terminal-1.0',
  'campaign_id': os.environ['C5K4_CAMPAIGN_ID'],
  'campaign_commit': os.environ['C5K4_CAMPAIGN_COMMIT'],
  'shard_id': os.environ['C5K4_SHARD_ID'],
  'range_start': int(os.environ['C5K4_SHARD_START']),
  'range_stop': int(os.environ['C5K4_SHARD_STOP']),
  'domain_sha256': os.environ['C5K4_SHARD_DOMAIN_SHA256'],
  'states_scanned': int(os.environ['C5K4_SHARD_STOP']) - int(os.environ['C5K4_SHARD_START']),
  'terminal_reason': 'DOMAIN_EXHAUSTED',
}
path = Path(os.environ['C5K4_WORKER_OUTPUT']) / 'terminal.json'
path.write_text(json.dumps(value, sort_keys=True, separators=(',', ':')) + '\\n')
"""
        )
        terminal = self.run_one(manifest(command))
        self.assertEqual(terminal["terminal_reason"], "DOMAIN_EXHAUSTED")
        self.assertEqual(terminal["states_scanned"], 3)
        self.assertFalse(terminal["timed_out"])

    def test_zero_exit_without_attestation_is_not_completion(self) -> None:
        terminal = self.run_one(manifest(self.worker("pass\n")))
        self.assertEqual(terminal["terminal_reason"], "WORKER_INCOMPLETE")
        self.assertIsNone(terminal["states_scanned"])

    def test_partial_exhaustion_claim_is_rejected(self) -> None:
        command = self.worker(
            """import json, os
from pathlib import Path
value = {
  'schema': 'c5k4-scientific-worker-terminal-1.0',
  'campaign_id': os.environ['C5K4_CAMPAIGN_ID'],
  'campaign_commit': os.environ['C5K4_CAMPAIGN_COMMIT'],
  'shard_id': os.environ['C5K4_SHARD_ID'],
  'range_start': 0, 'range_stop': 3,
  'domain_sha256': os.environ['C5K4_SHARD_DOMAIN_SHA256'],
  'states_scanned': 2,
  'terminal_reason': 'DOMAIN_EXHAUSTED',
}
Path(os.environ['C5K4_WORKER_OUTPUT'], 'terminal.json').write_text(
  json.dumps(value, sort_keys=True, separators=(',', ':')) + '\\n')
"""
        )
        terminal = self.run_one(manifest(command))
        self.assertEqual(terminal["terminal_reason"], "INVALID_WORKER_ATTESTATION")

    def test_deadline_is_runner_owned_prefix_even_if_worker_ignores_term(self) -> None:
        command = self.worker(
            "import signal,time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\ntime.sleep(30)\n"
        )
        terminal = self.run_one(manifest(command))
        self.assertEqual(terminal["terminal_reason"], "DEADLINE_PREFIX")
        self.assertTrue(terminal["timed_out"])

    def test_manifest_rejects_overlapping_shards(self) -> None:
        value = manifest([sys.executable, "worker.py"])
        value["shards"].append({
            "shard_id": "s1", "range_start": 2, "range_stop": 4,
            "domain_sha256": "c" * 64, "args": ["x"],
        })
        path = self.root / "overlap.json"
        path.write_bytes(RUNNER.canonical_bytes(value))
        with self.assertRaisesRegex(RUNNER.ContractError, "overlap"):
            RUNNER.load_manifest(path, COMMIT)

    def test_campaign_exhaustion_requires_every_expected_shard(self) -> None:
        value = manifest([sys.executable, "worker.py"])
        frozen = dict(value)
        frozen["command"] = list(value["command"])
        frozen["shards"] = [dict(value["shards"][0])]
        evidence = self.root / "evidence"
        evidence.mkdir()
        shard = frozen["shards"][0]
        terminal = RUNNER._runner_terminal(
            frozen, shard, reason="DOMAIN_EXHAUSTED", worker_returncode=0,
            timed_out=False, wall_milliseconds=10, states_scanned=3, detail="",
        )
        artifact = evidence / "artifact-s0"
        artifact.mkdir()
        (artifact / "runner-terminal.json").write_bytes(RUNNER.canonical_bytes(terminal))
        index = RUNNER.aggregate(frozen, evidence, self.root / "index")
        self.assertEqual(index["campaign_terminal_reason"], "DOMAIN_EXHAUSTED")

        frozen["shards"].append({
            "shard_id": "s1", "range_start": 3, "range_stop": 6,
            "domain_sha256": "c" * 64, "args": [],
        })
        incomplete = RUNNER.aggregate(frozen, evidence, self.root / "index-incomplete")
        self.assertEqual(incomplete["campaign_terminal_reason"], "INCOMPLETE_EVIDENCE")
        self.assertEqual(incomplete["missing_shards"], ["s1"])

    def test_prepare_path_cannot_escape_repository(self) -> None:
        outside = self.root.parent / "outside-scientific-manifest.json"
        outside.write_text("{}", encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        with self.assertRaisesRegex(RUNNER.ContractError, "escapes"):
            RUNNER._inside_repository("../outside-scientific-manifest.json", self.root)


if __name__ == "__main__":
    unittest.main()
