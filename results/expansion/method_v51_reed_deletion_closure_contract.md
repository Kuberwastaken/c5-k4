# Frozen theorem-shadow trial: deletion closure of the v49 Reed graph

Date: **2026-08-13 UTC**

Target: the current DeepMind finite-graph Reed declaration
`2 * χ(G) ≤ ω(G) + Δ(G) + 2` only.

## Structural observation frozen before evaluation

The v49 graph has exact profile `(χ,ω,Δ)=(9,7,10)` and doubled slack one.
The v50 exhaustive menu established that deleting **each one** of its 89 edges
produces an eight-colorable graph (indeed every row has exact `χ=8`).

Colorability is monotone under edge deletion.  Therefore, if a deletion set
contains any genuine edge `e`, the resulting graph is a subgraph of the
already eight-colorable graph obtained by deleting `e` alone.  It too is
eight-colorable.  Thus v50 does not merely rule out one-edge pruning: it rules
out every nonempty edge-deletion operation from this base graph.

## Preregistered work

1. Refresh the exact upstream file and require the finite declaration to
   remain `research open` with the same source blob.
2. Re-run the 995 connected Atlas-graph Reed gate and require zero violations.
3. Reconstruct the frozen v49 graph and require its digest and exact profile.
4. Formalize the general deletion-closure lemma in Lean: if every genuine
   singleton-edge deletion is `q`-colorable, then every deletion set meeting
   the graph's edge set is `q`-colorable.
5. Apply the already completed v50 certificate table at `q=8`; do not launch
   another graph menu.

Every process is capped at 60 seconds.  No public action or numerical
counterexample claim is authorized.

