# Erdős 23 prospective connected voltage-lift trial

## Outcome

`HOLD_BOUNDED`.

The exact current formal statement and divisibility arithmetic were inspected
before the voltage family was frozen. After the database and lift controls
passed, 50 canonical connected two-sheet lifts were solved exactly. There were
no crossings and no unresolved solves.

This is a negative prospective experiment around a major human conjecture. It
is not a public or upstream claim.

## Construction and bound

The base `B_m` is the balanced independent-set blow-up of `C5` with five parts
of size `m`. A binary voltage on each base edge determines whether its two
lifted edges are parallel or crossed between sheets. The lift has

```text
|V| = 2*(5m) = 5*(2m),
```

so the exact Erdős 23 allowance is `(2m)^2=4m^2`. The frozen sizes `m=2,3,4`
gave orders 20, 30, and 40.

The voltage matrices were nonseparable diagonal, bilinear, and circulant
patterns applied on every nonzero interface-mask orbit under the dihedral
symmetry of the base cycle. Canonical graph labeling removed isomorphic
duplicates. Three switching-trivial/disconnected order-20 outcomes were
rejected exactly as prescribed; 50 connected classes remained.

Every lift is triangle-free because a triangle in a cover would project to a
triangle in the triangle-free base. This was also checked directly on every
constructed adjacency graph rather than trusted as metadata.

## Gates

The first gate repeated 33 divisibility-correct triangle-free controls from the
completed blow-up trial, with zero crossings. The lift-specific controls then
behaved exactly as predicted:

- zero voltage gives two disconnected copies of `B_m`, with bipartization
  numbers `8,18,32 = 2m^2`;
- uniform voltage on one cyclic interface gives a connected bipartite lift,
  with bipartization number zero.

## Exact development results

| base size `m` | lift order | classes | bound `4m^2` | largest observed bipartization | minimum slack |
|---:|---:|---:|---:|---:|---:|
| 2 | 20 | 11 | 16 | 8 | 8 |
| 3 | 30 | 18 | 36 | 18 | 18 |
| 4 | 40 | 21 | 64 | 32 | 32 |

Thus no voltage twist even exceeded the disconnected two-copy burden `2m^2`;
the conjectured allowance is twice that value. Several twists made the graph
substantially easier to bipartize, including connected bipartite members.

Maximum cuts were solved by a binary vertex/cut-edge MILP with a ten-second cap
and zero MIP gap. Each record includes the two cut sides and every deleted
same-side edge. All returned graphs completed exactly within bounded
checkpoints.

## Independent checks

For all 13 order-20 voltage graphs (11 development graphs plus the two lift
controls), a separate exhaustive implementation enumerated all `2^19` cuts
after fixing one vertex side. It matched every MILP optimum.

All 56 voltage graph records were then decoded from graph6 and replayed
adversarially: triangle-freeness, connectivity, order divisibility, cut edges,
deleted edges, post-deletion bipartiteness, and bound arithmetic all passed.
The append-only stream has SHA-256
`9bcda60f9ab08dc6231f1e7b77e0cd14c70afbf1fcaa56fc2ba76e2c8ae570ba`.

## Interpretation

Nonseparable two-sheet frustration does not amplify the balanced wall in this
family. The cover doubles the original odd-cycle burden, but it also creates a
sheet degree of freedom that allows cuts saving at least half of the Erdős
allowance. The direction is therefore safely inward, despite being genuinely
outside nonuniform blow-ups and single-edge surgery.

No apparent crossing arose, so the candidate-specific literature and novelty
gate was not triggered. No commit, push, release, issue, PR, or other public
action was taken.
