# Frozen prospective trial: WOWII 61 higher-order neutral corridor

Frozen: 2026-08-13 UTC, before evaluating any development switch.

## Target and inherited source gate

The sole target remains current DeepMind WOWII 61 at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, source SHA-256
`54620e7b70a9a98eaaf7ce10154f533046b9f6d36fa276c8923c1a7301a7e091`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The recovered WOWII record and current formal-conjectures source classify the
statement as open. The source reading is unambiguous. The database-sanity and
candidate protocols of
`results/expansion/prospective_wowii61_realization_spectrum_contract.md` are
inherited without relaxation. No public action is authorized.

## Fixed seed

The parent trial prospectively found a new order-twelve realization cliff at
frozen manifest index 623, with degree sequence

```text
[6,6,4,3,2,1,1,1,1,1,1,1].
```

This contract fixes its unique sampled tight realization as the only seed:

```text
graph6       K^qA@A?_A?G?
residue      8
diameter     4
ceil(D/3)    2
forest       10
residual     0
```

Its stored induced-forest witness is
`{0,1,2,5,6,7,8,9,10,11}`. Before development, every seed invariant and the
complete Havel--Hakimi trajectory must be recomputed exactly.

## Distinction from the completed order-eight surgery lane

The order-eight trial required every retained first switch to improve diameter
or residual immediately; all 87 seeds were local minima under that rule. This
higher-order trial instead freezes a **neutral-corridor** operation. It may
retain several degree-preserving switches with unchanged forest and diameter
before a later switch raises the diameter ceiling.

The prospective target is a path from the fixed seed to a graph satisfying

```text
forest <= 10  and  diameter >= 7.
```

Because the degree sequence fixes residue at eight, such an endpoint has
`forest - 8 - ceil(diameter/3) <= -1` and is a candidate crossing. A forest
drop at smaller diameter is also recorded if it makes the residual negative.

## Frozen move, corridor, and ranking

A legal 2-switch selects distinct vertices `a,b,c,d`, deletes existing edges
`ab,cd`, and inserts nonedges `ac,bd`; the alternate orientation is enumerated
separately. Children must remain finite, simple, connected, and have exactly
the seed degree sequence.

A nonnegative child is corridor-eligible exactly when

```text
forest(child) <= 10  and  diameter(child) >= 4.
```

Thus no step may compensate a diameter change by increasing the maximum
induced forest above the seed value, but residual-zero steps may form a neutral
corridor. Negative children are retained regardless of ranking and trigger the
candidate protocol.

At each depth, pairwise nonisomorphic eligible children are ranked by:

1. negative residual first, then smaller residual;
2. larger `ceil(diameter/3)`;
3. larger diameter;
4. smaller forest;
5. lexicographically smaller graph6.

The global seen set rejects graphs isomorphic to any graph retained at a
smaller or equal depth. Paths retain the exact deleted/inserted edge pairs.

## Frozen bounds and logging

- maximum path depth: 8;
- beam width: 32 pairwise nonisomorphic eligible children per depth;
- at most 128 lexicographically ordered raw legal connected switches per
  expanded graph;
- at most 8,000 exact child evaluations;
- every subprocess and induced-forest solve capped at 60 seconds;
- append the database gate before development;
- append every completed depth, improved residual, timeout, candidate, and
  final verdict to the ledger;
- record every retained endpoint with graph6, edge list, full path, degree
  sequence, Havel--Hakimi trajectory, residue, diameter, exact forest witness,
  residual, and solve time.

Induced forests are solved by decreasing-cardinality exhaustive subset search
with explicit acyclicity tests. A returned forest therefore supplies both a
witness and an exact upper certificate: all larger subsets were rejected.

## Frozen verdicts

- `CORRIDOR_CROSSING`: a negative endpoint surviving independent verification.
- `CEILING_APPROACH`: a retained endpoint reaches diameter five or six without
  forest compensation but does not cross.
- `NEUTRAL_CORRIDOR`: eligible depth-two-or-greater endpoints exist without a
  crossing.
- `HOLD_BOUNDED`: the complete frozen beam/budget finishes without a crossing.
- `INCONCLUSIVE`: a relevant exact solve or process times out.

No issue, PR, release, commit, push, or other public action is authorized.

