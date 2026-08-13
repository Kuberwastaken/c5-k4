# Snake-in-the-box dimension 9 Phase-0 source/status contract

Audit time: **2026-08-13T11:22:03Z**
Outcome: **STRICT_STOP_ONE_SIDED_FIXED_VALUE_WALL**
Scope: source/status and existing-witness audit only; zero development rows.

## Current source lock

Current `google-deepmind/formal-conjectures` remote `main` resolves to
`d16e05aded22b8c467a0a27c14b2311f53185006`.

- Source: [`FormalConjectures/Wikipedia/SnakeInTheBox.lean`](https://github.com/google-deepmind/formal-conjectures/blob/d16e05aded22b8c467a0a27c14b2311f53185006/FormalConjectures/Wikipedia/SnakeInTheBox.lean)
- Git blob: `9682d8124dc617b7dc823afaf309ddd893279031`
- SHA-256: `1781f117a71066c6d1e74c5fb04059889169ceb80d1e9d04cb0f48a706977bd3`

The source defines `Hypercube n` on subsets of `Fin n`, with adjacency exactly
when symmetric difference has cardinality one. A length-`k` snake is an
induced subgraph equal to the subgraph of a simple walk of `k` edges. This is
now source-faithful: merged PR #4617 corrected an earlier definition which
could accept chorded paths.

The open declaration is

```text
snake_dim_nine : LongestSnakeInTheBox 9 = answer(sorry)
```

Here `answer(sorry)` has expected type `Nat`, not `Prop`. Under the default
`answer` elaborator it remains a canonical unspecified natural-number answer;
unlike proposition-valued answers, it is not replaced by `True`. Consequently
the declaration contains no frozen candidate value and has no positive versus
negative orientation to falsify.

Classification: **UNAMBIGUOUS_FIXED_VALUE_QUESTION_WITH_UNINSTANTIATED_ANSWER**.

## Current theorem inventory

The same module records:

- exact optima through dimension eight: edge lengths
  `0,1,2,4,7,13,26,50,98` for dimensions zero through eight;
- `snake_dim_nine_lower_bound : 190 <= LongestSnakeInTheBox 9`;
- a general real-valued upper bound.

All three are source statements ending in `sorry`; none is a local no-`sorry`
certificate in `c5-k4`. The general upper theorem does not close dimension
nine at 190 or 191. The source comment that 190 is “the best length found so
far” is now stale, although the inequality `190 <= ...` remains true.

Exact local searches in `c5-k4` found this target only in the current-manifest
audit and the prior selection-only ranking. There is no Snake-9 constructor,
development ledger, exact witness file, theorem, or certificate in this
repository before this contract.

## Current literature and record status

The July 2026 primary paper P. Orland, L. Fagan et al.,
[*A Census of New Snake-in-the-Box Records*](https://arxiv.org/abs/2607.15270v2),
states that exact values are known only through dimension eight and that for
dimensions at least nine only lower bounds are known. It reports **131
inequivalent dimension-9 snakes of length 191**, improving the previous 190
record by one, and publishes computer-verifiable transition sequences.

The live [Snake-in-the-Box record table](https://www.minortriad.com/snake/),
updated 2026-08-11 and citing that paper/dataset, also records dimension 9
snake length 191. Its sample transition sequence has 191 coordinate flips.
A representation-independent replay performed as source verification found:

```text
transitions = 191
vertices = 192
distinct_vertices = 192
used_coordinate_mask = 111111111
nonconsecutive_pairs_at_Hamming_distance_0_or_1 = 0
```

Thus the published sequence is an exact induced-path lower certificate for

```text
191 <= LongestSnakeInTheBox 9.
```

This replay is verification of an already published witness, not a
development-family row. The paper PDF had no OCR gaps and SHA-256
`02529c7852f3b089e0f689c34c80ad158c76f920ed49cf537a3c561234020e87`;
the audited record page snapshot had SHA-256
`62fe3f292411694cfd72261437bbcd841220f3c2dc4f4e25b9a553497ee743c0`.

## Live issue and pull-request audit

GitHub searches covered `snake_dim_nine`, `SnakeInTheBox.lean`, “Snake in the
box,” and dimension-9 variants.

- [PR #551](https://github.com/google-deepmind/formal-conjectures/pull/551)
  introduced the module and merged in 2025.
- [Issue #4521](https://github.com/google-deepmind/formal-conjectures/issues/4521)
  identified the induced-path semantic defect; it is closed by merged
  [PR #4617](https://github.com/google-deepmind/formal-conjectures/pull/4617).
- PRs #2997 and #3020 attempted formal-status changes for the already-known
  auxiliary theorems but closed without merge; neither claimed the dimension-9
  optimum.
- Open issue #3596 is a generic missing-docstrings list and contains a stale
  Snake entry; it is not a value/status claim.
- No open target-specific issue or PR claims an exact dimension-9 value or
  supplies a global upper certificate as of the audit timestamp.

## Wall and surgery admissibility

The published 191-edge path is a fixed exact **lower wall**. It can seed a
bounded local code surgery—endpoint extension, coordinate flip replacement,
or detour insertion—and every successful child would have a cheap exact lower
certificate: replay the transition sequence and check distinctness plus the
absence of nonconsecutive Hamming-distance-one pairs.

It does **not** supply the other side required for this fixed-value target:

1. A length-192 child would improve the lower bound but would not falsify
   `snake_dim_nine`, because `answer(sorry)` does not name 190 or 191.
2. Exhausting one bounded surgery neighborhood proves only local maximality of
   the chosen 191 witness. It cannot certify
   `LongestSnakeInTheBox 9 <= 191` over all induced paths in the 512-vertex
   hypercube.
3. The current literature explicitly makes no completeness claim for the 131
   length-191 classes and says only lower bounds are known for dimension nine.
4. A genuine exact answer requires both an explicit longest path and a global
   upper certificate. No bounded, independently replayable upper-certificate
   scheme is presently supplied by the source, local repository, or audited
   literature.

Therefore a local surgery would be legitimate record hunting, but not a
falsifiable prospective trial of the current DeepMind declaration under the
Invariant-Wall Method.

## Strict stop

```text
PHASE0_OUTCOME = STRICT_STOP_ONE_SIDED_FIXED_VALUE_WALL
current_lower_bound = 191
current_exact_value = unknown
selected_surgery = null
development_rows = 0
```

Snake-9 is removed from this bounded prospective-method round. It may be
reopened only if a contract supplies either (a) a frozen numerical answer to
test, with source authority, or (b) a global upper-certificate format whose
verification is independently bounded and whose semantics cover every induced
path in `Q9`.

No development family was frozen or evaluated, and no commit, push, issue,
PR, release, or other public action was performed.
