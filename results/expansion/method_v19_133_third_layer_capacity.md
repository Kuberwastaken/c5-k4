# Method v0.19: WOWII 133 third-layer capacity

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133ThirdLayerCapacity.lean`

## Bounded controls

For every oriented radius geodesic in the two exact controls, the union of
all third-choice sets was measured after taking all three clean first choices
and all nine second choices.

| graph | first choices | distinct second choices | distinct third choices |
|---|---:|---:|---:|
| incidence graph of `PG(2,3)` | 3 | 9 | 9 |
| `Kneser(7,3)` | 3 | 9 | 18 |

These counts are constant over every oriented radius geodesic in each graph.
They show that third-layer overlap can be substantial: the projective-plane
control has 27 third-choice incidences collapsing to only nine vertices.
Therefore an argument assuming 27 globally distinct candidates is false.

Neither control realizes a blocking contact pattern; all valid second choices
still have a clean third candidate.  The formal statements below were chosen
to capture the exact overlap and target-capacity facts that survive both
controls.

## Same-branch third-layer disjointness

For a fixed first choice `c`, each second choice `b` has exactly three third
choices:

```text
A(c,b) = N(b) \ {c}.
```

Lean proves `|A(c,b)|=3` under four-regularity.

More importantly, distinct second choices `b₁,b₂` in the same branch have
disjoint third sets.  A common `a` would make

```text
c -- b₁ -- a -- b₂ -- c,
```

a forbidden C4.  This is
`thirdHandleChoices_disjoint_same_branch`.  Hence each fixed `c` exposes nine
distinct third vertices, exactly matching the minimum realized by
`PG(2,3)`.

Across different first-choice branches, however, those nine-vertex layers
may coincide.  The projective-plane control realizes the maximal collapse,
so no stronger global distinctness theorem follows from girth five alone.

## Residual target capacity

The file also formalizes the exact degree slots available at early geodesic
targets:

- index zero uses one geodesic edge and has three outside-neighbor slots;
- every internal index uses two geodesic edges and has two outside slots.

These are `card_outsideTargetNeighbors_zero_eq_three` and
`card_outsideTargetNeighbors_internal_eq_two`.  For indices `0..4` when index
four is internal, total outside capacity is therefore

```text
3 + 2 + 2 + 2 + 2 = 11.
```

## Why capacity does not yet close the proof

Within one first branch there are nine distinct third vertices.  If all are
blocked, v0.17 gives one contact incidence per vertex, consuming nine of the
eleven target slots; this is possible.  Thus same-branch counting does not
eliminate any of the ten singleton triples by itself.

Across all three branches there are 27 incidences, but the same third vertex
may occur in multiple branches.  In `PG(2,3)` the union has only nine vertices,
and one contact edge could then account for repeated appearances.  Abstract
capacity therefore still permits all ten local pattern types unless
multiplicities across branches are controlled.

The exact realized incidence obstruction to naive counting is:

```text
3 branches x 9 third incidences = 27 incidences
but only 9 distinct third vertices.
```

## Next independent graph constraint

The missing relation is multiplicity: bound how many different
`(first choice, second choice)` pairs can share one third vertex, and combine
that bound with its single-contact property from v0.17.  `PG(2,3)` shows the
sharp multiplicity may be three, so a useful theorem must exploit how those
three parent pairs are distributed, not merely cap multiplicity below three.

An alternative route is to use the fact that all nine projective-plane third
vertices are nevertheless unblocked: a shared third vertex's adjacency to
one early target may force a C4 with one of its several parents.  This couples
overlap multiplicity directly to blocker capacity and is the next genuinely
new constraint.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-third-cap:/tmp/c5k4-133-choice:\
/tmp/c5k4-133-pivot:/tmp/c5k4-133-metric:/tmp/c5k4-133-cross-row:\
/tmp/c5k4-133-depth3:/tmp/c5k4-133-early-comb:\
/tmp/c5k4-133-handle-existence:/tmp/c5k4-133-deep-handle:\
/tmp/c5k4-133-degree-four:/tmp/c5k4-133-regular:\
/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133ThirdLayerCapacity.lean
```

Result: exit code 0 in 7.9 seconds.

This is a sharp layer-capacity theorem and calibrated obstruction report, not
unrestricted handle existence or a counterexample release candidate.
