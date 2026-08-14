# Graffiti³ Conjecture 13: verified base-two counterexample

Date: 2026-08-14 UTC

Status: **VERIFIED COUNTEREXAMPLE; APPARENTLY UNRECORDED CONNECTION; NO PUBLIC ACTION**

Authoritative campaign commit: `b1fd235404b6d2fa2f7224e2b63e1b69dd951674`

Authoritative GitHub Actions run:
[`31797234229`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31797234229)

## Statement and source reading

Conjecture 13 of Randy Davila's January 2026 preprint
[*Graffiti³: Compact Theory Libraries for Automated Mathematical Discovery*](https://doi.org/10.21203/rs.3.rs-8493329/v1)
states, for a fixed base `b >= 2` and empirically `b=2`, that

```text
phi(n) <= (9/19)n  implies that n is not a Fermat pseudoprime to base b.
```

Thus a base-two counterexample is an odd composite `n` satisfying both

```text
19*phi(n) <= 9*n
pow(2,n-1,n) = 1.
```

The source's integer snapshot ends at `2,000,000`, so the frozen campaign
searched beyond that boundary. The snapshotted PDF is text-based, has 42
pages, requires no OCR, and has SHA-256
`9758ec4530febf62bbcee35bd5804d2dda9e226a0878b082a25eaf1c7e4a9f7a`.

## Canonical counterexample

The first crossing in the frozen sorted A001567 catalogue after the source
boundary is

```text
n = 81,722,145
  = 3 * 5 * 17 * 29 * 43 * 257,

phi(n)       = 38,535,168,
19*phi(n)    = 732,168,192,
9*n          = 735,499,305,
9*n-19phi(n) = 3,331,113 > 0,
2^(n-1) mod n = 1.
```

Therefore `n` satisfies the premise and is a Fermat pseudoprime to base two,
contradicting Conjecture 13. It is not a Carmichael number. The normalized
certificate is
[`graffiti3-conjecture13-candidate-81722145.json`](graffiti3-conjecture13-candidate-81722145.json).

This number is A001567 index 1886. Index 355 is the first frozen sequence entry
above `2,000,000`; an independent exact scan of all 1,532 entries from indices
355 through 1886 found exactly one crossing, this one. This establishes the
first crossing in that locked sorted sequence, not the globally least integer
counterexample.

## Independent evidence audit

Independent replay verified:

- all 73 checksum manifests and all 518 files they bind;
- the exact campaign, manifest, source PDF, OEIS snapshot, and gate-attestation
  hashes;
- all 40 gate chunks by recomputing Euler's totient on every integer from 2
  through 2,000,000: 1,999,999 rows, 679,502 premise rows, 354 base-two
  pseudoprimes, and zero crossings;
- both positive controls, 341 and 561: each is a base-two pseudoprime and each
  correctly fails the premise;
- all 72 unique arm/shard assignments, 89,432 hash-chained ledger rows, 72
  execution-status records with every exit code zero, and all terminal bindings;
- every catalogue construction step against the locked A001567 order and every
  Carmichael overlap exclusion;
- all 24 generic blocks by fresh totient and modular-exponentiation scans over
  6,291,456 integers; none of their 38,614 premise composites crossed;
- the complete 10,107-number wall by independently rebuilding the locked
  A002997 plus depth-two Korselt-extension domain and its SHA-256 sharding; and
- all nine emitted candidate certificates by independent prime-factor,
  totient, Korselt, inequality, and modular-residue replay.

There were no worker errors, malformed rows, child timeouts, or deadline
prefixes.

## Arm dispositions

| Arm | Proposed | Exact | Overlap excluded | Crossings | Terminals |
|---|---:|---:|---:|---:|---|
| catalogue | 79,076 | 72,716 | 6,360 | 9 | 9 certificate; 15 exhausted |
| generic | 6,291,456 | 6,291,456 | 0 | 0 | 24 exhausted |
| wall navigation | 10,107 | 10,107 | 0 | 0 | 24 exhausted |

The nine independently verified catalogue certificates are:

```text
81,722,145
8,700,387,585
36,693,243,105
116,291,248,305
167,041,654,305
202,228,602,465
228,565,392,105
421,114,213,185
503,686,014,105
```

Each is a non-Carmichael base-two pseudoprime with `19*phi(n) <= 9*n`.
The first is canonical because it is the earliest locked-sequence crossing.

## Current standing and novelty discipline

The source still presents Conjecture 13 as open, and the located scholarly
record remains Research Square version 1. The current OEIS A001567 and A002997
b-files exactly match the frozen hashes. Current exact-number, exact-formula,
title/DOI, scholarly-web, GitHub code/issue, author-repository, and related
pseudoprime searches found no prior public record connecting any of these
numbers to Graffiti³ Conjecture 13.

The number `81,722,145` itself is not new: OEIS already records it as a
base-two pseudoprime, including in A328691 for a different abundancy-index
property. The apparently new item is the observation and exact certificate
that it violates the Graffiti³ totient threshold. “Apparently unrecorded” is a
dated public-search conclusion, not an absolute priority claim; private or
unindexed work cannot be excluded.

This target is neither a DeepMind `formal-conjectures` declaration nor a
Written on the Wall I target. No issue, pull request, release, or other public
action is authorized or taken by this result. Frozen scope and source details
remain in the [contract](graffiti3-conjecture13-contract.md),
[manifest](graffiti3-conjecture13-manifest.json), and
[source/status attestation](graffiti3-conjecture13-source-status.md).
