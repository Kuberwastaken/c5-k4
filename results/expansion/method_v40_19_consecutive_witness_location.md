# Method v40: WOWII #19/#13 consecutive witness location

## Scope

This rung converts the final numerical obstruction in the consecutive-added-
edge geometry into a finite, indexed geometric split.

Lean source:
`lean/GraphConjecture19ConsecutiveWitnessLocation.lean`

## Position type

The file defines `ConsecutiveWitnessPosition`, with five constructors relative
to the added edge between geodesic indices `i` and `i+1`:

1. the witness is `extraLeft`;
2. the witness is `extraRight`;
3. the witness occurs at an index `j<i` on the strict left tree arm;
4. the witness occurs at an index `j>i+1` on the strict right tree arm;
5. the witness is off the geodesic, where saturation forces it adjacent to the
   selected center `c`.

The position theorem is exhaustive.  If the vertex lies in the path support,
`mem_support_iff_exists_getVert` supplies an index.  Natural-number trichotomy
then isolates the two endpoint indices and two strict arms.  If it does not
lie in the path, the saturated cover

`P union N(c) = V`

forces membership in `N(c)`.

## Full-independent maximum-degree witness

Under the sole remaining charge obstruction

`localMax(G) = maxDegree(G)`,

the file selects a vertex `v` satisfying:

- `degree(v) = maxDegree(G)`;
- the entire open neighborhood `N(v)` is independent;
- `v` occupies one of the five positions above.

Both an inductive-position result and an expanded five-way disjunction are
certified for downstream proofs.

## Exact residual

The consecutive nontriangle branch is now a finite collection of cases:

- **endpoint witness:** analyze the opposite added endpoint and the first edge
  of the fundamental detour inside the independent neighborhood;
- **internal arm witness:** its predecessor and successor are distinct tree
  neighbors in an independent neighborhood; additional maximum-degree
  branches must respect the unique-cycle restriction;
- **off-geodesic witness:** it is adjacent to `c`, has maximum degree, and has
  a fully independent neighborhood; saturation and the two-tree-arm structure
  locate all of its remaining neighbors.

No maximum attainment, local-independence-to-neighborhood bridge, or coarse
position search remains.  A direct contradiction is not claimed at this rung:
fully independent neighborhoods at internal path vertices are compatible with
tree geometry and require degree/branch counting.

The fundamental-triangle case remains separate.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 6.6 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
