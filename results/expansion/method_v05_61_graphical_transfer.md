# Method v0.5: WOWII 61 graphical-transfer lane

Date: **2026-08-13 UTC**

Outcome: **graphicality is now carried by explicit simple-graph realizations,
the old list counterexample is formally excluded, and the first nonvacuous
graphical transfer is certified.**  No graphical counterexample was found.
The general residue-monotonicity theorem remains open; its exact proposition
and the first obstruction to a naive induction are isolated in Lean.

This is not a proof of WOWII 61 or of the full Griggs--Kleitman inequality.

## Frozen scope

- New certificate only:
  `lean/GraphConjecture61GraphicalTransfer.lean`.
- Parent transfer boundary: commit `4c280e2`.
- Upstream residue implementation:
  `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Residue.lean`.
- No edits were made to `lean/GraphConjecture61Partial.lean`.
- No graph-deletion/Maxine induction, upstream mutation, release, commit, or
  push was attempted in this lane.

## Explicit realization predicate

The new `IsGraphical s` does not infer graphicality from parity, entry bounds,
or a numerical Havel--Hakimi test.  Its data is

```text
there exist n, G : SimpleGraph (Fin n), and a decidable adjacency witness
such that descendingDegreeList(G) = s.
```

Thus every use of graphicality carries a concrete finite simple graph.  The
certificate proves the following consequences from that witness:

1. `IsGraphical.exists_order_eq_length`: the witness graph order equals the
   list length;
2. `IsGraphical.pairwise_ge`: the list is descending;
3. `IsGraphical.mem_lt_length`: every realized degree is strictly below the
   graph order; and
4. `IsGraphical.sum_eq_twice`: the list sum is twice the witness graph's edge
   count, via mathlib's degree-sum theorem.

These necessary arithmetic properties are derived from the graph.  They are
not treated as sufficient substitutes for realizability.

`GraphicalUnitTransfer s t` then requires:

```text
IsGraphical s
IsGraphical t
DescendingUnitTransfer s t.
```

Both endpoints therefore have independent explicit realizations.

## The old counterexample is genuinely removed

The preceding unrestricted lane found

```text
[2,2,0] -> [2,1,1]
residueAux: 1 -> 2.
```

This lane proves, without finite guessing, that a realized degree list of
length three cannot contain both degree zero and degree two.  A degree-two
vertex on three vertices must be adjacent to every other vertex, contradicting
the zero-degree witness.  The reusable theorem is

```text
IsGraphical.not_mem_zero_and_two_of_length_eq_three.
```

Consequently Lean proves both

```text
not_graphical_two_two_zero
not_graphicalUnitTransfer_old_counterexample.
```

The target `[2,1,1]` is separately realized by `pathGraph 3`, so the exclusion
is specifically at the nongraphical source rather than an accidental failure
of the predicate to recognize ordinary graphs.

## Exact small-order rung

The gap condition in a nontrivial unit transfer, combined with the realized
degree bound, forces degree entries two and zero whenever the source length is
at most three.  The preceding realization lemma rules this out.  Lean therefore
proves

```text
not_graphicalUnitTransfer_of_length_le_three
residueAux_monotone_graphicalUnitTransfer_length_le_three.
```

The monotonicity theorem through order three is vacuous but exact: there is no
graphical atomic transfer in that range.  It formally establishes that the
first possible graphical test is order four.

## First nonvacuous graphical transfer

Two explicit four-vertex graphs are defined:

- `pathThreeWithIsolated`, realizing `[2,1,1,0]`; and
- `matchingFour`, realizing `[1,1,1,1]`.

Lean certifies the atomic balancing move

```text
[2,1,1,0] -> [1,1,1,1]
```

as `first_graphicalUnitTransfer`.  The required residue direction holds:

```text
residueAux [1,1,1,1] = 2
residueAux [2,1,1,0] = 3.
```

This is the smallest nonvacuous positive instance of the proposed graphical
monotonicity.

## Why naive residue induction fails

For that same graphical transfer, the canonical successors are

```text
havelHakimiStep [2,1,1,0] = [0,0,0]
havelHakimiStep [1,1,1,1] = [1,1,0].
```

Their sums are zero and two.  Therefore they are not comparable by the
equal-sum majorization relation used before the recursive step.  Lean certifies
this exact mismatch in `first_graphicalUnitTransfer_successors`.

This rules out the simplest proposed proof:

```text
unit transfer at length n
  -> same-direction equal-sum majorization after havelHakimiStep
  -> apply induction at length n-1.
```

The middle implication is already false at the first graphical example.  A
general proof needs a richer recursive invariant that accounts for the change
in the removed maximum degree, or a direct realization-level argument for the
terminal zero count.

## Exact unresolved proposition

The file names, but does not assert,

```text
GraphicalTransferResidueMonotone :=
  forall s t,
    GraphicalUnitTransfer s t -> residueAux t <= residueAux s.
```

`residueAux_le_of_graphicalUnitTransfer` is only an explicit conditional
interface taking this proposition as a hypothesis.  There is no axiom or
hidden assumption supplying it.

The next proof-quality rung must establish one of the following:

1. a stronger well-founded simulation relation on Havel--Hakimi states that
   allows their sums and maximum entries to differ; or
2. a realization-level switching theorem that compares the eventual zero
   counts directly, without requiring one-step majorization to commute with
   `havelHakimiStep`.

Only after that theorem exists should the campaign connect actual
maximum-vertex deletion to the canonical successor and begin Maxine induction.

## Bounded counterexample diagnostics

The preceding exact enumeration had found no graphical atomic-transfer failure
through order ten.  This lane added a deterministic-seed random graph scan:

- graph orders: 4 through 21 completed before the next tranche hit the cap;
- sampled graphs: 54,000;
- tested graphical unit-transfer targets: 982,416;
- residue-monotonicity failures: 0.

Every target was independently checked by the exact Havel--Hakimi graphicality
test before its residue was compared.  The process reached the 60-second cap
during the order-22 tranche, and that incomplete tranche was discarded.  This
is evidence for continuing the proof route, not proof of the general theorem.

A separate exact successor diagnostic immediately found the order-four
obstruction described above: the two Havel--Hakimi successors need not have
equal sums.  That search completed well below the cap and its witness is now
formally certified.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61GraphicalTransfer.lean
```

Result: **PASS** in approximately seven seconds.  The source contains no
`sorry`, `admit`, or custom `axiom`.  Every compile and diagnostic subprocess
in this lane was individually bounded by 60 seconds.

## Verdict

The unrestricted false theorem has been replaced by the correct
realization-aware target.  Its smallest spurious counterexample is excluded
formally, its first genuine instance behaves in the desired direction, and
nearly one million additional graphical transfers produced no counterexample.
The remaining blocker is no longer “carry graphicality”: that is done.  It is
the precise recursive comparison needed when Havel--Hakimi successors lose
equal-sum majorization.
