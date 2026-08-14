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
profile stores the frozen GAP expression and permutation generators. GAP output
formatting is explicitly disabled before emitting the tab-delimited profile
marker. The parser continues to require exactly one complete marker on one
physical line ending in the explicit `@@END@@` sentinel, and rejects wrapped,
partial, duplicate, or malformed output.

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

A frozen descriptor is scoreable only when its GAP subprocess returns a
complete, independently parsed profile. Nonzero exits and missing, duplicate,
or malformed profile markers produce a durable `descriptor_error` row with
bounded raw stdout, stderr, and return code. They increment neither exact
evaluations nor holds/crossings and do not terminate the rest of an arm. This
distinguishes an unsupported or failed construction from a successful profile
without converting one family endpoint into a whole-worker failure.

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

## Invalid first execution

GitHub Actions run `31792034789` at campaign commit
`2619631aea514dcb19e36463dff8a67573b2f2bc` is classified `INVALID_RUN`.
All three arms reproduced the mandatory sanity controls, but GAP's formatted
stdout wrapped longer permutation-generator output after the marker began.
The strict parser therefore stopped with `malformed GAP profile marker`.
The run is evidence of an emission-protocol defect only. No evaluated target
row, apparent hold, crossing, timeout, or terminal prefix from that run is
admissible as mathematical evidence; the A5 controls provide sanity evidence
and nothing further. Exact artifact identifiers and terminal receipts are
recorded in `solvable-cyclic-subgroups-run-31792034789-invalid.md`.

GitHub Actions run `31792455211` at campaign commit
`1be238c1e6de413b2fd5dce7f9fcbb607ca0cc25` is also classified
`INVALID_RUN`. The framing correction allowed long successful profiles, but
the frozen `Aut(A7)` descriptor returned code zero without any profile marker.
Because that version discarded per-query stdout/stderr before ledger emission,
the construction failure cannot be diagnosed from its preserved arm artifact.
No target row from this run is admitted as a hold, crossing, or denominator;
only the repeated sanity gate is retained. The exact invalid-run record is
`solvable-cyclic-subgroups-run-31792455211-invalid.md`.
