import GraphConjecture59CornerExclusion

/-!
# WOWII 59: one-for-one exchange constraints

Let `S` be a maximum induced bipartite six-core, let `x` lie outside it, and
fix a valid two-coloring `c` of `G[S]`.  The v0.12 obstruction says that `x`
has an attachment in each color class.

This file proves the sharp exchange dichotomy for each color `k`: either `x`
has at least two attachments of color `k`, or deleting the unique such
attachment and inserting `x` produces another induced bipartite six-core.  If
`f(G)=4`, every five-vertex deletion from the exchanged core is again cyclic.
-/

namespace WrittenOnTheWallII.GraphConjecture59CoreExchange

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Attachments into one color class of a fixed coloring. -/
def colorAttachments (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2) (k : Fin 2) : Finset V :=
  (_root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.attachments G S x).filter
    fun y ↦ c y = k

omit [Fintype V] in
/-- If a color class has at most one attachment, removing its known attachment
makes that color compatible with every remaining neighbor of `x`. -/
theorem compatible_color_after_erasing_unique_attachment
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2) (k : Fin 2)
    (hsmall : (colorAttachments G S x c k).card ≤ 1)
    {v : V} (hvS : v ∈ S) (hxv : G.Adj x v) (hcv : c v = k) :
    ∀ y ∈ S.erase v, G.Adj x y → k ≠ c y := by
  intro y hy hxy heq
  have hvA : v ∈ colorAttachments G S x c k := by
    simp [colorAttachments,
      _root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.attachments,
      hvS, hxv, hcv]
  have hyS : y ∈ S := (mem_erase.mp hy).2
  have hyA : y ∈ colorAttachments G S x c k := by
    simp [colorAttachments,
      _root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.attachments,
      hyS, hxy, heq.symm]
  have hyv : y = v := (card_le_one.mp hsmall) y hyA v hvA
  exact (mem_erase.mp hy).1 hyv

omit [Fintype V] in
/-- One-for-one exchange: a unique attachment on one color side can be removed
and replaced by the outside vertex while preserving bipartiteness and order
six. -/
theorem exchange_core_of_color_attachment_card_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSsix : S.card = 6) (hx : x ∉ S) (k : Fin 2)
    (hsmall : (colorAttachments G S x c k).card ≤ 1)
    {v : V} (hvS : v ∈ S) (hxv : G.Adj x v) (hcv : c v = k) :
    (G.induce ((insert x (S.erase v) : Finset V) : Set V)).IsBipartite ∧
      (insert x (S.erase v)).card = 6 := by
  have hrestricted :
      ∀ u ∈ S.erase v, ∀ w ∈ S.erase v,
        G.Adj u w → c u ≠ c w := by
    intro u hu w hw hadj
    exact hc u (mem_erase.mp hu).2 w (mem_erase.mp hw).2 hadj
  have hcompatible := compatible_color_after_erasing_unique_attachment
    G S x c k hsmall hvS hxv hcv
  constructor
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.induce_insert_isBipartite_of_compatible_color
        G (S.erase v) x c hrestricted k hcompatible
  · rw [card_insert_of_notMem (fun h ↦ hx ((mem_erase.mp h).2)),
      card_erase_of_mem hvS, hSsix]

/-- With `f(G)=4`, the exchanged bipartite six-core inherits the same
deletion-critical obstruction as the original core. -/
theorem exchanged_core_is_deletion_critical
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSsix : S.card = 6) (hx : x ∉ S) (k : Fin 2)
    (hsmall : (colorAttachments G S x c k).card ≤ 1)
    {v : V} (hvS : v ∈ S) (hxv : G.Adj x v) (hcv : c v = k)
    (hf : G.largestInducedForestSize = 4) :
    let T := insert x (S.erase v)
    (G.induce (T : Set V)).IsBipartite ∧ T.card = 6 ∧
      ∀ z ∈ T, ¬(G.induce ((T.erase z : Finset V) : Set V)).IsAcyclic := by
  dsimp
  obtain ⟨hTbip, hTcard⟩ := exchange_core_of_color_attachment_card_le_one
    G S x c hc hSsix hx k hsmall hvS hxv hcv
  refine ⟨hTbip, hTcard, ?_⟩
  intro z hz
  exact
    _root_.WrittenOnTheWallII.GraphConjecture59CornerStructure.single_deletion_not_acyclic_of_six_of_forest_eq_four
      G (insert x (S.erase v)) hTcard hf hz

/-- **Exchange dichotomy.** If no one-for-one exchange through color `k` is
bipartite, then the outside vertex has at least two attachments of color `k`.
-/
theorem two_color_attachments_of_no_bipartite_exchange
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSsix : S.card = 6)
    (hb : G.largestInducedBipartiteSubgraphSize = 6)
    (hx : x ∉ S) (k : Fin 2)
    (hnoexchange : ∀ v ∈ S,
      ¬(G.induce ((insert x (S.erase v) : Finset V) : Set V)).IsBipartite) :
    2 ≤ (colorAttachments G S x c k).card := by
  by_contra hnot
  have hsmall : (colorAttachments G S x c k).card ≤ 1 := by omega
  obtain ⟨v, hvS, hxv, hcv⟩ :=
    _root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.every_color_occurs_among_attachments
      G S c hc hSsix hb hx k
  obtain ⟨hTbip, -⟩ := exchange_core_of_color_attachment_card_le_one
    G S x c hc hSsix hx k hsmall hvS hxv hcv
  exact hnoexchange v hvS hTbip

/-- If no one-for-one exchange works through either color, every outside
vertex has at least two attachments on each side of the bipartition. -/
theorem two_attachments_in_each_color_of_no_bipartite_exchange
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSsix : S.card = 6)
    (hb : G.largestInducedBipartiteSubgraphSize = 6)
    (hx : x ∉ S)
    (hnoexchange : ∀ v ∈ S,
      ¬(G.induce ((insert x (S.erase v) : Finset V) : Set V)).IsBipartite) :
    2 ≤ (colorAttachments G S x c 0).card ∧
      2 ≤ (colorAttachments G S x c 1).card := by
  exact ⟨
    two_color_attachments_of_no_bipartite_exchange
      G S x c hc hSsix hb hx 0 hnoexchange,
    two_color_attachments_of_no_bipartite_exchange
      G S x c hc hSsix hb hx 1 hnoexchange⟩

end WrittenOnTheWallII.GraphConjecture59CoreExchange
