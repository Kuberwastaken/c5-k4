import GraphConjecture59TwoVertexCompatibility

/-!
# WOWII 59: compatibility selection and its exact obstruction

This file turns the seven-vertex compatibility theorem into a finite exchange
criterion over two candidate pools and isolates the precise obstruction when
selection fails.
-/

namespace WrittenOnTheWallII.GraphConjecture59CompatibilityExchange

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Candidates blocked from joining the outside color side. -/
def outsideSideBlocked (G : SimpleGraph V) [DecidableRel G.Adj]
    (P : Finset V) (x y z : V) : Finset V :=
  P.filter fun p ↦ G.Adj p x ∨ G.Adj p y ∨ G.Adj p z

/-- Candidates blocked from joining the core color side. -/
def coreSideBlocked (G : SimpleGraph V) [DecidableRel G.Adj]
    (Q : Finset V) (a b : V) : Finset V :=
  Q.filter fun q ↦ G.Adj q a ∨ G.Adj q b

omit [Fintype V] [DecidableEq V] in
/-- A proper outside-side blocker set leaves a compatible candidate. -/
theorem exists_outside_side_candidate_of_blocked_lt
    (G : SimpleGraph V) [DecidableRel G.Adj] (P : Finset V) (x y z : V)
    (h : (outsideSideBlocked G P x y z).card < P.card) :
    ∃ p ∈ P, ¬G.Adj p x ∧ ¬G.Adj p y ∧ ¬G.Adj p z := by
  have hnsub : ¬P ⊆ outsideSideBlocked G P x y z := by
    intro hsub
    have := card_le_card hsub
    omega
  obtain ⟨p, hpP, hp⟩ := Finset.not_subset.mp hnsub
  refine ⟨p, hpP, ?_⟩
  simpa [outsideSideBlocked, hpP, not_or] using hp

omit [Fintype V] [DecidableEq V] in
/-- A proper core-side blocker set leaves a compatible candidate. -/
theorem exists_core_side_candidate_of_blocked_lt
    (G : SimpleGraph V) [DecidableRel G.Adj] (Q : Finset V) (a b : V)
    (h : (coreSideBlocked G Q a b).card < Q.card) :
    ∃ q ∈ Q, ¬G.Adj q a ∧ ¬G.Adj q b := by
  have hnsub : ¬Q ⊆ coreSideBlocked G Q a b := by
    intro hsub
    have := card_le_card hsub
    omega
  obtain ⟨q, hqQ, hq⟩ := Finset.not_subset.mp hnsub
  refine ⟨q, hqQ, ?_⟩
  simpa [coreSideBlocked, hqQ, not_or] using hq

omit [Fintype V] [DecidableEq V] in
/-- Exact obstruction: every candidate is blocked iff the blocker filter is
the whole candidate pool. -/
theorem outside_selection_fails_iff_all_blocked
    (G : SimpleGraph V) [DecidableRel G.Adj] (P : Finset V) (x y z : V) :
    (¬∃ p ∈ P, ¬G.Adj p x ∧ ¬G.Adj p y ∧ ¬G.Adj p z) ↔
      outsideSideBlocked G P x y z = P := by
  constructor
  · intro h
    apply Subset.antisymm
    · exact filter_subset _ _
    · intro p hp
      simp only [outsideSideBlocked, mem_filter, hp, true_and]
      by_contra hnone
      have hpx : ¬G.Adj p x := fun hx ↦ hnone (Or.inl hx)
      have hpy : ¬G.Adj p y := fun hy ↦ hnone (Or.inr (Or.inl hy))
      have hpz : ¬G.Adj p z := fun hz ↦ hnone (Or.inr (Or.inr hz))
      exact h ⟨p, hp, hpx, hpy, hpz⟩
  · intro heq hex
    obtain ⟨p, hp, hpx, hpy, hpz⟩ := hex
    have : p ∈ outsideSideBlocked G P x y z := by simpa [heq] using hp
    simp only [outsideSideBlocked, mem_filter] at this
    rcases this.2 with h | h | h
    · exact hpx h
    · exact hpy h
    · exact hpz h

omit [Fintype V] [DecidableEq V] in
/-- Two proper blocker sets produce the opposite-side compatibility data
needed by the seven-vertex theorem. -/
theorem exists_opposite_side_compatible_pair
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (P Q : Finset V) (a b x y z : V)
    (hP : (outsideSideBlocked G P x y z).card < P.card)
    (hQ : (coreSideBlocked G Q a b).card < Q.card)
    (hdisj : Disjoint P Q) :
    ∃ p ∈ P, ∃ q ∈ Q, p ≠ q ∧
      OppositeSideCompatible G a b x y z p q := by
  obtain ⟨p, hpP, hpx, hpy, hpz⟩ :=
    exists_outside_side_candidate_of_blocked_lt G P x y z hP
  obtain ⟨q, hqQ, hqa, hqb⟩ :=
    exists_core_side_candidate_of_blocked_lt G Q a b hQ
  have hpq : p ≠ q := by
    intro hpq
    subst q
    exact (Finset.disjoint_left.mp hdisj) hpP hqQ
  exact ⟨p, hpP, q, hqQ, hpq, hpx, hpy, hpz, hqa, hqb⟩

end WrittenOnTheWallII.GraphConjecture59CompatibilityExchange
