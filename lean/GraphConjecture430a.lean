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
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Eccentricity
import Mathlib.Combinatorics.SimpleGraph.Hasse

/-!
# Written on the Wall II - Conjecture 430a

*Reference:*
[E. DeLaVina, Written on the Wall II, Conjectures of Graffiti.pc](http://cms.dt.uh.edu/faculty/delavinae/research/wowII/)

The source conjectures that every connected graph `G` of order greater than
three satisfies

`i(G) ≤ α(G[N(C)]) + 2 floor(CW(G) - 1)`,

where `C` is the center, `N(C)` is the union of the open neighborhoods of its
vertices, and `CW(G) = ∑ v, 1 / (degree(v) + 1)` is the Caro--Wei sum.

The counterexample is the nonuniform clique blow-up of `P₇` with blob orders
`(1,4,12,19,12,4,1)`.  It has independent domination number three, while the
center is the middle clique, `α(G[N(C)]) = 2`, and
`CW(G) = 51123/25585 < 2`.  Thus the conjectured inequality reads `3 ≤ 2`.

The certificate uses the library's independent domination number and
independence number.  Center membership is expressed by the finite computable
eccentricity and radius, which equal their graph-theoretic counterparts for
connected finite graphs.  No unproved axiom or `sorry` is used.
-/

namespace WrittenOnTheWallII.GraphConjecture430a

open Classical SimpleGraph Finset

/-- Blob index in the `(1,4,12,19,12,4,1)` blow-up of `P₇`. -/
def blob (v : Fin 53) : Fin 7 :=
  if v.1 < 1 then 0 else if v.1 < 5 then 1 else if v.1 < 17 then 2
  else if v.1 < 36 then 3 else if v.1 < 48 then 4 else if v.1 < 52 then 5 else 6

/-- The nonuniform `P₇` clique blow-up on 53 vertices. -/
def P7Blowup : SimpleGraph (Fin 53) where
  Adj u v := u ≠ v ∧
    (blob u = blob v ∨ (blob u).1 + 1 = (blob v).1 ∨ (blob v).1 + 1 = (blob u).1)
  symm := by
    rintro u v ⟨hne, h⟩
    exact ⟨hne.symm, h.elim (fun h => Or.inl h.symm)
      (fun h => h.elim (fun h => Or.inr (Or.inr h)) (fun h => Or.inr (Or.inl h)))⟩
  loopless := by intro v h; exact h.1 rfl

instance : DecidableRel P7Blowup.Adj := fun u v =>
  inferInstanceAs (Decidable (u ≠ v ∧
    (blob u = blob v ∨ (blob u).1 + 1 = (blob v).1 ∨ (blob v).1 + 1 = (blob u).1)))

/-- DeLaViña's `N(S)`: the union of open vertex neighborhoods.  This need not
be disjoint from `S` when `G[S]` contains edges. -/
def setNeighborhood {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Finset V :=
  Finset.univ.filter fun v => ∃ u ∈ S, G.Adj u v

/-- The exact rational Caro--Wei sum. -/
def caroWei {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] : ℚ :=
  ∑ v : V, 1 / ((G.degree v + 1 : ℕ) : ℚ)

/-- The exact finite reading of WOWII Conjecture 430a.  Both sides are placed
in `ℤ`, matching the integer-valued floor in the printed statement. -/
def conjecture430aExactStatement : Prop :=
  ∀ (V : Type) [Fintype V] [DecidableEq V] [Nonempty V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
    G.Connected → 3 < Fintype.card V → (
      let center := Finset.univ.filter fun v => G.eccent v = G.radius
      (G.indepDominationNumber : ℤ) ≤
        ((G.induce (setNeighborhood G center : Set V)).indepNum : ℤ) +
          2 * ⌊caroWei G - 1⌋)

theorem P7Blowup_connected : P7Blowup.Connected := by
  have hle : SimpleGraph.pathGraph 53 ≤ P7Blowup := by
    intro u v huv
    rw [SimpleGraph.pathGraph_adj] at huv
    revert u v
    native_decide
  exact (SimpleGraph.pathGraph_connected 52).mono hle

/-- Three mutually separated blobs give an independent dominating set. -/
def threeWitness : Finset (Fin 53) := {0, 17, 52}

theorem threeWitness_independent :
    P7Blowup.IsIndepSet (threeWitness : Set (Fin 53)) := by
  intro u hu v hv huv
  change u ∈ threeWitness at hu
  change v ∈ threeWitness at hv
  revert u v
  native_decide

theorem threeWitness_dominating :
    P7Blowup.IsDominating (threeWitness : Set (Fin 53)) := by
  intro v
  change v ∈ threeWitness ∨ ∃ w ∈ threeWitness, P7Blowup.Adj v w
  revert v
  native_decide

theorem threeWitness_card : threeWitness.card = 3 := by native_decide

/-- No set with zero, one, or two specified vertices is independently
dominating.  This checks `1 + 53 + 53²` small candidates directly, without
ever constructing the full powerset of the 53-vertex type. -/
theorem no_empty_independent_dominating :
    ¬P7Blowup.IsIndepDominating (∅ : Set (Fin 53)) := by
  intro h
  exact (h.2 0).elim (by simp) (by simp)

theorem no_singleton_independent_dominating :
    ∀ u : Fin 53, ¬P7Blowup.IsIndepDominating ({u} : Set (Fin 53)) := by
  intro u h
  have hd : ∀ v : Fin 53,
      v = u ∨ P7Blowup.Adj v u := by
    intro v
    rcases h.2 v with hv | ⟨w, hw, hvw⟩
    · left
      simpa only [Set.mem_singleton_iff] using hv
    · right
      have hwu : w = u := by simpa only [Set.mem_singleton_iff] using hw
      simpa [hwu] using hvw
  have hn : ∀ u : Fin 53, ¬(∀ v : Fin 53,
      v = u ∨ P7Blowup.Adj v u) := by
    native_decide
  exact hn u hd

/-- One representative vertex from each blob. -/
def representative (k : Fin 7) : Fin 53 :=
  ![0, 1, 5, 17, 36, 48, 52] k

theorem blob_representative : ∀ k : Fin 7, blob (representative k) = k := by
  native_decide

/-- Closed-neighborhood incidence in the seven-vertex path quotient. -/
def quotientNear (k a : Fin 7) : Prop :=
  k = a ∨ k.1 + 1 = a.1 ∨ a.1 + 1 = k.1

instance quotientNear_decidable (k a : Fin 7) : Decidable (quotientNear k a) :=
  inferInstanceAs (Decidable (k = a ∨ k.1 + 1 = a.1 ∨ a.1 + 1 = k.1))

/-- Two equal or nonadjacent positions of `P₇` cannot dominate its quotient.
This is the only exhaustive lower-bound certificate: 49 pairs on `Fin 7`. -/
theorem quotient_no_two_cover :
    ∀ a b : Fin 7,
      (a = b ∨ ¬(a.1 + 1 = b.1 ∨ b.1 + 1 = a.1)) →
      ¬∀ k : Fin 7, quotientNear k a ∨ quotientNear k b := by
  native_decide +revert

theorem no_pair_independent_dominating :
    ∀ u v : Fin 53, ¬P7Blowup.IsIndepDominating ({u, v} : Set (Fin 53)) := by
  intro u v h
  let a := blob u
  let b := blob v
  have hqind : a = b ∨ ¬(a.1 + 1 = b.1 ∨ b.1 + 1 = a.1) := by
    by_cases huv : u = v
    · left
      simp [a, b, huv]
    · by_cases hab : a = b
      · exact Or.inl hab
      · right
        intro hadj
        have huvAdj : P7Blowup.Adj u v := by
          exact ⟨huv, Or.inr hadj⟩
        exact h.1 (by simp) (by simp) huv huvAdj
  apply quotient_no_two_cover a b hqind
  intro k
  have hk := h.2 (representative k)
  rcases hk with hk | ⟨y, hy, hky⟩
  · simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hk
    rcases hk with hk | hk
    · left; left
      rw [← blob_representative k, hk]
    · right; left
      rw [← blob_representative k, hk]
  · simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hy
    rcases hy with rfl | rfl
    · left
      rcases hky.2 with hsame | hforward | hbackward
      · rw [blob_representative k] at hsame
        exact Or.inl (by simpa [a] using hsame)
      · exact Or.inr (Or.inl (by simpa [a, blob_representative] using hforward))
      · exact Or.inr (Or.inr (by simpa [a, blob_representative] using hbackward))
    · right
      rcases hky.2 with hsame | hforward | hbackward
      · rw [blob_representative k] at hsame
        exact Or.inl (by simpa [b] using hsame)
      · exact Or.inr (Or.inl (by simpa [b, blob_representative] using hforward))
      · exact Or.inr (Or.inr (by simpa [b, blob_representative] using hbackward))

lemma no_independent_dominating_of_card_lt_three (D : Finset (Fin 53))
    (hD : D.card < 3) : ¬P7Blowup.IsIndepDominating (D : Set (Fin 53)) := by
  interval_cases hcard : D.card
  · rw [Finset.card_eq_zero.mp hcard]
    simpa using no_empty_independent_dominating
  · obtain ⟨u, rfl⟩ := Finset.card_eq_one.mp hcard
    simpa using no_singleton_independent_dominating u
  · obtain ⟨u, v, _huv, rfl⟩ := Finset.card_eq_two.mp hcard
    simpa using no_pair_independent_dominating u v

theorem P7Blowup_indepDominationNumber :
    P7Blowup.indepDominationNumber = 3 := by
  apply le_antisymm
  · unfold SimpleGraph.indepDominationNumber
    apply csInf_le
    · exact ⟨0, fun _ _ => Nat.zero_le _⟩
    · exact ⟨threeWitness,
        ⟨threeWitness_independent, threeWitness_dominating, threeWitness_card⟩⟩
  · unfold SimpleGraph.indepDominationNumber
    apply le_csInf
    · exact ⟨3, threeWitness,
        ⟨threeWitness_independent, threeWitness_dominating, threeWitness_card⟩⟩
    · intro n hn
      obtain ⟨D, hD⟩ := hn
      rw [← hD.card_eq]
      by_contra hlt
      exact no_independent_dominating_of_card_lt_three D (by omega)
        ⟨hD.isIndep, hD.isDominating⟩

/-- The center consists exactly of the middle blob. -/
theorem P7Blowup_center :
    (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius) =
      Finset.univ.filter fun v => blob v = 3 := by
  have hlookup : ∀ v : Fin 53,
      P7Blowup.computable_eccent v = ![6, 5, 4, 3, 4, 5, 6] (blob v) := by
    native_decide +revert
  have hr : P7Blowup.computable_radius = 3 := by
    unfold SimpleGraph.computable_radius
    simp_rw [hlookup]
    native_decide
  ext v
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  rw [SimpleGraph.eccent_eq_computable P7Blowup P7Blowup_connected,
    SimpleGraph.radius_eq_computable P7Blowup P7Blowup_connected,
    hlookup, hr]
  revert v
  native_decide

/-- The union of the open neighborhoods of the middle clique consists of the
three middle blobs.  In particular, it includes the center clique itself. -/
theorem P7Blowup_center_neighborhood :
    setNeighborhood P7Blowup
      (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius) =
      Finset.univ.filter fun v => blob v = 2 ∨ blob v = 3 ∨ blob v = 4 := by
  rw [P7Blowup_center]
  native_decide

/-- Every independent subset of the three-vertex quotient path has size at
most two. -/
theorem middle_path_independent_bound :
    ∀ q : Finset (Fin 7),
      (∀ x ∈ q, x = 2 ∨ x = 3 ∨ x = 4) →
      (∀ x ∈ q, ∀ y ∈ q, x ≠ y →
        ¬(x.1 + 1 = y.1 ∨ y.1 + 1 = x.1)) → q.card ≤ 2 := by
  native_decide

lemma center_neighborhood_independent_card_le_two
    (s : Finset {v : Fin 53 // v ∈ setNeighborhood P7Blowup
      (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)})
    (hs : (P7Blowup.induce
      (setNeighborhood P7Blowup
        (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius) :
          Set (Fin 53))).IsIndepSet
        (↑s : Set {v : Fin 53 //
          v ∈ setNeighborhood P7Blowup
            (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)})) :
      s.card ≤ 2 := by
  let f : {v : Fin 53 // v ∈ setNeighborhood P7Blowup
    (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)} → Fin 7 :=
    fun v => blob v.1
  let q : Finset (Fin 7) := s.image f
  have hf_inj : Set.InjOn f (s : Set _) := by
    intro u hu v hv huv
    by_contra hne
    have hadj : P7Blowup.Adj u.1 v.1 := ⟨Subtype.coe_injective.ne hne, Or.inl huv⟩
    exact hs hu hv hne (by exact hadj)
  have hcard : q.card = s.card := Finset.card_image_iff.mpr hf_inj
  have hqmid : ∀ x ∈ q, x = 2 ∨ x = 3 ∨ x = 4 := by
    intro x hx
    obtain ⟨v, hv, rfl⟩ := Finset.mem_image.mp hx
    have hvN := v.2
    have hvN' : v.1 ∈ Finset.univ.filter fun v =>
        blob v = 2 ∨ blob v = 3 ∨ blob v = 4 := by
      rw [← P7Blowup_center_neighborhood]
      exact hvN
    simpa [f] using (Finset.mem_filter.mp hvN').2
  have hqind : ∀ x ∈ q, ∀ y ∈ q, x ≠ y →
      ¬(x.1 + 1 = y.1 ∨ y.1 + 1 = x.1) := by
    intro x hx y hy hxy hcon
    obtain ⟨u, hu, rfl⟩ := Finset.mem_image.mp hx
    obtain ⟨v, hv, hvblob⟩ := Finset.mem_image.mp hy
    subst hvblob
    have huv : u ≠ v := by
      intro h
      subst v
      exact hxy rfl
    have hadj : P7Blowup.Adj u.1 v.1 := by
      exact ⟨Subtype.coe_injective.ne huv,
        Or.inr (hcon.elim Or.inl Or.inr)⟩
    exact hs hu hv huv hadj
  rw [← hcard]
  exact middle_path_independent_bound q hqmid hqind

theorem P7Blowup_center_neighborhood_indepNum :
    (P7Blowup.induce
      (setNeighborhood P7Blowup
        (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius) :
          Set (Fin 53))).indepNum = 2 := by
  apply le_antisymm
  · unfold SimpleGraph.indepNum
    apply csSup_le
    · exact ⟨0, ⟨∅, ⟨by simp, rfl⟩⟩⟩
    · rintro n ⟨s, hs, rfl⟩
      exact center_neighborhood_independent_card_le_two s hs
  · let a : {v : Fin 53 // v ∈ setNeighborhood P7Blowup
        (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)} :=
      ⟨5, by rw [P7Blowup_center_neighborhood]; native_decide⟩
    let b : {v : Fin 53 // v ∈ setNeighborhood P7Blowup
        (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)} :=
      ⟨36, by rw [P7Blowup_center_neighborhood]; native_decide⟩
    let pair : Finset {v : Fin 53 //
      v ∈ setNeighborhood P7Blowup
        (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)} := {a, b}
    have hpair :
        (P7Blowup.induce
          (setNeighborhood P7Blowup
            (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius) :
              Set (Fin 53))).IsIndepSet
            (↑pair : Set {v : Fin 53 //
              v ∈ setNeighborhood P7Blowup
                (Finset.univ.filter fun v => P7Blowup.eccent v = P7Blowup.radius)}) := by
      intro u hu v hv huv
      change u ∈ ({a, b} : Finset _) at hu
      change v ∈ ({a, b} : Finset _) at hv
      simp only [Finset.mem_insert, Finset.mem_singleton] at hu hv
      rcases hu with rfl | rfl <;> rcases hv with rfl | rfl
      · exact (huv rfl).elim
      · intro hadj
        change P7Blowup.Adj 5 36 at hadj
        exact (by native_decide : ¬P7Blowup.Adj 5 36) hadj
      · intro hadj
        change P7Blowup.Adj 36 5 at hadj
        exact (by native_decide : ¬P7Blowup.Adj 36 5) hadj
      · exact (huv rfl).elim
    have hcard : pair.card = 2 := by native_decide
    exact hcard ▸ hpair.card_le_indepNum

theorem P7Blowup_caroWei : caroWei P7Blowup = 51123 / 25585 := by
  native_decide

theorem P7Blowup_floor_caroWei_sub_one : ⌊caroWei P7Blowup - 1⌋ = 0 := by
  rw [P7Blowup_caroWei]
  norm_num

/-- The exact intended reading of WOWII Conjecture 430a is false. -/
theorem conjecture430a_exact_false : ¬conjecture430aExactStatement := by
  intro h
  have h430 := h (Fin 53) P7Blowup P7Blowup_connected (by norm_num)
  dsimp only at h430
  rw [P7Blowup_indepDominationNumber,
    P7Blowup_center_neighborhood_indepNum,
    P7Blowup_floor_caroWei_sub_one] at h430
  norm_num at h430

/-- WOWII Conjecture 430a has answer `False`, witnessed by the nonuniform
`P₇` clique blow-up with blob orders `(1,4,12,19,12,4,1)`. -/
@[category research solved, AMS 5]
theorem conjecture430a : answer(False) ↔ conjecture430aExactStatement := by
  rw [false_iff]
  exact conjecture430a_exact_false

#print axioms conjecture430a

end WrittenOnTheWallII.GraphConjecture430a
