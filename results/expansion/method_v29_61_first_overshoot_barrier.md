# WOWII 61: the first residual-overshoot barrier

## Outcome

This pass attacks the no-overshoot bridge from v0.28 at its first possible
failure depth.  It proves that:

- prefix-one dominance always funds the first Havel--Hakimi head;
- strict dominance of the original two-entry prefix prevents an overshoot at
  depth two;
- consequently, any first depth-two failure must lie on exact equality of the
  original two-entry prefix;
- that equality wall cannot be resolved using only the top two entries, even
  for graphical sequences.

New certificate:

```text
lean/GraphConjecture61FirstOvershootBarrier.lean
```

This is a genuine arbitrary-list theorem class, not a finite verification.
The remaining depth-two lemma is now sharply localized to transferring the
later prefix information across the equality wall.

## Successor-head interval

For a descending positive-head list

```text
d :: e :: tail
```

whose tail entries are bounded by `e`, the earlier endpoint criterion gives
the exact alternatives

```text
head(HH(s)) = e
```

or

```text
head(HH(s)) = e - 1.
```

The new file packages the lower half as

```text
e - 1 <= head(HH(d :: e :: tail)).
```

The corresponding upper bound `head(HH(s)) <= e` was already formalized.

## Strict two-prefix barrier

Let source and target begin

```text
source = d :: e :: sourceTail
target = a :: b :: targetTail.
```

Assume positive source heads, descending-tail upper bounds, and

```text
a + b < d + e.
```

The target successor head is at most `b`, while the source successor head is
at least `e - 1`.  Because the original two-prefix advantage is an integer and
strict, it absorbs that possible one-unit endpoint loss.  Lean proves

```text
cum_2(target) <= cum_2(source).
```

Notably, this theorem does not require graphicality.  It identifies a purely
local arithmetic region where the no-overshoot bridge is automatic.

Adding prefix-one order and two-step admissibility, Lean upgrades this to

```text
ResidualGapDoesNotOvershootThrough 2 source target.
```

This uses the exact residual-gap/cumulative-head equivalence from v0.28.

## Exact first-failure localization

Under weak original two-prefix order

```text
a + b <= d + e,
```

Lean proves that a depth-two cumulative failure forces

```text
a + b = d + e.
```

Therefore a first overshoot cannot occur in the open strict region.  It must
occur, if at all, on the equality wall where the target successor attains its
upper endpoint and the source successor attains its lower endpoint.

The previous survival/saturation files completely handled the subcase where
the two leading entries themselves agree.  The remaining case permits the
individual entries to differ while their sum agrees.  A proof must use later
prefix inequalities to rule out the bad endpoint combination.

## Smallest graphical boundary countermodel

The top two entries alone are insufficient on the equality wall.  Lean checks

```text
source = [1,1,0,0]  (one edge plus two isolates)
target = [1,1,1,1] (a perfect matching).
```

Both are graphical and their prefix sums agree at lengths one and two.  But

```text
HH(source) = [0,0,0]
HH(target) = [1,1,0],
```

so their cumulative first two heads are respectively `1` and `2`.

This does **not** refute the full bridge: the pair fails full degree-prefix
dominance at the later total prefix (`4 > 2`).  Instead it proves that the
remaining equality-wall argument must genuinely consume the tail-prefix
premises.  No theorem depending only on the top two entries can work.

An increasing-order exact search found this as the first graphical example:
orders below four contain no such pair.

## Verification

The fresh warning-as-error check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61FirstOvershootBarrier.lean
```

It exited `0` in 7.36 seconds with no output.  The source contains no `sorry`,
`admit`, `native_decide`, or custom axiom.

## Next exact rung

The smallest remaining lemma is:

> If descending admissible source and target lists satisfy full degree-prefix
> dominance and equality at prefix two, then the target's successor upper
> endpoint cannot coincide with the source's successor lower endpoint.

Equivalently, full tail-prefix dominance must transfer enough multiplicity or
saturation to rule out that sole bad endpoint combination.  This is narrower
than global successor dominance and is consistent with every previously
formalized counterexample.
