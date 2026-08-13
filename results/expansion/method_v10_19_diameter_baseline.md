# Method v0.10 proof extraction: WOWII 19 diameter baseline

Date: **2026-08-13 UTC**

Status: **geodesic endpoint splice proved in warning-clean no-`sorry` Lean; full WOWII 13 baseline not yet claimed**

## Target

The non-self-centered branch of WOWII 19 reduces to the solved source
inequality WOWII 13,

```text
b(G) >= diameter(G) + max_v lambda(v) - 1,
```

where `lambda(v)` is the independence number of the open neighborhood of
`v`.  The current upstream WOWII 13 declaration contains `sorry`, so this
proof-extraction lane does not import it.

The intended combinatorial construction starts at a diametral endpoint `u`,
takes a maximum independent set `A` in `N(u)`, and splices it to a shortest
`u`--`v` path after deleting the path's first vertex.  The retained vertex set
is schematically

```text
A union {x_0, x_2, x_3, ..., x_d}.
```

It has `|A| + d` vertices and is bipartite: members of `A` can meet the
retained path only at `x_2`.

## New formal result

[`lean/GraphConjecture19DiameterBaseline.lean`](../../lean/GraphConjecture19DiameterBaseline.lean)
proves the complete metric and adjacency-separation core of that splice.

For a shortest walk `p` it establishes:

1. exact segment distances,
   `dist(p[i], p[j]) = Nat.dist i j`;
2. chordlessness whenever `i + 2 <= j`;
3. if `a` is adjacent to the initial endpoint, then
   `a != p[i]` for every `i >= 2`;
4. the key splice fact, `not Adj a p[i]` for every `i >= 3`;
5. the corresponding set-level statement for an arbitrary independent
   `A subset N(u)`;
6. a packaged diametral-geodesic existence theorem carrying all these facts.

The final packaged endpoint is:

```lean
theorem exists_diametral_geodesic_from_endpoint
    (hconn : G.Connected) (u v : V)
    (huv : G.dist u v = G.diam) :
    exists p : G.Walk u v,
      p.IsPath and p.length = G.diam and
      (forall a, G.Adj u a ->
        (forall i, 2 <= i -> i <= p.length -> a != p.getVert i) and
        (forall i, 3 <= i -> i <= p.length ->
          not G.Adj a (p.getVert i)))
```

This proves that the proposed geodesic splice has no hidden graph-theoretic
edge obstruction.  Only `p.getVert 2` can interact with the independent
neighborhood layer, exactly as required by the alternating bipartition.

## What this does and does not close

If a diametral endpoint `u` also attains `max_v lambda(v)`, the displayed
splice gives the stronger bound

```text
b(G) >= diameter(G) + max_v lambda(v),
```

one above WOWII 13.  The present file deliberately stops before claiming this
endpoint because the remaining Lean work is representation plumbing:

- construct the finite union from `A`, `u`, and indices `2..p.length`;
- give its alternating two-coloring;
- prove its exact cardinality using path injectivity and the newly proved
  non-overlap facts;
- insert it into the `sSup` definition of `b`.

More importantly, the **full** WOWII 13 theorem does not assume that a vertex
attaining maximum local independence is a diametral endpoint.  The endpoint
splice alone therefore does not prove the global maximum version.  A complete
proof still needs one of:

- a construction coupling an arbitrary `lambda`-maximizing vertex to a
  diametral path while losing at most one vertex overall; or
- a reduction showing that some diametral endpoint has local independence at
  least `lambda_max - 1`.

Neither coupling statement is asserted here.  This is the exact mathematical
boundary, distinct from the now-settled shortest-path separation facts.

## Trust and build audit

Compiled against current `formal-conjectures` with the subprocess below kept
under the 60-second cap:

```text
lake env lean -R .../c5-k4/lean -DwarningAsError=true \
  .../GraphConjecture19DiameterBaseline.lean
```

Result: **exit 0**.  The source has no `sorry`, `admit`, custom `axiom`, or
embedded `#print`.  The endpoint's axiom audit is exactly:

```text
[propext, Classical.choice, Quot.sound]
```

No upstream conjecture theorem and no `sorryAx` is inherited.
