#!/usr/bin/env python3
"""Source-closure checks for the strict P1R publication validator."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts/verify_benchmark_v15_p1r_publication.py"
SPEC = importlib.util.spec_from_file_location("p1r_publication", VALIDATOR)
assert SPEC and SPEC.loader
P = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(P)


class ValidatorContractTests(unittest.TestCase):
    def test_exact_draft_topology_and_no_activation_claim_are_enforced(self) -> None:
        raw = VALIDATOR.read_text(encoding="utf-8")
        for fragment in (
            'OID = re.compile(r"^[0-9a-f]{40}$")', "if len(parents) != 1:",
            '!= [P1R_PATH]', '"p1r_is_activation_boundary": False',
            '"full_exact_c_replay_required": True', "hashlib.sha256(p1t_raw).hexdigest()",
            "checkout P1R bytes differ from exact commit bytes",
        ):
            self.assertIn(fragment, raw)
        self.assertNotIn("shell=True", raw)


class ExactTopologyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.git("init", "-q", "-b", "method-v1.5-p1r"); self.git("config", "user.name", "P1R Test"); self.git("config", "user.email", "p1r@example.invalid")
        p1t = {"artifact_kind": "P1T", "protocol_version": "1.5"}
        p1t_raw = self.write(P.P1T_PATH, p1t); self.git("add", "-A"); self.git("commit", "-qm", "P1T"); self.p1t = self.git("rev-parse", "HEAD")
        p1r = {
            "schema_version": "c5k4-method-v1.5-p1r-1.0", "artifact_kind": "P1R",
            "status": "NONAUTHORITATIVE_DRAFT_AWAITING_FULL_EXACT_C_REPLAY", "protocol_version": "1.5",
            "p1t": {"path": P.P1T_PATH, "sha256": hashlib.sha256(p1t_raw).hexdigest()}, "p1t_commit": self.p1t,
            "observation": {"p1t": {"ref": "refs/heads/method-v1.5-p1", "commit": self.p1t}},
            "activation_policy": {"structural_draft_only": True, "p1r_is_activation_boundary": False, "p1t_alone_is_activation_boundary": False, "full_exact_c_replay_required": True, "p1r_parent_must_be_exact_p1t": True, "allowed_p1r_changed_paths": [P.P1R_PATH], "public_p1r_ref_required": True},
        }
        self.write(P.P1R_PATH, p1r); self.git("add", "-A"); self.git("commit", "-qm", "P1R"); self.p1r = self.git("rev-parse", "HEAD")
        self.old_root = P.ROOT; P.ROOT = self.root

    def tearDown(self) -> None:
        P.ROOT = self.old_root; self.tmp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

    def write(self, path: str, value: dict) -> bytes:
        raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(); destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(raw); return raw

    def test_exact_nonauthoritative_one_path_draft_accepts(self) -> None:
        P.validate(self.p1r)

    def test_extra_path_or_activation_claim_rejected(self) -> None:
        (self.root / "extra").write_text("x", encoding="utf-8"); self.git("add", "-A"); self.git("commit", "-qm", "extra")
        with self.assertRaisesRegex(P.ObserverError, "canonical P1R path"):
            P.validate(self.git("rev-parse", "HEAD"))
        value = json.loads((self.root / P.P1R_PATH).read_text()); value["activation_policy"]["p1r_is_activation_boundary"] = True
        self.git("reset", "--hard", "-q", self.p1t)
        self.write(P.P1R_PATH, value); self.git("add", "-A"); self.git("commit", "-qm", "false activation")
        with self.assertRaisesRegex(P.ObserverError, "falsely claims activation"):
            P.validate(self.git("rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
