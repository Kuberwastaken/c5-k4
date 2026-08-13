# Method v0.24 proof extraction: conventional unicyclic decomposition

Date: **2026-08-13 UTC**

Status: **real tree-plus-one-edge existence bridge proved; surplus-core existence remains**

[`lean/GraphConjecture19UnicyclicDecomposition.lean`](../../lean/GraphConjecture19UnicyclicDecomposition.lean)
introduces a conventional, portable presentation of a connected unicyclic
graph: a spanning connected acyclic graph plus one additional edge not present
in that tree.  Its adjacency field states exactly that every graph edge is
either a tree edge or one orientation of the single added edge.

This is materially different from assuming the v0.23 certificate.  From the
tree-plus-one-edge decomposition alone, Lean proves:

- the resulting graph is connected because it contains the spanning tree;
- deleting the first endpoint of the added edge leaves an induced graph that
  is a subgraph of the induced spanning tree;
- the endpoint-deleted graph is therefore acyclic and bipartite;
- every graph in the conventional class has an explicit vertex whose deletion
  is bipartite.

The last theorem is the requested real existence bridge from a standard
unicyclic decomposition to the one-vertex odd-cycle-transversal side of the
v0.22 charge method.  It no longer asks the caller to supply the deletion
vertex or prove bipartiteness after deletion.

## Exact remaining boundary

This rung does not construct the v0.23 surplus witnesses relative to an
arbitrary maximum-degree vertex and diametral path.  The tree-plus-one-edge
presentation identifies the unique cycle implicitly—the added edge plus the
unique tree path between its endpoints—but Mathlib's acyclic API does not
directly expose that unique path as cycle-core decomposition data.

The next bridge is consequently precise: obtain the unique tree path between
the added-edge endpoints and prove that, in each equality-danger configuration
of the diameter--degree count, some vertex on that fundamental cycle lies
outside the relevant path/neighborhood union.  That would construct
`OddUnicyclicCoreCertificate` from `TreePlusOneEdge` and turn v0.23 into a
blanket theorem for this conventional class.

No numerical inequality, v0.22 route disjunction, or v0.23 certificate is
repackaged as an assumption in this file.

## Trust

Lean compiled directly against `FormalConjecturesUtil` with
`-DwarningAsError=true`, exit 0.  Each subprocess remained below 60 seconds.
No `sorry`, `admit`, `native_decide`, custom axiom, placeholder, commit, push,
or public action was used.
