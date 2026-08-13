import FormalConjecturesUtil

/-!
# WOWII 133: final local blocker splice

For a genuine third choice `z` below `u-c-parent`, failure of early cleanliness
means adjacency to one of geodesic indices `0..4`.  C4-freeness excludes index
zero by the cycle `u-c-parent-z-u`.  The remaining contact is exactly
membership in one of the four internal outside-neighbor finsets.

Combining this local translation with three disjoint cardinality-three third
sets in one branch and the four capacity-two internal target sets gives the
end-to-end local contradiction.
-/

namespace WrittenOnTheWallII.GraphConjecture133FinalLocalSplice

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

def HasC4 (G : SimpleGraph V) : Prop :=
  ∃ a b c d : V,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a

def earlyContactSet {u v : V} (G : SimpleGraph V) (p : G.Walk u v)
    (z : V) [DecidableRel G.Adj] : Finset ℕ :=
  (Finset.range 5).filter fun k ↦ G.Adj z (p.getVert k)

def internalOutside {u v : V} (G : SimpleGraph V) (p : G.Walk u v)
    (k : Fin 4) [DecidableRel G.Adj] : Finset V :=
  ((G.neighborFinset (p.getVert (k.val + 1))).erase (p.getVert k.val)).erase
    (p.getVert (k.val + 2))

def internalOutsideUnion {u v : V} (G : SimpleGraph V) (p : G.Walk u v)
    [DecidableRel G.Adj] : Finset V :=
  ((internalOutside G p 0 ∪ internalOutside G p 1) ∪
    internalOutside G p 2) ∪ internalOutside G p 3

omit [Fintype V] [DecidableEq V] in
/-- The index-zero contact of a genuine third is impossible. -/
theorem genuine_third_not_contact_zero
    {G : SimpleGraph V} (hc4 : ¬HasC4 G)
    {u v c parent z : V} (p : G.Walk u v)
    (huc : G.Adj u c) (hcp : G.Adj c parent)
    (hpz : G.Adj parent z) (hparentu : parent ≠ u) (hzc : z ≠ c) :
    ¬G.Adj z (p.getVert 0) := by
  simpa [Walk.getVert_zero] using
    (show ¬G.Adj z u from by
      intro hzu
      apply hc4
      refine ⟨u, c, parent, z, huc.ne, hparentu.symm, hzu.ne.symm,
        hcp.ne, hzc.symm, hpz.ne, huc, hcp, hpz, hzu⟩)

omit [Fintype V] [DecidableEq V] in
/-- Negating early cleanliness gives an actual contact index in `0..4`. -/
theorem contact_of_not_early_clean
    (G : SimpleGraph V) [DecidableRel G.Adj]
    {u v z : V} (p : G.Walk u v)
    (hnot : ¬∀ k, k < 5 → k ≤ p.length → ¬G.Adj z (p.getVert k)) :
    ∃ k, k < 5 ∧ k ≤ p.length ∧ G.Adj z (p.getVert k) := by
  push_neg at hnot
  exact hnot

/-- A contact at internal index `k+1` is membership in that target's outside
set once adjacency to its two geodesic neighbors is excluded. -/
theorem mem_internalOutside_of_contact
    (G : SimpleGraph V) [DecidableRel G.Adj]
    {u v z : V} (p : G.Walk u v) (k : Fin 4)
    (hcontact : G.Adj z (p.getVert (k.val + 1)))
    (hprev : z ≠ p.getVert k.val)
    (hnext : z ≠ p.getVert (k.val + 2)) :
    z ∈ internalOutside G p k := by
  simp [internalOutside, hcontact.symm, hprev, hnext]

/-- A fresh genuine third with failed early cleanliness lies in the internal
outside union.  The endpoint contact is removed by C4-freeness. -/
theorem internal_blocker_of_not_early_clean
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {u v c parent z : V} (p : G.Walk u v)
    (huc : G.Adj u c) (hcp : G.Adj c parent)
    (hpz : G.Adj parent z) (hparentu : parent ≠ u) (hzc : z ≠ c)
    (hzfresh : z ∉ p.support)
    (hnot : ¬∀ k, k < 5 → k ≤ p.length → ¬G.Adj z (p.getVert k)) :
    z ∈ internalOutsideUnion G p := by
  obtain ⟨k, hk5, _hklen, hcontact⟩ :=
    contact_of_not_early_clean G p hnot
  have hk0 : k ≠ 0 := by
    intro hk
    subst k
    exact genuine_third_not_contact_zero hc4 p huc hcp hpz
      hparentu hzc hcontact
  have hk : k = 1 ∨ k = 2 ∨ k = 3 ∨ k = 4 := by omega
  rcases hk with rfl | rfl | rfl | rfl
  · have hm := mem_internalOutside_of_contact G p (0 : Fin 4) hcontact
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 0))
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 2))
    exact Finset.mem_union_left _ (Finset.mem_union_left _
      (Finset.mem_union_left _ hm))
  · have hm := mem_internalOutside_of_contact G p (1 : Fin 4) hcontact
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 1))
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 3))
    exact Finset.mem_union_left _ (Finset.mem_union_left _
      (Finset.mem_union_right _ hm))
  · have hm := mem_internalOutside_of_contact G p (2 : Fin 4) hcontact
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 2))
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 4))
    exact Finset.mem_union_left _ (Finset.mem_union_right _ hm)
  · have hm := mem_internalOutside_of_contact G p (3 : Fin 4) hcontact
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 3))
      (fun h ↦ hzfresh (h ▸ p.getVert_mem_support 5))
    exact Finset.mem_union_right _ hm

/-- Internal geodesic targets have exactly two outside-neighbor slots in a
four-regular graph. -/
theorem card_internalOutside_eq_two
    (G : SimpleGraph V) [DecidableRel G.Adj]
    {u v : V} (p : G.Walk u v) (hpPath : p.IsPath)
    (hreg : G.IsRegularOfDegree 4) (k : Fin 4)
    (hk : k.val + 1 < p.length) :
    (internalOutside G p k).card = 2 := by
  have hprev : p.getVert k.val ∈
      G.neighborFinset (p.getVert (k.val + 1)) := by
    simpa [adj_comm] using p.adj_getVert_succ (by omega : k.val < p.length)
  have hnext : p.getVert (k.val + 2) ∈
      G.neighborFinset (p.getVert (k.val + 1)) := by
    simpa using p.adj_getVert_succ hk
  have hne : p.getVert k.val ≠ p.getVert (k.val + 2) := by
    intro h
    have := hpPath.getVert_injOn
      (show k.val ≤ p.length by omega)
      (show k.val + 2 ≤ p.length by omega) h
    omega
  have hnextErase : p.getVert (k.val + 2) ∈
      (G.neighborFinset (p.getVert (k.val + 1))).erase
        (p.getVert k.val) :=
    Finset.mem_erase.mpr ⟨hne.symm, hnext⟩
  simp only [internalOutside]
  rw [Finset.card_erase_of_mem hnextErase,
    Finset.card_erase_of_mem hprev,
    G.card_neighborFinset_eq_degree, hreg]

def threeThirds (s₀ s₁ s₂ : Finset V) : Finset V :=
  (s₀ ∪ s₁) ∪ s₂

/-- End-to-end local configuration theorem.  Three disjoint third-choice
triples below one first branch cannot all fail early cleanliness. -/
theorem exists_early_clean_third_of_branch_capacity
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4) (hc4 : ¬HasC4 G)
    {u v c p₀ p₁ p₂ : V} (geod : G.Walk u v)
    (hpath : geod.IsPath) (hlen : 5 ≤ geod.length)
    (huc : G.Adj u c)
    (hcp₀ : G.Adj c p₀) (hcp₁ : G.Adj c p₁) (hcp₂ : G.Adj c p₂)
    (hp₀u : p₀ ≠ u) (hp₁u : p₁ ≠ u) (hp₂u : p₂ ≠ u)
    (s₀ s₁ s₂ : Finset V)
    (hs₀ : s₀.card = 3) (hs₁ : s₁.card = 3) (hs₂ : s₂.card = 3)
    (hd₀₁ : Disjoint s₀ s₁) (hd₀₂ : Disjoint s₀ s₂)
    (hd₁₂ : Disjoint s₁ s₂)
    (howner₀ : ∀ z ∈ s₀, G.Adj p₀ z ∧ z ≠ c ∧ z ∉ geod.support)
    (howner₁ : ∀ z ∈ s₁, G.Adj p₁ z ∧ z ≠ c ∧ z ∉ geod.support)
    (howner₂ : ∀ z ∈ s₂, G.Adj p₂ z ∧ z ≠ c ∧ z ∉ geod.support) :
    ∃ z, z ∈ threeThirds s₀ s₁ s₂ ∧
      ∀ k, k < 5 → k ≤ geod.length → ¬G.Adj z (geod.getVert k) := by
  by_contra hclean
  push_neg at hclean
  have hcover : threeThirds s₀ s₁ s₂ ⊆ internalOutsideUnion G geod := by
    intro z hz
    simp only [threeThirds, Finset.mem_union] at hz
    rcases hz with (hz₀ | hz₁) | hz₂
    · obtain ⟨hpz, hzc, hzfresh⟩ := howner₀ z hz₀
      apply internal_blocker_of_not_early_clean G hc4 geod huc hcp₀ hpz
        hp₀u hzc hzfresh
      push_neg
      exact hclean z (by simp [threeThirds, hz₀])
    · obtain ⟨hpz, hzc, hzfresh⟩ := howner₁ z hz₁
      apply internal_blocker_of_not_early_clean G hc4 geod huc hcp₁ hpz
        hp₁u hzc hzfresh
      push_neg
      exact hclean z (by simp [threeThirds, hz₁])
    · obtain ⟨hpz, hzc, hzfresh⟩ := howner₂ z hz₂
      apply internal_blocker_of_not_early_clean G hc4 geod huc hcp₂ hpz
        hp₂u hzc hzfresh
      push_neg
      exact hclean z (by simp [threeThirds, hz₂])
  have hthirdCard : (threeThirds s₀ s₁ s₂).card = 9 := by
    have hd012 : Disjoint (s₀ ∪ s₁) s₂ :=
      Finset.disjoint_union_left.mpr ⟨hd₀₂, hd₁₂⟩
    simp only [threeThirds]
    rw [Finset.card_union_of_disjoint hd012,
      Finset.card_union_of_disjoint hd₀₁, hs₀, hs₁, hs₂]
  have houtsideCard : (internalOutsideUnion G geod).card ≤ 8 := by
    have h0 := card_internalOutside_eq_two G geod hpath hreg (0 : Fin 4)
      (by omega)
    have h1 := card_internalOutside_eq_two G geod hpath hreg (1 : Fin 4)
      (by omega)
    have h2 := card_internalOutside_eq_two G geod hpath hreg (2 : Fin 4)
      (by omega)
    have h3 := card_internalOutside_eq_two G geod hpath hreg (3 : Fin 4)
      (by omega)
    have h01 := Finset.card_union_le
      (internalOutside G geod 0) (internalOutside G geod 1)
    have h012 := Finset.card_union_le
      (internalOutside G geod 0 ∪ internalOutside G geod 1)
      (internalOutside G geod 2)
    have h0123 := Finset.card_union_le
      ((internalOutside G geod 0 ∪ internalOutside G geod 1) ∪
        internalOutside G geod 2) (internalOutside G geod 3)
    simp only [internalOutsideUnion]
    omega
  have hinject := Finset.card_le_card hcover
  omega

/- ## Specialization to actual graph neighborhoods -/

def thirdChoices (G : SimpleGraph V) (c parent : V)
    [DecidableRel G.Adj] : Finset V :=
  (G.neighborFinset parent).erase c

theorem card_thirdChoices_eq_three
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4) {c parent : V}
    (hcp : G.Adj c parent) :
    (thirdChoices G c parent).card = 3 := by
  have hmem : c ∈ G.neighborFinset parent := by simpa using hcp.symm
  simp only [thirdChoices]
  rw [Finset.card_erase_of_mem hmem,
    G.card_neighborFinset_eq_degree, hreg]

theorem thirdChoices_disjoint
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) {c p q : V}
    (hcp : G.Adj c p) (hcq : G.Adj c q) (hpq : p ≠ q) :
    Disjoint (thirdChoices G c p) (thirdChoices G c q) := by
  rw [Finset.disjoint_left]
  intro z hzp hzq
  have hpz : G.Adj p z := by
    simpa [thirdChoices] using Finset.mem_of_mem_erase hzp
  have hqz : G.Adj q z := by
    simpa [thirdChoices] using Finset.mem_of_mem_erase hzq
  have hzc : z ≠ c := Finset.ne_of_mem_erase hzp
  apply hc4
  refine ⟨c, p, z, q, hcp.ne, hzc.symm, hcq.ne,
    hpz.ne, hpq, hqz.ne.symm, hcp, hpz, hqz.symm, hcq.symm⟩

/-- Actual end-to-end local theorem.  If one first-choice branch has all
three second parents clean against the geodesic, then one of their nine
actual third choices is clean at every early index `0..4`. -/
theorem exists_early_clean_third_of_three_clean_parents
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hreg : G.IsRegularOfDegree 4) (hc4 : ¬HasC4 G)
    {u v c : V} (geod : G.Walk u v)
    (hpath : geod.IsPath) (hlen : 5 ≤ geod.length)
    (huc : G.Adj u c)
    (parent : Fin 3 → V)
    (hcparent : ∀ i, G.Adj c (parent i))
    (hparentu : ∀ i, parent i ≠ u)
    (hparentInj : Function.Injective parent)
    (hparentClean : ∀ i, ∀ x ∈ geod.support,
      ¬G.Adj (parent i) x) :
    ∃ i : Fin 3, ∃ z,
      z ∈ thirdChoices G c (parent i) ∧
      ∀ k, k < 5 → k ≤ geod.length → ¬G.Adj z (geod.getVert k) := by
  let s₀ := thirdChoices G c (parent 0)
  let s₁ := thirdChoices G c (parent 1)
  let s₂ := thirdChoices G c (parent 2)
  have howner : ∀ i : Fin 3, ∀ z ∈ thirdChoices G c (parent i),
      G.Adj (parent i) z ∧ z ≠ c ∧ z ∉ geod.support := by
    intro i z hz
    have hpz : G.Adj (parent i) z := by
      simpa [thirdChoices] using Finset.mem_of_mem_erase hz
    have hzc : z ≠ c := Finset.ne_of_mem_erase hz
    have hzfresh : z ∉ geod.support := by
      intro hzmem
      exact hparentClean i z hzmem hpz
    exact ⟨hpz, hzc, hzfresh⟩
  obtain ⟨z, hz, hzclean⟩ :=
    exists_early_clean_third_of_branch_capacity G hreg hc4 geod
      hpath hlen huc (hcparent 0) (hcparent 1) (hcparent 2)
      (hparentu 0) (hparentu 1) (hparentu 2)
      s₀ s₁ s₂
      (card_thirdChoices_eq_three G hreg (hcparent 0))
      (card_thirdChoices_eq_three G hreg (hcparent 1))
      (card_thirdChoices_eq_three G hreg (hcparent 2))
      (thirdChoices_disjoint G hc4 (hcparent 0) (hcparent 1)
        (hparentInj.ne (by decide)))
      (thirdChoices_disjoint G hc4 (hcparent 0) (hcparent 2)
        (hparentInj.ne (by decide)))
      (thirdChoices_disjoint G hc4 (hcparent 1) (hcparent 2)
        (hparentInj.ne (by decide)))
      (howner 0) (howner 1) (howner 2)
  simp only [threeThirds, s₀, s₁, s₂, Finset.mem_union] at hz
  rcases hz with (hz | hz) | hz
  · exact ⟨0, z, hz, hzclean⟩
  · exact ⟨1, z, hz, hzclean⟩
  · exact ⟨2, z, hz, hzclean⟩

end WrittenOnTheWallII.GraphConjecture133FinalLocalSplice
