# WOWII 61: full prefix dominance closes the depth-two equality wall

## Outcome

The first possible residual-gap overshoot is now completely excluded.

New certificate:

```text
lean/GraphConjecture61EqualityWall.lean
```

For descending positive degree lists, full initial degree-prefix dominance
implies cumulative eliminated-head dominance through the first two
Havel--Hakimi steps.  With the usual admissibility hypotheses, it follows that
the signed residual degree-sum gap cannot overshoot its initial value through
depth two.

No graphicality premise is required beyond the descending/admissible list
structure used by Havel--Hakimi.  No successor-prefix dominance is asserted.

## The equality-wall split

The previous rung proved the result whenever the original two-entry prefix is
strict:

```text
a + b < d + e.
```

Only equality remained:

```text
a + b = d + e,
```

where source begins `d,e` and target begins `a,b`, with prefix-one dominance
`a <= d`.

The new proof splits this wall into two cases.

### Common leading degree

If `a = d`, the two-prefix equality forces `b = e`.  Removing the common
first entry preserves full degree-prefix dominance on the tails.  The existing
descending-survival theorem then applies: target endpoint survival saturates
the boundary prefix, full prefix dominance transfers that saturation to the
source, and the successor heads are ordered.

Lean formalizes the reusable cancellation lemma

```text
DegreePrefixDominates (d :: source) (d :: target)
  -> DegreePrefixDominates source target.
```

### Unequal leading degree

If `a < d`, the equality gives

```text
d - a = b - e > 0.
```

Assume the bad endpoint combination, beginning with target survival.  Because
the target tail is descending and bounded by `b`, survival beyond the first
`a` decremented entries forces its next `a+1` entries all to equal `b`.
Therefore the target prefix of length `a+2` has sum

```text
a + (a+1)b.
```

Every entry in the corresponding source tail prefix is at most `e`, so the
source prefix has sum at most

```text
d + (a+1)e.
```

Their difference is exactly

```text
[a + (a+1)b] - [d + (a+1)e]
  = a(d-a)
  > 0.
```

This contradicts full prefix dominance at length `a+2`.  Hence the target
upper endpoint cannot occur at all in the unequal-head equality branch.  Its
successor head is `b-1`, which is bounded by the source's lower endpoint
`e-1` after accounting for the initial head difference.

This is precisely the tail-prefix contradiction requested by the previous
rung.  It consumes a later prefix inequality rather than inventing a relation
between the full successor lists.

## Complete depth-two theorem

Combining the earlier strict case and both equality branches, Lean proves

```text
DegreePrefixDominates source target
descending positive source and target
------------------------------------------------
cum_2(target) <= cum_2(source).
```

The certificate then combines prefix-zero, prefix-one, and this new prefix-two
result with the residual-gap equivalence from v0.28 to obtain

```text
ResidualGapDoesNotOvershootThrough 2 source target.
```

Thus the conjecture-specific bridge is closed completely through two
eliminations, including the equality cliff where top-two data alone was known
to be insufficient.

## Verification

The fresh warning-as-error command was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61EqualityWall.lean
```

It exited `0` in 6.91 seconds with no output.  The source contains no `sorry`,
`admit`, `native_decide`, or custom axiom.

## Next frontier

The first possible overshoot depth is now three or later.  The v0.26 theorem
already gives the exact local third-head endpoint split once the two successor
states share a leading pair, while v0.27 permits larger bank-funded reversals.

The next global rung should seek an analogue of the present proof at the first
bad depth: use the accumulated bank and the earliest saturated target prefix
to identify a prefix of the original target whose excess contradicts initial
degree-prefix dominance.  The successful depth-two calculation suggests the
right quantity is the area of a saturated rectangle, not preservation of a
successor majorization order.
