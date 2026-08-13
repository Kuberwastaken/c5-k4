import GraphConjecture40Baseline

/-!
# WOWII 40: the colour-imbalance residual

The source baseline only uses the larger colour class of a maximum induced
bipartite subgraph.  Keeping the resulting colour-class imbalance proves the
full conjectured inequality whenever that imbalance pays for `p(G) - 1`.

This is a strict extension of the traceable (`p(G) = 1`) slice: it permits
arbitrary path-cover number, provided a maximum bipartite witness has colour
classes whose size difference is at least `p(G) - 1`.
-/

namespace WrittenOnTheWallII.GraphConjecture40Residual

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

abbrev zeroClass (S : Finset V) (c : V → Fin 2) : Finset V :=
  S.filter fun x ↦ c x = 0

abbrev oneClass (S : Finset V) (c : V → Fin 2) : Finset V :=
  S.filter fun x ↦ c x ≠ 0

/-- A maximum induced bipartite witness with sufficiently imbalanced colour
classes pays the complete integer residual in WOWII 40. -/
theorem integer_bound_of_maximum_bipartite_coloring_imbalance
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected)
    (S : Finset V)
    (hmax : S.card = G.largestInducedBipartiteSubgraphSize)
    (c : V → Fin 2)
    (hc : ∀ x ∈ S, ∀ y ∈ S, G.Adj x y → c x ≠ c y)
    (horder : (oneClass S c).card ≤ (zeroClass S c).card)
    (hpay : pathCoverNumber G ≤
      (zeroClass S c).card - (oneClass S c).card + 1) :
    pathCoverNumber G + G.largestInducedBipartiteSubgraphSize + 1 ≤
      2 * G.largestInducedForestSize := by
  let A := zeroClass S c
  let C := oneClass S c
  have hpart : A.card + C.card = S.card := by
    simpa [A, C, zeroClass, oneClass] using
      (Finset.card_filter_add_card_filter_not
        (s := S) (p := fun x ↦ c x = 0))
  have hAind : G.IsIndepSet (A : Set V) := by
    intro x hx y hy hxy hadj
    have hcx : c x = 0 := (Finset.mem_filter.mp hx).2
    have hcy : c y = 0 := (Finset.mem_filter.mp hy).2
    exact (hc x (Finset.mem_filter.mp hx).1 y
      (Finset.mem_filter.mp hy).1 hadj) (hcx.trans hcy.symm)
  obtain ⟨v, hv⟩ :=
    GraphConjecture40Baseline.exists_not_mem_of_indep_of_connected
      hconn A hAind
  have hforest : A.card + 1 ≤ G.largestInducedForestSize := by
    have hins :=
      GraphConjecture40Baseline.card_le_largestInducedForestSize G
        (insert v A)
        (GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
          G A v hAind)
    simpa [Finset.card_insert_of_notMem hv] using hins
  change C.card ≤ A.card at horder
  change pathCoverNumber G ≤ A.card - C.card + 1 at hpay
  omega

/-- The preceding integer inequality in the exact real/ceiling shape of the
upstream conjecture. -/
theorem conjecture40_of_maximum_bipartite_coloring_imbalance
    (G : SimpleGraph V) [Nontrivial V]
    (S : Finset V)
    (hmax : S.card = G.largestInducedBipartiteSubgraphSize)
    (c : V → Fin 2)
    (hc : ∀ x ∈ S, ∀ y ∈ S, G.Adj x y → c x ≠ c y)
    (horder : (oneClass S c).card ≤ (zeroClass S c).card)
    (hpay : pathCoverNumber G ≤
      (zeroClass S c).card - (oneClass S c).card + 1)
    (hconn : G.Connected) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hint := integer_bound_of_maximum_bipartite_coloring_imbalance
    G hconn S hmax c hc horder hpay
  have hintR :
      (pathCoverNumber G : ℝ) + b G + 1 ≤
        2 * (G.largestInducedForestSize : ℝ) := by
    unfold b
    exact_mod_cast hint
  rw [Int.ceil_le]
  norm_num
  linarith

end WrittenOnTheWallII.GraphConjecture40Residual
