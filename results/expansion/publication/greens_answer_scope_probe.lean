import FormalConjecturesUtil
/-!
# Probe: `green_24` and `green_16` pin a non-constant quantity to one closed value
Definitions copied verbatim from upstream `main` @ 638da20e.
-/

open Filter Finset

-- ############################ Green 24 ############################
namespace Green24

noncomputable def max013AffineTranslates (n : ℕ) : ℕ :=
  sSup { k |
    ∃ A : Finset ℤ,
      A.card = n ∧
      k = ((A ×ˢ A).filter (fun (x, y) ↦ x ≠ y ∧ x + 3 * (y - x) ∈ A)).card
  }

theorem max013_zero : max013AffineTranslates 0 = 0 := by
  have h : { k | ∃ A : Finset ℤ, A.card = 0 ∧
      k = ((A ×ˢ A).filter (fun (x, y) ↦ x ≠ y ∧ x + 3 * (y - x) ∈ A)).card } = {0} := by
    ext k
    constructor
    · rintro ⟨A, hA, rfl⟩
      rw [Finset.card_eq_zero.mp hA]
      simp
    · rintro rfl
      exact ⟨∅, by simp, by simp⟩
  rw [max013AffineTranslates, h, csSup_singleton]

theorem max013_three : 1 ≤ max013AffineTranslates 3 := by
  apply le_csSup
  · refine ⟨9, ?_⟩
    rintro k ⟨A, hA, rfl⟩
    calc ((A ×ˢ A).filter (fun (x, y) ↦ x ≠ y ∧ x + 3 * (y - x) ∈ A)).card
        ≤ (A ×ˢ A).card := Finset.card_filter_le _ _
      _ = A.card * A.card := Finset.card_product _ _
      _ = 9 := by rw [hA]
  · exact ⟨({0, 1, 3} : Finset ℤ), by decide, by decide⟩

/-- Hence no closed `a : ℕ` satisfies upstream `green_24 : ∀ n, max013AffineTranslates n = a`. -/
theorem green_24_no_closed_answer : ¬ ∃ a : ℕ, ∀ n, max013AffineTranslates n = a := by
  rintro ⟨a, ha⟩
  have h0 := ha 0
  have h3 := ha 3
  rw [max013_zero] at h0
  rw [← h0] at h3
  have := max013_three
  omega

end Green24

-- ############################ Green 16 ############################
namespace Green16

def SolutionFree (A : Finset ℕ) : Prop :=
  ∀ x ∈ A, ∀ y ∈ A, ∀ z ∈ A, ∀ w ∈ A,
    [x, y, z, w].Nodup →
    x + 3 * y ≠ 2 * z + 2 * w

/-- Upstream `green_16` with a closed answer `a : ℕ` is refutable: `N = 0` forces `a = 0`
and `N = 1` forces `1 ≤ a`. -/
theorem green_16_no_closed_answer : ¬ ∃ a : ℕ, ∀ N : ℕ,
    ∃ A : Finset ℕ, A ⊆ Finset.Icc 1 N ∧ SolutionFree A ∧
      A.card = a ∧
      MaximalFor (fun B => B ⊆ Finset.Icc 1 N ∧ SolutionFree B) Finset.card A := by
  rintro ⟨a, ha⟩
  -- `N = 0`: `Icc 1 0 = ∅`, so the only candidate is `∅` and `a = 0`.
  obtain ⟨A0, hA0sub, -, hA0card, -⟩ := ha 0
  have hA0 : A0 = ∅ := Finset.subset_empty.mp (by simpa using hA0sub)
  have ha0 : a = 0 := by rw [← hA0card, hA0]; simp
  -- `N = 1`: `{1}` is a solution-free subset of `Icc 1 1` of cardinality `1`.
  obtain ⟨A1, -, -, hA1card, hA1max⟩ := ha 1
  have hsub : ({1} : Finset ℕ) ⊆ Finset.Icc 1 1 := by decide
  have hsf : SolutionFree ({1} : Finset ℕ) := by
    intro x hx y hy z hz w hw hnd
    simp only [Finset.mem_singleton] at hx hy hz hw
    subst hx; subst hy; subst hz; subst hw
    simp at hnd
  have hle : A1.card ≤ ({1} : Finset ℕ).card := by
    rw [hA1card, ha0]; simp
  have := hA1max.2 ⟨hsub, hsf⟩ hle
  rw [hA1card, ha0] at this
  simp at this

end Green16

Definitions copied verbatim from upstream `main` @ 638da20e. -/

namespace Green37
open Set Filter

def IsAPCover (A : Set ℕ) (N k : ℕ) : Prop := ∀ d, 1 ≤ d ∧ d ≤ N → Set.ContainsAP A k d

noncomputable def m (N k : ℕ) : ℕ :=
  sInf { m | ∃ A : Finset ℕ, A.card = m ∧ IsAPCover (A : Set ℕ) N k }

/-- A `0`-term AP is the empty set, so every set is a `0`-cover. -/
theorem apCover_zero (A : Set ℕ) (N : ℕ) : IsAPCover A N 0 := by
  intro d _
  exact ⟨0, ∅, Set.empty_subset _, by simp⟩

/-- Hence `0` is least for `k = 0`. -/
theorem zero_mem (N : ℕ) : (0 : ℕ) ∈ { m | ∃ A : Finset ℕ, A.card = m ∧ IsAPCover (A : Set ℕ) N 0 } :=
  ⟨∅, rfl, by simpa using apCover_zero _ N⟩

/-- For `k = 2` and `N ≥ 1` the empty set is not a cover: a `2`-term AP is nonempty. -/
theorem empty_not_cover (N : ℕ) (hN : 1 ≤ N) : ¬ IsAPCover (∅ : Set ℕ) N 2 := by
  intro h
  obtain ⟨a, s, hs, hcard, -⟩ := h 1 ⟨le_refl 1, hN⟩
  rw [Set.subset_empty_iff] at hs
  subst hs
  simp at hcard

/-- Upstream `green_37` admits no closed answer: `(N, k) = (1, 0)` forces `0`, which fails at
`(N, k) = (1, 2)`. -/
theorem green_37_no_closed_answer :
    ¬ ∃ a : ℕ, ∀ N k : ℕ, IsLeast { m | ∃ A : Finset ℕ, A.card = m ∧ IsAPCover (A : Set ℕ) N k } a := by
  rintro ⟨a, ha⟩
  have h0 : a = 0 := Nat.le_zero.mp ((ha 1 0).2 (zero_mem 1))
  obtain ⟨A, hAcard, hAcov⟩ := (ha 1 2).1
  rw [h0, Finset.card_eq_zero] at hAcard
  subst hAcard
  exact empty_not_cover 1 le_rfl (by simpa using hAcov)

end Green37

namespace Green37b
open Set Filter Green37

/-- `m N 0 = 0` for every `N`. -/
theorem m_zero (N : ℕ) : m N 0 = 0 := Nat.sInf_eq_zero.mpr (Or.inl (zero_mem N))

/-- For `1 ≤ N` the empty set is not a `1`-cover: a `1`-term AP is a singleton. -/
theorem empty_not_cover_one (N : ℕ) (hN : 1 ≤ N) : ¬ IsAPCover (∅ : Set ℕ) N 1 := by
  intro h
  obtain ⟨a, s, hs, hap⟩ := h 1 ⟨le_rfl, hN⟩
  rw [Set.subset_empty_iff] at hs
  subst hs
  rw [show ((1 : ℕ) : ℕ∞) = 1 from rfl, Set.IsAPOfLengthWith.one] at hap
  exact (Set.singleton_ne_empty a) hap.symm

/-- `{0}` is a `1`-cover, so the `1`-cover set is nonempty. -/
theorem one_cover_nonempty (N : ℕ) :
    { m | ∃ A : Finset ℕ, A.card = m ∧ IsAPCover (A : Set ℕ) N 1 }.Nonempty := by
  refine ⟨1, {0}, by simp, fun d _ => ⟨0, {0}, by simp, ?_⟩⟩
  rw [show ((1 : ℕ) : ℕ∞) = 1 from rfl, Set.IsAPOfLengthWith.one]

/-- `m N 1 ≠ 0` for `1 ≤ N`. -/
theorem m_one_ne_zero (N : ℕ) (hN : 1 ≤ N) : m N 1 ≠ 0 := by
  intro h
  rcases Nat.sInf_eq_zero.mp h with h0 | hempty
  · obtain ⟨A, hA, hcov⟩ := h0
    rw [Finset.card_eq_zero] at hA
    subst hA
    exact empty_not_cover_one N hN (by simpa using hcov)
  · exact absurd hempty (Set.nonempty_iff_ne_empty.mp (one_cover_nonempty N))

/-- Upstream `green_37_asymptotic` admits no closed answer `g : ℕ → ℝ`:
`k = 0` forces `g` eventually `0`, but `m N 1 ≠ 0` for `N ≥ 1`. -/
theorem green_37_asymptotic_no_closed_answer :
    ¬ ∃ g : ℕ → ℝ, ∀ k : ℕ, ∀ᶠ N in atTop, (m N k : ℝ) = g N := by
  rintro ⟨g, hg⟩
  obtain ⟨N, ⟨hN0, hN1'⟩, hN1⟩ :=
    (((hg 0).and (hg 1)).and (eventually_ge_atTop 1)).exists
  rw [m_zero N] at hN0
  rw [← hN0] at hN1'
  exact m_one_ne_zero N hN1 (by exact_mod_cast hN1')

end Green37b
