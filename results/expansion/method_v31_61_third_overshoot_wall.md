# WOWII 61: exact zero-bank wall for a depth-three overshoot

## Outcome

This pass extends the depth-two theorem into an exact characterization of the
first possible depth-three failure in the shared-successor-prefix class.

New certificate:

```text
lean/GraphConjecture61ThirdOvershootWall.lean
```

Full initial prefix dominance already gives cumulative order through depth
two.  Lean now proves that a failure at depth three can occur only if all of
the following hold simultaneously:

1. the two cumulative head sums tie exactly after depth two;
2. the original first heads are equal;
3. the target's second-step maximum survives the decrement boundary;
4. the source's corresponding maximum does not survive.

Thus every positive-credit case is closed.  The only remaining wall has zero
bank and the sole bad endpoint-flag combination.

## Formal setup

Write the original lists as

```text
source = p :: q :: sourceRest
target = a :: b :: targetRest
```

and suppose their first successors share the positive prefix

```text
HH(source) = d :: e :: sourceTail
HH(target) = d :: e :: targetTail.
```

The original lists are descending, positive, and satisfy full
`DegreePrefixDominates`.  The successor tails are bounded by their shared
second entry `e`, exactly as required by the endpoint criterion.

## Why the failure wall is exact

The proof first imports the complete depth-two theorem from v0.30:

```text
cum_2(target) <= cum_2(source).
```

It then performs the exact second-step flag split.

- If the target maximum does not survive, its third head is `e-1`.  The source
  third head is at least `e-1`, so depth-three order follows.
- If the source maximum survives, its third head is `e`.  The target third head
  is at most `e`, so depth-three order again follows.
- Therefore failure forces target-survives/source-does-not-survive.

In the bad combination the v0.26 iff theorem says

```text
cum_3(target) <= cum_3(source)
  ↔ cum_2(target) < cum_2(source).
```

Failure therefore rules out strict depth-two credit.  Combined with weak
depth-two order, this forces equality.

Finally, because the first successor heads are both `d`, the equality

```text
p + d = a + d
```

forces `p = a`.  Hence any depth-three counterexample in this class lies on a
common-original-head wall as well as a zero-credit wall.

## Exact missing tail lemma

The file names the remaining transfer statement

```text
CommonHeadSuccessorSurvivalTransfer.
```

It asks:

> Given full initial prefix dominance after a common original head, and given
> canonical successors with the same first two entries `d,e`, does survival
> of `e` in the target's second step imply survival in the source's second
> step?

This is strictly weaker than successor-prefix dominance.  It transfers only
one endpoint bit, under the exact zero-bank/shared-prefix conditions forced by
a potential failure.

Lean proves that this single implication suffices to establish

```text
cum_3(target) <= cum_3(source).
```

The proof combines the full depth-two theorem with the v0.26 endpoint-survival
extension theorem.

## Bounded search signal

An increasing-order exact search enumerated descending step-admissible lists
and filtered for:

- full initial prefix dominance;
- equal depth-two cumulative sums;
- identical first two entries in the first successors;
- target third head strictly larger than source third head.

No such pair occurs through order seven.  Counts of admissible descending
lists checked at orders three through seven were:

```text
6, 21, 77, 287, 1079.
```

The process cap stopped the broader enumeration before order eight completed,
so this is reported only as a bounded signal.  The Lean theorem does not rely
on it.

## Verification

After compiling the preceding local certificate, the fresh check was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61ThirdOvershootWall.lean
```

It exited `0` in 6.69 seconds with no output; the two-command chain including
the prerequisite compilation completed in 15.77 seconds.  The source contains
no `sorry`, `admit`, `native_decide`, or custom axiom.

## Next rung

The remaining task is a later-prefix lift across one Havel--Hakimi layer.  With
the original common head removed, full tail-prefix dominance must be converted
into the one-bit `CommonHeadSuccessorSurvivalTransfer` conclusion.

The v0.30 proof suggests the correct form: target survival saturates a boundary
prefix in the first successor.  One should pull the sum of that saturated
prefix back through the common initial decrement-and-sort operation and show
that source non-survival would make some original target prefix exceed its
source counterpart.  Only this scalar saturated-prefix comparison is needed;
full successor majorization remains false and unnecessary.
