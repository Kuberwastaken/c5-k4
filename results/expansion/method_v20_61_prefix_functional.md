# Method v0.20: WOWII 61 two-step prefix functional

Date: **2026-08-13 UTC**

Outcome: **the first nontrivial universal degree-prefix bound for cumulative
canonical Havel--Hakimi heads is proved in ordinary Lean.**  For every
descending list with at least two entries,

```text
cumulativeHeadSum(2,s) <= sum(s.take 2).
```

The tempting equality is false.  The five-vertex path sequence
`[2,2,2,1,1]` has top-two prefix sum four but cumulative canonical head sum
three.

This is a genuine prefix-functional theorem, not another credit reformulation.
It does not by itself prove two-step monotonicity between two weakly majorized
sequences, because both cumulative values may lie strictly below their ordered
prefix upper bounds.  This lane does not prove WOWII 61.

## Frozen scope

- New certificate only: `lean/GraphConjecture61PrefixFunctional.lean`.
- New report only:
  `results/expansion/method_v20_61_prefix_functional.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Candidate tests

Several simple degree-prefix identities were checked against exact graphical
controls before formalization.

The most natural candidate was

```text
cumulativeHeadSum(k,s) = sum(s.take k).
```

At `k=1` this is tautological.  At `k=2`, it already becomes false at order
five on the path degree sequence:

```text
s = [2,2,2,1,1]
step(s) = [1,1,1,1]
cumulative heads = 2+1 = 3
top-two prefix = 2+2 = 4.
```

The equality does hold on many regular examples, including `[2,2,2,2]`, which
explains why it is initially plausible.  The path exposes the correction
introduced when decrementing the second maximum during the first step.

## Universal successor-entry lemma

The Lean proof begins with a general list fact requiring neither graphicality
nor descending order.

Suppose every entry of `rest` is at most `bound`.  Every entry of

```text
havelHakimiStep(d :: rest)
```

is also at most `bound`.

The proof transports membership backward through the merge-sort permutation.
An output entry either came from the untouched suffix, where the original bound
applies directly, or from the decremented prefix, where

```text
x - 1 <= x <= bound.
```

This is a reusable monotonicity lemma about canonical reduction as a
degree-prefix operator.

## Second-head theorem

For a descending shape

```text
d :: e :: tail,
```

all entries of `e :: tail` are at most `e`.  The successor-entry lemma therefore
shows

```text
headDegree(step(d :: e :: tail)) <= e.
```

The certificate separately proves that a nonempty tail yields a nonempty
successor, using the exact Havel--Hakimi length theorem.  Thus the head argument
does not rely on assigning a bound to an impossible empty successor case.

## Universal two-step prefix bound

The first canonical head is exactly `d`; the second is at most `e`.  Lean
therefore proves

```text
cumulativeHeadSum 2 (d :: e :: tail)
  <= sum((d :: e :: tail).take 2).
```

The assumption is explicit:

```text
every entry of e :: tail is at most e.
```

For an ordinarily descending degree sequence, this is exactly the needed
tail-bound premise.

This theorem is independent of graphicality and hence applies to every
descending natural sequence, graphical or not.

## Strict and tight controls

Lean certifies both behaviors.

Strict path control:

```text
cumulativeHeadSum 2 [2,2,2,1,1] = 3 < 4
  = sum([2,2,2,1,1].take 2).
```

Tight regular control:

```text
cumulativeHeadSum 2 [2,2,2,2] = 4
  = sum([2,2,2,2].take 2).
```

Both successor computations are kernel-checked through merge-sort permutation
and pairwise descending order.  No native evaluator is used.

## Why this does not yet prove pairwise monotonicity

If source weakly prefix-dominates target, then

```text
sum(target.take 2) <= sum(source.take 2).
```

The new theorem gives

```text
cumulativeHeadSum(2,target) <= sum(target.take 2)
```

and

```text
cumulativeHeadSum(2,source) <= sum(source.take 2).
```

These inequalities point the wrong way for comparing the two cumulative head
sums: an upper bound on the source does not supply the lower bound needed to
finish the chain.  The path's strictness shows this is not merely a missing
Lean lemma.

Thus the universal prefix bound is a real monotonicity rung but not a complete
two-sequence theorem.

## Exact remaining functional

At two steps,

```text
cumulativeHeadSum(2,s)
  = firstEntry(s) + firstEntry(step(s)).
```

The new theorem bounds the second term by the original second entry.  A full
majorization proof needs a correction functional measuring how much the first
step depresses that second entry.  Candidate corrections must distinguish the
path sequence, where the depression is one, from the regular four-cycle shape,
where it is zero.

A promising next target is an exact formula for the second successor head in
terms of the first three original degrees and the number of maximal entries
decremented by the first step.  Such a formula would remain purely in degree-
sequence prefixes and avoid the refuted original-graph incident-edge route.

## Bounded evidence and claim limit

The earlier 105,582,418-pair order-ten audit remains evidence that pairwise
cumulative-head monotonicity may be true.  It is not invoked by the Lean proof
and is not used to upgrade this one-sequence upper bound into a general theorem.

The strict order-five path control is an exact counterexample to the equality
candidate, not to cumulative-head monotonicity itself.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61PrefixFunctional.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

Cumulative canonical heads have a genuine universal prefix bound at two
steps, but not the naive top-prefix equality.  The result advances the
majorization-lattice route by proving that canonical reduction cannot raise the
second head above the original second degree.  The remaining obstacle is an
exact sequence-level correction describing when and by how much that second
head falls.
