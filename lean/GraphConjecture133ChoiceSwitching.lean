import GraphConjecture133PivotContacts

/-!
# WOWII 133: choice switching at the geodesic endpoint

The three neighbors of a four-regular geodesic endpoint other than its first
geodesic neighbor are exactly the three possible first handle choices.  A
depth-three candidate contacting index zero is therefore not arbitrary: it is
an alternative first choice.  C4-freeness also makes the forward sets of two
different first choices disjoint.
-/

namespace WrittenOnTheWallII.GraphConjecture133ChoiceSwitching

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- The possible first handle vertices at the head of a nontrivial walk. -/
def firstHandleChoices {u v : V} (G : SimpleGraph V) (p : G.Walk u v)
    [DecidableRel G.Adj] : Finset V :=
  (G.neighborFinset u).erase p.snd

omit [Nonempty V] in
/-- A four-regular endpoint has exactly three possible first handle choices. -/
theorem card_firstHandleChoices_eq_three
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v : V} (p : G.Walk u v)
    (hp : ¬p.Nil) (hreg : G.IsRegularOfDegree 4) :
    (firstHandleChoices G p).card = 3 := by
  have hsnd : p.snd ∈ G.neighborFinset u := by
    simpa using p.adj_snd hp
  unfold firstHandleChoices
  rw [Finset.card_erase_of_mem hsnd, G.card_neighborFinset_eq_degree, hreg u]

omit [Nonempty V] in
/-- Contact with geodesic index zero is exactly membership among the
alternative first choices, provided the candidate is not the geodesic's
second vertex. -/
theorem mem_firstHandleChoices_iff_adj_index_zero
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v a : V}
    (p : G.Walk u v) (hane : a ≠ p.snd) :
    a ∈ firstHandleChoices G p ↔ G.Adj a (p.getVert 0) := by
  simp [firstHandleChoices, G.mem_neighborFinset, hane, Walk.getVert_zero,
    adj_comm]

omit [Nonempty V] in
/-- Thus every index-zero blocker can be pivoted into one of the three first
handle choices. -/
theorem index_zero_contact_is_choice
    (G : SimpleGraph V) [DecidableRel G.Adj] {u v a : V}
    (p : G.Walk u v) (hane : a ≠ p.snd)
    (ha0 : G.Adj a (p.getVert 0)) :
    a ∈ firstHandleChoices G p :=
  (mem_firstHandleChoices_iff_adj_index_zero G p hane).2 ha0

/-- The three forward neighbors of a first choice after removing the endpoint. -/
def secondHandleChoices (G : SimpleGraph V) (u c : V)
    [DecidableRel G.Adj] : Finset V :=
  (G.neighborFinset c).erase u

omit [Nonempty V] in
/-- Different first choices have disjoint forward sets in a C4-free graph.
A common forward vertex would form `u-c₁-b-c₂-u`. -/
theorem secondHandleChoices_disjoint
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {u c₁ c₂ : V}
    (huc₁ : G.Adj u c₁) (huc₂ : G.Adj u c₂) (hc : c₁ ≠ c₂) :
    Disjoint (secondHandleChoices G u c₁) (secondHandleChoices G u c₂) := by
  rw [Finset.disjoint_left]
  intro b hb₁ hb₂
  have hbc₁ : G.Adj b c₁ := by
    simpa [secondHandleChoices, adj_comm] using Finset.mem_of_mem_erase hb₁
  have hbc₂ : G.Adj b c₂ := by
    simpa [secondHandleChoices, adj_comm] using Finset.mem_of_mem_erase hb₂
  apply hc4
  refine ⟨u, c₁, b, c₂, ?_, ?_, ?_, ?_, ?_, ?_,
    huc₁, hbc₁.symm, hbc₂, huc₂.symm⟩
  · exact huc₁.ne
  · exact (Finset.ne_of_mem_erase hb₁).symm
  · exact huc₂.ne
  · exact hbc₁.ne.symm
  · exact hc
  · exact hbc₂.ne

omit [Nonempty V] in
/-- Each first choice in a four-regular graph has exactly three second
choices. -/
theorem card_secondHandleChoices_eq_three
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4) {u c : V} (huc : G.Adj u c) :
    (secondHandleChoices G u c).card = 3 := by
  have humem : u ∈ G.neighborFinset c := by simpa [adj_comm] using huc
  unfold secondHandleChoices
  rw [Finset.card_erase_of_mem humem, G.card_neighborFinset_eq_degree, hreg c]

end WrittenOnTheWallII.GraphConjecture133ChoiceSwitching
