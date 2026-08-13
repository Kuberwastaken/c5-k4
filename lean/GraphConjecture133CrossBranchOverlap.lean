import FormalConjecturesUtil

/-!
# WOWII 133: one clean parent per branch

Three cross-branch parents each expose a triple of third choices.  C4-freeness
only bounds every pairwise intersection by one.  The sharp resulting union
lower bound is six, not nine.  Since four internal targets have eight outside
slots, this no longer forces an unblocked third.

An explicit six-vertex incidence and blocker-color model attains the bound
while satisfying pairwise overlap, per-parent target distinctness, and target
capacity two.  It isolates the residual-degree/metric condition still absent
from local counting.
-/

namespace WrittenOnTheWallII.GraphConjecture133CrossBranchOverlap

variable {V : Type*} [DecidableEq V]

/-- Three triples with pairwise intersections at most one have union at least
six. -/
theorem six_le_card_union_three
    (A B C : Finset V)
    (hA : A.card = 3) (hB : B.card = 3) (hC : C.card = 3)
    (hAB : (A ∩ B).card ≤ 1)
    (hAC : (A ∩ C).card ≤ 1)
    (hBC : (B ∩ C).card ≤ 1) :
    6 ≤ ((A ∪ B) ∪ C).card := by
  have hABeq := Finset.card_union_add_card_inter A B
  have hABunion : 5 ≤ (A ∪ B).card := by omega
  have hsub : (A ∪ B) ∩ C ⊆ (A ∩ C) ∪ (B ∩ C) := by
    intro z hz
    simp only [Finset.mem_inter, Finset.mem_union] at hz ⊢
    rcases hz.1 with hzA | hzB
    · exact Or.inl ⟨hzA, hz.2⟩
    · exact Or.inr ⟨hzB, hz.2⟩
  have hinterUnion := Finset.card_le_card hsub
  have hunionInter := Finset.card_union_le (A ∩ C) (B ∩ C)
  have hinter : ((A ∪ B) ∩ C).card ≤ 2 := by omega
  have hfinal := Finset.card_union_add_card_inter (A ∪ B) C
  omega

/-- The blocker capacity eight is compatible with the sharp lower bound six;
pure cardinal arithmetic has a two-slot gap. -/
theorem six_fits_internal_capacity : (6 : ℕ) ≤ 8 := by omega

/-- Equality classification for the sharp lower bound.  A six-point union
forces three distinct pairwise overlaps and no triple overlap. -/
theorem union_six_forces_triangle_overlap
    (A B C : Finset V)
    (hA : A.card = 3) (hB : B.card = 3) (hC : C.card = 3)
    (hAB : (A ∩ B).card ≤ 1)
    (hAC : (A ∩ C).card ≤ 1)
    (hBC : (B ∩ C).card ≤ 1)
    (hU : ((A ∪ B) ∪ C).card = 6) :
    (A ∩ B).card = 1 ∧ (A ∩ C).card = 1 ∧
      (B ∩ C).card = 1 ∧ ((A ∩ B) ∩ C).card = 0 := by
  have hABeq := Finset.card_union_add_card_inter A B
  have hfinal := Finset.card_union_add_card_inter (A ∪ B) C
  have hsub : (A ∪ B) ∩ C ⊆ (A ∩ C) ∪ (B ∩ C) := by
    intro z hz
    simp only [Finset.mem_inter, Finset.mem_union] at hz ⊢
    rcases hz.1 with hzA | hzB
    · exact Or.inl ⟨hzA, hz.2⟩
    · exact Or.inr ⟨hzB, hz.2⟩
  have hcardSub := Finset.card_le_card hsub
  have hpairUnion := Finset.card_union_le (A ∩ C) (B ∩ C)
  have hx : (A ∩ B).card = 1 := by omega
  have hy : (A ∩ C).card = 1 := by omega
  have hz : (B ∩ C).card = 1 := by omega
  have hD : ((A ∪ B) ∩ C).card = 2 := by omega
  have hpairEq : (A ∩ C) ∪ (B ∩ C) = (A ∪ B) ∩ C := by
    ext z
    simp only [Finset.mem_union, Finset.mem_inter]
    aesop
  have hinterEq := Finset.card_union_add_card_inter (A ∩ C) (B ∩ C)
  have hinterZero : ((A ∩ C) ∩ (B ∩ C)).card = 0 := by
    rw [hpairEq, hD, hy, hz] at hinterEq
    omega
  have htripleEq : (A ∩ C) ∩ (B ∩ C) = (A ∩ B) ∩ C := by
    ext z
    simp only [Finset.mem_inter]
    aesop
  exact ⟨hx, hy, hz, by simpa [htripleEq] using hinterZero⟩

/- ## Sharp finite survivor -/

abbrev Branch := Fin 3
abbrev ThirdVertex := Fin 6
abbrev InternalTarget := Fin 4

/-- Pairwise shared points are `0,1,2`; private points are `3,4,5`. -/
def thirds : Branch → Finset ThirdVertex
  | 0 => {0, 1, 3}
  | 1 => {0, 2, 4}
  | _ => {1, 2, 5}

def allThirds : Finset ThirdVertex :=
  (thirds 0 ∪ thirds 1) ∪ thirds 2

/-- A capacity-two blocker coloring.  Each parent's three thirds receive
three distinct target colors. -/
def blockerTarget : ThirdVertex → InternalTarget :=
  ![0, 1, 2, 2, 1, 0]

def targetFiber (k : InternalTarget) : Finset ThirdVertex :=
  Finset.univ.filter fun z ↦ blockerTarget z = k

theorem three_thirds_per_parent (b : Branch) :
    (thirds b).card = 3 := by
  fin_cases b <;> decide

theorem cross_parent_intersection_eq_one
    (b₁ b₂ : Branch) (h : b₁ ≠ b₂) :
    ((thirds b₁) ∩ (thirds b₂)).card = 1 := by
  revert h
  fin_cases b₁ <;> fin_cases b₂ <;> decide

theorem triple_intersection_empty :
    ((thirds 0 ∩ thirds 1) ∩ thirds 2).card = 0 := by
  decide

theorem sharp_union_card_six : allThirds.card = 6 := by
  decide

theorem every_vertex_is_owned : allThirds = Finset.univ := by
  decide

theorem target_capacity_two (k : InternalTarget) :
    (targetFiber k).card ≤ 2 := by
  fin_cases k <;> decide

/-- Two distinct thirds below one parent never use the same target.  This is
the abstract form of the parent--third--target C4 restriction. -/
theorem blocker_injective_on_parent
    (b : Branch) {z w : ThirdVertex}
    (hz : z ∈ thirds b) (hw : w ∈ thirds b)
    (hzw : z ≠ w) : blockerTarget z ≠ blockerTarget w := by
  revert hz hw hzw
  fin_cases b <;> fin_cases z <;> fin_cases w <;> decide

/-- Every third is assigned an internal blocker. -/
theorem every_third_has_internal_blocker
    (z : ThirdVertex) : z ∈ targetFiber (blockerTarget z) := by
  simp [targetFiber]

/-- The exact cross-branch survivor: all three triples, pairwise overlap one,
empty triple overlap, union six, target capacity two, and per-parent target
injectivity coexist. -/
theorem cross_branch_capacity_survivor :
    (∀ b : Branch, (thirds b).card = 3) ∧
    (∀ b₁ b₂ : Branch, b₁ ≠ b₂ →
      ((thirds b₁) ∩ (thirds b₂)).card ≤ 1) ∧
    ((thirds 0 ∩ thirds 1) ∩ thirds 2).card = 0 ∧
    allThirds.card = 6 ∧
    (∀ k : InternalTarget, (targetFiber k).card ≤ 2) ∧
    (∀ b : Branch, ∀ z ∈ thirds b, ∀ w ∈ thirds b,
      z ≠ w → blockerTarget z ≠ blockerTarget w) ∧
    (∀ z : ThirdVertex, z ∈ targetFiber (blockerTarget z)) := by
  refine ⟨three_thirds_per_parent, ?_, triple_intersection_empty,
    sharp_union_card_six, target_capacity_two, ?_,
    every_third_has_internal_blocker⟩
  · intro b₁ b₂ h
    rw [cross_parent_intersection_eq_one b₁ b₂ h]
  · intro b z hz w hw hzw
    exact blocker_injective_on_parent b hz hw hzw

/-- Degree bookkeeping for the sharp survivor.  The three pair-shared thirds
use two parent edges and one blocker edge, leaving one degree slot; the three
private thirds use one parent edge and one blocker edge, leaving two slots. -/
theorem residual_degree_signature :
    (∀ _z : Fin 3, 2 + 1 + 1 = 4) ∧
    (∀ _z : Fin 3, 1 + 1 + 2 = 4) := by
  constructor <;> intro _z <;> omega

end WrittenOnTheWallII.GraphConjecture133CrossBranchOverlap
