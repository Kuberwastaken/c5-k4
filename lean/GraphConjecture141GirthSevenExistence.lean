import GraphConjecture141GirthSeven

/-!
# WOWII 141: existence reduction at a maximum local center

This file constructs `DistanceTwoLeafData` rather than assuming it.  The two
remaining graph-level inputs are stated exactly: every neighborhood is
independent, and a center attaining maximum local independence has a
distance-two vertex with a unique attachment back into that neighborhood.
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthSevenExistence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141GirthSeven

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- All open neighborhoods are independent.  This is the exact local
consequence of triangle-freeness needed by the construction. -/
def LocallyIndependent (G : SimpleGraph V) : Prop :=
  ∀ v, G.IsIndepSet (G.neighborSet v)

/-- At any center attaining the global local-independence maximum, there is a
genuine distance-two vertex whose only attachment back into the center's
neighborhood is the chosen middle vertex. -/
def MaximumCenterDistanceTwoLeafProperty
    (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v, indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G) →
    ∃ u x : V,
      G.Adj v u ∧ G.Adj u x ∧ x ≠ v ∧ ¬G.Adj v x ∧
      ∀ a ∈ G.neighborFinset v, G.Adj x a → a = u

/-- The irreducible existence input: every maximizing center starts a simple
two-edge path to a nonneighbor.  Girth supplies uniqueness separately. -/
def MaximumCenterHasDistanceTwoPath
    (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v, indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G) →
    ∃ u x : V, G.Adj v u ∧ G.Adj u x ∧ x ≠ v ∧ ¬G.Adj v x

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A two-step attachment is unique back into the center's neighborhood when
girth is at least six: a second attachment would make a 4-cycle. -/
lemma unique_neighbor_attachment_of_six_le_girth
    (G : SimpleGraph V) (hgirth : 6 ≤ G.girth)
    {v u x : V} (hvu : G.Adj v u) (hux : G.Adj u x)
    (hxv : x ≠ v) :
    ∀ a ∈ G.neighborSet v, G.Adj x a → a = u := by
  intro a hva hxa
  by_contra hau
  have huv : u ≠ v := hvu.ne.symm
  have hax : a ≠ x := hxa.ne.symm
  have huxne : u ≠ x := hux.ne
  have hav : a ≠ v := hva.ne.symm
  have hvxne : v ≠ x := hxv.symm
  have hxvne : x ≠ v := hxv
  have hxu : x ≠ u := hux.ne.symm
  have hua : u ≠ a := fun h => hau h.symm
  have hxa_ne : x ≠ a := hxa.ne
  let c : G.Walk v v :=
    .cons hvu (.cons hux (.cons hxa (.cons hva.symm .nil)))
  have hc : c.IsCycle := by
    simp [c, Walk.isCycle_def, Walk.isTrail_def, huv, huxne, hua,
      hav, hvxne, hxvne, hxa_ne]
  have := G.girth_le_length hc
  simp [c] at this
  omega

omit [DecidableEq V] [Nonempty V] in
/-- At girth at least six, an ordinary two-edge witness already has the
unique-neighborhood property required by the splice. -/
theorem maximumCenterDistanceTwoLeafProperty_of_six_le_girth
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirth : 6 ≤ G.girth)
    (hpath : MaximumCenterHasDistanceTwoPath G) :
    MaximumCenterDistanceTwoLeafProperty G := by
  intro v hvmax
  obtain ⟨u, x, hvu, hux, hxv, hvx⟩ := hpath v hvmax
  refine ⟨u, x, hvu, hux, hxv, hvx, ?_⟩
  intro a ha hxa
  apply unique_neighbor_attachment_of_six_le_girth G hgirth hvu hux hxv
  · simpa [G.mem_neighborFinset] using ha
  · exact hxa

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Girth at least six forces every open neighborhood to be independent. -/
lemma locallyIndependent_of_six_le_girth
    (G : SimpleGraph V) (hgirth : 6 ≤ G.girth) :
    LocallyIndependent G := by
  intro v a ha b hb hab habAdj
  let c : G.Walk v v :=
    .cons ha (.cons habAdj (.cons hb.symm .nil))
  have hc : c.IsCycle := by
    simp [c, Walk.isCycle_def, Walk.isTrail_def,
      hab, ha.ne, hb.ne, ha.ne.symm, hb.ne.symm]
  have := G.girth_le_length hc
  simp [c] at this
  omega

omit [Nonempty V] [DecidableEq V] in
/-- If the whole open neighborhood is independent, its local independence
number is its degree. -/
lemma indepNeighborsCard_eq_degree_of_independent_neighborhood
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hN : G.IsIndepSet (G.neighborSet v)) :
    indepNeighborsCard G v = G.degree v := by
  unfold indepNeighborsCard
  rw [← G.card_neighborSet_eq_degree]
  symm
  apply maximumIndepSet_card_eq_indepNum
  constructor
  · intro x _hx y _hy hxy
    change ¬G.Adj x.val y.val
    exact hN x.property y.property (Subtype.coe_injective.ne hxy)
  · intro t _ht
    exact Finset.card_le_univ t

omit [DecidableEq V] in
/-- The finite maximum in the WOWII statement is attained by a vertex. -/
lemma exists_maximum_local_center (G : SimpleGraph V) :
    ∃ v : V,
      indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G) := by
  obtain ⟨v, _hv, hv⟩ :=
    Finset.exists_mem_eq_sup (Finset.univ : Finset V) Finset.univ_nonempty
      (indepNeighborsCard G)
  exact ⟨v, hv.symm⟩

/-- Local independence plus the sharply isolated distance-two property
constructs the complete `DistanceTwoLeafData` package at an attained maximum
center. -/
theorem exists_distanceTwoLeafData
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hlocal : LocallyIndependent G)
    (hleaf : MaximumCenterDistanceTwoLeafProperty G) :
    Nonempty (DistanceTwoLeafData G) := by
  obtain ⟨v, hvmax⟩ := exists_maximum_local_center G
  obtain ⟨u, x, hvu, hux, hxv, hvx, hunique⟩ := hleaf v hvmax
  refine ⟨{
    center := v
    localSet := G.neighborFinset v
    extra := x
    attachment := u
    localIndependent := ?_
    localSubset := Finset.Subset.rfl
    localCard := ?_
    centerMaximal := hvmax
    attachment_mem := ?_
    extra_not_mem := ?_
    center_extra_nonadj := hvx
    extra_unique_local := ?_
  }⟩
  · simpa [← coe_neighborFinset] using hlocal v
  · rw [G.card_neighborFinset_eq_degree]
    exact (indepNeighborsCard_eq_degree_of_independent_neighborhood
      G v (hlocal v)).symm
  · simpa [G.mem_neighborFinset] using hvu
  · simp only [Finset.mem_insert, not_or]
    refine ⟨hxv, ?_⟩
    intro hxN
    exact hvx (by simpa [G.mem_neighborFinset] using hxN)
  · intro a ha
    constructor
    · exact hunique a ha
    · intro hau
      subst a
      exact hux.symm

/-- Exact upstream-shaped WOWII 141 for girth six or seven, reduced to the
two precise structural consequences expected from the girth hypothesis. -/
theorem conjecture141_of_girth_six_or_seven_of_local_properties
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 6 ≤ G.girth) (hgirthUpper : G.girth ≤ 7)
    (hlocal : LocallyIndependent G)
    (hleaf : MaximumCenterDistanceTwoLeafProperty G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  let D := Classical.choice (exists_distanceTwoLeafData G hlocal hleaf)
  exact conjecture141_of_girth_six_or_seven_of_distanceTwoLeafData
    G hgirthLower hgirthUpper D

/-- The final reduced theorem: girth supplies every chord-exclusion fact, so
only existence of a simple two-edge path from a maximizing center remains as
an explicit hypothesis. -/
theorem conjecture141_of_girth_six_or_seven_of_maximumCenterHasDistanceTwoPath
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 6 ≤ G.girth) (hgirthUpper : G.girth ≤ 7)
    (hpath : MaximumCenterHasDistanceTwoPath G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  apply conjecture141_of_girth_six_or_seven_of_local_properties
    G hgirthLower hgirthUpper
  · exact locallyIndependent_of_six_le_girth G hgirthLower
  · exact maximumCenterDistanceTwoLeafProperty_of_six_le_girth
      G hgirthLower hpath

end WrittenOnTheWallII.GraphConjecture141GirthSevenExistence
