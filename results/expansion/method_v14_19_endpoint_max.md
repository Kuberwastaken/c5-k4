# Method v0.14 proof extraction: WOWII 19 endpoint maximum

Date: **2026-08-13 UTC**

Status: **proposed global coupling false; corrected two-route sufficient reduction proved**

## Bounded falsification

All 995 connected graphs of orders 2 through 7 in NetworkX's frozen Graph
Atlas were tested exactly.  Neighborhood independence numbers were computed by
exhaustive subset enumeration; diametral endpoints were obtained from exact
eccentricities.  The tested claim was

```text
max{lambda(u) : ecc(u)=diameter} >= max_v lambda(v) - 1.
```

It fails on 191 graphs.  The smallest countermodel is the claw `K1,3`, Graph6
`CF`:

```text
n=4, m=3, diameter=2,
global lambda maximum=3 (at the center),
maximum lambda over diametral endpoints=1 (at every leaf).
```

Thus the endpoint coupling can lose two units already at order four.  This is
not a counterexample to WOWII 13: the induced star is the whole claw and has
order four, exactly its required right-hand side `2+3-1=4`.

## Corrected formal reduction

[`lean/GraphConjecture19EndpointMax.lean`](../../lean/GraphConjecture19EndpointMax.lean)
defines the finite maximum `localMax`, proves it is attained, and formalizes
both valid routes exposed by the countermodel:

1. the maximum induced star always proves `b >= localMax+1`;
2. consequently WOWII 13 holds outright whenever `diameter <= 2`;
3. for diameter at least two, the canonical-tail endpoint theorem proves
   WOWII 13 whenever a diametral endpoint satisfies
   `localMax <= lambda(u)+1`.

Both statements use the exact real-valued `b` normalization and require no
upstream conjecture theorem.

The remaining gap for a full proof is now sharply confined to graphs of
diameter at least three in which every diametral endpoint loses at least two
units from the global local-independence maximum.  The Atlas contains such
graphs already at order five (for example Graph6 `DBc`, with diameter three,
global maximum three, and peripheral maximum one), so neither proved route
alone covers the general case.  A complete proof needs a mixed construction
coupling a nonperipheral maximum-local-independence vertex to a long geodesic,
not an endpoint comparison theorem.

Build under `-DwarningAsError=true`: **exit 0**.  No `sorry`, `admit`, custom
axiom, or external mutation was used.  The bounded search subprocess completed
in 1.5 seconds, below the fixed 60-second cap.
