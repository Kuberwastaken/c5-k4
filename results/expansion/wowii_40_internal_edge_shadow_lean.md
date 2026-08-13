# WOWII #40 internal-edge theorem shadow: Lean extraction

Date: 2026-08-13

Status: **proved in Lean**

## Result

Let `H` be an arbitrary finite graph on a right-side type `B`, with
`c = |B|`.  Define `G(H)` by adjoining two nonadjacent hubs, each adjacent to
every vertex of `H`; edges among right-side vertices are exactly the edges of
`H`.

The new Lean module proves both the structural and invariant forms of the
theorem shadow found in the bounded WOWII #40 experiments:

1. If an induced bipartite witness in `G(H)` has at least `c + 1` vertices,
   its complement has at most one vertex.
2. The omitted right-side vertices therefore form a vertex cover of `H` of
   cardinality at most one.  Otherwise an internal edge with both endpoints
   present, together with either present hub, would form a triangle.
3. A graph with a subsingleton vertex cover is a star plus isolated vertices,
   hence is acyclic.
4. All `c` right-side vertices consequently form an induced-forest witness in
   `G(H)`.

In the repository invariants, the final theorem is

```text
c + 1 ≤ b(G(H))  →  c ≤ f(G(H)).
```

The `sSup`-defined bipartite invariant is handled by the existing finite
attainment theorem in `GraphConjecture40Baseline.lean`; this is not merely a
certificate-only surrogate.  The module also retains the lower-level honest
certificate API for reuse with explicit `Finset` witnesses.

## Lean artifacts

- `lean/GraphConjecture40InternalEdgeShadow.lean`
- Main structural theorem:
  `exists_subsingleton_internal_vertexCover_of_large_bipartiteSize`
- Main ambient bound:
  `extension_forest_bound_of_large_bipartiteSize`
- Supporting induced-copy isomorphism: `rightSideIso`

The proof imports the already audited
`lean/GraphConjecture40Baseline.lean` and uses its finite-`sSup` attainment and
explicit induced-forest bound APIs.

## Verification

A fresh dependency-aware build was run from the pinned
`formal-conjectures` environment.  Both processes were capped at 55 seconds:

```bash
timeout 55s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/c5k4-40-shadow-final.us767M/GraphConjecture40Baseline.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40Baseline.lean

timeout 55s env LEAN_PATH=/tmp/c5k4-40-shadow-final.us767M \
  lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  -o /tmp/c5k4-40-shadow-final.us767M/GraphConjecture40InternalEdgeShadow.olean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40InternalEdgeShadow.lean
```

Results:

- baseline: exit 0 in 6.44 seconds;
- theorem-shadow module: exit 0 in 6.90 seconds;
- warning-as-error enabled;
- no `sorry`, `admit`, `native_decide`, or custom axioms;
- `#print axioms` reports only `propext`, `Classical.choice`, and
  `Quot.sound`.

## Interpretation

This closes the computationally observed internal-edge direction as a theorem
shadow: within the entire `K_{2,c}`-plus-internal-edges family, reaching
`b(G(H)) ≥ c+1` forces the internal graph into the star-plus-isolates class
and simultaneously forces an ambient induced forest of order at least `c`.
Thus arbitrary internal-edge surgery cannot independently raise the
bipartite side past this threshold while keeping the right-side forest witness
small.
