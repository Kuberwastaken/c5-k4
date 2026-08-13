import FormalConjecturesUtil

/-!
# WOWII 133: cross-branch parent distinctness

Two distinct first choices adjacent to the same endpoint cannot share a second
parent in a C4-free graph.  Combining this with the common-neighbor bound shows
that any cross-branch parent pair shares at most one third vertex.
-/

namespace WrittenOnTheWallII.GraphConjecture133CrossBranchParents

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

omit [Fintype V] [DecidableEq V] in
/-- Distinct endpoint branches cannot merge at their second parent. -/
theorem crossBranch_secondParents_ne
    {G : SimpleGraph V} (hc4 : ¬HasC4 G)
    {u c₁ c₂ p₁ p₂ : V}
    (huc₁ : G.Adj u c₁) (huc₂ : G.Adj u c₂)
    (hc₁p₁ : G.Adj c₁ p₁) (hc₂p₂ : G.Adj c₂ p₂)
    (hc : c₁ ≠ c₂) (hp₁u : p₁ ≠ u) : p₁ ≠ p₂ := by
  intro hp
  subst p₂
  apply hc4
  refine ⟨u, c₁, p₁, c₂, ?_, ?_, ?_, ?_, ?_, ?_,
    huc₁, hc₁p₁, hc₂p₂.symm, huc₂.symm⟩
  · exact huc₁.ne
  · exact hp₁u.symm
  · exact huc₂.ne
  · exact hc₁p₁.ne
  · exact hc
  · exact hc₂p₂.ne.symm

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
  refine ⟨p, a, q, b, hpa.ne, hpq, hpb.ne,
    hqa.ne.symm, hab, hqb.ne, hpa, hqa.symm, hqb, hpb.symm⟩

/-- Full branch-to-third composition: second parents selected below distinct
first branches share at most one third neighbor. -/
theorem crossBranch_commonThirds_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G)
    {u c₁ c₂ p₁ p₂ : V}
    (huc₁ : G.Adj u c₁) (huc₂ : G.Adj u c₂)
    (hc₁p₁ : G.Adj c₁ p₁) (hc₂p₂ : G.Adj c₂ p₂)
    (hc : c₁ ≠ c₂) (hp₁u : p₁ ≠ u) :
    ((G.neighborFinset p₁) ∩ (G.neighborFinset p₂)).card ≤ 1 := by
  exact card_common_neighbors_le_one G hc4
    (crossBranch_secondParents_ne hc4 huc₁ huc₂ hc₁p₁ hc₂p₂ hc hp₁u)

omit [Fintype V] [DecidableEq V] in
/-- Two named shared thirds are already impossible across endpoint branches. -/
theorem crossBranch_not_two_sharedThirds
    {G : SimpleGraph V}
    (hc4 : ¬HasC4 G)
    {u c₁ c₂ p₁ p₂ a b : V}
    (huc₁ : G.Adj u c₁) (huc₂ : G.Adj u c₂)
    (hc₁p₁ : G.Adj c₁ p₁) (hc₂p₂ : G.Adj c₂ p₂)
    (hc : c₁ ≠ c₂) (hp₁u : p₁ ≠ u) (hab : a ≠ b)
    (hp₁a : G.Adj p₁ a) (hp₁b : G.Adj p₁ b)
    (hp₂a : G.Adj p₂ a) (hp₂b : G.Adj p₂ b) : False := by
  have hp := crossBranch_secondParents_ne hc4 huc₁ huc₂ hc₁p₁ hc₂p₂ hc hp₁u
  apply hc4
  refine ⟨p₁, a, p₂, b, hp₁a.ne, hp, hp₁b.ne,
    hp₂a.ne.symm, hab, hp₂b.ne, hp₁a, hp₂a.symm, hp₂b, hp₁b.symm⟩

/- Abstract same-slot ownership design from the earlier colored profile. -/

abbrev Branch := Fin 3
abbrev ParentSlot := Fin 3
abbrev ThirdVertex := Fin 9

def ownedThirds (_b : Branch) (p : ParentSlot) : Finset ThirdVertex :=
  Finset.univ.filter fun z ↦ z.val % 3 = p.val

theorem repeated_sameSlot_owns_three
    (b₁ b₂ : Branch) (p : ParentSlot) :
    ((ownedThirds b₁ p) ∩ (ownedThirds b₂ p)).card = 3 := by
  fin_cases p <;> simp [ownedThirds] <;> decide +revert

/-- Final abstract incompatibility: repeated same-slot ownership cannot satisfy
the graph-derived cross-branch intersection bound. -/
theorem repeated_sameSlot_ownership_eliminated
    (b₁ b₂ : Branch) (p : ParentSlot) :
    ¬((ownedThirds b₁ p) ∩ (ownedThirds b₂ p)).card ≤ 1 := by
  rw [repeated_sameSlot_owns_three]
  omega

end WrittenOnTheWallII.GraphConjecture133CrossBranchParents
