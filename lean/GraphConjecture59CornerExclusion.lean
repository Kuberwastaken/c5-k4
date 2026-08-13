import GraphConjecture59CornerStructure

/-!
# WOWII 59: ambient attachment obstruction

This file closes the first global gap left by the six-vertex corner audit.
Given a maximum induced bipartite six-set `S`, every outside vertex has at
least two neighbors in `S`.  Indeed, a vertex with zero or one attachment can
always be assigned a color extending a two-coloring of `G[S]`; then `S` plus
that vertex would be an induced bipartite seven-set, contradicting `b(G)=6`.
-/

namespace WrittenOnTheWallII.GraphConjecture59CornerExclusion

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Attachments of `x` into a finite retained vertex set. -/
def attachments (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) : Finset V :=
  S.filter fun y ↦ G.Adj x y

omit [Fintype V] in
/-- If one color is compatible with every attachment of a new vertex, it
extends a coloring of `S` to `insert x S`. -/
theorem induce_insert_isBipartite_of_compatible_color
    (G : SimpleGraph V) (S : Finset V) (x : V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (cx : Fin 2)
    (hcx : ∀ y ∈ S, G.Adj x y → cx ≠ c y) :
    (G.induce ((insert x S : Finset V) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨fun z ↦ if z = x then cx else c z, ?_⟩
  intro u hu v hv hadj
  by_cases hux : u = x
  · subst u
    have hvx : v ≠ x := hadj.ne.symm
    have hvS : v ∈ S := (mem_insert.mp hv).resolve_left hvx
    simpa [hvx] using hcx v hvS hadj
  · by_cases hvx : v = x
    · subst v
      have huS : u ∈ S := (mem_insert.mp hu).resolve_left hux
      simpa [hux] using (hcx u huS hadj.symm).symm
    · have huS : u ∈ S := (mem_insert.mp hu).resolve_left hux
      have hvS : v ∈ S := (mem_insert.mp hv).resolve_left hvx
      simpa [hux, hvx] using hc u huS v hvS hadj

omit [Fintype V] [DecidableEq V] in
/-- Zero or one attachment always admits a compatible color. -/
theorem exists_compatible_color_of_attachment_card_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hcard : (attachments G S x).card ≤ 1) :
    ∃ cx : Fin 2, ∀ y ∈ S, G.Adj x y → cx ≠ c y := by
  classical
  by_cases hA : (attachments G S x).Nonempty
  · obtain ⟨a, ha⟩ := hA
    let cx : Fin 2 := if c a = 0 then 1 else 0
    refine ⟨cx, ?_⟩
    intro y hyS hxy
    have hyA : y ∈ attachments G S x := by
      classical
      simpa [attachments] using (mem_filter.mpr ⟨hyS, hxy⟩)
    have hya : y = a := (card_le_one.mp hcard) y hyA a ha
    subst y
    dsimp [cx]
    by_cases hca : c a = 0
    · simp [hca]
    · have hcaOne : c a = 1 := Fin.eq_one_of_ne_zero (c a) hca
      simp [hcaOne]
  · refine ⟨0, ?_⟩
    intro y hyS hxy
    exfalso
    apply hA
    exact ⟨y, by
      classical
      simpa [attachments] using (mem_filter.mpr ⟨hyS, hxy⟩)⟩

omit [Fintype V] in
/-- A vertex with at most one attachment can be inserted while preserving
bipartiteness. -/
theorem induce_insert_isBipartite_of_attachment_card_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) (x : V)
    (hS : (G.induce (S : Set V)).IsBipartite)
    (hcard : (attachments G S x).card ≤ 1) :
    (G.induce ((insert x S : Finset V) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring] at hS
  obtain ⟨c, hc⟩ := hS
  obtain ⟨cx, hcx⟩ :=
    exists_compatible_color_of_attachment_card_le_one G S x c hcard
  exact induce_insert_isBipartite_of_compatible_color G S x c hc cx hcx

/-- **Universal ambient attachment obstruction.** If `S` is a six-vertex
induced bipartite witness in a graph with `b(G)=6`, every vertex outside `S`
has at least two neighbors in `S`. -/
theorem two_le_attachment_card_of_maximum_bipartite_six
    (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V)
    (hS : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6)
    (hb : G.largestInducedBipartiteSubgraphSize = 6)
    {x : V} (hx : x ∉ S) :
    2 ≤ (attachments G S x).card := by
  by_contra hnot
  have hcard : (attachments G S x).card ≤ 1 := by omega
  have hins := induce_insert_isBipartite_of_attachment_card_le_one
    G S x hS hcard
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
      G (insert x S) hins
  rw [card_insert_of_notMem hx, hSsix, hb] at hbound
  omega

/-- Stronger parity form of the ambient obstruction: relative to every valid
two-coloring of a maximum bipartite six-set, each outside vertex attaches to
both color classes. -/
theorem every_color_occurs_among_attachments
    (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V)
    (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSsix : S.card = 6)
    (hb : G.largestInducedBipartiteSubgraphSize = 6)
    {x : V} (hx : x ∉ S) (k : Fin 2) :
    ∃ y ∈ S, G.Adj x y ∧ c y = k := by
  by_contra hnone
  have hcompatible : ∀ y ∈ S, G.Adj x y → k ≠ c y := by
    intro y hy hadj heq
    apply hnone
    exact ⟨y, hy, hadj, heq.symm⟩
  have hins := induce_insert_isBipartite_of_compatible_color
    G S x c hc k hcompatible
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
      G (insert x S) hins
  rw [card_insert_of_notMem hx, hSsix, hb] at hbound
  omega

/-- Combined exact structure forced by the hypothetical `(b,f)=(6,4)`
corner: all one-vertex cards of the witness are cyclic, and all ambient outside
vertices have at least two attachments into it. -/
theorem corner_witness_structure
    (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V)
    (hS : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6)
    (hb : G.largestInducedBipartiteSubgraphSize = 6)
    (hf : G.largestInducedForestSize = 4) :
    (∀ v ∈ S,
      ¬(G.induce ((S.erase v : Finset V) : Set V)).IsAcyclic) ∧
    (∀ x ∉ S, 2 ≤ (attachments G S x).card) := by
  constructor
  · intro v hv
    exact
      _root_.WrittenOnTheWallII.GraphConjecture59CornerStructure.single_deletion_not_acyclic_of_six_of_forest_eq_four
        G S hSsix hf hv
  · intro x hx
    exact two_le_attachment_card_of_maximum_bipartite_six
      G S hS hSsix hb hx

end WrittenOnTheWallII.GraphConjecture59CornerExclusion
