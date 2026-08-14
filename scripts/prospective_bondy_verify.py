#!/usr/bin/env python3
"""Independent artifact verifier for the frozen Bondy DEVELOPMENT arm."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Sequence

import networkx as nx

import prospective_bondy_construct as construct

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_TERMINALS = {
    "CANDIDATE_FOUND",
    "DOMAIN_EXHAUSTED",
    "CAP_PREFIX",
    "NO_APPLICABLE_CANDIDATES",
    "NO_TARGET_RAISING_CANDIDATES",
    "GATE_FAIL",
}
EXPECTED_DISCOVERY_ALGORITHM = "python_endpoint_path_cover_dp_v1"
EXPECTED_PYTHON_VERSION = "3.11.9"
EXPECTED_NETWORKX_VERSION = "3.3"
COMMON_EVALUATION_FIELDS = {
    "candidate",
    "classification",
    "algorithm",
    "dp_digests",
    "upper_deletion_sets_completed",
    "evaluation_seconds_millis",
}
EVALUATION_FIELDS = {
    "Q4_UPPER_BOUND_REJECTED": COMMON_EVALUATION_FIELDS | {"upper_rejection"},
    "NO_Q_WITH_FOUR_PATH_AND_COMPLEMENT_COVER": COMMON_EVALUATION_FIELDS
    | {"q_sets_completed", "q_sets_with_simple_path"},
    "CANDIDATE_PENDING_INDEPENDENT_REPLAY": COMMON_EVALUATION_FIELDS
    | {
        "Q",
        "Q_mask",
        "Q_vertex_set",
        "cover_H_minus_Q",
        "cycle_C",
        "circumference_claim",
        "q_sets_completed",
        "q_sets_with_simple_path",
        "literal_failure",
    },
}


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def atomic_json(path: Path, value: object) -> None:
    data = canonical_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_canonical_json(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical JSON bytes: {path}")
    return value


def verify_ledger(path: Path) -> tuple[list[dict[str, object]], str]:
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise RuntimeError("ledger lacks exact final ASCII newline")
    previous = "0" * 64
    count = 0
    records: list[dict[str, object]] = []
    for line in raw.splitlines(keepends=True):
        value = json.loads(line)
        if line != canonical_bytes(value):
            raise RuntimeError("ledger noncanonical-byte drift")
        claimed = value.pop("record_sha256")
        if value.get("record_index") != count or value.get("previous_sha256") != previous:
            raise RuntimeError("ledger chronology/hash-chain drift")
        actual = hashlib.sha256(canonical_bytes(value)).hexdigest()
        if claimed != actual:
            raise RuntimeError("ledger record hash drift")
        previous = claimed
        count += 1
        records.append(value)
    return records, previous


def semantic_payload(record: dict[str, object]) -> dict[str, object]:
    return {k: v for k, v in record.items() if k not in ("record_index", "previous_sha256")}


def validate_evaluation_schema(result: dict[str, object]) -> str:
    classification = result.get("classification")
    if not isinstance(classification, str) or classification not in EVALUATION_FIELDS:
        raise RuntimeError("missing or unknown target evaluation classification")
    if set(result) != EVALUATION_FIELDS[classification]:
        raise RuntimeError("target evaluation schema drift")
    expected_candidate = classification == "CANDIDATE_PENDING_INDEPENDENT_REPLAY"
    if result.get("candidate") is not expected_candidate:
        raise RuntimeError("target classification/candidate Boolean disagreement")
    if result.get("algorithm") != EXPECTED_DISCOVERY_ALGORITHM:
        raise RuntimeError("target evaluation algorithm drift")
    digests = result.get("dp_digests")
    if not isinstance(digests, dict) or set(digests) != {"pc_table_sha256", "endpoint_table_sha256"}:
        raise RuntimeError("target evaluation DP digest schema drift")
    if any(not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value) for value in digests.values()):
        raise RuntimeError("target evaluation DP digest value drift")
    upper_completed = result.get("upper_deletion_sets_completed")
    elapsed = result.get("evaluation_seconds_millis")
    if isinstance(upper_completed, bool) or not isinstance(upper_completed, int) or not 1 <= upper_completed <= 1351:
        raise RuntimeError("target upper-catalogue accounting drift")
    if isinstance(elapsed, bool) or not isinstance(elapsed, int) or elapsed < 0:
        raise RuntimeError("target evaluation timing drift")
    if classification != "Q4_UPPER_BOUND_REJECTED" and upper_completed != 1351:
        raise RuntimeError("target result lacks complete q4 upper audit")
    if classification == "NO_Q_WITH_FOUR_PATH_AND_COMPLEMENT_COVER":
        if result["q_sets_completed"] != 4845:
            raise RuntimeError("false exhaustive Q terminal")
        q_paths = result["q_sets_with_simple_path"]
        if isinstance(q_paths, bool) or not isinstance(q_paths, int) or not 0 <= q_paths <= 4845:
            raise RuntimeError("target Q-path accounting drift")
    if classification == "CANDIDATE_PENDING_INDEPENDENT_REPLAY":
        q_completed = result["q_sets_completed"]
        q_paths = result["q_sets_with_simple_path"]
        if (
            isinstance(q_completed, bool)
            or not isinstance(q_completed, int)
            or not 1 <= q_completed <= 4845
            or isinstance(q_paths, bool)
            or not isinstance(q_paths, int)
            or not 1 <= q_paths <= q_completed
        ):
            raise RuntimeError("candidate Q-catalogue accounting drift")
    return classification


def validate_upper_rejection(graph: nx.Graph, result: dict[str, object]) -> dict[str, int]:
    if result.get("classification") != "Q4_UPPER_BOUND_REJECTED" or result.get("candidate") is not False:
        raise RuntimeError("not a frozen q4 upper-rejection record")
    witness = result.get("upper_rejection")
    if not isinstance(witness, dict) or set(witness) != {"X", "removed_mask", "kept_mask", "pc_H_minus_X", "cover_H_minus_X"}:
        raise RuntimeError("q4 upper rejection lacks counter-witness")
    removed = [int(v) for v in witness.get("X", [])]
    if removed != sorted(set(removed)) or len(removed) >= construct.K or any(not 0 <= v < construct.H_ORDER for v in removed):
        raise RuntimeError("upper-rejection removed set is noncanonical")
    removed_mask = sum(1 << v for v in removed)
    all_mask = (1 << construct.H_ORDER) - 1
    if witness.get("removed_mask") != removed_mask or witness.get("kept_mask") != all_mask ^ removed_mask:
        raise RuntimeError("upper-rejection mask/set disagreement")
    cover = [[int(v) for v in path] for path in witness.get("cover_H_minus_X", [])]
    if not 1 <= len(cover) <= construct.K or any(not replay_path(graph, path) for path in cover):
        raise RuntimeError("upper-rejection path cover replay failed")
    flattened = [v for path in cover for v in path]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(range(construct.H_ORDER)) - set(removed):
        raise RuntimeError("upper-rejection cover omission or overlap")
    if witness.get("pc_H_minus_X") != len(cover):
        raise RuntimeError("upper-rejection cover count drift")
    expected_ordinal = 0
    for size in range(construct.K):
        for frozen_removed in itertools.combinations(range(construct.H_ORDER), size):
            expected_ordinal += 1
            if frozen_removed == tuple(removed):
                break
        else:
            continue
        break
    if result.get("upper_deletion_sets_completed") != expected_ordinal:
        raise RuntimeError("upper-rejection witness/catalogue ordinal drift")
    return {"removed": len(removed), "paths": len(cover)}


def verify_ledger_semantics(records: list[dict[str, object]], artifact: dict[str, object]) -> dict[str, object]:
    if len(records) < 2 or semantic_payload(records[0]) != {"kind": "campaign_handoff", "handoff": artifact.get("handoff")}:
        raise RuntimeError("ledger does not begin with exact campaign handoff")
    if semantic_payload(records[1]) != {"kind": "source_control", "record": construct.source_control()}:
        raise RuntimeError("ledger does not begin with exact S(4,4) source control")
    expected_rows = list(construct.generate(construct.ROW_LIMIT))
    cursor = 2
    constructor_count = 0
    applicable = 0
    evaluated = 0
    outstanding_applicable: list[int] = []
    evaluations: dict[int, dict[str, object]] = {}
    while cursor < len(records):
        current = semantic_payload(records[cursor])
        if current.get("kind") != "constructor_row":
            raise RuntimeError("ledger target row is not preceded by its constructor row")
        row_index = int(current.get("row_index", -1))
        if row_index != constructor_count or row_index >= construct.ROW_LIMIT:
            raise RuntimeError("constructor indices are not contiguous frozen order")
        expected_full = expected_rows[row_index]
        expected_ledger = {k: v for k, v in expected_full.items() if k not in ("edges_h", "roles")}
        if current != expected_ledger:
            raise RuntimeError(f"constructor row {row_index} differs from exact replay")
        constructor_count += 1
        cursor += 1
        if expected_full["constructor_verdict"] != "APPLICABLE":
            continue
        applicable += 1
        if cursor < len(records) and semantic_payload(records[cursor]).get("kind") == "target_evaluation":
            target = semantic_payload(records[cursor])
            if int(target.get("row_index", -1)) != row_index or row_index in evaluations:
                raise RuntimeError("target evaluation row binding/order drift")
            result = target.get("result")
            if not isinstance(result, dict):
                raise RuntimeError("target evaluation is not an object")
            classification = validate_evaluation_schema(result)
            if classification == "Q4_UPPER_BOUND_REJECTED":
                peripheral = construct.graph_from_edges(construct.H_ORDER, expected_full["edges_h"])
                validate_upper_rejection(peripheral, result)
            evaluations[row_index] = result
            evaluated += 1
            cursor += 1
        else:
            outstanding_applicable.append(row_index)
    status = artifact.get("status")
    candidate_rows = [row_index for row_index, result in evaluations.items() if result["candidate"] is True]
    if status == "CANDIDATE_FOUND":
        if outstanding_applicable or not evaluations:
            raise RuntimeError("candidate has an unevaluated applicable predecessor")
        row_index = int(artifact["row"]["row_index"])
        if row_index != max(evaluations) or evaluations[row_index] != artifact.get("evaluation"):
            raise RuntimeError("candidate/evaluation artifact is not bound to exact final ledger row")
        if artifact["row"] != expected_rows[row_index] or not evaluations[row_index].get("candidate"):
            raise RuntimeError("candidate row differs from exact constructor replay")
        if candidate_rows != [row_index]:
            raise RuntimeError("candidate terminal has prior or unbound candidate evaluations")
    elif status == "DOMAIN_EXHAUSTED":
        if constructor_count != construct.ROW_LIMIT or outstanding_applicable or evaluated != applicable:
            raise RuntimeError("truncated false DOMAIN_EXHAUSTED")
    elif status == "NO_APPLICABLE_CANDIDATES":
        if constructor_count != construct.ROW_LIMIT or applicable != 0 or evaluated != 0:
            raise RuntimeError("false NO_APPLICABLE_CANDIDATES")
    elif status == "NO_TARGET_RAISING_CANDIDATES":
        if constructor_count != construct.ROW_LIMIT or applicable <= 0 or evaluated != 0:
            raise RuntimeError("false NO_TARGET_RAISING_CANDIDATES")
    elif status == "CAP_PREFIX":
        if constructor_count == construct.ROW_LIMIT and not outstanding_applicable and evaluated == applicable:
            raise RuntimeError("CAP_PREFIX falsely replaces completed domain")
        if len(outstanding_applicable) > 1 or (outstanding_applicable and outstanding_applicable[-1] != constructor_count - 1):
            raise RuntimeError("CAP_PREFIX has nonfinal evaluation holes")
    elif status != "GATE_FAIL":
        raise RuntimeError("unknown artifact status during semantic replay")
    if status != "CANDIDATE_FOUND" and candidate_rows:
        raise RuntimeError("noncandidate terminal contains a candidate evaluation")
    for field, exact in (("applicable", applicable), ("evaluated", evaluated)):
        if field in artifact and int(artifact[field]) != exact:
            raise RuntimeError(f"terminal {field} count drift")
    return {"constructor_rows": constructor_count, "applicable": applicable, "evaluated": evaluated}


def replay_path(graph: nx.Graph, path: Sequence[int]) -> bool:
    return len(path) == len(set(path)) and all(graph.has_edge(a, b) for a, b in zip(path, path[1:]))


def replay_cycle(graph: nx.Graph, cycle: Sequence[int]) -> bool:
    return (
        len(cycle) >= 4
        and cycle[0] == cycle[-1]
        and len(set(cycle[:-1])) == len(cycle) - 1
        and all(graph.has_edge(a, b) for a, b in zip(cycle, cycle[1:]))
    )


def deadline_timeout(deadline: float, cap: float = 10.0) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0.25:
        raise TimeoutError("independent verifier internal deadline")
    return min(cap, remaining)


def terminate_and_reap(process: subprocess.Popen[str]) -> str:
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        output, _ = process.communicate(timeout=0.2)
    except subprocess.TimeoutExpired:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        output, _ = process.communicate()
    finally:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
    return output


def compile_replay(work: Path, deadline: float) -> tuple[Path, dict[str, object]]:
    source = Path(__file__).with_name("prospective_bondy_replay.cpp")
    binary = work / "prospective_bondy_replay"
    compiler = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
    command = ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(binary)]
    completed = subprocess.run(command, text=True, capture_output=True, timeout=deadline_timeout(deadline))
    if completed.returncode != 0:
        raise RuntimeError("independent replay compilation failed: " + completed.stdout + completed.stderr)
    provenance = {
        "compiler": compiler,
        "flags": ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror"],
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
    }
    return binary, provenance


def validate_search_replay_audit(prior_upper: object) -> dict[str, object]:
    if not isinstance(prior_upper, dict):
        raise RuntimeError("candidate lacks bound pre-publication independent upper replay")
    prior_process = prior_upper.get("process_audit", {})
    prior_record = prior_upper.get("record", {})
    expected_prior_stdout = b'{"status":"Q4_UPPER_BOUND_VERIFIED","deletion_sets":1351,"pc_table_bytes":1048576}\n'
    if (
        set(prior_upper) != {"record", "pc_table_sha256", "process_audit"}
        or prior_record != {"status": "Q4_UPPER_BOUND_VERIFIED", "deletion_sets": 1351, "pc_table_bytes": 1048576}
        or set(prior_process) != {"pid", "returncode", "timed_out", "elapsed_seconds_millis", "process_group_isolated", "process_group_reaped", "binary_sha256", "source_sha256", "stdout_sha256", "reported_status"}
        or prior_process.get("returncode") != 0
        or prior_process.get("timed_out") is not False
        or prior_process.get("process_group_isolated") is not True
        or prior_process.get("process_group_reaped") is not True
        or prior_process.get("reported_status") != "Q4_UPPER_BOUND_VERIFIED"
        or prior_process.get("source_sha256") != hashlib.sha256(Path(__file__).with_name("prospective_bondy_replay.cpp").read_bytes()).hexdigest()
        or prior_process.get("stdout_sha256") != hashlib.sha256(expected_prior_stdout).hexdigest()
        or isinstance(prior_process.get("pid"), bool) or not isinstance(prior_process.get("pid"), int) or prior_process["pid"] <= 0
        or any(not isinstance(prior_process.get(key), str) or len(prior_process[key]) != 64 or any(c not in "0123456789abcdef" for c in prior_process[key]) for key in ("binary_sha256", "source_sha256", "stdout_sha256"))
        or isinstance(prior_process.get("elapsed_seconds_millis"), bool) or not isinstance(prior_process.get("elapsed_seconds_millis"), int) or prior_process["elapsed_seconds_millis"] < 0
    ):
        raise RuntimeError("candidate pre-publication replay provenance drift")
    return prior_process


def require_replay_binary_binding(prior_process: dict[str, object], build: dict[str, object]) -> None:
    if build.get("binary_sha256") != prior_process.get("binary_sha256"):
        raise RuntimeError("search-time and verification replay binary drift")


def verify_candidate(candidate: dict[str, object], work: Path, deadline: float) -> dict[str, object]:
    if set(candidate) != {
        "schema", "kind", "status", "handoff", "row", "edges_g", "evaluation", "q4_upper_certificate_obligation",
        "independent_upper_replay", "provenance", "ledger_head",
    } or candidate.get("schema") != "bondy_candidate_v3" or candidate.get("kind") != "candidate" or candidate.get("status") != "CANDIDATE_FOUND":
        raise RuntimeError("candidate file is not CANDIDATE_FOUND")
    row = candidate["row"]
    evaluation = candidate["evaluation"]
    prior_upper = candidate.get("independent_upper_replay", {})
    if prior_upper.get("record", {}).get("status") != "Q4_UPPER_BOUND_VERIFIED" or prior_upper.get("pc_table_sha256") != evaluation.get("dp_digests", {}).get("pc_table_sha256"):
        raise RuntimeError("candidate lacks bound pre-publication independent upper replay")
    prior_process = validate_search_replay_audit(prior_upper)
    provenance = candidate.get("provenance", {})
    expected_caps = {"search": 48, "finalize": 54, "external": 60}
    if (
        set(provenance) != {"search_algorithm", "replay_algorithm", "python_version", "networkx_version", "search_elapsed_seconds_millis", "caps_seconds", "search_source_sha256", "replay_source_sha256"}
        or candidate.get("q4_upper_certificate_obligation") != "for_all_X_card_lt_4_pc_H_minus_X_gt_4"
        or provenance.get("search_algorithm") != "python_endpoint_path_cover_dp_v1"
        or provenance.get("replay_algorithm") != "cpp_endpoint_path_cover_dp_v1"
        or provenance.get("python_version") != EXPECTED_PYTHON_VERSION
        or provenance.get("networkx_version") != EXPECTED_NETWORKX_VERSION
        or provenance.get("caps_seconds") != expected_caps
        or provenance.get("search_source_sha256") != hashlib.sha256(Path(__file__).with_name("prospective_bondy_search.py").read_bytes()).hexdigest()
        or provenance.get("replay_source_sha256") != prior_process.get("source_sha256")
        or not isinstance(provenance.get("search_elapsed_seconds_millis"), int)
        or provenance.get("search_elapsed_seconds_millis", -1) < evaluation.get("evaluation_seconds_millis", 0)
    ):
        raise RuntimeError("candidate search timing/version provenance drift")
    peripheral = construct.graph_from_edges(construct.H_ORDER, row["edges_h"])
    reconstructed, metadata = construct.construct_row(
        tuple(row["parameters"]["matching_choices"]),
        int(row["parameters"]["quotient_index"]),
        int(row["parameters"]["port_permutation_index"]),
    )
    if construct.edge_list(reconstructed) != construct.edge_list(peripheral) or metadata != row["parameters"]:
        raise RuntimeError("constructor replay drift")
    verdict, gate = construct.constructor_gate(peripheral, metadata)
    if verdict != "APPLICABLE" or gate.get("induced_claw") != row["gate"].get("induced_claw"):
        raise RuntimeError("candidate no longer passes target-free gates")
    q_path = [int(v) for v in evaluation["Q"]]
    if construct.induced_claw(construct.join_separator(peripheral)) is None:
        raise RuntimeError("candidate entered the proved claw-free domain")
    if len(q_path) != construct.K or not replay_path(peripheral, q_path):
        raise RuntimeError("Q path replay failed")
    if set(q_path) != set(int(v) for v in evaluation["Q_vertex_set"]):
        raise RuntimeError("Q path and frozen Q vertex set disagree")
    if evaluation.get("Q_mask") != sum(1 << v for v in q_path):
        raise RuntimeError("Q path and frozen Q mask disagree")
    if evaluation.get("circumference_claim") != 20:
        raise RuntimeError("candidate circumference claim drift")
    cover = [[int(v) for v in path] for path in evaluation["cover_H_minus_Q"]]
    if not 1 <= len(cover) <= construct.K or any(not replay_path(peripheral, path) for path in cover):
        raise RuntimeError("explicit H-Q path cover failed")
    flattened = [v for path in cover for v in path]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(range(construct.H_ORDER)) - set(q_path):
        raise RuntimeError("explicit H-Q cover has an omission or overlap")
    joined = construct.join_separator(peripheral)
    expected_edges_g = construct.edge_list(joined)
    if candidate.get("edges_g") != expected_edges_g:
        raise RuntimeError("candidate complete joined edge list drift")
    if construct.edge_list(construct.graph_from_edges(construct.G_ORDER, candidate["edges_g"])) != expected_edges_g:
        raise RuntimeError("candidate joined edge-list round-trip failed")
    cycle = [int(v) for v in evaluation["cycle_C"]]
    if not replay_cycle(joined, cycle):
        raise RuntimeError("stitched cycle replay failed")
    if set(cycle[:-1]) != set(range(construct.G_ORDER)) - set(q_path):
        raise RuntimeError("cycle/off-cycle coordinates disagree")
    if evaluation.get("literal_failure") != {"P_support_length": 4, "P_support_length_plus_one": 5, "k": 4}:
        raise RuntimeError("literal target failure drift")
    edge_file = work / "candidate-H.edges"
    pc_table = work / "pc-table.bin"
    edge_file.write_text("".join(f"{u} {v}\n" for u, v in construct.edge_list(peripheral)), encoding="ascii")
    replay_binary, build = compile_replay(work, deadline)
    require_replay_binary_binding(prior_process, build)
    child = subprocess.Popen(
        [str(replay_binary), str(edge_file), str(pc_table)], text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, start_new_session=True,
    )
    output = ""
    timed_out = False
    try:
        output, _ = child.communicate(timeout=deadline_timeout(deadline, 44.0))
    except (subprocess.TimeoutExpired, TimeoutError):
        timed_out = True
        output = terminate_and_reap(child)
    except BaseException:
        terminate_and_reap(child)
        raise
    process_audit = {"pid": child.pid, "returncode": child.returncode, "timed_out": timed_out, "process_group_isolated": True, "process_group_reaped": child.poll() is not None}
    if timed_out or child.returncode != 0:
        raise RuntimeError("independent q4 upper replay rejected or timed out: " + output)
    replay_record = json.loads(output)
    if replay_record.get("status") != "Q4_UPPER_BOUND_VERIFIED" or replay_record.get("deletion_sets") != 1351:
        raise RuntimeError("independent q4 upper replay terminal drift")
    pc_table_sha256 = hashlib.sha256(pc_table.read_bytes()).hexdigest()
    if pc_table_sha256 != evaluation["dp_digests"]["pc_table_sha256"]:
        raise RuntimeError("independent and discovery pc-table digest mismatch")
    # q4>=16 follows from the explicit H-Q cover; exhaustive replay gives
    # q4<=16. Hence circumference(K4 join H)=4+q4=20 exactly.
    return {
        "status": "CANDIDATE_VERIFIED",
        "q4_lower": 16,
        "q4_upper": 16,
        "circumference": 20,
        "independent_replay": replay_record,
        "pc_table_sha256": pc_table_sha256,
        "independent_build": build,
        "independent_process_audit": process_audit,
    }


def verify_terminal(terminal: dict[str, object]) -> dict[str, object]:
    status = terminal.get("status")
    if (
        set(terminal) != {"schema", "kind", "status", "handoff", "applicable", "evaluated", "ledger_head"}
        or terminal.get("schema") != "bondy_terminal_v3"
        or terminal.get("kind") != "terminal"
        or status not in ALLOWED_TERMINALS - {"CANDIDATE_FOUND", "GATE_FAIL"}
    ):
        raise RuntimeError("unknown or misplaced terminal")
    if status == "CAP_PREFIX" and "evaluated" not in terminal:
        raise RuntimeError("CAP_PREFIX lacks exact evaluated prefix")
    if status == "DOMAIN_EXHAUSTED" and int(terminal.get("evaluated", 0)) <= 0:
        raise RuntimeError("false domain exhaustion")
    return {"status": "TERMINAL_VERIFIED", "terminal_status": status}


def main() -> int:
    verification_started = time.monotonic()
    verifier_deadline = verification_started + 54.0
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(TimeoutError("external verifier TERM")))
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("candidate", "terminal"))
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-attestation", type=Path, required=True)
    parser.add_argument("--campaign-commit", required=True)
    args = parser.parse_args()
    records, head = verify_ledger(args.ledger)
    artifact = read_canonical_json(args.artifact)
    attestation_raw = args.source_attestation.read_bytes()
    attestation = json.loads(attestation_raw)
    if attestation_raw != canonical_bytes(attestation):
        raise RuntimeError("source attestation is not canonical")
    handoff = {
        "schema": "bondy_campaign_handoff_v1",
        "campaign_commit": args.campaign_commit,
        "source_attestation_sha256": hashlib.sha256(attestation_raw).hexdigest(),
    }
    checked_out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if artifact.get("handoff") != handoff or checked_out != args.campaign_commit:
        raise RuntimeError("artifact campaign/source-attestation handoff drift")
    if artifact.get("ledger_head") != head and artifact.get("status") != "GATE_FAIL":
        raise RuntimeError("terminal/candidate does not bind exact ledger head")
    semantic = verify_ledger_semantics(records, artifact)
    if args.mode == "candidate":
        with tempfile.TemporaryDirectory(prefix="bondy-replay-") as directory:
            result = verify_candidate(artifact, Path(directory), verifier_deadline)
    else:
        result = verify_terminal(artifact)
    result.update({
        "schema": "bondy_verification_v3",
        "handoff": handoff,
        "ledger_rows": len(records),
        "ledger_head": head,
        "semantic_replay": semantic,
        "verifier_version": "bondy_artifact_verifier_v1",
        "verification_seconds_millis": round((time.monotonic() - verification_started) * 1000),
        "verifier_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    })
    atomic_json(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
