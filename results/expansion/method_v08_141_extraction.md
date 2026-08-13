# Method v0.8: WOWII 141 induced-star extraction

Date: 2026-08-13
Status: verified partial proof extraction; not a held-out discovery and not a
resolution of the open conjecture

## Exact target

The current `formal-conjectures` statement is

```text
girth(G) / 2 - 1 + max_v indepNeighborsCard(G,v)
  <= largestInducedTreeSize(G).
```

The division is integer division and the left side is then compared in
`Int`.  The repository convention is `girth(G) = 0` for an acyclic graph.

## Extracted construction

For any vertex `v`, take a maximum independent set `A` in the open
neighborhood `N(v)`.  The graph induced by

```text
{v} union A
```

is exactly a (possibly one-vertex) star: every vertex of `A` is adjacent to
`v`, and there are no edges inside `A`.  Therefore it is connected and
acyclic, and

```text
indepNeighborsCard(G,v) + 1 <= largestInducedTreeSize(G).
```

Maximizing over `v` gives

```text
max_v indepNeighborsCard(G,v) + 1 <= largestInducedTreeSize(G).
```

This proves the complete WOWII 141 inequality whenever `girth(G) <= 5`,
because `floor(girth/2) - 1 <= 1` in that range.  In particular this includes
the acyclic convention, graphs with triangles, and the first two
triangle-free girth cases.

## Lean certificate

The fully checked file
[`lean/GraphConjecture141Extraction.lean`](../../lean/GraphConjecture141Extraction.lean)
proves:

- `induce_insert_isTree_of_indep_neighbors`;
- the finite-`sSup` comparison `card_le_largestInducedTreeSize`;
- existence of an ambient maximum local-independent-set witness;
- `indepNeighborsCard_add_one_le_largestInducedTreeSize`;
- `localIndependenceMax_add_one_le_largestInducedTreeSize`; and
- the exact upstream-shaped specialization
  `conjecture141_of_girth_le_five`.

Verification command (from the `formal-conjectures` checkout):

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141Extraction.lean
```

Result: exit 0 in 6.7 seconds.  The file contains no proof placeholders or
custom axioms.

## Honest boundary and next rung

The star alone cannot pay the growing `floor(girth/2) - 1` term once the
girth reaches 6.  A full proof must splice a sufficiently long induced path
or a segment of a shortest cycle into the local star while controlling which
neighbors of the center are lost to chords.  The useful next lemma is thus a
cardinality-preserving induced-tree extension of the form

```text
|T| >= indepNeighborsCard(G,v) + floor(girth(G)/2) - 1.
```

The present extraction certifies the entire base range and isolates that
extension problem; it does not claim the general conjecture.
