/-
Copyright 2025 The Formal Conjectures Authors.

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
# Probe
-/

open Set Filter

set_option linter.style.ams_attribute false
set_option linter.style.category_attribute false

namespace Probe

def AdditiveBasisCondition (A : Set ℕ) : Prop :=
  ∀ (k : ℕ), ∃ (n : ℕ) (a : ℕ), a ∈ A ∧ k = a + n^2

-- (a) the limsup in the current declaration elaborates in `ℝ`
example : (fun (A : Set ℕ) => Filter.atTop.limsup (fun N => (A ∩ Icc 1 N).ncard / √N)) =
    (fun (A : Set ℕ) => Filter.atTop.limsup (fun N => ((A ∩ Icc 1 N).ncard : ℝ) / √(N : ℝ))) := rfl

-- (b) `1 < limsup` in `ℝ` forces the eventual-upper-bound set to be nonempty
theorem lt_limsup_nonempty (u : ℕ → ℝ) (h : (1 : ℝ) < Filter.atTop.limsup u) :
    {a : ℝ | ∀ᶠ n in Filter.atTop, u n ≤ a}.Nonempty := by
  by_contra hc
  rw [Set.not_nonempty_iff_eq_empty] at hc
  rw [Filter.limsup_eq, hc, Real.sInf_empty] at h
  linarith

-- (c) A = ℕ satisfies the additive basis condition
theorem univ_abc : AdditiveBasisCondition (Set.univ : Set ℕ) :=
  fun k => ⟨0, k, Set.mem_univ k, by ring⟩

-- (d) the ratio for A = ℕ is √N (for N ≥ 1) hence unbounded, so the set in (b) is empty
theorem univ_ratio (N : ℕ) :
    (((Set.univ : Set ℕ) ∩ Icc 1 N).ncard : ℝ) / √(N : ℝ) = (N : ℝ) / √(N : ℝ) := by
  rw [Set.univ_inter]
  congr 2
  rw [Set.ncard_eq_toFinset_card']
  simp

theorem univ_not_witness :
    ¬ ((1 : ℝ) < Filter.atTop.limsup
      (fun N : ℕ => (((Set.univ : Set ℕ) ∩ Icc 1 N).ncard : ℝ) / √(N : ℝ))) := by
  intro h
  obtain ⟨a, ha⟩ := lt_limsup_nonempty _ h
  simp only [Set.mem_setOf_eq] at ha
  have hgo : Filter.Tendsto (fun N : ℕ => √(N : ℝ)) Filter.atTop Filter.atTop :=
    Real.tendsto_sqrt_atTop.comp tendsto_natCast_atTop_atTop
  have hbig : ∀ᶠ N : ℕ in Filter.atTop, a < √(N : ℝ) := hgo.eventually_gt_atTop a
  obtain ⟨N, hN1, hN2⟩ := ((ha.and hbig).and (Filter.eventually_gt_atTop 0)).exists
  obtain ⟨hle, hlt⟩ := hN1
  rw [univ_ratio, Real.div_sqrt] at hle
  linarith

end Probe

#print axioms Probe.univ_not_witness
#print axioms Probe.lt_limsup_nonempty
#print axioms Probe.univ_abc
#print axioms Probe.univ_ratio
