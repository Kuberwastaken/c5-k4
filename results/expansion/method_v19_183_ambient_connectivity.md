# Method v0.19: #183 ambient connectivity transport

## Outcome

The last tree-component coercion field is closed.

The module defines the explicit graph homomorphism from the leaf-deleted graph
on the connected-component subtype, through the outside-vertex subtype, into
the ambient graph induced on the flattened trunk.  It proves the homomorphism
injective and maps source walks endpoint-by-endpoint to establish ambient
preconnectedness and nonemptiness.

The theorem `leafDeletionAmbientConnected` proves the exact named proposition
left by v0.18.  Consequently `exists_treeComponent_local_package` is now
unconditional given only:

- the selected outside component;
- nontriviality of its support; and
- the assertion that its component graph is a tree.

It chooses the root-sensitive leaf, constructs and flattens the deleted-leaf
trunk, and returns the complete local package consumed by the final component
fold.  No subtype-to-ambient transport premise remains.

## Verification

The strict command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183AmbientConnectivity.lean
```

Result: exit code `0` in 6.4 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
