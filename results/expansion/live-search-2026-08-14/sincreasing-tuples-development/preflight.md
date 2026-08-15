# Strong 2-increasing-tuples bound: DEVELOPMENT preflight

**Audit date:** 2026-08-14 UTC

**Disposition:** `GO_FOR_SEPARATE_FREEZE`

**Target:** `Arxiv.«1609.08688».maximalLength_le_strong`

**Execution state:** `NOT_FROZEN_NOT_EVALUATED`

This is a source, status, certificate-shape, and method-fit preflight only. It
does not freeze a constructor, evaluate a target row, report a bounded hold,
produce a counterexample, authorize a workflow, or authorize a release or any
other public action.

## Immutable source and declaration identity

The audited upstream is
[`google-deepmind/formal-conjectures@2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`](https://github.com/google-deepmind/formal-conjectures/commit/2411d22e1bd550d050d0eac6c1fb379a76a3e7c5),
the live `main` tip at the audit time.

- commit: `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`;
- root tree: `f6b52f1d3f63b365d6f8c405623d5f7a4e674efc`;
- committer timestamp: `2026-08-14T19:16:38Z`;
- path:
  `FormalConjectures/Arxiv/1609.08688/sIncreasingrTuples.lean`;
- Git blob: `84d2e1e808a8318b1b3c18c0c5208333776faed3`;
- raw-file SHA-256:
  `7b56bf82bd3233a9b606cef15d1ed467478dc57da0ec96cfdd75b2b0aaa56eeb`;
- current declaration lines: 271--274.

The exact declaration is:

```lean
/-- $F(n) \leq n^{3/2}$. -/
@[category research open, AMS 5]
theorem maximalLength_le_strong (n : ℕ) : F n ≤ Real.sqrt n ^ 3 := by
  sorry
```

Here `F` is local notation for `maximalLength`, the supremum of lengths of
lists of triples with coordinates in `Set.Icc 1 n` whose list order is
pairwise `lt₂`. The file defines `a <₂ b` to mean that `a` is strictly smaller
than `b` in at least two of the three labelled coordinates.

The most recent change to this file at the audited tip is the docstring-only
delimiter repair in commit `7eb70784eab1a3c6f4c3d99f8920b970cd7f68c4`.
It does not change the target declaration or its definitions.

## Current status and duplicate audit

The exact target remains tagged `research open` and still has a `sorry` at the
audited commit. Repository issue/PR searches for `maximalLength`,
`maximalLength_le_strong`, `sIncreasingrTuples`, and `2-increasing` found no
open or merged proof or disproof of the strong bound.

The relevant returned items are:

- merged PR
  [#4616](https://github.com/google-deepmind/formal-conjectures/pull/4616),
  commit `0a21ca1b229bb3bf66830934caf4c1e6a6472dc2`, proves only the weaker
  theorem `maximalLength_le`, namely `F n ≤ n ^ 2`;
- its closed issue
  [#4615](https://github.com/google-deepmind/formal-conjectures/issues/4615)
  also names only that `n²` upper bound;
- closed issue
  [#4206](https://github.com/google-deepmind/formal-conjectures/issues/4206)
  concerns only the pigeonhole API lemma `exists_pair_of_mem_Icc`;
- closed, unmerged PRs
  [#2751](https://github.com/google-deepmind/formal-conjectures/pull/2751),
  [#3272](https://github.com/google-deepmind/formal-conjectures/pull/3272),
  and
  [#3379](https://github.com/google-deepmind/formal-conjectures/pull/3379)
  change metadata for the already-solved `n²` upper bound, square lower
  bound, asymptotic upper bound, and product theorem. Their diffs do not touch
  `maximalLength_le_strong`;
- open issues
  [#4747](https://github.com/google-deepmind/formal-conjectures/issues/4747)
  and
  [#3596](https://github.com/google-deepmind/formal-conjectures/issues/3596)
  are repository-wide proof-accounting/docstring maintenance, not resolving
  claims for this target.

This is a point-in-time targeted audit, not a substitute for the complete
open-PR changed-path and fresh literature scan required by a later freeze.
Any target-specific claim or target-path touch found in that complete live
gate is a strict stop before construction.

## Local contamination and classification

The module and declaration occur in the committed benchmark inventories under
`results/benchmark/`, so this target is not held out. The current repository
contains no target-specific constructor, search ledger, result report, Lean
certificate, release, tag, or publication record for
`maximalLength_le_strong`; outside the benchmark inventory, the exact target
name had no local hit before this preflight.

Reading the declaration and deriving the arm below makes the lane explicitly
**DEVELOPMENT-contaminated**. It can improve the method and can produce a
mathematical candidate, but it cannot enter a held-out success-rate claim.

## Intended formal reading and literal crossing

The target is a direct universal inequality, not an `answer(sorry)` wrapper.
At a fixed natural `n`, one finite list is enough to refute it: a list `s` of
triples must satisfy

1. every coordinate of every triple lies in the inclusive interval `1..n`;
2. for every pair of positions `i < j`, `s[i] <₂ s[j]`; and
3. `s.length`, coerced to the reals through the definition of `F`, is strictly
   greater than `Real.sqrt n ^ 3`.

It is not enough to check consecutive pairs. `IsIncreasing₂` is
`List.Pairwise lt₂`, and `lt₂` is explicitly non-transitive. A certificate
must replay every earlier/later pair.

At `n = 5`,

```text
(sqrt 5)^3 = 5*sqrt 5,
11 < 5*sqrt 5 < 12.
```

Therefore a valid **12-term** list in `[1,5]^3` proves `12 ≤ F(5)` and
contradicts the declared upper bound. A list of length at most 11 is not a
counterexample, regardless of how close it is to the wall. The formal bridge
must prove list membership in the supremum defining `F`, derive
`12 ≤ F(5)`, and prove `5*sqrt 5 < 12` exactly; a decimal approximation is
not evidence.

## Exact wall and separating coordinate

The file records the exact test theorem

```lean
theorem maximalLength_four : maximalLength 4 = 8
```

and `8 = 4^(3/2)`. Thus order four is an exact equality wall. Moving to order
five creates 61 new triples containing the new coordinate value `5`, while
the integer crossing threshold moves from 9 to 12. The proposed separating
coordinate is not merely larger `n`: it is the **cut-compatible insertion
capacity of the new-value triples around an embedded order-four extremizer**.

For a fixed eight-term order-four extremizer and each of its nine list cuts,
a new triple has a completely explicit compatibility condition: every base
triple before the cut must be `lt₂` it, and it must be `lt₂` every base triple
after the cut. Multiple inserted triples must additionally satisfy all their
mutual ordered `lt₂` constraints. A crossing in the frozen family requires
four compatible insertions, producing a 12-term list. This is the local-wall
navigation prediction; it is not yet an observed result.

## Database-sanity gate required before target evaluation

A later frozen implementation must stop before the `n=5` arm unless two
independent evaluators agree on all of the following controls:

1. the source examples `lt₂_example_1`, `lt₂_example_2`,
   `lt₂_example_3`, and `not_lt₂_example`;
2. the explicit three-triple witness used by `not_trans_lt₂_nat`, including
   the failure of the first-to-third relation;
3. `maximalLength_zero = 0` and `maximalLength_one = 1` under the literal
   inclusive-coordinate convention;
4. an explicit eight-term order-four list whose full pair table passes;
5. an exact, independently replayable exclusion of every order-four list of
   length nine, thereby reproducing `F(4)=8` rather than trusting the
   source's still-`sorry` test theorem; and
6. invariance of every control under all six labelled-coordinate
   permutations and under simultaneous value reversal combined with list
   reversal.

The two implementations must not share the same adjacency table. One should
evaluate triples and strict-coordinate counts directly; the other should
reconstruct the directed `lt₂` relation independently, for example as
bitsets, and replay the entire ordered-pair matrix. Any disagreement,
timeout, incomplete order-four exclusion, or boundary mismatch is
`SANITY_GATE_FAILED`, with zero target rows.

## Proposed first arm under the hard cap

The first arm is a separately frozen **order-four-wall insertion arm**, not a
flat order-five maximum search.

1. Enumerate or canonically reconstruct the order-four extremizers accepted
   by the sanity gate.
2. Embed them into `[1,5]^3` using all frozen order-preserving coordinate
   injections, quotienting only by explicitly verified labelled-coordinate
   symmetries.
3. For each embedding, enumerate the 61 triples outside its embedded
   `4 × 4 × 4` coordinate box and place each in every compatible cut of the
   embedded base list. For the standard inclusion these are exactly the
   triples having at least one coordinate equal to `5`.
4. Use exact depth-first branch-and-bound, or an equivalently exact Boolean
   model, to seek four mutually compatible insertions. The branch order,
   deduplication key, symmetry rules, base-extremizer set, and tie order must
   be committed before the first `n=5` residual is evaluated.
5. Stop immediately on a 12-term list and serialize it before any further
   search. Otherwise stop when the frozen insertion universe is exhausted or
   the deadline is reached.

The process must stop launching work by 54 seconds and run inside an external
process-group cap of 60 seconds. A cap hit is `TIMEOUT_BRACKET`; it is not a
bounded hold. Exhausting this insertion family with no 12-term list is
`HOLD_BOUNDED` only for this family and says nothing about arbitrary
order-five sequences that contain no embedded order-four extremizer.

No generic or adaptive second arm is authorized by this document. A direct
order-five maximum search, a move to `n=6`, a relaxed base family, or a new
solver requires a separate committed contract before seeing its target rows.

## Candidate verifier and formal-certificate requirements

A provisional 12-term output must be checked in a separate process by an
implementation that did not construct it. The durable certificate must
contain:

- the 12 labelled triples in exact list order;
- the full `12 choose 2 = 66` earlier/later pair table, including the two or
  three increasing coordinate indices for every pair;
- all 36 coordinate range checks;
- the base-extremizer identity, embedding, cut assignment, and insertion
  provenance, which audit the arm but are not prerequisites of the theorem;
- a canonical serialization and SHA-256 digest; and
- exact arithmetic proving `5*sqrt 5 < 12`, preferably by nonnegativity and
  the squared inequality `125 < 144`.

The Lean certificate must use the current declaration's literal `lt₂`,
`IsIncreasing₂`, interval, and `maximalLength` definitions. It must be
warning-clean, contain no `sorry`, `admit`, `native_decide`, or custom axiom,
and end with an axiom audit. Kernel `decide` over the explicit finite pair
table is allowed only if the surrounding supremum and real-inequality bridge
is proved transparently.

A numerical list remains only a candidate until the live source/status and
complete duplicate gate is repeated, the independent verifier passes, and
the Lean bridge compiles at the frozen upstream toolchain. Nothing in this
preflight authorizes a release.

## Strict stops

Stop before target evaluation if any of the following occurs:

- upstream `main` is not the frozen descendant allowed by a later continuity
  policy, or the target path, blob, declaration/category/sorry shape, semantic
  import closure, or toolchain changes;
- any open PR touches the target or its semantic closure, or any open, closed,
  or merged item actually claims the strong `n^(3/2)` bound or a
  counterexample;
- the complete literature/source gate finds that the proposed order-five
  insertion family or a 12-term witness is already reported;
- the local theorem/result/release audit finds target-specific work that this
  preflight missed;
- the order-four database-sanity gate does not finish and independently
  reproduce `F(4)=8` below its own cap;
- a constructor or verifier checks only adjacent list entries, uses `0..n-1`
  instead of `1..n`, merges labelled coordinates without a proved symmetry,
  uses floating point for the crossing, or accepts a list shorter than 12;
- any row has an incomplete pair table, noncanonical serialization, hash
  mismatch, or independent-replay disagreement; or
- the frozen 54/60-second or family boundary is reached. Do not add bases,
  embeddings, triples, cuts, solver settings, runtime, or a larger `n` after
  observing the outcome.

## Preflight conclusion

This is the strongest next DEVELOPMENT fit found after subtracting completed
local lanes. The exact `F(4)=8` equality wall, the isolated new-value
coordinate, the four-insertion crossing threshold, the 125-vertex finite
universe, and the 66-check certificate give a concrete wall-navigation test
with a plausible sub-60-second first arm.

The conclusion is only `GO_FOR_SEPARATE_FREEZE`. As of this file, target
evaluations are **zero**, candidate lists are **zero**, mathematical results
are **zero**, and releases or public actions authorized are **zero**.
