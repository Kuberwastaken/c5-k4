#!/usr/bin/env python3
"""Reconstruct the frozen finite Equation 677 -> 255 SAT encoding.

This is a replay implementation of the clause order used by the completed
development selector.  It does not turn the historical n=5,6,7 runs into
hash-preserved runs: those CNF digests were not retained at evaluation time.
Do not treat a later replay as part of that original evidence ledger.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import threading
import time
from typing import Iterable


def variable(n: int, i: int, j: int, k: int) -> int:
    """DIMACS variable for the assertion i * j = k."""
    return 1 + (i * n + j) * n + k


def build_clauses(n: int) -> list[list[int]]:
    """Build clauses in the exact order used by the frozen selector."""
    if n < 1:
        raise ValueError("order must be positive")

    v = lambda i, j, k: variable(n, i, j, k)
    clauses: list[list[int]] = []

    # The operation is total and single-valued.
    for i in range(n):
        for j in range(n):
            values = [v(i, j, k) for k in range(n)]
            clauses.append(values)
            for a in range(n):
                for b in range(a + 1, n):
                    clauses.append([-values[a], -values[b]])

    # Equation 677 makes every left translation surjective, hence a
    # permutation in a finite magma.  Adding this derived property is a valid
    # redundant strengthening of the finite search.
    for i in range(n):
        for k in range(n):
            values = [v(i, j, k) for j in range(n)]
            clauses.append(values)
            for a in range(n):
                for b in range(a + 1, n):
                    clauses.append([-values[a], -values[b]])

    # Equation 677: y * (x * ((y * x) * y)) = x.
    for x, y, a, b, c in itertools.product(range(n), repeat=5):
        clauses.append([-v(y, x, a), -v(a, y, b), -v(x, b, c), v(y, c, x)])

    # Negate Equation 255 at x=0.  This is without loss of generality under a
    # relabelling of any finite countermodel and its failing element.
    for a, b in itertools.product(range(n), repeat=2):
        clauses.append([-v(0, 0, a), -v(a, 0, b), -v(b, 0, 0)])

    return clauses


def cnf_sha256(clauses: Iterable[Iterable[int]]) -> str:
    """Hash newline-joined clauses, with no header or trailing newline."""
    payload = "\n".join(" ".join(map(str, clause)) for clause in clauses).encode()
    return hashlib.sha256(payload).hexdigest()


def solve(n: int, cap_seconds: float, solver_name: str) -> int:
    try:
        from pysat.solvers import Solver
    except ImportError as exc:
        raise SystemExit("install python-sat==1.9.dev7 to replay the SAT solve") from exc

    clauses = build_clauses(n)
    print(json.dumps({
        "event": "cnf",
        "n": n,
        "variables": n**3,
        "clauses": len(clauses),
        "cnf_sha256": cnf_sha256(clauses),
        "serialization": "newline-joined clauses; no DIMACS header or trailing newline",
    }, sort_keys=True), flush=True)

    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        timer = threading.Timer(cap_seconds, solver.interrupt)
        timer.start()
        start = time.monotonic()
        try:
            result = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
        elapsed = time.monotonic() - start

        status = "SAT" if result is True else "UNSAT" if result is False else "TIMEOUT"
        print(json.dumps({
            "event": "solve_result",
            "n": n,
            "solver": solver_name,
            "cap_seconds": cap_seconds,
            "status": status,
            "wall_seconds": elapsed,
        }, sort_keys=True), flush=True)

        if result is True:
            model = {literal for literal in solver.get_model() if literal > 0}
            table = [
                [next(k for k in range(n) if variable(n, i, j, k) in model)
                 for j in range(n)]
                for i in range(n)
            ]
            payload = json.dumps(table, separators=(",", ":")).encode()
            print(json.dumps({
                "event": "countermodel",
                "n": n,
                "table": table,
                "table_sha256": hashlib.sha256(payload).hexdigest(),
            }, sort_keys=True), flush=True)
            return 1
        return 0 if result is False else 124


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", required=True, type=int)
    parser.add_argument("--cap-seconds", type=float, default=60.0)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()
    if not 0 < args.cap_seconds <= 60:
        parser.error("cap must lie in (0,60]")
    return solve(args.n, args.cap_seconds, args.solver)


if __name__ == "__main__":
    raise SystemExit(main())
