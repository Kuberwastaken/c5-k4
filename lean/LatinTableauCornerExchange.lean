import FormalConjecturesUtil

/-!
# Latin Tableau corner-exchange lemmas

Reusable algebraic and coloring lemmas extracted from the order-15
bottom-corner theorem signal. These lemmas do not prove the Latin Tableau
Conjecture or the remaining Ferrers exchange-existence step.
-/

namespace LatinTableau.CornerExchange

/-- If `dA` and `dB` are consecutive differences of cumulative profiles `A`
and `B`, and `delta` is their cumulative difference, then the difference of
the profiles is the consecutive difference of `delta`. Using `Int` avoids
hidden truncated-subtraction hypotheses. -/
theorem profile_difference_eq_delta_step
    (A B dA dB delta : ℕ → ℤ) (k : ℕ)
    (hdA : dA (k + 1) = A (k + 1) - A k)
    (hdB : dB (k + 1) = B (k + 1) - B k)
    (hdelta : ∀ j, delta j = A j - B j) :
    dA (k + 1) - dB (k + 1) = delta (k + 1) - delta k := by
  rw [hdA, hdB, hdelta, hdelta]
  ring

/-- When deletion changes every cumulative optimum by zero or one, a single
profile coordinate can change only by `-1`, `0`, or `1`. -/
theorem binary_delta_bounds_profile_change
    (A B dA dB delta : ℕ → ℤ) (k : ℕ)
    (hdA : dA (k + 1) = A (k + 1) - A k)
    (hdB : dB (k + 1) = B (k + 1) - B k)
    (hdelta : ∀ j, delta j = A j - B j)
    (hbinary : ∀ j, delta j = 0 ∨ delta j = 1) :
    dA (k + 1) - dB (k + 1) = -1 ∨
      dA (k + 1) - dB (k + 1) = 0 ∨
      dA (k + 1) - dB (k + 1) = 1 := by
  rw [profile_difference_eq_delta_step A B dA dB delta k hdA hdB hdelta]
  rcases hbinary (k + 1) with hnext | hnext <;>
    rcases hbinary k with hprev | hprev <;> omega

/-- The consecutive difference of a positive threshold step is one at the
threshold and zero elsewhere. -/
theorem threshold_delta_step (c k : ℕ) :
    ((if c ≤ k + 1 then (1 : ℤ) else 0) - if c ≤ k then 1 else 0) =
      if k + 1 = c then 1 else 0 := by
  split_ifs <;> omega

/-- A threshold cumulative difference forces a single basis-vector change in
the successive profile. -/
theorem threshold_delta_implies_basis_profile_change
    (A B dA dB delta : ℕ → ℤ) (c k : ℕ)
    (hdA : dA (k + 1) = A (k + 1) - A k)
    (hdB : dB (k + 1) = B (k + 1) - B k)
    (hdelta : ∀ j, delta j = A j - B j)
    (hthreshold : ∀ j, delta j = if c ≤ j then 1 else 0) :
    dA (k + 1) - dB (k + 1) = if k + 1 = c then 1 else 0 := by
  rw [profile_difference_eq_delta_step A B dA dB delta k hdA hdB hdelta,
    hthreshold, hthreshold]
  exact threshold_delta_step c k

section Coloring

open SimpleGraph

variable {V Color : Type*}

/-- Extend a proper coloring across one new `Option.none` vertex. Old-old
edges must already belong to `G`; every new-old edge must avoid `c`. -/
def extendColoringAtNone
    (G : SimpleGraph V) (H : SimpleGraph (Option V)) (C : G.Coloring Color)
    (c : Color)
    (hOld : ∀ {v w}, H.Adj (some v) (some w) → G.Adj v w)
    (hNew : ∀ {v}, H.Adj none (some v) → c ≠ C v) :
    H.Coloring Color :=
  SimpleGraph.Coloring.mk
    (fun v ↦ match v with | none => c | some w => C w)
    (by
      intro v w hvw
      cases v with
      | none =>
          cases w with
          | none => exact (H.loopless none hvw).elim
          | some w => exact hNew hvw
      | some v =>
          cases w with
          | none => exact (hNew hvw.symm).symm
          | some w => exact C.valid (hOld hvw))

@[simp] theorem extendColoringAtNone_apply_none
    (G : SimpleGraph V) (H : SimpleGraph (Option V)) (C : G.Coloring Color)
    (c : Color)
    (hOld : ∀ {v w}, H.Adj (some v) (some w) → G.Adj v w)
    (hNew : ∀ {v}, H.Adj none (some v) → c ≠ C v) :
    extendColoringAtNone G H C c hOld hNew none = c := rfl

@[simp] theorem extendColoringAtNone_apply_some
    (G : SimpleGraph V) (H : SimpleGraph (Option V)) (C : G.Coloring Color)
    (c : Color)
    (hOld : ∀ {v w}, H.Adj (some v) (some w) → G.Adj v w)
    (hNew : ∀ {v}, H.Adj none (some v) → c ≠ C v) (v : V) :
    extendColoringAtNone G H C c hOld hNew (some v) = C v := rfl

end Coloring

end LatinTableau.CornerExchange
