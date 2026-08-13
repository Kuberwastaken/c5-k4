# Frozen prospective addendum: critical false-twin rays from the #40 wall

Frozen: 2026-08-13 UTC, before evaluating any transformed graph.

## Input identity and rejection of the line-graph move

This addendum uses the 69 exact equality rows in the canonical first 1,200
attempts of the frozen #40 block-surgery trial.  With

```text
tau_F = n - largest_induced_forest,
tau_B = n - largest_induced_bipartite_order,
L     = n - path_cover_number,
R     = L + tau_B - 2*tau_F,
```

exact equality is precisely the parity wall `R in {1,2}`.  Thirteen rows have
`R=1` and 56 have `R=2`.

The already-frozen line-graph trial is not extended.  All eight of its exact
outputs are Hamiltonian; their residuals are `1,2,3,3,5,5,5,7`, so incidence
closure did not isolate the required negative-residual direction.

## Frozen separating transformation

Use exactly the thirteen canonical `R=1` rows.  For every vertex-orbit
representative `v`, enumerate every maximum induced forest of its seed.  Keep
`v` only when every maximum forest containing it gives it induced degree at
least two.  This is a seed-only criticality test: adding one independent false
twin of `v` then cannot extend a maximum forest merely by adjoining the twin.

For each retained `(G,v)`, replace `v` by an independent false-twin class of
size `k`, preserving its open neighborhood, for the unique values
`k >= 2` that give transformed orders 12 through 16.  This is an iterated
critical-clone ray, not another one/two-edge mutation or a continuation of the
broad bracket.

The prospective separating prediction is exact in residual coordinates.  If
the clone lift keeps the forest maximum fixed, enlarges the bipartite maximum
by every added clone, and preserves path-cover number, then each added clone
changes

```text
(Delta L, Delta tau_B, Delta tau_F) = (1, 0, 1),
Delta R = -1.
```

Thus an `R=1` seed crosses after two such steps.  The exact evaluator, not the
prediction, decides whether those three coordinate conditions actually hold.

## Frozen gate and budget

- Deterministically deduplicate seed automorphism orbits and transformed
  graph isomorphism classes.
- Orders are 12--16, with at most 80 transformed graphs.
- Each exact solve and each process is capped below 60 seconds; timeouts are
  `INCONCLUSIVE`.
- Reuse the already-passed 1,031-control #40 database-sanity gate.
- Log graph6, edges, all three exact witnesses, residual, and coordinate
  changes incrementally.
- Stop at the first strict crossing.  Before any release claim, independently
  recompute it and rerun current source/status/novelty checks.

No commit, push, release, issue, PR, or other public action is authorized in
this lane.

