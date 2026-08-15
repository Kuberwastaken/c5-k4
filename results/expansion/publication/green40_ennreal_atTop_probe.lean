import FormalConjecturesUtil
/-! # Probe: `atTop` on `ℝ≥0∞` -/

open Filter Topology Asymptotics
open scoped ENNReal

/-- `atTop` on `ℝ≥0∞` is the principal ultrafilter at `⊤`. -/
theorem atTop_ennreal_eq : (atTop : Filter ℝ≥0∞) = pure ⊤ := by
  rw [(isTop_top (α := ℝ≥0∞)).atTop_eq]
  have : Set.Ici (⊤ : ℝ≥0∞) = {⊤} := by
    ext x; simp only [Set.mem_Ici, Set.mem_singleton_iff, top_le_iff]
  rw [this, principal_singleton]

/-- Consequently `Tendsto g l atTop` on `ℝ≥0∞` says `g` is eventually `⊤`. -/
theorem tendsto_atTop_ennreal_iff {α : Type*} (l : Filter α) (g : α → ℝ≥0∞) :
    Tendsto g l (atTop : Filter ℝ≥0∞) ↔ ∀ᶠ x in l, g x = ⊤ := by
  rw [atTop_ennreal_eq, tendsto_pure]

/-- The `𝓝 ⊤` form used by `green_40` is strictly weaker: eventual equality implies it. -/
theorem tendsto_nhds_top_of_eventually {α : Type*} (l : Filter α) (g : α → ℝ≥0∞)
    (h : ∀ᶠ x in l, g x = ⊤) : Tendsto g l (𝓝 ⊤) :=
  tendsto_nhds_of_eventually_eq h

/-- `green_35.lower`: the first conjunct is closed by the zero function. -/
theorem g35_lower_first_conjunct (c : ℝ≥0∞ → ℝ≥0∞) :
    ∀ p : ℝ≥0∞, 1 < p → (0 : ℝ≥0∞ → ℝ≥0∞) p ≤ c p := fun p _ => by simp

/-- `green_35.upper`: `ub` is unconstrained away from `⊤`. -/
theorem g35_upper_shape (c : ℝ≥0∞ → ℝ≥0∞) (h : c ⊤ < 0.7505) :
    ∃ ub : ℝ≥0∞ → ℝ≥0∞, (∀ p : ℝ≥0∞, 1 < p → c p ≤ ub p) ∧ ub ⊤ < 0.7505 :=
  ⟨fun p => if p = ⊤ then c ⊤ else ⊤, by
    intro p _
    by_cases hp : p = ⊤ <;> simp [hp], by simp [h]⟩

/-- Reflexivity closes `green_27.equivalent`-shaped goals. -/
theorem g27_refl {α : Type*} (l : Filter α) (m : α → ℝ) : m ~[l] m := Asymptotics.IsEquivalent.refl

/-- Reflexivity closes `green_37_theta`-shaped goals. -/
theorem g37_theta_refl {α : Type*} (l : Filter α) (m : α → ℝ) :
    m =Θ[l] m := Asymptotics.isTheta_refl _ _
