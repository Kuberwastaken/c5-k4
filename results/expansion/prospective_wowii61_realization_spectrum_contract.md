# Frozen prospective trial: WOWII 61 realization spectra

Frozen: 2026-08-13 UTC, before the first development evaluation.

## Target and status lock

The sole target is the current theorem
`FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean` at upstream
commit `9a1636c4030039f70cf78b866c216d8b6c5f35b0`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3)
```

for finite nontrivial connected simple graphs. The file SHA-256 is
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`.
The recovered WOWII row is marked open, dated March 25, 2004, and agrees with
the Lean reading. Read-only GitHub issue and PR searches on the freeze date
found no target-specific resolution claim.

## Independence from the degree-geometry lane

This trial does not compare majorizing degree sequences, alter threshold
multiplicities, or test the residual-overshoot proof bridge. Degree sequences
are used only as strata with a fixed residue. The prospective variable is the
range of diameter and induced-forest values across multiple nonisomorphic
realizations of the same sequence.

Define

```text
R61(G) = forest(G) - residue(G) - ceil(diameter(G)/3).
```

A negative value is a conjecture candidate. Within one degree-sequence
stratum, prioritize realizations minimizing `forest-ceil(diameter/3)` and
record the full realization spectrum, including null variation.

## Frozen database-sanity gate

Before evaluating any development stratum, independently recompute degree
sequence, every Havel--Hakimi state, connectivity, diameter, and exact largest
induced forest for:

- every connected nontrivial Graph Atlas graph through order seven;
- `C5--C10`, `P2--P10`, Petersen, `K3,3`, complete graphs through order ten,
  stars through order twelve, and complete bipartite graphs through order
  twelve;
- `C5[K2]`.

Any negative residual pauses the trial for a source/reading audit. The gate
must be appended to the ledger before construction begins.

## Frozen development strata

1. **Exhaustive small realization spectrum.** Enumerate every connected
   nonisomorphic graph of orders `2..8` (Atlas through seven, nauty at eight).
   Group by exact degree sequence and retain the complete diameter, forest,
   and residual spectrum for each stratum.
2. **Exhaustive graphical sequences.** Enumerate every nonincreasing
   positive graphical sequence at orders `8..12` whose degree sum is at least
   `2(n-1)`. Order strata by decreasing Havel--Hakimi residue, then increasing
   edge count, then lexicographically. Evaluate until either every stratum is
   processed or the global sequence budget is reached.
3. **Multiple realization sampling.** For each processed sequence, construct
   connected realizations from deterministic Havel--Hakimi seeds and
   degree-preserving double-edge-switch walks. Retain at most 64 pairwise
   nonisomorphic realizations per sequence and require at least two whenever
   two can be found within 256 attempts. The deterministic seed is
   `61006120260813`.
4. **Random high-order tail.** If the exact sequence budget remains, sample
   positive graphical sequences of orders `13..18`, biased toward the upper
   quartile of residue at each order, and retain at most 32 nonisomorphic
   connected realizations per sequence.

No construction family or ranking rule may be added after observing results.

## Budgets and exactness

- at most 20,000 graphical sequences;
- at most 25,000 connected nonisomorphic realizations;
- at most 256 realization attempts per sequence;
- at most 8,000 random-tail sequences;
- every subprocess and every exact induced-forest solve capped at 60 seconds;
- append a ledger record after the gate, every 100 completed sequences, every
  improved residual, every timeout, and the final verdict.

Induced forests are solved by decreasing-cardinality subset enumeration with
an explicit acyclicity test. A timed-out solve is `INCONCLUSIVE` and cannot
support a candidate. Isomorphism rejection uses WL bucketing followed by an
exact isomorphism check. Graphicality and residue are recomputed from the
degree sequence for every retained graph.

## Candidate protocol

Before recording `CONJECTURE_CANDIDATE`:

1. rerun the current-source and GitHub novelty/status audit;
2. recompute the full Havel--Hakimi trajectory independently;
3. independently verify connectivity and diameter;
4. produce a maximum induced-forest witness and an exact upper certificate;
5. replay the database gate with both implementations;
6. record graph6, an edge list, degree sequence, realization provenance, and
   all verification evidence.

No issue, PR, release, commit, push, or other public action is authorized.

## Frozen verdicts

- `CONJECTURE_CANDIDATE`: a negative residual surviving the full protocol.
- `REALIZATION_CLIFF`: a fixed degree sequence with two realizations whose
  residuals differ by at least two, including one at residual zero.
- `HOLD_BOUNDED`: no crossing within the frozen universe.
- `INCONCLUSIVE`: a potentially relevant exact solve timed out.
