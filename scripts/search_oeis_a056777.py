#!/usr/bin/env python3
"""Exact factorization-first search of the three A056777 escape strata."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import signal
import time
from contextlib import contextmanager

from prepare_oeis_a056777_gate import MANIFEST, M, sha, verify

ZERO = "0" * 64


class Deadline(Exception):
    pass


def alarm_handler(_signum, _frame):
    raise Deadline()


@contextmanager
def block_alarm():
    """Defer SIGALRM until a completed state transition is fully durable."""
    old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)


def error_receipt(exc: BaseException) -> dict:
    message = str(exc)[:1000]
    return {"type": type(exc).__name__, "message": message,
            "message_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest()}


class Ledger:
    def __init__(self, path: pathlib.Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path; self.stream = path.open("x", encoding="ascii")
        self.seq = 0; self.previous = ZERO

    def append(self, payload: dict) -> None:
        with block_alarm():
            row = dict(payload); row["seq"] = self.seq; row["previous_row_sha256"] = self.previous
            body = json.dumps(row, sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(body.encode("ascii")).hexdigest(); row["row_sha256"] = digest
            self.stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            self.stream.flush(); os.fsync(self.stream.fileno())
            self.previous = digest; self.seq += 1

    def close(self) -> None:
        self.stream.close()


def atomic_json(path: pathlib.Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="ascii") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":")); stream.write("\n")
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def is_prime(n: int) -> bool:
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: s += 1; d //= 2
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0: continue
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True


def brent(n: int) -> int:
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3
    for c in (1, 3, 5, 7, 11, 13, 17, 19, 23):
        y, r, q, m, g = 2, 1, 1, 64, 1
        while g == 1:
            x = y
            for _ in range(r): y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n; q = q * abs(x - y) % n
                g = math.gcd(q, n); k += m
            r *= 2
        if g == n:
            while True:
                ys = (ys * ys + c) % n; g = math.gcd(abs(x - ys), n)
                if g > 1: break
        if g != n: return g
    raise RuntimeError(f"factorization failed for {n}")


def factor(n: int) -> list[tuple[int, int]]:
    flat = []
    def split(value: int) -> None:
        if value == 1: return
        if is_prime(value): flat.append(value); return
        divisor = brent(value); split(divisor); split(value // divisor)
    split(n); flat.sort(); result = []
    for p in flat:
        if result and result[-1][0] == p: result[-1] = (p, result[-1][1] + 1)
        else: result.append((p, 1))
    return result


def arithmetic(factors: list[tuple[int, int]]) -> tuple[int, int]:
    phi = sigma = 1
    for p, e in factors:
        phi *= (p - 1) * p ** (e - 1)
        sigma *= (p ** (e + 1) - 1) // (p - 1)
    return phi, sigma


def prime_quadruple_witness(n: int) -> int | None:
    root = math.isqrt(n + 16)
    if root * root != n + 16 or root < 4: return None
    p = root - 4
    if p * (p + 8) != n: return None
    return p if all(is_prime(p + gap) for gap in (0, 2, 6, 8)) else None


def certificate(arm: str, shard: int, commit: str, gate_sha: str, n: int,
                fn: list[tuple[int, int]], fn12: list[tuple[int, int]]) -> dict | None:
    phi, sigma = arithmetic(fn); phi12, sigma12 = arithmetic(fn12)
    if phi12 != phi + 12 or sigma12 != sigma + 12: return None
    witness = prime_quadruple_witness(n)
    if witness is not None: return None
    return {
        "schema": "oeis-a056777-certificate-v1", "campaign_commit": commit,
        "source_commit": M["formal_conjectures"]["commit"], "manifest_sha256": sha(MANIFEST),
        "gate_attestation_sha256": gate_sha, "declaration": M["formal_conjectures"]["declaration"],
        "arm": arm, "shard": shard, "n": n,
        "factors_n": [list(x) for x in fn], "factors_n_plus_12": [list(x) for x in fn12],
        "phi_n": phi, "phi_n_plus_12": phi12, "sigma_n": sigma, "sigma_n_plus_12": sigma12,
        "composite_n": True, "comes_from_prime_quadruple": False,
    }


def first_primes(count: int) -> list[int]:
    limit = 32
    while True:
        sieve = bytearray(b"\x01") * (limit + 1); sieve[:2] = b"\x00\x00"
        for p in range(2, math.isqrt(limit) + 1):
            if sieve[p]: sieve[p*p:limit+1:p] = b"\x00" * (((limit-p*p)//p)+1)
        primes = [i for i, flag in enumerate(sieve) if flag]
        if len(primes) >= count: return primes[:count]
        limit *= 2


def prime_window(start: int, count: int):
    value = max(2, start)
    if value > 2 and value % 2 == 0: value += 1
    found = 0
    while found < count:
        if is_prime(value):
            yield found, value; found += 1
        value = 3 if value == 2 else value + 2


def floor_root(n: int, exponent: int) -> int:
    low, high = 1, 2
    while high ** exponent <= n: high *= 2
    while low + 1 < high:
        middle = (low + high) // 2
        if middle ** exponent <= n: low = middle
        else: high = middle
    return low


def arm_states(arm: str, shard: int):
    """Yield canonical (coordinate,n,factors) in the frozen tuple-domain order."""
    spec = M["arms"][arm]; lower, upper = M["value_minimum"], M["value_maximum"]
    if arm == "PURE_PRIME_POWER":
        global_ordinal = 0
        for exponent in range(spec["exponent_min"], spec["exponent_max"] + 1):
            lo = floor_root(lower - 1, exponent) + 1; hi = floor_root(upper, exponent)
            offset = 0; value = max(2, lo)
            if value > 2 and value % 2 == 0: value += 1
            while value <= hi:
                if is_prime(value):
                    if global_ordinal % M["shards"] == shard:
                        yield {"global_ordinal": global_ordinal, "exponent": exponent, "p_offset_in_root_interval": offset, "p": value}, value ** exponent, [(value, exponent)]
                    offset += 1
                    global_ordinal += 1
                value = 3 if value == 2 else value + 2
        return
    primes = first_primes(spec["p_rank_first"] + spec["p_rank_count"] - 1)
    first = spec["p_rank_first"]
    for local_rank in range(spec["p_rank_count"]):
        p_rank = first + local_rank
        if (p_rank - first) % M["shards"] != shard: continue
        p = primes[p_rank - 1]
        if arm == "REPEATED_POWER_SURGERY":
            for exponent in spec["exponents"]:
                power = p ** exponent
                q_start = max(p + 1, (lower + power - 1) // power)
                for q_offset, q in prime_window(q_start, spec["q_prime_offsets"]):
                    n = power * q
                    if n > upper: break
                    yield {"p_rank": p_rank, "p": p, "exponent": exponent, "q_offset": q_offset, "q": q}, n, [(p, exponent), (q, 1)]
        elif arm == "SQUAREFREE_THREE_BLOCK":
            for q_offset, q in prime_window(p + 1, spec["q_prime_offsets_after_p"]):
                pq = p * q; r_start = max(q + 1, (lower + pq - 1) // pq)
                for r_offset, r in prime_window(r_start, spec["r_prime_offsets"]):
                    n = pq * r
                    if n > upper: break
                    yield {"p_rank": p_rank, "p": p, "q_offset": q_offset, "q": q, "r_offset": r_offset, "r": r}, n, [(p, 1), (q, 1), (r, 1)]


def run(args) -> int:
    verify(args.gate_bundle, args.campaign_commit)
    gate_sha = sha(args.gate_bundle / "gate-attestation.json")
    ledger = Ledger(args.ledger); visited = 0
    counts = {"states_evaluated": 0, "equation_hits": 0}
    reason = "DEADLINE_PREFIX"; found = None; best = None; worker_error = None
    last_coordinate = last_n = last_fn = last_fn12 = None
    signal.signal(signal.SIGALRM, alarm_handler); signal.alarm(M["internal_seconds"])
    ledger.append({"schema": "oeis-a056777-progress-v1", "campaign_commit": args.campaign_commit, "arm": args.arm, "shard": args.shard, "visited": 0, "last_coordinate": None, "last_n": None, "last_factors_n": None, "last_factors_n_plus_12": None, "counts": counts, "strict_best": None})
    try:
        for coordinate, n, fn in arm_states(args.arm, args.shard):
            fn12 = factor(n + 12)
            if factor(n) != fn: raise RuntimeError("constructed factor certificate mismatch")
            phi, sigma = arithmetic(fn); phi12, sigma12 = arithmetic(fn12)
            metrics = [abs((sigma12 + phi12 - 2*(n+12)) - (sigma + phi - 2*n)), abs(phi12-phi-12) + abs(sigma12-sigma-12)]
            next_counts = dict(counts); next_counts["states_evaluated"] += 1
            if phi12 == phi + 12 and sigma12 == sigma + 12: next_counts["equation_hits"] += 1
            next_best = best
            if next_best is None or metrics < next_best["metrics"]:
                next_best = {"metrics": metrics, "coordinate": coordinate, "n": n}
            next_found = certificate(args.arm, args.shard, args.campaign_commit, gate_sha, n, fn, fn12)
            if next_found is not None: next_found["coordinate"] = coordinate
            with block_alarm():
                # A candidate becomes visible before and only before its in-memory
                # prefix commit. A failed atomic rename therefore leaves the prior
                # prefix authoritative and is reported as WORKER_ERROR.
                if next_found is not None:
                    atomic_json(args.certificate, next_found)
                next_visited = visited + 1
                if next_found is None and next_visited % M["checkpoint_interval"] == 0:
                    ledger.append({"schema": "oeis-a056777-progress-v1", "campaign_commit": args.campaign_commit, "arm": args.arm, "shard": args.shard, "visited": next_visited, "last_coordinate": coordinate, "last_n": n, "last_factors_n": [list(x) for x in fn], "last_factors_n_plus_12": [list(x) for x in fn12], "counts": dict(next_counts), "strict_best": next_best})
                counts = next_counts; visited += 1; best = next_best
                last_coordinate, last_n, last_fn, last_fn12 = coordinate, n, fn, fn12
                found = next_found
                if found is not None:
                    reason = "CERTIFICATE_FOUND"; signal.alarm(0)
            if found is not None: break
        else: reason = "DOMAIN_EXHAUSTED"
    except Deadline:
        if found is None: reason = "DEADLINE_PREFIX"
    except BaseException as exc:
        reason = "WORKER_ERROR"; worker_error = error_receipt(exc)
    finally:
        signal.alarm(0)
        if visited % M["checkpoint_interval"] != 0 or found is not None:
            ledger.append({"schema": "oeis-a056777-progress-v1", "campaign_commit": args.campaign_commit, "arm": args.arm, "shard": args.shard, "visited": visited, "last_coordinate": last_coordinate, "last_n": last_n, "last_factors_n": None if last_fn is None else [list(x) for x in last_fn], "last_factors_n_plus_12": None if last_fn12 is None else [list(x) for x in last_fn12], "counts": dict(counts), "strict_best": best})
        ledger.close()
        terminal = {
            "schema": "oeis-a056777-terminal-v1", "campaign_commit": args.campaign_commit,
            "source_commit": M["formal_conjectures"]["commit"], "gate_attestation_sha256": gate_sha,
            "arm": args.arm, "shard": args.shard, "tuple_domain_only": True,
            "visited": visited, "last_coordinate": last_coordinate, "last_n": last_n, "counts": counts, "strict_best": best,
            "terminal_reason": reason, "certificate_present": found is not None,
            "worker_error": worker_error,
            "ledger_rows": ledger.seq, "final_row_sha256": ledger.previous, "ledger_sha256": sha(args.ledger),
        }
        atomic_json(args.terminal, terminal)
    return 21 if worker_error is not None else 0


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--arm", choices=M["arms"], required=True); parser.add_argument("--shard", type=int, choices=range(M["shards"]), required=True); parser.add_argument("--campaign-commit", required=True); parser.add_argument("--gate-bundle", type=pathlib.Path, required=True); parser.add_argument("--ledger", type=pathlib.Path, required=True); parser.add_argument("--terminal", type=pathlib.Path, required=True); parser.add_argument("--certificate", type=pathlib.Path, required=True)
    args = parser.parse_args()
    if len(args.campaign_commit) != 40 or any(c not in "0123456789abcdef" for c in args.campaign_commit): raise SystemExit("exact lowercase campaign commit required")
    return run(args)


if __name__ == "__main__": raise SystemExit(main())
