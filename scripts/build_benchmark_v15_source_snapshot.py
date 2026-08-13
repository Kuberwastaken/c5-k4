#!/usr/bin/env python3
"""Build target-blind Method v1.5 source-interval and session ledgers.

This module deliberately does not know a registry alias.  It captures the
complete P1-to-preselection source interval and assigns source units an origin
and an exposure disposition.  A later, separately frozen identity join may
decide whether a unit bears a target identity.

The hardened filesystem and Git snapshot primitives are inherited from v1.4;
v1.5 adds interval chronology, export coverage, and typed session parsing.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterator

import build_benchmark_v14_source_snapshot as v14


SCHEMA = "c5k4-source-interval-ledger-input-1.5"
SOURCE_SNAPSHOT_SCHEMA = "c5k4-method-v1.5-source-snapshot-1.0"
SESSION_LEDGER_SCHEMA = "c5k4-method-v1.5-provenance-ledger-1.0"
EXPOSURE_CLASSES = {
    "SEMANTIC_EXPOSURE",
    "MACHINE_REGISTRY_CONTACT",
    "IMMUTABLE_SOURCE_CUSTODY",
    "UNKNOWN",
}
ORIGIN_CLASSES = {
    "USER",
    "ASSISTANT",
    "TOOL_CALL",
    "TOOL_OUTPUT",
    "SESSION_METADATA",
    "UNPARSEABLE",
}
EXPORT_KINDS = {"RELEASE", "ISSUE", "PULL_REQUEST"}
SOURCE_KINDS = {
    "GIT_REPOSITORY", "SESSION_ARCHIVE", "CHAT_ARCHIVE", "RELEASE_EXPORT",
    "ISSUE_PR_EXPORT", "GENERATED_ARTIFACT",
}
ENDPOINT_SOURCE_KINDS = {
    "git_history", "git_sessions", "git_user_delta", "tree",
    "release_metadata_snapshot", "platform_export_snapshot",
}


canonical_json = v14.canonical_json
pretty_json = v14.pretty_json
sha256 = v14.sha256
content_address = v14.content_address


def _utc(value: str, field: str) -> dt.datetime:
    if not isinstance(value, str) or not v14.RFC3339_UTC.fullmatch(value):
        raise ValueError(f"{field} must be whole-second RFC3339 UTC")
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _text_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    values: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") in {"text", "input_text", "output_text"} and isinstance(block.get("text"), str):
            values.append(block["text"])
    return "\n".join(values)


def _unit(
    source_id: str,
    relative_path: str,
    line_number: int,
    record_kind: str,
    origin_class: str,
    exposure_class: str,
    raw: bytes,
    *,
    session_format: str,
    call_id: str | None = None,
    tool_name: str | None = None,
    reason: str,
) -> dict[str, Any]:
    if origin_class not in ORIGIN_CLASSES:
        raise ValueError(f"unknown origin_class {origin_class!r}")
    if exposure_class not in EXPOSURE_CLASSES:
        raise ValueError(f"unknown exposure_class {exposure_class!r}")
    delivery_path = {
        "USER": "HUMAN_OR_MODEL",
        "ASSISTANT": "HUMAN_OR_MODEL",
        "TOOL_CALL": "UNPROVED",
        "TOOL_OUTPUT": "HUMAN_OR_MODEL" if exposure_class == "SEMANTIC_EXPOSURE" else "UNPROVED",
        "SESSION_METADATA": "UNPROVED",
        "UNPARSEABLE": "UNPROVED",
    }[origin_class]
    role = {
        "USER": "user-turn",
        "ASSISTANT": "assistant-turn",
        "TOOL_CALL": f"{session_format}-tool-call",
        "TOOL_OUTPUT": f"{session_format}-tool-output",
        "SESSION_METADATA": "session-metadata",
        "UNPARSEABLE": "unparseable-session-record",
    }[origin_class]
    row: dict[str, Any] = {
        "source_id": source_id,
        "source_kind": "git_sessions",
        "locator": f"{relative_path}:{line_number}",
        "role": role,
        "content_sha256": sha256(raw),
        "content_schema": f"{session_format}-session-{record_kind}-1.0",
        "provenance_class": exposure_class,
        "classification_reason": reason,
        "delivery_path": delivery_path,
        "producer_proof_sha256": None,
    }
    row["unit_id"] = content_address(row, "unit_id")
    return row


def parse_session_exposure_units(
    raw: bytes,
    fmt: str,
    source_id: str,
    relative_path: str,
    machine_lane_declaration: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Parse one immutable transcript without performing a target alias join."""

    if fmt not in {"codex", "claude"}:
        raise ValueError(f"unknown session format: {fmt}")
    # Session tool output has already been delivered into an interactive
    # transcript.  A sidecar declaration can be authored after the fact and
    # cannot prove otherwise, so it is never an exemption mechanism.
    if machine_lane_declaration is not None:
        raise ValueError("session machine-lane declarations are not trusted provenance proofs")

    def make_unit(
        line_number: int, record_kind: str, origin_class: str,
        exposure_class: str, content: bytes, *, reason: str,
        call_id: str | None = None, tool_name: str | None = None,
    ) -> dict[str, Any]:
        return _unit(
            source_id, relative_path, line_number, record_kind, origin_class,
            exposure_class, content, session_format=fmt, call_id=call_id,
            tool_name=tool_name, reason=reason,
        )
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError:
        return [make_unit(1, "malformed-session", "UNPARSEABLE", "UNKNOWN", raw,
                          reason="SESSION_NOT_UTF8")]

    calls: dict[str, str] = {}
    units: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        line_raw = line.encode("utf-8")
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            units.append(make_unit(line_number, "malformed-json", "UNPARSEABLE", "UNKNOWN", line_raw,
                                   reason="MALFORMED_OR_TRUNCATED_JSON"))
            continue
        if not isinstance(row, dict):
            units.append(make_unit(line_number, "non-object-json", "UNPARSEABLE", "UNKNOWN", line_raw,
                                   reason="NON_OBJECT_SESSION_RECORD"))
            continue

        if fmt == "codex":
            payload = row.get("payload")
            if row.get("type") == "response_item" and isinstance(payload, dict):
                kind = payload.get("type")
                if kind in {"message", "agent_message"}:
                    value = _text_content(payload.get("content"))
                    if value:
                        role = payload.get("role", "assistant")
                        origin = "USER" if role == "user" else "ASSISTANT" if role in {"assistant", "assistant-agent"} else "SESSION_METADATA"
                        exposure = "SEMANTIC_EXPOSURE" if origin in {"USER", "ASSISTANT"} else "UNKNOWN"
                        units.append(make_unit(line_number, "message", origin, exposure,
                                               value.encode("utf-8"), reason="RETAINED_NATURAL_LANGUAGE" if exposure == "SEMANTIC_EXPOSURE" else "UNCLASSIFIED_MESSAGE_ROLE"))
                    else:
                        units.append(make_unit(line_number, "empty-message", "SESSION_METADATA", "UNKNOWN", line_raw,
                                               reason="MESSAGE_WITHOUT_TEXT"))
                elif kind in {"function_call", "custom_tool_call"}:
                    call_id, tool_name = payload.get("call_id"), payload.get("name")
                    arguments = payload.get("arguments") if kind == "function_call" else payload.get("input")
                    if not isinstance(call_id, str) or not isinstance(tool_name, str):
                        units.append(make_unit(line_number, "malformed-tool-call", "UNPARSEABLE", "UNKNOWN", line_raw,
                                               reason="TOOL_CALL_LACKS_ID_OR_NAME"))
                        continue
                    calls[call_id] = tool_name
                    call_raw = canonical_json({"tool_name": tool_name, "tool_input": arguments})
                    units.append(make_unit(line_number, "tool-call", "TOOL_CALL", "UNKNOWN", call_raw,
                                           call_id=call_id, tool_name=tool_name, reason="TARGET_BLIND_TOOL_CALL_FAILS_CLOSED"))
                elif kind in {"function_call_output", "custom_tool_call_output"}:
                    call_id, output = payload.get("call_id"), payload.get("output")
                    tool_name = calls.get(call_id) if isinstance(call_id, str) else None
                    output_text = _text_content(output)
                    if not output_text or tool_name is None:
                        units.append(make_unit(line_number, "unpaired-tool-output", "UNPARSEABLE", "UNKNOWN", line_raw,
                                               call_id=call_id if isinstance(call_id, str) else None, reason="UNPAIRED_OR_MALFORMED_TOOL_OUTPUT"))
                        continue
                    units.append(make_unit(line_number, "tool-output", "TOOL_OUTPUT", "SEMANTIC_EXPOSURE",
                                           output_text.encode("utf-8"), call_id=call_id, tool_name=tool_name,
                                           reason="INTERACTIVE_TOOL_OUTPUT_IS_SEMANTIC"))
                else:
                    units.append(make_unit(line_number, "unsupported-response-item", "SESSION_METADATA", "UNKNOWN", line_raw,
                                           reason="UNSUPPORTED_SESSION_RECORD"))
            elif row.get("type") == "turn_context" and isinstance(payload, dict) and isinstance(payload.get("summary"), str) and payload["summary"]:
                units.append(make_unit(line_number, "context-summary", "ASSISTANT", "SEMANTIC_EXPOSURE",
                                       payload["summary"].encode("utf-8"), reason="RETAINED_ASSISTANT_SUMMARY"))
            elif row.get("type") == "event_msg" and isinstance(payload, dict) and payload.get("type") in {"user_message", "agent_message"}:
                value = payload.get("message")
                if isinstance(value, str) and value:
                    origin = "USER" if payload["type"] == "user_message" else "ASSISTANT"
                    units.append(make_unit(line_number, "event-message", origin, "SEMANTIC_EXPOSURE",
                                           value.encode("utf-8"), reason="RETAINED_NATURAL_LANGUAGE"))
                else:
                    units.append(make_unit(line_number, "malformed-event-message", "UNPARSEABLE", "UNKNOWN", line_raw,
                                           reason="MESSAGE_WITHOUT_TEXT"))
            else:
                units.append(make_unit(line_number, "unsupported-record", "SESSION_METADATA", "UNKNOWN", line_raw,
                                       reason="UNSUPPORTED_SESSION_RECORD"))
        else:
            message = row.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if row.get("type") not in {"user", "assistant"} or not isinstance(content, list):
                units.append(make_unit(line_number, "unsupported-record", "SESSION_METADATA", "UNKNOWN", line_raw,
                                       reason="UNSUPPORTED_SESSION_RECORD"))
                continue
            if row["type"] == "assistant":
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        call_id, tool_name = block.get("id"), block.get("name")
                        if not isinstance(call_id, str) or not isinstance(tool_name, str):
                            units.append(make_unit(line_number, "malformed-tool-call", "UNPARSEABLE", "UNKNOWN", line_raw,
                                                   reason="TOOL_CALL_LACKS_ID_OR_NAME"))
                            continue
                        calls[call_id] = tool_name
                        units.append(make_unit(line_number, "tool-call", "TOOL_CALL", "UNKNOWN",
                                               canonical_json({"tool_name": tool_name, "tool_input": block.get("input")}),
                                               call_id=call_id, tool_name=tool_name, reason="TARGET_BLIND_TOOL_CALL_FAILS_CLOSED"))
            natural = [block for block in content if not (isinstance(block, dict) and block.get("type") in {"tool_use", "tool_result"})]
            value = _text_content(natural)
            if value:
                origin = "USER" if row["type"] == "user" else "ASSISTANT"
                units.append(make_unit(line_number, "message", origin, "SEMANTIC_EXPOSURE",
                                       value.encode("utf-8"), reason="RETAINED_NATURAL_LANGUAGE"))
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                call_id = block.get("tool_use_id")
                tool_name = calls.get(call_id) if isinstance(call_id, str) else None
                output = _text_content(block.get("content"))
                if not output or tool_name is None:
                    units.append(make_unit(line_number, "unpaired-tool-output", "UNPARSEABLE", "UNKNOWN", line_raw,
                                           call_id=call_id if isinstance(call_id, str) else None, reason="UNPAIRED_OR_MALFORMED_TOOL_OUTPUT"))
                    continue
                output_raw = output.encode("utf-8")
                units.append(make_unit(line_number, "tool-output", "TOOL_OUTPUT", "SEMANTIC_EXPOSURE", output_raw,
                                       call_id=call_id, tool_name=tool_name,
                                       reason="INTERACTIVE_TOOL_OUTPUT_IS_SEMANTIC"))
    return units


def typed_session_ledger(
    raw: bytes,
    fmt: str,
    source_id: str,
    relative_path: str,
    machine_lane_declaration: dict[str, Any] | None = None,
    *,
    ledger_id: str = "typed-session-ledger",
    created_at_utc: str = "1970-01-01T00:00:00Z",
    source_snapshot_sha256: str = "0" * 64,
    ontology_sha256: str = "0" * 64,
) -> dict[str, Any]:
    _utc(created_at_utc, "created_at_utc")
    for field, value in (("source_snapshot_sha256", source_snapshot_sha256), ("ontology_sha256", ontology_sha256)):
        if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise ValueError(f"{field} must be lowercase SHA-256")
    units = parse_session_exposure_units(raw, fmt, source_id, relative_path, machine_lane_declaration)
    counts = {name: 0 for name in sorted(EXPOSURE_CLASSES)}
    for unit_row in units:
        counts[unit_row["provenance_class"]] += 1
    fail_closed = counts["UNKNOWN"] > 0
    result: dict[str, Any] = {
        "schema": SESSION_LEDGER_SCHEMA,
        "status": "CLASSIFIED_FAIL_CLOSED" if fail_closed else "CLASSIFIED_COMPLETE",
        "ledger_id": ledger_id,
        "created_at_utc": created_at_utc,
        "source_snapshot_sha256": source_snapshot_sha256,
        "source_id": source_id,
        "ontology_sha256": ontology_sha256,
        "units": units,
        "counts": counts,
        "source_complete": True,
        "fail_closed": fail_closed,
    }
    result["ledger_sha256"] = content_address(result, "ledger_sha256")
    return result


def build_source_snapshot(
    *,
    snapshot_id: str,
    source_id: str,
    source_kind: str,
    captured_at_utc: str,
    lower_bound_utc: str,
    upper_bound_utc: str,
    producer_id: str,
    executable_sha256: str,
    invocation_contract_sha256: str,
    artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create one complete, target-blind source snapshot envelope."""

    if source_kind not in SOURCE_KINDS:
        raise ValueError(f"invalid source_kind {source_kind!r}")
    captured = _utc(captured_at_utc, "captured_at_utc")
    lower = _utc(lower_bound_utc, "lower_bound_utc")
    upper = _utc(upper_bound_utc, "upper_bound_utc")
    if lower > upper or captured < upper:
        raise ValueError("source snapshot chronology is invalid")
    for field, value in (("executable_sha256", executable_sha256), ("invocation_contract_sha256", invocation_contract_sha256)):
        if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise ValueError(f"{field} must be lowercase SHA-256")
    normalized = []
    seen = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict) or set(artifact) != {"locator", "content_sha256", "byte_count"}:
            raise ValueError("source snapshot artifact has an invalid shape")
        locator, digest, byte_count = artifact["locator"], artifact["content_sha256"], artifact["byte_count"]
        if not isinstance(locator, str) or not locator or locator in seen:
            raise ValueError("artifact locators must be unique nonempty strings")
        if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("artifact content_sha256 must be lowercase SHA-256")
        if not isinstance(byte_count, int) or isinstance(byte_count, bool) or byte_count < 0:
            raise ValueError("artifact byte_count must be a nonnegative integer")
        seen.add(locator)
        normalized.append(dict(artifact))
    normalized.sort(key=lambda row: row["locator"].encode())
    result: dict[str, Any] = {
        "schema": SOURCE_SNAPSHOT_SCHEMA,
        "status": "COMPLETE_CONTENT_ADDRESSED_SOURCE_SNAPSHOT",
        "snapshot_id": snapshot_id,
        "source_id": source_id,
        "source_kind": source_kind,
        "captured_at_utc": captured_at_utc,
        "coverage": {"lower_bound_utc": lower_bound_utc, "upper_bound_utc": upper_bound_utc, "complete": True, "gaps": []},
        "capture": {"producer_id": producer_id, "executable_sha256": executable_sha256, "invocation_contract_sha256": invocation_contract_sha256},
        "artifacts": normalized,
        "source_complete": True,
    }
    result["snapshot_sha256"] = content_address(result, "snapshot_sha256")
    return result


def _sources_by_id(snapshot: dict[str, Any], label: str) -> dict[str, dict[str, Any]]:
    sources = snapshot.get("sources")
    if not isinstance(sources, list):
        raise ValueError(f"{label}.sources must be a list")
    result: dict[str, dict[str, Any]] = {}
    for row in sources:
        if not isinstance(row, dict) or not isinstance(row.get("source_id"), str):
            raise ValueError(f"{label} has a malformed source")
        if row["source_id"] in result:
            raise ValueError(f"{label} has duplicate source_id {row['source_id']!r}")
        result[row["source_id"]] = row
    return result


def _validate_endpoint_snapshot(snapshot: object, label: str) -> dict[str, dict[str, Any]]:
    """Reject incomplete, unauthenticated, or structurally unknown endpoints."""

    if not isinstance(snapshot, dict) or snapshot.get("complete") is not True:
        raise ValueError(f"{label} endpoint snapshot is not complete")
    for field in ("snapshot_sha256", "corpus_sha256"):
        value = snapshot.get(field)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError(f"{label}.{field} must be a lowercase SHA-256")
    if snapshot["snapshot_sha256"] != content_address(snapshot, "snapshot_sha256"):
        raise ValueError(f"{label} endpoint snapshot digest does not verify")
    sources = _sources_by_id(snapshot, label)
    if not sources:
        raise ValueError(f"{label} endpoint snapshot has no sources")
    for source_id, row in sources.items():
        if row.get("complete") is not True or row.get("failure") is not None:
            raise ValueError(f"{label} source {source_id!r} is incomplete")
        if row.get("kind") not in ENDPOINT_SOURCE_KINDS:
            raise ValueError(f"{label} source {source_id!r} has unrecognized kind")
        digest = row.get("corpus_sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError(f"{label} source {source_id!r} lacks a valid corpus digest")
    return sources


def build_interval_ledger_input(
    p1_snapshot: dict[str, Any],
    cutoff_snapshot: dict[str, Any],
    *,
    checkpoint_identity: str,
    quota_gate_passed: bool,
    hard_horizon_utc: str,
) -> dict[str, Any]:
    """Bind endpoint snapshots for the complete target-blind accumulation interval."""

    p1_at = _utc(p1_snapshot.get("acquired_at_utc"), "p1 acquired_at_utc")
    cutoff_at = _utc(cutoff_snapshot.get("acquired_at_utc"), "cutoff acquired_at_utc")
    horizon = _utc(hard_horizon_utc, "hard_horizon_utc")
    if cutoff_at <= p1_at:
        raise ValueError("cutoff must be after P1")
    if cutoff_at > horizon:
        raise ValueError("cutoff exceeds the frozen hard horizon")
    if not quota_gate_passed and cutoff_at != horizon:
        raise ValueError("a pre-horizon cutoff requires an identity-only quota-gate pass")
    if not isinstance(checkpoint_identity, str) or not checkpoint_identity:
        raise ValueError("checkpoint_identity is required")
    p1_sources = _validate_endpoint_snapshot(p1_snapshot, "p1")
    cutoff_sources = _validate_endpoint_snapshot(cutoff_snapshot, "cutoff")
    missing = sorted(set(p1_sources) - set(cutoff_sources))
    if missing:
        raise ValueError(f"cutoff omitted P1 sources: {missing}")
    export_kinds = {
        row.get("export_kind")
        for row in cutoff_sources.values()
        if row.get("kind") in {"release_metadata_snapshot", "platform_export_snapshot"}
    }
    missing_exports = sorted(EXPORT_KINDS - export_kinds)
    if missing_exports:
        raise ValueError(f"cutoff lacks required release/issue/PR exports: {missing_exports}")
    intervals = []
    for source_id in sorted(cutoff_sources):
        start = p1_sources.get(source_id)
        end = cutoff_sources[source_id]
        intervals.append({
            "source_id": source_id,
            "origin_kind": end.get("kind"),
            "origin_class": end.get("origin_class", "LOCAL_RESEARCH_STATE"),
            "exposure_default": end.get("exposure_default", "UNKNOWN"),
            "p1_corpus_sha256": None if start is None else start.get("corpus_sha256"),
            "cutoff_corpus_sha256": end.get("corpus_sha256"),
            "introduced_after_p1": start is None,
            "target_identity_joined": False,
        })
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "interval": {
            "p1_acquired_at_utc": p1_snapshot["acquired_at_utc"],
            "cutoff_acquired_at_utc": cutoff_snapshot["acquired_at_utc"],
            "checkpoint_identity": checkpoint_identity,
            "identity_only_quota_gate_passed": quota_gate_passed,
            "hard_horizon_utc": hard_horizon_utc,
        },
        "target_identity_joined": False,
        "candidate_semantics_inspected": False,
        "required_export_kinds": sorted(EXPORT_KINDS),
        "complete": True,
        "sources": intervals,
    }
    result["ledger_input_sha256"] = content_address(result, "ledger_input_sha256")
    return result


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    session = commands.add_parser("parse-session")
    session.add_argument("--input", type=Path, required=True)
    session.add_argument("--format", choices=("codex", "claude"), required=True)
    session.add_argument("--source-id", required=True)
    session.add_argument("--relative-path", required=True)
    session.add_argument("--machine-lane", type=Path)
    session.add_argument("--output", type=Path)
    interval = commands.add_parser("build-interval")
    interval.add_argument("--p1-snapshot", type=Path, required=True)
    interval.add_argument("--cutoff-snapshot", type=Path, required=True)
    interval.add_argument("--checkpoint-identity", required=True)
    interval.add_argument("--quota-gate-passed", action="store_true")
    interval.add_argument("--hard-horizon-utc", required=True)
    interval.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "parse-session":
        value = typed_session_ledger(
            args.input.read_bytes(), args.format, args.source_id, args.relative_path,
            _load(args.machine_lane) if args.machine_lane else None,
        )
    else:
        value = build_interval_ledger_input(
            _load(args.p1_snapshot), _load(args.cutoff_snapshot),
            checkpoint_identity=args.checkpoint_identity,
            quota_gate_passed=args.quota_gate_passed,
            hard_horizon_utc=args.hard_horizon_utc,
        )
    rendered = pretty_json(value)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
