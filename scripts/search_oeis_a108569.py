#!/usr/bin/env python3
"""Frozen odd-support profile search for OEIS A108569; never scans flat k."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import signal
from contextlib import contextmanager
from fractions import Fraction

from prepare_oeis_a108569_gate import MANIFEST, M, factor, parse_bfile, sha, totient_factors, verify

ZERO = "0" * 64
TARGET_ARMS = ("ODD_CORE_PROFILES", "ODD_COLLISION_WALL")
STOPS = ("NO_TRANSLATED_ENDPOINT_PROFILE", "NO_RHO_COLLISION",
         "RHO_COLLISION_NO_TRANSLATION", "SUPPORT_RHO_MISMATCH",
         "EXPONENT_LATTICE_MISMATCH", "RESIDUAL_NONZERO",
         "CATALOGUE_LIFT_CONTROL", "SOURCE_CONTROL", "SURVIVOR")


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
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path; self.stream = path.open("x", encoding="ascii")
        self.seq = 0; self.previous = ZERO

    def append(self, payload: dict) -> None:
        row = dict(payload); row["seq"] = self.seq; row["previous_row_sha256"] = self.previous
        body = json.dumps(row, sort_keys=True, separators=(",", ":"))
        row["row_sha256"] = hashlib.sha256(body.encode("ascii")).hexdigest()
        self.stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        self.stream.flush(); os.fsync(self.stream.fileno())
        self.previous = row["row_sha256"]; self.seq += 1

    def close(self) -> None:
        self.stream.close()


def first_odd_primes(count: int) -> list[int]:
    values: list[int] = []; number = 3
    while len(values) < count:
        if all(number % divisor for divisor in range(3, math.isqrt(number) + 1, 2)):
            values.append(number)
        number += 2
    return values


def factor_product(factors: tuple[tuple[int, int], ...]) -> int:
    return math.prod(prime ** exponent for prime, exponent in factors)


def rho(factors: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    value = Fraction(1, 1)
    for prime, _exponent in factors:
        value *= Fraction(prime - 1, prime)
    return value.numerator, value.denominator


def _support_rows(limit: int, support: int):
    spec = M["profile_catalogues"]
    primes = first_odd_primes(spec["odd_prime_rank_last"])
    if support == 1:
        for first_rank, first in enumerate(primes, 1):
            group = first_rank - 1
            for exponents in ((e,) for e in spec["single_exponents"]):
                factors = ((first, exponents[0]),)
                value = factor_product(factors)
                if value <= limit:
                    yield value, factors, [first_rank], list(exponents), group
    elif support == 2:
        group = 0
        for first_rank, first in enumerate(primes, 1):
            for second_rank in range(first_rank + 1, len(primes) + 1):
                second = primes[second_rank - 1]
                for exponents in map(tuple, spec["mixed_exponent_pairs"]):
                    factors = ((first, exponents[0]), (second, exponents[1]))
                    value = factor_product(factors)
                    if value <= limit:
                        yield value, factors, [first_rank, second_rank], list(exponents), group
                group += 1
    elif support == 3:
        group = 0
        for first_rank, first in enumerate(primes, 1):
            for second_rank in range(first_rank + 1, len(primes) + 1):
                second = primes[second_rank - 1]
                for third_rank in range(second_rank + 1, len(primes) + 1):
                    third = primes[third_rank - 1]
                    for exponents in map(tuple, spec["triple_exponent_tuples"]):
                        factors = ((first, exponents[0]), (second, exponents[1]), (third, exponents[2]))
                        value = factor_product(factors)
                        if value <= limit:
                            yield value, factors, [first_rank, second_rank, third_rank], list(exponents), group
                    group += 1
    else:
        raise ValueError("unsupported support cardinality")


def profiles(arm: str):
    supports = M["arms"][arm]["support_cardinalities"]
    ordinal = 0
    for support in supports:
        for value, factors, ranks, exponents, group in _support_rows(M["k_maximum"], support):
            yield ordinal, value, factors, {
                "support_cardinality": support, "prime_ranks": ranks, "exponents": exponents,
                "support_group_ordinal": group}
            ordinal += 1


def sharded_profiles(arm: str, shard: int):
    """Filter canonical arm ordinals without changing their ownership."""
    for row in profiles(arm):
        if row[0] % M["shards"] == shard:
            yield row


def endpoint_catalogue() -> dict[int, tuple[tuple[int, int], ...]]:
    answer: dict[int, tuple[tuple[int, int], ...]] = {}
    maximum = M["endpoint_exclusive_maximum"] - 1
    for support in (1, 2, 3):
        for value, factors, _ranks, _exponents, _group in _support_rows(maximum, support):
            prior = answer.setdefault(value, factors)
            if prior != factors:
                raise RuntimeError("nonunique endpoint factorization")
    return answer


def ratio_catalogue(catalogue: dict[int, tuple[tuple[int, int], ...]]) -> dict[tuple[int, int], list[tuple[int, tuple[tuple[int, int], ...]]]]:
    answer: dict[tuple[int, int], list[tuple[int, tuple[tuple[int, int], ...]]]] = {}
    for value, factors in catalogue.items():
        answer.setdefault(rho(factors), []).append((value, factors))
    return answer


def catalogue_digest(catalogue: dict[int, tuple[tuple[int, int], ...]]) -> str:
    digest = hashlib.sha256()
    for value in sorted(catalogue):
        digest.update(canonical({"value": value, "factors": [list(item) for item in catalogue[value]]}))
    return digest.hexdigest()


def profile_digest(support: int) -> tuple[int, str]:
    digest = hashlib.sha256(); count = 0
    for value, factors, ranks, exponents, _group in _support_rows(M["k_maximum"], support):
        profile = {"support_cardinality": support, "prime_ranks": ranks, "exponents": exponents}
        digest.update(canonical({"ordinal": count, "value": value,
                                 "factors": [list(item) for item in factors], "profile": profile}))
        count += 1
    return count, digest.hexdigest()


def evaluate(k: int, k_factors: tuple[tuple[int, int], ...], endpoint: int,
             endpoint_factors: tuple[tuple[int, int], ...], source_values: set[int]) -> dict:
    phi_k = totient_factors(k_factors); phi_endpoint = totient_factors(endpoint_factors)
    residual = phi_endpoint - phi_k
    values = {"phi_k": phi_k, "phi_endpoint": phi_endpoint, "residual": residual}
    if k in source_values:
        return {**values, "stop": "SOURCE_CONTROL"}
    if residual == 0:
        return {**values, "stop": "SURVIVOR"}
    return {**values, "stop": "RESIDUAL_NONZERO"}


def tuples(arm: str, shard: int, source_values: set[int]):
    if arm not in TARGET_ARMS:
        raise ValueError("control arm is verified by the gate, not target enumeration")
    endpoints = endpoint_catalogue()
    ratios = ratio_catalogue(endpoints) if arm == "ODD_COLLISION_WALL" else None
    for ordinal, k, k_factors, profile in sharded_profiles(arm, shard):
        phi_k = totient_factors(k_factors); endpoint = k + phi_k
        coordinate = {"profile_ordinal": ordinal, "k": k,
                      "k_factors": [list(item) for item in k_factors], **profile}
        endpoint_factors = None
        if arm == "ODD_CORE_PROFILES":
            endpoint_factors = endpoints.get(endpoint)
            if endpoint_factors is None:
                yield coordinate, {"stop": "NO_TRANSLATED_ENDPOINT_PROFILE",
                                   "phi_k": phi_k, "endpoint": endpoint}
                continue
            a, b = rho(k_factors); desired = (a, a + b)
            if rho(endpoint_factors) != desired:
                yield coordinate, {"stop": "SUPPORT_RHO_MISMATCH", "support_pair_completed": True, "phi_k": phi_k,
                                   "endpoint": endpoint, "desired_endpoint_rho": list(desired)}
                continue
        else:
            a, b = rho(k_factors); desired = (a, a + b)
            collisions = ratios.get(desired, []) if ratios is not None else []
            if not collisions:
                yield coordinate, {"stop": "NO_RHO_COLLISION", "phi_k": phi_k,
                                   "endpoint": endpoint, "desired_endpoint_rho": list(desired)}
                continue
            for value, factors in collisions:
                if value == endpoint:
                    endpoint_factors = factors; break
            if endpoint_factors is None:
                yield coordinate, {"stop": "RHO_COLLISION_NO_TRANSLATION", "support_pair_completed": True, "phi_k": phi_k,
                                   "endpoint": endpoint, "desired_endpoint_rho": list(desired),
                                   "rho_collision_count": len(collisions)}
                continue
            coordinate["desired_endpoint_rho"] = list(desired)
        a, b = rho(k_factors)
        if b * endpoint != (a + b) * k:
            yield coordinate, {"stop": "EXPONENT_LATTICE_MISMATCH", "support_pair_completed": True, "phi_k": phi_k,
                               "endpoint": endpoint, "desired_endpoint_rho": [a, a + b]}
            continue
        coordinate["desired_endpoint_rho"] = [a, a + b]
        coordinate["support_rho_identity_verified"] = True
        coordinate["exponent_lattice_identity_verified"] = True
        coordinate["endpoint_factors"] = [list(item) for item in endpoint_factors]
        yield coordinate, {"endpoint": endpoint, "support_pair_completed": True,
                           **evaluate(k, k_factors, endpoint, endpoint_factors, source_values)}


def make_certificate(arm: str, shard: int, commit: str, gate_sha: str,
                     coordinate: dict, outcome: dict) -> dict:
    if outcome["stop"] != "SURVIVOR":
        raise ValueError("certificate requested for non-survivor")
    k = coordinate["k"]
    if k <= 1 or k % 2 != 1:
        raise RuntimeError("candidate parity/range drift")
    document = {
        "schema": "oeis-a108569-certificate-v1", "campaign_commit": commit,
        "source_commit": M["formal_conjectures"]["commit"], "manifest_sha256": sha(MANIFEST),
        "gate_attestation_sha256": gate_sha, "declaration": M["formal_conjectures"]["declaration"],
        "arm": arm, "shard": shard, "coordinate": coordinate,
        "k": k, "endpoint": outcome["endpoint"],
        "factors_k": coordinate["k_factors"], "factors_endpoint": coordinate["endpoint_factors"],
        "phi_k": outcome["phi_k"], "phi_endpoint": outcome["phi_endpoint"],
        "residual": outcome["residual"], "odd_counterexample": True,
        "source_catalogue_excluded": True,
        "enumeration_bridge": {
            "index_definition": "i := Nat.count A k",
            "nth_rule": "Nat.nth_count",
            "nth_conclusion": "a i = k",
            "positive_index_predecessor": 1,
            "strict_count_rule": "Nat.count_strict_mono",
            "positive_index_reason": "A 1 and 1 < k via Nat.count_strict_mono",
            "conclusion": "0 < i"
        },
        "candidate_status": "LITERAL_COUNTEREXAMPLE_PENDING_FORMALIZATION"
    }
    document["certificate_sha256"] = hashlib.sha256(canonical(document)).hexdigest()
    return document


def progress(commit: str, arm: str, shard: int, visited: int, coordinate, outcome,
             counts: dict, checkpoint_reason: str) -> dict:
    return {"schema": "oeis-a108569-progress-v1", "campaign_commit": commit, "arm": arm,
            "shard": shard, "visited": visited, "last_coordinate": coordinate,
            "last_outcome": outcome, "counts": dict(counts), "checkpoint_reason": checkpoint_reason}


def run(args) -> int:
    gate = verify(args.gate_bundle, args.campaign_commit)
    source_rows = parse_bfile(args.gate_bundle / "snapshots/b108569.txt")
    source_values = {k for _, k in source_rows}
    gate_sha = sha(args.gate_bundle / "gate-attestation.json")
    ledger = Ledger(args.ledger); counts = {name: 0 for name in STOPS}; visited = 0
    last_coordinate = last_outcome = found = worker_error = None; reason = "CAP_PREFIX"
    since_checkpoint = 0
    signal.signal(signal.SIGALRM, alarm_handler)
    with block_alarm():
        ledger.append(progress(args.campaign_commit, args.arm, args.shard, 0, None, None, counts, "INITIAL"))
    signal.alarm(M["internal_seconds"])
    try:
        for coordinate, outcome in tuples(args.arm, args.shard, source_values):
            next_counts = dict(counts); next_counts[outcome["stop"]] += 1; next_visited = visited + 1
            candidate = make_certificate(args.arm, args.shard, args.campaign_commit, gate_sha,
                                         coordinate, outcome) if outcome["stop"] == "SURVIVOR" else None
            with block_alarm():
                if candidate is not None:
                    atomic_json(args.certificate, candidate)
                elif outcome.get("support_pair_completed") is True or since_checkpoint + 1 >= M["checkpoint_minimum_exponent_coordinates"]:
                    checkpoint_reason = "SUPPORT_PAIR_COMPLETE" if outcome.get("support_pair_completed") is True else "EXPONENT_COORDINATE_INTERVAL"
                    ledger.append(progress(args.campaign_commit, args.arm, args.shard, next_visited,
                                           coordinate, outcome, next_counts, checkpoint_reason))
                    since_checkpoint = -1
                counts, visited = next_counts, next_visited
                last_coordinate, last_outcome, found = coordinate, outcome, candidate
                since_checkpoint += 1
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
            if found is None and since_checkpoint:
                ledger.append(progress(args.campaign_commit, args.arm, args.shard, visited,
                                       last_coordinate, last_outcome, counts, "FINAL_PREFIX"))
            ledger.close()
            terminal = {
                "schema": "oeis-a108569-terminal-v1", "campaign_commit": args.campaign_commit,
                "source_commit": M["formal_conjectures"]["commit"],
                "gate_attestation_sha256": gate_sha, "arm": args.arm, "shard": args.shard,
                "odd_profile_domain_only": True, "catalogue_rows": gate["table"]["catalogue"]["rows"],
                "visited": visited, "last_coordinate": last_coordinate, "last_outcome": last_outcome,
                "counts": counts, "terminal_reason": reason, "certificate_present": found is not None,
                "worker_error": worker_error, "ledger_rows": ledger.seq,
                "final_row_sha256": ledger.previous, "ledger_sha256": sha(args.ledger),
            }
            atomic_json(args.terminal, terminal)
    return 21 if worker_error is not None else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=TARGET_ARMS, required=True)
    parser.add_argument("--shard", type=int, choices=range(M["shards"]), required=True)
    parser.add_argument("--campaign-commit", required=True)
    parser.add_argument("--gate-bundle", type=pathlib.Path, required=True)
    parser.add_argument("--ledger", type=pathlib.Path, required=True)
    parser.add_argument("--terminal", type=pathlib.Path, required=True)
    parser.add_argument("--certificate", type=pathlib.Path, required=True)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
