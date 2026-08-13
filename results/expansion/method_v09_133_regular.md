# Method v0.9: WOWII 133 regular and low-local-average classes

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133Regular.lean`

## Stronger surviving theorem

The next general rung is larger than the cubic stratum:

```text
connected(G) and floor(l(G)) <= 1  ==>  WOWII 133(G).
```

No regularity, triangle-freeness, or C4-freeness is required.  If `G`
contains a four-cycle, the source exponent is zero.  Otherwise the conjecture
is bounded by

```text
radius(G) + floor(l(G))
  <= radius(G) + 1
  <= path(G).
```

The Lean theorems `c4FreeBranch_of_floor_l_le_one` and
`sourceConclusion_of_floor_l_le_one` certify the two forms of this argument.
This class contains many nonregular and noncubic graphs; it is not merely a
restatement of the cubic result.

## Regular triangle-free wall

For a `d`-regular triangle-free C4-free graph, v0.8 and the exact identity
`l(G)=d` reduce the conjecture to

```text
radius(G) + d <= path(G).
```

`sourceConclusion_of_regular_triangleFree_pathWall` proves that this natural
integer path wall is sufficient for the exact source-shaped proposition.
This theorem makes the remaining mathematical burden explicit rather than
hiding it in a local-average definition.

The unrestricted assertion that this wall holds for every connected regular
triangle-free C4-free graph was not assumed or claimed here.  The existing
bounded search found no counterexample, but that is not a proof.

## Noncubic closed specializations

`oneRegularTriangleFreeSpecialization` closes every connected 1-regular
triangle-free graph.  Here `l(G)=1`, so the universal
`radius(G)+1<=path(G)` theorem finishes the exact upstream-shaped statement.
This supplies one formally certified regular degree other than three.

More substantially, `twoRegularTriangleFreeSpecialization` closes every
connected 2-regular triangle-free graph.  The Lean proof does not rely on a
prepackaged cycle classification.  It proves directly that:

1. such a graph has radius at least two;
2. a radius geodesic has a unique neighbor away from its first edge;
3. triangle-freeness prevents contact with the second geodesic vertex;
4. C4-freeness and shortestness prevent contact farther down the geodesic;
5. prepending that neighbor gives an induced path on `radius+2` vertices.

Therefore the degree-two wall `radius+2<=path` holds.  If the graph contains
a C4, the exponent-zero source branch is already universal; otherwise the
new path-wall proof applies.  This completes the exact source proposition
for the whole connected triangle-free 2-regular class, a genuinely new
noncubic infinite family.

For regular degrees at least four, the exact remaining target is still the
regular path wall above.

## Lean audit

The file contains no proof holes or custom axioms.  Local dependencies were
compiled first, then the new module was checked with warnings promoted to
errors:

```text
LEAN_PATH=/tmp/c5k4-133-regular:/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133Regular.lean
```

Result: exit code 0 in 6.3 seconds.

This is theorem extraction for an open conjecture, not a counterexample and
not a project-release candidate.
