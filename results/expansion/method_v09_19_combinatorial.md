# Method v0.9 proof extraction: WOWII 19 combinatorial branch

Date: **2026-08-13 UTC**

Status: **self-centered diameter-two branch proved in warning-clean no-`sorry` Lean; full WOWII 19 remains open**

## Scope

The current `formal-conjectures` statement is
`FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean` at upstream
commit `9a1636c4030039f70cf78b866c216d8b6c5f35b0`:

```lean
theorem conjecture19 (G : SimpleGraph α) [Nontrivial α] (h_conn : G.Connected) :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
        (Fintype.card α : ℝ) +
      sSup (Set.range (indepNeighbors G))⌋ ≤ b G
```

This extraction adds no candidate graph, changes no invariant reading, and
makes no claim about any corpus outside the WOWII declarations covered by
`formal-conjectures`.

## New proved branch

The new certificate is
[`lean/GraphConjecture19Combinatorial.lean`](../../lean/GraphConjecture19Combinatorial.lean).
It proves the exact upstream inequality under

```text
G connected,
radius(G) = diameter(G),
diameter(G) = 2.
```

The argument is structural and exact:

1. self-centeredness identifies every eccentricity with the diameter, hence
   the average eccentricity in the upstream expression is exactly `2`;
2. every vertex has a distinct non-neighbor (otherwise its eccentricity would
   be at most one);
3. choose a vertex attaining
   `sSup (Set.range (indepNeighbors G))`;
4. its non-neighbor is a singleton independent set outside the closed
   neighborhood;
5. the already formalized induced-star construction gives an induced
   bipartite subgraph of order `lambda_max + 2`.

Thus the lower bound produced by the witness is exactly the floored expression,
with no rounding loss.

The principal endpoint is:

```lean
theorem conjecture19_of_radius_eq_ediam_diam_eq_two
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hself : G.radius = G.ediam)
    (hdiam : G.diam = 2) :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
          (Fintype.card V : ℝ) +
        sSup (Set.range (indepNeighbors G))⌋ ≤ b G
```

Reusable intermediate endpoints prove:

- every vertex has a non-neighbor in this branch;
- one non-neighbor yields `indepNeighborsCard G v + 2 ≤ b G`;
- maximization yields `2 + sSup (range (indepNeighbors G)) ≤ b G`;
- the eccentricity average is exactly two.

This branch includes the original carrier `C₅[K₄]` and the dense
diameter-two equality geometry that motivated the proof extraction.  The proof
does not rely on any graph-specific computation.

## Trust and compile audit

The file imports the two preceding local #19 proof modules rather than the
upstream conjecture declaration:

- `GraphConjecture19StarBound.lean` for the induced-bipartite witness;
- `GraphConjecture19Eccentricity.lean` for finite `sSup` attainment.

All three were compiled in dependency order against the current
`formal-conjectures` environment, with each subprocess capped below 60 seconds:

```text
lake env lean -R .../c5-k4/lean -DwarningAsError=true \
  -o .../GraphConjecture19StarBound.olean .../GraphConjecture19StarBound.lean
lake env lean -R .../c5-k4/lean -DwarningAsError=true \
  -o .../GraphConjecture19Eccentricity.olean .../GraphConjecture19Eccentricity.lean
lake env lean -R .../c5-k4/lean -DwarningAsError=true \
  .../GraphConjecture19Combinatorial.lean
```

Final result: **exit 0**, with warnings treated as errors.  The new source
contains no `sorry`, `admit`, custom `axiom`, or embedded `#print`.  The endpoint
axiom audit reports only the standard Lean foundations:

```text
[propext, Classical.choice, Quot.sound]
```

In particular it does not inherit `sorryAx` from upstream WOWII 13 or 19.

## Exact remaining boundary

This is a proper theorem branch, not a full proof of WOWII 19.

- In the **non-self-centered** branch, the preceding eccentricity module proves
  the necessary integral loss
  `floor(average eccentricity) ≤ diameter - 1`.  Completion still needs a
  no-`sorry` proof of the source WOWII 13 baseline
  `b ≥ diameter + lambda_max - 1`; its current upstream declaration contains
  `sorry` and is therefore not imported.
- In the **self-centered diameter at least three** branch, the unresolved
  graph-theoretic obligation remains an outside independent-set lower bound
  strong enough to contribute `diameter - 1` vertices beyond the center and
  its independent neighborhood.

The diameter-two result removes the entire carrier-scale self-centered branch
from that second obstruction.  Future work should therefore concentrate on
either a no-`sorry` proof of WOWII 13 or the genuinely higher-diameter
self-centered case.
