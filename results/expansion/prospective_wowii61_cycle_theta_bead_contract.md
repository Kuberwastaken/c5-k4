# Frozen prospective trial: WOWII 61 cycle/theta bead bridges

Frozen: 2026-08-13 UTC, before constructing or evaluating any development
graph.

## Target and inherited gate

The sole target remains current DeepMind WOWII 61 at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, source SHA-256
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The source and recovered WOWII record classify it as open. Inherit the exact
1,030-control database gate and candidate protocol from
`results/expansion/prospective_wowii61_realization_spectrum_contract.md`.
No public action is authorized.

## Fixed bases

Use exactly the three protocol-exact order-twelve neutral endpoints, ordered
by depth and graph6:

```text
KniA@A?_A?G?
K~Q?PA?_A?G?
K~IA?Q?_A?G?
```

Each must independently recompute to degree sequence
`[6,6,4,3,2,1,1,1,1,1,1,1]`, residue eight, diameter four, exact maximum
induced forest ten, and residual zero before development.

## Frozen rooted bead menu

Every bead has a distinguished root `s`.

1. **Cycle beads:** `C_l`, rooted at vertex zero, for every `3 <= l <= 12`.
   Their order is `l`, root eccentricity is `floor(l/2)`, and their exact
   maximum induced forest is `l-1`.
2. **Theta beads:** `Theta(p,L)`, for `p in {3,4}` and
   `L in {2,3,4,5}`. This is the union of `p` internally vertex-disjoint
   `s--t` paths, each of exactly `L` edges, with no other edges. Its order is
   `2+p(L-1)`, root eccentricity is `L`, and deleting `s` leaves a forest of
   order `|Theta|-1`. Since the bead contains a cycle, its exact maximum
   induced forest is `|Theta|-1`.

There are exactly 18 rooted bead types. Their maximum degree is at most four;
all nonterminal theta vertices and all cycle vertices have degree two before
attachment. This is the preregistered low-degree contrast with the failed
clique beads.

## Frozen transformation

For every unordered diametral pair `{u,v}` in each base and every ordered pair
of bead types `(A,B)` from the 18-type menu:

1. take disjoint labelled copies of `A` and `B`;
2. add the bridge from `u` to the root of `A` and the bridge from `v` to the
   root of `B`; and
3. add no other inter-block edge.

Evaluate every labelled construction. The expected mechanical family size is

```text
(3 + 4 + 6) * 18^2 = 4,212,
```

where `3,4,6` are the already recorded diametral-pair counts of the fixed
bases. Pause rather than evaluate if recomputation disagrees with this count.

This operation changes the degree sequence and is distinct from
degree-preserving switches, clique beads, and ordinary 2-lifts.

## Preregistered coordinates

For a rooted bead `X`, let `n_X` be its order and `rho_X` its root
eccentricity. The two attachments are bridges, so every cycle lies inside one
of the three blocks. Therefore the transformed graph `T` must satisfy exactly

```text
forest(T)   = 10 + (n_A - 1) + (n_B - 1)
diameter(T) = 4 + (rho_A + 1) + (rho_B + 1)
            = 6 + rho_A + rho_B.
```

The forest witness is the stored ten-vertex base witness together with every
bead vertex except one cycle vertex in each bead. The upper certificate is
block-additive: base at most ten, and each cyclic bead at most its order minus
one.

All bead pairs have diameter at least eight and therefore raise
`ceil(diameter/3)` above the base value. The trial's empirical question is
whether the many degree-two vertices preserve or raise Havel--Hakimi residue,
unlike clique beads. The residue is not assumed; it is recomputed from the full
trajectory.

For each graph record the coordinate threshold

```text
required_residue_to_cross
  = forest(T) - ceil(diameter(T)/3) + 1.
```

A candidate exists exactly when `residue(T)` meets or exceeds this threshold.

## Exactness, caps, and logging

Before development, replay the 1,030 controls by direct exact induced-forest
search. For every transformed graph:

1. verify simplicity, connectivity, bead construction, and exactly two joining
   bridges;
2. recompute degree sequence, full Havel--Hakimi trajectory, and residue;
3. compute diameter by all-source BFS and match the coordinate prediction;
4. record the explicit induced-forest witness;
5. verify the blockwise exact forest upper certificate;
6. record graph6, labelled edge list, base and attachment coordinates, bead
   specifications, invariants, residual, and timings; and
7. replay every candidate independently with separately written HH, BFS,
   witness, and block-certificate code.

Frozen resource bounds:

- exactly 4,212 labelled constructions;
- at most 5,000 exact invariant evaluations;
- every subprocess and exact solve capped at 60 seconds;
- one subprocess per base;
- append the gate before development, each base summary, every improved
  residual, mismatch, timeout, candidate, independent replay, and final verdict.

The block proof replaces exponential subset enumeration on large transformed
graphs but supplies an exact upper certificate, not a heuristic estimate.

## Frozen verdicts

- `CYCLE_THETA_CROSSING`: a negative residual surviving independent replay.
- `RESIDUE_PRESERVED`: a construction has residue at least eight but does not
  cross.
- `HOLD_BOUNDED`: every frozen construction completes with nonnegative
  residual and no timeout.
- `INCONCLUSIVE`: a gate, family count, coordinate, exactness, candidate replay,
  process, or budget fails.

No issue, PR, release, commit, push, or other public action is authorized.

