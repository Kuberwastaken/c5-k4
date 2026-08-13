# WOWII 40 v0.28: include-dominant recursive branch

## Outcome

The complementary branch of the one-vertex separator envelope now has an
exact recursive interpretation.

For a finite graph `H` with designated vertex `c`, define its constrained
include-deficiency by

```text
includeDeficiency(H,c) = |V(H)| - forestOrderIncluding(H,c).
```

When the include branch dominates at a one-vertex separation, the global
feedback coordinate is exactly additive across the recursively typed sides:

```text
feedbackDeletion(G)
  = includeDeficiency(G[L],c) + includeDeficiency(G[R],c).
```

Together with v0.27, the max envelope therefore supplies a complete recursive
dichotomy:

```text
exclude branch: tau(G) = tau(G-c) + 1
include branch: tau(G) = includeDeficiency(G[L],c)
                       + includeDeficiency(G[R],c).
```

Ties may satisfy both descriptions, as expected. The file also packages exact
and upper-bound wrappers for consuming recursively established side values.
This is the natural state recurrence needed by a block-tree induction: the
exclude branch allocates one feedback unit to the cut/leaf step, while the
include branch splits into two strictly side-local constrained subproblems.

## Verification

The full 22-module dependency chain was rebuilt in topological order into the
fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_include_branch_final.W1GEM4`.
Every Lean process used an explicit olean output,
`-DwarningAsError=true`, and a 60-second process cap; all 22 returned exit code
zero. The new source contains no `native_decide`, `sorry`, `admit`, `#print`,
or custom axiom.
