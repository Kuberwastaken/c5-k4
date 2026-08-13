import GraphConjecture59RelabeledCoreProfile
import GraphConjecture59FullFanPropagation

/-!
# WOWII 59: deletion-critical core and full-fan cover synthesis

The relabeled six-core is `K3,3` or `K3,3-e`.  A v29 full-fan frame forces
the third same-side core vertex to hit two or three named frame vertices.
This file gives the exact joint case table, including the location of the
unique possible missing core edge.
-/

namespace WrittenOnTheWallII.GraphConjecture59CoreCoverSynthesis

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CoreProfileMultiplicity
open WrittenOnTheWallII.GraphConjecture59RelabeledCoreProfile
open WrittenOnTheWallII.GraphConjecture59FullFanPropagation

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Number of named frame vertices met by the third core vertex. -/
def thirdCoreFrameCount (G : SimpleGraph V) [DecidableRel G.Adj]
    (d w p q : V) : ℕ :=
  (({q, p, w} : Finset V).filter fun x ↦ G.Adj d x).card

omit [Fintype V] in
/-- The full-fan cover really is the cardinal statement "at least two of the
three frame vertices", once the frame vertices are distinct. -/
theorem two_le_thirdCoreFrameCount_of_cover
    (G : SimpleGraph V) [DecidableRel G.Adj] (d w p q : V)
    (hwp : w ≠ p) (hwq : w ≠ q) (hpq : p ≠ q)
    (hcover : ThirdCoreCover G d w p q) :
    2 ≤ thirdCoreFrameCount G d w p q := by
  have memOf {x : V} (hx : x = q ∨ x = p ∨ x = w)
      (hadj : G.Adj d x) :
      x ∈ ({q, p, w} : Finset V).filter fun y ↦ G.Adj d y := by
    simp only [mem_filter, mem_insert, mem_singleton]
    exact ⟨hx, hadj⟩
  rcases hcover with h | h | h
  · apply one_lt_card.mpr
    exact ⟨q, memOf (Or.inl rfl) h.1,
      p, memOf (Or.inr (Or.inl rfl)) h.2, hpq.symm⟩
  · apply one_lt_card.mpr
    exact ⟨q, memOf (Or.inl rfl) h.1,
      w, memOf (Or.inr (Or.inr rfl)) h.2, hwq.symm⟩
  · apply one_lt_card.mpr
    exact ⟨p, memOf (Or.inr (Or.inl rfl)) h.1,
      w, memOf (Or.inr (Or.inr rfl)) h.2, hwp.symm⟩

omit [Fintype V] in
/-- A frame has only three named vertices, so the cover count is at most
three without any graph-theoretic assumptions. -/
theorem thirdCoreFrameCount_le_three
    (G : SimpleGraph V) [DecidableRel G.Adj] (d w p q : V) :
    thirdCoreFrameCount G d w p q ≤ 3 := by
  unfold thirdCoreFrameCount
  calc
    (({q, p, w} : Finset V).filter fun x ↦ G.Adj d x).card ≤
        ({q, p, w} : Finset V).card := card_filter_le _ _
    _ ≤ ({p, w} : Finset V).card + 1 := card_insert_le q {p, w}
    _ ≤ ({w} : Finset V).card + 2 := by
      have := card_insert_le p {w}
      omega
    _ ≤ 3 := by simp

/-- Every one of the nine cross-edges is present. -/
def CompleteCoreMatrix (E : Fin 3 → Fin 3 → Bool) : Prop :=
  ∀ i j, E i j = true

instance (E : Fin 3 → Fin 3 → Bool) : Decidable (CompleteCoreMatrix E) := by
  unfold CompleteCoreMatrix
  infer_instance

/-- Exactly one cross-edge is absent, and its left endpoint is row `i`. -/
def OneMissingCoreEdgeAtRow (E : Fin 3 → Fin 3 → Bool)
    (i : Fin 3) : Prop :=
  ∃ j, E i j = false ∧
    ∀ r s, E r s = false → r = i ∧ s = j

instance (E : Fin 3 → Fin 3 → Bool) (i : Fin 3) :
    Decidable (OneMissingCoreEdgeAtRow E i) := by
  unfold OneMissingCoreEdgeAtRow
  infer_instance

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
/-- Finite exact matrix shape at edge counts eight and nine.  In the
one-edge-deleted case it additionally locates the missing edge among three
named, pairwise-distinct rows. -/
theorem exact_matrix_shape : ∀ (E : Fin 3 → Fin 3 → Bool) (a b d : Fin 3),
    a ≠ b → a ≠ d → b ≠ d →
    (matrixEdgeCount E = 9 → CompleteCoreMatrix E) ∧
    (matrixEdgeCount E = 8 →
      ((matrixRowDegree E d = 2 ∧ OneMissingCoreEdgeAtRow E d) ∨
       (matrixRowDegree E d = 3 ∧
        (OneMissingCoreEdgeAtRow E a ∨ OneMissingCoreEdgeAtRow E b)))) := by
  decide

/-- Exact remaining coordinate cases.  The marked vertices `a,b,d` are the
three distinct rows of the core matrix.  The first two acquire four known
full-fan/outside incidences; the third acquires `t=2` or `t=3` incidences.

The displayed additions are marked-incidence bookkeeping.  They are not
identified with `SimpleGraph.degree` in this definition; that later step must
also certify that the named outside vertices are distinct from the core.

The table distinguishes whether the unique possible missing core edge is in
the third row or in one of the two aligned rows. -/
def ExactCoreCoverProfile (E : Fin 3 → Fin 3 → Bool)
    (a b d : Fin 3) (t : ℕ) : Prop :=
  (matrixEdgeCount E = 9 ∧
    CompleteCoreMatrix E ∧
    matrixRowDegree E a + 4 = 7 ∧
    matrixRowDegree E b + 4 = 7 ∧
    (matrixRowDegree E d + t = 5 ∨ matrixRowDegree E d + t = 6)) ∨
  (matrixEdgeCount E = 8 ∧
    ((matrixRowDegree E d = 2 ∧
      OneMissingCoreEdgeAtRow E d ∧
      matrixRowDegree E a + 4 = 7 ∧
      matrixRowDegree E b + 4 = 7 ∧
      (matrixRowDegree E d + t = 4 ∨ matrixRowDegree E d + t = 5)) ∨
    (matrixRowDegree E d = 3 ∧
      (OneMissingCoreEdgeAtRow E a ∨ OneMissingCoreEdgeAtRow E b) ∧
      ((matrixRowDegree E a + 4 = 6 ∧ matrixRowDegree E b + 4 = 7) ∨
       (matrixRowDegree E a + 4 = 7 ∧ matrixRowDegree E b + 4 = 6)) ∧
      (matrixRowDegree E d + t = 5 ∨ matrixRowDegree E d + t = 6))))

instance (E : Fin 3 → Fin 3 → Bool) (a b d : Fin 3) (t : ℕ) :
    Decidable (ExactCoreCoverProfile E a b d t) := by
  unfold ExactCoreCoverProfile
  infer_instance

lemma rowDegree_le_three (E : Fin 3 → Fin 3 → Bool) (i : Fin 3) :
    matrixRowDegree E i ≤ 3 := by
  unfold matrixRowDegree
  simpa using card_filter_le (univ : Finset (Fin 3)) (fun j ↦ E i j)

lemma two_le_rowDegree_of_deletionCritical
    (E : Fin 3 → Fin 3 → Bool) (h : MatrixDeletionCritical E)
    (i : Fin 3) : 2 ≤ matrixRowDegree E i := by
  fin_cases i
  · have hc := h.1 2
    have hsub :
        (univ.filter fun j ↦ E (nextIndex 2) j && E (previousIndex 2) j) ⊆
          univ.filter fun j ↦ E 0 j := by
      intro j hj
      simp only [mem_filter, mem_univ, true_and, Bool.and_eq_true] at hj ⊢
      simpa [nextIndex, previousIndex] using hj.1
    exact hc.trans (card_le_card hsub)
  · have hc := h.1 0
    have hsub :
        (univ.filter fun j ↦ E (nextIndex 0) j && E (previousIndex 0) j) ⊆
          univ.filter fun j ↦ E 1 j := by
      intro j hj
      simp only [mem_filter, mem_univ, true_and, Bool.and_eq_true] at hj ⊢
      simpa [nextIndex, previousIndex] using hj.1
    exact hc.trans (card_le_card hsub)
  · have hc := h.1 1
    have hsub :
        (univ.filter fun j ↦ E (nextIndex 1) j && E (previousIndex 1) j) ⊆
          univ.filter fun j ↦ E 2 j := by
      intro j hj
      simp only [mem_filter, mem_univ, true_and, Bool.and_eq_true] at hj ⊢
      simpa [nextIndex, previousIndex] using hj.1
    exact hc.trans (card_le_card hsub)

lemma matrixEdgeCount_eq_three_rows (E : Fin 3 → Fin 3 → Bool) :
    matrixEdgeCount E = matrixRowDegree E 0 + matrixRowDegree E 1 +
      matrixRowDegree E 2 := by
  simp [matrixEdgeCount, Fin.sum_univ_succ, Nat.add_assoc]

/-- **Core/cover synthesis.** Deletion criticality and one v29 cover leave
exactly the coordinate cases listed by `ExactCoreCoverProfile`. -/
theorem exactCoreCoverProfile_of_deletionCritical
    (E : Fin 3 → Fin 3 → Bool) (a b d : Fin 3) (t : ℕ)
    (hcrit : MatrixDeletionCritical E)
    (hab : a ≠ b) (had : a ≠ d) (hbd : b ≠ d)
    (htwo : 2 ≤ t) (hthree : t ≤ 3) :
    ExactCoreCoverProfile E a b d t := by
  have hprofile := matrix_profile_of_deletionCritical E hcrit
  have haLower := two_le_rowDegree_of_deletionCritical E hcrit a
  have hbLower := two_le_rowDegree_of_deletionCritical E hcrit b
  have hdLower := two_le_rowDegree_of_deletionCritical E hcrit d
  have haUpper := rowDegree_le_three E a
  have hbUpper := rowDegree_le_three E b
  have hdUpper := rowDegree_le_three E d
  have hsum : matrixEdgeCount E = matrixRowDegree E a +
      matrixRowDegree E b + matrixRowDegree E d := by
    have hrows := matrixEdgeCount_eq_three_rows E
    fin_cases a <;> fin_cases b <;> fin_cases d <;>
      simp_all <;> omega
  have hshape := exact_matrix_shape E a b d hab had hbd
  unfold ExactCoreCoverProfile
  rcases hprofile with hfull | honeMissing
  · right
    rcases hfull with ⟨hedges, -⟩
    refine ⟨hedges, ?_⟩
    by_cases hdTwo : matrixRowDegree E d = 2
    · left
      have hmissing : OneMissingCoreEdgeAtRow E d := by
        rcases hshape.2 hedges with h | h
        · exact h.2
        · omega
      refine ⟨hdTwo, hmissing, ?_, ?_, ?_⟩ <;> omega
    · right
      have hdThree : matrixRowDegree E d = 3 := by omega
      have hmissing : OneMissingCoreEdgeAtRow E a ∨
          OneMissingCoreEdgeAtRow E b := by
        rcases hshape.2 hedges with h | h
        · omega
        · exact h.2
      refine ⟨hdThree, hmissing, ?_, ?_⟩
      · omega
      · omega
  · left
    rcases honeMissing with ⟨hedges, -⟩
    exact ⟨hedges, hshape.1 hedges, by omega, by omega, by omega⟩

/-- A complete core and representatives of both one-edge-deleted branches
show that the synthesis table itself is consistent.  Hence no five-forest or
residue contradiction follows from deletion criticality plus one cover alone.
-/
theorem representative_synthesis_cases_are_realizable :
    let complete : Fin 3 → Fin 3 → Bool := fun _ _ ↦ true
    let missingAtThird : Fin 3 → Fin 3 → Bool :=
      fun i j ↦ !(i == 2 && j == 0)
    let missingAtAligned : Fin 3 → Fin 3 → Bool :=
      fun i j ↦ !(i == 0 && j == 0)
    (MatrixDeletionCritical complete ∧
      ExactCoreCoverProfile complete 0 1 2 2) ∧
    (MatrixDeletionCritical missingAtThird ∧
      ExactCoreCoverProfile missingAtThird 0 1 2 2) ∧
    (MatrixDeletionCritical missingAtAligned ∧
      ExactCoreCoverProfile missingAtAligned 0 1 2 2) := by
  decide

/-- End-to-end graph form.  The core relabeling is constructed, the actual
v29 frame cover is converted to `t=2` or `3`, and the exact joint coordinate
profile is returned with the marked core rows. -/
theorem exists_relabeling_with_exact_core_cover_profile
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (c : V → Fin 2) (a b d w p q : V)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6) (hf : G.largestInducedForestSize = 4)
    (hclass : ∀ k : Fin 2, (S.filter fun v ↦ c v = k).card = 3)
    (ha : a ∈ S ∧ c a = 0) (hb : b ∈ S ∧ c b = 0)
    (hd : d ∈ S ∧ c d = 0)
    (hab : a ≠ b) (had : a ≠ d) (hbd : b ≠ d)
    (hwp : w ≠ p) (hwq : w ≠ q) (hpq : p ≠ q)
    (hcover : ThirdCoreCover G d w p q) :
    ∃ (A B : Finset V) (eA : Fin 3 ≃ A) (eB : Fin 3 ≃ B)
        (ia ib id : Fin 3),
      A = S.filter (fun v ↦ c v = 0) ∧
      B = S.filter (fun v ↦ c v = 1) ∧
      ((eA ia : A) : V) = a ∧ ((eA ib : A) : V) = b ∧
      ((eA id : A) : V) = d ∧
      ia ≠ ib ∧ ia ≠ id ∧ ib ≠ id ∧
      let E : Fin 3 → Fin 3 → Bool :=
        fun i j ↦ decide (G.Adj (eA i) (eB j))
      ExactCoreCoverProfile E ia ib id (thirdCoreFrameCount G d w p q) := by
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
  have haA : a ∈ A := by simpa [A] using ha
  have hbA : b ∈ A := by simpa [A] using hb
  have hdA : d ∈ A := by simpa [A] using hd
  let ia := eA.symm ⟨a, haA⟩
  let ib := eA.symm ⟨b, hbA⟩
  let id := eA.symm ⟨d, hdA⟩
  have hiab : ia ≠ ib := by
    intro h
    apply hab
    have := congrArg (fun i ↦ ((eA i : A) : V)) h
    simpa [ia, ib] using this
  have hiad : ia ≠ id := by
    intro h
    apply had
    have := congrArg (fun i ↦ ((eA i : A) : V)) h
    simpa [ia, id] using this
  have hibd : ib ≠ id := by
    intro h
    apply hbd
    have := congrArg (fun i ↦ ((eA i : A) : V)) h
    simpa [ib, id] using this
  let E : Fin 3 → Fin 3 → Bool :=
    fun i j ↦ decide (G.Adj (eA i) (eB j))
  have hcrit : MatrixDeletionCritical E := by
    apply relabeled_matrix_deletionCritical G S A B c hc hSbip hSsix hf
    · intro v
      simp [A]
    · intro v
      simp [B]
  have htwo : 2 ≤ thirdCoreFrameCount G d w p q :=
    two_le_thirdCoreFrameCount_of_cover G d w p q hwp hwq hpq hcover
  have hthree : thirdCoreFrameCount G d w p q ≤ 3 :=
    thirdCoreFrameCount_le_three G d w p q
  have hexact := exactCoreCoverProfile_of_deletionCritical
    E ia ib id (thirdCoreFrameCount G d w p q) hcrit hiab hiad hibd htwo hthree
  refine ⟨A, B, eA, eB, ia, ib, id, rfl, rfl, ?_, ?_, ?_,
    hiab, hiad, hibd, hexact⟩
  · simp [ia]
  · simp [ib]
  · simp [id]

end WrittenOnTheWallII.GraphConjecture59CoreCoverSynthesis
