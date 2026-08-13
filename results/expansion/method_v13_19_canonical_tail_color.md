# Method v0.13 proof extraction: WOWII 19 canonical-tail coloring

Date: **2026-08-13 UTC**

Status: **diametral-endpoint theorem completed in warning-clean no-`sorry` Lean**

[`lean/GraphConjecture19CanonicalTailColor.lean`](../../lean/GraphConjecture19CanonicalTailColor.lean)
completes the canonical endpoint witness left by v0.12.  Rather than choosing
an index preimage for every image vertex, it colors every vertex by parity of
its distance from the endpoint.  On a shortest path that distance equals the
path index.

The proof establishes both remaining v0.11 certificate fields:

- adjacent canonical-tail vertices have index distance one, hence opposite
  distance parity;
- if a neighbor of the endpoint is adjacent to a retained-tail vertex, the
  triangle inequality forces that vertex to have endpoint distance zero or
  two, hence the designated nonzero color.

Combining this coloring with v0.10 metric separation, v0.11 witness assembly,
and v0.12 exact cardinality yields:

```lean
theorem diam_add_indepNeighborsCard_le_b_of_diametral_endpoint
    (G : SimpleGraph V) [DecidableRel G.Adj] (u v : V)
    (hconn : G.Connected) (huv : G.dist u v = G.diam)
    (hdiam : 2 ≤ G.diam) :
    (((G.diam + indepNeighborsCard G u : ℕ) : ℝ)) ≤ b G
```

Thus the endpoint-local construction is now unconditional and even one unit
stronger than WOWII 13.  The only remaining obstruction to the global WOWII
13 baseline is no longer representation plumbing: it is the genuinely global
comparison between maximum local independence and local independence at
diametral endpoints.

Build result under `-DwarningAsError=true`: **exit 0**.  The file contains no
`sorry`, `admit`, custom axiom, or upstream conjecture-theorem dependency.
