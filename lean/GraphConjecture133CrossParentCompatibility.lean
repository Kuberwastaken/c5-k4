import FormalConjecturesUtil

/-!
# WOWII 133: cross-parent neighborhood compatibility

In a C4-free graph, two distinct vertices have at most one common neighbor.
Consequently, two saturated parents have third-choice sets intersecting in at
most one vertex.  The modular colored ownership profile instead gives
intersection size three for every cross-branch same-slot parent pair, so this
constraint eliminates that model whenever those parents are distinct graph
vertices.
-/

namespace WrittenOnTheWallII.GraphConjecture133CrossParentCompatibility

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Four distinct vertices forming a not-necessarily-induced four-cycle. -/
def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

/-- Distinct vertices in a C4-free graph have at most one common neighbor. -/
theorem card_common_neighbors_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {p q : V} (hpq : p ≠ q) :
    ((G.neighborFinset p) ∩ (G.neighborFinset q)).card ≤ 1 := by
  apply Finset.card_le_one.mpr
  intro a ha b hb
  simp only [Finset.mem_inter] at ha hb
  have hpa : G.Adj p a := by simpa using ha.1
  have hqa : G.Adj q a := by simpa using ha.2
  have hpb : G.Adj p b := by simpa using hb.1
  have hqb : G.Adj q b := by simpa using hb.2
  by_contra hab
  apply hc4
  refine ⟨p, a, q, b, ?_, ?_, ?_, ?_, ?_, ?_,
    hpa, hqa.symm, hqb, hpb.symm⟩
  · exact hpa.ne
  · exact hpq
  · exact hpb.ne
  · exact hqa.ne.symm
  · exact hab
  · exact hqb.ne

/-- Three explicit third choices of a parent. -/
def thirdTriple (z₁ z₂ z₃ : V) : Finset V := {z₁, z₂, z₃}

/-- If both explicit triples lie in the corresponding saturated-parent
neighborhoods, their intersection has size at most one. -/
theorem card_thirdTriple_inter_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {p q : V} (hpq : p ≠ q)
    {a₁ a₂ a₃ b₁ b₂ b₃ : V}
    (hpa₁ : G.Adj p a₁) (hpa₂ : G.Adj p a₂) (hpa₃ : G.Adj p a₃)
    (hqb₁ : G.Adj q b₁) (hqb₂ : G.Adj q b₂) (hqb₃ : G.Adj q b₃) :
    ((thirdTriple a₁ a₂ a₃) ∩ (thirdTriple b₁ b₂ b₃)).card ≤ 1 := by
  have hsub : (thirdTriple a₁ a₂ a₃) ∩ (thirdTriple b₁ b₂ b₃) ⊆
      (G.neighborFinset p) ∩ (G.neighborFinset q) := by
    intro x hx
    simp only [Finset.mem_inter] at hx ⊢
    constructor
    · simp only [thirdTriple, Finset.mem_insert, Finset.mem_singleton] at hx
      rcases hx.1 with rfl | rfl | rfl
      · simpa using hpa₁
      · simpa using hpa₂
      · simpa using hpa₃
    · simp only [thirdTriple, Finset.mem_insert, Finset.mem_singleton] at hx
      rcases hx.2 with rfl | rfl | rfl
      · simpa using hqb₁
      · simpa using hqb₂
      · simpa using hqb₃
  exact (Finset.card_le_card hsub).trans
    (card_common_neighbors_le_one G hc4 hpq)

omit [Fintype V] [DecidableEq V] in
/-- Two different parents cannot share two named third vertices. -/
theorem not_two_shared_thirds
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {p q a b : V}
    (hpq : p ≠ q) (hab : a ≠ b)
    (hpa : G.Adj p a) (hpb : G.Adj p b)
    (hqa : G.Adj q a) (hqb : G.Adj q b) : False := by
  apply hc4
  refine ⟨p, a, q, b, hpa.ne, hpq, hpb.ne,
    hqa.ne.symm, hab, hqb.ne, hpa, hqa.symm, hqb, hpb.symm⟩

omit [Fintype V] in
/-- Equality case: one shared third is compatible with the C4-free bound. -/
theorem singleton_intersection_is_allowed_by_bound
    {a b c d e : V}
    (hab : a ≠ b) (hac : a ≠ c)
    (had : a ≠ d) (hae : a ≠ e)
    (hbd : b ≠ d) (hbe : b ≠ e)
    (hcd : c ≠ d) (hce : c ≠ e) :
    ((thirdTriple a b c) ∩ (thirdTriple a d e)).card = 1 := by
  simp [thirdTriple, hab, hac, had, hae, hbd, hbe, hcd, hce]

/- ## Abstract colored ownership check -/

abbrev Branch := Fin 3
abbrev ParentSlot := Fin 3
abbrev ThirdVertex := Fin 9

def ownedThirds (_b : Branch) (p : ParentSlot) : Finset ThirdVertex :=
  Finset.univ.filter fun z ↦ z.val % 3 = p.val

/-- The v0.22 modular profile assigns the same three third vertices to the
same parent slot in each branch. -/
theorem colored_same_slot_intersection_three
    (b₁ b₂ : Branch) (p : ParentSlot) :
    ((ownedThirds b₁ p) ∩ (ownedThirds b₂ p)).card = 3 := by
  fin_cases p <;> simp [ownedThirds] <;> decide +revert

/-- Therefore the modular colored ownership profile violates the genuine C4-
free cross-parent bound whenever same-slot parents in different branches are
distinct graph vertices. -/
theorem modular_profile_incompatible_with_distinct_same_slot_parents
    (b₁ b₂ : Branch) (p : ParentSlot) :
    ¬((ownedThirds b₁ p) ∩ (ownedThirds b₂ p)).card ≤ 1 := by
  rw [colored_same_slot_intersection_three]
  omega

end WrittenOnTheWallII.GraphConjecture133CrossParentCompatibility
