# OEIS A063880 DEVELOPMENT: all frozen MITM domains exhausted, no candidate

Date: 2026-08-14 UTC

Status: **FINITE DEVELOPMENT BOUNDED ZERO; NO CANDIDATE; NO RELEASE**

Campaign commit: `9b00f90f55147e3365346ae5b72649cd7ea9af1f`

GitHub Actions run:
[`31801225563`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31801225563)

This was a prospective, target-specific **DEVELOPMENT** trial of exact
Euler-factor wall navigation. It is useful negative method data, but it is not
a positive crossing and it is not a claim that either conjecture is true.

## Target and frozen meaning

At the frozen `google-deepmind/formal-conjectures` commit
`942fb149e782a56c2719c543ab58e093f733acb4`, the declarations
`OeisA63880.mod_216_of_a` and `OeisA63880.unique_primitive_108` are
`research open`. A063880 consists of positive integers satisfying

```text
sigma(n) = 2 * usigma(n).
```

For `n = prod p^e`, the worker used the exact factorization

```text
sigma(n) / usigma(n) = prod (1 + p + ... + p^e) / (1 + p^e).
```

Exponent-one primes contribute one, so the frozen search works on powerful
cores. A candidate had to have an exact rational product of two, lie in
`[10^18,10^36]`, satisfy the arm's factor and largest-prime restrictions, and
either fall outside the residue class `108 mod 216` or be a primitive core
other than `108`.

The locked OEIS source says only that `108` is the unique primitive term
**strictly below** `10^18`; it does not cover equality. Accordingly, the frozen
candidate universe begins at exactly `10^18`. The separate source report that
the residue observation was checked through `10^7` is not promoted to a
`10^18` residue claim.

## Independent evidence audit

Independent replay verified:

- the successful workflow-dispatch run, exact campaign head, all 74 successful
  jobs, and all 73 non-expired artifact identities;
- one gate plus exactly three arms by shards `0..23`, giving 72 complete and
  unique worker assignments with no missing or duplicate pair;
- all 73 `SHA256SUMS` manifests, covering 548 non-manifest artifact files;
- the immutable Lean snapshot, OEIS source record, and 10,000-row b-file at
  their frozen hashes;
- all 40 contiguous gate chunks and all 10,000 b-file rows by independent
  factorization, with `sigma=2*usigma`, residue `108 mod 216`, and powerful
  core `108` on every row;
- all 147,554 ledger rows, canonical predecessor/hash chains, exact rational
  state order, left-ordinal sharding, right-complement matches, and counters;
- all 72 terminal-to-ledger bindings, execution receipts with every exit code
  zero, and semantic `DOMAIN_EXHAUSTED` claims; and
- zero worker-error rows, candidate files, and certificate files.

The run and artifacts are bound to gate-attestation file SHA-256
`b7bd94825c44515118049ab52fcf89f703756dcc1009d8a40582e0b80cdb0b75`.
The other principal locks are:

- frozen manifest SHA-256:
  `4330c9fc726fa00ceba60535e8738fd1f02e03fff3c27a9c446b29436ccfed9a`;
- source/status attestation SHA-256:
  `f8c5b12988a47c0bf54c66923e733a53f204ebb7227bb92d7d8645db0be3d9d1`;
- Lean module SHA-256:
  `b50d00e13735613cbe37bd3a25c19130874e8f036ca2a0e3c1aceb177a33c683`;
- OEIS source-record SHA-256:
  `9beab80f0dce23835cd26015df59848a13b9f07e41df142305efca75bd2dd20c`;
- OEIS b-file SHA-256:
  `015517f2a16615e0c9ac93931b4f798040b6693cdf10afeb39408829bca417b9`.

## Authoritative arm totals

| Arm | Right states | Left states | Ledger rows | Raw exact-ratio matches | Candidate-eligible matches | Terminals | Disposition |
|---|---:|---:|---:|---:|---:|---|---|
| `CATALOGUE` | 49,395 | 87,778 | 92,410 | 1 | 0 | 24 `DOMAIN_EXHAUSTED` | frozen candidate domain exhausted |
| `GENERIC` | 21,883 | 4,096 | 6,160 | 1 | 0 | 24 `DOMAIN_EXHAUSTED` | frozen candidate domain exhausted |
| `WALL_NAVIGATION` | 24,656 | 46,656 | 48,984 | 1 | 0 | 24 `DOMAIN_EXHAUSTED` | frozen candidate domain exhausted |

Totals: 95,934 right-half states, 138,530 left-half states, 147,554
ledger rows, three operational raw exact-ratio matches, zero candidate-eligible
matches, zero deadline prefixes, zero errors, zero candidates, and zero
certificates.

All three raw matches reconstruct the same historical control

```text
108 = 2^2 * 3^3,
(7/5) * (10/7) = 2.
```

It appears once in each arm's raw half-state traversal because their low-prime
constructor coordinates overlap before final acceptance. In `CATALOGUE` it is
rejected because `108 < 10^18`. In `GENERIC` and `WALL_NAVIGATION` it is also
outside the required largest-prime bands. Thus the count is three operational
matches but one unique known core, not three new mathematical objects.

## Scope

The bounded zero applies only to the three finite prime/exponent/factor-cap
domains frozen in [`manifest.json`](manifest.json). It does not cover all
powerful numbers, all primitive A063880 terms, or all members of A063880. Full
exhaustion here means the exact frozen MITM candidate domains were completed;
it is not global conjecture exhaustion.

No issue, pull request, Lean certificate, release, or README claim follows from
this zero. The source, historical boundary, domains, and execution discipline
remain recorded in [`CONTRACT.md`](CONTRACT.md) and
[`source-status-attestation.json`](source-status-attestation.json).
