import FormalConjecturesUtil

/-!
# WOWII 133: colored branch ownership counterprofile

This is the smallest colored incidence model for the fully collapsed aggregate
profile.  Nine third vertices each have one parent in each of three branches,
each of the nine parents owns three incidences, blocker targets respect the
`3,2,2,2,2` capacity vector, and the parent--target contact relation is empty.

The model is deliberately an incidence structure, not a simple graph.
-/

namespace WrittenOnTheWallII.GraphConjecture133ColoredOwnership

abbrev Branch := Fin 3
abbrev ParentSlot := Fin 3
abbrev ThirdVertex := Fin 9
abbrev Target := Fin 5

/-- Parent slot `z mod 3` owns third vertex `z` in every branch. -/
def parentOwns (_b : Branch) (p : ParentSlot) (z : ThirdVertex) : Prop :=
  p.val = z.val % 3

instance instDecidableParentOwns (b : Branch) (p : ParentSlot)
    (z : ThirdVertex) : Decidable (parentOwns b p z) := by
  unfold parentOwns
  infer_instance

/-- Nine blockers distributed cyclically across five targets. -/
def blockerTarget (z : ThirdVertex) : Target :=
  ⟨z.val % 5, Nat.mod_lt _ (by omega)⟩

def parentSlot (z : ThirdVertex) : ParentSlot :=
  ⟨z.val % 3, Nat.mod_lt _ (by omega)⟩

/-- The smallest incidence counterprofile uses no parent--target contacts.
This makes the v0.20 non-incidence rule hold maximally. -/
def parentContactsTarget (_b : Branch) (_p : ParentSlot) (_x : Target) : Prop :=
  False

instance instDecidableParentContactsTarget
    (b : Branch) (p : ParentSlot) (x : Target) :
    Decidable (parentContactsTarget b p x) := by
  unfold parentContactsTarget
  infer_instance

/-- Every third vertex has exactly one parent slot in each colored branch. -/
theorem unique_parent_in_each_branch :
    ∀ z : ThirdVertex, ∀ b : Branch,
      ∃! p : ParentSlot, parentOwns b p z := by
  intro z b
  refine ⟨parentSlot z, rfl, ?_⟩
  intro p hp
  apply Fin.ext
  exact hp

/-- Every colored parent owns exactly three third-layer incidences. -/
theorem three_thirds_per_parent :
    ∀ b : Branch, ∀ p : ParentSlot,
      ((Finset.univ.filter fun z : ThirdVertex ↦ parentOwns b p z).card = 3) := by
  intro b p
  fin_cases p <;> simp [parentOwns] <;> decide +revert

/-- Each branch therefore owns all nine third-layer incidences. -/
theorem nine_incidences_per_branch :
    ∀ b : Branch,
      ∑ p : ParentSlot,
        (Finset.univ.filter fun z : ThirdVertex ↦ parentOwns b p z).card = 9 := by
  intro b
  simp [parentOwns]
  decide +revert

/-- The three branch colors account for all 27 parent incidences. -/
theorem twenty_seven_colored_parent_incidences :
    ∑ b : Branch, ∑ p : ParentSlot,
      (Finset.univ.filter fun z : ThirdVertex ↦ parentOwns b p z).card = 27 := by
  decide

/-- Explicit target-capacity vector from the earlier geodesic calculation. -/
def targetCapacity (x : Target) : ℕ :=
  if x.val = 0 then 3 else 2

/-- Every target receives at most its outside blocker capacity. -/
theorem blocker_capacity_respected :
    ∀ x : Target,
      ((Finset.univ.filter fun z : ThirdVertex ↦ blockerTarget z = x).card ≤
        targetCapacity x) := by
  intro x
  fin_cases x <;> decide

/-- The nine distinct blockers use only nine of the eleven available slots. -/
theorem nine_blockers_within_eleven_slots :
    ∑ x : Target,
      (Finset.univ.filter fun z : ThirdVertex ↦ blockerTarget z = x).card = 9 ∧
    (9 : ℕ) ≤ 11 := by
  constructor <;> decide

/-- Parent--target non-incidence holds for every owned blocked third vertex. -/
theorem blocker_forbids_every_owning_parent :
    ∀ z : ThirdVertex, ∀ b : Branch, ∀ p : ParentSlot,
      parentOwns b p z →
        ¬ parentContactsTarget b p (blockerTarget z) := by
  simp [parentContactsTarget]

/-- Complete colored counterprofile.  This simultaneously realizes branch
ownership, parent load, blocker capacity, and parent--target non-incidence. -/
theorem colored_ownership_counterprofile :
    (∀ z : ThirdVertex, ∀ b : Branch,
      ∃! p : ParentSlot, parentOwns b p z) ∧
    (∀ b : Branch, ∀ p : ParentSlot,
      (Finset.univ.filter fun z : ThirdVertex ↦ parentOwns b p z).card = 3) ∧
    (∀ x : Target,
      (Finset.univ.filter fun z : ThirdVertex ↦ blockerTarget z = x).card ≤
        targetCapacity x) ∧
    (∀ z : ThirdVertex, ∀ b : Branch, ∀ p : ParentSlot,
      parentOwns b p z →
        ¬ parentContactsTarget b p (blockerTarget z)) := by
  exact ⟨unique_parent_in_each_branch, three_thirds_per_parent,
    blocker_capacity_respected, blocker_forbids_every_owning_parent⟩

/-- Nine is minimal for any 27-incidence model with multiplicity at most
three, independently of colors. -/
theorem nine_le_distinct_of_multiplicity_three
    {distinct : ℕ} (hcapacity : 27 ≤ 3 * distinct) :
    9 ≤ distinct := by
  omega

end WrittenOnTheWallII.GraphConjecture133ColoredOwnership
