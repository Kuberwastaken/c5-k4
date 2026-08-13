# Method v0.46: Lean certificate for the WOWII #133 Heawood contraction

Date: 2026-08-13 UTC
Status: complete finite hold certificate; no universal claim

## Scope

[`GraphConjecture133HeawoodContraction.lean`](../../lean/GraphConjecture133HeawoodContraction.lean)
formalizes the unique isomorphism class produced by contracting one edge of
the Heawood graph in the frozen prospective lane.  The graph is presented by
its explicit twenty-edge Boolean table on `Fin 13`, corresponding to graph6
`LhcIGCP_GGc@_P`.

This artifact proves the complete source-shaped WOWII #133 inequality on that
finite graph.  It is a hold certificate for a rejected transformation, not a
counterexample and not a proof of the universal conjecture.

## Compiled facts

The warning-clean file proves, without `sorry`:

- `contractedHeawood_connected`;
- `contractedHeawood_c4Free` for the source's not-necessarily-induced C4
  predicate;
- `contractedHeawood_triangleFree`;
- `contractedHeawood_radius`:
  `contractedHeawood.radius.toNat = 2`;
- `contractedHeawood_degree_profile`: vertex zero has degree four and all
  other vertices have degree three;
- `contractedHeawood_averageDegree`:
  `averageDegree contractedHeawood = 40/13`;
- `contractedHeawood_l` and `contractedHeawood_floor_l`:
  the source local invariant is `40/13` and its floor is three;
- `targetPath_isInduced`: `[0,1,2,11,10]` is an induced path;
- `five_le_contractedHeawood_path`;
- `contractedHeawood_radius_add_floor_l_le_path`, the exact C4-free decision
  wall `2 + 3 <= path`;
- `contractedHeawood_sourceConclusion`, the current source-shaped proposition
  with the C4-characteristic exponent;
- `contractedHeawood_hold_certificate`, packaging all of these facts.

The local `SourceConclusion` reproduces the current upstream formula exactly
but is kept local so the certificate imports only the already compiled #133
invariant interface.  Triangle-freeness transfers local independence to
ordinary degree through `GraphConjecture133Next`, eliminating any need to
compute noncomputable maximum independent sets directly.

## Honest boundary

The Lean file does not prove that this edge table is obtained by contracting
a particular formal Heawood construction; that provenance is established by
the exact discovery ledger and graph6 certificate.  It also does not compute
the maximum induced-path order, which is seven experimentally.  The source
statement only needs the explicit five-vertex induced path, so formal exact
maximization would add cost without strengthening the decision.

## Verification

Every subprocess was capped at 60 seconds.  From the unmodified
`formal-conjectures` Lake project, the final warning-as-error command was:

```text
timeout 60s env LEAN_PATH=/Users/kuber.mehta/Projects/c5-k4/lean \
  lake env lean -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133HeawoodContraction.lean
```

It exited successfully with no output in approximately six seconds.  A
temporary `#print axioms` audit reported only `propext`, `Classical.choice`,
`Lean.ofReduceBool`, `Lean.trustCompiler`, and `Quot.sound`; it reported no
`sorryAx` or project-specific axiom.  The temporary print commands were
removed, and a source scan found no `sorry`, `admit`, or custom `axiom`.

No commit, push, release, issue, PR, or other public action was performed.
