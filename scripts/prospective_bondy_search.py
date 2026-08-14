#!/usr/bin/env python3
"""Frozen Bondy q_4 target evaluator, mechanically disabled before commit.

Importing this module is harmless. Calling main cannot reach target evaluation
unless the immutable manifest opts in and exact boolean, commit, token, clean
tree, source attestation, and freeze verification all agree.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Sequence

import networkx as nx

import prospective_bondy_construct as construct

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development"
MANIFEST = HERE / "manifest.json"
INTERNAL_SEARCH_SECONDS = 48
INTERNAL_FINALIZE_SECONDS = 54
EXTERNAL_SECONDS = 60


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


class DurableLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.previous = "0" * 64
        self.index = 0
        self.closed = False

    def append(self, payload: dict[str, object]) -> None:
        if self.closed:
            raise RuntimeError("ledger append after durable candidate/terminal")
        body = dict(payload)
        body["record_index"] = self.index
        body["previous_sha256"] = self.previous
        body["record_sha256"] = hashlib.sha256(canonical_bytes(body)).hexdigest()
        data = canonical_bytes(body)
        with self.path.open("ab", buffering=0) as handle:
            handle.write(data)
            os.fsync(handle.fileno())
        self.previous = str(body["record_sha256"])
        self.index += 1

    def seal(self) -> None:
        self.closed = True


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
        directory_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def unlock(args: argparse.Namespace) -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text())
    lock = manifest["target_execution_lock"]
    failures: list[str] = []
    if args.enable_target is not True:
        failures.append("exact_boolean_missing")
    head = git("rev-parse", "HEAD")
    if args.campaign_commit != head:
        failures.append("campaign_commit_is_not_checked_out_HEAD")
    if git("status", "--porcelain"):
        failures.append("worktree_not_clean")
    supplied_hash = hashlib.sha256(args.activation_token.encode("utf-8")).hexdigest()
    if supplied_hash != lock.get("activation_token_sha256"):
        failures.append("exact_activation_token_mismatch")
    if lock.get("token_provisioned") is not True:
        failures.append("activation_token_not_provisioned")
    runtime = manifest.get("runtime", {})
    if sys.version.split()[0] != runtime.get("python_version"):
        failures.append("frozen_python_version_mismatch")
    if nx.__version__ != runtime.get("networkx_version"):
        failures.append("frozen_networkx_version_mismatch")
    if failures:
        raise RuntimeError("TARGET_EXECUTION_DISABLED:" + ",".join(failures))
    subprocess.run([sys.executable, str(HERE / "verify_freeze.py")], cwd=ROOT, check=True, timeout=20)
    return manifest


def replay_path(graph: nx.Graph, path: Sequence[int]) -> bool:
    return len(path) == len(set(path)) and all(graph.has_edge(a, b) for a, b in zip(path, path[1:]))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EndpointPathCoverDP:
    """Exact p(S) recurrence, capped at five paths, for all S subseteq V(H)."""

    def __init__(self, graph: nx.Graph, deadline: float) -> None:
        if set(graph) != set(range(construct.H_ORDER)):
            raise ValueError("endpoint DP requires frozen labels 0..19")
        self.n = construct.H_ORDER
        self.size = 1 << self.n
        self.adj = [sum(1 << u for u in graph.neighbors(v)) for v in range(self.n)]
        self.p = bytearray([5]) * self.size
        self.p[0] = 0
        self.end = bytearray([5]) * (self.size * self.n)
        for mask in range(1, self.size):
            if (mask & 0x1fff) == 0 and time.monotonic() >= deadline:
                raise TimeoutError("endpoint path-cover DP deadline")
            vertices = mask
            best_p = 5
            base = mask * self.n
            while vertices:
                bit = vertices & -vertices
                v = bit.bit_length() - 1
                previous = mask ^ bit
                best = min(5, self.p[previous] + 1)
                neighbors = previous & self.adj[v]
                previous_base = previous * self.n
                while neighbors:
                    u_bit = neighbors & -neighbors
                    u = u_bit.bit_length() - 1
                    if self.end[previous_base + u] < best:
                        best = self.end[previous_base + u]
                    neighbors ^= u_bit
                self.end[base + v] = best
                if best < best_p:
                    best_p = best
                vertices ^= bit
            self.p[mask] = best_p

    def reconstruct_end(self, mask: int, endpoint: int) -> list[list[int]]:
        bit = 1 << endpoint
        if not mask & bit:
            raise RuntimeError("endpoint reconstruction mask drift")
        value = self.end[mask * self.n + endpoint]
        previous = mask ^ bit
        if min(5, self.p[previous] + 1) == value:
            return self.reconstruct(previous) + [[endpoint]]
        neighbors = previous & self.adj[endpoint]
        while neighbors:
            u_bit = neighbors & -neighbors
            u = u_bit.bit_length() - 1
            if self.end[previous * self.n + u] == value:
                paths = self.reconstruct_end(previous, u)
                paths[-1].append(endpoint)
                return paths
            neighbors ^= u_bit
        raise RuntimeError("endpoint DP predecessor absent")

    def reconstruct(self, mask: int) -> list[list[int]]:
        if mask == 0:
            return []
        value = self.p[mask]
        vertices = mask
        while vertices:
            bit = vertices & -vertices
            v = bit.bit_length() - 1
            if self.end[mask * self.n + v] == value:
                paths = self.reconstruct_end(mask, v)
                if len(paths) != value:
                    raise RuntimeError("endpoint DP cover-count replay drift")
                return paths
            vertices ^= bit
        raise RuntimeError("endpoint DP optimum endpoint absent")

    def digests(self) -> dict[str, str]:
        return {
            "pc_table_sha256": hashlib.sha256(self.p).hexdigest(),
            "endpoint_table_sha256": hashlib.sha256(self.end).hexdigest(),
        }


def simple_four_path(graph: nx.Graph, vertices: Sequence[int]) -> list[int] | None:
    if len(vertices) != 4 or len(set(vertices)) != 4:
        return None
    # The formal target asks for a simple path in the induced off-cycle graph;
    # extra edges among its support are allowed.  Freeze the least ordering.
    for ordering in itertools.permutations(sorted(vertices)):
        if all(graph.has_edge(a, b) for a, b in zip(ordering, ordering[1:])):
            reverse = tuple(reversed(ordering))
            return list(min(ordering, reverse))
    return None


def stitched_cycle(paths: Sequence[Sequence[int]]) -> list[int]:
    if not 1 <= len(paths) <= construct.K:
        raise ValueError("cannot stitch frozen cover")
    hubs = list(range(construct.H_ORDER, construct.G_ORDER))
    cycle: list[int] = []
    for index, path in enumerate(paths):
        cycle.append(hubs[index])
        cycle.extend(path)
    cycle.extend(hubs[len(paths):])
    return cycle + [cycle[0]]


def replay_cycle(graph: nx.Graph, closed_walk: Sequence[int]) -> bool:
    return (
        len(closed_walk) >= 4
        and closed_walk[0] == closed_walk[-1]
        and len(set(closed_walk[:-1])) == len(closed_walk) - 1
        and all(graph.has_edge(a, b) for a, b in zip(closed_walk, closed_walk[1:]))
    )


def target_evaluate(row: dict[str, object], remaining: float) -> dict[str, object]:
    """The only proposed-candidate target call; forbidden in constructor tests."""
    evaluation_started = time.monotonic()
    peripheral = construct.graph_from_edges(construct.H_ORDER, row["edges_h"])
    deadline = time.monotonic() + remaining
    dp = EndpointPathCoverDP(peripheral, deadline)
    result: dict[str, object] = {
        "candidate": False,
        "algorithm": "python_endpoint_path_cover_dp_v1",
        "dp_digests": dp.digests(),
        "upper_deletion_sets_completed": 0,
    }
    all_mask = (1 << construct.H_ORDER) - 1
    for size in range(construct.K):
        for removed_tuple in itertools.combinations(range(construct.H_ORDER), size):
            removed_mask = sum(1 << v for v in removed_tuple)
            result["upper_deletion_sets_completed"] = int(result["upper_deletion_sets_completed"]) + 1
            if dp.p[all_mask ^ removed_mask] <= construct.K:
                kept_mask = all_mask ^ removed_mask
                counter_cover = dp.reconstruct(kept_mask)
                if not 1 <= len(counter_cover) <= construct.K or any(not replay_path(peripheral, path) for path in counter_cover):
                    raise RuntimeError("upper-rejection counter-cover replay failed")
                flattened = [v for path in counter_cover for v in path]
                if len(flattened) != len(set(flattened)) or set(flattened) != set(range(construct.H_ORDER)) - set(removed_tuple):
                    raise RuntimeError("upper-rejection counter-cover omission or overlap")
                result.update({
                    "classification": "Q4_UPPER_BOUND_REJECTED",
                    "upper_rejection": {
                        "X": list(removed_tuple),
                        "removed_mask": removed_mask,
                        "kept_mask": kept_mask,
                        "pc_H_minus_X": dp.p[kept_mask],
                        "cover_H_minus_X": counter_cover,
                    },
                    "evaluation_seconds_millis": round((time.monotonic() - evaluation_started) * 1000),
                })
                return result
    q_sets_with_path = 0
    q_sets_completed = 0
    for q_tuple in itertools.combinations(range(construct.H_ORDER), construct.K):
        if (q_sets_completed & 0xff) == 0 and time.monotonic() >= deadline:
            raise TimeoutError("frozen Q catalogue deadline")
        q_path = simple_four_path(peripheral, q_tuple)
        if q_path is None:
            q_sets_completed += 1
            continue
        q_sets_with_path += 1
        q_sets_completed += 1
        q_mask = sum(1 << v for v in q_tuple)
        complement = all_mask ^ q_mask
        if dp.p[complement] > construct.K:
            continue
        cover = dp.reconstruct(complement)
        if any(not replay_path(peripheral, path) for path in cover):
            raise RuntimeError("endpoint DP reconstructed an invalid path cover")
        joined = construct.join_separator(peripheral)
        cycle = stitched_cycle(cover)
        if not replay_cycle(joined, cycle) or set(cycle[:-1]) != set(range(construct.G_ORDER)) - set(q_tuple):
            raise RuntimeError("stitched cycle replay failed")
        result.update({
            "candidate": True,
            "classification": "CANDIDATE_PENDING_INDEPENDENT_REPLAY",
            "Q": q_path,
            "Q_mask": q_mask,
            "Q_vertex_set": list(q_tuple),
            "cover_H_minus_Q": cover,
            "cycle_C": cycle,
            "circumference_claim": 20,
            "q_sets_completed": q_sets_completed,
            "q_sets_with_simple_path": q_sets_with_path,
            "literal_failure": {"P_support_length": 4, "P_support_length_plus_one": 5, "k": 4},
            "evaluation_seconds_millis": round((time.monotonic() - evaluation_started) * 1000),
        })
        return result
    result.update({
        "classification": "NO_Q_WITH_FOUR_PATH_AND_COMPLEMENT_COVER",
        "q_sets_completed": q_sets_completed,
        "q_sets_with_simple_path": q_sets_with_path,
        "evaluation_seconds_millis": round((time.monotonic() - evaluation_started) * 1000),
    })
    return result


def independent_upper_replay(binary: Path, edges: Sequence[Sequence[int]], expected_pc_sha256: str, seconds: float) -> dict[str, object]:
    if seconds <= 0.25:
        raise TimeoutError("no independent replay budget remains")
    with tempfile.TemporaryDirectory(prefix="bondy-upper-") as directory:
        edge_file = Path(directory) / "H.edges"
        pc_table = Path(directory) / "pc-table.bin"
        edge_file.write_text("".join(f"{u} {v}\n" for u, v in edges), encoding="ascii")
        child_seconds = max(0.1, seconds - 0.1)
        started = time.monotonic()
        process = subprocess.Popen([str(binary), str(edge_file), str(pc_table)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        timed_out = False
        try:
            output, _ = process.communicate(timeout=child_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                output, _ = process.communicate(timeout=0.2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                output, _ = process.communicate()
        audit = {
            "pid": process.pid,
            "returncode": process.returncode,
            "timed_out": timed_out,
            "elapsed_seconds_millis": round((time.monotonic() - started) * 1000),
            "process_group_isolated": True,
            "process_group_reaped": process.poll() is not None,
            "binary_sha256": file_sha256(binary),
            "source_sha256": file_sha256(ROOT / "scripts/prospective_bondy_replay.cpp"),
            "stdout_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        }
        if timed_out:
            raise TimeoutError("independent q4 upper replay deadline")
        try:
            record = json.loads(output)
        except json.JSONDecodeError as error:
            raise RuntimeError("GATE_FAIL:independent replay emitted malformed JSON") from error
        audit["reported_status"] = record.get("status")
        if process.returncode != 0:
            raise RuntimeError(
                "GATE_FAIL:independent replay nonzero logical/internal exit:"
                + json.dumps({"returncode": process.returncode, "record": record}, sort_keys=True, separators=(",", ":"))
            )
        pc_sha256 = file_sha256(pc_table) if pc_table.is_file() else None
        if record.get("status") != "Q4_UPPER_BOUND_VERIFIED" or record.get("deletion_sets") != 1351 or pc_sha256 != expected_pc_sha256:
            raise RuntimeError("independent q4 upper replay rejected")
        return {"record": record, "pc_table_sha256": pc_sha256, "process_audit": audit}


def run(args: argparse.Namespace) -> int:
    manifest = unlock(args)
    attestation = json.loads(args.source_attestation.read_text())
    if attestation.get("status") != "PASS" or attestation.get("upstream") != manifest["upstream"]:
        raise RuntimeError("GATE_FAIL:source attestation missing or drifted")
    started = time.monotonic()
    ledger = DurableLedger(args.ledger)
    ledger.append({"kind": "source_control", "record": construct.source_control()})
    applicable = 0
    evaluated = 0
    for row in construct.generate(manifest["grammar"]["row_limit"]):
        now = time.monotonic()
        if now - started >= INTERNAL_SEARCH_SECONDS:
            terminal = {"kind": "terminal", "status": "CAP_PREFIX", "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
            ledger.seal()
            atomic_json(args.terminal, terminal)
            return 0
        ledger.append({k: v for k, v in row.items() if k not in ("edges_h", "roles")})
        if row["constructor_verdict"] != "APPLICABLE":
            continue
        applicable += 1
        try:
            evaluation = target_evaluate(row, INTERNAL_SEARCH_SECONDS - (time.monotonic() - started))
        except TimeoutError:
            terminal = {"kind": "terminal", "status": "CAP_PREFIX", "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
            ledger.seal()
            atomic_json(args.terminal, terminal)
            return 0
        evaluated += 1
        ledger.append({"kind": "target_evaluation", "row_index": row["row_index"], "result": evaluation})
        if evaluation["candidate"]:
            try:
                upper = independent_upper_replay(
                    args.replay_binary,
                    row["edges_h"],
                    evaluation["dp_digests"]["pc_table_sha256"],
                    INTERNAL_FINALIZE_SECONDS - (time.monotonic() - started),
                )
            except TimeoutError:
                terminal = {"kind": "terminal", "status": "CAP_PREFIX", "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
                ledger.seal()
                atomic_json(args.terminal, terminal)
                return 0
            candidate = {
                "kind": "terminal",
                "status": "CANDIDATE_FOUND",
                "row": row,
                "edges_g": construct.edge_list(construct.join_separator(construct.graph_from_edges(construct.H_ORDER, row["edges_h"]))),
                "evaluation": evaluation,
                "q4_upper_certificate_obligation": "for_all_X_card_lt_4_pc_H_minus_X_gt_4",
                "independent_upper_replay": upper,
                "provenance": {
                    "search_algorithm": "python_endpoint_path_cover_dp_v1",
                    "replay_algorithm": "cpp_endpoint_path_cover_dp_v1",
                    "python_version": sys.version.split()[0],
                    "networkx_version": nx.__version__,
                    "search_elapsed_seconds_millis": round((time.monotonic() - started) * 1000),
                    "caps_seconds": {"search": INTERNAL_SEARCH_SECONDS, "finalize": INTERNAL_FINALIZE_SECONDS, "external": EXTERNAL_SECONDS},
                    "search_source_sha256": file_sha256(Path(__file__)),
                    "replay_source_sha256": file_sha256(ROOT / "scripts/prospective_bondy_replay.cpp"),
                },
                "ledger_head": ledger.previous,
            }
            ledger.seal()
            atomic_json(args.candidate, candidate)
            return 0
    if time.monotonic() - started >= INTERNAL_FINALIZE_SECONDS:
        raise RuntimeError("GATE_FAIL:missed 54-second finalization boundary")
    if applicable == 0:
        status = "NO_APPLICABLE_CANDIDATES"
    elif evaluated == 0:
        status = "NO_TARGET_RAISING_CANDIDATES"
    else:
        status = "DOMAIN_EXHAUSTED"
    terminal = {"kind": "terminal", "status": status, "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
    ledger.seal()
    atomic_json(args.terminal, terminal)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enable-target", action="store_true")
    parser.add_argument("--campaign-commit", required=True)
    parser.add_argument("--activation-token", required=True)
    parser.add_argument("--source-attestation", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--replay-binary", type=Path, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(TimeoutError("external TERM")))
    try:
        return run(args)
    except Exception as error:
        failure = {"kind": "terminal", "status": "GATE_FAIL", "error_type": type(error).__name__, "error": str(error)}
        atomic_json(args.terminal, failure)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
