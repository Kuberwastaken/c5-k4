#!/usr/bin/env python3
"""Algebraic A056777 mixed square/triple surgery; never scans flat n values."""
from __future__ import annotations

import argparse, bisect, hashlib, json, math, os, pathlib, signal
from contextlib import contextmanager
from dataclasses import dataclass

from prepare_oeis_a056777_v2_gate import MANIFEST, M, sha, verify

ZERO = "0" * 64


class Deadline(Exception): pass


def alarm_handler(_signum, _frame): raise Deadline()


@contextmanager
def block_alarm():
    old = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try: yield
    finally: signal.pthread_sigmask(signal.SIG_SETMASK, old)


def error_receipt(exc: BaseException) -> dict:
    message = str(exc)[:1000]
    return {"type": type(exc).__name__, "message": message,
            "message_sha256": hashlib.sha256(message.encode()).hexdigest()}


def atomic_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("x", encoding="ascii") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":")); stream.write("\n")
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try: os.fsync(directory)
    finally: os.close(directory)


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

    def close(self): self.stream.close()


def first_primes(count: int) -> list[int]:
    bound = 32
    while True:
        flags = bytearray(b"\x01") * (bound+1); flags[:2] = b"\x00\x00"
        for divisor in range(2, math.isqrt(bound)+1):
            if flags[divisor]: flags[divisor*divisor:bound+1:divisor] = b"\x00" * (((bound-divisor*divisor)//divisor)+1)
        answer = [n for n, flag in enumerate(flags) if flag]
        if len(answer) >= count: return answer[:count]
        bound *= 2


def is_prime(n: int) -> bool:
    if n < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    odd, twos = n-1, 0
    while odd % 2 == 0: odd //= 2; twos += 1
    for base in (2,325,9375,28178,450775,9780504,1795265022):
        if base % n == 0: continue
        x = pow(base, odd, n)
        if x in (1, n-1): continue
        for _ in range(twos-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True


@dataclass(frozen=True, order=True)
class Block:
    product: int
    t_rank: int
    u_rank: int
    t: int
    u: int


def semiprime_index(primes: list[int]) -> tuple[list[Block], list[int]]:
    blocks = [Block(primes[i]*primes[j], i+1, j+1, primes[i], primes[j])
              for i in range(len(primes)) for j in range(i+1, len(primes))]
    blocks.sort(); return blocks, [block.product for block in blocks]


def ceil_div(a: int, b: int) -> int: return -((-a)//b)


def denominator_window(arm: str, r: int, primes: list[int], qmax: int) -> tuple[int, int]:
    """Conservative exact consequence of positive p and the lower value band."""
    center = 2*r*r; min_sum, max_sum = primes[0]+primes[1], primes[-2]+primes[-1]
    if arm == "REPEATED_LOWER":
        pmin = ceil_div(M["value_minimum"], r*r)
        coefficient = max(abs(2*min_sum-2*r-1), abs(2*max_sum-2*r-1))
        numerator_bound = 24 + qmax*coefficient
    else:
        pmin = ceil_div(M["value_minimum"], qmax)
        numerator_bound = max(abs(12+r*r*(2*r+1-2*min_sum)), abs(12+r*r*(2*r+1-2*max_sum)))
    width = numerator_bound//pmin + 1
    return max(1, center-width), center+width


def prior_squarefree_coordinate(t_rank: int, u_rank: int, t: int, u: int, p: int) -> bool:
    prior = M["prior_freeze"]
    if t_rank > prior["squarefree_smallest_rank_last"] or u_rank-t_rank > prior["squarefree_middle_prime_offsets"] or p <= u:
        return False
    start = max(u+1, ceil_div(M["value_minimum"], t*u))
    value = max(2, start)
    if value > 2 and value % 2 == 0: value += 1
    for _ in range(prior["squarefree_terminal_prime_offsets"]):
        while not is_prime(value): value = 3 if value == 2 else value+2
        if value == p: return True
        if value > p: return False
        value = 3 if value == 2 else value+2
    return False


STOP_NAMES = ("ZERO_DENOMINATOR", "K_SIGN", "K_NONINTEGRAL", "PARTNER_NONINTEGRAL",
              "PRODUCT_MISMATCH", "NONCANONICAL", "BAND", "NONPRIME", "PRIOR_FROZEN", "C_IDENTITY", "SURVIVOR")


def evaluate(arm: str, r: int, block: Block) -> dict:
    t, u, qblock, total = block.t, block.u, block.product, block.t+block.u
    if arm == "REPEATED_LOWER":
        denominator = qblock-2*r*r; numerator = 24+qblock*(2*total-2*r-1)
    else:
        denominator = 2*r*r-qblock; numerator = 12+r*r*(2*r+1-2*total)
    base = {"denominator": denominator, "numerator": numerator}
    if denominator == 0: return {**base, "stop": "ZERO_DENOMINATOR"}
    if numerator*denominator <= 0: return {**base, "stop": "K_SIGN"}
    if numerator % denominator: return {**base, "stop": "K_NONINTEGRAL"}
    p = numerator//denominator
    if arm == "REPEATED_LOWER":
        partner_numerator = p+2*r+1-2*total
        if partner_numerator % 2: return {**base, "p": p, "stop": "PARTNER_NONINTEGRAL"}
        q = partner_numerator//2; n = r*r*p; m = qblock*q
        product_ok = m == n+12; canonical = r < p and t < u < q
    else:
        q = 2*p+2*total-2*r-1; n = qblock*p; m = r*r*q
        product_ok = m == n+12; canonical = t < u < p and r < q
    values = {**base, "p": p, "q": q, "n": n, "m": m}
    if not product_ok: return {**values, "stop": "PRODUCT_MISMATCH"}
    if not canonical: return {**values, "stop": "NONCANONICAL"}
    if not (M["value_minimum"] <= n <= M["value_maximum"] and m == n+12): return {**values, "stop": "BAND"}
    if not (is_prime(p) and is_prime(q)): return {**values, "stop": "NONPRIME"}
    if arm == "REPEATED_UPPER" and prior_squarefree_coordinate(block.t_rank, block.u_rank, t, u, p):
        return {**values, "stop": "PRIOR_FROZEN"}
    if arm == "REPEATED_LOWER": c_ok = r*p+r*(r-1) == (total-1)*q+(qblock-total+1)
    else: c_ok = (total-1)*p+(qblock-total+1) == r*q+r*(r-1)
    return {**values, "stop": "SURVIVOR" if c_ok else "C_IDENTITY"}


def tuples(arm: str, shard: int):
    primes = first_primes(M["block_prime_rank_last"]); blocks, products = semiprime_index(primes); qmax = products[-1]
    for rank in range(M["r_rank_first"]+shard, M["r_rank_last"]+1, M["shards"]):
        r = primes[rank-1]; low, high = denominator_window(arm, r, primes, qmax)
        left, right = bisect.bisect_left(products, low), bisect.bisect_right(products, high)
        for index in range(left, right):
            block = blocks[index]
            coordinate = {"orientation": arm, "lower_signature": [2,1] if arm == "REPEATED_LOWER" else [1,1,1],
                          "upper_signature": [1,1,1] if arm == "REPEATED_LOWER" else [2,1],
                          "r_rank": rank, "r": r, "t_rank": block.t_rank, "t": block.t,
                          "u_rank": block.u_rank, "u": block.u, "Q": block.product,
                          "window_low": low, "window_high": high}
            yield coordinate, evaluate(arm, r, block)


def arithmetic(factors: list[tuple[int,int]]) -> tuple[int,int]:
    phi = sigma = 1
    for prime, exponent in factors:
        phi *= (prime-1)*prime**(exponent-1); sigma *= (prime**(exponent+1)-1)//(prime-1)
    return phi, sigma


def make_certificate(arm: str, shard: int, commit: str, gate_sha: str, coordinate: dict, outcome: dict) -> dict:
    r, t, u, p, q, n = coordinate["r"], coordinate["t"], coordinate["u"], outcome["p"], outcome["q"], outcome["n"]
    fn = [(r,2),(p,1)] if arm == "REPEATED_LOWER" else [(t,1),(u,1),(p,1)]
    fm = [(t,1),(u,1),(q,1)] if arm == "REPEATED_LOWER" else [(r,2),(q,1)]
    fn.sort(); fm.sort(); phi, sigma = arithmetic(fn); phim, sigmam = arithmetic(fm)
    if phim != phi+12 or sigmam != sigma+12: raise RuntimeError("survivor failed defining equations")
    return {"schema":"oeis-a056777-v2-certificate-v1","campaign_commit":commit,
            "source_commit":M["formal_conjectures"]["commit"],"manifest_sha256":sha(MANIFEST),
            "gate_attestation_sha256":gate_sha,"declaration":M["formal_conjectures"]["declaration"],
            "arm":arm,"shard":shard,"coordinate":coordinate,"n":n,"factors_n":[list(x) for x in fn],
            "factors_n_plus_12":[list(x) for x in fm],"phi_n":phi,"phi_n_plus_12":phim,
            "sigma_n":sigma,"sigma_n_plus_12":sigmam,"composite_n":True,"comes_from_prime_quadruple":False}


def progress(commit: str, arm: str, shard: int, visited: int, coordinate, outcome, counts: dict) -> dict:
    return {"schema":"oeis-a056777-v2-progress-v1","campaign_commit":commit,"arm":arm,"shard":shard,
            "visited":visited,"last_coordinate":coordinate,"last_outcome":outcome,"counts":dict(counts)}


def run(args) -> int:
    verify(args.gate_bundle, args.campaign_commit); gate_sha = sha(args.gate_bundle/"gate-attestation.json")
    ledger = Ledger(args.ledger); counts = {name:0 for name in STOP_NAMES}; visited = 0
    last_coordinate = last_outcome = found = worker_error = None; reason = "DEADLINE_PREFIX"
    signal.signal(signal.SIGALRM, alarm_handler)
    with block_alarm(): ledger.append(progress(args.campaign_commit,args.arm,args.shard,0,None,None,counts))
    signal.alarm(M["internal_seconds"])
    try:
        for coordinate, outcome in tuples(args.arm, args.shard):
            next_counts = dict(counts); next_counts[outcome["stop"]] += 1; next_visited = visited+1
            candidate = make_certificate(args.arm,args.shard,args.campaign_commit,gate_sha,coordinate,outcome) if outcome["stop"] == "SURVIVOR" else None
            with block_alarm():
                if candidate is not None:
                    # The atomic certificate is the candidate state commit.  No
                    # fallible operation may intervene before the corresponding
                    # in-memory state becomes authoritative.  The ledger
                    # intentionally remains at its preceding durable checkpoint.
                    atomic_json(args.certificate, candidate)
                elif next_visited % M["checkpoint_interval"] == 0:
                    ledger.append(progress(args.campaign_commit,args.arm,args.shard,next_visited,coordinate,outcome,next_counts))
                counts, visited, last_coordinate, last_outcome = next_counts, next_visited, coordinate, outcome
                found = candidate
            if found is not None: reason = "CERTIFICATE_FOUND"; signal.alarm(0); break
        else: reason = "DOMAIN_EXHAUSTED"
    except Deadline: reason = "DEADLINE_PREFIX" if found is None else "CERTIFICATE_FOUND"
    except BaseException as exc: reason = "WORKER_ERROR"; worker_error = error_receipt(exc)
    finally:
        signal.alarm(0)
        with block_alarm():
            # A certificate is the atomic final state commit.  Never touch the
            # append-only ledger after it becomes durable: a late write/fsync
            # failure could otherwise leave bytes not represented by seq/hash.
            if found is None and visited % M["checkpoint_interval"] != 0:
                ledger.append(progress(args.campaign_commit,args.arm,args.shard,visited,last_coordinate,last_outcome,counts))
            ledger.close()
            terminal = {"schema":"oeis-a056777-v2-terminal-v1","campaign_commit":args.campaign_commit,
                        "source_commit":M["formal_conjectures"]["commit"],"gate_attestation_sha256":gate_sha,
                        "arm":args.arm,"shard":args.shard,"tuple_domain_only":True,"visited":visited,
                        "last_coordinate":last_coordinate,"last_outcome":last_outcome,"counts":counts,
                        "terminal_reason":reason,"certificate_present":found is not None,"worker_error":worker_error,
                        "ledger_rows":ledger.seq,"final_row_sha256":ledger.previous,"ledger_sha256":sha(args.ledger)}
            atomic_json(args.terminal, terminal)
    return 21 if worker_error is not None else 0


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--arm",choices=M["arms"],required=True); parser.add_argument("--shard",type=int,choices=range(M["shards"]),required=True); parser.add_argument("--campaign-commit",required=True); parser.add_argument("--gate-bundle",type=pathlib.Path,required=True); parser.add_argument("--ledger",type=pathlib.Path,required=True); parser.add_argument("--terminal",type=pathlib.Path,required=True); parser.add_argument("--certificate",type=pathlib.Path,required=True)
    args=parser.parse_args()
    if len(args.campaign_commit)!=40 or any(c not in "0123456789abcdef" for c in args.campaign_commit): raise SystemExit("exact lowercase campaign commit required")
    return run(args)


if __name__ == "__main__": raise SystemExit(main())
