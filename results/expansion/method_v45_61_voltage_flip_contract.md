# Frozen prospective trial: WOWII 61 realization-cliff voltage flip

Frozen: **2026-08-13 UTC, before evaluating any lifted graph**

## Exact target

For a finite connected simple graph `G`, current DeepMind WOWII 61 asserts

`residue(G) + ceil(diameter(G) / 3) <= largestInducedForestSize(G)`.

The signed residual is

`R61 = forest - residue - ceil(diameter / 3)`;

a crossing has `R61 < 0`.

## Pre-freeze analysis of the complete order-eight spectrum

The independent regrouping of all 11,117 connected order-eight records
reproduced the exact 36 realization-cliff strata used here: degree sequences
with minimum residual zero and residual spread at least two.

All 36 selected tight realizations have diameter four. Thirty-one have
`(residue, forest) = (3,5)` and five have `(4,6)`. Equivalently, every tight
base has feedback-vertex number equal to its residue. This is the forest lock
to preserve while moving the diameter across the next ceiling boundary.

The frozen base is graph6 `G?aN]w`, degree sequence
`(5,5,4,4,4,2,1,1)`, with `residue=3`, `diameter=4`, `forest=5`, and
`R61=0`. It was selected before lift evaluation because:

- its exact degree-sequence stratum has only eight realizations;
- it has two pendant diameter endpoints and a dense feedback core;
- it has 13 edges and cycle rank 6, giving a complete 64-class bounded lift
  experiment after spanning-tree gauge fixing.

## Frozen transformation

Construct canonical two-lifts of `G?aN]w`. Fix voltage zero on a deterministic
BFS spanning tree and enumerate all `2^6` assignments on the six cotree edges.
The all-zero lift is disconnected and is a control; retain the 63 nonzero
assignments and require connectedness exactly.

Each retained graph has the duplicated degree multiset
`(5,5,5,5,4,4,4,4,4,4,2,2,1,1,1,1)`, so every voltage flip preserves the
entire degree sequence and hence the Havel--Hakimi residue.

The sole prospective move is a **one-cotree-edge voltage flip** between two
connected lift assignments at Hamming distance one. A directed crossing pair
must satisfy:

1. source lift is tight (`R61=0`);
2. target has a larger `ceil(diameter/3)`;
3. target has the same residue automatically;
4. target forest is no larger than source forest;
5. therefore target has `R61<0`.

No adaptive change of base, lift degree, gauge, or Hamming radius is allowed.

## Exact evaluation and stop rules

- Havel--Hakimi residue: exact deterministic integer trajectory, with the
  common trajectory retained.
- Diameter: all-pairs BFS, with an explicit geodesic witness.
- Largest induced forest: exact descending subset enumeration/bitset cycle
  test on 16 vertices, with a maximum forest witness and exhaustive upper
  certificate. Any candidate is independently recomputed using minimum
  feedback-vertex-set enumeration.
- Evaluate at most 63 connected lifts and all Hamming-one edges among them.
- Stop immediately for independent candidate verification if a crossing pair
  appears; otherwise close as a bounded hold after the complete class.

Every subprocess has a hard 60-second cap. Append the ledger after the base
recheck, lift-class evaluation, and independent verification. No commit, push,
release, issue, PR, or other public action is authorized.

