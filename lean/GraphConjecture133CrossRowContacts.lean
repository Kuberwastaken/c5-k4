import GraphConjecture133DepthThreeCover

/-!
# WOWII 133: cross-row contact restrictions

Distinct forward candidates sharing one parent cannot hit the same geodesic
target: that would make a four-cycle.  Their early-contact rows are therefore
pairwise disjoint.  Triangle-freeness also makes the candidates themselves
pairwise nonadjacent.
-/

namespace WrittenOnTheWallII.GraphConjecture133CrossRowContacts

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- The contact indices in the early window `0..4`. -/
def earlyContactSet {u v : V} (G : SimpleGraph V) (p : G.Walk u v)
    (a : V) [DecidableRel G.Adj] : Finset ℕ :=
  (Finset.range 5).filter (fun k ↦ G.Adj a (p.getVert k))

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Two distinct neighbors of a common parent cannot share a target in a
C4-free graph. -/
theorem not_common_target_of_shared_parent {G : SimpleGraph V}
    (hc4 : ¬HasC4 G) {a b c x : V}
    (hab : G.Adj a b) (hcb : G.Adj c b) (hac : a ≠ c)
    (hbx : b ≠ x) (hax : G.Adj a x) :
    ¬G.Adj c x := by
  intro hcx
  apply hc4
  refine ⟨b, a, x, c, ?_, ?_, ?_, ?_, ?_, ?_, hab.symm, hax, hcx.symm, hcb⟩
  · exact hab.ne.symm
  · exact hbx
  · exact hcb.ne.symm
  · exact hax.ne
  · exact hac
  · exact hcx.ne.symm

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Cross-row form: distinct candidates sharing `b` have disjoint early
contact sets. -/
theorem earlyContactSet_disjoint_of_shared_parent
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v a c b : V}
    (p : G.Walk u v) (hc4 : ¬HasC4 G)
    (hab : G.Adj a b) (hcb : G.Adj c b) (hac : a ≠ c)
    (hbfresh : b ∉ p.support) :
    Disjoint (earlyContactSet G p a) (earlyContactSet G p c) := by
  rw [Finset.disjoint_left]
  intro k hka hkc
  simp only [earlyContactSet, Finset.mem_filter] at hka hkc
  apply not_common_target_of_shared_parent (x := p.getVert k) hc4 hab hcb hac
  · intro h
    exact hbfresh (h ▸ p.getVert_mem_support k)
  · exact hka.2
  · exact hkc.2

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Distinct candidates sharing a parent are themselves nonadjacent in a
triangle-free graph. -/
theorem not_adj_of_shared_parent_of_triangleFree {G : SimpleGraph V}
    (htri : G.CliqueFree 3) {a b c : V}
    (hab : G.Adj a b) (hcb : G.Adj c b) (hac : a ≠ c) :
    ¬G.Adj a c := by
  exact G.isIndepSet_neighborSet_of_triangleFree htri b
    (by simpa [G.mem_neighborSet] using hab.symm)
    (by simpa [G.mem_neighborSet] using hcb.symm)
    hac

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- If two distinct siblings are both blocked, their blocking rows contain
two distinct early indices. -/
theorem exists_distinct_contacts_of_two_blocked_siblings
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v a c b : V}
    (p : G.Walk u v) (hc4 : ¬HasC4 G)
    (hab : G.Adj a b) (hcb : G.Adj c b) (hac : a ≠ c)
    (hbfresh : b ∉ p.support)
    (ha : (earlyContactSet G p a).Nonempty)
    (hc : (earlyContactSet G p c).Nonempty) :
    ∃ i j : ℕ, i ≠ j ∧ i ∈ earlyContactSet G p a ∧
      j ∈ earlyContactSet G p c := by
  obtain ⟨i, hi⟩ := ha
  obtain ⟨j, hj⟩ := hc
  refine ⟨i, j, ?_, hi, hj⟩
  intro hij
  subst j
  exact (Finset.disjoint_left.mp
    (earlyContactSet_disjoint_of_shared_parent p hc4 hab hcb hac hbfresh)) hi hj

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Three pairwise distinct blocked siblings require three pairwise distinct
early contact indices.  This is the exact cross-row counting content supplied
by C4-freeness. -/
theorem exists_three_distinct_contacts_of_three_blocked_siblings
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v a₁ a₂ a₃ b : V}
    (p : G.Walk u v) (hc4 : ¬HasC4 G)
    (h₁b : G.Adj a₁ b) (h₂b : G.Adj a₂ b) (h₃b : G.Adj a₃ b)
    (h₁₂ : a₁ ≠ a₂) (h₁₃ : a₁ ≠ a₃) (h₂₃ : a₂ ≠ a₃)
    (hbfresh : b ∉ p.support)
    (ha₁ : (earlyContactSet G p a₁).Nonempty)
    (ha₂ : (earlyContactSet G p a₂).Nonempty)
    (ha₃ : (earlyContactSet G p a₃).Nonempty) :
    ∃ i₁ i₂ i₃ : ℕ,
      i₁ ≠ i₂ ∧ i₁ ≠ i₃ ∧ i₂ ≠ i₃ ∧
      i₁ ∈ earlyContactSet G p a₁ ∧
      i₂ ∈ earlyContactSet G p a₂ ∧
      i₃ ∈ earlyContactSet G p a₃ := by
  obtain ⟨i₁, hi₁⟩ := ha₁
  obtain ⟨i₂, hi₂⟩ := ha₂
  obtain ⟨i₃, hi₃⟩ := ha₃
  have hd₁₂ := earlyContactSet_disjoint_of_shared_parent p hc4 h₁b h₂b h₁₂ hbfresh
  have hd₁₃ := earlyContactSet_disjoint_of_shared_parent p hc4 h₁b h₃b h₁₃ hbfresh
  have hd₂₃ := earlyContactSet_disjoint_of_shared_parent p hc4 h₂b h₃b h₂₃ hbfresh
  refine ⟨i₁, i₂, i₃, ?_, ?_, ?_, hi₁, hi₂, hi₃⟩
  · intro h; subst i₂; exact (Finset.disjoint_left.mp hd₁₂) hi₁ hi₂
  · intro h; subst i₃; exact (Finset.disjoint_left.mp hd₁₃) hi₁ hi₃
  · intro h; subst i₃; exact (Finset.disjoint_left.mp hd₂₃) hi₂ hi₃

end WrittenOnTheWallII.GraphConjecture133CrossRowContacts
