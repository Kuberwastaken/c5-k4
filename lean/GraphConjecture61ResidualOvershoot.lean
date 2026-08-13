import GraphConjecture61FundedTrajectory
import GraphConjecture61CumulativeCredit
import GraphConjecture61Induction

/-!
# WOWII 61: residual-gap overshoot is the exact missing bridge

Along admissible Havel--Hakimi trajectories, cumulative eliminated heads and
the remaining degree sum carry exactly the same information.  This file turns
the proposed global funding bridge into a graph-specific residual-gap claim:
the signed source-minus-target degree-sum gap must never exceed its initial
value.  A first unfunded head would force an overshoot of at least two.
-/

namespace WrittenOnTheWallII.GraphConjecture61ResidualOvershoot

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61FundedTrajectory

/-- Signed source-minus-target degree-sum gap after `k` canonical steps. -/
def signedResidualGap (k : ℕ) (source target : List ℕ) : ℤ :=
  (((havelHakimiStep^[k]) source).sum : ℤ) -
    (((havelHakimiStep^[k]) target).sum : ℤ)

/-- Admissibility is inherited by every shorter trajectory prefix. -/
theorem admissibleFor_mono
    {j k : ℕ} {s : List ℕ} (hjk : j ≤ k)
    (h : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor k s) :
    WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor j s := by
  induction j generalizing k s with
  | zero => trivial
  | succ j ih =>
      cases k with
      | zero => omega
      | succ k =>
          obtain ⟨d, rest, hs, hadm, htail⟩ := h
          exact ⟨d, rest, hs, hadm, ih (by omega) htail⟩

/-- Exact remaining-sum accounting in the cumulative-head vocabulary used by
the endpoint and funding files. -/
theorem iterate_sum_add_twice_cumulativeHeadSum
    {k : ℕ} {s : List ℕ}
    (h : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor k s) :
    ((havelHakimiStep^[k]) s).sum + 2 * cumulativeHeadSum k s = s.sum := by
  have hloss :=
    WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeStepLoss_eq_twice_cumulativeHeadSum h
  have htel :=
    WrittenOnTheWallII.GraphConjecture61Induction.sum_eq_iterate_add_cumulativeStepLoss k s
  have hstepEqAll : ∀ (n : ℕ) (x : List ℕ),
      WrittenOnTheWallII.GraphConjecture61Induction.cumulativeStepLoss n x =
        WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeStepLoss n x := by
    intro n x
    induction n generalizing x with
    | zero => simp [WrittenOnTheWallII.GraphConjecture61Induction.cumulativeStepLoss,
        WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeStepLoss]
    | succ n ih =>
        simp only [WrittenOnTheWallII.GraphConjecture61Induction.cumulativeStepLoss,
          WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeStepLoss]
        rw [ih]
        rfl
  have hheadEqAll : ∀ (n : ℕ) (x : List ℕ),
      WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeHeadSum n x =
        cumulativeHeadSum n x := by
    intro n x
    induction n generalizing x with
    | zero => simp [WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeHeadSum,
        cumulativeHeadSum]
    | succ n ih =>
        simp only [WrittenOnTheWallII.GraphConjecture61CumulativeCredit.cumulativeHeadSum,
          cumulativeHeadSum]
        rw [ih]
        rfl
  have hstepEq := hstepEqAll k s
  have hheadEq := hheadEqAll k s
  rw [← hstepEq, hheadEq] at hloss
  omega

/-- The residual signed gap equals the initial gap minus twice the cumulative
head surplus. -/
theorem signedResidualGap_eq_initial_sub_twice_headSurplus
    {k : ℕ} {source target : List ℕ}
    (hs : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k source)
    (ht : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k target) :
    signedResidualGap k source target =
      (source.sum : ℤ) - (target.sum : ℤ) -
        2 * ((cumulativeHeadSum k source : ℤ) -
          (cumulativeHeadSum k target : ℤ)) := by
  have hsEq := iterate_sum_add_twice_cumulativeHeadSum hs
  have htEq := iterate_sum_add_twice_cumulativeHeadSum ht
  simp only [signedResidualGap]
  omega

/-- Pointwise exact bridge: cumulative-head order is equivalent to saying the
current signed residual gap has not overshot the initial signed gap. -/
theorem cumulativeHeadOrder_iff_residualGap_noOvershoot
    {k : ℕ} {source target : List ℕ}
    (hs : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k source)
    (ht : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k target) :
    cumulativeHeadSum k target ≤ cumulativeHeadSum k source ↔
      signedResidualGap k source target ≤ signedResidualGap 0 source target := by
  rw [signedResidualGap_eq_initial_sub_twice_headSurplus hs ht]
  simp only [signedResidualGap, Function.iterate_zero_apply]
  omega

/-- A first unfunded transition cannot be subtle: it makes the next residual
gap exceed the initial gap by at least two degree-sum units. -/
theorem first_unfunded_forces_residualGap_overshoot
    {k : ℕ} {source target : List ℕ}
    (hs : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      (k + 1) source)
    (ht : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      (k + 1) target)
    (hprevious : cumulativeHeadSum k target ≤ cumulativeHeadSum k source)
    (hunfunded : ¬ HeadReversalFundedAt k source target) :
    signedResidualGap 0 source target + 2 ≤
      signedResidualGap (k + 1) source target := by
  have hnext : ¬ cumulativeHeadSum (k + 1) target ≤
      cumulativeHeadSum (k + 1) source := by
    exact fun horder ↦ hunfunded
      ((next_cumulative_order_iff_headReversalFunded k source target
        hprevious).1 horder)
  have hgapEq := signedResidualGap_eq_initial_sub_twice_headSurplus hs ht
  rw [hgapEq]
  simp only [signedResidualGap, Function.iterate_zero_apply]
  omega

/-- The precise graph-specific property still needed for the global bridge. -/
def ResidualGapDoesNotOvershootThrough
    (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j ≤ k →
    signedResidualGap j source target ≤ signedResidualGap 0 source target

/-- If admissibility and no-overshoot hold through `k`, every cumulative head
prefix is ordered.  This is the exact next rung required from graphical
degree-prefix dominance. -/
theorem cumulativeHeadDominates_of_residualGap_noOvershoot
    {k : ℕ} {source target : List ℕ}
    (hs : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k source)
    (ht : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k target)
    (hgap : ResidualGapDoesNotOvershootThrough k source target) :
    ∀ j : ℕ, j ≤ k →
      cumulativeHeadSum j target ≤ cumulativeHeadSum j source := by
  intro j hj
  have hsJ := admissibleFor_mono hj hs
  have htJ := admissibleFor_mono hj ht
  exact (cumulativeHeadOrder_iff_residualGap_noOvershoot hsJ htJ).2
    (hgap j hj)

/-- No-overshoot supplies exactly the funded-trajectory premise from v0.27. -/
theorem headReversalsFunded_of_residualGap_noOvershoot
    {k : ℕ} {source target : List ℕ}
    (hs : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k source)
    (ht : WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor
      k target)
    (hgap : ResidualGapDoesNotOvershootThrough k source target) :
    HeadReversalsFundedThrough k source target := by
  intro j hj
  have hdom := cumulativeHeadDominates_of_residualGap_noOvershoot hs ht hgap
  have hprevious := hdom j (by omega)
  have hnext := hdom (j + 1) (by omega)
  exact (next_cumulative_order_iff_headReversalFunded j source target
    hprevious).1 hnext

/-- The exact list-side conjecture-specific bridge left open by this file.
For graphical descending degree lists, admissibility is canonical; proving this
proposition from initial degree-prefix dominance would close the trajectory
funding step without any successor-dominance claim. -/
def DegreePrefixNoResidualOvershootBridge : Prop :=
  ∀ (k : ℕ) (source target : List ℕ),
    WrittenOnTheWallII.GraphConjecture61PrefixSaturation.DegreePrefixDominates
      source target →
    WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor k source →
    WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor k target →
    ResidualGapDoesNotOvershootThrough k source target

end WrittenOnTheWallII.GraphConjecture61ResidualOvershoot
