import GraphConjecture40OneVertexSeparation

/-!
# WOWII 40: separated unions preserve acyclicity

Two induced forests with no cross edges have an acyclic induced union.  The
proof colors the union by its side and observes that every walk preserves that
color, so every cycle localizes to one side.
-/

namespace WrittenOnTheWallII.GraphConjecture40SeparatedUnion

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- A walk in an anticomplete union cannot change sides. -/
lemma Walk.end_mem_left_of_anticomplete
    (G : SimpleGraph V) (A B : Finset V)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hu : u.1 ∈ A) : v.1 ∈ A := by
  induction p with
  | nil => exact hu
  | @cons u w v huw p ih =>
      have hwAB : w.1 ∈ A ∨ w.1 ∈ B := Finset.mem_union.mp w.property
      have hwA : w.1 ∈ A := by
        rcases hwAB with hwA | hwB
        · exact hwA
        · exact (hcross u.1 hu w.1 hwB huw).elim
      exact ih hwA

omit [Fintype V] in
/-- Every vertex on a walk whose initial vertex lies on the left also lies on
the left. -/
lemma Walk.support_subset_left_of_anticomplete
    (G : SimpleGraph V) (A B : Finset V)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hu : u.1 ∈ A) : ∀ z ∈ p.support, z.1 ∈ A := by
  intro z hz
  obtain ⟨puz, _pzv, hp⟩ := Walk.mem_support_iff_exists_append.mp hz
  subst p
  exact Walk.end_mem_left_of_anticomplete G A B hcross puz hu

omit [Fintype V] in
/-- A walk in an anticomplete union that begins on the right remains on the
right. -/
lemma Walk.end_mem_right_of_anticomplete
    (G : SimpleGraph V) (A B : Finset V)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hu : u.1 ∈ B) : v.1 ∈ B := by
  induction p with
  | nil => exact hu
  | @cons u w v huw p ih =>
      have hwAB : w.1 ∈ A ∨ w.1 ∈ B := Finset.mem_union.mp w.property
      have hwB : w.1 ∈ B := by
        rcases hwAB with hwA | hwB
        · exact (hcross w.1 hwA u.1 hu huw.symm).elim
        · exact hwB
      exact ih hwB

omit [Fintype V] in
/-- Every vertex on a walk whose initial vertex lies on the right also lies on
the right. -/
lemma Walk.support_subset_right_of_anticomplete
    (G : SimpleGraph V) (A B : Finset V)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b)
    {u v : ↥(↑(A ∪ B) : Set V)}
    (p : (G.induce (↑(A ∪ B) : Set V)).Walk u v)
    (hu : u.1 ∈ B) : ∀ z ∈ p.support, z.1 ∈ B := by
  intro z hz
  obtain ⟨puz, _pzv, hp⟩ := Walk.mem_support_iff_exists_append.mp hz
  subst p
  exact Walk.end_mem_right_of_anticomplete G A B hcross puz hu

omit [Fintype V] in
/-- Reverse separated-union lemma. -/
theorem induce_union_isAcyclic_of_anticomplete
    (G : SimpleGraph V) (A B : Finset V)
    (hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b)
    (hA : (G.induce (↑A : Set V)).IsAcyclic)
    (hB : (G.induce (↑B : Set V)).IsAcyclic) :
    (G.induce (↑(A ∪ B) : Set V)).IsAcyclic := by
  intro v p hp
  have hvAB : v.1 ∈ A ∨ v.1 ∈ B := Finset.mem_union.mp v.property
  rcases hvAB with hvA | hvB
  · have hs : ∀ z ∈ p.support, z.1 ∈ A :=
      Walk.support_subset_left_of_anticomplete G A B hcross p hvA
    let f : p.toSubgraph.coe →g G.induce (↑A : Set V) :=
      { toFun := fun z => ⟨z.1.1, hs z.1 (p.mem_verts_toSubgraph.mp z.2)⟩
        map_rel' := fun hadj => by
          exact p.toSubgraph.coe_adj_sub _ _ hadj }
    have hf : Function.Injective f := by
      intro x y h
      have h' := congrArg Subtype.val h
      change x.1.1 = y.1.1 at h'
      apply Subtype.ext
      apply Subtype.ext
      exact h'
    have hhom : Function.Injective p.toSubgraph.hom := by
      exact SimpleGraph.Subgraph.hom_injective
    have hpSub : p.mapToSubgraph.IsCycle := by
      apply (Walk.map_isCycle_iff_of_injective hhom).mp
      rw [Walk.map_mapToSubgraph_hom]
      exact hp
    exact hA (p.mapToSubgraph.map f) (hpSub.map hf)
  · have hs : ∀ z ∈ p.support, z.1 ∈ B :=
      Walk.support_subset_right_of_anticomplete G A B hcross p hvB
    let f : p.toSubgraph.coe →g G.induce (↑B : Set V) :=
      { toFun := fun z => ⟨z.1.1, hs z.1 (p.mem_verts_toSubgraph.mp z.2)⟩
        map_rel' := fun hadj => by
          exact p.toSubgraph.coe_adj_sub _ _ hadj }
    have hf : Function.Injective f := by
      intro x y h
      have h' := congrArg Subtype.val h
      change x.1.1 = y.1.1 at h'
      apply Subtype.ext
      apply Subtype.ext
      exact h'
    have hhom : Function.Injective p.toSubgraph.hom := by
      exact SimpleGraph.Subgraph.hom_injective
    have hpSub : p.mapToSubgraph.IsCycle := by
      apply (Walk.map_isCycle_iff_of_injective hhom).mp
      rw [Walk.map_mapToSubgraph_hom]
      exact hp
    exact hB (p.mapToSubgraph.map f) (hpSub.map hf)

namespace OneVertexSeparation

variable {G : SimpleGraph V}

/-- The reverse exclude-state inequality, obtained by unioning attained side
forests and applying separated-union cycle localization. -/
theorem sum_within_erase_le_forestOrderExcluding
    (D : OneVertexSeparation G) :
    forestOrderWithin G (D.left.erase D.cut) +
        forestOrderWithin G (D.right.erase D.cut) ≤
      GraphConjecture40CutVertexSum.forestOrderExcluding G D.cut := by
  obtain ⟨A, hAL, hAacyc, hAcard⟩ :=
    exists_forestOrderWithin_witness G (D.left.erase D.cut)
  obtain ⟨B, hBR, hBacyc, hBcard⟩ :=
    exists_forestOrderWithin_witness G (D.right.erase D.cut)
  have hdisj : Disjoint A B := by
    rw [Finset.disjoint_left]
    intro v hvA hvB
    have hvinter : v ∈ D.left ∩ D.right :=
      mem_inter.mpr ⟨(mem_erase.mp (hAL hvA)).2,
        (mem_erase.mp (hBR hvB)).2⟩
    have hvc : v = D.cut := by simpa [D.inter] using hvinter
    exact (mem_erase.mp (hAL hvA)).1 hvc
  have hcross : ∀ a ∈ A, ∀ b ∈ B, ¬G.Adj a b := by
    intro a ha b hb
    exact D.no_cross a (mem_erase.mp (hAL ha)).2
      (mem_erase.mp (hAL ha)).1 b (mem_erase.mp (hBR hb)).2
      (mem_erase.mp (hBR hb)).1
  have hacyc := induce_union_isAcyclic_of_anticomplete G A B hcross
    hAacyc hBacyc
  have hcut : D.cut ∉ A ∪ B := by
    simp only [mem_union]
    push_neg
    exact ⟨fun h => (mem_erase.mp (hAL h)).1 rfl,
      fun h => (mem_erase.mp (hBR h)).1 rfl⟩
  have hbound := GraphConjecture40CutVertexSum.card_le_forestOrderExcluding
    G D.cut (A ∪ B) hacyc hcut
  rw [card_union_of_disjoint hdisj, hAcard, hBcard] at hbound
  exact hbound

/-- Exact exclude-cut state formula for a one-vertex separation. -/
theorem forestOrderExcluding_eq_sum_within_erase
    (D : OneVertexSeparation G) :
    GraphConjecture40CutVertexSum.forestOrderExcluding G D.cut =
      forestOrderWithin G (D.left.erase D.cut) +
        forestOrderWithin G (D.right.erase D.cut) := by
  exact le_antisymm D.forestOrderExcluding_le_sum_within_erase
    (sum_within_erase_le_forestOrderExcluding D)

end OneVertexSeparation

end WrittenOnTheWallII.GraphConjecture40SeparatedUnion
