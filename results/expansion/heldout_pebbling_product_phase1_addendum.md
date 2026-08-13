# Graph pebbling product — Phase 1 threshold-shell addendum

Frozen: **2026-08-13 UTC**, before constructing `L □ L` or any pebble state.

This activates only the 4,032 states frozen in
`heldout_pebbling_product_phase0_contract.md` (current Phase 0 contract digest
`0b9ccc12583c84e9a2932daa13b58f89e9c03bcedbe03a04c6dc0e42249f3eb6`).
No graph substitution, support change, redistribution, or extra state is in
scope.

## Frozen graph and state order

The two factors are the labelled original Lemke graph with roles `v1,...,v8`
and the 13-edge table in the Phase 0 contract. Product vertices are ordered
lexicographically as `(vi,vj)`. Roots are enumerated in that order; for each
root, the extra-pebble location is enumerated in the same order with the root
omitted.

For every `(r,x)`, `x != r`, the state is exactly

```text
D(r,x)(r)=0, D(r,x)(x)=2, D(r,x)(u)=1 otherwise.
```

## Frozen directional prediction

Every one of the 4,032 states is root-solvable. Choose the lexicographically
first shortest path

```text
x = p0, p1, ..., pk = r.
```

Initially `p0` has two pebbles. After moving from `p0` to `p1`, the latter's
existing singleton makes two pebbles. Inductively the same is true at every
internal `pi`; the final move places one pebble on the initially empty root.
The predicted exact coordinates for every row are:

```text
move count = dist(x,r), final root count = 1,
total pebbles after moves = 64 - dist(x,r).
```

This is the obstruction-derived minimal relay around the immobile
63-singleton lower-bound configuration. A completed table matching these
coordinates ends as `PREDICTION_CONFIRMED`; it is also a bounded hold only for
this frozen shell and says nothing about other 64-pebble distributions.

## Exact implementation and independent calibration

The primary oracle constructs the shortest-path move sequence and replays
every move against the literal two-for-one adjacency rule. It stores every
intermediate distribution.

Before the product constructor unlocks, an independent breadth-first search
over the finite distribution transition graph must agree with the primary
oracle on all frozen-shell states of `K2`, `P3`, `K3`, and `C4`, and must
confirm that the corresponding one-pebble-on-every-nonroot states with only
`n-1` pebbles are unreachable. Any mismatch is `GATE_FAIL` with zero product
states.

## Serialization and batching

Each product-state row stores:

- the complete 208-edge labelled product edge list;
- the 64-entry role map `(factor_G_vertex,factor_H_vertex)`;
- the complete initial and final 64-entry distributions;
- root, extra location, shortest vertex path, and literal move replay;
- the labelled graph digest and labelled state digest.

Graph6 is not used as a substitute for labelled data. Rows append to
`heldout_pebbling_product_phase1_ledger.jsonl`.

The exact batch partition is eight consecutive half-open intervals of 504
states:

```text
[0,504), [504,1008), [1008,1512), [1512,2016),
[2016,2520), [2520,3024), [3024,3528), [3528,4032).
```

Every process is externally capped at 60 seconds and has a 55-second internal
deadline. A batch appends after every state. A timeout stops as
`TIMEOUT_BRACKET`; it is never a hold. A single independently replayed
unreachable state stops immediately as `CANDIDATE_LOWER_BOUND`, not as a
counterexample to Graham's conjecture. No later state is evaluated after
either stop.

After all eight batches, finalization requires exactly 4,032 unique consecutive
indices, no timeout/candidate/error row, and a fresh literal replay of every
stored move sequence.

No commit, push, issue, PR, release, or other public action is authorized.
