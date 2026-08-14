#!/usr/bin/env python3
"""Independent replay of frozen OEIS A067720 profile evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

from prepare_oeis_a067720_gate import MANIFEST, M, parse_bfile, sha, verify

ZERO = "0" * 64
STOPS = ("NO_TRANSLATED_ENDPOINT_PROFILE", "RESIDUAL_NONZERO", "KNOWN_EXCEPTION_CONTROL",
         "CATALOGUE_CONTROL", "SURVIVOR")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def independent_primes(count: int) -> list[int]:
    ceiling = 64
    while True:
        composite = [False] * (ceiling + 1)
        for base in range(2, math.isqrt(ceiling) + 1):
            if not composite[base]:
                for multiple in range(base * base, ceiling + 1, base):
                    composite[multiple] = True
        values = [number for number in range(2, ceiling + 1) if not composite[number]]
        if len(values) >= count:
            return values[:count]
        ceiling *= 2


def deterministic_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % divisor == 0:
            return value == divisor
    d, s = value - 1, 0
    while d & 1 == 0:
        d >>= 1; s += 1
    for witness in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if witness % value == 0:
            continue
        residue = pow(witness, d, value)
        if residue in (1, value - 1):
            continue
        accepted = False
        for _ in range(s - 1):
            residue = pow(residue, 2, value)
            if residue == value - 1:
                accepted = True; break
        if not accepted:
            return False
    return True


def factor_data(factors: list[list[int]]) -> tuple[int, int]:
    product = phi = 1; previous = 1
    for item in factors:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("factor-pair shape drift")
        prime, exponent = item
        if not isinstance(prime, int) or not deterministic_prime(prime) or prime <= previous:
            raise ValueError("invalid/unsorted certified prime")
        if not isinstance(exponent, int) or exponent < 1:
            raise ValueError("invalid certified exponent")
        product *= prime ** exponent; phi *= (prime - 1) * prime ** (exponent - 1); previous = prime
    return product, phi


def profiles(arm: str):
    spec = M["profile_catalogues"]; primes = independent_primes(spec["successor_prime_rank_last"])
    maximum = M["k_maximum"] + 1; ordinal = 0
    if arm == "SUCCESSOR_PROFILE_SURGERY":
        for rank, prime in enumerate(primes, 1):
            for exponent in spec["successor_single_exponents"]:
                value = prime ** exponent
                if value <= maximum:
                    yield ordinal, value, [[prime, exponent]], {
                        "signature": "SINGLE", "prime_ranks": [rank], "exponents": [exponent]}
                    ordinal += 1
    elif arm == "TOTIENT_RATIO_WALL":
        for left_rank in range(1, len(primes) + 1):
            left = primes[left_rank - 1]
            for right_rank in range(left_rank + 1, len(primes) + 1):
                right = primes[right_rank - 1]
                for left_exp, right_exp in spec["successor_mixed_exponent_pairs"]:
                    value = left ** left_exp * right ** right_exp
                    if value <= maximum:
                        yield ordinal, value, [[left, left_exp], [right, right_exp]], {
                            "signature": "MIXED", "prime_ranks": [left_rank, right_rank],
                            "exponents": [left_exp, right_exp]}
                        ordinal += 1
    else:
        raise ValueError("unknown arm")


def endpoints() -> dict[int, list[list[int]]]:
    spec = M["profile_catalogues"]; primes = independent_primes(spec["endpoint_prime_rank_last"])
    maximum = M["k_maximum"] ** 2 + 1; result: dict[int, list[list[int]]] = {}
    for prime in primes:
        for exponent in spec["endpoint_single_exponents"]:
            value = prime ** exponent
            if value <= maximum:
                factors = [[prime, exponent]]
                if value in result and result[value] != factors:
                    raise ValueError("endpoint uniqueness drift")
                result[value] = factors
    for left_rank in range(1, len(primes) + 1):
        left = primes[left_rank - 1]
        for right_rank in range(left_rank + 1, len(primes) + 1):
            right = primes[right_rank - 1]
            for left_exp, right_exp in spec["endpoint_mixed_exponent_pairs"]:
                value = left ** left_exp * right ** right_exp
                if value <= maximum:
                    factors = [[left, left_exp], [right, right_exp]]
                    if value in result and result[value] != factors:
                        raise ValueError("endpoint uniqueness drift")
                    result[value] = factors
    return result


def expected_outcome(k: int, successor_factors: list[list[int]], endpoint: int,
                     endpoint_factors: list[list[int]] | None, source_values: set[int]) -> dict:
    if endpoint_factors is None:
        return {"stop": "NO_TRANSLATED_ENDPOINT_PROFILE", "k": k, "endpoint": endpoint}
    successor, phi_s = factor_data(successor_factors); product_m, phi_m = factor_data(endpoint_factors)
    if product_m != endpoint or successor != k + 1:
        raise ValueError("translated product drift")
    residual = phi_m - k * phi_s
    values = {"k": k, "endpoint": endpoint, "phi_successor": phi_s, "phi_endpoint": phi_m,
              "residual": residual}
    if k == 8:
        stop = "KNOWN_EXCEPTION_CONTROL"
    elif k in source_values:
        stop = "CATALOGUE_CONTROL"
    elif residual == 0:
        stop = "SURVIVOR"
    else:
        stop = "RESIDUAL_NONZERO"
    return {**values, "stop": stop}


def independent_tuples(arm: str, shard: int, source_values: set[int]):
    endpoint_map = endpoints()
    for ordinal, successor, factors, profile in profiles(arm):
        if ordinal % M["shards"] != shard:
            continue
        k = successor - 1; endpoint = k * k + 1; endpoint_factors = endpoint_map.get(endpoint)
        coordinate = {"successor_profile_ordinal": ordinal, "successor": successor,
                      "successor_factors": factors, **profile}
        if endpoint_factors is not None:
            coordinate["endpoint_factors"] = endpoint_factors
        yield coordinate, expected_outcome(k, factors, endpoint, endpoint_factors, source_values)


def locate(coordinate: dict, arm: str, shard: int, source_values: set[int]) -> dict:
    ordinal = coordinate.get("successor_profile_ordinal")
    if type(ordinal) is not int or ordinal < 0 or ordinal % M["shards"] != shard:
        raise ValueError("coordinate shard ownership drift")
    for expected, outcome in independent_tuples(arm, shard, source_values):
        current = expected["successor_profile_ordinal"]
        if current == ordinal:
            if expected != coordinate:
                raise ValueError("coordinate payload drift")
            return outcome
        if current > ordinal:
            break
    raise ValueError("coordinate outside frozen profile domain")


def expected_certificate(document: dict, outcome: dict, commit: str, gate_digest: str) -> dict:
    coordinate = document["coordinate"]; factors_s = coordinate["successor_factors"]
    factors_m = coordinate["endpoint_factors"]; successor, phi_s = factor_data(factors_s)
    endpoint, phi_m = factor_data(factors_m); k = successor - 1
    if endpoint != k * k + 1 or outcome.get("stop") != "SURVIVOR" or outcome["residual"] != 0:
        raise ValueError("certificate is not an exact survivor")
    proper = factors_s[0][0]
    result = {
        "schema": "oeis-a067720-certificate-v1", "campaign_commit": commit,
        "source_commit": M["formal_conjectures"]["commit"], "manifest_sha256": sha(MANIFEST),
        "gate_attestation_sha256": gate_digest, "declaration": M["formal_conjectures"]["declaration"],
        "arm": document["arm"], "shard": document["shard"], "coordinate": coordinate, "k": k,
        "successor": successor, "endpoint": endpoint, "factors_successor": factors_s,
        "factors_endpoint": factors_m, "phi_successor": phi_s, "phi_endpoint": phi_m,
        "residual": 0, "known_exception_excluded": k != 8,
        "source_catalogue_excluded": True, "proper_divisor_successor": proper,
    }
    result["certificate_sha256"] = hashlib.sha256(canonical(result)).hexdigest()
    return result


def candidate(path: pathlib.Path, bundle: pathlib.Path, commit: str) -> dict:
    verify(bundle, commit)
    raw = path.read_bytes(); document = json.loads(raw)
    if raw != canonical(document):
        raise ValueError("certificate is not canonical JSON bytes")
    arm, shard, coordinate = document.get("arm"), document.get("shard"), document.get("coordinate")
    if document.get("schema") != "oeis-a067720-certificate-v1" or document.get("campaign_commit") != commit:
        raise ValueError("certificate identity drift")
    if arm not in M["arms"] or type(shard) is not int or not 0 <= shard < M["shards"] or not isinstance(coordinate, dict):
        raise ValueError("certificate arm/shard/coordinate drift")
    rows = parse_bfile(bundle / "snapshots/b067720.txt"); source_values = {k for _, k in rows}
    outcome = locate(coordinate, arm, shard, source_values)
    expected = expected_certificate(document, outcome, commit, sha(bundle / "gate-attestation.json"))
    if document != expected:
        raise ValueError("certificate payload/self-hash drift")
    k, successor, proper = document["k"], document["successor"], document["proper_divisor_successor"]
    if k == 8 or k in source_values or not (1 < proper < successor and successor % proper == 0):
        raise ValueError("exception/catalogue/compositeness certificate drift")
    return document


def chain(path: pathlib.Path, commit: str, arm: str, shard: int) -> tuple[list[dict], str]:
    if type(shard) is not int or not 0 <= shard < M["shards"]:
        raise ValueError("ledger requested shard drift")
    rows = []; previous = ZERO
    raw_lines = path.read_bytes().splitlines(keepends=True)
    for sequence, raw in enumerate(raw_lines):
        row = json.loads(raw); digest = row.pop("row_sha256", None)
        if raw != canonical({**row, "row_sha256": digest}):
            raise ValueError("ledger noncanonical-byte drift")
        if type(row.get("seq")) is not int or row.get("seq") != sequence or row.get("previous_row_sha256") != previous:
            raise ValueError("ledger order/previous-hash drift")
        if row.get("campaign_commit") != commit or row.get("arm") != arm or row.get("shard") != shard:
            raise ValueError("ledger identity drift")
        progress_keys = {"schema", "campaign_commit", "arm", "shard", "visited", "last_coordinate",
                         "last_outcome", "counts", "seq", "previous_row_sha256"}
        if set(row) != progress_keys:
            raise ValueError("ledger progress key drift")
        if type(row.get("visited")) is not int or row["visited"] < 0 or type(row.get("shard")) is not int:
            raise ValueError("ledger numeric field drift")
        if set(row.get("counts", {})) != set(STOPS) or any(type(value) is not int or value < 0 for value in row["counts"].values()) or sum(row["counts"].values()) != row["visited"]:
            raise ValueError("ledger count field drift")
        actual = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
        if digest != actual:
            raise ValueError("ledger hash-chain drift")
        row["row_sha256"] = digest; rows.append(row); previous = digest
    if not rows:
        raise ValueError("empty ledger")
    return rows, previous


def validate_error(reason: str, error) -> None:
    if reason == "WORKER_ERROR":
        if not isinstance(error, dict) or set(error) != {"type", "message", "message_sha256"}:
            raise ValueError("worker error receipt shape drift")
        if hashlib.sha256(error["message"].encode()).hexdigest() != error["message_sha256"]:
            raise ValueError("worker error receipt digest drift")
    elif error is not None:
        raise ValueError("spurious worker error")


def replay(terminal_doc: dict, rows: list[dict], certificate_doc: dict | None,
           source_values: set[int]) -> None:
    visited = terminal_doc["visited"]
    if type(visited) is not int or visited < 0:
        raise ValueError("terminal visited must be a nonnegative integer")
    if set(terminal_doc.get("counts", {})) != set(STOPS) or any(type(value) is not int or value < 0 for value in terminal_doc["counts"].values()) or sum(terminal_doc["counts"].values()) != visited:
        raise ValueError("terminal count domain drift")
    expected_visits = [0] + list(range(M["checkpoint_interval"], visited + 1, M["checkpoint_interval"]))
    if visited % M["checkpoint_interval"]:
        expected_visits.append(visited)
    if certificate_doc is not None and expected_visits[-1] == visited:
        expected_visits.pop()
    if [row.get("visited") for row in rows] != expected_visits:
        raise ValueError("ledger checkpoint gap/duplicate drift")
    counts = {name: 0 for name in STOPS}; checkpoints = {row["visited"]: row for row in rows}
    iterator = independent_tuples(terminal_doc["arm"], terminal_doc["shard"], source_values)
    last_coordinate = last_outcome = first_survivor = None; first_survivor_index = None
    for ordinal in range(visited):
        try:
            coordinate, outcome = next(iterator)
        except StopIteration as exc:
            raise ValueError("visited prefix exceeds frozen domain") from exc
        counts[outcome["stop"]] += 1; last_coordinate, last_outcome = coordinate, outcome
        if first_survivor is None and outcome["stop"] == "SURVIVOR":
            first_survivor = coordinate; first_survivor_index = ordinal
        count = ordinal + 1
        if count in checkpoints:
            row = checkpoints[count]
            if row.get("schema") != "oeis-a067720-progress-v1" or row.get("last_coordinate") != coordinate or row.get("last_outcome") != outcome or row.get("counts") != counts:
                raise ValueError("checkpoint semantic drift")
    zero = checkpoints[0]
    if zero.get("schema") != "oeis-a067720-progress-v1" or zero.get("last_coordinate") is not None or zero.get("last_outcome") is not None or zero.get("counts") != {name: 0 for name in STOPS}:
        raise ValueError("initial checkpoint drift")
    if terminal_doc.get("algebraic_profile_domain_only") is not True or terminal_doc.get("last_coordinate") != last_coordinate or terminal_doc.get("last_outcome") != last_outcome or terminal_doc.get("counts") != counts:
        raise ValueError("terminal prefix drift")
    if certificate_doc is not None:
        if first_survivor is None or certificate_doc["coordinate"] != first_survivor or first_survivor_index != visited - 1:
            raise ValueError("candidate is not the first survivor and final visited state")
    elif first_survivor is not None:
        raise ValueError("candidate omission")
    if terminal_doc["terminal_reason"] == "DOMAIN_EXHAUSTED":
        try:
            next(iterator)
        except StopIteration:
            pass
        else:
            raise ValueError("false frozen-domain exhaustion")


def terminal(ledger_path: pathlib.Path, terminal_path: pathlib.Path, certificate_path: pathlib.Path | None,
             bundle: pathlib.Path, commit: str, arm: str, shard: int) -> dict:
    gate = verify(bundle, commit); raw = terminal_path.read_bytes(); document = json.loads(raw)
    if raw != canonical(document):
        raise ValueError("terminal is not canonical JSON bytes")
    rows, final = chain(ledger_path, commit, arm, shard)
    terminal_keys = {"schema", "campaign_commit", "source_commit", "gate_attestation_sha256",
                     "arm", "shard", "algebraic_profile_domain_only", "catalogue_rows", "visited",
                     "last_coordinate", "last_outcome", "counts", "terminal_reason",
                     "certificate_present", "worker_error", "ledger_rows", "final_row_sha256", "ledger_sha256"}
    if set(document) != terminal_keys:
        raise ValueError("terminal key drift")
    if type(document.get("shard")) is not int or type(document.get("visited")) is not int or document["visited"] < 0:
        raise ValueError("terminal numeric field drift")
    if type(document.get("certificate_present")) is not bool:
        raise ValueError("terminal certificate_present must be Boolean")
    if document.get("schema") != "oeis-a067720-terminal-v1" or document.get("campaign_commit") != commit:
        raise ValueError("terminal identity drift")
    if document.get("source_commit") != M["formal_conjectures"]["commit"] or document.get("gate_attestation_sha256") != sha(bundle / "gate-attestation.json"):
        raise ValueError("terminal source/gate binding drift")
    if (document.get("arm"), document.get("shard")) != (arm, shard):
        raise ValueError("terminal arm/shard drift")
    if document.get("catalogue_rows") != gate["table"]["catalogue"]["rows"]:
        raise ValueError("terminal catalogue binding drift")
    if type(document.get("ledger_rows")) is not int or document["ledger_rows"] < 0 or document.get("ledger_rows") != len(rows) or document.get("final_row_sha256") != final or document.get("ledger_sha256") != sha(ledger_path):
        raise ValueError("terminal ledger binding drift")
    if document.get("terminal_reason") not in {"CAP_PREFIX", "DOMAIN_EXHAUSTED", "CERTIFICATE_FOUND", "WORKER_ERROR"}:
        raise ValueError("terminal reason drift")
    validate_error(document["terminal_reason"], document.get("worker_error"))
    present = certificate_path is not None
    if document["certificate_present"] != present or (document["terminal_reason"] == "CERTIFICATE_FOUND") != present:
        raise ValueError("terminal/certificate presence drift")
    cert = candidate(certificate_path, bundle, commit) if present else None
    source_values = {k for _, k in parse_bfile(bundle / "snapshots/b067720.txt")}
    replay(document, rows, cert, source_values)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="mode", required=True)
    check = sub.add_parser("candidate"); check.add_argument("certificate", type=pathlib.Path); check.add_argument("bundle", type=pathlib.Path); check.add_argument("--campaign-commit", required=True)
    replay_parser = sub.add_parser("terminal"); replay_parser.add_argument("ledger", type=pathlib.Path); replay_parser.add_argument("terminal", type=pathlib.Path); replay_parser.add_argument("certificate"); replay_parser.add_argument("bundle", type=pathlib.Path); replay_parser.add_argument("--campaign-commit", required=True); replay_parser.add_argument("--arm", choices=M["arms"], required=True); replay_parser.add_argument("--shard", type=int, required=True)
    args = parser.parse_args()
    if args.mode == "candidate":
        result = candidate(args.certificate, args.bundle, args.campaign_commit)
        print(json.dumps({"verified": True, "k": result["k"]}, separators=(",", ":")))
    else:
        terminal(args.ledger, args.terminal, None if args.certificate == "-" else pathlib.Path(args.certificate),
                 args.bundle, args.campaign_commit, args.arm, args.shard)
        print('{"verified":true}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
