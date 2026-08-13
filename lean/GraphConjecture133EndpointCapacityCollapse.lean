import FormalConjecturesUtil

/-!
# WOWII 133: endpoint exclusion collapses the blocker budget

Typing target zero as the common endpoint removes all three of its apparent
blocker slots.  A genuine third choice adjacent to that endpoint would form
the four-cycle `u-c-p-z-u`.  Consequently only the four internal targets,
with total outside capacity eight, remain.

This file combines that graph fact with same-branch C4 overlap control,
degree-four neighborhood completion, and the multiplicity accounting.  The
strongest remaining profile `(3,0,8)` is eliminated, and in fact the same
eight-slot inequality is incompatible with every 27-incidence profile of
multiplicity at most three.
-/

namespace WrittenOnTheWallII.GraphConjecture133EndpointCapacityCollapse

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

omit [Fintype V] [DecidableEq V] in
/-- A genuine third choice cannot contact geodesic index zero. -/
theorem third_choice_not_adj_endpoint
    {G : SimpleGraph V} (hc4 : ¬HasC4 G)
    {u c p z : V}
    (huc : G.Adj u c) (hcp : G.Adj c p) (hpz : G.Adj p z)
    (hpu : p ≠ u) (hzc : z ≠ c) : ¬G.Adj z u := by
  intro hzu
  apply hc4
  refine ⟨u, c, p, z, huc.ne, hpu.symm, hzu.ne.symm,
    hcp.ne, hzc.symm, hpz.ne, huc, hcp, hpz, hzu⟩

omit [Fintype V] [DecidableEq V] in
/-- Same-branch third sets are disjoint: two distinct second parents below one
first choice cannot own the same genuine third. -/
theorem same_branch_parents_cannot_share_third
    {G : SimpleGraph V} (hc4 : ¬HasC4 G)
    {c p₁ p₂ z : V}
    (hcp₁ : G.Adj c p₁) (hcp₂ : G.Adj c p₂)
    (hp₁z : G.Adj p₁ z) (hp₂z : G.Adj p₂ z)
    (hp : p₁ ≠ p₂) (hzc : z ≠ c) : False := by
  apply hc4
  refine ⟨c, p₁, z, p₂, hcp₁.ne, hzc.symm, hcp₂.ne,
    hp₁z.ne, hp, hp₂z.ne.symm, hcp₁, hp₁z, hp₂z.symm, hcp₂.symm⟩

/-- Across branches, two distinct parents can share at most one third. -/
theorem distinct_parents_common_neighbors_le_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {p q : V} (hpq : p ≠ q) :
    ((G.neighborFinset p) ∩ (G.neighborFinset q)).card ≤ 1 := by
  apply Finset.card_le_one.mpr
  intro z₁ hz₁ z₂ hz₂
  simp only [Finset.mem_inter] at hz₁ hz₂
  have hpz₁ : G.Adj p z₁ := by simpa using hz₁.1
  have hqz₁ : G.Adj q z₁ := by simpa using hz₁.2
  have hpz₂ : G.Adj p z₂ := by simpa using hz₂.1
  have hqz₂ : G.Adj q z₂ := by simpa using hz₂.2
  by_contra hz
  apply hc4
  refine ⟨p, z₁, q, z₂, hpz₁.ne, hpq, hpz₂.ne,
    hqz₁.ne.symm, hz, hqz₂.ne, hpz₁, hqz₁.symm, hqz₂, hpz₂.symm⟩

/-- Four explicit distinct neighbors exhaust a degree-four neighborhood. -/
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
  have hknown : ({a, b, c, d} : Finset V).card = 4 := by
    simp [hab, hac, had, hbc, hbd, hcd]
  have hneighbors : (G.neighborFinset v).card = 4 := by
    rw [G.card_neighborFinset_eq_degree, hreg v]
  exact Finset.Subset.antisymm
    (fun x hx ↦ by
      have hle := Finset.eq_of_subset_of_card_le hsub (by
        rw [hneighbors, hknown])
      simpa [hle] using hx)
    hsub

/-- Endpoint plus three second choices saturate a first-choice vertex. -/
theorem first_choice_neighborhood_exhausted
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4)
    {c u p₀ p₁ p₂ : V}
    (hup₀ : u ≠ p₀) (hup₁ : u ≠ p₁) (hup₂ : u ≠ p₂)
    (hp₀₁ : p₀ ≠ p₁) (hp₀₂ : p₀ ≠ p₂) (hp₁₂ : p₁ ≠ p₂)
    (hcu : G.Adj c u) (hcp₀ : G.Adj c p₀)
    (hcp₁ : G.Adj c p₁) (hcp₂ : G.Adj c p₂) :
    G.neighborFinset c = {u, p₀, p₁, p₂} :=
  neighborFinset_eq_four_known G hreg hup₀ hup₁ hup₂ hp₀₁ hp₀₂ hp₁₂
    hcu hcp₀ hcp₁ hcp₂

/- ## Exact aggregate collapse -/

def MultiplicityAccounting (n₁ n₂ n₃ : ℕ) : Prop :=
  n₁ + 2 * n₂ + 3 * n₃ = 27

/-- Same-branch disjointness across three branches makes multiplicity three
the maximum, so 27 incidences require at least nine distinct thirds. -/
theorem nine_le_distinct_thirds
    {n₁ n₂ n₃ : ℕ} (hinc : MultiplicityAccounting n₁ n₂ n₃) :
    9 ≤ n₁ + n₂ + n₃ := by
  unfold MultiplicityAccounting at hinc
  omega

/-- Once target zero is unavailable, the four internal target prefixes offer
only eight blocker edges. -/
theorem internal_target_capacity_le_eight
    {m₁ m₂ m₃ m₄ : ℕ}
    (h₁ : m₁ ≤ 2) (h₂ : m₂ ≤ 2) (h₃ : m₃ ≤ 2) (h₄ : m₄ ≤ 2) :
    m₁ + m₂ + m₃ + m₄ ≤ 8 := by
  omega

/-- The strongest remaining profile has eleven distinct thirds.  If all are
blocked within the five capacities, all three endpoint slots and every
internal slot must be used. -/
theorem profile_3_0_8_forces_full_target_capacity
    {e m₁ m₂ m₃ m₄ : ℕ}
    (hblock : e + m₁ + m₂ + m₃ + m₄ = 11)
    (he : e ≤ 3) (h₁ : m₁ ≤ 2) (h₂ : m₂ ≤ 2)
    (h₃ : m₃ ≤ 2) (h₄ : m₄ ≤ 2) :
    e = 3 ∧ m₁ = 2 ∧ m₂ = 2 ∧ m₃ = 2 ∧ m₄ = 2 := by
  omega

/-- Since genuine thirds cannot use endpoint slots, the `(3,0,8)` profile is
arithmetically impossible after the graph-level endpoint exclusion. -/
theorem profile_3_0_8_eliminated
    {e m₁ m₂ m₃ m₄ : ℕ}
    (hblock : e + m₁ + m₂ + m₃ + m₄ = 11)
    (hnoEndpoint : e = 0)
    (h₁ : m₁ ≤ 2) (h₂ : m₂ ≤ 2)
    (h₃ : m₃ ≤ 2) (h₄ : m₄ ≤ 2) : False := by
  omega

/-- Stronger profile-independent conclusion: no multiplicity profile carrying
27 third incidences can fit into the eight internal blocker slots. -/
theorem no_multiplicity_profile_fits_internal_targets
    {n₁ n₂ n₃ : ℕ}
    (hinc : MultiplicityAccounting n₁ n₂ n₃)
    (hinternal : n₁ + n₂ + n₃ ≤ 8) : False := by
  have := nine_le_distinct_thirds hinc
  omega

/-- Exact six-profile corollary after the already eliminated `(0,0,9)` case.
Each remaining aggregate profile has more than eight distinct thirds. -/
theorem remaining_six_profiles_exceed_internal_capacity
    {n₁ n₂ n₃ : ℕ}
    (hprofiles :
      (n₁ = 0 ∧ n₂ = 3 ∧ n₃ = 7) ∨
      (n₁ = 0 ∧ n₂ = 6 ∧ n₃ = 5) ∨
      (n₁ = 1 ∧ n₂ = 1 ∧ n₃ = 8) ∨
      (n₁ = 1 ∧ n₂ = 4 ∧ n₃ = 6) ∨
      (n₁ = 2 ∧ n₂ = 2 ∧ n₃ = 7) ∨
      (n₁ = 3 ∧ n₂ = 0 ∧ n₃ = 8)) :
    9 < n₁ + n₂ + n₃ := by
  rcases hprofiles with h | h | h | h | h | h <;> omega

end WrittenOnTheWallII.GraphConjecture133EndpointCapacityCollapse
