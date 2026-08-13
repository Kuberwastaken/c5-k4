# Frozen prospective trial: WOWII 61 sparse high-feedback bead bridges

Frozen: 2026-08-13 UTC, before certifying a bead coordinate or constructing a
development graph.

## Target and inherited gate

The sole target remains current DeepMind WOWII 61 at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, source SHA-256
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The source and recovered WOWII record classify it as open. Inherit the exact
1,030-control gate and candidate protocol from the realization-spectrum
contract. No public action is authorized.

## Fixed bases

Use exactly the three protocol-exact order-twelve neutral endpoints:

```text
KniA@A?_A?G?
K~Q?PA?_A?G?
K~IA?Q?_A?G?
```

Before development, each must recompute to degree sequence
`[6,6,4,3,2,1,1,1,1,1,1,1]`, residue eight, diameter four, exact maximum
induced forest ten, and residual zero.

## Frozen rooted sparse-bead menu

The menu contains exactly six rooted graphs:

| name | construction | root | predicted order | predicted root eccentricity | predicted exact forest | feedback loss |
|---|---|---:|---:|---:|---:|---:|
| `Prism3` | triangular prism | vertex 0 | 6 | 2 | 4 | 2 |
| `K3,3` | complete bipartite graph | vertex 0 | 6 | 2 | 4 | 2 |
| `Cube3` | 3-cube | vertex 0 | 8 | 3 | 6 | 2 |
| `Petersen` | Petersen graph | vertex 0 | 10 | 2 | 7 | 3 |
| `PetersenSub` | subdivide Petersen edge `{0,1}` once | new subdivision vertex 10 | 11 | 3 | 8 | 3 |
| `Heawood` | Heawood graph | vertex 0 | 14 | 3 | 10 | 4 |

These predictions are part of the frozen trial. Before any attachment, direct
decreasing-cardinality subset enumeration must certify each exact forest
number and witness, and all-source BFS must certify its root eccentricity. A
single mismatch makes the trial `INCONCLUSIVE`; the menu is not repaired or
replaced.

All bead degrees are at most four before bridge attachment. The menu spans
feedback losses two, three, and four, contrasting with cycle/theta beads whose
loss was only one and clique beads whose degree geometry collapsed residue.

## Frozen transformation

For every unordered diametral pair `{u,v}` in every base and every ordered
pair `(A,B)` from the six-bead menu:

1. take disjoint labelled copies of `A` and `B`;
2. add the bridge from `u` to the root of `A` and the bridge from `v` to the
   root of `B`; and
3. add no other inter-block edge.

The bases have frozen diametral-pair counts 3, 4, and 6. The expected family is

```text
(3 + 4 + 6) * 6^2 = 468
```

labelled constructions. Pause if recomputation disagrees. This family is
distinct from degree-preserving switches, ordinary 2-lifts, clique beads, and
cycle/theta beads.

## Preregistered coordinates

For bead `X`, let `n_X`, `rho_X`, and `f_X` denote its certified order, root
eccentricity, and maximum induced-forest order. Because the attachments are
bridges, cycles cannot cross the base/bead blocks. Every transformed graph `T`
must satisfy exactly

```text
forest(T)   = 10 + f_A + f_B,
diameter(T) = 6 + rho_A + rho_B.
```

Thus all frozen constructions have diameter at least ten, raising
`ceil(diameter/3)` from two to at least four. The exact forest witness is the
stored ten-vertex base witness united with certified maximum forests of both
beads. The upper certificate is block-additive.

For each graph compute the complete Havel--Hakimi trajectory and record

```text
required_residue_to_cross
  = forest(T) - ceil(diameter(T)/3) + 1.
```

A candidate exists exactly when the measured residue reaches this threshold.
No residue behavior is assumed in advance.

## Exactness, caps, and logging

Before development:

1. replay all 1,030 controls by direct exact induced-forest search;
2. certify all six bead coordinate rows exactly; and
3. recompute every base and the total family size.

For every transformed graph:

- verify simplicity, connectivity, exact bead blocks, and exactly two joining
  bridges;
- record graph6 and the full labelled edge list;
- recompute degree sequence, full Havel--Hakimi trajectory, and residue;
- compute diameter with all-source BFS and match the coordinate prediction;
- record the explicit block-union forest witness and exact upper certificate;
- record crossing threshold, residual, and timings; and
- replay every candidate with an independently written HH/BFS/block verifier.

Frozen resource bounds:

- exactly 468 labelled constructions;
- at most 500 exact development evaluations;
- every subprocess and exact solve capped at 60 seconds;
- one subprocess per base;
- append the database gate, bead gate, every base summary, every improved
  residual, mismatch, timeout, candidate, verifier result, and final verdict.

## Frozen verdicts

- `SPARSE_BEAD_CROSSING`: a negative residual surviving independent replay.
- `NEAR_THRESHOLD`: minimum residual zero or one without a crossing.
- `HOLD_BOUNDED`: all frozen graphs complete with minimum residual at least two
  and no timeout.
- `INCONCLUSIVE`: a database, bead, base, family-count, coordinate, exactness,
  candidate-replay, process, or budget check fails.

No issue, PR, release, commit, push, or other public action is authorized.

