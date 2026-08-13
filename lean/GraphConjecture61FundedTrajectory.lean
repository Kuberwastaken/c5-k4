import GraphConjecture61ThirdHeadCredit

/-!
# WOWII 61: globally funded unit reversals

Ordinary prefix dominance need not survive a Havel--Hakimi step.  The usable
global invariant is instead cumulative: at each depth, a target head may be
one larger than the source head exactly when an earlier strict cumulative
surplus pays for that unit reversal.
-/

namespace WrittenOnTheWallII.GraphConjecture61FundedTrajectory

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61PrefixSaturation

/-- The head exposed at trajectory depth `k`. -/
def trajectoryHead (k : ℕ) (s : List ℕ) : ℕ :=
  headDegree ((havelHakimiStep^[k]) s)

theorem cumulativeHeadSum_succ (k : ℕ) (s : List ℕ) :
    cumulativeHeadSum (k + 1) s =
      cumulativeHeadSum k s + trajectoryHead k s := by
  induction k generalizing s with
  | zero => simp [cumulativeHeadSum, trajectoryHead]
  | succ k ih =>
      change headDegree s + cumulativeHeadSum (k + 1) (havelHakimiStep s) =
        headDegree s + cumulativeHeadSum k (havelHakimiStep s) +
          trajectoryHead (k + 1) s
      rw [ih (havelHakimiStep s)]
      simp only [trajectoryHead, Function.iterate_succ_apply]
      omega

/-- At depth `k`, either the target head is already monotone, or its sole
allowed excess is one and the preceding cumulative comparison is strict. -/
def UnitReversalFundedAt (k : ℕ) (source target : List ℕ) : Prop :=
  trajectoryHead k target ≤ trajectoryHead k source ∨
    (trajectoryHead k target = trajectoryHead k source + 1 ∧
      cumulativeHeadSum k target < cumulativeHeadSum k source)

/-- Every head exposed before depth `k` satisfies the local funding rule. -/
def UnitReversalsFundedThrough (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j < k → UnitReversalFundedAt j source target

/-- The cumulative surplus banked before depth `k`. -/
def bankedHeadCredit (k : ℕ) (source target : List ℕ) : ℕ :=
  cumulativeHeadSum k source - cumulativeHeadSum k target

/-- General local funding rule.  Unlike the endpoint-specialized rule above,
this permits a reversal of any size, provided the accumulated bank covers it. -/
def HeadReversalFundedAt (k : ℕ) (source target : List ℕ) : Prop :=
  trajectoryHead k target ≤
    bankedHeadCredit k source target + trajectoryHead k source

/-- Every transition before depth `k` is paid for by its current bank. -/
def HeadReversalsFundedThrough (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j < k → HeadReversalFundedAt j source target

/-- Exact local payment law: under a unit reversal, extending the cumulative
order is equivalent to having strict earlier surplus. -/
theorem next_cumulative_order_iff_strict_of_unit_reversal
    (k : ℕ) (source target : List ℕ)
    (hreversal : trajectoryHead k target = trajectoryHead k source + 1) :
    cumulativeHeadSum (k + 1) target ≤ cumulativeHeadSum (k + 1) source ↔
      cumulativeHeadSum k target < cumulativeHeadSum k source := by
  rw [cumulativeHeadSum_succ, cumulativeHeadSum_succ, hreversal]
  omega

/-- A funded local step preserves the cumulative-head order. -/
theorem next_cumulative_order_of_funded
    (k : ℕ) (source target : List ℕ)
    (hprevious : cumulativeHeadSum k target ≤ cumulativeHeadSum k source)
    (hfunded : UnitReversalFundedAt k source target) :
    cumulativeHeadSum (k + 1) target ≤ cumulativeHeadSum (k + 1) source := by
  rw [cumulativeHeadSum_succ, cumulativeHeadSum_succ]
  rcases hfunded with hmonotone | ⟨hreversal, hstrict⟩
  · omega
  · omega

/-- Exact general local credit law. -/
theorem next_cumulative_order_iff_headReversalFunded
    (k : ℕ) (source target : List ℕ)
    (hprevious : cumulativeHeadSum k target ≤ cumulativeHeadSum k source) :
    cumulativeHeadSum (k + 1) target ≤ cumulativeHeadSum (k + 1) source ↔
      HeadReversalFundedAt k source target := by
  rw [cumulativeHeadSum_succ, cumulativeHeadSum_succ]
  simp only [HeadReversalFundedAt, bankedHeadCredit]
  omega

/-- Global amortization theorem.  Local endpoint comparisons may reverse, so
no successor-prefix premise appears.  Funding every unit reversal suffices to
preserve every cumulative prefix along the whole trajectory. -/
theorem cumulativeHeadDominates_of_unitReversalsFunded
    (k : ℕ) (source target : List ℕ)
    (hfunded : UnitReversalsFundedThrough k source target) :
    ∀ j : ℕ, j ≤ k →
      cumulativeHeadSum j target ≤ cumulativeHeadSum j source := by
  induction k with
  | zero =>
      intro j hj
      have : j = 0 := by omega
      subst j
      simp [cumulativeHeadSum]
  | succ k ih =>
      intro j hj
      by_cases hle : j ≤ k
      · apply ih
        · intro i hi
          exact hfunded i (by omega)
        · exact hle
      · have hjEq : j = k + 1 := by omega
        subst j
        apply next_cumulative_order_of_funded k source target
        · exact ih (fun i hi ↦ hfunded i (by omega)) k (le_refl _)
        · exact hfunded k (Nat.lt_succ_self k)

/-- Global exact-credit induction, allowing reversals larger than one. -/
theorem cumulativeHeadDominates_of_headReversalsFunded
    (k : ℕ) (source target : List ℕ)
    (hfunded : HeadReversalsFundedThrough k source target) :
    ∀ j : ℕ, j ≤ k →
      cumulativeHeadSum j target ≤ cumulativeHeadSum j source := by
  induction k with
  | zero =>
      intro j hj
      have : j = 0 := by omega
      subst j
      simp [cumulativeHeadSum]
  | succ k ih =>
      intro j hj
      by_cases hle : j ≤ k
      · apply ih
        · intro i hi
          exact hfunded i (by omega)
        · exact hle
      · have hjEq : j = k + 1 := by omega
        subst j
        have hprevious := ih (fun i hi ↦ hfunded i (by omega)) k (le_refl _)
        exact (next_cumulative_order_iff_headReversalFunded k source target
          hprevious).2 (hfunded k (Nat.lt_succ_self k))

/-- The smallest successor-prefix obstruction is nevertheless a nonvacuous
funded trajectory: `P₃` plus an isolate starts one unit ahead of a perfect
matching, whose next head reverses by one and consumes exactly that credit. -/
theorem orderFour_prefixPair_is_funded :
    DegreePrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] ∧
      UnitReversalsFundedThrough 4 [2, 1, 1, 0] [1, 1, 1, 1] ∧
      ∀ j : ℕ, j ≤ 4 →
        cumulativeHeadSum j [1, 1, 1, 1] ≤
          cumulativeHeadSum j [2, 1, 1, 0] := by
  have hprefix : DegreePrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] := by
    constructor
    · norm_num
    · intro k hk
      norm_num at hk
      interval_cases k <;> norm_num
  have hfunded :
      UnitReversalsFundedThrough 4 [2, 1, 1, 0] [1, 1, 1, 1] := by
    intro j hj
    interval_cases j <;>
      norm_num [UnitReversalFundedAt, trajectoryHead, cumulativeHeadSum,
        headDegree, havelHakimiStep, List.splitAt_eq, List.mergeSort]
  exact ⟨hprefix, hfunded,
    cumulativeHeadDominates_of_unitReversalsFunded 4 _ _ hfunded⟩

/-- Unit-only funding is not a global consequence of initial prefix
dominance.  At order five the target reverses by two at depth two, but the
source has banked exactly two units, so the general credit rule still holds. -/
theorem orderFive_twoUnitReversal_boundary :
    DegreePrefixDominates [4, 4, 2, 2, 2] [3, 3, 3, 3, 2] ∧
      cumulativeHeadSum 2 [3, 3, 3, 3, 2] + 2 =
        cumulativeHeadSum 2 [4, 4, 2, 2, 2] ∧
      trajectoryHead 2 [3, 3, 3, 3, 2] =
        trajectoryHead 2 [4, 4, 2, 2, 2] + 2 ∧
      ¬ UnitReversalFundedAt 2 [4, 4, 2, 2, 2] [3, 3, 3, 3, 2] ∧
      HeadReversalFundedAt 2 [4, 4, 2, 2, 2] [3, 3, 3, 3, 2] ∧
      cumulativeHeadSum 3 [3, 3, 3, 3, 2] =
        cumulativeHeadSum 3 [4, 4, 2, 2, 2] := by
  have hprefix : DegreePrefixDominates [4, 4, 2, 2, 2] [3, 3, 3, 3, 2] := by
    constructor
    · norm_num
    · intro k hk
      norm_num at hk
      interval_cases k <;> norm_num
  refine ⟨hprefix, ?_⟩
  norm_num [UnitReversalFundedAt, HeadReversalFundedAt, bankedHeadCredit,
    trajectoryHead, cumulativeHeadSum, headDegree, havelHakimiStep,
    List.splitAt_eq, List.mergeSort]

end WrittenOnTheWallII.GraphConjecture61FundedTrajectory
