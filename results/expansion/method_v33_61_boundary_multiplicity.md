# WOWII 61: exact original-tail multiplicity for successor survival

## Outcome

This pass pulls the successor survival condition completely back through one
Havel--Hakimi step.  The remaining bridge is no longer phrased using sorted
successor prefixes at all; it is one explicit count functional on the original
descending tails.

New certificate:

```text
lean/GraphConjecture61BoundaryMultiplicity.lean
```

For a common original head `p` and a positive successor boundary value `e`,
define

```text
M(p,e,rest)
  = count(e+1, take p rest) + count(e, drop p rest).
```

Lean proves that `M` is exactly the number of copies of `e` in the canonical
Havel--Hakimi successor.  Consequently, ordering `M` between target and source
is sufficient to transfer the second-step survival bit.

## Exact pullback formula

Before merge-sorting, the Havel--Hakimi tail is

```text
map (x ↦ x-1) (take p rest) ++ drop p rest.
```

For positive `e`, Lean first proves

```text
count e (map (x ↦ x-1) xs) = count (e+1) xs.
```

Therefore

```text
count e (laidOffTail p rest)
  = count (e+1) (take p rest) + count e (drop p rest)
  = M(p,e,rest).
```

Merge sort preserves multiplicities, giving the exact canonical formula

```text
count e (HH(p :: rest)) = M(p,e,rest).
```

This equality needs no graphicality or descending-order assumption.  It is a
direct structural identity for the Havel--Hakimi implementation.

## Survival transfer

Suppose source and target successors share the prefix

```text
d :: e
```

and the target successor tail is descending and bounded by `e`.  If its `e`
survives beyond the first `d` entries, saturation implies that the whole
successor tail contains more than `d` copies of `e`.

Now assume only

```text
M(p,e,targetRest) <= M(p,e,sourceRest).
```

The exact pullback formula transfers the copy-count inequality through the two
merge sorts.  The shared first successor entry contributes the same possible
extra copy of `e` on both sides and cancels.  Thus the source successor tail
also contains more than `d` copies of `e`, which forces source survival.

Lean packages this as

```text
successor_survival_transfer_of_boundaryMultiplicity.
```

This theorem bypasses successor-prefix dominance and even the single sorted
boundary-prefix comparison from v0.32.  It uses only a count in the original
laid-off tails.

## Exact remaining scalar statement

The file names the live proposition

```text
CommonHeadBoundaryMultiplicityMonotone.
```

Under descending original tails, full initial prefix dominance, and shared
successor prefix `d,e`, it asks for exactly

```text
M(p,e,targetRest) <= M(p,e,sourceRest).
```

Expanded, the desired inequality is

```text
count(e+1, take p targetRest) + count(e, drop p targetRest)
  <=
count(e+1, take p sourceRest) + count(e, drop p sourceRest).
```

This is the smallest current combinatorial bridge.  It makes explicit what a
future prefix-dominance argument must control: entries one above the successor
threshold inside the decrement zone, plus entries exactly at the threshold
outside it.

## Exact-search evidence

An increasing-order search enumerated descending step-admissible lists and
grouped pairs by common original head and shared first two successor entries.
Within each group it checked full original prefix dominance and the required
successor boundary-prefix inequality.

No countermodel was found through order nine.  Candidate within-group pair
counts before the prefix-dominance filter were:

| order | admissible descending lists | grouped candidate pairs |
|---:|---:|---:|
| 3 | 6 | 1 |
| 4 | 21 | 28 |
| 5 | 77 | 387 |
| 6 | 287 | 4,657 |
| 7 | 1,079 | 58,276 |
| 8 | 4,082 | 764,757 |
| 9 | 15,522 | 10,382,396 |

The order-ten enumeration exceeded the per-process cap before completing.
This is bounded evidence only; the Lean results are independent of it.

## Verification

After compiling the v0.32 prerequisite, the fresh certificate check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61BoundaryMultiplicity.lean
```

It exited `0` in 6.14 seconds with no output.  The source contains no `sorry`,
`admit`, `native_decide`, or custom axiom.

## Next rung

The next proof should work directly with the threshold `e` in the two
descending original tails.  Prefix dominance constrains the area above every
horizontal threshold; the shared successor prefix constrains the maximum
after decrementing the first `p` entries.  The goal is to combine those facts
to order the two-term count `M`.

This is now a discrete threshold-count lemma rather than a sorting theorem:
merge sort has been eliminated entirely from the missing implication.
