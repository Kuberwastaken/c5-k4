import GraphConjecture19DiameterBaseline

/-!
# WOWII 19/13: canonical retained geodesic tail
-/

namespace WrittenOnTheWallII.GraphConjecture19CanonicalTail

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Retained indices `0,2,3,...,length`. -/
def retainedIndices {G : SimpleGraph V} {u v : V} (p : G.Walk u v) : Finset ℕ :=
  insert 0 (Finset.Icc 2 p.length)

/-- The canonical retained tail `x₀,x₂,...,x_d`. -/
def canonicalTail {G : SimpleGraph V} {u v : V} (p : G.Walk u v) : Finset V :=
  (retainedIndices p).image p.getVert

omit [Fintype V] [DecidableEq V] in
lemma mem_retainedIndices_iff {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (i : ℕ) :
    i ∈ retainedIndices p ↔ i = 0 ∨ (2 ≤ i ∧ i ≤ p.length) := by
  simp [retainedIndices]

omit [Fintype V] [DecidableEq V] in
lemma zero_mem_retainedIndices {G : SimpleGraph V} {u v : V} (p : G.Walk u v) :
    0 ∈ retainedIndices p := by simp [retainedIndices]

omit [Fintype V] [DecidableEq V] in
lemma card_retainedIndices {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hlen : 2 ≤ p.length) :
    (retainedIndices p).card = p.length := by
  rw [retainedIndices, card_insert_of_notMem]
  · simp [Nat.card_Icc]
    omega
  · simp

omit [Fintype V] [DecidableEq V] in
/-- A path is injective on all retained indices. -/
lemma getVert_injOn_retainedIndices {G : SimpleGraph V} {u v : V}
    (p : G.Walk u v) (hpPath : p.IsPath) :
    Set.InjOn p.getVert (retainedIndices p : Set ℕ) := by
  intro i hi j hj hij
  apply hpPath.getVert_injOn
  · rw [Finset.mem_coe] at hi
    show i ≤ p.length
    rcases (mem_retainedIndices_iff p i).mp hi with rfl | hi
    · omega
    · exact hi.2
  · rw [Finset.mem_coe] at hj
    show j ≤ p.length
    rcases (mem_retainedIndices_iff p j).mp hj with rfl | hj
    · omega
    · exact hj.2
  · exact hij

omit [Fintype V] in
/-- The canonical tail has exactly `length` vertices. -/
lemma card_canonicalTail {G : SimpleGraph V} {u v : V}
    (p : G.Walk u v) (hpPath : p.IsPath) (hlen : 2 ≤ p.length) :
    (canonicalTail p).card = p.length := by
  rw [canonicalTail, Finset.card_image_iff.mpr]
  · exact card_retainedIndices p hlen
  · intro i hi j hj hij
    exact getVert_injOn_retainedIndices p hpPath hi hj hij

omit [Fintype V] in
/-- Every canonical-tail vertex is the endpoint or a non-neighbor of it. -/
lemma canonicalTail_outside_openNeighborhood
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (q : V) (hq : q ∈ canonicalTail p) :
    q = u ∨ ¬G.Adj u q := by
  obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hq
  rcases (mem_retainedIndices_iff p i).mp hi with rfl | hi
  · exact Or.inl p.getVert_zero
  · refine Or.inr ?_
    have h := _root_.WrittenOnTheWallII.GraphConjecture19DiameterBaseline.not_adj_getVert_of_add_two_le
      p hp (i := 0) (j := i) (by omega) hi.2
    simpa only [p.getVert_zero] using h

omit [Fintype V] in
/-- At a diametral endpoint, the canonical tail already supplies the exact
cardinality and outside-neighborhood halves of the endpoint certificate. -/
theorem canonicalTail_card_and_outside_of_diametral
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hpPath : p.IsPath) (hp : p.length = G.dist u v)
    (hdiam : G.dist u v = G.diam) (hlen : 2 ≤ G.diam) :
    (canonicalTail p).card = G.diam ∧
      ∀ q ∈ canonicalTail p, q = u ∨ ¬G.Adj u q := by
  constructor
  · rw [card_canonicalTail p hpPath (by omega), hp, hdiam]
  · exact fun q hq => canonicalTail_outside_openNeighborhood p hp q hq

end WrittenOnTheWallII.GraphConjecture19CanonicalTail
