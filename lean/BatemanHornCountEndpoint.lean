import FormalConjectures.Wikipedia.BatemanHornConjecture

/-!
# Endpoint defect in the formal Bateman--Horn counting helper

For the polynomial `X + 2`, the frozen helper counts `n = 0` at `x = 0`, even
though the cited Bateman--Horn count ranges over positive integers.
-/

open Polynomial

namespace BatemanHornConjecture

noncomputable def endpointPolynomial : ℤ[X] := X + C 2

theorem endpointPolynomial_at_zero : endpointPolynomial.eval 0 = 2 := by
  norm_num [endpointPolynomial]

theorem countSimultaneousPrimes_at_zero :
    CountSimultaneousPrimes {endpointPolynomial} 0 = 1 := by
  norm_num [CountSimultaneousPrimes, endpointPolynomial]
  native_decide

theorem zero_is_formally_counted :
    ∀ f ∈ ({endpointPolynomial} : Finset ℤ[X]),
      (f.eval (0 : ℤ)).natAbs.Prime := by
  intro f hf
  simp only [Finset.mem_singleton] at hf
  subst f
  norm_num [endpointPolynomial]

end BatemanHornConjecture
