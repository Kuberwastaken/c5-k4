# Method v0.8: WOWII 19 finite maximum and eccentricity floor

Date: **2026-08-13 UTC**

Status: **complete local no-`sorry` proof of the finite-maximum and
non-self-centered arithmetic rungs; not a proof of WOWII 19**

Local artifact:

```text
lean/GraphConjecture19Eccentricity.lean
```

No formal-conjectures source file was edited, and the upstream WOWII 19 and
WOWII 13 theorems (whose proofs contain `sorry`) are not invoked.

## Finite `sSup` normalization

The local-neighborhood invariant has finite nonempty range.  The file defines
its ordinary `Finset.max'` as `maxIndepNeighbors` and proves

```lean
lemma sSup_range_indepNeighbors_eq_maxIndepNeighbors [Nonempty V]
    (G : SimpleGraph V) :
    sSup (Set.range (indepNeighbors G)) = maxIndepNeighbors G
```

The proof identifies `Set.range (indepNeighbors G)` with the coercion of
`Finset.univ.image (indepNeighbors G)` and applies
`Finset.Nonempty.csSup_eq_max'`.  It also retains both useful attainment
forms:

```lean
∃ v, indepNeighbors G v = sSup (Set.range (indepNeighbors G))

∃ v, (indepNeighborsCard G v : ℝ) =
  sSup (Set.range (indepNeighbors G))
```

Thus the real supremum in the conjecture is not merely bounded: it is exactly
the cast of an attained natural number.

## Non-self-centered average bound

For a connected finite graph, `connected_iff_ediam_ne_top` makes the extended
diameter finite.  Consequently `ENat.toNat_le_toNat` transfers
`eccent_le_ediam` to

```lean
(G.eccent v).toNat ≤ G.diam.
```

If one vertex satisfies `G.eccent v < G.ediam`, rewriting both finite `ENat`
values as casts proves the strict natural inequality at that vertex.  Then
`Finset.sum_lt_sum` gives a strict sum inequality, and division by the positive
vertex count gives

```lean
lemma average_eccentricity_lt_diam_of_exists_lt_ediam ... :
    (∑ v : V, ((G.eccent v).toNat : ℝ)) / (Fintype.card V : ℝ) <
      (G.diam : ℝ)
```

Using the current `Int.floor_lt` API yields the requested integral endpoint:

```lean
lemma floor_average_eccentricity_le_diam_sub_one ... :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
        (Fintype.card V : ℝ)⌋ ≤ (G.diam : ℤ) - 1
```

The hypothesis `∃ v, G.eccent v < G.ediam` is exactly the extended-distance
form of “not every vertex has diameter eccentricity”; no radius theorem or
upstream conjecture is required.

## Exact floor assembly

Since the attained supremum is a natural-number cast,
`Int.floor_add_natCast` gives the lossless identity

```lean
∃ v,
  ⌊x + sSup (Set.range (indepNeighbors G))⌋ =
    ⌊x⌋ + (indepNeighborsCard G v : ℤ).
```

Combining this with the non-self-centered floor bound produces the strongest
direct assembly needed at this rung:

```lean
lemma exists_floor_average_add_sSup_le_diam_add_indepNeighborsCard_sub_one
    (G : SimpleGraph V) [Nonempty V] (hconn : G.Connected)
    (hnotcentered : ∃ v : V, G.eccent v < G.ediam) :
    ∃ v : V,
      ⌊average-expression + sSup (Set.range (indepNeighbors G))⌋ ≤
        (G.diam : ℤ) + (indepNeighborsCard G v : ℤ) - 1
```

Here `average-expression` is expanded in the actual Lean statement exactly as
it appears upstream.  There is no approximation or independent choice of the
local maximum hidden in this assembly.

## Verification

The warning-as-error build was run from the formal-conjectures Lake project,
with the subprocess externally capped at 60 seconds:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture19Eccentricity.lean
```

Result: **exit 0** in approximately 6.2 seconds with no output.  The source
contains no `sorry`, `admit`, or custom `axiom`.

## Remaining boundary

No `ENat`, finite-supremum, real-division, or floor API lemma remains missing:
all requested arithmetic and metric bridges are exact and compiled.

What remains is graph-theoretic.  The next proof stage must supply a
no-`sorry` induced-bipartite lower bound strong enough to dominate

```text
diam(G) + max_v indepNeighborsCard(G,v) - 1
```

in the non-self-centered branch, and the corresponding

```text
diam(G) + max_v indepNeighborsCard(G,v)
```

in the self-centered branch.  The induced-star theorem from method v0.7 only
provides this after constructing a sufficiently large independent set outside
the chosen maximum-local-neighborhood vertex.  Establishing that construction,
or replacing it with a more flexible explicit bipartite witness, is the exact
remaining combinatorial lemma; it is not an arithmetic normalization issue.

