import FormalConjectures.Paper.LatinTableau

/-!
# Latin Tableau corner-exchange lemmas

Reusable algebraic and coloring lemmas extracted from the order-15
bottom-corner theorem signal. These lemmas do not prove the Latin Tableau
Conjecture or the remaining Ferrers exchange-existence step.
-/

namespace LatinTableau.CornerExchange

open Set SimpleGraph

variable {V : Type*}

/-- Every concrete union of `k` independent sets is bounded by the cumulative
optimum `indepNumK`. -/
theorem family_ncard_le_indepNumK [Finite V]
    (G : SimpleGraph V) (k : ℕ) (f : Fin k → Set V)
    (hf : ∀ i, G.IsIndepSet (f i)) :
    (⋃ i, f i).ncard ≤ G.indepNumK k := by
  apply le_csSup
  · refine ⟨Nat.card V, ?_⟩
    rintro n ⟨g, _hg, rfl⟩
    exact Set.ncard_le_card _
  · exact ⟨f, hf, rfl⟩

/-- Passing to an induced graph cannot increase the cumulative optimum. -/
theorem induce_indepNumK_le [Finite V]
    (G : SimpleGraph V) (s : Set V) (k : ℕ) :
    (G.induce s).indepNumK k ≤ G.indepNumK k := by
  unfold SimpleGraph.indepNumK
  apply csSup_le
  · refine ⟨0, ?_⟩
    refine ⟨fun _ ↦ ∅, ?_, by simp⟩
    intro i
    simp [SimpleGraph.isIndepSet_iff]
  · rintro n ⟨f, hf, rfl⟩
    let f' : Fin k → Set V := fun i ↦ Subtype.val '' f i
    have hf' : ∀ i, G.IsIndepSet (f' i) := by
      rintro i _ ⟨x, hx, rfl⟩ _ ⟨y, hy, rfl⟩ hxy hadj
      exact hf i hx hy (fun h ↦ hxy (congrArg Subtype.val h))
        (SimpleGraph.induce_adj.mpr hadj)
    have hcard : (⋃ i, f' i).ncard = (⋃ i, f i).ncard := by
      rw [show (⋃ i, f' i) = Subtype.val '' (⋃ i, f i) by
        ext w
        simp [f']]
      exact Set.ncard_image_of_injective _ Subtype.val_injective
    rw [← hcard]
    exact family_ncard_le_indepNumK G k f' hf'

/-- Deleting one vertex changes the actual cumulative optimum by at most one
in the downward direction. The graph on the right is induced on the vertices
different from `v`. -/
theorem indepNumK_le_induce_ne_add_one [Finite V]
    (G : SimpleGraph V) (v : V) (k : ℕ) :
    G.indepNumK k ≤ (G.induce {w | w ≠ v}).indepNumK k + 1 := by
  unfold SimpleGraph.indepNumK
  apply csSup_le
  · refine ⟨0, ?_⟩
    refine ⟨fun _ ↦ ∅, ?_, by simp⟩
    intro i
    simp [SimpleGraph.isIndepSet_iff]
  · rintro n ⟨f, hf, rfl⟩
    let f' : Fin k → Set {w : V // w ≠ v} := fun i ↦ {w | (w : V) ∈ f i}
    have hf' : ∀ i, (G.induce {w | w ≠ v}).IsIndepSet (f' i) := by
      intro i x hx y hy hxy hadj
      exact hf i hx hy (fun h ↦ hxy (Subtype.ext h))
        (SimpleGraph.induce_adj.mp hadj)
    have hcard : (⋃ i, f' i).ncard = ((⋃ i, f i) \ {v}).ncard := by
      rw [show (⋃ i, f i) \ {v} = (⋃ i, f i) ∩ {w | w ≠ v} by ext; simp]
      rw [← Set.ncard_subtype (fun w : V ↦ w ≠ v) (⋃ i, f i)]
      congr 1
      ext w
      simp [f']
    calc
      (⋃ i, f i).ncard ≤ ((⋃ i, f i) \ {v}).ncard + 1 := by
        simpa using Set.ncard_le_ncard_diff_add_ncard (⋃ i, f i) ({v} : Set V)
      _ = (⋃ i, f' i).ncard + 1 := by rw [hcard]
      _ ≤ (G.induce {w | w ≠ v}).indepNumK k + 1 :=
        Nat.add_le_add_right (family_ncard_le_indepNumK _ _ f' hf') 1

/-- Deleting one vertex changes `indepNumK` by at most one. -/
theorem indepNumK_induce_ne_stable [Finite V]
    (G : SimpleGraph V) (v : V) (k : ℕ) :
    (G.induce {w | w ≠ v}).indepNumK k ≤ G.indepNumK k ∧
      G.indepNumK k ≤ (G.induce {w | w ≠ v}).indepNumK k + 1 :=
  ⟨induce_indepNumK_le G _ k, indepNumK_le_induce_ne_add_one G v k⟩

/-- The cumulative optimum's deletion difference is literally binary, in the
form consumed by the abstract profile lemmas below. -/
theorem indepNumK_eq_induce_ne_or_eq_add_one [Finite V]
    (G : SimpleGraph V) (v : V) (k : ℕ) :
    G.indepNumK k = (G.induce {w | w ≠ v}).indepNumK k ∨
      G.indepNumK k = (G.induce {w | w ≠ v}).indepNumK k + 1 := by
  rcases indepNumK_induce_ne_stable G v k with ⟨hlower, hupper⟩
  omega

/-- If `dA` and `dB` are consecutive differences of cumulative profiles `A`
and `B`, and `delta` is their cumulative difference, then the difference of
the profiles is the consecutive difference of `delta`. Using `Int` avoids
hidden truncated-subtraction hypotheses. -/
theorem profile_difference_eq_delta_step
    (A B dA dB delta : ℕ → ℤ) (k : ℕ)
    (hdA : dA (k + 1) = A (k + 1) - A k)
    (hdB : dB (k + 1) = B (k + 1) - B k)
    (hdelta : ∀ j, delta j = A j - B j) :
    dA (k + 1) - dB (k + 1) = delta (k + 1) - delta k := by
  rw [hdA, hdB, hdelta, hdelta]
  ring

/-- When deletion changes every cumulative optimum by zero or one, a single
profile coordinate can change only by `-1`, `0`, or `1`. -/
theorem binary_delta_bounds_profile_change
    (A B dA dB delta : ℕ → ℤ) (k : ℕ)
    (hdA : dA (k + 1) = A (k + 1) - A k)
    (hdB : dB (k + 1) = B (k + 1) - B k)
    (hdelta : ∀ j, delta j = A j - B j)
    (hbinary : ∀ j, delta j = 0 ∨ delta j = 1) :
    dA (k + 1) - dB (k + 1) = -1 ∨
      dA (k + 1) - dB (k + 1) = 0 ∨
      dA (k + 1) - dB (k + 1) = 1 := by
  rw [profile_difference_eq_delta_step A B dA dB delta k hdA hdB hdelta]
  rcases hbinary (k + 1) with hnext | hnext <;>
    rcases hbinary k with hprev | hprev <;> omega

/-- The consecutive difference of a positive threshold step is one at the
threshold and zero elsewhere. -/
theorem threshold_delta_step (c k : ℕ) :
    ((if c ≤ k + 1 then (1 : ℤ) else 0) - if c ≤ k then 1 else 0) =
      if k + 1 = c then 1 else 0 := by
  split_ifs <;> omega

/-- A threshold cumulative difference forces a single basis-vector change in
the successive profile. -/
theorem threshold_delta_implies_basis_profile_change
    (A B dA dB delta : ℕ → ℤ) (c k : ℕ)
    (hdA : dA (k + 1) = A (k + 1) - A k)
    (hdB : dB (k + 1) = B (k + 1) - B k)
    (hdelta : ∀ j, delta j = A j - B j)
    (hthreshold : ∀ j, delta j = if c ≤ j then 1 else 0) :
    dA (k + 1) - dB (k + 1) = if k + 1 = c then 1 else 0 := by
  rw [profile_difference_eq_delta_step A B dA dB delta k hdA hdB hdelta,
    hthreshold, hthreshold]
  exact threshold_delta_step c k

section Coloring

open SimpleGraph

variable {V Color : Type*}

/-- Extend a proper coloring across one new `Option.none` vertex. Old-old
edges must already belong to `G`; every new-old edge must avoid `c`. -/
def extendColoringAtNone
    (G : SimpleGraph V) (H : SimpleGraph (Option V)) (C : G.Coloring Color)
    (c : Color)
    (hOld : ∀ {v w}, H.Adj (some v) (some w) → G.Adj v w)
    (hNew : ∀ {v}, H.Adj none (some v) → c ≠ C v) :
    H.Coloring Color :=
  SimpleGraph.Coloring.mk
    (fun v ↦ match v with | none => c | some w => C w)
    (by
      intro v w hvw
      cases v with
      | none =>
          cases w with
          | none => exact (H.loopless none hvw).elim
          | some w => exact hNew hvw
      | some v =>
          cases w with
          | none => exact (hNew hvw.symm).symm
          | some w => exact C.valid (hOld hvw))

@[simp] theorem extendColoringAtNone_apply_none
    (G : SimpleGraph V) (H : SimpleGraph (Option V)) (C : G.Coloring Color)
    (c : Color)
    (hOld : ∀ {v w}, H.Adj (some v) (some w) → G.Adj v w)
    (hNew : ∀ {v}, H.Adj none (some v) → c ≠ C v) :
    extendColoringAtNone G H C c hOld hNew none = c := rfl

@[simp] theorem extendColoringAtNone_apply_some
    (G : SimpleGraph V) (H : SimpleGraph (Option V)) (C : G.Coloring Color)
    (c : Color)
    (hOld : ∀ {v w}, H.Adj (some v) (some w) → G.Adj v w)
    (hNew : ∀ {v}, H.Adj none (some v) → c ≠ C v) (v : V) :
    extendColoringAtNone G H C c hOld hNew (some v) = C v := rfl

end Coloring

end LatinTableau.CornerExchange
