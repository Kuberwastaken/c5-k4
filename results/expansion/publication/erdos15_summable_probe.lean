/-
Copyright 2026 The Formal Conjectures Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-/

import FormalConjecturesUtil

/-!
# Probe 15
-/

set_option linter.style.ams_attribute false
set_option linter.style.category_attribute false

namespace Probe15

open Filter Topology

theorem summable_rat_to_real (f : ℕ → ℚ) (h : Summable f) :
    Summable (fun k => (f k : ℝ)) :=
  (h.hasSum.map (Rat.castHom ℝ).toAddMonoidHom Rat.continuous_coe_real).summable

theorem reduce (h : Summable (fun k : ℕ => (-1 : ℚ) ^ (k + 1) * (k + 1) / (k.nth Nat.Prime))) :
    Summable (fun k : ℕ => ((k : ℝ) + 1) / (k.nth Nat.Prime)) := by
  have h2 := (summable_rat_to_real _ h).abs
  refine h2.congr fun k => ?_
  push_cast
  rw [abs_div, abs_mul, abs_pow, abs_neg, abs_one, one_pow, one_mul]
  rw [abs_of_nonneg (by positivity : (0 : ℝ) ≤ (k : ℝ) + 1),
    abs_of_nonneg (by positivity : (0 : ℝ) ≤ ((k.nth Nat.Prime : ℕ) : ℝ))]

end Probe15

#print axioms Probe15.summable_rat_to_real
#print axioms Probe15.reduce
