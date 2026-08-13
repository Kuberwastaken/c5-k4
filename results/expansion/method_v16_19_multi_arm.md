# Method v0.16 proof extraction: WOWII 19 multi-arm witness

Date: **2026-08-13 UTC**

Status: **all 14 v0.15 Atlas residuals closed by whole-graph/one-deletion certificates; reusable Lean reductions proved**

## Frozen residual test

The 14 residual controls from v0.15 were tested before choosing the formal
interface.  Every one satisfies the exact count

```text
|V| >= diameter + localMax - 1.
```

More specifically:

- six are bipartite, including the smallest tree `EiGO`;
- each of the other eight becomes bipartite after deleting one vertex;
- for every nonbipartite residual, `|V| = diameter+localMax`, so the induced
  bipartite graph after one deletion has exactly the required order;
- the six bipartite rows have count slack zero or one.

Thus the multi-arm construction is literal: retain all branches, deleting at
most one odd-cycle-transversal vertex.  No second countermodel appears in the
frozen residual set.

## Lean certificate

[`lean/GraphConjecture19MultiArm.lean`](../../lean/GraphConjecture19MultiArm.lean)
proves warning-clean no-`sorry` reductions for this structure:

```text
G bipartite                         => b(G) >= |V|,
G-z induced bipartite               => b(G) >= |V|-1,
G bipartite and d+M <= |V|+1        => WOWII 13,
G-z bipartite and d+M <= |V|        => WOWII 13.
```

Here `M=localMax`.  The proof retains the full finite vertex set or its erase,
inserts the induced bipartite witness into the repository `sSup` definition of
`b`, and performs the exact integer/real count transfer.

This formally captures all-arms retention as a reusable graph/block-class
certificate.  It closes the entire 14-row bounded residual ledger when paired
with their exact computed bipartiteness/deletion witnesses.  It is not a full
proof of WOWII 13: arbitrary larger graphs need not have odd-cycle transversal
at most one, and the count hypotheses still need a structural derivation for a
general multi-arm decomposition.

The next mathematical gap is therefore no longer represented by any connected
Atlas graph through order seven.  A full proof needs to generalize the count to
a multi-branch core while charging a larger odd-cycle transversal against
surplus vertices off a diametral path.

## Trust

The exact residual script completed in 2.4 seconds under the 60-second cap.
Lean compilation under `-DwarningAsError=true` exited 0.  No `native_decide`,
`sorry`, `admit`, custom axiom, commit, push, or external action was used.
