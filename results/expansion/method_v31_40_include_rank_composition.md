# WOWII 40 v0.31: include-branch rank composition

## Outcome

The additive feedback recurrence for an include-dominant separator now has a
matching linear-forest/path-family composition theorem.

`PathFamilyJoin G P Q` records the precise allocation condition needed after
lifting two recursive side certificates into the parent graph:

- the two support families have no duplicate components;
- every support from the left family is vertex-disjoint from every support
  from the right family.

In a block-tree application the second condition is obtained by allocating
the shared cut to at most one side. Under this condition, Lean proves that
`P union Q` is again a path-support family and that both component count and
covered-vertex count add exactly.

Consequently, side rank certificates

```text
|P| + (2*kL+1) <= covered(P)
|Q| + (2*kR+1) <= covered(Q)
```

compose to the parent target

```text
|P union Q| + (2*(kL+kR)+1) <= covered(P union Q).
```

The two side certificates actually provide one spare unit of surplus. This is
exactly what is needed to match v0.28's include-branch recurrence

```text
tau(G) = includeDeficiency(G[L],c) + includeDeficiency(G[R],c).
```

The end-to-end theorem combines those identities and proves WOWII 40 for a
bipartite include-dominant composition. Thus both branches now have matching
rank interfaces: exclude nodes consume an allocated three-vertex leaf path,
while include nodes join two cut-allocated recursive path families.

The remaining structural task for a total block-tree theorem is constructing
`PathFamilyJoin` automatically from side-local subtype certificates by a
canonical shared-cut allocation/transport operation.

## Verification

The complete 25-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_include_rank_final.QrHbjk`.
Every Lean process used an explicit olean output,
`-DwarningAsError=true`, and a 60-second cap; all 25 returned exit code zero.
The new source contains no `native_decide`, `sorry`, `admit`, `#print`, or
custom axiom.
