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
LIVE_GATE_CHECKS = {
    "bracket_snapshot_stable",
    "complete_delta_disjoint",
    "complete_open_pr_bindings",
    "declaration_shape_exact",
    "exact_allowed_search_result_sets",
    "exact_local_contamination_history",
    "frozen_commit_is_live_ancestor",
    "historical_anchor_exact",
    "known_ingestion_issue_exact",
    "known_ingestion_pr_exact",
    "live_main_stable",
    "live_target_exact",
    "no_open_pr_touches_protected_paths",
    "no_standalone_repository_hit",
    "paper_sha256",
    "semantic_closure_exact",
    "toolchain_and_external_revisions_exact",
}
LIVE_ATTESTATION_FIELDS = {
    "schema",
    "kind",
    "status",
    "checks",
    "campaign",
    "pinned_upstream",
    "live_upstream",
    "continuity",
    "open_pr_protected_path_matches",
    "bracket_snapshot_before",
    "bracket_snapshot_after",
    "graphql_rate_limit_observations",
    "local_history_hits",
    "local_history_identities",
}
BRACKET_FIELDS = {"main", "continuity", "known_issue", "known_pr", "searches", "open_pull_binding_surface", "repository_total_count"}
PULL_IDENTITY_FIELDS = {
    "node_id",
    "number",
    "state",
    "title",
    "draft",
    "updated_at",
    "head_sha",
    "head_ref",
    "head_repo",
    "base_sha",
    "base_ref",
    "base_repo",
    "changed_files",
}
PULL_BINDING_FIELDS = PULL_IDENTITY_FIELDS | {"changed_paths", "changed_paths_sha256"}
FROZEN_TARGET_PATH = "FormalConjectures/Arxiv/2606.03696/BondyLongestCycles.lean"
CONTINUITY_FIELDS = {
    "pinned", "live", "merge_base", "ancestor_verified", "commits", "delta", "delta_sha256",
    "target", "target_raw_utf8", "declaration", "closure_count", "closure_sha256", "closure_entries",
    "toolchain_sha256", "toolchain", "external_revisions_sha256", "external_revisions", "protected_paths",
}
CONTINUITY_SURFACE_FIELDS = {
    "canonical_sha256", "live", "target", "target_raw_bytes", "target_raw_sha256", "declaration",
    "closure_count", "closure_sha256", "toolchain_sha256", "external_revisions_sha256",
}


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


class DurableLedger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("xb", buffering=0) as handle:
            os.fsync(handle.fileno())
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


def validate_live_attestation(attestation: dict[str, object], manifest: dict[str, object]) -> None:
    checks = attestation.get("checks")
    before = attestation.get("bracket_snapshot_before")
    after = attestation.get("bracket_snapshot_after")
    continuity = attestation.get("continuity")
    if (
        set(attestation) != LIVE_ATTESTATION_FIELDS
        or manifest.get("live_gate", {}).get("schema") != "bondy_source_status_duplicate_gate_tip_continuity_v3_2"
        or attestation.get("schema") != "bondy_source_status_duplicate_gate_tip_continuity_v3_2"
        or attestation.get("kind") != "source_status_duplicate_gate"
        or attestation.get("status") != "PASS"
        or attestation.get("pinned_upstream") != manifest["upstream"]
        or not isinstance(attestation.get("campaign"), dict) or set(attestation["campaign"]) != {"commit", "tree"}
        or not all(isinstance(attestation["campaign"].get(key), str) and len(attestation["campaign"][key]) == 40 for key in ("commit", "tree"))
        or not isinstance(checks, dict)
        or set(checks) != LIVE_GATE_CHECKS
        or any(value is not True for value in checks.values())
        or not isinstance(before, dict)
        or set(before) != BRACKET_FIELDS
        or before != after
        or not isinstance(continuity, dict)
        or set(continuity) != CONTINUITY_FIELDS
        or attestation.get("open_pr_protected_path_matches") != []
    ):
        raise RuntimeError("GATE_FAIL:source attestation missing or drifted")
    frozen = manifest.get("semantic_closure")
    surface = before.get("continuity")
    binding_surface = before.get("open_pull_binding_surface")
    if (
        not isinstance(frozen, dict) or not isinstance(surface, dict) or set(surface) != CONTINUITY_SURFACE_FIELDS
        or surface.get("canonical_sha256") != canonical_sha256(continuity)
        or surface.get("live") != continuity.get("live")
        or surface.get("target") != continuity.get("target")
        or surface.get("declaration") != continuity.get("declaration")
        or surface.get("closure_count") != continuity.get("closure_count")
        or surface.get("closure_sha256") != continuity.get("closure_sha256")
        or surface.get("toolchain_sha256") != continuity.get("toolchain_sha256")
        or surface.get("external_revisions_sha256") != continuity.get("external_revisions_sha256")
        or continuity.get("pinned") != {"commit": manifest["upstream"]["commit"], "tree": manifest["upstream"]["tree"]}
        or continuity.get("live") != attestation.get("live_upstream")
        or continuity.get("live") != before.get("main")
        or continuity.get("merge_base") != manifest["upstream"]["commit"]
        or continuity.get("ancestor_verified") is not True
        or continuity.get("closure_count") != frozen.get("count")
        or continuity.get("closure_sha256") != frozen.get("sha256")
        or canonical_sha256(continuity.get("closure_entries")) != frozen.get("sha256")
        or continuity.get("toolchain_sha256") != frozen.get("toolchain_sha256")
        or canonical_sha256(continuity.get("toolchain")) != frozen.get("toolchain_sha256")
        or continuity.get("external_revisions_sha256") != frozen.get("external_revisions_sha256")
        or canonical_sha256(continuity.get("external_revisions")) != frozen.get("external_revisions_sha256")
        or not isinstance(continuity.get("target_raw_utf8"), str)
        or surface.get("target_raw_bytes") != len(continuity["target_raw_utf8"].encode("utf-8"))
        or surface.get("target_raw_sha256") != hashlib.sha256(continuity["target_raw_utf8"].encode("utf-8")).hexdigest()
        or surface.get("target_raw_sha256") != manifest.get("source_sha256")
        or continuity.get("target", {}).get("path") != manifest["upstream"]["path"]
        or set(continuity.get("target", {})) != {"path", "mode", "type", "blob", "bytes", "sha256"}
        or continuity.get("target", {}).get("mode") != "100644"
        or continuity.get("target", {}).get("type") != "blob"
        or continuity.get("target", {}).get("bytes") != surface.get("target_raw_bytes")
        or continuity.get("target", {}).get("blob") != manifest["upstream"]["blob"]
        or continuity.get("target", {}).get("sha256") != manifest.get("source_sha256")
        or continuity.get("declaration") != {"declaration_count": 1, "exact_open_attribute_count": 1, "answer_wrapper_count": 1, "exact_by_sorry_block_count": 1}
        or not isinstance(binding_surface, dict) or set(binding_surface) != {"total_count", "bindings"}
        or not isinstance(before.get("main"), dict) or set(before["main"]) != {"commit", "tree"}
        or not all(isinstance(before["main"].get(key), str) and len(before["main"][key]) == 40 for key in ("commit", "tree"))
        or any(any(c not in "0123456789abcdef" for c in before["main"][key]) for key in ("commit", "tree"))
        or not isinstance(before.get("known_issue"), dict)
        or set(before["known_issue"]) != {"number", "state", "state_reason", "title", "author", "created_at", "updated_at", "closed_at", "node_id", "is_pull_request"}
        or not isinstance(before.get("known_pr"), dict)
        or set(before["known_pr"]) != {"number", "state", "draft", "merged", "merged_at", "merge_commit_sha", "title", "author", "head_sha", "base_sha", "updated_at", "node_id"}
    ):
        raise RuntimeError("GATE_FAIL:v3 continuity binding drift")
    protected = continuity.get("protected_paths")
    closure_entries = continuity.get("closure_entries")
    toolchain_entries = continuity.get("toolchain")
    delta = continuity.get("delta")
    bindings = binding_surface.get("bindings")
    expected_count = binding_surface.get("total_count")
    canonical_delta = sorted(delta, key=lambda row: (row.get("path", ""), row.get("status", ""))) if isinstance(delta, list) and all(isinstance(row, dict) for row in delta) else None
    if (
        not isinstance(closure_entries, list) or not isinstance(toolchain_entries, list)
        or any(not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not entry["path"] for entry in closure_entries + toolchain_entries)
        or not isinstance(protected, list)
        or protected != sorted({entry["path"] for entry in closure_entries + toolchain_entries})
        or not all(isinstance(path, str) and path for path in protected)
        or not isinstance(delta, list) or continuity.get("delta_sha256") != canonical_sha256(delta)
        or any(
            not isinstance(row, dict) or set(row) != {"status", "path"}
            or row.get("status") not in {"A", "M", "D", "T", "U"}
            or not isinstance(row.get("path"), str) or not row["path"]
            or row["path"] in protected for row in delta
        )
        or delta != canonical_delta
        or len({(row["status"], row["path"]) for row in delta}) != len(delta)
        or isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 0
        or not isinstance(bindings, list) or len(bindings) != expected_count
        or before.get("repository_total_count") != 0
        or before.get("searches") != {
            'repo:google-deepmind/formal-conjectures "bondy_conjecture"': [4879],
            'repo:google-deepmind/formal-conjectures "BondyLongestCycles"': [],
            'repo:google-deepmind/formal-conjectures "2606.03696"': [4879],
        }
        or before.get("known_issue", {}).get("number") != 4858
        or before.get("known_issue", {}).get("state") != "closed"
        or before.get("known_issue", {}).get("state_reason") != "completed"
        or before.get("known_issue", {}).get("closed_at") != "2026-08-14T20:25:51Z"
        or before.get("known_issue", {}).get("is_pull_request") is not False
        or any(not isinstance(before["known_issue"].get(key), str) or not before["known_issue"][key] for key in ("title", "author", "created_at", "updated_at", "node_id"))
        or before.get("known_pr", {}).get("number") != 4879
        or before.get("known_pr", {}).get("state") != "closed"
        or before.get("known_pr", {}).get("draft") is not False
        or before.get("known_pr", {}).get("merged") is not True
        or before.get("known_pr", {}).get("merged_at") != "2026-08-14T20:25:50Z"
        or before.get("known_pr", {}).get("merge_commit_sha") != "8781428a922a53914450550218bf14be703d8d69"
        or any(not isinstance(before["known_pr"].get(key), str) or not before["known_pr"][key] for key in ("title", "author", "head_sha", "base_sha", "updated_at", "node_id"))
        or any(len(before["known_pr"][key]) != 40 or any(c not in "0123456789abcdef" for c in before["known_pr"][key]) for key in ("head_sha", "base_sha"))
    ):
        raise RuntimeError("GATE_FAIL:v3 delta or binding completeness drift")
    numbers: list[int] = []
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != PULL_BINDING_FIELDS:
            raise RuntimeError("GATE_FAIL:source attestation file binding schema drift")
        number = binding.get("number")
        paths = binding.get("changed_paths")
        changed_files = binding.get("changed_files")
        if (
            isinstance(number, bool)
            or not isinstance(number, int)
            or number <= 0
            or not isinstance(paths, list)
            or not all(isinstance(path, str) and path for path in paths)
            or paths != sorted(set(paths))
            or binding.get("changed_paths_sha256") != canonical_sha256(paths)
            or bool(set(paths).intersection(protected))
            or not isinstance(binding.get("node_id"), str) or not binding["node_id"]
            or binding.get("state") != "OPEN"
            or any(not isinstance(binding.get(key), str) or not binding[key] for key in ("title", "updated_at", "head_ref", "base_ref", "base_repo"))
            or any(not isinstance(binding.get(key), str) or len(binding[key]) != 40 or any(c not in "0123456789abcdef" for c in binding[key]) for key in ("head_sha", "base_sha"))
            or (binding.get("head_repo") is not None and (not isinstance(binding["head_repo"], str) or not binding["head_repo"]))
            or not isinstance(binding.get("draft"), bool)
            or isinstance(changed_files, bool) or not isinstance(changed_files, int) or changed_files < 0 or changed_files > len(paths)
            or len(paths) > 2 * changed_files
            or (changed_files == 0 and paths != [])
        ):
            raise RuntimeError("GATE_FAIL:source attestation file binding drift")
        numbers.append(number)
    if numbers != sorted(set(numbers)):
        raise RuntimeError("GATE_FAIL:source attestation file binding drift")
    commits = continuity.get("commits")
    if not isinstance(commits, list) or (continuity["live"]["commit"] != continuity["pinned"]["commit"] and not commits):
        raise RuntimeError("GATE_FAIL:continuity commit provenance missing")
    previous = continuity["pinned"]["commit"]
    commit_paths: set[str] = set()
    commit_oids: set[str] = set()
    for row in commits:
        if (
            not isinstance(row, dict) or set(row) != {"commit", "parents", "tree", "subject", "changed_paths"}
            or row.get("parents") != [previous]
            or any(not isinstance(row.get(key), str) or len(row[key]) != 40 or any(c not in "0123456789abcdef" for c in row[key]) for key in ("commit", "tree"))
            or not isinstance(row.get("subject"), str) or not isinstance(row.get("changed_paths"), list)
            or not row["changed_paths"] or row["changed_paths"] != sorted(set(row["changed_paths"]))
            or not all(isinstance(path, str) and path for path in row["changed_paths"])
        ):
            raise RuntimeError("GATE_FAIL:continuity commit chain drift")
        previous = row["commit"]
        if previous in commit_oids:
            raise RuntimeError("GATE_FAIL:duplicate continuity commit provenance")
        commit_oids.add(previous)
        commit_paths.update(row["changed_paths"])
    if previous != continuity["live"]["commit"] or (commits and commits[-1]["tree"] != continuity["live"]["tree"]) or any(row["path"] not in commit_paths for row in delta):
        raise RuntimeError("GATE_FAIL:continuity commit/delta provenance drift")
    telemetry = attestation.get("graphql_rate_limit_observations")
    if not isinstance(telemetry, dict) or set(telemetry) != {"before", "after"}:
        raise RuntimeError("GATE_FAIL:GraphQL quota audit missing")
    for rows in telemetry.values():
        if not isinstance(rows, list) or any(
            not isinstance(row, dict) or set(row) != {"cost", "remaining", "reset_at"}
            or isinstance(row["cost"], bool) or not isinstance(row["cost"], int)
            or isinstance(row["remaining"], bool) or not isinstance(row["remaining"], int)
            or row["cost"] <= 0 or row["remaining"] < 0
            or not isinstance(row["reset_at"], str) or not row["reset_at"] for row in rows
        ):
            raise RuntimeError("GATE_FAIL:GraphQL quota audit drift")
        if rows != sorted(rows, key=lambda row: (row["remaining"], row["cost"], row["reset_at"])):
            raise RuntimeError("GATE_FAIL:GraphQL quota audit noncanonical order")
    before_rate = telemetry["before"]
    after_rate = telemetry["after"]
    before_cost = sum(row["cost"] for row in before_rate)
    if (
        not before_rate or not after_rate
        or min(row["remaining"] for row in before_rate) < before_cost + 25
        or min(row["remaining"] for row in after_rate) < 25
    ):
        raise RuntimeError("GATE_FAIL:GraphQL quota reserve drift")
    hits = attestation.get("local_history_hits")
    identities = attestation.get("local_history_identities")
    if (
        not isinstance(hits, list) or hits != list(dict.fromkeys(hits))
        or not all(isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit) for commit in hits)
        or not isinstance(identities, list) or len(identities) != len(hits)
        or [row.get("commit") if isinstance(row, dict) else None for row in identities] != hits
    ):
        raise RuntimeError("GATE_FAIL:local contamination evidence drift")
    allowed_kinds = {"known_preflight", "known_repin_audit", "known_continuity_audit", "known_graph_rotation", "freeze_introducer"}
    for row in identities:
        if (
            not isinstance(row, dict) or set(row) != {"commit", "subject", "paths", "kind"}
            or row.get("kind") not in allowed_kinds or not isinstance(row.get("subject"), str) or not row["subject"]
            or not isinstance(row.get("paths"), list) or not row["paths"] or row["paths"] != sorted(set(row["paths"]))
            or not all(isinstance(path, str) and path for path in row["paths"])
        ):
            raise RuntimeError("GATE_FAIL:local contamination identity schema drift")
    by_kind = {row["kind"]: row for row in identities if row["kind"] != "freeze_introducer"}
    freeze_roots = (
        "scripts/prospective_bondy_", "scripts/test_bondy_",
        "results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/",
        ".github/workflows/bondy-longest-cycles-development.yml",
    )
    freeze_rows = [row for row in identities if row["kind"] == "freeze_introducer"]
    if (
        any(sum(row["kind"] == kind for row in identities) != 1 for kind in ("known_preflight", "known_repin_audit", "known_continuity_audit", "known_graph_rotation"))
        or by_kind.get("known_preflight", {}).get("commit") != "d22eb07173794848fd375b5675059946ee3860b5"
        or by_kind.get("known_repin_audit") != {"commit": "e17905b1d62048f43bab89e06625aebdcf280faf", "subject": "research: audit Bondy upstream repin", "paths": ["results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/upstream-drift-repin-audit.md"], "kind": "known_repin_audit"}
        or by_kind.get("known_continuity_audit") != {"commit": "c4d327479110cf51f2aae126d12e2fbc609c0921", "subject": "research: define Bondy tip continuity gate", "paths": ["results/expansion/live-search-2026-08-14/bondy-longest-cycles-development/tip-continuity-policy-audit.md"], "kind": "known_continuity_audit"}
        or by_kind.get("known_graph_rotation") != {"commit": "6a80fcdcb0489dc196162554cd4fec4f41ad2187", "subject": "research: record empty held-out graph rotation", "paths": ["results/expansion/live-search-2026-08-14/next-heldout-graph-rotation-strict-stop.md"], "kind": "known_graph_rotation"}
        or len(freeze_rows) != 4
        or any("scripts/prospective_bondy_gate.py" not in row["paths"] or not all(any(path.startswith(root) for root in freeze_roots) for path in row["paths"]) for row in freeze_rows)
    ):
        raise RuntimeError("GATE_FAIL:local contamination exact history drift")


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
        except (subprocess.TimeoutExpired, TimeoutError):
            timed_out = True
            output = terminate_and_reap(process)
        except BaseException:
            terminate_and_reap(process)
            raise
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


def run(args: argparse.Namespace) -> int:
    manifest = unlock(args)
    attestation_bytes = args.source_attestation.read_bytes()
    attestation = json.loads(attestation_bytes)
    if attestation_bytes != canonical_bytes(attestation):
        raise RuntimeError("GATE_FAIL:source attestation is not canonical JSON")
    validate_live_attestation(attestation, manifest)
    checked_campaign = {"commit": args.campaign_commit, "tree": git("show", "-s", "--format=%T", "HEAD")}
    if attestation["campaign"] != checked_campaign:
        raise RuntimeError("GATE_FAIL:live attestation campaign commit/tree drift")
    output_paths = (args.ledger, args.candidate, args.terminal)
    if len({path.resolve() for path in output_paths}) != len(output_paths):
        raise RuntimeError("GATE_FAIL:target output paths are not distinct")
    stale_outputs = [path for path in output_paths if path.exists()]
    if stale_outputs:
        raise RuntimeError("GATE_FAIL:target output path already exists:" + ",".join(str(path) for path in stale_outputs))
    handoff = {
        "schema": "bondy_campaign_handoff_v1",
        "campaign_commit": args.campaign_commit,
        "source_attestation_sha256": hashlib.sha256(attestation_bytes).hexdigest(),
    }
    started = time.monotonic()
    ledger = DurableLedger(args.ledger)
    ledger.append({"kind": "campaign_handoff", "handoff": handoff})
    ledger.append({"kind": "source_control", "record": construct.source_control()})
    applicable = 0
    evaluated = 0
    for row in construct.generate(manifest["grammar"]["row_limit"]):
        now = time.monotonic()
        if now - started >= INTERNAL_SEARCH_SECONDS:
            terminal = {"schema": "bondy_terminal_v3", "kind": "terminal", "status": "CAP_PREFIX", "handoff": handoff, "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
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
            terminal = {"schema": "bondy_terminal_v3", "kind": "terminal", "status": "CAP_PREFIX", "handoff": handoff, "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
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
                terminal = {"schema": "bondy_terminal_v3", "kind": "terminal", "status": "CAP_PREFIX", "handoff": handoff, "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
                ledger.seal()
                atomic_json(args.terminal, terminal)
                return 0
            candidate = {
                "schema": "bondy_candidate_v3",
                "kind": "candidate",
                "status": "CANDIDATE_FOUND",
                "handoff": handoff,
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
    terminal = {"schema": "bondy_terminal_v3", "kind": "terminal", "status": status, "handoff": handoff, "applicable": applicable, "evaluated": evaluated, "ledger_head": ledger.previous}
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
