import FormalConjectures.OEIS.«109074»

/-!
# Counterexample to the formalized OEIS A109074 identity

At `n = 1`, the formalized left side is `1`, while its formalized shifted
`b`-ratio is `3`.  This certificate concerns the exact declaration merged in
`google-deepmind/formal-conjectures` at commit
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
-/

namespace OeisA109074

theorem frac_one : frac 1 = 1 := by
  native_decide

theorem b_one : b 1 = 1 := by
  native_decide

theorem b_two : b 2 = 3 := by
  native_decide

theorem counterexample_at_one :
    frac 1 ≠ (b (1 + 1) : ℚ) / (b 1 : ℚ) := by
  native_decide

theorem formalized_conjecture_false :
    ¬∀ n : ℕ, n ≥ 1 → frac n = (b (n + 1) : ℚ) / (b n : ℚ) := by
  intro h
  exact counterexample_at_one (h 1 (by omega))

end OeisA109074
