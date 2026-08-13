# Method v0.4: WOWII 133 local-average floor bridge

Date: 2026-08-13 UTC

Status: **CORRECTED CUBIC C4-FREE SPECIALIZATION FORMALLY PROVED / NO SORRY**

Local artifact: `lean/GraphConjecture133Cubic.lean`

## Result

This pass closes the last boundary in the corrected cubic specialization of
WOWII Conjecture 133.  The file now proves both local-average identities:

```text
triangle-free cubic:                 floor(l(G)) = 3
cubic, C4-free, containing triangle: floor(l(G)) = 2
```

Together with the already formalized path extensions, these identities
assemble the exact split

```text
triangle-free:      radius(G) + 3 <= path(G)
contains triangle:  radius(G) + 2 <= path(G)
```

and prove `CubicC4FreeConclusion G`.  The final packaged theorem is
`cubicC4FreeTheorem : CubicC4FreeTheorem`.

This is a complete formal proof of the corrected specialization for finite,
connected, simple, cubic, C4-free graphs.  It is not a proof of the remaining
noncubic C4-free branch of full WOWII 133.

## Triangle-free identity

The reusable lemma

```lean
indepNeighborsCard_eq_degree_of_triangleFree
```

uses mathlib's `isIndepSet_neighborSet_of_triangleFree`.  The whole
neighborhood subtype is an independent set, hence is a maximum independent
set of its induced graph.  Cubicity therefore gives
`indepNeighborsCard G v = 3` at every vertex.  Unfolding
`averageIndepNeighbors` makes the average exactly three, so

```lean
floor_l_eq_three_of_cubic_triangleFree
```

proves `floor(l(G)) = 3`.

## Triangle-containing identity

Three local facts control the other branch.

1. `indepNeighborsCard_le_degree` bounds every local independence number by
   the cardinality of its neighborhood, hence by three in a cubic graph.
2. `two_le_indepNeighborsCard_of_cubic_c4Free` enumerates the three neighbors
   of a vertex.  Either the first pair is nonadjacent, or its being an edge
   forces the second pair to be nonadjacent; otherwise the center and the
   three neighbors form a four-cycle.  Thus every local value is at least two.
3. A graph which is not triangle-free supplies an embedding of `K3`.
   At one triangle vertex, the other two triangle vertices form an edge inside
   its three-vertex neighborhood, so a local independent set cannot contain
   all three vertices.  This yields a local value at most two.

Consequently every local value lies in `[2,3]`, and at least one equals two.
`floor_average_eq_two_of_local_bounds` proves that the real average lies in
`[2,3)`, and

```lean
floor_l_eq_two_of_cubic_c4Free_not_triangleFree
```

concludes `floor(l(G)) = 2`.

## Assembly

`cubicC4FreeSplit` combines the two floor identities with the previously
compiled theorems

```text
radius_add_three_le_path_of_cubic_triangleFree_c4Free
radius_add_two_le_path_of_cubic_c4Free
```

The existing arithmetic bridge `conclusion_of_split` then yields
`cubicC4FreeSpecialization`, and `cubicC4FreeTheorem` packages both the split
and conclusion in the original local theorem target.

## Verification

Every subprocess was capped at 60 seconds.  The final warning-as-error build
from the unmodified `formal-conjectures` Lake project was:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Cubic.lean
```

It exited successfully with no output in approximately 11 seconds.

Temporary `#print axioms` audits of both floor identities and the packaged
theorem reported only `propext`, `Classical.choice`, and `Quot.sound`.  They
reported neither `sorryAx` nor a project-specific axiom, and the temporary
commands were removed.  A source scan finds no `sorry`, `admit`, or custom
`axiom` in the artifact.

## Scope boundary

The formal result does not silently restore the false intermediate claim that
every cubic C4-free neighborhood is independent: triangle-containing graphs
correctly use floor two.  It also makes no statement about noncubic C4-free
graphs and therefore does not claim the full open WOWII Conjecture 133.
