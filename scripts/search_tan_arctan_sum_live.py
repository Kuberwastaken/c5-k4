#!/usr/bin/env python3
"""Frozen three-arm DEVELOPMENT search for tan_arctan_sum_not_integer.

No target value is evaluated by importing this module.  Execution requires the
frozen manifest, passes the arithmetic sanity gate, and then works entirely in
integer arithmetic.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Mapping, Sequence


sys.set_int_max_str_digits(0)

ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
INTERNAL_STOP_SECONDS = 54.0
EXTERNAL_STOP_SECONDS = 60
UPSTREAM_COMMIT = "942fb149e782a56c2719c543ab58e093f733acb4"
UPSTREAM_BLOB = "7ddef467be2c61f20e99945685fe9e2e6bbe2be8"
UPSTREAM_DECLARATION = "Arxiv.«2607.05739».tan_arctan_sum_not_integer"
FREEZE_BASE_COMMIT = "c936765104ee4354e7e1c0809a32761e2c377ecb"
LEDGER_SCHEMA = "c5k4-tan-arctan-sum-live-jsonl-1.0"
TERMINAL_SCHEMA = "c5k4-tan-arctan-sum-live-terminal-1.0"
MANIFEST_SCHEMA = "c5k4-tan-arctan-sum-live-manifest-1.0"
ZERO_SHA256 = "0" * 64
TERMINAL_REASONS = {
    "DOMAIN_EXHAUSTED",
    "PROPOSAL_LIMIT",
    "SEARCH_EXHAUSTED",
    "DEADLINE_PREFIX",
    "CERTIFICATE_FOUND",
    "SANITY_GATE_FAILED",
    "WORKER_ERROR",
}

# Remark 3.3 of arXiv:2607.05739v1 records E intersect [5, 60000]
# as the finite illustration of Proposition 3.2.
PAPER_EXCEPTIONAL_CATALOGUE = (
    15, 17, 80, 82, 395, 397, 1904, 1906, 9163, 9165, 44086, 44088,
)
SEARCH_START = 60_001
SEARCH_MAX_N = 250_000
GENERIC_SAMPLE_BITS = 4  # exactly 1/16 of eligible non-wall indices
GENERIC_SEED = 0x54414E4152435441
PROGRESS_INTERVAL = 1_000

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT / "results" / "expansion" / "live-search-2026-08-14"
    / "tan-arctan-sum-manifest.json"
)


class SearchError(ValueError):
    """Raised when a frozen-contract or exact-arithmetic check fails closed."""


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def integer_sha256(value: int) -> str:
    sign = b"-" if value < 0 else b"+"
    magnitude = abs(value)
    raw = magnitude.to_bytes(max(1, (magnitude.bit_length() + 7) // 8), "big")
    return hashlib.sha256(b"c5k4-signed-integer-v1\0" + sign + raw).hexdigest()


def load_and_verify_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != MANIFEST_SCHEMA:
        raise SearchError("wrong tan-arctan manifest schema")
    upstream = value.get("upstream", {})
    if upstream.get("commit") != UPSTREAM_COMMIT or upstream.get("blob") != UPSTREAM_BLOB:
        raise SearchError("manifest does not pin the frozen upstream source")
    if upstream.get("declaration") != UPSTREAM_DECLARATION:
        raise SearchError("manifest declaration drift")
    if value.get("freeze_base_commit") != FREEZE_BASE_COMMIT:
        raise SearchError("c5-k4 freeze-base commit drift")
    if value.get("arms") != list(ARMS):
        raise SearchError("frozen arm list changed")
    if value.get("internal_stop_seconds") != int(INTERNAL_STOP_SECONDS):
        raise SearchError("internal stop changed")
    if value.get("external_stop_seconds") != EXTERNAL_STOP_SECONDS:
        raise SearchError("external stop changed")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise SearchError("artifact lock is absent")
    for artifact in artifacts:
        artifact_path = REPO_ROOT / str(artifact.get("path", ""))
        if not artifact_path.is_file() or sha256_file(artifact_path) != artifact.get("sha256"):
            raise SearchError(f"frozen artifact digest mismatch: {artifact_path}")
    return value


@dataclass(frozen=True)
class GaussianState:
    n: int
    a: int
    b: int
    omega: int


def initial_state() -> GaussianState:
    return GaussianState(0, 1, 0, 1)


def recurrence_step(state: GaussianState) -> GaussianState:
    """Multiply A+iB by 1+i(n+1), and update its exact norm."""

    k = state.n + 1
    return GaussianState(
        k,
        state.a - k * state.b,
        k * state.a + state.b,
        state.omega * (1 + k * k),
    )


def _balanced_gaussian_product(low: int, high: int) -> tuple[int, int]:
    """Independent balanced multiplication of (1+i*k) over an interval."""

    if low > high:
        return 1, 0
    if low == high:
        return 1, low
    middle = (low + high) // 2
    left_a, left_b = _balanced_gaussian_product(low, middle)
    right_a, right_b = _balanced_gaussian_product(middle + 1, high)
    return (
        left_a * right_a - left_b * right_b,
        left_a * right_b + left_b * right_a,
    )


def direct_gaussian_product(n: int) -> GaussianState:
    if n < 0:
        raise SearchError("negative product endpoint")
    a, b = _balanced_gaussian_product(1, n)
    return GaussianState(n, a, b, a * a + b * b)


def reduced_denominator(a: int, b: int) -> int:
    """Denominator of B/A in lowest terms; zero denotes the tangent pole."""

    if a == 0:
        return 0
    return abs(a) // math.gcd(abs(a), abs(b))


def is_integer_value(a: int, b: int) -> bool:
    # Since A^2+B^2 is positive, A=0 implies B!=0 and hence A does not divide B.
    return reduced_denominator(a, b) == 1


def is_exceptional_wall(n: int, a: int, b: int) -> bool:
    """Exact form of |B/A| > n/2+1, treating A=0 as a pole."""

    return a == 0 or 2 * abs(b) > (n + 2) * abs(a)


def database_sanity_gate() -> dict[str, Any]:
    """Use only the four documented non-target values n=1,...,4."""

    expected = {
        0: (1, 0, 1),
        1: (1, 1, 2),
        2: (-1, 3, 10),
        3: (-10, 0, 100),
        4: (-10, -40, 1700),
    }
    state = initial_state()
    rows: list[dict[str, Any]] = []
    for n in range(0, 5):
        if n:
            state = recurrence_step(state)
        direct = direct_gaussian_product(n)
        if state != direct or (state.a, state.b, state.omega) != expected[n]:
            raise SearchError(f"sanity recurrence mismatch at n={n}")
        if state.a * state.a + state.b * state.b != state.omega:
            raise SearchError(f"sanity norm mismatch at n={n}")
        if n and not is_integer_value(state.a, state.b):
            raise SearchError(f"documented integer control failed at n={n}")
        rows.append({"n": n, "a": state.a, "b": state.b, "omega": state.omega})
    if reduced_denominator(6, 15) != 2 or is_integer_value(6, 15):
        raise SearchError("synthetic nonintegral divisibility control failed")
    if not is_integer_value(-7, 21):
        raise SearchError("synthetic integral divisibility control failed")
    return {
        "controls": rows,
        "documented_integer_indices": [1, 2, 3, 4],
        "synthetic_noninteger": {"a": 6, "b": 15, "reduced_denominator": 2},
        "target_values_evaluated": 0,
    }


@dataclass
class Counters:
    recurrence_steps: int = 0
    proposals: int = 0
    exact_divisibility_tests: int = 0
    certificates: int = 0


class DurableLedger:
    def __init__(self, path: Path, arm: str):
        if arm not in ARMS:
            raise SearchError("arm is outside the frozen manifest")
        if path.exists() and path.stat().st_size:
            raise SearchError("ledger must be a fresh file")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.arm = arm
        self.started = time.monotonic()
        self.sequence = 0
        self.previous = ZERO_SHA256
        self.counters = Counters()
        self.emit("checkpoint", {"label": "started"})

    def emit(self, kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        row: dict[str, Any] = {
            "schema": LEDGER_SCHEMA,
            "kind": kind,
            "arm": self.arm,
            "sequence": self.sequence,
            "elapsed_milliseconds": int((time.monotonic() - self.started) * 1000),
            "counters": asdict(self.counters),
            "previous_row_sha256": self.previous,
            **dict(payload),
        }
        row["row_sha256"] = hashlib.sha256(canonical_json(row)).hexdigest()
        raw = canonical_json(row)
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            view = memoryview(raw)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:  # pragma: no cover
                    raise OSError("short durable write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.previous = row["row_sha256"]
        self.sequence += 1
        return row


def write_terminal(path: Path, ledger: DurableLedger, reason: str, cursor: Mapping[str, Any]) -> dict[str, Any]:
    if reason not in TERMINAL_REASONS:
        raise SearchError("unknown terminal reason")
    terminal_row = ledger.emit("terminal", {"terminal_reason": reason, "cursor": dict(cursor)})
    receipt = {
        "schema": TERMINAL_SCHEMA,
        "arm": ledger.arm,
        "terminal_reason": reason,
        "cursor": dict(cursor),
        "counters": asdict(ledger.counters),
        "final_row_sha256": terminal_row["row_sha256"],
    }
    raw = canonical_json(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:  # pragma: no cover
                raise OSError("short terminal write")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return receipt


def generic_selected(n: int) -> bool:
    raw = f"{GENERIC_SEED}:{n}".encode("ascii")
    value = int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")
    return value & ((1 << GENERIC_SAMPLE_BITS) - 1) == 0


def candidate_certificate(state: GaussianState, previous: GaussianState) -> dict[str, Any]:
    if state != recurrence_step(previous):
        raise SearchError("candidate predecessor does not replay")
    replay = direct_gaussian_product(state.n)
    if replay != state:
        raise SearchError("candidate failed independent direct-product replay")
    if not is_integer_value(state.a, state.b) or state.a == 0:
        raise SearchError("certificate requested for a non-candidate")
    m = state.b // state.a
    if state.a * m != state.b:
        raise SearchError("quotient is not an exact divisibility witness")
    if state.a * state.a + state.b * state.b != state.omega:
        raise SearchError("candidate norm identity failed")
    if state.a * state.a * (1 + m * m) != state.omega:
        raise SearchError("candidate integrality/norm identity failed")
    return {
        "n": state.n,
        "a_n": str(state.a),
        "b_n": str(state.b),
        "m": str(m),
        "a_previous": str(previous.a),
        "b_previous": str(previous.b),
        "omega_n": str(state.omega),
        "identities": {
            "a_n_eq_a_previous_minus_n_b_previous": True,
            "b_n_eq_n_a_previous_plus_b_previous": True,
            "b_n_eq_m_a_n": True,
            "omega_n_eq_a_n_sq_plus_b_n_sq": True,
            "omega_n_eq_a_n_sq_times_one_plus_m_sq": True,
        },
        "independent_direct_product_replay": True,
    }


def compact_evaluation(state: GaussianState, provenance: Mapping[str, Any]) -> dict[str, Any]:
    denominator = reduced_denominator(state.a, state.b)
    return {
        "n": state.n,
        "a_sha256": integer_sha256(state.a),
        "b_sha256": integer_sha256(state.b),
        "omega_sha256": integer_sha256(state.omega),
        "a_bit_length": abs(state.a).bit_length(),
        "b_bit_length": abs(state.b).bit_length(),
        "reduced_denominator_bit_length": denominator.bit_length(),
        "reduced_denominator_sha256": integer_sha256(denominator),
        "is_integer_value": denominator == 1,
        "is_exceptional_wall": is_exceptional_wall(state.n, state.a, state.b),
        "provenance": dict(provenance),
    }


def advance_to(
    state: GaussianState,
    target: int,
    ledger: DurableLedger,
    deadline: float,
) -> tuple[GaussianState, GaussianState | None, bool]:
    previous: GaussianState | None = None
    while state.n < target:
        if time.monotonic() >= deadline:
            return state, previous, False
        previous = state
        state = recurrence_step(state)
        ledger.counters.recurrence_steps += 1
        if state.n % PROGRESS_INTERVAL == 0:
            ledger.emit("progress", {"n": state.n, "a_sha256": integer_sha256(state.a), "b_sha256": integer_sha256(state.b)})
    return state, previous, True


def evaluate_and_record(
    state: GaussianState,
    previous: GaussianState,
    ledger: DurableLedger,
    provenance: Mapping[str, Any],
) -> bool:
    ledger.counters.proposals += 1
    ledger.counters.exact_divisibility_tests += 1
    payload = compact_evaluation(state, provenance)
    if payload["is_integer_value"]:
        # Durably preserve the finite witness before the potentially longer
        # independent balanced-product replay.  A hard kill can then lose only
        # the replay/terminal suffix, never the observed exact divisibility.
        m = state.b // state.a
        ledger.emit("candidate_prefix", {
            "n": state.n,
            "a_n": str(state.a),
            "b_n": str(state.b),
            "m": str(m),
            "a_previous": str(previous.a),
            "b_previous": str(previous.b),
            "omega_n": str(state.omega),
            "b_n_eq_m_a_n": state.b == m * state.a,
        })
        payload["certificate"] = candidate_certificate(state, previous)
        ledger.counters.certificates += 1
    ledger.emit("evaluated_index", payload)
    return bool(payload["is_integer_value"])


def run_catalogue(ledger: DurableLedger, deadline: float) -> tuple[str, dict[str, Any]]:
    state = initial_state()
    for catalogue_index, n in enumerate(PAPER_EXCEPTIONAL_CATALOGUE):
        state, previous, complete = advance_to(state, n, ledger, deadline)
        if not complete:
            return "DEADLINE_PREFIX", {"catalogue_index": catalogue_index, "next_n": n, "reached_n": state.n}
        assert previous is not None
        if evaluate_and_record(state, previous, ledger, {"generator": "paper_exceptional_catalogue", "catalogue_index": catalogue_index}):
            return "CERTIFICATE_FOUND", {"catalogue_index": catalogue_index, "n": n}
    return "DOMAIN_EXHAUSTED", {"catalogue_size": len(PAPER_EXCEPTIONAL_CATALOGUE)}


def run_generic(ledger: DurableLedger, deadline: float) -> tuple[str, dict[str, Any]]:
    state = initial_state()
    state, _, complete = advance_to(state, SEARCH_START - 1, ledger, deadline)
    if not complete:
        return "DEADLINE_PREFIX", {"next_n": SEARCH_START, "reached_n": state.n}
    for n in range(SEARCH_START, SEARCH_MAX_N + 1):
        state, previous, complete = advance_to(state, n, ledger, deadline)
        if not complete:
            return "DEADLINE_PREFIX", {"next_n": n, "reached_n": state.n}
        assert previous is not None
        if is_exceptional_wall(n, state.a, state.b) or not generic_selected(n):
            continue
        if evaluate_and_record(state, previous, ledger, {"generator": "seeded_nonwall_sample", "seed": GENERIC_SEED, "sample_bits": GENERIC_SAMPLE_BITS}):
            return "CERTIFICATE_FOUND", {"n": n}
    return "PROPOSAL_LIMIT", {"next_n": SEARCH_MAX_N + 1, "maximum_n": SEARCH_MAX_N}


def run_wall_navigation(ledger: DurableLedger, deadline: float) -> tuple[str, dict[str, Any]]:
    state = initial_state()
    state, _, complete = advance_to(state, SEARCH_START - 1, ledger, deadline)
    if not complete:
        return "DEADLINE_PREFIX", {"next_n": SEARCH_START, "reached_n": state.n}
    for n in range(SEARCH_START, SEARCH_MAX_N + 1):
        state, previous, complete = advance_to(state, n, ledger, deadline)
        if not complete:
            return "DEADLINE_PREFIX", {"next_n": n, "reached_n": state.n}
        assert previous is not None
        if not is_exceptional_wall(n, state.a, state.b):
            continue
        if evaluate_and_record(state, previous, ledger, {"generator": "exact_exceptional_wall", "wall_inequality": "2*abs(B_n)>(n+2)*abs(A_n) or A_n=0"}):
            return "CERTIFICATE_FOUND", {"n": n}
    return "SEARCH_EXHAUSTED", {"next_n": SEARCH_MAX_N + 1, "maximum_n": SEARCH_MAX_N}


def run_worker(arm: str, ledger_path: Path, terminal_path: Path, manifest_path: Path) -> None:
    load_and_verify_manifest(manifest_path)
    ledger = DurableLedger(ledger_path, arm)
    try:
        try:
            gate = database_sanity_gate()
        except Exception as exc:
            write_terminal(terminal_path, ledger, "SANITY_GATE_FAILED", {"exception_type": type(exc).__name__, "message": str(exc)})
            raise
        ledger.emit("database_sanity_gate", gate)
        deadline = ledger.started + INTERNAL_STOP_SECONDS
        if arm == "CATALOGUE":
            reason, cursor = run_catalogue(ledger, deadline)
        elif arm == "GENERIC":
            reason, cursor = run_generic(ledger, deadline)
        else:
            reason, cursor = run_wall_navigation(ledger, deadline)
        write_terminal(terminal_path, ledger, reason, cursor)
    except Exception as exc:
        if not terminal_path.exists():
            write_terminal(terminal_path, ledger, "WORKER_ERROR", {"exception_type": type(exc).__name__, "message": str(exc)})
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--internal-seconds", type=float, default=INTERNAL_STOP_SECONDS)
    args = parser.parse_args(argv)
    if args.internal_seconds != INTERNAL_STOP_SECONDS:
        parser.error(f"--internal-seconds is frozen at {INTERNAL_STOP_SECONDS:g}")
    try:
        run_worker(args.arm, args.ledger, args.terminal, args.manifest)
    except (OSError, SearchError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
