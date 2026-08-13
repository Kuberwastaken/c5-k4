import FormalConjecturesUtil

/-!
# WOWII 133: blocker-injection bridge

This is the finite bridge from actual third-choice layers to the corrected
eight-slot blocker budget.  Three parent slots in each of three branches give
27 incidences.  Same-branch disjointness makes each branch union a nine-point
set.  If every distinct third is blocked internally, the identity map embeds
that union into four outside-neighbor sets of size at most two, which is
impossible.

The proof deliberately exposes the blocker embedding: a blocker edge at a
target uses the third vertex itself as an outside neighbor, so no arbitrary
choice of a new blocker vertex is involved.
-/

namespace WrittenOnTheWallII.GraphConjecture133BlockerInjectionBridge

variable {V : Type*} [DecidableEq V]

abbrev Branch := Fin 3
abbrev ParentSlot := Fin 3
abbrev InternalTarget := Fin 4

/-- The three third-choice sets belonging to one first-choice branch. -/
def branchThirds (thirds : Branch → ParentSlot → Finset V)
    (b : Branch) : Finset V :=
  (thirds b 0 ∪ thirds b 1) ∪ thirds b 2

/-- The union of all three branch layers. -/
def allThirds (thirds : Branch → ParentSlot → Finset V) : Finset V :=
  (branchThirds thirds 0 ∪ branchThirds thirds 1) ∪
    branchThirds thirds 2

/-- Four internal geodesic targets, corresponding to original indices 1--4. -/
def internalOutsideUnion (outside : InternalTarget → Finset V) : Finset V :=
  ((outside 0 ∪ outside 1) ∪ outside 2) ∪ outside 3

omit [DecidableEq V] in
/-- The nine parent slots account for all 27 third incidences. -/
theorem twenty_seven_actual_third_incidences
    (thirds : Branch → ParentSlot → Finset V)
    (hcard : ∀ b p, (thirds b p).card = 3) :
    ∑ b : Branch, ∑ p : ParentSlot, (thirds b p).card = 27 := by
  simp_rw [hcard]
  decide

/-- Pairwise disjoint triples in one branch have union cardinality nine. -/
theorem card_branchThirds_eq_nine
    (thirds : Branch → ParentSlot → Finset V)
    (hcard : ∀ b p, (thirds b p).card = 3)
    (hdisjoint : ∀ b p q, p ≠ q → Disjoint (thirds b p) (thirds b q))
    (b : Branch) :
    (branchThirds thirds b).card = 9 := by
  have h01 : Disjoint (thirds b 0) (thirds b 1) :=
    hdisjoint b 0 1 (by decide)
  have h02 : Disjoint (thirds b 0) (thirds b 2) :=
    hdisjoint b 0 2 (by decide)
  have h12 : Disjoint (thirds b 1) (thirds b 2) :=
    hdisjoint b 1 2 (by decide)
  have h012 : Disjoint (thirds b 0 ∪ thirds b 1) (thirds b 2) :=
    Finset.disjoint_union_left.mpr ⟨h02, h12⟩
  simp only [branchThirds]
  rw [Finset.card_union_of_disjoint h012,
    Finset.card_union_of_disjoint h01, hcard, hcard, hcard]

/-- In particular, the full three-branch union contains at least nine
distinct thirds. -/
theorem nine_le_card_allThirds
    (thirds : Branch → ParentSlot → Finset V)
    (hcard : ∀ b p, (thirds b p).card = 3)
    (hdisjoint : ∀ b p q, p ≠ q → Disjoint (thirds b p) (thirds b q)) :
    9 ≤ (allThirds thirds).card := by
  have hsub : branchThirds thirds 0 ⊆ allThirds thirds := by
    intro z hz
    exact Finset.mem_union_left _ (Finset.mem_union_left _ hz)
  rw [← card_branchThirds_eq_nine thirds hcard hdisjoint 0]
  exact Finset.card_le_card hsub

/-- Four outside-neighbor sets of cardinality at most two have union
cardinality at most eight. -/
theorem card_internalOutsideUnion_le_eight
    (outside : InternalTarget → Finset V)
    (hcard : ∀ k, (outside k).card ≤ 2) :
    (internalOutsideUnion outside).card ≤ 8 := by
  have h01 := Finset.card_union_le (outside 0) (outside 1)
  have h012 := Finset.card_union_le (outside 0 ∪ outside 1) (outside 2)
  have h0123 := Finset.card_union_le
    ((outside 0 ∪ outside 1) ∪ outside 2) (outside 3)
  have h0 := hcard 0
  have h1 := hcard 1
  have h2 := hcard 2
  have h3 := hcard 3
  simp only [internalOutsideUnion]
  omega

/-- Membership in the four-set union supplies a concrete internal target
whose outside-neighbor set contains the blocker vertex. -/
theorem exists_internal_target_of_mem_union
    (outside : InternalTarget → Finset V) {z : V}
    (hz : z ∈ internalOutsideUnion outside) :
    ∃ k : InternalTarget, z ∈ outside k := by
  simp only [internalOutsideUnion, Finset.mem_union] at hz
  rcases hz with ((hz | hz) | hz) | hz
  · exact ⟨0, hz⟩
  · exact ⟨1, hz⟩
  · exact ⟨2, hz⟩
  · exact ⟨3, hz⟩

/-- Conversely, selecting one internal target for a third puts that same
vertex in the combined outside-neighbor set. -/
theorem mem_union_of_exists_internal_target
    (outside : InternalTarget → Finset V) {z : V}
    (hz : ∃ k : InternalTarget, z ∈ outside k) :
    z ∈ internalOutsideUnion outside := by
  obtain ⟨k, hk⟩ := hz
  fin_cases k
  · exact Finset.mem_union_left _ (Finset.mem_union_left _
      (Finset.mem_union_left _ hk))
  · exact Finset.mem_union_left _ (Finset.mem_union_left _
      (Finset.mem_union_right _ hk))
  · exact Finset.mem_union_left _ (Finset.mem_union_right _ hk)
  · exact Finset.mem_union_right _ hk

/-- The selected blocker embedding is the identity on graph vertices. -/
def blockerEmbedding
    (thirds : Branch → ParentSlot → Finset V)
    (outside : InternalTarget → Finset V)
    (hcover : allThirds thirds ⊆ internalOutsideUnion outside) :
    {z // z ∈ allThirds thirds} → {z // z ∈ internalOutsideUnion outside} :=
  fun z ↦ ⟨z.1, hcover z.2⟩

theorem blockerEmbedding_injective
    (thirds : Branch → ParentSlot → Finset V)
    (outside : InternalTarget → Finset V)
    (hcover : allThirds thirds ⊆ internalOutsideUnion outside) :
    Function.Injective (blockerEmbedding thirds outside hcover) := by
  intro z w h
  apply Subtype.ext
  exact congrArg (fun x ↦ x.1) h

/-- Exact bridge contradiction.  The 27 incidence hypotheses are represented
by nine pairwise-disjoint triples branchwise; if every distinct third has an
internal blocker, the resulting identity embedding would put at least nine
vertices into a union of cardinality at most eight. -/
theorem no_internal_blocker_cover_of_twenty_seven_incidences
    (thirds : Branch → ParentSlot → Finset V)
    (outside : InternalTarget → Finset V)
    (hthirdCard : ∀ b p, (thirds b p).card = 3)
    (hbranchDisjoint : ∀ b p q, p ≠ q →
      Disjoint (thirds b p) (thirds b q))
    (houtsideCard : ∀ k, (outside k).card ≤ 2)
    (hcover : allThirds thirds ⊆ internalOutsideUnion outside) : False := by
  have hlower := nine_le_card_allThirds thirds hthirdCard hbranchDisjoint
  have hupper := card_internalOutsideUnion_le_eight outside houtsideCard
  have hinject := Finset.card_le_card hcover
  omega

/-- Per-third selection form of the bridge.  If every distinct third chooses
one internal target containing it as an outside neighbor, the induced cover
is impossible. -/
theorem no_internal_blocker_selection_of_twenty_seven_incidences
    (thirds : Branch → ParentSlot → Finset V)
    (outside : InternalTarget → Finset V)
    (hthirdCard : ∀ b p, (thirds b p).card = 3)
    (hbranchDisjoint : ∀ b p q, p ≠ q →
      Disjoint (thirds b p) (thirds b q))
    (houtsideCard : ∀ k, (outside k).card ≤ 2)
    (hblocked : ∀ z ∈ allThirds thirds,
      ∃ k : InternalTarget, z ∈ outside k) : False := by
  apply no_internal_blocker_cover_of_twenty_seven_incidences
    thirds outside hthirdCard hbranchDisjoint houtsideCard
  intro z hz
  exact mem_union_of_exists_internal_target outside (hblocked z hz)

/-- Constructive form: under the layer and capacity hypotheses, some actual
third is absent from every internal outside-neighbor set. -/
theorem exists_third_without_internal_blocker
    (thirds : Branch → ParentSlot → Finset V)
    (outside : InternalTarget → Finset V)
    (hthirdCard : ∀ b p, (thirds b p).card = 3)
    (hbranchDisjoint : ∀ b p q, p ≠ q →
      Disjoint (thirds b p) (thirds b q))
    (houtsideCard : ∀ k, (outside k).card ≤ 2) :
    ∃ z, z ∈ allThirds thirds ∧ z ∉ internalOutsideUnion outside := by
  by_contra h
  have hcover : allThirds thirds ⊆ internalOutsideUnion outside := by
    intro z hz
    by_contra hzout
    exact h ⟨z, hz, hzout⟩
  exact no_internal_blocker_cover_of_twenty_seven_incidences
    thirds outside hthirdCard hbranchDisjoint houtsideCard hcover

end WrittenOnTheWallII.GraphConjecture133BlockerInjectionBridge
