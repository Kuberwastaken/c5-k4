# Method v21: WOWII #59 two-vertex compatibility

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59TwoVertexCompatibility.lean`

## Outcome

The aligned-five boundary from v20 upgrades exactly to the desired

```text
b(G) >= 7
```

once two distinct additional vertices are compatible with the two existing
color classes.

The favorable aligned five-set has bipartition

```text
core side:    {a,b}
outside side: {x,y,z}.
```

Let `p` join the outside side and `q` join the core side.  The complete extra
compatibility requirement is only

```text
p !~ x, p !~ y, p !~ z,
q !~ a, q !~ b.
```

No condition is needed on `p-q`, because they receive opposite colors.  No
condition is needed on any other cross-side pair either.  Together with
pairwise distinctness of the seven vertices, these five within-color
nonedges are the smallest direct extension hypothesis for this prescribed
coloring.

## Formal theorem

`PairwiseDistinctSeven` extends the exact v20 distinctness predicate.
`OppositeSideCompatible` packages the five new nonedges.

`aligned_seven_isBipartite` supplies the explicit coloring

```text
color 0: a,b,q
color 1: x,y,z,p
```

and checks every possible edge between the seven vertices.  The theorem
allows all cross-color adjacencies, including `p-q`.

`seven_le_b_of_aligned_compatible_extensions` then invokes the existing
induced-bipartite witness API and proves

```text
7 <= largestInducedBipartiteSubgraphSize(G).
```

This is the requested local bridge to `b>=7`; it does not claim that the two
compatible extension vertices must exist in every graph covered by WOWII 59.

## Sharp fixed-color obstruction

The compatibility conditions cannot simply omit a within-side nonedge.  For
example, if `q-a` is an edge, both endpoints receive color zero, so the fixed
seven-vertex coloring is not proper.  Lean proves this precise obstruction as
`edge_to_core_blocks_fixed_extension_coloring`.

By symmetry, an edge from `q` to `b`, or from `p` to any of `x,y,z`, blocks
the same prescribed extension.  This does not prove the seven-vertex graph is
nonbipartite under every recoloring; it establishes the exact boundary of the
aligned coloring argument.

## Next mathematical step

The remaining existence problem is now concrete: extract two vertices from
the unused core or ambient graph satisfying opposite-side compatibility.
Possible routes are:

1. a pigeonhole argument over attachment types;
2. a core-exchange step that replaces one incompatible aligned vertex;
3. a local obstruction theorem showing that failure of every compatible
   pair forces the separate forest or residue exit.

This theorem should be used as the terminal witness builder for any such
existence argument.

## Lean audit

The module contains no native computation, proof holes, or custom axioms.  It
was checked against the already compiled aligned-triple bridge with warnings
promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-59-v21-audit \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59TwoVertexCompatibility.lean
```

Result: exit code 0 in 10.8 seconds.

WOWII 59 is already externally disproved.  This is theorem extraction, not a
new counterexample or release candidate.
