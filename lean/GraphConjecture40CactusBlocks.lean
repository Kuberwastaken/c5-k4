import GraphConjecture40FeedbackPathFamily

/-!
# WOWII 40: explicit cactus-petal certificates

A bridge-connected cactus can be harvested blockwise: each cyclic petal
supplies a path on at least three vertices, and one bridge supplies an extra
edge.  This file packages exactly that local certificate, proves that its
pieces assemble into a disjoint path family of rank at least `2k+1`, and
closes the bipartite WOWII 40 inequality when the feedback coordinate is `k`.
-/

namespace WrittenOnTheWallII.GraphConjecture40CactusBlocks

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A block-level certificate consisting of `k` disjoint petal paths of order
at least three and one further disjoint bridge path of order at least two. -/
structure CactusPetalCertificate (G : SimpleGraph V) (k : ℕ) where
  petals : Finset (Finset V)
  bridge : Finset V
  petals_family :
    GraphConjecture40PathFamily.IsPathSupportFamily G petals
  petals_card : petals.card = k
  petals_three : ∀ s ∈ petals, 3 ≤ s.card
  bridge_path : ∃ (a z : V) (p : G.Walk a z),
    p.IsPath ∧ bridge = p.support.toFinset
  bridge_two : 2 ≤ bridge.card
  bridge_disjoint :
    Disjoint bridge (GraphConjecture40PathFamily.coveredVertices petals)

namespace CactusPetalCertificate

variable {G : SimpleGraph V} {k : ℕ}

omit [Fintype V] in
lemma bridge_not_mem_petals (C : CactusPetalCertificate G k) :
    C.bridge ∉ C.petals := by
  intro hmem
  obtain ⟨x, hx⟩ := Finset.card_pos.mp (lt_of_lt_of_le (by omega) C.bridge_two)
  have hxcovered : x ∈
      GraphConjecture40PathFamily.coveredVertices C.petals :=
    GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
      ⟨C.bridge, hmem, hx⟩
  exact Finset.disjoint_left.mp C.bridge_disjoint hx hxcovered

omit [Fintype V] in
/-- The petals and bridge assemble into a path-support family. -/
lemma insert_bridge_isPathSupportFamily (C : CactusPetalCertificate G k) :
    GraphConjecture40PathFamily.IsPathSupportFamily G
      (insert C.bridge C.petals) := by
  refine ⟨?_, ?_⟩
  · intro s₁ hs₁ s₂ hs₂ hne
    simp only [mem_insert] at hs₁ hs₂
    rcases hs₁ with rfl | hs₁P
    · rcases hs₂ with hsame | hs₂P
      · exact (hne hsame.symm).elim
      · rw [Finset.disjoint_left]
        intro x hxb hxS
        exact Finset.disjoint_left.mp C.bridge_disjoint hxb
          (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
            ⟨s₂, hs₂P, hxS⟩)
    · rcases hs₂ with rfl | hs₂P
      · rw [Finset.disjoint_left]
        intro x hxS hxb
        exact Finset.disjoint_left.mp C.bridge_disjoint hxb
          (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
            ⟨s₁, hs₁P, hxS⟩)
      · exact C.petals_family.1 s₁ hs₁P s₂ hs₂P hne
  · intro s hs
    simp only [mem_insert] at hs
    rcases hs with rfl | hsP
    · exact C.bridge_path
    · exact C.petals_family.2 s hsP

omit [Fintype V] in
lemma insert_bridge_card (C : CactusPetalCertificate G k) :
    (insert C.bridge C.petals).card = k + 1 := by
  rw [card_insert_of_notMem C.bridge_not_mem_petals, C.petals_card]

omit [Fintype V] in
/-- The assembled petal certificate has rank at least `2k+1`. -/
lemma insert_bridge_rank (C : CactusPetalCertificate G k) :
    (insert C.bridge C.petals).card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices
        (insert C.bridge C.petals)).card := by
  rw [GraphConjecture40FeedbackPathFamily.card_coveredVertices_eq_sum
    G (insert C.bridge C.petals) C.insert_bridge_isPathSupportFamily]
  rw [sum_insert C.bridge_not_mem_petals]
  have hpetalSum : ∑ s ∈ C.petals, 3 ≤
      ∑ s ∈ C.petals, s.card :=
    Finset.sum_le_sum fun s hs ↦ C.petals_three s hs
  have hpetalLower : C.petals.card * 3 ≤
      ∑ s ∈ C.petals, s.card := by simpa using hpetalSum
  rw [C.insert_bridge_card]
  rw [C.petals_card] at hpetalLower
  have hbridge := C.bridge_two
  omega

end CactusPetalCertificate

/-- Block/cactus structural class for WOWII 40: `k` cyclic petals harvested
as three-vertex paths, plus one disjoint bridge edge, pay the full bipartite
deficiency budget. -/
theorem conjecture40_of_bipartite_of_cactusPetalCertificate
    (G : SimpleGraph V) (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    (C : CactusPetalCertificate G k) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  exact GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG htau (insert C.bridge C.petals)
      C.insert_bridge_isPathSupportFamily C.insert_bridge_rank

end WrittenOnTheWallII.GraphConjecture40CactusBlocks
