import GraphConjecture59CyclicCardRectangle

/-!
# WOWII 59: end-to-end relabeling of the deletion-critical core

The two three-vertex color classes are explicitly relabeled by `Fin 3` and
the cyclic-card rectangle theorem is transported to the exact matrix profile.
-/

namespace WrittenOnTheWallII.GraphConjecture59RelabeledCoreProfile

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CornerStructure
open WrittenOnTheWallII.GraphConjecture59CyclicCardRectangle
open WrittenOnTheWallII.GraphConjecture59CoreProfileMultiplicity

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

def matrixRowDegree (E : Fin 3 → Fin 3 → Bool) (i : Fin 3) : ℕ :=
  (univ.filter fun j ↦ E i j).card

def matrixColDegree (E : Fin 3 → Fin 3 → Bool) (j : Fin 3) : ℕ :=
  (univ.filter fun i ↦ E i j).card

def matrixEdgeCount (E : Fin 3 → Fin 3 → Bool) : ℕ :=
  ∑ i, matrixRowDegree E i

def matrixDegreeThreeCount (E : Fin 3 → Fin 3 → Bool) : ℕ :=
  (univ.filter fun i ↦ matrixRowDegree E i = 3).card +
  (univ.filter fun j ↦ matrixColDegree E j = 3).card

def MatrixDeletionCritical (E : Fin 3 → Fin 3 → Bool) : Prop :=
  (∀ d, 2 ≤ (univ.filter fun j ↦
    E (nextIndex d) j && E (previousIndex d) j).card) ∧
  (∀ d, 2 ≤ (univ.filter fun i ↦
    E i (nextIndex d) && E i (previousIndex d)).card)

instance (E : Fin 3 → Fin 3 → Bool) : Decidable (MatrixDeletionCritical E) := by
  unfold MatrixDeletionCritical
  infer_instance

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
/-- Label-independent form of the v26 finite classifier. -/
theorem matrix_profile_of_deletionCritical
    : ∀ E : Fin 3 → Fin 3 → Bool, MatrixDeletionCritical E →
      (matrixEdgeCount E = 8 ∧ matrixDegreeThreeCount E = 4) ∨
      (matrixEdgeCount E = 9 ∧ matrixDegreeThreeCount E = 6) := by
  decide

/-- The `f=4` corner supplies a rectangle whose sides agree with a fixed
proper two-coloring of the six-core. -/
theorem colored_corner_deletion_rectangle
    (G : SimpleGraph V) (S : Finset V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6) (hf : G.largestInducedForestSize = 4)
    {z : V} (hz : z ∈ S) :
    ∃ a b x y,
      a ∈ S.erase z ∧ b ∈ S.erase z ∧
      x ∈ S.erase z ∧ y ∈ S.erase z ∧
      c a = 0 ∧ c b = 0 ∧ c x = 1 ∧ c y = 1 ∧
      a ≠ b ∧ x ≠ y ∧
      G.Adj a x ∧ G.Adj a y ∧ G.Adj b x ∧ G.Adj b y := by
  have hcardData := every_single_deletion_bipartite_and_cyclic
    G S hSbip hSsix hf hz
  let T := S.erase z
  let H := G.induce (T : Set V)
  let I : Set {v // v ∈ T} := {v | c v = 0}
  let X : Set {v // v ∈ T} := {v | c v = 1}
  have hTcard : T.card = 5 := by
    simp [T, card_erase_of_mem hz, hSsix]
  have htypecard : Fintype.card {v // v ∈ T} = 5 := by
    simpa using hTcard
  have hcyc : ¬H.IsAcyclic := by simpa [H, T] using hcardData.2
  have hbw : H.IsBipartiteWith I X := by
    constructor
    · rw [Set.disjoint_left]
      intro v hvI hvX
      simp [I, X] at hvI hvX
      omega
    · intro u v huv
      have huT : (u : V) ∈ T := u.property
      have hvT : (v : V) ∈ T := v.property
      have hne := hc u (mem_erase.mp huT).2 v (mem_erase.mp hvT).2 huv
      by_cases hu : c u = 0
      · have hv0 : c v ≠ 0 := fun hv ↦ hne (hu.trans hv.symm)
        have hv : c v = 1 := Fin.eq_one_of_ne_zero _ hv0
        exact Or.inl ⟨by simpa [I] using hu, by simpa [X] using hv⟩
      · have hu1 : c u = 1 := Fin.eq_one_of_ne_zero _ hu
        have hv1 : c v ≠ 1 := fun hv ↦ hne (hu1.trans hv.symm)
        have hv : c v = 0 := by
          by_contra hv0
          exact hv1 (Fin.eq_one_of_ne_zero _ hv0)
        exact Or.inr ⟨by simpa [X] using hu1, by simpa [I] using hv⟩
  obtain ⟨a, b, x, y, haI, hbI, hxX, hyX, hab, hxy,
      hax, hay, hbx, hby⟩ :=
    exists_rectangle_of_bipartiteWith_card_five
      H I X htypecard hbw hcyc
  exact ⟨a, b, x, y, a.property, b.property, x.property, y.property,
    haI, hbI, hxX, hyX, by exact_mod_cast hab, by exact_mod_cast hxy,
    hax, hay, hbx, hby⟩

lemma fin_three_survivor (p q d r : Fin 3)
    (hpd : p ≠ d) (hqd : q ≠ d) (hpq : p ≠ q) (hrd : r ≠ d) :
    r = p ∨ r = q := by
  fin_cases p <;> fin_cases q <;> fin_cases d <;> fin_cases r <;> simp_all

/-- Relabeling the two color classes transports all six deletion rectangles
to the exact common-neighbor conditions of `MatrixDeletionCritical`. -/
theorem relabeled_matrix_deletionCritical
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S A B : Finset V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6) (hf : G.largestInducedForestSize = 4)
    (hAmem : ∀ v, v ∈ A ↔ v ∈ S ∧ c v = 0)
    (hBmem : ∀ v, v ∈ B ↔ v ∈ S ∧ c v = 1)
    (eA : Fin 3 ≃ A) (eB : Fin 3 ≃ B) :
    let E : Fin 3 → Fin 3 → Bool :=
      fun i j ↦ decide (G.Adj (eA i) (eB j))
    MatrixDeletionCritical E := by
  dsimp
  let E : Fin 3 → Fin 3 → Bool :=
    fun i j ↦ decide (G.Adj (eA i) (eB j))
  change MatrixDeletionCritical E
  constructor
  · intro d
    have hz : ((eA d : A) : V) ∈ S := (hAmem _).mp (eA d).property |>.1
    obtain ⟨a, b, x, y, ha, hb, hx, hy, hca, hcb, hcx, hcy,
        hab, hxy, hax, hay, hbx, hby⟩ :=
      colored_corner_deletion_rectangle G S c hc hSbip hSsix hf hz
    have haA : a ∈ A := (hAmem _).mpr ⟨(mem_erase.mp ha).2, hca⟩
    have hbA : b ∈ A := (hAmem _).mpr ⟨(mem_erase.mp hb).2, hcb⟩
    have hxB : x ∈ B := (hBmem _).mpr ⟨(mem_erase.mp hx).2, hcx⟩
    have hyB : y ∈ B := (hBmem _).mpr ⟨(mem_erase.mp hy).2, hcy⟩
    let ia := eA.symm ⟨a, haA⟩
    let ib := eA.symm ⟨b, hbA⟩
    let jx := eB.symm ⟨x, hxB⟩
    let jy := eB.symm ⟨y, hyB⟩
    have hiad : ia ≠ d := by
      intro h
      have he := congrArg (fun q ↦ ((eA q : A) : V)) h
      simp [ia] at he
      exact (mem_erase.mp ha).1 he
    have hibd : ib ≠ d := by
      intro h
      have he := congrArg (fun q ↦ ((eA q : A) : V)) h
      simp [ib] at he
      exact (mem_erase.mp hb).1 he
    have hiab : ia ≠ ib := by
      intro h
      have he := congrArg (fun q ↦ ((eA q : A) : V)) h
      simp [ia, ib] at he
      exact hab he
    have hjxy : jx ≠ jy := by
      intro h
      have he := congrArg (fun q ↦ ((eB q : B) : V)) h
      simp [jx, jy] at he
      exact hxy he
    have hn : nextIndex d ≠ d := by fin_cases d <;> decide
    have hp : previousIndex d ≠ d := by fin_cases d <;> decide
    have hnext := fin_three_survivor ia ib d (nextIndex d) hiad hibd hiab hn
    have hprev := fin_three_survivor ia ib d (previousIndex d) hiad hibd hiab hp
    have adjOf (r : Fin 3) (hr : r = ia ∨ r = ib) (j : Fin 3)
        (hj : j = jx ∨ j = jy) : G.Adj (eA r) (eB j) := by
      rcases hr with rfl | rfl <;> rcases hj with rfl | rfl <;>
        simp [ia, ib, jx, jy] <;> assumption
    have memj (j : Fin 3) (hj : j = jx ∨ j = jy) :
        j ∈ univ.filter fun q ↦ E (nextIndex d) q && E (previousIndex d) q := by
      simp only [mem_filter, mem_univ, true_and, Bool.and_eq_true]
      constructor <;> simp only [E, decide_eq_true_eq] <;>
        apply adjOf <;> assumption
    have htwo := one_lt_card.mpr
      ⟨jx, memj jx (Or.inl rfl), jy, memj jy (Or.inr rfl), hjxy⟩
    omega
  · intro d
    have hz : ((eB d : B) : V) ∈ S := (hBmem _).mp (eB d).property |>.1
    obtain ⟨a, b, x, y, ha, hb, hx, hy, hca, hcb, hcx, hcy,
        hab, hxy, hax, hay, hbx, hby⟩ :=
      colored_corner_deletion_rectangle G S c hc hSbip hSsix hf hz
    have haA : a ∈ A := (hAmem _).mpr ⟨(mem_erase.mp ha).2, hca⟩
    have hbA : b ∈ A := (hAmem _).mpr ⟨(mem_erase.mp hb).2, hcb⟩
    have hxB : x ∈ B := (hBmem _).mpr ⟨(mem_erase.mp hx).2, hcx⟩
    have hyB : y ∈ B := (hBmem _).mpr ⟨(mem_erase.mp hy).2, hcy⟩
    let ia := eA.symm ⟨a, haA⟩
    let ib := eA.symm ⟨b, hbA⟩
    let jx := eB.symm ⟨x, hxB⟩
    let jy := eB.symm ⟨y, hyB⟩
    have hjxd : jx ≠ d := by
      intro h
      have he := congrArg (fun q ↦ ((eB q : B) : V)) h
      simp [jx] at he
      exact (mem_erase.mp hx).1 he
    have hjyd : jy ≠ d := by
      intro h
      have he := congrArg (fun q ↦ ((eB q : B) : V)) h
      simp [jy] at he
      exact (mem_erase.mp hy).1 he
    have hjxy : jx ≠ jy := by
      intro h
      have he := congrArg (fun q ↦ ((eB q : B) : V)) h
      simp [jx, jy] at he
      exact hxy he
    have hiab : ia ≠ ib := by
      intro h
      have he := congrArg (fun q ↦ ((eA q : A) : V)) h
      simp [ia, ib] at he
      exact hab he
    have hn : nextIndex d ≠ d := by fin_cases d <;> decide
    have hp : previousIndex d ≠ d := by fin_cases d <;> decide
    have hnext := fin_three_survivor jx jy d (nextIndex d) hjxd hjyd hjxy hn
    have hprev := fin_three_survivor jx jy d (previousIndex d) hjxd hjyd hjxy hp
    have adjOf (i : Fin 3) (hi : i = ia ∨ i = ib) (r : Fin 3)
        (hr : r = jx ∨ r = jy) : G.Adj (eA i) (eB r) := by
      rcases hi with rfl | rfl <;> rcases hr with rfl | rfl <;>
        simp [ia, ib, jx, jy] <;> assumption
    have memi (i : Fin 3) (hi : i = ia ∨ i = ib) :
        i ∈ univ.filter fun q ↦ E q (nextIndex d) && E q (previousIndex d) := by
      simp only [mem_filter, mem_univ, true_and, Bool.and_eq_true]
      constructor <;> simp only [E, decide_eq_true_eq] <;>
        apply adjOf <;> assumption
    have htwo := one_lt_card.mpr
      ⟨ia, memi ia (Or.inl rfl), ib, memi ib (Or.inr rfl), hiab⟩
    omega

/-- **End-to-end core profile.** The equivalences are constructed from the
two class-cardinality hypotheses; the resulting adjacency matrix has eight
or nine edges and degree profile `[3,3,3,3,2,2]` or `[3,3,3,3,3,3]`. -/
theorem exists_relabeling_with_exact_core_profile
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (c : V → Fin 2)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6) (hf : G.largestInducedForestSize = 4)
    (hclass : ∀ k : Fin 2, (S.filter fun v ↦ c v = k).card = 3) :
    ∃ (A B : Finset V) (eA : Fin 3 ≃ A) (eB : Fin 3 ≃ B),
      A = S.filter (fun v ↦ c v = 0) ∧
      B = S.filter (fun v ↦ c v = 1) ∧
      let E : Fin 3 → Fin 3 → Bool :=
        fun i j ↦ decide (G.Adj (eA i) (eB j))
      (matrixEdgeCount E = 8 ∧ matrixDegreeThreeCount E = 4) ∨
      (matrixEdgeCount E = 9 ∧ matrixDegreeThreeCount E = 6) := by
  let A := S.filter fun v ↦ c v = 0
  let B := S.filter fun v ↦ c v = 1
  have hAcard : Fintype.card A = 3 := by
    rw [Fintype.card_coe]
    exact hclass 0
  have hBcard : Fintype.card B = 3 := by
    rw [Fintype.card_coe]
    exact hclass 1
  let eA : Fin 3 ≃ A := (Fintype.equivFinOfCardEq hAcard).symm
  let eB : Fin 3 ≃ B := (Fintype.equivFinOfCardEq hBcard).symm
  let E : Fin 3 → Fin 3 → Bool :=
    fun i j ↦ decide (G.Adj (eA i) (eB j))
  have hcritical : MatrixDeletionCritical E := by
    apply relabeled_matrix_deletionCritical G S A B c hc hSbip hSsix hf
    · intro v
      simp [A]
    · intro v
      simp [B]
  have hprofile := matrix_profile_of_deletionCritical E hcritical
  exact ⟨A, B, eA, eB, rfl, rfl, hprofile⟩

end WrittenOnTheWallII.GraphConjecture59RelabeledCoreProfile
