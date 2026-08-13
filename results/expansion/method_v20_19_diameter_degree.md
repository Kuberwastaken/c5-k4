# Method v0.20 proof extraction: diameter--maximum-degree count

Date: **2026-08-13 UTC**

Status: **complete finite-set/path selection proof; one metric intersection lemma remains**

[`lean/GraphConjecture19DiameterDegree.lean`](../../lean/GraphConjecture19DiameterDegree.lean)
formalizes the classical counting proof down to its exact metric hinge.

For a diametral shortest path with vertex set `P` and a maximum-degree vertex
`c` with neighborhood `N`, it proves both finite-set cases:

- if `c in P` and `|P intersect N|<=2`, then
  `diameter+maximumDegree<=n+1`;
- if `c notin P` and `|P intersect N|<=3`, adjoining `c` to `P union N`
  recovers the extra unit and proves the same bound.

The development then selects a maximal-degree vertex, selects vertices at
distance equal to Mathlib's natural diameter, obtains a shortest path from
connectedness, proves its support has exactly `diameter+1` vertices from path
nodup, identifies the neighborhood cardinality with maximum degree, and
assembles the two cases.

The precise remaining predicate is
`DiametralNeighborhoodIntersectionBound G`:

```text
for every diametral shortest path p and vertex c,
c on p  -> at most 2 neighbors of c lie on p,
c off p -> at most 3 neighbors of c lie on p.
```

This is the sole remaining bridge.  It is the standard shortcut argument:
four path neighbors of an off-path vertex, or three when the vertex is on the
path, would replace a path segment by a walk through `c` and contradict
shortestness.  Formalizing it requires converting arbitrary members of
`p.support.toFinset intersect neighborFinset c` back to unique path indices,
ordering those indices, and applying the shortest-subwalk distance lemma.

The file also plugs the resulting diameter--degree count into v0.19 and proves
the full WOWII 13 tree conclusion conditional only on this one predicate.
Degenerate conventions are handled by Mathlib's APIs: `exists_dist_eq_diam`
works for nonempty finite vertex types, while connectedness supplies the
shortest path; no assumption that diameter is positive is inserted.

The unconditional classical theorem is therefore not yet claimed.  The
strongest reusable result is the fully assembled reduction

```text
Connected G + DiametralNeighborhoodIntersectionBound G
  => diameter(G)+maximumDegree(G)<=|V|+1.
```

Lean compiled with `-DwarningAsError=true`, exit 0.  No `sorry`, `admit`,
`native_decide`, custom axiom, commit, push, or public action was used.
