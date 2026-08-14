import FormalConjectures.OEIS.«113019»

/-!
# An additional fixed point for OEIS A113019

The value `9^9 = 387420489` has nine decimal digits and digital root nine, so
the formalized sequence maps it to itself.  It is distinct from the two fixed
points named in the merged question, `1` and `32`.
-/

namespace OeisA113019

theorem a_387420489 : a 387420489 = 387420489 := by
  native_decide

theorem extra_fixed_point :
    ∃ n : ℕ, a n = n ∧ n ≠ 1 ∧ n ≠ 32 := by
  exact ⟨387420489, a_387420489, by native_decide, by native_decide⟩

theorem proposed_fixed_point_classification_false :
    ¬∀ n : ℕ, a n = n → n = 1 ∨ n = 32 := by
  intro h
  have classified := h 387420489 a_387420489
  omega

end OeisA113019
