# WOWII 40 v0.33: mixed recursive rank-certificate tree

## Outcome

The exclude and include composition laws are now packaged in one recursive
certificate datatype.

`RankTree G k P` has three constructors:

- `atom` supplies a verified family at coordinate `k`;
- `exclude` consumes one child certificate and an allocated
  `LeafBlockStep`, changing `k` to `k+1` and inserting its support;
- `join` consumes two child certificates and a `PathFamilyJoin`, changing
  `(kL,kR)` to `kL+kR` and unioning their families.

Structural induction proves that every arbitrarily nested tree yields a valid
path-support family satisfying

```text
|P| + (2*k+1) <= covered(P).
```

If `k` is the graph's exact feedback coordinate, the tree proves WOWII 40 for
a bipartite graph.

Both graph-state branches have state-aware constructors:

- an exclude-dominant separator identifies `k+1` with the parent feedback
  coordinate and applies the `exclude` tree node;
- an include-dominant separator consumes two genuinely recursive subtype
  `RankTree` children. Their families are canonically lifted, the right child
  allocates away its copy of the shared cut, and the resulting join tree has
  index `kL+kR`, exactly the parent feedback coordinate.

Thus arbitrary mixtures of unary exclude rank steps and binary include rank
joins share one induction theorem. The remaining work for a completely
self-generating block-tree proof object is purely structural: extracting the
appropriate separators, leaf paths, base atoms, and cut-avoidance choices from
a chosen graph class.

## Verification

The complete 27-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_ranktree_final.jNa6Vk`. Every
Lean process used an explicit olean output, `-DwarningAsError=true`, and a
60-second cap; all 27 returned exit code zero. The new source contains no
`native_decide`, `sorry`, `admit`, `#print`, or custom axiom.
