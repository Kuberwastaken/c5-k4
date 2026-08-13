import GraphConjecture40Deficiency

/-!
# WOWII 40: elementary path-cover API

The repository defines `pathCoverNumber` by an `sInf`, but currently exposes
no generic witness-comparison lemmas.  This file constructs the canonical
singleton cover and the edge-plus-singletons cover directly from
`SimpleGraph.IsPathCover`.
-/

namespace WrittenOnTheWallII.GraphConjecture40PathCoverAPI

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

def singletonPathCover : Finset (Finset V) :=
  Finset.univ.image fun v ↦ {v}

/-- All singleton walks form a path cover. -/
lemma singletonPathCover_isPathCover (G : SimpleGraph V) :
    IsPathCover G (singletonPathCover (V := V)) := by
  refine ⟨?_, ?_, ?_⟩
  · intro s₁ hs₁ s₂ hs₂ hne
    simp only [singletonPathCover, mem_image, mem_univ, true_and] at hs₁ hs₂
    obtain ⟨x, rfl⟩ := hs₁
    obtain ⟨y, rfl⟩ := hs₂
    simpa using hne
  · intro x _
    simp [singletonPathCover]
  · intro s hs
    simp only [singletonPathCover, mem_image, mem_univ, true_and] at hs
    obtain ⟨x, rfl⟩ := hs
    exact ⟨x, x, .nil, Walk.IsPath.nil, by simp⟩

/-- The singleton cover has exactly the graph order many members. -/
lemma singletonPathCover_card :
    (singletonPathCover (V := V)).card = Fintype.card V := by
  rw [singletonPathCover, card_image_of_injective]
  · exact card_univ
  · intro x y h
    simpa using h

/-- Any explicit path cover bounds the `sInf` path-cover invariant. -/
lemma pathCoverNumber_le_card_of_isPathCover
    (G : SimpleGraph V) (P : Finset (Finset V))
    (hP : IsPathCover G P) :
    pathCoverNumber G ≤ P.card := by
  unfold pathCoverNumber
  exact Nat.sInf_le ⟨P, rfl, hP⟩

/-- Every finite graph has path-cover number at most its order. -/
theorem pathCoverNumber_le_card (G : SimpleGraph V) :
    pathCoverNumber G ≤ Fintype.card V := by
  rw [← singletonPathCover_card (V := V)]
  exact pathCoverNumber_le_card_of_isPathCover G _
    (singletonPathCover_isPathCover G)

def edgePathCover (u v : V) : Finset (Finset V) :=
  insert {u, v}
    (((Finset.univ.erase u).erase v).image fun x ↦ {x})

/-- One edge, together with singleton paths on every other vertex, is a path
cover. -/
lemma edgePathCover_isPathCover (G : SimpleGraph V) {u v : V}
    (huv : G.Adj u v) :
    IsPathCover G (edgePathCover u v) := by
  refine ⟨?_, ?_, ?_⟩
  · intro s₁ hs₁ s₂ hs₂ hne
    simp only [edgePathCover, mem_insert, mem_image, mem_erase, mem_univ,
      and_true] at hs₁ hs₂
    rcases hs₁ with rfl | ⟨x, ⟨hxv, hxu⟩, rfl⟩
    · rcases hs₂ with hpair | ⟨y, ⟨hyv, hyu⟩, rfl⟩
      · exact (hne hpair.symm).elim
      · rw [Finset.disjoint_singleton_right]
        simp [hyu, hyv]
    · rcases hs₂ with hpair | ⟨y, ⟨hyv, hyu⟩, rfl⟩
      · subst s₂
        rw [Finset.disjoint_singleton_left]
        simp [hxu, hxv]
      · simpa using hne
  · intro x _
    by_cases hxu : x = u
    · subst x
      simp [edgePathCover]
    by_cases hxv : x = v
    · subst x
      simp [edgePathCover]
    · simp [edgePathCover, hxu, hxv]
  · intro s hs
    simp only [edgePathCover, mem_insert, mem_image, mem_erase, mem_univ,
      and_true] at hs
    rcases hs with rfl | ⟨x, -, rfl⟩
    · exact ⟨u, v, huv.toWalk, Walk.IsPath.of_adj huv, by
        simp⟩
    · exact ⟨x, x, .nil, Walk.IsPath.nil, by simp⟩

/-- The edge-plus-singletons cover has one fewer member than the graph
order. -/
lemma edgePathCover_card (u v : V) (huv : u ≠ v) :
    (edgePathCover u v).card + 1 = Fintype.card V := by
  have hn : 2 ≤ Fintype.card V := by
    have hcard := Finset.card_le_card
      (show ({u, v} : Finset V) ⊆ Finset.univ from Finset.subset_univ _)
    simpa [Finset.card_pair huv] using hcard
  unfold edgePathCover
  have hpair : {u, v} ∉
      ((Finset.univ.erase u).erase v).image
        (fun x : V ↦ ({x} : Finset V)) := by
    intro h
    simp only [mem_image, mem_erase, mem_univ, and_true] at h
    obtain ⟨x, -, hx⟩ := h
    have : ({u, v} : Finset V).card = ({x} : Finset V).card :=
      congrArg Finset.card hx.symm
    simp [huv] at this
  rw [card_insert_of_notMem hpair, card_image_of_injective]
  · rw [card_erase_of_mem (by simp [huv.symm]),
      card_erase_of_mem (by simp), card_univ]
    omega
  · intro x y h
    simpa using h

/-- A graph containing an edge has path-cover number strictly below its
order. -/
theorem pathCoverNumber_lt_card_of_adj (G : SimpleGraph V) {u v : V}
    (huv : G.Adj u v) :
    pathCoverNumber G < Fintype.card V := by
  have hle := pathCoverNumber_le_card_of_isPathCover G (edgePathCover u v)
    (edgePathCover_isPathCover G huv)
  have hcard := edgePathCover_card u v huv.ne
  omega

/-- A connected graph on more than one vertex contains an edge and therefore
has path-cover number strictly below its order. -/
theorem pathCoverNumber_lt_card_of_connected
    (G : SimpleGraph V) [Nontrivial V] (hconn : G.Connected) :
    pathCoverNumber G < Fintype.card V := by
  let u : V := Classical.choice inferInstance
  obtain ⟨v, huv⟩ := hconn.preconnected.exists_adj_of_nontrivial u
  exact pathCoverNumber_lt_card_of_adj G huv

/-- The deficiency equivalence with its elementary path-cover upper bound
discharged. -/
theorem integer_bound_iff_deficiency_bound (G : SimpleGraph V) :
    pathCoverNumber G + G.largestInducedBipartiteSubgraphSize + 1 ≤
        2 * G.largestInducedForestSize ↔
      2 * GraphConjecture40Deficiency.feedbackDeletion G + 1 ≤
        GraphConjecture40Deficiency.linearForestRank G +
          GraphConjecture40Deficiency.oddDeletion G :=
  GraphConjecture40Deficiency.integer_bound_iff_deficiency_bound G
    (pathCoverNumber_le_card G)

/-- The complete connected nontrivial zero-feedback-deletion base case. -/
theorem conjecture40_of_isAcyclic
    (G : SimpleGraph V) [Nontrivial V]
    (hconn : G.Connected) (hG : G.IsAcyclic) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize :=
  GraphConjecture40Deficiency.conjecture40_of_isAcyclic_of_pathCoverNumber_lt_card
    G hG (pathCoverNumber_lt_card_of_connected G hconn)

end WrittenOnTheWallII.GraphConjecture40PathCoverAPI
