# Method v0.21: WOWII 141 distance-four extraction

Date: 2026-08-13
Status: complete chordless four-edge-prefix extraction; global radius-three
BFS exclusion remains

## Exact global target

For girth ten and eleven the three-leaf assembly requires a fourth path
vertex.  The global property is

```text
for every v, there exists w with dist(v,w) >= 4.
```

The file defines both this all-centers form and the weaker maximum-local-
center form actually needed by WOWII 141.

## Verified shortest-path package

[`lean/GraphConjecture141DistanceFour.lean`](../../lean/GraphConjecture141DistanceFour.lean)
proves that connectedness plus `dist(v,w) >= 4` supplies a complete chordless
prefix

```text
v -- u -- x -- y -- z.
```

The `FourEdgePrefix` certificate records:

- all four path edges;
- exact pairwise distinctness of all five vertices, expressed by a five-
  element finset cardinality; and
- every prohibited shortcut among nonconsecutive prefix vertices:
  `v-x`, `v-y`, `v-z`, `u-y`, `u-z`, and `x-z` are all nonedges.

Pairwise distinctness is derived from shortest-path support injectivity.
Every nonedge is proved uniformly: replacing the corresponding initial path
segment by one edge gives a shorter walk to `w`, contradicting the distance
equality.

This is the full local metric input needed for the third-leaf chord argument.

## Radius-three obstruction

The file defines `RadiusThreeCenter G v` and proves the exact negation
equivalence:

```text
not EveryVertexHasDistanceAtLeastFour G
  <-> exists v, RadiusThreeCenter G v.
```

It also packages the residual as `NoCyclicRadiusThreeLayer G`: every
radius-three center forces acyclicity.  This property plus girth at least ten
immediately yields the desired all-centers distance-four theorem.

## Remaining global proof

Unlike the radius-two case, a depth-three BFS layering has four alternating
layers.  The intended proof should show that, at girth at least ten:

- edges and multiple-parent attachments inside the first three layers create
  cycles of length at most nine; and
- the resulting parent structure is a forest rooted at the center.

Equivalently, one can formalize the general inequality
`girth <= 2*radius+1` using a BFS tree and a non-tree edge.  This v0.21 pass
does not assume either statement; it isolates the exact radius-three
certificate boundary.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141DistanceFour.lean
```

Result: exit 0 in 8.8 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
