# Method v0.16: #183 tree-trunk existence

## Edge-case audit

The rooted construction works uniformly for an edge, path, or star, but the
deleted leaf must be distinct from the prescribed root.  On `K2`, if the root
is one endpoint, delete the other.  On a rooted star, delete any leaf other
than the root (if the root is itself a leaf); if the root is the center, delete
any leaf.  Thus there is no mathematical exception among nontrivial trees.

## Formalized construction

For a connected graph and a degree-one vertex `q`, Lean proves that

```text
D = V - {q}
```

is connected dominating.  It also proves `|D|+1=|V|`.  If `q` differs from the
prescribed root, the root belongs to `D`.  These results are packaged as
`rooted_deleteLeaf_trunk` without any graph-order shortcut or computation.

The tree-component endpoint `treeComponent_package_of_leaf` feeds the exact
deleted-leaf budget through the named v0.15 tree adapter.  The root membership
is derived from the chosen leaf being distinct from the root and transported
to the flattened trunk explicitly; the cardinality and ambient
connectivity/domination flattening facts also remain explicit while those
coercion lemmas remain outside Mathlib.

## Remaining boundary

The only tree-specific existence lemma still missing from the library is the
root-sensitive choice: every finite nontrivial tree has a degree-one vertex
different from a prescribed root.  Mathlib currently exposes existence of one
degree-one vertex, which is insufficient when that chosen vertex equals the
root.  The edge/path/star audit confirms this is a formal-library gap, not a
mathematical exception.

## Verification

The strict command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183TreeTrunkExistence.lean
```

Result: exit code `0` in 6.9 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
