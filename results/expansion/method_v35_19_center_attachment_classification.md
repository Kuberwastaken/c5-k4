# Method v35: WOWII #19/#13 center attachment classification

## Scope

This rung derives exact attachment restrictions in the center-attained
incidence branch from v34.  It treats the orientation
`extraLeft = c`; the opposite orientation is symmetric but is not claimed in
this file.

Lean source:
`lean/GraphConjecture19CenterAttachmentClassification.lean`

## Saturation and edge classification

Assume:

- `P union N(c) = V`;
- `N(c)` is independent;
- `extraLeft = c`;
- `extraRight` is outside `P`.

The file proves the following complete local classification for every vertex
`z` outside `P`.

1. **Center adjacency.** Saturation forces `z` into `N(c)`, hence `c-z` is an
   edge.

2. **Which center edge is added.** If `z != extraRight`, then `c-z` is a tree
   edge.  The only possible non-tree center edge is the designated added edge
   `c-extraRight`.

3. **All other neighbors lie on the path.** If `z-x` is an edge and `x != c`,
   then `x` lies in `P`.  Indeed saturation places `x` in `P` or `N(c)`; the
   second alternative contradicts independence because both `z` and `x` are
   in `N(c)`.

4. **Those attachments are tree edges.** Every such `z-x` with `x in P` and
   `x != c` is a tree edge.  Either added-edge orientation would put
   `extraRight` on `P` or identify `x` with `c`.

Thus the off-path portion is an independent collection of center-adjacent
vertices whose only possible additional attachments go directly to the
geodesic through spanning-tree edges.  Exactly one center edge—the one to
`extraRight`—may be outside the tree.

## Distinct-witness branch

The file also certifies the first required split for v34's distinct
full-independent maximum-neighborhood witness `v`:

`v in P or G.Adj c v`.

This is the exact `v in P` versus `v in N(c)` location forced by saturation.

## Exact residual

In the center-attained orientation, the next cycle-specific step is now
finite and explicit:

- show that an ordinary off-path vertex `z != extraRight` cannot have a
  second tree attachment to `P`, because `c-z-x` competes with the tree path
  carried by the geodesic from `c` to `x`;
- show that `extraRight` has exactly one tree attachment to `P`, which then
  identifies the fundamental cycle as the geodesic segment from that
  attachment back to `c` plus the added edge;
- use oddness/diametrality on that identified segment to obtain charge slack
  or constrain the consecutive-added-edge geometry.

Formalizing those statements requires a tree-walk version of the geodesic
subpath (or direct path-uniqueness surgery).  This file supplies all required
edge-membership facts without overclaiming that conversion.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
chain exited 0 with no warnings; each process was below the 60-second cap.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
