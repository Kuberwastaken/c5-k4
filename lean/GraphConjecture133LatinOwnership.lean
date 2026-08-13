import FormalConjecturesUtil

/-!
# WOWII 133: Latin ownership survivor

The repeated-slot ownership profile is incompatible with the C4-free
cross-parent bound.  This file tests the natural replacement: the three
parallel classes of a 3-by-3 Latin square.  Distinct colored parents then
share at most one third vertex, while every parent still owns three thirds.

An explicit blocker assignment also respects the `3,2,2,2,2` target
capacities and introduces no parent shared by two thirds at one target.  The
result is an exact finite incidence model for all currently extracted local
constraints.  It is not asserted to be a completion to the original metric
graph configuration.
-/

namespace WrittenOnTheWallII.GraphConjecture133LatinOwnership

abbrev Branch := Fin 3
abbrev ParentSlot := Fin 3
abbrev ThirdVertex := Fin 9
abbrev Target := Fin 5
abbrev ColoredParent := Branch × ParentSlot

/-- The three ownership directions are row, column, and Latin diagonal. -/
def ownerSlot (b : Branch) (z : ThirdVertex) : ParentSlot :=
  if b.val = 0 then
    ⟨(z.val / 3) % 3, Nat.mod_lt _ (by omega)⟩
  else if b.val = 1 then
    ⟨z.val % 3, Nat.mod_lt _ (by omega)⟩
  else
    ⟨((z.val / 3) + (z.val % 3)) % 3, Nat.mod_lt _ (by omega)⟩

def parentOwns (q : ColoredParent) (z : ThirdVertex) : Prop :=
  ownerSlot q.1 z = q.2

instance instDecidableParentOwns (q : ColoredParent) (z : ThirdVertex) :
    Decidable (parentOwns q z) := by
  unfold parentOwns
  infer_instance

def parentThirds (q : ColoredParent) : Finset ThirdVertex :=
  Finset.univ.filter fun z ↦ parentOwns q z

def thirdOwners (z : ThirdVertex) : Finset ColoredParent :=
  Finset.univ.filter fun q ↦ parentOwns q z

/-- Every colored parent owns exactly three third vertices. -/
theorem three_thirds_per_parent (q : ColoredParent) :
    (parentThirds q).card = 3 := by
  rcases q with ⟨b, p⟩
  fin_cases b <;> fin_cases p <;> decide

/-- Every third has one owner in each of the three branches. -/
theorem three_owners_per_third (z : ThirdVertex) :
    (thirdOwners z).card = 3 := by
  fin_cases z <;> decide

/-- Ownership is functional inside each branch. -/
theorem unique_owner_in_branch (b : Branch) (z : ThirdVertex) :
    ∃! p : ParentSlot, parentOwns (b, p) z := by
  refine ⟨ownerSlot b z, rfl, ?_⟩
  intro p hp
  exact hp.symm

/-- Two distinct colored parents have at most one common third.  Same-branch
parents have none; cross-branch parents meet in exactly one in this profile. -/
theorem distinct_parents_common_thirds_le_one
    (q₁ q₂ : ColoredParent) (h : q₁ ≠ q₂) :
    ((parentThirds q₁) ∩ (parentThirds q₂)).card ≤ 1 := by
  revert h
  rcases q₁ with ⟨b₁, p₁⟩
  rcases q₂ with ⟨b₂, p₂⟩
  fin_cases b₁ <;> fin_cases p₁ <;>
    fin_cases b₂ <;> fin_cases p₂ <;> decide

/-- The stronger cross-branch equality: every pair of parents from different
parallel classes meets in exactly one third. -/
theorem cross_branch_common_thirds_eq_one
    (b₁ b₂ : Branch) (p₁ p₂ : ParentSlot) (h : b₁ ≠ b₂) :
    ((parentThirds (b₁, p₁)) ∩ (parentThirds (b₂, p₂))).card = 1 := by
  revert h
  fin_cases b₁ <;> fin_cases b₂ <;>
    fin_cases p₁ <;> fin_cases p₂ <;> decide

/-- The blocker classes are pieces of the unused fourth parallel class.
The loads are `3,2,1,2,1`. -/
def blockerTarget : ThirdVertex → Target :=
  ![0, 3, 1, 1, 0, 3, 4, 2, 0]

def targetCapacity (x : Target) : ℕ :=
  if x.val = 0 then 3 else 2

def blockedThirds (x : Target) : Finset ThirdVertex :=
  Finset.univ.filter fun z ↦ blockerTarget z = x

/-- All five blocker loads fit the geodesic target capacities. -/
theorem blocker_capacity_respected (x : Target) :
    (blockedThirds x).card ≤ targetCapacity x := by
  fin_cases x <;> decide

/-- The exact target loads expose the two unused capacity slots. -/
theorem blocker_load_vector :
    (blockedThirds 0).card = 3 ∧
    (blockedThirds 1).card = 2 ∧
    (blockedThirds 2).card = 1 ∧
    (blockedThirds 3).card = 2 ∧
    (blockedThirds 4).card = 1 := by
  decide

theorem all_nine_thirds_are_blocked_once :
    ∑ x : Target, (blockedThirds x).card = 9 := by
  decide

/-- Two distinct thirds assigned to one blocker target have no common colored
parent.  Hence the parent--third--target part creates no four-cycle. -/
theorem coblocked_thirds_have_no_common_parent
    (z w : ThirdVertex) (hzw : z ≠ w)
    (ht : blockerTarget z = blockerTarget w) :
    ((thirdOwners z) ∩ (thirdOwners w)).card = 0 := by
  revert hzw ht
  fin_cases z <;> fin_cases w <;> decide

/-- Parents make one first-layer contact plus three third-layer contacts. -/
theorem parent_local_degree_saturated (q : ColoredParent) :
    1 + (parentThirds q).card = 4 := by
  rw [three_thirds_per_parent]

/-- Thirds make three parent contacts plus their unique blocker contact. -/
theorem third_local_degree_saturated (z : ThirdVertex) :
    (thirdOwners z).card + 1 = 4 := by
  rw [three_owners_per_third]

/-- Saturation is compatible with the required owning-parent/blocker-target
non-incidence: the abstract model has no parent--target contacts. -/
def parentContactsTarget (_q : ColoredParent) (_x : Target) : Prop := False

theorem blocker_forbids_every_owning_parent
    (z : ThirdVertex) (q : ColoredParent) (_howns : parentOwns q z) :
    ¬parentContactsTarget q (blockerTarget z) := by
  simp [parentContactsTarget]

/-- Exact surviving abstract model.  It simultaneously satisfies ownership,
the C4-derived cross-parent bound, blocker capacities, collision-free blocker
classes, both local degree-four saturation counts, and parent--target
non-incidence. -/
theorem latin_ownership_survives_all_local_constraints :
    (∀ q : ColoredParent, (parentThirds q).card = 3) ∧
    (∀ z : ThirdVertex, (thirdOwners z).card = 3) ∧
    (∀ q₁ q₂ : ColoredParent, q₁ ≠ q₂ →
      ((parentThirds q₁) ∩ (parentThirds q₂)).card ≤ 1) ∧
    (∀ x : Target, (blockedThirds x).card ≤ targetCapacity x) ∧
    (∀ z w : ThirdVertex, z ≠ w → blockerTarget z = blockerTarget w →
      ((thirdOwners z) ∩ (thirdOwners w)).card = 0) ∧
    (∀ q : ColoredParent, 1 + (parentThirds q).card = 4) ∧
    (∀ z : ThirdVertex, (thirdOwners z).card + 1 = 4) ∧
    (∀ z : ThirdVertex, ∀ q : ColoredParent, parentOwns q z →
      ¬parentContactsTarget q (blockerTarget z)) := by
  exact ⟨three_thirds_per_parent, three_owners_per_third,
    distinct_parents_common_thirds_le_one, blocker_capacity_respected,
    coblocked_thirds_have_no_common_parent, parent_local_degree_saturated,
    third_local_degree_saturated, blocker_forbids_every_owning_parent⟩

end WrittenOnTheWallII.GraphConjecture133LatinOwnership
