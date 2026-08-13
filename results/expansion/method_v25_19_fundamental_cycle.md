# Method v0.25 proof extraction: fundamental cycle path

Date: **2026-08-13 UTC**

Status: **unique spanning-tree fundamental path formalized; surplus incidence bridge remains**

[`lean/GraphConjecture19FundamentalCycle.lean`](../../lean/GraphConjecture19FundamentalCycle.lean)
builds the first canonical cycle-core object from the committed
`TreePlusOneEdge` decomposition.

For every decomposition it proves:

- the spanning tree contains a unique simple path from the second endpoint of
  the added edge to the first;
- the spanning tree is a subgraph of the full graph;
- the added edge is genuinely present in the full graph;
- the added edge cannot occur among the edges of any spanning-tree walk;
- the fundamental path support is nodup, contains both added-edge endpoints,
  and has exactly one more vertex than path edges;
- any competing simple tree path between the endpoints is equal to the
  canonical fundamental path.

This is a real unique-cycle decomposition rung rather than a restatement of
the v0.23 certificate.  The fundamental cycle is now represented by the unique
tree path together with the separately certified added edge, with all
non-overlap and uniqueness facts needed to assemble a cycle.

## Exact remaining boundary

The next theorem must compare this fundamental-path support with an arbitrary
diametral path and the neighborhood of a maximum-degree vertex.  In the two
equality-danger cases from v0.23, it must extract a fundamental-cycle vertex
outside the relevant union.  That is now an incidence/intersection theorem
about two explicit finite path supports, not a missing unique-path existence
theorem.

This file deliberately stops before constructing `OddUnicyclicCoreCertificate`:
uniqueness of the cycle carrier alone does not automatically identify which
cycle vertex lies outside an arbitrary path/neighborhood union.  Promoting
that conclusion without the incidence proof would repackage the desired
surplus as an assumption.

## Trust

Lean compiled with `-DwarningAsError=true`, exit 0.  Every subprocess remained
below 60 seconds.  No `sorry`, `admit`, `native_decide`, custom axiom,
placeholder, commit, push, or public action was used.
