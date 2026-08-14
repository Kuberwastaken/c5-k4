import Mathlib.Data.Nat.Nth
import Mathlib.Algebra.Ring.Parity

/-!
The target-free enumeration bridge for `OeisA108569.conjecture`.

It reduces a future odd semantic member of any decidable predicate to an
explicit positive sequence index without computing `Nat.count p k`.
Instantiating `p` with `OeisA108569.A` leaves only `A 1`, `A k`, `1 < k`, and
oddness as obligations. This file evaluates no candidate coordinate.
-/

namespace A108569EnumerationBridge

theorem exists_pos_index_of_member
    (p : ℕ → Prop) [DecidablePred p]
    (hp1 : p 1) {k : ℕ} (hk : 1 < k) (hpk : p k) :
    ∃ n, 0 < n ∧ Nat.nth p n = k := by
  refine ⟨Nat.count p k, ?_, Nat.nth_count hpk⟩
  exact lt_of_le_of_lt (Nat.zero_le _) (Nat.count_strict_mono hp1 hk)

theorem odd_member_refutes_parity
    (p : ℕ → Prop) [DecidablePred p]
    (hp1 : p 1) {k : ℕ} (hk : 1 < k) (hpk : p k) (hkodd : Odd k) :
    ¬ ∀ n, 0 < n → Even (Nat.nth p n) := by
  obtain ⟨n, hn, ha⟩ := exists_pos_index_of_member p hp1 hk hpk
  intro hparity
  exact (Nat.not_even_iff_odd.mpr hkodd) (ha ▸ hparity n hn)

end A108569EnumerationBridge
