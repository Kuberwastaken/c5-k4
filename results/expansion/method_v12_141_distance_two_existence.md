# Method v0.12: WOWII 141 closed through girth seven

Date: 2026-08-13
Status: verified unconditional theorem for every connected finite graph with
`girth <= 7`; not a resolution of the unrestricted conjecture

## The residual is discharged

The v0.11 pass reduced the girth-six/seven branch to a simple question: does
a center attaining maximum local independence have a two-edge path to a
nonneighbor?

[`lean/GraphConjecture141DistanceTwoExistence.lean`](../../lean/GraphConjecture141DistanceTwoExistence.lean)
now proves more: every vertex has such a path in a connected graph of girth
at least six.

The proof separates cleanly into two reusable facts.

First, every vertex has a nonneighbor.  If some vertex `v` were adjacent to
every other vertex, then its open neighborhood would be independent (already
proved from girth at least six).  The whole graph would therefore be a star,
formally certified acyclic by the independent-parts/unique-neighbor lemma.
But positive girth contradicts acyclicity under the repository's
zero-for-acyclic convention.

Second, connectedness turns a nonneighbor `w` into a two-edge witness.  A
shortest path from `v` to `w` has length at least two.  Taking its vertices at
indices one and two gives

```text
v -- u -- x.
```

Path support nodup proves `x != v`.  If `v` were adjacent to `x`, replacing
the first two path edges by that shortcut would contradict shortestness.

The v0.11 explicit 4-cycle argument then proves that `u` is the unique
attachment of `x` back into `N(v)`.

## Verified theorem

The file proves the exact upstream-shaped statement without an additional
structural hypothesis:

```text
G.Connected
and 6 <= girth(G) <= 7
  -> floor(girth(G)/2) - 1 + max_v indepNeighborsCard(G,v)
       <= largestInducedTreeSize(G).
```

Combining this with the v0.8 induced-star proof for `girth <= 5` yields the
larger unconditional theorem:

```text
G.Connected and girth(G) <= 7
  -> WOWII 141.
```

Thus the first two ranges beyond the bare induced-star bound are now fully
closed.  There is no remaining maximum-center or distance-two hypothesis.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141DistanceTwoExistence.lean
```

Result: exit 0 in 6.9 seconds.  The file contains no proof placeholders or
custom axioms.

## Next range

At girth eight or nine, the right side demands three vertices beyond maximum
local independence rather than two.  The natural next construction is a
two-vertex tail attached to the maximum local star.  The present shortest
path extraction already supplies the candidate vertices; the next proof must
exclude attachments and chords involving the third path vertex using the
girth-eight lower bound.
