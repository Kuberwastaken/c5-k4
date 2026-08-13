import FormalConjecturesUtil

/-!
# WOWII 133: degree-four completion boundary

Four known distinct neighbors exhaust a vertex in a four-regular graph.  In
the colored third-layer configuration this means both a second parent and a
blocked multiplicity-three third vertex are already saturated.  Degree
completion therefore forbids, rather than forces, an additional parent--target
contact.
-/

namespace WrittenOnTheWallII.GraphConjecture133DegreeCompletion

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Four explicit distinct neighbors exhaust the neighborhood of a degree-four
vertex. -/
theorem neighborFinset_eq_four_known
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {v a b c d : V}
    (hab : a ≠ b) (hac : a ≠ c) (had : a ≠ d)
    (hbc : b ≠ c) (hbd : b ≠ d) (hcd : c ≠ d)
    (hva : G.Adj v a) (hvb : G.Adj v b)
    (hvc : G.Adj v c) (hvd : G.Adj v d) :
    G.neighborFinset v = {a, b, c, d} := by
  have hsub : ({a, b, c, d} : Finset V) ⊆ G.neighborFinset v := by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_singleton] at hx
    rcases hx with rfl | rfl | rfl | rfl
    · simpa using hva
    · simpa using hvb
    · simpa using hvc
    · simpa using hvd
  have hcardKnown : ({a, b, c, d} : Finset V).card = 4 := by
    simp [hab, hac, had, hbc, hbd, hcd]
  have hcardNeighbor : (G.neighborFinset v).card = 4 := by
    rw [G.card_neighborFinset_eq_degree, hreg v]
  exact (Finset.eq_of_subset_of_card_le hsub (by
    rw [hcardNeighbor, hcardKnown])).symm

/-- Any fifth candidate is excluded once four known neighbors are fixed. -/
theorem not_adj_of_four_known
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {v a b c d x : V}
    (hab : a ≠ b) (hac : a ≠ c) (had : a ≠ d)
    (hbc : b ≠ c) (hbd : b ≠ d) (hcd : c ≠ d)
    (hva : G.Adj v a) (hvb : G.Adj v b)
    (hvc : G.Adj v c) (hvd : G.Adj v d)
    (hxa : x ≠ a) (hxb : x ≠ b) (hxc : x ≠ c) (hxd : x ≠ d) :
    ¬G.Adj v x := by
  intro hvx
  have hxmem : x ∈ G.neighborFinset v := by simpa using hvx
  rw [neighborFinset_eq_four_known G hreg hab hac had hbc hbd hcd
    hva hvb hvc hvd] at hxmem
  simp [hxa, hxb, hxc, hxd] at hxmem

/-- A second parent has its first-choice neighbor and three third choices;
these four vertices exhaust its degree. -/
theorem parent_neighborhood_exhausted
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {p first z₁ z₂ z₃ : V}
    (hf₁ : first ≠ z₁) (hf₂ : first ≠ z₂) (hf₃ : first ≠ z₃)
    (hz₁₂ : z₁ ≠ z₂) (hz₁₃ : z₁ ≠ z₃) (hz₂₃ : z₂ ≠ z₃)
    (hpf : G.Adj p first) (hp₁ : G.Adj p z₁)
    (hp₂ : G.Adj p z₂) (hp₃ : G.Adj p z₃) :
    G.neighborFinset p = {first, z₁, z₂, z₃} :=
  neighborFinset_eq_four_known G hreg hf₁ hf₂ hf₃ hz₁₂ hz₁₃ hz₂₃
    hpf hp₁ hp₂ hp₃

/-- Consequently, a geodesic target outside those four known vertices cannot
contact the parent.  No triangle-free, C4-free, or metric assumption is needed
beyond the stated distinctness. -/
theorem parent_forbids_extra_target
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {p first z₁ z₂ z₃ target : V}
    (hf₁ : first ≠ z₁) (hf₂ : first ≠ z₂) (hf₃ : first ≠ z₃)
    (hz₁₂ : z₁ ≠ z₂) (hz₁₃ : z₁ ≠ z₃) (hz₂₃ : z₂ ≠ z₃)
    (hpf : G.Adj p first) (hp₁ : G.Adj p z₁)
    (hp₂ : G.Adj p z₂) (hp₃ : G.Adj p z₃)
    (htf : target ≠ first) (ht₁ : target ≠ z₁)
    (ht₂ : target ≠ z₂) (ht₃ : target ≠ z₃) :
    ¬G.Adj p target :=
  not_adj_of_four_known G hreg hf₁ hf₂ hf₃ hz₁₂ hz₁₃ hz₂₃
    hpf hp₁ hp₂ hp₃ htf ht₁ ht₂ ht₃

/-- A multiplicity-three blocked third vertex is likewise saturated by its
three owning parents and one blocker target. -/
theorem triple_blocker_neighborhood_exhausted
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {z p₁ p₂ p₃ target : V}
    (hp₁₂ : p₁ ≠ p₂) (hp₁₃ : p₁ ≠ p₃) (hp₁t : p₁ ≠ target)
    (hp₂₃ : p₂ ≠ p₃) (hp₂t : p₂ ≠ target) (hp₃t : p₃ ≠ target)
    (hz₁ : G.Adj z p₁) (hz₂ : G.Adj z p₂)
    (hz₃ : G.Adj z p₃) (hzt : G.Adj z target) :
    G.neighborFinset z = {p₁, p₂, p₃, target} :=
  neighborFinset_eq_four_known G hreg hp₁₂ hp₁₃ hp₁t hp₂₃ hp₂t hp₃t
    hz₁ hz₂ hz₃ hzt

/-- Degree-four completion cannot provide the positive parent--target contact
needed to eliminate the colored empty-contact model: for every fully specified
parent, that contact is formally impossible. -/
theorem degree_completion_reinforces_empty_contact
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {p first z₁ z₂ z₃ target : V}
    (hf₁ : first ≠ z₁) (hf₂ : first ≠ z₂) (hf₃ : first ≠ z₃)
    (hz₁₂ : z₁ ≠ z₂) (hz₁₃ : z₁ ≠ z₃) (hz₂₃ : z₂ ≠ z₃)
    (hpf : G.Adj p first) (hp₁ : G.Adj p z₁)
    (hp₂ : G.Adj p z₂) (hp₃ : G.Adj p z₃)
    (htf : target ≠ first) (ht₁ : target ≠ z₁)
    (ht₂ : target ≠ z₂) (ht₃ : target ≠ z₃) :
    ¬G.Adj p target :=
  parent_forbids_extra_target G hreg hf₁ hf₂ hf₃ hz₁₂ hz₁₃ hz₂₃
    hpf hp₁ hp₂ hp₃ htf ht₁ ht₂ ht₃

end WrittenOnTheWallII.GraphConjecture133DegreeCompletion
