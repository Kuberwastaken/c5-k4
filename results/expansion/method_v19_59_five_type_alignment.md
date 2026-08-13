# Method v0.19: WOWII 59 sharp five-type alignment

Date: 2026-08-13

## Scope

This pass formally closes the sharp synchronization theorem identified by the
v0.18 exact audit. WOWII 59 is already externally disproved; this is proof
extraction around its low-residue theorem shadow, not a new disproof or
held-out result.

## Four-valued side encoding

A dense attachment set on a three-vertex color class is one of four sets:

```text
the three complementary two-subsets,
the full three-set.
```

Encode the complementary pairs by `0,1,2`, according to the omitted vertex,
and the full set by `3`. A triple has empty common intersection exactly when
its codes are the three distinct proper values `0,1,2`. This is the
**rotating-complement** exception isolated symbolically in v0.16.

A full row type is a pair of side codes, hence an element of

```text
Fin 4 x Fin 4.
```

A triple is bi-aligned when it is not rotating in either coordinate.

## Formal sharp theorem

The new Lean module proves:

```text
every five-element finset of full row types contains a three-element
subfamily aligned in both coordinates.
```

This is precisely the sharp theorem reported by v0.18. The proof no longer
asks reduction to enumerate every subset of the 16-element row-type space.
Instead it selects five named rows symbolically. If the first three are not
already bi-aligned, one coordinate is a rotating triple. The proof normalizes
its three proper codes to `0,1,2`; only the seven remaining four-valued
coordinates are then checked by a compact Boolean certificate. Coordinate
swap handles rotation on the other side.

Thus the global finset theorem, distinctness bookkeeping, coordinate
normalization, and symmetry step are ordinary symbolic Lean. Only the small
normalized classification uses kernel `decide`. It does not use
`native_decide`, compiled-code trust, a custom axiom, or an external search
result.

## Formal sharpness obstruction

The module also gives the explicit four-type family

```text
(0,1), (0,2), (1,0), (2,0).
```

It formally certifies both:

```text
the family has cardinality four,
the family contains no bi-aligned triple.
```

Thus five is the lowest possible distinct-type threshold.

## Graph specialization

For a finite outside-vertex set `X` and a coding function

```text
rowCode : X -> Fin 4 x Fin 4,
```

the graph-facing theorem says that if at least five distinct full row codes
occur, then five of the occurring codes contain a bi-aligned triple.

Under the omitted-vertex encoding above, that triple corresponds to three
outside vertices sharing a common core attachment on the left and a common
core attachment on the right. In other words, the three outside vertices share
a `K_{3,2}` incidence pattern into two opposite-color core vertices.

The specialization deliberately takes the coding function as explicit data.
The earlier v0.14 theorem proves that every exchange-resistant graph row lies
among the four side types; choosing names for the three core vertices is the
only representation step needed to instantiate this code.

## Formal artifact

[`lean/GraphConjecture59FiveTypeAlignment.lean`](../../lean/GraphConjecture59FiveTypeAlignment.lean)
contains:

1. `SideType`, `RowType`, `Rotating`, `Aligned`, and `BiAligned`;
2. the exact `HasBiAlignedTriple` family predicate;
3. `five_distinct_types_have_bialigned_triple`;
4. the explicit `sharpFour` obstruction and its certificate;
5. `five_encoded_graph_rows_have_bialigned_triple`.

## Verification

The full dependency chain from `GraphConjecture40Baseline` through v0.18 was
compiled into a fresh temporary directory with warning-as-error enabled. The
target was then checked with

```text
LEAN_PATH=/tmp lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59FiveTypeAlignment.lean
```

The isolated target recheck finished in 23.92 seconds and emitted no warnings
or errors. Every individual process in the clean-chain audit was capped at 60
seconds. The file contains no `sorry`, `admit`, custom axiom,
`native_decide`, or imported upstream conjecture proof.

## Remaining graph bridge

The synchronized combinatorics are now formal at the optimal threshold. What
remains is no longer a row-family pigeonhole problem:

```text
five distinct dense rows
  => three rows share opposite-color common core vertices.
```

The unresolved step is to combine that `K_{3,2}` incidence pattern with the
outside adjacency graph. The exact v0.16 triple audit says every explicit
three-row extension with ambient residue three already has `f>=5` or `b>=7`.
A symbolic proof should split by the outside triple's four unlabeled adjacency
types—independent, one edge, path, or triangle—and build the corresponding
forest/bipartite witness or degree-sequence reduction.

## Outcome

`SHARP_FIVE_TYPE_SYNCHRONIZATION_FORMALIZED`.

The exact threshold five and its four-type obstruction are now kernel-checked
Lean theorems. The remaining #59 corner problem has moved entirely to the graph
structure carried by a bi-aligned outside triple.
