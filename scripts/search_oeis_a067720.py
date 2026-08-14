#!/usr/bin/env python3
"""Frozen algebraic profile search for OEIS A067720; never scans flat k."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import signal
from contextlib import contextmanager

from prepare_oeis_a067720_gate import MANIFEST, M, parse_bfile, sha, verify

ZERO = "0" * 64
STOPS = ("NO_TRANSLATED_ENDPOINT_PROFILE", "RESIDUAL_NONZERO", "KNOWN_EXCEPTION_CONTROL",
         "CATALOGUE_CONTROL", "SURVIVOR")


class Deadline(Exception):
    pass


def alarm_handler(_signum, _frame):
    raise Deadline()


@contextmanager
def block_alarm():
    old = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, old)


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def atomic_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def error_receipt(exc: BaseException) -> dict:
    message = str(exc)[:1000]
    return {"type": type(exc).__name__, "message": message,
            "message_sha256": hashlib.sha256(message.encode()).hexdigest()}


class Ledger:
    def __init__(self, path: pathlib.Path):
        path.parent.mkdir(parents=True, exist_ok=True); self.path = path
        self.stream = path.open("x", encoding="ascii"); self.seq = 0; self.previous = ZERO

    def append(self, payload: dict) -> None:
        row = dict(payload); row["seq"] = self.seq; row["previous_row_sha256"] = self.previous
        body = json.dumps(row, sort_keys=True, separators=(",", ":"))
        row["row_sha256"] = hashlib.sha256(body.encode("ascii")).hexdigest()
        self.stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        self.stream.flush(); os.fsync(self.stream.fileno())
        self.previous = row["row_sha256"]; self.seq += 1

    def close(self) -> None:
        self.stream.close()


def first_primes(count: int) -> list[int]:
    limit = 64
    while True:
        flags = bytearray(b"\x01") * (limit + 1); flags[:2] = b"\x00\x00"
        for prime in range(2, math.isqrt(limit) + 1):
            if flags[prime]:
                flags[prime * prime:limit + 1:prime] = b"\x00" * (((limit - prime * prime) // prime) + 1)
        values = [number for number, flag in enumerate(flags) if flag]
        if len(values) >= count:
            return values[:count]
        limit *= 2


def totient(factors: tuple[tuple[int, int], ...]) -> int:
    answer = 1
    for prime, exponent in factors:
        answer *= (prime - 1) * prime ** (exponent - 1)
    return answer


def factor_product(factors: tuple[tuple[int, int], ...]) -> int:
    answer = 1
    for prime, exponent in factors:
        answer *= prime ** exponent
    return answer


def successor_profiles(arm: str):
    spec = M["profile_catalogues"]; primes = first_primes(spec["successor_prime_rank_last"])
    maximum = M["k_maximum"] + 1; ordinal = 0
    if arm == "SUCCESSOR_PROFILE_SURGERY":
        for rank, prime in enumerate(primes, 1):
            for exponent in spec["successor_single_exponents"]:
                value = prime ** exponent
                if value <= maximum:
                    yield ordinal, value, ((prime, exponent),), {"signature": "SINGLE", "prime_ranks": [rank], "exponents": [exponent]}
                    ordinal += 1
    elif arm == "TOTIENT_RATIO_WALL":
        for left_rank in range(1, len(primes) + 1):
            left = primes[left_rank - 1]
            for right_rank in range(left_rank + 1, len(primes) + 1):
                right = primes[right_rank - 1]
                for left_exp, right_exp in spec["successor_mixed_exponent_pairs"]:
                    value = left ** left_exp * right ** right_exp
                    if value <= maximum:
                        yield ordinal, value, ((left, left_exp), (right, right_exp)), {
                            "signature": "MIXED", "prime_ranks": [left_rank, right_rank],
                            "exponents": [left_exp, right_exp]}
                        ordinal += 1
    else:
        raise ValueError("unknown arm")


def endpoint_catalogue() -> dict[int, tuple[tuple[int, int], ...]]:
    spec = M["profile_catalogues"]; primes = first_primes(spec["endpoint_prime_rank_last"])
    maximum = M["k_maximum"] ** 2 + 1; answer: dict[int, tuple[tuple[int, int], ...]] = {}
    for prime in primes:
        for exponent in spec["endpoint_single_exponents"]:
            value = prime ** exponent
            if value <= maximum:
                factors = ((prime, exponent),)
                if value in answer and answer[value] != factors:
                    raise RuntimeError("nonunique endpoint factorization")
                answer[value] = factors
    for left_index, left in enumerate(primes):
        for right in primes[left_index + 1:]:
            for left_exp, right_exp in spec["endpoint_mixed_exponent_pairs"]:
                value = left ** left_exp * right ** right_exp
                if value <= maximum:
                    factors = ((left, left_exp), (right, right_exp))
                    if value in answer and answer[value] != factors:
                        raise RuntimeError("nonunique endpoint factorization")
                    answer[value] = factors
    return answer


def catalogue_digest(catalogue: dict[int, tuple[tuple[int, int], ...]]) -> str:
    digest = hashlib.sha256()
    for value in sorted(catalogue):
        digest.update(canonical({"value": value, "factors": [list(item) for item in catalogue[value]]}))
    return digest.hexdigest()


def evaluate_translation(k: int, successor: int, successor_factors: tuple[tuple[int, int], ...],
                         endpoint: int, endpoint_factors: tuple[tuple[int, int], ...],
                         source_values: set[int]) -> dict:
    phi_successor = totient(successor_factors); phi_endpoint = totient(endpoint_factors)
    residual = phi_endpoint - k * phi_successor
    values = {"phi_successor": phi_successor, "phi_endpoint": phi_endpoint, "residual": residual}
    if k == 8:
        return {**values, "stop": "KNOWN_EXCEPTION_CONTROL"}
    if k in source_values:
        return {**values, "stop": "CATALOGUE_CONTROL"}
    if residual == 0:
        return {**values, "stop": "SURVIVOR"}
    return {**values, "stop": "RESIDUAL_NONZERO"}


def tuples(arm: str, shard: int, source_values: set[int]):
    endpoint_map = endpoint_catalogue()
    for ordinal, successor, successor_factors, profile in successor_profiles(arm):
        if ordinal % M["shards"] != shard:
            continue
        k = successor - 1; endpoint = k * k + 1
        coordinate = {"successor_profile_ordinal": ordinal, "successor": successor,
                      "successor_factors": [list(item) for item in successor_factors], **profile}
        endpoint_factors = endpoint_map.get(endpoint)
        if endpoint_factors is None:
            yield coordinate, {"stop": "NO_TRANSLATED_ENDPOINT_PROFILE", "k": k, "endpoint": endpoint}
            continue
        coordinate["endpoint_factors"] = [list(item) for item in endpoint_factors]
        outcome = evaluate_translation(k, successor, successor_factors, endpoint, endpoint_factors, source_values)
        yield coordinate, {"k": k, "endpoint": endpoint, **outcome}


def make_certificate(arm: str, shard: int, commit: str, gate_sha: str,
                     coordinate: dict, outcome: dict) -> dict:
    if outcome["stop"] != "SURVIVOR":
        raise ValueError("certificate requested for non-survivor")
    successor = coordinate["successor"]; k = outcome["k"]; endpoint = outcome["endpoint"]
    proper_divisor = coordinate["successor_factors"][0][0]
    if not (1 < proper_divisor < successor and successor % proper_divisor == 0):
        raise RuntimeError("compositeness witness drift")
    document = {
        "schema": "oeis-a067720-certificate-v1", "campaign_commit": commit,
        "source_commit": M["formal_conjectures"]["commit"], "manifest_sha256": sha(MANIFEST),
        "gate_attestation_sha256": gate_sha, "declaration": M["formal_conjectures"]["declaration"],
        "arm": arm, "shard": shard, "coordinate": coordinate, "k": k,
        "successor": successor, "endpoint": endpoint,
        "factors_successor": coordinate["successor_factors"],
        "factors_endpoint": coordinate["endpoint_factors"],
        "phi_successor": outcome["phi_successor"], "phi_endpoint": outcome["phi_endpoint"],
        "residual": outcome["residual"], "known_exception_excluded": k != 8,
        "source_catalogue_excluded": True, "proper_divisor_successor": proper_divisor,
    }
    document["certificate_sha256"] = hashlib.sha256(canonical(document)).hexdigest()
    return document


def progress(commit: str, arm: str, shard: int, visited: int, coordinate, outcome, counts: dict) -> dict:
    return {"schema": "oeis-a067720-progress-v1", "campaign_commit": commit, "arm": arm,
            "shard": shard, "visited": visited, "last_coordinate": coordinate,
            "last_outcome": outcome, "counts": dict(counts)}


def run(args) -> int:
    gate = verify(args.gate_bundle, args.campaign_commit)
    source_rows = parse_bfile(args.gate_bundle / "snapshots/b067720.txt")
    source_values = {k for _, k in source_rows}; gate_sha = sha(args.gate_bundle / "gate-attestation.json")
    ledger = Ledger(args.ledger); counts = {name: 0 for name in STOPS}; visited = 0
    last_coordinate = last_outcome = found = worker_error = None; reason = "CAP_PREFIX"
    signal.signal(signal.SIGALRM, alarm_handler)
    with block_alarm():
        ledger.append(progress(args.campaign_commit, args.arm, args.shard, 0, None, None, counts))
    signal.alarm(M["internal_seconds"])
    try:
        for coordinate, outcome in tuples(args.arm, args.shard, source_values):
            next_counts = dict(counts); next_counts[outcome["stop"]] += 1; next_visited = visited + 1
            candidate = make_certificate(args.arm, args.shard, args.campaign_commit, gate_sha, coordinate, outcome) if outcome["stop"] == "SURVIVOR" else None
            with block_alarm():
                if candidate is not None:
                    # The durable certificate is the authoritative candidate
                    # commit. No fallible ledger write is allowed after it.
                    atomic_json(args.certificate, candidate)
                elif next_visited % M["checkpoint_interval"] == 0:
                    ledger.append(progress(args.campaign_commit, args.arm, args.shard, next_visited,
                                           coordinate, outcome, next_counts))
                counts, visited = next_counts, next_visited
                last_coordinate, last_outcome, found = coordinate, outcome, candidate
            if found is not None:
                reason = "CERTIFICATE_FOUND"; signal.alarm(0); break
        else:
            reason = "DOMAIN_EXHAUSTED"
    except Deadline:
        reason = "CAP_PREFIX" if found is None else "CERTIFICATE_FOUND"
    except BaseException as exc:
        reason = "WORKER_ERROR"; worker_error = error_receipt(exc)
    finally:
        signal.alarm(0)
        with block_alarm():
            if found is None and visited % M["checkpoint_interval"] != 0:
                ledger.append(progress(args.campaign_commit, args.arm, args.shard, visited,
                                       last_coordinate, last_outcome, counts))
            ledger.close()
            terminal = {
                "schema": "oeis-a067720-terminal-v1", "campaign_commit": args.campaign_commit,
                "source_commit": M["formal_conjectures"]["commit"],
                "gate_attestation_sha256": gate_sha, "arm": args.arm, "shard": args.shard,
                "algebraic_profile_domain_only": True, "catalogue_rows": gate["table"]["catalogue"]["rows"],
                "visited": visited, "last_coordinate": last_coordinate, "last_outcome": last_outcome,
                "counts": counts, "terminal_reason": reason, "certificate_present": found is not None,
                "worker_error": worker_error, "ledger_rows": ledger.seq,
                "final_row_sha256": ledger.previous, "ledger_sha256": sha(args.ledger),
            }
            atomic_json(args.terminal, terminal)
    return 21 if worker_error is not None else 0


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--arm", choices=M["arms"], required=True)
    parser.add_argument("--shard", type=int, choices=range(M["shards"]), required=True)
    parser.add_argument("--campaign-commit", required=True); parser.add_argument("--gate-bundle", type=pathlib.Path, required=True)
    parser.add_argument("--ledger", type=pathlib.Path, required=True); parser.add_argument("--terminal", type=pathlib.Path, required=True)
    parser.add_argument("--certificate", type=pathlib.Path, required=True); args = parser.parse_args()
    if len(args.campaign_commit) != 40 or any(c not in "0123456789abcdef" for c in args.campaign_commit):
        raise SystemExit("exact lowercase campaign commit required")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
