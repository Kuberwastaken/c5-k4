# Method v0.14: WOWII 141 eccentricity-three bridge

Date: 2026-08-13
Status: exact controls support the conjectured radius bound; shortest-path
extraction is verified, while the general girth-to-eccentricity implication
remains to be formalized

## Exact control audit

A bounded NetworkX audit checked every connected graph in the Graph Atlas and
named cycle/circular-ladder controls through order 30.  The Atlas has no graph
of girth at least eight because its graphs stop at seven vertices.  Among 23
eligible named controls, none had a vertex of eccentricity below three.

```text
eligible controls: 23
violations:         0
```

This is evidence, not a proof.  No countermodel was found.

## Formalized metric bridge

[`lean/GraphConjecture141EccentricityThree.lean`](../../lean/GraphConjecture141EccentricityThree.lean)
defines both the all-vertex and maximum-local-center forms of the remaining
claim:

```text
EveryVertexHasDistanceAtLeastThree G
MaximumCenterHasDistanceAtLeastThree G.
```

It then proves that connectedness turns any witness at distance at least
three into a chordless three-edge prefix

```text
v -- u -- x -- y.
```

All six pairwise distinctions among the four prefix vertices are certified
from shortest-path support nodup.  The three shortcut nonedges

```text
not Adj(v,x), not Adj(v,y), not Adj(u,y)
```

are certified by replacing the corresponding shortest-path prefix and
contradicting minimality.  Thus eccentricity at least three at a maximizing
center supplies exactly the path half of the v0.13 two-tail construction.

## Current obstruction

The intended graph theorem is plausible and survived the controls:

```text
connected and girth >= 8 -> every vertex has eccentricity >= 3.
```

A proof should use a shortest girth cycle.  If every cycle vertex were within
distance two of a fixed center, two suitably chosen center-to-cycle paths,
together with an arc of the cycle, would produce a cycle shorter than eight.
The formal difficulty is coordinating intersections of those paths so the
result is a simple `Walk.IsCycle`, not merely a closed walk.

The file therefore does not claim the implication as an assumption or hide
it inside the final theorem.  It records the stronger all-centers property,
the weaker maximum-center property actually needed, and the fully verified
shortest-path consequence.

## Verified corrected class

For `8 <= girth(G) <= 9`, the exact WOWII 141 statement is certified whenever
the graph supplies a `TwoVertexTailSplice`.  The eccentricity hypothesis is
now known to provide its required chordless path prefix; the remaining
construction must combine the v0.13 girth chord exclusions with the generic
leaf-extension theorem to manufacture the splice's final induced-tree field.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141EccentricityThree.lean
```

Result: exit 0 in 7.1 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
