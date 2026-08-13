# Method v0.18 proof extraction: transversal-charge classes

Date: **2026-08-13 UTC**

Status: **diameter-at-most-two class proved unconditionally; bipartite/tree and one-deletion classes reduced to sharp order counts**

## Pre-formalization controls

The frozen deterministic order-8--10 sample from v0.17 was rerun with class
labels before formalization.  Among 5,516 connected graphs it contained:

```text
425 bipartite graphs,
1,573 graphs with tau_odd <= 1,
2,356 graphs with diameter <= 2.
```

There were zero failures of
`tau_odd+diameter+localMax <= n+1` in every class (and zero overall).  The run
completed in 27 seconds under the 60-second cap.

## Formal results

[`lean/GraphConjecture19TransversalChargeClasses.lean`](../../lean/GraphConjecture19TransversalChargeClasses.lean)
proves:

- bipartite graphs have `tau_odd=0`;
- a certified one-vertex deletion gives `tau_odd<=1`;
- the complement of a maximum induced star is always an odd-cycle
  transversal, yielding the universal inequality
  `tau_odd+localMax+1 <= n`;
- consequently every graph of diameter at most two satisfies the full charge
  and WOWII 13 unconditionally;
- bipartite graphs (including trees) satisfy the charge once the sharp
  classical order count `diameter+localMax <= n+1` is supplied;
- one-deletion graphs (including many unicyclic and cactus graphs) satisfy the
  charge once `diameter+localMax <= n` is supplied.

The first unconditional class is substantial and does not require
connectedness.  Its proof explains the charge directly: preserve a maximum
induced star and delete every other vertex; the two diameter units are then
exactly absorbed by the `+1` allowance.

## Honest boundary

This file does **not** claim a new formal proof of the classical
order--diameter--maximum-degree inequality for all trees.  In a bipartite graph
each neighborhood is independent, so `localMax` is the maximum degree and the
remaining tree count is the familiar `diameter+Delta <= n+1`.  Mathlib has the
individual degree and diameter APIs but no ready theorem connecting them; a
no-`sorry` proof requires a separate diametral-path/off-path-neighbor counting
development.

Likewise, `tau_odd<=1` alone does not imply the sharper order count needed in
the one-deletion class without additional structure.  These conditions are
kept explicit rather than promoted from sampled evidence.

## Trust

Lean compiled with `-DwarningAsError=true`, exit 0.  No `native_decide`,
`sorry`, `admit`, custom axiom, commit, push, or external action was used.
