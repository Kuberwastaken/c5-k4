# Method v0.15: #183 nontrivial bipartite trunks

## Result

For any connected component `c` of `G-N(x)`, the module defines the finite
witness consisting of the entire support of `c`.  It proves the exact coercion
and cardinality identities for this witness.

If the component-induced graph is bipartite, the entire support is an induced-
bipartite witness of order `|c|`.  Therefore a rooted connected-dominating
trunk `T` satisfying

```text
|T| + 1 <= |c|
```

feeds directly through the v0.14 nontrivial branch adapter.  All witness
support, bipartiteness, and local budget obligations are derived rather than
left to the caller.

The named Lean theorem `treeComponent_rootedTrunk_local_package` is the tree
specialization: it invokes Mathlib's `IsTree.isBipartite` and then applies the
bipartite adapter.  Mixed assignments built from the v0.14 exact
singleton package and these nontrivial bipartite/tree packages feed directly
to the final outside-budget certificate.

## Remaining boundary

For bipartite components, only the classical rooted trunk itself remains:
construct a rooted connected dominating trunk omitting at least one component
vertex.  The general non-bipartite case additionally needs the full corrected
rooted-trunk theorem to relate trunk order to the maximum induced-bipartite
witness.  Neither assertion is installed as an axiom or hidden in a global
premise here.

## Verification

After compiling the parent module into a temporary module directory, the
strict child command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183NontrivialTrunk.lean
```

Result: exit code `0` in 6.3 seconds.  The module contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom declaration.
