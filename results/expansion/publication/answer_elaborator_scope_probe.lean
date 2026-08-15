import FormalConjecturesUtil
/-! # Probe: what `answer( )` accepts in `with_auxiliary` mode -/

section Closed
set_option google.answer "with_auxiliary"

/-- A CLOSED answer is accepted: the auxiliary definition `okClosed._answer` is created. -/
theorem okClosed : (answer(37) : ℕ) = 37 := rfl

#print okClosed._answer
end Closed

section Open
set_option google.answer "with_auxiliary"

/-- An answer mentioning the theorem's own binder is REJECTED. -/
theorem badOpen (k : ℕ) : (answer(k) : ℕ) = k := rfl
end Open


set_option linter.style.answer_attribute true

/-- Explicit binder in the `declSig`: the linter fires. -/
@[category research open, AMS 5]
theorem explicitBinder (m : ℕ) : answer(sorry) ↔ (0 < m) := by sorry

section
variable {n : ℕ}

/-- Same statement, binder introduced by `variable`: the linter is silent. -/
@[category research open, AMS 5]
theorem sectionBinder : answer(sorry) ↔ (0 < n) := by sorry

end

/-- With a closed answer, `answer(sorry) ↔ (Odd n → Q n)` under `∀ n` forces the answer
to be `True`, because the right-hand side is vacuously true at every even `n`.
So `answer(False)` is unprovable whatever the conjecture's truth value. -/
theorem answer_forced_true {Q : ℕ → Prop} (A : Prop) (h : ∀ n : ℕ, A ↔ (Odd n → Q n)) : A :=
  (h 2).mpr (fun h2 => absurd h2 (by decide))
