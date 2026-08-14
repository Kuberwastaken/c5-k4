#!/usr/bin/env python3
"""Unit entry point for the exact P1T publication validator."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts/verify_benchmark_v15_p1t_publication.py"


class ValidatorSourceContractTests(unittest.TestCase):
    def test_validator_freezes_exact_git_and_topology_checks(self) -> None:
        raw = VALIDATOR.read_text(encoding="utf-8")
        for required in (
            'OID = re.compile(r"^[0-9a-f]{40}$")',
            'git("diff-tree", "--no-commit-id", "--name-only", "-r", commit)',
            'if len(parents) != 1:',
            'if value["p1a_commit"] != parents[0]',
            'hashlib.sha256(p1a_raw).hexdigest()',
            'checkout P1T bytes differ from exact commit bytes',
        ):
            self.assertIn(required, raw)
        self.assertNotIn("shell=True", raw)


if __name__ == "__main__":
    unittest.main()
