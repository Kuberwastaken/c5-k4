# Method v0.17: WOWII 141 exceptional-root acyclicity

Date: 2026-08-13
Status: global radius-two acyclicity assembly verified; deriving all layer
fields from girth remains

## The partition subtlety

The radius-two BFS layering is not covered directly by the earlier
independent-parts lemma.  With even layer `{root} union L2` and odd layer
`L1`, every `L2` vertex has at most one odd neighbor, but the exceptional root
can have many.  The old lemma required uniqueness at every even vertex.

[`lean/GraphConjecture141RadiusTwoAcyclic.lean`](../../lean/GraphConjecture141RadiusTwoAcyclic.lean)
proves the needed generalization:

```text
I union X = univ
I and X are independent
r in I
every i in I other than r has at most one neighbor in X
  -> G is acyclic.
```

## Cycle proof

The proof treats the exceptional root explicitly.

- If a hypothetical cycle contains `r`, rotate it to start at `r`.  The
  vertex two steps later lies in `I`, differs from `r`, and has the distinct
  first and third cycle vertices as neighbors in `X`, contradicting
  uniqueness.
- If the cycle avoids `r`, either its starting vertex is a non-root member of
  `I`, or its second vertex is.  The original independent-parts argument then
  gives the same two-neighbor contradiction.

All distinctions are obtained from `Walk.IsCycle` support/path lemmas; no
informal parity assumption is inserted.

The file packages the exact hypotheses as `RadiusTwoForestCertificate` and
proves that every such certificate yields `G.IsAcyclic`.

## Remaining girth-to-layer work

For a radius-two center `v`, instantiate the certificate with

```text
even = {v} union {w | dist(v,w)=2}
odd  = neighborSet(v).
```

The remaining local implications from `girth >= 8` are:

1. `odd` is independent (the triangle exclusion is already proved);
2. `even` is independent, requiring the explicit cycle-at-most-five argument
   for an edge between two second-layer vertices; and
3. every non-root even vertex has a unique odd neighbor (the 4-cycle
   exclusion is already proved).

Once the second-layer independence lemma and the set-cover bookkeeping are
formalized, the new exceptional-root theorem closes
`NoCyclicRadiusTwoLayer`, hence every-vertex distance at least three.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141RadiusTwoAcyclic.lean
```

Result: exit 0 in 7.5 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
