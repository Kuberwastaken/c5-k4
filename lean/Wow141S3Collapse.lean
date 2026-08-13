import FormalConjecturesUtil

/-!
# The `S₃`-to-`Z₃` collapse behind the WOWII 141 cover obstruction

In a three-sheet permutation lift, a short fundamental cycle containing one
cotree edge has monodromy equal to that edge permutation (or its inverse).
Requiring the monodromy to be fixed-point-free therefore forces the generator
into the alternating subgroup `A₃`.  This file records the reusable algebraic
boundary: every fixed-point-free permutation of three letters is one of the
two 3-cycles, arbitrary products stay in the three-element alternating
subgroup, and all such products commute.
-/

namespace Wow141S3Collapse

abbrev S3 := Equiv.Perm (Fin 3)

/-- A permutation has no fixed sheet. -/
def FixedPointFree (σ : S3) : Prop :=
  ∀ i, σ i ≠ i

instance fixedPointFreeDecidable (σ : S3) : Decidable (FixedPointFree σ) := by
  unfold FixedPointFree
  infer_instance

/-- One of the two oriented 3-cycles. -/
def cycle012 : S3 :=
  Equiv.swap (0 : Fin 3) 1 * Equiv.swap (1 : Fin 3) 2

/-- The oppositely oriented 3-cycle. -/
def cycle021 : S3 :=
  cycle012⁻¹

/-- On three letters, the only fixed-point-free permutations are the two
3-cycles. -/
theorem fixedPointFree_classification :
    ∀ σ : S3, FixedPointFree σ ↔ σ = cycle012 ∨ σ = cycle021 := by
  decide

/-- The alternating subgroup on three letters consists exactly of the
identity and the two oriented 3-cycles. -/
theorem alternatingGroup_classification :
    ∀ σ : S3,
      σ ∈ alternatingGroup (Fin 3) ↔
        σ = 1 ∨ σ = cycle012 ∨ σ = cycle021 := by
  intro σ
  rw [Equiv.Perm.mem_alternatingGroup]
  have hsign : ∀ τ : S3,
      Equiv.Perm.sign τ = 1 ↔
        τ = 1 ∨ τ = cycle012 ∨ τ = cycle021 := by
    decide
  exact hsign σ

/-- Fixed-point-free monodromy on three sheets is necessarily even. -/
theorem fixedPointFree_mem_alternatingGroup {σ : S3}
    (hσ : FixedPointFree σ) :
    σ ∈ alternatingGroup (Fin 3) := by
  rw [alternatingGroup_classification σ]
  exact Or.inr (fixedPointFree_classification σ |>.mp hσ)

/-- Conversely, a nonidentity alternating permutation on three sheets is
fixed-point-free. -/
theorem fixedPointFree_of_mem_alternatingGroup_of_ne_one {σ : S3}
    (hσ : σ ∈ alternatingGroup (Fin 3)) (hne : σ ≠ 1) :
    FixedPointFree σ := by
  rw [fixedPointFree_classification σ]
  rcases (alternatingGroup_classification σ).mp hσ with rfl | h
  · exact (hne rfl).elim
  · exact h

/-- Any ordered product of fixed-point-free three-sheet generators remains
inside `A₃`. -/
theorem list_prod_mem_alternatingGroup
    (generators : List S3)
    (hgenerators : ∀ σ ∈ generators, FixedPointFree σ) :
    generators.prod ∈ alternatingGroup (Fin 3) := by
  induction generators with
  | nil => exact Subgroup.one_mem _
  | cons σ generators ih =>
      apply Subgroup.mul_mem
      · exact fixedPointFree_mem_alternatingGroup
          (hgenerators σ (by simp))
      · apply ih
        intro τ hτ
        exact hgenerators τ (by simp [hτ])

/-- Hence every such product is exactly the identity or one of the two
3-cycles. -/
theorem list_prod_classification
    (generators : List S3)
    (hgenerators : ∀ σ ∈ generators, FixedPointFree σ) :
    generators.prod = 1 ∨
      generators.prod = cycle012 ∨ generators.prod = cycle021 := by
  exact (alternatingGroup_classification generators.prod).mp
    (list_prod_mem_alternatingGroup generators hgenerators)

/-- A set of fixed-point-free edge generators generates no permutation
outside `A₃`.  This is the subgroup-level boundary used by a voltage system. -/
theorem closure_le_alternatingGroup
    (generators : Set S3)
    (hgenerators : ∀ σ ∈ generators, FixedPointFree σ) :
    Subgroup.closure generators ≤ alternatingGroup (Fin 3) := by
  apply (Subgroup.closure_le (alternatingGroup (Fin 3))).2
  intro σ hσ
  exact fixedPointFree_mem_alternatingGroup (hgenerators σ hσ)

/-- The three-element alternating subgroup is abelian. -/
theorem alternatingGroup_commute :
    ∀ σ τ : S3,
      σ ∈ alternatingGroup (Fin 3) →
      τ ∈ alternatingGroup (Fin 3) →
      σ * τ = τ * σ := by
  intro σ τ hσ hτ
  rcases (alternatingGroup_classification σ).mp hσ with rfl | rfl | rfl <;>
    rcases (alternatingGroup_classification τ).mp hτ with rfl | rfl | rfl <;>
    decide

/-- Products of two independently ordered fixed-point-free generator lists
commute.  Thus after singleton short-cycle constraints force each edge
generator to be fixed-point-free, no nonabelian degree of freedom remains. -/
theorem fixedPointFree_products_commute
    (left right : List S3)
    (hleft : ∀ σ ∈ left, FixedPointFree σ)
    (hright : ∀ σ ∈ right, FixedPointFree σ) :
    left.prod * right.prod = right.prod * left.prod := by
  exact alternatingGroup_commute left.prod right.prod
    (list_prod_mem_alternatingGroup left hleft)
    (list_prod_mem_alternatingGroup right hright)

/-- The exact obstruction boundary for an ordered cycle product: once every
edge generator is fixed-point-free, asking the product itself to be
fixed-point-free is equivalent to excluding the identity element of `A₃`. -/
theorem product_fixedPointFree_iff_ne_one
    (generators : List S3)
    (hgenerators : ∀ σ ∈ generators, FixedPointFree σ) :
    FixedPointFree generators.prod ↔ generators.prod ≠ 1 := by
  constructor
  · intro hfixed hidentity
    rw [hidentity] at hfixed
    exact hfixed 0 rfl
  · intro hne
    exact fixedPointFree_of_mem_alternatingGroup_of_ne_one
      (list_prod_mem_alternatingGroup generators hgenerators) hne

end Wow141S3Collapse

#print axioms Wow141S3Collapse.fixedPointFree_classification
#print axioms Wow141S3Collapse.closure_le_alternatingGroup
#print axioms Wow141S3Collapse.fixedPointFree_products_commute
#print axioms Wow141S3Collapse.product_fixedPointFree_iff_ne_one
