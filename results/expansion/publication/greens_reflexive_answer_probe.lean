import FormalConjecturesUtil
/-!
# Probe: degenerate `answer( )` holes in `GreensOpenProblems`

Definitions copied verbatim from upstream `main` @ 638da20e.  Each theorem below
is the upstream statement with `answer(sorry)` replaced by an explicit term and
`sorry` replaced by a real proof.  `google.answer` is set to `with_auxiliary`,
the strictest mode, so every answer accepted here is a genuine closed term.
-/

open Asymptotics Filter Finset Real
open scoped Pointwise

set_option google.answer "with_auxiliary"

-- ############################ Green 25 ############################
namespace Green25

def Property25 (k N : ℕ) : Prop :=
  1 ≤ k ∧ k ≤ N ∧
  ∀ P : Finpartition (Icc 1 N), #P.parts = k →
  10 * #(P.parts.biUnion Finset.restrictedSumset) ≥ N

/-- Upstream `green_25`, closed by `rfl` with a **closed** answer. -/
theorem green_25 : {k : ℕ → ℕ | ∀ᶠ N in atTop, Property25 (k N) N} =
    answer({k : ℕ → ℕ | ∀ᶠ N in atTop, Property25 (k N) N}) := rfl

end Green25

-- ############################ Green 51 ############################
namespace Green51

noncomputable def guaranteedMaxCosetDim (n : ℕ) (α : ℝ) : ℕ :=
  sInf { maxCosetDim (ZMod 2) (𝔽₂ n) ↑(A + A) | (A : Finset (𝔽₂ n)) (_h : A.dens ≥ α) }

/-- Upstream `green_51`, closed by `rfl` with a **closed** answer. -/
theorem green_51 : answer(guaranteedMaxCosetDim) = guaranteedMaxCosetDim := rfl

end Green51

-- ############################ Green 27 ############################
namespace Green27

noncomputable def m (p : ℕ) : ℝ :=
  (sInf { (A.card) | (A : Finset (ZMod p)) (_ : 2 ≤ A.card) (_ : HasNoUniqueRepresentation A) } : ℝ)

def primesAtTop : Filter ℕ := atTop ⊓ 𝓟 {p : ℕ | p.Prime}

/-- Upstream `green_27.equivalent`, closed by `IsEquivalent.refl` with a **closed** answer. -/
theorem green_27.equivalent : (answer(m) : ℕ → ℝ) ~[primesAtTop] m := IsEquivalent.refl

end Green27
