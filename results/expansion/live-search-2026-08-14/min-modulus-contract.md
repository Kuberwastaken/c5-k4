# Minimum-modulus live-search contract

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**. This is a prospective method-development
trial, not held-out Method v1.5 evidence. No target value may be evaluated
before this contract and its machine-readable manifest are frozen. Source and
status inspection, syntax checks, constructor-only tests, and tests on synthetic
or explicitly documented calibration controls are permitted before execution.

## Pinned source and status

- Repository: `google-deepmind/formal-conjectures`.
- Commit: `942fb149e782a56c2719c543ab58e093f733acb4`.
- Module: `FormalConjectures/Arxiv/2607.08366/MinModulus.lean`.
- Declaration: `Arxiv.2607.08366.min_modulus`, lines 61--65 at the pin.
- Source: arXiv:2607.08366v2, *Minimum modulus for the unique multiset-sum
  problem*, Jose A. R. Fonollosa.

At the pin the declaration is tagged `@[category research open]`. Formal
Conjectures issue #4811 was closed when statement-introduction PR #4829 merged;
neither is a mathematical resolution. An all-state exact source/name search on
2026-08-14 found no resolving issue, pull request, or merged commit. The source
paper proves that the super-increasing set is first valid at the displayed
modulus and explicitly leaves optimality over all size-`n` residue sets as a
conjecture.

## Literal statement and negation

For

```text
M(n) = 2^n - 2^(floor(log_2 n)),
```

the intended right-hand side says that for every `n >= 2`, every positive
`N < M(n)`, and every size-`n` set `A` of residues modulo `N`, `A` is not valid.
Validity means that the all-ones multiplicity vector is the unique nonnegative
integer multiplicity vector of total mass `n` whose `A`-weighted sum agrees
with the sum of the elements of `A` modulo `N`.

The finite-witness negation is

```text
exists n N A,
  2 <= n and 0 < N and N < M(n) and |A| = n and IsValidMod(A).
```

Because the upstream declaration is `answer(sorry) <-> RHS`, such a witness
determines the intended answer/RHS as false. It is not described as a literal
contradiction of the opaque `answer(sorry)` biconditional.

## Exact evaluator and certificate

Write a sorted representative as `A = (a_0,...,a_(n-1))` with each
`0 <= a_i < N`. Translation and multiplication by a unit modulo `N` preserve
validity and may be used only for canonical deduplication, never as an
unrecorded mathematical assumption.

The exact evaluator enumerates every weak composition

```text
m_0 + ... + m_(n-1) = n,  m_i >= 0.
```

It counts a collision when `m != (1,...,1)` and

```text
sum_i m_i*a_i == sum_i a_i  (mod N).
```

The primary objective is the exact nonnegative collision count `C(A,N)`.
The candidate predicate is exactly

```text
N < M(n) and C(A,N) = 0.
```

Every candidate is replayed by a separately implemented recursive composition
generator and direct modular sum. The durable candidate payload contains `n`,
`N`, the canonical and original residue lists, the exact number of
compositions checked, `C(A,N)`, and the modulus gap `M(n)-N`.

## Database-sanity gate

Before an arm evaluates a target proposal it must reproduce these controls:

1. `{0,1}` is valid modulo `2 = M(2)` and is not a sub-threshold candidate.
2. `{0,1,3}` is valid modulo `6 = M(3)` and is not a sub-threshold candidate.
3. `{0,1}` modulo `1` is rejected because a two-element residue set cannot
   exist there.
4. `{0,1,2}` modulo `6` has a non-all-one collision (`(0,3,0)`) and
   is not valid.

The worker must fail closed if a control is not reproduced.

## Frozen arms

Each `(arm, shard)` worker is externally capped at 60 seconds and stops
internally at 54 seconds, leaving time to fsync a terminal receipt.

### CATALOGUE

Enumerate sorted residue sets containing zero for increasing `(n,N)` with
`2 <= n <= 6` and `n <= N < M(n)`. Translation normalization is complete:
every residue set has a translate containing zero. Shards partition proposals
by a stable SHA-256 identity. Exact unit-orbit canonicalization removes
duplicates. The arm records `DOMAIN_EXHAUSTED` only if its complete assigned
finite range was consumed.

### GENERIC

Use seed `0x4D494E4D4F44 + shard`. For `6 <= n <= 11`, sample positive
sub-threshold gaps geometrically toward the wall, then sample size-`n` residue
sets containing zero. Canonicalize by translation and units. This arm has a
fixed proposal ceiling of 200,000 per shard; it terminates as
`PROPOSAL_LIMIT` or `DEADLINE_PREFIX`, never as domain exhaustion.

### WALL_NAVIGATION

For `3 <= n <= 12`, start from the proved super-increasing set
`{2^k-1}` modulo `M(n)`. Explore decreasing moduli and deterministic one- and
two-residue substitutions, retaining states by lexicographic score
`(collision_count, -modulus_gap, canonical_residues)`. A bounded beam of 128
states and depth 6 is frozen. This arm terminates as `SEARCH_EXHAUSTED`,
`DEADLINE_PREFIX`, or `CROSSING_VERIFIED`; it makes no claim about the complete
space of residue sets.

## Durable output and terminal semantics

Every emitted JSONL row is canonical JSON, hash-chained to the preceding row,
flushed, and `fsync`ed. Counters distinguish proposals, canonical-unique
states, hypothesis survivors, exact evaluations, and objective-scored states.

Allowed terminal reasons are:

- `DOMAIN_EXHAUSTED`;
- `PROPOSAL_LIMIT`;
- `SEARCH_EXHAUSTED`;
- `DEADLINE_PREFIX`;
- `CROSSING_VERIFIED`;
- `WORKER_ERROR`.

Normal process exit is not evidence of exhaustion. A terminal receipt records
the reason, next proposal/domain index when meaningful, counters, final row
hash, and whether a verified crossing was emitted.

## Publication gate

This harness performs no issue, pull request, release, README edit, or public
claim. A candidate may leave development only after independent replay,
source/novelty re-audit, and a separate exact certificate suitable for Lean.
