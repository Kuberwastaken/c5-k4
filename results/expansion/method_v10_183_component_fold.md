# Method v0.10: #183 connected-component fold

## Outcome

The arbitrary-graph additive component layer is now formalized.  Lean first
records the exact partition theorem: connected-component supports are pairwise
disjoint and their union is the whole vertex set.

For a finite graph `H`, assign each connected component `c` a finite witness
`B c` contained in `c.supp`.  Lean proves that witnesses belonging to distinct
components are:

- disjoint, because a common vertex identifies the components; and
- anticomplete, because one cross edge would put both endpoints in the same
  connected component.

It then folds any finite collection of the witnesses and proves both

```text
H[union B c] is bipartite
```

and

```text
|union B c| = sum |B c|.
```

For any explicitly selected finite collection `C` of components this gives the
unconditional invariant bound

```text
sum_(c in C) |B c| <= b(H).
```

## Reduced construction boundary

`ComponentFoldInput G x` packages an explicit finite component collection,
local bipartite witnesses in `G-N(x)`, an ambient finite set `D`, and only two remaining
global obligations:

1. `D` is connected dominating in `G`; and
2. the rooted-trunk and singleton accounting proves
   `|D| <= sum_c |B c|`.

The definition `outsideBudgetCertificate_of_componentFoldInput` converts this
data unconditionally into `OutsideBudgetCertificate G x`.  Thus no further
disjointness, anticompleteness, coloring compatibility, or finite-union
cardinality argument remains inside `NontrivialComponentConstruction`.

The next mathematical boundary is now precisely the attachment-neighbor
selection that constructs `D`, proves its ambient domination/connectivity, and
connects its size to the already-formalized local trunk/singleton budget.

## Verification

After compiling the parent modules into a temporary module directory, the
strict child command was:

```bash
LEAN_PATH=/tmp/c5k4_183_component_fold_v1 timeout 60s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture183ComponentFold.lean
```

Result: exit code `0` in 6.8 seconds.  The module contains no `sorry`, `admit`,
`#print`, or custom axiom declaration.
