import FormalConjecturesUtil

/-!
# Independent domination for clique centers with private leaves

For positive private-leaf counts `p i`, the structural choices are: select no
center and therefore every leaf, or select one center `i` and every leaf owned
by the other centers.  This module proves the resulting minimum-cost formula
and supplies an honest certificate adapter to `indepDominationNumber`.
-/

namespace IndependentDominationPrivateLeaves

open SimpleGraph

universe u v

/-- Cost of the two structural forms: `none` means all leaves, while `some i`
means center `i` together with every leaf owned by the other centers. -/
def privateLeafCost {ι : Type u} [Fintype ι] [DecidableEq ι]
    (p : ι → ℕ) : Option ι → ℕ
  | none => ∑ i, p i
  | some i => 1 + ((∑ j, p j) - p i)

/-- Every structural choice costs at least `1 + total - maximum`.  Positivity
of the maximum is exactly what also handles the no-center/all-leaves choice. -/
theorem privateLeafCost_lower
    {ι : Type u} [Fintype ι] [DecidableEq ι]
    (p : ι → ℕ) (M : ℕ)
    (hMpos : 1 ≤ M)
    (hMsum : M ≤ ∑ i, p i)
    (hmax : ∀ i, p i ≤ M) :
    ∀ choice, 1 + ((∑ i, p i) - M) ≤ privateLeafCost p choice := by
  intro choice
  cases choice with
  | none =>
      simp only [privateLeafCost]
      omega
  | some i =>
      simp only [privateLeafCost]
      exact Nat.add_le_add_left (Nat.sub_le_sub_left (hmax i) (∑ j, p j)) 1

/-- Choosing a center with the maximum number of private leaves attains the
lower bound. -/
theorem privateLeafCost_at_max
    {ι : Type u} [Fintype ι] [DecidableEq ι]
    (p : ι → ℕ) (M : ℕ) (i : ι) (hi : p i = M) :
    privateLeafCost p (some i) = 1 + ((∑ j, p j) - M) := by
  simp [privateLeafCost, hi]

/-- A graph-specific certificate isolates the only construction-dependent
work. `classify` says every independent dominating set is no cheaper than a
modeled center choice; `realize` supplies a set for every modeled choice. -/
structure PrivateLeafCertificate
    {V : Type v} [Fintype V] [DecidableEq V]
    {ι : Type u} [Fintype ι] [DecidableEq ι]
    (G : SimpleGraph V) (p : ι → ℕ) : Prop where
  classify : ∀ n (D : Finset V), G.IsNIndepDominatingSet n D →
    ∃ choice, privateLeafCost p choice ≤ n
  realize : ∀ choice, ∃ D : Finset V,
    G.IsNIndepDominatingSet (privateLeafCost p choice) D

/-- Generic bridge from an explicit witness and a universal lower bound to
the `sInf` definition of independent domination. -/
theorem indepDominationNumber_eq_of_certificate
    {V : Type v} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (k : ℕ)
    (hwitness : ∃ D : Finset V, G.IsNIndepDominatingSet k D)
    (hlower : ∀ n (D : Finset V), G.IsNIndepDominatingSet n D → k ≤ n) :
    G.indepDominationNumber = k := by
  unfold SimpleGraph.indepDominationNumber
  apply le_antisymm
  · exact csInf_le ⟨0, fun _ _ ↦ Nat.zero_le _⟩ hwitness
  · apply le_csInf
    · exact ⟨k, hwitness⟩
    · intro n hn
      obtain ⟨D, hD⟩ := hn
      exact hlower n D hD

/-- The exact private-leaf formula follows from a supplied structural
certificate and an attained positive maximum leaf count. -/
theorem indepDominationNumber_eq_privateLeafFormula
    {V : Type v} [Fintype V] [DecidableEq V]
    {ι : Type u} [Fintype ι] [DecidableEq ι]
    (G : SimpleGraph V) (p : ι → ℕ) (M : ℕ) (imax : ι)
    (hcert : PrivateLeafCertificate G p)
    (hMpos : 1 ≤ M)
    (hMsum : M ≤ ∑ i, p i)
    (hmax : ∀ i, p i ≤ M)
    (hattain : p imax = M) :
    G.indepDominationNumber = 1 + ((∑ i, p i) - M) := by
  apply indepDominationNumber_eq_of_certificate
  · rw [← privateLeafCost_at_max p M imax hattain]
    exact hcert.realize (some imax)
  · intro n D hD
    obtain ⟨choice, hchoice⟩ := hcert.classify n D hD
    exact (privateLeafCost_lower p M hMpos hMsum hmax choice).trans hchoice

/-- The private-leaf profile of the frozen transferred graph. -/
def transferredProfile : Fin 5 → ℕ := ![4, 6, 5, 5, 5]

theorem transferredProfile_sum : ∑ i, transferredProfile i = 25 := by
  decide

theorem transferredProfile_le_six : ∀ i, transferredProfile i ≤ 6 := by
  intro i
  fin_cases i <;> decide

theorem transferredProfile_one_eq_six : transferredProfile 1 = 6 := by
  decide

/-- Exact arithmetic/graph adapter: any graph carrying the supplied structural
certificate for `(4,6,5,5,5)` has independent domination number 20. -/
theorem transferredProfile_indepDominationNumber_eq_twenty
    {V : Type v} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V)
    (hcert : PrivateLeafCertificate G transferredProfile) :
    G.indepDominationNumber = 20 := by
  have hformula := indepDominationNumber_eq_privateLeafFormula
    G transferredProfile 6 (1 : Fin 5) hcert (by omega) (by norm_num [transferredProfile_sum])
      transferredProfile_le_six transferredProfile_one_eq_six
  norm_num [transferredProfile_sum] at hformula ⊢
  exact hformula

#print axioms privateLeafCost_lower
#print axioms privateLeafCost_at_max
#print axioms indepDominationNumber_eq_of_certificate
#print axioms indepDominationNumber_eq_privateLeafFormula
#print axioms transferredProfile_indepDominationNumber_eq_twenty

end IndependentDominationPrivateLeaves
