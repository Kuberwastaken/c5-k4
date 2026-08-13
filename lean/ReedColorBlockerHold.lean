import FormalConjecturesUtil

/-!
# Reed color-blocker hold certificate

This file freezes the sixteen-vertex graph found by the prospective Reed
color-blocker search.  Vertices `0,...,14` form `C₅[K₃]`; vertex `15` is
adjacent to `0,1,2,3,4,6,9,12,13`.

The search did not find a counterexample.  Instead, the explicit certificates
below prove the strongest source-shaped conclusion needed here: this graph
satisfies Reed's inequality.  We deliberately use only one-sided certificates
(`χ ≤ 8`, `6 ≤ ω`, and `9 ≤ Δ`), rather than claiming exact invariant values
that are unnecessary for the conclusion.
-/

namespace ReedColorBlockerHold

open SimpleGraph

/-- Two bags of the carrier lie next to one another on its five-cycle. -/
private def CycleAdjacent (a b : ℕ) : Prop :=
  (a + 1) % 5 = b ∨ (b + 1) % 5 = a

/-- The neighbors of the added color-blocking vertex. -/
private def IsBlockerNeighbor (v : Fin 16) : Prop :=
  v.val ∈ [0, 1, 2, 3, 4, 6, 9, 12, 13]

/-- Symmetric, loop-free adjacency relation for the frozen graph. -/
private def EdgeRel (u v : Fin 16) : Prop :=
  u ≠ v ∧
    ((u.val < 15 ∧ v.val < 15 ∧
        (u.val / 3 = v.val / 3 ∨ CycleAdjacent (u.val / 3) (v.val / 3))) ∨
      (u.val = 15 ∧ IsBlockerNeighbor v) ∨
      (v.val = 15 ∧ IsBlockerNeighbor u))

/-- `C₅[K₃]` together with the added nine-neighbor color blocker. -/
def graph : SimpleGraph (Fin 16) where
  Adj := EdgeRel
  symm := by
    intro u v huv
    rcases huv with ⟨hne, hcarrier | hblocker | hblocker⟩
    · refine ⟨hne.symm, Or.inl ⟨hcarrier.2.1, hcarrier.1, ?_⟩⟩
      rcases hcarrier.2.2 with hsame | hcycle
      · exact Or.inl hsame.symm
      · exact Or.inr (hcycle.elim Or.inr Or.inl)
    · exact ⟨hne.symm, Or.inr (Or.inr hblocker)⟩
    · exact ⟨hne.symm, Or.inr (Or.inl hblocker)⟩
  loopless := by
    intro v hvv
    exact hvv.1 rfl

instance : DecidableRel graph.Adj := by
  intro u v
  change Decidable (EdgeRel u v)
  unfold EdgeRel IsBlockerNeighbor CycleAdjacent
  infer_instance

/-- The explicit coloring returned by the exact search, in vertex order. -/
def color (v : Fin 16) : Fin 8 :=
  if v = 0 then 0
  else if v = 1 then 1
  else if v = 2 then 2
  else if v = 3 then 3
  else if v = 4 then 4
  else if v = 5 then 5
  else if v = 6 then 1
  else if v = 7 then 2
  else if v = 8 then 6
  else if v = 9 then 0
  else if v = 10 then 5
  else if v = 11 then 7
  else if v = 12 then 3
  else if v = 13 then 4
  else if v = 14 then 6
  else 5

/-- The displayed map is a proper eight-coloring. -/
def eightColoring : graph.Coloring (Fin 8) :=
  ⟨color, by decide⟩

/-- The first two adjacent carrier bags give the displayed six-clique. -/
def sixClique : Finset (Fin 16) := {0, 1, 2, 3, 4, 5}

/-- Direct certificate that the displayed six vertices are pairwise adjacent. -/
lemma sixClique_isClique : graph.IsClique sixClique := by
  decide

/-- Vertex zero has the nine certified neighbors
`1,2,3,4,5,12,13,14,15`. -/
lemma degree_zero : graph.degree 0 = 9 := by
  decide

/-- The color blocker really destroys claw-freeness: center `0` and leaves
`15,5,14` induce a claw. -/
lemma induced_claw_certificate :
    graph.Adj 0 15 ∧ graph.Adj 0 5 ∧ graph.Adj 0 14 ∧
      ¬graph.Adj 15 5 ∧ ¬graph.Adj 15 14 ∧ ¬graph.Adj 5 14 := by
  decide

/-- The frozen color-blocker graph satisfies the doubled, denominator-free
form of Reed's bound. -/
theorem reed_bound :
    2 * graph.chromaticNumber ≤ graph.cliqueNum + graph.maxDegree + 2 := by
  have hchi : graph.chromaticNumber ≤ (8 : ℕ∞) :=
    (show graph.Colorable 8 from ⟨eightColoring⟩).chromaticNumber_le
  have homega : 6 ≤ graph.cliqueNum := by
    simpa [sixClique] using sixClique_isClique.card_le_cliqueNum
  have hDelta : 9 ≤ graph.maxDegree := by
    rw [← degree_zero]
    exact graph.degree_le_maxDegree 0
  have homega' : (6 : ℕ∞) ≤ graph.cliqueNum := by
    exact_mod_cast homega
  have hDelta' : (9 : ℕ∞) ≤ graph.maxDegree := by
    exact_mod_cast hDelta
  calc
    2 * graph.chromaticNumber ≤ 2 * (8 : ℕ∞) := by gcongr
    _ ≤ (6 : ℕ∞) + 9 + 2 := by norm_num
    _ ≤ graph.cliqueNum + graph.maxDegree + 2 := by gcongr

end ReedColorBlockerHold
