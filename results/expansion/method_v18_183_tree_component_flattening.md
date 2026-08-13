# Method v0.18: #183 tree-component flattening

## Outcome

The tree-component coercion boundary is reduced to one named transport fact.

The module maps the leaf-deleted finset on the connected-component subtype to
outside vertices and proves:

- exact membership: a vertex is retained iff it lies in the component and is
  not the deleted leaf;
- exact cardinality preservation under subtype flattening;
- domination of the entire outside component;
- root membership for the root-sensitive leaf chosen in v0.17.

The endpoint `exists_treeComponent_local_package_of_flattening` selects a leaf
distinct from the prescribed root, constructs the flattened trunk, and returns
the full local package consumed by the v0.14 fold, conditional only on
`LeafDeletionAmbientConnected`: connectedness after the two subtype-forgetful
maps into the ambient graph.

Thus all tree mathematics and every other coercional field are closed.  One
pure graph-embedding connectivity lemma remains; it contains no cardinality,
domination, attachment, or tree-existence content.

## Verification

The strict command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183TreeComponentFlattening.lean
```

Result: exit code `0` in 6.3 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
