# Method v0.22: WOWII 61 exact second-head endpoint criterion

Date: **2026-08-13 UTC**

Outcome: **the endpoint ambiguity from v0.21 is now exact.**  For a positive
second entry `e` in a descending list `d :: e :: tail`, the successor head is
equal to `e` exactly when a copy of `e` survives beyond the first `d` tail
positions that are decremented:

```text
head(step(d :: e :: tail)) = e
  iff
e ∈ (e :: tail).drop d.
```

When the removed head is positive and no copy survives, the successor head is
exactly `e-1`.

Lean also proves the multiplicity implication

```text
d < count(e, rest) -> e ∈ rest.drop d.
```

The full equal-prefix pairwise theorem is proved under the precise surviving-
maximum comparison: whenever a target maximum survives, a source maximum also
survives.

This lane does not derive that comparison from arbitrary graphical weak
majorization and therefore does not claim unrestricted `k=2` monotonicity or
WOWII 61.

## Frozen scope

- New certificate only:
  `lean/GraphConjecture61SecondHeadCriterion.lean`.
- New report only:
  `results/expansion/method_v22_61_second_head_criterion.md`.
- No existing file was edited.  No commit, push, release, issue, PR, or other
  public action was made.
- Every subprocess was capped at 60 seconds.

## Decrement-boundary multiplicity

The first Havel--Hakimi step removes the head `d`, decrements

```text
(e :: tail).take d,
```

and leaves

```text
(e :: tail).drop d
```

untouched before sorting.  The predicate

```text
UndecrementedMax d e rest := e ∈ rest.drop d
```

is therefore the exact boundary formulation of “a maximum-degree copy survives
the decrement.”

The count theorem is independent of descending order: if `rest` contains more
than `d` copies of `e`, at most `d` can lie in `rest.take d`, so at least one
lies in `rest.drop d`.  Lean proves this from `take_append_drop`, count
additivity, and `count <= length`.

For a descending tail bounded by `e`, occurrences of `e` form the initial
maximum block, so the boundary predicate is precisely the expected multiplicity
threshold.  The certificate uses the stronger exact boundary predicate in the
endpoint theorem and exposes the count implication separately.

## Exact upper endpoint

Lean first proves an origin theorem for every successor entry: it either came
from a decremented prefix entry `x`, becoming `x-1`, or it came unchanged from
the dropped suffix.

Suppose the successor head equals positive `e`.  It cannot have arisen as
`x-1`, because all original tail entries satisfy `x <= e`; positive `e` rules
out truncated subtraction at zero.  Hence it must be an untouched suffix copy.

Conversely, if an untouched `e` survives, it is a successor member.  The sorted
successor head dominates it, while the general original-tail bound says the
head is at most `e`.  Therefore the head equals `e`.

This proves the exact biconditional.

## Exact lower endpoint

When `d > 0`, the first tail entry `e` is decremented, so `e-1` always appears
in the successor.  The sorted head is at least `e-1` and at most `e`.

If no untouched `e` survives, the upper-endpoint biconditional rules out head
`e`.  For positive `e`, natural-number discreteness forces

```text
head = e-1.
```

Lean proves the reverse implication as well: if the head is `e-1`, a surviving
`e` would force it to equal `e`, a contradiction.

## Corrected equal-prefix theorem

Consider source and target with identical first two entries `d,e`.  Their first
canonical heads are identical.  Their second heads are each either `e-1` or
`e`.

Lean proves cumulative two-head monotonicity under exactly the needed flag
condition:

```text
target has an undecremented e -> source has an undecremented e.
```

If the target survives at the upper endpoint, the source does too, so the
second heads are equal.  If the target does not survive, its second head is at
most `e-1`, while the source second head is at least `e-1`.

This closes the equal-prefix case for the full class where survival flags are
ordered.

## Why unrestricted equality remains open

Equal top-two sums under weak majorization do not necessarily mean identical
first two entries.  For example, a source may have a larger first entry and a
smaller second entry, with the same sum.  The strict-prefix theorem from v0.21
does not apply, and the new equal-entry theorem does not cover that shape.

Even when the first two entries match, deriving the survival-flag implication
from all later prefix inequalities requires a separate multiplicity argument.
The exact order-ten audit found no graphical `k=2` failure, but finite evidence
is not substituted for that theorem.

## Next proof target

The remaining equal-sum task is now discrete rather than analytic:

1. prove that weak prefix dominance with identical first two entries orders the
   maximum multiplicity across the decrement boundary; then
2. handle equal sums with different first entries using the one-unit endpoint
   interval and the compensating first-head gap.

The first item should be approachable by taking the first prefix at which the
target retains its `(d+1)`-st maximum copy: if the source lacked that copy,
descending order and identical earlier entries should contradict prefix
dominance.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61SecondHeadCriterion.lean
```

Result: **PASS** in approximately eight seconds.  The source contains no
unfinished proof, custom axiom, native evaluator, or external oracle.

## Verdict

The second-head correction is now exact: it is a single multiplicity bit at the
decrement boundary.  Lean proves both endpoint biconditionals, a count-based
survival theorem, and equal-prefix two-step monotonicity whenever the target's
survival bit is bounded by the source's.  The remaining work is to derive that
bit comparison from graphical weak-prefix structure in the unrestricted equal-
sum case.
