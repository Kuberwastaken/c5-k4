#!/usr/bin/env python3
"""Independent, fail-closed replay of A056777 certificates and search prefixes."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

from prepare_oeis_a056777_gate import MANIFEST, M, sha, verify

ZERO = "0" * 64


def prime(n: int) -> bool:
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    odd, twos = n - 1, 0
    while odd & 1 == 0: twos += 1; odd >>= 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % n == 0: continue
        residue = pow(base, odd, n)
        if residue in (1, n - 1): continue
        for _ in range(twos - 1):
            residue = pow(residue, 2, n)
            if residue == n - 1: break
        else: return False
    return True


def floyd_divisor(n: int) -> int:
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3
    for seed, constant in ((2, 1), (3, 1), (2, 3), (5, 7), (7, 11), (11, 13)):
        x = y = seed; divisor = 1
        while divisor == 1:
            x = (x * x + constant) % n
            y = (y * y + constant) % n; y = (y * y + constant) % n
            divisor = math.gcd(abs(x - y), n)
        if divisor != n: return divisor
    raise ValueError(f"independent factorization failed for {n}")


def refactor(n: int) -> list[tuple[int, int]]:
    values = []
    stack = [n]
    while stack:
        value = stack.pop()
        if value == 1: continue
        if prime(value): values.append(value); continue
        divisor = floyd_divisor(value); stack.extend((divisor, value // divisor))
    values.sort(); result = []
    for p in values:
        if result and result[-1][0] == p: result[-1] = (p, result[-1][1] + 1)
        else: result.append((p, 1))
    if math.prod(p**e for p, e in result) != n or any(not prime(p) for p, _ in result):
        raise ValueError("factorization certificate is not exact")
    return result


def values(factors: list[tuple[int, int]]) -> tuple[int, int]:
    phi = sigma = 1
    for p, exponent in factors:
        phi = phi * (p - 1) * p ** (exponent - 1)
        sigma = sigma * ((p ** (exponent + 1) - 1) // (p - 1))
    return phi, sigma


def has_arm_shape(arm: str, factors: list[tuple[int, int]]) -> bool:
    if arm == "REPEATED_POWER_SURGERY": return len(factors) == 2 and factors[0][1] >= 2 and factors[1][1] == 1
    if arm == "SQUAREFREE_THREE_BLOCK": return len(factors) == 3 and all(e == 1 for _, e in factors)
    if arm == "PURE_PRIME_POWER": return len(factors) == 1 and factors[0][1] >= 3
    return False


def quadruple(n: int) -> int | None:
    square = math.isqrt(n + 16)
    if square * square != n + 16 or square < 4: return None
    p = square - 4
    if p * (p + 8) != n: return None
    return p if all(prime(p + offset) for offset in (0, 2, 6, 8)) else None


def expected_certificate(arm: str, shard: int, commit: str, gate_sha: str, n: int,
                         fn: list[tuple[int, int]], fn12: list[tuple[int, int]], coordinate: dict | None = None) -> dict | None:
    phi, sigma = values(fn); phi12, sigma12 = values(fn12)
    if phi12 != phi + 12 or sigma12 != sigma + 12 or quadruple(n) is not None: return None
    result = {
        "schema": "oeis-a056777-certificate-v1", "campaign_commit": commit,
        "source_commit": M["formal_conjectures"]["commit"], "manifest_sha256": sha(MANIFEST),
        "gate_attestation_sha256": gate_sha, "declaration": "OeisA56777.comesFromPrimeQuadruple_of_a",
        "arm": arm, "shard": shard, "n": n, "factors_n": [list(x) for x in fn],
        "factors_n_plus_12": [list(x) for x in fn12], "phi_n": phi, "phi_n_plus_12": phi12,
        "sigma_n": sigma, "sigma_n_plus_12": sigma12, "composite_n": True,
        "comes_from_prime_quadruple": False,
    }
    if coordinate is not None: result["coordinate"] = coordinate
    return result


def initial_primes(count: int) -> list[int]:
    bound = 32
    while True:
        flags = bytearray(b"\x01") * (bound + 1); flags[:2] = b"\x00\x00"
        for divisor in range(2, math.isqrt(bound) + 1):
            if flags[divisor]: flags[divisor*divisor:bound+1:divisor] = b"\x00" * (((bound-divisor*divisor)//divisor)+1)
        result = [number for number, flag in enumerate(flags) if flag]
        if len(result) >= count: return result[:count]
        bound *= 2


def following_primes(start: int, count: int):
    number = max(2, start)
    if number > 2 and number % 2 == 0: number += 1
    offset = 0
    while offset < count:
        if prime(number): yield offset, number; offset += 1
        number = 3 if number == 2 else number + 2


def exact_floor_root(n: int, exponent: int) -> int:
    lower, upper = 1, 2
    while upper ** exponent <= n: upper *= 2
    while lower + 1 < upper:
        middle = (lower + upper) // 2
        if middle ** exponent <= n: lower = middle
        else: upper = middle
    return lower


def independent_states(arm: str, shard: int):
    spec = M["arms"][arm]; low, high = M["value_minimum"], M["value_maximum"]
    if arm == "PURE_PRIME_POWER":
        ordinal = 0
        for exponent in range(spec["exponent_min"], spec["exponent_max"] + 1):
            lo = exact_floor_root(low - 1, exponent) + 1; hi = exact_floor_root(high, exponent)
            offset = 0; p = max(2, lo)
            if p > 2 and p % 2 == 0: p += 1
            while p <= hi:
                if prime(p):
                    if ordinal % M["shards"] == shard:
                        yield {"global_ordinal": ordinal, "exponent": exponent, "p_offset_in_root_interval": offset, "p": p}, p**exponent, [(p, exponent)]
                    ordinal += 1; offset += 1
                p = 3 if p == 2 else p + 2
        return
    plist = initial_primes(spec["p_rank_first"] + spec["p_rank_count"] - 1)
    first = spec["p_rank_first"]
    for local in range(spec["p_rank_count"]):
        rank = first + local
        if local % M["shards"] != shard: continue
        p = plist[rank - 1]
        if arm == "REPEATED_POWER_SURGERY":
            for exponent in spec["exponents"]:
                pe = p ** exponent; start = max(p + 1, (low + pe - 1) // pe)
                for offset, q in following_primes(start, spec["q_prime_offsets"]):
                    n = pe * q
                    if n > high: break
                    yield {"p_rank": rank, "p": p, "exponent": exponent, "q_offset": offset, "q": q}, n, [(p, exponent), (q, 1)]
        elif arm == "SQUAREFREE_THREE_BLOCK":
            for qoff, q in following_primes(p + 1, spec["q_prime_offsets_after_p"]):
                pq = p*q; start = max(q + 1, (low + pq - 1) // pq)
                for roff, r in following_primes(start, spec["r_prime_offsets"]):
                    n = pq*r
                    if n > high: break
                    yield {"p_rank": rank, "p": p, "q_offset": qoff, "q": q, "r_offset": roff, "r": r}, n, [(p, 1), (q, 1), (r, 1)]


def coordinate_factorization(arm: str, shard: int, coordinate: dict, n: int) -> list[tuple[int, int]]:
    for expected_coordinate, expected_n, factors in independent_states(arm, shard):
        if expected_coordinate == coordinate:
            if expected_n != n: raise ValueError("coordinate/value mismatch")
            return factors
    raise ValueError("coordinate outside frozen tuple slice")


def candidate(path: pathlib.Path, bundle: pathlib.Path, commit: str) -> dict:
    verify(bundle, commit); gate_sha = sha(bundle / "gate-attestation.json")
    document = json.loads(path.read_text())
    if document.get("schema") != "oeis-a056777-certificate-v1" or document.get("campaign_commit") != commit:
        raise ValueError("certificate identity drift")
    arm, shard, n = document.get("arm"), document.get("shard"), document.get("n")
    if arm not in M["arms"] or not isinstance(shard, int) or not 0 <= shard < M["shards"] or not isinstance(n, int):
        raise ValueError("certificate coordinates drift")
    coordinate = document.get("coordinate")
    if not isinstance(coordinate, dict) or not M["value_minimum"] <= n <= M["value_maximum"]:
        raise ValueError("certificate outside owned finite tuple slice")
    constructed = coordinate_factorization(arm, shard, coordinate, n)
    fn, fn12 = refactor(n), refactor(n + 12)
    if fn != constructed or not has_arm_shape(arm, fn):
        raise ValueError("certificate escape stratum drift")
    expected = expected_certificate(arm, shard, commit, gate_sha, n, fn, fn12, coordinate)
    if expected is None or document != expected:
        raise ValueError("certificate does not exactly refute declaration")
    return document


def chain(path: pathlib.Path, commit: str, arm: str, shard: int) -> tuple[list[dict], str]:
    rows, previous = [], ZERO
    for sequence, line in enumerate(path.read_text(encoding="ascii").splitlines()):
        row = json.loads(line); digest = row.pop("row_sha256", None)
        if row.get("seq") != sequence or row.get("previous_row_sha256") != previous or row.get("campaign_commit") != commit or row.get("arm") != arm or row.get("shard") != shard:
            raise ValueError("ledger identity/order drift")
        actual = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
        if actual != digest: raise ValueError("ledger hash-chain drift")
        row["row_sha256"] = digest; rows.append(row); previous = digest
    if not rows: raise ValueError("empty ledger")
    return rows, previous


def replay_prefix(t: dict, rows: list[dict], certificate_doc: dict | None) -> None:
    arm, shard, visited = t["arm"], t["shard"], t["visited"]
    if not isinstance(visited, int) or visited < 0: raise ValueError("invalid visited count")
    expected_visits = [0] + list(range(M["checkpoint_interval"], visited + 1, M["checkpoint_interval"]))
    if visited % M["checkpoint_interval"] != 0:
        expected_visits.append(visited)
    if [row.get("visited") for row in rows] != expected_visits:
        raise ValueError("incremental checkpoint gap/duplicate drift")
    counts = {"states_evaluated": 0, "equation_hits": 0}
    checkpoints = {row["visited"]: row for row in rows}
    first_candidate = None; best = None
    last_coordinate = last_n = None
    state_iterator = independent_states(arm, shard)
    for ordinal in range(visited):
        try: coordinate, n, constructed = next(state_iterator)
        except StopIteration as exc: raise ValueError("visited prefix exceeds tuple slice") from exc
        fn, fn12 = refactor(n), refactor(n + 12)
        if fn != constructed: raise ValueError("constructed factor replay mismatch")
        counts["states_evaluated"] += 1
        phi, sigma = values(fn); phi12, sigma12 = values(fn12)
        if phi12 == phi + 12 and sigma12 == sigma + 12: counts["equation_hits"] += 1
        metrics = [abs((sigma12+phi12-2*(n+12))-(sigma+phi-2*n)), abs(phi12-phi-12)+abs(sigma12-sigma-12)]
        if best is None or metrics < best["metrics"]: best = {"metrics": metrics, "coordinate": coordinate, "n": n}
        if first_candidate is None:
            first_candidate = expected_certificate(arm, shard, t["campaign_commit"], t["gate_attestation_sha256"], n, fn, fn12, coordinate)
        last_coordinate, last_n = coordinate, n
        count = ordinal + 1
        if count in checkpoints:
            row = checkpoints[count]
            expected_factors = [list(x) for x in fn]; expected_partner = [list(x) for x in fn12]
            if (row.get("schema") != "oeis-a056777-progress-v1" or row.get("last_coordinate") != coordinate
                    or row.get("last_n") != n or row.get("last_factors_n") != expected_factors
                    or row.get("last_factors_n_plus_12") != expected_partner or row.get("counts") != counts
                    or row.get("strict_best") != best):
                raise ValueError("checkpoint semantic drift")
    zero = checkpoints[0]
    if (zero.get("schema") != "oeis-a056777-progress-v1" or zero.get("last_coordinate") is not None
            or zero.get("last_n") is not None or zero.get("last_factors_n") is not None
            or zero.get("last_factors_n_plus_12") is not None or zero.get("counts") != {name: 0 for name in counts}
            or zero.get("strict_best") is not None):
        raise ValueError("initial checkpoint drift")
    if t.get("tuple_domain_only") is not True or t.get("last_coordinate") != last_coordinate or t.get("last_n") != last_n or t.get("counts") != counts or t.get("strict_best") != best:
        raise ValueError("terminal prefix drift")
    if first_candidate != certificate_doc:
        raise ValueError("candidate omission, mutation, or late attachment")
    if certificate_doc is not None and certificate_doc["n"] != last_n:
        raise ValueError("search continued after certificate")
    if t["terminal_reason"] == "DOMAIN_EXHAUSTED":
        try: next(state_iterator)
        except StopIteration: pass
        else: raise ValueError("false tuple-slice exhaustion")


def validate_worker_error(reason: str, error) -> None:
    if reason == "WORKER_ERROR":
        if not isinstance(error, dict) or set(error) != {"type", "message", "message_sha256"}: raise ValueError("worker error receipt drift")
        if not isinstance(error["type"], str) or not error["type"] or not isinstance(error["message"], str) or len(error["message"]) > 1000: raise ValueError("worker error fields drift")
        if hashlib.sha256(error["message"].encode("utf-8")).hexdigest() != error["message_sha256"]: raise ValueError("worker error digest drift")
    elif error is not None:
        raise ValueError("spurious worker error receipt")


def terminal(ledger_path: pathlib.Path, terminal_path: pathlib.Path, certificate_path: pathlib.Path | None,
             bundle: pathlib.Path, commit: str, arm: str, shard: int) -> dict:
    verify(bundle, commit); t = json.loads(terminal_path.read_text()); rows, final_hash = chain(ledger_path, commit, arm, shard)
    if t.get("schema") != "oeis-a056777-terminal-v1" or t.get("campaign_commit") != commit or t.get("source_commit") != M["formal_conjectures"]["commit"] or t.get("gate_attestation_sha256") != sha(bundle / "gate-attestation.json") or t.get("arm") != arm or t.get("shard") != shard:
        raise ValueError("terminal identity drift")
    if t.get("ledger_rows") != len(rows) or t.get("final_row_sha256") != final_hash or t.get("ledger_sha256") != sha(ledger_path):
        raise ValueError("terminal ledger binding drift")
    if t.get("terminal_reason") not in {"DEADLINE_PREFIX", "DOMAIN_EXHAUSTED", "CERTIFICATE_FOUND", "WORKER_ERROR"}:
        raise ValueError("terminal reason drift")
    error = t.get("worker_error")
    validate_worker_error(t["terminal_reason"], error)
    present = certificate_path is not None
    if bool(t.get("certificate_present")) != present or (t.get("terminal_reason") == "CERTIFICATE_FOUND") != present or (t.get("terminal_reason") == "WORKER_ERROR" and present):
        raise ValueError("certificate/terminal mismatch")
    document = candidate(certificate_path, bundle, commit) if present else None
    if document is not None and (document["arm"], document["shard"]) != (arm, shard):
        raise ValueError("certificate arm/shard mismatch")
    replay_prefix(t, rows, document)
    return t


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("candidate"); p.add_argument("certificate", type=pathlib.Path); p.add_argument("bundle", type=pathlib.Path); p.add_argument("--campaign-commit", required=True)
    p = sub.add_parser("terminal"); p.add_argument("ledger", type=pathlib.Path); p.add_argument("terminal", type=pathlib.Path); p.add_argument("certificate"); p.add_argument("bundle", type=pathlib.Path); p.add_argument("--campaign-commit", required=True); p.add_argument("--arm", choices=M["arms"], required=True); p.add_argument("--shard", type=int, required=True)
    args = parser.parse_args()
    if args.mode == "candidate":
        result = candidate(args.certificate, args.bundle, args.campaign_commit); print(json.dumps({"verified": True, "n": result["n"]}, separators=(",", ":")))
    else:
        terminal(args.ledger, args.terminal, None if args.certificate == "-" else pathlib.Path(args.certificate), args.bundle, args.campaign_commit, args.arm, args.shard); print('{"verified":true}')
    return 0


if __name__ == "__main__": raise SystemExit(main())
