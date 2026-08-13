# Frozen addendum: WOWII 61 realization-cliff surgery

Frozen: 2026-08-13 UTC, before constructing or evaluating any 2-switch path.

## Fixed target and inherited gates

This addendum retains the exact source, reading, status lock, database gate,
exact invariant definitions, candidate protocol, and prohibition on public
action from
`results/expansion/prospective_wowii61_realization_spectrum_contract.md`.
The target residual is still

```text
R61(G) = forest(G) - residue(G) - ceil(diameter(G)/3).
```

The parent trial exhaustively evaluated all 11,117 connected nonisomorphic
graphs of order eight and, under its predeclared definition, identified 36
degree-sequence strata as `REALIZATION_CLIFF`s. This addendum treats those 36
strata as a frozen training set for a local surgery rule. It does not infer a
new order-eight counterexample from a universe already known to have minimum
residual zero.

## Prospective question

Starting from every tight realization in each cliff stratum, can short legal
degree-preserving 2-switch paths systematically move toward a lower WOWII 61
residual by increasing diameter without increasing maximum induced-forest
order?

The purpose is to learn whether the realization cliffs expose a reusable
local move. Any crossing found at order eight would conflict with the parent
exhaustive result and therefore trigger an implementation audit, not a claim.
The useful output is a fully specified transition fingerprint that can later
be applied prospectively to higher-order tight strata.

## Frozen seeds

The seed set is determined mechanically from the already-written exhaustive
order-eight records:

1. group records by exact nonincreasing degree sequence;
2. retain a stratum exactly when its residual range is at least two and its
   minimum residual is zero;
3. within each retained stratum, use every residual-zero realization as a
   seed; and
4. order strata by degree sequence and seeds by graph6.

No seed may be added or removed after surgery results are observed.

## Frozen move and path rule

A legal 2-switch chooses distinct vertices `a,b,c,d` with edges `ab,cd` and
nonedges `ac,bd`, deletes `ab,cd`, and adds `ac,bd`. The alternate orientation
is covered by the enumeration of ordered endpoint choices. A child is retained
only if it is simple, connected, has the seed's exact degree sequence, and is
not isomorphic to an already retained graph at the same or smaller depth.

Every child receives an exact Havel--Hakimi trajectory, residue, all-source BFS
diameter, and maximum induced-forest solve. Relative to its fixed seed, a child
is **direction-eligible** only when

```text
forest(child) <= forest(seed)
```

and either its diameter is larger or its residual is smaller. Direction-
eligible children are ordered by:

1. smaller residual;
2. larger diameter;
3. smaller forest;
4. smaller graph6 encoding.

Paths have maximum depth four. At each depth retain at most 64 pairwise
nonisomorphic direction-eligible children per seed. Enumerate at most 256
legal raw switches per expanded graph, ordered lexicographically by the two
deleted and two inserted edges. If more than 256 exist, the suffix is not
evaluated. A path cannot revisit a graph6 encoding.

## Frozen controls and budgets

Before development surgery, replay the parent's 1,030-graph database sanity
gate with the surgery evaluator. Additionally, for every generated child,
verify the degree multiset before computing the conjecture residual. Any
control mismatch or negative control pauses the trial.

- exactly the 36 frozen order-eight cliff strata;
- every tight seed in those strata;
- depth at most four;
- beam width at most 64 per seed and depth;
- at most 256 raw legal switches per expanded graph;
- at most 25,000 exact child evaluations globally;
- every subprocess and exact solve capped at 60 seconds;
- append after the gate, after every completed stratum, every improved
  residual, every timeout, and the final summary.

The deterministic tie-breaking seed remains `61006120260813`, though the
frozen lexicographic move order is deterministic without randomness.

## Frozen outputs and verdicts

For every retained path endpoint record the seed and endpoint graph6 strings,
the full edge-switch path, degree sequence, Havel--Hakimi trajectory, diameter,
maximum induced-forest order and witness, residue, residual, and exact-solve
time.

- `SURGERY_CROSSING`: negative residual surviving the inherited independent
  candidate protocol.
- `DIRECTIONAL_DROP`: a path lowers residual but remains nonnegative.
- `DIAMETER_LIFT`: a path increases diameter without increasing forest but
  leaves residual unchanged.
- `NO_ELIGIBLE_MOVE`: no direction-eligible child survives from a seed.
- `HOLD_BOUNDED`: every frozen seed and path budget completes without a
  crossing.
- `INCONCLUSIVE`: a relevant exact solve times out.

No issue, PR, release, commit, push, or other public action is authorized.

