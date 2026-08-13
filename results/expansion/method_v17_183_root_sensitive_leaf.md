# Method v0.17: #183 root-sensitive tree leaf

## Result

The missing tree lemma is now proved: for every finite nontrivial tree and
every prescribed root `r`, there is a degree-one vertex `q != r`.

The proof is a degree-sum argument.  If `r` were the only leaf, connectedness
would force every other vertex to have degree at least two.  The total degree
would then be at least `2n-1`, contradicting the tree identities
`|E|=n-1` and `sum degree = 2|E|`.

The theorem `IsTree.exists_rooted_deleteLeaf_trunk` combines this result with
v0.16 and returns the rooted connected-dominating trunk `V-{q}` with exact
budget `|D|+1=|V|`.

## Component integration

This removes the only tree-specific mathematical existence gap identified in
v0.16.  The remaining component-level work is coercional: flatten the
leaf-deleted finset on the component subtype to outside vertices and discharge
the already-explicit ambient connectivity/domination transport fields of
`treeComponent_package_of_leaf`.

## Verification

The strict command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183RootSensitiveLeaf.lean
```

Result: exit code `0` in 7.3 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
