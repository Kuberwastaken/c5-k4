# Solvability from cyclic-subgroup count: frozen DEVELOPMENT contract

Date: **2026-08-14 UTC**. Evidence split: **DEVELOPMENT**.

No nonsolvable target group beyond the source-documented `A5` sanity row may
be evaluated before this contract, implementation, and manifest are committed.
Constructor-only tests and source/status inspection are permitted.

## Source and logical resolution

The target is
`FormalConjectures/Arxiv/2604.08040/Conjecture5_5.lean::solvable_of_cyc_lt`
at `google-deepmind/formal-conjectures@942fb149e782a56c2719c543ab58e093f733acb4`,
blob `cb099f09a40eab0149b3332979d92e190ef44def`. It remains tagged
`research open`. The exact status audit is stored in
`solvable-cyclic-subgroups-source-status.json`.

For a finite nonsolvable group `G`, define

```text
R(G) = cyc(G) - 2^(pi(G)+2).
```

The intended conjecture is equivalent to `R(G) >= 0` for every nonsolvable
finite group. A counterexample is one explicit nonsolvable finite group with
`R(G) < 0`. The Lean declaration is answer-wrapped, so such a witness resolves
the intended finite-universal RHS as false; it does not contradict an opaque
`answer(sorry)` value by itself.

## Exact primary evaluator

For every GAP group construction, the primary evaluator obtains the conjugacy
classes of elements and records the exact element-order histogram. It computes

```text
cyc(G) = sum_d count(elements of order d) / phi(d).
```

Python independently checks divisibility by `phi(d)`, the total element count,
the cyclic-subgroup sum, distinct prime support, threshold, and residual. Every
profile stores the frozen GAP expression and permutation generators.

## Mandatory sanity gate

Every arm must reproduce, before target evaluation:

- `S3`: order 6, five cyclic subgroups, solvable;
- `A4`: order 12, eight cyclic subgroups, solvable;
- `A5`: order 60, 32 cyclic subgroups, nonsolvable, and exact residual zero.

`A5` is the only nonsolvable group allowed in pre-freeze validation, and tests
use a source-documented serialized fixture rather than invoking GAP.

## Frozen arms

Each arm has a 54-second internal stop and a separate 60-second process cap.
Every individual GAP query is separately capped at eight seconds so a difficult
group cannot consume the terminal-receipt margin.

### CATALOGUE

In increasing `(order, SmallGroup id)` order, exhaust every nonsolvable GAP
SmallGroup of order 60 through 255. `DOMAIN_EXHAUSTED` is permitted only after
the complete finite range is consumed. A deadline produces `DEADLINE_PREFIX`.

### GENERIC

For every SmallGroups-supported order 256 through 2000, obtain the nonsolvable
IDs, rank them by SHA-256 of `(source blob, order, id)`, and select at most four
per order. The global ceiling is 1,024 selected groups. This arm terminates as
`PROPOSAL_LIMIT`, `SEARCH_EXHAUSTED`, or `DEADLINE_PREFIX`, never as exhaustive
coverage of all finite groups.

### WALL_NAVIGATION

Track `rho(G)=cyc(G)/2^pi(G)`, whose conjectured wall is `rho=4`. Starting with
the exact `A5` wall, replace the simple socle using the source theorem's
shortlist `A5,A6,A7,A8,M11,J1,PSU(3,4),Sz(8)` and `PSL(2,q)` for frozen prime
powers through 64. Evaluate each simple group and its automorphism-group
endpoint. `A5 x C_p` for `p=7,11,13` are calibration-only coprime product
controls. They cannot be post-result retuned into a different family.

## Durable evidence and terminal meanings

Python writes canonical JSONL rows with a SHA-256 predecessor chain. Every row
and terminal/certificate document is flushed through `fsync`. Allowed terminal
reasons are `DOMAIN_EXHAUSTED`, `PROPOSAL_LIMIT`, `SEARCH_EXHAUSTED`,
`DEADLINE_PREFIX`, `CERTIFICATE_FOUND`, `SANITY_GATE_FAILED`, and
`WORKER_ERROR`. A per-group timeout is recorded and is not a hold.

## Certificate and independent replay

A primary candidate document contains the group expression, permutation
generators, order, prime support, element-order histogram, exact cyclic count,
threshold, and residual. A separately launched GAP verifier must enumerate
conjugacy classes of subgroups and sum the sizes of those whose representative
is cyclic. Only agreement on group order, prime support, nonsolvability, cyclic
count, and a strict negative residual permits `CERTIFICATE_FOUND`.

No README edit, release, issue, pull request, or public claim is authorized by
this harness. Any candidate requires a fresh novelty audit and no-`sorry` Lean
certificate before promotion.
