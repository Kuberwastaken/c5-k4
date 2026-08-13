# Method v38: WOWII #19/#13 center nontriangle contradiction

## Scope

This rung uses the rigid attachment geometry from v37 to eliminate the entire
center-attained saturated equality branch whenever the fundamental tree path
has length at least four.

Lean source:
`lean/GraphConjecture19CenterNontriangleContradiction.lean`

## Attachment index

Let `x` be the unique spanning-tree attachment of the off-path added-edge
endpoint `extraRight` to the diametral geodesic.  Both `c` and `x` occur on the
geodesic, while `extraRight` is adjacent to both:

- `c-extraRight` is the added edge;
- `x-extraRight` is the unique tree attachment.

The two-edge route through `extraRight` and the exact geodesic subpath metric
give

`Nat.dist(index(c), index(x)) <= 2`.

The file excludes the smaller values exactly:

- distance zero contradicts `x != c`;
- distance one makes `c-x` an edge, hence puts both `x` and `extraRight` in
  the independent set `N(c)`, even though they are adjacent.

Therefore

`Nat.dist(index(c), index(x)) = 2`.

## Fundamental path contradiction

The previously certified distance-two route theorem now applies with:

- the on-geodesic added endpoint equal to `c`;
- the off-geodesic endpoint `extraRight`;
- the on-geodesic attachment vertex equal to `x`.

It turns the two-edge geodesic segment from `c` to `x`, followed by the tree
edge `x-extraRight`, into a three-edge spanning-tree path between the endpoints
of the added edge.  Tree path uniqueness forces the canonical fundamental
tree path to have length exactly three.

This contradicts the nontriangle hypothesis that every fundamental tree path
has length at least four.  Hence the theorem
`center_attained_nontriangle_impossible` closes this branch with `False`.

## Consequence for the proof lane

There is no remaining numerical charge obstruction in the center-attained
nontriangle geometry.  The apparent equality case

- saturated path/neighborhood cover;
- center is an added-edge endpoint;
- center neighborhood fully independent;
- off-path added endpoint with a unique geodesic attachment;

cannot exist when the fundamental cycle has length at least five.

The center-attained residue is now confined to the fundamental-triangle case,
which was intentionally separated at v28.  The other major unresolved
geometry remains the branch where both added-edge endpoints lie consecutively
on the diametral geodesic.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 7.0 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
