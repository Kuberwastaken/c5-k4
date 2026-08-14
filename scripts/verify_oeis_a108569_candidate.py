#!/usr/bin/env python3
"""Independent replay of frozen OEIS A108569 odd-profile evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
from fractions import Fraction

from prepare_oeis_a108569_gate import MANIFEST, M, parse_bfile, sha, verify

ZERO = "0" * 64
TARGET_ARMS = ("ODD_CORE_PROFILES", "ODD_COLLISION_WALL")
STOPS = ("NO_TRANSLATED_ENDPOINT_PROFILE", "NO_RHO_COLLISION",
         "RHO_COLLISION_NO_TRANSLATION", "SUPPORT_RHO_MISMATCH",
         "EXPONENT_LATTICE_MISMATCH", "RESIDUAL_NONZERO",
         "CATALOGUE_LIFT_CONTROL", "SOURCE_CONTROL", "SURVIVOR")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def odd_primes(count: int) -> list[int]:
    limit = 1024
    while True:
        sieve = bytearray(b"\x01") * (limit + 1); sieve[:2] = b"\x00\x00"
        for p in range(2, math.isqrt(limit) + 1):
            if sieve[p]:
                sieve[p*p:limit+1:p] = b"\x00" * (((limit - p*p) // p) + 1)
        values = [n for n in range(3, limit + 1, 2) if sieve[n]]
        if len(values) >= count:
            return values[:count]
        limit *= 2


def prime(n: int) -> bool:
    if type(n) is not int or n < 2:
        return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0:
            return n == p
    d, twos = n - 1, 0
    while d % 2 == 0:
        d //= 2; twos += 1
    for base in (2,325,9375,28178,450775,9780504,1795265022):
        if base % n == 0:
            continue
        value = pow(base, d, n)
        if value in (1, n - 1):
            continue
        for _ in range(twos - 1):
            value = value * value % n
            if value == n - 1:
                break
        else:
            return False
    return True


def factor_data(factors: list[list[int]]) -> tuple[int, int]:
    product = phi = 1; prior = 1
    if not isinstance(factors, list) or not factors:
        raise ValueError("empty/invalid factor list")
    for item in factors:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("factor-pair shape drift")
        p, e = item
        if not prime(p) or p <= prior or type(e) is not int or e < 1:
            raise ValueError("invalid ordered complete factorization")
        product *= p ** e; phi *= (p - 1) * p ** (e - 1); prior = p
    return product, phi


def support_rows(limit: int, support: int):
    spec = M["profile_catalogues"]; primes = odd_primes(spec["odd_prime_rank_last"])
    if support == 1:
        for i, p in enumerate(primes, 1):
            for e in spec["single_exponents"]:
                value = p ** e
                if value <= limit:
                    yield value, [[p,e]], [i], [e], i - 1
    elif support == 2:
        group = 0
        for i, p in enumerate(primes, 1):
            for j in range(i + 1, len(primes) + 1):
                q = primes[j - 1]
                for e, f in spec["mixed_exponent_pairs"]:
                    value = p ** e * q ** f
                    if value <= limit:
                        yield value, [[p,e],[q,f]], [i,j], [e,f], group
                group += 1
    elif support == 3:
        group = 0
        for i, p in enumerate(primes, 1):
            for j in range(i + 1, len(primes) + 1):
                q = primes[j - 1]
                for h in range(j + 1, len(primes) + 1):
                    r = primes[h - 1]
                    for e, f, g in spec["triple_exponent_tuples"]:
                        value = p ** e * q ** f * r ** g
                        if value <= limit:
                            yield value, [[p,e],[q,f],[r,g]], [i,j,h], [e,f,g], group
                    group += 1
    else:
        raise ValueError("support drift")


def profiles(arm: str):
    ordinal = 0
    for support in M["arms"][arm]["support_cardinalities"]:
        for value, factors, ranks, exponents, group in support_rows(M["k_maximum"], support):
            yield ordinal, value, factors, {"support_cardinality": support, "prime_ranks": ranks,
                "exponents": exponents, "support_group_ordinal": group}
            ordinal += 1


def endpoints() -> dict[int, list[list[int]]]:
    answer = {}; limit = M["endpoint_exclusive_maximum"] - 1
    for support in (1,2,3):
        for value, factors, _ranks, _exponents, _group in support_rows(limit, support):
            prior = answer.setdefault(value, factors)
            if prior != factors:
                raise ValueError("endpoint uniqueness drift")
    return answer


def rho_key(factors: list[list[int]]) -> tuple[int, int]:
    ratio = Fraction(1,1)
    for p, _e in factors:
        ratio *= Fraction(p - 1, p)
    return ratio.numerator, ratio.denominator


def expected_tuples(arm: str, shard: int, source_values: set[int]):
    endpoint_map = endpoints(); ratios = {}
    if arm == "ODD_COLLISION_WALL":
        for value, factors in endpoint_map.items():
            ratios.setdefault(rho_key(factors), []).append((value, factors))
    for ordinal, k, factors_k, profile in profiles(arm):
        if ordinal % M["shards"] != shard:
            continue
        product_k, phi_k = factor_data(factors_k)
        if product_k != k:
            raise ValueError("core factor drift")
        endpoint = k + phi_k
        coordinate = {"profile_ordinal": ordinal, "k": k, "k_factors": factors_k, **profile}
        endpoint_factors = None
        if arm == "ODD_CORE_PROFILES":
            endpoint_factors = endpoint_map.get(endpoint)
            if endpoint_factors is None:
                yield coordinate, {"stop":"NO_TRANSLATED_ENDPOINT_PROFILE","phi_k":phi_k,"endpoint":endpoint}
                continue
            a,b = rho_key(factors_k); desired = (a,a+b)
            if rho_key(endpoint_factors) != desired:
                yield coordinate, {"stop":"SUPPORT_RHO_MISMATCH","support_pair_completed":True,
                    "phi_k":phi_k,"endpoint":endpoint,"desired_endpoint_rho":list(desired)}
                continue
        else:
            a,b = rho_key(factors_k); desired = (a,a+b); collisions = ratios.get(desired,[])
            if not collisions:
                yield coordinate, {"stop":"NO_RHO_COLLISION","phi_k":phi_k,"endpoint":endpoint,
                    "desired_endpoint_rho":list(desired)}
                continue
            endpoint_factors = next((f for value,f in collisions if value == endpoint), None)
            if endpoint_factors is None:
                yield coordinate, {"stop":"RHO_COLLISION_NO_TRANSLATION","support_pair_completed":True,
                    "phi_k":phi_k,"endpoint":endpoint,"desired_endpoint_rho":list(desired),
                    "rho_collision_count":len(collisions)}
                continue
            coordinate["desired_endpoint_rho"] = list(desired)
        a,b = rho_key(factors_k)
        if b * endpoint != (a+b) * k:
            yield coordinate, {"stop":"EXPONENT_LATTICE_MISMATCH","support_pair_completed":True,
                "phi_k":phi_k,"endpoint":endpoint,"desired_endpoint_rho":[a,a+b]}
            continue
        coordinate.update({"desired_endpoint_rho":[a,a+b], "support_rho_identity_verified":True,
                           "exponent_lattice_identity_verified":True,
                           "endpoint_factors":endpoint_factors})
        product_m, phi_m = factor_data(endpoint_factors)
        if product_m != endpoint:
            raise ValueError("endpoint factor product drift")
        residual = phi_m - phi_k
        stop = "SOURCE_CONTROL" if k in source_values else "SURVIVOR" if residual == 0 else "RESIDUAL_NONZERO"
        yield coordinate, {"endpoint":endpoint,"support_pair_completed":True,"phi_k":phi_k,
                           "phi_endpoint":phi_m,"residual":residual,"stop":stop}


def locate(coordinate: dict, arm: str, shard: int, source_values: set[int]) -> dict:
    ordinal = coordinate.get("profile_ordinal")
    if type(ordinal) is not int or ordinal < 0 or ordinal % M["shards"] != shard:
        raise ValueError("coordinate shard ownership drift")
    for expected, outcome in expected_tuples(arm, shard, source_values):
        if expected["profile_ordinal"] == ordinal:
            if canonical(expected) != canonical(coordinate):
                raise ValueError("coordinate payload drift")
            return outcome
        if expected["profile_ordinal"] > ordinal:
            break
    raise ValueError("coordinate outside frozen domain")


BRIDGE = {"index_definition":"i := Nat.count A k","nth_rule":"Nat.nth_count",
          "nth_conclusion":"a i = k","positive_index_predecessor":1,
          "strict_count_rule":"Nat.count_strict_mono",
          "positive_index_reason":"A 1 and 1 < k via Nat.count_strict_mono","conclusion":"0 < i"}


def expected_certificate(document: dict, outcome: dict, commit: str, gate_digest: str) -> dict:
    coordinate = document["coordinate"]; k, phi_k = factor_data(coordinate["k_factors"])
    endpoint, phi_endpoint = factor_data(coordinate["endpoint_factors"])
    if k <= 1 or k % 2 == 0 or endpoint != k + phi_k or phi_endpoint != phi_k:
        raise ValueError("candidate mathematical preconditions fail")
    if outcome.get("stop") != "SURVIVOR":
        raise ValueError("candidate is not a survivor")
    result = {"schema":"oeis-a108569-certificate-v1","campaign_commit":commit,
        "source_commit":M["formal_conjectures"]["commit"],"manifest_sha256":sha(MANIFEST),
        "gate_attestation_sha256":gate_digest,"declaration":M["formal_conjectures"]["declaration"],
        "arm":document["arm"],"shard":document["shard"],"coordinate":coordinate,
        "k":k,"endpoint":endpoint,"factors_k":coordinate["k_factors"],
        "factors_endpoint":coordinate["endpoint_factors"],"phi_k":phi_k,
        "phi_endpoint":phi_endpoint,"residual":0,"odd_counterexample":True,
        "source_catalogue_excluded":True,"enumeration_bridge":BRIDGE,
        "candidate_status":"LITERAL_COUNTEREXAMPLE_PENDING_FORMALIZATION"}
    result["certificate_sha256"] = hashlib.sha256(canonical(result)).hexdigest()
    return result


def candidate(path: pathlib.Path, bundle: pathlib.Path, commit: str) -> dict:
    verify(bundle, commit); raw = path.read_bytes(); document = json.loads(raw)
    if raw != canonical(document):
        raise ValueError("certificate noncanonical")
    arm, shard, coordinate = document.get("arm"), document.get("shard"), document.get("coordinate")
    if arm not in TARGET_ARMS or type(shard) is not int or not 0 <= shard < M["shards"] or not isinstance(coordinate,dict):
        raise ValueError("certificate arm/shard drift")
    source_values = {k for _,k in parse_bfile(bundle/"snapshots/b108569.txt")}
    outcome = locate(coordinate,arm,shard,source_values)
    expected = expected_certificate(document,outcome,commit,sha(bundle/"gate-attestation.json"))
    if raw != canonical(expected) or document["k"] in source_values:
        raise ValueError("certificate payload/source exclusion drift")
    # This validates schema and preconditions, not a Lean proof.
    phi_one = 1
    phi_two = factor_data([[2,1]])[1]
    if document["enumeration_bridge"] != BRIDGE or document["k"] <= 1 or phi_one != phi_two:
        raise ValueError("symbolic Nat.count/Nat.nth bridge drift")
    return document


def chain(path: pathlib.Path, commit: str, arm: str, shard: int) -> tuple[list[dict],str]:
    rows=[]; previous=ZERO
    for seq,raw in enumerate(path.read_bytes().splitlines(keepends=True)):
        full=json.loads(raw); digest=full.get("row_sha256"); body=dict(full); body.pop("row_sha256",None)
        if raw != canonical(full):
            raise ValueError("ledger noncanonical")
        keys={"schema","campaign_commit","arm","shard","visited","last_coordinate","last_outcome",
              "counts","checkpoint_reason","seq","previous_row_sha256"}
        if set(body)!=keys or type(body.get("seq")) is not int or body.get("seq")!=seq or body.get("previous_row_sha256")!=previous:
            raise ValueError("ledger key/order drift")
        if body.get("campaign_commit")!=commit or body.get("arm")!=arm or type(body.get("shard")) is not int or body.get("shard")!=shard:
            raise ValueError("ledger identity drift")
        if body.get("checkpoint_reason") not in {"INITIAL","SUPPORT_PAIR_COMPLETE","EXPONENT_COORDINATE_INTERVAL","FINAL_PREFIX"}:
            raise ValueError("checkpoint reason drift")
        if type(body.get("visited")) is not int or body["visited"]<0 or set(body.get("counts",{}))!=set(STOPS):
            raise ValueError("ledger numeric/count drift")
        if any(type(x) is not int or x<0 for x in body["counts"].values()) or sum(body["counts"].values())!=body["visited"]:
            raise ValueError("ledger count sum drift")
        actual=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode("ascii")).hexdigest()
        if digest!=actual:
            raise ValueError("ledger hash-chain drift")
        rows.append(full); previous=digest
    if not rows:
        raise ValueError("empty ledger")
    return rows,previous


def progress(commit,arm,shard,visited,coordinate,outcome,counts,reason):
    return {"schema":"oeis-a108569-progress-v1","campaign_commit":commit,"arm":arm,"shard":shard,
            "visited":visited,"last_coordinate":coordinate,"last_outcome":outcome,
            "counts":dict(counts),"checkpoint_reason":reason}


def replay(document: dict, rows: list[dict], cert: dict|None, source_values:set[int]) -> None:
    visited=document["visited"]; counts={name:0 for name in STOPS}; expected_rows=[]
    expected_rows.append(progress(document["campaign_commit"],document["arm"],document["shard"],0,None,None,counts,"INITIAL"))
    iterator=expected_tuples(document["arm"],document["shard"],source_values)
    last_coordinate=last_outcome=first_survivor=None; since=0
    for index in range(visited):
        try: coordinate,outcome=next(iterator)
        except StopIteration as exc: raise ValueError("prefix exceeds domain") from exc
        counts[outcome["stop"]]+=1; last_coordinate,last_outcome=coordinate,outcome; since+=1
        if outcome["stop"]=="SURVIVOR" and first_survivor is None:
            first_survivor=(index,coordinate)
        if outcome["stop"]!="SURVIVOR" and (outcome.get("support_pair_completed") is True or since>=M["checkpoint_minimum_exponent_coordinates"]):
            reason="SUPPORT_PAIR_COMPLETE" if outcome.get("support_pair_completed") is True else "EXPONENT_COORDINATE_INTERVAL"
            expected_rows.append(progress(document["campaign_commit"],document["arm"],document["shard"],index+1,coordinate,outcome,counts,reason)); since=0
    if cert is None and since:
        expected_rows.append(progress(document["campaign_commit"],document["arm"],document["shard"],visited,last_coordinate,last_outcome,counts,"FINAL_PREFIX"))
    stripped=[]
    for row in rows:
        copy=dict(row); copy.pop("row_sha256"); copy.pop("seq"); copy.pop("previous_row_sha256"); stripped.append(copy)
    if canonical(stripped)!=canonical(expected_rows):
        raise ValueError("checkpoint boundary/semantic replay drift")
    semantic_observed={"counts":document["counts"],"last_coordinate":document["last_coordinate"],"last_outcome":document["last_outcome"]}
    semantic_expected={"counts":counts,"last_coordinate":last_coordinate,"last_outcome":last_outcome}
    if document.get("odd_profile_domain_only") is not True or canonical(semantic_observed)!=canonical(semantic_expected):
        raise ValueError("terminal prefix drift")
    if cert is not None:
        if first_survivor!=(visited-1,cert["coordinate"]):
            raise ValueError("candidate not first survivor/final state")
    elif first_survivor is not None:
        raise ValueError("candidate omission")
    if document["terminal_reason"]=="DOMAIN_EXHAUSTED":
        try: next(iterator)
        except StopIteration: pass
        else: raise ValueError("false domain exhaustion")


def terminal(ledger_path:pathlib.Path, terminal_path:pathlib.Path, certificate_path:pathlib.Path|None,
             bundle:pathlib.Path, commit:str, arm:str, shard:int)->dict:
    gate=verify(bundle,commit); raw=terminal_path.read_bytes(); document=json.loads(raw)
    if raw!=canonical(document): raise ValueError("terminal noncanonical")
    rows,tail=chain(ledger_path,commit,arm,shard)
    keys={"schema","campaign_commit","source_commit","gate_attestation_sha256","arm","shard",
          "odd_profile_domain_only","catalogue_rows","visited","last_coordinate","last_outcome",
          "counts","terminal_reason","certificate_present","worker_error","ledger_rows",
          "final_row_sha256","ledger_sha256"}
    if set(document)!=keys: raise ValueError("terminal key drift")
    if type(document.get("shard")) is not int or not 0 <= document["shard"] < M["shards"] or type(document.get("visited")) is not int or document["visited"]<0 or type(document.get("certificate_present")) is not bool:
        raise ValueError("terminal numeric/boolean drift")
    if set(document.get("counts",{})) != set(STOPS) or any(type(x) is not int or x < 0 for x in document["counts"].values()) or sum(document["counts"].values()) != document["visited"]:
        raise ValueError("terminal count drift")
    if document.get("schema")!="oeis-a108569-terminal-v1" or (document.get("arm"),document.get("shard"))!=(arm,shard):
        raise ValueError("terminal identity drift")
    if document.get("campaign_commit")!=commit or document.get("source_commit")!=M["formal_conjectures"]["commit"] or document.get("gate_attestation_sha256")!=sha(bundle/"gate-attestation.json"):
        raise ValueError("terminal binding drift")
    if document.get("catalogue_rows")!=gate["table"]["catalogue"]["rows"] or type(document.get("ledger_rows")) is not int or document.get("ledger_rows")!=len(rows) or document.get("final_row_sha256")!=tail or document.get("ledger_sha256")!=sha(ledger_path):
        raise ValueError("terminal catalogue/ledger drift")
    reason=document.get("terminal_reason")
    if reason not in {"CAP_PREFIX","DOMAIN_EXHAUSTED","CERTIFICATE_FOUND","WORKER_ERROR"}:
        raise ValueError("terminal reason drift")
    error=document.get("worker_error")
    if reason=="WORKER_ERROR":
        if not isinstance(error,dict) or set(error)!={"type","message","message_sha256"} or any(type(error[key]) is not str for key in error) or hashlib.sha256(error["message"].encode()).hexdigest()!=error["message_sha256"]:
            raise ValueError("worker error receipt drift")
    elif error is not None: raise ValueError("spurious worker error")
    present=certificate_path is not None
    if document["certificate_present"]!=present or (reason=="CERTIFICATE_FOUND")!=present:
        raise ValueError("terminal/certificate race drift")
    cert=candidate(certificate_path,bundle,commit) if present else None
    source_values={k for _,k in parse_bfile(bundle/"snapshots/b108569.txt")}
    replay(document,rows,cert,source_values); return document


def main()->int:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="mode",required=True)
    c=sub.add_parser("candidate"); c.add_argument("certificate",type=pathlib.Path); c.add_argument("bundle",type=pathlib.Path); c.add_argument("--campaign-commit",required=True)
    t=sub.add_parser("terminal"); t.add_argument("ledger",type=pathlib.Path); t.add_argument("terminal",type=pathlib.Path); t.add_argument("certificate"); t.add_argument("bundle",type=pathlib.Path); t.add_argument("--campaign-commit",required=True); t.add_argument("--arm",choices=TARGET_ARMS,required=True); t.add_argument("--shard",type=int,required=True)
    args=parser.parse_args()
    if args.mode=="candidate":
        result=candidate(args.certificate,args.bundle,args.campaign_commit); print(json.dumps({"verified":True,"k":result["k"]},separators=(",",":")))
    else:
        terminal(args.ledger,args.terminal,None if args.certificate=="-" else pathlib.Path(args.certificate),args.bundle,args.campaign_commit,args.arm,args.shard); print('{"verified":true}')
    return 0


if __name__=="__main__":
    raise SystemExit(main())
