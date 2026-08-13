import GraphConjecture19ConsecutiveEdgeStructure
import GraphConjecture19CenterEqualityIncidence

/-!
# WOWII 19/13: locating the full-independent witness in consecutive geometry
-/

namespace WrittenOnTheWallII.GraphConjecture19ConsecutiveWitnessLocation

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19CenterCharge
open WrittenOnTheWallII.GraphConjecture19CenterEqualityIncidence

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The five exact positions of a vertex relative to a geodesic whose added
edge occurs between indices `i` and `i+1`. -/
inductive ConsecutiveWitnessPosition
    {G : SimpleGraph V} {a b : V} (D : TreePlusOneEdge G)
    (p : G.Walk a b) (c v : V) (i : ℕ) : Prop
  | extraLeft : v = D.extraLeft → ConsecutiveWitnessPosition D p c v i
  | extraRight : v = D.extraRight → ConsecutiveWitnessPosition D p c v i
  | leftArm (j : ℕ) : j < i → p.getVert j = v →
      ConsecutiveWitnessPosition D p c v i
  | rightArm (j : ℕ) : i + 1 < j → j ≤ p.length → p.getVert j = v →
      ConsecutiveWitnessPosition D p c v i
  | offGeodesic : v ∉ p.support.toFinset → G.Adj c v →
      ConsecutiveWitnessPosition D p c v i

/-- Every vertex occupies exactly one of the five coarse locations once the
added endpoints are fixed at consecutive indices and the path/neighborhood
cover is saturated. -/
theorem locate_vertex_in_consecutive_geometry
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b)
    (c v : V) {i : ℕ}
    (hiLeft : p.getVert i = D.extraLeft)
    (hiRight : p.getVert (i + 1) = D.extraRight)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ) :
    ConsecutiveWitnessPosition D p c v i := by
  by_cases hvP : v ∈ p.support.toFinset
  · obtain ⟨j, hjv, hjLength⟩ := Walk.mem_support_iff_exists_getVert.mp
      (List.mem_toFinset.mp hvP)
    rcases lt_trichotomy j i with hji | hji | hij
    · exact ConsecutiveWitnessPosition.leftArm j hji hjv
    · apply ConsecutiveWitnessPosition.extraLeft
      rw [← hjv, hji, hiLeft]
    · rcases eq_or_lt_of_le (show i + 1 ≤ j by omega) with hEq | hlt
      · apply ConsecutiveWitnessPosition.extraRight
        rw [← hjv, ← hEq, hiRight]
      · exact ConsecutiveWitnessPosition.rightArm j hlt hjLength hjv
  · apply ConsecutiveWitnessPosition.offGeodesic hvP
    have hvCover : v ∈ p.support.toFinset ∪ G.neighborFinset c := by
      rw [hsat]
      simp
    have hvN := (Finset.mem_union.mp hvCover).resolve_left hvP
    simpa [mem_neighborFinset] using hvN

/-- Under the sole remaining numerical obstruction `localMax=maxDegree`, a
maximum-degree vertex with a fully independent neighborhood exists in one of
the five exact positions. -/
theorem exists_full_independent_witness_with_position
    {G : SimpleGraph V} [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b)
    (c : V) {i : ℕ}
    (hiLeft : p.getVert i = D.extraLeft)
    (hiRight : p.getVert (i + 1) = D.extraRight)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hEq : localMax G = G.maxDegree) :
    ∃ v : V,
      G.degree v = G.maxDegree ∧
      G.IsIndepSet (G.neighborSet v) ∧
      ConsecutiveWitnessPosition D p c v i := by
  obtain ⟨v, hvDegree, hvFull⟩ :=
    exists_maxDegree_vertex_with_full_local_independence G hEq
  have hvIndep := neighborSet_independent_of_indepNeighborsCard_eq_degree
    G v hvFull
  exact ⟨v, hvDegree, hvIndep,
    locate_vertex_in_consecutive_geometry
      D p c v hiLeft hiRight hsat⟩

/-- Expanded disjunction form for downstream branch proofs. -/
theorem full_independent_witness_five_way_split
    {G : SimpleGraph V} [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b)
    (c : V) {i : ℕ}
    (hiLeft : p.getVert i = D.extraLeft)
    (hiRight : p.getVert (i + 1) = D.extraRight)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hEq : localMax G = G.maxDegree) :
    ∃ v : V,
      G.degree v = G.maxDegree ∧
      G.IsIndepSet (G.neighborSet v) ∧
      (v = D.extraLeft ∨ v = D.extraRight ∨
        (∃ j : ℕ, j < i ∧ p.getVert j = v) ∨
        (∃ j : ℕ, i + 1 < j ∧ j ≤ p.length ∧ p.getVert j = v) ∨
        (v ∉ p.support.toFinset ∧ G.Adj c v)) := by
  obtain ⟨v, hvDegree, hvIndep, hvPos⟩ :=
    exists_full_independent_witness_with_position
      D p c hiLeft hiRight hsat hEq
  refine ⟨v, hvDegree, hvIndep, ?_⟩
  cases hvPos with
  | extraLeft hv => exact Or.inl hv
  | extraRight hv => exact Or.inr (Or.inl hv)
  | leftArm j hj hjv => exact Or.inr (Or.inr (Or.inl ⟨j, hj, hjv⟩))
  | rightArm j hjLower hjLength hjv =>
      exact Or.inr (Or.inr (Or.inr (Or.inl ⟨j, hjLower, hjLength, hjv⟩)))
  | offGeodesic hvP hcv =>
      exact Or.inr (Or.inr (Or.inr (Or.inr ⟨hvP, hcv⟩)))

end WrittenOnTheWallII.GraphConjecture19ConsecutiveWitnessLocation
