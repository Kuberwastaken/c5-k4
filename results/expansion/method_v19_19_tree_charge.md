# Method v0.19 proof extraction: tree charge

Date: **2026-08-13 UTC**

Status: **local-independence/degree and acyclic/transversal bridges proved; classical diameter--degree count remains unformalized**

## Exact pre-check

The proposed class lemma

```text
diameter(G) + maximumDegree(G) <= |V(G)| + 1
```

was checked on all 995 connected Graph Atlas graphs and a new deterministic
fixed-seed sample of 5,492 connected graphs of orders 8--10.  There were zero
failures among 6,487 graphs, including 240 trees.  The run completed in 1.7
seconds under the 60-second cap.  This is consistent with the classical
connected-graph inequality; it is not being inferred from the sample.

## Lean results

[`lean/GraphConjecture19TreeCharge.lean`](../../lean/GraphConjecture19TreeCharge.lean)
proves warning-clean no-`sorry` bridges:

1. `indepNeighborsCard G v <= degree G v` for every vertex of every finite
   graph;
2. hence `localMax G <= maxDegree G`;
3. the diameter--maximum-degree order count implies
   `diameter+localMax <= n+1`;
4. acyclicity supplies bipartiteness, hence `tau_odd=0` through v0.18;
5. consequently every finite acyclic graph satisfying the classical count
   satisfies WOWII 13.  Connected trees are the intended specialization.

The first two items are useful beyond trees and remove the need to formalize
the stronger equality `localMax=maxDegree` in bipartite graphs.

## Exact remaining gap

The requested unconditional tree endpoint is not claimed.  The one remaining
Lean theorem is the classical finite connected-graph count

```lean
G.Connected -> G.diam + G.maxDegree <= Fintype.card V + 1.
```

Mathlib supplies maximal-degree vertices, shortest paths, path injectivity,
and `path.length < card`, but no assembled diameter--degree theorem.  A direct
proof must count the union of a diametral path and neighbors of a
maximum-degree vertex, splitting whether that vertex lies on the path and
bounding how many consecutive path vertices its neighborhood can meet.  That
substantial path/Finset intersection development did not fit this rung, so the
hypothesis remains explicit rather than hidden behind an axiom.

## Trust

Lean compiled with `-DwarningAsError=true`, exit 0.  No `native_decide`,
`sorry`, `admit`, custom axiom, commit, push, or external action was used.
