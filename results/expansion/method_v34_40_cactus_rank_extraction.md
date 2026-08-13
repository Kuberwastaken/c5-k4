# WOWII 40 v0.34: concrete cactus rank-tree extraction

## Outcome

The recursive rank-tree framework now accepts the concrete cactus witnesses
already developed in the repository.

The following structural data extract directly to `RankTree` certificates:

- `CactusPetalCertificate G k` becomes a rank-tree atom at coordinate `k`;
- `SharedCutPetalCertificate G k` first trims the allocated common center and
  then becomes the same cactus-petal atom;
- `SharedCenterFlowerData G` becomes an explicit coordinate-one rank tree.

The file also constructs a coordinate-zero atom from any graph edge. For an
acyclic bipartite graph, acyclicity proves `tau=0`, so this edge atom closes
the nontrivial recursive base case.

For a shared-center flower, the standard apex-forest hypotheses—deleting the
center is acyclic while the full graph is cyclic—prove `tau=1` internally.
The extracted flower rank tree therefore proves WOWII 40 without an externally
supplied feedback-coordinate equality.

This is the smallest honest structural-extraction rung currently available.
Mathlib and this repository do not yet define a general finite cactus graph,
its block-cut tree, or a theorem that every connected nontrivial cactus has a
leaf block. Consequently, claiming extraction for every connected bipartite
cactus would require first building that missing graph-structural API. The
new results establish that once block/petal witnesses are extracted, they fit
the recursive proof object with no remaining rank or state gap.

## Verification

The complete 28-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_cactus_extract_final2.4vf4se`.
Every Lean process used an explicit olean output,
`-DwarningAsError=true`, and a 60-second cap; all 28 returned exit code zero.
The new source contains no `native_decide`, `sorry`, `admit`, `#print`, or
custom axiom.
