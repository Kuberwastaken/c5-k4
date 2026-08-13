# Method v0.7 proof-extraction scout: WOWII 19

Date: **2026-08-13 UTC**

Status: **source-faithful lemma ladder; no proof of WOWII 19 claimed**

This report is a proof-extraction audit only.  It generated no candidate graph,
searched no new family, and changes no statement or invariant.  The only
computational check below reuses the frozen connected Graph Atlas and named
controls as a countermodel guard for proposed intermediate lemmas.

## Exact source and formal statement

The local WOWII transcription, `data/wowii-conjectures.json` row 19, records

```text
b(G) >= floor(average_v ecc_G(v) + max_v lambda_G(v)),
```

for a finite simple connected graph.  It is source-marked open, dated 3 July
2003.  The source note dated 22 June 2005 says that the conjecture follows from
WOWII 13 when the average eccentricity is at most `diameter - 1`.

The current formal-conjectures module at local commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0` is
`FormalConjectures/WrittenOnTheWallII/GraphConjecture19.lean`.  Its exact target
is

```lean
theorem conjecture19 (G : SimpleGraph α) [Nontrivial α] (h_conn : G.Connected) :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) / (Fintype.card α : ℝ) +
      sSup (Set.range (indepNeighbors G))⌋ ≤ b G
```

This agrees with the recovered glossary:

- `b(G)` is the maximum order of an induced bipartite subgraph;
- `ecc(v)=max_u dist(v,u)`;
- `indepNeighbors G v` is the real cast of the independence number of
  `G[N(v)]`; and
- the average is over all vertex eccentricities.

There is no set-eccentricity ambiguity in this statement.  The Lean theorem
uses `sSup (Set.range (indepNeighbors G))`, whereas neighboring files often
use the maximum of the finite image of `indepNeighborsCard`; a normalization
bridge is therefore required before the graph argument.

## Existing wall and proved baseline

The complete prior sweep found equality on the carrier:

```text
b=4, average eccentricity=2, lambda_max=2.
```

The later upstream-selection ledger records residual zero on 17
nonisomorphic complete/mixed blob controls.  These are wall data, not new
evidence in this report.

WOWII 13 is source-marked solved and is already stated in
`GraphConjecture13.lean` as

```text
b(G) >= diameter(G) + lambda_max(G) - 1.
```

Its current Lean declaration still ends in `sorry`.  It is a valid
mathematical baseline for the lemma ladder, but an honest no-`sorry` proof of
19 may not merely invoke that declaration: either a no-`sorry` proof of the
13 bound must be supplied locally, or a separately audited formal proof must
be imported.  Otherwise `#print axioms` for the resulting theorem would retain
`sorryAx` through `conjecture13`.

## Core induced-bipartite lower bound

Fix a vertex `v`.  Let `A` be an independent subset of `N(v)`, and let `I` be
an independent set outside the closed neighborhood `N[v]`.  Then

```text
A | ({v} union I)
```

is a bipartition of the graph induced by `A union {v} union I`: `A` is
independent, `{v} union I` is independent, and arbitrary `A`--`I` edges cross
the displayed bipartition.  Taking both sets maximum gives the exact reusable
bound

```text
b(G) >= lambda(v) + 1 + alpha(G-N[v]).                 (Star)
```

Here `G-N[v]` means the graph induced by vertices neither equal nor adjacent
to `v`.  This is the structural lower bound already recorded in
`results/family_forest.md`; the present report separates it into Lean-sized
rungs.

The following signatures use only current Mathlib/formal-conjectures APIs.
They are proposed theorem interfaces, not declarations added by this report.

```lean
lemma card_le_largestInducedBipartiteSubgraphSize_of_induce_isBipartite
    (G : SimpleGraph α) (s : Finset α)
    (hs : (G.induce (s : Set α)).IsBipartite) :
    s.card ≤ G.largestInducedBipartiteSubgraphSize

lemma induce_insert_union_isBipartite_of_indep
    (G : SimpleGraph α) (v : α) (A I : Finset α)
    (hA : G.IsIndepSet (A : Set α))
    (hAN : (A : Set α) ⊆ G.neighborSet v)
    (hI : G.IsIndepSet (I : Set α))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    (G.induce ((insert v (A ∪ I) : Finset α) : Set α)).IsBipartite

lemma exists_local_indep_witness (G : SimpleGraph α) (v : α) :
    ∃ A : Finset α,
      G.IsIndepSet (A : Set α) ∧
      A ⊆ G.neighborFinset v ∧
      A.card = indepNeighborsCard G v

lemma local_indep_add_outside_indep_add_one_le_b
    (G : SimpleGraph α) (v : α) (I : Finset α)
    (hI : G.IsIndepSet (I : Set α))
    (hIout : I ⊆ Finset.univ \ insert v (G.neighborFinset v)) :
    ((indepNeighborsCard G v + I.card + 1 : ℕ) : ℝ) ≤ b G
```

The first lemma is a direct bounded-`sSup` insertion into the definition of
`largestInducedBipartiteSubgraphSize`.  The second can use the existing
`induce_isBipartite_iff_exists_coloring`, coloring `A` by `0` and
`{v} union I` by `1`.  The third follows from
`exists_isNIndepSet_indepNum` in the induced neighborhood and mapping subtype
vertices back to `α`.  The fourth assembles the first three plus disjoint
Finset cardinality identities.

**First formalizable rung:**
`induce_insert_union_isBipartite_of_indep`.  It is representation-local,
requires no metric argument and no extremal-choice plumbing, and immediately
exposes whether the current induced-subgraph/coloring APIs suffice.  The
`card_le_...` insertion is even smaller, but it is generic infrastructure;
the coloring lemma is the first graph-specific rung of the proof.

## Eccentricity dichotomy

Let `d=diam(G)`, `e_avg` be average eccentricity, and `lambda` be maximum
local independence.  Every eccentricity is an integer at most `d`.
Consequently:

1. if some vertex has eccentricity strictly below `d`, then
   `floor(e_avg) <= d-1`;
2. otherwise every vertex has eccentricity `d`, equivalently
   `radius(G)=ediam(G)`, and `e_avg=d`.

Because `lambda` is an integer,
`floor(e_avg+lambda)=floor(e_avg)+lambda`.  In the first branch, the solved
WOWII 13 bound gives

```text
b >= d+lambda-1 >= floor(e_avg)+lambda.
```

Thus the only genuinely new mathematical branch is the self-centered case.
The arithmetic/metric bridges can be stated with the current target syntax as

```lean
lemma floor_average_eccentricity_le_diam_sub_one_of_exists_lt
    (G : SimpleGraph α) (hconn : G.Connected)
    (hnotself : ∃ v : α, G.eccent v < G.ediam) :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
        (Fintype.card α : ℝ)⌋ ≤ (G.diam : ℤ) - 1

lemma all_eccent_eq_ediam_of_not_exists_lt
    (G : SimpleGraph α)
    (h : ¬ ∃ v : α, G.eccent v < G.ediam) :
    ∀ v : α, G.eccent v = G.ediam

lemma floor_add_nat_cast (x : ℝ) (n : ℕ) :
    ⌊x + n⌋ = ⌊x⌋ + n
```

Mathlib already provides `eccent_le_ediam` and
`radius_eq_ediam_iff`; formal-conjectures provides
`averageEccentricity`.  The first displayed lemma is finite-sum arithmetic:
one summand is at most `d-1`, all others are at most `d`, so the average is
strictly below `d` and its floor is at most `d-1`.

## Exact hard rung in the self-centered branch

The strongest source-faithful completion exposed by the current ledgers is:

```text
Self-centered outside-set lemma.
If G is finite, connected, and radius(G)=diameter(G), then for every v,
G-N[v] has an independent set of order at least diameter(G)-1.
```

In current APIs the intended theorem signature is

```lean
lemma exists_large_indep_outside_closedNeighborhood_of_radius_eq_ediam
    (G : SimpleGraph α) [DecidableRel G.Adj]
    (hconn : G.Connected) (hself : G.radius = G.ediam) (v : α) :
    ∃ I : Finset α,
      G.IsIndepSet (I : Set α) ∧
      I ⊆ Finset.univ \ insert v (G.neighborFinset v) ∧
      G.diam - 1 ≤ I.card
```

Combined with `(Star)` at a vertex attaining `lambda_max`, it gives

```text
b >= lambda + 1 + (d-1) = lambda+d
  = floor(e_avg+lambda),
```

which closes the self-centered branch exactly.  This lemma is the first
unproved mathematical obstruction, not the first Lean engineering task.  No
general proof is claimed here.  A proof must construct the independent set;
merely taking alternate vertices of one diametral geodesic gives only about
half of `d-1` and is insufficient.

The finite maximum and source-syntax normalization required for final assembly
can be isolated as

```lean
lemma exists_vertex_indepNeighbors_eq_sSup (G : SimpleGraph α) :
    ∃ v : α, indepNeighbors G v = sSup (Set.range (indepNeighbors G))

lemma sSup_range_indepNeighbors_eq_finset_max (G : SimpleGraph α) :
    sSup (Set.range (indepNeighbors G)) =
      (((Finset.univ.image (indepNeighborsCard G)).max'
        (by simp) : ℕ) : ℝ)
```

The complete ladder is therefore:

1. normalize the average and finite `sSup` in `conjecture19`;
2. prove the coloring lemma and the induced-bipartite `sSup` insertion;
3. extract maximum independent witnesses in `N(v)` and outside `N[v]`, proving
   `(Star)`;
4. supply a no-`sorry` proof of the solved WOWII 13 baseline;
5. formalize the non-self-centered eccentricity-average floor bound;
6. prove the self-centered outside-set lemma;
7. split on self-centeredness and assemble the exact source theorem.

## Frozen-control countermodel audit

A single read-only Python check, externally capped at 60 seconds, used only
the already-fixed controls: all 995 connected Graph Atlas graphs of orders
2--7, `P2`--`P12`, `C2`--`C12`, Petersen, `K3,3`, and `K7`, deduplicated by
graph6 to 1,012 graphs.  It computed eccentricity, local independence, and
independence in `G-N[v]` exactly by subset enumeration.

Results:

- 267 controls were self-centered;
- all 267 satisfied the outside-set lemma for **every** vertex;
- all 1,012 satisfied the combined numerical relation
  `floor(e_avg) <= max(d-1, 1+alpha(G-N[v]))` when `v` ranges over
  `lambda_max` achievers;
- there was no timeout.

This is a countermodel guard only and is not evidence substituted for proof.
It also falsifies two tempting stronger shortcuts on frozen controls:

1. **False without self-centeredness:** a `lambda_max` vertex always has
   `floor(e_avg) <= 1+alpha(G-N[v])`.  The path `P6` has `e_avg=4` and
   `lambda_max=2`, but every useful internal achiever has outside independence
   only two, giving `4 > 3`.  This is precisely why the WOWII 13 diameter
   branch is needed.
2. **False with one extra unit:** in a self-centered graph,
   `alpha(G-N[v]) >= diameter(G)`.  The frozen cycle `C5` has diameter two,
   while the vertices outside any closed neighborhood induce an edge and have
   independence one.  Thus `diameter-1` in the hard rung is sharp on an
   existing control.

## Honest stop point

The induced-star/outside-independent-set bound has a short, concrete Lean
route, and the average-eccentricity dichotomy reduces the source theorem to a
single self-centered structural assertion.  The first implementation step is
the coloring lemma
`induce_insert_union_isBipartite_of_indep`; the first genuinely mathematical
unproved rung is
`exists_large_indep_outside_closedNeighborhood_of_radius_eq_ediam`.

This report does not prove WOWII 19, does not promote the frozen-control audit
to a theorem, and does not authorize a source-status change.  In particular,
using the current `conjecture13` declaration without first eliminating its
`sorryAx` dependency would not constitute a complete formal proof.
