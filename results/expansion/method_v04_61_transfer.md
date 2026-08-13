# Method v0.4: WOWII 61 degree-transfer boundary

Date: **2026-08-13 UTC**

Outcome: **the minimal sorted-list comparison was formalized, and the
unrestricted residue-monotonicity step was exactly falsified.**  The smallest
counterexample has length three and is already one elementary balancing
transfer.  It is nongraphical, so this does not refute the classical
Griggs--Kleitman theorem; it proves that the next formal step must retain a
graphical-realization invariant.

This lane deliberately stops before graph deletion, Maxine induction, or any
claim about WOWII 61 itself.

## Frozen scope

- Parent certificate: `lean/GraphConjecture61Partial.lean` at parent commit
  `a2d647d` before this lane's edits.
- Upstream definition:
  `FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Residue.lean`.
- Upstream target:
  `FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean`.
- Previous bridge audit:
  `results/expansion/method_v04_61_residue_bridge.md`.
- Upstream checkout inspected in full at the campaign's frozen commit
  `9a1636c4030039f70cf78b866c216d8b6c5f35b0`.

The required Maxine comparison has the following orientation.  If a
maximum-degree vertex is deleted, its actual neighbours need not be the
largest-degree remaining vertices.  Therefore the actual deletion sequence
is generally more concentrated than the canonical Havel--Hakimi successor.
Writing `actual ≽ canonical` for descending prefix majorization, the desired
numerical step would be

```text
residueAux canonical <= residueAux actual.
```

## Formalized comparisons

The certificate adds two list-level definitions.

1. `DescendingMajorizes s t` means:

   - `s` and `t` are descending;
   - they have equal length and equal sum; and
   - every prefix sum of `s` is at least the matching prefix sum of `t`.

   The relation is oriented from the more concentrated sequence to the more
   balanced sequence.

2. `DescendingUnitTransfer s t` is one atomic Robin-Hood move: choose an
   earlier value `a` and a later value `b` with `b + 2 <= a`, replace them by
   `a - 1` and `b + 1`, and sort descending again.  The gap condition excludes
   a move that merely permutes equal/adjacent values.

This atomic move is exactly the nontrivial degree exchange suggested by
replacing a lower-degree deleted neighbour with a higher-degree non-neighbour.
Repeated moves generate the intended majorization direction, but that general
closure theorem was not needed to test monotonicity and is not asserted here.

## Exact counterexample

The smallest failure is

```text
s = [2, 2, 0]
t = [2, 1, 1].
```

It has all of the proposed unrestricted hypotheses:

```text
DescendingMajorizes s t
DescendingUnitTransfer s t
```

The unit transfer takes the second `2` and the final `0` to `1,1`.  Direct
evaluation of the upstream recursive definition gives

```text
residueAux [2, 2, 0] = 1
residueAux [2, 1, 1] = 2.
```

Consequently both candidate implications are false:

```text
DescendingMajorizes s t    -> residueAux t <= residueAux s
DescendingUnitTransfer s t -> residueAux t <= residueAux s.
```

The no-`sorry` theorems
`residueAux_not_monotone_under_descendingMajorizes` and
`residueAux_not_monotone_under_descendingUnitTransfer` certify these exact
failures in Lean.

## Why length three is genuinely minimal

The certificate proves the closed form

```text
residueAux [a,b] =
  if a = 0 then 2
  else if b <= 1 then 1
  else 0.
```

It then proves `residueAux_pair_monotone_of_majorization`: for arbitrary
descending pairs `[a,b]` and `[c,d]` of equal sum with `c <= a`,

```text
residueAux [c,d] <= residueAux [a,b].
```

Empty equal-length/equal-sum lists coincide, and singleton lists coincide by
their equal sums.  Thus no counterexample of length zero, one, or two exists;
the displayed length-three witness is minimal by list length.  This is a
symbolic proof over all natural entries, not a finite enumeration claim.

## The missing invariant is graphicality

`[2,2,0]` is not the degree sequence of a simple graph: on three vertices,
two degree-two vertices are adjacent to every other vertex and force the third
vertex to have degree two.  In contrast, `[2,1,1]` is the degree sequence of
the three-vertex path.

This explains why the counterexample does not challenge the classical
residue bound.  The upstream `residueAux` accepts every natural-number list,
but the Maxine argument only encounters graphical degree sequences.  Plain
majorization forgets precisely that realization constraint.

A diagnostic exhaustive enumeration of all descending graphical sequences
with entries in `0..n-1` found no graphical majorization counterexample for
orders `n <= 9`.  The numbers of graphical sequences checked were

```text
n = 1,2,3,4,5,6,7,8,9
    1,2,4,11,31,102,342,1213,4361.
```

This completed in under one second under the 60-second process cap.  It is
only search evidence, not a proof.  A broader naive all-pairs run through
order 11 reached the 60-second cap before flushing a usable result and was
discarded; no conclusion is drawn from it.

A second, more targeted diagnostic generated only graphical elementary unit
transfers.  It found no monotonicity failure through order 10, after checking

```text
n = 1,2,3,4,5,6,7,8,9,10
graphical sequences = 1,2,4,11,31,102,342,1213,4361,16016
unit transfers      = 0,0,0,8,71,510,2988,16462,84769,421964.
```

Every generated target was also graphical.  The order-11 tranche reached its
60-second cap before completing and was discarded.  Again, this is diagnostic
support for the realization-aware next rung, not a substitute for its proof.

## Exact new boundary

The original five-step ladder cannot use an unrestricted list theorem for its
second rung.  The honest replacement is:

1. define a graphical-sequence predicate, preferably tied to an explicit
   finite simple-graph realization rather than only an arithmetic test;
2. prove residue monotonicity for a graphical elementary transfer, or prove a
   realization-level edge-transfer lemma that implies the required residue
   comparison;
3. only then connect actual maximum-vertex deletion to the canonical
   Havel--Hakimi successor;
4. after that, begin the vertex-count/Maxine induction.

Steps 3 and 4 were intentionally not attempted in this lane.  The immediate
blocker is now exact: **graphical transfer monotonicity**, not generic prefix
majorization.

## Verification

From the pinned `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61Partial.lean
```

Result: **PASS** in approximately seven seconds.  A source audit found no
`sorry`, `admit`, or custom `axiom`.  Every compile and search subprocess in
this lane was bounded by 60 seconds.

## Verdict

The proposed unrestricted monotonicity is false in the strongest local sense:
one elementary balancing transfer can increase `residueAux`.  The failure is
minimal and fully machine checked.  Its nongraphical source is equally
important: it redirects the proof effort toward the exact realization-aware
theorem needed by Griggs--Kleitman instead of allowing a false stronger lemma
to enter the campaign.
