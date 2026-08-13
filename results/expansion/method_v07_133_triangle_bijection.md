# Method v0.7: WOWII 133 triangle bijection

## Result

The final #133 representation bridge is closed in
`lean/GraphConjecture133TriangleBijection.lean`:

```text
neighborhoodEdgeCount(G,v) = numTrianglesAtVertex(G,v).
```

The proof constructs the bijection explicitly.  An induced-neighborhood edge
with endpoints `a,b` maps to the ambient finset `{v,a,b}`.  Conversely, for a
3-clique `s` containing `v`, `s.erase v` has cardinality two; its two distinct
vertices are neighbors of `v` and are adjacent to one another, hence form an
edge of the induced neighborhood.

Injectivity is proved by erasing `v` from the image.  This recovers the mapped
endpoint finset, and `Sym2.ext` then recovers the original unordered pair.
Surjectivity uses `Finset.card_eq_two` and `Finset.insert_erase` to implement
the inverse construction.

## Source identity

The pointwise bijection is summed and combined with the committed incidence
double count

```text
sum_v numTrianglesAtVertex(G,v) = 3t
```

and the committed C4-free matching-neighborhood formula

```text
l(G) = (2m - triangleIncidenceCount(G)) / n.
```

This yields, with no auxiliary triangle-incidence hypothesis,

```text
l(G) = (2m - 3t) / n
```

for every finite nonempty C4-free graph, in the source's natural-number
subtraction convention.  The Lean development contains no `sorry`, `admit`,
or custom axiom.
