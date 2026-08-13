# Method v20: WOWII #59 aligned-triple bridge

## Outcome

Alignment alone is insufficient to force any of the requested global exits

```text
f(G) >= 5,
b(G) >= 7,
residue(G) <= 2.
```

The obstruction appears before global invariant arithmetic: the three outside
vertices still have four possible unlabeled induced adjacency types, and any
outside edge forms a triangle with either common core neighbor.

This rung therefore formalizes the sharp local boundary and states exactly
which adjacency data is missing.  It does not turn a five-vertex local witness
into an unsupported seven-vertex or residue claim.

## Four outside adjacency types

For outside vertices `x,y,z`, the file defines and exhaustively classifies:

1. `independent`: zero outside edges;
2. `oneEdge`: exactly one outside edge;
3. `path`: exactly two outside edges;
4. `triangle`: all three outside edges.

The theorem `outside_triple_type_exhaustive` proves that every labeled triple
realizes one of these four types by splitting its three edge decisions.  This
is an ordinary symbolic proof, not graph enumeration.

## Exact aligned-five boundary

Let `a,b` be the shared core vertices and assume both are adjacent to all of
`x,y,z`.  For five pairwise distinct vertices, Lean proves the equivalence

```text
G[{a,b,x,y,z}] is bipartite
  <->
not Adj(a,b) and {x,y,z} is independent.
```

The forward direction is forced by triangles:

- if `a-b` is an edge, then `a-b-x-a` is a triangle;
- if any outside edge such as `x-y` exists, then `a-x-y-a` is a triangle.

The reverse direction supplies the explicit two-coloring

```text
color 0: a,b
color 1: x,y,z.
```

Thus the four-type split is decisive:

| outside type | aligned five-set bipartite? |
|---|---|
| independent | exactly when `a-b` is a nonedge |
| one edge | no |
| path | no |
| triangle | no |

## Certified witness and its limit

Under pairwise distinctness, outside independence, and the core nonedge, the
file invokes the existing #40/#59 induced-bipartite witness API and certifies

```text
5 <= b(G).
```

This is the strongest conclusion supplied by the aligned five vertices alone.
It is two vertices short of `b(G)>=7`.  Moreover, the favorable local graph
may be `K_{2,3}`, which contains cycles, so this same configuration does not
force a five-vertex induced forest.

Residue is a global degree-sequence invariant.  No bound such as
`residue(G)<=2` follows from these five local incidences without additional
control of the remaining vertices and degrees.

## Smallest exact counterconfiguration

The smallest missing adjacency is a single outside edge.  If `x-y` is added
while `a` remains a common aligned neighbor, the three vertices `{a,x,y}` form
a triangle.  The theorem

```text
one_outside_edge_blocks_aligned_five_bipartite
```

formally proves that the entire aligned five-set is then not bipartite.  This
obstruction is already present in the `oneEdge` type; the path and triangle
types only add more such triangles.

Consequently alignment must at least be supplemented by:

```text
not Adj(a,b)
and no edges among x,y,z.
```

Those hypotheses recover only the five-vertex bipartite witness.  Reaching
`b>=7` additionally requires two compatible vertices from the remaining core
(or elsewhere) with a consistent two-coloring.  Reaching `f>=5` requires an
acyclic deletion/attachment condition that breaks the possible `K_{2,3}`
cycle.  A residue bridge requires a global degree-profile hypothesis.

## Formal artifact

```text
lean/GraphConjecture59AlignedTripleBridge.lean
```

Principal declarations:

- `OutsideTripleType`;
- `RealizesOutsideType`;
- `outside_triple_type_exhaustive`;
- `AlignedOutsideTriple`;
- `PairwiseDistinctFive`;
- `aligned_five_isBipartite_iff`;
- `five_le_b_of_aligned_independent_nonedge`;
- `one_outside_edge_blocks_aligned_five_bipartite`.

## Verification

```bash
LEAN_PATH=/tmp timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture59AlignedTripleBridge.lean
```

Result: exit code 0, no diagnostics, approximately eight seconds.  The file
contains no `sorry`, `admit`, `native_decide`, or custom axiom.
