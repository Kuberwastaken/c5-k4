#!/usr/bin/env python3
"""Adversarial tests for the private Method v1.5 identity/exposure join."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft7Validator


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_benchmark_v15_identity_hits as hits  # noqa: E402
import build_benchmark_v15_source_snapshot as source  # noqa: E402


class IdentityHitTests(unittest.TestCase):
    def target(self) -> dict:
        return {
            "cluster_id": "future-graph-fresh",
            "path": "FormalConjectures/GraphFresh.lean",
            "identity_sha256": "1" * 64,
            "module_blob_sha256": "2" * 64,
            "declarations": [{
                "name": "graph_fresh",
                "statement_header_sha256": "3" * 64,
            }],
        }

    def session_ledger(self, message: str, provenance_class: str = "SEMANTIC_EXPOSURE") -> tuple[dict, bytes]:
        record = {
            "type": "response_item",
            "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": message}]},
        }
        raw_session = (json.dumps(record) + "\n").encode()
        ledger = source.typed_session_ledger(
            raw_session, "codex", "codex-local-sessions", "2026/08/session.jsonl",
            ledger_id="real-session-style", created_at_utc="2026-08-17T00:18:00Z",
            source_snapshot_sha256="4" * 64, ontology_sha256="5" * 64,
        )
        unit = ledger["units"][0]
        unit["provenance_class"] = provenance_class
        ledger["counts"] = {name: 0 for name in sorted(source.EXPOSURE_CLASSES)}
        ledger["counts"][provenance_class] = 1
        ledger["fail_closed"] = provenance_class == "UNKNOWN"
        ledger["status"] = "CLASSIFIED_FAIL_CLOSED" if ledger["fail_closed"] else "CLASSIFIED_COMPLETE"
        ledger["ledger_sha256"] = source.content_address(ledger, "ledger_sha256")
        return ledger, message.encode()

    def test_real_session_hashed_content_exact_path_hit_and_strict_schema(self) -> None:
        message = "Please inspect `FormalConjectures/GraphFresh.lean` and graph_fresh before selection."
        ledger, content = self.session_ledger(message)
        digest = ledger["units"][0]["content_sha256"]
        output = hits.build([self.target()], [ledger], {digest: content})
        self.assertEqual(output["binding_count"], 1)
        self.assertEqual(
            output["clusters"][0]["bindings"][0]["matched_alias_kinds"],
            ["DECLARATION_NAME", "MODULE_PATH"],
        )
        self.assertNotIn(message, json.dumps(output))
        self.assertNotIn(self.target()["path"], json.dumps(output))
        schema = json.loads((ROOT / "schemas/benchmark-private-identity-hits-v1.5.schema.json").read_text())
        errors = list(Draft7Validator(schema).iter_errors(output))
        self.assertEqual(errors, [], [error.message for error in errors])

    def test_content_digest_mismatch_fails_closed(self) -> None:
        ledger, content = self.session_ledger("graph_fresh was discussed")
        digest = ledger["units"][0]["content_sha256"]
        with self.assertRaisesRegex(hits.IdentityHitError, "digest mismatch"):
            hits.build([self.target()], [ledger], {digest: content + b"tampered"})

    def test_missing_content_fails_closed(self) -> None:
        ledger, _ = self.session_ledger("graph_fresh was discussed")
        with self.assertRaisesRegex(hits.IdentityHitError, "unavailable"):
            hits.build([self.target()], [ledger], {})

    def test_false_substrings_do_not_match(self) -> None:
        message = (
            "graph_fresh_extra and xFormalConjectures/GraphFresh.lean.backup "
            "are unrelated aliases"
        )
        ledger, content = self.session_ledger(message)
        digest = ledger["units"][0]["content_sha256"]
        output = hits.build([self.target()], [ledger], {digest: content})
        self.assertEqual(output["binding_count"], 0)
        self.assertEqual(output["clusters"], [])

    def test_unknown_exact_name_emits_unknown_binding(self) -> None:
        ledger, content = self.session_ledger("The name graph_fresh is present.", "UNKNOWN")
        digest = ledger["units"][0]["content_sha256"]
        output = hits.build([self.target()], [ledger], {digest: content})
        self.assertEqual(output["clusters"][0]["bindings"][0]["provenance_class"], "UNKNOWN")
        self.assertEqual(hits.exclusion_reasons(self.target(), output), {"UNKNOWN_EXPOSURE"})

    def test_content_pack_is_strict_and_content_addressed(self) -> None:
        raw = b"graph_fresh"
        digest = hits.sha256(raw)
        import base64
        pack = {"schema": hits.CONTENT_PACK_SCHEMA, "publication_permitted": False, "entries": [{
            "content_sha256": digest, "content_base64": base64.b64encode(raw).decode(),
        }]}
        self.assertEqual(hits.load_content_pack(pack), {digest: raw})
        schema = json.loads((ROOT / "schemas/benchmark-private-provenance-content-pack-v1.5.schema.json").read_text())
        errors = list(Draft7Validator(schema).iter_errors(pack))
        self.assertEqual(errors, [], [error.message for error in errors])
        pack["extra"] = True
        with self.assertRaisesRegex(hits.IdentityHitError, "non-strict"):
            hits.load_content_pack(pack)


if __name__ == "__main__":
    unittest.main()
