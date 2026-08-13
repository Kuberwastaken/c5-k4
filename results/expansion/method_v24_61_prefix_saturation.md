# Method v0.24: WOWII 61 bounded-prefix saturation

Date: **2026-08-13 UTC**

Outcome: **full weak prefix dominance now transports a saturated target
boundary prefix to the source, forcing source maximum multiplicity and the
equal-top-two two-step inequality. One pure sorted-list localization lemma
remains between target survival and target saturation.**

This is a partial theorem, not WOWII 61.

## Bounded-list saturation

The new Lean file proves for every natural-number list `xs` whose entries are
at most `e`:

```text
xs.sum <= xs.length * e.
```

It then proves the equality case constructively by induction:

```text
xs.length * e <= xs.sum
and every x in xs satisfies x <= e
  -> xs = replicate xs.length e.
```

At the induction step, the tail upper bound and total lower bound force the
head to equal `e`; the residual inequality then saturates the tail.

A companion prefix lemma says that if all entries of `take (d+1) xs` are both
at most and at least `e`, then

```text
take (d+1) xs = replicate (d+1) e.
```

This is the exact endpoint needed after descending order transports a
surviving maximum backwards across the decrement boundary.

## Saturation implies multiplicity

Lean proves

```text
take (d+1) xs = replicate (d+1) e
  -> d < xs.count e.
```

The proof computes the prefix count as `d+1` and uses
`take_append_drop` plus count additivity to compare it with the full count.
Thus saturation supplies the exact source condition consumed by v0.23.

## Prefix dominance transports saturation

The file defines direct mathematical weak prefix dominance:

```text
source.length = target.length,
for every k <= source.length,
  sum (take k target) <= sum (take k source).
```

Assume the target `(d+1)`-prefix is saturated by `e`, the source has at least
`d+1` entries, and every source entry is at most `e`. At prefix `d+1`:

```text
(d+1)e
  = targetPrefix.sum
  <= sourcePrefix.sum
  <= (d+1)e.
```

The bounded saturation theorem forces

```text
source.take (d+1) = replicate (d+1) e,
```

and therefore `d < source.count e`.

## Equal-top-two endpoint

For states beginning with the same positive `d,e`, the final theorem combines:

- full weak prefix dominance between `e :: sourceTail` and
  `e :: targetTail`;
- source and target maximum bounds by `e`;
- target boundary-prefix saturation;
- the v0.23 count-to-survival theorem;
- the v0.22 exact second-head criterion.

It proves

```text
cumulativeHeadSum 2 target <= cumulativeHeadSum 2 source.
```

No graphicality hypothesis or finite computation is used in this transfer.

## Exact remaining residual

The only missing bridge from the originally desired descending-list theorem
is now:

```text
target is descending,
all target entries are <= e,
e occurs in target.drop d
  -> every x in target.take (d+1) satisfies e <= x.
```

Together with the already-formal upper bound, the new
`prefix_eq_replicate_of_forall_ge_le` theorem immediately converts this into
target saturation. Mathematically, an occurrence of `e` after position `d`
forces every earlier entry to be at least `e` in a descending list.

The remaining proof is purely an indexing API lemma for `List.Pairwise (·>=·)`:
extract the surviving element's absolute index via `getElem_drop`, then use
`Pairwise.rel_get_of_lt` for each earlier prefix index. No graph theory,
Havel--Hakimi arithmetic, or optimization remains in the `k=2` equal-prefix
case.

The `C4/P4` countermodel from v0.23 remains the warning: equal top two alone
does not imply saturation or survival. Full prefix dominance is essential.

## Verification

New file:

```text
lean/GraphConjecture61PrefixSaturation.lean
```

After compiling the local v0.22 and v0.23 imports, the independent check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61PrefixSaturation.lean
```

It exited `0` in 6.10 seconds with no output. The source contains no
`native_decide`, `sorry`, `admit`, or custom axiom. Every subprocess remained
under 60 seconds.

## Verdict

The bounded-sum and prefix-dominance portion of survival-flag monotonicity is
now formal. Target saturation forces source saturation, source multiplicity,
source survival, and the desired equal-top-two two-step inequality. The exact
residual is one descending-list index-localization lemma converting target
survival into target prefix saturation.
