import GraphConjecture183OddCyclePackage

/-!
# WOWII 183: the fixed adjacent-pair cycle complement is a path

For every cycle of order at least five, deleting vertices `0` and `1` leaves
the increasing interval `2, ..., n - 1`.  This module identifies that induced
graph explicitly with `pathGraph (n - 2)` and transports connectivity and a
two-coloring across the isomorphism.  The `C3` exception remains separate.
-/

namespace WrittenOnTheWallII.GraphConjecture183CycleComplementPath

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture183OddCyclePackage

/-- The vertices retained after deleting the package's fixed pair `{0,1}`. -/
def zeroOneComplement (n : ℕ) (h : 5 ≤ n) : Set (Fin n) :=
  ({cycleDeleteFirst h, cycleDeleteSecond h} : Set (Fin n))ᶜ

/-- Increasing enumeration `2, ..., n - 1` of the retained vertices. -/
def zeroOneComplementEquiv (n : ℕ) (h : 5 ≤ n) :
    Fin (n - 2) ≃ zeroOneComplement n h where
  toFun i := ⟨⟨i.val + 2, by omega⟩, by
    simp only [zeroOneComplement, Set.mem_compl_iff, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    push_neg
    constructor <;> intro heq <;> have hv := congrArg Fin.val heq <;>
      simp [cycleDeleteFirst, cycleDeleteSecond] at hv⟩
  invFun z := ⟨z.val.val - 2, by
    have hzlt := z.val.isLt
    omega⟩
  left_inv i := by
    apply Fin.ext
    simp
  right_inv z := by
    apply Subtype.ext
    apply Fin.ext
    have hz : 2 ≤ z.val.val := by
      have hp := z.property
      simp only [zeroOneComplement, Set.mem_compl_iff, Set.mem_insert_iff,
        Set.mem_singleton_iff] at hp
      push_neg at hp
      rcases hp with ⟨hz0, hz1⟩
      have hz0' : z.val.val ≠ 0 := fun hv => hz0 (Fin.ext hv)
      have hz1' : z.val.val ≠ 1 := fun hv => hz1 (Fin.ext hv)
      omega
    change (z.val.val - 2) + 2 = z.val.val
    omega

/-- Modular subtraction cannot wrap between two vertices in `2, ..., n-1`
and still have value one. -/
private lemma shifted_sub_val_eq_one_iff (n : ℕ) (h : 5 ≤ n)
    (u v : Fin (n - 2)) :
    ((⟨u.val + 2, by omega⟩ : Fin n) - ⟨v.val + 2, by omega⟩).val = 1 ↔
      v.val + 1 = u.val := by
  let U : Fin n := ⟨u.val + 2, by omega⟩
  let V : Fin n := ⟨v.val + 2, by omega⟩
  have hu := u.isLt
  have hv := v.isLt
  constructor
  · intro hsub
    have hint := Fin.intCast_val_sub_eq_sub_add_ite U V
    rw [hsub] at hint
    simp only [U, V] at hint
    by_cases hle : V ≤ U
    · have hleval : v.val + 2 ≤ u.val + 2 := hle
      rw [if_pos hle] at hint
      omega
    · have hnleval : ¬v.val + 2 ≤ u.val + 2 := by
        intro hval
        exact hle hval
      rw [if_neg hle] at hint
      omega
  · intro huv
    have hle : (⟨v.val + 2, by omega⟩ : Fin n) ≤
        ⟨u.val + 2, by omega⟩ := Fin.mk_le_mk.mpr (by omega)
    rw [Fin.sub_val_of_le hle]
    change (u.val + 2) - (v.val + 2) = 1
    omega

/-- Deleting adjacent vertices `0,1` from a sufficiently long cycle gives a
path on the remaining `n-2` vertices. -/
def zeroOneComplementPathIso (n : ℕ) (h : 5 ≤ n) :
    (pathGraph (n - 2)) ≃g (cycleGraph n).induce (zeroOneComplement n h) where
  toEquiv := zeroOneComplementEquiv n h
  map_rel_iff' := by
    intro u v
    rw [induce_adj, cycleGraph_adj', pathGraph_adj]
    change (((⟨u.val + 2, by omega⟩ : Fin n) -
        ⟨v.val + 2, by omega⟩).val = 1 ∨
      ((⟨v.val + 2, by omega⟩ : Fin n) -
        ⟨u.val + 2, by omega⟩).val = 1) ↔
      (u.val + 1 = v.val ∨ v.val + 1 = u.val)
    rw [shifted_sub_val_eq_one_iff n h u v,
      shifted_sub_val_eq_one_iff n h v u]
    tauto

/-- The fixed-pair complement is connected. -/
theorem zeroOneComplement_connected (n : ℕ) (h : 5 ≤ n) :
    ((cycleGraph n).induce (zeroOneComplement n h)).Connected := by
  apply (zeroOneComplementPathIso n h).connected_iff.mp
  have hn : n - 2 = (n - 3) + 1 := by omega
  rw [hn]
  exact pathGraph_connected (n - 3)

/-- The fixed-pair complement is bipartite. -/
theorem zeroOneComplement_isBipartite (n : ℕ) (h : 5 ≤ n) :
    ((cycleGraph n).induce (zeroOneComplement n h)).IsBipartite := by
  let e := zeroOneComplementPathIso n h
  obtain ⟨c⟩ := (pathGraph.bicoloring (n - 2)).colorable
  refine ⟨Coloring.mk (fun z => c (e.symm z)) ?_⟩
  intro z w hzw
  exact c.valid (e.symm.map_rel_iff.mpr hzw)

/-- The vertices retained after deleting the package's second fixed pair
`{2,3}`. -/
def twoThreeComplement (n : ℕ) (h : 5 ≤ n) : Set (Fin n) :=
  ({cycleDeleteThird h, cycleDeleteFourth h} : Set (Fin n))ᶜ

private lemma first_add_third (n : ℕ) (h : 5 ≤ n) :
    cycleDeleteFirst h + cycleDeleteThird h = cycleDeleteThird h := by
  apply Fin.ext
  simp [cycleDeleteFirst, cycleDeleteThird, Fin.val_add,
    Nat.mod_eq_of_lt (by omega : 2 < n)]

private lemma second_add_third (n : ℕ) (h : 5 ≤ n) :
    cycleDeleteSecond h + cycleDeleteThird h = cycleDeleteFourth h := by
  apply Fin.ext
  simp [cycleDeleteSecond, cycleDeleteThird, cycleDeleteFourth, Fin.val_add,
    Nat.mod_eq_of_lt (by omega : 3 < n)]

/-- Translation by two restricts to an equivalence between the two retained
vertex sets. -/
def zeroOneToTwoThreeEquiv (n : ℕ) (h : 5 ≤ n) :
    zeroOneComplement n h ≃ twoThreeComplement n h := by
  letI : NeZero n := ⟨by omega⟩
  exact (Equiv.addRight (cycleDeleteThird h)).subtypeEquiv fun x => by
    simp only [zeroOneComplement, twoThreeComplement, Set.mem_compl_iff,
      Set.mem_insert_iff, Set.mem_singleton_iff]
    push_neg
    constructor
    · rintro ⟨hx0, hx1⟩
      constructor
      · intro hx
        apply hx0
        apply add_right_cancel (b := cycleDeleteThird h)
        simpa [first_add_third n h] using hx
      · intro hx
        apply hx1
        apply add_right_cancel (b := cycleDeleteThird h)
        simpa [second_add_third n h] using hx
    · rintro ⟨hx2, hx3⟩
      constructor
      · intro hx
        apply hx2
        rw [hx]
        change cycleDeleteFirst h + cycleDeleteThird h = cycleDeleteThird h
        exact first_add_third n h
      · intro hx
        apply hx3
        rw [hx]
        change cycleDeleteSecond h + cycleDeleteThird h = cycleDeleteFourth h
        exact second_add_third n h

@[simp] lemma zeroOneToTwoThreeEquiv_apply (n : ℕ) (h : 5 ≤ n)
    (x : zeroOneComplement n h) :
    (zeroOneToTwoThreeEquiv n h x).val = x.val + cycleDeleteThird h := by
  letI : NeZero n := ⟨by omega⟩
  rfl

/-- Translation by two is a graph isomorphism between the two induced
complements. -/
def zeroOneToTwoThreeIso (n : ℕ) (h : 5 ≤ n) :
    (cycleGraph n).induce (zeroOneComplement n h) ≃g
      (cycleGraph n).induce (twoThreeComplement n h) where
  toEquiv := zeroOneToTwoThreeEquiv n h
  map_rel_iff' := by
    intro u v
    rw [induce_adj, induce_adj, cycleGraph_adj', cycleGraph_adj']
    rw [zeroOneToTwoThreeEquiv_apply, zeroOneToTwoThreeEquiv_apply]
    letI : NeZero n := ⟨by omega⟩
    simp

/-- The translated fixed-pair complement is connected. -/
theorem twoThreeComplement_connected (n : ℕ) (h : 5 ≤ n) :
    ((cycleGraph n).induce (twoThreeComplement n h)).Connected := by
  exact (zeroOneToTwoThreeIso n h).connected_iff.mp
    (zeroOneComplement_connected n h)

/-- The translated fixed-pair complement is bipartite. -/
theorem twoThreeComplement_isBipartite (n : ℕ) (h : 5 ≤ n) :
    ((cycleGraph n).induce (twoThreeComplement n h)).IsBipartite := by
  let e := zeroOneToTwoThreeIso n h
  obtain ⟨c⟩ := zeroOneComplement_isBipartite n h
  refine ⟨Coloring.mk (fun z => c (e.symm z)) ?_⟩
  intro z w hzw
  exact c.valid (e.symm.map_rel_iff.mpr hzw)

/-- The root-sensitive pair chosen by the package always leaves a connected
bipartite path. -/
theorem cyclePairComplementPathProperty : CyclePairComplementPathProperty := by
  intro n h r
  by_cases hr : r = cycleDeleteFirst h ∨ r = cycleDeleteSecond h
  · have hp : rootSensitiveCyclePair h r =
        (cycleDeleteThird h, cycleDeleteFourth h) := by
      simp [rootSensitiveCyclePair, hr]
    rw [hp]
    simpa [twoThreeComplement] using
      And.intro (twoThreeComplement_connected n h)
        (twoThreeComplement_isBipartite n h)
  · have hp : rootSensitiveCyclePair h r =
        (cycleDeleteFirst h, cycleDeleteSecond h) := by
      simp [rootSensitiveCyclePair, hr]
    rw [hp]
    simpa [zeroOneComplement] using
      And.intro (zeroOneComplement_connected n h)
        (zeroOneComplement_isBipartite n h)

end WrittenOnTheWallII.GraphConjecture183CycleComplementPath
