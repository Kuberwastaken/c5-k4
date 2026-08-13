import FormalConjecturesUtil

/-!
# WOWII 133: first metric failure of the Latin ownership model

The capacity-three target is geodesic index zero, hence the common endpoint
itself.  Its outside neighbors are not anonymous slots: after removing the
geodesic successor, they are exactly the three first handle choices.

This identity eliminates the Latin incidence model.  A third adjacent to the
endpoint and owned below two distinct first branches forces a four-cycle in
at least one branch.  The fixed blocker assignment already sends three such
thirds to index zero, so it has no endpoint-prefix realization.
-/

namespace WrittenOnTheWallII.GraphConjecture133EndpointMetricFailure

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

omit [Fintype V] [DecidableEq V] in
/-- In one branch, an endpoint-blocking third must coincide with that
branch's first choice.  Otherwise `u-c-p-z-u` is a four-cycle. -/
theorem endpoint_blocker_forces_first_eq
    {G : SimpleGraph V} (hc4 : ¬HasC4 G)
    {u c p z : V}
    (huc : G.Adj u c) (hcp : G.Adj c p)
    (hpz : G.Adj p z) (hzu : G.Adj z u)
    (hpu : p ≠ u) : z = c := by
  by_contra hzc
  apply hc4
  refine ⟨u, c, p, z, huc.ne, hpu.symm, hzu.ne.symm,
    hcp.ne, (fun hcz ↦ hzc hcz.symm), hpz.ne, huc, hcp, hpz, hzu⟩

omit [Fintype V] [DecidableEq V] in
/-- One endpoint blocker cannot be owned below two distinct first branches. -/
theorem cross_branch_endpoint_blocker_impossible
    {G : SimpleGraph V} (hc4 : ¬HasC4 G)
    {u c₁ c₂ p₁ p₂ z : V}
    (huc₁ : G.Adj u c₁) (huc₂ : G.Adj u c₂)
    (hc₁p₁ : G.Adj c₁ p₁) (hc₂p₂ : G.Adj c₂ p₂)
    (hp₁z : G.Adj p₁ z) (hp₂z : G.Adj p₂ z)
    (hzu : G.Adj z u) (hp₁u : p₁ ≠ u) (hp₂u : p₂ ≠ u)
    (hc : c₁ ≠ c₂) : False := by
  have hz₁ := endpoint_blocker_forces_first_eq
    hc4 huc₁ hc₁p₁ hp₁z hzu hp₁u
  have hz₂ := endpoint_blocker_forces_first_eq
    hc4 huc₂ hc₂p₂ hp₂z hzu hp₂u
  exact hc (hz₁.symm.trans hz₂)

/- The fixed Latin kernel from v0.26, repeated here so this certificate can be
checked directly against the fresh upstream dependency chain. -/

abbrev Branch := Fin 3
abbrev ParentSlot := Fin 3
abbrev ThirdVertex := Fin 9
abbrev Target := Fin 5
abbrev ColoredParent := Branch × ParentSlot

def ownerSlot (b : Branch) (z : ThirdVertex) : ParentSlot :=
  if b.val = 0 then
    ⟨(z.val / 3) % 3, Nat.mod_lt _ (by omega)⟩
  else if b.val = 1 then
    ⟨z.val % 3, Nat.mod_lt _ (by omega)⟩
  else
    ⟨((z.val / 3) + (z.val % 3)) % 3, Nat.mod_lt _ (by omega)⟩

def parentOwns (q : ColoredParent) (z : ThirdVertex) : Prop :=
  ownerSlot q.1 z = q.2

def blockerTarget : ThirdVertex → Target :=
  ![0, 3, 1, 1, 0, 3, 4, 2, 0]

def targetCapacity (x : Target) : ℕ :=
  if x.val = 0 then 3 else 2

def blockedThirdsFor (blocker : ThirdVertex → Target)
    (x : Target) : Finset ThirdVertex :=
  Finset.univ.filter fun z ↦ blocker z = x

def blockedThirds (x : Target) : Finset ThirdVertex :=
  blockedThirdsFor blockerTarget x

/-- The fixed Latin assignment uses three endpoint blocker slots. -/
theorem three_thirds_block_index_zero :
    (blockedThirds 0).card = 3 := by
  decide

/-- Even abstractly, nine blockers cannot fit into four internal targets of
capacity two unless at least one blocker uses index zero. -/
theorem endpoint_blocker_is_capacity_forced
    {n₀ n₁ n₂ n₃ n₄ : ℕ}
    (hsum : n₀ + n₁ + n₂ + n₃ + n₄ = 9)
    (h₁ : n₁ ≤ 2) (h₂ : n₂ ≤ 2) (h₃ : n₃ ≤ 2) (h₄ : n₄ ≤ 2) :
    0 < n₀ := by
  omega

/-- Function-level capacity form: every assignment of all nine thirds to the
five target prefixes, with internal capacities two, uses target zero. -/
theorem exists_index_zero_blocker_of_capacities
    (blocker : ThirdVertex → Target)
    (hcap : ∀ x : Target,
      (blockedThirdsFor blocker x).card ≤ targetCapacity x) :
    ∃ z : ThirdVertex, blocker z = 0 := by
  by_contra h
  have hno : ∀ z : ThirdVertex, blocker z ≠ 0 := by
    intro z hz
    exact h ⟨z, hz⟩
  let internal : Finset Target := Finset.univ.erase 0
  have hmaps : ∀ z ∈ (Finset.univ : Finset ThirdVertex),
      blocker z ∈ internal := by
    intro z _hz
    simp [internal, hno z]
  have hfiber : ∀ x ∈ internal,
      ((Finset.univ : Finset ThirdVertex).filter fun z ↦ blocker z = x).card ≤ 2 := by
    intro x hx
    have hx0 : x ≠ 0 := Finset.ne_of_mem_erase hx
    simpa [blockedThirdsFor, targetCapacity, hx0] using hcap x
  have hcard := Finset.card_le_mul_card_image_of_maps_to hmaps 2 hfiber
  have hthirdCard : (Finset.univ : Finset ThirdVertex).card = 9 := by
    decide
  have hinternalCard : internal.card = 4 := by
    decide
  rw [hthirdCard, hinternalCard] at hcard
  omega

/-- Data required to embed the fixed incidence kernel at the first geodesic
prefix `u--x₁`.  The last clause identifies blocker target zero with `u`.
The parent freshness clause is exactly membership in the second-choice set
after erasing `u`. -/
def EndpointPrefixRealizationFor
    (blocker : ThirdVertex → Target)
    (G : SimpleGraph V) (u x₁ : V)
    (first : Branch → V) (parent : ColoredParent → V)
    (third : ThirdVertex → V) : Prop :=
  G.Adj u x₁ ∧
  (∀ b : Branch, G.Adj u (first b)) ∧
  (∀ b : Branch, first b ≠ x₁) ∧
  Function.Injective first ∧
  (∀ q : ColoredParent, G.Adj (first q.1) (parent q)) ∧
  (∀ q : ColoredParent, parent q ≠ u) ∧
  (∀ q : ColoredParent, ∀ z : ThirdVertex,
    parentOwns q z → G.Adj (parent q) (third z)) ∧
  (∀ z : ThirdVertex,
    blocker z = 0 → G.Adj (third z) u)

def EndpointPrefixRealization
    (G : SimpleGraph V) (u x₁ : V)
    (first : Branch → V) (parent : ColoredParent → V)
    (third : ThirdVertex → V) : Prop :=
  EndpointPrefixRealizationFor blockerTarget G u x₁ first parent third

omit [Fintype V] [DecidableEq V] in
/-- No capacity-respecting blocker reassignment repairs the Latin kernel. -/
theorem no_endpointPrefixRealizationFor_of_latin_kernel
    (blocker : ThirdVertex → Target)
    (hcap : ∀ x : Target,
      (blockedThirdsFor blocker x).card ≤ targetCapacity x)
    (G : SimpleGraph V) (hc4 : ¬HasC4 G)
    (u x₁ : V) (first : Branch → V) (parent : ColoredParent → V)
    (third : ThirdVertex → V) :
    ¬EndpointPrefixRealizationFor blocker G u x₁ first parent third := by
  intro hreal
  obtain ⟨z, htarget⟩ := exists_index_zero_blocker_of_capacities blocker hcap
  rcases hreal with ⟨_hux₁, hufirst, _hfirstx₁, hfirstInj,
    hfirstParent, hparentFresh, hparentThird, hblockEndpoint⟩
  let q₀ : ColoredParent := (0, ownerSlot 0 z)
  let q₁ : ColoredParent := (1, ownerSlot 1 z)
  have howns₀ : parentOwns q₀ z := by
    rfl
  have howns₁ : parentOwns q₁ z := by
    rfl
  have hzfirst₀ : third z = first 0 :=
    endpoint_blocker_forces_first_eq hc4
      (hufirst 0)
      (by simpa [q₀] using hfirstParent q₀)
      (hparentThird q₀ z howns₀)
      (hblockEndpoint z htarget)
      (hparentFresh q₀)
  have hzfirst₁ : third z = first 1 :=
    endpoint_blocker_forces_first_eq hc4
      (hufirst 1)
      (by simpa [q₁] using hfirstParent q₁)
      (hparentThird q₁ z howns₁)
      (hblockEndpoint z htarget)
      (hparentFresh q₁)
  have h01 : (0 : Branch) ≠ 1 := by decide
  apply h01
  apply hfirstInj
  exact hzfirst₀.symm.trans hzfirst₁

omit [Fintype V] [DecidableEq V] in
/-- Exact noncompletion certificate: the v0.26 Latin kernel with its fixed
blocker assignment cannot realize even the first geodesic prefix in a
C4-free graph.  The proof uses only third `0` and branches `0` and `1`. -/
theorem no_endpointPrefixRealization_of_latin_kernel
    (G : SimpleGraph V) (hc4 : ¬HasC4 G)
    (u x₁ : V) (first : Branch → V) (parent : ColoredParent → V)
    (third : ThirdVertex → V) :
    ¬EndpointPrefixRealization G u x₁ first parent third := by
  refine no_endpointPrefixRealizationFor_of_latin_kernel blockerTarget ?_
    G hc4 u x₁ first parent third
  intro x
  fin_cases x <;> decide

end WrittenOnTheWallII.GraphConjecture133EndpointMetricFailure
