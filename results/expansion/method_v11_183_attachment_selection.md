# Method v0.11: #183 attachment selection

## Outcome

The ambient connected-domination layer is now isolated and formalized.

`AttachmentSelectionInput G x` records one attachment neighbor of `x`, one
root, and one rooted trunk for every non-root component of `G-N(x)`.  Its
coverage field says explicitly that every outside vertex other than `x` is in
one of the selected components.  The hypotheses are local and independently
satisfiable; no global connected-dominating conclusion is included in the
input.

Lean proves that:

1. each attachment vertex together with its rooted trunk induces a connected
   ambient subgraph;
2. `x` plus all such branches is connected, by a finite fold gluing each
   branch through its chosen `x`-attachment edge;
3. neighbors of `x` are dominated by `x`; and
4. every nonneighbor of `x` belongs to a covered outside component and is
   dominated by that component's trunk.

Under the claw-free hypothesis it also proves the selection's crucial
cardinality property: two distinct outside components cannot use the same
attachment neighbor of `x`.  The shared neighbor, `x`, and the two component
roots would otherwise form a claw.  Hence the image of the attachment map has
cardinality exactly equal to the number of selected components.

The resulting unconditional endpoint is

```text
selectedDominatingSet_isConnectedDominating :
  G.IsConnectedDominating (selectedDominatingSet G x A)
```

Finally, `AttachmentBudgetInput` adds only component-supported bipartite
witnesses and the local numerical size budget.  It converts directly through
`ComponentFoldInput` to `OutsideBudgetCertificate`; global domination and
connectivity are supplied by the theorems above rather than repeated as input
hypotheses.

## Remaining boundary

Combined with v0.10, global disjointness, coloring compatibility, component
cardinality addition, domination, and connectivity are no longer open proof
obligations.  The remaining construction work is:

- derive existence of the attachment selections from connectedness (their
  claw-free injectivity is now proved);
- instantiate the corrected rooted-trunk theorem in each nontrivial outside
  component; and
- prove the exact size comparison between the selected ambient set and the
  folded bipartite witnesses, including singleton components.

## Verification

After compiling the parent modules into a temporary module directory, the
strict child command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183AttachmentSelection.lean
```

Result: exit code `0` in 10.7 seconds.  The module contains no `sorry`,
`admit`, `#print`, or custom axiom declaration.
