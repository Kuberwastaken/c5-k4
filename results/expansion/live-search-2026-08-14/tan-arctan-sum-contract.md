# Tan-arctan-sum frozen DEVELOPMENT live-search contract

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**. This is prospective finite counterexample
search, not held-out evidence and not a proof attempt. No value with `n >= 5`
may be computed before this contract, implementation, workflow, tests, and
manifest are frozen. Pre-freeze tests are restricted to syntax, serialization,
constructors, synthetic divisibility examples, and the documented values
`n = 1,2,3,4` outside the target domain.

## Exact source and current status

- Repository: `google-deepmind/formal-conjectures`.
- Current `main` pin: `942fb149e782a56c2719c543ab58e093f733acb4`
  (2026-08-14 06:25:12 UTC).
- Source blob: `7ddef467be2c61f20e99945685fe9e2e6bbe2be8`.
- Module: `FormalConjectures/Arxiv/2607.05739/TanArctanSum.lean`.
- Declaration: `Arxiv.«2607.05739».tan_arctan_sum_not_integer`.
- Upstream category at the pin: `research open`.
- Paper: Ken Ono, arXiv:2607.05739v1, *Integer values of
  tan(arctan 1 + ... + arctan n) are rare*.

The focused all-state GitHub searches on 2026-08-14 found only issue #4812 and
PR #4824. Both are closed because #4824 introduced the statement at commit
`f1005eb375cfff3145328f3ca97c648bb24b314d`; its theorem body is still `sorry`
and it is not a resolution. Exact declaration, arXiv identifier, module name,
and conjecturer-name searches found no open or merged resolving issue/PR. The
paper proves a density-one result and explicitly describes the remaining
indices as hard; it does not prove the universal conjecture. This is a current
search result, not a guarantee against unindexed prior art.

The c5-k4 tree was inspected at base commit
`c936765104ee4354e7e1c0809a32761e2c377ecb`. This lane is isolated from other
in-progress development and its eventual Actions execution must name the exact
40-hex commit that contains the frozen files.

## Literal statement and exact finite negation

Let

```text
Z_n = product_(k=1)^n (1+i*k) = A_n+i*B_n,
IsIntegerValue(n) := A_n divides B_n.
```

The declaration asks whether

```text
for every natural n, 5 <= n implies not IsIntegerValue(n).
```

Its exact finite negation/certificate is one natural `n >= 5` and integers
`A_n,B_n,m` such that

```text
B_n = m*A_n,
A_n+i*B_n = product_(k=1)^n (1+i*k).
```

The product is evaluated by the exact recurrence

```text
A_0=1, B_0=0,
A_n=A_(n-1)-n*B_(n-1),
B_n=n*A_(n-1)+B_(n-1).
```

Writing `omega_n=product_(k=1)^n(1+k^2)`, every step also checks

```text
A_n^2+B_n^2=omega_n.
```

The exact reduced denominator is
`|A_n|/gcd(|A_n|,|B_n|)` when `A_n != 0`; integrality is exactly the assertion
that this denominator is one. If `A_n=0`, the positive norm forces `B_n!=0`,
so the formal divisibility predicate is false as intended. For a certificate,
the worker independently replays the direct Gaussian product and checks

```text
omega_n=A_n^2*(1+m^2).
```

Thus the certificate uses the same integrality/divisibility content as the
upstream declaration and the paper's norm argument. It does not substitute a
near-pole score, floating tangent value, or asymptotic proxy for the objective.

## Mandatory sanity gate

Before any `n >= 5` evaluation, every arm must reproduce by recurrence and an
independent balanced Gaussian-product tree

```text
(A_0,B_0,omega_0)=(1,0,1)
(A_1,B_1,omega_1)=(1,1,2)
(A_2,B_2,omega_2)=(-1,3,10)
(A_3,B_3,omega_3)=(-10,0,100)
(A_4,B_4,omega_4)=(-10,-40,1700).
```

It also checks one synthetic integral pair and one synthetic nonintegral pair.
The gate receipt states `target_values_evaluated: 0`. A failure terminates as
`SANITY_GATE_FAILED` before any target proposal.

## Frozen, separately attributable arms

Each arm stops internally at 54 seconds and is externally killed at 60 seconds.

1. `CATALOGUE` evaluates exactly the twelve exceptional-set indices recorded
   in Remark 3.3 for `E intersect [5,60000]`, as the finite illustration of
   Proposition 3.2:
   `15,17,80,82,395,397,1904,1906,9163,9165,44086,44088`. It is attributable
   to the paper catalogue and may end `DOMAIN_EXHAUSTED` only after all twelve.
2. `GENERIC` advances from the origin through `60001 <= n <= 250000`, excludes
   exact exceptional-wall indices, and evaluates the deterministic 1/16 sample
   selected by SHA-256 of `(seed,n)`, seed `0x54414E4152435441`. It is the
   separately attributable non-wall sample and ends `PROPOSAL_LIMIT` only at
   the frozen maximum.
3. `WALL_NAVIGATION` advances over the same post-paper range but evaluates
   exactly the disjoint exceptional-wall indices satisfying
   `A_n=0` or `2|B_n|>(n+2)|A_n|`, the integer-only form of
   `|x_n|>n/2+1`. It ends `SEARCH_EXHAUSTED` only at the frozen maximum.

The generic and wall arms are disjoint by construction. The catalogue is a
separate source-attributable replay below 60001. Proposal membership and order
are frozen; no target observation may change them.

## Durable records and terminal meanings

Every emitted JSONL row is canonical JSON, SHA-256 chained to the preceding
row, appended with a full-write loop, and `fsync`ed. Progress rows preserve an
incremental exact-state prefix. A divisibility witness is fsynced as a
`candidate_prefix` before its potentially longer independent balanced-product
replay, so a hard kill cannot erase the observed exact witness. A separate
canonical terminal receipt is also written with exclusive creation and
`fsync` and binds the final row hash.

Allowed terminal reasons are `DOMAIN_EXHAUSTED`, `PROPOSAL_LIMIT`,
`SEARCH_EXHAUSTED`, `DEADLINE_PREFIX`, `CERTIFICATE_FOUND`,
`SANITY_GATE_FAILED`, and `WORKER_ERROR`. Process exit or an external timeout
is never reinterpreted as exhaustion; only the already-fsynced prefix survives.

## Publication boundary

The workflow is manual and grants only `contents: read`. It checks out a
caller-supplied exact 40-hex c5-k4 commit with credentials disabled and uploads
evidence artifacts only. This lane performs no README edit, issue, pull
request, release, push, or novelty claim. A `CERTIFICATE_FOUND` receipt remains
development evidence pending independent implementation, fresh source/status
review, and a separate formal certificate.
