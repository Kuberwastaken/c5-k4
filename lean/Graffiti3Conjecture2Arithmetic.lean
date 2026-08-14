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
# Graffiti³ Conjecture 2: double-star arithmetic certificate

Graffiti³ Conjecture 2 asks whether the independence number of a connected
graph is at most its second geometric-arithmetic index

`RGA2(G) = ∑ uv ∈ E(G), 2 * sqrt (d₂(u) * d₂(v)) / (d₂(u) + d₂(v))`,

where `d₂(u)` counts the vertices at distance at most two from `u`, including
`u` itself.

For the double star whose adjacent centers have eleven and twelve leaves, the
two centers have `d₂ = 25`, the eleven left leaves have `d₂ = 13`, and the
twelve right leaves have `d₂ = 14`.  Its 23 leaves are independent.  The
lemmas below certify only the resulting exact arithmetic reduction and its
logical consequence; they do not formalize the graph, the distance-two
invariant, or the edge sum.
-/

namespace Graffiti3.Conjecture2

/-- The left spoke radical reduces from `sqrt (13 * 25)` to `5 * sqrt 13`. -/
@[category test, AMS 5]
lemma sqrt_thirteen_mul_twenty_five :
    Real.sqrt ((13 : ℝ) * 25) = 5 * Real.sqrt 13 := by
  rw [Real.sqrt_mul (by positivity : (0 : ℝ) ≤ 13)]
  norm_num <;> ring

/-- The right spoke radical reduces from `sqrt (14 * 25)` to `5 * sqrt 14`. -/
@[category test, AMS 5]
lemma sqrt_fourteen_mul_twenty_five :
    Real.sqrt ((14 : ℝ) * 25) = 5 * Real.sqrt 14 := by
  rw [Real.sqrt_mul (by positivity : (0 : ℝ) ≤ 14)]
  norm_num <;> ring

/-- The three edge classes of the `(11, 12)` double star give the displayed
closed form: one center edge, eleven left spokes, and twelve right spokes. -/
@[category test, AMS 5]
lemma edge_class_decomposition :
    2 * Real.sqrt ((25 : ℝ) * 25) / (25 + 25) +
        11 * (2 * Real.sqrt ((13 : ℝ) * 25) / (13 + 25)) +
        12 * (2 * Real.sqrt ((14 : ℝ) * 25) / (14 + 25)) =
      1 + 55 * Real.sqrt 13 / 19 + 40 * Real.sqrt 14 / 13 := by
  rw [sqrt_thirteen_mul_twenty_five, sqrt_fourteen_mul_twenty_five]
  norm_num <;> ring

/-- Exact strict arithmetic certificate for the candidate's RGA2 value. -/
@[category test, AMS 5]
theorem double_star_11_12_rga2_lt_twenty_three :
    (1 : ℝ) + 55 * Real.sqrt 13 / 19 + 40 * Real.sqrt 14 / 13 < 23 := by
  have h13 : Real.sqrt (13 : ℝ) < 361 / 100 := by
    apply (Real.sqrt_lt' (by norm_num : (0 : ℝ) < 361 / 100)).2
    norm_num
  have h14 : Real.sqrt (14 : ℝ) < 15 / 4 := by
    apply (Real.sqrt_lt' (by norm_num : (0 : ℝ) < 15 / 4)).2
    norm_num
  nlinarith

/-- The same strict certificate in the unsimplified three-edge-class form. -/
@[category test, AMS 5]
theorem double_star_11_12_edge_sum_lt_twenty_three :
    2 * Real.sqrt ((25 : ℝ) * 25) / (25 + 25) +
        11 * (2 * Real.sqrt ((13 : ℝ) * 25) / (13 + 25)) +
        12 * (2 * Real.sqrt ((14 : ℝ) * 25) / (14 + 25)) < 23 := by
  rw [edge_class_decomposition]
  exact double_star_11_12_rga2_lt_twenty_three

/-- Any independently certified graph data with independence number at least
23 and the double-star RGA2 formula violates `alpha ≤ RGA2`.

The hypotheses deliberately expose the two graph-theoretic obligations not
proved in this arithmetic-only file. -/
@[category test, AMS 5]
theorem violates_alpha_le_rga2_of_certificate
    (alpha : ℕ) (rga2 : ℝ)
    (hIndependent : 23 ≤ alpha)
    (hRga2 : rga2 =
      1 + 55 * Real.sqrt 13 / 19 + 40 * Real.sqrt 14 / 13) :
    ¬(alpha : ℝ) ≤ rga2 := by
  intro hBound
  have hTwentyThree : (23 : ℝ) ≤ alpha := by
    exact_mod_cast hIndependent
  rw [hRga2] at hBound
  have hStrict := double_star_11_12_rga2_lt_twenty_three
  linarith

/-- For the balanced `(12, 12)` double star, a spoke radical reduces from
`sqrt (14 * 26)` to `2 * sqrt 91`. -/
@[category test, AMS 5]
lemma sqrt_fourteen_mul_twenty_six :
    Real.sqrt ((14 : ℝ) * 26) = 2 * Real.sqrt 91 := by
  rw [show (14 : ℝ) * 26 = 4 * 91 by norm_num,
    Real.sqrt_mul (by positivity : (0 : ℝ) ≤ 4)]
  norm_num <;> ring

/-- The center edge and 24 spokes of the balanced `(12, 12)` double star
reduce to a particularly short closed form. -/
@[category test, AMS 5]
lemma balanced_edge_class_decomposition :
    2 * Real.sqrt ((26 : ℝ) * 26) / (26 + 26) +
        24 * (2 * Real.sqrt ((14 : ℝ) * 26) / (14 + 26)) =
      1 + 12 * Real.sqrt 91 / 5 := by
  rw [sqrt_fourteen_mul_twenty_six]
  norm_num <;> ring

/-- A second arithmetic certificate from the balanced `(12, 12)` double star.
Its 24 leaves are independent and its exact RGA2 value is below 24. -/
@[category test, AMS 5]
theorem double_star_12_12_rga2_lt_twenty_four :
    (1 : ℝ) + 12 * Real.sqrt 91 / 5 < 24 := by
  have h91 : Real.sqrt (91 : ℝ) < 191 / 20 := by
    apply (Real.sqrt_lt' (by norm_num : (0 : ℝ) < 191 / 20)).2
    norm_num
  nlinarith

/-- The balanced strict certificate in its unsimplified edge-class form. -/
@[category test, AMS 5]
theorem double_star_12_12_edge_sum_lt_twenty_four :
    2 * Real.sqrt ((26 : ℝ) * 26) / (26 + 26) +
        24 * (2 * Real.sqrt ((14 : ℝ) * 26) / (14 + 26)) < 24 := by
  rw [balanced_edge_class_decomposition]
  exact double_star_12_12_rga2_lt_twenty_four

end Graffiti3.Conjecture2
