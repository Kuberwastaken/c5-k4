# Graffiti³ Conjecture 13: frozen DEVELOPMENT contract

This contract is frozen before any `n>2,000,000` target is evaluated. It is a
cross-cluster Graffiti³ development trial, not cross-corpus or v1.5 benchmark
evidence.

## Exact wall and separating move

Let `T(n)=9n-19phi(n)`. The premise is `T(n)>=0`. For squarefree `n`,
`phi(n)/n=prod_(p|n)(1-1/p)`. Carmichael numbers remove the modular obstruction:
Korselt's criterion makes every coprime base a Fermat witness. Starting from a
Carmichael `n`, adjoining a prime `q` preserves Korselt when

```text
q-1 | n-1,  q = 1 mod lcm_(p|n)(p-1),  q does not divide n.
```

The move strictly decreases `phi(n)/n`; this prediction is frozen.

## Prepared database gate

Target workers may not compute or repair their own gate. A separate workflow
job must download and hash-check the primary PDF and exact OEIS snapshots,
then replay every `2<=n<=2,000,000` in contiguous chunks. Every child chunk has
an individual four-second hard cap and a content-addressed receipt. The
aggregator accepts only exact gap-free coverage, zero literal crossings, and
the fixed 341/561 calibration controls. It writes a self-hashed attestation.
The attestation is also bound to the exact immutable campaign commit; a worker
at any other commit rejects it before proposing a target.

The gate artifact contains the attestation, all chunk receipts, and the two
hash-locked OEIS files. Every target worker independently verifies every hash,
coverage boundary, receipt, control, and zero count. Missing, partial, stale,
or tampered evidence ends `SANITY_GATE_FAILED` before a target proposal.

## Frozen arms

All arms have 24 shards, a 54-second internal deadline inside a 60-second
external process cap, fresh hash-chained `fsync` ledgers, and no adaptive
replacement family.

- `CATALOGUE`: first 100,000 locked A001567 values above the boundary, split
  contiguously. Exact Carmichael rows are excluded, making it disjoint from the
  wall arm.
- `GENERIC`: one SHA-256-selected aligned block of width `2^18` per shard in
  `[2,000,001,2^40)`. This bound keeps every exact factorization inside the
  factorization envelope certified from the locked snapshots. Each block scan
  is a separately capped four-second child.
  Locked A001567/A002997 identities are excluded.
- `WALL_NAVIGATION`: locked A002997 Carmichael values above the boundary plus
  depth-one and depth-two exact Korselt prime extensions of locked Carmichael
  seeds at or below the boundary. Identities are factor-tuple canonicalized and
  assigned by SHA-256 modulo 24. Depth-two expansion continues only while the
  parent remains inside the locked snapshot factorization envelope; all emitted
  identities are below `2^64`.

Arm classification is enforced before scoring. Every target satisfies
`n>2,000,000`; a boundary violation is a worker error, never calibration.

## Candidate and output discipline

A candidate file contains `n`, its complete factorization, `phi(n)`, exact
margin, modular residue, and a structured arm-construction witness. A separate
standard-library verifier rechecks
deterministic 64-bit primality, product and totient reconstruction,
compositeness, oddness, boundary, generic block identity or complete Korselt
extension chain, arm classification, and modular power.

Every proposal/block receipt and terminal is appended, flushed, and `fsync`ed.
Allowed terminals are `DOMAIN_EXHAUSTED`, `DEADLINE_PREFIX`,
`CERTIFICATE_FOUND`, `SANITY_GATE_FAILED`, and `WORKER_ERROR`. No workflow has
write permissions or performs a public action.
