# Method v0.9: WOWII 141 one-vertex splice certificate

Date: 2026-08-13
Status: verified conditional extension into girth 6 and 7; not a resolution of
the general open conjecture

## Why one extra vertex is the next exact rung

The v0.8 extraction proved

```text
max_v indepNeighborsCard(G,v) + 1 <= largestInducedTreeSize(G).
```

For girth 6 or 7, WOWII 141 asks for

```text
max_v indepNeighborsCard(G,v) + 2 <= largestInducedTreeSize(G).
```

Thus the first range beyond the induced-star proof needs exactly one genuine
vertex of induced-tree growth, not a new asymptotic estimate.

## Corrected splice interface

The new Lean structure `OneVertexSplice G` records:

- a center `v` attaining maximum local independence;
- a maximum independent set `A` in `N(v)`;
- an extra vertex `x` outside `{v} union A`; and
- an exact certificate that `G[{x,v} union A]` is a tree.

The final field is intentionally an induced-tree certificate rather than the
weaker informal phrase "take a distance-two vertex."  Distance two supplies
an attachment edge, but without a chord-exclusion argument it does not by
itself certify that retaining the whole maximum local star is acyclic.  At
large girth that exclusion should follow from the absence of triangles and
4-cycles; formalizing that implication is the next graph-theoretic bridge.

## Lean result

[`lean/GraphConjecture141Splice.lean`](../../lean/GraphConjecture141Splice.lean)
proves without placeholders:

```text
OneVertexSplice G
  -> max_v indepNeighborsCard(G,v) + 2
       <= largestInducedTreeSize(G)
```

and consequently the exact upstream inequality for every graph satisfying

```text
girth(G) <= 7
```

with such a certificate.  A second theorem states the genuinely new branch
with the explicit range `6 <= girth(G) <= 7`.

The proof checks both cardinal gains.  Local maximality identifies `|A|` with
the global local-independence maximum; neighborhood membership proves that
the center is not in `A`; and `x` being outside the star gives the second
inserted vertex.  The resulting explicit tree is then injected into the
finite `sSup` definition of `largestInducedTreeSize`.

Verification command (from the `formal-conjectures` checkout):

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141Splice.lean
```

Result: exit 0 in 6.5 seconds.  There are no proof placeholders or custom
axioms.

## Boundary and next bridge

This pass does not claim that every connected graph of girth 6 or 7 has a
`OneVertexSplice`; that existence statement is precisely what remains.
The prospective bridge is:

1. at a center maximizing local independence, triangle-freeness identifies a
   maximum local independent set with the entire neighborhood;
2. choose a distance-two vertex and one attachment neighbor;
3. use 4-cycle-freeness to show that it has no second attachment into the
   retained neighborhood; and
4. conclude that the extra vertex is a leaf of the induced star.

Steps 1--3 already describe the correct structural reason the splice should
work.  Step 4 needs a reusable Lean lemma saying that adjoining a certified
leaf to an induced tree preserves `IsTree`.  That is now the sharply isolated
formal target; the v0.9 certificate prevents the argument from silently
assuming it.
