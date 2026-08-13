# WOWII 40 v0.32: subtype path transport and shared-cut allocation

## Outcome

The last typing/transport gap in the include branch is closed.

For a side `A`, `liftFamily A P` maps every finite subtype support through the
canonical subtype embedding and then maps the whole family injectively. Lean
proves that:

- a path-support family in `G.induce A` lifts to a path-support family in `G`;
- every subtype path maps to the corresponding ambient path and remains a
  simple path;
- family cardinality and covered-vertex cardinality are preserved exactly;
- consequently every path-family rank certificate is preserved.

For a one-vertex separation, lifting left and right side families is almost
automatically disjoint: any common ambient vertex lies in `left intersect
right`, hence is the cut. If the right subtype family avoids its copy of the
cut, all cross supports are disjoint. Nonemptiness of path supports then also
rules out duplicate components, producing the `PathFamilyJoin` required by
v0.31.

The end-to-end theorem now starts with genuinely recursive subtype data:

```text
P : path family in G[left]
Q : path family in G[right]
cut not covered by Q
```

and transports, allocates, joins, and applies their rank certificates to prove
WOWII 40 for a bipartite include-dominant parent. Thus the complementary
recursive branches now both have typed composition interfaces:

- exclude branch: delete the cut and allocate a three-vertex leaf path;
- include branch: recurse on both induced sides, allocate the shared cut to
  one side, lift both families, and join them.

## Verification

The complete 26-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_transport_final.CcxLGS`. Every
Lean process used an explicit olean output, `-DwarningAsError=true`, and a
60-second cap; all 26 returned exit code zero. The new source contains no
`native_decide`, `sorry`, `admit`, `#print`, or custom axiom.
