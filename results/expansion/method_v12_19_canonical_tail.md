# Method v0.12 proof extraction: WOWII 19 canonical tail

Date: **2026-08-13 UTC**

Status: **canonical tail cardinality and outside-neighborhood certificate proved; parity coloring remains**

[`lean/GraphConjecture19CanonicalTail.lean`](../../lean/GraphConjecture19CanonicalTail.lean)
constructs the canonical retained geodesic set

```text
Q = {x_0, x_2, x_3, ..., x_d}
```

as the image of the finite index set `insert 0 (Icc 2 p.length)`.

The warning-clean no-`sorry` development proves:

- membership is exactly `i=0` or `2 <= i <= p.length`;
- a shortest path is injective on those retained indices;
- for `p.length >= 2`, `|Q| = p.length`;
- every member of `Q` is either the initial endpoint or a non-neighbor of it;
- for a diametral path, `|Q| = diameter(G)` and the outside-neighborhood
  condition required by the v0.11 endpoint certificate holds.

Thus exact cardinality, path injectivity, and disjointness from an independent
set in the endpoint neighborhood are fully formalized.

The remaining representation step is the parity coloring of `Q`.  One must
define the color of an image vertex through its unique retained index and prove
that adjacency forces consecutive indices (except the removed `x_1`, whose
potential `x_0--x_2` chord is excluded by shortestness).  The v0.10 metric
lemmas already supply the latter mathematical fact; the unresolved work is the
Lean finite-image/unique-preimage parity interface.  Consequently this file
does not claim the requested unconditional endpoint theorem yet.

Build:

```text
lake env lean -R .../c5-k4/lean -DwarningAsError=true \
  .../GraphConjecture19CanonicalTail.lean
```

Result: **exit 0**, no `sorry`, `admit`, custom axioms, or upstream conjecture
theorem dependency.
