# Method v0.16: WOWII 133 metric contact matrices

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133MetricContactMatrices.lean`

## Exact metric filter

Suppose distinct forward candidates `a` and `c` share parent `b`, with
contacts at geodesic indices `i<j`.  Then

```text
x_i -- a -- b -- c -- x_j
```

is a four-edge walk.  Replacing the geodesic segment from `x_i` to `x_j` by
this walk would shorten the full radius geodesic whenever `j-i>4`.

Therefore geodesic shortestness imposes exactly

```text
|i-j| <= 4.
```

The v0.15 matrices use only indices `0..4`.  Every pair in that window already
satisfies this bound.  Re-enumerating all 20 matrices with the metric filter
therefore leaves **all 20**.

This is a useful negative result: neither girth at least five nor ordinary
geodesic shortestness can remove another matrix solely from its early contact
indices.  The four-edge alternative route is never strictly shorter inside a
five-index window.

## Formal theorem

`crossContact_index_gap_le_four` constructs the replacement walk explicitly:

1. take the geodesic prefix through index `i`;
2. traverse `x_i-a-b-c-x_j`;
3. append the geodesic suffix starting at `j`.

Comparing its length with the distance-realizing original proves `j<=i+4`.
The proof works for arbitrary finite or infinite vertex types and does not
assume regularity, triangle-freeness, or C4-freeness once the four contact
edges are supplied.

`not_crossContacts_of_gap_five` packages the strict exclusion: two sibling
rows cannot contain contacts separated by five or more indices.

`EarlyMetricCompatible` records the symmetric abstract filter, and
`earlyMetricCompatible_of_lt_five` formally verifies that every pair in
`0..4` passes it.

## Why short-cycle filtering adds nothing

The sibling route plus the geodesic segment creates a closed walk of length
`4+|i-j|`.  The existing cross-row theorem already removes `i=j`, which would
give a C4.  For distinct indices the resulting lengths are at least five, so
the triangle-free and C4-free hypotheses do not forbid them.  This exactly
matches the abstract enumeration.

## Consequence for the proof strategy

The 20 matrices cannot be eliminated by treating the radius geodesic only as
a shortest path.  Further progress needs one of the stronger facts not yet
encoded in the matrix:

- the chosen endpoint realizes the graph radius rather than merely one
  distance;
- alternative equal-length paths may allow a better radius geodesic choice;
- one can splice a blocked candidate into a different induced path rather
  than insist on the original clean-handle layout;
- degree-four constraints on the target vertices' remaining incident edges
  may forbid simultaneous realization of the matrix.

The equal-length boundary `|i-j|=4`, especially contacts at indices zero and
four, is the natural pivot: it creates a second geodesic rather than a
contradiction and may permit rerouting to expose an unblocked handle.

## Lean audit

The module uses no native computation, proof holes, or custom axioms.  It was
checked with local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-metric:/tmp/c5k4-133-cross-row:\
/tmp/c5k4-133-depth3:/tmp/c5k4-133-early-comb:\
/tmp/c5k4-133-handle-existence:/tmp/c5k4-133-deep-handle:\
/tmp/c5k4-133-degree-four:/tmp/c5k4-133-regular:\
/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133MetricContactMatrices.lean
```

Result: exit code 0 in 7.3 seconds.

This is an exact metric classification and a negative-pruning result, not a
proof of unrestricted handle existence or a counterexample release.
