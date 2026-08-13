import GraphConjecture59ResidueThreshold

/-!
# WOWII 59: multiplicity forced by a deletion-critical `3+3` core

The degree-only route cannot control residue.  This file instead records the
exact internal degree multiplicity of a `3+3` bipartite core whose every
five-vertex deletion still contains a cycle.
-/

namespace WrittenOnTheWallII.GraphConjecture59CoreProfileMultiplicity

open SimpleGraph Finset

/-- A four-edge rectangle gives an explicit four-cycle. -/
theorem four_cycle_not_acyclic
    {V : Type*} (G : SimpleGraph V) (a b c d : V)
    (hab : G.Adj a b) (hbc : G.Adj b c)
    (hcd : G.Adj c d) (hda : G.Adj d a)
    (habv : a ≠ b) (hacv : a ≠ c) (hadv : a ≠ d)
    (hbcv : b ≠ c) (hbdv : b ≠ d) (hcdv : c ≠ d) :
    ¬G.IsAcyclic := by
  intro hacyclic
  let p : G.Walk a a :=
    Walk.cons hab (Walk.cons hbc (Walk.cons hcd (Walk.cons hda Walk.nil)))
  apply hacyclic p
  rw [Walk.isCycle_def]
  simp [p, habv, hacv, hadv, hbcv, hbdv, hcdv, ne_comm]

/-- The nine possible cross-edges of a labeled `3+3` core, encoded by a
nine-bit mask. -/
def edge (m : Fin 512) (i j : Fin 3) : Bool :=
  Nat.testBit m.val (3 * i.val + j.val)

/-- Internal degree of a left-side core vertex. -/
def rowDegree (m : Fin 512) (i : Fin 3) : ℕ :=
  (univ.filter fun j ↦ edge m i j).card

/-- Internal degree of a right-side core vertex. -/
def colDegree (m : Fin 512) (j : Fin 3) : ℕ :=
  (univ.filter fun i ↦ edge m i j).card

/-- Number of cross-edges in the labeled core. -/
def edgeCount (m : Fin 512) : ℕ :=
  ∑ i, rowDegree m i

/-- Number of the six core vertices having internal degree three. -/
def degreeThreeCount (m : Fin 512) : ℕ :=
  (univ.filter fun i ↦ rowDegree m i = 3).card +
  (univ.filter fun j ↦ colDegree m j = 3).card

/-- A `K₂,₂` rectangle in the cross-edge matrix. -/
def Rectangle (m : Fin 512) (i₁ i₂ j₁ j₂ : Fin 3) : Prop :=
  i₁ ≠ i₂ ∧ j₁ ≠ j₂ ∧
  edge m i₁ j₁ ∧ edge m i₁ j₂ ∧
  edge m i₂ j₁ ∧ edge m i₂ j₂

instance (m : Fin 512) (i₁ i₂ j₁ j₂ : Fin 3) :
    Decidable (Rectangle m i₁ i₂ j₁ j₂) := by
  unfold Rectangle
  infer_instance

/-- First of the two indices surviving deletion of `i`. -/
def nextIndex (i : Fin 3) : Fin 3 :=
  ⟨(i.val + 1) % 3, Nat.mod_lt _ (by decide)⟩

/-- Second of the two indices surviving deletion of `i`. -/
def previousIndex (i : Fin 3) : Fin 3 :=
  ⟨(i.val + 2) % 3, Nat.mod_lt _ (by decide)⟩

/-- Exact matrix form of deletion criticality: after deleting any left or
right core vertex, the remaining `2+3` or `3+2` matrix still contains a
rectangle, hence a four-cycle. -/
def DeletionCritical (m : Fin 512) : Prop :=
  (∀ d : Fin 3, 2 ≤
    (univ.filter fun j ↦
      edge m (nextIndex d) j && edge m (previousIndex d) j).card) ∧
  (∀ d : Fin 3, 2 ≤
    (univ.filter fun i ↦
      edge m i (nextIndex d) && edge m i (previousIndex d)).card)

instance (m : Fin 512) : Decidable (DeletionCritical m) := by
  unfold DeletionCritical
  infer_instance

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
/-- **Exact full-profile constraint.** Deletion criticality is equivalent to
having at least eight of the nine cross-edges.  Consequently every internal
degree is at least two and at least four core vertices have internal degree
three.  The only profiles are `[3,3,3,3,3,3]` and `[3,3,3,3,2,2]`. -/
theorem deletionCritical_profile : ∀ m : Fin 512,
    (DeletionCritical m ↔ 8 ≤ edgeCount m) ∧
    (DeletionCritical m →
      (edgeCount m = 8 ∨ edgeCount m = 9) ∧
      (∀ i, 2 ≤ rowDegree m i) ∧
      (∀ j, 2 ≤ colDegree m j) ∧
      4 ≤ degreeThreeCount m ∧
      (edgeCount m = 9 → degreeThreeCount m = 6) ∧
      (edgeCount m = 8 → degreeThreeCount m = 4 ∧
        (univ.filter fun i ↦ rowDegree m i = 2).card +
        (univ.filter fun j ↦ colDegree m j = 2).card = 2)) := by
  decide

end WrittenOnTheWallII.GraphConjecture59CoreProfileMultiplicity
