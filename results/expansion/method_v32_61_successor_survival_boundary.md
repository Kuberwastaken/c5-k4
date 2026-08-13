# WOWII 61: successor survival needs one boundary-prefix inequality

## Outcome

The unrestricted transfer proposition named in v0.31 is false because it
omitted descending-order hypotheses on the original tails.  This pass gives a
kernel-checked exact countermodel and replaces that proposition with the
smallest scalar lemma actually needed by the depth-three proof.

New certificate:

```text
lean/GraphConjecture61SuccessorSurvivalBoundary.lean
```

The corrected result is:

> To transfer the target's second-step survival bit to the source, one does
> not need full successor-prefix dominance.  It suffices to compare the single
> successor-tail prefix sum at the saturation boundary `d+1`.

## Exact countermodel to the broad proposition

Take

```text
source = [1,2,2,1,2,2]
target = [1,1,2,2,2,2].
```

They have a common first head and the source fully prefix-dominates the target
in their displayed order:

```text
source prefix sums: 1,3,5,6,8,10
target prefix sums: 1,2,4,6,8,10.
```

Their canonical successors are

```text
HH(source) = [2,2,2,1,1]
HH(target) = [2,2,2,2,0].
```

Thus both successors share `d=e=2`.  In the target successor tail,

```text
[2,2,2,0].drop 2 = [2,0],
```

so a `2` survives.  In the source successor tail,

```text
[2,2,1,1].drop 2 = [1,1],
```

so no `2` survives.

Lean proves the initial prefix dominance, computes both Havel--Hakimi steps,
and derives a contradiction from `CommonHeadSuccessorSurvivalTransfer`.
Therefore the broad proposition is formally false.

This is a quantifier correction, not a counterexample to the intended degree-
sequence bridge: neither original list is descending.  In particular, their
first entries are not maximum degrees.  The live theorem must retain the
descending canonical-list hypotheses already present in the depth-two work.

## Exact multiplicity reduction

Suppose shared-prefix successor tails are

```text
e :: sourceTail
e :: targetTail,
```

with common length, entries bounded above by `e`, and descending target tail.
Assume only the single inequality

```text
sum(take (d+1) (e :: targetTail))
  <= sum(take (d+1) (e :: sourceTail)).
```

If the target maximum survives beyond the decrement boundary, descending
order forces

```text
take (d+1) (e :: targetTail) = replicate (d+1) e.
```

Its boundary-prefix sum is therefore the maximum possible `(d+1)e`.  The
single assumed inequality forces the bounded source prefix to attain the same
maximum.  Lean applies the previously proved equality-saturation theorem to
obtain

```text
take (d+1) (e :: sourceTail) = replicate (d+1) e.
```

Hence the source has more than `d` copies of `e`, and one survives as well.

This is formalized as

```text
survival_transfer_of_boundaryPrefixSum.
```

It is exactly the multiplicity argument requested by the v0.31 residual wall.

## Corrected missing lift

The file names the remaining statement

```text
CommonHeadSuccessorBoundaryPrefixLift.
```

It restores descending original tails and asks initial full prefix dominance
to imply only

```text
sum(take (d+1) targetSuccessorTail)
  <= sum(take (d+1) sourceSuccessorTail)
```

when the canonical successors share `d,e`.

This is strictly weaker than successor-prefix dominance:

- it compares one prefix length only;
- that length is selected by the shared successor head `d`;
- it is needed only on the zero-bank wall characterized in v0.31.

Proving this scalar lift would combine immediately with the new survival
lemma and the v0.31 depth-three extension theorem.

## Search notes

Exact descending step-admissible enumeration through order ten found no
countermodel to the intended descending transfer form, although the order-ten
pair comparison exhausted the process cap before every pair was tested.

A randomized unrestricted search found the displayed order-six countermodel.
This agrees with the formal diagnosis: ordered prefix dominance alone is too
weak when the original tails are not canonical descending degree lists.

Search results are diagnostic only; the countermodel and positive boundary
lemma are both independently kernel-checked.

## Verification

After compiling the v0.31 prerequisite, the fresh chain was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61SuccessorSurvivalBoundary.lean
```

The full two-command chain exited `0` in 15.69 seconds with no output.  The
source contains no `sorry`, `admit`, `native_decide`, or custom axiom.

## Next rung

The remaining proof obligation is now a single-prefix rearrangement theorem
for a common Havel--Hakimi head:

> decrement the first `p` entries of two descending prefix-dominance-ordered
> tails, sort both results, and compare only the top `d+1` sum selected by a
> shared successor head.

Unlike the previously refuted recursive strategy, this does not assert that
all successor prefixes remain ordered.  It asks only for the one saturated
rectangle required to transfer the endpoint multiplicity bit.
