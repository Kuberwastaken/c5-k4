# Method v0.24: WOWII #183 exact triangle branch

Date: 2026-08-13
Status: separate `C3` branch verified; no weaker budget required

## Correction and exact alternative

The earlier v0.22 commentary treated `C3` as a local-budget obstruction.  The
formal check shows the opposite: relative to any prescribed root, delete the
other two triangle vertices.

The retained set is the root singleton.  It is:

- connected;
- bipartite;
- dominating, because the root is adjacent to both deleted vertices; and
- root-preserving by construction.

Thus `C3` satisfies the same `IsGoodTwoDeletion` structural predicate as the
longer odd-cycle branch.  It merely needs a separate root-sensitive selector
because the v0.22 `{0,1}`/`{2,3}` selector assumes `n >= 5`.

## Exact budget

For a triangle component:

```text
component order                         n = 3
retained connected dominating trunk    t = 1
maximum induced-bipartite witness       b = 2
mandatory attachment plus trunk         t + 1 = 2.
```

Consequently the ordinary two-deletion hypotheses are sharp:

```text
t + 2 <= n       1 + 2 <= 3
n <= b + 1       3 <= 2 + 1
t + 1 <= b       2 <= 2.
```

No slack transfer, attachment waiver, or weakened local budget is needed.
The exact local alternative is simply:

> retain the prescribed root and delete the other two vertices.

## Lean certificate

[`lean/GraphConjecture183TriangleBranch.lean`](../../lean/GraphConjecture183TriangleBranch.lean)
defines

```text
trianglePair r = (r + 1, r + 2)
```

on `Fin 3` and proves:

- `trianglePair_avoids_root`;
- `trianglePair_isGoodTwoDeletion`; and
- the exact specialization of `twoDeletion_budget` at `(t,b,n)=(1,2,3)`.

The concrete proof uses ordinary kernel reduction and finite case splitting;
it does not use `native_decide`.

## Verification

The complete recursive #183 chain was compiled from source into the fresh
directory `/tmp/c5k4_183_triangle_audit.HLLje6`.  Each module used:

```bash
LEAN_PATH=/tmp/c5k4_183_triangle_audit.HLLje6 timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_183_triangle_audit.HLLje6/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

All dependencies from `GraphConjecture183OutsideBudget` and
`GraphConjecture183Attachment` through
`GraphConjecture183CycleComplementPath` passed, followed by the new
`GraphConjecture183TriangleBranch`.  Every invocation exited `0`, emitted no
Lean diagnostics, used warnings-as-errors, and was individually capped at 60
seconds.  The new module contains no `sorry`, `admit`, `native_decide`,
`#print`, or custom axiom declaration.
