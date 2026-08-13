# Method v0.23: WOWII 61 survival-flag multiplicity

Date: **2026-08-13 UTC**

Outcome: **boundary maximum multiplicity now formally orders the equal-top-two
survival flag and closes the two-step cumulative-head comparison under that
count condition. Equality of the first two entries alone is formally refuted.**

This is a partial theorem, not WOWII 61.

## Exact flag

For a state beginning `d :: e :: tail`, v0.22 proved that the second
canonical Havel--Hakimi head equals `e` exactly when

```text
UndecrementedMax d e (e :: tail),
```

meaning a copy of `e` occurs after the first `d` tail entries. Otherwise the
second head is `e-1` under the positive descending-bound hypotheses.

The new file makes the multiplicity bridge explicit. If

```text
d < targetRest.count e,
targetRest.count e <= sourceRest.count e,
```

then the target's survival flag implies the source's. The source has more than
`d` copies of `e`, so the previously proved count lemma places one in
`sourceRest.drop d`.

## Equal-top-two cumulative consequence

For lists with the same first two entries `d,e`, positive heads, and all later
entries bounded by `e`, Lean now proves:

```text
target count(e) <= source count(e)
and d < target count(e)
  -> cumulativeHeadSum 2 target <= cumulativeHeadSum 2 source.
```

This discharges the survival implication required by the v0.22 equal-prefix
theorem. Both second heads attain the upper endpoint `e`, so the two-step sums
are ordered (indeed equal when the first two entries agree).

## Equal top two alone is false

Lean certifies the exact flag and endpoint countermodel

```text
target = [2,2,2,2]   (the degree list of C4)
source = [2,2,1,1]   (the degree list of P4).
```

Their first two entries are identical. With decrement boundary `d=2`, the
tails used by the first step are

```text
targetRest = [2,2,2],
sourceRest = [2,1,1].
```

The target has an undecremented `2` after the boundary; the source does not.
Consequently their exact successor heads are

```text
head(step [2,2,2,2]) = 2,
head(step [2,2,1,1]) = 1.
```

Both degree lists are graphical (`C4` and `P4`), so graphicality plus equality
of the top two degrees is still insufficient. This is not a counterexample to
weak prefix dominance: `[2,2,1,1]` does not dominate `[2,2,2,2]` at the third
prefix. Instead it proves that the later-prefix hypothesis is genuinely doing
work.

## Remaining prefix argument

The new Lean theorem consumes count dominance; it does not yet derive it from
full weak prefix dominance. The remaining equal-top-two question has now been
reduced to:

```text
source weakly prefix-dominates target,
both lists descend and begin d,e,
target has more than d copies of e
  -> source has more than d copies of e.
```

The mathematical route is clear. Target survival in a descending list means
its first `d+1` tail entries all equal the maximum `e`, so its prefix sum is
`(d+1)e`. Prefix dominance forces the source prefix sum to be at least this.
Since every source entry is at most `e`, all those entries must also equal
`e`, yielding source survival.

Formalizing that step requires a bounded-sum saturation lemma for list
prefixes:

```text
length xs = m,
every x in xs satisfies x <= e,
m*e <= xs.sum
  -> every x in xs equals e.
```

and a descending-list lemma transporting a surviving maximum in `drop d` back
across `take (d+1)`. These are the next exact API rungs; no additional graph
search is required.

## Verification

New file:

```text
lean/GraphConjecture61SurvivalFlag.lean
```

After compiling `GraphConjecture61SecondHeadCriterion.lean` locally, the
independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61SurvivalFlag.lean
```

It exited `0` in 7.79 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess remained
under 60 seconds.

## Verdict

The equal-top-two correction bit is now ordered by a concrete multiplicity
condition, and the corresponding two-step cumulative-head theorem is formal.
The `C4/P4` control proves top-two equality alone cannot do this. The sole
remaining `k=2` bridge is the bounded-prefix saturation lemma converting full
weak prefix dominance into the required maximum-count comparison.
