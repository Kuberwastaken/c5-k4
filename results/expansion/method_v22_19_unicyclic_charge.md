# Method v0.22 proof extraction: unicyclic charge classes

Date: **2026-08-13 UTC**

Status: **connected bipartite class closed unconditionally; exact two-route odd-unicyclic certificate proved and covers all bounded controls**

## Exact tests before formalization

All 54 connected unicyclic graphs in the Graph Atlas were evaluated exactly.
No graph violated

```text
tau_odd + diameter + localMax <= n+1.
```

The 37 nonbipartite (odd-cycle) rows split exactly across two structural
routes:

```text
25 have localMax < maximumDegree,
18 have diameter + maximumDegree <= n,
6 satisfy both.
```

Thus every odd-unicyclic Atlas graph satisfies at least one route.  A second
deterministic test generated 5,750 labeled unicyclic graphs of orders 8--30 by
adding one seeded random nonedge to a seeded random tree.  Again there were
zero charge failures.  The combined subprocess completed in 3.6 seconds under
the 60-second cap.

## Formal class theorems

[`lean/GraphConjecture19UnicyclicCharge.lean`](../../lean/GraphConjecture19UnicyclicCharge.lean)
uses the unconditional v0.21 theorem
`diameter+maximumDegree<=n+1` and v0.19's
`localMax<=maximumDegree` to prove:

1. if `localMax<maximumDegree`, then `diameter+localMax<=n`;
2. a one-vertex odd-cycle transversal plus that strict local discount satisfies
   the full transversal charge;
3. alternatively, a one-vertex transversal plus the sharper count
   `diameter+maximumDegree<=n` satisfies the charge;
4. either route therefore proves WOWII 13;
5. every finite connected bipartite graph satisfies WOWII 13 unconditionally.

The last result strictly extends the completed tree class and includes every
even-unicyclic graph.

For odd-unicyclic graphs, the formal theorem uses an explicit cycle-vertex
deletion certificate and the exact disjunction observed in every bounded
control:

```text
localMax < maximumDegree
or
diameter + maximumDegree <= n.
```

This is a substantial one-transversal graph class, but it is not advertised as
an unconditional theorem for all unicyclic graphs.  Mathlib has no native
unicyclic/pseudoforest/cactus predicate or cycle-core decomposition from which
to derive the disjunction.  Proving that structural decomposition is the exact
remaining formal step for a blanket odd-unicyclic theorem.

No counterconfiguration was found: all 54 exhaustive Atlas rows and 5,750
larger deterministic controls satisfy the charge.  The hypotheses remain
explicit because bounded evidence is not substituted for the missing
unicyclic-core proof.

## Trust

Lean compiled with `-DwarningAsError=true`, exit 0.  No `sorry`, `admit`,
`native_decide`, custom axiom, commit, push, or public action was used.
