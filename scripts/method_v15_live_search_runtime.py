#!/usr/bin/env python3
"""Small scientific-output layer for one Method v1.5 live-search tree.

The production triplet contract remains authoritative for arm names, canonical
JSON, and the 60 second wall cap.  This module adds only the semantics that an
actual search worker needs: exact graph canonicalization through nauty
``labelg``, uniform counters, durable JSONL rows, and a hard process-group cap.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, Sequence

import networkx as nx


HERE = Path(__file__).resolve().parent
ZERO_SHA256 = "0" * 64
SCHEMA = "c5k4-method-v1.5-live-search-jsonl-1.0"
COUNTER_FIELDS = (
    "proposed",
    "canonical_unique",
    "hypothesis_survivor",
    "exact_evaluated",
    "objective_scored",
)


def _load_triplet_runtime() -> Any:
    path = HERE / "method_v15_triplet_production_runtime.py"
    spec = importlib.util.spec_from_file_location("c5k4_v15_live_triplet_runtime", path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError("cannot load Method v1.5 triplet runtime")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TRIPLET_RUNTIME = _load_triplet_runtime()
ARMS = TRIPLET_RUNTIME.ARMS
WALL_CAP_SECONDS = TRIPLET_RUNTIME.WALL_CAP_SECONDS
canonical_bytes = TRIPLET_RUNTIME.canonical_bytes


class LiveSearchRuntimeError(ValueError):
    pass


@dataclass(frozen=True)
class CanonicalGraph:
    graph6: str
    sha256: str


class LabelgCanonicalizer:
    """Produce an exact, label-independent graph6 identity or fail closed."""

    def __init__(self, executable: Path, *, timeout_seconds: float = 10.0):
        self.executable = executable.resolve()
        self.timeout_seconds = timeout_seconds
        if not self.executable.is_file() or not os.access(self.executable, os.X_OK):
            raise LiveSearchRuntimeError(f"labelg is not executable: {self.executable}")

    @classmethod
    def from_environment(cls) -> "LabelgCanonicalizer":
        raw = os.environ.get("C5K4_LABELG")
        if not raw:
            raise LiveSearchRuntimeError("C5K4_LABELG must name the frozen nauty labelg executable")
        return cls(Path(raw))

    def canonicalize(self, graph: nx.Graph) -> CanonicalGraph:
        if graph.is_directed() or graph.is_multigraph():
            raise LiveSearchRuntimeError("only finite simple undirected graphs are canonicalized")
        relabeled = nx.convert_node_labels_to_integers(graph, ordering="default")
        encoded = nx.to_graph6_bytes(relabeled, header=False).decode("ascii").strip()
        try:
            completed = subprocess.run(
                [str(self.executable), "-q"],
                input=(encoded + "\n").encode("ascii"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=self.timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise LiveSearchRuntimeError(f"exact labelg canonicalization failed: {exc}") from exc
        lines = [line.strip() for line in completed.stdout.decode("ascii", "strict").splitlines() if line.strip()]
        if completed.returncode != 0 or len(lines) != 1:
            detail = completed.stderr.decode("utf-8", "replace").strip()
            raise LiveSearchRuntimeError(
                f"labelg rejected graph (exit {completed.returncode}, rows {len(lines)}): {detail}"
            )
        canonical = lines[0]
        try:
            replay = nx.from_graph6_bytes(canonical.encode("ascii"))
        except Exception as exc:
            raise LiveSearchRuntimeError("labelg emitted invalid graph6") from exc
        # This check prevents a wrong binary or wrapper from silently becoming
        # the scientific identity authority.  No WL/hash proxy is accepted.
        if not nx.is_isomorphic(relabeled, replay):
            raise LiveSearchRuntimeError("labelg output is not isomorphic to its input")
        digest = hashlib.sha256(b"c5k4-exact-canonical-graph6-v1\0" + canonical.encode("ascii")).hexdigest()
        return CanonicalGraph(canonical, digest)


@dataclass
class UsefulWorkCounters:
    proposed: int = 0
    canonical_unique: int = 0
    hypothesis_survivor: int = 0
    exact_evaluated: int = 0
    objective_scored: int = 0


class ScientificJsonl:
    """Append one hash-chained row with flush+fsync for every emit call."""

    def __init__(self, path: Path, arm: str, tree_index: int):
        if arm not in ARMS or type(tree_index) is not int or not 0 <= tree_index < 8:
            raise LiveSearchRuntimeError("arm/tree identity is outside the Method v1.5 triplet")
        self.path = path.resolve()
        self.arm = arm
        self.tree_index = tree_index
        self.tree_id = f"{arm}-{tree_index}"
        self.started = time.monotonic()
        self.cpu_started = time.process_time()
        self.sequence = 0
        self.previous = ZERO_SHA256
        self.counters = UsefulWorkCounters()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and self.path.stat().st_size:
            raise LiveSearchRuntimeError("scientific JSONL must be a fresh per-tree file")
        self.checkpoint("started")

    @classmethod
    def from_environment(cls) -> "ScientificJsonl":
        try:
            return cls(
                Path(os.environ["C5K4_SCIENTIFIC_JSONL"]),
                os.environ["C5K4_ARM"],
                int(os.environ["C5K4_TREE_INDEX"]),
            )
        except (KeyError, ValueError) as exc:
            raise LiveSearchRuntimeError("live-search environment is incomplete") from exc

    def _append(self, kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        row: dict[str, Any] = {
            "schema": SCHEMA,
            "kind": kind,
            "arm": self.arm,
            "tree_id": self.tree_id,
            "sequence": self.sequence,
            "elapsed_milliseconds": int((time.monotonic() - self.started) * 1000),
            "cpu_milliseconds": int((time.process_time() - self.cpu_started) * 1000),
            "counters": asdict(self.counters),
            "previous_row_sha256": self.previous,
            **dict(payload),
        }
        row["row_sha256"] = hashlib.sha256(canonical_bytes(row)).hexdigest()
        raw = canonical_bytes(row)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            view = memoryview(raw)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:  # pragma: no cover
                    raise OSError("short JSONL write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.previous = row["row_sha256"]
        self.sequence += 1
        return row

    def checkpoint(self, label: str) -> dict[str, Any]:
        if not label:
            raise LiveSearchRuntimeError("checkpoint label is empty")
        return self._append("checkpoint", {"label": label})

    def evaluated_candidate(
        self,
        canonical: CanonicalGraph,
        *,
        objective: int | str | None,
        crossing: bool | None,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.counters.exact_evaluated += 1
        if objective is not None:
            if isinstance(objective, bool) or not isinstance(objective, (int, str)):
                raise LiveSearchRuntimeError("exact objective must be an integer, exact string, or null")
            if type(crossing) is not bool:
                raise LiveSearchRuntimeError("a scored objective requires an exact crossing boolean")
            self.counters.objective_scored += 1
        return self._append("evaluated_candidate", {
            "canonical_graph6": canonical.graph6,
            "canonical_sha256": canonical.sha256,
            "objective": objective,
            "crossing": crossing,
            "payload": dict(payload or {}),
        })

    def finish(self) -> dict[str, Any]:
        return self._append("summary", {"status": "COMPLETED"})


Hypothesis = Callable[[nx.Graph], bool]
Evaluator = Callable[[nx.Graph], Mapping[str, Any]]


class GraphSearchRecorder:
    """Apply the five counter definitions uniformly around a target evaluator."""

    def __init__(self, ledger: ScientificJsonl, canonicalizer: LabelgCanonicalizer):
        self.ledger = ledger
        self.canonicalizer = canonicalizer
        self._seen: set[str] = set()

    def evaluate(self, graph: nx.Graph, hypothesis: Hypothesis, evaluator: Evaluator) -> dict[str, Any] | None:
        self.ledger.counters.proposed += 1
        canonical = self.canonicalizer.canonicalize(graph)
        if canonical.sha256 in self._seen:
            return None
        self._seen.add(canonical.sha256)
        self.ledger.counters.canonical_unique += 1
        survived = hypothesis(graph)
        if type(survived) is not bool:
            raise LiveSearchRuntimeError("hypothesis adapter must return bool")
        if not survived:
            return None
        self.ledger.counters.hypothesis_survivor += 1
        result = dict(evaluator(graph))
        if "objective" not in result or "crossing" not in result:
            raise LiveSearchRuntimeError("evaluator must return objective and crossing")
        objective = result.pop("objective")
        crossing = result.pop("crossing")
        return self.ledger.evaluated_candidate(
            canonical, objective=objective, crossing=crossing, payload=result
        )


@dataclass(frozen=True)
class ArmProcessResult:
    returncode: int
    timed_out: bool
    wall_milliseconds: int


def run_arm_process(
    command: Sequence[str],
    *,
    arm: str,
    tree_index: int,
    output: Path,
    labelg: Path,
    cap_seconds: float = WALL_CAP_SECONDS,
) -> ArmProcessResult:
    """Run and, at the deadline, kill the complete worker process group."""

    if arm not in ARMS or type(tree_index) is not int or not 0 <= tree_index < 8 or not command:
        raise LiveSearchRuntimeError("invalid arm command")
    output = output.resolve()
    if output.exists():
        raise LiveSearchRuntimeError("arm output must not pre-exist; stale scientific rows are forbidden")
    output.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update({
        "C5K4_ARM": arm,
        "C5K4_TREE_INDEX": str(tree_index),
        "C5K4_SCIENTIFIC_JSONL": str(output),
        "C5K4_LABELG": str(labelg.resolve()),
        "C5K4_WALL_CAP_SECONDS": str(WALL_CAP_SECONDS),
    })
    started = time.monotonic()
    process = subprocess.Popen(
        list(command), env=env, start_new_session=True,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    timed_out = False
    try:
        returncode = process.wait(timeout=cap_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            returncode = process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            returncode = process.wait()
    elapsed = int((time.monotonic() - started) * 1000)
    return ArmProcessResult(returncode, timed_out, elapsed)


def _run_cli(args: argparse.Namespace) -> int:
    if args.wall_seconds != WALL_CAP_SECONDS:
        raise LiveSearchRuntimeError("the Method v1.5 live cap is fixed at exactly 60 seconds")
    result = run_arm_process(
        args.command, arm=args.arm, tree_index=args.tree_index,
        output=args.output, labelg=args.labelg,
    )
    from lint_method_v15_live_search_output import lint_jsonl

    findings = lint_jsonl(
        args.output, allow_timeout_prefix=result.timed_out, labelg=args.labelg
    )
    report = {
        "arm": args.arm,
        "tree_id": f"{args.arm}-{args.tree_index}",
        "returncode": result.returncode,
        "timed_out": result.timed_out,
        "wall_milliseconds": result.wall_milliseconds,
        "scientific_output_valid": not findings,
        "findings": [finding.as_dict() for finding in findings],
    }
    sys.stdout.buffer.write(canonical_bytes(report))
    return 0 if not findings and (result.returncode == 0 or result.timed_out) else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="subcommand", required=True)
    run = sub.add_parser("run", help="run one real arm tree under the hard cap")
    run.add_argument("--arm", choices=ARMS, required=True)
    run.add_argument("--tree-index", type=int, choices=range(8), required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--labelg", type=Path, required=True)
    run.add_argument("--wall-seconds", type=int, default=WALL_CAP_SECONDS)
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    try:
        return _run_cli(args)
    except LiveSearchRuntimeError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
