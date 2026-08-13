#!/usr/bin/env python3
"""Focused tests for Method v1.5 source and typed-session ledgers."""

from __future__ import annotations

import base64
import json
from pathlib import Path
import unittest

import jsonschema

import build_benchmark_v15_source_snapshot as snapshot
import classify_benchmark_provenance_v15 as provenance


def jsonl(*rows: object) -> bytes:
    return ("\n".join(json.dumps(row, separators=(",", ":")) for row in rows) + "\n").encode()


class TypedSessionTests(unittest.TestCase):
    def test_private_content_sink_roundtrips_exact_hashed_message_bytes(self) -> None:
        message = "FormalConjectures/GraphFresh.lean and graph_fresh"
        raw = jsonl({
            "type": "response_item",
            "payload": {"type": "message", "role": "user", "content": [
                {"type": "input_text", "text": message}
            ]},
        })
        sink: dict[str, bytes] = {}
        ledger = snapshot.typed_session_ledger(
            raw, "codex", "sessions", "codex/private.jsonl",
            private_content_sink=sink,
        )
        digest = ledger["units"][0]["content_sha256"]
        self.assertEqual(sink, {digest: message.encode()})
        pack = snapshot.private_content_pack(sink)
        self.assertIs(pack["publication_permitted"], False)
        self.assertEqual(base64.b64decode(pack["entries"][0]["content_base64"]), message.encode())
        schema = json.loads((Path(__file__).parents[1] / "schemas/benchmark-private-provenance-content-pack-v1.5.schema.json").read_text())
        jsonschema.validate(pack, schema)

    def test_codex_text_is_semantic_and_undeclared_tool_traffic_fails_closed(self) -> None:
        raw = jsonl(
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "inspect target"}]}},
            {"type": "response_item", "payload": {"type": "function_call", "call_id": "c1", "name": "exec", "arguments": "{\"q\":\"target\"}"}},
            {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c1", "output": "target row"}},
            {"type": "turn_context", "payload": {"summary": "the target was inspected"}},
        )
        units = snapshot.parse_session_exposure_units(raw, "codex", "sessions", "codex/a.jsonl")
        self.assertEqual(
            [row["provenance_class"] for row in units],
            ["SEMANTIC_EXPOSURE", "UNKNOWN", "SEMANTIC_EXPOSURE", "SEMANTIC_EXPOSURE"],
        )
        self.assertEqual(units[0]["delivery_path"], "HUMAN_OR_MODEL")
        self.assertEqual(units[1]["delivery_path"], "UNPROVED")
        self.assertNotIn("target", json.dumps(units))

    def test_forgeable_session_lane_declaration_is_rejected(self) -> None:
        output = "identity-only registry row"
        raw = jsonl(
            {"type": "response_item", "payload": {"type": "function_call", "call_id": "c1", "name": "registry", "arguments": {"mode": "identity"}}},
            {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c1", "output": output}},
        )
        declaration = {
            "schema_version": "c5k4-declared-machine-lane-1.5",
            "declared_at_utc": "2026-08-13T00:00:00Z",
            "interval_close_utc": "2026-08-20T00:00:00Z",
            "source_id": "sessions",
            "session_format": "codex",
            "relative_path": "codex/a.jsonl",
            "outputs": [{
                "call_id": "c1", "tool_name": "registry",
                "output_content_sha256": snapshot.sha256(output.encode()),
                "identity_only": True,
            }],
        }
        with self.assertRaisesRegex(ValueError, "not trusted"):
            snapshot.parse_session_exposure_units(raw, "codex", "sessions", "codex/a.jsonl", declaration)

    def test_malformed_and_unpaired_records_are_unknown(self) -> None:
        raw = b'{"truncated"\n' + jsonl(
            ["not", "object"],
            {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "missing", "output": "x"}},
        )
        units = snapshot.parse_session_exposure_units(raw, "codex", "sessions", "codex/b.jsonl")
        self.assertEqual(len(units), 3)
        self.assertTrue(all(row["provenance_class"] == "UNKNOWN" for row in units))
        self.assertTrue(all(row["delivery_path"] == "UNPROVED" for row in units))

    def test_claude_retains_human_and_assistant_text_and_types_tools(self) -> None:
        raw = jsonl(
            {"type": "user", "message": {"content": [{"type": "text", "text": "question"}]}},
            {"type": "assistant", "message": {"content": [
                {"type": "text", "text": "answer"},
                {"type": "tool_use", "id": "t1", "name": "Read", "input": {"file": "x"}},
            ]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "bytes"}]}},
        )
        units = snapshot.parse_session_exposure_units(raw, "claude", "sessions", "claude/a.jsonl")
        self.assertEqual(
            [row["provenance_class"] for row in units],
            ["SEMANTIC_EXPOSURE", "UNKNOWN", "SEMANTIC_EXPOSURE", "SEMANTIC_EXPOSURE"],
        )

    def test_real_codex_event_and_custom_tool_records_are_retained(self) -> None:
        raw = jsonl(
            {"type": "event_msg", "payload": {"type": "user_message", "message": "human text"}},
            {"type": "event_msg", "payload": {"type": "agent_message", "message": "agent text"}},
            {"type": "response_item", "payload": {"type": "custom_tool_call", "call_id": "c1", "name": "exec", "input": "code"}},
            {"type": "response_item", "payload": {"type": "custom_tool_call_output", "call_id": "c1", "output": [{"type": "input_text", "text": "tool bytes"}]}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {}}},
        )
        units = snapshot.parse_session_exposure_units(raw, "codex", "sessions", "real.jsonl")
        self.assertEqual(len(units), 5)
        self.assertEqual([row["provenance_class"] for row in units], [
            "SEMANTIC_EXPOSURE", "SEMANTIC_EXPOSURE", "UNKNOWN",
            "SEMANTIC_EXPOSURE", "UNKNOWN",
        ])
        self.assertEqual(units[3]["role"], "codex-tool-output")

    def test_parser_units_compose_with_general_classifier(self) -> None:
        raw = jsonl(
            {"type": "response_item", "payload": {"type": "message", "role": "user", "content": "question"}},
            {"type": "response_item", "payload": {"type": "custom_tool_call", "call_id": "c", "name": "exec", "input": "x"}},
            {"type": "response_item", "payload": {"type": "custom_tool_call_output", "call_id": "c", "output": "answer"}},
        )
        units = snapshot.parse_session_exposure_units(raw, "codex", "sessions", "e2e.jsonl")
        classified = provenance.classify_units(units, [])
        self.assertEqual([row["provenance_class"] for row in classified], [
            provenance.SEMANTIC_EXPOSURE, provenance.UNKNOWN, provenance.SEMANTIC_EXPOSURE,
        ])

    def test_ledger_has_exact_counts_and_no_alias_join(self) -> None:
        raw = jsonl({"type": "response_item", "payload": {"type": "message", "role": "assistant", "content": "hello"}})
        ledger = snapshot.typed_session_ledger(
            raw, "codex", "sessions", "a.jsonl",
            ledger_id="L1", created_at_utc="2026-08-13T22:00:00Z",
            source_snapshot_sha256="1" * 64, ontology_sha256="2" * 64,
        )
        self.assertEqual(ledger["schema"], snapshot.SESSION_LEDGER_SCHEMA)
        self.assertEqual(sum(ledger["counts"].values()), len(ledger["units"]))
        self.assertFalse(ledger["fail_closed"])
        self.assertNotIn("aliases", ledger)
        schema = json.loads((Path(__file__).parents[1] / "schemas/benchmark-provenance-ledger-v1.5.schema.json").read_text())
        jsonschema.validate(ledger, schema)


class SourceIntervalTests(unittest.TestCase):
    def test_source_snapshot_is_complete_sorted_and_content_addressed(self) -> None:
        value = snapshot.build_source_snapshot(
            snapshot_id="S", source_id="sessions", source_kind="SESSION_ARCHIVE",
            captured_at_utc="2026-08-20T00:00:00Z",
            lower_bound_utc="2026-08-13T00:00:00Z", upper_bound_utc="2026-08-20T00:00:00Z",
            producer_id="capture-v1", executable_sha256="1" * 64,
            invocation_contract_sha256="2" * 64,
            artifacts=[
                {"locator": "z", "content_sha256": "3" * 64, "byte_count": 2},
                {"locator": "a", "content_sha256": "4" * 64, "byte_count": 1},
            ],
        )
        self.assertEqual([row["locator"] for row in value["artifacts"]], ["a", "z"])
        self.assertEqual(value["snapshot_sha256"], snapshot.content_address(value, "snapshot_sha256"))
        self.assertEqual(value["coverage"]["gaps"], [])
        schema = json.loads((Path(__file__).parents[1] / "schemas/benchmark-source-snapshot-v1.5.schema.json").read_text())
        jsonschema.validate(value, schema)

    def endpoint(self, at: str, include_exports: bool = True) -> dict:
        sources = [{"source_id": "repo:x", "kind": "git_user_delta", "corpus_sha256": "a" * 64,
                    "complete": True, "failure": None}]
        if include_exports:
            for kind in sorted(snapshot.EXPORT_KINDS):
                sources.append({
                    "source_id": "export:" + kind.lower(), "kind": "platform_export_snapshot",
                    "export_kind": kind, "corpus_sha256": snapshot.sha256(kind.encode()),
                    "complete": True, "failure": None,
                })
        result = {"acquired_at_utc": at, "complete": True, "corpus_sha256": "e" * 64,
                  "sources": sources}
        result["snapshot_sha256"] = snapshot.content_address(result, "snapshot_sha256")
        return result

    def test_interval_accepts_first_passing_checkpoint_and_is_target_blind(self) -> None:
        value = snapshot.build_interval_ledger_input(
            self.endpoint("2026-08-13T00:00:00Z"), self.endpoint("2026-08-20T00:00:00Z"),
            checkpoint_identity="weekly-1", quota_gate_passed=True,
            hard_horizon_utc="2027-08-13T00:00:00Z",
        )
        self.assertTrue(value["complete"])
        self.assertFalse(value["candidate_semantics_inspected"])
        self.assertFalse(value["target_identity_joined"])

    def test_interval_rejects_early_failed_gate_or_missing_platform_export(self) -> None:
        with self.assertRaisesRegex(ValueError, "quota-gate pass"):
            snapshot.build_interval_ledger_input(
                self.endpoint("2026-08-13T00:00:00Z"), self.endpoint("2026-08-20T00:00:00Z"),
                checkpoint_identity="weekly-1", quota_gate_passed=False,
                hard_horizon_utc="2027-08-13T00:00:00Z",
            )

    def test_interval_rejects_incomplete_null_digest_and_unrecognized_source(self) -> None:
        valid = self.endpoint("2026-08-13T00:00:00Z")
        end = self.endpoint("2026-08-20T00:00:00Z")
        for mutation, message in (
            (lambda x: x.update(complete=False), "not complete"),
            (lambda x: x.update(snapshot_sha256=None), "snapshot_sha256"),
            (lambda x: x["sources"][0].update(kind="mystery"), "unrecognized kind"),
            (lambda x: x["sources"][0].update(complete=False), "is incomplete"),
        ):
            broken = json.loads(json.dumps(end))
            mutation(broken)
            if broken.get("snapshot_sha256") is not None:
                broken["snapshot_sha256"] = snapshot.content_address(broken, "snapshot_sha256")
            with self.assertRaisesRegex(ValueError, message):
                snapshot.build_interval_ledger_input(
                    valid, broken, checkpoint_identity="weekly-1", quota_gate_passed=True,
                    hard_horizon_utc="2027-08-13T00:00:00Z",
                )
        with self.assertRaisesRegex(ValueError, "release/issue/PR"):
            snapshot.build_interval_ledger_input(
                self.endpoint("2026-08-13T00:00:00Z", False), self.endpoint("2026-08-20T00:00:00Z", False),
                checkpoint_identity="weekly-1", quota_gate_passed=True,
                hard_horizon_utc="2027-08-13T00:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
