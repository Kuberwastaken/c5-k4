# Frozen prospective trial: WOWII 61 serial cube chains

Frozen: 2026-08-13 UTC, before constructing or evaluating any development
graph.

## Target and source/status lock

The sole target is current DeepMind WOWII 61 at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, source SHA-256
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The source and recovered WOWII record classify it as open. Inherit the exact
1,030-control database gate and full candidate protocol from the frozen
realization-spectrum contract. No release or other public action is authorized.

## Certified coordinate carried forward, not altered

The independently audited v0.50 gate established for the canonical binary
3-cube `Q3`:

```text
order                  8
root                   0
antipodal port          7
distance(root,port)     3
root eccentricity       3
maximum induced forest 5
feedback loss           3
```

The fixed forest witness is `{0,1,2,4,5}`. All 28 six-vertex subsets contain a
cycle, proving the exact upper bound five. This new trial uses that corrected
coordinate without changing any v0.50 artifact.

## Fixed bases

Use exactly the three protocol-exact order-twelve neutral endpoints:

```text
KniA@A?_A?G?
K~Q?PA?_A?G?
K~IA?Q?_A?G?
```

Each must recompute to degree sequence `[6,6,4,3,2,1,1,1,1,1,1,1]`, residue
eight, diameter four, exact maximum induced forest ten, and residual zero.

## Frozen serial construction

Let `C_t` be a chain of `t` disjoint canonical binary cubes, for
`1 <= t <= 8`. Within cube `i`, call vertices zero and seven its input and
output ports. Add one bridge from output seven of cube `i` to input zero of
cube `i+1`; add no other inter-cube edge.

For every unordered diametral pair `{u,v}` in every base and every ordered
`(a,b)` in `[1,8]^2`:

1. attach the input port of `C_a` to `u` by one bridge;
2. attach the input port of a disjoint `C_b` to `v` by one bridge; and
3. add no other inter-block edges.

The bases have frozen diametral-pair counts 3, 4, and 6. Therefore the exact
finite family is

```text
(3 + 4 + 6) * 8^2 = 832
```

labelled graphs. Pause on any family-count mismatch. This operation is
distinct from isolated bead pairs: it tests repeated copies of the single
corrected high-feedback block along a serial distance direction.

## Preregistered exact coordinates

Every inter-block edge is a bridge. Each cube contributes exactly five
vertices to a maximum induced forest, and bridge unions of forests remain
forests. Therefore for `T(base,u,v,a,b)`:

```text
forest(T) = 10 + 5(a+b).
```

From a base attachment to the far output port of a `t`-cube chain there is
one initial bridge, `t` antipodal three-edge cube traversals, and `t-1`
inter-cube bridges, hence distance `4t`. Since `{u,v}` is diametral in the
base:

```text
diameter(T) = 4a + 4 + 4b = 4(a+b+1).
```

These formulas are frozen and must be checked on every graph. The explicit
forest witness is the ten-vertex base witness plus the translated five-vertex
cube witness in every block. The upper certificate is block-additive.

For each graph recompute the complete Havel--Hakimi trajectory and record

```text
required_residue_to_cross
  = forest(T) - ceil(diameter(T)/3) + 1.
```

The empirical question is whether serial copies of `Q3`, whose feedback loss
is one larger than frozen v0.50 originally assumed, grow residue quickly
enough to meet this threshold.

## Gates, exactness, and budgets

Before development:

1. replay all 1,030 controls with direct exact induced-forest search;
2. independently re-certify the canonical cube coordinate, including all 28
   six-vertex subsets;
3. recompute every base; and
4. require the family count 832.

For every development graph:

- verify simplicity, connectivity, every canonical cube block, and all joining
  bridges;
- record graph6 and the full labelled edge list;
- record degree sequence, full Havel--Hakimi trajectory, and residue;
- compute diameter by all-source BFS and match `4(a+b+1)`;
- record the explicit forest witness and exact block upper certificate;
- record crossing threshold, residual, and timings; and
- independently replay every negative candidate.

Frozen limits:

- exactly 832 labelled graphs;
- at most 900 exact development evaluations;
- one subprocess per base;
- every subprocess and exact solve capped at 60 seconds;
- incremental JSONL after the gate, cube gate, every base, improved residual,
  mismatch, timeout, candidate, independent replay, and final verdict.

## Strict verdict taxonomy

- `CUBE_CHAIN_CROSSING`: a negative residual surviving independent replay.
- `NEAR_THRESHOLD`: minimum residual zero or one without a crossing.
- `HOLD_BOUNDED`: all 832 graphs complete with minimum residual at least two
  and no timeout.
- `INCONCLUSIVE`: any gate, family count, coordinate, exactness, candidate
  replay, process, or budget check fails.

No issue, PR, release, commit, push, or other public action is authorized.

