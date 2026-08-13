# Frozen prospective trial: current DeepMind WOWII 61 degree geometry

Frozen: 2026-08-13 UTC, before the first development-family evaluation.

## Current target and status lock

Only the current theorem in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture61.lean` at upstream
commit `9a1636c4030039f70cf78b866c216d8b6c5f35b0` is in scope:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3)
```

for every finite nontrivial connected simple graph.  `residue` is the number
of zero entries left by the canonical descending Havel--Hakimi reduction.

The file is `research open`.  A pre-trial GitHub issue/PR search found no
target-specific solution or counterexample claim for WOWII 61.  Historical
readings outside the current DeepMind declaration are out of scope.

## Prospective mechanism

The existing theorem-extraction chain reduces its missing list-side bridge to
no residual overshoot.  For descending graphical lists `source` and `target`
with initial weak prefix dominance, define

```text
gap(k) = sum(HH^k(source)) - sum(HH^k(target)).
```

The live obstruction asserts `gap(k) <= gap(0)` throughout the admissible
trajectories.  A first failure must overshoot by at least two.  The new trial
prospectively targets graph operations that change threshold multiplicities
at the Havel--Hakimi decrement boundary while retaining graphicality.

Two outcomes are distinguished:

1. a graphical sequence pair with `gap(k) > gap(0)` refutes the proposed
   no-overshoot proof bridge but is not by itself a counterexample to WOWII
   61;
2. a connected graph with
   `forest - residue - ceil(diameter/3) < 0` is a conjecture candidate, subject
   to the full source/status/novelty and independent-verification gate.

## Frozen database-sanity gate

Before any construction lane, evaluate:

- every connected nontrivial Graph Atlas graph through order seven;
- `C5--C10`, `P2--P10`, Petersen, `K3,3`, complete graphs through order ten,
  stars through order twelve, and complete bipartite graphs through order
  twelve;
- `C5[K2]`, the previous dense unit-slack control.

The gate independently recomputes the descending degree sequence, every
Havel--Hakimi state, residue, diameter, and largest induced forest.  Any
database violation pauses the construction search for reading audit.

## Frozen development lanes

Only the following lanes will be evaluated after the database gate passes.

1. **Graphical majorizing transfers.** From connected graphs of orders
   `8..18`, move one or two incident edges from a lower-degree vertex to a
   nonadjacent higher-degree vertex whenever simplicity and connectedness
   survive.  Orient every resulting graphical degree-sequence pair by full
   weak prefix dominance and test every residual-gap prefix.
2. **Split, chain, and nonthreshold defects.** Enumerate split graphs with a
   clique of order `2..8` and nested clique-neighborhoods on the independent
   side, and bipartite chain graphs with Ferrers row lengths.  Add every
   lexicographic one-edge defect and up to 2,000 deterministic two-edge
   defects per seed.  Orders are `6..22`.  Retain graphical pairs sharing
   order and compare all prefix-dominance orientations.
3. **Joins and unequal blowups.** Apply joins, independent blowups, clique
   blowups, and alternating unequal blowups to `P3--P6`, `C4--C7`, stars,
   complete bipartite graphs, and the house/diamond controls.  Bag sizes are
   `1..5`, total order at most 22.  Compare each construction to its balanced
   and one-unit-smoothed variants.
4. **Bounded realization surgery.** For every lane-1--3 graph of order at most
   16 with conjecture residual zero or one, enumerate connected realizations
   reachable by at most three canonical degree-preserving 2-switches, with at
   most 500 nonisomorphic realizations retained per degree sequence.  This
   keeps residue fixed while testing diameter/forest compensation outside the
   earlier Atlas-based switch components.

The deterministic subsampling seed is `6120260813`.  No family may be added
after results are observed.

## Budgets and exactness

- At most 20,000 distinct graphical degree sequences.
- At most 250,000 prefix-comparable sequence pairs.
- At most 10,000 distinct connected graph realizations.
- Every subprocess is capped at 60 seconds.
- Every induced-forest exact solve is capped at 60 seconds; a timed-out graph
  is `INCONCLUSIVE` and cannot support a crossing.
- Havel--Hakimi states, residues, graphicality, diameters, induced-forest
  witnesses, and graph6 edge witnesses are written incrementally.

## Mandatory candidate protocol

Before any candidate status or alert:

1. rerun the current-source and GitHub novelty/status audit;
2. independently recompute graphicality and the entire Havel--Hakimi
   trajectory with a second implementation;
3. for a graph crossing, independently recompute connectivity, diameter, and
   maximum induced forest, and store both a maximum witness and an exact upper
   certificate;
4. replay the database sanity gate with both implementations;
5. append the exact sequence(s), graph6/edge list, transformation provenance,
   and all verification evidence to the ledger.

No issue, PR, release, commit, push, or other public action is authorized.

## Frozen verdicts

- `CONJECTURE_CANDIDATE`: an exact negative WOWII 61 residual surviving every
  mandatory check and the novelty gate.
- `BRIDGE_COUNTERMODEL`: exact graphical descending lists refuting residual
  no-overshoot; explicitly not a conjecture counterexample.
- `HOLD_BOUNDED`: no crossing in the frozen lanes and budgets, with the
  persistent invariant recorded as a theorem signal.
- `INCONCLUSIVE`: a potentially crossing case lacks an exact result within a
  process cap.

