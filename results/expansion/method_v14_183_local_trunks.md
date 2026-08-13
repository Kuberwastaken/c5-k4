# Method v0.14: #183 local trunks and singleton payment

## Singleton correction

A non-root singleton outside component has bipartite order one.  Keeping both
its root and its attachment in the ambient dominating set would cost two, so it
cannot satisfy the desired local budget.  The exact construction instead keeps
only the attachment.  That attachment is connected to `x` and dominates the
omitted singleton root; the singleton root itself is retained as the
one-vertex induced-bipartite witness.  The local cost and witness order are
both one.

`singleton_local_package` verifies every part of this construction in Lean:
attachment membership, branch connectedness, domination of the component,
witness support, witness bipartiteness, and the exact cardinality budget.

## Flexible final interface

`LocalBranchData` permits either:

- a nontrivial rooted-trunk branch containing the attachment and trunk; or
- the attachment-only singleton branch above.

All its assumptions are component-local.  Lean derives the global connected
dominating set, sums the local branch budgets, uses the root-component witness
to pay for `x`, folds the component bipartite witnesses, and produces
`OutsideBudgetCertificate` through
`outsideBudgetCertificateOfLocalBranches`.

Thus the remaining explicit hypotheses are the weakest honest local ones:
construct a connected attachment branch dominating its outside component,
construct a component-supported induced-bipartite witness, and prove the local
branch-cardinality bound.  The singleton case is discharged completely here;
the nontrivial case is exactly where the corrected rooted-trunk principle is
to be instantiated.  The theorem `nontrivial_rootedTrunk_local_package`
provides that adapter: a rooted trunk, its local domination/connectedness facts,
and an induced-bipartite witness satisfying `|T|+1 <= |B|` yield every field
needed for the flexible branch.  Consequently only the underlying classical
nontrivial rooted-trunk construction itself remains external.

## Verification

After compiling the parent modules into a temporary module directory, the
strict child command was:

```bash
LEAN_PATH=/tmp/c5k4_183_attachment_selection_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183LocalTrunks.lean
```

Result: exit code `0`.  The module contains no `native_decide`, `sorry`,
`admit`, `#print`, or custom axiom declaration.
